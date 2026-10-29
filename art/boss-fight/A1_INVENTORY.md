# Kiểm kê trước sinh ảnh — Lô A1

Thời điểm kiểm kê: trước khi bắt đầu generate A1; phạm vi `art/boss-fight` tại commit `52a3186`. **Chưa có asset nào được đánh dấu đạt chuẩn tổng thể**, vì pivot/alpha/VFX, hoạt cảnh và đọc hình chưa được director duyệt. Nguồn `GAME_DIRECTOR_VISION/docs/design` tập 04 §4.3 và tập 06 Mốc A không có trong checkout hiện tại hoặc nhánh chính/nhánh director được kiểm tra; chưa thể đối chiếu chính xác 5 tiêu chuẩn trong tài liệu đó. Bảng sau tạm dùng đúng năm yếu tố điện ảnh user nêu trong lệnh cinematic, KHÔNG nhận là bảng thay thế tài liệu gốc.

| Tiêu chuẩn tạm đối chiếu | Đạt | Chưa đạt/chưa xác nhận | Bằng chứng |
|---|---|---|---|
| Khởi đòn / anticipation | Có nguồn `charge`, `beam_warning` và logic sạc/lùi | Chưa kiểm thị giác, chưa QA timing/telegraph trong engine | `exports/effects/`, `build-cinematic.py` |
| Va chạm / impact | Có nguồn nổ, lóe; script có freeze 2–3 frame | Không có chuỗi **ba ảnh riêng** chớp → lửa → khói tàn được thiết kế liên tục; chưa duyệt | `exports/cinematic/`, `cinematic-manifest.json` |
| Nhịp thở | Kịch bản có khoảng nghỉ sau đòn | Chưa xem duyệt không tiếng 3 lần; chưa QA runtime | `BOSS_CINEMATIC.md`, `CINEMATIC_SPEC.md` |
| Môi trường diễn cùng | Có `beacon`, `smoke`, `debris`, `spark` | Texture khói/tia lửa chuyên dụng và mảnh giáp vỡ cần tạo/kiểm; overlay bậc hư hại 2/3 chưa có; mép `turret-destruction` đáng nghi | `exports/cinematic/`, `CINEMATIC_ASSET_STATUS.md` |
| PLAYER là nhân vật chính / suýt chết | Có PLAYER đã duyệt và quỹ đạo dàn dựng | Chưa kiểm hitbox/đường né; GIF không phải gameplay | `build-cinematic.py`, `CINEMATIC_SPEC.md` |

## Kiểm kê theo món A1

| Món | Tình trạng trước A1 | Quyết định |
|---|---|---|
| Hư hại bậc 2 | Chỉ có `exports/boss-layers/damage.png` là một overlay khói/lửa; chưa có bậc 2 riêng | Sinh riêng |
| Hư hại bậc 3 | Chưa có overlay bậc 3 riêng | Sinh riêng |
| Mảnh giáp vỡ | Có `masters/cinematic/debris.png` là một ứng viên; chưa QA kiểu giáp, màu và ghép | Sinh thêm mảnh giáp vỡ riêng cho cảnh chết |
| Chớp → lửa → khói tàn | Có các VFX đơn lẻ, không phải một chuỗi ba ảnh được thiết kế liên tục | Sinh lần lượt ba ảnh riêng, không cắt ảnh cũ bù |
| Texture khói | Có một plume `masters/cinematic/smoke.png`; không xác nhận là texture lặp | Sinh texture khói riêng |
| Texture tia lửa | Có một spark `masters/cinematic/ambient-spark.png`; không xác nhận là texture | Sinh texture tia lửa riêng |
| Linh kiện / pivot | Hull, ụ và pod đã có bản xuất; pivot/ghép/xoay chưa được QA | Không kết luận bản nào hỏng chỉ vì pivot chưa đo; cần xem/kiểm sau |

Lô này chỉ tạo ảnh nguồn. Không tách nền, ghép, đo pivot, dựng GIF/frame-sheet hoặc xác nhận đầy đủ hồ sơ. Ngưỡng và planner không bị sửa.
