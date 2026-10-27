# 134 — `PVP_Manager..cctor`: 5 bảng tĩnh + luật PvP mặc định (và sửa 42 → 43 dòng)

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Phần phụ thuộc server/nhịp chạy đều đánh dấu `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_pvp_manager_rules.json.gz` (4597 B, sha256 `5e8feef0dba53bbd863763c32531e2d8a8449b583e51310d6fc409a1e439a546`)
**Raw mới:** `reverse-engineering/raw/pvp-rules-535b0541/native.json.gz` — chỉ 2 cửa sổ 8 byte (`0x757E48`, `0x7579D0`), không đào thêm method nào.
**Báo cáo trước:** 127 (§6.1–6.5 đọc từng literal), 129/130/131 (key), 133 (bảng thưởng hunter).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Một trận PvP mặc định có mấy mạng? | **3** (`pvpMaxLife`) | `str d0,[x8,#0x28]` ← pool `0x757E48` = `03 00 00 00 dc 05 00 00` |
| Chết mất bao nhiêu điểm? | **1500** (`pointReduceDie`), cùng một store 8 byte | cùng cửa sổ trên |
| Thời lượng / bước thời gian? | **160 s** / **10 s** (`timePlay`/`timeStep`) | `str d1,[x8,#0x40]` ← pool `0x7579D0` = `a0 00 00 00 0a 00 00 00` |
| Bảng rank hiện bao nhiêu dòng? | **100** (`RankShowCount`) | `mov w10,#0x64` @ RVA 19936540 |
| `pvpTimeScale`, `IsOpen`, `pvpDatas`? | **1,0f**, **false**, **null** | `0x3F800000`, `strb wzr`, `str xzr` |
| Có mấy bảng tĩnh? | **5**: `AllSeasonRewards`, `TournamentAddStarPoints`, `TournamentRewardMedals`, `MaxRankStars`, `AllRewards` | 5 store vào `klass+0xB8` |
| Thưởng mùa theo dải rank? | **10 dải**, mỗi dải **1 gift `Gems`**: 2000/1000/500/300/200/150/100/80/50/20 | §3.1 |
| Điểm sao tournament? | `[25, 10, 5, −1, −6, −12]` | 6 `mov w1,#imm` inline |
| Medal tournament? | **14 dòng × 6 cột** | §3.3 |
| `AllRewards`? | **43 dòng** `PVPReward{rank, lvl, medal, gem}` — **không phải 42** | §5, đính chính |
| `MaxRankStars`? | chỉ **cấu trúc**: 10 mảng `int[]` dài `3,3,4,4,5,5,5,5,5,5` | §6 — giá trị **chưa** bind được |

**Một câu:** `.cctor` của `PVP_Manager` dựng đúng **5 bảng** và **8 hằng luật** bằng literal build; đếm theo lời gọi constructor/add trong thân hàm cho ra một đẳng thức khoá (`53 = 10 + 43`, `87 = 10+10+14+10+43`, `90 = 6 + 14×6`) — chính đẳng thức này lộ ra việc bảng `AllRewards` bị đếm thiếu **1 dòng** ở báo cáo 127.

---

## 1. Phương pháp — không đào native mới, chỉ pin 2 cửa sổ 8 byte

Báo cáo 127 đọc `.cctor` bằng cách "nhìn literal rồi chép". Báo cáo này đọc lại **toàn bộ** bằng máy, từ hai nguồn đã pin:

```text
PVP_Manager..cctor  RVA 19916640 · 19.944 B · sha256 74a43a93…
  ├─ raw meta-rewards-535b0541  → instructions (4.986 lệnh) + literals (64 điểm nạp)
  └─ raw pvp-rules-535b0541     → 2 cửa sổ rodata 8 byte (chỉ để chứng minh byte)
```

`literals[]` của raw ghi **byte thật** tại mỗi điểm `adrp + ldr`, nên mọi giá trị trong báo cáo này đọc được từ artifact, không phải từ ký ức của báo cáo trước. Hai cửa sổ `--rodata` mới chỉ để trả lời đúng một câu: "8 byte mà `str d0` ghi vào `+0x28` là gì".

| cửa sổ | VA (thập phân) | hex | đọc là 2 `int` |
|---|---|---:|---|
| `0x757E48` | 7700040 | `03000000dc050000` | **3**, **1500** |
| `0x7579D0` | 7698896 | `a00000000a000000` | **160**, **10** |

