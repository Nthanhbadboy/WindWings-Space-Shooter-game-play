# ANIMATION SCRIPT — code gọi animation nào, lúc nào

> Mục tiêu của file này **không phải** "animation trông thế nào" (feel), mà là **script**:
> *hàm nào gọi `SetAnimation` với tên gì*, *event nào nổ ở giây thứ mấy*, *nhịp ra đòn bao nhiêu*.
> Đây là thứ cần để dựng lại **cơ chế** khi art làm lại hoàn toàn.
>
> Quy ước mức chắc chắn **A/B/C/D** theo `AI_FEASIBILITY.md` §0.0. Mọi con số đều đếm được
> bằng `tools/verify-claims.py` (nhóm **J** + **G**).

---

## 0. Kết luận trong 6 dòng

1. Game có **hai hệ animation độc lập**, không phải một: **Spine** (`SkeletonAnimation`) và
   **Unity AnimationClip + event** (`Animator` / `AnimationEvent`).
2. **Boss 1 (`Boss-39001`, `Boss-39002`) hoàn toàn bằng Spine** — **0 event clip**; script của nó
   là **`Boss1_Director`**, một lớp C# gọi `AnimationState.SetAnimation(track, entryName, loop)`.
3. **33 prefab `Boss-*` khác thì ngược lại**: **793 event clip**, mang theo **mốc thời gian** —
   tức nhịp ra đòn **nằm trong asset**, đọc được chính xác đến 0,01 s.
4. **Enemy gần như không có event clip** (toàn bộ 795 event chỉ có **2** ngoài nhóm boss) ⇒
   animation enemy là **máy trạng thái do code điều khiển** (`Enemy_Movement` 3 nhánh, hit flash
   `Invoke` 0,05 s), không phải event.
5. **Thời gian chờ trong code boss**: **22 lần `WaitForSeconds`**, chỉ **4** là hằng số
   (0,5 · 1,0 · 2,0 · 3,0 s), **18** lấy từ biến ⇒ nhịp pha boss phần lớn **do dữ liệu prefab**.
6. **Tên entry của boss 1 đã giải xong** (8 chuỗi: `Xuathien` · `Baydi` · `Dead` · `Attack1/2/3` ·
   `Chuyensangattack2/3`) và `BossWork` là **bảng chuyển state 5 nhánh**. Còn thiếu chỉ là **tên
   tham số Animator của enemy** + **ai gán 12 delegate** — đã giao nhánh dữ liệu (`HANDOFF_ANIM_RAW.md`).

---

## 1. Hai hệ animation — bằng chứng phân biệt

| | **Spine** | **AnimationClip + event** |
|---|---|---|
| lớp điều khiển | `SkeletonAnimation.AnimationState` | `Animator` + `AnimationEvent` |
| bằng chứng trong asm | `Boss1_Director.Start` gọi thẳng **`SkeletonAnimation.get_AnimationState`**, `AnimationState.add_Event`, `AnimationState.add_Complete`, `AnimationState.SetAnimation`, `Material.SetColor` | `event-receivers.json.gz`: mỗi bản ghi là một `AnimationEvent` có `time`, `functionName`, `clip_name` |
| nơi dùng | `Boss-39001`, `Boss-39002` (rig `skeleton__21`), `Boss-39003` (rig `skeleton__8`) | **33** prefab `Boss-*` + 1 prefab enemy (`CB-30040`) |
| số event | 2 tên event trong rig `skeleton__21` (`Stop` ×5, `Banplasma`), **0** trong `skeleton__8` | **795** event use, **795/795** có `time` |
| nhịp lấy từ | thời lượng animation trong file skeleton | `time` của từng event trong clip |

Hệ quả thực dụng: **hai nhánh phải dựng lại bằng hai cách khác nhau.**
Spine ⇒ một bảng `entryName → (track, loop, hành vi)` + timer coroutine.
Animator ⇒ một bảng `clip → [(t, hàm)]` chép nguyên mốc thời gian (§3).

---

## 2. Boss 1 — script nằm trong `Boss1_Director` (mức **A**)

`Boss1_Director` là lớp duy nhất trong 3 lớp boss 1 thật sự **gọi** animation. Bảng method:

| method | byte | việc |
|---|---:|---|
| `Start` | 588 | lấy `SkeletonAnimation` → `get_AnimationState` → `add_Event` + `add_Complete` → `SetAnimation` → `Material.SetColor` |
| `OnGunDie` | 1104 | súng con chết → chuyển pha |
| `Attack2` / `Attack3` | 516 | hai đòn chính; có `GameObject.SetActive`, `Behaviour.set_enabled` |
| `BossWork(string)` | 280 | **dispatch theo tên entry** — 2 nhánh (`+0x28`, `+0x58`) rồi `SetAnimation` |
| `Defeat` | 136 | `VibrateCamera.ActionVibrateStatic` + `Enemy_Destroy.OnBusrtItems` + `Enemy_Destroy.OnDefeated` |
| `SetHpSource(int)` | 460 | đổi nguồn HP khi tách bộ phận |
| `ClearGuns(int)` | 380 · `SetAttachmentDefeatGun1` 788 · `SetAttachmentDefeatShields` 172 | thay/tháo attachment của rig Spine khi phá bộ phận |

Phía rig có thêm `Boss_1_Animation` — lớp mỏng cùng tên method:

| method | byte | việc |
|---|---:|---|
| `BossWork(string)` | 336 | **5** lần `String.op_Equality` → rẽ 5 nhánh entry rồi gọi `SetAnimation` qua `[0x88]` |
| `SetDefeat(int turn, int index)` | 32 | `turn==1` → nhánh A, `turn==0` → nhánh B |
| `BossDefeat` | 20 | `ldr x0,[x0,#0x70]; cbz; b` → **cùng hàm** với nhánh fallback của `BossWork` |

### 2.0 Bảng script — **giải xong, mức A**

`Boss1_Director` có **8 field chuỗi** (typetree `Boss1_Director.jsonl.gz`) và vị trí bộ nhớ của
chúng suy ra được từ chính asm: `Start` gọi `SetAnimation(track 0, [0x28], loop=false)` ⇒ `[0x28]`
là **animation lúc vào trận**. Từ đó offset chạy liên tiếp 0x28 → 0x60:

| offset | field | giá trị | ai dùng |
|---|---|---|---|
| `0x28` | `stateAppear` | **`Xuathien`** | `Start` phát lúc vào trận, `loop=false` |
| `0x30` | `stateRunAway` | **`Baydi`** | `BossWork` → `Defeat()` |
| `0x38` | `stateDie` | **`Dead`** | `BossWork` → `Defeat()` |
| `0x40` | `stateAttack1` | **`Attack1`** | `BossWork` phát, `loop=true` |
| `0x48` | `stateAttack2` | **`Attack2`** | `BossWork` phát, `loop=true` |
| `0x50` | `stateAttack3` | **`Attack3`** | `BossWork` phát, `loop=true` |
| `0x58` | `statePreAttack2` | **`Chuyensangattack2`** | `BossWork` → `Attack2()` |
| `0x60` | `statePreAttack3` | **`Chuyensangattack3`** | `BossWork` → `Attack3()` |

Chuỗi offset — `0x28=Xuathien` · `0x30=Baydi` · `0x38=Dead` · `0x40=Attack1` · `0x48=Attack2` · `0x50=Attack3` · `0x58=Chuyensangattack2` · `0x60=Chuyensangattack3`

Thứ tự so chuỗi trong `BossWork`: `0x28` → `0x58` → `0x60` → `0x30` → `0x38`.

**8 tên entry kiểm chứng bằng dữ liệu serialize** (24/10, dòng mới kéo từ nhánh dữ liệu:
`docs/apk-analysis/Boss1_Director.csv`). Trước đây 8 chuỗi này suy ra **gián tiếp** từ offset; nay đọc
thẳng giá trị field:

| prefab | instance | `stateAppear` | `stateRunAway` | `stateDie` | `stateAttack1/2/3` | `statePreAttack2/3` |
|---|---:|---|---|---|---|---|
| `Boss-39002` | **1** | `Xuathien` | `Baydi` | `Dead` | `Attack1` · `Attack2` · `Attack3` | `Chuyensangattack2` · `Chuyensangattack3` |

⇒ 8/8 khớp suy luận offset trước đó, và **`Boss1_Director` chỉ có đúng 1 instance** (trên `Boss-39002`),
không phải "mỗi boss một director".

**Chuỗi gọi** (đọc từ asm, không suy đoán):

```
Spine.Complete(TrackEntry)                    # SkeletonAnimation_AnimationState_Complete, 50 B
  → trackEntry.Animation.Name                 # [x1+0x10] → [x8+0x10]
  → BossWork(name)                            # tail-call, không copy
```

