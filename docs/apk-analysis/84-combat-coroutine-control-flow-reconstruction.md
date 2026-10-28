# 84 — Dịch control-flow đủ 25 combat coroutine; đóng ledger timer/yield của83

**25/10/2026 — tạm thời, APK-native source walk.** Không thêm một inventory-only vòng nữa:
đã đọc các nhánh entry/resume/exit của đủ **25 MoveNext** và nối thêm hai delegated iterator, phân vai emitter/control/
transform/particle, giải **3 computed BR**, nối nguồn **14 wait sites** và làm mô hình
control có thể chạy để regression. Không tuyên bố đã dịch xong toàn bộ APK/game.

## 1. Artifact dùng được và provenance

- `datas/combat_coroutine_flow.json`: 25 bản dịch control-flow, fields đúng metadata,
  state/current stores có context, branch edges, direct/indirect call sites,
  native anchors cho các điểm dễ đọc sai và 7 factory parameter-copy bodies/callers.
- `tools/verify/combat_coroutine_models.py`: executable control reconstructions của
  10/11/12/13/14/17/18/23/24 và7/9; đầu ra phân biệt **helper dispatch / wait / frame /
  callback / particle setting**. Helper dispatch không tự là projectile hay hit.
- `tools/verify/combat_coroutine_flow.py`: tái sinh bằng raw, không chỉnh asm. Semantics
  là source walk có anchors, **không giả làm bằng chứng decompiler-equivalence**.
- `reverse-engineering/raw/combat-chain/coroutine-jump-tables.json`: bổ sung đúng **9 byte jump-table** cùng20 byte delegated literal cells
  lấy từ lib SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`
  trong XAPK SHA đã pin. Collector chỉ đọc năm cell, không chạy full Analyze/dumper/media.
  Recovery **40208240352 SUCCESS**, raw commit `23b1ceec3`.
- JSON hash từng raw/factory/model input. Raw cũ không sửa; chỉ thêm jump-table receipt.

```sh
python3 -m tools.verify.combat_coroutine_flow --check
python3 -m tools.verify.combat_rate_consumers --check
PYTHONPATH=/home/user/test-deps python3 -m unittest discover -s tests -q
python3 datas/validate.py
```

## 2. Hai lỗi diễn giải đã loại, một chỗ dễ đếm nhầm

### 2.1 7/9: không được đọc state theo thứ tự số hoặc theo vị trí code

|Table|Bytes|State→landing của implementation7|
|---|---|---|
|`0x77a07d`, 4 byte|`00 11 21 25`|dùng riêng6: base`0x14b3da8` + byte×4|
|`0x77a081`, 5 byte|`03 09 89 00 00`|0→`0x14b6314`;1→`0x14b632c`;2→`0x14b652c`;3/4→`0x14b6308`|

Implementation9 dùng cùng table5 byte nhưng base`0x14bb02c`. Đã đối chiếu ADRP+ADD,
ADRx10, LDRB theo state, ADD shifted2 và BR; không đoán target theo block gần đó.

**State0 chạy pha attack, không chạy `_delay` trước.** Attack tiến tới `_target`
(speed6 rồi4 sau trigger khi khoảng cách<1), yield null state1 khi còn di chuyển.
Tới khoảng cách<=0.1 → Wait(f32(0.35)) → state2 → nếu `_delay>0` mới Wait(_delay)
state3 → quay về owner (24×deltaTime), yield null state4; tới khoảng cách<=0.5 thì
PoolObject và gọi `_ended`, kết thúc. Factory9 có code copy args nhưng không có
**direct caller trong corpus preserved**; không bịa lịch gọi nó ở encounter.

### 2.2 18 IESpawnHeart: tên không phải semantics

`get_emission`@`0x27c2208` và `EmissionModule.set_rateOverDistance`@`0x27c2564`:

```text
cache particle.emission
loop:
    rateOverDistance = 2
    yield WaitForSeconds(0.5)   # state1
    rateOverDistance = 0
    yield WaitForSeconds(1.0)   # state2 → loop
