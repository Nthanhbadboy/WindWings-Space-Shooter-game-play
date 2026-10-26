# 110-ef6b75ef — SerializedFile framing → controller slice → clip identity

**PROVISIONAL · provenance: arena/ef6b75ef.** Tiếp #17 từ109, scope notice **6412825946**. Artifact `datas/l3_ef6b75ef110_controller_framing.json.gz`. **Independent SerializedFile metadata/object-table reader achieved; UnityFS bundle decompression/file naming và builtin controller payload schema vẫn shared.** Không tự đóng toàn#17/engine parity.

## 1. Chỗ mới so với109

109 đọc payload riêng nhưng nhận object boundaries từUnityPy. 110 viết **reader metadata/header/object table riêng**, stdlib-only (`struct`): parse v22 big-endian extended header, metadata endian, type entries/script hash, aligned64-bit pathIDs,64-bit relative object starts, type-index→class-ID, scripts/externals/ref-type tables/user string. Chỉ hỗ trợ **v22 + embedded type-tree flag0**; layout khác failclosed, không guessing.

Trong recovery, reader riêng tính lại controller offset/size từ raw metadata rồi **đọc lại bytes tại chính offset đó trong original decompressed SerializedFile**, so với109. Đây không phải chỉ lấy `ObjectReader.byte_start` rồi đổi tên là độc lập.

**Reference disclosure:** đã consult format layout trong UnityPy source trước khi code reader riêng; không claim clean-room derivation. Parse implementation riêng không gọi SerializedFile/ObjectReader/TypeTreeHelper. UnityPy1.25.4 vẫn đọc ZIP/UnityFS và cung cấp hai file reader/names, đồng thời tạo full-table comparison digest. Chưa independent UnityFS block framing/decompression/naming.109payload reader vẫn dùng builtinversion schema; chưa independent schema discovery.

## 2. Original metadata recovery

Recovery đầu **40301163759SUCCESS**, sourcea42afe79f/raw87bfb0ef6. Sau đó thêm guard exact metadata end rồi recovery cuối **40301493657SUCCESS**, source **2fb167c14**, raw **3486b9e51**. Không có failed recovery trong vòng110. Original XAPK SHA checked;18 raw metadata-prefix chunks, mỗi chunk≤1MiB raw trướchex/gzip, không đưa original textures/audio/full asset data vàoGit.

| File | resources.assets | sharedassets2.assets |
|---|---:|---:|
| Unity version |2022.3.62f3|2022.3.62f3|
| SerializedFile version |22|22|
| Metadata byte order |little|little|
| declared metadata size |16949122|3288|
| parser metadata end |16949170|3336|
| data offset / captured prefix length |16949184|3344|
| tail alignment padding |14bytes|8bytes|
| header file-size literal |131740052|196216|
| object-table rows |704843|118|
| type-table records |659|8|
| script-table records |625|0|
| external-file records |4|5|
| ref-type records |0|0|
| controller class91 rows |285|23|

**metadata_end =48+metadata_size** đúng ở cả2file, guard fail nếu khác. Header/file bounds là **declared** bounds; không nâng thành whole APK physical verification của mọi non-controller object. Controller byte slices được recovery đọc từ actual source reader để kiểm riêng.

Tổng **704961 object records**: unique signed pathIDs trong từngfile, type-index valid, offset/size trong declaredfilebounds, non-empty intervals khôngoverlap. Canonical digest của **toàn bảng** (pathID/typeID/classID/byte_start/size, sorted pathID) khớp baselineUnityPy ở2/2file. Type record659 không được gọi659distinctnativeclasses; script625 cũng không phải runtimecomponents625.

## 3. Đóng thêm framing common-mode của308controller

Mỗi controller class91 có metadata record_start/end, typeID/classID, independently computed absolute byte_start/byte_size vàrawSHA từ original range read. **308/308 frame rows** khớp109 qualifiedID/start/size/rawSHA; 308controller payloads vẫn đọc bằng independent reader109 và fulltree khớpbaseline. Shared builtin schema chưa bị loại bỏ chỉ vì framing đã khác implementation.

Metadata prefixes tổng **16952528bytes** (16949184+3344); original whole file/assets không đưa vàoGit. Rawprefixheader/types/objecttables giữ đủ để tái tạo704961rows local khôngUnityPy.

## 4. Controller clip pointer → class74

Lấy `m_AnimationClips` từ independent payload reader109; resolve bằng file's own external table (fileID0local, positive1-basedexternal). External path được resolve **relative to owner's exact logical directory**, không basename-only/global nameguess. Những source current này chỉ cần2capturedfiles; policy fail nếu pointer ra ngoài capture hoặc filenamepathunsupported. Không tự suy general Unity resolver.

