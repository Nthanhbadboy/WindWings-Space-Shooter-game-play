# 172 — Sửa bảng reader của 169: ô metadata đội lốt field, và coroutine hoá ra là sync Firebase

**Trạng thái:** `DECODED_STATIC` (slice + `dump.cs` đã ghim; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mỗi kết luận "đọc cell" hay "đọc field" đều kèm **lệnh định nghĩa gần nhất** của thanh ghi base.
**Artifact:** `datas/l2_535b0541_pvp_move_next.json.gz` — **2975 B**, sha256 `ec79aff771ea83f7011490a49fddf4fd2560eee15f1890fe4d9fb67080c53a2d`
**Verifier:** `tools/verify/pvp_move_next.py` (**13 check**) · **Test:** `tests/test_pvp_move_next.py` (**18 test**)
**Sửa:** 169 (`datas/l2_535b0541_pvp_reward_arrays.json.gz`)

---

## 0. TL;DR

| trường | 169 ghi | 172 đo |
|---|---|---|
| `rewardIndexs` | 19791640 · 19792936 · **19811092** | **19791640 · 19792936** |
| `rewardValues` | 19791640 · 19792936 · **19811092** | **19791640 · 19792936** |
| `rewardScales` | 19791640 · **19811092** | **19791640** |
| `allBetCoinValues` | 19779724 · **19813332** | **19779724** |
| `allBetGemValues` | 19779984 · **19813332** | **19779984** |
| `allBetMedalValues` | 19780244 · **19813332** | **19780244** |

Sáu chỗ ghi (ctor 19796420) **không đổi** — chúng là store vào `this`, base do `mov`, không phải cell.

Nguyên nhân: IL2CPP nạp **ô metadata** bằng đúng một dạng lệnh như nạp field:

```asm
adrp x0, #0x2ae0000        ; trang của token
ldr  x0, [x0, #0x198]      ; ô 0x2ae0198  — KHÔNG phải Board_PVP.rewardIndexs
```

`0x198/0x1a0/0x1a8/0x208/0x210/0x218` vừa là offset field của `Board_PVP`, vừa là **phần thấp của địa chỉ ô** trong trang `0x2ae0000`. Quét theo offset là không phân biệt được.

---

## 1. Cách phân loại

Với mỗi `ldr/str …, [xN, #off]` có `off` thuộc sáu offset, tìm **lệnh ghi gần nhất** vào `xN` trong cùng method:

| định nghĩa gần nhất | nghĩa | kết luận |
|---|---|---|
| `adrp xN, #page` | `xN` giữ **địa chỉ ô** | `cell` |
| `mov xN, x19` (hoặc bất kỳ lệnh không phải `adrp`) | `xN` giữ **con trỏ object** | `instance` |
| không tìm thấy (tham số vào) | không kết luận | `unknown` |

Kết quả trên toàn bộ slice `Board_PVP*`: **29** điểm chạm, **12** là `cell`, **17** là `instance`, 0 `unknown`.

| method | vai | offset chạm | loại |
|---|---|---|---|
| `<IsCollected\|0>` (19811092) | kiểm tra "đã nhận" | `0x198 · 0x1a0 · 0x1a8` | **cell** |
| `MoveNext` (19813332) | coroutine sync Firebase | `0x208 · 0x210 · 0x218` | **cell** |
| `SetupHunters` (19791640) | dựng 12 điểm thưởng | `0x198 · 0x1a0 · 0x1a8` | instance |
| `OnClickHunterCollect` (19792936) | trao thưởng theo id | `0x198 · 0x1a0` | instance |
| `OnChangeCoins/Gems/Medals` | đổi bậc cược | `0x208` / `0x210` / `0x218` | instance |
| `.ctor` (19796420) | khởi tạo 6 mảng + 1 list | cả sáu | instance (**store**) |

`<IsCollected|0>` là closure của `IESummarySeasonRewards` — nó hỏi *class token*, không đọc mảng nào của `Board_PVP`; cờ "đã nhận" của nó nằm ở `PlayerPreferences` (171 đã chỉ ra).

---

## 2. Coroutine `MoveNext` thực ra là gì

`Board_PVP.<GetPvPUserCachingDatas>d__78.MoveNext` — **1808 B / 452 lệnh**, không đọc một field nào của `Board_PVP`. Nó là vòng đồng bộ dữ liệu người chơi PvP qua Firebase:

| RVA | gọi | việc |
|---|---|---|
| 19813760 | `PVP_Manager.get_pathOfDataUsers` | dựng đường dẫn |
| 19813772 | `DataUser.get_userID` | ghép user |
| 19813804 | `String.Format` | path cuối |
| 19813904 | `FirebaseDatabaseManager.DownloadDatabase` | tải |
| 19813992 | `WaitUntil` | chờ |
| 19814168 | `WaitForSecondsRealtime` | nhịp 1 giây |
| 19814232 | `DateTimeMethods.BinaryStringToDateTime` | đọc mốc thời gian đã lưu |
| 19814288 | `DateTime.op_LessThan` | so với hiện tại |
| 19814504 / 19814700 | `IESummarySeasonRewards` / `LoadPvPDatas` | dữ liệu còn mới |
| 19814988 | `FirebaseDatabaseManager.DeleteDatabase` | dữ liệu cũ → xoá |

169 gán coroutine này làm reader của ba mảng bậc cược **chỉ vì** nó chạm ba ô `0x208/0x210/0x218`. Ba ô đó là token khởi tạo lớp, không phải bậc cược.

---

## 3. Cái 169 làm đúng

* Sáu chỗ ghi trong `.ctor` (19796420) — 172 xác nhận lại, cả sáu là store vào `this`.
* `SetupHunters` / `OnClickHunterCollect` đọc `rewardIndexs`/`rewardValues`; `OnChangeCoins/Gems/Medals` đọc bậc cược tương ứng. Đây là toàn bộ reader thật trong slice đã ghim.

## 4. Giới hạn

1. Phân loại cần thanh ghi base được định nghĩa **trong cùng method**; base đến từ tham số ⇒ `unknown` (lần này 0 ca).
2. Ảnh hưởng của việc 169 ghi thừa: các report sau (171) đã dùng 169 để suy "ai đọc mảng" — 171 kết luận đúng vì nó đọc thẳng `SetupHunters`, không dựa vào danh sách reader. Nhưng nếu ai đó dùng danh sách của 169 để suy "coroutine này đọc bậc cược", họ sẽ sai.
3. Dữ liệu Firebase mà coroutine ghi vào cache vẫn là `MODEL_NOT_MEASURED runtime`.

---

## 5. Tái lập

```bash
python3 tools/verify/pvp_move_next.py            # 13/13 check, 29 điểm, 12 cell
python3 -m unittest tests.test_pvp_move_next -q  # 18 test
```
