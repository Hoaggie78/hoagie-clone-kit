#!/bin/bash
# Runs ON THE POD, started for you by scripts/3_train.sh. One command does everything:
#   setup -> audio check -> preprocess -> train. Safe to run again: finished stages are skipped.
# Progress:  tail -f /workspace/out/STATUS.txt       Full training log: /workspace/out/train.log
OUT=/workspace/out; DS=/root/dataset; mkdir -p $OUT; say() { echo "$(date +%H:%M) $*" | tee -a $OUT/STATUS.txt; }
TRIGGER=$(cat $DS/trigger.txt); N=$(ls $DS/*.mp4 | wc -l | tr -d ' '); FR=$(cat $DS/frames.txt)
GPU=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1); MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
say "pod GPU: $GPU | clips: $N | frames per clip: $FR | trigger: $TRIGGER"
if [ "$FR" -ge 449 ] && [ "$MEM" -lt 90000 ]; then say "STOP: 15-second clips peaked at 81 GB in our run. This GPU has $((MEM/1024)) GB and will run out of memory. Use a GPU with 96 GB or more (see docs/03)."; exit 1; fi
if ! grep -q SETUP_COMPLETE /root/setup.log 2>/dev/null; then say "1/4 installing the trainer and downloading models (about 7 minutes)"; bash /root/kit/setup_pod.sh; fi
grep -q SETUP_COMPLETE /root/setup.log || { say "STOP: setup failed. Usual cause: the Hugging Face token is wrong, or the LTX-2.5 licence is not accepted on that account. Last lines:"; tail -5 /root/setup.log | tee -a $OUT/STATUS.txt; exit 1; }
say "2/4 checking that audio can be read"; bash /root/kit/audio_check.sh > $OUT/audio_check.log 2>&1
grep -q AUDIO_OK $OUT/audio_check.log || { say "STOP: audio cannot be read, so the voice would not be trained. See $OUT/audio_check.log"; exit 1; }
M=/root/models25; cd /root/LTX-2/packages/ltx-trainer
if [ "$(ls $DS/.precomputed/latents 2>/dev/null | wc -l)" != "$N" ] || [ "$(ls $DS/.precomputed/audio_latents 2>/dev/null | wc -l)" != "$N" ]; then
  say "3/4 preprocessing $N clips (about 1 minute per clip)"
  /root/ltx-venv/bin/python scripts/process_dataset.py $DS/dataset.json --resolution-buckets "544x960x$FR" \
    --model-path $M/diffusion_models/ltx-2.5-22b-dev-transformer-bf16.safetensors --text-encoder-path $M/text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors \
    --video-vae-path $M/vae/ltx-2.5-video-vae-bf16.safetensors --audio-vae-path $M/vae/ltx-2.5-audio-vae-bf16.safetensors --lora-trigger "$TRIGGER" > $OUT/preprocess.log 2>&1
fi
v=$(ls $DS/.precomputed/latents 2>/dev/null | wc -l | tr -d ' '); a=$(ls $DS/.precomputed/audio_latents 2>/dev/null | wc -l | tr -d ' ')
[ "$v" = "$N" ] && [ "$a" = "$N" ] || { say "STOP: preprocessing made $v video and $a audio files, expected $N of each. See $OUT/preprocess.log"; exit 1; }
say "4/4 training started. 2000 steps. Our run took 5 hours on a B200. A checkpoint is saved every 250 steps in $OUT/checkpoints"
/root/ltx-venv/bin/python scripts/train.py /root/dataset/train.yaml > $OUT/train.log 2>&1
if grep -aq "Training Statistics" $OUT/train.log; then say "TRAINING_DONE $(grep -a 'Total time' $OUT/train.log | tail -1 | tr -s ' ')"; say "Now download the checkpoints BEFORE stopping the pod: scripts/4_download_lora.sh"
else say "TRAINING_FAILED. Last error lines:"; tr '\r' '\n' < $OUT/train.log | grep -aiE "error|out of memory|Traceback" | tail -5 | tee -a $OUT/STATUS.txt; fi
