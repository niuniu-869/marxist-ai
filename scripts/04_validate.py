#!/usr/bin/env python3
"""
04_validate.py —— v0.3 后处理硬规则校验 + 修复

功能：
  1. 扫描 data/intermediate/02b_annotate_v2/**/*.json
  2. 删除违反硬规则的 notes / hard_sentences / polemic 字段
  3. 输出修复版到原位置（可选 --dry-run 只统计）
  4. 输出 docs/validation_report.json 含违规率、采样

硬规则（来自 codex review）：
  N1   surface 超长（含必保留术语豁免清单）
  N2   modern 以 指/即/就是/是指 开头 OR modern == surface OR modern 与 surface 5-gram 重合
  N3   concept surface 命中黑名单形态（动宾/因果/整句/描述性长定语/泛指词）
  N4   concept 缺 sense_id
  EVAL 评价词扫描所有字段
  HS   hard_sentences.parse.claim 与 quote 5-gram 重合
  POL  polemic their_view 与 author_response 5-gram 重合 OR their_view 含定性词

使用：
  python3 scripts/04_validate.py            # 扫描 + 修复
  python3 scripts/04_validate.py --dry-run  # 只统计不写
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANN_DIR = ROOT / "data" / "intermediate" / "02b_annotate_v2"
REPORT = ROOT / "docs" / "validation_report.json"

SURFACE_LIMITS = {
    "concept": 5, "metaphor": 8, "archaic": 4,
    "person": 12, "place": 10, "org": 16,
    "work": 16, "event": 12, "social_group": 12,
    "slogan": 12, "program_clause": 24,
}

# concept 长度豁免（核心范畴优先于长度规则）
CONCEPT_WHITELIST_LONG = {
    "无产阶级专政", "无产阶级革命", "资产阶级专政", "资产阶级革命",
    "无产阶级民主", "资产阶级民主", "社会沙文主义", "社会民主主义",
    "经济基础", "上层建筑", "生产资料", "生产关系", "生产力",
    "商品拜物教", "交换价值", "使用价值", "剩余价值", "剩余劳动",
    "雇佣劳动", "异化劳动",
    "辩证唯物主义", "历史唯物主义", "科学社会主义", "空想社会主义",
    "唯物辩证法", "形而上学",
    "机会主义", "修正主义", "教条主义", "经验主义",
    "工联主义", "无政府主义", "考茨基主义", "托洛茨基主义",
    "帝国主义", "超帝国主义", "垄断资本主义", "金融资本",
    "小资产阶级", "大资产阶级",
}

# N2 循环复述前缀
CIRCULAR_PREFIXES = ("指", "即", "就是", "是指")

# N3 黑名单形态正则
N3_BLACKLIST_PATTERNS = [
    re.compile(r".+了.+"),       # 含动词时态："丧失了""排除了"
    re.compile(r"由于.+"),
    re.compile(r"为了.+"),
    re.compile(r".+实施.+"),
    re.compile(r".+进行.+"),
    re.compile(r".+放弃.+"),
    re.compile(r".+反对.+"),
    re.compile(r".+成为.+"),
]

# N3 泛指词单独标 concept 禁止
N3_VAGUE_SINGLETONS = {"上层", "下层", "方面", "时期", "社会", "群体", "层面", "范畴", "对象"}

# 评价词扫描
EVAL_WORDS = [
    "伟大", "光辉", "深刻", "英明", "精辟", "杰出", "卓越", "划时代", "历史性",
    "科学地证明", "完美地阐述", "彻底地揭示", "一针见血", "高瞻远瞩",
    "反动透顶",
    "积极地", "完美地", "极为", "极其重要", "至关重要",
    "具有划时代意义", "具有深远影响",
]

# polemic.their_view 不准的定性词（论敌不会这么形容自己）
POLEMIC_THEIR_VIEW_FORBIDDEN = [
    "被作者", "被列宁", "被马克思", "被恩格斯", "被斯大林",
    "被批判", "被视为", "被定性为", "错误地", "庸俗化",
    "粗糙的辩护", "拙劣的", "反动的",
]


def has_5gram_overlap(s1: str, s2: str, n: int = 5) -> bool:
    if not s1 or not s2 or len(s1) < n or len(s2) < n:
        return False
    grams = {s1[i:i+n] for i in range(len(s1) - n + 1)}
    return any(s2[i:i+n] in grams for i in range(len(s2) - n + 1))


def contains_any(text: str, words: list[str]) -> str | None:
    for w in words:
        if w in text:
            return w
    return None


def field_text(obj, *paths) -> str:
    """安全取嵌套字段为字符串"""
    cur = obj
    for p in paths:
        if not isinstance(cur, dict):
            return ""
        cur = cur.get(p)
    if isinstance(cur, str):
        return cur
    return ""


def validate_note(note: dict, original_text: str) -> tuple[bool, str]:
    """返回 (合法, 删除原因)"""
    surface = (note.get("surface") or "").strip()
    modern = (note.get("modern") or "").strip()
    ntype = note.get("type")

    # 空 note
    if not surface or not modern:
        return False, "empty"

    # N1
    limit = SURFACE_LIMITS.get(ntype)
    if limit and len(surface) > limit:
        if ntype == "concept" and surface in CONCEPT_WHITELIST_LONG:
            pass  # 豁免
        else:
            return False, f"n1_overflow_{ntype}_{len(surface)}>{limit}"

    # N2 循环复述
    if any(modern.startswith(p) for p in CIRCULAR_PREFIXES):
        return False, "n2_circular_prefix"
    if modern.strip() == surface.strip():
        return False, "n2_eq_surface"
    if has_5gram_overlap(modern, surface):
        return False, "n2_5gram_with_surface"

    # N3 concept 黑名单
    if ntype == "concept":
        if surface in N3_VAGUE_SINGLETONS:
            return False, "n3_vague_singleton"
        for pat in N3_BLACKLIST_PATTERNS:
            if pat.fullmatch(surface):
                return False, "n3_blacklist_pattern"
        # N4 sense_id
        if not note.get("sense_id"):
            return False, "n4_concept_no_sense_id"

    # 评价词扫描 modern
    hit = contains_any(modern, EVAL_WORDS)
    if hit:
        return False, f"eval_word:{hit}"

    # confidence: low 不展示，但不丢弃（保留以便后续审计；merge 阶段过滤）
    return True, ""


def validate_hard_sentence(hs: dict) -> tuple[bool, str]:
    quote = (hs.get("quote") or "").strip()
    parse = hs.get("parse") or {}
    claim = (parse.get("claim") or "").strip()

    if not quote or not claim:
        return False, "empty"

    # claim 与 quote 5-gram 重合
    if has_5gram_overlap(quote, claim):
        return False, "claim_5gram_with_quote"

    # 评价词扫描
    explain = field_text(hs, "why", "explanation")
    impl = (hs.get("implication") or "").strip()
    reader_block = (hs.get("reader_block") or "").strip()
    for f, name in [(claim, "claim"), (explain, "explanation"),
                     (impl, "implication"), (reader_block, "reader_block")]:
        hit = contains_any(f, EVAL_WORDS)
        if hit:
            return False, f"eval_word:{name}:{hit}"

    return True, ""


def validate_polemic(pol: dict) -> tuple[bool, str]:
    if not pol.get("is_polemical"):
        return True, ""
    tv = (pol.get("their_view") or "").strip()
    ar = (pol.get("author_response") or "").strip()

    if not tv or not ar:
        return False, "polemic_empty_field"

    # their_view 含定性词
    hit = contains_any(tv, POLEMIC_THEIR_VIEW_FORBIDDEN)
    if hit:
        return False, f"polemic_their_view_qualifier:{hit}"

    # 评价词
    for f, name in [(tv, "their_view"), (ar, "author_response"),
                     (pol.get("target") or "", "target")]:
        hit = contains_any(f, EVAL_WORDS)
        if hit:
            return False, f"eval_word:{name}:{hit}"

    # their_view ≈ author_response 5-gram
    if has_5gram_overlap(tv, ar):
        return False, "their_view_eq_response_5gram"

    return True, ""


def validate_paragraph_evals(ann: dict) -> list[str]:
    """扫描段级字段评价词，返回违规字段列表"""
    issues = []
    for f in ["gist", "argument_link", "importance_reason"]:
        v = (ann.get(f) or "").strip()
        hit = contains_any(v, EVAL_WORDS)
        if hit:
            issues.append(f"{f}:{hit}")
    return issues


def process_file(p: Path, dry_run: bool) -> dict:
    """处理单文件，返回违规统计"""
    try:
        d = json.loads(p.read_text("utf-8"))
    except Exception:
        return {"file_load_error": 1}
    a = d.get("annotation")
    if not isinstance(a, dict):
        return {}

    stats = {
        "notes_kept": 0, "notes_dropped": 0,
        "hs_kept": 0, "hs_dropped": 0,
        "polemic_zeroed": 0,
        "para_eval_issues": 0,
    }
    drop_reasons = []

    # 段级评价词
    para_evals = validate_paragraph_evals(a)
    if para_evals:
        stats["para_eval_issues"] = len(para_evals)
        # 评价词命中段级字段：把字段清空（保守做法，避免污染前端）
        for issue in para_evals:
            field, _hit = issue.split(":", 1)
            a[field] = ""

    # 句级 notes
    paragraph_text = a.get("gist", "")
    for s in a.get("sentences", []):
        kept = []
        for n in (s.get("notes") or []):
            ok, reason = validate_note(n, paragraph_text)
            if ok:
                kept.append(n); stats["notes_kept"] += 1
            else:
                stats["notes_dropped"] += 1
                drop_reasons.append(("note", reason))
        s["notes"] = kept

    # hard_sentences
    kept_hs = []
    for hs in (a.get("hard_sentences") or []):
        ok, reason = validate_hard_sentence(hs)
        if ok:
            kept_hs.append(hs); stats["hs_kept"] += 1
        else:
            stats["hs_dropped"] += 1
            drop_reasons.append(("hs", reason))
    a["hard_sentences"] = kept_hs

    # polemic
    pol = a.get("polemic_in_paragraph")
    if pol and pol.get("is_polemical"):
        ok, reason = validate_polemic(pol)
        if not ok:
            stats["polemic_zeroed"] += 1
            drop_reasons.append(("polemic", reason))
            a["polemic_in_paragraph"] = {
                "is_polemical": False, "target": None,
                "their_view": None, "author_response": None,
                "polemic_kind": None, "confidence": None,
            }

    if not dry_run and (stats["notes_dropped"] or stats["hs_dropped"] or
                         stats["polemic_zeroed"] or stats["para_eval_issues"]):
        # 标记本文件已被 04_validate 修复
        d.setdefault("_validate_passes", []).append({
            "version": "v0.3-validate",
            "stats": stats,
            "reasons": [f"{k}:{v}" for k, v in drop_reasons[:30]],
        })
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), "utf-8")

    return {**stats, "drop_reasons": drop_reasons}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=str(ANN_DIR), help="ann dir")
    args = ap.parse_args()

    root = Path(args.root)
    files = sorted(root.rglob("p*.json"))
    print(f"扫描 {len(files)} 文件 from {root}", flush=True)

    agg = {
        "files_processed": 0,
        "notes_kept": 0, "notes_dropped": 0,
        "hs_kept": 0, "hs_dropped": 0,
        "polemic_zeroed": 0,
        "para_eval_issues": 0,
    }
    all_reasons = {}

    for i, p in enumerate(files):
        s = process_file(p, args.dry_run)
        agg["files_processed"] += 1
        for k in ["notes_kept", "notes_dropped", "hs_kept", "hs_dropped",
                   "polemic_zeroed", "para_eval_issues"]:
            agg[k] += s.get(k, 0)
        for kind, reason in s.get("drop_reasons", []):
            key = f"{kind}:{reason}"
            all_reasons[key] = all_reasons.get(key, 0) + 1
        if (i + 1) % 1000 == 0:
            print(f"  [{i+1}/{len(files)}] notes_dropped={agg['notes_dropped']} hs_dropped={agg['hs_dropped']}", flush=True)

    total_notes = agg["notes_kept"] + agg["notes_dropped"]
    total_hs = agg["hs_kept"] + agg["hs_dropped"]
    print(f"\n=== 04_validate 报告 ===")
    print(f"  files: {agg['files_processed']}")
    print(f"  notes: {agg['notes_kept']} 保留 / {agg['notes_dropped']} 删除"
          f" ({agg['notes_dropped']*100/max(total_notes,1):.2f}%)")
    print(f"  hard_sentences: {agg['hs_kept']} 保留 / {agg['hs_dropped']} 删除"
          f" ({agg['hs_dropped']*100/max(total_hs,1):.2f}%)")
    print(f"  polemic 清零: {agg['polemic_zeroed']}")
    print(f"  段级评价词违规字段: {agg['para_eval_issues']}")

    print(f"\n违规原因 Top 15:")
    for reason, c in sorted(all_reasons.items(), key=lambda x: -x[1])[:15]:
        print(f"  {c:5d}  {reason}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "summary": agg,
        "drop_reasons": dict(sorted(all_reasons.items(), key=lambda x: -x[1])),
        "dry_run": args.dry_run,
    }, ensure_ascii=False, indent=2), "utf-8")
    print(f"\n✅ 报告: {REPORT}")


if __name__ == "__main__":
    main()
