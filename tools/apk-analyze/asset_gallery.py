#!/usr/bin/env python3
"""Build a browseable asset reference pack from the Unity export.

Input : /tmp/apk/unity/export/{Sprite,Texture2D,AudioClip,Font}/*  (unity_assets.py export)
Output: docs/assets/
          INDEX.md                 — danh mục + hướng dẫn
          manifest.csv             — mọi asset: path_id, loại, tên, kích thước, nhóm
          sprites-index.csv        — sprite kèm sheet + ô số mấy
          contact-sheets/*.jpg     — bảng ảnh có đánh số, để xem nhanh trong repo
          audio-index.csv          — clip, kênh, sample rate, thời lượng

The contact sheets are downscaled JPEG previews (design reference only).
Full-size PNG/WAV stay in the `windwings-assets` artifact / draft release.
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import sys
import wave
from collections import Counter, defaultdict

EXPORT = os.environ.get("EXPORT_DIR", "/tmp/apk/unity/export")
OUT = os.environ.get("ASSET_OUT", "docs/assets")
SHEETS = os.path.join(OUT, "contact-sheets")
TILE = int(os.environ.get("TILE", "150"))
COLS = int(os.environ.get("COLS", "8"))
ROWS = int(os.environ.get("ROWS", "8"))
MAX_TILES = COLS * ROWS
JPEG_Q = int(os.environ.get("JPEG_Q", "80"))

# ------------------------------------------------------------------ categories
CATS: list[tuple[str, str, str]] = [
    ("ships",       r"^(100[0-2][0-9]|10999)$",                                   "Tàu người chơi (sprite id = ship id)"),
    ("drones",      r"^(200[0-1][0-9])$",                                          "Drone / droid"),
    ("bosses",      r"^(70[0-2][0-9]|90[0-2][0-9])$",                              "Boss theo wave (idWave)"),
    ("items",       r"^(\+1Level|Fullpower|\+Hp|Droid-\d+)$",                      "Item rơi"),
    ("ui",          r"(?i)(^ui_|_ui$|icon|btn|button|panel|popup|frame|badge|tab|cell|slot|bar$|_bg$|board)",
                   "UI: icon, nút, panel, khung"),
    ("enemy",       r"(?i)(enemy|_en_|droid|monster|alien|ufo)",
                   "Enemy thường"),
    ("bullet",      r"(?i)(bullet|_blt|laser|missile|rocket|beam|plasma|torpedo)",
                   "Đạn, laser, tên lửa"),
    ("fx",          r"(?i)(fx|effect|explos|smoke|fire|spark|glow|wave_|shock|hit|trail|saw)",
                   "Hiệu ứng, nổ, trail"),
    ("background",  r"(?i)(bg|background|space|nebula|star|planet|galaxy|sky)",
                   "Nền, tinh vân, hành tinh"),
    ("atlas",       r"(?i)^sactx",
                   "Texture atlas gốc (UI + nhân vật gộp)"),
    ("font",        r"(?i)(sdf|font|noto|roboto|amiri|barlow|character)",
                   "Font atlas / bảng ký tự"),
]


def classify(name: str, kind: str, atlas: str = "") -> str:
    if kind == "AudioClip":
        return "audio"
    if kind == "Font":
        return "font"
    for field in (name, atlas):          # the atlas name is often the only hint
        if not field:
            continue
        for cat, pattern, _ in CATS:
            if re.search(pattern, field):
                return cat
    if kind == "Texture2D" or "sactx" in (atlas or "").lower():
        return "atlas"
    return "unclassified"


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


MANIFEST = os.environ.get("EXPORT_MANIFEST", "/tmp/apk/unity/export-manifest.csv")


def manifest_index():
    """relative_path -> {path_id, atlas, name} (from unity_assets.py export)."""
    idx = {}
    if not os.path.isfile(MANIFEST):
        return idx
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rel = r.get("path") or ""
            if rel:
                idx[rel] = {"path_id": r.get("path_id", ""), "atlas": r.get("atlas", ""),
                            "name": r.get("name", "")}
    return idx


def collect():
    rows = []
    meta = manifest_index()
    for kind in ("Sprite", "Texture2D", "AudioClip", "Font"):
        d = os.path.join(EXPORT, kind)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if not os.path.isfile(p):
                continue
            name = os.path.splitext(fn)[0]
            rel = f"{kind}/{fn}"
            m = meta.get(rel, {})
            rows.append({"kind": kind, "name": name, "file": p,
                         "bytes": os.path.getsize(p),
                         "path_id": m.get("path_id", ""),
                         "atlas": m.get("atlas", ""),
                         "category": classify(name, kind, m.get("atlas", ""))})
    return rows


def contact_sheets(rows):
    """Labeled grid previews; returns index of (row -> sheet, tile)."""
    from PIL import Image, ImageDraw

    try:
        font = ImageDraw.getfont()
    except Exception:  # noqa: BLE001
        font = None

    os.makedirs(SHEETS, exist_ok=True)
    index: dict[str, tuple[str, int]] = {}
    by_cat = defaultdict(list)
    for r in rows:
        if r["kind"] in ("Sprite", "Texture2D", "Font"):
            by_cat[r["category"]].append(r)

    written = []
    for cat, items in sorted(by_cat.items()):
        items.sort(key=lambda r: r["name"])
        chunks = [items[i:i + MAX_TILES] for i in range(0, len(items), MAX_TILES)]
        for ci, chunk in enumerate(chunks, 1):
            rows_used = max(1, math.ceil(len(chunk) / COLS))
            width, height = COLS * TILE, rows_used * TILE + 26
            sheet = Image.new("RGB", (width, height), (24, 24, 30))
            draw = ImageDraw.Draw(sheet)
            draw.text((6, 6), f"{cat} - {len(items)} asset - sheet {ci}/{len(chunks)}",
                      fill=(230, 230, 240), font=font)
            for i, r in enumerate(chunk):
                cx, cy = i % COLS, i // COLS
                x0, y0 = cx * TILE, cy * TILE + 26
                # checkerboard so transparency is visible
                for yy in range(0, TILE, 15):
                    for xx in range(0, TILE, 15):
                        shade = 58 if ((xx // 15 + yy // 15) % 2 == 0) else 44
                        draw.rectangle([x0 + xx, y0 + yy, x0 + xx + 14, y0 + yy + 14],
                                       fill=(shade, shade, shade))
                try:
                    with Image.open(r["file"]) as im:
                        im = im.convert("RGBA")
                        im.thumbnail((TILE - 10, TILE - 10), Image.LANCZOS)
                        sheet.paste(im, (x0 + (TILE - im.width) // 2,
                                         y0 + (TILE - im.height) // 2), im)
                except Exception:  # noqa: BLE001
                    draw.text((x0 + 4, y0 + 4), "ERR", fill=(255, 90, 90), font=font)
                draw.text((x0 + 3, y0 + TILE - 13), f"#{i + 1}", fill=(255, 255, 120), font=font)
                index[r["file"]] = (f"{cat}-{ci:02d}.jpg", i + 1)
            fn = f"{cat}-{ci:02d}.jpg"
            sheet.save(os.path.join(SHEETS, fn), quality=JPEG_Q, optimize=True)
            written.append((fn, cat, len(chunk), os.path.getsize(os.path.join(SHEETS, fn))))
    return written, index


def audio_index(rows):
    out = []
    for r in rows:
        if r["kind"] != "AudioClip":
            continue
        ch = rate = frames = 0
        dur = 0.0
        try:
            with wave.open(r["file"], "rb") as w:
                ch, rate, frames = w.getnchannels(), w.getframerate(), w.getnframes()
                dur = frames / rate if rate else 0.0
        except Exception:  # noqa: BLE001
            pass
        if not dur and r["file"].endswith((".ogg", ".m4a", ".mp3")):
            dur = 0.0   # compressed: duration lives in the codec header, skipped here
        out.append({"name": r["name"], "channels": ch, "sample_rate": rate,
                    "seconds": round(dur, 2), "bytes": r["bytes"],
                    "format": os.path.splitext(r["file"])[1].lstrip("."),
                    "file": os.path.relpath(r["file"], EXPORT)})
    return out


def main() -> int:
    if not os.path.isdir(EXPORT):
        print(f"export dir missing: {EXPORT}")
        return 0
    os.makedirs(OUT, exist_ok=True)
    rows = collect()
    print(f"assets found: {len(rows)}")
    if not rows:
        return 0

    sheets, index = contact_sheets(rows)
    audio = audio_index(rows)
    counts = Counter(r["category"] for r in rows)

    with open(os.path.join(OUT, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "kind", "name", "path_id", "atlas", "bytes", "relative_path"])
        for r in sorted(rows, key=lambda r: (r["category"], r["kind"], r["name"])):
            w.writerow([r["category"], r["kind"], r["name"], r["path_id"], r["atlas"],
                        r["bytes"], os.path.relpath(r["file"], EXPORT)])

    with open(os.path.join(OUT, "sprites-index.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "name", "kind", "path_id", "atlas", "contact_sheet", "tile",
                    "bytes", "relative_path"])
        for r in sorted(rows, key=lambda r: (r["category"], r["name"])):
            sheet, tile = index.get(r["file"], ("", ""))
            w.writerow([r["category"], r["name"], r["kind"], r["path_id"], r["atlas"], sheet, tile,
                        r["bytes"], os.path.relpath(r["file"], EXPORT)])

    if audio:
        with open(os.path.join(OUT, "audio-index.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(audio[0]))
            w.writeheader()
            w.writerows(audio)

    desc = {c: d for c, _, d in CATS}
    desc.update({"unclassified": "Sprite không rõ nguồn (xem cột `atlas`)", "audio": "Âm thanh", "font": "Font"})
    lines = ["# Asset tham chiếu — WindWings 1.3.118", "",
             f"- Tổng asset: **{len(rows)}**  ({human(sum(r['bytes'] for r in rows))})",
             f"- Contact sheet: **{len(sheets)}** file trong [`contact-sheets/`](contact-sheets/)",
             "- Ảnh gốc full-size: artifact `windwings-analysis` (mục `/tmp/apk/unity/export`)",
             "  và draft release `windwings-assets-1.3.118`.", "",
             "## Nhóm asset", "",
             "| nhóm | số lượng | mô tả | contact sheet |", "|---|---:|---|---|"]
    for cat, n in counts.most_common():
        files = [s[0] for s in sheets if s[1] == cat]
        link = f"[{len(files)} sheet](contact-sheets/{files[0]})" if files else "—"
        lines.append(f"| `{cat}` | {n} | {desc.get(cat, '')} | {link} |")
    if audio:
        total_s = sum(a["seconds"] for a in audio)
        lines += ["", "## Âm thanh", "",
                  f"- **{len(audio)}** clip, tổng ~{total_s:.0f} giây "
                  f"({human(sum(a['bytes'] for a in audio))})",
                  "- Danh sách: [`audio-index.csv`](audio-index.csv) (tên, kênh, sample rate, giây, định dạng)",
                  ""]
    lines += ["", "## Cách dùng", "",
              "1. Mở `contact-sheets/<nhóm>-01.jpg` để xem nhanh toàn bộ asset của nhóm đó,",
              "   mỗi ô có số `#n` ở góc dưới.",
              "2. Tra số đó trong `sprites-index.csv` (cột `tile`) để biết tên + `path_id`.",
              "3. `manifest.csv` là danh sách đầy đủ, `audio-index.csv` là danh sách âm thanh.",
              "4. File PNG gốc lấy từ artifact/release — repo chỉ chứa bản preview JPEG.",
              "", "> Ảnh/âm thanh gốc thuộc bản quyền GCenter. Dùng làm **mẫu tham chiếu thiết kế**;",
              "> không đóng gói vào bản phát hành.", ""]
    with open(os.path.join(OUT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(os.path.join(OUT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump({"total": len(rows), "by_category": dict(counts),
                   "sheets": [{"file": s[0], "category": s[1], "tiles": s[2], "bytes": s[3]}
                              for s in sheets],
                   "audio_clips": len(audio),
                   "audio_seconds": round(sum(a["seconds"] for a in audio), 1)}, f, indent=1)
    print("\n".join(lines[:20]))
    print(f"sheets: {len(sheets)}, audio: {len(audio)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
