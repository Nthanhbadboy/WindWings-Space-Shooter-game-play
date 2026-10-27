# 54 — Đúng resource prefab của stage 2/3, không gộp theo tên

**PROVISIONAL — dữ liệu cấu hình bóc từ APK gốc, không phải runtime replay.**
Premium để riêng. Nối resource route report52 với spawn gates report53.

## Bằng chứng và kiểm lại

- Runner `40184816569`, cache XAPK có SHA256
  `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- `tools/apk-analyze/early_wave_prefabs.py`: duyệt container của
  ResourceManager/AssetBundle; resolve PPtr trong đúng serialized file; giữ toàn
  bộ subtree, không cap số component, không dedupe theo tên node.
- `reverse-engineering/raw/early-waves/index.json`: **14 container entries**.
  Mỗi export có input SHA, identity file/pathID, GO/Transform/component typetree,
  bytes MonoBehaviour base64 + SHA256, và prefab enemy references đã resolve.
  Không lưu APK, texture hay audio vào Git.
- `resolved-default-waves.json.gz`: bảng từng Call_Data, local position, trigger
  y, rate, parentPoints/child count, prefab names, item flags;18 checks.
- `python3 tools/verify/early_wave_prefabs.py`
- `python3 -m unittest discover -s tests -q`:48 tests pass lúc lập report.

**Cảnh báo decoder:** `tree.m_Script` trong typetree sinh tự động có thể lệch
alignment ở header MonoBehaviour (vd Call_Data hiện m_FileID=16777216).
Không dùng field đó để resolve class! Exporter lấy class từ
`parse_monobehaviour_head().m_Script` của UnityPy; giữ bytes gốc để kiểm lại.
Custom spawn fields và prefab references bên dưới là output typetree, được
cross-check với trigger/native loop; không coi toàn bộ header generated là đúng.

## 1. Tên wave không phải khóa duy nhất

Map normal chapter0 ở report52 tạo `Datas/Maps/Waves/Wave_NNNN`. Container:

| Wave | Container key chính xác | File | Root GameObject pathID |
|---|---|---|---:|
| 0164 | `datas/maps/waves/wave_0164` | resources.assets | 148604 |
| 0113 | `datas/maps/waves/wave_0113` | resources.assets | 21468 |
| 0005 | `datas/maps/waves/wave_0005` | resources.assets | 38187 |

Chapter2 có **root khác**, dù cùng tên:0164→148637,0113→21456,0005→38205.
0005 còn có8 container branch/challenge khác. Không chọn prefab bằng tên GO,
không cộng cả Chapter2, không coi copies trong `datas/waves.json` là số đợt.
Bảng cũ dùng friendly enum5/6 sai và nhóm tên; không dùng nó làm nguồn đếm mới.

## 2. Cấu hình spawn của đúng ba root

| Stage hiển thị, normal chapter0 | Wave | Nodes | Call_Data | Marker5/6 | Slot cấu hình không tính marker |
|---|---|---:|---:|---:|---:|
| 2, internal1 | 0164 | 537 | 42 | 2 | **274** |
| 3, internal2, wave đầu | 0113 | 387 | 91 | 2 | **95** |
| 3, internal2, wave sau | 0005 | 58 | 16 | 2 | **155** |

Các GO trong3 subtree đều active; component có m_Enabled đều enabled trong
snapshot. Đây không đảm bảo không bị runtime thay đổi.

Mọi Call_Data ở đây đều serialize `number=0`, `listIdEnemies=[]`.
**Không có nghĩa không spawn:** report53 chứng minh Call_Point.OnEnable đặt
`number=max(number,listPrefabEnemies.Length)` và dựng dữ liệu trước trigger.
Ở snapshot này không có trường hợp number lớn hơn prefab array.

Slot tổng tính bằng độ dài prefab array ở các điểm **không phải marker5/6**.
Mỗi EndPoint còn chứa1 prefab reference, nhưng chỉ có base Spawner, không đưa
reference đó vào enemy slots. StartPoint có0 prefab. SpawnTypes.None0 vẫn có
PinMap_Spawner, **không bỏ qua tất cả type0**.

Không gọi274 hay95+155=250 là số enemy phải diệt: chưa nối denominator
GP_Datas.countEnemies, PoolingManager failure, kiểu entity, runtime mutation,
điểm chưa trigger, hoặc enemy phát sinh thêm. Đây chỉ là slot cấu hình.

### Spawner implementation nằm thật trong prefab

| Wave | Path | Waypoints | PointToPoint | PinMap | AirFree | Base marker |
|---|---:|---:|---:|---:|---:|---:|
| 0164 | 14 | 12 | 0 | 13 | 1 | 2 |
| 0113 | 0 | 0 | 80 | 9 | 0 | 2 |
| 0005 | 11 | 0 | 0 | 3 | 0 | 2 |

Spawn enum không đủ xác định implementation:0113 thực sự dùng
PointToPoint_Spawner, không tự suy nó là Waypoints_Spawner từ enum2.

## 3. Prefab references — không suy ID/type từ tên

| Wave | Phân bố tên prefab ở slot không phải marker |
|---|---|
| 0164 | CB-30003×150; CB-30001×46; XB-34003×35; CB-30002×14; H-38001×12; XB-34005×6; CD-31003×4; CD-31004×3; XB-34001×3; BB-36001×1 |
| 0113 | CB-30024×58; CB-30001×16; H-38001×8; CB-30002×4; CD-31003×2; GD-33005×2; CD-31002×2; XB-34003×2; CD-31004×1 |
| 0005 | CB-30003×140; CD-31003×4; CD-31005×4; H-38001×4; CD-31004×3 |

Các tên này lấy từ GameObject được resolve qua PPtr, không từ suy đoán ảnh.
Chưa dùng prefix/tên BB để tuyên bố boss gate, hoặc H để suy loại vật phẩm.

## 4. Ví dụ position/rate và giới hạn timeline

Trong đúng0164:

- `Path_CB3_5 (12)`: local y26.20000076; ySpawn9.60000038;16 references
  CB-30003; rate0.5. Report53 chứng minh Path iterator chờ scaled rate mỗi
  lượt, kể cả lượt cuối trước ended. Không suy thời điểm bắt đầu từ local y.
- `Point_H`:2 references H-38001; PinMap_Spawner; rate serialize0.0;
  ySpawn12; local(x2.69000006,y28.14999771). Không suy rate semantics chung
  từ Path sang PinMap; PinMap.OnSpawn còn tự ghi rate0 tại1466a84.
- `StartPoint`: local y−4.40000153; ySpawn9.60000038; type6/base Spawner.
- `EndPoint`: local y89.29000092; ySpawn5; type5/base Spawner.

Local position ≠ world trigger position. Muốn timeline phải ghép terrain/wave
placement, parent rotation/scale, scroll speed/pause và gate tutorial. Đã giữ
hết Transform trong subtree; không lấy thứ tự BFS exporter làm thứ tự spawn.

## Tiếp tục tự đào

Đã chuyển sang raw enemy lifecycle: GP_Datas đăng ký event78/79, Enemy_Destroy
emit pool event; cần nối remove khỏi active-list với từng kiểu thoát/kill và
threshold mission trước khi quy các slot ở trên thành điều kiện thắng.
