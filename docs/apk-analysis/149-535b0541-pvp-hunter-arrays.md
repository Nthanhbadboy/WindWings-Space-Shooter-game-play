# 149 — Sáu array của `Board_PVP..ctor`: thang reward 6 mức và ba thang cược

**Trạng thái:** `DECODED_STATIC` (chỉ đọc APK gốc + metadata đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Đây là byte **lúc build**; phần "người chơi thực nhận gì trong một trận" vẫn là `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_pvp_hunter_arrays.json.gz` (3648 B, sha256 `034bb93bc8cd3585d07bc47d56a2465d90a205619b57acbef004e694a1333975`)
**Báo cáo trước:** 148 (kiểm lại 56 mục mở — đây là 2 mục `ACTIONABLE` của nó), 133 (bảng reward hunter, nơi đặt câu hỏi).
**Verifier:** `tools/verify/pvp_hunter_arrays.py` (~1,0 s) · **Test:** `tests/test_pvp_hunter_arrays.py` (19 test).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| 133 tắc ở đâu? | hai chỗ, **cả hai là đặc điểm của raw chứ không phải thiếu dữ liệu** | §1 |
| Sáu array là gì? | `rewardIndexs [23,0,14,1,15,18]` · `rewardValues [100,10000,10,100,10,10]` · `rewardScales float[6]` · ba thang cược | §2 |
| Thang reward có mấy mức? | **6**, mỗi mức một loại + một lượng, và **mức 5 là mức khoá** (10 khoá) | §3 |
| Ba thang cược là coin/gem/medal? | **Đúng** — không đoán theo nội dung: mỗi thang có method đọc riêng (`OnChangeCoins/Gems/Medals`) và field index riêng (`betCoins/betGems/betMedals`) | §4 |
| Vì sao tin được phép gán blob? | nó **tái tạo đúng** blob mà 133 đã nhận diện bằng nội dung, trước khi áp cho 5 array còn lại | §5 |
| Còn gì mở? | 3 mục: trận thật, số marker trong scene, và class sau cell `0x2ADF238` | §6 |

**Một câu:** sáu array của constructor PvP đều đọc được từ field-default đã pin; cái làm 133 dừng lại không phải thiếu bảng metadata mà là **raw này không trích `initialize_arrays` cho constructor đó** — raw kia thì có.

---

## 1. Hai chỗ tắc, và vì sao cả hai đều là đặc điểm của raw

**a) "cần metadata usage table cho handle slot `0x2ae0010` / `0x2ae0018`".** Cùng một constructor `Board_PVP..ctor` (rva **19796420**, 500 B, 125 lệnh) nằm trong **hai** raw đã pin:

| Raw | `initialize_arrays` cho constructor này | Kết quả |
|---|---|---|
| `arena-pvp-535b0541` | **0** | 133 đọc ở đây ⇒ handle slot trông như chưa phân giải |
| `key-grant-535b0541` | **6** event, mỗi event có token + `slot_va` + `length` | đủ để chạy phép gán của 131 |

Đây là kiểu sai "không tra ≠ thiếu": dữ liệu có, chỉ là ở raw khác. 148 đã ghi đúng nguyên tắc này; báo cáo này là một ca cụ thể của nó.

**b) "nội dung một mình không đặt tên được ba thang cược".** Đúng — nhưng không cần nội dung. Mỗi event InitializeArray được theo sau bởi một `str x20, [x19, #off]`, và `off` chính là offset instance của field đó trong `dump.cs`. Vị trí + token xác định array; nội dung chỉ dùng để **kiểm lại**, không phải để đoán.

---

## 2. Sáu array

`Board_PVP..ctor` gọi `RuntimeHelpers.InitializeArray` (rva **33927292**) sáu lần, mỗi lần `new int[6]` / `new float[6]` rồi gán vào instance:

