# Tổng kiểm analysis + SPEC — tồn đọng, thiếu sót và mức đủ của báo cáo

**Ngày kiểm:** 2026-10-27 (Asia/Saigon).  
**Snapshot trong repo:** branch `arena/a5a74747-windwings-space-shooter-game-p`, trước báo cáo này `HEAD=0376abe932e2d4b09b05efab4f74edd913656562`.  
**Snapshot kiểm toán ban đầu:** paginated PR12 đến claim `6426579737`; lúc đó ACK mới nhất là vòng 113 (`6426353854`).
**Status refresh:** đã đối chiếu ACK114 (`6426867942`), D5-residual claim `6426986645`, và user-lead claim `6427556449` / report 165; xem §5–§6 bên dưới.
**Kết luận nhanh:** có thể viết báo cáo trạng thái trung thực; **chưa thể kết luận analysis/SPEC đã khép toàn bộ**. Các kết quả H1–H3 và D5 đều là kết quả bounded, không phải đóng các câu hỏi rộng hơn. Các trạng thái giữa central spec và snapshot trong working branch phải được phân biệt.

## 1. Phạm vi và giới hạn kiểm toán

Đối chiếu các report/receipt hiện có với `docs/spec/OPEN_ISSUES.md`, `MISSING_FOR_NEW_GAME.md`, `START_HERE.md`, `DATA_SYNC.md`, `README.md`, các spec animation liên quan và trạng thái task được comment trên PR12. Đã chạy lại các kiểm tra cục bộ ghi ở §6.

Đây là **kiểm toán tài liệu và trạng thái**, không phải phân tích lại binary hoặc kiểm tra độc lập các lane khác. Không đọc native/FDE artifacts, không chạy runtime/emulator/probe, không dùng secret, và không lấy bằng chứng từ route khác để lấp gap. Với task khác nhánh, trạng thái dưới đây chỉ phản ánh handoff/progress comment được trích, không phải review độc lập nội dung kỹ thuật.

## 2. Kết luận điều hành

1. **D5 report 163 đủ cho phần kết quả static-array join đã làm; không đủ để tuyên bố D5 hoàn tất.** Có 24/24 `Player_Attack_N → N−1` joins tới bốn mảng tĩnh. Component/GameObject/projectile owner và extra-life serialized rewiring vẫn `NOT_BOUND`. ACK vòng 113 gọi rõ kết quả này là **ĐÓNG-HALF**, và residual vẫn bounded.
2. **H1/A2, H2/B6-half, H3/C7 cũng chỉ đóng bó scope**: bảng map có thứ tự nội bộ nhưng không có named scene/stage/runtime parity; census BodyPhysics không bind semantics hoặc 19 Director classes; 45 root identity không cho asset role/use. Giữ các `NOT_BOUND`/bounded-missing.
3. **Tại snapshot kiểm toán ban đầu, local spec chưa đồng bộ các handoff mới.** ACK114 sau đó formal-close H4/121 và nói central spec đã áp dụng 7 sửa đổi, gồm OPEN_ISSUES counts, B3, MISSING_FOR_NEW_GAME, Arena/PvP, README và G1 locator. Các mâu thuẫn §4 còn tồn tại trong working copy này cho đến khi mirror patch; không gọi chúng là lỗi central spec sau ACK114.
4. **Có thể viết báo cáo trạng thái có điều kiện, không thể viết “đã hoàn tất toàn bộ analysis/spec”.** Các hạng mục thiết kế, asset-role, binding, runtime-gated, hoặc source-locator đang mở cần giữ nguyên trạng thái thay vì nâng mức bằng suy luận.

## 3. Bảng trạng thái analysis — việc đã làm và giới hạn còn lại

