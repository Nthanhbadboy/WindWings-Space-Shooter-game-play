# 51 — Consumer tutorial, drone được trang bị và nhánh Continue

**PROVISIONAL — bóc tĩnh từ APK gốc, chưa phải replay runtime.** Nối tiếp report50;
không lấy screenshot làm bằng chứng số stage, không phân tích Premium.

## Nguồn và tái kiểm chứng

- Recovery `40183580920` và `40183664095`: native classes ở
  `reverse-engineering/raw/ui-audit/extra-native/` (asm + inventory JSON).
- `stage23-rodata.json`: giữ bytes bảng nhảy và veneer executable từ cùng
  `libil2cpp.so`; checksum APK được workflow kiểm tra trước khi bóc.
- `tutorial-consumer-flow.json.gz`:17 method bodies, hash nguồn, declarations,
  direct calls, metadata joins, bảng nhảy/veneer;11 assertion kiểm chứng mẫu lệnh.
  Metadata scanner bảo thủ: không có record trong output không có nghĩa không có reference.
- `python3 tools/verify/tutorial_consumer_flow.py`
- `python3 -m unittest discover -s tests -q`:37 tests pass.

Các assertion là kiểm tra evidence tĩnh cụ thể, không phải ARM64 emulator hoặc
bằng chứng mọi nhánh gameplay đã chạy.

## 1. Callback số đã nối tới consumer thật

`GP_Manager.GameStarted @14f3fb4` gọi `GP_Spawner.SpawnEnemies @14f404c`,
rồi tạo Action<int> chuyển vào `GP_Tutorials.GameStarted @14fa024`.
Callback slot `2ae8fb8` → relocation `2bc4950` → metadata
`GP_Manager.OnThroughTut`, MethodAddress `14f47cc`.

Có một bước không được bỏ qua: `14f4004 b 2990898` đi ra ngoài body export.
Raw executable tại2990898 là `ldr x22,[x22,#fb8]`, sau đó `b 14f4008`.
Đây là cầu nối trở lại call SpawnEnemies, không phải kết thúc GameStarted.
Không suy callback chỉ từ tên method hoặc giả định code sau unconditional branch
vẫn tự chạy tiếp.

### Bảng dispatch của OnThroughTut

Selector=`eventState+1`, unsigned compare với9; ngoài range -1..8 trả về.
Table `77a13e`, bytes `00 29 23 3d 41 55 5d 63 4f 74`, base `14f482c`,
target=base+byte*4. **Không dùng thứ tự block asm làm thứ tự case.**

| eventState | target | Tác động nhìn thấy trong consumer |
|---:|---|---|
| -1 |14f482c| lockMove=true; Controller.GameStarted; lockUiTut=false; isLockChange=false; ShowSkillButtons rồi ShowUi |
| 0 |14f48d0| lockMove=true; Controller.GameStarted |
| 1 |14f48b8| ShowUi |
| 2 |14f4920| lockUiTut=false |
| 3 |14f4930| ShowSkillButtons, trừ nhánh IndexTutorial==1 và stageIndex==1 |
| 4 |14f4980| lockUiTut=true; ShowDroneSkillButtons |
| 5 |14f49a0| HideSkillButtons |
| 6 |14f49b8| isLockChange=true; lockUiTut=true |
| 7 |14f4968| ShowSkillButtons |
| 8 |14f49fc| gpLoader.StartDrones |

Offsets được đối chiếu dump: Manager+28=gpDisplay, +30=gpLoader,
+60=gpController; Display+20=lockUiTut; Datas+65=isLockChange;
Controller static+0=lockMove. Đây là **eventState nội bộ**, không phải EventID.
Tên Show/Hide ở bảng là lời gọi method; bảng không tự chứng minh mọi object UI
đều hiện/ẩn vì nội dung các method vẫn có thể có điều kiện riêng.

### Bổ sung quan trọng cho stage2/3

- Stage2 gọi0/1/2 trước coroutine; sau2 scaled s, callback8 **thực sự gọi
  StartDrones**, không chỉ thông báo chung chung. Sau droneAppear và3.9 scaled s,
  coroutine đóng băng thời gian rồi callback4 (`14fc69c`) khóa UI tutorial và gọi
  ShowDroneSkillButtons. Dùng skill xong callback2 gỡ lockUiTut. Report50 đã bổ sung
  callback4 vốn bị lược trong sơ đồ prose cũ; raw body trước đó đã giữ lệnh này.
- Stage3 callback8 cũng StartDrones; lúc overlay callback5 gọi HideSkillButtons;
  sau chạm burst callback7 gọi ShowSkillButtons. LockMove/lockRestoreTime còn do
  coroutine ghi trực tiếp như report50, không phải chỉ consumer này.
- Nhánh không chọn talent: callback8 rồi-1 chạy đường setup/unlock/UI tổng quát;
  không có cơ sở dựng một popup talent bắt buộc cho nhánh này.

## 2. Drone 20001: chọn trang bị không đồng nghĩa mở khóa sở hữu

Trong **nhánh đi tới LoadToLoading** của `Board_Endgame.Continue`:

