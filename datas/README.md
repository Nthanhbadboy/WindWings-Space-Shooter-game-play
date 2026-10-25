# `datas/` — data pack WindWings

## Reborn/shield/zone state — report87

`player_shield_flow.json`: Invoke string exact ELF RELA→metadata literal RebornDone, packed initializer3/10, TypeInfo/typed-field joins,7 method roots/417 instructions,32 primary anchors +6 cross-root checks. `python3 -m tools.verify.player_shield_flow [--check]`;18 tests mới. **Correction:** Lifecycle.hit_enemy_enabled tương ứng Physics.activeHitEnemey@90, không phải movement. Shield callbacks không refcount; zone list không OR protection. [Report87](../docs/apk-analysis/87-reborn-invincibility-shields-and-zone-state.md), raw/player-invincibility gồm provenance/toolchain format reference; không Unity timing approval.


## Player HP lifecycle — report86

`player_lifecycle_flow.json`: 3 exact GOT/ELF RELA/metadata callback bindings +43 native anchors và4 literal binary32. `python3 -m tools.verify.player_lifecycle_flow [--check]`; model `player_lifecycle_models.py`,19 tests bao gồm nối receiver85→extra-life→HP1. Bám logic/số bản gốc khi có chứng cứ, art mới; không biến mục tiêu sản phẩm thành “đã phủ toàn APK/không cần kiểm thử”. Raw `reverse-engineering/raw/player-lifecycle/` và peer snapshot riêng (không phải APK evidence).


## Damage receiver flow — report85

`damage_receiver_flow.json`: 44 receiver/helper source walks/3485 native instructions, pinned critical order anchors, CFG-proven ability arguments, exact MB4-state byte targets, event names và coefficient identities. Reproduce `python3 -m tools.verify.damage_receiver_flow [--check]`. Executable finite-domain fixtures `tools/verify/{enemy_damage_model,damage_receiver_models}.py` và48 checks; không giả lập Unity, physics, full FPCR hoặc subscriber registration. Raw bổ sung `reverse-engineering/raw/combat-receivers/`; [report85](../docs/apk-analysis/85-damage-receivers-callbacks-hp-and-death.md).


## Combat coroutine flow — report84

`combat_coroutine_flow.json`: bản dịch control-flow25 MoveNext, CFG branch edges/3 byte-table dispatches, state/current stores và anchors, literal cells,7 factory parameter-copy bodies/direct callers. Reproduce `python3 -m tools.verify.combat_coroutine_flow [--check]`. `tools/verify/combat_coroutine_models.py` là control reconstructions có thể chạy (không thay Unity/IL2CPP); report84 giải nghĩa14 waits, không measured cadence/DPS.


## Combat rate consumers — report83

`combat_rate_consumers.json`: 24 rate-field/demo/deadline bindings, 96 owner-qualified accesses (có wide write overlap), scheduler prefixes/dispatches, StartAttack contexts, 25 MoveNext/14 WaitForSeconds sites. Sinh/check bằng `python3 -m tools.verify.combat_rate_consumers [--check]`. Hash từng raw input trong JSON; derivation receipt dưới `reverse-engineering/raw/combat-chain/rate-consumer-derivation.json`. Không phải bảng projectile cadence/DPS; coroutine site inventory chưa phải toàn bộ emission semantics. Xem [report83](../docs/apk-analysis/83-main-rate-field-deadline-and-dispatch-audit.md).


Dữ liệu bóc từ APK **WindWings: Space Shooter 1.3.118**, đã chuẩn hoá thành JSON để dùng cho
bản clone (engine nào cũng đọc được). Sinh tự động bằng:

```bash
python3 tools/apk-analyze/data_pack.py --root .   # đọc từ docs/apk-analysis/*.csv
python3 datas/validate.py                          # kiểm tra tính nhất quán
```

## Nội dung

