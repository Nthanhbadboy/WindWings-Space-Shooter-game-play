### 24.29 Report 96 — Đưa L3 lên ưu tiên chính + UI screen→node→sprite index (peer `79fd382fff`, code `8789ef433`)

- **Đổi ưu tiên theo chủ dự án**: **hoàn thiện chuỗi L3 trước** (hình trong đúng cảnh · bố cục ·
  thứ lớp · ánh sáng · chuyển động · nhịp FX/âm); wing/map-save chỉ đào khi là **dependency cụ thể**
  của cảnh/hiệu ứng cần dựng. Không lấy export/test xanh/số native kết luận L3 đủ; không blind-A/B.
- **Bảng 6 mắt xích L3** (§1) — mỗi mắt ghi "thiếu cần làm", cấm đổi thành "đủ": identity/meaning →
  **asset→UI/cảnh** → composited (hierarchy/material/blend/light/particle trong cảnh) → motion/juice
  (ghép object/state, transitions, camera/feedback) → sound-đi-với-hình → **đối chiếu đầu ra** (gate
  chưa chứng nhận; cùng metric ≠ cùng hình).
- **Review spec `b000f905`**: lần 33 đính chính L3 **ĐÚNG** ✓ — nhưng còn stale: README mục "L3 bỏ"/
  "bỏ L2/L3" + `DESIGN_READINESS` câu "chỉ cần nếu làm L2/L3" ⇒ đã sửa ở lần 35 này (đánh dấu
  LỊCH SỬ / hiện hành). Đếm 505/643/27 của mình = **peer audit, chưa đo mới** — giữ nguyên nhãn.
- **UI binding index — ĐÓNG một phần gap lần 32**: `datas/ui_l3_bindings.json.gz` tra theo
  `sources`/`uses` (source index · node/component index · path · position/scale/rotation/size ·
  activeSelf · visual_properties raw); identity exact = **(serialized_file, path_id)** qua PPtr +
  externals, **không join tên toàn cục** (name_candidate_only không nâng thành exact). Đo:
  **797 sources/117 class** (thuộc `_index.csv`) · **76.806** sprite component observations ·
  **75.749** resolve nonnull · **1.057** null PPtr (không phải failed join) · **1.099 sprite identity
  khác nhau**; **54.787 file ngoài index chưa join** — không âm thầm gộp coverage. ⚠ **Sửa nhận định
  của mình**: report 43/46 **đã có** scoped joins — thiếu là bảng đủ rộng đưa cho design, không phải
  "chưa từng có". 12 tests binding mới; Verify `40224533473 SUCCESS`.
- **Queue L3 (thứ tự mới)**: ① UI reference chain (mở rộng ngoài index theo owner-scope: parent
  effective state, sorting/material/font, selected/pressed/disabled; đi Home → chọn màn/tàu/drone →
  HUD → pause/reborn → kết trận) ② gameplay appearance chain (player/drone/enemy/boss/bullet/
  pickup/background → prefab → SpriteRenderer/mesh/material/particle/Spine → clip/state/event).

### 24.30 Report 97 — audit đủ 55.584 layout + composition (peer `06ab4ef2b`, tests UI mới)

- **Không bỏ 54.787 file ngoài index — cũng không coi là 54.787 màn thiếu**: full scan
  (`ui_layout_inventory.py`, ~132 s + hash regression toàn file) → `datas/ui_layout_inventory.json.gz`
  + 4 shards: ngoài index **3.843.228** sprite-obs **chỉ còn tên** · **0** scoped `m_Sprite` ·
  **1.003.504** TMP không font PPtr (schema legacy không giữ) ⇒ **exact identity từ layout legacy
  là bất khả** — muốn exact phải về serialized source; 30.827 topology groups · 14.081 file match
  indexed (409 groups) · 30.418 groups không candidate. ⚠ **Sửa hướng đọc report 96 của mình**:
  "54.787 chưa join" ≠ "54.787 màn độc lập chưa biết" — cùng 117 class label có trong index.
- **Composition** (`datas/ui_composition.json.gz` + 6 shards): **100.312** visual-component obs ·
  **99.731** matrix TRS (581 ambiguous — không thay bằng identity) · activity 89.754 F / 10.409 T /
  149 unknown · **76.802** material exact scoped join · **18.467** TMP font + sharedMaterial.
- **Bẫy slash thật**: node `TMP SubMesh [TextMeshPro/Sprite]` chứa `/` — split cuối bịa thêm cấp,
  mất 1.478 parent matches; sửa bằng suffix `/` + name; **160 ambiguous parents** giữ nguyên.
