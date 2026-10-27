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

## 1. Mười bốn hệ — trạng thái

| # | Hệ | Đủ để dựng lại? | Đang có (bằng chứng) | Thiếu gì |
|---:|---|---|---|---|
| 1 | **Vòng lặp lõi** (30 s / 1 phiên / 1 tuần) | ✅ **đủ** | `GAMEPLAY.md` §0; 3 vòng lặp viết được thành design doc | — |
| 2 | **Điều khiển + va chạm** | ✅ **đủ** | kéo ngón để lái, nhấc tay đổi tàu; biên **20×25**, radius **15 unit** (`ENEMY_BEHAVIOUR.md`) | — (L1 tự chọn cảm giác) |
| 3 | **Súng / đạn / sát thương** | ✅ **đủ** cho L1 | **458 súng** · damage **40–1.200** (median 400) · **186 loại đạn** · burst 5 tham số (`COMBAT.md`) | **B3**: đường cong damage theo rank — xem §2.2 |
| 4 | **Enemy** | ✅ **đủ** | **109 prefab** (39 boss + 70) · 9 component · 399 đường bay *(đo từ bản 800-cũ — CSV hiện hành 981 dòng, chưa có cột path để đếm lại)* · **150 HP id** (`datas/enemy_hp_by_id.json`) | — (B1 coi như đóng: HP theo **id**, không theo wave) |
| 5 | **Boss** | 🟡 **một phần** | 39 prefab `Boss-*` · **795 event** có mốc thời gian · 268 cặp (prefab, clip) · nhịp **0,17 / 0,33 / 1,0 / 5,0 s**; Boss-39001 Spine chain + completion-state branches are statically traced (reports 140–142, 157) | **D3**: thứ tự pha + điều kiện vào/thoát — có mốc, **chưa có** thứ tự (mức C); Boss-39001 Event callback is `RET`, its slot/handler/marker join remains unresolved (no runtime inference) |
| 6 | **Wave / spawn** | ✅ **đủ** | **282 wave · 11.089 dòng cấu hình · 23.757 spawner · 22.451 entry** (`H2`, `I3`, `M3`, `AQ7`) | `rate = 0` **chưa** kết luận "spawn cả loạt" — xem §2.4 |
| 7 | **Độ khó 3 chế độ** | ✅ **đủ** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · không nhân số quân | ngưỡng % riêng = tự chọn |
| 8 | **Kinh tế / rơi đồ** | ✅ **đủ** | 3 tầng rơi: **702** vật đặt sẵn (**676 coin / 26 item**) · **246/2.094** slot mang item · **6** loại (`AE1`–`AE3`) · chuỗi nổ vàng **đã nối (report 88)**: DropGold `lost > iPlus×10` → event6 → budget **28 → 8 object** (chia 5) → pool · **tiền nhặt ĐÃ CÓ CÔNG THỨC (report 89)**: Coin1 `A=min(1,5g;16)+2,5` · Coin2 `B=min(3g;23)+12`, 4 band balance ×L(tech) ×device ×.86(stage≤40); Burst 8 item = **69/165 xu** (stage 1/41) | trọng số chọn giữa 6 loại — **tự chọn** |
| 9 | **Meta: tàu / sao / talent / drone** | 🟡 **một phần** | **25 tàu**; `Player_Info` **4 field**: `id` · `Sprite` · `Star` · `Actived` (claim **AM3**) — nhưng damage **có** lookup theo tàu: `GetMainCannonDamage(playerIndex)` đọc **mảng static float** `0x78` theo `playerIndex` (§2.2); `Player_Talent` **23 method** · **13 drone** | 6 mảng damage/rate/cost **đã decode** (§2.2); **bind combat ĐÃ SỬA (report 81/82)**: impl N → index N−1 (tàu 10001→2 · 10003→0; id−10001 chỉ đúng save/load) ⇒ TTK **ước lượng** theo từng tàu. **HP max tàu ĐÃ CÓ CÔNG THỨC (report 91)**: `GetStartHp` = **2500 × (1 + 0,18×TechStatPoints(0) + 1×ability7)** — công thức chung, không bảng theo tàu (§2.2); luật bắn **12 impl drone + wing barrels theo Level ĐÃ CÓ (report 90)** (`DATA_SYNC` §24.23). Còn: DPS **runtime** (cần health/shield gates); **23 wing impl** còn lại + DPS closure (scope 90) — ~~mapping drone prefab→sourceID · `turnRate3` serialized~~ **ĐÓNG (report 92: bindings 20001..20012 → Drone_Attack1..12; turnRate3 live = 1,0)** |
| 10 | **UI** | ✅ **cấu trúc** · ✅ **luật thị giác** / ❌ **asset** | **797 màn · 150.131 node · 5.831 nút** (`N2`, `P6`); **55.584** layout file; khung hình **0,4813** · accent **≤10 %** · tương phản **0,45–0,80** (`VISUAL_DESIGN.md`, **AN1**, **AN2**) | asset gốc: **vẽ mới**; luật thì **đã có số** |
| 11 | **Âm thanh** | 🟡 **có dữ liệu + 15 luật tĩnh** | **69 clip / 571,5 s** (`audio-index.csv`) · `datas/audio_rules.json`: **15 rules** (mute/volume/pause/oneshot/music…) · registry **92** id · enum **118** (report 67; `DATA_SYNC` §21.1) | **đối chiếu nghe + trigger lúc chơi** — tĩnh hiện PROVISIONAL, cần 1 lần chạy để nâng mức |
| 12 | **Save / load + live-ops** | 🟡 **một phần** | key đã đọc: **`StarCount`** · **`StarStageMaster{stageIndex}_{modeIndex}`** (default 0) qua `PlayerPreferences.SetInt → PlayerPrefs.SetInt`; model `savedStars/result` (report 57); **170 IAP** | **schema đầy đủ** (mọi khoá/kiểu/migrate) + **chưa** chứng minh flush đĩa — xem §2.3 |
| 13 | **Tech / build** | 🟡 **một phần** | Unity **2022.3.x** (`UNITY_RULES.md`) · Spine · DOTween · 3 loader trong repo này | plugin list đầy đủ + cấu hình build (lấy từ `dump.cs`/manifest, không cần thiết bị) |
| 16 | **Sprite/Prefab: ý nghĩa + binding** | 🟡 **catalog A — binding 🔴 chưa join** | catalog đủ: index **2.197** (`sprites-index.csv`) + `datas/sprites.csv` **2.885** (2.184 Sprite/632 Texture2D/69 AudioClip); ý nghĩa: 925 rule + 124 mắt + 643 passthrough + **505 unknown**; geometry/pixel/pivot/border **ĐÓNG** (62/72/75); binding item: tàu **25/25** · boss **46** (`ships.json`/`bosses.json` → sprite_path_id) | **sprite → consumer CHƯA có join toàn cục**: `prefab_joins.csv` 3.870 rows **0 sprite**; UI 55.584 layout chỉ summary bên này (cây ở peer raw); scene-1 218/1.377 (report 76); spine 27 rig identity **inferred**; bucket **glyph** (292 — **ngoài** CSV 624) gom **118 tên số = 25 tàu + 32 boss + 13 drone + 48** (lần 34 đo lại; lần 32 ghi sai cơ chế) — vẽ theo bucket sẽ bỏ sót 70 sprite chính; **L3 chains ĐÃ CÓ (reports 96–98)**: `ui_l3_bindings` (797 sources · **1.099 sprite identity**) + `ui_layout_inventory` (**đủ 55.584** — ngoài index: 3.843.228 obs chỉ tên, **0 scoped PPtr** ⇒ exact-identity legacy bất khả, phải về serialized source) + `ui_composition` (**100.312** component · matrix 99.731/581 unknown) + `l3_scene_chains` (**805 root views** · 665/665 clips channel-exact · 2.139 callbacks · camera `max(h/w×5,4; 9,6)`) — CLI `l3_recipe.py`; còn: renderer_enabled unknown · 160 ambiguous parents · gate render chưa chạy; 116 atlas-name + rig thật + nhãn 505/643 vẫn queue |
| 14 | **Arena / PvP** | 🟡 **khung mode A — luật in-game CHƯA đào** | `GAMEPLAY` §2: PlayMode 5 = **Arena** (async, **10 league** Bronze→Champion, luật mùa/phòng: `ArenaConfig.MaxRoomCount/MinUserCount` · `RankUpIndexs/RankDropIndexs` · `txt_rule_desc1..6`) · 6 = **PVP** (**10 rank** Herald→God; 3 `PVPMode` {Tournament/Solo/Hunter} vs text Leagues/**Betting**/Hunter — **lệch mức A**, phải quyết thiết kế: bỏ/hay thay Betting) · 2 luật PVP tình cờ theo reports 86/87 (`Player_Controller` PVP `0x14c44e0` · PVP `HealHp` 1 không WaitUntil) · asset `PVP1..10` = 91 sprite huy hiệu · `Board_PVP` 42 slot UI | **0 report/batch riêng về Arena/PvP**; dump.cs **40 class** (ArenaManager 34 · ArenaHub 23 · GP_PVP_Manager 21 · PVP_Manager 15 method — **chưa dịch class nào**); map pool `AllArenaStartMaps/AllArenaRandomMaps/AllPvPStartMaps` — tên+offset biết (`DIFFICULTY_MODES` §7), **giá trị chưa decode**; thân `GetArenaScore/GetPVPPlayScore/GetArenaPlayScore` mức **D** (`BALANCE` §6.6); medal/shop exchange; `datas/` **0 file** — đã queue PR12 (không khẩn) |
| 15 | **Meta thưởng ngày/tuần** | 🟡 **cấu trúc A — luật số 0 hit** | khung (kiểm 25/10 lần 31): gift login **30 ô** (`Tab_LogIn` · `Popup_BuySpeed` ×2 tốc độ nhận) · **quest ngày** `Board_Quest` → `Board_QuestRewards` (3 loại hộp → key0–2) · **BP** `Board_BattlePass` **85** + `Board_BattlePassNew` **39** mốc ×2 track (mốc 16 = 3 ngày premium) · **event season pass** `Board_EventSeasonPass` + ability event · **premium daily** (`Popup_PremiumDailyRewards` · flag `IsCollectPremiumDailyGift`) · **holiday gift 75** slot · **rewarded video** (`Popup_WatchVideos(+New)` 48 slot + `TimeFreeRewardPack`) · **VIP** `Board_Vip` + `GetVipLevel(vipPoints)` · **energy** hồi thời gian (`energy`/`timeRewards`, `Popup_BuyEnergy`) | **0 giá trị decode**: `MAX_LEVEL_BP` · `timeRewards` · `vipPoints` · giá từng ô gift/quest/video — **0 hit** trong `ia-resolved.json`; dump.cs có class (`Board_QuestRewards` · `Achievement`×2 · `TimeFreeRewardPack` · `SeasonRewards`…) **chưa dịch class nào** ⇒ **queue PR12** (sau named map/save consumers) — chiến lược retention có mô tả (`GAMEPLAY` §1/§3) nhưng số thưởng/thời gian chưa có |

