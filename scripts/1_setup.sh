#!/bin/bash
# Step 1. Checks your computer and creates your private my-clone/ folder. Run it again any time; it only adds what is missing.
KIT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$KIT"; ok=1
say() { printf "%-34s %s\n" "$1" "$2"; }
[ "$(uname -s)" = Darwin ] && [ "$(uname -m)" = arm64 ] && say "Apple Silicon Mac" "yes" || { say "Apple Silicon Mac" "NO - dataset prep and training still work; rendering in step 5 needs one (docs/04)"; }
MEM=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1073741824 )); say "Memory" "${MEM} GB $([ $MEM -ge 64 ] && echo '(enough to render)' || echo '(rendering was tested with 64 GB; less may not work)')"
command -v ffmpeg >/dev/null && say "ffmpeg" "found" || { say "ffmpeg" "MISSING - install with: brew install ffmpeg"; ok=0; }
command -v python3 >/dev/null && say "python3" "$(python3 -V 2>&1)" || { say "python3" "MISSING - install Python 3.11 or newer"; ok=0; }
command -v ssh >/dev/null && say "ssh" "found" || { say "ssh" "MISSING"; ok=0; }
[ -f ~/.ssh/id_ed25519.pub ] && say "SSH key for RunPod" "found (~/.ssh/id_ed25519.pub)" || say "SSH key for RunPod" "not yet - docs/03 step 2 makes one"
say "Free disk" "$(df -h "$KIT" | tail -1 | awk '{print $4}') (rendering needs about 80 GB for model files)"
[ $ok = 1 ] || { echo; echo "Fix the MISSING items above, then run this again."; exit 1; }
[ -d .venv ] || { echo "creating .venv (a private Python for this kit)..."; python3 -m venv .venv; }
.venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q pyyaml numpy pillow av onnxruntime opencv-python "mlx-whisper; platform_machine=='arm64'" || { echo "STOP: installing Python packages failed"; exit 1; }
mkdir -p my-clone/footage my-clone/dataset my-clone/lora my-clone/renders my-clone/backgrounds
[ -f my-clone/clone.yaml ] || cp clone.example.yaml my-clone/clone.yaml
[ -f .env ] || cp .env.example .env
echo; echo "Setup is fine. Next:"; echo "  1. Open my-clone/clone.yaml and set your trigger word and description."; echo "  2. Record your footage (docs/01-record-yourself.md) and put the files in my-clone/footage/"; echo "  3. Run: bash scripts/2_prepare_dataset.sh"
