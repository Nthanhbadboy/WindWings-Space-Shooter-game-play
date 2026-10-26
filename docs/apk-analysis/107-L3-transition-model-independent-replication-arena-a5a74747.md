# 107 — REPLICATION độc lập transition model — arena/a5a74747

**Phạm vi có giới hạn, tạm thời.** Đây là **đối chiếu/recount độc lập ở cấp artifact đã decode**,
không phải parser APK thứ hai, không phải Unity readback, không phải runtime, và không render. Mục
#16 trong BẢNG ĐIỀU PHỐI PR12; claim trước khi làm ở comment `6411344770`.

## 1. Trả lời ngắn

Tôi viết một tool mới, không import `l3_transition_scheduler.py`, tự đi lại các mảng constant
đã decode trong `datas/l3_animator_programs.json.gz`, tự đếm và so sánh có thứ tự với
`datas/l3_transition_model.json.gz` theo identity controller đầy đủ `(serialized_file, path_id)`.
Kết quả:

- **232 controller / 232 machine / 667 state / 377 parameter**
- **932 transition** = 343 AnyState + 125 state + 464 selector
- **376 condition** = mode `If` 375 + `IfNot` 1
- **666 motion leaf**, 231 default state hợp lệ + 1 machine rỗng/default không hợp lệ
- Tất cả các con số đối chiếu với transition artifact: **khớp**.
- So sánh ordered field-by-field: **932/932 transition, 376/376 condition, 667/667 state,
  377/377 parameter, 666/666 motion leaf**, 232/232 machine, **0 mismatch**.

### Ranh giới quan trọng

Nguồn recount vẫn là `l3_animator_programs.json.gz` — artifact đã giải mã trước đó. Đây là independent
**calculation/normalization audit trên source artifact**, không phải independent recovery từ APK bytes.
Artifact nguồn và artifact đích có cùng lineage dữ liệu; `transition_model` khai báo input gốc
animator-programs + motion + common + scheduler. Vì vậy kết quả mạnh nhất hợp lệ là:

> “Bản transition model bảo toàn đúng các trường/đếm được kiểm tra từ artifact decoded; không có
> khác biệt khi tái chuẩn hoá độc lập.”

Không được rút thành “đã xác nhận độc lập trực tiếp từ APK” hoặc “đã xác nhận Unity behavior”. Muốn
mức đó phải có một decoder độc lập từ raw serialized Animator constants / APK hoặc một runtime trace.

## 2. Recipe và provenance

```sh
python3 tools/verify/l3_transition_replication.py --build
python3 tools/verify/l3_transition_replication.py --summary
python3 tools/verify/l3_transition_replication.py --controller 1792
python3 -m unittest tests.test_l3_transition_replication -v
```

Artifact: `datas/l3_transition_replication.json.gz`, **6 856 B**, SHA-256
`83674021682a13c66eeac0e82fec2cfcbc8da288022f89a20b3aabad876ed811`; `--build` chạy hai lần
liên tiếp cho cùng bytes.

| Input | SHA-256 |
|---|---|
| `datas/l3_animator_programs.json.gz` | `114d8f442e07a0733b0a68538ce71c78288cb2c36565bb3ec186f17dd032cd44` |
| `datas/l3_transition_model.json.gz` | `b02b766ceb15ba6b363457a727c08c027caf36568528e44d745d51aea5a990e9` |
| Recount tool `tools/verify/l3_transition_replication.py` | `f7ce79153eba506de7eb3f23199460a7eeb603c4384e8b370523ccdfbe5b60ae` |

SHA của hai input nằm trong artifact; nó cũng ghi rõ lineage của model artifact gốc (motion
`b2036fe60a7bfef7…`, common `6e0f5c589189f49c…`, scheduler `548a5e55449b4e6a…`). Tool replication
không import/call các tool đó; lineage chỉ để công khai quan hệ phụ thuộc của đối tượng được kiểm.

## 3. Đếm lại trực tiếp từ decoded constant arrays

| Đo | Recount | So với model |
|---|---:|---|
| Controller / machine / layer | 232 / 232 / 232 | khớp |
| State | 667 | khớp |
| AnyState transition | 343 | khớp |
| State transition | 125 | khớp |
| Selector transition | 464 | khớp |
| Tổng transition raw | **932** | 932/932 |
| Condition | **376** | 376/376 |
| Parameter | 377 | 377/377 |
| Motion leaf | 666 (đều có clip identity) | 666/666 |
| State không có motion | 1 | khớp |
| Machine có state rỗng | 1 | khớp |
| Default index hợp lệ / không hợp lệ | 231 / 1 | khớp |

Condition lấy từ `wrapper.raw.m_ConditionConstantArray`, không đếm theo summary cache: `If` 375,
`IfNot` 1. Destination lấy từ literal `m_DestinationState` hoặc `m_Destination` theo scope:
**698** trỏ vào state index cục bộ của machine, **234** không phải local index. Distribution raw có
`30000 ×232`, `30001 ×1`, `4294967295 ×1`; các giá trị giữ nguyên, không được diễn giải thành một
state hay cơ chế engine.

