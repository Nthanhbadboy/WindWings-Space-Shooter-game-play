# Phân việc vòng 4 — cái còn thiếu thật

[Report91](apk-analysis/91-spec-review-hp-writers-and-drone-board-consumers.md) **đã làm yêu cầu spec6400762294**, review peer ecff896c. HP Start/cctor/reset/event36+64/GetStartHp/tech/device được nối; Board ctor price24→SetUpgradeCost, static attack12×2→GetPlayerPower→textDispDamage. **Không còn queue HP writers chưa đọc**; cập nhật spec từ D sang named-path evidence, không universal2500. UI500/800 khác combat450/6000, không lấy Drone_Get_Datas xác nhận UI.56 new/full648 PASS; contract `player_hp_board_flow.json`. Nhờ peer áp90+91/ACK; sửa MISSING§2.1/§5 map structure DONE≠entry binding UNKNOWN và DATA_SYNC ACK89 stale. Queue sau:23 wing còn lại; prefab/loadout drone ID/serialized turnRate3; map/save named consumers. Không merge/push peer.

[Report90](apk-analysis/90-wing-level-barrels-and-current-drone-base-fire.md), `datas/wing_drone_flow.json`:73 ranges/6041 instructions,68 anchors,44 numeric fields;92 tests mới/full592 PASS. **Áp spec:** shared Level lazy−1/cache/cap; wing1/source10003 numbers/rate/packet law;9 projectile implementations count per barrel/no midloop charge gate; sweep4 và strict laser7/9; ability25 base/(2.5*points), BaseDamages12/.16-level/rank/abi21=2.5. Không extrapolate wing1 sang23 tàu khác; không tự bind serialized drone IDs từ suffix hoặc ctor default8 của SerializeField turnRate3. **Peer:** ACK88/89 đã nhận (raw peer-review); xin ACK90 khi áp trên nhánh spec, không merge/push peer. **Queue tiếp:** đọc SetBarrels/Shoot23 ship còn lại từ raw combat-chain; bind drone prefab/loadout/sourceID và serialized turnRate3; HP writers theo comment6400762294 đã thực hiện ở report91 (xem đầu file). Đừng suy common HP từ không thấy tên mảng hay đòi screenshot/runtime trước khi đọc raw.

## Hiện hành — report89: pickup → callback → collected currency

[Report89](apk-analysis/89-pickup-dispatch-and-collected-currency.md), `datas/pickup_currency_flow.json`:20 ranges/3530 instructions/63 anchors,50 tests mới. IPooling.GetID slot0,13 switch bytes/coin aliases70001=70011,70002=70012; direct callback assignments. Collider item trước contact-hit guards; drone emits2 rồi pool, receiver không pool. Coin formula strict thresholds5500/4300/3300/2500×L,stagegroup/caps/device/.86/trunc; storecoinCount trước synchronous48; delta0 vẫn emit. Burst28 conditional69/165 khi thu đủ từ0, không cố định28 và không gộp payout qua threshold. GetStatValue2 formula có raw, array values test là synthetic chứ không APK table mới. **Peer** ACK88/89 đã nhận sau mốc89 (xem update90 ở trên); không merge/push peer. **Batch kế tiếp mốc89 đã thực hiện ở report90**; queue hiện hành xem đầu file, không viện thiếu raw chung hay đòi screenshot/runtime.


Report89 nghiệm thu: full500 PASS37.337s, code0a700993d, Verify40214936072 SUCCESS55s. Findings giao PR12comment6400594184; chưa ACK89. Recovery40214229547/raw eaa5c7434; release media vẫn draft.

## Lịch sử — report88: producer địch thật → FX/gold/items

[Report88](apk-analysis/88-enemy-hit-producers-and-gold-burst-chain.md), `datas/enemy_hit_callback_flow.json`: **16 method ranges/1256 instructions/56 anchors,19 serialized co-attachments**,4 exact callback/listener bindings +6 type joins. Skeleton.Start **overwrite** hitCallback; DropGold.Start **Combine** hitDamageCallback; Test_Enemy.Combine chỉ là component test, không thay gameplay producer. Skeleton17 và DropGold2 trên GO cóHealth đã joinfile-qualified/membership, không tự coi đãspawn. DropGold ctor28/10/iPlus1, strictlost>iPlus×10, mỗi invocation chỉ1event, damage argumentunused. Event6→Items_Manager chia spawn budget:28→3×70001+5×70002 (8objects),không28objects/28tiền; radius4pieces literal6766e63f khácnearest1.8. Đã đọc ellipsehelper +pool/IItem/explicitactivation, không measured playback.

**Đã ACK87** ở PR12comment6400347386, peertip8ac40be40e; chưa ACK88. AI spec cập nhật findings88 cùng87, không merge/push nhánhpeer. **Tiếp static:** pickupbranch Player_Physics.ItemCollected14bc328/OnTriggerEnter2D14bc9c0→Controller.OnCollectCoin1/2 để nối collectedcurrency, không suy giá trị nhặt từchia5. Queuepeer: wing-cannon SetBarrels/getter14b1eb0 và dronebasefire; reviewrawđãcó trước khi gọi thiếu dữliệu. Khôngreopenpool-history/screenshot/runtime để né static. Full450 PASS38.652s, code16748ccc3/Verify40213772726SUCCESS55s; findings gửi PR12comment6400435826. Recovery40213095828SUCCESS33s/raw098135279, mediarelease vẫn draft.


## Lịch sử — report87: end-invincibility, shield và invisible-zone

[Report87](apk-analysis/87-reborn-invincibility-shields-and-zone-state.md), `datas/player_shield_flow.json`: đã nối GOT2ae8560→RELA2be4670→metadata literal **RebornDone**, initializer delay3/10;7 roots/417instructions và18 tests mới. Không còn ghi Invoke target unknown hay tự gán2s. **Sửa85/86:** Physics.activeHitEnemey@90 là enemy-contact hit, KHÔNGmovement; Controller+48 là Player_Talent, bool20=reborning, KHÔNGinput. RebornDone giữ invincible ở shield branches, chỉ clear trực tiếp khi4flagsfalse; preserve≠settrue. Shield callbacks aggregate skill/101/103, không refcount rebirth/onehit. SetInvisible heal setup trước live reborn guard, exit A còn B vẫn clear invisible; không tự thêm replay zone trong RebornDone.

**Peer nhánh `arena/20330d0e-windwings-space-shooter-game-p`:** cập nhật các rule/erratum87 cùng6corrections đã giao86 ở PR12comment6400139575. **Đã nhận ACK85+86** ở PR12comment6400213174, peer tip266a05dd78; peer báo sửa6/6, text tipmới chưa được review lại trong batch87. Findings87 gửi6400262252, chưa có ACK87. **Việc static tiếp:** tìm producer writes/registration thật cho Enemy_Health.hitCallback@20 vàhitDamageCallback@28; receiver CalculateDamage158479c đã dịch85, fixture callbacks không phải registration evidence. Không quay lại pool-history/fullAPK/fullmedia hoặc xin runtime thay việc đọc native. Report87 code691f225b8, **full412 PASS36.340s/Verify40212492774 SUCCESS56s**. Recovery40211999354SUCCESS25s/raw7518813f4; hai failedrun do splitAPK đã giữtrace/sửa. Draftrelease vẫn giữdraft.


## Lịch sử — report86: review peer và producer extra-life/heal

Peer tip **b8f72a4127dbc2e7a24f8ff212172eb2f6eeb2ef**, snapshot10docs giữ raw. **Đã ACK84** qua PR12 (trước đây ghi chưa ack là trạng thái cũ), chưa ACK85. [Review86](apk-analysis/86-peer-spec-review-and-player-extra-life-heal.md) yêu cầu sửa: DATA_SYNC2723–2725 gộp11/13 waits và clone/projectile9; COMBAT355–365 dùng damage×interval ước lượngTTK; COMBAT416–432 bảng800/189 và noDamage=đồ trang trí; worklist cũ xin dữ liệu đã có; không nâng mục tiêu sản phẩm thành coverage/visual approval. Gửi peer sửa trên chính nhánh spec, không merge/push nhánh đó.

Tiếp việc đã hoàn thành **binding onExtraLife thật**: GOT2ae8480→RELA2bc83d0→OnExtralife14c42d4, cùng destroyShieldOneHit và WaitUntil noTouch; normal hồiHP1 trước pause/wait, resume timeScale .05 + HealHp(.5); PVP không wait/pause, HealHp(1). HealHp target snapshot, progress bắt đầu1, theo scaled deltaTime/null yield, không currentHP loop hay fullHP snap. Zone heal1.235%maxHP sau wait.2. Có19 checks mới, full394 PASS34.624s; code25734422b, Verify40211604072 SUCCESS50s. Raw2738ad848/recovery40211002716 SUCCESS. PR12 comment6400139575 giao6 corrections cho peer. Tiếp: **Invoke string GOT2ae8560** + end-invincibility flags/rewiring và enemy callback producers; rawController/RebornDone đã có, không xinfullAnalyze. Định hướng bám cơ chế bản gốc/art mới đã ghi; không chép câu “mọi thứ đã có/không test” thành bằng chứng.


## Lịch sử nghiệm thu — report85, receiver callback/damage/HP/death

[Report85](apk-analysis/85-damage-receivers-callbacks-hp-and-death.md) + `datas/damage_receiver_flow.json`: 44 body source walks/3485 instructions; enemy mutable ref + hai callbacks; controller rereadHP sau UpdateHpBar; player hai truncations → synchronous events21/39 → rereadHP → extra-life/death. Hai death overrides đã recover/dịch: Delayed dùng WaitUntil(condition), KHÔNG delayTime2; MB ba Wait1, không base Pool tail. Ability32 Destroyed là recursive damage request radius3, không chỉ FX, không dedup receiver. 48 checks mới; full375 PASS (36.026s), validate/regen/diff PASS. Code035a64f44, Verify40210554491 SUCCESS (50s). Raw220fa2d53, recovery40210107165 SUCCESS. Tiếp: exact producer/serialized receiver joins và extra-life/heal rewiring từ raw Player_Controller mới, không khai báo thiếu raw hoặc ép dependency này cần runtime. GOT2ae8480 ở Start cần metadata binding chính xác, không đoán theo tên. Không nâng callback fixtures thành subscriber thực tế. Peer nhánh `arena/20330d0e-windwings-space-shooter-game-p` áp corrections receiver cùng reports81–84; chưa có ack/merge. Coroutine recipe7 sửa typo return threshold .5, outbound .1 giữ nguyên.


## Lịch sử nghiệm thu — report84, đóng coroutine control/yield ledger83

Đã dịch control-flow đủ25 MoveNext (không còn inventory-only), giải3 computed BR từ9 byte APK, nối14 wait origins và7 factory args, có executable control models/regression. Quan trọng: 7/9 `_delay` sau attack;17 chờ sau cặp;18 toggle ParticleSystem.rateOverDistance chứ không spawn projectile. Xem [report84](apk-analysis/84-combat-coroutine-control-flow-reconstruction.md), `datas/combat_coroutine_flow.json`, `tools/verify/combat_coroutine_models.py`. Không suy dispatch thành hit/DPS hoặc coi đã có project Unity/C# hoàn chỉnh. Đã recover và nối thêm clone/pumpkin +2 iterator (30 methods); clone stop→wait0.34→pool, pumpkin deadline active2/charge1/duration4 +callback→Hide. Không chạy lại full APK/media. Local327 PASS; code58ef9809a, Verify40209405979 SUCCESS (37s). Peer đã được báo PR12 comment6399840843; chưa có ack. Peer cập nhật combat spec theo các correction này.


## Bổ sung hiện hành — report83 (25/10/2026)

Peer `arena/20330d0e-windwings-space-shooter-game-p`: khi cập nhật spec combat, đọc [report83](apk-analysis/83-main-rate-field-deadline-and-dispatch-audit.md) và `datas/combat_rate_consumers.json`. Rate là main-deadline interval; 23 schedulers extra counter, 19 riêng; 22/23/24 refresh `GetNumberAbility(4)` trong scheduler. N+1 dispatch chỉ khi N dương giữ nguyên/counter đầu 0, không phải N+1 projectile/hit. Đừng lấy spawner wait hay rate table làm player DPS. Agent nhánh này tiếp tục giải 25 MoveNext/14 wait sites theo §6, chưa giao peer làm hoặc coi complete. Không merge/spec-ack thay peer. Local 302 PASS; code `07f98ba80`, Verify `40207885962` SUCCESS (50s); peer đã được báo PR12 comment6399630253, chưa có ack.


> **Cửa vào hiện hành (sau report86):** đọc [START_HERE_NEW_GAME.md](START_HERE_NEW_GAME.md) + report81 combat-chain + report82 proof-audit + report83/84 rate/coroutine control,85 receiver và86 review/lifecycle. Review cf27b9755 và các vòng/snapshot cũ dưới đây là lịch sử, chỉ áp dụng finding còn mở; không tự là task hay phán xét hiện hành.

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

