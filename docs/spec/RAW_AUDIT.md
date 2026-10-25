# RAW_AUDIT — claim nào **đo từ dữ liệu gốc**, claim nào chỉ là văn

> Sinh bằng `python3 tools/raw-audit.py`; luật phân loại nằm ở `classify_claims()`
> trong `tools/verify-claims.py`. **Đừng sửa tay** số trong file này.
> Mục đích: trả lời câu *"tài liệu dựa vào raw hay nói mồm?"* bằng máy, không bằng lời.

## 0. Tổng

**RAW 145 · DOC 3 · CONST 37 · tổng 185**

| loại | số claim | nghĩa |
|---|---:|---|
| **RAW** | **145** | hàm đo **mở file** trong `datas/` · `reverse-engineering/` · `docs/assets/` |
| **DOC** | **3** | chỉ đọc `docs/**` — kiểm tính nhất quán tài liệu, **không** phải dữ liệu gốc |
| **CONST** | **37** | **không mở file** — số đo một lần, không tái đo bằng máy |
| **cộng** | **185** | |

⇒ **145/185** claim tái đo được từ raw. **37** claim là hằng số (xem §2) — dùng để **tham khảo**, không dùng làm bằng chứng khi thiết kế.

## 1. Cách phân loại

Đọc **source của hàm đo** (và các hàm nó gọi, sâu 3 tầng). Nếu source có đường dẫn tới
`datas/`, `reverse-engineering/`, `docs/assets/`, hoặc gọi `ref_lines`/`ref_json`/`_csv_rows`
⇒ **RAW**. Chỉ có `docs/` ⇒ **DOC**. Không có gì ⇒ **CONST**.

> **Giới hạn:** đây là kiểm **tĩnh theo source**, không chứng minh hàm đo *dùng dữ liệu đúng cách*.
> Một claim RAW vẫn có thể diễn giải sai (đã từng: `23.757` dòng vs lượt). Nó chỉ bảo đảm **có file thật**
> đứng sau con số và chạy lại được trên máy khác.

## 2. Claim **CONST** — "đo một lần", không tái lập

| claim | tài liệu | ghi chú |
|---|---|---|
| **A1** | `SUMMARY_vi.md` | số file /statics đọc được trong thư mục phiên |
| **A2** | `SUMMARY_vi.md` | — |
| **A3** | `SUMMARY_vi.md` | — |
| **A4** | `SUMMARY_vi.md` | — |
| **A5** | `SUMMARY_vi.md` | — |
| **A6** | `SUMMARY_vi.md` | — |
| **A7** | `SUMMARY_vi.md` | — |
| **A8** | `SUMMARY_vi.md` | — |
| **A9** | `SUMMARY_vi.md` | — |
| **A10** | `CROSSCHECK-static-vs-runtime.md` | số động đo được; số tĩnh 12 nằm trong APK, không có trong ảnh chụp này |
| **B9** | `ANIMATION.md` | con số duy nhất trong ANIMATION.md không kiểm lại được offline |
| **F4** | `ANIMATION.md` | Sprite chỉ kiểm được nếu export thêm typetree Sprite |
| **D1** | `RamusBridge.cs` | route tồn tại trong bridge |
| **D2** | `collect.sh` | collect.sh gọi endpoint ở mỗi mốc dump |
| **D3** | `collect.sh` | gate đòi file chứa số đo playback |
| **D4** | `build-bridge.sh` | 5 lần biên dịch; mục thứ 6 của ma trận là self-test chạy, không compile |
| **D5** | `README.md` | — |
| **E1** | `DIFFICULTY_MODES.md` | Stage_Datas.MaxModeIndex — số chế độ |
| **E2** | `BALANCE.md` | — |
| **E3** | `BALANCE.md` | — |
| **E4** | `BALANCE.md` | — |
| **E5** | `BALANCE.md` | — |
| **E6** | `BALANCE.md` | — |
| **E7** | `BALANCE.md` | — |
| **E8** | `BALANCE.md` | — |
| **E9** | `MISSIONS_STARS.md` | — |
| **E11** | `MISSIONS_STARS.md` | danh sách enemy bị bỏ qua trong chế độ nhiệm vụ |
| **E12** | `MISSIONS_STARS.md` | — |
| **Q3** | `ASSETS.md` | 12 page chỉ chứa ~17% lượng px² của toàn bộ art |
| **R1** | `BOSS_ANIM_TIMELINE.md` | quy mô timeline: mọi số khác suy từ đây |
| **R2** | `BOSS_ANIM_TIMELINE.md` | 67% event là state, 27% là đòn — không phải 100% damage |
| **R3** | `BOSS_ANIM_TIMELINE.md` | 3 callback state = 43% event |
| **R4** | `BOSS_ANIM_TIMELINE.md` | đòn liên hoàn ~6 hit/giây |
| **R5** | `BOSS_ANIM_TIMELINE.md` | clip chờ 73 s — đừng chờ nó xong mới cho bắn |
| **R6** | `BOSS_ANIM_TIMELINE.md` | enemy gần như không có event clip; 2 event trùng mốc = double damage |
| **W4** | `ANIMATION_SCRIPT.md` | PathFollow đổi hướng bằng atan2 rồi rad→deg |
| **W5** | `ANIMATION_SCRIPT.md` | bước quét vòng tròn = 1 độ mỗi bước |

## 3. Claim **DOC** — tự nhất quán, không phải bằng chứng dữ liệu

| claim | tài liệu | ghi chú |
|---|---|---|
| **P1** | `COVERAGE_AUDIT.md` | quy mô tài liệu hiện có trong docs/spec |
| **RD1** | `README.md` | số dòng · số bảng của 39 tài liệu trong bảng README khớp file thật (bảng đếm theo dòng `|---`) |
| **RB1** | `RAW_AUDIT.md` | sổ kiểm claim↔raw: chạy lại tools/raw-audit.py và so đúng 4 số ở §0. CONST = số không mở file nào ⇒ phải đọc là 'đo một lần', không phải bằng chứng tái lập |

## 4. Luật dùng số

1. Số để **quyết định thiết kế** phải là claim **RAW** — hoặc ghi rõ "đo một lần, ngày …".
2. Số **CONST** được phép tồn tại, nhưng **không** được dùng để bác một kết luận khác.
3. Thêm claim mới: **đừng** viết `lambda: <hằng số>`; mở file raw và đo, hoặc khai báo là CONST.

```bash
python3 tools/raw-audit.py      # sinh lại file này
python3 tools/verify-claims.py  # claim RB1 khoá dòng "RAW … · tổng …" ở §0
```
