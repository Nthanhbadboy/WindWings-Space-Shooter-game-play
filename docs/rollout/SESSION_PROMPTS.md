# SESSION PROMPTS — prompt hiện hành cho từng session (tên theo mã nhánh, lần 137)

> **Quy ước đặt tên:** session = mã nhánh của nó (không dùng AI-1/2/3). Prompt dưới đây là **nội dung đăng lại được** cho từng session. Mỗi prompt có mục **ĐÓNG/MỞ** — cột tóm tắt ở cuối file. Board-delta mới nhất luôn thắng nếu mâu thuẫn.
> **Lần 138 — cơ chế TỰ NHẬN VAI:** session mới không định danh trước được (mã nhánh chỉ biết sau commit đầu) ⇒ mọi session khởi động bằng **PROMPT CHUNG** (`SESSION_COMMON_PROMPT.md`, dán từ user) → tự SELF-ID/CLAIM vai qua comment PR12 theo bảng [ROLE-BOARD]; khi báo XONG thì user đọc chat quyết ĐÓNG hay chạy tiếp.
> Kỷ luật chung (nhắc 1 dòng trong mọi prompt): CLAIM trước trên PR12 · nhánh riêng · nhãn bằng chứng 6 loại · KHÔNG SDK/publish/merge/close/force-push không lệnh · đọc text thẳng, không đăng `@/tmp/…` (glitch lặp ở `535b0541`).

---

## `20330d0e` — director / spec / tích hợp
> Điều phối end-to-end theo mandate; sổ DONE/DATA_SYNC/needle; board-delta PR12; tổng hợp kết quả session → Gate proposal; chỉ research/plan — không implement/SDK/publish.
> **ĐÓNG/MỞ:** giữ suốt vòng đời (đường dài).

## `535b0541` — decode static + registry ledger
> Hiện trạng: `daad5209f` — mục 32 đã đóng bằng store-census của 178 (chứng minh không tạo chu trình) ✓.
> **Việc giờ (lane cuối):** hoàn thành **registry-v4 final ledger** (điều kiện C2 của Gate-1): mỗi mục còn mở gắn đúng 1 loại {shipped-default · served · policy · missing-input · runtime-gated→USER} + next-step; số mở **không cần = 0**, cần NHẤT QUÁN. C1 (149-vs-169/177): resolve opportunistic nếu rẻ — **KHÔNG đào lane mới** (lệnh user 132/133). Xong → đăng HANDOFF registry-v4 (artifact + SHA + CI headSha) trên PR12.
> **ĐÓNG:** ngay sau registry-v4 publish + `8141386a` nâng verdict + Gate-1 khép. Việc runtime còn lại → USER.

## `ef6b75ef` — build/packaging spec + port verifier
> Hiện trạng: đang đào tầng 135 (apply-seed + channel-sampler — phục vụ gameplay port: random/pose). User biết và cho chạy.
> **Việc giờ:** ① kết thúc tầng 135 trong tối đa 1 vòng — xuất learning-note + artifact (đủ cho port dùng), sau đó **dừng hẳn đào** ② chuyển sang **Godot 4.x build/packaging spec**: export presets (Windows → MS Store MSIX; Android APK≤4GB / AAB≤150MB qua gradle), versioning, signing flow, target-API AppGallery/Amazon, port-plan = map scene/systems từ spec #29 + learning-note 135 ③ sau này làm **verifier độc lập** cho code của session Godot-coder (tách người viết/người kiểm). KHÔNG build/SDK/keystore thật; scaffold chỉ theo lệnh user.
> **ĐÓNG/CHUYỂN:** không đóng — chuyển vai verifier khi session Godot-coder mở.

## `a5a74747` — asset inventory + store-assets spec
> Hiện trạng: ĐÃ GIAO xong `1817a2516` — `docs/rollout/STORE_ASSETS_AND_LISTING_DRAFT.md` (+ HANDOFF `6442519089`) ✓ đã tích hợp về nhánh spec.
> **Việc giờ:** không còn lane bắt buộc — giữ trạng thái chờ; nhiệm vụ duy nhất còn lại: khi session art-designer mở → bàn giao capture-pack (manifest `19fcf9eb` 84 file · 42 contact sheets · sprites-index 2.197) làm brief.
> **ĐÓNG:** sau khi art-designer ACK nhận brief (dự kiến Gate-5).

## `8141386a` — reviewer độc lập
> Hiện trạng: `57aee0cc1` archival checkpoint; verdict **NOT_READY giữ đến registry-v4** ✓ đúng protocol.
> **Việc giờ:** chờ `535b0541` publish registry-v4 → re-review C1–C5; đủ điều kiện thì **nâng verdict** (chỉ reviewer nâng được — nguyên tắc 124) + so Gate-1 proposal trình user. Sau Gate-1: verify-lane cho Gate 2–7 (review spec store/Godot theo yêu cầu director).
> **ĐÓNG:** không — reviewer cần suốt vòng đời port.

