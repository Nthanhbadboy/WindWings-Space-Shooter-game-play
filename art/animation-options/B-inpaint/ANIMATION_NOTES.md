# B-inpaint — gói THỬ

Slot: `game/art/ships/PLAYER-10001.png` (256²), `game/art/bosses/Boss-37001.png` (512²). Tĩnh nền; tất cả lớp phụ cùng canvas và cùng gốc. Không file lửa. `PLAYER-10001-canopy-glow.png` là pixels canopy từ ảnh gốc để bật/tắt trên canopy đã inpaint kín. Boss `-turret-left.png` / `-turret-right.png` là pod cắt từ đúng boss gốc; pivot ước lượng (88,217)/(424,217), chưa xác nhận chính xác. `Boss-37001-core-glow.png` lấy vùng lõi sáng từ ảnh gốc, tâm (256,226); thay opacity nhưng ánh sáng lõi vẫn nung trong nền ở ngoài vùng inpaint.

Pixel gốc RGB ngoài ba khu vực mask trên master: **0 pixel thay đổi** đã kiểm; export RGBA ngoài mask đã chiếu sang canvas và nở thêm biên lọc Lanczos 3px: **0 pixel thay đổi** so với gói C. Trong mask, các pixel có thể thay đổi hoàn toàn bởi inpaint. Xem `preview/*-inpaint-before-after.jpg` và mask ở `steps/`. Việc inpaint bao phủ cả footprint của pod, không thể xác nhận mỗi pixel tái dựng từng bị che; chất lượng viền nối/chồng lắp và pivot cần USER/coder kiểm. Không nhận khớp vật lý hay animation-ready tuyệt đối.

Planner trong `metrics/` đều exit 1; preview 20-unit chỉ mô phỏng, không phải screenshot game.
