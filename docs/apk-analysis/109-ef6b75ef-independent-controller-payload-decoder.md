# 109-ef6b75ef — Independent controller payload decoder, shared framing/schema

**PROVISIONAL · provenance: arena/ef6b75ef.** Claim#17 **6412551521**. Artifact `datas/l3_ef6b75ef109_controller_decode.json.gz`. **Second object-payload reader achieved; independent schema discovery / bundle & SerializedFile framing NOT achieved.** Xin spec review phân tầng, không tự ACK toàn#17/engine interpolation.

## 1. Scope upfront: cái gì độc lập và cái gì dùng chung

Recovery mở pinned XAPK, bóc nguyên object bytes AnimatorController, lưu raw slices + schema + UnityPy comparison tree. `controller109_binary.py` là stdlib-only reader (chỉ import `struct`), tự quản cursor, scalar endian, signed lengths, stringUTF8/alignment, Array/vector/map/pair/struct và m_MetaFlag4000 alignment; không gọi UnityPy/TypeTreeHelper/high-level generator để decode.

**Common-mode dependency khai rõ:** UnityPy1.25.4 frame bundle/SerializedFile/object slice và cung cấp schema từ **builtin version type database**. Mọi308object ở snapshot này dùng builtin schema, không serialized_type.node chứa trong APK. Kế hoạch claim ban đầu dự kiến có serialized schema; recovery thực tế không có, không ghi nhầm schema là raw APK evidence. Node names/field types/flags/layout đến từ shared type database, không independent discovery; framing/schema bug vẫn có thể làm cả baseline và reader mới cùng sai. Chỉ byte-read arithmetic/traversal implementation là riêng.

**NOT** native transition scheduler, interpolation, clip blending, property registration/custom23, observed Animator state/Unity readback/render. Không dùng36tests này đóng#15 native interpolation hay#12 viewport-transition integration.

## 2. Recovery và pin

Recovery **40299220671 SUCCESS**, source **afaee21b7**, raw receipt **5c2b5f46f**. Original XAPK SHA checked trước extract; payload SHA/length inputs trong raw index. Không cần owner cấp lại APK hoặc screenshot. Chỉ controller object slices/graph metadata, không original sprite/audio/media.

- **308 raw objects**, **291564 bytes**; lớn nhất9468bytes.
- **285** `data.unity3d/resources.assets`, **23** `data.unity3d/sharedassets2.assets`.
- **1 distinct shared schema**, pin canonical SHA; raw chunks10×tối đa32rows, mỗi chunk SHA/rows và mỗi object rawSHA/byte length/file-qualified identity kiểm riêng.
- **308/308 full payload reads consume exactly original byte_size**, không silently bỏ tail.
- **6916 alignment padding spans /16293padding bytes** được giữ offset+hex; không giả định padding làzero. Raw hash giữ nguyên toàn payload.

Các root field spans được ghi per-object để kiểm cursor độc lập. **m_ControllerSize literal khác consumed m_Controller disk span ở308/308objects**: skeleton_Controller root232bytes, literal592 nhưng m_Controller span136bytes. Không dùng literal làm số byte cần skip; **không suy literal này có nghĩa gì ở runtime**. Đây là counterexample chống reader cắt opaque block theo tên “Size”.

## 3. Full-tree differential, không chỉ đếm lại artifact

Reader tự dựng full nested tree từ original object bytes rồi so với baseline UnityPy tree: **308 full trees equal /0mismatch**. Canonical decoded-tree SHA và baseline-treeSHA ghi riêng per qualified object.

Sau đó join **232 qualified identities** của `datas/l3_animator_programs.json.gz` tới original raw row location và raw_objectSHA; cả **232/232 full original raw trees** khớp decode mới, không chỉ các totals dưới đây. Raw rows cũ là comparison input, không nguồn decode mới. **76controllers ngoài old232 subset** vẫn decode/compare đầy đủ.

| Count | All308 | Old232 subset |
|---|---:|---:|
| layers |308|232|
| machines |308|232|
| states |794|667|
| AnyState transitions |386|343|
| state transitions |147|125|
| selector transitions |616|464|
| conditions |421|376|
| selector transitions omit m_InterruptionSource |616|464|

Subset tổng transition **343+125+464=932**; all308 **386+147+616=1149**. Các số là các tập khác nhau, không regression/tăng coverage của runtime.

