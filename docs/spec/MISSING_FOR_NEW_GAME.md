# MISSING — còn thiếu gì để **học lại và làm một game mới**

> Viết 25/10 sau khi kéo snapshot **`575113776`**. Mọi con số trong tài liệu này đều có claim trong
> `tools/verify-claims.py` (nhóm **AM**), chạy: `python3 tools/verify-claims.py --only AM`.
>
> **Định nghĩa "thiếu" ở đây** = thiếu **dữ liệu / thông số** để dựng lại một hệ, **không** phải thiếu
> ý tưởng thiết kế. Cái gì dữ liệu không có mà **tự chọn được** thì ghi là *lựa chọn thiết kế*, không
> ghi là thiếu — đúng mức L1 (*giống cơ chế, không cần giống số*).

---

## 0. Cách kiểm

Mỗi hệ trả lời 4 câu, không được bỏ câu nào:

1. **Để làm game mới cần gì?** (cần đúng cái gì, không phải "cần hiểu game")
2. **Đang có gì?** — file + claim, không chép báo cáo.
3. **Thiếu đúng cái gì?** — tên file/địa chỉ, không nói "còn mờ".
4. **Việc kế tiếp** + có cần **thiết bị** không.

---

## 1. Mười ba hệ — trạng thái

| # | Hệ | Đủ để dựng lại? | Đang có (bằng chứng) | Thiếu gì |
|---:|---|---|---|---|
| 1 | **Vòng lặp lõi** (30 s / 1 phiên / 1 tuần) | ✅ **đủ** | `GAMEPLAY.md` §0; 3 vòng lặp viết được thành design doc | — |
| 2 | **Điều khiển + va chạm** | ✅ **đủ** | kéo ngón để lái, nhấc tay đổi tàu; biên **20×25**, radius **15 unit** (`ENEMY_BEHAVIOUR.md`) | — (L1 tự chọn cảm giác) |
| 3 | **Súng / đạn / sát thương** | ✅ **đủ** cho L1 | **458 súng** · damage **40–1.200** (median 400) · **186 loại đạn** · burst 5 tham số (`COMBAT.md`) | **B3**: đường cong damage theo rank — xem §2.2 |
| 4 | **Enemy** | ✅ **đủ** | **109 prefab** (39 boss + 70) · 9 component · 399 đường bay · **150 HP id** (`datas/enemy_hp_by_id.json`) | — (B1 coi như đóng: HP theo **id**, không theo wave) |
| 5 | **Boss** | 🟡 **một phần** | 39 prefab `Boss-*` · **795 event** có mốc thời gian · 268 cặp (prefab, clip) · nhịp **0,17 / 0,33 / 1,0 / 5,0 s** | **D3**: thứ tự pha + điều kiện vào/thoát — có mốc, **chưa có** thứ tự (mức C) |
| 6 | **Wave / spawn** | ✅ **đủ** | **282 wave · 11.089 dòng cấu hình · 23.757 spawner · 22.451 entry** (`H2`, `I3`, `M3`, `AQ7`) | `rate = 0` **chưa** kết luận "spawn cả loạt" — xem §2.4 |
| 7 | **Độ khó 3 chế độ** | ✅ **đủ** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · không nhân số quân | ngưỡng % riêng = tự chọn |
| 8 | **Kinh tế / rơi đồ** | ✅ **đủ** | 3 tầng rơi: **702** vật đặt sẵn (**676 coin / 26 item**) · **246/2.094** slot mang item · **6** loại (`AE1`–`AE3`) | trọng số chọn giữa 6 loại — **tự chọn** |
| 9 | **Meta: tàu / sao / talent / drone** | 🟡 **một phần** | **25 tàu**; `Player_Info` **4 field**: `id` · `Sprite` · `Star` · `Actived` (claim **AM3**) — nhưng damage **có** lookup theo tàu: `GetMainCannonDamage(playerIndex)` đọc **mảng static float** `0x78` theo `playerIndex` (§2.2); `Player_Talent` **23 method** · **13 drone** | **giá trị** mảng damage theo tàu (6 blob rodata); HP riêng của tàu = **chưa biết**, không suy từ field vắng |
| 10 | **UI** | ✅ **cấu trúc** · ✅ **luật thị giác** / ❌ **asset** | **797 màn · 150.131 node · 5.831 nút** (`N2`, `P6`); **55.584** layout file; khung hình **0,4813** · accent **≤10 %** · tương phản **0,45–0,80** (`VISUAL_DESIGN.md`, **AN1**, **AN2**) | asset gốc: **vẽ mới**; luật thì **đã có số** |
| 11 | **Âm thanh** | 🟡 **có dữ liệu, chưa có luật phát** | **69 clip / 571,5 s**, trong đó **5 vòng nhạc > 60 s** (`docs/assets/audio-index.csv`) | **ai phát cái gì, lúc nào** (`AudioSource`/`AudioManager` chưa bóc) |
| 12 | **Save / load + live-ops** | 🟡 **một phần** | key đã đọc: **`StarCount`** · **`StarStageMaster{stageIndex}_{modeIndex}`** (default 0) qua `PlayerPreferences.SetInt → PlayerPrefs.SetInt`; model `savedStars/result` (report 57); **170 IAP** | **schema đầy đủ** (mọi khoá/kiểu/migrate) + **chưa** chứng minh flush đĩa — xem §2.3 |
| 13 | **Tech / build** | 🟡 **một phần** | Unity **2022.3.x** (`UNITY_RULES.md`) · Spine · DOTween · 3 loader trong repo này | plugin list đầy đủ + cấu hình build (lấy từ `dump.cs`/manifest, không cần thiết bị) |

