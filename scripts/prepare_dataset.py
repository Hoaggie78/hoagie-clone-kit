"""Cuts your footage into 15-second training clips, writes one caption per clip (with the exact words you say), and writes
the training settings. Input: my-clone/footage/*.mov|mp4. Output: my-clone/dataset/ (clips, .wav files, dataset.json,
train.yaml, val_first_frame.png, a contact sheet to look at). Nothing leaves your computer in this step.
usage: prepare_dataset.py KIT_DIR [--seconds 15] [--max-clips 40]"""
import json, re, subprocess, sys
from pathlib import Path
import yaml

KIT = Path(sys.argv[1]); ME = KIT / "my-clone"; DS = ME / "dataset"; DS.mkdir(exist_ok=True)
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
SECONDS, MAXC = arg("--seconds", 15), arg("--max-clips", 40)
C = yaml.safe_load(open(ME / "clone.yaml")); FPS = 30
FRAMES = SECONDS * FPS // 8 * 8 + 1   # the model wants 8n+1 frames: 449 for 15 s
N = FRAMES + 6; DUR = N / FPS
stop = lambda m: sys.exit("\nSTOP: " + m + "\n")
trig = str(C.get("trigger", "")).strip()
if not re.fullmatch(r"[a-z][a-z0-9_]{3,}", trig) or trig == "alexclone": stop("set your own 'trigger' in my-clone/clone.yaml (one made-up lower-case word, e.g. your name plus 'clone').")
files = sorted(p for p in (ME / "footage").iterdir() if p.suffix.lower() in (".mov", ".mp4", ".m4v"))
if not files: stop("put your recordings in my-clone/footage/ first (docs/01-record-yourself.md).")
run = lambda *a, **k: subprocess.run([str(x) for x in a], check=True, capture_output=True, **k)
probe = lambda p, e: subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", e, "-of", "csv=p=0", str(p)]).decode().strip().strip(",")
import mlx_whisper
plan = []
for f in files:
    if "arib-std-b67" in probe(f, "stream=color_transfer") or "smpte2084" in probe(f, "stream=color_transfer"):   # iPhone HDR: the colours come out wrong unless converted
        sdr = DS / f"_sdr_{f.stem}.mov"
        if not sdr.exists():
            print(f"{f.name}: HDR video, converting to normal colour (SDR)...", flush=True)
            try: run("avconvert", "-s", f, "-p", "Preset1920x1080", "-o", sdr, "--replace")
            except Exception: stop(f"{f.name} is HDR and could not be converted. Re-record with HDR video turned OFF (docs/01), or convert it to SDR yourself.")
        f = sdr
    wav = DS / "_full.wav"; run("ffmpeg", "-v", "error", "-y", "-i", f, "-vn", "-ac", "1", "-ar", "16000", wav)
    print(f"{f.name}: listening to it to find sentences...", flush=True)
    r = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en", word_timestamps=True)
    words = [w for s in r["segments"] for w in s["words"]]; wav.unlink()
    total = float(probe(f, "format=duration")); t = 0.0
    starts = [w["start"] for i, w in enumerate(words) if i == 0 or words[i - 1]["word"].strip()[-1:] in ".?!"]
    for s in starts:                                             # windows start on a sentence, never overlap
        if s < t or s + DUR > total: continue
        inside = [w for w in words if s - 0.05 <= w["start"] and w["end"] <= s + FRAMES / FPS]
        if len(inside) < SECONDS * 1.5: continue                 # mostly silence: skip
        gaps = [b["start"] - a["end"] for a, b in zip(inside, inside[1:])]
        if gaps and max(gaps) > 2.5: continue                    # a long pause in the middle: skip
        plan.append({"src": f, "start": max(0.0, s - 0.1), "text": "".join(w["word"] for w in inside).strip()}); t = s + DUR
plan = plan[:MAXC]
if len(plan) < 15: stop(f"only {len(plan)} usable {SECONDS}-second clips were found. You need at least 15, and 30 or more is better: record more talking with fewer long pauses (about {SECONDS * 40 // 60} minutes of steady talking gives 30+ clips).")
w, h = map(int, probe(plan[0]["src"], "stream=width,height").split(",")[:2])
rot = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream_side_data=rotation", "-of", "csv=p=0", str(plan[0]["src"])], capture_output=True, text=True).stdout
if "90" in rot: w, h = h, w
crop = f"crop={int(h * 9 / 16) // 2 * 2}:{h}," if w > h else ""       # landscape footage: keep the centre as a portrait
ds = []
for i, c in enumerate(plan, 1):
    name = f"clip_{i:02d}"
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{c['start']:.3f}", "-i", c["src"], "-frames:v", N, "-vf", f"{crop}scale=544:-2:flags=lanczos,crop=544:960,setsar=1,fps={FPS}",
        "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.4f}", DS / f"{name}.mp4")
    run("ffmpeg", "-v", "error", "-y", "-ss", f"{c['start']:.3f}", "-i", c["src"], "-t", f"{DUR:.4f}", "-vn", "-ac", "1", "-ar", "48000", DS / f"{name}.wav")
    cap = (f"In a static medium shot framed from the waist up, lit with {C['training_lighting']}, {C['person']} stands centered against {C['training_backdrop']}, "
           f"wearing {C['training_wardrobe']}. Looking directly into the camera, the person speaks in a calm, conversational tone, blinking naturally and moving "
           f"slightly while talking: \"{c['text']}\" There is no background music or ambient sound, and no on-screen text.")
    ds.append({"caption": cap, "video": f"{name}.mp4", "audio": f"{name}.wav"}); print(f"{name}: {c['text'][:70]}...", flush=True)
json.dump(ds, open(DS / "dataset.json", "w"), indent=1)
(DS / "trigger.txt").write_text(trig); (DS / "frames.txt").write_text(str(FRAMES))
run("ffmpeg", "-v", "error", "-y", "-i", DS / "clip_01.mp4", "-frames:v", "1", DS / "val_first_frame.png")
t = (KIT / "pod/train.template.yaml").read_text()
for k, v in {"TRIGGER": trig, "PERSON": C["person"], "WARDROBE": C["training_wardrobe"], "BACKDROP": C["training_backdrop"]}.items(): t = t.replace("{{" + k + "}}", str(v))
(DS / "train.yaml").write_text(t)
n = len(ds); cols = 8; rows = (n + cols - 1) // cols
ins = sum((["-i", str(DS / d["video"])] for d in ds), [])
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", "".join(f"[{i}:v]select=eq(n\\,60),scale=136:240[v{i}];" for i in range(n)) + "".join(f"[v{i}]" for i in range(n)) + f"xstack=inputs={n}:layout=" + "|".join(f"{(i % cols) * 136}_{(i // cols) * 240}" for i in range(n)) + ":fill=black", "-frames:v", "1", str(DS / "CONTACT_SHEET.jpg")], capture_output=True)
for p in DS.glob("_sdr_*"): p.unlink()
print(f"\nDone: {n} clips of {SECONDS} s in my-clone/dataset/.\nLOOK at my-clone/dataset/CONTACT_SHEET.jpg and read a few captions in dataset.json before training:\n"
      " - every clip should show you, framed the same way, on the plain backdrop\n - the words in each caption should be what you say in that clip\nThen: docs/03-train-on-runpod.md")
