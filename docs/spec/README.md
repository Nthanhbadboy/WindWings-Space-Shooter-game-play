# SPEC — WindWings: Space Shooter

Bộ **spec hoá** game Android *WindWings: Space Shooter* (`com.Wind.wings.Space.Shooter`
v1.3.118, Unity 2022.3.62f3, IL2CPP arm64) từ kết quả dịch ngược APK.

**Mục đích:** đủ số để **dựng lại một game cùng thể loại nhưng khác hoàn toàn về art** —
không phải để clone y nguyên. Toàn bộ asset gốc (sprite, atlas, Spine, audio) thuộc bản quyền
**GCenter / GCENTER VIET NAM TECHNOLOGY JSC** và **không được tái sử dụng**.

> Đây là **tài liệu**, không phải code. Không có file nguồn game nào trong repo này.
> Mọi con số đều kèm nguồn là file dữ liệu bóc trực tiếp từ APK.

---

## 1. Đọc gì trước

| Nếu bạn là… | Đọc theo thứ tự này |
|---|---|
| **Designer / cân bằng số** | `GAMEPLAY.md` §0 → `BALANCE.md` §0 → `COMBAT.md` §0 → `ECONOMY.md` §0 |
| **Engineer dựng lại gameplay** | `GAMEPLAY.md` (core loop) → `COMBAT.md` (súng/đạn) → `ENCOUNTERS.md` (wave) → `UI.md` (màn hình) |
| **Art / tech art** | `ASSETS.md` §0–§5 (art direction "Ink & Ember") → `sprite-list.csv` |
| **Producer / ước lượng** | `GAMEPLAY.md` §9 (thứ tự build) → `ASSETS.md` §7 (atelier plan) → `ECONOMY.md` §8 |

Ba file `BALANCE`, `COMBAT`, `ENCOUNTERS` là **số**; `GAMEPLAY`, `UI`, `ASSETS` là **cấu trúc**;
`ECONOMY` là **cái gì có thật và cái gì không**.

---

## 2. Danh mục file

| File | Nội dung | Kích thước |
|---|---|---:|
| `GAMEPLAY.md` | One-pager, 3 vòng lặp (30 s / 10 phút / 1 tuần), core loop, **7 `PlayMode` + 3 `PVPMode`**, 9 nhánh progression, SOURCE/SINK, meta, boss, thứ tự build | 610 dòng · 27 bảng |
| `UI.md` | `BoardManager`/`UIManager`, screen graph, **125 class UI** (53 board · 63 popup · 8 tab), điều kiện mở từng popup | 469 dòng · 17 bảng |
| `ASSETS.md` | Art direction **"Ink & Ember"**, inventory sprite/atlas/Spine/audio, atlas plan 12 page, **legal checklist** | 425 dòng · 20 bảng |
| `BALANCE.md` | HP **39 prefab boss** + so sánh 2 chương, roster tàu/drone/item, công thức damage, khung balance đề xuất | 731 dòng · 29 bảng |
| `COMBAT.md` | **458** `Gun_Attack`, histogram damage, burst pattern, **DPS lý thuyết**, súng boss, **TTK**, hitbox va chạm, đạn | 432 dòng · 21 bảng |
| `ENCOUNTERS.md` | **282 wave** / 23.757 spawner, `spawn_type`, tham số spawn, **250 map** + parallax, 299 stage | 391 dòng · 34 bảng |
| `ECONOMY.md` | `Box_Rewards`, `Shop_Cell`, `DataShopPack`, IAP **170 SKU**, `Sub_Item`, `PurchaseType` — **cái gì là số thật** | 370 dòng · 19 bảng |
| `screens.csv` | 125 dòng: `class, board_id, mo_tu_dau, popup_con, data_can_load` | 125 dòng |
| `sprite-list.csv` | 163 dòng: atlas page (size + MB thật), background, Spine, UI 9-slice, ship/drone, bullet | 163 dòng |

---

## 3. Bản đồ nguồn — số nào lấy từ file nào

Nguồn sự thật là **file dữ liệu bóc trực tiếp từ APK**, không phải tài liệu tóm tắt:

| Nhóm dữ liệu | Đường dẫn | Nuôi file spec nào |
|---|---|---|
| ScriptableObject (91 loại) | `reverse-engineering/scriptableobjects/*.csv` | `COMBAT`, `ECONOMY`, `BALANCE` |
| Bảng dữ liệu bóc sẵn | `docs/apk-analysis/*.csv` | `BALANCE`, `UI`, `ASSETS`, `ECONOMY` |
| Bản đồ wave (23.757 spawner) | `datas/waves.json` | `ENCOUNTERS` |
| Roster / IAP / item | `datas/{ships,drones,items,iap_products}.json` | `BALANCE`, `GAMEPLAY`, `ECONOMY` |
| Mã IL2CPP (enum + class) | `reverse-engineering/il2cpp/dump.cs.gz` | tất cả (enum, field name) |
| Text/graphics | `reverse-engineering/textassets/` | `ASSETS` |

