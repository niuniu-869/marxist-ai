#!/bin/bash
# 每 2 小时巡检一次管线进度，写到 logs/monitor.log
# 用法: nohup ./monitor.sh > logs/monitor.out 2>&1 &

ROOT="/niuniu869_dev/Marxist_ai"
cd "$ROOT" || exit 1
mkdir -p logs

while true; do
  TS=$(date +'%Y-%m-%d %H:%M:%S')
  {
    echo "==================== $TS ===================="
    echo "## raw HTML"
    find data/raw -name '*.html' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## 01b_split"
    find data/intermediate/01b_split -name '*.json' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## 01d_segment"
    find data/intermediate/01d_segment -name '*.json' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## 02a_meta"
    find data/intermediate/02a_meta -name '*.json' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## 02_annotate"
    find data/intermediate/02_annotate -name '*.json' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## 03 final"
    find data/books/marxists/documents -name '*.json' 2>/dev/null | wc -l | xargs echo "  files:"
    echo "## run process"
    pgrep -af "run_all.py\|02_annotate\|02a_meta" | head -10 || echo "  (no run_all process)"
    echo "## last run log"
    LATEST_LOG=$(ls -1t logs/02_annotate_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
      echo "  log: $LATEST_LOG"
      tail -5 "$LATEST_LOG" | sed 's/^/  | /'
    fi
    echo
  } >> logs/monitor.log

  sleep 7200  # 2 hours
done
