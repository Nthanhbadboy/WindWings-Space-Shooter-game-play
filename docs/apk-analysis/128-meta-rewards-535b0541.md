# 128 — Meta thưởng ngày/tuần: bảng pack, season-pass shop, sentinel `GameDatas` (STATIC-ONLY)

**Task:** #30 (AI-4) · **Branch:** `arena/535b0541-windwings-space-shooter-game-p`
**Artifact:** `datas/l2_535b0541_meta_rewards.json.gz` (72.690 B, SHA256 `4edc47670c2948d95e6e10ec4e5fc166ecbb2a955969c2276dca2700b3fc1f79`)
**Raw bytes:** `reverse-engineering/raw/meta-rewards-535b0541/native.json.gz` (447.975 B, SHA256 `e91a8c7664666f349042d78994b7ecd53ae8e67e243c4bf3326f8cab232d4937`)
**Bằng chứng:** `STATIC_ONLY_ORIGINAL_APK` — không emulator, không thiết bị, không probe. Mọi giá trị dưới đây là byte tĩnh của APK gốc; **decode tĩnh ≠ hành vi runtime**.

Đóng 2 khoá rẻ mà ACK #29 yêu cầu (`metadataUsagePairs` → `ArenaManager.rewards`/`ArenaConfig`, blob token → `PVP_Manager.MaxRankStars`) và mở phần meta thưởng ngày/tuần (`Shop_Pack`, `TimeFreeRewardPack`, `Popup_WatchVideos`, `GameDatas`, `Board_EventSeasonPass`).

---

## 1. Nguồn và pin

| Nguồn | SHA256 | Vai trò |
|---|---|---|
| `windwings.xapk` (release `windwings-apk-1.3.118`) | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` | nguồn byte gốc |
| `lib/arm64-v8a/libil2cpp.so` | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` | mã máy + `.data.rel.ro` |
| `dump.cs` (giải nén) | `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c` | layout field + TypeDefIndex + `<PrivateImplementationDetails>` |
| `reverse-engineering/il2cpp/stringliteral.json` | pin trong artifact | chỉ mục `Il2CppString` theo địa chỉ |
| `reverse-engineering/il2cpp/field-defaults.json` | pin trong artifact | `fieldDefaultValues` (blob literal) |

Trích xuất: `tools/recovery/meta_rewards_native.py` (workflow `meta-rewards-static-recovery.yml`, run **40349801977** SUCCESS, commit raw `00e010460`) — **cố ý tách khỏi** `arena_pvp_native.py` để raw/artifact của #29 (đã ACK, pin SHA) không bị sinh lại. Quy mô: **540 method / 70 class / 13 họ**.

Giải mã: `tools/verify/meta_rewards.py` (join metadata usage ↔ string literal, token `InitializeArray` ↔ blob) + `tools/verify/arena_pvp_initializers.py` (pass symbolic, đã mở rộng).

## 2. Hai lỗi của bản #29 đã tìm ra và sửa (nguyên nhân gốc)

1. **Pairing `InitializeArray` sai.** Bản #29 append các event đã ghép *trở lại* danh sách đang được lọc, nên mọi `bl #0x205b07c` lấy `before[-1]` = event đầu tiên: 10 mảng `MaxRankStars` cùng trỏ một slot ⇒ `[3,3,3]` lặp 10 lần. Bản này giữ `initialize_arrays` riêng, mỗi call một event.
2. **Ordinal token lệch 1.** `src = 2·ordinal+1` chỉ đúng nếu **đếm đủ mọi field** của `<PrivateImplementationDetails>`. Bộ lọc đầu tiên chỉ nhận field `__StaticArrayInitTypeSize=…` nên bỏ mất field vô hướng `internal static readonly int 27ECD0A5… = -1;` (0x13B8) và đẩy lệch toàn bộ ordinal: `GameDatas.cctor` ra ordinal 369 thay vì **368** (`7BB8C603…`, 24 B — đối chiếu `ia-resolved.json`), và 11/15 mảng "khớp size" một cách ngẫu nhiên. Đếm đủ field ⇒ **15/15** mảng khớp `declared_bytes ≥ 4·len` và `default_bytes < 4·len+16`.

Hai bug này là lý do `MaxRankStars` từng bị khai `not_decoded` ở báo cáo 127.

## 3. Kết quả

### 3.1 Metadata usage (slot → literal)

| Chỉ số | Giá trị |
|---|---|
| Slot metadata trong scope | **3.447** |
| Kind 1 (`TypeInfo`) | 1.981 |
| Kind 3 (`MethodDef`) | 113 |
| Kind 4 (`FieldInfo`) | 15 |
| Kind 5 (`StringLiteral`) | **551** (543 có text, 8 literal rỗng thật) |
| Kind 6 (`MethodRef`) | 787 |
| Chưa phân giải | 2.896 (không phải literal — không có text để mất) |