**Quy ước trong mọi file:**
- Mỗi bảng ghi `(nguồn: <file>)` hoặc có cột **Nguồn**.
- Suy đoán luôn đánh dấu `> Giả định:` — không trộn với số đo được.
- Số **raw** (nguyên văn file) và số **sau khi bỏ bản trùng** được ghi tách biệt;
  xem cảnh báo nhân đôi ở `ENCOUNTERS.md` §1.3 và `COMBAT.md` §1.
- Mỗi file kết thúc bằng **"Còn thiếu / phải đoán"**, chỉ liệt kê cái thật sự thiếu.

---

## 4. Nếu chỉ đọc 10 con số

| Chỉ số | Giá trị | Nguồn | Chi tiết |
|---|---:|---|---|
| Súng serialize được | **458** (420 không trùng) | `Gun_Attack.csv` | `COMBAT.md` §1 |
| Damage/viên | **40 – 1.200**, median 400 | `Gun_Attack.csv` | `COMBAT.md` §1 |
| DPS lý thuyết của địch | **7,8 – 3.333**, median 454 | tính từ `Gun_Attack.csv` | `COMBAT.md` §4 |
| HP boss | **270 K – 11,2 M**; median ch1 4,2 M → ch2 6,0 M | `15-enemy-hp.csv` | `BALANCE.md` §2 |
| HP enemy thường | median **500 K** | `15-enemy-hp.csv` | `BALANCE.md` §2.4 |
| Wave / spawner / map | **282 / 23.757 / 250** | `waves.json`, `MapController.csv` | `ENCOUNTERS.md` §0 |
| Stage trên board map | **299** (199 Normal · 49 Combat · 26 Boss · 25 MiniBoss) | `Stage_Behaviour.csv` | `ENCOUNTERS.md` §5 |
| Class UI | **125** (53 board · 63 popup · 8 tab · 1 cell) | `08-ui-map.md` + `dump.cs`; đối chiếu `class-inventory.csv` (116) | `UI.md` §0 |
| Sprite / atlas page | **2.185 / 67 page (66 nhóm) · 31,0 MB** | `04-asset-manifest.csv` | `ASSETS.md` §0 |
| IAP SKU | **170** (không có giá) | `13-iap-products.csv` | `ECONOMY.md` §5 |

---

## 5. Cái gì **không** có trong APK

Đây là danh sách quan trọng nhất khi lập kế hoạch — **đừng thiết kế dựa vào số không tồn tại**:

| Thiếu | Bằng chứng | Hệ quả |
|---|---|---|
| **Giá** (coin/gem/IAP) | `Box_Rewards.id` = 0 (**800/800**), `Shop_Cell` không có cột giá, giá truyền runtime dạng `string` | phải tự thiết kế `ECONOMY.md` §9 |
| **Damage của player** | `Gun_Attack.forceType = Enemy` **458/458** | không có TTK tuyệt đối (`COMBAT.md` §6) |
| **HP của player** | `Player_Health.StartHealth` chỉ có trong code | không biết "sống mấy phát" |
| **Tên enemy trong wave** | `waves.json` `enemies` = `"?"` **45.659/45.659** | không map được prefab → wave |
| **Trọng số random** | không có cột `weight`/`rate` ở bất kỳ bảng thưởng nào | phải tự quyết |

8 class config **không được serialize** trong `data.unity3d` (phải decompile `libil2cpp.so`):
`Player_Get_Datas` · `Droid_Data_Balance` · `Tech_Datas` · `Stage_Get_Datas` · `Map_Get_Datas` ·
`Enemy_Data_Balance` · `Device_Get_Data` · `GameDatas`
(giải thích: `BALANCE.md` §6.0b).

---

## 6. Trạng thái

| Vòng | Nội dung | Trạng thái |
|---|---|---|
| 1 | `GAMEPLAY` · `UI` + `screens.csv` · `ASSETS` + `sprite-list.csv` · `BALANCE` | ✅ xong |
| 2 | `COMBAT` · `ENCOUNTERS` · `ECONOMY` + đồng bộ lại 4 file vòng 1 theo dữ liệu mới | ✅ xong |

**Đã sửa so với vòng 1** (đều do dữ liệu bóc lại khác bản trước): HP 981 → **800** dòng,
`Texture2D` 654 → **653**, `SkeletonDataAsset` 25 → **27**, page 66/32,5 MB → **67/31,0 MB**,
và premise "`Box_Rewards`/`Shop_Cell` có thưởng" của handoff là **sai**.

Mọi giới hạn còn lại nằm ở mục **"Còn thiếu / phải đoán"** cuối mỗi file — đó là danh sách
việc cho vòng sau, không phải lỗ hổng của spec.
