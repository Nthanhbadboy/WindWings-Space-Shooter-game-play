# 93 — Review ACK92; đọc rộng 24 wing, chứng minh 17 cấu hình SetBarrels

**Provisional, APK pinned**, không dùng spec làm nguồn gameplay. Bên spec yêu cầu tiếp23 wing
implementation còn lại và named map/save consumers; batch này làm phần wing theo cụm, không
báo đóng toàn bộ23 firing implementations chỉ vì đã thu đủ native.

## 1. Review spec thực tế

Peer **c80b1c50dfd16261eee751ffbf07cce9ff136590**; ACK92 **6401411518** đã lưu cùng hai
snapshot DATA_SYNC/MISSING trong raw/peer-review. Kiểm tra độc lập:

- DATA_SYNC§24.22 đã tách player-collider gọi ItemCollected trực tiếp khỏi drone postevent2.
- §24.24 và MISSING§2.2 giữ guard CurrentHealth>0, tech level≤0→heal0.
- MISSING§5 footer đã tách structural classification DONE khỏi named entry/order UNKNOWN.
- §24.25 áp mapping12 drone, serialized turnRate3=1, getter fresh-array/mode4 và loader đúng scope.

Ba góp ý92 được xử lý đúng; **không còn pending ACK92**. Không gửi lại lỗi cũ như lỗi mới.

## 2. Nguồn mới, không phải chỉ đếm method

- `raw/wing-implementations/method-bytes.json.gz`: **876 method bodies, 24 implementations và
  nested classes**, lấy thẳng ELF của XAPK SHAf5d3c7… / lib SHA9cb038… đã pin.
  Scope range mỗi method = đến RVA kế tiếp trong dump, không cắt theo cửa sổ256/512 instruction.
- Số đã kiểm chứng: **66845 instructions**: Capstone5.0.3 disassemble toàn bộ
  bytes từng body và so từng instruction với native text bảo tồn. Không có decode gap.
- Giữ numeric pool bytes và raw ELF RELA entries riêng. Sửa collector để giữ cả GOT load
  dùng offset **decimal `#8`** (vd ctor22/GOT2ae8008), không chỉ regex `#0x...`.
- CI recovery **40221325255 SUCCESS**, bản bổ sung RELA **40221709393 SUCCESS/job43s**.
  Gzip482626 B, không APK/native library/media hay file>5MB trong snapshot hiện tại.
- Contract `datas/wing_implementations.json`:24 rows, source identity provenance,
  fields/access sites, all method hashes,14 numeric-array constructor joins,
  normal configuration parameters cho17 implementations, virtual damage sites và7 named special paths.

**Raw đầy đủ không tự đồng nghĩa semantic rewrite đầy đủ.** Phần được làm tới hành vi trong
batch này là **17 SetBarrels bodies / 1314 instructions**, gồm impl1 đã có và **16 impl mới**.

## 3. Normal shot-rate, speed, spread: không copy impl1 cho mọi tàu

Đặt **S = startShotRate đang nằm trên instance**, **V = startBltSpeed**;
L là từng lần getter Level được gọi lại. Bảng viết gọn cho các lần đọc có cùng L;
fixture riêng giữ timeline khi các lần đọc khác nhau. Từng phép tính làm f32 theo instruction,
không fused multiply-add; số thập phân dưới đây là cách viết ngắn, raw bits nằm trong pool.
**S/V là input instance, KHÔNG tự lấy constructor thay serialized prefab.**

