#!/usr/bin/env python3
"""W4 previews: contact sheet (items+fx), item silhouettes @64, battle mock."""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W1 = os.path.join(HERE, "..", "w1-player", "sprites")
W3 = os.path.join(HERE, "..", "w3-boss", "sprites")
INK900 = (11, 14, 20)
PAPER = (232, 227, 217)
LGOLD = (245, 197, 24)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FBOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(p):
    return Image.open(p).convert("RGBA")


def contact():
    items = sorted(os.listdir(os.path.join(HERE, "sprites", "items")))
    fxs = sorted(os.listdir(os.path.join(HERE, "sprites", "fx")))
    cell, cols, lab = 176, 6, 24
    rows_i = (len(items) + cols - 1) // cols
    rows_f = (len(fxs) + cols - 1) // cols
    W = cols * cell
    H = 46 + rows_i * (cell + lab) + 42 + rows_f * (cell + lab) + 12
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 12)
    ft = ImageFont.truetype(FBOLD, 16)
    d.text((10, 10), "W4 ITEM x9 @128 (recipe item)", font=ft, fill=PAPER)
    for i, name in enumerate(items):
        r, c = divmod(i, cols)
        x, y = c * cell, 46 + r * (cell + lab)
        im = load(os.path.join(HERE, "sprites", "items", name)).resize((cell - 16, cell - 16), Image.LANCZOS)
        img.paste(im, (x + 8, y + 3), im)
        d.text((x + 6, y + cell - 8), name.replace("item_", "").replace("_128@gold.png", ""), font=f, fill=LGOLD)
    y0 = 46 + rows_i * (cell + lab) + 12
    d.text((10, y0), "W4 FX x26 @256/128 (recipe fx, near-achromatic glows)", font=ft, fill=PAPER)
    for i, name in enumerate(fxs):
        r, c = divmod(i, cols)
        x, y = c * cell, y0 + 30 + r * (cell + lab)
        im = load(os.path.join(HERE, "sprites", "fx", name)).resize((cell - 16, cell - 16), Image.LANCZOS)
        img.paste(im, (x + 8, y + 3), im)
        d.text((x + 6, y + cell - 8), name.replace("fx_", "").split("_")[0], font=f, fill=PAPER)
    img.save(os.path.join(HERE, "preview", "w4_contact.png"))
    print("w4_contact.png", img.size)


def silhouettes():
    names = sorted(os.listdir(os.path.join(HERE, "sprites", "items")))
    cell, cols = 84, 9
    img = Image.new("RGB", (cols * cell, cell + 34), INK900)
    d = ImageDraw.Draw(img)
    d.text((8, 8), "W4 item silhouettes @64 (G-B read test)", font=ImageFont.truetype(FBOLD, 13), fill=PAPER)
    for i, n in enumerate(names):
        im = load(os.path.join(HERE, "sprites", "items", n)).resize((64, 64), Image.LANCZOS)
        sil = Image.new("RGBA", (64, 64), PAPER + (0,))
        sil.putalpha(im.getchannel("A"))
        img.paste(sil, (i * cell + 10, 34 + 10), sil)
    img.save(os.path.join(HERE, "preview", "w4_items_silhouettes_64.png"))
    print("w4_items_silhouettes_64.png", img.size)


def mock():
    W, H = 720, 1280
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    rng = random.Random(3)
    for _ in range(150):
        x, y = rng.randrange(W), rng.randrange(H)
        g = rng.choice([40, 70, 110, 160])
        d.point((x, y), fill=(g, g, g + 10))
    Fx = lambda n: load(os.path.join(HERE, "sprites", "fx", n))  # noqa
    It = lambda n: load(os.path.join(HERE, "sprites", "items", n))  # noqa
    P1 = lambda sub, n: load(os.path.join(W1, sub, n))  # noqa
    Bs = lambda n: load(os.path.join(W3, "bodies", n))  # noqa

    def put(im, cx, cy, w):
        h = int(w * im.height / im.width)
        im2 = im.resize((w, h), Image.LANCZOS)
        img.paste(im2, (cx - w // 2, cy - h // 2), im2)

    put(Bs("boss_ringfort01_512@ember.png"), 360, 250, 380)
    put(Fx("fx_boom_256@paper.png"), 300, 270, 300)        # boss exploding
    put(Fx("fx_shatter_256@paper.png"), 470, 200, 190)
    put(Fx("fx_crossfire_256@paper.png"), 180, 420, 130)
    put(It("item_fullpower_128@gold.png"), 250, 560, 74)   # drops falling
    put(It("item_cellamber_128@gold.png"), 370, 640, 66)
    put(It("item_lootbag_128@gold.png"), 480, 570, 78)
    put(It("item_orechunk_128@gold.png"), 560, 680, 64)
    put(P1("bullets", "player_bullet_beam_32x512@emberdim.png"), 340, 810, 26)
    put(Fx("fx_heal_256@paper.png"), 470, 1030, 120)       # pickup glows near player
    put(Fx("fx_powerup_256@paper.png"), 245, 1045, 105)
    put(P1("ships", "player_ship_01_256@ember.png"), 355, 1105, 150)
    d.text((14, 14), "W4 FX + ITEM battle mock 720x1280 (concept layout)",
           font=ImageFont.truetype(FBOLD, 15), fill=PAPER)
    img.save(os.path.join(HERE, "preview", "w4_battle_mock_720x1280.png"))
    print("w4_battle_mock_720x1280.png", img.size)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    contact()
    silhouettes()
    mock()
