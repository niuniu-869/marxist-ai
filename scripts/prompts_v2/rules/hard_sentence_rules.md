## hard_sentences 规则（v0.3，codex-fixed）

### 总原则：选「读者卡点」，不是「长句」

> 一段 80 字的长句若结构清晰、用词常见，**不是难句**。
> 一段 25 字的反讽 + 典故，**才是难句**。
>
> 你的任务是替「第一次读马列的大学生」识别——他读到哪句会卡住、查百度都查不通？

### 触发条件（gates，按优先级降序）

`needs_hard_sentence: true` 仅当本段至少有一句满足以下任一**真正卡点**条件：

| 优先级 | 条件 | 描述 | 示例 |
|---|---|---|---|
| **P0 最高** | `inverted_logic` | 双重否定 / 反问 / 隐含让步 / 反讽 | "难道我们只与 X 战斗吗？"（实指还有 Y） |
| **P0** | `allusion` | 圣经/古典/民间典故、隐喻引用 | "把绵羊跟山羊分开""土利街裁缝代表英国人民" |
| **P0** | `term_polysemy` | 同一词在本段需特定 sense（如"无产者"在古罗马语境≠现代工人） | "罗马的所谓无产者" |
| P1 | `cross_ref` | 句中"它/他们/这种"指向跨段或全篇前文 | 段首突兀代词 |
| P1 | `rhetorical_omission` | 省略让步/前提/对比项 | "虽然 X，但是……"省略让步 |
| P2 | `term_density` | 句内 ≥ 3 个 LAYER A 术语堆叠且形成新论断 | 仅术语堆不算，必须形成新意 |
| P2 | `long_nested` | 句长 ≥ 80 字**且**含 ≥ 2 层从句嵌套**且** P0/P1 不能解释 | 长但易懂的不算 |
| **P0 异常** | `text_anomaly` | 明显排版残留 / 数字乱码 / OCR 错误（如"海盗10时代"） | 强制开 hard_sentence 并标 `confidence: low`，提示读者是文本问题 |

**每个 trigger 必须给出"读者卡点"的具体证据**，不能只列 trigger 名。

### 严格规则：先判 P0，没有 P0 才下放 P1/P2

- 优先选 P0 的句（最高读者价值）
- 只有 P0/P1 全无时才考虑 P2
- 一段最多 2 条；若 P0 已 2 条，舍弃 P1/P2

### 三段式结构

```jsonc
{
  "anchor": "p12s3",
  "quote": "原句一字不改",
  "trigger": "inverted_logic | allusion | term_polysemy | cross_ref | rhetorical_omission | term_density | long_nested | text_anomaly",
  "reader_block": "（30-60 字）说出读者会卡在哪里。例：「双重否定 + 时代术语，读者直觉读成正面陈述」",
  "parse": {
    "claim": "这句的主张/陈述（30-80 字，必须是【从原句无法直接读出】的提炼，不是同义换写）",
    "qualifiers": "限定条件（30-80 字，可空。包括时间、范围、程度限定）",
    "contrast_or_target": "对比对象/反驳对象（30-80 字，可空。仅论辩句填）"
  },
  "why": {
    "relation": "continues | contrasts | example | conclusion | definition | polemic | none",
    "explanation": "本句在论证链中的角色（50-120 字。必须绑定 relation。relation=none 时本字段为空）"
  },
  "implication": "若有明确推论，30-80 字。无则 null。",
  "confidence": "high | medium | low",
  "source_basis": "text_evidence | known_context | inferred"
}
```

### `parse.claim` 写法硬约束（codex 重点）

- ✅ **必须**抽出主谓宾的核心断言，把"它/他们/这种"替换成具体所指
- ✅ **必须**把双重否定还原为肯定（"非……者乎"→"是……的"）
- ✅ **必须**把反问还原为陈述（"难道 X 吗？"→"实际上 X 不是……"）
- ❌ **不准**与原句任何 5-gram 重合（5 个连续汉字相同视为复述失败 → 整条 hard_sentence 丢弃）
- ❌ **不准**只是去掉修辞、保留主干（这是 paraphrase 不是 parse）
- ❌ **不准**写"作者认为/作者指出/这句话说"等元描述，必须给出具体内容

### `reader_block` 写法（v0.3 新增）

- 30-60 字
- 必须**具体**：不是"较难理解"这种空话
- 例 ✅："双重否定+'伏尔泰主义'这个词，读者会以为反动派只反伏尔泰，实际反更广"
- 例 ❌："这是一个长句，结构复杂"

### `parse.qualifiers` 写法

- 把句中所有"在……条件下""对于……来说""如果……"单独拎出
- 注明 qualifier 的对象（限定的是 claim 的什么）

### `parse.contrast_or_target`（与 polemic_in_paragraph 协同）

- 仅在句子是论辩 / 区别时填
- **绝不准**把作者立场写进来（"作者认为..."不行）
- 内容：被反驳/对比的**对象本身的观点**，用对方语气
- 与 `polemic_in_paragraph.their_view` 5-gram 不能完全重合（避免重复）

### `why.relation` 枚举严格

| 值 | 含义 | 必须能在 explanation 体现 |
|---|---|---|
| `continues` | 承上段 | 引用上一段结论 |
| `contrasts` | 与上文/某派观点对照 | 点出对照对象 |
| `example` | 举例支撑前文 | 指出被支撑的论点 |
| `conclusion` | 推出结论 | 引用前文前提 |
| `definition` | 给术语下定义 | 指出术语 |
| `polemic` | 反驳论敌 | 必须 polemic_in_paragraph 也激活 |
| `none` | 不属于上述任何关系 | explanation 留空 |

### 严格禁止

- ❌ `parse.claim` 与原句 5-gram 重合 → 整条 drop
- ❌ `why.explanation` 写成"这是为了说明……""作者深刻地指出……""一针见血地揭示……"
- ❌ 把不难的句子标进来（纯叙事段、署名段、章节标题、用词常见的长句）
- ❌ 同段内 ≥ 3 个 hard_sentences
- ❌ `confidence: low` 的 hard_sentence 前端不展示（除 text_anomaly 例外，需提示文本异常）
- ❌ `reader_block` 写成"较难""复杂""需要解释"等空话

### 自检（输出前 LLM 必走）

- [ ] 每条 hard_sentence 命中 P0/P1/P2 中明确触发器
- [ ] **优先选 P0**，没有 P0 才下放
- [ ] `reader_block` 具体说出卡点是什么（不是"较难"）
- [ ] `parse.claim` 与 `quote` 无 5-gram 重合
- [ ] `parse.contrast_or_target` 不与 `polemic_in_paragraph.their_view` 5-gram 重合
- [ ] `why.relation` ∈ 枚举值
- [ ] `why.relation == "polemic"` 时 `polemic_in_paragraph.is_polemical = true`
- [ ] 每段 hard_sentences ≤ 2
- [ ] `confidence` `source_basis` 都填了
- [ ] 所有字段没有评价词（"伟大""深刻"等）
