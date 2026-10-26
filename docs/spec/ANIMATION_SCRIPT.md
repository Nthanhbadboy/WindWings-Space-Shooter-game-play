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
2. **Boss 1 (`Boss-39001`, `Boss-39002`) hoàn toàn bằng Spine** — **0 event clip** (`AnimationClip`; còn
   **Spine event** thì **có**: `Stop` · `Banplasma`). **Hai route driver RIÊNG BIỆT** (sync-review
   `152` + report 143 — không dùng chung driver): **Boss-39001** = `Boss_1_Animation` (serialized
   path 674445 · `SkeletonAnimation` 602882 · `parentDestroy` 601110); **Boss-39002** = `Boss1_Director`
   (path 582209 · `SkeletonAnimation` 664302 · `parentDestroy` 601111). Cả hai trỏ asset Spine chung
   580611/JSON 918 — asset chung **không** gộp component/driver identity. Driver là lớp C# gọi
   `AnimationState.SetAnimation(track, entryName, loop)`.
3. **33 prefab `Boss-*` khác thì ngược lại**: **793 event clip**, mang theo **mốc thời gian** —
   tức nhịp ra đòn **nằm trong asset**, đọc được chính xác đến 0,01 s.
4. **Enemy gần như không có event clip** (toàn bộ 795 event chỉ có **2** ngoài nhóm boss) ⇒
   animation enemy là **máy trạng thái do code điều khiển** (`Enemy_Movement` 3 nhánh, hit flash
   `Invoke` 0,05 s), không phải event.
5. **Thời gian chờ trong code boss**: **38 lần `WaitForSeconds`**, chỉ **12** là hằng số
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

Tổng: **38 lần `WaitForSeconds` · 12 hằng số · 26 lấy từ biến** (bản `9edc21f4d`, asm **139** file; trước là 22/4/18 trên 69 file). Nghĩa là **không thể** suy nhịp
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
gọi `UnityEvent`** để gây sát thương. **Giá trị slot callback Boss-39002 — identity ĐÃ RESOLVE (static, 27/10):** slot `0x2ADFB48`
qua RELA gốc → literal **`Stop`** (report **123-ef6b75ef**: native-relocations 288.733 entries
pin `0x2ADFB48→0x2BE5CB8` · 3 cells.json cùng RELA hex `48fbad02…b85cbe02…` @offset 3.563.112 ·
`stringliteral.json` độc lập `0x2BE5CB8→"Stop"` · literal index 7763 bytes `53746f70`; join 1-1
theo địa chỉ, kind-5 addend = địa chỉ literal). **Chỉ là literal identity** — KHÔNG phải method
pointer / delegate đã đăng ký / invocation / runtime event ⇒ **dispatch = `MODEL_NOT_MEASURED
runtime`**. `Banplasma` vẫn **chưa bind** slot nào (asset-level marker). `BossSpineEventHandler`
vẫn **0 instance export** ⇒ §T1 của `HANDOFF_ANIM_RAW.md`.

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

**33 prefab boss · 793 event · 2 ngoài boss**. **129 tên hàm phân biệt** trong nhóm boss (**130** nếu tính cả `CB-30040` —
xem `BOSS_ANIM_TIMELINE.md`); dày nhất:

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

### 3.2 Prefab nào dùng **lớp handler** nào — đã ghép được **17/34** (mức **A**)

`typetrees/*AnimationEvents*.jsonl.gz` là export **theo instance** (mỗi dòng = 1 MonoBehaviour, có
`gameobject` = đường dẫn trong prefab) ⇒ ghép được **prefab ↔ lớp handler** mà không cần chạy gì.
**18 lớp** đã export, phủ **17 prefab**, quan hệ **1:1** (không prefab nào có 2 lớp):

