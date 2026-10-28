# 170 — Cho audit đọc 168/169: 2 mục đóng thêm, 3 mục thu hẹp, 1 mục chuyển sang runtime

**Trạng thái:** `DECODED_STATIC` (chỉ đọc artifact đã pin; không disassembly mới, không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Mỗi verdict là một **proof chạy lại được** trên artifact của báo cáo đã đóng mục đó.
**Artifact:** `datas/l2_535b0541_open_items_audit.json.gz` — **10 748 B**, sha256 `3b782ffa0f8605b7ea0632803ef662a9c792b9c0a59293aef1b7772fae33a0d3`
**Verifier:** `tools/verify/open_items_audit.py` (56 mục · **28 proof**) · **Test:** `tests/test_open_items_audit.py` (**32 test**)
**Trước:** 148 (audit gốc, ảnh chụp tại 147) · 168 (residue) · 169 (sáu mảng `Board_PVP`)

---

## 0. Vì sao có báo cáo này

148 đóng băng verdict cho 56 mục mở **như chúng đứng ở 147**. Từ đó lane đóng thêm hai mục và thu hẹp ba mục, nhưng `open_items_audit.py` chỉ biết `REPORTS` 127–146, nên artifact vẫn in `closed 17 / restated 3 / actionable 2 / runtime 19 / still_open 14` — **sai ở 4 ô** so với chính các artifact mà lane đã ship.

Đây là lỗi *inventory*, không phải lỗi dữ liệu: audit tự nhận "verdict là ảnh chụp", nhưng nó là thứ duy nhất trong lane nói "còn bao nhiêu việc", nên để nó trôi là để cả lane đọc sai số của chính mình.

---

## 1. Tổng mới

| | 148 (tại 147) | **170 (tại 169)** | Δ |
|---|---|---|---|
| items | 56 | 56 | — |
| câu hỏi riêng biệt | 53 | 53 | — |
| **đóng** | 17 | **19** | **+2** |
| **thu hẹp** | 3 | **6** | **+3** |
| **gỡ chặn** | 2 | **0** | **−2** |
| **runtime** | 19 | **20** | **+1** |
| ghi chú | 1 | 1 | — |
| **còn mở** | 14 | **10** | **−4** |
| proof | 24 | **28** | **+4** |

Ba con số đáng chú ý:

1. **`actionable` về 0.** Hai mục "amount/icon scale per stage" của 133 được đánh `ACTIONABLE` vì 131 đã chứng minh *đường đi* nhưng chưa ai chạy. 169 **chạy** đường đó và nó dừng ở byte ⇒ đúng ra phải là `RESTATED`, không phải "chờ chạy".
2. **`runtime` +1** vì mục "medal shop prices / stock" (127) không còn là câu hỏi tĩnh: 168 chứng minh 251 bảng ScriptableObject đã trích **không có** cột giá/tồn và **không có** asset `Shop_Pack` ⇒ giá được *serve*, không ship trong APK.
3. **`still_open` 14 → 10**: hai cái đóng (n11, n29), một sang runtime (n9), một sang thu hẹp (n30).

---

## 2. Hai mục đóng thêm

| n | Báo cáo | Mục | Đóng bởi | Proof (giá trị artifact) |
|---|---|---|---|---|
| 11 | 139 | "`rewards` consumer" | **168** | `[22795496, 22793460, 22795328]` |
| 29 | 132 | "per-call pack amount for the 20 `SaveDataReward` clones" | **168** | `[1, 'mov w2, #1', 19187472]` |

**n11** — 139 kết luận "không method nào trong raw arena-pvp index `ArenaManager.rewards` (+0x38)". 168 tìm ra: `Board_Arena.GetRewards` (22795496) index mảng tại **22795328**, sau guard `arenaRank`; chuỗi là `SetStatusRank` (22793460) → `SetRewards` (22794144) → `GetRewards`. Cái 139 thiếu không phải dữ liệu mà là *mẫu tìm*: đọc `+0x38` trên base statics không bắt được vì index đi qua `userProfile.arenaRank`.

**n29** — mục này còn sai cả **tiền đề**: "20 clone" là 20 nhánh store trong **một** thân hàm `SaveDataReward` (1108 B), và chỉ có **một** call site: `TimeFreeRewardPack.GetRewards`, truyền `mov w2, #1` tại 19187452. Số lượng là literal, không phải `_value` từ pack data.

---

## 3. Ba mục thu hẹp (closer = 169)

| n | Báo cáo | Mục | Trước | Sau |
|---|---|---|---|---|
| 30 | 132 | "PvP stage reward types and amounts" | OPEN | RESTATED |
| 39 | 133 | "amount per stage (`rewardValues`)" | ACTIONABLE | RESTATED |
| 40 | 133 | "icon scale per stage (`rewardScales`)" | ACTIONABLE | RESTATED |

Proof dùng chung: `169-pvp-arrays` = `[6, 6, ['0x198','0x1a0','0x1a8','0x208','0x210','0x218']]` và `169-blob-census` = `[982, 99, 7, 3, 4]` (PID field · blob đúng 24 B · đọc ra 6 float hợp lý · đã thuộc ctor khác · còn lại).

- **n30**: 169 chỉ ra `Board_PVP` **không có** field `rewardTypes`, và hai mảng kia điền **trong `.ctor`** bằng 6 lệnh `InitializeArray` — nên nửa "types" của câu hỏi không có đối tượng, nửa "amounts" bị chặn ở byte.
- **n39/n40**: đây là chỗ 148 lạc quan nhất. "Gỡ chặn" nghĩa là *đường đã có, việc chưa làm*; 169 làm rồi và kết quả là **không bind được** — 4 ứng viên 24 B, không cái nào cạnh blob `rewardIndexs` (data_index 30944). Chặn mới là **bảng metadata usage**, không phải công cụ.

---

## 4. Một mục chuyển sang runtime

| n | Báo cáo | Mục | Verdict | Lý do |
|---|---|---|---|---|
| 9 | 127 | "medal shop prices / stock" | **RUNTIME** | 146 pin hình dạng khoá (`ARENA_SHOP_ITEM_ID`/`_STOCK`, ba band); 168 đóng phần dữ liệu theo chiều ngược: 251 bảng ScriptableObject đã trích **không có** cột giá/tồn, **không có** asset `Shop_Pack` ⇒ giá được serve. |

Đây là ca `MODEL_NOT_MEASURED runtime` đúng nghĩa: không phải "chưa đào", mà là "APK không chứa".

---

## 5. Hai lý do được sửa theo 168

`open_items_audit` giữ nguyên **text** của mục (lấy từ artifact nguồn, không chép 147), nhưng phần `reason` thì do audit viết — và hai chỗ vẫn đang nói bằng giọng cũ:

| n | Câu cũ | Sửa |
|---|---|---|
| 49 | "GetText không có trong raw nào" | body **không** có, nhưng **127** call site chạm tới nó |
| 12 | "RVA 21103836 xuất hiện trong 0 raw" | body không có, nhưng **2** call site (19885148, 21285196) |

Cả hai mục vẫn `OPEN` (thiếu **thân hàm**, không thiếu người gọi), nên không đổi verdict — chỉ đổi lý do. Đây là loại sửa mà 168 đã làm một lần và lần này audit chép lại cho đúng.

---

## 6. Audit giờ đọc gì

```python
REPORTS = {..., 168: 'lane_residue', 169: 'pvp_reward_arrays'}
PROOFS  = {..., '168-rewards-chain': …, '168-save-data': …, '168-reasons': …,
                '169-pvp-arrays': …, '169-blob-census': …}
RECORDS = [..., (168, 'correction', 12), (168, 'correction', 49)]
sources = 20 artifact lane + closeout 147 + **2 artifact của 168/169**
```

Một khác biệt schema phải xử lý: **168 đặt tên danh sách là `corrected`**, không phải `corrections` như các báo cáo khác. Audit chấp nhận cả hai tên cho `RECORDS`, và ghi rõ trong code rằng lane không nhất quán — thay vì sửa artifact cũ (đã ship, đã pin).

Vòng lặp phải tránh: 168 đã băm artifact này vào `provenance` của nó, nên nếu 170 băm ngược
artifact 168 thì hai báo cáo không bao giờ hội tụ (168 → audit → 168). Vì vậy 168/169 được đọc
**qua `PROOFS`** (giá trị, không phải digest) — và 168 phải rebuild một lần vì `census` của nó
trích verdict cũ; xem ERRATA ở đầu 168.

`next_steps` cũng được viết lại: bước 1 giờ là *bảng metadata usage* (chặn thật của 169), bước 2 giữ nguyên `GetText`, bước 3 là **decode `SetupHunters` + `<GetPvPUserCachingDatas>d__78.MoveNext`** — tức việc kế tiếp của lane, thay cho "tìm consumer của `rewards`" vì 168 đã tìm ra.

---

## 7. Cái gì **không** đổi

- 56 mục, 53 câu hỏi riêng biệt, 3 cặp trùng (`[3,25]`, `[27,54]`, `[34,48]`), 11 bản ghi gốc + 2 mới.
- Text `blocking` vẫn lấy từ artifact nguồn, không cắt 220 ký tự, không `str(None)`.
- Ba `corrections` của 148 vẫn nhắm 147; chỉ con số `by_semantics` đổi 19 → 20 (n9).
- `lane_closeout` không đổi: nó vẫn là bộ 20 báo cáo 127–146.

---

## 8. Open item của chính báo cáo này

1. **Audit vẫn là ảnh chụp.** Nó biết 168/169 vì được thêm tay; báo cáo 171 trở đi sẽ lại làm nó trôi. Cách sửa đúng là để audit **quét** `datas/l2_535b0541_*.json.gz` và tự đọc `corrections`/`closed` của báo cáo mới nhất — nhưng làm vậy sẽ đổi luôn `provenance` và vòng pin của 4 báo cáo khác, nên tách thành việc riêng.
2. **n30 vẫn có thể tách làm hai** ("types" = đã trả lời là *không tồn tại*; "amounts" = chặn ở byte). Báo cáo giữ nguyên một mục để không đổi bộ 56 của 147.
3. **`169-blob-census` là proof theo nội dung**, không theo danh tính: nếu sau này có bảng metadata usage, proof này phải đổi thành so *slot → field*, không phải đếm blob.

---

## 9. Tái lập

```bash
python3 tools/verify/open_items_audit.py     # in bytes/sha + totals, ghi lại artifact
python3 -m unittest tests.test_open_items_audit -v
python3 tools/verify/lane_residue.py         # 168 rebuild theo audit mới (32/32)
python3 tools/verify-claims.py               # APKD1 đếm lại số .md (đã sync 115/147)
```

Artifact là `json.dumps(sort_keys=True, separators=(',',':'))` rồi `gzip.compress(mtime=0)` ⇒ byte ổn định; test `test_rebuild_reproduces` so bản dựng lại với bản đã pin.
