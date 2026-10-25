# DONE — "hoàn hảo" nghĩa là gì, và kiểm bằng gì

> Mục đích: biến chữ **"hoàn hảo"** từ một tính từ thành **4 mức kiểm được**.
> Không mức nào dùng % tự đánh giá. Số đếm được ghi **(A)**, ước lượng ghi **(C)**.
> Mục cuối: **Còn thiếu / phải đoán**.

> **Sửa lại (lần 4 — 25/10, audit toàn bộ 42 tài liệu `docs/spec/` + 71 `.md` apk-analysis):**
> câu **“chưa có giá trị / thiếu blob / 573 / 957 static mức D”** đã **sai**, và sai ở nhiều file.
> Hiện trạng đúng: `reverse-engineering/il2cpp/ia-resolved.json` có **17 method · 623 record**
> (**576** Map + **6** Player + 5 nhóm `Board_*` + Tech 7 + Device 12 + Droid 3 + Stage 2 + GameDatas 1).
> **Cái thiếu là `bind`, không phải `dump`.** Còn **thật sự** thiếu: ~~HP enemy (150 float trong
> `.rodata`)~~ — **gạch bỏ ở lần 5**, đã có bảng — coin/gem delta, thưởng hộp, trọng số rơi,
> ngưỡng VIP, mapping wave→stage.
> Đã sửa: `BALANCE` §6 (thêm §6.10), `DATA_SYNC` §18.2 + §23, `MISSING` §2.2c, `OPEN_ISSUES` B3,
> `ENEMY_HP_RUNTIME` §0, `AI_FEASIBILITY` §1.7, `apk-analysis/31`. Claim mới: **IA6 · IA7 · IAB1 ·
> IAB2 · APKD1 · IA8**.
>
> **Sửa lại (lần 5 — 25/10, rà nốt các câu "xin dump"):** phát hiện 3 nhóm câu **ảo** mà lần 4 bỏ sót.
> (1) `datas/enemy_hp_by_id.json` **đã có 150 cặp `id → HP`** từ chính `.cctor` đang bị "xin"; 3 file
> asm `Enemy_Get_Datas` / `Enemy_Controller` / `Enemy_Health` **đã có 41 method** ⇒ **không cần `.so`,
> không cần dump lại class**. (2) `15-enemy-hp.csv` là **field serialize** — `CB-*` **0/69** dòng > 0 —
> nên câu "109/109 prefab có HP" ở lần 4 là **ảo ngược**; sửa thành 981 dòng · **467** > 0, gộp dict
> được **108/109** prefab spawn có số HP. (3) `waves.json` hiện có **0** dấu `?` · **109** prefab tên
> thật ⇒ mọi câu "45.659 entry = `?`" là lịch sử. Claim mới: **WRH1–WRH5** (thay 2 claim WRH cũ).
> Đã sửa thêm: `ENEMY_HP_RUNTIME` §2/§4/§5/§6, `WHERE_TO_LOOK` §3/§4, `ENCOUNTERS` §9, `COMBAT` §6.1,
> `DESIGN_QUESTIONS`, `README` §5, `AI_FEASIBILITY` §1.7/§2.1, `START_HERE` bẫy 20, `HANDOFF_REPLY` §6,
> `CROSS_BRANCH` · `CROSSCHECK`.
>
> **Sửa lại (lần 6 — 25/10, đọc chọn lọc report 70–74 của nhánh dữ liệu `4fe0cef8e`, không kéo file):**
> (1) **khôi phục L2/L3**: không còn “❌ bỏ” — L2 **hoãn sau L1**, L3 là **đích cuối** sau L2
> (ý chủ dự án); (2) sửa hướng dẫn cắt sprite: **KHÔNG clamp** 40 rect — round từng biên + pad 1 px
> cho 9 case (report 72) — sửa 3 chỗ trong `ASSET_TRIAGE` §9; (3) sửa `txt_free_after` English thành
> “Free after” (lookup **first-index**, report 73) trong 2 CSV; (4) bổ sung nguồn font thật
> (7 TMP SDF + fallback chain) vào `ASSETS.md`; (5) pack **v2 identity-safe** bổ sung vào §21.2 +
> bẫy 17. Chi tiết + 6 việc peer giao: `DATA_SYNC.md` §24.
>
> **Sửa lại (lần 7 — 25/10, sau khi bị nhắc "bind xong lâu rồi"):** rút lại toàn bộ câu
> "việc kế tiếp = bind" trong `MISSING` §2/§4/§5 — **bind chính đã xong từ trước**: index↔tàu
> = **id − 10001** (T4), cấu trúc bảng Map = **11 cấu trúc / 614 mảng** đã phân loại
> (`DIFFICULTY_MODES` §7), chi tiết entry đã ghép (`map_table_segments.json` + `maps.json`).
> **Còn thiếu thật sự** (4): `kHp[mode]` · `missionKillPercent` 6/9 số · `StartHpPoint`←`Init`
> `0x1582f5c` (1 method asm) · kiểm runtime `rate` (cần thiết bị). Cập nhật thêm report **75**
> (mesh 2185/27.072 vertex, không quad/PPU mặc định, không clamp) — `DATA_SYNC` §24.7–24.8.
>
> **Sửa lại (lần 8 — 25/10, sau khi bị nhắc "cả 4 đều đã có"):** ⚠ *khối này ĐÃ RÚT ở lần 9 (ngay dưới) — đọc lần 9 trước.* Rút lại "còn thiếu thật sự (4)" của
> lần 7 — **cả 4 đều đã có theo dạng khác**: ① `kHp[mode]` **không tồn tại** như hệ số (chế độ đổi
> composition + thưởng; `DIFFICULTY_MODES` §3–5); ② `missionKillPercent` là **một** `float[3]` theo
> mission index — đủ **3/3**, "3×3 còn 6" là ảo đơn vị; ③ `StartHpPoint` ← dict **đã bind theo id**
> (dict là nguồn, `Init` chỉ plumbing); ④ `rate` = **giây delay theo nhánh** (report 53) — không phải
> *shot/giây*. Số sửa: `MISSING` §2/§4/§5 · `DIFFICULTY_MODES` §5.2/§5.5/§6/§8 · `OPEN_ISSUES` B8 ·
> `COMBAT` §6.1 · `DESIGN_QUESTIONS` · `ENEMY_HP_RUNTIME` §6 · `START_HERE` số 7 · `WHERE_TO_LOOK` ×2 ·
> `EXTERNAL_REFS` §7 · `UNITY_RULES` · `DATA_SYNC` §24.8 · `BALANCE` §6.0a.
>
> **Sửa lại (lần 9 — 25/10, chủ dự án xác nhận):** ⚠ *lô tài liệu của lần này
> (`DESIGN_QUESTIONS` · `OPEN_ISSUES` D1 · `MISSING` §3/§4 · `DIFFICULTY` §5.5 · `UNITY_RULES` #7)
> KHÔNG vào tree — script abort, chỉ DONE + README kịp ghi; "tally ✅ 31 · ⚠ 16 · ❌ 1" dưới đây là
> số định, lần 11 kéo lại với tally thật **33/14/1** (E2 và E3 là 2 dòng riêng, đều ĐÓNG-BỎ).*
> (1) **playback thật ĐÃ LÀM** — phiên phone
> 23/10 nằm sẵn trong repo (`ramus/2026-10-23-phone/`): bridge 8/9 endpoint, freeze/slow-mo,
> statics khi đang chơi, 7 lần chụp live với instance fields (`killCount` **276** · `coinCount`
> **540**), HP trong game khớp **2500** ⇒ mọi mục "cần thiết bị" chuyển thành "đọc JSON có sẵn";
> (2) **feel BỎ theo quyết định** — game gốc không có (0 site trên mẫu asm) và quá nhỏ ⇒ game mới
> không thêm (`OPEN_ISSUES` D1 · `DESIGN_QUESTIONS` hạng 3 · `MISSING` §3). Mở lại 3 câu cũ trong
> `DESIGN_QUESTIONS`: **A6 ✅** (bind map xong) · **B1 ✅** (HP theo id) · **C4 ⚠** (mẫu runtime
> 276→540) — tally mới **✅ 31 · ⚠ 16 · ❌ 1**. Runtime còn sót: 2 phép tái đối chiếu `CROSSCHECK`
> (Map content `&arr=256&depth=2` · device 12↔10) — làm khi có lần chạy, không chặn.
>
> **Sửa lại (lần 10 — 25/10, đồng bộ peer tới report 77 / `d66037d10`, peer 239 tests):** đọc chọn
> lọc report **76** (SpriteRenderer scene mở đầu: 1377 root, 218 typed Sprite, đếm activity ≠ visible)
> và **77** (5 Camera + 12 SpriteMask, ortho **9,6** khớp mốc spawn y=9,6 của mình, culling mask
> disjoint Game/UI, cutoff 0,2 raw) — `DATA_SYNC` §24.9–24.10 + task peer 3 nhóm. `START_HERE` số 5
> thêm khớp chéo ortho. Phía peer đang làm CameraScaler (chưa có report). 2 phép tái đối chiếu
> runtime bên mình **giữ nguyên** — report 76/77 không đụng Map-content và device 12↔10.

> **Sửa lại (lần 34 — 25/10, tái kiểm CẨN THẬN theo nhắc của chủ dự án "cứ làm kiểu quán tính" — tự bắt lỗi của chính mình):**
> ① **Bucket glyph lần 32 ghi SAI cơ chế**: CSV 624 chỉ chứa tên-chữ — bucket glyph (292) nằm NGOÀI
> CSV; đo lại: **118 tên số = 25 tàu + 32 boss + 13 drone + 48 unclassified** (số "~34 boss" là
> ước lượng sai, thật = 32) ⇒ sửa `ASSETS` §9.1 + `MISSING` row 16: vẽ theo bucket sẽ bỏ sót
> **70 sprite chính**; ② **TechStatLevel âm** rơi nhánh base (report 91) — sửa "≤0 → 0" thành
> "0 → 0; âm → base" ở §24.24 + `MISSING` §2.2 (lần 29 khái quát quá); ③ `START_HERE` L2 refresh
> tiến độ wing (93 config 17/24 · 94 emission · 95 pooled leaves); ④ **§24.28 report 95**
> (`4981c4ce2`): 5 leaves lifetime 5/5/4/10/4 · Activate TRƯỚC GetComponent<IBullet> ·
> **trampoline 23** branch ngoài method (64 raw bytes, không đoán opcode) · formation callbacks
> Combine trước caller; kéo `datas/wing_pooled_leaves.json` (datas/ = **42**).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 33 — 25/10, đính chính tuyên bố L3 theo bắt lỗi của chủ dự án — "thế mà dám tuyên bố L3 đủ"):**
> Hạ **L3 từ "input đã đủ / bắt chước đủ ✅" → 🟡 một phần** ở cả `START_HERE` row L3 · `DONE` §2
> row "Bắt chước đủ?" · §4.2 row L3: đủ để **vẽ lại từng sprite đã biết** (pixel/pivot/border ĐÓNG);
> **chưa đủ L3 trọn** — 505 unknown + 643 passthrough · chưa có bảng sprite→màn/prefab (UI chưa
> join) · rig spine inferred · worklist bucket glyph sai nhãn · **metrics/so-ảnh/timeline = gate
> chưa chạy lần nào** (kể cả câu "Đo cảm giác cần người chơi thật" cũ cũng sai — đã sửa: đo được
> bằng máy, blind-A/B bị thay lần 14/21). Sửa nốt §3 "5.818 field còn D" → 623 record decode +
> 4.861 SerializeField pack v2. **§24.27 report 94** (wing 13/22/23/24 emission — N chẵn ra N+1
> call, leaf entry là ranh giới quan sát; sửa nhãn `15b50ac` = PlayOneShot không phải camera
> shake); kéo `datas/wing_emission_flow.json` (datas/ = **41**). verify 209 PASS · 0 FAIL · 2 SKIP ·
> unittest OK.
>
> **Sửa lại (lần 32 — 25/10, kiểm "asset/sprite/prefab: ý nghĩa + gắn đầy đủ chưa" theo nhắc của chủ dự án — đo từ file thật, không suy):**
> `ASSETS` thêm **§9.1** + row 11: ý nghĩa 2.197 sprite = 925 rule + 124 mắt + 643 passthrough +
> **505 unknown**; **binding sprite→consumer CHƯA có join toàn cục** — `prefab_joins.csv` 3.870
> rows **0 row sprite** (chỉ Wave/Controller/Movement/Gun/Boss/Stage); UI 55.584 layout = summary
> bên này (cây ở peer raw); có sẵn: tàu 25/25 · boss 46 → sprite_path_id · scene-1 218/1.377 ·
> spine 27 rig *inferred*. **Lỗi ngữ nghĩa worklist 624**: `is_digit` gom tàu "10001"/boss "7001"
> vào bucket glyph-font (không mất sprite, nhãn sai — tách ra khi vẽ). `MISSING` thêm **row 16**
> (8 hệ một phần). Queue PR12 5 việc peer (join UI/prefab-sprite, 505+643 nhãn, 116 atlas, rig
> thật). verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 31 — 25/10, kiểm "stage/mode/thưởng ngày" theo nhắc của chủ dự án + đồng bộ report 93 peer `32bed14da8a`):**
> **Stage/mode — đã có từ trước, không phải chưa làm:** tổng **299 stage · 250 map · 282 wave ·
> 2 chapter** (`GAMEPLAY` §0/§3.6) · 3 độ khó đủ luật (`DIFFICULTY_MODES`) · khung 7 PlayMode + BP/
> quest/event season (`GAMEPLAY` §2/§3). **Gap còn lại của stage**: `MAX_STAGE_OF_CHAPTERS[]`/
> `MAX_ZONE_OF_CHAPTERS[]` **0 hit** trong `ia-resolved` (giá trị chưa bóc — độ dài từng chapter D) +
> **binding map→stage→wave** vẫn UNKNOWN (§2.1, chờ peer named map). **Thưởng ngày — chưa làm thật**:
> `MISSING` thêm **row 15** (gift login 30 ô · quest ngày/BP 85+39 · season · premium daily ·
> holiday 75 · rewarded video 48 · VIP · energy — cấu trúc A, **0 giá trị decode**: `MAX_LEVEL_BP`/
> `timeRewards`/`vipPoints` 0 hit; dump.cs chưa dịch class nào) + queue PR12. **Report 93**:
> review ACK92 ✓ không góp ý mới; wing config **17/24 impl** (count 3 kiểu, 14 array SHA,
> bẫy 13/21-clampL · 20-super-angleDelta) + fixture Unicorn chạy native bytes; kéo
> `datas/wing_implementations.json` (datas/ = **40**); peer đã nhận queue Arena/PvP.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 30 — 25/10, kiểm "Arena/PvP đã làm tới đâu" theo nhắc của chủ dự án):**
> **Chưa có batch/report nào đào riêng Arena/PvP** — hiện có (mức rải rác): `GAMEPLAY` §2 khung
> mode A (PlayMode 5=Arena · 6=PVP · 10 league · 10 rank · PVPMode lệch enum/text — Betting);
> `DIFFICULTY_MODES` §7 (AllArena*/AllPvP* tên+offset, giá trị chưa decode); `BALANCE` §6.4/6.6/6.8
> (GetArenaScore/PVPPlayScore chỉ signature; arenaPoints/arenaMedal/pvpMedal chưa giá trị);
> `DATA_SYNC` §e (GetListMapPvP — cấu trúc A/giá trị D); 2 luật PVP tình cờ theo reports 86/87
> (Player_Controller PVP `0x14c44e0` · HealHp 1 không WaitUntil); asset PVP1..10 (91 sprite) +
> Board_PVP 42 slot UI; dump.cs **40 class** chưa dịch class nào; `datas/` 0 file. ⇒ thêm **row 14
> MISSING** (🟡 khung A — luật in-game chưa đào) + queue PR12 (không khẩn, sau 23 wing impl).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 29 — 25/10, đồng bộ report 92 peer `713be8c85a0` + xử lý 3 góp ý wording review `de2d1366` (PR12 `6401242325`)):**
> ① §24.22: đường **player KHÔNG post event2** (`ItemCollected` trực tiếp → pool; chỉ drone post2 →
> `OnCollectItem` — tránh đếm kép); ② §24.24 + `MISSING` §2.2: AutoGain **guard Current>0** +
> **TechStatLevel(0)≤0 → techHeal 0** (level0 không phải ,01×1,0); ③ `MISSING` §5 footer: chỉ
> "phân loại cấu trúc" xong, named binding/thứ tự nạp còn đào; ④ **§24.25 report 92**: mapping
> sourceID 20001..20012 → Drone_Attack1..12 + Drone3 serialized **turnRate 1,0** (gap turnRate3
> ĐÓNG; idBlt 80084 serialized ≠ 80014 OnEnable — không bê serialized vào runtime) + save slots
> (`DroneUsed{slot}` default 0 · `CheckDoubleIDDrone` riêng · `get_indexDrones` new int[2] mỗi call,
> playMode4→[0,0]) + StartDrones (scale ,8 · pos ±20); ⑤ `MISSING` row 9 + DONE §4 gạch
> mapping/turnRate3. Kéo `datas/drone_loadout_flow.json` (datas/ = **39**). verify 209 PASS ·
> 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 28 — 25/10, áp report 90+91 peer `142eb5998` + xử lý 5 góp ý review spec (report 91 §6 / PR12 `6400980901`)):**
> **2 gap L1 ĐÓNG**: wing barrels + drone base-fire (90 — `wing_drone_flow.json`, hẹp scope
> impl1/source10003); **HP tàu ĐÓNG bằng công thức** (91 — `2500×(1+,18×TechStatPoints(0)+abi7)`,
> 3 writer + event36/64 + AutoGain 5 s, cấm tuyên bố "mọi tàu 2500"); **`Board_Drones` ĐÓNG**
> (UI power/price ≠ combat); **góp ý**: ③ cấm xác nhận chéo Board↔GetBaseDamage · ④ `MISSING` §5
> tách phân-loại-cấu-trúc (xong) khỏi binding-entry (unknown) · ⑤ ledger ACK đồng bộ (§24.22
> "chưa ACK89" → ACK89 ✓). Kéo 2 contract (datas/ = **38** file — AI1); ACK90+91 PR12.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 27 — 25/10, tái kiểm 5 mục L2 còn thiếu theo dữ liệu hiện hành + raw mới peer `39b377383`):**
> ① DPS runtime — không đổi, peer chưa có commit parity sau 83; ② 2 CROSSCHECK — không đổi (file
> `ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md`, cần lần chạy); ③ **HP tàu nâng bằng
> chứng:** `Player_Health` = static `StartHealth/CurrentHealth 0x0/0x4` + `Armor` + auto-gain —
> KHÔNG có bảng theo tàu trong 6 mảng (raw mới xác nhận), writer chưa đọc; ④ **Board_Drones đang
> được đào** (`Drone_Get_Datas.json`: GetBaseDamage/GetDroneSkillDamage/GetDroneAbilityCooldown…;
> `Board_Players` vẫn chưa có consumer); ⑤ bind 576 map — report 89 đã đọc `get_stageIndex`
> (Test-gate/IsBranch), unknown còn thứ tự nạp; ⑥ save schema — 89 thêm device internals
> (`GetPlayerDevices`/`GetDevice` dict lazy-load), trial/flush vẫn chưa. `MISSING` §2.1/2.2/2.2c/row 9
> đã cập nhật; xin peer đọc writer `StartHealth` qua PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 26 — 25/10, "cập nhật bổ sung + tái kiểm" — đồng bộ report 89 peer `c30dd46eb2` + chốt bảng L1/L2/L3 còn thiếu vào `DONE`):**
> `DATA_SYNC` §24.22 (2 đường nhặt player/drone — tag Item trước hit-guard · `IPooling.GetID` ·
> **công thức xu Coin1/Coin2**: 4 band balance ×L(tech) ×device ×.86 stage≤40 · store `coinCount`
> trước PostEvent48 · Burst 8 = **69/165 xu** — KHÔNG còn suy tiền từ chia 5); `MISSING` row 8
> (tiền nhặt **đã có công thức** — đóng gap) · row 9 (+ drone bắn nền/wing nhịp: peer đang
> recover, chưa report); `START_HERE` row L2 (+89, sót đủ 6 mục `MISSING` §2); `DONE` §L1 thêm
> row "Còn thiếu" (4 mục) · §L2 "Còn thiếu" mở đủ 6 mục; kéo `datas/pickup_currency_flow.json`;
> ACK89 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 25 — 25/10, rà tài liệu trả lời "L1/L2/L3 còn thiếu gì" + đồng bộ report 88 peer `eaa5c74342`):**
> `DATA_SYNC` §24.21 (producer hit thật: skeleton gán đè/DropGold Combine/19 co-attachments ·
> DropGold **28/10** strict-threshold, HP reread, không dùng `_damage` · event6 budget **28 → 8
> object** (chia 5) — chưa chứng minh tiền nhặt; radius 4 = bits6766e63f); `START_HERE` row L2
> (producer/serialized joins **đã nối** — còn DPS runtime + 2 tái đối chiếu CROSSCHECK); `MISSING`
> row 8 (+ chuỗi report 88, gap còn `OnCollectCoin1/2`); kéo `datas/enemy_hit_callback_flow.json`;
> ACK88 qua PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 24 — 25/10, audit toàn bộ sau nhắc của chủ dự án — quét pattern trên 45 file):**
> ① **ENEMY_BEHAVIOUR đo lại trên bản hiện hành 981** (CSV 982 dòng gồm header; cũ ghi 800):
> turret **112/981** · facingMove **949/981** · ≥2 tốc độ **137/981** · phổ biến **5,0 (562/981)** ·
> Meteorite **852 dòng/577 object**; "399 path" là đo bản 800-cũ — CSV không có cột path ⇒ ghi chú
> ở MISSING row 4; ② BALANCE §1 bảng nguồn (800/394 → **981/467 + 150 cặp**; 189/800 → **241/981**);
> ③ DIFFICULTY §bảng đối chiếu: row `kHp` → KHÔNG tồn tại; ④ DATA_SYNC: §kiểm lại SerializeField
> (pack v2) · §8 rows 1/2/3/6 (static 623 record · SerializeField pack · HP boss gom prefab
> `boss_hp.json` **253 prefab** (đo lại từ meta của file — 277 ghi trước đó sai) · pivot/border report 75) · §22.3 ("DPS = proxy" → damage·s); ⑤ 6 worklist
> còn "xin AssetRipper" → pack v2 (TUNING_KNOBS ×3 · AI_FEASIBILITY ×3 — feel row BỎ) · PARALLEL_TASKS
> header LỊCH SỬ · ENCOUNTERS cách-đọc-cũ (m_PathID/AssetRipper/Frida) → ĐÃ RESOLVE (WRH4);
> ⑥ DONE các row cũ (Chưa-đọc tool · 5.818 field · 92 prefab/800 dòng · 641 → **624** ×5 chỗ) ·
> README 3 row (COMBAT TTK · BALANCE +150 cặp · DESIGN_READINESS proxy → damage·s) ·
> DESIGN_QUESTIONS B4. **Sau verify bắt thêm 2 nhóm:** ⑦ **ECONOMY `Box_Rewards` đo lại = 1065
> dòng** (cũ ghi 800 — `id=0`/`number=0` **1065/1065**; bảng phân bố root làm lại từ CSV: 75 root,
> top `Board_BattlePass` 85 · `Board_Shop` 84 · `EndgameLoader` **36** · BP tổng 85+39=124; sửa
> ECONOMY ×11 + AI_FEASIBILITY + BALANCE + UI) · ⑧ **`boss_hp.json` = 253 prefab** (meta
> `count=253`; 277 ghi trước đó sai nguồn — pack v2 peer đo 256/P5; DATA_SYNC §8 + DONE log).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 23 — 25/10, kiểm câu hỏi chủ dự án "peer đã đính chính ảnh/asset/sprite — cập nhật chưa?"):**
> `DATA_SYNC` §24.1–24.7/24.9–24.10 **đã đồng bộ đủ reports 70–77 từ các lần trước**; kiểm lại spec
> thấy 3 chỗ còn stale so với các report đó — đã sửa: ① `ASSETS` §9 (4/6 "không xác định" → **ĐÓNG**:
> kích thước pixel — manifest + geometry + **pixel tái tạo 2185/2185** (72); border 9-slice — **75**;
> pivot — **75**; row 3 spine-mapping 🟡 một phần — **71**; row "thiếu width×height" → ✅); ②
> `DESIGN_READINESS` §5 UI-art ("chưa phân tích nội dung" → **đã phân tích tĩnh** 72/75/76, chưa
> render approval); ③ `SYSTEM_MANIFEST` Assets row (đủ reference vẽ: kích thước + pivot + border;
> worklist 624) + `START_HERE` bẫy 17 (pack chưa "đủ APK" nhưng **đủ reference vẽ**). Không có
> report asset/sprite mới sau 77 (78–87 = combat/camera/lifecycle).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 22 — 25/10, vai "AI nhận viết game" phản biện + đồng bộ report 87 peer `0561a2185b`, 412 tests):**
> **(a) Phát hiện khi dựng thử 30 s đầu — CHỈ ghi ở đây vì dịch ngược CHƯA XONG** (chưa sửa
> `SYSTEM_MANIFEST`/`MISSING` để khỏi đóng đinh): ① **pháo cánh**: damage có (`StartWingCannonDamages[24]`)
> nhưng **nhịp/barrels-theo-level chưa có luật** — dấu vết: `pN_startShotRate` · `SetupBarrels` đọc
> getter `Player_Ingame 0x14b1eb0` (report 80) — AI dựng sẽ phải newdesign có ghi hoặc chờ đào;
> ② **drone**: roster 13 + skill fields + modifiers (`abi20/21/25`) có, **luật bắn nền của drone
> chưa có**; ③ tài liệu = **snapshot tới tip `0561a2185b`** — bên kia đào mỗi ngày, người dựng cần
> biết tuổi bản đồng bộ. Cả 3 **không chặn bắt đầu L1** (main cannon/enemy/boss đầy đủ nhất);
> đã gửi 2 gap ① ② sang PR12 cho hàng đợi đào của nhánh dữ liệu.
> **(b) Report 87**: RebornDone `TimeResetInvincible 3,0` · `TimeCanActiveInvincible 10,0`; shield
> callbacks **không refcount** (callback(false) có thể tắt invincible của extra-life); `activeHitEnemey@90`
> = contact-hit, không phải khóa di chuyển; zone invisible/heal — `SYSTEM_MANIFEST` row hồi sinh +
> `DATA_SYNC` §24.20. Peer pin ACK85/86 (`raw/peer-review/ack-85-86-6400213174.json`).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 21 — 25/10, nhận review 6 finding của peer trên tip `b8f72a4127` + đồng bộ reports 85–86 peer `82f14784e5`):**
> Peer review trực tiếp nhánh spec (không chỉ changelog) — **sửa đủ 6**: ① DATA_SYNC §24.17 impl **11**
> ≠ `shotRate/number` (chỉ 13; descriptor 0,04 + duration theo rank); ② tách **Player9_Clone** (0,34)
> khỏi **projectile 7/9** (0,35) — gộp nhầm trước đây; ③ **bỏ TTK theo tích damage×rate** (đơn vị
> **damage·s**) — COMBAT §0/§6.1/§6.2 · BALANCE §1.1b · MISSING · ENEMY_HP_RUNTIME · BOSSES ·
> COVERAGE_AUDIT · README — TTK = **newdesign** (HP thật + DPS giả định) hoặc **measured**; ④ COMBAT
> §6.4 **241/981** (sửa 189/800) + native rule `noDamage && !ignoreInvincible` skip / ignore bypass
> (report 85) — bỏ kết luận "chỉ trang trí"; ⑤ **superseded ngay tại đoạn**: COMBAT §10 (5 rows đã
> đóng), BALANCE §0.6.2/§0.6.x, UNITY_RULES §12 (rows 1/6); ⑥ START_HERE "tra là có hết / không test"
> → **tra reference trước + scoped unknown không bịa + automated regression/reference checks bắt buộc**
> (metrics = gate phát hiện lệch, không phải approval) — đồng bộ DONE §2 · MISSING §0 ·
> SYSTEM_MANIFEST · START_HERE khối mục đích + L3. **Reports 85–86**: receivers enemy/player đã dịch
> (2 callbacks + truncations + HP re-read; Delayed = WaitUntil · MB 3×Wait(1) · ability32 recursive
> không dedup) + OnExtralife/heal lifecycle (1 s, normal 0,05+0,5 · PVP 1 · zone 1,235 % maxHP) —
> `SYSTEM_MANIFEST` 2 dòng mới/cập nhật · `OPEN_ISSUES` D5 · `DATA_SYNC` §24.18–24.19.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 20 — 25/10, đồng bộ report 84 peer tip `c7f72fe22e`, 327 tests):** peer dịch đủ
> **25 combat coroutine** (CFG + jump-table + models chạy được) — 3 đính chính ghi vào
> `SYSTEM_MANIFEST` (nhịp bắn) + `OPEN_ISSUES` D5 + `DATA_SYNC` §24.17: `_delay` 7/9 **sau** attack ·
> 17 chờ theo cặp · **18 = toggle particle, không spawn đạn**; clone 0,34/pumpkin 2-1-4. Peer chờ
> ack (PR12 `6399840843`) — đã ack sau khi cập nhật. Khối "mục đích" bên dữ liệu **vẫn chưa được
> commit** (grep tip = 0) ⇒ refresh `docs/HANDOFF_DATA_PURPOSE_6144d7cb.md` **v2** với anchor mới
> (report 84 đã đổi 3 chỗ chèn) + nhắc lại trên PR12.
>
> **Sửa lại (lần 19 — 25/10, vai "AI tiếp nhận" soi tài liệu — thiếu/nhất quán):** ① **worklist art**
> (thiếu lớn nhất cho nhiệm vụ thiết kế duy nhất — vẽ art): có số "~641" nhưng **không có danh sách**
> ⇒ tạo `tools/art-worklist.py` + `docs/assets/art-worklist.csv` (**624 thứ phải vẽ + font 292 glyph**,
> luật pin tái tạo được; "~641" = ước lượng cũ chênh ≈2,7 %); ② SYSTEM_MANIFEST/DATA_SYNC đánh dấu
> 3 file hợp đồng combat **chỉ có ở nhánh dữ liệu** (`combat_chain_contract` · `combat_argument_audit` ·
> `combat_rate_consumers` — xin qua PR12); ③ GAMEPLAY §0: "800 instance HP" → **981 + 150 cặp id** +
> trỏ path đầy đủ; DONE art row 641→**624** + link; ④ TUNING_KNOBS: "chạy AssetRipper" → pack v2 bên
> peer đã chứa binary. Kiểm khác: §-trỏ từ SYSTEM_MANIFEST/START_HERE **0 lệch**; MISSING §6 gate
> victory đủ; GAMEPLAY §7 thứ tự build giữ nguyên.
>
> **Sửa lại (lần 18 — 25/10, đồng bộ reports 80–83 peer tip `23b1ceec31` — ĐÍNH CHÍNH bind):**
> ① **"id − 10001" bị hẹp scope**: peer CFG-proof **72/72** getter call (report 82) + source prefab
> (report 81) ⇒ **combat**: impl `Player_Attack_N` đọc mảng index **N−1**, tàu **10001 → index 2**
> (proxy 12.864) · **10003 → index 0** (proxy 21.600) · 10004–10024 → id−10001; công thức cũ
> (`0x14e2ce4`) **giữ nguyên ở consumer save/load**. Sửa 8 file: MISSING §2.2/row 9/§2-đầu/§6 ·
> COMBAT §0/§6.1 · BALANCE §1.1b/§5.2 · DESIGN_READINESS ①/B3 · README 2 dòng · SYSTEM_MANIFEST ·
> DATA_SYNC §22.3/§24.8. ② **Nhịp bắn đủ 24/24** (report 83): interval nhóm phát — dual deadline,
> N extra ⇒ N+1 entry, không catch-up (80), modifier tech tier 0/3/5/8/10/12 % (82), demo override
> 3,0/4,0; OPEN_ISSUES D5 cập nhật A/B. ③ **Luật mất máu enemy** (81 §E): armor factor ±, overkill
> clamp 0, IsCaAttack@0x2F, noDamage 241/981 (sửa 189/800 cũ), Shield_Sub riêng; COMBAT §6.2.
> ④ 38 ends_clean = coroutine Reset/OnDrawGizmos — không cắt (đừng xin dump). DATA_SYNC §24.13–24.16.
>
> **Sửa lại (lần 17 — 25/10, chuyển bổ sung "mục đích" sang nhánh dữ liệu):** chủ dự án yêu cầu
> cập nhật cả bên nhánh dữ liệu. Khuôn phiên chỉ push nhánh spec ⇒ giao bằng kênh chuẩn: file
> **`docs/HANDOFF_DATA_PURPOSE_6144d7cb.md`** (3 chỗ chèn paste-ready vào `START_HERE_NEW_GAME.md` ·
> `HANDOFF_AI_TASKS.md` · `datas/README.md`, anchor trích từ tip **`ffa9959c9e`** — peer đã lên
> report 82, sync đầy đủ để vòng sau) + comment PR12 yêu cầu peer tự commit theo quy trình bên đó.
> Không đụng luật bằng chứng (mức A/B/C, pin SHA) — chỉ bổ sung mục đích sản phẩm.
>
> **Sửa lại (lần 16 — 25/10, chủ dự án: "đừng đóng đinh mọi thứ — chỉ thiết kế lại art là được"):**
> viết lại các khối "mục đích" của lần 15 theo hướng **giảm việc, không thêm rào cản**: bỏ giọng cấm
> đoán ("không được lệch hướng / không suy diễn / không cải tiến") → nói điều dương: **mọi thứ trừ
> art bản gốc đã trả lời hết — tra reference là xong, không test không hỏi; việc thiết kế duy nhất
> là vẽ lại art, giữ chuẩn ở `VISUAL_DESIGN`**. Sửa 7 chỗ: `START_HERE` (khối đầu) · `DONE` §2 ·
> `MISSING` §0 · `DESIGN_READINESS` · `SYSTEM_MANIFEST` · `VISUAL_DESIGN` · `README`.
>
> **Sửa lại (lần 15 — 25/10, chủ dự án chốt mục đích — ghi vào mọi điểm vào):** *"dịch ngược để làm
> gì: để có các thứ để từ đó thiết kế game mới theo cách **bắt chước**, chứ không phải phát triển
> game mới theo kiểu **sáng tạo**. Để AI phát triển mà không bị lệch hướng hay sai logic hay sai art
> hay animation và tất cả mọi thứ — **đã có bản gốc đối chiếu, không test không hỏi lại, có bản gốc
> trả lời**. Cơ chế game đã có từ nghìn đời nay, tất cả đều bắt chước nhau, thiết kế lại hình ảnh cho
> khác thôi."* — Ghi nguyên khối ở **đầu `START_HERE.md`** + dòng dẫn ở `DONE` §2 · `MISSING` §0 ·
> `DESIGN_READINESS` đầu trang · `SYSTEM_MANIFEST` header · `VISUAL_DESIGN` header (hình khác —
> chuẩn giữ). Kèm sửa lệch sót của lần 11: `DESIGN_READINESS` header ⑥ tally 31/16/1 → **33/14/1**.
> verify 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 14 — 25/10, chủ dự án đổi định nghĩa nghiệm thu L3):** *"không cần người test thật
> vì APK gốc đã thiết kế chuẩn trải nghiệm, ta phải copy những trải nghiệm ấy; art cũng thế — chuẩn
> màu sắc, ánh sáng; dự án để học tập thiết kế, sao lại hoãn"*. ⇒ **L3 đổi nghĩa + đổi thứ tự**:
> (a) nghiệm thu = **đối chiếu reference đo được bằng máy** (metrics `VISUAL_DESIGN` + so ảnh cùng
> scene + timeline 795 event + audio 15 rules) — **bỏ blind A/B + playtest thống kê**; (b) **KHÔNG
> hoãn** — đích của dự án, bắt đầu khi L1 chạy được, **song song với L2** (câu "đích cuối sau L2" của
> sáng cùng ngày bị thay); (c) input xác nhận **đã đủ** (pack v2 + pixel/geometry/spine/font +
> metrics 35 ảnh). Sửa: `DONE` §2 (L2 + L3) · §4.1 · `START_HERE` §2 · `MISSING` §4 ·
> `DESIGN_READINESS` đầu trang + §5 · `VISUAL_DESIGN` mở đầu + §6. Cụm "playtest người thật" trong
> log lần 11 bên dưới là **lịch sử, không còn đúng**.
>
> **Sửa lại (lần 13 — 25/10, audit "còn chỗ nào ngu" trước khi bàn giao AI mới):** sửa 6 chỗ mâu
> thuẫn/stale mà verifier không bắt (không có claim neo): `START_HERE` §2 **L2** ("6 blob rodata
> chưa bóc" — sai, số đã decode/bind; sót DPS-runtime + 2 tái đối chiếu) và **L3** ("bỏ" → **HOÃN,
> không bỏ**) + 2×"40 file" → 43 + §4 thêm `SYSTEM_MANIFEST.md`; `README` row Damage ("còn thiếu
> bind" → xong + proxy) + "phải decompile" (strike); `BALANCE` §5.2 (bind xong); `UNITY_RULES` §11
> row 1 `kHp` (không tồn tại) · row 2 `pct` (đã đọc [0,2/0,6/0,98]) · row 4 feel (BỎ); `DATA_SYNC`
> §22.3 "Vẫn chưa" 3/4 mục đã xong. Kiểm lại: MISSING §1 tally **8 đủ · 5 một phần · 0 thiếu**
> khớp `START_HERE`; `AI_FEASIBILITY` mức-B `.so` giữ nguyên (đúng — có guard chống xin .so cho HP).
> verify **209** PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 12 — 25/10, đồng bộ report 78–79 peer `549a7b5b7c`, peer 250 tests):** peer review
> nhánh mình tại `029559d47` + đào native nhịp bắn tàu 1 (raw `player-firing`). P0 qua PR12:
> ① DPS/TTK — **sửa rồi**: report 79 chứng minh tàu 1 dùng `StartMainCannonRate` làm **interval đặt
> hạn bắn** (deadline `@0x10c = Time.time + rate @0xa8`) ⇒ `damage × rate` chỉ là **proxy**, không
> giao như DPS; kèm **đính chính report 53** (delay spawn) từng bị dùng đóng nhầm consumer player —
> sửa `MISSING` §2.2, `COMBAT` §0/§6.1/§6.2, `BALANCE` §1.1b, `DESIGN_QUESTIONS` B4 (còn stale
> "thiếu StartHp"), `BOSSES`, `ENEMY_HP_RUNTIME`, `COVERAGE_AUDIT` §1; ② bind "chưa bind" → **ĐÃ
> XONG** ở COMBAT/BALANCE; ③ CameraScaler **report 78**: `ortho = max(h/w × 5.4f, 9.6f)` — 9,6 là
> **sàn**, không cố định (`DATA_SYNC` §24.11 + `START_HERE` số 5); ④ **`SYSTEM_MANIFEST.md`** mới —
> bảng tối giản `hệ thống → raw → luật → tự chọn → test` (task ⑤); ⑤ `OPEN_ISSUES` thêm **D5**.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK. Reply PR12 sau push + CI.
>
> **Sửa lại (lần 11 — 25/10, audit "giao thiết kế được chưa" + cứu lô lần 9):** audit 4 tài liệu
> điểm vào (`START_HERE` → `MISSING` → `DESIGN_READINESS` → `COVERAGE_AUDIT`) bắt stale: tally cũ
> 29/15/4 + claim "151/149" (thật **211 claim · 209 PASS · 2 SKIP**), "2 chặn map→wave + HP runtime"
> (**ĐÃ ĐÓNG** — bind xong + `kHp` không tồn tại), L3 ghi "BỎ" (sửa lại **HOÃN — đích cuối, không
> bỏ**), UI-art "chưa kéo về" (stale — pack v2 report 70), MISSING row 11 audio (**15 luật** trong
> `datas/audio_rules.json`, report 67), START_HERE bẫy 17→**21**. Cùng lúc phát hiện lô lần 9 mất
> (xem khối lần 9) — kéo lại hết: `DESIGN_QUESTIONS` A6/B1 ✅ · C4 ⚠ · E2/E3 ✅ ĐÓNG-BỎ (tally
> **33/14/1**), `OPEN_ISSUES` D1 BỎ, `MISSING` §3/§4, `COVERAGE_AUDIT` §0/§2/§5. **Kết quả audit:
> L1 GIAO ĐƯỢC** — 0 chặn số; thiếu thật = 2 tái đối chiếu runtime + playtest người thật (sau L2).
> verify **209** PASS · 0 FAIL · 2 SKIP · unittest 45 OK.
>
> **Sửa lại (lần 3):** pipeline vòng 3 (nhánh `ef6b75ef`, commit `61d5385`) đã resolve
> **tên enemy trong wave** — **22.451** entry, **109** prefab, **0** `"?"`. Đây là mục
> tôi từng ghi là "chưa biết". Số mới ở `ENCOUNTERS.md` §2.6.
>
> **Sửa lại (lần 2):** bản đầu của file này phóng đại khối lượng. Sau khi đọc **tên gốc** spawner
> và **dedup**, con số thật nhỏ hơn nhiều: **48 archetype spawner**, **109 prefab enemy được spawn**,
> **11.089 dòng / 10.782 cấu hình khác nhau** (median **28,5 dòng/wave**), **boss là 45 wave riêng**. Xem §1.

