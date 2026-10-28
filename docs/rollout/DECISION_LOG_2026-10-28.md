# DECISION LOG — 2026-10-28 (lần 160)

> **Thẩm quyền:** user trả lời trực tiếp 2026-10-28. Ba câu hỏi của director đã được chốt; hai việc được lệnh làm, một session bị bỏ.
> **Phạm vi:** **chỉ edit doc** — không build, không SDK, không keystore, không store. Giữ luật `RAW_AUDIT` (không đụng `docs/spec/` ngoài mục đã chốt — mục ghi rõ bên dưới).

---

## 1. User chốt (3 câu hỏi)

| # | Câu hỏi của director | **Chốt của user** | Hệ quả |
|---|---|---|---|
| 1 | Bản Windows là paid thuần hay paid + IAP? | **F2P và IAP** | **Đổi toàn bộ lane Windows** — `Windows.Services.Store` trở lại critical path; MSIX bắt buộc |
| 2 | Có làm free trial không? | **không** | F2P ⇒ không cần trial; xóa khỏi lane |
| 3 | Phạm vi launch đầu | **Build bản Windows chạy ngay để test** | Mục tiêu là **bản runnable local**, **không phải** release. ⇒ plain `.exe`, **không cần MSIX** |
| 4 | Art + cân bằng | **Phải thiết kế lại và có nguyên mẫu để bắt chước**; balance **học kịch bản sẵn**, **không cần để ý người chơi** | Điểm này **phần nào đúng** — xem §4 |

**Chốt thêm (user):** **"không ads"** cho bản Windows.

---

## 2. Việc làm — Task 1 (sửa số + mâu thuẫn `rate` + cổng `count`)

### 2.1 Kết quả chính — **một correction quan trọng của director**

Director **đã tự sửa lại** một correction mình làm đầu tiên. `docs/HANDOFF_SPEC_FIX_25c367aca.md` §2 và claim `AQ7` trong `tools/verify-claims.py` có **cơ sở hai nguồn độc lập**:

- **spawner = 23.757** = Σ `copies` = số instance `Call_Data` — **khớp `class-inventory.csv` 23.757** (hai nguồn)
- **11.089** = số **dòng cấu hình** sau khi export gộp object trùng (khớp `count_spawners = 11089` trong file)
- **22.451** = Σ `len(enemies)` = **entry** enemy trong danh sách spawner
- **45.659** = Σ `len × copies` = instance enemy

⇒ Director **không đổi nhãn**, chỉ **làm rõ đơn vị** + thêm số bị bỏ. Việc này **không** mâu thuẫn với HANDOFF.

### 2.2 Các edit thực tế

| File | Thay đổi |
|---|---|
| `DIRECTOR_MASTER_PICTURE.md` §1 | `282 (236 campaign + 45 boss-wave)` → **`282 (236 + 45 + **1 lỗi**)`** (236+45=281 ≠ 282; khớp `ENCOUNTERS.md` §309) |
| `DIRECTOR_MASTER_PICTURE.md` §1 | headline đơm 4 đơn vị: `23.757 spawner (= Σ copies; khớp class-inventory.csv) · 11.089 dòng cấu hình · 22.451 entry · 45.659 instance enemy (Σ len×copies)` |
| `DIRECTOR_MASTER_PICTURE.md` M5 | chấp-nhận thêm **cổng `count == 0`** |
| `PORT_PLAN_SCENE_SYSTEM_MAP.md` row 6 | headline 4 đơn vị như trên |
| `PORT_PLAN_SCENE_SYSTEM_MAP.md` **S2** | **cổng mới**: *không đọc field `count` (= 0 ở 11.089/11.089 dòng) — quân tính `len(enemies) × copies`* |
| `MISSING_FOR_NEW_GAME.md` row 6 | headline 4 đơn vị + cổng `count` + `rate = 0` = 2.366 |
| `DESIGN_READINESS.md` §3 | **sửa mâu thuẫn**: `2.371`/`2.373` → **`2.366`** (số đo được, khớp `count_spawners`); thêm phân bố 6 giá trị lớn + ghi rõ 119 spawner còn lại có 20+ giá trị nhỏ |
| `DESIGN_READINESS.md` §3 | `rate = 0` **không còn "mở và chặn A7"** → **KHÉP ở mức thiết kế = B (spawn cả loạt)**, giữ **🟡 một nửa / không chặn** (đúng §2, §6) |
| `DESIGN_READINESS.md` §3.1 | bảng `rate = 0 (waves.json)` → **2.366** (trước ghi 2.371) |
| `DESIGN_READINESS.md` §6, §6.1 | `rate = 0` ghi **KHÉP 27/10 = spawn cả loạt**; A7 giữ **🟡 một nửa** (không nâng lên ✅) |
| `DESIGN_READINESS.md` §8 | **tally giữ nguyên** (4 ✅ / 4 🟡 / 1 🔴 blocker; 33 ✅ / 14 ⚠ / 1 ❌ design) — vì A7 vẫn 🟡 |
| `docs/spec/README.md` | chạy `tools/refresh-readme-sizes.py` — `DESIGN_READINESS.md` 311 → **321 dòng** (do §3 mở rộng) |

