# 85 — Callback → damage → HP → sống/chết, cả enemy và player

**Tạm thời; chỉ cùng APK đã pin.** Đây là bản dịch nhánh receiver, không phải
báo cáo inventory hàm, không phải đo DPS/TTK hay tuyên bố dịch xong toàn APK.

## 1. Nguồn và phần đã làm

- Raw cũ: `reverse-engineering/raw/combat-chain/native/` + dump.cs.gz + ELF
  referenced-cells/RELA/symbols. Không export lại full Analyze/media.
- Raw bổ sung: `reverse-engineering/raw/combat-receivers/`: hai lớp con trực tiếp
  của Enemy_Destroy trong dump (`Enemy_DestroyDelayed`, `MB_Destroy`), hai iterator,
  **Observer**.EventDispatcher/Extension, Player_Controller và các iterator của nó.
  Root export giữ cả dependency methods; **không nói mọi method mới đều đã dịch**.
- `datas/damage_receiver_flow.json`: **44 source walks, 3.485 instruction**, branch/call
  anchors, CFG must-value proof cho mọi GetNumberAbility ở các body được chọn,
  field identities và hai literal HP/burn. Có SHA cho từng nguồn.
- `tools/verify/enemy_damage_model.py`: giữ hàm arithmetic cũ, thêm receiver mutable
  qua cả hai callback. `damage_receiver_models.py`: enemy controller, base death,
  hai death coroutine, ability32 blast và player receiver tới extra-life/death.
- Hai test files mới: **48 checks** (42 model + 6 native/regen). Fixtures callback
  giả lập trường hợp hợp lệ của API, **không phải chứng cứ stage thực tế đăng ký
  chính những callback giả lập đó**. Model không chạy Unity/physics/render/audio.

## 2. Enemy: callback có thể đổi kết quả sống/chết

`Enemy_Sub.TakeDamage 1587ecc` → controller `1582938`: **Display.OnHit trước**
OnTakeDamage `1582ad4`, kể cả sau đó HP<=0 hoặc IsCaAttack=false bị gate.

Controller chỉ vào phần sau khi CurrentHealthPoint>0 && IsCaAttack. Có health object
hợp lệ và Damager không null thì gọi CalculateDamage. Ngược lại log lỗi **nhưng vẫn
đi UpdateHpBar**, không phải mọi null Damager đều return ngay như player.

`Enemy_Health.CalculateDamage 158479c`:

1. noDamage && !ignore → return; HP<=0 → return.
2. Armor>=0: `100/(100+armor)`; armor<0: `2-100/(100-armor)`.
   Binary32 từng phép; ghi `max(oldHP-requestedDamage*factor,0)` tại **1584808**.
   Không có gate requestedDamage>0; damage âm có thể tăng HP vượt startHP.
3. Load/invoke hitCallback tại **1584820**, nếu có. Không đòi loss>0.
4. **Sau callback**, load lại hitDamageCallback tại **1584824**. Nếu có,
   đọc lại HP qua ref argument **158482c**, tính oldHP-currentHP. Chỉ khi delta>0
   invoke callback thứ hai tại **1584854**. Callback đầu có thể heal, thay/xóa
   delegate thứ hai; callback thứ hai cũng có thể sửa HP lần nữa.
5. Ref argument giữ **data object đã truyền**. Nếu callback thay controller.dataScript,
   delta vẫn đọc object cũ; controller tiếp theo đọc dataScript hiện tại. Có test riêng.

Controller gọi **UpdateHpBar 1582bec trước đọc HP lại 1582bf8**; helper lấy
current/start rồi SetHpBar. HP còn dương → kiểm stun31 rồi burn34. Stun có rate>0,
`rate>=Random.Range(int 0,100)`, thời gian3. Burn rate>=100 hoặc rate>=float random;
copy **requested damage và killEvent** sang Damager mới, gọi Burn(interval=f32(.4),
arg6), không dùng observed HP loss. **noDamage không tự skip** các nhánh controller này.

HP<=0 → `OnDieWhenZeroHp 15846f8`: tắt cờ move@5c, IsInvisible=true, disable
collider, virtual Destroy(type0). **Sau khi dispatch trả về**, mới load lại
Damager.killEvent@18 tại **1582de0** và invoke với GameObject nếu có. Một destroy
callback có thể thay killEvent trước lần load này. Exception ở callback không bị
model nuốt; các bước sau không được tự coi đã chạy.

## 3. Death dispatch: base, delayed, MB không được gộp

### Base Enemy_Destroy.Destroy(0)