---

## 0. Trả lời ngắn

**"Game đơn giản" — đúng. "Bắt chước là ra" — đúng, nhưng chỉ tới một mức.**

| Mệnh đề | Đánh giá | Vì sao |
|---|---|---|
| Game **đơn giản về cơ chế** | ✅ **đúng** | 2.5D sprite · physics 2D · không netcode realtime · không navmesh · không rig 3D (§`AI_FEASIBILITY.md` §1.9) |
| **Bắt chước** cho ra game **chơi được** | ✅ **đúng** | cơ chế đã có đủ số; AI dựng được khung |
| Bắt chước cho ra game **hoàn hảo** | 🟡 **đúng một phần** | bắt chước giải quyết **thiết kế**, không giải quyết **khối lượng** và **kiểm chứng** |

> **Điểm cần tách:** *đơn giản* và *nhỏ* là **hai trục khác nhau**.
> Game này **đơn giản** (ít hệ thống phức tạp) nhưng **không nhỏ** (rất nhiều đơn vị nội dung).
> Bắt chước làm trục "đơn giản" rẻ đi gần như bằng 0. Nó **không** làm trục "khối lượng" rẻ đi.

---

## 1. Hoá đơn sản xuất — **sửa lại: nhỏ hơn tôi nói**

> ⚠ **Mục này bản trước sai** — nhưng sai vì **lẫn đơn vị**, không phải vì dữ liệu có bản trùng.
> `waves.json` có **11.089 dòng** (mỗi dòng = 1 `Call_Data`), và **23.757 lượt** (`Σ copies`).
> Câu "84,2 spawner/wave" là lấy **lượt/wave**; câu "1.015 cấu hình đặt tay" đúng (1.015 tên khác
> nhau), nhưng **1.015 tên rút về 53 tên gốc** — cả hai đều thật, ở hai mức khác nhau.

