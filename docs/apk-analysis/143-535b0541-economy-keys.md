# 143 — Khoá save của `GameDatas`: 21 khoá `PlayerPrefs`, 48 lần đọc, 42 lần ghi

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY; con số lưu trong máy là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_economy_keys.json.gz` (3993 B, sha256 `c655860a23529ab8954d69311948735d481aff638d090095eccfc13f3a6eb8f8`)
**Báo cáo trước:** 142 (bốn getter tiền tệ — báo cáo này **đính chính** một `not_decoded` của 142), 128 (`GameDatas..cctor` sentinel), 141 (`GameConfig`), CM4 (`opening_persistence`: hai store).
**Verifier:** `tools/verify/economy_keys.py` · **Test:** `tests/test_economy_keys.py` (28 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| 142 nói "không đọc được chuỗi khoá"? | **sai** — mọi ô đều có `slot_ref.addend` tra được trong `stringliteral.json` | §1, §6 |
| Khoá của coins? | **`GCoins`** (không phải `Coins`) | literal 46002640 |
| Khoá của gems / stars / wingCoins? | `Gems` / `StarCount` / `WingCoins` | literal 46003168 / 46029696 / 46045488 |
| `GameDatas` dùng bao nhiêu khoá `PlayerPrefs`? | **21**, mỗi khoá có **cả đọc và ghi** | §2, §3 |
| Bao nhiêu lời gọi? | **90** = 48 `GetInt` (`bl`) + 42 `SetInt` (tail `b`) | §2 |
| Vì sao quét `bl` không thấy phía ghi? | cả 42 phía ghi là **tail call** | §2 |
| Có khoá nào khác tên property? | `ControlType` ↔ `TypeControl`; `PREMIUM_DAILY_COLLECTED` ↔ `IsCollectPremiumDailyGift` | §3, §5 |
| 6 property không dùng `PlayerPrefs`? | dùng store riêng **`PlayerPreferences`** (RVA 20912644) | §4 |
| Store riêng lớn cỡ nào? | **174** lời gọi ở 4 raw, 42 khoá ứng viên — **chưa chốt khoá** | §4 |

**Một câu:** kinh tế `GameDatas` nằm trong **21 khoá `PlayerPrefs`** với **cả hai chiều** (48 `GetInt` + 42 `SetInt`), và phía ghi chỉ lộ ra khi quét cả **tail call** — đây là lý do 142 thấy "không có khoá nào" rồi dừng lại.

---

## 1. Đính chính 142: literal **có** `addend`

142 ghi trong `not_decoded`: *"các ô string `0x2ADC0B8/0xC8/0xE0/0x1D0` không có `addend` gắn với một deref đã pin"*. Sai ở chỗ 142 chỉ ghi **địa chỉ ô** mà không tra `slot_refs`:

| Ô | `slot_va` | `slot_ref` gần nhất | `addend` | Chuỗi |
|---|---:|---:|---:|---|
| `0x2ADC0E0` | 44941536 | 20069716 | 46002640 | `GCoins` |
| `0x2ADC0B8` | 44941496 | 20069100 | 46003168 | `Gems` |
| `0x2ADC0C8` | 44941512 | 20076128 | 46029696 | `StarCount` |
| `0x2ADC1D0` | 44941776 | 20070496 | 46045488 | `WingCoins` |

`slot_refs.rva` trỏ đúng **lệnh deref** của ô khoá (`ldr x0,[xK]`), và `slot_va` **bằng đúng** `adrp page` + `ldr #offset` trong asm — nên quy tắc "lấy `slot_ref` string gần nhất trước lời gọi" là hợp lệ. Khoảng cách đo được: 46 lời gọi đọc cách 4 lệnh, 2 cách 36 (nhánh thứ hai của `get_WingCoins`), 40 lời gọi ghi cách 12, 2 cách 8.

---

## 2. Hai chiều, và cái bẫy tail call

