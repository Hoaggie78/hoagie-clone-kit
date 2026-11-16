# 3. Train your LoRA on RunPod

A LoRA is a small file that teaches the video model what you look and sound like. Training it needs a very large
graphics card for a few hours, so you rent one. Follow the steps in order. **You pay for every minute the pod is
running, including while you read, so read this page to the end before step 3.**

RunPod changes its website from time to time. If a button is named a little differently, look for the same idea.

## Step 1. Check you are ready

- `my-clone/dataset/` has your clips, `dataset.json` and `train.yaml` (docs/02).
- `.env` has your `HF_TOKEN`, and you accepted the LTX-2.5 licence on Hugging Face (docs/00).
- Your RunPod account has credit.

## Step 2. Give RunPod your SSH key (once)

An SSH key lets your computer talk to the rented machine without a password.

1. In a terminal, see if you already have one:

       cat ~/.ssh/id_ed25519.pub

   If it prints a line starting with `ssh-ed25519`, copy that whole line. If it says "No such file", make one, pressing
   Enter at every question, then run the `cat` command again:

       ssh-keygen -t ed25519

2. On runpod.io, open **Settings**, find **SSH Public Keys**, paste the line, and save.

Only ever share the file ending in `.pub`. The other file, without `.pub`, is private.

## Step 3. Start the pod

1. On runpod.io choose **Pods**, then **Deploy**.
2. **GPU:** pick one with **96 GB of memory or more** (in October 2026 that meant a B200, 180 GB, at $7.99/hour).
   Training on 15-second clips peaked at 81 GB in our run, so an 80 GB card (H100, A100) **runs out of memory**.
   The training script checks this and stops before you waste money.
3. **Template:** a "RunPod PyTorch" template (Ubuntu with CUDA). The kit installs everything else.
4. **Disk:** set **Container Disk to 150 GB** and **Volume Disk to 50 GB**. The model files are large; the default is too small.
5. Make sure **SSH** (TCP port 22) is enabled, choose **On-Demand** (not Spot or Interruptible, which can be taken
   away mid-training), and deploy.
6. Wait until the pod says **Running**.

## Step 4. Find the pod's address

1. Click **Connect** on the pod.
2. Find **SSH over exposed TCP**. It shows a command like `ssh root@203.0.113.7 -p 12345 -i ~/.ssh/id_ed25519`.
3. The first number is the IP, the number after `-p` is the port.

## Step 5. Put the address in `.env`

Open `.env` in the kit folder and fill in, using your own numbers:

    POD_IP=203.0.113.7
    POD_PORT=12345

These change every time a pod is stopped and started. Update them if you restart.

## Step 6. Start training

    bash scripts/3_train.sh

It uploads your dataset, then starts everything on the pod: install (about 7 minutes), an audio check, preprocessing
(about a minute per clip), and training (2,000 steps). **Training keeps running if you close the terminal or your
laptop sleeps.** Our run with 37 clips took 5 hours 7 minutes of training.

## Step 7. Watch it

    bash scripts/3_watch.sh

Run it whenever you like. You will see lines such as `4/4 training started` and then a step counter. Good signs:

- within 20 minutes: `3/4 preprocessing`
- within 45 minutes: a step counter that goes up
- every 250 steps: a new file listed under checkpoints, and a short test video

To see the test videos while it trains, run `bash scripts/4_download_lora.sh` and look in `my-clone/lora/samples/`.
By step 1000 the test video should clearly be you, speaking the test sentence in your voice.

## Step 8. Download your LoRA

When `3_watch.sh` shows **TRAINING_DONE**:

    bash scripts/4_download_lora.sh

It copies every checkpoint to `my-clone/lora/` and checks each copy is complete. Wait until it says the final file
(step 02000) is safely on your computer.

## Step 9. Stop paying

**Only after step 8 succeeds:** on runpod.io, click the pod's menu and choose **Terminate** (deletes it and its disk).
**Stop** alone still charges a smaller amount for the stored disk. Check the Pods page shows nothing running.

Back up `my-clone/lora/` somewhere safe. That file is your clone; it cannot be downloaded again.

## If something goes wrong

**Do not terminate the pod over a fixable error.** You would pay again for setup, and a good GPU may not be free when
you come back. Read the message first.

| What you see | What it means | What to do |
|---|---|---|
| `cannot reach the pod` | Wrong IP or port, pod not running, or SSH key not added | Recheck steps 2, 4 and 5 |
| `STOP: setup failed` with 401 or 403 | Token wrong, or licence not accepted on that account | Fix `.env`, accept the licence, run `3_train.sh` again |
| `STOP: This GPU has 80 GB` | Card too small for 15-second clips | Terminate it and deploy a 96 GB+ card |
| `STOP: audio cannot be read` | The voice would not be trained | Send `/workspace/out/audio_check.log` to whoever is helping you |
| `STOP: preprocessing made N video and M audio files` | Some clips failed | Look at `/workspace/out/preprocess.log` on the pod |
| `TRAINING_FAILED ... out of memory` | Card too small | Use a larger card |
| No pod with enough memory is available | RunPod is busy | Try another region or try again later |

Running `bash scripts/3_train.sh` again is always safe: finished stages are skipped.

**Smaller card?** `bash scripts/2_prepare_dataset.sh --seconds 8` makes 8-second clips, which need less memory.
An earlier version of our clone was trained on shorter clips, but that path was **not tested with this kit**.

Next: `docs/04-render.md`