15 slot kind-4 khớp **đúng 15** call `InitializeArray`: mỗi token field là một slot riêng ⇒ phép join tự nhất quán.

### 3.2 `ArenaConfig` — khoá #29 (RVA `22726640`)

| Field | Giá trị tĩnh |
|---|---|
| `RankSplit` | `20-45;15-45;15-45;10-45;10-45;10-45;10-45;10-45;10-45;10-45` |
| `SeasonTime` | `1440;2880;4320;7200;10080;11520;12960;14400;15840;17280` |
| `MaxRoomCount` / `MinRoomCount` | 50 / 10 (một literal 8 B `32000000 0a000000` @ 7.698.976) |
| `SummaryTime` / `IsOpen` | 60.0 / false |

10 mốc `RankSplit` (số phòng tối thiểu–tối đa mỗi bậc) và 10 mốc `SeasonTime` (phút: 1.440 = 24 h → 17.280 = 12 ngày) khớp đúng 10 bậc mùa.

### 3.3 `ArenaManager.rewards[10]` — bảng thưởng mùa arena (RVA `22692372`)

Mỗi chuỗi là bảng thưởng theo hạng cho một mùa, đúng thứ tự mùa 1→10:

| Mùa | #1 (Medal/Gems) | #2 | #3-4 | #5-10 | #11-45 | #46-50 |
|---|---|---|---|---|---|---|
| 1 | 680 / 250 | 460 / 180 | 320 / 120 | 200 / 80 | 120 / 50 | 60 / 20 |
| 2 | 800 / 300 | 540 / 220 | 380 / 150 | 240 / 100 | 140 / 60 | 70 / 20 |
| 3 | 1000 / 350 | 680 / 250 | 470 / 170 | 290 / 110 | 170 / 70 | 90 / 30 |
| 4 | 1250 / 400 | 850 / 290 | 490 / 190 | 370 / 130 | 220 / 80 | 110 / 30 |
| 5 | 1500 / 500 | 1010 / 360 | 700 / 240 | 440 / 160 | 260 / 100 | 130 / 40 |
| 6 | 2000 / 600 | 1350 / 430 | 940 / 290 | 590 / 190 | 350 / 120 | 180 / 50 |
| 7 | 2500 / 700 | 1690 / 500 | 1180 / 330 | 740 / 220 | 440 / 140 | 220 / 60 |
| 8 | 3000 / 800 | 2030 / 580 | 1410 / 390 | 880 / 260 | 530 / 160 | 270 / 60 |
| 9 | 4000 / 900 | 2710 / 650 | 1890 / 430 | 1180 / 290 | 710 / 180 | 360 / 70 |
| 10 | 5000 / 1000 | 3380 / 720 | 2350 / 480 | 1470 / 320 | 880 / 200 | 440 / 80 |

### 3.4 `PVP_Manager.MaxRankStars` (RVA `19916640`, 10 call `InitializeArray`)

| Bậc | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Độ dài | 3 | 3 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 |
| Giá trị | `[3,3,3]` | `[4,4,4]` | `[4,4,4,4]` | `[5,5,5,5]` | `[5,5,5,5,5]` | … (6 bậc cuối giống nhau, cùng blob `7861A5C4…`) |

Token: `0x8000000d`, `0x800000ff`, `0x80000545`, `0x800002ed`, `0x800002c7`×6 (RVA call 19.930.288 … 19.931.340).

### 3.5 `GameDatas` (RVA `20085468`, 244 B) — sentinel khởi tạo

`GameDatas` **không** giữ giá trị kinh tế thật trong `.cctor`; nó ghi sentinel/cap rồi runtime nạp lại từ PlayerPrefs:

| Field | Giá trị tĩnh | Ghi chú |
|---|---|---|
| `timeRewards` | 90.000.000 | word thứ 2 của vector hằng dùng lại cho `maxCheat`/`itemPowerup` |
| `vipPoints` | **-1** | sentinel "chưa nạp" |
| `arenaPoints`, `campaignPoints`, `pvpMedal`, `w`, `h` | -1 | cùng sentinel |
| `energy` | 1.101 | trùng `antiCheat` |
| `coins` / `gems` | 990.000.000 / 100.000.000 | trùng `maxCheatCoins`/`maxCheatGems` |
| `percentGraphics` | `float[6]` = 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 | blob `7BB8C603…` (khớp ground-truth `ia-resolved`) |
| `cheatTutIndex` | 6 | |

