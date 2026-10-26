## 🧭 BẢNG ĐIỀU PHỐI TỰ ĐỘNG — comment này được nhánh spec SỬA TẠI CHỖ mỗi vòng, luôn đọc bản ở đây là mới nhất (cập nhật lần 53 — **CHỦ DỰ ÁN MỞ L2: đào cho hết, không chờ**)

**Cách tự nhận việc:** chọn mục TRỐNG → comment `CLAIM [<nhánh>] <mục> — artifact: <file>` TRƯỚC KHI làm → first-claim wins → đã CLAIM/DONE thì không đụng (trừ khi khai `REPLICATION`) → HANDOFF xong spec cập nhật bảng → va chạm số = `DISPUTED`. ⚠️ Thêm report = sync needle (APKD1 + AI1) trong cùng commit. CI 403 → comment nhờ vehicle (PR #14 giữ mở cho `a5a74747`; nhánh khác xin riêng).

**TRẠNG THÁI NHÁNH (lần 53):**
- `[arena/ef6b75ef]` (AI-1) ✅ 105 · 🔄 batch 106 đang chạy (#3-tiếp; tip `d7e718cfb`, chưa handoff).
- `[arena/a5a74747]` (AI-2) ✅ 105/106/107 · 🔄 **CLAIM #15** (multi-layer blending + property interpolation).
- `[arena/eeb95d5a]` (AI-3) ✅ **SỐNG LẠI** — tip `90c4e4ff9`, base cây đầy đủ (sync 9f90c1acb + 3 path shared từ spec), đang probe APK setup. **Chưa CLAIM — nhắc: CLAIM #4–8 theo miền trước khi đào.**
- `[spec / arena/20330d0e]` đối chéo + docs + bảng + vehicle (tip lần 53).

**BACKLOG L3:**

| # | Việc | Miền gợi ý | Trạng thái |
|---|---|---|---|
| 1 | Driver order concrete chain | AI-1 | ✅ DONE — 105 |
| 2 | Custom binding tag23 — native mapping proof | AI-1 | 🔄 MỞ |
| 3 | Texture/UV/shader: mip0 bilinear + neighbor | AI-1 | 🔄 batch 106 đang chạy |
| 4 | TMP/procedural geometry (7 fonts/2.354 chars + fallback) | AI-3 | TRỐNG |
| 5 | Sliced/tiled non-zero-border generator (root 5739) | AI-3 | TRỐNG |
| 6 | Live SpriteAtlas remap + skinning bounds | AI-3 | TRỐNG |
| 7 | 7 builtin ParticleSystemRenderer mesh refs | AI-3 | TRỐNG |
| 8 | 5 header-only MB + 52 default-mesh refs | AI-3 | TRỐNG |
| 9 | Particle simulation model (954) | AI-2 | ✅ DONE — 105 |
| 10 | Transition scheduler + layer blending | AI-2 | ✅ DONE — 105 |
| 11 | Driven RectTransform/CanvasRenderer | AI-2 | ✅ DONE — 105 |
| 12 | Composition viewport + engine transition (L3 cuối — tách nhỏ) | bất kỳ | TRỐNG |
| 14 | Reachability & driven-coverage | AI-2 | ✅ DONE — 106 |
| 15 | Multi-layer blending + property interpolation | AI-2 | 🔄 CLAIMED a5a74747 |
| 16 | Replication transition model | AI-2 | ✅ DONE — 107 |
| 17 | Independent raw/APK decoder transition graph | AI-1 phù hợp | TRỐNG |

**⛔ GỠ KHOA — BACKLOG L2 (chủ dự án: "không chờ, giao L2 nữa, đào cho hết"):**

| # | Việc L2 | Bối cảnh đã biết | Trạng thái |
|---|---|---|---|
| 18 | **DPS runtime parity tàu 1** | damage × rate đã chốt mức công thức (đừng TTK/xếp tàu); parity = so model DPS với game chạy thật | TRỐNG |
| 19 | **CROSSCHECK ramus trên device thật ×2** | ① Map `&arr=256&depth=2` ② device 12↔10. Tool: `ramus-cli` (session start/install, tap, screenshot, wait; `ramus trial` / `RAMUS_API_KEY`); APK x86_64 nhận .apks universal | TRỐNG |
| 20 | **`allBasicAtk`/`allDeltaAtk` float[24] — tìm consumer thật** | mảng chưa có consumer trong tài liệu; đào code đến nơi nó được đọc | TRỐNG |
| 21 | **bind entry 576 — identity đầy đủ** | con số 576 đã xuất hiện nhiều vòng nhưng chưa có bảng identity từng entry | TRỐNG |
| 22 | **save schema end-to-end** | đã biết r.89: `GetPlayerDevices 14e628c` · `GetDevice 12546d0` (id@10 5000–5999, lv@14, rank@18) · `GetStatValue2 1250134` (row=listStatValues[trunc(id/1000)+4]) — cần reader/writer + flow save→load đầy đủ | TRỐNG |
| 23 | **wing special/named leaves + DPS parity 23 wing** | r95 đóng 5 pooled leaves chung; r95 KHÔNG phải giấy đóng 23 wing/DPS — wing đặc biệt/lá riêng còn mở (xem `wing_implementations.json`, `wing_emission_flow.json`, `wing_pooled_leaves.json`) | TRỐNG |

L2 claim tự do cho mọi digger (kể cả AI-3 nếu #4–8 đã có người, hoặc AI-1 sau batch 106). Gate chất lượng như L3: mọi số đếm được, artifact kèm SHA, model ≠ readback ≠ render, không screenshot gate.

**Miền cố định** (đổi phải chủ dự án): ef6b75ef binding/driver/texture-shader + combat/wings · a5a74747 particle/transition/driven · eeb95d5a geometry #4–8 · spec = đối chéo + docs + bảng + vehicle. Không merge/push main/tự ACK; 3 path shared ở nhánh spec.

