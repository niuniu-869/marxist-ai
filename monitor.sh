#!/bin/bash
# 每 15 分钟轻量巡检，写到 logs/monitor.log
ROOT="/niuniu869_dev/Marxist_ai"
cd "$ROOT" || exit 1
mkdir -p logs

while true; do
  TS=$(date +'%Y-%m-%d %H:%M:%S')
  RAW=$(find data/raw -name '*.html' 2>/dev/null | wc -l)
  SPLIT=$(find data/intermediate/01b_split -name '*.json' 2>/dev/null | wc -l)
  SEG=$(find data/intermediate/01d_segment -name '*.json' 2>/dev/null | wc -l)
  META=$(find data/intermediate/02a_meta -name '*.json' 2>/dev/null | wc -l)
  ANN=$(find data/intermediate/02_annotate -name 'p*.json' 2>/dev/null | wc -l)
  FIN=$(find data/books/marxists/documents -name '*.json' 2>/dev/null | wc -l)
  # ps 替代 pgrep -af（pgrep 的 \| 跨 shell 不稳）
  RUNNING=$(ps -ef | grep -E "scripts/(run_all|01_harvest|01b_split|01d_segment|02a_meta|02_annotate|03_merge)\.py" | grep -v grep | wc -l)
  STAGE=$(ps -ef | grep -E "scripts/(01_harvest|01b_split|01d_segment|02a_meta|02_annotate|03_merge)\.py" | grep -v grep | head -1 | grep -oE "(01_harvest|01b_split|01d_segment|02a_meta|02_annotate|03_merge)" | head -1)
  printf '%s | raw=%-4d split=%-4d seg=%-4d meta=%-4d ann=%-5d final=%-4d procs=%d stage=%s\n' \
    "$TS" "$RAW" "$SPLIT" "$SEG" "$META" "$ANN" "$FIN" "$RUNNING" "${STAGE:-idle}" >> logs/monitor.log
  sleep 900
done
