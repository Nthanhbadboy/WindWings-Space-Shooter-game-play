# Kết luận — trạng thái và độ tin cậy

## Report88 — callback producers đã nối đến burst item thật

[Report88](apk-analysis/88-enemy-hit-producers-and-gold-burst-chain.md): skeleton overwrite hitCallback, DropGold Combine hitDamageCallback, exact bindings từ ELFRELA/metadata.19 co-attachments,16 method ranges/1256instructions,56anchors. DropGold đọc tỷ lệ HP hiện tại/strictthreshold, không dùngdamageargument/không catchup nhiều mốc. Event6→Items_Manager→budget28 thành8item→ellipsehelper→pool/IItem/explicitactivation. Chia5 không chứng minh collectedcurrency; non-nearest radius literal6766e63f được giữ.38tests mới, khôngUnityplayback haywhole-program indirectwriterclosure. Peer ACK87, chưa ACK88; queuewing/drone được ghi chứ không giả định toàn bộrawthiếu.


## Report87 — Invoke đã bóc, khiên và zone state đã nối

[Report87](apk-analysis/87-reborn-invincibility-shields-and-zone-state.md): raw ELF RELA→encoded metadata literal chứng minh Invoke **RebornDone**, initializer TimeResetInvincible=3 và TimeCanActiveInvincible=10 (không wall-clock approval).7 roots/417 instructions; bốn shield flags không phải refcount; SetInvisible heal trước reborn guard, exit không OR theo số zone. **Erratum85/86:** Physics.activeHitEnemey@90 là contact-hit, không movement; Controller+48 là Talent, không input.18 tests mới, full412 PASS/Verify40212492774 SUCCESS56s, có branch combinations/live reread. Peer đã ACK85/86 tại6400213174, chưa ACK87. `datas/player_shield_flow.json`, raw/player-invincibility. Tiếp producer hitCallback/hitDamageCallback thật của Enemy_Health, không lặp inventory hay pool-history.


## Report86 — review spec thật và callback hồi sinh đã bind

[Report86](apk-analysis/86-peer-spec-review-and-player-extra-life-heal.md): peer b8f72a412 đã ACK84 nhưng còn hai nhầm timing (11/13, clone/projectile9), TTK từ damage×interval sai đơn vị và noDamage bị suy thành đồ trang trí. Snapshot10docs cóSHA, peer được giao sửa cụ thể. Ba producer callback được chốt qua ELF RELA/metadata: OnExtralife, DestroyShieldOneHit, noTouch wrapper. Normal/PVP hồiHP1 trước, HealHp(.5/1) riêng; normal resume timeScale.05; zone heal literal1.235% mỗi wait.2. Không tuyên bố fullHP tức thời hay runtime2s.19 tests mới; scope/nguồn ở `datas/player_lifecycle_flow.json`.


## Report85 — dịch receiver qua callbacks, HP reread và death overrides

[Report85](apk-analysis/85-damage-receivers-callbacks-hp-and-death.md), `datas/damage_receiver_flow.json`: 44 bodies/3485 instructions +48 checks mới, full375 PASS. Enemy delta callback đọc lại ref sau hitCallback; controller đọc lại data sau UpdateHpBar. Player device/armor → truncate → ability reductions → truncate → HP → events21/39 → HP reread. Có cả extra-life/death, hai Enemy_Destroy overrides và ability32 recursive requested damage. Delayed không dùng delayTime2; MB ba Wait1, không base Pool. Các fixture callback không chứng minh actual subscribers/stage outcomes. Raw220fa2d53/recovery40210107165 SUCCESS; không đổi draft media release. Bước tiếp là producer/serialized binding và extra-life/heal rewiring, không phải mở lại inventory coroutine84.


## Report84 — đóng control/yield của25 combat coroutine

