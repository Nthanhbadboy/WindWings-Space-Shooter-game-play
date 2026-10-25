# Bắt đầu ở đây — bàn giao cho AI viết game mới

**Cập nhật report90:** [wing level → barrels và current drone base-fire](apk-analysis/90-wing-level-barrels-and-current-drone-base-fire.md). Shared lazy Level getter + wing implementation1/source10003;12 current drone implementations (9 projectile,1 sweep,2 laser),44 numeric fields và damage source.92 tests mới/full592 PASS. ACK88/89 đã nhận,90 chưa ACK. Không suy all24 wing laws, prefab sourceID binding hay DPS từ fixture.

**Cập nhật report89:** [pickup tới currency](apk-analysis/89-pickup-dispatch-and-collected-currency.md) nối report88 enemy-hit→burst. Không lấy ngân sách28 làm28tiền, không chặn item pickup bằng contact-hit flags; formula đọc balance mỗi lần, event48 sau store. ACK87 đã nhận;88/89 chưa ACK. Full evidence/fixtures không phải whole-game runtime approval.


## Định hướng sản phẩm đã đồng bộ với nhánh spec

Bám logic, cơ chế, nhịp và số của bản gốc theo **APK/reference đã kiểm chứng**; không tự thêm cơ chế hoặc hỏi lại quyết định đã có. Art vẽ mới, không bê asset gốc vào game phát hành và không vẽ lại từ screenshot. Dùng đối chiếu reference/motion/render và kiểm máy để nghiệm thu, không đặt blind A/B hay playtest người thật thành điều kiện bắt buộc. **Mục tiêu bắt chước không đồng nghĩa dữ liệu đã phủ hết hoặc bỏ regression tests**: phần có raw thì triển khai theo raw; scoped unknown thì tiếp tục bóc, không bịa. Review chéo mới: [report86](apk-analysis/86-peer-spec-review-and-player-extra-life-heal.md), peer b8f72a412 đã ACK84;85 đang chờ đồng bộ.


**Report85 — nhận damage tới HP/sống/chết:** [receiver translation](apk-analysis/85-damage-receivers-callbacks-hp-and-death.md), 44 source walks +48 checks. Enemy hit callbacks có thể đổi HP/delegate/ref; player hai truncations, events21/39 đồng bộ trước rereadHP. Delayed death là WaitUntil không phải2s; MB death ba Wait1; ability32 blast có thể gửi damage tiếp. Local375 PASS. Không gộp dispatch/requested damage/HP loss/death event/pool. Các facts vẫn tạm thời; raw + dependencies được giữ, không phải full gameplay rewrite.


**Report84 — coroutine control đã dịch, không chỉ inventory:** [bản dịch25 MoveNext](apk-analysis/84-combat-coroutine-control-flow-reconstruction.md), JSON CFG/anchors/factory bindings và executable control models. 7/9 delay sau attack;17 phát theo cặp rồi chờ;18 particle emission toggle. 14 wait sites core đã nối nguồn và resume; clone/pumpkin delegated bodies cũng đã recover và nối (+2 cleanup waits clone), không lấy tên hàm hoặc số wait ctor làm projectile cadence.


**Report83 — main-rate consumers:** [24 field → deadline → dispatch](apk-analysis/83-main-rate-field-deadline-and-dispatch-audit.md). 96 owner-qualified accesses (48 reads), 23 extra-counter schedulers / riêng 19 single-deadline; 22/23/24 refresh ability trong scheduler. Đừng đồng nhất rate với projectile cadence/DPS. 25 MoveNext/14 wait sites đã inventory, remaining semantics có RVA cụ thể ở §6. Local 302 PASS; raw giữ nguyên.


**Cập nhật 25/10/2026, sau report86. Tất cả kết luận APK vẫn tạm thời.**
Repo này là **kho dữ liệu reverse-engineering + tài liệu tham khảo**, **chưa phải project game chạy được**. Có đủ dữ liệu để bắt đầu prototype có scope; quyết định bám bản gốc/art mới đã có; vẫn phải nối đủ raw, triển khai và nghiệm thu, không cần hỏi lại định hướng.

## 1. Nguồn nào được tin, tài liệu nào chỉ dẫn đường?

