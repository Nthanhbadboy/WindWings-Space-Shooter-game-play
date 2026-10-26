# 105 — model runtime animation: particle sim, transition scheduler, driven rect/alpha

**Tạm thời. Source APK là authority; đây là *model output*, không phải engine readback và
không phải render. Không có render/screenshot acceptance ở đây.**

Branch `arena/a5a74747-windwings-space-shooter-game-p`. Ba deliverable model-level, không đụng
texture decode, shader execution, geometry generator của digger khác; không sửa `tools/` của
peer — mọi thứ nằm trong ba tool riêng + `l3_model_common.py`.

## Ranh giới

| Làm | Không làm |
|---|---|
| Chạy được headless, phát state theo `t` | Render, screenshot gate, vẽ lại |
| Lấy số từ artifact đã decode (count đo lại) | Nhận số ước lượng / số của peer làm nguồn |
| Giữ nguyên encoded destination (30000/30001/UINT_MAX) | Đoán index state cho selector |
| Ghi rõ policy nào là model choice (`proven:false`) | Gọi policy của mình là "Unity scheduling" |
| Báo field không giải được | Đoán tên field từ CRC gần đúng |

## Nguồn và SHA pin

Mọi input đều được băm trong `artifact['inputs']` (18 shard `animation_bindings-*`, 13 shard
`nodes-*`, 1 shard `motion-*` — lần này pin **toàn bộ** shard đọc, không chỉ `-000`).

| Nguồn | sha256 (16) |
|---|---|
| `datas/l3-visual-surface/particles-000.json.gz` | `d9e868555b113cea` |
| `datas/l3-visual-surface/particles-001.json.gz` | `edda26d726960155` |
| `datas/l3-visual-surface/particles-002.json.gz` | `b4740dfc5bfb0c81` |
| `datas/particle_systems.csv.gz` | `6d8e2bcd6d372277` |
| `datas/l3_animator_programs.json.gz` | `114d8f442e07a073` |
| `datas/l3-scene-chains/motion-000.json.gz` | `b2036fe60a7bfef7` |
| `datas/l3-scene-chains/animation_bindings-000.json.gz` | `79982d83626c9fab` |
| `datas/l3-scene-chains/nodes-000.json.gz` | `f4362be94bcdba4a` |
| `datas/l3_frame_cases.json.gz` | `daf9f0d335863635` |
| `reverse-engineering/raw/typetrees/native-types.jsonl.gz` | `aaf257cd14aea12a` |

Artifact (full sha256):

- `datas/l3_particle_model.json.gz` `9216e6b618424add98fc251fbd77012f9b054d81dab5f65485a9617ea9a06fd5` (183 457 B)
- `datas/l3_transition_model.json.gz` `b02b766ceb15ba6b363457a727c08c027caf36568528e44d745d51aea5a990e9` (43 783 B)
- `datas/l3_driven_props.json.gz` `ed3f51739a89df3a0b2e13e36e39d0c4210e00551dc9920df2581db7f68b2310` (22 050 B)

Tool: `l3_model_common` `6e0f5c589189f49c`, `l3_particle_model` `ff4324f9c0c3f9c6`,
`l3_transition_scheduler` `548a5e55449b4e6a`, `l3_driven_props` `5e5e0b53c3e90b76`.
Cả ba artifact rebuild 2 lần liên tiếp → byte-identical (test `RegenerationTests`).

## 1. Particle simulation model — 954 hệ

Scope lấy từ visual-surface: **883** hệ trong `data.unity3d/resources.assets` + **71** trong
`data.unity3d/level2`. Ghép native constants: **4 845** record trong `native-types.jsonl.gz`,
**954/954** hệ ghép 1:1. Ghép prefab root: **953/954** (duy nhất lẻ:
`resources.assets:502274`), 31 prefab root phân biệt.

| Module bật | Số hệ | Module bật | Số hệ |
|---|---:|---|---:|
| Emission | 954 | Rotation | 94 |
| Initial | 954 | Velocity | 57 |
| Color | 801 | ColorBySpeed | 45 |
| Size | 707 | Collision | 18 |
| Shape | 504 | Noise | 16 |
| UV | 96 | Trail | 16 |
| RotationBySpeed | 6 | Sub | 5 |
| Force | 3 | Trigger | 0 |

