# Boss-37001 — HỒ SƠ CHỈNH CHU — CHỜ USER DUYỆT

Chuẩn tổng thể director `28716f4` Book §3.5(7); không chấm khớp từng pixel. Đã ngừng decal A1–A6. [ART] là tự kiểm hình/GIF dàn cảnh; **không phải USER đã duyệt hoặc runtime đã QA**. [ENGINE] chuyển coder QA và không chặn ART.

## [ART] Thân, lắp ghép, hoạt cảnh

| Món | ĐẠT / CHƯA | Kết quả tự kiểm / lỗi còn lưu ý | Số lần sinh lại |
|---|---|---|---:|
| Thân B2 — phân biệt 3 bậc cỡ game (câu 1) | ĐẠT | Sheet 240×350 và timeline phân biệt nguyên/vừa/nặng; chưa kiểm runtime | 1 / 1 |
| Chuyển bậc trong chuyển động (câu 2) | ĐẠT | Chuyển nguyên thân tại va chạm; test trước/sau không thấy ghost/lỗ hay mất thân | 1 / 1 |
| Cùng một boss (câu 3) | ĐẠT | Ba bậc chung silhouette/thiết kế, dùng chung ụ và pod | 1 / 1 |
| Lắp ụ/pod, pivot | ĐẠT | Hai ụ có đế tĩnh/đầu xoay, test 360° trên thân nguyên/hư nặng, sheet 8 hướng ở cỡ game | trái 1 / phải 2 |
| FX chính sáng/tối | ĐẠT | Tự xem charge, reticle, overload, muzzle, arc, nổ ụ/pod, khói, nổ chính, shockwave và impact trên hai nền (`fx-review.png`) | theo nguồn trước |
| Đoạn chết riêng | ĐẠT | 4,3 s, trắng 0,3 s, bốn mảnh, 1 s khói; **cảnh báo flash trắng toàn màn**, tùy chọn giảm flash chuyển coder | — |
| GIF toàn trận + frame sheet | ĐẠT | 32 s, 635 frame mã hóa; 64 mốc 0,5 s và các span 0,5 s đã đối chiếu ba hồi; **không phải QA gameplay** | — |
| SPEC, kịch bản, manifest | ĐẠT | §3.5 và 7 quyết định, họ đạn/điểm sinh art, kịch bản và manifest; vẫn chờ USER duyệt | — |

## [ART] Bộ đạn boss

Số sinh lại tính từ master đầu tiên của từng họ trong bộ mới. Sheet không nhãn dùng PLAYER 18 px = 1,4 unit và các cỡ bay **của GIF minh họa**, không khẳng định cỡ runtime.

| Họ | ĐẠT / CHƯA | Tự kiểm art | Số lần sinh lại |
|---|---|---|---:|
| Cầu DOMINANT | ĐẠT | Cầu cam lõi sáng; core/glow riêng, 3 mức pulse, canvas 64² | 1 |
| Laser ENRAGED | ĐẠT | Thuôn tím, core/glow 3 mức, canvas 64×128; phân biệt cầu trong các span 0,5 s | 1 |
| Tỏa PANIC | ĐẠT | Hình thoi vàng nhỏ, core/glow 3 mức, từng viên nhìn được trong span nhiều viên | 1 |
| Tên lửa khóa | ĐẠT | Đỏ, tâm sáng, 64², khói rời phía đuôi và đổi hướng cùng thân; pulse 3 mức | 2 |
| Đầu/thân tia | ĐẠT | Đầu tia và dải 64×128, glow 3 mức; hai đầu tile khớp ở lớp body/glow, có ảnh lặp | 0 |
| Khói đuôi | ĐẠT | Layer riêng, chỉnh xám để đọc trên gameplay, gắn sau tên lửa trong các mẫu clip | 0 |
| Sheet cỡ game | ĐẠT | Sheet không nhãn cạnh PLAYER, ảnh sáng/tối và các span 0,5 s; cỡ runtime chuyển coder | — |

## [ENGINE] CHUYỂN CODER QA — không chặn hoàn thành ART

| Món | Chuyển giao |
|---|---|
| Collider 0,15 unit đạn / tia rộng 0,3 unit; speed và damage | CHUYỂN CODER QA |
| Khe né thật, quỹ đạo, lock, nhịp và các pha theo HP | CHUYỂN CODER QA |
| Muzzle/điểm gắn và đuôi khói trong runtime | CHUYỂN CODER QA |
| Lọc tile, dọn đạn bằng sóng xung kích, tùy chọn giảm flash | CHUYỂN CODER QA |

Chi tiết đánh giá, phạm vi và cảnh báo: `ART_REVIEW.md`. Tệp, nguồn và SHA: `FINAL_ART_MANIFEST.json` cùng manifest trong từng nhóm. GIF là minh họa, coder không được nhúng GIF hay dùng mốc giây làm logic trận.
