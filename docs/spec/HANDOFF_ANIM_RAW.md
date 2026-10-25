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
| Nhịp pha boss | **22** lần `WaitForSeconds`, **4** hằng số (0,5 / 1 / 2 / 3 s), **18** lấy từ biến | asm 69 file |

Tất cả số trên đã khoá bằng claim `J*` + `K*` trong `tools/verify-claims.py`.

---

## 1. Bốn task

### T1 — Ba lớp **có asm nhưng không có typetree**

**Giả định:** `Boss1_AnimationEvents`, `BossSpineEventHandler`, `Boss_1_Animation` **có** instance
trên prefab boss 1 (`Boss-39001` / `Boss-39002`), và field chuỗi của chúng nằm trong **cùng bộ tên
entry** đã biết ở §0.

**Việc:** thêm 3 lớp vào `TARGETS` của exporter typetree, chạy lại, xuất
`typetrees/{class}.jsonl.gz` + đếm instance qua `script-links.jsonl.gz`.

**Artifact:** `anim-raw-T1/instances.json`
```json
{"class": "BossSpineEventHandler", "count": 0, "prefab_roots": [],
 "string_fields": {"onEventName": "...", "offEventName": "..."}}
```

**Tự kiểm:** in ra `(số instance, số field chuỗi)` cho từng lớp. Hiện tại `script-links` có **0**
instance cho cả 3 lớp — nếu sau khi export vẫn **0** thì kết luận của task là **REVERSED**:
chúng là **code không gắn prefab nào** (và 12 handler ở §T2 chỉ có thể do `Boss-37xxx` dùng).

**Lật ngược nếu:** field chuỗi của `BossSpineEventHandler` **không phải** `Stop` / `Banplasma`
(2 tên event duy nhất trong rig `skeleton__21`) ⇒ ứng viên ở `ANIMATION_SCRIPT.md` §2.2 sai và
phải tìm tên khác trong `datas/spine_anim.json.gz`.

**Mở khoá:** nhánh Spine từ **B** lên **A**; biết `Boss_1_Animation` có phải bản cũ của
`Boss1_Director` hay không.

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

**Lật ngược nếu:** **0/12** tìm thấy ⇒ 12 handler không được gán bằng code C# trong assembly này
(có thể do prefab `AnimationEvent` gọi thẳng, hoặc lớp chưa từng được dùng). Ghi rõ là REVERSED.

**Mở khoá:** "sự kiện → hành vi" của **793 event** trên 33 prefab boss, tức mức **C → A** cho nửa
còn lại của `ANIMATION_SCRIPT.md`.

---

### T3 — `UnityEvent` persistent calls

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

**Lật ngược nếu:** tổng số call = **0** trên toàn bộ prefab ⇒ game **không** dùng Inspector-wired
event; mọi thứ nối bằng code. Đó cũng là một câu trả lời đóng §T3, không phải lỗi.

**Mở khoá:** `Enemy_Movement.OnPathEnded` → chuyện gì xảy ra; và kiểm chéo kết luận §T2.

---

### T4 — `Animator`: tham số + transition của **87 prefab roster**

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

**Lật ngược nếu:** tổng parameter = **0** ⇒ enemy dùng `Animator.Play("tên clip")` từ code; khi đó
task kế là xref các lệnh gọi `Play`, **không** phải đọc parameter.

**Mở khoá:** "animation enemy = máy trạng thái" từ mức **A về cấu trúc** lên **A về điều kiện**.

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

## 2. Hợp đồng chạy (giống `PARALLEL_TASKS.md`, rút gọn cho 4 task)

| # | Luật | Vì sao |
|---|---|---|
| 1 | Job **không** `git push`, chỉ `upload-artifact` tên `anim-raw-T{n}` | 4 job chạy cùng lúc không tranh chấp |
| 2 | `permissions: contents: read` | job không sửa được repo |
| 3 | Mỗi job tự chứa, không `needs` job khác; `fail-fast: false` | 1 task hỏng không giết 3 task kia |
| 4 | Kết quả ghi `verdict.json`: `{"task":"T1","verdict":"PASS\|REVERSED\|MISSING","counts":{...}}` | job hợp nhất chỉ đọc JSON, không đọc log |
| 5 | Exit code: **0** PASS · **2** REVERSED · **3** MISSING (thiếu input) | mã thoát = phán quyết |

**Thứ tự ưu tiên nếu chỉ chạy được một task:** **T1** (rẻ nhất — chỉ thêm 3 dòng vào `TARGETS`,
mở khoá nhánh Spine) → **T2** (mở khoá 793 event) → **T6** (map→wave, blocker #1 của
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