- ⚠ **renderer_enabled = unknown** (exporter whitelist không có m_Enabled) — không default true.
- Backlog đổi từ file-sang **source/scene chains**: ① recovery PPtr identity + m_Enabled ② ghép
  font/material/renderer + camera/Canvas theo flow Home→chọn→HUD→pause/reborn→kết trận
  ③ gameplay appearance chain ④ sau khi đủ chuỗi mới dựng/đối chiếu output.

### 24.31 Report 98 — chuỗi APK → scene recipe → hình/motion/VFX/audio (peer `1f2d12f6e`, **921 tests**)

- **Root views: 805** (12 core UI: Maps/Players/Drones/Reborn/Endgame/Stage, 3 Reborn_IAP, Home,
  Pause, GP_Tutorials + 793 resource GO) · 37.766 logical/25.536 visual nodes · 3.504 typed assets ·
  1.587 animators · **665/665 clips numeric channel-exact** (301.603 streamed keys; đã sửa 31 sprite
  clips: cộng `discreteCurveCount`; sprite keys giữ mapping rời rạc, không blend pointer) ·
  **52.400 bindings** (51.990 unique / 393 unresolved / 17 ambiguous) · **2.139 callbacks** (904
  persistent + 1.235 anim-event) · 2.037 AllClipName · 92 SoundClip. Raw 128.724 objects /
  345.090 edges; 0 read failure; 5 header-only (GunEventCatcher, Player_Attack_2…) giữ rõ.
- **3 recipe mẫu** (CLI `tools/verify/l3_recipe.py`, `--include-raw`, header thắng raw cũ):
  **Board_Pause** root10 — 235 nodes/404 assets/4 Animator/5 clips (Appear 0,5 s · Hide 0,333 s)/
  15 callbacks/26 sound fields; `Button_Sound.soundClickDown=1 → Sfx_ClickDown → AudioClip:1695`,
  native `OnDown@0x141fdc4`/`OnClick@0x141fddc` nối đúng class+field; **Effect90045** root402 —
  48 nodes/68 assets/310 bindings, ParticleSystem giữ serialized modules; **Player_Attack_13**
  root769 — 33 nodes, bridge enum5 `Sfx_Shot1 → AudioClip:1752` (khớp `wing_emission_flow`).
- **Camera không bị bỏ**: 5 Camera + 1 Canvas (level0) + native size writers nối qualified identity
  với `datas/camera_scaler_contract.json` (SHA pin): `max(h/w × 5,4; 9,6)` — không nhầm
  CameraScaler (game) với CanvasScaler (Unity).
- Kéo về: `datas/l3_scene_chains.json.gz` + 37 shards `l3-scene-chains/` · `ui_layout_inventory` +
  `ui_composition`. **Đối chéo độc lập bằng datas trong repo (lần 36): counts khớp 100% report 98 ·
  camera contract + composition + inventory totals khớp 97.**
- **Review độc lập đợt 2 (lần 37 — peer ghi CI xanh `40229636747 SUCCESS` @ receipt98/handoff
  `6402605773`)**: đếm **từng loại từ 22 shards riêng** (không tin `counts` tổng) — callbacks
  **2139** ✓ (904 persistent + 1.235 anim-event) · sounds **2037** ✓ · animation_bindings **52400** ✓ ·
  assets **3504** ✓ · scene_context **5 Camera** ✓ (+1 Canvas) · `camera_scaler_contract.json` chứa
  formula + factor 5,4/min 9,6 ✓ — **khớp 100% cả 6 điểm đo được**. 5 điểm nhờ review: header
  authority/ambiguity/discrete-keys = proof gốc ở raw (bên peer); camera ownership + callback/sound
  gates **đã xác mức data**. ACK97/98 ✓ (comment `6402657559`); batch L3 **CI xanh toàn chuỗi**.
- **Không phải**: rendered approval · 805 views ≠ 805 prefab độc lập · batch 12 core không nhận công
  797. Tiếp: recipe → composition/playback, không thêm vòng inventory.

### 24.32 Report 99 — Animator programs + property probes (peer `4d0dc6906`→code `5c3ba250d`, CI `40230913183 SUCCESS`, **940 tests**)

- **Controller → state → clip → thuộc tính đúng object** (không còn controller là raw blob):
  **232 controllers/232 machines/667 states** (mỗi controller 1 layer) · **1.587 Animator** nối
  direct `m_Controller` (không nối vì trùng clip/name) · **377 parameters** (tên theo `m_TOS`,
  typed default slot) · **343 AnyState + 125 state transitions** (destination/điều kiện/eventID/
  threshold/exit-time/duration/interruption — giữ source) · **666 motion leaves** nối hết đúng
  scoped clip; 1 empty machine + 1 state không motion **không tự chèn**; destination encoded
  30001/30000/UINT_MAX giữ là selector/exit (không ép index).