### Report53 — wave/spawn-ended ≠ kill-ended

Recoveries40184325868/40184418916 success; bot00d23f3c1. Report53,
raw/ui-audit/wave-spawn-flow.json.gz22methods/15checks;45tests pass.
Spawner.Awake nối virtualOnSpawn vào Call_Point.onSpawn, không spawn thẳng.
Call_Point.FixedUpdate: chưaspawned, state!=Endgame3, MapController.isMoveEnemyLayer,
y<=ySpawn→spawnedtrue/invoke. WarningySpawn+3 là khoảngcách, KHÔNG3giây.
Wave.SetLastWave khởi CheckSpawnEnded; GetComponentsInChildrenSpawner(false).
Normal aggregation countPoints đợi ended callback, loại5EndMapPoint/6StartWavePoint;
branch-even riêng. WaitUntil countPoints<1→WaveEndedEvent74, nếulast→SpawnEnded73.
Path coroutine number/rate/IDpool, kết thúcinvokeended+28; không phải enemydeath.
Manager listener73→b__11_7→StartCheckEndgame. Poll đợi listActiveEnemies.Count0
&& Playing1; sau đó normal dùng GetMissionCompleted(killCount,countEnemies)>=0,
còncheckplayer; không auto-win/không hardcodekill100%. Wait2scaled s→manager
cleanup/stateEndgame→MoveOutPlayer→closurebool→OpenBoardVictory.
Next: đúngprefabWave0164/0113/0005→Call_Data/Spawner counts/timing; liveenemylist
add/remove và missionthresholds. Raw mới nhiều spawn implementations sẵn để nối.

## Agent hiện tại — report54, exact early-wave resource joins

- Đã resolve14 container entries từ APK pinned, giữ full trees + raw component
  bytes ở `reverse-engineering/raw/early-waves/`. Đúng default roots0164→148604,
  0113→21468,0005→38187 trong resources.assets; Chapter2/branch là roots khác.
- Report54 + verifier19 checks;48 tests pass. Slot cấu hình không marker:
  274/95/155, **không phải kill denominator hoặc observed enemy counts**.
- Không dùng `datas/waves.json` nhóm theo tên hoặc enum5/6 cũ. Không resolve
  generated typetree m_Script header; class exporter đọc parsed Mono head.
- Premium tiếp tục deferred. Agent đang tự nối GP_Datas event78/79 và
  Enemy_Destroy/pooling với mission thresholds, không cần chờ screenshot.

## Agent hiện tại — report55, pool-list và mission arrays

- Đã nối GP_Datas.ResetAlls: event78→Contains/Add listActiveEnemies+70;
  event79→Contains/Remove; event19→death callback có killCount+1c increment.
- Base Enemy_Controller movement-complete→DestroyType2→Enemy_Destroy.Pool→79:
  active-list rỗng không chứng minh diệt hết. Virtual override vẫn chưa join.
- Decode3 normal mission arrays bằng relocation→field-default12bytes, SHA256
  khớp hash field: mode0=.20/.45/.80;1=.35/.60/.98;other=.50/.80/1.
  Caller Stage_Datas.ModeCurrent+34, result−1..2, truncate float32 product.
- Raw `enemy-exit-missions.json.gz`,15methods12checks; toàn bộ52 tests pass.
- Next tự đào: Stage_Get_Datas.GetCountEnemies12c5f60 load resource/Call_Data,
  skip marker5, IPooling-ID filter; nối store GP_Datas+58 + filter membership
  và concrete Enemy_Destroy subclasses. Không dùng274/250 slots làm denominator.

## Agent hiện tại — report56: denominator và concrete destroy đã nối

- Raw mới: `early-waves/default-enemy-components.json.gz`14 exact roots, full
  root components/raw Mono bytes; Sub_Object.GetID recovered40185361444.
- MapController.Start132a5ec→GetCountEnemies12c5f60,132a5f4→GP_Datas+58.
- Filter là Stage_Get_Datas.listIgroneEnemies+18,31 cctor literal IDs; KHÔNG
  dùng Enemy_Data_Balance.listStaticEmemies thay thế. Chỉ38001 giao14 roots.
- Default chapter0 denominators: wave0164=262 (274−12),0113=87 (95−8),
  0005=151 (155−4); stage2=262/stage3=238. Native skip5, không skip6;6 arrayrỗng.
- Mode0 tier result0/1/2 thresholds:52/117/209 và47/107/190. Không gọi thắng
  ngay hoặc tự đổi sang UI stars. Mode1/other giữ riêng trong raw/report.
-14 Enemy_Controller.destroyScript PPtrs đều trỏ base Enemy_Destroy cùng root;
  đã cross-check ID/critical PPtrs bằng bytes, không resolve generated m_Script.
- `mission-denominators.json.gz`:4methods11checks;57 tests pass.
- Tiếp raw join result GetMissionCompleted→star UI/save + victory/unlock/Continue,
  và movement-completion callback registration/timing. Premium vẫn deferred.

## Agent hiện tại — report57: mission UI / saved stars / Continue

- Đúng `boards/board_endgame` root113205/resources.assets;1070nodes, Board
  component621494.3 normal Stage_Mission components648536/636132/696150;
  BtnContinue92306 persistent call→this board.OnPressedButtonContinue.
- Native Stage_Mission/GameDatas40185724759; prefab retry40185845817success.
- Ordinary LevelCurrent0: savedStars>rowIndex for old flags; result+1 saves
  only if more than prior completed rows; only NEW rows add GameDatas.StarCount.
  Keys StarStageMaster{stage}_{mode}, StarCount→Unity PlayerPrefs.SetInt;
  disk flush not proven. Replay3stars with result0 retains3/no new global stars.
- Animator triggers None/Collected/Clear, NOT SetBool.3 mission rows confirmed,
  not yet3 graphical star icons or clip durations.
- RunMissions new-row clear/reward→WaitForSecondsRealtime(0.5), includinglast;
  Continue→isQuitingtrue→SkipUnbox→StopAllCoroutines→settle remaining rows.
- IMPORTANT: GP_Endgame.OpenBoardVictory target++block14f08f4..14f09b4 has
  mode/target/cap guards but no read/test incomingvictoryw20. Do not restate
  “victory-only unlock”. Runtime defeat reachability still unproven.
- Raw endgame-missions/mission-progress-flow.json.gz18methods16checks;
  full63tests pass. Premium remains deferred.
- Next raw joins: movement-completion wiring/timing; target-advance defeat
  reachability; actual Continue visibility gates/Animator clips (without Premium).

## Agent hiện tại — report58: conditional false result reaches target++

- GP_Manager.<Start>b__11_7→StartCheckEndgame; `_endgame` callback metadata
  resolves14f6190→stateEndgame3. CheckEndgame gate active-listempty&&Playing1.
- Normal GameMode0/IsBranchfalse: kill result>=0 sets closure.victory;
  IHealth interface slot1=GetCurrentHealth()==0 forcesfalse. IPlayer slot0
  SetVictory() call is NOT evidence that closure bool is overwritten true.
- Join regardless bool→display.SetEndgame(bool)→2s SCALED→_endgame action→
  MoveOutPlayer(same closure callback)→OpenBoardVictory(bool). Distinguish
  force-VictoryNow callback which passes literaltrue.
- Exact MovePlayer dispatch recovery40186449228→755480732: bytes00162d8d at
  77a13a, base14f1c00; states0/1/2/3→1c00/1c58/1cb4/1e34.
  Move-out starts4sREALTIMEwatchdog before1sSCALEDwait. Watchdog invokes same
  callback then stops move handle. World movement y−2 then y15;0.3/0.5 are
  speed-accumulator increments per frame, NOT seconds; squared-distance1e−10.
- Target++ has GameMode0/stage==target/zonecap guards regardless incomingbool.
  Setter ADDITIONALLY clamps min(value,MAX_STAGE_INDEX), writes cache+3c and
  PlayerPreferences.SetInt("StageTarget"). No durable flush proof.
- False-input STATIC witness now connected to target-advance path, stronger
  than report57's local absence-of-guard. Still NOT a runtime defeat-unlock
  replay; assumptions: valid components, stable inputs/getters, live owner,
  external interface/event handlers don't prevent callback completion.
  Not mid-wave death/reborn; don't generalize to all defeat/Premium flows.
-15method bodies21checks in raw/endgame-missions/false-result-reachability.json.gz;
  source hashes for gzip use DECOMPRESSED bytes (timestamps are not game data).
  72tests pass. Next: actual Enemy_Movement completion/counter reachability,
  Continue visibility and Animator graph. Premium still deferred.

## Review nhánh spec theo yêu cầu người dùng — snapshot25c367aca

Đọc **docs/HANDOFF_SPEC_REVIEW_25c367aca.md** trước khi viết tiếp design.
Pin peer25c367aca99f06f14df546d2f30e60b427827157, đối chiếu data61fce8ae7.
Raw `peer-review/spec-25c367aca.json.gz` giữ9file/code/CSV + classifier experiment;
collector `tools/verify/peer_spec_review.py`,76tests pass.

- R1/P0: MISSIONS_STARS sai fallbackmode, thiếu arrays đã resolve; getter stars
  lưu bị nghi là tính kills. Dùng raw55–58, scope normal LevelCurrent0.
- R2/P0: ENCOUNTERS còn khuyên divide2/dedup theo tên. Rút lời khuyên; dùng
  container key/file/root pathID, không gộp normal với Chapter2.
- R3/P1:116 atlas name-unmatched không chứng minh116 sheet chưa tách; suffix
 5x2/2x3 không chứng minh crop16ô chắc chắn. T9 rect/atlas là gap THẬT, data nhận.
- R4/P1: CodaR22 bịR14 bắt trước (CSV4rowui/A); XVideoR23 bịR18 bắt trước;
 643 retained labels được cấpA vô điều kiện, không có provenance audit mới.
- R5/P1: readiness D3 vừapartial vừaclosed ở hai đoạn cùngfile.
- R6/P1: parser exception→SKIP/exit0; AB1 không đo67rect, AB4 chỉđếm CSV nên
  PASS không chứng minh semantic mapping. Thêm strict-required, không bỏref-first.

Nhánh spec sửa trên nhánh của họ; không merge/push thay nhánh spec. Mọi kết
luận vẫn provisional. Premium deferred; không dùng screenshot làm nguồn số.

## Agent hiện tại — report59: concrete movement end → pool (không phải kill)

- Recovery40187130445→12280632a có Enemy_Movement/VertexPath full native.
-14 enemy root referenced trong exact early waves đều Controller PPtr→base
  Enemy_Movement/Enemy_Appear/Enemy_Destroy; verify critical joins bằng Mono
  bytes. Tất cả typeMoveEnded0Destroy/endInstruction2Stop/persistent-eventempty.
- Controller.OnEnable→Appear gắn OnMoveCompleted1584778 qua slot2aec4d8;
  baseAppear gọi Appeared1584868 ngay→movingtrue. SetEventMoveEnded resetold
  delegate, self-stop+UnityEvent rồi appendcontroller chỉ khi mode0&&nonnull.
- PathFollow speed×deltaTime→VertexPath.GetPointAtDistance: normalize length,
  Stopclamp; callback cần finalinterpolation==1 && endpointdistance²<1e−10.
  PointToPoint cuối segment gọi cùng onEnded. Turretmovingtrue worldy<−15
  cũng gọi; Linearly cầnmoveintrue và vượt borderx±10/y±15.
- DestroyWhenDone2 BỎQUA death/hit handlers rồi Pool→event79→Contains/Remove
  active-list; KHÔNG tự chèn Enemy_Destroy.OnMoveCompleted hook vào CFG.
  Pool path không phát kill19; external listener effects vẫn chưa replay.
- Slots exact0164:Path150/Way104/Pin19/AirFree1=274;
 0113:PointToPoint80/Pin15=95;0005:Path140/Pin15=155. Không phải actualspawns/kills.
- AirFree BB-36001 córootAnimator, khôngturret, spawnerchỉITransform.SetAngle/
  SetPosition; CHƯA gánpath/waypoint ở bodyđó. Không suy tựpool hayphảibắn.
- Parser phát hiện2 ITransform trùngtên: globalTypeDef228 là3methods game;
  UIElementsTypeDef4428 làpropertiesUI. Giữnamespacekeys+testcollision, tránh
  nhầmglobal interface slot0/1 thànhget_position/set_position củaUI.
- Rawearly-waves/movement-completion.json.gz28methods20checks/14joins;
 84tests pass. Low-kill witness58 mạnhhơnnhưng vẫnstaticconditional, khôngreplay.
- Tiếp tự đào BB-36001Animator/controller/clips/events và terrainparent/scroll;
  T9assetrect/texture/rotation/trim vẫn taskraw nhận từspec. Premiumdeferred.

## Agent hiện tại — report60: BB-36001 streamed animation (provisional)

- CI40187741686→192d2290f: raw `balloon-animation/bb-36001-animation.json.gz`,
  exact root185704/Animator496390/controller1908;37nodes/full3clips+bytesSHA.
