#!/usr/bin/env python3
"""classify-by-measure.py — phân loại asset bằng **luật có bằng chứng** + bảng tách sheet.

Đầu vào (đều đã có trong repo):
  docs/assets/sprites-index.csv            tên · path_id · sheet · tile
  docs/apk-analysis/04-asset-manifest.csv  kích thước gốc (width/height)
  docs/assets/art-study.csv                số đo pixel của từng ô (tools/art-study.py)

Đầu ra:
  docs/assets/sprites-auto-classified.csv  nhãn tự động + luật + mức tin cậy
  docs/assets/sheet-splits.csv             sprite nào thật ra là **sheet**, rect từng mảnh

Hai loại luật, ghi rõ trong cột `evidence`:
  A — **tên/id tự mô tả** (khớp từ vựng đã có trong repo: `blt`, `CB-300xx`, `Rank`, `Head`…)
  B — **chỉ dựa vào số đo** (màu/bão hoà/sáng/ncomp/fill) ⇒ mức tin cậy thấp hơn
  — — không luật nào khớp ⇒ để `unresolved`, **không đoán**.

Chạy:  python3 tools/classify-by-measure.py
"""
from __future__ import annotations

import collections
import csv
import os
import re
import struct
import sys
import zlib

INDEX = "docs/assets/sprites-classified.csv"   # đã có 1.049 nhãn từ vòng trước
MANIFEST = "docs/apk-analysis/04-asset-manifest.csv"
STUDY = "docs/assets/art-study.csv"
OUT_CLASS = "docs/assets/sprites-auto-classified.csv"
OUT_SPLIT = "docs/assets/sheet-splits.csv"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── luật A: tên/id ────────────────────────────────────────────────────
NAME_RULES = [
    (r"^blt", "bullet", "A", "tên `blt_` = đạn (khớp `bltDamage` trong COMBAT.md)"),
    (r"^(CB|W1-|W2-|MB\d)", "enemy", "A", "id prefab enemy `CB-300xx` / `W1-30xxx`"),
    (r"^[Bb]oss.*Gray$", "ui", "A", "ảnh boss bị khoá = icon UI, không phải sprite boss"),
    (r"^([Bb]oss\b|boss_|Boss\d)", "bosses", "A", "tên boss"),
    (r"^(Head|Gun|Wing|Body|Bone|Hand|Leg|Tail|Vai|Tay|Phundoc|Sung)", "parts",
     "A", "bộ phận rời của boss/tàu (`BOSSES.md` gọi là part)"),
    (r"^sieuhopthe", "parts", "A", "`sieuhopthe_tachbophan` = siêu hợp thể **tách bộ phận**"),
    (r"^(Rank|PVP|Vip|Hotro)", "ui", "A", "huy hiệu/cấp/bảng UI"),
    (r"^(Avatar|AppleInAppPurchase|NoAds|GameOver|SelectMode|Thanh|Tip|Btn|Board|Popup|Tab|Icon|Frame|Bgr|Bg)", "ui",
     "A", "tên chức năng UI"),
    (r"^(Giam|Tang|Time|Sao|Star|Lock|Khoa|Hp|HP)", "ui", "A", "nhãn/thanh UI"),
    (r"^Coin", "items", "A", "đồng tiền = vật phẩm"),
    (r"\d+Radar$", "ui", "A", "radar/minimap của màn chọn"),
]

# ── luật B: chỉ số đo ────────────────────────────────────────────────
def feature_rule(r: dict) -> tuple[str, str] | None:
    w, h = r["w"], r["h"]
    ncomp, fill = r["ncomp"], r["fill"]
    sat, val, dark = r["sat"], r["val"], r["dark"]
    if max(w, h) >= 512 and val <= 0.50 and sat <= 0.45:
        return ("background", "B: ≥512 px · sáng ≤0,50 · bão hoà ≤0,45")
    if dark >= 0.30 and ncomp <= 3:
        return ("bullet", "B: `dark_share` ≥0,30 (thân tối) · ≤3 mảnh")
    if sat <= 0.15 and val >= 0.65 and fill <= 0.25:
        return ("fx", "B: gần vô sắc · sáng · thưa (glow)")
    if fill >= 0.60 and ncomp <= 2:
        return ("ui", "B: lấp ≥60 % ô · 1–2 mảnh (nền nút/panel)")
    if ncomp >= 8 and max(w, h) <= 256:
        return ("ui", "B: ≥8 mảnh trong ≤256 px (bộ icon ghép)")
    return None


