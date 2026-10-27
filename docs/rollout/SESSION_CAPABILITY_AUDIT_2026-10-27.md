# SESSION CAPABILITY AUDIT — tái phân việc theo sở trường (2026-10-27; cập nhật lần 137 sau vòng chạy 1)
> **Prompt hiện hành từng session:** xem `SESSION_PROMPTS.md` (cùng thư mục) — tên theo mã nhánh, kèm lịch ĐÓNG/MỞ rõ từng session.

> **Lệnh user:** *"để ý năng lực AI mà giao việc; giả sử thiết kế hình ảnh hay code mà không sở trường thì giao việc khác hoặc đóng session mở session."*
> Phương pháp: đánh giá theo **bằng chứng đã làm được** (report PR12 + commit trên nhánh từng session), không đánh giá theo ý muốn. Mỗi verdict kèm trigger.

## 1. Danh mục session thực tế trên remote (`git ls-remote`, 27/10/2026)

| Session | Nhánh | Tip | Trạng thái |
|---|---|---|---|
| **director/spec** | `20330d0e` | `6621c0fca` | giữ — suốt vòng đời |
| **`535b0541`** decode+registry | `535b0541` | `daad5209f` — vòng 1: mục 32 đóng (178/179) | registry-v4 = lane cuối → **ĐÓNG** sau đó |
| **`ef6b75ef`** spec+verifier | `ef6b75ef` | `58cf84cc5` — vòng 1: tầng 135 apply-seed (user cho chạy, kết thúc ≤1 vòng) | giữ → chuyển verifier khi Godot-coder mở |
| **`a5a74747`** asset spec | `a5a74747` | `1817a2516` — **GIAO XONG** store-assets draft (đã tích hợp về nhánh spec) | chờ → **ĐÓNG** khi art-designer nhận brief |
| **`8141386a`** reviewer | `8141386a` | `57aee0cc1` — archival; NOT_READY giữ đúng protocol | giữ suốt vòng đời |
| **`46e50499`** researcher | `46e50499` | `de28a38a4` — vòng-2 verify terms, đóng 6 mục treo | → **ĐÓNG** sau Gate-6 |
| **`eeb95d5a`** RE probe | `eeb95d5a` | `ceebe881d` — vòng 1: KHÔNG hoạt động mới | **ĐÓNG NGAY** (sau 1 handoff cuối) |
| **`1b836828`** art planner | `1b836828` | `971a7eea8` — vòng 1: v2 re-baseline +346 h reuse +4 cột | giữ (controller khối lượng art) |

## 2. Ma trận năng lực (bằng chứng, không đoán)

| Session | Đã CHỨNG MINH mạnh (bằng chứng cụ thể) | Chưa chứng minh / không sở trường | Verdict |
|---|---|---|---|
| **SS 0** | điều phối 12+ vòng không lỗi quy trình; sổ DONE/DATA_SYNC 209-claim; verify-trước-push; tổng hợp D1–D12 + disposition Gate-1 | vẽ art; viết game-code thực | **GIỮ — director + integration** |
| **AI-4 (535)** | decode tĩnh byte-chính xác (shop 162/164/165/160 · pvp 169 · medal 155 · season 152) + registry 56 mục + tự sửa false-positive (172) | research thị trường; vẽ art; runtime | **GIỮ tới registry-v4 xong → ĐÓNG** (lane hết; items còn lại runtime-gated = user) |
| **ef** | disassembly FDE sâu (119→134), verifier tooling, erratum minh bạch, handoff pin đủ | viết GDScript game-code (chưa từng); vẽ art | **GIỮ — build/packaging spec + VERIFIER của port** (tách writer/verifier theo kỷ luật bằng chứng của dự án) |
| **a5** | capture runtime 84-file, sprites-index 2.197, contact sheets 42, worklist 624, correction 166 | vẽ art mới; code | **GIỮ — asset inventory + store-assets spec** (không giao vẽ) |
| **AI-3** | adversarial review Gate-1 → NOT_READY + 5 conditions có bằng chứng | — (review là sở trường, dự án cần suốt port) | **GIỮ — reviewer Gate-1 + sau này review port** |
| **Session E** | 73 nguồn có ngày, UNVERIFIED tại chỗ, 3-col store comparison, D1–D12 | code; art | **GIỮ tới Gate-6 (submission kits) xong → ĐÓNG** |
| **AI-2 (`eeb95d5a`)** | RE probe/analysis reports (tree sync từ ef+2033) | — | **ĐÓNG SAU 1 COMMENT HANDOFF** — lane đào-APK đã dừng theo lệnh user (lần 132/133); không còn việc thuộc sở trường này. Yêu cầu: đăng 1 HANDOFF cuối liệt kê những mảnh đáng giữ (nếu có), rồi user đóng session |
| **Session F (`1b836828`)** | art planning định lượng: 2.185 records → **788 đơn vị vẽ thật**, L2=149h/L3≈1.264h/full-parity≈3.916h, planner 651 dòng 28 cột, đọc đúng spec+worklist của a5 (đã khớp số, không trùng việc) | **tạo hình ảnh thật chưa chứng minh** (plan-only) | **GIỮ — art PLANNER**; production art → Session H (mới) |

