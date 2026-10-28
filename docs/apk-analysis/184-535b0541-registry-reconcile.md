# 184 — Đối soát registry: hai mục 50/52 đã trả lời được, một mục 51 thì không

**Trạng thái:** `RECONCILED_STATIC` (chỉ đọc APK gốc; không chạy game, không probe)
**Lớp bằng chứng:** STATIC-ONLY. Phần "bản nào đang chạy / có đăng nhập hay không" vẫn `MODEL_NOT_MEASURED runtime`.
**Artifact:** `datas/l2_535b0541_registry_reconcile.json.gz` (2432 B, sha256 `b57602199ec2bd7e3d7530197fd087ecffbbe085138c160deef2eb387afc0ffa`)
**Verifier:** `tools/verify/registry_reconcile.py` · **Test:** `tests/test_registry_reconcile.py` (33 test)
**Báo cáo trước:** 180 (registry-v4, ledger đang pin), 181 (cell `0x2ADB958`), 182 (giải ô string), 183 (base của path literal).
**Vì sao có báo cáo này:** reviewer `8141386a` (`6445017285`) chỉ ra đúng một chỗ lệch — ledger v4 pin ở cut của 180, còn 181/182 đã sinh bằng chứng mới cho **hai** dòng trong đó. Báo cáo này **không viết lại v4**; nó gắn một *amendment* cho từng dòng, kèm phần còn lại.

---

## 0. TL;DR

| Câu hỏi | Trả lời đo được | Bằng chứng |
|---|---|---|
| Phải đối soát những dòng nào? | **3** dòng có nhắc slot tuyệt đối (50, 51, 52), **4** slot | §1 (quét theo text, không chọn tay) |
| Mục **50** — `ArenaManager` root variants? | **giải được**: 3 ô `45009312 / 45009320 / 45009328` ⇒ `arena-test-datas` / `arena---datas` / `arena--datas` | §2 |
| Vì sao v4 nói "chưa dereference"? | v4 pin ở cut 180; đường `relocations → ScriptString` của 182 chưa có lúc đó | §2 |
| Mục **52** — class sở hữu static field 0? | **`FirebaseDatabaseManager`**, static field 0 = `Instance` (`// 0x0`) | §3 |
| Bao nhiêu điểm đọc statics? | **56/141** site, **tất cả** ở offset `0x0` của block `klass+0xB8` | §3 |
| Mục **51** — `PVP_Manager` config class? | **vẫn mở**: ô `0x2AE1000` không có entry relocation **và** không có site nào nạp nó | §4 |
| Mục audit 53? | **vẫn `RUNTIME`** — báo cáo này không đo payload nào | §5 |
| v4 có bị sửa không? | **không**: 4851 B / `bcd0e0fd…` đúng bằng cut của 180 | §1 |

**Một câu:** hai trong ba dòng của ledger có thể đóng bằng bằng chứng static đã pin (50 ⇒ ba chuỗi root; 52 ⇒ `FirebaseDatabaseManager.Instance`), còn dòng 51 thì phép join mà v4 đề xuất **không có đầu vào** trong corpus hiện tại — nên nó ở lại `policy` cho owner, và đây là lần đầu lý do đó được đo chứ không chỉ suy ra.

---

## 1. Phạm vi được **suy ra**, không được chọn tay

Tool quét text của cả **32** dòng ledger, tìm mọi VA tuyệt đối (`>= 0x1000000`; dưới ngưỡng đó là offset, vd `// 0x0`, `klass+0xB8`):

| Dòng | Label ở cut 180 | Slot trong text |
|---|---|---|
| 50 | `missing-input` | `0x2AEC9A0` (45009312), `0x2AEC9B0` (45009328) |
| 51 | `policy` | `0x2AE1000` (44961792) |
| 52 | `policy` | `0x2ADB958` (44939608) |

⇒ `rows_with_slots 3 · slots 4 · resolved 3 · unresolved 1`; **29** dòng còn lại không nhắc slot nào nên không bị đụng tới.

**v4 giữ nguyên byte:** `datas/l2_535b0541_registry_v4.json.gz` vẫn 4851 B / `bcd0e0fd95af375b8841021856209eb701d284bf013966d48f868e9143e21a96`, đúng cut của 180 (`cf17c7f`). Amendment sống **trong artifact của 184**, không sửa file cũ — để người review đọc được cả *trước* và *sau* trong một chỗ.

