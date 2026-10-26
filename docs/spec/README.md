# SPEC — WindWings: Space Shooter

Bộ **spec hoá** game Android *WindWings: Space Shooter* (`com.Wind.wings.Space.Shooter`
v1.3.118, Unity 2022.3.62f3, IL2CPP arm64) từ kết quả dịch ngược APK.

**Mục đích:** đủ số để **dựng lại một game cùng thể loại nhưng khác hoàn toàn về art** —
không phải để clone y nguyên. Toàn bộ asset gốc (sprite, atlas, Spine, audio) thuộc bản quyền
**GCenter / GCENTER VIET NAM TECHNOLOGY JSC** và **không được tái sử dụng**.

> **Dữ liệu gốc ĐÃ được phân tích — dùng để học, không để chép.** Kho đo nằm ngay trong repo:
> **2.112** sprite × 12 số đo (`docs/assets/art-study.csv`) · **42** contact sheet · **35** ảnh chụp
> thật có số đo khung hình (`design-metrics.json`) · **54.019** layout · **139** file asm
> (**142.136** dòng) · **126** bảng ScriptableObject · **1.857/2.197** sprite đã phân loại.
> **Cách dùng đúng:** đọc **số** (tỉ lệ, tương phản, ngân sách màu, mật độ chi tiết, nhịp) rồi
> **vẽ mới**; **không** phát hành file gốc. "Không tái lập 1:1" **không** phải lý do hạ chuẩn —
> chất lượng thị giác có test bằng máy ở `VISUAL_DESIGN.md` §5. Danh mục đầy đủ: **`START_HERE.md` §1**.

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

> **Kiểm tự động (`RD1`):** **50/50** dòng trong bảng trên khớp **số dòng · số bảng** đo lại từ file.

> **Lượt 25/10 (tối):** nhánh dữ liệu lên `7c7c9f064` và review 5 điểm N1–N5 — đã sửa hết, xem
> `docs/HANDOFF_REPLY_7c7c9f064.md` + `DATA_SYNC.md` §18. Claim mới: **CM1 · CM2 · CM3**.

## 1. Đọc gì trước

| Nếu bạn là… | Đọc theo thứ tự này |
|---|---|
| **AI/agent sắp dựng game mới** | **`START_HERE.md`** (kho dữ liệu + 8 số xương sống + 12 bẫy) → `MISSING_FOR_NEW_GAME.md` → `GAMEPLAY.md` §0+§7 → `TUNING_KNOBS.md` |
| **Designer / cân bằng số** | `GAMEPLAY.md` §0 → `BALANCE.md` §0 → `COMBAT.md` §0 → `ECONOMY.md` §0 → **`TUNING_KNOBS.md`** (núm vặn + công thức) |
| **Engineer dựng lại gameplay** | `GAMEPLAY.md` (core loop) → `COMBAT.md` (súng/đạn) → `ENCOUNTERS.md` (wave) → `UI.md` (màn hình) |
| **Art / tech art** > **Kiểm tự động (`RD1`):** **51 dòng · 0 lệch** — mỗi dòng `N dòng · M bảng` được đo lại từ file;
> sửa tài liệu mà quên cập nhật bảng là đỏ (`python3 tools/refresh-readme-sizes.py --check`).

| **`ART_STUDY.md`** (số đo mẫu gốc: màu/gradient/outline) → **`VISUAL_DESIGN.md`** (khung, tương phản, accent, juice + test máy) → `ASSETS.md` §0–§5 (art direction "Ink & Ember", atlas plan) → `sprite-list.csv` |
| **Producer / ước lượng** | **`COVERAGE_AUDIT.md`** (còn thiếu gì, cái gì chặn) → `GAMEPLAY.md` §7 (thứ tự build) → **`DONE.md`** (hoá đơn sản xuất + 4 mức kiểm) → `ASSETS.md` §7 (atlas plan) → `AI_FEASIBILITY.md` (rủi ro) |
| **Đánh giá rủi ro trước khi build** | `AI_FEASIBILITY.md` §2 (lỗ hổng) → `COVERAGE_AUDIT.md` (cái gì chặn) → `DESIGN_READINESS.md` (D3 còn 🟡) |

Ba file `BALANCE`, `COMBAT`, `ENCOUNTERS` là **số**; `GAMEPLAY`, `UI`, `ASSETS` là **cấu trúc**;
`ECONOMY` là **cái gì có thật và cái gì không**.

---

## 2. Danh mục file