và `BossWork` (280 B, **5 nhánh**) là **bảng chuyển state**:

| animation vừa chạy **xong** | gọi | rồi phát | loop |
|---|---|---|---|
| `Xuathien` | `Attack1()` 44 B | **`Attack1`** | ✔ |
| `Chuyensangattack2` | `Attack2()` 516 B | **`Attack2`** | ✔ |
| `Chuyensangattack3` | `Attack3()` 516 B | **`Attack3`** | ✔ |
| `Baydi` **hoặc** `Dead` | `Defeat()` 136 B | — (tan biến) | — |
| tên khác | — | không làm gì (`ret`) | — |

**Đọc ra được gì:** boss 1 **không có timeline**. Nó là **máy trạng thái tự chạy**: mỗi animation
kết thúc thì tự gọi state kế. Ba đòn `Attack1/2/3` **lặp vô hạn** (`loop=true`) — muốn thoát phải
có code khác phát clip chuyển (`ChuyensangattackN`), và **đó chính là chỗ `loop=true` + 33 s của
`Attack1` được giải thích**: 33 s là *một vòng lặp*, không phải một đòn.

⇒ Script boss 1 gọn lại còn: **8 tên entry**, **5 nhánh**, **3 vòng đòn lặp**. Không có event,
không có timeline, không có random.

### 2.1 Nhịp pha — hằng số và biến

| coroutine | `WaitForSeconds` |
|---|---|
| `_WarningBossAppear_d__15` | **3,0 s** rồi **0,5 s** |
| `_IEAttack1_d__25` | **1,0 s** |
| `_OnGun1Static_d__28` | **2,0 s** |
| `_OffGun1Head_d__27` · `_OffGun1Static_d__26` | lấy từ biến (`float _duration`) |
| `Boss_AttackTypes._IE*` (5 kiểu bắn) | **18/22** lần lấy từ biến |

Tổng: **22 lần `WaitForSeconds` · 4 hằng số · 18 lấy từ biến**. Nghĩa là **không thể** suy nhịp
pha boss chỉ từ code — phải đọc dữ liệu prefab (chưa export).

### 2.2 Cầu nối event Spine — `BossSpineEventHandler` (mức **B**)

`Start` (616 B): `GetComponent` → `get_AnimationState` → đăng ký **≥3 delegate** (đôi `add/remove`
trên các static `MethodInfo` cache).
`HandleEvent(TrackEntry, Event)` (164 B) so **`e.data.name`** với **đúng 2 chuỗi**:

| khớp | hành vi |
|---|---|
| slot **#1** | `Behaviour.set_enabled(false)` trên `[0x40]` → nếu `[0x38]` khác null thì `UnityEvent.Invoke()` |
| slot **#2** | `Behaviour.set_enabled(true)` — không invoke |
| không khớp | `ret` |

**Tên field — nay biết chính xác (mức A)** từ `reverse-engineering/il2cpp/interesting-classes.cs`
(kéo 24/10), đúng 5 field serialized:

| offset | field | kiểu | vai trò trong `HandleEvent` |
|---|---|---|---|
| `0x20` | `attackEventName` | `string` | khớp ⇒ `chargeEffect.set_enabled(false)` + `onAttack.Invoke()` |
| `0x28` | `preAttackEffectEventName` | `string` | khớp ⇒ `chargeEffect.set_enabled(true)` |
| `0x30` | `skeletonAnimation` | `SkeletonAnimation` | đăng ký delegate trong `Start` |
| `0x38` | `onAttack` | `UnityEvent` | gọi khi khớp `attackEventName` |
| `0x40` | `chargeEffect` | `GameObject` | bật/tắt theo 2 event trên |

⇒ Cơ chế **đọc được trọn** (A): "event trước đòn" **bật hiệu ứng tích tụ**, "event đòn" **tắt hiệu ứng +
gọi `UnityEvent`** để gây sát thương. Còn **giá trị 2 chuỗi** thì vẫn **B** — ứng viên duy nhất vẫn là
**`Stop`** và **`Banplasma`**, và theo tên field thì `attackEventName` nhiều khả năng = **`Banplasma`**
(nghĩa đen "bắn plasma"), `preAttackEffectEventName` = **`Stop`**. **Chưa có bằng chứng trực tiếp** vì
`BossSpineEventHandler` vẫn **0 instance export** ⇒ §T1 của `HANDOFF_ANIM_RAW.md`.

