# 132 — Nguồn kiếm key (`KeyCount0/1/2`): ai cộng, ai trừ, lưu ở đâu

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY — mọi con số dưới đây đọc từ 4 raw đã pin + `dump.cs`; phần *số lượng thật* một người chơi nhận được phụ thuộc dữ liệu pack/PvP ⇒ đánh dấu `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_key_sources.json.gz` (5325 B, sha256 `e97ca22a1c71f436f2d87a10c8acaa78cf42ceea8c9b8326ae7b1e83c5a91c3c`)
**Báo cáo trước:** 129 (index pack + đổi energy) · 130 (nút mở box `typeBox`) · 131 (nội dung 4 mảng `BoxKeyCost/KeyPrices/NumberRewards/AllTimeAds`)

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Key nằm ở đâu | 3 static `GameDatas`: `0x50` `0x54` `0x58` (int) | getter 20070740 / 20071068 / 20071396 |
| Mặc định khi chưa có save | **0** — getter thấy static `= −1` thì `PlayerPrefs.GetInt(key, 0)` | pattern `cmn w9, #1` → `GetInt` |
| Ghi có clamp âm? | Có: `bic w19, w19, w19, asr #31` = `max(value, 0)` | setter 20070940 / 20071268 / 20071596 |
| Có tự hồi theo thời gian? | **Không.** Không caller nào cộng bằng hằng số/timer | 35 method, 191 call site |
| Ai cộng | **21 màn thưởng** qua `SaveDataReward` (index 16/17/18) + **3 nút** cộng trực tiếp | bảng §4, §5 |
| Ai trừ | Chỉ nút mở box `Board_QuestRewards.OnPressedButtonOpenNow` (−30 mỗi box) | §6 |
| Trần chống cheat | `Key0 ≥ 1.000.000`, `Key1 ≥ 500.000`, `Key2 ≥ 100.000` ⇒ **ghi lại 0** | `IsHasCheatResources` 20068376 |
| Lưu | ghi ngay `PlayerPrefs.SetInt` mỗi lần set; đọc lại 3 getter khi build dictionary save | §9 |

**Một câu:** key là bộ đếm tiến độ *mua bằng thưởng*, không phải tài nguyên hồi theo giờ — chỉ 3 loại thưởng cộng (pack thưởng index 16/17/18, thanh quest, nút “thu hoạch” PvP), chỉ nút mở box trừ, và bị guard chống cheat reset về 0 nếu vượt trần.

---

## 1. Phạm vi & phương pháp

Bốn raw pin riêng (mỗi file một mục đích, không tái sinh file cũ):

| Raw | Nội dung | Dùng để trả lời |
|---|---|---|
| `reverse-engineering/raw/call-sites-535b0541/calls.json.gz` | quét **toàn bộ** `.text` tìm `bl`/`b` nhắm 6 accessor | *ai* gọi, kể cả lớp không nằm trong danh sách family |
| `reverse-engineering/raw/key-jump-535b0541/native.json.gz` | thân `TimeFreeRewardPack.SaveDataReward` + bảng nhảy `0x779C4A` (22 byte) | index pack nào chạm key nào |
| `reverse-engineering/raw/key-grant-535b0541/native.json.gz` | `Board_Quest`, `Board_PVP`, `Bonus_Quest`, `GameDatas` (448 method) | thân hàm cộng/trừ/guard/clamp |
| `reverse-engineering/raw/pvp-dispatch-535b0541/native.json.gz` | bảng nhảy `0x779DF0` (10 byte) | `rewardIndexs` của PvP rơi vào nhánh nào |

Quy mô quét: **6.765.005 word** trong 1 segment thực thi (`vaddr 16533228`, `filesz 27060020`), **191 call site** (bl+b) → **35 method / 31 lớp**. Tất cả RVA ghi dạng **thập phân**.

> Đây là quét **lời gọi**, không phải quét **ghi**. Một lớp nào đó gán thẳng `statics 0x50/0x54/0x58` bằng `str` (không qua setter) sẽ không xuất hiện — ghi vào `not_decoded`. Trong 4 lớp đã giải phẫu (`GameDatas`, `Board_Quest`, `Board_PVP`, `Bonus_Quest`) **không** có lệnh ghi trực tiếp nào ngoài setter (đã kiểm bằng mẫu `ldr …,#0xb8` + `str …,#0x50/0x54/0x58`).

---

## 2. Hai hàm truy cập — và cách chúng lưu

`GameDatas.get_KeyCount0` (RVA **20070740**, 200 B):