1. Nguồn game: raw bóc từ **cùng APK**: `reverse-engineering/raw/`, dump/native/serialized identity. Report dẫn tới raw, không thay raw.
2. `datas/`: bảng dẫn xuất để import; kiểm schema/nguồn/scope trước khi dùng. `datas/waves.json` grouped theo export **không phải** timeline runtime hay danh sách spawn đã dedup đúng theo resource.
3. `docs/apk-analysis/`: phân tích có phạm vi và cách tái kiểm. Tìm report mới theo **chủ đề**, không coi số report cao hơn là phủ định mọi report cũ.
4. `docs/spec/` trên nhánh này **chỉ có snapshot cũ**, không phải spec đầy đủ mới nhất của peer. Không bắt đầu triển khai từ bốn file đó mà bỏ review.
5. Nhánh spec `arena/20330d0e-windwings-space-shooter-game-p` đã kiểm explicit tới **b8f72a4127** (snapshot10docs trong raw/peer-review/review-b8f72a412.json.gz; report86 ghi các lỗi còn lại, peer đã ACK84); report79–81 có các sửa mới về rate/DPS, ID→implementation và concrete bullet/receiver. Peer chưa xác nhận đã áp dụng toàn bộ. Xem HANDOFF_AI_TASKS và report81; review cf27b9755 là lịch sử, chỉ áp dụng finding chưa được sửa, không wholesale merge hai nhánh.
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

## 2. Thứ tự đọc để viết gameplay, không phải đọc tuần tự mọi report

`raw/` trong bảng là `reverse-engineering/raw/`.

**Combat entrypoint mới:** [report81](apk-analysis/81-combat-chain-family-reference-and-receiver-rules.md)
+ `datas/combat_chain_contract.json.gz`. Đọc bảng mapping24implementation trước khi gán chỉ số tàu.

| Cần dựng | Đọc report | Input triển khai / bằng chứng |
|---|---|---|
| Scene → stage → map → waves | 52 | `raw/ui-audit/scene-map-flow.json.gz`, `datas/maps.json`, `datas/map_segments_full.json`; nhánh chapter/branch/mode phải đi theo consumer |
| Wave/spawn/wave-end | 53–54 | `raw/early-waves/index.json`, exact root exports, `resolved-default-waves.json.gz`; index chứa file/root/PPtr identity |
| Mission denominator + result + save | 55–58, 64–65 | `raw/early-waves/mission-denominators.json.gz`, `raw/endgame-missions/{mission-progress-flow,false-result-reachability,shared-stage-victory}.json.gz` |
| Tutorial và UI Continue | 45, 47, 50–51, 64 | `raw/ui-audit/{stage23-ui-flow,tutorial-consumer-flow}.json.gz`, `raw/il2cpp-consts/{DataTutorials,GP_Tutorials,Board_Endgame}.{asm.txt,json}` |
| Enemy/controller/boss/animation | 34–41, 59–63 khi liên quan | raw controller graph, native receiver/consumer, decoded clips. Timestamp không đủ làm state machine |
| UI render/layout/sprite refs | 43–47, 62 | `raw/ui/_index.csv`, UI reference/render exports, typed PPtr. Lấy index làm population, không glob mọi layout cũ |
| Sprite → texture/atlas | 62 | `raw/sprite-geometry/{index.json,objects-000..005.jsonl.gz,resolved-geometry.json.gz}` |
| Ship save/equip/rank/trial/tech/talent | 65–66 | `datas/player_loadout_persistence.json`, `raw/player-loadout/{index.json,array-blobs.json.gz,contracts.json.gz,native/*}`; saved khác trial/effective/cached |
| Ship/drone/gun/HP/economy | 14–15, 19, 28 + native consumer | `datas/README.md`, config CSV, `raw/il2cpp-consts/Player_Get_Datas*`. HP prefab không mặc định là HP runtime; thiếu field không chứng minh không có khác biệt theo tàu |
| Audio rules/trigger | 67 | `datas/audio_rules.json`, `raw/audio-rules/contracts.json.gz`;65method/25checks/15rules; mute vs pause, realtime playlist vs per-frame fade |
| Asset pack / Spine / Sprite pixels | 70–72 + `docs/assets/INDEX.md` | V2identity-safe archive audit;27localSpine chains;2185exactSpriteRGBA matches, khôngUnityGPUapproval. V1collisionreport68 là lịch sử |
| Fonts / localization | 73 | `raw/font-language/`, `datas/font_language_contract.json.gz`, `docs/assets/font-browser.html`;7staticSDFassets/default105+6fallback,19locales/nativefirstIndex |

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

### Loadout save và consumer — bổ sung report66

Đọc [66 — tàu/rank/trial/tech/talent](apk-analysis/66-player-loadout-save-rank-trial-tech-consumers.md), `datas/player_loadout_persistence.json` (15keyfamilies; raw33methods/43checks). Có exact keys/defaults, mảng rank metadata-backed và consumer gameplay. **Equip getter lỗi reset cả hai slot; rank base repair trước trial override; floor2 ở loader không phải getter; mode4/Game có effective-tech/device override, không xóa save.** Talent selection−1 khác tech level0. Không tự sửa rocket count stat5 level6..8→3 thành9. Chưa có schema/migration toàn game hay full upgrade/trial lifecycle.

### Save mở đầu — contract mới đã bóc (report65)