[Report84](apk-analysis/84-combat-coroutine-control-flow-reconstruction.md): native source walk đủ25 MoveNext +3 computed BR từ9 byte đã pin +14 wait origins +7 factory parameter copies + executable control reconstructions. Phát hiện cụ thể: 17 wait sau cặp,7/9 delay sau attack trước return,18 set_rateOverDistance particle không phải pool-spawn loop. Local327 tests PASS; vẫn phân biệt helper dispatch/spawn/hit/HP loss. Không phải bản dịch toàn bộ APK hay project game có thể build.


## Bổ sung report83 — 24 main-rate consumers (25/10/2026)

[Report83](apk-analysis/83-main-rate-field-deadline-and-dispatch-audit.md) + `datas/combat_rate_consumers.json`: đủ 24 getter-return → demo FCSEL → rate field → main deadline → dispatch; 96 owner-qualified byte-overlap-aware accesses. 19 không extra counter; 22/23/24 refresh ability trong scheduler. Giữ phân biệt dispatch/spawn/hit/requested damage/HP loss. 25 MoveNext/14 wait sites mới inventory kèm các câu hỏi native cụ thể, không tuyên bố hoàn tất coroutine semantics. Local 302 tests PASS, validate/diffcheck PASS. Tạm thời APK-static, không measured cadence/DPS.


> **Mọi kết luận trong repo này là TẠM THỜI.** Mỗi lần pipeline chạy lại, số liệu có thể đổi
> (đổi version APK, đổi backend typetree, sửa parser). File này là sổ đăng ký: kết luận nào,
> lấy từ đâu, độ tin cậy bao nhiêu, và **cách kiểm lại**.
>
> Quy ước độ tin cậy:
> - **A — đo được**: đọc trực tiếp từ dữ liệu serialize (CSV/JSON trong `datas/`, `docs/apk-analysis/`).
> - **B — suy ra**: tính từ dữ liệu A bằng công thức/cách gom nhóm đã ghi rõ.
> - **C — giả định**: suy luận thiết kế, chưa có dữ liệu chống lưng.
>
> Kết luận C **không được** dùng làm thông số implement; chỉ để định hướng.

## Trạng thái kiểm lại hiện hành — sau report78 (ưu tiên hơn bảng lịch sử dưới đây)

**Report78:**CameraScaler.Awake→Resize dùng Screenheight/width vàmax(*5.4f,9.6f),
khôngfixedsource9.6mọimànhình.5scene camerahashes/bindings match77,exactfloatpool giữraw;
binary32sampleskhôngdevice/FPCR/runtime-writerclosure. Sharedcamera khôngspawnproof.

**Report77:**5initial-sceneCamera+12SpriteMask/layercontext,66overlaprawhashesmatch76.
Gamecamera masks7959/32disjoint;12maskcontexts khôngaffectingbindings,78bit+activityAND
khôngvisibility. Sourceortho/maskranges/alpha/layernames giữnguyên, chưaGPU/stencil/runtimeproof.

**Report76:**1377initialsceneSpriteRenderers/218Spritejoins/7materials/fullancestorchains;
78serializedactivityAND khôngvisibility,303mask-dependentstates,61438excludedprefabroots.
Raw/scene-sprites +typedcontract giữPPtr/flip/scale/sorting/drawmode state, chưaUnityrender.

**Report75:**2185serializedSprite mesh contracts/27072vertices/24375triangles,
497PPUvalues, sourcepivot khácmesh-AABB origin diagnostic ở467rows >1e-5.
2185zero serializedsubmeshAABBs giữnguyên,measuredvertexbounds táchriêng.
KhôngPNGpivot/UV/sceneplacement/GPUapproval, khôngrepairwinding/clamporigin.

**Report74:** draft thêmfont-reference-v1.zip tựchứa7SDFassets/primarymaterials/1separateTTF,
19members; sourceV2bytesgiữnguyên,post-uploadredownload/memberhashPASS,existingassetskhôngđổi.
Raw/font-reference cóaudit/delivery; offlineindexkhôngphảiTMPshaderpreview/importapproval.