**Đọc bảng này theo đúng nghĩa:** 8 hệ **đủ** để dựng lại, **5 hệ một phần**, **0 hệ thiếu hoàn toàn** (save/load đã có key, chưa đủ schema — §2.3).

---

## 2. Bốn chỗ **cần biết trước** — và địa chỉ để mở

A6 và B3 là **dữ liệu chưa dump**; save đã có **một phần**; `rate = 0` là **giới hạn suy luận**.
Tự chọn ở A6/B3 thì game mới **lệch số**; tự chọn ở `rate = 0` thì lệch **nhịp**, nhưng được phép nếu ghi rõ.

### 2.1 A6 — một **stage** gồm mấy wave: **3/576 entry đã resolve**, phần còn lại chưa dump

- **Kích thước export:** `Map_Get_Datas..cctor` **100.896 B · `ends_clean: true`** · **4.020** const · **576** `init_array` (claim **AM1**) — **đầy đủ, không bị cắt**. `GetListWaves` **1.112 B**, trả `int[]`.
- **ĐÃ RESOLVE (mức A, phạm vi hẹp)** (`CM1`): **3 entry** = `[25, 9010]` · `[164]` · `[113, 5]` · **13** check;
  `Map_Get_Datas..cctor` dựng `listMapDatas`; **3 entry đầu** đọc được
  **literal trong asm**: entry0 `[25, 9010]` · entry1 `[164]` · entry2 `[113, 5]` — ứng với **stage nội bộ
  0/1/2** của **ChapterCurrent = 0, GameMode = 0, nonbranch** (không áp cho branch/test/mode khác).
  Consumer đã nối tới cuối: `MapController.Start → setup.get_stageIndex → Map_Get_Datas.GetListWaves(index)`,
  **không** +1/−1 giữa getter và tham số. Nguồn: report **52** + `raw/ui-audit/scene-map-flow.json.gz`
  (**13** check) + `raw/il2cpp-consts/Map_Get_Datas.asm.txt`.
- **CHƯA RESOLVE:** **573** entry còn lại (tổng **576**). `datas/maps.json` là **bảng dẫn xuất** —
  **không** phải nguồn độc lập; đừng dùng nó để "xác nhận" chính nó.
- **Địa chỉ để dump tiếp:** mỗi `init_array` có địa chỉ nguồn (`a:`), ví dụ `0x2bd4838` (len **36**),
  `0x2bd5488` (len **36**), `0x2bd58a8` (len **3**). Phân bố độ dài: **3 → 320 mảng**, **7 → 104**,
  **36 → 63**, 4 → 21, 5 → 12, 6 → 9.
