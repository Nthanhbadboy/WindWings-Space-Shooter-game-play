# A-clean — gói THỬ, không khẳng định đã sạch toàn bộ ánh sáng

Đường dẫn slot là tương đối trong thư mục này: `game/art/ships/PLAYER-10001.png` (256²) và `game/art/bosses/Boss-37001.png` (512²). Mọi lớp phụ cùng canvas và tâm gốc (0,0); ảnh slot là hình tĩnh, phụ là tùy chọn thử. Không có file lửa; particle do coder.

- Tàu: `game/art/layers/ships/PLAYER-10001-canopy-glow.png` tâm (128,96), `PLAYER-10001-nozzle-glow.png` tâm (128,211); điều khiển opacity/nhấp nháy, không xoay. Lớp là ảnh AI glow riêng, không có flame.
- Boss: `game/art/layers/bosses/Boss-37001-turret-left.png` và `-right.png`, mỗi lớp 512². Tâm đặt pod (100,220)/(412,220); tâm quay đề xuất xấp xỉ (100,191)/(412,191), chỉ là ƯỚC LƯỢNG từ ảnh, chưa được kiểm bằng runtime. `Boss-37001-core-glow.png` tâm (256,210), đổi opacity.
- Hull boss được AI sinh liền bên dưới vị trí pod; pod sinh riêng. AI không giữ chính xác silhouette gốc, tàu A bị giản lược/phẳng hơn dù không cố ý làm xấu. Canopy tàu vẫn có highlight và boss vẫn có vài đèn amber/teal nung trong ảnh nền, nên yêu cầu **no baked lighting chưa được đảm bảo**; glow tắt không thể làm chúng tối hoàn toàn. Pháo, ánh sáng và vị trí là prototype, cần USER/coder kiểm mắt và chạy thật.
- Planner đo riêng body/ship, xem `metrics/`; mọi kết quả exit 1. `preview/gameplay-20units.jpg` là mô phỏng 20-unit, không phải screenshot engine. 64px gồm ảnh nền và bản composite.
