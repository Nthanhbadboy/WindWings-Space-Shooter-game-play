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

## Đính chính 23/10 (sau run `39935865412`)

Run `39935865412` là lần đầu **`session install` trên trial chạy được** (step 13 `success`,
`Validate key` skipped ⇒ vẫn trial, không có adb). Cùng ngày, user vào phiên bằng tay và
**vào được game**.

| Dữ kiện | Nguồn | Mức |
|---|---|---|
| `session install --apk … --timeout 600` trên trial: **thành công** | run `39935865412`, step 13 | A |
| Consent của game hiện trên màn hình: *"To use Wind Wings you must affirm that y…"* + `Continue` | `ui-after-dialog` (1466 B → 0 B sau khi tap) | A |
| Google Play Games đăng nhập bị huỷ, app vẫn tiếp tục | logcat `--filter package`: `I/Unity: SignInStatus:Canceled` @ 10:03:05 | A |
| App **bắt đầu nạp scene** | logcat: `I/Unity: Start Load Scene` @ 10:03:06, `<WaitLoading>d__22:MoveNext()` | A |
| **Vào được game** | user xác nhận trực tiếp trong phiên | A (lời user) |
| Vài lần crash trong phiên | **do user chỉnh tay**, không phải app tự chết | A (lời user) |

> Nhận định: chuỗi *"cài → launch → consent → `Start Load Scene` → vào game"* giờ đã có
> bằng chứng cho từng mốc, trừ mốc cuối là lời user chứ chưa phải ảnh do harness chụp.
>
> Nhận định: các lần crash trong phiên **không dùng được** làm bằng chứng app lỗi — chúng
> xảy ra sau thao tác tay. Mọi kết luận kiểu "app chết lúc load" rút ra từ phiên đó phải bỏ.

### Hai lỗi đo còn lại của harness (đã thấy trong chính run này)

1. `ramus snapshot` trả `{"message": "Cannot read properties of null (reading 'length')"}`
   đúng lúc cây UI đổi (consent → loading) ⇒ `ui-after-dialog` ghi **0 B** dù màn hình có nội dung.
2. `logcat` mặc định chỉ trả 500 dòng cuối của buffer **`system`**; dòng của game chỉ hiện khi
   lọc `--filter com.wind.wings.Space.Shooter`. Báo cáo vì thế từng in "no Unity line" trong khi
   Unity **đang** ghi log.

Cả hai đã sửa trong `.github/scripts/ramus-probe.mjs` (retry snapshot; logcat theo package;
pha `Load watch` chụp 3 khung trong lúc scene nạp) nhưng **chưa chạy lại** — xem mục dưới.

## Còn thiếu / phải đoán

- ~~Nguyên nhân chết trong lúc load~~ — **câu hỏi này sai tiền đề**: app không tự chết, user vào
  được game; các lần crash là do chỉnh tay (mục Đính chính ở trên).
- **Chưa có khung hình in-game do harness chụp.** `screen-02` là khung lúc *đang* load
  (`mean 41,6`), ba khung sau đó chưa được chụp vì pha `Load watch` mới thêm, chưa chạy lại.
- Chưa trả lời được: màn hình đầu tiên **sau** khi scene load xong trông thế nào, và mất bao
  nhiêu giây từ `Start Load Scene` tới frame đầu. Cần một run nữa (tốn 1 phiên trial).
- Emulator Ramus có thể dùng lớp chuyển đổi arm64→x86_64. **Chưa kiểm chứng**: cần
  `abilist` của thiết bị (chỉ key mode mới đọc được).
- Chưa xác định app "chết" hay "tự thoát": UI rời foreground giống nhau ở cả hai.
