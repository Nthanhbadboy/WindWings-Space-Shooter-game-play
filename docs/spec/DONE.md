# DONE — "hoàn hảo" nghĩa là gì, và kiểm bằng gì

> Mục đích: biến chữ **"hoàn hảo"** từ một tính từ thành **4 mức kiểm được**.
> Không mức nào dùng % tự đánh giá. Số đếm được ghi **(A)**, ước lượng ghi **(C)**.
> Mục cuối: **Còn thiếu / phải đoán**.

---

## 0. Trả lời ngắn

**"Game đơn giản" — đúng. "Bắt chước là ra" — đúng, nhưng chỉ tới một mức.**

| Mệnh đề | Đánh giá | Vì sao |
|---|---|---|
| Game **đơn giản về cơ chế** | ✅ **đúng** | 2.5D sprite · physics 2D · không netcode realtime · không navmesh · không rig 3D (§`AI_FEASIBILITY.md` §1.9) |
| **Bắt chước** cho ra game **chơi được** | ✅ **đúng** | cơ chế đã có đủ số; AI dựng được khung |
| Bắt chước cho ra game **hoàn hảo** | 🟡 **đúng một phần** | bắt chước giải quyết **thiết kế**, không giải quyết **khối lượng** và **kiểm chứng** |

> **Điểm cần tách:** *đơn giản* và *nhỏ* là **hai trục khác nhau**.
> Game này **đơn giản** (ít hệ thống phức tạp) nhưng **không nhỏ** (rất nhiều đơn vị nội dung).
> Bắt chước làm trục "đơn giản" rẻ đi gần như bằng 0. Nó **không** làm trục "khối lượng" rẻ đi.

---

## 1. Hoá đơn sản xuất — cái phải *làm ra*, không phải cái phải *hiểu*

Đếm trực tiếp từ `docs/apk-analysis/*.csv` và `datas/waves.json`:

| Hạng mục | Số lượng (A) | Nguồn |
|---|---:|---|
| Wave | **282** | `waves.json` (`count_waves`) |
| Spawner trong wave | **23.757** | `waves.json` (`count_spawners`) |
| **Slot enemy trong spawner** | **45.659** — **tất cả đều `"?"`** | `waves.json` |
| Tên spawner khác nhau | **1.015** | `waves.json` |
| Stage trên board | **299** | `Stage_Behaviour.csv` |
| `Gun_Attack` → cấu hình súng | **458 → 420** | `Gun_Attack.csv` |
| Enemy có dữ liệu | **800 dòng → 690 GameObject** | `Enemy_Datas.csv` |
| Boss prefab | **39** | `15-enemy-hp.csv` |
| Ô shop | **315** trên **20** board | `Shop_Cell.csv` |
| Class UI | **125** (53 board · 63 popup · 8 tab · 1 cell) | `class-inventory.csv` |
| Sprite | **2.185** | `04-asset-manifest.csv` |
| Atlas page | **67** · 31,0 MB · max 3,09 MB | `04-asset-manifest.csv` |
| AudioClip | **69** | `04-unity-assets.md` |
| `SoundClip` (khai báo) | **92** | `SoundClip.csv` |
| Chuỗi localization | **1.416** | `12-localization.csv` |
| SKU IAP | **170** | `IAPProduct.csv` |

**Ba con số đáng chú ý nhất:**

| Con số | Nghĩa |
|---|---|
| **45.659** slot enemy đều `"?"` | **Toàn bộ** nội dung enemy của game là **chưa biết** — không phải một phần |
| **1.015** tên spawner khác nhau | không phải 3–4 template lặp; là **1.015** cấu hình đặt tay |
| **23.757** spawner / 282 wave = **84,2** | trung bình **84** spawner mỗi wave |

> `> Nhận định (mức B):` đây là lý do khối lượng **không** co lại theo độ đơn giản.
> Một wave "đơn giản" vẫn phải đặt 84 spawner. 282 wave vẫn là 282 lần đặt.

---

## 2. Bốn mức "hoàn hảo" — và mỗi mức kiểm bằng gì

Thay vì tranh luận, định nghĩa **4 mức tăng dần**, mỗi mức có **bài kiểm cụ thể**.

### L0 — Chạy được

| | |
|---|---|
| **Nghĩa** | build mở được, vào màn, bắn, chết, qua màn |
| **Kiểm bằng** | máy: chạy 30 phút không crash, không log error |
| **Đạt khi** | 100% màn chơi không exception |
| **Bắt chước đủ?** | ✅ **đủ** — đây là mức AI làm tốt nhất |
| **Chi phí** | thấp |

### L1 — Đúng luật

| | |
|---|---|
| **Nghĩa** | cơ chế hành xử đúng như spec, không chỉ "giống giống" |
| **Kiểm bằng** | máy: **test tự động** đối chiếu từng con số đã có (mức A) |
| **Ví dụ test cụ thể** | wave 0163 spawn **621** spawner · `rate` mặc định **1,0** (16.173 spawner) · `y_spawn` **9,6** (15.485) · vùng chơi **20×25** unit · bán kính va chạm đạn **15** · `border.w` 15 cho **799/800** |
| **Đạt khi** | **100%** test pass |
| **Bắt chước đủ?** | ✅ **đủ cho phần đã có số** — nhưng phải **viết test**, bắt chước không sinh ra test |
| **Chi phí** | trung bình |