```

Không có PoolingManager.GetObject, bullet setup, damage call hay indirect call trong
MoveNext này. Vì vậy câu hỏi “heart spawn loop” ở83§6 đã được **đổi thành particle
emission toggle**, không giữ như một projectile-spawn limitation chưa biết.
Không suy rộng thành mọi hiệu ứng của particle trong engine đều đã phân tích.

### 2.3 17: chờ sau **cặp**, không chờ sau từng vị trí

Native `i % 2 == 1` ở `0x14961bc..0x14961d0`; chỉ nhánh này vào wait ctor`0x1496214`.

```text
for i in saved_positions:
    dispatch_emitter(i)
    if i is odd: yield WaitForSeconds(f32(0.2))   # state1
# kể cả mảng rỗng
yield null                                      # state2
clear saved_positions; finish
```

N vị trí cố định → floor(N/2) wait0.2, một terminal frame yield; **không** N wait0.2.
Một helper dispatch vẫn có thể không có object/receiver hợp lệ, không biến N thành hit.

## 3. Đóng đủ 14 wait sites: nguồn và ý nghĩa

|Implementation / ctor site|Nguồn argument đã nối|Yield/resume dùng làm gì|
|---|---|---|
|6 `0x14b3dd8`|`_delay` iterator@0x20; factory`0x14b3220` copy s0→s8→field; MainCannonAttack gọi với index×f32(0.2)|delay **ban đầu** trước điều khiển object có sẵn; khác7/9|
|7 `0x14b655c`|`_delay`@0x34; factory`0x14b5818` copy s3→s8→packed store@0x30|delay **sau attack hold**, trước quay về|
|7 `0x14b67ac`|pool`0x756b0c`: `3333b33e` =0.3499999940395355|attack arrival hold →state2|
|9 `0x14bb280`|`_delay`@0x34; factory`0x14ba730`, cùng parameter copy7|sau attack hold, không phải initial delay|
|9 `0x14bb4d0`|cùng pool`0x756b0c`|attack arrival hold →state2|
|10 `0x147fc4c`|immediate0.25|sau mỗi round, **kể cả round cuối**, resume tăng i|
|11 `0x1482948`|`<rate>5__5`@0x38; init từ packed pool`0x757918`: .04 +35|sau một pass qua3 Barrel descriptors, trước kiểm deadline tiếp|
|12 `0x1486db8`|pool`0x75700c`: `cdcc4c3e` =.20000000298023224|**trước** side-dependent sync dispatch, không loop theo wait|
|13 `0x148a228`|`<rate>5__5`@0x38 ← `FMINNM(owner.shotRate/number,.05)`|sau mỗi cặp barrel-side dispatch; number là factory arg|
|14 `0x148d208`|`_delayCallback`@0x34; factory`0x148a910` copy s1; main launch5.5, return/OnDisable0|sau khi đến target mới chờ, sau resume state2 mới callback|
|17 `0x1496214`|pool`0x75700c`, .2|chỉ sau index lẻ, không từng index|
|18 `0x1499b50`|CFG chọn0.5/state1 hoặc1/state2, đã nối particle setters|on/off particle rateOverDistance|
|23 `0x14a7170`|owner.`shotRate`@0xac / float(Transform.childCount)|sau ShootBasicBullets cho từng child, không dùng arg`number` làm mẫu số|
|24 `0x14a92bc`|cùng field/callee như23|cùng timing nhưng helper implementation24|

23/24: kiểm childCount trước GetChild mỗi lượt; **sau helper**, đọc shotRate rồi gọi
childCount lại để chia. Đây không phải snapshot count đầu vòng. Không thêm guard
mẫu số0 vốn không có; helper làm đổi hierarchy có thể ảnh hưởng wait tiếp theo.
Wait sau child cuối vẫn tồn tại, resume sau đó mới kiểm vòng và kết thúc.
Factory copy `idBlt,number` vào iterator@0x28/0x2c; `number` chuyển tiếp tới
ShootBasicBullets@`0x14a5a84`/`0x14a8178`, **không phải** childCount.

## 4. Bản dịch control-flow đủ 25 bodies

Mỗi entry dưới đây có nguyên native body đã preserve, fields/RVA/anchors/edges trong
JSON. “Đủ25” ở đây là đủ control roles + yield/resume/exit của corpus25, không phải
khẳng định mọi phép toán của mọi helper trong game đã dịch thành project C# chạy được.

### 6.ControlMainCannonBullet — `0x14b3cf4`

**existing_projectile_control** — State0 optionally yields Wait(_delay)>0 to state1, then initializes enemy exclusion list. Per-target search/reselection uses radius10 or20 based list emptiness, owner.GetEnemy and live object tests; movement toward selected enemy at15*deltaTime yields null state2; fallback movement at12*deltaTime toward saved endPos yields null state3. Resumes reset state and continue control/reselection. On invalid/arrived target increment index, clear enemy, repeat while index<owner.numberTargets and breakList is false; otherwise PoolObject and return false. Operates on passed _bltObj, not a repeated pool-spawn loop.

### 6.SawAppear — `0x14b43c0`

**one_frame_saw_setup** — State0 clears saw-hidden flag, activates saw GameObject, detaches parent, sets owner rotation-speed bits to float600, calls SetSizeSaw and assigns scale(size,size,1). Yield null state1 once; state1 finishes. Not an interpolation loop.

### 6.SawHide — `0x14b44c8`

**one_frame_saw_setup** — State0 sets saw-hidden flag, reparents saw to owner transform, clears rotation speed, scale=(0,0,1), yields null state1 once then finishes. No SetActive(false) call in this body.

### 7.ControlMainCannonBullet — `0x14b6284`

**existing_projectile_control** — State0 initializes attack=false/speed6 and starts attack movement toward _target, null yield state1; state1 resumes attack movement. Within distance<1 set attack=true/speed4 and Animator.SetTrigger once. At distance<=0.1 yield Wait(f32(0.35)) to state2. State2 optionally Wait(_delay)>0 to state3, then return toward owner at24*deltaTime, null yield state4. States3/4 enter return path; when within0.1 call PoolObject then required _ended, finish. _delay is AFTER attack, not initial: exact byte table proves state0 != state2.

### 8.SawAppear — `0x14b938c`

**one_frame_saw_setup** — Same saw appear control as6: activate/detach/set rotation speed600/SetSizeSaw/scale, yield one null then complete.

### 8.SawHide — `0x14b9494`

**one_frame_saw_setup** — Same saw hide control as6: hidden flag/reparent/rotation0/scale(0,0,1), one null yield then complete, not GameObject deactivation.

### 9.ControlMainCannonBullet — `0x14bafa8`

**existing_projectile_control** — Same control topology as7 after address normalization: state0 attack init,1 attack loop; arrival Wait(0.35)→state2, then optional _delay→state3, return loop null→state4, PoolObject+ended on owner arrival within0.5. _delay factory exists but has no recovered direct call site in preserved methods; do not invent an external invocation schedule.

### 9.ShipCloneAttack — `0x14bb558`

**clone_launch** — State0 gets pooled clone, activates and positions/scales/orients it, sets damage field from rank multiplier and virtual damage getter, resolves Player9_Clone and calls StartAttack(duration from statics), yields null state1; state1 completes. Clone firing loop is in Player9_Clone, not repeated in this iterator.

### 10.AttackMainCannon — `0x147f40c`

**emission_loop** — On entry choose 1/2/3 rounds for rank<3/==3/>3, initialize ignored-enemy list and i=0. Each round acquires enemy via GetEnemy(radius=20), runs target/fallback emitter branch, then yields Wait(0.25), including after last round. Resume increments i; stop when i>=rounds.

### 10.IEUpdateRange — `0x147fcd0`

**scale_animation** — States0/1: compare squared scale distance to pool epsilon; if close return false. Otherwise set localScale=Lerp(current,scale,Clamp01(deltaTime*8)), yield null to state1 and repeat. No emitter call.

### 11.IEMainCannonAttack — `0x148236c`

**duration_emission_loop** — Entry builds 3 Barrel descriptors; packed fields id=88017,maxRdAngle=20,rate=f32(0.04),bulletSpeed=35. EndTime=Time.time+(rank<3?f32(0.4):rank==3?1:f32(0.6)). Before each pass test now<EndTime; emit over descriptor array, yield Wait(rate), resume state1 and recheck deadline. No catch-up pass after deadline.

### 12.SyncAttack — `0x1486c8c`

**delayed_emission** — State0 yields Wait(f32(0.2)) BEFORE emission. State1 tests _isLeft and matching live bullet/root lists, aborts normally when empty, otherwise executes side-dependent sync emission branch; returns false. No repeated 0.2-second firing loop.

### 13.IEMainCannonAttack — `0x1489664`

**launch_moving_objects** — State0 uses rank-indexed parentPoints, records child positions and launches pooled main objects with MoveObject(speed=8) and callbacks; then yields null state1. State1 finishes. Movement and later callbacks are separate from this one-frame launcher.

### 13.MoveObject — `0x1489b20`

**movement_callback** — Entry sets startSlow=Time.time+1. States0/1: if speed<=0 or XY distance<=0.5, invoke required callback(objMove), return false. Otherwise MoveTowards 3D target by speed*deltaTime. After startSlow, speed=max(speed+timeScale*negative_literal,0); yield null state1 and repeat. XY arrival and 3D movement are distinct.

### 13.ShotAllBarrels — `0x1489df0`

**paired_emission_loop** — Entry computes width=owner.localScale.x/number, speed=4, rate=minNumber(owner.shotRate/number,f32(0.05)), i=0. While i<number, run two barrel-side emitter paths, yield Wait(rate); resume increments i. Wait also follows last pair; main rate is NOT the wait field. Division precedes loop guard; no invented zero clamp.

### 14.IEMainCannonAttack — `0x148cae0`

**launch_moving_objects** — State0 snapshots child positions from parentPoints[min(rank-2,2)] (no lower clamp), launches pooled objects and MoveObject; main launch call passes delayCallback=5.5. Yield null state1 then finish. Do not attribute delayCallback to the launcher yield.

### 14.MoveObject — `0x148cfa0`

**movement_delay_callback** — States0/1 move _objMove toward live _target.position at _speed*deltaTime, yielding null state1 while outside XY threshold0.5. On arrival yield Wait(_delayCallback) to state2. State2 invokes required _callback(_objMove), then completes. OnDisable/return callbacks construct this with speed12 and delay0; main launch delay5.5.

### 15.IEUpdateRange — `0x148fd98`

**scale_animation** — Same scale update/control topology as implementation10: states0/1, squared-distance epsilon, Lerp Clamp01(deltaTime*8), yield null; no timed projectile emission.

### 15.UpdateLaserPositions — `0x148ff0c`

**laser_transform_update** — Entry duration=Time.time+1. Before each update pass test duration>now. For each live laser/root pair, apply hold-dependent Euler/attack-point orientation then copy root position to laser; yield null state1, repeat until deadline. No WaitForSeconds and no spawn in this MoveNext.

### 17.IEMainCannonAttack — `0x1495be4`

**staggered_emission** — Entry snapshots rank-indexed child positions and initializes id88029. Iterate position array: run emitter branch; only ODD zero-based indices yield Wait(f32(0.2)) state1. Even indices increment and continue in the same MoveNext: pairs are emitted before each wait. Resume increments index. After array completion yield null state2; state2 clears stored array and completes. Empty array still reaches terminal frame yield. Do not omit final null yield.

### 17.RotateClamp — `0x14962a0`

**rotation_oscillator** — Entry initializes angle6,max7,step0.1,signedStep0.1 and Euler storage. Per resume use Time.timeScale (NOT deltaTime), add signedStep*timeScale, clamp to7 or0, flip sign at endpoint; apply opposite offset for first clamp and positive offset for later clamps atop stored base angles. Yield null state1 forever unless exception/cancelled; no firing timer.

### 18.IESpawnHeart — `0x1499a44`

**particle_emission_toggle** — State0 caches ParticleSystem.EmissionModule. States0/2 set rateOverDistance=2, yield Wait(0.5) to state1. State1 sets rateOverDistance=0, yields Wait(1) to state2. Repeat. This body does NOT call GetObject, projectile setup or enemy damage: name SpawnHeart does not establish bullet spawning.

### 23.IEMainCannonAttack — `0x14a6894`

**launch_moving_objects** — State0 snapshots rank-indexed parentPoints children, runs pooled-object setup, movement/tween operations and callback registration; yields null state1 once, then completes. Separate IEShootBarrels is the timed child emitter; do not attach that wait to this launcher.

### 23.IEShootBarrels — `0x14a6ff4`

**live_child_emission_loop** — Entry i=0. While i<owner.barrel.childCount (read live each round), GetChild(i), call ShootBasicBullets(child,idBlt,number,callbacks), reread childCount AFTER helper, yield Wait(owner.shotRate/float(childCount)); resume state1 increments i. Wait after final child also happens. number is forwarded emission argument, NOT wait denominator.

### 24.IEShootBarrels — `0x14a9140`

**live_child_emission_loop** — Same child traversal/timing as23, but helper is implementation24 ShootBasicBullets. Live count reread after helper; number forwarded, not denominator. No rate-field@0x9c read in this wait path.

## 5. Khóa scope bằng tên phương thức, không dùng “phải chờ runtime” chung chung

### Đã đóng trong chuỗi82→83→84

- 72 stat getter arguments;24 main-rate formula→demo field→deadline→dispatch;
  23 extra-counter schedulers và exception19;22/23/24 live ability refresh.
- **Toàn bộ25 MoveNext control/yield flow của corpus player attack**, gồm14 wait origins,
  ba computed dispatch, frame-vs-wait, initial-vs-post-attack delay, final yields,
  grouped emission17, callback timing14, particle toggle18.
-7 parameter factories đã pin byte copy và direct callers, không bịa factory9 được gọi.

### Ranh giới helper còn nguyên, không biến thành “đã dịch cả game”

Không dừng ở ranh giới hai delegated class: đã recover thêm **Player9_Clone,
Player23_Pumpkin và hai nested iterator**, **30 methods** có raw/metadata, không capped;
đã kiểm contiguous instructions và clip đúng next global RVA (kể cả Dispose/RET8-byte
export overlap). Raw tại `reverse-engineering/raw/combat-delegates/`, commit`d9fc84c3d`;
exact literal bổ sung commit`158425a47`, recovery **40209189621 SUCCESS**.
Không full Analyze/dumper/media; chỉ export bốn class từ binary SHA đã pin.

### Player9_Clone — đã nối launcher → Update/Shoot → StopAttack → Pool

- `StartAttack`@`0x1470d68` bật isAttack và StartCoroutine(DelayPool(duration));
  **không reset timeToShot**. Update chỉ Shoot(numberNormal) khi isAttack.
- Shoot: finite now>=timeToShot → deadline=now+shotRate; vòng numberNormal lượt,
  fixed pool ID **88020**, không dùng parameter idBlt để thay pool index.
- Ctor numberNormal=6; packed cell`0x7581d0` bytes`9a99193e00009041` →
  shotRate **0.15000000596046448**, speed**18**. Đây là ctor values, không tự là
  encounter cadence nếu field/lifecycle bị đổi.
- DelayPool: Wait(duration) state1 → StopAttack (clear isAttack, animator trigger) →
  Wait(**0.3400000035762787**, cell`0x756aa4` bytes`7b14ae3e`) state2 → PoolObject.
  Không gộp thời điểm ngừng bắn và thời điểm trả pool.

### Player23_Pumpkin — đến target, active window, callback, Hide

- `StartAttack`@`0x14dc390` tạo IEStartAttack, copy start/target/callback đầy đủ.
  State0 set position=start;0/1 MoveTowards target với8×deltaTime, yield null state1
  đến khi squared 3D distance<pool epsilon≈1e−10.
- Đến target mới đặt timeout=now+**duration4**. Ctor cell`0x7572e0`
  bytes`000000400000803f` → timeAttack**2**, timeCharge**1**.
- Trước mỗi frame active-window: nếu now>=timeout thì gọi optional callback(GameObject),
  sau đó Hide. Hide có effect pool ID**91105**, rồi pool chính object.
- Nếu now>timeToCheck: gọi FindAndAttackEnemy, đặt nextCheck=now+**0.5**.
- actived=true: khi now>timeToDeactive, clear actived và nextActive=now+timeCharge;
  **vẫn gọi AttackLaser trong nhánh ấy**. Inactive và now>timeToActive thì bật actived,
  nextDeactive=now+timeAttack; nhánh vừa bật không lập tức gọi AttackLaser trước yield.
- Sau logic trên RotateToTarget rồi null yield state2. **Không có WaitForSeconds**
  trong IEStartAttack này: laser timing là deadline checks theo frame.
- AttackLaser gọi Check trước các visual gates; **Check tự kiểm actived** và return
  nếu false. Không suy một lần gọi AttackLaser thành một damage request/hit.

JSON chứa source-walk hai delegated behaviors, mọi method span/call/branch và literal
bytes. Models có regression stop-vs-pool, strict >activation/deactivation và callback
trước Hide. Pumpkin branch fixture dùng một timestamp cho các sample trong một lượt;
native gọi Time.time nhiều lần riêng, không giả fixture là clock simulator.

Các event `ShootBasicBullets`, IBullet setup, GetEnemy/TargetCanAttack, callback,
PoolingManager giữ đúng call boundary/raw_ref. Model control không dựng giả nội dung
helper hoặc tính projectile/hit/DPS từ event. Callback-specific enemy HP re-read chain
(report82) là task khác, không giấu vào ledger25 này. Encounter simulation vẫn cần
stage/loadout/schedule cụ thể, không cần chúng để dịch các body đang có.

## 6. Verifier và kiểm thử không tô hồng kết quả

- CFG giữ hai conditional edges; 3 BR phải có byte-table targets nằm trong method.
- Alias của iterator qua spill stack implementation23 được kiểm save@`0x14a69c4`
  dominates reload@`0x14a6f58`; không có bất kỳ SP use/adjust/escape giữa hai chỗ.
  Không bỏ mất state/current stores chỉ vì iterator không ở cùng register cả hàm.
- Models là executable **control reconstructions**, không đầy đủ Unity/IL2CPP;
  chỉ wait/frame events đánh dấu Unity suspension, helper events không phải yield
  gameplay. Float32 literals giữ bytes; test không chứng minh FPCR/lifecycle/collision.
- Đã chạy **327 tests PASS**, datasvalidate và diffcheck PASS. Code **58ef9809a**, Verify **40209405979 SUCCESS** (37s);
  regenerate-map/pinned dependency/regression steps đều PASS.
- Có25 tests mới: pair17/terminal frame, live denominator23/24 (kể cả0), post-attack
  delay7/9, wait-before-emission12, final wait10, particle-vs-projectile18,
  factory9 không caller, computed tables, iterator spill proof và bốn delegated behavior tests.

**Không show file/diff/preview, chỉ bàn giao bằng chat theo yêu cầu.**
