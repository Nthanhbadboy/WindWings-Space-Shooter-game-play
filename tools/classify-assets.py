#!/usr/bin/env python3
"""Sinh docs/assets/sprites-classified.csv từ docs/assets/sprites-index.csv.

Mục đích: bộ ảnh gốc còn 1.554/2.197 sprite `unclassified`. Script này gán nhãn
**chỉ khi có bằng chứng** (tên tự mô tả, hoặc đã xem contact sheet), và đánh dấu
phần còn lại là `unknown` kèm toạ độ tile để người sau xem ảnh.

Chạy: python3 tools/classify-assets.py
Xuất: docs/assets/sprites-classified.csv
"""
import csv
import re
import sys
from pathlib import Path

SRC = Path("docs/assets/sprites-index.csv")
OUT = Path("docs/assets/sprites-classified.csv")

# (regex trên tên, nhãn, mã luật, mức). Thứ tự quan trọng: luật đầu khớp thì thôi.
# Mức A = tên tự mô tả hoặc đã xem contact sheet xác nhận; B = suy từ tên nhóm;
# C = suy từ tương tự tên, phải xem ảnh.
RULES = [
    # --- đạn -------------------------------------------------------------
    (r"^blt", "bullet", "R01 blt_*", "A"),
    (r"^(20(1[1-5])|40(1[1-5]))$", "bullet", "R02 sheet đạn (thấy ảnh 01 #18-22,#31-35)", "A"),
    # --- boss ------------------------------------------------------------
    (r"^(boss_|boss[A-Z0-9]|miniboss|mini_boss)", "bosses", "R03 boss_*", "A"),
    (r"^(sieuhopthe|sieuhopthetachbophan)", "bosses", "R04 siêu hợp thể = boss ghép", "B"),
    # --- enemy -----------------------------------------------------------
    (r"^(CB|CD)-", "enemy", "R05 mã prefab enemy CB-/CD-", "A"),
    (r"^E_", "enemy", "R06 E_* (mảnh/prefab enemy)", "B"),
    (r"^DA-\d", "enemy", "R07 DA-2xxxx (đạn/kỹ năng boss? - họ số 20001-20012)", "C"),
    # --- background ------------------------------------------------------
    (r"^(bg|Bg|BG)", "background", "R08 bg*", "A"),
    (r"^(Nen|Background)", "background", "R09 Nền*", "A"),
    (r"^(Earth|Mars|Moon|Jupiter|Venus|Saturn|Neptune|Cloud_|Nebula)", "background", "R10 tên hành tinh/mây", "A"),
    # --- ui --------------------------------------------------------------
    (r"^(Khung|NenAvatar|NenBoss|Hotro|Vip|Goigem|Shop_|Stat|SubStat|Nut|Overdrive_|_Hp_|Hoicham|Hoisinh|NoAds|Notice|CheckBox|Lock|Knob|Loading|Line|Number|End$|End1$|Enegry|Gift_Box|Finger|Hand$|Alert|Cover$|PA$|Dot$)", "ui", "R11 khung/nút/icon UI", "A"),
    (r"^(Rank\d|Rank_)", "ui", "R12 Rank* = huy hiệu rank", "A"),
    (r"^PVP\d", "ui", "R13 PVP* = huy hiệu PVP", "A"),
    (r"^(Coin|Goigem)", "ui", "R14 Coin_* (đã xem ảnh 03 #13-20)", "A"),
    (r"^(A_?\d|A\d+$)", "ui", "R15 A(n) = avatar/huy hiệu (ảnh 01 #41-50)", "A"),
    (r"^Avatar", "ui", "R16 Avatar*", "A"),
    (r"^(AppleInAppPurchase|ApplePay|GooglePay|GooglePlayWordmark|Google_Play_Games|ArenaMedal|BOm|BombAttack|Blink|Change|Circle6|Circle7|Circle$|Circle_2)", "ui", "R17 logo IAP/nút", "A"),
    (r"^(DF5_|HotSale_|Web2|XVideo|Shop)", "ui", "R18 ảnh chụp banner/thumb shop", "B"),
    (r"^Manh", "ui", "R19 Manh* (mảnh ghép UI)", "C"),
    (r"^Boss\w*Gray$", "ui", "R26 Boss*Gray = chân dung boss chưa mở (xám)", "B"),
    (r"^Boss", "bosses", "R27 Boss* (chân dung/khung boss)", "B"),
    (r"^Border", "ui", "R28 Border* = viền khung", "B"),
    (r"^Body", "parts", "R29 Body* = thân rời", "B"),
    (r"^Bone", "parts", "R31 Bone* = khúc/xương rời", "B"),
    (r"^(Bong_Den|Botro)", "ui", "R32 bóng đèn / bổ trợ (icon UI)", "B"),
    # --- fx --------------------------------------------------------------
    (r"^(Circle_blue|Circle_mask|Circle_)", "fx", "R20 Circle_* = quầng sáng (ảnh 03 #1-6)", "A"),
    (r"^(Bomb|Boom)", "fx", "R33 Bomb/Boom = nổ", "B"),
    (r"^(Light|Gate|Ghost|Blink)", "fx", "R21 hiệu ứng hình học", "C"),
    # --- drone / tàu ------------------------------------------------------
    (r"^drone", "drones", "R24 drone*", "A"),
    (r"^mini_ship", "ships", "R25 mini_ship*", "A"),
    # --- font ------------------------------------------------------------
    (r"^(Coda_|GooTest_)", "font", "R22 Coda/GooTest = họ font (tên font, chưa xem ảnh)", "B"),
    # --- bộ phận ---------------------------------------------------------
    (r"^(Rock|Head|Foot)", "items", "R23 bộ phận/mảnh rời", "C"),
]