- `tools/verify/balloon_animation.py`→`decoded-clips.json.gz`:3clips17checks,
  giữframes/coeff/keyoffset/bindings/targets. Formatref AssetStudio pinned
  d158e864b556b5970709c2a52e47944d53aa98a2 +MIT giữ riêngtoolchain;khônggamefacts.
- Graph defaultSpawn1468(2.5)→Idle1467(10)↔Attack11466(12),speed1,
  exitTime1/duration0/no conditions;no params/AnyState/behaviours/events.
- QUANTRỌNG: **cả3clip animate root-local position** path0/attr1/Transform4.
  Animator.applyRootMotionfalse KHÔNG phủđịnh ordinary localtransform animation.
  Spawn(-12.41,7.33)→(-3.66,2.3);Idle ends(-3.77,6.04)=Attackstart;
  Attackend(-3.66,2.3)=Idlestart. Đây làkeyvalues,khôngworld/runtimebounds.
- 12/15/12streamedchannels;9/66/76frames kểsentinels;0dense;Attack3constant
  rootEulerzero. Firsttime−FLT_MAX không−inf;last+inf0keys. Khôngdecode dense.
- CRCm_Enabled3305885265: Barrels1MachineGun690037/Barrels2639146/script1:338
  resolve bằngrawMonoheader,KHÔNG lệchtypetreem_Script. Spawn2súngoff;
  IdleBarrels1on@0/off@9;AttackBarrels2on@0/off@10. Collider490394off@0Spawn,
  on@2.5Spawn/onIdleAttack. Enabledkey≠đãchứngminhshotcount/damage.
-9duplicatePointpaths giữlistkhôngoverwrite;mọibindingđangxétuniquetarget.
- Khôngterminalflyaway/poolstate/events/GameObjectbinding trong3clip; KHÔNG suy
  BBphảibắn/tựpool. Root-localkeys≠worldcubicbounds;parent/update-order/movein
  gates59 cònthiếu. Khôngnângconditional lowkillwitness thànhreachableplaythrough.
- Tiếp tựđào AirFree spawn-parent/terrain-scroll và Machine_Gun_Attack lifecycle;
  T9atlasrect cònrawtask;Premiumdeferred. Chi tiết report60,8tests mới.

## Agent hiện tại — report61: pool-parent/scroll/gun lifecycle (provisional)

- User yêu cầu tự làm tiếp cho đầy đủ, không cần hỏi từng bước. Đã chạy native
  recovery40188073425→c0ffce078: PoolingManager/Machine_Gun_Attack/
  Boss_BodyPhysics/Obj_Collider/Enemy_Datas fullasm+JSON; khôngbinary/APK.
