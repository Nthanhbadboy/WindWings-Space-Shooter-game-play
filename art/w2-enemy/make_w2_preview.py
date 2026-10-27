#!/usr/bin/env python3
"""W2 previews: contact sheet, silhouettes @64, W1 x W2 combat mock 720x1280."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W1 = os.path.join(HERE, "..", "w1-player", "sprites")
INK900 = (11, 14, 20)
PAPER = (232, 227, 217)
LTEAL = (79, 209, 197)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FBOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(p):
    return Image.open(p).convert("RGBA")


def contact():
    bodies = sorted(os.listdir(os.path.join(HERE, "sprites", "bodies")))
    bullets = sorted(os.listdir(os.path.join(HERE, "sprites", "bullets")))
    cell, cols, lab = 170, 6, 22
    rows_b = (len(bodies) + cols - 1) // cols
    rows_u = (len(bullets) + cols - 1) // cols
    W = cols * cell
    H = 44 + rows_b * (cell + lab) + 36 + rows_u * (cell // 2 + lab) + 10
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 11)
    ft = ImageFont.truetype(FBOLD, 15)
    d.text((10, 10), "W2 ENEMY — bodies x23 @128 (recipe enemy, face DOWN)", font=ft, fill=PAPER)
    for i, name in enumerate(bodies):
        r, c = divmod(i, cols)
        x, y = c * cell, 44 + r * (cell + lab)
        im = load(os.path.join(HERE, "sprites", "bodies", name))
        im2 = im.resize((cell - 16, cell - 16), Image.LANCZOS)
        img.paste(im2, (x + 8, y + 4), im2)
        d.text((x + 6, y + cell - 6), name.replace("enemy_body_", "").replace("_128@teal.png", ""), font=f, fill=LTEAL)
    y0 = 44 + rows_b * (cell + lab) + 8
    d.text((10, y0), "W2 ENEMY — bullets x11 @64 (recipe bullet, fly DOWN)", font=ft, fill=PAPER)
    for i, name in enumerate(bullets):
        r, c = divmod(i, cols)
        x, y = c * cell, y0 + 28 + r * (cell // 2 + lab)
        im = load(os.path.join(HERE, "sprites", "bullets", name))
        im2 = im.resize((64, 64), Image.LANCZOS)
        img.paste(im2, (x + cell // 2 - 32, y + 4), im2)
        d.text((x + 6, y + 62), name.replace("enemy_bullet_", "").replace("_64@emberdim.png", ""), font=f, fill=LTEAL)
    img.save(os.path.join(HERE, "preview", "w2_contact.png"))
    print("w2_contact.png", img.size)


def silhouettes():
    names = sorted(os.listdir(os.path.join(HERE, "sprites", "bodies")))
    cell, cols = 84, 8
    rows = (len(names) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell, rows * cell + 30), INK900)
    d = ImageDraw.Draw(img)
    d.text((8, 6), "W2 silhouettes @64 (G-B read test)", font=ImageFont.truetype(FBOLD, 13), fill=PAPER)
    for i, n in enumerate(names):
        im = load(os.path.join(HERE, "sprites", "bodies", n)).resize((64, 64), Image.LANCZOS)
        sil = Image.new("RGBA", (64, 64), PAPER + (0,))
        sil.putalpha(im.getchannel("A"))
        r, c = divmod(i, cols)
        img.paste(sil, (c * cell + 10, 30 + r * cell + 10), sil)
    img.save(os.path.join(HERE, "preview", "w2_silhouettes_64.png"))
    print("w2_silhouettes_64.png", img.size)


def mock():
    W, H = 720, 1280
    img = Image.new("RGB", (W, H), INK900)
    d = ImageDraw.Draw(img)
    import random
    rng = random.Random(7)
    for _ in range(150):
        x, y = rng.randrange(W), rng.randrange(H)
        g = rng.choice([40, 70, 110, 160])
        d.point((x, y), fill=(g, g, g + 10))
    B = lambda n: load(os.path.join(HERE, "sprites", "bodies", n))  # noqa
    U = lambda n: load(os.path.join(HERE, "sprites", "bullets", n))  # noqa
    P = lambda sub, n: load(os.path.join(W1, sub, n))  # noqa

    def put(im, cx, cy, w):
        h = int(w * im.height / im.width)
        im2 = im.resize((w, h), Image.LANCZOS)
        img.paste(im2, (cx - w // 2, cy - h // 2), im2)

    # enemy wave (top, facing down)
    wave = [("enemy_body_saucer01_128@teal.png", 130, 150), ("enemy_body_triblade01_128@teal.png", 300, 110),
            ("enemy_body_lance01_128@teal.png", 450, 170), ("enemy_body_barge01_128@teal.png", 600, 130),
            ("enemy_body_orbiter01_128@teal.png", 200, 330), ("enemy_body_shard01_128@teal.png", 380, 300),
            ("enemy_body_ringgun01_128@teal.png", 540, 340)]
    for n, x, y in wave:
        put(B(n), x, y, 120)
    # enemy bullets raining down
    for n, x, y in [("enemy_bullet_orb_64@emberdim.png", 240, 520), ("enemy_bullet_teardrop_64@emberdim.png", 430, 560),
                    ("enemy_bullet_orbspike_64@emberdim.png", 580, 500), ("enemy_bullet_miniorb_64@emberdim.png", 150, 640),
                    ("enemy_bullet_capsule_64@emberdim.png", 500, 700)]:
        put(U(n), x, y, 44)
    # player (W1) + drones + beams up
    ship = P("ships", "player_ship_01_256@ember.png")
    drone = P("drones", "player_drone_01_128@gold.png")
    beam = P("bullets", "player_bullet_beam_32x512@emberdim.png")
    bolt = P("bullets", "player_bullet_boltmk5_32@emberdim.png")
    put(beam, 360, 760, 26)
    put(bolt, 300, 640, 30)
    put(bolt, 420, 600, 30)
    put(drone, 250, 1080, 64)
    put(drone, 470, 1080, 64)
    put(ship, 360, 1100, 150)
    d.text((14, 14), "W1 PLAYER x W2 ENEMY — combat mock 720x1280 (concept layout)",
           font=ImageFont.truetype(FBOLD, 15), fill=PAPER)
    img.save(os.path.join(HERE, "preview", "w2_combat_mock_720x1280.png"))
    print("w2_combat_mock_720x1280.png", img.size)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    contact()
    silhouettes()
    mock()
