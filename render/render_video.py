#!/usr/bin/env python3
# Сборка Shorts из стока Pexels: качает клипы по сценам, режет 9:16, выжигает
# субтитры С ПЕРЕНОСОМ (textfile), склейка + пекшот, опц. музыка.
# Usage: render_video.py job.json out.mp4
import sys, json, subprocess, os, urllib.request
job=json.load(open(sys.argv[1])); OUT=sys.argv[2]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; W,H=1080,1920
WORK=os.path.dirname(OUT) or "."
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def dl(url,dst):
    req=urllib.request.Request(url,headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=180) as r, open(dst,'wb') as f: f.write(r.read())
def wrap(t,maxc=20):
    words=(t or "").split(); lines=[]; cur=""
    for w in words:
        if len((cur+" "+w).strip())<=maxc: cur=(cur+" "+w).strip()
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return "\n".join(lines)
def captxt(name,text):
    p=os.path.abspath(f"{WORK}/cap_{name}.txt"); open(p,"w").write(wrap(text)); return p
def run(a): subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error"]+a,check=True)

segs=[]
for i,sc in enumerate(job.get("scenes",[])):
    raw=f"{WORK}/raw_{i}.mp4"; seg=f"{WORK}/seg_{i}.mp4"; dur=sc.get("dur",4)
    dl(sc["url"],raw)
    vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    cap=sc.get("onscreen_text")
    if cap:
        cf=captxt(str(i),cap)
        vf+=(f",drawtext=fontfile={FONT}:textfile={cf}:fontcolor=white:fontsize=58:line_spacing=14:"
             f"box=1:boxcolor=black@0.55:boxborderw=28:x=(w-text_w)/2:y=h-540")
    run(["-i",raw,"-t",str(dur),"-vf",vf,"-r","30","-an","-c:v","libx264","-pix_fmt","yuv420p",seg])
    segs.append(seg)

ps=job.get("packshot")
if ps:
    seg=f"{WORK}/seg_pack.mp4"
    tf=captxt("title",ps.get("text","FoodGenius AI"))
    vf=f"drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize=82:line_spacing=12:x=(w-text_w)/2:y=(h/2)-180"
    if ps.get('cta'):
        cf=captxt("cta",ps['cta'])
        vf+=(f",drawtext=fontfile={FONT}:textfile={cf}:fontcolor=0x4ade80:fontsize=48:line_spacing=14:"
             f"x=(w-text_w)/2:y=(h/2)+20")
    run(["-f","lavfi","-i",f"color=c=0x12343b:s={W}x{H}:d={ps.get('dur',2.5)}","-vf",vf,"-r","30","-an","-c:v","libx264","-pix_fmt","yuv420p",seg])
    segs.append(seg)

lst=f"{WORK}/concat.txt"; open(lst,"w").write("\n".join(f"file '{os.path.abspath(s)}'" for s in segs))
concat=f"{WORK}/silent.mp4"
run(["-f","concat","-safe","0","-i",lst,"-c:v","libx264","-pix_fmt","yuv420p",concat])

mu=job.get("music_url")
if mu:
    m=f"{WORK}/music.mp3"
    try:
        dl(mu,m); run(["-i",concat,"-stream_loop","-1","-i",m,"-filter:a","volume=0.45","-map","0:v","-map","1:a","-shortest","-c:v","copy","-c:a","aac","-movflags","+faststart",OUT])
    except Exception:
        run(["-i",concat,"-c:v","copy","-movflags","+faststart",OUT])
else:
    run(["-i",concat,"-c:v","copy","-movflags","+faststart",OUT])
print("rendered:",OUT,os.path.getsize(OUT))
