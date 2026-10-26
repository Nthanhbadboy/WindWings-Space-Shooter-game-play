# 50 — Stage2 / Stage3: gate → tutorial → chờ thao tác → tiếp tục

**PROVISIONAL — bóc trực tiếp APK gốc, không cần ảnh stage2/3, không dùng số
Premium.** Report49 chỉ nói bộ ảnh chưa chụp hai stage; không có nghĩa raw thiếu
logic hai stage. Report này nối các mảnh raw thành luồng có điều kiện.

## Nguồn và bằng chứng được giữ

- Recovery **40183022449**, bot a519c67bf: thêm native Board_Begin và
  Stage_Behaviour. Recovery **40183197035**, bot7787b781c: thêm rodata dispatch.
- Native SHA256: `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.
- `reverse-engineering/raw/ui-audit/stage23-ui-flow.json.gz`: **24 method**,
  nguyên asm + hash + declaration + callsite + GOT→metadata, panel references,
  chữ/key tiếng Việt. Giữ cả coroutine declarations để biết offset nào là field gì.
- `stage23-rodata.json`: byte thật của jump table và float literal từ libil2cpp.
- Gốc layout: `raw/ui/GP_Tutorials__1902.json.gz`, serialized_file **level2**.
  Không ghép pathID trần giữa các asset file.

## 1. Đã nối số stage hiển thị với index trong code

`Board_Begin.Start` nhánh label thường/không branch:

- `0x15dcfb8` gọi GP_Setup.get_stageIndex;
- `0x15dcfc4` **cộng1**;
- `0x15dcff8` format với chuỗi `{0} {1}`, phần tên lấy key `txt_stage`;
- thêm mode theo `txt_stagemode_` rồi ghi vào `textStage`.

Metadata slots được resolve: 2addc30→txt_stage, 2adc708→`{0} {1}`,
2addbf8→txt_stagemode_, 2aede88→`<size=6>[{0}]</size>`.
Do đó **internal1 → displayStage2; internal2 → displayStage3**, không chỉ dựa
vào tên get_hasTutStage2/3. GP_Setup.get_stageIndex nhánh thường đọc
Stage_Datas.StageCurrent static+0x24; branch/test có đường riêng, không gộp.

## 2. Stage2 — hướng dẫn dùng kỹ năng drone

### Gate thật

`DataTutorials.get_hasTutStage2 @0x1327f08`:

```text
IndexTutorial == 1 && GP_Setup.Instance.stageIndex == 1
```

`GameStarted @0x14f47c8` tailbranch vào CheckRunTutorialNew. Khi gate đúng:

- cho phép hiện nút Pause;
- gọi eventState lần lượt với0,1,2 (giữ numeric, **không nhầm với EventID**);
- đặt GP_Datas.isLockChange=false (instance+0x65);
- `0x14fa260`: TutDrones(panel=tutobjUseDroneSkill, delay=2, eventState,
  eventCompleted=null), rồi StartCoroutine.

### State machine đã đọc cả jump table

Jump table5byte tại0x77a148 = `00 0f 2e 3e 9c`.
Targets lần lượt state0..4: 14fc574 /14fc5b0 /14fc62c /14fc66c /14fc7e4.
Không suy thứ tự từ vị trí text asm.

```text
Chờ WaitForSeconds(2)
→ eventState(8)
→ WaitUntil(droneAppear)
→ WaitForSeconds(~3.9)
→ Time.timeScale=0
→ eventState(4) — consumer/UI đã nối tiếp ở report51
→ hiện panel drone + cover + hiệu ứng focus nút skill
→ reset hasUseDroneSkill=false
→ WaitUntil(hasUseDroneSkill)
→ eventState(2)
→ ẩn focus, trả/pool hiệu ứng, ẩn cover và panel
→ Time.timeScale=GP_Time.timeScale
→ kết thúc coroutine
```

Float3.9 đọc từ0x756e58, bytes`9a997940`. Cả2 và3.9 là **scaled seconds**, không
phải tổng thời gian tính từ lúc load scene hay đồng hồ thực; còn chờ drone xuất hiện.

- OnDroneAppear @14fa72c đặt field+0x94; predicate b__48_0 đọc đúng field này.
- OnUseDroneSkill @14fa840 đặt field+0x96; predicate b__48_1 đọc đúng field này.
- Focus parent chọn btnSkillDrone/btnSkillDrone2 theo GetDroneUsed(0)>0.
- Chưa đủ để nói ở đây cấp quyền sở hữu drone. GP_Setup.get_indexDrones đọc các
  slot đã dùng; đoạn tutorial này chủ yếu **chờ** drone/skill, không tự chứng minh grant.

### Panel có sẵn trong raw

`tutobjUseDroneSkill` instance+0x68 → local PPtr(0,1906), `TutUseDroneSkill`,
2node, root serialize inactive. Text key `txt_tutorial_usedroneskill`:
**“Kỹ năng máy bay phụ phá giáp kẻ địch và gây sát thương lớn.”**
Cover → local1908. Activation do coroutine, không lấy inactive mặc định làm
kết luận panel không bao giờ hiện.

### Kết nối sang stage3

Coroutine drone ở nhánh này **không nhận completion callback**, không thấy nó
increment IndexTutorial. Nhánh thắng của Endgame ThroughTut cho early index≤1
mới bật Continue/ẩn Replay và increment index (report45/47).
Luồng ứng viên first-run chuẩn: stage2 với index1 → thắng → index2 → Continue.
Còn scene/loading/advance phải theo nhánh Continue thực tế, không nhảy trực tiếp
sang stage3 chỉ vì coroutine drone đã kết thúc.

## 3. Stage3 — hướng dẫn talent / chạm hai ngón tay

### Gate khác stage2, không được copy điều kiện index

`get_hasTutStage3 @0x1327f8c`:

```text
GP_Setup.Instance.stageIndex == 2 && !IsTutTouchSkillDone()
IsTutTouchSkillDone := PlayerPreferences.GetInt("TUT_TOUCH_SKILL", 0) == 1
```

**Không có yêu cầu IndexTutorial==2 trong gate này.** Phân biệt gate hiển thị
với guard increment trong callback bên dưới; replay chưa hoàn tất vẫn có thể
vào hướng dẫn nếu caller đi qua nhánh này.

CheckRunTutorialNew sau đó đọc Board_Talents.GetTalentIndex:

- **!=-1:** ẩn nút Pause, eventState(8), TutTalents(panel=tutobjTouchSkill,
  delay=3, eventState, completion=b__1), StartCoroutine.
- **==-1:** không chạy TutTalents; eventState(8), eventState(-1), bật Pause,
  ghi **TUT_TOUCH_SKILL=1**. Không vẽ overlay bắt buộc trong trường hợp này.

### Coroutine và thao tác hoàn tất

```text
lockTalent=true; WaitForSeconds(3)
→ lockMove=true, lockRestoreTime=true, lockTalent=false
→ Time.timeScale=0
→ căn panel theo player (có deltaPosCam), hiện panel + cover
→ eventState(5); focus chuyển về btnTalent
→ reset hasTouchBurst=false; WaitUntil(hasTouchBurst)
→ gỡ lockMove/lockRestoreTime; eventState(7)
→ ẩn cover/panel/focus/helper; khôi phục GP_Time.timeScale
→ completion callback
```

GP_Tutorials.Start đăng ký event0x1c/0x1d; EventID trong dump xác nhận chúng là
OnTouchBurst28/OnDroneAppear29. OnTouchBurst @14fa84c đặt+0x97, predicate b__52_0
đọc+0x97. Hint trong prefab mới là nguồn mô tả **chạm hai ngón tay**; chưa dùng
đoạn này để khẳng định toàn bộ thuật toán nhận dạng input.

### Completion callback b__1 @0x14fb8dc

1. Ghi **TUT_TOUCH_SKILL=1**, key resolve từslot2adc338.
2. Nếu IndexTutorial==2 **và Stage_Datas.StageCurrent==2**, tăng index thêm1
   (thành3 trong điều kiện này).
3. Bật lại Pause.

Đây là tiến độ hoàn tất **trong gameplay**, không phải đợi clear stage3.
Không kết luận đã flush PlayerPrefs xuống đĩa; không suy lên increment cho mọi replay.

### Panel raw

`tutobjTouchSkill` instance+0x70 → local PPtr(0,1911), `TutUseTouchSkill`,6node:
ObjectTut/Ranger/Image_UseSkill/Image_UseSkill2 và Text_Tut.
Key `txt_tutorial_touchskill`:
**“Chạm hai ngón tay trên màn hình để sử dụng kỹ năng đặc biệt (tài năng)”**.
Cùng cover1908; focus object+0x20 được reparent vào btnTalent+0x48.

## 4. Checklist dựng flow từ raw, không cần chờ thêm ảnh

| Stage | Khi nào hiện tutorial | Chờ gì để bỏ overlay | Điểm cần giữ |
|---|---|---|---|
| 2 | internal1 + tutorialIndex1, delay2 rồi chờ drone và3.9scaled s | hasUseDroneSkill | panel drone, cover, focus đúng slot; pause cho phép; restore tốc độ cấu hình |
| 3 | internal2 + touchFlag chưa==1 + có talent, delay3scaled s | hasTouchBurst | ẩn rồi bật Pause, input locks, panel bám player, flag riêng và callback có guard |

Phần **đã nối được**: số stage ↔ gate ↔ panel ↔ pause/timeScale ↔ predicate ↔
callback/flag. Chưa gọi là replay runtime hoàn chỉnh: còn mapping consumer của
numeric eventState, input path đầy đủ, grants/unlocks và end-to-end loading/advance.
Bảng stage_gates UNRESOLVED của inventory cũ report42/early-stage-coverage là
snapshot cũ, **không còn đại diện trạng thái mapping tutorial hiện tại**.

```sh
python3 tools/verify/stage23_ui_flow.py
python3 -m unittest discover -s tests -q
```

9checks native và33unit tests pass ở lượt này. Không dùng screenshot, không chạy
game giả, không đưa dữ liệu Premium vào kết luận.
