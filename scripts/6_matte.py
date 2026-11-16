"""Step 6. Cuts the person out of a grey-backdrop render and puts them on a background image of your choice.
Uses Background Matting v2 (ONNX, runs on the CPU). It needs two things: the render, and a picture of the EMPTY backdrop.
This script builds the empty-backdrop picture from the render itself, which works when the backdrop is plain and evenly lit.
usage: .venv/bin/python scripts/6_matte.py RENDER.mp4 BACKGROUND.jpg OUT.mp4 [--model models/bgmv2.onnx]"""
import subprocess, sys
from pathlib import Path
import av, cv2, numpy as np, onnxruntime as ort
from PIL import Image

src, bg_path, out = sys.argv[1:4]
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else str(Path(__file__).resolve().parent.parent / "models/bgmv2.onnx")
if not Path(model).exists(): sys.exit(f"\nSTOP: matting model not found at {model}. See docs/05-matting.md, step 1.\n")
c = av.open(src); fps = float(c.streams.video[0].average_rate); frames = [f.to_ndarray(format="rgb24") for f in c.decode(video=0)]; c.close()
h, w, _ = frames[0].shape
# --- empty backdrop ("clean plate"): find the person in a middle frame, paint the backdrop back in over them
f0 = frames[len(frames) // 2].astype(np.float32)
L = np.stack([np.convolve(np.median(f0[:, 4:40], 1)[:, k], np.ones(61) / 61, "same") for k in range(3)], 1)
R = np.stack([np.convolve(np.median(f0[:, -40:-4], 1)[:, k], np.ones(61) / 61, "same") for k in range(3)], 1)
L[:30], L[-30:], R[:30], R[-30:] = L[30], L[-31], R[30], R[-31]                       # the running average is wrong at the very top and bottom
for E in (L, R):                                                                       # where an arm touches the frame edge, the edge is not backdrop:
    ref = np.median(E[: int(h * 0.4)], 0); bad = np.abs(E - ref).sum(1) > 40          # carry the last good backdrop row down past it
    for y in range(1, h):
        if bad[y]: E[y] = E[y - 1]
t = np.linspace(0, 1, w)[None, :, None]; model_bg = L[:, None, :] * (1 - t) + R[:, None, :] * t   # backdrop guess: blend of the left and right edges, row by row
person = (np.abs(f0 - model_bg).sum(-1) > 45).astype(np.uint8)
person = cv2.dilate(cv2.morphologyEx(cv2.morphologyEx(person, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), cv2.MORPH_CLOSE, np.ones((35, 35), np.uint8)), np.ones((41, 41), np.uint8))
if person.mean() > 0.85: sys.exit("\nSTOP: could not tell the person from the backdrop. Matting needs a plain, evenly lit backdrop with some of it visible on both sides (docs/05).\n")
soft = cv2.GaussianBlur(person.astype(np.float32), (0, 0), 6)[..., None]
plate = model_bg * soft + f0 * (1 - soft)          # modelled backdrop under the person, real backdrop pixels everywhere else
Image.fromarray(plate.astype(np.uint8)).save(str(Path(out).with_suffix("")) + "_cleanplate.png")
b = (plate / 255).transpose(2, 0, 1)[None].astype(np.float32)
bg = np.asarray(Image.open(bg_path).convert("RGB").resize((w, h), Image.LANCZOS), np.float32) / 255
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?",
                       "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", out], stdin=subprocess.PIPE)
prev = None
for i, f in enumerate(frames):
    s = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    pha, fgr = sess.run(["pha", "fgr"], {"src": s, "bgr": b})[:2]; a = pha[0, 0][..., None]; fg = fgr[0].transpose(1, 2, 0)
    if prev is not None: a = np.where(np.abs(a - prev) < 0.08, 0.5 * a + 0.5 * prev, a)     # calm single-frame flicker at the edges
    prev = a
    ff.stdin.write((np.clip(fg * a + bg * (1 - a), 0, 1) * 255).astype(np.uint8).tobytes())
    if i % 50 == 0: print(f"frame {i}/{len(frames)}", flush=True)
ff.stdin.close(); ff.wait(); print("wrote", out)
