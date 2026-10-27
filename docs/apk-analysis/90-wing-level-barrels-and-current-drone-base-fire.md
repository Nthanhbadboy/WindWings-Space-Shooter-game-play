# 90 — Level → wing barrels; luật bắn của 12 implementation drone hiện hành

**Tạm thời, chỉ dựa APK đã pin.** Batch này đi liền getter/cache → cấu hình →
scheduler → thứ tự gọi projectile; thêm sweep4, laser7/9 và nguồn damage của drone.
Không dùng `Droid_Attack` đời cũ làm luật cho `Drone_Attack` hiện hành.

## 1. Evidence và kiểm chứng

Raw tại `reverse-engineering/raw/wing-drone/`: native ASM/JSON, RELA và các ô float
4/8/16 byte; liên kết raw combat-chain, field-defaults và dump.cs cùng APK.
Recovery40215280030/40215404409/40215598053/40215715389/40215827547 SUCCESS;
refresh cuối raw39b377383. XAPK SHA
`f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`;
lib SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.

`datas/wing_drone_flow.json`: **73 method ranges /6041 instructions,68 operand anchors,
44 numeric static fields**, byte provenance cho initializer,9 projectile-loop proofs,
2 InitializeArray field bindings và mẫu wing level0..10. Range count không đồng nghĩa
mọi method đã được mô phỏng toàn bộ physics/rendering.

`python3 -m tools.verify.wing_drone_flow --check` kiểm range, raw hashes, các operand,
RELA→Dumper field→SHA-named array, packed initializer và ô float thật. Models tại
`tools/verify/wing_drone_models.py`; **92 test mới**, full **592 PASS40.119s**;
`datas/validate.py` PASS. Fixture hữu hạn, không overflow int32; phép float dùng f32,
không suy Unity tick spacing/FPS, hit count hay DPS từ deadline.

## 2. Level không phải số cố định đọc từ prefab

`Player_Ingame.get_Level`14b1eb0 đọc static+4; giá trị−1 mới gọi
`Player_Get_Datas.GetStartPowerUpPoints`14e5404 rồi cache. Setter14b21d8 ghi thẳng,
không clamp. Getter trả−1 thì lần đọc tiếp vẫn có thể gọi lại nguồn.

Tech stat getter13999ac cho tier khởi đầu: tech≤2→0;3..4→1;5..6→2;7→3;≥8→4.
`UseItems[3]` true cộng3 rồi **xóa cờ trước khi gọi cap**. Cap14e553c đọc tech lần nữa:

```
cap = 6 + min(techTier + ability12 + 2*ability13, 4)
techTier = 0 nếu tech≤0; 1 nếu=1; 2 nếu2..3; 3 nếu4..5; 4 nếu≥6
startLevel = min(startTier + consumedItemBonus, cap)
```

Không tự thêm lower clamp. Fixtures kiểm getter đọc lại, cờ đã mất khi dependency
phía sau throw, và cache/setter độc lập với phép tính start.

## 3. Wing Player_Attack_1: getter → SetBarrels → Shoot

Phạm vi này là **implementation1/source10003** theo binding81; không đổi thành
source10001 và không áp công thức này cho 23 implementation tàu còn lại.

Ctor147c5f8 khởi tạo10 int:
`[3,4,5,6,7,8,9,12,13,14]`. Chuỗi chứng minh:
GOT2ae7c58→RELA effective2bd4568→private field
`0FBFBDF0559CFEAC3F82F3F97A7C5E7B63A7893DA11C14D91A8F2F1846B2D8B2`;
InitializeArray length10; SHA256 của **40 byte sử dụng** khớp tên field.
8 byte cuối raw blob48B là padding, không phải thêm2 phần tử.

SetBarrels147b3b8 reset `bCount` rồi đọc Level **hai lần** trước kiểm super.
Với Level ổn định:

```
index = L>2 ? trunc((L-2)/2)+2 : max(L,0)
index upper-clamped vào array
numberNormal = array[index]
```