### 2.3 Kiểm tự động

```
python3 tools/verify-claims.py   →  PASS 209 · FAIL 0 · SKIP 2 · ERROR 0
python3 tools/refresh-readme-sizes.py --check →  0 lệch
```

- Trước khi edit: `RD1` và `AA2` đang đỏ.
- `AA2` đỏ là do director đổi tallies ⇒ **đã khôi phục** (A7 vẫn 🟡).
- `RD1` đỏ là **hệ quả phụ** của §3 mở rộng ⇒ **đã refresh README**.
- **209/0/2** là kết quả **sạch** — không còn FAIL nào.

---

## 3. Việc làm — Task 3 (re-baseline lane Windows → F2P + IAP, không ads)

### 3.1 Cơ sở user chốt

User: **"F2P và IAP"** + **"không ads"**. ⇒ **D3(b) khẳng định**, **D6(a) → (b)**, **D4/G9 không áp dụng Windows**, **G12 đổi thành giá IAP**, **G16 biến mất**.

### 3.2 Các edit

| File | Thay đổi |
|---|---|
| `STORE_ASSETS_AND_LISTING_DRAFT.md` §1 | MS Store Windows: *"planned premium, ad-free edition"* → **"planned free-to-play with in-app purchases, no ads"** |
| `STORE_ASSETS_AND_LISTING_DRAFT.md` §MS | heading `(premium, no ads)` → **`(free-to-play + IAP, no ads)`** |
| `STORE_ASSETS_AND_LISTING_DRAFT.md` §MS | short description: premium ad-free → **free-to-play, no ads, optional IAP, no paid loot boxes** |
| `STORE_ASSETS_AND_LISTING_DRAFT.md` §MS | long description: **"premium, ad-free release"** → **"free-to-play release with in-app purchases and no ads"** |
| `STORE_ASSETS_AND_LISTING_DRAFT.md` §MS | "Do not add yet": **a price** → **any price (app or in-app)** |
| `DECISIONS_NEEDED.md` | dãy chốt: `D3(b) hoặc (a) · D6(a)` → **`D3(b) · D6(b)`** — định vị **"Windows = F2P + IAP, không ads"** |
| `DECISIONS_NEEDED.md` §ghi-chú | **D3b CHỐT USER 2026-10-28** + hệ quả (D4/G9 không áp dụng Windows; G12 → giá IAP; **G16 biến mất**) |
| `DECISIONS_RESOLVED.md` | **Header mới**: ⚠ CHỐT USER 2026-10-28 (lần 160) — tóm tắt hệ quả toàn bộ |
| `DECISIONS_RESOLVED.md` D3 | **(b) Windows KHÔNG ads — CHỐT USER 2026-10-28** + lý do hạ tầng (MS không còn ad SDK cho game, không có plugin Godot cho SDK Windows) |
| `DECISIONS_RESOLVED.md` D4 | **chỉ áp dụng Android/Fire/AppGallery** — Windows không ads ⇒ **không có SKU "remove ads" trên Windows** |
| `DECISIONS_RESOLVED.md` D6 | **(a) → (b) Chỉ F2P — BẢN CẢI 2026-10-28**; SKU Windows = IAP; xóa khỏi lane: paid app, free trial, reserve-price tier |
| `DECISIONS_RESOLVED.md` cấu-hình-launch | `Windows = F2P + IAP, không ads (D3b/D6b — CHỐT USER 2026-10-28)`; SKU gỡ-ads gắn **chỉ Android** |
| `GATE4_GODOT_COMMERCE_QUEUE.md` | **G9 KHÔNG ÁP DỤNG Windows** — chỉ Android/Fire/AppGallery |
| `PHASE_B_COMMERCIAL_RESEARCH.md` | 2 chỗ ghi "paid premium edition" cho Windows → đánh **[SUPERSEDED 2026-10-28]** |
| `PHASE_C_EXECUTION_PLAN.md` | row D3: **eCPM/fill-rate Windows → BỊ HỦY** (không ads ⇒ không cần benchmark, không cần hợp đồng Vungle Windows) |

