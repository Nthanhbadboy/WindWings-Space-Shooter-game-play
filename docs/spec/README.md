# SPEC — WindWings: Space Shooter

Bộ **spec hoá** game Android *WindWings: Space Shooter* (`com.Wind.wings.Space.Shooter`
v1.3.118, Unity 2022.3.62f3, IL2CPP arm64) từ kết quả dịch ngược APK.

**Mục đích:** đủ số để **dựng lại một game cùng thể loại nhưng khác hoàn toàn về art** —
không phải để clone y nguyên. Toàn bộ asset gốc (sprite, atlas, Spine, audio) thuộc bản quyền
**GCenter / GCENTER VIET NAM TECHNOLOGY JSC** và **không được tái sử dụng**.

> Đây là **tài liệu**, không phải code. Không có file nguồn game nào trong repo này.
> Mọi con số đều kèm nguồn là file dữ liệu bóc trực tiếp từ APK.

> **Đọc trước khi tin bất kỳ con số nào:** xem `AI_FEASIBILITY.md` §0.0 — quy ước **mức chắc chắn
> A/B/C/D**. Tài liệu này **không** dùng % cho thứ chưa đo, và **không** viết "không thể" cho thứ
> chỉ là "chưa chạy công cụ".
>
> **Phạm vi đã chốt:** mục tiêu là **L1 — giống cơ chế, sáng tạo phần còn lại** (`DONE.md` §4.2).
> Không cần khớp số với bản gốc, không cần test đối chiếu. Vì vậy **AssetRipper / Ghidra là tuỳ chọn**,
> và mọi con số còn thiếu chỉ là **tham khảo**, không phải điều kiện.

---

## 1. Đọc gì trước

