# 98 — L3: một chuỗi APK → scene recipe → hình/motion/VFX/audio

**26/10/2026 — TẠM THỜI, không phải nghiệm thu hình ảnh.** Batch này không dừng ở
sprite inventory. Đã trở lại APK để nối object/parent/component/state, vật liệu/font/rig,
clip/binding/event và âm thanh thành **recipe có thể nạp theo root**, giữ source gốc cạnh
bản dẫn xuất. Không vẽ lại từ ảnh điện thoại, không cần chờ capture mới để bóc raw.

## Sản phẩm thực tế và cách dùng

- Raw: `reverse-engineering/raw/l3-chain/index.json` và các object/link shards. Từng
  object có serialized file + pathID + native classID + SHA256; link ghi cả null/unresolved.
- `tools/verify/l3_chain_graph.py`: hierarchy bằng PPtr, header authority, TRS trong root frame.
- `tools/verify/l3_scene_chains.py`: nối thành `datas/l3_scene_chains.json.gz` và
  `datas/l3-scene-chains/*.json.gz`. Root chứa node/callback/sound/animator indices và
  closure tài nguyên **typed**, không lần theo GO tuỳ ý được script tham chiếu.
- `tools/verify/l3_recipe.py`: xuất một recipe, tuỳ chọn materialize raw object snapshots.
  Script/renderer không có hình vẫn được giữ trong logical membership; không còn làm
  Button_Sound/UnityEvent biến mất chỉ vì GO ấy không có renderer.

```sh
python3 -m tools.verify.l3_recipe --label Board_Pause
python3 -m tools.verify.l3_recipe --root 10 --include-raw --out /home/user/pause-recipe.json.gz
python3 -m tools.verify.l3_recipe --root 402 --include-raw --out /home/user/effect-90045.json.gz
python3 -m tools.verify.l3_recipe --root 769 --include-raw --out /home/user/homeplayer-10013.json.gz
```

Root numbers thuộc snapshot hiện tại, **không phải game enum**; lookup label rồi xác nhận
qualified identity. `--include-raw` giữ generated tree và binary MonoBehaviour header riêng:
**header thắng** ở m_GameObject/m_Enabled/m_Script, không âm thầm sửa raw cũ.

Recipe có: GO layer/name/activity, Transform/RectTransform nguyên bản (kể cả root local TRS),
root-frame matrix/parent, tất cả component identities + raw locators, visual properties,
asset closure + media paths/SHA, animator→clip→binding targets, numeric animation storage,
sprite key→PPtr table→asset identity, callbacks/arguments/method candidates và sound bridges.
Raw locators là `{path,row}` zero-based trong JSONL đã hash-pin; không phải object index toàn cục.
Shader/mesh opaque payload không được biến thành dữ liệu giả.

Media paths là đường dẫn **trong external asset pack**, không phải URL localhost hoặc bản gốc
được commit vào Git. Font/SkeletonDataAsset/atlas→TextAsset/material/texture đi bằng qualified
references; `--include-raw` cho nguyên serialized metadata của chúng. Payload Spine/font/audio/
pixel vẫn lấy pack/artifact đã có; không bake lại từ screenshot. Closure có thể gồm toàn atlas,
font fallbacks, controller clips, nên asset count **không** là số tài nguyên thực sự được vẽ.

## Ba chuỗi cụ thể, không chỉ đếm

### A. Board_Pause: UI → hình/font → appear/hide → click sound

Root `data.unity3d/resources.assets:212696` (root10) xuất được 235 logical nodes,
404 assets trong closure, 4 Animator/5 clips, 16 binding instances, 15 callbacks và 26
serialized sound fields. Các node không render vẫn ở trong recipe và có raw component.

Ví dụ sound owner `resources.assets:594174`, class **Button_Sound**:
` soundClickDown = 1 → AllClipName.Sfx_ClickDown → SoundClip:580679 → AudioClip:1695 `.
Registry nối được WAV external + SHA; `soundClick = 2` đi riêng qua Sfx_ClickUp.
Native rule nối đúng **class + field** tới `Button_Sound.OnDown@0x141fdc4` và
`OnClick@0x141fddc`, không lấy cùng tên field của class khác làm bằng chứng. `None0`
không có registry là skip có chủ đích theo native rule, không phải thất lạc clip.

Clips có `Appear:1572` (0.5s), `Hide:1573` (~0.33333334s), `idle:1495`, `stop:1496`,
`idle1:1557`; mọi ID ở cùng serialized file trên. Binding bám subtree Animator thật,
không tìm target cùng tên ở prefab khác. Không suy rằng tất cả clips đang đồng thời chạy.

### B. Effect90045: prefab → emitter/renderer/material → motion/event/sound field

Root402 `poolingobjects/effects/effect/90045`: 48 nodes, 68 closure assets, 4 clips,
310 binding instances, 2 callbacks, 1 serialized sound field. ParticleSystem giữ đủ serialized
module parameters trong raw snapshot; ParticleSystemRenderer/LineRenderer/TrailRenderer
có renderer parameters, không chỉ tên effect. Recipe kéo được cả emitter và logical owner.
Đây là dữ liệu xây effect; chưa tự mô phỏng random seed, particle lifecycle hoặc GPU shading.

### C. Player_Attack_13: prefab → native firing sound bridge → đúng audio asset

