## 句级 notes 严格规则（v0.3，codex-fixed）

### 总原则

> 标得少而准，胜过标得多而滥。
> 一个段落 0 条 notes 是合法的。
> v0.2 翻车：14% surface 超长 / 16% modern 循环复述 / 错误 type。v0.3 必须根除。

### N1 · surface 长度硬上限

| type | surface 最长字数 |
|---|---|
| `concept` | 5 字 |
| `metaphor` | 8 字 |
| `archaic` | 4 字 |
| `person` | 12 字（单一专名，含字号） |
| `place` | 10 字 |
| `org` | 16 字（单一组织全称） |
| `work` | 16 字（单一书名） |
| `event` | 12 字 |
| `quote` | 不通过 surface 标，用 sentences[].speaker |
| `slogan` | 12 字（口号整句） |
| `program_clause` | 24 字（纲领单条） |
| `social_group` | 12 字（**v0.3 新增**：社会群体如"无业游民""山区牧羊人"——v0.2 把"皮费拉利""拉察罗尼"误标 person） |

**违反即视为非法注释，直接丢弃**（后处理 04_validate.py 强制执行）。

### N1 · 必保留术语豁免（**v0.3 新增**）

下列**复合术语**可超出 5 字 concept 上限（核心范畴优先于长度规则）：

```
无产阶级专政     无产阶级革命     资产阶级专政     资产阶级革命
无产阶级民主     资产阶级民主     社会沙文主义     社会民主主义
经济基础         上层建筑         生产资料         生产关系
生产力           商品拜物教       交换价值         使用价值
剩余价值         剩余劳动         雇佣劳动         异化劳动
辩证唯物主义     历史唯物主义     科学社会主义     空想社会主义
唯物辩证法       形而上学
机会主义         修正主义         教条主义         经验主义
工联主义         无政府主义       考茨基主义       托洛茨基主义
帝国主义         超帝国主义       垄断资本主义     金融资本
小资产阶级       大资产阶级
```

豁免清单内的 surface 必须**完全匹配**才豁免；变体（如"无产阶级革命家"）仍按 5 字限。

### N2 · `modern` 字段禁循环复述

- ❌ **绝不准**以以下开头：`指 <surface>` / `即 <surface>` / `就是 <surface>` / `<surface> 是` / `<surface> 指`
- ❌ **绝不准** modern 与 surface 完全相等
- ❌ **绝不准** modern 与原句 5-gram 重合
- ✅ **必须**包含原文之外的**情境/出处/作用**信息
- ✅ 可以以"在……语境下""出自……""作者用此词……"开头

#### v0.2 翻车反例

```
❌ surface: "工人阶级的儿女", modern: "指代党员的阶级出身"
   ↑ "指代"开头 + 信息为零 → 删除

❌ surface: "中共和国民党", modern: "指当时合作进行国民革命的两个政党，即中国共产党和中国国民党。"
   ↑ "指"开头 → 删除（虽然有信息但格式违规，让 LLM 重写）

✅ surface: "中共和国民党", modern: "1924-1927 年第一次国共合作中两党并称，国民党借共产党扩大群众基础。"
   ↑ 给情境 + 历史出处
```

### N3 · `concept` 三层准入