| prefab | event | lớp handler | | prefab | event | lớp handler |
|---|---:|---|---|---|---:|---|
| `Boss-39012` | 78 | `Boss10_AnimationEvents` | | `Boss-39007` | 19 | `Boss6_AnimationEvents` |
| `Boss-39019` | 76 | `BossAnimationEvents` | | `Boss-39010` | 19 | `Boss4_AnimationEvents` |
| `Boss-39020` | 75 | `BossAnimationEvents` | | `Boss-39016` | 14 | `Boss6_Mini_AnimationEvents` |
| `Boss-39021` | 75 | `BossAnimationEvents` | | `Boss-37018` | 12 | `BossAnimationEvents` |
| `Boss-39015` | 58 | `Boss15_AnimationEvents` | | `Boss-39004` | 6 | `Boss5_AnimationEvents` |
| `Boss-39011` | 48 | `Boss9_AnimationEvents` | | | | |
| `Boss-39017` | 42 | `Boss17_AnimationEvents` | | | | |
| `Boss-39018` | 34 | `Boss18_AnimationEvents` | | | | |
| `Boss-39014` | 27 | `Boss12_AnimationEvents` | | | | |
| `Boss-39013` | 26 | `Boss11_AnimationEvents` | | | | |
| `Boss-39009` | 22 | `Boss8_AnimationEvents` | | | | |
| `Boss-39006` | 19 | `Boss4_AnimationEvents` | | | | |

⇒ **17 prefab còn lại có event clip nhưng chưa export lớp handler** (`Boss-37001/02/04/09…17`,
`Boss-39003/05/08`, `CB-30040`) — **145/795 event (18 %)** chưa biết thuộc lớp nào.

> **Sửa một hiểu sai quan trọng:** 12 handler ở §3.1 là của `Boss1_AnimationEvents` — lớp đó **không**
> phải lớp của các prefab lớn nhất. `Boss-39012` dùng `Boss10_AnimationEvents`, `Boss-39019/20/21`
> dùng `BossAnimationEvents`. Nghĩa là **không thể** lấy 12 tên ở §3.1 làm bộ handler chung; mỗi lớp
> có bộ tên riêng (đúng như 130 tên hàm quan sát được).

### 3.3 Ma trận `*_Director` ↔ `*_AnimationEvents` (mức **A**)

`docs/apk-analysis/*_Director.csv` (**16** file) + `*_AnimationEvents.csv` (**18** file), mỗi dòng có
`_gameobject` ⇒ ma trận đầy đủ. Trong **34 prefab có event clip**:

| có cả hai (**15**) | chỉ `_Director` (**2**) | chỉ `_AnimationEvents` (**3**) | không có gì (**14**) |
|---|---|---|---|
| 39004 · 39006 · 39007 · 39009 · 39011 · 39012 · 39013 · 39014 · 39015 · 39016 · 39017 · 39018 · 39019 · 39020 · 39021 | 39005 · 39008 | 37018 · 37019 · 39010 | 37001 · 37002 · 37004 · 37009…37017 (9) · 39003 · `CB-30040` |

Tính trên **39 prefab `Boss-*`**: **18 có `*_Director`** và **16 có lớp `*_AnimationEvents`** — hai tập
**lệch 5 + 3** (sau khi đồng bộ `55bd18ac8`): **5** prefab có director mà **không** có lớp handler
(`Boss-39002`, `39005`, `39008`, `39013`, `39016`) và **3** prefab có handler mà không có director
(`Boss-37018`, `37019`, `39010`). Bản trước ghi *"lệch 3"* — số đó đúng với export cũ, **không** đúng
với export mới; giữ lại để thấy vì sao phải neo claim vào **tên file** chứ vào trí nhớ.

**Ba điều đọc được:**

1. **Tên lớp ≠ tên prefab**: `Boss-39012` → `Boss10_Director` + `Boss10_AnimationEvents`; `Boss-39006`
   → `Boss4_Director`; `Boss-39011` → `Boss9_Director`. Đánh số lớp **không** theo thứ tự prefab ⇒
   mọi phép ghép phải dùng **`_gameobject`**, không dùng số.
2. **`Boss_Director` dùng chung**: `Boss-39019/39020/39021` cùng chạy lớp base `Boss_Director`
   ⇒ 3 prefab khác art nhưng **cùng script**.
3. **14 prefab không có director** trong export (đa số là `Boss-370xx`) ⇒ script của chúng **chỉ** là
   event clip (§3) — không có máy trạng thái nào để đọc, và đó là lý do **145 event (18 %)** vẫn
   chưa biết lớp handler.

