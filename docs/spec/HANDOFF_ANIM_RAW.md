# HANDOFF_ANIM_RAW — giao việc **đào raw** cho nhánh dữ liệu

> **Đây là bản yêu cầu cho nhánh phân tích ngược** (`arena/ef6b75ef-…`). Tôi **không** commit sang
> nhánh đó; tôi chỉ `git fetch` và đọc. File này nằm trong `docs/spec/` của nhánh Arena.
>
> **Chỉ đạo của chủ dự án:** *"phần việc nào cần phân tích mà đào raw thì giao cho nhánh bên kia"*.
> ⇒ Mọi việc **cần export thêm asset hoặc xref asm** nằm ở đây. Mọi việc **đọc được từ dữ liệu đã
> có** thì tôi đã làm xong, liệt kê ở §0 để **không ai làm lại**.
>
> Bốn task dưới đây **độc lập**, **không cần thiết bị**, và mỗi task là **một giả định sai được**.

---

## 0. Đã xong — **đừng làm lại**

| Hạng mục | Kết quả | Nguồn |
|---|---|---|
| Tên entry Spine của boss 1 | **8 chuỗi**: `Xuathien` · `Baydi` · `Dead` · `Attack1` · `Attack2` · `Attack3` · `Chuyensangattack2` · `Chuyensangattack3` | `typetrees/Boss1_Director.jsonl.gz` |
| Vị trí bộ nhớ của 8 chuỗi | `0x28`→`0x60`, suy từ `Start` gọi `SetAnimation(0, [0x28], loop=false)` | `Boss1_Director.asm.txt` |
| Bảng chuyển state của boss 1 | **5 nhánh** `BossWork`; `Xuathien`→`Attack1` loop · `Chuyensangattack2`→`Attack2` loop · `Chuyensangattack3`→`Attack3` loop · `Baydi`/`Dead`→`Defeat()` | asm `BossWork` 280 B |
| Cầu nối Spine → code | `SkeletonAnimation_AnimationState_Complete(TrackEntry)` = **tail-call** `BossWork(trackEntry.Animation.Name)`, 50 B | asm |
| Nhịp 33 prefab boss | **793 event**, 129 tên hàm, nhịp **0,17 / 0,33 / 1,0 / 5,0 s** | `event-receivers.json.gz` |
| Hit flash enemy | **0,05 s** qua `Invoke`, alpha **0,5**, 2 hằng số trong `Enemy_Display.OnHit` | `native-calls.json` |
| Nhịp pha boss | **38** lần `WaitForSeconds`, **12** hằng số (0,5 / 1 / 2 / 3 s), **26** lấy từ biến | asm **139** file (bản `9edc21f4d`) |
| Ghép **prefab ↔ lớp handler** | **17/34** prefab (17 còn thiếu, **145** event), quan hệ **1:1**, từ **18** lớp `*_AnimationEvents` đã export (`typetrees/*AnimationEvents*` là export **theo instance**, `gameobject` = đường dẫn trong prefab) | claim **S1** |
| Timeline theo giây của 269 cặp (prefab, clip) | `BOSS_ANIM_TIMELINE.md` — 795 event, 130 tên hàm | claim **R1–R6** |
| Tên field 12 delegate + 5 field `BossSpineEventHandler` | `interesting-classes.cs` (kéo 24/10) | claim **T2**, **T3** |
| 8 tên entry boss 1 đọc thẳng từ prefab | `Boss1_Director.csv`: `Boss-39002`, **1** instance | claim **T1** |
| Ma trận `*_Director` ↔ `*_AnimationEvents` | **18** / **18** / **15** trên 39 prefab `Boss-*` | claim **T4** |
| **Ai đặt trigger `Animator`** | **7 call site `Animator.SetTrigger` / 5 method**, tất cả trong `Boss_AttackPhases` (`CallMixAnimation` · `OnGunDie` · 3 vòng `IEAttackRound*`) | `native-calls.json`, claim **W1** — **đừng** đi tìm lại |
| **Tên trigger** | **288** trigger (`m_Type=9`) · **15** bool · **49/52** controller boss; `Appear` 30 · `Attack2` 23 · `Die` 22 · `Attack1` 20 | `controller-graphs.json.gz`, claim **W2–W3** |
| **Chuyển động enemy** | `Update` 3 nhánh · `PathFollow` dùng `VertexPath.GetPointAtDistance` + hướng `atan2`×`57.29578` · `OnPathEnded` = `UnityEvent.Invoke()` | `native-calls.json`, claim **W4** |

