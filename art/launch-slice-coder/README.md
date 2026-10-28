# Launch-slice — mẫu đang phát triển, chưa bàn giao

PLAYER-10001 là mẫu code mới đã qua `measure_asset.py --class ship --style` tại planner `100cfcebc38c`; đây chỉ là sàn số. Hình hiện có khối góc cạnh giản lược; chưa chứng minh đạt thẩm mỹ kim loại 2.5D. Chưa kiểm halo / độ đọc ở 64px / bảng so gốc / gate_batch; không coi là sẵn sàng tích hợp, chưa đạt L3.

`manifest-draft.json` ghi công thức màu và sáng đã khóa, metrics và SHA-256; `source/player_pipeline.py` tái dựng với Python Pillow+numpy, tham số AO `0.20`. Chạy script sẽ ghi `master.png` và `player.png` cạnh script. Chỉ nộp mẫu tàu vì mẫu CB-30003 áp cùng công thức trượt chuẩn enemy; không đưa mẫu đỏ vào repo. Chưa có các slot khác. License UNKNOWN.
