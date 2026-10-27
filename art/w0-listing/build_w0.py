#!/usr/bin/env python3
"""
W0 listing-art builder — WindWings (Godot port)  ·  vai Art-designer · arena/5438fec9

Takes the 7 AI-generated masters in masters/ (original art drawn to the Ink & Ember
palette + recipes of docs/art-plan/ART_REDRAW_PLAN.md @971a7eea, branch 1b836828)
and exports exact-pixel store files for Microsoft Store / Amazon Appstore /
Huawei AppGallery. Store sizes verified against official docs on 2026-10-27
(see W0_MANIFEST.md for source URLs). No original-game PNG/atlas is used as an asset.

Run:  python3 build_w0.py            (needs Pillow)
Outputs are deterministic from the masters; re-running overwrites exports.
"""
import colorsys
import json
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, "masters")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Ink & Ember (ART_REDRAW_PLAN §4.4)
INK_900 = (0x0B, 0x0E, 0x14)
PAPER = (0xE8, 0xE3, 0xD9)
EMBER = (0xFF, 0x5A, 0x2B)

TITLE = "WindWings"  # working title per STORE_ASSETS_AND_LISTING_DRAFT §4 (rights pending)

SCENES = ["scene_s1_wave_master.png", "scene_s2_boss_master.png",
          "scene_s3_drone_master.png", "scene_s4_beam_master.png"]

records = []  # for manifest/metrics dump


def load(name):
    return Image.open(os.path.join(MASTERS, name)).convert("RGB")


def crop_to_ratio(im, ratio, cx=0.5, cy=0.5):
    """Crop im to width/height == ratio, crop window centered at (cx, cy) fractions."""
    w, h = im.size
    cur = w / h
    if cur > ratio:  # too wide -> trim sides
        nw = int(h * ratio)
        x0 = int(cx * (w - nw))
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / ratio)
    y0 = int(cy * (h - nh))
    return im.crop((0, y0, w, y0 + nh))


def fit(im, size, cx=0.5, cy=0.5):
    return crop_to_ratio(im, size[0] / size[1], cx, cy).resize(size, Image.LANCZOS)