| Thuộc tính | Đo được |
|---|---|
| rateOverTime > 0 / = 0 | 410 / 544 |
| burst (m_BurstCount > 0) | 402 |
| looping / prewarm / playOnAwake | 599 / 198 / 941 |
| randomSeed tường minh | **0** (mọi hệ dùng auto seed — model tự đặt seed) |
| startSpeed = 0 | 674 |
| gravityModifier ≠ 0 | 141 |
| maxNumParticles ≤ 10 | 159 (trong đó 736 hệ = 1000) |
| lengthInSec phổ biến | 5.0×446, 2.0×219, 1.0×148, 3.0×7, 6.0×40 |

### Model chạy được

`ParticleSim(system, seed, gravity, spread, overrides, axis)` — `sample(t, limit)` trả về state:

- `emitter_time = t * simulationSpeed`; `cycle_time = emitter_time mod lengthInSec` (looping) hoặc
  `min(emitter_time, lengthInSec)`.
- Sinh hạt ở `k / rate`, `k = 1..`; mỗi hạt có lifetime/speed/size/rotation lấy từ hằng số curve
  đã decode; `spread='range'` rút đều trong cặp `(scalar, minScalar)` bằng splitmix64
  `(seed, stream, index)` — **PRNG của model, không phải engine RNG**.
- `position = v0*age + 0.5*g*age²`, `v0 = speed * direction`; `direction` là nón nửa góc
  `ShapeModule.angle` quanh trục khai báo (`+Y` emitter-local). `ShapeModule.type` **không** được
  diễn giải (enum chưa decode) — nằm trong `decode_limits`.
- `g` **không** lấy mặc định engine: caller truyền (`gravity=`), mặc định `(0,0,0)`;
  `gravityModifier` chỉ được báo, không tự nhân với −9.81.
- `alpha = 1.0` + cờ `color_gradient_absent`: gradient ColorModule/ColorBySpeed không có trong
  artifact → **không** claim fade.
- Vượt `maxNumParticles` → drop hạt cũ nhất (policy khai báo, không phải ring-buffer Unity).

Cờ decode (`counts.decode_flag_counts`): `curve_keys_absent` 954, `gradient_absent` 801,
`bursts_not_exported` 402, `local_vs_world_flags_absent` 57, `collision_planes_absent` 18,
`noise_field_absent` 16, `prewarm_declared_not_simulated` 198, `sub_emitters_not_modelled` 5.

### State mẫu (đo từ artifact, không vẽ)

`level2:4784` (rate 3.0, startSpeed 60, lifetime 1.0, cap 10, gravity caller `(0,−9.81,0)`, seed 1234):

| t | alive | hạt đầu: age | position |
|---:|---:|---:|---|
| 0.5 | 1 | 0.1667 | (0.641888, 9.978007, 0.165395) |
| 1.0 | 3 | 0.6667 | (2.567552, 39.912028, 0.661581) |
| 2.0 | 3 | 0.6667 | (−5.350918, 39.372979, −4.597409) |
| 3.0 | 3 | 0.6667 | (−8.777395, 38.609022, 5.683378) |

`level2:4785` (rate 10, life 5, cap 1000): alive 5 / 10 / 20 / 50 tại t = 0.5 / 1 / 2 / 5; t = 6 vẫn
50 (cap chưa chạm). `level2:4783` (cap 1, rate 1, life 2): t = 2.0 và 5.0 alive = 1, hạt cũ bị
drop — cap policy đúng. Cùng seed → state trùng bit; đổi seed chỉ đổi `direction/spread`, không đổi
`alive`/`birth_time`.

## 2. Transition scheduler + layer blend — 232 controller

