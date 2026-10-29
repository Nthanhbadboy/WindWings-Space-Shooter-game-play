# Boss-37001 — tự kiểm ART, chờ USER duyệt

Chuẩn: Boss Book §3.2/§3.5, director `28716f4` §3.5(7), §6.4.2 và bảng số trong `BOSS_SPEC.md`. Các nhận định dưới đây chỉ về **ảnh và GIF dàn cảnh**, không phải kiểm thử game. GIF có một flash trắng toàn màn 0,3 giây; **cảnh báo trước khi xem**.

## Ba hồi khi xem không tiếng

Đã tự đối chiếu sheet toàn trận 64 mốc, mỗi mốc cách 0,5 giây (`exports/battle-study/timeline-review.jpg`), và các nhóm 5 khung trong 0,5 giây (`art-review-spans.jpg`):

1. **Áp đảo:** boss vào trong 1,5 giây, lõi/đầu pháo bật dần; cầu nặng cam có báo, boss tiến ép rồi lui.
2. **Bị thách thức:** thanh HP đổi bậc, lõi sáng lúc chuyển; laser tím, reticle bám tàu rồi khóa, bốn cặp tên lửa đỏ bay theo tọa độ cũ; đèn thành chuyển đỏ, báo hổ phách trước tia.
3. **Tuyệt vọng:** giáp chuyển mức vừa rồi nặng dưới 30%, đạn tỏa vàng, tia cuối hai chiều, quá tải sau khi HP dưới 15%; sau đó ụ trái nổ → pod phải cháy → điện → trắng → nổ/sóng + bốn mảnh → khói → kết quả giả.

Đây là xem mẫu khung và kiểm thời gian mã hóa, **không phải khẳng định đã thử điều khiển hay xem 2 clip gameplay**. Chuyển bậc hình là cắt thân tại khung va chạm, không trộn hai thân; kiểm hình ở `hull-variants-B2/stage-transition.gif` và sheet trước/sau. Hai ụ đã quay toàn vòng trên thân nguyên và hư nặng trong `assembly-360.gif`. Ba thân vẫn là cùng một tàu khi đặt cạnh nhau.

## Bộ đạn: đọc được — sống — công bằng về trình bày

Sheet không nhãn `exports/bullet-B2/projectile-real-size-unlabelled.png` dùng cùng tỉ lệ minh họa với GIF: PLAYER 18px; cầu cam 16px, laser tím 10×20px, tỏa vàng 10px, tên lửa đỏ 18px, tia cam là dải dài. Các nhóm khung 0,5s trong GIF cho thấy họ khác nhau qua hình/màu; tên lửa có khói xám đi sau thân và đổi hướng theo thân. Các thân và ba glow riêng có trong từng thư mục; `pulse-study.gif` minh họa nhịp 3 mức. Tâm sáng nhất biểu thị tâm dự kiến, không đồng nghĩa hitbox thực.

`beam-repeat.png` cho thấy 3 tile liền nhau; hai đầu body và từng glow trùng hàng pixel. `light-dark.png` cho từng họ và `fx-review.png` cho các FX chính được tự đối chiếu trên nền sáng/tối. Kiểm alpha bốn góc của body/glow đều bằng 0; các kích thước là 64², laser và dải tia 64×128. Đây là **tự kiểm art**; filtering, màu và scale tại runtime chuyển coder.

## Đoạn chết và cảnh báo

Đoạn riêng `exports/death-study/death-study.gif` dài 4,3 giây, gồm đúng 0,3 giây trắng, 4 mảnh và 1 giây khói cuối. GIF toàn trận dài 32 giây, 635 frame mã hóa / 32.000 ms, có mock kết quả. Flash được giữ theo kịch bản director; cần cảnh báo cho người xem và để coder xem xét tùy chọn giảm flash theo chính sách accessibility, không tự thay chuẩn đã chốt. Sóng xung kích **chưa xác minh xóa đạn trong engine**.

## Bàn giao engine

Collider đạn 0,15 unit, tia rộng 0,3 unit, damage 330/150/300, tốc độ, spawn/muzzle, ngưỡng HP, reticle, khe né, filtering, dọn đạn và tùy chọn accessibility: **CHUYỂN CODER QA**. Không xem phép đo hay hình dàn cảnh là bằng chứng gameplay. USER duyệt hình trước; coder sau đó cài hệ thống theo tình huống, không nhúng GIF.