### 1.1 Quy luật spawn — có, và rất rõ

Tên spawner có dạng `TênGốc (n)` — **`(n)` chỉ là số thứ tự instance**, không phải cấu hình khác.
Bỏ hậu tố đó: **1.015 tên → 53 tên gốc**, trừ 5 marker (`StartPoint`/`EndPoint`/`CheckPlayerNo`/
`KhoaPlayer`/`Endpoint`) còn **48 archetype spawner thật**.

| Archetype | Số lần | `spawn_type` | `rate` | `y_spawn` |
|---|---:|---|---|---|
| `CB1 Nhanh` (nhanh) | 4.622 | point_range **100%** | **1,0 cho 4.622/4.622** | **9,6 cho 4.618** |
| `Point 1` | 4.192 | point / point_range | 1,0 (2.536) · 0,0 (1.656) | 12,0 (2.262) |
| `CB1 Vua` (vua) | 2.951 | point_range **100%** | **1,0 cho 2.951/2.951** | **9,6 cho 2.945** |
| `CB1 Cham` (chậm) | 1.487 | point_range **100%** | **1,0 cho 1.487/1.487** | **9,6 cho 1.487** |
| `6-CB09_Left` | 1.238 | point_range | 0,0 (1.172) | 9,6 (1.238) |
| `CB1` | 1.150 | point_range | 0,0 (953) | 12,0 (880) |
| `Path_CB3_5` | 1.130 | path **100%** | 0,5 (571) | 9,6 (1.114) |
| `Group` | 929 | point_range | 0,0 (929) | 0,0 (605) |
| `ChamNo` | 536 | point_range | 1,0 (536) | 9,6 (528) |
| `CB15` | 435 | point_range | 0,0 (359) | 0,0 (269) |
| `Point_H` | 387 | point | 0,0 (387) | 12,0 (387) |
| `CB1 Ban Vua` | 304 | point_range | 1,0 (304) | 9,6 (304) |

