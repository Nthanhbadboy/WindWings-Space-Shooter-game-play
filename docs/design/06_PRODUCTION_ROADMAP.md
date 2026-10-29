# 06 — LỘ TRÌNH SẢN XUẤT & CỔNG DUYỆT

## 6.1 Nguyên tắc lộ trình

Làm **trọn vẹn từng lát dọc (vertical slice)** theo vòng lặp tập 00:
mỗi mốc phải chơi được từ menu → hangar → trận → kết quả, dù nội dung
ít. Cấm làm ngang (vẽ hết địch rồi mới có hangar; code hết hệ thống rồi
mới có art). Thứ tự dưới đây khóa cứng; việc ngoài lộ trình phải có lệnh
riêng của director/USER.

## 6.2 Các mốc

### Mốc A — Boss mẫu chuẩn (đang dở, hoàn thiện trước)
- Art: hồ sơ Boss-37001 đầy đủ (Boss Book 3.2): linh kiện đã có →
  bổ sung hư hại bậc, mảnh vỡ, chuỗi nổ, GIF xoay chứng minh pivot,
  BOSS_SPEC (đòn theo %HP + thông số + khe né) **kèm Bảng chuẩn đạn &
  pha đã tra gốc** (nguồn: tập 04 §4.1 — `COMBAT.md` §3+§7,
  `Gun_Attack.csv`, `Bullet_Linearly.csv`; mỗi thông số ghi [GỐC] hoặc
  [ĐỀ XUẤT]). SPEC còn để thông số dạng tính từ ("nhỏ hơn glow") là
  chưa đạt cổng, phải quay lại tra.
  **Kế hoạch lô theo năng lực 10 ảnh/turn (tập 04 §4.3):** Lô A1 (≤10):
  món bổ sung còn thiếu của bộ linh kiện (hư hại bậc 2–3, mảnh vỡ, chuỗi
  nổ...) — phần lớn linh kiện chính đã có sẵn nên lô này nhỏ; Lô A2:
  chỉ sinh thay thế các món lỗi/chưa chuẩn phát hiện qua GIF xoay và
  đối chiếu kịch bản; sau đó 1 turn hậu kỳ + render GIF/bằng chứng
  (không tính quota sinh ảnh). Không được khai "xong hồ sơ" trước khi
  các lô này đủ.
- Coder (chỉ sau khi hồ sơ duyệt): cài boss thành hệ thống theo tình
  huống; vũ khí tia/tên lửa là vũ khí thật có hitbox.
- **Cổng A:** USER duyệt GIF hoạt cảnh; bản build cho 2 clip chơi khác
  nhau → 2 trận khác nhau cùng tính cách; pivot không lộ lỗi ở build thật.

### Mốc B — Hangar thật
- Coder dựng scene theo tập 02 (khung tạm được phép, ghi placeholder),
  art giao lô: nền khoang + khung giàn + bệ (lô 10 ảnh đầu cùng địch).
- **Cổng B:** clip 30s hangar sống; đổi 3 tàu mượt; xuất kích từ hangar
  vào thẳng wave 1; USER mở build thấy hangar ngay, không phải tìm.

### Mốc C — Đội địch & 5 wave có hồn
- Art theo lô: đủ 13–16 địch của 5 wave (tập 01) + đạn 2 phe + FX cơ bản.
- Coder: ý đồ wave đọc được (đặt tên ý đồ trong dữ liệu wave), địch có
  hành vi theo họ, hết địch hình thoi trong bản Slice.
- **Cổng C:** chơi liền 5 wave không gặp asset tạm; mỗi wave gọi tên
  được ý đồ; độ khó leo thang cảm nhận được.

### Mốc D — Đóng gói Launch Slice như một game nhỏ
- Đủ vòng: menu → hangar → 5 wave → boss mẫu → kết quả sao → về hangar
  nâng cấp → chơi lại mạnh hơn. Nhạc 3 khu vực + SFX chính (05).
- **Cổng D (cổng lớn):** USER chơi từ đầu tới cuối trên Windows như một
  game hoàn chỉnh nhỏ và phán quyết "đây là game" — trước cổng này mọi
  báo cáo đều là "đang làm", sau cổng này mới mở rộng nội dung.

