# 102 — Layout owner → geometry/font → material/shader → animation → recipe

**Kết luận tạm thời, nguồn APK đã pin, không phải Unity render acceptance.**

## Không dừng ở reference

Batch101 có ObjectScaler6686 nhưng Animator4647 mới là metadata trên GO110 Alert.
Batch102 thu hồi đầy đủ body/asset closure dưới **585 layout component owners**. Recovery
40236718364 rồi40236919629 SUCCESS; bản sau bổ sung shader analysis và redaction cho
opaque byte buffer biểu diễn bằng integer-list. Raw riêng `raw/l3-visual-surface`, không
thay đổi nguồn101 hay nguồn95/100 để làm lệch provenance cũ.

- **56714 objects /16061 GameObjects**, descendant hierarchy + referenced asset closure.
  Không mở arbitrary script GameObject references; đây không phải toàn bộ APK hay mọi797
  resource recipe. Recipe có coverage và danh sách GO ngoài scope, không coi empty là complete.
- **11380 renderer records**,153 materials,17 shaders,1389 sprites +2 meshes có decoded
  local vertices/normals/UV/indices/triangles. Cả1391 geometry decodes thành công.
  Raw serialized buffers giữ SHA/length; derived geometry không dùng OBJ exporter đảo dấu X.
- **7 TMP font assets /7 atlas textures /2354 character entries**, face/glyph metrics,
  glyph rect, atlas index, ordered fallback links, material và exact exported PNG identities.
  So bảng glyph/character với nguồn font-language cũ: trùng hoàn toàn.1737 TextMeshPro instances
  nối font/material và serialized style/text, không đoán live localized string.
- **954 ParticleSystem +954 ParticleSystemRenderer**: full numeric module trees được giữ
  trong raw, module descriptors và renderer/material/reference joins vào artifact. Không giả
  làm đã phát sinh vertices/simulate random seeds hay emitter lifecycle.
- **1057 Animators /91 controllers /348 clips**; cả348 decoded numeric stream/dense/constant,
  binding channel widths khớp.79907 instance bindings:74916 unique targets,4983 unresolved,
  8 ambiguous. Đây là trạng thái resolver hiện tại, không kết luận thiếu asset/impossible runtime.

## Chuỗi cụ thể Alert, đã vá gap101

`level2:GO110 Alert` có Transform2232, SpriteRenderer5105, Animator4647, ObjectScaler6686.
Scaler vẫn dùng native contract101; renderer vẫn sprite `sharedassets2.assets:114`, material
`globalgamemanagers.assets:2` (Sprites-Default), shader
`Resources/unity_builtin_extra:10753` có **parsed name `Sprites/Default`**. Shader object name
rỗng nên không dùng tên rỗng để kết luận shader mất. Renderer serialized Color=(1,1,1,0).

Animator4647 → controller `sharedassets2.assets:78 Alert`:

| State | Clip | Local stop | Alpha model |
|---|---|---:|---|
| none (default index0) |44 none|0|constant0|
| alert |42 alert|.125|0→.7843137383460999|
| fade |43 fade|.25|.7843137383460999→0|

Clip bindings path0/type212/property CRC match **same renderer5105.m_Color.a**, không ghép
bằng tên gần giống. Midpoints: alert@.0625=.3921568840742111,
fade@.125=.39215685427188873. Đây là explicit coefficient probes với Python arithmetic model,
không phải engine float precision/transition trace.

Controller có Trigger-type9 parameters Alert/Fade, default false; AnyState→alert/fade giữ
conditions nguồn. alert→fade và fade→none có exitTime1/duration0. Không tự chọn state, phát
trigger, nối hai clip thành observed engine timeline hay khẳng định thời điểm warning xuất hiện.

Material saved _Color=(1,1,1,1), _MainTex null và _AlphaTex null được giữ nguyên, không thay null
bằng một texture phỏng đoán. Sprite source texture/atlas references và exact cropped media có
trong recipe. Shader pass rtBlend0 lưu numeric src1/dst10/op0/color-mask15 cùng alpha state;
đây là serialized states, không có auto queue/platform/variant/dynamic property-block resolution.

## Shader và font có dữ liệu sử dụng được đến đâu

