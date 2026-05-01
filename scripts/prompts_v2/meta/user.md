## 任务

为下列马列经典文献生成篇章级元数据。

**标题**：{title}
**作者**：{author}
**抓取自**：{source_url}
**已确定性解析的 provenance**（来自原文末尾溯源块）：
```
{provenance_block}
```

**全文（截取前 8000 字符，已切分段落）**：
```
{text_head}
```

---

{{include: rules/objectivity_and_stance.md}}

---

## 输出要求

### `tldr_modern`（21 世纪一句话摘要，30-80 字）

用大白话告诉读者"这篇在干什么"。**不评价**。

### `tldr_extended`（3-5 条要点）

帮没读过的读者快速立住框架，每条一句白话。

### `historical_context`（写作背景，200-400 字）

写作时间、作者处境、欧洲背景、写作动机。**仅基于** provenance + 公认史实。模糊处用"据现有材料"或留空。**不评论**。

### `polemic_targets`（论战对象，0-N 条）

```json
{
  "target_type": "person | school | doctrine | trend",
  "target_id": "feuerbach / kautsky / opportunism / utopian_socialism",
  "target_name_zh": "费尔巴哈",
  "view_being_refuted": "1-2 句对方观点",
  "author_position": "1-2 句作者立场"
}
```

### `local_glossary`（本作品本地术语表，**v0.2 新增**）

列出本作品中**反复出现且需要展开**的核心术语，给统一定义。后续段级 prereading 引用此处即可，不重复 inline。

```jsonc
{
  "term_id": "alienation_early_marx",
  "surface_zh": "异化",
  "scope": "1844 经济学哲学手稿语境",
  "definition": "60-150 字。给读者进入本作品所需的最小理解。不评价、不展开太远。",
  "first_appearance_paragraph_n": 12,
  "confidence": "high"
}
```

只列**本作品独有**或**需在本作品语境下专门理解**的术语。"商品""资本"这种通用马列术语不必每篇都列。

### `key_concepts` / `key_persons` / `key_works` / `key_events` / `key_orgs`

列出本文实际提到的概念/人物/著作/事件/组织 ID。**只列实际提到的**。

### `categories` + `primary_category`

categories 数组 ⊆ {philosophy, political_economy, scientific_socialism, history, polemic, letter, speech, program}

### `author_period` / `historical_period` / `thematic_domain`

如：
- author_period: `marx_1845_1848`
- historical_period: `pre_1848_revolutions`
- thematic_domain: `["philosophy", "praxis_theory"]`

### `provenance`

把已解析 provenance 拆字段：
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
  "raw_text": "..."
}
```
不可考字段填 `null`。

### `evidence`

事实陈述的证据来源数组：
```json
{
  "claim": "...",
  "source": "provenance_block | known_history",
  "quote": "..."
}
```

### `reading_path`（**v0.2 新增**，规则计算 + LLM 评分混合）

```json
{
  "difficulty": "easy | moderate | hard | expert",
  "best_read_after": ["alienation_concept", "1848_european_revolutions"],
  "recommended_for": ["new_reader_30min", "deep_study"]
}
```

注意：`estimated_minutes` 由后处理脚本根据字数 + difficulty 计算，**不要 LLM 估**。`essential_paragraphs` 也由后处理选段级 importance_score top-N，**不要 LLM 直接列**。

---

## 输出格式

```json
{
  "tldr_modern": "...",
  "tldr_extended": ["...", "...", "..."],
  "historical_context": "...",
  "polemic_targets": [],
  "local_glossary": [],
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
  "evidence": [],
  "reading_path": {}
}
```

## 自检

- [ ] 没有评价词
- [ ] historical_context 全部基于 provenance 或公认史实
- [ ] 不可考处用 null 或留空
- [ ] local_glossary 是本作品独有的术语，不重复全集通用术语
- [ ] 没有 estimated_minutes / essential_paragraphs（这些由后处理生成）
- [ ] 纯 JSON 输出
