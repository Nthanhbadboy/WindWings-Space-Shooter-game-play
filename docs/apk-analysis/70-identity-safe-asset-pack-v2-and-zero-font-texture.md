# 70 — Asset pack v2: không ghi đè tên, có browser và kiểm archive độc lập

**25/10/2026 — tạm thời, static APK evidence; không phải nghiệm thu hình/render/audio/runtime.**

## Kết quả chính

Đã chạy **narrow re-export từ cached XAPK đã pin**, không chạy lại full analyze/native pipeline.
Pack mới `assets-v2.zip` được **thêm** vào releaseID **421174835**, vẫn **draft**;
không thay `assets.z01`, `assets.zip`, `manifest-full.csv` hay preview cũ.

| Loại object trong Unity payload | Nguồn | Xuất được | Exception |
|---|---:|---:|---:|
| Sprite | 2185 | 2185 PNG | 0 |
| Texture2D | 654 | 653 PNG | 1 object 0×0, không có pixel payload |
| AudioClip | 69 | 69 WAV | 0 |
| TextAsset | 64 | 64 file nguyên byte | 0 |
| Font | 1 | 1 TTF | 0 |
| SpriteAtlas | 66 | 66 typetree JSON | 0 |
| **Tổng** | **3039** | **3038** | **1** |

Traversal đối chiếu với `env.objects`, phủ **717262 object** trong **12 serialized files**
của payload đã load, sau đó chọn sáu loại trên. Không nói đã export mọi loại object
hay mọi Android resource trong APK.

So với media trong pack cũ, v2 có thêm **282 Sprite outputs +39 Texture2D outputs**
(2185 vs1903;653 vs614). Đây là số **object outputs được giữ riêng**, không khẳng định
321 ảnh khác nhau về pixel. Lỗi basename collision của report68 được loại khỏi v2;
pack cũ vẫn giữ nguyên lỗi như bằng chứng lịch sử.

## Identity và raw

Tên output: `<type>/<serialized-basename>__<SHA256-full-logical-serialized-path>__<pathID>.<ext>`;
audio thêm sample ordinal. Tên hiển thị gốc nằm trong manifest/browser, không làm
primary key. Hash dùng toàn đường dẫn logical, không chỉ `resources.assets` basename.
Tool từ chối trùng identity/path; ghi bằng exclusive create, không overwrite.

- Producer: `tools/recovery/asset_pack_v2.py` (UnityPy **1.25.4**).
- Recovery run **40194721870 success**, input commit `3ac2faa45`.
- `raw/asset-pack-v2/catalog.json.gz`: source file inventory, input SHA,3039object rows,
  output path/size/SHA, status và exception; không có original media trong Git.
- `raw/asset-pack-v2/release-upload.json`: release draft và versioned asset IDs/digests.
- `docs/assets/pack-browser-v2.html`: offline metadata-only browser, search name/pathID/
  file, filter type/status, phân trang100object; preview ảnh, nghe audio và mở text/font
  khi đặt cạnh media. Không cần fetch hay server để mở `file://`.

Các gate accounting/identity/path/hash/filesystem đều PASS. Gate
`all_target_objects_exported` **vẫn false**, giữ đúng exception, không sửa để xanh đẹp.

## Texture2D654 vs653: gap đã xác định chính xác

`data.unity3d/resources.assets`, Texture2D **pathID535**, tên **Font Texture**:

- width=0, height=0, `m_CompleteImageSize=0`, `m_ImageCount=0`;
- `image data=[]`;
- `m_StreamData={offset:0,size:0,path:""}`.

Raw typetree và raw-object hash giữ tại `raw/asset-pack-v2/font-texture-exception.json`,
recover độc lập từ cùng cached/pinned XAPK. UnityPy image decoder trả
`IsADirectoryError(21, 'Is a directory')`; lỗi này giữ nguyên ở catalog.
Nguồn serialize không chứa pixel để xuất PNG. **Không tự vẽ ảnh thay thế**, không
nói missing texture có pixel đã bị bỏ qua; cũng chưa chứng minh runtime font atlas
được tạo bằng cơ chế nào. Font program embedded riêng vẫn xuất được.

