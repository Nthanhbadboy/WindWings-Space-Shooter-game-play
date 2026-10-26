# 105 — ef6b75ef: Pause native order → current state; texture thật → UV → Sprites/Default

**Tạm thời · provenance: arena/ef6b75ef · 26/10/2026.**
Miền của tôi trong batch này: **AI-1 custom binding / driver order / texture-shader**.
Không render, không Unity readback, không screenshot gate. Không sửa tool/data của digger khác.

## 1. Custom binding: điều tra native thật, kết quả vẫn UNPROVED

Animator `level2:4695`, clip `resources.assets:1609`: attribute0/customType23/type212
vẫn **không** được gọi là CRC(m_Sprite) hoặc proven field binding. Thu hồi trực tiếp
`SpriteRenderer.set_sprite@0x278ad60`, span68B đến method kế tiếp0x278ada4:
resolver call0x110cfec, cache function pointer, cuối `br x2`. Body này chứng minh bridge
đến engine setter, **không chứa chứng cứ registration customType23→m_Sprite**.
Raw bytes/file offset và disassembly có trong texture.json/derived artifact.

Search bytes chính xác trên pinned libil2cpp và metadata giữ toàn bộ file offsets trong
`native_search`; thấy tên setter trong lib và m_Sprite trong metadata không chứng minh tag table.
Không suy không thấy chuỗi `customType` thành engine không có mapping. Đây là tìm kiếm hẹp,
không phải audit hết registry/libunity. **Kết luận chưa chứng minh được**, không đổi policy104:
writer mặc định reject; muốn áp phải explicit per-binding policy, log đúng là policy; unknown
mapping không thành null. Tests104 vẫn chạy trong full suite, không tự nâng bằng chứng.

## 2. ONE NEW concrete chain: Board_Pause, không Alert/Border_Info

Root `resources.assets:212696`, Board_Pause690342. Mở rộng nguồn98 bằng đúng235 source
nodes của recipe Pause; header authority giữ nguyên. Hai collider493280/492598 ở raw98 mới
identity-only, **không phải APK mất fields**: recovery105 đọc lại full typed trees, kiểm cùng
raw-object SHA trước khi thay projection. Không sửa/xoá raw98. Tools riêng:
`tools/verify/l3_pause105.py`, dùng lại Frame104 và nested native harness101.

Chạy **toàn body APK Board_Pause.Align@0x12cb128** bằng Unicorn, không chỉ gọi hai marker:

1. source callsite0x12cb150 → top597593.ObjectAnchor;
2. 0x12cb160 → bottom616420.ObjectAnchor;
3. boxBound493280.set_size → set_offset;
4. boxContent492598.set_size → Transform274606.set_position;
5. parentView267691.set_position (native tail branch0x12cb454).

Trace40 hook calls (gồm2 nested-anchor entry hooks) giữ source callsite và owner identity, gồm5 setter calls; engine
getters/setters dùng **cùng current Frame overlay**, không snapshot stale. Literal width14.4
lấy **bytes66666641 tại VA/file-offset0x756dd8**, không dùng rounded JSON constant làm raw.
Nested ObjectAnchor dùng101 source instructions, SafeArea cache và private states104.
Transform↔world dùng explicit affine bridge; engine objects/Camera getters/metadata vẫn stub.

Profile **synthetic1080×2400**, safeRect[0,96,1080,2208], chọn explicit scene2 main3976;
Pause là **resource template**, serialized root inactive. Các lời gọi explicit không chứng minh
engine đã activate/dispatch Start hoặc instantiate prefab trên scene2.

| Current state | trước | sau native Align |
|---|---:|---:|
|top marker worldY|7.900000095367432|9.34000015258789|
|bottom marker worldY|-7.75|-9.190000534057617|
|boxBound sizeY|21.600000381469727|18.530000686645508|
|boxBound offsetY|-1.2000000476837158|0.07499980926513672|
|boxContent sizeY|18|18.530000686645508|
|boxContent worldY|-2.9690001010894775|0.07499980926513672|
|parentView worldY|8|9.34000015258789|
|descendant renderer549984 worldY|-6.460000038146973|-5.119999885559082|

**Start/Align/clip order tách rõ**:
- Source hai anchors playOnStart=false: native Start chỉ bind camera, before==after_start;
  direct Align yêu cầu đã bind. Không giả gọi ObjectAnchor là tự chạy Start.