# Nhãn xem **bằng mắt** trên contact sheet: (số sheet, tile) -> (nhãn, luật, mức).
# Chỉ ghi cái đã nhìn thấy; tile không chắc thì để trống cho vòng sau.
EYE = {
    7: {5: "fx", 6: "drones", 7: "ui", 8: "ships", 9: "ships", 10: "ui", 11: "ui", 12: "ui",
        13: "items", 14: "items", 15: "ui", 16: "enemy", 17: "parts", 18: "parts", 19: "parts",
        20: "parts", 21: "parts", 22: "parts", 23: "parts", 24: "parts", 25: "parts", 26: "parts",
        27: "parts", 28: "enemy", 29: "parts", 30: "parts", 31: "parts", 32: "parts", 33: "bullet",
        34: "bullet", 35: "bullet", 36: "bullet", 37: "parts", 38: "fx", 39: "parts", 40: "parts",
        41: "parts", 42: "parts", 43: "bullet", 44: "parts", 45: "parts", 46: "parts", 47: "parts",
        48: "parts", 49: "parts", 50: "parts", 51: "parts", 52: "enemy", 53: "parts", 54: "parts",
        55: "bullet", 56: "ui", 57: "enemy", 58: "parts", 59: "parts", 60: "enemy", 61: "ui",
        62: "ui", 63: "ui", 64: "parts"},
    8: {1: "parts", 2: "parts", 3: "enemy", 4: "items", 5: "enemy", 6: "parts", 7: "enemy",
        8: "parts", 9: "enemy", 10: "enemy", 11: "bullet", 12: "parts", 13: "parts", 14: "drones",
        15: "parts", 16: "enemy", 17: "bullet", 18: "bullet", 19: "enemy", 20: "parts", 21: "ui",
        22: "enemy", 23: "parts", 24: "bullet", 25: "ui", 26: "ui", 27: "ui", 28: "fx", 29: "ui",
        30: "ui", 31: "ui", 32: "ui", 33: "parts", 34: "parts", 35: "items", 36: "items",
        37: "parts", 38: "ui", 39: "ui", 40: "ui", 41: "parts", 42: "ui", 43: "ui", 44: "ui",
        45: "items", 46: "items", 47: "items", 48: "ui", 49: "parts", 50: "parts", 51: "ui",
        52: "fx", 53: "fx", 54: "fx", 55: "parts", 56: "parts", 57: "parts", 58: "parts",
        59: "ui", 60: "parts", 61: "fx", 62: "parts", 63: "parts", 64: "parts"},
}

