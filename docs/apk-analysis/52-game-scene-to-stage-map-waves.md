# 52 — Continue/fade → Game → terrain → wave consumer

**PROVISIONAL — chỉ bằng chứng tĩnh từ APK gốc, không phải replay runtime.**
Nối report50–51, không dùng ảnh để suy stage/index, không đào Premium.

## Evidence và kiểm tra

- Recovery `40183973174` success, bot commit `575113776`: bổ sung MapController,
  ScenesManager, FadeScreen và nested classes ở `raw/ui-audit/extra-native/`.
- `reverse-engineering/raw/ui-audit/scene-map-flow.json.gz`:12 method bodies,
  inventories không size_capped, source hashes, calls, metadata/relocation slots,
  dump declarations và raw cctor excerpts cho hai mảng campaign.
- `tools/verify/scene_map_flow.py`:13 assertions, đọc trực tiếp asm/dump/metadata;
  **không đọc datas/maps.json hay dùng lại prose để suy ID wave**.
- `python3 tools/verify/scene_map_flow.py`
- `python3 -m unittest discover -s tests -q`:41 tests pass.

Assertions kiểm tra mẫu lệnh và joins cụ thể, không thay thế emulator/dataflow
checker cho toàn bộ chương trình. Các điều kiện mode/branch/chapter dưới đây
không được bỏ khi tái dựng.

## 1. Đường fade cũng về Game, không phải scene Loading riêng

`Board_Endgame.LoadToLoading @126f3c8`:

- Nhánh không có FadeScreen: gọi ScenesManager.LoadScene(2), như report51.
- Nhánh fade: metadata slot `2addcf0` → `2bceb80` →
  `Board_Endgame.<>c.<LoadToLoading>b__130_0`, RVA `1276e1c`.
  Delegate được tạo tại126f4e0, đưa vào FadeScreen.FadeOut tại126f510.
- Body callback1276e1c: `mov w0,#2; mov x1,xzr; b 141b488`.
  Vì enum2=Game, hai đường cùng yêu cầu scene Game.

`ScenesManager.LoadScene @141b488` chuyển nguyên index cho
Unity SceneManager.LoadScene(int sceneBuildIndex) tại141b4e8 (target27903b8),
sau đó ghi ScenesManager.Current bằng index đó tại141b4f4.
Không có bước cộng/trừ stage trong wrapper này; build index scene và stage index
là hai loại dữ liệu khác nhau.

### Callback được truyền qua fade thế nào?

- FadeOut nhận Action, gọi FadeTo(alphaFrom0, alphaTo1, callback, flag) tại13bb3b8,
  rồi StartCoroutine tại13bb3c8.
- Factory FadeTo lưu callback ở coroutine+38 tại13bb348.
- MoveNext có block đọc đúng+38 tại13bbb30, null-check rồi invoke tại13bbb44.

Đã nối danh tính delegate/factory/invocation, **chưa giải bảng dispatch8state**
tại779f66 hoặc float literal wait756fe0. Vì vậy không công bố thời lượng fade,
trình tự mọi yield, hay thời điểm title xuất hiện. Loading object trong FadeScreen
không đồng nghĩa một scene riêng tên Loading.

## 2. GP_Setup không copy StageCurrent vào instance trong Awake

`GP_Setup.Awake @14f6988` chỉ gán singleton instance. Getter
`get_stageIndex @14f0da0` đọc static state theo nhánh:

1. Nếu Application.companyName so sánh bằng literal `Test` và
   GameDatas.fixedStagePlay (+38) bật: đọc Map_Get_Datas.mapCurrentPlayTest (+20).
2. Nếu không đi test override và Stage_Datas.IsBranch (+30) bật:
   đọc StageBranchCurrent (+2c).
3. Nếu không branch: đọc StageCurrent (+24), trả tại14f0ec8.

Vậy ở normal/nonbranch, thay đổi StageCurrent trong Continue đi vào getter của
setup, không cần bịa một bước “loader copy stage vào field instance”. Nhánh test
là companyName, **không tự đổi thành scene name hay build mode**.

## 3. GP_Manager gọi loader terrain thật

`GP_Manager.Start` gọi `gpSpawner.LoadPlayer` tại14f3460.
Tên LoadPlayer dễ gây hiểu nhầm: body này có đường load **map terrain**.

Ở GameMode0, nonbranch, vùng14f3d50..14f3e8c:

```text
setup.stageIndex
→ int.ToString("0000")
→ "Datas/Maps/Terrains/Map-" + formattedIndex
→ Resources.Load<GameObject>
→ Instantiate<GameObject>(..., parentMaps)
→ SetActive(true)
→ GetComponent<MapController>()
→ lưu gpSpawner.mapController (+28)
```

