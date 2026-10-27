#!/usr/bin/env python3
"""build_hero.py — quy trình tái tạo hero PLAYER ID 10001, hướng A Ink & Ember.

Chạy:  python3 build_hero.py   (cần Pillow + numpy)
Input: process/gen_raw_v4.png  (ảnh sinh thô, nền magenta #FF00FF, xem PROMPTS.md)
       process/ref_tile01.png  (crop gốc ID 10001 từ docs/assets/contact-sheets/ships-01.jpg)
Output: master/hero_10001_master_1024.png   (nguồn lossless RGBA)
        sprites/player_ship_10001_256@inkember.png (sprite RGBA 256x256)
        preview/*.png, compare/*.png

Không script nào ở đây "vẽ" thay ảnh: toàn bộ hình là sản phẩm của bước sinh ảnh
(xem PROMPTS.md), script chỉ làm key nền -> alpha, unpremultiply despill, crop bbox,
pad vuông đúng footprint gốc, resize LANCZOS và dựng bảng kiểm/đối chiếu.
"""
from __future__ import annotations

import hashlib
import os
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "process" / "gen_raw_v4.png"
REF = HERE / "process" / "ref_tile01.png"
OLD_A = HERE / "process" / "old_a_player_ship_01_256.png"

FOOT = 0.867  # tỉ lệ subject/canvas đo từ ô gốc: 130/150 px trong ships-01.jpg
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def font(sz: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, sz)


