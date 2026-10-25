# 81 — Gói combat theo chuỗi: 24 implementation tàu → bullet → callback → damage/HP

**Tất cả kết luận tạm thời.** Gói static reference + bounded models, không chạy Unity,
không chứng nhận all-ship DPS/TTK/playback hay render. Mục tiêu là một gói bàn giao có
coverage và rule nối được, không thêm một báo cáo chỉ về một hàm.

## A. Phạm vi và công cụ

- Raw `reverse-engineering/raw/combat-chain/`: toàn bộ family `Player_Attack_1..24`,
  nested coroutine/display classes; họ Bullet/Homing/Rocket; Obj_Collider, Damager,
  các Sub receiver, Enemy_Controller/Health/Destroy, Player_Health và lookup/GP_Datas.
- Final recovery **40205786566 SUCCESS**, collector39b0b664a, rawbot99ba44829.
  Các lần recovery cùng batch bổ sung symbolic/GOT/source joins; không republish media.
- Pinned XAPK/native/metadata hashes trong index; SHA dump và hash từng file được verifier kiểm.
- Il2CppDumper6.7.46 tạo script/dummy output rồi **exit−6 ở Console.ReadKey do stdin closed**.
  Raw symbols lưu logtail nguyên, cả warning protected/search và địa chỉ registrations.
  Không nói process decoder exit0: workflow chấp nhận output tồn tại, verifier kiểm
  SHA inputs, RVA/declarations và critical joins. Không coi warning này là chứng minh APK protected.
- Lần40204984803 fail ở validation sau capture (áp kiểm native `methods` lên component-index).
  Sửa6d8b587b4; final recovery thành công và index hiện hành băm đủ raw. Intermediate output
  không được dùng thay final manifest. Full Analyze/media/release không chạy.

## B. Coverage đã kiểm, không biến coverage thành semantic approval

| Hạng | Số |
|---|---:|
| classes | 123 |
| methods | 1563 |
| ships | 24 |
| capped | 0 |
| unclean | 38 |
| clipped | 132 |
| components | 4133 |
| component_errors | 5 |
| direct_sites | 13144 |
| indirect_sites | 622 |

- 498 candidate GOT cells nối được qua ELF RELA→symbolic usage. Candidate collector chỉ
  theo ADRP/LDR sơ bộ, không là toàn bộ register-liveness/dataflow proof. Các critical joins
  §D được đối chiếu instruction cụ thể; không nâng toàn498 candidates thành executed uses.
- 1419 source component→m_OPScript entries; 1623 Obj_Collider roots.
- 5 source exceptions: 1 known builtin script-header resource580792; 4 Player_Attack_2 full
  typetree EOF. Giữ raw bytes/GO cho cả4, **không dựng full tree giả**.
- 101 attack components đọc đủ có rawprefix ID@32/demo@40 khớp tree100%; prefix4 source
  lỗi decode riêng với empty-name header@28 được kiểm. Đây chỉID/demo, không phục hồi suffix.
- 0 size_capped không phải mọi method boundary đều exact: 38 ends_clean=false giữ nguyên;
  132 minimum-span/shared-boundary overlaps được clip bằng next-declared-RVA khi dựng call sites.
- Direct call graph là inventory địa chỉ, không timeline; indirect sites còn là unresolved
  mặc định trừ từng đường đã đối chiếu bên dưới. Không tuyên bố đọc nghĩa xong mọi1550+hàm.

## C. Bảng nối nguồn cho cả 24 implementation

**Hậu tố class ≠ ID tàu.** Native rate lookup dùng constant argument thể hiện trong bảng;
sourceID lấy từ parsed script identity + serialized component, không từ tên gallery.
Đặc biệt implementation1 sourceID10003/array0 và implementation3 sourceID10001/array2.
Không dùng `id−10001` để gán mù chỉ số combat từ ID serialized; công thức đó ở consumer
save/load khác vẫn có thể đúng tại scope riêng. Không suy gameplay roster từ preview/demo.

