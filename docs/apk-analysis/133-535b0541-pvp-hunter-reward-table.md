# 133 — Bảng thưởng PvP hunter: 6 mốc, mốc cuối là mốc trả key

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Cái gì cần dữ liệu scene/server đều đánh dấu `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_pvp_hunter_reward_table.json.gz` (2123 B, sha256 `4649f273aacb59fa063e691d5d2726aab932bc8da48174668963887fa5bdfa79`)
**Báo cáo trước:** 132 (nguồn kiếm key) — báo cáo này đóng dòng `not_decoded` "PvP stage reward types and amounts" **một nửa**: loại thưởng đã chốt, số lượng thì chưa.

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| PvP hunter có mấy mốc thưởng? | **6 slot** × 2 marker = 12 marker, chỉ marker **lẻ** bấm được | `Board_PVP..ctor` (19796420) + `SetupHunters` (19791640) |
| Mỗi mốc thưởng gì? | `[PVPMedal, Gcoins, DroneCards, Gems, PlayerCards, **Key2**]` | blob `rewardIndexs` = `[23, 0, 14, 1, 15, 18]` |
| Mốc nào trả key? | **slot 5** (marker 11) → `set_KeyCount2` | `OnClickHunterCollect` (19792936) |
| Mốc nào trả `Key0`/`Key1`? | **Không có** — 16/17 rơi nhánh `ret` | bảng nhảy `0x779DF0` |
| Số lượng mỗi mốc | **chưa chốt** (`rewardValues` blob chưa bind) | §7 |
| Điều kiện nhận | `marker < SeasonProgress` và `!IsCollected(marker)` | §5 |

**Một câu:** chuỗi PvP hunter có đúng 6 phần thưởng theo thứ tự cố định trong mã, mốc **cuối cùng** là mốc duy nhất cộng key (và chỉ cộng `KeyCount2`); số lượng từng mốc nằm trong một mảng `int[6]` mà báo cáo này **không** gán được tên blob ⇒ ghi đúng bước chặn, không đoán.

---

## 1. Phương pháp

Không đào native mới: `Board_PVP` đã nằm nguyên trong raw `key-grant-535b0541` (273 method). Báo cáo này thêm **một nguồn phi-native** đã có sẵn trong repo — `reverse-engineering/il2cpp/field-defaults.json` (`fieldDefaultValues` v31, 10.493 field) — vì `InitializeArray` đọc dữ liệu từ metadata, không từ `.so`.

Chuỗi suy luận:

```
Board_PVP..ctor (19796420)
  ├─ new int[6]  → bl RuntimeHelpers.InitializeArray (0x205B07C) → str [x19,#0x198]
  ├─ new int[6]  → InitializeArray                              → str [x19,#0x1A0]
  ├─ new float[6]→ InitializeArray                              → str [x19,#0x1A8]
  ├─ new int[6]  → InitializeArray                              → str [x19,#0x208]
  ├─ new int[6]  → InitializeArray                              → str [x19,#0x210]
  └─ new int[6]  → InitializeArray                              → str [x19,#0x218]
```

6 lời gọi `0x205B07C` (`RuntimeHelpers.InitializeArray(Array, RuntimeFieldHandle)`), mỗi lời gọi ngay sau `mov w1, #6` + `bl 0x110D09C` (newarr), và mỗi lời gọi có một `str` ghi vào field instance trong 1–4 lệnh kế tiếp.

| field | offset | kiểu khai báo | `InitializeArray` RVA |
|---|---|---|---|
| `rewardIndexs` | `0x198` | `int[]` | 19796684 |
| `rewardValues` | `0x1A0` | `int[]` | 19796716 |
| `rewardScales` | `0x1A8` | `float[]` | 19796748 |
| `allBetCoinValues` | `0x208` | `int[]` | 19796804 |
| `allBetGemValues` | `0x210` | `int[]` | 19796836 |
| `allBetMedalValues` | `0x218` | `int[]` | 19796876 |

(offset khớp đúng khai báo trong `dump.cs`, TypeDefIndex 852.)

---

## 2. Chốt `rewardIndexs` bằng nội dung — và vì sao chỉ có một ứng viên

Bảng metadata usage (slot `0x2AE0008` → field token) **không** nằm trong dữ liệu đã pin, nên không thể đọc thẳng "blob nào là `rewardIndexs`". Thay vào đó dùng hai ràng buộc **độc lập**:

1. **Độ dài**: `new T[6]` ⇒ blob 6 phần tử int = 24 byte, được đệm thành **32 byte** trong `fieldDefaultValues` (cùng quy ước với 4 mảng của báo cáo 131: 12 byte → 16 byte raw).
2. **Miền giá trị**: `OnClickHunterCollect` chỉ xử lý đúng 6 id thưởng — 4 id trong bảng nhảy `0x779DF0` (`14 → SetDroneCards`, `15 → SetPlayerCards`, `18 → set_KeyCount2`, `23 → set_PvPMedal`) và 2 id xử lý trước switch (`0 → set_Coins`, `1 → set_Gems`). Một mảng 6 phần tử "loại thưởng" gần như buộc phải nằm trong `{0, 1, 14…23}`.

Quét **toàn bộ** `<PrivateImplementationDetails>` (982 blob): có **48** blob 6-int (32 byte raw, 2 int đệm bằng 0). Trong 48 blob đó, **đúng 1** blob có cả 6 giá trị nằm trong miền trên:

```
data_index 30944 · field_index 17001
raw  17 00 00 00 00 00 00 00 0e 00 00 00 01 00 00 00 0f 00 00 00 12 00 00 00 00 00 00 00 00 00 00 00
     → [23, 0, 14, 1, 15, 18]
```

Ba lớp kiểm chéo:

* **Tính duy nhất**: 1/48 (và 1/982 nếu tính mọi blob) — không phải chọn tay.
* **Bao trùm**: tập giá trị `{23, 0, 14, 1, 15, 18}` trùng **đúng** tập id mà hàm thu có nhánh xử lý — kể cả `0`/`1` vốn không đi qua bảng nhảy.
* **Nhãn khớp enum**: 4 id sống khớp tên `GiftType` cùng số (14 `DroneCards`, 15 `PlayerCards`, 18 `Key2`, 23 `PVPMedal`), `0` = `Gcoins`, `1` = `Gems`.

> Đây là **nhận dạng bằng nội dung**, không phải bằng token metadata. Nếu một ngày đọc được bảng usage, phép gán này phải được xác nhận lại — đã ghi vào §7.

---

## 3. Sáu mốc, theo đúng thứ tự trong blob

| slot | `type_id` | `GiftType` | hàm thu (RVA) | marker bấm được |
|---|---|---|---|---|
| 0 | 23 | `PVPMedal` | `set_PvPMedal` | 1 |
| 1 | 0 | `Gcoins` | `set_Coins` | 3 |
| 2 | 14 | `DroneCards` | `SetDroneCards` | 5 |
| 3 | 1 | `Gems` | `set_Gems` | 7 |
| 4 | 15 | `PlayerCards` | `SetPlayerCards` | 9 |
| **5** | **18** | **`Key2`** | **`set_KeyCount2`** | **11** |

⇒ Muốn kiếm key từ PvP, phải đi hết 5 mốc trước; mốc key là mốc **cuối mùa**. Và vì `16`/`17` không có nhánh, chuỗi này **không bao giờ** cho `Key0`/`Key1` (khớp báo cáo 132).

---

## 4. 12 marker, chỉ marker lẻ là nút thật

`SetupHunters` (19791640, 1124 B) duyệt `allPoints` (`WinPoint[]`, `0x190`):

```
i = 0 … allPoints.Length-1
  child.SetActive(i & 1)                 ; chỉ marker LẺ hiện nút
  if (i even) continue                   ; marker chẵn: không SetInfo, không click
  idx = (i - 1) / 2   (kẹp ≥ 0 bằng csel) ; 2 marker / 1 slot thưởng
  type = rewardIndexs[idx]
  amount = rewardValues[idx]             ; (blob chưa bind — §7)
  scale  = rewardScales[idx]
  icon   = GetBoxSpriteGeneral(type)     ; 20180172
  SetInfo(box, icon, amount, isCards = (type == 14 || type == 15), scale)  ; 19990656
```

* `type == 14` → icon lấy từ `statics[0]` của lớp ở slot `0x2add190` tại `+0x58`; `type == 15` → `+0x50`; các type khác → mảng icon `statics[0].+0x20[type]` (lớp này **chưa định danh** trong phạm vi báo cáo — chỉ chứng minh đường đọc Sprite).
* `isCards` = `(type & ~1) == 14` ⇒ 14/15 vẽ theo kiểu *card*, còn key/coin/gem/medal vẽ theo kiểu số.
* Thanh tiến độ: `lineProgress.size.x = SeasonProgress * 1.5`.
* Marker "hoàn tất": `transform.GetChild(1).SetActive(SeasonProgress == allPoints.Length)`.

