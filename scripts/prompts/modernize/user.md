## 任务

为以下段落生成"说人话"标注。本段是**第 {para_n}/{total} 段**。

**文献**：{title}（{author}）
**论战对象**（如有）：{polemic_target_summary}

**前后段语境**（仅供你理解，不改写）：
```
{context}
```

**待标注段落**：

原文整段：
```
{paragraph_original}
```

已切分句子（**LLM 不得改动 sid 和 original**，只能为每个 sid 生成 plain 和 notes）：

```json
{sentences_input}
```

---

{{include: rules/speak_human_rules.md}}

---

## 输出要求

### 段落级

- `gist`：30-80 字，告诉读者本段在论证链中的位置 / 在干什么。**不评价**。
- `plain_rewrite`：整段当代汉语改写。
  - 长度：原文 80%-180%（短句、格言、标题、引文 block 不在此限）。
  - 拆长句、调语序，使其符合当代汉语阅读习惯。
  - **必保留术语**全部保留。**核心比喻**原句保留。
  - 不要在改写中插入 `[]` `（）` 注释——注释另由 sentences[].notes 承载。
- `block_type`：`author_text`（默认）/ `quote_block`（长引文区块，本段是引用他人原话）/ `aphorism`（格言）/ `title`（标题）/ `footnote`（脚注内容）。
- `length_policy`：与 block_type 联动：`normal_paragraph` / `preserve_plus_note` / `no_rewrite_or_minimal` / `summarize_allowed` / `preserve`。

### 句子级（按输入 sids 顺序，**长度必须与输入相同**）

每个 sid 输出：

```json
{
  "sid": "p3s2",
  "plain": "该句的当代汉语版（不改 sid 与 original）",
  "speaker": "author | quoted_marx | quoted_engels | quoted_lenin | quoted_opponent | editor | unknown",
  "stance": "endorsed | criticized | neutral_citation | self",
  "notes": [
    {
      "surface": "实践",
      "type": "concept | concept_archaic_translation | person | place | event | work | org | quote | metaphor | polemic_ref | translator_note | footnote_ref",
      "target": "目标 ID（小写下划线，无则 null）",
      "modern": "现代等价/解释（必填，10-60 字）",
      "highlight": "term | archaic | metaphor | polemic | quote | null"
    }
  ]
}
```

#### `notes[].type` 选用规则

- 核心哲学/经济/政治概念 → `concept`，highlight=`term`
- 老译晦涩词（鄙陋、庸碌、乡愿、藉以、寻常 等）→ `concept_archaic_translation`，highlight=`archaic`
- 历史人物（杜林、考茨基、伯恩施坦、施蒂纳 等）→ `person`
- 历史事件（巴黎公社、二月革命、1848 革命）→ `event`
- 著作（《基督教的本质》《资本论》《哲学的贫困》）→ `work`
- 组织（第一国际、社会民主党）→ `org`
- 地名 → `place`
- 引用他人原话 → `quote`
- 核心比喻（鸦片、幽灵、枷锁、国家机器 等）→ `metaphor`，highlight=`metaphor`
- 隐指的论敌或被批驳观点 → `polemic_ref`
- 译者注 / 编者注引用 → `translator_note` / `footnote_ref`

每条 note 的 `modern` 字段必须是**现代等价说明**，不要只复述词形。

#### `speaker` / `stance`（关键，防止 M1/M3 翻车）

- 作者本人陈述 → `speaker: author`，`stance: self`
- 作者引用马克思/恩格斯/列宁的原话 → `speaker: quoted_marx | quoted_engels | quoted_lenin`，`stance: endorsed`
- 作者引用论敌原话以批驳 → `speaker: quoted_opponent`，`stance: criticized`
- 中性引用历史文献 → `speaker: editor | unknown`，`stance: neutral_citation`

---

## 输出格式（**严格 JSON**）

```json
{
  "gist": "...",
  "plain_rewrite": "...",
  "block_type": "author_text",
  "length_policy": "normal_paragraph",
  "sentences": [
    {
      "sid": "p3s1",
      "plain": "...",
      "speaker": "author",
      "stance": "self",
      "notes": []
    }
  ]
}
```

## 自检

- [ ] sentences[] 长度与输入 sids 完全一致
- [ ] 每个 sid 都对应输入中的 sid（不创造新 sid，不丢 sid）
- [ ] **必保留术语清单**全部保留
- [ ] 没有命中**禁止替换映射**
- [ ] 核心比喻原句保留
- [ ] 没有现代政治类比（M2）
- [ ] 没有评价词（M7）
- [ ] notes[].modern 字段非空且具体
- [ ] 纯 JSON 输出，无 markdown 标记