- Trong Align, top→bottom→collider→content→parentView là **thứ tự source đã execute**.
- Source Refresh test private `align+0x188`; nhánh false gọi Align@0x12c9cb0 rồi store1.
  Artifact giữ bounded instructions của guard; **không execute toàn Refresh/OnEnable**.
- Chosen source-attached Animator498199→idle1495@.25 ghi renderer549984.m_Color.a từ1
  thành **0.5797794461250305**, giữ current world pose đã propagate qua parentView.
- Clip-before-Align và Align-before-clip cho **cùng snapshot cuối** vì ghi khác fields.
  Hai thứ tự là thử nghiệm model, **không** suy Unity scheduler/lifecycle order hoặc animation
  state entry. Phần cross-component scheduling vẫn unresolved; không bán commutation thành proof.

## 3. Genuine APK texture + simple UV join, không làm live atlas remap của AI-2

Cùng Pause, Btn_Resume212670/Box212686 → renderer563997 (drawMode0) → sprite2585
→ exact m_RenderDataKey → Common SpriteAtlas580546 → Texture2D785. Material được nối bằng
qualified PPtr tới globalgamemanagers.assets:2 rồi shader10753; giữ _MainTex/_AlphaTex null
trong saved material, không giả serialized material có texture atlas. Atlas là explicit sampler
input trong probe, không chứng minh engine uniform upload.
Texture **2048×1024**, format numeric47, filter1, wrapU/V1 giữ trong raw; decode **8388608
RGBA bytes** trên recovery runner. Pixels/PNG gốc **chỉ Actions artifact**, không vào Git.
Sprite cropped PNG SHA khớp **exact asset-pack-v2 output**, không vẽ lại.

Decoded103 sprite có **4 vertices/2 triangles**, MeshHelper UV0 là **4 cặp[0,0]**.
Không dùng placeholder đó làm atlas UV. Exact serialized render-key map có
uvTransform=[77.34139251708984,1438,77.34139251708984,190.5]; dùng affine
`u=(localX*x+y)/2048; v=(localY*z+w)/1024`, rectangle[1310,129,256,123].
UV extents số học nằm gần [1310/2048,1566/2048] × [129/1024,252/1024]; giữ chênh floating
source vertices, không snap cho đẹp. Flips đổi positions nhưng không đổi source UV indices.
Source settingsRaw1 là packed=true, packingMode0/tight, rotation0; topology quad đã decode,
không tự generate tight mesh. Đây là **bounded source atlas UV join**, không native Sprite.uv readback, không general/live
atlas override, rotated/tight/sliced/tiled/TMP/skinning generator. Unsupported packing bị reject.

**7 texel-center probes** từ decoded image, origin bottom-left, mỗi cái có UV, triangle,
barycentric weights, reconstructed local point, RGBA8 và output arithmetic. Ví dụ:
(1310,129)=[255,134,2,0], center(1438,190)=[224,117,35,255], cạnh alpha12/26.
Không fabricate missing pixel. Probes chỉ mip0 center bytes/255, **không** tự gọi là engine
bilinear/mip/sRGB/mediump readback. Btn_Resume là nhánh sibling trong Pause: **không** nhận
Align đã move renderer563997; artifact cho thấy nó giữ world pose. Renderer propagate thật của
Align là549984, tách identity rõ thay vì ghép hai nhánh thành một renderer giả.

## 4. Sprites/Default: body thật, không chỉ pass-state inventory

Pinned shader10753, compressed blob SHA giữ ở raw. UnityPy export102 chỉ ra property/pass
text; thử generic ShaderProgram parser105 lộ lỗi format keyword/program payload (13 parsed
entries **diagnostic only**, không lấy làm13 valid variants). Đọc **LZ4-decoded platform
segments5/9** và bóc exact byte-located ASCII GLSL: **8 complete source runs = 2 platform ×
PixelSnap on/off × external-alpha on/off**; mỗi run có source offset/length/SHA.
Không tuyên bố compile/link/GPU execution hay toàn bộ shader variants trong engine.

Source GLES cho:
- vertex XY×_Flip, ObjectToWorld→MatrixVP, UV passthrough;
- varyingColor=(in_COLOR0×_Color)×_RendererColor;
- texel alpha có thể lerp với _AlphaTex.r bằng _EnableExternalAlpha;
- c=sample×varyingColor; output RGB=c.rgb×c.a, output A=c.a;
- serialized blend One/OneMinusSrcAlpha Add (cả alpha); ZWriteOff/CullOff.