### 3.4 Boss 1 là **hai** prefab, **hai** driver — không phải một (sửa 25/10)

Trước đây tài liệu này gộp `Boss-39001` + `Boss-39002` thành "boss 1 dùng `Boss1_Director`". **Sai một
nửa.** Dữ liệu serialize mới (`Boss_1_Animation.csv`, kéo 25/10 từ `9aed767b1`) cho:

| prefab | lớp driver | instance | bằng chứng |
|---|---|---:|---|
| `Boss-39001` | **`Boss_1_Animation`** | **1** (`Boss-39001/Enemy_Ingame/Body/Boss 1`) | `skeAnim` → component `602882` → SDA `580611` → TextAsset `918` |
| `Boss-39002` | **`Boss1_Director`** | **1** | `Boss1_Director.csv`, 8 field `state*` |

Cả hai dùng **chung rig** `skeleton__21` và **chung 8 tên entry** (`Xuathien` · `Baydi` · `Dead` ·
`Attack1/2/3` · `Chuyensangattack2/3`) — nhưng **driver khác nhau**:

- `Boss1_Director` (39002) chuyển state **bằng code**: `BossWork(name)` 5 nhánh (§2.0).
- `Boss_1_Animation` (39001) chuyển state **bằng Inspector**: 2 `UnityEvent` có persistent call —
  `defeatEvent` → **`OnDefeated`**, `burstEvent` → **`OnBusrtItems`** (giữ nguyên chính tả của game),
  cùng trỏ component `601110`.

⇒ Khi dựng lại: **một** lớp driver là đủ; nhưng phải biết bản gốc có **hai** cách nối, và cái nối bằng
UnityEvent **không** nằm trong code — đọc từ prefab mới thấy.

### 3.5 Hai mắt còn thiếu của phần animation — **đã có raw** (25/10)

| mắt | số **đo lại từ raw** (không chép report) | nghĩa khi dựng lại |
|---|---|---|
| **T3 — `UnityEvent` nối bằng Inspector** | **1.335** field · **111** field không rỗng · **115** call (riêng enemy/boss **1.202** field · **114** call) | nối "bắn ↔ cửa sổ bắn" của enemy **không** nằm trong code: `Enemy_Attack_Event.startShootEvent` / `stopShootEvent` là cặp **mở/đóng**, wire trên từng khẩu súng |
| **T4 — graph `Animator`** | **52** controller · **63** prefab root · **303** parameter · **395** state · **357** transition (**302** có condition) | parameter **trùng tên state** (`Appear`, `Attack1`…, kiểu `Trigger`) ⇒ enemy chuyển state bằng **trigger đặt tên theo clip**; `Afterburner` (**27** prefab) có **0** parameter, **1** state = đứng yên |

**Ba con số đáng nhớ từ T4:**

1. `Afterburner` phủ **27** prefab mà **không có parameter nào** ⇒ gần **1/4 roster** là enemy
   "một state": bay theo path, không có animation đổi trạng thái. Dựng lại chỉ cần **1** clip.
2. `Boss 1` (controller `1833`) có **20 state**, `Body 2` (`1822`) có **28** — đây là mức "nhiều đòn"
   thật của bản gốc; boss ít nhất (`Boss`/`TayPhai`/`Rocket`) chỉ **2–3** state.
3. Tổng transition **357** mà **302** có condition ⇒ **85 %** chuyển state là **có điều kiện**, không
   phải "tự chạy hết clip". Đây là chỗ dựng lại hay sai nhất: nếu để clip tự chạy hết, boss sẽ ra đòn
   chậm hơn bản gốc.

> ⚠️ **Không** được ghi "đã đóng 87/87 roster": 63 prefab root của T4 lọc theo tiền tố
> `CB-`/`Boss-`/`MB-`, **khác** mẫu số roster 109/87. Muốn so thì phải ghép hai tập trước.

### 3.6 Ai **đặt** trigger — chỗ nối code ↔ máy trạng thái (mới 25/10, mức **A** cho call site)

