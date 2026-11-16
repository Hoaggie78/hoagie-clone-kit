"""Step 7. Joins your clips into one video: trims the silent start and end of each clip (so there is no awkward pause or
closed-mouth smile between lines), joins them without the sound drifting, and optionally adds captions and a speed-up.
usage: .venv/bin/python scripts/7_finish.py OUT.mp4 CLIP1.mp4 CLIP2.mp4 ... [--speed 1.1] [--captions] [--script my-clone/script.txt]"""
import re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np

a = sys.argv[1:]; opt = lambda k, d=None: (a[a.index(k) + 1] if d is not None or True else None) if k in a else d
speed = float(opt("--speed", "1.0")); caps = "--captions" in a; script = opt("--script", "")
skip = set(); [skip.update({i, i + 1}) for i, x in enumerate(a) if x in ("--speed", "--script")]
pos = [x for i, x in enumerate(a) if i not in skip and x != "--captions"]; out, clips = pos[0], pos[1:]
if not clips: sys.exit(__doc__)
T = Path(tempfile.mkdtemp()); SR = 48000; LEAD, TAIL, TAIL_LAST = 0.08, 0.15, 0.45
run = lambda *c: subprocess.run([str(x) for x in c], check=True)
def pcm16k(p): return np.frombuffer(subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]), np.int16).astype(np.float32) / 32768
def nframes(p): return int(subprocess.check_output(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", p]).strip().strip(b","))
def fps(p): n, d = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", p]).decode().strip().strip(",").split("/"); return float(n) / float(d)
lines = [l.strip() for l in Path(script).read_text().splitlines() if l.strip() and not l.startswith("#")] if script else []
FPS = fps(clips[0]); pieces = []; pcm_all = b""
for n, c in enumerate(clips):
    x = pcm16k(c); k = len(x) // 320; rms = np.sqrt((x[:k * 320].reshape(k, 320) ** 2).mean(1)); on = np.nonzero(rms > rms.max() * 10 ** (-32 / 20))[0]
    a0, a1 = on[0] * 0.02, (on[-1] + 1) * 0.02; N = nframes(c)
    f0 = max(0, int((a0 - LEAD) * FPS)); f1 = min(N, int((a1 + (TAIL_LAST if n == len(clips) - 1 else TAIL)) * FPS) + 1); sh = f0 / FPS; d = (f1 - f0) / FPS
    vf = f"trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS"; ins = []
    if caps:
        import mlx_whisper
        from PIL import Image, ImageDraw, ImageFont
        w, h = map(int, subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", c]).decode().strip().strip(",").split(","))
        wav = T / "q.wav"; run("ffmpeg", "-v", "error", "-y", "-i", c, "-vn", "-ac", "1", "-ar", "16000", wav)
        ws = [x for s in mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en", word_timestamps=True)["segments"] for x in s["words"]]
        txt = lines[n].split() if n < len(lines) and len(lines[n].split()) == len(ws) else [x["word"].strip() for x in ws]   # your own spelling when the word counts agree
        font = next((ImageFont.truetype(p, int(w * 0.062)) for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if Path(p).exists()), None)
        if font is None: sys.exit("\nSTOP: no bold font found for captions. Run again without --captions.\n")
        chain = "[v0]"; flt = [f"[0:v]{vf}[v0]"]
        for q in range(0, len(ws), 3):
            words = " ".join(re.sub(r"[.,?!]+$", "", t) for t in txt[q:q + 3]).upper(); png = T / f"c{n}_{q}.png"
            L = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(L).text((w / 2, h * 0.80), words, font=font, fill="white", anchor="mm", stroke_width=max(4, w // 130), stroke_fill="black"); L.save(png)
            t0 = max(0, ws[q]["start"] - sh - 0.04); t1 = (ws[q + 3]["start"] - sh) if q + 3 < len(ws) else d
            ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.3f}", "-i", png]; nxt = f"[v{len(ins) // 8}]"
            flt.append(f"{chain}[{len(ins) // 8}:v]overlay=0:0:enable='between(t,{t0:.3f},{t1 - 0.02:.3f})'{nxt}"); chain = nxt
        fc, vmap = ";".join(flt), chain
    else: fc, vmap = f"[0:v]{vf}[vo]", "[vo]"
    piece = T / f"p{n:02d}.mp4"
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", c, *ins, "-filter_complex", fc, "-map", vmap, "-an", "-frames:v", f1 - f0, "-r", FPS, "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", piece)
    raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{sh:.3f}", "-i", c, "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"])
    want = int(round((f1 - f0) / FPS * SR)) * 4; pcm_all += raw[:want].ljust(want, b"\0"); pieces.append(piece)   # audio cut to exactly this piece's video length: no drift
    print(f"{Path(c).name}: kept {d:.2f} s of {N / FPS:.2f} s", flush=True)
(T / "list.txt").write_text("".join(f"file '{p}'\n" for p in pieces)); (T / "a.pcm").write_bytes(pcm_all)
joined = T / "joined.mp4"
run("ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", T / "list.txt", "-f", "s16le", "-ar", SR, "-ac", "2", "-i", T / "a.pcm", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", joined)
if speed != 1.0: run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", joined, "-filter_complex", f"[0:v]setpts=PTS/{speed}[v];[0:a]atempo={speed}[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out)
else: run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", joined, "-c", "copy", "-movflags", "+faststart", out)
print("wrote", out, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).decode().strip(), "s")
