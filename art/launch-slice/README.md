# Launch slice — mẫu thử, KHÔNG PHẢI bản giao

PLAYER-10001 và CB-30003 là ảnh sinh mới; `source/` là ảnh AI thô, `masters/` và `exports/` là bản thử sau tách nền. Không dùng asset gốc để tạo sprite. File trong `preview/` chỉ đối chiếu học tập, chứa toàn bộ contact sheet gốc, không được dùng trong game. Bảng này chưa đạt yêu cầu so cùng footprint; ảnh gốc không được cắt theo lệnh USER.

Cả hai mẫu đều trượt các ngưỡng planner: xem `metrics/`; không dùng làm asset tích hợp, chưa kiểm halo đầy đủ, chưa tự nhận chất lượng. Master hiện cùng độ phân giải và nội dung với export, chưa phải master chất lượng cao. USER là người duyệt cuối; license=UNKNOWN.

Planner gốc: commit `100cfcebc38c1aec6dd8dc1cfa62c6aa23f77d86`, `docs/art-plan/measure_asset.py`, được chạy nguyên bản với `--class ship|enemy --style`; exit 1 cả hai. Không sửa ngưỡng.

Sau mẫu đã thử thêm boss và nền (`boss-37001`, `bg-gameplay`), preview `gameplay-draft.jpg`; cả hai cũng trượt đo planner (`metrics/boss.txt`, `metrics/bg.txt`). Nền chỉ đặt alpha=0 tại đúng bốn góc để thử canvas, không bảo đảm ghép hay cuộn liền mạch. Không có đủ 41 enemy, FX, đạn, UI, so sánh toàn bộ hay master độ phân giải cao: đây là bản thử không hoàn chỉnh và không sẵn sàng tích hợp.

## Worklist thay thế (USER redo)

**Toàn bộ file mẫu bên trên là lịch sử, không dùng để tích hợp.** Worklist Wave_0000–Wave_0004 đã hủy. Nguồn hiện hành `game/data/launch_slice_waves.json` tại coder commit `19a37d8`, SHA-256 `c417fb5640e153b663b120ae4f90e82ac0cc83a523e395178e03827d5d61db92`. Mười ba prefab stage: CB-30001, CB-30002, CB-30003, CB-30009, CB-30023, CB-30024, CD-31002, CD-31004, CD-31005, GD-33002, GD-33004, H-38001, XB-34001; cộng Boss-37001 và PLAYER-10001. Xem comment PR #12 `6477533357` để biết theo từng wave. Đến nay chưa có mẫu redo vượt gate, không có tài sản nào của tuyến này sẵn sàng tích hợp.