| Hạng mục | Evidence hiện có | Còn thiếu / không được kết luận |
|---|---|---|
| **H1 / A2** — report 160 | Trích 250 mảng `listMapDatas`; 3 entry đối chiếu khớp | Internal index chưa là campaign/stage/scene identity. Không có runtime readback/parity. |
| **H2 / B6-half** — report 161 | Census 251 `Boss_BodyPhysics`, distributions và serialized joins | Semantics field và gán vào 19 Director classes `NOT_BOUND`; không dùng census để khẳng định damage runtime. |
| **H3 / C7** — report 162 | 45 root `900xx` identities có metadata; 0/45 trùng roster `waves.json` trong snapshot đã pin | Asset role, component/art identity và use ngoài roster `NOT_ASSIGNED`/bounded-missing. |
| **D5** — report 163 | 24/24 class suffixes nối vào bốn captured static arrays theo quy tắc report 82 | Không có serialized owner cho `Player_Attack_N`; một hàng `GP_Datas` không bind extra-life fields. Extra-life rewiring/projectile owner `NOT_BOUND`; không đo DPS/runtime. |
| **Boss-39001/39002 callback** | Spec hiện giữ hai route riêng. Static slot identity `0x2ADFB48 = "Stop"` được nêu theo provenance AI-1 riêng. | Không suy marker occurrence, callback invocation/delivery, defeat/burst, playback hoặc runtime effect. Không nhập bằng chứng giữa hai prefab. |

**D5 được viết đủ cho phần bounded result**, nhưng chưa phải lời giải cho producer→serialized instance join. Không có export mới trong snapshot này để chốt phần đó. Nếu không có nguồn serialize mới được phép, đúng kết luận là giữ residual bounded/`NOT_BOUND`, không tiếp tục chạy lại những bước đã làm hoặc nâng claim.

## 4. Những tồn đọng và thiếu sót cần xử lý trong analysis/SPEC

**Phân biệt branch snapshot với central spec:** các mục dưới đây được phát hiện trong working copy trước ACK114. ACK114 sau đó ghi central spec đã áp dụng 7 P1/P2 sửa đổi; vì vậy, chúng vẫn là lỗi/độ lệch của bản local này cho đến khi có patch sync, không phải lỗi còn mở ở central spec.

### P1 — Mâu thuẫn nội bộ trong bảng vấn đề

1. **`OPEN_ISSUES.md` tổng đếm không khớp bảng:** phần đầu ghi “28 vấn đề” và “11 mục đóng / 28”. Các ID hiện liệt kê là A1–A4 (4), B1–B8 (8), C1–C8 (8), D1–D5 (5), E1–E4 (4) — tổng **29 ID**. Đếm cú pháp các hàng có `~~` hoặc `✅` cho **15 hàng**, nhưng B3 vừa có dấu hoàn tất vừa còn một mệnh đề bind chưa dứt. Đây không phải số “đóng” có thể công bố ngay: cần thống nhất đơn vị và quy tắc trạng thái, rồi tính lại summary.
2. **B3 trong `OPEN_ISSUES.md` còn ghi `StartHpPoint ← dict + kHp[mode]` là việc phải bind.** `MISSING_FOR_NEW_GAME.md` §2 và `DIFFICULTY_MODES.md` §3–5 nói `kHp[mode]` không tồn tại như hệ số, HP theo ID đã bind; vì vậy câu ở bảng B3 đang mâu thuẫn với các phần đã cập nhật. Cần sửa câu tồn đọng để không hồi sinh giả thuyết đã rút.
3. **Binding tàu bị mô tả hai cách trong `MISSING_FOR_NEW_GAME.md`:** bảng §1 vẫn nói damage/rate/cost còn thiếu index→ID tàu; phần §2 lại ghi save/load và combat đã bind theo các luật riêng (combat `Player_Attack_N → N−1`). Hãy nêu đúng phạm vi và không gộp save ID với combat index.
4. **Arena/PvP trong `MISSING_FOR_NEW_GAME.md` lệch ở working copy này:** hàng §1 còn ghi “0 report/batch” và chưa dịch class nào. ACK114 xác nhận central spec đã cập nhật theo AI-4 149–152; các số report đó trùng số report #27-GS ở repo này nên không đồng nhất file giữa lanes. Mirror patch vào working copy khi đồng bộ; giữ đúng bounded scope, không biến các slice thành luật Arena/PvP đầy đủ.

### P1 — Đồng bộ spec và provenance