**Đọc ra:** mỗi archetype có **bộ tham số gần như hằng số**. `CB1 Nhanh` = "nhanh, một nhịp,
xuất hiện ở y 9,6" — chạy 4.622 lần với đúng cùng tham số. Đây là **quy luật**, không phải
đặt tay từng cái. **Bạn đúng.**

### 1.2 Ba đơn vị — và con số đúng cho từng câu hỏi

| Câu hỏi | Số đúng | Đơn vị |
|---|---:|---|
| Có bao nhiêu **cấu hình** spawn? | **11.089** | dòng = 1 `Call_Data` component |
| Có bao nhiêu **lượt sinh quân**? | **23.757** | `Σ copies` (bảng cũ ghi số này) |
| Bỏ marker thì còn bao nhiêu lượt? | **22.385** | `Σ copies` của dòng không phải `StartPoint`/`EndPoint` |
| Bao nhiêu **cấu hình khác nhau** (gộp `tên + type + rate + speed + y` trong từng wave)? | **10.782** | dòng, dedup **trong từng wave** (đo 25/10) |
| Median mỗi wave | **28,5 dòng** · **62 lượt** | — |

> **Cái từng bị gọi là "bản trùng export" thực ra là `copies`** — một field của dữ liệu, không
> phải lỗi export. Sau khi gộp theo 5 trường, **10.782 / 23.757 = 45,4 %** lượt là *cấu hình mới*;
> phần còn lại là **cùng cấu hình chạy nhiều lần** (`copies`).
>
> `> Nhận định (mức B):` nội dung wave **không phải** 23.757 lần đặt tay — mà là **~10.800 lần**
> chọn-trong-**48 archetype**-và-đặt-vị-trí (53 tên gốc − 5 marker). Đây là phần **tự động hoá được
> gần hết**.

