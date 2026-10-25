# Asset tham chiếu — WindWings 1.3.118

> **Mesh report75:** `datas/sprite_mesh_contract.json.gz` giữ2185Sprite meshes/27072vertices/24375triangles và497PPUvalues từraw. Sourcepivot,mesh-origin,serializedzeroAABB vàtrimmedPNG registration táchriêng; khôngtựclamp/recenter/UV/windingrepair. [Report75](../apk-analysis/75-serialized-sprite-mesh-origins-and-bounds.md). Khôngmedia mới/khôngUnityplacementapproval.

> **Font ZIP report74:** draft `font-reference-v1.zip` (1627375bytes,asset675170630) tựchứa7SDFatlas+font/primarymaterial metadata,1TTF inventoryriêng,indexoffline.19members/sourcehashes/CRC vàpost-uploadHTTPredownload PASS,7existingreleaseassets khôngđổi. [Report74](../apk-analysis/74-self-contained-font-reference-pack-and-delivery-audit.md), raw/font-reference. Khôngfontimport/render/RTL/shapingapproval; khôngcần tựghépbrowserreport73vớiV2.

> **Fonts report73:**7staticTMP SDFassets vớidefault105+6localfallback, metrics/character/glyph/atlasjoins ở`datas/font_language_contract.json.gz`; [fontbrowser](font-browser.html) copycạnhTexture2D/ trong extractedV2đểxem7rawatlases+metadata.1exportedTTF khôngphải1fonttoàngame. KhôngTTFgiảtừSDFPNG/khôngRTL/shaping/renderapproval; [report73](../apk-analysis/73-tmp-font-fallback-and-localization-first-index.md).

> **Pixel report72:**2185/2185SpritePNG v2 match separate rawgeometry/texture crop+flip+mesh-mask reproduction.40fractional-outside rects chỉ9roundedpadding;517PNGkhácsourcecanvas size. `datas/sprite_export_contract.json.gz` giữsourcepivot/offsets, khôngfinalPNGpivot. [Report72](../apk-analysis/72-sprite-pixel-reproduction-fractional-crops-and-pivots.md): **không UnityGPU/PMA/placement approval**.


> **Spine report71:** draft thêm `spine-reference-v1.zip` (27folder riêng, mỗi folder skeleton.json/atlas/source-texture/Unity settings). [Báo cáo71](../apk-analysis/71-spine-file-scoped-chains-loader-and-reference-folders.md), `datas/spine_identity.json` và raw/spine-identity giữ chain/PPtr/native/provenance. Không còn chọn giữa26texture cùng basename; vẫn chưa nghiệm thu render/PMA/blend/import.


> **Hiện hành — report70:** [identity-safe v2](../apk-analysis/70-identity-safe-asset-pack-v2-and-zero-font-texture.md) đã có trên draft release: `assets-v2.zip` + `assets-v2.sha256`. Giải nén ZIP thường và mở `index.html`; [browser metadata trong Git](pack-browser-v2.html) cần đặt cạnh media. V2 có2185Sprite/653Texture2D/69WAV/64TextAsset/1TTF/66SpriteAtlasJSON; texture thứ654 là Font Texture0×0/empty payload có raw exception. Archive SHA/size/CRC,2838PNG full decode PASS, không phải crop/listening/Spine import approval. **Danh mục dưới đây là lịch sử v1**, không phải population/identity map v2.



> **Audit mới — report68:** archive CRC/SHA hợp lệ nhưng **151 manifest paths va chạm,321 extra rows,320 size mismatches**; chưa phải full pack. Có [browser offline](pack-browser.html) cho các file còn tồn tại, cần đặt cạnh media đã giải nén. Đọc [report68](../apk-analysis/68-draft-asset-pack-integrity-collisions-and-browser.md) trước khi dùng số liệu/manifest lịch sử dưới đây; [report67](../apk-analysis/67-audio-manager-preferences-triggers-and-playlist.md) nối audio rules/trigger.

> **Danh mục preview lịch sử**, không phải chứng nhận full pack/crop đúng. Xem [bàn giao asset hiện hành](../START_HERE_NEW_GAME.md#4-asset-pack--bắt-buộc-cho-tham-khảo-thiết-kế-chưa-được-gọi-là-đã-kiểm-đủ) và report62 cho geometry; số nhãn peer khác population ở đây.

- Tổng asset: **2197**  (133.6MB)
- Contact sheet: **42** file trong [`contact-sheets/`](contact-sheets/)
- Ảnh gốc full-size: artifact `windwings-analysis` (mục `/tmp/apk/unity/export`)
  và draft release `windwings-assets-1.3.118`.

## Nhóm asset

| nhóm | số lượng | mô tả | contact sheet |
|---|---:|---|---|
| `unclassified` | 1554 | Sprite không rõ nguồn (xem cột `atlas`) | [25 sheet](contact-sheets/unclassified-01.jpg) |
| `atlas` | 132 | Texture atlas gốc (UI + nhân vật gộp) | [3 sheet](contact-sheets/atlas-01.jpg) |
| `background` | 109 | Nền, tinh vân, hành tinh | [2 sheet](contact-sheets/background-01.jpg) |
| `fx` | 80 | Hiệu ứng, nổ, trail | [2 sheet](contact-sheets/fx-01.jpg) |
| `ui` | 73 | UI: icon, nút, panel, khung | [2 sheet](contact-sheets/ui-01.jpg) |
| `audio` | 69 | Âm thanh | — |
| `bullet` | 67 | Đạn, laser, tên lửa | [2 sheet](contact-sheets/bullet-01.jpg) |
| `bosses` | 32 | Boss theo wave (idWave) | [1 sheet](contact-sheets/bosses-01.jpg) |
| `enemy` | 31 | Enemy thường | [1 sheet](contact-sheets/enemy-01.jpg) |
| `ships` | 25 | Tàu người chơi (sprite id = ship id) | [1 sheet](contact-sheets/ships-01.jpg) |
| `drones` | 13 | Drone / droid | [1 sheet](contact-sheets/drones-01.jpg) |
| `font` | 8 | Font | [1 sheet](contact-sheets/font-01.jpg) |
| `items` | 4 | Item rơi | [1 sheet](contact-sheets/items-01.jpg) |

## Âm thanh

- **69** clip, tổng ~571 giây (47.6MB)
- Danh sách: [`audio-index.csv`](audio-index.csv) (tên, kênh, sample rate, giây, định dạng)


## Cách dùng

1. Mở `contact-sheets/<nhóm>-01.jpg` để xem nhanh toàn bộ asset của nhóm đó,
   mỗi ô có số `#n` ở góc dưới.
2. Tra số đó trong `sprites-index.csv` (cột `tile`) để biết tên + `path_id`.
3. `manifest.csv` là danh sách đầy đủ, `audio-index.csv` là danh sách âm thanh.
4. File PNG gốc lấy từ artifact/release — repo chỉ chứa bản preview JPEG.

> Ảnh/âm thanh gốc thuộc bản quyền GCenter. Dùng làm **mẫu tham chiếu thiết kế**;
> không đóng gói vào bản phát hành.