- **Probe 665/665 clips** đầu/giữa/cuối — **1.853 clip-time probes**: 86.905 streamed + 51.926
  constant + 69 discrete + **1.461 initial-constant** (lỗi mô hình đã sửa: frame `-FLT_MAX` là
  key initial-value thật a=b=c=0, d = giá trị ban đầu — không phải unknown giả; sprite clip 965:
  mapping 0 có sẵn từ frame 0, key đầu 0,2333 s mới đổi) — **0 unknown tại các điểm probe**
  (không suy thành mọi timestamp). Kết quả = arithmetic model, **không** phải readback Unity.
- **Ví dụ Popup_QuitMissions** (Board_Pause): GO57508 → Animator **495980** → controller
  **1974** (tên Popup_Network reused — tên không đổi identity) → default state **Appear** → clip
  **1572**; probe: t0 scale 0/0 alpha 0 · t0,25 scale ~1,0304 alpha ~0,83137 · t0,5 scale 1/1,
  alpha **giữ ~0,83137** (serialized curve — không sửa thành 1 theo cảm giác).
- **Audit 410 non-unique bindings** = **376 path không có trong subtree + 17 thiếu hẳn component
  class** (13 cần MonoBehaviour mà GO chỉ có Transform/SpriteRenderer; 4 cần BoxCollider2D —
  *wording 98 sửa: không phải inheritance mismatch*) + **17 ambiguous giữ nguyên**.
- Kéo về: `datas/l3_animator_programs.json.gz`. **Đối chéo độc lập (lần 38): counts khớp
  10/10** (232/232/667/377/343/125/666/1587/410/1) · diagnostics **376/17/17** ✓ · Animator
  495980 → controller 1974 (324 refs) → clip 1572 (62 refs) ✓; probe values sống ở CLI output +
  raw `local99.json` (bên peer), không trong contract.
- **L3 VẪN CHƯA hoàn tất** (peer ghi rõ): còn script-driven runtime selection · transition
  scheduler/layer blending · driven RectTransform · particle sim · shader/stencil/culling ·
  composition qua viewport. Bước phải đi: **program/property model → composition/playback thực
  với external original assets**. ACK99 qua PR12.

### 24.33 Report 100 — script UI → activation → state/clip → event → deactivation (peer `0ce8cc017`, code `ad986c7b9`, CI `40232850860 SUCCESS`, **957 tests**)

- **Chuỗi Popup_QuitMissions (Board_Pause) ĐÓNG đủ bằng source** — lifecycle thật, không
  "chọn state bằng tay": GO **57508** inactive + `Popup_Notices.SetPopup@0x13b83cc` →
  **SetActive(true)** @0x13b83f4 → Animator **495980** → controller **1974** (tên Popup_Network
  reused) — **SetPopup ≠ Animator.Play(Appear)** (entry/reset là engine, chưa readback);
  `OnPressedButtonExit@0x13c5370` đọc `anim+0x20` → literal **"Hide"** (GOT→RELA→metadata, không
  tìm chữ trong disassembly) → `Animator.SetTrigger` → transition condition → state Hide → clip
  **1573**; event **OffBoard @0,333 s** → same-GO receiver **644901** →
  `Popup_Notices.OffBoard@0x13ca5dc` → exitAction + **SetActive(false) cùng GO 57508**.
  Guard `exitAfterConfirm+0x38` giữ symbolic (không gọi mọi confirm là đóng vô điều kiện).
- **Recovery native UI**: **1.074 methods/13 root classes** (namespace thật **TuPro** cho
  `UIObjectAnchors` — lần recover fail đã sửa đúng, không bỏ class); bytes dùng next-distinct-RVA
  + `span_decode_status` (không giả padding là instruction).
- **Counts** (`datas/l3_ui_drivers.json.gz`): **214 UI instances · 1.751 potential calls ·
  receivers 1.414 resolved / 337 unresolved** (không resolve ≠ source thiếu) · **230 animator
  routes · 687 exact receiver+RVA links · 409 callback/effects · +9 inherited candidates** (46
  old anim-event gaps: 9 có base-declared qua `Popup_QuitEvent : Popup_Notices`, 37 chưa).
  Sửa model getter: **+140 receiver joins** qua `get_transform`/`get_gameObject` edges (thiếu
  transfer function, không phải APK thiếu).
- Kéo về: `datas/l3_ui_drivers.json.gz`. **Đối chéo độc lập (lần 39): counts khớp 8/8** ·
  chuỗi Popup CÓ trong artifact (57508 ×24 · 495980 · 1974 · 644901 · 1573 · OffBoard ×168 ·
  13ca5dc · 13b83cc) ✓.
