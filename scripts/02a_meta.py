#!/usr/bin/env python3
"""
02a_meta.py —— 篇章级 meta 生成

输入：data/intermediate/01d_segment/<author>/<slug>.json
输出：data/intermediate/02a_meta/<author>/<slug>__<subdoc_id>.json
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "data" / "intermediate" / "01d_segment"
OUT_DIR = ROOT / "data" / "intermediate" / "02a_meta"

sys.path.insert(0, str(Path(__file__).parent))
from llm_client import call_llm_json  # noqa: E402
from prompts import load_prompt, PROMPT_VERSION  # noqa: E402

MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "20"))
MANIFEST_PATH = ROOT / "data" / "raw" / "manifest.json"

AUTHOR_NAMES = {"marx": "马克思", "engels": "恩格斯", "lenin": "列宁", "stalin": "斯大林"}


def gen_meta_for_subdoc(doc: dict, sub: dict) -> dict:
    """对一个 subdoc 调一次 LLM 生成 meta"""
    # 拼前 8000 字符作为上下文
    text_parts = []
    used = 0
    for p in sub["paragraphs"]:
        s = p["original_plain"]
        if used + len(s) > 8000:
            break
        text_parts.append(f"[第{p['n']}段] {s}")
        used += len(s)
    text_head = "\n\n".join(text_parts)

    sys_prompt = load_prompt("meta/system.md")
    user_prompt = load_prompt(
        "meta/user.md",
        title=sub.get("label") or doc["title"],
        author=AUTHOR_NAMES.get(doc["author"], doc["author"]),
        source_url=doc["source_url"],
        provenance_block=sub.get("provenance_text", "") or "（无明确 provenance 块）",
        text_head=text_head,
    )

    result = call_llm_json(sys_prompt, user_prompt, temperature=0.2)
    return result


def process_one(doc_path: Path) -> tuple[str, int, int]:
    """处理一个 segment json，返回 (slug, ok, fail)"""
    doc = json.loads(doc_path.read_text("utf-8"))
    rel = doc_path.relative_to(IN_DIR)
    out_dir = OUT_DIR / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = doc_path.stem
    ok, fail = 0, 0

    for sub in doc["subdocs"]:
        sid = sub["subdoc_id"]
        out_path = out_dir / f"{slug}__{sid}.json"
        if out_path.exists():
            try:
                ex = json.loads(out_path.read_text("utf-8"))
                if ex.get("_prompt_version") == PROMPT_VERSION:
                    continue
            except Exception:
                pass
        try:
            meta = gen_meta_for_subdoc(doc, sub)
            payload = {
                "_prompt_version": PROMPT_VERSION,
                "source_url": doc["source_url"],
                "author": doc["author"],
                "subdoc_id": sid,
                "label": sub.get("label"),
                "title": sub.get("title_local") or doc["title"],
                "year": doc.get("year"),
                "meta": meta,
            }
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")
            ok += 1
        except Exception as e:
            print(f"  ! meta failed {slug}/{sid}: {e}")
            fail += 1
    return slug, ok, fail


def _build_priority_index() -> dict:
    """从 manifest.json 读取每个 url 的 priority"""
    if not MANIFEST_PATH.exists():
        return {}
    try:
        items = json.loads(MANIFEST_PATH.read_text("utf-8"))
        # key = url; 也按 local_path 文件名做映射
        idx = {}
        for it in items:
            lp = it.get("local_path", "")
            stem = Path(lp).stem
            idx[stem] = it.get("priority", 1)
        return idx
    except Exception:
        return {}


def main():
    if not IN_DIR.exists():
        print("ERR: 先跑 01d_segment.py")
        sys.exit(1)
    pidx = _build_priority_index()
    files = list(IN_DIR.rglob("*.json"))
    # 按优先级排序：priority 0 (核心) 在前
    files.sort(key=lambda f: (pidx.get(f.stem, 1), str(f)))
    print(f"02a_meta: {len(files)} files, MAX_WORKERS={MAX_WORKERS}")
    total_ok, total_fail = 0, 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(process_one, f): f for f in files}
        done = 0
        for fut in as_completed(futs):
            done += 1
            try:
                slug, ok, fail = fut.result()
                total_ok += ok
                total_fail += fail
                if done % 10 == 0 or done == len(files):
                    print(f"  [{done}/{len(files)}] {slug}: +{ok} ok / +{fail} fail (cum {total_ok}/{total_fail})")
            except Exception as e:
                print(f"  ! worker error: {e}")
    print(f"02a_meta done: ok={total_ok} fail={total_fail}")


if __name__ == "__main__":
    main()