```text
126f26c GetIndexTutorial
nếu ==1:
    GetDroneUsed(slot0)                [126f280]
    nếu kết quả ==0:
        SetDroneUsed(slot0,20001)      [126f290; 20001=0x4e21]
LoadToLoading                         [126f298]
```

Đây không phải mọi lần nhấn Continue: phía trước có GameMode, tutorial/FirstPlay
và các route khác. Không ghi đè slot0 đã có drone.

`SetDroneUsed @14db228` ghép key slot rồi gọi PlayerPreferences.SetInt
`14db2bc`; body không gọi `SetDroneUnlocked @14db13c`.
Setter unlock là method khác, có logging unlock và key `DroneUnlocked`.
Vì vậy đã chứng minh **assignment trang bị có điều kiện**, chưa chứng minh
ownership grant tại chỗ này, và chưa xác định toàn bộ callsite cấp quyền sở hữu.
Cũng không đồng nhất SetInt với SaveToDisk/flush thiết bị.

`GP_Loader.StartDrones @14f2864` lấy `GP_Setup.indexDrones` (`14f2908`),
bỏ entry<1 (`14f2924`), dựng tên `Prefabs/Drones/Drone_` + index,
lấy child slot, tạo object và SetActive(true) (`14f29f4`).
Getter setup đã đọc GetDroneUsed ở report50; vậy callback8 có cầu nối tới
**drone đang được chọn**, không phải tự suy drone mặc định luôn có sẵn.
Chưa dùng đường này để khẳng định thời điểm EventID29 được phát.

## 3. Talent được chọn là dữ liệu riêng

`Board_Talents.get_GetTalentIndex @1397438` đọc `TALENT_SELECTED`, default=-1
(`1397494`); setter13974a4 ghi cùng key bằng PlayerPreferences.SetInt.
Kết hợp gate stage3 trong report50: không có selection thì bypass overlay và ghi
flag TUT_TOUCH_SKILL. Chưa chứng minh talent tự được mở/chọn trước stage3;
không dùng selection getter làm bằng chứng ownership unlock.

## 4. Tiến trình: target thay đổi trước Continue, Continue không luôn +1

### Target trong OpenBoardVictory

Ở `GP_Endgame.OpenBoardVictory @14f0830`, vùng14f0914..14f09b4:

```text
nếu GameMode static+0 ==0
và setup.stageIndex == StageTarget
và StageTarget < ZoneUnlocked*10+9:
    StageTarget = StageTarget+1
```

Đối chiếu static fields/type slots với dump. Gọi setter `12bac5c` tại14f09b4.
Đây là điều kiện thấy trong body; không thêm điều kiện `_victory==true` vào đoạn
này khi asm không có. Tên method không đủ để suy mọi caller chỉ có chiến thắng.
Getter/setter StageTarget có logic cache/clamp/zone; không giả định getter thuần
hoặc requested value luôn được ghi nguyên vẹn.

### Continue chọn current stage

Vùng126f0d0..126f1c0 (normal progression route):

- Nếu StageCurrent!=StageTarget hoặc StageMode>1:
  `StageCurrent=min(StageTarget,StageCurrent+1)`.
  Chuỗi126f128 add /126f12c cmp /126f130 csinc /126f134 store chứng minh clamp.
- Nếu current==target và mode<=1: đi nhánh duyệt stage/mode, gọi GetStageStars
  `12b7860`, tìm điều kiện stars<=2, ghi stage/mode được chọn tại126f1bc/1c0.
  Không rút gọn nhánh này thành “luôn vào màn kế tiếp”.

Vì target có thể tăng ở endgame trước khi Continue chọn current, không gom
hai biến này thành một biến stage duy nhất. Với điều kiện nhánh phù hợp, current1
và target>=2 sẽ cho current2 (nhãn3 ở normal/nonbranch); đây là hệ quả có điều kiện,
không phải chứng minh mọi save đều đi stage2→3 như nhau.

## 5. Method LoadToLoading không chứng minh có scene tên Loading

`Board_Endgame.LoadToLoading @126f3c8` đặt isQuiting=true, có nhánh qua
FadeScreen.FadeOut và callback; nhánh không có fade gọi trực tiếp
`ScenesManager.LoadScene(2)` tại126f528.

**Enum raw:2=Game**, không phải Loading (enum gồm Menu/Home/Game/Endgame/HomeData).
Vậy đã xác định direct scene route vào Game; chưa lần theo đầy đủ callback fade,
loader coroutine, unload/reload và thời điểm title màn kế hiện ra.
Không dùng tên method để bịa một scene Loading.

## Còn mở — chuyển lượt đào kế tiếp

1. Tất cả callsite SetDroneUnlocked và setter talent: ai cấp ownership/chọn talent
   trước các tutorial, tách khỏi cơ chế Premium.
2. Callback fade của LoadToLoading và Game loader: stage fields copy vào setup ra sao.
3. GP_Spawner normal/branch map consumer: SpawnEnemies đã có raw mới nhưng chưa
   nối hết loader/map/wave. Không biến số row group thành số enemy spawn.
4. Input gọi skill → event phát → cờ hoàn tất, và trace runtime thực tế vẫn riêng;
   các kết luận trên là tạm thời từ cùng APK gốc.
