# 104 — cập nhật peer, góp ý, và áp writes vào cùng modeled frame

**Tạm thời. Source APK là authority; viewport/order/policy explicit là model inputs, không là
observed Unity frame. Không có render acceptance.**

## Cập nhật và góp ý đã đối nguồn

Peer head **23bf66c76f795f97ec4ae13efd380b086c62c3f5**, đã đọc DATA_SYNC §24.34–24.36
và DESIGN_READINESS; snapshot nguyên văn +SHA ở `raw/peer-review/l3-23bf66c7`.
PR12 có ACK101/102/103, đối count/identity/mask và giữ ranh giới model≠render. Không tự ACK.

Nhận xét: ACK giúp phát hiện sai sync nhưng không thay cho numerical/native audit. Headline
“Alert chain full”/“geometry làm thật” cần hiểu là **source/model đến footprint**, không phải
full visual/runtime. Không dùng số file datas/ hay số tests như tỷ lệ hoàn thiện bộ mặt game.
Chuyển review sang reproduction/counterexamples: Start false vs direct Align, propagation,
cache khi camera đổi, f32 write rounding, rollback và encoded pointer binding.

## Gap103 được xử lý, không chỉ thêm contract

Trước103, layout/scaler/clip/projection được probe độc lập. `tools/verify/l3_frame.py` tạo
**một shared modeled state** trên typed source graph, rồi áp các operation theo thứ tự caller:

1. Chọn modeled Camera.main explicit; CameraScaler contract cập nhật half-height model.
2. Native bounded Start/ObjectAnchor/ObjectScaler thật sự chạy AArch64 source bodies bằng
   harness101; so model, lấy local-position/renderer-size writes và persist vào state.
3. Chosen source-attached clip-local channels được convert thành typed writes, float32 store.
4. World matrices/activity của descendants được đọc lại từ overlay, không dùng snapshot stale.
5. Geometry/projection dùng current sprite/size/color/pose và current camera pose/mask.

Không tự chạy mọi source callback, không phát trigger, không đoán Unity lifecycle order hoặc
select controller state. `Start` có thể được gọi explicit như probe method body, không có nghĩa
Unity đã dispatch nó khi component/ancestor inactive.

### Case Alert: size và alpha cùng renderer

Explicit scene2 camera3976, synthetic1080×2400, renderer5105/scaler6686/Animator4647:

| State trong model | sizeY | stored alpha | projected vertical bounds |
|---|---:|---:|---|
| serialized after modeled camera resize |19.200000762939453|0|240.000038…→2159.999961…|
| native scaler + alert42@.0625 |24.000001907348633|.3921568989753723|0→2400|
| subsequent fade43@.25 |24.000001907348633|0|0→2400|

Coefficient sample102/103 là **.3921568840742111** (double model); float32 field store là
**.3921568989753723**. Giữ cả hai, không gọi sai khác này là asset mismatch hay engine precision
proof. Alpha về0 không xoá geometry; không biến mask/footprint thành một boolean “visible”.

### Case Border_Info: Start không được tự biến thành Align

`level2:7048 UIObjectAnchors` trên GO1414 Border_Info / renderer5739; serialized playOnStart=false.
Native Start bind modeled main camera nhưng không ghi position/capture anchor root. Explicit
ObjectAnchor tiếp theo đổi worldY **7→8.440000534057617** trong cùng profile safeRect
[0,96,1080,2208]. **320 descendant Transform** nhận cùng world-Y delta1.440000534057617.

Sprite con **level2:5452** có simple position geometry: pixel bottom1717.700156805613→
1861.7001987672797, delta≈144.0000419616667. Root renderer5739 có nonzero border nên generator103
vẫn trả not_generated; không lấy propagation test để dựng một quad giả cho root đó.

Private anchor state giữ start/root/cachedZ qua calls; safeArea cache dùng chung giữa anchors
trong một Frame, không tự refresh khi camera/safeRect đổi nếu cache còn nonzero. Mỗi Frame là
một isolated modeled world, không phải nhiều Unity objects có static cache riêng. Caches không
được reset chỉ vì có viewport/profile mới.

## Write semantics và phát hiện pointer quan trọng

- Source scalar field hash phải unique và target unique. Transform position/quaternion/scale
  có bounded writer; Euler/invalid quaternion/unknown channels bị reject, không silently skip.
- Boolean0/1, integer integral, finite float32 stores. Current MonoBehaviour public anchor,
  fixed/play flags được đọc từ state, không bắt buộc lấy lại serialized baseline.
- Clip transaction lập plan rồi commit; gặp unresolved/ambiguous/unsupported write thì không
  giữ lại nửa clip. **Atomicity này là bảo đảm của tool, không là Unity exception semantics.**
- Root mount là full world placement explicit, được đổi thành parent bridge để root vẫn có
  thể bị driver/clip move sau mount. Không hard-freeze root world matrix che mất writes.
- Pointer override là runtime qualified-object reference, không bịa serialized fileID mới.
  Invalid/unknown mapping không được coi là null clear; type/body checks giữ rõ.

Source clips có sprite bindings **attribute0/customType23/type212** (ví dụ Animator4695 /
resources clip1609). Field này **không thể gọi là CRC(m_Sprite)**. Default writer từ chối;
caller có thể truyền explicit per-binding field policy `m_Sprite`, kiểm source field và mapped
object type Sprite, log là `explicit_custom_binding_field_policy`. Test có áp actual source clip
với policy, nhưng **chưa coi tag23→field là native engine mapping được chứng minh**. Các pointer
fields ngoài bounded sprite/mesh/uiCamera vẫn reject. Không tự chọn effective override-controller
clip, skinning hay dynamic asset lifecycle từ source closure.

## Artifact/API/recipe

- `datas/l3_frame_cases.json.gz`: hai complete ordered model cases, before/after/current fields,
  native inputs/outputs, private cache/logs, descendants và projected child. Source/tool SHAs pin.
- `Frame` cho phép clip application, native layout/scaler writes, explicit root mount và projection
  trên cùng state; old raw trees không bị sửa, các Frames độc lập.
- Recipe chỉ gắn `frame_application` contract, **auto_execute=false**, yêu cầu explicit instance
  context/order. Không áp hai scene2 case vào mọi prefab recipe.

```sh
python3 -m tools.verify.l3_frame
python3 -m unittest discover -s tests -p test_l3_frame.py -v
```

**29 tests mới; full1072 localPASS219.316s.** Có regenerate equality, actual source native
Start/Align/cache,320-child propagation, f32 alpha, failed transaction rollback, mount+root writes,
raw immutability/isolation, exact pointer policy vs unknown→null, wrong camera/clip and recipe guard.
Synthetic fault-injection tests được tách khỏi actual source cases, không phải dữ liệu game.

## Chưa hoàn tất, bước tiếp

Đã apply writes vào modeled state, chưa Unity render/frame execution. Model/native harness vẫn
chia sẻ float64 affine bridge và metadata/engine stubs. Clip interpolation là model coefficients,
không engine blending/normalized quaternion or scheduling. Position geometry vẫn bounded103;
UV/live atlas, nonzero-border/tiled, TMP mesh, skinning/spine, particles và shader raster/blend
chưa chạy ở đây. Nguồn101/102 gaps vẫn nguyên, không được reset bằng pass tests104.

Ưu tiên tiếp: giải native/custom binding và driver order trên concrete chain, tiếp đến textured
geometry/shader execution dùng media APK, không kéo dài bằng count-only ACK. Không screenshot
gate, không redraw; L3 vẫn **một phần**, peer reproduction chưa phải render acceptance.
