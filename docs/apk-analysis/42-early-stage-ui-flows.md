# 42 — UI khi người chơi mới qua stage 1–3 (PROVISIONAL)

## Kết luận hiện tại

**Chưa đủ bằng chứng để chốt toàn bộ luồng UI stage 1–3 theo APK.** Có layout của
các board cốt lõi và khai báo tutorial riêng cho stage đầu; chưa resolve điều
kiện/flag và thứ tự popup. Không lấy “125 class UI” làm “125 màn/luồng đã đủ”.
Không dùng ảnh điện thoại hoặc runtime build Premium-mod để lấp phần này.

Nguồn kiểm trực tiếp: `reverse-engineering/il2cpp/dump.cs.gz`,
`reverse-engineering/raw/ui/*.json.gz`. Raw audit tái lập bằng
`python3 tools/verify/early_ui_flows.py` → `raw/ui-audit/early-stage-coverage.json.gz`.
Khai báo dump chứng minh API/field tồn tại, **không chứng minh method body**.

## 1. Phần đã có để dựng giao diện

Các class sau đều có layout export trong tập hiện có:
`Board_Home`, `Board_Maps`, `Board_Stage`, `Board_Endgame`, `Board_Players`,
`Board_Drones`, `Board_Pause`, `Board_Reborn`, `Board_Reborn_IAP`.
Nhiều file cùng class qua nhiều lần export không phải nhiều màn khác nhau.
Root ID kiểu số rất lớn trong tên file layout cũ không được dùng làm Unity PPtr.

| Đoạn luồng cần kiểm | Bằng chứng declaration/layout | Cái chưa chốt |
|---|---|---|
| Home → Map/chọn stage | Home/Maps có layout; Maps có OnClickStageButton, InitStages | Người mới đi qua Home hay vào trận thẳng; stage đầu mở mặc định; điều kiện khóa |
| Chọn stage → chuẩn bị → Play | Stage có btnPlay/btnUpgrade, popupFollowTut, popupNoEnergy; OnPressedButtonPlay | Tutorial nào chen vào, có bắt nâng cấp không, kiểm energy và ưu tiên popup |
| Trong trận | GP_Tutorials có tutobjControl/ChangePlane/UseDroneSkill/TouchSkill, coverObject, btnPause | Trigger stage nào/wave nào; thứ tự chặn input, pause/time scale, hoàn tất và skip |
| Victory/Defeat → kết quả | Endgame có allVictoryObjects/allDefeatObjects, btnBack/Replay/Continue, SetupTut | Hiện nút nào ở clear đầu; thưởng lưu khi nào; popup nào trước/sau tutorial |
| Kết quả → trận tiếp theo | OnPressedButtonContinue/Continue | Vào thẳng trận hay mở Stage; stage index cập nhật và off-by-one |
| Kết quả → Map/Home | OnPressedButtonBackToMap/BackToMap/LoadSceneHome | Có ghé Home; cập nhật sao/lock; queue unlock/gift/offer/rating |
| Sau trận → nâng cấp | Endgame có OnPressedButtonGoToUpgradePlayer/Drone/Tech; Home.CheckTutorialFocus | Bắt buộc hay tùy chọn; lần đầu ở stage mấy; lưu flag và quay lại đâu |
| Thua/Pause/Revive/Replay | Có layout Pause/Reborn/Reborn_IAP và Endgame.Restart | Tutorial khi retry; popup ưu tiên; hồi sinh/hủy có trả đúng trạng thái |

Bảng này là **checklist audit**, không phải graph runtime đã xác nhận. Tên method
không tự chứng minh cạnh điều hướng. Đặc biệt không tự gọi Continue là “next stage”
trước khi đọc consumer body.

## 2. Có bằng chứng riêng cho tutorial stage đầu, nhưng chưa được phép gán nội dung

`DataTutorials` TypeDefIndex 254 khai báo:

| API | RVA | Trạng thái |
|---|---|---|
| get_hasTutStage1 | 0x1327E90 | Chưa giải điều kiện |
| get_hasTutStage2 | 0x1327F08 | Chưa giải điều kiện |
| get_hasTutStage3 | 0x1327F8C | Chưa giải điều kiện |
| get_hasTutStage4 | 0x1328008 | Chưa giải điều kiện |

Không tự hiểu `hasTutStageN` là “đã hoàn tất” hay “cần chạy”: cần body getter.
Không đồng nhất stage hiển thị 1 với index lưu 0 trước khi đọc phép chuyển đổi.

