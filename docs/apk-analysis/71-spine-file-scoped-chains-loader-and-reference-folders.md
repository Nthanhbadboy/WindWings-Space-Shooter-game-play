# 71 — Spine: file-scoped chains, native page loader và reference folders

**25/10/2026 — provisional/static APK evidence, chưa nghiệm thu render/import/runtime.**

## Đã nối được gì?

Từ cùng cached XAPK pin hash của report70, đã recover:

- **27 SkeletonDataAsset →27 SpineAtlasAsset →27 atlas TextAsset**.
- **27 skeleton JSON →27 page Texture2D**, đi qua owning atlas/material, không chọn
  từ26texture cùng tên `skeleton` trên toàn file.
- Graph giữ **167 objects /168 resolved links**:54MonoBehaviour (27+27),54TextAsset,
  29Material,27Texture2D,3Shader property projections.
-29Material gồm27material chính +2blend replacements của một rig.
-185animation names; skeleton format header **26×3.8.99 +1×3.8.84**. Không mặc định
  Spine4.x đọc được nguyên trạng hoặc có cùng behavior.

Scope scan:125453MonoBehaviour headers; một object `resources.assets:580792` không
resolve được MonoScript vì thiếu `unity default resources`. Exception giữ nguyên,
`all_MB_headers_classified=false`.27rig được chọn đều khép graph trong phạm vi đã đọc;
**không** gọi đó là định lý toàn build chỉ có27rig hay xóa object chưa phân loại.

## Raw, producer và bảng import tham khảo

- `tools/recovery/spine_identity.py` + workflow `recover-spine-identity.yml`:
  pinned payload/native/metadata, UnityPy1.25.4,TypeTreeGeneratorAPI0.0.10/AssetStudio,
  capstone5.0.3; không full APK analyze, không export lại media.
- `reverse-engineering/raw/spine-identity/chains.json.gz`: full relevant component/
  material typetrees, file externals, raw object hashes, resolved pointer owner/location/
  fileID/pathID/target; shader chỉ property metadata, texture chỉ name/dimensions;
  TextAsset chỉ SHA/length/headers, original bytes ở draft v2, không đưa media vào Git.
- `raw/spine-identity/native/{SpineAtlasAsset,MaterialsTextureLoader,Material}.{json,asm.txt}`:
  **15 uncapped methods**, Material chỉ getter mainTexture; không collapse overloads.
- `raw/spine-identity/index.json`: scoped hashes, dump hash; không tự index chính nó
  hay các artifact dẫn xuất.
- `tools/verify/spine_chain_contracts.py` → **`datas/spine_identity.json`**: file-scoped
  rig identities, sources, page/material/texture binding, dimensions, Unity scale/mix/
  blend settings,185animation names và12native regression checks.

`raw/` trong phần còn lại là `reverse-engineering/raw/`. Các bảng `datas/spine.json`
và `spine_anim.json.gz` cũ vẫn giữ nguyên làm nội dung animation, không thay identity
mới bằng global pathID join.

### Cẩn thận header do backend typetree đọc khác

Các54selected MonoBehaviour có `tree.m_Script` từ generated typetree khác với
`parse_monobehaviour_head()` độc lập. Ví dụ root580611:

- generated tree: fileID16777216/pathID33772535808;
- parsed header: **fileID1/pathID2013**.

Giữ cả hai raw, không sửa đè. Class discovery dùng **parsed header →MonoScript**,
không dùng generated `tree.m_Script` sai làm PPtr. Các liên kết custom fields được
resolve riêng với owner serialized file; assertions kiểm fileID0 không nhảy file.
Không lấy việc parse được các custom fields làm chứng nhận mọi base-header field.

## Native loader giải bài toán page theo cách nào?

`MaterialsTextureLoader.Load` RVA **0x222f580**:

1. `Path.GetFileNameWithoutExtension(path)` call0x222f61c→0x20848cc.
2. Lấy `atlasAsset.materials` từ owner, duyệt đúng array đó; **không tìm toàn cục**.
3. Gọi `Material.get_mainTexture` (0x2769448), texture `Object.get_name`
   (0x2784a54), rồi string equality (0x1feca34).
4. **First matching material** thoát loop; gán material vào page.rendererObject.
   Model/exporter dẫn xuất bảo thủ: yêu cầu đúng1local candidate; duplicate sẽ reject
   thay vì tự chọn. Trong27chain đang xét đều đúng1candidate.
5. Chỉ khi page width hoặc height bằng0 mới fill kích thước từ texture;
   nếu cả hai khác0, giữ parsed dimensions.

Getter mainTexture có attribute query flag128, negative-result fallback
`GetTexture(string)`0x276953c. ShaderPropertyFlags.MainTexture=128 trong dump;
cả3shader property projections không có flag này, `_MainTex` là Texture property
flags4. Fallback string được nối từnative relocation2adcd60→2bea600→`_MainTex`
qua raw ui-audit cùng native hash. Tất cả27material chính chỉ có1nonnull saved
texture property `_MainTex`. Không nâng điều này thành rule cho shader bất kỳ.

