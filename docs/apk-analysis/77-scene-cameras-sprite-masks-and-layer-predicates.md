# 77 — Camera, SpriteMask và layer predicates của scene ban đầu

**25/10/2026 — tạm thời/static, không phải visibility hoặc render approval.**

## Nguồn và scope

Tiếp report76: bổ sung context cho303renderer có MaskInteraction khác0, không đoán mask
chỉ từ tên hoặc ancestor. Không full APK export, không mở preview, không ảnh/media mới.

- Collector `tools/recovery/scene_render_context.py`, workflow `recover-scene-context.yml`.
- **Recovery40201827785 SUCCESS**, raw bot **379866994**.
- `reverse-engineering/raw/scene-context/{index.json,objects-*.jsonl.gz,links.json.gz}`:
  **122objects,0read errors/0unresolved selected links/0ambiguous GO transforms**.
- Roots chỉ level0..3: **5Camera +12SpriteMask**,0SortingGroup.
- GameObject50/Transform50,1Sprite identity,1Material,1Shader identity,BuildSettings và
  TagManager projections. Không shader code hoặc texture pixels.
- Ngoài root scope: **191SpriteMask trongresources.assets,1Camera trongsharedassets0**.
  Catalog không có serialized SortingGroup nào; không suy runtime không thể tạo thêm.
- Cùng pinned XAPK/data.unity3d report70–76.66objects trùng giữa hai capture76/77 có
  **raw object hashes bằng nhau**. Source chunks/PPtrs/catalog/mesh hashes giữ trongcontract.

## Camera state đã đọc

`datas/scene_render_context_contract.json.gz`, verifier `tools/verify/scene_context_contracts.py`.
Scene names theo BuildSettings.scenes/levelN như76; tất cả5cameras có serializedactivityANDtrue,
orthographic=true, size **9.600000381469727**, viewport(0,0,1,1),TargetTexture=null.
Đó là snapshot, không phải camera state sau Awake/Start, resize hoặc gameplay.

| Scene / Camera ID | Tên raw | CullingMask bits | Depth | Far clip |
|---|---|---:|---:|---:|
|Menu/level0:58|Main Camera|3895|−1|20|
|Home/level1:39|Main Camera|3895|−1|120|
|Game/level2:3975|Game Camera|7959|−1|50|
|Game/level2:3976|Main Camera|32|0|50|
|EndGame/level3:1308|Main Camera|4294967295|0|60|

Near clip tất cả≈0.30000001192092896. Không suy viewport pixels/aspect hoặc world-to-screen
matrix từ các giá trị này; camera Transform chain giữ nguyên, không flatten.

TagManager xác nhận layer names theoindex:
0Default,1TransparentFX,2Ignore Raycast,4Water,5UI,8Player,9Enemy,10Bullet,11Item,
12Map,13BlackHole. Empty layer slots giữ empty, không tự đặt tên.

**Hai camera Game scene không có bit-layer giao nhau:**
-3975/mask7959:0/1/2/4/8/9/10/11/12, cóMap nhưng khôngUI.
-3976/mask32: chỉ layer5UI.

Không gộp cảscene thành mộtcamera rồi suy final draw order. Depth ởđây là source field,
không phải mô phỏng compositing, clear flags hoặc render pipeline.

Sorting layers là một namespace khác: raw TagManager chỉ có `Default,uniqueID0`, khớp
SortingLayerID0 của1377renderers trong76. Không dùng GameObject layer index để thay nó.

## Mask state đã đọc, không phải affecting-mask bindings

12mask đều tham chiếu **cùng typedSprite** `sharedassets0.assets:37`, raw object hash khớp
source mesh contract75; link tới PNG/mesh giữ nguyên. Không suy hình mask bằng tênSprite.

- Game/level2 có9mask; EndGame/level3 có3mask.
-3mask có serializedactive+enabled, đều level2:6373,6375,6377.9mask còn lại predicatefalse.
-9mask custom-range-active,3mask không customrange. Front/back sorting fields giữ nguyên.
- Alpha cutoff đều **0.20000000298023224**; không normalize/repair thành giá trị khác.
- Active masks6373/6375/6377 đều backOrder−1/frontOrder0; cácmaskkhác có1→2,2→3 hoặc0→1,
  ngoài3mask khôngcustomrange có0/0. Không tự đảo endpoints hoặc diễn giải inclusion rule.

Contract chứa danh sách same-scene masks cho các renderer phụ thuộc mask. **Đó chỉ là
inventory context, không phải danh sách mask thực sự ảnh hưởng renderer đó.**
Chưa execute hierarchy/sorting-range application, alpha sampling, stencil, native batching,
mask movement hoặc dynamic prefabs. Không biến12mask thành12clip groups đã bind.

## Bit predicates: thêm dữ liệu không đồng nghĩa đã chứng minh visibility

Hàm bit-test giữ32bits: `(bits & 0xffffffff) & (1 << GameObjectLayer)`; layer phải0..31.
Signed−1/highbit có tests riêng, không làm mất bit31.

Mỗi1377renderer từ76 được ghép với cameras **cùng serializedscene**, giữ cácboolriêng:
- `gameobject_layer_allowed`;
- camera serializedactive+enabled;
- renderer serializedactive+enabled từ76;
- phépAND của các điều kiện trên.

**78renderers vượt phépAND ởít nhất1camera**, bằng sốpredicate activityAND trướcđó.
Điều này không phải78visibleobjects: một trong78vẫnSprite=null; không có frustum test,
clipping/occlusion/stencil/alpha/material/runtime update nào được thực thi.
Camera fields cóđủđểtham khảo chứchưađủđể gọi bounds/pivot/PNG placement đã đúng.

303mask-dependent renderer states từ76 được giữ nguyên;12newmaskcontexts không “đóng”
chúng thành verified visibility. Không tự sửa culling masks để cho mọi layer qua.

## Tái kiểm / bàn giao

```bash
python3 tools/verify/scene_context_contracts.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

Verifier rehash raw chunks/PPtrs, đối chiếu source catalog, regenerate renderercontract76,
kiểm66overlap object hashes, typedmaskSprite→mesh, layernames và source-camera bit tests.
7tests mới: regeneration, signed/highbit, scopedcounts, dual-camera disjoint layers,
maskstate/no-bindingclaims, activity≠visibility và preserved camera projection fields.

**Local239tests PASS** vớiPillow12, datasvalidation PASS; finalVerify của code bàn giao
**40202243648 SUCCESS** trêncode0f7ae8853:239tests/pinnedPillow12.
Tests không thực thiUnityrendering.

Không ảnh/PNG/ZIP gốc mới trongGit, release/media không đổi. Không ngụy tạo UV/world matrix,
không dùng camera setup khác để thay original data. Premium/pool-history vẫnhoãn.

**Task peer** `arena/20330d0e-windwings-space-shooter-game-p`, xemHANDOFF:
1. Import typedcamera/mask/transform/layer context nếu dựng initialscene reference; giữ riêng
   GameObject layer và SortingLayerID, haiGamecameras và source clear/depth fields.
2. Không coi scene-level maskinventory là affecting-mask binding hoặc bitpredicate là visiblelist.
3. Muốn đóng rendering cần native/engine evaluation cụ thể cho mask ranges/stencil/camera
   projection/runtime writers. Snapshot orthoSize không chứng minh mọi frame giữ9.6.
4. Resources191masks/sharedcamera ngoài rootscope không phải missingfiles; không fullAPK rerun.
