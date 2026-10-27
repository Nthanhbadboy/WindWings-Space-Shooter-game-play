# 61 — BB-36001: pool parent, map scroll và lifecycle súng

> **Tạm thời, static original-APK; không phải runtime replay.** A: trường/asm
> trực tiếp; B: join/diễn giải từ raw; C: giả thuyết chưa đủ điều kiện.
> Không mở lại Premium, không lấy số từ screenshot hoặc summary kế thừa.

## 1. Raw mới và tái lập

Recovery **40188073425**, bot commit **c0ffce078**, cùng input APK đã pin:
`libil2cpp.so` SHA256 `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.
Đã giữ full native JSON/asm cho `PoolingManager`, `Machine_Gun_Attack`,
`Boss_BodyPhysics`, `Obj_Collider`, `Enemy_Datas` tại
`reverse-engineering/raw/ui-audit/extra-native/`.

Collector `tools/verify/balloon_lifecycle.py` ghép chúng với raw MapController,
AirFree/PinMap/PinTerrain và Enemy_Movement có sẵn. Output:
`reverse-engineering/raw/balloon-animation/lifecycle-parent-scroll.json.gz`.
Có **40 method bodies / 26 checks**, source SHA dùng bytes giải nén gzip;
method inventory không size-capped. Giữ declaration theo namespace, resolved
calls và metadata relocation loads bên cạnh asm, không chỉ ghi kết luận văn bản.
`GetObject` có 4 overload: collector cố ý lấy **overload đầu `(int index)`**,
đúng call của AirFree; không đánh đồng body của các overload.

```sh
python3 tools/verify/balloon_lifecycle.py
python3 -m unittest discover -s tests -q
```

## 2. Pool return có reparent; pool get không detach trong body đã đọc

### 2.1. Lấy object

A/B, `PoolingManager.getObject`, RVA **0x123a2c8**:

1. Chuyển ID thành string; lookup prefab dictionary.
2. Nếu list pooled instance có phần tử: lấy index0, đặt world position về
   `prefPos`, rồi `RemoveAt(0)` khỏi list.
3. Nếu cần clone: vô hiệu hóa prefab, `Instantiate<GameObject>` rồi vô hiệu hóa clone.
4. Nhánh chung đặt **world position** và **world rotation** rồi trả object;
   không thấy direct call `Transform.SetParent` trong body này.

`GetObject(int)` RVA **0x123a9fc** truyền position **(-255,-255,-255)** vào
`getObject`; ctor PoolingManager đặt `prefPos=(-99,-99,-99)`.
Các số này giải trực tiếp bit immediate float32 trong asm, **không phải border
hoặc vị trí gameplay cuối cùng**.

`Enemy_Movement.SetPosition` **0x1584070** ghi `Transform.position` rồi
`GameObject.SetActive(true)`; không ghi moveType trong method đó.
AirFree dùng SetAngle rồi SetPosition (report59); không gọi reparent trực tiếp.

### 2.2. Trả object

A/B, `PoolingManager.poolObject` **0x123a66c**:

- Kiểm tra object tồn tại rồi **SetActive(false)** tại **0x123a750**.
- Lấy IPooling/GetID và list ứng với ID; có các guard ID/list/Contains/object.
- Nhánh thêm object mới vào list: lấy clone.transform và manager.transform,
  gọi **SetParent(manager.transform)** tại **0x123a970**, sau đó append list.
- Không nói mọi invocation đều reparent: nhánh null/ID không hợp lệ/đã có trong
  list có thể return trước đó. Guard và asm được giữ trong raw.

**Hệ quả B:** không được mặc định mỗi lần lấy pooled object là root không parent.
Một instance qua nhánh return trên có thể còn parent của PoolingManager khi lấy
lại; `getObject` không có bước detach trực tiếp đã xác định. Prefab BB root
Transform **413057** có `m_Father=0`, localPosition0/localRotation identity/scale1,
nhưng **asset parent0 không chứng minh runtime reused parent0**.
Chưa có phép đo world matrix của PoolingManager lúc BB xuất hiện. Vì vậy chưa
đổi bảng root-local keys ở report60 thành world trajectory tuyệt đối.

## 3. Không gộp AirFree với PinMap hoặc PinTerrain

| Spawner | Reparent trong OnSpawn đã đọc | Bằng chứng A/B |
|---|---|---|
| AirFree | Không direct SetParent | OnSpawn1465e98 lấy pooled object, ITransform setters |
| PinMap | Có: enemy → parent của spawner | get spawner.transform → get_parent → SetParent tại1466b60 |
| PinTerrain | Có: enemy → `parentTerrains` | field offset30 → SetParent tại1467154 |

`PinTerrain_Spawner.parentTerrains` là serialized Transform; không tự coi đó là
`MapController.enemyParentMove`. Start của PinTerrain đã giữ trong raw: đặt
world z của spawner theo GameLayer; không chứng minh một runtime parent join
đến map layer. Không có raycast trong body OnSpawn đã đọc — không được suy từ
tên “Terrain” thành raycast/surface detection.

Report59 xác định slot partition của exact stage2/3: stage2 có 1 AirFree BB;
PinMap là các slot khác. Không chuyển logic reparent của PinMap sang AirFree chỉ
vì cùng thuộc một wave. Không suy enemy transform luôn nằm dưới terrain.

## 4. Map scroll: hai công thức khác nhau, không phải tất cả enemy đều trôi

A/B, `MapController.Awake` **0x1329f60**:

- Lấy `allMoveLayers[1]` gán **enemyParentMove** (offset28).
- `RemoveAt(1)` khỏi allMoveLayers. Do đó serialized enemyParentMove trống ở
  một typetree không đủ để kết luận runtime enemy layer trống: Awake ghi lại.
- Không lấy một map prefab theo tên để thay thế exact stage map runtime.

`Update` **0x132ba34** branch thẳng `ScrollMap` **0x132ba38**. Đọc thân ScrollMap
thấy các phép toán (dt là `Time.deltaTime`, không realtime):

```text
commonDelta = multipleSpeed * dt
for layer in allMoveLayers (duyệt ngược):
    layer.parentLayer.localY -= commonDelta * layer.speed * boostSpeed
