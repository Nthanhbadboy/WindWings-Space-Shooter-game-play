# 53 — Wave → Call_Point → Spawner → endgame gates

**PROVISIONAL — native/dump/metadata từ APK gốc, không phải runtime replay.**
Nối report52; Premium tiếp tục để riêng. Không suy ID hay số enemy từ screenshot.

## Nguồn giữ lại / tái kiểm chứng

- Recovery `40184325868` success, bot424beb253: Wave, Spawner, Call_Data,
  các implementation spawn và nested coroutines.
- Recovery `40184418916` success, bot00d23f3c1: bổ sung Call_Point trigger.
- Native asm + inventory: `reverse-engineering/raw/ui-audit/extra-native/`.
- `wave-spawn-flow.json.gz` ở cùng thư mục audit:22 method bodies,15 checks,
  source hashes, metadata slots, declarations/calls. Giữ cả GetMissionCompleted
  để không lấy tên method làm bằng chứng “diệt100%”.
- `python3 tools/verify/wave_spawn_flow.py`
- `python3 -m unittest discover -s tests -q`:45 tests pass.

Assertions kiểm tra các đoạn lệnh/joins được nêu, không phải emulator mọi nhánh.
Các implementation mới có raw không tự chứng minh chúng thuộc Wave_0164/0113/0005;
còn cần nối script component/Call_Data trong đúng prefab.

## 1. SetLastWave không chỉ gán một bool

Report52 đã giữ MapController gọi SetLastWave(index==arrayLength-1), rồi active
wave. Body `Wave.SetLastWave @13fda20`:

```text
CheckSpawnEnded(lastWave) [1417da4]
→ StartCoroutine         [tailcall278276c tại13fda40]
```

Do đó mỗi wave được gọi method này có coroutine theo dõi spawn-ended; bool cuối
quyết định event tổng sau đó, không phải lệnh thắng ngay lập tức.

## 2. Spawn trigger là Call_Point, có điều kiện vị trí/scroll

`Spawner.Awake @1468078`:

- GetComponent<Call_Point> bằng metadata slot2ae7908.
- Tạo delegate từ virtual slot OnSpawn của chính instance (146812c), nối vào
  Call_Point.onSpawn (+20) tại1468140..146816c.
- GetComponent<Call_Data> qua slot2ae7910, lưu Spawner.dataScript (+20).

Không gọi thẳng OnSpawn trong Awake. Delegate còn phải được trigger.

`Call_Point.OnEnable @1465874` với dataScript hợp lệ reset spawned(+40)=false
(tại1465914); có xử lý number/list prefab/ID riêng, không đồng nhất một component
Call_Data với một enemy.

`Call_Point.FixedUpdate @1465a30` kiểm tra:

1. dataScript tồn tại và spawned chưa bật.
2. GP_States.gameState **khác Endgame=3**. Không viết lại thành “chỉ Playing”.
3. MapController.instance.isMoveEnemyLayer (+78) phải bật
   (slot2ae1708 đối chiếu MapController type).
4. Đọc transform.position.y; khi y<=Call_Data.ySpawn (+40), đặt spawned=true
   tại1465cb0 rồi invoke onSpawn bằng tail-branch1465cdc nếu delegate không null.

Có đoạn cảnh báo trước đó tại y<=ySpawn+3, với warningPoints và warning flag;
không biến khoảng cách3 này thành3giây. Không chốt vị trí màn hình/pixel hoặc
thời điểm từ lúc vào scene chỉ từ các tọa độ native này.

Hệ quả: **SetActive wave không đồng nghĩa toàn bộ enemy xuất hiện ngay**.
FixedUpdate, scroll flag, vị trí từng call point và spawned flag vẫn là gate.

## 3. Ví dụ implementation: Path và Waypoints

`Path_Spawner.OnSpawn` khởi chạy SpawnEnemies coroutine. MoveNext:

- i so với Call_Data.number (+44), không dùng số row group làm số vòng lặp.
- Chọn ID từ listIdEnemies (+28), có đường lấy entry cuối khi i vượt độ dài list.
- PoolingManager.GetObject tại146656c; tăng GP_Datas.spawnCount (+60),
  phát EventID.OnSpawnEnemy=78 tại14665b8; setup item/path tùy interface/type.
- Đọc Call_Data.rate (+48), yield WaitForSeconds(rate) tại1466790.
  Đây là scaled wait, không phải wall-clock hoặc tổng thời lượng wave.
- Khi loop kết thúc: đọc Spawner.ended (+28), invoke với chính spawner tại1466678,
  kết thúc coroutine. Đường Path chờ yield ở mỗi lượt, kể cả trước khi loop quay
  lại và phát ended sau lượt cuối; không tự bớt một interval khi dựng timeline.

Waypoints coroutine cũng có vòng lặp, pool/interface/point setup, rate wait và
ended callback (1468750), nhưng không mặc định mọi nhánh wait giống Path.
Đã giữ raw cả hai để đối chiếu, chưa áp một implementation cho mọi call point
của stage2/3 khi chưa có prefab join.

**ended nói “spawner đã hoàn tất công việc spawn”, không nói enemy đã chết.**
Event78 được phát trong đường lấy object/setup; không tự dùng event này làm
bằng chứng enemy đã render thành công hay đã bị diệt.

## 4. Wave.countPoints là bộ đếm callback, không phải kill counter

`Wave.<CheckSpawnEnded>d__7.MoveNext @1418120`:

