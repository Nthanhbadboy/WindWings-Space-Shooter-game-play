#!/usr/bin/env python3
"""W1 preview evidence: contact sheets (on ink), 64px silhouette sheet (gate G-B),
and a 720x1280 gameplay mock composed ONLY from W1 sprites over a procedural
Ink & Ember background (no original-game art)."""
import glob
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK900 = (0x0B, 0x0E, 0x14)
INK700 = (0x16, 0x1C, 0x26)
INK500 = (0x2A, 0x34, 0x42)
PAPER = (0xE8, 0xE3, 0xD9)
TEAL = (0x4F, 0xD1, 0xC5)


def files(pat):
    return sorted(glob.glob(os.path.join(HERE, pat)))


def sheet_grid(items, cols, cell, title, out, bg=INK900, scale_mode="fit"):
    """items: [(PIL RGBA thumb-source, label)]"""
    rows = (len(items) + cols - 1) // cols
    W = cols * cell + (cols + 1) * 10
    H = 46 + rows * (cell + 24) + 10
    sh = Image.new("RGB", (W, H), (5, 7, 10))
    d = ImageDraw.Draw(sh)
    d.text((10, 10), title, font=ImageFont.truetype(FONT, 22), fill=PAPER)
    fl = ImageFont.truetype(FONT_R, 13)
    for i, (im, label) in enumerate(items):
        r, c = divmod(i, cols)
        x = 10 + c * (cell + 10)
        y = 46 + r * (cell + 24)
        tile = Image.new("RGB", (cell, cell), bg)
        t = im.copy()
        t.thumbnail((cell - 8, cell - 8), Image.LANCZOS if scale_mode == "fit" else Image.NEAREST)
        tile.paste(t, ((cell - t.width) // 2, (cell - t.height) // 2), t)
        sh.paste(tile, (x, y))
        d.rectangle([x, y, x + cell - 1, y + cell - 1], outline=INK500)
        d.text((x + 2, y + cell + 4), label, font=fl, fill=PAPER)
    sh.save(out, "PNG", optimize=True)
    print(out, sh.size)


def silhouette(im, size=64):
    small = im.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    black = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    out.paste(black, (0, 0), small.split()[3].point(lambda a: 255 if a > 127 else 0))
    return out


def main():
    prev = os.path.join(HERE, "preview")
    os.makedirs(prev, exist_ok=True)
    ships = files("sprites/ships/*.png")
    drones = files("sprites/drones/*.png")
    bullets = files("sprites/bullets/*.png")
    fx = files("sprites/fx/*.png")

    sheet_grid([(Image.open(p), os.path.basename(p).replace("player_ship_", "ship_").replace("_256@ember.png", ""))
                for p in ships],
               cols=5, cell=170, title="W1 P-SHIP x25 - 256px - recipe ship (shown ~162px on ink-900)",
               out=os.path.join(prev, "w1_ships_contact.png"))

    small = []
    for p in drones:
        small.append((Image.open(p), os.path.basename(p).replace("player_drone_", "drone_").replace("_128@gold.png", "")))
    for p in bullets:
        im = Image.open(p)
        if im.height > 128:  # beam: show top 128px segment at 3x width for visibility
            im = im.crop((0, 0, 32, 128)).resize((96, 128), Image.NEAREST)
            small.append((im, os.path.basename(p).replace("player_bullet_", "").replace("@emberdim.png", "") + " (seg)"))
        else:
            small.append((im.resize((128, 128), Image.NEAREST),
                          os.path.basename(p).replace("player_bullet_", "").replace("@emberdim.png", "") + " 32px@4x"))
    for p in fx:
        small.append((Image.open(p), os.path.basename(p).replace("player_fx_", "fx_").replace("_128@paper.png", "")))
    sheet_grid(small, cols=5, cell=170,
               title="W1 P-DRONE x13 (128) + P-BULLET x8 (32, beams 32x512 seg) + P-FX x2 (128)",
               out=os.path.join(prev, "w1_small_contact.png"))

    sils = [(silhouette(Image.open(p)), f"ship_{i+1:02d}") for i, p in enumerate(ships)]
    sils += [(silhouette(Image.open(p)), f"drone_{i+1:02d}") for i, p in enumerate(drones)]
    sheet_grid(sils, cols=8, cell=76, title="G-B SILHOUETTE @64px - ships x25 + drones x13 (black on paper)",
               out=os.path.join(prev, "w1_silhouettes_64.png"), bg=PAPER)

    # ---- gameplay mock 720x1280, only W1 sprites + procedural bg ----
    W, H = 720, 1280
    bg = Image.new("RGB", (W, H), INK900)
    bd = ImageDraw.Draw(bg, "RGBA")
    rng = random.Random(42)
    for _ in range(26):  # flat nebula blobs ink700/ink500
        x, y = rng.randint(-80, W), rng.randint(-60, H)
        r = rng.randint(60, 220)
        col = INK700 if rng.random() < 0.6 else INK500
        bd.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=col + (70,))
    for _ in range(170):  # stars
        x, y = rng.randint(0, W), rng.randint(0, H)
        s = rng.choice([1, 1, 1, 2])
        bd.ellipse([x, y, x + s, y + s], fill=PAPER + (rng.randint(70, 190),))
    bd.ellipse([W * 0.62, H * 0.16, W * 0.86, H * 0.16 + (W * 0.24)], fill=INK500 + (120,))  # dim planet
    frame = bg.convert("RGBA")

    def paste(pat, cx, cy, w=None, h=None):
        im = Image.open(os.path.join(HERE, pat))
        if w or h:
            im = im.resize((w or im.width, h or im.height), Image.LANCZOS)
        frame.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

    # enemy stand-ins at top use drones flipped (mock only, labeled in manifest)
    for (ex, ey, k) in [(0.22, 0.12, 2), (0.5, 0.09, 6), (0.78, 0.12, 12)]:
        im = Image.open(os.path.join(HERE, f"sprites/drones/player_drone_{k:02d}_128@gold.png")).rotate(180)
        im = im.resize((92, 92), Image.LANCZOS)
        frame.paste(im, (int(W * ex - 46), int(H * ey - 46)), im)
    paste("sprites/fx/player_fx_muzzleflash_128@paper.png", W * 0.5, H * 0.30, 120, 120)
    paste("sprites/bullets/player_bullet_plasmaorb_32@emberdim.png", W * 0.30, H * 0.38, 36, 36)
    paste("sprites/bullets/player_bullet_plasmaorb_32@emberdim.png", W * 0.70, H * 0.42, 36, 36)
    # player beam (tile segment) + ship + drones + bolts + plume
    beam = Image.open(os.path.join(HERE, "sprites/bullets/player_bullet_beam_32x512@emberdim.png")).crop((0, 0, 32, 512))
    frame.paste(beam, (int(W * 0.5 - 16), int(H * 0.30)), beam)
    paste("sprites/drones/player_drone_05_128@gold.png", W * 0.27, H * 0.80, 84, 84)
    paste("sprites/drones/player_drone_11_128@gold.png", W * 0.73, H * 0.80, 84, 84)
    for bx in (0.27, 0.73):
        for by in (0.52, 0.62, 0.72):
            paste("sprites/bullets/player_bullet_boltmk5_32@emberdim.png", W * bx, H * by, 30, 30)
    paste("sprites/fx/player_fx_engineplume_128@paper.png", W * 0.5, H * 0.845, 74, 74)
    paste("sprites/ships/player_ship_03_256@ember.png", W * 0.5, H * 0.76, 150, 150)
    out = os.path.join(prev, "w1_gameplay_mock_720x1280.png")
    frame.convert("RGB").save(out, "PNG", optimize=True)
    print(out, frame.size)


if __name__ == "__main__":
    main()
