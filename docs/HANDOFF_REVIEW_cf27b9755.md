# Review mới nhánh spec và cửa vào cho AI dựng game

**25/10/2026 — tạm kết, không phải audit toàn bộ nhánh.**
Đã fetch **đúng ref tường minh** của `arena/20330d0e-windwings-space-shooter-game-p`, pin **cf27b97553ef25107b45b039f316d9ca7850a885**. `git fetch origin` mặc định trước đó vẫn để tracking ref ở 25c367aca; kiểm `ls-remote` mới phát hiện head mới. Không được báo “bên kia không có gì mới” từ ref cũ.

## 1. Phải ghi nhận các sửa đúng, không lặp review cũ như hiện trạng

Đọc `HANDOFF_SPEC_FIX_25c367aca`, `MISSIONS_STARS`, `ENCOUNTERS`, classifier và verifier tại snapshot mới:

- R1: đã sửa selector mode 0/1/fallback, có ngưỡng normal stage 2/3 và tách saved stars khỏi kills.
- R2: đã rút divide-by-two theo tên; phân biệt normal/Chapter2; sửa đơn vị thành **23.757 Call_Data object / 11.089 dòng grouped**. Không lấy tổng bằng nhau làm chứng minh từng wave không đổi.
- R3: đã đổi “sheet chưa tách” thành tên atlas không match; có ghi geometry join không phải crop validation.
- R4: `Coda_A` hiện tới rule font; `XVideo` hiện tới UI; passthrough không tự cấp A, có provenance. Đã tái kiểm RULES bằng AST, không chạy mã peer.
- R5: readiness không còn đóng D3 chỉ từ timestamp.
- R6: verifier đã có ERROR, no-skip, required-prefix, empty-selection guard. **Xác nhận sửa code bằng đọc tĩnh; chưa chạy suite/CI của nhánh peer trong checkout này.** `None`/missing document vẫn có SKIP: dùng strict-required khi nghiệm thu.

Có `START_HERE` và `MISSING_FOR_NEW_GAME`, tốt hơn trước về đường đọc theo vai. Nhưng cửa vào mới chưa an toàn để AI khác coi là hợp đồng triển khai.

## 2. Các chỗ cần sửa tiếp trước bàn giao

### N1 — Map→wave bị ghi là blocker chưa bóc, trong khi đã có consumer và raw

`MISSING_FOR_NEW_GAME §2.1, §5` vẫn yêu cầu bóc 576 blob để biết một stage có mấy wave. Trong cùng snapshot, DATA_SYNC đã nhận report52 và các kết quả sau đó.

Raw `ui-audit/scene-map-flow.json.gz` giữ consumer/cctor cho hai mảng campaign; `datas/maps.json` là bảng dẫn xuất, không phải nguồn độc lập. Opening campaign Chapter0 đã nối stage index 0/1/2 → `[25,9010] / [164] / [113,5]` qua nhánh consumer. Không nói toàn bộ 576 blob/mọi mode đã xong; phải tách **campaign list đã resolve** khỏi phần chưa decode. Không yêu cầu chạy lại full APK vì một blocker đã có lời giải trong raw.

### N2 — Suy damage/HP của tàu từ 4 field là không hợp lệ

`MISSING_FOR_NEW_GAME §1 hàng9, §2.2`: `Player_Info` chỉ 4 field ⇒ “tàu không có HP/damage riêng”, toàn bộ khác biệt chỉ ở rank/Star.

Raw **GetMainCannonDamage(int playerIndex)** giữ tham số ở w19 (`14e396c`), lấy array static offset `0x78` (`14e3a78`), kiểm index rồi đọc float **theo playerIndex** (`14e3a84..14e3a90`). Rank/upgrade đi vào phần tính tiếp, không xoá lookup theo tàu.

Sửa: bỏ suy luận từ việc field vắng trong một class. Chưa resolve đủ giá trị thì giữ unknown; lookup theo playerIndex không tự chứng minh mọi tàu có giá trị khác nhau, cũng không tự chốt HP. Đọc consumer và array tương ứng, không tự đổi tên playerIndex thành rank.

### N3 — Proxy ảnh bị nâng thành định luật art và máy chấm “đẹp”

`START_HERE §3`, `VISUAL_DESIGN §3, §5`, `ART_STUDY §3.2`:

- “đạt 4 khoảng ... là đạt”, “lệch thì sửa art, không sửa số” không được suy ra từ vài histogram/contrast/edge metrics. Chúng không kiểm silhouette, readability đạn, font, hierarchy, temporal clutter hay chất lượng art.
- ART_STUDY đo trên **JPEG contact sheet**, đã resize, caro và flood-fill, không phải alpha/texel gốc. `val_std` không tự là độ sâu gradient bóng; dark-pixel share không tự là outline. Median nhóm không phải hằng số của mọi sprite. Chính bảng có background 0.12 và font 0.09, trái câu gradient 0.20–0.26 cho mọi nhóm.
- 54.019 bbox lấy từ derived UI không thể tự gọi là 54.019 màn hợp lệ độc lập. Index hiện được audit là 797 file; report62 đã phân biệt hàng chục nghìn file ngoài index. Phải chốt sample/frame, index/source hash, xử lý instance trùng trước thống kê. Max bbox không tự chứng minh ScrollRect/danh sách cuộn.
- Tỉ lệ screenshot một thiết bị không phải canvas bắt buộc cho mọi máy. Cần responsive/safe-area; không dùng nó ép 1080×2244 như dữ liệu engine gốc.

