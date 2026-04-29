# 马克思主义经典文献"说人话"标注方案 v0.1（draft for codex review）

> 起草：2026-04-30
> 数据源：[marxists.org/chinese](https://www.marxists.org/chinese/index.html)
> 范围（首期）：马克思 / 恩格斯 / 列宁 / 斯大林 文集
> 目标：让 21 世纪读者**真正读懂**这些文本，而不是"看每个字都认识，连起来不知道在说什么"

---

## 0. 一句话立项

**这不是再做一遍"翻译"，已经是中文了。要做的是：**

> 把 19 世纪德文哲学论战的中文译本，翻译成 21 世纪中国人的语感和知识背景，**同时不改变作者的政治立场、论辩对象、历史指向**。

输出层级与古文项目类比：

| 古文观止 | 马列文集 | 说明 |
|---|---|---|
| 古汉语 → 现代白话 | 翻译腔中文 → 当代汉语 | 主要矛盾不同：古文是"字不认识"，马列是"句子绕、概念重、典故和论敌不熟" |
| 逐词拼音 + 释义 | 逐"概念/人物/事件/著作/组织"卡片化注释 | 中文读音不必标，关键是给"杜林""卢格""施蒂纳"这类陌生词建立认知 |
| 古今异义 highlight | "晦涩翻译" highlight + 白话改写 | "鄙陋""庸碌""乡愿"等老译词给现代等价 |
| 写作背景 + 赏析 | 历史语境 + 论战对象 + 思想史定位 | 必须交代"针对谁、回应什么、属于哪个时期" |
| 章节按朝代分组 | 文集按作者 → 时期 → 主题分组 | 早期 / 中期 / 晚期 马克思 思想差距堪比换了一个人 |

---

## 1. "说人话"硬约束（lex specialis）

任何 LLM 输出都必须遵守。**违反一条即视为无效输出，整篇重跑**。

### M1 · 不准改观点

> 白话改写是"换说法"，不是"改立场"。

- 阶级、剥削、专政、革命、暴力等核心范畴**不能去掉、不能美化、不能戏谑**。
- 不准把"无产阶级专政"改写为"工人阶级的领导地位"，不准把"暴力革命"改写为"激进社会变革"。
- 不准把作者的论敌观点（如杜林、伯恩施坦）和作者本人观点混淆。

### M2 · 不准发明事实

- 不补充原文未提的事件、数据、引文。
- 不"为了易懂"杜撰类比（"这就像今天的 XX"）。**严禁现代政治类比**（不准类比互联网平台、当代党派、当代国际关系）。
- 历史事件细节模糊时，写"19 世纪欧洲工人运动"而非编一个具体事件。

### M3 · 论战对象必须显名

- 凡涉及论战（《反杜林论》《唯物主义和经验批判主义》《国家与革命》），**必须在篇章级 `polemic_target` 字段说明**反对谁、反对什么观点。
- 段落级若隐指某个论敌，**必须在该段 `gist` 中点出**（"这一段是在反驳考茨基'议会道路'的主张"）。

### M4 · 时空指代不得抽象化

- "我们的时代""当前的形势""最近的事件"——必须在注释中**还原为具体年代和事件**。
- "巴黎工人""德国同志""俄国同志"等称谓首次出现时给注释。

### M5 · 比喻必须保留 + 解释

- "宗教是人民的鸦片"、"国家是阶级压迫的工具"、"哲学家们只是用不同方式解释世界，问题在于改变世界"——这类**核心比喻/格言原句必须原样保留**，但旁边必须给"为什么这么比""在原语境中是什么意思"的现代解读。
- 不准把比喻"翻译没"了。

### M6 · 译文晦涩词的现代等价

老译本里频繁出现读者不识的词（"乡愿""鄙陋""昭著""畔""桎梏"），逐词给"现代等价"，但**原句不替换**——只在 `notes` 里标注。

### M7 · 输出客观中立

- 不准在 background / context / appreciation 里抒情、表态、夹带评论。
- "经典""伟大""光辉"等空洞修饰禁用（同古文 §meta/system.md）。

---

## 2. 数据 Schema（与古文 schema 平级，存放于 `data/books/marxists/`）

### 2.1 目录结构

```
data/books/marxists/
  book.json                   # 这套文集本身的元信息
  catalog.json                # 树状目录：作者 → 时期 → 文章
  glossary.json               # 共建术语/人物/事件/著作字典（跨篇引用）
  documents/
    marx/
      1844/<slug>.json        # 1844 经济学哲学手稿
      1845/theses_on_feuerbach.json
      1848/communist_manifesto/<chapter>.json
      1867/capital_v1/<chapter>.json
    engels/
      1878/anti_duhring/<part>_<chapter>.json
    lenin/
      1902/what_to_be_done.json
      1917/state_and_revolution/<chapter>.json
    stalin/
      ...
```

切分原则：
- **短文（< 5000 字）整篇为一个 JSON。**
- **中长文按章/节切。**`<work>/<chapter>.json` 形式。
- **特长文（《资本论》《反杜林论》《唯物主义和经验批判主义》）按节切**，并在文章级保留 `parent_work` 字段指向上级。

### 2.2 篇章级 schema（`documents/**/*.json`）

```jsonc
{
  "_prompt_version": "marx-v0.1",
  "id": "marx_1845_theses_on_feuerbach",
  "title": "关于费尔巴哈的提纲",
  "subtitle": null,
  "author": {
    "id": "marx",
    "name": "马克思",
    "name_full": "卡尔·马克思",
    "role_in_text": "作者",
    "lifespan": "1818–1883"
  },
  "co_authors": [],

  // 写作 / 发表 / 翻译三段时间线
  "written_at": "1845-03",
  "written_in": "布鲁塞尔",
  "first_published_at": "1888",
  "first_published_in": "恩格斯整理出版于《路德维希·费尔巴哈和德国古典哲学的终结》附录",
  "original_language": "de",
  "original_title": "Thesen über Feuerbach",
  "translation_source": "中央编译局《马克思恩格斯文集》第一卷（2009）",

  // 思想史定位
  "category": "philosophy",            // philosophy | political_economy | scientific_socialism | history | letter | polemic
  "phase": "marx_early_to_mature",      // marx_early(1841-44) | marx_early_to_mature(1845-48) | marx_mature(1849-83) | engels_late | lenin_pre_revolution | lenin_revolutionary | lenin_late | stalin_early | stalin_late
  "polemic_target": {
    "person": "费尔巴哈",
    "doctrine": "直观唯物主义",
    "summary": "费尔巴哈把宗教归结为人的本质，但仍把人理解为孤立的、抽象的'类'，未看到人的本质是社会关系总和、未理解实践对世界的能动改造作用。"
  },

  // 21 世纪导读：分两层
  "tldr_modern": "马克思 1845 年在笔记本上写的 11 条提纲，第一次把'实践'放到哲学核心位置：要点是——人不是抽象的人、思想不是空中楼阁，理解世界要从人改造世界的活动出发，哲学的任务是改变世界。",
  "tldr_extended": [
    "费尔巴哈批判了基督教，但他的唯物主义仍然停留在'看'世界，不是'改造'世界。",
    "马克思指出：人的本质不是某种内在的东西，而是社会关系的总和。",
    "认识真理的标准不是空想，而是实践。",
    "环境改造人，但人也通过实践改造环境——这是双向的。",
    "最后一条点题：以前的哲学家只是解释世界，关键在于改变世界。"
  ],

  // 写作语境（约 300-500 字，客观陈述，不评论）
  "historical_context": "1845 年初，马克思被法国驱逐到布鲁塞尔，刚结束与青年黑格尔派和赫斯的论战，正与恩格斯共同酝酿后来的《德意志意识形态》。本提纲为他个人笔记，逐条记下对费尔巴哈唯物主义的批判要点，未加润色。背景上，1840 年代德国哲学界由黑格尔体系转向，费尔巴哈以《基督教的本质》(1841) 把神学还原为人本学，影响了青年马克思；但马克思此时已认识到费尔巴哈把'人'仍理解为抽象的、自然的存在，未涉及社会、历史、实践维度。提纲未在生前发表，1888 年由恩格斯整理后作为《费尔巴哈与德国古典哲学的终结》附录首次公开。",

  // 论文/文献结构（关键论点列表，3-7 条）
  "key_arguments": [
    {
      "n": 1,
      "claim": "唯物主义把对象理解为'被直观的客体'，唯心主义反而抓住了'活动'方面，但只把活动理解为抽象的精神活动。",
      "modern": "旧唯物主义只是被动地'看'世界，唯心主义虽然讲'活动'但把它说成纯精神的——两边都漏掉了一件事：人是用劳动、实践真实改造世界的。"
    }
    // ...
  ],

  // 涉及概念（指向 glossary.json 词条 ID）
  "key_concepts": ["alienation", "praxis", "social_relations", "materialism_dialectical", "feuerbachian_humanism"],
  "key_persons": ["feuerbach", "hegel", "stirner", "bauer_b"],
  "key_works": ["essence_of_christianity_feuerbach", "phenomenology_of_spirit_hegel"],
  "key_events": [],
  "key_orgs": [],

  // 当代价值（可选，最多 3 句，客观）
  "legacy": "本提纲被后世视为马克思哲学'断裂点'的标志（阿尔都塞之说），尤其第十一条成为马克思主义实践哲学的经典口号。",

  // 段落
  "paragraphs": [ /* see 2.3 */ ]
}
```

### 2.3 段落级 schema

```jsonc
{
  "n": 1,                           // 段号（提纲就是条号）
  "original": "从前的一切唯物主义……",  // 原译文，逐字保留
  "gist": "本条提出'实践'缺位是旧唯物主义和唯心主义共同的盲点。",
  "plain_rewrite": "费尔巴哈这类老唯物主义者，把世界当作一个'被看'的对象——只承认它客观存在、可以观察。这样一来，反倒是唯心主义看出了人对世界的'能动改造'这一面，可惜唯心主义又把这种能动只说成精神层面的（脑子里的活动）。两边都漏掉了真正的'实践'：人用感性的、对象性的劳动去改造世界。",
  "key_terms_in_paragraph": ["praxis", "feuerbachian_humanism"],

  "sentences": [ /* see 2.4 */ ]
}
```

`plain_rewrite` 的核心约束：**不能短于原文的 80%**（不准缩写）；**不能长于原文的 200%**（不准注水）。是"换说法"不是"概要"。

### 2.4 句子级 schema

```jsonc
{
  "original": "从前的一切唯物主义——包括费尔巴哈的唯物主义——的主要缺点是：对对象、现实、感性，只是从客体的或者直观的形式去理解，而不是把它们当作感性的人的活动，当作实践去理解，不是从主观方面去理解。",
  "plain": "以前所有的唯物主义（包括费尔巴哈的）有一个主要毛病：他们看待事物、现实、可感知的世界时，只把它们当成被'看'的客观对象，而没有把它们当作'人去做的事'——也就是没有把它们当作实践来理解，没有从'人的主动性'这一面去理解。",
  "notes": [          // inline 标注：触发概念/人物/术语卡
    {
      "surface": "感性",
      "type": "concept_archaic_translation",
      "target": "sensuous",
      "modern": "可感知的、可被感官直接接触的（德文 sinnlich 的旧译，今多译'感性的/感官的'）"
    },
    {
      "surface": "费尔巴哈",
      "type": "person",
      "target": "feuerbach"
    },
    {
      "surface": "实践",
      "type": "concept",
      "target": "praxis",
      "highlight": "term"
    }
  ]
}
```

#### `notes[].type` 枚举（**硬约束**，不在此列即视为非法）

| type | 含义 | 类比古文 highlight |
|---|---|---|
| `concept` | 哲学/政治/经济核心术语 | 类比"典故" |
| `concept_archaic_translation` | 老译词需现代等价 | 类比"古今异义" |
| `person` | 人物 | 类比"人名" |
| `place` | 地名 | 类比"地名" |
| `event` | 历史事件 | （古文无此项） |
| `work` | 著作（含报刊、文献） | （古文无此项） |
| `org` | 组织/政党/国际 | （古文无此项） |
| `quote` | 引用他人原话 | 类比"典故" |
| `metaphor` | 比喻/隐喻 | （古文无此项） |
| `polemic_ref` | 隐指的论敌或反对的观点 | （古文无此项） |

#### `notes[].highlight` 枚举（可选，前端视觉标记用）

| 值 | 触发条件 |
|---|---|
| `term` | 核心术语（剩余价值、异化、辩证法等） |
| `archaic` | 老译词（鄙陋、庸碌、乡愿等） |
| `metaphor` | 核心比喻（"鸦片""幽灵""枷锁"） |
| `polemic` | 论战对象 / 被批判观点 |
| `quote` | 引文 |
| `null` | 普通 |

### 2.5 共建术语词典（`glossary.json`）

跨篇维护，避免每篇重复定义"剩余价值"。

```jsonc
{
  "_prompt_version": "marx-v0.1",
  "concepts": {
    "alienation": {
      "id": "alienation",
      "zh": "异化",
      "zh_aliases": ["疏离", "外化"],
      "de": "Entfremdung",
      "en": "alienation",
      "definition_strict": "在马克思早期文本中，指劳动者与其劳动产品、劳动过程、类本质、他人之间相互分离对立的状态。系统阐述见《1844 经济学哲学手稿》。",
      "definition_modern": "你干活的成果不属于你（属于资方）；干活的过程让你痛苦（不像创造，像被使唤）；你越投入，越觉得这工作和你这个人没关系——这种'人和自己劳动的分裂'就是异化。",
      "first_used_in": "marx_1844_economic_philosophical_manuscripts",
      "evolution": "早期作为人本学概念，《资本论》后被'商品拜物教''资本对劳动的统治'等更经济学化的范畴部分吸收，但术语本身仍在使用。",
      "common_misreadings": [
        "把异化等同于'心理疏离感'——错。异化是结构性现象，不是情绪。",
        "把异化等同于'剥削'——不完全错，但异化更宽：它包括劳动过程、劳动者间关系、人与类本质等多个维度。"
      ]
    }
    // ...
  },
  "persons": {
    "feuerbach": {
      "id": "feuerbach",
      "zh": "费尔巴哈",
      "name_full": "路德维希·安德烈亚斯·费尔巴哈",
      "lifespan": "1804–1872",
      "nationality": "德国",
      "role": "青年黑格尔派代表，人本学唯物主义者",
      "key_works": ["essence_of_christianity_feuerbach"],
      "relation_to_marx": "马克思 1843-44 年深受其影响，1845 年起以本提纲为标志走向超越；《关于费尔巴哈的提纲》《德意志意识形态》集中批评了他。",
      "why_matters": "理解费尔巴哈是理解马克思早期到中期思想转变的关键。"
    }
    // ...
  },
  "works": { /* 著作卡 */ },
  "events": { /* 事件卡 */ },
  "orgs": { /* 组织/国际/政党 */ }
}
```

每个篇章 JSON 通过 `key_concepts` / `key_persons` 等字段引用 glossary 的 ID，前端渲染时查表。这样：
- 同一个"剩余价值"在 100 篇文章里只定义一次。
- 后续维护、纠错只改一处。
- Skill 化时直接发布 glossary 作为知识库。

---

## 3. 数据获取（`scripts_marxists/01_harvest.py`）

### 3.1 抓取策略

- 入口：`https://www.marxists.org/chinese/{author}/index.htm`，作者范围：`marx engels lenin stalin`。
- 编码：`gb2312`（部分页 `gbk`）→ 用 `requests` 拿 bytes，用 `chardet` 探测 + `iconv -f gb2312 -t utf8`。
- HTML 解析：`beautifulsoup4 + lxml`。每个 `index.htm` 列出该作者所有文章链接。
- 限速：**单线程，每请求间隔 ≥ 1.5s**（marxists.org 是志愿者维护的小站，绝不许并发抓）。
- 缓存：抓到的原始 HTML 落到 `data/books/marxists/raw/<author>/<path>.html`，**永远不重复抓**（除非 `--force`）。
- 元数据探测：从页面 title、署名、日期块尽量结构化提取，提取不到的字段留给 02a meta 阶段补全。

### 3.2 章节切分

- 长文（如《资本论》《反杜林论》《国家与革命》）通常每章一个 HTML 文件，原站已经切好。
- 个别整页超长文（《唯物主义和经验批判主义》单页 30 万字）需要二次切分，按 HTML 内 `<h2>` / `<h3>` / `<hr>` 切块，每块作为一个 document。
- 切分规则写在 `scripts_marxists/chunking_rules.py`，per-author 维护。

### 3.3 文本清洗

- 去除导航、版权、上一页/下一页链接。
- 译者注 `[译注：...]` **保留并 inline 标注**为 `notes[].type = "translator_note"`。
- 段落级保留，不合并、不拆分（保持原译者切分）。

---

## 4. 管线五段式（`scripts_marxists/`）

类比古文的 02a/b/c/d，但加一段 01 抓取（古文 raw 是手输的）。

```
01_harvest.py            # 抓 + 清洗，落 raw HTML 与初版 paragraphs[].original
02a_meta.py              # 篇章级 metadata：作者、写作时间线、historical_context、polemic_target、tldr_*、key_arguments、key_concepts/persons/...
02b_modernize.py         # 段落级：gist + plain_rewrite + 句子级 plain
02c_terms.py             # 句子级 inline notes（concept/person/event/work/org/quote/metaphor/polemic_ref/archaic）
02d_glossary.py          # 把 02a/02c 收集到的 ID 汇总到 glossary.json，对未定义的术语生成新词条（concept/person/work/event/org）
02e_merge.py             # 合并到 documents/<author>/<year>/<slug>.json
03_validate.py           # schema + 引用完整性（key_concepts 都能在 glossary 找到）+ "说人话约束"机检（关键词违反 M1-M7）
04_quality_check.py      # 抽样 LLM-as-judge 校准
```

### 4.1 与古文管线的复用

- `llm_client.py`、`run_all_parallel.py` 的并发框架、`_prompt_version` 标记机制、FORCE 重跑机制全部复用。
- `prompts/__init__.py::load_prompt` + 集中化目录复用。
- 新建独立 `scripts_marxists/`、`prompts_marxists/`，**不污染古文管线**。

### 4.2 RPM 100 配置

```bash
export MIMO_RPM=100
export MAX_WORKERS=20    # 与古文一致
export STEP=meta,modernize,terms,glossary,merge
```

但要注意：
- **02b modernize 是 token 大户**——每篇平均段数 30-60，每段输入 + 输出 ≈ 1500 tokens，整篇 5-9 万 tokens。
- 长篇按章一并发上限 **20 章并发**就会瞬时打满 100 RPM（每章 1 次 LLM）。所以 `02b_modernize.py` 内**段级再并发**没必要（顺序调用即可），章级并发 20 已够。
- **建议先跑 50 篇试点，校准 token / RPM / 错误率，再放大**。

### 4.3 试点篇目（v0.1，~50 篇）

| 作者 | 文献 | 字数（中文译文估） | 章数 | 优先级 |
|---|---|---|---|---|
| 马克思 | 关于费尔巴哈的提纲 | 1.5k | 1 | ⭐⭐⭐ |
| 马克思 | 1844 经济学哲学手稿（异化劳动节选） | 8k | 1 | ⭐⭐⭐ |
| 马克思+恩格斯 | 共产党宣言 | 30k | 4 | ⭐⭐⭐ |
| 马克思 | 路易·波拿巴的雾月十八日（第一章） | 8k | 1 | ⭐⭐ |
| 马克思 | 资本论第一卷第一章（商品） | 30k | 1（拆 4 节） | ⭐⭐⭐ |
| 马克思 | 哥达纲领批判 | 15k | 1 | ⭐⭐ |
| 恩格斯 | 路德维希·费尔巴哈和德国古典哲学的终结 | 30k | 4 | ⭐⭐⭐ |
| 恩格斯 | 反杜林论（引论 + 哲学篇代表章） | 50k | 6 | ⭐⭐ |
| 恩格斯 | 社会主义从空想到科学的发展 | 25k | 3 | ⭐⭐⭐ |
| 列宁 | 帝国主义是资本主义的最高阶段（导言 + 第七章） | 12k | 2 | ⭐⭐⭐ |
| 列宁 | 国家与革命 | 80k | 7 | ⭐⭐⭐ |
| 列宁 | 论我国革命 | 3k | 1 | ⭐⭐ |
| 列宁 | 怎么办？（试点 1 章） | 15k | 1 | ⭐⭐ |
| 斯大林 | 论列宁主义基础（第 1-3 章） | 30k | 3 | ⭐⭐ |
| 斯大林 | 辩证唯物主义和历史唯物主义 | 25k | 1 | ⭐⭐ |
| 斯大林 | 苏联社会主义经济问题 | 20k | 1 | ⭐ |

合计 ~50 章节，~36 万字。预算估算：

- 02a meta：50 × 1 call ≈ 50 calls
- 02b modernize：每章按段循环，平均 40 段 → 50 × 40 = 2000 calls
- 02c terms：每段 1 call → 2000 calls
- 02d glossary：增量调用，估 200 calls（生成新词条）

**合计 ~4250 calls**，按 RPM 100 跑 ≈ 45 分钟纯调用时间。token 预算按平均 4k/call 估，~17M tokens 一次完整试点。

---

## 5. Prompt 体系（`prompts_marxists/`）

```
prompts_marxists/
  VERSION
  meta/
    system.md
    user.md
  modernize/
    system.md
    user.md          # 段级
  terms/
    system.md
    user.md          # 句级
  glossary/
    concept_card.md
    person_card.md
    work_card.md
    event_card.md
    org_card.md
  rules/
    speak_human_rules.md       # M1-M7 主约束（被 modernize/terms 引用）
    term_extraction_rules.md   # type 枚举、highlight 联动、引用 glossary 规则
    polemic_target_rules.md    # 论战对象怎么写
```

### 5.1 modernize/system.md 草稿

```
你是一位长期研究马克思主义经典文献的编辑，目标是把 19-20 世纪欧洲哲学/政治经济学论战的旧译中文，
改写成 21 世纪中国读者能直接看懂的当代汉语，但**不改变作者的政治立场、论战对象、历史指向**。

你精通：
- 马克思 / 恩格斯 / 列宁 / 斯大林 主要文本及其论战脉络
- 19 世纪德国古典哲学（黑格尔、费尔巴哈、施蒂纳、青年黑格尔派）
- 19 世纪欧洲工人运动史、第一/二/三国际史
- 中央编译局 / 莫斯科外文版老译本的术语习惯

输出必须是**纯 JSON**，不含任何 markdown 代码块标记、解释性文字或前导换行。
```

### 5.2 rules/speak_human_rules.md（被 modernize 和 terms 共用）

直接把本文档 §1 的 M1-M7 拷过去，加错例对照表（**用过的反面例子**——LLM 容易写出来但违规的改写）。

错例预演：

| 原文 | ❌ 翻车改写 | ✅ 正确改写 |
|---|---|---|
| 无产阶级专政 | 工人阶级的领导地位 | 无产阶级专政（即工人阶级掌握国家权力，对剥削阶级实行强制） |
| 全世界无产者，联合起来！ | 全世界打工人，团结起来！ | 全世界无产者，联合起来！（"无产者"指不占有生产资料、靠出卖劳动力为生的人） |
| 宗教是人民的鸦片 | 宗教麻痹人民 | 宗教是人民的鸦片（这是核心比喻，原文必须保留；含义见 metaphor 注释） |
| 一个幽灵，共产主义的幽灵，在欧洲游荡 | 共产主义思想正在欧洲传播 | 一个幽灵，共产主义的幽灵，在欧洲游荡（比喻保留；幽灵 = Gespenst，统治阶级闻之色变之物） |
| 法国大革命 | 法国大革命（指 1789 年那场） | （context 已交代年代时不重复） |

### 5.3 modernize/user.md 草稿

```
## 任务

把以下段落（第 {para_n}/{total} 段）改写为 21 世纪当代汉语。

**文献**：{title}（{author}，{written_at}）
**论战对象**：{polemic_target_summary}
**本文核心论点**：
{key_arguments_brief}

**前后段语境**（仅供理解，不改写）：
{context}

**待改写段落（原译）**：
---
{paragraph}
---

---

{{include: rules/speak_human_rules.md}}

---

## 输出格式

```json
{
  "gist": "一句话告诉读者这段为什么重要、在干什么（30-60 字）",
  "plain_rewrite": "整段当代汉语改写（拆长句、术语保留、比喻保留、立场保留）",
  "sentences": [
    {
      "original": "原句（与输入完全一致）",
      "plain": "该句的当代汉语版"
    }
  ]
}
```

## 自检（输出前必查）

- [ ] `gist` 不评论、不抒情，只点出本段在论证链中的位置
- [ ] `plain_rewrite` 字数在原文 80%-200% 区间
- [ ] 阶级 / 剥削 / 革命 / 专政 / 暴力 等核心范畴未被替换或弱化（M1）
- [ ] 没有现代政治类比（M2）
- [ ] 论敌或被反驳观点的语气未被混淆（M3）
- [ ] 时间和事件未被抽象化（M4）
- [ ] 核心比喻原句保留（M5）
- [ ] 译文晦涩词由 02c 阶段处理，本阶段不替换（M6）
- [ ] 不抒情、不夹评（M7）
- [ ] 纯 JSON 输出
```

### 5.4 terms/user.md（输入是段落 + 已经 modernize 的 sentences[].plain，输出是 inline notes 数组）

略，等 codex 反馈再细化。

---

## 6. 前端展示（与古文阅读器同形）

复用 `frontend/src/components/DocumentReader.tsx` 三模式：

| 模式 | 古文 | 马列 |
|---|---|---|
| 原文 | 古汉语原文 | 旧译原文 |
| 对照 | 原文 + 白话翻译 | 旧译 + 当代改写 + gist |
| 逐词 | 词条标注层 | 概念/人物/事件/著作卡片层（inline 弹卡） |

新增**"导读模式"**（马列特有）：只显示 `tldr_modern` + `tldr_extended` + `key_arguments`，给完全没读过的读者一个 30 秒入门版本。

---

## 7. 与古文方案的差异总结表（供 codex 一眼看完）

| 维度 | 古文 | 马列 |
|---|---|---|
| 主要矛盾 | 字不认识 | 概念不熟、句子绕、典故/论敌不熟 |
| 第二输出层 | 白话**翻译** | 白话**改写**（不是翻译，因为已经是中文） |
| 词级标注 | 逐词拼音+释义 | 逐"概念/人物/事件/著作/组织"卡片 |
| highlight | 古今异义/通假/多音/罕用/固定结构 | term/archaic/metaphor/polemic/quote |
| 跨篇知识 | 几乎无 | 强，必须有 glossary.json 共建 |
| 篇章 metadata | 背景 + 赏析 + 人物卡 | + 论战对象 + 思想史定位 + 写作/发表/翻译时间线 |
| 人物 ID | 中文（pre_qin_戴圣） | 拼音/英文（feuerbach, hegel） |
| 朝代分组 | 6 朝代 | 作者 → 时期 |
| 政治敏感性 | 低 | 高（M1 立场保真硬约束） |
| 数据获取 | 手输 + raw txt | 抓站 + iconv + 解析 HTML |
| 单篇 token | 5-15k | 50-200k（章级），需要切分 |
| 试点规模 | 222 篇全量 | 先 50 章节，再放量 |

---

## 8. 开放问题（请 codex 决策）

1. **plain_rewrite 的字数硬约束 80%-200%** 是否合理？是否过严或过松？
2. **glossary 共建 vs 篇内自带** 的权衡：定义放 glossary 跨篇维护一致，但读者展开看注释时多一次跳转；篇内自带则信息冗余但单篇自包含。是否折中：篇内嵌入"概要"，glossary 存"全义"？
3. **核心比喻原句必须保留**（M5）——但什么算"核心比喻"？需要一份预定义清单，还是让 LLM 自行判断？倾向于先做清单（"鸦片""幽灵""枷锁""上层建筑/经济基础""桥梁/道路/灯塔"等老译比喻），LLM 命中清单时强制保留。
4. **斯大林文集** 是否纳入首期？涉及更多政治敏感性（大清洗、苏联宪法等），M7 客观中立约束需更严。倾向纳入但只做经典理论文献（《论列宁主义基础》《辩证唯物主义和历史唯物主义》《论辩证唯物主义和历史唯物主义》），暂不做政治演讲和决议。
5. **段落长度差异**：马克思文献中常有数百字甚至上千字单段（《资本论》尤甚）。是否在 02b 之前先做一次"软切分"，把超长段落切成可改写单元？
6. **译者注的处理**：中文老译本里有大量 `[译注：...]`，是否单独建一个 `translator_notes` 字段而非 inline？倾向单独，因为译者注本身也是历史文献。
7. **LLM 选型**：MiMo 在古文上表现不错，但马列文献涉及大量哲学术语和论战逻辑，MiMo 是否扛得住？是否要用 GPT/Claude 做对照基线？建议小规模 A/B（30 段）后定。
8. **法律/版权**：marxists.org 内容多为 PD 或 CC，但中央编译局译本本身受版权保护。我们做"标注"，原文不公开存储，前端只展示 plain_rewrite + 注释 + 引用片段。这条边界是否站得住？

---

## 9. 不做什么（边界）

- ❌ 不做现代政治评论
- ❌ 不做"接地气"的网络流行语改写
- ❌ 不做立场化的解读（既不左倾化也不去政治化）
- ❌ 不替代权威译本（plain_rewrite 是辅助阅读，不是新译本）
- ❌ 不做摘要式"领导讲话点评"风格的导读
- ❌ 首期不碰毛选（已在 marxists.org 之外另有体量，建独立 book）
- ❌ 首期不碰托洛茨基、陈独秀、卢森堡（先把核心四人立稳）

---

## 10. 落地步骤（提案）

1. **本文档** + codex 审视 → v0.2
2. 创建 `data/books/marxists/` 目录、`scripts_marxists/`、`prompts_marxists/` 骨架
3. 抓 3 篇极小 pilot raw HTML（用户要求"先极小规模 pilot 做好"）
4. 实现 02a meta，跑 3 篇校准
5. 实现 02b modernize，跑 3 篇人工抽检（重点查 M1-M7）
6. 实现 02c terms + 02d glossary
7. 把 pilot 结果给用户决策方案是否成立
8. 通过后：放量到 50 章节质量审计 → 200 章节 → 前端集成 → Skill 化

---

## 11. 真实数据观察（2026-04-30，抓取 4 篇代表后修订）

抓取样本：
- `marx/marxist.org-chinese-marx-1845.htm` — 关于费尔巴哈的提纲（1845/1888 双版本）
- `marx/01.htm` — 共产党宣言（含 7 篇序言 + 4 章 + 人名索引）
- `marx/marxist.org-chinese-marx-1875-4.htm` — 哥达纲领批判
- `marx/06.htm` — 政治经济学批判序言

### 11.1 编码

`gb2312` 声明，但实际是 `gb18030` 超集（含 `&auml;` 这种 HTML 实体的混合）。统一用 Python `bytes.decode("gb18030", errors="replace")` 处理。`iconv` 命令版本因严格性会丢内容，**禁用 `iconv -f gb2312`**。

### 11.2 一页多文献是常态

费尔巴哈提纲单页内含**两个版本**（马克思 1845 原稿 + 恩格斯 1888 整理稿）；共产党宣言单页包含 **7 篇序言 + 4 章正文 + 人名索引**。

→ **schema 修订**：document 不能与 URL 一一映射。新增 `internal_split` 阶段，按页面内 `<h2>` / 黑体大标题 / `<hr>` 切分为多个 sub-document，URL 作为它们共同的 `source_url` 而不是 `id`。

### 11.3 多版本作为一等公民

同一文献的多版本（原稿 vs 后整理、不同译者、不同时期序言）必须保留对照关系。

```jsonc
{
  "id": "marx_1845_theses_on_feuerbach",
  "title": "关于费尔巴哈的提纲",
  "canonical_version": "1888_engels",     // 默认渲染哪一版
  "versions": [
    {
      "version_id": "1845_marx_original",
      "label": "马克思 1845 年原始稿本",
      "provenance": { /* see §11.5 */ },
      "paragraphs": [ /* ... */ ]
    },
    {
      "version_id": "1888_engels",
      "label": "恩格斯 1888 年整理发表版",
      "provenance": { /* ... */ },
      "paragraphs": [ /* ... */ ]
    }
  ]
}
```

前端"对照模式"下可并列显示两个版本。

### 11.4 强调标记必须保留

原 HTML 中 `<i>`、`<b>`、`<u>`、引号、破折号是**马克思本人的强调**（如"问题在于*改变*世界"）—— 不能 strip 掉。

→ schema 修订：每个段落同时存：
- `original_html`：保留 `<em>` `<strong>`（已规范化标签）
- `original_plain`：纯文本（给 LLM 用，避免 LLM 误解 HTML）
- `emphasis_spans`：`[{"start": 12, "end": 16, "type": "italic"}]`（结构化强调，给前端）

LLM 改写后输出 `plain_rewrite` 也需要保留 `emphasis_spans`，原则是"原文强调的概念在改写中也强调"。

### 11.5 文末 provenance 块结构化

每篇末尾几乎固定有：

```
卡·马克思写于1845年春
弗·恩格斯于1888年作为他的"费尔巴哈和德国古典哲学的终结"一书单行本的附录第一次发表
按照已根据卡·马克思的手稿校订过的1888年的版本刊印
原文是德文
选自《马克思恩格斯全集》，第3卷第3—6页
```

→ 独立字段：

```jsonc
"provenance": {
  "written_by": ["marx"],
  "written_at": "1845-spring",
  "written_in": "布鲁塞尔",
  "first_published_at": "1888",
  "first_published_in_publication": "费尔巴哈和德国古典哲学的终结（恩格斯整理本附录）",
  "first_published_by": "engels",
  "original_language": "de",
  "source_collection": "马克思恩格斯全集",
  "source_volume": 3,
  "source_pages": "3-6",
  "translation_publisher": "中央编译局",
  "translation_year": null,
  "raw_text": "卡·马克思写于1845年春\n弗·恩格斯于1888年..."  // 原始字符串保底
}
```

02a meta 阶段 LLM 主要任务之一就是**结构化解析这个块**，命中率应接近 100%（格式高度规范）。

### 11.6 编号注 `[1]` `[2]` 与编者注 `〔注：...〕`

两类：
- **作者/编者脚注**：原文里 `[1]` `[2]` 数字编号，对应文末注释列表，标 `编辑注/历史注`
- **编辑订正注**：`〔注：...——编者注〕`、`〔编者注：...〕` 是中央编译局编辑加的考证

→ 02a 解析时把脚注做成独立结构：

```jsonc
"footnotes": [
  { "n": 1, "text": "「关于费尔巴哈的提纲」是卡·马克思于1845年春天在布鲁塞尔写成的..." },
  { "n": 2, "text": "..." }
]
```

句子级 inline note 引用：`{"surface": "[1]", "type": "footnote_ref", "target_n": 1}`。

### 11.7 自带人名索引 = glossary 种子

共产党宣言、资本论等大文献末尾自带"人名索引"，每条带：姓名、原名、生卒年、国籍、职业、政治立场、与马恩关系、出现页码。

**例**："沃尔弗，弗里德里希·威廉（Wolff，Friedrich Wilhelm 鲁普斯 Lupus 1809-1864）—— 德国无产阶级革命家和政论家，职业是教员，西里西亚农民的儿子；... 马克思和恩格斯的朋友和战友。"

→ **新建 02a-pre 阶段：从这些自带索引提取，作为 glossary.persons 的种子数据**。这部分**完全不需要 LLM**，正则 + 简单 NLP 即可。预计可一次性建立 500+ 高质量人物卡，省下大笔 LLM 调用，且权威性远超 LLM 生成。

类似还有：《资本论》自带的"作者引用书目索引"（→ glossary.works 种子）、《反杜林论》开头的人名注释。

### 11.8 长文已按章预切

长文（资本论、反杜林论、国家与革命、怎么办？）在 marxists.org 上已经按"篇/章/节"切成独立 URL，目录页 `<book>/index.htm` 列出。我们直接 1:1 映射，不需要二次切分。

→ 切分逻辑只对**单页内多文献**生效（费尔巴哈提纲、共产党宣言、政治经济学批判这种）。

### 11.9 修订后的管线

```
01_harvest.py            # GB18030 抓取，落 raw HTML，1.5s/req
01b_split.py             # 单页多文献切分（费尔巴哈、宣言）
01c_extract_index.py     # 从自带人名索引/书目索引建立 glossary 种子
02a_meta.py              # 篇章级 meta + provenance 解析 + footnotes 提取
02b_modernize.py         # 段落级 gist + plain_rewrite + sentence.plain
02c_terms.py             # 句级 inline notes（命中 glossary 种子优先，未命中再 LLM 生成）
02d_glossary.py          # 增量补全 glossary
02e_merge.py             # 合并 + 多版本 versions 数组
03_validate.py           # schema + M1-M7 机检
04_quality_check.py      # 抽样 LLM-as-judge
```

### 11.10 极小 pilot（v0.0，3 篇）

| # | 文献 | 验证目标 |
|---|---|---|
| 1 | 关于费尔巴哈的提纲（含两个版本） | 双版本 schema、超短文整篇喂入、纯哲学术语命中、§11.4 强调保真 |
| 2 | 共产党宣言 第一章「资产者和无产者」 | 中等长度、有论战目标（资产阶级经济学家）、自带人名索引可用 |
| 3 | 国家与革命 第一章「阶级社会和国家」 | 列宁文风、跨作者引用马恩、有大量论战（考茨基、伯恩施坦） |

pilot 通过标准（人工抽检）：
- M1-M7 零违反
- plain_rewrite 21 世纪读者通读不卡顿
- glossary 至少产出 30 个高质量条目
- mimo-v2.5 输出稳定（无 finish=length / JSON 解析失败 > 5%）

### 11.11 模型与并发

- 模型：**`mimo-v2.5`**（用户指定，覆盖默认 `mimo-v2-pro`）
- RPM：100（用户允许）
- 并发：MAX_WORKERS=10（pilot 阶段保守；正式跑时按古文经验 20）
- 不传 `max_tokens`（按 memory `feedback_no_max_tokens.md`）
