# Boss-37001 — cinematic / liên kết SPEC

**STATUS: CHƯA XONG.** Các bảng định lượng về họ đạn, 5 tham số GunData, hitbox, nguồn, ngưỡng HP, nhịp pha, chuyển trạng thái và các câu hỏi chưa có đáp án đã chuyển về [BOSS_SPEC.md](BOSS_SPEC.md). Tài liệu đó là bảng chính; không dùng các giá trị mô tả định tính trong bản cũ làm thông số cài đặt.

GIF cũ là choreography dựng sẵn, không phải replay engine, và có các sai khác với Boss Book 3.2 được liệt kê tại `BOSS_SPEC.md` mục **CLIP CẦN SỬA**. Khung impact 2–3 frame trong GIF là minh họa. Việc áp dụng hit-stop, camera, flash vào game phải xác định bằng số, đồng thời giữ input và telegraph không bị thay đổi; chưa có giá trị runtime đã duyệt.

## QA chặn hoàn thành

- Chốt câu hỏi nguồn/hitbox/đơn vị/nhịp và gán họ đạn trong `BOSS_SPEC.md`; không suy đoán pixel từ `border.w`.
- Đo pivot/điểm sinh và chứng minh 360°, kiểm alpha/halo; không dùng tọa độ `manifest.json` làm số đã xác thực.
- Kiểm va chạm, đường né, state/HP, thời gian và flash trong engine; GIF không chứng minh gameplay.
- Dựng lại theo bảng đã duyệt; xem không tiếng ba lần và trả lời được ba câu user đã giao. Chưa hoàn tất.
