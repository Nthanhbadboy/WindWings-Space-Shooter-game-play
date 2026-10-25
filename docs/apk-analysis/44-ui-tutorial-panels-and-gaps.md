# 44 — Đào tiếp UI: tutorial panel, style và nhánh Endgame (PROVISIONAL)

Nguồn đã nhận: bot **c570485c5**, Analyze **40177270586 success**.
Không dùng screenshot/build điện thoại. Raw mới: `ui-audit/visual-coverage.json`,
`ui-audit/tutorial-texts.csv`, `ui-audit/early-native-gates.json`.

## 1. Lỗ hổng tutorial layout đã lấy được

`GP_Tutorials__1902.json.gz`: subtree 126 node và 8 field panel resolve local.
8 reference nhưng **7 GO khác nhau**: tutSettings/tutSettings2 cùng GO634.
Không được vẽ thành hai modal khác nhau chỉ vì hai field.

| Field → GO | Node trong subtree | Chữ Việt lấy theo key |
|---|---:|---|
| tutobjControl →1909 | 3 | Di chuyển ngón tay của bạn để điều khiển máy bay |
| tutobjChangePlane →1904 | 6 | Thả ngón tay của bạn để đổi máy bay và kích hoạt pháo đặc biệt ngay bây giờ |
| tutobjChangePlane2 →329 | 9 | Hãy thay đổi máy bay một cách linh hoạt; Không thể tiêu diệt; Tiêu diệt dễ dàng |
| tutobjUseDroneSkill →1906 | 2 | Kỹ năng máy bay phụ phá giáp kẻ địch và gây sát thương lớn. |
| tutobjTouchSkill →1911 | 6 | Chạm hai ngón tay trên màn hình để sử dụng kỹ năng đặc biệt (tài năng) |
| coverObject →1908 | 1 | Không có text |
| tutSettings/tutSettings2 →634 | 30 | Hãy đổi tốc độ chơi khi tạm dừng. Tốc độ chậm giúp bạn dễ chơi hơn; Nhạc nền; Âm thanh; Tốc độ chơi; Đồng ý |

**Đủ để bắt đầu vẽ các panel này từ prefab**, không còn thiếu toàn bộ tutorial
layout như snapshot report 42. Không đồng nghĩa đã mô phỏng đúng input/focus,
chờ coroutine hoặc thứ tự sau clear stage.

CSV giữ từng text node, original text, localization key, tiếng Việt, font size,
font PPtr, local_pos/size_delta. Chữ trong prefab tiếng Anh và bản dịch Việt có
thể khác nội dung (đặc biệt drone); không tự sửa để cho giống nhau.

## 2. Style đã có — phân biệt reference với resolve

Tất cả TMP component và SpriteRenderer **trong các subtree được kiểm** đã giữ
font PPtr/cỡ chữ và sprite PPtr/sorting order. Ví dụ GP_Tutorials có 25 TMP/53
SpriteRenderer, Home 27 TMP/97 SpriteRenderer, Stage 173 TMP/469 SpriteRenderer,
Endgame 167 TMP/499 SpriteRenderer. Đây là số component trong subtree có cả
inactive/template; không phải số phần tử hiện đồng thời.

Ví dụ text hướng dẫn control: size6, font PPtr(file3,path105), material(file3,path10),
wordWrapping=true, màu trắng. **Size6 là đơn vị serialize TMP, không phải 6 pixel.**
Các trường alignment/style numeric giữ nguyên, không đoán enum.

Phần còn thiếu: resolve đúng external file3 → asset font/material, sprite
rect/pivot/PPU và camera gắn với board. Không dùng path105 để tra local file0.
Đã mở exporter render-context (a2fac1df7): Camera, TMP_FontAsset, metadata Font,
Material, Sprite geometry và bảng external file IDs của từng serialized file.
Không xuất binary font/image vào Git.

## 3. Nhánh sau SetupTut đã tìm được callback thật

Report 43: SetupTut ẩn Back/Replay/Continue khi IndexTutorial<=1.
Giờ đã tìm `Board_Endgame.<CheckPremiumPopup>g__ThroughTut|91_2`, RVA **0x126d3cc**.
Exporter đang đặt header ngắn `_2` do ký tự `|` trong tên generated; raw vẫn giữ
signature đầy đủ nên không nhầm với hàm tên `_2` khác.

- CheckPremiumPopup chỉ đi phần tutorial khi IndexTutorial<=1; có các nhánh
  popup premium trước fallback tail-call 0x126d3cc. Không được chèn premium vào
  mọi lần clear: còn điều kiện entitlement/flag.
- Tại callback, nhánh bool true đọc static slot0x2adc6b0,+0: ẩn Replay(+0x80),
  bật Continue(+0x88), đặt focus về Continue, gọi get_IndexTutorial → **+1** →
  set_IndexTutorial @0x14f9f84.
- Nhánh bool false có xử lý Replay theo mode và focus; không chạy increment ở
  block true nói trên. **Chưa resolve metadata slot bool thành tên field bằng
  registration map**, nên không nâng tên nhánh thành “victory” chỉ theo ý nghĩa.
- Không thấy callback này bật Back trong block trên: không vẽ cả ba nút đều bật.
- Còn phải trace lúc nào CheckPremiumPopup được gọi sau reward, callback premium,
  Continue destination và persistence/quit/retry trước khi đóng luồng runtime.

Raw giữ đầy đủ excerpt CheckPremiumPopup, callback `_2`, các callback b__91_0/1,
SHA256 và 6 instruction checks; không chỉ giữ lời diễn giải.

## 4. Lỗ hổng mới: Map bị cắt đúng 6.000 node

Index c570485c5 ghi Board_Maps__60426 có **6.000 node**, bằng MAX_NODES cũ.
Không được báo “Map đầy đủ” từ dump này. Đã tăng budget lên 12.000 và ghi rõ
walk_diagnostics: pending_transforms, child_limit_skipped, truncated. Nếu vẫn
truncated thì tiếp tục lấy, không giấu việc cắt. Test có case cây bị cắt/cây đủ.
Không coi số lượng node biến động giữa exporter cũ/mới là game đổi phiên bản.

## 5. Còn đào gì / mức đủ để vẽ

| Việc | Trạng thái |
|---|---|
| Bộ board tĩnh và tutorial panel | Có raw để vẽ reference |
| Text Việt, TMP size/style và sprite sorting | Đã giữ trong raw mới |
| Font/material external binding + sprite PPU/pivot + camera context | Đã thêm exporter; CHƯA nghiệm thu output lượt mới |
| Map hết cây và báo truncation | Đã sửa exporter; CHƯA nghiệm thu output lượt mới |
| Queue popup, finish/skip, Continue/replay/quit persistence stage đầu | OPEN, không tự ghép theo tên hàm |
| Pixel-accurate runtime theo tỉ lệ màn hình | OPEN; không gán 100px/unit toàn game |

Lượt export tiếp do commit 1989defc2 kích hoạt; trạng thái job phải kiểm riêng.
**Bắt đầu vẽ được nhiều hơn report43: gồm cả tutorial panel. Chưa gọi toàn bộ
luồng 1–3 hoặc mọi trạng thái UI đã đủ.** Các task còn OPEN là đầu việc cụ thể,
không phải yêu cầu designer bịa phần thiếu.