| Offset | Field (dump.cs) | Kiểu | Giá trị |
|---|---|---|---|
| 408 | `rewardIndexs` | `int[]` | `[23, 0, 14, 1, 15, 18]` |
| 416 | `rewardValues` | `int[]` | `[100, 10000, 10, 100, 10, 10]` |
| 424 | `rewardScales` | `float[]` | `[1.0, 1.0, 0.6, 1.0, 0.6, 0.8]` (f32) |
| 520 | `allBetCoinValues` | `int[]` | `[500, 2000, 5000, 10000, 20000, 50000]` |
| 528 | `allBetGemValues` | `int[]` | `[0, 10, 25, 50, 100, 500]` |
| 536 | `allBetMedalValues` | `int[]` | `[0, 30, 50, 100, 200, 1000]` |

Mỗi blob là 24 byte đúng bằng `4 × 6`, khai báo `<PrivateImplementationDetails>.__StaticArrayInitTypeSize=24`, ordinal thuộc PID `TypeDefIndex 2461` (740 field). `rewardScales` là `float[]` chứ không phải `int[]` — hex `0000803f 0000803f 9a99193f 0000803f 9a99193f cdcc4c3f` giải ra `0x3F800000`, `0x3F19999A`, `0x3F4CCCCD`, tức **0.6 f32 = 0,6000000238418579** và **0.8 f32 = 0,800000011920929** — artifact giữ đúng giá trị đã mở rộng, không làm tròn thành 0,6.

---

## 3. Thang reward PvP: 6 mức

`rewardIndexs[i]` là **id loại reward**, `rewardValues[i]` là lượng, và 133 đã có bảng handler cho từng id:

| Mức | `rewardIndexs` | Handler (133) | `rewardValues` | `rewardScales` |
|---|---|---|---|---|
| 0 | 23 | `set_PvPMedal` | 100 | 1.0 |
| 1 | 0 | `set_Coins` | 10 000 | 1.0 |
| 2 | 14 | `SetDroneCards` | 10 | 0.6 |
| 3 | 1 | `set_Gems` | 100 | 1.0 |
| 4 | 15 | `SetPlayerCards` | 10 | 0.6 |
| 5 | 18 | `set_KeyCount2` | **10** | 0.8 |

**Mức 5 là mức khoá.** 133 đã nêu `key_stage = {slot: 5, type_id: 18, collectible_point: 11}` và chỉ ra nó là slot duy nhất ghi vào bộ đếm khoá; bảng này khớp cả ba con số: `rewardIndexs[5] = 18`, `rewardValues[5] = 10` (10 khoá), và theo luật `index = (marker - 1) / 2` của 133 thì marker **11** → index **5**. Ba nguồn độc lập, một kết luận.

Thang này cũng là câu trả lời cho mục 39 của 148 (`amount per stage (rewardValues)`), vốn bị xếp `ACTIONABLE`.

---

## 4. Ba thang cược, và vì sao nhãn không còn là phỏng đoán

133 ghi: *"three ascending int[6] ladders; the label order (coin > gem > medal) is a runtime assumption, and 18 six-int blobs are already strictly ascending, so content alone cannot name them"*. Đúng — nên nhãn ở đây lấy từ **hai** nguồn khác:

1. **offset → field** trong `dump.cs` (bảng §2), và
2. **method đọc** từng offset, tự tìm trong chính các method của `Board_PVP`:

| Thang | Offset | Field index | Offset index | Method đọc | Luật |
|---|---|---|---|---|---|
| coin | 520 | `betCoins` | `0x1F8` | `OnChangeCoins(int amount)` | `idx = clamp(idx + amount, 0, len-1)` → format phần tử → gán vào label; giá trị được chọn ghi vào một static block ở `+0x10` |
| gem | 528 | `betGems` | `0x1FC` | `OnChangeGems(int amount)` | như trên, static `+0x14` |
| medal | 536 | `betMedals` | `0x200` | `OnChangeMedals(int amount)` | như trên, static `+0x18` |

Ba method này đối xứng từng lệnh một (cùng 260 B, 65 lệnh, cùng hình `csel` kẹp hai đầu), chỉ khác offset thang và offset static đích — nên việc gán nhãn không thể sai lệch giữa ba thang mà không lộ ra ngay.

Thêm một chỗ khớp: cả ba thang đều **tăng dần và không trùng**, và ở mức 0 thì gem = medal = **0** còn coin = 500 — tức vé rẻ nhất chỉ trả bằng coin. Đó là **củng cố**, không phải chứng minh; chứng minh là method đọc ở bảng trên.