> Đây là mức mà `Spec2Game` đo được **Rule & Mechanism 45,6/100** — tức mức mà AI **hay trượt nhất**
> khi chỉ có đặc tả. Cách chặn: **test viết trước**, không phải review bằng mắt.

### L2 — Đúng số

| | |
|---|---|
| **Nghĩa** | cùng một phát bắn ra **cùng một lượng damage**; cùng một wave ra **cùng nhịp** |
| **Kiểm bằng** | máy: replay 1 wave, so DPS/TTK/HP với bản gốc trong **dung sai khai báo trước** |
| **Đạt khi** | (dung sai do bạn chọn — ví dụ ±5%) |
| **Bắt chước đủ?** | ❌ **chưa** — cần **giá trị thật**, hiện còn ở mức **D** |
| **Đang thiếu gì** | **4.861** `[SerializeField]` + **957** `static` chưa có giá trị (`AI_FEASIBILITY.md` §1.10) |
| **Chi phí** | chạy AssetRipper + Ghidra |

> L2 là mức **"bắt chước" đúng nghĩa nhất** — và cũng là mức **chưa đạt được hôm nay**.
> Không phải vì khó, mà vì **chưa chạy 2 tool**.

### L3 — Không phân biệt được

| | |
|---|---|
| **Nghĩa** | người đã chơi bản gốc **không chỉ ra được** bản nào là gốc |
| **Kiểm bằng** | **người**: blind A/B, N người chơi, mỗi người 2 bản, chọn bản nào là gốc |
| **Đạt khi** | tỉ lệ chọn đúng **không khác 50%** có ý nghĩa thống kê |
| **Bắt chước đủ?** | ❌ **không** — cái này là **cảm giác**, không nằm trong file nào |
| **Chi phí** | **cao nhất** — cần playtest thật |

> **Đây là mức duy nhất xứng với chữ "hoàn hảo".** Và nó **không** được giải quyết bởi
> reverse engineering — nó được giải quyết bởi **số vòng playtest**.

---

## 3. Bắt chước giải quyết cái gì — bằng số

| Việc | Bắt chước có giúp? | Vì sao |
|---|---|---|
| Biết **cần làm gì** | ✅ **gần hết** | 45.659 slot, 1.015 spawner, 420 súng — **đã có danh sách** |
| Biết **con số đúng** | 🟡 **một phần** | 25 hằng số đọc ngay; 5.818 field còn ở mức D |
| **Làm ra** 282 wave × 84 spawner | ❌ **không** | khối lượng, không phải hiểu biết |
| **Vẽ** 2.185 sprite thay thế | ❌ **không** | gu thẩm mỹ |
| **Đo** cảm giác (L3) | ❌ **không** | cần người chơi thật |
| Chọn **bỏ gì, thêm gì** | ❌ **không** | quyết định thiết kế |

> **Cách nói chính xác:** bắt chước biến **"không biết làm gì"** thành **"biết phải làm gì, rất nhiều"**.
> Đó là một bước rất lớn — nhưng nó **không** làm bước "làm" biến mất.

---

## 4. Chỗ tôi đồng ý với bạn, và chỗ tôi phải nói khác

### Đồng ý

- Game này **đơn giản** — so với 3D open world hay realtime PvP, nó **dễ hơn nhiều lần**.
- **Bắt chước là chiến lược đúng** — không phải đạo đức giả; rất nhiều game mobile thành công
  là "cùng thể loại, khác art". Đó là **bình thường** trong ngành.
- Một đội 3 người + AI **có thể** ra sản phẩm **người chơi thấy tương đương**. Đó là mục tiêu thật.

### Nói khác

- **"Hoàn hảo" phải định nghĩa ở mức nào** — L0/L1/L2/L3 ở trên. Không có định nghĩa thì không
  kiểm được, và cái gì không kiểm được thì không biết đã đạt chưa.
- **Đơn giản ≠ nhỏ.** 23.757 spawner là khối lượng, không phải độ phức tạp.
- **45.659 slot enemy đều `"?"`** — đây không phải "chi tiết nhỏ còn thiếu", mà là **nội dung
  enemy của toàn bộ game**. Imitation không điền vào đó; **thiết kế** mới điền được.

> `> Kết luận (mức B):` bắt chước đưa bạn tới **L1** nhanh. **L2** cần 2 tool. **L3** cần
> vòng playtest. Ba mức này **không loại trừ nhau** — chúng là **ba khoản chi phí khác nhau**,
> và không khoản nào là "không cần làm".

---

## 5. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | Giá trị **5.818** field (`4.861` serialized + `957` static) | **D** | chưa chạy AssetRipper/Ghidra |
| 2 | **45.659** slot enemy trong wave | **D** | `waves.json` = `"?"`; cần resolve `m_PathID` |
| 3 | Ngưỡng N người cho test L3 | **C** | phải tự chọn; chưa ai trong dự án đo |
| 4 | Dung sai cho L2 | **C** | phải tự chọn (đề xuất ±5%, chưa có cơ sở) |
| 5 | Thời gian làm 282 wave | **C** | không đoán ở đây; phụ thuộc công cụ authoring |

> Không có dòng nào trong bảng này là "không thể". Cả 5 dòng đều là **"chưa chọn"** hoặc
> **"chưa chạy"** — hai trạng thái khác nhau, và cả hai đều **đổi được**.
