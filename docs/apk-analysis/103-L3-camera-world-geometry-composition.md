# 103 — Camera → world pose → geometry → layer gate/clip → composition recipe

**Tạm thời, source APK đã pin + explicit numerical model. Không phải Unity frame acceptance.**

## Đã nối xuyên chuỗi

Không cần recovery mới: merge raw101 (`l3-layout-native/objects.json.gz`) với raw102
(`l3-visual-surface/`) bằng **qualified file/pathID**, kiểm **1760 overlapping bodies có cùng
raw SHA** và duplicate pointer edges không xung đột.57480 unique objects trong merged graph.
Không đổi nguồn101/102 để làm lệch các hash đã bàn giao.

- **11380 renderer world poses** đều dựng được từ typed Transform/RectTransform parent PPtrs,
  gồm root local TRS (khác matrix layout-root frame trong95). Parent thiếu/unresolved/cycle
  không được thay bằng identity. Activity là serialized parent-chain conjunction, không visibility.
- Trong scope102: **558 renderer thuộc known serialized scene files level0–3**;
  **10822 thuộc asset templates**, không tự coi đã được instantiate vào scene.
- Sáu camera nối world pose, source projection parameters, culling mask, clear flags, depth,
  display/render-target descriptors và native size-writer bank101. Sharedassets0:79 vẫn là
  camera template, không tự chèn vào các scene.
- **1104 same-source-scene camera/renderer pairs**:558 layer-mask pass,546 fail. Chưa cộng
  footprint/alpha/shader để gọi đó là visible. Không so mọi prefab với mọi global camera.
- Camera depth groups giữ ties và clear/target descriptors. Chưa tạo total draw-order từ
  sortingLayerID, cũng không coi các camera thuộc scene khác nhau là một live camera stack.

## Alert — scaler/native → generated position geometry → camera → alpha

GO `level2:110`, renderer5105, scaler6686, Animator4647 và source parent2497 được nối đủ.
Synthetic profile1080×2400, giả thiết CameraScaler main/UI size như profile:

1. CameraScaler half-height **12.000000953674316**.
2. Bounded native ObjectScaler.Start và model đồng ý size
   **[10.800000190734863,24.000001907348633]** (default finite static clamp101).
3. Source Sprite114 có drawMode1, border0, pivot(.5,.5), PPU50. Bounded **position-only
   zero-border sliced rectangle model** dùng size đó, không scale bừa native tight-mesh
   5.12×5.12 thành quad nếu chưa kiểm draw mode/border.
4. Serialized world z=1; camera-local depth11 ở Game Camera3975 (world z=-10),
   depth21 ở Main Camera3976 (world z=-20). Cả hai đều có triangle/box footprint giao viewport.
5. Nhưng renderer layer5: **Game Camera mask7959 không chứa layer5**;
   **Main Camera mask32 có chứa layer5**. Không dùng Game Camera chỉ vì nó tên “Game”.
6. Main footprint theo model float64:
   `[0.000033378598385258584,0,1079.9999666214017,2400]` px, origin bottom-left.
   Gần full viewport, không gọi đây là engine-exact pixel coverage.
7. Source-attached alert42@.0625 cho renderer.m_Color.a **.3921568840742111** từ102.
   Không tự apply trigger/state transition, không biến alpha đó thành một rendered RGBA frame.

Serialized scene2 camera depth-1/clearFlags2 (Game Camera) rồi depth0/clearFlags3 (Main Camera)
được giữ riêng. Đây là snapshot composition descriptors, không phải quan sát actual render pipeline.

## Position geometry và clipping đã làm thật đến đâu

`l3_composition_math.py` có affine inverse/point, uint32 layer test và conventional mono
orthographic projection, camera local+Z forward. Triangle clipping qua **6 planes** giữ cả
trường hợp mọi original vertex đều ngoài viewport nhưng triangle cắt qua màn hình. Không dùng
“một góc vào screen” hay center-only heuristic. Near/far/behind/degenerate/crossing cases có test.

- Simple sprite: dùng decoded local vertices/triangle indices, modeled flipX/Y không sửa raw.
- Sliced sprite: **chỉ zero-border, positive finite size** được generate thành rectangle;
  border khác0/tiled được trả status not_generated, không tự dựng quad thay thế.
- Static MeshRenderer có source mesh: dùng base decoded position geometry.
- TMP/procedural/skinned/particle/line/trail generation chưa được áp bởi probe này.
- Chưa làm UV regeneration, live SpriteAtlas remap, skinning/deformation, vertex shader,
  framebuffer rasterization, stencil/alpha test, occlusion, depth buffer hay final blend.

Projection giả thiết conventional viewport aspect và orthographic matrix. Camera.aspect/custom
projection overrides, XR và render targets không được simulate. Scale/shear/reflection camera
không lặng lẽ biến thành zoom; model từ chối non-rigid camera. Arithmetic float64 + raw near-unit
quaternion TRS, **không phải numerical fidelity proof của Unity transforms/projection/geometry**.
Pixel polygons có positive area threshold1e-10 để bỏ degenerate/touch-only output.

## Dựng scene và nguồn giao nhau

`datas/l3_composition.json.gz` chứa source matrices/activity, scene/template classification,
camera/depth descriptors và mask pairs. Các matrices là serialized/template poses, không phải
Awake cache hay runtime placement. `probe` từ chối template/cross-scene nếu không có explicit
**full renderer-local→world override matrix**. Override không được gọi là observed instance pose;
activity flags vẫn là serialized flags, không thay cho live activation readback.

Recipe10 Pause nối8 renderer composition records; chúng đều là asset templates. Camera bank6
là global candidates, không auto-selected stack. `composition` đi cùng surface102 và native layout101,
không ghi đè layout-frame matrices cũ hay tự chạy mọi anchor Start/Align.

```sh
python3 -m tools.verify.l3_composition
python3 -m tools.verify.l3_composition --alert --width 1080 --height 2400 --time .0625
python3 -m tools.verify.l3_recipe --root 10 --include-raw --out /home/user/pause.json.gz
```

Raw103 receipts tại `reverse-engineering/raw/l3-composition-verification/`; giữ cả native scaler,
geometry model, per-camera mask/footprint và clip probe, không thay chúng bằng screenshot.
**31 tests mới; full1043PASS202.733s**. Regeneration equality, current input hashes, source scene
separation, parent failure semantics, all-vertices-outside crossing triangle, near/far, rigid-camera
checks, real Alert chain và scoped recipe được kiểm. Remote CI receipt bổ sung riêng.

## Phần còn lại chính xác

Nguồn layout101 vẫn có1 unclassified built-in-resource header; raw102 vẫn có1 Player_Attack_2
header-only và7 builtin particle mesh references chưa resolve.103 không xoá/“chữa” các tình trạng
đó bằng giả định. Source scope vẫn là585 layout owners + closure/context, chưa bao toàn bộ APK.

**L3 chưa hoàn tất.** Geometry/layout generation ngoài bounded cases, runtime controller/driver
application, actual shader/particle/text/spine execution và composition frame còn phải nối tiếp.
Không lấy screenshot làm gate, không vẽ lại game, không nhận model PASS làm render PASS.
Peer review độc lập; không tự ACK.

## Receipt103

Finalcode **dddd75aed**, Verify **40240026886 SUCCESS**, full1043localPASS202.733s.
Raw CI/handoff receipts giữ riêng; PR12 đã nhận peer review request, chưa independent ACK.