Virtual OnDestroyByZeroHp `15856cc` → **Pool luôn ở tail Destroy** `15815d0`
(nếu những lời gọi trước trả về bình thường).

- onDead@28 nếu có → load lại onDestroyed@20.
- onDestroyed null: skip burst/Destroyed/death events trong OnDestroyByZeroHp;
  vẫn quay về Destroy → Pool.
- onDestroyed có: invoke → OnBusrtItems → Destroyed → event19 OnEnemyDie → event79
  OnPoolEnemy. Sau đó Pool clear onDead và tự phát event79 một lần nữa.
  Đây là **hai lệnh PostEvent79** trên nhánh này, không phải chứng minh hai lần
  pool vật lý, hai kill hoặc listener xử lý hai lần.

### Enemy_DestroyDelayed

Destroy `15814a0` tạo coroutine; ctor đặt delayTime=2 **nhưng factory/MoveNext
không dùng delayTime để WaitForSeconds**. State0 gọi dieEventDelayStart nếu có,
then **WaitUntil** bằng wrapper `1581570` gọi **condition field hiện tại** mỗi poll.
condition null đi null-failure, không phải false. Resume state1 gọi thẳng base
Enemy_Destroy.Destroy(type đã capture). Table không có computed-BR.

Vì vậy controller.killEvent có thể xảy ra trước base OnEnemyDie/Pool khi điều kiện
chưa thỏa. Không được ép thứ tự base death đồng bộ lên lớp con này.

### MB_Destroy

Destroy(0) → override OnDestroyByZeroHp: onDead nếu có, StartCoroutine DieEffect.
Không có base Destroy→Pool tail. Bốn state được chốt bằng byte table **77a324**:
`00 14 27 3a` → `1574b8c / 1574bdc / 1574c28 / 1574c74`.

State0 activate efxDefeat → Wait1; state1 hide body → Wait1; state2 burst items →
Wait1; state3 Destroyed → ghi thời gian sống → event19 → event79 → finish.
Không biến ba Wait1 thành một frame timer hay thêm base Pool không tồn tại trong body.

### Ability32 trong Destroyed không chỉ là FX

`15850bc`: ability32>=1, chance=abi32Rate*level; >=100 bỏ random, còn lại dùng
chance>=float random. Amount từ **get_abi32Amount 14dbc84**, không phải incoming
Damager hay oldHP-currentHP. Physics OverlapSphere radius3, enemyLayer; rồi kiểm
collider/GameObject/layer mask, Obj_Collider.GetIHealth và GetIDamageable **không null**.
Không gọi IHealth.IsAlive ở đây. Tạo Damager mới(amount, killEvent=null), gọi
IDamageable.TakeDamage(ignore=false) tại **1585494**. Có thể vào lại receiver.

Body duyệt collider array, **không dedup cùng receiver**; fixture hai collider
cùng receiver có hai request. Đây không chứng minh một prefab/stage thực tế luôn
có hai collider, hay chắc chắn trúng/nổ dây chuyền.

## 4. Player: gates trước damage, hai lần truncate, events trước quyết định chết

`Sub_Player.TakeDamage 14c8390` tạo Action từ controller@30, metadata GOT
**2ae8550 → RELA 2bc83c8 → Player_Controller.OnDie 14c27f8**, rồi gọi health.
Sub_Player.SetDieCallback và Destroyed đều RET; không áp cơ chế onDead enemy sang player.

`Player_Health.TakeDamage 14c6de4`, finite normal path:

1. CurrentHealth>0, !invisible@49, Damager!=null, !IsVictory.
2. Invincible && !ignore: ability30 có thể gọi interface IHealth heal;
   chance equality được nhận; amount=(abi30Amount/100*level)*GetStartHealth.
   Sau nhánh này return, không tiếp tục lấy damage. ignore không bỏ các gate khác.
3. Player_Attack.IsInvisible: rank@44>=5 và now<=timeToVisible@34 mới true.
4. **immuneDeadline < now: cập nhật now+TimeToImmuneOneHit rồi RETURN bỏ hit**.
   Deadline bằng hoặc lớn hơn now mới đi damage path. Giữ nguyên nhánh native,
   không đảo nó theo cách hiểu tên “immune”. Hai Time.time reads riêng.
   Getter dùng TechStatLevel(index0): <1 FLT_MAX;1..3=50;4..5=45;6=40;
   7..8=35;9=30;>9=25. Đây là khoảng lần bỏ hit này, không phải bằng chứng player
   bất tử trong toàn khoảng. Player_Attack.SetInvisible là cơ chế khác: rank>=5,
   gate cooldown@48/statics@c, ghi deadline now+2 và có animation coroutine.