Đọc [65 — khóa save/cache/side effect](apk-analysis/65-opening-save-keys-cache-and-read-side-effects.md) và import tham khảo `datas/opening_persistence.json` (8 key families, raw `raw/persistence/opening-contracts.json.gz`). Có key/default/backend/cache và method IDs, không phải schema đầy đủ toàn game. Đặc biệt **StageTarget và IndexTutorial getter có thể ghi tiến độ**, typed PlayerPrefs khác dictionary `/Prefs`; không biến SaveToDisk custom thành flush tất cả. Scope company!=Test cho default. Đọc callback guard và refresh-vs-reset trước khi làm profile/replay.

## 4. Asset pack — bắt buộc cho tham khảo thiết kế, chưa được gọi là đã kiểm đủ

**Update report70:** đã có **identity-safe v2** từ pinned APK, không overwrite pack cũ.
3038outputs:2185Sprite/653Texture2D/69WAV/64TextAsset/1TTF/66SpriteAtlasJSON.
Object Texture2D còn lại (`resources.assets:535`, Font Texture) là0×0/0bytes/empty stream có raw,
không bịa PNG. Source-accounting3039object, archive member SHA/size/CRC và full PNG decode PASS.
Không còn basename-overwrite trong v2; `all_target_objects_exported` vẫn false vì exception.
Đọc [report70](apk-analysis/70-identity-safe-asset-pack-v2-and-zero-font-texture.md) và
`raw/asset-pack-v2/` cho input/digest/scope. Release vẫn **draft**.

- Dùng `assets-v2.zip` + `assets-v2.sha256`, ZIP thường; không ghép với `assets.z01`/`assets.zip` cũ.
- Giải nén **ngoài Git**, mở `extracted/index.html` để xem ảnh/nghe audio/tìm name+file+pathID.
- `docs/assets/pack-browser-v2.html` trong Git chỉ metadata; không có ảnh/audio gốc đi kèm.
- Pack v1/report68 giữ nguyên151collisionpaths/320size mismatches; không lấy manifest v1 làm identity map mới.

```bash
mkdir -p /home/user/windwings-reference-v2
cd /home/user/windwings-reference-v2
gh release download windwings-assets-1.3.118 --pattern assets-v2.zip --pattern assets-v2.sha256 --dir .
sha256sum -c assets-v2.sha256
unzip -t assets-v2.zip
unzip assets-v2.zip -d extracted
```

**Spine update report71:** `datas/spine_identity.json` khép27selected rig chains qua owning
atlas/material/texture và12native checks. Draft có `spine-reference-v1.zip`:27folder riêng,
skeleton/atlas nguyên byte và texture đúng identity, kèmUnity mix/scale/blend settings.
Đọc [report71](apk-analysis/71-spine-file-scoped-chains-loader-and-reference-folders.md).
7atlas1024×1024 dùngtexture512×512: giữ nguyên, không tự resize/sửa coordinates.
Root580647 có2blend replacement materials; không gộp vào material chính.
Scope125453MB có1header chưa classifiable; không tuyên bố toànbuild đã đóng.

**Pixel export audit report72:**2185/2185Sprite PNG v2 match rawRGBA sau separate
crop/flip/mesh-mask reconstruction từowningtexture PNG; không phải UnityGPU approval.
40float-outside rects chỉ9rounded boxes cầnpadding1pixel (31khôngpadding).
`datas/sprite_export_contract.json.gz` giữtypedoutputs/sourcepivot/offsets/rawmeshref;
517output sizes khácroundedsourcecanvas, không reuse normalizedsourcepivot trênPNGtrim.
Đọc [report72](apk-analysis/72-sprite-pixel-reproduction-fractional-crops-and-pivots.md).

**Font/localization report73:**7staticTMPassets/default105+6orderedasset-localfallback,
19LanguageAssets/nativefirstIndex; globalsettingsnull khôngnghĩanofallback.
`datas/font_language_contract.json.gz` giữmetrics/atlasPNGs/lookup/systemmap;
`docs/assets/font-browser.html` copycạnhmediaV2đểxemSDFatlases vàmetadata.
English`txt_free_after` đãsửaCSVlast-wins→nativefirst-index. Khôngfont/renderapproval.
Đọc [report73](apk-analysis/73-tmp-font-fallback-and-localization-first-index.md).

**Font pack report74:** draft có `font-reference-v1.zip` (1627375bytes,19members):
7typedfontfolders gồm PNG+fullfont/primarymaterial metadata,1TTF inventory riêng vàindexoffline.
Không cần copybrowsercạnhV2 nữa; source bytes giữnguyên, post-upload redownload hashes PASS.
Đọc [report74](apk-analysis/74-self-contained-font-reference-pack-and-delivery-audit.md).
KhôngUnityimport/renderapproval; khônggánTTFvàosourceFontFile=nullbằngheuristic.

