# 108 — native Animator evidence cho blend/interpolation — arena/a5a74747

**Mục #15 — handoff có giới hạn / phần interpolation còn BLOCKED.** Tôi claim trước khi làm ở PR12
comment `6411524443`. Kết quả là bằng chứng ranh giới: *không* thêm thuật toán blend của Unity,
không tự mở rộng `l3_transition_scheduler`, và không gọi model thành engine truth.

## Kết luận

1. Trong toàn bộ **308 AnimatorController graph** có trong artifact decoded, **308/308 chỉ có đúng
   1 layer**. Tổng layer mode raw là `0 ×308`, default weight `0.0 ×308`, synchronized-layer index
   `0 ×308`. Do vậy multi-layer blending **không được exercise bởi graph set đã thu hồi**; không có
   case serialized để hiệu chỉnh/test mô hình blend giữa hai layer.
2. Transition model #10 là **232/232 controller một layer**, nối đủ 232/232 với graph raw qua
   `(path_id, name)`. Kết quả này nhất quán với report 99/105, nhưng không khẳng định game không có
   blend được gọi động qua API/Playable.
3. IL2CPP metadata của đúng build có API quan sát layer/state/clip và entry `AnimationCurve.Evaluate`;
   `Keyframe` có time/value/in/out tangents, weighted-mode, in/out weights. Nhưng `dump.cs.gz` chỉ
   chứa declarations + RVA và body rỗng `{ }`: **không có implementation Unity native** để chứng
   minh cách engine evaluate keyframe, property write, hoặc combine property với clip/layer weights.
4. `motion-000` có **301.603 streamed key record**, mỗi vector coefficient dài 4; đây là dữ liệu đã
   export. Tôi không diễn giải hệ số thành công thức engine ở report này — dù tool driven-props hiện
   có policy `streamed_polynomial`, report 104 nói rõ đó là model, không phải engine interpolation.

**Quyết định:** không thêm mô hình engine-style vào code. Phần multi-layer đóng ở mức
`NOT_EXERCISED_IN_RECOVERED_GRAPH_SET`; phần native property interpolation **chưa chứng minh**.

## 1. Đo từ serialized graph / component records

Artifact `datas/l3_animator_blend_native_evidence.json.gz`, **10.890 B**, SHA-256
`8d4a8c667c8263a5a7a92c30058c12e8f12a81124c17deb30cba39243855ec12` (build lặp lại byte-identical).

| Đo | Số |
|---|---:|
| `AnimatorController` graph (raw controller constant arrays) | 308 |
| path IDs unique / duplicate | 308 / 0 |
| Layer tổng / controller có >1 layer / controller 0 layer | 308 / **0** / 0 |
| Blend mode raw literal | `0`: 308 |
| Default weight literal | `0.0`: 308 |
| Synchronized layer index | `0`: 308 |
| `Animator` MonoBehaviour records | 5.792 |
| `Animator` không gắn controller PPtr | 14 |
| Controller PPtr khác 0, phân biệt | 307 |
| Controller assets trong native type export | 308 |
| Controller asset có record nhưng không được Animator PPtr tham chiếu | path ID `1758` (`skeleton_Controller`) |
| `AnimationClip` records trong native type export | 791 |
| Các array ordinary typed curve (rotation/euler/position/scale/float/PPtr) | tổng 0 ở mọi field |
| Motion clip artifact (khác tập mẫu, 665 clip) | 48.823 channel · 29.555 streamed curve · 42 discrete |
| Streamed key record trong export | 301.603, coefficient length 4 |
| Dense `m_CurveCount` / `m_SampleArray` values | 0 / 0; 144.839 frame records được khai báo |

`native-types.jsonl.gz` không mang `serialized_file`; cross-check controller ID/name qua type export
và raw graph là **308/308 path ID khớp, 0 name mismatch**, nhưng đây vẫn là identity check trong
snapshot export, không phải dump gốc độc lập. `animator-controller-graphs` có `path_id` duy nhất
trong chính tập graph, không dùng `path_id` một mình để nối controller với file khác.