- **Vì sao vẫn tính là chặn A5:** 250 map ↔ 282 wave; biết 3 stage **không** suy ra độ dài phiên. Nhưng
  **không còn** là "phải bóc lại APK từ đầu" — chỉ còn **đọc 573 blob** (vài KB).
- **Nếu chỉ cần L1:** tự chọn độ dài map là **hợp lệ**, miễn ghi rõ là **lựa chọn thiết kế**.

### 2.2 B3 — đường cong damage của **tàu** theo rank

- **Có gì:** `Player_Get_Datas..cctor` **2.492 B** · **6** `init_array` · mảng dài nhất **24** (claim **AM2**).
  Bốn mảng đó ứng với `StartMainCannonDamages` (`0x78`) · `StartMainCannonRate` (`0x80`) ·
  `StartWingCannonDamages` (`0x88`) — đọc offset từ `dump.cs.gz`.
- **Thiếu gì:** bytes của **4 mảng × 24 float** + 2 mảng × 3, tại `0x2bd5a40`, `0x2bd4d28`, `0x2bd5af8`,
  `0x2bd45c0`.
- **Sửa 25/10 (review peer N2):** **KHÔNG** được suy "tàu không có damage riêng" từ việc `Player_Info` chỉ
  có 4 field (claim **AM3**). Asm `Player_Get_Datas.GetMainCannonDamage(int playerIndex)` đọc **mảng static
  float** tại offset **`0x78`** và **index theo `playerIndex`**: `ldr x8,[x8,#0x78]` → so `w9, w19` →
  `ldr s8,[x8, w19, sxtw #2 + 0x20]` (`14e3a78..14e3a90`). Rank/upgrade vào phần tính **sau** (`0x14e3c40`),
  **không** xoá lookup theo tàu ⇒ **damage phụ thuộc tàu là có thật**; chỉ **giá trị** là chưa biết.
- **Bằng chứng asm (`CM2`):** `0x78` + `sxtw #2` + index `w19` — kiểm bằng máy trên `Player_Get_Datas.asm.txt`.
- **Đã có thêm (nhưng KHÁC lớp):** `raw/player-loadout/array-blobs.json.gz` — **5 blob** · **49 int** · **5/5 sha256 OK** (claim **CM5**). Đây là **int** của `Player_Saved_Datas` (giá craft/unlock), **không**
  phải 4 mảng **float** damage của `Player_Get_Datas`; field binding cũng chưa chốt
  (`PROVISIONAL_METADATA_ARRAY_BLOBS_NOT_ALL_FIELD_BINDINGS`). ⇒ **B3 vẫn mở.**
- **Còn thiếu:** giá trị **6 mảng rodata** (24 float × 4 + 2 mảng × 3) ⇒ DPS/TTK tuyệt đối vẫn chưa tính.
  HP riêng của tàu: **chưa có bằng chứng** theo cả hai chiều ⇒ giữ **D**, không kết luận.
- **Việc kế tiếp:** cùng một lần dump rodata với §2.1 (hai class, 6 blob).
- **Sau khi có:** `TTK` từ "tương đối" lên **số thật**; `COMBAT.md` §6 hết câu "chưa có số tuyệt đối".

### 2.4 `rate = 0` **không** phải "spawn cả loạt cùng frame"

- `rate` là field thật (`Call_Data.rate`), nhưng **cách dùng khác nhau theo loại spawner**: nhánh
  Path/Waypoints đưa giá trị vào `WaitForSeconds`, nhánh khác dùng trực tiếp (report **53**). `WaitForSeconds(0)`
  **không** chứng minh mọi enemy sinh trong cùng một frame — nó chỉ nói "không chờ thêm" trong nhánh đó.
- Vì vậy: **68 %** dòng là `point_range` và `rate` trung vị **1,0 s** là **mô tả phân bố**, không phải
  "luật spawn của game". Muốn mô phỏng khác thì ghi **lựa chọn thiết kế**.