Native dùng getter thứ nhất cho nhánh, getter thứ hai cho số học; fixture không
thay hai lần đọc bằng một. Super vẫn đổi number/reset count, nhưng **không đổi**
shotRate/speed/angle trong SetBarrels. Nhánh thường thêm2 getter đọc Level:

```
shotRate = f32(.12 + f32(L * -.0035))
speed    = min(f32(14 + f32(L * 1.1)), 42)
angle    = min(3*trunc(L/10)+5, 15)
```

| Level |0|1|2|3|4|5|6|7|8|9|10|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| numberNormal |3|4|5|5|6|6|7|7|8|8|9|

Level10: rate≈.085, speed25, angle8, number9. Không có rate floor ở đây;
không dùng level ngoài gameplay bình thường để bịa invariant rate dương.
Ctor normal(.12,14), super(.06,20), numberSuper20 được chứng minh bằng packed
q0@779b40 và store98. `numberSuper` là field riêng: không tráo với numberNormal.

Shoot147ad24 qua cả `timeToShot` và `timeToBarrelShot` với equality được qua.
Nó đặt `timeToBarrelShot = now + ((shotRate-.01)*.3)/10` — **mẫu số là độ dài
array10, không phải numberNormal**. Tăng bCount; chỉ khi **bằng** numberNormal mới
reset0 và đặt timeToShot=now+shotRate. Một packet có2 attempt thường hoặc3 super;
scheduler ghi trước emission, pool/component failure không rollback deadline.
Không gọi numberNormal là số projectile hit trong một frame.

StartAttack147b264: sau gates58/player28, `_isStart=true` xóa10c và đặt wing
BC=now+`31082c3e` (=f32 .168); false đặt main-cannon10c=now+a8, không cùng thao tác
BC. Gates/player2d và dispatch sau đó vẫn được giữ; không hiểu .168 là cadence
lặp lại. Main-cannon update80 vẫn là luật riêng, không gộp vào wing packet.

## 4. Nguồn cấu hình thật của drone hiện hành

GOT2adbd90 là **Drone_Get_Datas**, không phải legacy Droid_Data_Balance.
Initializer14dadc4 ghi44 numeric fields; verifier chạy đoạn numeric tail theo byte
ở từng store, gồm `dup`, packed double, MOV/MOVK và fmov vector.

Bảng dưới ghi giá trị cấu hình/ctor bằng decimal dễ đọc; raw bits trong contract:

| Implementation | shotRate | turn/chargeRate | turnNumber | speed / projectile |
|---|---:|---:|---:|---|
|1|.3|—|—|18 /80012|
|2|.1|.5|3|18 /80013|
|3|2|ctor8, **SerializeField**|3|24 /80014|
|4|3|**0 do OnEnable ghi**|3|sweep laser|
|5|.1|.68|5|18 /86001|
|6|.12|.12|1|25 /86005|
|7|attack.2|charge1|—|laser, ctor values|
|8|1|1|1|18 /86012|
|9|attack1.5|charge1.5|—|laser, ctor width10|
|10|.12|.12|3|25 /86013|
|11|.1|.68|1|18 /86017|
|12|1|1|1|18 /86022|

**Drone3 turnRate8 chỉ là constructor default**, không được nâng thành mọi prefab
đang chạy: field có SerializeField, OnEnable không ghi lại nó. Drone9 width10 cũng
là ctor default cho SerializeField. Hai timer laser7/9 không có SerializeField.
Bảng không phải mapping serialized sourceID→implementation/spawn: class suffix
không tự chứng minh source ID. Dữ liệu source-ID cần binding prefab/loadout riêng.

Ability25: Player_Get_Datas static348 tên **abi25AddDroneShotRate**, giá trị **2.5f**.
q3@779100 được store ở340; lane2 chính là348. Khi guard lần đọc đầu ability25≥1,
những rate mà từng OnEnable cấu hình lấy:

```
newRate = baseRate / f32(2.5f * ability25_read_again)
```

**Không phải** base/(1+2.5*point), không phải giảm2.5%. Native đọc point lại cho
mỗi rate được chia; không bắt getter thứ hai bằng getter đầu bằng giả định cache.
Families2/5/6/8/10/11/12 cấu hình cả turn và shot;1/3/4 cấu hình shot;3 không ghi
turnRate,4 ghi turnRate0. Không áp công thức này sang timer laser7/9.

## 5. Projectile scheduler: đếm từng barrel, không đếm volley

Base Fixed1468a94 chỉ Find khi isAttack và **now>timeToCheck**, đặt next=now+.5
trước Find. .5 là nhịp tìm target, không phải shotRate. Các projectile wrapper
đã qua isAttack gọi base rồi Shoot mà **không recheck isAttack sau base call**.

Family1 Shoot14695d4: qua now≥deadline, **ghi deadline trước** kiểm barrels null/
empty; giữ length rồi attempt mỗi barrel. Không có charge counter.

Families **2/3/5/6/8/10/11/12**:

```
if chargeDeadline > now: return
if now < shotDeadline: return
shotDeadline = now + shotRate
length = barrels.Length
for each captured barrel index:
    projectile attempt / optional component / activation
    count += 1
    if count >= turnNumber:
        count = 0
        chargeDeadline = now + turnRate
```

Không xét chargeDeadline lại giữa loop.2 barrel và turnNumber1 vẫn có2 attempt
trong invocation đã qua gate;3 barrel và turnNumber2 có thể kết thúc với count1.
Thiếu component theo nhánh skip vẫn tới counter; **exception trước counter thì
không tăng**. Null barrels throw sau deadline write; empty array tiêu deadline
nhưng không tăng counter. Callback adapter không hứa mọi pool call đều thành đạn.

## 6. Sweep4 và hai laser không thể thay bằng projectile loop

Drone4 Update146cdcc: isAttack mới Shoot; khi không shooting mới baseRotate.
Shoot146cdfc qua2 gate trước; chưa shooting thì set true/phase0 rồi return, không
xoay ngay. Đang shooting: MoveTowardsAngle ở **20×deltaTime độ**, ghi rotation rồi
chỉ khi **bằng targetAngle chính xác** mới đổi phase:

- arrival0 bật FX, target−16;
- arrival1 target+16;
- arrival2 target0;
- arrival3 target0, phase4 hoàn tất.

Start không tự reset targetAngle. Phase4 clear shooting, shotDeadline=now+shotRate,
tắt FX rồi tăng count; count≥turnNumber reset và ghi turnDeadline=now+turnRate.
Do OnEnable ghi turnRate0, không tự thêm cooldown8/.5 theo constructor lớp khác.
Model giữ việc re-read phase sau FX callback và check exact angle, không bỏ frame
khởi động hoặc phase quay về0.

Drone7 Fixed146e2e4 và9 Update146fa94 đều có outer isAttack guard, timer strict **>**:
activation equality chưa bật; deactivation equality vẫn attack. Lúc bật chỉ đặt
active/deactive deadline, **không AttackLaser ngay tick bật**.

-7: hết hạn thì clear actived, next=now+charge, **vẫn gọi AttackLaser** tick đó.
  AttackLaser gọi Check146e5d8; Check kiểm actived ở146e670 nên nhánh đã clear
  **không damage**. Không đổi câu này thành “hết hạn vẫn gây damage”.
-9: hết hạn clear actived/đặt next, hide hitPoint rồi return, không AttackLaser;
  inactive/equality chạy fade branch. FixedUpdate9 là RET, không tự chèn base poll.
-9 OnEnable146fa64 chỉ hide laser GameObject qua renderer a0; **không reset active
  hoặc timers**. Stop isAttack không tự clear timer trong các tick này.