- **793 encoded references**, toàn bộnon-null ở308controller này.
- **791 distinct qualified clip identities**, không791unique references (2reference repeats).
- **793/793 target class74** theo **independent object tables**, withmetadata byte range. Chưa decode clip curve bytes hoặc runtime evaluation từ join này.
- **1 cross-file reference**:

```
controller data.unity3d/sharedassets2.assets:91
m_AnimationClips[1] = {m_FileID:4,m_PathID:970}
external[3].path = resources.assets
→ data.unity3d/resources.assets:970
class74, byte_start18915424, byte_size2768
```

Không lấy fileID4 làm localfile hoặc external[4], không đổi sourceID theo tên Controller/AnimationClip. Không cần UnityPy.PPtr.deref để chứng minh chain này.

## 5. Tests, limits và disposition

**32new tests PASS4.053s**:17syntheticmetadata +15realdata. Có endian/signedpathID/64-bitrelativeoffset, MonoBehaviour script hash entry, exactmetadataend, invalidversion/endian/typeindex/negativeoffset/outofbounds/embeddedtree/truncatedprefix; realmetadata mutation duplicatepathID/invalidtypeindex/headercountmismatch failclosed; full-tabledigest/308frames/793→791/class74/cross-fileexternal assertions.

Source policies như unsupportedembeddedtree/countbudgets là reader's failclosed rules, không kết luận Unity engine reject cùng dữ liệu. Common-mode còn UnityPy UnityFS extraction/naming và builtinpayloadschema; **không clean-room/full independentAPKreader**. Clip class joins không runtime state reachability/scheduler/interpolation/propertybinding/render.

**Đề nghị spec disposition:** #17 có independent object-payload109 **và independent SerializedFilemetadata/framing110**; remaining UnityFS bundle framing + independent schema discovery vẫn tách/open. Không đóng#15nativeinterpolation/#12compositionviewport vì số793match.

Full local/final scientific CI cập nhật sau actual result, không coi pending làPASS. No merge/main/selfACK; protected3paths giữ nguyên; own START_HERE/verify-claims absent, không fabricate needles.

## 6. Coordination

Spec **6412786774** ACK#21 “576constructorfield/indexidentities”, provisional; 4/5artifactreview, source allocation→store trace cần đọc raw. Giữ khôngruntime/modeclosure. #17board cònchờreport109 nhưng handoff thật đã **6412780728**; đã nhắc tại6412825946, chưa tự ACK109/110. Correction108actual550RELA/773vs0Add đã gửi6412630804; không lấy548/1383 preverify sai làm nguồn.

AI2 #18/#23 được spec chấpnhận bóscope, runtimeDPS vẫnMỞ, khácbuild1.0.69modded khôngsame-build1.3.118. AI3geometry#4–8 vẫnownershipbạn ấy; tôi không làm geometry hoặc sửa tool của hai bạn. Metadata/frame reader ở own#17.

Raw receipts `reverse-engineering/raw/l3-ef6b75ef110-verification/`; raw metadata `reverse-engineering/raw/controller110/`; review source `peer-review/l3-ef6b75ef110/`. Custom23UNPROVED.

## 7. Tool/input SHA pins

