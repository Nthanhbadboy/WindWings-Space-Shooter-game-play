# Cinematic VFX — nguồn đang chờ duyệt

**STATUS: CHƯA XONG.** Theo yêu cầu mới nhất, chỉ sinh và lưu nguyên ảnh nguồn; chưa dựng GIF/kịch bản/SPEC mới, chờ USER nhắn tiếp. Ảnh nguồn chưa tách alpha và chưa được kiểm bằng mắt hay kiểm khi ghép.

Các loại nguồn bổ sung: `electric-arc`, `debris`, `wall-warning`, `smoke`, `turret-destruction`, `pod-fire`, `missile-impact-redo`, `core-critical-redo`, `main-blast-redo`, `ambient-spark`. Chúng bổ trợ bộ ảnh boss/VFX đã có, không thay thế các asset khác bằng cách cắt ảnh cũ. Ba bản `core-critical.png`, `main-blast.png`, `missile-impact.png` có phần sáng sát hoặc chạm mép ở ngưỡng kiểm tự động nên được giữ để truy xuất, không chọn là bản hoàn chỉnh; mỗi bản `-redo` được generate riêng và không chạm mép ở ngưỡng RGB tối đa >30. Ngưỡng số này không chứng minh quầng sáng không bị cụt. Xem `cinematic-masters.json` để đối chiếu SHA, kích thước và bbox.

Chưa khẳng định đã đủ chất liệu đạt yêu cầu: cần xem kỹ bằng mắt, tách nền và thử ghép khi USER cho tiếp tục; ví dụ hiệu ứng `turret-destruction` có nội dung sáng cách mép trên chỉ 3px theo phép đo, có thể cần generate lại. Không khẳng định đã hoàn thành tự kiểm GIF ba lần hoặc đảm bảo hoạt cảnh chơi được.
