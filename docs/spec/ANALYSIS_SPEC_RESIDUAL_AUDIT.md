# Tổng kiểm analysis + SPEC — tồn đọng, thiếu sót và mức đủ của báo cáo

**Ngày kiểm:** 2026-10-27 (Asia/Saigon).  
**Snapshot trong repo:** branch `arena/a5a74747-windwings-space-shooter-game-p`, trước báo cáo này `HEAD=0376abe932e2d4b09b05efab4f74edd913656562`.  
**Snapshot phối hợp:** paginated PR12 đến claim kiểm toán `6426579737`; ACK trung tâm mới nhất là vòng 113 (`6426353854`), với cập nhật sau ACK đến comment `6426567410`.  
**Kết luận nhanh:** có thể viết báo cáo trạng thái trung thực; **chưa thể kết luận analysis/SPEC đã khép toàn bộ**. Các kết quả H1–H3 và D5 đều là kết quả bounded, không phải đóng các câu hỏi rộng hơn. Đồng thời, vài bảng trạng thái trong SPEC đang lệch nhau và cần đồng bộ trước khi xem chúng là một nguồn trạng thái duy nhất.

## 1. Phạm vi và giới hạn kiểm toán

Đối chiếu các report/receipt hiện có với `docs/spec/OPEN_ISSUES.md`, `MISSING_FOR_NEW_GAME.md`, `START_HERE.md`, `DATA_SYNC.md`, `README.md`, các spec animation liên quan và trạng thái task được comment trên PR12. Đã chạy lại các kiểm tra cục bộ ghi ở §6.

Đây là **kiểm toán tài liệu và trạng thái**, không phải phân tích lại binary hoặc kiểm tra độc lập các lane khác. Không đọc native/FDE artifacts, không chạy runtime/emulator/probe, không dùng secret, và không lấy bằng chứng từ route khác để lấp gap. Với task khác nhánh, trạng thái dưới đây chỉ phản ánh handoff/progress comment được trích, không phải review độc lập nội dung kỹ thuật.

## 2. Kết luận điều hành

1. **D5 report 163 đủ cho phần kết quả static-array join đã làm; không đủ để tuyên bố D5 hoàn tất.** Có 24/24 `Player_Attack_N → N−1` joins tới bốn mảng tĩnh. Component/GameObject/projectile owner và extra-life serialized rewiring vẫn `NOT_BOUND`. ACK vòng 113 gọi rõ kết quả này là **ĐÓNG-HALF**, và residual vẫn bounded.
2. **H1/A2, H2/B6-half, H3/C7 cũng chỉ đóng bó scope**: bảng map có thứ tự nội bộ nhưng không có named scene/stage/runtime parity; census BodyPhysics không bind semantics hoặc 19 Director classes; 45 root identity không cho asset role/use. Giữ các `NOT_BOUND`/bounded-missing.
3. **Chưa có một spec snapshot đồng bộ hoàn toàn với các handoff mới nhất.** Report 152 vẫn được index là “Partial sync”; H4/report 121 đã được push nhưng lần cập nhật mới nhất nói CI còn chờ trước formal handoff. Ngoài ra, có các mâu thuẫn nội bộ đo được trong `OPEN_ISSUES.md` và `MISSING_FOR_NEW_GAME.md` (§4).
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

### P1 — Mâu thuẫn nội bộ trong bảng vấn đề

1. **`OPEN_ISSUES.md` tổng đếm không khớp bảng:** phần đầu ghi “28 vấn đề” và “11 mục đóng / 28”. Các ID hiện liệt kê là A1–A4 (4), B1–B8 (8), C1–C8 (8), D1–D5 (5), E1–E4 (4) — tổng **29 ID**. Đếm cú pháp các hàng có `~~` hoặc `✅` cho **15 hàng**, nhưng B3 vừa có dấu hoàn tất vừa còn một mệnh đề bind chưa dứt. Đây không phải số “đóng” có thể công bố ngay: cần thống nhất đơn vị và quy tắc trạng thái, rồi tính lại summary.
2. **B3 trong `OPEN_ISSUES.md` còn ghi `StartHpPoint ← dict + kHp[mode]` là việc phải bind.** `MISSING_FOR_NEW_GAME.md` §2 và `DIFFICULTY_MODES.md` §3–5 nói `kHp[mode]` không tồn tại như hệ số, HP theo ID đã bind; vì vậy câu ở bảng B3 đang mâu thuẫn với các phần đã cập nhật. Cần sửa câu tồn đọng để không hồi sinh giả thuyết đã rút.
3. **Binding tàu bị mô tả hai cách trong `MISSING_FOR_NEW_GAME.md`:** bảng §1 vẫn nói damage/rate/cost còn thiếu index→ID tàu; phần §2 lại ghi save/load và combat đã bind theo các luật riêng (combat `Player_Attack_N → N−1`). Hãy nêu đúng phạm vi và không gộp save ID với combat index.
4. **Arena/PvP trong `MISSING_FOR_NEW_GAME.md` cần rà lại sau khi lane AI-4 được ACK:** hàng §1 còn ghi “0 report/batch” và chưa dịch class nào; các PR12 follow-up AI-4 149–151 đã báo cáo/handoff một số bounded slice. Số report trong lane AI-4 trùng với số report #27-GS ở repo này, và các handoff AI-4 chưa có ACK trung tâm trong snapshot; không đồng nhất chúng với file report cùng số ở branch hiện tại, cũng không sửa spec trước khi acceptance được xác nhận. Sau ACK, cập nhật “đã biết gì / còn thiếu gì” theo từng slice; không biến các slice thành luật Arena/PvP đầy đủ.