CPU bounded model chạy color/external-alpha/premultiplication và over-blend theo công thức
source; binary64 explicit, **không** GPU lowp/mediump/FMA equivalence. Với source opaque texel
center, white explicit vertex/material tint và serialized renderer tint white, RGB=[224/255,
117/255,35/255], A1. Texel alpha0 có RGB nguồn khác0 nhưng premul output[0,0,0,0]; blend trên
explicit gray[.5,.5,.5,1] giữ gray. Có tests tint multiplication, external-alpha, blend alpha,
nonfinite và missing-sample rejection. Shader inputs là explicit choices, không GPU uniform
upload readback; PixelSnap source recovered nhưng **không execute**, không raster/depth/stencil.

## 5. Deliverables, pins và tái chạy

- `datas/l3_ef6b75ef105.json.gz`: branch-qualified artifact, native/current states/order,
  reordered case, Refresh guard, setter bridge, geometry UV, texture samples/shader outputs.
- Raw `reverse-engineering/raw/l3-textured105/{texture.json,objects.json,gpu-analysis.json}`.
- Verification receipts `raw/l3-ef6b75ef105-verification/`; peer snapshot `raw/peer-review/l3-ef6b75ef105/`.
- Recovery **40287660478 SUCCESS**; external original pixels ở artifact
  `l3-textured105-original-pixels-external` của run này. Release cũ vẫn draft.
- **32 tests mới PASS33.925s; full1105 PASS274.466s**. Verify40290558746 SUCCESS trên code2da541e395c64494b62eeffe47d27f924ebc4fd7;
  local/CI PASS không tự là independent ACK.

```sh
python3 -m tools.verify.l3_textured105
python3 -m unittest discover -s tests -p test_l3_ef6b75ef105.py -v
python3 -m unittest discover -s tests -v
```

SHA256 input pins (artifact cũng kiểm từng pin; inherited chunk manifests kiểm hashes bên dưới):

| Path | SHA256 |
|---|---|
|`tools/verify/l3_textured105.py`|`c958e137efc1367a63bc30fec365f3cabfd380a049a184ff097c245d71c17a6b`|
|`tools/verify/l3_pause105.py`|`33f60cee6b471b0d549aa0f6235a13f94c7c11c68efea98cbd78902e22ecfcbd`|
|`tools/verify/l3_frame.py`|`5f85c803ec403fb39ca9a42c963998adfe43362a172120b65f675dceb03e9f25`|
|`tools/verify/l3_layout_emulator.py`|`866ff56ff7939669614794a31fa16ccfe4afca15b3f21e37b4ac9af7d8b366b2`|
|`tools/recovery/l3_textured105.py`|`8afe57878424c38ce69169c40f1deb1e3415a9ba351f8886d56b362e3aa9c593`|
|`datas/l3_scene_chains.json.gz`|`3be47092c0967c40c5f9abf1ec28eeba401bb1bf2cf0bec003a627e982d62eeb`|
|`datas/l3_visual_surface.json.gz`|`67bc398ec43073b66efa614af54e96330369784a57ab46c04a7a0b30edd796ef`|
|`datas/l3_layout.json.gz`|`217aa1c7ce9529f752de5d712845c36d9b51a1c16aa619bf34ff9fb9a8e57022`|
|`reverse-engineering/raw/l3-chain/index.json`|`6ea5ddeb943b8f07637d31a26502d6991156fd309515650445f04506e65bd8c9`|
|`reverse-engineering/raw/l3-ui-native/method-bytes.json.gz`|`e25b39d8293b2d2c45b90d39b697b1c57b5a876f82c0820330a9be65d0dde8ed`|
|`reverse-engineering/raw/l3-ui-native/native/Board_Pause.json`|`e2eacd7d93191620fd5c42558c641ab51c195e6ccf0f8b2c181ecc8a770d76ea`|
|`reverse-engineering/raw/l3-ui-native/native/Board_Pause.asm.txt`|`a991f2773648c15354f84d58cfd7bbb75dcb06f88bcca6453003e7f7e51761f0`|
|`reverse-engineering/raw/l3-textured105/texture.json`|`a093a9ef7dd47dd91d172de1d8d93a9a0f34f683e6d1d924110763fa127c83db`|
|`reverse-engineering/raw/l3-textured105/gpu-analysis.json`|`8e80010fe59b604038ad14003855f147a69f20ec0b4f063dbb436222cd6eb4f6`|
|`reverse-engineering/raw/l3-textured105/objects.json`|`5f5137bdeafe48f45c6b11a54a0650000149b65c0cc1382c886fca0da5bf9607`|

