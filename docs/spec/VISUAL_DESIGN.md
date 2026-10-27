# VISUAL_DESIGN — "đẹp" là thứ **đo được**, không phải thứ phải bỏ

> Viết 25/10, sau khi bị hỏi đúng: *"sao bỏ L3 được, yếu tố để thiết kế cho đẹp"*. **Cập nhật lần 14
> (25/10): L3 = tái lập 1:1 trải nghiệm + art bản gốc là ĐÍCH của dự án học tập thiết kế — không bỏ,
> KHÔNG hoãn**; APK gốc là chuẩn đã kiểm nghiệm ⇒ nghiệm thu = **đối chiếu reference đo được** (không
> cần người test thật). Tài liệu này là **bộ số nghiệm thu** cho phần thị giác — và **art là phần
> thiết kế duy nhất của bạn**: vẽ lại hình ảnh cho khác (không copy file asset), còn **chuẩn màu/
> ánh sáng/khung/nhịp giữ theo số ở đây**; thắc mắc tra reference là có đáp án.
>
> Đo bằng `tools/design-metrics.py` trên **35 ảnh chụp thật** (`docs/apk-analysis/ramus/2026-10-23-phone/`).
> Kết quả thô: `docs/assets/design-metrics.json`. Claim **AN1**, **AN2**.
>
> **Nguyên tắc:** ảnh chỉ dùng để **đo tỉ lệ, độ tương phản, ngân sách màu** — **không** dùng để
> vẽ lại, không lấy màu gốc, không cắt sprite. Art của game mới vẫn phải vẽ mới (xem `ASSETS.md` §1).

---

## 1. Khung hình — cái phải chốt trước mọi thứ khác

| Số đo | Giá trị | Hệ quả thiết kế |
|---|---|---|
| Độ phân giải ảnh chụp | **720 × 1.496** | canvas tham chiếu **một thiết bị** 1080 × 2244 — **không** phải canvas engine bắt buộc |
| Tỉ lệ | **0,4813** (≈ **9 : 18,7**) | dọc, cao hơn 16:9 — dùng làm **tham chiếu thiết kế**; game mới phải **responsive + safe-area**, không khoá cứng theo tỉ lệ này |
| Ảnh dùng được để đo | **35** | 28 cụm bố cục khác nhau (nhiều ảnh chụp lại cùng trạng thái) |
| **Tổng hợp đo được** | **35** ảnh · tỉ lệ **0,4813** · accent trung vị **0,0571** · chi tiết trung vị **17,26** | claim **AN1** |

---

## 2. Ba "chế độ sáng" của game — và mỗi chế độ có luật riêng

Đo trên cả 35 ảnh, chúng tự chia thành **3 cụm** rất rõ. Đây là thứ quan trọng nhất trong tài liệu này:
**không có một bảng màu duy nhất**, có **ba trạng thái thị giác**.

| Cụm | Ảnh | Bão hoà | Tương phản (p95−p05) | **Ngân sách accent** | Chi tiết (gradient) | Đọc là |
|---|---|---:|---:|---:|---:|---|
| **A. Gameplay** | 12 (`p_*`, `slow_*`, `live_1`, `after_touchtoplay`) | **0,56 – 0,70** | **0,47 – 0,76** | **2 – 10 %** | **13 – 22** | nhiều màu nhưng accent **rải**, không dồn |
| **B. Khung thưởng / kết trận** | 12 (`live_2…5_EndGame`, `victory_*`, `boss_now`) | **0,75 – 0,77** | **0,66** | **~47 %** | 17 | **một panel rực** chiếm gần nửa khung |
| **C. Màn tối / chuyển cảnh** | 9 (`live_6/7`, `r2_*`, `screenshot_*`) | (0,91 – 0,94 ✳) | **0,05 – 0,12** | 1 % | **2 – 5** | nền gần đen + UI mảnh |

