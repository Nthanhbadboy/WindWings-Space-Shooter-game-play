# 78 — CameraScaler.Awake ghi lại orthographicSize theo Screen ratio

**25/10/2026 — tạm thời/static native proof; không phải device/runtime-render approval.**

## Kết quả chính

Ortho size≈9.6 trong snapshot report77 **không phải giá trị cố định cho mọi màn hình**.
Captured `CameraScaler.Awake` tailcall `ResizeCameras`, nơi có Screen.height/width và
Camera.set_orthographicSize. Công thức danh nghĩa:

`setterArgument = max(((float)Screen.height / (float)Screen.width) * 5.4f, 9.6f)`

**Chuyển cảhai dimensions sangfloat trước khi chia**; C# integer division height/width
không mô phỏng nativeSCVTF/FDIV này.

Đây là consumer native đã đọc, không suy từ screenshot hoặc target resolution. Không có
projection/UV/stencil/visibility simulation. Không coi dữ liệu này đóng mọi camera writer.

## Raw và provenance

- Collector `tools/recovery/camera_scaler.py`; workflow `recover-camera-scaler.yml`.
- Recovery **40202623509 SUCCESS**, bổ sung exact float-pool bytes
  **40202782008 SUCCESS**, raw bot **f84462770**.
- `reverse-engineering/raw/camera-scaler/components.json.gz`:125453parsedheaders,
  **5capturedCameraScaler components/6nonnull camera refs**,1known built-in header error.
- `native/CameraScaler.{asm.txt,json}`:3method records, không size-capped.
- `native-data.json`:2raw4byte pool slices +VA/fileoffset/SHA/float32, nativeSHA pin như77.
- `index.json`: source hashes và dump hash; raw typetree giữ riêng parsedscriptpointer,
  không dùng generated m_Script sai để join class.

5component/camera bindings:

| Owning file / scaler | Camera array order | Native write order |
|---|---|---|
|level0:89|58|58|
|level1:52|39|39|
|level2:6678|3976(UI),3975(Game)|3975(Game),3976(UI)|
|level3:2391|1308|1308|
|sharedassets0.assets:121|79|79|

**Cả5scene cameras trong77 đều được bind** và freshcamera object hashes/trees khớp snapshot.
Sharedassets camera79 là serialized reference, chưa chứng minh prefab đó thực sự được spawn.
Class scan còn1unclassified built-in header; không tuyên bố census runtime tuyệt đối.
Component/gameobject serialized fields giữ nguyên, không tự biến chúng thành chứng minh
thứ tự Awake/OnEnable hoặc toàn bộ lifecycle Unity.

## Native path và exact literals

- Awake entry `0x141d70c` →ResizeCameras `0x141d710`.
- `Screen.get_height 0x27665e4`, sau đó `get_width 0x27665bc`.
- Height giữ ởw20; cả2ints được `scvtf`; `fdiv s0,s0,s3`; `fmul` factor;
  `fmaxnm s8,s0,s2`; setter `Camera.set_orthographicSize 0x275e1b0` nhận cùngs8.
- Camera array field0x20, loop từlength−1 xuống0. Không đoán order từtên camera.
- Captured code dùng **whole Screen dimensions**, không đọc từngcamera.pixelRect/aspect
  hoặc kích thước screenshot để tính giá trị này.
- Null array/camera pointer đi failure helper path0x110d250; không phải skip-null loop.
  Không thêm null-repair vào APK fact. Captured6refs đều nonnull.

| Pool VA | Little-endian bytes | Exact decoded binary32 |
|---|---|---:|
|0x756f00|cdccac40|5.400000095367432|
|0x756fb8|9a991941|9.600000381469727|

Native exporter JSON cũ hiển thị rounded5.4/9.6; không lấy rounded text làm bit-pattern proof.
Contract dùng raw4bytes, giữ cảinputsSHA vàsource offsets.

### Method boundary note

Raw exporter có minimum8bytes: Awake thực tế chỉ4bytes nên record có thêm firstinstruction
của ResizeCameras ở0x141d710. Raw giữ nguyên. Verifier clip semanticAwake instructions
bằng nextdeclaredRVA từdump, chỉ giữ branch0x141d70c. Không diễn giải prologue của method
sau thành code Awake và không gọi raw8bytes là exact semanticbody.

## Arithmetic model, không phải kết quả đo thiết bị

`datas/camera_scaler_contract.json`, verifier `tools/verify/camera_scaler_contracts.py` giữ
8native checks, resolvedcalls, component bindings, float pool và mẫu arithmetic.
Model dùng positive signed-int32 width/height, nominal binary32 rounding sau conversions,
divide/multiply; runtimeFPCR vàdevice execution không được capture.

| Width×height giả định | Modeled setter argument |
|---|---:|
|1080×1920|9.600000381469727|
|1080×2400|12.000000953674316|
|1920×1080|9.600000381469727|
|720×1280|9.600000381469727|
|390×844|11.68615436553955|

Model dự đoán setterargument, không phải Unity property readback; engine setter internals
chưa thực thi. Các kích thước này **chỉ là test inputs**, không phải đo phone của user hoặc capture APK.
Không dùng số rounded12.0 để khẳng định bit-identical output. Màn hình cao hơn có thể làm
size tăng; giữ9.6 cố định trong implementation sẽ không mô phỏng consumer này.

Model từ chối width/height0,negative,non-int/outsideint32. Đây là **model domain restriction**,
không khẳng định native có input-validation hoặc fallback cho các trường hợp đó.

## Những gì chưa đóng

- Có Awake→Resize không chứng minh Resize không thể được gọi lại, không có writer khác,
  hoặc rotation/resolution-change được xử lý thế nào. Không thêm update-every-frame từguess.
- Setter chỉ ghi orthographicSize trong methodđangxét; không suy camera source transforms,
  culling masks/depth hoặc actual frames không thể đổi ở nơi khác.
- Game camera7959/UIcamera32 vẫn là source context của77; shared scaler vàscene scaler
  không bị gộp thành một global camera singleton.
- No Unity lifecycle/FPCR/rendering, world projection, mask stencil hoặc screenshot match.
- No APK/media export mới;originalpixels/TTF/nativebinary không vàoGit, release khôngđổi.
  Premium/pool-history vẫnhoãn.

## Tái kiểm và task peer

```bash
python3 tools/verify/camera_scaler_contracts.py
python3 -m unittest discover -s tests -v
python3 datas/validate.py
```

**Local247tests PASS** vớiPillow12, datasvalidation PASS; finalVerify của code bàn giao
kiểmriêng.

8tests mới: regeneration/rawfloatbytes, aspect model/clamp/domain,5scene bindings +shared
scope,reverse array writeorder, Awake boundary clipping, native checks/classscan caveat.

**Task peer** `arena/20330d0e-windwings-space-shooter-game-p`, xemHANDOFF:
1. Sửa giả định ortho9.6 fixed từsnapshot77: sourcewriter dùng max(height/width*5.4f,9.6f).
2. Dùng typedscaler→camera refs, giữ2Gamecameras vàsource layer/depth/transform khác nhau;
   cùngsize không cónghĩa cùngcullingmask hoặc cùngcamera.
3. Ghi implementation arithmetic/runtime rounding scope rõ. Nếu thêm resizeevent/nullskip/
   khác Screen source thì ghi newdesign thay vì APK fact.
4. Tiếp camera movement/otherwriters cụ thể nếu cần; không đòi fullAPK dump chỉvì chưa
   có runtime video hoặc nativeUnityrenderer.
