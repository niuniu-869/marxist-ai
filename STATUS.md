# Marxist_ai 全量跑量状态（晨起验收用）

> 启动：2026-04-30 03:22
> 预期跑到：2026-04-30 11:00 ± 1h
> 模型：mimo-v2.5 / RPM 100 / MAX_WORKERS 20

## 一句话状态

把 marxists.org/chinese 上马恩列斯的全部"著作"区域文献（估 800-1500 篇）拉下来，跑四阶段管线（抓取 → 切分 → 篇章 meta → 段级 annotate），输出"21 世纪说人话"标注 JSON。

按"核心文献优先"排序，预期 8 小时窗口内能完整跑完 200-400 篇核心文献的 meta + 段级标注（含 gist/plain_rewrite/逐句白话/术语卡）。

## 怎么验收

```bash
cd /niuniu869_dev/Marxist_ai
# 1. 看进度
tail -50 logs/monitor.log

# 2. 看 nohup 是否还在跑（应至少有 2 个进程）
ps aux | grep -E "python3.*Marxist|monitor.sh" | grep -v grep

# 3. 看产出
find data/books/marxists/documents -name '*.json' | wc -l
ls data/books/marxists/documents/marx/ | head

# 4. 抽一篇看质量
python3 -c "
import json, glob
files = glob.glob('data/books/marxists/documents/marx/*.json')
files.sort()
d = json.load(open(files[0]))
print('==>', d['title'])
print('TLDR:', d['meta'].get('tldr_modern',''))
print('段落数:', len(d['paragraphs']))
print()
for p in d['paragraphs'][:3]:
    print(f'--- 段 {p[\"n\"]} ---')
    print('原文:', p['original_plain'][:120])
    print('白话:', (p.get('plain_rewrite') or '')[:120])
    print('段意:', p.get('gist',''))
    print()
"
```

## 已知问题 / 待你拍板

1. **优先级关键词太宽**：harvest priority 0 标了几乎所有 85 篇——会按字典序跑，不严格按"核心程度"。早晨醒来如果发现核心文献没跑完，是这个原因。改进留给 v0.2。

2. **共产党宣言 split 时 manifesto_ch1/2/3/4 重复检测**（目录与正文都匹配同一 pattern），会有重复 subdoc。不影响内容但会有重复 LLM 调用。

3. **prompt 较大**（speak_human_rules.md 约 2k 字符 + modernize/user.md 约 4k）。如果晨起发现吞吐慢，可以缩短规则到核心 5 条 + 关键禁词列表。

4. **段级 annotate 单次 22-25s**，不算快但稳。8 小时 × 20 并发 ≈ 25000 calls，如果总段数 > 25000 会跑不完——按优先级跑，core 文献保证。

5. **没做 04_validate / 03_merge 还没自动跑**——run_all.py 会在 annotate 后自动 merge，但 validate 留给手动。早起后如果 annotate 已完成，可手动 `python3 scripts/04_validate.py`（暂未实现，得现写）。

## 管线五段

| 阶段 | 脚本 | LLM | 输入 | 输出 |
|---|---|---|---|---|
| 1. harvest | `01_harvest.py` | 否 | marxists.org/chinese | `data/raw/<author>/*.html` (gb18030→utf8) + `manifest.json` |
| 2. split | `01b_split.py` | 否 | raw HTML | `data/intermediate/01b_split/<author>/*.json`（含 subdocs / paragraphs / footnotes / provenance） |
| 3. segment | `01d_segment.py` | 否 | split | `data/intermediate/01d_segment/<author>/*.json`（每段 sentences[] 带 sid + char_start/end） |
| 4. meta | `02a_meta.py` | 是 | segment | `data/intermediate/02a_meta/<author>/<slug>__<subdoc_id>.json`（每 subdoc 一次 LLM：tldr/historical_context/polemic_targets/key_concepts/provenance/...） |
| 5. annotate | `02_annotate.py` | 是 | segment + meta | `data/intermediate/02_annotate/<author>/<slug>__<subdoc_id>/p####.json`（每段一次 LLM：gist/plain_rewrite/句级 plain/notes） |
| 6. merge | `03_merge.py` | 否 | 上面所有 | `data/books/marxists/documents/<author>/<year>_<slug>__<subdoc_id>.json`（最终成品） |

## "说人话"硬约束（M1-M7）

写在 `scripts/prompts/rules/speak_human_rules.md`，每次 02_annotate 调用都包含：

- **M1** 不准改观点（必保留术语清单 + 禁止替换映射，如"无产阶级"≠"打工人"、"专政"≠"治理"）
- **M2** 不准发明事实（不编年代/事件、严禁现代政治类比）
- **M3** 论战对象显名（句级 speaker/stance 字段）
- **M4** 时空指代具体化
- **M5** 核心比喻原句保留（鸦片/幽灵/枷锁/国家机器/上层建筑等）
- **M6** 老译晦涩词在 notes 给现代等价（原句不替换）
- **M7** 客观中立（禁评价词"伟大""光辉""精辟"）

## codex review 已吸收

- 双层 meta：deterministic provenance parser → LLM 用证据组织文字
- 句子级 deterministic 切分（不让 LLM 自切句，保 sid/char_start/end 稳定）
- 句级 speaker / stance 字段防止把论敌观点误当作者观点
- evidence 字段（meta 任何事实都要给来源）
- block_type / length_policy 防止格言/标题/引文 block 被强制改写

## 还未做的（v0.2 留作）

- 04_validate.py（M1-M7 硬规则机检 + LLM-as-judge）
- 02d_glossary.py（人名/概念词典共建）
- 01c_seed_glossary.py（从自带人名索引提种子）
- 前端 Astro 集成

## 启动命令（如果 nohup 死了你重启）

```bash
cd /niuniu869_dev/Marxist_ai
nohup python3 scripts/run_all.py > logs/run_all_$(date +%Y%m%d_%H%M%S).out 2>&1 &
nohup ./monitor.sh > logs/monitor.out 2>&1 &
disown
```
