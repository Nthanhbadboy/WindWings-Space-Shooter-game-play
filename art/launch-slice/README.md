# Launch slice — mẫu thử, KHÔNG PHẢI bản giao

PLAYER-10001 và CB-30003 là ảnh sinh mới; `source/` là ảnh AI thô, `masters/` và `exports/` là bản thử sau tách nền. Không dùng asset gốc để tạo sprite. File trong `preview/` chỉ đối chiếu học tập, chứa toàn bộ contact sheet gốc, không được dùng trong game. Bảng này chưa đạt yêu cầu so cùng footprint; ảnh gốc không được cắt theo lệnh USER.

Cả hai mẫu đều trượt các ngưỡng planner: xem `metrics/`; không dùng làm asset tích hợp, chưa kiểm halo đầy đủ, chưa tự nhận chất lượng. Master hiện cùng độ phân giải và nội dung với export, chưa phải master chất lượng cao. USER là người duyệt cuối; license=UNKNOWN.

Planner gốc: commit `100cfcebc38c1aec6dd8dc1cfa62c6aa23f77d86`, `docs/art-plan/measure_asset.py`, được chạy nguyên bản với `--class ship|enemy --style`; exit 1 cả hai. Không sửa ngưỡng.