| Implementation | Source IDs | Native rate-index (CFG proved82) | Family method records | Source scope |
|---|---|---|---:|---|
| Player_Attack_1 | [10003] | [0] | 28 | full parsed snapshots |
| Player_Attack_2 | [10002] | [1] | 27 | prefix only (4 EOF) |
| Player_Attack_3 | [10001] | [2] | 28 | full parsed snapshots |
| Player_Attack_4 | [10004] | [3] | 28 | full parsed snapshots |
| Player_Attack_5 | [10005] | [4] | 23 | full parsed snapshots |
| Player_Attack_6 | [10006] | [5] | 48 | full parsed snapshots |
| Player_Attack_7 | [10007] | [6] | 34 | full parsed snapshots |
| Player_Attack_8 | [10008] | [7] | 43 | full parsed snapshots |
| Player_Attack_9 | [10009] | [8] | 40 | full parsed snapshots |
| Player_Attack_10 | [10010] | [9] | 50 | full parsed snapshots |
| Player_Attack_11 | [10011] | [10] | 34 | full parsed snapshots |
| Player_Attack_12 | [10012] | [11] | 45 | full parsed snapshots |
| Player_Attack_13 | [10013] | [12] | 52 | full parsed snapshots |
| Player_Attack_14 | [10014] | [13] | 43 | full parsed snapshots |
| Player_Attack_15 | [10015] | [14] | 40 | full parsed snapshots |
| Player_Attack_16 | [10016] | [15] | 29 | full parsed snapshots |
| Player_Attack_17 | [10017] | [16] | 45 | full parsed snapshots |
| Player_Attack_18 | [10018] | [17] | 43 | full parsed snapshots |
| Player_Attack_19 | [10019] | [18] | 30 | full parsed snapshots |
| Player_Attack_20 | [10020] | [19] | 29 | full parsed snapshots |
| Player_Attack_21 | [10021] | [20] | 27 | full parsed snapshots |
| Player_Attack_22 | [10022] | [21] | 29 | full parsed snapshots |
| Player_Attack_23 | [10023] | [22] | 44 | full parsed snapshots |
| Player_Attack_24 | [10024] | [23] | 37 | full parsed snapshots |

**Đính chính report82:** các giá trị trong bảng đã được kiểm CFG must-value:72/72
rate/main-damage/wing-damage calls của24implementation đều truyền suffix−1. Candidate
text-scan của81 được thay bằng proof này; không tự biến argument proof thành roster/lifecycle proof. Exact call address/method/constant instruction is in
`datas/combat_chain_contract.json.gz`. Không cho rằng 24 tàu có cùng timer/emitter:
coroutine lasers/saws/bursts/homing của từng family đã có native riêng để đọc/implement.

## D. Đóng chuỗi static của implementation1, sửa scope report79–80

“Tàu1” trong79–80 = **Player_Attack_1**, KHÔNG phải chắc chắn playerID10001.
Typed source10003 là phát hiện mới. Giữ các timer facts79–80 trong scope implementation này.

### D1. Setup / pool / concrete bullet types

- SetupDatas main bullet literal80003; MainCannonAttack rank branch pooled ID88004.
- Typed same-file m_OPScript nguồn nối80003→**Bullet_Plasma**,88004→**Homing_Missile**.
  Không áp hành vi base Bullet_Linearly cho80003 mà bỏ override Plasma.
- MainCannonShoot creates two Action delegates, target=self, supplies them to IBullet.SetBullet;
  delegate ctor exact span0x19a9434..0x19a954c lưu raw bytes/asm, không dựng từ tên method.

### D2. ELF GOT→symbolic usage giải được chỗ hở80

On-disk GOT cells =0 không có nghĩa null runtime. ELF64 R_AARCH64_RELATIVE1027 addends:

| GOT | RELA pointee | Resolved meaning |
|---|---|---|
|0x2ae7c28|0x2bc8090|OnBulletMainCannonCollided, MethodAddress0x147c1ac|
|0x2ae7c30|0x2bc80a0|OnBulletMainCannonDestroyed,0x147c1a8|
|0x2adcbe8|0x2bc4cf8|GameObject.GetComponent<IBullet>()|
|0x2adcbf0|0x2ba7250|SpaceShooter.IBullet_TypeInfo|
|0x2adcaa8|0x2bc4da8|GameObject.GetComponent<Obj_Collider>()|
|0x2adcb88|0x2ba73d8|IDamageable_TypeInfo|
|0x2adcac0|0x2bc1200|Component.GetComponent<IDamageable>()|

`relocations.json.gz` giữ original24-byte RELA rows+offset; `symbols.json.gz` giữ exact
Dumper usage entries. Join bằng RELA addend, **không** join nhầm GOT-address với usage-address.
Do đó chỗ delegate/type-pointer UNKNOWN ở80 đã có static binding cho đường này.
Không có nghĩa tất cả622 indirect sites trong toàn batch đã resolve.

### D3. SetBullet → callback concrete Plasma

- Bullet_Plasma.SetBullet0x158d278 gọi Bullet_Linearly.SetBullet0x158e0c0 rồi
  Bullet_Object.SetBullet0x158c0d8; base0x158c108 stores collision/destroy delegates@0x40/48.
- Plasma.OnTriggerEnter2D: mask predicate, stop và hasTriggerStay gates rồi virtual OnCollide.
- Plasma.OnCollide0x158d2a0: actived + delegate + collider nonnull; lấy collider.gameObject,
  invoke delegate0x158d300. Override này không tự clear delegate/actived như base OnCollide.
- Source80003 hasTriggerStay=false; không biến native OnTriggerStay path thành source bật sẵn.
  Có khác biệt multihit/piercing semantics giữa subclass; không đồng nhất mỗi projectile một hit.
- Base/Homing bodies cũng nằm raw. Frame/physics scheduling và số lần thực trúng vẫn chưa đo.

### D4. Callback → Obj_Collider → receiver

- Callback main lấy Obj_Collider qua resolved generic usage, GetIDamageable0x123ba28,
  crit/getter/Damager, rồi interface TakeDamage(ignoreInvincible=false), như80.
- Obj_Collider.GetIDamageable gọi Init(false), trả cached interface@0x28.
  Init đọc rootTransform@0x20, GetComponent<IDamageable>(), stores cache. `init=true` được
  ghi **trước** kiểm root; forceinit là đường riêng. Không tự thêm retry/repair khi root null.
- 1.623 source colliders→typed root GameObject/component inventory:1.472 candidates Enemy_Sub,
  76 Shield_Sub,6 Sub_Player,1 Sub_ShipProtect;64 source rootTransform null và4 root không có
  candidate trong inventory. Không phải1.623 receiver khác nhau hay concurrent instances.
- Enemy_Sub.TakeDamage0x1587ecc→controller0x1582938→OnTakeDamage0x1582ad4.
  Gate currentHP@Enemy_Datas0x28 và flag@0x2f; valid Damager/healthScript mới gọi
  Enemy_Health.CalculateDamage0x158479c với by-ref currentHP. Report82 đối chiếu dump:
  flag@0x2f là `Enemy_Datas.IsCaAttack`, không còn unknown.
- Sub_Player→Player_Health.TakeDamage0x14c6de4 có nhánh health/flags/ability/invincibility riêng.
  Shield_Sub.TakeDamage không dùng enemy armor formula, chủ yếu hit effect/scheduled state.
  **Không áp một mô hình enemy armor cho mọi IDamageable.**

## E. Enemy damage / HP arithmetic rule để implement

Native Enemy_Health.CalculateDamage (finite normal scope):

```
if noDamage && !ignoreInvincible: return
if hp <= 0: return
if armor >= 0: factor = 100 / (100 + armor)
else:          factor = 2 - 100 / (100 - armor)
hp = max(hp - damage * factor, 0)
if hitCallback != null: hitCallback()
loss = oldHp - hp  # HP RE-READ sau hitCallback
if hitDamageCallback != null && loss > 0: hitDamageCallback(loss)
```

