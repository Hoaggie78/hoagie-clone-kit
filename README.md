# Hoagie Clone Kit

Make a video clone of yourself: a model that looks and sounds like you and says whatever you type. You record
yourself once, train a small add-on model (a LoRA) on a rented GPU, and then render new talking-head videos on your
own Mac for no per-video fee.

This is the method behind the HoagieAI avatar, with everything specific to that channel removed. It contains scripts
and step-by-step guides. It does **not** contain anyone's face, voice, footage or model files.

> **Clone yourself, or someone who has agreed in writing. Label what you make as AI.** See `docs/00-before-you-start.md`.

## What you end up with

A finished vertical video of you talking, on a background you choose, with captions, made from a text file.

## The six steps

| | Step | Guide | Where it runs | Time |
|---|---|---|---|---|
| 0 | Accounts, costs, the rules | `docs/00-before-you-start.md` | browser | 15 min |
| 1 | Record yourself | `docs/01-record-yourself.md` | your phone | 30 min |
| 2 | Make the dataset | `docs/02-make-the-dataset.md` | your Mac | 30 min |
| 3 | Train the LoRA on RunPod | `docs/03-train-on-runpod.md` | rented GPU | about 5.5 hours, about $45 for us |
| 4 | Render clips | `docs/04-render.md` | your Mac | 27 min per 12-second clip |
| 5 | Put yourself on a background | `docs/05-matting.md` | your Mac | 3 min per clip |
| 6 | Join, caption, speed | `docs/06-finish.md` | your Mac | 1 min |

## Quick start

    git clone https://github.com/Hoaggie78/hoagie-clone-kit.git
    cd hoagie-clone-kit
    bash scripts/1_setup.sh

Then open `docs/00-before-you-start.md` and go in order. Every script tells you what to do next and stops with a plain
message when something is wrong.

**Using an AI coding assistant?** Open this folder in your editor and say: *"Read AGENTS.md and help me make my clone."*
It works with any assistant that can read files and run commands.

## What you need

- An Apple Silicon Mac with 64 GB of memory (tested on an M1 Max) and about 100 GB of free disk
- A phone, a plain backdrop and two lamps
- A RunPod account with credit, and a free Hugging Face account
- `ffmpeg` and Python 3.11 or newer (`brew install ffmpeg python`)

## What is in here

    docs/                  the guides, in order
    scripts/1_setup.sh           check your computer, make my-clone/
    scripts/2_prepare_dataset.sh cut clips, write captions and training settings
    scripts/3_train.sh           upload to your pod and start training      (3_watch.sh shows progress)
    scripts/4_download_lora.sh   bring the LoRA home and verify it
    scripts/5_render.sh          render my-clone/script.txt, check the words
    scripts/6_matte.py           cut out the person, add a background
    scripts/7_finish.py          trim, join, caption, speed
    pod/                   what runs on the rented GPU
    clone.example.yaml     the settings for your clone
    my-clone/              YOUR footage, dataset, LoRA and videos (created by setup; never committed to git)

## What was tested, and what was not

Honest status as of November 2026:

- **Tested for this kit:** the matting script and the join/caption/speed script, on real 12-second renders; the prompt
  builder; the pieces the training and render scripts are made from.
- **Taken from our own working runs, but not re-run end to end from this repository:** dataset preparation, the
  RunPod training flow (same trainer version, commands, settings and fixes as the run that produced our clone:
  37 clips of 15 seconds, 2,000 steps, 5 h 7 min, 81 GB peak on a B200), and the Mac render command.
- **Not tested:** 8-second clips with this kit, rendering on a rented GPU, Macs with less than 64 GB, Windows and Linux
  for the local steps.

If a step fails for you, the error message and the troubleshooting table in that step's guide are the place to start.
Fixes are welcome.

## Models and licences

The kit downloads nothing by itself except Python packages and the Whisper speech model. You download the rest and
accept each licence yourself:

- LTX-2.5 by Lightricks (video and voice model, and its trainer)
- ltx-2-mlx by dgrauet (the Mac port used for rendering)
- Whisper by OpenAI, through mlx-whisper (word checking and captions)
- Background Matting v2 by Peter Lin and others (cutout)

The scripts and guides here are under the MIT licence (`LICENSE`).