### 1.3 Chỉ có **92 prefab enemy** — không phải hàng trăm

Đếm từ `Enemy_Datas.csv` theo **root của prefab path** (bỏ sub-object `Gun5`/`HP`/`Child2`):

| Họ | Số prefab | Dải id | Vai trò |
|---|---:|---|---|
| `CB` (30xxx) | **26** | 30001–30060 | enemy thường chương 1 |
| `CD` (31xxx) | **13** | 31002–31016 | " |
| `GD` (33xxx) | **4** | 33002–33005 | " |
| `XB` (34xxx) | **4** | 34003–34006 | " |
| `BB` (36xxx) | **3** | 36001–36004 | " |
| `H` (38xxx) | **2** | 38001–38002 | " |
| **Tổng enemy thường** | **52** | | |
| `Boss` (37xxx + 39xxx) | **39** | 37001–39021 | boss |
| `MB` (39xxx) | **1** | 39005 | mini-boss |
| **Tổng** | **92** | | |

**Bạn đúng lần nữa:** **52 loại enemy thường** + **40 boss-family**. Không phải 690 GameObject
như tôi ghi trước đó — 690 là **mọi** object trong prefab (súng, hitbox, con, hiệu ứng).

> ⚠ **Ba số "enemy" khác nhau — đừng tráo:**
> **92** = prefab có script `Enemy_Datas` (bảng trên) · **109** = tên prefab **thực sự được spawn**
> trong `waves.json` (đo 25/10) · **189** = mọi GameObject có HP trong `datas/enemy_hp.json`.
> Khi nói "game có bao nhiêu loại quân" thì dùng **109**; **92** là số *loại có script HP*.

