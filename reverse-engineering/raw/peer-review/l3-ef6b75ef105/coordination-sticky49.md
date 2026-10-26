## 🧭 BẢNG ĐIỀU PHỐI TỰ ĐỘNG — comment này được nhánh spec SỬA TẠI CHỖ mỗi vòng, luôn đọc bản ở đây là mới nhất (cập nhật lần 49)

**Cách tự nhận việc (không cần đợi phân việc):**
1. Chọn 1 mục **TRỐNG** trong BACKLOG dưới đây (hoặc đề xuất mục mới bằng comment riêng).
2. Post comment: `CLAIM [<tên-nhánh-của-bạn>] <mục> — artifact dự kiến: <file>` **TRƯỚC KHI bắt đầu**.
3. Mục đã CLAIM/DONE bởi nhánh khác → **KHÔNG làm**; muốn làm cùng việc thì khai `REPLICATION` rõ trong report.
4. Xong → HANDOFF như thường lệ (nhánh + code SHA + CI run ID + test count + điểm nhờ review). Spec cập nhật bảng.
5. **First-claim wins**. Va chạm số liệu → spec flag `DISPUTED`.

**TRẠNG THÁI NHÁNH (lần 49):**
- `[arena/ef6b75ef]` (AI-1) **ĐANG CHẠY batch 105-ef6b75ef** — đã CLAIM #1 (Board_Pause driver order: collider→content Transform→parentView→renderer549984, Native Align trên cùng Frame) + giữ #2 #3. Local 1103 PASS; chờ handoff code/CI.
- `[arena/a5a74747]` (AI-2) ✅ **HANDOFF 105-a5a74747 xong** — DONE #9 #10 #11 (particle model · transition scheduler · driven props). SHA 3/3 khớp, spec đã đối chéo. ⚠️ **CHƯA CÓ CI RUN ID** — nhánh mới không trigger `docs-verify`, dispatch bị 403; chờ owner dispatch (hoặc duyệt draft PR để lấy run).
- `[spec / arena/20330d0e]` đối chéo + docs + bảng này (tip `7bdd50032`→đang commit lần 49).

**BACKLOG:**

| # | Việc | Miền gợi ý | Trạng thái |
|---|---|---|---|
| 1 | Driver order concrete chain Board_Pause | AI-1 | 🔄 CLAIMED ef6b75ef |
| 2 | Custom binding customType23/type212 — native mapping proof | AI-1 | 🔄 AI-1 đang điều tra |
| 3 | Texture decode + UV join + shader Sprites/Default model | AI-1 | 🔄 AI-1 (textured105) |
| 4 | TMP/procedural geometry: 7 fonts/2.354 chars/glyph bounds + fallback 1.737 texts | AI-2 | TRỐNG |
| 5 | Sliced/tiled non-zero-border generator (vd root 5739) | AI-2 | TRỐNG |
| 6 | Live SpriteAtlas remap + skinning bounds (bounded) | AI-2 | TRỐNG |
| 7 | 7 builtin ParticleSystemRenderer mesh refs — resolve hoặc chứng minh không thể | AI-2 | TRỐNG |
| 8 | 5 header-only MB + 52 default-mesh refs — kết luận từng nhóm | AI-2 | TRỐNG |
| 9 | Particle simulation model (954 modules) | AI-2 | ✅ DONE — 105-a5a74747 |
| 10 | Transition scheduler + layer blending (232 controllers) | AI-2 | ✅ DONE — 105-a5a74747 |
| 11 | Driven RectTransform/CanvasRenderer kiểu r104 | AI-2 | ✅ DONE — 105-a5a74747 (CanvasRenderer/CanvasGroup = 0 binding, kết luận âm) |
| 12 | Composition viewport + engine transition (mảnh L3 cuối — lớn, tách nhỏ khi claim) | bất kỳ | TRỐNG |
| 13 | L2 còn 6 mục | bất kỳ | ⛔ chờ chủ dự án bật L2 |

**Việc mới từ kết quả 105-a5a74747 (claim tự do):**
| # | Việc | Trạng thái |
|---|---|---|
| 14 | Particle sim depth: keyframe/gradient/burst-table decode rồi mô phỏng over-lifetime (hiện alpha=1.0+cờ) | TRỐNG |
| 15 | Multi-layer blending + property interpolation khi có bằng chứng native Animator (>1 layer/controller) | TRỐNG |
| 16 | Independent replication transition model (hiện 1 nguồn — digger khác đào trùng để chéo kiểm) | TRỐNG |

**Miền cố định giữ nguyên** (đổi phải chủ dự án): ef6b75ef binding/driver/texture-shader · a5a74747 particle/transition/driven · digger geometry (khi vào) miền #4–8 · spec = đối chéo + docs + bảng. Ràng buộc chung: source APK authority · mọi số đếm được · model ≠ readback ≠ render · 3 path shared ở nhánh spec · không merge/push main/tự ACK · artifact kèm SHA.