| Đo | Số |
|---|---:|
| controller / machine / layer | 232 / 232 / 232 (mỗi controller **1 layer**) |
| state | 667 (`states_without_motion` 1) — `empty_machines` 1 |
| motion leaf | 666, resolve được clip length **666/666** |
| transition | 468 = 343 AnyState + 125 state; **464 selector** |
| condition | 376 (`If` 375, `IfNot` 1; threshold 0.0 cho cả 376) |
| `m_HasExitTime` | False 361 / True 107 |
| `m_HasFixedDuration` | False 431 / True 37 |
| duration ≠ 0 | 30 (0.25×19, 0.5×5, 1.0×4, 0.2×2); 0×438 |
| `m_Loop` | False 430 / True 237 |
| `m_Speed` | 1.0 × 667 (không state nào ≠ 1) |
| parameter | 377 (Bool 16, Trigger 361) |

Selector/exit giữ nguyên encoded: `30000` × 232, `30001` × 1, `4294967295` × 1 —
`encoded_destinations_kept`, scheduler **từ chối** đi tiếp và ghi lý do
`encoded_destination_not_local`, không suy ra index.

### Interruption source — sửa cách đọc

Vòng trước artifact in `{"0":468,"null":464}`, đọc lên thành "464 transition không rõ nguồn". Sai:
464 transition đó **không có** field `m_InterruptionSource` serialized (toàn bộ là selector). Đã
tách: `interruption_sources = {"0": 468}` (đo được), `interruption_source_absent = 464`,
`interruption_source_absent_scope = {"selector": 464}`; test ràng buộc
`selector_transitions == interruption_source_absent`. Vì vậy SHA transition model đổi sang
`b02b766c…` và driven-props (pin SHA transition model) đổi sang `ed3f5173…`.

### Policy — cái nào là model choice

| Rule | proven | Ghi chú |
|---|---|---|
| Encoded destination không bao giờ được đi | **true** | literal từ dữ liệu |
| Self-transition bỏ khi `m_CanTransitionToSelf = false` | **true** | cờ serialized |
| Exit time: eligible khi `state_time ≥ exit_time` (fixed → giây, else × length) | false | normalization là model |
| Duration: `transition_duration` (fixed) hoặc `× source length` | false | model |
| Blend: `w_dest = clamp(elapsed/blend_seconds,0,1)`, `w_src = 1−w` | false | linear, không phải Unity curve |
| Thứ tự: AnyState (serialized order) trước, rồi state list, first-eligible-wins | false | APK không lưu thứ tự engine |
| Trigger bị consume khi transition được đi | false | hành vi model hoá, không chứng minh |
| Interruption: nguồn `None` không bị thay khi đang transition | false | enum 0–4 có trong dữ liệu, áp dụng là model |
| `engine_equivalence` | false | tuyên bố rõ trong artifact |

### Case chạy

| Case | Kết quả đo |
|---|---|
| `BB-36002` (2 400 step @1/60) | 0→1 @t=1.0 (blend 0), 1→2 @19.0 (1.8000000268 s), 2→1 @20.8167 (0.2 s), 1→2 @38.8167; cuối ở state 1 `Idle`, w = {1: 0.3425926024, 2: 0.6574073976}; 2 396 lần bị chặn (`exit_time_not_reached`) |
| `BLT_88011` (trigger `Attack` @0.05) | 0→1 @0.0667 (consume trigger), 1→2 @1.0667 (blend 0.5); cuối state 2 `Idle`; 267 chặn (`condition_false` + `exit_time_not_reached`) |
| `Box_Gift (0)` (trigger Flick/Change/Pop) | 0→1 @0.1167, 1→2 @0.6167, 2→0 @1.0167 — cả ba instant (duration 0) |
| `Warning_Boss_Appear` (1857) | 0→1 @0.5, 1→2 @2.5; transition `m0:state2:0` destination `30001` bị chặn 210 frame với lý do `encoded_destination_not_local` |

## 3. Driven RectTransform / renderer-alpha — 67 route trên 52 400 binding

Route table dựng bằng CRC32 của tên field so với `attribute` trong binding, **không** dùng bảng
của peer: **52/52** route có tên field khớp CRC (`crc32_field_name_matches_attribute`,
`equal: true`). Ví dụ `m_SizeDelta.x` 1967290853, `m_AnchoredPosition.y` 538195251,
`m_Color.a` 304273561, `m_IsActive` 2086281974.