Tất cả số trên đã khoá bằng claim `J*` + `K*` trong `tools/verify-claims.py`.

---

## 1. Bốn task

### T1 — **17 prefab** có event clip nhưng chưa export lớp handler

> **Tách route (sync-review `152` + ef123, 27/10):** việc mở chia 2 route — **(a) Boss-39001**
> handler identity/instance/serialized values (E1 — nguồn serialized mới từ lane dữ liệu);
> **(b) Boss-39002** slot `0x2ADFB48` — **identity ĐÃ resolve = `Stop`** (ef123 native lane,
> spec-ACK lần 93/94 giao; dispatch `MODEL_NOT_MEASURED` — E2 hết blocked ở tầng identity).
> **Không lặp lại census văn bản đã đóng (p20–22)** — chỉ nguồn mới được phép/được uỷ quyền.

**Cập nhật 25/10 (số đúng của snapshot `9aed767b1`):** bản đầu ghi *"3 lớp thiếu typetree"*; bản
24/10 ghi **18 prefab / 262 event** (số của `019e704d1`). Đo lại: **17 prefab** còn thiếu, **145 event
/ 795 = 18 %** (`Boss-37001/02/04/09/10/11/12/13/14/15/16/17`, `Boss-39003/05/09/11/21` bớt nhóm đã
ghép, `CB-30040`) — claim **S1** giữ đúng bộ số `(17, 17, 145, 34)`. Danh sách chính xác phải lấy
bằng `event-receivers.json.gz` ⋈ `typetrees/*AnimationEvents*`, **không** chép tay từ đây.

**2 lớp** ở trạng thái **có asm nhưng không có typetree** (có `il2cpp-consts/*.json`, **0** instance
export): `Boss1_AnimationEvents` · `BossSpineEventHandler`. Lớp thứ ba, **`Boss_1_Animation`, đã xong
25/10**: có **1 instance** trên `Boss-39001` (`Boss_1_Animation.csv`, snapshot `9aed767b1`), 8 field
`state*` + 2 `UnityEvent` (`defeatEvent` → `OnDefeated`, `burstEvent` → `OnBusrtItems`).
Đây chỉ là phần *nhỏ nhất* của T1, không phải toàn bộ.

**Giả định:** mỗi prefab trong 18 cái đó có **đúng một** lớp `*_AnimationEvents` (như 16 prefab đã
ghép được, quan hệ 1:1), và lớp đó **có** trong `il2cpp-consts/*.json` (69 lớp đã dump) nhưng chỉ
**thiếu bước export instance**.

**Việc (đã hẹp lại 24/10 — tên field không còn phải tìm):**

| lớp | đã biết | còn thiếu | việc |
|---|---|---|---|
| `BossSpineEventHandler` | **5 field** + offset + cơ chế `HandleEvent` | **giá trị** `attackEventName` / `preAttackEffectEventName` | export **instance** (chỉ cần 1 dòng) |
| `Boss1_AnimationEvents` | **12 field** `0x20…0x78` + tên | **có gắn prefab nào không** | export **instance** |
| `Boss_1_Animation` | ✅ **XONG 25/10**: 1 instance trên `Boss-39001`; 8 field `state*`; 2 `UnityEvent` | — | — |

1. thêm 3 lớp trên vào `TARGETS` của exporter typetree (**lớp `*_AnimationEvents` khác đã export đủ 14**);
2. xuất `typetrees/{class}.jsonl.gz` (**instance**, kèm `gameobject`) + `script-links.jsonl.gz`;
3. in **giá trị** field chuỗi của 2 lớp đầu.

**Artifact:** `anim-raw-T1/instances.json`
```json
{"class": "BossSpineEventHandler", "count": 0, "prefab_roots": [],
 "string_fields": {"onEventName": "...", "offEventName": "..."}}
```