| File | Bản ghi | Ý nghĩa |
|---|---:|---|
| `ships.json` | 25 | roster tàu (`id`, `star`, `actived`, sprite) |
| `drones.json` | 13 | roster drone |
| `bosses.json` | 46 | wave → boss icon (ch1 `7001–7022`, ch2 `9001–9024`) |
| `items.json` | 6 | item rơi (`index`, icon, 5 sprite stat) |
| `enemy_hp.json` | 981 | HP serialize của từng enemy/boss component |
| `boss_hp.json` | 277 | gom theo prefab gốc, bỏ bản trùng scene |
| `iap_products.json` | 170 | product ID, tách consumable / non-consumable |
| `sprites.csv` | ~2.800 | `path_id → tên sprite + file PNG` (chỉ có sau lần export mới) |
| `../i18n/en.json`, `vi.json` | 1.415 key | chuỗi UI tiếng Anh / tiếng Việt |

## Quy ước

- `sprite_path_id` / `sprite_name`: **pathID Unity**, không phải asset path. Tên chỉ có khi
  `docs/apk-analysis/04-asset-manifest.csv` đã có cột `path_id` (lần chạy pipeline mới).
  Tra bằng `sprites.csv`.
- `star`: hệ số sức mạnh (2.0 → 5.11) — **không phải** sao hiển thị.
- `actived: false` = có trong data nhưng chưa mở cho người chơi.
- HP trong `enemy_hp.json` là giá trị **serialize sẵn trong prefab**; HP runtime còn bị nhân bởi
  `Enemy_Data_Balance` và cấu hình stage.
- Các class config nằm trong code (`Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`,
  `Stage_Get_Datas`, `Map_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas`)
  **không được serialize** trong build → giá trị nằm trong thân hàm IL2CPP, cần decompile
  `libil2cpp.so` mới lấy được. Chúng không có trong pack này.

## Bản quyền

ID, số liệu và khoá chuỗi là dữ liệu kỹ thuật của game gốc (GCenter). Dùng để tham chiếu thiết kế
cho bản clone của bạn; **không** phát hành lại kèm asset/âm thanh/nội dung chữ gốc.

## Contract save mở đầu — bổ sung sau report65

`opening_persistence.json` là bảng **dẫn xuất tạm thời** của 8 nhóm khóa (tutorial,
stage/zone, sao, drone equip/unlock), không phải save thực hay schema toàn game.
Có kiểu lưu, kiểu getter trả về, default theo scope, cache, side effect, method IDs
và SHA256 raw evidence. `schema_version=1` là version **định dạng contract**, không
phải version save của APK. Xem
[`65-opening-save-keys-cache-and-read-side-effects.md`](../docs/apk-analysis/65-opening-save-keys-cache-and-read-side-effects.md).

Tái tạo: `python3 tools/verify/opening_persistence.py`. Không sửa bảng này tay.
Không gọi getter trong serializer/debug như truy vấn thuần: StageTarget và
IndexTutorial có nhánh ghi ngược tiến độ; Unity PlayerPrefs khác dictionary `/Prefs`.

## Contract ship/loadout — bổ sung report66

`player_loadout_persistence.json`:15 nhóm khóa int32 cho ship equip/unlock,
level/rank/trial/cards/skin, tech/device/talent; có reader return type riêng,
method refs, raw hash, mảng rank đã join metadata và consumer gameplay.
**Tạm thời/partial**, không phải full save schema hay save version của APK.
Raw `reverse-engineering/raw/player-loadout/` giữ native ASM/JSON, metadata array
blobs có padding và `contracts.json.gz` (33methods/43checks).

Tái tạo: `python3 tools/verify/player_loadout_persistence.py`. Không sửa tay.
Phân biệt saved/trial/effective/cached: getter equip lỗi có thể reset cả hai slot;
rank repair base trước override; floor2 nằm ở loader; mode4/Game override tech và
device không xóa saved state. Xem [report66](../docs/apk-analysis/66-player-loadout-save-rank-trial-tech-consumers.md).