| impl | normal shotRate | normal btlSpeed | angleDelta |
|---:|---|---|---|
|1|S−.0035L|min(V+1.1L,42)|min(3trunc(L/10)+5,15)|
|3|S−.001L|min(V+1.15L,38)|không ghi field này|
|5|S−.00689L|min(V+.5L,45)|như1|
|7|S|min(V,45)|như1|
|9|S−.0035L|min(V+.4L,45)|như1|
|11|S−.005L|min(V+1.5L,42)|min(2trunc(L/10)+3,6)|
|13|S−.003L|min(V+.5L,42)|không ghi|
|14|max(S−.005L,.036)|min(V+.1L,42)|như11|
|16|max(S−.01L,.06)|min(V+.2L,42)|min(6trunc(L/10)+30,60)|
|17|S|min(V,42)|như11|
|18|S−.001L|min(V+1.15L,38)|không ghi|
|19|max(S−.03L,.02)|không có field speed|không ghi|
|20|S−.0035L|min(V+1.1L,42)|min(trunc(L/10)+1,5)|
|21|max(S−.005L,.2)|min(V+.1L,42)|không ghi|
|22|S−.005L|min(V+1.5L,42)|như11|
|23|S−.005L|min(V+1.5L,42)|như11|
|24|S−.005L|min(V+1.5L,42)|không ghi|

Đây là **normal SetBarrels configuration**, không phải tốc độ đạn/bắn cuối cùng qua mọi skill.
Nhánh super của các method này bỏ qua rate/speed/spread normal; count/list selection vẫn chạy.
**Ngoại lệ20:** angleDelta nằm SAU điểm nhập lại của nhánh super, **vẫn được tính** dù rate/speed
không bị SetBarrels ghi lại. Không viết universal “super bỏ qua toàn bộ SetBarrels”.

## 4. Count index khác nhau, và count không tự là số projectile/volley

- **Compressed/two-read**:1/3/11/16/17/18/20/22/23/24. Cùng L0..10 →
  index **0,1,2,2,3,3,4,4,5,5,6** (có upper clamp theo length).
  Cụ thể khi firstRead>2: n=secondRead−2; n<−5→0, else min(trunc(n/2)+2,length−1).
  Khi firstRead≤2: secondRead<0→0, else min(secondRead,length−1).
- **Level−1**:5/7/9/14 → max(L−1,0), **không tự upper-clamp** trước array bounds check.
- **Clamp level trực tiếp**:13/21 → clamp(L,0,length−1), không L−1.
- **19** không có allNumberBullets/count lookup trong SetBarrels.
- **3/18** chọn một barrel-list từ listAllBarrels, không phải số đạn int trong constructor.
  Fixture đưa list length rõ ràng, không bịa length gameplay prefab.

14 constructor arrays đã nối `InitializeArray` argument → GOT→RELA→Field$ → raw field-default
bytes, verify SHA trong tên field và store đúng `allNumberBullets` của instance:

|impl|raw array|
|---:|---|
|1|3,4,5,6,7,8,9,12,13,14|
|5|1,2,3,3,4,4,5,5,6,6|
|7|3,5,5,7,7,7,9,9,9,9|
|9|4,4,5,5,6,6,6,7,7,7|
|11/17|3,3,4,4,5,5,5,6,7,7|
|13|2,3,4,5,5,6,6,7,7,8,8|
|14|1×11|
|16/23/24|1×10|
|20|6,6,8,8,10,10,12,12,14,14|
|21|3,3,4,4,5,5,6,6,6,7,7|
|22|2,3,3,4,4,5,5,5,5,5|

Arrays trên là **constructor initialization**, không tự phủ nhận override serialized/runtime.
Không lấy array toàn1 của14/16/23/24 để kết luận một projectile/cả volley: packet/circle/coroutine
là consumer tiếp sau. Đây cũng không phải shared Level cap; cap/shared getter đã có report90.

## 5. Cách kiểm chứng hành vi: chạy đúng native bytes, không model tự so với model

`wing_native_fixture.py` dùng **Unicorn2.1.4**, ARM64, explicit **FPCR=0** cho fixture.
Chạy nguyên SetBarrels function bytes gồm lookup/count/super branch/float math/return;
chỉ adapter sáu dependency entry rõ tên: metadata-init noop, get_Player_Ingame, get_Level,
List.get_Item, null exception và bounds exception. Heap/list/player và S/V đều input công khai.
Không thực thi Unity, không giả live save state, không suy FPCR thiết bị từ fixture.

