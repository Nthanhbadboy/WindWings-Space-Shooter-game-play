# 171 — `Board_PVP.SetupHunters`: 12 điểm, 6 hộp thưởng, và "đã nhận" là dữ liệu máy

**Trạng thái:** `DECODED_STATIC` (một method đọc hết từ slice đã pin; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mọi khẳng định dưới đây là một lệnh cụ thể trong `Board_PVP.SetupHunters` (19791640, 1124 B, 281 lệnh); 35 landmark được kiểm bằng `(rva, mnemonic op_str)` chính xác.
**Artifact:** `datas/l2_535b0541_pvp_setup_hunters.json.gz` — **5170 B**, sha256 `0d60c01519acaef1b76329ec72ffa554db22e5516d0012c123f4298d6013e0e1`
**Verifier:** `tools/verify/pvp_setup_hunters.py` (**26 check**) · **Test:** `tests/test_pvp_setup_hunters.py` (**36 test**)
**Trước:** 169 (sáu mảng ↔ sáu field) · 167/166 (phía `Box_Rewards`) · 163 (lambda `onExit`)

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | § |
|---|---|---|
| Sáu mảng thưởng dùng ở đâu? | Trong `SetupHunters`: 12 điểm `WinPoint`, **điểm lẻ** nhận hộp thưởng, `k = (i−1)/2` ⇒ 6 hộp | §2 |
| Hộp nhận gì? | `SetInfo(boxSpr = GetBoxSpriteGeneral(rewardIndexs[k]), iconSpr, number = rewardValues[k], isCards, scale = rewardScales[k])` | §3 |
| `isCards` bằng gì? | `(id & 0xfffffffe) == 14` ⇒ đúng id **14, 15** là loại "card" | §4 |
| Icon lấy từ đâu? | 3 nhánh theo id: 14 → `+0x58`, 15 → `+0x50`, còn lại → `[list + id*8 + 0x20]` | §4 |
| "Đã nhận" đọc từ đâu? | **Không** đọc mảng thưởng: `PlayerPreferences.GetInt(prefix + i, 0) == 1` | §5 |
| Ai bắt click? | `wp.onClick = new Action<WinPoint>(this)` (rva 19792464 → lưu `[wp+0x40]` 19792632) | §6 |
| Còn mở gì? | nội dung `rewardValues`/`rewardScales` (169), nội dung 3 nhánh icon (asset), giá trị prefix, `d__78.MoveNext` | §8 |

---

## 1. Vì sao báo cáo này

169 trả lời "mảng nào ↔ field nào" và "ai đọc", nhưng reader chỉ là *danh sách RVA*. Câu hỏi thật của lane là: **sáu hàng thưởng của PvP hiển thị gì, và trạng thái "đã nhận" đến từ đâu** — nếu nó đến từ server thì phải là `MODEL_NOT_MEASURED runtime`, còn nếu từ file save cục bộ thì đó là câu trả lời khác hẳn.

Đồng thời 169 để lại một cái bẫy tên: có **hai** method tên `IsCollected`. Cái mà 169 thấy trong danh sách reader là local function `<>c__DisplayClass79_0.<IESummarySeasonRewards>g__IsCollected|0` (19811092) — nó **mới** đọc mảng. Còn `Board_PVP.IsCollected(int)` (19792764) mà `SetupHunters` gọi thì **không** đọc mảng nào. Báo cáo này đọc đúng cái thứ hai.

---

## 2. Mười hai điểm, sáu thưởng

`allPoints` là `WinPoint[]` (field 0x190). Vòng lặp:

```
19792220  ldr x8, [x19, #0x190]     ; allPoints
19792224  cbz x8, → 19792756        ; null guard
19792240  ldr w9, [x8, #0x18]       ; array length
19792244  cmp w20, w9 / b.ge        ; i < Length
19792252  add x8, x8, x29, lsl #3 / ldr x8, [x8, #0x20]   ; element i
19792260  ldr x0, [x8, #0x28]       ; wp.boxRewards
19792264  bl  41415048              ; Component.get_gameObject
19792268  and w1, w20, #1
19792272  bl  41424900              ; GameObject.SetActive(i & 1)
19792276  tbz w20, #0, → 19792604   ; chẵn: nhánh "đã nhận"
```

Điểm **chẵn** chỉ bật/tắt `collectedObject`; điểm **lẻ** mới điền hộp thưởng. Chỉ số thưởng:

```
19792292  sub w9, w20, #1
19792296  cmp w9, #0
19792300  csel w9, w20, w9, lt      ; (i-1) nếu >= 0, ngược lại i
19792304  asr w11, w9, #1           ; k = (i-1) >> 1
```

Với 12 điểm: i = 1,3,5,7,9,11 → k = 0…5 ⇒ **6 hộp**, khớp đúng 6 phần tử của mảng (169). `tbl` trong artifact ghi cả 12 dòng.

---

## 3. Hộp thưởng nhận gì (`SetInfo`)

Ba mảng được đọc ngay trước lời gọi, mỗi cái bằng một `ldr` khác nhau:

| Đối số `SetInfo` | Giá trị | Lệnh |
|---|---|---|
| `_boxSpr` (x1) | `GetBoxSpriteGeneral(rewardIndexs[k])` | 19792180 `bl 20180172` → 19792224 `mov x1, x0` |
| `_number` (w3) | `rewardValues[k]` | 19792196 `ldr w23, [x8, #0x20]` → 19792240 `mov w3, w23` |
| `_scaleIcon` (s0) | `rewardScales[k]` | 19792212 `ldr s0, [x8, #0x20]` |
| `_isCards` (w4) | `(id & ~1) == 14` | 19792188 `and w8, w21, #0xfffffffe`, `cmp #0xe`, 19792228 `cset w4, eq` |
| `_iconSpr` (x2) | sprite theo 3 nhánh (xem §4) | 19792236 `mov x2, x22` |
| gọi | `Box_Rewards.SetInfo` 19990656 | 19792252 `bl` |

`_number` ở đây **không** phải `rewardIndexs[k]`: id chỉ dùng để chọn sprite và cờ card; số lượng hiển thị là `rewardValues[k]`.

---

## 4. Ba nhánh icon và cờ "card"

`rewardIndexs[k]` được so với hai hằng: `#0xe` (14) và `#0xf` (15).

| id | Icon lấy từ | Lệnh |
|---|---|---|
| 14 | `[singleton+0xb8] → +0x58` | 19792148 `add x8, x0, #0x58` |
| 15 | `[singleton+0xb8] → +0x50` | 19792124 `add x8, x0, #0x50` |
| khác | `[list + id*8 + 0x20]` (bounds-checked) | 19792176 `add x8, x8, x21, lsl #3; add #0x20` |

Cờ card là `(id & 0xfffffffe) == 14` ⇒ true cho **id 14 và 15**. Đây chính là `_isCards` mà 166/167 đo ở phía `Box_Rewards` (hiện badge "card"), nay có điều kiện sinh ra nó.

---

## 5. "Đã nhận" là PlayerPreferences, không phải mảng thưởng

`Board_PVP.IsCollected(int)` (19792764, 172 B, **43 lệnh**) — **0** lệnh đọc 0x198/0x1a0/0x1a8:

```
19792840  bl 34616120     ; Int32.ToString()
19792868  ldr x8, [x20]   ; tiền tố từ cell 0x2adffa8 (adrp 0x2adf000 + 0xfa8)
19792884  bl 33439876     ; String.Concat(prefix, i)
19792908  bl 20912668     ; PlayerPreferences.GetInt(key, 0)
19792908  cmp w0, #1  /  cset w0, eq
```

Hệ quả:

1. trạng thái "đã nhận" là **một khoá lưu máy cho mỗi điểm** (0…11), không đồng bộ từ server;
2. nó độc lập với `rewardIndexs` ⇒ đổi bảng thưởng không đổi trạng thái đã nhận;
3. giá trị cụ thể của tiền tố là chuỗi trong cell ⇒ `MODEL_NOT_MEASURED runtime`.

---

## 6. Click và thanh tiến trình

- `wp.onClick = new Action<WinPoint>(this)`: `bl 25843072` (`Action<WinPoint>..ctor`) tại 19792464, lưu `str x21, [x22, #0x40]` tại 19792632 (chỉ nhánh điểm chẵn).
- `allDieObjects` (0x170): `SetActive(i < get_SeasonDies())` — 19791816 gọi getter, 19791840 `bl SetActive`.
- Thanh tiến trình `lineProgress` (`SpriteRenderer` 0x188): `get_size` 19792536 → `size = get_SeasonProgress() * 1.5` (`fmov s2, #1.50000000` 19792552, `fmul` 19792556) → `set_size` 19792564.
- Hai con của thanh: `GetChild(0)` 19792596 → `SetActive(progress > 0)`; `GetChild(1)` 19792672 → `SetActive(progress == allDieObjects.Length)`.
- `WinPoint.SetPointActive()` gọi ở 19792320 (nhánh chẵn, điểm đã mở).

---

## 7. Đối chiếu với 169 (không mâu thuẫn)

| 169 nói | 171 đo |
|---|---|
| `rewardIndexs`/`rewardValues`/`rewardScales` đọc bởi 3 method | đúng — `SetupHunters` là một trong ba, và đây là chỗ chúng *được dùng* |
| `IsCollected|0` (19811092) đọc cả ba mảng | đúng — nhưng đó là local function khác với `Board_PVP.IsCollected` (19792764) mà method này gọi |
| `allBet*` đọc bởi `OnChange*` + `d__78.MoveNext` | không xuất hiện trong method này (đúng: chúng thuộc luồng đặt cược) |

---

## 8. Còn mở

1. **`rewardValues[k]` / `rewardScales[k]`** — vẫn `NOT_BOUND` như 169: hộp được nối dây đúng, nhưng **không hàng nào** có số lượng hay scale cụ thể.
2. **Nội dung ba nhánh icon** — danh sách sprite ở `[singleton+0xb8]` là asset serialize, không phải code.
3. **Tiền tố khoá PlayerPreferences** (cell `0x2adffa8`) — `MODEL_NOT_MEASURED runtime`.
4. **`<GetPvPUserCachingDatas>d__78.MoveNext`** (19813332, 1808 B) — đọc cả ba ladder bet; chưa đọc ở đây (ghi trong `boundary.not_consulted`), là việc của báo cáo sau.

---

## 9. Tái lập

```bash
python3 tools/verify/pvp_setup_hunters.py
python3 -m unittest tests.test_pvp_setup_hunters -v
```

Verifier đọc 8 slice + `dump.cs` + artifact 169; RVA in dạng thập phân.
