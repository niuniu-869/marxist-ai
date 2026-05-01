## prereading 规则（v0.3，codex-fixed）

### 触发条件（v0.3 扩展）

`needs_prereading: true` 仅当满足任一条件：

| 条件 | 描述 | v0.2 漏开案例 |
|---|---|---|
| `term_first_use` | 本段首次出现某 LAYER A 术语，且其在本作品中含义需展开（如费尔巴哈语境的"类"、《资本论》语境的"价值"） | 篇章 `local_glossary` 已覆盖则不开 |
| `term_polysemy` | **v0.3 新增** · 同一词在本段需特定 sense，与读者直觉不同（如"无产者"在古罗马 ≠ 现代工人；"民主"指资产阶级民主 vs 无产阶级民主） | engels p323"所谓无产者"漏开 |
| `history_density` | **v0.3 新增** · 段内出现 **≥ 2 个**具体历史专名（人物/事件/组织/法令/会议/刊物），且篇章 `historical_context` 没具体说明 | engels p024 巴黎六月战斗+马尔摩停战+法兰克福议会+普富尔内阁+弗兰格尔，全 false 翻车 |
| `history_missing` | 段中隐指 1 个具体历史事件/人物/法令，读者不查不知；篇章 `historical_context` 未说明 | 单个专名情况 |
| `cross_ref_pronoun` | 段开头/中部用代词（"他们""这种学说""上面所说的"）指向跨段或全篇前文 | 跨段代词 |
| `allusion` | **v0.3 新增** · 段中含圣经/古典/民间典故、隐喻引用（"绵羊跟山羊分开""土利街裁缝") | engels p015"把绵羊跟山羊分开"、p013"土利街裁缝代表英国人民" |
| `text_anomaly` | **v0.3 新增** · 段中明显 typo/排版残留/数字乱码（"海盗10时代"），影响理解 | engels p060"海盗10时代"漏开 |

**疑则 false** 但**遇 history_density / allusion / term_polysemy / text_anomaly 必开**——这些是 v0.2 系统漏开点。

### 输出形式

```jsonc
"prereading_refs": [
  // 引用篇章 local_glossary 中已定义的条目 ID（首选；避免重复定义）
  "feuerbachian_class",
  "1848_european_revolutions"
],
"prereading_inline": [
  // 仅本段独有、glossary 未覆盖、必须现场说明的内容
  {
    "topic": "（5-15 字关键词）",
    "explain": "（30-80 字）给读者进入本段所需最小知识",
    "why_needed": "term_first_use | term_polysemy | history_density | history_missing | cross_ref_pronoun | allusion | text_anomaly",
    "confidence": "high | medium | low",
    "source_basis": "known_history | metadata | text_evidence"
  }
]
```

### 优先级（v0.3 新增）：先解释「会导致误读」的，再解释「不知道就不懂」的

> 不是所有 prereading 价值相等。优先级：

| 优先级 | 类型 | 例 |
|---|---|---|
| **P0** 误读防御 | term_polysemy / allusion / text_anomaly | 「所谓无产者」古罗马义、「绵羊与山羊」圣经典 |
| P1 关键空白 | history_missing 单个专名、cross_ref_pronoun | 单个事件名 |
| P2 背景补充 | history_density、term_first_use | 多专名密集段 |

**P0 必标**。P1 多数标。P2 看读者负载。

### `prereading_inline.explain` 写法硬约束

- ✅ 30-80 字。多了说明你在写 essay 不是在做支架
- ✅ 必须给读者**进入本段**所需的最小知识
- ✅ allusion 必须说出典故来源（"圣经马太福音""希腊神话"）
- ✅ term_polysemy 必须给出"读者直觉义 vs 本段义"的对照
- ✅ text_anomaly 必须明示"原文疑似排版残留/typo"，避免 LLM 再去强行解释错误文本
- ❌ 不解释自明事实（"19 世纪 = 1801-1900"）
- ❌ 不重复 historical_context 已说过的
- ❌ 不要先说"这是一个重要的概念"等空话开头
- ❌ 不准与原文同 5-gram 重合

### `topic` 写法

- 5-15 字
- 用读者会查询的词（"复辟时期"而不是"1814-1830 年法国波旁王朝复辟"）

### 严格禁止

- ❌ 同一概念在同篇文献多次 inline 解释。第二次起必须用 `prereading_refs`
- ❌ 解释中含原文同 5-gram
- ❌ "众所周知""显然""我们都知道"等空话
- ❌ 用现代类比（"这就像今天的 X"）
- ❌ `prereading_inline` 长度 ≥ 4 条（说明你在 over-explain）
- ❌ 解释非真问题：解释一个本就常识的事

### 自检（输出前 LLM 必走）

- [ ] 本段确有 prereading 触发器（trigger 字段对应明确）
- [ ] **特别检查**：是否有 allusion / term_polysemy / text_anomaly / history_density？这些是 v0.2 系统漏开点
- [ ] P0 类型（term_polysemy/allusion/text_anomaly）必标了
- [ ] 已在篇章 local_glossary 的术语用 prereading_refs，未重复 inline
- [ ] inline 每条 30-80 字
- [ ] 不重复 historical_context
- [ ] 不含现代类比
- [ ] 没有评价词