if isMoveEnemyLayer:
    enemyParentMove.parentLayer.localY -= commonDelta * enemyParentMove.speed
ScrollBackgrounds()
```

**Nhánh enemy layer không nhân boostSpeed lần nữa.** Nhân cùng boost cho cả
hai nhánh sẽ sai native hiện có. SetSpeedMap chỉ ghi multipleSpeed offsetC0.

`ScrollBackgrounds` **0x132c1d8** xét **worldY < -1.5 * bgLength**, rồi tăng
worldY thêm **bgLength * countBg** cho từng background đủ điều kiện. Đây là
wrap background, không phải bằng chứng pool/remove/kill enemy.

Có method `IsScrolling` riêng, nhưng **Update/ScrollMap hiện đọc không gọi nó**.
Không tự chèn điều kiện Playing/Endgame vào pseudo-code ScrollMap chỉ từ tên
method hoặc từ sự tồn tại của getter đó. Các caller điều chỉnh multipleSpeed,
flag enemy layer hoặc activation vẫn cần xét nếu muốn dựng timeline cụ thể.

**Chưa chứng minh BB là child của enemyParentMove**, cũng chưa chứng minh
terrain scroll kéo BB qua border. Điều này độc lập với chuyện BB root có
animation position rõ ràng ở report60.

## 5. Súng không dùng coroutine: OnEnable → timer/FixedUpdate

### 5.1. Exact serialized guns

Nguồn A: subtree BB trong raw report60; Mono header identity resolve
`Machine_Gun_Attack` script `{fileID:1,pathID:338}`.

| Field | Barrels1 / component690037 | Barrels2 / component639146 |
|---|---:|---:|
| parentBarrels Transform | 447801 | 241448 |
| isAttack / typeDelay | true / Border0 | true / Border0 |
| delayShoot | 1 | 1 |
| shotRate | 0.15 (float32) | 0 |
| bRate | 0 | 0.1 (float32) |
| turnRate / turnNumber | 2 / 3 | 2 / 3 |
| bltSpeed | 8 | 6 |
| idBlt / lifetime | 80054 / 5 | 80054 / 5 |
| isReverse | false | true |
| bltPinMap | false | false |
| damage (serialized, chưa power) | 300 | 300 |
| allGunDatas | [] | [] |
| eventStart / eventEnded persistent calls | [] / [] | [] / [] |

Không nâng serialized damage thành damage thực: OnEnable gọi damage-powered
helper rồi tạo Damager. allGunDatas rỗng ở **hai instance này** nên nhánh mode
GunData override không được áp dụng từ array đó; không generalize sang súng khác.

### 5.2. OnEnable thực sự reset gì?

A/B, **0x1453bdc**: sau các phụ thuộc gameplay/mode/power:

- `timeToShot = Time.time + delayShoot` tại **0x1453e80–e98**.
- Ghi zero 8 byte ở7C: **timeToTurn + countTurn**.
- Reset **bCount**, **inverse**, **isStunned**.
- Tạo Damager từ damage qua helper.

**Không phải reset toàn bộ field.** Body này không ghi `isTurnStarted` (AC),
`timeToBarrelShot` (9C), `timeToStart` (A8). Đừng tự thêm reset từ trực giác.
Hai clip bật lại component có thể chạy OnEnable, nhưng đây chưa phải mô phỏng
thứ tự animation/lifecycle hoặc chứng minh tất cả timer stale đều không ảnh hưởng.

### 5.3. FixedUpdate và turn hooks

`FixedUpdate` **0x1454024**:

1. `!isAttack` → return.
2. TypeDelay.Timer1 và `Time.time < timeToStart` → return.
3. TypeDelay.Border0 và `IsOutScreen()` → return.
4. `isStunned` → return; còn lại gọi Shoot.

`Shoot` **0x1454084** chờ timeToTurn, gọi start-turn hook nếu cần, rồi:
**bRate == 0 → NormalShoot**, khác0 → BarrelShoot.
Do đó exact Barrels1 dùng normal route, Barrels2 dùng barrel route với serialized
values nêu trên (nếu không có writer khác đổi fields).

`NormalShoot` **0x14540e8** chờ timeToShot rồi đặt lần tới = now + shotRate,
Shooting, đếm turn; khi đủ turnNumber thì gọi end-turn hook, reset count và đặt
timeToTurn = now + turnRate. BarrelShoot có timer shot/barrel và child index
riêng; full body đã giữ, **chưa tính số đạn theo thời gian render**.

OnStartTurnShoot **0x1454b00** / OnEndTurnShoot **0x1454b14** gọi UnityEvent ở
C0/C8 khi khác null. Dump class **không khai báo OnDisable**. Vì vậy không được
suy animation enabled→0 sẽ gọi end-turn UnityEvent hoặc “complete enemy”.
Persistent listeners rỗng không chứng minh không ai gắn listener runtime.

Không có direct owner-destroy/pool call trong các turn hooks trên. Callback bullet
có thể đi đến IDamageable của **object va chạm**, không tự đồng nhất nó với
owner BB. Chưa có chứng minh animation hết pha súng sẽ phát kill19/remove79.

## 6. Collision và no-path gate: thu hẹp câu hỏi, không đóng giả playthrough

- Raw mới có Boss_BodyPhysics collision/trigger routes và Obj_Collider cache
  IHealth/IDamageable; OnDefeat của Boss_BodyPhysics lấy Collider2D rồi disable.
  Tên Boss_BodyPhysics không biến BB thành level boss trong logic roster.
  Chưa mô phỏng collision layer/health/reborn, cũng chưa suy touch-kill owner.
- Enemy_Movement.OnEnable **0x1586024** chỉ lấy GameLayer zFixed và ghi48;
  không reset typeMove/path trong body này. Không coi OnEnable là reset toàn bộ.
- Enemy_Movement.Update dispatch theo runtime moveType; **PathFollow return
  ngay nếu path=null** (load50/cbz tại15861ec–f0).
- FixedUpdate (report59) có turret boundary và movein+Linear2 boundary, **không
  phải một out-of-screen callback vô điều kiện cho mọi movement mode**.

Mệnh đề kiểm thử được, **chỉ có điều kiện**:

```text
moving=true, moveType=Path0, path=null, isTurret=false
→ không có path route; không có turret/linear boundary route trong hai body này
```

Kể cả animation/parent khiến world position ở rất xa border, nó không tự bật
các gate đó. Tuy nhiên **chưa chứng minh đây luôn là runtime state của BB**:
typeMove/path là private runtime fields, ctor không tương đương reset mọi lần
pool reuse; external writer, instance history và các route death/removal khác
vẫn cần xét. Vì vậy chưa nói “BB buộc phải bắn” hoặc “BB tự bay thoát”.

## 7. Trạng thái sau vòng này

Đã khép phần **đọc body spawn/pool-parent, công thức scroll, hai gun-instance
config và lifecycle dispatch** bằng raw kèm checks. Tăng độ chắc của report59–60,
đặc biệt loại bỏ giả định local=world và terrain-parent chung cho mọi spawner.

Chưa khép: exact live parent/world matrix, pool history/runtime field writers,
actual shots/collision/reborn và low-kill stage2 reachability. Không coi các mục
đó là hoàn tất chỉ vì unit tests xanh. Tiếp tục từ writer/caller graph và exact
map joins; không đòi screenshot mới làm điều kiện. T9 atlas rect là nhánh raw
riêng đang được ghi trong HANDOFF, Premium vẫn deferred.
