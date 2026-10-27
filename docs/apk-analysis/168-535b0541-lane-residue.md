# 168 — Phần còn lại của lane #29/#30: cái gì đóng được, cái gì sai lý do, cái gì chờ runtime

> **ERRATA 170 (27/10):** artifact này đọc `open_items_audit`, nên khi 170 làm audit đọc
> thêm 168/169 thì `census` và 3 check ở đây đổi theo (32/32 vẫn xanh): hai mục của
> báo cáo này nay là `CLOSED` trong audit, và n39/n40 thành `RESTATED` bởi 169.
> Byte/sha mới ở dòng Artifact; kết luận của 168 không đổi.


**Trạng thái:** `DECODED_STATIC` (chỉ đọc artifact đã pin + 8 slice + 126 bảng ScriptableObject, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Chuỗi `SetStatusRank → SetRewards → GetRewards`, toán hạng `_value = 1` và bảng vắng mặt là hằng lúc build; **giá/stock shop**, **hai handle slot `0x2ae0010/0x2ae0018`**, **độ dài mảng cấu hình** và **giá trị server** là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_lane_residue.json.gz` (4902 B, sha256 `bae0e6da7afa9da0bce8f005ef505af523e1c82742e505cb1edbffb6772ad402`)
**Báo cáo trước:** 167 (xref hàng thưởng), 166 (hộp thưởng), 165 (widget số lượng), 139 (`ArenaManager.rewards`), 132 (pack quà), 133 (bảng thưởng hunter), 127 (giá shop).
**Verifier:** `tools/verify/lane_residue.py` (~1,3 s, **32 check**) · **Test:** `tests/test_lane_residue.py` (**37 test**).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Lane còn bao nhiêu open item? | **56** item: 17 đã đóng, **14 còn mở**, 19 runtime, 3 restated, 2 actionable, 1 note | §2 |
| Ai đọc `ArenaManager.rewards` (+0x38)? | **`Board_Arena.SetRewards`** (22794144, 1344 B): `[x0+0xb8]` → `[x8+0x38]`, guard theo `[x8+0x18]`, phần tử `[x8+idx*8+0x20]`, `idx = userProfile.arenaRank` (+0x1c) | §3 |
| Ai gọi `SetRewards`? | **một**: `Board_Arena.SetStatusRank` (22793460, 576 B) @22793992 | §3 |
| Gói quà theo giờ tặng bao nhiêu? | **1** — site `SaveDataReward` duy nhất (19187472) đặt `w2 = #1` @19187452, `_device = null` | §4 |
| `MyLibrary.ToRoman` / `LanguageManager.GetText` có trong raw không? | body **không**, nhưng có **2** và **127** call-site ⇒ lý do cũ ("0 raw") chỉ đúng cho body | §5 |
| Giá/stock shop có trong dữ liệu APK không? | **không**: 126 bảng ScriptableObject, không cột giá/stock nào (chỉ `Shop_Cell.csv` có `textCost/textPrice/textStock` là **tham chiếu UI**), không có asset `Shop_Pack` | §6 |
| Hai handle slot của 133? | vẫn chặn: bảng metadata usage **không có trong repo** | §7 |

**Một câu:** trong 14 item còn mở của lane, **2 đóng được ngay** bằng code đã pin (consumer của `rewards`, toán hạng `_value`), **2 lý do phải sửa** (body vắng ≠ đường gọi vắng), **1 item hoá ra là dữ liệu không ship** (giá shop), phần còn lại hoặc là runtime hoặc cần bảng metadata không có trong repo.

---

## 1. Vì sao cần báo cáo này

167 khép nửa xref của hàng thưởng. Sau đó lane chỉ còn `open_items_audit`: 56 item, trong đó 14 còn mở và 2 "actionable". Câu hỏi đúng lúc này không phải "đào thêm cái mới" mà "**cái đang mở, cái nào đóng được bằng thứ đã có**" — vì ba trong số đó (n11, n12, n49) đã có bằng chứng nằm sẵn trong artifact của chính báo cáo đã mở chúng.

Phạm vi: chỉ đọc lại artifact + slice đã pin, cộng một lần quét 126 bảng ScriptableObject đã bóc. Không mở lại 158–167.

---

## 2. Bản kiểm kê

`open_items_audit` (56 item) phân loại: **17 CLOSED**, **14 OPEN**, **19 RUNTIME**, **3 RESTATED**, **2 ACTIONABLE**, **1 NOTE**. Báo cáo này xử lý 6 item có số thứ tự cụ thể:

| n | Báo cáo | Trạng thái cũ | Việc báo cáo này làm |
|---|---|---|---|
| 11 | 139 | OPEN | **ĐÓNG** — consumer là `Board_Arena.SetRewards` (§3) |
| 29 | 132 | OPEN | **ĐÓNG** — `_value = 1` ở site duy nhất (§4) |
| 12 | 139 | RESTATED | **SỬA LÝ DO** — body vắng, **2** call-site có (§5) |
| 49 | 137 | OPEN | **SỬA LÝ DO** — body vắng, **127** call-site có (§5) |
| 9 | 127 | OPEN | **ĐÓNG một nửa** — giá/stock không nằm trong dữ liệu APK (§6) |
| 39, 40 | 133 | ACTIONABLE | **vẫn chặn** — bảng metadata usage không có trong repo (§7) |

Phần còn lại (n18, n30, các item RUNTIME) không đổi: chúng cần dữ liệu server hoặc trạng thái máy.

---

## 3. n11 — consumer của `ArenaManager.rewards` (đóng)

139 viết "no method in this raw indexes `ArenaManager.rewards` (+0x38)" và để item mở, **nhưng chính artifact 139 đã có reader**: `read_rva = 22795328` trong `Board_Arena.SetRewards`. Chuỗi đầy đủ:

| RVA | Lệnh | Nghĩa |
|---|---|---|
| 22793992 | `bl #0x15bd1c8` | `Board_Arena.SetStatusRank` gọi `SetRewards` |
| 22795324 | `ldr x8, [x0, #0xb8]` | ArenaManager instance từ static |
| **22795328** | **`ldr x8, [x8, #0x38]`** | **`rewards`** |
| 22795332 | `cbz x8, …` | null guard |
| 22795336 | `ldrsw x9, [x20, #0x1c]` | `idx = userProfile.arenaRank` |
| 22795340 | `ldr w10, [x8, #0x18]` | `rewards.Length` |
| 22795344 | `cmp w9, w10` + `b.hs` | bounds guard |
| 22795352 | `add x8, x8, x9, lsl #3` | `&rewards[idx]` (stride 8) |
| 22795356 | `ldr x1, [x8, #0x20]` | phần tử `ArenaRewards` |
| 22795360 | `ldr w2, [x20, #0x28]` | tham số 2 = `userProfile.status` |
| 22795380 | `bl #0x15bd4e8` | `GetRewards(rankSetup, userRank)` (22795496) |

Xref: `SetRewards` có **đúng 1** caller (`SetStatusRank`, 576 B) và `GetRewards` có **đúng 1** caller (`SetRewards`). Vậy chuỗi dữ liệu là `ArenaUserProfile → SetStatusRank → SetRewards → GetRewards → 139's 10 hàng` — không có nhánh thứ hai trong 8 slice.

Cái mà 139 thật sự thiếu không phải consumer, mà là **đầu vào**: `arenaRank`/`status` là dữ liệu hồ sơ người chơi. Đó là item runtime, không phải item "không có code".

---

## 4. n29 — gói quà theo giờ tặng đúng 1 đơn vị (đóng)

132 để mở "per-call pack amount for the 20 SaveDataReward clones" vì giá trị đến từ tham số `_value`. Nó có đến từ tham số — và chỉ có **một** site gọi trong 8 slice:

| RVA | Lệnh | Tham số |
|---|---|---|
| 19187452 | `mov w2, #1` | **`_value = 1`** |
| 19187460 | `mov w1, w23` | `_index` = biến vòng lặp |
| 19187464 | `mov x3, xzr` | `_device = null` |
| 19187468 | `mov w4, w21` | `_idDrone` |
| 19187472 | `bl #0x124c9fc` | `TimeFreeRewardPack.SaveDataReward` (19188220) |

`SaveDataReward` là **một** method 1108 B / 277 lệnh với 20 nhánh store bên trong (không phải 20 call-site), nên cả 20 nhánh cùng nhận `_value = 1`. Nói cách khác: quà theo giờ **không** cộng dồn theo bậc — mỗi lần nhận là +1 đơn vị vào đúng slot mà `_index` trỏ tới.

---

## 5. n12 / n49 — "không có trong raw" chỉ đúng cho **body**

Ba lý do cũ trong audit viết theo kiểu "RVA này không xuất hiện trong raw nào". Đúng là *method* không có, nhưng *đường gọi* thì có:

| RVA | Method | Body trong 8 slice | Call-site | Ví dụ site |
|---|---|---|---|---|
| 21103836 | `MyLibrary.ToRoman` | **0** | **2** | 19885148, 21285196 |
| 21202600 | `LanguageManager.GetText` | **0** | **127** | 22736164, 22772348 |
| 19049040 | `GameConfig.ReplaceDatas` | **0** | **2** | 22806360, 19802752 |
| 19082168 | `GameConfig..cctor` | **0** | **0** | — |
| 19042256 | `GameConfig.SetupDatas` | **0** | **0** | — |

Hệ quả cho cách đọc audit:

- `GetText` bị gọi **127** lần trong mẫu — nó là đường sống của mọi chuỗi UI, nên "không đọc được body" là giới hạn của mẫu, không phải bằng chứng nó không được dùng.
- `GameConfig..cctor`/`SetupDatas` = 0 site **và** 0 body: đây mới là "không có đường nào trong mẫu", và nó khớp với kết luận của 141 (giá trị đến từ JSON server).
- `ToRoman` (bảng số La Mã cho tên rank) và `ReplaceDatas` (thay cấu hình) đều **được gọi**, chỉ là không đọc được thân.

Đây là sửa **cách viết**, không phải sửa số: 0 body vẫn là 0 body.

---

## 6. n9 — giá và stock shop không nằm trong dữ liệu APK

127 để mở "medal shop prices / stock" với lý do "prices and stock per item come from the shop config arrays, which no report in the lane decodes". Câu hỏi trước khi đào tiếp là: **các mảng đó có trong APK không?**

| Kiểm | Kết quả |
|---|---|
| Số bảng ScriptableObject đã bóc | **126** |
| Bảng có cột chứa `cost`/`price`/`stock` | **1**: `Shop_Cell.csv` — và cả 6 cột đều là `textCost/textPrice/textStock` dạng `*.m_PathID` (tham chiếu **text UI**, không phải số) |
| Asset `Shop_Pack*` | **0** |
| Cột của asset shop duy nhất (`DataShopPack.csv`) | **72** cột, toàn sprite/list (`allSpriteRewards`, `allRankSprites`, `listAvatars`, `listSpriteDrones`, `listSpritePlayers`, `cardDroneRandomSprite`, `itemRandomSprite`) + `m_Name`/`m_Script` |

Vậy giá và stock **không** ship dưới dạng số: `DataShopPack` chỉ là bảng sprite, `Shop_Pack` được dựng lúc chạy từ dữ liệu khác. Item n9 vì thế không phải "chưa ai decode" mà là "**không có gì để decode trong APK**" — phần số thuộc `MODEL_NOT_MEASURED runtime` (hoặc thuộc báo cáo dữ liệu server, ngoài lane này).

---

## 7. Cái vẫn chặn

| Item | Vì sao |
|---|---|
| n39 `rewardValues`, n40 `rewardScales` (133) | Cần **bảng metadata usage** để tên hai handle slot `0x2ae0010` / `0x2ae0018`. Bảng đó nằm trong `global-metadata.dat` của APK gốc, **không có trong repo** (đã kiểm: 0 file khớp). Không có nó thì chỉ còn suy đoán theo nội dung blob — mà 133 đã chứng minh nội dung không đủ phân biệt. |
| n18 (146) | Độ dài mảng là `ldr wT, [xConfig, #0x18]` trên object cấu hình ⇒ dữ liệu serialize, không phải code |
| n30 (132) | `Board_PVP.rewardTypes/rewardValues` là mảng instance được điền lúc chạy |
| 19 item RUNTIME | Trạng thái máy / giá trị server: `MODEL_NOT_MEASURED runtime` |

---

## 8. Giới hạn

- Mọi kết luận ở đây là **đọc code + đọc artifact**, không có lần chạy nào; "không có trong 8 slice" luôn có nghĩa "không có trong mẫu", không phải "không tồn tại".
- §6 kết luận trên **126 bảng đã bóc**; nếu pipeline bóc asset bỏ sót một bảng thì kết luận phải xét lại — số 126 lấy từ `AI1`, không phải từ lần quét này.
- §3 không khẳng định `arenaRank`/`status` mang giá trị gì; chỉ khẳng định **ai** đọc `rewards` và **theo chỉ số nào**.

---

## 9. Cách tái lập

```bash
python3 tools/verify/lane_residue.py     # in bytes/sha256/32 check, ghi lại artifact
python3 -m unittest tests.test_lane_residue -v
python3 tools/verify-claims.py           # APKD1 + AI1 đã sync theo báo cáo này
```

Verifier đọc `open_items_audit`, artifact 139/132/133, `dump.cs` và 8 slice; mọi RVA ghi dạng **thập phân**.