## Audio contract — report67; pack audit — report68

`audio_rules.json` giữ118enum names,92registry rows,15rules dẫn xuất và reference
raw `reverse-engineering/raw/audio-rules/contracts.json.gz` (65methods/25checks).
Method refs có RVA để phân biệt overload. Registry PPtr→export file là **candidate
legacy pathID join**, chưa file-scoped identity proof. Tái tạo bằng
`python3 tools/verify/audio_rules.py`. Float pool defaults≈0.73/.30 và fade≈.01
là decimal rounded từ exporter, không full IEEE bits. Không nhầm realtime playlist
với fade theo coroutine frame, mute preference với AudioListener.pause.

Asset pack ngoài Git đã kiểm CRC nhưng chưa đủ: raw/asset-pack/catalog.json.gz
có151collision paths và320manifest size mismatches. Đọc report68/browser instructions;
không dùng manifest filename như object identity, không coi0missing paths là đủ.

## Spine identity hiện hành — report71

`spine_identity.json` giữ27selected SkeletonDataAsset→SpineAtlasAsset→Material→Texture
file-scoped chains +source output hashes, Unity scale/defaultMix/transition/blend và12native checks.
Tái tạo: `python3 tools/verify/spine_chain_contracts.py`; raw tại `raw/spine-identity/`.
185animation names không phải185rig; bảng spine.json/spine_anim.json.gz cũ
vẫn là nội dung animation tham khảo, không dùng global pathID của chúng làm primary key.
7atlas headers1024 cótexture512, không tự sửa tọa độ; source-associated reference folders
ở draft `spine-reference-v1.zip`, chưa runtime/import approval. Xem report71 cho scan exception.

## Sprite export contract — report72

`sprite_export_contract.json.gz`:2185typedSprite outputs +PNGhash/path, source_rect/
source_normalized_pivot/ppu/trim+atlasoffsets/exportsize/alphabbox/rawmeshref. Sinh lại
bằng `python3 tools/verify/sprite_pixel_contracts.py` từ `raw/sprite-pixels/audit.json.gz`.
2185RGBA matches là format-tool crop/flip/mask reproduction, khôngUnityGPU approval.
40float-outside→9roundedpadding;517output khácroundedsourcecanvas. **Không dùngsource
normalizedpivot nhưfinalPNGpivot**, khôngclamp/center tựý. Report72 ghiđủscope/source.

## Fonts / localization contract — report73

`font_language_contract.json.gz`:7typedstaticTMPfontassets, glyph+character/face metrics,
7atlasPNGrefs/hashes, asset-localfallbackorder105→110→106→108→109→111→107.
19LanguageAssets first-index/effective translations (1415nonemptykeys mỗi language),
duplicate evidence/system-language defaultmap/native34methods/10checks/provenance.
`tools/verify/font_language.py` regenerates bằngraw/font-language;10tests mới.
Globalfallbacknull khôngnghĩanofallback;1TTF khôngnghĩa1fonttoàngame.
`i18n/en.json` sửa`txt_free_after` thànhnativefirst-value`Free after`; generator ưu tiên
rawarrays thayCSVđãdedup. Glyphcodepointdeltas khôngphảirenderedmissingglyphs;
chưaUnityfontshader/RTL/shaping/normalization/runtimefontmutationapproval.
OfflineSDFatlas+metrics reference: `docs/assets/font-browser.html` copycạnhmediaV2.


## Font reference delivery — report74

Dùng `tools/verify/font_reference_contracts.py` kiểmmanifest/audit/release metadata dưới
`reverse-engineering/raw/font-reference/`:7typedfontfolders/8exactmedia/19ZIPmembers,
full rawfont+primarymaterial projections,1TTF inventoryriêng,post-uploadreadback.
Draft `font-reference-v1.zip` mởindexoffline trực tiếp, không cần ghépV2.
KhôngUnityimport/render/RTL/shapingapproval; khôngoriginalmedia mới trongGit.


