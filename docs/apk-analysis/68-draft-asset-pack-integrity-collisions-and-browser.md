# 68 — Draft asset pack: CRC hợp lệ, nhưng export bị va chạm tên

**Tạm thời, ngày25/10/2026. Đây là kiểm tra archive/export, không chứng nhận full pack đủ để dựng game.**

## Kết quả quan trọng

Draft release `windwings-assets-1.3.118`, **release ID421174835**, vẫn draft, đã được download/convert/test trên CI **40193251582 success**. Không publish, không thay/clobber các media gốc.

**Zip integrity PASS không có nghĩa asset completeness PASS.** Tìm thấy:

| Hạng mục | Kết quả |
|---|---:|
| File thật trong archive, không kể directory | 2652 |
| Manifest export rows | 2907 |
| Đường dẫn manifest không xuất hiện trong archive | 0 |
| Đường dẫn bị nhiều manifest row cùng dùng | **151** |
| Manifest rows vượt quá unique paths | **321** |
| Manifest row có byte size khác file đang tồn tại | **320**, thuộc150 paths |
| CRC tất cả entry | PASS |
| Manifest path→identity injective | **FAIL** |
| Manifest size consistency | **FAIL** |
| Complete APK reference | **NOT ESTABLISHED** |

Không báo “0 missing paths tức đủ asset”: nhiều source objects đã cùng ghi vào một filename. 321 là số identity rows bị gộp đường dẫn, **không phải đã chứng minh321 ảnh có nội dung pixel khác nhau**.320 size mismatch đủ chỉ ra không thể phục hồi từng row chỉ bằng đọc file hiện tại.

## Raw được giữ và pin

`reverse-engineering/raw/asset-pack/`:

- `manifest-full.csv`:220114bytes, **nguyên byte** lấy từ release, không tạo lại từ summary.
- `catalog.json.gz`: zip entry paths/bytes/CRC/SHA256, media header metadata, toàn manifest rows theo path, collision summary, validation gates, source archive hashes/asset IDs và giới hạn.
- `docs/assets/pack-browser.html`: browser metadata-only, sinh từ catalog, có search/category/pagination, preview PNG và audio controls, link font/text; **đánh dấu ambiguous identity** và cảnh báo NOT complete. Không có PNG/WAV/font gốc trong Git.

| Input release asset | Asset ID | SHA256 |
|---|---:|---|
| assets.z01 (94371840B) | 674836818 | `95a9db86d53d9e7e892c8e4e4116adc70fb7d2842bb6ac8281213c90ffbef3b7` |
| assets.zip (63277518B) | 674837135 | `5cef167cdfbd3874503998852a974954f108fc747ab7863666d998d474e7937f` |
| manifest-full.csv | 674837209 | `f1a5cf69d9562bb95ba0a43c71fbf4888d73682f4f265bb0f3ef143023451e54` |

Tất cả khớp `digest` của release API. Manifest trong zip cũng khớp SHA với asset CSV ngoài. Không kiểm tra media từ một bản APK mới/latest.

Local sandbox không tải được signed release-assets host; dùng workflow CI có network để đọc **existing draft release ID**, không phát hành release nhằm vượt hạn chế. Endpoint release-by-tag trả404 với draft này, endpoint theo ID thành công; giữ nguyên draft, không đổi visibility. Hai lần thử đầu fail ở lookup trước audit, không được tính là PASS.

## Phân bố thực tế trong archive

| Directory | File thật | Manifest rows khi có |
|---|---:|---:|
| Sprite | **1903** |2185 |
| Texture2D | **614** |653 |
| AudioClip |69 WAV |69 |
| Font |1 TTF |không có Font rows trong CSV export này |
| textassets |64 |không nằm trong CSV export này |
| root |1 manifest CSV |— |

- 2517 PNG được kiểm signature/IHDR+CRC, **chưa kiểm pixel/crop/mask/trim/flip**. Số manifest Texture2D653 khác population raw geometry report62=654; chưa coi đó là decoder/completeness đã được giải quyết.
- 69 WAV có header hợp lệ, tổng≈**571.465giây**; không phải nghe thử69 clip. Audio rules/enum/trigger ở [report67](67-audio-manager-preferences-triggers-and-playlist.md).
- 1 file font là `Font/SVN-Agency_FB_bold.ttf`; **không suy APK chỉ có một font**, cũng không đồng nhất8 font-preview tiles với8 binary font files.
- Textassets gồm26 `skeleton*.json` và27 atlas text; phần khác gồm charset/text. Chỉ presence/bytes/CRC; **không chứng nhận rig↔atlas-page↔texture binding**. `Texture2D/skeleton.png` bị nhiều manifest identities cùng dùng nên ghép rig bằng tên rất dễ lấy sai ảnh.