- **L3 CHƯA render-complete** (peer ghi rõ): CFG là over-approximation, chưa transition
  scheduler/runtime delegate/particles/shaders/composition; 5 header-only + 52 default-mesh
  giữ nguyên. Bước tiếp: composition/playback thực. ACK100 qua PR12.

### 24.34 Report 101 — camera → safe-area → UI anchors/renderer → recipe (peer `91a0ad6df`→code `b18e783a7`, CI `40236171639 SUCCESS`, **984 tests**)

- **Quét toàn APK 125.453 MonoBehaviour headers**: **584 TuPro.UIObjectAnchors + 1 ObjectScaler**
  (= 585 typed instances); **1 header chưa phân loại giữ nguyên** (`resources.assets:580792` —
  thiếu `unity default resources`, không coi là chắc chắn không có target class); typed read
  errors 0. Bounded context **2.526 objects · 9.161 edges resolved / 660 null · 0 unresolved**;
  parent poses đủ 585 targets; 0 pose errors; 0 unmodeled affine bridges.
- **Camera**: 6 camera nối đúng **6 native CameraScaler writer bindings**; 4 MainCamera-tag
  candidates thuộc scene khác nhau (không phải 4 camera đồng thời); **576 anchors thiếu
  serialized uiCamera / 8 explicit** — không tự chọn Camera.main từ danh sách global. Native
  Start gán Camera.main qua `op_Implicit`; **gọi ObjectAnchor trực tiếp KHÔNG tự chạy Start**
  (guard playOnStart). 461 playOnStart=true / 55 fixed-max (flags có thể runtime đổi).
- **Semantics lấy từ native**: enum None0…Right9; GetRootAnchor jump bytes `00090f03070d0a10`;
  roots ±5,4/±9,6 đọc literal + kiểm bằng execution. General path ghi world rồi restore local.z;
  Left/Right chỉ sửa world-X, **không restore local.z**. Fixed-max: min(UI half-height,
  clampCamSize default **12.420000076293945** — static mutable, CLI hỗ trợ override finite) +
  aspect clamp [0,43478259444236755; 0,75]. Top/bottom dùng SafeArea của Camera.main; cache chỉ
  recompute khi top/bottom có 0.
- **Alert (level2)**: ObjectScaler **6686 → SpriteRenderer 5105**, cùng owner **GO110 `Alert`**
  (+ Animator **4647** — metadata-only, KHÔNG có attachment trong bank animator-programs); H14
  full/clamp: height **24.84000015258789**; drawMode1/width 10,8; sprite `sharedassets2.assets:114`
  · material `globalgamemanagers.assets:2` — size/identity chain, KHÔNG phải render proof.
  Join bank100: **92 call links / 85 anchors** (không phải complete census); Pause:
  callsite 0x12cb150→597593 (top) · 0x12cb160→616420 (bottom).
- **Probe synthetic** 1080×2400, safeRect [0,96,1080,2208] → half-height
  **12.000000953674316**; Pause top 597593 worldY 7,9→**9,34** (model = native); H14 → 11,18
  (raw, không gán cho máy thật). Unicorn chạy source bodies NHƯNG metadata/engine stubs + dùng
  chung float64 affine bridge ⇒ **không phải Unity transform/render proof**.
- Kéo về: `datas/l3_layout.json.gz`. **Đối chéo độc lập (lần 40): counts khớp 13/13**
  (2.526 · 9.161+660 · 585=584+1 · 6 cameras · 4 candidates · 576+8 · 20+4 native checks ·
  0 pose · 0 read · 1 header error đúng 580792) + **461 playOnStart / 55 fixed / 85 anchors-92
  links đếm lại từ instances** ✓ · chuỗi Alert 6686→5105/4647 + Pause 597593/616420/690342 +
  callsites ✓ (sprite/material lưu tách field file+path_id). **L3 CHƯA hoàn tất** (peer): tiếp
  geometry/material/font + particle/shader/composition + engine transition/blending. ACK101
  qua PR12.

### 24.35 Report 102 — layout-owner visual construction (peer `9d38a08d1`→code `d1a65f01d`, CI `40238106907 SUCCESS`, **1012 tests**)

- **Scope: descendants dưới 585 layout owners + asset closure** — KHÔNG phải toàn APK, KHÔNG
  phải cả 797 recipe roots; recipes công bố coverage/out-of-scope IDs.
