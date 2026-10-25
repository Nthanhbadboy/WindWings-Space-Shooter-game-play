# 101 — Camera → safe-area → UI anchors/renderer → recipe

**Tạm thời, chỉ dữ liệu APK đã pin. Không phải Unity runtime/render acceptance.**

## Chuỗi đã thực hiện

- Recovery GitHub **40234506938 SUCCESS**, raw tại `reverse-engineering/raw/l3-layout-native/`.
  Native helpers/cells, method bytes và toàn bộ target-class scan được giữ nguyên cùng manifest
  7 file không trùng, kiểm SHA trước khi dựng contract. APK/native/metadata SHA nằm trong raw index.
- Quét **125453 MonoBehaviour headers**: nhận diện **584 TuPro.UIObjectAnchors +1 ObjectScaler**.
  **1 header chưa phân loại** (`resources.assets:580792`, thiếu `unity default resources`);
  không được coi header đó là chắc chắn không có target class. Typed read errors:0.
- Bounded context **2526 objects**, 9161 PPtr edges resolved/660 null, 0 unresolved trong context này.
  Đây không phải toàn bộ visual components của mọi màn hình. Đủ parent poses cho585 targets;
  tất cả invertible trong affine bridge được công bố, 0 pose errors.
- Sáu camera được nối lại với **sáu native CameraScaler writer bindings** đã bóc trước đó.
  Bốn serialized MainCamera-tag candidates thuộc các scene khác nhau, không phải bốn camera
  chắc chắn đồng thời sống. 576 anchors thiếu serialized uiCamera;8 có liên kết explicit.
  Không tự chọn Camera.main từ một danh sách global/prefab.
- `Start` native gán Camera.main nếu uiCamera không qua `UnityEngine.Object.op_Implicit`;
  chỉ gọi ObjectAnchor nếu playOnStart khác0. Native Start được thực thi với4 tổ hợp
  camera-null/explicit × playOnStart false/true. **Gọi ObjectAnchor trực tiếp không tự chạy Start**.
  Contract lớp áp dụng cho584 typed instances, không đồng nghĩa đã quan sát Unity scheduling.
  461 serialized playOnStart=true,55 fixed-max=true; flags có thể bị runtime đổi.
- Join từ bank100 giữ92 potential call links trên85 anchors trong scope cũ; không gọi đó là
  complete caller census cho584 anchors. Pause GUIBoardPause690342.Align: callsite0x12cb150
  →597593(top),0x12cb160→616420(bottom). Recipe10 chứa bảy scoped anchor records.

## Semantics lấy từ native, không suy từ screenshot

Enum từ dump.cs: None0,Center1,Bottom2,BottomLeft3,BottomRight4,Top5,TopLeft6,
TopRight7,Left8,Right9. GetRootAnchor jump bytes `00090f03070d0a10`; roots ±5.4/±9.6
là binary32 đọc từ literal cells và được kiểm bằng native execution.

GetRoot chỉ capture world start và local.z một lần. General path ghi world position rồi
restore local.z; Left/Right chỉ sửa world-X, giữ current worldY/Z, **không restore local.z**.
None/Center cũng đi đường general setter, không được tối ưu thành “skip”. Parent rotation
có thể làm restore local.z thay đổi worldXY; model giữ private state qua nhiều lần gọi.

Fixed-max: min(UI half-height, ObjectScaler.clampCamSize) và aspect clamp
[0.43478259444236755,0.75], ảnh hưởng X. Top/bottom dùng SafeArea từ **Camera.main**,
không dùng fixed UI clamp; bỏ qua horizontal insets. Cache safeArea chỉ recompute khi
ít nhất một trong top/bottom bằng0; không giả định đọc lại mỗi frame.

ObjectScaler.cctor cho default **12.420000076293945**, nhưng đây là public mutable static,
không phải hằng runtime bất biến. CLI/model hỗ trợ finite `clamp_value` override; NaN/Inf
không thuộc domain kiểm chứng này. Full mode height=H+H; non-full=(H*currentHeight)/f32(9.6);
width không đổi. Mọi phép scalar liên quan được làm tròn binary32 theo thứ tự native.

## Probe có actual serialized identities, viewport là synthetic

Profile thử1080×2400, safeRect[0,96,1080,2208], CameraScaler dự đoán half-height
**12.000000953674316**. Giả thiết main/UI cùng size này và Awake pose bằng serialized pose:
Pause top597593 worldY **7.900000095367432→9.34000015258789**, model=native.
Probe riêng H14 cho worldY11.180000305175781; không gán các số này cho điện thoại thật.

ObjectScaler **level2:6686→SpriteRenderer5105**, cùng owner **GO110 `Alert`**, drawMode1, width10.800000190734863.
Với H14, full/clamp true: height24.84000015258789. Sprite identity
`sharedassets2.assets:114`, catalog PNG256×256/SHA được nối; material
`globalgamemanagers.assets:2`. Media vẫn dùng asset-pack artifact, không đưa ảnh gốc vào Git.
Đây là size/identity chain, không phải bằng chứng shader/draw-call đã render.
Owner còn có Animator4647: có PPtr/type metadata nhưng body không nằm trong bounded layout
context, cũng chưa có attachment trong bank animator-programs hiện tại. Giữ component refs
và snapshot flags rõ ràng; không gọi alert renderer là background hay coi visual alert đã hoàn tất.

## Deliverables và cách tái chạy

- `datas/l3_layout.json.gz`: source hashes, global585 typed instances, camera writer bank,
  parent/world poses, conditional native callers,20 anchor-mode native comparisons,
  four scaler-mode comparisons và synthetic full-chain probe.
- `tools/verify/l3_layout_{math,emulator}.py`, `l3_layout.py`: model, AArch64 Unicorn harness,
  regeneration và actual-instance CLI. Recipe gắn scoped layout + global camera candidates.
- `reverse-engineering/raw/l3-layout-verification/`: input viewport, actual-instance CLI
  outputs, local/remote receipts. Raw source riêng vẫn được giữ, không thay bằng báo cáo.

```sh
python3 -m tools.verify.l3_layout
python3 -m tools.verify.l3_layout --instance 597593 \
  --viewport reverse-engineering/raw/l3-layout-verification/viewport101.json
python3 -m tools.verify.l3_layout --instance 6686 --file data.unity3d/level2 \
  --viewport reverse-engineering/raw/l3-layout-verification/viewport101.json
python3 -m unittest discover -s tests -v
```

CI pin Unicorn2.1.4, Capstone5.0.3, Pillow12.0.0. Local full984PASS160.186s;
27 layout tests PASS sau chỉnh boundary finite clamp; final full-CI receipt cập nhật riêng.
Regeneration equality được test, không chỉ assert số lượng.

## Ranh giới chính xác, phần tiếp theo

Harness thực sự chạy bounded instructions từ APK nhưng metadata/init, live engine objects,
Camera getter, Transform setters đều stub. Native/model **dùng chung float64 affine bridge**:
không phải kiểm độc lập độ chính xác Unity Transform. Không biết actual loaded scenes,
Camera.main selection, live Screen.safeArea, Awake cache/activation ordering từ những probe này.

Layout gap đã được đào xuyên camera→anchor/renderer→recipe ở mức source/model này;
**L3 chưa hoàn tất**. Tiếp theo là nối geometry/material/font và particle/shader/composition
execution vào scene construction, cùng engine animation transition/blending còn thiếu.
Không lấy screenshot làm gate, không vẽ lại UI, không gọi native arithmetic PASS là render PASS.
Peer review phải độc lập; không tự ACK.