FAMILY = re.compile(r"_\d+$")


def sheet_no(contact_sheet):
    m = re.search(r"unclassified-(\d+)\.jpg", contact_sheet or "")
    return int(m.group(1)) if m else 0


def classify(name, atlas, eye=None, sheet=0):
    if eye:
        return eye, f"R30 xem contact sheet {sheet:02d}", "A"
    for pat, cat, rule, level in RULES:
        if re.search(pat, name):
            return cat, rule, level
    return "", "", ""


def bucket(name):
    if re.fullmatch(r"\d+(\.\d+)?[a-zA-Z]?", name) or re.fullmatch(r"[A-Za-z]?\d+(_\d+)?", name):
        return "numeric"
    if re.fullmatch(r"[A-Za-z][A-Za-z _.\-]{0,20}", name):
        return "word"
    return "other"


def rule_id_of(rule):
    m = re.match(r"(R\d+)", rule or "")
    return m.group(1) if m else ""


def shadowed_rules(names):
    """Luật **không bao giờ** thắng vì luật đứng trước đã bắt hết tên.

    Đây là lỗi `R14` che `R22` (Coda_*) và `R18` che `R23` (XVideo) mà review
    `25c367aca` bắt được: bảng tài liệu liệt kê nhãn theo một luật, nhưng dữ liệu
    ra lại theo luật khác. Trả [(rule, số tên bị che)].
    """
    out = []
    for i, (pat, _cat, rule, _lvl) in enumerate(RULES):
        rx = re.compile(pat)
        hit = miss = 0
        for n in names:
            if not rx.search(n):
                continue
            if any(re.search(p, n) for p, *_ in RULES[:i]):
                miss += 1
            else:
                hit += 1
        if miss and not hit:
            out.append((rule, miss))
    return out


def main():
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    out = []
    tally = {"A": 0, "B": 0, "C": 0, "unknown": 0}
    for r in rows:
        name = r["name"]
        if r["category"] != "unclassified":
            # Nhãn lấy từ cột `category` (raw class) — KHÔNG phải audit lại.
            # Vì vậy confidence để trống, và ghi rõ nguồn; đừng gộp với mức A của luật.
            out.append(dict(r, proposed_category=r["category"], rule="(giữ nhãn gốc)",
                            confidence="", label_source="category_passthrough",
                            rule_id="", evidence_ref="sprites-index.csv:category",
                            reviewed="false", bucket="", needs_eye=""))
            continue
        eye_cat = EYE.get(sheet_no(r["contact_sheet"]), {}).get(int(r["tile"]))
        cat, rule, level = classify(name, r.get("atlas") or "", eye_cat,
                                    sheet_no(r["contact_sheet"]))
        if cat:
            tally[level] += 1
        else:
            tally["unknown"] += 1
        out.append(dict(r, proposed_category=cat, rule=rule, confidence=level,
                        label_source="eye" if eye_cat else ("rule" if cat else "unknown"),
                        rule_id=rule_id_of(rule),
                        evidence_ref=("docs/assets/contact-sheets/" + r["contact_sheet"]
                                      if eye_cat else ("NAME_RULES" if cat else "")),
                        reviewed="true" if (eye_cat or level in ("A", "B")) else "false",
                        bucket="" if cat else bucket(name),
                        needs_eye="" if cat else f'{r["contact_sheet"]}#{r["tile"]}'))
    sh = shadowed_rules([r["name"] for r in rows])
    if sh:
        print("CẢNH BÁO luật bị che (không bao giờ khớp):",
              ", ".join(f"{r} ({n} tên)" for r, n in sh))
    cols = ["name", "kind", "path_id", "atlas", "bytes", "contact_sheet", "tile",
            "category", "proposed_category", "rule", "confidence", "label_source",
            "rule_id", "evidence_ref", "reviewed", "bucket", "needs_eye",
            "relative_path"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in cols})
    print(f"rows={len(out)} labeled_AB={tally['A'] + tally['B']} labeled_C={tally['C']} "
          f"unknown={tally['unknown']} -> {OUT}")


if __name__ == "__main__":
    sys.exit(main())