Sửa: gọi số này là **tham khảo trên sample/preview cụ thể**, tách khỏi art direction mới. Bắt buộc review ảnh gameplay thật, kiểm readability/motion trên nhiều aspect ratio; không vẽ lại từ screenshot. Full asset pack vẫn là đầu vào tham khảo, không bị thay bằng thống kê JPEG.

### N4 — Default/không thấy xref bị biến thành luật toàn game

`START_HERE §2` trình bày 1 enemy/1s như xương sống spawn; `MISSING §1` nói rate0 là spawn cả loạt. Report53/native spawner có concrete implementations khác nhau, rate ở Path/Waypoints đưa vào WaitForSeconds; 0 không chứng minh cùng frame. Lấy transform/default của một script làm luật chung sẽ làm sai scenario.

`MISSING §3`, `VISUAL_DESIGN §4` nói “không tồn tại trong build / đừng thêm slow-mo” từ 0 site trong 139 asm file. Đây là sample, không phải whole-build closure. Không kết luận bản gốc chắc có slow-mo; kết luận phép suy **không đủ** để cấm tính năng hay chốt feel. Bản game mới dùng quyết định thiết kế có nhãn riêng nếu user chọn, không giả làm APK fact.

### N5 — Save “0 tài liệu” và thiếu tutorial/result contract

`MISSING §1, §2.3` gọi save 0 tài liệu, nhưng report45/47/51/57/58 đã bóc một phần key/branch/save/Continue. **Schema đầy đủ vẫn chưa xong**, không được đổi thành “save đã đủ”; cũng không bỏ phần có thật.

Peer đồng bộ data tới 622b700e5; chưa nhận report63/64 và điều chỉnh ưu tiên của user. Cần bổ sung:
- Stage1/2/3 gate riêng; stage3 không gate IndexTutorial2.
- Shared campaign result/Board_Endgame, player health=0 ép false; enough kills không tự kết thúc giữa wave.
- Tutorial overlay/Continue nằm trong board chung; first-run/replay/defeat khác nhau, không làm ba victory system riêng.
- Không chặn reconstruction bằng BB pool-history/low-kill-playthrough proof.

## 3. Lỗi bàn giao ngay nhánh dữ liệu — đã sửa trong lượt này

- README trỏ `docs/spec/` local chỉ có bản cũ như thể đây là spec mới, số report cố định đã lỗi thời.
- `HANDOFF_AI_TASKS` mở đầu bằng luật/vòng4 lịch sử, dễ đọc thành lệnh hiện hành.
- `conclusions` còn đặt low-kill reachability/runtime history như thiếu hụt ưu tiên cho stage2/3, trái chỉ đạo mới.
- Lệnh `cat assets.z01 assets.zip > assets.zip` trong README **truncate input assets.zip** trước khi cat. Workflow dùng `zip -s`, cần `zip -s 0 assets.zip --out assets-full.zip`, không nối đè file. Đã sửa README và hướng dẫn cho release mới; **không chạy export/publish release**.

Đã thêm **docs/START_HERE_NEW_GAME.md**: cửa vào nhánh này, phân nguồn/status, reading map, early-stage implementation contract, asset/download contract và acceptance checklist. Đây là bản hướng dẫn tiếp nhận, không giả thành game đã được viết hay mọi config đã resolve.

## 4. Việc giao lại peer

1. Sửa N1/N2/N4 trước vì AI sẽ viết sai logic/config.
2. Hạ các khẳng định aesthetic thành metric mô tả sample; giữ review hình/motion + responsive.
3. Update missing/readiness bằng đúng raw hiện có; bổ sung report64; không copy kết luận rồi đánh A nếu chưa đọc raw.
4. Viết contract triển khai có engine/platform được user chốt, input/output/schema/state và acceptance, không thay bằng file-count PASS.

## Tái lập và giới hạn

- `raw/peer-review/spec-cf27b9755.json.gz`: pin **15 file peer nguyên văn + SHA256**.
- `raw/peer-review/handoff-cf27b9755.json.gz`: thân native damage + raw map/save/shared-result/geometry inputs, source hashes, **16 kiểm tra**.
- `python3 tools/verify/peer_handoff_review.py`; tests chỉ kiểm pin/source/lệnh/AST và phát hiện câu cần sửa; PASS **không** chứng nhận peer đã sửa N1–N5 hay game đẹp/đúng runtime.
- Không import spec wholesale, không checkout/sửa/push/merge peer branch. Không audit hết mọi ảnh, mọi file hoặc toàn game.