---

## 2. Mục 50 — ba ô của `ArenaManager.get_pathRoot`, và một lỗi thời về từ ngữ

Chuỗi đo được (hai bảng đã pin, không cần `.so`):

```
slot 45009312 --relocations--> 46051744 --ScriptString--> "arena-test-datas"
slot 45009320 --relocations--> 46051720 --ScriptString--> "arena---datas"
slot 45009328 --relocations--> 46051728 --ScriptString--> "arena--datas"
```

Điểm nạp (`adrp` → `ldr`, cách nhau đúng 4 byte) đều nằm trong **`ArenaManager.get_pathRoot` (22685676)**, method 204 byte:

| Slot | `adrp` | `ldr` | Chuỗi |
|---|---|---|---|
| 45009312 | 22685716 | 22685720 | `arena-test-datas` |
| 45009320 | 22685728 | 22685732 | `arena---datas` |
| 45009328 | 22685740 | 22685744 | `arena--datas` |

Ba RVA `adrp` này **trùng khớp** với `load_rva` mà 182 đã ghi (test `test_load_sites_agree_with_182` so trực tiếp với artifact 182) — tức đây là phép đo lại độc lập, không phải chép lại.

**Amendment #50**

| | Trước (cut 180) | Sau (184) |
|---|---|---|
| Label | `missing-input` | `shipped-default` (phần chuỗi) |
| Verdict | `OPEN` | `STATIC_CONFIRMED` |
| Lý do chặn | "slots `0x2AEC9A0/0x2AEC9B0` are never dereferenced in the pinned raws" | lỗi thời: cả hai (và ô thứ ba `0x2AEC9A8` mà 138 không nhắc) đều dereference được |
| Còn lại | — | **`runtime-gated→USER`**: bản nào đang chạy phụ thuộc `Application.get_companyName()` (41274380) và `VersionControlSystem.get_PREMIUM()` (20068044) — `MODEL_NOT_MEASURED runtime` |

Nói cho rõ: đóng phần **chuỗi** không đóng phần **lựa chọn**. Reviewer dặn không tự đóng #50 — báo cáo này cũng không đóng nó, chỉ tách nó thành hai nửa và ghi nửa nào đo được.

---

## 3. Mục 52 — class của ô `0x2ADB958` giờ có tên từ **ba** hướng

| Hướng | Kết quả |
|---|---|
| `relocations[44939608]` → `ScriptMetadata` | **`FirebaseDatabaseManager_TypeInfo`** (182 đã chạm, 184 đo lại) |
| `dump.cs` | `public class FirebaseDatabaseManager : MonoBehaviour // TypeDefIndex: 1485` · `public static FirebaseDatabaseManager Instance; // 0x0` |
| Census của 184 (141 site, 34 method, 3 raw) | **56** site đi qua block statics `klass+0xB8`, và **tất cả 56** đọc **offset `0x0`** — không có static nào khác bị chạm |

Phân bố idiom trên 141 site — mỗi site rơi vào **đúng một** ô (54 + 56 + 31 = 141):

| Tag | Số site |
|---|---|
| `class_init(0x110D028)` — chỉ thấy gọi helper khởi tạo, không đọc statics trong cửa sổ 8 lệnh | 54 |
| `statics(klass+0xB8)` — đọc block statics, và **chỉ** offset `0x0` | 56 |
| `unclassified` — không thấy init/flag/statics trong cửa sổ 8 lệnh | 31 |

**Amendment #52**

| | Trước (cut 180) | Sau (184) |
|---|---|---|
| Label | `policy` | `shipped-default` |
| Verdict | `OPEN` | `STATIC_CONFIRMED` |
| Lý do chặn | "the class behind slot `0x2ADB958` is unnamed" | đã có tên, ba hướng độc lập ở trên |
| Còn lại | — | **`runtime-gated→USER`**: `Instance` có non-null và đã đăng nhập lúc fetch hay không là trạng thái máy |

---

## 4. Mục 51 — phép join của v4 **không có đầu vào**, và đó là kết quả đo

v4 đề nghị: *"`JsonParse.FromJson<object>` lấy type từ metadata slot `0x2AE1000` — thử phép join kiểu `InitializeArray` đã sửa 30/39/40"*. Đo trên corpus đang pin:

| Phép kiểm | Kết quả |
|---|---|
| `relocations[44961792]` | **không có entry** (bảng có 288733 dòng) |
| `adrp 0x2AE0000` + `ldr xN,[xN,#0x1000]` trong **mọi** raw đã pin | **0** site |
| `ScriptMetadata` / `ScriptString` tại target | không áp dụng được (không có target) |

⇒ Slot đó không phải một ô pointer đã relocate trong corpus này. Nhãn **ở lại `policy`**, verdict **`OPEN`**, và bước kế tiếp đổi từ "thử join" thành câu hỏi cho owner: hoặc cần một raw phủ vùng đó, hoặc cần bảng metadata-usage — chứ không phải "đào thêm một vòng nữa".

Ghi chú kỷ luật: **"không thấy" ≠ "không tồn tại"**. Câu đúng là *"slot 0x2AE1000 không xuất hiện như một cell trong 3 raw đang pin và không có relocation entry"*; nó không nói gì về việc binary có dùng ô đó hay không.

---

## 5. Những gì báo cáo này **không** làm

- **Không** nâng mục audit **53** khỏi `RUNTIME`: artifact ghi `audit_53 = "RUNTIME"`, và 184 không đọc payload nào từ server.
- **Không** đổi số của v4 tại cut cũ: 29/32 dòng không bị đụng, 3 dòng chỉ nhận amendment.
- **Không** phê duyệt 182/183 thay reviewer: `APPROVE-BOUNDED` của `8141386a` pin tới 181, nên 184 cũng là bằng chứng **do producer** đưa ra và **cần audit độc lập** như 182.
- **Không** đụng `libunity.so` FDE (AI-1), `#27-GS` C# (AI-2), `#7/#8` geometry (AI-3), và không sửa 3 file protected.

`not_measured` (3 dòng, đều mang nhãn `MODEL_NOT_MEASURED runtime`): bản root nào đang chạy · `Instance` có đăng nhập lúc fetch hay không · mọi giá trị phục vụ và mọi con số thay vào path mà 182/183 đã in.

---

## 6. Tự kiểm (19 check, 0 fail)

`tools/verify/registry_reconcile.py` in ra `checks` ngay trong artifact; các mốc chính:

| Check | Nội dung |
|---|---|
| `ledger bytes/sha match the pinned v4` | 4851 B · `bcd0e0fd…` |
| `scan found the three rows` | đúng `[50, 51, 52]` |
| `row 50: all resolved as strings` · `every string non-empty` | 3/3 ô ⇒ 3 chuỗi khác rỗng |
| `row 50: adrp sites match the ones 182 recorded` | so trực tiếp với artifact 182 |
| `row 52: metadata name` | `FirebaseDatabaseManager_TypeInfo` |
| `row 52: census offsets are all 0x0` | `{"0": 56}` |
| `row 51: no load site` · `slot unresolved` | 0 hit · không có entry |
| `audit row 53 still RUNTIME` | không nâng |
| `ledger rows untouched` | 29 |

**Gate tại commit này:** `tests/test_registry_reconcile.py` **33 test** · discover toàn bộ **1720** OK · verify-claims **209 PASS / 0 FAIL / 2 SKIP** · audit_drift **52** artifact / contract 33 / 19/19 rule · registry-v4 vẫn **4851 B / `bcd0e0fd…` / 19/19** (chứng minh không viết lại v4) · lane_residue 32/32 · item32_closure 14/14 · lane_closeout 0 failing.

---

## 7. Bước kế tiếp (ghi lại để không mở lại lane cũ)

1. **#51**: chỉ owner quyết — cần raw phủ `0x2AE1000` hoặc bảng metadata-usage; không đào lại vùng đã đóng.
2. **#50/#52 residual**: thuộc nhóm `runtime-gated→USER`; nếu người dùng muốn đo thì phải mở lane runtime riêng (ngoài phạm vi static-only hiện hành).
3. **Ledger**: nếu director muốn v4 "hiện hành", việc phát hành v5 = áp 2 amendment này + giữ 29 dòng còn lại; báo cáo này đã đủ dữ liệu để làm, nhưng **không tự phát hành** vì v4 là hồ sơ Gate-1 đã pin.