---

## 2. Luật PvP mặc định — 6 store, 8 field

`.cctor` kết thúc bằng 6 store vào khối static (`klass + 0xB8`). Hai store là `str d` **8 byte**, nên chúng ghi **hai field `int` liền nhau** trong một lệnh — không phải `double`:

| field | offset | kiểu (dump.cs) | giá trị | lệnh | RVA |
|---|---:|---|---:|---|---:|
| `pvpMaxLife` | `0x28` | `int` | **3** | `str d0,[x8,#0x28]` ← pool 7700040 | 19936548 |
| `pointReduceDie` | `0x2C` | `int` | **1500** | *cùng store* (nửa cao của `d0`) | — |
| `RankShowCount` | `0x30` | `int` | **100** | `str w10,[x8,#0x30]` | 19936552 |
| `pvpDatas` | `0x38` | `UserDataLeagues` | **null** | `str xzr,[x8,#0x38]` | 19936556 |
| `timePlay` | `0x40` | `int` | **160** | `str d1,[x8,#0x40]` ← pool 7698896 | 19936560 |
| `timeStep` | `0x44` | `int` | **10** | *cùng store* (nửa cao của `d1`) | — |
| `pvpTimeScale` | `0x48` | `float` | **1,0** | `str w9,[x8,#0x48]`, `w9 = 0x3F800000` | 19936564 |
| `IsOpen` | `0x4C` | `bool` | **false** | `strb wzr,[x8,#0x4C]` | 19936568 |

**Vì sao chắc chắn là 2 `int` chứ không phải `double`:** `dump.cs` khai `public static int pvpMaxLife; // 0x28` và `public static int pointReduceDie; // 0x2C` — một `double` tại `0x28` sẽ **nuốt** luôn `0x2C`, không thể cùng tồn tại. Bộ biên dịch gộp 2 hằng `int` liền nhau thành một literal 8 byte (`03 00 00 00 dc 05 00 00`) và phát một `str d0`. Đọc 8 byte đó như `double` ra `3,18e-311` (denormal) — rác, và là cái bẫy dễ mắc nhất ở đây.

**Đọc thành luật chơi:** trận mặc định **3 mạng**, mỗi lần chết **−1500 điểm**, đồng hồ **160 s** chia bước **10 s**, tốc độ thời gian **×1,0**, bảng rank hiển thị **100** dòng, `IsOpen = false` cho tới khi remote config bật. `pvpDatas` null ở `.cctor` — nó được `LoadRemoteConfigs` (RVA 19916080) điền sau ⇒ **dải rank thật là dữ liệu server**, không phải hằng build.

---

## 3. Năm bảng tĩnh

Mỗi bảng là một reference store vào `klass+0xB8`; cả 5 nằm trong `.cctor` và được dựng theo đúng thứ tự khai báo.

| bảng | kiểu | store RVA | nội dung |
|---|---|---:|---|
| `AllSeasonRewards` | `List<SeasonRewards>` | 19919772 | 10 dải rank |
| `TournamentAddStarPoints` | `List<int>` | 19920420 | 6 int |
| `TournamentRewardMedals` | `List<List<int>>` | 19930240 | 14 × 6 int |
| `MaxRankStars` | `List<int[]>` | 19931460 | 10 `int[]` (giá trị chưa bind) |
| `AllRewards` | `List<PVPReward>` | 19936528 | 43 dòng |

### 3.1 `AllSeasonRewards` — 10 dải liền kề, mỗi dải 1 gift

`SeasonRewards{rankStart @0x10, rankEnd @0x14, gifts @0x18}` (TypeDefIndex 898); `Gift{type @0x10, number @0x14}` (TypeDefIndex 1244), `GiftType.Gems = 1`.

| dải | 1 | 2–3 | 4–5 | 6–10 | 11–50 | 51–100 | 101–200 | 201–500 | 501–1250 | 1251–3000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `Gems` | **2000** | 1000 | 500 | 300 | 200 | 150 | 100 | 80 | 50 | 20 |

Dải đầu `1..1` là ngoại lệ duy nhất **không** nạp từ pool: `movi v0.2s, #1` sinh `(1,1)` tại chỗ (RVA 19917256), 9 dải còn lại `ldr d0` từ pool. Luật đọc (`GetSeasonRewards`, RVA 19915396, theo 127): quét theo thứ tự, trả gift list của phần tử đầu tiên thoả `rankStart ≤ rank+1 ≤ rankEnd`.