**Đọc bảng này theo đúng nghĩa:** 8 hệ **đủ** để dựng lại, **8 hệ một phần** (Arena/PvP · meta thưởng ngày/tuần · sprite/prefab-binding — catalog có, chỗ chưa: luật số / join), **0 hệ thiếu hoàn toàn** (save/load đã có key, chưa đủ schema — §2.3).

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
- **Nội dung đọc được:** **576 mảng `int`** · **5.154** giá trị · **253** wave id khác nhau · **0** giá trị không có trong `datas/waves.json` (claim **IA3**). Riêng `listMapDatas` nay đã được trích chính xác theo `.cctor`: **250 entry / 742 số**, gồm 243 payload `InitializeArray` + 7 literal arrays; xem A2 và report 160.
  ⇒ **Payload wave đã có; phần còn mở là bind internal index sang stage/scene**, không phải chờ dump.
- **Không phải “573 = 576 − 3”.** Ba entry mở đầu (`CM1`): **3 entry** = `[25, 9010]` · `[164]` · `[113, 5]` · **13** check; chúng được dựng bằng
  **literal store**, **không** nằm trong 576 `InitializeArray` ⇒ trừ đi là **sai đơn vị**. Và **576 cũng
  không phải 576 stage**: đó là số *mảng*, chưa bind sang (chapter, stage, mode).