def pillarbox(im, size):
    """Portrait scene centered on a blurred, darkened zoom of itself (landscape frame)."""
    bg = fit(im, size).filter(ImageFilter.GaussianBlur(18))
    bg = bg.point(lambda v: int(v * 0.45))
    scale = size[1] / im.height
    fg = im.resize((int(im.width * scale), size[1]), Image.LANCZOS)
    bg.paste(fg, ((size[0] - fg.width) // 2, 0))
    return bg


def draw_title(im, center_y_frac, font_px, tracking=6):
    """Draw TITLE centered horizontally with middle near center_y_frac of height."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT_BOLD, font_px)
    # measure with manual tracking
    widths = [d.textlength(ch, font=font) for ch in TITLE]
    total = sum(widths) + tracking * (len(TITLE) - 1)
    x = (im.width - total) / 2
    y = center_y_frac * im.height - font_px * 0.62
    for ch, cw in zip(TITLE, widths):
        d.text((x + 3, y + 3), ch, font=font, fill=INK_900)  # soft seat shadow
        d.text((x, y), ch, font=font, fill=PAPER)
        x += cw + tracking
    # ember rule under title
    rule_y = y + font_px * 1.25
    d.rectangle([(im.width - total) / 2, rule_y,
                 (im.width + total) / 2, rule_y + max(3, font_px // 14)], fill=EMBER)
    return im


def metrics(im):
    """Plan §4.9 steps 3-5 adapted to opaque listing frames (full-frame, no alpha mask):
    val/val_std from HSV V; dark = share max(R,G,B)<45; chroma = mean(S*V)."""
    small = im.convert("RGB")
    if max(small.size) > 512:
        small = small.resize((512, int(512 * small.height / small.width)), Image.LANCZOS)
    px = list(small.getdata())
    n = len(px)
    vals, chromas, dark = [], [], 0
    for r, g, b in px:
        mx = max(r, g, b)
        if mx < 45:
            dark += 1
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        vals.append(v)
        chromas.append(s * v)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    return {"val": round(mean, 3), "val_std": round(var ** 0.5, 3),
            "dark": round(dark / n, 3), "chroma": round(sum(chromas) / n, 3)}


def save(im, relpath, slot, note=""):
    path = os.path.join(HERE, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", optimize=True)
    rec = {"file": relpath, "slot": slot, "px": f"{im.width}x{im.height}",
           "mode": im.mode, "bytes": os.path.getsize(path), "note": note,
           "metrics_full_frame": metrics(im)}
    records.append(rec)
    print(f"{relpath}  {im.width}x{im.height}  {rec['bytes'] // 1024} KB  {rec['metrics_full_frame']}")


def main():
    icon = load("icon_master.png")
    hero = load("hero_master.png")
    poster = load("poster_master.png")
    scenes = [load(s) for s in SCENES]

    # ---------- Microsoft Store (Windows PC, MSIX) ----------
    # 1:1 app tile icon 300x300 (store logo) — no title
    save(fit(icon, (300, 300)), "microsoft-store/ms_tile_icon_300x300.png",
         "MS 1:1 App tile icon (store logo)")
    # 1:1 box art 1080x1080 — title allowed, keep in top 2/3 (title band ~50%)
    box = draw_title(fit(hero, (1080, 1080)), 0.50, 118)
    save(box, "microsoft-store/ms_box_art_1080x1080.png",
         "MS 1:1 Box art", "title band centered 50% height (top-2/3 rule)")
    # 2:3 poster art 720x1080 — title in calm zone ~60% (still top 2/3, bottom third clean)
    pos = draw_title(fit(poster, (720, 1080)), 0.60, 84)
    save(pos, "microsoft-store/ms_poster_art_720x1080.png",
         "MS 2:3 Poster art", "title band centered 60% height; bottom third text-free")
    # 16:9 super hero art 1920x1080 — NO title/text (store rule)
    save(fit(hero, (1920, 1080)), "microsoft-store/ms_super_hero_1920x1080.png",
         "MS 16:9 Super hero art", "no text per store rule; action centered/upper")
    # Desktop screenshots 1920x1080 x4 — vertical gameplay pillarboxed, no marketing text
    for i, sc in enumerate(scenes, 1):
        save(pillarbox(sc, (1920, 1080)), f"microsoft-store/ms_screenshot_{i}_1920x1080.png",
             "MS Desktop screenshot", "CONCEPT frame - recapture from Windows build before submit")

    # ---------- Amazon Appstore (Fire tablet) ----------
    # Icons: PNG with alpha channel (full-bleed art, alpha=255), edge-to-edge key art
    save(fit(icon, (512, 512)).convert("RGBA"), "amazon-appstore/amazon_icon_large_512x512.png",
         "Amazon large icon", "full-bleed art in RGBA container")
    save(fit(icon, (114, 114)).convert("RGBA"), "amazon-appstore/amazon_icon_small_114x114.png",
         "Amazon small icon", "same bold design; legibility checked at 114px in preview sheet")
    # Promotional image 1024x500 — must include app name; text >=50px from edges
    promo = draw_title(fit(hero, (1024, 500), cy=0.42), 0.52, 92)
    save(promo, "amazon-appstore/amazon_promo_1024x500.png",
         "Amazon Promotional Image", "title centered; >50px edge margin; check 300x146 legibility in preview")
    # Screenshots: portrait reading of allowable 1280x800 -> 800x1280 (min 3, max 10)
    for i, sc in enumerate(scenes, 1):
        save(fit(sc, (800, 1280), cy=0.44), f"amazon-appstore/amazon_screenshot_{i}_800x1280.png",
             "Amazon screenshot (tablet assets)", "CONCEPT frame - recapture on Fire tablet build")

    # ---------- Huawei AppGallery (APK, mobile) ----------
    save(fit(icon, (512, 512)), "huawei-appgallery/huawei_icon_512x512.png",
         "AppGallery icon (APK spec 512 option)")
    save(fit(icon, (216, 216)), "huawei-appgallery/huawei_icon_216x216.png",
         "AppGallery icon (APK/HarmonyOS spec 216)")
    for i, sc in enumerate(scenes, 1):
        save(fit(sc, (450, 800), cy=0.46), f"huawei-appgallery/huawei_screenshot_{i}_450x800.png",
             "AppGallery screenshot (APK spec)", "CONCEPT frame - recapture on HMS build")
        save(fit(sc, (720, 1280), cy=0.46), f"huawei-appgallery/huawei_screenshot_{i}_720x1280.png",
             "AppGallery screenshot (HarmonyOS spec variant)", "CONCEPT frame - recapture on device build")

    with open(os.path.join(HERE, "w0_exports.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)
    print(f"\nTotal exports: {len(records)} -> w0_exports.json")


if __name__ == "__main__":
    main()
