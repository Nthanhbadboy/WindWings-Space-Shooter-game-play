# Phân việc vòng 3 — dùng asset thật để thiết kế lại

> Vòng 1 (spec) và vòng 2 (combat/encounters/economy) đã xong. Giờ có **asset thật**:
> `docs/assets/` (42 contact sheet, 2.197 asset), `docs/assets/manifest.csv` (kèm `path_id`,
> `atlas`), `docs/assets/audio-index.csv` (69 clip, 571 giây).

## Luật

1. Nguồn: `docs/assets/*.csv`, `datas/*.json`, `docs/apk-analysis/*.csv`. **Không** trích dẫn
   `PHAN_TICH_*`, `probe-results.md` hay tài liệu tóm tắt cũ.
2. Chỉ ghi trong `docs/spec/`. Không sửa `docs/assets/`, `datas/`, `tools/`, `.github/`.
3. PR riêng, tiêu đề `docs(spec3): ...`. Mỗi bảng ghi `(nguồn: file)`.

## Việc

### A. `docs/spec/ART-DIRECTION.md` — art bible cho bản mới
- Đọc `docs/assets/contact-sheets/` (ships, bosses, drones, enemy, bullet, fx, ui, background).
- Phân tích **ngôn ngữ thị giác của bản gốc**: bảng màu theo nhóm (lấy mẫu từ chính sprite),
  silhouette tàu (đối xứng dọc, mũi nhọn, chi tiết ở cánh), độ chi tiết, hướng sáng.
- Đề xuất **hướng mới khác rõ rệt** nhưng cùng "đọc được": ví dụ flat-shaded neon vs painterly,
  palette, tỉ lệ, style guide cho tàu/boss/enemy/đạn/FX/UI.
- Bảng: `hạng mục | bản gốc | bản mới | lý do`.

### B. `docs/spec/ASSET-PLAN.md` — danh sách asset cần vẽ
- Từ `docs/assets/manifest.csv` + `sprites-index.csv`: mỗi asset gốc → asset mới tương ứng
  (giữ nguyên mục đích, đổi hình), ghi kích thước đích và có cần animation không.
- Ưu tiên P0/P1/P2: P0 = 1 chapter chơi được (1 tàu, 5 enemy, 1 boss, đạn, UI Home/Chapters/Endgame).
- Ước lượng: số sprite, số Spine rig, số clip audio.

### C. `docs/spec/UI-REBUILD.md` — dựng lại UI từ sprite thật
- Đối chiếu `ui-01/02.jpg` với `screens.csv`: icon/nút/khung nào dùng ở board nào.
- `docs/assets/manifest.csv` có `path_id` → khớp với bảng `14-*.csv` (tàu/boss/item) để biết
  sprite nào là nhân vật, sprite nào là UI thuần.
- Bảng: màn hình | sprite cần | text key (`i18n/vi.json`) | nút | data load.
- Kết luận: dựng lại **bao nhiêu %** UI bằng sprite gốc + số đo từ prefab, bao nhiêu phải vẽ mới.

### D. `docs/spec/SCOPE-V1.md` — chốt phạm vi bản clone v1
- Từ A/B/C rút ra: v1 làm gì (1 chapter, N tàu, M enemy, 1–2 boss, 5 board), bỏ gì.
- Đường găng: cái gì phải xong trước, ước lượng người-tuần cho từng mảng.
- Danh sách "không làm ở v1" kèm lý do.

## Xong khi
- 4 file trên, mỗi kết luận có nguồn, có bảng ưu tiên và ước lượng.
- Không khẳng định gì về art mà không chỉ ra được sheet/asset cụ thể đã xem.
