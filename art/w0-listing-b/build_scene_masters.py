#!/usr/bin/env python3
"""Compose W0 CONCEPT scenes from the CURRENT Variant-B commercial 2.5D sprites.

IMPORTANT EVIDENCE STATUS: `[RUNTIME_UNVERIFIED]`
These 4 scene masters are marketing CONCEPT composites assembled from real
Variant-B gameplay sprites (`W1..W5`), NOT Godot runtime captures. They must be
recaptured from the real playable Godot build before store submission.
"""
from __future__ import annotations

import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "art"))
import pbr25d

W, H = 900, 1400
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def asset(rel: str, size: int | tuple[int, int]) -> Image.Image:
    im = Image.open(os.path.join(ROOT, rel)).convert("RGBA")
    sz = (size, size) if isinstance(size, int) else size
    return pbr25d.downsample_straight_rgba(im, sz)


def _draw_orbital_rails_and_planet(im: Image.Image, seed: int) -> None:
    """Add authentic WindWings vertical-shmup stage depth:
    - Deep cosmos upper void (`p05 ~ 0.05`)
    - Distant W5 3D celestial body (`planet_earth_terra` / `mars` / `jupiter` / `saturn`)
    - Sunlit stratospheric cloud banks near lower flanks (`p95 ~ 0.65`)
    - Metallic orbital dock side-girders with panel seams (`detail-gradient ~ 15-20`)
    """
    planet_map = {
        1: ("art/w5-full-b/sprites/bg/parallax/bg_ap_0105_planet_earth_terra_1024@cerulean.png", 560, 760, 420, 0.72),
        2: ("art/w5-full-b/sprites/bg/parallax/bg_ap_0107_planet_mars_crimson_1024@crimson.png", 520, 140, 470, 0.68),
        3: ("art/w5-full-b/sprites/bg/parallax/bg_ap_0106_planet_jupiter_giant_1024@solar.png", 560, 160, 490, 0.72),
        4: ("art/w5-full-b/sprites/bg/parallax/bg_ap_0109_planet_saturn_ringed_1024@solar.png", 640, 730, 560, 0.74),
    }
    p_rel, p_sz, px, py, dim = planet_map.get(seed, planet_map[1])
    p_path = os.path.join(ROOT, p_rel)
    if os.path.exists(p_path):
        pl = asset(p_rel, p_sz)
        pa = np.asarray(pl, dtype=np.float32)
        pa[:, :, :3] *= dim
        pa[:, :, 3] *= 0.88
        pl = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8), "RGBA")
        im.alpha_composite(pl, (round(px - p_sz / 2), round(py - p_sz / 2)))

    # Sunlit lower stratospheric cloud wisps (flanking hero lane without washing center)
    clouds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    rng = np.random.default_rng(4200 + seed)
    cloud_spots = [
        (-80, 980, 340, 1280, (176, 218, 252, 126)),
        (610, 940, 980, 1260, (184, 224, 255, 130)),
        (-40, 1140, 390, 1420, (214, 240, 255, 146)),
        (560, 1160, 960, 1430, (212, 238, 255, 144)),
    ]
    for x0, y0, x1, y1, col in cloud_spots:
        cd.ellipse((x0, y0, x1, y1), fill=col)
    clouds = clouds.filter(ImageFilter.GaussianBlur(34))
    im.alpha_composite(clouds)

    # Subtle recessed orbital shipyard side-rails (`x=0..54` and `x=846..900`)
    rails = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rails)
    for side in (0, 1):
        rx0 = 0 if side == 0 else W - 52
        rx1 = 52 if side == 0 else W
        rd.rectangle((rx0, 82, rx1, H), fill=(18, 28, 52, 196))
        edge_x = 52 if side == 0 else W - 52
        rd.line([(edge_x, 82), (edge_x, H)], fill=(58, 128, 196, 185), width=3)
        for y in range(110, H, 88):
            rd.rectangle((rx0 + 6, y, rx1 - 6, y + 58), fill=(28, 44, 78, 205), outline=(74, 118, 172, 165), width=1)
            rd.line([(rx0 + 10, y + 12), (rx1 - 10, y + 12)], fill=(128, 178, 228, 130), width=2)
            # Small amber beacon LED every 3rd bay
            if ((y // 88) + seed) % 3 == 0:
                bx = rx1 - 14 if side == 0 else rx0 + 14
                rd.ellipse((bx - 4, y + 34, bx + 4, y + 42), fill=(255, 196, 48, 215))

    # Crisp starfield pinpoints with multi-scale brightness
    for _ in range(135):
        sx = int(rng.integers(64, W - 64))
        sy = int(rng.integers(92, H - 40))
        br = int(rng.integers(135, 248))
        sz = 2 if rng.random() > 0.72 else 1
        rd.ellipse((sx - sz, sy - sz, sx + sz, sy + sz), fill=(br - 18, br - 6, br, 210))
    im.alpha_composite(rails)


def background(seed: int = 1) -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = yy / H
    arr = np.zeros((H, W, 3), dtype=np.float32)
    # Deep cosmos top (`p05 ~ 0.05`) transitioning into rich midnight cobalt horizon
    top = np.array([5.0, 9.0, 22.0])
    mid = np.array([12.0, 26.0, 58.0])
    bot = np.array([28.0, 62.0, 112.0])
    arr[:] = np.where(
        t[:, :, None] < 0.58,
        top[None, None, :] * (1 - t[:, :, None] / 0.58) + mid[None, None, :] * (t[:, :, None] / 0.58),
        mid[None, None, :] * (1 - (t[:, :, None] - 0.58) / 0.42) + bot[None, None, :] * ((t[:, :, None] - 0.58) / 0.42),
    )
    ribbon = np.exp(-((xx - (210 + seed * 135) - 95 * np.sin(yy / 235.0)) / 155.0) ** 2)
    arr += ribbon[:, :, None] * np.array([14.0, 24.0, 44.0])[None, None, :]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    _draw_orbital_rails_and_planet(im, seed)
    return im


def glow_line(im, p0, p1, color=(0, 222, 255), width=5, glow=18, alpha=230):
    width = max(1, int(round(width)))
    glow = max(1, int(round(glow)))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).line((p0, p1), fill=(*color, 155), width=width + glow)
    lay = lay.filter(ImageFilter.GaussianBlur(glow / 2.0))
    im.alpha_composite(lay)
    core = Image.new("RGBA", im.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    cd.line((p0, p1), fill=(*color, alpha), width=width)
    if width >= 4:
        cd.line((p0, p1), fill=(242, 255, 255, min(255, alpha)), width=max(1, width // 3))
    im.alpha_composite(core)


def orb(im, xy, r, color=(255, 54, 150), alpha=235):
    x, y = xy
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4), fill=(*color, 88))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 1.1))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha), outline=(255, 218, 238, 235), width=max(1, r // 4))
    d.ellipse((x - r * 0.38, y - r * 0.38, x + r * 0.38, y + r * 0.38), fill=(255, 250, 254, 248))


def paste_center(im, sprite, x, y):
    im.alpha_composite(sprite, (round(x - sprite.width / 2), round(y - sprite.height / 2)))


def draw_enemy_hp(im, x, y, frac=0.72):
    d = ImageDraw.Draw(im)
    w, h = 58, 7
    x0, y0 = round(x - w / 2), round(y)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=3, fill=(14, 20, 36, 215), outline=(92, 128, 178, 195), width=1)
    fw = max(6, round((w - 2) * frac))
    d.rounded_rectangle((x0 + 1, y0 + 1, x0 + 1 + fw, y0 + h - 1), radius=2, fill=(255, 68, 98, 240))