| Nếu bạn là… | Đọc theo thứ tự này |
|---|---|
| **Designer / cân bằng số** | `GAMEPLAY.md` §0 → `BALANCE.md` §0 → `COMBAT.md` §0 → `ECONOMY.md` §0 → **`TUNING_KNOBS.md`** (núm vặn + công thức) |
| **Engineer dựng lại gameplay** | `GAMEPLAY.md` (core loop) → `COMBAT.md` (súng/đạn) → `ENCOUNTERS.md` (wave) → `UI.md` (màn hình) |
| **Art / tech art** | `ASSETS.md` §0–§5 (art direction "Ink & Ember") → `sprite-list.csv` |
| **Producer / ước lượng** | `GAMEPLAY.md` §9 (thứ tự build) → **`DONE.md`** (hoá đơn sản xuất + 4 mức kiểm) → `ASSETS.md` §7 (atlas plan) → `AI_FEASIBILITY.md` (rủi ro) |
| **AI/agent sắp dựng game** | `AI_FEASIBILITY.md` §2 (lỗ hổng) → `TUNING_KNOBS.md` (núm vặn + nơi lấy) → `ENEMY_BEHAVIOUR.md` §6 (kiến trúc enemy) |

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
| `ENEMY_BEHAVIOUR.md` | Tốc độ enemy **0,2–30** (bản cũ 800 dòng; bản đủ 981: **1,0–20,0** — xem `BOSSES.md` §5.3), **95 turret** (bản cũ), bán kính va chạm **15 unit**, biên vùng chơi **20×25**, **399** đường bay, thiên thạch, nhịp nổ boss, kiến trúc **9 component/enemy** | 248 dòng · 12 bảng |
| `AI_FEASIBILITY.md` | AI dựng lại được đến đâu — đối chiếu nghiên cứu 2025–2026 (`Spec2Game`, GameCraft-Bench, Play2Code) với lỗ hổng của bộ spec; chuỗi công cụ; xếp hạng độ khó | 505 dòng · 24 bảng |
| `TUNING_KNOBS.md` | **Toàn bộ núm vặn**: `Player_Get_Datas` 178 field, công thức giá, feel (shake/slow-mo/hit color), art scale 10,8×19,2; **giá trị nằm ở đâu** (const / prefab / `.cctor`) | ~275 dòng · 15 bảng |
| `DONE.md` | **Định nghĩa "hoàn hảo" thành 4 mức kiểm được** (L0 chạy được · L1 đúng luật · L2 đúng số · L3 không phân biệt được) + **hoá đơn sản xuất** 282 wave / 23.757 spawner / 45.659 slot `"?"` / 1.015 spawner | 168 dòng · 12 bảng |
| **`BOSSES.md`** | **39 boss** đầy đủ (HP, bộ phận, wave, va chạm) · **45/45 wave boss có boss, 0/237 wave thường** · enemy thường **70 prefab / 8 họ** · turret **21** · **87 class hành vi chưa đọc** · **§8 kiểm 7 lớp kịch bản**: sinh quân 100%, damage enemy thường **0%** (`Enemy_Physics` 981) | 477 dòng · 30 bảng |
| `DATA_SYNC.md` | **Đối chiếu với pipeline vòng 3** (nhánh `ef6b75ef`): cái gì tôi đã sai (audio 0→69 clip · enemy `?`→109 prefab · HP 800→981 dòng) và cái gì **vẫn** chưa có (IL2CPP constants = **0**) | 224 dòng · 14 bảng |
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
| HP boss (tổng/prefab) | **470 K – 14,5 M**; tổng 39 boss = **206.167.000** | `15-enemy-hp.csv` (981 dòng) | **`BOSSES.md` §2** |
| HP enemy thường | **68 / 70 prefab = 0**; 2 prefab = 20.000 | `15-enemy-hp.csv` + `Enemy_Datas.csv` | **`BOSSES.md` §6** |
| Wave / spawner / map | **282 / 23.757 / 250** | `waves.json`, `MapController.csv` | `ENCOUNTERS.md` §0 |
| Tốc độ enemy / turret | **1,0–20,0**, 85,8% rơi vào 2 nấc 5,0 và 20,0 / **21 tiền tố turret** (16,7% entry) | `Enemy_Movement.csv` (981 dòng) | **`BOSSES.md` §5.3** |
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
| 2b | `ENEMY_BEHAVIOUR` (di chuyển/đường bay/thiên thạch) · `AI_FEASIBILITY` (đánh giá + nghiên cứu) | ✅ xong |
| 2c | Cập nhật nghiên cứu **tháng 10/2026**: GameCraft-Bench 41,46% · Play2Code +37 điểm · Opus 5.5 decompile < 30 phút | ✅ xong |
| 2d | **Chuỗi công cụ** (§1.7) + **bảng đường lấy lỗ hổng** (§2.3): mỗi "chưa có" đều kèm tool + kết quả kỳ vọng | ✅ xong |
| 2e | **Xác nhận 2.5D** (§1.8): 2 `Mesh` · 0 `SkinnedMeshRenderer` · 7 `BoxCollider` 3D vs 5.424 `BoxCollider2D` | ✅ xong |
| 2f | **Xếp hạng độ khó** (§1.9): không 3D · không netcode realtime · không navmesh → **cơ chế dễ clone**, nhưng chỉ 15–20% công việc | ✅ xong |
| 2g | `TUNING_KNOBS.md` — đào lại feel/cân bằng/art bằng **tên field** trong `dump.cs`: 178 field player, công thức giá, 4.861 `[SerializeField]` | ✅ xong |
| 2h | **Ba tầng bằng chứng** (§1.11): bỏ mọi % tự chế, thay bằng số đếm được + bảng **"điều gì sẽ làm kết luận này sai"** | ✅ xong |
| 2i | **Định nghĩa "chất lượng tương đương"** (§1.12): 6 tiêu chí đo được; spec cho **v1.0**, chênh lệch tới **v1.3.118** là 118 vòng build | ✅ xong |
| 2j | **Rà lại văn phong khẳng định** (§0.0): thêm quy ước mức **A/B/C/D**, bỏ hết % độ phủ tự đánh giá, sửa 3 con số của chính mình | ✅ xong |
| 2k | `DONE.md` — 4 mức "hoàn hảo" kiểm được + hoá đơn sản xuất; tách **đơn giản** khỏi **nhỏ** | ✅ xong |
| 2l | **Chốt phạm vi L1** (§4.2): giống cơ chế, không cần giống số ⇒ bỏ L2/L3, bỏ 2 tool, bỏ 1.416 chuỗi | ✅ xong |
| 2m | `DATA_SYNC.md` — đọc dữ liệu vòng 3: **không merge**, chỉ đối chiếu; 3 kết luận cũ bị bác | ✅ xong |

**Đã sửa so với vòng 1** (đều do dữ liệu bóc lại khác bản trước): HP 981 → **800** dòng,
`Texture2D` 654 → **653**, `SkeletonDataAsset` 25 → **27**, page 66/32,5 MB → **67/31,0 MB**,
và premise "`Box_Rewards`/`Shop_Cell` có thưởng" của handoff là **sai**.

Mọi giới hạn còn lại nằm ở mục **"Còn thiếu / phải đoán"** cuối mỗi file — đó là danh sách
việc cho vòng sau, không phải lỗ hổng của spec.
