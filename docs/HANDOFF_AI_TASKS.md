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

## UI raw vòng tiếp — tutorial đã có layout, Map cần tái xuất

Đọc report44: raw c570485c5 có 8 tutorial refs/7 GO resolve local, text Việt,
font/style/sorting. Dùng ui-audit/tutorial-texts.csv + visual-coverage.json.
Endgame callback @0x126d3cc có nhánh bật Continue/ẩn Replay/IndexTutorial++;
static bool branch chưa resolve tên bằng registration map, không tự nâng kết luận.
Map đạt trần6000 node, không báo full coverage. Commit1989defc2 tăng12000 và
báo truncation; a2fac1df7 thêm external/font/material/camera context. Nghiệm thu
raw mới rồi mới bỏ OPEN. Tất cả là PROVISIONAL.

## UI routing vòng tiếp — report45

Raw routing-and-persistence.json.gz có direct-call sites, asm/hash và enum scene.
Continue không phải cạnh Next Stage duy nhất: có Home/Game routes, có nhánh
popupNotice khi btnX20Coins active; callback confirm tail-call Continue.
set_IndexTutorial gọi PlayerPreferences.SetInt, chưa chứng minh flush/restart.
GOT slot chưa được gọi là metadata address: metadata name recovery đã có raw,
lượt relocation recovery dùng native checksum-pinned để resolve đúng slot.
Không nâng Unknown chỉ vì có tên gần giống. Xem trạng thái nghiệm thu report45.

### Relocation recovery đã xác nhận (report45 bổ sung)

40180955473 success/633d552b1: GOT→effective metadata giữ native/script SHA.
Cờ là victory, key là TUTORIAL; fade callbacks load scene Home1/Game2.
Đừng gộp scene Home với Board_Home: Continue Normal chuẩn bị defaultBoard=6
(BoardStage), có zone/stars override=5 (BoardMaps). IsContinue=true/IsReplay=false.
Nhánh sau chuẩn bị: victory && IndexTutorial<=2 đi Game, còn lại đi scene Home.
Còn đọc Home_Loader consumer/queue để chốt màn hiện thực tế. Raw +10checks giữ
ở ui-audit/routing-and-persistence.json.gz, không chỉ lời bàn giao.

### Nghiệm thu raw UI 4c8d6461e (report46)

40180792800 success nhưng audit bắt 2 lỗi: native render-context thiếu file
scope; Map10315 node vẫn skip120 child do cap80. Không gọi full. 9f4f8fa10 sửa
cả hai và có test; chờ raw lượt sau nghiệm thu. Camera6/Material261/Sprite2185/
TMP7 typetree đã có để tham khảo, chưa được join external pathID khi scope rỗng.

### Cập nhật mới nhất — report47 thay trạng thái chờ của report46

Analyze40181265305 success/bot7325738be: scope đã đầy đủ; linker exact scoped
PPtr nối được 10.568 sprite +1.642 font +1.642 material occurrence trong 11root
được chọn. Raw `ui-audit/scoped-visual-links.json.gz` có hash/source/link từng node.
**Map vẫn truncated:**12.000node/2.760pending, không được gọi full. Collector mới
50.000/deque cần nghiệm thu snapshot kế; đừng lấy output cũ rồi báo đã sửa.

Recovery40181445658/f7f7ad7f3 giữ full metadata+relocations và extra-native.
`loader-and-prefs.json.gz` chứng minh Home loader nhận defaultBoard6, phát
OpenBoard56(BoardEvent selectedBoard,mode0), resetdefaultBoard1, rồi CheckSpecPopup.
Queue/callback/override vẫn OPEN. PlayerPreferences int wrappers tailcall Unity
PlayerPrefs; custom SaveToDisk không chứng minh flush TUTORIAL. Đọc report47
trước khi dùng report45/46; mọi kết luận PROVISIONAL, không blind-merge branch.

### Runtime probe — đọc report48 trước khi chạy thêm phiên

Đã audit remote25c367aca, không chỉ code cũ của nhánh này. Bản kia có injection,
property/array/anim/phone-interop fixes; không lặp lại kết luận "chưa sửa" từ bản cũ.
**Phát hiện từ APK gốc:** GP_Tutorials.get_IndexTutorial @14f4a14 có nhánh
StageTarget>=2 && cachedIndex==0 → cache6 +SetInt(TUTORIAL,6). `/statics` gọi mọi
property getter có thể tự làm đổi thứ cần đo. Dùng allowlist native field,
không arbitrary getter/forced init/Save. Raw asm/calls/metadata:
`raw/runtime-probe/getter-observer-effect.json.gz`; plan14fields/13methods ở
`stage1-3-watchpoints.json.gz` (kế hoạch, KHÔNG phải giá trị đã thu).

Run40181812673 CI xanh nhưng session/probe SKIPPED, artifact bridge:no; XAPK SHA
khớp nguồn gốc. Đã recovery40182134370 không bật phiên cloud. Phone log remote
lại thuộc packagePremium: không nhận làm gameplay evidence bản gốc.
`collect.sh` của remote còn gọi get ở4b trước definition: chuyển helper lên đầu,
kiểm JSON ok và missing/errors từng field, không lấy HTTP200/CIgreen làm nghiệm thu.
Giữ raw/provenance cho mọi lần đo, không blind-merge tooling.

### Ưu tiên mới từ người dùng — xem ảnh đọc flow, Premium để sau

