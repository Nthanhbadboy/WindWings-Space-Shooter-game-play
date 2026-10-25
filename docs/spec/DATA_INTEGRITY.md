# DATA_INTEGRITY — dữ liệu gốc có bị sửa không?

**Trả lời ngắn: hai phiên làm việc vừa rồi (phân loại sprite + tách sheet)** không sửa file gốc nào.
Nhưng khi kiểm kỹ thì lộ ra **hai vấn đề về dấu vết dữ liệu** — không phải do sửa tay, mà do *kéo nhiều
đợt từ nhiều snapshot khác nhau*. Tài liệu này ghi cả hai, kèm cách kiểm lại bằng máy.

Máy kiểm: `python3 tools/data-integrity.py` (1,7 s) → `docs/assets/data-integrity.json`.
Mã thoát **1** nếu có file **đang sửa trong working tree** khác HEAD, hoặc khác đầu nhánh dữ liệu mà
không khớp snapshot nào (dấu hiệu sửa tay). Bản kéo cũ khớp HEAD **không** làm đỏ.

---

## 1. "Dữ liệu gốc" ở đây là gì

| đường dẫn | nội dung | ghi chú |
|---|---|---|
| `datas/` | data pack bóc từ APK (waves, HP, ships, items…) | nguồn của phần lớn con số trong `docs/spec/` |
| `reverse-engineering/` | typetree, scriptableobjects, asm, dump IL2CPP | nguồn của A5/A6/B3 |
| `docs/apk-analysis/` | báo cáo + manifest 2.907 asset | nguồn kích thước sprite |
| `raw/` | dump UI/anim/runtime | |
| `docs/assets/contact-sheets/` | 42 ảnh JPEG — **ảnh gốc duy nhất trong repo** | chỉ đọc, không ghi |

---

## 2. Kiểm 1 — hai commit của phiên này có chạm vào đó không?

```
git diff --name-only 677c24feb..HEAD -- datas docs/apk-analysis reverse-engineering raw docs/assets/contact-sheets
(rong)
```

14 file thay đổi trong 2 commit, **không file nào** nằm trong 5 đường dẫn trên:

| nhóm | file |
|---|---|
| dữ liệu **phái sinh** (do tool sinh) | `art-study.csv` · `sprites-auto-classified.csv` · `sheet-splits.csv` · `sprites-knn.csv` · `sprites-atlas-page.csv` · `classify-knn.json` · `sheet-splits-sample.png` |
| tool | `art-study.py` · `classify-by-measure.py` · `classify-knn.py` · `verify-claims.py` |
| tài liệu | `ASSET_TRIAGE.md` · `README.md` · `COVERAGE_AUDIT.md` · `ANIMATION_SCRIPT.md` |

`docs/assets/art-study.csv` **có** bị ghi đè, nhưng nó là **đầu ra của tool**, không phải dữ liệu gốc.
Kiểm từng ô: **0 ô lệch** trong **16 cột cũ**, chỉ **thêm 2 cột** (`ncomp`, `comps`); 2.112 dòng, thứ tự dòng
không đổi.

Các tool mới chỉ mở file để **đọc**; đường ghi duy nhất là `docs/assets/*.csv|json|png` và thư mục `--crop`
truyền vào (mặc định ngoài repo).

---

## 3. Kiểm 2 — bảng `sha256` trong `datas/PROVENANCE.md`

Bảng này ghi sha256 của từng file **lúc kéo 019e704d1 (23/10)** — tức bản chụp để phát hiện sửa tay.

**PROVENANCE: 244/383 khớp · 139 lệch · 0 thiếu**

139 file lệch **không** phải sửa tay: chúng được **kéo lại** ở các commit sync sau (`bc0e11bf2`,
`6ae2f5753`, `71b1e9861`), nên bảng ghi từ 23/10 đã **cũ**. Ví dụ `datas/enemy_hp.json`: bảng ghi
`6727a1a1…`, file hiện tại `9a8cd7f4…`.

⇒ **Kết luận 1: bảng PROVENANCE hết tác dụng làm dấu vết** — nó chỉ đúng với bản kéo đầu tiên. Muốn dùng
lại thì phải ghi **sha256 hiện tại kèm commit** (việc này chưa làm, xem §6).

