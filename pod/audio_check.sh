#!/bin/bash
# Runs ON THE POD. The trainer silently trains WITHOUT the voice when it cannot read audio files. This proves it can,
# and repairs the usual cause (a torchaudio that needs torchcodec + ffmpeg). Prints AUDIO_OK or AUDIO_FAIL.
export PATH="$HOME/.local/bin:$PATH"; PY=/root/ltx-venv/bin/python; WAV=$(ls /root/dataset/*.wav | head -1)
t() { $PY -c "import torchaudio,sys; w,sr=torchaudio.load(sys.argv[1]); print('loaded', tuple(w.shape), sr)" "$WAV" 2>&1 | tail -1; }
r=$(t); echo "audio test 1: $r"; case "$r" in loaded*) echo AUDIO_OK; exit 0;; esac
tv=$($PY -c 'import torch;print(".".join(torch.__version__.split("+")[0].split(".")[:2]))')
case "$tv" in 2.8) tc="==0.7.*";; 2.9) tc="==0.8.*";; 2.10) tc="==0.9.*";; *) tc="";; esac
uv pip install -q --python $PY "torchcodec$tc" 2>&1 | tail -1
r=$(t); echo "audio test 2: $r"; case "$r" in loaded*) echo AUDIO_OK;; *) echo AUDIO_FAIL;; esac
