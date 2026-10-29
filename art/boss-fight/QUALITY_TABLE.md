# Boss-37001 — bảng chất lượng / đang dở

Đối chiếu nguồn chính thức bằng `git show` commit `185aa8b09cb30209a8a02871d27674ad048f1407` từ nhánh `arena/020ecffe-windwings-space-shooter-game-p`: `03_BOSS_BOOK.md` §3.2/§3.5, `04_COMBAT_FX_ART_ANIMATION.md` §4.1, `06_PRODUCTION_ROADMAP.md` §6.4.1. Không sửa/cherry-pick tài liệu. Quy định mới của USER ưu tiên chất lượng; năng lực công cụ thực tế vẫn tối đa 10 ảnh mỗi turn, ảnh lỗi sinh lại turn sau. **ĐẠT chỉ khi xác thực toàn bộ tiêu chí liên quan; ứng viên chưa được coi là hoàn thành.** Số sinh lại dưới đây tính lần thử thay thế trong lịch sử bộ ảnh này, không tính hậu kỳ.

| Món | ĐẠT / CHƯA | Lỗi/thiếu cụ thể đang thấy | Số lần sinh lại |
|---|---|---|---:|
| Thân trần | CHƯA | Master `round4/01-hull.png` đã đóng ổ giữa; chưa chứng minh tách alpha/halo và thân không pháo ma ở cỡ game; kiểm trên sáng/tối | 2 |
| Ụ pháo trái | CHƯA | Master `02-left-turret.png` gắn phần ụ và vòng đế trong cùng ảnh; xoay cả sprite sẽ xoay cả vòng, chưa có lớp đế tĩnh riêng; pivot còn ước lượng, chưa có GIF 360°/halo | 0 |
| Ụ pháo phải | CHƯA | Master `round2/03-right-turret-redo.png` gồm ụ + vòng đế trong cùng ảnh, chưa tách đế tĩnh/đầu xoay; pivot ước lượng, chưa GIF 360°/kiểm lắp | 1 |
| Pháo giữa | CHƯA | Có nguồn và layer; chưa kiểm sạch alpha, điểm gắn và quay; chưa có chứng minh pivot | 2 |
| Pod trái | CHƯA | Nguồn và layer có; chưa duyệt mép/halo khi lắp | 2 |
| Pod phải | CHƯA | Sinh lại theo pod trái; chưa kiểm pixel/alpha/halo và mép ghép | 1 |
| Lõi teal | CHƯA | Có layer core, chưa chứng minh tâm và độ đọc ở kích thước game | 0 |
| Overlay hư hại bậc 2 | CHƯA | A1 vẽ lại boss, sai. A2 tối chìm nền; A3 #01 vệt chém dị dạng, #02 nứt + khói độc lập. Đã thử RGBA 512², không tràn hull theo alpha, nhưng chưa chứng minh vết khớp cấu trúc từng pixel/halo ở cỡ thật | 3 |
| Overlay hư hại bậc 3 | CHƯA | A1 vẽ lại boss, sai. A2 là họa tiết rời. Đã thử RGBA 512² không tràn hull theo alpha; vết nứt vẫn như phủ lên bề mặt, chưa chứng minh khớp cấu trúc từng pixel/halo ở cỡ thật | 1 |
| Mảnh giáp vỡ | CHƯA | `A1/03` có một mảnh; chưa tách alpha, kiểm cỡ thật và chuỗi 3–4 mảnh | 0 |
| Nổ frame 1 — chớp | CHƯA | `A1/04` nguồn rời; chưa tách alpha, chưa chứng minh giữ tâm và timing | 0 |
| Nổ frame 2 — lửa | CHƯA | `A1/05` nguồn rời; chưa kiểm chuyển tiếp liên tục từ frame 1 | 0 |
| Nổ frame 3 — khói tàn | CHƯA | `A1/06` nguồn rời; chưa kiểm chuyển tiếp liên tục từ frame 2, bản thử 3 giây | 0 |
| Texture khói | CHƯA | `A1/07` là khối khói; chưa tách nền/halo hoặc kiểm lặp nếu cần | 0 |
| Texture tia lửa | CHƯA | `A1/08` là trường tia lửa; chưa tách nền/halo hoặc kiểm lặp nếu cần | 0 |
| Cầu năng lượng | CHƯA | Có export 64²; chưa QA halo và vị trí sinh | 0 |
| Đạn laser | CHƯA | Có export 64×128; chưa QA halo và đọc ở cỡ thật | 0 |
| Dải tia | CHƯA | Đầu/cuối đồng pixel sau hậu kỳ; chưa thử tile/filter trong engine | 0 |
| Đầu tia | CHƯA | Có export; chưa kiểm tâm, halo trên hai nền | 0 |
| Vòng sạc | CHƯA | Bản trước cắt mép; có bản sinh lại, chưa QA alpha/timing | 1 |
| Tên lửa | CHƯA | Có export, chưa kiểm hitbox và gốc phóng | 0 |
| Chớp đầu nòng | CHƯA | Có export; chưa kiểm đăng ký đúng muzzle | 0 |
| Sóng xung kích | CHƯA | Có export, chưa kiểm halo và xóa đạn engine | 0 |
| Cảnh báo tia | CHƯA | Có asset amber; chưa kiểm ở kích thước thật, nhịp | 0 |
| Đuôi tên lửa | CHƯA | Có asset; chưa kiểm hướng và điểm gắn | 0 |
| Tia lửa va chạm | CHƯA | Có asset; chưa kiểm alpha và timing | 0 |
| Lõi quá tải | CHƯA | Có asset; chưa kiểm halo, nhịp dưới 15% | 0 |
| Điện dọc thân | CHƯA | Có asset; chưa kiểm registration thân và halo | 0 |
| Đèn thành | CHƯA | Có asset; chưa xác nhận chuyển đỏ khi sạc tia | 0 |
| Pháo nổ | CHƯA | Master `turret-destruction` chỉ cách mép trên 3 px theo ngưỡng; chưa QA có bị cắt | 0 |
| Pod cháy | CHƯA | Có asset; chưa kiểm ghép vào pod phải | 0 |
| Nổ chính | CHƯA | Bản gốc bị cắt; bản redo chưa thử đoạn chết/halo | 1 |
| Tên lửa va chạm | CHƯA | Bản gốc bị cắt; bản redo chưa thử impact frame/halo | 1 |
| Lõi trắng | CHƯA | Bản gốc bị cắt; bản redo chưa kiểm flash 0,3 s và accessibility | 1 |
| Tia quét chính / cuối | CHƯA | Script hiện quét đầu 1,4 s, góc −24°→24°, sạc 1,1 s; Boss Book yêu cầu 1,2 s, −25°→25° trong 1,9 s. Tia cuối hiện chỉ một chiều, không phải hai chiều liên tiếp | Không áp dụng (choreography) |
| Khóa + tên lửa | CHƯA | Script dùng 3 cặp và điểm mục tiêu lệch 100/105 px khỏi PLAYER; sách yêu cầu reticle bám 0,8 s rồi khóa/phóng 4 cặp | Không áp dụng (choreography) |
| Cái chết | CHƯA | Đã có đoạn dàn cảnh nhưng chưa kiểm trực quan 3 giây riêng, sự liên tục/khung; số mảnh văng trong script 10 thay vì 3–4 | Không áp dụng (choreography) |
| GIF toàn trận + frame sheet | CHƯA | Bản cũ trên GitHub chưa khớp Boss Book các dòng trên; chưa tự xem không tiếng và trả lời 3 câu user yêu cầu; chưa kiểm cỡ thực và né an toàn | Không áp dụng (render) |
| BOSS_SPEC / gameplay | CHƯA | SPEC hiện đề xuất, không có hitbox chạy thật và chưa đối chiếu đầy đủ nhịp Boss Book 3.2 | Không áp dụng |

