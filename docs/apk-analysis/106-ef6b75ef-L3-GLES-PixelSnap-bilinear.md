# 106 — ef6b75ef: source GLES vertex/PixelSnap → varying → genuine APK bilinear

**26/10/2026 · TẠM THỜI · provenance: arena/ef6b75ef.**
Miền batch: **AI-1 texture/shader execution model**. Claim PR12 **6411403047** đã gửi trước
khi bắt đầu, sau đọc sticky50. Không claim transition/particle/driven hoặc live atlas remap,
TMP/sliced/tiled/skinning/gap của digger khác. Không render/Unity readback/screenshot gate.

## Kết quả mới so với105

105 mới có source-atlas UV và7texel-center probes; PixelSnap source recovered nhưng chưa
execute.106 nối **toàn vertex reference (Flip→ObjectToWorld→MatrixVP→optional PixelSnap)**,
UV/color passthrough, perspective-correct varying, **mip0 bilinear từ pixel APK thật**, fragment
premultiply và over blend. Đây là bounded procedural CPU reference, **không** arbitrary GLSL
interpreter/compiler, GPU precision proof hoặc framebuffer renderer.

- Reuse **đúng artifact105 đã handoff6411373032**, code2da541e395c64494b62eeffe47d27f924ebc4fd7,
  Verify40290558746SUCCESS. Source sprite2585/renderer563997/material2/shader10753 giữ identity.
- **4 decoded source vertices ×2 explicit variants** (PixelSnapfalse/true); không generate
  topology mới, không đổi sprite/atlas render-key/UV mapping105.
- **7 source UV seeds →7 fixed viewport pixel centers**, mỗi pixel thử cả2variants =
  **14 queries**, cả14 nằm trong input triangles theo point/barycentric model.
- **5 sampler-only probes**, tách khỏi scene coverage: equal four taps, atlas-neighbor,
  fractional interior và full-texture clamp low/high.
- Recovery từ pinned APK decode lại Texture785 **2048×1024**, raw-object SHA và full RGBA
  SHA **khớp105**. Chỉ giữ **46 unique RGBA8 source texels** đủ các neighborhoods; không
  fabricate missing pixel, không đưa full PNG/texture/APK vào Git.

## 1. Vertex và PixelSnap thật sự execute đến đâu

`tools/verify/l3_shader106_math.py` thực hiện đúng staged multiply/add order trong recovered
GLSL ASCII runs105 (platform5/9). Dùng row-major matrices bên CPU, đọc thành4columns đúng
shader ABI; không transpose nhầm. Flip XY **trước** ObjectToWorld; object position w1 theo
source code (không tự hỗ trợ arbitrary w ở input). World→clip qua MatrixVP, giữ clipZW.
Color varying=(in_COLOR0×_Color)×_RendererColor; UV passthrough không bị round/snap.

PixelSnap path:
1. clipXY/clipW;
2. nhân `_ScreenParams.xy * .5`;
3. round-even;
4. chia nửa screen size, rồi nhân clipW trở lại XY; giữ ZW nguyên.

GLES100 có scalar source `floor(x+.5)` và tie test `y-x==.5 ? floor(.5*y)*2 : y`;
GLES300 dùng roundEven. CPU reference dùng công thức scalar105 đã bóc, test cả ties âm/dương:
±.5→0,±1.5→±2,2.5→2. **Binary64 explicit**, không emulation GPU lowp/mediump/FMA/FPCR.
Magnitude snap bị bound2**24; nonfinite/undefined clipW/non-affine object matrix bị reject,
không giả Unity cũng reject thế. Đây là guard của tool.

`source_contract()` kiểm **byte-located source SHA + statements** của8source variants105,
gồm branches snap/external-alpha; không biến generic13parser diagnostic entries105 thành
valid variants. Statement audit + procedural reference **không là formal equivalence proof**.

### Instance/profile và giới hạn authority