**Tự kiểm:** in `(số prefab ghép được, số prefab còn thiếu)` — mốc hiện tại **(16, 18)**; sau task
phải là **(34, 0)** hoặc ghi rõ lớp nào **không tồn tại** trong assembly.

**Lật ngược nếu:** export xong mà `Boss1_AnimationEvents` vẫn **0 instance** trong **phạm vi export** ⇒
ghi **"không tìm thấy trong tập này"**, **không** kết luận "code chết": 0 instance export ≠ 0 instance
runtime (có thể lớp được `AddComponent` lúc chạy, hoặc prefab nằm ngoài tập). Khi đó 12 handler ở §T2
**không** phải đường mà 16 prefab kia dùng — điều này không làm hỏng gì: 16 prefab đã ghép được lớp thật
(`Boss10_…`, `BossAnimationEvents`, …). (Hạ mức theo review 25/10, mục R6-T1.)

**Lật ngược (2):** field chuỗi của `BossSpineEventHandler` **không phải** `Stop` / `Banplasma` (2 tên
event duy nhất trong rig `skeleton__21`) ⇒ ứng viên ở `ANIMATION_SCRIPT.md` §2.2 sai.

**Mở khoá:** nhánh Spine từ **B** lên **A**; biết `Boss_1_Animation` là bản cũ của `Boss1_Director`
hay lớp riêng; và **33 % event** còn lại có chủ.

---

### T2 — Ai gán **12 delegate field** của `Boss1_AnimationEvents`

**Giả định:** có một lớp khác (`*_Director` / `*_Animation`) gán 12 field này bằng `+=`, và tìm
được bằng xref trong asm **đã có** — không cần chạy game.

12 handler là **12 delegate field liền nhau `0x20`…`0x78`**, đúng thứ tự khai báo:

| offset | method | offset | method |
|---|---|---|---|
| `0x20` | `OnAnimationEndedEvent` | `0x50` | `Attack2StartCheckShoot` |
| `0x28` | `OnDie` | `0x58` | `Attack12Shoot` |
| `0x30` | `Attack1HandLeft` | `0x60` | `OnCallAttack4Event` |
| `0x38` | `Attack2HandRight` | `0x68` | `OnCallAttack6Event` |
| `0x40` | `Attack3TwoHands` | `0x70` | `OnCallAttack9StartEvent` |
| `0x48` | `Attack1StartCheckShoot` | `0x78` | `OnCallAttack9EndEvent` |

> **Cập nhật 24/10:** 12 field dưới đây là của **`Boss1_AnimationEvents`**. 16 prefab đã ghép lớp
> dùng **lớp khác** (`Boss10_AnimationEvents`, `BossAnimationEvents`, `Boss4_…`), mỗi lớp có bộ tên
> riêng ⇒ task này phải chạy **theo từng lớp**, không chỉ lớp `Boss1`. Bản đồ prefab→lớp: claim **S1**.

**Tên + offset đã có (24/10)** — `interesting-classes.cs` cho đúng 12 field `0x20…0x78` kèm method.
Task này vì thế **chỉ còn một câu**: *ai gán chúng*.

**Việc:** trong toàn bộ asm (không chỉ 69 file đã export), tìm lệnh ghi vào `[xN + offset]` với
`offset ∈ {0x20…0x78}` trên đối tượng thuộc lớp `*_AnimationEvents`; hoặc tìm `Delegate.Combine` /
`Action.ctor` có `MethodInfo` trỏ tới đúng 12 method trên.

**Artifact:** `anim-raw-T2/delegate-wiring.json`
```json
[{"field_offset": "0x28", "handler": "OnDie",
  "setter_class": "...", "setter_method": "...", "rva": "0x..."}]
```

**Tự kiểm:** đếm **số handler có ít nhất một chỗ gán** (kỳ vọng 12, không phải "có vẻ nhiều").
Handler chưa tìm thấy phải liệt kê riêng — đó là dữ liệu, không phải thất bại.

**Lật ngược nếu:** **0/12** tìm thấy ⇒ ghi **"0 xref trong phạm vi đã quét"**, **không** suy ra
"không có C# assignment": chưa chứng minh coverage toàn binary / toàn type / indirect call /
registration. Trùng offset **không** đủ xác định type. Ghi REVERSED kèm phạm vi quét. (review R6-T2)

