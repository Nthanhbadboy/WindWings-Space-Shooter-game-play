# BỘ KỊCH BẢN GAME — MỤC LỤC & TẦM NHÌN (00)

> Đây là bộ tài liệu kịch bản đầy đủ của game, viết theo phương pháp:
> **nguyên mẫu là thư viện chất liệu và ngôn ngữ thiết kế — sáng tạo nội dung
> mới trên nền đó, không sao chép asset/số liệu bề mặt.**
> Mọi con số ghi "[gốc]" đều truy được về `datas/` hoặc `docs/spec/` của repo.
> `GAME_DIRECTOR_VISION.md` (docs/rollout) là bản luật tóm tắt; bộ này là bản
> đầy đủ có hiệu lực chi tiết. USER là người duyệt thẩm mỹ/trải nghiệm cuối cùng.

## Mục lục bộ kịch bản

| Tập | Nội dung | Câu hỏi nó trả lời |
|---|---|---|
| 01 | Chiến dịch, wave & địch | Người chơi bay qua những gì, theo nhịp nào? |
| 02 | Hạm đội, hangar & tiến trình | Người chơi sở hữu gì, lớn lên thế nào? |
| 03 | Sách boss (Boss Book) | Mỗi con boss là ai, đánh thế nào, chết thế nào? |
| 04 | Chiến đấu, FX & nghệ thuật chuyển động | Trận đánh trông/nghe/cảm thấy ra sao? |
| 05 | Màn hình, UI, âm thanh & hệ thống phụ | Toàn bộ khung sườn thương mại quanh trận đánh |
| 06 | Lộ trình sản xuất & cổng duyệt | Làm theo thứ tự nào, xong là xong thế nào? |

## Game trong một câu

Phi công tinh nhuệ xuất kích từ hangar trạm vũ trụ, xuyên qua các chặng
pháo đài địch theo đội hình leo thang, hạ boss trấn ải trong một trận đấu
như cảnh phim, mang chiến lợi phẩm về hangar nâng cấp tàu — và mạnh dần
lên qua một chiến dịch dài như game thương mại thật.

## Quy mô nguyên mẫu (chất liệu tham chiếu) vs quy mô bản làm mới

| Hạng mục | Nguyên mẫu [gốc] | Launch Slice (mốc đầu) | Tầm nhìn đầy đủ |
|---|---|---|---|
| Wave | 282 wave · 23.757 spawner · 22.451 lượt địch (`waves.json`) | 5 wave (Wave_0016–0020) | Theo chương, mở dần về phía 282 |
| Địch thường | 70 prefab · 399 đường bay · 981 dòng HP (`enemy_hp.json`) | 13 loại của 5 wave | Đủ họ địch theo 01 |
| Boss | 39 prefab · 46 sprite · 795 event animation (`boss_anim_events.csv`) | 1 boss mẫu chuẩn (Boss-37001) | 39 boss theo Boss Book (03) |
| Tàu người chơi | 25 tàu (`ships.json`) · 13 drone · 23 method talent | 3 tàu chọn được | Mở dần theo tiến trình (02) |
| Vũ khí/đạn | 458 súng · damage 40–1.200 (median 400) · 186 loại đạn (`COMBAT.md`) | Bộ súng cơ bản 3 tàu | Phân họ theo 04 |
| Màn hình UI | 797 màn · 150.131 node · 5.831 nút | ~8 màn cốt lõi (05) | Đủ luồng thương mại theo 05 |
| Âm thanh | 92 id registry · 69 clip/571,5s · 15 luật (`audio_rules.json`) | Nhạc 3 khu vực + SFX chính | Theo bản đồ âm thanh (05) |
| Hệ thống phụ | Arena 10 hạng · PvP 10 hạng · Battle Pass 85+39 mốc · login 30 ngày · VIP · energy · 170 IAP | Chỉ vòng lặp lõi + sao lưu | Theo lộ trình 06, IAP = USER-ONLY |
| Sprite | 2.885 catalog (2.184 sprite) — **cấm dùng lại, chỉ tham chiếu ngôn ngữ** | Đếm theo slot thật | Kế hoạch sản xuất theo lô (04) |

## Ba trụ cột (lặp lại từ luật đạo diễn — mọi tập đều phải tuân)

1. **Đọc được:** 0,5 giây ở kích thước thật phân biệt ta/địch/đạn.
2. **Sống:** không thực thể chính nào là ảnh tĩnh.
3. **Công bằng:** mọi sát thương lớn đều báo trước đủ thời gian né.

## Quy ước phạm vi trong toàn bộ tài liệu

- **[SLICE]** — bắt buộc có trong Launch Slice (mốc đang làm).
- **[MỞ RỘNG]** — thuộc tầm nhìn đầy đủ, làm sau khi Slice được USER duyệt.
- **[CẮT]** — quyết định không làm (ghi rõ để không ai tự mở lại).
- Mọi session nhận việc phải khai: làm theo tập nào, mục nào của bộ này.
