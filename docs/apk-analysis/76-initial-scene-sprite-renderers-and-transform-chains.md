# 76 — SpriteRenderer ban đầu trong scene và cây Transform

**25/10/2026 — mọi kết luận vẫn tạm thời/static. Không phải render/placement/visibility approval.**

## Mục tiêu và nguồn

Report75 giữ Sprite mesh gốc; report này nối một phạm vi **renderer instances có sẵn trong
4scene** tới Sprite/mesh, material và ancestor transforms. Không làm full APK export,
không mở preview, không lấy screenshot dựng lại game.

Scoped recovery dùng cùng XAPK/data.unity3d SHA đã pin của report70–75:
- `tools/recovery/scene_sprite_renderers.py`, workflow `recover-scene-sprites.yml`.
- **40200702387 SUCCESS**, raw bot **91b6045a3**; BuildSettings projection được thu hẹp
  về scene/version/graphics fields ở8fc8cd259, recovery **40200823589 SUCCESS** tái kiểm.
- Raw `reverse-engineering/raw/scene-sprites/{index.json,objects-*.jsonl.gz,links.json.gz}`.
- **5698objects,0read errors/0unresolved selected links/0ambiguous GameObject transforms**.
- Built-in types, UnityPy1.25.4; không cần generated MonoBehaviour headers hoặc native dump mới.

Raw chứa1377SpriteRenderer,2044GameObject,2011Transform,33RectTransform,218Sprite identities,
7Material,6Shader identities,1Texture2D metadata và1BuildSettings scene projection.
Không có shader programs, texture pixels hoặc original media mới trongGit.

## Phạm vi rất quan trọng: không phải tổng runtime renderers

Catalog APK có **62815serialized SpriteRenderers**. Chỉ1377thuộc level0..3 là roots ởđây.
**61430resources.assets +8sharedassets0 =61438 không được mở rộng thành renderer roots**.
Không biến các count này thành số địch, stage, draw calls hoặc live actors.

BuildSettings.scenes giữ thứ tự; ghép scene index với serialized filename levelN:

| File | Scene path suffix | Renderers | Serialized activity AND predicate |
|---|---|---:|---:|
|level0|Menu.unity|8|6|
|level1|Home.unity|4|3|
|level2|Game.unity|1036|66|
|level3|EndGame.unity|329|3|
|Tổng trong phạm vi|4scene riêng biệt|1377|78|

Full scene paths ởcontract/raw, không suy từ tên GameObject. Không coi4scene là cùng lúc visible.
Predicate chỉ là `renderer.m_Enabled AND every ancestor GameObject.m_IsActive`.
**78không phải78visible sprites**: trong đó có1renderer vớiSprite=null, chưa kể camera,
mask, alpha, scripts hoặc animation. Không thực thi Awake/Start/OnEnable/spawn ởđây.

## Typed joins và dữ liệu để implement tham khảo

`datas/scene_sprite_contract.json.gz`, verifier `tools/verify/scene_sprite_contracts.py`:

1. Renderer→GameObject, chọn đúng1Transform/RectTransform trong raw m_Component.
2. Đi m_Father lên tận root; giữ **leaf-to-root**, reject cycles, không flatten world matrix.
3. Giữ local position/quaternion/scale; RectTransform anchors/sizeDelta/pivot giữ nguyên.
4. Renderer.m_Sprite→**218unique typed Sprite identities**, đối chiếu raw object SHA với
   `datas/sprite_mesh_contract.json.gz`; PNG path/hash/PPU chỉ là source reference.
5. Null Sprite giữ null; m_Materials resolve7typed materials, giữ full saved properties và
   Shader PPtr identity. Không chọn texture bằng global basename.
6. Externals/PPtrs và từng chunk hash kiểm lại; source mesh contract/catalog hashes giữ riêng.

GameObject layer, renderer RenderingLayerMask và SortingLayerID không phải một field.
Không gộp chúng thành một “layer” mới trong spec. Contract giữ `gameobject_layer` rõ nghĩa,
renderer fields nằm trong `renderer_tree` nguyên kiểu serialized.

### State inventory trong1377renderer roots

