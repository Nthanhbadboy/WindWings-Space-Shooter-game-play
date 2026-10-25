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
| **Producer / ước lượng** | **`COVERAGE_AUDIT.md`** (còn thiếu gì, cái gì chặn) → `GAMEPLAY.md` §9 (thứ tự build) → **`DONE.md`** (hoá đơn sản xuất + 4 mức kiểm) → `ASSETS.md` §7 (atlas plan) → `AI_FEASIBILITY.md` (rủi ro) |
| **AI/agent sắp dựng game** | `AI_FEASIBILITY.md` §2 (lỗ hổng) → `TUNING_KNOBS.md` (núm vặn + nơi lấy) → `ENEMY_BEHAVIOUR.md` §6 (kiến trúc enemy) |

Ba file `BALANCE`, `COMBAT`, `ENCOUNTERS` là **số**; `GAMEPLAY`, `UI`, `ASSETS` là **cấu trúc**;
`ECONOMY` là **cái gì có thật và cái gì không**.

---

## 2. Danh mục file

| File | Nội dung | Kích thước |
|---|---|---:|
| `GAMEPLAY.md` | One-pager, 3 vòng lặp (30 s / 10 phút / 1 tuần), core loop, **7 `PlayMode` + 3 `PVPMode`**, 9 nhánh progression, SOURCE/SINK, meta, boss, thứ tự build | 689 dòng · 31 bảng |
| `UI.md` | `BoardManager`/`UIManager`, screen graph, **125 class UI** (53 board · 63 popup · 8 tab), điều kiện mở từng popup · **§9 manifest `_index.csv`: 733 instance · 114 lớp · 103.227 node · 5.174 nút** (giải thích luôn vì sao 114 ≠ 125) | 511 dòng · 19 bảng |
| `ASSETS.md` | Art direction **"Ink & Ember"**, inventory sprite/atlas/Spine/audio, **atlas plan 12 page đã kiểm bằng px² thật (§4.5)**, **legal checklist** | 530 dòng · 25 bảng |
| `BALANCE.md` | HP **39 prefab boss** + so sánh 2 chương, roster tàu/drone/item, công thức damage, khung balance đề xuất | 1577 dòng · 65 bảng |
| `COMBAT.md` | **458** `Gun_Attack`, histogram damage, burst pattern, **DPS lý thuyết**, súng boss, **TTK**, hitbox va chạm, đạn | 483 dòng · 20 bảng |
| `ENCOUNTERS.md` | **282 wave** / **11.092 spawner** / **45.659 quân**, `spawn_type`, tham số spawn, **250 map** + parallax, 299 stage | 660 dòng · 30 bảng |
| `ECONOMY.md` | `Box_Rewards`, `Shop_Cell`, `DataShopPack`, IAP **170 SKU**, `Sub_Item`, `PurchaseType` — **cái gì là số thật** | 375 dòng · 17 bảng |
| `ENEMY_BEHAVIOUR.md` | Tốc độ enemy **0,2–30** (bản cũ 800 dòng; bản đủ 981: **1,0–20,0** — xem `BOSSES.md` §5.3), **95 turret** (bản cũ), bán kính va chạm **15 unit**, biên vùng chơi **20×25**, **399** đường bay, thiên thạch, nhịp nổ boss, kiến trúc **9 component/enemy** | 248 dòng · 12 bảng |
| `AI_FEASIBILITY.md` | AI dựng lại được đến đâu — đối chiếu nghiên cứu 2025–2026 (`Spec2Game`, GameCraft-Bench, Play2Code) với lỗ hổng của bộ spec; chuỗi công cụ; xếp hạng độ khó | 650 dòng · 32 bảng |
| `TUNING_KNOBS.md` | **Toàn bộ núm vặn**: `Player_Get_Datas` 178 field, công thức giá, feel (shake/slow-mo/hit color), art scale 10,8×19,2; **giá trị nằm ở đâu** (const / prefab / `.cctor`) | 310 dòng · 18 bảng |
| `DONE.md` | **Định nghĩa "hoàn hảo" thành 4 mức kiểm được** (L0 chạy được · L1 đúng luật · L2 đúng số · L3 không phân biệt được) + **hoá đơn sản xuất** 282 wave / 23.757 spawner / 45.659 slot `"?"` / 1.015 spawner | 356 dòng · 18 bảng |
| **`BOSSES.md`** | **39 boss** đầy đủ (HP, bộ phận, wave, va chạm) · **45/45 wave boss có boss, 0/237 wave thường** · enemy thường **70 prefab / 8 họ** · turret **21** · **87 class hành vi chưa đọc** · **§8 kiểm 7 lớp kịch bản**: sinh quân 100%, damage enemy thường **0%** (`Enemy_Physics` 981) | 585 dòng · 22 bảng |
| **`PIPELINE_AUDIT.md`** | **Đánh giá nhánh phân tích ngược:** 42 commit thật/4h39 · 5/6 tuyến cho dữ liệu thật · **lạc ở IL2CPP constants** (60/98 dòng là rác `288733`) · **`Enemy_Physics` 981 không có trong `TARGETS`** · 3 dòng code mở 100% lớp hành vi | 424 dòng · 26 bảng |
| **`ANIMATION.md`** | **4 hệ animation:** Spine **27 rig / 180 animation / 616 bone** (đọc 100%, có event bắn trong rig) · Unity Animator **791 clip / 308 controller / 5.792 instance** (**0 %** curve giải được — **9,19 MB** chưa giải · **100 % tên**; **62,5 % là UI**, enemy chỉ **203**) · `Rotate` **1.044** instance · flipbook **0 clip** (`m_PPtrCurves` **0/791**; 28 chuỗi/160 ảnh chỉ là tên sprite) ⇒ game **không dùng khung hình**. **§4.5 đếm riêng enemy**: `Enemy_Movement` **109/109** · `Enemy_Appear` **107/109** · Animator **87/109** · Spine chỉ **2 boss** | 413 dòng · 20 bảng |
| **`SCRIPTS.md`** | **3 tầng: số — kịch bản — mã.** Bằng chứng "số liệu chết" (`CurrentHealthPoint` = 0 ở **981/981**); **§0.5 luồng mở game lần đầu** (5 scene · 39 board · tutorial **5 bước** chạy trong trận); 5 lớp kịch bản; **giải mã timeline bắn** (6 tham số, **102 pattern**/516 slot); timeline spawn (**1 con/1,0 s · y 9,6 · radius 0,1**); pha boss **63 instance** (112 field damage đã đọc) | 339 dòng · 15 bảng |
| **`DESIGN_QUESTIONS.md`** | **48 câu hỏi designer phải trả lời** để làm game mới: ✅ **29 có số** · ⚠ **11 một phần** · ❌ **8 chưa trả lời** — cả 8 câu ❌ đều là **blocker**, xếp theo chi phí trả lời.
| **`ANIMATION_SCRIPT.md`** | **Script animation enemy + boss** (code gọi animation nào, lúc nào — không phải feel). **Hai hệ độc lập**: Spine (`Boss-39001/2`, **0 event clip**, điều khiển bằng `Boss1_Director` → `AnimationState.SetAnimation`) và AnimationClip + event (**33 prefab boss · 793 event · 2 ngoài boss**; 129 tên hàm). **268 cặp (prefab, clip)** — **61 cặp** có ≥3 event nên đọc được nhịp: **0,17 · 0,33 · 1,0 · 5,0 s**, chuỗi 8–14 đòn/boss, `idle` cũng bắn đòn. **12 handler `Boss1_AnimationEvents` = 28 byte, chỉ gọi delegate** (hành vi nằm ở UnityEvent, mức **C**). **Enemy không có timeline** ⇒ máy trạng thái (`Enemy_Movement.Update` 3 nhánh) + hit flash **0,05 s** qua `Invoke`. **22 lần `WaitForSeconds` · 4 hằng số · 18 lấy từ biến**. | 287 dòng · 12 bảng |
| **`COVERAGE_AUDIT.md`** | **Kiểm lại toàn bộ: thiếu chỗ nào?** Chia game thành **14 vùng năng lực** và đếm cái đang có: **10 vùng đủ** (A/B) · **3 thiếu một phần** (điều kiện Animator · FX curve · trigger âm thanh) · **1 thiếu** (feel, cần máy). **6 chỗ còn thiếu**, chỉ **2 chặn dựng** (map→wave numbering · HP runtime theo chế độ). **§3 tưởng-thiếu-nhưng-đã-có**: sprite 2.885 có kích thước · bản địa hoá **1.416 key × 19 ngôn ngữ** · IAP **170** · FX **4.845** · UI **52.583** file layout. **§4 ba cặp số dễ tráo** (UI 733 vs 52.583 · audio 69 vs 92 · sprite 2.885 vs 2.185). | 125 dòng · 5 bảng |
| **`HANDOFF_ANIM_RAW.md`** | **Lô 4 việc đào raw giao nhánh dữ liệu** (theo chỉ đạo *"cần đào raw thì giao bên kia"*): **T1** 3 lớp có asm mà **chưa có typetree** (`Boss1_AnimationEvents`, `BossSpineEventHandler`, `Boss_1_Animation`) · **T2** ai gán **12 delegate field `0x20`…`0x78`** (mở khoá 793 event) · **T3** `UnityEvent` persistent calls · **T4** tham số + transition `Animator` của 87 prefab roster · **T5** `rate = 0` nghĩa là gì (mật độ địch). Kèm **§0 danh sách đã xong — đừng làm lại** (8 tên entry, bảng chuyển state, nhịp đòn) và hợp đồng `verdict.json` + exit 0/2/3. | 201 dòng · 4 bảng |
| **`DESIGN_READINESS.md`** | **Đã đủ thiết kế chưa?** → **ĐỦ cho L1** (giống cơ chế, không cần giống số). **Vòng 2 (sau script animation)**: **35/39 prefab boss** có script đọc được · boss 1 giải xong **8 tên entry + 5 nhánh** · hit flash **0,05 s / alpha 0,5** (hết trống dữ liệu) · UI cấu trúc **125 màn hình** ⇒ **9/10 mục** design doc viết được ngay. Còn treo: `rate = 0` (đã hẹp còn **B**) · A6 stage↔wave · feel phải **quyết** chứ không đo. **10/10 mục** design doc viết được ngay. | 189 dòng · 7 bảng |
| `DATA_SYNC.md` | **Đối chiếu với nhánh dữ liệu qua 9 bản** (`821efc5` → `cd0372d`): cái gì tôi đã sai (audio 0→69 · enemy `?`→109 prefab · HP 800→981 · 981 **không phải** 981 enemy · 42→**68** prefab súng) · **§9 sổ theo dõi 11 mắt ghép 100%** · **§10 kéo `scriptableobjects/` (1.339 file, 7,8 MB)**: `Call_Data.csv` = **1.200 dòng · 23 field**, **không có `delay`** ⇒ `rate` là field thời gian duy nhất; `number = 0` ở 1.200/1.200 ⇒ số quân = độ dài list. Kèm lý do **không** kéo cây `raw/ui` (53.318 file, 142,7 MB) — nhưng **có** kéo **2 manifest** của nó (`_index.csv`, `_skipped.csv`) và **140 file md/csv** của `docs/apk-analysis/`, trong đó `spine-events.csv` (**21 dòng**) xác nhận rig boss 1 chỉ có **2 tên event**. | 1644 dòng · 89 bảng |
| **`ASM_INTEGRITY.md`** | **Gác cổng chống cắt cụt im lặng**: sự cố 4.608 B/method · **3 cờ tự kiểm** (`size_capped` · phủ địa chỉ · opcode cuối) · **script · 2 bảng chạy được, nhúng nguyên văn** · **baseline 17 class** (16/17 PASS, `RankManager` thiếu 8 B) · **quy tắc "được phép phủ định"** | 293 dòng · 3 bảng |
| **`ENEMY_HP_RUNTIME.md`** | **Enemy thường KHÔNG chết 1 phát** — **109/109** prefab được spawn có HP bar (**909** instance `Enemy_Hp_Bar`, **909/909 `m_Enabled=1`**; thêm đường `Enemy_Display.hpProgressBarRenderer` **976/981**). ❌ rút lại câu "HP bar chỉ trên boss". **HP thực tế = bảng × `kHp[mode]`** (→ `DIFFICULTY_MODES` §5). Nguồn HP: `Enemy_Get_Datas` → **`Dictionary<int,float>` trong `.cctor 0x157F7CC`** (**chưa** có trong `TARGET_CLASSES`). **Enemy cũng có giáp** (`armor @0x34`). Và **"treo máy" không phải vì HP**: **12 quân/s**, **~50–950 con**, **~40–100 phép tính HP/s** vs 10⁹ ops/s | 228 dòng · 9 bảng |
| **`DIFFICULTY_MODES.md`** | **3 chế độ: không nhân số quân — chỉ đổi ngưỡng %, thưởng, năng lượng (+ HP).** `kCount ≡ 1` (**A**, ba nguồn: người chơi kiểm lại · `GetCountEnemies` **304 lệnh · 0 `mul`** · `GetListWaves` **278 lệnh · 0 phép nhân**). Kênh **có** thay đổi: `pct[mode]` · `levelDelta[mode]` (**`float[]` index bằng `ModeCurrent`**, `cmp w9,w20` + `b.ls throw`) · `GetCostEnergyForPlay(stageIndex, stageLevel)`. **Vì sao "thấy đông hơn"**: Little's law — HP cao ⇒ sống lâu ⇒ **cùng lúc nhiều hơn** (47–157 → ~70–235) với **cùng** 45.659 quân. **"Số quân không theo quy luật"**: CV **1,01** · median **131** · max **951** · **150/282** giá trị khác nhau · HP bar **109/109** | 449 dòng · 17 bảng |
| **`MISSIONS_STARS.md`** | **Ngưỡng sao = `(int)( pct[mode][slot] × countEnemies )`** — asm `ldr w21,[x9,#0x34]` (`ModeCurrent`) → `GetKillPercentMissionComplete` → `scvtf`/`fmul`/`fcvtzs`; mẫu số **giống nhau** ở 3 chế độ ⇒ **UI in đúng số** (bạn xác nhận). `IsMissionCompleted` = **`completed > missionIndex`** ⇒ **cộng dồn ⇒ 1/2/3 sao**; sao lưu theo **(stage, mode)**. Loại nhiệm vụ xoay theo **`stageIndex % 6`**. `GetCountEnemies` **304 lệnh · 0 `mul`** ⇒ **cộng bảng, không đếm spawn**. **`pct` = 9 số** — `GetKillPercentMissionComplete` ∈ `Player_Get_Datas` (188 B, 3 mảng `static float[3]` + `memcpy`); giá trị còn thiếu vì `InitializeArray` (`debug_rva` resolve **2/1.929 = 0,1 %**). Kèm phân bố số quân (**CV 1,01**) và cách đo `pct` bằng **3 con số trên UI** | 272 dòng · 7 bảng |
| **`EXTERNAL_REFS.md`** | **Không có ai phân tích ngược game này.** 6 loại nguồn: 2 repo GitHub quét manifest (`beerphilipp/taptrap` · `tabbed-out` → `target_sdk **34**`, **77 activity**, **3 package name** cùng họ) · ~30 trang mod APK (**danh sách mod = bản đồ "cái gì ở client"**: One Hit Kill ⇒ HP enemy client-side · High Gold Attraction ⇒ rơi vàng quyết định lúc vào màn) · r/Windwingsgame (403) · YouTube · **wiki Galaxy Attack = GAME KHÁC, cấm trích số** · metadata store. Kèm **phép tìm đã chạy** (`windwings il2cpp` → **0**) và hệ quả: *repo này là nguồn duy nhất có số* | 169 dòng · 10 bảng |
| **`UNITY_RULES.md`** | **Luật engine tự chốt 6 mục**: field chỉ serialize khi `public`/`[SerializeField]` ⇒ `armor` **0/981** (enemy **không** giáp per-prefab) · PPtr null ⇒ `dataScript` **23.570/23.570** rỗng (**C3 đóng**) · `autoCacheColliders = false` **981/981** (**C6 đóng**) · `indexWave` **686/686 = 0** (**C4 đóng**) · `m_PPtrCurves` **0/791** ⇒ **không flipbook** · `m_MuscleClipSize` **9,19 MB** trên **782 clip** ⇒ curve **có thật**, thiếu decoder · `m_Events` **793** + `m_AnimationClips` **793** + `m_TOS` **3.871** ⇒ **C1/C2 hạ D → B** · `static` không serialize ⇒ **`kHp`/`pct` không nằm trong asset** | 378 dòng · 18 bảng |
| **`WHERE_TO_LOOK.md`** | **Chẩn đoán 3 blocker theo nguyên nhân, không theo độ khó**: `.cctor` `Map_Get_Datas` **1,1 % RVA** (dữ liệu **viết thẳng** ⇒ chỉ cần parser) vs `Device_Get_Data` **47,6 % RVA** (⇒ cần relocation) vs `Enemy_Health` **chỉ có `noDamage`** (⇒ phải **quyết**). Gồm **phép kiểm thứ tự đã THẤT BẠI** (117 cặp **không** phải map→wave) và **quy tắc phép kiểm rỗng** | 217 dòng · 9 bảng |
| **`VERIFY_ROUND1.md`** | **Kiểm chéo 6 phán quyết của nhánh dữ liệu** (`68ce86a7`): 4/6 đúng nguyên · **`T2` sai cơ chế** (`ends_clean` **True rỗng** che 25 method vắng mặt) · **`T4` phép kiểm yếu** (`#0x2711` là **trừ** không phải cộng) · **`T6` REVERSED** (13 `200xx` là **drone**) · **`T1`/`T5` vẫn MISSING** với số đo **1.192/1.194** slot trỏ `\x7fELF` · số liệu đổi do tái export (HP boss **1,89× → 1,79×**) | 252 dòng · 12 bảng |
| **`VERIFY_ROUND2.md`** | **Đo lại 75 con số của chính mình** bằng `tools/verify-claims.py`: **73 đúng · 2 không kiểm được**. Bốn lỗi cùng một dạng — *đếm hai tập khác nhau rồi ghi vào một dòng*: **21** file `/statics` (không phải 18) · **185** animation Spine (180 = 26 rig, `Saw` 5) · **26** rig `skeleton*` (không phải 25) · **29 claim nữa ở §5b–§5d**. Trong đó **mục 1.4 hoá ra SAI**: **203** Animator tái lập được đúng khi biết roster = 109 tên trong `waves.json` — đã khôi phục 203, và đó là **lần thứ năm** mắc cùng lỗi. FAIL → mã thoát 1, có job CI riêng | 130 dòng · 6 bảng |
| **`PARALLEL_TASKS.md`** | **Lô 13 việc kiểm chứng chạy song song** cho nhánh dữ liệu: 13 giả định **sai được** (mỗi cái có *điều kiện lật ngược*) · 13 task độc lập (6 không cần APK) · **vì sao 4 workflow hiện tại không song song được** (`contents: write` + `git push` ở 4/4 job) · 1 workflow matrix 13 job + 1 job hợp nhất · **hợp đồng artifact** (`verdict` PASS/REVERSED/MISSING) · luật hợp nhất **một lần** | 288 dòng · 8 bảng |
| **`OPEN_ISSUES.md`** | **Sổ 28 vấn đề chưa chốt**, chia theo **nguyên nhân** (lỗi export · RVA data · chưa lấy · vắng mặt thật · cần chạy game) — mỗi vấn đề có **bằng chứng số + cách chốt rẻ nhất + nếu không chốt thì thiết kế quyết gì**. **8/28 đóng** (23/10: **C3 · C4 · C6** đóng nhờ `UNITY_RULES`; **C1 · C2** hạ **D → B**) · **B8 đã đóng nửa**: `kCount ≡ 1` (A); còn **HP theo chế độ** (C) | 421 dòng · 13 bảng |
| `screens.csv` | 125 dòng dữ liệu: `class, board_id, mo_tu_dau, popup_con, data_can_load` | 126 dòng · 0 bảng |
| `sprite-list.csv` | 163 dòng dữ liệu: atlas page (size + MB thật), background, Spine, UI 9-slice, ship/drone, bullet | 164 dòng · 0 bảng |

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

