#!/usr/bin/env python3
"""
03_merge.py —— 把 segment + meta + annotate 合并为最终 documents JSON

输出：data/books/marxists/documents/<author>/<year>_<slug>__<subdoc_id>.json
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEG_DIR = ROOT / "data" / "intermediate" / "01d_segment"
META_DIR = ROOT / "data" / "intermediate" / "02a_meta"
ANN_DIR = ROOT / "data" / "intermediate" / "02_annotate"
OUT_DIR = ROOT / "data" / "books" / "marxists" / "documents"

sys.path.insert(0, str(Path(__file__).parent))
from prompts import PROMPT_VERSION  # noqa: E402


def merge_one(seg_path: Path) -> int:
    rel = seg_path.relative_to(SEG_DIR)
    slug = seg_path.stem
    doc = json.loads(seg_path.read_text("utf-8"))
    out_count = 0

    for sub in doc["subdocs"]:
        sid = sub["subdoc_id"]
        meta_path = META_DIR / rel.parent / f"{slug}__{sid}.json"
        ann_dir = ANN_DIR / rel.parent / f"{slug}__{sid}"
        if not meta_path.exists():
            continue

        meta_payload = json.loads(meta_path.read_text("utf-8"))
        meta = meta_payload.get("meta", {})

        # 合并段落 annotation
        merged_paras = []
        for p in sub["paragraphs"]:
            ann_path = ann_dir / f"p{p['n']:04d}.json"
            ann = {}
            if ann_path.exists():
                try:
                    ann_payload = json.loads(ann_path.read_text("utf-8"))
                    ann = ann_payload.get("annotation", {})
                except Exception:
                    pass

            # 句子合并
            ann_sents = {s["sid"]: s for s in ann.get("sentences", [])}
            merged_sents = []
            for s in p.get("sentences", []):
                a = ann_sents.get(s["sid"], {})
                merged_sents.append({
                    "sid": s["sid"],
                    "original": s["original"],
                    "char_start": s["char_start"],
                    "char_end": s["char_end"],
                    "plain": a.get("plain"),
                    "speaker": a.get("speaker"),
                    "stance": a.get("stance"),
                    "notes": a.get("notes", []),
                })

            merged_paras.append({
                "n": p["n"],
                "original_html": p["original_html"],
                "original_plain": p["original_plain"],
                "gist": ann.get("gist"),
                "plain_rewrite": ann.get("plain_rewrite"),
                "block_type": ann.get("block_type", "author_text"),
                "length_policy": ann.get("length_policy", "normal_paragraph"),
                "sentences": merged_sents,
            })

        # 文件名
        year = doc.get("year") or "0000"
        fname = f"{year}_{slug}__{sid}.json"
        author = doc["author"]
        out_path = OUT_DIR / author / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)

        final = {
            "_prompt_version": PROMPT_VERSION,
            "id": f"{author}_{year}_{slug}_{sid}",
            "title": sub.get("label") or doc["title"],
            "title_local": sub.get("title_local"),
            "author_id": author,
            "year": year,
            "source_url": doc["source_url"],
            "is_multi_doc_page": doc.get("is_multi_doc", False),
            "subdoc_id": sid,
            "meta": meta,
            "footnotes": sub.get("footnotes", []),
            "provenance_text_raw": sub.get("provenance_text", ""),
            "paragraphs": merged_paras,
        }
        out_path.write_text(json.dumps(final, ensure_ascii=False, indent=2), "utf-8")
        out_count += 1

    return out_count


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for seg_path in sorted(SEG_DIR.rglob("*.json")):
        try:
            n = merge_one(seg_path)
            total += n
        except Exception as e:
            print(f"  ! merge fail {seg_path.stem}: {e}")
    print(f"merged {total} documents")


if __name__ == "__main__":
    main()
