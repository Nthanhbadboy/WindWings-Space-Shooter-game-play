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
    (r"^(Coin|Goigem|Coda_)", "ui", "R14 Coin_* (đã xem ảnh 03 #13-20)", "A"),
    (r"^(A_?\d|A\d+$)", "ui", "R15 A(n) = avatar/huy hiệu (ảnh 01 #41-50)", "A"),
    (r"^Avatar", "ui", "R16 Avatar*", "A"),
    (r"^(AppleInAppPurchase|ApplePay|GooglePay|GooglePlayWordmark|Google_Play_Games|ArenaMedal|BOm|BombAttack|Blink|Change|Circle6|Circle7|Circle$|Circle_2)", "ui", "R17 logo IAP/nút", "A"),
    (r"^(DF5_|HotSale_|Web2|XVideo|Shop)", "ui", "R18 ảnh chụp banner/thumb shop", "B"),
    (r"^Manh", "ui", "R19 Manh* (mảnh ghép UI)", "C"),
    # --- fx --------------------------------------------------------------
    (r"^(Circle_blue|Circle_mask|Circle_)", "fx", "R20 Circle_* = quầng sáng (ảnh 03 #1-6)", "A"),
    (r"^(Light|Gate|Ghost|Blink)", "fx", "R21 hiệu ứng hình học", "C"),
    # --- font ------------------------------------------------------------
    (r"^(Coda_|GooTest_)", "font", "R22 chữ cái của logo (ảnh 03 #9-12, #52-62)", "A"),
    # --- bộ phận ---------------------------------------------------------
    (r"^(Rock|Head|Foot|XVideo)", "items", "R23 bộ phận/mảnh rời", "C"),
]

FAMILY = re.compile(r"_\d+$")


def classify(name, atlas):
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


def main():
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    out = []
    tally = {"A": 0, "B": 0, "C": 0, "unknown": 0}
    for r in rows:
        name = r["name"]
        if r["category"] != "unclassified":
            out.append(dict(r, proposed_category=r["category"], rule="(giữ nhãn gốc)",
                            confidence="A", bucket="", needs_eye=""))
            continue
        cat, rule, level = classify(name, r.get("atlas") or "")
        if cat:
            tally[level] += 1
        else:
            tally["unknown"] += 1
        out.append(dict(r, proposed_category=cat, rule=rule, confidence=level,
                        bucket="" if cat else bucket(name),
                        needs_eye="" if cat else f'{r["contact_sheet"]}#{r["tile"]}'))
    cols = ["name", "kind", "path_id", "atlas", "bytes", "contact_sheet", "tile",
            "category", "proposed_category", "rule", "confidence", "bucket", "needs_eye",
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
