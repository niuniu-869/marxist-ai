# Codex Review · Marxist_ai v0.2 标注质量评审

**评审日期**：2026-04-30
**评审范围**：9 个抽样段（covering 8 种 gate 组合 / 4 位作者）+ 全量自检 (`auto_self_check.json`，9276 段 / 8256 notes)

> codex 由于只读沙箱限制无法写入此文件；本文档由 Claude 落盘 codex 输出。

---

## 总评

**不及格 · 不适合发布给真实读者。**

`gist` 多数能定位段落功能，但 v0.2 的核心支架没有稳定达成：

- gate 漏开明显，历史/典故密集段被判无需支架；
- notes 仍有长短语 concept、循环"指……"解释和错误 type；
- hard_sentences 常挑长句/热闹句，而不是读者真正卡住的句子。

---

## 段级评估

### Sample 1 · engels__18900907 p013 (T,T,T, score=3)
- `gist` 有效。
- `prereading` 有增量，但"反对派=青年派"重复 meta，`source_basis: text_evidence` 不准。
- `hard_sentences` 可用但有原文复述倾向。
- `polemic` target 准确，`their_view` 的"激进代表"证据偏 meta。
- **该改**：p13s4 整句标 `quoted_marx` 有 M3 风险，句内既有恩格斯叙述又有马克思引文，应支持句内 quote 范围。
- 18 岁读者基本能懂。

### Sample 2 · lenin__1915-5 p130 (T,T,T, score=2)
- `prereading` 对"经济主义"和刊物有用，但"司徒卢威式地"高置信补入"生产力论"证据不足。
- `polemic.their_view` 错，把"被列宁视为庸俗化马克思主义"写成论敌观点。
- **该删**：`革命社会民主主义无产阶级分子`（14 字）、`小资产阶级机会主义分子`（11 字）两条 concept note，违反 N1。
- **违规**：`argument_link` 含禁用词"深刻"。

### Sample 3 · engels__18480120 p015 (T,T,F, score=2)
- `prereading` 不合格：`皮费拉利`、`拉察罗尼` 被标为 `person`，但它们是社会群体；
- 且"皮费拉利=小土地所有者"与仓库旧注释"山区牧羊人"冲突。
- **该改**：真正难点是"把绵羊跟山羊分开"（圣经典故），应补 metaphor/hard_sentence；
- p15s5 不符合 `inverted_logic` 触发条件。
- 18 岁读者会卡在典故和意大利群体。

### Sample 4 · marx_manifesto_ch3 p018 (T,F,T, score=2)
- 评估略（codex 未单独展开此段）

### Sample 5 · lenin__19170910 p036 (F,T,T, score=2)
- `gist` 和 hard_sentence 基本有效，能提示这是反问讽刺。
- `prereading=false` 可接受。
- **问题**：`polemic.their_view` 把列宁的讽刺性设问实化为对方明确主张，应写成"被讽刺的托词"。
- 18 岁读者能懂。

### Sample 6 · engels__1884-3 p323 (T,F,F, score=2)
- `gist` 可用。
- `prereading` 解释"罗马王政废除约前 509 年"不是最大障碍。
- **漏点**：真正需要解释的是"所谓无产者"在古罗马语境中不是现代工业无产阶级；
- p323s2 的"公共权力/它/奴隶/无产者"应开 hard_sentence。
- 现有支架不足以让白板用户懂国家暴力逻辑。

### Sample 7 · engels__187606-11 p024 (F,T,F, score=2)
- `needs_prereading=false` **明显错误**。本段密集出现：巴黎六月战斗、马尔摩停战协定、法兰克福议会、普富尔内阁、弗兰格尔。
- hard_sentence 选 p24s20 街垒叙事高潮，漏掉真正难的 p24s5–s12 政治因果链。
- **该删/重写**：`资产阶级` note，它不是概念解释，只是段内评价压缩。

### Sample 8 · engels__187802-03 p013 (F,F,T, score=1)
- `gist` 可用。
- gate 漏开：p13s6 含双重否定和"土利街裁缝代表英国人民"典故，应开 hard_sentence/prereading。
- notes 对"联邦共和起义""根特代表大会"只做名词替换，没解释论证作用；漏掉最影响理解的"土利街裁缝"。
- 18 岁读者不能稳定看懂。

### Sample 9 · stalin__192610 p017 (F,F,F, score=0)
- 署名段处理正确。无需 prereading、hard_sentence、polemic、notes。**可跳过 ✅**

### Sample 10 · engels__1884-3 p060 (F,F,F, score=1)
- `gist` 可用，但 gate 全 false 错。
- `海盗10时代` 明显像脚注/排版残留，应触发 typo/清洗警告；
- "塔西佗时代的德意志人、诺曼人"也需要最小历史说明。
- 18 岁读者只能懂铁器和文字，后半例子会迷路。

---

## 横向问题（跨段反复出现的毛病）

1. **gate 漏开系统性存在**：p24、p13 西班牙、p60 都不该 (F,F,F)。
2. **notes 仍有 v0.1 病根**：长 surface concept、错误 type、循环"指……"解释。
3. **hard_sentence 选择标准偏"长句"**，不是"读者卡点"。
4. **polemic 的 `their_view` 经常写成作者定性**，不是论敌原观点。
5. `auto_self_check.json` 全量数据印证不是抽样偶发：
   - `n1_surface_overflow = 1171` (14.2%)
   - `n2_circular = 1330` (16.1%)
   - `claim_5gram_with_quote = 830`
   - `their_view_eq_response = 477`
6. `家庭、私有制和国家的起源` 样本 `doc_year=1849`，但 meta 写 1884，元数据会污染前端和 prompt。

---

## 该改 prompt 的地方（按优先级）

1. **[HIGH]** `N1/N2/N3` 必须进硬校验，超长 surface 和"指……"空解释**直接丢弃**（不是建议，而是后处理过滤）。
2. **[HIGH]** gate 增加历史密度、典故密度、文本异常触发条件。
3. **[HIGH]** hard_sentence 先判断"最大理解障碍"，不要只选长句。
4. **[HIGH]** polemic 明确：`their_view` 只能写论敌观点，作者定性进 `author_response`。
5. **[MID]** prereading 优先解释会导致误读的词（如"所谓无产者"），不要只补年代。
6. **[MID]** 禁用评价词扫描所有 annotation 字段（包括 argument_link、importance_reason）。
7. **[MID]** 支持句内引文范围，避免整句 speaker 误标。
8. **[LOW]** 增加 `social_group` 类型或禁止把社会群体（如"皮费拉利""拉察罗尼"）标 `person`。

---

## 是否值得发布给真实读者？

**现状：否。**

**必修项**：
- 硬校验 notes（N1/N2/N3 强制后处理过滤）
- 重做 gate 触发逻辑
- 修正 polemic 边界
- 句内引文范围支持

**可改项（不阻塞）**：
- 署名/标题段保持极简
- 增加 `doc_year` 一致性校验
- hard_sentence 增加"为什么选这句"的内部自检

---

*评审 by codex-cli 0.125.0；样本与全量自检数据见同目录 samples.json / auto_self_check.json*