def impact_burst(im, x, y, color=(255, 184, 38), scale=1.0):
    pbr25d.draw_25d_plasma_bloom(im, x, y, 64 * scale, 64 * scale, color, strength=0.86)
    for k in range(8):
        a = k * math.pi / 4 + 0.18
        r0, r1 = 18 * scale, 60 * scale
        glow_line(im, (x + math.cos(a) * r0, y + math.sin(a) * r0),
                  (x + math.cos(a) * r1, y + math.sin(a) * r1), color=color,
                  width=max(2, round(3 * scale)), glow=9 * scale, alpha=205)
    orb(im, (x, y), max(5, round(10 * scale)), color, 242)


def hud(im, wave=1, score="024800", boss_name=None, boss_hp=0.78):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle((0, 0, W, 86), fill=(4, 11, 28, 232))
    d.line((0, 85, W, 85), fill=(52, 152, 224, 195), width=2)
    f = ImageFont.truetype(FONT_B, 19)
    fs = ImageFont.truetype(FONT_B, 14)
    d.text((88, 15), f"WAVE {wave:02d}", font=f, fill=(214, 242, 255, 245))
    d.text((88, 45), "SOLAR SECTOR", font=fs, fill=(104, 168, 214, 225))
    d.text((W - 256, 15), score, font=f, fill=(255, 226, 112, 248))
    d.text((W - 256, 45), "SCORE", font=fs, fill=(116, 174, 212, 225))
    # Player shield/HP bar
    d.rounded_rectangle((W / 2 - 112, 16, W / 2 + 112, 34), radius=7, fill=(10, 24, 48, 235), outline=(88, 168, 224, 230), width=2)
    d.rounded_rectangle((W / 2 - 108, 20, W / 2 + 74, 30), radius=4, fill=(32, 218, 246, 235))
    if boss_name:
        d.rounded_rectangle((168, 98, W - 168, 118), radius=6, fill=(22, 10, 28, 228), outline=(228, 68, 112, 225), width=2)
        bw = round((W - 344) * boss_hp)
        d.rounded_rectangle((172, 102, 172 + bw, 114), radius=4, fill=(248, 52, 96, 240))
        d.text((174, 122), boss_name, font=fs, fill=(255, 186, 204, 230))
    d.rounded_rectangle((W - 132, 16, W - 88, 58), radius=8, fill=(16, 38, 76, 230), outline=(92, 176, 236, 220), width=2)
    d.text((W - 118, 25), "II", font=f, fill=(222, 244, 255, 240))
    im.alpha_composite(lay)


