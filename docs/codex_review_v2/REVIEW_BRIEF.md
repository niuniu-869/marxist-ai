# Codex Review · Marxist_ai v0.2 标注质量

## 背景

`Marxist_ai` 是把 marxists.org/chinese 的马恩列斯中文译文做成"AI 标注阅读器"。v0.1 失败（plain_rewrite 是同义词替换、白话比原文还难懂），v0.2 重做：**不再翻译原文**，改成 **「在原文上加四种脚手架」**：

```
原文（1 字未改，主角）
  ├── gist                      段意 30-60 字
  ├── prereading_inline / refs  读前须知（术语/史实/代词指代）
  ├── hard_sentences            难句结构化拆解 (claim/qualifiers/contrast + why/implication)
  └── polemic_in_paragraph      在反对谁（target/their_view/author_response）
```

外加段级 `importance_score` 0-3 + `argument_role` + `block_type`，句级 `speaker/stance + notes`。

**目标用户**：18 岁第一次读马列的大学生 + 80 岁奶奶。**不是**马列研究生。

## 当前状态

- v0.2 全量重跑中，已完成 9181/21194 段（43%）。
- 60.6% 的段被 LLM 判为 (F,F,F)（无任何支架），21.7% 仅 polemic，3% 全开（T,T,T）。
- gate 分布详见 samples.json。

## 你的任务

抽 9 段样本（`samples.json`，覆盖不同 gate 组合 + 不同作者 + 不同 importance_score），**严苛地**判定：

> **一个第一次读马列的大学生看到这段原文 + 我们这套支架，是不是真的能看懂？还是只看到一堆 AI slop？**

请按以下五个维度逐段（或分组）打分 + 举证：

### 维度 1：脚手架是否真给读者增加了信息？

判定每个 prereading_inline / hard_sentences / polemic 字段：

- **+1 真增量**：读者看完支架理解显著好于只看原文
- **0 中性**：信息正确但读者本来就懂 / 不影响理解
- **−1 负价值**：循环复述原文（用更多字说同一件事）/ 装样子（说了等于没说）/ 错误/误导

**特别警惕**：
- `gist` 是"在干什么"还是"原文 paraphrase"？
- `hard_sentences.parse.claim` 是否就是把原句去掉修辞照抄？
- `prereading_inline.explain` 是不是百度百科口水话？
- `polemic_in_paragraph.author_response` 是不是把原文最后一句重复？

### 维度 2：notes 是否真有用？

逐条注释审视：
- surface 选词是不是 18 岁读者真的不懂？还是 LLM 在标"显而易见"的词？
- modern 解释是不是循环（"指 X" / "X 是…" / 5-gram 与原句重合）？
- concept + sense_id 是否合理？
- confidence: high 的注释是不是真 high？

**给我一份"该删的 note"清单**。

### 维度 3：gate 判断是否准确？

- 60.6% 段 (F,F,F) — 检查 (F,F,F) 样本（p2 段 / p17 / p60）：是真不需要支架，还是 LLM 偷懒？
- 全开 (T,T,T) 样本：是不是该开的开了，没乱开？
- prereading_reason / hard_sentence_reason / polemic_reason 字段值是否对应触发事实？

### 维度 4：客观性 / M1-M7 rules

是否有：
- 评价词（"伟大""光辉""深刻"）
- 现代政治类比（用今天概念套19世纪）
- 编造历史（具体时间/地名/人名/数据）
- 篡改观点（M1：阶级、革命、专政这些范畴有没有被稀释）
- 论敌没显名（M3：把"反动派"含糊处理）

### 维度 5：白板用户能看懂吗？

挑 1-2 段你觉得最丰富的（importance_score=3 全开），假设你是大一学生：
- 跟着支架读一遍，能不能讲出这段在干啥？
- 有没有一些你觉得"还需要再展开"的地方？

## 输出格式

**严苛、具体、给反例**。不要"总体不错"这种话。我希望看到：

```markdown
## 总评（200 字内）
[非常好 / 还行 / 不及格] · 关键问题 1-3 条

## 段级评估（9 段每段一节）

### Sample 1: engels__18900907 p013 (T,T,T, score=3)

**gist**: ✅/⚠️/❌ — [评语 + 反例]
**prereading_inline**: ...
**hard_sentences**: ...
**polemic**: ...
**notes**: ...

**该删**: [...]
**该改**: [...]
**18 岁读者能看懂吗**: 能 / 不能 + 原因

## 横向问题（跨段反复出现的毛病）

1. ...
2. ...

## 该改 prompt 的地方（按优先级）

1. [HIGH] notes_rules.md 里 N2 没拦住这种 modern: "..."
2. [MID] hard_sentence_rules.md 没禁 contrast_or_target 等于 their_view 抄一遍
3. ...

## 是否值得发布给真实读者？

- 现状：[是 / 否 / 修复 X 后是]
- 必修项：[1-3 条]
- 可改项（不阻塞）：[...]
```

## 禁止
- "整体不错" 这种空话
- 不举具体反例的批评
- 替我重写整篇 prompt（只指出哪里要改 + 改的方向）

## 资料清单

- `samples.json` — 9 段标注产出（含原文、meta 上下文、annotation）
- `../../scripts/prompts_v2/rules/scaffold_philosophy.md`
- `../../scripts/prompts_v2/rules/objectivity_and_stance.md`
- `../../scripts/prompts_v2/rules/notes_rules.md`
- `../../scripts/prompts_v2/rules/hard_sentence_rules.md`
- `../../scripts/prompts_v2/rules/prereading_rules.md`
- `../../scripts/prompts_v2/annotate/user.md`（主 prompt）
- `../postmortem_v0.1_and_plan_b.md`（v0.1 失败复盘 + plan B 设计）