**Sprite mesh report75:** `datas/sprite_mesh_contract.json.gz` giữ2185typedmeshes,
27072vertices/24375triangles, sourcepivot/PPU/bounds táchriêng.497PPUvalues;
serializedsubmeshAABB đều0 khôngthaymeasuredvertexbounds. KhôngđoánPNGpivot/clamporigin,
khôngfabricateUV/windingrepair; [report75](apk-analysis/75-serialized-sprite-mesh-origins-and-bounds.md).

**Scene SpriteRenderer report76:** `datas/scene_sprite_contract.json.gz` nối1377initial
level0..3renderers tới218typedSprites/7materials vàancestorTransformchains.78serialized
activityAND predicates khôngvisibility;303mask-dependentstates cần thêmmask/camera context.
61438resources/sharedassets renderers khôngmởrộng, khôngruntimepopulation.
[Report76](apk-analysis/76-initial-scene-sprite-renderers-and-transform-chains.md).

**Camera/mask report77:** `datas/scene_render_context_contract.json.gz` giữ5sceneCamera,
12SpriteMask,TagManagerlayers;2Gamecameras cómask7959/32disjointUI-vsnonUI.
3maskserializedactive,maskranges/cutoff/sourceSprite giữnguyên;78cameraLayer/activityAND
khôngvisiblelist,maskinventorykhôngaffectingbindings. [Report77](apk-analysis/77-scene-cameras-sprite-masks-and-layer-predicates.md).

**Camera writer report78:** CameraScaler.Awake ghiorthoSize theo
max(Screen.height/Screen.width*5.4f,9.6f),khôngfixed9.6mọidisplay.5scene camera refs match77;
sharedcamera referencegiữscope. `datas/camera_scaler_contract.json` cóexactfloatpool/nativechecks,
khôngdeviceexecution. [Report78](apk-analysis/78-camera-scaler-native-awake-and-screen-ratio.md).

Nghiệm thu fidelity còn mở: UnityGPU/PMA/filtering/sceneplacement và pivot consumer,
nghe audio, font runtime/shaping/RTL/coverage và Spine import; staticfallback/rigidentityđãcóscope.
27atlas pages đều có nhiều **global** name candidates, nhưng report71 đã resolve qua local material chain.
Folder pack mới giữpagebasename trongfolder riêng, không phải rewrite atlas text; vẫn **không gọi runtime/import-approved**.
JPEG preview metrics không thay texel/alpha gốc.

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
python3 tools/verify/opening_persistence.py
python3 tools/verify/player_loadout_persistence.py
python3 tools/verify/audio_rules.py
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
- Assets: identity-safe pack/archive/browsability đã có report70; Spine rig/atlas/material/texture joins và reference folders đã có report71; report72 đã matchexportcrop/flip/mask2185Sprite; report73 đãcó7fontassetfallback+19localizationlookup; tiếp UnityGPU/PMA/blend/placement fidelity, nghe audio vàfontruntime/shaping/RTL. Không rerun full export chỉ vì còn exception Font Texture0×0.
- Triển khai: chốt platform/engine/scope rồi viết vertical-slice plan, không lấy một bảng “8/13 hệ đủ” thay acceptance.
- Raw chỉ đào tiếp theo thiếu hụt cụ thể ảnh hưởng implementation. Không mở lại Premium hoặc speculative lifecycle proof ngoài scope.

`HANDOFF_AI_TASKS.md`, `HANDOFF_DATA_SYNC.md`, `CROSS_BRANCH_20330d0e.md` giữ lịch sử phối hợp; phần cũ không phải lệnh hiện hành. Tài liệu này là điểm bắt đầu, report/raw được dẫn mới là căn cứ.

## Blob Map/Player đã có — report69

Không chờ dump mới cho576Map/6Player InitializeArray records: xem
`apk-analysis/69-existing-initializearray-blobs-and-typed-player-bindings.md` và
`reverse-engineering/raw/initialize-arrays/typed-inventory.json.gz`.
PlayerCosts là int[24], ba main/rate/wing arrays là float[24].
Inventory không tự bind Map container/index, không chứng minh stagecount hay DPS/TTK.

- **79 — review peer029559d47 + player firing timer:** sửa claim damage×rate=DPS;
  scoped ship1 native dùng rate làm deadline interval. Xem
  `apk-analysis/79-peer-gap-review-and-player-main-cannon-timer.md` và HANDOFF.
- **80 — ship1 extra shots / callback:** Nextra→N+1 emitter entries, dualdeadline/no catchup;
  rank branch và damage callback khác deliveredhit. Bounded model có7tests, xem report80.

- **82 — proof audit:**72stat-argument proofs/all24,mainrate tech1 modifier,IsCaAttack flag,
  38unclean heuristic/68root classification đãđóng; đọcledger82§6 thayunknownchung81.
