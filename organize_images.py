#!/usr/bin/env python3
"""Organize collected WindWings: Space Shooter images into gameplay categories.

Categorization is based on:
  - OCR text extracted from each image (RapidOCR)
  - Source page context (title / screenshot numbering)
  - Image dimensions/orientation
Confidence levels: high = OCR-confirmed, medium = strong source context, low = inferred.
"""
import csv
import hashlib
import os
import shutil
from PIL import Image

SRC = "image-search"
ROOT = os.path.dirname(os.path.abspath(__file__))

# old_filename -> (folder, new_name, source_site, source_url, confidence, notes)
MAPPING = {
    # ---------------- Ship_Types ----------------
    "windwings-galaxy-attack-level-select-cam-1.jpg": (
        "Ship_Types", "ship_01_collect-your-spaceship_taptap.jpg",
        "taptap.io", "https://www.taptap.io/app/247558", "high",
        "OCR: 'COLLECT YOUR SPACESHIP' - official ship collection screen"),
    "windwings-galaxy-attack-spaceship-ships-5.png": (
        "Ship_Types", "ship_02_google-play-screenshot-01_appbrain.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-space-shooter/com.Wind.wings.Space.Shooter", "medium",
        "Google Play screenshot 1/9; ship content inferred from search context - verify"),
    "windwings-space-shooter-spaceship-select-4.jpg": (
        "Ship_Types", "ship_03_playmods-gallery-720p.jpg",
        "playmods.net", "https://playmods.net/game/windwings-space-shooter/com.Wind.wings.Space.Shooter1", "medium",
        "720p full screenshot from hangar/ship selection gallery - inferred, verify"),

    # ---------------- Level_Screens ----------------
    "windwings-space-shooter-gameplay-screens-3.png": (
        "Level_Screens", "level_01_softonic-screenshot.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "Gameplay screenshot (Softonic)"),
    "windwings-space-shooter-gameplay-screens-4.jpg": (
        "Level_Screens", "level_02_apkmody-screenshot-02.jpg",
        "apkmody.com", "https://apkmody.com/games/windwings-space-shooter", "high", "OCR: score '12' - in-level gameplay"),
    "windwings-space-shooter-gameplay-screens-5.jpg": (
        "Level_Screens", "level_03_apkmody-screenshot-06.jpg",
        "apkmody.com", "https://apkmody.com/games/windwings-space-shooter", "high", "Gameplay screenshot 6 (Apkmody)"),
    "windwings-space-shooter-spaceship-select-1.jpg": (
        "Level_Screens", "level_04_playmods-gallery-720p.jpg",
        "playmods.net", "https://playmods.net/game/windwings-space-shooter/com.Wind.wings.Space.Shooter1", "high", "720p full-resolution gameplay screenshot"),
    "windwings-space-shooter-spaceship-select-3.webp": (
        "Level_Screens", "level_05_modyolo-gallery-04.webp",
        "modyolo.com", "https://modyolo.com/windwings-space-shooter.html", "high", "Gameplay gallery screenshot"),
    "windwings-space-shooter-spaceship-select-5.png": (
        "Level_Screens", "level_06_apkdog-screenshot.png",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "Gameplay screenshot"),
    "windwings-space-shooter-boss-fight-enemy-4.png": (
        "Level_Screens", "level_07_apkdog-screenshot-02.png",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "Gameplay screenshot"),
    "windwings-space-shooter-boss-monster-big-5.jpg": (
        "Level_Screens", "level_08_google-play-premium-screenshot.jpg",
        "play.google.com (via Brave cache)", "https://play.google.com/store/apps/details?id=com.Gcenter.WindWings.SpaceShooter.Premium", "high", "OCR: score '6668' - in-level gameplay"),
    "windwings-space-shooter-pvp-multiplayer--3.jpg": (
        "Level_Screens", "level_09_liteapks-versus-screenshot.jpg",
        "liteapks.com", "https://liteapks.com/windwings-space-shooter-gala.html", "high", "OCR: 'VS' - versus/battle screen"),
    "windwings-galaxy-attack-level-select-cam-4.jpg": (
        "Level_Screens", "level_10_taptap-chapter-screenshot.jpg",
        "taptap.io", "https://www.taptap.io/app/247558", "high", "OCR: '2193 2' - level/chapter screen"),
    "windwings-galaxy-attack-weapons-laser-me-5.png": (
        "Level_Screens", "level_11_google-play-screenshot.png",
        "play.google.com (via Brave cache)", "https://play.google.com/store/apps/details?id=com.Wind.wings.Space.Shooter", "high", "Google Play gameplay screenshot"),
    "windwings-galaxy-attack-weapons-laser-me-3.png": (
        "Level_Screens", "level_12_transform-in-battle_gamespot.png",
        "gamespot.com.cn", "https://m.gamespot.com.cn/en/games/20355", "high", "OCR: 'TRANSFORM IN BATTLE' - ship transformation mechanic"),
    "windwings-space-shooter-alien-monsters-e-4.jpg": (
        "Level_Screens", "level_13_transform-in-battle_modyolo.jpg",
        "modyolo.com", "https://modyolo.com/windwings-premium.html", "high", "OCR: 'TRANSFORM IN BATTLE' - ship transformation mechanic"),
    "windwings-space-shooter-alien-monsters-e-5.jpg": (
        "Level_Screens", "level_14_apkpure-screenshot-02.jpg",
        "apkpure.com", "https://m.apkpure.com/id/windwings-space-shooter/com.Wind.wings.Space.Shooter", "high", "Google Play screenshot 2 (low-res 92x200)"),
    "windwings-galaxy-attack-spaceship-ships-2.png": (
        "Level_Screens", "level_15_google-play-screenshot-09_appbrain.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-space-shooter/com.Wind.wings.Space.Shooter", "medium", "Google Play screenshot 9/9"),
    "windwings-galaxy-attack-spaceship-ships-3.png": (
        "Level_Screens", "level_16_google-play-screenshot-06_appbrain.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-space-shooter/com.Wind.wings.Space.Shooter", "medium", "Google Play screenshot 6/9"),
    "windwings-galaxy-attack-spaceship-ships-4.png": (
        "Level_Screens", "level_17_google-play-screenshot-07_appbrain.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-space-shooter/com.Wind.wings.Space.Shooter", "medium", "Google Play screenshot 7/9"),
    "windwings-galaxy-attack-upgrade-equipmen-4.jpg": (
        "Level_Screens", "level_18_google-play-pro-screenshot-06_appbrain.jpg",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-galaxy-attack-pro/com.Gcenter.WindWings.SpaceShooter.Premium", "medium", "Google Play Pro screenshot 6/9"),
    "windwings-galaxy-attack-upgrade-equipmen-2.png": (
        "Level_Screens", "level_19_google-play-pro-screenshot-01_appbrain.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-galaxy-attack-pro/com.Gcenter.WindWings.SpaceShooter.Premium", "medium", "Google Play Pro screenshot 1/9 (has 'PREMIUM FOREVER' watermark)"),
    "windwings-space-shooter-vgtimes-screensh-1.jpg": (
        "Level_Screens", "level_31_apkdog-timer-screenshot.jpg",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "OCR: timer '70.35s' - in-level gameplay with HUD timer"),
    "windwings-space-shooter-vgtimes-screensh-3.jpg": (
        "Level_Screens", "level_32_transform-in-battle_apkdog.jpg",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "OCR: 'TRANSFORM IN BATTLE' - ship transformation mechanic"),
    "windwings-space-shooter-vgtimes-screensh-5.jpg": (
        "Level_Screens", "level_33_apkdog-timer-screenshot-02.jpg",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "OCR: timer '18.84s' - in-level gameplay with HUD timer"),
    "vgtimes-windwings-space-shooter-screensh-1.jpg": (
        "Level_Screens", "level_20_apkmody-screenshot-08.jpg",
        "apkmody.com", "https://apkmody.com/games/windwings-space-shooter", "high", "OCR: 'WIND WINGS' - Google Play screenshot 8"),
    "vgtimes-windwings-space-shooter-screensh-2.jpg": (
        "Level_Screens", "level_21_apkmody-screenshot-07-versus.jpg",
        "apkmody.com", "https://apkmody.com/games/windwings-space-shooter", "high", "OCR: 'VS' - Google Play screenshot 7, versus battle"),
    "windwings-galaxy-attack-boss-battle-fina-3.jpg": (
        "Level_Screens", "level_22_taptap-screenshot-01.jpg",
        "taptap.io", "https://www.taptap.io/app/247558", "high", "Gameplay screenshot (TapTap)"),
    "windwings-galaxy-attack-boss-battle-fina-5.jpg": (
        "Level_Screens", "level_23_taptap-screenshot-02.jpg",
        "taptap.io", "https://www.taptap.io/app/247558", "high", "OCR: '1000' - score HUD, in-level gameplay"),
    "files-vgtimes-com-windwings-space-shoote-2.jpg": (
        "Level_Screens", "level_24_liteapks-screenshot-01.jpg",
        "liteapks.com", "https://liteapks.com/windwings-space-shooter.html", "high", "Google Play screenshot 1 (LiteAPKs)"),
    "files-vgtimes-com-windwings-space-shoote-4.png": (
        "Level_Screens", "level_25_softonic-screenshot-01.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "Gameplay screenshot (Softonic)"),
    "files-vgtimes-com-windwings-space-shoote-5.jpg": (
        "Level_Screens", "level_26_liteapks-screenshot-02.jpg",
        "liteapks.com", "https://liteapks.com/windwings-space-shooter.html", "high", "Gameplay screenshot (LiteAPKs)"),
    "windwings-galaxy-attack-spaceship-hangar-3.png": (
        "Level_Screens", "level_27_tyhacks-google-play-screenshot.png",
        "tyhacks.com", "https://tyhacks.com/windwings-space-shooter-galaxy-attack-hack/", "medium", "Google Play screenshot mirror"),
    "kotaku-windwings-space-shooter-screensho-3.png": (
        "Level_Screens", "level_28_softonic-screenshot-03.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "Gameplay screenshot (Softonic)"),
    "kotaku-windwings-space-shooter-screensho-4.png": (
        "Level_Screens", "level_29_softonic-screenshot-04.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "Gameplay screenshot (Softonic)"),
    "kotaku-windwings-space-shooter-screensho-5.png": (
        "Level_Screens", "level_30_softonic-screenshot-05.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "Gameplay screenshot (Softonic)"),

    # ---------------- Enemy_Types ----------------
    "windwings-space-shooter-alien-monsters-e-2.png": (
        "Enemy_Types", "enemy_01_ldplayer-screenshot.png",
        "ldplayer.net", "https://www.ldplayer.net/games/windwings-space-shooter-on-pc.html", "medium",
        "From LDPlayer WindWings page (alien-enemy search context); square crop - may be icon crop, verify"),
    "windwings-galaxy-attack-ufo-alien-enemy--5.png": (
        "Enemy_Types", "enemy_02_google-play-combat-screenshot.png",
        "play.google.com (via Brave cache)", "https://play.google.com/store/apps/details?id=com.Wind.wings.Space.Shooter", "medium",
        "Google Play screenshot surfaced via alien/enemy search - enemy combat scene (inferred)"),
    "windwings-space-shooter-alien-enemy-form-3.jpg": (
        "Enemy_Types", "enemy_03_taptap-post-gameplay-frame.jpg",
        "taptap.io", "https://www.taptap.io/post/3476440", "medium",
        "Gameplay video frame from TapTap post (OCR: '2021 WIND WINGS'); alien-wave combat (inferred)"),

    # ---------------- Upgrades_UI ----------------
    "windwings-galaxy-attack-game-levels-back-1.jpg": (
        "Upgrades_UI", "upgrade_01_ship-upgrade-technology_modyolo.jpg",
        "modyolo.com", "https://modyolo.com/windwings-premium.html", "high",
        "OCR: 'GREENCYBORG SHURIKEN LV.4/30, NORMAL CANNON Lvl.4, SuperPower, Health, Magnet, Laser weapon, Upgrade Technology, MORE WAYS to be STRONGER' - full upgrade/equipment screen"),
    "windwings-galaxy-attack-level-select-cam-3.jpg": (
        "Upgrades_UI", "upgrade_02_more-ways-to-be-stronger_taptap.jpg",
        "taptap.io", "https://www.taptap.io/app/247558", "high",
        "OCR: 'MORE WAYS to be STRONGER' - upgrade/feature screen"),

    # ---------------- Boss_Fighters ----------------
    "windwings-space-shooter-vgtimes-screensh-2.jpg": (
        "Boss_Fighters", "boss_01_epic-boss-fight_apkdog.jpg",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "OCR: 'EPIC BOSS FIGHT' - boss battle screen"),
    "windwings-galaxy-attack-boss-battle-fina-2.jpg": (
        "Boss_Fighters", "boss_02_chapter-1-final-boss_reddit.jpg",
        "reddit.com (r/Windwingsgame)", "https://reddit.com/r/Windwingsgame/comments/nw0ttx/so_heres_the_final_boss_for_chapter_1_of_wind/", "medium",
        "Source post: 'the final boss for chapter 1 of wind wings game'. OCR also picked up mode-menu labels (BATTLE/CHALLENGE/ENDLESS/SPEED/CHAPTERS/UPGRADE) - verify exact content"),

    # ---------------- Backgrounds ----------------
    "windwings-space-shooter-spaceship-select-2.png": (
        "Backgrounds", "background_01_windwings-logo-keyart_modyolo.png",
        "modyolo.com", "https://modyolo.com/windwings-space-shooter.html", "high", "OCR: 'WINDWINGS' - logo key art"),
    "windwings-space-shooter-gameplay-screens-1.jpg": (
        "Backgrounds", "background_02_shoot-em-up-feature-collage_sbenny.jpg",
        "sbenny.com", "https://sbenny.com/games/windwings-space-shooter-galaxy-attack-premium", "high",
        "OCR: 'SHOOT EM UP / COLLECT YOUR SPACESHIP / TRANSFORM IN BATTLE' - feature collage art"),
    "windwings-space-shooter-boss-monster-big-3.jpg": (
        "Backgrounds", "background_03_title-screen_modyolo.jpg",
        "modyolo.com", "https://modyolo.com/windwings-premium.html", "high", "OCR: 'WINDWINGS SPACE SHOOTER' - title screen art"),
    "windwings-space-shooter-boss-monster-big-2.jpg": (
        "Backgrounds", "background_04_title-shoot-em-up_modyolo.jpg",
        "modyolo.com", "https://modyolo.com/windwings-premium.html", "high", "OCR: 'SHOOT EM UP' - title screen art"),
    "windwings-galaxy-attack-game-levels-back-5.jpg": (
        "Backgrounds", "background_05_title-shoot-em-up_playmods.jpg",
        "playmods.net", "https://playmods.net/game/windwings-space-shooter/com.Wind.wings.Space.Shooter1", "high", "OCR: 'SHOOT EM UP' - title screen art (PlayMods watermark)"),
    "windwings-space-shooter-gameplay-screens-2.png": (
        "Backgrounds", "background_06_title-splash_softonic.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "OCR: 'WINDWINGS' - title splash art"),
    "windwings-galaxy-attack-upgrade-equipmen-3.png": (
        "Backgrounds", "background_07_title-splash_appbrain-pro.png",
        "appbrain.com (Google Play listing mirror)", "https://www.appbrain.com/app/windwings-galaxy-attack-pro/com.Gcenter.WindWings.SpaceShooter.Premium", "high", "OCR: 'WINDWINGS' - title splash art (Pro listing)"),
    "windwings-space-shooter-vgtimes-screensh-4.png": (
        "Backgrounds", "background_08_logo-banner_apkdog.png",
        "apk.dog", "https://wind-wings-space-shooter-galaxy-attack.apk.dog/", "high", "OCR: 'WIND WINGS SPACE SHOOTER' - logo banner (landscape)"),
    "vgtimes-windwings-space-shooter-screensh-5.jpg": (
        "Backgrounds", "background_09_landscape-scene_liteapks.jpg",
        "liteapks.com", "https://liteapks.com/windwings-space-shooter.html", "high", "Landscape space-battle scene (1000x562)"),
    "windwings-space-shooter-boss-fight-enemy-1.jpg": (
        "Backgrounds", "background_10_hero-bluestacks.jpg",
        "bluestacks.com", "https://www.bluestacks.com/apps/arcade/windwings-space-shooter-on-pc.html", "medium", "Hero banner art (549x180) from BlueStacks page"),
    "kotaku-windwings-space-shooter-screensho-2.png": (
        "Backgrounds", "background_11_logo-banner_softonic.png",
        "softonic.com", "https://windwings-space-shooter.en.softonic.com/android", "high", "OCR: 'WINDWINGS' - logo banner (landscape 340x191)"),
    "windwings-galaxy-attack-spaceship-ships-1.webp": (
        "Backgrounds", "background_12_feature-graphic_happymod.webp",
        "happymod.cloud", "https://www.happymod.cloud/windwings-space-shooter-galaxy-attack-premium/com.Gcenter.WindWings.SpaceShooter.Premium/", "high", "OCR: 'WIND WINGS SPACE SHOOTER' - Google Play feature graphic banner"),
    "windwings-space-shooter-alien-enemy-form-5.png": (
        "Backgrounds", "background_13_keyart-kotaku-1080p.png",
        "kotaku.com (IGDB gallery)", "https://kotaku.com/games/windwings-space-shooter/gallery/1", "high",
        "1920x1080 key art, OCR: 'WIND WINGS SPACE SHOOTER'; screenshot credit: GCenter"),
}

# Files that are NOT WindWings: Space Shooter assets (other games / unrelated art / badges)
IRRELEVANT = {
    "windwings-galaxy-attack-upgrade-equipmen-1.png": "Flyff Universe equipment UI (mislabeled result)",
    "windwings-space-shooter-alien-monsters-e-1.png": "Galaga enemy PNG (different game, pngmart)",
    "windwings-space-shooter-alien-monsters-e-3.png": "Galaga alien PNG (different game, pngmart)",
    "windwings-space-shooter-boss-fight-enemy-2.png": "'Monster Shooter: Space Invader' icon (different game)",
    "windwings-space-shooter-boss-fight-enemy-3.png": "'Galaxy Attack - Space Shooter 2020' icon (different game)",
    "windwings-space-shooter-boss-monster-big-1.png": "'Monster Shooter: Space Invader' icon (duplicate)",
    "windwings-space-shooter-boss-monster-big-4.webp": "Final Fantasy boss article image (WatchMojo, unrelated)",
    "windwings-space-shooter-pvp-multiplayer--1.webp": "'FPS Strike Ops' icon (different game)",
    "windwings-space-shooter-pvp-multiplayer--2.jpg": "Dead Space 2 multiplayer screenshot (unrelated)",
    "windwings-space-shooter-pvp-multiplayer--4.jpg": "Space Marine 2 Eternal War screenshot (unrelated)",
    "windwings-space-shooter-pvp-multiplayer--5.jpg": "Space Marine 2 Eternal War screenshot (unrelated)",
    "windwings-space-shooter-alien-enemy-form-1.png": "Galaxy War: Space Shooting screenshot (different game, cafebazaar)",
    "windwings-space-shooter-alien-enemy-form-2.jpg": "Galaxy War: Space Shooting screenshot (different game, cafebazaar)",
    "windwings-space-shooter-alien-enemy-form-4.png": "'Universe Invader 2: Alien War' icon (different game)",
    "windwings-galaxy-attack-ufo-alien-enemy--1.jpg": "Redbubble alien UFO cat art print (unrelated)",
    "windwings-galaxy-attack-ufo-alien-enemy--2.jpg": "Redbubble alien UFO cat art print (unrelated)",
    "windwings-galaxy-attack-ufo-alien-enemy--3.jpg": "Redbubble alien UFO cat art print (unrelated)",
    "windwings-galaxy-attack-ufo-alien-enemy--4.jpg": "Redbubble alien UFO cat art print (unrelated)",
    "windwings-galaxy-attack-boss-battle-fina-4.jpg": "Super Mario Galaxy 'Final Battle with Bowser' image (unrelated)",
    "windwings-galaxy-attack-spaceship-hangar-1.webp": "'Burning Sky: Aircraft Combat' icon (different game)",
    "windwings-galaxy-attack-spaceship-hangar-2.png": "WindWings game icon (apkpure) - not gameplay media",
    "windwings-galaxy-attack-spaceship-hangar-4.jpg": "'Aircraft Wargame Touch Edition' screenshot (different game)",
    "windwings-galaxy-attack-weapons-laser-me-2.png": "WindWings game icon (240x240, Google Play) - not gameplay media",
    "windwings-galaxy-attack-weapons-laser-me-4.jpg": "WindWings game icon (240x240, Google Play) - not gameplay media",
    "windwings-galaxy-attack-game-levels-back-2.jpg": "'PREMIUM FOREVER' store badge watermark (not a game asset)",
    "windwings-galaxy-attack-game-levels-back-3.jpg": "'PREMIUM' store badge watermark (not a game asset)",
    "windwings-galaxy-attack-game-levels-back-4.png": "'PREMIUM FOREVER' store badge watermark (not a game asset)",
    "windwings-galaxy-attack-weapons-laser-me-1.png": "'PREMIUM FOREVER' badge (duplicate of game-levels-back-4)",
    "windwings-galaxy-attack-level-select-cam-2.png": "'PREMIUM FOREVER' badge watermark (not a game asset)",
    "vgtimes-windwings-space-shooter-screensh-3.png": "Duplicate of Softonic screenshot (md5-identical)",
    "vgtimes-windwings-space-shooter-screensh-4.png": "Duplicate of Softonic screenshot (md5-identical)",
    "kotaku-windwings-space-shooter-screensho-1.png": "Duplicate of Softonic screenshot (md5-identical)",
    "kotaku-windwings-space-shooter-gallery-s-1.jpg": "Duplicate of feature collage (md5-identical to gameplay-screens-1)",
    "kotaku-windwings-space-shooter-gallery-s-2.png": "Duplicate of Softonic screenshot (md5-identical)",
    "kotaku-windwings-space-shooter-gallery-s-3.png": "Duplicate of Softonic logo banner (md5-identical)",
    "kotaku-windwings-space-shooter-gallery-s-4.png": "Duplicate of Softonic screenshot (md5-identical)",
    "kotaku-windwings-space-shooter-gallery-s-5.png": "Duplicate of Softonic title splash (md5-identical)",
    "windwings-galaxy-attack-upgrade-equipmen-5.jpg": "Duplicate of upgrade_01 source image (md5-identical)",
    "windwings-galaxy-attack-level-select-cam-5.jpg": "Duplicate of upgrade_01 source image (md5-identical)",
    "windwings-galaxy-attack-boss-battle-fina-1.webp": "Duplicate of feature graphic (md5-identical)",
    "windwings-galaxy-attack-spaceship-hangar-5.jpg": "Duplicate of upgrade_01 source image (md5-identical)",
    "windwings-space-shooter-boss-fight-enemy-5.png": "Duplicate of enemy_01 source image (md5-identical)",
    "files-vgtimes-com-windwings-space-shoote-1.webp": "9mod MOD APK thumbnail/icon (150x150, not a game asset)",
    "files-vgtimes-com-windwings-space-shoote-3.webp": "9mod MOD APK thumbnail/icon (150x150, not a game asset)",
    "vgtimes-windwings-unnamed-gallery-1.jpg": "WindWings 2: Galaxy Revenge (sequel - different game, modyolo)",
    "vgtimes-windwings-unnamed-gallery-2.jpg": "WindWings 2: Galaxy Revenge (sequel - different game, modyolo)",
    "vgtimes-windwings-unnamed-gallery-4.jpg": "WindWings 2: Galaxy Revenge (sequel - different game, modyolo)",
    "vgtimes-windwings-unnamed-gallery-3.jpg": "Met Museum 'Michael C. Rockefeller Wing' photo (unrelated)",
    "vgtimes-windwings-unnamed-gallery-5.png": "Zelda: Wind Waker figurine gallery photo (unrelated)",
}


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main():
    os.chdir(ROOT)
    seen_md5 = {}
    manifest_rows = []
    moved, skipped_dup, deleted = [], [], []

    for old, (folder, new, site, url, conf, notes) in sorted(MAPPING.items()):
        if not os.path.exists(os.path.join(SRC, old)):
            print(f"!! MISSING from mapping: {old}")
            continue
        h = md5(os.path.join(SRC, old))
        if h in seen_md5:
            skipped_dup.append((old, f"duplicate of {seen_md5[h]}"))
            continue
        seen_md5[h] = new
        dest_dir = os.path.join(ROOT, folder)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, new)
        shutil.move(os.path.join(SRC, old), dest)
        with Image.open(dest) as im:
            w, hh = im.size
            fmt = im.format
        moved.append(dest)
        manifest_rows.append([folder, new, site, url, old, w, hh, fmt, h[:8], conf, notes])

    # delete irrelevant / duplicate leftovers
    for f in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, f)
        if not os.path.isfile(p):
            continue
        reason = IRRELEVANT.get(f, "not catalogued (unidentified/low quality)")
        os.remove(p)
        deleted.append((f, reason))

    # remove empty download scratch dir
    if os.path.isdir("temp_downloads"):
        shutil.rmtree("temp_downloads")

    # write manifest
    with open("image_manifest.csv", "w", newline="", encoding="utf-8") as fh:
        wcsv = csv.writer(fh)
        wcsv.writerow(["folder", "filename", "source_site", "source_url",
                       "original_filename", "width", "height", "format", "md5_8",
                       "confidence", "notes"])
        wcsv.writerows(manifest_rows)

    # summary
    counts = {}
    for r in manifest_rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    print("MOVED:", len(moved))
    for k in ["Ship_Types", "Level_Screens", "Enemy_Types", "Upgrades_UI", "Boss_Fighters", "Backgrounds"]:
        print(f"  {k}: {counts.get(k, 0)}")
    print("SKIPPED AS DUPLICATE:", len(skipped_dup))
    for a, b in skipped_dup:
        print(f"  {a} -> {b}")
    print("DELETED (irrelevant/dupes):", len(deleted))


if __name__ == "__main__":
    main()