Cả17 shaders có parsed properties/subshaders/pass render states, platform metadata, buffer SHA,
và **UnityPy textual decompiler analysis thành công**. Raw giữ text +SHA; bản phân tích tự ghi
“not a valid shader file”, không phải replacement shader đã compile. Có Sprites/Default, mask,
Spine blend modes, custom grayscale/bloom/progress, TMP distance-field và particle shaders.
Không tuyên bố shader body không lấy được; cũng không coi decompiler text là GPU execution.

`glyph_probe` đi theo exact codepoint/ordered serialized asset fallbacks. Ví dụ **“Tiếp tục”**
đủ8 character matches, kể cảế/ụ, mỗi match có source glyph/face/atlas PNG. Zero-area space
vẫn có advance, không sinh rectangle giả. Không parse rich text, đổi case/style/weight, shape,
line-wrap, chọn global fallback hay dynamic atlas. “Absent in selected static chain” không có
nghĩa game không thể hiển thị bằng đường runtime khác.

Geometry là serialized local source: **chưa áp live atlas overrides, sliced/tiled sprite generation,
skinning, TMP glyph mesh generation, shader displacement hay particle/line/trail generation**.
Raw SpriteAtlas render maps, sprite pivot/border/PPU, particle modules và font feature tables
vẫn giữ để bước dựng tiếp không mất dữ liệu. Không gán camera/safe-area hiện tại cho prefab.

## Artifact, recipe và kiểm chứng

- `datas/l3_visual_surface.json.gz` là header;249 hashed section chunks tại
  `datas/l3-visual-surface/`, mỗi chunk <5MB (lớn nhất2350459B). Không nhét original media,
  font programs, shader compressed binary, APK hay lib vào Git.
- `tools/verify/l3_visual_surface.py`: regeneration, raw/chunk SHA assertions, static glyph
  probe, source-attached clip probe, scoped recipe join và selected raw materialization.
- Recipe10 Pause nối **8 renderers /3 texts /5 sprite geometry records**, scoped materials,
  shaders và global7-font candidate bank. Không tự chọn font cho null font pointer. Với
  `--include-raw`, `selected_surface_raw_objects` giữ selected surface records riêng; không
  nói đó là full transitive raw closure. Raw locators và source-qualified refs vẫn còn.
- `raw/l3-surface-verification/`: actual-identity Alert/glyph probes và local/remote receipts.
- **28 tests mới; full1012 PASS178.853s**. Bao gồm regenerate equality, geometry indices,
  integer-list buffer redaction, source shader analysis hash, exact Alert alpha binding,
  discrete pointer channel, wrong-file/wrong-clip/time rejection, font atlas and scope coverage.

```sh
python3 -m tools.verify.l3_visual_surface
python3 -m tools.verify.l3_visual_surface --file data.unity3d/level2 \
  --animator 4647 --clip 42 --clip-file data.unity3d/sharedassets2.assets --time .0625
# Font PID lấy từ default_font trong header hoặc fonts section, luôn kèm serialized file:
python3 -m tools.verify.l3_visual_surface --font FONT_PID --file FONT_FILE --text 'Tiếp tục'
python3 -m tools.verify.l3_recipe --root 10 --include-raw --out /home/user/pause.json.gz
```

## Thiếu được xác định bằng nguồn, không nói chung chung

0 read failures;1 header-only **Player_Attack_2 resources.assets:704560**, typetree EOF,
binary MB header vẫn giữ. **7 unresolved references**, đều ParticleSystemRenderer.m_Mesh
trỏ `unity default resources` chưa có trong input extraction. Không lấp mesh đó bằng quad/cube
phỏng đoán. Những renderer khác có null mesh/sprite không tự coi là lost asset; TMP/animation
có thể gán/generate sau, source references và serialized null được giữ.

Chưa có Unity render/frame acceptance, animation transition/blending execution, particle
simulation hay live text shaping/layout. Chuỗi102 đã nối nguồn layout→visual inputs→animation
property→material/shader→recipe; **L3 chưa hoàn tất**. Bước kế tiếp: camera/composition/culling
và renderer geometry generation thực tế trên các chain đã có, giữ rõ engine/runtime inputs.
Không chờ screenshot, không vẽ lại UI. Peer phải review độc lập, không tự ACK.