Root769 `prefabs/homeplayers/player_10013`, 33 nodes, có component Player_Attack_13.
Nối thêm contract đã bóc `datas/wing_emission_flow.json`: attack13/22/23/24 dùng sound enum5
**Sfx_Shot1 → AudioClip resources.assets:1752**, với native sound/dispatch evidence được
hash-pin. Giữ điều kiện demo suppress và khác biệt gate normal/super; không gọi sound cho
mọi frame/packet theo suy đoán. Serialized enum sound và native-only bridge là hai loại evidence
riêng. Đây không phải lý do quay lại backlog wing; chỉ nối dependency nghe được của appearance.

## Camera/composition không bị bỏ khỏi chuỗi

Bank scene context giữ 5 Camera và 1 Canvas với identity/GO/properties; không gắn tất cả
camera vào mọi prefab. Camera native size writers nối **đúng qualified Camera identity**
với `datas/camera_scaler_contract.json`, gồm write order và enabled của scaler:
`max(float32(float32(float32(height)/float32(width))*factor), minimum)`,
factor~5.400000095/minimum~9.600000381. Cả contract hash và dump hash được kiểm.
Không nhầm CameraScaler native của game với class CanvasScaler của Unity UI.

Matrix dẫn xuất bỏ root local TRS ra ngoài để ở root frame; root TRS nguyên bản được giữ
trong node. Nó không tự giải RectTransform driven layout, viewport, scene instantiation,
camera culling hoặc world/screen projection. Serialized active/enabled không là runtime visibility.

## Độ phủ của snapshot đã nối

| Mục | Kết quả |
|---|---:|
| Raw objects / resolved edges |128724 /345090|
| Null / unresolved edges |166639 /52|
| Read failures / header-only MonoBehaviours |0 /5|
| Root views |805:12 core UI views +793 resource GO views|
| Logical / visual node observations |37766 /25536|
| Typed assets / Animators / clips |3504 /1587 /665|
| Animation binding instances |52400|
| Unique / unresolved / ambiguous targets |51990 /393 /17|
| Callbacks |2139:904 persistent calls +1235 animation-event instances|
| Scalar AllClipName fields / SoundClip registry names |2037 /92|
| Hierarchy/transform errors / unknown matrices |0 /0|

805 **views/aliases**, không khẳng định 805 prefab độc lập hay tất cả game UI. Core12 views
là Board_Maps/Players/Drones/Reborn/Endgame/Stage,3 Reborn_IAP,Home,Pause,GP_Tutorials.
Toàn797 legacy indexed layouts vẫn ở report96/97, không lấy batch12 này nhận công full797.
Header-only5 giữ chi tiết object/class/parser exception ở raw index, gồm GunEventCatcher và
Player_Attack_2; chưa bịa downstream fields cho chúng.

665/665 clip có streamed/dense/constant numeric storage đọc được, channel coverage khớp
chính xác genericBindings, tổng301603 streamed keys. Đã sửa31 sprite clips: số kênh phải
cộng **discreteCurveCount**, không chỉ curveCount. Sprite keys giữ mapping-index rời rạc,
**không nội suy/blend sprite pointers**. Coefficients, dense sample grid, constants, events,
ordinary curves, mapping raw và resolved identities đều còn. Không đồng nghĩa đã chạy
Unity Animator state machine/layer blending/override selection.

Native classID thay bảng class-name đoán tay: GameObject active bindings target GO; Transform
binding nhận Transform/RectTransform; script binding yêu cầu đúng scoped MonoScript. Còn393
unresolved:376 không có path trong subtree,13 không khớp script ở path có thật,4 yêu cầu
BoxCollider2D ở path không có component ấy. Giữ17 ambiguous, không chọn candidate đầu tiên.
CRC32 field candidates chỉ lấy scalar field thật trên target; vẫn ghi là candidate, không giả là
mọi packed engine attribute đã giải thành field API. Không gọi unresolved static match là
chứng minh engine không thể resolve bằng inherited/runtime state.

52 unresolved graph links đều tới Unity default-resource meshes, không phải 52 packaged game
assets biến mất. 18074 generated MonoBehaviour script-header pointers từng sai đã được kiểm
đối chiếu binary header, sửa **edge traversal**, giữ disagreement gốc; không đổ lỗi APK thiếu.
Audio mixers chỉ có identity/hash ở raw projection hiện tại: recipe giữ chúng như vậy, không
nhận đã tái dựng mixer routing/effects. 46 animation-event instances chưa có receiver method
candidate khai báo ngay trên cùng GO; không suy thành chắc chắn callback không chạy/inherited
method không tồn tại. Persistent calls giữ m_CallState/mode/arguments và target; không invoke.

## Kiểm chứng và bàn giao

18 tests mới: fixture header/file scope/flags/discrete/dense shape; regenerate mọi row/header;
hash/size chunks; đầy đủ logical owners; exact native classIDs; ambiguity/null giữ nguyên;
clip coverage/sprite mapping; typed asset closure/raw locators; Button_Sound/native sound bridge;
camera bank; export Pause recipe có cả raw nonvisual components. Full suite **921 PASS**,
124.500s local. CI receipt ghi riêng sau khi chạy, không lấy local PASS làm remote PASS.

Recovery source run40228467063 SUCCESS, raw bot commitcb1919d77. Raw và derived đều giữ,
không commit APK/original media/file>5MB. Peer cần review độc lập recipe/source interpretation,
đặc biệt runtime state, sprite keys, callback targets và camera ownership; không tự ACK.

**Đã có dữ liệu xây scene theo chuỗi, chưa có rendered acceptance.** Phần tiếp phải dùng recipe
này để dựng/kiểm composition/playback bằng đúng assets, không mở thêm vòng inventory đếm file,
không báo clip decode/tests green là hình game đã giống. Các kết luận vẫn tạm thời.
