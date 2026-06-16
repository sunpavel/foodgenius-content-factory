#!/usr/bin/env python3
# Мультисцена-сборка: job.json -> вертикальный 1080x1920 ролик со склейкой сцен,
# субтитрами по сценам и финальным пекшотом. Аудио (TTS+музыка) добавим следующим шагом.
# Использование: render_multi.py job.json out.mp4
import sys, json, subprocess, os
job = json.load(open(sys.argv[1])); OUT = sys.argv[2]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920
WORK = os.path.dirname(OUT) or "."

def esc(t):
    return (t or "").replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def drawtext(text, y, size, color="white", box=0.55):
    return (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontcolor={color}:fontsize={size}:"
            f"line_spacing=10:box=1:boxcolor=black@{box}:boxborderw=22:x=(w-text_w)/2:y={y}")

def run(args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, check=True)

segs = []
for i, sc in enumerate(job.get("scenes", [])):
    seg = f"{WORK}/seg_{i}.mp4"; dur = sc.get("dur", 4)
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if sc.get("caption"):
        vf += "," + drawtext(sc["caption"], H - 360, 56)
    run(["-i", sc["clip"], "-t", str(dur), "-vf", vf, "-r", "30",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", seg])
    segs.append(seg)

ps = job.get("packshot")
if ps:
    seg = f"{WORK}/seg_pack.mp4"
    vf = drawtext(ps.get("text", "FoodGenius AI"), "(h/2)-120", 76)
    if ps.get("cta"):
        vf += "," + f"drawtext=fontfile={FONT}:text='{esc(ps['cta'])}':fontcolor=0x4ade80:fontsize=46:x=(w-text_w)/2:y=(h/2)+30"
    run(["-f", "lavfi", "-i", f"color=c=0x12343b:s={W}x{H}:d={ps.get('dur',2.5)}",
         "-vf", vf, "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", seg])
    segs.append(seg)

lst = f"{WORK}/concat.txt"
open(lst, "w").write("\n".join(f"file '{os.path.abspath(s)}'" for s in segs))
run(["-f", "concat", "-safe", "0", "-i", lst, "-c:v", "libx264", "-pix_fmt", "yuv420p",
     "-movflags", "+faststart", OUT])
print("rendered:", OUT, os.path.getsize(OUT))