## Audit độc lập trên archive tải lại từ draft

Auditor `tools/recovery/asset_pack_v2_audit.py`; run **40194948219 success**,
input commit `a435b84ea`. Download lại v2 từ release, không chỉ kiểm thư mục producer.
Raw `raw/asset-pack-v2/archive-audit.json.gz`:

- ZIP CRC PASS; không duplicate/unsafe paths.
- Exact population: **3038 media files +manifest-v2.json +index.html**.
- Mọi media member match SHA256 và size; manifest trong ZIP bằng catalog giữ trong Git;
  index.html bằng browser metadata trong Git; release digest match archive.
- **2838 PNG** được load/decode toàn ảnh và kiểm dimensions, không chỉ đọc header.
- **69 WAV** đọc header/frames; tổng **571.4650289115647 giây**; không phải listening approval.
- TTF parse bằng fontTools **4.61.0**:258glyph/252Unicode codepoints; không chứng minh
  toàn game chỉ dùng font này hoặc đủ fallback/localization.
- Text classification theo nội dung: **27 skeleton JSON +27 atlas text +10 other**.
  Không lấy con số26skeletonJSON của audit cũ làm sốrig tối đa; parser/phạm vi khác.
-27atlas page names:26trang có26Texture2D name candidates mỗi trang;1trang có2candidate.
  **Không trang nào được giải identity chỉ bằng tên**. Raw giữ candidates để đi tiếp,
  không autojoin `skeleton.png` vào một texture bất kỳ.

Sprite texture PPtr trực tiếp null ở1550object nhưng SpriteAtlas PPtr đều resolved;
635object còn lại có texture pointer resolved. Không suy null direct pointer là
sprite bị thiếu ảnh; cả2185Sprite đã decode PNG. Chưa tự nhận pixel/crop/mask đúng.

## Lấy và mở pack mới

Dùng thư mục riêng **ngoài checkout**; v2 là ZIP thường, **không ghép với part v1**:

```bash
mkdir -p /home/user/windwings-reference-v2
cd /home/user/windwings-reference-v2
gh release download windwings-assets-1.3.118 --pattern assets-v2.zip --pattern assets-v2.sha256 --dir .
sha256sum -c assets-v2.sha256
unzip -t assets-v2.zip
unzip assets-v2.zip -d extracted
# Mở extracted/index.html trong browser.
```

Archive: **175684102 bytes**, assetID **675035745**,
SHA256 `4b18cc23b9d71d095dbe8be4458a8ca95fe1d16f5bc0c96bb2329c7bc5de3506`.
SHA sidecar assetID675035746. Artifact `identity-safe-asset-pack-v2` trong recovery run
là kênh khác nếu cần. Không publish draft; original media chỉ làm tư liệu tham khảo,
không mặc định có quyền đóng gói vào game mới.

## Đã đóng / còn mở

**Đã đóng trong scope sáu loại:** loss do basename overwrite, thiếu browsable identity
catalog, đối chiếu source population/output và archive integrity. Exception0×0 có raw.

**Còn mở:** rendered crop/alpha/trim/pivot/rotation và40fractional rect report62;
nghe audio/so trigger; Spine SkeletonDataAsset→AtlasAsset→Material→Texture identity
joins và import rig; font runtime/fallback/localization. Source Spine text giữ nguyên,
page references **không rewrite** theo tên file mới: pack duyệt được nhưng chưa phải
folder drag-and-drop vào Spine runtime. Premium/pool-history vẫn không phải blocker.

Regression: **180 tests PASS local**, datas validation PASS. CI recovery/audit ở trên
đã PASS; regression CI của final report commit phải kiểm riêng, không suy từ run cũ.
Re-export workflow chuyển sang manual sau lần tạo v2 để không tự chạy lại/đụng tên
asset evidence đã tồn tại. Muốn xuất version sau phải đặt tên mới, không clobber v2.
