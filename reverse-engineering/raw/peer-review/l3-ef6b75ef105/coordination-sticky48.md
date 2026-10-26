## 🧭 BẢNG ĐIỀU PHỐI TỰ ĐỘNG — comment này được nhánh spec SỬA TẠI CHỖ mỗi vòng, luôn đọc bản ở đây là mới nhất

**Cách tự nhận việc (không cần đợi phân việc):**
1. Chọn 1 mục **TRỐNG** trong BACKLOG dưới đây (hoặc đề xuất mục mới bằng comment riêng).
2. Post comment: `CLAIM [<tên-nhánh-của-bạn>] <mục> — artifact dự kiến: <file>` **TRƯỚC KHI bắt đầu**.
3. Mục đã CLAIM bởi nhánh khác → **KHÔNG làm**; muốn làm cùng việc thì phải khai `REPLICATION` rõ trong report (đào trùng độc lập có giá trị, giấu là bị trả lại).
4. Xong → HANDOFF như thường lệ (nhánh + code SHA + CI + test count + điểm nhờ review). Spec cập nhật bảng.
5. **First-claim wins** (xét theo thời điểm comment). Va chạm số liệu → spec flag `DISPUTED`, phân xử bởi chủ dự án hoặc digger thứ 3.

**TRẠNG THÁI HIỆN TẠO (lần 48 — từ tip + comment, ghi rõ mức tin):**
- `[AI-1 / arena/ef6b75ef]` **ĐANG LÀM** (suy từ tip `1db187112`, chưa handoff): batch textured105 — texture decode + GPU shader programs (platform 5 GLES) · SpriteRenderer setter bridge cho customType23 (đang điều tra) · Pause Align literal. 
- `[AI-2]` chưa thấy nhánh trên remote — chờ claim từ BACKLOG.
- `[AI-3]` chưa thấy nhánh trên remote — chờ claim từ BACKLOG.
- `[spec / arena/20330d0e]` đối chéo + docs + giữ bảng này (tip `0d08a8561`).

**BACKLOG — mục TRỐNG là tự claim được; mục ĐANG LÀM là đang có người giữ:**

| # | Việc | Miền gợi ý | Trạng thái |
|---|---|---|---|
| 1 | Driver order trên concrete chain MỚI (≠ Alert/Border_Info) | AI-1 | TRỐNG |
| 2 | Custom binding customType23/type212 — native mapping proof | AI-1 | 🔄 AI-1 |
| 3 | Texture decode + UV join + shader Sprites/Default execution model | AI-1 | 🔄 AI-1 |
| 4 | TMP/procedural geometry: 7 fonts/2.354 chars/glyph bounds + static fallback 1.737 texts | AI-2 | TRỐNG |
| 5 | Sliced/tiled non-zero-border generator (vd root 5739 — hết not_generated) | AI-2 | TRỐNG |
| 6 | Live SpriteAtlas remap + skinning bounds (bounded) | AI-2 | TRỐNG |
| 7 | 7 builtin ParticleSystemRenderer mesh refs — resolve hoặc chứng minh không thể | AI-2 | TRỐNG |
| 8 | 5 header-only MB + 52 default-mesh refs — mỗi nhóm một kết luận | AI-2 | TRỐNG |
| 9 | Particle simulation model (954 modules, headless, state theo t) | AI-3 | TRỐNG |
| 10 | Transition scheduler + layer blending (232 controllers/343+125 transitions) | AI-3 | TRỐNG |
| 11 | Driven RectTransform/CanvasRenderer trên modeled state kiểu r104 | AI-3 | TRỐNG |
| 12 | Composition viewport + engine transition (mảnh L3 cuối — lớn, nên tách nhỏ khi claim) | AI-1→AI-3 | TRỐNG |
| 13 | L2 còn 6 mục (DPS runtime · CROSSCHECK ramus ×2 · float[24] consumer · bind 576 · save schema · wing leaves) | bất kỳ | ⛔ chờ chủ dự án bật L2 — chưa claim được |

**Miền cố định giữ nguyên** (đổi phải chủ dự án): AI-1 binding/driver/texture-shader · AI-2 geometry/gap · AI-3 particle/transition/driven · spec = đối chéo + docs + bảng này (không đào). Ràng buộc chung: source APK là authority · mọi số đếm được · model ≠ readback ≠ render · 3 path shared giữ ở nhánh spec · không merge/push main/tự ACK · artifact kèm SHA.