def load_csv(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    idx = load_csv(INDEX)
    man = {r["path_id"]: r for r in load_csv(MANIFEST)}
    study = {(r["sheet"], r["tile"]): r for r in load_csv(STUDY)}

    rows = []
    stats = collections.Counter()
    rules = collections.Counter()
    for r in idx:
        m = man.get(r["path_id"]) or {}
        s = study.get((r["contact_sheet"], r["tile"])) or {}
        w = int(m.get("width") or 0)
        h = int(m.get("height") or 0)
        rec = {
            "name": r["name"], "path_id": r["path_id"],
            "category_now": r["category"], "w": w, "h": h,
            "ncomp": int(s.get("ncomp") or 0),
            "fill": float(s.get("fill") or 0),
            "sat": float(s.get("sat") or 0),
            "val": float(s.get("val") or 0),
            "dark": float(s.get("dark_share") or 0),
            "colors": int(s.get("colors") or 0),
            "sheet": r["contact_sheet"], "tile": r["tile"],
            "comps": s.get("comps", ""),
        }
        prev = (r.get("proposed_category") or "").strip()
        if prev and prev not in ("", "unclassified", "unknown") and r.get("confidence"):
            rec.update({"category_auto": prev, "evidence": r.get("confidence") or "A",
                        "rule": r.get("rule") or "giữ nhãn vòng trước",
                        "confidence": r.get("confidence") or "A"})
            stats[prev] += 1
            rules["giữ nhãn vòng trước"] += 1
        else:
            hit = None
            for pat, cat, conf, why in NAME_RULES:
                if re.search(pat, r["name"]):
                    hit = (cat, conf, why)
                    break
            if hit:
                rec.update({"category_auto": hit[0], "evidence": hit[1],
                            "rule": hit[2], "confidence": hit[1]})
                rules[hit[2]] += 1
                stats[hit[0]] += 1
            else:
                fr = feature_rule(rec)
                if fr:
                    rec.update({"category_auto": fr[0], "evidence": "B",
                                "rule": fr[1], "confidence": "B"})
                    rules[fr[1]] += 1
                    stats[fr[0]] += 1
                else:
                    rec.update({"category_auto": "unresolved", "evidence": "—",
                                "rule": "không luật nào khớp", "confidence": "—"})
                    stats["unresolved"] += 1
        rows.append(rec)

    cols = ["name", "path_id", "category_now", "category_auto", "confidence",
            "rule", "w", "h", "ncomp", "fill", "sat", "val", "dark", "colors",
            "sheet", "tile"]
    with open(OUT_CLASS, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for rec in rows:
            wr.writerow({k: rec[k] for k in cols})

    # ── sheet: sprite nào thật ra là nhiều hình ──
    splits = []
    for rec in rows:
        if rec["ncomp"] < 3 or not rec["comps"]:
            continue
        is_page = rec["category_now"] == "atlas"
        if not (is_page or rec["ncomp"] >= 10):
            continue
        parts = [p.split(",") for p in rec["comps"].split(";") if p]
        bx = max((int(p[0]) + int(p[2]) for p in parts), default=1)
        by = max((int(p[1]) + int(p[3]) for p in parts), default=1)
        sx = rec["w"] / bx if bx else 1
        sy = rec["h"] / by if by else 1
        rects = ";".join(
            f"{round(int(p[0]) * sx)},{round(int(p[1]) * sy)},"
            f"{max(1, round(int(p[2]) * sx))},{max(1, round(int(p[3]) * sy))}"
            for p in parts)
        splits.append({
            "name": rec["name"], "w": rec["w"], "h": rec["h"],
            "ncomp": rec["ncomp"], "category": rec["category_now"],
            "page": "sactx" if rec["name"].startswith("sactx") else "",
            "rects_native": rects, "sheet": rec["sheet"], "tile": rec["tile"],
        })
    with open(OUT_SPLIT, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(splits[0]) if splits else ["name"])
        wr.writeheader()
        wr.writerows(splits)

    print("nhãn:", dict(stats))
    print("\nluật dùng nhiều nhất:")
    for k, v in rules.most_common(12):
        print(f"  {v:4d}  {k}")
    resolved = len(idx) - stats["unresolved"]
    print(f"\nđã phân loại được {resolved}/{len(idx)} · còn unresolved {stats['unresolved']}")
    print(f"sheet cần tách: {len(splits)} (page sactx: "
          f"{sum(1 for s in splits if s['page'])}), tổng mảnh: "
          f"{sum(int(s['ncomp']) for s in splits)}")
    print("đã ghi", OUT_CLASS, "và", OUT_SPLIT)

    if "--crop" in sys.argv:
        outdir = sys.argv[sys.argv.index("--crop") + 1]
        lim = int(sys.argv[sys.argv.index("--crop-limit") + 1]) if "--crop-limit" in sys.argv else None
        nf, npx = crop_sheets(rows, outdir, lim)
        print(f"đã cắt {nf} PNG · {npx / 1e6:.2f} Mpx · vào {outdir}")
    return 0


# ── tách sheet ra PNG (tuỳ chọn) ──────────────────────────────────────
# Cắt từ **contact sheet 150 px/ô** ⇒ ảnh ra là *bản xem trước*, không phải
# sprite gốc. Rect theo pixel gốc nằm trong `sheet-splits.csv`; muốn cắt đúng
# thì cần `Sprite.m_RD.rect` do nhánh dữ liệu export (ASSET_TRIAGE.md §9.6).
def _png(path: str, w: int, h: int, rgba: bytes) -> None:
    """Ghi PNG RGBA không cần thư viện ngoài."""
    raw = b"".join(b"\x00" + rgba[y * w * 4:(y + 1) * w * 4] for y in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n"
                 + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw, 6))
                 + chunk(b"IEND", b""))