**Nguồn thứ hai, độc lập** — `docs/apk-analysis/spine-events.csv` (21 dòng dữ liệu, kéo từ nhánh dữ liệu
24/10) xác nhận đúng **2 tên event** đó, kèm mốc thời gian:

| rig | animation | event | mốc (s) |
|---|---|---|---|
| `skeleton__21` | `Attack3` | `Stop` ×**5** | 0,6333 · 3,3 · 5,8667 · 8,2 · 10,6 |
| `skeleton__21` | `Attack4` | `Banplasma` ×1 | 0,7 |
| `skeleton__8` | — | **không có event nào** | — |
| `skeleton__17` | `Attack01…12` | `Shot` ×12 | 0,3333 (mỗi clip) |

**`skeleton__21`: 6 event · 2 tên phân biệt** (5×`Stop` + 1×`Banplasma`).

⇒ Với rig boss 1, **chỉ tồn tại 2 tên**: `Stop` và `Banplasma` — nên 2 slot chuỗi của
`BossSpineEventHandler` **chắc chắn** lấy từ tập này (mức **A** cho *tập ứng viên*). Còn **slot nào
là tên nào** thì vẫn **B**. Đọc thêm: `Stop` nằm trong `Attack3` (12,667 s) cách nhau ~2,4 s ⇒ nó là
nhịp **tắt/bật một bộ phận** giữa đòn, khớp với hành vi `set_enabled` ở bảng trên.

> **Chưa biết lớp này có ai dùng hay không:** `BossSpineEventHandler` **không có** trong
> `script-links.jsonl.gz` (5 instance của `BossAnimationEvents`, **0** của lớp này) và **không có**
> trong `typetrees/`. Nhưng tập `script-links` chỉ phủ các lớp nằm trong `TARGETS`, nên **không
> được kết luận "code chết"** — đó là việc §T1 của `HANDOFF_ANIM_RAW.md`.

---

## 3. 33 prefab boss còn lại — nhịp đòn nằm trong clip (mức **A**)

**33 prefab boss · 793 event · 2 ngoài boss**. 129 tên hàm phân biệt; dày nhất:

`OnStartAttack` 146 · `OnAnimationEndedEvent` 137 · `OnStateExit` 56 · `OnStopAttack` 50

**268 cặp (prefab, clip)**, trong đó **61 cặp (prefab, clip, hàm)** có ≥ 3 event — đây là các
"chuỗi đòn" đọc được nhịp. Ví dụ đo được:

| prefab | clip | hàm | n | Δ trung vị | clip dài ≥ |
|---|---|---|---:|---:|---:|
| `Boss-39012` | `attack2` | `AttackHandLeft` | 8 | **0,17 s** | 1,92 s |
| `Boss-39012` | `attack5` | `AttackHand5Left` | 12 | **0,33 s** | 7,17 s |
| `Boss-39012` | `attack6` | `AttackHand5Right` | 12 | **0,33 s** | 7,17 s |
| `Boss-39021` | `attack1` | `OnStartAttack` | 8 | **5,00 s** | 40,67 s |
| `Boss-39019` | `attack3` | `OnStartAttack` | 12 | **1,05 s** | 19,88 s |
| `Boss-39020` | `idle1` | `OnStartAttack` | 14 | **1,02 s** | 8,17 s |

**Đọc ra được gì cho clone:**

- **Nhịp đòn là bội số đẹp**: 0,17 · 0,33 · 0,5 · 1,0 · 1,05 s — tức "mỗi 1/6 hoặc 1/3 giây một
  nhịp", không phải random. Clone chỉ cần **một nhịp cơ sở + số lần lặp** (`n` ở trên).
- **Clip `idle` cũng bắn đòn**: `Boss-39020.idle1` gọi `OnStartAttack` 14 lần ⇒ boss "đứng yên"
  vẫn bắn. Đây là chỗ rất dễ dựng sai nếu chỉ nhìn tên clip.
- **Tên clip là tiếng Việt không dấu**: `Xuathien` (xuất hiện), `Chuyensangdot2` (chuyển sang đợt 2),
  `chuyen sang dot 2`, `dead`, `Die`, `idle1..3`, `attack1..16`. Tức **14 đòn / 1 boss** là bình
  thường, không phải 3.
- **`OnStateExit` luôn là event cuối clip** (56 lần) ⇒ code dùng nó làm mốc "hết state", tương ứng
  `AnimationState.add_Complete` bên nhánh Spine.

