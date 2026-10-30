# DREADNOUGHT — bảng chất lượng / CHƯA XONG

Chuẩn: Book §3.2A và §3.5, roadmap Mốc A tại director `5701bed`. Bản tối thiểu cũ ở `fd4f65a` không đạt yêu cầu nâng cấp. Canvas và vị trí trong `dreadnought-manifest.json` mới là **vùng thiết kế**, không phải pivot hoặc muzzle đã đo. Không tuyên bố `DREADNOUGHT — CHỜ USER DUYỆT`.

## [ART]

| Món | ĐẠT/CHƯA | Lỗi/thiếu cụ thể | Số sinh lại |
|---|---|---|---:|
| Silhouette dreadnought / thân | CHƯA | Chưa có thân mới chứa 11 điểm; không dùng thân cũ dán nòng thay thế. Lần thử sinh master bị dịch vụ từ chối 403, không có ảnh | 0 thành công / 1 yêu cầu lỗi |
| 11 điểm hỏa lực | CHƯA | Chỉ có ứng viên 2 đế/đầu BigGun và Main cũ, chưa kiểm fit; thiếu 4 ụ phụ, 2 pod 8 ống, 2 pháo quạt, iris; xem bảng riêng | 0 thành công |
| Pivot / GIF lắp trên thân | CHƯA | Chưa có bố trí mới, chưa đo 6 pivot và mọi muzzle, chưa có GIF xoay trên thân Dreadnought | — |
| 3 biến thể hư hại + đế cháy | CHƯA | 3 thân cũ không có cấu tạo mới / các đế cháy; chưa có hư hại vừa 2–3 điểm và nặng nứt lõi–cánh/khói | 0 thành công |
| Trạng thái bộ phận đã phá | CHƯA | Chưa có đầu BigGun biến mất/đế cháy trái/phải và pod cháy trái/phải | 0 thành công |
| Bảy tiết mục | CHƯA | Cả 7 mới có kịch bản trong `BOSS_CINEMATIC.md`, chưa có hình/chuyển động minh họa | — |
| GIF toàn trận ≥40s + sheet | CHƯA | Chưa render; clip 32s cũ thiếu 11 điểm và 7 tiết mục, không phải bản nâng cấp | — |
| SPEC và kịch bản | CHƯA | Đã cập nhật số/cấu tạo/7 tiết mục từ 5701bed; tọa độ thực, asset, manifest thành phẩm, thời lượng và kiểm tổng thể còn thiếu | — |
| Bộ đạn tái dùng | CHƯA | Có candidate B2/B3 từ hồ sơ cũ; chưa tích hợp 11 điểm hoặc kiểm lại khi bắn lưới chéo/quạt | 0 lượt mới |

## [ART] Kiểm kê riêng: 11 điểm hỏa lực

“Thiếu” = chưa có thành phẩm được lắp/đánh giá trên thân DREADNOUGHT. Vị trí tham chiếu là vùng thiết kế theo §3.2A, không phải muzzle.

| # | Điểm | Đủ/thiếu | Lỗi cụ thể |
|---:|---|---|---|
| 1 | BigGun trái | THIẾU | Có đế/đầu cũ riêng làm candidate, chưa lắp/đo/kiểm ±65° trên thân mới; thiếu đế cháy |
| 2 | BigGun phải | THIẾU | Có đế/đầu cũ riêng làm candidate, chưa lắp/đo/kiểm ±65° trên thân mới; thiếu đế cháy |
| 3 | Main Cannon / tia | THIẾU | Có pháo cũ candidate, chưa kiểm tỷ lệ/điểm gắn mới; cố định |
| 4 | ụ vai trái | THIẾU | Chưa có đế và đầu riêng, ±45° |
| 5 | ụ vai phải | THIẾU | Chưa có đế và đầu riêng, ±45° |
| 6 | ụ hông trái | THIẾU | Chưa có đế và đầu riêng, ±35° |
| 7 | ụ hông phải | THIẾU | Chưa có đế và đầu riêng, ±35° |
| 8 | pod trái | THIẾU | Chưa có pod cố định 8 ống và trạng thái cháy |
| 9 | pod phải | THIẾU | Chưa có pod cố định 8 ống và trạng thái cháy |
| 10 | quạt lõi trái | THIẾU | Chưa có pháo cố định hướng xuống-trái |
| 11 | quạt lõi phải | THIẾU | Chưa có pháo cố định hướng xuống-phải |

Ngoài 11 điểm còn thiếu vòng giáp lõi mở/đóng, 3 thân đúng cấu tạo và các lớp khói/lửa. Thử sinh 6 asset: **0 ảnh thành công**, cả 6 yêu cầu trả 403 từ dịch vụ tạo ảnh; không bỏ/giảm yêu cầu vì lỗi này.

## [ENGINE] CHUYỂN CODER QA — không chặn ART

| Món | Trạng thái |
|---|---|
| HP thân/bộ phận, nhân damage lõi, hệ quả phá ụ và Overdrive | CHUYỂN CODER QA |
| Điều kiện vị trí tàu, dự đoán 0,35s, máy trạng thái, bảy tiết mục | CHUYỂN CODER QA |
| Muzzle, collider đạn 0,15 unit/tia 0,3 unit, khe né runtime | CHUYỂN CODER QA |
| Vòng giáp/lõi, pulse, khóa tên lửa, dọn đạn và accessibility | CHUYỂN CODER QA |

Hồ sơ tài liệu `BOSS_SPEC.md` / `BOSS_CINEMATIC.md` chỉ là chuẩn sản xuất; `dreadnought-manifest.json` là inventory thiết kế chưa có tọa độ thực. Không coi các asset cũ đã chép về là hoàn thành DREADNOUGHT.