**Report73:**7staticTMPfonts, main105→110/106/108/109/111/107localfallback,7v2atlasPNGs;
globalnullfallback khôngphủđịnhasset-localchain.19LanguageAssets1426rows/1415nonemptykeys,
nativefirstIndex chứkhônglast-wins. Current→English→key; initialselection/systemmap khác
Englishfallback. English`txt_free_after` sửa thành`Free after`;9797serializedtextcomponents
khônglivescreencounts. Raw/typedcontract/fontbrowserđãcó; chưaRTL/shaping/renderapproval.
Peerpin2d0a0e139 đãtypedPlayerarrays, khôngcòngiữ“chờ573+6dump” làblocker.

Đọc [START_HERE_NEW_GAME.md](START_HERE_NEW_GAME.md). Report64 tách gate tutorial1/2/3 khỏi victory/Board_Endgame campaign dùng chung. User đã bỏ ưu tiên chứng minh low-kill playthrough/BB pool history; không lấy chúng làm blocker scenario. Review spec mới: [cf27b9755](HANDOFF_REVIEW_cf27b9755.md), không lặp finding snapshot25 như chưa được sửa.

**Không dùng số lượng export, số file trên đĩa hoặc unit-test PASS làm bằng chứng
playthrough/design đã hoàn tất.** Xem `docs/apk-analysis/62-raw-audit-and-sprite-geometry.md`.

| Phạm vi | Đã có bằng chứng | Còn thiếu / không được suy |
|---|---|---|
| Stage2/3 | exact resource/prefab joins, denominator và threshold normal có raw53–59 | chưa nghiệm thu runtime; không lấy low-kill reachability/pool-history làm blocker scenario |
| BB-36001 | 3 clip streamed đã giải binding/root keys60; lifecycle/pool-parent/scroll61 | không suy tự thoát hoặc bắt buộc diệt; không generalize sang791clip |
| Audio | raw67:65methods/25checks/15rules; prefs/pool/fade/playlist + scoped consumers | chưa listening/replay/toàn consumer/settings; registry legacy thiếu serialized-file identity |
| Draft pack v2 | raw70:3039source objects/3038outputs, identity-safe paths; archive CRC/SHA/size +2838PNG full decode PASS;535Font Texture0×0/empty payload raw | v1 collisions giữ lịch sử; v2 exception explicit, không pixel/listening/Spine import approval;27atlas pages đều name-ambiguous |
| Spine associations | raw71:27selected rig chains,167metadata objects/168links,15native methods/12checks;27reference folders draft ZIP | 7atlas1024/texture512 giữnguyên;2blend replacements; chưa render/PMA/import approval,1MBheader chưa classify |
| Sprite/atlas export pixels | raw72:2185SpriteRGBAmatch separate crop/flip/mesh-mask reproduction;40float-outside→9roundedpadding,517outputvsroundedsourcecanvas differences | tool reproduction≠UnityGPU/PMA/filtering/placement approval;sourcepivot không normalizedPNGpivot;giữoffsets/mesh |
| UI hiện tại | `_index.csv` snapshot audit:797file/117class/150131nodes | 55584file có trên đĩa không phải55584layout hợp lệ;54787ngoàiindex không tự là duplicate hay rác |
| Spawn | enum raw53:0PinMap/1Path/2Points/3RandomTopDown/4Rocket/5EndMap/6StartWave | “45659quân thật đã chốt” ở kết luận cũ bị rút: cần scoped whole-build recount và runtime semantics |
| Ship/loadout save | raw66:33methods/43checks/15keyfamilies; rank arrays metadata-backed, base/trial/effective/cached phân biệt | full upgrade/trial expiry/migration và cache lifecycle chưa đóng; không sửa branch rocket6..8→3 thành design đẹp |
| Save mở đầu | raw65:41method/8keyfamilies; typed Unity prefs và dictionary /Prefs riêng, getter progression có side effect | schema toàn game/cloud/migration/crash durability chưa có; không dùng SaveToDisk custom làm bằng chứng flush PlayerPrefs |
| Pipeline | pin SHA được enforce trước extract; raw-only changes trigger tests; recovery exporter không kích full analyze | tests hiện tại kiểm static predicates/joins, không thay emulator/Unity replay |