Field-presence audit bắt đúng điểm dễ bị che bởi normalizer: mọi **464 selector** đều *thiếu* các
field `m_InterruptionSource`, `m_HasExitTime`, `m_HasFixedDuration`, `m_TransitionDuration`,
`m_TransitionOffset`, `m_CanTransitionToSelf`; các 468 transition AnyState/state có field
`m_InterruptionSource` và serialized value `0`. “Thiếu” được đếm riêng, không đổi thành nguồn
interruption 0. Model normalized chuyển một vài bool selector bị thiếu thành false; differential so
đúng normalized result, còn artifact này giữ presence audit raw để người đọc không nhầm.

Các recount phụ: 107 transition có `m_HasExitTime=true`; 37 fixed-duration; 30 duration khác 0;
467 `m_CanTransitionToSelf=true`, 1 false (selector không serialize field này); 237 state loop;
0 state có `m_Speed != 1`.

## 4. Differential độc lập

Không join theo transition ID (`m0:any:0` lặp giữa controller). Tool so sánh trong thứ tự serialized,
trong controller/machine/scope/state:

- parameter identity/type/name/default (377)
- machine default index/status và selector `m_IsEntry`
- state index, speed, loop, mirror, write-default, cùng motion leaf clip identity/duration/offset/status
- destination literal, source scope/state, toàn bộ raw flags/duration/offset/exit/interruption
- mọi condition: mode, parameter ID/name, threshold, exit time

| Unit | So sánh | Mismatch |
|---|---:|---:|
| Controller identity | 232 | 0 |
| Machine | 232 | 0 |
| State | 667 | 0 |
| Parameter | 377 | 0 |
| Motion leaf | 666 | 0 |
| Transition | 932 | 0 |
| Condition | 376 | 0 |

Artifact ghi `comparison_to_transition_model.all_equal=true`, `mismatch_counts={}` và không có
mismatch example. Hai test mutation cố tình đổi destination/mode trong normalized model đều bị bắt;
đổi display name không làm hỏng join vì identity là cặp qualified.

## 5. Model choices và giới hạn

- Đây là **REPLICATION** (đúng cách khai trên bảng), không phải việc mới tách domain AI-3; source và
  comparison target cùng cây artifact. Không claim trích xuất độc lập trực tiếp từ APK.
- Đếm `destination_local_to_machine` là phép kiểm số học với tập state index cùng machine, không
  kết luận ý nghĩa của destination encoded. Mốc encoded giữ literal.
- Normalizer có thể điền bool false khi raw thiếu. `raw_field_presence_by_scope` cung cấp lớp kiểm
  tra độc lập việc này; không coi giá trị default đã serialize.
- Không chạy scheduler để kiểm thứ tự ưu tiên, exit-time, blend/interruption, trigger consumption;
  những thứ ấy vẫn là model policy `proven:false` theo report 105.
- Không kiểm tra bind tới script SetTrigger/Play, không trace runtime, không render.
- Đối chiếu đạt không thay thế review decoder nguồn. Nếu `l3_animator_programs` có lỗi upstream thì
  phép recount lặp lại lỗi đó; giới hạn này được đánh dấu trong artifact và report.

## 6. Verification / receipt

**13 test mới** (`tests/test_l3_transition_replication.py`): direct recount, partition per controller,
absence-vs-false, exact differential, mutation detection, qualified identity, duplicate transition-ID
regression, SHA pin và byte-identical gzip.

`verify-claims.py --require AB,AO,AP` được đồng bộ cùng vòng này: APKD1 report count **72→74**
(đã gồm report 106 và 107), AI1 datas count **70→71**.

- Branch: `arena/a5a74747-windwings-space-shooter-game-p`
- Claim #16 trước khi làm: PR12 comment `6411344770`; `REPLICATION` khai ở đây và trong artifact.
- Code commit: `3ca37f93f`; tool SHA `f7ce79153eba506de7eb3f23199460a7eeb603c4384e8b370523ccdfbe5b60ae`.
- Artifact: SHA `83674021682a13c66eeac0e82fec2cfcbc8da288022f89a20b3aabad876ed811` (6 856 B).
- Local: **160 PASS** (`python3 -m unittest discover -s tests -q`, 21.104 s), gồm 13 test mới.
- Claims: **209 PASS · 0 FAIL · 2 SKIP · 0 ERROR** (`verify-claims.py --require AB,AO,AP`).
- Raw audit: **180 RAW · 3 DOC · 28 CONST / 211**; opening persistence 65 methods; loadout 41 methods;
  audio rules 33 methods — tất cả lệnh kiểm CI chạy local đều exit 0.
- CI tại commit `3ca37f93f`: `docs-verify` **40291751791 SUCCESS** · `bridge-build`
  **40291751800 SUCCESS** · `runtime-probe` **40291751874 SUCCESS** (draft PR #14).
- `provenance: arena/a5a74747-windwings-space-shooter-game-p`
