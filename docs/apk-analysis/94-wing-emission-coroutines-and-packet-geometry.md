# 94 — Wing13/22/23/24: Shoot → coroutine → packet geometry

**Tạm thời, chỉ build APK đã pin.** Nối tiếp config93, không đổi tên kết quả thành
“đã xong toàn bộ23 wing”. Batch này đi qua bốn Shoot, ba coroutine, ba Basic packet,
hai Circle packet; bổ sung cả nhánh13 có IBullet đến SetBullet/SetActive.

## 1. Bằng chứng và kiểm tra

- `datas/wing_emission_flow.json`: **39 method bodies, 3,208 instructions** đối chiếu
  byte lib → Capstone → ASM đã giữ; gồm ctor, wrappers, iterators/accessors và terminal leaves.
- Raw chính `raw/wing-implementations/{index.json,method-bytes.json.gz}` giữ nguyên876 bodies.
  `raw/wing-emission/pool.json` bổ sung đúng8 bytes VA7575e0, SHA APK/lib cùng payload chính.
  Bytes `0ad7233d0ad7a33d` = f32(.04), f32(.08). Recovery40222486395 SUCCESS, receipt cùng thư mục.
- Exact RELA→symbol: GameLayer TypeInfo và GetComponent<IBullet>, callback13/23;
  dump GameLayer+0x14 static=`layerBullet`. Đây **không phải** giá trị instance/scene mặc định9:
  số9 là đầu vào chủ động trong fixture để phát hiện nhầm Z.
- Native Unicorn2.1.4, FPCR0; SDK adapters khai báo rõ. `wing_emission_models.py` là
  bản dịch độc lập ở các boundary hữu hạn, không lấy output emulator làm expected.
- **53 tests mới; full814 PASS67.850s; datas validate PASS.** Source/input hashes nằm trong contract.
  Basic tests quét N−3..8 × spacingX0/2 × demo false/true × ba implementations, ngoài các
  tests clock/order/null/bounds/mutation. Không suy từ fixture sang FPS, hit count hay DPS.

## 2. Shoot: ghi deadline trước hay sau callback là khác nhau

| Impl | Đủ deadline (kể cả bằng) | Emission dispatch |
|---|---|---|
|13|StartCoroutine **trước** rồi đọc time lần nữa, cộng shotRate, ghi timeToShot|iterator nhận number/id|
|22|ghi timeToShot trước|loop đồng bộ đọc childCount sống, mỗi child một Basic packet|
|23/24|ghi timeToShot trước|StartCoroutine sau đó; iterator nhận number/id|

Không cache “now” thành một số cho tất cả calls. Không có busy-coroutine guard trong chính
bốn Shoot: test gọi lần nữa tại deadline tạo iterator thứ hai; **không** kết luận caller/Unity
luôn cho overlap. Nếu StartCoroutine adapter ném exception,13 chưa ghi deadline,23/24 đã ghi.
Callback đổi shotRate trong StartCoroutine ảnh hưởng deadline13, không hồi tố23/24.
22 không có child vẫn tiêu deadline; barrel=null có thể throw **sau** ghi deadline.

### Sound, sửa nhãn sai trong commit collector

15b50ac là `PlayOneShot(AllClipName,float)`, **không camera shake**. Clip argument5;
normal volume f32(.6), super1. Interval indexed bởi super: super.04, normal.08.
Demo bỏ sound, không bỏ packet.13 kiểm sound sau hai pool attempts mỗi iteration;
22/23/24 kiểm trong Shoot. Việc sound gate đã mở không đồng nghĩa có projectile sống.
Commit32bed14da có chữ camera-shake trong message; tên đó không phải kết luận được giữ lại.

## 3. Coroutine13: hai phía mỗi nhịp, cấu hình IBullet đọc trực tiếp

MoveNext1489df0; wrapper1487e44; Shoot1487aec. State0 tính **một lần**:
`widthStep = owner.transform.localScale.x / number`,
`wait = min(shotRate/number, f32(.05))`. State1 tăng index, không tính lại hai số này.
Mỗi index i=0..number−1 thử **hai Pool.GetObject calls**, không dùng childCount làm số phía.
Có yield sau cả cặp cuối, lần resume sau mới false. N≤0 không pool/yield; không tự thêm center.

Nhánh pool hợp lệ và **có IBullet** đã chạy native, không chỉ dừng ở missing-component:

- Lấy child0/child1 của barrel; x lần lượt `childX − widthStep*i`, `childX + widthStep*i`;
  y giữ childY. Normal z=GameLayer.layerBullet; demo z=**barrel parent**.position.z+.1,
  không phải z riêng từng child.
- Angle lần lượt +4*i/−4*i degrees; native chuyển sang radians cho Internal_FromEulerRad,
  gọi setter rotation. Fixture ghi Euler input và trả quaternion identity kiểm soát;
  **không** tự nhận đã tái tạo Unity quaternion internals.
- IBullet.SetBullet: force1, target=null, targetLayer từ owner, startSpeed=btlSpeed sống,
  startLifetime=2, startAngle=angle trên, collision/destroy delegates bind owner;
  throughShield = super && owner.throughShield. **2 là lifetime, không damage.**
- Sau SetBullet gọi SetActive(true). Tests N3/scaleX6 cho x10,40,8,42,6,44 và angle0,0,4,−4,8,−8.
  Đây input transform fixture, không tọa độ prefab được tuyên bố cho APK.
