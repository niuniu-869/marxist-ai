## 任务

为下列段落生成"读懂支架"标注。本段是第 {para_n}/{total} 段。

**文献**：{title}（{author}，{written_at}）
**篇章 historical_context**（已生成，不要重复）：
```
{historical_context}
```

**篇章 polemic_targets**（已生成）：{polemic_targets_brief}

**篇章 local_glossary**（已定义术语，本段引用即可，不要 inline 重复）：
{local_glossary_brief}

**前一段简述**（仅供你判断 argument_role）：
{prev_para_gist}

**本段原文**：
```
{paragraph_original}
```

**已确定性切句的句子（你不得改 sid 与 original，只能给每个 sid 生成 plain 与 notes）**：

```json
{sentences_input}
```

---

{{include: rules/scaffold_philosophy.md}}

---

{{include: rules/objectivity_and_stance.md}}

---

{{include: rules/notes_rules.md}}

---

{{include: rules/hard_sentence_rules.md}}

---

{{include: rules/prereading_rules.md}}

---

{{include: rules/polemic_rules.md}}

---

## 输出格式（**严格 JSON**）

```jsonc
{
  "block_type": "author_text | quote_block | aphorism | program_clause | narrative | footnote | title | signature",

  "gist": "30-60 字客观点出本段在干什么。不评价、不抒情。叙事段照实陈述，论辩段点出反驳谁。",

  "importance_score": 0,
  "importance_reason": "（30-60 字）本段在全文中的角色：core_thesis | core_critique | example | transition | digression | meta",
  "// importance_score": "0=可跳过 1=辅助 2=支撑 3=核心",

  "argument_role": "continues | contrasts | example | conclusion | definition | transition | none",
  "argument_link": "（仅 argument_role != none 时，30-80 字）本段与上段的论证关系。",

  "paragraph_gates": {
    "needs_prereading": false,
    "prereading_reason": "all_known | term_first_use | history_missing | cross_ref_pronoun | none",
    "needs_hard_sentence": false,
    "hard_sentence_reason": "long_nested | term_density | inverted_logic | rhetorical | cross_ref | none",
    "needs_polemic": false,
    "polemic_reason": "explicit_target | implicit_target | refute_quotation | none"
  },

  "prereading_refs": [],
  "prereading_inline": [],

  "hard_sentences": [],

  "polemic_in_paragraph": {
    "is_polemical": false,
    "target": null,
    "their_view": null,
    "author_response": null,
    "polemic_kind": null,
    "confidence": null
  },

  "sentences": [
    {
      "sid": "p3s1",
      "speaker": "author | quoted_marx | quoted_engels | quoted_lenin | quoted_opponent | editor | unknown",
      "stance": "self | endorsed | criticized | neutral_citation",
      "notes": []
    }
  ]
}
```

## 输出前自检（v0.3 强化必走）

### A · 结构对齐
- [ ] sentences[] 长度与输入 sids 完全一致，sid 全对应
- [ ] paragraph_gates 全部判断完毕；needs_X = false 时对应字段为空数组/null
- [ ] importance_score ∈ {0,1,2,3}，importance_reason 给出

### B · 内容客观（M-block）
- [ ] **所有字段**（gist / argument_link / explain / parse.* / their_view / author_response / modern）都没有评价词
- [ ] 没有命中"必保留术语清单 + 禁止替换映射"的违规
- [ ] 没有现代政治类比
- [ ] 引用论敌的句子 speaker = quoted_opponent，绝不写成 author

### C · 反 AI slop（v0.3 重点）
- [ ] **没有任何字段与原句 5-gram 重合**：gist / parse.claim / explain / their_view / author_response / modern
- [ ] `parse.claim` 不是原句去掉修辞后的 paraphrase
- [ ] `polemic.their_view` 是论敌口吻，不含"被批判""错误地"等定性词
- [ ] `polemic.author_response` 是作者立场，不重复 their_view
- [ ] `their_view` 与 `author_response` 5-gram 无重合
- [ ] `prereading.explain` 不重复 historical_context

### D · 支架精准
- [ ] `hard_sentences` 优先选 P0（inverted_logic / allusion / term_polysemy / text_anomaly）
- [ ] 每条 hard_sentence 的 `reader_block` 具体说出卡点（不是"较难""复杂"）
- [ ] hard_sentences ≤ 2
- [ ] `prereading_inline` ≤ 3 条，glossary 已有的用 refs

### E · notes 硬规则（N1-N8）
- [ ] surface 长度 ≤ N1 上限（必保留术语豁免清单除外）
- [ ] modern 不以"指/即/就是/是指"开头
- [ ] concept 都有 sense_id 且属白名单或满足 LAYER B
- [ ] 没有动宾/因果/整句/描述性长定语被标为 concept
- [ ] 社会群体用 social_group 不是 person
- [ ] 每句 notes ≤ 3，每段 notes ≤ 8
- [ ] 每个 note 有 confidence 与 source_basis

### F · 输出格式
- [ ] 纯 JSON 输出，无 markdown 标记