⇒ **`timeRewards`/`vipPoints` không phải bảng thưởng**; chúng là state người chơi, `.cctor` chỉ đặt mặc định. Mọi con số "thưởng theo ngày" thật nằm ở §3.6–3.8.

### 3.6 `TimeFreeRewardPack` (RVA `19190916`) và `Popup_WatchVideos` (RVA `20313632`)

| Field | Giá trị |
|---|---|
| `TimeFreeRewardPack.keySysTime` | `"TimeFreePacks"` (PlayerPrefs key) |
| `TimeFreeRewardPack.timeAds` | **43200.0 s** (12 h) — dựng bằng `mov x11,#0x180000000000` + `movk x11,#0x40e5,lsl#48` |
| `TimeFreeRewardPack.totalSecs` / `timeUpdate` | 0.0 / 1 |
| `Popup_WatchVideos.NumberSlots` | 6 |
| `Popup_WatchVideos.coinXValue` / `gemBonus` | 150 / 20 |
| `Popup_WatchVideos.duration` | **900.0 s** (15 phút) |

### 3.7 `Shop_Pack` (RVA `20237248`, 21.560 B) — bảng pack thưởng ngày/tuần/video

`PackDaily[3]` (quà ngày):

| # | Nội dung |
|---|---|
| 0 | Gems 30 · Overdrive 3 |
| 1 | Gems 0 · DeviceB 2 · Key0 30 · Key1 30 · WingCoins 20 · multipleBonus 2 |
| 2 | DeviceA 3 · Key1 30 · Key2 30 · WingCoins 120 · multipleBonus 3 |

`PackWeekly[5]` (quà tuần):

| # | Nội dung |
|---|---|
| 0 | Gcoins 25.000 · Gems 300 · Key1 25 · multipleBonus 4 |
| 1 | Gems 2.000 · Key1 180 · Key2 45 · multipleBonus 5 |
| 2 | DeviceS 1 · Gems 4.900 · Key2 60 · WingCoins 300 · multipleBonus 6 |
| 3 | DeviceSS 1 · Gems 9.999 · Key2 120 · WingCoins 666 · multipleBonus 5 |
| 4 | DeviceSS 2 · Gems 29.000 · Key2 150 · WingCoins 1.500 · multipleBonus 8 |

`PackDailyVideo[3]` (thưởng xem video):

| # | Nội dung |
|---|---|
| 0 | Gcoins 3.000 · Gems 15 |
| 1 | Gcoins 5.000 · Gems 20 · PlayerCards 2 |
| 2 | Gcoins 10.000 · Gems 25 · PlayerCards 3 · DroneCards 3 |

`PackSpec[3]`: `{Gcoins 250.000, Gems 3.000, Key1 60, Key2 30, multipleBonus 12}` · `{Gcoins 600.000, Gems 6.500, Key2 60, WingCoins 280, multipleBonus 12}` · `{Gcoins 99.999, Gems 1.200, Key1 30, multipleBonus 12}`.

`FreeGift` = `{Gems 500, Energy 1.000}` · `PremiumDailyRewards` = `{Gems 300, DroneCards 20, PlayerCards 10}` (field `Premium`/`multipleBonus` = 0 tĩnh).

List dựng trong `.cctor` (đếm phần tử, artifact giữ từng dòng): `allVipRewards` 7 · `allVipRewardsFree` 7 · `allFightBossRewards` 19 · `allLogInRewardsRoot` 29 · `allLogInRewardsRoot2` 29 · `allBattlePassPacksRoot` 29 (mảng đôi). Ví dụ `allVipRewards[6] = {Gcoins 100.000, PlayerCards 200, Key2 90, DeviceSS 1}`; `allFightBossRewards[0] = {Gems 20, DroneExp 6.500, DroneCards 8, WingCoins 6}`.

**Cảnh báo độ tin:** `BoxRewardsRoot[0…2]` chứa nhiều giá trị `1` và `Gcoins = 68` (0x44) ở cả 3 dòng — đúng như mã ghi, nhưng trùng hợp về mặt ngữ nghĩa chưa được kiểm chứng; coi là **template box**, không phải giá bán.

### 3.8 `Board_EventSeasonPass.eventRewards[20]` (RVA `19462112`) — shop season-pass

20 dòng `EventRewards{ pack, number, price, stock }` dựng tĩnh trong `.cctor` (trước đây bị xếp vào "serialized ngoài `.so`"):

