#!/bin/bash
# Shows where training is. Safe to run as often as you like.
. "$(dirname "$0")/common.sh"
pod 'cat /workspace/out/STATUS.txt 2>/dev/null; echo "---"; tr "\r" "\n" < /workspace/out/train.log 2>/dev/null | grep -a "Training [0-9]*/" | tail -1 | cut -c1-110; echo "GPU memory: $(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader)"; pgrep -f "train_on_pod.sh|train.py" >/dev/null && echo "state: RUNNING" || echo "state: NOT RUNNING (finished or stopped; read the lines above)"; ls /workspace/out/checkpoints 2>/dev/null | tail -3'