1. `START_HERE.md` vẫn gọi report 152 là **Partial sync** với route/key wording cần reconcile. Các đoạn hiện tại của `ANIMATION_SCRIPT.md` đã phân biệt Boss-39001/39002, nêu riêng provenance `Stop` và giữ delivery unresolved; tuy vậy report 152 vẫn là review lịch sử, còn H4/report 121 chưa có formal handoff/central ACK ở snapshot này. Sau khi H4 hoàn tất, cần cập nhật index/status thay vì để “Partial sync” không rõ là hiện trạng hay lịch sử.
2. H4/report 121 progress (`6426567410`) từng nói formal handoff đang chờ CI; ACK114 (`6426867942`) sau đó **formal-close** H4 và xác nhận locator G1 đã sửa đủ bốn chỗ trên central spec (`153/G1` → HANDOFF `6422888569`, DATA_SYNC §24.88, reports 109/122; report 153 giữ riêng G2). Working copy này vẫn cần được mirror để tránh giữ citation cũ.
3. Cần sửa phần opening summary của `ANIMATION_SCRIPT.md` cho thật rõ: **slot identity `Stop` đã được xác định riêng; điều chưa biết là marker occurrence/delivery/callback/runtime effect**. Phần thân hiện giải thích ranh giới này, nhưng câu tóm tắt “chưa có binding tới callback key cụ thể” dễ bị đọc thành phủ định cả static literal identity.
4. Không lấy dòng “report 152 Partial sync” hoặc kết quả H4 progress làm bằng chứng mới về game. Đây là trạng thái đồng bộ tài liệu, không mở rộng source evidence.

### P2 — Open issues là lẫn lộn giữa missing evidence và lựa chọn thiết kế

`OPEN_ISSUES.md` còn các mục cần xử lý hoặc phân loại rõ hơn: B1 device stat values; B4 stage enemy counts; B5 43/305 trace chưa đối chiếu; B6/C8 semantics và 19-class assignment; C5 `Call_Data.number/editType`; C7 identity đã có nhưng role chưa; D2 runtime resolve order; D3 drop-rate design; D4 armor/device coefficient; D5 component/extra-life join; cùng E1/E3/E4 tool/source integrity notes. Không phải tất cả đều cần một report mới:

- **Evidence gap** (ví dụ B1/B4/B5, D5 owner) cần nguồn cho phép hoặc phải ghi bounded-missing.
- **Semantic assignment** (B6/C8/C7) cần giữ `NOT_BOUND` nếu không có join.
- **Design choice** (D3, một phần D4) phải được gắn nhãn “tự chọn”, không mô tả như raw còn thiếu.
- **Runtime-gated** (D2 và playback/parity) không được suy ra từ static. Lệnh đóng #28 runtime lane vẫn giữ hiệu lực.

### P2 — Mức sẵn sàng sản phẩm không đồng nghĩa độ phủ report

`MISSING_FOR_NEW_GAME.md` nói L1 đủ để dựng cơ chế với art/số tự chọn; L2 chưa đạt tương đương số; L3 vẫn là đích, cần so ảnh/scene/timeline/audio bằng gate máy. Điều này không phủ định report tĩnh đã hoàn thành, nhưng cũng không cho phép tuyên bố game/spec “đủ nghiệm thu”. Giữ rõ: **analysis coverage ≠ runtime parity ≠ L3 acceptance**. Các missing sprite labels/consumer binding và các gate chưa chạy là project work, không phải lý do để tăng mức bằng chứng report hiện có.

**README catalog formatting:** ở `docs/spec/README.md` §1, dòng “Art / tech art” đang gộp label với RD1 note (`>` trong cell) thay vì có cell điều hướng riêng. RD1 chỉ kiểm số dòng/bảng của các file được liệt kê, nên có thể xanh dù cấu trúc Markdown/navigation bị vỡ. Tách lại row Art/tech-art và đưa RD1 note ra ngoài bảng; không ảnh hưởng số liệu game.

## 5. Status refresh sau ACK114 và D5-residual

ACK114 (`6426867942`) nhận tổng kiểm này và ghi **7 P1/P2 fixes đã áp dụng trên central spec**: danh mục 29 ID và quy tắc 13/25 A–D; gỡ giả thuyết `kHp[mode]`; tách save-ID/combat-index; cập nhật Arena/PvP bounded slices; sửa README art row; sửa G1 locator; xác nhận wording report152/`Stop` đã sạch. ACK114 cũng formal-close H4/121, nhận AI-4 #29 follow-ups 150–152, và nhận HANDOFF128 bounded. **Đây là trạng thái central spec; không tự động có nghĩa các file cùng tên trong working branch này đã đồng bộ.** Các mâu thuẫn §4 là findings của branch snapshot lúc audit; central spec đã báo đã sửa chúng.

Sau ACK114, ceiling trung tâm còn review-126→127 (AI-3), ef-M1, AI-4 follow-up-20 (tự chọn), registry còn 12 open, và D5-residual. Các handoff khác được ghi dưới đây theo comment trạng thái, không phải review độc lập nội dung lane.

