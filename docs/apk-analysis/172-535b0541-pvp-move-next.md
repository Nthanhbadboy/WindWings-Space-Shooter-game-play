# 172 — Sửa một false positive của 169, và đọc cái coroutine bị gọi nhầm là "reader"

**Trạng thái:** `DECODED_STATIC` (chỉ đọc slice + `dump.cs`; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mỗi dòng của bảng reader mới đều kèm **loại base register** đã phân loại bằng định nghĩa gần nhất, nên "đọc field" và "đọc cell" không còn lẫn nhau.
**Artifact:** `datas/l2_535b0541_pvp_move_next.json.gz` — **4739 B**, sha256 `ac3f1070c21ab2eedbea7ad64773eaba69c3b4e96ce86c680d0b894bfa60a9a4`
**Verifier:** `tools/verify/pvp_move_next.py` (**19 check**) · **Test:** `tests/test_pvp_move_next.py` (**27 test**)
**Sửa:** 169 (danh sách reader) · **Đọc:** `Board_PVP.<GetPvPUserCachingDatas>d__78.MoveNext` (19813332, 1808 B / 452 lệnh)

---

## 0. TL;DR

| | 169 nói | 172 đo |
|---|---|---|
| `rewardIndexs` reader | {19791640, 19792936, **19811092**} | **{19791640, 19792936}** |
| `rewardValues` reader | {19791640, 19792936, **19811092**} | **{19791640, 19792936}** |
| `rewardScales` reader | {19791640, **19811092**} | **{19791640}** |
| `allBetCoinValues` | {19779724, **19813332**} | **{19779724}** |
| `allBetGemValues` | {19779984, **19813332**} | **{19779984}** |
| `allBetMedalValues` | {19780244, **19813332**} | **{19780244}** |

**Nguyên nhân:** IL2CPP phát `adrp xN, #page; ldr xN, [xN, #off]` cho **cell metadata**, giống hệt cú pháp đọc field. Sáu offset của `Board_PVP` (0x198/0x1a0/0x1a8/0x208/0x210/0x218) tình cờ trùng offset trong page `0x2ae0000`, nên mọi hit ở đó đều là **cell**, không phải field:

| field | cell thật sự bị đọc |
|---|---|
| `rewardIndexs` | `0x2ae0198` |
| `rewardValues` | `0x2ae01a0` |
| `rewardScales` | `0x2ae01a8` |
| `allBetCoinValues` | `0x2ae0208` |
| `allBetGemValues` | `0x2ae0210` |
| `allBetMedalValues` | `0x2ae0218` |

Cái coroutine bị gọi nhầm hoá ra là **luồng đồng bộ dữ liệu PvP qua Firebase**: dựng path → `DownloadDatabase` → `WaitUntil` → `WaitForSecondsRealtime(1.0)` → so ngày lưu với đồng hồ → tươi thì `IESummarySeasonRewards`/`LoadPvPDatas`, cũ thì `DeleteDatabase`. Nó **không** chạm mảng nào của `Board_PVP`.

---

## 1. Cách phân loại (để không lặp lại lỗi này)

Với mỗi `ldr xT, [xB, #off]` có `off` ∈ sáu offset:

1. tìm **định nghĩa gần nhất** của `xB` trước lệnh đó;
2. nếu định nghĩa là `adrp` → base là **địa chỉ cell** ⇒ `static_cell`, địa chỉ = `page + off`;
3. nếu không → base là con trỏ đối tượng (receiver) ⇒ `object_field`.

Kết quả trên 7 method được quét: **23** lệnh chạm sáu offset, **11** là field thật, **12** là cell. Mọi cell rơi đúng vào page `0x2ae0000` (§0).

Đây là cùng một lỗi mà 166/167 đã tránh bằng `last_def`; 169 áp regex trực tiếp nên dính. Báo cáo này đưa bộ phân loại vào verifier để lần sau không thể dính lại.

---

## 2. Bảng reader đúng

| Mảng | Reader thật (RVA) | field reads | cell reads |
|---|---|---|---|
| `rewardIndexs` 0x198 | 19791640 `SetupHunters`, 19792936 `OnClickHunterCollect` | 2 | 2 |
| `rewardValues` 0x1a0 | 19791640, 19792936 | 2 | 2 |
| `rewardScales` 0x1a8 | 19791640 | 1 | 2 |
| `allBetCoinValues` 0x208 | 19779724 `OnChangeCoins` | 2 | 2 |
| `allBetGemValues` 0x210 | 19779984 `OnChangeGems` | 2 | 2 |
| `allBetMedalValues` 0x218 | 19780244 `OnChangeMedals` | 2 | 2 |

Hệ quả đọc được:

1. **Mọi mảng thưởng/bet chỉ có reader trong chính `Board_PVP`** — không có lớp UI nào đọc trực tiếp; chúng đi qua `SetupHunters` (dựng hộp, xem 171) và `OnChange*` (đổi loại tiền đặt).
2. `rewardScales` là mảng **ít người đọc nhất**: chỉ `SetupHunters` — khớp 171 (chỉ dùng làm `_scaleIcon`).
3. "Đã nhận" trong 171 **không** đọc mảng nào (đã chứng minh ở 171); cell `0x2ae0198/01a0/01a8` trong `IsCollected|0` là **class-init**, không phải dữ liệu.

---

## 3. `d__78.MoveNext` thật ra làm gì

Coroutine 6 trạng thái (field `0x10`, 8 lần ghi, giá trị ∈ {−1,1,2,3,4,5}):

| Bước | Lệnh | Ý nghĩa |
|---|---|---|
| 1 | 19813760 `PVP_Manager.get_pathOfDataUsers()` · 19813772 `DataUser.get_userID()` · 19813804 `String.Format(fmt, path, userID)` | dựng đường dẫn tới document của user |
| 2 | 19813904 `FirebaseDatabaseManager.DownloadDatabase(path, Action<DataSnapshot>)` | tải document |
| 3 | 19813992 `new WaitUntil(Func<bool>)` · 19814168 `new WaitForSecondsRealtime(1.0f)` | chờ tải xong rồi chờ 1 giây |
| 4 | 19814232 `DateTimeMethods.BinaryStringToDateTime` · 19814288 `DateTime.op_LessThan` | so ngày lưu với hiện tại |
| 5a | 19814412 `Debug.Log` · 19814504 `IESummarySeasonRewards(userDatas, callback)` | dữ liệu cũ → log rồi chạy tóm tắt mùa |
| 5b | 19814700 `LoadPvPDatas(userDatas)` | dữ liệu còn tươi → nạp bảng PvP |
| 5c | 19814988 `FirebaseDatabaseManager.DeleteDatabase(path, Action<bool>)` | nhánh xoá (dữ liệu không dùng được) |
| 6 | 19814520 / 19814716 `MonoBehaviour.StartCoroutine` | hai iterator được khởi động từ trong coroutine |

Nghĩa là **nguồn dữ liệu PvP là Firebase**, có cổng thời gian: dữ liệu quá cũ thì bị xoá thay vì dùng. Đây là lý do các câu hỏi kiểu "rank hiện tại là bao nhiêu" phải là `MODEL_NOT_MEASURED runtime`.

---

## 4. Cái gì không đổi

- 169 vẫn đúng ở phần **ánh xạ sáu mảng ↔ sáu field** (0x198/0x1a0/0x1a8/0x208/0x210/0x218) và ở kiểu khai báo (`rewardScales` là `float[]`). Báo cáo này chỉ sửa *danh sách reader*, không đổi kết luận nào về nội dung mảng.
- 170 vẫn đúng ở các verdict đã đóng; báo cáo này chỉ sửa **danh sách reader**, không đổi kết luận nào về "mảng nào chứa gì".
- 171 vẫn đúng: `SetupHunters` là reader của cả ba mảng thưởng.

---

## 5. Còn mở

1. **Sáu cell `0x2ae0198…0x2ae0218` là cell gì** — dạng metadata (type-info của lớp nào) chưa đọc được vì thiếu bảng metadata usage; `MODEL_NOT_MEASURED runtime` cho danh tính.
2. **Nhánh nào của coroutine chạy cho một user cụ thể** — phụ thuộc dữ liệu Firebase + đồng hồ.
3. **Nội dung document Firebase** — served data.
4. Chuỗi format ở cell `0x2adebb0` — dữ liệu, không phải code.

---

## 6. Tái lập

```bash
python3 tools/verify/pvp_move_next.py
python3 -m unittest tests.test_pvp_move_next -v
```

Verifier đọc 8 slice + `dump.cs` + artifact 169; RVA in dạng thập phân, cell in dạng hex vì là địa chỉ.