- Armor100 halves positive damage; armor−100 multiplies1.5, không dùng nhánh positive chung.
- Overkill clamps HP0; callback loss không phải raw requested damage.
- damage0 vẫn có thể tới hitCallback. Native không clamp inputdamage>=0 trong thân này;
  negative damage có thể tăng HP và không clamp maxHP ở CalculateDamage.
- **Reentrancy:** hitCallback có thể đổi HP/throw; hitDamageCallback đọc HP sau đó. Bounded model
  chỉ tới storeHP trước user callbacks, không giả vờ simulate callbacks.
- 981 Enemy_Health source snapshots:740 noDamage=false,241 true; armor là private runtime field,
  không có trong serialized tree này. Không fabricate armor snapshot hoặc default0 “đã chứng minh”.
- `tools/verify/enemy_damage_model.py`: binary32 arithmetic finite-model; input validation chỉmodel,
  không native validation. Không FPCR/NaN/Infinity/runtime approval.

## F. AI thiết kế/triển khai nhận một gói, không phải đống TODO lẻ

| Hệ | Đầu vào chính | Luật đã có thể bám | Không được tự gọi APK fact |
|---|---|---|---|
|24 ship implementations|combat_chain_contract.ships + native families|source ID/demo, getter sites, callbacks/coroutines riêng|allships dùng một timer, suffix=ID|
|Grouped timer|report80 + player_main_cannon_timer.py|dual deadlines,N+1 entries,no catchup trong span|model enteredEmitter=bullet/hit|
|Bullet identity|combat_chain_contract.pool_bindings|typed m_OPScript ID→class, override concrete|mọi bullet là Bullet_Linearly|
|Delegate/interface|resolved_got + RELA/symbols + native|đường chính implementation1 đã nối typed callback|tất cả indirect calls toànbuild đã resolve|
|Collider/receiver|collider_roots + Obj_Collider/receiver native|lazy root cache, typed source receivers|source root inventory=runtime instance/lifecycle|
|Enemy armor/HP|Enemy_Health native + enemy_damage_model|piecewise armor,clamp,callback order|enemy formula áp cho shield/player|
|Player defense|Sub_Player/Player_Health native|có đường riêng, guards/abilities nằm raw|ignoreInvincible bypass mọi guard|
|TTK/feel parity|chưa runtime approval|game mới chọn số/physics rõ là newdesign|damage×rate hoặc damage/rate là actualDPS|

**Acceptance cho implementation mới:** test ID→implementation mapping trước combat;
không gộp demo/live; test timer equality/late frame/extra gates; chọn concrete bullet override;
test callbacknull/rootnull/nodamage/ignore/dead/overkill/armor±/callback mutation;
log simulated emitted/hit/HPchange riêng. Các lựa chọn khác phải ghi newdesign.

**Trạng thái còn lại đã cụ thể hóa tại report82§6; không dùng đoạn lịch sử này làm checklist
unknown hiện hành.** Inventory toàn family không tương đương decompile semantic sạch
cả24tàu; chưa runtime scheduling/collision rate, toàn modifier của từng tàu, mọi receiver subtype,
FPCR/playback hoặc actualDPS/TTK. Không dùng những phần này để bắt hoãn L1, cũng không gọi L2 đủ.
Premium/pool-history vẫn hoãn. Raw/reference art/audio/fonts/Spine pack trước đây giữ nguyên.


## G. Regression / delivery checks

20tests mới (12contract +8damage model); full **278tests local PASS**,Pillow12,25.950s;
`datas/validate.py` và `git diff --check` PASS. FinalCI ghi riêng sau push.

**Final Verify40206236112 SUCCESS** cho codeb5f2cc62a: regenerate tables, pinned dependency
và regression steps PASS. Peer delivery PR12comment6399402332; chưa coi gửi task là peer đã sửa.

Report82 đóng72stat-argument proofs, commonmainrate modifier, tênflag,38unclean heuristic
và68source-root classifications. Không dùng các caveat cũ tương ứng để xin thêm capture.

**Parser correction82:** regex operandlessRET sửa đểkhôngnuốt nextinstruction; currentcontract
directsites13616 (khôngphải historical13144). Raw native/methodcounts khôngđổi.
