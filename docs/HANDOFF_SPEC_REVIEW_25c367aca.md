# Review nhánh spec — snapshot25c367aca, cập nhật raw tới61fce8ae7

**PROVISIONAL, review có giới hạn. Ngày25/10/2026.**
Nhánh được review: `arena/20330d0e-windwings-space-shooter-game-p`.
Pin chính xác: **25c367aca99f06f14df546d2f30e60b427827157**. Nhánh có thể tiếp tục
đổi sau snapshot này; không gọi các finding là trạng thái của commit chưa đọc.
Không checkout, push, merge hay sửa nhánh spec trong lượt review này.

## Kết luận

**Có2 lỗi P0 ảnh hưởng số/logic thiết kế,4 nhóm P1 ảnh hưởng độ tin cậy.**
Không nên lấy kết quả verify-claims PASS làm chứng nhận spec đúng toàn bộ.
Điểm tốt: ref-first/provenance đã sửa, tách label C/unknown, không ép phân loại
mọi sprite, chủ động giữ T9 rect/atlas là gap. Không bỏ các cải tiến đó.

Raw review: `reverse-engineering/raw/peer-review/spec-25c367aca.json.gz`, pin
**9 file đầy đủ**, SHA256, code/CSV classifier thực tế, native percent selector
và các array đã resolve. Tái tạo bằng `python3 tools/verify/peer_spec_review.py`.
Nguồn kết luận game là raw APK; nguồn kết luận lỗi tài liệu/code là snapshot
Git của chính nhánh spec, không phải kiến thức kế thừa hay screenshot.

## R1 — P0: MISSIONS_STARS sai fallback, chưa dùng các kết quả đã bóc được

**Vị trí:** `docs/spec/MISSIONS_STARS.md:83–88,319–332`.

- Dòng83: mode ngoài0..2 rơi về **mode0**. Raw selector thực tế: mode0 chọn
  slot2ae8b88, mode1 chọn2ae8b80, **other chọn2ae8b78**, không phải mode0.
- Dòng85..88 vẫn gọi bảng normal percents là blockerT5; cuối file chỉ biết
  `[.2,.6,.98]` và chưa biết mode/slot. Đó không phải3 normal arrays đã resolve.
- Dòng326..327: GetStarStageMaster/Branch còn bị ghi chưa export, nghi tính
  trực tiếp từ kills. Raw hiện có: chúng đọc **saved star count**; không lẫn
  với GetMissionCompleted tính kết quả lượt chơi.
- Thiếu denominator đúng resource/filter cho stage2/3, trong khi đã có raw.

**Thay bằng kết quả có scope:** ordinary nonbranch LevelCurrent0:

| ModeCurrent | coefficients |
|---|---|
|0|.20 / .45 / .80|
|1|.35 / .60 / .98|
|other|.50 / .80 /1|

Denominator stage2=262, stage3=238; mode0 thresholds52/117/209 và47/107/190.
Result−1..2; saved stars=result+1 khi cải thiện. Replay không cộng lại row cũ.
Không tự đặt tên difficulty; không áp bảng này cho branch/special missions.

**Raw cần đọc:** ui-audit/enemy-exit-missions.json.gz, early-waves/mission-denominators.json.gz,
endgame-missions/mission-progress-flow.json.gz và false-result-reachability.json.gz.
Report55–58 chỉ là đường dẫn đọc, không thay raw evidence.

**Nghiệm thu:** xóa/đánh dấu superseded các đoạn contradicted, thêm test selector
mode0/1/other, saved-vs-current result và stage2/3 thresholds. Không đòi screenshot
để phân biệt bảng mà raw đã resolve được.

## R2 — P0: ENCOUNTERS chia đôi/dedup theo tên không phải số thiết kế

**Vị trí:** `docs/spec/ENCOUNTERS.md:33–42,82–100`.

- Dòng27 nói prefab đã resolve nhưng33..35 vẫn nói tất cả enemies='?': hai
  snapshot đang cùng được trình bày như hiện trạng.
- Dòng42,82,93..100 khuyên số thiết kế≈raw/2 và khẳng định hai Boss_1 là một
  boss ghi hai lần. Đếm tuple/tên giống nhau không chứng minh identity đó.
- Raw container hiện đã chứng minh cùng Wave_0164 tồn tại resource khác:
  normal root148604 và Chapter2 root148637, cùng resources.assets. Các wave
 0113/0005 cũng có resource riêng. Không được xoá một prefab vì cùng tên GO.

**Sửa:** archive các số waves.json cũ dưới nhãn legacy-grouped snapshot; rút
khuyến nghị chia2. Đếm từ container key + serialized-file + root pathID +
Call_Data component identity; tách marker5/6, prefab slots, runtime number,
denominator và actual spawned count. Không tuyên bố fixed spawn count từ slots.

**Raw:** early-waves/index.json + các exact exports, resolved-default-waves.json.gz,
mission-denominators.json.gz; native wave-spawn-flow/scene-map-flow.
Đối chiếu report52–56. `rate` ở Path/Waypoints được dùng WaitForSeconds(rate),
không còn phải đoán từ argument “game phát hành thì rate0 chắc phải burst”.
Không tự suy WaitForSeconds(0) là toàn bộ enemy cùng một frame.

**Nghiệm thu:** không còn lời khuyên divide2 theo tên; stage2/3 join đúng keys;
bảng lịch sử không bị verifier coi là số runtime hiện hành.

## R3 — P1: asset labels by-name bị nâng thành bằng chứng tách ảnh

**Vị trí:** `ASSET_TRIAGE.md:41,155,164,188,202`; verify-claims.py `asset_triage_stats`.

