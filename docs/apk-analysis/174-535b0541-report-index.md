# 174 — Chỉ mục report lấy từ tên file: vá lỗ mù 21 artifact + erratum 149/150 của 173

**Trạng thái:** `DECODED_STATIC` (không đọc byte mới; chỉ sửa **cách tra số report**)
**Lớp bằng chứng:** STATIC-ONLY. Không có artifact mới — artifact của 174 **là** `datas/l2_535b0541_audit_drift.json.gz` do 173 sinh lại, nên mọi số dưới đây truy được về `blind_spot` trong file đó.
**Artifact (sinh lại):** `datas/l2_535b0541_audit_drift.json.gz` — **7815 B**, sha256 `2e32096e42c4983e32c294ef3f56e8d8171fca6436fd5c3acb2bd98d1c6ecbef`
**Verifier:** `tools/verify/audit_drift.py` (**19 check**) · **Test:** `tests/test_audit_drift.py` (**42 test**)
**Sửa:** 173 (cách tra report + số `unread_targets`) · **Nối tiếp:** 173 §4.1

---

## 0. TL;DR

| | trước 174 (173 gốc) | sau 174 |
|---|---|---|
| nguồn ánh xạ report → topic | chỉ `AUDIT.REPORTS` (22 khoá) | hợp của `AUDIT.REPORTS` **∪** tên file `docs/apk-analysis/<n>-535b0541-<topic>.md` (**42** số, 133…174) |
| artifact đặt tên được report | **22/43** | **43/43** |
| `unread_targets` (sửa mức-report nhắm report không tên được) | `[149]` | `[]` |
| `cell_identity` là report số | ~~149~~ (**sai**) | **150** |
| report **149** | ~~`cell_identity`~~ (**sai**) | **`pvp_hunter_arrays`** |

Không có số đo nào của 173 bị đảo: 9 claim, 20 luật, 37 dòng hợp đồng, 0 luật hỏng — tất cả giữ nguyên. Chỉ **cái tên** của hai report bị sửa, và lỗ mù 21 artifact được đóng.

---

## 1. Vấn đề: bảng viết tay không thể là nguồn sự thật

`AUDIT.REPORTS` dừng ở `146`, nhảy `168`, `169`. Mọi report sau 146 — trừ hai cái được thêm tay — đều **không có tên** trong bảng đó. Nhưng tên của chúng đã tồn tại, ở chỗ khác: **tên file báo cáo**.

```
docs/apk-analysis/150-535b0541-cell_identity.md     → 150 = cell_identity
docs/apk-analysis/149-535b0541-pvp_hunter_arrays.md → 149 = pvp_hunter_arrays
```

42 file như vậy, phủ `133…174`. Nghĩa là: cái "lỗ mù" không phải thiếu dữ liệu, mà là **tra sai chỗ**.

## 2. Sửa: hợp hai nguồn, không ghi thêm số tay

```python
def doc_index():                       # docs/apk-analysis/<n>-535b0541-<topic>.md
    ...

@functools.lru_cache(maxsize=None)
def known_reports():
    table = dict(AUDIT.REPORTS)        # 127…146, 168, 169 — cái audit tự khai
    for number, topic in doc_index().items():
        table.setdefault(number, topic)
    return table

def report_of(stem):                   # dùng known_reports(), không dùng thẳng AUDIT.REPORTS
    ...
```

`setdefault` chứ không `update`: nếu audit **và** tên file cùng đặt tên một số mà lệch nhau, tên trong audit thắng — nhưng check `the-docs-do-not-contradict-the-audit-on-a-shared-number` bắt trường hợp lệch đó **nếu** cái tên trong file lại đúng là một artifact có thật (tức lệch thật, không phải bí danh).

Ba nguồn thông tin, ba vai:

| nguồn | nói gì | ai giữ |
|---|---|---|
| `lane_closeout` | 20 artifact của tập đóng 127…146 | 147 |
| `AUDIT.REPORTS` | audit **tự** khai nó đọc report nào | 170 |
| tên file `docs/apk-analysis/…` | report **nào tồn tại**, số nào, chủ đề gì | mỗi report tự sinh |

## 3. Kết quả đo trên 43 artifact

| | số |
|---|---|
| artifact cổng đọc | **43** |
| đặt tên được bằng **tên file** (∪ audit) | **43** — **0** không tên |
| đặt tên được bằng **chỉ** `AUDIT.REPORTS` | **22** |
| `AUDIT.REPORTS` vẫn thiếu (cửa sổ report **có artifact**, 127–172) | **24** report lúc 174 — **175 điền nốt, còn 0** |
| số trong `doc_index()` | **42** |
| `unread_targets` sau khi có chỉ mục | **`[]`** |

