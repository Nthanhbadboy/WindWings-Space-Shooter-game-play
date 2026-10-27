# 173 — Cổng chống trôi: hợp đồng mở khoá cho 37 mục mà audit chưa gọi là `CLOSED`

**Trạng thái:** `DECODED_STATIC` (chỉ đọc artifact + slice đã bóc; không chạy game)
**Lớp bằng chứng:** STATIC-ONLY. Đây **không phải** một lần bóc mới — nó là cổng đọc lại **mọi** artifact của lane và đối chiếu với `open_items_audit`.
**Artifact:** `datas/l2_535b0541_audit_drift.json.gz` — **7828 B**, sha256 `9e5c7a63ca94a23a0ff0f0902590255d20896c06badd851fc608caf6c1fb0d4d` (bản 176/172/177 sinh lại; 173 gốc 7895 B / `6a8a4bd5…`)
**Verifier:** `tools/verify/audit_drift.py` (**19 check**) · **Test:** `tests/test_audit_drift.py` (**42 test**)
**Đọc:** 43 artifact `datas/l2_535b0541_*.json.gz` · **Đối chiếu:** 56 mục của audit (19 `CLOSED` · 20 `RUNTIME` · 10 `OPEN` · 6 `RESTATED` · 1 `NOTE`)

---

## 0. TL;DR

| | 170 làm | 173 làm |
|---|---|---|
| Audit biết report nào | `REPORTS` viết tay, thêm 168/169 bằng tay | cổng đọc **43** artifact, suy report từ `AUDIT.REPORTS` **+ tên file report** → **43/43** (174) |
| Câu "168 đóng mục 11" | người đọc rồi chép vào `records` | **R2**: `closed[n]` phải khớp `verdict == CLOSED` **và** `closer == report` |
| Câu "169 sửa mục 39" | chép tay | **R3**: phải thấy trong `records`, hoặc `RESTATED`+closer, hoặc `reason` có số report |
| Mục bị chặn | ghi lý do bằng văn xuôi | **R4** + hợp đồng 37 dòng: `step`, `owner`, `kind` cho **từng** mục chưa `CLOSED` |
| Trôi tiếp | vẫn trôi | **fail** khi một artifact nêu số mục mà report của nó không có tên ở cả hai nguồn (**R1**), hoặc sửa mức-report nhắm vào report không đặt tên được (**R5**) |

Kết quả chạy: **19/19 check PASS**, **20 luật**, **0 luật hỏng**, **37 dòng hợp đồng**, **0 dòng `TODO`** — và một **lỗ mù 21 artifact** được ghi tên (mục 4).

---

## 1. Vì sao "snapshot tay" là lỗi hệ thống, không phải lỗi một lần

170 đã dạy `open_items_audit` đọc 168/169. Cách đó đúng cho hôm nay và **sai** cho tuần sau: audit chỉ thấy những report mà ai đó **nhớ** thêm vào `REPORTS`. Mọi report viết sau 170 sẽ lại rơi ra ngoài — đúng cái đã xảy ra với 149 (mục 4).

173 đảo chiều: thay vì audit tự khai nó đọc gì, **cổng đọc hết** rồi hỏi audit. Ba tính chất làm nó không trôi lại:

1. **Danh sách nguồn là glob, không phải list**: `datas/l2_535b0541_*.json.gz`, trừ `lane_closeout`, `open_items_audit` và chính nó. Thêm artifact mới là **tự động** vào cổng.
2. **Ánh xạ report lấy từ chỉ mục**, không có bảng viết tay: `report_of(stem)` tra ngược tên topic trong `AUDIT.REPORTS` **và** trong tên file `docs/apk-analysis/<n>-535b0541-<topic>.md`. Không tra được ở cả hai ⇒ `report = None` ⇒ **R1 hỏng**. (173 gốc chỉ có `AUDIT.REPORTS` ⇒ 22/43; 174 thêm nửa tên-file ⇒ 43/43, xem §4.1.)
3. **Hợp đồng suy ra từ verdict**, không chép lại: mục `RUNTIME` chưa viết bước riêng thì nhận `DEFAULTS['RUNTIME']` = `device or served state — MODEL_NOT_MEASURED runtime`. Chỉ 17 mục cần bước **đặc thù** mới nằm trong `CONTRACT`.

---

## 2. Năm luật

