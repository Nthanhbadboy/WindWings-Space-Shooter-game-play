# 56 — Mẫu số mission stage2/3 và concrete enemy destroy references

**PROVISIONAL — APK gốc, static normal GameMode0 / nonbranch / ChapterCurrent0.**
Không phải runtime replay. Không áp sang Chapter2, branch, challenge, debug-map
hoặc bản Premium. Nối các khoảng trống report54–55 bằng raw mới.

Mức **A**: field/bytes/native lệnh đọc trực tiếp. Mức **B**: kết quả nối/tính từ
các nguồn đó, có verifier. Các mức vẫn không biến kết luận thành final design.

## 1. Raw mới và tái kiểm chứng

- Recovery `40185308994`: pinned XAPK như report54; export đúng **14 root
  enemy GameObject** đã được reference bởi3 default wave, không chọn theo tên.
- `reverse-engineering/raw/early-waves/default-enemy-components.json.gz`:
  đầy đủ component ở mỗi enemy root; MonoBehaviour có bytes base64/SHA256,
  class đọc bằng parsed Mono head, script identity và header PPtr đúng context.
- Recovery `40185361444`: `Sub_Object.asm.txt/json` trong
  `reverse-engineering/raw/ui-audit/extra-native/` — implementation GetID.
- `Stage_Get_Datas.asm.txt/json` trong `raw/il2cpp-consts/`: GetCountEnemies và
  cctor không capped; MapController.Start trong `raw/ui-audit/extra-native/`.
- `mission-denominators.json.gz` ở `raw/early-waves/`:4 native bodies,
  metadata/calls, source hashes,31 ID lọc với instruction addresses,14 exact
  enemy reference joins, từng Call_Data/prefab ID,3 wave totals và2 stage totals.
- `python3 tools/verify/early_stage_denominators.py`: **11 checks**.
- `python3 -m unittest discover -s tests -q`: **57 tests pass**.

Exporter chạy `--enemy-details` chỉ thêm snapshot enemy; không ghi đè full wave
exports report54. Không thêm APK, texture hoặc audio vào Git.

Cảnh báo alignment header ở report54 vẫn áp dụng: **không resolve generated
`tree.m_Script`**. Custom ObjectPool.id và các PPtr quan trọng bên dưới được
cross-check trực tiếp với component bytes, không chỉ tin typetree generated.

## 2. Mẫu số từ đâu vào GP_Datas? — mức A/B

`MapController.Start`:

```text
132a4dc: đọc Stage_Datas.IsBranch +30
132a4e8: nonbranch →132a59c
132a5b0: GP_Datas.get_Instance @14c78cc →x19
132a5c8: GP_Setup.GetStageIndex @14f0da0 →w20
132a5ec: Stage_Get_Datas.GetCountEnemies(w20) @12c5f60
132a5f4: lưu result vào GP_Datas.countEnemies +58
```

Nhánh branch có kiểm tra khác và có thể dùng GetCountSpecialEnemies; không
lấy GetCountEnemies áp cho mọi nhánh. Getter stage có debug/test behavior theo
report52; bảng ở đây dùng internal1/2 tương ứng display2/3 bình thường.

## 3. GetCountEnemies không cộng number, cũng không đếm mọi prefab — mức A/B

Native `Stage_Get_Datas.GetCountEnemies @12c5f60`:

1. `Map_Get_Datas.GetListWaves(stageIndex)` tại12c6068.
2. Chọn resource prefix theo ChapterCurrent/IsBranch, format wave ID0000,
   `Resources.Load<GameObject>` tại12c6278.
3. `GetComponentsInChildren<Call_Data>(false)` tại12c6290; không include
   inactive descendants. Các node trong3 wave snapshot ở đây đều active.
4. **Bỏ spawnType5** (12c62c0..d8); không dùng `number` làm số đếm.
5. Duyệt `listPrefabEnemies +30`, GetComponent<IPooling>, gọi interface GetID.
6. Cộng1 nếu ID **không** nằm trong `Stage_Get_Datas.listIgroneEnemies +18`.
   Contains tại12c63a4; negation/and/add tại12c63b8..c4.

Pseudo-code có điều kiện resource/components/references hợp lệ:

```text
count = 0
for waveID in GetListWaves(stageIndex):
    prefab = Resources.Load(prefix + waveID.ToString("0000"))
    for data in prefab.GetComponentsInChildren<Call_Data>(false):
        if data.spawnType == EndMapPoint5: continue
        for enemyPrefab in data.listPrefabEnemies:
            if !listIgroneEnemies.Contains(enemyPrefab.GetComponent<IPooling>().GetID()):
                count++
return count
```

Native **không có skip6 ở đây**. StartWavePoint6 vẫn được duyệt nhưng prefab
array ở3 wave này rỗng, nên không thêm count. EndPoint5 có1 prefab reference
nhưng bị skip. SpawnType0/number0 không phải điều kiện bỏ qua.

### listIgroneEnemies từ cctor — mức A

`Stage_Get_Datas.cctor @12c75f4` dựng List<int>, append31 literal IDs rồi store
list ở static+18 tại12c8364. Verifier đối chiếu từng fast-path literal với
fallback List.Add argument cùng giá trị; không cộng trùng hai nhánh.