```
LAYER A · 白名单（直接通过，必带 sense_id）
  哲学：异化 实践 客体 主体 类（费尔巴哈用语）感性 直观 能动 对象性 范畴
        辩证法 辩证 唯物 唯心 形而上学 否定 矛盾
  政经：商品 价值 使用价值 交换价值 剩余价值 拜物教 商品拜物教
        劳动力 雇佣劳动 工资 资本 资本积累 剥削 剩余劳动
        生产资料 生产关系 生产力 上层建筑 经济基础
  科社：阶级 阶级斗争 无产阶级 资产阶级 小资产阶级
        专政 无产阶级专政 国家 国家机器 民主 革命 暴力革命
        私有制 公有制 共产主义 社会主义 共产党 工人阶级
  论敌：机会主义 修正主义 教条主义 经验主义 工联主义 沙文主义
        无政府主义 改良主义 社会沙文主义 经济主义

LAYER B · 候选区（必须满足 *全部* 条件才放行）
  - 在本段 *承担论证功能*（不是描述性出现）
  - 在本作品中 *至少出现 3 次* 或在马列文献语料中是稳定术语
  - 不是动宾短语、因果短语、整句

LAYER C · 黑名单形态（**永远不准** 标 concept）
  - **含动词的短语**：「实施了……的政策」「进行……的斗争」「丧失了……的统治」「排除了……」「放弃了……」
  - **含因果的短语**：「由于……的危险」「为了……的目的」
  - **整句、整段**（任何含完整主谓的）
  - **描述性长定语**：「非法的延长工作时间」「对工人不利的条件」
  - **数字、日期**（用 type=event 而非 concept）
  - **国名、地名**（用 type=place）
  - **报刊名、书名**（用 type=work）
  - **政党、组织、苏维埃、国际**（用 type=org）
  - **社会群体**（用 type=social_group，不是 person）
  - **段内评价压缩**：把"资产阶级如何如何"段意压缩成一个 concept（v0.2 翻车点）
  - **泛指词**：「上层」「方面」「社会」「群体」「时期」单独标 concept 一律禁止

### N4 · `concept` 必须带 `sense_id`

每个 concept note 必须显式标 sense_id，区分同一词的不同含义：

```
"价值" → sense_id: "value_political_economy"   （政治经济学语境）
"价值" → sense_id: "value_general"             （普通用法，不应标 concept）
"国家" → sense_id: "state_marxist_theory"      （阶级压迫工具，需展开）
"国家" → sense_id: "state_geographic"          （地理上的国家，不标 concept）
"民主" → sense_id: "democracy_proletarian"     （无产阶级民主）
"民主" → sense_id: "democracy_bourgeois"       （资产阶级民主）
"阶级" → sense_id: "class_marxist"             （马克思主义阶级范畴）
"劳动" → sense_id: "labor_economic"            （政治经济学概念）
"劳动" → sense_id: "labor_general"             （普通含义，不标）
"实践" → sense_id: "praxis_marxist"
"异化" → sense_id: "alienation_early_marx"
"无产者" → sense_id: "proletarian_modern"      （现代工业无产阶级）
"无产者" → sense_id: "proletarian_roman"       （古罗马无产者，反义需 prereading）
```

**没有合理 sense_id 的词不应标 concept**。

### N5 · 密度上限

- 单句 notes ≤ 3
- 单段 notes ≤ 8
- 同 surface 在本段只标第一次出现
- 已在篇章 `key_concepts` 列出的术语，每篇只在第一次出现处标
- 优先级（多 note 候选时按此选）：
  ```
  metaphor > polemic_ref > person > work > event > org > place > social_group > concept(layer A) > slogan > program_clause > archaic
  ```

### N6 · `confidence` 与 `source_basis`

每个 note 必须带：

```jsonc
{
  "surface": "...",
  "type": "...",
  "modern": "...",
  "highlight": "term | metaphor | archaic | polemic | quote | null",
  "confidence": "high | medium | low",
  "source_basis": "whitelist | text_evidence | metadata | known_history | inferred",
  "sense_id": "（仅 concept 必填）"
}
```

`confidence: low` 的 note **前端不展示**（避免低质污染）。

### N7 · 禁止「装样子标」（v0.3 强化）

避免标毫无解释价值的常用词：

- ❌ "上层" "下层" "方面" "时期" "社会" "群体" 单独标
- ❌ "资产阶级"标 concept 时只解释"指资产阶级"——已在白名单，多数情况不必再 inline
- ❌ 把作者评价压缩成一个 concept（如把整段对资产阶级的描述压成一个"资产阶级"note）

### N8 · 自检（输出前 LLM 必走一遍）

- [ ] 每个 surface 长度 ≤ N1 上限（豁免清单除外）
- [ ] 没有 modern 以"指/即/就是/是指"开头
- [ ] modern 与原句 5-gram 无重合
- [ ] concept 都有 sense_id 且属白名单或满足 LAYER B
- [ ] 每句 notes ≤ 3，每段 notes ≤ 8
- [ ] 没有动宾/因果/整句/描述性长定语被标为 concept
- [ ] 社会群体用 social_group 不是 person
- [ ] 每个 note 有 confidence 与 source_basis
- [ ] 同 surface 段内只标第一次

不通过 → 删除该 note 重新输出。
