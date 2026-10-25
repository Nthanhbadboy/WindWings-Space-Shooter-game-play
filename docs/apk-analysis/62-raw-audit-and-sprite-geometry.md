# 62 — Kiểm lại phần dịch ngược raw: thừa, thiếu và sửa gì

> **Provisional**. Đây là audit phạm vi, pipeline và một bước recovery mới;
> không phải tuyên bố đã dịch ngược hết game. A: trường/bytes; B: join/diễn giải;
> C: chưa đủ bằng chứng. Premium vẫn để sau.

## 1. Kết quả rà soát

| Vấn đề | Thừa/thiếu/sai phạm vi | Xử lý vòng này |
|---|---|---|
| Kết luận tổng hợp lỗi thời | `docs/conclusions.md` còn enum spawn sai, “45659quân thật đã chốt”, và curve chưa đọc được cho tất cả | Đặt registry hiện hành lên đầu; đánh dấu các hàng17/18/13d/16b/21b cũ không dùng như kết luận A hiện hành |
| Tích lũy raw UI nhiều lần | Quét mọi file trên đĩa làm phình coverage và lặp công đọc | Đo inventory riêng; phân biệt current index với dữ liệu ngoàiindex; chưa xoá raw |
| Recovery nhỏ kích full analyze | Sửa early_wave exporter từng kích cả full APK pipeline lẫn recovery riêng | Loại exporter đó khỏi trigger full analyze; workflow-only config changes dùng manual dispatch nếu cần full run |
| Pin APK chỉ in SHA ở main analyze | Cache key ghi version/hash nhưng cache miss tải URLlatest; in SHA không từ chối input khác | Main analyze enforce `sha256sum --check --strict` trước extract, fail thay vì trộn build |
| CI bỏ sót raw-only edits | Verify paths thiếu raw/dump; bot `[skip ci]`/GITHUB_TOKEN không đảm bảo tạo run mới | Thêm raw/il2cpp trigger; quan trọng hơn: hai recovery producer chạy unittest trước bot commit |
| Geometry atlas thiếu thật | Render-context cũ giữ Sprite rect/pivot nhưng bỏ m_RD; thiếu full atlas render map/texture join | Recovery targeted + verifier mới, không export lại pixel/audio/full pack |
| Tests dễ bị hiểu quá mức | Nhiều test kiểm snippet/model đã viết, không phải independent replay | Giữ giới hạn rõ; thêm negative tests scope/missing atlas key/bounds; không gọi100+test PASS là gameplay complete |

Raw process snapshot: `reverse-engineering/raw/process-audit/scope-inventory.json.gz`,
collector `tools/verify/raw_scope_audit.py`. Raw này là **inventory checkout**, không
phải dữ kiện game APK. Nó không xác minh tác giả từng file hoặc provenance của
mọi run cũ; không dùng để thực hiện xoá hàng loạt.

## 2. UI: lượng file trên đĩa không phải lượng màn đã xác minh

Snapshot tại audit này:

- **55584** file `raw/ui/*.json.gz`, compressed file bytes **157576919**.
- `_index.csv`: **797** rows / **797** unique files / **117** class / **150131** nodes.
- **54787** file ngoài index hiện tại; **0** indexed file bị thiếu.
- SHA index: `6d6500f39764b4145891b6ae6ab3c878f5a71297d9adfc90f5f4de1336ace4f4`.

**Không kết luận54787file là duplicate/hỏng/rác.** Các export cũ có thể chứa màn
chưa nằm trong index mới, schema cũ hoặc scope thiếu. Chưa hash/so semantic tree
của từng file nên không báo “đã dedup”. Không xoá raw để làm gọn số hoặc phá các
report cũ đang trỏ chúng. Cách tiết kiệm trước mắt: verifier đọc exact indexed
scope/file+pathID hoặc explicit pinned export, không glob indiscriminate rồi
cộng count qua nhiều run. Nếu dọn sau phải lập manifest/quarantine có provenance
và sửa mọi reference trước; không coi user yêu cầu xoá file ngoài phiên là quyền
xoá dữ liệu chưa xác định nguồn.

## 3. Sửa các kết luận cũ bị quá tay

- Enum Call_Data hiện đã đối chiếu raw/native report53–59:
  **0PinMap/1Path/2Points/3RandomTopDown/4Rocket/5EndMap/6StartWave**.
  Hàng cũ gắn6=boss và lấy len(enemies)×copies làm “quân thật” không còn được
  chấp nhận. Exact stage totals ở report56/59 là scoped denominator/slots,
  **không phải runtime spawned/killed counts toàn game**.