Vì `rewardIndexs.Length == 6` và `idx = (i-1)/2`, `allPoints.Length` **phải** là 12 để phủ 6 slot — nhưng số marker thật vẫn do scene quyết định (đọc từ serialized array) ⇒ `MODEL_NOT_MEASURED runtime`; mã chỉ chứng minh phép chia đôi.

---

## 5. Điều kiện nhận & lưu trạng thái

| Việc | Cơ chế | RVA |
|---|---|---|
| đủ điều kiện bấm | `marker < Board_PVP.SeasonProgress` | `get_SeasonProgress` 19784460 |
| hiện/ẩn điểm | `marker < Board_PVP.SeasonDies` | `get_SeasonDies` 19784352 |
| đã nhận chưa | `PlayerPrefs.GetInt(<prefix> + marker.ToString(), 0) == 1` | `IsCollected` 19792764 |
| ghi tiến độ mùa | `PlayerPrefs.SetInt(key, value)` | `set_SeasonProgress` 19794028 |
| đánh dấu đã nhận | `SetPointActive()` + `PlayerPrefs.SetInt(prefix+index, 1)` | `OnClickHunterCollect` 19792936 |

`SeasonProgress`/`SeasonDies` đều là `PlayerPrefs` int ⇒ tiến độ mùa PvP **lưu bền theo máy**, giống mô hình key ở báo cáo 132 (static `-1` + lazy load + write-through).

---

## 6. Số lượng thưởng — bước chặn chính xác

`rewardValues` là `int[6]` cùng constructor, nhưng:

* blob 6-int: **48** ứng viên, trong đó **18** là dãy tăng dần dương (dạng "bậc thang" hợp lý cho thưởng/bet);
* không có ràng buộc nội dung nào (như miền `type_id`) để phân biệt `rewardValues` với `allBetCoinValues`/`allBetGemValues`/`allBetMedalValues` hay 44 mảng 6 phần tử khác trong game;
* ⇒ **`status: NOT_BOUND`**, cần bảng metadata usage cho 3 slot handle `0x2AE0010`, `0x2AE0018`, `0x2AE0020`… (đúng hơn: cho từng slot handle mà constructor nạp).

Cùng lý do, **3 bảng bet** (`allBetCoinValues` 6 bậc, `allBetGemValues`, `allBetMedalValues`) đã chốt **cấu trúc** (6 bậc, offset `0x208/0x210/0x218`, RVA như §1) nhưng **chưa chốt giá trị** — việc "coin > gem > medal" là giả định thứ tự, không phải bằng chứng, nên không dùng để gán blob.

---

## 7. Cái chưa đo

| Hạng mục | Bước chặn |
|---|---|
| `rewardValues[0..5]` (số lượng mỗi mốc) | blob chưa bind; cần usage table |
| `rewardScales[0..5]` (scale icon) | như trên (chỉ là trang trí) |
| 3 bảng bet `allBet*Values` | như trên, 18 dãy tăng dần không phân biệt được bằng nội dung |
| xác nhận lại phép gán `rewardIndexs` bằng token | cần usage table (`0x2AE0008`) |
| số marker thật trong scene | `allPoints` serialized; `MODEL_NOT_MEASURED runtime` |
| số lượng mùa/thứ hạng mùa | nằm ở `PVP_Manager..cctor` (19916640, 19.944 B, 10 lời gọi `InitializeArray` độ dài 3/4/5) — **ngoài phạm vi báo cáo này** |

---

## 8. Tái lập

```bash
python3 tools/verify/pvp_hunter_reward.py       # ghi lại artifact
python3 -m unittest tests.test_pvp_hunter_reward -q   # 20 test
```

Test khoá: sha artifact, 4 nguồn + sha, 6 mảng đúng offset/độ dài/RVA, `rewardIndexs = [23,0,14,1,15,18]`, quy tắc nhận dạng + 48 blob quét, miền giá trị = đúng 6 id có handler, nhãn khớp enum `GiftType`, chỉ slot 5 trả key, không slot nào trả `Key0/Key1`, 12 marker / lẻ-only, gate `SeasonProgress`/`SeasonDies`/`IsCollected`, và mọi `NOT_BOUND` đều kèm `blocking`.

`provenance:` XAPK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` · `libil2cpp.so` `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` · sha256 của 4 nguồn (`key-grant` raw, `pvp-dispatch` raw, `field-defaults.json`, `dump.cs.gz`) nằm trong `datas/l2_535b0541_pvp_hunter_reward_table.json.gz → provenance.sources`.
