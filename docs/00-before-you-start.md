# 0. Before you start

Read this page once. It takes five minutes and saves you money.

## The rule

Clone **yourself**, or someone who has agreed **in writing**. Say in every post that the video is AI-made. Never use a
clone to make it look as if a real person said something they did not say. The platforms also ask for an "AI-generated"
label when you upload; tick it.

## What you need

| Thing | Why | Cost |
|---|---|---|
| A phone that films video | To record yourself | You have it |
| A plain backdrop and two lamps | The model learns you best against a plain wall | A grey sheet works |
| An Apple Silicon Mac, 64 GB memory | To render videos at home. This is what the kit was tested on (M1 Max). | You have it, or see "No Mac?" below |
| About 100 GB of free disk | Model files are large | |
| A RunPod account with credit | To rent a big graphics card for a few hours to train | See below |
| A Hugging Face account | To download the LTX-2.5 model | Free |

**No Mac, or less memory?** Steps 1 to 4 (record, dataset, train) still work; the dataset step uses a Mac-only speech
tool, so do it on any Apple Silicon Mac. For rendering you can rent a GPU instead; that route is described briefly in
`docs/04-render.md` and was not tested as part of this kit.

## What it cost us (October 2026, your prices will differ)

- **Training:** one rented GPU for about 5.5 hours. Ours was a 180 GB card at **$7.99 per hour, so about $45**.
  Check today's price on RunPod before you start; it changes.
- **Rendering:** nothing per video. One 12-second clip took **about 27 minutes** on an M1 Max with 64 GB.
- **Everything else:** free software.

## Set up your three accounts (do this now)

1. **RunPod:** make an account at runpod.io and add credit. $60 covers one training run with room for a mistake.
2. **Hugging Face:** make an account at huggingface.co.
3. **Accept the model licence and make a token:**
   - Open the model page `Lightricks/LTX-2.5` on Hugging Face while signed in. Read the licence and click to accept it.
     You are responsible for following it, including its rules on commercial use.
   - Do the same on `dgrauet/ltx-2.5-mlx-q8` (the Mac version used for rendering).
   - In your Hugging Face settings, open **Access Tokens**, create a token with **Read** access, and copy it.
   - You will paste it into the file `.env` in step 1. **Never** paste a token into a chat, a post, or a file you share.

## How long it takes

| Step | Your time | Waiting time |
|---|---|---|
| Record | 30 minutes | |
| Dataset | 10 minutes | 20 minutes |
| Train on RunPod | 20 minutes | about 5.5 hours |
| First render | 10 minutes | 27 minutes per 12-second clip |

Next: `docs/01-record-yourself.md`