**Presence preserved:**616selector transition records của all308 không có m_InterruptionSource;464 ở old232subset. Không fill false/0 để làm như serialized field tồn tại. Sentinel/destination literals ở raw trees giữ UInt32, không diễn giải30000/UINT_MAX thành native engine exit policy. Layer count308 không là live layer observation.

## 4. Reader safety và test boundaries

36new tests:20synthetic binary fixtures +16recovered-data/differential tests. Có signed/unsigned64/endian/bool/UTF8, nonzero padding, vector/map/pair/struct, negative/oversizedcount,truncation/trailingbytes,unsupportedleaf,duplicatefields,nestingbudget. Real-payload mutation: corrupt name count /remove field /truncate /append junk đều fail; flip bool hợp lệ decode được nhưng full-tree differential phát hiện khác baseline.

Strict bool0/1, count budget, unsupported-leaf errors là **reader policy**, không tuyên bố Unity engine sẽ reject cùng lỗi. Supported schema được exercise trên308objects này, không general Unity type-system implementation. Không parse external object pointer resolution bằng engine; PPtr chỉ là fields trong tree. Floating values đọc bằng struct, không numerical transition simulation.

**36new tests PASS0.741s.** Full local/finalscientific CI chỉ ghi sau khi thực sự kết thúc; pending khôngPASS. Deterministic gzip mtime0, không file>5MB; bảo vệ3sharedpaths.

## 5. Coordination updates

Spec reply **6412555942**, tip **a54ca00e50b877392e2b48d510cdd38891b71623**: đã sửa wording GetDevice “repository-wide unavailable” thành chưaconsulted trongbatch110; cảm ơn đúng scope. Report110 AI2 ở5ed3328f8 chưa có raw body file của own r89 nên không phê bạn “không grep file có sẵn”. AI2 #23handoff chưa có artifact trên remote theo spec; chưaACK. Spec ghi AI2claim#18; tôi không làm các task đó. AI3 tipceebe881d chưa geometrydelivery mới được xác minh.

**Sửa spec pre-verify108** tại **6412630804**: handoff chính thức đã là6412515057, không thiếu; actual artifact SHA ccf8309e… có **550RELA**, không548; capacity calls **773/0List.Add**, không1383. Số548 là earlier recovery trước decimal-offset fix. Không nhập số comment vào report mà bỏ artifact recount.

#21constructorbindings đã bàn giao, chờ independentreview; không tự ACK. #17report này đề nghị acceptance đúng mức second payload decoder với sharedschema, không giấu partial independence để tick toàn L3.

Raw coordination snapshots `reverse-engineering/raw/peer-review/l3-ef6b75ef109/`; receipts `reverse-engineering/raw/l3-ef6b75ef109-verification/`. Own START_HERE/verify-claims không có; không fabricate needle rules của peer. Custom23UNPROVED giữ nguyên; no merge/main/selfACK/render acceptance.

## 6. Tool/input SHA pins

| File | SHA-256 |
|---|---|
| `datas/l3_animator_programs.json.gz` | `114d8f442e07a0733b0a68538ce71c78288cb2c36565bb3ec186f17dd032cd44` |
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
| `reverse-engineering/raw/l3-chain/objects-0016.jsonl.gz` | `421076b58f68f67739727b6c46a3605316ba72291ed6726509bf3b272a4f465c` |
| `reverse-engineering/raw/l3-chain/objects-0017.jsonl.gz` | `f4a185cae10c07f035027a2764f37ff751856c1a95fc2e5f87a2d6eb45587ed6` |
| `reverse-engineering/raw/l3-chain/objects-0643.jsonl.gz` | `495abf221f1615ac88ae7625ec285aa6cfd412026c350348fe25428b5312af42` |
| `tools/recovery/asset_pack_v2.py` | `0e56d670f1c5e69076eea824d37a13e8f681d1eaf93b401a61186a3294de2924` |
| `tools/recovery/controller109.py` | `7d10df7d0ea4bf6226123e08ce25ce0c6fdb93d36000bd586d6e1530359d0a27` |
| `tools/verify/controller109.py` | `810599d4501d2f311f17d4436e0f6eb10a1f33a8ef83196e6d4caee64020b84b` |
| `tools/verify/controller109_binary.py` | `481a8c746d421345a02a78640b03cde60395c325586b2ef8e149c2c15f399eb9` |

Artifact SHA-256 `90508507ee1599bcc98d0bd29a5b3ee97a6e7215b0493194f8b4dccbeb96de3f`.
