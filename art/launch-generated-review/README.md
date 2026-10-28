# PLAYER-10001 — ứng viên để USER xem mắt, KHÔNG đạt cổng số

Ảnh `source/PLAYER-10001-generated.png` được sinh mới bằng prompt USER, không trace/cắt sprite gốc. Master RGBA 1408×1408 giữ pixel nguồn không upscale; export 256² và ảnh 64². Cắt footprint từ ảnh sinh, không cắt reference. **Ngọn lửa chạm và bị cắt bởi cạnh dưới ảnh sinh**; thân và hai cánh nằm trọn. `preview/alpha-edges.png` đặt trên nền tối/xám/trắng: viền tối vẫn nhìn thấy trên nền sáng; chưa chứng minh không halo, cần xử lý lại trước khi tích hợp. License=UNKNOWN.

`preview/reference-overview.jpg` hiển thị nguyên contact sheet gốc (chỉ để review; không dùng trong game); ô ứng viên 150×150 đặt cạnh ô #1 cũng 150×150, không cắt/trace ảnh gốc. `preview/gameplay.jpg` hiển thị cả sprite 256 và bản 64 trên nền AI thử nghiệm trước đây. Bản 64 thực tế trong `preview/PLAYER-10001-64px.png`.

Số planner nguyên bản (xem `metrics/player.txt`) **exit 1**, chặn colors/val/val_std/chroma/grad_stops/detail; đây là bản xem hình, không phải file tích hợp, không phải PASS L3. Có thử lượng tử 20 mức + 150 màu + điều chỉnh saturation 0,9/brightness 0,98: colors=135, val=0,495, val_std=0,194, chroma=0,235, grad=33, detail=0,916; vẫn đỏ. Giữ export chưa lượng tử để USER xem hình nguyên hơn. Không thử làm phẳng/cắt bỏ chi tiết để ép số.

Chưa có mẫu enemy hay 23 slot; dừng xin USER xem mắt. USER duyệt hình không thay cho việc phải đạt cổng số trước khi giao.
