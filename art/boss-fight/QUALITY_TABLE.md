# Boss-37001 — bảng chất lượng hai tầng

Chuẩn director `28716f4` Book §3.5(7): hình được chấm tổng thể ở cỡ hiển thị và trong chuyển động; không còn chấm khớp giáp từng pixel. Đã **dừng** kỹ thuật decal A1–A6. [ENGINE] chuyển coder QA, không tính làm art chưa xong. Tình trạng: **ART CHƯA XONG**.

## [ART] Hư hại, lắp ghép, hoạt cảnh

| Món | ĐẠT / CHƯA | Lỗi cụ thể / đã tự xử lý | Số lần sinh lại |
|---|---|---|---:|
| Biến thể B2 — phân biệt 3 bậc cỡ game (câu 1) | ĐẠT | Đã sinh lại thân nguyên khối với vết ngoài giáp rộng hơn; sheet gameplay 240×350 thể hiện nguyên/vừa/nặng phân biệt được | 1 / 1 |
| Biến thể — chuyển bậc (câu 2) | ĐẠT trong test art | Đổi nguyên thân tại va chạm, không crossfade; sheet trước/sau và GIF test không thấy ghosting/lỗ hay mất thân | 1 / 1 |
| Biến thể — cùng một boss (câu 3) | ĐẠT | Ba bậc chung silhouette/thiết kế và cùng bộ pháo/pod trong sheet gameplay, không đòi khớp từng pixel | 1 / 1 |
| Lắp ụ, pod / pivot | ĐẠT trong test art | Hai ụ có đế/đầu độc lập; test lắp nguyên vẹn và hư nặng xoay 360°, sheet 8 hướng không thấy lỗ ở cỡ game | trái 1 / phải 2 |
| Bộ đạn | CHƯA | Xem bảng riêng bên dưới: cần đọc cỡ game, tách glow, pulse, tile và đuôi tên lửa | theo họ |
| Death GIF | CHƯA | Study 4,3 s có 4 mảnh và khói 1 s; flash trắng toàn màn 0,3 s cần kiểm visual/accessibility, chưa chốt art | — |
| GIF toàn trận + manifest | CHƯA | Đã gắn thân B2, đạn B2/B3, pulse và kết quả giả vào GIF study 32s; chưa duyệt toàn bộ liên tục không tiếng/chưa khóa clip | — |
| SPEC/kịch bản | CHƯA | Đã cập nhật §3.5(7), họ đạn B2/B3 và anchor đề xuất; manifest đang là candidate, chưa chốt sản phẩm | — |

## [ART] Bảng bộ đạn mới

Số lần sinh lại là số lần sinh thay thế trong loạt bộ đạn mới, không tính master B1 đầu tiên. Toàn bộ `bullet-B1` là ứng viên, không phải export cuối.

| Họ | ĐẠT / CHƯA | Lỗi cụ thể | Số lần sinh lại |
|---|---|---|---:|
| Cầu DOMINANT | CHƯA | B2 cam, tâm sáng; body/glow 3 trạng thái tách riêng, còn kiểm nhịp pulse ở cỡ hiển thị | 1 |
| Laser ENRAGED | CHƯA | B2 tím hình thuôn đọc rõ hơn; body/glow 3 trạng thái, còn duyệt pulse/halo trong chuyển động | 1 |
| Tỏa PANIC | CHƯA | B2 vàng hình thoi; còn duyệt nhịp và độ phân biệt khi bắn nhiều viên | 1 |
| Tên lửa khóa | CHƯA | B3 hình kim khí sáng tâm, tô đỏ khác cầu; glow và khói riêng; đã thử gắn đuôi, còn kiểm xoay và pulse trong clip | 2 |
| Đầu tia + thân tia | CHƯA | B1 tạo body/glow 3 trạng thái, nhân bản đối xứng cho hai đầu tile trùng pixel; còn xem chuyển động/pulse cỡ game | 0 |
| Khói đuôi | CHƯA | Tự chỉnh chiết khói thành xám thay vì trắng gắt, gắn đuôi theo góc; còn kiểm khi nhiều quả bay | 0 |
| Sheet cỡ thật | CHƯA | Sheet dùng PLAYER 18 px = 1,4 unit, 5 họ khác silhouette/màu; chỉ là tỷ lệ art demo chưa chốt, cần kiểm nhận biết trong 0,5s không nhãn | — |

## [ENGINE] CHUYỂN CODER QA — không chặn hoàn thành ART

| Món | Chuyển giao |
|---|---|
| Collider 0,15 unit đạn / tia rộng 0,3 unit; speed và damage | CHUYỂN CODER QA |
| Khe né thật, quỹ đạo, lock, nhịp và các pha theo HP | CHUYỂN CODER QA |
| Muzzle/điểm gắn và đuôi khói trong runtime | CHUYỂN CODER QA |
| Tia tile/filter, dọn đạn bằng sóng xung kích | CHUYỂN CODER QA |

## Ghi chú tiến độ

Hư hại B2: `exports/hull-variants-B2/three-stages-gameplay.png`, `stage-transition.gif`, `assembly-360.gif`, manifest. B1 giữ làm lịch sử; alpha biên dùng thân gốc để chống nền sai. Ngưỡng clip minh họa ≤30% vừa, <15% nặng; không thay Book.

Bộ đạn: `exports/bullet-B2/projectile-real-size-study.png` và bản không nhãn, `pulse-study.gif`, `beam-repeat.png`, `missile-tail-test.png`, manifest. Các họ năng lượng được tách phần corona theo alpha và tạo glow 3 mức; core vẫn có tâm phát sáng, không tuyên bố thuật toán tách mọi ánh sáng chính xác tuyệt đối. Sheet PLAYER 18 px / 1,4 unit, art widths đề xuất 16/10/10/18 px. Đây là cỡ của **study**, không phải xác nhận runtime.

GIF study mới `exports/battle-study/battle-study.gif` 32 s, có 0,3 s flash trắng toàn màn, 4 mảnh, 1 s khói và màn kết quả giả; gắn B2/B3, vẫn CHƯA khóa cho đến khi duyệt chuyển động và bộ đạn. Chưa tuyên bố hồ sơ hoàn chỉnh.
