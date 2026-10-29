# Boss-37001 — bảng chất lượng / đang dở

Đối chiếu nguồn chính thức bằng `git show` commit `589a7de4a64f7891ef1f992f337b4b9cea92797b` từ nhánh `arena/020ecffe-windwings-space-shooter-game-p`: `03_BOSS_BOOK.md` §3.2, `04_COMBAT_FX_ART_ANIMATION.md` §4.3, `06_PRODUCTION_ROADMAP.md` Mốc A. Không sửa/cherry-pick tài liệu. Quy định mới của USER ưu tiên chất lượng; năng lực công cụ thực tế vẫn tối đa 10 ảnh mỗi turn, ảnh lỗi sinh lại turn sau. **ĐẠT chỉ khi xác thực toàn bộ tiêu chí liên quan; ứng viên chưa được coi là hoàn thành.** Số sinh lại dưới đây tính lần thử thay thế trong lịch sử bộ ảnh này, không tính hậu kỳ.

| Món | ĐẠT / CHƯA | Lỗi/thiếu cụ thể đang thấy | Số lần sinh lại |
|---|---|---|---:|
| Thân trần | CHƯA | Master `round4/01-hull.png` đã đóng ổ giữa; chưa chứng minh tách alpha/halo và thân không pháo ma ở cỡ game; kiểm trên sáng/tối | 2 |
| Ụ pháo trái | CHƯA | Layer có, pivot còn số ước lượng; chưa có GIF xoay 360° và chưa chứng minh đế đứng yên, halo | 0 |
| Ụ pháo phải | CHƯA | Layer có, pivot còn ước lượng; chưa GIF xoay 360° và kiểm lắp | 1 |
| Pháo giữa | CHƯA | Có nguồn và layer; chưa kiểm sạch alpha, điểm gắn và quay; chưa có chứng minh pivot | 2 |
| Pod trái | CHƯA | Nguồn và layer có; chưa duyệt mép/halo khi lắp | 2 |
| Pod phải | CHƯA | Sinh lại theo pod trái; chưa kiểm pixel/alpha/halo và mép ghép | 1 |
| Lõi teal | CHƯA | Có layer core, chưa chứng minh tâm và độ đọc ở kích thước game | 0 |
| Overlay hư hại bậc 2 | CHƯA | A1 vẽ lại boss, sai. A2 `01-damage-level2.png` là họa tiết độc lập, **RGB nền đen**; nét nứt/ám khói rất tối hòa nền, chưa có alpha, chưa khớp 512² từng pixel | 1 |
| Overlay hư hại bậc 3 | CHƯA | A1 vẽ lại boss, sai. A2 `02-damage-level3.png` là họa tiết lửa/khói rời **RGB nền đen**; chưa tách alpha, đặt/kiểm khớp thân 512² và halo | 1 |
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

## Turn hiện tại

Đã sinh lại **hai ảnh nguồn** A2. Xem mắt: cả hai không vẽ cả con boss như A1; tuy nhiên nền thực tế là RGB chứ không phải alpha thật, đặc biệt vết tối ở #01 khó phân biệt nền đen. Chúng chỉ là ứng viên, **không đạt** cho đến khi tách và chứng minh ghép đúng vị trí/halo. Không cắt ảnh A1 để bù. SHA-256:

- `masters/A2/01-damage-level2.png`: `d603099b2630cfd5b20db76baae2ca1f5eed897fb98a0b53ba09435c91f6bd07`
- `masters/A2/02-damage-level3.png`: `485f3952425b758a5b45851f74ac577596d46adfb59771969582e92fd4a84c24`

Turn này dừng ở **hai ứng viên overlay chưa tách alpha/đăng ký canvas**. Chưa đo pivot, chưa render GIF mới hoặc khẳng định tài liệu hoàn tất. Theo phân kỳ đã giao trước đó, phần hậu kỳ/kiểm xoay/ghép là turn riêng sau A2; ưu tiên kiểm overlay trước, nếu không đạt phải sinh lại ở turn sau.
