#!/usr/bin/env python3
"""Generate art/w5-full-b/preview/w5b_contact_sheet.png showcasing all 274 W5-full Variant B units."""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def checker(w, h, step=10):
    im = Image.new("RGBA", (w, h), (18, 48, 118, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, step):
        for x in range(0, w, step):
            if ((x // step) + (y // step)) % 2 == 1:
                d.rectangle([x, y, x + step - 1, y + step - 1], fill=(28, 68, 152, 255))
    return im


def main():
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    recs = json.load(open(os.path.join(HERE, "w5b_units.json"), encoding="utf-8"))

    bg_recs = [r for r in recs if r["lane"] == "BG"]      # 34
    fx_item = [r for r in recs if r["lane"] in ("FX", "ITEM")]  # 19
    ui_recs = [r for r in recs if r["lane"] == "UI"]      # 221

    W, H = 2060, 2180
    sheet = Image.new("RGBA", (W, H), (10, 28, 78, 255))
    d = ImageDraw.Draw(sheet)
    f_h1 = ImageFont.truetype(FONT_B, 28)
    f_h2 = ImageFont.truetype(FONT_B, 19)
    f_lb = ImageFont.truetype(FONT_B, 11)
    f_sm = ImageFont.truetype(FONT_R, 14)

    d.rectangle([0, 0, W, 82], fill=(18, 68, 178, 255))
    d.line([(0, 82), (W, 82)], fill=(255, 208, 24, 255), width=4)
    d.text((24, 14), "WINDWINGS — WAVE W5-FULL VARIANT B ('SOLAR NEON ARCADE-POP' · 274 UNITS -> 510/510 NON-EXCL PARITY)", font=f_h1, fill=(255, 232, 92, 255))
    d.text((24, 50), "Branch: arena/eca8588b-windwings-space-shooter-game-p  |  BG +34 (44/44) · FX +17 (26/26) · ITEM +2 (9/9) · UI +221 (307/307) · EXCL 278 = 0", font=f_sm, fill=(216, 242, 255, 255))

    def draw_grid(title, items, y_start, cols, cell_w, cell_h, thumb_sz):
        d.text((24, y_start), title, font=f_h2, fill=(92, 246, 255, 255))
        y0 = y_start + 28
        for i, r in enumerate(items):
            col, row = i % cols, i // cols
            x = 24 + col * (cell_w + 8)
            y = y0 + row * (cell_h + 8)
            d.rounded_rectangle([x, y, x + cell_w, y + cell_h], radius=7, fill=(14, 40, 102, 255), outline=(56, 148, 246, 255), width=1)
            ck = checker(cell_w - 8, cell_h - 24)
            sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA")
            sp.thumbnail((thumb_sz, thumb_sz), Image.LANCZOS)
            ck.alpha_composite(sp, ((ck.width - sp.width) // 2, (ck.height - sp.height) // 2))
            sheet.alpha_composite(ck, (x + 4, y + 4))
            d.text((x + 5, y + cell_h - 17), f"{r['row_id']} {r['variant'][:11]}", font=f_lb, fill=(232, 244, 255, 255))
        rows_used = (len(items) + cols - 1) // cols
        return y0 + rows_used * (cell_h + 8) + 14

    y = draw_grid("1. BG (+34 -> 44/44: 25 G-PARALLAX Planets/Nebulae/Star-Nodes @ 1024px + 9 G-UI @ 512px)", bg_recs, 96, 17, 110, 112, 82)
    y = draw_grid("2. FX (+17 -> 26/26: Portals/Vortex/Afterimage/Victory) & ITEM (+2 -> 9/9: Thruster Boot & Meteorite)", fx_item, y, 19, 98, 104, 72)
    draw_grid("3. UI (+221 -> 307/307: U-ICON x58 @64 · U-KIT x59 [incl. 15 Boss Codex] · U-META x53 · U-SHOP x51 @256)", ui_recs, y, 19, 98, 104, 72)

    out = os.path.join(HERE, "preview/w5b_contact_sheet.png")
    sheet.convert("RGB").save(out, "PNG", optimize=True)
    print("Saved", out, sheet.size)


if __name__ == "__main__":
    main()