```asm
; đọc — get_Coins (20069516): bl
20069696  adrp x8, #0x2adc000
20069700  ldr  x8, [x8, #0xe0]      ; ô khoá 44941536 = "GCoins"
20069716  ldr  x0, [x8]
20069720  bl   #0x277cca0           ; PlayerPrefs.GetInt(key, default)

; ghi — set_Coins (20069860, 124 B): tail call
20069908  ldr  x0, [x0, #0xe0]      ; cùng ô khoá 44941536
20069964  str  w19, [x8, #0x44]     ; GameDatas.coins = value
20069968  ldr  x0, [x21]            ; key
20069980  b    #0x277cc10           ; PlayerPrefs.SetInt(key, value)  ← `b`, không `bl`
```

| Phía | API | RVA | Số lời gọi | Kiểu gọi |
|---|---|---:|---:|---|
| đọc | `PlayerPrefs.GetInt` | 41405600 | **48** | `bl` |
| ghi | `PlayerPrefs.SetInt` | 41405456 | **42** | **tail `b`** |

Tổng **90** lời gọi, chia đều hai raw (`key-grant` 45 · `meta-rewards` 45). Quét chỉ `bl` ⇒ thấy 48 đọc và **0** ghi — đúng kết cục của 142.

---

## 3. Bảng 21 khoá (mỗi khoá có cả đọc và ghi)

| Khoá | literal | ô (`slot_va`) | getter RVA | setter RVA |
|---|---:|---:|---:|---:|
| `ArenaMedal` | 45983600 | 44941936 | 20084804 | 20085004 |
| `ArenaPoints` | 45983608 | 44964128 | 20084148 | 20084348 |
| `AutoChangePlayer` | 45985160 | 44964072 | 20078040 | 20078240 |
| `AutoChangePosition` | 45985168 | 44964080 | 20078364 | 20078564 |
| `CampaignPoints` | 45987424 | 44964136 | 20084476 | 20084676 |
| `CoinEvent1` | 45987704 | 44964048 | 20077064 | 20077264 |
| `ControlType` | 45988752 | 44964056 | 20077392 (`get_TypeControl`) | 20077592 |
| `Energy` | 45989928 | 44941768 | 20069984 | 20070184 |
| `GCoins` | 46002640 | 44941536 | 20069516 (`get_Coins`) | 20069860 |
| `Gems` | 46003168 | 44941496 | 20068904 | 20069244 |
| `GraphicsLevel` | 46003712 | 44964088 | 20079032 | 20079232 |
| `KeyCount0` | 46016056 | 44941760 | 20070740 | 20070940 |
| `KeyCount1` | 46016064 | 44941800 | 20071068 | 20071268 |
| `KeyCount2` | 46016072 | 44941784 | 20071396 | 20071596 |
| `OverDrive` | 46020648 | 44941792 | 20075604 | 20075804 |
| `PvPMedal` | 46023512 | 44941912 | 20085132 | 20085332 |
| `StarCount` | 46029696 | 44941512 | 20075932 | 20076272 |
| `TimeRewards` | 46038928 | 44941752 | 20076736 | 20076936 |
| `UILeftRight` | 46040432 | 44964064 | 20077716 | 20077916 |
| `VipPoints` | 46044896 | 44941544 | 20079604 | 20080008 |
| `WingCoins` | 46045488 | 44941776 | 20070312 | 20070612 |

`GCoins` / `Gems` / `StarCount` mỗi khoá có **4** lần đọc (hai nhánh `companyName` × hai raw) — khớp 142 §5; `WingCoins` chỉ **2** vì setter/getter của nó không nhân đôi nhánh.

Bốn khoá tiền tệ nối trực tiếp sang 142: `GCoins` ← mặc định **68999**, `Gems` ← **500**, `StarCount` ← **0**, `WingCoins` ← **999999/0** (142 §5), và bốn `cache` tương ứng `0x44 / 0x48 / 0x4C / 0x5C`.