- Cái **đo được** và nên giữ: mỗi wave có **1 `StartPoint` + 1 `EndPoint`** (tổng **608** dòng mốc) và
  danh sách enemy nằm trong `listPrefabEnemies` — đó là **cấu trúc**, không phải nhịp.

### 2.3 Save / load — **8 key family đã có contract**, chưa phải schema đầy đủ

Từ report **65** + `datas/opening_persistence.json` (raw: `raw/persistence/opening-contracts.json.gz`,
**41** method · **25** check):

| Key / format | Owner → kiểu | Cache | Khi **đọc** có gì ngoài đọc |
|---|---|---|---|
| `TUTORIAL` | `GP_Tutorials.IndexTutorial` → int | +0x10, sentinel −1 | đọc `StageTarget`; nếu target ≥ 2 và tutorial = 0 thì ghi **6** |
| `TUT_TOUCH_SKILL` | `GP_Tutorials.IsTutTouchSkillDone` → bool | — | trả `stored == 1` (không phải `!= 0`) |
| `StageTarget` | `Stage_Datas.StageTarget` → int | +0x3C, sentinel −1 | **tăng 1 mỗi lần đọc** khi `target < ZoneUnlocked*10`, rồi ghi lại |
| `ZoneUnlocked` | `Stage_Datas.ZoneUnlocked` → int | +0x40, sentinel −1 | setter ghi cache + prefs, **không** tự clamp |
| `StarStageMaster{stage}_{mode}` | `Stage_Datas.GetStarStageMaster` → int | — | saved star count, **không** phải kills |
| `StarCount` | `GameDatas.StarCount` → int | +0x4C, sentinel −1 | gọi Unity `PlayerPrefs` trực tiếp; tổng sao |
| `DroneUsed{slot}` | `Drone_Saved_Datas.GetDroneUsed` → int | — | giá trị âm → ghi 0 rồi đọc lại |
| `DroneUnlocked{drone}` | `Drone_Saved_Datas.IsDroneUnlocked` → bool | — | ID 20001 có đường tự ghi 1; ID ≥ 20002 đòi `stored == 1` |

**8 key family** · **2 store** · **7 limitation** (claim **CM4**). Hai store: `Unity.PlayerPrefs` (typed wrapper
tail-call) và `PlayerPreferences.dictionary` → file `persistentDataPath + /Prefs`.

> ⚠ **Getter có side effect.** `get_StageTarget` **tăng 1** rồi lưu lại; `get_IndexTutorial` tự sửa
> `TUTORIAL = 6`. Nghĩa là **HUD/debug/serializer gọi getter nhiều lần có thể đổi dữ liệu**. Nếu game mới
> chọn getter thuần + migrate rõ ràng thì **ghi là quyết định thiết kế**, đừng giả là phục dựng nguyên hàm.


#### 2.3b Loadout tàu (report **66**) — thêm **15 key family · 33 method · 43 check**

Raw: `raw/player-loadout/contracts.json.gz` (38 KB, **sha256 kiểm tại chỗ**) + `datas/player_loadout_persistence.json`.
Đây là **cùng một kiểu lưu** (int32 qua typed `PlayerPreferences` → `Unity.PlayerPrefs`), **khác** dictionary
`persistentDataPath/Prefs` của report 65. Giá trị default dưới đây là **đọc từ contract**, không suy:

| key | kiểu | default | bẫy khi đọc/ghi |
|---|---|---:|---|
| `PlayerUsed{slot}` | int32 | slot0 **10001**, slot khác **10002** | đọc **≤ 0** thì ghi lại 10001/10002 rồi đọc tiếp |
| `PlayerUnlocked{ship}` | int32 | 0 | `ship < 10003` ⇒ **true** (không phải validate roster); setter gọi analytics **trước** khi ghi |
| `PLAYER_RANK{ship}` | int32 | **2** | base ≤ 1 ⇒ **ghi 2** trước khi xét trial; `trial==1` trả rank trial default 0 |
| `PLAYER_LEVEL{ship}` | int32 | 0 | chỉ đọc level trial khi `TRIAL_ID_{ship}==1`; **không clamp** |
| `TRIAL_ID/RANK/LEVEL_{ship}` | int32 | 0 | cờ trial đúng bằng **1**; vòng đời writer/expiry **chưa** bóc |
| `PLAYER_CARDS{ship}` | int32 | 0 | nhánh Test lấy default từ CheatGameInfo |
| `PLAYER_DEFAULT_SKIN{ship}` | int32 | **−1** | `−1` là **hợp lệ**: `GP_Loader` dùng nó để chọn skin mặc định |
| `PlayerStatPoints{stat}` · `PlayerStatLevel{stat}` · `TECHLAB_LV` | int32 | 0 | không clamp trong các thân hàm đã đọc |
| `PLAYER_DEVICE_{ship}_{slot}` | int32 | **−1** | **4 slot**; mode 4 ở scene `Game` trả mảng mới `[-1,-1,-1,-1]` |
| `FIRST_INSTALL_DEVICE` | int32 | 0 | cờ "dùng lần đầu": sau 4 lần ghi, nếu có giá trị ≠ −1 và cờ cũ… |
| `TALENT_SELECTED` | int32 | **−1** | là **lựa chọn đã lưu**, **không** phải level talent |

**Bảng rank (6 bảng, đọc từ `cctor`):** `MaxLevelPerRanks` **[10, 20, 30, 60, 120, 250, 500]** ·
`CardUpgrades` **[0, 20, 50, 80, 250, 500, 800]** · `StartRanks` **24 × 2** · `MAX_RANK_INDEX` **6**.
Các bảng này **không** tự áp cap — limit nằm ở wrapper gameplay, nên đừng dùng bảng làm luật cứng.

**8 limitation ghi nguyên trong file** (đừng đọc là đã xong): schema_version là version **của pack**, không
phải save version của APK · chỉ nhánh normal non-Test/non-Premium · không có first-install runtime/atomicity/
migration/cloud · trial writer + expiry chưa bóc (**không** suy trial từ trạng thái unlock) · bảng rank không
phải luật · không suy roster từ so sánh ID · cache gameplay chỉ một phần · consumer tech/talent là **ví dụ**,
không phủ toàn bộ công thức chiến đấu.

**Còn thiếu (đừng gọi là đủ):** IAP/cloud/Premium chưa bóc; chưa có migrate; **chưa** chứng minh flush đĩa
(status trong file: `PROVISIONAL_STATIC_PARTIAL_SAVE_CONTRACT_NOT_FULL_SCHEMA`).

---

## 3. Cái **không phải** thiếu (đừng đi tìm nữa)

| Thứ | Vì sao không thiếu |
|---|---|
| **feel** (hit stop · aim assist · input latency) | 0 site `timeScale` / 0 method `aim` trên **139** file asm (**AF2**, **AF3**) = **chưa thấy**, **không** phải "không tồn tại" (139 file là **mẫu**, không phải whole-build closure). Cái **đo được**: hit flash **0,5 / 0,05 s** (`J9`), rung **241** prefab (`AF1`). Game mới muốn có feel thì **được** — ghi là lựa chọn thiết kế |
| **art, font, atlas (bản gốc)** | L1 **vẽ mới**. Cái **không** bỏ là **luật thị giác**: khung hình · ba chế độ sáng · ngân sách accent · vignette khung thưởng · mật độ chi tiết — đã đo và ghi ở `VISUAL_DESIGN.md` |
| **số cân bằng cụ thể** (giá, tốc độ, mật độ) | L1 cho phép tự chọn; cái phải giữ là **cơ chế** (3 chế độ, không nhân quân, rơi đồ 3 tầng) |
| **thứ tự pha boss (D3)** | Có **795 event + mốc thời gian**; thứ tự là **lựa chọn thiết kế**, dữ liệu chỉ cần đủ để biết "mỗi pha có đòn gì" |
| **13 class "chưa phân loại" trong ASSET_TRIAGE** | vẫn còn **1.554** `unclassified` / 2.197 — nhưng đây là việc **phân loại ảnh**, không chặn dựng game (L1 vẽ mới) |