**Mở khoá (thu hẹp 25/10, review R2):** 12 handler này **chỉ** thuộc lớp `Boss1_AnimationEvents`; **không**
phải chìa khoá cho 793 event của 33 prefab boss — các prefab đó dùng lớp khác (`Boss10_AnimationEvents`
78 use · `BossAnimationEvents` 246 · `Boss9_…` 48 · `Enemy_Sync_Attack2` 24 …). Số đó là **candidate
records**, không cộng thành unique event khi còn nhập nhằng. Việc phải làm là bảng theo từng
**(prefab, Animator GO, receiver component/class, method, binding, hành vi)**, ưu tiên receiver **có
instance thật**. Không tìm thấy lớp ≠ lớp không bao giờ được tạo runtime.

---

### T3 — `UnityEvent` persistent calls  · ✅ **đã có raw 25/10**

> **Kết quả từ nhánh dữ liệu (report 39, snapshot `9aed767b1`):** **1.335** field `UnityEvent`,
> **111** field không rỗng, **115** persistent call — **114** trong nhóm enemy/boss.
> `Enemy_Movement.moveEndedEvent` chỉ có **2** instance không rỗng (không phải cả 981).
> `Enemy_Attack_Event.startShootEvent` / `stopShootEvent` là cặp **mở/đóng cửa sổ bắn** wire bằng
> Inspector trên từng khẩu súng. ⇒ Phần *liệt kê* xong; phần còn lại chỉ là **đọc giá trị**.


**Giả định:** các callback không phải delegate field — `Enemy_Movement.OnPathEnded`,
`BossSpineEventHandler` slot #1 `[0x38]` — là **`UnityEvent` có `m_PersistentCalls` khác rỗng**,
nên đọc được "gọi hàm nào trên object nào" mà không cần chạy game.

**Việc:** export object `UnityEvent` (PPtr từ field `UnityEvent` trong mỗi MonoBehaviour) và
`m_PersistentCalls.m_Calls[]` (`m_Target`, `m_TargetAssemblyTypeName`, `m_MethodName`, `m_Mode`,
`m_Arguments`, `m_CallState`).

**Artifact:** `anim-raw-T3/unityevent-calls.json`
```json
[{"prefab": "Enemy_...", "owner_class": "Enemy_Movement", "owner_field": "eventMoveEnded",
  "calls": [{"m_Target": {"m_PathID": 0}, "m_MethodName": "...", "m_Mode": 1}]}]
```

**Tự kiểm:** `(số prefab có ≥1 persistent call, tổng số call)`.

**Lưu ý phạm vi (R6-T3):** `UnityEvent` thường là dữ liệu **inline** trong prefab, **không** phải asset
PPtr riêng — PPtr chỉ là `m_Target`/`m_ObjectArgument` bên trong. Tập export rỗng **không** đại diện
mọi prefab nếu thiếu class/tree. Raw mới **đã có** persistent calls ⇒ trong tập này **không** còn giả
thuyết "mọi thứ nối bằng code".

**Lật ngược nếu:** tổng số call = **0** trên toàn bộ prefab ⇒ game **không** dùng Inspector-wired
event; mọi thứ nối bằng code. Đó cũng là một câu trả lời đóng §T3, không phải lỗi.

**Mở khoá:** `Enemy_Movement.OnPathEnded` → chuyện gì xảy ra; và kiểm chéo kết luận §T2.

---

### T4 — `Animator`: tham số + transition của **87 prefab roster**  · ✅ **đã có raw 25/10**

> **Kết quả (report 40):** **52** controller trên **63** prefab root (lọc `CB-`/`Boss-`/`MB-`),
> **303** parameter, **395** state, **357** transition (**302** có condition). Parameter lấy tên từ
> `m_TOS` bằng hash id; condition lấy từ `m_ConditionConstantArray` (**không** đoán từ tên state).
> Raw: `raw/typetrees/animator-controller-graphs.jsonl.gz` (**308** controller).
> ⚠️ **Không** cùng mẫu số với roster 109/87 ⇒ **chưa** được báo "đóng 87/87".


