# v0.1 复盘 + plan B（draft for codex）

> 起草：2026-04-30 下午
> 上下文：v0.1 已完成全量（326 篇 final，~21k 段标注）。用户人工 review 后判定"白话不如原文好理解，词语标注也很幽默，方向错了"。

---

## 1. 诊断（基于真实抽样的硬证据）

### 1.1 `plain_rewrite` 整段白话改写：基本是同义换词，零信息增益

抽 5 篇 10 段 hard 对比（包含宣言一章、费尔巴哈提纲 1888、哥达纲领批判、列宁 1917、恩格斯 1880）：

| 原文 | plain_rewrite | 评价 |
|---|---|---|
| "由于推广机器和分工" | "随着机器的普及和分工的细化" | 同义换词 |
| "劳动越使人感到厌恶" | "劳动越让人觉得枯燥" | **削弱原文**（"厌恶"≠"枯燥"，违反 M1） |
| "这里刊印的手稿" | "现在刊印的这份手稿" | 完全无意义 |
| "工人变成了机器的单纯的附属品" | "工人变成了机器的附属品" | 删了"单纯"，损失精度 |
| "这是个天大的骗局" | "这完全是一个巨大的骗局" | 失去原文节奏 |
| "对对象、现实、感性，只是从客体的或者直观的形式去理解" | "只是把对象、现实和感性当作外在于人的客体，或者仅仅通过直观去理解" | "客体"还是"客体"，**真正难懂的仍然难懂** |

哥达纲领批判第 9 段：原文 174 字 / 改写 174 字，**等长无差异**。

**根因**：
1. prompt 里 `length_policy: 80%-180%` 是陷阱——这个区间最安全的策略就是同义改写，LLM 选了它。
2. "翻译腔→当代汉语"这个 framing 错了一半——中央编译局译本本来就不算特别欧化，原文已是流畅中文。
3. **真正难懂的不是语言，是别的**：概念抽象、历史背景缺失、论战脉络不明、推理链跨段。这些 plain_rewrite 解决不了。

### 1.2 句级 notes 翻车统计（80 篇随机抽样的硬数据）

| 翻车模式 | 例数 | 严重度 | 抽样 |
|---|---|---|---|
| **把短语/整句当 concept 标** | **2373** | ⚠️⚠️⚠️ | "由于无知而无法预防的危险" / "非法的延长工作时间" / "告工人、士兵和农民书" 都被标为 `concept` |
| **循环定义**（"X 指 X..."） | 114 | ⚠️⚠️ | `"全俄"` → "指全俄罗斯..." / `"1905年"` → "指1905年俄国革命..." |
| **解释比 surface 还短** | 128 | ⚠️⚠️⚠️ | surface 是整句引文，解释一句话；surface 是"在那里"解释成"指德国" |
| **现代年代错位词** | 20 | ⚠️ | "平台"用在"宣传革命思想的平台"——19 世纪没这词义 |
| **单句 8+ notes 过密** | 5 | ⚠️ | 一句 100 字塞 8 个高亮，眼花缭乱 |

**根因**：
1. `surface` 长度无硬约束，LLM 想标多长标多长 → 把整句当 concept 是常态。
2. `concept` type 边界不清，LLM 把"非法的延长工作时间"也标 concept（应该不标，或标 `event`/`practice`）。
3. `modern` 字段允许"指 X..."循环复述。
4. "为了让读者看懂"这个目标导致 LLM 标注密度过高（"反正多标点没坏处"），结果适得其反。

### 1.3 字段总结

| 字段 | 现状 | 评价 | 处置 |
|---|---|---|---|
| `tldr_modern` | 可用 | 真有价值 | ✅ 保留并提质 |
| `tldr_extended` | 可用 | 真有价值 | ✅ 保留 |
| `historical_context` | 可用 | 真有价值 | ✅ 保留 |
| `polemic_targets` | 可用 | 真有价值 | ✅ 保留 |
| `key_concepts/persons/...` | 命中率高 | 有价值 | ✅ 保留 |
| `gist`（段意） | 可用，部分啰嗦 | 真有价值 | ✅ 保留 + 收紧 |
| `notes`（inline 概念注释） | **2373 个翻车** | 有 1/3 价值 | 🔄 **彻底重做** |
| **`plain_rewrite`（整段改写）** | 同义换词为主 | **基本无价值** | ❌ **删除** |