```
ldr   x9, [x8, #0xb8]     ; static fields
ldr   w9, [x9, #0x50]     ; KeyCount0
cmn   w9, #1              ; == -1 ?
b.ne  …                   ; có rồi thì trả luôn
bl    PlayerPrefs.GetInt(key, 0)   ; chưa có ⇒ nạp từ PlayerPrefs, mặc định 0
str   w19, [x9, #0x50]    ; cache lại
```

`GameDatas.set_KeyCount0` (RVA **20070940**, 128 B):

```
bic   w19, w19, w19, asr #31   ; w19 = max(value, 0)  ← chặn số âm
str   w19, [x8, #0x50]         ; ghi static
b     PlayerPrefs.SetInt(key, value)   ; ghi ngay xuống đĩa (tail call)
```

⇒ Ba hệ quả kiểm chứng được:

1. **Không có “key âm”**: mọi phép trừ đều bị setter kẹp về 0, nên UI “thiếu key” phải tự so sánh trước khi trừ (đúng như §6).
2. **Key là dữ liệu lưu bền**, không phải biến phiên: mỗi lần cộng/trừ là một lần ghi `PlayerPrefs`.
3. **Giá trị khởi tạo của profile mới = 0** (tham số `defaultValue` của `GetInt`), không phải 30/1.

Tên khoá lưu: ba literal `KeyCount0`, `KeyCount1`, `KeyCount2` nằm liền nhau trong `reverse-engineering/il2cpp/stringliteral.json` (`0x2BE1638`, `0x2BE1640`, `0x2BE1648`). **Chưa** chứng minh được slot ↔ literal (bảng metadata usage không có trong raw) — xem §10.

| Counter | getter (RVA) | setter (RVA) | static | kích thước getter/setter |
|---|---|---|---|---|
| `KeyCount0` | 20070740 | 20070940 | `0x50` | 200 / 128 B |
| `KeyCount1` | 20071068 | 20071268 | `0x54` | 200 / 128 B |
| `KeyCount2` | 20071396 | 20071596 | `0x58` | 200 / 128 B |

---

## 3. Bảng phân vai 35 method (191 call site)

| Vai | Method | Lớp | Call site | Nghĩa |
|---|---|---|---|---|
| `grant_via_pack_value` | 21 | 21 | 126 | mỗi màn thưởng một bản `SaveDataReward` |
| `grant_direct` | 3 | 3 | 5 | 3 nút cộng trực tiếp (§5) |
| `spend` | 2 | 2 | 15 | nút mở box + closure của nó (§6) |
| `cheat_guard` | 1 | 1 | 6 | `IsHasCheatResources` (§8) |
| `serialization` | 1 | 1 | 3 | `DataPrefs.GetDictionaryKeyIntResourceDatas` (§9) |
| `display_or_state` | 7 | 7 | 42 | 6 hàm chỉ đọc + 1 (`ResfreshRewards`) |

`display_or_state` gồm: `Board_Quest.OnEnable` 19954300, `Board_Quest.IsFocus` 19969452, `Board_Quest.<AdsTimer>d__77.MoveNext` 19977604, `Board_Quest.<UpdateKey0>d__34.MoveNext` 19980832, `<UpdateKey1>d__38` 19981872, `<UpdateKey2>d__42` 19982936, `Board_QuestRewards.ResfreshRewards` 19985884. **Tất cả đều chỉ `bl get_KeyCountN`, không một lệnh `set`** ⇒ không có vòng hồi key theo thời gian hay theo nhịp coroutine.

---

## 4. Ai cộng (1/2): 21 màn thưởng qua bảng nhảy `SaveDataReward`

`TimeFreeRewardPack.SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0)`
(RVA **19188220**, 1108 B, bảng nhảy VA **0x779C4A** = 7.839.818, 22 byte):

```
cmp  w23, #0x15        ; _index > 21 ⇒ nhánh mặc định
b.hi default
adrp/add x9, #0x779C4A ; bảng byte
ldrb w11, [x9, x8]
add  x10, x10, w11, lsl #2   ; pad = 0x124ca98 + 4*byte
br   x10
```

Bảng 22 byte: `22 34 0f 0f 0f 0f 46 56 00 00 00 00 00 72 7c 8a 9e be be ce 6c de`
⇒ index → pad:

| index | 0 | 1 | 2–5 | 6 | 7 | 8–12 | 13 | 14 | 15 | **16** | **17** | **18** | 19 | 20 | 21 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| đích | `get_Coins` | `get_Gems` | `GetItemCount` | `get_OverDrive`+set | `get_Energy` | *mặc định* | `GetDroneExp`+set | `GetDroneCards`+set | `GetPlayerCards` | **`KeyCount0`** | **`KeyCount1`** | **`KeyCount2`** | `get_WingCoins`+set | *mặc định* | `get_TimeRewards`+set |

Ba khối key có dạng **giống hệt nhau** (đây là bằng chứng “cộng đúng bằng tham số”, không cộng hằng số):

```
0x124cd10 bl get_KeyCount0
0x124cd30 add w0, w0, w19      ; w19 = _value (mov w19, w2 ở đầu hàm)
0x124cd4c b  set_KeyCount0      ; tail call
```

(`KeyCount1` pad 19189072, `KeyCount2` pad 19189136; cả 3 đều `adds_value = true`.)

**index 20 và 8–12 rơi vào nhánh mặc định** (`0x124cc48` = `ret` sau khi khôi phục thanh ghi): pack value thuộc nhóm đó **không** cộng gì — chi tiết này quan trọng khi đọc dữ liệu pack, tránh suy luận “mọi index đều là một loại tiền”.

21 lớp có `SaveDataReward` (mỗi lớp = một màn hình thưởng), RVA thập phân:

| Lớp | RVA | Lớp | RVA |
|---|---|---|---|
| `TimeFreeRewardPack` | 19188220 | `Board_GiftLogin` | 19501572 |
| `Board_Endgame` | 19355604 | `Board_Maps` | 19630172 |
| `Board_EventSeasonPass` | 19459160 | `Popup_SeasonRewards` | 19894520 |
| `Board_QuestRewards` | 19992704 | `BoardGiftCode` | 20202452 |
| `Gift_Pack` | 20272180 | `Popup_FirstGiftFree` | 20284504 |
| `Popup_PremiumDailyRewards` | 20292864 | `Popup_WatchVideosOld` | 20328216 |
| `Popup_WeekSales` | 20338916 | `Shop_Gifts` | 20369416 |
| `Board_Vip` | 20652148 | `Popup_HolidayGift` | 20742900 |
| `Board_BattlePass` | 22857788 | `Board_BattlePassPro` | 22893528 |
| `ItemBuffetPack` | 23050520 | `ShipBuffetPack` | 23086144 |
| `ShipSalePack` | 23102588 | | |

Đọc theo nhóm nguồn: **quest/box** (`Board_QuestRewards`), **đăng nhập & quà tặng** (`Board_GiftLogin`, `Popup_FirstGiftFree`, `Popup_HolidayGift`, `Shop_Gifts`, `Gift_Pack`), **xem quảng cáo** (`Popup_WatchVideosOld`, `TimeFreeRewardPack`), **battle pass / season** (`Board_BattlePass`, `Board_BattlePassPro`, `Board_EventSeasonPass`, `Popup_SeasonRewards`), **mã quà tặng**, **map/endgame**, **VIP**, **khuyến mãi tuần**, **buffet tàu/item**.
Bản thân *giá trị* `_value` đến từ dữ liệu pack (không nằm trong mã) ⇒ `MODEL_NOT_MEASURED runtime`.

---

## 5. Ai cộng (2/2): ba nút cộng trực tiếp

### 5.1 Thanh quest — `Board_Quest.<>c__DisplayClass57_0.<OnQuestCollect>g__Collect|2`
RVA **19965788** (1196 B). Với mỗi thanh quest vừa hoàn thành, `Bonus_Quest` (TypeDefIndex 916) mang 3 field:

| field | offset | cộng vào |
|---|---|---|
| `key0` | `0x10` | `set_KeyCount0(get_KeyCount0() + bonus.key0)` |
| `key1` | `0x14` | `set_KeyCount1(get_KeyCount1() + bonus.key1)` |
| `key2` | `0x18` | `set_KeyCount2(get_KeyCount2() + bonus.key2)` |

Mỗi khối chỉ chạy khi giá trị `>= 1` (`cmp w8, #1; b.lt skip`) — đây cũng là lý do một thanh quest có thể **không** cho key nào.
Sau khi cộng, nhãn được vẽ lại dạng `"<keyCountN>/<BoxKeyCost[N]>"` (khối 0 đọc `BoxKeyCost[0]`, khối 1 đọc phần tử 1 tại `+0x24`, khối 2 đọc phần tử 2 tại `+0x28`) — khớp mảng 30/30/30 của báo cáo 131; hàm vẽ nhãn tương ứng là `Board_Quest.CheckKey0` (19954584), `CheckKey1` (19954648), `CheckKey2` (19954712).
Cuối hàm: `GetQuestCollectIndex(questIndex)` (19965560) `+1` → `SetQuestCollectIndex` (19971460) → `Board_Quest.ResfreshQuests` (19956632).