---

## 5. Vì sao tin được phép gán blob (thứ tự kiểm)

Phép gán `token → PID ordinal → fieldDefaultValues` không tự chứng minh nó đúng. Ở đây nó được kiểm **trước** khi dùng:

1. **Kiểm độc lập trên `rewardIndexs`.** 133 đã nhận diện blob đó bằng nội dung (blob sáu-int duy nhất mà mọi giá trị đều là id handler) và ghi `F2ADB78D…`, giá trị `[23,0,14,1,15,18]`. Phép gán token của báo cáo này cho **đúng blob đó, đúng giá trị đó** — hai đường khác nhau, một kết quả.
2. **Chỉ sau đó** mới áp cùng phép gán cho 5 array còn lại.
3. **Kiểm kiểu:** mỗi event phải có `declared_bytes == 4 × length` và kiểu khai báo trong `dump.cs` phải khớp cách giải (`int[]` ↔ int32, `float[]` ↔ float32) — 6/6.
4. **Kiểm tên:** offset sau lệnh `str` phải mang đúng tên mà 133 giả định (408/416/424/520/528/536) — 6/6, và tên đó lấy từ layout instance của `dump.cs`, không từ 133.

Tổng **18 check**, tất cả PASS.

---

## 6. Còn mở

| Mục | Bước chặn |
|---|---|
| người chơi thực nhận gì trong một trận | thang là tĩnh; nhận hay không cần trận thật — `MODEL_NOT_MEASURED runtime` |
| scene có bao nhiêu marker | `allPoints` là `WinPoint[]` serialized, đổ từ scene — không đổi so với 133 |
| class sau cell **`0x2ADF238`** (nơi giá trị cược được chọn ghi vào) | slot chỉ phân giải ra một addend `45765696`, không phải string literal, nên class vẫn chưa có tên; chỉ biết ba offset `+0x10 / +0x14 / +0x18` |

Mục thứ ba là mục mới, và nó có đúng dạng "chưa đọc" chứ không phải "không có": cần bảng nào gán cell → class (cùng loại việc với mục 50–52 của 138).

---

## 7. Đóng được gì

| Mục | Trước | Sau |
|---|---|---|
| 148 #39 `rewardValues` | `ACTIONABLE` (133: handle slot chưa phân giải) | **đóng** — 6 giá trị, khớp `key_stage` |
| 148 #40 `rewardScales` | `ACTIONABLE` (cùng lý do) | **đóng** — `float[6]`, f32 chính xác |
| 133 `bet_tables.status` | `NOT_BOUND` (nội dung không phân biệt được) | **đóng** — nhãn theo offset + method đọc |
| 133 `reward_indexs` | đã đóng bằng nội dung | **xác nhận độc lập** bằng token |

Ba mục của 133 vì vậy không còn `NOT_BOUND` nào; phần còn mở của 133 chỉ là số marker trong scene (runtime).

---

## 8. Bốn xác nhận ghi trong artifact

`confirmations` của artifact 149 ghi việc đóng theo đúng quy ước lane (báo cáo sau ghi vào artifact của mình): hai mục `ACTIONABLE` của 148 (#39 `rewardValues`, #40 `rewardScales`) và hai mục `NOT_BOUND` của 133 (`reward_values` / `reward_scales` / `bet_tables`). Lần kiểm kê sau (nếu có) sẽ thấy chúng ở đây thay vì phải suy lại từ văn bản.

---

## 9. Chạy lại

```bash
python3 tools/verify/pvp_hunter_arrays.py       # in bytes/sha + 6 array + 18/18 check + 6 mức
python3 -m unittest tests.test_pvp_hunter_arrays -q
```

Artifact dựng lại tất định (gzip `mtime=0`, `sort_keys=True`, `separators=(',',':')`).

---

provenance: static-only decode of the original XAPK; 5 sources with sha256 in `datas/l2_535b0541_pvp_hunter_arrays.json.gz` §`provenance` (`key-grant` raw, `arena-pvp` raw, `field-defaults.json` v31, `dump.cs`, and 133's artifact). No emulator, no probe, no device. RVAs decimal. The arrays are build-time bytes; a played match stays `MODEL_NOT_MEASURED runtime`.
