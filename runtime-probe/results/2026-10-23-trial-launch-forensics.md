# Điều tra khởi động trên Ramus trial — 23/10/2026

Chuỗi 7 phiên trial, mỗi phiên trả lời đúng một câu. Kết quả **đảo ngược** kết luận
trước đó ("app không khởi động").

## TL;DR

| Câu hỏi | Trả lời | Mức |
|---|---|---|
| APK có cài được không? | **Có** | A — session `active`, không có lỗi cài |
| XAPK 117 MB có vượt hạn mức không? | **Không** — 117.158.131 B < 150 MB | A — in trong report mỗi lượt |
| App có khởi động không? | **Có** — activity Unity ở foreground, vào chế độ full-screen | A |
| Có tới được menu game không? | **Không** — chết trong lúc load, sau hộp thoại đồng ý | A |
| Vì sao chết? | **Chưa biết** — trial không trả buffer `main`/`crash` | chưa có |

Giả thuyết **"arm64-only nên không chạy được trên emulator x86_64"**: **bị bác bỏ ở mức
khởi động** — app đã chạy. Nó vẫn có thể là nguyên nhân của lần chết sau đó (một plugin
`.so` chỉ có arm64 nạp muộn), nhưng hiện **không có dòng log nào** chứng minh.

## Chuỗi bằng chứng

| Run | Thời điểm | Quan sát | Kết luận rút ra |
|---|---|---|---|
| `39925095796` | 08:31Z | logcat chỉ `system=500`, 0 dòng chứa package | "app không khởi động" — **SAI**, xem dưới |
| `39930193786` | 09:00Z | ảnh 29.756 B → 57.212 B, hash khác | màn hình **có** nội dung và **có** đổi |
| `39930806984` | 09:12Z | 3 ảnh trùng hash; UI: `com.android.systemui` + "Viewing full screen" / "Got it" | hộp thoại immersive của Android đang che app |
| `39931868778` | 09:26Z | bấm "Got it" (toạ độ chuẩn hoá từ `bounds`) → UI đổi sang `com.Wind.wings.Space.Shooter`, text "To use Wind Wings you must affirm…" + "Continue"; logcat: `D/VRI[MessagingUnityPlayerActivity]` | **app đang chạy** |
| `39932494059` | 09:33Z | bấm "Continue" 3 lần → UI thành `com.google.android.apps.nexuslauncher` | app rời foreground |
| `39933117377` | 09:41Z | từng bước: tap 0 → app **còn** ở trước (ảnh `mean 51.9`, 126 màu = màn hình load tối); tap 1 → app **mất** | chết trong lúc load |

## Hai lỗi trong chính harness đã che mất sự thật

1. **`snapshot --raw` trả JSON bọc XML** (`{"gen":5,"raw":"<hierarchy …>"}`). Regex
   `package="…"` chạy trên chuỗi JSON đã escape nên **không khớp gì** ⇒ mọi report cũ ghi
   "packages: —". Đã sửa bằng `unwrapXml()`.
2. **`tap <ref>` cần `--gen` khớp**; generation đổi giữa lúc snapshot và lúc bấm ⇒
   "found Got it but tap failed". Đã chuyển sang `tap <x,y>` chuẩn hoá, lấy từ `bounds`
   trong XML, kèm `--expect-gone` để CLI xác nhận.

Hệ quả: kết luận "app không khởi động" ở các vòng trước là **lỗi đo**, không phải lỗi game.

## Cái còn thiếu để trả lời "vì sao chết"

Trial chỉ trả **stream `system`**; crash của app ghi vào `main`/`crash`. Cần **key mode**
(`RAMUS_API_KEY` + adb). Bước adb trong workflow đã được sửa để tự thu:

- `getprop ro.product.cpu.abilist` / `ro.product.cpu.abi`
- `logcat -b main -b crash -d` hai lần (ngay sau tunnel và sau khi probe xong)
- `dumpsys activity activities`
- `monkey -p com.Wind.wings.Space.Shooter -c android.intent.category.LAUNCHER 1`

## Còn thiếu / phải đoán

- Nguyên nhân chết trong lúc load: **chưa có log**. Ứng viên, chưa cái nào được chứng minh:
  - plugin native chỉ build cho arm64 nạp muộn (Unity core đã load được);
  - hết bộ nhớ khi nạp asset;
  - bước xác nhận consent gọi mạng rồi thoát.
- Emulator Ramus có thể dùng lớp chuyển đổi arm64→x86_64. **Chưa kiểm chứng**: cần
  `abilist` của thiết bị (chỉ key mode mới đọc được).
- Chưa xác định app "chết" hay "tự thoát": UI rời foreground giống nhau ở cả hai.
