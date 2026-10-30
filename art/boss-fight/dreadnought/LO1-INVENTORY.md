# DREADNOUGHT-GEN — Lô 1: TẠM DỪNG / CHỜ CHỈ ĐẠO

**Nguồn thiết kế đã đọc từ remote:** `2e9b0fc` — `docs/design/03_BOSS_BOOK.md` §3.2A, §3.5; `04_COMBAT_FX_ART_ANIMATION.md` §4.3; `06_PRODUCTION_ROADMAP.md` §6.4.1–6.4.2. Hồ sơ cũ tham chiếu commit `fd4f65a` thuộc branch art chính `arena/215aa58f-windwings-space-shooter-game-p`; không sao chép ảnh cũ vào bộ ảnh mới.

## Giao được: 1/10 ảnh mới

| # | Món | File | Kích thước | Trạng thái |
|---|---|---|---|---|
| 1 | Thân trần sạch, hướng xuống, ổ gắn pháo/ụ phụ/pháo quạt, giếng lõi trống | [`01-hull-clean.png`](01-hull-clean.png) | **512×512 RGBA**, khung alpha 498×505 tại (7,3) | Mới sinh, hậu kỳ bỏ nền caro giả, xem sheet để kiểm alpha trên nền tối/sáng. **Ứng viên hình ảnh, chưa duyệt fit với linh kiện cũ.** |
| 2 | Thân hư hại nhẹ | — | — | Hai yêu cầu liên tiếp bị **403 PERMISSION_DENIED**, không có ảnh. |
| 3–4 | Thân hư hại vừa / nặng | — | — | Chưa sinh. |
| 5–6 | Đầu quay hai nòng / đế tĩnh ụ phụ | — | — | Chưa sinh. |
| 7–8 | Đầu cố định / đế pháo quạt sát lõi | — | — | Chưa sinh. |
| 9 | Vòng giáp lõi MỞ | — | — | Chưa sinh. |
| 10 | Đế BigGun ĐÃ PHÁ | — | — | Chưa sinh. |

**Sheet:** [`LO1-partial-sheet.png`](LO1-partial-sheet.png), 1112×660; cùng **một** thân 512×512 trên nền tối và nền sáng để kiểm tách nền. Hai hình trên sheet không phải hai asset khác nhau, không thay thế các món chưa sinh.

**Kiểm chất lượng sơ bộ:** đường bao rộng và liền mạch, nhiều ổ gắn trống, hình thép xanh-đen + teal đọc được ở 512; ảnh sinh ban đầu là RGB với nền caro *dính vào pixel*, đã hậu kỳ tách nền và thu về 512 RGBA. Tâm ổ/giếng thực tế phải được art chính đo lại khi lắp (tọa độ trong §3.2A chỉ là vùng thiết kế). Chưa có kiểm tra fit hoặc pivot chính thức, không đánh dấu ĐẠT hoàn chỉnh.

## Dự định tái dùng — từ hồ sơ CŨ (chỉ ứng viên, không tính ảnh mới)

| Hạng mục | Nguồn ở commit `fd4f65a`, dưới `art/boss-fight/` | Kích thước gốc | Điều kiện |
|---|---|---:|---|
| Hai BigGun, đế + đầu quay riêng | `exports/turret-pivot-tests/{left,right}-{base,head}.png` | 512×512 từng layer | Kiểm fit lên ổ lớn của thân mới trước khi tái dùng. |
| Main Cannon / tia | `exports/boss-layers/cannon.png`; họ beam trong `exports/bullet-B2/` | cannon 512×512 | Kiểm điểm họng và khe ghép. |
| Hai pod tên lửa | `exports/boss-layers/pod_left.png`, `pod_right.png` | 512×512 từng layer | Kiểm ổ hông và kích cỡ 8 ống/pod. |
| Lõi | `exports/boss-layers/core.png` | 512×512 | Kiểm giếng lõi và trạng thái vòng giáp mở mới. |
| Bộ đạn hiện có, không sinh lại | `exports/bullet-B2/` (laser, beam, heavy-orb, missile, panic...) | Ví dụ laser 64×128 | Chỉ tái dùng khi đọc được ở cỡ thật. |

**Không tái dùng như ảnh mới:** thân cũ 3 bậc, đế/đầu BigGun cũ, pháo chính, pod cũ, lõi cũ, bộ đạn cũ. Chưa sinh món nào của Lô 2; chưa dựng GIF hay cài code.

## Sự cố dịch vụ sinh ảnh

- **2026-10-30 ~18:28 UTC:** ảnh #2 bị trả 403 ở yêu cầu đầu, đã dừng ngay và không gọi thêm trong turn đó.
- **2026-10-30 ~18:29 UTC:** USER yêu cầu “thử tạo lại” ở turn kế, thử **đúng 1 lần** ảnh #2; cùng lỗi 403, đã dừng, không sinh tiếp.
- Nguyên văn mã lỗi từ dịch vụ: `403 Forbidden`, `code: 403`, `status: PERMISSION_DENIED`; thông báo: `Request rejected due to terms of use violation. Your account has been flagged for suspicious activity. Please check the email associated with your account for more details.` Đây **không phải** `Image generation limit of 10 reached for this turn`.

**DREADNOUGHT-GEN LÔ 1 — CHỜ DUYỆT / CHỜ CHỈ ĐẠO VỀ 403.**