Giá trị `m_LayerBlendingMode = 0` chỉ giữ **raw enum integer**; artifact không tự gán tên `Override`
hoặc semantics của enum. Tương tự `m_DefaultWeight=0` là default serialized, không phải live runtime
weight quan sát được.

## 2. API surface tìm thấy trong IL2CPP dump

Nguồn `reverse-engineering/il2cpp/dump.cs.gz` (SHA-256
`e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454`), UnityEngine type declarations
ở `TypeDefIndex 10666` (`Animator`), 10663 (`AnimatorClipInfo`), 10664 (`AnimatorStateInfo`),
10665 (`AnimatorTransitionInfo`), 7663 (`AnimationCurve`), 7662 (`Keyframe`). Một số RVA cụ thể:

| API / field | RVA / layout evidence | Có thể kết luận |
|---|---|---|
| `Animator.get_layerCount()` | `0x27584C0` | API declaration có trong metadata |
| `Animator.GetLayerWeight(int)` | `0x27584FC` | có getter API; không có live call/readback ở đây |
| `GetCurrentAnimatorStateInfo` / `GetNextAnimatorStateInfo` | `0x275859C` / `0x275861C` | current/next state info API được khai báo |
| `GetCurrentAnimatorClipInfo` / `GetNextAnimatorClipInfo` | `0x2758780` / `0x2758880` | current/next clip info API được khai báo |
| `AnimatorClipInfo.weight` | getter `0x2758234` | clip weight có property getter |
| `AnimatorStateInfo.normalizedTime` | getter `0x27582F0` | normalized state-time có getter |
| `AnimationCurve.Evaluate(float)` | `0x275C6D8` | curve evaluation API entry có trong metadata |
| `Keyframe` | offsets: time `0x0`, value `0x4`, in/out tangent `0x8/0xC`, weighted mode `0x10`, in/out weight `0x14/0x18` | keyframe layout được dump khai báo |

Trong toàn bộ `dump.cs.gz`, các tên `SetLayerWeight`, `CrossFade`, `CrossFadeInFixedTime`,
`IsInTransition`, `GetAnimatorTransitionInfo` có **0 occurrence**. Đây chỉ là *coverage của dump
hiện có*; stripping hoặc partial type dump có thể giải thích vắng mặt. `AnimatorTransitionInfo` struct
có metadata fields `m_HasFixedDuration`, `m_Duration`, `m_NormalizedTime`, `m_AnyState`,
`m_TransitionType`, nhưng không tìm thấy accessor transition-info trong đoạn `Animator` dump.

Các method declarations đều có body `{ }` trong `dump.cs.gz`; đây là metadata/stub, **không** phải
machine code của Unity native engine. RVA không đủ để suy ngược algorithm. API có thể cho ta *probe
design*, không tự chứng minh phép tính.

## 3. Vì sao chưa thể chứng minh property interpolation

Để kết luận engine nội suy property, cần một trong hai dạng bằng chứng có thể lặp lại:

**A. Native implementation path** — UnityPlayer/libil2cpp code bytes của Animator/AnimationCurve,
liên kết chính xác với APK 1.3.118 và metadata/build tương ứng; disassemble từ entry đã pin và theo
callee cho tới evaluator / property application / weighting. Workspace hiện có `dump.cs.gz`, native
type trees và một số native body của **game classes**, nhưng không có Unity engine implementation
bytes cho các entry trên. Không được lấy managed method stub làm thân hàm.