def scene(which: int) -> Image.Image:
    im = background(which)
    hero1 = asset("art/w1-player-b/masters/ships/player_ship_01_256@solar.png", 246)
    hero4 = asset("art/w1-player-b/masters/ships/player_ship_04_256@solar.png", 242)
    hero8 = asset("art/w1-player-b/masters/ships/player_ship_08_256@solar.png", 236)
    hero12 = asset("art/w1-player-b/masters/ships/player_ship_12_256@solar.png", 248)
    drone1 = asset("art/w1-player-b/masters/drones/player_drone_01_128@cyan.png", 108)
    drone4 = asset("art/w1-player-b/masters/drones/player_drone_04_128@cyan.png", 110)
    drone5 = asset("art/w1-player-b/masters/drones/player_drone_05_128@cyan.png", 110)
    plume = asset("art/w1-player-b/sprites/fx/player_fx_engineplume_128@solar.png", 112)
    missile = asset("art/w1-player-b/masters/bullets/player_bullet_missile_32@solar.png", 54)

    en_orb = asset("art/w2-enemy-b/masters/bodies/enemy_body_06_swarmling_pod_128@amber.png", 114)
    en_rai = asset("art/w2-enemy-b/masters/bodies/enemy_body_05_beetle_cruiser_128@crimson.png", 122)
    en_drt = asset("art/w2-enemy-b/masters/bodies/enemy_body_01_scout_dart_128@crimson.png", 112)
    en_mec = asset("art/w2-enemy-b/masters/bodies/enemy_body_18_phantom_hex_128@violet.png", 122)
    en_dsc = asset("art/w2-enemy-b/masters/bodies/enemy_body_14_cyber_disc_128@violet.png", 116)

    boss_cit = asset("art/w3-boss-b/masters/bodies/boss_body_04_citadel_mk1_512@crimson.png", 496)
    boss_krk = asset("art/w3-boss-b/masters/bodies/boss_body_09_kraken_mk1_512@crimson.png", 510)

    coin_pile = asset("art/w5-full-b/masters/ui/u-icon/ui_ap_0191_icon_coin_pile_64@solar.png", 82)
    wep_up = asset("art/w4-core-b/sprites/items/item_drop_01_weapon_up_128@solar.png", 86)

    if which == 1:
        hud(im, 3, "048650")
        wave_units = [
            (185, 235, en_rai, 0.85), (362, 215, en_mec, 0.92), (538, 215, en_mec, 0.64), (715, 235, en_rai, 1.0),
            (225, 378, en_orb, 0.72), (380, 365, en_drt, 0.45), (520, 365, en_drt, 0.88), (675, 378, en_orb, 1.0),
            (175, 515, en_drt, 1.0),  (345, 510, en_rai, 0.38), (555, 510, en_rai, 0.78), (725, 515, en_drt, 1.0),
        ]
        for x, y, sp, hp in wave_units:
            paste_center(im, sp, x, y)
            if hp < 0.99:
                draw_enemy_hp(im, x, y - 64, hp)
        for x in (372, 450, 528):
            glow_line(im, (x, 995), (x + (x - 450) * 0.18, 545), width=6, glow=16, alpha=228)
        paste_center(im, missile, 292, 745)
        paste_center(im, missile, 608, 710)
        paste_center(im, wep_up, 665, 675)
        paste_center(im, plume, 450, 1255)
        for x in (205, 695):
            paste_center(im, drone4, x, 1085)
            glow_line(im, (x, 1020), (x, 660), color=(96, 238, 255), width=4, glow=10, alpha=195)
        paste_center(im, hero1, 450, 1135)
        for x, y in ((270, 650), (620, 760), (450, 625), (335, 815)):
            orb(im, (x, y), 9, (255, 58, 152), 232)
        impact_burst(im, 345, 528, (255, 188, 38), 0.95)
    elif which == 2:
        hud(im, 8, "128940", boss_name="DREADNOUGHT // CITADEL-7001", boss_hp=0.68)
        paste_center(im, boss_cit, 450, 355)
        # Radial boss bullet curtain with clear dodge lane
        for ang_deg, rad in [(-56, 250), (-36, 290), (-18, 330), (18, 330), (36, 290), (56, 250),
                             (-44, 430), (-22, 470), (0, 410), (22, 470), (44, 430)]:
            a = math.radians(ang_deg + 90)
            orb(im, (450 + math.cos(a) * rad, 395 + math.sin(a) * rad), 10, (255, 54, 142), 236)
        for x in (386, 514):
            glow_line(im, (x, 1015), (450 + (x - 450) * 0.35, 525), color=(255, 206, 48), width=6, glow=18, alpha=235)
        paste_center(im, plume, 450, 1265)
        paste_center(im, hero4, 450, 1145)
        for x in (198, 702):
            paste_center(im, drone1, x, 1085)
            glow_line(im, (x, 1018), (450 + (x - 450) * 0.48, 510), width=4, glow=12, alpha=205)
        impact_burst(im, 342, 492, (255, 196, 48), 0.88)
        impact_burst(im, 568, 478, (0, 232, 255), 0.76)
    elif which == 3:
        hud(im, 14, "214780")
        squad = [
            (180, 250, en_dsc, 0.82), (450, 215, en_mec, 0.56), (720, 250, en_dsc, 0.90),
            (285, 395, en_rai, 0.44), (615, 395, en_rai, 0.75),
            (185, 535, en_orb, 1.0),  (715, 535, en_orb, 0.62),
        ]
        for x, y, sp, hp in squad:
            paste_center(im, sp, x, y)
            if hp < 0.99:
                draw_enemy_hp(im, x, y - 64, hp)
        paste_center(im, coin_pile, 668, 685)
        paste_center(im, coin_pile, 248, 735)
        paste_center(im, wep_up, 450, 635)
        for x in (375, 525):
            glow_line(im, (x, 1005), (x + (450 - x) * 0.32, 435), width=5, glow=15, alpha=222)
        paste_center(im, plume, 450, 1252)
        paste_center(im, drone5, 192, 1055)
        paste_center(im, drone5, 708, 1055)
        paste_center(im, hero8, 450, 1130)
        for x, y in ((315, 695), (585, 775), (195, 790), (695, 825)):
            orb(im, (x, y), 9, (255, 64, 162), 228)
        impact_burst(im, 285, 422, (255, 188, 44), 0.86)
        impact_burst(im, 450, 248, (0, 228, 255), 0.72)
    else:
        hud(im, 20, "388760", boss_name="APEX SIEGE // KRAKEN-7006", boss_hp=0.42)
        paste_center(im, boss_krk, 450, 355)
        # Focused Overdrive Plasma Beam Column + concentric shock rings at point of impact
        glow_line(im, (450, 1020), (450, 465), color=(0, 224, 255), width=24, glow=46, alpha=242)
        glow_line(im, (450, 1020), (450, 465), color=(215, 254, 255), width=8, glow=14, alpha=255)
        for r, a in ((108, 48), (76, 86), (46, 155)):
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).ellipse((450 - r, 465 - r, 450 + r, 465 + r), outline=(255, 206, 58, a), width=8)
            im.alpha_composite(lay)
        impact_burst(im, 450, 465, (255, 206, 52), 1.05)
        for x, y in ((210, 560), (295, 665), (605, 665), (690, 560), (245, 790), (655, 790)):
            orb(im, (x, y), 10, (255, 56, 148), 232)
        paste_center(im, plume, 450, 1268)
        paste_center(im, hero12, 450, 1148)
        for x in (215, 685):
            paste_center(im, drone4, x, 1082)
            glow_line(im, (x, 1018), (450 + (x - 450) * 0.55, 485), color=(255, 198, 48), width=4, glow=12, alpha=210)
    return im.convert("RGB")


def main():
    names = {
        1: "scene_s1_wave_master.png",
        2: "scene_s2_boss_master.png",
        3: "scene_s3_drone_master.png",
        4: "scene_s4_beam_master.png",
    }
    for i, name in names.items():
        out = os.path.join(HERE, "masters", name)
        scene(i).save(out, "PNG", optimize=True)
        print(out)


if __name__ == "__main__":
    main()
