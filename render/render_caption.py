#!/usr/bin/env python3
# Красивая подпись -> прозрачный PNG: жирный Montserrat, авто-перенос по ширине, обводка.
# usage: render_caption.py "текст" out.png [width] [fontsize]
import sys
from PIL import Image, ImageDraw, ImageFont
text = sys.argv[1]; out = sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 960
size = int(sys.argv[4]) if len(sys.argv) > 4 else 68
FONT = '/opt/foodgenius/render/fonts/Montserrat-Black.ttf'
font = ImageFont.truetype(FONT, size)
stroke = max(4, size // 12)
dummy = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
def wof(s):
    b = dummy.textbbox((0, 0), s, font=font, stroke_width=stroke); return b[2] - b[0]
# жадный перенос строк по ширине W
lines, cur = [], ''
for word in text.split():
    t = (cur + ' ' + word).strip()
    if wof(t) <= W or not cur: cur = t
    else: lines.append(cur); cur = word
if cur: lines.append(cur)
lh = int(size * 1.22); pad = 28
bw = min(W + pad * 2, max((wof(l) for l in lines), default=10) + pad * 2)
bh = lh * len(lines) + pad * 2
img = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
y = pad
for l in lines:
    x = (bw - wof(l)) // 2
    d.text((x, y), l, font=font, fill=(255, 255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0, 235))
    y += lh
img.save(out)
print('caption_png', out, bw, bh, len(lines), 'lines')