> **Đã resolve (vòng 3):** **22.451** entry · **109** prefab · **0** `"?"` — xem `ENCOUNTERS.md` §2.6.
> Trần nội dung enemy là **109 prefab**, không phải hàng chục nghìn.

### 1.4 Boss là **màn riêng** — xác nhận

| Nhóm wave | Số wave | Vai trò |
|---|---:|---|
| `Wave_00xx` – `Wave_02xx` | **236** | campaign thường |
| `Wave_70xx` | **22** | **boss chương 1** — màn riêng |
| `Wave_90xx` | **23** | **boss chương 2** — màn riêng |
| `unknown` | 1 | lỗi export |
| **Tổng** | **282** | |

Board cũng tách: `Stage_Behaviour.stageType` = Normal **199** · **Combat 49** · Boss **26** ·
MiniBoss **25** (nguồn: `Stage_Behaviour.csv`).

> **Sửa lỗi đọc trước:** tôi từng ghi "686 spawner `spawn_type = boss`". Sai — `boss` ở đây là
> **marker `EndMapPoint`**: **327 dòng = 686 lượt**, có ở **gần như mọi** wave; `special` là
> **`StartPoint`**: **281 dòng = 686 lượt** (hai số 686 trùng nhau, đừng đọc thành một).
> Nội dung boss nằm ở **45 wave riêng** (`70xx`/`90xx`).

### 1.6 Art cũng co lại — **2.185 sprite → ~641 thứ phải vẽ**

Đếm từ `04-asset-manifest.csv` (2.185 Sprite), bỏ hậu tố `(n)`/`_n`/số cuối:

| Nhóm | Số | Ghi chú |
|---|---:|---|
| Sprite ghi nhận | **2.185** | |
| Glyph / ký tự (1–2 ký tự hoặc toàn số) | **292** | `%` `+` `1`…`9` — **một bộ bitmap font**, không phải 292 hình |
| Sprite còn lại | **1.893** | |
| **Tên gốc sau dedup** | **~641** | biến thể màu/frame gộp về một |
| **Tỉ lệ nén** | **~3,4×** | |

**Hệ quả:** hoá đơn art là **~641 hình + 1 bộ font**, không phải 2.185.
**Danh sách thật để vẽ (lần 19):** `docs/assets/art-worklist.csv` — **624 thứ phải vẽ + 1 bộ font
292 glyph**, sinh bằng `tools/art-worklist.py` từ `docs/apk-analysis/04-asset-manifest.csv`
(luật pin: glyph = ≤2 ký tự/toàn số; gốc = lowercase + bỏ `(n)` + bỏ đuôi số ×2; số "~641" ở bảng
trên là **ước lượng cũ** — chênh 624 vs 641 ≈ 2,7 %, dùng danh sách cho việc vẽ).
Với năng suất 10 hình/ngày, đó là **~64 ngày làm việc** — khớp với ước lượng
**2–3 tháng/1 artist** đã ghi ở `AI_FEASIBILITY.md` §6. **Ước lượng đó giữ nguyên**, nhưng
lý do đúng hơn: không phải vì "2.185 hình" mà vì **641 hình + sửa đi sửa lại**.

> `> Nhận định (mức B):` đây là lần thứ **ba** trong phiên này mà một con số lớn co lại khi
> đọc đúng tên gốc (spawner 1.015→53 · enemy 690→92 · sprite 2.185→641). Quy luật: **dữ liệu
> export đếm theo instance, không theo loại.** Con số "loại" luôn nhỏ hơn nhiều.

### 1.5 Hoá đơn còn lại

| Hạng mục | Số lượng (A) | Nguồn |
|---|---:|---|
| Wave | **282** = 236 campaign + 45 boss + 1 lỗi | `waves.json` |
| Cấu hình khác nhau **sau dedup** | **10.782** | tính lại §1.2 |
| Archetype spawner | **48** (+5 marker) | tính lại §1.1 |
| Prefab enemy | **92** = 52 thường + 39 boss + 1 MB | `Enemy_Datas.csv` §1.3 |
| Stage trên board | **299** (Normal 199 · Combat 49 · Boss 26 · MiniBoss 25) | `Stage_Behaviour.csv` |
| `Gun_Attack` → cấu hình súng | **458 → 420** | `Gun_Attack.csv` |
| Ô shop | **315** trên **20** board | `Shop_Cell.csv` |
| Class UI | **125** | `class-inventory.csv` |
| Sprite ghi nhận | **2.185** | `docs/apk-analysis/04-asset-manifest.csv` |
| **Art phải vẽ (sau dedup)** | **624** tên gốc + **1 bộ font 292 glyph** | `docs/assets/art-worklist.csv` (`tools/art-worklist.py`; §1.6) |
| Atlas page | **67** · 31,0 MB | `04-asset-manifest.csv` |
| AudioClip | **69** | `04-unity-assets.md` |
| Chuỗi localization | **1.416** | `12-localization.csv` |
| SKU IAP | **170** | `IAPProduct.csv` |

## 2. Bốn mức "hoàn hảo" — và mỗi mức kiểm bằng gì

> **Mục đích tổng** (khối đầu `START_HERE.md`): dịch ngược để **bắt chước bản gốc** — tra reference
> TRƯỚC khi tự suy (scoped unknown thì đừng bịa); **việc thiết kế duy nhất là art**; automated
> regression/reference checks **vẫn bắt buộc** — metrics là gate phát hiện lệch, không phải approval.

Thay vì tranh luận, định nghĩa **4 mức tăng dần**, mỗi mức có **bài kiểm cụ thể**.

### L0 — Chạy được

| | |
|---|---|
| **Nghĩa** | build mở được, vào màn, bắn, chết, qua màn |
| **Kiểm bằng** | máy: chạy 30 phút không crash, không log error |
| **Đạt khi** | 100% màn chơi không exception |
| **Bắt chước đủ?** | ✅ **đủ** — đây là mức AI làm tốt nhất |
| **Chi phí** | thấp |

### L1 — Đúng luật

| | |
|---|---|
| **Nghĩa** | cơ chế hành xử đúng như spec, không chỉ "giống giống" |
| **Kiểm bằng** | máy: **test tự động** đối chiếu từng con số đã có (mức A) |
| **Ví dụ test cụ thể** | wave 0163 spawn **622** spawner · `rate` mặc định **1,0** (16.173 spawner) · `y_spawn` **9,6** (15.485) · vùng chơi **20×25** unit · bán kính va chạm đạn **15** · `border.w` 15 cho **799/800** |
| **Đạt khi** | **100%** test pass |
| **Bắt chước đủ?** | ✅ **đủ cho phần đã có số** — nhưng phải **viết test**, bắt chước không sinh ra test |
| **Chi phí** | trung bình |
| **Còn thiếu (đã biết, không chặn)** | ① ~~wing-cannon nhịp/barrels~~ **ĐÓNG (report 90)**: `shotRate = .12−.0035L` · barrels L0–10 = 3,4,5,5,6,6,7,7,8,8,9 · super(.06,20) — hẹp scope impl1/source10003 (23 impl còn lại) · ② ~~drone bắn nền~~ **ĐÓNG (report 90)**: 12 impl shotRate/turn/charge/speed + ability25 `rate/(2,5×p)`; ~~mapping prefab→sourceID~~ **ĐÓNG (92: bindings 20001..20012 → Drone_Attack1..12)** · ③ D3 thứ tự pha boss (mức C) — dựng theo `BOSS_ANIM_TIMELINE.md` + ghi lựa chọn thiết kế; ④ `rate = 0` (**2.366** dòng) — tự chọn, ghi rõ (`MISSING` §2.4) |

> Đây là mức mà `Spec2Game` đo được **Rule & Mechanism 45,6/100** — tức mức mà AI **hay trượt nhất**
> khi chỉ có đặc tả. Cách chặn: **test viết trước**, không phải review bằng mắt.

### L2 — Đúng số

| | |
|---|---|
| **Nghĩa** | cùng một phát bắn ra **cùng một lượng damage**; cùng một wave ra **cùng nhịp** |
| **Kiểm bằng** | máy: replay 1 wave, so DPS/TTK/HP với bản gốc trong **dung sai khai báo trước** |
| **Đạt khi** | (dung sai do bạn chọn — ví dụ ±5%) |
| **Bắt chước đủ?** | ✅ **đủ** (lần 14, 25/10) — mọi giá trị đã decode + bind xong |
| **Đã có gì** | 6 mảng `Player_Get_Datas` (bind: save/load **id−10001** · combat **impl N→index N−1**, report 81/82) · **576** mảng `Map_Get_Datas` (**11 cấu trúc**, `DIFFICULTY_MODES` §7) · **150 cặp HP enemy** · `StartHpPoint`←dict · `kHp` **không tồn tại** (`DIFFICULTY_MODES` §3–5) · **HP max tàu 2500×(1+,18×points+abi7) + luật 12 drone impl (reports 90–92 — mapping sourceID + turnRate3=1,0 đóng bởi 92)** |
| **Còn thiếu** | chứng minh **DPS runtime** (report 79 — `rate` = interval; peer làm parity tàu 1) + **2** tái đối chiếu `CROSSCHECK` · ~~HP riêng của tàu~~ **ĐÓNG (report 91)**: max = 2500×(1+,18×points+abi7), không bảng theo tàu · `Board_Drones` **ĐÓNG (91)** — còn `Board_Players` (B) · **binding entry** 576 map (unknown, §2.1) · save schema đầy đủ (§2.3) · scope-90: 23 wing impl/mapping sourceID/turnRate3 |
| **Chi phí** | ~~AssetRipper + Ghidra~~ → **không cần tool** — replay + đối chiếu |