### 3.3 Lane Windows sau khi re-baseline

| Thứ | Trước | Sau |
|---|---|---|
| Download | paid app | **F2P (free)** |
| Kiếm tiền | paid + IAP | **IAP toàn bộ** |
| Ads | rewarded (Vungle) | **0 ads** |
| Trial | — | **không** (user chốt) |
| Quản lý phần mềm | `Windows.Services.Store` | **bắt buộc** (IAP ⇒ MSIX có identity) |
| G9 (remove ads) | áp dụng | **không áp dụng Windows** |
| G12 | giá app $7.99/$9.99/$12.99 | **giá IAP / battle pass** |
| G16 (eCPM Windows) | đo ở soft launch | **biến mất** |

---

## 4. Kiểm lại điểm user nói — "nguyên mẫu có kịch bản sẵn học tập nó, không cần để ý người chơi"

**Phần nào ĐÚNG, phần nào QUÁ MỨC.** Director đo lại trên `datas/` + `BALANCE.md` §5.

### 4.1 ĐÚNG — có công thức thật, không phải chỉ ý tưởng

`BALANCE.md` §5.1 (mức **A/B**):

| Cái đã decode | Giá trị |
|---|---|
| Damage địch | `Gun_Attack.bltDamage` **40–1.200** (457 giá trị >0) + công thức DPS đầy đủ |
| Sát thương chạm boss | `dmgFirst + dmgPerSec × t` (200–10.000 / 5–1.000) |
| **HP enemy theo id** | **150 cặp** (`datas/enemy_hp_by_id.json`) |
| `levelDelta` | **`[1, 2, 3.6, 3.6]`** — scale **thưởng**, không scale HP |
| `startBonusValues` | int[5] |
| **Tiền nhặt** | Coin1 `A=min(1,5g;16)+2,5` · Coin2 `B=min(3g;23)+12` × 4 band × L(tech) × device × .86(stage≤40) |
| damage/rate/wing/cost player | float[24] + int[24], bind combat = impl N → index N−1 |
| **`kCount ≡ 1`** | 3 nguồn độc lập — **không nhân số quân** |
| Rơi đồ 3 tầng | 702 vật đặt sẵn (676 coin / 26 item), chuỗi nổ vàng đã nối |

`MISSING_FOR_NEW_GAME.md` §4 xác nhận: **L1 = ĐỦ**; **L3 = nghiệm thu bằng đối chiếu reference đo được bằng máy, không cần playtest người thật**.

⇒ **"không cần để ý người chơi" đúng ở mức parity cơ chế/hình ảnh.**

### 4.2 QUÁ MỨC — 6 nhóm **không có số**