- `tools/verify/balloon_lifecycle.py` + rawballoon-animation/
  lifecycle-parent-scroll.json.gz:40methods26checks,8tests mới/**100tests pass**.
  SHA gzip theo DECOMPRESSEDbytes;declarations namespacequalified.
- Pool getObject123a2c8:reuse list[0]/RemoveAt0 hoặc instantiateinactive,
  common worldposition+rotation, KHÔNG directSetParent/detach. GetObject(int)
  dùngposition(-255,-255,-255);ctorprefPos(-99,-99,-99),khônggameplayborder.
- Pool return123a66c:deactivate trước;nhánhvalidID/notContains/existingobjects
  SetParent(manager.transform)123a970 rồiappendlist. Guarded,khôngmọicall.
  Vìgetkhôngdetach,assetrootFather0 KHÔNGchứngminh reusedruntimeparent0.
- AirFreekhôngdirectreparent;PinMap→spawner.transform.parent1466b60;
  PinTerrain→serializedparentTerrains+30 tại1467154 (KHÔNGraycast/tựsuyMaplayer).
- MapControllerAwake lấyallMoveLayers[1]→enemyParentMove,RemoveAt1.
  UpdatebranchScrollMaptrực tiếp;commonDelta=multipleSpeed*deltaTime;
  allMoveLayers.localY-=delta*speed*boostSpeed;
  enemyParentMove.localY-=delta*speed CHỈisMoveEnemyLayertrue,KHÔNGboostfactor.
  ScrollBackgroundswrap worldY<−1.5*bgLength→+bgLength*countBg;khôngenemyPool.
  IsScrollingcómethodnhưngkhôngtựchènvàoUpdate/ScrollMapvìkhôngcallởbodyđãđọc.
- Gun exact690037normalbRate0/shotRate.15/speed8;639146barrelbRate.1/
  shotRate0/speed6;bothdelay1/Border0/turnRate2/turnNumber3/id80054/lifetime5/
  damage300serialized/allGunDatas[]/bltPinMapfalse/emptyturneventpersistent.
- GunOnEnabletimeToShot=Time.time+delay,resettimeToTurn/countTurn,bCount,
  inverse,stun;KHÔNGresetisTurnStarted/timeToBarrelShot/timeToStart.
  FixedUpdateisAttack→Border/Timer gate→stun→Shoot;khôngcoroutine.
  NoOnDisabledeclared;animationdisabled≠OnEndTurnShoot/death/remove.
  TurnhooksUnityEventkhôngownerpool;runtime listeners/actualshotschưareplay.
- EnemyMovementOnEnable1586024 chỉzFixed48,khôngresettypeMove/path.
  PathFollowpathnullreturn. Conditionalmovingtrue/typeMovePath0/pathnull/
  nonturret→khôngpathcallbackhayFixedUpdateboundaryroute,ngaycảanimationraxa.
  KHÔNGchứngminhstateđónắmgiữmọiruntimeBB;poolhistory/writerscònthiếu.
- Đọc report61 trước khi chốt stage2lowkill. Không được suy rootlocal=world,
  mọiAirFreeautoescape,hoặcBBmustdie. Kếtiếp:exactmapjoin+poolinstancehistory,
  typeMove/pathwritersvàexternalremoval/health/collision. T9atlasrect vẫnrawtask
  riêng;Premiumdeferred. Nhữnggapruntimekhôngđượcđóngbằng100unitPASS.

## Agent hiện tại — report62: audit raw + T9 geometry recovery

- User yêu cầu kiểm thừa/thiếu phần dịch ngược rồi tự đào. Report62 là audit,
  KHÔNGđóngtoàngame. `docs/conclusions.md` thêmregistryưu tiên,mark17/18/13d/
  16b/21bcũrút/giớihạn:enumspawn0PinMap1Path2Points3Random4Rocket5EndMap6StartWave;
 45,659"quânthậtchốt"KHÔNGđượcdùng;missingparam≠mọitàuHPgiốngnhau.
- Rawprocess-audit/scope-inventory.json.gz:55584UIgztrênđĩa,157576919compressed
  bytes;index797file/117class/150131nodes,54787ngoàiindex,0missing. **KHÔNG**
  kếtluậnngoàiindex=duplicate/rác;khôngxoárawchưaprovenance/semanticcompare.
- Fullanalyze trướcchỉinSHA,cachemissURLlatest cóthểmixbuild: naySHAstrictfail
  trướcextract. Earlywaveexporterloạikhỏifullanalyzetrigger;config-onlyfullrun
  dùngmanualdispatch;raw/il2cppedittriggerverify. Hai recoveryproducer chạy
  unittesttrướcbotcommit vì[skipci]/GITHUB_TOKENkhôngbảođảmtriggerverifyriêng.
- T9GAPTHẬT đãđào:CI40188735212→d97399106;tools/apk-probe/sprite_geometry.py
  giữ6chunksfullSprite/Atlas,Texturemetadata/noimage;counts2185/66/654,0error.
  inputsdataSHA7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7.
- `tools/verify/sprite_geometry.py`→rawsprite-geometry/resolved-geometry.json.gz:
 2185/2185file-scopedPPtrjoins;635m_RDdirect/1550Atlaspointer+exactrenderkey,
 0unresolved. No atlasnameguesses/globalpathID. Rawhasrect/offset/pivot/PPU/
  border/mesh/UV/settings;toolchainUnityPy1.25.4wheelref+MITseparatefromgamefacts.
- Settingsrotation0:2041,1flipH:53,2flipV:54,3rot180:37,4rot90:0;144nonzero.
 40directRDrectboundsfractionaloutby~1.9e−6..0.9963px;giữnguyênkhôngclamp,
  KHÔNGnói40spritehỏng. T9metadatajoinđãcó≠pixelcrop/trim/maskđãvalidated.
-7geometry+3process tests mới,**110tests pass**. Fullpackreleaseintegrity/audio/
  spine/fonts/browsabilitychưaauditlạitrongvòngnày. ChưađedupUI,chưarenderảnh.
- Tiếpưu tiênstage2/3BBwriters/liveparent/history/removal;T9pixelcrop/mask/
  packing40fractionalcaseslàbướcassettiếp. Đừngbóclạidanhmụcđếmcountschođẹp,
  khôngfullAPKexportvìtargetedcollector,khôngchốtgameplaytừunittestPASS.
  Premiumdeferred. Report62vàregistrymớilàentrypointchứkhôngbảngkếtluậncũ.
- Bổ sungauditCI:40189044132/44102/44138fail; signedlogsEOF. Tái lậpcleanarchive
  phát hiệnpeer_spec_reviewtestphụthuộcgitshowpeerSHAkhôngcóởshallowcheckout.
  Đãsửadefaultđọc9inputgốctrongrawsnapshot,khóacanonicalSHA b9325a6cc3a2fb394b3a0ba37eadeef57e0438be1d972aaee30e3e8be709ece0;
  experimentsvẫntínhtừinputtext,khôngdùngprosekếtluận. --from-gitoptional.
  TestcấmsubprocessGitdefault,111testspasscảworkspacevàarchivekhông.git.
- CI saufixđềusuccess:Verify40189296572/geometry40189296654/native40189296604;
  producerregressionpass,tránhfullanalyze. Local+cleanarchive111PASS.

## Agent hiện tại — report63: movement state writers/reuse contracts

- Không rerunAPK vìđủraw; `tools/verify/movement_state_writers.py`→
  rawballoon-animation/movement-state-writers.json.gz:21EnemyMovementmethods,
 9checks+5Subsetterbodies+sourceSHA. Scannerlinearthis-aliasstoreHINTS,
 KHÔNGCFG/whole-nativewriterclosure;testtránhstack4C/callerclobber/wordalias.
- Trongclassđãđọc:typeMove4CwritersSetPathFollower0/SetWaypoints1/
 SetMoveLinearly2/RocketResumeMove2;path50storechỉSetPathFollower.
- EnablechỉzFixed48;Stop/Startchỉmoving;separateSetPosition/Anglekhôngdirect
 resetmode/path/movein;combinedSetPositionAndAngleclear5C/D0. AirFreedùng
 separatenênKHÔNGgộpthànhcombinedlúctáidựngvìthayđổifieldeffects.
- Pháthiệnmới:SetWaypointsnonnulllen<2ghiMode1/distance0TRƯỚClog-return,
 chưaoverwritewaypoints60/index/cache;khôngno-op,oldstatecóthểcònlại.
 Nullinputexceptionkhôngđượcmôhìnhtựsetupthànhcông.
- ExactAirFreerefduynhất3earlywaves:0164/w15/Boss_2/CallData599908→
 resources.assets185704BB. CallDataspawnType0nhưngconcretespawnerAirFree;
 khôngphânloạichỉtheoenum/nodename. KhôngnewclaimBBmustdie/autoescape.
- ModelreusepriorMode2/pathold/moveintrueCHỈconditionalfieldcontract,
 khôngchứngminhactualBBhistory/reachableplaythrough. SetActivecallbackorder,
 externalwriters/parentmatrix/alternatehealth-removalchưakhép.
-8testsmới,**119tests pass**local. Report63entrypointmovementcontracts;
 T9pixelcrop/mask40fractionalrectcònmở;Premiumdeferred.

## Điều chỉnh ưu tiên theo người dùng — đọc kịch bản, không cố chứng minh playthrough

Người dùng nhắc: “xem kịch bản là biết ngay, số địch diệt và player còn sống
chứ không cần cố chứng minh”. Áp dụng từ đây:
- Đọc kịch bản stage/wave và luồng kết quả theo số địch diệt + trạng thái player
  còn sống; dùng denominator/threshold và điều kiện health đã bóc khi mô tả.
- Dừng đào pool history/live parent/writer closure chỉ để chứng minh tồn tại một
  low-kill playthrough hoặc tranh luận BB bắt buộc chết/tự thoát. Không lấy các
  gap chứng minh đó làm blocker cho mô tả hay dựng kịch bản.
- Giữ raw/report59–63 làm tham chiếu; không xoá hoặc đổi chúng thành bằng chứng
  runtime. Chỉ đào lifecycle thêm nếu có mâu thuẫn cụ thể ảnh hưởng kịch bản.
- Các bước tiếp tập trung thiếu dữ liệu triển khai thật (kịch bản, UI, assets),
  không lặp audit mang tính chứng minh vượt nhu cầu. Premium vẫn để sau.

## Report 64 — ưu tiên hiện tại đã kiểm lại: tutorial riêng, victory chung
- Đọc raw APK và giữ snapshot `raw/endgame-missions/shared-stage-victory.json.gz`: 21 method, 19 checks; collector `tools/verify/shared_stage_victory.py`, 4 test mới; tổng 123 tests PASS.
- Stage1 gate stageIndex0/tutorialIndex0; Stage2 1/1; Stage3 stageIndex2/!touchDone (không gate tutorialIndex2). Khác biệt gate/overlay/Continue không được mô hình hóa thành ba victory system riêng.
- Campaign normal/nonbranch: manager callback → shared CheckEndgame (kills/mission + health) → MoveOutPlayer → OpenBoardVictory(bool) → Board_Endgame.Init/SetMissions chung, gồm ba opening stage. `VictoryNow` ép true nhưng cũng về cùng board; không nói mọi entry phải tính kill trước.
- Board SetupTut <=1 và ThroughTut thay đổi UI/index; Continue routing còn guard. Không khẳng định mọi mode/giao diện/reward giống hệt nhau. Kết luận tạm từ static raw, không cần pool-history/playthrough proof.

## Cập nhật review peer + bàn giao AI viết game mới — sau report64
- Fetch tường minh peer cho ra cf27b97553ef25107b45b039f316d9ca7850a885 (fetch origin mặc định trước đó vẫn giữ ref25 cũ). Đã ghi nhận R1–R6 được sửa; không tái báo chúng như lỗi hiện hành.
- Review mới: `docs/HANDOFF_REVIEW_cf27b9755.md`. N1 stale map blocker; N2 ship damage/HP suy từ thiếu field; N3 JPEG metrics/bbox population bị nâng thành luật đẹp; N4 sample/default→whole-game rules; N5 save0/stale tutorial/result handoff. Phân biệt invalid inference với kết luận chắc game có/không có tính năng.
- Cửa vào hiện hành: `docs/START_HERE_NEW_GAME.md`. README, spec local README và các tài liệu lịch sử đã có chỉ dẫn; conclusions bỏ low-kill history làm blocker. Không có game project chạy được ở repo này, chưa tự chốt engine/platform/art.
- Raw giữ15 input peer nguyên văn+SHA và5 input local (native body/map/save/shared-victory/geometry) trong raw/peer-review/*cf27b9755*.json.gz. Collector hermetic `peer_handoff_review.py`,16checks; 4test mới. Tổng127testsPASS; datas/validate PASS. Peer tests chỉ được đọc tĩnh, không báo đã chạy chúng.
- Sửa lệnh nối ZIP phá input trong README và template release của workflow; không chạy full analyze hay publish release. API xác nhận asset release còn draft/có4file; chưa download/extract/integrity toàn pack.
- Tiếp: peer sửa N1–N5; full-pack/crop/browsability; agent implement đọc contract rồi chốt scope/engine với user. Premium deferred, không speculative pool-history detour.


## Report65 — dữ liệu triển khai save mở đầu, không chỉ review spec
- `datas/opening_persistence.json`:8keyfamilies typed/default/cache/read-write effect/method IDs/store + raw hash. Format schema_version1 KHÔNG phải version save APK.
- `raw/persistence/opening-contracts.json.gz`:41method ASM/inventory không capped + metadata/relocation strings/direct calls/dump fields/source hashes,25checks. Collector `tools/verify/opening_persistence.py`,8tests mới; tổng135testsPASS, data validatePASS. Không rerunAPK/Premium.
- Keys: TUTORIAL/TUT_TOUCH_SKILL/StageTarget/ZoneUnlocked/StarStageMaster{stage}_{mode}/StarCount/DroneUsed{slot}/DroneUnlocked{drone}. Backend default0 chỉ scope company!=Test; đây không có nghĩa mọi getter trả0 hoặc thuần đọc.
- StageTarget getter cache hit/miss đều có nhánh zone<MAX_ZONE_INDEX && target<zone*10→tăng1/lưu qua upper-capped setter mỗi lần đọc, không loop/clamp ngay tới zone*10. IndexTutorial đọc StageTarget; target>=2 && tutorial0→ghi6. Không gọi logging/serializer getter như pure read.
- Touch flag stored==1 mới done. Callback b__1 ghi flag1 trước, chỉ tăng index nếu IndexTutorial2 && StageCurrent2; không đổi gate stage3 thành tutorialIndex2.
- DroneUsed âm→ghi0/reread; missing0 không autoequip20001. IsDroneUnlocked20001 tựghi1 nếu0; ID>=20002 stored==1; invalid lowerIDs true trong native không chứng minh roster hợp lệ. Keep fallback Continue riêng.
- Typed Set/Get Int/Float/String→Unity PlayerPrefs; SetValue/GetValue→dictionary static riêng→JSON/Encrypt/ASCII/file persistentDataPath+/Prefs. SaveToDisk/focus/quit custom không có direct Unity Save trong3body đã đọc, không chứng minh flush mọi prefs/toàn game không flush.
- DeleteKey chỉUnity; DeleteAll clearUnity+dict+customSave nhưng thân đó không invalidate progression caches. RefreshDatas chỉcache−1, không resetprofile. Caller/runtime/cloud/migration chưa audit đủ.
- Entry START_HERE, conclusions, datasREADME đã nối report65. Tiếp bóc ship/equip/talent/audio/save còn thiếu theo nhu cầu implement; fullassetpack/crop/browsability vẫn mở. Không speculative BB-history và Premium.


## Report66 — ship save/loadout và tech/talent consumer, hiện hành
- Report `apk-analysis/66-player-loadout-save-rank-trial-tech-consumers.md`; `datas/player_loadout_persistence.json`:15keyfamilies, exact defaults/type/method refs; raw `player-loadout/contracts.json.gz`:33methods/43checks. 10tests mới +3recoverytests; tổng148PASS. Các con số là static checks, không replay.
- Hai lớp Player_Saved_Datas/Player_Device_Saved_Datas được recover riêng từ cached XAPK/native/metadata đã pin hash: CI40192146035success. Raw ASM+JSON/index/metadata array blobs giữ đủ, không commit original binary/full assets.
- PlayerUsed slot0default10001/other10002; missing không write. Stored<=0 reset CẢ PlayerUsed0/1 rồi reread. SetPlayerUsed không tự check unlock/duplicate hay flush loadout cache. CheckDoubleIDShip là routine riêng, khi trùng tìm ship unlocked khác để đổi slot0.
- Base PLAYER_RANK default2/repair<=1 trước trial flag; TRIAL_ID_==1 chọn TRIAL_RANK_/TRIAL_LEVEL_ default0. Không gộp getter với loader floor2. Rank arrays metadata-backed MaxLevel=[10,20,30,60,120,250,500], Cards=[0,20,50,80,250,500,800], StartRanks=[2]*24, MAX_RANK_INDEX6; không suy full payment flow/cap enforcement.
- GP_Setup cached two-slot array -> GP_Loader rank/unlock/skin consumer. Tech wrapper mode4 AND sceneGame trả0; device wrapper trả[-1]*4, không xóa saved. TALENT_SELECTED default−1, startup callback cần StageTarget>=Board_Begin.stageUnlockTalents + mode!=4; numeric threshold còn mở. Stat5 rocket count6..8=>3 giữ nguyên, không sửa monotonic.
- **Task peer** nhánh arena/20330d0e-windwings-space-shooter-game-p: cập nhật spec save/loadout theo report65–66, phân biệt saved/trial/effective/cached, exact1 flags và getter write-on-read. Giữ trial expiry/full upgrade lifecycle là unknown; nếu thêm validation/atomicity hay sửa branch thì ghi new design. Không dùng snapshot spec cũ làm bằng chứng APK.
- Tiếp audio trigger/rules và full pack sprite/audio/spine/font browsing/validation. Premium, speculative BB pool history vẫn không phải task/blocker.


## Report67–68 — audio rules và asset-pack audit, hiện hành
- Audio `datas/audio_rules.json` + raw/audio-rules/contracts.json.gz:65method không capped/25checks/15rules,118enum names/92registry rows/69legacyPPtr pairs. Source recovery40192970188success; overload method refs có RVA, không collapse GetAudioSource/get_Current.
- MUTE_AUDIO missing0 exact1; VolumeSound≈0.73/VolumeMusic≈0.3, mute getters trả0; mute setter body chỉ persist, Pause→AudioListener.pause. Music ignoreListenerPause=true; fade≈.01 mỗi coroutine iteration/yieldnull, không duration cố định. Game playlist33..36, realtime(length−2)/None/realtime2, reroll previous; không tự thêm Bgm_Game5. Endgame.MovePlayer Sfx_Flying26, không mặc định Victory27.
- Draft asset audit40193251582success, raw/asset-pack/{catalog.json.gz,manifest-full.csv}. ReleaseID421174835 vẫn draft; hashes/digests+CRC PASS, nhưng **151 collision paths/321extra manifest rows/320size mismatches**. Sprite archive1903 vs manifest2185;Texture614 vs653. Producer export_assets reset used=set mỗi object. Không gọi full pack đủ.
- Browser docs/assets/pack-browser.html offline metadata-only; cần copy cạnh media đã giải nén. Hiển thị identity ambiguous; fullmedia không trongGit. Fonts actual1TTF ≠ toàn game1font;26skeletonJSON/27atlas presence ≠ binding xong.
- Tổng162testsPASS (8audio/recovery +6packtools/catalog mới), data validatePASS. Numeric float pool là rounded approximation, không bit-pattern proof. Registry/export filename mapping chỉ legacy PPtr/pathID candidate do thiếu serialized-file identity.
- **Task tiếp agent extraction:** narrow identity-safe asset re-export từ cached original: serialized-file+type+pathID filenames, population check/no silent skip, versioned new draft assets không clobber originals, rig/atlas-page joins/crop/listening kiểm riêng. Không full APK pipeline. Chưa hoàn tất task này ở report68.
- **Task peer** nhánh arena/20330d0e-windwings-space-shooter-game-p: đưa rules report67 vào spec với scope/refs; ghi pack completeness FAIL từ report68, không lấy basename collision làm image metric của nhiều object. Không đảo static facts thành runtime approval; Premium/BB-history vẫn hoãn.

## Report69 — peer không phải chờ dump Map/Player blob nữa
- Peer pin `cfc0197f691f4623294b5ec65195923aa738e397` đã có `il2cpp/ia-resolved.json`: Map cctor576 + Player cctor6, hai nhóm exact record/raw equality với extraction branch; fingerprint tại raw/initialize-arrays/peer-comparison.json.
- Deliverable `raw/initialize-arrays/typed-inventory.json.gz`, collector `tools/verify/initialize_array_inventory.py`: raw giữ nguyên, Map int32 view chưa bind container/index; Player sáu field đã bind native stores+dump types. 1int[24]+3float[24]+2float[3], không phải4float[24]. Decode len elements, giữ alignment tail, không đọc ints float bits thành giá trị damage.
- **Task peer:** bỏ blocker “chờ573+6 raw”; đọc report69 rồi bind Map call→container→index qua native cctor/consumer, đối chiếu datas maps/segments đã có. Không tự trừ3 opening literal arrays khỏi576InitializeArray; không quy sốcall thành stagecount. Player index→ship/consumer/formula vẫn cần scope đúng trước DPS/TTK.
- 167tests + datas validation PASS local. Không khẳng định L2/gameplay equivalence đã đóng. Asset identity-safe re-export của report68 vẫn chưa làm; Premium/pool-history không phải blocker.

## Report70 — identity-safe pack v2 đã xuất và audit độc lập
- Recovery40194721870 + independent-audit40194948219 success. Draft release421174835 thêm `assets-v2.zip` (175684102B,ID675035745,SHA4b18cc23b9d71d095dbe8be4458a8ca95fe1d16f5bc0c96bb2329c7bc5de3506) +sha sidecar; không overwrite bốn asset v1, vẫn draft.
- raw/asset-pack-v2/{catalog.json.gz,release-upload.json,archive-audit.json.gz,font-texture-exception.json}; browser docs/assets/pack-browser-v2.html, ZIP cóindex.html offline. Source3039objects six types→3038outputs:2185Sprite/653Texture/69WAV/64Text/1TTF/66SpriteAtlasJSON. SHA/size/CRC/exactpopulation/2838PNG full decode PASS.
- Exception duy nhất resources.assets Texture2D535 Font Texture:0×0,CompleteImageSize0,image data[],stream0/0/empty. Có raw; không invent PNG/không suy runtime font generation. all_target_objects_exported giữfalse; không gọi toàn game đủfont/fidelity.
- 27skeletonJSON/27atlastext/10other theo content;27page names đều nhiều Texture name candidates (26pages×26candidate,1page×2), không identity join. Sprite directtexture null1550 nhưng atlas pointer resolved1550;635directtexture resolved. Không suy null là mất sprite.
- **Task peer:** chuyển tham chiếu pack sangv2/manifest-v2.json theo serialized-file+type+pathID; đừng dùng path_id global hoặc v1basename/preview metrics làm luật. ZIPv2 thường, không nối partv1; giải nén ngoàiGit/mởindex.html. Đây là reference, chưa Spine import-ready vì sourcepage paths chưa rewrite.
- **Task extraction tiếp:** Spine SkeletonDataAsset→AtlasAsset→Material→Texture identity joins rồi assembly/export riêng có provenance; crop/mask/fractional rect, listening và font fallback vẫn mở. Không full re-export lại để cố tạo ảnh cho texture0×0. Premium/BBpool-history vẫn hoãn.
- 180tests + datas validation PASS local; manual re-export workflow để không rerun/clobber evidence. Report70 có acceptance và phần chưa làm; final CI kiểm riêng.

## Report71 — Spine chains và reference folders hiện hành
- Raw `raw/spine-identity/`:167objects/168resolvedlinks;27SkeletonDataAsset/27SpineAtlasAsset/54TextAsset/29Material/27Texture/3shader metadata; selected roots được resolve bằng parsedMonoBehaviour header, không dùng generated tree.m_Script sai. Scan125453headers có1unknown resources.assets580792 thiếuunity default resources; giữclassificationfalse, không đòi đóng nó để làm27rigđãcó.
- `datas/spine_identity.json`, verifier `spine_chain_contracts.py`:27rig/27pages/185animationnames,15uncappednative methods/12checks. Loader0x222f580 tìmfirstmatchingtexturebasename CHỈtrong owningatlas materials; mainTexturefallback_MainTex, shaderskhôngMainTextureflag128. Không cònglobalbasenameambiguity cho27pageđãbind.
- **7atlas1024×1024→texture512×512** giữnguyên; nativeguardgiữparsednonzero dimensions. Không autoresize/fixcoordinates. 26skeletonheader3.8.99/1header3.8.84; scale≈.01all27; defaultMix26×.2/1×.5(Saw580615); transition580611 Attack1→Baydi≈.1. Root580647 additiveMat38/screenMat39 cùngTexture413, rawsettingsđủ; chưashader/PMA/render approval.
- Draft release421174835 thêm `spine-reference-v1.zip` **8057645B**,ID675073587,SHAfabc89bdad02b7a754c3b3ff593b6d21676f52503828200a6da35e0839e3e091.27folderđộc lập;81sourcecopies+27settings+manifest+README=110members. OriginalJSON/atlas/PNGv2giữnguyênbyte. rawreference-pack manifest/audit/release; releasevẫn draft, khôngclobberv1/v2.
- Recovery40196115012success;assembly40196217595success.191tests+datasvalidationPASSlocal, finalCIkiểmriêng. Manualassemblyworkflow sauassetcreationđểkhôngrerunđụngtêncũ. Cácfailure/rebase/headerexceptiontrướcgiữtrongreport71, khôngruntimeproof.
- **Task peer:** đọc report71 và importtypedjoins/settings đúngscope; khôngglobalpathID/namejoins, không tự dùngSpine4.x, không đánhđồngfolderreferencevớiruntime-ready. v2global atlasnamesambiguous đãcólocalidentitysolution, khôngtiếptụcđòidumptexturebasename.
- **Task extraction tiếp:** renderedPMA/blend/crop/fractionalrect audit và animation event/timeScale consumers cụ thể; font fallback/localization, ngheaudio. Khônginventfonttexture0×0/resize7atlas/đàoPremium hoặcBBpool-history.

## Report72 — Sprite pixel reproduction và fractional/pivot contract
- `raw/sprite-pixels/audit.json.gz`, auditor `tools/recovery/sprite_pixel_audit.py`;CI40196744366success,raw7d2436d66. Tải lạiauditedv2, compare2185SpritePNG bằngRGBA bytes với separate rawgeometry/owningTexturePNG crop+packedflip+floatposition/uint16triangle-mask reconstruction.2185match/0error;482texturePNGsused;Pillow12.0.0. KhôngUnityPy SpriteHelper/MeshHandler call trongauditor, nhưng môphỏng format-tool semantics, **khôngUnityGPU/render/PMA approval**.
-593fractional textureRects;40float-outside nhưng31roundedboxes trongbounds/9padding1pixel. Top8IDs2072/2099/2114/2134/2169/4006/4050/4085,right4092,đềuresources.assets/unpacked/rotation0. Khôngauto-clamp:9clampedboxsizekhácv2outputs. Raw/payload/hash/crop/alphabbox/differenceextrema giữđủ, originalpixels chỉrelease.
-517PNG output sizeskhácroundedsource_rect. `datas/sprite_export_contract.json.gz`/verifier `sprite_pixel_contracts.py`:2185typedidentity/sourcepivot/rect/trim+atlasoffset/ppu/exportsize/PNGhash/rawmeshref. Source normalizedpivot KHÔNGnormalizedexportPNGpivot, không center/registrationguess. AllobservedUV0zero→maskpath, rejectunreviewedlayout/nonzeroUV.
- **Task peer:** cập nhật40rectblockerthànhphânbiệt40float-outside/9padding; dùngtypedcontract, khôngsửaAtlas bounds hoặcreuse sourcepivot trêntrimPNG.2185matchchỉđóngconsistencycủaexportsemantics;UnityGPU/placement/PMA/shader vẫnunknown, khônggameplayapproval.
-202testsPASSlocalvencóPillow13 +datasvalidationPASS;pixelCI12success,finalCIkiểmriêng.VerifyCIcàipinnedPillow12đểkhôngskip2syntheticpixeltests. Report72 córawrefs/limits. Tiếpfontfallback/localization/audio hoặcconsumerplacementcụthể, khôngfullassetreexport/Premium/BB-history.


## Report73 — font fallback / localization / peer sync hiện hành
- Peerpin2d0a0e139 đãtypedPlayerstartingarrays/report69corrections; snapshot3docs+blobhashes ởraw/peer-review/update-2d0a0e139.json.gz, khôngAPKtruth/khôngmergewholesale. Khôngchờ573+6dump.
- Recovery40197895269+40198072388SUCCESS, raw61083ec31:125453MBheaders/1knownbuiltinexception,12296selectedobjects/0readerrors/0unresolvedlinks.34uncappednative methods,128bytesboundedSystemLanguage mappingtable.
- `datas/font_language_contract.json.gz`, `raw/font-language/`:7staticSDFfontassets main105→110→106→108→109→111→107,7typedv2atlasPNGs,2352glyphrows/2354characterrows/2285Unicodeunion. Globalfallbacklist[null] khôngnghĩanofallback. Sourcefontnull/mode0all7, khônggiảđịnhtựaddruntimeglyphs hoặc7TTFs;font535emptytexturekhôngphải7atlasesnày.
- 9797serializedtextcomponents:9796fontrefs→105,1nullresources699094;RTLflagfalseall9797khôngchứngminhArabicsuccess/failure.2442languagewrappers,19LanguageAssets×1426rows/1415nonemptykeys. NativeContains→IndexOf→listValue **firstoccurrence**, current→English→key, forceDefaultskipsselected.English`txt_free_after` corrected`Free after`, generatorraw-firstkhôngCSVlast-wins.
- SavedLanguage preference overridesApplication.systemLanguage map; English0defaultLanguagefallback khácinitialselection. NativegenericChinese6/Traditional41 defaultEnglish0, Simplified40→18, Vietnamese39→1; khôngtựgộpChinesevariants. Settercache→onChange→persistordergiữnguyên.
- Offline`docs/assets/font-browser.html`:copycạnhTexture2D/ trongextractedV2đểxemrawSDFatlases/metrics, khôngTMPshaderpreview. Originalmedia/draftreleasekhôngđổi, khôngđưaoriginalfontprograms/PNGvàoGit.212testsPASSlocalvencóPillow13+datasvalidatePASS, finalCIkiểmriêng.
- **Task peer** arena/20330d0e-windwings-space-shooter-game-p:importtypedfontchain/translationfirstIndex/defaultselectionfacts;refreshgap/assetssummariestheo67–73, khôngnângstaticUnicodeinventorydeltasthànhrenderedmissingglyphs. Nếuchọnfont/RTL/shaping/normalizationkhácAPK,ghi newdesign;SDFPNGkhôngphảiCSS@font-faceTTF. Premium/poolhistoryvẫnhoãn;tiếpconcreterender/placement/audiofollowups.

- **Report73 final CI:** Verify40198971054 SUCCESS trên3e7b143ab,212tests/pinnedPillow12; data validatePASS. Broad accidental run40198724717 CANCELLED, publishSKIPPED; partialbot8c9e0217c outputs restored, trace ởraw/font-language/workflow-scope-incident.json.gz. Analyze40198971219 SKIPPED theo scopedguard, draftmedia digests/IDs không đổi.


## Report74 — font reference ZIP tự chứa, delivery đã tải lại kiểm tra
- Peer vẫn2d0a0e139, không commit mới; extraction không merge spec. Gói mới chỉ dùng scopedraw/report73 và auditedV2, không fullAPK export.
- Draft421174835 thêm `font-reference-v1.zip`, asset675170630,1627375bytes,SHA1c20bda1b61d11bb3e4dd06ed07a64672978c66cec33592fb4c25a3b22901848.19members:7typedfolders×(atlas.png+font-reference.json),1separateTTF,programinventory/index/README/manifest. 7PNG+1TTF exact-byte V2copies, full rawfont+primarymaterial projections giữfeatures/kerning, khôngUnityimport-ready.
- Assembly40199471450SUCCESS/raw25ea43c67. CRC/population/allmemberhash/sourcehash checks vàpost-uploadHTTPredownload toànZIP/memberchecksPASS, trongcùngCIjob khôngrendererapproval.7existingassets ID/digest/update-time giữ nguyên,releasevẫndraft. Raw/font-reference giữmanifest/audit/release+deliverytrace; khôngoriginalmedia trongGit.
- `tools/verify/font_reference_contracts.py` kiểmtypedsourcejoins/regenerated7metadatahashes/uploadreadback;6tests mới. Publisher manual-only/existingfilenameguard/no-clobber, không rerunversionđãcó.
- **Task peer:** dùngZIPđộc lập/offlineindex đểtham khảo7SDFassets;khôngphải ghépbrowservớiV2. 1TTF vẫnseparateinventory, khôngsourceFontFilebindinggiả. Có7primarymaterials, khôngtuyênbốmọitextvariant/shader/runtimeplacementđãđóng. Cả7serializedkerning/featurepairtables0entries khôngchứngminhtoàngamekhôngkerning. Fontimport/render/RTL/shaping vàaudio listeningvẫnunknown;Premium/poolhistoryhoãn.

- Report74 local218tests/Pillow13+datasvalidationPASS;assembly40199471450 có216tests/Pillow12, finalVerify sau2delivery/publishingtests mới kiểmriêng.

- **Report74 final:** Verify40199813697 SUCCESS trêncode4fe0cef8e,218tests/pinnedPillow12;datasvalidatePASS. Assembly/delivery40199471450SUCCESS,sourceassetIDs/digests giữ nguyên;khôngmởfile/diff/preview.


## Report75 — serialized Sprite meshes/origin, không PNG-pivot guess
- `datas/sprite_mesh_contract.json.gz`, verifier `sprite_mesh_contracts.py`:2185Sprites/27072vertices/24375triangles, float32positions/uint16indices từpreservedrawgeometry;typedidentity/object+payloadhash/PNGrefs. Raw/sprite-meshes/derivation.json làderivationmetadata, khôngcaptureAPK mới; nguồnrawreport62/72 giữ nguyên.
- 1652non-quadmeshes,497PPUvalues (980SpritesPPU100).467mesh-AABB origin diagnostics khácsourcepivot >1e-5.7strictoutside/6beyond1e-5, 2836chỉ−3.076e−8;khôngclamp/recenter. 2185serializedsubmeshlocalAABBs đều0 nhưngmeasuredvertexbounds không0, giữnguyênhaibảngkhácnhau.
- Trianglecrosssignsnegative24013/positive17/zero345, khôngGPUcullingverdict/khôngrepairwinding/khôngxóatriangles. UV0allzero khôngđủđểfabricateUVs.6tests mới;release/media khôngđổi, khôngfullAPKpipeline/preview.
- **Task peer:** importtypedmesh/PPU khi cầnguồngeometry;sourcepivot/mesh-origin/serializedAABB/trimmedPNGregistrationkhácnhau. Quad/recenter/UVmappingmới lànewdesign/approximation nếuchưacóconsumerproof. ConcreteUV/rendererflip/transform/material/sceneplacementvẫnunknown;Premium/poolhistoryhoãn.

- **Report75 final:** Verify40200221258 SUCCESS trêncode1a6c051b7,224tests/pinnedPillow12;local224tests/Pillow13+datasvalidatePASS. KhôngfullAPK/export/media/releasechanges, khôngreport/diff/previewpresentation.


## Report76 — initial-scene SpriteRenderer/ancestor graph
- Raw/scene-sprites/index+chunks+links từpinnedAPK, recovery40200702387/40200823589SUCCESS;5698objects/0readerrors/0unresolvedselectedlinks.1377rendererroots chỉlevel0..3;61438resources/sharedassets renderers đếmnhưngkhôngmởrộng,khôngruntimepopulation.
- `datas/scene_sprite_contract.json.gz`/verifier:Renderer→GO→Transform→ancestors,218typedSprites matchmeshsourcehash/PNGrefs,7fullmaterialprojections/6shaderidentities. SourceBuildSettings orderMenu/Home/Game/EndGame =>8/4/1036/329roots,activityAND6/3/66/3 khôngvisibility. NullSprite56/disabled26/alpha-zero43;78activityAND có1nullSprite.
- FlipX68/FlipY10;negative-scale ancestorchains14/zero-scale4;RectTransformchains43/maxdepth10. DrawMode numeric0:922/1:441/2:14,giữnguyênsize/flags khôngsuyfinalgeometry. SortingLayerID0all1377 khôngfinaldraworder. MaskNone1074/Inside302/Outside1 từdumpenum,303mask-dependentinstances cầnSpriteMask/camera context,khôngrenderapproval.
-8tests mới,local232tests/Pillow12+datasvalidatePASS;finalCIkiểmriêng. No media/release/fullAPKexport/preview. Workspaceoldcheckoutđãbackup152differingfilesngoàiGit vàrestoređúngremote194f9755f cùngbranch;khôngmấtbảncũ.
- **Task peer:** đọcreport76/importtypedscenechain,numericrendererstate vàscopelimits. SourceSpriteMesh/pivot/PPU khác effective renderer draw-mode/UV/transform;khôngdoubleflip,khôngcoi78làvisiblesprites hoặc61438làmissingassets. ConcreteSpriteMask/camera/SortingGroup/runtimewriter followups cònmở;Premium/poolhistoryhoãn.

- **Report76 final:** Verify40201293124 SUCCESS trêncodee5ed7d070,232tests/pinnedPillow12;local232tests/Pillow12+datasvalidatePASS. Media/releasekhôngđổi,khôngfullAPKpipeline/file/diff/previewpresentation.


## Report77 — scene cameras / SpriteMasks / layer predicates
- Recovery40201827785SUCCESS/raw379866994:122objects,5Camera+12SpriteMask scene roots,0readerrors/0unresolvedselectedlinks.191resourcesmasks+1sharedcamera ngoài rootscope;catalog0serializedSortingGroup khôngruntimeabsenceproof.66sharedobjects vsreport76 rawhashequal.
- `datas/scene_render_context_contract.json.gz`/verifier:5cameras source ortho9.600000381469727/fullviewport/nullTargetTexture. Gamelevel2camera3975mask7959 excludesUI/includesMap;3976mask32 onlyUI,disjointbits. TagManagerlayernames/sortingDefaultID0 giữriêngnamespace.
-12mask cùngtypedSprite sharedassets0:37/sourcehash→mesh75;3serializedactive masks6373/6375/6377,9custom-range-active,cutoff≈.2/rawfloat giữđúng. Same-scene masklist chỉinventory,khôngaffecting-maskbindings.78renderers pass cameraLayer+activityAND chưavisibility (1nullSprite),303mask-dependentstates chưaStencil/renderapproval.
-7tests mới;nooriginalmediaGit/no fullAPKexport/no releasechanges/preview. **Taskpeer:** importtypedcontextkhônggộpcamera/layernamespaces;giữmaskranges,depth/clear/nativewriterunknown. Concreteprojection/mask-stencil/runtimevalidation cònmở;khôngnângboolpredicatethànhvisiblelist hoặc191excludedmasks thànhmissingassets. Premium/poolhistoryhoãn.

- **Report77 final:** Verify40202243648 SUCCESS trêncode0f7ae8853,239tests/pinnedPillow12;local239tests/Pillow12+datasvalidatePASS. Recovery40201827785SUCCESS;nomedia/releasechanges/fullAPKexport/file-diff-previewpresentation.


## Report78 — CameraScaler.Awake native screen-ratio writer
- Recovery40202623509+40202782008SUCCESS/rawf84462770;5capturedscalers/6nonnullcameraRefs,125453headers/1knownbuiltinerror. Cả5scene camera hashes/trees match77;sharedassets0scaler121→camera79 làserializedref chưaspawnproof. Raw/camera-scaler giữcomponents/native/2exactfloatpools/index.
- Awake0x141d70c→Resize0x141d710,Screenheight0x27665e4/width0x27665bc→scvtf/fdiv/fmul/fmaxnm→Camera.set_orthographicSize0x275e1b0. Formula max(height/width*5.4f,9.6f),exactfloats5.400000095367432/9.600000381469727. Khôngfixed9.6mọidisplay. Gamearray[3976UI,3975Game] viếtreverseGame→UI,cùngscalar.
- `datas/camera_scaler_contract.json`/verifier:8nativechecks/typedbindings/binary32arithmeticmodel.1080×2400model12.000000953674316,khôngdevicecapture. Modelpositiveint32domain khôngnativevalidationproof. Nullarray/ref đifailurepath,khôngnullskip. Awake rawmin8byteoverlap đượcclipanalysisnextRVA4bytes,rawgiữ nguyên.
-8tests mới;noactualUnitylifecycle/FPCR/render/other-writerabsenceproof,release/media khôngđổi. **Taskpeer:** thayfixedorthoassumption vớiwriterformula+typedrefs,nếuthêmresizeevent/nullrepair/khácScreen sourceghi newdesign. Khônggộp2Gamecameras vìcùngsize;native movement/otherwriters cònmở,Premium/poolhistoryhoãn.

- Report78 lưuý: float-convert height/width TRƯỚCdivision (SCVTF/FDIV),khôngC#integerdivision. Model chỉsetterargument,khôngUnitypropertyreadback. Local247tests/Pillow12+datasvalidatePASS,finalCIkiểmriêng.

- Report78 final: code812775d7e, Verify40203127918SUCCESS (regenerate/pinneddependency/regressionstepsPASS); PR12comment6398981965. Raw vẫn giữ nguyên; khôngruntime/renderapproval.

## Review peer029559d47 — thiếu thật để giao AI game mới (25/10/2026)

Đã fetch explicit nhánh spec, không merge/sửa nhánh bạn. Snapshot nguyên văn 4 tài liệu:
`raw/peer-review/update-029559d47.json.gz` (peer docs KHÔNG phải APK evidence).

**P0 spec tự sửa trước khi giao AI mới:**
- MISSING bảng13hệ vẫn nói audio chưa bóc,asset thiếu: lỗi thời so với chính phần cập nhật
  report67 và pack69–74. Đồng bộ entrypoint/bảng tổng với raw hiện hành, không chỉ append.
- COMBAT §6.1 còn thiếu bindplayerID trong khi MISSING đã đóng; thống nhất trạng thái.
- MISSING §2.2 lấy report53 `Path/Waypoints.WaitForSeconds(rate)` để đóng **player
  StartMainCannonRate**: KHÁC consumer/field. Spawn delay không chứng minh player shot rate.
  Damage×rate vẫn proxy, chưa phải DPS/TTK runtime tương đương; không giao số này như ground truth.
- Đồng bộ78: ortho snapshot9.6 không fixed; float-convert dimensions trước chia, typed camera refs.
- Các con số luật thị giác từ đoảnh/heuristic phải giữ derived/design scope, không nâng thành APK fact.

**Nhánh dữ liệu nhận:** scoped native recovery `Player_Get_Datas` + `Player_Attack` +
`Player_Attack_1` (SetupDatas/Update/MainCannonAttack/MainCannonShoot/getdamage): lần theo
mainrate→timer→bullet/damage, trước mắt chỉship1, không suy24ships từ1implementation.
Recovery mới `recover-player-firing.yml`; raw sẽ lưu riêng `raw/player-firing/`.
Đây là gap cụ thể ảnh hưởng thiết kế nhịpbắn/TTK, KHÔNG xin fullAPKexport.

**Nhánh spec nhận để giao AI mới:** một bảng tối giản `system → raw/contract → implementation
rule → new-design choices → acceptance test`, ghi rõ reference pack có sẵn nhưng chưa
runtime/import/visualapproval. L1 có thể khởi công, không chờ playback để chọn cơ chế mới.
Save migrate/cloud, plugin/build parity, allboss phase closure và shader/stencil/runtime feel
vẫn scopedunknown; chỉ đào khi task triển khai cần cụ thể. Premium/pool-history tiếp tục hoãn.

### Kết quả đào gap player firing — report79
Recovery40203414134SUCCESS/rawbb896f1da. Player_Attack_1.SetupDatas gọi
GetMainCannonRate(0) rồi ghi timeRateMainCannon@0xa8 (demo override3);
MainCannonShoot0x147a988..990 đặt deadline@0x10c = Time.time + interval@0xa8.
**Không giao damage×StartMainCannonRate như actualDPS/TTK**; ngay cả damage/rate còn thiếu
extra-shot timer/barrels/modifiers/hit gates. Chỉ xác nhận consumer tàu1, không suy24tàu.
Xem79 + raw/player-firing; 3targeted evidence testsPASS, khôngruntimeapproval.

- Report79 finalCI40203611037SUCCESS cho9aa2d7e6f; local250testsPASS. Peer đã nhận PR12comment6399041480, chưa có xác nhận đã sửa bên peer.

## Report80 — ship1 grouped shots / damage callback (tạm thời)
- Native timer Nextra dương tạo N+1 lượt vào emitter từcounter0; lượtcuối resetcounter
  rồi đặt maindeadline. Cảmain/extra deadlines đều gate, khôngcatch-up trongspanđọc.
- MainCannonShoot duyệt mainCannonBarrels rồi tailbranchMainCannonAttack:
  rank3→2 vòng,rank>=4→4; pool/component/setup gates nên khôngđếm nhưsuccessfulhits.
- OnEnable extra-count=GP_Datas.GetNumberAbility(4),demo0; khôngdùng ctordefault1
  thaypost-enable. Level(get_Level) khácrank@0x44.
- Collision callbackbody: critcomparison→virtualdamagegetter→Damager→interfacedispatch;
  chưaresolve emitterdelegate/interface type-pointer nên chưachứngminh mọi bullet dùngcallbacknày.
- Boundedtimer model +7tests; local257tests+datasvalidatePASS. Xem80/rawtimer-derivation.
  **entered emitter≠spawnedbullet≠hit≠actualhealthdelta**; chưaDPS/TTKapproval.

- Report80 final: ability getter thuộc **GP_Datas.GetNumberAbility(4)**, không Player_Ability.
  Declaration regression đãthêm; 8newtests/full258localPASS; Verify40204504124SUCCESS cho5989366d7.
  Gap tiếp: delegate/type-pointer + bullet/receiver TakeDamage; chưaactualDPS/TTK.


## Report81 — Giao nguyên gói combat, không task lẻ (25/10/2026)

Final recovery40205786566SUCCESS/raw99ba44829. `raw/combat-chain` gồm123classes/1563methods,
24attackimplementations+coroutines,bulletfamilies,Obj_Collider,Damager,enemy/player/shield receivers.
4133components/1623collider roots,1419pool links; 498GOT joins quaRELA rows (count xem index/contract),
khôngđọc on-diskzeroGOT là runtime null. 0caps/38unclean/132clipped giữ scope;5sourceexceptions.

**P0 sửa SPEC trước khi giao AI mới:**
1. Hậu tốclass KHÔNG phảiID: Player_Attack_1 sourceID10003/nativeGetMainRate index0;
   Player_Attack_3 sourceID10001/index2. Player_Attack_2 source10002/index1: fulltree4EOF,
   chỉprefix ID/demo bámbytes, validated với101fullsourcecomponents. Bảngđủ24 trong81/contract.
   Đừng lấy save getter `id−10001` làm allcombatidentity binding.
2. Primarybullet80003→Bullet_Plasma,extra88004→Homing_Missile,khôngdefaultbaseLinearly.
3. Chỗhở80 delegate/interface đãnối static: RELA→Dumperusage→constructor→SetBullet→Plasma
   collisiondelegate→Obj_Collider.GetIDamageable lazyrootcache→Enemy_Sub→Enemy_Controller
   →Enemy_Health.CalculateDamage. Còn branchgates,khôngmỗiinvocationđềuhit.
4. Armor>=0:100/(100+a);armor<0:2−100/(100−a); clampHP0,hitcallback chạytrước rereadloss.
   Không áp enemyformula cho Shield_Sub/Player_Health. SnapshotnoDamage740false/241true;
   armorprivate runtime khôngcó trongserializedtree,khôngfabricate0.
5. Không damage×rate/DPS/TTKequivalence. Fullfamilyinventory≠semanticapprovalallships.

**Gói AI nhận:** report81 bảngsystem→contract→rule→newdesign/test + datas/combat_chain_contract.json.gz
(regeneratable verifier),rawnative/symbols/RELA/componentshards,declarative all24mapping,
player_main_cannon_timer +enemy_damage_model. 20newtests/full278localPASS/datasvalidatePASS.
Đọc81§F thayviệc đợitừngreportnhỏ. Khôngchờ Premium/pool-history hayplayback đểkhởicôngL1.
Decoderexit−6 sauoutputởConsole.ReadKey đượcgiữlog,khônggiấu/khônggọidecoderexit0.

- Report81 final: Verify40206236112SUCCESS cho b5f2cc62a; full278localPASS. PR12comment6399402332.
  498GOT joins là candidate-address joins (collectorkhôngfullregisterliveness); criticalpath§D đãđốichiếuriêng.
  Khôngnâng fullnativeinventory thành allshipsemantic/DPS/runtimeapproval; chưapeerack.


## Report82 — Không ghi giới hạn chung thay việc đọc native
72/72 directstatcalls (rate/mainDamage/wingDamage×24) đã CFG must-valueprove argument suffix−1,
khôngcòncandidateMOV. SourceID mapping81 vẫn táchriêng (impl1=10003/index0,impl3=10001/index2).
CommonGetMainRatePercent đãđọc: Tech_Datas.GetTechStatLevel(1) tiers≤0:0,1:.03,2–3:.05,
4–6:.08,7–8:.10,≥9:.12; exactpoolbits+24baserates/arrayfield bindingtrongargumentauditJSON.
Enemyflag0x2f=IsCaAttack. 38unclean=36Reset exceptionbodies+2GizmosREToutside12window,
KHÔNG38truncation. 68roots=64nullpointer+4noMonoBehaviour,khôngreceiverunknownchung.
Xem82§6: từngviệccònchưađọc phải ghi method/consumer/callback cầnnối,khônggọimất dữliệu
haydùngchưaruntime/FPCR/playback đểnéđọcstatic. ProofJSON datas/combat_argument_audit.json.

- Audit82 còn sửa parser operandlessRET nuốt instructionkếtiếp do\s* crossingnewline;
  đãregencontract81: directsites13144→13616,rawkhôngthiếu;72CFGproofs giữnguyên.

- Report82 final: codecd2b317dd, Verify40207070647SUCCESS;290localtestsPASS.
  PeerPR12comment6399518575 nhậnproof/realparserfix vàledger mới, chưapeerack.

- Receipt91: code4b7a01a69, Verify40217833652 SUCCESS/job56s; full648 local PASS39.654s.
  Findings/review PR12comment6400980901; HP/Board tasks answered, chưa tự ACK90/91.

## Report92 — Đã trả lời modern drone binding/loadout/serialized turnRate
- Report `docs/apk-analysis/92-modern-drone-resource-bindings-and-loadout.md`, contract
  `datas/drone_loadout_flow.json`; raw/drone-prefabs + raw/drone-loadout giữ đủ pointer/bytes/native.
- Đủ12 ResourceManager→rootGO→MonoScript/id bindings20001..20012; thêm24 bản UI tách riêng.
  Drone3 resource serialized turnRate=1.0, không ctor8; OnEnable không ghi đè turnRate.
- GP_Setup getter **new int[2] mỗi lần**, mode4 trả0/0, còn lại saved DroneUsed0/1.
  StartDrones gọi getter từng slot, prefix Prefabs/Drones/Drone_, localScale f32.8/ .8/1,
  positions±20,−20,0, SetActive true. Không nhét dedup vào loader: routine riêng sửa slot0.
- 35new/full683tests PASS42.905s, datas validate PASS;5ranges319instructions29anchors4symboljoins.
- ACK90/91 đã nhận6401051274. Review peer de2d1366: còn event2/player-route wording,
  AutoGain guardCurrent>0/level0zero, map footer stale; feedback receipt raw/peer-review/review92-*.
- Spec nhập ba đáp án drone trên; reverse tiếp23wing implementations/named map-save consumers.
  Không coi batch này đóng hai nhóm đó; không đợi ACK để làm tiếp.
- Receipt92: code8bb7bd717, Verify40219912118 SUCCESS/job1m4s; đã gửi report92 qua PR12,
  raw/drone-loadout/handoff92-receipt.json giữ ID/response. Không tự coi peer đã ACK92.

## Report93 — ACK92 reviewed; remaining wings configuration batch
- Peer c80b1c50, ACK92=6401411518: 3/3 wording fixes independently verified, snapshots/raw retained.
- `docs/apk-analysis/93-spec-review-and-wing-configurations.md`, `datas/wing_implementations.json`:
  all24 roots/nested 876 method bodies/66845 instructions byte→ASM checked;14 ctor numeric-array joins.
  17 SetBarrels functions/1314 instructions, including16 beyond impl1, normal/index/super config laws.
  78new/full761 tests PASS49.228s; native Unicorn2.1.4 fixture, FPCR0 explicit, not live Unity/FPS/DPS.
- Spec nhập floors14/16/19/21; direct-clamp level13/21; super20 still updates angle; keep S/V instance
  inputs separate from ctor defaults. 10002 raw-prefix ID proof remains valid despite curve parse error.
- NOT all23wing firing closure: next named Shoot/packet/coroutine consumers for17 configs and
  special paths2/4/6/8/10/12/15 (report93§6), plus named map/save consumers unchanged.
- 85 virtual-entry sites,83 receiver-must-owner; two15 GunCheckEnemies stack-spill sites explicit
  unproven automatically, not missing native bytes. Do not replace this with global UNKNOWN rhetoric.
- Receipt93: code8d5d2eba7, Verify40222156868 SUCCESS/job1m9s. Handoff93/green-receipt
  đã gửi PR12, raw/wing-implementations giữ response IDs. Chưa tự nhận ACK93.

## Report94 — Wing13/22/23/24 emission chains, not whole23 closure
- `docs/apk-analysis/94-wing-emission-coroutines-and-packet-geometry.md`, `datas/wing_emission_flow.json`:
  39 bodies/3208 instructions byte→ASM;53new/full814 local PASS67.850s; datas validate PASS.
-13 StartCoroutine before deadline;22/23/24 after deadline.13 two pool attempts/yield, frozen
  width/rate-per-number capped.05. Present IBullet branch exercised to SetBullet/SetActive,
  x±width*i, angles±4*i, lifetime2 (NOT damage), through=super&&throughShield.
-23/24 one child packet/yield incl trailing wait; live shotRate/live childCount after packet,
  mutation to count0 passes+inf to Wait ctor, not silent clamp.
-Basic22/23/24: even N + spacingX0 can emit N+1 calls; N0 can center; only id−1 earlyfilter.
  Circle22/23 uses full worldXYZ; no duplicate endpoint; doesn't apply Basic id−1 filter.
-Closure ABI22 differs23/24; callbacks decoded separately. Basic/Circle terminal helper entry
  remains explicit observation boundary; no successful pool/hit/DPS claim.13 quaternion adapter
  returns controlled identity, records native Euler inputs, not Unity quaternion implementation.
-Sound pool.04super/.08normal, PlayOneShot clip5 volume1/.6, not camera shake; pinned8byte recovery.
-ACK93 received6401658709/raw retained; peer spec not yet independently re-reviewed. Queue Arena/PvP
  after remaining named wing consumers + map/save, per6401593117. Don't wait ACK94 to continue.
- Receipt94: code589e1f588, Verify40223289936 SUCCESS/job1m4s; handoff/green response JSON
  giữraw/wing-emission. Chưa tự nhận ACK94. Không show diff/file/preview cho user.

## Report95 — Bỏ cả5 leaf interceptions94; nối pooled/formation dispatch
- `docs/apk-analysis/95-wing-pooled-leaves-and-formation-dispatch.md`, `datas/wing_pooled_leaves.json`:
  5 bodies/837instructions + exact2instruction trampoline2990890→14a600c (recovery40223486658).
  40new/full854 local PASS69.819s; validate PASS. Không sửa fixture/hash report94.
- Actual leaves22Basic/Circle,23Basic/Circle,24Basic chạy tới Pool/IBullet SDK boundaries.
  Lifetimes22=5,23Circle=10,23/24Basic=4; Circle speed captured arg, Basic live field.
  All5 throughShield đọc trực tiếp field, không local super guard như13.
- All5 activate trước GetComponent. Thiếu IBullet22/Circle23 return sau activation;
  Basic23/24 recycle; thiếu/Unity-null formation cũng recycle. Poolnull throws.
- Basic rotation cộng pointEuler; Circle không; SetBullet angle reread pooledEuler.
  Quaternion identity/pooledEuler77 là controlled inputs, không Unity numeric truth.
- Basic23/24 callbacks formation first + caller second. CreateBullets sau SetBullet nhận
  caller collision gốc, lifetime4. Null external callback vẫn giữ formation callback.
- Boundary tiếp: bên trong Formation.CreateBullets123d98c/Scale/IELerpTo + concrete IBullet,
  các Shoot còn lại của93/special consumers. Không tự coi done23, physics/hit/DPS hoặc ACK95.
- Receipt95: code772839187 Verify40223865259 SUCCESS/job59s; raw/wing-emission giữ recovery,
  handoff và green response. Chưa tự coi ACK94/95.

## Asset binding queue — peer comment6401749563 (chưa independent verify counts)
- Full comment lưuraw/peer-review/asset-binding-audit-6401749563.json. Không gọi asset semantic
  binding “đầy đủ” chỉ vì đã export/index đủ. Numeric sprite name không tự là glyph font.
- Peer báo lỗi art-worklist.py `is_digit` bucket ships/bosses thành glyph; file này không có
  trong current reverse tracked tree khi kiểm95. Cần exact peer source path/commit trước sửa,
  không tự chế tool/khẳng định đã sửa. Sprite identities vẫn theo direct raw/ship/boss joins.
- 5 việc được ghi nhận: UI node→sprite→screen joins; gameplay prefab sprite refs;
  unknown/passthrough labels; unmatched atlas names; actual27 spine rig identities.
  Các số đếm trong comment là peer audit, chưa nâng thành kết quả đo độc lập ở branch này.

## Report96 — USER REPRIORITIZATION: L3 lên trước, không hoãn sau wing/map-save
- User26/10: “L3 đang thiếu trầm trọng… bộ mặt thật của game”. Thay queue trước:
  L3 appearance/UI/gameplay/VFX/motion/audio chains là trục chính; wing/map-save chỉ tiếp
  khi là named dependency của chain nhìn thấy. Arena/PvP vẫn không chen trước việc này.
- Peer spec b000f905 reviewed L3 wording;6 source docs snapshot raw/peer-review/l3-b000f905.
  DONE/START_HERE đã hạ “đủ”; README historical “L3 bỏ” và conditional readiness dễ gây hiểu sai.
- Đã làm UI drawing-use index datas/ui_l3_bindings.json.gz:797files/117class labels,
  76,806 sprite observations,75,749 exact scoped PPtr resolutions,1057null,1099 distinct sprites.
  Inventory55,584 KHÔNG coverage:54,787 ngoài index chưa join. Existing scoped work43/46
  không bị phủ nhận;96 mở rộng indexed coverage thành artifact tra trực tiếp.
-12 tests mới PASS; validate PASS. Chưa pass render/composition/motion/audio; local activeSelf
  không là effective visibility. Không tự nhận visual semantics cho unknown/passthrough/spine.
- Tiếp: ngoài-index scoped references + hierarchy/state/sorting/font/material; gameplay
  prefab→sprite/VFX/rig→clip/event; scene-level reference outputs. Không vẽ từ screenshot,
  không yêu cầu playtest người thật/screenshot mới làm điều kiện bắt đầu phần raw đã có.
- Receipt96: code8789ef433 Verify40224533473 SUCCESS/job1m10s; raw/l3-ui giữ CI/handoff.
  Không tự ACK peer hay tự gọi UI binding regression là L3 composition/render approval.

## Report97 — L3 full saved-layout audit + composition metadata
- Tất cả55.584 saved UI layouts đã scan/hash:54.787 outside index có3.843.228 sprite-name
  observations,0 scoped sprite PPtrs;1.003.504 TMP components khôngfontPPtr.117class labels
  trùng current index; KHÔNG54.787 màn mới.30.827 topology groups;14.081 outsidefiles match
  indexed topology candidates, nhưng KHÔNG chuyển bindings/semantic identity; giữraw tất cả.
- `datas/ui_layout_inventory.json.gz` +4shards; `datas/ui_composition.json.gz` +6shards.
  Composition797sources:100.312visual components;99.731 root-frame matrices/581unknown;
  serialized activity false89754/true10409/unknown149, không runtime visibility.
-76802 material-array scoped joins;18467font +18467sharedMaterial joins, mỗi loại thêm1null.
  Parent reconstruction unique path/depth NOT typed PPtr edges.160ambiguous nodes giữunknown.
  Đã sửa slash-in-name TMP SubMesh path handling, không match-first.
- Renderer m_Enabled không có trong exporter whitelist -> UNKNOWN, không defaulttrue;
  RectTransform anchored/driven layout chưa chạy; matrix float64 không Unity world/render approval.
-37new tests +12tests96 lifecycle cleanup; full suite/CI receipt follows. Việc tiếp:
  scoped GO/Transform/parent/component+enabled recovery; camera/Canvas/dynamic state;
  gameplay prefab→sprite/material/rig/VFX→clip/event/audio. L3 vẫn ưu tiên trước wing backlog.
- Receipt97: final codec915ac075 Verify40226781914 SUCCESS/job1m51s/full suite.
  Full903local PASS73.060s;49UI-focusedPASS14.659s, then22composition rerun after arithmetic pin.
  Matrix summation explicit left-to-right forPython3.11/3.12 consistency; source chunks giữ nguyên.
  Regeneration compare per-record để không format huge diffs; không nới tolerance/fields.
  Old40226331214 superseded, statusraw giữ riêng, cancellation403; KHÔNG giả định green/cancelled.
  ACK96=6402053761 nhận/raw retained, chưa independent verify new peer spec; chưa tự ACK97.

## Report98 — L3 whole-chain recipe, không drip-feed inventory
- Raw source native-classID collector06ab4ef2b / recovery40228467063 SUCCESS / botcb1919d77.
  128724 objects,345090resolved/166639null/52Unity-default-mesh unresolved,0readfail,5header-only.
  Binary MB header authority sửa18074 false script links; generated disagreements vẫn giữ.
- datas/l3_scene_chains.json.gz +shards:805root views,37766logical/25536visual node observations,
  3504typed assets,1587animators,665clips. Root owns nodes/callbacks/sounds/animators/asset closure;
  nonvisual Button_Sound/UnityEvent owners không mất. Raw locators/materialize được từng component.
-665/665 numeric stream+dense+constant decoded/channel exact;301603keys; discrete sprite mappings
  nối scoped identities, không blend pointers.51990unique/393unresolved/17ambiguous binding instances,
  dùng native classID và same-Animator subtree; giữ candidate/nonmatch thay chọn đầu tiên.
-2139callbacks,2037scalar AllClipName fields,92SoundClip registry names. ButtonDown/Up exact native
  method+field; native firing13/22/23/24 clip5 bridge hash-pin report94. CameraScaler native writers
  exact-join5scene cameras;1Canvas, không nhầm CanvasScaler hay gắn mọi camera vào mọi prefab.
- tools/verify/l3_recipe.py: root10Pause235nodes/5clips/26sound fields; root402effect90045;
  root769homeplayer10013. --include-raw nối full raw objects + external media SHA/path; no originalmedia.
-18new tests, full921localPASS124.500s. CI receipt follows, no render approval/selfACK.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review độc lập report98 + recipes, ưu tiên
  MonoBehaviour header authority, target/class/path ambiguity, sprite discrete keys, camera ownership
  và sound/callback condition. Không merge peer/selfACK; PvP vẫn sau L3.
- Tiếp bằng recipe→composition/playback dựng thật/verify source, không quay lại vòng đếm inventory.
  Runtime Animator selection/blending, driven layout, particle simulation/shader execution chưa chạy.
  52default meshes/5header-only/393static target misses giữ rõ, không blanket “thiếu animation”.
- Receipt98: code1f2d12f6e / Verify40229636747 SUCCESS/job2m56s/Python3.12;
  raw/l3-chain-verification giữ receipts +3recipe example summaries. Peer handoff6402605773
  trên PR12; chưa independent ACK, không render approval.

## Report99 — L3 chưa hoàn tất; tiếp compiled Animator programs + target property probes
- Không nhận batch98/tests xanh là complete L3. datas/l3_animator_programs.json.gz nối232
  controllers/232machines/667states/377params/666motion leaves/343AnyState+125state transitions.
  1587Animator direct controller links; recipe bây giờ có programs/links/diagnostics, không chỉclipset.
- Explicit state/clip-time probe nối channels tới binding targets. Popup_QuitMissions GO57508,
  Animator495980→controller1974 Popup_Network reused→defaultAppear→clip1572. Scale0→~1.0304→1,
  alpha0→~.83137256→.83137256 ở0/.25/.5; không tween dựng tay, không gọi engine readback.
-1853start/mid/end clip-time probes trên665clips;0unknown ở các điểm probe.1461initial constant
  sentinel values được xử lý đúng coefficients0/0/0/d; không bịa thiếu key/animation.
- Audit393misses:376no-path;13GO không có MonoBehaviour,4khôngBoxCollider2D. Làm rõ98:
  không phải13MBscript inheritance mismatches.17ambiguous vẫn giữ, không global-match.
-19newtests; full suite/remote receipt follows. Chưa script-driven selection/transition scheduler/
  layer blends/Rect layout/particles/shader/composition-render; đây là missing thật, không selfACK.
- Peer branch arena/20330d0e-windwings-space-shooter-game-p: review report99 state/clip indexing,
  destination mã hoá, source initial keys và direct Animator ownership. Không nhận L3complete.
- Receipt99: full940localPASS131.369s; code5c3ba250d / Verify40230913183SUCCESS2m30s.
  raw/l3-playback-verification giữ local/probe/CI/handoff6402815443; chưa independent ACK.

## Report100 — UI script→activation/trigger→state/clip→event→deactivation
- Native collector cddde2fa7 / recover40231440486SUCCESS / bot161bee87d:1074methods
  from13core UI/root families+nested, pinned executable intervals/RELA/native consts.
  First40231346501 failed namespace: UIObjectAnchors isTuPro, corrected from dump, not omitted.
- datas/l3_ui_drivers.json.gz:214serialized instances,1751potential appearance-call instances,
  1414exact receiver joins/337unknown,230Animator routes,687exact direct-callee links,409callback
  entries. Recipe includes native_ui/global indices/artifactSHA, not just unordered state clips.
- Popup_QuitMissions GO57508/Script644901/Animator495980: SetPopup→SetActive(true),
  defaultAppear/controller1974/clip1572; OnExit→RELA/literalHide→SetTrigger→Hideclip1573;
  eventOffBoard@.33333334→nativeOffBoard→sameGO.SetActive(false). No fake Play(Appear),
  no claiming engine delivery/reset. Confirm guard exitAfterConfirm+0x38 retained symbolically.
- Namespace-qualified inheritance review46event gaps:9base-declared candidates/37remain.
  Popup_QuitEvent594188→Popup_Notices.OffBoard; private base is candidate, not engine lookup proof.
- CFG joins differing values toUnknown; unsupported writes kill; ABI clobbers regs+flags;
  indirect delegates/runtime args unknown, predicates not executed. Source life chain, not runtime trace.
-17newtests; full957localPASS145.887s. Remote receipt follows; no render acceptance/selfACK.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review100 CFG soundness, literal/RELA
  identity, script offset→PPtr receiver, exactcalleeRVA/overloads, callback ancestry and lifecycle.
  Remaining engine blending/layout/particle/shader/composition execution still explicit; L3notcomplete.
- Receipt100: finalad986c7b9 / Verify40232850860SUCCESS3m14s; getter audit thêm140joins,
  final1414resolved/337unknown. x1 ABI không là decoded Vector3/float. Raw receipts
  l3-ui-driver-verification; peer6403162684/PR12, chưa independent ACK hay render acceptance.

## Batch101 — native camera/safe-area layout → recipe (2026-10-26)
- Report `docs/apk-analysis/101-L3-native-camera-safearea-layout.md`; raw native/objects manifest
  `raw/l3-layout-native`, generated585 typed contracts `datas/l3_layout.json.gz`.
-125453 headers scanned;584anchors+1scaler;1unclassified built-in-resource header explicitly retained.
 2526boundedobjects/9161resolvededges/660null; six camera/scaler-writer joins; no automatic main pick.
- Native20anchor/fixed combinations+4scaler modes,4Start camera/flag combinations; model state/cache,
  world-vs-local-z special cases, actual-instance CLI probes and sprite/material references joined.
- Local984PASS160.186s; final27layout tests rechecked after finite-clamp boundary validation.
- Peer arena/20330d0e-windwings-space-shooter-game-p: audit root jump table/literal provenance,
  native Start camera fallback vs direct call, safeArea cache/main-camera distinction, parent bridge
  shared-oracle caveat, source-qualified identities and non-runtime camera selection. No selfACK.
- Next coherent L3 chain: geometry/material/font + particle/shader/composition scene construction,
  then engine transition/blending. Do not mark Unity rendering accepted from model/native-stub tests.

- Receipt101: finalcodeb18e783a7 / Verify40236171639SUCCESS. Raw ci101/handoff101;
  peer PR12 comment https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6403663070; chưa independent ACK.

## Batch102 — layout-owner visual construction + Alert closure (2026-10-26)
- `docs/apk-analysis/102-L3-layout-owner-visual-construction.md`; raw l3-visual-surface,
  artifact l3_visual_surface +249 hashed chunks. Recovery40236919629SUCCESS.
-56714objects/16061GO;11380renderers/153materials/17parsed+decompiled-analysis shaders;
  1391decoded geometry;7fonts/7atlases/2354charentries/1737text instances;954particle modules.
- Fixed101 Alert gap: Animator4647→controller78→none44/alert42/fade43→renderer5105.m_Color.a;
  precise source file identities, trigger/transition descriptors, clip-local coefficients.
-1057animators/91controllers/348decoded clips;79907bindings=74916unique/4983unresolved/8ambiguous.
- Recipe scoped surface/coverage; include-raw selected surface bodies; null font/main camera not auto-picked.
- 0readfailures,1header-only Player_Attack_2:704560,7unresolved builtin particle mesh references.
- Full1012localPASS178.853s,28new tests. Final remote receipt follows.
- Peer arena/20330d0e-windwings-space-shooter-game-p: audit mesh decoder coordinate/UV source,
  live-atlas/slicing caveat, shader raw pass states vs decompiler non-executable analysis, glyph atlas
  bounds/static fallback scope, Alpha binding CRC source, incomplete targets and recipe coverage.
- Not render/VFX/engine blending acceptance. Next camera/composition/culling and actual renderer
  geometry generation; no screenshot gate, no invented default meshes, no selfACK.

- Receipt102: finalcoded1a65f01d / Verify40238106907SUCCESS4m7s; raw ci102/handoff102.
  Peer request https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6403986603; chưa independent ACK/render acceptance.

## Batch103 — world pose/camera geometry/composition chain (2026-10-26)
- Report103-L3-camera-world-geometry-composition; artifact datas/l3_composition.json.gz;
  raw l3-composition-verification. Merge101/102 with1760 body SHA overlaps verified,57480objects.
-11380known serialized world poses;558scene-renderers/10822unplacedtemplates. No unresolved parent→identity.
-6camera snapshots;1104same-scene mask pairs=558pass/546fail; depth groups preserve source clear/target fields.
- Alert: native scaler size10.80000019×24.0000019→zero-border sliced position rectangle→actual source
  world z1→Game/Main depth11/21. Mask7959excludeslayer5;mask32includes. Main almost full1080×2400
  synthetic footprint. Explicit alert clip alpha retained separately, no fake visibility/frame verdict.
-31newtests;full1043localPASS202.733s. Final remote receipt follows.
- Peer arena/20330d0e-windwings-space-shooter-game-p: review merged SHA/edge authority, root-included
  matrices, scene/template separation + placement override, triangle/6plane clipping and float64 scope,
  source zero-border generator assumptions, mask/alpha/footprint distinction, no implicit camera stack.
- Not Unity numerical/render acceptance. Continue actual geometry generation/driver application and
  shader/particle/text/spine execution; source gaps101/102 retained; no screenshot gate/selfACK.

- Receipt103: finalcodedddd75aed / Verify40240026886SUCCESS; raw ci103/handoff103.
  Peer request https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6404277110; chưa independent ACK/render acceptance.

## Batch104 — peer update/feedback + shared modeled write application (2026-10-26)
- Peer head23bf66c7, DATA_SYNC24.34–36/DESIGN_READINESS frozen in raw/peer-review/l3-23bf66c7;
  reported ACK101–103 confirmed, only contract/identity/mask checks, not full numerical/engine acceptance.
- New l3_frame applies native Start/Anchor/Scaler and explicit clip typed writes on SAME instance state;
  current hierarchy/geometry/projection read overlays. Raw immutable; Frame worlds isolated.
- Alert size19.2→24 + sample alpha.392156884→f32 stored.392156899→fade0, footprint unchanged by fade.
- Border_Info7048 playOnStart=false: Start bind only; direct Anchor moves Y7→8.440000534,
  all320descendants propagate; child renderer5452 projection moves144.00004196px. Root border≠0 not_generated.
- Private/static cache semantics retained; atomic clip writes tool-only; mounts remain movable roots.
- Pointer attr0/custom23/type212 NOT field CRC. Strict default reject; explicit m_Sprite policy with
  source type checks log as policy, not engine mapping proof. No unknown mapping→null or fabricated fileID.
-29newtests/full1072localPASS219.316s; artifact datas/l3_frame_cases.json.gz; receipt l3-frame-verification.
- Peer requested numerical reproduction/counterexamples, not count-only ACK: false Start, propagation,
  private/cache persistence, f32 stores, failed plan no partial commit, custom pointer policy.
- Recipe frame_application auto_execute=false. No Unity scheduler/blend/render acceptance. Continue
  concrete binding/order + textured geometry/shader pipeline; existing source gaps remain.