**Giả định:** enemy chuyển state bằng **tham số Animator** (Bool/Trigger/Float), nên đọc được
điều kiện chuyển state từ `AnimatorController`.

**Việc:** export `Animator` + `RuntimeAnimatorController` cho đúng **87 prefab** (roster 109 tên,
định nghĩa ở `ANIMATION.md` §4.5, claim `B15`) và xuất `parameters[]`, `states[]`,
`transitions[{from, to, conditions[{mode, threshold}], hasExitTime}]`.

**Artifact:** `anim-raw-T4/animator-graph.json`
```json
[{"prefab": "...", "controller": "Afterburner",
  "parameters": [{"name": "...", "type": "Bool"}],
  "states": ["Idle", "Run"], "transitions": 12}]
```

**Tự kiểm:** `(số prefab, số controller phân biệt, tổng parameter, tổng transition có điều kiện)`.
Mốc đã biết: `datas/animator_map.csv.gz` có **5.792** dòng, `Afterburner` là controller phổ biến
nhất (**72** dòng enemy).

**Lưu ý phạm vi (R6-T4):** 0 parameter **không** chứng minh `Animator.Play` — graph có thể tự chạy /
thoát theo exit-time, crossfade, override, hoặc Playables. Chỉ **xref `Play`** mới xác nhận `Play`.

**Lật ngược nếu:** tổng parameter = **0** ⇒ enemy dùng `Animator.Play("tên clip")` từ code; khi đó
task kế là xref các lệnh gọi `Play`, **không** phải đọc parameter.

**Mở khoá:** "animation enemy = máy trạng thái" từ mức **A về cấu trúc** lên **A về điều kiện**.

---

### T4b — **6 chuỗi trigger** mà `Boss_AttackPhases` truyền vào `Animator.SetTrigger` (mới 25/10)

**Đã biết (không cần tìm lại):** `Animator.SetTrigger` có **7 call site / 5 method**, tất cả trong
`Boss_AttackPhases` — `CallMixAnimation` `0x152e880` · `OnGunDie` `0x15326d0` · 3 vòng
`IEAttackRound1/2/3` `0x1532f74`/`0x1533428`/`0x1533978` (+2 trong cùng coroutine); mỗi site nạp
đối số `x1` từ **hằng chuỗi metadata** rồi `bl #0x27583b0`. Tên trigger trong controller là **288**
chuỗi đã có (`Appear`, `Attack1`…`Attack16`, `Mix1..4`, `Die`, …).

**Còn thiếu:** **chuỗi cụ thể** ở 6 site đó. Đây là chỗ **không** suy được từ asset: cần bảng
`string literal` của `global-metadata.dat` (offset metadata ↔ chuỗi) — việc **đào raw**, không phải
đọc prefab.

**Việc:** với mỗi site, lấy `ldr x1, [x8, #off]` (x8 = `Il2CppMetadataUsage` của lớp) → tra bảng literal
→ in `(method, rva, chuỗi)`. Nếu bảng literal không có, xuất **offset metadata** thôi cũng đủ để tôi
đối chiếu chéo với 288 tên trigger đã có (khớp duy nhất hay không).

**Artifact:** `anim-raw-T4b/trigger-strings.json`
```json
[{"caller": "Boss_AttackPhases.CallMixAnimation", "rva": "0x152e880",
  "metadata_offset": "0x...", "string": "Mix1" | null}]
```

**Tự kiểm:** `(số site có chuỗi, số site chỉ có offset)` = **(6, 0)** khi xong; chuỗi phải nằm trong
tập **288** tên trigger đã export — nếu không, ghi rõ là trigger **không** thuộc 49 controller đã đọc.

**Lật ngược nếu:** chuỗi không khớp bất kỳ tên trigger nào ⇒ `SetTrigger` gọi trên Animator **khác**
(không phải controller của prefab boss) — khi đó phải export thêm `Animator` runtime.

---

## 1b. T5 — `rate = 0` nghĩa là gì (mật độ địch)

Không phải việc animation, nhưng **cùng loại việc** (cần asm chưa export), và nó là **blocker #1**
của `DESIGN_READINESS.md` §6.