| luật | câu hỏi | hỏng khi |
|---|---|---|
| **R1 coverage** | artifact nêu số mục thì report của nó có tên trong chỉ mục? | `report is None` hoặc report lạ |
| **R2 closure** | "tôi đóng mục *n*" có đúng là audit ghi `CLOSED` **do chính report đó**? | verdict khác `CLOSED`, hoặc `closer` là report khác |
| **R3 correction** | "tôi sửa mục *n*" có dấu vết trong audit? | không có `records[report, correction, n]`, không `RESTATED`+closer, `reason` không nhắc số report |
| **R4 blocker** | "mục *n* bị chặn" có mâu thuẫn với việc chính report đó đóng nó? | audit ghi `CLOSED` bởi cùng report |
| **R5 target** | sửa **mức-report** ("report X sai") có trỏ vào report audit **đặt tên được**? | `target` rỗng hoặc không có trong `REPORTS` |

Ba loại câu được trích ra khỏi artifact: khoá `closed` / `corrected` / `blocked` có trường `n` (⇒ claim theo mục), và `corrections` / `corrected` **không** có `n` nhưng có `target` (⇒ claim mức-report).

---

## 3. Kết quả trên dữ liệu thật

| | số | ghi chú |
|---|---|---|
| artifact được quét | **43** | toàn bộ lane, trừ audit/closeout/chính nó |
| claim theo mục | **9** | tất cả đến từ `lane_residue` (168): **2** `closed`, **2** `corrected`, **5** `blocked` |
| claim mức-report | **2** | cả hai từ `cell_identity` (149): nhắm report **138** và **149** |
| luật đã chạy | **20** | `9 × 2 + 2` — mỗi claim theo mục bị kiểm **hai** lần (R1 + luật riêng của nó) |
| luật hỏng | **0** | |
| mục chưa `CLOSED` | **37** | 56 − 19 |

Chín claim của 168 đều **đứng vững** dưới luật mới: hai mục 11/29 đúng là `CLOSED` do **168**, hai mục 12/49 đúng là `RESTATED` do **169** (R3 thoả qua `records`), năm mục bị chặn không mục nào bị 168 đóng. Nói cách khác 170 không phải chỉ "chép lại cho khớp" — nó khớp **vì** dữ liệu đúng; 173 chỉ là cái máy kiểm tra điều đó mãi mãi.

---

## 4. Phát hiện: audit chỉ đặt tên được **22/43** artifact

`AUDIT.REPORTS` có **22** khoá: liền mạch `127…146`, rồi nhảy `168`, `169`. Đối chiếu với 43 artifact cổng đọc:

| | số | |
|---|---|---|
| artifact cổng đọc | **43** | |
| artifact `AUDIT.REPORTS` **đặt tên được** | **22** lúc 173 đo | nay **43** — 175 vá bảng, xem §4.2 |
| artifact **không** đặt tên được bằng bảng đó | **21** | `cell_identity`, `arena_rewards`, `exchange_chain`, … |
| report thiếu trong `REPORTS` (cửa sổ report **có artifact**, 127–172) | **24** | `147…167` + `170`, `171`, `172` — nay **0** |

Đây là **lỗ mù thật**, không phải chuyện của riêng một report. Cổng hôm nay vẫn xanh **vì** trong 21 artifact không tên kia chưa cái nào đóng/chặn một mục audit — chỉ `lane_residue` (168, có tên) làm việc đó. Ngày đầu tiên một trong 21 artifact đó nói "mục 44 đã xong", **R1 sẽ nổ**, và nổ đúng.

### 4.1 Cách 174 vá: chỉ mục lấy từ tên file report

Tên file đã mang số: `docs/apk-analysis/<n>-535b0541-<topic>.md`. Nên `report_of` tra trong **hợp** của hai nguồn: `AUDIT.REPORTS` (127…146, 168, 169) và tên file (133…173). Kết quả trên cùng 43 artifact:

| | 173 gốc | sau 174 | sau 175 |
|---|---|---|---|
| artifact có tên report | **22/43** | **43/43** | **43/43** |
| artifact không tên | **21** | **0** | **0** |
| sửa đổi mức-report nhắm report **không** tên được (`unread_targets`) | **`[149]`** | **`[]`** | **`[]`** |
| `AUDIT.REPORTS` thiếu (cửa sổ artifact) | 24 report | **24** | **0** — bảng có **49** khoá, `127…175` liền mạch |
| nguồn ánh xạ | bảng viết tay | bảng ∪ tên file | **bảng tự điền từ tên file** |

