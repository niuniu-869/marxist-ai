## polemic_in_paragraph 规则（v0.3，codex-fixed）

### 核心硬约束（v0.2 翻车点 → v0.3 修复）

> v0.2 全量出现 477 例 `their_view` 与 `author_response` 5-gram 重合 / 同质化。
> 根因：LLM 把"被作者批判的观点"写成"作者对该观点的批判"，于是两边都是作者立场。

**`their_view` 必须是论敌的话**，**`author_response` 必须是作者的话**。两者立场必须可分离。

### 触发条件

`needs_polemic: true` 仅当：

| 条件 | 描述 |
|---|---|
| `explicit_target` | 段中**显式提到**论战对象（人名、流派、刊物） |
| `implicit_target` | 段中**隐含**论敌（用"反对派""他们""有些人""所谓的 X 派"） |
| `refute_quotation` | 段中引用论敌话语并反驳（含"他们说""他们认为"） |

**疑则 false**。普通陈述段、纯叙事段、无对手段不开 polemic。

### 输出结构

```jsonc
"polemic_in_paragraph": {
  "is_polemical": true,
  "target": "论敌名（人名/流派/教条），如：考茨基 / 修正主义 / 第二国际中派",
  "their_view": "（30-80 字）他们说什么。必须是论敌口吻或转述其观点本身。",
  "author_response": "（30-80 字）作者怎么回应。必须是作者立场。",
  "polemic_kind": "exposes_contradiction | refutes_premise | reveals_class_basis | counter_quotation | strategic_critique",
  "confidence": "high | medium | low"
}
```

### `their_view` 写法硬约束

- ✅ 用论敌的语气、概念、术语（哪怕是错的）
  - 例：「考茨基认为，民族战争年代马克思的态度证明社会党可保卫祖国」
  - 例：「他们说，本国胜利能加速资本主义发展，从而更快迎来社会主义」
- ❌ **绝不准**写"被作者视为""被列宁批判为""作者认为这是""这种错误的观点"等定性词
- ❌ **绝不准**用作者立场转述（"他们 *错误地* 认为..."）
- ❌ **绝不准**与 `author_response` 5-gram 重合
- ❌ **绝不准**与 `parse.contrast_or_target` 5-gram 完全重合（避免重复）

#### 反例（v0.2 翻车）

```
❌ their_view: "社会沙文主义者认为本国胜利能加速资本主义发展，考茨基则反对这种粗糙的辩护。"
   ↑ 这一句把"论敌观点"和"另一论敌的反对"混在一起，整体仍是作者视角的描述
```

```
✅ 拆分为：
   their_view (社会沙文主义者): "本国胜利能加速资本主义发展，从而更快迎来社会主义。"
   author_response: "列宁指出这是为本国资产阶级服务的'司徒卢威主义'变种。"

   或如果论敌有多个，target 写主要一个，their_view 用主要一个的话，author_response 一并回应
```

### `author_response` 写法硬约束

- ✅ 用作者的判定、术语、立场
  - 例：「列宁指出这是托词，本质上是放弃国际主义」
  - 例：「恩格斯反讽他们斗争对象远超政治自由主义」
- ✅ 可含作者使用的范畴词（无产阶级、专政、辩证法等必保留术语）
- ❌ 不准只复述 their_view（"他们这样错了"是无信息）
- ❌ 不准用评价词（"深刻""英明"等）
- ❌ 不准与 `their_view` 5-gram 重合

### `polemic_kind` 枚举

| 值 | 含义 |
|---|---|
| `exposes_contradiction` | 揭露论敌内部自相矛盾 |
| `refutes_premise` | 反驳论敌前提 |
| `reveals_class_basis` | 揭示论敌的阶级基础 |
| `counter_quotation` | 引论敌自己的话反驳 |
| `strategic_critique` | 战略路线批判 |

### `target` 写法

- ✅ 具体名（"考茨基""伯恩施坦""孟什维克"）
- ✅ 具体流派（"机会主义""社会沙文主义"——使用必保留术语原词）
- ❌ "反动派""敌人""他们"——除非段内确实没显名（此时 confidence: low）
- ❌ 含糊的"某些人""一些理论家"

### 严格禁止

- ❌ 把作者本段陈述硬塞成 polemic（明明只是叙事或定义）
- ❌ `their_view` 5-gram 与 `author_response` 重合
- ❌ `their_view` 含评价词（论敌不会评价自己"反动")
- ❌ 多论敌混进一个 their_view 里（导致立场模糊）

### 自检（输出前 LLM 必走）

- [ ] `is_polemical=true` 时 4 字段全填
- [ ] `their_view` 是论敌口吻
- [ ] `author_response` 是作者立场
- [ ] 二者 5-gram 无重合
- [ ] `target` 显名（除非 confidence: low）
- [ ] `polemic_kind` ∈ 枚举值
- [ ] 不含评价词
