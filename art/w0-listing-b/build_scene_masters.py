#!/usr/bin/env python3
"""Compose W0 concept scenes from the CURRENT Variant-B gameplay sprites.

These are marketing composition masters, not Godot/runtime captures. The four
existing master filenames are retained so the immutable 25-slot export contract
can be rebuilt without renaming any store file.
"""
from __future__ import annotations
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "art"))
import pbr25d

W, H = 900, 1400
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def asset(rel, size):
    im = Image.open(os.path.join(ROOT, rel)).convert("RGBA")
    return pbr25d.downsample_straight_rgba(im, (size, size))


def background(seed=0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    arr = np.zeros((H, W, 3), dtype=np.float32)
    top = np.array([4.0, 10.0, 28.0]); bot = np.array([18.0, 48.0, 88.0])
    arr[:] = top[None, None, :] * (1 - t[:, :, None]) + bot[None, None, :] * t[:, :, None]
    # Large, low-contrast nebula ribbons, not a bright full-frame cyan wash.
    ribbon = np.exp(-((xx - (190 + seed * 170) - 80 * np.sin(yy / 260)) / 170) ** 2)
    arr += ribbon[:, :, None] * np.array([10.0, 18.0, 30.0])[None, None, :]
    # Localized cockpit/arena glow: raises gameplay readability and p95-p05
    # without washing the whole frame in cyan (audit's W0 hierarchy finding).
    focus_strength = {1: 0.62, 2: 0.70, 3: 0.82, 4: 0.52}.get(seed, 0.62)
    focus = np.exp(-(((xx - 450.0) / 390.0) ** 2 + ((yy - 900.0) / 450.0) ** 2)) * focus_strength
    arr += focus[:, :, None] * np.array([15.0, 38.0, 68.0])[None, None, :]
    rng = np.random.default_rng(1700 + seed)
    stars = rng.random((H, W))
    arr += (stars > 0.9993)[:, :, None] * np.array([38.0, 52.0, 72.0])[None, None, :]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(haze)
    for k in range(5):
        x = -150 + k * 250 + seed * 30
        hd.ellipse((x, 530 + k * 90, x + 420, 670 + k * 90), fill=(26, 61, 104, 28))
    haze = haze.filter(ImageFilter.GaussianBlur(42))
    return Image.alpha_composite(im, haze)


def glow_line(im, p0, p1, color=(0, 222, 255), width=5, glow=18, alpha=230):
    width = max(1, int(round(width))); glow = max(0, int(round(glow)))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line((p0, p1), fill=(*color, 150), width=width + glow)
    lay = lay.filter(ImageFilter.GaussianBlur(glow / 2))
    im.alpha_composite(lay)
    core = Image.new("RGBA", im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    cd.line((p0, p1), fill=(*color, alpha), width=width)
    if width >= 4: cd.line((p0, p1), fill=(238, 255, 255, min(255, alpha)), width=max(1, width // 3))
    im.alpha_composite(core)


def orb(im, xy, r, color=(255, 54, 150), alpha=230):
    x, y = xy
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((x - r * 2.5, y - r * 2.5, x + r * 2.5, y + r * 2.5), fill=(*color, 80))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 1.2)); im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha), outline=(255, 210, 236, 230), width=max(1, r // 4))
    d.ellipse((x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35), fill=(255, 247, 252, 245))


def paste_center(im, sprite, x, y):
    im.alpha_composite(sprite, (round(x - sprite.width / 2), round(y - sprite.height / 2)))


def impact_burst(im, x, y, color=(255, 174, 38), scale=1.0):
    """Compact readable hit/explosion accent, never a full-screen white wash."""
    pbr25d.draw_25d_plasma_bloom(im, x, y, 62 * scale, 62 * scale, color, strength=0.82)
    for k in range(8):
        a = k * math.pi / 4 + 0.18
        r0, r1 = 20 * scale, 58 * scale
        glow_line(im, (x + math.cos(a) * r0, y + math.sin(a) * r0),
                  (x + math.cos(a) * r1, y + math.sin(a) * r1), color=color,
                  width=max(2, round(3 * scale)), glow=9 * scale, alpha=190)
    orb(im, (x, y), max(5, round(10 * scale)), color, 235)


def hud(im, wave=1, score="024800"):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, W, 82), fill=(3, 9, 26, 218))
    d.line((24, 80, W - 24, 80), fill=(40, 125, 180, 170), width=2)
    f = ImageFont.truetype(FONT_B, 18); fs = ImageFont.truetype(FONT, 15)
    # Safe margins account for the 450:800 / 720:1280 center crop.
    d.text((92, 16), f"WAVE {wave:02d}", font=f, fill=(174, 218, 238, 230))
    d.text((92, 46), "WINDWINGS // SECTOR 01", font=fs, fill=(92, 143, 175, 220))
    d.text((W - 258, 17), score, font=f, fill=(238, 216, 133, 235))
    d.text((W - 258, 46), "SCORE", font=fs, fill=(107, 157, 185, 220))
    d.rounded_rectangle((W / 2 - 105, 18, W / 2 + 105, 34), radius=6, outline=(71, 125, 157, 220), width=2)
    d.rounded_rectangle((W / 2 - 101, 22, W / 2 + 55, 30), radius=4, fill=(41, 192, 214, 210))
    d.text((W - 142, 18), "II", font=f, fill=(183, 218, 231, 230))
    im.alpha_composite(lay)


