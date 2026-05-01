#!/usr/bin/env python3
"""
03_merge_v2.py —— 合并 v0.2 annotate 产出到最终 documents

输入：
  data/intermediate/01d_segment/<author>/<slug>.json
  data/intermediate/02a_meta/<author>/<slug>__<sid>.json   (复用 v0.1 meta)
  data/intermediate/02b_annotate_v2/<author>/<slug>__<sid>/p####.json

输出：
  data/books/marxists_v2/documents/<author>/<year>_<slug>__<sid>.json

后处理：
  - 根据段级 importance_score 选 top 5-7 写到 reading_path.essential_paragraphs
  - 根据字数 + difficulty 计算 estimated_minutes
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEG_DIR = ROOT / "data" / "intermediate" / "01d_segment"
META_DIR = ROOT / "data" / "intermediate" / "02a_meta"
ANN_DIR = ROOT / "data" / "intermediate" / "02b_annotate_v2"
OUT_DIR = ROOT / "data" / "books" / "marxists_v2" / "documents"

import importlib.util
PROMPTS_V2 = Path(__file__).parent / "prompts_v2"
spec = importlib.util.spec_from_file_location("prompts_v2_loader", PROMPTS_V2 / "__init__.py")
prompts_v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(prompts_v2)
PROMPT_VERSION = prompts_v2.PROMPT_VERSION


# 难度对应阅读速度（中文字符/分钟）
READ_SPEED = {
    "easy": 400,
    "moderate": 280,
    "hard": 180,
    "expert": 120,
}


def calc_essential_paragraphs(merged_paras: list[dict], top_n: int = 6) -> list[int]:
    """按 importance_score 选 top-N"""
    scored = [(p.get("importance_score") or 0, p["n"]) for p in merged_paras]
    scored.sort(key=lambda x: (-x[0], x[1]))
    # 至少选到 score >= 2 的；不够补到 top_n
    essential = [n for s, n in scored if s >= 2][:top_n]
    if len(essential) < min(top_n, 3):
        essential = [n for _, n in scored[:top_n]]
    return sorted(essential)


def calc_estimated_minutes(merged_paras: list[dict], difficulty: str) -> int:
    total_chars = sum(len(p.get("original_plain", "")) for p in merged_paras)
    speed = READ_SPEED.get(difficulty, 280)
    return max(1, round(total_chars / speed))


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

            ann_sents = {s["sid"]: s for s in ann.get("sentences", [])}
            merged_sents = []
            for s in p.get("sentences", []):
                a = ann_sents.get(s["sid"], {})
                # confidence: low 的 notes 不入产出
                notes = [n for n in a.get("notes", []) if n.get("confidence") != "low"]
                merged_sents.append({
                    "sid": s["sid"],
                    "original": s["original"],
                    "char_start": s["char_start"],
                    "char_end": s["char_end"],
                    "speaker": a.get("speaker", "author"),
                    "stance": a.get("stance", "self"),
                    "notes": notes,
                })

            # hard_sentences：confidence: low 不展示
            hs = [h for h in ann.get("hard_sentences", []) if h.get("confidence") != "low"]

            merged_paras.append({
                "n": p["n"],
                "original_plain": p["original_plain"],
                "original_html": p.get("original_html"),
                "block_type": ann.get("block_type", "author_text"),
                "gist": ann.get("gist"),
                "importance_score": ann.get("importance_score"),
                "importance_reason": ann.get("importance_reason"),
                "argument_role": ann.get("argument_role"),
                "argument_link": ann.get("argument_link"),
                "paragraph_gates": ann.get("paragraph_gates"),
                "prereading_refs": ann.get("prereading_refs", []),
                "prereading_inline": [
                    pr for pr in ann.get("prereading_inline", [])
                    if pr.get("confidence") != "low"
                ],
                "hard_sentences": hs,
                "polemic_in_paragraph": ann.get("polemic_in_paragraph"),
                "sentences": merged_sents,
            })

        # reading_path 后处理（不让 LLM 直接选 essential_paragraphs / estimated_minutes）
        rp = dict(meta.get("reading_path") or {})
        difficulty = rp.get("difficulty", "moderate")
        rp["essential_paragraphs"] = calc_essential_paragraphs(merged_paras)
        rp["estimated_minutes"] = calc_estimated_minutes(merged_paras, difficulty)

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
            "subdoc_id": sid,
            "meta": {**meta, "reading_path": rp},
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
            print(f"  ! merge_v2 fail {seg_path.stem}: {e}")
    print(f"merged_v2 {total} documents")


if __name__ == "__main__":
    main()
