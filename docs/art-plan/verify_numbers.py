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

    print("4b) tổng 22 batch — khớp bảng §2.2 / §3.6")
    batches: dict[str, float] = {}
    for r in rows:
        if r["lane"] == "LISTING":
            continue
        batches[r["batch_id"]] = batches.get(r["batch_id"], 0.0) + num(r, "h_scope_v2")
    QUOTED = {
        "U-KIT": 227.4, "G-PARALLAX": 211.7, "E-BODY": 188.9, "B-BODY": 141.6, "U-SHOP": 140.8,
        "U-HUD": 97.9, "U-META": 84.8, "P-SHIP": 75.2, "G-UI": 72.8, "F-GLOW": 71.2, "X-PART": 48.8,
        "E-BULLET": 46.4, "B-PART": 36.1, "F-BOOM": 32.8, "P-DRONE": 26.9, "I-DROP": 24.7,
        "U-ICON": 22.6, "P-BULLET": 13.1, "X-BRAND": 10.0, "P-FX": 4.6, "F-ENEMY": 0.0, "X-TRIAGE": 0.0,
    }
    check_eq("số batch", len(batches), 22)
    for b, want in QUOTED.items():
        check(f"batch {b}", batches.get(b, 0.0), want, tol=0.06)

    print("4c) rollup theo lane — bảng §2.3 (v1 + v2)")
    LANE_V1 = {"UI": 424.3, "BG": 208.7, "ENEMY": 163.5, "BOSS": 177.7, "PLAYER": 118.5,
               "FX": 72.1, "ITEM": 19.0, "EXCL": 48.7}
    LANE_V2 = {"UI": 573.6, "BG": 284.5, "ENEMY": 235.3, "BOSS": 177.7, "PLAYER": 119.8,
               "FX": 104.0, "ITEM": 24.7, "EXCL": 58.8}
    lane1: dict[str, float] = {}
    lane2: dict[str, float] = {}
    for r in rows:
        if r["lane"] == "LISTING":
            continue
        lane1[r["lane"]] = lane1.get(r["lane"], 0.0) + num(r, "h_scope")
        lane2[r["lane"]] = lane2.get(r["lane"], 0.0) + num(r, "h_scope_v2")
    check_eq("số lane", len(lane2), 8)
    for lane, want in LANE_V1.items():
        check(f"lane {lane} v1", lane1.get(lane, 0.0), want, tol=0.06)
    for lane, want in LANE_V2.items():
        check(f"lane {lane} v2", lane2.get(lane, 0.0), want, tol=0.06)
    check("Σ lane v1", sum(lane1.values()), 1232.38)
    check("Σ lane v2", sum(lane2.values()), 1578.42)

    print("4d) tính toàn vẹn de_est / reuse_est (§3.6)")
    units_rows = [r for r in rows if r["unit"] != "overhead"]
    bad_de = [(r["row_id"], int(r["de_est"]), int(r["kept_records"] or 0)) for r in units_rows
              if r["de_est"] and not (1 <= int(r["de_est"]) <= int(r["kept_records"] or 0))]
    check_eq("0 dòng có de_est > kept hoặc < 1", len(bad_de), 0)
    bad_ru = [r["row_id"] for r in units_rows if r["de_est"]
              and abs(num(r, "reuse_est") - int(r["de_est"]) / max(1, int(r["kept_records"] or 0))) > 0.011]
    check_eq("reuse_est = de_est / kept_records", len(bad_ru), 0)
    meas = sum(int(r["kept_records"] or 0) for r in units_rows if r["de_est"])
    check_eq("bản ghi đã đo", meas, 705)
    unmeas = [r for r in units_rows if not r["de_est"] and int(r["kept_records"] or 0) > 1]
    check_eq("dòng chưa đo nhưng kept > 1", len(unmeas), 6)
    check("giờ của 6 dòng đó", sum(num(r, "h_scope_v2") for r in unmeas), 45.99)

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
        ("plan", "5.7"), ("plan", "s0-pilot-pack.csv"), ("plan", "pilot 16 asset"),
        ("plan", "Bộ hồ sơ"), ("plan", "45,99"), ("plan", "573,6"),
    ):
        ok = token in text[doc]
        print(f"  {'OK ' if ok else 'FAIL'} {doc:4s} chứa {token!r}")
        if not ok:
            fails.append(f"{doc} thiếu {token!r}")

    print("7b) liên kết S0 ↔ W1 + cổng wave + rủi ro mới")
    s0_ids = {r["id"] for r in csv.DictReader((HERE / "s0-pilot-pack.csv").open(encoding="utf-8"))}
    linked = [r for r in w1 if r.get("s0_probe")]
    check_eq("unit W1 có probe ở S0", len(linked), 8)
    check_eq("s0_probe trỏ tới asset S0 có thật",
             sum(1 for r in linked if r["s0_probe"] not in s0_ids), 0)
    check_eq("PS-01 gắn đúng S0-01 (luật 3 §5.7)",
             next(r["s0_probe"] for r in w1 if r["uid"] == "PS-01"), "S0-01")
    import re
    risks = re.findall(r"^\| \*\*(R\d+)\*\* \|", text["plan"], re.M)
    check_eq("mã rủi ro không trùng", len(risks), len(set(risks)))
    check_eq("số rủi ro §6", len(risks), 13)
    sec8 = text["plan"].split("## 8. Còn thiếu")[1]
    items = re.findall(r"^\| (\d+) \|", sec8, re.M)
    check_eq("mục §8 liên tục 1..15",
             [int(x) for x in items], list(range(1, len(items) + 1)))
    check_eq("số mục §8", len(items), 15)
    for name, doc in (("plan", text["plan"]), ("w1", text["w1"]), ("w0", text["w0"])):
        check_eq(f"{name}: không còn 'pilot 20 asset'", doc.count("pilot 20 asset"), 0)
    for token in ("### 5.8", "**R11**", "**R12**", "**R13**", "| 13 | **Ngân sách màu",
                  "| 14 | **Canvas đạn orb**", "| 15 | **10/27 slot"):
        ok = token in text["plan"]
        print(f"  {'OK ' if ok else 'FAIL'} plan chứa {token!r}")
        if not ok:
            fails.append(f"plan thiếu {token!r}")

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

    print("8c) S0 pilot pack — s0-pilot-pack.csv (§5.7)")
    s0 = list(csv.DictReader((HERE / "s0-pilot-pack.csv").open(encoding="utf-8")))
    names = {r["base_name"].strip(): r for r in rows if r["unit"] != "overhead"}
    check_eq("pilot: 16 asset", len(s0), 16)
    check_eq("pilot: mọi base_name có trong planner", sum(1 for r in s0 if r["base"] not in names), 0)
    art = sum(num(r, "h") for r in s0)
    check("pilot: Σ art", art, 20.38)
    check("pilot: Σ art + 11,62 chuẩn bị = 32", art + 11.62, 32.0)
    check_eq("pilot: đủ 9 recipe", len({r["recipe"] for r in s0}), 9)
    check_eq("pilot: blockout = 3", sum(1 for r in s0 if r["mode"] == "blockout"), 3)
    check_eq("pilot: blockout không hứa A11 (colors)", sum(1 for r in s0 if r["mode"] == "blockout" and "A11" in r["proves"]), 0)
    check_eq("pilot: asset full", sum(1 for r in s0 if r["mode"] == "full"), 13)
    check_eq("pilot: mọi asset nêu rõ chứng minh gì", sum(1 for r in s0 if not r["proves"]), 0)

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