---

## 4. Kiểm 3 — so từng blob với **đầu nhánh dữ liệu**

`ref = origin/arena/ef6b75ef-windwings-space-shooter-game-p @ 7e0da2ee3b07` (25/10, đo lại
lần cuối sau khi kéo bằng chứng review).

| | số file |
|---|---:|
| có ở cả hai nhánh | **2.465** |
| **giống hệt blob** | **2.211** |
| **khác** | **254** |
| chỉ có ở nhánh dữ liệu | 55.672 (chủ yếu `raw/ui` + ảnh chụp) |
| chỉ có ở đây | 85 (`datas/PROVENANCE.md`, ảnh chụp ramus, CSV do phân tích) |

254 file khác — **244** khớp **nguyên blob** với một snapshot **cũ** đã pin; **10** khớp đúng HEAD
của mình nhưng cũ hơn danh sách snapshot (kéo ở commit không nằm trong danh sách):

| khớp snapshot | số file |
|---|---:|
| `9aed767b1` (25/10) | 141 |
| `55bd18ac8` (25/10) | 30 |
| `019e704d1` / `6dc5c4bf5` (23/10) | 66 |
| khớp nhiều snapshot | 7 |
| khớp **HEAD** nhưng cũ hơn snapshot (không sửa tay) | **10** |
| **đang sửa trong working tree** | **0** |

⇒ **Kết luận 2: không có sửa tay.** Nhưng bản local là **hỗn hợp 3 snapshot**, không phải một bản chụp
nguyên khối — vì mỗi lần sync chỉ kéo một danh sách file, không kéo cả cây.

Bằng chứng phụ: `git log -1 -- <file>` của cả 254 file đều là commit **sync**, không có commit nào là
"sửa tay".

---

## 5. Kiểm 4 — đổi `.gz` byte ≠ đổi dữ liệu

157 file `.gz` nằm trong nhóm 254 (gzip ghi `mtime` vào header nên kéo lại là đổi byte):

| | số file |
|---|---:|
| giải nén ra **giống hệt** | **88** |
| giải nén ra **khác thật** | **69** |

⇒ Nói "nhánh dữ liệu có 254 file mới" là **sai**: chỉ **69** file `.gz` + phần `.csv/.json/.md` là đổi
**nội dung**; 88 file chỉ đổi header.

---

## 6. Vì sao **không** tự động kéo đè 254 file

| lý do | bằng chứng |
|---|---|
| nội dung đổi thật, nên **số phái sinh phải đo lại** | 66/148 `.gz` khác sau giải nén; 95 `.csv` khác |
| **nhóm HP theo root không ổn định giữa snapshot** | `datas/boss_hp.json`: 254 instance (23/10) → 256 (25/10 `9aed767b1`) → 244 (đầu nhánh 25/10). Cùng nguyên nhân: root path lúc có tiền tố `Board_FightBoss/Parent/…`, lúc không |
| hai nhánh đang **cùng sửa** các file này | nếu kéo đè, mọi claim của `verify-claims.py` phải đo lại **trong cùng một commit** — nếu không sẽ lặp lại lỗi "local-first đọc ref đóng băng" đã sửa ở `bc0e11bf2` |

Việc đúng, nếu muốn bám đầu nhánh dữ liệu: kéo **theo lô**, mỗi lô ghi **ref + sha256**, chạy lại
`verify-claims.py --ref <ref> --strict-ref`, sửa số trong tài liệu **cùng commit** với lô đó.
Đây là quy trình `DATA_SYNC.md` đã đặt ra; tài liệu này chỉ thêm bước **ghi sha256 mới** vào PROVENANCE.

---

## 7. Tự kiểm

| mã | nội dung | đo bằng |
|---|---|---|
| **AP1** | **PROVENANCE: 244/383 khớp · 139 lệch · 0 thiếu** | đọc bảng sha256 trong `datas/PROVENANCE.md`, băm lại 383 file |
| — | 254 file khác đầu nhánh dữ liệu, **0** đang sửa trong working tree | `tools/data-integrity.py` (cần `git fetch` nhánh dữ liệu) |
| — | 157 `.gz` đổi byte → 88 giống nội dung, 69 khác | cùng tool, mục 3 |