Chỗ đáng chú ý: **149 không phải `cell_identity`**. Đó là **erratum của chính 173**:

| nói | thực tế |
|---|---|
| "`cell_identity` (149)" | `cell_identity` = **150** (`docs/apk-analysis/150-535b0541-cell_identity.md`) |
| — | **149** = `pvp_hunter_arrays` (`docs/apk-analysis/149-535b0541-pvp_hunter_arrays.md`) |

Lỗi này **không đổi kết luận** (cả 149 lẫn 150 đều không có trong `REPORTS`), nhưng nó đổi **tên miền** của câu sửa: dòng `corrections` thứ hai của `cell_identity` nhắm report **149** = `pvp_hunter_arrays` — tức nó sửa câu "chỉ biết offset +0x10/+0x14/+0x18" mà **149** đã viết, không phải tự sửa mình. Đúng ngữ nghĩa `target` hơn hẳn.

Sau 174, hai check canh việc này: `every-artifact-maps-to-a-report-now-that-the-docs-are-the-index` (0 artifact không tên) và `no-report-level-correction-points-at-an-unknown-report` (`unread == []`). Cái bẫy đổi chiều: giờ **thiếu file report là R1 nổ**, thay vì thiếu dòng trong bảng viết tay.

### 4.2 Cách 175 vá tận gốc: bảng của audit tự điền

174 để `AUDIT.REPORTS` nguyên (sửa nó là đổi hash 170 trong artifact đang băm nó). 175 kiểm lại giả định đó và thấy **sai**: `REPORTS` là **chỉ mục**, không mục nào, proof nào hay digest nào sống trong đó — `by_report` bỏ qua report không có item (`if not own: continue`). Nên điền thêm **27** khoá **không đổi một byte** của artifact:

| | trước 175 | sau 175 |
|---|---|---|
| khoá trong `REPORTS` | 22 | **49** (`127…175`, không lỗ) |
| sha256 artifact audit | `3b782ffa…` | **`3b782ffa…` — y nguyên** |
| `blind_spot.reports_the_audit_cannot_name` | 24 | **`[]`** |
| `blind_spot.named_by_the_audit` | 22 | **43** |

Cách làm giống 174: `_doc_index()` đọc tên file, `REPORTS.setdefault(...)` điền chỗ trống; dòng pinned vẫn thắng nên bí danh `134`/`136` (`pvp_manager_rules` ≠ `pvp_manager_rules_tables`) không bị ghi đè. Thêm một assert không lỗ hổng: `set(range(min, max+1)) == set(REPORTS)`.

Vì sao điều này quan trọng hơn vẻ ngoài: **chu trình hash là lo ngại đúng, nhưng lo ngại đó không áp dụng cho một chỉ mục**. Kiểm bằng số (sha không đổi) rẻ hơn nhiều so với sinh lại 168 → 170 → 172 → 173 theo thứ tự — và nếu không kiểm, ta đã tự trói mình vào một bảng viết tay mãi mãi.

## 5. Ba chỗ 173 tự sửa chính mình

Viết cổng rồi đọc lại kết quả là cách duy nhất để thấy cổng có nói thật không. Ba lỗi bị bắt ngay trong lượt này:

| chỗ | sai | sửa |
|---|---|---|
| `four-items-need-an-owner-policy-decision` | tên nói **bốn**, tập là **năm** (30/39/40/51/52) | đổi tên thành `five-items-…` và kiểm đúng tập năm |
| check POLICY | `A == [30,39,40,51,52] or A == [30,39,40,51,52]` — vế thứ hai chép lại vế đầu, **luôn đúng** | bỏ vế lặp; điều kiện còn **một** vế |
| `CONTRACT[9]` | 170 xếp mục 9 ("medal shop prices / stock") vào nhóm **served payload**; 173 chép verdict `RUNTIME` nên đẩy nó sang nhóm thiết bị | trả 9 về `DATA`; nhóm `DATA` là **sáu** mục `[9,18,19,34,44,48]`, `RUNTIME` còn **19** |

Vế lặp của check POLICY là ví dụ đẹp nhất cho lý do phải có test: một check **luôn đúng** trông giống hệt một check **đang đúng**. Test `test_r3_…`/`test_r4_…` vì thế chạy luật trên hàng **tổng hợp** (dựng row giả, claim giả) chứ không chỉ đọc artifact — nếu không, ta chỉ đang test lại snapshot.

