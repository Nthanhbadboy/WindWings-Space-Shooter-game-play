# Nghiên cứu sprite động (để học, không phát hành lại)

Mục tiêu: tìm **một nhóm ảnh động** thật (nhiều khung của cùng một vật) để học cách
chia lớp và nhịp hoạt hình — không phải ảnh concept tĩnh.

## Bộ đã tìm được

**Pixel SHMUP Free** — kho sprite pixel art cho shmup nhìn từ trên xuống
(repo tham chiếu: `TheKing47JK/Protocol_Omega`, thư mục `sprites/Pixel SHMUP Free/`).

| Nhóm | Số khung | Kích thước | Ghi chú |
|---|---|---|---|
| `main_ship-1..15.png` | **15** | 48×58 | tàu người chơi: **5 tư thế nghiêng × 3 khung lửa đuôi** |
| `enemy_1_1..3.png` | 3 | 48×48 | địch: 3 khung (nhấp nháy/động cơ) |
| `Explosion/explosion-1..8.png` | 8 | ~48×48 | nổ 8 khung |
| `Explosion/Spritesheet/explosion-spritesheet.png` | — | — | bản ghép lưới của 8 khung trên |

Đo bằng numpy trên 15 khung tàu:

- khác biệt giữa 3 khung liền nhau ≈ **2.0** (chỉ đổi đuôi lửa),
- khác biệt khi sang tư thế kế tiếp ≈ **23–34** (đổi dáng thân),
- bbox phần “mực” đổi theo tư thế: `x 3→6`, `x max 44→41`, `y max 48→51→54`
  (khung lửa dài dần 3 px mỗi khung).

=> Một bộ 15 ảnh = **2 vòng lặp độc lập** ghép lại: dáng thân (5 nấc, chậm) ×
lửa đuôi (3 khung, nhanh).

> Bộ sprite này **chỉ dùng để tham khảo**. Giấy phép của gói không rõ ràng, nên
> không chép vào repo và không phát hành lại. Toàn bộ hình trong game vẫn do mình vẽ.

## Bài học áp dụng vào `shipdemo`

1. **Tách lớp theo nhịp.** Thân/cánh đổi chậm (gồng → bắn → hồi), lửa đuôi đổi nhanh
   15 hình/giây, chớp đầu nòng chỉ 3 hình. Không gộp tất cả vào một biến thời gian.
2. **Lửa đuôi đúng 3 hình**, hai ống lệch pha 1 khung → nhìn ra ngay là “đang nổ máy”.
3. **Cơ cấu thì chia nấc.** Giáp của tàu SINH CƠ mở theo **3 nấc** (`stepped()`), nghe
   như bản lề khoá, thay vì trượt đều kiểu cao su.
4. **Chớp đầu nòng 3 hình** (to → vừa → tắt) thay vì phóng to liên tục.
5. **Silhouette trước, chi tiết sau.** Viền tối dày + viền sáng một bên (ánh sáng từ
   trên trái) để tàu tách khỏi nền tối; chi tiết nhỏ (bu-lông, đai nòng) chỉ thêm sau.
6. **Laser phải có nguồn.** Mỗi tia bắn ra từ toạ độ **đầu nòng** do tàu tự khai báo
   (`muzzles()`), có bệ/tháp/nòng nhìn thấy được — không vẽ tia từ hư không.

## Bộ sprite động tham khảo khác (chưa dùng)

- Kenney — *Space Shooter Extension* (CC0): `spaceShooter2_spritesheet.png` + XML atlas,
  ~270 sprite tĩnh (tàu, đạn, hiệu ứng) — dùng để tham khảo bố cục atlas.
- *Space ship sprite sheet* (OpenGameArt, CC0): 26 tàu tĩnh 256×256 + 4 `sideship`.
- gvituri — *SpaceShooter Asset Pack* (itch.io): có 12 animation (booster, nổ, khiên).

Cách lấy lại nhanh (đều qua GitHub API, không cần trình duyệt):

```bash
gh api -H "Accept: application/vnd.github.raw" \
  "repos/TheKing47JK/Protocol_Omega/contents/sprites/Pixel%20SHMUP%20Free/main_ship-1.png" \
  > main_ship-1.png
```
