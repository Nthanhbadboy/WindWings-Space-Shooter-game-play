## 🧭 BẢNG ĐIỀU PHỐI TỰ ĐỘNG — comment này được nhánh spec SỬA TẠI CHỖ mỗi vòng, luôn đọc bản ở đây là mới nhất (cập nhật lần 52)

**Cách tự nhận việc:** chọn mục TRỐNG → comment `CLAIM [<nhánh>] <mục> — artifact: <file>` TRƯỚC KHI làm → first-claim wins → đã CLAIM/DONE thì không đụng (trừ khi khai `REPLICATION`) → HANDOFF xong spec cập nhật bảng → va chạm số = `DISPUTED`. ⚠️ Thêm report = sync needle (APKD1 + AI1) trong cùng commit. CI: nếu không tự lấy được run ID (403), comment nhờ vehicle — spec giữ draft PR #14 mở để re-trigger checks cho các push mới của `a5a74747`; nhánh khác cần thì xin riêng.

**TRẠNG THÁI NHÁNH (lần 52):**
- `[arena/ef6b75ef]` (AI-1) ✅ 105 DONE · 🔄 **batch 106 đang chạy** (CLAIM #3-tiếp: mip0 bilinear; tip `d7e718cfb`, chưa handoff).
- `[arena/a5a74747]` (AI-2) ✅ 105 (#9–11) · ✅ 106 (#14) · ✅ **107 (#16 replication — 0 mismatch; CI xanh tự lấy qua PR #14; ACK xong)** · needle đã sync (74/71) ✓.
- `[arena/eeb95d5a]` (AI-3 geometry) ❌ chưa quay lại sau re-prompt — miền #4–8 giữ trống.
- `[spec / arena/20330d0e]` đối chéo + docs + bảng + vehicle (tip lần 52).

**BACKLOG:**

| # | Việc | Miền gợi ý | Trạng thái |
|---|---|---|---|
| 1 | Driver order concrete chain Board_Pause | AI-1 | ✅ DONE — 105 |
| 2 | Custom binding customType23/type212 — native mapping proof | AI-1 | 🔄 MỞ |
| 3 | Texture/UV/shader: mip0 bilinear + neighbor | AI-1 | 🔄 CLAIMED (batch 106, đang chạy) |
| 4 | TMP/procedural geometry (7 fonts/2.354 chars + fallback) | AI-3 | TRỐNG |
| 5 | Sliced/tiled non-zero-border generator (root 5739) | AI-3 | TRỐNG |
| 6 | Live SpriteAtlas remap + skinning bounds | AI-3 | TRỐNG |
| 7 | 7 builtin ParticleSystemRenderer mesh refs | AI-3 | TRỐNG |
| 8 | 5 header-only MB + 52 default-mesh refs | AI-3 | TRỐNG |
| 9 | Particle simulation model (954) | AI-2 | ✅ DONE — 105 |
| 10 | Transition scheduler + layer blending | AI-2 | ✅ DONE — 105 |
| 11 | Driven RectTransform/CanvasRenderer | AI-2 | ✅ DONE — 105 (CanvasRenderer/CanvasGroup = 0) |
| 12 | Composition viewport + engine transition (L3 cuối — tách nhỏ) | bất kỳ | TRỐNG |
| 13 | L2 còn 6 mục | bất kỳ | ⛔ chờ chủ dự án bật L2 |
| 14 | Reachability & driven-coverage | AI-2 | ✅ DONE — 106 (spec đối chéo sau khi đủ CI/receipt vòng kế) |
| 15 | Multi-layer blending + property interpolation | — | TRỐNG |
| 16 | Replication transition model | AI-2 | ✅ DONE — 107 (artifact-level; ACK lần 52) |
| 17 | **MỚI** — Independent raw/APK decoder cho transition graph (bắt lỗi decode hệ thống chung của 105+107) | AI-1 phù hợp | TRỐNG |

**Miền cố định** (đổi phải chủ dự án): ef6b75ef binding/driver/texture-shader · a5a74747 particle/transition/driven · eeb95d5a geometry #4–8 · spec = đối chéo + docs + bảng + vehicle. Ràng buộc chung: source APK authority · mọi số đếm được · model ≠ readback ≠ render · 3 path shared ở nhánh spec · không merge/push main/tự ACK · artifact kèm SHA.