✳ **Cảnh báo đọc số:** ở cụm C, giá trị sáng trung bình chỉ **0,03 – 0,06** ⇒ khi gần đen thì "độ bão
hoà" **vô nghĩa** (chia cho max≈0). Đừng trích 0,93 của cụm C làm "game bão hoà cao" — đó là **lỗi đọc**.

### 2.1 Luật rút ra (dùng được ngay, không cần bản gốc)

1. **Ngân sách accent:** gameplay **≤ 10 %** số pixel được là màu nóng bão hoà; panel thưởng được
   phép **~45 %**. Nếu cả màn đều 40 % accent thì khung thưởng **hết** nổi bật.
2. **Tương phản tối thiểu 0,45** (p95−p05 trên thang 0–1). Dưới 0,4 là "phẳng"; trên 0,8 là chói.
3. **Độ chi tiết 13–22** (trung bình |ΔRGB| giữa 2 pixel kề, đo mỗi 2 px). Dưới 10 = trống, trên 25 =
   nhiễu. Đây là **proxy** cho "mật độ chi tiết" — dùng để so bản mới với bản gốc mà không cần nhìn.
4. **Ba dải sáng (trên 15 % / giữa / dưới 15 %)** — cụm B cho tỉ lệ **0,03 / 0,27 / 0,03** ⇒ viền trên
   và dưới **tối hơn tâm ~9 lần**. Đó là **vignette chủ đích**, không phải ngẫu nhiên: nó dồn mắt vào
   panel thưởng. Bản mới **nên giữ** kỹ thuật này (nó miễn phí và rất hiệu quả).

---

## 3. Hình học bố cục — đo trên **54.019** bbox **dẫn xuất** (không phải 54.019 màn độc lập)

`datas/ui_screens.json.gz` có `bbox` cho từng màn. **Đây là dữ liệu phái sinh từ dump UI** (một số file
có nhiều instance), nên **54.019 là số bbox**, không phải số màn đã kiểm độc lập — index được audit kỹ là
**797** file (report 62 tách riêng hàng chục nghìn file ngoài index). Muốn dùng làm số thiết kế thì phải
chốt **mẫu / frame / hash nguồn / cách gộp instance trùng** trước.

| Số màn có `bbox` dùng được | **54.019** | rộng trung vị **4,05** · cao **7,50** · tỉ lệ **0,67** | claim **AN2** |

| Số đo (đơn vị world) | p05 | **trung vị** | p95 | max |
|---|---:|---:|---:|---:|
| rộng | 3,32 | **4,05** | 10,72 | 43,85 |
| cao | 1,91 | **7,50** | 28,39 | 698,98 |
| tỉ lệ rộng:cao | 0,34 | **0,67** | 4,74 | — |

**Đọc ra luật thiết kế:**

- Panel **cao hơn rộng** (0,67 ≈ 2:3). Đừng thiết kế panel ngang kiểu tablet.
- **p95 cao 28,4** và **max 699** ⇒ **có** màn cao bất thường; đây là **dấu hiệu** danh sách cuộn, **không**
  chứng minh mọi màn là ScrollRect. Kết luận dùng được: layout phải chịu nội dung dài, **không** vỡ.
- **p95 rộng 10,72** so với trung vị 4,05 ⇒ có màn rộng gấp 2,6 lần; nếu làm theo lưới cố định 1 cột
  sẽ hỏng ở nhóm này (đây là các board bản đồ / sự kiện).

---

## 4. Chuyển động — "juice" đã có số từ dữ liệu, không cần cảm nhận

| Yếu tố | Số đo | Nguồn | Dùng thế nào |
|---|---|---|---|
| Hit flash | **0,5** alpha, **0,05 s** | `Enemy_Display.OnHit` (claim **J9**) | 0,05 s là **3 frame** ở 60 fps — đúng ngưỡng "thấy mà không chớp" |
| Rung màn hình | `lvVibr` **0,05 / 0,10 / 0,15** · `timeVibr` **15 / 20 / 30 / 40** frame | 241 prefab (claim **AF1**) | phổ biến nhất **0,10 · 20 frame** ⇒ biên độ nhỏ, thời gian ngắn |
| Nhịp đòn boss | **0,17 · 0,33 · 1,0 · 5,0 s** | `BOSS_ANIM_TIMELINE.md` | 0,17 s ≈ nửa nhịp thở; 5 s là "đòn nặng" |
| Chờ trong code | **38** chỗ `WaitForSeconds`, 4 hằng **0,5 / 1 / 2 / 3 s** | claim **J8** | nhịp chờ **thô** (nguyên giây) ⇒ game gốc canh nhịp bằng clip, không bằng code |