Các mục lịch sử không được kiểm lại dưới đây **không tự nhận mức A hiện hành**.
Riêng hàng18,17,13d,16b,21b cần đọc cảnh báo giới hạn; việc giữ lịch sử không phải
xác nhận các suy luận cũ. Raw vẫn được giữ, không xoá chỉ để làm số coverage đẹp.

## Đăng ký kết luận

| # | Kết luận | Mức | Nguồn | Kiểm lại bằng |
|---|---|---|---|---|
| 1 | Build Unity 2022.3.62f3, IL2CPP, metadata v31, arm64 | A | `02-unity-engine.md`, `01-apk-inventory.json` | `gh workflow run analyze-apk.yml` → xem `02` |
| 2 | 3.662 type, 2.095 class gameplay, 255 enum | A | `03-il2cpp.md`, `07-enums.md` | đếm lại từ `dump.cs.gz` |
| 3 | 25 tàu (10001–10024 + 10999), 13 drone, 46 wave-boss, 6 item | A | `14-*.csv`, `datas/*.json` | `datas/validate.py` |
| 4 | 1.416 key × 19 ngôn ngữ, có tiếng Việt | A | `12-localization.csv` | đếm dòng CSV |
| 5 | 170 product IAP (99 non-consumable + 71 consumable) | A | `13-iap-products.csv` | `datas/iap_products.json` |
| 6 | 981 `Enemy_Datas`, HP serialize 0–10.000.000 — **nhưng ≥126 dòng thuộc màn chọn boss**, enemy "trong trận" ≈ 777–855 (mức B cho phần này) | A (số dòng) / B (số enemy dùng được) | `15-enemy-hp.csv` | `reverse-engineering/raw/typetrees/Enemy_Datas.jsonl.gz` |
| 7 | Boss chương 1 = idWave 7001–7022, chương 2 = 9001–9024 | A | `14-bosses.csv` | cùng file |
| 8 | 282 wave, ~11k spawner, enemy prefab theo tên thật | A | `datas/waves.json` | đọc `raw/typetrees/Call_Data.jsonl.gz` |
| 9 | 458 súng, damage 40–1200 | A | `Gun_Attack.csv` | `raw/typetrees/Gun_Attack.jsonl.gz` |
| 10 | 69 AudioClip tổng ~571 giây, dữ liệu thật trong `resources.resource` | A | `17-audio-diagnose.md`, `assets/audio-index.csv` | release `windwings-assets-1.3.118` |
| 11 | 2.185 sprite + 653 texture, 46 board / 63 popup | A | `04-asset-manifest.csv`, `08-ui-map.md` | `docs/assets/manifest.csv` |
| 12 | Hằng số trong thân hàm: **12 class, 305 method** (GameDatas 73, Player_Get_Datas 62, IAP_Manager 35, ArenaManager 34, Tech_Datas 25…) | **B** | `19-il2cpp-constants.md`, `raw/il2cpp-consts/*.json` + `.asm.txt` | đọc `.asm.txt`, đối chiếu control flow; hằng số có thể là epsilon/clamp chứ không phải giá trị thiết kế |
| 12b | **Hằng số float đọc trực tiếp từ literal pool `.rodata`** (`adrp`+`ldr` → VA → offset qua `PT_LOAD`, **chỉ segment read-only**): **76 dòng** trong bảng MD (82 dòng CSV thô, 6 dòng trùng VA), hệ số thật như `GetBaseDamage` 0.6, `GetBonusCoin` 0.1, `GetWingCannonDamage` 0.168→0.1764→0.1932 (tăng 1.05×/cấp), `GetTechStatUpgradePrice` 0.86/0.689, `GetPlayerUpgradePrice` 0.12 + trần 150000. Đọc int từ pool đã **bỏ** (VA dùng chung cho ra word đóng gói, không phải hằng). Đây là byte có thật trong file, không phải suy luận | **A** (giá trị) / **B** (ý nghĩa) | `19-il2cpp-constants.md` mục "Float đọc từ literal pool", `il2cpp-pool-floats.csv` | đọc lại `.so` tại đúng VA đã ghi |
| 12c | Getter **hầu hết không** trả hằng số: **244 getter** đã phân loại → `call` **173**, `computed` **37**, `field` **23**, `const` **11** (`GetMaxRebornCount` 5, `GetTimeFreeOverdrive` 60.0, `GetMaxCountRockets` 10, `TimeToImmuneOneHit` 25.0…). Bảng cân bằng nằm trong dữ liệu, không hard-code trong getter | **A** | `19-il2cpp-constants.md` mục "Getter: trả hằng số hay đọc dữ liệu?" | chạy lại `il2cpp_consts.py`, xem cột `getter_kind` trong JSON |
| 13 | Layout từng màn: **608 màn, 80.806 node**, có `local_pos`/`scale`/`rotation`, class component, text + nút | **B** | `20-ui-layout.md`, `raw/ui/*.json.gz` (584 file) | so với screenshot; layout group có thể override |
| 13b | UI của game là **SpriteRenderer world-space**, không phải Canvas/RectTransform (chỉ 1 `Canvas` trong toàn build) | **A** | `20-ui-layout.md` (bảng component) | đếm lại `Canvas`/`RectTransform` trong raw |
| 13d (SNAPSHOT CŨ) | **Không dùng số dưới đây thay index hiện tại; xem snapshot62 ở trên.** Lịch sử: 6.580 file layout / **114 tên màn** / 1.404.553 node; "
"`_index.csv` của lần chạy mới nhất chỉ có 630 file / 98 màn → **16 màn chỉ còn ở file cũ** "
"(`Board_Shop`, `Board_Pause`, `Board_Drones`, `Board_Items`…) | **A** | `24-ui-screens.md`, "
"`datas/ui_screens.json.gz`, `datas/ui_text_keys.csv.gz` | `python3 tools/apk-analyze/ui_index.py` |
"
 "| 13c | **Spine: 27 rig / 185 animation / 12.274 keyframe**, thời lượng thật từng anim, 21 event (`Shot` đúng 0.3333 s trong 12 anim đánh, boss `Attack3` có `Stop` tại 0.63/3.3/5.87/8.2 s) | **A** | `23-spine-anim.md`, `datas/spine_anim.json.gz`, `spine-events.csv` | `python3 tools/apk-analyze/spine_anim.py` |