- **Kiểm bằng asm (`CM2`):** `0x78` + `sxtw #2` + index `w19` — `GetMainCannonDamage` đọc mảng theo `playerIndex`.
- **Phân bố độ dài** (số mảng): `3 → 320` · `7 → 104` · `36 → 63` · `4 → 21` · `5 → 12` · `6 → 9` ·
  `20 → 5` · `24 → 2` · dài nhất **69**.
- **Việc còn lại là *identity bind*, không phải *payload/order dump*:** consumer chain đã nối tới cuối (`MapController.Start → setup.get_stageIndex → Map_Get_Datas.GetListWaves(index)`; report 89 đọc tiếp `get_stageIndex`: Test-gate → `mapCurrentPlayTest@20` · `IsBranch@30` → `StageBranchCurrent@2c`/`StageCurrent@24`). H1 xác nhận `.cctor` insertion order của 250 `listMapDatas` rows, nhưng **không** ghép từng internal index với (chapter, stage, mode) hoặc scene name. Giữ identity **unknown**, không gán theo trực giác.
- `datas/maps.json` (**250** map) khớp **250/250** với source-linked H1 extraction; `datas/map_waves_candidate.json` là legacy candidate và lệch 242 rows, nên không dùng làm full table.
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
- **Khác lớp (đừng gộp):** `raw/player-loadout/array-blobs.json.gz` — **5 blob** · **49 int** · **5/5 sha256 OK** (claim **CM5**) — có năm payload records / 49 declared int32 across two classes: ba `Player_Saved_Datas.cctor` arrays bind trực tiếp tới `MaxLevelPerRanks`, `CardUpgrades`, `StartRanks`; hai records còn lại là method-local arrays, không phải named application fields. The separate `GetCostCraftPlayer` `InitializeArray` at `0x14e7c78` selects a handle-indexed int[7] payload for IDs 10001–10024, but those payloads are **NOT_BOUND** in the checked capture (G6). Không gộp các mảng int này với float damage; field name/value alone does not establish broader design purpose.
- **Bind index↔tàu — ĐÃ HẸP SCOPE (sửa 25/10 theo report 81/82 peer):** ~~id − 10001 cho mọi consumer~~
  → **chỉ đúng ở consumer save/load** (`0x14e2ce4`, `CROSS_BRANCH` T4 — giữ nguyên scope đó).
  **Combat**: impl `Player_Attack_N` đọc mảng index **N−1** (CFG **72/72** call — 24 rate + 24 damage +
  24 wing, report 82 §1); source tàu: impl1→**10003** · impl2→10002 · impl3→**10001** · impl4–24→
  10004–10024 ⇒ tàu **10001 → index 2** (proxy **12.864**), tàu **10003 → index 0** (proxy **21.600**).
  Hợp đồng: `datas/combat_chain_contract.json.gz` + `datas/combat_argument_audit.json` (peer).