Callsites: getter14f3d64; format14f3d80; prefix slot2ae8fa0;
Resources14f3e04; Instantiate14f3e60; component14f3e88; store14f3e8c.
Generic method identities từ metadata, không suy chỉ từ call RVA chung.

Nhánh branch dùng prefix khác `Datas/Maps/Terrains_Branch/Map-`
(slot2ae8f88). Còn các nhánh mode khác và đường parent đã có child;
không khẳng định mọi invocation luôn instantiate terrain mới.

Với điều kiện đường normal được thực hiện:

| Stage hiển thị* | Internal index | Resource terrain được dựng tên |
|---:|---:|---|
|2|1|Datas/Maps/Terrains/Map-0001|
|3|2|Datas/Maps/Terrains/Map-0002|

\* Dùng phép nối label stageIndex+1 trong normal/nonbranch của Board_Begin.Start
đã giữ raw ở report50; không áp số này vào branch/test override.
Resource key không có extension, đây là tên native yêu cầu, không phải xác nhận
asset đã load thành công trên thiết bị.

## 4. Đã đóng cầu stage → GetListWaves → resource wave

`MapController.Start @132a15c`, nhánh lấy index setup:

```text
132a84c setup.get_stageIndex
132a858 w20=w0
132a870 w0=w20
132a878 Map_Get_Datas.GetListWaves(mapIndex)
```

Không có +1/-1 giữa getter và tham số call này.
Ở normal/nonbranch, GetListWaves lấy `listMapDatas` static+28 tại13feb84,
clamp index vào0..Count-1 (13feb98..13febac), rồi trả mảng ID wave.
Mode1/2/4 và branch có đường khác; không áp campaign table cho chúng.

### Tái đọc literal campaign, không tái dùng bảng kế thừa

Raw cctor Map_Get_Datas:

-1406bf0 tạo List, x28 giữ List mới; các append đầu giữ trong evidence.
-Entry0:25,9010; entry1 tạo int[1] tại1406c9c,
  `mov w8,#0xa4; str w8,[x1,#20]` → **164**.
-Entry2 tạo int[2] tại1406d10,
  store0x71 vào+20, store5 vào+24 → **113,5**.
-List x28 được gán static+28 tại140e19c, đối chiếu dump= listMapDatas.

Verifier đọc lại hai allocation/literal-store spans, fail closed nếu thiếu store
hoặc register nguồn không còn immediate. Excerpts tạo list, append đầu và store
field đều được giữ cạnh kết quả; toàn body cctor vẫn ở raw/il2cpp-consts.

### Consumer load đúng thứ tự mảng

Sau GetListWaves, MapController.Start duyệt mảng qua x21=data+20, index x26=0;
mỗi lượt tăng index1 và pointer4 tại132ac48/4c.

- Format ID bằng `0000` (132a8d0).
- Default prefix `Datas/Maps/Waves/Wave_` (slot2adf9a0).
- Normal ChapterCurrent>=1 đổi sang `Datas/Maps/Chapter2/Waves/Wave_`
  (132aa2c..132aa58); branch/challenge có prefix riêng.
- Resources.Load tại132ab40 → Instantiate dưới parentWaves(+30) tại132ab6c.
- GetComponent<Wave>, dùng GetWaveLength/GetWaveReduceStartY để đặt vị trí.
- SetLastWave(index==length-1) tại132ac30; SetActive(true) tại132ac40.

Vì vậy **GameMode0, nonbranch, ChapterCurrent0**, không test override:

| Stage hiển thị | ID wave theo thứ tự | Resource key tương ứng |
|---:|---|---|
|2|164|Datas/Maps/Waves/Wave_0164|
|3|113 rồi5|Datas/Maps/Waves/Wave_0113 → Datas/Maps/Waves/Wave_0005|

Đây là **1 và2 prefab wave được consumer dựng theo table**, không phải số enemy,
không phải1 và2 coroutine wave chạy tuần tự theo đồng hồ. Loop instantiate/activate
các wave; thời điểm spawner của từng wave chạy còn phụ thuộc script/triggers.
Không đổi grouped rows42/91/82 thành số enemy spawn.

## Còn mở, không che bằng suy đoán

1. Wave activation → Spawner/OnSpawn → coroutine từng kiểu enemy; điều kiện kết
   thúc wave và victory. Chưa có trace runtime hoặc tổng enemy count được xác minh.
2. Bảng dispatch/literals fade để chốt thứ tự yield và thời gian; không suy từ thứ
   tự các block MoveNext trong file asm.
3. Toàn bộ caller cấp DroneUnlocked/chọn TALENT_SELECTED trước stage2/3 vẫn mở.
4. Scene lifecycle thực tế, title/UI timing và các đường save/mode khác chưa được
   chứng minh chỉ bằng cầu resource này. Không gọi static chain là replay hoàn chỉnh.
