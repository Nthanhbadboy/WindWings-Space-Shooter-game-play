#!/usr/bin/env python3
"""W3 previews: contact sheet, silhouettes @128, boss-fight mock 720x1280."""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W1 = os.path.join(HERE, "..", "w1-player", "sprites")
W2 = os.path.join(HERE, "..", "w2-enemy", "sprites")
INK900 = (11, 14, 20)
PAPER = (232, 227, 217)
LEMBER = (255, 122, 61)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FBOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(p):
    return Image.open(p).convert("RGBA")


def contact():
    bodies = sorted(os.listdir(os.path.join(HERE, "sprites", "bodies")))
    parts = sorted(os.listdir(os.path.join(HERE, "sprites", "parts")))
    cell, cols, lab = 212, 6, 24
    rows_b = (len(bodies) + cols - 1) // cols
    rows_p = (len(parts) + cols - 1) // cols
    W = cols * cell
    H = 46 + rows_b * (cell + lab) + 40 + rows_p * (cell // 2 + lab) + 12
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 12)
    ft = ImageFont.truetype(FBOLD, 16)
    d.text((10, 10), "W3 BOSS — bodies x35 @512 (recipe boss, face DOWN)", font=ft, fill=PAPER)
    for i, name in enumerate(bodies):
        r, c = divmod(i, cols)
        x, y = c * cell, 46 + r * (cell + lab)
        im = load(os.path.join(HERE, "sprites", "bodies", name)).resize((cell - 14, cell - 14), Image.LANCZOS)
        img.paste(im, (x + 7, y + 3), im)
        d.text((x + 6, y + cell - 8), name.replace("boss_", "").replace("_512@ember.png", ""), font=f, fill=LEMBER)
    y0 = 46 + rows_b * (cell + lab) + 10
    d.text((10, y0), "W3 BOSS — parts x7 @256 (destructible blocks)", font=ft, fill=PAPER)
    for i, name in enumerate(parts):
        r, c = divmod(i, cols)
        x, y = c * cell, y0 + 30 + r * (cell // 2 + lab)
        im = load(os.path.join(HERE, "sprites", "parts", name)).resize((96, 96), Image.LANCZOS)
        img.paste(im, (x + cell // 2 - 48, y + 2), im)
        d.text((x + 6, y + 94), name.replace("bosspart_", "").replace("_256@ember.png", ""), font=f, fill=LEMBER)
    img.save(os.path.join(HERE, "preview", "w3_contact.png"))
    print("w3_contact.png", img.size)


def silhouettes():
    names = sorted(os.listdir(os.path.join(HERE, "sprites", "bodies")))
    cell, cols, S = 150, 7, 128
    rows = (len(names) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell, rows * cell + 34), INK900)
    d = ImageDraw.Draw(img)
    d.text((8, 8), "W3 silhouettes @128 (G-B read test)", font=ImageFont.truetype(FBOLD, 14), fill=PAPER)
    for i, n in enumerate(names):
        im = load(os.path.join(HERE, "sprites", "bodies", n)).resize((S, S), Image.LANCZOS)
        sil = Image.new("RGBA", (S, S), PAPER + (0,))
        sil.putalpha(im.getchannel("A"))
        r, c = divmod(i, cols)
        img.paste(sil, (c * cell + 11, 34 + r * cell + 11), sil)
    img.save(os.path.join(HERE, "preview", "w3_silhouettes_128.png"))
    print("w3_silhouettes_128.png", img.size)


def mock():
    W, H = 720, 1280
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    rng = random.Random(11)
    for _ in range(150):
        x, y = rng.randrange(W), rng.randrange(H)
        g = rng.choice([40, 70, 110, 160])
        d.point((x, y), fill=(g, g, g + 10))
    Bp = lambda n: load(os.path.join(HERE, "sprites", "bodies", n))  # noqa
    Pt = lambda n: load(os.path.join(HERE, "sprites", "parts", n))  # noqa
    P1 = lambda sub, n: load(os.path.join(W1, sub, n))  # noqa
    E2 = lambda n: load(os.path.join(W2, "bullets", n))  # noqa

    def put(im, cx, cy, w):
        h = int(w * im.height / im.width)
        im2 = im.resize((w, h), Image.LANCZOS)
        img.paste(im2, (cx - w // 2, cy - h // 2), im2)

    put(Bp("boss_behemoth01_512@ember.png"), 360, 270, 470)  # hero boss
    put(Pt("bosspart_rotor_256@ember.png"), 120, 520, 150)   # detached destructible parts
    put(Pt("bosspart_turretcore_256@ember.png"), 605, 540, 120)
    for n, x, y in [("enemy_bullet_orb_64@emberdim.png", 250, 620), ("enemy_bullet_teardrop_64@emberdim.png", 430, 660),
                    ("enemy_bullet_orbspike_64@emberdim.png", 560, 700), ("enemy_bullet_miniorb_64@emberdim.png", 160, 740)]:
        put(E2(n), x, y, 44)
    put(P1("bullets", "player_bullet_beam_32x512@emberdim.png"), 360, 800, 26)
    put(P1("bullets", "player_bullet_boltmk5_32@emberdim.png"), 300, 680, 30)
    put(P1("drones", "player_drone_01_128@gold.png"), 250, 1090, 64)
    put(P1("drones", "player_drone_01_128@gold.png"), 470, 1090, 64)
    put(P1("ships", "player_ship_01_256@ember.png"), 360, 1110, 150)
    d.text((14, 14), "W3 BOSS fight mock 720x1280 — behemoth + parts (concept layout)",
           font=ImageFont.truetype(FBOLD, 15), fill=PAPER)
    img.save(os.path.join(HERE, "preview", "w3_bossfight_mock_720x1280.png"))
    print("w3_bossfight_mock_720x1280.png", img.size)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    contact()
    silhouettes()
    mock()
