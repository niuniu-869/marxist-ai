## 任务

为下列马列经典文献生成篇章级元数据。

**标题**：{title}
**作者**：{author}
**抓取自**：{source_url}
**已确定性解析的 provenance**（来自原文末尾溯源块，不要凭空补充）：
```
{provenance_block}
```

**全文（截取前 8000 字符，已切分段落，仅供 meta 任务理解上下文）**：
```
{text_head}
```

---

## 输出要求

### `tldr_modern`（21 世纪一句话摘要，30-80 字）

用大白话告诉读者"这篇在干什么"。**不评价**。

### `tldr_extended`（3-5 条要点，每条一句白话）

帮完全没读过的读者快速立住框架。**不评价**。

### `historical_context`（写作背景，200-400 字）

交代：写作时间、作者处境、写作动机、欧洲背景。**仅基于** provenance 块或公认史实。模糊处用"据现有材料"或留空。**不评论**。

### `polemic_targets`（论战对象，0-N 条）

若文献是论战性质，列出反对谁、反对什么观点。每条：
```json
{
  "target_type": "person | school | doctrine | trend",
  "target_id": "如 feuerbach / kautsky / opportunism / utopian_socialism",
  "target_name_zh": "如 费尔巴哈",
  "view_being_refuted": "对方的观点，1-2 句",
  "author_position": "作者立场，1-2 句"
}
```

无论战内容则输出 `[]`。

### `key_concepts`（涉及核心概念 ID 列表）

从下列概念词典中挑选本文涉及的核心概念。如果遇到词典外的核心概念，可以创造新 ID（小写英文+下划线）。

**已知概念 ID（部分）**：
```
alienation praxis materialism_dialectical materialism_historical idealism
class_struggle proletariat bourgeoisie petty_bourgeoisie
proletarian_dictatorship state_machine revolution violent_revolution
private_property capital surplus_value commodity use_value exchange_value
commodity_fetishism wage_labor labor_power
opportunism revisionism economism utopian_socialism scientific_socialism
productive_forces relations_of_production base_superstructure
imperialism national_liberation party_of_new_type
```

### `key_persons` / `key_works` / `key_events` / `key_orgs`

列出本文提到的人物 / 著作 / 事件 / 组织 ID（拼音或英文，小写下划线）。**只列本文实际提到的**，不补全。

### `categories` + `primary_category`

`categories: ["philosophy" | "political_economy" | "scientific_socialism" | "history" | "polemic" | "letter" | "speech" | "program"]`，可多选。`primary_category` 单选。

### `author_period` / `historical_period`

`author_period`: 作者活跃期分段，如 `marx_1845_1848`、`lenin_1917`、`engels_late`。
`historical_period`: 历史背景，如 `pre_1848_revolutions`、`paris_commune`、`pre_ww1_socialdemocracy`、`russian_revolution_1917`。

### `thematic_domain`

主题域数组，如 `["philosophy", "praxis_theory"]`。

### `provenance`（结构化 provenance 块）

把已解析的 provenance 拆字段：
```json
{
  "written_by": ["marx" | "engels" | ...],
  "written_at": "1845-spring",
  "written_in": "布鲁塞尔",
  "first_published_at": "1888",
  "first_published_in_publication": "...",
  "first_published_by": "engels",
  "original_language": "de | ru | en | fr",
  "source_collection": "马克思恩格斯全集",
  "source_volume": 3,
  "source_pages": "3-6",
  "translation_publisher": "中央编译局",
  "raw_text": "原始 provenance 字符串"
}
```
不可考字段填 `null`。

### `evidence`

列出 meta 中事实陈述的证据来源。每条：
```json
{
  "claim": "马克思于1845年春在布鲁塞尔写作本提纲",
  "source": "provenance_block | known_history",
  "quote": "卡·马克思写于1845年春..."
}
```

---

## 输出格式

```json
{
  "tldr_modern": "...",
  "tldr_extended": ["...", "...", "..."],
  "historical_context": "...",
  "polemic_targets": [],
  "key_concepts": [],
  "key_persons": [],
  "key_works": [],
  "key_events": [],
  "key_orgs": [],
  "categories": [],
  "primary_category": "...",
  "author_period": "...",
  "historical_period": "...",
  "thematic_domain": [],
  "provenance": {},
  "evidence": []
}
```

## 自检

- [ ] 没有评价词（"伟大""光辉""科学地证明"）
- [ ] historical_context 全部基于 provenance 或公认史实
- [ ] 不可考处用 null 或留空，未编造
- [ ] 纯 JSON 输出
