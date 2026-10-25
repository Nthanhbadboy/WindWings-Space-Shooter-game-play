# MISSING — còn thiếu gì để **học lại và làm một game mới**

> Viết 25/10 sau khi kéo snapshot **`575113776`**. Mọi con số trong tài liệu này đều có claim trong
> `tools/verify-claims.py` (nhóm **AM**), chạy: `python3 tools/verify-claims.py --only AM`.
>
> **Định nghĩa "thiếu" ở đây** = thiếu **dữ liệu / thông số** để dựng lại một hệ, **không** phải thiếu
> ý tưởng thiết kế. Cái gì dữ liệu không có mà **tự chọn được** thì ghi là *lựa chọn thiết kế*, không
> ghi là thiếu — đúng mức L1 (*giống cơ chế, không cần giống số*).
>
> **Mục đích dịch ngược** (khối đầu `START_HERE.md`): đủ thứ để **bắt chước bản gốc** — tra reference
> trước khi tự suy; chỗ ghi scoped unknown thì không bịa; phần "thiết kế" còn lại chỉ là **art**
> (vẽ lại), nghiệm thu bằng automated reference checks.

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
| 4 | **Enemy** | ✅ **đủ** | **109 prefab** (39 boss + 70) · 9 component · 399 đường bay *(đo từ bản 800-cũ — CSV hiện hành 981 dòng, chưa có cột path để đếm lại)* · **150 HP id** (`datas/enemy_hp_by_id.json`) | — (B1 coi như đóng: HP theo **id**, không theo wave) |
| 5 | **Boss** | 🟡 **một phần** | 39 prefab `Boss-*` · **795 event** có mốc thời gian · 268 cặp (prefab, clip) · nhịp **0,17 / 0,33 / 1,0 / 5,0 s** | **D3**: thứ tự pha + điều kiện vào/thoát — có mốc, **chưa có** thứ tự (mức C) |
| 6 | **Wave / spawn** | ✅ **đủ** | **282 wave · 11.089 dòng cấu hình · 23.757 spawner · 22.451 entry** (`H2`, `I3`, `M3`, `AQ7`) | `rate = 0` **chưa** kết luận "spawn cả loạt" — xem §2.4 |
| 7 | **Độ khó 3 chế độ** | ✅ **đủ** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · không nhân số quân | ngưỡng % riêng = tự chọn |
| 8 | **Kinh tế / rơi đồ** | ✅ **đủ** | 3 tầng rơi: **702** vật đặt sẵn (**676 coin / 26 item**) · **246/2.094** slot mang item · **6** loại (`AE1`–`AE3`) · chuỗi nổ vàng **đã nối (report 88)**: DropGold `lost > iPlus×10` → event6 → budget **28 → 8 object** (chia 5) → pool | trọng số chọn giữa 6 loại — **tự chọn**; tiền **nhặt được** (`OnCollectCoin1/2`) — peer tiếp pickup branch |
| 9 | **Meta: tàu / sao / talent / drone** | 🟡 **một phần** | **25 tàu**; `Player_Info` **4 field**: `id` · `Sprite` · `Star` · `Actived` (claim **AM3**) — nhưng damage **có** lookup theo tàu: `GetMainCannonDamage(playerIndex)` đọc **mảng static float** `0x78` theo `playerIndex` (§2.2); `Player_Talent` **23 method** · **13 drone** | 6 mảng damage/rate/cost **đã decode** (§2.2); **bind combat ĐÃ SỬA (report 81/82)**: impl N → index N−1 (tàu 10001→2 · 10003→0; id−10001 chỉ đúng save/load) ⇒ TTK **ước lượng** theo từng tàu. Còn: **HP riêng của tàu** (chưa biết, **khác** HP enemy đã có); DPS **runtime** (cần health/shield gates) — luật nhịp đã đủ **24/24** impl (report 83) |
| 10 | **UI** | ✅ **cấu trúc** · ✅ **luật thị giác** / ❌ **asset** | **797 màn · 150.131 node · 5.831 nút** (`N2`, `P6`); **55.584** layout file; khung hình **0,4813** · accent **≤10 %** · tương phản **0,45–0,80** (`VISUAL_DESIGN.md`, **AN1**, **AN2**) | asset gốc: **vẽ mới**; luật thì **đã có số** |
| 11 | **Âm thanh** | 🟡 **có dữ liệu + 15 luật tĩnh** | **69 clip / 571,5 s** (`audio-index.csv`) · `datas/audio_rules.json`: **15 rules** (mute/volume/pause/oneshot/music…) · registry **92** id · enum **118** (report 67; `DATA_SYNC` §21.1) | **đối chiếu nghe + trigger lúc chơi** — tĩnh hiện PROVISIONAL, cần 1 lần chạy để nâng mức |
| 12 | **Save / load + live-ops** | 🟡 **một phần** | key đã đọc: **`StarCount`** · **`StarStageMaster{stageIndex}_{modeIndex}`** (default 0) qua `PlayerPreferences.SetInt → PlayerPrefs.SetInt`; model `savedStars/result` (report 57); **170 IAP** | **schema đầy đủ** (mọi khoá/kiểu/migrate) + **chưa** chứng minh flush đĩa — xem §2.3 |
| 13 | **Tech / build** | 🟡 **một phần** | Unity **2022.3.x** (`UNITY_RULES.md`) · Spine · DOTween · 3 loader trong repo này | plugin list đầy đủ + cấu hình build (lấy từ `dump.cs`/manifest, không cần thiết bị) |

