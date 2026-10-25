# 95 — Nối hết năm terminal leaves Basic/Circle22/23/24

**Tạm thời, đúng APK/lib đã pin.** Report94 dừng Basic/Circle tại entry helper.
Batch này bỏ đúng năm interception đó, chạy thân native đến Pool/GetComponent,
IBullet.SetBullet, SetActive và nhánh Bullet_Formation.CreateBullets/PoolObject.
Không đổi báo cáo94/hashes của fixture cũ, không tuyên bố hoàn tất23 wing.

## Bằng chứng

- `datas/wing_pooled_leaves.json`:5 native bodies, **837 instructions**; tham chiếu
  payload876 methods/index đã pin ở93, method hashes, các call/tail sites và4 exact RELA→symbol joins.
- `tools/verify/wing_pooled_leaf_fixture.py`: mở rộng fixture94, không sao chép expected từ emulator.
  `tests/test_wing_pooled_leaves.py`: **40 tests mới**, bao gồm cả geometry94 chạy xuyên leaf thật.
- Full **854 tests PASS69.819s**, datas validate PASS. FPCR0/Unicorn2.1.4 như94.
- Điểm bất ngờ: Basic23 tại14a6008 **branch ra ngoài method** đến2990890. Không đoán opcode
  hoặc bỏ qua lệnh này: recovery40223486658 SUCCESS lấy64 raw bytes ở địa chỉ đó từ cached
  APK cùng SHA. `raw/wing-emission/formation-trampoline.json` giữ file offset/VA/hash.
  Hai lệnh thực dùng là `ldr x10,[x10,#0xbf0]` rồi `b #0x14a600c`, bytes
  `4af945f9de55ac17`; native fixture thực thi cả hai, không hook/thay bằng Python.
  Các bytes tiếp theo là lân cận được giữ raw, **không** gọi là code đã đi qua.

## 1. Năm leaves không chung lifetime/speed

| Leaf | startLifetime | startSpeed | Nhánh formation |
|---|---:|---|---|
|22 Basic14a3f50|5|owner.btlSpeed hiện tại|không|
|22 Circle14a3d80|5|speed argument capture|không|
|23 Basic14a5d2c|4|owner.btlSpeed hiện tại|có|
|23 Circle14a58b4|10|speed argument capture|không|
|24 Basic14a8420|4|owner.btlSpeed hiện tại|có|

VA trong bảng lấy trực tiếp từ payload đã pin.
Tất cả force argument1, target=null, mask từ owner.targetLayer. Các số5/4/10 là
**lifetime**, không damage và không số viên. Circle speed argument15 và owner speed17
trong test cố ý khác nhau để chứng minh capture, không gán15/17 làm default APK.

**throughShield ở cả năm leaf = owner.throughShield trực tiếp**, không tự AND super.
Điều này khác13:13 native có super&&throughShield tại consumer. Config/caller vẫn có thể
quản lý giá trị field trước đó; không từ leaf suy normal gameplay chắc chắn xuyên shield.

## 2. Rotation và pool: phân biệt dữ liệu đầu vào với góc đọc sau

- Basic: lấy point.eulerAngles.z + packetAngle, nhân f32(.01745329238474369), gọi
  Internal_FromEulerRad, rồi truyền XYZ/quaternion cho Pool123ab5c.
- Circle: quaternion chỉ từ packetAngle, không cộng point.eulerAngles.z.
- Sau pool, SetBullet **đọc lại pooledObject.transform.eulerAngles.z**. Không truyền
  nguyên packetAngle làm startAngle. Đầu ra transform tùy Pool/Unity, không tự đồng nhất.
- Fixture quaternion trả identity có kiểm soát, pooled Euler77/point Euler30 có kiểm soát:
  chỉ chứng minh native đọc đúng nguồn/order. **Không** nói identity tương ứng77° hay
  Unity tính góc này như fixture. Native geometry group đã đối chiếu bằng các expected độc lập.
- Pool=null → null exception; không phải return bình thường hay missing-component skip.