Report49 đã xem35PNG của phone capture (ref25c367aca), chỉ dùng để nhận diện
trạng thái/luồng UI, không dùng balance, không đo/vẽ lại từ screenshot.
Có intro STAGE1 NORMAL/TOUCH TO PLAY; hint kéo tay; hint nhả tay đổi tàu;
Switch ships wisely Hard fight/Easy kill; combat; boss; VICTORY bị modal che.
Hint nhả tay còn xuất hiện lúc boss: không tự cố định nó ở đầu stage.
**Chưa thấy title stage2/3 hoặc kết quả sạch/Home/Map.** Tên p_2/r2_2 không phải
stage2; victory_next không chứng minh đã chuyển stage. Contact sheets không phải
timeline. Để nội dung Premium sang sau, ưu tiên thu chuỗi kết quả sạch→Continue
→titleStage2→titleStage3 có timestamps/actions. Manifest/raw quan sát được giữ
trong raw/ui-flow-review; JPEG duyệt ở docs/apk-analysis/ui-flow-review.

### Đã đào stage2/3 từ APK raw — report50 supersedes inventory gate OPEN cũ

Nguồn `ui-audit/stage23-ui-flow.json.gz` giữ24methods asm/hash/calls/metadata +
panelbinding/text; rodata literal/jumptable ở stage23-rodata.json. Recovery
40183022449 và40183197035 success. Board_Begin.Start chứng minh label stageIndex+1.
Stage2: internal1 && IndexTutorial1 → TutDrones(panel1906,delay2) → chờdrone →
3.9scaled s → timescale0/cover/focus skill → chờhasUseDroneSkill → restore GP_Time.
Stage3: internal2 && TUT_TOUCH_SKILL!=1 (KHÔNG yêu cầuIndexTutorial2 trong gate)
→ nếuTalentIndex!=-1 chạy TutTalents(panel1911,delay3), ẩnPause, lock input,
chờhasTouchBurst; callbackghiTUT_TOUCH_SKILL1, chỉ++Index khiindex2 && StageCurrent2,
bậtPause. TalentIndex==-1 có nhánh skip+ghi flag, không vẽ modal bắt buộc.
Không đòi thêm ảnh stage2/3 để bắt đầu dựng các panel/flow này. Giữ unknown ở
consumer eventState/grant/unlock/advance và runtime, không trộn với gate đã resolve.

### Report51 — consumer callback / equip / Continue đã bóc tiếp từ raw

`docs/apk-analysis/51-tutorial-consumer-equipment-continue.md` + raw
`ui-audit/tutorial-consumer-flow.json.gz`17methods/11checks;37tests pass.
Recovery40183580920 và40183664095 success. OnThroughTut table77a13e
`0029233d41555d634f74` dùng selector eventState+1:8=StartDrones,
4=lockUiTut+ShowDroneSkillButtons,2=unlockUiTut,5=HideSkillButtons,
7=ShowSkillButtons,-1=setup Controller/UI/unlocks. KHÔNG EventID.
GameStarted veneer2990898 load callback slot2ae8fb8 rồi quay14f4008;
slot→2bc4950→GP_Manager.OnThroughTut. Không bỏ branch veneer khi đọc asm.
Continue có nhánh IndexTutorial1 && slot0empty→SetDroneUsed(0,20001),
KHÔNG chứng minh ownership unlock. Loader đọc selection→Prefabs/Drones/Drone_.
Talent keyTALENT_SELECTED default-1. OpenBoardVictory normal route có tăng
StageTarget khi setup.stageIndex==target và target<ZoneUnlocked*10+9;
không tự thêm boolvictory gate. Continue nhánh min(target,current+1), nhánh khác
star-search; KHÔNG unconditional+1. LoadToLoading direct LoadScene2=Game,
không phải enumLoading. Fade callback và Game loader chưa nối hết.
Next: grant/unlock callsites, talent-selection caller, fade/loader, map-wave
consumer. Giữ raw mới GP_Spawner để nối tiếp; không cần screenshot làm điều kiện.

### Report52 — scene/fade → terrain → map wave consumer đã nối

Recovery40183973174 success/bot575113776; report52 và
raw/ui-audit/scene-map-flow.json.gz giữ12methods/13checks/cctor literals.
41tests pass. Fade callback1276e1c cũng LoadScene2=Game; wrapper gọi Unity
LoadScene(int sceneBuildIndex), không sceneLoading. FadeTo lưu Action+38,
MoveNext có invoke+38; chưa giải jump table8states/timing.
GP_Setup.Awake chỉ singleton; getterstageIndex đọc StageCurrent+24 khi nonbranch,
StageBranchCurrent+2c nếubranch; companyNameTest&&fixedStagePlay override riêng.
GP_Manager.Start14f3460→Spawner.LoadPlayer; normal terrain prefix
Datas/Maps/Terrains/Map- + stageIndex.ToString0000, GetComponentMapController.
MapController.Start132a84c getter→132a878GetListWaves, không +/-1. Normal
GetListWaves lấy listMapDatas+28/clamp. Tái đọc cctor literal array1406c9c=[164],
1406d10=[113,5], Listx28→static+28@140e19c; không đọc datas/maps.json.
Consumer formatID0000→Resources/Instantiate dướiparentWaves→SetLastWave→active.
GameMode0/nonbranch/ChapterCurrent0: display2→Wave_0164;
display3→Wave_0113 rồiWave_0005. Chapter>=1 đổi prefix Chapter2; branch riêng.
Đây là số prefab wave, KHÔNG enemy count hoặc thời gian chạy tuần tự.
Next: Wave/Spawner activation/completion; grant/select callers; fade dispatch.
