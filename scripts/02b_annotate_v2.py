#!/usr/bin/env python3
"""
02b_annotate_v2.py —— v0.2 「读懂支架」段级标注

每段一次 LLM 调用，输出：
  - block_type / gist / importance_score / argument_role / argument_link
  - paragraph_gates（4 个布尔 + reason）
  - prereading_refs / prereading_inline （仅 gate 命中时）
  - hard_sentences （仅 gate 命中时，最多 2 条）
  - polemic_in_paragraph （仅 gate 命中时）
  - sentences[].speaker / stance / notes

输入：
  - data/intermediate/01d_segment/<author>/<slug>.json
  - data/intermediate/02a_meta/<author>/<slug>__<sid>.json   (v0.1 meta，复用)

输出：
  - data/intermediate/02b_annotate_v2/<author>/<slug>__<sid>/p####.json

环境变量：
  PILOT_SLUGS  逗号分隔的 slug 关键词（命中即跑），不设则全量
  MAX_WORKERS  默认 20
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEG_DIR = ROOT / "data" / "intermediate" / "01d_segment"
META_DIR = ROOT / "data" / "intermediate" / "02a_meta"
OUT_DIR = ROOT / "data" / "intermediate" / "02b_annotate_v2"
MANIFEST_PATH = ROOT / "data" / "raw" / "manifest.json"

# 用 prompts_v2 加载器（独立于 v0.1）
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "prompts_v2"))

from llm_client import call_llm_json  # noqa: E402

# 切换到 v2 prompts 目录加载（用绝对路径方式）
import importlib.util
PROMPTS_V2 = Path(__file__).parent / "prompts_v2"
spec = importlib.util.spec_from_file_location("prompts_v2_loader", PROMPTS_V2 / "__init__.py")
prompts_v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts_v2)
PROMPT_VERSION_V2 = prompts_v2.PROMPT_VERSION
load_prompt_v2 = prompts_v2.load_prompt

MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "20"))
PILOT_SLUGS = os.environ.get("PILOT_SLUGS", "").strip()

AUTHOR_NAMES = {"marx": "马克思", "engels": "恩格斯", "lenin": "列宁", "stalin": "斯大林"}


# =====================================================================
# 输入构造
# =====================================================================

def get_local_glossary_brief(meta: dict) -> str:
    """v0.1 meta 没有 local_glossary 字段，返回空。v0.2 跑 meta 后会有。"""
    glos = meta.get("local_glossary", [])
    if not glos:
        return "（暂无 local_glossary，本段如需展开术语，按 prereading_inline 处理）"
    lines = []
    for g in glos[:20]:
        lines.append(f"  - {g.get('term_id','?')}: {g.get('surface_zh','?')} → {g.get('definition','')[:80]}")
    return "\n".join(lines)


def get_polemic_targets_brief(meta: dict) -> str:
    targets = meta.get("polemic_targets", [])
    if not targets:
        return "（无明确论战对象）"
    lines = []
    for t in targets[:5]:
        lines.append(f"  - {t.get('target_name_zh') or t.get('target_id','?')}: {t.get('view_being_refuted','')[:80]}")
    return "\n".join(lines)


def gen_annotation(title: str, author: str, written_at: str,
                   historical_context: str, polemic_targets_brief: str,
                   local_glossary_brief: str,
                   prev_para_gist: str,
                   para: dict, total: int) -> dict:
    sentences_input = [
        {"sid": s["sid"], "original": s["original"]}
        for s in para["sentences"]
    ]
    if not sentences_input:
        return _stub_for_empty_para()

    sys_prompt = load_prompt_v2("annotate/system.md")
    user_prompt = load_prompt_v2(
        "annotate/user.md",
        para_n=para["n"],
        total=total,
        title=title,
        author=author,
        written_at=written_at or "(年代不详)",
        historical_context=(historical_context or "")[:1500],
        polemic_targets_brief=polemic_targets_brief,
        local_glossary_brief=local_glossary_brief,
        prev_para_gist=(prev_para_gist or "")[:200],
        paragraph_original=para["original_plain"],
        sentences_input=json.dumps(sentences_input, ensure_ascii=False, indent=2),
    )
    result = call_llm_json(sys_prompt, user_prompt, temperature=0.2)

    # 强校验：sid 必须对齐
    expected_sids = [s["sid"] for s in sentences_input]
    got_sids = [s.get("sid") for s in result.get("sentences", [])]
    if got_sids != expected_sids:
        # 重试 1 次
        retry = user_prompt + (
            "\n\n## 上次输出 sid 不对齐。**严格按下列 sid 列表逐项输出 sentences[]**：\n"
            + json.dumps(expected_sids, ensure_ascii=False)
        )
        result = call_llm_json(sys_prompt, retry, temperature=0.05)
        got_sids = [s.get("sid") for s in result.get("sentences", [])]
        if got_sids != expected_sids:
            # 强制对齐（按输入 sid 顺序，缺的补默认）
            got_map = {s.get("sid"): s for s in result.get("sentences", [])}
            aligned = []
            for sin in sentences_input:
                g = got_map.get(sin["sid"], {})
                aligned.append({
                    "sid": sin["sid"],
                    "speaker": g.get("speaker", "author"),
                    "stance": g.get("stance", "self"),
                    "notes": g.get("notes", []),
                })
            result["sentences"] = aligned
    return result


def _stub_for_empty_para() -> dict:
    return {
        "block_type": "title",
        "gist": "",
        "importance_score": 0,
        "importance_reason": "empty_paragraph",
        "argument_role": "none",
        "argument_link": None,
        "paragraph_gates": {
            "needs_prereading": False,
            "prereading_reason": "all_known",
            "needs_hard_sentence": False,
            "hard_sentence_reason": "none",
            "needs_polemic": False,
            "polemic_reason": "none",
        },
        "prereading_refs": [],
        "prereading_inline": [],
        "hard_sentences": [],
        "polemic_in_paragraph": {"is_polemical": False, "target": None, "their_view": None, "author_response": None},
        "sentences": [],
    }


# =====================================================================
# 任务调度
# =====================================================================

def process_subdoc(seg_path: Path, sub: dict, meta_payload: dict) -> tuple[int, int]:
    rel = seg_path.relative_to(SEG_DIR)
    sid = sub["subdoc_id"]
    out_dir = OUT_DIR / rel.parent / f"{seg_path.stem}__{sid}"
    out_dir.mkdir(parents=True, exist_ok=True)

    title = sub.get("label") or sub.get("title_local") or "?"
    author_name = AUTHOR_NAMES.get(meta_payload["author"], meta_payload["author"])
    meta = meta_payload.get("meta", {})
    written_at = (meta.get("provenance") or {}).get("written_at", "") or ""
    historical_context = meta.get("historical_context", "")
    polemic_brief = get_polemic_targets_brief(meta)
    glos_brief = get_local_glossary_brief(meta)

    paras = sub["paragraphs"]
    total = len(paras)
    tasks = []
    for i, p in enumerate(paras):
        out_path = out_dir / f"p{p['n']:04d}.json"
        if out_path.exists():
            try:
                ex = json.loads(out_path.read_text("utf-8"))
                if ex.get("_prompt_version") == PROMPT_VERSION_V2:
                    continue
            except Exception:
                pass
        prev_gist = ""
        if i > 0:
            # 试着从上一段已写文件中读 gist
            prev_p = paras[i - 1]
            prev_path = out_dir / f"p{prev_p['n']:04d}.json"
            if prev_path.exists():
                try:
                    prev_ann = json.loads(prev_path.read_text("utf-8")).get("annotation", {})
                    prev_gist = prev_ann.get("gist", "")
                except Exception:
                    pass
            if not prev_gist:
                prev_gist = prev_p["original_plain"][:120]
        tasks.append((p, prev_gist, out_path))

    ok, fail = 0, 0

    def _run(task):
        p, prev_gist, out_path = task
        try:
            ann = gen_annotation(
                title, author_name, written_at,
                historical_context, polemic_brief, glos_brief,
                prev_gist, p, total,
            )
            payload = {
                "_prompt_version": PROMPT_VERSION_V2,
                "n": p["n"],
                "annotation": ann,
            }
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")
            return True
        except Exception as e:
            print(f"  ! ann_v2 failed p{p['n']} {seg_path.stem}/{sid}: {e}", flush=True)
            return False

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(_run, t) for t in tasks]
        for fut in as_completed(futs):
            if fut.result():
                ok += 1
            else:
                fail += 1
    return ok, fail


def matches_pilot(seg_path: Path) -> bool:
    if not PILOT_SLUGS:
        return True
    keys = [k.strip().lower() for k in PILOT_SLUGS.split(",") if k.strip()]
    name = str(seg_path).lower()
    return any(k in name for k in keys)


def main():
    files = sorted(SEG_DIR.rglob("*.json"))
    files = [f for f in files if matches_pilot(f)]
    print(f"02b_annotate_v2: {len(files)} segment files (PILOT_SLUGS={PILOT_SLUGS or 'ALL'}), MAX_WORKERS={MAX_WORKERS}", flush=True)
    print(f"prompt version: {PROMPT_VERSION_V2}", flush=True)

    total_ok, total_fail = 0, 0
    for i, seg_path in enumerate(files):
        rel = seg_path.relative_to(SEG_DIR)
        slug = seg_path.stem
        try:
            doc = json.loads(seg_path.read_text("utf-8"))
        except Exception as e:
            print(f"  ! seg load fail {slug}: {e}", flush=True)
            continue
        for sub in doc["subdocs"]:
            sid = sub["subdoc_id"]
            meta_path = META_DIR / rel.parent / f"{slug}__{sid}.json"
            if not meta_path.exists():
                continue
            try:
                meta_payload = json.loads(meta_path.read_text("utf-8"))
            except Exception as e:
                print(f"  ! meta load fail {slug}/{sid}: {e}", flush=True)
                continue
            try:
                ok, fail = process_subdoc(seg_path, sub, meta_payload)
                total_ok += ok
                total_fail += fail
                print(f"  [{i+1}/{len(files)}] {slug}/{sid}: +{ok} ok +{fail} fail (cum {total_ok}/{total_fail})", flush=True)
            except Exception as e:
                print(f"  ! subdoc fail {slug}/{sid}: {e}", flush=True)
    print(f"02b_annotate_v2 done: ok={total_ok} fail={total_fail}", flush=True)


if __name__ == "__main__":
    main()
