#!/usr/bin/env bash
# Тест мультисцена-сборки: 3 цветных тест-клипа + субтитры + пекшот -> out/multi.mp4
set -e
cd /opt/foodgenius/render
mkdir -p out in
ffmpeg -y -hide_banner -loglevel error -f lavfi -i color=c=0x2d6a4f:s=1080x1920:d=5 in/s0.mp4
ffmpeg -y -hide_banner -loglevel error -f lavfi -i color=c=0x40916c:s=1080x1920:d=5 in/s1.mp4
ffmpeg -y -hide_banner -loglevel error -f lavfi -i color=c=0x1b4332:s=1080x1920:d=5 in/s2.mp4
cat > in/job.json <<'JSON'
{"scenes":[
 {"clip":"in/s0.mp4","caption":"Хватит считать калории","dur":3},
 {"clip":"in/s1.mp4","caption":"Меню под твои тренировки","dur":3},
 {"clip":"in/s2.mp4","caption":"Список покупок собирается сам","dur":3}
],"packshot":{"text":"FoodGenius AI","cta":"Открой бота в Telegram","dur":2.5}}
JSON
python3 render_multi.py in/job.json out/multi.mp4
echo MULTI_OK