## 3. Activate trước khi biết IBullet tồn tại

Cả năm leaf gọi **SetActive(true) trước GetComponent<IBullet>**. Điều này khác nhánh13
đã đo94, vốn activate sau SetBullet và thiếu IBullet thì không activate.

| Tình huống |22 Basic/Circle,23 Circle|23/24 Basic|
|---|---|---|
|Pool=null|throw trước activation|throw trước activation|
|Thiếu IBullet|đã activate; return, không PoolObject trong leaf|đã activate; PoolObject|
|IBullet có, thiếu formation|không yêu cầu formation|PoolObject, không SetBullet/CreateBullets|
|Transform=null sau component|throw sau activation|throw sau activation|
|Đủ components|SetBullet|SetBullet rồi CreateBullets|

Basic23/24 gọi cả hai GetComponent trước guard IBullet. Formation dùng Unity
Object.op_Inequality(obj,null), không chỉ pointer!=0: test pointer vẫn nonzero nhưng
adapter trả Unity-null thì đi PoolObject. Không giả định PoolObject đã hoàn thành thực tế:
đây SDK call được quan sát, chưa chạy implementation PoolManager trong fixture.

## 4. Basic23/24: callback formation trước, callback caller sau

Exact RELA/symbol bindings:
- GetComponent<Bullet_Formation> GOT2ae8030.
- Bullet_Formation.OnCollided GOT2ae8020, metadata45876264.
- Bullet_Formation.OnDestroyed GOT2ae8028, metadata45876272.

Dùng Delegate.Combine để ghép:
- IBullet onCollision = **formation.OnCollided, rồi caller onBulletCollided**.
- IBullet onDestroy = **formation.OnDestroyed, rồi caller onBulletDestroyed**.
- Caller callbacks=null vẫn giữ formation callbacks, không bỏ hook formation.
- Sau IBullet.SetBullet gọi `Bullet_Formation.CreateBullets(force1,target=null,
  targetLayer,owner.btlSpeed,lifetime4,caller onBulletCollided)`.
  Callback cho CreateBullets là **caller collision gốc**, không composite và không destroyed.

CreateBullets đọc speed/mask lại sau SetBullet; không phải native cache chung bất biến.
Các test chỉ dùng fields ổn định ở đoạn này, không từ đó suy cannot mutate trong callback SDK.
Các leaf khác truyền callback caller thẳng, không tự thêm formation callback.

Delegate cast fail ném exception sau activation, không tự PoolObject cleanup. CreateBullets
SDK ném exception thì SetBullet đã chạy trước. Tests giữ partial side effects, không biến
failure thành successful atomic volley. Delegate.Combine/typecast/Unity-null là adapters
khai báo rõ, không phải đã chạy CLR/Unity implementation hay đã invoke delegates.

## 5. Phạm vi đã nối và phần còn lại cụ thể

**Đã nối boundary94:** cả5 Basic/Circle helper bodies thực thi, kể cả trampoline23;
count/geometry → Pool request → activate → components → SetBullet/formation dispatch.
N2 spacingX0 thực đi3 leaf/3 SetBullet trong adapter hợp lệ, không chỉ3 entry observations.
Circle id−1 vẫn đi Pool với int32 bitpatternffffffff; Pool thật xử lý ID đó là việc riêng,
không lấy fake valid return của adapter làm bằng chứng ID tồn tại trong APK.

**Chưa chạy bên trong:** PoolManager.GetObject/PoolObject, Unity quaternion/transform engine,
IBullet concrete implementation/physics/collision/destroy callback delivery,
Bullet_Formation.CreateBullets123d98c cùng Scale/IELerpTo coroutines. Thân ASM của Formation
đã có trong raw/combat-chain/native; ghi rõ consumer tiếp theo, không gọi thiếu bằng chứng.

Các Shoot consumers khác của93 và special2/4/6/8/10/12/15/19 vẫn theo ledger trước;
map/save và Arena/PvP giữ thứ tự ưu tiên, không lấy95 làm giấy đóng23 wings hay DPS/hit semantics.