### 3.1 12 handler của `Boss1_AnimationEvents` — chỉ là ống dẫn (mức **A**)

`Boss1_AnimationEvents`: `OnDie` · `Attack1HandLeft` · `Attack2HandRight` · `Attack3TwoHands` ·
`Attack1StartCheckShoot` · `Attack2StartCheckShoot` · `Attack12Shoot` · `OnCallAttack4Event` ·
`OnCallAttack6Event` · `OnCallAttack9StartEvent` · `OnCallAttack9EndEvent` ·
`OnAnimationEndedEvent` — **12 handler · 28 byte** mỗi cái.

**12 field delegate `0x20`…`0x78` có tên** (từ `interesting-classes.cs`, kéo 24/10) — đúng thứ tự khai báo:

| offset | field | method gán vào | | offset | field | method |
|---|---|---|---|---|---|---|
| `0x20` | `onAnimationEndedEvent` | `OnAnimationEndedEvent` | | `0x50` | `onCallAttack2CheckEvent` | `Attack2StartCheckShoot` |
| `0x28` | `die` | `OnDie` | | `0x58` | `onCallAttack12ShootEvent` | `Attack12Shoot` |
| `0x30` | `onCallAttack1Event` | `Attack1HandLeft` | | `0x60` | `onAttack4Event` | `OnCallAttack4Event` |
| `0x38` | `onCallAttack2Event` | `Attack2HandRight` | | `0x68` | `onAttack6Event` | `OnCallAttack6Event` |
| `0x40` | `onCallAttack3Event` | `Attack3TwoHands` | | `0x70` | `onAttack9StartEvent` | `OnCallAttack9StartEvent` |
| `0x48` | `onCallAttack1CheckEvent` | `Attack1StartCheckShoot` | | `0x78` | `onAttack9EndEvent` | `OnCallAttack9EndEvent` |

Thân mỗi hàm đúng 4 lệnh: `ldr x8,[x0,#off]; cbz; ldr x2,[x8,#0x18]; ldr x0,[x8,#0x40];
ldr x1,[x8,#0x28]; br x2` ⇒ **chỉ gọi một delegate, không có logic**.

> **Chỗ tôi từng viết sai:** bản đầu của mục này ghi *"hành vi nằm ở UnityEvent binding trên
> prefab"*. **Sai.** Đó là **field delegate** (`Action`), **không** phải `UnityEvent`: lệnh
> `ldr x2,[x8,#0x18]` lấy `method_ptr` của delegate, không phải `m_PersistentCalls`. Delegate
> **không serialize** ⇒ không có trên prefab, mà do **code khác gán lúc chạy**. Ai gán thì **chưa
> biết** — việc này đã giao sang nhánh dữ liệu (`HANDOFF_ANIM_RAW.md` §T2).

Vì vậy: chép được **tên sự kiện + thời điểm** (§3), **không** chép được "sự kiện đó làm gì".

### 3.2 Prefab nào dùng **lớp handler** nào — đã ghép được **16/34** (mức **A**)

`typetrees/*AnimationEvents*.jsonl.gz` là export **theo instance** (mỗi dòng = 1 MonoBehaviour, có
`gameobject` = đường dẫn trong prefab) ⇒ ghép được **prefab ↔ lớp handler** mà không cần chạy gì.
**14 lớp** đã export, phủ **16 prefab**, quan hệ **1:1** (không prefab nào có 2 lớp):

| prefab | event | lớp handler | | prefab | event | lớp handler |
|---|---:|---|---|---|---:|---|
| `Boss-39012` | 78 | `Boss10_AnimationEvents` | | `Boss-39007` | 19 | `Boss6_AnimationEvents` |
| `Boss-39019` | 76 | `BossAnimationEvents` | | `Boss-39010` | 19 | `Boss4_AnimationEvents` |
| `Boss-39020` | 75 | `BossAnimationEvents` | | `Boss-39016` | 14 | `Boss6_Mini_AnimationEvents` |
| `Boss-39015` | 58 | `Boss15_AnimationEvents` | | `Boss-37018` | 12 | `BossAnimationEvents` |
| `Boss-39017` | 42 | `Boss17_AnimationEvents` | | `Boss-37019` | 8 | `BossAnimationEvents` |
| `Boss-39018` | 34 | `Boss18_AnimationEvents` | | `Boss-39004` | 6 | `Boss5_AnimationEvents` |
| `Boss-39014` | 27 | `Boss12_AnimationEvents` | | | | |
| `Boss-39013` | 26 | `Boss11_AnimationEvents` | | | | |
| `Boss-39008` | 20 | `Boss7_AnimationEvents` | | | | |
| `Boss-39006` | 19 | `Boss4_AnimationEvents` | | | | |

