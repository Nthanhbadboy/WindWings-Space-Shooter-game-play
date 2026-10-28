# Animation notes — NHÁP / CHƯA SẴN SÀNG TÍCH HỢP

Đây là thử nghiệm tách pixel, **không phải bàn giao cuối**. Cả hai hình là generate; ảnh PLAYER gốc đúng byte với master đã duyệt. Chưa vẽ lại hay tạo riêng các bộ phận boss. Hai file trong `exports/ships/` và `exports/bosses/` chỉ dùng xem thử, chưa chép vào `game/art/`.

## PLAYER-10001 (canvas 256², tâm 128,128)

- Thân tĩnh: `exports/ships/PLAYER-10001.png`; tương ứng slot `game/art/ships/PLAYER-10001.png`, **không dùng tích hợp**.
- Nhấp nháy thử: `exports/layers/ships/PLAYER-10001-glow.png`, căn cùng canvas 256², tâm 128,128; gồm các pixel sáng được chọn trong vùng canopy. Không có lớp nozzle glow đầy đủ, vì ánh sáng cam đã nung vào kim loại và không có ảnh kim loại phía sau.
- Lửa bị loại bằng mask từ ảnh thật, chứng cứ tại `steps/PLAYER-10001-removed-flame.png`; mask cũng cắt mất một số pixel thân và để lại đốm sáng ở họng máy. Các pixel phản xạ cam nằm lẫn trong thân không thể phục hồi chính xác từ một ảnh phẳng mà không ước lượng/vẽ lại. Lớp glow trích từ ảnh gây lỗ trong canopy khi tắt; không phải lớp emission vật lý. **Không thể nhận tàu sạch/nozzle sạch như yêu cầu.**

## Boss-37001 (canvas 512², toàn bộ lớp cùng gốc và căn chỉnh)

- `exports/bosses/Boss-37001.png`: ảnh đầy đủ để tham khảo, tương ứng slot `game/art/bosses/Boss-37001.png`; **không dùng tích hợp**.
- `Boss-37001-body.png`: các pixel còn lại sau phân vùng. Để tĩnh.
- `Boss-37001-turret-left.png` / `-right.png`: phân vùng theo X<135 và X≥377. Pivot ước lượng lần lượt **(88,217)** / **(424,217)** theo pixel canvas gốc, chuẩn hóa (0,171875,0,423828125) và (0,828125,0,423828125), chưa chứng minh là trục thật. Hai phần chứa toàn bộ pod, không phải riêng nòng pháo.
- `Boss-37001-core.png` / `-glow.png`: vùng elip quanh (256,226), bán trục 43×45px; glow là các pixel xanh sáng bên trong elip. Đặt cùng gốc (0,0), không offset; glow chỉ là mask của ảnh phẳng, không phải emission tách vật lý.
- Năm mask phân vùng không chồng lấn, lấy từ **một** ảnh boss. Khi alpha-composite, alpha khớp, pixel đục khớp, nhưng 361 pixel biên có RGB chênh do làm tròn (tối đa 5/255); không khai khớp byte từng pixel. Đường chia thẳng có thể cắt qua chi tiết.
- **Không xoay tháp pháo trong game:** ảnh gốc không có giáp/nền bị pod che, nên xoay để lộ lỗ; pivot chỉ ước lượng, không thể xác nhận "đúng tâm" từ ảnh phẳng. Cần USER duyệt phương án tạo phần bị che hoặc asset có lớp riêng trước khi coder dùng.

Cả hai asset chưa qua sàn máy (`metrics/`), preview chỉ là ảnh ghép mô phỏng, không phải runtime. Không nhận PASS L3. License UNKNOWN.
