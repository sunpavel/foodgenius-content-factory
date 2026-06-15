#!/usr/bin/env bash
# Тест сборки: берём клип (ранее сгенерённый Veo, иначе тест-фон), выжигаем текст, шлём в Telegram.
# Секреты читает из окружения: GEMINI, TG, CHAT. Сам секретов не содержит.
set -uo pipefail
cd /opt/foodgenius/render
mkdir -p in out

echo "=== 1. достаём клип ==="
curl -s -H "x-goog-api-key: ${GEMINI}" \
  "https://generativelanguage.googleapis.com/v1beta/files/l7xln2aizw1v:download?alt=media" \
  -o in/clip1.mp4 || true
SZ=$(stat -c%s in/clip1.mp4 2>/dev/null || echo 0)
echo "clip size: $SZ"
if [ "$SZ" -lt 50000 ]; then
  echo "Veo-клип недоступен — генерю тест-фон"
  ffmpeg -y -hide_banner -loglevel error -f lavfi -i color=c=0x1e6f5c:s=1080x1920:d=6 \
    -f lavfi -i anullsrc=r=44100:cl=stereo -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac in/clip1.mp4
fi

echo "=== 2. рендер (выжигаем текст) ==="
bash render.sh in/clip1.mp4 out/final1.mp4
echo "rendered size: $(stat -c%s out/final1.mp4 2>/dev/null || echo 0)"

echo "=== 3. отправка в Telegram ==="
HTTP=$(curl -s -o /tmp/tg.json -w "%{http_code}" \
  -F chat_id="${CHAT}" \
  -F "caption=FoodGenius · тест сборки: текст выжжен через ffmpeg" \
  -F video=@out/final1.mp4 \
  "https://api.telegram.org/bot${TG}/sendVideo")
echo "telegram http: $HTTP"
grep -o '"ok":[a-z]*' /tmp/tg.json 2>/dev/null || head -c 200 /tmp/tg.json
echo
echo REMOTE_DONE
