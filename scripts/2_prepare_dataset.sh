#!/bin/bash
# Step 2. Turns the videos in my-clone/footage/ into training clips, captions and the training settings file.
. "$(dirname "$0")/common.sh"; "$PY" "$KIT/scripts/prepare_dataset.py" "$KIT" "$@"
