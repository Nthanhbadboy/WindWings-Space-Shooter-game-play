# 49 — Nhìn ảnh để đọc luồng UI / stage

**Tạm thời, chỉ mô tả những gì thấy trong ảnh.** Theo yêu cầu mới: tập trung
luồng UI/màn chơi, để chuyện Premium và số liệu balance sang sau. Không dùng
ảnh để vẽ lại asset hay đo kích thước/font/toạ độ; raw APK vẫn là nguồn dựng UI.

Đã xem **35 PNG**, cả ba contact sheet và mở riêng các frame intro, tutorial
so sánh tàu, boss. Nguồn pinned remote `25c367aca99f06f14df546d2f30e60b427827157`,
`docs/apk-analysis/ramus/2026-10-23-phone/`. Manifest giữ git blob + SHA256 của
**từng PNG** ở `reverse-engineering/raw/ui-flow-review/image-sources.json`.
Ảnh gốc còn trong Git của nhánh kia; chỉ thêm JPEG thu nhỏ để duyệt, không chép
lại full PNG. Contact sheet **xếp theo tên file**, không phải timeline đã xác minh.

## Luồng nhìn thấy / luồng ứng viên

```text
INTRO: STAGE 1 [NORMAL] + tàu trong vòng tròn + TOUCH TO PLAY
    ⇢ vào gameplay, HUD xuất hiện / nền thế giới xuất hiện
    ⇢ hướng dẫn kéo ngón tay điều khiển tàu
    ⇢ chiến đấu với đội hình enemy + đạn / vật phẩm
       ├─ overlay nhả ngón tay để đổi tàu + special cannon
       └─ overlay so sánh Switch ships wisely: Hard fight / Easy kill
    ⇢ boss robot vàng, các frame tấn công khác nhau
    ⇢ trạng thái VICTORY nhìn được phía sau modal
    ? màn kết quả sạch / Continue / màn kế tiếp chưa nhìn thấy
```

`⇢` là chuỗi diễn giải **ứng viên** từ các trạng thái hình ảnh, không phải trace
sự kiện/input đã được chứng minh. Hai tutorial không được coi là các màn riêng
hay thứ tự cố định chỉ vì tên ảnh. Đặc biệt `live_1_Game.png` có hint nhả tay khi
boss đã ở trên màn hình: hint đó không thể bị ép chỉ xuất hiện lúc đầu wave.

## Các trạng thái UI cụ thể

| Trạng thái | Nhìn thấy | Ảnh kiểm |
|---|---|---|
| Chờ bắt đầu | Nền xanh, STAGE 1 / [NORMAL], tàu lớn trong vòng tròn, TOUCH TO PLAY; không phải menu chọn stage | live_6, live_7, r2_1–3 |
| Frame chuyển tiếp ứng viên | Nền xanh, tàu nhỏ và một phần HUD, không còn title/vòng tròn | screenshot_frozen_stage1 |
| Hướng dẫn di chuyển | Nền Trái Đất/công trình đã hiện, tàu phía dưới; chữ Move your finger to control the spaceship; có ảnh bàn tay | after_touchtoplay, screenshot_unfrozen_stage1 |
| Hướng dẫn nhả tay | Dải overlay tối phía trên, chữ hướng dẫn, panel tàu/phun lửa bên phải, thế giới và HUD vẫn thấy | p_2, screenshot_now, live_1 |
| So sánh đổi tàu | Hai panel cyan Hard fight / Easy kill, chữ Switch ships wisely ở giữa; phủ trên chiến trường chứ không thay cảnh | p_4 |
| Chiến đấu thường | Các đội hình enemy, đạn, pickup/coin; HUD vẫn ở trên | p_1, p_3, p_5–6, slow_7–8 |
| Boss | Robot vàng lớn ở trên, tàu chơi ở dưới; các frame có thanh đỏ, đạn xanh, cung chém | slow_9–12 |
| Kết quả bị che | VICTORY phía sau modal; không nhìn được toàn bộ điều khiển kết quả | live_2–5, victory_next1–3, victory_tapoutside, victory_wait60s |

Tên frozen/running/next/wait60s là nhãn file của người thu, **không tự chứng minh**
app bị freeze, đã bấm Next thành công hoặc đã chờ đúng60s.

## Cái ảnh giúp làm rõ

- Cần tách **intro chờ chạm** khỏi gameplay. Không nên đưa tàu vào bắn ngay lúc
  mới vào stage mà bỏ trạng thái TOUCH TO PLAY.
- Tutorial là **các lớp phủ trên gameplay**, ít nhất có ba dạng nhìn được: kéo
  ngón tay, nhả ngón tay/đổi tàu, và so sánh hai tàu. Không gộp thành một popup
  hướng dẫn chung; cũng không chuyển scene riêng chỉ để hiển thị chúng.
- HUD nhìn được gồm icon tàu/thanh xanh và các vạch phía trái, coin ở trên,
  pause góc phải. Có nhóm counter/icon phía phải và marker ở boss; **không gán
  nghĩa/giá trị chính xác từ ảnh** nếu chưa đối chiếu APK.
- Cần có trạng thái thường → boss → endgame trong checklist dựng flow. Ảnh boss
  chỉ là vài mẫu frame, chưa đủ để dựng timing, pattern đạn hay phase transition.

## Chưa thấy — đừng lấp bằng suy đoán

1. **Không có title STAGE 2 hay STAGE 3** trong bộ này. `p_2`, `r2_2`, `slow_9`
   không phải số stage; không dùng chúng để nói đã xem đủ stage1→2→3.
2. Không có màn kết quả sạch: chưa nhìn thấy/kiểm được nút Continue/Replay,
   màn nhận thưởng và nhánh quay về Home/Map.
3. Không có ảnh Home/Map/chọn stage trong bộ35PNG này.
4. Các ảnh intro lặp lại đều ghi STAGE1: chưa đủ biết đó là replay, phiên mới,
   hay đã chuyển stage rồi quay lại. Không nối nó thành cạnh tự động Victory→Stage1.
5. Không biết gameplay có bị pause dưới tutorial hay không chỉ từ ảnh tĩnh.
   Để nội dung modal Premium sang sau; việc nó che kết quả chỉ là giới hạn quan sát.

**Ảnh cần thu bổ sung:** kết quả không bị che → thao tác Continue → title stage2
→ tutorial/HUD stage2 → kết quả → title stage3; kèm timestamp và action log.
Chưa cần đào balance Premium cho mục tiêu này.

## Duyệt nhanh

- [Sheet1](ui-flow-review/contact-1.jpg): hint di chuyển/nhả tay, intro, gameplay.
- [Sheet2](ui-flow-review/contact-2.jpg): so sánh tàu, intro lặp, frame chuyển tiếp.
- [Sheet3](ui-flow-review/contact-3.jpg): boss và các ảnh kết quả bị che.

Raw quan sát theo tên từng ảnh: `reverse-engineering/raw/ui-flow-review/observations.json`.
Không thay thế những OPEN runtime trước; đây là lớp ghi nhận trực quan bổ sung.