- Lấy GetComponentsInChildren<Spawner>(includeInactive=false) tại1418268,
  qua slot2ae6090. Không gọi đây là toàn bộ spawner kể cả inactive.
- Khởi tạo closure.countPoints từ số component tìm được.
- Ở đường normal/nonbranch (và các nhánh đi chung): phân loại Call_Data.spawnType:

| SpawnTypes raw | Xử lý trong bộ đếm |
|---|---|
|5=EndMapPoint|trừ countPoints ngay; không đợi callback này trong aggregation thường|
|6=StartWavePoint|trừ ngay; gán callback b__2 để phát các start-event có điều kiện|
|còn lại|gán callback b__3; callback giảm countPoints khi spawner báo ended|

Các callback b__1 và b__3 đều decrement countPoints(+10). b__2 là đường start
và event phụ, **không phải decrement b__3**. Nhánh branch-even riêng đặt countPoints=1
và gắn callback b__1 cho EndMapPoint (1418544..1418624); không mang bảng xử lý
normal áp cho nhánh này.

Coroutine yield WaitUntil(predicate b__0) tại14183f4.
Predicate141810c: `countPoints<1`. Đây không phải `GP_Datas.killCount`.
Các ghi callback vào Spawner.ended+28 thấy trực tiếp trong asm.

### Sau khi countPoints đạt điều kiện

State1 tiếp tục tại1418418:

1. Phát **EventID.WaveEndedEvent=74**, param indexWave (+20) tại1418450.
2. Nếu closure.lastWave=true: phát **EventID.SpawnEndedEvent=73** tại1418470,
   rồi kết thúc coroutine.
3. Nếu không phải cuối: đi đường cleanup; kiểm endPoint.position.y<-30,
   có đường deactivate/destroy và yield WaitForSeconds(10) để kiểm tiếp.
   Không hiểu10 là delay giữa hai wave hoặc thời lượng combat.

Các EventID73/74/78 trên khác hoàn toàn callback số0..8 của tutorial ở report51.
WaveEnded không tự chứng minh player đã diệt hết enemy của wave.

## 5. SpawnEndedEvent mới bắt đầu poll endgame

`GP_Manager.Start` tạo listener từ slot2ae8f50 →2bc4930 →
`<Start>b__11_7 @14f6104`; register EventID73 tại14f3a7c..14f3a8c.
Handler lấy gpEndgame (+50), gọi StartCheckEndgame tại14f6188, truyền callback
`<Start>b__11_11` (slot2ae9030).

`GP_Endgame.<CheckEndgame>d__4.MoveNext @14f13d0` poll:

```text
GP_Datas.listActiveEnemies (+70).Count == 0
AND GP_States.gameState == Playing(1)
→ bắt đầu khối đánh giá kết quả
nếu chưa đủ → WaitForEndOfFrame → poll tiếp
```

Count đọc tại14f1510..151c, state check14f1554..1558. Vì poll được khởi tạo qua
SpawnEndedEvent, không được bỏ lớp spawn-ended và chỉ kiểm list rỗng ở đầu màn.
Cũng chưa chứng minh mọi enemy chết/thoát đều được thêm/xóa list đúng; đó là
một cầu raw khác cần nối, không giả định Count0 tương đương kill100%.

### Kết quả thắng/thua là bước nữa, không phải auto-win

Trong GameMode0/nonbranch, đường14f17fc..14f1864:

- Lấy GP_Datas.killCount static+1c và countEnemies instance+58.
- Gọi Board_Endgame.GetMissionCompleted(count,maxCount) tại14f1850.
- `mvn` rồi shift31 chuyển dấu kết quả: bool=true khi result>=0,
  false khi result<0; lưu outcome closure+10.
- GetMissionCompleted có loop/threshold từ dữ liệu mission/mode; **chưa chốt các
  float threshold**, không tự thay lời gọi này bằng killCount==countEnemies.
- Coroutine còn xét trạng thái player/interface; có đường ghi outcome=false.
  Branch/challenge có mục tiêu supply/star hoặc đường khác, không gộp chúng.

Sau đánh giá, có UI cleanup, Time.timeScale=1, hiển thị kết quả qua GP_Display,
WaitForSeconds(2) tại14f19dc..14f19e8. Resume state1 gọi callback manager tại14f16cc,
rồi MoveOutPlayer tại14f170c. Callback manager đặt state Endgame3 và gọi cleanup.
Đây là2scaled giây ở đúng bước này, không phải “sau enemy cuối chết2giây vào màn mới”.

Closure `<CheckEndgame>b__0 @14f13ac` nhận outcome bool và gọi
OpenBoardVictory(bool) tại14f13c4 sau đường di chuyển player.
Không bỏ qua MovePlayer/timeout hoặc nhận diện tên OpenBoardVictory là luôn thắng.

## Còn mở sau lượt này

1. Prefab Wave_0164/0113/0005 → danh sách Call_Data, spawner cụ thể, tọa độ,
   number/rate và các marker. Chưa có tổng enemy instance đã được xác minh.
2. OnSpawnEnemy / enemy chết / out-of-screen → listActiveEnemies add/remove,
   killCount và các mission thresholds chính xác. Empty list không thay kill ratio.
3. MovePlayer/timeout và thời điểm UI/victory/scene transition trên runtime.
4. Callsite cấp ownership drone/chọn talent; fade dispatch/timing vẫn mở như report52.
   Không cần thêm screenshot làm điều kiện bắt đầu các phép bóc raw này.
