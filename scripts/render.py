"""Renders my-clone/script.txt: one clip per line (keep each line to about 25 words = 12 seconds).
Each clip is checked with Whisper against the line; on a mismatch the next seed is tried (3 seeds), and the result is
reported honestly. Output: my-clone/renders/NN.mp4 (+ NN.txt = what was heard).
usage: render.py KIT_DIR [--dry-run] [--only N] [--seconds 12] [--lora FILE] [--strength 0.8]"""
import os, re, subprocess, sys, time
from pathlib import Path
import yaml

KIT = Path(sys.argv[1]); ME = KIT / "my-clone"; OUT = ME / "renders"; OUT.mkdir(exist_ok=True)
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
stop = lambda m: sys.exit("\nSTOP: " + m + "\n")
C = yaml.safe_load(open(ME / "clone.yaml")); DRY = "--dry-run" in sys.argv
SECONDS = arg("--seconds", 12); FRAMES = SECONDS * 25 // 8 * 8 + 1   # 8n+1 frames: 297 for 12 s
script = ME / "script.txt"
if not script.exists(): stop("write what your clone should say in my-clone/script.txt, one clip per line (about 25 words per line).")
lines = [l.strip() for l in script.read_text().splitlines() if l.strip() and not l.startswith("#")]
for n, l in enumerate(lines, 1):
    if '"' in l: stop(f"line {n} contains a double quote. Remove it: the clone should never say the word 'quote'.")
    if len(l.split()) > SECONDS * 2.4: stop(f"line {n} has {len(l.split())} words; about {int(SECONDS * 2.2)} fit in {SECONDS} seconds. Split it into two lines.")
def prompt(line):
    said = line
    for k, v in (C.get("say") or {}).items(): said = said.replace(k, v)
    return (f"{C['trigger']}, In a locked-off tripod shot with a completely fixed camera, no zoom, no push-in, a static medium shot framed from the waist up "
            f"and centred, with plain backdrop visible on both sides of the arms and shoulders, {C['person']}, wearing {C['render_wardrobe']}, stands in front of a "
            f"completely plain, smooth, seamless mid-grey studio backdrop, one even, flat, evenly lit grey surface filling the whole frame, no room, no furniture, "
            f"no objects, no shadows on the backdrop. Soft, even studio lighting. Looking directly into the camera, the person speaks {C.get('accent', '')}: "
            f"{C['render_tone']}, saying, \"{said}\" After the last word the face stays relaxed and neutral. There is no background music.")
if DRY:
    for n, l in enumerate(lines, 1): print(f"--- clip {n:02d}\n{prompt(l)}\n")
    print(f"{len(lines)} clips x {SECONDS} s = {FRAMES} frames each. On an M1 Max with 64 GB a 12-second clip took about 27 minutes."); sys.exit()
X = os.environ.get("LTX_MLX_DIR", "")
if not X or not (Path(X) / ".venv/bin/ltx-2-mlx").exists(): stop("LTX_MLX_DIR in .env must point at your ltx-2-mlx folder (docs/04-render.md, step 1).")
W = next(iter(sorted(Path(X, "weights").glob("ltx-2.5-mlx-q8*"))), None)
if not W: stop(f"the LTX-2.5 MLX model files are not in {X}/weights (docs/04-render.md, step 1).")
lora = Path(arg("--lora", str(ME / "lora/lora_weights_step_02000.safetensors")))
if not lora.exists(): stop(f"LoRA file not found: {lora}. Finish docs/03 first (scripts/4_download_lora.sh).")
ref = ME / "start_frame.png"
if not ref.exists():
    src = ME / "dataset/val_first_frame.png"
    if not src.exists(): stop("my-clone/start_frame.png is missing and there is no dataset frame to make it from.")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", "scale=704:1248:flags=lanczos", str(ref)], check=True)
    print("made my-clone/start_frame.png from your first training clip. Every clip starts from this frame, so look at it: any flaw in it shows in every clip.")
import mlx_whisper
norm = lambda t: " ".join(re.sub(r"[^a-z0-9 ]", "", t.lower().replace("-", " ")).split())
only = arg("--only", 0); strength = arg("--strength", 0.8); env = dict(os.environ, LTX2_LORA_MODE="unfused")
for n, line in enumerate(lines, 1):
    if only and n != only: continue
    out = OUT / f"{n:02d}.mp4"
    if out.exists(): print(f"clip {n:02d}: already rendered, skipping (delete the file to redo it)"); continue
    want = norm(line); best = None
    for seed in (110, 111, 112):
        t0 = time.time(); tmp = OUT / f".{n:02d}_s{seed}.mp4"
        r = subprocess.run([f"{X}/.venv/bin/ltx-2-mlx", "generate", "--distilled", "--low-ram", "--model", str(W), "--lora", str(lora), str(strength), "--image", str(ref), "0", "1.0",
                            "--prompt", prompt(line), "--width", "704", "--height", "1248", "--frames", str(FRAMES), "--frame-rate", "25", "--seed", str(seed), "-o", str(tmp)],
                           cwd=X, env=env, capture_output=True, text=True)
        if r.returncode or not tmp.exists(): print(f"clip {n:02d} seed {seed}: the renderer failed:\n{(r.stderr or r.stdout)[-600:]}"); continue
        wav = OUT / ".q.wav"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        heard = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en")["text"].strip(); wav.unlink()
        match = norm(heard) == want; print(f"clip {n:02d} seed {seed}: {int(time.time() - t0) // 60} min | heard: {heard} | {'WORDS MATCH' if match else 'WORDS DIFFER'}", flush=True)
        best = best or (tmp, heard, False)
        if match: best = (tmp, heard, True); break
    if not best: print(f"clip {n:02d}: FAILED on all seeds"); continue
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(best[0]), "-vf", "scale=1024:1792:flags=lanczos", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", str(out)], check=True)
    (OUT / f"{n:02d}.txt").write_text(f"wanted: {line}\nheard:  {best[1]}\nmatch:  {best[2]}\n")
    for p in OUT.glob(f".{n:02d}_s*.mp4"): p.unlink()
    if not best[2]: print(f"clip {n:02d}: the words did NOT match on any seed. Kept the first take. LISTEN to it: Whisper often writes names and numbers differently "
                          f"('12' for 'twelve') while the audio is right. If a word really is wrong, respell it under 'say:' in clone.yaml and delete {out.name}.")
print("\nRendering done. Listen to every clip yourself: a word check cannot hear a wrong accent or an odd pronunciation.")
