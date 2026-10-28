# 169 — Sáu mảng thưởng của `Board_PVP`: lệnh nào điền mảng nào, ai đọc, và vì sao con số vẫn chưa đọc được

> **ERRATUM 180:** câu "giá trị vẫn `NOT_BOUND`, cần bảng metadata usage" trong report này **SAI**. Event `InitializeArray` mang sẵn `field_id`, nên `slot_va → field_id → field-defaults.json` giải ra 24 byte của cả sáu array; **149** đã đọc đúng như vậy. Xem `docs/apk-analysis/180-535b0541-registry-v4.md` §1.

**Trạng thái:** `DECODED_STATIC` (chỉ đọc `dump.cs` + 8 slice + `field-defaults.json` đã pin, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Sáu cặp `InitializeArray → store offset`, kiểu khai báo, chiều dài 6 và danh sách reader là hằng lúc build; **byte của hai blob** (`rewardValues`, `rewardScales`) là `MODEL_NOT_MEASURED runtime` vì thiếu bảng metadata usage.
**Artifact:** `datas/l2_535b0541_pvp_reward_arrays.json.gz` (4618 B, sha256 `cb3711ec8dc742b88a1f605df2e3afdf0e78226ddc57be85d7aa57c87c8d583b`)
**Báo cáo trước:** 168 (quét residue), 167 (xref hộp thưởng), 166 (hộp thưởng), 133 (bảng thưởng hunter), 132 (pack quà).
**Verifier:** `tools/verify/pvp_reward_arrays.py` (~0,7 s, **28 check**) · **Test:** `tests/test_pvp_reward_arrays.py` (**40 test**).

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| `Board_PVP` có mấy mảng thưởng? | **6** mảng chiều dài **6**: `rewardIndexs` 0x198, `rewardValues` 0x1a0, `rewardScales` 0x1a8, `allBetCoinValues` 0x208, `allBetGemValues` 0x210, `allBetMedalValues` 0x218 | §2 |
| Lệnh nào điền mảng nào? | **6** lệnh `InitializeArray` trong `.ctor` (19796420, 500 B / 125 lệnh); mỗi lệnh được theo ngay bởi `str x20, [x19, #offset]` (call+4) | §2 |
| `rewardScales` kiểu gì? | **`float[]`** (dump), không phải `int[]` | §3 |
| Ai đọc từng mảng? | `rewardIndexs`/`rewardValues` cùng **3** reader; `rewardScales` **2**; ba mảng bet mỗi cái 2 (một chung `<GetPvPUserCachingDatas>d__78`) | §4 |
| 132 nói đúng không? | **sai hai chỗ**: `Board_PVP` **không có** field `rewardTypes`, và hai mảng kia được điền **trong `.ctor`** từ blob build-time, không phải "filled at runtime" | §5 |
| Vậy đọc được số chưa? | **chưa**: 982 blob PID, 99 blob đúng 24 byte, chỉ 7 đọc ra 6 float hợp lý, 3 trong đó đã thuộc ctor khác ⇒ 4 ứng viên, không cái nào cạnh data của `rewardIndexs` | §6 |
| `.cctor` làm gì? | 88 B / 22 lệnh, chỉ zero một struct 3 slot (double từ `.rodata` `0x757fe8` + hai zero) | §7 |

**Một câu:** ctor trả lời được "**mảng nào**" mà không cần bảng metadata (vì store nằm ngay sau call), nhưng "**số nào**" vẫn chặn ở đúng chỗ 133 đã ghi — chỉ khác là block hẹp hơn: không phải "không biết field", mà là "không đọc được blob".

---

## 1. Vì sao cần báo cáo này

168 quét residue và để lại hai câu: n30 (132) nói `Board_PVP.rewardTypes/rewardValues` là "instance arrays filled at runtime", còn n33/n39/n40 (133) nói hai handle slot `0x2ae0010`/`0x2ae0018` chưa giải được nên chưa biết lệnh nào điền field nào. Hai câu đó **không thể cùng đúng**, và ctor là chỗ phân xử: nếu mỗi `InitializeArray` được theo ngay bởi một store vào field thì cặp (call ↔ field) là *quan hệ kề trong instruction stream*, không phải suy luận từ metadata.

Phạm vi: chỉ `Board_PVP..ctor`/`..cctor`, bảng field của class, và reader của 6 offset. Không mở lại 127–168.

---

## 2. Sáu lệnh, sáu field

`Board_PVP..ctor` (19796420, 500 B, 125 lệnh) — mỗi lần: `bl 0x110d09c` (helper `newarr`, `w1 = 6`) → `ldr x1, [xR]` (handle từ cell) → `bl 0x205b07c` (`RuntimeHelpers.InitializeArray`) → `str x20, [x19, #offset]`:

| # | Call RVA | Field | Offset | Handle | Store (call+4) |
|---|---|---|---|---|---|
| 1 | 19796684 | `rewardIndexs` | `0x198` | `ldr x1, [x20]` | `str x20, [x19, #0x198]` |
| 2 | 19796716 | `rewardValues` | `0x1a0` | `ldr x1, [x29]` | `str x20, [x19, #0x1a0]` |
| 3 | 19796748 | `rewardScales` | `0x1a8` | `ldr x1, [x27]` | `str x20, [x19, #0x1a8]` |
| 4 | 19796804 | `allBetCoinValues` | `0x208` | `ldr x1, [x24]` | `str x20, [x19, #0x208]` |
| 5 | 19796836 | `allBetGemValues` | `0x210` | `ldr x1, [x23]` | `str x20, [x19, #0x210]` |
| 6 | 19796876 | `allBetMedalValues` | `0x218` | `ldr x1, [x8]` | `str x20, [x19, #0x218]` |

Cả sáu dùng **cùng** một helper cấp phát (`bl #0x110d09c`) với `w1 = 6`, nên chiều dài 6 là hằng lúc build, không phải `ldr` từ cấu hình.

Đối chiếu 133: sáu `initarray_rva` mà 133 ghi lại **trùng khít** sáu RVA trên — nghĩa là 133 *đã* có ánh xạ call↔field; cái 133 thiếu chỉ là **byte của blob**, không phải field.

---

## 3. Kiểu khai báo (từ `dump.cs`)

| Offset | Khai báo | Ghi chú |
|---|---|---|
| `0x198` | `private int[] rewardIndexs` | reward id |
| `0x1a0` | `private int[] rewardValues` | số lượng |
| `0x1a8` | **`private float[] rewardScales`** | scale icon — **float**, không phải int |
| `0x208` | `private int[] allBetCoinValues` | ladder bet coin |
| `0x210` | `private int[] allBetGemValues` | ladder bet gem |
| `0x218` | `private int[] allBetMedalValues` | ladder bet medal |

---

## 4. Ai đọc sáu mảng

| Mảng | Readers (RVA · method · số lệnh `ldr` trúng offset) |
|---|---|
| `rewardIndexs` 0x198 | 19791640 `SetupHunters()` · 19792936 `OnClickHunterCollect(WinPoint point)` · 19811092 `<IESummarySeasonRewards>g__IsCollected\|0(int index)` |
| `rewardValues` 0x1a0 | 19791640 · 19792936 · 19811092 (đúng ba cái trên) |
| `rewardScales` 0x1a8 | 19791640 · 19811092 |
| `allBetCoinValues` 0x208 | 19779724 `OnChangeCoins(int amount)` · 19813332 `<GetPvPUserCachingDatas>d__78.MoveNext()` |
| `allBetGemValues` 0x210 | 19779984 `OnChangeGems(int amount)` · 19813332 |
| `allBetMedalValues` 0x218 | 19780244 `OnChangeMedals(int amount)` · 19813332 |

Hệ quả đọc được:

1. **Ba mảng thưởng đọc như bộ ba cùng index** — `rewardIndexs[i]` (id), `rewardValues[i]` (số lượng), `rewardScales[i]` (scale icon) — đúng hình dạng `SetInfo(number, isCards, scale)` mà 166/167 đo ở phía hộp thưởng. `IsCollected(index)` nhận `int index` và đọc cả ba, nên index thưởng và index bet dùng chung một không gian (6).
2. **Ba mảng bet có một reader chung là `MoveNext()` của `<GetPvPUserCachingDatas>d__78`**, cộng ba handler `OnChangeCoins/Gems/Medals` — nghĩa là ladder bet được chọn theo *loại tiền*, và cache dữ liệu PvP đọc cả ba cùng lúc (§4 bảng trên).
3. Mọi reader có thân trong 8 slice **và** thực sự `ldr` từ đúng offset đó (cột `loads` > 0, kiểm bằng `every-reader-loads-its-own-offset`) — không phải suy ra từ tên field.

---

## 5. Hai chỗ 132/133 ghi chưa đúng

| Báo cáo | Viết cũ | Đo được |
|---|---|---|
| 132 (n30) | "`Board_PVP.rewardTypes/rewardValues` are instance arrays filled at runtime" | `Board_PVP` **không có** field `rewardTypes` (0 lần xuất hiện trong class body); `rewardValues`/`rewardScales` được điền **trong `.ctor`** bằng `InitializeArray` từ blob build-time ⇒ "filled at runtime" sai; đúng hơn là "filled from build data, content unreadable" |
| 133 (handle slot) | "handle slot `0x2ae0010`/`0x2ae0018` chưa giải ⇒ chưa biết lệnh nào điền field nào" | Lệnh nào điền field nào **biết được** nhờ store kề sau call; cái chưa biết chỉ là **byte** trong blob ⇒ block hẹp hơn nhiều |

Đây là loại sửa quan trọng vì nó đổi *hướng* của việc đào tiếp: không cần tìm consumer trong code nữa (đã có), mà cần bảng metadata usage.

---

## 6. Vì sao byte vẫn chưa đọc được

`InitializeArray(array, handle)` nhận `RuntimeFieldHandle` từ cell; cell đó là một *metadata usage* trỏ tới field của `<PrivateImplementationDetails>`. Bảng usage không có trong repo (168 đã kiểm: không có `global-metadata.dat`). Nên chỉ còn cách thử theo **nội dung**:

| Kiểm | Số |
|---|---|
| Field `<PrivateImplementationDetails>` trong `field-defaults.json` | **982** |
| Blob đúng **24 byte** (6 × 4) | **99** |
| Đọc 24 byte đầu thành 6 `float` và đòi mọi giá trị ∈ [0.25, 4.0] | **7** |
| Trong 7 cái đó, đã được `ia-resolved.json` gán cho ctor khác | **3** (`7BB8C603…`, `849203E6…`, `C9A0FA1D…`) |
| Còn lại | **4**: `39FCC36F…` `[0.8, 1.0, 1.5, 2.0, 2.5, 3.0]` · `4F6F5A47…` `[2.67, 2.67, 2.25, 2.0, 1.875, 2.0]` · `98B3C479…` `[4.0, 4.0, 3.75, 3.0, 2.25, 3.0]` · `D838203D…` `[1.0, 1.0, 0.6, 1.0, 0.6, 0.8]` |

Không ứng viên nào nằm cạnh data của `rewardIndexs` (`data_index 30944`; các láng giềng là 30888/30904/30928/30976/30992/31008), nên **không** có cơ sở chọn một blob. Bốn ứng viên được ghi lại đúng như *ứng viên*, không phải kết luận.

Blob của `rewardIndexs` thì đọc được (133 đã pin): data_index **30944**, sáu giá trị `[23, 0, 14, 1, 15, 18]` — đây là *reward id*, khớp với `OnClickHunterCollect` xử lý các id đó.

---

## 7. `Board_PVP..cctor`

88 B / **22 lệnh**: guard `ldrb w8, [x19, #0x448]` + `tbnz` (chống chạy hai lần) → `ldr x20, [x20, #0x238]` (cell static, `adrp 0x2adf000`) → `ldr x8, [x20]` → `ldr x8, [x8, #0xb8]` (struct lồng) → `ldr d0, [x9, #0xfe8]` (`adrp 0x757000` ⇒ `.rodata` `0x757fe8`) → `str d0, [x8]` · `str xzr, [x8, #0x10]` · `str wzr, [x8, #0x18]`.

Tức `.cctor` chỉ **zero một struct 3 slot** (một double + hai zero); **không** đụng tới sáu mảng — sáu mảng được điền ở `.ctor`.

---

## 8. Giới hạn và open item

1. **Bốn blob ứng viên** (§6) — không chọn được nếu không có bảng metadata usage ⇒ `MODEL_NOT_MEASURED runtime`.
2. **Giá trị double ở `.rodata` `0x757fe8`** (khởi tạo một slot của struct static trong `.cctor`) — địa chỉ suy được từ `adrp 0x757000` + `ldr d0, [x9, #0xfe8]`, nhưng không window rodata nào trong 8 slice phủ địa chỉ này ⇒ `MODEL_NOT_MEASURED runtime`.
3. **Ngữ nghĩa từng stage** (`index 0..5` tương ứng màn/chặng nào) — code chỉ chứng minh bộ ba mảng cùng index, không nói index nghĩa là gì.
4. Không khẳng định `rewardScales` là 4 ứng viên nào trong §6; báo cáo chỉ nêu số lượng và giá trị của chúng.

---

## 9. Cách tái lập

```bash
python3 tools/verify/pvp_reward_arrays.py        # in bytes/sha256/28 check, ghi lại artifact
python3 -m unittest tests.test_pvp_reward_arrays -v
python3 tools/verify-claims.py                   # APKD1 + AI1 đã sync theo báo cáo này
```

Verifier đọc `dump.cs`, 8 slice, `field-defaults.json`, `ia-resolved.json` và artifact 132/133; mọi RVA ghi dạng **thập phân**.
