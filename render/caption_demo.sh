#!/usr/bin/env bash
# Демо красивых субтитров: хук + нижняя подпись на чистом фоне -> out/multi.mp4
set -e
cd /opt/foodgenius/render
mkdir -p out tmp
python3 render_caption.py "Что приготовить за 15 минут под твою тренировку?" tmp/hook.png 940 74
python3 render_caption.py "FoodGenius соберёт меню и список покупок сам" tmp/cta.png 940 54
ffmpeg -y -hide_banner -loglevel error -f lavfi -i "color=c=0x0f1419:s=1080x1920:d=6" \
  -i tmp/hook.png -i tmp/cta.png \
  -filter_complex "[0][1]overlay=(W-w)/2:300[a];[a][2]overlay=(W-w)/2:H-460" \
  -r 30 -c:v libx264 -pix_fmt yuv420p -movflags +faststart out/multi.mp4
echo MULTI_OK