> ⚠ **Trạng thái 23/10 — các đường dẫn trên không nằm ở nhánh này, nhưng KHÔNG mất.**
> Chúng ở nhánh phân tích **`arena/ef6b75ef-windwings-space-shooter-game-p`** (`8492c220`,
> 241 commit, 53.698 file), vẫn còn trên remote. Nhánh này và nhánh đó cùng tách từ
> `8b3689dc` nên **không** chia sẻ commit nào ngoài gốc.
>
> Đọc được **không cần merge, không cần checkout**:
>
> ```bash
> git fetch origin 'refs/heads/arena/ef6b75ef-windwings-space-shooter-game-p:refs/remotes/origin/arena/ef6b75ef-windwings-space-shooter-game-p'
> git show origin/arena/ef6b75ef-windwings-space-shooter-game-p:datas/waves.json | jq
> git ls-tree -r --name-only origin/arena/ef6b75ef-windwings-space-shooter-game-p -- datas/
> ```
>
> Ba cái tên trong bảng trên cần sửa cho đúng khi fetch:
> `datas/formula_traces.json` và `datas/anim_clips.json` thực tế là **`.json.gz`**;
> `reverse-engineering/scriptableobjects/*.csv` là **`reverse-engineering/scriptableobjects/*.csv`**
> cộng `reverse-engineering/raw/typetrees/*.jsonl.gz` (111 class).
>
> Dữ liệu chạy thật (điện thoại) nằm ngay nhánh này:
> `docs/apk-analysis/ramus/2026-10-23-phone/*.json` — đối chiếu với dữ liệu tĩnh ở
> `CROSSCHECK-static-vs-runtime.md` cùng thư mục.

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
| Prefab có súng | **68** (Boss 26 · Wave/BLT 22 · CD 13 · CB 6 · BB 1) · **319 súng thật** + 139 preview UI | `prefab_joins.csv.gz` | **`DATA_SYNC.md` §7.19** |
| Tốc độ enemy / turret | **0,2–30,0**, median 5,0; 69,3% rơi vào 2 nấc 5,0 và 20,0 | `Enemy_Movement.csv` (981 bản ghi) | **`BOSSES.md` §5.3** |
| **Turret** | **112 component / 44 prefab · hai tầng**: **21 prefab spawn** (7.568 quân = 16,6%) + **23 prefab đặt sẵn trong `Wave_*`** (71 component) · tỷ lệ theo prefab thật **14,4%** (112/777) | `prefab_joins` + `transform-tree` | **`BOSSES.md` §5.1** · `DATA_SYNC.md` §7.20 |
| Prefab enemy **chưa từng xuất hiện** | **22** (`W2-30041…30057` · `W2-30053 Mau` · `CB-30005/17/19` · `CD-31017`) | `prefab_joins` | `DATA_SYNC.md` §7.20.5 |
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