**Đọc bảng này theo đúng nghĩa:** 8 hệ **đủ** để dựng lại, **5 hệ một phần**, **0 hệ thiếu hoàn toàn** (save/load đã có key, chưa đủ schema — §2.3).

---

## 2. Bốn chỗ **cần biết trước** — và địa chỉ để mở

A6 và B3 **không còn là "dữ liệu chưa dump"** (câu cũ đã sai từ 25/10): raw **đã có** trong
`ia-resolved.json` (576 mảng Map · 6 mảng Player). **Bind chính ĐÃ XONG** (sửa 25/10, đừng lặp lại
TODO cũ): ① index ↔ tàu = **id − 10001 — hẹp scope 25/10 (report 81/82)**: đúng cho save/load (`0x14e2ce4`); combat = impl N → index N−1 (tàu 10001→2 · 10002→1 · 10003→0 · 10004+→id−10001); ② cấu trúc bảng Map = **11 cấu trúc,
đã phân loại 614 mảng** — 320×len3 ↔ 3 chế độ · 118×len2 = `stage → boss` · 104×len7 ↔ 7 `PlayMode`
(`DIFFICULTY_MODES` §7). **Sửa 25/10 (lần 2): 4 mục "còn thiếu" trước đây đều đã có theo dạng khác** —
`kHp[mode]` **không tồn tại** như hệ số (chế độ đổi composition + thưởng, `DIFFICULTY_MODES` §3–5);
`missionKillPercent` là **một** `float[3]` theo mission index, đủ **3/3**; `StartHpPoint` ← dict
**đã bind theo id** (dict là nguồn, `Init` chỉ là plumbing); `rate` = **giây delay theo nhánh**, đã
chốt (A, report 53). Vẫn còn: save **một phần**; `rate = 0` là giới hạn suy luận.
Tự chọn ở A6/B3 thì game mới **lệch số**; tự chọn ở `rate = 0` thì lệch **nhịp**, nhưng được phép nếu ghi rõ.

### 2.1 A6 — stage ↔ wave: **dữ liệu ĐÃ CÓ trong repo**, thiếu phần *bind*, không thiếu blob

> Sửa 25/10 sau khi đối chiếu: mục này từng ghi *"573 blob còn lại chưa dump"* và **xin nhánh dữ liệu dump
> thêm**. Sai. Toạ độ + hex đã nằm trong `reverse-engineering/il2cpp/ia-resolved.json` **của chính repo này**
> (và của cả hai nhánh), `length_valid` **576/576**.

- **Số thật:** `Map_Get_Datas..cctor` **100.896 B · `ends_clean: true`** · **4.020** const · **576** `init_array` (claim **AM1**), đã resolve **576/576** (claim **IA1**).
- **Nội dung đọc được:** **576 mảng `int`** · **5.154** giá trị · **253** wave id khác nhau · **0** giá trị không có trong `datas/waves.json` (claim **IA3**).
  ⇒ **Danh sách wave của bảng map đã đọc được**, không phải chờ dump.
