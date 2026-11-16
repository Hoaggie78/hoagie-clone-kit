#!/bin/bash
# Step 3. Sends your dataset to the RunPod pod and starts training there. Run it again if it stops: finished stages are skipped.
. "$(dirname "$0")/common.sh"; DS="$ME/dataset"
[ -f "$DS/dataset.json" ] || die "no dataset yet. Run: bash scripts/2_prepare_dataset.sh"
[ -n "$HF_TOKEN" ] || die "HF_TOKEN is empty in .env (docs/00-before-you-start.md, step 3)."
echo "Connecting to the pod..."; pod true || die "cannot reach the pod. Is it running? Are POD_IP and POD_PORT in .env the ones shown under Connect -> SSH over exposed TCP? Is your SSH key added in RunPod settings? (docs/03, steps 2 and 5)"
echo "Pod GPU: $(pod 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader')"
printf 'HF_TOKEN=%s\n' "$HF_TOKEN" | pod 'umask 077; cat > /root/.hf_env; mkdir -p /root/dataset /root/kit /workspace/out'
echo "Uploading the dataset and scripts (a few minutes)..."
( cd "$DS" && COPYFILE_DISABLE=1 tar -cf - dataset.json train.yaml trigger.txt frames.txt val_first_frame.png clip_*.mp4 clip_*.wav ) | pod 'tar -xf - -C /root/dataset'
( cd "$KIT/pod" && COPYFILE_DISABLE=1 tar -cf - *.sh ) | pod 'tar -xf - -C /root/kit && chmod +x /root/kit/*.sh'
n=$(pod 'ls /root/dataset/clip_*.mp4 | wc -l' | tr -d ' '); [ "$n" = "$(ls "$DS"/clip_*.mp4 | wc -l | tr -d ' ')" ] || die "upload incomplete ($n clips arrived). Run this script again."
pod 'pgrep -f train_on_pod.sh >/dev/null' && die "training is already running on the pod. Watch it with: bash scripts/3_watch.sh"
pod 'cd /root && setsid nohup bash /root/kit/train_on_pod.sh > /workspace/out/run.log 2>&1 < /dev/null &'
echo; echo "Training has started on the pod. It keeps running if you close this window or your laptop sleeps."
echo "Check on it any time:   bash scripts/3_watch.sh"; echo "When it says TRAINING_DONE: bash scripts/4_download_lora.sh   (BEFORE you stop the pod)"
