#!/usr/bin/env python3
"""
W1 side-by-side comparison board (STYLE-CORRECTION lan-149 requirement).
Left: my redone 2.5D sprite (Ink & Ember). Right: nearest-by-form ORIGINAL sprite
cropped from the analysis contact sheets (docs/assets/contact-sheets @238f2b41c).
Originals are REVIEW-ONLY reference crops - never shipped as game assets.
Output: preview/w1_compare_vs_original.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = "/home/user/_refs/style149"
INK900 = (11, 14, 20)
PAPER = (232, 227, 217)
DIM = (150, 158, 175)
CELL = 252
LBL = 44


def font(sz, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/"):
        p = base + name
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def crop_cell(sheet, idx, cols, rows):
    """idx is 1-based, left->right top->bottom. Center-crop to drop #labels/edges."""
    W, H = sheet.size
    cw, ch = W / cols, H / rows
    c, r = (idx - 1) % cols, (idx - 1) // cols
    x0, y0 = c * cw, r * ch
    box = (int(x0 + cw * 0.09), int(y0 + ch * 0.10), int(x0 + cw * 0.91), int(y0 + ch * 0.84))
    return sheet.crop(box)


def fit(im, size):
    """Scale (up or down) so the longest side == size: same display scale for both."""
    s = size / max(im.width, im.height)
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


PAIRS = [
    ("sprites/ships/player_ship_01_256@ember.png", "ship_01 dart (256)", "ships-01", 19, 4),
    ("sprites/ships/player_ship_08_256@ember.png", "ship_08 delta (256)", "ships-01", 3, 4),
    ("sprites/ships/player_ship_13_256@ember.png", "ship_13 broad (256)", "ships-01", 14, 4),
    ("sprites/ships/player_ship_18_256@ember.png", "ship_18 crescent (256)", "ships-01", 21, 4),
    ("sprites/ships/player_ship_23_256@ember.png", "ship_23 twinboom (256)", "ships-01", 25, 4),
    ("sprites/drones/player_drone_01_128@gold.png", "drone_01 orb-ring (128, x2)", "drones-01", 4, 2),
    ("sprites/drones/player_drone_05_128@gold.png", "drone_05 capsule (128, x2)", "drones-01", 5, 2),
]


def main():
    sheets = {n: Image.open(os.path.join(REFS, n + ".jpg")).convert("RGB")
              for n in ("ships-01", "drones-01")}
    W = CELL * 2 + 30
    H = 64 + len(PAIRS) * (CELL + LBL) + 58
    board = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(board)
    d.text((12, 10), "W1 REDO 2.5D (lan-149) - MINE vs NEAREST ORIGINAL", fill=PAPER, font=font(19))
    d.text((12, 38), "left: Ink & Ember redo (render25d)   right: original contact-sheet crop (upscaled)",
           fill=DIM, font=font(13, False))
    y = 64
    for rel, label, sheet_name, idx, rows in PAIRS:
        mine = Image.open(os.path.join(HERE, rel)).convert("RGBA")
        mine = fit(mine, CELL)
        board.paste(mine, ((CELL - mine.width) // 2 + 6, y + (CELL - mine.height) // 2), mine)
        orig = fit(crop_cell(sheets[sheet_name], idx, 8, rows), CELL)
        board.paste(orig, (CELL + 18 + (CELL - orig.width) // 2, y + (CELL - orig.height) // 2))
        d.rectangle([6, y, 6 + CELL, y + CELL], outline=(42, 52, 66))
        d.rectangle([CELL + 18, y, CELL + 18 + CELL, y + CELL], outline=(42, 52, 66))
        d.text((10, y + CELL + 6), label, fill=PAPER, font=font(14))
        d.text((CELL + 22, y + CELL + 6), f"original {sheet_name} #{idx} (reference only)",
               fill=DIM, font=font(14, False))
        y += CELL + LBL
    d.text((12, y + 6), "Originals (c) their owners - internal style reference per lan-149, NOT game assets.",
           fill=(245, 197, 24), font=font(13))
    d.text((12, y + 28), "Same compositions/palette as flat W1 @8e6cd2f5; rendering upgraded only.",
           fill=DIM, font=font(13, False))
    out = os.path.join(HERE, "preview", "w1_compare_vs_original.png")
    board.save(out)
    print(out, board.size)


if __name__ == "__main__":
    main()