## Turn hiện tại — Director 185aa8b

Đã thay `BOSS_SPEC.md` theo 6 quyết định (damage 330/150/300, collider 0,15 unit và 0,3 unit tia; nhịp không cộng). Các con số hoạt cảnh trước đây vẫn CHƯA được sửa trong GIF.

A3 #01 là vệt chém/điện, không giống cháy giáp, lỗi. A3 #02 tạo các cụm nứt + khói, không vẽ cả boss; đã tạo ảnh RGBA 512² thử nghiệm từ #02 và A2 bậc 3, tạo composite nền sáng/tối. Cả hai có góc alpha bằng 0; so alpha với thân: 0 pixel alpha >0 nằm ngoài hull. Đây **không** chứng minh vết nứt khớp hình giáp từng pixel, không phải duyệt cuối hay xuất production. Vết nứt bậc 3 nhìn như lớp phủ nằm trên giáp; cần sửa/soi thêm ở cỡ thật.

Dở tại: hai overlay là bản thử, chưa chốt độ khớp và halo; pivot hai ụ chưa đo hay chứng minh 360°, đoạn chết/GIF chưa render lại. Xem `exports/candidates/`; không dùng Vercel. Không tuyên bố hoàn thành.

**Vướng hình cần xử lý tiếp:** cả hai ảnh ụ hiện có vòng đế vẽ liền với bộ phận quay. Xoay nguyên ảnh sẽ quay đế, không đáp ứng chứng minh đế đứng yên; cần sinh lại bộ đế và đầu quay riêng (hoặc kiểm cách tách đã được phép), không được khai pivot đã đạt chỉ vì số tâm nhìn đúng.