## Sprite mesh contract — report75

`sprite_mesh_contract.json.gz`:2185typedSprite meshes/27072positions/24375triangles,
rawobject/payloadhashes,sourcepivot/rect/PPU,bounds/PNGrefs. Regenerate bằng
`python3 tools/verify/sprite_mesh_contracts.py`;raw/sprite-meshes/derivation.json giữsource
hashes vàdiagnostics, khôngAPKcapture mới. Mesh-AABB origin ratio khôngPNGpivot;
497PPUvalues,serializedzeroAABBkhôngmeasuredbounds. KhôngUVfabrication/windingrepair/
renderertransform hoặcUnityGPUapproval.6tests mới;media/release khôngđổi.


## Initial-scene SpriteRenderer contract — report76

`scene_sprite_contract.json.gz`:1377rendererroots chỉlevel0..3,218typedSprite/meshjoins,
7materials vàleaf-to-rootTransform/RectTransformchains;raw/scene-sprites cóindex/chunks/links.
`python3 tools/verify/scene_sprite_contracts.py` táikiểmPPtrs/sourcehashes/ancestors/numericstate.
78activityAND khôngvisibility,303mask-dependentstates;61438prefabrenderers ngoàirootscope.
Khôngworldmatrix/UV/runtimewriter/camera/shader/PMAapproval,khôngresetflip/scale/nullSprite.
8tests mới;release/media khôngđổi.


## Scene camera / mask context — report77

`scene_render_context_contract.json.gz`:5initial-sceneCamera/12SpriteMask/TagManagerlayers,
sourcechains/bitpredicates cho1377renderers từ76,khôngvisiblelist/affectingmaskbindings.
Raw/scene-context giữ122objects/chunks/links;66cross-captureobjects rawhashequal.
`python3 tools/verify/scene_context_contracts.py` kiểmhashes/PPtrs/typedmaskSprite/layerbits.
Gamecameras mask7959/32disjoint,3masksserializedactive,191resourcesmasks ngoài rootscope.
7tests mới;khôngcamera projection/stencil/runtime/GPUapproval,media/release khôngđổi.


## CameraScaler runtime-writer contract — report78

`camera_scaler_contract.json`:5serializedscalers/6camera refs,5scene camerahashes match77,
Awake→Resize nativechecks/floatpool/sourcehashes,nominalbinary32model
max(Screen.height/Screen.width*5.4f,9.6f). Raw/camera-scaler giữexact4byte literals,
khôngroundedreportnumbers. Verifier `camera_scaler_contracts.py`,8tests mới.
Khôngfixed9.6mọiresolution,khôngactualdevice/FPCR/startup/projection/renderapproval;
khônginventresizeevent/nullskip/absenceofotherwriters. Release/media khôngđổi.


### Combat chain family pack — report81

`combat_chain_contract.json.gz`:123classes/1563method records,24implementation source-ID/rate-index
inventory,1419poolbindings,1623colliderroots,498GOT→ELFRELA→symbolicjoins. Regenerate:
`python3 tools/verify/combat_chain_contracts.py`; regression checks raw/index hashes.
Không phải actualDPS/TTK simulator; đọc scope report81. Prefix-only Player_Attack_2 khôngfulltree.
Enemy damage bounded arithmetic: `tools/verify/enemy_damage_model.py`; khôngáp cho player/shield.


### Combat argument audit — report82
`combat_argument_audit.json`:72CFG must-value proofs/24implementation,commonrate tech1tiers,
exactbinary32/basearray binding,38ends_clean classifications,68receiver-absence snapshots.
Regenerate `python3 tools/verify/combat_argument_audit.py`. KhôngcònchỉlastMOVcandidate;
sourceID/implementation mapping vẫn riêng. Xem82§6 cho ledger đãđóng/consumer cầnđọc tiếp.