78 tests mới:17×normal/floors-caps/super/null; normal và floor-cap mỗi test chạy L0..10;
đối chiếu model f32 độc lập với kết quả native bytes; actual14 constructor arrays làm input.
Có reread timeline[10,2,20,3] của impl1, empty-array exception, high-index throw ở5 và clamp ở1.
Fixture instruction budget chỉ chống test treo, không thêm native loop cap.

Trong lúc kiểm chứng đã bắt được ba lỗi nếu gom family bừa:13/21 dùng clampL không L−1;
20 super vẫn ghi angleDelta. Đã sửa model theo source và rerun, không nới expected cho qua.

**Full761 tests PASS49.228s**, datas validate PASS. Kết quả fixture không phải playtest,
không tạo DPS/frames/target-hit frequency từ cấu hình.

## 6. 24 implementation có consumer thật; bảy special paths không giả làm projectile wing

Contract giữ **85 vtable-entry178/188 load→BLR sites**, **83 sites có CFG must-owner receiver**
(bao gồm24 max-power getter gọi normal getter). Entry tương ứng abstract getter slot4/5 trong dump;
không gọi mọi indirect BLR trong class là wing damage.

Các consumer đặc biệt đã định vị bằng native, không thiếu nguyên implementation:

|impl|named consumer cần tiếp tục dịch đầy đủ|
|---:|---|
|2|UpdateParticle; OnParticleCollision/OnParticleCollision2|
|4|FindAndAttackEnemies; LevelUp range config|
|6|SetSizeSaw; OnCollision|
|8|SetSizeSaw; OnCollision và FindAndAttackEnemies|
|10|AttackNormal; AttackEnemy; HitEnemy; UpdateRange|
|12|AttackNormal/AttackSuper; FindAndAttackEnemies; SyncAttack/animation events; OnHitSuper|
|15|GunCheckEnemies; UpdateLaserPositions|

Hai sites chưa có must-owner proof tự động đều trong **GunCheckEnemies15** tại148e180/148e244:
owner đi qua `str x20,[sp,#28]`/`ldr x21,[sp,#28]`, slot stack này còn được reuse sau đó.
Bộ owner-analysis hiện tại không track stack. Contract giữ false rõ ràng; không đánh đồng nó với
“hai getter không biết nguồn” hay thiếu method bytes. Chưa nâng hai site này thành CFG proof giả.

Impl16 còn OnBulletNormalBoostedCollided/HitEnemy;18 có OnHeartCollision;19 AttackEnemy/HitEnemy;
21 callback `_1` — đều có owner-qualified dispatch trong contract. Không bỏ hết geometry/secondary
hit thành một OnBulletNormalCollided chung.

Source mapping theo report81:impl1=10003, impl3=10001; **impl2=10002 vẫn có proof raw prefix**
(id@byte32 của4 objects, hashes verified), dù particle-curve full typetree từng lỗi. Không biến lỗi
curve phía sau thành “mất cả ID”; cũng không đổi provenance thành full-tree parse thành công.

## 7. Góp ý và giao tiếp tục cho spec

- Nhập17 normal configs/index policies theo implementation, không copy luật impl1 sang23 tàu.
- Giữ rate floors14/16/19/21 và ngoại lệ super20; S/V input instance chưa được đóng bằng ctor.
- Không dùng `numberNormal` hay UI power làm DPS. Giữ các special consumer ở§6 riêng.
- Đã kiểm ACK92 đúng, không còn yêu cầu sửa ba wording cũ. Map/save named binding vẫn chưa
  được batch wing này trả lời, không đổi ledger sang DONE.
- **Chưa đóng toàn bộ23 wing firing laws:** phần đã đóng thêm là16 normal SetBarrels configs,
  array joins/index/super behavior; phần kế tiếp là Shoot/packet/coroutine consumers cho17 configs
  cùng7 special paths cụ thể ở§6. Không thiếu APK/raw/native nên không dùng “cần thiết bị” để né đọc.