- **Không phải “573 = 576 − 3”.** Ba entry mở đầu (`CM1`): **3 entry** = `[25, 9010]` · `[164]` · `[113, 5]` · **13** check; chúng được dựng bằng
  **literal store**, **không** nằm trong 576 `InitializeArray` ⇒ trừ đi là **sai đơn vị**. Và **576 cũng
  không phải 576 stage**: đó là số *mảng*, chưa bind sang (chapter, stage, mode).
- **Kiểm bằng asm (`CM2`):** `0x78` + `sxtw #2` + index `w19` — `GetMainCannonDamage` đọc mảng theo `playerIndex`.
- **Phân bố độ dài** (số mảng): `3 → 320` · `7 → 104` · `36 → 63` · `4 → 21` · `5 → 12` · `6 → 9` ·
  `20 → 5` · `24 → 2` · dài nhất **69**.
- **Việc còn lại là *bind*, không phải *dump*:** entry thứ *i* ↔ (chapter, stage, mode). Consumer đã nối tới
  cuối (`MapController.Start → setup.get_stageIndex → Map_Get_Datas.GetListWaves(index)`), nhưng **thứ tự nạp
  `listMapDatas` chưa được chứng minh** ⇒ ghi **unknown**, đừng gán theo trực giác.
- `datas/maps.json` (**250** map) là **bảng dẫn xuất khác nguồn** — không dùng nó để "xác nhận" 576.
- **Nếu chỉ cần L1:** chọn số map × độ dài map là **hợp lệ**, miễn ghi rõ là **lựa chọn thiết kế**.

### 2.2 B3 — damage tàu: **giá trị đã có**, chỉ còn **HP riêng của tàu** là chưa

> **Phân biệt (đừng nhầm với B3 ở `OPEN_ISSUES`):** "HP" ở mục này là **HP của tàu người chơi**
> (`Player_Health`), vẫn mức **D**. **HP enemy** thì **đã có** — **150 cặp `id → HP`** trong
> `datas/enemy_hp_by_id.json` (§3, claim **WRH2**).

> Sửa 25/10: mục này từng ghi *"4 mảng × 24 float"* và *"thiếu 6 blob rodata"*. Cả hai đều sai.

**Đã decode 6 mảng** (`Player_Get_Datas..cctor` **2.492 B** · **6** `init_array` · mảng dài nhất **24**, claim **AM2**)
từ hex trong `ia-resolved.json` — **theo kiểu của field**, không
đọc cột `ints` (cột đó là bit pattern; float phải unpack `<f`):

| field | kiểu | len | offset | giá trị (index 0…) |
|---|---|---:|---|---|
| `PlayerCosts` | **int[24]** | 24 | `0x38` | `0, 0, 1050, 3150, −1, 3850, 4550, 2450 …` (**8** phần tử `−1` = không bán) |
| `StartMainCannonDamages` | **float[24]** | 24 | `0x78` | `4500, 220, 2680, 8000, 710, 1650 …` |
| `StartMainCannonRate` | **float[24]** | 24 | `0x80` | `4,8 … 12,0` |
| `StartWingCannonDamages` | **float[24]** | 24 | `0x88` | `218, 75, 186, 118 … 2800` |
| `shipCloneDamage` | **float[3]** | 3 | `0x1C8` | `1,35 · 1,6 · 1,86` |
| `PercentToCompleteMissions222` | **float[3]** | 3 | `0x308` | `0,2 · 0,6 · 0,98` |

- **Bind đã kiểm bằng asm** (claim **IA2**): ngay sau mỗi `InitializeArray` là store đúng offset
  `0x38 / 0x78 / 0x80 / 0x88 / 0x1C8 / 0x308` (`0x14e5b48`, `0x14e5e9c`, `0x14e5ec4`, `0x14e5f18`,
  `0x14e60c4`, `0x14e6244`), và `mov w1,#0x18` (=24) / `#3` là độ dài mảng.
