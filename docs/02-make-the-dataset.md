# 2. Make the dataset

This turns your recordings into the short labeled clips the trainer needs. Everything happens on your computer.

## Do this

1. In a terminal, in the kit folder, run:

       bash scripts/1_setup.sh

   It checks your computer and makes your private folder `my-clone/`. Fix anything it marks MISSING and run it again.

2. Open `my-clone/clone.yaml` in your editor. Change:
   - `trigger`: one made-up word, lower case, no spaces. For example your first name plus `clone`.
   - `person`: a short plain description, such as `a woman with shoulder-length dark hair`.
   - `training_wardrobe`: what you wore in the footage.
   Leave the rest for now.

3. Open `.env` and paste your Hugging Face token after `HF_TOKEN=`.

4. Make sure your recordings are in `my-clone/footage/`, then run:

       bash scripts/2_prepare_dataset.sh

   It listens to your footage, finds stretches of steady talking, cuts 15-second clips that start on a sentence, and
   writes a caption for each one containing the exact words you say. About 20 minutes for 30 minutes of footage.

## Check the result (do not skip)

- Open `my-clone/dataset/CONTACT_SHEET.jpg`. Every tile should show you, framed the same way, on the plain backdrop.
- Open `my-clone/dataset/dataset.json` and read three captions while playing those clips. The quoted words should be
  what you say. Small spelling differences in names are fine.
- Delete nothing by hand. If a take is bad, remove that file from `my-clone/footage/` and run the script again.

## If it stops

| Message | What to do |
|---|---|
| only N usable clips were found | Record more steady talking (docs/01). |
| is HDR and could not be converted | Turn HDR Video off on the phone and record again. |
| set your own 'trigger' | Edit `my-clone/clone.yaml`. |

Next: `docs/03-train-on-runpod.md`
