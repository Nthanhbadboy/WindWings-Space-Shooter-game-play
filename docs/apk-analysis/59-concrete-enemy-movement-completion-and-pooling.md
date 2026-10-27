# 59 — Enemy movement thật → callback → pool, không đồng nghĩa kill

**PROVISIONAL — static original-APK evidence, chưa runtime replay.**
Scope: các resource wave normal chapter0 của stage hiển thị2/3 đã xác định;
14 enemy root được tham chiếu, không tổng quát cho mọi enemy/boss/subclass.
A=bytes/native/metadata trực tiếp; B=logic nối từ chúng. Cả hai vẫn tạm thời.
Premium/reborn ngoài scope.

## 1. Bằng chứng mới, chạy lại được

- Native recovery **40187130445**, preserve commit **12280632a**: đầy đủ
  Enemy_Movement và VertexPath + nested helper, không size-capped.
- `raw/ui-audit/extra-native/{Enemy_Movement,VertexPath}.{asm.txt,json}`.
- Exact roots/raw Mono bytes: `raw/early-waves/default-enemy-components.json.gz`.
- Exact wave containers: `raw/early-waves/index.json` + exports0164/0113/0005.
- Derived `raw/early-waves/movement-completion.json.gz`: **28 method bodies,
  20 checks**,14 concrete joins, slots theo implementation, source hashes và
  declarations/metadata/calls. Gzip source hashes dùng decompressed bytes.
- `python3 tools/verify/enemy_move_completion.py`
- `python3 -m unittest discover -s tests -q`: **84 tests pass**.

Input SHA256 libil2cpp.so vẫn
`9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`;
collector đối chiếu native relocation với prefab inputs. Không dùng generated
m_Script header bị lệch alignment; giữ script identity đã parse và raw bytes.

## 2. Từ GO active tới callback: không còn chỉ suy delegate target — mức A/B

Cả14 Enemy_Controller.movementScript PPtr đã resolve đến **base Enemy_Movement**
trong đúng resources.assets/root. appearScript và destroyScript cũng lần lượt
trỏ **base Enemy_Appear / Enemy_Destroy**. Các pointer quan trọng được kiểm
ngược từ raw Mono bytes, không chỉ đọc tên component trong JSON.

Luồng native:

```text
Enemy_Controller.OnEnable @15826e0
  → Appear @15826e4
    → tạo Action(this.OnMoveCompleted)
    → movement.SetEventMoveEnded(action) @1582834
    → appearScript.Appear(Action(this.Appeared))
```

Metadata slot **2aec4d8** resolve OnMoveCompleted1584778;
slot **2aec4d0** resolve Appeared1584868. Base Enemy_Appear1582108 invoke callback
ngay, không có coroutine/timed wait trong body này. Appeared đặt moving+5c=true.
Không áp kết luận “appear ngay” cho appearance subclasses chưa kiểm.

## 3. onEnded không chỉ là callback destroy — mức A/B

`Enemy_Movement.SetEventMoveEnded @1583be8`:

1. Xóa onEnded+68 cũ.
2. Tạo/gắn callback self `<SetEventMoveEnded>b__22_0 @15869e4`.
3. Chỉ nếu argumentnonnull **và typeMoveEnded==0** mới Combine thêm callback
   controller. Mode enum: **Destroy0 / Event1**.

Callback self đặt movingfalse rồi invoke moveEndedEvent(UnityEvent), nếu có.
Callback controller mới làm pool. Vì vậy không được suy “onEnded luôn destroy”
cho modeEvent1 hoặc khi callback controller không được đăng ký.

**Trong14 root đang xét:** tất cả serialize typeMoveEnded0,
endOfPathInstruction2 (**Stop**), moveEndedEvent persistent calls rỗng,
Enemy_Destroy.isNoPoolfalse. Custom bytes32.. được kiểm lại cả enums, số speed,
float speeds, border và turret flag. Persistent-empty không chứng minh không
có runtime listener được thêm về sau.

## 4. Điều kiện hoàn tất path và waypoint thật — mức A/B

### PathFollower

Enemy_Movement.Update chỉ chạy khi movingtrue; typeMove0 gọi PathFollow.
SetPathFollower chọn typeMove0, reset distance0, lấy speed từ **phần tử cuối**
listSpeeds; lưu VertexPath của PathCreator. Không lấy Call_Data.speed thay cho
speed này mà chưa có consumer evidence.

PathFollow15861d4:

```text
dstTravelled += speed * Time.deltaTime
VertexPath.GetPointAtDistance(dstTravelled,endOfPathInstruction,onEnded)
```

GetPointAtDistance143db50 chia distance cho VertexPath.length rồi GetPoint.
CalculatePercentOnPathData với **Stop2** clamp normalized t về0..1.
Trong GetPoint, callback **không đơn giản là t>=1**:

- callbacknonnull;
- interpolation percent của đoạn cuối **==1**;
- squared distance giữa điểm nội suy và vertex cuối **< epsilon**;
- epsilon tại756a58 = float32≈**9.99999944e−11**, đã lấy bytes ở report58.

Đủ điều kiện thì invoke callback tại143dc50. Không có one-shot bool trong riêng
GetPoint; one-shot phụ thuộc movement dừng/pool và caller lifecycle. Không lấy
số lần gọi GetPoint làm số kill hoặc số wave completed.

### PointToPoint