def key_magenta(img: Image.Image) -> Image.Image:
    """Nền magenta -> alpha, rồi unpremultiply để bỏ viền hồng (despill).

    Alpha chỉ lấy từ miền NỀN thật: flood-fill (connected component) các pixel
    giống magenta chạm biên ảnh. Nhờ vậy các tông tím/hồng NHỎ bên trong thân
    (bóng đổ của metal) không bị biến thành pixel bán trong suốt.
    """
    from scipy import ndimage

    a = np.asarray(img.convert("RGB")).astype(np.float64)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = np.clip((np.minimum(r, b) - g) / 255.0, 0.0, 1.0)  # 1 = thuần magenta
    cand = m > 0.25
    lab, n = ndimage.label(cand)
    border = np.unique(np.concatenate([lab[0, :], lab[-1, :], lab[:, 0], lab[:, -1]]))
    border = border[border > 0]
    exterior = np.isin(lab, border)
    a_raw = np.where(exterior, 1.0 - m, 1.0)
    # khử halo: nền sinh ra có noise magenta ~2-8% => alpha rau ria 1..63 quanh ship
    alpha = np.clip((a_raw - 0.08) * 1.12, 0.0, 1.0)
    fg = np.zeros_like(a)
    safe = alpha > 1e-3
    for i, bgc in enumerate((255.0, 0.0, 255.0)):
        fg[..., i] = np.where(
            safe & exterior,
            np.clip((a[..., i] - (1.0 - alpha) * bgc) / np.maximum(alpha, 1e-3), 0, 255),
            np.where(exterior, 0.0, a[..., i]))
    out = np.dstack([fg, alpha * 255.0]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ---- grade art-direction v2 (tham số ghi trong MANIFEST.md, không sửa ngưỡng đo) ----
# Mục đích: hướng A tối nhưng ĐỌC ĐƯỢC trên nền gameplay ink900:
#  - nén dải gần-đen [0, SHADOW_TOP] lên [SHADOW_FLOOR, ...] để bỏ viền/AO đen sì
#    (dark_share giảm, outline không còn là viền đen);
#  - gain trung/sáng để tăng trải sáng (val_std) và độ sáng trung bình (val);
#  - nhân bão hoà nhẹ cho miền có màu (ember/hổ phách) để giữ cá tính Ink & Ember.
SHADOW_TOP = float(os.environ.get("GR_SHADOW_TOP", 0.18))
SHADOW_FLOOR = float(os.environ.get("GR_FLOOR", 0.20))
MID_K = float(os.environ.get("GR_MID_K", 1.70))
MID_TOP = float(os.environ.get("GR_MID_TOP", 0.42))
HI_GAIN = float(os.environ.get("GR_HI_GAIN", 1.70))
SAT_BOOST = float(os.environ.get("GR_SAT", 1.02))
V_ADD = float(os.environ.get("GR_ADD", 0.0))


def grade(img: Image.Image) -> Image.Image:
    """S-curve 3 vùng: nâng sàn gần-đen, hạ nhẹ trung độ, tăng sáng vùng sáng.

    Vùng 1 v<SHADOW_TOP   -> [FLOOR, FLOOR+0.05]   (bỏ viền/AO đen sì)
    Vùng 2 [TOP, MID_TOP) -> dốc MID_K < 1         (tách bóng giáp khỏi sáng)
    Vùng 3 >= MID_TOP     -> dốc HI_GAIN > 1       (rim/highlight tách xa => val_std tăng)
    """
    a = np.asarray(img.convert("RGBA")).astype(np.float64)
    rgb, al = a[..., :3], a[..., 3]
    mx = rgb.max(axis=2)
    v = mx / 255.0
    z2_at_top = SHADOW_FLOOR + 0.05
    z3_at_mid = z2_at_top + (MID_TOP - SHADOW_TOP) * MID_K
    v2 = np.where(
        v < SHADOW_TOP,
        SHADOW_FLOOR + (v / max(SHADOW_TOP, 1e-6)) * 0.05,
        np.where(v < MID_TOP,
                 z2_at_top + (v - SHADOW_TOP) * MID_K,
                 z3_at_mid + (v - MID_TOP) * HI_GAIN))
    v2 = np.clip(v2 + V_ADD, 0.0, 1.0)
    k = np.where(mx > 0, v2 / np.maximum(v, 1e-6), 0.0)
    rgb2 = np.clip(rgb * k[..., None], 0, 255)
    mn = rgb2.min(axis=2)
    mx2 = rgb2.max(axis=2)
    s = np.where(mx2 > 0, (mx2 - mn) / np.maximum(mx2, 1e-6), 0.0)
    boost = np.where(s > 0.15, SAT_BOOST, 1.0)
    lum = rgb2.mean(axis=2, keepdims=True)
    rgb3 = np.clip(lum + (rgb2 - lum) * boost[..., None], 0, 255)
    out = np.dstack([rgb3, al]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def subject_bbox(img: Image.Image, thr: int = 8) -> tuple[int, int, int, int]:
    al = np.asarray(img.split()[-1])
    ys, xs = np.where(al > thr)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def fit_canvas(img: Image.Image, side: int, foot: float = FOOT) -> Image.Image:
    """Cắt bbox rồi đặt subject chiếm `foot` cạnh canvas, giữa khung (như ô gốc)."""
    x0, y0, x1, y1 = subject_bbox(img)
    sub = img.crop((x0, y0, x1, y1))
    w, h = sub.size
    target = side * foot
    s = target / max(w, h)
    sub = sub.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(sub, ((side - sub.size[0]) // 2, (side - sub.size[1]) // 2), sub)
    return canvas


def checker(side: int, sq: int = 8) -> Image.Image:
    y, x = np.mgrid[0:side, 0:side]
    v = np.where(((x // sq) + (y // sq)) % 2 == 0, 44, 58).astype(np.uint8)
    return Image.fromarray(np.dstack([v, v, v]), "RGB")


def over(bg: Image.Image, fg: Image.Image, box: tuple[int, int]) -> None:
    bg.paste(fg, box, fg)


def label(d: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, sz: int = 12,
          fill=(232, 227, 217)) -> None:
    d.text(xy, text, font=font(sz), fill=fill)


def main() -> None:
    (HERE / "master").mkdir(exist_ok=True)
    (HERE / "sprites").mkdir(exist_ok=True)
    (HERE / "preview").mkdir(exist_ok=True)
    (HERE / "compare").mkdir(exist_ok=True)

    raw = Image.open(RAW)
    keyed = key_magenta(raw)
    master = fit_canvas(grade(keyed), 1024)
    sprite = master.resize((256, 256), Image.LANCZOS)
    s64 = sprite.resize((64, 64), Image.LANCZOS)
    master.save(HERE / "master" / "hero_10001_master_1024.png")
    sprite.save(HERE / "sprites" / "player_ship_10001_256@inkember.png")

    # ---------------- preview: 64 px HIỂN THỊ THẬT (1:1) ----------------
    ref64 = fit_canvas(Image.open(REF).convert("RGBA"), 64)
    olda = Image.open(OLD_A).convert("RGBA") if OLD_A.exists() else None
    olda64 = olda.resize((64, 64), Image.LANCZOS) if olda else None

    W, H = 760, 300
    board = Image.new("RGB", (W, H), (11, 14, 20))
    d = ImageDraw.Draw(board)
    label(d, (16, 12), "64x64 HIEN THI THAT (1:1) — khong phong to.  Xem o 100% zoom.", 14)
    label(d, (16, 32), "hang 1: nen caro (kiem alpha/vien)   hang 2: nen gameplay ink900 (kiem do doc)", 12,
          fill=(150, 158, 170))
    cols = [("A moi · hero 10001", s64), ("GOC · ships-01.jpg #1 = ID 10001", ref64)]
    if olda64:
        cols.append(("A cu @125e1e33 · cung slot", olda64))
    for i, (name, im64) in enumerate(cols):
        x = 24 + i * 240
        cb = checker(64)
        cb.paste(im64, (0, 0), im64)
        board.paste(cb, (x, 60))
        dark = Image.new("RGB", (64, 64), (11, 14, 20))
        dark.paste(im64, (0, 0), im64)
        board.paste(dark, (x, 150))
        label(d, (x, 226), name, 12)
        label(d, (x, 244), "64 px that", 11, fill=(150, 158, 170))
    board.save(HERE / "preview" / "verify_64_true_size.png")

    # ---------------- preview: zoom 4x (nearest) + 256 1:1 ----------------
    z = s64.resize((256, 256), Image.NEAREST)
    W, H = 860, 330
    zb = Image.new("RGB", (W, H), (11, 14, 20))
    d = ImageDraw.Draw(zb)
    label(d, (16, 12), "TRAI: ban 64 px PHONG TO 4x (nearest) CHI de soi chi tiet.", 14)
    label(d, (16, 32), "PHAI: ban xuat 256 px hien thi 1:1.  Khong dung anh 4x lam bang chung 64 px.", 12,
          fill=(150, 158, 170))
    cb = checker(256)
    cb.paste(z, (0, 0), z)
    zb.paste(cb, (24, 60))
    label(d, (24, 322), "64 px -> 4x nearest", 12)
    cb2 = checker(256)
    cb2.paste(sprite, (0, 0), sprite)
    zb.paste(cb2, (320, 60))
    label(d, (320, 322), "sprite xuat 256 px (1:1)", 12)
    zb.save(HERE / "preview" / "zoom_4x_and_256.png")

    # ---------------- preview: alpha / silhouette / vien ----------------
    al = np.asarray(sprite.split()[-1])
    sil = (al > 127).astype(np.uint8) * 255
    pad = np.pad(sil, 1)
    edge = ((pad[1:-1, 1:-1] > 0) & ~((pad[:-2, 1:-1] > 0) & (pad[2:, 1:-1] > 0)
                                     & (pad[1:-1, :-2] > 0) & (pad[1:-1, 2:] > 0))).astype(np.uint8) * 255
    W, H = 860, 330
    ab = Image.new("RGB", (W, H), (11, 14, 20))
    d = ImageDraw.Draw(ab)
    label(d, (16, 12), "Kiem alpha:  alpha channel | silhouette | bien silhouette (1 px)", 14)
    for i, (arr, name) in enumerate([(al, "alpha"), (sil, "silhouette >127"), (edge, "boundary 1px")]):
        im = Image.fromarray(arr, "L").convert("RGB")
        ab.paste(im, (24 + i * 280, 60))
        label(d, (24 + i * 280, 322), name, 12)
    ab.save(HERE / "preview" / "alpha_silhouette_edge.png")

    # ---------------- compare: cac cap cung footprint ----------------
    pairs = [
        ("TRUE", "10001", REF, "ships-01.jpg#1", "docs/assets/contact-sheets/ships-01.jpg o #1 (tile 1)"),
        ("ANALOGUE", "10013", HERE / "process" / "ref_tile13.png", "ships-01.jpg#13", "ships-01.jpg o #13"),
        ("ANALOGUE", "10019", HERE / "process" / "ref_tile19.png", "ships-01.jpg#19", "ships-01.jpg o #19"),
        ("ANALOGUE", "10020", HERE / "process" / "ref_tile20.png", "ships-01.jpg#20", "ships-01.jpg o #20"),
    ]
    SHEET_SHA = "82862b8b1eef77159c4aa09ffb04a478f1b3307c1259eaf99600fc1be01a613b"
    rows = []
    for i, (role, oid, refp, sheetref, srcnote) in enumerate(pairs):
        if not refp.exists():
            continue
        ref_fit = fit_canvas(Image.open(refp).convert("RGBA"), 256)
        W, H = 560, 330
        cb = Image.new("RGB", (W, H), (11, 14, 20))
        d = ImageDraw.Draw(cb)
        c1 = checker(256)
        c1.paste(ref_fit, (0, 0), ref_fit)
        cb.paste(c1, (16, 40))
        c2 = checker(256)
        c2.paste(sprite, (0, 0), sprite)
        cb.paste(c2, (288, 40))
        label(d, (16, 12), f"cap {i + 1} — {role} — goc ID {oid} | cung footprint 256, subject 86.7% canvas", 13)
        label(d, (16, 300), srcnote, 11, fill=(150, 158, 170))
        label(d, (288, 300), "A moi · player_ship_10001_256@inkember.png", 11, fill=(150, 158, 170))
        cb.save(HERE / "compare" / f"pair{i + 1}_{role.lower()}_{oid}.png")
        rows.append((i + 1, role, oid, sheetref, SHEET_SHA,
                     str(refp.relative_to(HERE)), sha256(refp),
                     "sprites/player_ship_10001_256@inkember.png",
                     sha256(HERE / "sprites" / "player_ship_10001_256@inkember.png")))
    with (HERE / "compare" / "compare_index.csv").open("w") as f:
        f.write("pair,role,original_id,original_sheet,original_sheet_sha256,"
                "original_crop_file,original_crop_sha256,mine_file,mine_sha256,footprint\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + ",256x256 subject 86.7% canvas\n")

    # ---------------- compare: vs A cu (khong phai goc) ----------------
    if olda:
        W, H = 560, 330
        cb = Image.new("RGB", (W, H), (11, 14, 20))
        d = ImageDraw.Draw(cb)
        c1 = checker(256)
        c1.paste(olda, (0, 0), olda)
        cb.paste(c1, (16, 40))
        c2 = checker(256)
        c2.paste(sprite, (0, 0), sprite)
        cb.paste(c2, (288, 40))
        label(d, (16, 12), "A cu @125e1e33 (TRAI) vs A moi (PHAI) — cung slot, KHONG phai sprite goc", 13)
        label(d, (16, 300), "art/w1-player/sprites/ships/player_ship_01_256@ember.png @125e1e33", 11,
              fill=(150, 158, 170))
        label(d, (288, 300), "A moi · hero 10001", 11, fill=(150, 158, 170))
        cb.save(HERE / "compare" / "vs_old_a_same_slot.png")

    print("master sha256", sha256(HERE / "master" / "hero_10001_master_1024.png"))
    print("sprite sha256", sha256(HERE / "sprites" / "player_ship_10001_256@inkember.png"))
    print("OK")


if __name__ == "__main__":
    main()