5. Dodge8: base coefficient*level; nếu HP/startHP < **f32(.3)** thêm bonus22;
   cap90; **chance>float random** mới Miss. Dodge trước shield, nên miss không ăn shield.
6. ShieldOneHit: clear flag31 **trước invoke callback đã load**, rồi return.
7. Ability28: now>timeToClear → timeToClear=now+1, effect99005. Ability35 virtual
   hook sau đó; requested damage và armor/device được load **sau hook**.
8. `damage-device*damage` → armor factor như enemy → **FCVTZS #1 14c7418**.
   Multiplier=max(`1-abi9ReduceREDDmg*n9-abi10ReduceREDDmg*n10`,0), nhân float của
   int thứ nhất → **FCVTZS #2 14c74ac**. HP=max(currentHP-float(finalInt),0),
   store **14c74e8**. Ví dụ3.8 và reduction.2 → truncate3 → truncate2,
   không phải truncate3.04→3. Negative request có thể heal không cap ở path này.
9. Post **21 OnPlayerUpdateHp với boxed HP tại thời điểm dispatch**, rồi
   **39 OnPlayerTakeDamage**. Extension gọi Observer dispatcher; dictionary lookup
   lấy Action<object>, **tail invoke đồng bộ 14347f4**, không phải queue frame sau.
10. **Đọc lại static HP tại14c7530**. Event handlers có thể đổi HP; payload21 đã box
    không tự đổi theo HP mới. Còn HP>0 gọi Player_Attack.SetInvisible; HP<=0 vào death.

Native có compare +Infinity và FCSEL -2147483648.0 ở **cả hai** conversion chains,
ngoài FCVTZS saturation semantics. Model giới hạn finite intermediate/in-range int;
validation model không phải native reject input, không tuyên bố emulation FPCR/NaN/Inf.

## 5. Player death và extra-life

Death effect91005/audio58 → **pvpLife-- trước chọn nhánh**. Nếu mode6 && pvpLife>=1
hoặc ability16>=1 && ability16>rebornNow (nhánh sau tăng rebornNow), gọi onExtraLife
nếu có rồi return. Null onExtraLife vẫn return: không tự fallthrough death.
Ở nhánh này không ghi isAlive=false, không gọi onDie và không phát event18 tại đây.

Ngược lại ghi isAlive=false tại14c76ac → invoke onDie **bắt buộc** tại14c76c0
(null đi failure, không im lặng skip) → cleanup invoke/tween/particle → event18
OnPlayerDie với transform payload. Player_Controller.OnDie đã recover: clear move
flag, gọi attack virtual teardown, StopAllCoroutines, tắt hai child objects và particle
systems; không lấy death event làm measured game-over timestamp.

Player_Controller.Start còn có site ghi delegate health.onExtraLife tại **14c20b4**;
OnExtralife body chọn mode6 DoExtraLifePVP, còn lại coroutine DoExtraLife. Hai body
đều gọi **Player_Health.GainHealth(1)** sớm; coroutine normal sau đó dùng WaitUntil,
không phải “HP=full ngay khi zeroHP”. Các dependency này đã giữ raw, không ghi
“missing raw/requires runtime”. Exact metadata binding của GOT2ae8480 mới ở site
Start và toàn lifecycle heal/rewire là phần join tiếp, không đổi kết luận thứ tự HP
receiver ở trên. Callback fixture vẫn là input, không tuyên bố mặc định luôn null.

## 6. Nghiệm thu và bàn giao

- `python3 -m tools.verify.damage_receiver_flow --check`
- `python3 -m unittest tests.test_damage_receiver_models tests.test_damage_receiver_flow -q`
- Chạy full suite + datas/validate.py; receipt trong
  `reverse-engineering/raw/combat-receivers/derivation.json`.
- Recovery lần đầu40209828584 fail do masked parser tái dùng giữa exports; reload
  parser sửa ở42951b7ed,40209963114 success. Sau đó bắt trùng tên Unity
  UIElements.EventDispatcher, filter **namespace Observer**, chỉ xóa hai artifact
  trùng do phiên này sinh. Recovery cuối **40210107165 SUCCESS**, raw220fa2d53.
- Sửa đúng một typo report84 recipe7: **return arrival .5**, outbound vẫn .1.
  Regenerate JSON + provenance; không mở lại cả25 coroutine thành “chưa dịch”.
- Tiếp theo: join producer callback/serialized receiver với entry points đã dịch,
  và hoàn thiện extra-life/heal rewiring từ raw mới. Không nâng dynamic delegate
  fixture thành subscriber thực tế, không suy DPS/TTK từ số dispatch/test pass.