- Pool=null → throw; pool có object nhưng thiếu IBullet → bỏ cấu hình/SetActive, vẫn tiếp tục
  hai attempts rồi yield. Có IBullet nhưng thiếu child1 → exception sau pool attempt thứ hai.
  Không đánh đồng ba tình huống đó với “đã spawn hai viên thành công”.

## 4. Coroutine23/24: một child packet mỗi yield, đọc lại dữ liệu sống

23 MoveNext14a6ff4;24 MoveNext14a9140. State0 index0; state1 tăng index.
Mỗi resume so với **childCount hiện tại**, gọi Basic, rồi đọc shotRate và lại đọc childCount
để tạo WaitForSeconds(rate/currentCount). Có wait sau child cuối.

- Baseline hai children/rate.12 → hai yields .06, rồi false, không phải một delay trước volley.
- Đổi rate/children tại terminal callback ảnh hưởng wait ngay iteration đó và guard lần sau.
  Test đổi2→1 child,rate.6: emit đầu xong wait.6 rồi false.
- Callback làm childCount0 **sau emission** → native chia ra +inf và vẫn truyền cho Wait ctor.
  Không clamp về0 hay biến thành “không yield”; xử lý infinity của Unity scheduler ngoài boundary này.
- Dispose của cả ba iterator không đổi state/current hay hoàn tất projectile cleanup;
  không suy thành StopCoroutine/scene lifetime semantics. Unknown state không tự restart.

## 5. Basic22/23/24: số cấu hình không luôn bằng số terminal calls

Basic RVAs14a39a8/14a5a84/14a8178, byte bodies thực sự chạy.
Chỉ id==−1 return sớm. Với N lẻ, hoặc spacingX/2==0, gọi center trước guard N<2.
N chẵn spacingX≠0: ring đầu0, offsetX=spacingX/2, offsetAngle=deltaAngle/2.
Trường hợp có center: ring đầu1, half offsets0 cho N lẻ.
Sau đó floor(N/2) rings với **đúng hai entries** directs (ctor−1,+1), mỗi entry một terminal call.
Giữ nguyên nhóm f32 mul/add native, không rút gọn hay FMA trong model.

**Các góc không được “sửa cho hợp lý”:**

- N2 và spacingX0 → center + một pair = **3 calls**. N0/spacingX0 → **1 center**.
- Negative odd N cũng có thể center trước return. Đây boundary behavior, không nói config93
  thực tế phát negative N. id−1 vẫn bỏ tất cả trước đó.
- directs thiếu entry thứ hai: có thể phát entry đầu rồi mới throw; không atomic rollback.
  N1 không cần dereference directs. Không suy thành “array có bao nhiêu hướng thì phát bấy nhiêu”.
- Basic center/pairs: normal z=layerBullet; demo lấy fresh point.position.z+.1.
  x và y cũng gọi getter riêng; test getter biến đổi chứng minh không có một atomic XYZ snapshot.
- Native stack capture ABI **khác22**: ref+16 owner,+24 collided,+32 destroyed;
  23/24 ref+16 destroyed,+24 collided,+32 owner. Fixture decode riêng; callback descriptor
  inputs0x111/0x222 được giữ đúng, không nhầm owner thành destroyed. Chưa invoke delegate ở đây.

## 6. Circle22/23 và ranh giới terminal helper

N<1 return, còn angle=`startAngle + f32(f32(arcRange/N)*i)`. N3/arc360/start−180
→−180,−60,+60, không thêm endpoint180. Wrapper Circle **không** filter id−1 như Basic.
Vector truyền vào terminal dùng lần đọc world.position cuối, **không** Basic layerBullet/demoZ override.
24 không có Circle method trong raw class này, không tự ghép tính năng23 sang24.

Năm terminal leaves Basic/Circle thực có Pool123ab5c call sites (13 iterator có Pool123a9fc).
Their native bytes đã đối chiếu, nhưng Basic/Circle fixture dừng ở **entry của leaf**:
geometry/count/captured arguments đã quan sát; leaf Quaternion/Pool/GetComponent/IBullet branch
chưa được thực thi trong fixture này. Không gọi chúng là successful pooled emission, hit, damage
hay DPS.13 đi sâu hơn đến SetBullet/SetActive adapter nhưng vẫn không chạy projectile behavior,
callback collision/destroy hay Unity scheduling. Các giới hạn ở đây là named boundaries, không
phán “thiếu dữ liệu APK”: code leaf vẫn có sẵn để nối tiếp.

## 7. Handoff và việc tiếp

Peer ACK93 comment6401658709 đã lưu raw/peer-review; chưa coi lời ACK là independent
verification của toàn spec mới. Arena/PvP comment6401593117 vẫn xếp **sau wing + named map/save**.

Nhập batch này theo đúng dispatch/timing/count laws, không thay thành constructorN×barrelCount chung.
Tiếp nối Basic/Circle leaves vừa nêu; các Shoot/consumer còn lại của config93 và special2/4/6/8/
10/12/15/19 vẫn phải đi theo method cụ thể. Không dùng report94 làm chứng chỉ đóng23 wings.

**CI receipt:** code589e1f588, Verify40223289936 **SUCCESS/job1m4s**.
Handoff94 và green receipt đã gửi PR12, JSON responses giữ ở raw/wing-emission.
Không tự nhận ACK94; source/body assertions không thay bằng CI status.
