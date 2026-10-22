# DONE — "hoàn hảo" nghĩa là gì, và kiểm bằng gì

> Mục đích: biến chữ **"hoàn hảo"** từ một tính từ thành **4 mức kiểm được**.
> Không mức nào dùng % tự đánh giá. Số đếm được ghi **(A)**, ước lượng ghi **(C)**.
> Mục cuối: **Còn thiếu / phải đoán**.

> **Sửa lại (lần 2):** bản đầu của file này phóng đại khối lượng. Sau khi đọc **tên gốc** spawner
> và **dedup**, con số thật nhỏ hơn nhiều: **48 archetype spawner**, **92 prefab enemy**,
> **10.776 placement** (median **28/wave**), và **boss là 45 wave riêng**. Xem §1.

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

## 1. Hoá đơn sản xuất — **sửa lại: nhỏ hơn tôi nói**

> ⚠ **Mục này bản trước sai.** Tôi viết "23.757 spawner / 282 wave = 84,2 mỗi wave" và
> "1.015 cấu hình đặt tay". **Cả hai đều phóng đại.** Đếm lại theo **tên gốc** và **dedup**:

### 1.1 Quy luật spawn — có, và rất rõ

Tên spawner có dạng `TênGốc (n)` — **`(n)` chỉ là số thứ tự instance**, không phải cấu hình khác.
Bỏ hậu tố đó: **1.015 tên → 53 tên gốc**, trừ 5 marker (`StartPoint`/`EndPoint`/`CheckPlayerNo`/
`KhoaPlayer`/`Endpoint`) còn **48 archetype spawner thật**.

| Archetype | Số lần | `spawn_type` | `rate` | `y_spawn` |
|---|---:|---|---|---|
| `CB1 Nhanh` (nhanh) | 4.622 | point_range **100%** | **1,0 cho 4.622/4.622** | **9,6 cho 4.618** |
| `Point 1` | 4.192 | point / point_range | 1,0 (2.536) · 0,0 (1.656) | 12,0 (2.262) |
| `CB1 Vua` (vua) | 2.951 | point_range **100%** | **1,0 cho 2.951/2.951** | **9,6 cho 2.945** |
| `CB1 Cham` (chậm) | 1.487 | point_range **100%** | **1,0 cho 1.487/1.487** | **9,6 cho 1.487** |
| `6-CB09_Left` | 1.238 | point_range | 0,0 (1.172) | 9,6 (1.238) |
| `CB1` | 1.150 | point_range | 0,0 (953) | 12,0 (880) |
| `Path_CB3_5` | 1.130 | path **100%** | 0,5 (571) | 9,6 (1.114) |
| `Group` | 929 | point_range | 0,0 (929) | 0,0 (605) |
| `ChamNo` | 536 | point_range | 1,0 (536) | 9,6 (528) |
| `CB15` | 435 | point_range | 0,0 (359) | 0,0 (269) |
| `Point_H` | 387 | point | 0,0 (387) | 12,0 (387) |
| `CB1 Ban Vua` | 304 | point_range | 1,0 (304) | 9,6 (304) |

**Đọc ra:** mỗi archetype có **bộ tham số gần như hằng số**. `CB1 Nhanh` = "nhanh, một nhịp,
xuất hiện ở y 9,6" — chạy 4.622 lần với đúng cùng tham số. Đây là **quy luật**, không phải
đặt tay từng cái. **Bạn đúng.**

### 1.2 Số thật sau khi bỏ bản trùng export

| Chỉ số | Bản trước (sai) | **Đếm lại** | Ghi chú |
|---|---:|---:|---|
| Spawner ghi nhận | 23.757 | 23.757 | giữ nguyên (đúng là dữ liệu thô) |
| − trừ marker `StartPoint`/`EndPoint` | — | **22.385** | khớp `ENCOUNTERS.md` §0 |
| **Sau dedup (cùng tên + type + rate + speed + y)** | — | **10.776** | **45,4%** — 12.981 dòng là bản trùng |
| Placement/wave | **84,2** | **median 28** (min 3 · max 255) | **giảm 3×** |

> `> Nhận định (mức B):` 10.776 placement, dựng từ **48 archetype**. Nghĩa là nội dung wave
> **không phải** 23.757 lần đặt tay — mà là **~11.000 lần** chọn-trong-48-và-đặt-vị-trí.
> Đây là công việc **có thể tự động hoá phần lớn**.

### 1.3 Chỉ có **92 prefab enemy** — không phải hàng trăm

Đếm từ `Enemy_Datas.csv` theo **root của prefab path** (bỏ sub-object `Gun5`/`HP`/`Child2`):