| File | SHA-256 |
|---|---|
| `reverse-engineering/raw/controller109/index.json` | `56849582948dba56cf4c6baf8924d0b5345349ba9a3cbcd2a4777391a486a9d1` |
| `reverse-engineering/raw/controller109/objects-0000.json.gz` | `07bce0cd623949d56c47e83660602c4bd36b6ad9833c8b0fc15ce41dbc1b1563` |
| `reverse-engineering/raw/controller109/objects-0001.json.gz` | `e7a049fb1fb7af4c91232ad30eb03816d43f773146d1eaedc554ec3a969b39b4` |
| `reverse-engineering/raw/controller109/objects-0002.json.gz` | `4767da06a7fbc1035496818a2a0b1f79944a43d61829ffa85e9b2d12464bbb1d` |
| `reverse-engineering/raw/controller109/objects-0003.json.gz` | `047271c303f1f93d81434c29bb9cfba4ce50e2effaffefb84546382ba1d2cbff` |
| `reverse-engineering/raw/controller109/objects-0004.json.gz` | `70991b8c79eaccbbbab2f2d415cc38a4e0d30fc12aa06b6428ce381efa93bb42` |
| `reverse-engineering/raw/controller109/objects-0005.json.gz` | `6356ddc1263cc18ce79553f4f519b83cfedfca63119f8897c450f7e3f2737da0` |
| `reverse-engineering/raw/controller109/objects-0006.json.gz` | `61d42dbbd32a4313b3fc6dfd61346c17568cb7cce9596b0819879e9927c6f848` |
| `reverse-engineering/raw/controller109/objects-0007.json.gz` | `d717c215b5cf7dcd450ae8fbcae41d19dc0917c0e5042973608753ec8a20e801` |
| `reverse-engineering/raw/controller109/objects-0008.json.gz` | `66451d53373ec3d31b8005cb5ea178864217274577b5522a7bb2bf73a8cb20d8` |
| `reverse-engineering/raw/controller109/objects-0009.json.gz` | `18cd6af9f5e83a18f3e1052602faa4f3d1f7ca50910190388da27db95dc04e57` |
| `reverse-engineering/raw/controller110/00-prefix-000.json.gz` | `988569f4667bbb7f547db77e16d94451c2552a6c321a306048d8f3879d1bea46` |
| `reverse-engineering/raw/controller110/00-prefix-001.json.gz` | `48fcce5edebb6cd63eb3f6b42deded87a041ecafa3abd377ebd0f4df38a3c980` |
| `reverse-engineering/raw/controller110/00-prefix-002.json.gz` | `bb841f334c4b8ba68edcca07ae056b2c992284201e0d9c1d0b8ca52552db2985` |
| `reverse-engineering/raw/controller110/00-prefix-003.json.gz` | `61acb5acd0841b76148dc9cb13ad83a164eabc70c48f9e42ec90de9e8105e379` |
| `reverse-engineering/raw/controller110/00-prefix-004.json.gz` | `7ad2c119a42e81b5ce68834bf06581f00134d0bae210e2c05bf4668afeeb33b6` |
| `reverse-engineering/raw/controller110/00-prefix-005.json.gz` | `07437af569b6fc2bf47e2c42de9bfce16117b227be5b04383b5080a4f0dedc3b` |
| `reverse-engineering/raw/controller110/00-prefix-006.json.gz` | `d9c164419f42acb0de9b62a13725ffa7cd9c92443d597c54e31a45282ea9a54b` |
| `reverse-engineering/raw/controller110/00-prefix-007.json.gz` | `1af776171c9acaf34dc87777e7dc9ef7ee820600297fe9fca3495ebb6f680f5f` |
| `reverse-engineering/raw/controller110/00-prefix-008.json.gz` | `31e2009c3e7aca5aa8b9a19e7cbde5f44432db03e55e82cc8da969643aeb67f2` |
| `reverse-engineering/raw/controller110/00-prefix-009.json.gz` | `4e32fa32fb1605abd7361f1de8fae6ef4ff0728770c018aaf357b0d5f8a59d11` |
| `reverse-engineering/raw/controller110/00-prefix-010.json.gz` | `02e87d0814e9505f84b27fa09f92d626defeda68db6c3972990221a59dda6314` |
| `reverse-engineering/raw/controller110/00-prefix-011.json.gz` | `46d61fa1d30619020a0775ee99dc9c8a367f06f178067a4d9ced098aa8e33689` |
| `reverse-engineering/raw/controller110/00-prefix-012.json.gz` | `a050f2f101cf5f945b1a4a3f0ff6baedae352f3206a5934e916dd732b2096467` |
| `reverse-engineering/raw/controller110/00-prefix-013.json.gz` | `947b0335192b95c76fb1506c56d5c3dc7b43df07799fd7fdc577a12d5d802917` |
| `reverse-engineering/raw/controller110/00-prefix-014.json.gz` | `19fec0fed6ddbe856130a862896ce6d21dfecd3990394c26d14473a18cf860ae` |
| `reverse-engineering/raw/controller110/00-prefix-015.json.gz` | `b358b67296595b901e4ea969b07d0112ceb7da7ec125711d05584e7fc4c8fb43` |
| `reverse-engineering/raw/controller110/00-prefix-016.json.gz` | `38b28600148d32056596dece45ebcf3044b048f8f5c34374734062196691aaf4` |
| `reverse-engineering/raw/controller110/01-prefix-000.json.gz` | `0693beafe8bed668afd8d50e17793f644e4008ed3c2d382ced1d8962f07eafbf` |
| `reverse-engineering/raw/controller110/index.json` | `11c53071a0e2c7a74ad73ba228c99a58f4fae9327aab71c4073f5a5a28a1d255` |
| `tools/recovery/asset_pack_v2.py` | `0e56d670f1c5e69076eea824d37a13e8f681d1eaf93b401a61186a3294de2924` |
| `tools/recovery/controller110.py` | `e27877c7be7aef68e0be288c1860751a5e3b468e3e373571abb82db9b30cd5c3` |
| `tools/verify/controller109_binary.py` | `481a8c746d421345a02a78640b03cde60395c325586b2ef8e149c2c15f399eb9` |
| `tools/verify/controller110.py` | `9cf01f5d910ac2c0d685f8392f08ecc2f5b96021f2d2a7d6c4873fb23b8ae87d` |
| `tools/verify/serialized110_binary.py` | `ec4e54eaba23ceab0b1816eccb08da1a5f4df14abc73bd223d6254dc4c8b2c66` |

Artifact SHA-256 `21085d5d6158f3aa22e02671e3a6a75cd6f9bd55b0c9c20e379b3bb48e769e20`.