SetWaypoints chọn typeMove1, yêu cầu ít nhất2 points, thiết lập pointIndex/count.
MovePointToPoint dùng speed×deltaTime tiến tới destination, so tọa độ đến đích,
tăng index. Khi index tới segment cuối, invoke onEnded tại1586588..65b4.
Không có một wait cố định “đợiN giây rồi pool” trong nhánh này.

Waypoints arrays/curve geometry, speed, frame scheduling, timeScale và tutorial
freeze ảnh hưởng thời gian thật. Chưa cộng khoảng cách thành timestamp wall-clock.

## 5. Border exit: đọc world coordinates, có gates — mức A/B

Enemy_Movement.FixedUpdate1586084 bắt đầu bằng guard moving.

- Nếu isTurrettrue và **world y < border.z**, invoke onEnded.
- Có đường riêng cho **moveintrue && typeMoveLinearly2**: nếu vượt ngoài
  x∈[border.x,border.y], y∈[border.z,border.w], invoke onEnded.
- Cả14 snapshot border đều **x−10..10, y−15..15**. Tại đúng biên chưa là out.

Không diễn giải −15 thành15 giây hoặc lấy triggerY làm wait time. Chưa nối đầy
đủ terrain parenting/scroll tới thời điểm world y cắt border cho từng turret.
Turret branch có fallthrough; không dùng predicate test như bằng chứng callback
luôn exactly-once khi listener đổi state hoặc cả hai nhánh cùng đủ điều kiện.

## 6. Controller callback WhenDone2 → pool, không đi death handlers — mức A/B

OnMoveCompleted1584778 đọc destroyScript+50, virtual dispatch
**DestroyType.WhenDone2**. Do prefab đã nối base Enemy_Destroy nên ta có body thật:

```text
Destroy(type2) @1581598
  → bỏ handler type0/1
  → Pool @1584bf0
    → event79(OnPoolEnemy)
    → PoolingManager.ReturnToPool
```

**Điểm tránh chèn sai bước:** Destroy2 không gọi virtual OnMoveCompleted hook
của Enemy_Destroy trong body này; nó nhảy thẳng từ15815a8 tới15815c8 rồi Pool.
Việc base có một method tên OnMoveCompleted không chứng minh method đó chạy.

GP_Datas.<ResetAlls>b__60_1 nhận event79, Contains/Remove khỏi
listActiveEnemies+70. Đường base trên không phát event19 OnEnemyDie như death/hit
handlers. Vì vậy có đường **active count giảm mà killCount không tăng**.
Không suy rằng external listeners tuyệt đối không thể có side effects khác.

## 7. Phân hoạch slots theo spawner, không biến thành actual kills

Mỗi reference dưới đây join bằng **file + prefab root pathID**, không dedup tên:

| Resource wave | Path | Waypoints | PointToPoint | PinMap | AirFree | Tổng slots cấu hình |
|---|---:|---:|---:|---:|---:|---:|
|0164 (stage2)|150|104|0|19|1|274|
|0113 (stage3 đầu)|0|0|80|15|0|95|
|0005 (stage3 sau)|140|0|0|15|0|155|

Đây là partition của prefab arrays bỏ marker5/6. Không đếm marker prefab thành
spawn, không đếm các reference này như số instance đã render/chết.
Normal denominator sau ID filter vẫn là262 / (87+151=238), không phải274/250.

**Ngoại lệ phải giữ:** AirFree duy nhất của0164 nhắm **BB-36001**, root có
Animator, isTurretfalse. AirFree.OnSpawn đọc ITransform, gọi slot1(SetAngle)
rồi slot0(SetPosition); nó **không gọi SetPathFollower/SetWaypoints** trong
body đã xét. Đã phân biệt **global ITransform (TypeDef228)** với
UnityEngine.UIElements.ITransform trùng tên; parser theo tên ngắn sẽ lấy nhầm
slot/property UI. Verifier giữ cả2 declarations và test collision. Enemy_Sub.SetPosition chỉ forward movement.SetPosition, không
chọn path mode hoặc gắn waypoint list.

Do đó chưa được áp “path hết thì tự pool” cho BB-36001 chỉ vì nó có base
Enemy_Movement. Animator/clip/callback của riêng prefab này còn phải nối.
Cũng chưa được kết luận BB bắt buộc phải bị bắn hoặc sẽ treo game.

## 8. Cập nhật độ chắc chắn của low-kill witness report58

Ta đã đóng thêm mắt ghép cụ thể: không phải chỉ “base class có thể pool”, mà
14 referenced roots có đúng callback mode/base scripts, cùng conditional
path/waypoint/border exits giảm active-list không cần kill event.

Nhưng chưa chứng minh session kill51/46 thật chạy tới gate empty-list:

- có slot AirFree/Animator chưa resolve;
- chưa runtime replay toàn wave/tutorial/player input;
- collisions, enemy attacks, geometry, point validity và event listeners có thể
  ràng buộc reachable state.

Model test `active=[lastEnemy], kills51 → pool → active=[], kills51` chỉ kiểm
logic list/counter giới hạn. **Không nâng thành “người chơi thua vẫn chắc chắn
unlock”**, không gộp stage target, saved stars và Continue scene thành một bước.

## Tiếp theo, không cần chờ screenshot

1. BB-36001 root Animator/controller/clip/event recipients và gameplay callbacks.
2. Terrain parenting/scroll của PinMap để nối world border exit.
3. Runtime wave validation và timeline có source geometry; giữ raw bên cạnh.
4. T9 Sprite rect/texture/rotation/trim là task asset còn mở đã nhận từ review.
Premium vẫn riêng; không redraw từ ảnh điện thoại.