Không lấy timeAttack/(attack+charge) làm DPS. Bộ raycast, hình học resize beam và
receiver collision còn là các method riêng; ở đây chỉ dịch đúng gates/timing.

## 7. Damage drone: bóc luôn nguồn số, không đoán hệ số

GetBaseDamage14da6f0 dùng `BaseDamages[sourceID-20001]`. Native cctor:
GOT2ae8a48→field `48C9657C06827BE5576FB588370BE769F2628E925BBEA0E0304A03E27C323AA4`
→InitializeArray12 float→static20.48 byte sử dụng khớp SHA field; raw56 có8 padding.
**Không nhầm x25/GOT2ae8a40**: đó là array UnlockNowCosts ởstatic18, không BaseDamages.

```
BaseDamages = [450,600,6000,135,935,315,650,1200,248,650,1200,2650]
scaled = (1 + .16f*GetDroneLevel(sourceID)) * BaseDamages[sourceID-20001]
rankExtra = rank1:0; rank2:.2; rank3:.35; rank4:.5; nhánh còn lại:.56
result = scaled * (1+rankExtra) * (1 + 2.5f*ability21)
```

Từng phép f32 theo thứ tự native, không gộp algebra rồi round cuối. rank=−1 gọi
GetDroneRank14d9f70; rank cụ thể bỏ call này. GetDroneLevel14da8ac vẫn gọi trước
array bounds. ability21 amount là **abi21AddDmgDrone static338=2.5f**, q2@779830 lane2.
Level coefficient raw`0ad7233e`=.16, không phải đoán .01. Rank fallback gồm cả
rank ngoài1..4, không tự clamp. Helper rank/level được giữ là explicit inputs của
fixture, không suy save schema hoặc giá trị live từ constructor. Skill damage và
Board consumer không được coi đã approve chỉ vì cùng class có method.

## 8. Legacy được tách riêng; handoff không tự đóng mọi gap

Legacy SpaceShooter.Droid_Attack14551dc/1455250 có magazine/round scheduler khác:
MagStart callback trước shot gate; shotTime>0 luân child hoặc luôn child0 tùy
countShots; shotTime≤0 phát N lần child0/toàn children/parent rồi audio một lần.
MagEnded ghi reload deadline trước callback, đọc lại countMags, equality mới kết
round. infinity chỉ bỏ callback round, **không bỏ round deadline**. StartSync clear
shot/reload/round/counters, không clear start gate/stun. Các fixture này được đặt
`LegacyDroidGun`, không trộn array5 damage legacy thành12 modern drone.

**Cho AI spec:** áp level/cache và wing1 đầy đủ§2–3; adapters cho9 projectile impl,
sweep4,2 laser và44 fields§4–7. Không đổi static numeric defaults thành toàn bộ
prefab/spawn/serialized source-ID mapping. Không lấy nhịp deadline thành damage/time.
Wing23 implementation còn lại cần dịch SetBarrels/Shoot tương ứng; raw ởcombat-chain
đã có, không gọi “thiếu dữ liệu”. Drone sourceID→prefab/loadout binding và serialized
turnRate3 là việc named consumer tiếp theo, không thiếu toàn bộ drone law.

Đã nhận **ACK88 comment6400582139 / ACK89 comment6400668714**, lưu raw peer-review.
Đây là peer tự báo đồng bộ, không phải đã độc lập review mọi file spec mới.
Comment6400762294 xin đọc HP writer: queue Start14c6b5c, ResetStaticVariables14c6ca0,
OnChangeDataDevice14c58ec. Không suy “mọi tàu chung HP” từ việc không thấy mảng tên HP;
phải đọc writer trước. Không merge/push nhánh peer. Chưa có ACK90 lúc viết report.

**Receipt90:** codebf4827ae2, Verify40216724849 SUCCESS (verify job43s); full592 local
PASS40.119s. Raw receipt và handoff comment6400835733 đã lưu trong wing-drone.
