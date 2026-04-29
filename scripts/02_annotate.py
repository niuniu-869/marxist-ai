#!/usr/bin/env python3
"""
02_annotate.py —— 段落级 annotate（合并 modernize + terms）

每段一次 LLM 调用，输出：gist + plain_rewrite + sentences[].plain + sentences[].notes[]

输入：data/intermediate/01d_segment/<author>/<slug>.json
      data/intermediate/02a_meta/<author>/<slug>__<subdoc_id>.json
输出：data/intermediate/02_annotate/<author>/<slug>__<subdoc_id>__p<n>.json

并发：每个 subdoc 内段落并发 MAX_WORKERS=20
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEG_DIR = ROOT / "data" / "intermediate" / "01d_segment"
META_DIR = ROOT / "data" / "intermediate" / "02a_meta"
OUT_DIR = ROOT / "data" / "intermediate" / "02_annotate"
MANIFEST_PATH = ROOT / "data" / "raw" / "manifest.json"

sys.path.insert(0, str(Path(__file__).parent))
from llm_client import call_llm_json  # noqa: E402
from prompts import load_prompt, PROMPT_VERSION  # noqa: E402

MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "20"))

AUTHOR_NAMES = {"marx": "马克思", "engels": "恩格斯", "lenin": "列宁", "stalin": "斯大林"}


def annotate_paragraph(title: str, author: str, polemic_summary: str,
                       prev_para: str, next_para: str, para: dict) -> dict:
    sentences_input = [
        {"sid": s["sid"], "original": s["original"]}
        for s in para["sentences"]
    ]
    if not sentences_input:
        # 段落无切句结果，跳过
        return {
            "gist": "",
            "plain_rewrite": para["original_plain"],
            "block_type": "title",
            "length_policy": "no_rewrite_or_minimal",
            "sentences": [],
        }
    context = ""
    if prev_para:
        context += f"[前一段] {prev_para[:200]}...\n"
    if next_para:
        context += f"[后一段] {next_para[:200]}...\n"

    sys_prompt = load_prompt("modernize/system.md")
    user_prompt = load_prompt(
        "modernize/user.md",
        para_n=para["n"],
        total="?",  # 总段数对模型不重要
        title=title,
        author=author,
        polemic_target_summary=polemic_summary or "（无明确论战对象）",
        context=context or "（首段或独立段）",
        paragraph_original=para["original_plain"],
        sentences_input=json.dumps(sentences_input, ensure_ascii=False, indent=2),
    )

    result = call_llm_json(sys_prompt, user_prompt, temperature=0.25)

    # 校验
    expected_sids = [s["sid"] for s in sentences_input]
    got_sids = [s.get("sid") for s in result.get("sentences", [])]
    if got_sids != expected_sids:
        # 重试一次：要求严格按 sid 输出
        retry_prompt = user_prompt + "\n\n## 上次输出 sid 不匹配，必须严格按下列顺序输出每个 sid 的 plain：\n" + json.dumps(expected_sids, ensure_ascii=False)
        result = call_llm_json(sys_prompt, retry_prompt, temperature=0.1)
        got_sids = [s.get("sid") for s in result.get("sentences", [])]
        if got_sids != expected_sids:
            # 强制对齐：保留输入 sid + original，把 plain 留空
            print(f"    ⚠️ sid mismatch for p{para['n']}, force-align")
            aligned = []
            got_map = {s.get("sid"): s for s in result.get("sentences", [])}
            for sin in sentences_input:
                g = got_map.get(sin["sid"], {})
                aligned.append({
                    "sid": sin["sid"],
                    "plain": g.get("plain", sin["original"]),
                    "speaker": g.get("speaker", "author"),
                    "stance": g.get("stance", "self"),
                    "notes": g.get("notes", []),
                })
            result["sentences"] = aligned

    return result


def get_polemic_summary(meta: dict) -> str:
    targets = meta.get("polemic_targets", [])
    if not targets:
        return ""
    parts = []
    for t in targets[:3]:
        parts.append(f"{t.get('target_name_zh', t.get('target_id', '?'))}：{t.get('view_being_refuted', '')}")
    return " | ".join(parts)


def process_subdoc(seg_path: Path, sub: dict, meta_payload: dict) -> tuple[int, int]:
    """处理一个 subdoc 内所有段落（段级并发）"""
    rel = seg_path.relative_to(SEG_DIR)
    sid = sub["subdoc_id"]
    out_dir = OUT_DIR / rel.parent / f"{seg_path.stem}__{sid}"
    out_dir.mkdir(parents=True, exist_ok=True)

    title = sub.get("label") or sub.get("title_local") or "?"
    author = AUTHOR_NAMES.get(meta_payload["author"], meta_payload["author"])
    polemic_summary = get_polemic_summary(meta_payload.get("meta", {}))

    paras = sub["paragraphs"]
    tasks = []
    for i, p in enumerate(paras):
        out_path = out_dir / f"p{p['n']:04d}.json"
        if out_path.exists():
            try:
                ex = json.loads(out_path.read_text("utf-8"))
                if ex.get("_prompt_version") == PROMPT_VERSION:
                    continue
            except Exception:
                pass
        prev_p = paras[i - 1]["original_plain"] if i > 0 else ""
        next_p = paras[i + 1]["original_plain"] if i + 1 < len(paras) else ""
        tasks.append((p, prev_p, next_p, out_path))

    ok, fail = 0, 0

    def _run(task):
        p, prev_p, next_p, out_path = task
        try:
            res = annotate_paragraph(title, author, polemic_summary, prev_p, next_p, p)
            payload = {
                "_prompt_version": PROMPT_VERSION,
                "n": p["n"],
                "annotation": res,
            }
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), "utf-8")
            return True
        except Exception as e:
            print(f"  ! ann failed p{p['n']} {seg_path.stem}/{sid}: {e}")
            return False

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(_run, t) for t in tasks]
        for fut in as_completed(futs):
            if fut.result():
                ok += 1
            else:
                fail += 1
    return ok, fail


def _build_priority_index() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        items = json.loads(MANIFEST_PATH.read_text("utf-8"))
        return {Path(it.get("local_path", "")).stem: it.get("priority", 1) for it in items}
    except Exception:
        return {}


def main():
    pidx = _build_priority_index()
    files = list(SEG_DIR.rglob("*.json"))
    files.sort(key=lambda f: (pidx.get(f.stem, 1), str(f)))
    print(f"02_annotate: {len(files)} segment files, MAX_WORKERS={MAX_WORKERS}")
    total_ok, total_fail = 0, 0
    for i, seg_path in enumerate(files):
        rel = seg_path.relative_to(SEG_DIR)
        slug = seg_path.stem
        try:
            doc = json.loads(seg_path.read_text("utf-8"))
        except Exception as e:
            print(f"  ! seg load fail {slug}: {e}")
            continue
        for sub in doc["subdocs"]:
            sid = sub["subdoc_id"]
            meta_path = META_DIR / rel.parent / f"{slug}__{sid}.json"
            if not meta_path.exists():
                # meta 没跑出来，跳过（可后续补）
                continue
            try:
                meta_payload = json.loads(meta_path.read_text("utf-8"))
            except Exception as e:
                print(f"  ! meta load fail {slug}/{sid}: {e}")
                continue
            try:
                ok, fail = process_subdoc(seg_path, sub, meta_payload)
                total_ok += ok
                total_fail += fail
                print(f"  [{i+1}/{len(files)}] {slug}/{sid}: +{ok} ok +{fail} fail (cum {total_ok}/{total_fail})")
            except Exception as e:
                print(f"  ! subdoc fail {slug}/{sid}: {e}")
    print(f"02_annotate done: ok={total_ok} fail={total_fail}")


if __name__ == "__main__":
    main()
