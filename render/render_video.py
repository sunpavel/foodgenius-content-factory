#!/usr/bin/env python3
# Сборка Shorts из стока: job.json -> качает Pexels-клипы по сценам, режет 9:16,
# выжигает субтитры, склейка + пекшот, опц. музыка. Usage: render_video.py job.json out.mp4
import sys, json, subprocess, os, urllib.request
job=json.load(open(sys.argv[1])); OUT=sys.argv[2]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; W,H=1080,1920
WORK=os.path.dirname(OUT) or "."
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def dl(url,dst):
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=180) as r, open(dst,'wb') as f: f.write(r.read())
def esc(t): return (t or "").replace("\\","\\\\").replace(":","\\:").replace("'","\\'").replace("%","\\%").replace("\n"," ").replace("\r"," ")
def run(a): subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error"]+a,check=True)

segs=[]
for i,sc in enumerate(job.get("scenes",[])):
    raw=f"{WORK}/raw_{i}.mp4"; seg=f"{WORK}/seg_{i}.mp4"; dur=sc.get("dur",4)
    dl(sc["url"],raw)
    vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    cap=sc.get("onscreen_text")
    if cap:
        vf+=f",drawtext=fontfile={FONT}:text='{esc(cap)}':fontcolor=white:fontsize=64:line_spacing=12:box=1:boxcolor=black@0.5:boxborderw=26:x=(w-text_w)/2:y=h-440"
    run(["-i",raw,"-t",str(dur),"-vf",vf,"-r","30","-an","-c:v","libx264","-pix_fmt","yuv420p",seg])
    segs.append(seg)

ps=job.get("packshot")
if ps:
    seg=f"{WORK}/seg_pack.mp4"
    vf=f"drawtext=fontfile={FONT}:text='{esc(ps.get('text','FoodGenius AI'))}':fontcolor=white:fontsize=76:x=(w-text_w)/2:y=(h/2)-120"
    if ps.get('cta'):
        vf+=f",drawtext=fontfile={FONT}:text='{esc(ps['cta'])}':fontcolor=0x4ade80:fontsize=44:line_spacing=10:x=(w-text_w)/2:y=(h/2)+30"
    run(["-f","lavfi","-i",f"color=c=0x12343b:s={W}x{H}:d={ps.get('dur',2.5)}","-vf",vf,"-r","30","-an","-c:v","libx264","-pix_fmt","yuv420p",seg])
    segs.append(seg)

lst=f"{WORK}/concat.txt"; open(lst,"w").write("\n".join(f"file '{os.path.abspath(s)}'" for s in segs))
concat=f"{WORK}/silent.mp4"
run(["-f","concat","-safe","0","-i",lst,"-c:v","libx264","-pix_fmt","yuv420p",concat])

mu=job.get("music_url")
if mu:
    m=f"{WORK}/music.mp3"
    try:
        dl(mu,m)
        run(["-i",concat,"-stream_loop","-1","-i",m,"-filter:a","volume=0.45","-map","0:v","-map","1:a","-shortest","-c:v","copy","-c:a","aac","-movflags","+faststart",OUT])
    except Exception as e:
        run(["-i",concat,"-c:v","copy","-movflags","+faststart",OUT])
else:
    run(["-i",concat,"-c:v","copy","-movflags","+faststart",OUT])
print("rendered:",OUT,os.path.getsize(OUT))