Con số 24 là **cố ý giữ**: 174 không sửa `open_items_audit` (làm vậy sẽ đổi hash của 170 ngay trong artifact đang băm nó — đúng cái bẫy chu trình đã gặp giữa 168 và audit). Cái được sửa là **cổng**: nó không còn tin bảng viết tay là nguồn duy nhất.

## 4. Erratum: 149 ≠ `cell_identity`

173 viết "`cell_identity` (149)" hai lần. Sai số:

| 173 nói | thực tế | nguồn |
|---|---|---|
| "`cell_identity` (149)" | `cell_identity` = **150** | `docs/apk-analysis/150-535b0541-cell_identity.md` |
| (không nói) | **149** = `pvp_hunter_arrays` | `docs/apk-analysis/149-535b0541-pvp_hunter_arrays.md` |

**Không đổi kết luận** — cả 149 lẫn 150 đều không nằm trong `AUDIT.REPORTS`, nên R5 vẫn đúng khi báo "target không tên được". Nhưng nó đổi **ý nghĩa** của dòng sửa, và cái này mới là chỗ đáng sửa:

`cell_identity` có hai dòng `corrections`:

| # | `statement` bị sửa | `target` |
|---|---|---|
| 1 | "`get_pathRoot` trả slot 0x2AEC9A0 khi companyName == "Test" và 0x2AEC9B0 khi PREMIUM" | **138** (`remote_configs`) |
| 2 | "chỉ biết offset +0x10 / +0x14 / +0x18" | **149** (`pvp_hunter_arrays`) |

Dòng 2 **không** phải `cell_identity` tự sửa mình — nó sửa câu mà report **149** đã viết về cell `0x2ADF238`, và đưa ra kết luận: cell đó **là `Board_PVP`**, ba offset `+0x10/+0x14/+0x18` là `betCoinValues`/`betGemValues`/`betMedalValues`. Đọc đúng số report làm câu sửa có nghĩa; đọc sai thì nó thành "tự sửa mình", nghe như lỗi.

Vì thế erratum này **không phải việc đánh vần**: nó là bằng chứng rằng tra sai bảng thì *ngữ nghĩa* cũng sai theo, không chỉ con số.

## 5. Test đã đổi theo

| test | nội dung mới |
|---|---|
| `test_report_of_reads_the_docs_and_the_audit_together` | `lane_residue`→168 · `cell_identity`→**150** · `pvp_hunter_arrays`→**149** · topic lạ→`None` |
| `test_the_audit_alone_cannot_name_cell_identity` | `audit_report_of('…cell_identity')` = `None` (đây là lỗ mù), `lane_residue` = 168 |
| `test_every_artifact_is_named_by_the_docs` | `unnamed == []`, `named_by_the_docs == 43` |
| `test_the_audit_alone_still_names_only_twenty_two` | giữ đúng sự thật về bảng viết tay |
| `test_the_audit_still_cannot_name_147_to_167_plus_170_to_173` | **25** số, không giảm |
| `test_no_correction_now_points_at_an_unnamed_report` | `unread_targets == []` |
| `test_a_missing_doc_is_now_the_tripwire` | tập số chỉ-tên-file-có = `133…173` ∖ `REPORTS` |

Điểm cuối là **đảo chiều bẫy**: trước 174, quên thêm dòng vào `REPORTS` là im lặng; sau 174, **thiếu file report** mới là thứ làm R1 nổ.

## 6. Còn lại

* ~~`AUDIT.REPORTS` thiếu 24 số~~ — **175 đã điền**: hoá ra `REPORTS` là chỉ mục thuần (không item/proof/digest), nên điền thêm 26 khoá **không đổi một byte** artifact của 170 (`3b782ffa…` y nguyên) ⇒ không có chu trình, không phải sinh lại 168/170/172/173.
* Bí danh `134`/`136` (`pvp_manager_rules` vs `pvp_manager_rules_tables`, `pvp_rank_api` vs `rank_api`): tên file dài hơn tên artifact. Chấp nhận được vì artifact vẫn có tên qua audit; nếu sau này đổi thì phải đổi **cả** tên file, không chỉ một bên.

---

## 7. Tái lập

```bash
python3 tools/verify/audit_drift.py            # 19/19 check, unread_targets = []
python3 -m unittest tests.test_audit_drift -q  # 42 test
python3 -c "import sys; sys.path.insert(0,'tools/verify'); import audit_drift as A; \
print(A.doc_index()[149], A.doc_index()[150], len(A.doc_index()))"   # pvp_hunter_arrays cell_identity 42
```