- **26renderer disabled**, **56null Sprite**; không coi là mất asset hoặc tự fillSprite mặc định.
- **FlipX68 / FlipY10**;14renderer chains có negative-scale component,4có zero-scale component.
  Không gộp renderer flip với Transform scale hoặc áp flip hai lần lên source mesh/PNG.
-43chains chứaRectTransform; maxchain length10. Không chỉ đọc transform của leaf.
- DrawMode numeric counts **0:922,1:441,2:14**; m_Size/threshold/tile fields giữ nguyên.
  Không khẳng định mọi renderer dùng source mesh/quads giống nhau sau native draw-mode logic.
  Managed dump đang giữ không có enum SpriteDrawMode; report này không bịa enum proof.
- SortingLayerID numeric **0ởcả1377**; SortingOrder giữ từng instance, không tự sort toànscene
  theo một field rồi gọi đó là final draw order.
- MaskInteraction **0:1074,1:302,2:1**. Dump enum xác nhận0=None,1=VisibleInsideMask,
  2=VisibleOutsideMask. **303instances có mask-dependent state**; SpriteMask graph chưa thu.
-43renderer colors cóalpha0, không tự sửa thành1 hoặc coi predicate hoạt động là nhìn thấy.
- SpriteSortPoint numeric0:1376,1:1, giữ nguyên; chưa có consumer/render validation cho nó.

7materials: typed `Sprites-Default`, `Additive`, `BloomSimple`, `GrayScale`, `Radial_UI`,
`PrgBar_Verticle+Gray`, `PrgBar_Verticle` — tên chỉ giúp đọc, không thay owning identity.
Tất cả m_CustomRenderQueue=-1; không biến sentinel này thành actual draw queue.
Null saved texture fields không tự chứng minh SpriteRenderer không có texture: source Sprite
join đã có, nhưng engine material/property binding và shader code chưa chạy.

## Giới hạn, lỗi workflow và trạng thái workspace

- Resources prefab spawn/state, pooled clones, animation, runtime Transform writers,
  camera projection/culling, SortingGroup, SpriteMask geometry và GPU output **chưa kiểm**.
- Không tính world matrix/RectTransform layout rồi gọi là vị trí Unity thật. Source mesh
  registration từ75 vẫn khác effective geometry/UV của renderer sau draw-mode processing.
- Children và sibling components ngoài selected Transform chỉ giữ raw pointers; không mở
  rộng tất cả GameObjects/components của APK. Shader identities không phải shader disassembly.
- Lượt đầu40200644348: collector +224tests PASS nhưng preserve step dùng sai tên
  `graph-index.json` thay vì `index.json`, runFAIL. Đã sửa guard; không gọi runđó là recovery success.
- Workspace đầu lượt quay về initial checkout trong khi remote có đủreport75. Đã sao lưu
  152files khác remote (khoảng5.9MB) ngoàiGit ở `/home/user/workspace-recovery-before-report76.tar.gz`,
  rồi khôi phục đúng remote HEAD trên cùng nhánh; không xóa root/.git, không mất bản cũ.
  Đây là operational note, không bằng chứng game mới.
- Release/media không thay đổi, không original assets mới vàoGit. Premium/pool-history vẫn hoãn.

## Kiểm lại và bàn giao

```bash
python3 tools/verify/scene_sprite_contracts.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

**8tests mới**, local **232tests PASS** vớiPillow12 và datasvalidation PASS.
**Final Verify40201293124 SUCCESS** trêncodee5ed7d070:232tests/Pillow12.
Tests không thực thi Unity rendering.

Task peer `arena/20330d0e-windwings-space-shooter-game-p`, xem `docs/HANDOFF_AI_TASKS.md`:
- Dùng typed renderer→Sprite/mesh/material và đầy đủ ancestor chain khi tham khảo scene state.
- Không mặc định PPU100/quad/source pivot là PNGpivot; không trộn flipX/Y vớinegative-scale.
-78serialized activity predicates không phải visible population;61438excludedroots không phải
  “missing assets” hoặc toàn bộ runtime spawn demand.
-303mask-dependent instances làm **SpriteMask/camera/render context** thành follow-up cụ thể
  nếu cần kiểm visibility. Không đòi full asset export để lấy lại dữ liệu đã có.
