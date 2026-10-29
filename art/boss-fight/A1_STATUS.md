# ĐÃ GIAO LÔ A1 — 0/10 ảnh đạt chuẩn được xác nhận

**8/10 lượt sinh đã dùng; 2 lượt không dùng.** Trong tám ảnh nguồn: **6/8 ứng viên nhìn riêng có vẻ đúng loại**, chưa thể coi là đạt chuẩn director; **2/8 lỗi**, giữ nguyên để truy vết. Không generate bù hai ảnh lỗi trong lượt này. [Danh sách và SHA](A1-manifest.json); [kiểm kê trước sinh](A1_INVENTORY.md).

| # | Ảnh nguồn | Kiểm tra sơ bộ | Trạng thái |
|---|---|---|---|
| 01 | damage level 2 | Vẽ cả thân boss và mảnh thay vì lớp overlay rời | **LỖI** |
| 02 | damage level 3 | Vẽ cả thân boss và mảnh thay vì lớp overlay rời | **LỖI** |
| 03 | armor fragment | Một mảnh giáp xanh thép bị vỡ | Ứng viên, chưa duyệt |
| 04 | explosion flash | Chớp sáng riêng | Ứng viên, chưa duyệt |
| 05 | explosion fire | Quả nổ lửa riêng | Ứng viên, chưa duyệt |
| 06 | explosion smoke | Khói tàn riêng | Ứng viên, chưa duyệt |
| 07 | smoke texture | Khối khói nguồn riêng | Ứng viên, chưa duyệt; chưa kiểm texture lặp |
| 08 | sparks texture | Trường tia lửa riêng | Ứng viên, chưa duyệt; chưa kiểm texture lặp |

**Còn thiếu:** overlay hư hại bậc 2 và bậc 3 dùng được; kiểm và chốt tính liên tục bộ ba frame; alpha, kích thước, halo, ghép lớp và điều kiện director. Hai chỗ quota chưa dùng không phải ảnh đã sinh. Ảnh master đều là ảnh nguồn nền đen, không khẳng định đã có alpha hoặc đạt tiêu chuẩn xuất game.

Không tìm thấy `GAME_DIRECTOR_VISION/docs/design` tập 04 §4.3 và tập 06 Mốc A trong checkout/những nhánh đã kiểm: chưa thể kiểm đúng năm tiêu chuẩn chính thức và không thể công bố ảnh đạt chuẩn tổng thể. Kiểm kê tạm dựa trên năm yếu tố cinematic user từng nêu, có ghi rõ trong bảng. Cần user cung cấp đường dẫn/ref tới tài liệu hoặc cho biết nhánh chứa nó.

Chưa đo pivot, chưa render GIF xoay pháo hay GIF cinematic mới, chưa xuất frame-sheet; chờ lệnh cho Lô A2. Không đụng `docs/spec/`, `datas/`, `tools/`, `tests/`.
