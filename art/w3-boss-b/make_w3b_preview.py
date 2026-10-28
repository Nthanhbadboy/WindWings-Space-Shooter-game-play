#!/usr/bin/env python3
"""Build preview/w3b_contact_sheet.png for Wave W3 BOSS (42 units, Variant B)."""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (14, 16, 46)
BORDER = (255, 168, 24)
GOLD = (255, 218, 42)
WHITE = (248, 250, 255)
MUTED = (204, 198, 242)


def checker_cell(w, h, bright=True):
    yy, xx = np.mgrid[0:h, 0:w]
    chk = ((xx // 16) + (yy // 16)) % 2
    c1 = np.array([32, 118, 232] if bright else [22, 26, 70], dtype=np.uint8)
    c2 = np.array([24, 98, 206] if bright else [30, 36, 90], dtype=np.uint8)
    return Image.fromarray(np.where(chk[:, :, None] == 0, c1, c2), "RGB").convert("RGBA")


def main():
    recs = json.load(open(os.path.join(HERE, "w3b_units.json"), encoding="utf-8"))
    bodies = [r for r in recs if r["batch"] == "B-BODY"]
    parts = [r for r in recs if r["batch"] == "B-PART"]

    W, H = 1520, 1790
    sheet = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(sheet)

    f_ban = ImageFont.truetype(FONT_B, 28)
    f_sub = ImageFont.truetype(FONT_R, 16)
    f_sec = ImageFont.truetype(FONT_B, 22)
    f_sm = ImageFont.truetype(FONT_R, 11)
    f_lab = ImageFont.truetype(FONT_B, 13)

    d.rectangle([0, 0, W, 84], fill=(32, 14, 68, 255))
    d.line([(0, 82), (W, 82)], fill=BORDER + (255,), width=3)
    d.text((24, 14), "W3 — BOSS LANE (42 UNITS)  ·  VARIANT B: SOLAR NEON ARCADE-POP", font=f_ban, fill=GOLD)
    d.text((24, 50), "Branch: arena/eca8588b  |  B-BODY x35 (512x512 asymmetric + destructible satellite) · B-PART x7 (256x256 + 512px masters)", font=f_sub, fill=MUTED)

    y = 100
    d.text((24, y), "1. B-BODY — 35 Asymmetric Dreadnought Bosses (AP-0117..0120 · each with >=1 detached destructible module)", font=f_sec, fill=GOLD)
    y += 34
    cw, ch = 198, 176
    for idx, r in enumerate(bodies):
        row, col = divmod(idx, 7)
        x = 24 + col * (cw + 14)
        yy = y + row * (ch + 32)
        cell = checker_cell(cw, ch, bright=True)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((168, 168), Image.LANCZOS)
        cell.alpha_composite(sp, ((cw - 168) // 2, (ch - 168) // 2))
        sheet.paste(cell, (x, yy))
        d.rectangle([x, yy, x + cw - 1, yy + ch - 1], outline=BORDER, width=2)
        d.text((x + 2, yy + ch + 4), f"BB-{idx+1:02d} {r['variant'][:15]}", font=f_sm, fill=WHITE)

    y += 5 * (ch + 32) + 16
    d.text((24, y), "2. B-PART — 7 Destructible Boss Sub-Parts (AP-0122..0128)", font=f_sec, fill=GOLD)
    d.text((920, y), "3. Live Boss Showdown & Gate Summary", font=f_sec, fill=GOLD)
    y += 34

    pcw, pch = 198, 180
    for idx, r in enumerate(parts):
        row, col = divmod(idx, 4)
        x = 24 + col * (pcw + 14)
        yy = y + row * (pch + 32)
        cell = checker_cell(pcw, pch, bright=False)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((164, 164), Image.LANCZOS)
        cell.alpha_composite(sp, ((pcw - 164) // 2, (pch - 164) // 2))
        sheet.paste(cell, (x, yy))
        d.rectangle([x, yy, x + pcw - 1, yy + pch - 1], outline=BORDER, width=2)
        d.text((x + 2, yy + pch + 4), f"{r['row_id']} {r['variant']}", font=f_sm, fill=WHITE)

    # Gate box + Live Boss Showdown panel
    d.rectangle([920, y, 1210, y + 408], fill=(28, 14, 64, 255), outline=BORDER, width=1)
    d.text((934, y + 14), "W3 Variant B Gates (42/42):", font=f_lab, fill=GOLD)
    for k, ln in enumerate([
        "• 35/35 B-BODY 512x512 RGBA",
        "• 7/7 B-PART 256x256 + 512px masters",
        "• 100% asymmetric L!=R weapon arms",
        "• >=1 separated destructible module",
        "• 8 distinct dreadnought chassis",
        "  (citadel, arachnid, leviathan,",
        "   chronos, seraph, kraken,",
        "   scorpion, colossus)",
        "• 0 corner alpha bleed (straight RGBA)",
        "• Functional snake_case filenames",
    ]):
        d.text((934, y + 42 + k * 28), ln, font=f_sm, fill=WHITE)

    mw, mh = 268, 408
    yy_g, xx_g = np.mgrid[0:mh, 0:mw]
    t = yy_g / (mh - 1.0)
    sky = np.zeros((mh, mw, 4), dtype=np.uint8)
    sky[:, :, 0] = (16 + 84 * t).astype(np.uint8)
    sky[:, :, 1] = (96 + 124 * t).astype(np.uint8)
    sky[:, :, 2] = (224 + 26 * t).astype(np.uint8)
    sky[:, :, 3] = 255
    mock = Image.fromarray(sky, "RGBA")
    boss_im = Image.open(os.path.join(HERE, bodies[4]["file"])).resize((208, 208), Image.LANCZOS)
    mock.alpha_composite(boss_im, (mw // 2 - 104, 8))
    eb_p = os.path.join(ROOT, "art/w2-enemy-b/sprites/bullets/enemy_bullet_10_plasma_orb_64@crimson.png")
    if os.path.exists(eb_p):
        eb = Image.open(eb_p).resize((24, 24), Image.LANCZOS)
        for bx, by in [(38, 196), (76, 224), (122, 236), (168, 224), (206, 196), (92, 268), (152, 268)]:
            mock.alpha_composite(eb, (bx, by))
    bm_p = os.path.join(ROOT, "art/w1-player-b/sprites/bullets/player_bullet_beam_32x512@cyan.png")
    if os.path.exists(bm_p):
        bm = Image.open(bm_p).resize((16, 130), Image.LANCZOS)
        mock.alpha_composite(bm, (mw // 2 - 8, 186))
    ps_p = os.path.join(ROOT, "art/w1-player-b/sprites/ships/player_ship_05_256@solar.png")
    if os.path.exists(ps_p):
        ps = Image.open(ps_p).resize((88, 88), Image.LANCZOS)
        mock.alpha_composite(ps, (mw // 2 - 44, 304))
    sheet.paste(mock, (1226, y))
    d.rectangle([1226, y, 1226 + mw - 1, y + mh - 1], outline=GOLD, width=2)

    out = os.path.join(HERE, "preview", "w3b_contact_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out, "PNG", compress_level=9)
    print(f"{out}  {sheet.size}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