| Lane / item | Trạng thái cập nhật mới nhất đã kiểm | Việc còn lại |
|---|---|---|
| **D5-residual** | Claim `6426986645` / report 164 bounds PPtr/extra-life; user-lead claim `6427556449` / report 165 supports the previously published Health-tech route, while starter premium, initial extra-life stock, and player component owners remain `NOT_BOUND`. | Reuse reports 79–87, 109, 163–164; no coroutine/receiver repetition or runtime/native/FDE expansion. |
| **#27 H4 / report 121** | Formal-close theo ACK114; 7/7 findings và G1 locator correction được xác nhận. | Không còn là blocker; chỉ mirror central changes vào branch/spec snapshot nếu cần. |
| **#27 HANDOFF128** | Accepted bounded theo ACK114. | M1 là next candidate; không thuộc D5 và không review native/FDE ở đây. |
| **AI-4 #29 reports 150–152** | Accepted theo ACK114 (lane-local numbering; khác file reports 150–152 trong repo #27-GS). | Queue tiếp theo là follow-up-20; các report này không được dùng để tự nâng toàn bộ Arena/PvP semantics. |
| **Registry** | 12 items còn open; ACK114 nói phần lớn runtime/bounded. | Giữ từng item theo status/owner; không đổi thành static closure bằng suy đoán. |
| **Review 126→127** | Review-126 claimed; 127 để vòng riêng theo ACK114. | Review 126 rồi mới tiến 127, ngoài phạm vi audit này. |

Các trạng thái lane khác là **PR12 coordination status**, không phải audit độc lập report 121/128 hoặc AI-4. Không kiểm tra native/FDE hay runtime lane trong cuộc tổng kiểm này.

## 6. Kiểm tra cục bộ tái chạy được

- `python tools/verify-claims.py`: **213 PASS / 0 FAIL / 2 SKIP**. Hai skip: B9 (một con số animation chưa kiểm lại offline) và F4 (Sprite cần TypeTree export thêm).
- `python tools/raw-audit.py`: **184 RAW · 3 DOC · 28 CONST = 215** claim; đây là phân loại claim, không phải tỷ lệ hoàn tất dự án.
- `python -m unittest discover -s tests`: **282 tests OK**.
- `git diff --check`: sạch sau khi cập nhật báo cáo và mục lục.

Các kiểm tra này xác nhận consistency của claim/test hiện có; **không** xóa `NOT_BOUND`, không chốt các open issue thiết kế, và không xác nhận runtime parity.

## 7. Thứ tự đề xuất

1. **Mirror sync đã được central spec chấp nhận:** H4/121 đã formal-close ở ACK114; nếu cập nhật working copy, dùng 7 corrections đã xác nhận ở central spec và giữ provenance/branch identity. Không đánh dấu H4 còn pending.
2. **D5 residual:** report 164 bổ sung bounded serialized-export coverage, nhưng không có owner/extra-life join; giữ `NOT_BOUND` trừ khi có source serialization mới.
3. **Dọn các mâu thuẫn còn tồn tại trong local snapshot:** đếm lại OPEN_ISSUES theo quy tắc đã ACK'd (29 ID; 13/25 A–D), bỏ B3/kHp, tách combat index khỏi save ID, và mirror update Arena/PvP sau khi kiểm lane-local source.
4. **Gom các open issues theo loại:** evidence / semantics / design / runtime-gated; ưu tiên B1/B4/B5/B6/C8 nếu cần thêm fidelity, và đánh dấu D3/D4 là quyết định thiết kế khi không có raw đủ.
5. **Không báo project completion:** L1 đủ cho cơ chế không đồng nghĩa L2 parity hay L3 visual/scene acceptance; giữ các gate riêng và không tự mở lại #28 runtime lane.

**Bottom line:** report 163 và reports 160–162 đủ làm handoff bounded. Tồn đọng lớn nhất hiện không phải thiếu thêm một câu kết luận static, mà là **(a)** những `NOT_BOUND` có chủ ý, **(b)** các bảng SPEC cũ chưa được đồng bộ nhất quán, và **(c)** các gate sản phẩm/thiết kế chưa hoàn tất. Báo cáo tổng thể nên trình bày đúng ba lớp này, không gộp thành một tỷ lệ “hoàn thành”.
