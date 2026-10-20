"""Ghép các khung PNG (do `npm run render:ship2d` xuất ra) thành GIF xem trước.

    python3 tools/ship2d_gif.py /tmp/ship2d-xxxx

Kết quả: docs/previews/<tên>.gif  +  docs/previews/<tên>-khung.jpg
Cần: pip install pillow
"""
import glob
import os
import sys

from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
name = sys.argv[2] if len(sys.argv) > 2 else 'tau-omen-2d'
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.normpath(os.path.join(here, '..', '..', 'docs', 'previews'))
os.makedirs(out, exist_ok=True)

files = sorted(glob.glob(os.path.join(src, 'f_*.png')))
if not files:
    raise SystemExit('không thấy khung nào trong ' + src)

# GIF chỉ có 256 màu → giảm xuống 48 màu, khung nhỏ cho nhẹ
small = [Image.open(f).convert('RGB').resize((280, 350), Image.LANCZOS) for f in files]
frames = [im.quantize(colors=48, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG) for im in small]
gif = os.path.join(out, name + '.gif')
frames[0].save(gif, save_all=True, append_images=frames[1:], duration=72, loop=0, optimize=True, disposal=1)
print('GIF:', gif, os.path.getsize(gif) // 1024, 'KB')

# bảng khung: 6 mốc + khung xương (hàng dưới, canh giữa)
picks = [0, len(small) // 3, len(small) // 2, len(small) // 2 + 4, len(small) // 2 + 10, len(small) - 8]
sheet = Image.new('RGB', (280 * 3, 350 * 2 + 700), (3, 6, 15))
for i, p in enumerate(picks):
    sheet.paste(small[p], ((i % 3) * 280, (i // 3) * 350))
bones_path = os.path.join(src, 'bones.png')
if os.path.exists(bones_path):
    bones = Image.open(bones_path).convert('RGB').resize((560, 700), Image.LANCZOS)
    sheet.paste(bones, ((280 * 3 - 560) // 2, 700))
jpg = os.path.join(out, name + '-khung.jpg')
sheet.save(jpg, quality=90)
print('Bảng khung:', jpg)
