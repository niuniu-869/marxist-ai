#!/usr/bin/env python3
"""
01d_segment.py —— 段落 → 句子级确定性切分（不让 LLM 自行切句）

输入：data/intermediate/01b_split/<author>/<slug>.json
输出：data/intermediate/01d_segment/<author>/<slug>.json
  paragraphs[].sentences[]: { sid, original, char_start, char_end }

切分规则：
- 中文标点 。！？ 和 ；为强切点
- 引号""'' 内的标点不切
- 「『」』 内不切
- 长度 > 200 字仍未切则强制按 ， 切
- 长度 < 8 字的"句"合并到上一句
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "data" / "intermediate" / "01b_split"
OUT_DIR = ROOT / "data" / "intermediate" / "01d_segment"

sys.path.insert(0, str(Path(__file__).parent))
from prompts import PROMPT_VERSION  # noqa: E402

# 强切点：在引号外的 。！？；
STRONG_BREAK = set("。！？")
# 弱切点（仅 > 200 字时使用）
WEAK_BREAK = set("，")
# 引号配对
QUOTE_OPEN = "“‘「『（《"
QUOTE_CLOSE = "”’」』）》"


def split_sentences(text: str) -> list[tuple[int, int]]:
    """返回 [(start, end), ...]，end 包含标点"""
    if not text:
        return []
    spans = []
    n = len(text)
    depth = 0
    last = 0
    i = 0
    while i < n:
        c = text[i]
        if c in QUOTE_OPEN:
            depth += 1
        elif c in QUOTE_CLOSE:
            depth = max(0, depth - 1)
        if depth == 0 and c in STRONG_BREAK:
            # 处理省略号 ......
            j = i
            while j + 1 < n and text[j + 1] == c:
                j += 1
            spans.append((last, j + 1))
            last = j + 1
            i = j + 1
            continue
        # ；也作切点
        if depth == 0 and c == "；":
            spans.append((last, i + 1))
            last = i + 1
        i += 1
    if last < n:
        spans.append((last, n))

    # 二次处理：长度 > 200 字的句子按 ， 强切
    refined = []
    for s, e in spans:
        seg = text[s:e]
        if len(seg) <= 200:
            refined.append((s, e))
            continue
        # 内部 ， 切
        sub_last = 0
        sub_depth = 0
        for j in range(len(seg)):
            cc = seg[j]
            if cc in QUOTE_OPEN:
                sub_depth += 1
            elif cc in QUOTE_CLOSE:
                sub_depth = max(0, sub_depth - 1)
            if sub_depth == 0 and cc == "，" and j - sub_last > 80:
                refined.append((s + sub_last, s + j + 1))
                sub_last = j + 1
        if sub_last < len(seg):
            refined.append((s + sub_last, e))

    # 三次处理：合并 < 8 字的小段到前一句
    merged = []
    for s, e in refined:
        seg = text[s:e].strip()
        if not seg:
            continue
        if len(seg) < 8 and merged:
            ps, pe = merged[-1]
            merged[-1] = (ps, e)
        else:
            merged.append((s, e))

    # 去掉首尾空白对应的边界
    cleaned = []
    for s, e in merged:
        seg = text[s:e]
        # 调整 s 跳过空白
        ss = s
        while ss < e and text[ss] in " \t\n　":
            ss += 1
        ee = e
        while ee > ss and text[ee - 1] in " \t\n":
            ee -= 1
        if ee > ss:
            cleaned.append((ss, ee))
    return cleaned


def segment_doc(doc: dict) -> dict:
    for sub in doc["subdocs"]:
        for p in sub["paragraphs"]:
            text = p["original_plain"]
            spans = split_sentences(text)
            sentences = []
            for k, (s, e) in enumerate(spans):
                sentences.append({
                    "sid": f"p{p['n']}s{k+1}",
                    "original": text[s:e].strip(),
                    "char_start": s,
                    "char_end": e,
                })
            p["sentences"] = sentences
    doc["_prompt_version"] = PROMPT_VERSION
    return doc


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok, skip, fail = 0, 0, 0
    for jf in IN_DIR.rglob("*.json"):
        rel = jf.relative_to(IN_DIR)
        out_path = OUT_DIR / rel
        if out_path.exists():
            try:
                ex = json.loads(out_path.read_text("utf-8"))
                if ex.get("_prompt_version") == PROMPT_VERSION:
                    skip += 1
                    continue
            except Exception:
                pass
        try:
            doc = json.loads(jf.read_text("utf-8"))
            result = segment_doc(doc)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), "utf-8")
            ok += 1
        except Exception as e:
            print(f"  ! seg failed {jf}: {e}")
            fail += 1
    print(f"segment: ok={ok} skip={skip} fail={fail}")


if __name__ == "__main__":
    main()
