# Asset tham chiếu — WindWings 1.3.118

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
