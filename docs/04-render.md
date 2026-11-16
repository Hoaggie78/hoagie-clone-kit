# 4. Render a video on your Mac

Now the clone talks. Rendering runs on your Mac and costs nothing per video. Tested on an M1 Max with 64 GB:
about 27 minutes for one 12-second clip.

## Step 1. Install the renderer (once)

The kit uses the open-source MLX port of LTX-2 by dgrauet. In a terminal, somewhere outside the kit folder:

    git clone https://github.com/dgrauet/ltx-2-mlx.git
    cd ltx-2-mlx

Follow **that project's README** to install it (it creates a `.venv` folder containing the `ltx-2-mlx` command) and
to download the **LTX-2.5 q8** model into `weights/ltx-2.5-mlx-q8`. The download is about 70 GB. The kit was tested
with that project as of November 2026 (commit `747b30e`); if its commands have changed, its README wins.

Then open the kit's `.env` and set the folder, for example:

    LTX_MLX_DIR=/Users/you/ltx-2-mlx

## Step 2. Write what the clone says

Make the file `my-clone/script.txt`. **One line = one clip of about 12 seconds = about 25 words.**

    Hi, I'm an AI clone, and every second of this was made on a laptop.
    Here is how it works. I recorded myself talking, and a model learned my face and my voice.

Rules that save you re-renders:
- Write numbers as words: `sixty-four`, not `64`.
- Write the clone's lines the way a person talks. Never put quotation marks in a line.
- If a word comes out wrong, add a respelling under `say:` in `clone.yaml` (for example `LoRA: Laura`).

## Step 3. Look at the prompts (free)

    bash scripts/5_render.sh --dry-run

This prints the full prompt for each clip and renders nothing. The prompt describes the shot, the wardrobe and the
plain grey backdrop. It does **not** describe your face: the LoRA does that. Do not add face wording.

## Step 4. Render

    bash scripts/5_render.sh

For each line it renders a clip, listens to it with Whisper and compares the words with your line. If they differ it
tries up to two more times with a different seed. Results go to `my-clone/renders/01.mp4`, `02.mp4`, … with a
`.txt` beside each saying what was heard.

**Every clip starts from the same picture,** `my-clone/start_frame.png`, made from your first training clip. That keeps
you looking the same from clip to clip. Look at that picture closely once: a flaw in it appears in every clip.

## Step 5. Watch and listen

The word check cannot hear a wrong accent or an odd pronunciation, and it often writes `12` where you said `twelve`.
Play every clip. To redo one, delete its file and run step 4 again.

## Settings you can change

| Option | Default | Notes |
|---|---|---|
| `--strength 0.8` | 0.8 | How strongly the LoRA is applied. Try 0.7 to 1.0 if the likeness is weak or stiff. |
| `--lora FILE` | step 02000 | Try an earlier checkpoint (for example step 01500) if the last one looks overcooked. |
| `--seconds 12` | 12 | Longer clips take longer and use more memory. 12 was what we tested on the Mac. |
| `--only 3` | all | Render only clip 3. |

## No suitable Mac?

Rent a GPU and render with the official `ltx_pipelines` from the LTX-2 repository (the same code the training pod
installs), using the dev model, the distilled LoRA and your LoRA. We rendered that way before moving to the Mac, but
this kit does not include scripts for it.

Next: `docs/05-matting.md`
