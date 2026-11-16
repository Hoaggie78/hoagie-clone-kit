# 5. Put yourself on a background (matting)

Your clips show you on a grey backdrop. Matting cuts you out so you can stand in front of any picture: an office, a
studio, a brand colour. It is optional; a plain backdrop is a perfectly good look.

## Why render on grey first

You could ask the model for an office in the prompt, but the room would change a little in every clip. Rendering on a
plain backdrop and adding **one** background picture afterwards gives every clip exactly the same background.

## Step 1. Get the matting model (once)

The kit uses **Background Matting v2** (BackgroundMattingV2 by Peter Lin and others, MIT licence).

1. Open the project page: `github.com/PeterL1n/BackgroundMattingV2`.
2. Follow its **Download** link to the model files and get an **ONNX** model with the **MobileNetV2** backbone,
   **HD** version (about 20 MB).
3. Save it in the kit as `models/bgmv2.onnx`.

File names on that page may differ from ours; any ONNX file from that project with inputs named `src` and `bgr` works.

## Step 2. Choose a background picture

Any JPG or PNG, upright (portrait), at least 1024 × 1792. Put it in `my-clone/backgrounds/`. Use a picture you own,
made yourself, or are licensed to use. A slightly out-of-focus, darker background makes the person stand out.

## Step 3. Cut out and place

    .venv/bin/python scripts/6_matte.py my-clone/renders/01.mp4 my-clone/backgrounds/office.jpg my-clone/renders/01_office.mp4

About 3 minutes per 12-second clip on the CPU. It also saves `01_office_cleanplate.png`, its guess at your empty
backdrop. Repeat for each clip (or ask your AI assistant to loop over them).

## How it works, so you can fix problems

The model compares each frame with a picture of the **empty backdrop** and keeps whatever differs. You never filmed an
empty backdrop for these AI-made clips, so the script builds one: it reads the backdrop colour down the left and right
edges of the frame and fills in the area behind you.

| Problem | Cause | Fix |
|---|---|---|
| Halo or grey patches beside the arms | Arms touch the frame edge, so the edges are not all backdrop | Keep "backdrop visible on both sides" in the shot; a start frame with space around the arms |
| Parts of the clothing go see-through | Clothing colour too close to the backdrop | Use a wardrobe that contrasts (dark top on mid-grey) in `render_wardrobe` |
| Flicker at the hair | Fine hair against uneven backdrop | Even lighting in the training footage; a slightly blurred background hides it |
| `could not tell the person from the backdrop` | Backdrop is not plain in the render | Check the prompt still asks for a plain grey backdrop |

A cutout will never be perfect on every frame. Check the result at full size before you publish.

Next: `docs/06-finish.md`