---

## 2. 真正的痛点是什么

不是"语言现代化"，是这四件事：

| 痛点 | 例子 | 现 v0.1 解决了吗 |
|---|---|---|
| **概念抽象** | "对象性的活动""商品拜物教""使用价值" | ❌ plain_rewrite 还是用这些词 |
| **历史背景缺失** | 读者不知道 1844 普鲁士状况、1848 欧洲革命、1917 俄国双重政权 | 部分（在篇章 historical_context，但段级不知） |
| **论战对象隐没** | "他们说……"的"他们"是谁？这段反驳谁？ | 部分（篇章 polemic_targets 列了，段级未点出） |
| **推理链跨段** | 上段说 A，本段说 B，为什么从 A 到 B？ | ❌ |

---

## 3. Plan B 总体方向

> **从「语言现代化（rewrite）」转向「读懂支架（scaffolding）」**。
> 不再"换说法"，而是给读者真正缺失的预备知识 + 难句展开 + 推理链。

### 3.1 核心切换

```
v0.1：原文 + 同义改写 + inline 注释
v0.2：原文 + 段意 + 段前预备 + 难句解读 + inline 注释（精简）+ 论敌点名
```

**plain_rewrite 字段彻底删除**。

### 3.2 段落级新字段

```jsonc
{
  "n": 12,
  "block_type": "author_text | quote_block | aphorism | program_clause | narrative | footnote",
  "original_plain": "...",
  "gist": "30-60 字客观点出本段在干什么（不评价）",

  "prereading": [
    "（1-3 条，每条 30-80 字）读这段前你需要知道的一件事。可以是术语预习、历史背景、上一段铺垫。",
    "示例：'类'在费尔巴哈那里是个专门术语，指把所有人抽象起来的'共同本质'，不是生物学'物种'。",
    "若读者已具备本段所需全部前置知识，则输出空数组。"
  ],

  "hard_sentences": [
    {
      "anchor": "p12s3",                       // 指向句子 sid
      "quote": "原句一字不改",
      "what": "这句到底说什么（80-150 字，不是同义改写，而是抓住主谓宾 + 限定关系）",
      "why": "为什么这么说（80-150 字，连接到本段或上下文论证）",
      "implication": "推出什么（30-80 字，可空）"
    }
  ],
  // hard_sentences 仅在段内有真正难懂的句子（嵌套从句、术语堆叠、典故密集）才生成。
  // 一段 0-2 条，宁缺毋滥。

  "polemic_in_paragraph": {
    "is_polemical": false,
    "target": "对方是谁（如 杜林 / 考茨基 / 资产阶级经济学家）",
    "their_view": "对方观点 1 句",
    "author_response": "作者反驳 1 句"
  },
  // 只在本段是论辩时填，否则 is_polemical: false 其余 null。

  "argument_link": "（可空，30-100 字）本段与上段的论证关系。'承上：上段说 X；本段：X 推出 Y'。",

  "sentences": [
    {
      "sid": "p12s1",
      "original": "...",
      "speaker": "author | quoted_marx | ...",
      "stance": "self | endorsed | criticized | neutral_citation",
      "notes": [ /* 见 3.3 */ ]
    }
  ]
}
```

### 3.3 句级 notes 彻底重做

**v0.1 的根本病是没硬边界**。v0.2 加 4 条死规则：