- **Đào visual thật từ source**: **56.714 objects / 16.061 GO · 11.380 renderers · 153
  materials · 17 shaders** (parsed + decompiled-analysis — **KHÔNG phải replacement shader hợp
  lệ**) · **1.389 sprites + 2 meshes** decode geometry số (không phải render) · **7 fonts /
  7 atlases / 2.354 character entries · 1.737 texts · 954 particle modules** (data có, simulation
  KHÔNG claim) · **đủ 348 clips** decode đúng channel widths · **1.057 animators / 91 controllers /
  79.907 bindings (74.916 unique / 4.983 unresolved / 8 ambiguous)**. 0 read failures; **1
  header-only** giữ nguyên (Player_Attack_2 `resources.assets:704560`); **7 unresolved builtin
  ParticleSystemRenderer mesh refs** (`unity default resources`) giữ — không bịa default mesh.
- **Alert gap (101) ĐÓNG mức source/model**: level2 GO110 scaler 6686 → renderer 5105 / sprite
  `sharedassets2.assets:114` / material `:2` / shader `Sprites/Default`; animator **4647 →
  controller `sharedassets2.assets:78`** với states **none44 / alert42 / fade43**; binding
  path0/type212 → cùng `renderer.m_Color.a`; clip alpha **0 → 0,784313738 trong 0,125 s**,
  reverse trong 0,25 s; params Alert/Fade giữ. **KHÔNG** state scheduling / trigger delivery /
  blending / render acceptance.
- Kéo về: `datas/l3_visual_surface.json.gz` + **249 shards** `l3-visual-surface/` (3 animators ·
  200 bindings · 1 controllers · 1 fonts · 4 geometry · 1 materials · 1 motion · 3 particles ·
  29 renderers · 1 shaders · 5 texts). **Đối chéo độc lập (lần 41): counts khớp 17/17** (gồm GO
  16.061 đếm lại từ `source_gameobjects` · header-only đúng 704560 · unresolved_edges đúng
  ParticleSystemRenderer/.m_Mesh) + **249 shards đúng cơ cấu** + **Alert chain trong chunks**:
  controller 78 tên "Alert" · clips none44/alert42/fade43 · alert42 chứa 784313738 + 0.125 ·
  fade43 chứa 784313738 ✓.
- Xin audit: MeshHelper coords/UV/index vs không sign-flip OBJ; live-atlas/sliced/tiled/
  skinning/TMP procedural; integer-list buffer redaction; glyph rect/atlas bounds + static
  fallback; source-qualified Alpha CRC binding; recipe scope coverage. **L3 CHƯA hoàn tất**:
  tiếp camera/composition/culling + actual geometry generation/engine execution. ACK102 qua PR12.

### 24.36 Report 103 — camera → world pose → geometry → layer gate/clip → composition (peer `8febe90e11`→code `dddd75aed8`, CI `40240026886 SUCCESS`, **1043 tests**)

- **Merge raw101+102** (không recovery mới): qualified file/pathID, kiểm **1.760 overlapping
  bodies cùng raw SHA** + pointer edges không xung đột → **57.480 objects** trong merged graph.
- **11.380 renderer world poses** dựng đủ từ typed Transform/RectTransform parent PPtrs (gồm
  root local TRS — khác matrix layout-root frame r95); parent thiếu/cycle KHÔNG thay bằng
  identity. Phân loại: **558 thuộc serialized scene level0–3 · 10.822 asset templates** (không
  tự coi đã instantiate).
- **6 camera** đầy đủ pose/projection/mask/clear/depth/display/target + writer bank101
  (sharedassets0:79 vẫn là template). **1.104 same-scene pairs = 558 pass / 546 fail layer
  mask** — chưa cộng footprint/alpha/shader, không gọi là visible; không tạo total draw-order
  từ sortingLayerID; không coi camera khác scene là một live stack.
- **Alert chain (source/model đến footprint — siết wording theo góp ý peer, lần 44)**: 1080×2400 → half **12.000000953674316** → native ObjectScaler size
  **10.800000190734863 × 24.000001907348633** → position-only zero-border sliced rect (border≠0/
  tiled = not_generated, không dựng quad thay) → world z=1 → depth 11/21 ở Game 3975 (z=−10) /
  Main 3976 (z=−20); footprint giao viewport ở cả hai NHƯNG **mask 7959 (Game) LOẠI layer5 ·
  mask 32 (Main) GIỮ**; Main footprint ~full viewport
  [0.000033378598385258584, 0, 1079.9999666214017, 2400]; alpha alert42@0,0625 =
  **0.3921568840742111** (từ 102) — không apply trigger, không thành rendered frame.