## Nguyên nhân có thể tái kiểm ngay trong producer

`tools/apk-analyze/unity_assets.py::export_assets` đang có:

```python
for obj in env.objects:
    ...
    sub = os.path.join(EXPORT, t)
    ...
    used: set[str] = set()  # reset bên trong mỗi object
    ...
    fn = safe_name(name, used) + ".png"
```

Reset used mỗi object làm chống trùng tên không có tác dụng giữa objects. File được ghi theo tên thay vì serialized-file/type/pathID identity. Manifest vẫn append từng object nên còn nhiều row `Sprite/1.png`, `Sprite/Body.png`, `Texture2D/skeleton.png` dù archive chỉ giữ một file mỗi đường dẫn.

Đây là lỗi export/reference pack, **không phải bằng chứng APK thiếu sprite/texture**. Không dùng image preview cũ cùng basename để sửa geometry của object khác. Không xóa raw identities hay sửa CSV giả thành không trùng để làm test xanh.

## Duyệt pack hiện có — đúng scope

Browser giúp duyệt **các file còn thực sự tồn tại**, không phục hồi file đã ghi đè. HTML không nhúng media gốc hoặc tải script bên ngoài; giữ catalog embedded để mở offline. Đặt HTML cùng root với directories Sprite/Texture2D/AudioClip/Font/textassets sau khi giải nén.

```bash
# Trong directory mới, giữ nguyên mọi input parts:
gh release download windwings-assets-1.3.118 \
  --pattern 'assets.*' --pattern 'manifest-full.csv' --dir downloaded
cd downloaded
zip -s 0 assets.zip --out assets-full.zip
unzip -t assets-full.zip
unzip assets-full.zip -d reference
# Copy từ checkout, với đường dẫn tuyệt đối tương ứng máy đang dùng:
cp /path/to/checkout/docs/assets/pack-browser.html reference/
# Mở reference/pack-browser.html trên máy đã có media.
```

**Không** `cat ... > assets.zip`, không ghi đè input split parts. Có thể serve root reference bằng HTTP trên máy của người duyệt nếu browser hạn chế file audio. Không mở HTML metadata-only trong repo rồi kỳ vọng repo đã chứa PNG/WAV.

Artifact CI `asset-pack-audit-and-browser` giữ metadata/browser. Full media vẫn ở **draft release**, không commit vào Git. Gallery có thể tìm theo tên/path/pathID nhưng collision card hiển thị mọi **claim từ manifest**, không công nhận tất cả claim là nội dung file hiện có.

## Tái tạo và bước sửa bắt buộc

```bash
# Với parts đã tải và convert, release API JSON lưu cạnh chúng:
python3 tools/recovery/asset_pack_audit.py --directory /path/to/downloaded
# Tái sinh phần annotation/browser từ raw đã giữ, không cần media:
python3 tools/recovery/asset_pack_audit.py --refresh-catalog
python3 -m unittest discover -s tests
```

6 tests cho tool/catalog, cộng audio/recovery → **162 tests toàn repo PASS**. Các FAIL validation gates ở trên là finding được test giữ nguyên, không phải lỗi unit test bị che.

**Task tiếp bắt buộc để đáp ứng full asset pack:**

1. Recovery/export **riêng asset** từ cached APK đã pin, không rerun full analyze. Đặt filename bằng serialized-file identity + type + pathID; kiểm collision trước write, giữ original name riêng trong manifest.
2. Đối chiếu population raw Sprite/Texture2D/Font/TextAsset/AudioClip, ghi rõ object empty/unsupported/failed; không im lặng skip exception.
3. Giữ audio69 đã kiểm nhưng nối file-scoped clip identity; giữ rig/atlas/page mapping đúng typed PPtr, không dùng basename.
4. Tạo pack mới versioned trong draft, **không clobber original archive đang là bằng chứng**; kiểm lại SHA/CRC/manifest/geometry và browser trên pack mới.
5. Sau đó mới duyệt crop/atlas/font/Spine và nghe audio; có archive đủ file vẫn chưa phải rendering/listening approval.

Full asset pack requirement **vẫn mở**, nhưng không còn blocker mơ hồ: đã có151 collision paths và producer site cụ thể để sửa. Không yêu cầu người dùng chụp thêm screenshot để tiến hành.