## 3. Sửa phân việc theo sở trường (thay đổi so với plan lần 134)

1. **ef KHÔNG viết game-code.** Build/packaging spec + port-plan là phân tích (sở trường ✓) — giữ. Khi user ra lệnh scaffold: **mở Session G (Godot Port Coder)** viết code, ef làm verifier độc lập.
2. **a5 + F không vẽ art.** Cả hai đều planner/inventory (sở trường ✓). Khi đến Gate-5 cần art thật (icon/banner/screenshot theo sizes của a5, theo plan 788-đơn-vị của F): **mở Session H (Store Art Designer)**.
3. **AI-2 đóng** — việc duy nhất hợp sở trường của nó (đào APK) đã dừng.
4. **535 + E có mốc đóng rõ** — không kéo dài session không còn việc.
5. F và a5 đã tự khớp số (F đọc worklist 624 của a5 → tách 788 đơn vị) — **không giao việc trùng**; a5 giữ store-assets spec (listing sizes), F giữ redraw plan.

## 4. Prompt mở session mới (soạn sẵn — user dán khi đến trigger)

**Session G — Godot Port Coder** *(mở khi user ra lệnh scaffold)*:
> Mục tiêu: port WindWings lên Godot 4.x theo spec của nhánh `arena/20330d0e` (`docs/spec/` + `datas/` là bản vẽ; APK gốc = design reference). Scope code: scenes/systems (player, enemy, wave, shop, pvp, economy theo ECONOMY spec) + adapter IAP/ads 3 store theo D9a (Amazon IAP · HMS IAP/Ads · Windows commerce — "theo đúng luật từng store, không tranh cãi"). Kỷ luật: CLAIM đầu tiên trên PR12; nhánh riêng `arena/<mã>-…`; mỗi vòng 1 comment PR12 kèm bằng chứng (screenshot chạy, file + SHA); nhãn bằng chứng 6 loại; KHÔNG SDK/publish/merge không lệnh; keystore do user giữ; spec/tool/datas là protected paths — đọc được, sửa không. Cắm động cơ chơi được (player bay + bắn + 1 enemy wave) trước, IAP/ads sau.

**Session H — Store Art Designer** *(mở khi Gate-5 cần art thật)*:
> Mục tiêu: sản xuất art theo plan có sẵn — brief = `docs/art-plan/ART_REDRAW_PLAN.md` + `art-planner.csv` (651 dòng, nhánh `arena/1b836828`) + sizes listing 3 store do a5 spec. Bắt đầu từ listing art (icon/feature-graphic/screenshot MS · Fire · AppGallery) rồi W1 in-game (PLAYER 48 đơn vị). Kỷ luật: KHÔNG đụng `docs/spec/`/`datas/`/`tools/`; mỗi asset đăng kèm file; user duyệt từng lô; không tự thay style gốc khi chưa có lệnh.

## 5. Tóm tắt lifecycle

| Hành động | Đối tượng | Trigger |
|---|---|---|
| Đóng (sau handoff cuối) | **AI-2 `eeb95d5a`** | NGAY |
| Đóng | **535** | registry-v4 publish + Gate-1 khép |
| Đóng | **Session E** | Gate-6 submission kits xong |
| Mở | **Session G** (Godot coder) | user ra lệnh scaffold |
| Mở | **Session H** (art designer) | Gate-5 cần art thật (hoặc sớm hơn nếu user muốn triển khai listing sớm) |
| Giữ nguyên | SS 0 · ef · a5 · AI-3 · F | — |