`BALANCE.md` §5.2 (mức **D**):

| Nhóm | Vì sao không có |
|---|---|
| **Giá nâng cấp coin/gem** | `PlayerCosts[]`, `GetUpgadeCostCoins()` — thân hàm; **0 cột giá trong 91 CSV** |
| **Tỉ lệ rơi item trong màn** | Không có field trọng số; chỉ có tỉ lệ **instance** 676 coin : 26 item |
| **Hệ số scale HP theo stage** | `Enemy_Data_Balance` + `Stage_Get_Datas` — **chưa tìm ra** (scene bundle khác) |
| **Ngưỡng VIP 1..6** | `GetVipLevel(vipPoints)` — thân hàm |
| **Giá energy / trận** | `Stage_Datas.CostOverDrive`, `CostItems[]` |
| **Rank threshold arena** | **Nằm trên Firebase** (server) |

Plus `BALANCE.md` §5.1: **damage player chỉ có công thức dạng** — *"thứ tự nhân và hệ số cụ thể không xác định"*.

⇒ Nhóm này **không có kịch bản để học**. Nếu game thương mại muốn progression có nghĩa (giá nâng cấp, tỉ lệ rơi, VIP), **phải tự thiết kế**. Đây chính là chỗ **"không cần để ý người chơi" không áp dụng** — vì nó ảnh hưởng revenue.

### 4.3 Kết luận về điểm này

- **Học nguyên mẫu để làm cơ chế đúng** → ✅
- **Không dùng nguyên mẫu để xác định số cân bằng thương mại** → ❌ (6 nhóm mức D + damage player)
- **"Không cần playtest người thật"** → ✅ cho L3 parity; ❌ cho commercial viability (D1/D7/D30 retention, ARPDAU, conversion — **G16: đo ở soft launch, không dự đoán**)

---

## 5. Session bị bỏ

User: **"session đó bỏ"** — **không soạn prompt cho session Godot-coder** (việc director đề xuất ở cuối round trước).

⇒ **Không tạo prompt build.** Lane "build bản Windows chạy ngay" **chưa có owner/prompt** — cần user ra lệnh lại nếu muốn.

---

## 6. Việc còn lại sau lần 160

| # | Việc | Trạng thái | Chú |
|---|---|---|---|
| 1 | **Build bản Windows runnable local** (vertical slice S1–S5, plain `.exe`) | **Không owner** (session bị bỏ) | User ra lệnh mới |
| 2 | **MSIX packaging + `Windows.Services.Store` GDExtension C++/WinRT** | plan-level | **Bắt buộc** khi bắt đầu IAP |
| 3 | **Reserve app name Partner Center + `Identity@Name/@Publisher`** | **thiếu trong plan** | predecessor của MSIX build |
| 4 | **CI cổng MSIX** (MakeAppx pack · version 4 thành phần · Publisher = cert CN · WACK) | **thiếu trong plan** | G1–G4 chưa có |
| 5 | **IARC + privacy policy URL** | đáp án có sẵn | cần host URL (G2) |
| 6 | **G10** consumable vs subscription store | mở | MS không cho nâng giá subscription |
| 7 | **G12** giá IAP / battle pass Windows | mở | thay cho giá app |
| 8 | **Quyền IP / phân phối** (Gate-4) | **USER-ONLY, chưa trả lời** | **chặn mọi lane** |
| 9 | **G13** bộ store sau Alexa Tablet | mở | Amazon Fire → Alexa Tablet (Android + GMS) |

---

## 7. Kiểm tra cuối

```
$ python3 tools/verify-claims.py
PASS 209 · FAIL 0 · SKIP 2 · ERROR 0

$ python3 tools/refresh-readme-sizes.py --check
0 lệch
```

**Branch:** `arena/e235c1c0-windwings-space-shooter-game-p`
**Nền:** tip `f956655800fb8dbb11f11d4758d684928dd442c7` (`arena/20330d0e`, 27/10 "lần 159") + corrections lần 160.
