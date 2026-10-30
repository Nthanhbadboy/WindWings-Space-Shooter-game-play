# SỰ CỐ 403 — session art-gen DREADNOUGHT (Lô 1)

- **Session**: art-gen, branch `arena/227ffc0a-windwings-space-shooter-game-p`
- **Thời điểm (UTC)**: `2026-10-30T18:49:17Z`
- **Endpoint**: `google-genai` / model `gemini-3.1-flash-image`
- **Số lần gọi bị lỗi**: **1** — lần gọi sinh ảnh **thứ hai** của Lô 1
  (`02-hull-damage-light`, biến thể hư hại nhẹ của thân Dreadnought).
- **Số lần thử lại**: **0**. Theo `04_COMBAT_FX_ART_ANIMATION.md` §4.3 mục (b):
  gặp 403 thì dừng ngay, cấm thử lại dưới mọi hình thức.

## Nguyên văn mã lỗi (không sửa)

```
Failed to generate image: Error during image generation with google-genai for model
endpoint gemini-3.1-flash-image: Failed to fetch image: 403 Forbidden - [{
  "error": {
    "code": 403,
    "message": "Request rejected due to terms of use violation. Your account has been flagged for suspicious activity. Please check the email associated with your account for more details.",
    "status": "PERMISSION_DENIED"
  }
}]
```

## Phân loại

| | |
|---|---|
| Có phải hết quota 10 ảnh/turn? | **Không.** Thông báo quota là `Image generation limit of 10 reached for this turn`; ở đây là `403 PERMISSION_DENIED`. |
| Bản chất | **Chặn ở cấp tài khoản dịch vụ**, đúng mẫu sự cố đã ghi ngày 30/10 (session `215aa58f` và `93c8b06c`). |
| Khác gì sự cố trước | Lần này là **yêu cầu đích danh của USER** cho Lô 1, đúng quy định "chỉ thử 1 yêu cầu"; vẫn 403 ⇒ cờ **chưa được gỡ**. |

## Đã làm sau khi dừng (việc không cần generate)

1. Tách nền + xuất canvas 512 cho món 01 đã sinh (không mất ảnh đã có).
2. Sửa 2 lỗi kỹ thuật của bộ tách nền: (a) thu nhỏ trong không gian
   **premultiplied** để không sinh quang sáng kiểu Lanczos ringing; (b) ramp
   alpha theo luminance ở dải sát nền để mép mềm, không răng cưa.
3. Kiểm halo trên nền sáng + nền tối và **đo** thay vì nhìn mắt:
   pixel nền sát hình đúng màu nền (max channel 230/232/236, 0 px > 240);
   viền alpha 20–200 có luminance TB 32,9, thấp hơn thân (58,4) ⇒ không halo.
4. Đo toạ độ 11 điểm hỏa lực trên file thật, ghi vào `manifest.json`.
5. Dựng `review/LO1-sheet.png` + bảng kê + manifest có sha256.

## Đang chặn

9 món còn lại của Lô 1 (02–10). **Không** món nào được thay bằng ảnh cũ, không
món nào được đánh dấu "đã sinh".

## Cần USER

Gỡ cờ tài khoản dịch vụ sinh ảnh (theo §4.3: không có thời hạn công bố; session
không tự gỡ được, không tạo session mới để lách). Khi có lệnh, session sẽ sinh
lại **từ món 02**, mỗi lần **đúng 1 yêu cầu**, dừng ngay nếu còn 403.