### 3.2 `TournamentAddStarPoints` = `[25, 10, 5, −1, −6, −12]`

Không đi qua blob: 6 phần tử được nhét thẳng bằng `mov w1,#imm` + `List<int>.AddWithResize` (`0x1B94D0C`). Ba số dương (25/10/5) và ba số âm (−1/−6/−12) ⇒ điểm sao cộng/trừ theo hạng, **không** phải bảng theo rank.

### 3.3 `TournamentRewardMedals` — 14 dòng × 6 cột

```
20 12  8 5 3 2     35 21 14 9 5 3     50 30 20 13 8 5    60 36 24 15 9 6
70 42 28 18 11 7    80 48 32 20 12 8   85 51 34 21 13 9   90 55 36 23 14 9
95 58 38 24 14 9    100 60 40 25 15 10 (5 dòng cuối trùng 100/60/40/25/15/10)
```

14 `new List<int>` + 14×6 `AddWithResize` (`0x1B94D0C`) + 14 lần `Add` vào list ngoài. Người đọc bảng là `PVP_Endgame.GetTournamentMedalReward(rank, index)` (RVA 19900768, theo 127) — nghĩa của chỉ số `rank 0..13` **không** nằm trong `.cctor`, nên ghi là `not_decoded`.

### 3.4 `AllRewards` — 43 dòng `PVPReward{rank, lvl, medal, gem}`

Mỗi dòng là **một cửa sổ pool 16 byte** nạp bằng `ldr q0` rồi `str q0,[x20,#0x10]`; `PVPReward` khai `rank @0x10, lvl @0x14, medal @0x18, gem @0x1C` (TypeDefIndex 897).

| rank | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lvl` có mặt | 1,2 | 0,1,2 | 0–3 | 0–3 | 0–4 | 0–4 | 0–4 | 0–4 | 0–4 | 0–4 |
| `medal` | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
| `gem` (chỉ `lvl=0`) | — | 200 | 600 | 900 | 1200 | 1400 | 1600 | 1800 | 1900 | 2000 |

Ba quy luật đo được, kiểm tự động trong verifier: `medal = 100 × (rank+1)` cho **cả 43** dòng; `gem ≠ 0` **đúng khi** `lvl = 0`; `rank` phủ đủ `0..9`.

---

## 4. Đẳng thức đếm — thứ làm bảng sai 1 dòng bị lộ

Đếm theo lời gọi trong từng cửa sổ của `.cctor`:

| cửa sổ | `Object..ctor` | `Gift..ctor` | `Add` (ref) | `Add` (int) | `List<int>..ctor` | `InitializeArray` |
|---|---:|---:|---:|---:|---:|---:|
| `AllSeasonRewards` | 10 | 10 | 20 | 0 | 0 | 0 |
| `TournamentAddStarPoints` | 0 | 0 | 0 | 6 | 1 | 0 |
| `TournamentRewardMedals` | 0 | 0 | 14 | 84 | 14 | 0 |
| `MaxRankStars` | 0 | 0 | 10 | 0 | 0 | 10 |
| `AllRewards` | **43** | 0 | **43** | 0 | 0 | 0 |
| **tổng** | **53** | 10 | **87** | **90** | 15 | **10** |

```
53 = 10 SeasonRewards + 43 PVPReward
87 = 10 gift + 10 season + 14 medal row + 10 star array + 43 reward
90 = 6 star points + 14 × 6 medal cell
10 = 10 MaxRankStars array
```

Bốn số này chỉ phụ thuộc **thân hàm**, không phụ thuộc cách đọc bảng ⇒ thêm/bớt một dòng là đẳng thức gãy. `verifier` assert cả bốn.

---

## 5. Đính chính: `AllRewards` là **43** dòng, không phải 42

| | báo cáo 127 | đo lại (134) |
|---|---|---|
| số dòng | 42 | **43** |
| dòng đầu | `[0,2,100,0]` | **`[0,1,100,0]`** |
| rank 0 có | chỉ `lvl=2` | **`lvl=1` và `lvl=2`** |

**Bằng chứng:** cửa sổ pool VA **7835632** (`hex 00000000010000006400000000000000`) được `str q0` vào object dựng tại **RVA 19931500**, rồi object đó được `Add` vào list y như 42 dòng còn lại; và `53 = 10 + 43` chỉ đúng khi dòng này được tính. Thiếu nó thì tổng `Object..ctor` là 53 nhưng bảng chỉ có 42 ⇒ lệch ngay.

**Hệ quả:** bảng tra thưởng PvP phải có `PVPReward(rank=0, lvl=1, medal=100, gem=0)`. Không có dòng đó thì rank 0 / level 1 rơi vào "không có thưởng" — sai.

---

## 6. `MaxRankStars` — cấu trúc chốt, giá trị **chưa** bind

10 lời gọi `RuntimeHelpers.InitializeArray` (`0x205B07C`) sau `newarr` với độ dài `3,3,4,4,5,5,5,5,5,5` ⇒ `List<int[]>` có **10 phần tử** (một mảng cho mỗi rank 0..9, khớp 10 rank của `AllRewards`).

**Bước chặn chính xác:** dữ liệu `fieldDefaultValues` mà raw pin được tại các `addend` của 10 blob là **metadata**, không phải giá trị `int`:

```
blob[0]  = 0d 00 00 80 00 00 00 00 | 0f 00 00 80 00 00 00 00 | 11 00 00 80 00 00 00 00
           → word 0x8000000D, 0x8000000F, 0x80000011 (bước +2, có bit 31) — token, không phải 13/15/17