⇒ Ba con số dùng ngay: **flash 0,05 s · shake 0,10/20 frame · nhịp 0,17–0,33 s**. Về slow-mo: **0 site**
`timeScale` trên **139** file asm (claim **AF2**) chỉ là **mẫu**, **không** phải whole-build closure ⇒
**không** được nói "bản gốc không có slow-mo". Game mới dùng thì ghi rõ là **lựa chọn thiết kế**.

---

## 5. Giữ gì / đổi gì

| Hạng mục | Giữ (đo được, tái dùng) | Đổi (thuộc về bản mới) |
|---|---|---|
| Khung hình | tỉ lệ **0,4813**, panel dọc **0,67** | canvas cụ thể |
| Tương phản | **≥ 0,45**, ba dải sáng lệch **~9×** ở khung thưởng | cách tạo vignette (mask hay sprite) |
| Ngân sách màu | gameplay **≤ 10 %** accent · khung thưởng **~45 %** | **toàn bộ palette** — dùng "Ink & Ember" (`ASSETS.md` §1.2), **không** lấy màu gốc |
| Mật độ | chi tiết **13–22** | mức noise/giấy của art mới |
| Chuyển động | **0,05 s** flash · **0,10/20 frame** shake · nhịp **0,17–0,33 s** | easing, trail, particle |
| Hình khối | silhouette đọc được ở **64 px** (`ASSETS.md` §1.3) | hình học, outline, "mặt cười" hay không |

**Cổng phát hiện lệch (máy đo, **không** phải chứng nhận "đẹp"):** chụp 10 khung gameplay + 3 khung
thưởng, chạy `python3 tools/design-metrics.py <thư mục ảnh>` rồi so:

- tương phản **0,45 – 0,80**;
- accent gameplay **≤ 10 %**, khung thưởng **35 – 50 %**;
- chi tiết **13 – 22**;
- ba dải sáng của khung thưởng: viền/tâm **≤ 0,15**.

Lệch khỏi 4 khoảng đó = **cờ để xem lại**, không phải phán quyết. Máy **không** đo được silhouette,
độ đọc của đạn, font, thứ bậc thị giác, rối ren theo thời gian hay chất lượng art. Vì vậy **bắt buộc**
thêm: review **ảnh gameplay thật** + **motion** + kiểm trên **nhiều tỉ lệ màn hình** (không chỉ 0,4813).
Muốn đổi số thì phải ghi lý do thiết kế; muốn đổi art thì phải xem ảnh.

---

## 6. Vì sao không tái lập 1:1 (và vì sao điều đó **không** làm game xấu đi)

- Asset gốc (atlas `sactx-*`, font, Spine) **không** được phép tái phát hành — xem `ASSETS.md` §1
  legal checklist. Tái lập 1:1 = vi phạm, và cũng **không cần**: người chơi nhận ra "đẹp" qua
  **tỉ lệ, tương phản, nhịp**, không qua từng pixel.
- Cái **phải** tái lập là **cấu trúc thị giác**: khung hình dọc, ba chế độ sáng, ngân sách accent,
  vignette khung thưởng, mật độ chi tiết, nhịp juice. Tất cả đã có số ở §1–§4.

⇒ **L3 "tái lập 1:1 trải nghiệm + art" = ĐÍCH — không bỏ, KHÔNG hoãn (lần 14, 25/10); nghiệm thu chính là §1–§5 của tài liệu này, đối chiếu reference đo được.**