---

## 4. Store thứ hai: `PlayerPreferences` (không phải Unity)

6 property của `GameDatas` **không** đi qua `PlayerPrefs`; chúng tail-call `PlayerPreferences.SetInt` (RVA **20912644**, `0x13F1A04`) — store JSON riêng của game (`GetRawData` / `SaveToDisk` / `LoadFromDisk`):

| Property | RVA setter | Khoá |
|---|---:|---|
| `Compensation` | 20068264 | `Compensation` |
| `IsCollectPremiumDailyGift` | 20080256 | `PREMIUM_DAILY_COLLECTED` |
| `CanCollectPremiumGift` | 20083580 | `CanCollectPremiumGift` |
| `IsPremiumTag` | 20083064 | `IsPremiumTag` |
| `CountThroughAds` | 20083816 | `CountThroughAds` |
| `LastArenaPoints` | 20084036 | `LastArenaPoints` |

Quét cùng quy tắc trên store này cho **174** lời gọi ở **4** raw (`meta-rewards` 74 · `key-grant` 49 · `arena-pvp` 41 · `box-draw` 10): `SetInt` 63 · `GetInt` 54 · `SetString` 32 · `GetString` 23 · `DeleteKey` 2. **Nhưng khoá chưa chốt**: 42 khoá ứng viên, chỉ **6** nằm trong 8 lệnh tính từ `slot_ref`, **11** lời gọi không quy được khoá nào (khoá ghép chuỗi theo index, và đối số mặc định cũng là string). Vì vậy báo cáo này **chỉ đếm** store đó và để việc chốt khoá cho một lượt riêng — không suy ra tên.

---

## 5. Hai chỗ tên khoá ≠ tên property

| Property | Khoá | Ghi chú |
|---|---|---|
| `GameDatas.TypeControl` | **`ControlType`** | đảo thứ tự từ |
| `GameDatas.IsCollectPremiumDailyGift` | **`PREMIUM_DAILY_COLLECTED`** | khác hẳn tên, store `PlayerPreferences` |

Đây là lý do bảng khoá phải đọc từ literal chứ không suy từ tên property.

---

## 6. `not_decoded` (3 mục)

| Mục | Bước chặn |
|---|---|
| Giá trị lưu của 21 khoá | nằm trong save của máy, không nằm trong APK — **`MODEL_NOT_MEASURED runtime`** |
| Khoá của 174 lời gọi store `PlayerPreferences` | khoá ghép theo index + đối số mặc định là string ⇒ quy tắc "slot_ref gần nhất" không đủ; cần pass theo dõi thanh ghi từng method |
| `PlayerPrefs` `GetString/GetFloat/SetString/DeleteKey` | 13 API đã resolve RVA, nhưng trong 8 raw đã pin chỉ có `GetInt`/`SetInt`; các call site còn lại nằm ngoài họ method đã pin |

---

## 7. Tái lập

```bash
python3 tools/verify/economy_keys.py              # in bytes/sha256 + đếm khoá/lời gọi/API
python3 -m unittest tests.test_economy_keys        # 28 test
python3 tools/verify-claims.py --require AB,AO,AP
```

`evidence: STATIC_ONLY_ORIGINAL_APK` · nguồn: 8 raw `reverse-engineering/raw/*/native.json.gz`,
`reverse-engineering/il2cpp/stringliteral.json` (chữ của 21 khoá), `reverse-engineering/il2cpp/dump.cs.gz`
(RVA của 13 API `PlayerPrefs` + 10 API `PlayerPreferences` + danh sách setter).

---

`provenance:` APK gốc `535b0541` → `libil2cpp.so` → raw `key-grant` + `meta-rewards` (24 + 24 method `GameDatas`) → `slot_refs.addend` → `stringliteral.json` → verifier → artifact 3993 B `c655860a…` → 28 test. Không emulator/probe/device.
