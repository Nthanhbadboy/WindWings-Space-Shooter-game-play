# 80 — Tàu1: phát phụ, emitter và damage callback

> **Cập nhật scope từ report81:** “tàu1” ở đây là implementation `Player_Attack_1`,
> source prefab ID10003, không suy ID10001 từ hậu tố. Report81 đã nối thêm ELF RELA/metadata
> callback→concrete Bullet_Plasma→Obj_Collider→receiver; limitation binding ở bản này là lịch sử.


**Tạm thời, static APK + bounded model; không runtime/DPS/TTK approval.**
Dùng lại raw79 `reverse-engineering/raw/player-firing/` (pinned index + native SHA),
không cần recovery/full export/media mới. Source declarations: `il2cpp/dump.cs.gz`.

## 1. MainCannonShoot không phải mỗi lần gọi đều phát

Native `Player_Attack_1.asm.txt`,0x147a91c..994:

```
if Time.time < timeToShotMainCannon@0x10c: return
if numberAddMainCannonCount@0x11c >= 1:
    if Time.time < timeToShotMainCannonDelay@0x118: return
    timeToShotMainCannonDelay = Time.time + rateAddMainCannon@0x124
    turnMainCannonCount@0x120 += 1
    if turnMainCannonCount <= numberAddMainCannonCount:
        goto emitter
    turnMainCannonCount = 0
# đi qua nhánh này mới cập nhật main deadline
 timeToShotMainCannon = Time.time + timeRateMainCannon@0xa8
emitter:
    # duyệt mainCannonBarrels, rồi MainCannonAttack
```

Pseudocode chỉ cho finite normal comparisons/counter không overflow; native không có
model input validation. Có nhiều lần gọi Time.time, mô hình coi chúng ổn định trong một invocation.
Đúng bằng deadline thì không bị nhánh `b.mi` chặn; không có vòng catch-up timer trong span này.

**N extra-count dương dẫn tới N+1 lần vào emitter** trong một chuỗi từ counter0,
không phải N lần. Lần thứ N+1 mới reset counter và đặt main deadline.
Cả hai gate đều được kiểm: khoảng nghỉ nhóm kế tiếp có thể bị extra deadline chi phối
nếu extra_delay lớn hơn main interval. Vì vậy không thể chỉ lấy `N / interval` làm rate.

`OnEnable0x147a634..650` gọi getter với argument4 rồi ghi extra-count; demo chọn0.
Dump resolve0x14c7758 = `GP_Datas.GetNumberAbility(int)` (argument4), không suy
con số thực của getter từ constructor. `.ctor0x147cd74/78` ghi count1 và delay bits
`0x3e4ccccd` (~0.2f), nhưng **constructor defaults không chứng minh trạng thái sau OnEnable**.

## 2. Hai đường emitter, không nhầm rank và level

- MainCannonShoot0x147a994..acbc duyệt `mainCannonBarrels@0x88`: lấy pooled object,
  tìm component, setup qua interface rồi SetActive(true). Component lookup có nhánh
  bỏ qua; pool/null/failure có đường lỗi. Số vòng lặp **không tự bằng số bullet spawn thành công**.
- 0x147acec tailbranch `MainCannonAttack0x147b608` sau emitter chính (kể cả array length0).
- MainCannonAttack đọc **rank@0x44**: rank3→2 vòng; rank>=4→4 vòng; rank<3 return.
  Không gọi số này là số nòng của toàn tàu hay số hit; mỗi vòng còn pool/component/setup gates.
- `SetBarrels` dùng getter của Player_Ingame tại0x14b1eb0 cho nhánh wing data. Không trộn
  level getter này với rank@0x44 của main emitter; report79 chưa đóng roster/barrel runtime.

## 3. Damage được tính trong callback, không phải pool spawn đồng nghĩa gây damage

Trong `OnBulletMainCannonCollided0x147c1ac`:
- obj truth/component checks rồi `GetIDamageable0x123ba28`; null thì returnpath.
- Random.Range(float,float) tại0x277d280 với0,1; getter
  `GetMainCannonCritPercent0x14e3e24`; so tại0x147c2fc.
- FCSEL0x147c30c: finite random > percent chọn multiplier1, ngược lại2.
  Không tự viết lại thành `<` strict; equality rơi về2 theo nhánh đã đọc.
- virtual damage getter qua vtable@0x198; chính override `get_GetMainCannonDamage`
  tại0x147a508 tailcalls `Player_Get_Datas.GetMainCannonDamage(0)0x14e3948`.
- 0x147c328 nhân multiplier với getter result rồi `.ctor Damager(float,Action)`
  tại0x123b7a4. Cuối callback dispatch interface với ignoreInvincible=false.

**Giới hạn:** dump xác nhận `IDamageable.TakeDamage(Damager,bool)` slot0 và signature
Damager ctor, nhưng chưa resolve metadata type-pointer tại interface lookup và delegate
method-pointer của emitter. Vì vậy đây là **callback method body**, chưa closure chứng minh
mọi bullet đã bind callback này, đúng receiver implementation nào, hay actual health delta.
Chưa mô hình callback2/crit modifier đầy đủ, shield/armor/invincibility/destroy/reuse.
Không suy emitted bullet → một hit → damage getter → HP giảm bằng số đó.

## 4. Model để AI triển khai không copy nhầm

`tools/verify/player_main_cannon_timer.py`: một invocation đã qua caller gates,
inputs injected representable binary32 finite nonnegative, count/counter bounded.
Chỉ trả `entered_emitter`, **không** trả bullet count/hits/DPS. No Unity/FPCR playback.
Time.time stable-within-call là giả định; caller stop/victory/demo/gameplay state không mô phỏng.
Giá trị toy interval4,extra-delay0.25,count2 **không phải captured save/device**:
invocation tại0/0.25/0.5 vào emitter, counter1/2/0; main deadline sau đó4.5.
Late invocation tại100 đặt deadline104, không bù các phát đã lỡ.

## 5. Bàn giao / next gap

AI game mới có thể implement timer/grouped emitter thành rule rõ ràng hoặc chọn cơ chế mới,
nhưng phải ghi newdesign nếu thêm catch-up, bỏ extra gate hoặc gộp nhiều nòng thành một hit.
Chưa có actual ship1 DPS, chưa có nhịp tương đương24tàu. Gap tiếp theo khi cần parity:
resolve emitter delegate/type pointers và bullet interface implementation → callback entry →
receiver.TakeDamage, rồi mới nối runtime health/shield gates. Không Premium/pool-history.

7 tests mới: deadline equality, N+1 entries, dual gates, no catchup, zero delay one-entry/call,
f32/domain và address-qualified branch/callback anchors. Raw hash/input tests79 giữ nguyên.

Local **257tests PASS** (Pillow12,23.573s), datasvalidate/diffcheck PASS.
Derived provenance `raw/player-firing/timer-derivation.json` giữ hashes và toy-input scope;
raw native79 vẫn nguyên vẹn.

Final bổ sung declaration regression: getter0x14c7758 thuộc **GP_Datas**, không
Player_Ability (đã sửa tên trong report/HANDOFF sau kiểm class scope trong dump).
8tests mới / **258tests local PASS** (23.999s); **Verify40204504124 SUCCESS** cho
5989366d7, regenerate/dependency/regressionstepsPASS. CI trước40204481857 cũngSUCCESS,
nhưng dùng mốc5989366d7 cho bản đã sửa class identity.
