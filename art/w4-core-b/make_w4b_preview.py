#!/usr/bin/env python3
"""Build preview/w4b_contact_sheet.png for Wave W4-core (114 files across BG/ITEM/FX/UI, Variant B)."""
import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (12, 22, 56)
BORDER = (0, 218, 255)
GOLD = (255, 214, 36)
WHITE = (248, 250, 255)
MUTED = (182, 210, 248)


def checker_cell(w, h, dark=False):
    yy, xx = np.mgrid[0:h, 0:w]
    chk = ((xx // 12) + (yy // 12)) % 2
    c1 = np.array([20, 32, 76] if dark else [30, 108, 218], dtype=np.uint8)
    c2 = np.array([28, 44, 98] if dark else [24, 90, 192], dtype=np.uint8)
    return Image.fromarray(np.where(chk[:, :, None] == 0, c1, c2), "RGB").convert("RGBA")


def main():
    recs = json.load(open(os.path.join(HERE, "w4b_units.json"), encoding="utf-8"))
    bgs = [r for r in recs if r["lane"] == "BG"]
    items = [r for r in recs if r["lane"] == "ITEM"]
    fxs = [r for r in recs if r["lane"] == "FX"]
    uis = [r for r in recs if r["lane"] == "UI"]

    W, H = 1600, 1985
    sheet = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(sheet)

    f_ban = ImageFont.truetype(FONT_B, 28)
    f_sub = ImageFont.truetype(FONT_R, 15)
    f_sec = ImageFont.truetype(FONT_B, 21)
    f_sm = ImageFont.truetype(FONT_R, 10)

    d.rectangle([0, 0, W, 84], fill=(16, 38, 96, 255))
    d.line([(0, 82), (W, 82)], fill=BORDER + (255,), width=3)
    d.text((24, 14), "W4-CORE — BG / ITEM / FX / UI (112 PLANNER ROWS = 114 FILES · EXCL 278 = 0)  ·  VARIANT B", font=f_ban, fill=GOLD)
    d.text((24, 50), "Branch: arena/eca8588b  |  BG x12 (3 seamless 1024px parallax + 9 G-UI 512px) · ITEM x7 (128px) · FX x9 (256px) · UI x86 (9-slice compliant)", font=f_sub, fill=MUTED)

    y = 98
    # Row 1: 3 Parallax 1024x1024 layers + Full-Game Stacked Seam & HUD Proof + 9 G-UI Backdrops
    d.text((24, y), "1. BG — 3 Seamless 1024x1024 Parallax Layers + Live Full-Suite Gameplay Proof + 9 G-UI 512px Boards", font=f_sec, fill=GOLD)
    y += 30
    for k in range(3):
        x = 24 + k * 212
        cell = checker_cell(198, 198, dark=True)
        sp = Image.open(os.path.join(HERE, bgs[k]["file"])).convert("RGBA").resize((190, 190), Image.LANCZOS)
        cell.alpha_composite(sp, (4, 4))
        sheet.paste(cell, (x, y))
        d.rectangle([x, y, x + 197, y + 197], outline=BORDER, width=2)
        d.text((x + 2, y + 201), f"AP-0091 #{k+1} {bgs[k]['variant']}", font=f_sm, fill=WHITE)

    # Full-Suite Live Gameplay Composite (240x416) showing seamless vertical tile wrap across y=208!
    mw, mh = 248, 418
    p1 = Image.open(os.path.join(HERE, bgs[0]["file"])).convert("RGBA").resize((mw, mw), Image.LANCZOS)
    p2 = Image.open(os.path.join(HERE, bgs[1]["file"])).convert("RGBA").resize((mw, mw), Image.LANCZOS)
    p3 = Image.open(os.path.join(HERE, bgs[2]["file"])).convert("RGBA").resize((mw, mw), Image.LANCZOS)
    comp = Image.new("RGBA", (mw, mh), (0, 0, 0, 255))
    # Tile vertically across the middle of `comp` to prove ZERO horizontal seam!
    for ty in (-90, -90 + mw):
        comp.alpha_composite(p1, (0, ty))
        comp.alpha_composite(p2, (0, ty + 20))
        comp.alpha_composite(p3, (0, ty + 45))
    # Overlay Boss HP HUD bar, Pause btn, Enemy,FX boom, Item drop, W1 Player!
    hp_bar = Image.open(os.path.join(HERE, "sprites/ui/u-hud/ui_hud_boss_hp_track_256@crimson.png")).resize((160, 48), Image.LANCZOS)
    pause_b = Image.open(os.path.join(HERE, "sprites/ui/u-hud/ui_hud_pause_btn_256@azure.png")).resize((38, 38), Image.LANCZOS)
    comp.alpha_composite(hp_bar, (12, 4))
    comp.alpha_composite(pause_b, (mw - 46, 8))
    boom = Image.open(os.path.join(HERE, fxs[1]["file"])).resize((76, 76), Image.LANCZOS)
    comp.alpha_composite(boom, (26, 98))
    drop = Image.open(os.path.join(HERE, items[0]["file"])).resize((42, 42), Image.LANCZOS)
    comp.alpha_composite(drop, (168, 178))
    e_path = os.path.join(ROOT, "art/w2-enemy-b/sprites/bodies/enemy_body_05_beetle_cruiser_128@crimson.png")
    if os.path.exists(e_path):
        comp.alpha_composite(Image.open(e_path).resize((68, 68), Image.LANCZOS), (126, 68))
    p_path = os.path.join(ROOT, "art/w1-player-b/sprites/ships/player_ship_05_256@solar.png")
    if os.path.exists(p_path):
        comp.alpha_composite(Image.open(p_path).resize((92, 92), Image.LANCZOS), (mw // 2 - 46, 296))
    sheet.paste(comp, (666, y))
    d.rectangle([666, y, 666 + mw - 1, y + mh - 1], outline=GOLD, width=2)
    d.text((668, y + mh + 4), "Live W1+W2+W4 Seam & HUD Proof", font=f_sm, fill=GOLD)

    # 9 G-UI backdrops (5 on top row right, 4 + 3 items on second row)
    for k, r in enumerate(bgs[3:]):
        if k < 4:
            gx, gy = 934 + k * 162, y
        else:
            gx, gy = 934 + (k - 4) * 130, y + 220
        sz = 150 if k < 4 else 120
        cell = checker_cell(sz, sz, dark=True)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((sz - 8, sz - 8), Image.LANCZOS)
        cell.alpha_composite(sp, (4, 4))
        sheet.paste(cell, (gx, gy))
        d.rectangle([gx, gy, gx + sz - 1, gy + sz - 1], outline=BORDER, width=1)
        d.text((gx + 2, gy + sz + 3), f"{r['row_id'][3:]} {r['variant'][:11]}", font=f_sm, fill=WHITE)

    # Under the 3 parallax cells on left (y + 224): 7 ITEM drops!
    d.text((24, y + 224), "2. ITEM — 7 Collectible Drops (128px)", font=f_sec, fill=GOLD)
    for k, r in enumerate(items):
        ix = 24 + k * 89
        iy = y + 254
        cell = checker_cell(82, 82, dark=False)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((74, 74), Image.LANCZOS)
        cell.alpha_composite(sp, (4, 4))
        sheet.paste(cell, (ix, iy))
        d.rectangle([ix, iy, ix + 81, iy + 81], outline=BORDER, width=1)
        d.text((ix + 1, iy + 84), f"{r['variant'][:10]}", font=f_sm, fill=WHITE)

    y += 452
    # Section 3: 9 FX (F-BOOM x5 + F-GLOW x4)
    d.text((24, y), "3. FX — 9 Boom & Glow Effects (F-BOOM x5 + F-GLOW x4 · 256x256 RGBA; F-ENEMY = 0)", font=f_sec, fill=GOLD)
    y += 30
    for k, r in enumerate(fxs):
        fx_x = 24 + k * 172
        cell = checker_cell(158, 138, dark=True)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA").resize((130, 130), Image.LANCZOS)
        cell.alpha_composite(sp, (14, 4))
        sheet.paste(cell, (fx_x, y))
        d.rectangle([fx_x, y, fx_x + 157, y + 137], outline=BORDER, width=1)
        d.text((fx_x + 2, y + 141), f"{r['row_id']} {r['variant'][:14]}", font=f_sm, fill=WHITE)

    y += 172
    # Section 4: 86 UI Widgets / Icons / 9-Slice Frames (11 cols x 8 rows = 88 slots)
    d.text((24, y), "4. UI — All 86 Kept Planner Widgets, Icons & 9-Slice Panels (U-HUD x27 · U-ICON x9 · U-KIT x38 · U-META x1 · U-SHOP x11)", font=f_sec, fill=GOLD)
    y += 30
    ucw, uch = 132, 118
    for idx, r in enumerate(uis):
        row, col = divmod(idx, 11)
        ux = 24 + col * (ucw + 10)
        uy = y + row * (uch + 26)
        cell = checker_cell(ucw, uch, dark=True)
        sp = Image.open(os.path.join(HERE, r["file"])).convert("RGBA")
        th_sz = 84 if sp.width == 64 else 108
        sp_t = sp.resize((th_sz, th_sz), Image.NEAREST if sp.width == 64 else Image.LANCZOS)
        cell.alpha_composite(sp_t, ((ucw - th_sz) // 2, (uch - th_sz) // 2))
        sheet.paste(cell, (ux, uy))
        d.rectangle([ux, uy, ux + ucw - 1, uy + uch - 1], outline=BORDER, width=1)
        short_v = r["variant"].replace("hud_", "").replace("kit_", "").replace("icon_", "").replace("shop_", "").replace("meta_", "")
        d.text((ux + 2, uy + uch + 3), f"{r['row_id'][3:]} {short_v[:13]}", font=f_sm, fill=WHITE)

    out = os.path.join(HERE, "preview", "w4b_contact_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.convert("RGB").save(out, "PNG", compress_level=9)
    print(f"{out}  {sheet.size}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
