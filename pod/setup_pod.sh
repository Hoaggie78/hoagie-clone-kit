#!/bin/bash
# Runs ON THE POD (started by pod/train_on_pod.sh). Installs the LTX-2 trainer and downloads the LTX-2.5 training models.
# Versions are the ones this kit was tested with (October 2026). Takes about 7 minutes on a fast pod.
exec > /root/setup.log 2>&1
set -a; . /root/.hf_env; set +a
export PATH="$HOME/.local/bin:$PATH" UV_CACHE_DIR=/root/.uv-cache UV_PROJECT_ENVIRONMENT=/root/ltx-venv HF_HUB_ENABLE_HF_TRANSFER=1
apt-get update -qq >/dev/null 2>&1; DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg git curl >/dev/null 2>&1   # ffmpeg: without it the audio is silently skipped
pip install -q -U "huggingface_hub[hf_transfer]" >/dev/null 2>&1
python3 - <<'PY' &
import os
from huggingface_hub import hf_hub_download
for p in ["vae/ltx-2.5-video-vae-bf16.safetensors", "vae/ltx-2.5-audio-vae-bf16.safetensors",
          "text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors",
          "diffusion_models/ltx-2.5-22b-dev-transformer-bf16.safetensors"]:
    f = hf_hub_download("Lightricks/LTX-2.5", p, local_dir="/root/models25", token=os.environ["HF_TOKEN"]); print("DOWNLOADED", f, os.path.getsize(f), flush=True)
print("MODELS_DONE", flush=True)
PY
DL=$!
curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
cd /root && { [ -d LTX-2 ] || git clone -q https://github.com/Lightricks/LTX-2.git; } && cd LTX-2 && git checkout -q e98f6d9 && uv sync 2>&1 | tail -2
/root/ltx-venv/bin/python -c "import torch,ltx_pipelines;print('VENV_OK cuda',torch.cuda.is_available())"
wait $DL && echo SETUP_COMPLETE || echo SETUP_FAILED_MODEL_DOWNLOAD
