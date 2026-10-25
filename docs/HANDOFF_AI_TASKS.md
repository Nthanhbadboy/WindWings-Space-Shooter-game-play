# Phân việc vòng 4 — cái còn thiếu thật

> Trạng thái hiện tại: `docs/conclusions.md`. Đã có **dữ liệu thô** trong
> `reverse-engineering/raw/` (typetree JSONL gz, UI layout gz, hằng số IL2CPP + asm).
> Mọi kết luận là **tạm thời** — phải ghi mức A/B/C khi trích dẫn.

## Luật (giữ nguyên)

1. Nguồn: `reverse-engineering/raw/**` (thô) + `datas/*.json` + `docs/apk-analysis/*.csv`.
   Không trích `PHAN_TICH_*` hay tài liệu tóm tắt cũ.
2. Chỉ ghi trong `docs/spec/`. Không sửa `reverse-engineering/`, `datas/`, `tools/`, `.github/`.
3. PR riêng `docs(spec4): ...`. Mỗi bảng ghi `(nguồn: file, mức A/B/C)`.

## Việc

### A. `docs/spec/CONSTANTS.md` — giải nghĩa hằng số IL2CPP
Nguồn: `docs/apk-analysis/19-il2cpp-constants.md`,
`reverse-engineering/raw/il2cpp-consts/<Class>.json` + `<Class>.asm.txt`.

- Với **10 method quan trọng nhất** (ưu tiên: `GetCostReborn`, `GetUpgadeCostCoins`,
  `GetUpgradeCostGems`, `GetBonusCoin`, `GetBonusExp`, `GetSurvivalScore`, `GetNumberWaves`,
  `GetPVPPlayScore`, `GetArenaScore`, `MAX_LV_TECHLAB`), đọc `.asm.txt` và viết lại **pseudo-code**
  của phép tính, chỉ rõ hằng số nào là hệ số, hằng số nào là clamp/epsilon.
- Bảng: `method | hằng số tìm thấy | ý nghĩa suy ra | mức tin (B/C)`.
- Những method chưa giải thích được thì liệt kê, đừng đoán bừa.

### B. `docs/spec/UI-MEASURE.md` — đọc layout thật
Nguồn: `docs/apk-analysis/20-ui-layout.md`, `reverse-engineering/raw/ui/*.json.gz`
(584 file; mở bằng `python3 -c "import gzip,json;..."`).

- Chọn 5 màn: `Board_Home`, `Board_Chapters`, `Board_Players`, `Board_Shop`, `Board_Endgame`.
- Với mỗi màn: bảng node (path, local_pos, scale, component, text/key), nhóm theo vùng
  (top bar / content / bottom nav / popup).
- Suy ra hệ toạ độ: bao nhiêu unit = 1 màn hình, vùng safe area, tỉ lệ.
- Kết luận: dựng lại được bao nhiêu % bố cục bằng số, chỗ nào phải tự thiết kế.

### C. `docs/spec/TEXT-MAP.md` — chữ nào ở đâu
Nguồn: `raw/ui/*.json.gz` (field `components[].text` + `key`) + `i18n/vi.json`.

- Ghép `key` → chuỗi tiếng Việt cho từng màn (bảng `screen | node path | key | vi`).
- Đếm: bao nhiêu % text node đọc được key, bao nhiêu chỉ có chữ cứng.
- Danh sách chuỗi cứng (hardcoded) — đây là chỗ phải viết lại khi làm bản mới.

### D. `docs/spec/GAPS.md` — còn gì không lấy được
- Tổng hợp từ `docs/conclusions.md` mục "chưa bóc được".
- Với mỗi mục: có lấy được nữa không, bằng công cụ gì, chi phí ước tính, và **nếu không lấy được
  thì thiết kế lại thế nào**.
- Đây là đầu vào cho quyết định scope, không phải danh sách mong muốn.

## Xong khi
- 4 file, mọi con số có `(nguồn, mức)`, không có kết luận nào ở mức C bị trình bày như số thật.
- Mỗi file có mục "còn thiếu" riêng.

## Ưu tiên mới — review nhánh spec 25/10/2026

Đọc **docs/HANDOFF_SPEC_REVIEW_71b1e9861.md** trước khi viết design tiếp.
R1–R3 là P0: timestamp không chứng minh thứ tự pha; 12 handler không mở khóa
793 event; base Enemy_Appear không chứng minh appearance của mọi enemy.
R4–R7 cập nhật raw và sửa điều kiện kết luận quá mạnh. Nhánh spec sửa tài liệu/
claim bên nhánh mình; nhánh dữ liệu giữ các task đào raw còn mở. Không merge.

## UI onboarding / first clear stage 1–3 — 25/10/2026

Xem report `docs/apk-analysis/42-early-stage-ui-flows.md`, raw
`reverse-engineering/raw/ui-audit/early-stage-coverage.json.gz`.
Chưa tuyên bố đủ luồng UI: có board/layout không chứng minh stage gate hoặc
queue popup. DataTutorials có getter hasTutStage1..4; chưa được tự gán nội dung.
Nhánh dữ liệu đã mở export native/typetree (921dc909b, Actions 40176643619).
Nhánh spec lập matrix first clear/replay/defeat/back/continue cho stage 1–3,
giữ UNKNOWN đến khi có branch evidence. Tutorial gameplay/HUD không nằm chắc
trong scope exporter root Board_/Popup_/Tab_; cần kiểm coverage riêng.

## UI drawing readiness — cập nhật sau native export

Report **43-ui-drawing-readiness.md**: đã có raw native daa2c3a03/40176643619.
Bắt đầu wireframe các board lõi được; chưa gọi đủ full onboarding. Đã resolve
stageIndex 0/1/2 → gate tutorial control/transform, drone, touch-skill (có thêm
điều kiện). Endgame.SetupTut với IndexTutorial<=1 ẩn Back/Replay/Continue.
Nhánh spec phải vẽ trạng thái này riêng và giữ callback bật lại OPEN.
Raw `ui-audit/drawing-inputs.json.gz` nối node → sprite gallery/contact-sheet;
raw `early-native-gates.json` giữ asm/check. Đừng match trực tiếp tên Unity với
tên gallery sanitize; dùng bảng original-name → type/path_id → gallery.
Exporter lượt tới bổ sung TMP/sprite properties và tutorial panel sibling;
chưa được xem như đã đủ pixel-accurate cho đến khi raw mới về/đã kiểm.

## Ưu tiên đồng bộ — tránh đọc mốc 019e704d1 cũ

Đọc **docs/HANDOFF_DATA_SYNC.md**. Kiểm trực tiếp remote ngày 25/10 thấy data
đã tới c570485c5, có 9 commit sau 019e704d1. Verifier spec local-first có thể
bỏ qua raw ở --ref mới khi file local cũ còn tồn tại. Fetch explicit remote
tracking ref, đối chiếu ls-remote/rev-parse và ghi source SHA trước khi báo lại.