§3.5 nói parameter kiểu `Trigger` trùng tên clip, nhưng chưa nói **ai** đặt. Raw
`animation-audit/native-calls.json` trả lời: **`Animator.SetTrigger` có đúng 7 call site, trên 5 method**
— **tất cả** trong `Boss_AttackPhases` (không có ở `Boss_AttackTypes`, cũng không có ở nhánh Spine):

| method | RVA | SetTrigger | Ghi chú |
|---|---|---:|---|
| `Boss_AttackPhases.CallMixAnimation` | `0x152e7ec` | 1 | "mix" đòn = đặt trigger, **không** phải gọi `Play` |
| `Boss_AttackPhases.OnGunDie` | `0x1532390` | 1 | súng chết ⇒ đổi state; float **0,15** trong thân |
| `<IEAttackRound1>d__13.MoveNext` | — | 1 | vòng 1 |
| `<IEAttackRound2>d__14.MoveNext` | — | 1 | vòng 2 |
| `<IEAttackRound3>d__15.MoveNext` | — | 1 | vòng 3 |

**Máy trạng thái đọc được ở mức nào:**

| thứ | số đo | mức | nghĩa |
|---|---:|---|---|
| Tham số **Trigger** (`m_Type = 9`) | **288** | **A** | mỗi state vào bằng 1 trigger đặt tên |
| Tham số **Bool** (`m_Type = 4`) | **15** | **A** | 15 chỗ dùng bool (bật/tắt liên tục) |
| Controller thuộc prefab `Boss-*` | **49** / 52 | **A** | chỉ 3 controller ngoài boss |
| **(tổng kiểm lại)** | **288** trigger · **15** bool · **49** controller boss | **A** | đọc từ `controller-graphs.json.gz`, không chép report |
| **Tên trigger phổ biến** | `Appear` **30** · `Attack2` **23** · `Die` **22** · `Attack1` **20** · `Attack3` **20** · `Attack4` **13** · `Attack6` **12** · `Attack5` **11** · `Attack7` **7** · `Mix2` **6** · `Idle3` **6** | **A** | tên **=** tên clip/state, không phải mã hoá |
| **Tên trigger cụ thể mà 6 call site trên truyền vào** | **chưa giải** — đối số là `string` hằng nạp từ metadata | **C** | cần bảng string literal của `global-metadata.dat`; **không** suy từ tên method |

⇒ **Chép lại đúng cách**: viết state machine **theo trigger tên clip** (`Appear`/`Attack1..16`/`Mix1..4`/
`Die`), rồi code gọi `SetTrigger(tên)` tại 3 vòng đòn + lúc súng chết + lúc mix. **Không** cần
`Animator.Play`, **không** cần timeline. Đây là "script animation" của 33 prefab boss ở mức
**cơ chế (A)**, chỉ thiếu **đúng 6 chuỗi** (C).

**Cùng họ, phía bắn đạn** — `Boss_AttackTypes` có **22 method**, trong đó 5 kiểu bắn lặp lại được
theo tên: `Fixed` · `Circle` · `Check` · `ArrangePositionX` · `RandomPositionX` (mỗi kiểu một cặp
`GetData…` + `IEGun…`), cộng `RegisterEvents` (**154** call — nối event 1 lần khi spawn) và
`OnBulletCollided` (**16** call). Đây là **bảng kiểu đạn của boss** cần dựng lại, không phải animation.

**Số đo của 5 kiểu bắn** (từ `float_evidence` của từng coroutine — mức **A** cho hằng số, **B** cho ý nghĩa):

| kiểu | hằng số đo được | đọc ra |
|---|---|---|
| `IEGunAttackAutoCircleBase` | `0.01745` · `90.0` · `−0.5` | bước quét **1° ≈ 0,01745 rad**/frame, cung 90°, bắt đầu lệch nửa bước |
| `IEGunAttackAutoCircle` | (dùng base) | quét liên tục |
| `IEGunAttackFixed` | `6.0` | bắn cố định (6 = số đạn? số đợt?) — **chưa chắc** |
| `IEGunAttackArrangePositionX` | `5.0` · `6.0` · `180.0` | dàn theo trục X, đối xứng 180° |
| `IEGunAttackRandomPositionX` | `−0.03141` · `180.0` | ngẫu nhiên trong nửa vòng |
| `IEGunCheckAttack` | `±6.0` · `±1.0` · `57.29578` | kiểm tra góc ngắm, đổi rad→deg |