### P1 — Đồng bộ spec và provenance

1. `START_HERE.md` vẫn gọi report 152 là **Partial sync** với route/key wording cần reconcile. Các đoạn hiện tại của `ANIMATION_SCRIPT.md` đã phân biệt Boss-39001/39002, nêu riêng provenance `Stop` và giữ delivery unresolved; tuy vậy report 152 vẫn là review lịch sử, còn H4/report 121 chưa có formal handoff/central ACK ở snapshot này. Sau khi H4 hoàn tất, cần cập nhật index/status thay vì để “Partial sync” không rõ là hiện trạng hay lịch sử.
2. H4/report 121 progress (`6426567410`) cho biết đã push `8d4d362…`, 7 sửa đổi nội dung trong 6 tài liệu đã có; **formal handoff đợi 4 CI checks xanh**. Progress ghi vehicle check xanh, ba check còn pending lúc comment. Có thêm **P2 source-locator cleanup**: các dòng 164/165/175 trong `MISSING_FOR_NEW_GAME.md` và dòng 1586 trong `BALANCE.md` cite `153/G1` hoặc `153/G1+G2`, nhưng report 153 là G2; G1 nên trỏ HANDOFF `6422888569`, DATA_SYNC §24.88 và reports 109/122. Chưa nên đánh dấu sync hoàn tất trước handoff và chốt locator.
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

## 5. Tình trạng queue PR12 sau ACK113

ACK113 (`6426353854`) ghi D5 **ĐÓNG-HALF** và nêu ceiling lúc đó gồm report150, ef-128, report121/reviews và D5 residual. Các comment sau ACK thay đổi trạng thái một phần; vì chưa thấy ACK trung tâm mới hơn trong paginated snapshot, không đánh dấu các handoff mới là accepted:

| Lane / item | Trạng thái trong comment mới nhất đã kiểm | Việc còn lại |
|---|---|---|
| **D5** | Half-close; report 163 handoff `6426257557`; extra-life/owner vẫn `NOT_BOUND` | Giữ bounded residual; chỉ mở lại khi có serialized export mới hoặc quyết định chấp nhận bounded-missing. |
| **#27 H4 / report 121** | Push được; CI còn chờ theo `6426567410` | Chờ đủ CI, formal handoff và reviews; rồi đồng bộ source-locator/index. |
| **#27 HANDOFF128** | Handoff đã đăng `6426561197` | Chờ ACK trung tâm; report lane khác, không dùng để lấp D5. |
| **#29 report 150** | Handoff `6426330120` đã đăng sau ACK113 | Chưa thấy ACK trung tâm mới hơn trong snapshot. |
| **#29 report 151** | Handoff `6426536411` đã đăng sau ACK113 | Chưa thấy ACK trung tâm mới hơn trong snapshot. |

Các trạng thái này là **PR12 coordination status**, không phải audit độc lập report 121/128/150/151. Không kiểm tra native/FDE hay runtime lane trong cuộc tổng kiểm này.

## 6. Kiểm tra cục bộ tái chạy được

- `python tools/verify-claims.py`: **213 PASS / 0 FAIL / 2 SKIP**. Hai skip: B9 (một con số animation chưa kiểm lại offline) và F4 (Sprite cần TypeTree export thêm).
- `python tools/raw-audit.py`: **184 RAW · 3 DOC · 28 CONST = 215** claim; đây là phân loại claim, không phải tỷ lệ hoàn tất dự án.
- `python -m unittest discover -s tests`: **282 tests OK**.
- `git diff --check`: sạch sau khi cập nhật báo cáo và mục lục.

Các kiểm tra này xác nhận consistency của claim/test hiện có; **không** xóa `NOT_BOUND`, không chốt các open issue thiết kế, và không xác nhận runtime parity.

## 7. Thứ tự đề xuất

1. **Đồng bộ SPEC trước:** hoàn tất H4/121 theo điều kiện CI/handoff; sửa source locator 153/G1; cập nhật trạng thái report152 trong START_HERE; làm rõ câu summary `Stop` identity vs delivery.
2. **Dọn các mâu thuẫn có thể sửa bằng tài liệu hiện có:** đếm lại OPEN_ISSUES (29 ID, status có quy tắc), sửa B3/kHp, combat index, và Arena/PvP coverage trong MISSING_FOR_NEW_GAME.
3. **Giữ D5 residual ở mức hiện có:** không thêm một report “đóng” giả nếu không có serialized join mới. Nếu không có nguồn mới, ghi rõ bounded-missing và để source owner quyết định closure.
4. **Gom các open issues theo loại:** evidence / semantics / design / runtime-gated; ưu tiên B1/B4/B5/B6/C8 nếu cần thêm fidelity, và đánh dấu D3/D4 là quyết định thiết kế khi không có raw đủ.
5. **Không báo project completion:** L1 đủ cho cơ chế không đồng nghĩa L2 parity hay L3 visual/scene acceptance; giữ các gate riêng và không tự mở lại #28 runtime lane.

**Bottom line:** report 163 và reports 160–162 đủ làm handoff bounded. Tồn đọng lớn nhất hiện không phải thiếu thêm một câu kết luận static, mà là **(a)** những `NOT_BOUND` có chủ ý, **(b)** các bảng SPEC cũ chưa được đồng bộ nhất quán, và **(c)** các gate sản phẩm/thiết kế chưa hoàn tất. Báo cáo tổng thể nên trình bày đúng ba lớp này, không gộp thành một tỷ lệ “hoàn thành”.