```
RULE-N1 (surface 长度)
  - 实词 / 概念：≤ 5 字
  - 人名 / 地名 / 组织 / 著作：可至 12 字（但单一专名）
  - 比喻：≤ 8 字
  - 典故：≤ 12 字
  - 长引文不作 surface（用 sentences[].speaker 处理）

RULE-N2 (modern 不可循环)
  禁止以"指 <surface>"、"即 <surface>"、"<surface> 是"开头。
  禁止 modern == surface。

RULE-N3 (concept 边界严格)
  concept 仅限"哲学/政治经济学/科学社会主义专门术语"，必须满足：
  - 是马列文献中反复使用的稳定术语（异化、剩余价值、商品、阶级、专政、国家机器、生产关系、上层建筑、辩证法 等）
  - 或是论敌的核心主张（机会主义、议会主义、修正主义 等）
  禁止把动宾短语/事件描述/状态描述当 concept。
  例：
    ❌ "非法的延长工作时间" / "由于无知而无法预防的危险" / "工兵农代表苏维埃"（应 type=org）
    ✅ "异化" / "剩余价值" / "无产阶级专政" / "拜物教"

RULE-N4 (密度上限)
  每句 notes ≤ 4 条。同段同 surface 只标第一次。
  注释优先级：metaphor > polemic_ref > person/event/work/org > concept > archaic
```

**新增 type**：
- `program_clause`（纲领条文，如哥达纲领的"劳动是一切财富……的源泉"）
- `slogan`（口号短语，如"全世界无产者，联合起来"）

**移除滥用 type**：`concept_archaic_translation`（v0.1 滥用了，"刊印""庸碌"这种用 R6 古今异义思路简化）。

### 3.4 篇章级字段微调

`polemic_targets`、`historical_context` 保留，但加：

```jsonc
"reading_path": {
  "estimated_minutes": 15,
  "difficulty": "easy | moderate | hard | expert",
  "best_read_after": ["alienation_concept", "1848_european_revolutions"],
  // 引用 glossary ID
  "skippable_paragraphs": [3, 5, 47],
  // 题外话/编者注/重复内容可跳
  "essential_paragraphs": [12, 30, 55]
  // 抓本文核心只读这几段
}
```

`reading_path` 是**真正"对老奶奶友好"的字段**：告诉她 15 分钟读完哪几段就能抓核心。

---

## 4. 管线变化

```
01_harvest        ← 不变（已抓 345 篇）
01b_split         ← 不变
01d_segment       ← 不变（已生成 sid + char_start/end）
02a_meta          ← 改：+reading_path（仅篇章级一次 LLM）
02_annotate       ← 大改：删 plain_rewrite；加 prereading / hard_sentences / polemic_in_paragraph / argument_link；缩 notes
                     输入仍是已切句的段落（继承 v0.1 sid）
03_merge          ← 不变（schema 自适应）
04_validate.py    ← 新增：硬规则机检（surface 长度 / 循环定义 / concept 边界 / 现代政治词 / 必保留术语 / notes 密度）
                     不通过的段记入 needs_rework.json，下一轮重跑
```

可复用 v0.1：
- 全部 raw HTML
- 全部 split / segment（句级 sid 不变）
- meta 大部分（仅补 reading_path）
- ✅ **复用**：作为 prompt 的"前段语境"和"上下文"上下文输入

不可复用 v0.1：
- 全部 02_annotate 输出（**plain_rewrite 删除 + notes 重做**）

### 4.1 新 prompt 文件清单

```
prompts_marxists/
  meta/system.md              微调（加 reading_path）
  meta/user.md                微调
  annotate/system.md          重写
  annotate/user.md            重写（删 plain_rewrite，加 4 个新字段）
  rules/notes_rules.md        重写（RULE-N1~N4 + concept 白名单）
  rules/hard_sentence_rules.md 新增（什么样的句子才挑出来；what/why/implication 三段式标准）
  rules/prereading_rules.md   新增（什么时候要预备；预备什么）
  rules/concept_whitelist.md  新增（合法 concept 词典 + 论敌主张词典）
  rules/forbidden_substitutions.md  保留（M1 必保留术语 + 禁止替换映射，从 v0.1 抽出）
  rules/objectivity_rules.md  保留（M7 评价词禁用）
```

