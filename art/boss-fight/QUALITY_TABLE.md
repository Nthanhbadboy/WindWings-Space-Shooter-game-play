# Boss-37001 — bảng chất lượng hai tầng

Chuẩn director `28716f4` Book §3.5(7): hình được chấm tổng thể ở cỡ hiển thị và trong chuyển động; không còn chấm khớp giáp từng pixel. Đã **dừng** kỹ thuật decal A1–A6. [ENGINE] chuyển coder QA, không tính làm art chưa xong. Tình trạng: **ART CHƯA XONG**.

## [ART] Hư hại, lắp ghép, hoạt cảnh

| Món | ĐẠT / CHƯA | Lỗi cụ thể / đã tự xử lý | Số lần sinh lại |
|---|---|---|---:|
| Biến thể thân B1 — phân biệt 3 bậc cỡ game (câu 1) | CHƯA | Đã tự sinh 2 thân nguyên khối theo thân gốc, lắp các phần vào sheet 240×350; bậc 2/3 thấy vết cam nhưng trong GIF đã lượng tử vết còn nhỏ/mờ, cần tăng độ đọc và xem liên tục | 0 / 0 (B1 đầu tiên) |
| Biến thể — chuyển bậc (câu 2) | CHƯA | Đã dựng thử chuyển hẳn thân tại va chạm, không crossfade; chưa tự duyệt toàn bộ chuyển động trong GIF và clip toàn trận, chưa khẳng định hết ghosting/lỗ | 0 |
| Biến thể — cùng một boss (câu 3) | ĐẠT trên sheet thử | Cả ba có chung silhouette/thiết kế và cùng bộ pháo/pod; không đòi khớp từng pixel | 0 |
| Lắp ụ, pod / pivot | CHƯA | Hai ụ có đế/đầu độc lập, GIF xoay 360°; đã ghép vào biến thể, còn kiểm toàn vòng và cỡ game không lộ lỗ | trái 1 / phải 2 |
| Bộ đạn | CHƯA | Xem bảng riêng bên dưới: cần đọc cỡ game, tách glow, pulse, tile và đuôi tên lửa | theo họ |
| Death GIF | CHƯA | Study 4,3 s có 4 mảnh và khói 1 s; flash trắng toàn màn 0,3 s cần kiểm visual/accessibility, chưa chốt art | — |
| GIF toàn trận + manifest | CHƯA | Đã gắn thân B1 vào study toàn trận, nhưng đạn vẫn nháp cũ; chưa duyệt liền mạch và chưa khóa clip | — |
| SPEC/kịch bản | CHƯA | Đã cập nhật §3.5(7) và bảng họ đạn ứng viên, chưa chốt sản phẩm/manifest | — |

## [ART] Bảng bộ đạn mới

Số lần sinh lại là số lần sinh thay thế trong loạt bộ đạn mới, không tính master B1 đầu tiên. Toàn bộ `bullet-B1` là ứng viên, không phải export cuối.

| Họ | ĐẠT / CHƯA | Lỗi cụ thể | Số lần sinh lại |
|---|---|---|---:|
| Cầu DOMINANT | CHƯA | Cầu cam đọc được trên sheet thử; glow vẫn nung trong body, 3 glow chỉ là lớp bổ sung, chưa clean split / QA pulse | 0 |
| Laser ENRAGED | CHƯA | Có silhouette tím dài 64×128; ở sheet đề xuất nhìn rất mảnh, glow trong body, chưa QA pulse/halo | 0 |
| Tỏa PANIC | CHƯA | Sao vàng khác hình, nhưng quá nhỏ ở sheet; glow trong body, chưa QA từng viên khi tỏa | 0 |
| Tên lửa khóa | CHƯA | B1 mũi đỏ nhưng thân tối gần mất trên nền game, điểm sáng ở mũi không phải tâm; B2 sáng hơn nhưng thành pixel art sai phong cách, loại; khói riêng chưa kiểm điểm gắn | 1 |
| Đầu tia + thân tia | CHƯA | Đầu corona và dải cam có nguồn; thân chưa có glow 3 trạng thái và mép tile chưa khớp/kiểm lặp | 0 |
| Khói đuôi | CHƯA | Nguồn rời không nung vào tên lửa; nền đen làm mất khói tối, chưa gắn đuôi/QA halo | 0 |
| Sheet cỡ thật | CHƯA | Sheet hiện tại dùng PLAYER 18 px = 1,4 unit và kích thước đề xuất; tên lửa gần vô hình, fan/laser khó đọc, chưa là tỷ lệ bay được xác nhận | — |

## [ENGINE] CHUYỂN CODER QA — không chặn hoàn thành ART

| Món | Chuyển giao |
|---|---|
| Collider 0,15 unit đạn / tia rộng 0,3 unit; speed và damage | CHUYỂN CODER QA |
| Khe né thật, quỹ đạo, lock, nhịp và các pha theo HP | CHUYỂN CODER QA |
| Muzzle/điểm gắn và đuôi khói trong runtime | CHUYỂN CODER QA |
| Tia tile/filter, dọn đạn bằng sóng xung kích | CHUYỂN CODER QA |

## Ghi chú tiến độ

Thân B1: `exports/hull-variants/three-stages-gameplay.png`, `stage-transition.gif`, manifest; thân vừa dùng nền trắng do model tạo nên dùng alpha thân nguyên vẹn và giữ mép silhouette gốc để chống viền. Chỉ kiểm tổng thể, không chấm từng pixel. Ngưỡng clip minh họa: ≤30% hư hại vừa, <15% nặng; không thay Book.

Bộ đạn: `exports/bullet-B1/projectile-real-size-study.png`, từng thư mục `body.png` / `glow-0..2.png`, manifest. Đây chỉ là các bước tự xử lý, không phải sản phẩm đạt; thân B1 đã tích hợp GIF study, đạn B1 chưa tích hợp. Lỗi được ghi đúng ở bảng trên.