`GP_Tutorials` (namespace SpaceShooter.Gameplay) có `IndexTutorial`,
`CheckRunTutorialNew`, `GameStarted`, `TutMoveFingers`, `TutTransform`,
`TutDrones`, `TutTalents`, `TutChangeGameSpeed`, `TutChangeGameSpeedBoss`,
`TutLaserSkill`. Đây là danh sách khả năng tutorial, **chưa có ánh xạ stage → tutorial**.
Nó còn có coroutine/callback generated: chỉ export wrapper IEnumerator sẽ thiếu
logic MoveNext. `SkipTutorial` và các flag persistent cũng phải được xét.

## 3. Những đường phát sinh dễ bị bỏ sót

- `Board_Endgame.SetupTut`, `CheckPremiumPopup`: không chỉ board kết quả tĩnh.
- `Board_Home.CheckTutorialFocus`, `CheckAutoPopup`, `CheckFocusTechLab`,
  IsNewUser, CountVisitHome, IsUnlockArena/IsUnlockPVP: tiến trình và popup có state.
- `Board_Maps.CheckPopupUnlock` có nhiều callback generated; không có nghĩa chúng
  đều mở trong stage 1–3. Phải đọc điều kiện trước.
- `Board_Stage.CheckTutStartItemToPlay` là coroutine, có `popupFollowTut`.
- Rating, premium/offer, login gift có thể phụ thuộc phiên/ngày/network, không chỉ
  stage. Chưa chứng minh xuất hiện ở ba stage đầu nên không thêm vào happy path.

## 4. Đào tiếp — đã yêu cầu export, chưa nhận kết quả tại thời điểm lập báo cáo

Commit `921dc909b` mở rộng native export DataTutorials, GP_Tutorials,
Board_Home/Maps/Stage/Endgame/Players/Drones, BoardManager, SkipTutorial,
Tut_Settings/Tut_Settings1; kèm nested coroutine bodies của các họ controller
UI đầu game. Mở rộng serialized typetree cho các component tương ứng.
Actions **40176643619** đã chạy; số liệu raw mới cần kiểm sau khi job hoàn tất.
Không dùng việc đã push cấu hình làm bằng chứng đã bóc xong gate.

Ưu tiên đọc: DataTutorials getters → GP_Tutorials.CheckRunTutorialNew/MoveNext →
Endgame.SetupTut/Continue/BackToMap → Home.CheckTutorialFocus/CheckAutoPopup →
Maps.CheckPopupUnlock → Stage.CheckTutStartItemToPlay. Resolve call target và
saved-key read/write; tránh suy theo tên method.

## 5. Tiêu chí đủ UI cho phạm vi này

Cần bảng riêng cho stage hiển thị 1, 2, 3, mỗi stage có:
1. Precondition: fresh install/first clear/replay, mode, saved flags.
2. Màn trước trận, tutorial bắt buộc, target/button input, điều kiện hoàn tất.
3. Victory → reward/save → tutorial/queue popup → destination chính xác.
4. Defeat/retry/revive/back và app restart: không skip nhầm/khóa input vĩnh viễn.
5. Mỗi cạnh có prefab/serialized callback hoặc RVA/asm branch chứng minh;
   phần chưa có bằng chứng ghi UNKNOWN.

Hiện **chưa chốt đủ cả ba stage**. Có thể dựng khung UI, chưa gọi đó là bản sao
đúng onboarding/first-clear flow của APK.

## 6. Kết quả inventory local vòng này

Quét 54.049 file layout hiện có (bao gồm nhiều lần export): các board lõi ở §1
đều có file. Nhưng **không có node component GP_Tutorials** trong tập layout này;
Tut_Settings cũng không thấy; Tut_Settings1 có trong 73 file, SkipTutorial trong
71 file. Đây là **phạm vi layout Board_/Popup_/Tab_**, không phải toàn scene:
`tools/apk-analyze/ui_layout.py` hiện chỉ chọn các root tiền tố đó. Vì vậy còn một
lỗ hổng export cụ thể: tutorial/HUD trong gameplay không được đảm bảo đi qua cùng
pipeline UI. Không được đọc kết quả 0 thành “game không có tutorial”.

Hash node list khác nhau giữa các export cũng không chứng minh layout khác thật:
export có thể thay metadata/sprite ID, node fields. Raw giữ source file/hash để
truy ngược, không báo số hash là số màn.

## Cập nhật tiếp — native đã về

Actions 40176643619 đã success, raw tại daa2c3a03. Xem **report 43** cho gate
hasTutStage1/2/3, nhánh Endgame ẩn ba nút và kết luận đủ/thiếu để vẽ. Các câu
“chưa nhận raw/đang chạy” phía trên chỉ mô tả snapshot lúc viết report 42.
