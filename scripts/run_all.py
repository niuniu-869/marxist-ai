#!/usr/bin/env python3
"""
run_all.py —— 串行驱动整个管线

01_harvest → 01b_split → 01d_segment → 02a_meta → 02_annotate → 03_merge

每阶段独立断点续跑，失败不阻塞下一阶段。
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
LOGS = ROOT / "logs"


def run(cmd: list[str], stage: str) -> int:
    LOGS.mkdir(exist_ok=True)
    log_path = LOGS / f"{stage}_{datetime.now():%Y%m%d_%H%M%S}.log"
    print(f"\n{'='*60}\n[{datetime.now():%H:%M:%S}] STAGE: {stage}\n{'='*60}")
    print(f"  cmd: {' '.join(cmd)}")
    print(f"  log: {log_path}")
    t0 = time.time()
    with open(log_path, "w") as lf:
        proc = subprocess.run(
            cmd, cwd=str(ROOT),
            stdout=lf, stderr=subprocess.STDOUT,
            env=os.environ.copy(),
        )
    dt = time.time() - t0
    print(f"  done in {dt:.1f}s, exit={proc.returncode}")
    return proc.returncode


def main():
    # 默认全跑；用 STAGE 环境变量限制
    stages_env = os.environ.get("STAGE", "harvest,split,segment,meta,annotate,merge")
    stages = set(s.strip() for s in stages_env.split(","))

    py = sys.executable

    if "harvest" in stages:
        run([py, str(SCRIPTS / "01_harvest.py")], "01_harvest")
    if "split" in stages:
        run([py, str(SCRIPTS / "01b_split.py")], "01b_split")
    if "segment" in stages:
        run([py, str(SCRIPTS / "01d_segment.py")], "01d_segment")
    if "meta" in stages:
        run([py, str(SCRIPTS / "02a_meta.py")], "02a_meta")
    if "annotate" in stages:
        run([py, str(SCRIPTS / "02_annotate.py")], "02_annotate")
    if "merge" in stages:
        run([py, str(SCRIPTS / "03_merge.py")], "03_merge")


if __name__ == "__main__":
    main()
