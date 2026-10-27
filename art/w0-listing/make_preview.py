#!/usr/bin/env python3
"""Build preview/w0_contact_sheet.png — every W0 export at review size, labelled.
Also renders two legibility probes required by store guidance:
Amazon promo at 300x146 and the 114px small icon at native size."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG = (0x0B, 0x0E, 0x14)
PAPER = (0xE8, 0xE3, 0xD9)
INK300 = (0x4A, 0x56, 0x6B)

GROUPS = [
    ("MICROSOFT STORE — Windows PC", [
        "microsoft-store/ms_tile_icon_300x300.png",
        "microsoft-store/ms_box_art_1080x1080.png",
        "microsoft-store/ms_poster_art_720x1080.png",
        "microsoft-store/ms_super_hero_1920x1080.png",
        "microsoft-store/ms_screenshot_1_1920x1080.png",
        "microsoft-store/ms_screenshot_2_1920x1080.png",
        "microsoft-store/ms_screenshot_3_1920x1080.png",
        "microsoft-store/ms_screenshot_4_1920x1080.png",
    ]),
    ("AMAZON APPSTORE — Fire tablet", [
        "amazon-appstore/amazon_icon_large_512x512.png",
        "amazon-appstore/amazon_icon_small_114x114.png",
        "amazon-appstore/amazon_promo_1024x500.png",
        "amazon-appstore/amazon_screenshot_1_800x1280.png",
        "amazon-appstore/amazon_screenshot_2_800x1280.png",
        "amazon-appstore/amazon_screenshot_3_800x1280.png",
        "amazon-appstore/amazon_screenshot_4_800x1280.png",
    ]),
    ("HUAWEI APPGALLERY — APK mobile (+ HarmonyOS variant)", [
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

COLW, THUMB_H, PAD, LABEL_H, HEAD_H = 300, 300, 16, 34, 52


def thumb(path):
    im = Image.open(os.path.join(HERE, path)).convert("RGB")
    im.thumbnail((COLW, THUMB_H), Image.LANCZOS)
    cell = Image.new("RGB", (COLW, THUMB_H), (0x16, 0x1C, 0x26))
    cell.paste(im, ((COLW - im.width) // 2, (THUMB_H - im.height) // 2))
    return cell, Image.open(os.path.join(HERE, path)).size


def main():
    cols = 4
    rows_total = sum((len(g[1]) + cols - 1) // cols for g in GROUPS)
    W = cols * COLW + (cols + 1) * PAD
    H = rows_total * (THUMB_H + LABEL_H + PAD) + len(GROUPS) * HEAD_H + PAD + 240
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    f_head = ImageFont.truetype(FONT, 26)
    f_lab = ImageFont.truetype(FONT_R, 15)
    y = PAD
    for title, files in GROUPS:
        d.text((PAD, y + 8), title, font=f_head, fill=PAPER)
        y += HEAD_H
        for i, rel in enumerate(files):
            r, c = divmod(i, cols)
            x = PAD + c * (COLW + PAD)
            yy = y + r * (THUMB_H + LABEL_H + PAD)
            cell, size = thumb(rel)
            sheet.paste(cell, (x, yy))
            d.rectangle([x, yy, x + COLW - 1, yy + THUMB_H - 1], outline=INK300)
            label = f"{os.path.basename(rel)}  ({size[0]}x{size[1]})"
            d.text((x + 2, yy + THUMB_H + 6), label, font=f_lab, fill=PAPER)
        y += ((len(files) + cols - 1) // cols) * (THUMB_H + LABEL_H + PAD)
    # legibility probes
    d.text((PAD, y + 4), "LEGIBILITY PROBES — Amazon promo @300x146 · small icon @114 native · MS tile @96",
           font=f_head, fill=PAPER)
    y += HEAD_H
    promo = Image.open(os.path.join(HERE, "amazon-appstore/amazon_promo_1024x500.png")).resize((300, 146), Image.LANCZOS)
    sheet.paste(promo, (PAD, y))
    sic = Image.open(os.path.join(HERE, "amazon-appstore/amazon_icon_small_114x114.png")).convert("RGB")
    sheet.paste(sic, (PAD + 330, y))
    tile = Image.open(os.path.join(HERE, "microsoft-store/ms_tile_icon_300x300.png")).resize((96, 96), Image.LANCZOS)
    sheet.paste(tile, (PAD + 480, y))
    out = os.path.join(HERE, "preview", "w0_contact_sheet.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out, "PNG", optimize=True)
    print(out, sheet.size, f"{os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    main()