- Report60 đã decode3clip BB. Không nói “mọi Unity curve đều đọc được”, cũng
  không giữ kết luận “không có curve vì ordinary curve arrays rỗng”.
- `Enemy_Physics` serialized fields rỗng không chứng minh runtime collision nằm
  hoàn toàn ở một nơi khác hoặc class không có tác dụng.
- Thiếu playerIndex trong một getter HP không đủ suy mọi tàu/talent/upgrade
  dùng chung toàn bộ chỉ số. Cần đọc consumers và writers.
- Các số UI trong bảng lịch sử là snapshot, không thay current index.

Raw cũ không bị sửa để khớp diễn giải mới. Registry `docs/conclusions.md` nay
chỉ rõ phần lịch sử đã bị rút/giới hạn và ưu tiên report mới.

## 4. Đào phần thiếu thật: Sprite / SpriteAtlas / texture geometry

### 4.1. Recovery và provenance

CI **40188735212**, recovery commit **d97399106** (commit này còn một thay đổi
probe-results độc lập). Exporter `tools/apk-probe/sprite_geometry.py` chạy từ
input APK pin; không tải source game khác, không nhìn screenshot để vẽ lại.

Raw tại `reverse-engineering/raw/sprite-geometry/`:

- index có input hashes, version **UnityPy1.25.4**, chunk hashes giải nén;
-6chunk JSONL.gz, mỗi chunk<5MB, không truncation;
- **2185Sprite**, full typetree gồm rect/pivot/border/PPU/render key/m_RD,
  offsets/uvTransform/mesh/index buffers/settings;
- **66SpriteAtlas**, full packed sprites + renderDataMap;
- **654Texture2D** metadata projection, không nhúng image bytes;
- **0export errors**. Giữ file scope và externals ở mỗi object, SHA256 object
  bytes để định danh; Texture2D projection không được gọi là full object bytes.

Input `data.unity3d` SHA:
`7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`.
Native/metadata hashes nằm trong index. Không thêm PNG/WAV/font program vào Git.

### 4.2. Join thực, không đoán theo tên

`tools/verify/sprite_geometry.py` → `resolved-geometry.json.gz`:

1. Xác minh chunk hash/count và unique `(serialized_file,path_id)`.
2. Sprite có atlas pointer → resolve theo fileID/externals, tìm exact
   `m_RenderDataKey` trong atlas `m_RenderDataMap`.
3. Nếu pointer0 nhưng có atlas tag: chỉ chấp nhận unique tag trong owning file,
   rồi vẫn phải khớp render key. **Dataset hiện tại không cần fallback này**.
4. Resolve texture/alpha pointer theo owner của render data, không lấy pathID
   hoặc name lookup toàn build.
5. Giữ rect/offset/pivot/border/PPU/settings và kích thước texture; kiểm tra
   rectangle bounds riêng. Missing/ambiguous render key → unresolved/fail,
   không fallback m_RD giả để làm đẹp coverage.

Kết quả B:

| Route | Sprite |
|---|---:|
| Sprite.m_RD trực tiếp | 635 |
| Atlas pointer + exact render key | 1550 |
| Tổng resolve | **2185/2185** |
| Unresolved pointer/render key | **0** |

Đây là **coverage join metadata**, không phải2185ảnh đã crop/render đúng.
Số654texture gồm context toànenv (khác scope export gallery cũ653);
không suy “đã thiếu đúng1ảnh” từ chênh số tổng.

### 4.3. Packing flags và40 ngoại lệ bounds

Format reference (không game facts): UnityPy1.25.4 wheel SHA, `SpriteHelper.py`,
`SpritePackingRotation.py`, MIT license được giữ riêng `toolchain/`.

```text
packed       = settingsRaw & 1
packingMode  = (settingsRaw >> 1) & 1
rotation     = (settingsRaw >> 2) & 15
meshType     = (settingsRaw >> 6) & 1
```

Raw settings decode được rotation codes: **0:2041,1:53,2:54,3:37**.
Enum reference:0none/1flipH/2flipV/3rotate180/4rotate90.
Không có code4 trong snapshot này; **144sprite cần xử lý flip/rotation khác0**,
không được crop rectangular rồi coi đã đúng hướng. Packed count1550.
DownscaleMultiplier toàn2185 là1; không tự nhân/chia kích thước theo suffix tên.