def scene(which):
    im = background(which)
    hero = asset("art/w1-player-b/masters/ships/player_ship_01_256@solar.png", 238)
    hero8 = asset("art/w1-player-b/masters/ships/player_ship_08_256@solar.png", 220)
    drone = asset("art/w1-player-b/masters/drones/player_drone_04_128@cyan.png", 106)
    enemy_a = asset("art/w2-enemy-b/masters/bodies/enemy_body_06_swarmling_pod_128@amber.png", 104)
    enemy_b = asset("art/w2-enemy-b/masters/bodies/enemy_body_01_scout_dart_128@crimson.png", 104)
    enemy_c = asset("art/w2-enemy-b/masters/bodies/enemy_body_18_phantom_hex_128@violet.png", 100)
    boss = asset("art/w3-boss-b/masters/bodies/boss_body_04_citadel_mk1_512@crimson.png", 470)
    boss_ring = asset("art/w3-boss-b/masters/bodies/boss_body_08_seraph_mk1_512@magenta.png", 420)

    if which == 1:
        hud(im, 1)
        for row, ys in enumerate((245, 375, 505)):
            for col, xs in enumerate((180, 340, 500, 660)):
                paste_center(im, (enemy_a if (row + col) % 3 == 0 else enemy_b), xs + (row % 2) * 22, ys)
        for x in (190, 710): paste_center(im, drone, x, 1070)
        paste_center(im, hero, 450, 1130)
        for x in (350, 450, 550): glow_line(im, (x, 1010), (x + (x - 450) * 0.25, 630), width=4, glow=12, alpha=205)
        for x, y in ((270, 650), (620, 740), (450, 580)): orb(im, (x, y), 7, (255, 58, 154), 210)
        impact_burst(im, 142, 548, (255, 174, 38), 0.82)
    elif which == 2:
        hud(im, 7, "096420")
        paste_center(im, boss, 450, 285)
        for x, y in ((150, 510), (270, 610), (630, 610), (750, 510), (450, 560), (350, 710), (550, 710)):
            orb(im, (x, y), 7, (255, 56, 142), 220)
        for x in (380, 520): glow_line(im, (x, 1050), (450 + (x - 450) * 0.3, 580), width=5, glow=16, alpha=220)
        paste_center(im, hero, 450, 1150)
        for x in (195, 705): paste_center(im, drone, x, 1080)
        impact_burst(im, 176, 468, (255, 86, 159), 0.72)
        impact_burst(im, 724, 520, (255, 190, 48), 0.62)
    elif which == 3:
        hud(im, 12, "141080")
        for x, y, sp in ((160, 260, enemy_c), (350, 220, enemy_a), (550, 260, enemy_b), (740, 220, enemy_c), (250, 420, enemy_b), (650, 420, enemy_a)):
            paste_center(im, sp, x, y)
        # A readable pickup and two escorts, with clear empty space around the hero.
        coin = asset("art/w5-full-b/masters/ui/u-icon/ui_ap_0191_icon_coin_pile_64@solar.png", 86)
        paste_center(im, coin, 700, 650)
        paste_center(im, drone, 190, 1040); paste_center(im, drone, 710, 1040)
        paste_center(im, hero8, 450, 1130)
        for x in (375, 525): glow_line(im, (x, 1000), (x + (450 - x) * 0.4, 590), width=4, glow=12, alpha=210)
        for x, y in ((300, 680), (590, 780), (450, 550), (180, 760)): orb(im, (x, y), 6, (255, 67, 165), 205)
        impact_burst(im, 254, 548, (255, 185, 44), 0.70)
        impact_burst(im, 650, 580, (0, 222, 255), 0.58)
    else:
        hud(im, 20, "388760")
        paste_center(im, boss_ring, 450, 290)
        # One readable beam and a compact impact bloom, not a full-screen white flash.
        glow_line(im, (450, 1110), (450, 480), color=(0, 224, 255), width=15, glow=38, alpha=235)
        glow_line(im, (450, 1110), (450, 480), color=(180, 250, 255), width=5, glow=10, alpha=250)
        for r, a in ((100, 35), (72, 65), (42, 130)):
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.ellipse((450 - r, 450 - r, 450 + r, 450 + r), outline=(255, 198, 62, a), width=8)
            im.alpha_composite(lay)
        orb(im, (450, 450), 18, (255, 196, 48), 245)
        paste_center(im, hero, 450, 1160)
        for x in (230, 670): paste_center(im, drone, x, 1080)
    return im.convert("RGB")


def main():
    names = {1: "scene_s1_wave_master.png", 2: "scene_s2_boss_master.png", 3: "scene_s3_drone_master.png", 4: "scene_s4_beam_master.png"}
    for i, name in names.items():
        out = os.path.join(HERE, "masters", name)
        scene(i).save(out, "PNG", optimize=True)
        print(out)


if __name__ == "__main__": main()
