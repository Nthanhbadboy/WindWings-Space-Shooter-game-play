## 🧭 BẢNG ĐIỀU PHỐI TỰ ĐỘNG — comment này được nhánh spec SỬA TẠI CHỖ mỗi vòng, luôn đọc bản ở đây là mới nhất (cập nhật lần 54)

**Cách tự nhận việc:** chọn mục TRỐNG → `CLAIM [<nhánh>] <mục> — artifact: <file>` TRƯỚC KHI làm → first-claim wins → đã CLAIM/DONE không đụng (trừ khi khai `REPLICATION`) → HANDOFF xong spec cập nhật → va chạm số = `DISPUTED`. ⚠️ Sync needle (APKD1+AI1) cùng commit. CI 403 → nhờ vehicle (PR #14 cho `a5a74747`; nhánh khác xin riêng).

**TRẠNG THÁI NHÁNH (lần 54):**
- `[arena/ef6b75ef]` (AI-1) ✅ 105 · ✅ **106 (#3 DONE — PixelSnap + bilinear thật; spec arithmetic review 9/9 PASS; CI 40292776800)** · #2 custom23 vẫn MỞ. Sẵn sàng nhận batch mới.
- `[arena/a5a74747]` (AI-2) ✅ 105/106/107 · ✅ **108 (#15 PARTIAL: (a) multi-layer NOT_EXERCISED ĐÓNG cho snapshot — phủ kép 308/308+232/232; (b) native interpolation MỞ — cần native bytes/on-device probe)** · CI xanh tự lấy. Sẵn sàng nhận batch mới.
- `[arena/eeb95d5a]` (AI-3) 🔄 tip `ceebe881d` — đang chuẩn bị batch đầu (chưa CLAIM; nhắc: CLAIM #4–8 trước khi đào).
- `[spec / arena/20330d0e]` đối chéo + docs + bảng + vehicle (tip lần 54; datas = 73).

**BACKLOG L3:**

| # | Việc | Miền gợi ý | Trạng thái |
|---|---|---|---|
| 1 | Driver order concrete chain | AI-1 | ✅ DONE — 105 |
| 2 | Custom binding tag23 — native mapping proof | AI-1 | 🔄 MỞ |
| 3 | Texture/UV/shader (mip0 bilinear + PixelSnap) | AI-1 | ✅ DONE — 106 |
| 4 | TMP/procedural geometry | AI-3 | TRỐNG |
| 5 | Sliced/tiled non-zero-border generator (root 5739) | AI-3 | TRỐNG |
| 6 | Live SpriteAtlas remap + skinning bounds | AI-3 | TRỐNG |
| 7 | 7 builtin ParticleSystemRenderer mesh refs | AI-3 | TRỐNG |
| 8 | 5 header-only MB + 52 default-mesh refs | AI-3 | TRỐNG |
| 9 | Particle simulation model (954) | AI-2 | ✅ DONE — 105 |
| 10 | Transition scheduler | AI-2 | ✅ DONE — 105 |
| 11 | Driven RectTransform/CanvasRenderer | AI-2 | ✅ DONE — 105 |
| 12 | Composition viewport + engine transition (L3 cuối — tách nhỏ) | bất kỳ | TRỐNG |
| 14 | Reachability & driven-coverage | AI-2 | ✅ DONE — 106-a5a74747 |
| 15 | (a) multi-layer coverage NOT_EXERCISED ✅ ĐÓNG · (b) native interpolation | — | 🔄 MỞ (tầng b) — cần native bytes/on-device probe |
| 16 | Replication transition | AI-2 | ✅ DONE — 107 |
| 17 | Independent raw/APK decoder transition graph | AI-1 phù hợp | TRỐNG |

**BACKLOG L2 (đã MỞ — claim tự do, first-claim wins):**

| # | Việc L2 | Bối cảnh | Trạng thái |
|---|---|---|---|
| 18 | DPS runtime parity tàu 1 | damage×rate chốt mức công thức (không TTK/xếp tàu) | TRỐNG |
| 19 | CROSSCHECK ramus device ×2 (Map &arr=256&depth=2 · device 12↔10) | ramus-cli; APK x86_64 .apks | TRỐNG |
| 20 | allBasicAtk/allDeltaAtk float[24] — consumer thật | đào tới nơi đọc | TRỐNG |
| 21 | bind entry 576 — identity từng entry | số đã lặp, chưa có bảng | TRỐNG |
| 22 | save schema end-to-end | r.89 RVA có sẵn | TRỐNG |
| 23 | wing special/named leaves + DPS parity 23 wing | r95 chỉ đóng 5 pooled chung; wing bắn vẫn ĐÓNG r92 | TRỐNG |

**Miền cố định** (đổi phải chủ dự án): ef6b75ef binding/texture-shader + combat/wings · a5a74747 particle/transition/driven · eeb95d5a geometry #4–8 · spec = đối chéo + docs + bảng + vehicle. Không merge/push main/tự ACK; 3 path shared ở nhánh spec.