- Geometry/clip làm thật: affine inverse + uint32 layer test + ortho projection (+Z forward);
  triangle clip **6 planes** giữ case mọi vertex ngoài mà triangle vẫn cắt màn hình; simple
  sprite dùng decoded vertices; TMP/procedural/skinned/particle/line/trail + UV/live-atlas/
  skinning/vertex shader/raster/occlusion/depth/blend CHƯA áp; float64 + non-rigid camera từ
  chối; probe từ chối template/cross-scene khi thiếu explicit full override matrix.
- Kéo về: `datas/l3_composition.json.gz`. **Đối chéo độc lập (lần 42): counts khớp 10/10**
  (11.380 · 6 · 1.760 · 57.480 · 558+10.822 · 1.104 = 558+546) + **mask xác minh bằng số học**:
  7959 & 32 = 0 (Game loại layer5) · 32 & 32 = 32 (Main giữ) · depth −1/0 + clearFlags 2/3 ✓.
  Probe values (10.8×24.0 · alpha .3921 · footprint) sống ở CLI/raw bên peer, KHÔNG trong
  contract. Recipe10 +8 template composition records. **L3 CHƯA hoàn tất**: tiếp actual
  geometry/driver application + shader/particle/text/spine execution. ACK103 qua PR12.

### 24.37 Định hướng vòng kế (chủ dự án — lần 43): probe compose thay vì tăng counts

Dừng mở rộng counts/contract riêng lẻ. Bước kế: **layout-write (101) + animation-write
(99/102) tác động lên CÙNG trạng thái Transform/renderer, rồi đưa trạng thái đó qua camera
(103)**. Đã gửi peer 2 probe cụ thể qua PR12 (dùng lại 101/102/103, không recovery mới,
không render):

- **Probe A — Alert 5105 (same-state compose)**: layout-write `ObjectScaler.Start` → size
  [10.800000190734863, 24.000001907348633] + anchor/parent pose GO110 → world transform;
  animation-write clip alert42 tại t ∈ {0; 0,0625; 0,125} → `m_Color.a` theo đường
  0 → 0.784313738/0,125 s (@0,0625 = 0.3921568840742111 từ 103) — xác nhận hai write chạm
  **khác field của cùng renderer**, không ghi đè; composed qua **Main 3976** (mask 32 giữ
  layer5, depth 21) → footprint px + camera-local depth + RGBA theo t. Đầu ra mong muốn:
  **3 dòng readback cùng một t** (layout-only / animation-only / composed).
- **Probe B — Popup_QuitMissions (Board_Pause root10)**: Appear (clip1572) tại
  t ∈ {0; 0,25; 0,5} → scale {0; ~1,0304; 1} · alpha {0; ~0,83137; giữ 0,83137}; popup
  GO57508 + Canvas thuộc resources.assets — theo phân loại 103 là **template context**: peer
  cho biết **placement authority** (override matrix tường minh hay scene2 instance) rồi camera
  nào trong 6 có mask giữ layer popup (nhiều pass thì depth/clear nào thắng theo snapshot,
  không tự tạo stack); xuất footprint theo t.

Câu hỏi kèm: harness Unicorn (101) + math (103) trả được composed state mức model không, hay
cần stub thêm? Ranh giới giữ nguyên: model ≠ readback Unity ≠ render — probe là **gate
  compose-state**, không phải render approval. Không kéo dữ liệu mới vòng này (datas/ = 65).

### 24.38 Report 104 — shared modeled frame: layout write + clip write trên CÙNG state (peer `f620ba4a67`, local **1072 tests PASS**; peer LÀM TRƯỚC/song song với probe A/B mình gửi — đúng hướng)

- **Peer review nhánh spec mình** (`raw/peer-review/l3-23bf66c7/` — snapshot DATA_SYNC +
  DESIGN_READINESS SHA-pinned): ① ACK giúp phát hiện sai sync nhưng **không thay
  numerical/native audit**; ② headline "Alert chain full"/"geometry làm thật" = **source/model
  đến footprint**, không phải full visual/runtime (đã siết §24.36); ③ **không dùng số file
  datas/ hay số tests như tỷ lệ hoàn thiện bộ mặt game** (bên mình: đó là inventory/gate
  verify, không phải % — giữ đúng nghĩa đó); ④ review chuyển sang **reproduction/
  counterexamples** (Start false vs direct Align, propagation, cache khi camera đổi, f32
  rounding, rollback, encoded pointer binding).
- `tools/verify/l3_frame.py` tạo **một shared modeled state**: explicit modeled Camera.main →
  CameraScaler half-height; **native bounded Start/ObjectAnchor/ObjectScaler chạy thật**
  (harness101) → writes persist vào state; clip-local channels → typed writes **float32
  store**; world matrices đọc lại từ overlay (không stale); projection dùng current
  size/color/pose/mask. Start explicit ≠ Unity đã dispatch khi inactive.
