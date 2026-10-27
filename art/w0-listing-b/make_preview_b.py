#!/usr/bin/env python3
"""
Build preview/w0_contact_sheet.png — all 25 W0-LISTING Variant B exports arranged
in the exact same 3-store 4-column layout as Variant A for effortless A/B comparison,
with non-overlapping labels + store-mandated legibility probes (Amazon promo @300x146,
Amazon small icon @114x114 native, MS tile @96x96, Huawei icon @72x72).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (11, 22, 54)          # deep royal arcade navy so bright thumbnails pop cleanly
CELL_BG = (18, 36, 84)
BORDER = (0, 210, 255)
GOLD = (255, 218, 36)
WHITE = (245, 250, 255)
MUTED = (176, 206, 245)

GROUPS = [
    ("MICROSOFT STORE — Windows PC (8 slots)", [
        "microsoft-store/ms_tile_icon_300x300.png",
        "microsoft-store/ms_box_art_1080x1080.png",
        "microsoft-store/ms_poster_art_720x1080.png",
        "microsoft-store/ms_super_hero_1920x1080.png",
        "microsoft-store/ms_screenshot_1_1920x1080.png",
        "microsoft-store/ms_screenshot_2_1920x1080.png",
        "microsoft-store/ms_screenshot_3_1920x1080.png",
        "microsoft-store/ms_screenshot_4_1920x1080.png",
    ]),
    ("AMAZON APPSTORE — Fire tablet (7 slots)", [
        "amazon-appstore/amazon_icon_large_512x512.png",
        "amazon-appstore/amazon_icon_small_114x114.png",
        "amazon-appstore/amazon_promo_1024x500.png",
        "amazon-appstore/amazon_screenshot_1_800x1280.png",
        "amazon-appstore/amazon_screenshot_2_800x1280.png",
        "amazon-appstore/amazon_screenshot_3_800x1280.png",
        "amazon-appstore/amazon_screenshot_4_800x1280.png",
    ]),
    ("HUAWEI APPGALLERY — APK mobile + HarmonyOS variant (10 slots)", [
        "huawei-appgallery/huawei_icon_512x512.png",
        "huawei-appgallery/huawei_icon_216x216.png",
        "huawei-appgallery/huawei_screenshot_1_450x800.png",
        "huawei-appgallery/huawei_screenshot_2_450x800.png",
        "huawei-appgallery/huawei_screenshot_3_450x800.png",
        "huawei-appgallery/huawei_screenshot_4_450x800.png",
        "huawei-appgallery/huawei_screenshot_1_720x1280.png",
        "huawei-appgallery/huawei_screenshot_2_720x1280.png",
        "huawei-appgallery/huawei_screenshot_3_720x1280.png",
        "huawei-appgallery/huawei_screenshot_4_720x1280.png",
    ]),
]

COLS = 4
COLW = 360
THUMB_H = 300
PAD = 20
LABEL_H = 48
HEAD_H = 54
BANNER_H = 88


def make_thumb(relpath):
    full = os.path.join(HERE, relpath)
    src = Image.open(full)
    orig_size = src.size
    kb = os.path.getsize(full) // 1024
    im = src.convert("RGB")
    im.thumbnail((COLW - 8, THUMB_H - 8), Image.LANCZOS)
    cell = Image.new("RGB", (COLW, THUMB_H), CELL_BG)
    cell.paste(im, ((COLW - im.width) // 2, (THUMB_H - im.height) // 2))
    return cell, orig_size, src.mode, kb


def main():
    rows_total = sum((len(files) + COLS - 1) // COLS for _, files in GROUPS)
    W = COLS * COLW + (COLS + 1) * PAD
    H = BANNER_H + rows_total * (THUMB_H + LABEL_H + PAD) + len(GROUPS) * HEAD_H + PAD + 250

    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)

    f_banner = ImageFont.truetype(FONT_B, 30)
    f_sub = ImageFont.truetype(FONT_R, 17)
    f_head = ImageFont.truetype(FONT_B, 24)
    f_lab1 = ImageFont.truetype(FONT_B, 14)
    f_lab2 = ImageFont.truetype(FONT_R, 13)

    # Top header banner
    d.rectangle([0, 0, W, BANNER_H], fill=(15, 34, 88))
    d.line([(0, BANNER_H - 2), (W, BANNER_H - 2)], fill=BORDER, width=3)
    d.text((PAD, 16), "W0-LISTING — VARIANT B  ·  SOLAR NEON ARCADE-POP  (25 SLOTS)", font=f_banner, fill=GOLD)
    d.text(
        (PAD, 54),
        "Role: Art-designer-B  |  Branch: arena/eca8588b-windwings-space-shooter-game-p  |  9 Original Masters -> 25 Exact Store Slots",
        font=f_sub,
        fill=MUTED,
    )

    y = BANNER_H + PAD // 2
    for title, files in GROUPS:
        d.text((PAD, y + 12), title, font=f_head, fill=GOLD)
        d.line([(PAD, y + HEAD_H - 6), (W - PAD, y + HEAD_H - 6)], fill=(40, 88, 165), width=2)
        y += HEAD_H
        for i, rel in enumerate(files):
            r, c = divmod(i, COLS)
            x = PAD + c * (COLW + PAD)
            yy = y + r * (THUMB_H + LABEL_H + PAD)
            cell, size, mode, kb = make_thumb(rel)
            sheet.paste(cell, (x, yy))
            d.rectangle([x, yy, x + COLW - 1, yy + THUMB_H - 1], outline=BORDER, width=2)
            fname = os.path.basename(rel)
            d.text((x + 2, yy + THUMB_H + 5), fname, font=f_lab1, fill=WHITE)
            d.text((x + 2, yy + THUMB_H + 24), f"{size[0]}x{size[1]} px  ·  {mode}  ·  {kb} KB", font=f_lab2, fill=MUTED)
        y += ((len(files) + COLS - 1) // COLS) * (THUMB_H + LABEL_H + PAD)

    # Store-mandated legibility probes
    d.text(
        (PAD, y + 8),
        "LEGIBILITY PROBES — Amazon promo @300x146  ·  Amazon icon @114 native  ·  MS tile @96  ·  Huawei icon @72",
        font=f_head,
        fill=GOLD,
    )
    d.line([(PAD, y + HEAD_H - 6), (W - PAD, y + HEAD_H - 6)], fill=(40, 88, 165), width=2)
    y += HEAD_H + 6

    promo = Image.open(os.path.join(HERE, "amazon-appstore/amazon_promo_1024x500.png")).resize((300, 146), Image.LANCZOS)
    sheet.paste(promo, (PAD, y))
    d.rectangle([PAD, y, PAD + 299, y + 145], outline=BORDER, width=1)
    d.text((PAD, y + 152), "amazon_promo @ 300x146", font=f_lab2, fill=MUTED)

    sic = Image.open(os.path.join(HERE, "amazon-appstore/amazon_icon_small_114x114.png")).convert("RGB")
    sheet.paste(sic, (PAD + 340, y))
    d.rectangle([PAD + 340, y, PAD + 340 + 113, y + 113], outline=BORDER, width=1)
    d.text((PAD + 340, y + 120), "114x114 native", font=f_lab2, fill=MUTED)

    tile = Image.open(os.path.join(HERE, "microsoft-store/ms_tile_icon_300x300.png")).resize((96, 96), Image.LANCZOS)
    sheet.paste(tile, (PAD + 500, y))
    d.rectangle([PAD + 500, y, PAD + 500 + 95, y + 95], outline=BORDER, width=1)
    d.text((PAD + 500, y + 102), "MS tile @ 96x96", font=f_lab2, fill=MUTED)

    hw72 = Image.open(os.path.join(HERE, "huawei-appgallery/huawei_icon_216x216.png")).resize((72, 72), Image.LANCZOS)
    sheet.paste(hw72, (PAD + 640, y))
    d.rectangle([PAD + 640, y, PAD + 640 + 71, y + 71], outline=BORDER, width=1)
    d.text((PAD + 640, y + 78), "Huawei @ 72x72", font=f_lab2, fill=MUTED)

    out = os.path.join(HERE, "preview", "w0_contact_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out, "PNG", compress_level=9)
    print(f"{out}  {sheet.size}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