⇒ **18 prefab còn lại có event clip nhưng chưa export lớp handler** (`Boss-37001/02/04/09…17`,
`Boss-39003/05/09/11/21`, `CB-30040`) — **262/795 event (33 %)** chưa biết thuộc lớp nào.

> **Sửa một hiểu sai quan trọng:** 12 handler ở §3.1 là của `Boss1_AnimationEvents` — lớp đó **không**
> phải lớp của 10 prefab lớn nhất. `Boss-39012` dùng `Boss10_AnimationEvents`, `Boss-39019/39020`
> dùng `BossAnimationEvents`. Nghĩa là **không thể** lấy 12 tên ở §3.1 làm bộ handler chung; mỗi lớp
> có bộ tên riêng (đúng như 130 tên hàm quan sát được).

### 3.3 Ma trận `*_Director` ↔ `*_AnimationEvents` (kéo 24/10, mức **A**)

`docs/apk-analysis/*_Director.csv` (**16** file) + `*_AnimationEvents.csv` (**14** file), mỗi dòng có
`_gameobject` ⇒ ma trận đầy đủ. Trong **34 prefab có event clip**:

| có cả hai (**13**) | chỉ `_Director` (**4**) | chỉ `_AnimationEvents` (**3**) | không có gì (**14**) |
|---|---|---|---|
| 39004 · 39006 · 39007 · 39008 · 39012 · 39013 · 39014 · 39015 · 39016 · 39017 · 39018 · 39019 · 39020 | 39005 · 39009 · 39011 · 39021 | 37018 · 37019 · 39010 | 37001 · 37002 · 37004 · 37009…37017 (9) · 39003 · `CB-30040` |

Ngoài ra **`Boss-39002` có `Boss1_Director` nhưng không có event clip** (Spine — xem §2.0b). Tính trên
**39 prefab `Boss-*`**: **18 có `*_Director`** (17 trong số đó có event clip + `Boss-39002`) và **16 có
lớp `*_AnimationEvents`**.

**Ba điều đọc được:**

1. **Tên lớp ≠ tên prefab**: `Boss-39012` → `Boss10_Director` + `Boss10_AnimationEvents`; `Boss-39006`
   → `Boss4_Director`; `Boss-39008` → `Boss7_Director`. Đánh số lớp **không** theo thứ tự prefab ⇒
   mọi phép ghép phải dùng **`_gameobject`**, không dùng số.
2. **`Boss_Director` dùng chung**: `Boss-39019/39020/39021` cùng chạy lớp base `Boss_Director`
   ⇒ 3 prefab khác art nhưng **cùng script**.
3. **13 prefab không có director** trong export (đa số là `Boss-370xx`) ⇒ script của chúng **chỉ** là
   event clip (§3) — không có máy trạng thái nào để đọc, và đó là lý do **262 event (33 %)** vẫn
   chưa biết lớp handler.

---

## 4. Enemy — animation do code điều khiển, không do event (mức **A**/**B**)

Toàn bộ **795** event chỉ có **2** ngoài nhóm boss (`CB-30040`, clip `Die`, `Attack` @1,5 s) ⇒
**enemy không có timeline**. Script enemy = **3 lớp**:

| lớp | method chính | byte | việc |
|---|---|---:|---|
| `Enemy_Controller` | `Appear` 452 · `OnTakeDamage` 864 · `OnDieWhenZeroHp` 84 · `Stun` 148 · `Burn` 180 · `GainHealth` 188 · `SetDieCallback` 168 · `CacheComponents` 400 | 33 method | vòng đời: xuất hiện → nhận đòn → chết |
| `Enemy_Movement` | `Update` → **`PathFollow` / `MoveLinearly` / `MovePointToPoint`** · `MoveToPoint` → `StartCoroutine(IELinearMove)` · `OnPathEnded` → `UnityEvent.Invoke` · `SetEventMoveEnded` | 21 method | **máy trạng thái di chuyển** = "animation" của enemy |
| `Enemy_Destroy` | `Destroyed` 1052 · `OnDefeated` 544 · `OnBusrtItems` 500 · `OnDestroyByZeroHp` 292 · `OnDestroyWhenHitPlayer` 292 · `Pool` 320 | 12 method | chết → nổ item → trả pool |