## Bảy atlas1024 nhưng texture512: không tự sửa tọa độ

| SkeletonDataAsset pathID (đều resources.assets) | Texture2D pathID |
|---:|---:|
| 580621 | 540 |
| 580623 | 565 |
| 580631 | 259 |
| 580639 | 646 |
| 580653 | 601 |
| 580659 | 273 |
| 580661 | 666 |

Cả7atlas header1024×1024, image512×512.19page khác khớp512/512 hoặc1024/1024,
page Saw khớp417×417. Derived contract giữ cảhai, `dimension_match=false` cho7;
**không** coi đây là failed identity, không resize PNG hoặc scale atlas coordinates
để làm số giống nhau. Native guard cho thấy loader giữ parsed nonzero dimensions;
chưa nghiệm thu UV/render/PMA hay nêu nguyên nhân build/import giảm kích thước.

## Unity-specific settings không được bỏ

- Scale của27root: float32≈0.01; không phải toàn game hay runtime timeScale.
- defaultMix:26root≈0.2; **root580615 (Saw/json928) =0.5**.
- root580611 có transition **Attack1→Baydi≈0.1**.
- root**580647**: requiresBlendModeMaterials/applyAdditiveMaterial true;
  additive page`skeleton.png`→Material**38**, screen→Material**39**;
  cảhai `_MainTex`→Texture**413**. Rawshader/material settings giữ riêng,
  không gộp thành material chính hay hứa renderer mới tự tái tạo blending.
- Modifiers arrays rỗng trong27root đã đọc; không suy không có runtime modifiers.

## Reference folders từ media v2 đã audit

`tools/recovery/spine_reference_pack.py` lấy đúng source v2 member bằng identity,
kiểm SHA/size trước copy, mỗi rig một folder độc lập:

```text
rig__<serialized-file-hash>__<SkeletonDataAsset-pathID>/
  skeleton.json                  # original TextAsset bytes
  skeleton.atlas                 # original TextAsset bytes
  skeleton.png hoặc Saw.png      # đúng Texture2D output của chain
  unity-reference-settings.json # provenance/settings, không phải import config tự chạy
```

Original atlas và skeleton **nguyên byte**; tên page không phải rewrite vì mỗifolder
riêng và giữ nguyên basename ở đúng chain. PNG nguyên byte exportv2, khôngresample.
Metadata-only manifest/audit/release records nằm ở `raw/spine-identity/reference-pack*`;
original media chỉ artifact/draft release. Đây là **source-associated reference pack**,
không tuyên bố đã import/render/play trong một Spine runtime.

Assembly run **40196217595 success**, raw metadata commit3de2e4a8b.
ZIP **8057645 bytes**, assetID **675073587**, **110 members** (81source media copies,
27Unity settings JSON,manifest,README). ZIP CRC/exact population/81source SHA+size
PASS; GitHub release digest khớp local audited ZIP. Không nói đã download lại bundle
sau upload để audit độc lập như v2 ở report70.
SHA256 `fabc89bdad02b7a754c3b3ff593b6d21676f52503828200a6da35e0839e3e091`.
Chi tiết ở `reference-pack-release.json` và `reference-pack-audit.json`. Tải ZIP thường vào thư mục ngoàiGit, không nối split partv1:

```bash
mkdir -p /home/user/windwings-spine-reference
cd /home/user/windwings-spine-reference
gh release download windwings-assets-1.3.118 --pattern spine-reference-v1.zip --dir .
unzip -t spine-reference-v1.zip
unzip spine-reference-v1.zip -d extracted
```

## Kiểm thử và việc tiếp

Recovery final run **40196115012 success** (raw commit163d5189e). Các run trước:
40195580699/40195703537 fail do bắt buộc toàn bộ MB header resolve; đã giữ explicit
unclassified exception, không đổi nó thành success.40195823176 recover/tests thành công
nhưng preserve rebase conflict với bot cũ; đã serialize writes và giữ generated scoped
output khi rebase,40196012715 và40196115012 success. Không lấy run lỗi làm runtime proof.

Regression **191tests PASS local** sau package, datas validationPASS. Tests mới giữ local-only joins,
reject duplicate/missing/case-mismatch/unsafepage, cross-file fileID0, saiMainTex,
27rig/seven dimension mismatch/blend replacements/native checks/artifact reproduction.
Hai test package mới kiểm81source copies/typed provenance và release digest/draft/110members. Final-commit CI kiểm riêng, không suy từ recovery/assembly cũ.

Tiếp: nghiệm thu rendered crop/alpha/PMA/blend và animation events/timeScale theo
consumer cụ thể; font fallback/localization, nghe audio. Không quay lại global basename
joins, không full export lại hoặc thêm Premium/speculative pool-history làm blocker.