| Họ | Số prefab | Dải id | Vai trò |
|---|---:|---|---|
| `CB` (30xxx) | **26** | 30001–30060 | enemy thường chương 1 |
| `CD` (31xxx) | **13** | 31002–31016 | " |
| `GD` (33xxx) | **4** | 33002–33005 | " |
| `XB` (34xxx) | **4** | 34003–34006 | " |
| `BB` (36xxx) | **3** | 36001–36004 | " |
| `H` (38xxx) | **2** | 38001–38002 | " |
| **Tổng enemy thường** | **52** | | |
| `Boss` (37xxx + 39xxx) | **39** | 37001–39021 | boss |
| `MB` (39xxx) | **1** | 39005 | mini-boss |
| **Tổng** | **92** | | |

**Bạn đúng lần nữa:** **52 loại enemy thường** + **40 boss-family**. Không phải 690 GameObject
như tôi ghi trước đó — 690 là **mọi** object trong prefab (súng, hitbox, con, hiệu ứng).

> Còn **45.659 slot `enemies` = `"?"`** là thật — nhưng đó là **tham chiếu chưa resolve**,
> không phải "45.659 thứ phải thiết kế". Trần nội dung enemy là **52 + 40 = 92 prefab**.

### 1.4 Boss là **màn riêng** — xác nhận

| Nhóm wave | Số wave | Vai trò |
|---|---:|---|
| `Wave_00xx` – `Wave_02xx` | **236** | campaign thường |
| `Wave_70xx` | **22** | **boss chương 1** — màn riêng |
| `Wave_90xx` | **23** | **boss chương 2** — màn riêng |
| `unknown` | 1 | lỗi export |
| **Tổng** | **282** | |

Board cũng tách: `Stage_Behaviour.stageType` = Normal **199** · **Combat 49** · Boss **26** ·
MiniBoss **25** (nguồn: `Stage_Behaviour.csv`).

> **Sửa lỗi đọc trước:** tôi từng ghi "686 spawner `spawn_type = boss`". Sai — `boss` ở đây là
> **marker `EndMapPoint`** có mặt ở **mọi** wave (686 lần trên 281 wave), không phải nội dung boss.
> Nội dung boss nằm ở **45 wave riêng** (`70xx`/`90xx`).

### 1.5 Hoá đơn còn lại

| Hạng mục | Số lượng (A) | Nguồn |
|---|---:|---|
| Wave | **282** = 236 campaign + 45 boss + 1 lỗi | `waves.json` |
| Placement spawner **sau dedup** | **10.776** | tính lại §1.2 |
| Archetype spawner | **48** (+5 marker) | tính lại §1.1 |
| Prefab enemy | **92** = 52 thường + 39 boss + 1 MB | `Enemy_Datas.csv` §1.3 |
| Stage trên board | **299** (Normal 199 · Combat 49 · Boss 26 · MiniBoss 25) | `Stage_Behaviour.csv` |
| `Gun_Attack` → cấu hình súng | **458 → 420** | `Gun_Attack.csv` |
| Ô shop | **315** trên **20** board | `Shop_Cell.csv` |
| Class UI | **125** | `class-inventory.csv` |
| Sprite | **2.185** | `04-asset-manifest.csv` |
| Atlas page | **67** · 31,0 MB | `04-asset-manifest.csv` |
| AudioClip | **69** | `04-unity-assets.md` |
| Chuỗi localization | **1.416** | `12-localization.csv` |
| SKU IAP | **170** | `IAPProduct.csv` |

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
- **Đơn giản và nhỏ — cả hai đều đúng ở đây.** 48 archetype + 92 prefab enemy là **bộ từ vựng nhỏ**.
  Khối lượng thật là **10.776 placement** (sau dedup), median **28/wave** — không phải 84.
- **45.659 slot `"?"`** là thật, nhưng trần nội dung chỉ là **92 prefab enemy** — nên cái thiếu là
  **cách gán 45.659 tham chiếu**, không phải 45.659 thiết kế mới. Resolve `m_PathID` là xong phần lớn.

> `> Kết luận (mức B):` bắt chước đưa bạn tới **L1** nhanh. **L2** cần 2 tool. **L3** cần
> vòng playtest. Ba mức này **không loại trừ nhau** — chúng là **ba khoản chi phí khác nhau**,
> và không khoản nào là "không cần làm".

---

## 5. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | Giá trị **5.818** field (`4.861` serialized + `957` static) | **D** | chưa chạy AssetRipper/Ghidra |
| 2 | **45.659** tham chiếu enemy trong wave | **D** | `waves.json` = `"?"`; cần resolve `m_PathID` — trần chỉ **92 prefab** |
| 3 | Ngưỡng N người cho test L3 | **C** | phải tự chọn; chưa ai trong dự án đo |
| 4 | Dung sai cho L2 | **C** | phải tự chọn (đề xuất ±5%, chưa có cơ sở) |
| 5 | Thời gian làm 282 wave | **C** | không đoán ở đây; phụ thuộc công cụ authoring |

> Không có dòng nào trong bảng này là "không thể". Cả 5 dòng đều là **"chưa chọn"** hoặc
> **"chưa chạy"** — hai trạng thái khác nhau, và cả hai đều **đổi được**.