**Cảnh báo đo được:** hiệu ứng bay chữ dùng `w3 = Board_Quest.keyMuliple (0xa0) * bonus.keyN`, còn **giá trị lưu chỉ tăng `bonus.keyN`**. Hai đại lượng này chỉ bằng nhau khi `keyMuliple == 1`; giá trị thật của `keyMuliple` do scene gán lúc chạy ⇒ `MODEL_NOT_MEASURED runtime`. Báo cáo này **không** kết luận đây là bug, chỉ ghi nhận hai công thức khác nhau.

### 5.2 Nút “thu hoạch tất cả quest” — `Board_Quest.OnPressedButtonCAQCollect(Transform)`
RVA **19955408** (588 B):

```
gate : GetQuestValue(999) == getQuestActiveCount()    ; 19955996 vs 19956160
bonus: Board_Quest.bonusClearAllQuests (static 0x28) → Bonus_Quest.key2 (0x18)
if key2 >= 1: set_KeyCount2(get_KeyCount2() + key2)
nhãn: "key/BoxKeyCost[2]"  → CheckKey2()  (19954712)
xong : SetQuestValue(999, -1) (19956464) → ResfreshQuests() (19956632)
```

Thanh ghi `999` là một bản ghi “số quest đang hoạt động”: nút chỉ mở khi `GetQuestValue(999)` bằng `getQuestActiveCount()`, và sau khi nhận thì ghi lại `-1` (đánh dấu đã thu).

⇒ Nút này **chỉ** cộng `KeyCount2`, và cộng **theo cấu hình bonus**, không theo số quest đã xong. (Bản thân `key2` là dữ liệu `Bonus_Quest`, không phải hằng số trong mã.)

### 5.3 PvP hunter — `Board_PVP.OnClickHunterCollect(WinPoint)`
RVA **19792936** (1092 B):

```
i = point.transform.GetSiblingIndex()
if i >= Board_PVP.SeasonProgress or IsCollected(i): return      ; đã nhận / chưa tới mốc
SetPointActive(); PlayerPrefs.SetInt(prefix+index, 1); child.SetActive(false)
type   = rewardIndexs[i/2]   (0x198)
amount = rewardValues[i/2]   (0x1A0)
switch (type - 14)  qua bảng 0x779DF0 (10 byte)
```

Bảng `0x779DF0` = `5f 8a 00 00 a3 00 00 00 00 af`, pad = `0x12e0518 + 4*byte`:

| type | 14 | 15 | 16 | 17 | **18** | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| nhánh | `SetDroneCards` | `SetPlayerCards` | — | — | **`set_KeyCount2`** | — | — | — | — | `set_PvPMedal` |

Bốn type “sống” khớp đúng tên `GiftType` cùng số (14 `DroneCards`, 15 `PlayerCards`, 18 `Key2`, 23 `PVPMedal`) ⇒ chuỗi PvP hunter **không bao giờ** cộng `Key0`/`Key1` (16/17 không có nhánh), chỉ `Key2`, và lượng cộng là `rewardValues[i/2]` do dữ liệu mùa quyết định (`MODEL_NOT_MEASURED runtime`).

---

## 6. Ai trừ: chỉ nút mở box

`Board_QuestRewards.OnPressedButtonOpenNow` (RVA **19989112**) và closure `<>c__DisplayClass21_0.<OnPressedButtonOpenNow>b__0` (RVA **19994568**) là **toàn bộ** 15 call site mang vai `spend`:

```
typeBox = Board_QuestRewards.typeBox (static 0x0)
need    = BoxKeyCost[typeBox]        (0x38, = 30/30/30 ← báo cáo 131)
if owned >= need: set_KeyCountN(owned - need)     ; N = typeBox
else           : price = KeyPrices[typeBox] * (need - owned)   ; 0x40 = 6/20/100
```

Vì setter đã kẹp âm, nhánh “không đủ key” **không** gọi setter mà chỉ tính `price` để hiện popup mua — đúng với 2 closure field `price (0x18)` và `keyMiss (0x1c)` đã thấy ở báo cáo 130.

---

## 7. Không có nguồn nào khác?

Ba kiểm tra loại trừ, tất cả đều dương tính theo nghĩa “không tìm thấy”:

1. **Không timer**: 7 method `display_or_state` chỉ đọc; `AdsTimer`/`UpdateKey0..2` là coroutine vẽ nhãn.
2. **Không phải logic “hồi theo thời gian”**: không call site nào có dạng `add w0, w0, #hằng`.
3. **Không có điều kiện đặc biệt nào dùng key**: ngoài 6 hàm trên, `IsHasCheatResources` là chỗ duy nhất còn lại (§8).

Hệ quả thiết kế: key là **gate tiến độ** (mở 3 box 30 key), không phải tiền tệ mua bán — không shop nào nhận key, không có chỗ nào tiêu key ngoài `open box`.

---

## 8. Trần chống cheat — `GameDatas.IsHasCheatResources` (RVA 20068376)

Hàm này là một chuỗi `if (resource >= cap) { set(resource, reset); dirty = true; }`:

| tài nguyên | ngưỡng | ghi lại | nguồn ngưỡng |
|---|---|---|---|
| `Gems` | static `0x10` | 0 | field (không phải hằng) |
| `Coins` | static `0x0c` | 0 | field |
| `Energy` | 1.600.000.000 (`0x5F50E100`) | 100 | hằng |
| `WingCoins` | 1.600.000.000 | 0 | hằng |
| **`KeyCount0`** | **1.000.000** (`0xF4240`) | **0** | hằng |
| **`KeyCount1`** | **500.000** (`0x7A120`) | **0** | hằng |
| **`KeyCount2`** | **100.000** (`0x186A0`) | **0** | hằng |

Ngưỡng key nhỏ hơn hẳn 3 bậc so với tiền tệ, và **reset về 0** (không phải kẹp về ngưỡng) ⇒ đây là phát hiện sửa save, không phải “giới hạn hiển thị”. Hàm trả `true` nếu đã sửa ít nhất một tài nguyên.

---

## 9. Lưu & khôi phục

* **Ghi**: mỗi `set_KeyCountN` → `PlayerPrefs.SetInt("KeyCountN", value)` (§2). Không có buffer, không có “save on exit”.
* **Đọc để lưu**: `DataPrefs.GetDictionaryKeyIntResourceDatas` (RVA **19068296**) gọi cả 3 getter để dựng dictionary `string → int` cho tài nguyên (3 call site, chỉ `bl get_…`).
* **Khôi phục**: getter tự nạp lazy từ `PlayerPrefs` khi cache `= −1` (§2) — đây chính là đường khôi phục cho key, không cần hàm load riêng. Một *đường khôi phục khác* ghi trực tiếp static sẽ không xuất hiện trong phép quét lời gọi; đã ghi vào `not_decoded`.

---

## 10. Cái chưa đo (và vì sao không bịa)

| Hạng mục | Bước chặn |
|---|---|
| `_value` thật của từng pack (21 màn) | giá trị đến từ dữ liệu pack lúc chạy, không nằm trong `.text`; `MODEL_NOT_MEASURED runtime` |
| Lượng key của từng mốc PvP | `Board_PVP.rewardValues` (0x1A0) là mảng instance nạp lúc chạy; bảng nhảy chỉ chứng minh **loại** |
| `Bonus_Quest.key0/1/2` cụ thể | là dữ liệu `Bonus_Quest` (ScriptableObject/JSON), không phải hằng trong mã |
| `keyMuliple` thật | field instance `0xa0`, scene gán; `MODEL_NOT_MEASURED runtime` |
| Slot ↔ literal `KeyCount0/1/2` | bảng metadata usage cho string slot không có trong raw đã pin |
| Người ghi static **không** qua setter | phép quét là quét lời gọi; một `str` trực tiếp ở lớp khác sẽ không lộ ra |

---

## 11. Tái lập

```bash
python3 tools/verify/key_sources.py        # ghi lại datas/l2_535b0541_key_sources.json.gz
python3 -m unittest tests.test_key_sources -q
```

Test khoá: sha256 artifact, 6 nguồn + sha của chúng, 191 hit / 35 method, offset static 0x50/0x54/0x58, clamp âm, lazy-load mặc định 0, trần 1e6/5e5/1e5 → 0, index 16/17/18 → `KeyCount0/1/2`, 3 nút cộng trực tiếp, 21 `SaveDataReward`, PvP type 18 → `KeyCount2` và 16/17 chết, và “không có caller set nào là timer”.

`provenance:` SHA-256 của 6 nguồn nằm trong `datas/l2_535b0541_key_sources.json.gz → provenance.sources`; XAPK gốc `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, `libil2cpp.so` `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.
