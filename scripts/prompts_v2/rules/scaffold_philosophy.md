## 读懂支架（scaffolding）总哲学

> 我们不"翻译"原文，因为原文已经是中文。
> 我们不"改写"原文，因为同义改写零信息增益。
> 我们做的是：**给读者真正缺失的支架——背景、论证关系、概念边界**——让读者**自己看懂原文**。

### 三个产物，三件事

| 字段 | 回答的问题 | 错误形态 |
|---|---|---|
| `gist` | 这段在干什么？ | "这段讲述了……"（元叙述） |
| `prereading` | 读这段前我需要知道什么？ | 重复篇章已有 background |
| `hard_sentences` | 这句到底想说什么？ | 同义改写原句 |

### 唯一目标

**降低进入论证的门槛**，不是降低文字本身的难度。

### 三条铁律

1. **不重复原文**。
   - 任何字段的文字与原句 n-gram 重合度高（5-gram 命中 ≥ 1 即视为复述）→ 视为输出失败。
   - 输出必须给原文之外的信息。

2. **不装样子**。
   - 不写"这是为了说明作者的观点"、"这一点很重要"、"作者深刻地指出"。
   - 没东西说就留空。空数组、空字段、`null` 都是合法的。

3. **不解释自明的部分**。
   - 编者注、署名、章节标题、纯叙事段：除非有指代/术语，否则只给 `gist` 不给其他支架。
   - 概念已在篇章 glossary 出现过：用 `prereading_refs` 引用，不重写。

### 按需输出（gates 驱动）

每段先回答四个 gate 问题：

```jsonc
"paragraph_gates": {
  "needs_prereading": false,
  "prereading_reason": "all_known | term_first_use | history_missing | cross_ref_pronoun | none",
  "needs_hard_sentence": false,
  "hard_sentence_reason": "long_nested | term_density | typo | rhetorical | inverted_logic | none",
  "needs_polemic": false,
  "polemic_reason": "explicit_target | implicit_target | refute_quotation | none"
}
```

**只有 needs_X = true 时才生成对应字段**。否则相应字段为空数组或 `null`。

不准为了"显得有产出"而强行触发 gate。判断 gate 时优先 `false`，疑则不做。
