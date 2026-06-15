#!/usr/bin/env bash
# FoodGenius render v1 — выжигает хук и CTA на вертикальном клипе 1080x1920.
# Тексты читает из in/hook.txt и in/cta.txt (UTF-8). Аргументы: IN_VIDEO OUT_VIDEO.
set -euo pipefail
IN="${1:?usage: render.sh IN OUT}"
OUT="${2:?usage: render.sh IN OUT}"
DIR="$(cd "$(dirname "$0")" && pwd)"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
W=1080; H=1920

# экранирование спецсимволов для drawtext
esc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/:/\\:/g' -e "s/'/\\\\'/g" -e 's/%/\\%/g'; }
HOOK=$(esc "$(cat "$DIR/in/hook.txt")")
CTA=$(esc "$(cat "$DIR/in/cta.txt")")

ffmpeg -y -hide_banner -loglevel error -i "$IN" \
  -vf "scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},\
drawtext=fontfile=${FONT}:text='${HOOK}':fontcolor=white:fontsize=78:line_spacing=12:box=1:boxcolor=black@0.55:boxborderw=26:x=(w-text_w)/2:y=230,\
drawtext=fontfile=${FONT}:text='${CTA}':fontcolor=white:fontsize=56:box=1:boxcolor=0x111111@0.72:boxborderw=22:x=(w-text_w)/2:y=h-330" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
echo "rendered: $OUT"
