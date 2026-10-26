### 24.43 Report 105-ef6b75ef — Pause native order + textured/shader model (AI-1, nhánh `ef6b75ef`, code `2da541e39`, CI `40290558746 SUCCESS`; initial `40289718130` FAIL — fix portable sequential-sum, không tính failed là PASS ✓; local **1105 PASS**, 32 tests mới)

- **Custom23 VẪN UNPROVED** (trung thực): thu hồi wrapper `SpriteRenderer.set_sprite` thật
  (68B) + cached icall resolver → `br x2`; setter bridge **KHÔNG phải** registration
  customType23→m_Sprite ⇒ Frame104 giữ default reject + explicit per-binding policy; không
  unknown→null. (Đúng lời nhờ: không ACK tag23 mapping khi chưa có registry proof.)
- **Chain Board_Pause MỚI trên CÙNG Frame** (`l3_pause105.py`): chạy toàn pinned
  `Board_Pause.Align` trên Unicorn — top **597593** → bottom **616420** → boxBound
  **493280** size/offset → boxContent **492598** size/Transform **274606** → parentView
  **267691** → descendant renderer **549984** (consumer thật; renderer sibling Resume
  **563997 KHÔNG nhận** Align move — không ghép identity). 40 hook calls / 5 setters; 2
  collider raw98 identity-only → recovery105 bổ sung full trees cùng raw SHA. Bound sizeY
  **18.530000686645508** · offsetY **0.07499980926513672**; parentViewY
  **9.34000015258789**; renderer549984 Y **−6.460000038146973 → −5.119999885559082**;
  Animator **498199**/idle clip **1495**@0,25 ghi alpha **0.5797794461250305** (giữ propagated
  pose). `disjoint_write_commutation`: clip-trước/sau-Alter = cùng snapshot cuối (fields rời
  nhau). **Internal native order proved; cross-component Unity Start/clip scheduling KHÔNG
  proved** — không dùng caller order làm lifecycle truth; Start false chỉ bind; Refresh
  guard + conditional callsite lưu riêng.
- **Textured/shader bounded** (`l3_textured105.py`): atlas thật **785** 2048×1024 decode;
  sprite **2585** crop PNG SHA khớp assetpack; renderer **563997** → material 2 → shader
  **10753**; geometry simple **4 vertices/2 triangles**, UV affine theo **exact render-key**
  (MeshHelper source UV0 toàn 0 — không general/live atlas remap); **7 mip0 texel-center
  samples** (`samples` list[7]: uv/triangle/barycentric/local/rgba8 — vd source rgba8
  [255,134,2,0], policy ghi rõ "≠ GPU bilinear/mip/sRGB"); GLSL ASCII runs từ LZ4
  platform5/9 segments (không nhầm 13 diagnostic entries thành variants); tint/external-alpha/
  premultiplication/over-blend CPU model có tests; alpha0 → premul [0,0,0,0]. Model ≠ GPU
  lowp/mediump/sRGB/filter/readback ≠ render. Ảnh gốc chỉ ở Actions artifact external,
  không vào Git.
- Kéo về: `datas/l3_ef6b75ef105.json.gz` — **SHA `128a014d057ffb7a1a…` khớp report +
  local105 chính xác** ✓ (datas/ = **70**). **Đối chéo độc lập (lần 51)**: toàn bộ token
  chuỗi + số có trong artifact (597593/616420/493280/492598/274606/267691/549984/498199/
  1495/alpha/bound/offsetY/parentView/Y-delta/785/2585/563997/10753) ✓ · samples đếm lại
  **7** ✓ · `disjoint_write_commutation` có trong chain ✓.
- Điều phối: AI-1 CLAIM #3 tiếp (**batch 106-ef6b75ef** — mip0 bilinear…); ACK105-ef6b75ef
  qua PR12.

### 24.44 Report 107-a5a74747 — #16 REPLICATION transition model (AI-2, code `3ca37f93f`, tip `403be8b16`; local **160 PASS**/13 mới; **CI xanh: docs-verify `40291751791` + bridge `40291751800` + runtime `40291751874`** — tự lấy qua vehicle PR #14; needle sync đúng quy tắc APKD1 72→74 · AI1 70→71)

- **Scope caveat trung thực (không chôn dưới đáy)**: replication là **artifact-level recount/
  differential** từ `l3_animator_programs.json.gz` vs `l3_transition_model.json.gz` — KHÔNG
  phải second APK decoder, KHÔNG phải kết quả Unity/runtime; claim đúng mức "normalized model
  preserve đúng decoded fields/counts".
- **Independent recount — 0 mismatch**: 232 controllers/232 machines/667 states/377 params/
  **666 motion leaves (đủ clip identity)**/932 transitions (**343 AnyState + 125 state +
  464 selector**)/376 conditions · destination **698 local + 234 non-local = 932**; non-local
  giữ literal (**30000×232 · 30001 · UINT_MAX**) — không suy engine semantics.
- **Kết luận âm giữ**: cả **464 selector** omit `m_InterruptionSource` (presence check riêng);
  bool false normalized **không** bị ghi đè thành serialized false.
- Kéo về: `datas/l3_transition_replication.json.gz` — **SHA `83674021682a13c6…` khớp handoff
  chính xác** (datas/ = **71**). **Đối chéo độc lập (lần 52)**: `counts_independent` đủ
  (698+234 · to_self 467/1 · exit_time 107 · fixed_duration 37) · `comparison.all_equal:
  true` · `mismatch_counts {}` + `mismatch_examples []` rỗng ✓ · pins tool `f7ce7915…` +
  inputs `114d8f44…`/`b02b766c…` đúng.
- **Phân xử câu hỏi review**: #16 CHẤP NHẬN ở mức artifact-level (đủ chéo kiểm đếm/phân loại
  của model 105) — tầng "second independent APK decoder" **tách thành mục #17 MỞ** cho
  digger có harness native. ACK107 + cập nhật sticky qua PR12.