---

## 4. Enemy — animation do code điều khiển, không do event (mức **A**/**B**)

Toàn bộ **795** event chỉ có **2** ngoài nhóm boss (`CB-30040`, clip `Die`, `Attack` @1,5 s) ⇒
**enemy không có timeline**. Script enemy = **3 lớp**:

| lớp | method chính | byte | việc |
|---|---|---:|---|
| `Enemy_Controller` | `Appear` 452 · `OnTakeDamage` 864 · `OnDieWhenZeroHp` 84 · `Stun` 148 · `Burn` 180 · `GainHealth` 188 · `SetDieCallback` 168 · `CacheComponents` 400 | 33 method | vòng đời: xuất hiện → nhận đòn → chết |
| `Enemy_Movement` | `Update` → **`PathFollow` / `MoveLinearly` / `MovePointToPoint`** · `MoveToPoint` → `StartCoroutine(IELinearMove)` · `OnPathEnded` → `UnityEvent.Invoke` · `SetEventMoveEnded` | 21 method | **máy trạng thái di chuyển** = "animation" của enemy |
| `Enemy_Destroy` | `Destroyed` 1052 · `OnDefeated` 544 · `OnBusrtItems` 500 · `OnDestroyByZeroHp` 292 · `OnDestroyWhenHitPlayer` 292 · `Pool` 320 | 12 method | chết → nổ item → trả pool |

`Enemy_Appear` là **base method** nhận `Action` **qua tham số `x1`** rồi tail-call đồng bộ. Điều đó
**không** chứng minh callback được gắn từ prefab: `Enemy_Controller.Appear` gọi **virtual dispatch**,
nên phải xét lớp con/override trước khi nói "không có animation riêng". (Sửa theo review 25/10, mục R3.)

### 4.0 Chuyển động — số đo trong code (mức **A**, mới 25/10)

`Enemy_Movement.Update` (`0x15861a4`) là **switch 3 nhánh**: `PathFollow` · `MoveLinearly` ·
`MovePointToPoint` — cả ba dùng `Time.get_deltaTime`, chỉ **khác nguồn toạ độ**:

| nhánh | nguồn toạ độ | hằng số | suy ra |
|---|---|---|---|
| `PathFollow` (`0x15861d4`) | `PathCreation.VertexPath.GetPointAtDistance(dst, …)` | `57.29578` (rad→deg) · `±1.0` (dấu) · `Time.deltaTime` | bay theo **path**; **hướng nhìn** = `atan2` của vector vận tốc ⇒ `set_eulerAngles` — đây là "animation quay đầu" của enemy |
| `MoveLinearly` (`0x1586618`) | `transform.position` + hướng | `deltaTime` | bay thẳng |
| `MovePointToPoint` (`0x158643c`) | `transform.position` → đích | `deltaTime` | bay tới điểm |

`OnPathEnded` (`0x15867e4`) chỉ có **một** lệnh: `UnityEvent.Invoke()` ⇒ "hết path" là **event rỗng
dây từ Inspector**, không phải code. `Enemy_Display.FixedUpdate` (`0x1585908`) lấy
`transform.parent.parent` rồi `set_eulerAngles` — **giữ sprite đúng hướng** mỗi frame vật lý.

⇒ Enemy **không có animation timeline**: chuyển động = tích phân path theo `deltaTime`, hướng = `atan2`,
va chạm/đổi trạng thái = `UnityEvent` hoặc trigger. Chép lại đúng 3 nhánh + 1 phép quay là đủ.

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

### 4.2 **70 enemy** có bao nhiêu animation thật? — đo bằng join 3 tập (mới 25/10, mức **A**)

Nguồn: roster **109** tên lấy từ `datas/waves.json` (39 `Boss-*` + **70** enemy), **87** root có
`Animator` trong `datas/animator_map.csv.gz`, graph đọc từ `controller-graphs.json.gz`. Đây là lần
đầu tách **boss khỏi enemy** khi nói "87/109 có Animator" — con số 87 **không phải** của riêng enemy:

**109 roster = 39 boss + 70 enemy · 87 có Animator · 27 chỉ `Afterburner` · 19 không Animator.**

| nhóm | số prefab | Animator | đọc là |
|---|---:|---|---|
| boss `Boss-*` | **39** | 36 | có máy trạng thái riêng (§3.6) |
| **enemy (không boss)** | **70** | **51** | trong đó **27 chỉ** có `Afterburner` = **0 param · 1 state** (`idle`) ⇒ **không có** máy trạng thái |
| enemy có máy trạng thái thật | **24** | 24 | 10 controller riêng (dưới); 5 `XB-*` có `Afterburner` **thêm** controller riêng |
| enemy **không có** `Animator` | **19** | 0 | chỉ có sprite + script chuyển động (§4.0) |

**Danh sách 24 prefab có controller riêng** (10 tên — cluster lớn nhất ngoài boss):

| controller | prefab | param | state |
|---|---:|---:|---|
| `CD-31002` | **12** (`CD-31002/03/04/05/06/07/08/09/10/13/15/16`) | *chưa có graph* | *chưa có graph* |
| `Body` | 1 (`CB-30038`) | **2** trigger (`Move` · `Idle`) | **2** |
| `Enemy_Ingame` | 1 (`CB-30040`) | **1** trigger (`Die`) | **2** |
| `BB-36001` · `BB-36002` (dùng cho cả `BB-36003`) · `BB-36004` | 4 | *chưa có graph* | *chưa có graph* |
| `Jelly` (`CD-31014`) · `Nguoi`+`Supply` (`H-38002`) · `W2-30033` (`W2-30033/34`) · `Trap_Circle` (`W2-30035`) · `W2-30037` | 7 | *chưa có graph* | *chưa có graph* |

⇒ **14** controller không thuộc boss; **11** trong số đó **chưa có graph** (10 tên, `BB-36002` có 2 id) ⇒
đây là **việc còn thiếu duy nhất** của phần enemy animation, và nó **nhỏ**: 11 controller, không phải 87.

**Kết luận cho người dựng lại:** với **46/70** enemy (**27** chỉ `Afterburner` + **19** không Animator), "animation"
= **1 sprite + script 3 nhánh + nháy trúng đòn 0,05 s**. Chỉ **24** prefab cần dựng state machine, và
phần lớn là 2 state (`Move`/`Idle`) hoặc `Idle`/`Die`. Đừng dựng 109 bộ animation.

> ⚠️ Nếu ai đó nói "87/109 enemy có Animator", câu đúng là: **87/109 roster**, trong đó **39 con là boss`;
> riêng enemy là **51/70**, và **27/51** chỉ là một state.

## 5. Bảng chép lại được / không chép được

| hạng mục | chép được? | nguồn |
|---|---|---|
| Tên + mốc thời gian 793 event boss (+2 event `CB-30040`) | **A** | `event-receivers.json.gz` · chi tiết: **`BOSS_ANIM_TIMELINE.md`** |
| Nhịp đòn (0,17 · 0,33 · 1,0 · 5,0 s) | **A** | suy từ `time` |
| Danh sách clip theo boss (14 đòn/boss) | **A** | `clip_name` |
| Chuỗi hàm boss 1 + hằng chờ (0,5/1/2/3 s) | **A** | asm `Boss1_Director` |
| Máy trạng thái enemy (3 nhánh move) | **A** | `native-calls.json` |
| Hit flash 0,05 s | **B** | suy từ asm `Enemy_Display.OnHit` |
| 2 tên event Spine ↔ hành vi | **A-static (identity) / MODEL_NOT_MEASURED (dispatch)** | slot `0x2ADFB48` → literal `Stop` (ef123) · `Banplasma` chưa bind |
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
python3 tools/verify-claims.py              # toàn bộ: 166 PASS · 0 FAIL · 2 SKIP
```

Nguồn: `reverse-engineering/raw/animation-audit/event-receivers.json.gz` (795 event) ·
`…/native-calls.json` (272 method, direct call + hằng số) ·
`reverse-engineering/raw/il2cpp-consts/*.asm.txt` (69 file) ·
`datas/spine_anim.json.gz` (event trong rig Spine).