**40rectangle không nằm hoàn toàn trong texture bounds theo phép kiểm strict**:
đều thuộc route m_RD trực tiếp, vượt trong khoảng
**0.0000019073486328125 đến0.9962615966796875pixel**.
Ví dụ `resources.assets/2072 PVP7_0`: texture512×512,
y201.9034881591797 + height311 >512. Raw m_Rect có height310.09649658203125.
Có dấu hiệu rounding/fractional rect, nhưng **chưa chốt nguyên nhân engine**.
Không clamp/chỉnh raw, không báo40sprite export hỏng. Chưa kiểm pixel padding,
coordinate flip và tight mesh mask khi crop; ngoại lệ được giữ nguyên trong JSON/tests.

## 5. Phần nào nên dừng làm lại, phần nào tiếp tục?

### Không cần bóc lại lúc này

- Danh mục clip/controller hoặc HP serialize tổng: đã có raw. Đọc chúng không
  giải quyết runtime removal/parent/collision chỉ bằng cách đếm thêm.
- Full APK/export asset pack mỗi khi đổi targeted collector.
- Quét mọi file UI cũ, gom theo tên rồi tăng phần trăm coverage.
- Tạo thêm prose report lặp kết luận mà không có raw join/check mới.

### Còn thiếu thật, theo ưu tiên

1. **Stage2/3 runtime reachability:** BB typeMove/path writers, pool-instance
   history, exact live parent/world matrix và alternate removal/collision path.
   Report61 đã có body/gate nhưng chưa live state. Không vì geometry hoàn chỉnh
   mà bỏ câu hỏi gameplay này.
2. **T9 geometry → usable assets:** metadata stage đã có; bước sau cần pixel crop
   với packing flags, trim/pivot/border/tight mesh + đối chiếu mẫu40fractionalrect.
   Không gọi T9 hoàn tất khi mới có pointer joins. Full asset pack draft release
   vẫn cần manifest integrity/browsability audit riêng cho audio/spine/fonts.
3. **Native parser robustness:** nhiều collector cũ còn lookup short class name
   và helper section lấy overload đầu. Report59/61 đã né collision ở scope của
   chúng; chưa tuyên bố đã refactor toàn bộ parser. Tách shared parser chỉ khi
   có regression fixtures cho namespace/overload, tránh sửa đồng loạt vô chứng.
4. **CI tests độc lập hơn:** hiện static invariants mạnh hơn trước nhưng vẫn có
   model/snippet tests do chính collector tác giả viết. Cần mutation/negative
   fixtures và runtime evidence nếu muốn nâng kết luận về gameplay.

## 6. Kiểm thử và giới hạn

Thêm7geometry tests: rebuild/source hashes, scoped PPtr collision, bad external,
flags, missing render key fail-closed, strict fractional bounds, texture no pixels.
Thêm3process guard tests: SHA pin trước extraction, raw triggers/producer tests,
inventory arithmetic và không tự xoá unindexed raw.

Các trigger GitHub không bảo đảm chạy từ bot commit có `[skip ci]`/GITHUB_TOKEN;
đã đặt regression command **trước commit trong hai recovery jobs** thay vì chỉ
thêm path filter rồi tuyên bố CI đã phủ hết. Pipelineconfig-only thay đổi không
kích full analysis tự động nữa, nhưng vẫn còn workflow_dispatch.

Không tuyên bố đã render ảnh, chạy gameplay, dedup54787file, hoặc kiểm toàn bộ
release pack trong vòng này. Mọi kết luận vẫn tạm thời.

### Lỗi tái lập phát hiện khi chạy CI audit

Run40189044132/44102/44138 fail; không lấy được signed logs trong sandbox.
Kiểm lại bằng archive tracked files ở thư mục sạch không có Git history phát
hiện `peer_spec_review.build()` còn gọi git show peer25c367aca mặc định; local
checkout chứa commit này nhưng checkout@v4 shallow không bảo đảm có.
Đã sửa default dùng9file input text/hash nguyên gốc được giữ trong raw review,
khóa thêm SHA256 canonical input set `b9325a6cc3a2fb394b3a0ba37eadeef57e0438be1d972aaee30e3e8be709ece0`.
Rebuild vẫn tính lại experiments/native findings, không lấy kết luận prose làm
input. `--from-git` là đối chiếu thêm có chủ đích khi có peer history, không dùng
cho acceptance mặc định. Thêm test cấm subprocess Git trong default path.
**111tests pass** cả workspace lẫn tracked-file archive không có `.git`.
