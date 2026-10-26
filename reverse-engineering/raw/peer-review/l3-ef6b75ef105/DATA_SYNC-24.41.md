### 24.41 Report 105-a5a74747 — particle/transition/driven models (digger nhánh `arena/a5a74747`, head `25ac3b46b`, model `d446d47d5`; local **122 PASS**; **chưa có CI** — nhánh mới không trigger workflow, dispatch 403, chờ owner)

- **3 tool + 3 artifact, SHA pin đủ — xác minh 3/3 sau kéo** (9216e6b6… · b02b766c… · ed3f5173…).
- **Particle model** (`l3_particle_model.json.gz`): **954 hệ** (883 resources + 71 level2);
  join native constant **954/954**; prefab root **953/954** (lẻ `resources.assets:502274`);
  modules: Emission 954 · Color 801 · Size 707 · Shape 504; rate>0 **410** / zero 544; burst
  **402**; looping **599**; explicit randomSeed **0**; prewarm 198 (declared, not simulated);
  decode flags: **curve_keys_absent 954 · gradient_absent 801** ⇒ alpha = 1.0 + cờ, burst
  table chưa export; sim bounded: birth `k/rate`, lifetime/speed/size từ constant curves,
  **gravity = caller input**. Đếm lại từ artifact: khớp 100% mọi counts.
- **Transition scheduler** (`l3_transition_model.json.gz`): **232 controllers/667 states/
  468 transitions** (343 AnyState + 125 state); conditions **376** (If 375 + IfNot 1,
  threshold toàn 0.0); duration **30**; m_Speed toàn 1.0 (states_speed_not_one 0); 1 layer
  mỗi controller; **encoded destinations giữ nguyên (30000×232/30001×1/UINT_MAX×1) và
  scheduler TỪ CHỐI đi**. **Sửa cách đọc r99**: 464 "null interruption" thực chất là
  transition không có field (toàn selector) ⇒ tách `interruption_source_absent 464` +
  `interruption_sources {"0": 468}` (SHA model đổi vì vậy).
- **Driven props** (`l3_driven_props.json.gz`): route **67**/52.400 bindings;
  **CRC32(field)==attribute 52/52**; rect 755 · alpha 3.575 · active 5.230 · text 525 ·
  particle_module 147; **16.671 binding chưa có field — không đoán**; layout channel 665/665,
  **634/665 layout_exact**. Case thật: `box_gift_appear` (clip 986): `m_SizeDelta.x`
  1.0→**1.850000023841858** · `m_Color.a` 0.0→1.0→**0.5000000447** · `m_textAlignment` int
  **4100** qua bit-reinterpret float32; timeline Box_Gift 0,0667/0,4667/0,8167 nối scheduler +
  channel writes cùng modeled state.
- **Kết luận âm quan trọng**: **0 binding CanvasRenderer(222)/CanvasGroup(225)** trong 665
  clip — ai tìm ra clip khác thì báo xét lại. Policy scheduling = **model choice
  (`proven:false`)**: cần bằng chứng native Animator mới nâng thành engine truth; blend tuyến
  tính trên weight, không nội suy property; multi-layer chưa chạy (1 layer/controller).
- **Đối chéo độc lập (lần 49)**: particle 954/883+71/953/410/402/599/seed0 + module counts
  khớp · transition 343+125=468/376=375+1/30/absent 464/encoded 232·1·1 khớp · driven
  67/755/3575/5230/525/147/16.671/634-665 + case clip 986 khớp. Report số **105 trùng AI-1**
  (đang chạy batch 105-ef6b75ef) — phân biệt bằng prefix nhánh, đúng quy ước §24.40.
- **Lưu ý điều phối**: AI-1 đã CLAIM #1 qua comment (first-claim hoạt động); bảng sticky
  `6410945198` đã cập nhật (#9–11 DONE, thêm #14–16 từ kết quả 105). AI-2 nhờ owner dispatch
  CI cho nhánh `a5a74747`. ACK105-a5a74747 qua PR12.