Source resource template **Btn_Resume/Box renderer563997**, world matrix từ current Frame105;
Pause root serialized inactive. Camera **level2:3976** và full viewport1080×2400 được chọn
**explicit**; conventional +Z-forward orthographic MatrixVP từ source camera parameters +
CameraScaler half-height12.000000953674316 của105. Đây **không** observed template placement,
Unity camera matrix upload, renderer property-block/keyword selection hoặc activation trace.
Vertex color white explicit, material _Color/source _Flip và renderer tint dùng source105 như
input policy; không nhận live uniform binding proof. PixelSnap true là **explicit variant
probe**, không nói game đang bật PixelSnap (saved material105 PixelSnap0 vẫn giữ nguyên).

Concrete vertex0:
- unsnapped window **[724.4999881982814,404.517600574684]**;
- snapped **[724,405]**;
- clipZW/UV/varyingColor giữ nguyên; displacement mỗi axis≤.5pixel trong model.

Không round object/local coordinates hoặc UV cho tiện; điều đó sẽ khác source shader.
Test có MatrixVP với clipW1.5 để bắt lỗi bỏ perspective divide/restoreW.

## 2. Varying tại CÙNG fixed pixel, không đổi vị trí probe để che ảnh hưởng snap

Mỗi seed lấy từ7texel probes105, map qua unsnapped source triangles thành window point rồi
chọn **floor(window)+.5**. Giữ point này cho cả snapfalse/true. Tìm inside source triangle
bằng barycentrics trên **current variant window vertices**; outside thì giữ outside, không
fake coverage. Đây là bounded point query, không rasterize framebuffer/MSAA/edge rules.

Smooth varying reference dùng normalized weights `(screenBary_i/clipW_i)/sum(screenBary/clipW)`
cho cả UV và color, không linear UV sai khi clipW khác nhau. Synthetic regression có W1/2/4,
bary1/3 cho UV[2/7,1/7], không [1/3,1/3]. Đây là reference conventional smooth interpolation,
không native GPU interpolation precision/readback; clip-positive-W domain riêng, không tự
cứu behind/undefined triangles.

**5/7 fixed pixel pairs có filtered RGBA khác khi bật PixelSnap**, 2pairs alpha0 giữ cùngRGBA.
Đây là exact CPU-array comparison, không perceptual metric hoặc visual acceptance.
Ví dụ cạnh source_seed5 tại **[726.5,325.5]**:

| Variant | interpolated UV | filtered alpha |
|---|---|---:|
|snapfalse|[0.6404037278798136,0.1864127742876135]|0.05091579864714838|
|snaptrue|[0.6405925451056999,0.18641052245083872]|0.08276148982721251|

Alpha thay đổi vì **interpolation tại cùng window point đổi UV → actual neighbors/weights**,
không do sửa trực tiếp renderer.m_Color.a hoặc dựng tween. Không chuyển alpha thành visibility.

## 3. Actual texture neighborhoods → bilinear → premultiply, không đảo order

Recovery `tools/recovery/l3_shader106.py` decode cùng actual APK Texture785 như105 bằng
UnityPy1.25.4/Pillow12.0.0, kiểm raw-object/full-RGBA hashes rồi lấy46pixels cần cho requests.
Pillow top-left→bottom-left bằng `getpixel((x,height-1-y))`; raw giữ requests, mỗi texel,
SHA tool/request-generator/math/previous-artifact, exact texture metadata.

Source texture filter1/wrapU1/wrapV1. Pinned dump.cs khai **FilterMode.Bilinear=1**,
**TextureWrapMode.Clamp=1** (source enum, không đoán từ ảnh). CPU sampler reference chọn
normalized UV→texel coordinate `[u*W-.5,v*H-.5]`, 4tap weights bilinear, **clamp addresses
vào toàn texture**. Không clamp vào sprite crop, vì sẽ che atlas-neighbor samples thật.
Đây là explicit mip0/raw-UNORM filtering model, **không** native GPU sampler setup/fraction
precision/derivatives/LOD/sRGB readback. Raw texture có **mip_count1/color_space_metadata1**;
giữ numeric metadata, không tự suy/execute color conversion hoặc engine runtime override.