- **~~DPS suy ra~~ → ĐỔI CÁCH GIAO (25/10 theo report 79 peer `549a7b5b7c`):** `damages[i] × rate[i]`
  (index 0 → **21.600**; min **456** · max **46.400**) chỉ là **tích proxy**. Tàu 1 dùng `rate` làm
  **interval đặt hạn bắn**: deadline `@0x10c = Time.time + rate @0xa8` (`MainCannonShoot 0x147a920`) —
  **reports 80–83 peer (`23b1ceec31`) đã nối tiếp:** **24/24 implementation** trace vào deadline
  scheduler (48 read site, report 83); phát phụ = **nhóm** (N extra ⇒ N+1 entry, dual deadline
  `@0x118/@0x10c`, không catch-up — report 80); modifier percent theo `GetTechStatLevel(1)`
  (tier **0/3/5/8/10/12 %** — report 82 §2); demo override 3,0/4,0; crit `random ≤ critPercent`
  ⇒ **×2** trong callback. DPS runtime **vẫn chưa chứng minh** (cần health/shield gates) nhưng
  **luật đã đủ để implement** (report 80 §4).
- **Đã có file dẫn xuất:** `datas/player_start_stats.json` (6 mảng + cột `main_cannon_dps` + cờ purchasable).
- **Khác lớp (đừng gộp):** `raw/player-loadout/array-blobs.json.gz` — **5 blob** · **49 int** · **5/5 sha256 OK** (claim **CM5**) là **int** của `Player_Saved_Datas` (giá craft/unlock), **không** phải mảng float damage ở trên.
- **Bind index↔tàu — ĐÃ HẸP SCOPE (sửa 25/10 theo report 81/82 peer):** ~~id − 10001 cho mọi consumer~~
  → **chỉ đúng ở consumer save/load** (`0x14e2ce4`, `CROSS_BRANCH` T4 — giữ nguyên scope đó).
  **Combat**: impl `Player_Attack_N` đọc mảng index **N−1** (CFG **72/72** call — 24 rate + 24 damage +
  24 wing, report 82 §1); source tàu: impl1→**10003** · impl2→10002 · impl3→**10001** · impl4–24→
  10004–10024 ⇒ tàu **10001 → index 2** (proxy **12.864**), tàu **10003 → index 0** (proxy **21.600**).
  Hợp đồng: `datas/combat_chain_contract.json.gz` + `datas/combat_argument_audit.json` (peer).
- **Vẫn chưa:** (1) **HP riêng của tàu** — chưa có bằng chứng theo cả hai chiều ⇒ giữ **D**.
  (2) **rate player ĐÃ ĐÀO (25/10, report 79 peer):** tàu 1 dùng `StartMainCannonRate` làm **interval**
  đặt hạn bắn tiếp — không phải shot/giây. ⚠ **Đính chính:** report **53** (từng dùng để đóng mục này)
  là **delay spawn** `Call_Data.rate` — **khác consumer/field**; tên `rate` giống nhau không nối được
  hai consumer. (3) **phát phụ + nhiều nòng** chưa nối — giao nhánh dữ liệu (parity tàu 1 trước).
- **Việc kế tiếp:** ~~bảng TTK theo tích damage×rate~~ **bỏ — sai đơn vị** (damage·s, review peer).
  Hai đường: **newdesign** (HP thật + DPS giả định) hoặc **measured** — peer đã dịch receivers
  (report 85) và đang nối producer/serialized + extra-life (report 86); replay đo khi xong.

### 2.4 `rate = 0` **không** phải "spawn cả loạt cùng frame"

- `rate` là field thật (`Call_Data.rate`), nhưng **cách dùng khác nhau theo loại spawner**: nhánh
  Path/Waypoints đưa giá trị vào `WaitForSeconds`, nhánh khác dùng trực tiếp (report **53**). `WaitForSeconds(0)`
  **không** chứng minh mọi enemy sinh trong cùng một frame — nó chỉ nói "không chờ thêm" trong nhánh đó.
- Vì vậy: **68 %** dòng là `point_range` và `rate` trung vị **1,0 s** là **mô tả phân bố**, không phải
  "luật spawn của game". Muốn mô phỏng khác thì ghi **lựa chọn thiết kế**.