### Mốc E+ — Mở rộng theo chương (sau Cổng D)
Mỗi chương: 1 vùng nền, 4–8 địch, 1 boss theo Boss Book (viết hồ sơ
trước), có thể 1 tàu. Arena/meta phụ theo 05 chỉ khi vòng lặp đã chứng
minh giữ chân được người chơi.

## 6.3 Cổng duyệt & bằng chứng (áp cho mọi mốc)

Thứ hạng bằng chứng (cao → thấp): **(1)** USER chạy trên máy →
**(2)** clip runtime 2 lần chơi khác nhau → **(3)** GIF hoạt cảnh từ
asset thật → **(4)** ảnh tĩnh. Báo cáo phải tự ghi bằng chứng của mình
đang ở hạng nào; gọi sai hạng là lỗi báo cáo nghiêm trọng.

Mỗi bàn giao bắt buộc có: danh sách đếm được (file/slot/scene), phần
placeholder nêu tên, đường dẫn file/artifact + hash, và một câu
"chưa làm gì" rõ ràng. Session không tự tuyên bố PASS thẩm mỹ — USER duyệt.

## 6.4 Vai trò

- **Director (session điều phối):** giữ bộ kịch bản này, phát lệnh theo
  mốc, kiểm chứng độc lập mọi báo cáo (đọc file, xem ảnh, đối chiếu CI)
  trước khi trình USER.
- **Art:** chịu trách nhiệm hình + linh kiện + kịch bản chuyển động +
  thông số thị giác; giao theo lô đếm được.
- **Coder:** chịu trách nhiệm hệ thống chơi được + build Windows qua CI;
  không tự hình dung thẩm mỹ, thiếu asset thì báo thiếu đúng tên slot.
- **USER:** duyệt đẹp/xấu và trải nghiệm; quyết định phạm vi.

### 6.4.1 Phân vai chi tiết (chốt 29/10 — bắt buộc mọi session tuân thủ)

| Việc | Director | Art | Coder | USER |
|---|---|---|---|---|
| Kịch bản trận đấu/pha, chuẩn đạn & số, tính công bằng | **QUYẾT** (viết vào Boss Book/SPEC; trả lời câu hỏi chặn bằng dữ liệu gốc) | Đề xuất kèm lý do, gắn nhãn [ĐỀ XUẤT], **không tự ý đổi chuẩn đã chốt** | Đề xuất khi vướng kỹ thuật, không tự đổi số cân bằng | Duyệt khi tranh chấp khó/dễ |
| Hình ảnh: bố cục, linh kiện, màu, chi tiết, chọn ảnh sinh | Đặt **chuẩn đầu ra** (đọc được ở cỡ thật, tách lớp, pivot có bằng chứng) | **TỰ ĐẠO DIỄN HÌNH ẢNH + chỉnh chu**: sinh lại không giới hạn số ảnh cho tới khi đạt chuẩn; tự chấm bằng bảng chất lượng | Không can thiệp hình; thiếu/không khớp thì báo đúng tên slot/lỗi | **Duyệt đẹp/xấu cuối cùng** |
| Animation trong engine | Chốt doctrine 3 tầng (tập 04) | Cung cấp linh kiện + kịch bản + bằng chứng xoay | Cài thành hệ thống theo tình huống (%HP/vị trí), cấm phang nguyên GIF/mốc giây | Duyệt bằng bản chạy thật |
| Kiểm chứng | Đối chiếu độc lập file/số/CI/ảnh trước khi trình USER | Tự kiểm có bằng chứng đính kèm | Test + CI + bằng chứng runtime | Phán quyết cuối |

Quy tắc leo thang: session gặp chỗ kịch bản chưa có/chưa rõ thì **hỏi
bằng văn bản trên board, gắn câu hỏi vào đúng mục tài liệu** — director
trả lời vào chính tài liệu đó (không trả lời miệng trôi qua). Session
tự ý quyết thay phần của director = sản phẩm bị trả lại, dù đẹp.
