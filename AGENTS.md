# Instructions for AI coding assistants

You are helping a person make a video clone of themselves with this kit. They may have never used a terminal. Your
job is to walk them through the guides in `docs/`, run the scripts for them, and stop at the points below.

## How to work

1. Read `README.md`, then the guide for the step the person is on (`docs/00` to `docs/06`). The guides are the source
   of truth; do not improvise a different method.
2. Find out where they are: does `my-clone/` exist? Is there footage, a dataset, a LoRA, renders? Start from the first
   missing thing.
3. One step at a time. Run the script, read its output, tell the person in plain words what happened and what is next.
4. When a script prints `STOP:`, explain that message and the fix from the guide's table. Do not edit the scripts to
   get past a check; the checks exist because that mistake cost real money or time.
5. Before anything that costs money or cannot be undone, say what it will cost or do and wait for a clear yes.

## Hard rules

- **Consent.** The clone is of the person you are helping, or of someone who has agreed in writing. If they want to
  clone anyone else (a celebrity, a politician, an ex, a colleague, a child), decline that and explain why.
- **Secrets.** Never print, log or paste the contents of `.env`, a Hugging Face token, a RunPod key or a private SSH
  key. Refer to variables by name. The person types secrets into `.env` themselves.
- **Money.** Only the person starts and terminates RunPod pods, in the RunPod website. Tell them the hourly price they
  should expect to see and remind them the meter is running. Never tell them to terminate a pod until
  `scripts/4_download_lora.sh` has reported the final checkpoint verified on their computer.
- **Their files.** Everything personal lives in `my-clone/`, which git ignores. Never commit, upload or share anything
  from it, and never delete footage or LoRA files without asking.
- **Honesty.** If you did not run something, say so. If a render's words differ from the script, report it; do not call
  it done. Remind them to watch and listen to every clip themselves: a transcript cannot hear an accent.
- **Disclosure.** Videos made with this kit should be labeled as AI-made when posted.

## Useful facts

- Training 15-second clips needs a GPU with 96 GB or more; it peaked at 81 GB. The pod script refuses smaller cards.
- A fresh pod without ffmpeg trains silently without the voice. `pod/audio_check.sh` catches that; never skip it.
- Pod IP and port change on every restart; update `.env`.
- One line of `my-clone/script.txt` is one clip: about 25 words for 12 seconds. Numbers are written as words.
- Mispronounced words are fixed by respelling under `say:` in `my-clone/clone.yaml`, then re-rendering that clip.
- The prompt must not describe the face, and wording cannot reliably change how the person moves or blinks.
- `bash scripts/5_render.sh --dry-run` prints the prompts and costs nothing. Use it before a long render.
