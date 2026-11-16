#!/bin/bash
# Step 5. Renders one clip per line of my-clone/script.txt on your Mac, and checks the spoken words of each clip.
. "$(dirname "$0")/common.sh"; "$PY" "$KIT/scripts/render.py" "$KIT" "$@"