## `46e50499` — commercial researcher
> Hiện trạng: vòng-2 verify store terms xong `de28a38a4` (đóng 6 mục treo) ✓.
> **Việc giờ — thứ tự ưu tiên:** ① **requirement sheets Gate-6**: rating questionnaire + data-safety/privacy form từng store (nguồn chính chủ + ngày, UNVERIFIED tại chỗ) ② **queue Godot**: ma trận plugin IAP/ads (Google Billing chính chủ × HMS IAP/Ads × Amazon IAP/Billing-Compatibility × AdMob-Poing) + analytics Godot trên Fire/HMS ③ **giá benchmark** remove-ads/premium genre → đề xuất bảng giá Gate-3 ④ eCPM rewarded Windows + trạng thái ads trên Fire 2026 ⑤ NPH-TQ để-sẵn (ưu tiên thấp). Nguyên tắc 135: *theo đúng luật từng store, không tranh cãi*.
> **ĐÓNG:** sau Gate-6 submission kits xong.

## `1b836828` — art planner
> Hiện trạng: v2 re-baseline `971a7eea8` — đo reuse trên 1,9k sprite, +346 h, +4 cột planner ✓.
> **Việc giờ:** ① thêm **W0-listing** vào planner: icon/feature-graphic/screenshot theo sizes trong `STORE_ASSETS_AND_LISTING_DRAFT.md` (đã ở nhánh spec) ② chuẩn hoá W1 (PLAYER 48 đơn vị) thành work-order có acceptance-per-unit — đầu vào cho session art-designer ③ KHÔNG vẽ.
> **ĐÓNG/MỞ:** giữ làm controller khối lượng/khớp tiến độ art suốt port (hoặc đóng sau khi W0+W1 work-orders được user duyệt — quyết tại Gate-5).

## `eeb95d5a` — RE probe (KHÔNG có hoạt động mới từ `ceebe881d`)
> **Việc giờ:** nếu còn hoạt động → đăng 1 HANDOFF cuối liệt kê mảnh đáng giữ (nếu không có gì thì ghi "trống") rồi DỪNG. Không nhận việc mới.
> **ĐÓNG: NGAY sau handoff đó** — lý do: lane đào-APK đã dừng theo lệnh user 132/133; mọi việc thuộc sở trường này không còn.

---

## Vai CHƯA CÓ NHÁNH (session mới tự CLAIM qua PROMPT CHUNG — `SESSION_COMMON_PROMPT.md`; mã nhánh chỉ biết sau commit đầu)

**Vai Godot-coder** — CLAIM khi user ra lệnh scaffold:
> Port WindWings lên Godot 4.x theo `docs/spec/` + `datas/` (nhánh `20330d0e` = bản vẽ; APK gốc = design reference). Scope: scenes/systems chơi được trước (player bay + bắn + 1 enemy wave theo GAMEPLAY spec) → rồi shop/pvp/economy theo spec → adapter IAP/ads 3 store theo D9a (Amazon IAP · HMS IAP/Ads · Windows commerce — "theo đúng luật từng store"). `ef6b75ef` là verifier — gửi code kèm cách kiểm. Không đụng protected paths; mỗi vòng 1 comment PR12 kèm bằng chứng chạy.

**Vai Art-designer** — ĐÃ CÓ CHỦ: `5438fec9` (W0 lô-1 chờ user duyệt) —
> hướng A: tối khí quyển **Ink & Ember** (theo planner). CHỜ DUYỆT mới chạy W1.

**Vai Art-designer-B** — TRỐNG, CLAIM NGAY (lần 141 — user mở thêm để A/B chọn sau):
> Hướng B: **sáng, arcade-pop, hành-động-dồn-dập** — đối chọi với A. Cùng đúng 25 slot, tên file +
> kích thước GIỐNG hệt `5438fec9` (đã verify nguồn chính chủ — lấy từ `art/w0-listing/W0_MANIFEST.md`
> nhánh A, cấm tự đổi), art khác hoàn toàn; directory riêng `art/w0-listing-b/` + `W0B_MANIFEST.md`
> (metadata như A, license "chờ user xác nhận quyền"). Làm ĐỘC LẬP phong cách với A — không trao đổi
> style, chỉ chung size/copy; nộp kèm 1 ảnh preview ghép toàn bộ slot để user so A/B. Xong STATUS: XONG
> chờ user chọn; vai tan sau khi user chọn A/B (người thua đóng, không làm W1).
> Sản xuất art theo `docs/art-plan/ART_REDRAW_PLAN.md` + `art-planner.csv` (nhánh `1b836828`) + sizes từ `STORE_ASSETS_AND_LISTING_DRAFT.md`. Thứ tự: W0-listing (icon/feature-graphic/screenshot 3 store) → W1 in-game (PLAYER 48 đơn vị). User duyệt từng lô; không tự đổi style gốc khi chưa có lệnh; không đụng `docs/spec/`/`datas/`/`tools/`.

## Tóm tắt ĐÓNG/MỞ (trả lời thẳng câu hỏi user)

| Session | MỞ/ĐÓNG | Khi nào |
|---|---|---|
| `eeb95d5a` | **ĐÓNG** | NGAY (sau 1 handoff cuối — hiện không có hoạt động) |
| `535b0541` | **ĐÓNG** | registry-v4 publish + Gate-1 khép |
| `a5a74747` | **ĐÓNG** | art-designer nhận brief (Gate-5) |
| `46e50499` | **ĐÓNG** | Gate-6 submission kits xong |
| `1b836828` | Đóng hoặc giữ | quyết tại Gate-5 (giữ = controller khối lượng art) |
| Godot-coder (nhánh mới) | **MỞ** | lệnh scaffold của user |
| Art-designer (nhánh mới) | **MỞ** | Gate-5 cần art thật / user muốn sớm |
| `20330d0e` · `ef6b75ef` · `8141386a` | giữ | suốt vòng đời |