---

## 4. Trả lời "đủ chưa" — theo L1 / L2 / L3

- **L1 (làm game **giống cơ chế**, art mới, số tự chọn): ĐỦ.** 8/13 hệ đủ, **5** hệ một phần nhưng phần
  thiếu đều **không chặn** (D3 = chọn thiết kế; audio = tự chọn; talent = tự chọn giá).
- **L2 (giống **số** đến mức chơi thấy tương đương): CHƯA.** Cần **6 blob** rodata của `Player_Get_Datas`
  + **573** entry `Map_Get_Datas` còn lại (§2.1 + §2.2).
  Ngoài ra cần playback thật để so cảm giác — việc này cần **thiết bị**.
- **L3 (tái lập **1:1 asset** gốc): BỎ** — art pack, font, shader, physics không tái lập từ APK.
  **Không** có nghĩa là bỏ "thiết kế cho đẹp": phần đó là `VISUAL_DESIGN.md` (khung hình **0,4813**,
  tương phản **0,45–0,80**, accent **≤10 %** gameplay / **~47 %** khung thưởng, chi tiết **13–22**,
  juice **0,05 s** + **0,10 · 20 frame**) và **kiểm được bằng máy**.

---

## 5. Nếu chỉ làm được **một** việc tiếp theo

Xin nhánh dữ liệu **một lần dump rodata**: **6 blob** của `Player_Get_Datas` + **573 blob còn lại** của
`Map_Get_Datas` (3/576 entry đã đọc literal; tất cả địa chỉ đã có trong `init_array.a`):

| được gì | mở khoá |
|---|---|
| 4 mảng 24 float (damage theo **playerIndex**) | **B3** đóng → TTK tuyệt đối, cân bằng súng theo rank/tàu |
| 573 mảng int | **A6** đóng → **A5** đóng → biết một phiên dài bao lâu |

Đó là **hai** trong **bốn** câu ❌ cuối cùng của `DESIGN_QUESTIONS.md` (48 câu: **29 ✅ · 15 ⚠ · 4 ❌**,
claim **S2**), và cả hai đều **không cần thiết bị**.

---

## 6. Đã có, không còn thiếu: **gate 3 stage mở đầu + khuôn victory chung** (report 64)

Ba stage mở đầu **khác nhau ở tutorial**, **không** phải ba hệ thống victory riêng — đã đọc ra predicate
và luồng chung (mức **A** cho lời gọi, **B** cho việc "cùng khuôn"):

| Stage | Predicate trong raw | Tutorial |
|---|---|---|
| 1 | `stageIndex == 0 && IndexTutorial == 0` (`1327e90`) | `TutMoveFingers`, `TutTransform` (delay đầu **9 s**) |
| 2 | `stageIndex == 1 && IndexTutorial == 1` (`1327f08`) | `TutDrones` + pause/resume |
| 3 | `stageIndex == 2 && !IsTutTouchSkillDone()` (`1327f8c`) | nhánh talent/touch-skill — **không** gate `IndexTutorial == 2` |

Khuôn chung: `GP_Manager.<Start>b__11_7 → GP_Endgame.StartCheckEndgame` → coroutine `_CheckEndgame_d__4`
(gate hoàn tất địch/wave **và** trạng thái `Playing`; **đủ kill giữa wave không tự kết thúc**) →
`Board_Endgame.GetMissionCompleted` → `OpenBoardVictory` (nhận **cả** bool false; health = 0 ép **false**) →
`Board_Endgame.Init` → `SetMissions` → sao/save.

> **Ranh giới:** đây là **direct-call trên 3 thân core đã đọc**, không phải chứng minh vắng mặt trên toàn
> chương trình. Nguồn: report 64 + `raw/endgame-missions/shared-stage-victory.json.gz` (**21** method ·
> **18** check, claim **CM3**). **Không** cần BB pool-history hay playthrough ít kill để kết luận cấu trúc này.
