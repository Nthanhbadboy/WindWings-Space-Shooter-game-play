# 175 — Bảng report của audit tự điền: 22 → 48 khoá, artifact không đổi một byte

**Trạng thái:** `DECODED_STATIC` (không đọc byte mới; sửa **chỉ mục** của audit)
**Lớp bằng chứng:** STATIC-ONLY. Không có artifact mới — thay đổi chứng minh bằng **sha bất biến** của artifact 170.
**Artifact (sinh lại):** `datas/l2_535b0541_audit_drift.json.gz` — **7725 B**, sha256 `e2a5d1e72065bc71de04812f57878d610cfe517b11358ca1677847998a958251`
**Artifact (bất biến):** `datas/l2_535b0541_open_items_audit.json.gz` — **10748 B**, sha256 `3b782ffa0f8605b7ea0632803ef662a9c792b9c0a59293aef1b7772fae33a0d3` (**y nguyên** trước/sau)
**Verifier:** `tools/verify/open_items_audit.py` + `tools/verify/audit_drift.py` (**19 check**) · **Test:** 38 + 42
**Sửa:** 170 (bảng viết tay) · **Nối tiếp:** 173 §4.2, 174 §6

---

## 0. TL;DR

| | trước 175 | sau 175 |
|---|---|---|
| khoá trong `REPORTS` | **22** (`127…146`, `168`, `169`) | **49** (`127…175`, **không lỗ**) |
| sha256 artifact của 170 | `3b782ffa…` | **`3b782ffa…`** — không đổi |
| `blind_spot.named_by_the_audit` | 22/43 | **43/43** |
| `blind_spot.reports_the_audit_cannot_name` | 24 | **`[]`** |
| `unread_targets` | `[]` (nhờ 174) | **`[]`** (nhờ bảng, không cần fallback) |

174 đã cứu cổng bằng cách tra thêm tên file, nhưng để nguyên cái bảng hỏng. 175 vá cái bảng — và cái giá là **0 byte**, vì bảng đó chưa bao giờ là dữ liệu.

---

## 1. Nỗi sợ đã chặn việc này, và tại sao nó không áp dụng

173 và 174 đều ghi: *"đừng sửa `open_items_audit` trong report này — đổi nó là đổi hash 170 ngay trong artifact đang băm nó"*. Đó là lo ngại **đúng**: 168 băm artifact của 170, nên 170 ↔ 168 là chu trình, và chu trình thì không hội tụ.

Nhưng lo ngại đó nói về **dữ liệu**, còn `REPORTS` là **chỉ mục**. Đọc `build_payload()`:

```python
for report in sorted(REPORTS):        # by_report
    own = [row for row in rows if row['report'] == report]
    if not own:
        continue                      # <- report không có item: không vào payload
```

`REPORTS` chỉ được dùng ở hai chỗ: `art(report)` (nạp artifact theo topic, chỉ gọi cho report **có** item/proof) và vòng `by_report` ở trên. Thêm khoá cho report **không có item** ⇒ không dòng nào được thêm ⇒ **blob không đổi**. Đo được, không phải suy đoán:

```
trước:  {"bytes": 10748, "sha256": "3b782ffa…"}   # 22 khoá
sau:    {"bytes": 10748, "sha256": "3b782ffa…"}   # 49 khoá
```

**Bài học đáng ghi hơn cả con số:** một ràng buộc được ghi lại bằng văn xuôi (*"đừng làm X, sẽ hỏng"*) phải được **kiểm** trước khi nó chặn ba report liên tiếp. Ở đây phép kiểm mất 30 giây.

---

## 2. Sửa gì trong code

```python
def _doc_index():                      # docs/apk-analysis/<n>-535b0541-<topic>.md
    out = {}
    for path in sorted(ROOT.glob('docs/apk-analysis/*-535b0541-*.md')):
        match = re.match(r'(\d+)-535b0541-(.+)\.md$', path.name)
        if match:
            out[int(match.group(1))] = match.group(2).replace('-', '_')
    return out

for _number, _topic in _doc_index().items():
    REPORTS.setdefault(_number, _topic)        # dòng pinned thắng

assert set(range(min(REPORTS), max(REPORTS) + 1)) == set(REPORTS), \
    sorted(set(range(min(REPORTS), max(REPORTS) + 1)) - set(REPORTS))
```

Ba quyết định, mỗi cái có lý do:

1. **`setdefault`, không `update`** — tên file không phải lúc nào cũng là tên artifact. `134` là `pvp_manager_rules` (artifact) nhưng tài liệu là `pvp_manager_rules_tables`; `136` là `pvp_rank_api` nhưng tài liệu là `rank_api`. Ghi đè là `art(134)` nạp file không tồn tại ⇒ vỡ. Dòng pinned thắng, và test `test_the_pinned_names_survive_the_merge` ghim đúng ba trường hợp.
2. **Assert không lỗ** — `127…174` liền mạch. Đây là bất biến **tự duy trì**: report mới có tài liệu ⇒ bảng tự dài; report nào bị bỏ quên giữa dải ⇒ assert nổ ngay lúc import, không đợi tới lúc cổng chạy.
3. **Thêm `build(output=None)`** — 170 chỉ có `main()` ghi file. 175 cần so sha **không ghi đè**, nên tách `build()` như các verifier khác; `main()` gọi lại, hành vi và byte không đổi.

---

## 3. Kết quả đo

| | số | nguồn |
|---|---|---|
| khoá `REPORTS` | **49** | `len(open_items_audit.REPORTS)` |
| dải khoá | `127…175` | assert không lỗ |
| số khoá được điền từ tên file | **27** | 43 tài liệu − 16 số đã pinned |
| sha artifact 170 | **không đổi** | `3b782ffa…` trước và sau |
| `blind_spot.named_by_the_audit` | **43/43** | artifact 173 sinh lại |
| `blind_spot.reports_the_audit_cannot_name` | **`[]`** | nt |
| `unread_targets` | **`[]`** | nt |

Hai số 173 từng ghi sai giờ **có nguồn duy nhất** là bảng: `REPORTS[150] = 'cell_identity'`, `REPORTS[149] = 'pvp_hunter_arrays'` — và cả hai **đến từ tên file**, không phải từ trí nhớ của ai.

---

## 4. Cổng và test đổi theo

| chỗ | thay đổi |
|---|---|
| `audit_drift` check `the-blind-spot-starts-after-146` (đòi `missing` khác rỗng) | → **`the-audit-names-every-report-that-produced-an-artifact`** (`missing == []`) |
| `tests/test_audit_drift.py` pin | 7815 B / `2e32096e…` → **7725 B / `e2a5d1e7…`** |
| `test_the_audit_alone_still_names_only_twenty_two` | → `test_the_audit_alone_now_names_all_of_them` (**43**) |
| `test_the_audit_still_cannot_name_147_to_167_plus_170_to_172` | → `test_nothing_is_left_unnamed` (`[]`) |
| `test_the_audit_alone_cannot_name_cell_identity` | → `test_the_audit_names_cell_identity_now_that_the_docs_fill_its_table` (150/149/168) |
| `tests/test_open_items_audit.py` | +5 test: không lỗ · mọi tài liệu đều có tên · pinned thắng bí danh · 149/150 đúng · **điền bảng không xê dịch artifact** |

Test cuối là test quan trọng nhất của report này: nó **khoá** kết luận "bảng là chỉ mục" vào đúng sha `3b782ffa…`, nên nếu ai sau này nhét `REPORTS` vào payload (làm nó thành dữ liệu), test gãy ngay chứ không âm thầm tạo lại chu trình 168↔170.

---

## 5. Còn lại

* **Digest của 168/169 không được pin trong 170** — proofs đọc giá trị, nhưng `provenance` cố ý không băm hai artifact đó (168 đã băm 170; băm ngược lại là chu trình). Vẫn giữ nguyên lựa chọn này của 170; 175 không mở lại.
* Hợp đồng 37 mục **không đổi**: AI-4 còn tĩnh **7** (12/27/32/49/50/54/56); **5** `POLICY` cần probe native (lệnh 26/10 cấm); **6** `DATA` + **19** `RUNTIME` thuộc chủ dự án.

---

## 6. Tái lập

```bash
python3 tools/verify/open_items_audit.py      # 10748 B, sha 3b782ffa… — y nguyên
python3 tools/verify/audit_drift.py           # 19/19 check, blind_spot.missing = []
python3 -c "import sys; sys.path.insert(0,'tools/verify'); import open_items_audit as A; \
print(len(A.REPORTS), A.REPORTS[149], A.REPORTS[150])"   # 48 pvp_hunter_arrays cell_identity
```
