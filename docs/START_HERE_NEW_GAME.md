# Bắt đầu ở đây — bàn giao cho AI viết game mới

**Cập nhật 25/10/2026, sau report64. Tất cả kết luận APK vẫn tạm thời.**
Repo này là **kho dữ liệu reverse-engineering + tài liệu tham khảo**, **chưa phải project game chạy được**. Có đủ dữ liệu để bắt đầu prototype có scope; chưa phải hợp đồng đầy đủ để một agent tự dựng/phát hành cả game mà không hỏi quyết định sản phẩm.

## 1. Nguồn nào được tin, tài liệu nào chỉ dẫn đường?

1. Nguồn game: raw bóc từ **cùng APK**: `reverse-engineering/raw/`, dump/native/serialized identity. Report dẫn tới raw, không thay raw.
2. `datas/`: bảng dẫn xuất để import; kiểm schema/nguồn/scope trước khi dùng. `datas/waves.json` grouped theo export **không phải** timeline runtime hay danh sách spawn đã dedup đúng theo resource.
3. `docs/apk-analysis/`: phân tích có phạm vi và cách tái kiểm. Tìm report mới theo **chủ đề**, không coi số report cao hơn là phủ định mọi report cũ.
4. `docs/spec/` trên nhánh này **chỉ có snapshot cũ**, không phải spec đầy đủ mới nhất của peer. Không bắt đầu triển khai từ bốn file đó mà bỏ review.
5. Nhánh spec `arena/20330d0e-windwings-space-shooter-game-p` đã đọc ở **cf27b97553ef25107b45b039f316d9ca7850a885**. Họ có START_HERE và sửa nhiều lỗi cũ, nhưng **đọc docs/HANDOFF_REVIEW_cf27b9755.md trước**. Không import wholesale/merge hai nhánh.
6. Screenshot dùng để xem UI/flow/tham khảo, không chứng minh numeric/native của build khác. **Không vẽ lại game từ screenshot.**

Mỗi lựa chọn triển khai phải ghi một trong: `APK fact + raw_ref + scope`, `derived + formula + inputs`, `new design + rationale`, `unknown + fallback cần duyệt`. Không nâng giả định thành A vì unit test PASS.

### Pin build đã phân tích

Lấy từ `reverse-engineering/raw/early-waves/index.json`:

| Input | SHA256 |
|---|---|
| data.unity3d | `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |
| libil2cpp.so | `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99` |
| global-metadata.dat | `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69` |

Không trộn input lấy từ latest APK khác vào raw này. Không commit APK/XAPK/full audio/full atlas hoặc file >5MB; release gốc giữ **draft**.

## 2. Thứ tự đọc để viết gameplay, không phải đọc tuần tự 64 report

`raw/` trong bảng là `reverse-engineering/raw/`.

| Cần dựng | Đọc report | Input triển khai / bằng chứng |
|---|---|---|
| Scene → stage → map → waves | 52 | `raw/ui-audit/scene-map-flow.json.gz`, `datas/maps.json`, `datas/map_segments_full.json`; nhánh chapter/branch/mode phải đi theo consumer |
| Wave/spawn/wave-end | 53–54 | `raw/early-waves/index.json`, exact root exports, `resolved-default-waves.json.gz`; index chứa file/root/PPtr identity |
| Mission denominator + result + save | 55–58, 64 | `raw/early-waves/mission-denominators.json.gz`, `raw/endgame-missions/{mission-progress-flow,false-result-reachability,shared-stage-victory}.json.gz` |
| Tutorial và UI Continue | 45, 47, 50–51, 64 | `raw/ui-audit/{stage23-ui-flow,tutorial-consumer-flow}.json.gz`, `raw/il2cpp-consts/{DataTutorials,GP_Tutorials,Board_Endgame}.{asm.txt,json}` |
| Enemy/controller/boss/animation | 34–41, 59–63 khi liên quan | raw controller graph, native receiver/consumer, decoded clips. Timestamp không đủ làm state machine |
| UI render/layout/sprite refs | 43–47, 62 | `raw/ui/_index.csv`, UI reference/render exports, typed PPtr. Lấy index làm population, không glob mọi layout cũ |
| Sprite → texture/atlas | 62 | `raw/sprite-geometry/{index.json,objects-000..005.jsonl.gz,resolved-geometry.json.gz}` |
| Ship/drone/gun/HP/economy | 14–15, 19, 28 + native consumer | `datas/README.md`, config CSV, `raw/il2cpp-consts/Player_Get_Datas*`. HP prefab không mặc định là HP runtime; thiếu field không chứng minh không có khác biệt theo tàu |
| Asset/audio/spine/font | `docs/assets/INDEX.md`, 17, 21–23 | Contact sheet để duyệt; full pack ngoài Git để tra/crop/nghe; audio-index + Spine mapping |

Không rerun full analyze chỉ để đọc một raw đã có. Muốn giữ/rebuild kết quả mới, giữ cả raw/source hash và tool/test tương ứng.

## 3. Contract tối thiểu cho ba opening stage

**Scope APK được nối: campaign thường GameMode0 / nonbranch / ChapterCurrent0; các điều kiện khác đọc consumer.**

| Stage hiển thị | Internal index | Wave IDs đúng thứ tự | Gate tutorial riêng |
|---|---:|---|---|
| 1 | 0 | 25, 9010 | index0 và IndexTutorial0; move/transform |
| 2 | 1 | 164 | index1 và IndexTutorial1; drone |
| 3 | 2 | 113, 5 | index2 và !touchSkillDone; không gate IndexTutorial2 |

Wave normal exact roots: `wave_0164` **148604**, `wave_0113` **21468**, `wave_0005` **38187**, serialized file resources.assets. Tra container_key trong raw index; **không** dùng Chapter2 root trùng tên. Stage1 wave25/9010 đọc bằng chain/map và export liên quan, không lấy ba exact-wave exports ở trên thay cho stage1.

### Chia state cho đúng

- Scenario/spawner và tutorial gate là hai tầng khác nhau. Giữ pause/resume/input lock theo nhánh tutorial đã đọc; replay không bật lại hướng dẫn chỉ vì cùng stage.
- Gate hoàn tất trận theo wave/active enemies + Playing. **Không** đủ kill là thắng/kết thúc ngay giữa wave.
- Campaign normal: đánh giá mission từ kill/count, player health=0 ép false; endgame/moveout → **cùng OpenBoardVictory(bool)** → **cùng Board_Endgame** cho cả ba stage.
- Method tên OpenBoardVictory nhận cả bool false. `VictoryNow` ép true cũng vào cùng board; không áp phép tính kill trước cho mọi entry debug/forced.
- Board chung có SetMissions/save và tutorial overlay; Continue còn kiểm mode/result/IndexTutorial. Không làm ba victory implementation riêng, cũng không bỏ overlay để ép mọi màn giống hệt.
- Result −1..2 khác saved stars 0..3. Chỉ lưu improvement theo đúng scope; replay không tự cộng lại sao. Không tự nói SaveToDisk đồng nghĩa PlayerPrefs đã flush.
- Target progression có nhánh **không gate theo incoming bool** (report58). Không “sửa cho hợp lý” mà không ghi đây là quyết định game mới.

### Ngưỡng đã resolve, không tự xin lại dữ liệu đã có

Normal LevelCurrent0: mode0 coefficients `.20/.45/.80`; mode1 `.35/.60/.98`; other `.50/.80/1`. float32 multiply rồi truncate theo consumer, không tự dùng round.

Stage2 denominator **262**, stage3 **238** → mode0 thresholds **52/117/209**, **47/107/190**. Đây là denominator đã filter, **không** phải số spawn chắc chắn hay số prefab slots. Stage1 không điền số suy từ wave-name/grouped totals.

Spawn enum: 0PinMap/1Path/2Points/3RandomTopDown/4Rocket/5EndMap/6StartWave. Concrete spawner mới quyết định hành vi: enum/nodename không thay được class/consumer. Rate0 không tự là cùng frame; `number=0` không có nghĩa không spawn. Không chia đôi/dedup enemy theo tên.

**Không lấy việc chưa chứng minh low-kill playthrough/BB pool history làm blocker** cho đọc/dựng scenario. Chỉ quay lại lifecycle khi có mâu thuẫn cụ thể ảnh hưởng logic đang viết.

## 4. Asset pack — bắt buộc cho tham khảo thiết kế, chưa được gọi là đã kiểm đủ

- Browse nhanh: `docs/assets/INDEX.md`, contact-sheets JPG, manifest, sprites-index, audio-index.
- Draft release `windwings-assets-1.3.118`: đã kiểm API thấy `assets.z01`, `assets.zip`, `manifest-full.csv`, `asset-previews.zip`. **API listing không chứng minh nội dung đủ/zip không lỗi.**
- Download vào thư mục **ngoài Git**, kiểm dung lượng/hash nếu có manifest, giữ nguyên các part. Với split ZIP tạo bởi `zip -s`:

```bash
gh release download windwings-assets-1.3.118 --dir /home/user/windwings-reference-assets --pattern 'assets.*' --pattern 'manifest-full.csv'
cd /home/user/windwings-reference-assets
zip -s 0 assets.zip --out assets-full.zip
unzip -t assets-full.zip
unzip assets-full.zip -d extracted
```

Không dùng `cat assets.z01 assets.zip > assets.zip` — sẽ phá file đầu vào. Không publish draft.

Full-pack acceptance còn mở: đối chiếu manifest→file thực, browse tất cả sprite/texture/atlas, nghe audio, mở Spine skeleton/atlas/texture liên quan và fonts. 2185/2185 geometry joins chỉ là metadata; kiểm crop alpha/trim/pivot/flip/rotation, 40 rect vượt biên <1px vẫn phải xử lý có chứng cứ, không tự clamp. JPEG preview metrics không thay texel/alpha gốc.

Art/audio/font của game phát hành mới cần nội dung và quyền sử dụng phù hợp. Không nhúng tài nguyên gốc chỉ vì đã tải được. Tư liệu gốc vẫn giữ cho tham khảo, không xoá vì đã chọn art mới.

## 5. Trước khi viết code mới, agent phải xuất một kế hoạch có thể duyệt

Chưa có quyết định rõ thì hỏi user, không tự đoán từ engine game gốc:

1. Engine/framework, platform, portrait/responsive/safe-area, input touch/keyboard và target devices.
2. Scope vertical slice: stage1–3, start/menu/game/HUD/tutorial/result/continue/replay/defeat; Premium **để sau**.
3. Asset map và art direction mới, nguồn/quyền sử dụng, placeholder nào tạm; không dựng lại screenshot.
4. Data contracts: stage/wave/spawn/mission/tutorial/save; mỗi record giữ typed ID + source + scope. Không dùng GO name/global pathID đơn lẻ làm primary key.
5. State transition table + signal consumer: bắt đầu/kết thúc wave, chết, tutorial pause/resume, result, Continue/back. Phần không có raw ghi **new design cần duyệt**, không lấp bằng giả định APK.
6. Save schema version/default/migration cho game mới: có một phần cơ chế gốc đã bóc, **chưa có schema đầy đủ**. Nếu tự thiết kế phải ghi rõ save mới, không giả là phục dựng nguyên bản.

## 6. Nghiệm thu vertical slice — khác với nghiệm thu kho raw

**Trước code/data import:** verify typed joins và scope; regenerate từ raw, không sửa số tay.

```bash
python3 datas/validate.py
python3 tools/verify/shared_stage_victory.py
python3 tools/verify/peer_handoff_review.py
python3 -m unittest discover -s tests -q
```

**Sau khi có game chạy được:**
- Stage1/2/3: first-run / replay; đủ kill + còn sống / không đủ mission / chết; kiểm result đúng nhánh, overlay không kẹt input.
- Wave-end/active enemy bookkeeping đúng; không kết thúc giữa wave vì vừa vượt ngưỡng kill; marker không biến thành enemy.
- Result sao/save improvement, reload, Continue/back; input và persistent flag không bị reset mỗi lượt.
- Multiple aspect ratios/safe areas; readability player/enemy bullets, text, UI hierarchy; crop/animation/audio đúng mapping.
- Playtest thật + ảnh/video trên target devices. Metrics màu/contrast chỉ trợ giúp; histogram PASS không chứng minh đẹp hoặc chơi tốt.
- Không gọi test static PASS là đã replay hay đã đủ toàn bộ game. Báo riêng: raw verified / implemented / runtime-tested / unknown.

## 7. Việc tiếp theo thực sự còn mở

- Spec peer: sửa N1–N5 trong `HANDOFF_REVIEW_cf27b9755.md`, cập nhật report64, soát thông tin stale ở cửa vào.
- Assets: full-pack integrity/browsability và pixel-crop validation, không chỉ tăng số label.
- Triển khai: chốt platform/engine/scope rồi viết vertical-slice plan, không lấy một bảng “8/13 hệ đủ” thay acceptance.
- Raw chỉ đào tiếp theo thiếu hụt cụ thể ảnh hưởng implementation. Không mở lại Premium hoặc speculative lifecycle proof ngoài scope.

`HANDOFF_AI_TASKS.md`, `HANDOFF_DATA_SYNC.md`, `CROSS_BRANCH_20330d0e.md` giữ lịch sử phối hợp; phần cũ không phải lệnh hiện hành. Tài liệu này là điểm bắt đầu, report/raw được dẫn mới là căn cứ.
