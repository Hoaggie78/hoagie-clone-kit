# 6. Join the clips into a video

    .venv/bin/python scripts/7_finish.py my-clone/final.mp4 my-clone/renders/01_office.mp4 my-clone/renders/02_office.mp4 \
        --captions --script my-clone/script.txt --speed 1.1

What it does:

- **Trims each clip to the speech.** The model leaves a pause, often with a closed-mouth smile, after each line. The
  script cuts from just before your first sound to just after your last, so the clips cut together like one take.
- **Joins without the sound drifting.** Simply gluing clips together lets the voice slide ahead of the lips a little
  with every clip. The script cuts the audio to exactly match each clip's picture.
- **`--captions`** adds simple captions, three words at a time. With `--script` they use your spelling whenever the
  number of words heard matches your line.
- **`--speed 1.1`** plays the result 10 % faster. AI clips are a little slow; 1.1 sounded natural to us and 1.2 was the most we liked.

Watch the finished video all the way through, with sound, before you post it. Label it as AI-made.

## Things we learned the hard way

- One idea per clip. Short lines survive the word check; long ones lose words.
- The same start frame for every clip is what keeps the person consistent.
- Prompt wording cannot reliably change how someone moves or blinks, and winks or big gestures on request usually fail.
  The LoRA copies the habits in the footage. If you want calmer delivery, record calmer footage.
- Hands are the weakest part. Framing the final video from the chest up hides them.
- Test a hard word in one clip before rendering twenty.
