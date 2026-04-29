# Marxist_ai

## 项目定位

把 marxists.org/chinese 上的马克思 / 恩格斯 / 列宁 / 斯大林 中文译本，做"21 世纪说人话"标注。
目标：让今天的读者能直接读懂这些 19-20 世纪欧洲哲学/政治论战的旧译本，但**不改变作者立场、论敌、历史指向**。

姊妹项目：`/niuniu869_dev/guwenguanzhi_ai/`（古文观止 AI 阅读器，已完成 222 篇）。复用其 LLM 客户端、prompt 加载器、并发框架。

## 目录结构

```
data/
  raw/                    # marxists.org 抓取的 GB18030 → UTF-8 原始 HTML
  intermediate/           # 切分、分句、meta 等中间产物
  books/marxists/
    book.json
    catalog.json
    glossary.json
    documents/{author}/{year}_{slug}.json

scripts/
  llm_client.py           # 复用古文版（mimo-v2.5, RPM 100）
  prompts/                # 集中化 prompt（含 VERSION）
  01_harvest.py           # 抓 marxists.org/chinese
  01b_split.py            # 单页多文献切分（费尔巴哈 1845/1888、宣言 7 序+4 章）
  01c_seed_glossary.py    # 自带人名索引提取（无 LLM）
  01d_segment.py          # 句子级确定性切分（不让 LLM 切句）
  02a_meta.py             # 篇章级 meta + provenance 解析
  02_annotate.py          # 段落级一次跑完 gist + plain_rewrite + sentences plain + notes
  03_merge.py             # 合成最终 documents JSON
  04_validate.py          # M1-M7 硬规则机检
  run_all.py              # 串行驱动
monitor.sh                # 每 2h 巡检
logs/                     # nohup 输出
docs/
  pipeline_design_v0.1.md # 方案
  codex_review_v0.1.txt   # codex review
```

## 关键约束（M1-M7 "说人话"硬约束）

详见 `scripts/prompts/rules/speak_human_rules.md`：

- **M1** 不准改观点（核心范畴不可弱化、不可去政治化）
- **M2** 不准发明事实
- **M3** 论战对象必须显名
- **M4** 时空指代不得抽象化
- **M5** 比喻必须保留 + 解释
- **M6** 老译晦涩词给现代等价（在 notes，不替换原句）
- **M7** 客观中立（不评论、不抒情）

## 跑全量

```bash
nohup python3 scripts/run_all.py > logs/run_$(date +%Y%m%d_%H%M).log 2>&1 &
./monitor.sh &  # 每 2h 巡检
```

## 模型与限速

- `MIMO_MODEL=mimo-v2.5`
- `MIMO_RPM=100`
- 不传 `max_tokens`（mimo reasoning 很长，硬限会截断）
- 单进程串行 driver；段级 LLM 调用使用 `MAX_WORKERS=20` 并发，受 RPM 100 全局限流

## 断点续跑

每个中间产物文件（`*.json`）写入时带 `_prompt_version`。重跑时，已存在且版本匹配的跳过；版本不匹配重跑。