| # | pack | number | price | stock |
|---|---|---|---|---|
| 0 | Gcoins 1 | 1.000 | 10 | 100 |
| 1 | DroneExp 1 | 1.000 | 10 | 50 |
| 2 | DroneCards 1 | 1 | 25 | 50 |
| 3 | DroneCards 2 | 1 | 33 | 50 |
| 4 | DroneCards 3 | 1 | 40 | 50 |
| 5 | DroneCards 4 | 1 | 48 | 50 |
| 6 | DroneCards 5 | 1 | 55 | 50 |
| 7 | DroneCards 6 | 1 | 65 | 50 |
| 8 | DroneCards 7 | 1 | 80 | 50 |
| 9 | PlayerCards 1 | 1 | 35 | 50 |
| 10 | PlayerCards 2 | 1 | 43 | 50 |
| 11 | PlayerCards 3 | 1 | 50 | 50 |
| 12 | PlayerCards 4 | 1 | 58 | 50 |
| 13 | PlayerCards 5 | 1 | 65 | 50 |
| 14 | PlayerCards 6 | 1 | 75 | 50 |
| 15 | PlayerCards 7 | 1 | 90 | 50 |
| 16 | PlayerCards 8 | 1 | 100 | 50 |
| 17 | DeviceC 1 | 1 | 85 | 35 |
| 18 | DeviceB 1 | 1 | 450 | 15 |
| 19 | DeviceA 1 | 1 | 2.000 | 5 |

`price` là **giá trong đơn vị của shop season-pass** (không phải IAP tiền thật); `stock` là số lượt mua còn lại.

### 3.9 Season reward arena (giữ nguyên từ #29)

`PVP_Manager.AllSeasonRewards` 10 dải liên tiếp 1 · 2–3 · 4–5 · 6–10 · 11–50 · 51–100 · 101–200 · 201–500 · 501–1.250 · 1.251–3.000, medal 2.000/1.000/500/300/200/150/100/80/50/20, gift type 1 (`GetSeasonRewards`, RVA `19915396`).

## 4. Kiểm chứng chéo

* **15/15** `InitializeArray`: `len(ints) == declared_length`, `declared_bytes ≥ 4·len`, `default_bytes < 4·len+16`.
* **Ground truth**: `GameDatas.cctor` phải trỏ field `7BB8C603…` (ordinal 368). Bản lệch-ordinal ra `7C2365F0…` (ordinal 369) và bị **test bắt** trước khi artifact được ghi.
* **551/551** slot string-literal có text (8 rỗng thật) — không có slot nào rơi vào "không tìm thấy".
* `TimeFreeRewardPack.timeAds = 43200.0` và `Popup_WatchVideos.duration = 900.0` chỉ đúng khi mô hình `movk`; khi bỏ `movk` chúng ra `1.3e-310` / `1.7e-310` (denormal) — đã sửa trong interpreter, không che bằng cách bỏ field.
* 28 contract mới (`tests/test_meta_rewards.py`), toàn repo **103 PASS**.

## 5. Không giải mã được (và chặn ở đâu)

| Mục | Lý do chặn |
|---|---|
| `MAX_LEVEL_BP` | **0 hit** trong `dump.cs`, **0 hit** trong `stringliteral.json` ⇒ không phải symbol managed của build này (khoá remote-config, không có trong `.so`). |
| Giá gift/quest/video theo từng người chơi | `Shop_Pack` là field instance; giá trị thật nằm trong board serialized + server. `.so` chỉ có bảng mặc định ở §3.7–3.8. |
| `ArenaManager.SeasonTimes`, `RankUpIndexs`, `RankDropIndexs` | null trong `.cctor`, gán trong `LoadRemoteConfigs` từ JSON remote ⇒ `MODEL_NOT_MEASURED runtime`. |
| `Board_BattlePassPro` / `BattlePassMission` | ngoài scope lượt này (45.308 B code) — chưa trích, chưa kết luận. |
| `Board_QuestRewards` nội dung quà | `.cctor` chỉ có `typeBox = 0`, `timeUpdate = 1`; quà dựng ở `ResfreshRewards`/`OpenBox` lúc chạy. |

## 6. Tái lập

```bash
python tools/recovery/meta_rewards_native.py --xapk windwings.xapk   # cần APK gốc (CI)
python tools/verify/meta_rewards.py                                   # -> datas/l2_535b0541_meta_rewards.json.gz
python -m unittest tests.test_meta_rewards -v
```

## 7. Bước rẻ tiếp theo

1. `Board_BattlePassPro.cctor` + `BattlePassMission` (bảng level/thưởng BP) — cùng pipeline, chỉ thêm 1 họ.
2. `Shop_Pack.GetListIndexRewards`/`GetValueByIndex` (RVA 20235736 / 20237060): dịch để gắn **index → field** cho `BoxRewardsRoot` (xoá cảnh báo "template box").
3. `allLogInRewardsRoot` 29 dòng: đối chiếu mốc ngày điểm danh với `keySysTime` của board login.