- AB1 chỉ lấy set tên categoryatlas rồi tìm tên đó trong cộtatlas. Kết quả116
  nghĩa là **không match qua tên trong index đó**, không chứng minh116 texture
  chưa hề có sprite được tách. Chính §6 thừa nhận cộtatlas không nói runtime
  sprite nào thuộc page nào.
-252/269 tên chỉ có1 sprite không chứng minh “không phải sheet thật”.
- Tên suffix5x2/2x3 là gợi ý layout, không đủ khẳng định16 ô cắt **chắc chắn
  đúng**: còn padding, margins, rotation, trim và kích thước ảnh thực tế.
- Phần kết luận còn nói21 contact sheet, bảngAB5 nói18/25: phải thống nhất định
  nghĩa “chưa xem hết” với “còn unknown”, không cập nhật bằng search-replace số.

**Sửa:** đổi metric thành `unmatched_atlas_name_count`; trạng thái extraction
phải theo texture PPtr/source file, Sprite.m_RD.textureRect/settingsRaw, atlas
lookup, rotation/trim và PNG output manifest. T9 là gap hợp lệ, nhánh dữ liệu
nhận tiếp; không điền thiếu hụt bằng tên file.

**Nghiệm thu:** AB1 không còn PASS claim “chưa tách” bằng phép đếm name-match;
unmatched != missing. Task T9 vẫn mở tới khi có source joins thật.

## R4 — P1: classifier có shadowed rule và tự cấp confidenceA cho643 row

**Vị trí:** `tools/classify-assets.py`, RULES R14/R18/R22/R23; main113–115.

Reproduce từ snapshot, không đoán ảnh:

```text
classify('Coda_A','') -> ui / R14 Coin_* / A
classify('XVideo','') -> ui / R18 / B
```

R14 chứaCoda_ đứng trước R22(font), nên R22 không xử lý Coda_*.
CSV thật có Coda_0..3 đềuui/A/R14 dù bảng tài liệu liệt kê Coda dưới font.
XVideo củaR23(items) cũng bịR18 bắt trước. Chưa kết luận nhãn visual nào đúng;
**lỗi xác nhận được là hợp đồng rule/doc không khớp và nhánh rule không tới được**.

Main gán confidenceA vô điều kiện cho mọi row có category gốc. CSV thật:
**643 retained rows, tất cả A**. Giữ nhãn cũ không phải audit lại nguồn nhãn.
Không kết luận643 nhãn đều sai; kết luận643 mứcA chưa được chứng minh bởi đoạn code.

**Sửa:** chốt intended label, thêm test precedence/overlap, bỏ alternative chết;
`label_source`, `rule_id`, `evidence_ref`, `reviewed` riêng; giữ inherited
confidence/unknown nếu chưa có provenance. Không dùng một cộtA lẫn raw class,
nhìn ảnh và suy nghĩa từ prefix.

## R5 — P1: readiness D3 vừa partial vừa closed

**Vị trí:** `DESIGN_READINESS.md` bảng§2 và dòng47–48.

Bảng đúng khi hạ D3 xuống “chưa có thứ tự pha / điều kiện / repeat / callback”,
nhưng đoạn ngay sau vẫn nói **đóng thêm1 câu(D3), không cần decoder nữa**.
Clip event timestamp chỉ chứng minh mốc local trong clip. Không tự đóng
control-flow runtime. Đây là mâu thuẫn còn sót, không phải thiếu count table.

**Sửa:** rút câu closedD3, tách “nguồn animation có sẵn” khỏi “đã giải script
sequence”. Không thay quyết định L1 của người dùng; chỉ sửa mô tả bằng chứng.

## R6 — P1: verifier có thể xanh khi phép đo lỗi hoặc bỏ sót semantics

**Vị trí:** `tools/verify-claims.py:evaluate/main`, nhómAB.

- `except Exception` chuyển lỗi parser/programming thành SKIP.
- `main` chỉ fail khi có FAIL; SKIP không ảnh hưởng exit0. Đây là policy được
  ghi rõ trong tool, **không phải lỗi ẩn**, nhưng không đủ làm acceptance gate
  cho các claim bắt buộc.
- AB1 anchor có cả “67 page chưa có rect” nhưng tuple đo không chứa67 và không
  đọc rect evidence. Match nguyên chuỗi không kiểm hết semantics trong chuỗi.
- AB4 kiểm count/confidence trên derived CSV, không kiểm các rule có mapping
  đúng. Vì vậy có thể PASS trong khi R14/R22 vẫn shadow nhau.

**Sửa:** thêm strict-required/no-skip cho gate nghiệm thu; parser exception→ERROR
(nonzero), source absent→SKIP có chủ đích; no-selected-claims phải nonzero.
Mỗi claim atom có measurement; runtime/native joins có test riêng. Giữ
`--strict-ref`/provenance, không lùi về local-first. Phân biệt CSV count PASS
với mapping/semantics VERIFIED.

## Thứ tự bàn giao

1. R1/R2 trước: sửa số/logic sẽ được dùng thiết kế stage2/3.
2. R3/R4: tiếp asset triage nhưng không nâng độ chắc chắn bằng tên/số đếm.
3. R5/R6: thống nhất readiness và làm gate bắt được source/parser error.
4. Pin raw snapshot mới, ghi blob/hash cho từng input; ghi rõ việc chưa làm.

Không yêu cầu vẽ lại từ screenshot, không đẩy Premium vào scope, không merge
hai nhánh trong lượt này. Nhánh dữ liệu tiếp tục chịu trách nhiệm raw/T9.