```text
30009, 30015, 30016, 38001, 30029, 30030, 31011, 31012,
31014, 38002, 30031, 30032, 30033, 30034, 30035, 30036,
30037, 30038, 30039, 30040, 30041, 35008, 35014, 35015,
35053, 35026, 35027, 35042, 35043, 35045, 35029
```

Đây là field của **Stage_Get_Datas**, không phải
Enemy_Data_Balance.listStaticEmemies. Không lấy hai list tên gần nghĩa thay nhau.
Trong14 enemy root liên quan, chỉ **ID38001** giao với list này.

## 4. IPooling ID đọc từ field thật, không parse tên prefab — mức A/B

Chuỗi inheritance trong dump:

```text
Enemy_Sub : Sub_Character : Sub_Object, IPooling
Sub_Object.m_OPScript : ObjectPool (+20)
ObjectPool.id : int (+20)
```

`Sub_Object.GetID @123bb54` đọc m_OPScript tại123bb58, null-check, đọc id tại
123bb60 rồi return. Không dùng chuỗi `H-38001` để suy numeric ID.

Với từng enemy root, verifier nối bằng `(serialized_file,path_id)`:

- Enemy_Sub.m_OPScript → đúng ObjectPool component cùng root;
- Enemy_Sub.controller → đúng Enemy_Controller component cùng root;
- Enemy_Controller.destroyScript → đúng Enemy_Destroy component cùng root.

Cross-check trực tiếp bytes gốc của snapshot pinned:
ObjectPool.id tại serialized offset32; Enemy_Sub.m_OPScript PPtr tại32;
Enemy_Controller.destroyScript PPtr tại32+6×12. Các offset serialized này
không phải quy tắc chung suy ra từ native offset+20 — chỉ dùng sau khi kiểm
raw của dataset hiện tại; đổi build/header phải audit lại.

## 5. Mẫu số đã resolve — mức B

| Display stage | Internal | Default wave | Slot không marker report54 | ID38001 bị loại | GetCountEnemies contribution |
|---|---:|---|---:|---:|---:|
|2|1|0164|274|12|**262**|
|3|2|0113|95|8|**87**|
|3|2|0005|155|4|**151**|

Tổng stage2 **262**, stage3 **238**. Mapping stage→wave được kiểm lại với
literal store asm của Map_Get_Datas cctor (raw report52, SHA nguồn hiện tại),
không dùng bảng tên wave đã aggregate trong datas/waves.json.

Đây là **denominator cấu hình theo thuật toán game**, không phải tổng object
đang sống, số spawn thành công quan sát được, hoặc số kill chắc chắn đạt được.
Runtime có thể thay dữ liệu; không giả định mọi slot đều đã trigger.

## 6. Threshold integer trên mẫu số này — mức B

Dùng float32 initializer report55, float32 multiplication rồi `fcvtzs` về0;
không ceil. Mode2 trong raw artifact đại diện **fallback mode khác0/1**, không
khẳng định đây là toàn bộ domain hoặc tên difficulty.

| Stage | Mode0: tier0 /tier1 /tier2 | Mode1 | Mode khác0/1 |
|---|---|---|---|
|2, denominator262|**52 /117 /209**|91 /157 /256|131 /209 /262|
|3, denominator238|**47 /107 /190**|83 /142 /233|119 /190 /238|

Tier ở đây là result GetMissionCompleted **0/1/2**, không tự gọi1/2/3 sao UI.
Ở mode0, result từ−1 sang0 khi counter đạt52 (stage2) hoặc47 (stage3).
**Không diễn đạt là chỉ cần bắn52/47 là thắng ngay**: còn SpawnEndedEvent,
active-list rỗng, state Playing, kiểm tra player và flow endgame report53.
Cũng chưa chứng minh ModeCurrent thực tế của một session bằng runtime.

## 7. Nhánh destroy giờ đã nối tới prefab cụ thể — mức A/B

Cả14 root đều có **base Enemy_Controller** và **base Enemy_Destroy**, và field
controller.destroyScript trỏ vào đúng base component, không chỉ tìm một
component có tên khớp ở đâu đó. Kể cả prefab tên BB-36001 vẫn là base component
ở snapshot này; không suy boss semantics hoặc gate riêng từ prefix tên.

Vì vậy base path report55 nay có applicability vào các root này:
movement-complete→Destroy(WhenDone2)→Pool→OnPoolEnemy79→Contains/Remove khỏi
active-list. Nó không tự emit OnEnemyDie19 ở nhánh type2.
Đây không chứng minh mọi enemy sẽ bay hết đường, hoặc runtime không đổi
reference; callback registration/movement timing còn là bài toán riêng.

## 8. Các giới hạn còn giữ

- Numeric mission tiers chưa nối sang số sao render và dữ liệu save/unlock.
- Denominator không có nghĩa killCount cũng filter bằng chính31 ID này.
  Death consumer có các nhánh reward/branch riêng; không đồng nhất hai phép đếm.
- Chưa quy world placement + scroll/tutorial pause thành timestamp spawn.
- Chưa có runtime replay của APK gốc; không dùng ảnh Premium thay bằng chứng.

Hướng raw join tiếp theo: result GetMissionCompleted→star UI/save, callback
victory→stage unlock/Continue, và concrete movement completion registration.