Concrete four-equal-weights tại UV[1438/2048,190/1024] cho RGBA:
**[0.884313725490196,0.48039215686274506,0.1588235294117647,1]**.
Atlas-left-neighbor probe đọc được x1309 (ngoài sprite rect1310 nhưng trong texture), alpha
**1/255**; không tự điền transparent black. Full-texture low clamp lấy actual texel[0,0]
**[69,139,251,0]**, không lấy crop corner. High clamp lấy[2047,1023].

Shader fragment: **filter straight sample trước**, nhân varyingColor, sau đó RGB×alpha;
alpha giữ product alpha. Không premultiply từng texel trước filter. Synthetic regression:
transparent red/opaque blue → filter=[.5,0,.5,.5] → fragment=[.25,0,.25,.5], khác
premult-before-filter=[0,0,.5,.5]. Fixture này là synthetic arithmetic counterexample,
không gọi là pixel APK. Actual14queries dùng đúng46source pixels, có output fragment và
blend trên explicit gray[.5,.5,.5,1] theo One/OneMinusSrcAlpha105.

External-alpha arithmetic có regression nhưng **không fabricate actual _AlphaTex**, material
saved texture envs105 vẫn null, explicit runtime sampler input riêng. Missing evidence luôn
reject (kể cả sparse pixel dictionary); đó là tool policy, không nói GPU bắt buộc4physical reads.
Repeat/Mirror/unknown wrap, missing samples, NaN/Infinity bị reject trong bounded tool.

## 4. Deliverables / kiểm chứng / pins

- `datas/l3_ef6b75ef106.json.gz`: source contract, matrix/profile, both vertex variants,
  fixed-pixel queries/barycentrics/varyings/taps/RGBA/fragment/over, source46pixels, metadata,
  countable counts và input SHA pins.
- Raw `reverse-engineering/raw/l3-shader106/samples.json` từ recovery
  **40291977206 SUCCESS**, bot commitd7e718cfb. First recovery40291858242 failed vì hash Path
  thay vì bytes; sửa và chạy lại, không dùng failed output làm evidence.
- Tools riêng `l3_shader106.py`, `l3_shader106_math.py`; không sửa tools105/other diggers.
- **32 tests mới PASS0.131s**: regenerate equality/current SHA pins, round-even±ties, true
  MatrixVP/Flip/order, nonunitW, varying perspective, same-window UV changes, 4tap mean,
  true atlas-neighbor/clamp evidence, filter-before-premul, alpha/blend/error guards/scopes.
  Full local **1137 PASS270.151s**; CI receipt bổ sung riêng, không coi local là CI PASS.

```sh
python3 -m tools.verify.l3_shader106
python3 -m unittest discover -s tests -p test_l3_shader106.py -v
python3 -m unittest discover -s tests -v
```

SHA256 pins (artifact giữ cùng bảng; inherited manifests/previous105 giữ raw dependency chain):

| Path | SHA256 |
|---|---|
|`tools/verify/l3_shader106.py`|`9ab95bb6e21040720acad3aba21abb13e1702eae15d629af3c37592ae50b5d7f`|
|`tools/verify/l3_shader106_math.py`|`7a5ab6c898b24b2385f715d00882b709924bf50ca8cdb2d82a314ea4d2bdf809`|
|`tools/verify/l3_textured105.py`|`c958e137efc1367a63bc30fec365f3cabfd380a049a184ff097c245d71c17a6b`|
|`tools/verify/ui_composition.py`|`385ce064747d02537c772a72fecd565f1cc1542218749746ed6f01d439de899c`|
|`tools/recovery/l3_shader106.py`|`08e70bac776e7e00a131a246e855bb6c4f1149374a9eb3395814f9a38fd38e90`|
|`datas/l3_ef6b75ef105.json.gz`|`128a014d057ffb7a1a8041802a1820b0855ccb8fdffb6f18f9b93435f91ca6c9`|
|`datas/l3_composition.json.gz`|`d54eb354fc42a8419c1e71fe52be33c5461dec695385fc4deb2a6399c900bae7`|
|`reverse-engineering/raw/l3-textured105/texture.json`|`a093a9ef7dd47dd91d172de1d8d93a9a0f34f683e6d1d924110763fa127c83db`|
|`reverse-engineering/raw/l3-textured105/gpu-analysis.json`|`8e80010fe59b604038ad14003855f147a69f20ec0b4f063dbb436222cd6eb4f6`|
|`reverse-engineering/raw/l3-shader106/samples.json`|`376f8407deb31b54c70837894631c9617558d735255de4ffc30ae7059479c3fc`|
|`reverse-engineering/il2cpp/dump.cs.gz`|`79b4028c6f59ddf203baef99f8982e152518c0224b416f57933d257d4f8c1f9a`|