| 16 | **Lớp hành vi enemy/boss đã export**: 981 `Enemy_Physics` · 971 `Enemy_Destroy` · 695 `Enemy_Burned` · 391 `Enemy_LookAtPlayer` · 140 `Enemy_Stun` · 981 `Enemy_Display`; `Enemy_Controller.uiScript` → **`Enemy_Display`** (không có class `Enemy_UI`) | **A** | `25-enemy-behaviour.md`, `raw/typetrees/*.jsonl.gz` | đọc lại `Enemy_Controller` + `script-links.jsonl.gz` |
| 16b (SUY LUẬN CHƯA ĐỦ) | **0 field có giá trị không chứng minh collision runtime hoặc class không làm gì.** Lịch sử: chỉ 2 field serialize, **0/981** dòng có giá trị → va chạm nằm ở `BoxCollider2D` runtime, không phải dữ liệu thiết kế | **A** | `25-enemy-behaviour.md` §2 | đếm lại field trong `Enemy_Physics.jsonl.gz` |
| 16c | **`Transform` 228.432 dòng** (2.089 root, 0,9%): mở **5 mắt ghép 0% → 100%** (458 súng · 251 hitbox boss · 558 `parentRotate` · 1.372 điểm đầu/cuối đường bay · 250 `bossObj` — mắt cuối nối vào `Board_Maps`, tức icon bản đồ chứ không phải prefab boss) | **A** | `25-enemy-behaviour.md` §5, `raw/typetrees/transform-tree.tsv.gz`, `datas/prefab_joins.csv.gz` | chạy `tools/apk-analyze/prefab_joins.py` |
| 16d | **`Call_Data` đủ 23.757** (trước cắt 1.500); `Call_Point` cùng 23.757 là **lớp bọc** trỏ `dataScript → Call_Data`, không phải bảng dữ liệu mới | **A** | `25-enemy-behaviour.md` §4 | `script-links.jsonl.gz` |
| 17 (PHẠM VI CŨ) | **Report60 đã giải3clip BB; không còn đúng nếu nói mọi curve đều chưa đọc được.** Danh mục cũ: 791 `AnimationClip` (226 tên, median 1,9 s, 251 clip lặp, 793 event) + 308 `AnimatorController`; keyframe curve **không lấy được bằng UnityPy** (2 cách đọc đều 0 — dữ liệu streamed) → lớp này ở mức nhịp, chưa dựng lại được | **A** (danh mục + việc curve không đọc được) / **C** (curve) | `26-native-animation.md`, `27-anim-curves.md`, `datas/anim_clips.json.gz` | giải mã streamed clip |
| 18 (ĐÃ RÚT KẾT LUẬN) | **Không dùng hàng này làm thông số implement**. Bản lịch sử ghi: `len(enemies) × copies` cộng dồn = **45.659 quân thật** (22.475 lượt khai báo trong `waves.json` của mình — nhánh spec đếm 22.483, lệch 8 do khoá dedupe; tích cuối khớp tuyệt đối). **Enum `spawnType` đã giải mã**: `0=point · 1=path · 2=point_range · 5=special · 6=boss` (16.498/4.199/1.688/686/686 trên 23.757 spawner); tổng lượt xuất hiện **45.659**; `number`/`editType` = 0 ở 100% → số con mỗi lượt **không** nằm trong prefab | **A** (phân bố) / **B** (gán nhãn) | `25-enemy-behaviour.md` §8 | đếm lại `Call_Data.jsonl.gz` |
| 17b | **`Animator` 5.792 instance đã nối**: prefab gốc 5.686/5.792 (98,2%), tên controller 5.603/5.792; `ParticleSystem` **4.845** đã ghi `path_id` (chưa có chi tiết module). Số instance khớp độc lập với nhánh spec đếm | **A** | `26-native-animation.md`, `datas/animator_map.csv.gz`, `raw/typetrees/native-types.jsonl.gz` | chạy `tools/apk-analyze/animator_joins.py` |
| 18b | **Truy vết công thức**: 305 method có flow hằng số theo địa chỉ + đích `bl` đã giải tên (200 bl); đọc thử `GetWingCannonDamage`: hệ số theo ngưỡng 4/58/118/248 (0.168 → ×1.05 → ×1.15) rồi `+1.0` | **A** (thứ tự lệnh) / **B** (diễn giải ngưỡng) | `28-formula-traces.md`, `datas/formula_traces.json.gz` | chạy `tools/apk-analyze/formula_trace.py` |
| 19 | **`ParticleSystem` 4.845 đã có tóm tắt module + MinMaxCurve**: thời lượng hệ median 5,0 s, tuổi thọ hạt median 1,0 s, tốc độ đầu = 0 ở 66% (FX dạng burst) | **A** | `29-particle-systems.md`, `raw/typetrees/native-types.jsonl.gz` | đọc lại mục ParticleSystem trong native-types |
| 19b | **Sprite/Texture đã có kích thước**: 2.816/2.885 dòng `sprites.csv` có `width×height` (từ ảnh export thật) | **A** | `datas/sprites.csv`, `04-asset-manifest.csv` | so `width/height` với PNG trong bản export |
| 20 | **Camera**: 6 cái, tất cả orthographic, `orthographicSize = 9,6` → chiều cao thấy được **19,2 world-unit**; khớp mốc spawn `y = 9,6` của wave (quân hiện đúng mép trên) | **A** | `24-ui-screens.md` mục Camera, `raw/typetrees/native-types.jsonl.gz` | đọc mục `Camera` trong native-types |
| 21 | **Đã quét asm thêm 5 class runtime** (`Player_Health`, `Player_Talent`, `Player_Ability`, `Player_Ingame`, `Player_Attack`): tổng **425 method / 324 `bl`** giải được tên. `Player_Health` gọi `GetStartHp` 3 lần trong lambda của `Start`, `TakeDamage` gọi `IsInvisible/SetInvisible` + `TimeToImmuneOneHit` | **A** | `19-il2cpp-constants.md`, `28-formula-traces.md`, `raw/il2cpp-consts/Player_Health.asm.txt` | chạy lại `il2cpp_consts.py` + `formula_trace.py` |
| 21b (GIỚI HẠN) | **Thiếu tham số không đủ chứng minh mọi tàu có HP/talent giống nhau.** Chữ ký đã ghi: **Không method HP nào nhận `playerIndex`**: 8/55 method float/int có tham số này và tất cả là damage/nhịp bắn/giá mở tàu → talent + nâng cấp là **chung mọi tàu**, tàu chỉ khác damage | **A** | `raw/il2cpp-consts/Player_Get_Datas.json` (cột signature) | đếm lại chữ ký hàm |
| 22 | **`StartHp = 2500`** (HP gốc người chơi): nạp bằng `ldr d` từ VA `0x757bc4` trong `.cctor`, ghi vào static offset `0x6c` (nửa trên của cặp đôi ghi ở `0x68`, nửa dưới là 0.18). `GetStartHp() = 2500 × (1 + GetHpStatPercent())` — fadd 1.0 + fmul thấy rõ trong asm | **A** | `raw/il2cpp-consts/Player_Get_Datas.json` (`.cctor`, via `ldr_pool_d`), `19-il2cpp-constants.md` | đọc lại 8 byte tại VA `0x757bc0` trong `.so` |
| 14 | Damage/giá/thưởng suy ra từ field serialize | **B** | `docs/spec/COMBAT.md`, `ECONOMY.md` | so với hằng số ở #12 |
| 15 | Nhận định "game dễ bypass", "nên dùng Spine"… | **C** | `PHAN_TICH_WINDWINGS_APK.md` | chỉ là đánh giá, không phải số |

