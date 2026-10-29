# Boss-37001 — SPEC cho coder (đề xuất, chưa triển khai)

## Nguyên tắc

Tọa độ local boss, pivot và vị trí spawn dùng `manifest.json` hiện có; đó là ước lượng, cần chốt bằng debug overlay. `cinematic-manifest.json` lưu SHA nguồn bổ sung, danh sách các thời điểm va chạm và hit-stop của mockup. GIF là choreography cố định 24 s, không phải replay engine. Không dùng timeline của GIF để buộc một trận thật đúng 24 s: state và HP làm nguồn chân lý.

## Trạng thái và ngưỡng

1. `ENTER` → `DOMINANT` sau khi hạ xong; không kích hoạt hitbox gây sát thương trong `ENTER`. Lần lượt bật visual turret-left, turret-right, core. Boss có chuyển động xuống/lùi, giới hạn trong vùng boss.
2. `DOMINANT` → `RECOGNIZE` khi HP **≤70%**, chỉ một lần, sau khi một đòn lớn kết thúc hoặc chuyển an toàn. `RECOGNIZE` 0,5 s: dừng movement và fire, core sáng; không đóng băng input PLAYER. → `ENRAGED`.
3. `ENRAGED` → `PANIC` khi HP **<30%**, một lần, sau khi xử lý an toàn đòn đang chạy; rung hình, khói, lõi quá tải; độ lệch bắn tăng có giới hạn và phải vẫn né được. Chỉ visual rung, không dịch hitbox theo mỗi rung.
4. HP ≤0 → `DYING`: chặn damage tiếp, dừng/spawn và hủy các đạn boss còn sống trong lúc sóng xung kích quét. Không áp dụng sát thương không báo trước. Diễn tuần tự **trái nổ → pod phải cháy → điện → lõi flash → nổ chính + mảnh vỡ + shockwave → 1 s khói**; tổng tối thiểu 3 s. Sau đó `DEAD`, trả kết quả màn chơi. `DYING` không gây va chạm bất ngờ.

## Các đòn / telegraph / hitbox

| State / đòn | Cảnh báo và lấy đà | Hoạt động / hitbox | Hồi phục / an toàn |
|---|---|---|---|
| `DOMINANT` heavy cannon | Sạc ít nhất 0,9 s, ụ lùi; một burst thưa | Viên riêng có collider nhỏ hơn vùng glow, spawn tại muzzle đã QA | ≥0,7 s, lõi yếu. Boss tiến/lùi có collision bounds, không ép PLAYER ra ngoài sân |
| Missile lock | ≥0,7 s reticle tại vị trí đã khóa; công khai lock | Missile có collider thân, bay về điểm đã khóa chứ không đổi hướng vô báo; hit/impact dùng collider rõ ràng, không dùng toàn bộ glow | ≥0,6 s sau loạt; reticle và điểm đến khớp |
| `ENRAGED` combo | ≥1,1 s sạc, pháo giật lùi và vạch báo hướng quét | Tia kích hoạt collider chỉ sau cảnh báo, hướng quét có thể dự đoán; hai ụ ép góc với corridor né vẫn đủ rộng cho PLAYER + biên an toàn | ≥0,6 s sau tia; lõi yếu |
| `PANIC` fan | ≥0,8 s vòng sạc | Nhiều viên, hướng lệch ngẫu nhiên có seed và giới hạn; kiểm tra luôn tồn tại đường né. Không coi glow là hitbox | Có nhịp nghỉ và giới hạn số đạn |
| `PANIC` desperate sweep | ≥0,6 s sạc và nghiêng, vạch hướng | Tia dài hơn ENRAGED; kiểm trước vệt né liên tục theo vị trí và tốc độ PLAYER; không kích hoạt collider trong telegraph | Kết thúc → cửa sổ phản công; không ép nhận sát thương |

Thông số giây là đề xuất từ mockup, không phải cân bằng đã thử. Đèn hai bên đồng bộ với state nguy hiểm; khói trôi một hướng và mảnh tàn rơi là visual không collider. Khung impact 2–3 frame ở 12 fps trong GIF là kỹ thuật hình ảnh: trong game ưu tiên freeze animation/camera ngắn thay vì khóa điều khiển hay thay đổi thời gian telegraph/hitbox; kiểm accessibility cho flash, rung và photosensitivity. Near-miss trong GIF là dàn cảnh toán học, **chưa** chứng minh collision hoặc đường né an toàn. Shockwave dọn đạn boss, không đụng projectile/player khác nếu chưa thiết kế rõ.

## QA bắt buộc

- Xem GIF không tiếng ba lần bởi người duyệt: kể lại 3 hồi; chưa hoàn tất.
- Debug alpha/halo, layer pivot và khớp muzzle khi xoay; hiện chỉ ước lượng.
- Mô phỏng HP ngưỡng, nhiều FPS, thời điểm hit-stop, hitbox vs glow, né an toàn, khóa mục tiêu và dọn đạn.
- Đảm bảo hiệu ứng không xuất hiện trước telegraph, không đột ngột đổi state/đòn, PLAYER vẫn có input và có thời gian hồi.
- Kiểm flash, readibility 64 px, performance và bản xem GitHub. Chưa có test runtime, chưa khẳng định PASS planner.
