# 64 — Stage 1/2/3: chặn tutorial riêng, khuôn victory chung

**Tạm kết từ raw APK, kiểm chứng tĩnh, không phải replay.** Phạm vi: campaign thường (`GameMode=0`, nonbranch, nhánh `LevelCurrent=0`); không suy rộng mọi mode thành cùng luật.

## Kết luận

Nhận định của user đúng trong phạm vi này: **ba stage mở đầu khác nhau ở tutorial, không phải ba hệ thống stage-victory riêng.** Chúng đi vào cùng luồng xác định kết quả, snapshot, `Board_Endgame`, tính mission/sao và lưu kết quả. Tutorial vẫn thay đổi một số nút/điều hướng trong chính board đó; “chung khuôn” không đồng nghĩa giao diện và Continue giống hệt mọi thời điểm.

Không cần chứng minh lịch sử pool BB hay dựng một playthrough ít kill để kết luận cấu trúc này.

## 1. Ba chặn mở đầu, đọc lại DataTutorials và GP_Tutorials

Stage hiển thị 1/2/3 tương ứng index 0/1/2.

| Stage | Predicate riêng trong raw | Tutorial tương ứng |
|---|---|---|
| 1 | `stageIndex == 0 && IndexTutorial == 0` (`1327e90`) | `TutMoveFingers`, `TutTransform`; lời gọi đầu có delay 9s |
| 2 | `stageIndex == 1 && IndexTutorial == 1` (`1327f08`) | `TutDrones`, thao tác drone và pause/resume tutorial |
| 3 | `stageIndex == 2 && !IsTutTouchSkillDone()` (`1327f8c`) | Nhánh talent/touch skill; có kiểm tra talent và flag hoàn tất riêng |

**Stage 3 không có điều kiện `IndexTutorial == 2` trong predicate.** Cũng không nên gọi đây là tutorial bắt buộc xuất hiện mỗi lần chơi lại: stage 1/2 phụ thuộc tiến độ tutorial, stage 3 phụ thuộc flag touch skill. `CheckRunTutorialNew` còn xét nhánh trước đó và điều kiện thiết bị/talent; bảng là gate stage, không thay thế toàn bộ dispatcher.

## 2. Khuôn endgame/victory dùng chung

Các mốc native đã đọc lại, giữ nguyên thân method trong raw kèm report:

1. Callback `GP_Manager.<Start>b__11_7` → `GP_Endgame.StartCheckEndgame` (`14f6188 → 14f052c`).
2. Coroutine `_CheckEndgame_d__4.MoveNext`: gate hoàn tất địch/wave và trạng thái Playing; **không phải cứ đủ kill giữa wave là tự kết thúc màn**. Nhánh campaign thường lấy kill/count rồi gọi **cùng** `Board_Endgame.GetMissionCompleted` (`14f1850 → 12734f8`).
3. Coroutine kiểm tra health; health bằng 0 ghi kết quả false (`14f18e8..14f18fc`). Số địch diệt không được ghi đè player đã chết thành victory.
4. `MoveOutPlayer` (`14f170c → 14f0768`) và callback `<CheckEndgame>b__0` mang bool kết quả vào **một** `OpenBoardVictory` (`14f13c4 → 14f0830`). Tên OpenBoardVictory không có nghĩa lời gọi nào cũng thắng: nó nhận cả bool false.
5. `OpenBoardVictory` chụp kết quả và chỉ số trận: bool tại `14f09e4`, kill tại `14f0b20`, count tại `14f0b38`, stage tại `14f0b50`. Stage ở đây là dữ liệu của kết quả chung, không phải selector sang một board victory dành riêng stage 1/2/3.
6. Cùng `Board_Endgame.Init` gọi `SetMissions` (`126c538 → 1272714`). Nhánh normal tiếp tục dùng chung mission/sao/save đã bóc ở report 57. Không có predicate tutorial stage 1/2/3 hay `get_IndexTutorial` được gọi trực tiếp trong ba thân core đã kiểm: coroutine, OpenBoardVictory, GetMissionCompleted.

Các hệ số sao và lượng kill yêu cầu là dữ liệu/nhánh mode; **cùng khuôn không có nghĩa cùng số địch hay cùng phần thưởng ở mọi stage**. Không biến kết quả không đạt yêu cầu thành thắng chỉ vì đã qua tutorial.

Có entry `VictoryNow` ép true, nhưng callback này **cũng vào cùng OpenBoardVictory** (`14f1318..14f131c`), không phải một board victory riêng. Không dùng entry này để khẳng định mọi nguồn victory đều phải chạy phép tính kill trước.

## 3. Khác biệt tutorial nằm bên trong board chung

- `Board_Endgame.SetupTut` (`126cac4`): đọc IndexTutorial tại `126cb0c`, so với 1. `>1` đặt trạng thái cho qua; `<=1` chưa cho qua và tắt các object UI tại field `0x88/0x80/0x78`.
- Generated helper `_2` (`<CheckPremiumPopup>g__ThroughTut|91_2`, `126d3cc`) thao tác UI rồi tăng IndexTutorial (`126d534..126d540`). Đọc phần ThroughTut để phân lớp tutorial, không mở rộng kết luận về Premium.
- `Continue` còn guard mode, victory và tiến độ tutorial. Đoạn `126f220..126f298` cho victory với IndexTutorial <=2 đi nhánh loading, trường hợp khác về home; không được bỏ các guard trước đó để gọi đây là routing vô điều kiện cho cả ba stage.

Vì vậy mô hình đúng cho reconstruction là:

```text
scenario stage + gate tutorial riêng
                  ↓
hoàn tất trận → đánh giá kill/mission + trạng thái player
                  ↓
         endgame / Board_Endgame chung
                  ↓
         mission, sao, kết quả, save
                  ↓
  tutorial overlay + Continue theo tiến độ/mode
```

## Raw và kiểm tra tái lập

- Nguồn chính: `raw/il2cpp-consts/{DataTutorials,GP_Tutorials,Board_Endgame}.{asm.txt,json}` và `raw/ui-audit/extra-native/GP_{Endgame,Manager,Setup}*`.
- Snapshot: `reverse-engineering/raw/endgame-missions/shared-stage-victory.json.gz`: **21 method**, ASM + inventory gốc + SHA-256 các file nguồn + **18 kiểm tra**. Các nguồn cũ không bị thay thế/xóa.
- Collector: `python3 tools/verify/shared_stage_victory.py`.
- Test: `python3 -m unittest discover -s tests`.
- Bốn test mới kiểm raw tái lập, stage 1/2 first-run/replay, stage 3 độc lập IndexTutorial, tách overlay khỏi core tính điểm. Hàm intro_gate chỉ mô phỏng ba predicate, không giả làm runtime hay bằng chứng playthrough.

Giới hạn: kiểm không có lời gọi predicate là kiểm **direct-call trên ba thân core được nêu**, không phải chứng minh vắng mặt trên toàn bộ chương trình. Kết luận dựa vào các đường gọi dương tính và nhánh campaign đã đọc, không khẳng định mọi mode/entry/UI giống nhau.