> **Cập nhật 24/10 — đã hẹp bằng dữ liệu kéo về:** `Call_Data.csv` (1.200 dòng, 23 field) **không
> có** field `delay`/`wait`/`interval` nào ⇒ `rate` là **field thời gian duy nhất**; và `number = 0`
> ở 1.200/1.200 dòng ⇒ số quân = **độ dài `listPrefabEnemies`**. Xem `DESIGN_READINESS.md` §3.1.
> Task này vì thế **không còn chặn thiết kế**, chỉ còn để lên mức A.

**Giả định:** `rate` là **khoảng cách giây giữa hai lần spawn** ⇒ `rate = 0` = spawn **tức thời cả
loạt** (không phải mỗi frame).

**Việc:** export asm của lớp spawner (lớp có method dùng `rate`; hiện **không có** trong
`il2cpp-consts/`), tìm chỗ `rate` được dùng: `InvokeRepeating`, `Time.deltaTime` cộng dồn, hay so
sánh ngưỡng.

**Artifact:** `anim-raw-T5/rate-semantics.json`
```json
{"class": "...", "method": "...", "rva": "0x...", "use": "invoke_repeating|accumulator|threshold",
 "rate0_behaviour": "burst|per_frame|never"}
```

**Tự kiểm:** đếm **số chỗ đọc field `rate`** trong asm (kỳ vọng ≥1, liệt kê đủ).

> **Cảnh báo diễn giải (R5, 25/10):** `rate = 0` là **quan sát A**; cách đọc nó (không giãn cách /
sentinel / default) vẫn là **giả thuyết** cho tới khi có consumer asm. Số quân/wave **không** đồng
nghĩa mật độ theo thời gian (quân/giây). Không dùng lý do "game đã phát hành" làm bằng chứng.

**Lật ngược nếu:** `rate` là **số quân mỗi giây** (không phải khoảng cách) ⇒ `rate = 0` = **không
spawn**, và 2.371 spawner đó phải có cơ chế khác kích hoạt (ví dụ `copies`). Khi đó §3 của
`DESIGN_READINESS.md` phải viết lại, không chỉ sửa số.

---

## 1c. T6 — **map → wave**: đánh số 250 map

Đây là **blocker #1** của `COVERAGE_AUDIT.md` §2.

**Giả định:** `maps.json` (**250** map, thứ tự zero-based, `listMapDatas @0x28`) + `31-map-tables.md`
(**540/540** token `InitializeArray` có blob, **0** token bó tay) là **đủ** để suy `map N ↔ wave nào`.

**Việc:** ghép 250 mảng với 282 wave bằng **khoá nội dung** (số wave + tổng spawner của từng mảng),
**không** bằng thứ tự. `14-Data_Boss.csv` (**46** boss, mỗi boss có `idWave`) dùng làm **mỏ neo
ngược**: boss nào thuộc wave id nào thì map chứa wave đó phải chứa boss.

**Artifact:** `map-wave-join.json`
```json
[{"map_index": 1, "wave_ids": [..], "confidence": "token|content|boss-anchor"}]
```

**Tự kiểm:** số map ghép được **bằng chứng token** phải **tăng từ 7**; mọi map ghép phải khớp **tổng
spawner** của các wave được gán; 46 boss phải rơi đúng map.

**Lật ngược nếu:** vẫn **7/250** ⇒ nội dung `maps.json` **không** phải map→wave; khi đó chỉ còn
đường `idWave` của boss (46 mỏ neo) và phải nói rõ "chỉ biết 46/299 stage".

---

## 1d. T7 — **trigger âm thanh**: 92 sound id ↔ sự kiện

**Giả định:** code gọi âm thanh qua một registry (`SoundClip`) bằng **tên hằng chuỗi**, nên tìm được
xref "sự kiện nào phát id nào" trong asm đã có.

**Việc:** tìm các lời gọi phát âm (method nhận `string`/`enum` sound id), đối chiếu với **92 id**
trong `datas/audio_map.json` (**92/92** đã resolve ra file).

**Artifact:** `audio-triggers.json`
```json
[{"sound_id": "Bgm_Boss1", "caller_class": "...", "caller_method": "...", "rva": "0x..."}]
```