Artifact SHA256 `62e3b6d274a9077be9eeea9d181b4896c8e49f2d03ec84f4ba52ef1566ea4fcf`.
APK SHA256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; full decoded RGBA SHA256 `94546174b10a687b9b9fe4fd34dc27092c33c63a4527a9d1c251469522ff2293`.

## 5. Peer/status và phần chưa làm

Spec fetched **bab67115f5192d5fa0e17c07920aa63f109a5afa**, DATA_SYNC24.43–44. Peer đã
**ACK105-ef6b75ef6411447910** ở mức artifact SHA/identity/count/value presence/commutation
structure/UV0placeholder; **chưa independent execute** native harness/LZ4/GLES, chưa ACK
custom23 mapping. Không nhận đó là numerical/GPU/native-independent acceptance.

Peer **107-a5a74747** code3ca37f93f/tip403be8b16 được spec ACK mức **artifact-level**
transition replication; không second APK decoder/Unity proof. CI của họ đã xanh theo handoff
6411493961; trạng thái105/106-a5 “CI còn pending” ở snapshot trước không còn dùng làm trạng
thái hiện tại. Claim mới6411524443 của họ là #15 native Animator blending evidence, giữ
ngoài texture/shader batch này. Không import/merge/edit artifact/tool của họ.

Sticky có quy tắc sync APKD1/AI1 khi thêm report. **Own branch không có**
`docs/spec/START_HERE.md`/`tools/verify-claims.py` nên không bịa hoặc chỉnh needle của nhánh
spec/peer; report/artifact branch-prefixed, Verify riêng thêm artifact106 vào paths.
Shared3paths giữ nguyên/absent, không main push/merge/self-ACK.

**Batch cover** source vertex/PixelSnap + varying + actual mip0 neighborhoods/bilinear/
fragment/over ở bounded scope trên. **Vẫn thiếu** native tag23 registration mapping,
actual uniform/keyword/renderer upload, driver/Animator scheduler, GPU precision/sRGB/
LOD/coverage/depth/stencil/raster. No image/frame/render acceptance. Không lấn miền khác.
Peer review nên tái tính round-even clip→window, UV tại cùng fixed pixel, 4tap means/clamp
neighbor, filter→premul order; các phép số học này có thể chạy từ artifact với stdlib,
không cần APK/Unicorn (decode/hash origins/GPU là tầng khác).

### Điều phối mới lúc chốt

PR12 **6411617634** thông báo L2 mở lại thành#18–23 và geometry digger eeb95d5a đã trở lại
(reported tip90c4e4ff9); **6411543326** chấp nhận#16 ở artifact-level, mở#17 independent
raw/APK decoder cho transition. Đây là trạng thái điều phối mới, không dùng trạng thái cũ
“L2 chờ mở/geometry chưa quay lại”. Batch106 vẫn shader/texture theo claim6411403047;
**không** đào/import/merge/sửa work của các miền đó trong batch này. Snapshot sticky-final/
coordination-updates giữ nguồn; bất kỳ batch mới cần claim lại theo bảng mới.

## Receipt106 final

Code **b979cfe657bffe96a2bc89fda184da29e97d7815**, **Verify40292776800 SUCCESS**, job4m48s.
Full local **1137 PASS270.151s**, **32new PASS0.131s**. PR12 handoff
**6411725150** có branch/code/CI/test count/review requests/provenance; raw CI/local/handoff
receipts giữ riêng. Đây là bàn giao nhờ review, **không self-ACK hoặc render acceptance**.
Spec fetched lúc chốt **b1e0035068e4efa53163a4221807e63da52c89a3**; điều phối mới đã ghi
ở trên/update-final.json, không import artifacts hoặc đổi miền theo suy đoán.