| File | Nội dung | Kích thước |
|---|---|---:|
| **`START_HERE.md`** | **Cửa vào cho AI dựng game mới.** Mở đầu bằng **mục đích**: bắt chước bản gốc — mọi thứ trừ art đã có đáp án; việc thiết kế duy nhất là vẽ lại art. Trả lời đúng 2 câu: *có đủ không* (**L1 đủ**) và *có dữ liệu gốc để học không* (**có**: 2.112 sprite có số đo · 42 contact sheet · 35 ảnh chụp · 54.019 layout · 139 file asm · 126 bảng SO). Gồm: kho dữ liệu + ranh giới **học vs phát hành** (không hạ chuẩn) · **8 số xương sống** để dựng đúng · **bảng số để làm đẹp** (màu/gradient/accent/tương phản/juice) + test máy · thứ tự đọc theo vai · **12 bẫy đơn vị** đã từng sai · **L0–L3** định nghĩa lại cho khỏi lẫn · lệnh tự kiểm. | 263 dòng · 8 bảng |
| **`ART_STUDY.md`** | **Học mẫu gốc bằng số** — **2.112** sprite / 42 contact sheet: ngân sách màu (**30–60** phụ · **110–160** chủ thể), gradient **0,20–0,26** cho mọi nhóm, thứ bậc sáng/bão hoà, **outline đen chỉ ~1 %** (sửa niềm tin "viền dày"), `fill` **0,08–0,87** ⇒ pack theo hình bao; 9 luật kiểm bằng `tools/art-study.py` | 140 dòng · 3 bảng |
| **`VISUAL_DESIGN.md`** | **"Đẹp" đo được** — khung hình **0,4813** · **3 chế độ sáng** (gameplay accent ≤10 %, khung thưởng ~47 %, màn tối) · tương phản **0,45–0,80** · chi tiết **13–22** · hình học **54.019** layout (panel dọc **2:3**) · juice **0,05 s / 0,10·20 frame** · **giữ/đổi** + test bằng máy (`tools/design-metrics.py`) | 130 dòng · 5 bảng |
| **`DATA_INTEGRITY.md`** | **Dữ liệu gốc có bị sửa?** Hai commit của phiên này **không chạm** 5 đường dẫn dữ liệu gốc (`git diff` rỗng). Bảng `sha256` trong `datas/PROVENANCE.md` **đã cũ**: **244/383** khớp · **139** lệch vì kéo lại. So đầu nhánh dữ liệu (`7e0da2ee3`): **2.211/2.465** file giống hệt, **254** khác — **244 khớp nguyên blob một snapshot đã pin**, **10** khớp đúng **HEAD** (kéo ở commit ngoài danh sách), **0 đang sửa** ⇒ **0 sửa tay**. **157** file `.gz` đổi byte nhưng **88 giống nội dung** sau giải nén, chỉ **69 khác thật**. Kiểm bằng `tools/data-integrity.py` (3,2 s). | 136 dòng · 7 bảng |
| **`MISSING_FOR_NEW_GAME.md`** | **Còn thiếu gì để làm game mới** — 16 hệ (**8 đủ · 8 một phần · 0 thiếu hoàn toàn**), **0 chặn số** (row cũ "2 chỗ chặn kèm rodata" đã ĐÓNG — 576/6 blob decode xong), danh sách **không phải thiếu**, và trả lời **L1 đủ / L2 sót 6 mục có tên / L3 một phần — ĐÍCH, ưu tiên L3 trước (report 96)** | 343 dòng · 9 bảng |
| `GAMEPLAY.md` | One-pager, 3 vòng lặp (30 s / 10 phút / 1 tuần), core loop, **7 `PlayMode` + 3 `PVPMode`**, 9 nhánh progression, SOURCE/SINK, meta, boss, thứ tự build | 689 dòng · 31 bảng |
| `UI.md` | `BoardManager`/`UIManager`, screen graph, **125 class UI** (53 board · 63 popup · 8 tab), điều kiện mở từng popup · **§9 manifest `_index.csv`: 797 instance · 117 lớp · 150.131 node · 5.831 nút** (giải thích luôn vì sao 117 ≠ 125) · **§9.2 bộ đầu vào vẽ** (11 board, 10.710 node, 100 % `local_pos`) · **§9.3 layout tutorial** (8 ref → 7 GO, 19 dòng text, callback Endgame `0x126d3cc`) | 602 dòng · 23 bảng |
| `ASSETS.md` | Art direction **"Ink & Ember"**, inventory sprite/atlas/Spine/audio, **atlas plan 12 page đã kiểm bằng px² thật (§4.5)**, **legal checklist** | 576 dòng · 27 bảng |
| `BALANCE.md` | HP **39 prefab boss** + **150 cặp HP enemy theo id**, roster tàu/drone/item, công thức damage (armor), khung balance đề xuất; §6.10 phân biệt 12 InitializeArray captures = 10 list rows + 2 percent fields (Report 119) | 1687 dòng · 69 bảng |
| `docs/apk-analysis/119-L2-Ramus-device-crosscheck-arena-a5a74747-windwings-space-shooter-game-p.md` | #19: device 12↔10 được phân loại thành 10 `listStatValues` + 2 percent fields; Map outer count 250 khớp nhưng nested readback còn placeholders, không có same-build parity | 72 dòng · 2 bảng |
| `docs/apk-analysis/120-L3-controller-schema-replication-17-arena-a5a74747-windwings-space-shooter-game-p.md` | #17 REPLICATION: đối chiếu native giới hạn ba literal field trên hai path; không khám phá TypeTree độc lập, schema vẫn mở | 57 dòng · 2 bảng |
| `docs/apk-analysis/121-L2-runtime-map-depth2-28-arena-a5a74747-windwings-space-shooter-game-p.md` | #28 vehicle run bị chặn trước session vì thiếu bridge trong APK; không có Map values/runtime readback | 67 dòng · 2 bảng |
| `docs/apk-analysis/122-L2-combat-semantics-24-arena-a5a74747-windwings-space-shooter-game-p.md` | #24 REPLICATION: #20 Board_Players arrays are a display-power path; one bounded Player_Attack_1 path reads the separate `StartMainCannonDamages@0x78`; rank selects guarded loop count, not per-hit input | 67 dòng · 1 bảng |
| `docs/apk-analysis/123-L3-sliced-tiled-geometry-5-arena-a5a74747-windwings-space-shooter-game-p.md` | #5 REPLICATION model: border metadata → 112 direct sliced grids plus 10 borderless tile models; no native generator/readback claim | 67 dòng · 1 bảng |
| `docs/apk-analysis/124-L2-map-depth2-28-static-fallback1-arena-a5a74747-windwings-space-shooter-game-p.md` | #28 fallback ①: 250 static map rows crosschecked against #21; `STATIC_CROSSCHECK_NOT_RUNTIME`, no nested runtime parity claim | 67 dòng · 2 bảng |
| `docs/apk-analysis/125-L2-save-durability-audit-25-arena-a5a74747-windwings-space-shooter-game-p.md` | #25 bounded save/flush census: zero direct `PlayerPrefs.Save()` edges in the pinned method/ASM scope; no durability or migration closure | 63 dòng · 2 bảng |
| `docs/apk-analysis/126-L2-static-root-pixel-projection-26-arena-a5a74747-windwings-space-shooter-game-p.md` | #26 `Board_Pause` root/PPtr audit: scoped scene captures have no exact instance match; `pixel_bounds=null`, no runtime/render approval | 89 dòng · 3 bảng |
| `docs/apk-analysis/127-L2-spriteatlas-remap-skinning-bounds-6-arena-a5a74747-windwings-space-shooter-game-p.md` | #6 bounded SpriteAtlas map: 1,550 exact serialized joins; 2,185 Sprite bones/bindposes empty; static AABBs only, runtime remap/deformation `NOT_OBSERVED` | 80 dòng · 2 bảng |
| `COMBAT.md` | **458** `Gun_Attack`, histogram damage, burst pattern, **DPS lý thuyết (địch)**, súng boss, **TTK = newdesign hoặc measured** (tích damage×rate không dùng — damage·s, review peer), hitbox va chạm, đạn | 505 dòng · 20 bảng |
| `ENCOUNTERS.md` | **282 wave** / **23.757 spawner** (11.089 dòng cấu hình) / **45.659 quân**, `spawn_type`, tham số spawn, **250 map** + parallax, 299 stage | 717 dòng · 32 bảng |
| `ECONOMY.md` | `Box_Rewards`, `Shop_Cell`, `DataShopPack`, IAP **170 SKU**, `Sub_Item`, `PurchaseType` — **cái gì là số thật** | 394 dòng · 18 bảng |
| `ENEMY_BEHAVIOUR.md` | Tốc độ enemy **0,2–30** (bản cũ 800 dòng; bản đủ 981: **1,0–20,0** — xem `BOSSES.md` §5.3), **95 turret** (bản cũ), bán kính va chạm **15 unit**, biên vùng chơi **20×25**, **399** đường bay, thiên thạch, nhịp nổ boss, kiến trúc **9 component/enemy** | 248 dòng · 12 bảng |
| `AI_FEASIBILITY.md` | AI dựng lại được đến đâu — đối chiếu nghiên cứu 2025–2026 (`Spec2Game`, GameCraft-Bench, Play2Code) với lỗ hổng của bộ spec; chuỗi công cụ; xếp hạng độ khó | 653 dòng · 32 bảng |
| `TUNING_KNOBS.md` | **Toàn bộ núm vặn**: `Player_Get_Datas` 178 field, công thức giá, feel (shake/slow-mo/hit color), art scale 10,8×19,2; **giá trị nằm ở đâu** (const / prefab / `.cctor`) | 312 dòng · 17 bảng |
| `DONE.md` | **Định nghĩa "hoàn hảo" thành 4 mức kiểm được** (L0 chạy được · L1 đúng luật · L2 đúng số · L3 không phân biệt được) + **hoá đơn sản xuất** 282 wave / **11.089** dòng (**23.757** lượt) / **22.451** slot enemy (0 `"?"`) / 1.015 tên | 890 dòng · 21 bảng |
| **`BOSSES.md`** | **39 boss** đầy đủ (HP, bộ phận, wave, va chạm) · **45/45 wave boss có boss, 0/237 wave thường** · enemy thường **70 prefab / 8 họ** · turret **21** · **87 class hành vi chưa đọc** · **§8 kiểm 7 lớp kịch bản**: sinh quân 100%, damage enemy thường **0%** (`Enemy_Physics` 981) | 586 dòng · 22 bảng |
| **`PIPELINE_AUDIT.md`** | **Đánh giá nhánh phân tích ngược:** 42 commit thật/4h39 · 5/6 tuyến cho dữ liệu thật · **lạc ở IL2CPP constants** (60/98 dòng là rác `288733`) · **`Enemy_Physics` 981 không có trong `TARGETS`** · 3 dòng code mở 100% lớp hành vi | 424 dòng · 26 bảng |
| **`ANIMATION.md`** | **4 hệ animation:** Spine **27 rig / 180 animation / 616 bone** (đọc 100%; asset markers không tự bind callback/runtime) · Unity Animator **791 clip / 308 controller / 5.792 instance** (**0 %** curve giải được — **9,19 MB** chưa giải · **100 % tên**; **62,5 % là UI**, enemy chỉ **203**) · `Rotate` **1.044** instance · flipbook **0 clip** (`m_PPtrCurves` **0/791**; 28 chuỗi/160 ảnh chỉ là tên sprite) ⇒ game **không dùng khung hình**. **§4.5 đếm riêng enemy**: `Enemy_Movement` **109/109** · `Enemy_Appear` **107/109** · Animator **87/109** · Spine chỉ **2 boss** | 436 dòng · 20 bảng |
| **`SCRIPTS.md`** | **3 tầng: số — kịch bản — mã.** Bằng chứng "số liệu chết" (`CurrentHealthPoint` = 0 ở **981/981**); **§0.5 luồng mở game lần đầu** (5 scene · 39 board · tutorial **5 bước** chạy trong trận); 5 lớp kịch bản; **giải mã timeline bắn** (6 tham số, **102 pattern**/516 slot); timeline spawn (**1 con/1,0 s · y 9,6 · radius 0,1**); pha boss **63 instance** (112 field damage đã đọc) | 346 dòng · 15 bảng |
| **`DESIGN_QUESTIONS.md`** | **48 câu hỏi designer phải trả lời** để làm game mới: ✅ **29 có số** · ⚠ **15 một phần** · ❌ **4 chưa trả lời** (cập nhật 25/10: câu D3 hạ ✅→⚠ theo review R1) — cả 4 câu ❌ đều là **blocker**, xếp theo chi phí trả lời.
| **`ANIMATION_SCRIPT.md`** | **Script animation enemy + boss** (code gọi animation nào, lúc nào — không phải feel). **Hai hệ độc lập**: Spine (Boss-39001 dùng `Boss_1_Animation`, Boss-39002 dùng `Boss1_Director`; shared asset không đồng nhất component route, callback key unresolved) và AnimationClip + event (**33 prefab boss · 793 event · 2 ngoài boss**; 129 tên hàm). **268 cặp (prefab, clip)** — **61 cặp** có ≥3 event nên đọc được nhịp: **0,17 · 0,33 · 1,0 · 5,0 s**, chuỗi 8–14 đòn/boss, `idle` cũng bắn đòn. **12 handler `Boss1_AnimationEvents` = 28 byte, chỉ gọi delegate** (hành vi nằm ở **delegate field**, không phải `UnityEvent` — ai gán: mức **C**, đã giao T2). **Enemy không có timeline** ⇒ máy trạng thái (`Enemy_Movement.Update` 3 nhánh, hướng bằng `atan2`×57,29578) + hit flash **0,05 s** qua `Invoke`. **§3.6 mới**: ai đặt trigger Animator = `Boss_AttackPhases` (**7 call site `SetTrigger` / 5 method**; **288** trigger + **15** bool trên **49/52** controller boss). **§4.2 mới**: **87/109 là roster** — riêng enemy **51/70** có Animator, **27** chỉ `Afterburner` (1 state), **19** không có ⇒ **46/70** enemy không có máy trạng thái. **38 lần `WaitForSeconds` · 12 hằng số · 26 lấy từ biến**. | 526 dòng · 25 bảng |
| **`BOSS_ANIM_TIMELINE.md`** | **Script animation boss đo bằng giây** — 795 `AnimationEvent` (34 prefab · 97 clip · **269 cặp (prefab, clip)** · 130 tên hàm), timeline từng clip: `0.37s AttackHand1Left · 0.65s …`. **67 % event là state** (`OnStartAttack` 146 · `OnAnimationEndedEvent` 137 · `OnStateExit` 56), chỉ 27 % là đòn. Nhịp multi-hit **0,17 s** (93 khoảng) · cửa sổ damage chỉ 2 cặp `Start→Stop` (4,17/2,67 s) · mốc cuối clip trung vị **3,52 s**, dài nhất **73,17 s** (`Lite_Appear`). **Enemy: 1/109** prefab có event (`CB-30040`, 2 event trùng mốc 1,5 s). Công cụ: `tools/boss-anim-timeline.py` · CSV phẳng `datas/boss_anim_events.csv`. | 186 dòng · 8 bảng |
| **`docs/HANDOFF_SPEC_REVIEW_71b1e9861.md`** | **Trả lời review `25c367aca`** — 6 điểm R1–R6: offset fallback `0xb78` · dedup chỉ là mẫu 14 wave · 67 page `sactx` ≠ 56 page có `category=atlas` · 643 nhãn passthrough **không mức** · D3 để 🟡 · `--no-skip`/`--require` để lỗi đo thành đỏ. Kèm **bảng 4 đơn vị spawner** (23.757 / 11.089 / 45.659 / 22.451) và danh sách **6 thứ vẫn chưa chứng minh**. 53 dòng · 2 bảng |
| **`ASSET_TRIAGE.md`** | **Bộ ảnh gốc còn thiếu gì?** 2.197 asset: **1.857 đã có nhãn** (1.692 vòng tên + **165** vòng số đo), **340 `unresolved`**. **§9** lần đầu có **bảng tách sheet**: **307** sheet · **4.250 mảnh** (`98` texture page · `64` page `sactx`), cắt thật bằng `tools/classify-by-measure.py --crop`; nhưng **56 %** mảnh lớn còn góc caro ⇒ cắt đúng cần `m_RD.rect`. **§9.6** gợi ý kNN có **đo sai số leave-one-out**: **781** ca · **86,3 %** đúng · phủ thêm **89**/340. **§4.3** bản gốc **tháo rời tàu/enemy thành bộ phận** (117 `parts`). Việc cần raw: **T9** export `Sprite.m_RD.rect`. | 519 dòng · 23 bảng |
| **`SYSTEM_MANIFEST.md`** | **Bảng tối giản cho AI game mới** — `hệ thống → raw/hợp đồng → luật đã chứng minh → AI tự chọn → test` (15 hệ thống, task ⑤ PR12): ghi rõ pack tham khảo **có sẵn nhưng chưa runtime/import/visual approval**; L1 khởi công không chờ playback. | 36 dòng · 1 bảng |
| **`COVERAGE_AUDIT.md`** | **Kiểm lại toàn bộ: thiếu chỗ nào?** Chia game thành **14 vùng năng lực** và đếm cái đang có: **10 vùng đủ** (A/B) · **4 thiếu một phần** (điều kiện Animator · FX curve · trigger âm thanh · UI *vẽ lại*) · **1 ngoài phạm vi** (feel — đã chốt bỏ, **script là đủ**). **6 chỗ thiếu — 0 chặn số** (2 chặn cũ ĐÃ ĐÓNG 25/10: map→wave bind xong · `kHp` không tồn tại; sót 2 tái đối chiếu runtime). **§3 tưởng-thiếu-nhưng-đã-có**: sprite 2.885 có kích thước · bản địa hoá **1.416 key × 19 ngôn ngữ** · IAP **170** · FX **4.845** · UI **55.584** file layout. **§4 bốn cặp số dễ tráo** (UI 797 vs 55.584 · audio 69 vs 92 · sprite 2.885 vs 2.907 · art 62,95 MB page-vs-toàn-bộ). | 139 dòng · 5 bảng |
| **`HANDOFF_ANIM_RAW.md`** | **Handoff raw có task ledger T1–T4 và follow-up T4b–T9**; §0 liệt kê kết quả đã xong và ranh giới không được lặp. Tách riêng Boss-39001 `Boss_1_Animation` khỏi Boss-39002 `Boss1_Director`; reports 142–159 ghi rõ bounded handler census, static slot literal `0x2ADFB48` = `Stop` via separate AI-1 handoff (while delivery/marker/effect remain unresolved), G4 `gun3Static` false→true `SetActive` sequence, G5 static `Stop` name match in `focusGameSpeed` (no runtime transition), G6's array-blob boundary, N2's serialized `Body 1` controller owner (PPtr `0:1856` → Animator `493584` under `Boss-37004`; no native graph-builder link claimed), and N1's read-only report-122 review (virtual-service sinks and prior graph counts superseded; allocator/prepared-state boundaries confirmed; exact raw pins unverifiable). T2 delegate, T3 `UnityEvent`, T4 Animator, cùng follow-ups còn trạng thái riêng; không suy runtime. | 389 dòng · 5 bảng |
| **`docs/HANDOFF_SPEC_FIX_25c367aca.md`** | **Sửa 6 điểm review `25c367aca`** (PR #12 comment `6396779924`) trên nhánh này, kèm bằng chứng từng điểm: R1 fallback `0xb78` + mẫu số 262/238 · R2 **cấm dedup theo tên** (14 file wave: **0** pathID trùng) · R3 67 vs 56 page `sactx` · R4 luật bị che + 643 passthrough **không** mức A · R5 **D3 KHÔNG đóng** · R6 lỗi đo = **ERROR** (exit 1). **§2 ghi lỗi của chính bản sửa (sửa 3 lần): spawner = 23.757 `Call_Data` object; 11.089 = dòng cấu hình** — bảng cũ đúng số, sai nhãn cột. **§3 liệt kê 5 thứ còn 🟡** để không đọc thành "đã xong". | 67 dòng · 2 bảng |
| **`DESIGN_READINESS.md`** | **Đã đủ thiết kế chưa?** → **ĐỦ cho L1** (giống cơ chế, không cần giống số). **GIAO ĐƯỢC L1 (cập nhật lần 18, 25/10)**: bind xong (save/load = id−10001 · combat = **impl N→index N−1**, tàu 10001→2 · 10003→0, report 81/82 peer · Map **11 cấu trúc/614 mảng** · HP enemy **150 cặp**) · feel **ĐÓNG — BỎ** (quyết định) · DPS = damage×rate **không dùng** (damage·s — review peer; receivers đã dịch 85–86) · tally **✅ 4/9 blocker · 🟡 4 · 🔴 1 (`A5`)** · claim **211/209 PASS**. Sót: `A5` luật continue + `B3` rẽ nhánh `stepLevel` (mức C). | 269 dòng · 12 bảng |
| `DATA_SYNC.md` | **Đối chiếu với nhánh dữ liệu qua 12 bản** (`821efc5` → `cd0372d`): cái gì tôi đã sai (audio 0→69 · enemy `?`→109 prefab · HP 800→981 · 981 **không phải** 981 enemy · 42→**68** prefab súng) · **§9 sổ theo dõi 11 mắt ghép 100%** · **§10 kéo `scriptableobjects/` (1.339 file, 7,8 MB)**: `Call_Data.csv` = **1.200 dòng · 23 field**, **không có `delay`** ⇒ `rate` là field thời gian duy nhất; `number = 0` ở 1.200/1.200 ⇒ số quân = độ dài list. Kèm lý do **không** kéo cây `raw/ui` (53.318 file, 142,7 MB) — nhưng **có** kéo **2 manifest** của nó (`_index.csv`, `_skipped.csv`) và **140 file md/csv** của `docs/apk-analysis/`, trong đó `spine-events.csv` (**21 dòng**) xác nhận rig boss 1 chỉ có **2 tên event**. **§11 kéo bản thứ hai (74 file, 5,1 MB)**: 16 `*_Director.csv` + 14 `*_AnimationEvents.csv` + `interesting-classes.cs` ⇒ đọc thẳng 8 tên entry, **12 field delegate**, **5 field `BossSpineEventHandler`**; **không** kéo 53.316 file `raw/ui` và `ui_text_keys.csv.gz` (7,1 MB > trần). **§13 đồng bộ ba snapshot** `9aed767b1` → `1989defc2` → `0a42eaa42`: ls-remote + rev-parse khớp, **12 commit** sau `019e704d1` (2 sau `9aed767b1`), 5/5 file đọc thật kiểm bằng blob SHA-1, verifier `--ref 1989defc2 --strict-ref` = **139 PASS** với 186 input từ ref, 0 input dữ liệu local. **§24.42 #12** sửa đúng type Transform 270123 và ghi rõ Popup_QuitMissions template-local transition; viewport projection vẫn mở đến khi có instance/camera authority. **§24.43 #19** tách 12 static captures Device thành 10 list rows + 2 percent fields; nội dung Map vẫn cần runtime receipt mới với `arr=256&depth=2`. **§24.54 report 163** chốt 24/24 static class-to-array joins, còn component ownership/extra-life serialization `NOT_BOUND`. **§24.55 report 164** bounds 126 CSV + 140 TypeTree rows; PPtr owner/extra-life vẫn `NOT_BOUND`, GP_Datas có một CSV–TypeTree field mismatch. **§24.56 report 165** tách Health-tech 2500 khỏi ship upgrade; 24h starter premium/extra-life stock và component owner vẫn `NOT_BOUND`. | 3490 dòng · 130 bảng |
| **`ASM_INTEGRITY.md`** | **Gác cổng chống cắt cụt im lặng**: sự cố 4.608 B/method · **3 cờ tự kiểm** (`size_capped` · phủ địa chỉ · opcode cuối) · **script · 2 bảng chạy được, nhúng nguyên văn** · **baseline 17 class** (16/17 PASS, `RankManager` thiếu 8 B) · **quy tắc "được phép phủ định"** | 293 dòng · 3 bảng |
| **`ENEMY_HP_RUNTIME.md`** | **Enemy thường KHÔNG chết 1 phát** — **109/109** prefab được spawn có HP bar (**909** instance `Enemy_Hp_Bar`, **909/909 `m_Enabled=1`**; thêm đường `Enemy_Display.hpProgressBarRenderer` **976/981**). ❌ rút lại câu "HP bar chỉ trên boss". **HP thực tế = bảng × `kHp[mode]`** (→ `DIFFICULTY_MODES` §5). Nguồn HP: `Enemy_Get_Datas` → **`Dictionary<int,float>` trong `.cctor 0x157F7CC`** (**chưa** có trong `TARGET_CLASSES`). **Enemy cũng có giáp** (`armor @0x34`). Và **"treo máy" không phải vì HP**: **12 quân/s**, **~50–950 con**, **~40–100 phép tính HP/s** vs 10⁹ ops/s | 244 dòng · 9 bảng |
| **`DIFFICULTY_MODES.md`** | **3 chế độ: không nhân số quân — chỉ đổi ngưỡng %, thưởng, năng lượng (+ HP).** `kCount ≡ 1` (**A**, ba nguồn: người chơi kiểm lại · `GetCountEnemies` **304 lệnh · 0 `mul`** · `GetListWaves` **278 lệnh · 0 phép nhân**). Kênh **có** thay đổi: `pct[mode]` · `levelDelta[mode]` (**`float[]` index bằng `ModeCurrent`**, `cmp w9,w20` + `b.ls throw`) · `GetCostEnergyForPlay(stageIndex, stageLevel)`. **Vì sao "thấy đông hơn"**: Little's law — HP cao ⇒ sống lâu ⇒ **cùng lúc nhiều hơn** (47–157 → ~70–235) với **cùng** 45.659 quân. **"Số quân không theo quy luật"**: CV **1,01** · median **131** · max **951** · **150/282** giá trị khác nhau · HP bar **109/109** | 479 dòng · 18 bảng |
| **`MISSIONS_STARS.md`** | **Ngưỡng sao = `(int)( pct[mode][slot] × countEnemies )`** — asm `ldr w21,[x9,#0x34]` (`ModeCurrent`) → `GetKillPercentMissionComplete` → `scvtf`/`fmul`/`fcvtzs`; mẫu số **giống nhau** ở 3 chế độ ⇒ **UI in đúng số** (bạn xác nhận). `IsMissionCompleted` = **`completed > missionIndex`** ⇒ **cộng dồn ⇒ 1/2/3 sao**; sao lưu theo **(stage, mode)**. Loại nhiệm vụ xoay theo **`stageIndex % 6`**. `GetCountEnemies` **304 lệnh · 0 `mul`** ⇒ **cộng bảng, không đếm spawn**. **`pct` = 9 số** — `GetKillPercentMissionComplete` ∈ `Player_Get_Datas` (188 B, 3 mảng `static float[3]` + `memcpy`); giá trị còn thiếu vì `InitializeArray` (`debug_rva` resolve **2/1.929 = 0,1 %**). Kèm phân bố số quân (**CV 1,01**) và cách đo `pct` bằng **3 con số trên UI** | 380 dòng · 11 bảng |
| **`EXTERNAL_REFS.md`** | **Không có ai phân tích ngược game này.** 6 loại nguồn: 2 repo GitHub quét manifest (`beerphilipp/taptrap` · `tabbed-out` → `target_sdk **34**`, **77 activity**, **3 package name** cùng họ) · ~30 trang mod APK (**danh sách mod = bản đồ "cái gì ở client"**: One Hit Kill ⇒ HP enemy client-side · High Gold Attraction ⇒ rơi vàng quyết định lúc vào màn) · r/Windwingsgame (403) · YouTube · **wiki Galaxy Attack = GAME KHÁC, cấm trích số** · metadata store. Kèm **phép tìm đã chạy** (`windwings il2cpp` → **0**) và hệ quả: *repo này là nguồn duy nhất có số* | 169 dòng · 10 bảng |
| **`UNITY_RULES.md`** | **Luật engine tự chốt 6 mục**: field chỉ serialize khi `public`/`[SerializeField]` ⇒ `armor` **0/981** (enemy **không** giáp per-prefab) · PPtr null ⇒ `dataScript` **23.570/23.570** rỗng (**C3 đóng**) · `autoCacheColliders = false` **981/981** (**C6 đóng**) · `indexWave` **686/686 = 0** (**C4 đóng**) · `m_PPtrCurves` **0/791** ⇒ **không flipbook** · `m_MuscleClipSize` **9,19 MB** trên **782 clip** ⇒ curve **có thật**, thiếu decoder · `m_Events` **793** + `m_AnimationClips` **793** + `m_TOS` **3.871** ⇒ **C1/C2 hạ D → B** · `static` không serialize ⇒ **`kHp`/`pct` không nằm trong asset** | 387 dòng · 18 bảng |
| **`WHERE_TO_LOOK.md`** | **Chẩn đoán 3 blocker theo nguyên nhân, không theo độ khó**: `.cctor` `Map_Get_Datas` **1,1 % RVA** (dữ liệu **viết thẳng** ⇒ chỉ cần parser) vs `Device_Get_Data` **47,6 % RVA** (⇒ cần relocation) vs `Enemy_Health` **chỉ có `noDamage`** (⇒ phải **quyết**). Gồm **phép kiểm thứ tự đã THẤT BẠI** (117 cặp **không** phải map→wave) và **quy tắc phép kiểm rỗng** | 226 dòng · 9 bảng |
| **`VERIFY_ROUND1.md`** | **Kiểm chéo 6 phán quyết của nhánh dữ liệu** (`68ce86a7`): 4/6 đúng nguyên · **`T2` sai cơ chế** (`ends_clean` **True rỗng** che 25 method vắng mặt) · **`T4` phép kiểm yếu** (`#0x2711` là **trừ** không phải cộng) · **`T6` REVERSED** (13 `200xx` là **drone**) · **`T1`/`T5` vẫn MISSING** với số đo **1.192/1.194** slot trỏ `\x7fELF` · số liệu đổi do tái export (HP boss **1,89× → 1,79×**) | 252 dòng · 12 bảng |
| **`VERIFY_ROUND2.md`** | **Đo lại 75 con số của chính mình** bằng `tools/verify-claims.py`: **73 đúng · 2 không kiểm được**. Bốn lỗi cùng một dạng — *đếm hai tập khác nhau rồi ghi vào một dòng*: **21** file `/statics` (không phải 18) · **185** animation Spine (180 = 26 rig, `Saw` 5) · **26** rig `skeleton*` (không phải 25) · **29 claim nữa ở §5b–§5d**. Trong đó **mục 1.4 hoá ra SAI**: **203** Animator tái lập được đúng khi biết roster = 109 tên trong `waves.json` — đã khôi phục 203, và đó là **lần thứ năm** mắc cùng lỗi. FAIL → mã thoát 1, có job CI riêng | 220 dòng · 8 bảng |
| **`PARALLEL_TASKS.md`** | **Lô 13 việc kiểm chứng chạy song song** cho nhánh dữ liệu: 13 giả định **sai được** (mỗi cái có *điều kiện lật ngược*) · 13 task độc lập (6 không cần APK) · **vì sao 4 workflow hiện tại không song song được** (`contents: write` + `git push` ở 4/4 job) · 1 workflow matrix 13 job + 1 job hợp nhất · **hợp đồng artifact** (`verdict` PASS/REVERSED/MISSING) · luật hợp nhất **một lần** | 292 dòng · 8 bảng |
| **`OPEN_ISSUES.md`** | Sổ việc chưa chốt theo nguyên nhân. **Count cần reconcile:** phần mở đầu ghi 28 vấn đề / 11 đóng; các ID liệt kê 29 dòng và close-marker có status pha trộn (audit `ANALYSIS_SPEC_RESIDUAL_AUDIT.md`). A2 đóng bounded scope H1; stage/scene identity, B6/C8 semantics, D5 owner/extra-life vẫn riêng | 419 dòng · 13 bảng |
| **`ANALYSIS_SPEC_RESIDUAL_AUDIT.md`** | Tổng kiểm analysis + SPEC theo snapshot 2026-10-27; tách bounded evidence, open issues, lệch trạng thái và sync queue | 101 dòng · 2 bảng |
| `screens.csv` | 125 dòng dữ liệu: `class, board_id, mo_tu_dau, popup_con, data_can_load` | 126 dòng · 0 bảng |
| `sprite-list.csv` | 163 dòng dữ liệu: atlas page (size + MB thật), background, Spine, UI 9-slice, ship/drone, bullet | 164 dòng · 0 bảng |

---

## 3. Bản đồ nguồn — số nào lấy từ file nào

Nguồn sự thật là **file dữ liệu bóc trực tiếp từ APK**, không phải tài liệu tóm tắt:

| Nhóm dữ liệu | Đường dẫn | Nuôi file spec nào |
|---|---|---|
| ScriptableObject (91 loại) | `reverse-engineering/scriptableobjects/*.csv` | `COMBAT`, `ECONOMY`, `BALANCE` |
| Bảng dữ liệu bóc sẵn | `docs/apk-analysis/*.csv` (**+64 file kéo 24/10**: 16 `*_Director`, 14 `*_AnimationEvents`, 7 `*_AttackPhases/_AttackTypes` …) | `BALANCE`, `UI`, `ASSETS`, `ECONOMY` |
| Bản đồ wave (**11.089** dòng / 23.757 lượt) | `datas/waves.json` | `ENCOUNTERS` |
| Roster / IAP / item | `datas/{ships,drones,items,iap_products}.json` | `BALANCE`, `GAMEPLAY`, `ECONOMY` |
| Mã IL2CPP (enum + class) | `reverse-engineering/il2cpp/dump.cs.gz` | tất cả (enum, field name) |
| Text/graphics | `reverse-engineering/textassets/` | `ASSETS` |

> ✅ **Cập nhật 26/10: phần lớn đường dẫn trên ĐÃ nằm ngay trong repo này** — không cần fetch để đọc:
> `datas/` (**116** file trực tiếp, **26.653.213 bytes / 26,7 MB**) · `reverse-engineering/` (**2.351** file, **43.921.529 bytes / 43,9 MB**: 139 file asm
> **142.136** dòng · 142 typetree · 126 bảng ScriptableObject · 64 textasset) · `docs/apk-analysis/`
> (**120** báo cáo `.md` + **107** bảng `.csv` + **83** ảnh chụp thật) · `docs/assets/` (42 contact
> sheet + 5 bảng đo). Danh mục đầy đủ + cách dùng: **`START_HERE.md` §1**.
>
> Còn **chỉ có ở nhánh dữ liệu** `arena/ef6b75ef-windwings-space-shooter-game-p` (`7e0da2ee3`):
> `raw/ui/*` (**803** file, ~142 MB cả cây) và ảnh chụp gốc chưa chọn lọc. Đọc **không cần merge**:
>
> ```bash
> git fetch origin 'refs/heads/arena/ef6b75ef-windwings-space-shooter-game-p:refs/remotes/origin/arena/ef6b75ef-windwings-space-shooter-game-p'
> git show origin/arena/ef6b75ef-windwings-space-shooter-game-p:datas/waves.json | jq
> git show origin/arena/ef6b75ef-windwings-space-shooter-game-p:docs/apk-analysis/52-game-scene-to-stage-map-waves.md
> ```
>
> Tên file cần lưu ý: `formula_traces` và `anim_clips` là **`.json.gz`**; typetree là
> `reverse-engineering/raw/typetrees/*.json.gz` (**142** file).
>
> Dữ liệu chạy thật (điện thoại) nằm ngay nhánh này:
> `docs/apk-analysis/ramus/2026-10-23-phone/*.json` — đối chiếu với dữ liệu tĩnh ở
> `CROSSCHECK-static-vs-runtime.md` cùng thư mục.

**Quy ước trong mọi file:**
- Mỗi bảng ghi `(nguồn: <file>)` hoặc có cột **Nguồn**.
- Suy đoán luôn đánh dấu `> Giả định:` — không trộn với số đo được.
- **Ghi rõ đơn vị** mỗi khi có hai cách đếm: *dòng* vs *lượt* (`Σ copies`) ở wave, *asset* vs *sprite*
  ở art. Quy tắc + 12 bẫy đã từng sai: `START_HERE.md` §5; số cụ thể: `ENCOUNTERS.md` §1.1.
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
| Wave / spawner / map | **282 / 11.089 dòng (23.757 lượt) / 250** | `waves.json`, `MapController.csv` | `ENCOUNTERS.md` §1 |
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
| **Damage của player** | `Gun_Attack.forceType = Enemy` **458/458** | `Gun_Attack.csv` không chứa súng player — **nhưng** 6 mảng damage/rate **đã decode** ở `ia-resolved.json` (`COMBAT.md` §6.1) ⇒ bind combat **theo report 81/82**: impl N → index N−1 (tàu 10001→2 · 10003→0); TTK = newdesign hoặc chờ measured — tích damage×rate **không dùng** (đơn vị damage·s, review peer) |
| **HP của player** | `Player_Health.StartHealth` chỉ có trong code | chưa bind "sống mấy phát" theo từng tàu (**khác** HP enemy đã có 150 cặp) |
| ~~**Tên enemy trong wave**~~ | ~~`waves.json` `enemies` = `"?"` **45.659/45.659**~~ | **SAI từ report 3**: bản `datas/waves.json` hiện hành có **0** dấu `?` · **109** prefab tên thật (claim **WRH4**) |
| **Trọng số random** | không có cột `weight`/`rate` ở bất kỳ bảng thưởng nào | phải tự quyết |

8 class config **không được serialize** trong `data.unity3d` (~~phải decompile~~ — đã đọc phần lớn qua asm + `ia-resolved.json`, đính chính ngay dưới):
`Player_Get_Datas` · `Droid_Data_Balance` · `Tech_Datas` · `Stage_Get_Datas` · `Map_Get_Datas` ·
`Enemy_Data_Balance` · `Device_Get_Data` · `GameDatas`
(giải thích: `BALANCE.md` §6.0b).

> **Đính chính 25/10:** "phải decompile" chỉ còn đúng với **field vô hướng chưa đọc**. Phần lớn
> giá trị **đã đọc** qua 139 file asm + `ia-resolved.json` (**17 method · 623 record**) và
> `datas/enemy_hp_by_id.json` (**150 cặp HP**). Xem `BALANCE.md` §6.0b.

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
| 2l | **Chốt phạm vi L1** (§4.2): giống cơ chế, không cần giống số ⇒ bỏ L2/L3, bỏ 2 tool, bỏ 1.416 chuỗi | ✅ xong — **[LỊCH SỬ, "bỏ L2/L3" đã bị thay]**: lần 14 (L3 = ĐÍCH KHÔNG hoãn) · lần 33 (L3 một phần) · report 96 (**ưu tiên L3 trước**) |
| 2m | `DATA_SYNC.md` — đọc dữ liệu vòng 3: **không merge**, chỉ đối chiếu; 3 kết luận cũ bị bác | ✅ xong |

**Đã sửa so với vòng 1** (đều do dữ liệu bóc lại khác bản trước): HP 981 → **800** dòng,
`Texture2D` 654 → **653**, `SkeletonDataAsset` 25 → **27**, page 66/32,5 MB → **67/31,0 MB**,
và premise "`Box_Rewards`/`Shop_Cell` có thưởng" của handoff là **sai**.

Mọi giới hạn còn lại nằm ở mục **"Còn thiếu / phải đoán"** cuối mỗi file — đó là danh sách
việc cho vòng sau, không phải lỗ hổng của spec.