### 4.2 04_validate 硬规则机检

```python
# 每段必检：
- 不存在 plain_rewrite 字段
- gist 字数 30-80
- prereading 数组每条 30-80 字
- hard_sentences[].what / why 字数 80-150
- 句级 notes ≤ 4
- surface 长度 ≤ 5（concept）/ 12（专名/典故）
- modern 不以"指 X""即 X" 开头
- modern 不含 [互联网/数字化/平台/算法/...] 现代词
- 必保留术语命中率 100%
- 禁止替换映射不命中

不通过 → needs_rework: 段级标记，重跑该段。
```

---

## 5. 重做范围与时间

### 5.1 选项 A：全量重做（用户原指令）

- 段级 LLM 调用 ~25000 次（v0.1 实际 20792 + 196 失败）
- 但 **prompt 平均长度增加 ~1.5x**（多 4 个新字段）
- 单段耗时按 v0.1 平均 30-40s 估
- 8h 跑量按 v0.1 实绩，应能跑完 80-90%

### 5.2 选项 B：核心 50 篇高质量重做 + 320 篇低风险重做

- 核心 50 篇（费尔巴哈/宣言/资本论第一卷第一章/反杜林论/国家与革命/帝国主义/列宁主义基础）：**完整 prompt v0.2**
- 其余：**简化 prompt**（只跑 gist + notes 重做，不做 prereading + hard_sentences）

**节省 ~40% 时间**，但产出有梯度。

### 5.3 选项 C：先跑 5 篇 pilot，人工 review，再放量

我倾向 C → A：先 pilot 5 篇 v0.2 prompt，看产出能不能让用户满意，再启动全量。

---

## 6. 给 codex 的关键审视点

1. **plan B 的 `hard_sentences` 三段式（what / why / implication）会不会成为新的"装样子文本"？**——LLM 对"为什么这么说"（why）容易写成同义改写或空话。怎么收紧？
2. **`prereading` 怎么避免重复**？同一篇里"异化"出现 50 次，每段都预读一次会噪音。建议：篇章级共享 prereading（首次出现给全套），后续 reference 不重复。
3. **`reading_path.essential_paragraphs` 由 LLM 选会不会糊弄**？是不是应该让 LLM 输出"该段重要性 0-3 分"再后处理选 top-N？
4. **concept 白名单是否全闭合**？我会给 ~80 个核心术语，但马列文献术语漂移大（同一词在不同时期含义不同），白名单太严会漏掉真概念，太宽又回到 v0.1。
5. **是否保留前端「对照阅读」tab**？plain_rewrite 删了，对照模式没的对。建议改名"带支架阅读"：左原文，右段落级 gist + prereading + hard_sentences。
6. **既然要重跑，要不要顺手换模型？**v0.1 mimo-v2.5 在斯大林晚期内容审核拒了 196 段。要不要把 stalin 的部分换 deepseek-r1 / claude haiku 兜底？
7. **是否需要 LLM-as-judge 04 阶段做语义校验**（M1 立场不替换、M3 论敌识别、M5 比喻保留）？只靠 04_validate 硬规则不够。
8. **段级 LLM 单次输出 token 会从 ~1500（v0.1）涨到 ~2500-3000（v0.2 多 4 字段）**，会不会触发 mimo 截断或风控？

---

## 7. 我的初步建议（待 codex 验证）

- ✅ 删 `plain_rewrite`
- ✅ 加 `prereading` `hard_sentences` `polemic_in_paragraph` `argument_link`
- ✅ notes 加 N1-N4 硬边界
- ✅ 加 `reading_path`（reading 友好关键）
- ✅ **路径 C**：先跑 5 篇 pilot，对比 v0.1 让用户拍板，再启动全量
- ⏸ 模型不切换（mimo-v2.5 总体可用，stalin 高风险段可跑后用 deepseek 补）
- ⏸ 04 LLM-as-judge：先做硬规则版，judge 留 v0.3
