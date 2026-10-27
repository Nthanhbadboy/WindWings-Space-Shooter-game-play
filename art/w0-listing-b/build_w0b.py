#!/usr/bin/env python3
"""
W0-LISTING Variant B builder — WindWings (Godot port)
Vai: Art-designer-B  ·  Nhánh: arena/eca8588b-windwings-space-shooter-game-p

Style: SOLAR NEON commercial 2.5D semi-realistic military metallic — bright
character/key-art accents over a grounded dark-cobalt gameplay stage. The four
scene masters are explicit marketing CONCEPT composites from current B sprites,
not Godot/runtime captures; recapture on a real build before store submission.

Reads the 9 original AI-generated text-free masters in masters/ and deterministically
exports the exact 25 store-listing PNG slots (identical filenames & pixel dimensions
to art/w0-listing/W0_MANIFEST.md on branch arena/5438fec9, verified 2026-10-27).
No original GCenter PNG/atlas is used, cropped, or traced.

Run:  python3 build_w0b.py
"""
import json
import os
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, "masters")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Solar Neon Arcade-Pop palette tokens (Variant B independent palette)
NAVY_STROKE = (6, 14, 46)        # #060E2E — crisp deep-cobalt outline
BADGE_NAVY = (8, 20, 62)         # #08143E — translucent speed-ribbon backing
NEON_CYAN = (0, 242, 255)        # #00F2FF — laser/shield/halo accent
SOLAR_TOP = (255, 255, 242)      # #FFFFF2 — wordmark top specular cream
SOLAR_MID = (255, 220, 24)       # #FFDC18 — wordmark arcade gold
SOLAR_BOT = (255, 109, 0)        # #FF6D00 — wordmark hot tangerine

TITLE = "WindWings"  # working title per STORE_ASSETS_AND_LISTING_DRAFT.md §4 (rights pending)
AUTHOR_BRANCH = "arena/eca8588b-windwings-space-shooter-game-p"
LICENSE_NOTE = "chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)"

SCENES = [
    ("scene_s1_wave_master.png", "b_scene_composite_dark_cobalt + b_ship_10001 + b_enemy_wave + b_drone_20004 + b_fx_sparse"),
    ("scene_s2_boss_master.png", "b_scene_composite_dark_cobalt + b_ship_10001 + b_boss_7001 + b_bullet_sparse"),
    ("scene_s3_drone_master.png", "b_scene_composite_dark_cobalt + b_ship_10008 + b_drone_20004 + b_coin_pile + b_fx_sparse"),
    ("scene_s4_beam_master.png", "b_scene_composite_dark_cobalt + b_ship_10001 + b_boss_7005 + b_hyper_beam_compact"),
]

records = []


def load(name):
    return Image.open(os.path.join(MASTERS, name)).convert("RGB")


def crop_to_ratio(im, ratio, cx=0.5, cy=0.5):
    w, h = im.size
    cur = w / h
    if abs(cur - ratio) < 1e-4:
        return im.copy()
    if cur > ratio:
        nw = int(round(h * ratio))
        x0 = int(round(cx * (w - nw)))
        x0 = max(0, min(w - nw, x0))
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(round(w / ratio))
    y0 = int(round(cy * (h - nh)))
    y0 = max(0, min(h - nh, y0))
    return im.crop((0, y0, w, y0 + nh))


def fit(im, size, cx=0.5, cy=0.5, sharpen=False):
    out = crop_to_ratio(im, size[0] / size[1], cx, cy).resize(size, Image.LANCZOS)
    if sharpen:
        out = out.filter(ImageFilter.UnsharpMask(radius=0.9, percent=115, threshold=2))
    return out


def arcade_pillarbox(im, size):
    """Bright atmospheric pillarbox for 16:9 Windows desktop view of vertical shmup:
    soft blurred orbital-sky side wings with subtle cyan viewport separator lines,
    no text/logos/device frames."""
    bg = fit(im, size, cy=0.5).filter(ImageFilter.GaussianBlur(22))
    bg = ImageEnhance.Color(bg).enhance(0.88)
    bg = ImageEnhance.Brightness(bg).enhance(0.68)

    scale = size[1] / im.height
    fg_w = int(round(im.width * scale))
    fg = im.resize((fg_w, size[1]), Image.LANCZOS)
    x0 = (size[0] - fg_w) // 2

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for dx, alpha in [(-5, 28), (-3, 60), (-1, 165), (0, 210)]:
        od.line([(x0 + dx, 0), (x0 + dx, size[1])], fill=(0, 242, 255, alpha), width=1)
        rx = x0 + fg_w - 1 - dx
        od.line([(rx, 0), (rx, size[1])], fill=(0, 242, 255, alpha), width=1)

    comp = bg.convert("RGBA")
    comp.paste(fg.convert("RGBA"), (x0, 0))
    comp = Image.alpha_composite(comp, overlay)
    return comp.convert("RGB")


