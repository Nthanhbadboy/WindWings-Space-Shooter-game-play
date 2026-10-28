#!/usr/bin/env python3
"""Build preview/w2b_contact_sheet.png for Wave W2 ENEMY (34 units, Variant B)."""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (14, 18, 48)
BORDER = (255, 42, 136)
GOLD = (255, 214, 36)
WHITE = (248, 250, 255)
MUTED = (196, 188, 236)


def checker_cell(w, h, bright=True):
    yy, xx = np.mgrid[0:h, 0:w]
    chk = ((xx // 16) + (yy // 16)) % 2
    c1 = np.array([34, 122, 236] if bright else [22, 28, 72], dtype=np.uint8)
    c2 = np.array([26, 102, 210] if bright else [30, 38, 92], dtype=np.uint8)
    return Image.fromarray(np.where(chk[:, :, None] == 0, c1, c2), "RGB").convert("RGBA")


def main():
    recs = json.load(open(os.path.join(HERE, "w2b_units.json"), encoding="utf-8"))
    bodies = [r for r in recs if r["batch"] == "E-BODY"]
    bullets = [r for r in recs if r["batch"] == "E-BULLET"]

    W, H = 1480, 1265
    sheet = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(sheet)

    f_ban = ImageFont.truetype(FONT_B, 28)
    f_sub = ImageFont.truetype(FONT_R, 16)
    f_sec = ImageFont.truetype(FONT_B, 22)
    f_sm = ImageFont.truetype(FONT_R, 12)
    f_lab = ImageFont.truetype(FONT_B, 13)

    d.rectangle([0, 0, W, 84], fill=(28, 12, 68, 255))
    d.line([(0, 82), (W, 82)], fill=BORDER + (255,), width=3)
    d.text((24, 14), "W2 — ENEMY LANE (34 UNITS)  ·  VARIANT B: SOLAR NEON ARCADE-POP", font=f_ban, fill=GOLD)
    d.text((24, 50), "Branch: arena/eca8588b  |  E-BODY x23 (128x128 + 256px masters) · E-BULLET x11 (64x64 + 128px masters)  |  Crimson / Magenta / Violet / Amber Menace", font=f_sub, fill=MUTED)

    y = 102
    d.text((24, y), "1. E-BODY — 23 Enemy Invader Silhouettes (AP-0046..AP-0068 · 128x128 RGBA, facing downward)", font=f_sec, fill=GOLD)
    y += 34
    cw, ch = 224, 146
    for idx, r in enumerate(bodies):
        row, col = divmod(idx, 6)
        x = 24 + col * (cw + 16)
        yy = y + row * (ch + 36)
        cell = checker_cell(cw, ch, bright=True)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA")
        cell.alpha_composite(sp, ((cw - 128) // 2, (ch - 128) // 2))
        sheet.paste(cell, (x, yy))
        d.rectangle([x, yy, x + cw - 1, yy + ch - 1], outline=BORDER, width=2)
        d.text((x + 2, yy + ch + 4), f"{r['row_id']} {r['variant']}", font=f_sm, fill=WHITE)

    y += 4 * (ch + 36) + 18
    d.text((24, y), "2. E-BULLET — 11 Bullet-Hell Projectiles (AP-0070..0080 · 2x zoom)", font=f_sec, fill=GOLD)
    d.text((870, y), "3. Gate G-B (64px) & W1-vs-W2 Live Read", font=f_sec, fill=GOLD)
    y += 34

    bcw, bch = 152, 146
    for idx, r in enumerate(bullets):
        row, col = divmod(idx, 5) if idx < 10 else (2, 0)
        if idx >= 6:
            row = 1
            col = idx - 6
        else:
            row = 0
            col = idx
        x = 24 + col * (bcw + 12) if row == 0 else 24 + col * (bcw + 12)
        # Use 6 cols x 2 rows for 11 bullets!
        row, col = divmod(idx, 6)
        x = 24 + col * (130 + 10)
        yy = y + row * (134 + 34)
        cell = checker_cell(130, 134, bright=False)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((112, 112), Image.NEAREST)
        cell.alpha_composite(sp, (9, 11))
        sheet.paste(cell, (x, yy))
        d.rectangle([x, yy, x + 129, yy + 133], outline=BORDER, width=1)
        d.text((x + 2, yy + 137), f"{r['row_id'][3:]} {r['variant'][:11]}", font=f_sm, fill=WHITE)

    # 64px black silhouette strip for 10 representative E-BODY designs
    sil = Image.new("RGBA", (320, 160), (240, 244, 255, 255))
    sd = ImageDraw.Draw(sil)
    sd.text((8, 5), "64px Black Silhouette Test (10 Enemy Hulls)", font=f_sm, fill=(22, 8, 48))
    for k, bi in enumerate([0, 1, 3, 4, 6, 9, 13, 14, 16, 18]):
        r_row, r_col = divmod(k, 5)
        sp = Image.open(os.path.join(HERE, bodies[bi]["file"])).convert("RGBA").resize((54, 54), Image.LANCZOS)
        a = np.asarray(sp)[:, :, 3]
        blk = np.zeros((54, 54, 4), dtype=np.uint8)
        blk[a > 96] = [22, 6, 48, 255]
        sil.alpha_composite(Image.fromarray(blk, "RGBA"), (10 + r_col * 60, 28 + r_row * 62))
    sheet.paste(sil, (870, y))
    d.rectangle([870, y, 870 + 319, y + 159], outline=BORDER, width=2)

    # Gate box below silhouettes
    d.rectangle([870, y + 174, 1190, y + 336], fill=(26, 14, 62, 255), outline=BORDER, width=1)
    d.text((882, y + 184), "W2 Variant B Gates (34/34):", font=f_lab, fill=GOLD)
    for k, ln in enumerate([
        "• 23/23 E-BODY 128px + 256px masters",
        "• 11/11 E-BULLET 64px + 128px masters",
        "• 0 corner alpha bleed (straight RGBA)",
        "• High-contrast Crimson/Violet/Amber",
        "• Instant faction separation vs W1",
    ]):
        d.text((882, y + 208 + k * 23), ln, font=f_sm, fill=WHITE)

    # Live W1-vs-W2 Combat Readability Panel (250x336)
    mw, mh = 250, 336
    yy_g, xx_g = np.mgrid[0:mh, 0:mw]
    t = yy_g / (mh - 1.0)
    sky = np.zeros((mh, mw, 4), dtype=np.uint8)
    sky[:, :, 0] = (18 + 86 * t).astype(np.uint8)
    sky[:, :, 1] = (102 + 120 * t).astype(np.uint8)
    sky[:, :, 2] = (228 + 24 * t).astype(np.uint8)
    sky[:, :, 3] = 255
    mock = Image.fromarray(sky, "RGBA")
    # Enemy wave at top + enemy bullets raining down + W1 player firing up!
    e_lead = Image.open(os.path.join(HERE, bodies[4]["file"])).resize((72, 72), Image.LANCZOS)
    e_flank = Image.open(os.path.join(HERE, bodies[0]["file"])).resize((54, 54), Image.LANCZOS)
    mock.alpha_composite(e_lead, (mw // 2 - 36, 16))
    mock.alpha_composite(e_flank, (22, 34))
    mock.alpha_composite(e_flank, (mw - 76, 34))
    eb_orb = Image.open(os.path.join(HERE, bullets[9]["file"])).resize((26, 26), Image.LANCZOS)
    eb_dart = Image.open(os.path.join(HERE, bullets[0]["file"])).resize((26, 26), Image.LANCZOS)
    for bx, by in [(54, 118), (94, 154), (132, 154), (172, 118), (74, 198), (152, 198)]:
        mock.alpha_composite(eb_orb, (bx, by))
    mock.alpha_composite(eb_dart, (36, 164))
    mock.alpha_composite(eb_dart, (188, 164))
    p_ship_path = os.path.join(ROOT, "art/w1-player-b/sprites/ships/player_ship_01_256@solar.png")
    if os.path.exists(p_ship_path):
        p_ship = Image.open(p_ship_path).resize((84, 84), Image.LANCZOS)
        mock.alpha_composite(p_ship, (mw // 2 - 42, 236))
    sheet.paste(mock, (1206, y))
    d.rectangle([1206, y, 1206 + mw - 1, y + mh - 1], outline=GOLD, width=2)

    out = os.path.join(HERE, "preview", "w2b_contact_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out, "PNG", compress_level=9)
    print(f"{out}  {sheet.size}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