> L2 là mức **"bắt chước" đúng nghĩa nhất** — **số đã đủ hôm nay**; sót việc **chứng minh nhịp bắn
> runtime** (việc của nhánh dữ liệu).

### L3 — Không phân biệt được

| | |
|---|---|
| **Nghĩa** | game mới **tái lập trải nghiệm + art của bản gốc 1:1** — chuẩn màu, ánh sáng, khung, nhịp (APK gốc là **chuẩn trải nghiệm đã kiểm nghiệm**; dự án = **học tập thiết kế**) |
| **Kiểm bằng** | **đối chiếu reference — đo được bằng máy, KHÔNG cần người test thật**: metrics `VISUAL_DESIGN` trong dung sai · so ảnh cùng scene · timeline khớp **795** event · audio khớp **15** rules |
| **Đạt khi** | mọi chỉ số khớp reference trong **dung sai khai báo trước** |
| **Bắt chước đủ?** | 🟡 **một phần — đính chính lần 33** (tuyên bố cũ "input đã đủ" là **quá mềm**, không đo đủ trước khi viết): đủ để **vẽ lại từng sprite đã biết** — pack v2 (70) + pixel/geometry/pivot/border ĐÓNG (62/72/75) + font 292 · **chưa đủ cho L3 trọn**: **505 sprite unknown** + 643 passthrough chưa kiểm (`ASSETS` §9.1) · **chưa có bảng sprite→màn/prefab** (UI 55.584 layout chưa join — queue PR12) · rig spine 27 *inferred* · worklist 624 có bucket glyph sai nhãn · metrics **35** ảnh/so ảnh/timeline = **gate chưa chạy**, không phải approval |
| **Chi phí** | sản xuất art + đối chiếu — **không cần playtest** |

