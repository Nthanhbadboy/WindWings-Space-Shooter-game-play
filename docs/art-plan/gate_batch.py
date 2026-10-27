#!/usr/bin/env python3
"""gate_batch.py — chấm **cả một lô** theo cổng của ART_REDRAW_PLAN (A1 · A6 · A11–A16 + G-H).

    python3 docs/art-plan/gate_batch.py --manifest <lô.csv> [--compare-sheet <ảnh.png>] [--out <kết-quả.csv>]

Manifest là CSV 2 cột bắt buộc, 1 cột tuỳ chọn:

    file,class[,canvas]
    PS-01_ship_main_256@ink.png,ship
    PS-02_ship_dart_256@ink.png,ship,256x256

`class` phải là một trong 9 nhóm của §4.3/§4.5b. `canvas` (nếu có) dạng `<w>x<h>`; nếu không có
thì script dùng cỡ chuẩn của §4.7 cho 5 nhóm có cỡ cố định (ship 256² · drone/enemy 128² ·
boss 512² · bg 1024²). Nhóm còn lại (bullet · ui · fx · item · laser) **phải** khai `canvas`.

Cổng chấm:

    A1   file PNG có alpha, có ≥ 1 pixel alpha > 0,5
    A6   canvas đúng §4.7 (xem trên)
    A11  `colors` trong dải §4.3 của nhóm
    A12  `val_std` trong dải §4.3
    A13  `dark` trong dải §4.3
    (kèm) `val` · `chroma` trong dải §4.3 — cùng điều kiện `--dir --class`
    A14  `grad_stops` ≥ dải §4.5b
    A15  `outline_px` ≤ dải §4.5b
    A16  `detail` trong dải §4.5b
    G-H  **có bảng so kế cạnh gốc** — truyền `--compare-sheet`; thiếu ⇒ cả lô FAIL

Exit 0 = lô ĐẠT hết; 1 = có ít nhất 1 cổng trượt (lô **không** được nộp); 2 = lỗi đầu vào.

`--selftest` dựng 3 mẫu bằng máy (phẳng · cartoon viền dày · 2.5D), chấm và **tự kiểm** rằng lô bị
chặn đúng lý do — chạy lệnh này sau khi sửa ngưỡng trong `measure_asset.py`.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys
import tempfile

sys.dont_write_bytecode = True  # không để __pycache__ khi import measure_asset

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import measure_asset as M  # noqa: E402  (import sau khi thêm HERE vào sys.path)

# cỡ chuẩn §4.7 cho 5 nhóm có một cỡ duy nhất
CANVAS: dict[str, tuple[int, int]] = {
    "ship": (256, 256),
    "drone": (128, 128),
    "enemy": (128, 128),
    "boss": (512, 512),
    "bg": (1024, 1024),
}


def _fmt(x: float) -> str:
    """Số kiểu Việt Nam: dấu phẩy thập phân, bỏ số 0 thừa (3,000 → 3 · 1,500 → 1,5)."""
    return f"{x:.3f}".rstrip("0").rstrip(".").replace(".", ",")


def grade_asset(path: pathlib.Path, cls: str, canvas: str | None) -> tuple[list[str], dict[str, float]]:
    """Trả (danh sách lỗi, số đo). Lỗi rỗng = asset ĐẠT mọi cổng của nhóm."""
    from PIL import Image

    bad: list[str] = []
    if not path.exists():
        return [f"A1 thiếu file {path.name}"], {}
    img = Image.open(path)
    if img.mode not in ("RGBA", "LA", "PA"):
        bad.append(f"A1 không có alpha ({img.mode})")
    m = M.measure_png(path)

    want = None
    if canvas:
        try:
            w, h = (int(v) for v in canvas.lower().replace("×", "x").split("x"))
            want = (w, h)
        except ValueError:
            bad.append(f"A6 canvas khai sai: {canvas!r}")
    elif cls in CANVAS:
        want = CANVAS[cls]
    else:
        bad.append(f"A6 nhóm `{cls}` phải khai canvas (không có cỡ chuẩn)")

    if want and (img.width, img.height) != want:
        bad.append(f"A6 canvas {img.width}×{img.height} ≠ {want[0]}×{want[1]}")

    bands = M.BANDS[cls]
    for gate, key in (("A11", "colors"), ("A12", "val_std"), ("A13", "dark")):
        if not M.in_band(m[key], bands[key]):
            bad.append(f"{gate} {key}={_fmt(m[key])} ∉ "
                       f"[{_fmt(bands[key][0])}, {_fmt(bands[key][1])}]")
    for key in ("val", "chroma"):
        if not M.in_band(m[key], bands[key]):
            bad.append(f"§4.3 {key}={_fmt(m[key])} ∉ "
                       f"[{_fmt(bands[key][0])}, {_fmt(bands[key][1])}]")

    sb = M.STYLE_BANDS[cls]
    for gate, key in (("A14", "grad_stops"), ("A15", "outline_px"), ("A16", "detail")):
        if not M.in_band(m[key], sb[key]):
            bad.append(f"{gate} {key}={_fmt(m[key])} ∉ "
                       f"[{_fmt(sb[key][0])}, {_fmt(sb[key][1])}]")
    return bad, m


def run(manifest: pathlib.Path, compare_sheet: str | None, out: pathlib.Path | None) -> int:
    if not manifest.exists():
        print(f"✗ không thấy manifest: {manifest}")
        return 2
    rows = list(csv.DictReader(manifest.open(encoding="utf-8", newline="")))
    if not rows:
        print(f"✗ manifest rỗng: {manifest}")
        return 2
    missing_cols = {"file", "class"} - set(rows[0])
    if missing_cols:
        print(f"✗ manifest thiếu cột: {', '.join(sorted(missing_cols))}")
        return 2
    unknown = {r["class"] for r in rows if r["class"] not in M.BANDS}
    if unknown:
        print(f"✗ class lạ: {', '.join(sorted(unknown))} — phải thuộc {', '.join(M.BANDS)}")
        return 2

    base = manifest.parent
    results: list[tuple[str, str, list[str], dict[str, float]]] = []
    for r in rows:
        path = (base / r["file"]).resolve()
        bad, m = grade_asset(path, r["class"].strip(), (r.get("canvas") or "").strip() or None)
        results.append((r["file"], r["class"].strip(), bad, m))

    n_bad = sum(1 for _, _, bad, _ in results if bad)
    gate_count: dict[str, int] = {}
    for _, _, bad, _ in results:
        for item in bad:
            gate_count[item.split()[0]] = gate_count.get(item.split()[0], 0) + 1

    print(f"lô: {manifest.name} · {len(results)} asset · nhóm: "
          f"{', '.join(sorted({c for _, c, _, _ in results}))}")
    for f, cls, bad, m in results:
        if m:
            head = (f"{f[:44]:44s} {cls:7s} colors={int(m['colors']):4d} "
                    f"val={_fmt(m['val'])} val_std={_fmt(m['val_std'])} dark={_fmt(m['dark'])} "
                    f"grad={int(m['grad_stops']):2d} outl={_fmt(m['outline_px'])} "
                    f"detail={_fmt(m['detail'])}")
        else:
            head = f"{f[:44]:44s} {cls:7s} —"
        print(f"  {'ĐẠT ' if not bad else 'TRƯỢT'} {head}")
        for item in bad:
            print(f"        ↳ {item}")

    sheet_ok = bool(compare_sheet) and pathlib.Path(compare_sheet).exists()
    print()
    print(f"  G-H bảng so kế cạnh: {'CÓ — ' + str(compare_sheet) if sheet_ok else 'THIẾU'}")
    if not sheet_ok:
        print("        ↳ thiếu bảng so kế cạnh ⇒ cả lô KHÔNG được duyệt (luật lần 149 mục 2)")

    print()
    if gate_count:
        print("  lỗi theo cổng: " + " · ".join(f"{k}×{v}" for k, v in sorted(gate_count.items())))
    ok = n_bad == 0 and sheet_ok
    print(f"  → {'ĐẠT: lô được nộp' if ok else f'KHÔNG ĐẠT: {n_bad}/{len(results)} asset trượt'}"
          f"{'' if sheet_ok else ' + thiếu G-H'}")

    if out:
        with out.open("w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\r\n")
            wr.writerow(["file", "class", "verdict", "fail_count", "fails",
                         "colors", "val", "val_std", "dark", "chroma",
                         "grad_stops", "outline_px", "detail", "compare_sheet"])
            for f, cls, bad, m in results:
                wr.writerow([f, cls, "PASS" if not bad else "FAIL", len(bad), " | ".join(bad),
                             int(m["colors"]) if m else "", _fmt(m["val"]) if m else "",
                             _fmt(m["val_std"]) if m else "", _fmt(m["dark"]) if m else "",
                             _fmt(m["chroma"]) if m else "",
                             int(m["grad_stops"]) if m else "", _fmt(m["outline_px"]) if m else "",
                             _fmt(m["detail"]) if m else "",
                             "yes" if sheet_ok else "no"])
        print(f"  đã ghi kết quả: {out}")

    return 0 if ok else 1


def selftest() -> int:
    """Dựng 3 mẫu, chấm như một lô, và tự kiểm lô bị chặn đúng lý do."""
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for kind in M.ARCHETYPES:
            M._archetype(kind).save(tmp / f"{kind}.png")
        man = tmp / "manifest.csv"
        with man.open("w", encoding="utf-8", newline="") as fh:
            wr = csv.writer(fh, lineterminator="\r\n")
            wr.writerow(["file", "class", "canvas"])
            for kind in M.ARCHETYPES:
                wr.writerow([f"{kind}.png", "ship", "128x128"])

        print("— lô thử 1: KHÔNG có bảng so kế cạnh (phải trượt vì G-H) —")
        rc1 = run(man, None, None)
        print()
        print("— lô thử 2: CÓ bảng so kế cạnh (vẫn trượt: mẫu máy không đạt màu §4.3/§4.5b) —")
        sheet = tmp / "compare.png"
        M._archetype("metal").save(sheet)
        out = tmp / "result.csv"
        rc2 = run(man, str(sheet), out)
        rows = list(csv.DictReader(out.open(encoding="utf-8", newline="")))

        fails = 0

        def check(name: str, got, want) -> None:
            nonlocal fails
            ok = got == want
            print(f"  {'OK ' if ok else 'FAIL'} {name:44s} got {got!r}  want {want!r}")
            fails += not ok

        print()
        check("lô thiếu G-H ⇒ exit 1", rc1, 1)
        check("lô đủ G-H nhưng mẫu sai ⇒ exit 1", rc2, 1)
        check("ghi đủ 3 dòng kết quả", len(rows), 3)
        check("mọi mẫu FAIL", sum(1 for r in rows if r["verdict"] == "FAIL"), 3)
        flat = next(r for r in rows if r["file"] == "flat.png")
        cartoon = next(r for r in rows if r["file"] == "cartoon.png")
        metal = next(r for r in rows if r["file"] == "metal.png")
        check("A-phẳng trượt A14", "A14" in flat["fails"], True)
        check("B-cartoon trượt A15", "A15" in cartoon["fails"], True)
        check("2.5D không trượt A14/A15/A16",
              all(g not in metal["fails"] for g in ("A14", "A15", "A16")), True)
        check("2.5D chỉ trượt vì màu (mẫu máy, không phải art)",
              all(g in metal["fails"] for g in ("A11",)), True)
        check("cột compare_sheet = yes", {r["compare_sheet"] for r in rows}, {"yes"})
        print()
        if fails:
            print(f"✗ {fails} phép kiểm của gate_batch trượt")
            return 1
        print("✓ gate_batch chặn đúng: thiếu G-H ⇒ chặn · A14 bắt phẳng · A15 bắt viền dày")
        return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chấm cả lô theo cổng của ART_REDRAW_PLAN")
    ap.add_argument("--manifest", type=pathlib.Path, help="CSV: file,class[,canvas]")
    ap.add_argument("--compare-sheet", help="đường dẫn bảng so kế cạnh gốc (G-H)")
    ap.add_argument("--out", type=pathlib.Path, help="ghi kết quả từng asset ra CSV")
    ap.add_argument("--selftest", action="store_true", help="tự kiểm bằng 3 mẫu dựng máy")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.manifest:
        ap.print_help()
        return 2
    return run(args.manifest, args.compare_sheet, args.out)


if __name__ == "__main__":
    sys.exit(main())
