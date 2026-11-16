#!/bin/bash
# Step 4. Copies the trained LoRA files and the test videos from the pod to my-clone/lora/, and proves each copy is complete.
# Run it BEFORE you stop or delete the pod. You can also run it during training to look at the test videos so far.
. "$(dirname "$0")/common.sh"; L="$ME/lora"; mkdir -p "$L/samples"; got=0
for f in $(pod 'ls /workspace/out/checkpoints/lora_weights_step_*.safetensors 2>/dev/null' | xargs -n1 basename 2>/dev/null); do
  [ -f "$L/$f" ] && { got=$((got+1)); continue; }
  for i in 1 2 3; do scp -q -o StrictHostKeyChecking=no -P "$POD_PORT" root@"$POD_IP":/workspace/out/checkpoints/$f "$L/.part_$f"
    r=$(pod "md5sum /workspace/out/checkpoints/$f" | cut -d' ' -f1); l=$(md5 -q "$L/.part_$f" 2>/dev/null || md5sum "$L/.part_$f" | cut -d' ' -f1)
    [ -n "$r" ] && [ "$r" = "$l" ] && { mv -f "$L/.part_$f" "$L/$f"; echo "verified: $f"; got=$((got+1)); break; }; sleep 5; done
done
scp -q -r -o StrictHostKeyChecking=no -P "$POD_PORT" root@"$POD_IP":/workspace/out/samples/. "$L/samples/" 2>/dev/null
echo; echo "$got checkpoint file(s) verified in my-clone/lora/. Test videos from training are in my-clone/lora/samples/."
if pod 'grep -q TRAINING_DONE /workspace/out/STATUS.txt' && [ -f "$L/lora_weights_step_02000.safetensors" ]; then
  echo "Training is finished and the final file (step 02000) is safely on your computer."; echo "NOW STOP THE POD in the RunPod website, or it keeps charging you. (docs/03, step 9)"
else echo "Training is not finished yet (or the final file has not arrived). Do NOT stop the pod. Check: bash scripts/3_watch.sh"; fi