- **Case Alert = Probe A thực tế** (camera 3976, 1080×2400): serialized sau camera-resize
  sizeY **19.200000762939453** → native scaler **24.000001907348633** + alert42@0,0625 alpha
  store **0.3921568989753723 (float32)** — coefficient double **0.3921568840742111** giữ RIÊNG
  (không gọi là mismatch); projected 240.000038→2159.999961 rồi 0→2400; fade43@0,25 tiếp theo
  → alpha 0 (geometry KHÔNG bị xoá). Hai writer chạm khác field cùng renderer 5105.
- **Case Border_Info (mới)**: `level2:7048` GO1414/renderer5739 playOnStart=false — native
  Start chỉ bind camera, KHÔNG ghi position; explicit Align → worldY 7→**8.440000534057617**,
  **320 descendants** nhận cùng delta (đếm lại 320/320 ✓); child sprite 5452 px bottom
  1717.700156805613→1861.7001987672797; root 5739 border≠0 → **not_generated** (không dựng
  quad giả); safeArea cache dùng chung per-Frame, không tự refresh.
- **Pointer quan trọng**: sprite bindings attribute0/customType23/type212 (Animator4695 /
  resources clip1609) **KHÔNG thể gọi là CRC(m_Sprite)** — default writer từ chối; chỉ nhận
  explicit per-binding policy `m_Sprite` (log `explicit_custom_binding_field_policy`, sống ở
  tool/tests, không trong artifact); pointer override = runtime qualified ref, không bịa
  fileID. Clip transaction atomic = **bảo đảm của tool**, không phải Unity semantics.
- Kéo về: `datas/l3_frame_cases.json.gz` (2 cases: alert before/after/faded · border_info
  before/after_start/after_align + descendants + child projections). **Đối chéo độc lập
  (lần 44): mọi số report có trong artifact đúng case** + 320/320 đếm lại ✓. Recipe chỉ gắn
  `frame_application` contract auto_execute=false. 101/102 gaps giữ nguyên. **L3 vẫn một
  phần**; ưu tiên peer: native/custom binding + driver order trên concrete chain → textured
  geometry/shader execution. ACK104 + trả lời góp ý review qua PR12.

### 24.39 Report 104 final — receipt CI + reproduction độc lập từ artifact (peer `9f90c1acb`→final `81fed2233`, CI `40242708365 SUCCESS`, **1073 tests**)

- **Peer fix 2 pitfalls hai-state trước chốt** (`81fed2233`): ① CameraScaler phải ghi vào
  **current camera property tree** — camera clip về H8 ghi SAU phải thắng resize trước đó
  (không để half-height side-cache che write); ② Start camera binding phải đọc được qua
  **current object reference view**; thêm: root mount không freeze che subsequent root writes.
  30 frame tests; artifact refresh **chỉ đổi SHA pin tool** trong `inputs` (diff struct 1 path —
  dữ liệu cases giữ nguyên, số đối chéo §24.38 vẫn hợp lệ).
- **Reproduction từ artifact + số học (lần 45 — theo yêu cầu peer, 5/5 PASS)**:
  ① **False Start vs explicit Anchor**: `after_start` == `before` **bit-exact** (Start false
  không move/không capture root) · explicit Align → world_matrix Y 7.0 → **8.440000534057617**;
  ② **320/320 descendants**: mỗi cái đúng **1 phần tử** đổi (index 7 = translation Y) delta
  **1.440000534057617** ±1e-9, không phần tử khác bị chạm; ③ **current-pose projection**: child
  5452 worldY 5.5 → 6.940000534057617 (px bottom 1717.700156805613→1861.7001987672797);
  ④ **f32 rounding**: `f32(0.3921568840742111)` = **0.3921568989753723** — khớp store chính xác
  (không phải asset mismatch); ⑤ **fade43 → alpha 0** NHƯNG sizeY 24.000001907348633 GIỮ
  (footprint không mất vì alpha 0).
- **Chưa chạy được (cần APK inputs + harness Unicorn — bên peer)**: camera clip H8 last-write
  projection, Start→current uiCamera, transaction rollback, tag23 policy label — chỉ đọc được
  qua 30 tests của peer, chưa independent execution (peer cũng ghi `independent_execution_ack:
  false`). **L3 vẫn một phần**; ACK104-final + kết quả reproduction qua PR12.

### 24.40 Đa digger (chủ dự án — lần 46): thêm 2 AI đào dữ liệu

Chủ dự án tăng đội hình đào: peer hiện có (`ef6b75ef`) + **2 AI đào mới**. Kiểm ls-remote đầu
vòng (lần 46): remote vẫn 3 nhánh (nhánh spec `20330d0e` `c9871cb73` · peer `ef6b75ef`
`9f90c1acb` chưa đổi · `main` nguyên) — 2 digger mới **chưa push**. Quy ước áp cho MỌI digger
từ nay:

1. **Mỗi nhánh tip fetch riêng mỗi vòng** — không coi report tới liền kề là từ cùng nguồn.
2. **Artifact chỉ nhận qua report có SHA nguồn** (nhánh + tool/input SHAs) — thiếu SHA thì
   nhờ bổ sung trước khi kéo.
3. **Đối chéo độc lập bắt buộc** trước khi ghi DATA_SYNC (counts tự đếm từ contract, không
   chép tổng).
4. **3 path shared** (`datas/PROVENANCE.md` · `boss_anim_events.csv` · `player_start_stats.json`)
   — nhánh spec giữ; digger nào xóa path shared thì ghi nhận và KHÔNG theo.
5. **Không merge chéo nhánh digger**; dữ liệu hợp luồng qua nhánh spec, mỗi artifact giữ
   provenance nhánh nguồn.
6. **ACK mỗi report = 1 comment PR12 riêng**, ghi rõ nhánh/nguồn; khi đánh số report va chạm
   giữa các digger thì ghi kèm tiền tố nhánh (`Report <N> — <nhánh>`).
7. Vai không đổi: digger đào sâu; spec = đối chéo + tài liệu + handoff, không tự đào thay.

**Chống lấn việc (bổ sung lần 47 — chủ dự án hỏi kịch bản khi digger xong phần rồi lấn nhau):**

- **Ownership theo miền artifact (cố định, ai muốn đổi phải qua chủ dự án):** AI-1 `ef6b75ef`
  = custom binding proof · driver order concrete chain · texture decode + execution model
  shader Sprites/Default; AI-2 = geometry generator (TMP/glyph/atlas · sliced/tiled
  non-zero-border · atlas remap · skinning bounds) + 3 nhóm gap (7 builtin mesh · 5
  header-only · 52 default-mesh); AI-3 = particle sim · transition scheduler/layer blending ·
  driven RectTransform/CanvasRenderer; spec = datas chung + đối chéo + docs + điều phối
  (không đào).
- **Đọc chéo được, sửa chéo không**: muốn dùng dữ liệu miền khác thì CHỈ dùng artifact ĐÃ
  handoff trên PR12 (có SHA), ghi provenance nguồn vào report; không kéo artifact dở/không
  review; không sửa tool/file của digger khác (cần mở rộng thì làm tool riêng hoặc đề xuất
  trên PR12).
- **Xong phần của mình thì làm gì**: báo "scope của tôi đã cover hết X" trong handoff +
  ĐỨNG chờ, hoặc nhận việc mới do chủ dự án phân — KHÔNG tự nhảy sang miền ai.
- **Trùng việc**: ai có batch trước về việc đó = owner tạm; thằng sau hoặc rút sang biên
  chưa ai làm, hoặc khai báo là **independent replication** (đào trùng độc lập vẫn có giá trị
  — hai nguồn cùng số = mạnh hơn) nhưng phải ghi rõ trong report, không giấu.
- **Va chạm số liệu**: cùng object/ID nhưng 2 số khác nhau → spec flag **disputed** trên
  PR12; mỗi bên trích raw + SHA của mình; không bên nào tự nhận đúng; phân xử = chủ dự án
  hoặc digger thứ 3 xác minh độc lập.
- **Phát hiện lấn việc im lặng**: spec diff từng tip mỗi vòng (`--name-status` tip mới vs cũ)
  — artifact/domain lạ trong nhánh A mà report A không provenance → trả lại, yêu cầu tách
  hoặc ghi provenance; trùng tên file datas/ → đổi tên có prefix miền.

**Tự điều phối — không đợi phân việc (bổ sung lần 48):** bảng điều phối sống ở **PR12 comment
sticky `6410945198`** — spec **sửa tại chỗ** (GitHub PATCH, đã test quyền) mỗi vòng, digger đọc
bản đó là mới nhất. Cơ chế: ① BACKLOG 13 mục đã biết (1–12 claim được; 13 = L2 ⛔ chờ chủ dự
án bật lại) ② CLAIM comment **trước khi làm** — first-claim wins theo thời điểm ③ mục đã
CLAIM không làm, trừ khi khai `REPLICATION` ④ HANDOFF xong thì spec cập nhật bảng ⑤ va chạm
số → `DISPUTED`. Trạng thái AI-1 trong bảng = suy từ tip (`1db187112`, chưa handoff) — ghi rõ
mức tin. Prompts digger thêm 1 dòng: đọc bảng mỗi vòng trước khi chọn việc.