- Cái **đo được** và nên giữ: mỗi wave có **1 `StartPoint` + 1 `EndPoint`** (tổng **608** dòng mốc) và
  danh sách enemy nằm trong `listPrefabEnemies` — đó là **cấu trúc**, không phải nhịp.

### 2.2c Board_* — raw **đã có**, field **đã bind**, ý nghĩa **chưa chốt**

`ia-resolved.json` (bản `3ac2faa45`) có thêm **5 nhóm `Board_*`** ⇒ tổng **17 nhóm · 623 record** (claim **IA7**).
Hai mảng của `Board_Players` đã bind được **tên field** bằng asm (store ngay sau `InitializeArray`):

| field | kiểu | giá trị (index 0…) | đọc là gì? |
|---|---|---|---|
| `Board_Players.allBasicAtk` (`0x10`) | **float[24]** | `4640, 5120, 5040, 6160, 8896, 6880, 8889, 5680, 5500, 9100, 6750, 7589, 6000, 7588, 9100, 10050, …` | **chưa chốt**: “atk” theo tên, nhưng chưa thấy consumer ⇒ **B** |
| `Board_Players.allDeltaAtk` (`0x18`) | **float[24]** | **0,168** × 24 | **chưa chốt**: nếu là “delta mỗi rank” thì damage(rank) = basic + 0,168·rank — **giả thuyết**, chưa kiểm |
| `Board_Drones.cctor[0]` | float[12] | `500, 600, 800, 1250, 1500, 1800, 2300, 2800, 2535, 2500, 1251, 2680` | 12 mốc drone — giá hay HP: **chưa chốt** |
| `Board_Drones.cctor[1]` | float[12] | **0,16** × 12 | hệ số — chưa rõ nhân vào đâu |
| `Board_Drones.ctor` | float[24] | `1,0 ×3 · 2,2 · 1,0 · 1,875 · …` | hệ số theo index — chưa rõ |
| `Board_Endgame.ctor` | **int[10]** | `900, 890, 880, 870, 860, 850, 840, 830, 820, 810` | giảm đều **10** mỗi bậc — dải ngưỡng, chưa rõ dùng cho gì |
| `Board_Players.ctor` | float[24] | **1,0** × 24 | baseline |

> **Đừng suy ý nghĩa từ tên field.** `allBasicAtk` chưa có consumer đã đọc ⇒ chỉ ghi “raw + tên field”,
> mức **B**. Muốn lên **A** phải đọc chỗ dùng (offset `0x10/0x18` của class static).

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

#### 2.3c **saved ≠ trial ≠ effective ≠ cached** — bốn lớp, đừng gộp

Đây là thứ dễ làm sai nhất khi dựng lại hệ tàu, nên tách hẳn ra (report 66, địa chỉ asm trong đó):

| lớp | là gì | bằng chứng |
|---|---|---|
| **saved** | 15 key int32 trong Unity `PlayerPrefs`, default như bảng §2.3b | `raw/player-loadout/contracts.json.gz` |
| **trial** | khi `TRIAL_ID_{ship} == 1` (đúng bằng **1**): đọc `TRIAL_RANK_`/`TRIAL_LEVEL_` (default **0**) **thay** cho rank/level đã lưu | getter `PLAYER_RANK`/`PLAYER_LEVEL` |
| **effective** | **rank sàn 2** áp ở **loader** (`0x14f238c..0x14f2394`), **không** phải getter, không phải migration · `Tech_Datas.GetTechStatLevel` trả **0** khi `mode4` **và** scene `Game` · devices ở cùng điều kiện trả mảng mới `[-1,-1,-1,-1]` | loader/tech/device wrapper — **không xoá** giá trị đã lưu |
| **cached** | `GP_Setup` giữ **mảng 2 slot** + cờ khởi tạo instance ⇒ **không** đọc lại save mỗi lần gọi; `set_indexPlayers` **không** tự refresh trận đang chạy | `GP_Setup.get_indexPlayers` |

Bốn bẫy cụ thể, đã có test của họ:

1. `PlayerUsed{slot}` đọc **≤ 0** ⇒ ghi lại **cả** `PlayerUsed0=10001` và `PlayerUsed1=10002` rồi đọc lại.
   `CheckDoubleIDShip` (`0x14e7464`) là routine **riêng**: trùng slot ⇒ tìm tàu unlocked khác và đổi **slot0**,
   **không** đổi slot1 — đừng nhét luật này vào mọi setter.
2. `GetMaxCountRockets` (`0x14e5380`, stat **5**) **không đơn điệu**: level ≤ 0 → **7** · 1–5 → **8** ·
   **6–8 → 3** · ≥ 9 → **10**. Giữ nguyên; **đừng** "sửa" 3 thành 9 cho đẹp.
3. Setter devices lặp **đúng 4 slot**, không theo độ dài mảng ⇒ mảng ngắn có thể ghi một phần rồi lỗi;
   **không** có atomicity được chứng minh.
4. `TALENT_SELECTED` default **−1**; startup chỉ chép khi `StageTarget ≥ Board_Begin.stageUnlockTalents`
   (số **chưa** nối value — đừng đoán) **và** selection ≠ −1 **và** `mode != 4`.

> **Giữ là unknown:** trial expiry/writer lifecycle, toàn chuỗi trả tiền nâng cấp, migrate save, atomicity,
> cloud/durability. Nếu game mới thêm validation/atomicity thì ghi **"new design"**, không ghi là phục dựng.

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
| **feel** (hit stop · aim assist · input latency) | 0 site `timeScale` / 0 method `aim` trên **139** file asm (**AF2**, **AF3**) = **chưa thấy**, **không** phải "không tồn tại" (139 file là **mẫu**, không phải whole-build closure). Cái **đo được**: hit flash **0,5 / 0,05 s** (`J9`), rung **241** prefab (`AF1`). **BỎ theo quyết định 25/10**: game mới **không thêm** feel; số đo cũ chỉ để tham khảo |
| **art, font, atlas (bản gốc)** | L1 **vẽ mới**. Cái **không** bỏ là **luật thị giác**: khung hình · ba chế độ sáng · ngân sách accent · vignette khung thưởng · mật độ chi tiết — đã đo và ghi ở `VISUAL_DESIGN.md` |
| **số cân bằng cụ thể** (giá, tốc độ, mật độ) | L1 cho phép tự chọn; cái phải giữ là **cơ chế** (3 chế độ, không nhân quân, rơi đồ 3 tầng) |
| **thứ tự pha boss (D3)** | Có **795 event + mốc thời gian**; thứ tự là **lựa chọn thiết kế**, dữ liệu chỉ cần đủ để biết "mỗi pha có đòn gì" |
| **blob `InitializeArray`** | **Đã có**: 576 mảng Map + 6 Player + 5 nhóm `Board_*` trong `ia-resolved.json` (**623** record). Xin dump lại = bỏ qua việc **grep repo trước** (`RAW_AUDIT` luật 4) |
| **HP enemy** | **Đã có**: `datas/enemy_hp_by_id.json` = **150 cặp `id → HP`** (claim **WRH2**); `15-enemy-hp.csv` = 981 dòng serialize (claim **WRH1**). Gộp lại **108/109** prefab spawn có số HP (claim **WRH5**). 3 class enemy đã có asm (claim **WRH3**) ⇒ **không cần `.so`** |
| **damage/rate/wing/cost của player** | **Đã decode** (float[24] + int[24], `BALANCE` §1.1b) — thiếu **bind index→ID tàu**, không thiếu số |
| **“cần dump thêm class config”** | 17 method / **623** record đã đọc; phần còn lại là **literal store** + `.rodata`, không phải class chưa dump |
| **13 class "chưa phân loại" trong ASSET_TRIAGE** | vẫn còn **1.554** `unclassified` / 2.197 — nhưng đây là việc **phân loại ảnh**, không chặn dựng game (L1 vẽ mới) |

---

## 4. Trả lời "đủ chưa" — theo L1 / L2 / L3

- **L1 (làm game **giống cơ chế**, art mới, số tự chọn): ĐỦ.** 8/13 hệ đủ, **5** hệ một phần nhưng phần
  thiếu đều **không chặn** (D3 = chọn thiết kế; audio = tự chọn; talent = tự chọn giá).