| kind | route | binding | kind | route | binding |
|---|---:|---:|---|---:|---:|
| rect | 10 | 755 | unresolved | 12 | 16 671 |
| alpha | 8 | 3 575 | local_position | 4+3 | 12 888 + 225 |
| active | 1 | 5 230 | local_scale | 1 | 5 547 |
| text | 7 | 525 | euler | 1 | 5 586 |
| particle_module | 8 | 147 | renderer_size | 2 | 46 |
| renderer_state | 4 | 1 003 | line_trail | 3 | 110 |
| scalar_field | 6 | 92 | | | |

Class ID: `4` Transform 24 021, `212` SpriteRenderer 20 513, `1` GameObject 5 230,
`114` MonoBehaviour 1 010, `224` RectTransform 980, `61` 191, `198` 147, `58` 131, `120` 109,
`60` 67, `96` 1.

**Không có binding nào cho CanvasRenderer (classID 222) hay CanvasGroup (225)** — 0 và 0. Nghĩa là
trong 665 clip, UI alpha được drive qua `SpriteRenderer.m_Color.a` / TMP `m_fontColor.*`, không qua
CanvasRenderer/CanvasGroup. Đây là phát hiện âm, không phải "thiếu tool".

Layout channel: **665/665** clip khớp `channel_count`; **634/665** `layout_exact`; 31 clip còn lại
đều có curve rời rạc (`m_CurveCount` 0 cho dense ở mọi clip, streamed luôn là prefix).

### Case (mỗi case lấy baseline serialized từ node/component thật của đúng Animator instance)

| Case | clip | binding | target snapshot | layout | ghi chú |
|---|---|---:|---|---|---|
| `box_gift_appear` | 986 `Appear` | 26 (25 có field) | 5/5 | 34 channel, exact | mỗi sample bỏ đúng 1 write (`binding 22`, `field_unresolved`) |
| `box_gift_flick` | 986 `Flick` | 26 | 5/5 | exact | cùng instance |
| `extra_life_apear` | — `apear` | 9 | 9/9 | 13 ch, exact | 4 GameObject `m_IsActive` |
| `efx_90016_active` | — `Active` | 5 | 5/5 | exact | rect + TMP color |

Giá trị cụ thể (`box_gift_appear`, baseline → driven):

| Target | Field | Baseline | Driven (t=0) |
|---|---|---:|---:|
| `576148` RectTransform `…/Box_Gift (7)/Text_Number` | `m_SizeDelta.x` | 1.0 | 1.850000023841858 |
| " | `m_SizeDelta.y` | 0.5 | 1.0 |
| " | `m_AnchoredPosition.x` | 0.4860000014305115 | 0.0 |
| " | `m_AnchoredPosition.y` | −0.7680000066757202 | −0.7099999785423279 |
| `277770` Transform (`Light`/root) | `m_LocalScale.x/y` | 1.0 | 0.5 (→1.2000000565 @t=0.1667) |
| `532836` SpriteRenderer | `m_Color.a` | 0.0 | 1.0 (→0.5000000447 @t=0.25) |
| `652439` TMP `Text_Number` | `m_fontSize` | *not inlined* | 3.8499999046325684 |

`652439` (`m_textAlignment`, attr 565532780) là curve `isIntCurve`: hằng số serialized
`5.74532370373175e-42` đọc như float; reinterpret bit pattern bằng
`struct.unpack('<i', struct.pack('<f', v))` → **4100**. Model giữ cả `value` (float) và
`value_int` (4100) và đánh dấu `baseline_status: component_snapshot_not_inlined` vì component
chỉ có trong snapshot rời (`raw_snapshot_only`), không inline trong node index.

`extra_life_apear`: 4 target `m_IsActive` = 1.0 (bool model `True`), RectTransform `571782`
`m_LocalScale.x` 0.0 → 0.5184000432491302 @t=0.0833.

### Nối scheduler ↔ driven props (`scheduled_timeline_case`)