## Những gì **chưa** bóc được (còn thiếu thật)

| Thiếu | Vì sao | Cách làm tiếp |
|---|---|---|
| Thân hàm của các class cân bằng | **0 instance** trong `data.unity3d` → giá trị nằm trong IL2CPP; đã quét **17 class** (gồm `Player_Health/Talent/Ability/Ingame/Attack`) | `19-il2cpp-constants.md` + `raw/il2cpp-consts/*.asm.txt` |
| Curve keyframe ngoài3clip BB report60 | **cả typetree lẫn UnityPy reader đều cho 0 keyframe** (đã thử, `27-anim-curves.md`) — curve nằm trong streamed clip nén | giải mã `m_StreamedClip` thủ công, hoặc dựng lại bằng nhịp ở `26-native-animation.md` |
| Curve chi tiết trong module ParticleSystem + nối PS → prefab | mới ở mức scalar/module | mở rộng `animator_joins` cho ParticleSystem |
| Công thức đầy đủ (thứ tự nhân, clamp, nội suy) | cần đọc control flow, không chỉ hằng số | Ghidra/IDA trên `libil2cpp.so` (đã có trong artifact) |
| Ý nghĩa từng hằng số ở #12 | capstone chỉ thấy số, không thấy phép tính | **Đã bóc được giá trị float thật từ literal pool** (#12b); còn thiếu *thứ tự nhân/chia* → đọc `raw/il2cpp-consts/*.asm.txt` hoặc Ghidra |
| Layout runtime thực tế | prefab ≠ runtime (layout group, safe area) | screenshot + so với `raw/ui/` |
| ~~`ui_layout.py` bỏ sót màn~~ | ✅ đã sửa: dedupe `(class, root)` thay vì root — một lần chạy đủ **742 file / 114 class** (trước 607/90, 186 candidate bị bỏ lặng lẽ) | chạy lại pipeline, xem `_index.csv` + `_skipped.csv` |
| ~~`orthographicSize` của camera~~ | ✅ **9,6** (6 Camera, tất cả orthographic) → vùng thấy cao 19,2 world-unit, khớp mốc spawn y=9,6 | `24-ui-screens.md` mục Camera |
| Hiệu ứng/particle cụ thể | đã có tóm tắt 4.845 hệ (`29-particle-systems.md`), chưa có curve | đọc curve trong module khi cần dựng FX |
| Logic PvP/Arena server | nằm ở Firebase, **không có trong APK** | không lấy được |
| Spine animation curve | **đã xong** — `23-spine-anim.md` + `datas/spine_anim.json.gz` (12.274 keyframe) | còn thiếu `timeScale` runtime |