> **Đây là đích của dự án — KHÔNG hoãn** (lần 14, 25/10, chủ dự án: *"không cần người test thật vì
> APK gốc đã thiết kế chuẩn trải nghiệm, ta phải copy những trải nghiệm ấy; art cũng thế — chuẩn màu
> sắc, ánh sáng; để học tập thiết kế, sao lại hoãn"*). Bắt đầu ngay khi **L1 chạy được**, làm **song
> song với L2**. Reference dùng để **đo và vẽ lại**; repo spec không lưu asset (pack do peer giữ).
> Định nghĩa blind-A/B cũ chỉ còn giá trị tham khảo — **đã bị thay**.

---

## 3. Bắt chước giải quyết cái gì — bằng số

| Việc | Bắt chước có giúp? | Vì sao |
|---|---|---|
| Biết **cần làm gì** | ✅ **gần hết** | 22.451 entry enemy, 109 prefab, 48 archetype, 420 súng — **đã có danh sách** |
| Biết **con số đúng** | 🟡 **một phần** | hằng số + static **623 record** đã decode (`ia-resolved`); **4.861** SerializeField binary có trong pack v2 — giá trị xin peer |
| **Làm ra** 282 wave × 84 spawner | ❌ **không** | khối lượng, không phải hiểu biết |
| **Vẽ** 2.185 sprite thay thế | ❌ **không** | gu thẩm mỹ |
| **Đo** cảm giác (L3) | ✅ **đo được bằng máy** | metrics + so ảnh + timeline/audio đối reference — blind-A/B đã bị thay (lần 14/21); gate **chưa chạy lần nào** |
| Chọn **bỏ gì, thêm gì** | ❌ **không** | quyết định thiết kế |

> **Cách nói chính xác:** bắt chước biến **"không biết làm gì"** thành **"biết phải làm gì, rất nhiều"**.
> Đó là một bước rất lớn — nhưng nó **không** làm bước "làm" biến mất.

---

## 4. Chỗ tôi đồng ý với bạn, và chỗ tôi phải nói khác

### Đồng ý

- Game này **đơn giản** — so với 3D open world hay realtime PvP, nó **dễ hơn nhiều lần**.
- **Bắt chước là chiến lược đúng** — không phải đạo đức giả; rất nhiều game mobile thành công
  là "cùng thể loại, khác art". Đó là **bình thường** trong ngành.
- Một đội 3 người + AI **có thể** ra sản phẩm **người chơi thấy tương đương**. Đó là mục tiêu thật.

### Nói khác

- **"Hoàn hảo" phải định nghĩa ở mức nào** — L0/L1/L2/L3 ở trên. Không có định nghĩa thì không
  kiểm được, và cái gì không kiểm được thì không biết đã đạt chưa.
- **Đơn giản và nhỏ — cả hai đều đúng ở đây.** 48 archetype + 92 prefab enemy là **bộ từ vựng nhỏ**.
  Khối lượng thật là **11.089 dòng** (**10.782** cấu hình khác nhau), median **28,5 dòng/wave** — không phải 84.
- **Đã resolve xong:** pipeline vòng 3 đọc được **22.451** entry · **109** prefab · **0** `"?"`.
  Trần nội dung enemy là **109 prefab** — không phải 45.659 thiết kế mới.

> `> Kết luận (mức B):` bắt chước đưa bạn tới **L1** nhanh. **L2** cần 2 tool. **L3** cần
> vòng playtest. Ba mức này **không loại trừ nhau** — chúng là **ba khoản chi phí khác nhau**,
> và không khoản nào là "không cần làm".

---

## 4.1 "Không có gì là không thể" — đúng ở đâu, và chữ "dễ" che mất gì

Sau ba lần số co lại (spawner · enemy · sprite), có thể kết luận: **chưa tìm thấy bức tường nào**.
Nhưng "không có gì không thể" là câu về **khả năng**; "quá dễ dàng" là câu về **thời gian**.
Hai câu khác nhau, và cái thứ hai mới là cái quyết định.

### Phân loại phần còn lại — theo **lý do** thiếu, không theo độ khó

| Loại | Nội dung | Vì sao còn thiếu | Cách xử lý | Bản chất |
|---|---|---|---|---|
| **1. Chưa đọc** | ~~4.861 `[SerializeField]` · 957 `static`~~ → SerializeField: **binary trong pack v2** (report 70 — xin peer); static: **623 record** 17 method đã decode | ~~chạy 2 tool~~ → xin pack + đã decode | **ngắn**, không khó |
| **2. Chưa chọn** | dung sai L2 · ngưỡng N cho L3 · bộ archetype nào đưa vào game | chưa ai quyết | quyết định thiết kế | **ngắn** |
| **3. Chưa làm** | **624** hình art (`art-worklist.csv`) · 69 audio · **10.782** cấu hình wave · 1.416 chuỗi | **không nằm trong APK để đọc** — phải tự sinh ra | sản xuất | **dài**, không khó |
| **4. Ngoài sản phẩm** | giá IAP · live-ops · dữ liệu người chơi | không thuộc bản build | quan sát, không trích xuất | **không cần** cho bản clone |

> **Không loại nào là "không thể".** Nhưng loại **3** là loại duy nhất **không rút ngắn bằng
> cách đọc thêm file** — vì nó là **sản xuất**, không phải **khảo sát**.

### Vì sao "dễ" là từ nguy hiểm ở đây

| Việc | Loại | Có rút ngắn được bằng hiểu biết? |
|---|---|---|
| Biết 48 archetype thay vì 1.015 tên | 1 | ✅ rút từ **nhiều tuần** xuống **một buổi** |
| Biết **624** hình thay vì 2.185 sprite (`art-worklist.csv`) | 1 | ✅ rút 3,4× |
| **Vẽ** 624 hình (worklist) | 3 | ❌ **không** — hiểu biết không vẽ hộ |
| **Chạy** 100 vòng playtest | 3 | ❌ không — nhưng AI làm mỗi vòng **rẻ hơn** |
| Biết damage player | 1 | ✅ sau khi chạy Ghidra |

> `> Kết luận (mức B):` hiểu biết đã **gần như miễn phí** — đó là phần bạn đúng, và đúng
> nhiều hơn tôi dự đoán ban đầu. Nhưng thứ còn lại không phải "khó", mà là **"phải làm"**.
> Với một game 2.5D, "phải làm" nghĩa là **624 hình (worklist) + ~11k placement + vài chục vòng test** —
> đó là **lịch**, không phải **rào cản**.

## 4.2 Phạm vi đã chốt — **L1: giống cơ chế, không cần giống số**

> **Quyết định của chủ dự án (ghi lại nguyên văn ý):** bắt chước + sáng tạo đôi chút;
> **không cần** test cho giống bản gốc; **giống cơ chế là đủ**.
>
> Đây là **mục tiêu L1**, và nó **hợp lệ** — không phải nhượng bộ. Nhiều game thành công
> đi đúng con đường này. Mục này ghi lại **cái gì rơi khỏi kế hoạch** khi chọn L1.

### Cái gì rơi khỏi kế hoạch

| Mục | Trước (mục tiêu L3) | **Sau khi chốt L1** | Hệ quả |
|---|---|---|---|
| **L2 — đúng số** | bắt buộc | ✅ **số đã đủ — làm ngay sau L1** | giá trị decode + bind xong; sót chứng minh **DPS runtime** (peer parity tàu 1) + 2 tái đối chiếu + wing còn special paths/named leaves (config 17/24 — 93 · emission 13/22/23/24 — 94; mapping/turnRate3 **ĐÓNG 92**)/`Board_Players`/bind entry map/save schema (`MISSING` §2) |
| **L3 — khớp trải nghiệm + art** | bắt buộc | ✅ **ĐÍCH dự án — KHÔNG hoãn** · 🟡 **input một phần** (đính chính lần 33) | đối chiếu reference đo được (metrics + so ảnh + timeline/audio) — **song song L2** sau khi L1 chạy được, **không cần người test**; còn thiếu: join sprite→màn + 505 unknown + gate chưa chạy (lần 32/33) |
| Giá trị **4.861** `[SerializeField]` | phải có | 🟡 **tuỳ chọn** | dùng làm **tham khảo**, không phải để khớp |
| Giá trị **957** `static` | phải có | 🟡 **tuỳ chọn** | " |
| **45.659** tham chiếu enemy | phải resolve | 🟡 **tuỳ chọn** | danh sách **109 prefab** (đã resolve) đủ để chọn |
| 1.416 chuỗi localization | phải có | 🟡 **có sẵn** | **1.415 key nonempty, lookup first-index** (report 73 peer `4fe0cef8e`) — dùng hoặc viết riêng đều được |
| 170 SKU IAP | phải khớp | ❌ **bỏ** | tự thiết kế shop |
| 282 wave | phải đủ | 🟡 **tự chọn số** | 20–40 wave là đủ cho bản đầu |

### Cái gì **vẫn** phải có — vì L1 cần

Đây là phần **không đọc được ở đâu khác**, và cũng là phần **đã có sẵn trong spec**:

| Cần | Đã có | Nguồn |
|---|---|---|
| Vùng chơi | **20 × 25** unit, `border` 15/−10/10/−15 | `ENEMY_BEHAVIOUR.md` §1 |
| Bán kính va chạm đạn | **15** unit (799/800) | `COMBAT.md` |
| Tốc độ enemy | **0,2–30**, median **5,0**; wave 3,5 · boss 5,0 | `ENEMY_BEHAVIOUR.md` §1 |
| 48 archetype spawn + tham số | bảng đầy đủ (`rate` 1,0 · `y` 9,6 · `spawn_type`) | `ENCOUNTERS.md` §2.4 |
| **109** prefab enemy + HP | **981** dòng HP · **150** cặp id (`enemy_hp_by_id.json`) · 39 boss | `BALANCE.md` §2–5 |
| 420 cấu hình súng + damage | damage 40–1.200, median 400 | `COMBAT.md` §2 |
| 6 dạng đạn + `bltSpeed`/`lifetime` | đầy đủ | `COMBAT.md` §7 |
| Nhịp wave | median **28** placement/wave, max 255 | `ENCOUNTERS.md` §1.3 |
| 9 component/enemy | kiến trúc chuẩn | `ENEMY_BEHAVIOUR.md` §6 |
| Atlas + tỉ lệ màn | 9:16, page ≤ 2048², **624 hình** (`art-worklist.csv`) | `ASSETS.md`, `DONE.md` §1.6 |

> **Không có dòng nào trong bảng trên cần chạy thêm tool.** Toàn bộ đã nằm trong 14 file spec.

### Vậy thứ duy nhất còn lại là gì

| Việc | Có bắt buộc? | Ghi chú |
|---|---|---|
| Dựng khung gameplay theo 9 component + 48 archetype | ✅ **bắt buộc** | AI làm được, spec đủ số |
| Tự chọn **damage/HP player** | ✅ bắt buộc | không cần khớp bản gốc — **tự cân** |
| Tự chọn **số wave** (khuyến nghị 20–40) | ✅ bắt buộc | không cần 282 |
| Vẽ **~641 hình** (hoặc ít hơn nếu giảm phạm vi) | ✅ bắt buộc | **đường găng thật** |
| Viết text riêng + audio riêng | ✅ bắt buộc | |
| Playtest **để tự thấy ổn**, không để khớp bản gốc | ✅ bắt buộc | rẻ hơn nhiều so với L3 |
| Chạy AssetRipper/Ghidra | ❌ **không** | chỉ khi tò mò một thông số cụ thể |

> `> Kết luận (mức B):` chọn L1 làm **rơi khỏi kế hoạch toàn bộ loại 1 và 2** ở §4.1
> (chưa đọc · chưa chọn) — tức **hai tool và mọi tranh luận về dung sai**.
> Phần còn lại là **loại 3: sản xuất**, và quy mô do bạn tự đặt, không do bản gốc áp.
> **L2/L3 không bị bỏ** (sửa 25/10): L2 **làm ngay sau L1** — số đã decode + bind xong.
> **L3 KHÔNG hoãn** (lần 14, 25/10): APK gốc là chuẩn trải nghiệm đã kiểm nghiệm ⇒ nghiệm thu =
> **đối chiếu reference đo được** (không cần blind A/B/playtest); bắt đầu khi L1 chạy được, song song L2.

## 5. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | ~~Giá trị **5.818** field~~ | ~~D~~ → 🟡 | static: **623 record** 17 method (`ia-resolved.json`); SerializeField: binary trong **pack v2** (report 70) — xin peer |
| 2 | ~~45.659 tham chiếu enemy~~ | ~~D~~ → **A** | ✅ **đã resolve** (`ENCOUNTERS.md` §2.6): 22.451 entry · 109 prefab |
| 3 | Ngưỡng N người cho test L3 | **C** | phải tự chọn; chưa ai trong dự án đo |
| 4 | Dung sai cho L2 | **C** | phải tự chọn (đề xuất ±5%, chưa có cơ sở) |
| 5 | Thời gian làm 282 wave | **C** | không đoán ở đây; phụ thuộc công cụ authoring |

> Không có dòng nào trong bảng này là "không thể". Cả 5 dòng đều là **"chưa chọn"** hoặc
> **"chưa chạy"** — hai trạng thái khác nhau, và cả hai đều **đổi được**.
>
> **Sau khi chốt phạm vi L1 (§4.2):** dòng 1, 2 và 4 **không còn là yêu cầu** — chúng chỉ còn
> là thông tin tham khảo. Dòng 3 và 5 vẫn phải chọn, nhưng chọn **theo ý mình**, không theo bản gốc.

---

## 12. Cập nhật 25/10 (lần 3) — đơn vị spawner, và geometry có toạ độ

| Việc | Trước | **Sau (đo lại)** | Bằng chứng |
|---|---|---|---|
| "spawner" là gì | 11.089 (gọi là spawner) | **spawner = 23.757 `Call_Data` object**; 11.089 = **dòng cấu hình** (đã gộp object trùng, mỗi dòng mang `copies`) | `Σ copies` = 23.757 = `class-inventory.csv` → **AQ7** |
| Dòng thật (bỏ mốc wave) | 10.493 | **10.481** (bỏ **608** dòng `StartPoint`/`EndPoint`) | `spawn_type` boss 327 + special 281 = 608 |
| Tổng có đổi khi đồng bộ `622b700e5`? | tưởng "không đổi" | **9 wave + `unknown` đã đổi** (`Σ copies` vẫn 23.757) | `DATA_SYNC.md` §17.1 |
| Sprite có toạ độ chưa | chưa | **2.185** sprite resolve `m_RD` · **40** rect lọt ngoài texture · **144** cần lật/xoay | report 62, `DATA_SYNC.md` §17.3 |
| 340 `unresolved` | 0 ca dùng được trang atlas | **282** ca biết trang thật, **18** gán được (precision ≥ 0,95) | `ASSET_TRIAGE.md` §9.6b (**AT1**) |

> ⚠ Geometry là **join metadata** (`PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`) — **không**
> phải bằng chứng "ảnh đã cắt đúng". 6 chunk `objects-*.jsonl.gz` **chưa kéo** ⇒ chưa tự kiểm `sha256`.

---

## 13. Cập nhật 25/10 (lần 4) — **chạy code**, không chỉ đọc report

Lượt này khác hẳn 3 lượt trước: chép **code của nhánh dữ liệu** vào rồi chạy trên raw đã kéo.

| việc | trước | nay |
|---|---|---|
| Save contract | đọc report 57, 2 key | **chạy** `tools/verify/opening_persistence.py` ⇒ **41 method · 25 check · 8 key family** (claim **OP1**) |
| Test của nhánh dữ liệu | không có | **16 test OK** trong repo này (claim **TS1**) — gồm side effect `StageTarget +1`, `TUTORIAL=6`, 2 store |
| Geometry | report 62: 2.185 sprite | **GE1/GE2/GE3**: 2.185/654/66 · `unresolved` **rỗng** · 144 lật-xoay · 40 `textureRect` vượt page ≤0,9963 px · **1.795** sprite có `source_rect ≠ texture_rect` ⇒ crop theo **`texture_rect`** |
| Sổ kiểm claim | người viết tự khai | **RB1 tự đồng bộ**: `tools/raw-audit.py` ghi lại 4 số vào doc **và** vào verifier ⇒ **151 RAW · 4 DOC · 37 CONST / 192** |
| README 39 dòng | sửa tay hay quên | **RD1** đo lại từng file + `tools/refresh-readme-sizes.py` |

**Số đã sai và đã sửa lượt này** (ghi lại vì cùng loại lỗi đã lặp 4 lần):

| Số cũ | Số đúng | Vì sao |
|---|---|---|
| "11.094 spawner" | **11.089** dòng cấu hình (**23.757** spawner khi ×`copies`) | vẫn là lỗi đơn vị; nay có `WR7` khoá **cả ba** đơn vị: 22.451 `Σ len` · 45.659 quân · 11.089 dòng |
| "Wave_0163 = 622 entry" | **620** | export lại ở `6ababbd31`; 45.659 quân **không đổi** |
| "`raw/ui-audit` chưa kéo" | **đã có** 320/388 `extra-native` + 273 `il2cpp-consts` | câu cũ sai, đã sửa ở `DATA_SYNC` §19.4 |
| "crop theo `source_rect`" | **`texture_rect`** | 1.795/2.185 sprite có hai rect khác nhau |

> Vẫn **chưa** kiểm pixel: 6 chunk nguồn của geometry chưa kéo, nên `status` của file vẫn là
> `PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`. Crop thử 1 page `sactx-*` là việc tiếp theo.