```

`reverse-engineering/il2cpp/ia-resolved.json` chỉ phủ **17 method** và **không** có method nào của PvP ⇒ không có đường đọc thứ hai. Cần resolve `<PrivateImplementationDetails>` blob của class này (một pass metadata mới) trước khi được phép viết 44 con số.

---

## 7. Giới hạn — cái gì **không** phải hằng build

| mục | trạng thái |
|---|---|
| dải rank thật, `pvpDatas`, `IsOpen` lúc chạy | `LoadRemoteConfigs` (19916080) đọc Firebase ⇒ **MODEL_NOT_MEASURED runtime** |
| nhịp đồng hồ 160 s / bước 10 s có đúng thời gian thực không | hằng build; nhịp thực tế **MODEL_NOT_MEASURED runtime** |
| nghĩa chỉ số 14 dòng medal | không có trong `.cctor` ⇒ `not_decoded` |
| giá trị `MaxRankStars` | §6 |
| `pvpMaxLife` và `pointReduceDie` có bao giờ bị sửa **riêng lẻ** không | bị gộp một store 8 byte ⇒ build data luôn đi cặp; runtime **MODEL_NOT_MEASURED** |

---

## 8. Tái lập

```bash
python3 tools/verify/pvp_manager_rules.py          # ghi lại artifact, in sha256 + luật
python3 -m unittest tests.test_pvp_manager_rules   # 27 test
python3 tools/verify-claims.py --require AB,AO,AP  # needle APKD1/AI1
```

Verifier tự assert: 6 store vô hướng khớp `dump.cs`, 2 cửa sổ pool khớp **byte-for-byte** với raw `pvp-rules` (hex + `length == 8`), 10 dải season liền kề phủ `1..3000`, 43 dòng reward thoả `medal = 100×(rank+1)` và `gem ≠ 0 ⇔ lvl = 0`, 14×6 medal, 10 độ dài star array, và 4 đẳng thức đếm ở §4.

---

## 9. Tệp thay đổi

| tệp | nội dung |
|---|---|
| `reverse-engineering/raw/pvp-rules-535b0541/native.json.gz` | 2 cửa sổ rodata 8 byte (917 B) |
| `tools/verify/pvp_manager_rules.py` | đọc `.cctor` + 2 cửa sổ, `build_payload()`, tự assert |
| `datas/l2_535b0541_pvp_manager_rules.json.gz` | artifact 4597 B |
| `tests/test_pvp_manager_rules.py` | 27 test |
| `docs/apk-analysis/134-535b0541-pvp-manager-rules-tables.md` | báo cáo này |
| `tools/verify-claims.py`, `docs/spec/START_HERE.md` | needle `APKD1` 78→79 `.md`, `AI1` datas 111→112 |

`provenance:` STATIC-ONLY, original APK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, `libil2cpp.so` `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`, `dump.cs` `8996f7cb9ec9b8c0b9be7a81c746328e632189699a72beb53fdb7364fa168d5c`; nguồn: `meta-rewards-535b0541` + `pvp-rules-535b0541`. RVA ghi dạng thập phân trong artifact.