**B. Runtime probe trên app thật** — instrument đúng Animator/GO/clip/property, sample nhiều timestamp
ngay trước/trong/sau một transition; cùng một frame ghi `current/next state`, normalized time,
current/next clip IDs + weights, `layerCount/GetLayerWeight`, và giá trị property thực tế từ
Transform/Renderer/TMP. Cần một clip có streamed keys với tangents/coefficients phân biệt linear vs
cubic; so sample engine với hai model candidate và pin thiết bị/build. Hiện artifact runtime chỉ
chứng minh công cụ probe tồn tại/chạy theo contract; **không có sample Animator/property blend đã
chạy trên device** trong workspace này.

**Multi-layer case** còn cần controller thật có >=2 layer hoặc script/Playable thêm layer động; graph
export hiện tại cho 0 case cấu hình như vậy. Trước khi có case native, test model multi-layer chỉ là
synthetic, không thể validate theo APK.

## 4. Recipe và provenance

```sh
python3 tools/verify/l3_animator_blend_evidence.py --build
python3 tools/verify/l3_animator_blend_evidence.py --summary
python3 -m unittest tests.test_l3_animator_blend_evidence -v
```

| Input | SHA-256 |
|---|---|
| `reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz` | `2ab434a1110c1b4ae645f741eee72196735f28b462f49cb3a1fb021f557ed093` |
| `reverse-engineering/raw/typetrees/native-types.jsonl.gz` | `aaf257cd14aea12a1de83b5f71044a671c394dfc8eb2f4e6d9cbb774cefe29a0` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `datas/l3_animator_programs.json.gz` | `114d8f442e07a0733b0a68538ce71c78288cb2c36565bb3ec186f17dd032cd44` |
| `datas/l3_transition_model.json.gz` | `b02b766ceb15ba6b363457a727c08c027caf36568528e44d745d51aea5a990e9` |
| `datas/l3-scene-chains/motion-000.json.gz` | `b2036fe60a7bfef7fc1e8324f4c33ccf4d597ba991c5e7422bda16e2c666fa7c` |
| Tool `tools/verify/l3_animator_blend_evidence.py` | `94120c8e692ae7d8f5e52f483fb000f6c85c3ded519cbe42cf25a557fb0e650b` |

**11 test mới**: graph/layer totals, exact 232 subset join, Animator/controller refs, raw enum literals,
curve API/tangent fields, placeholder-body non-overclaim, unproven status, input/generator SHA và
byte-identical gzip.

## 5. Handoff / review

- Branch `arena/a5a74747-windwings-space-shooter-game-p`.
- Claim #15 trước khi bắt đầu: PR12 `6411524443`.
- **Phần đã đóng:** serialized multilayer coverage = 0/308; target transition set = 0/232 multilayer.
- **Phần còn blocked:** native property interpolation semantics; chưa thêm model vì không có
  implementation bytes hoặc runtime comparison.
- Điểm nhờ spec/chủ dự án review: có đủ điều kiện đánh dấu #15 “multi-layer N/A trong APK snapshot,
  property interpolation OPEN” không, hay cần owner cấp lib/runtime probe để giữ item mở?
- Không sửa tool digger khác; chỉ tool riêng. Không đụng `PROVENANCE.md`, `boss_anim_events.csv`,
  `player_start_stats.json`. Không render/screenshot gate, không merge, không push `main`, không self-ACK.
- Code/tool: commit sẽ ghi trong receipt; tool SHA `94120c8e692ae7d8f5e52f483fb000f6c85c3ded519cbe42cf25a557fb0e650b`.
- Artifact SHA `8d4a8c667c8263a5a7a92c30058c12e8f12a81124c17deb30cba39243855ec12`; rebuild 2× byte-identical.
- Local: **171 PASS** (`python3 -m unittest discover -s tests -q`, 25.656 s), gồm 11 test mới.
- Claims: **209 PASS · 0 FAIL · 2 SKIP · 0 ERROR**; raw audit **180 RAW · 3 DOC · 28 CONST / 211**.
- Persistence/loadout/audio CI-contract commands đều exit 0.
- CI run IDs sẽ được thêm sau khi push commit này.
- `provenance: arena/a5a74747-windwings-space-shooter-game-p`