- **(1) HP riêng của tàu — ĐÃ ĐỌC XONG WRITER (report 91, `datas/player_hp_board_flow.json`):**
  **KHÔNG có bảng theo tàu.** Max HP = `GetStartHp 14e311c`: **2500 × (1 + 0,18×TechStatPoints(0) +
  1×ability7)** — cùng input ⇒ cùng max; cctor default **2000**; writers: `ResetStaticVariables`
  (Current=Start) · **event36** (payload==7 → chỉ ghi StartHealth) · **event64** (playMode1 ∧
  waveIndex≠0 → **giữ tỉ lệ** Current/Start; else reset — điều kiện là waveIndex, không phải tàu) ·
  `OnChangeDataDevice` **không** ghi max (chỉ band giảm-damage 1000–1999 / heal 5000–5999).
  Auto-gain 5 s — **guard Current>0** (không hồi sinh tàu đã chết); techHeal = **0** khi
  TechStatLevel(0) = 0 (**âm rơi nhánh base** — report 91, không tự thêm ≤0); clamp Start, không
  nhân deltaTime. Tàu 1 runtime **2500** = 0 point/0 abi7 —
  **không universal**; cách `TakeDamage` áp `reduceDamageByDevice` là consumer riêng, chưa đọc.
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

### 2.2c Board_* — `Board_Drones` và `Board_Players` đều có consumer UI; combat meaning vẫn **B**

`ia-resolved.json` (bản `3ac2faa45`) có thêm **5 nhóm `Board_*`** ⇒ tổng **17 nhóm · 623 record** (claim **IA7**).
Hai mảng của `Board_Players` đã bind được **tên field** bằng asm (store ngay sau `InitializeArray`):