- **L2 (giống **số** đến mức chơi thấy tương đương): CHƯA — nhưng không còn thiếu SỐ nào.**
  Giá trị damage/rate/cost/độ dài map **đã có** (§2.1 + §2.2); index↔tàu (T4) + cấu trúc bảng Map
  (`DIFFICULTY_MODES` §7) **đã bind**. Bốn mục từng liệt kê ở đây đều đã có/không tồn tại (§2):
  `kHp` không phải hệ số · `missionKillPercent` đủ 3/3 · HP enemy bind theo id · `rate` = giây.
  Playback thật **đã có sẵn trong repo** (phiên phone 23/10 — `docs/apk-analysis/ramus/2026-10-23-phone/`);
  sót **2 phép tái đối chiếu** (`CROSSCHECK`) — làm khi có lần chạy mới, không phải thiếu số.
  > Đừng nói “chờ bind”, “chờ dump thêm” hay “còn 4 số” nữa — cả ba đều là **câu trả lời cũ**, sai.
- **L3 (khớp trải nghiệm + art bản gốc): ĐÍCH của dự án — KHÔNG hoãn** (lần 14, 25/10). APK gốc là
  **chuẩn trải nghiệm đã kiểm nghiệm** ⇒ nghiệm thu = **đối chiếu reference đo được bằng máy, không
  cần playtest người thật**: `VISUAL_DESIGN.md` (khung **0,4813** · tương phản **0,45–0,80** · accent
  **≤10 %** gameplay / **~47 %** khung thưởng · chi tiết **13–22** · juice **0,05 s** + **0,10 · 20
  frame**) + so ảnh cùng scene + timeline **795** event + audio **15** rules. Input **đã đủ** (pack v2
  report 70 + pixel/geometry/spine/font + metrics **35** ảnh); bắt đầu khi L1 chạy được — **song song
  với L2**.

---

## 5. Nếu chỉ làm được **một** việc tiếp theo

**Không xin thêm raw nữa.** Việc đúng là **bind dữ liệu đã có**:

| việc | mở khoá | trạng thái |
|---|---|---|
| ~~Đọc consumer để nối `playerIndex` ↔ **ID tàu**~~ | **B3** đóng → TTK ước lượng | ✅ **XONG (hẹp scope 25/10)** — save/load: id − 10001; **combat: impl N → index N−1** (report 81/82, tàu 10001→index 2) |
| ~~Bind 576 mảng map → (chapter, stage, mode)~~ | **A6** đóng → **A5** đóng | ✅ **XONG phần cấu trúc** — 11 cấu trúc, 614 mảng phân loại xong (`DIFFICULTY_MODES` §7); chi tiết từng entry là việc nhánh dữ liệu đã ghép (`datas/map_table_segments.json` + `maps.json`) |
| ~~Tính `kHp[mode]`~~ | L2 | ✅ **KHÔNG TỒN TẠI** — chế độ không nhân HP (`DIFFICULTY_MODES` §3–5); khác biệt = composition bảng len-3 |
| ~~`missionKillPercent` 6/9 số~~ | nhiệm vụ/sao | ✅ **ĐỦ 3/3** — một `float[3]` theo mission index `[0.2/0.6/0.98]`; "3×3" là ảo đơn vị |
| ~~`StartHpPoint` ← dict~~ | TTK enemy | ✅ **đã bind theo id** — dict 150 cặp là nguồn (`GetStartHealthPoint(id)`); `Init` chỉ là plumbing |
| ~~Kiểm runtime `rate` (shot/giây?)~~ | L2 | ✅ **đã chốt (A)**: = giây delay theo nhánh (report 53, §2.4) |
| Playtest so TTK/cảm giác + `PlayerUsed` refresh | L2 → L3 | cần **thiết bị** — kiểm hành vi, không phải thiếu số |

> Bảng này **thay TODO cũ** (“đọc consumer nối playerIndex”, “bind 576 mảng”) — hai việc đó
> **đã xong**, đừng lặp nữa (sửa 25/10 sau khi bị nhắc).

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