`Box_Gift (0)` chạy 13 sample, transition instant tại 0.0667 / 0.4667 / 0.8167, mỗi sample mang
`states[]` với `weight` = scheduler trả về và full channel writes của clip đang chạy; tổng weight
= 1.0 mọi sample. Đây là **một modeled state**, không phải frame Unity: blend weight áp lên channel
value theo tuyến tính, không nội suy Transform kiểu engine.

## 4. Recipe

```sh
python3 -m tools.verify.l3_particle_model --build
python3 -m tools.verify.l3_particle_model --system 4784 --times 0,0.5,1,2,3 --seed 1234 --gravity 0,-9.81,0
python3 -m tools.verify.l3_transition_scheduler --build
python3 -m tools.verify.l3_transition_scheduler --controller 1910 --duration 40
python3 -m tools.verify.l3_transition_scheduler --controller 1940 --script '[{"t":0.05,"trigger":["Attack"]}]'
python3 -m tools.verify.l3_driven_props --build
python3 -m tools.verify.l3_driven_props --case box_gift_appear --t 0.25
python3 -m unittest discover -s tests -q
```

**77 test mới** (`test_l3_particle_model` 22, `test_l3_transition_scheduler` 28,
`test_l3_driven_props` 27); **full local: 122 PASS (16.679 s)**, baseline 45 test vẫn xanh.
Test không pin vào SHA artifact mà **rebuild rồi so byte** — sửa tool mà không rebuild là đỏ.

## 5. Chưa hoàn tất, điểm cần review

1. **Curve keys + gradient + burst table không có trong artifact** → particle chỉ là hằng số +
   rate; over-lifetime size/color/alpha, burst, noise, collision, trail, UV, sub-emitter,
   prewarm, rateOverDistance đều không mô phỏng. Muốn có phải bóc thêm từ APK (`MinMaxCurve`
   keyframes, gradients) — không phải việc của vòng này.
2. **Engine scheduling chưa được chứng minh**: thứ tự đánh giá, normalization exit-time/duration,
   trigger consumption, interruption enum đều `proven:false`. Ai có bằng chứng native (il2cpp
   `Animator`/`StateMachine`) thì thay policy, đừng đọc bảng này như engine truth.
3. **Chỉ 1 layer/controller** trong artifact → nhánh multi-layer weighting chưa được chạy; nếu
   artifact layer mới xuất hiện thì phải mở lại.
4. **Blend là tuyến tính trên weight**, không nội suy property; `m_Speed` toàn 1.0 nên speed
   parameter/`speedMultiplier` chưa exercise. Blend tree `m_Duration` giữ riêng, không dùng thay
   clip length.
5. **16 671 binding chưa có field** (12 route, lớn nhất `212:2302021180` 4 574). Không đoán; cần
   typetree thật của classID 212/114 (script-specific) mới đóng được.
6. **31 clip `layout_exact=false`** — đều do curve rời rạc (int/PPtr) nằm ngoài streamed+constant;
   model bỏ qua thay vì gán sai channel.
7. **Không có CanvasRenderer/CanvasGroup binding** trong artifact hiện có; nếu ai tìm ra clip
   drive classID 222/225 thì báo, vì kết luận "UI fade qua sprite/TMP color" sẽ phải xét lại.
8. `m_textAlignment` cần đọc int32; nếu downstream đọc float sẽ ra 5.7e-42 — đã có hàm `as_int32`
   trong tool để dùng lại.
9. Đã **không** sửa `datas/PROVENANCE.md`, `boss_anim_events.csv`, `player_start_stats.json`, và
   không sửa tool của peer.

## Receipt105

- Branch: `arena/a5a74747-windwings-space-shooter-game-p`
- Code: `d446d47d5` (tools + 3 artifact + 3 test file), report ở commit riêng sau đó
- Local: **122 PASS** (`python3 -m unittest discover -s tests -q`, 16.679 s), dominant 77 test mới
- Artifact SHA: particle `9216e6b6…a06fd5`, transition `b02b766c…a5a990e9`, driven `ed3f5173…7f68b2310`
- CI run: xem comment PR12 (workflow `docs-verify`, trigger `workflow_dispatch` trên branch này)
- `provenance: arena/a5a74747-windwings-space-shooter-game-p`
- Không self-ACK, không merge, không push `main`.
