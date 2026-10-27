#!/usr/bin/env python3
"""verify_numbers.py — kiểm mọi con số đã công bố trong bộ kế hoạch art.

Chạy từ gốc repo:

    python3 docs/art-plan/verify_numbers.py

Không cần thư viện ngoài. Exit 0 = khớp hết; exit 1 = có số lệch (in ra chỗ lệch).

Nguồn sự thật: `art-planner.csv` + `w1-work-order.csv`. Script này KHÔNG sửa file nào —
nó chỉ đọc và đối chiếu với các con số đang nằm trong 3 tài liệu markdown.
"""

from __future__ import annotations

import csv
import pathlib
import sys

sys.dont_write_bytecode = True  # không để lại __pycache__ khi import measure_asset

HERE = pathlib.Path(__file__).resolve().parent
PLANNER = HERE / "art-planner.csv"
W1_CSV = HERE / "w1-work-order.csv"
DOCS = {
    "plan": HERE / "ART_REDRAW_PLAN.md",
    "w1": HERE / "W1_WORK_ORDER.md",
    "w0": HERE / "W0_LISTING_ASSETS.md",
}

TOL = 0.02          # sai số làm tròn 2 chữ số thập phân
S0 = 32.0           # setup wave 0
fails: list[str] = []


def check(name: str, got: float, want: float, tol: float = TOL) -> None:
    ok = abs(got - want) <= tol
    print(f"  {'OK ' if ok else 'FAIL'} {name:38s} got {got:9.2f}  want {want:9.2f}")
    if not ok:
        fails.append(f"{name}: got {got:.2f}, want {want:.2f}")


def check_eq(name: str, got, want) -> None:
    ok = got == want
    print(f"  {'OK ' if ok else 'FAIL'} {name:38s} got {got!r}  want {want!r}")
    if not ok:
        fails.append(f"{name}: got {got!r}, want {want!r}")


def num(row: dict, key: str) -> float:
    v = row.get(key) or 0
    return float(v)


def denom(row: dict) -> float:
    """Số 'đơn vị giá' của dòng = de + (kept - de) * 0,25 (de mặc định = kept)."""
    kept = int(row["kept_records"] or 0)
    de = int(row["de_est"]) if row.get("de_est") else kept
    de = min(de, kept)
    return de + (kept - de) * 0.25