APK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; lib `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`; metadata `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`.
Atlas RGBA `94546174b10a687b9b9fe4fd34dc27092c33c63a4527a9d1c251469522ff2293`; cropped PNG `ed47cf756a2798f114f87d4709817dfc5f24914f3324999f5ac196141bb8a53b`.
Artifact SHA256 `128a014d057ffb7a1a8041802a1820b0855ccb8fdffb6f18f9b93435f91ca6c9`.

## 6. Peer status và ranh giới bàn giao

Đã đọc HANDOFF, reports98–104, DATA_SYNC24.29–40, PR12 feedback. Peer spec mới nhất đã fetch
**7bdd5003285f831abb5ef926122893abdc59f00d**; ACK104-final = **5/5 artifact arithmetic
reproduction**, không độc lập chạy native harness/H8/rollback/tag23. Không còn ghi104 “chưa
peer reproduction”. PR12 mới có ownership6410868087 và sticky6410945198; claim-confirmation
6411008329 ghi trung thực batch đã bắt đầu theo explicit user assignment trước sticky,
không nhận pre-start claim hồi tố. Không thấy nhánh AI-2/AI-3 ở lần kiểm remote này; không
suy họ không làm việc. Không sửa shared3 paths (nhánh này vốn không có các path đó).

Scope batch này đã cover: **một Pause native Align chain tới consumer thật + clip current-state,
một genuine atlas/simple-UV join và bounded Sprites/Default arithmetic**. **Chưa** cover native
customType23 registry, cross-component engine scheduling, GPU precision/uniform bindings/live
sampling/raster. Không nhận toàn miền AI-1 hoặc L3 đã xong, không chuyển sang miền AI-2/AI-3.
Peer review cần tái tính collider size/offset, trace order/tailcall, renderer propagation,
clip/Align commutation, zeroUV→source-render-key UV, texel orientation và premultiplied blend.
Không tự ACK, không merge, không push main.

### Cập nhật peer ngay trước receipt

Spec tip **b198574077d1a4edb367157eed98111d8e5aa201**, DATA_SYNC24.41/sticky49: đã có
**105-a5a74747** (particle/transition/driven), spec ACK6411130516, source modeld446d47d5/
head25ac3b46b; CI ID còn pending theo spec. Đó là peer-reported contract audit, **không phải
independent audit của tôi**. Không kéo/import tool/artifact đang làm của họ. Claim mới6411110604
reachability/driven coverage không thuộc batch này. Snapshots/update49.json giữ nguồn và SHA;
trạng thái “chưa thấy nhánh khác” phía trên là lần kiểm đầu batch, không phải trạng thái chốt.

### Portable arithmetic audit

Initial Verify40289718130 failed regression on Python3.12; local runner is3.11. Barycentric
reconstruction dùng builtin sum có khác thuật toán giữa3.11/3.12 (compensated sums từ3.12).
Đã thay bằng explicit sequential binary64 helper103; không gọi khác biệt này là engine mismatch.
Thêm regression kiểm accumulation order; giá trị sample geometry trên3.11 không đổi, chỉ tool
SHA pin đổi. Workflow failure giờ đưa bounded test-log tail vào check annotation để audit được.
Final full local/CI receipt bên dưới supersede initial run, không lấy failed CI làm PASS.

## Receipt105 final

Code **2da541e395c64494b62eeffe47d27f924ebc4fd7**, Verify **40290558746 SUCCESS**, job4m31s.
Final full local **1105 PASS274.466s** / new **32 PASS33.925s**; supersede31/1104 trước
portable-sum fix và failed initial run40289718130. Native data và sampled geometry không đổi;
sequential CPU accumulation giờ tường minh qua cả Python3.11 local/3.12 CI. Raw CI/local/handoff
receipts giữ riêng. Đây là bàn giao nhờ review độc lập, **không self-ACK/Unity readback/render**.
