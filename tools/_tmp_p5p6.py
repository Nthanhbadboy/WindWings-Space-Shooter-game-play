_buf = {}
_ERRORS = []


def rep(p, old, new, count=1):
    if p not in _buf:
        _buf[p] = open(p, encoding="utf-8").read()
    s = _buf[p]
    if s.count(old) != count:
        _ERRORS.append((p, s.count(old), old[:70]))
        print("MISS", p, "|", old[:60])
        return
    _buf[p] = s.replace(old, new)
    print("OK", p, "|", old[:52])


COV = "docs/spec/COVERAGE_AUDIT.md"
DS = "docs/spec/DATA_SYNC.md"
DN = "docs/spec/DONE.md"
VC = "tools/verify-claims.py"

rep(COV,
    "| UI layout | \"53k file chưa kéo về\" | `datas/ui_screens.json.gz`: **55.584** file · **8.437.020** node; `_index.csv`: **797** màn · **150.131** node |",
    "| UI layout | \"53k file chưa kéo về\" | `datas/ui_screens.json.gz`: **55.584** file · **8.440.354** node (peer refresh 26/10); `_index.csv`: **797** màn · **150.131** node |")
rep(COV,
    "**Một dòng để nhớ `datas/` đang có gì:** **4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **253** boss HP · **250** map · **170** IAP · **1.416** chuỗi.",
    "**Một dòng để nhớ `datas/` đang có gì:** **4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **246** boss HP (peer refresh 26/10 — cũ 253) · **250** map · **170** IAP · **1.416** chuỗi.")
rep(DS,
    "| 3 | ~~Đơn vị đếm tổng HP boss~~ | ~~C~~ → **A** | ✅ chốt: gom theo **prefab gốc** — `datas/boss_hp.json` **253 prefab** (meta `count=253`, bỏ bản trùng scene, `hp_max` = bản mạnh nhất; pack v2 peer đo 256 — report 78/P5) |",
    "| 3 | ~~Đơn vị đếm tổng HP boss~~ | ~~C~~ → **A** | ✅ chốt: gom theo **prefab gốc** — `datas/boss_hp.json` **246 prefab** (peer refresh 26/10 — cũ 253; `hp_max` = bản mạnh nhất; bảng đối chiếu lịch sử: 254→256 report 78/P5, 253→246 §17.1) |")
rep(VC,
    '"Một dòng để nhớ `datas/` đang có gì:** **4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **253** boss HP · **250** map · **170** IAP · **1.416** chuỗi.",',
    '"Một dòng để nhớ `datas/` đang có gì:** **4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **246** boss HP (peer refresh 26/10 — cũ 253) · **250** map · **170** IAP · **1.416** chuỗi.",')
rep(VC,
    'claim("P6", AUDIT, "**55.584** file · **8.437.020** node", (55584, 8437020, 797, 150131),',
    'claim("P6", AUDIT, "**55.584** file · **8.440.354** node (peer refresh 26/10)", (55584, 8440354, 797, 150131),')
rep(DN,
    "> **Sửa lại (lần 36 — 26/10, \"cập nhật, tái kiểm ×2\" — đồng bộ reports 97+98 peer `1f2d12f6e` (batch L3) + SỰ CỐ restore local .git):**",
    """> **Sửa lại (lần 36b — 26/10, verify bắt 2 claim lệch sau khi kéo datas peer refresh):**
> `boss_hp.json` **253 → 246 prefab** (peer refresh — sửa DATA_SYNC §8 row 3 + COVERAGE_AUDIT
> dòng-một + claim P5) · `ui_screens.json.gz` nodes **8.437.020 → 8.440.354** (summary regenerate —
> COVERAGE_AUDIT + claim P6). verify PASS lại 209/0/2.
>
> **Sửa lại (lần 36 — 26/10, \"cập nhật, tái kiểm ×2\" — đồng bộ reports 97+98 peer `1f2d12f6e` (batch L3) + SỰ CỐ restore local .git):**""")

if _ERRORS:
    print("\n!!! MISS — KHÔNG GHI")
    raise SystemExit(1)
for p, s in _buf.items():
    open(p, "w", encoding="utf-8").write(s)
print("\nđã ghi", len(_buf), "file")