`Enemy_Appear` chỉ là **vỏ delegate** (không field) ⇒ "xuất hiện" là **callback gắn từ prefab**,
không phải animation riêng.

### 4.1 Hit flash — con số duy nhất của "feel" còn lại (mức **B**)

`Enemy_Display` có **5 field**: `hpProgressBarRenderer`, `size`, `hitableRenderers`, `appearOff`,
`dieOff` — **không** có `timeScale`/`flashDuration` (đã ghi ở `DESIGN_READINESS.md` §2).
Nhưng `OnHit` (352 B) chứa **hai hằng số**:

| chỗ | giá trị | suy ra |
|---|---:|---|
| `#0x276a2b4(material, s0=0.5)` trong vòng lặp `hitableRenderers` | **0,5** | đặt một tham số material (alpha/độ sáng) = 0,5 khi trúng đòn |
| tail `#0x27822d4(Component, string tĩnh, s0=0.05)` | **0,05 s** | đúng dạng `MonoBehaviour.Invoke(tênHàm, 0,05)`; hàm khớp duy nhất là **`OffHitEffect`** (private, cùng lớp) |

⇒ **nháy trúng đòn = 0,05 s**, tắt bằng `Invoke` chứ không bằng coroutine. Đây là con số
**duy nhất** trong toàn bộ "animation enemy" mà chép lại được nguyên văn.

---

## 5. Bảng chép lại được / không chép được

| hạng mục | chép được? | nguồn |
|---|---|---|
| Tên + mốc thời gian 793 event boss (+2 event `CB-30040`) | **A** | `event-receivers.json.gz` · chi tiết: **`BOSS_ANIM_TIMELINE.md`** |
| Nhịp đòn (0,17 · 0,33 · 1,0 · 5,0 s) | **A** | suy từ `time` |
| Danh sách clip theo boss (14 đòn/boss) | **A** | `clip_name` |
| Chuỗi hàm boss 1 + hằng chờ (0,5/1/2/3 s) | **A** | asm `Boss1_Director` |
| Máy trạng thái enemy (3 nhánh move) | **A** | `native-calls.json` |
| Hit flash 0,05 s | **B** | suy từ asm `Enemy_Display.OnHit` |
| 2 tên event Spine ↔ hành vi | **B** | ứng viên `Stop`/`Banplasma` |
| Nội dung 12 handler (delegate do code gán) | **C** | cần tìm chỗ gán — `HANDOFF_ANIM_RAW.md` §T2 |
| **8 tên entry + bảng chuyển state boss 1** | **A** | typetree `Boss1_Director` + asm `BossWork` |
| Tham số Animator của enemy | **C** | chưa có tên nào |

---

## 6. Việc còn lại — **đã giao sang nhánh dữ liệu**

Ba mục **C** còn lại đều cần **đào raw** (export thêm asset / xref asm), nên theo chỉ đạo của chủ
dự án chúng được giao thành một lô cho nhánh phân tích ngược: xem **`HANDOFF_ANIM_RAW.md`**
(T1 = 3 lớp chưa export · T2 = ai gán 12 delegate · T3 = `UnityEvent` persistent calls ·
T4 = tham số + transition `Animator` của enemy).

Mỗi task trong đó có **giả định sai được**, **artifact cụ thể**, và **điều kiện lật ngược**, để
nhánh bên kia chạy được mà không phải hỏi lại.

## 7. Cách kiểm lại

```bash
python3 tools/verify-claims.py --only J     # 10/10 claim nhóm J (nhịp + event)
python3 tools/verify-claims.py --only K     # 6/6 claim nhóm K (tên entry + bảng chuyển state)
python3 tools/verify-claims.py --only R     # 6/6 claim nhóm R (timeline theo giây)
python3 tools/verify-claims.py              # toàn bộ: 119 PASS · 0 FAIL · 2 SKIP
```

Nguồn: `reverse-engineering/raw/animation-audit/event-receivers.json.gz` (795 event) ·
`…/native-calls.json` (272 method, direct call + hằng số) ·
`reverse-engineering/raw/il2cpp-consts/*.asm.txt` (69 file) ·
`datas/spine_anim.json.gz` (event trong rig Spine).