def main() -> int:
    rows = list(csv.DictReader(PLANNER.open(encoding="utf-8")))
    cols = list(rows[0].keys())
    w1 = list(csv.DictReader(W1_CSV.open(encoding="utf-8")))

    print("1) hình dạng planner")
    check_eq("số cột", len(cols), 36)
    check_eq("số dòng", len(rows), 655)
    check_eq("dòng listing W0", sum(1 for r in rows if r["lane"] == "LISTING"), 4)
    check_eq("dòng overhead", sum(1 for r in rows if r["unit"] == "overhead"), 22)
    for k in ("l2_de", "l2_h_v3", "h_w0", "w0_slots", "de_est", "reuse_est"):
        check_eq(f"có cột {k}", k in cols, True)

    print("2) tổng bất biến (§1.3 / §7.1 plan)")
    tot = lambda k: sum(num(r, k) for r in rows)  # noqa: E731
    ints = lambda k: sum(int(r[k] or 0) for r in rows)  # noqa: E731
    check_eq("Σ n_records", ints("n_records"), 2185)
    check_eq("Σ kept_records", ints("kept_records"), 801)
    check_eq("Σ l2_n", ints("l2_n"), 82)
    check_eq("Σ n_units", ints("n_units"), 788)
    check("Σ h_full", tot("h_full"), 3915.84)
    check("Σ h_scope", tot("h_scope"), 1232.38)
    check("Σ h_scope_v2", tot("h_scope_v2"), 1578.42)
    check("Σ l2_h (v1)", tot("l2_h"), 108.88)
    check("Σ l2_h_v2", tot("l2_h_v2"), 137.29)
    check("Σ h_w0", tot("h_w0"), 35.0)
    check("Σ w0_slots", tot("w0_slots"), 27.0)

    print("3) L2 theo đơn giá của từng dòng (§6 W1_WORK_ORDER)")
    art = sum(num(r, "l2_h_v3") for r in rows if r["unit"] != "overhead")
    oh = sum(num(r, "l2_h_v3") for r in rows if r["unit"] == "overhead")
    check("Σ l2_h_v3 (art)", art, 155.41)
    check("Σ l2_h_v3 (overhead)", oh, 16.62)
    check("Σ l2_h_v3 (tất cả)", art + oh, 172.03)
    over = [r["row_id"] for r in rows
            if r["unit"] != "overhead" and r["lane"] != "LISTING"
            and num(r, "l2_h_v3") > num(r, "h_scope_v2") + 1e-9]
    check_eq("số dòng có l2_h_v3 > h_scope_v2", len(over), 0)

    print("4) wave W1 — dựng lại từ planner")
    wave: dict[str, float] = {}
    for r in rows:
        if r["lane"] == "LISTING":
            continue
        h2, l3 = num(r, "h_scope_v2"), num(r, "l2_h_v3")
        wave["W1"] = wave.get("W1", 0.0) + l3
        wd = r["wave_done"]
        wave[wd] = wave.get(wd, 0.0) + (h2 - l3)
    wave["W1"] += S0
    for k, want in (("W1", 206.38), ("W2", 510.96), ("W3", 178.53),
                    ("W4", 166.68), ("W5", 489.07), ("X", 58.80)):
        check(f"wave {k}", wave.get(k, 0.0), want)
    check("Σ wave", sum(wave.values()), 1610.42)
    check("W1 − plan 177,3", wave["W1"] - 177.3, 29.08)

    print("5) lane PLAYER — work order")
    units = [r for r in w1 if r["kind"] == "unit"]
    variants = [r for r in w1 if r["kind"] == "variant"]
    oh_rows = [r for r in w1 if r["kind"] == "overhead"]
    check_eq("số unit", len(units), 48)
    check_eq("số biến thể (20006)", len(variants), 1)
    check_eq("số overhead", len(oh_rows), 4)
    check_eq("unit ở W1", sum(1 for r in units if r["scope"] == "W1"), 13)
    check_eq("unit bị cắt", sum(1 for r in units if r["scope"] == "out"), 9)
    play = [r for r in rows if r["lane"] == "PLAYER"]
    check_eq("planner: 16 dòng PLAYER", len(play), 16)
    check_eq("planner: 48 unit PLAYER", sum(int(r["n_units"] or 0) for r in play), 48)
    check("PLAYER h_scope_v2", sum(num(r, "h_scope_v2") for r in play), 119.80)
    check("PLAYER l2 art", sum(num(r, "l2_h_v3") for r in play if r["unit"] != "overhead"), 33.96)
    check("PLAYER l2 overhead", sum(num(r, "l2_h_v3") for r in play if r["unit"] == "overhead"), 7.23)
    check("work-order Σ h_l2", sum(num(r, "h_l2") for r in w1), 41.19, tol=0.05)
    check("work-order Σ h_full (in scope)",
          sum(num(r, "h_full") for r in units + variants if r["scope"] != "out"), 101.82)

    print("6) cổng nghiệm thu + mã accept (W1 work order)")
    check_eq("mã accept là duy nhất", len({r["accept"] for r in w1}), len(w1))
    check_eq("mọi dòng có mã accept", sum(1 for r in w1 if not r["accept"]), 0)
    check_eq("unit có A13 ở L2", sum(1 for r in units if "A13" in r["gates_l2"]), len(units))
    check_eq("unit không có A13 ở full",
             sum(1 for r in units if "A13" not in r["gates_full"]), 0)
    check_eq("unit không có A11/A12 ở full",
             sum(1 for r in units if "A11" not in r["gates_full"] or "A12" not in r["gates_full"]), 0)

    print("7) W0 listing — slot và giờ")
    w0 = [r for r in rows if r["lane"] == "LISTING"]
    slots = {r["batch_id"]: int(r["w0_slots"] or 0) for r in w0}
    hours = {r["batch_id"]: num(r, "h_w0") for r in w0}
    check_eq("icon slots", slots.get("L-ICON"), 8)
    check_eq("key art slots", slots.get("L-KEYART"), 4)
    check_eq("screenshot slots", slots.get("L-SHOT"), 15)
    check_eq("qa slots", slots.get("L-QA"), 0)
    check_eq("Σ slot = 8+4+15", sum(slots.values()), 27)
    check("icon h", hours.get("L-ICON", 0), 9.0)
    check("key art h", hours.get("L-KEYART", 0), 15.0)
    check("screenshot h", hours.get("L-SHOT", 0), 9.0)
    check("qa h", hours.get("L-QA", 0), 2.0)
    check("Σ h_w0 = 35", sum(hours.values()), 35.0)

    print("8) chuỗi số phải xuất hiện trong tài liệu")
    text = {k: p.read_text(encoding="utf-8") for k, p in DOCS.items()}
    for doc, token in (
        ("plan", "206,4"), ("plan", "155,4"), ("plan", "1.610,4"), ("plan", "1.578,4"),
        ("plan", "4.355,7"), ("plan", "37 dòng"), ("plan", "655 dòng**"),
        ("w1", "206,4"), ("w1", "41,19"), ("w1", "33,96"), ("w1", "67,9"),
        ("w0", "27 slot"), ("w0", "35 h"), ("w0", "1366×768"), ("w0", "450×800"),
        ("plan", "4.11"), ("plan", "A11"), ("plan", "A12"), ("plan", "A13"),
        ("w1", "A11"), ("w1", "A13"),
        ("w0", "w0-listing-slots.csv"), ("w0", "artboard"),
    ):
        ok = token in text[doc]
        print(f"  {'OK ' if ok else 'FAIL'} {doc:4s} chứa {token!r}")
        if not ok:
            fails.append(f"{doc} thiếu {token!r}")

    print("8b) W0 slot sheet — w0-listing-slots.csv")
    w0c = list(csv.DictReader((HERE / "w0-listing-slots.csv").open(encoding="utf-8")))
    lots: dict[str, int] = {}
    stores: dict[str, int] = {}
    for r in w0c:
        lots[r["lot"]] = lots.get(r["lot"], 0) + 1
        stores[r["store"]] = stores.get(r["store"], 0) + 1
    check_eq("sổ slot: 27 dòng", len(w0c), 27)
    check_eq("sổ slot = planner w0_slots", len(w0c), int(sum(num(r, "w0_slots") for r in rows)))
    check_eq("icon", lots.get("L-ICON"), 8)
    check_eq("key art", lots.get("L-KEYART"), 4)
    check_eq("screenshot", lots.get("L-SHOT"), 15)
    for store, want in (("MS", 9), ("Amazon", 8), ("Huawei", 7), ("internal", 1), ("Windows", 1), ("Android", 1)):
        check_eq(f"store {store}", stores.get(store), want)
    check_eq("tên file duy nhất", len({r["file"] for r in w0c}), len(w0c))
    check_eq("mọi slot có w/h", sum(1 for r in w0c if not (r["w"] and r["h"])), 0)
    check_eq("mọi slot có status", sum(1 for r in w0c if r["status"] != "TODO"), 0)

    print("9) tái lập 9 công thức tô (§4.5) bằng measure_asset.py")
    sys.path.insert(0, str(HERE))
    try:
        import measure_asset  # noqa: PLC0415 - import trễ vì nằm cùng thư mục
        rc = measure_asset.run_recipe_selftest(verbose=False)
        check_eq("measure_asset --recipe exit", rc, 0)
    except Exception as exc:  # noqa: BLE001
        print("  FAIL không import/chạy được measure_asset.py:", exc)
        fails.append(f"measure_asset: {exc}")

    print()
    if fails:
        print(f"✗ {len(fails)} điểm lệch:")
        for f in fails:
            print("   -", f)
        return 1
    print("✓ tất cả khớp — planner, work order và 3 tài liệu nhất quán")
    return 0


if __name__ == "__main__":
    sys.exit(main())