## Cách giữ cho kết luận không bị "chết cứng"

1. Dữ liệu thô luôn nằm trong `reverse-engineering/raw/` (JSONL gzip, **không cắt field**).
2. Mọi bảng tóm tắt đều sinh lại được từ thô bằng script trong `tools/apk-analyze/`.
3. Khi sửa parser, chạy lại pipeline rồi `git diff` — chênh lệch chính là chỗ kết luận cũ sai.
4. Đừng xoá file thô để "cho gọn": nếu thiếu dung lượng thì nâng cap trong workflow, không xoá.

## 79 — Peer gap review / player main-cannon timer (tạm thời)
Đã đối chiếu peer029559d47, giao sửa bảngtổng audio/assets và claim DPS/TTK.
Raw recovery40203414134SUCCESS/bb896f1da: ship1 sử dụng GetMainCannonRate trong
Time.time+interval deadline, không chứng minh damage×rate là DPS.
Giới hạn ship1, chưa collision/emittedbullet/allships/runtime closure. Xem report79/HANDOFF.
Local250tests+datasvalidatePASS; khôngruntime/renderapproval.

## 80 — Ship1 extra-shot timer/collision body (tạm thời)
Nextra dương→N+1 emitter entries từcounter0; dualdeadline, no catchup trongspanđãđọc.
MainCannonAttack rank3→2/rank>=4→4 vòng cópool/component gates; khôngactualhitcount.
Callback damage cócrit/getter/Damager dispatch nhưng delegate/type-pointer binding chưađóng.
Report80 + raw/player-firing/timer-derivation.json + boundedtimer model; local257testsPASS.