**Tự kiểm:** `(số id có ít nhất 1 caller, số class gọi)` trên 92 id. Id **không** có caller phải
liệt kê — đó là dữ liệu (có thể do prefab `UnityEvent` phát).

**Lật ngược nếu:** **0/92** tìm thấy ⇒ âm thanh phát qua `UnityEvent`/`AudioSource` trên prefab;
khi đó gộp vào T3 và đóng bằng `m_PersistentCalls`.

---

---

## 1e. T9 — **rect của `Sprite`** để cắt 67 page `sactx-*` (asset, không phải animation)

**Vì sao:** `ASSET_TRIAGE.md` §2 đo được **132** sheet `Texture2D` (**116** chưa có sprite nào) và
**67** page `sactx-*` (31,05 MB) — muốn cắt đúng sprite ra khỏi page phải có rect, hiện **không có**
trong export nào.

**Việc:** export cho **2.185** `Sprite` (và 653 `Texture2D` nếu có): `m_RD.texture` (PPtr),
`m_RD.rect` (x,y,w,h), `m_RD.textureRect`, `m_RD.settingsRaw` (packed/packingMode), `m_PixelsToUnits`.

**Artifact:** `asset-raw-T9/sprite-rects.jsonl.gz` — mỗi dòng
`{"sprite": "NutBuySkin 1", "path_id": 123, "texture": {"fileID": 3, "pathID": 456}, "rect": [x,y,w,h], "ppu": 100}`

**Tự kiểm:** `(số sprite có rect, số page nhận được ≥1 sprite)`; mọi rect phải nằm trong page tương ứng;
tổng diện tích rect ≤ diện tích page.

**Lật ngược nếu:** export ra **0** rect ⇒ sprite sinh lúc chạy hoặc atlas đóng gói bằng công cụ khác;
khi đó chỉ còn đường cắt theo lưới khai báo trong tên (`1_5x2` · `k_1__2x3`, 16 ô) và ghi rõ là **thiếu**.

---

## 2. Hợp đồng chạy (giống `PARALLEL_TASKS.md`, rút gọn cho các task: T1–T4 · T4b · T5 — sync-review `152` P2)

| # | Luật | Vì sao |
|---|---|---|
| 1 | Job **không** `git push`, chỉ `upload-artifact` tên `anim-raw-T{n}` | 4 job chạy cùng lúc không tranh chấp |
| 2 | `permissions: contents: read` | job không sửa được repo |
| 3 | Mỗi job tự chứa, không `needs` job khác; `fail-fast: false` | 1 task hỏng không giết 3 task kia |
| 4 | Kết quả ghi `verdict.json`: `{"task":"T1","verdict":"PASS\|REVERSED\|MISSING","counts":{...}}` | job hợp nhất chỉ đọc JSON, không đọc log |
| 5 | Exit code: **0** PASS · **2** REVERSED · **3** MISSING (thiếu input) | mã thoát = phán quyết |

**Thứ tự ưu tiên nếu chỉ chạy được một task:** **T1** (rẻ nhất — chỉ thêm 3 dòng vào `TARGETS`,
mở khoá nhánh Spine) → **T2** (chỉ lớp `Boss1_AnimationEvents`, **không** phải 793 event) → **T6** (map→wave, blocker #1 của
`COVERAGE_AUDIT.md`) → **T5** (mật độ địch) → **T3** → **T7** (âm thanh) → **T4** (đắt nhất, cần đọc
`AnimatorController` trong bundle).

---

## 3. Sau khi có kết quả

| Task xong | Tôi sẽ sửa ở đâu |
|---|---|
| T1 | `ANIMATION_SCRIPT.md` §2.2 (**B → A** hoặc xoá hẳn nếu 0 instance) |
| T2 | `ANIMATION_SCRIPT.md` §3.1 (**C → A**), bảng "event → hàm → hành vi" |
| T3 | `ANIMATION_SCRIPT.md` §4 (`Enemy_Movement.OnPathEnded`), `ENEMY_BEHAVIOUR.md` |
| T4 | `ANIMATION_SCRIPT.md` §4.2 mới: điều kiện chuyển state của enemy |

Mỗi kết quả về sẽ thành **claim mới** trong `tools/verify-claims.py` (nhóm `K`/`L`), không nhận
số bằng lời.