def _art_study():
    """Nạp tools/art-study.py (tên có dấu gạch) để dùng lại ppm/bg_mask/components."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "artstudy", os.path.join(ROOT, "tools", "art-study.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def crop_sheets(rows: list[dict], outdir: str, limit: int | None = None) -> tuple[int, int]:
    """Cắt **từng mảnh rời** của mọi sheet trong `rows` → PNG trong suốt."""
    import collections
    st = _art_study()
    os.makedirs(outdir, exist_ok=True)
    todo = [r for r in rows if r["comps"] and r["ncomp"] >= 3
            and (r["category_now"] == "atlas" or r["ncomp"] >= 10)]
    if limit:
        todo = todo[:limit]
    by_sheet = collections.defaultdict(list)
    for r in todo:
        by_sheet[r["sheet"]].append(r)

    manifest, n_files, n_px = [], 0, 0
    for sh in sorted(by_sheet):
        path = os.path.join(ROOT, "docs/assets/contact-sheets", sh)
        if not os.path.isfile(path):
            continue
        try:
            iw, ih, px = st.ppm(path)
        except Exception:
            continue
        cell = iw // st.COLS
        tones, cnt = [], collections.Counter()
        for y in range(0, min(ih, cell), 2):
            for x in range(0, iw, 2):
                i = (y * iw + x) * 3
                cnt[(px[i], px[i + 1], px[i + 2])] += 1
        tones = [c for c, _ in cnt.most_common(2)]
        if len(tones) < 2:
            continue
        for r in by_sheet[sh]:
            tile = int(r["tile"] or 0)
            if tile < 1:
                continue
            x0 = ((tile - 1) % st.COLS) * cell
            y0 = ((tile - 1) // st.COLS) * cell
            if x0 + cell > iw or y0 + cell > ih:
                continue
            bg = st.bg_mask(px, iw, x0, y0, cell, tones)
            comps = st.components(bg, cell, min_area=20, keep=400)
            for k, (cx, cy, cw, ch, area) in enumerate(comps):
                buf = bytearray(cw * ch * 4)
                for yy in range(ch):
                    src = ((y0 + cy + yy) * iw + x0 + cx) * 3
                    for xx in range(cw):
                        o = (yy * cw + xx) * 4
                        i = src + xx * 3
                        buf[o] = px[i]
                        buf[o + 1] = px[i + 1]
                        buf[o + 2] = px[i + 2]
                        buf[o + 3] = 0 if bg[(cy + yy) * cell + cx + xx] else 255
                stem = os.path.splitext(os.path.basename(sh))[0]
                fn = f"{stem}__t{tile:03d}__p{k:02d}.png"
                _png(os.path.join(outdir, fn), cw, ch, bytes(buf))
                manifest.append((fn, r["name"], cw, ch, area))
                n_files += 1
                n_px += cw * ch
    with open(os.path.join(outdir, "crops.csv"), "w", encoding="utf-8", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["file", "sprite", "w", "h", "area_px"])
        wr.writerows(manifest)
    return n_files, n_px


if __name__ == "__main__":
    sys.exit(main())