| field | kiểu | giá trị (index 0…) | đọc là gì? |
|---|---|---|---|
| `Board_Players.allBasicAtk` (`0x10`) | **float[24]** | `4640, 5120, 5040, 6160, 8896, 6880, 8889, 5680, 5500, 9100, 6750, 7589, 6000, 7588, 9100, 10050, …` | ✅ `GetPlayerPower` → `SetPlayerInfo.textPlayerPower`: confirmed UI-power consumer; **not** combat-damage proof (report 109) |
| `Board_Players.allDeltaAtk` (`0x18`) | **float[24]** | **0,168** × 24 | ✅ `GetPlayerPower` uses `delta[i] × GetPlayerLevel` in the UI-power expression; combat/rank interpretation remains **unproven** (report 109) |
| `Board_Drones.allBasicAtk` (static10) | float[12] | `500, 600, 800, 1250, 1500, 1800, 2300, 2800, 2535, 2500, 1251, 2680` | ✅ **UI power** — `GetPlayerPower 1263860`: round-half-even(basic[i] × (1 + delta[i] × GetDroneLevel)) → `textDispDamage` (report 91 §5b) |
| `Board_Drones.allDeltaAtk` (static18) | float[12] | **0,16** × 12 | ✅ **hệ số level** của công thức UI power trên |
| `Board_Drones.ctor` (`playerPriceMultipleA` @238) | float[24] | `1,0 ×3 · 2,2 · 1,0 · 1,875 · …` | ✅ **giá nâng cấp UI** — `SetUpgradeCost`, index = cellIndex − 20001 (report 91 §5a) |
| `Board_Endgame.devidedArenaMedals` (`this+0x2A0`, constructor) | **int[10]** | `900, 890, 880, 870, 860, 850, 840, 830, 820, 810` | ✅ `SetArenaRewards` (PlayMode 5): index = `GameMode.arenaRank`; divides `Board_Endgame.arenaPoints`; positive quotient → `SetGiftInfo` item ID 22 quantity. Item-22 identity is not bound (report 153) |
| `Board_Players.ctor` | float[24] | **1,0** × 24 | baseline |

> ⚠ **Cấm xác nhận chéo (góp ý #3, report 91 §6):** UI power (`allBasicAtk`) **≠** combat
> `GetBaseDamage` (report 90): 20001 → UI **500** vs combat **450** · 20003 → UI **800** vs combat
> **6000** — hai nguồn số khác consumer, không damage×rate proxy. `Board_Players.allBasicAtk/
> allDeltaAtk` (float[24], `4640…`/`,168`) có consumer UI `GetPlayerPower` → `textPlayerPower`;
> điều đó **không** chứng minh combat damage/rank semantics ⇒ B3 damage-theo-rank của tàu chưa chốt.
>
> **G1 reconciliation (PR12 claim `6422828995`, reports 109 + 122):** the UI consumer identity is
> already directly bound; the proposed `damage(rank) = basic + 0.168·rank` equation is **not supported**.
> The traced `GetPlayerPower` formula is multiplicative and uses `GetPlayerLevel` for display, while
> the bounded `Player_Attack_1` combat trace reads `Player_Get_Datas.StartMainCannonDamages` (`0x78`)
> and uses rank as a guarded loop bound, not as the getter's damage input. This is not a global
> non-use proof; keep combat semantics at **B**. `4640` is an entry in the board-power array, **not
> ship HP**.

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
| ~~Bind 576 mảng map → (chapter, stage, mode)~~ | **A6** đóng → **A5** đóng | ✅ **XONG phần phân loại cấu trúc** — 11 cấu trúc, 614 mảng (`DIFFICULTY_MODES` §7). ⚠ **Binding entry cụ thể vẫn UNKNOWN** (góp ý #4 report 91): thứ tự nạp `listMapDatas` chưa chứng minh (§2.1); `map_table_segments.json`/`map_waves_candidate.json` = **candidate**, `maps.json` = dẫn xuất khác nguồn — không dùng xác nhận |
| ~~Tính `kHp[mode]`~~ | L2 | ✅ **KHÔNG TỒN TẠI** — chế độ không nhân HP (`DIFFICULTY_MODES` §3–5); khác biệt = composition bảng len-3 |
| ~~`missionKillPercent` 6/9 số~~ | nhiệm vụ/sao | ✅ **ĐỦ 3/3** — một `float[3]` theo mission index `[0.2/0.6/0.98]`; "3×3" là ảo đơn vị |
| ~~`StartHpPoint` ← dict~~ | TTK enemy | ✅ **đã bind theo id** — dict 150 cặp là nguồn (`GetStartHealthPoint(id)`); `Init` chỉ là plumbing |
| ~~Kiểm runtime `rate` (shot/giây?)~~ | L2 | ✅ **đã chốt (A)**: = giây delay theo nhánh (report 53, §2.4) |
| Playtest so TTK/cảm giác + `PlayerUsed` refresh | L2 → L3 | cần **thiết bị** — kiểm hành vi, không phải thiếu số |

> Bảng này **thay TODO cũ** (“đọc consumer nối playerIndex”, “bind 576 mảng”) — việc đầu **đã xong**;
> “bind 576” chỉ **xong phần phân loại cấu trúc** — **named binding entry/thứ tự nạp `listMapDatas`
> vẫn phải đào** (§2.1; sửa footer theo góp ý review `de2d1366`). Đừng lặp việc xong, đừng gọi
> phần chưa xong là xong.

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