## 81 — Combat chain family reference (tạm thời, entrypoint mới)
Đã gom123classes/1563methods của24attackimplementations/coroutines +bullet/receiver families;
4133sourcecomponents/1623colliderroots,498ELF RELA→symbolicGOTjoins. Khôngchỉship1method.
SourceID implementation1=10003/index0;implementation3=10001/index2: khônggánID từsuffix.
Đãnối static callback+IBullet+Obj_Collider+enemyreceiver→armor/HP;80003 concreteBullet_Plasma,
88004Homing_Missile. Piecewisearmor/HPclamp/callbackorder cóboundedmodel,khôngactualDPS.
Report81+datas/combat_chain_contract.json.gz+raw/combat-chain;0caps nhưng38unclean/132clipped,
4attack2EOF prefix-only +1builtinheadererror. 278localtestsPASS,khôngruntime/playbackapproval.


## 82 — Rà và đóng giới hạn quá rộng
CFG must-value proves72/72statgetter arguments suffix−1 (rate/main/wing×24),tách sourceID81.
Mainrate Techstat1modifier+exactfloatpools/base24arraybinding đãđọc. Enemyflag@0x2f IsCaAttack.
38unclean=36Resetexception+2GizmosREToutside12window,khôngmissingbodies;
68roots=64null+4noMonoBehaviour. Report82ledger§6 chỉmethod/consumer thực cầnđọc tiếp.