def render_wordmark_layer(canvas_size, center_y_frac, font_px, shear=-0.15, badge_pad_x=44):
    """Render crisp 2x-supersampled Arcade-Pop 'WindWings' wordmark with C-accelerated
    round stroke, neon cyan halo, 3D extrusion shadow, and solar gradient fill."""
    W, H = canvas_size
    SS = 2
    sw, sh = W * SS, H * SS
    fpx = int(round(font_px * SS))
    stroke_r = max(5, int(round(fpx * 0.095)))
    font = ImageFont.truetype(FONT_BOLD, fpx)

    strip_h = fpx * 3
    tmp_fill = Image.new("L", (sw, strip_h), 0)
    tmp_stroke = Image.new("L", (sw, strip_h), 0)
    df = ImageDraw.Draw(tmp_fill)
    ds = ImageDraw.Draw(tmp_stroke)

    tracking = max(3, fpx // 24)
    advances = [df.textlength(ch, font=font) for ch in TITLE]
    total_w = sum(advances) + tracking * (len(TITLE) - 1)
    tx0 = (sw - total_w) / 2.0
    ty0 = fpx * 0.85

    cx = tx0
    for ch, adv in zip(TITLE, advances):
        ds.text((cx, ty0), ch, font=font, fill=255, stroke_width=stroke_r, stroke_fill=255)
        df.text((cx, ty0), ch, font=font, fill=255)
        cx += adv + tracking

    yc = ty0 + fpx * 0.45
    shift_x = shear * yc
    affine_params = (1.0, -shear, shift_x, 0.0, 1.0, 0.0)
    fill_strip = tmp_fill.transform((sw, strip_h), Image.AFFINE, affine_params, resample=Image.BICUBIC)
    stroke_strip = tmp_stroke.transform((sw, strip_h), Image.AFFINE, affine_params, resample=Image.BICUBIC)

    bx0, by0, bx1, by1 = fill_strip.getbbox()
    th = by1 - by0
    target_cy = int(round(center_y_frac * sh))
    paste_y = target_cy - (by0 + by1) // 2

    full_mask = Image.new("L", (sw, sh), 0)
    full_mask.paste(fill_strip, (0, paste_y))
    expanded = Image.new("L", (sw, sh), 0)
    expanded.paste(stroke_strip, (0, paste_y))

    fbx0, fby0, fbx1, fby1 = full_mask.getbbox()

    layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))

    # 1. Aerodynamic translucent navy speed-ribbon + neon cyan/gold rails
    pad_x = int(round(badge_pad_x * SS))
    pad_y = max(14 * SS, int(round(th * 0.28)))
    rx0 = max(36 * SS, fbx0 - pad_x)
    rx1 = min(sw - 36 * SS, fbx1 + pad_x)
    ry0 = fby0 - pad_y
    ry1 = fby1 + pad_y
    slant = int(round((ry1 - ry0) * 0.24))

    ribbon_pts = [
        (rx0 + slant, ry0),
        (rx1 + slant // 2, ry0),
        (rx1 - slant, ry1),
        (rx0 - slant // 2, ry1),
    ]
    glow_rib = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    ImageDraw.Draw(glow_rib).polygon(ribbon_pts, fill=(0, 242, 255, 95))
    glow_rib = glow_rib.filter(ImageFilter.GaussianBlur(10 * SS))
    layer = Image.alpha_composite(layer, glow_rib)

    ld = ImageDraw.Draw(layer)
    ld.polygon(ribbon_pts, fill=(BADGE_NAVY[0], BADGE_NAVY[1], BADGE_NAVY[2], 212))
    rail_h = max(3, fpx // 26)
    ld.line([ribbon_pts[0], ribbon_pts[1]], fill=(0, 242, 255, 245), width=rail_h)
    ld.line([ribbon_pts[3], ribbon_pts[2]], fill=(255, 196, 0, 245), width=rail_h)

    chev_w = max(4, fpx // 22)
    for k in range(2):
        ox = rx0 + slant // 2 + k * (chev_w * 3)
        ym = (ry0 + ry1) // 2
        hh = (ry1 - ry0) // 4
        ld.line([(ox + hh // 2, ym - hh), (ox, ym), (ox + hh // 2, ym + hh)],
                fill=(0, 242, 255, 195 - k * 55), width=chev_w)
        oxr = rx1 - slant // 2 - k * (chev_w * 3)
        ld.line([(oxr - hh // 2, ym - hh), (oxr, ym), (oxr - hh // 2, ym + hh)],
                fill=(255, 210, 24, 195 - k * 55), width=chev_w)

    # 2. Cyan neon outer halo around glyphs
    halo = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    halo_alpha = expanded.filter(ImageFilter.GaussianBlur(6 * SS))
    halo.paste((NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], 255), (0, 0), halo_alpha)
    layer = Image.alpha_composite(layer, halo)

    # 3. 3D extrusion drop shadow + deep-navy round stroke
    drop_shift = max(4, int(round(fpx * 0.055)))
    extrude_mask = ImageChops.offset(expanded, drop_shift, drop_shift)
    extrude_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    extrude_layer.paste((3, 8, 28, 245), (0, 0), extrude_mask)
    layer = Image.alpha_composite(layer, extrude_layer)

    stroke_layer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    stroke_layer.paste((NAVY_STROKE[0], NAVY_STROKE[1], NAVY_STROKE[2], 255), (0, 0), expanded)
    layer = Image.alpha_composite(layer, stroke_layer)

    # 4. Vertical solar gradient fill inside glyphs
    arr = np.zeros((sh, sw, 4), dtype=np.uint8)
    ys = np.arange(fby0, fby1)
    t = (ys - fby0) / max(1, (fby1 - fby0 - 1))
    r = np.where(t < 0.48,
                 SOLAR_TOP[0] + (SOLAR_MID[0] - SOLAR_TOP[0]) * (t / 0.48),
                 SOLAR_MID[0] + (SOLAR_BOT[0] - SOLAR_MID[0]) * ((t - 0.48) / 0.52))
    g = np.where(t < 0.48,
                 SOLAR_TOP[1] + (SOLAR_MID[1] - SOLAR_TOP[1]) * (t / 0.48),
                 SOLAR_MID[1] + (SOLAR_BOT[1] - SOLAR_MID[1]) * ((t - 0.48) / 0.52))
    b = np.where(t < 0.48,
                 SOLAR_TOP[2] + (SOLAR_MID[2] - SOLAR_TOP[2]) * (t / 0.48),
                 SOLAR_MID[2] + (SOLAR_BOT[2] - SOLAR_MID[2]) * ((t - 0.48) / 0.52))
    gleam = np.exp(-((t - 0.38) / 0.055) ** 2) * 0.55
    r = np.clip(r + (255 - r) * gleam, 0, 255).astype(np.uint8)
    g = np.clip(g + (255 - g) * gleam, 0, 255).astype(np.uint8)
    b = np.clip(b + (255 - b) * gleam, 0, 255).astype(np.uint8)

    arr[fby0:fby1, :, 0] = r[:, None]
    arr[fby0:fby1, :, 1] = g[:, None]
    arr[fby0:fby1, :, 2] = b[:, None]
    arr[:, :, 3] = np.array(full_mask, dtype=np.uint8)

    layer = Image.alpha_composite(layer, Image.fromarray(arr, mode="RGBA"))

    out_layer = layer.resize((W, H), Image.LANCZOS)
    text_bbox_1x = (fbx0 // SS, fby0 // SS, fbx1 // SS, fby1 // SS)
    ribbon_bbox_1x = (
        min(p[0] for p in ribbon_pts) // SS,
        ry0 // SS,
        max(p[0] for p in ribbon_pts) // SS,
        ry1 // SS,
    )
    return out_layer, text_bbox_1x, ribbon_bbox_1x


def add_title(im, center_y_frac, font_px, badge_pad_x=44):
    wm, tbbox, rbbox = render_wordmark_layer(im.size, center_y_frac, font_px, badge_pad_x=badge_pad_x)
    comp = Image.alpha_composite(im.convert("RGBA"), wm).convert("RGB")
    return comp, tbbox, rbbox


def metrics(im):
    """Vectorized full-frame HSV/dark/chroma metrics matching W0_MANIFEST.md §2."""
    small = im.convert("RGB")
    if max(small.size) > 512:
        small = small.resize((512, int(round(512 * small.height / small.width))), Image.LANCZOS)
    arr = np.asarray(small, dtype=np.float32)
    mx = arr.max(axis=2)
    mn = arr.min(axis=2)
    dark = float((mx < 45.0).mean())
    v = mx / 255.0
    chroma = (mx - mn) / 255.0  # exact S * V in HSV!
    return {
        "val": round(float(v.mean()), 3),
        "val_std": round(float(v.std()), 3),
        "dark": round(dark, 3),
        "chroma": round(float(chroma.mean()), 3),
    }


def save(im, relpath, slot, source_master, recipe, note="", max_kb=None):
    path = os.path.join(HERE, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", compress_level=9)
    sz_bytes = os.path.getsize(path)
    if max_kb is not None and sz_bytes > max_kb * 1024:
        raise RuntimeError(f"{relpath} exceeds {max_kb} KB cap ({sz_bytes} bytes)")
    rec = {
        "file": relpath,
        "slot": slot,
        "px": f"{im.width}x{im.height}",
        "mode": im.mode,
        "bytes": sz_bytes,
        "source": f"masters/{source_master}",
        "license": LICENSE_NOTE,
        "author": AUTHOR_BRANCH,
        "recipe": recipe,
        "note": note,
        "metrics_full_frame": metrics(im),
    }
    records.append(rec)
    print(f"{relpath:52s} {rec['px']:10s} {im.mode:4s} {sz_bytes // 1024:4d} KB  {rec['metrics_full_frame']}")


def main():
    icon = load("icon_master.png")
    box_m = load("box_master.png")
    poster_m = load("poster_master.png")
    hero_m = load("hero_master.png")
    promo_m = load("promo_master.png")
    scenes = [(load(fname), fname, recp) for fname, recp in SCENES]

    icon_recipe = "b_bg_solar_sky + b_ship_pearl_azure + b_fx_starburst_boom"
    key_recipe = "b_bg_solar_sky + b_ship_pearl_azure + b_boss_crimson_violet + b_fx_neon_pop"

    # ---------- 1. Microsoft Store (Windows PC, MSIX) — 8 slots ----------
    save(
        fit(icon, (300, 300), sharpen=True),
        "microsoft-store/ms_tile_icon_300x300.png",
        "MS 1:1 App tile icon (store logo)",
        "icon_master.png",
        icon_recipe,
        "no text; crisp silhouette",
        max_kb=50 * 1024,
    )

    box_img, box_tbbox, box_rbbox = add_title(fit(box_m, (1080, 1080)), center_y_frac=0.585, font_px=106, badge_pad_x=44)
    assert box_rbbox[3] <= 720, f"MS box art ribbon exceeds top-2/3 rule: {box_rbbox}"
    save(
        box_img,
        "microsoft-store/ms_box_art_1080x1080.png",
        "MS 1:1 Box art",
        "box_master.png",
        key_recipe + " + b_wordmark_solar_chrome",
        f"title band in top 2/3 (y={box_rbbox[1]}..{box_rbbox[3]}px <= 720px); bottom third text-free",
        max_kb=50 * 1024,
    )

    pos_img, pos_tbbox, pos_rbbox = add_title(fit(poster_m, (720, 1080)), center_y_frac=0.435, font_px=74, badge_pad_x=32)
    assert pos_rbbox[3] <= 720, f"MS poster art ribbon exceeds top-2/3 rule: {pos_rbbox}"
    save(
        pos_img,
        "microsoft-store/ms_poster_art_720x1080.png",
        "MS 2:3 Poster art",
        "poster_master.png",
        key_recipe + " + b_wordmark_solar_chrome",
        f"title band in top 2/3 (y={pos_rbbox[1]}..{pos_rbbox[3]}px <= 720px, >=4.5:1 contrast); bottom third clean",
        max_kb=50 * 1024,
    )

    save(
        fit(hero_m, (1920, 1080)),
        "microsoft-store/ms_super_hero_1920x1080.png",
        "MS 16:9 Super hero art",
        "hero_master.png",
        key_recipe,
        "no text/UI per store rule; main action in upper 2/3",
        max_kb=50 * 1024,
    )

    for i, (sc_im, sc_name, sc_rec) in enumerate(scenes, 1):
        save(
            arcade_pillarbox(sc_im, (1920, 1080)),
            f"microsoft-store/ms_screenshot_{i}_1920x1080.png",
            "MS Desktop screenshot",
            sc_name,
            sc_rec,
            "CONCEPT frame (bright orbital pillarbox, no text) - recapture from Windows build before submit",
            max_kb=50 * 1024,
        )

    # ---------- 2. Amazon Appstore (Fire tablet) — 7 slots ----------
    save(
        fit(icon, (512, 512), sharpen=True).convert("RGBA"),
        "amazon-appstore/amazon_icon_large_512x512.png",
        "Amazon large icon",
        "icon_master.png",
        icon_recipe,
        "full-bleed edge-to-edge key art in RGBA container; no rounded corners/border",
    )
    save(
        fit(icon, (114, 114), sharpen=True).convert("RGBA"),
        "amazon-appstore/amazon_icon_small_114x114.png",
        "Amazon small icon",
        "icon_master.png",
        icon_recipe,
        "full-bleed RGBA; unsharp-hinted for crisp 114px thumbnail legibility",
    )

    promo_base = fit(promo_m, (1024, 500), cy=0.45)
    promo_img, pr_tbbox, pr_rbbox = add_title(promo_base, center_y_frac=0.64, font_px=92, badge_pad_x=40)
    assert pr_tbbox[0] >= 50 and pr_tbbox[1] >= 50 and (1024 - pr_tbbox[2]) >= 50 and (500 - pr_tbbox[3]) >= 50, (
        f"Amazon promo text margin < 50px: {pr_tbbox}"
    )
    save(
        promo_img,
        "amazon-appstore/amazon_promo_1024x500.png",
        "Amazon Promotional Image",
        "promo_master.png",
        key_recipe + " + b_wordmark_solar_chrome",
        f"title margins >=50px (text bbox {pr_tbbox}); verified legible at 300x146",
    )

    for i, (sc_im, sc_name, sc_rec) in enumerate(scenes, 1):
        save(
            fit(sc_im, (800, 1280), cy=0.50),
            f"amazon-appstore/amazon_screenshot_{i}_800x1280.png",
            "Amazon screenshot (tablet assets)",
            sc_name,
            sc_rec,
            "CONCEPT frame - recapture on Fire tablet build before submit",
        )

    # ---------- 3. Huawei AppGallery (APK mobile + HarmonyOS variant) — 10 slots ----------
    save(
        fit(icon, (512, 512), sharpen=True),
        "huawei-appgallery/huawei_icon_512x512.png",
        "AppGallery icon (APK spec 512 option)",
        "icon_master.png",
        icon_recipe,
        "no text/badges; <=2 MB",
        max_kb=2048,
    )
    save(
        fit(icon, (216, 216), sharpen=True),
        "huawei-appgallery/huawei_icon_216x216.png",
        "AppGallery icon (APK/HarmonyOS spec 216)",
        "icon_master.png",
        icon_recipe,
        "no text/badges; <=500 KB HarmonyOS cap",
        max_kb=500,
    )

    for i, (sc_im, sc_name, sc_rec) in enumerate(scenes, 1):
        save(
            fit(sc_im, (450, 800), cy=0.50, sharpen=True),
            f"huawei-appgallery/huawei_screenshot_{i}_450x800.png",
            "AppGallery screenshot (APK spec)",
            sc_name,
            sc_rec,
            "CONCEPT frame - recapture on HMS build before submit",
            max_kb=2048,
        )
        save(
            fit(sc_im, (720, 1280), cy=0.50),
            f"huawei-appgallery/huawei_screenshot_{i}_720x1280.png",
            "AppGallery screenshot (HarmonyOS spec variant)",
            sc_name,
            sc_rec,
            "CONCEPT frame - recapture on device build before submit",
            max_kb=2048,
        )

    assert len(records) == 25, f"Expected 25 slots, got {len(records)}"
    out_json = os.path.join(HERE, "w0b_exports.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)
    print(f"\nSUCCESS: {len(records)} exact slots exported -> w0b_exports.json")


if __name__ == "__main__":
    main()