---

## 6. Hợp đồng mở khoá — 37 dòng

Mỗi mục chưa `CLOSED` có đúng ba trường: **bước kế tiếp là gì** (`step`), **ai làm được** (`owner`), **loại chặn** (`kind`).

| kind | số mục | mục | nghĩa |
|---|---|---|---|
| `RUNTIME` | **19** | 1, 4, 10, 13, 16, 20, 21, 24, 28, 35, 36, 37, 38, 41, 43, 45, 47, 53, 55 | trạng thái thiết bị/dịch vụ — `MODEL_NOT_MEASURED runtime` |
| `DATA` | **6** | 9, 18, 19, 34, 44, 48 | phải có payload được phục vụ (shop, config, league) |
| `POLICY` | **5** | 30, 39, 40, 51, 52 | chỉ còn đường **probe native** — lệnh chủ dự án 26/10 **cấm** |
| `PIN-RAW` | **3** | 12, 49, 50 | cần một raw chưa ghim (`ToRoman` 21103836, `GetText` 21202600, `get_pathRoot`) |
| `INDEX` | **2** | 27, 54 | nửa "index" của bảng khoá tính toán; 146 đã có 51 record/14 tiền tố |
| `SCAN` | **1** | 32 | quét rộng hơn: từ *call* sang *store* trên `0x50/0x54/0x58` |
| `NOTE` | **1** | 56 | không phải lỗ hổng — ghi để index đủ |

`owner` chia làm hai: **`owner`** (chủ dự án — cần thiết bị/payload/quyết định chính sách) và **`AI-4`** (còn làm được tĩnh: 12, 27, 32, 49, 50, 54, 56 — **bảy** mục).

### 6.1 Năm mục `POLICY` — vì sao không có bước tĩnh nào

| mục | cần gì | vì sao tĩnh không được |
|---|---|---|
| 30 | hai blob `Board_PVP` (`rewardValues`, `rewardScales`) | chúng là **cell metadata**; tên gọi nằm trong bảng *metadata usage*, không có trong repo |
| 39 | tên của slot `0x2ae0010` (`rewardValues`) | cùng bảng |
| 40 | tên của slot `0x2ae0018` (`rewardScales`) | cùng bảng |
| 51 | `JsonParse.FromJson<object>` lấy type từ slot `0x2AE1000` | không phải string literal, mà là type handle |
| 52 | class đứng sau slot `0x2ADB958` | không symbol nào trong slice đặt tên nó |

Đã kiểm lại trong lượt này: `reverse-engineering/il2cpp/ia-resolved.json` chỉ có **17** bucket method, `raw/ui-audit/metadata-slots.json` là **PROVISIONAL** và chỉ chứa đúng các địa chỉ đã hỏi (ví dụ `0x2adbd98`, `0x2addc68`), `raw/il2cpp-consts/` không có `Board_PVP`. **Không đi tìm lại bảng đó nữa** — muốn có nó phải chạy probe native, và lệnh 26/10 cấm.

---

## 7. Cổng này **không** làm gì

Ba giới hạn, ghi trong artifact ở khoá `limits`:

1. R1–R5 chỉ bắt **câu có nêu tên**. Một report đóng mục 44 bằng cách viết "đã xong" mà không ghi `n: 44` thì vẫn vô hình. Muốn bắt loại đó phải đọc văn — không tự động hoá được ở mức này.
2. Hợp đồng ghi **ai làm được**, không ghi **ai sẽ làm**. `owner` = quyết định, không phải cam kết.
3. `POLICY` ở đây là **kết luận**, không phải chỗ trốn: nó chỉ dùng khi đường tĩnh duy nhất còn lại là probe bị cấm.

---

## 8. Tái lập

```bash
python3 tools/verify/audit_drift.py            # ghi artifact, in totals, fail nếu có check hỏng
python3 -m unittest tests.test_audit_drift -v  # 42 test: pin byte + luật trên dữ liệu tổng hợp
```

Artifact băm **input** (`open_items_audit`, sha256 `3b782ffa…`) và băm **cả 43 artifact** nó đọc, nên đổi bất kỳ artifact nào là test pin gãy ngay — đúng ý đồ: số trong report phải truy được về file.
