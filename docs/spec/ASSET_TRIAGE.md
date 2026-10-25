# ASSET_TRIAGE — bộ ảnh gốc còn **chưa phân loại** / **chưa tách** bao nhiêu?

> **Nguồn:** `docs/assets/sprites-index.csv` (import từ nhánh dữ liệu, commit `0a42eaa42`,
> blob **`d9e27f94a`**), `docs/assets/INDEX.md` (blob `72c9f12c3`), `docs/apk-analysis/04-asset-manifest.csv`.
> Mọi số dưới đây đọc lại được bằng `tools/verify-claims.py` (nhóm **AB**). Không dùng ảnh điện thoại.

**Trả lời ngắn: 2.197 asset · 1.554 chưa có nhãn · 132 sheet (116 chưa tách) · 67 page chưa có rect.**
Ba con số đó là **ba việc khác nhau**, đừng cộng thành một.

---

## 1. Quy mô và 13 nhóm đang có

| nhóm | số | ghi chú |
|---|---:|---|
| `unclassified` | **1.554** | sprite không khớp mẫu tên nào của pipeline phân loại |
| `atlas` | **132** | **Texture2D** = ảnh sheet gộp, **chưa** cắt thành sprite |
| `background` | 109 | nền, tinh vân, hành tinh |
| `fx` | 80 | nổ, trail |
| `ui` | 73 | icon/nút/khung |
| `audio` | 69 | 92 id → 92 file |
| `bullet` | 67 | đạn |
| `bosses` | 32 | boss theo wave |
| `enemy` | 31 | enemy thường |
| `ships` | 25 | tàu |
| `drones` | 13 | drone |
| `font` | 8 | font |
| `items` | 4 | item rơi |
| **tổng** | **2.197** | 133,6 MB (bản preview JPEG, PNG gốc ở draft release) |

**Sprite đã có PNG riêng:** **1.903** dòng `kind = Sprite` đều có `relative_path = Sprite/<tên>.png`
⇒ phần *sprite* **đã** được tách sẵn. Cái còn thiếu là **nhãn**, **sheet gộp** và **rect**.

---

## 2. Ba loại "chưa xong" — khác nhau

| loại | số | nghĩa | đóng bằng cách nào |
|---|---:|---|---|
| **(a) chưa đặt nhãn** | **1.554** sprite `unclassified` | có ảnh, không biết thuộc nhóm nào | luật tên + xem contact sheet (§4) |
| **(b) chưa tách** | **132** sheet `Texture2D`; **116** trong đó **không có sprite nào** được cắt ra | ảnh gộp nhiều sprite | cắt theo rect (§5) |
| **(c) chưa có rect** | **67** page `sactx-*` | atlas runtime; muốn cắt phải có `Sprite.m_RD.rect` | **giao nhánh dữ liệu** (§6) |

> ⚠️ **Không** cộng 1.554 + 132 + 67: 1.554 là *sprite*, 132 là *texture sheet*, 67 là *page atlas* —
> ba mẫu số khác nhau (xem `COVERAGE_AUDIT.md` §4, đúng loại lỗi "đếm hai tập rồi ghi một dòng").

---

## 3. Vì sao 1.554 chưa phân loại

Pipeline phân loại theo **tên** (`blt_` → bullet, `BG*` → background, …). Tên không khớp mẫu nào thì
rơi vào `unclassified`. Đo lại:

- **396** trong 1.554 có cột `atlas` (đến từ **269** tên sheet); chỉ **16** tên sheet trong đó trùng với
  1 trong 132 sheet *có texture thật* ⇒ phần lớn chỉ là dấu vết sheet lúc build.
- **1.158** là ảnh **rời** (không thuộc sheet nào).
- Tên: **878** CamelCase · **626** tên số/ngắn · **48** tên thuần số.

---

## 4. Đã phân loại lại: **1.049/1.554 có nhãn**, còn **505 `unknown`**

Bộ phân loại `tools/classify-assets.py` (chạy lại được, xuất `docs/assets/sprites-classified.csv`)
gán nhãn **chỉ khi có bằng chứng**. Bốn mức:

| mức | nghĩa | số sprite (trong 1.554) |
|---|---|---:|
| **A** | tên tự mô tả **hoặc** đã xem contact sheet xác nhận | **863** |
| **B** | suy từ tên **nhóm** (nhiều sprite cùng họ, cùng ngữ nghĩa) | **116** |
| **C** | suy từ tên tương tự — **phải xem ảnh mới chắc** | **70** |
| **chưa gán** | không có bằng chứng nào | **505** |
| **cộng** | | **1.554** |

Nhãn đề xuất cho 1.554 sprite chưa phân loại:

| nhãn đề xuất | thêm | vì sao (mã luật trong CSV) |
|---|---:|---|
| `ui` | **563** | `Khung*` khung · `Rank1…10` huy hiệu · `PVP1…10` huy hiệu PVP · `A1…A24` avatar · `Coin_*` xu · logo IAP · `Nut*` nút · `Overdrive_Timer`/`_Hp_Timer` · `Shop_*` · `Border*` viền (14) · `Boss…Gray` chân dung boss khoá · `Bong_Den`/`Botro` · nút/khung ảnh 07–08 |
| `bullet` | **168** | `blt_*` **148** + họ số (`2011–2015`, `4011–4015`) **10** + 10 tile đạn (ảnh 07 #33–36/#43/#55, ảnh 08 #11/#17/#18/#24) |
| `bosses` | **87** | `boss_*` (19+13+12) · `miniboss*` · `sieuhopthe*` · `boss_dong_ho_real_*` · **`Boss*` chân dung boss (21)** |
| `enemy` | **69** | `CB-*`/`CD-*` trùng mã prefab · `E_*` · `DA-2xxxx` (C) · **17** tile nguyên con enemy (ảnh 07–08) |
| `parts` | **65** | **nhãn MỚI** — bộ phận rời (§4.3): cánh/khiên/vỏ/thân · `Body*` · `Bone*` |
| `items` | **39** | `Manh*` · `Rock`/`Head`/`Foot` · túi/rương/banana/gem (ảnh 07–08) |
| `fx` | **24** | quầng sáng `Circle_*` · `Gate*`/`Light` · `Bomb`/`Boom` nổ · hố đen (ảnh 08 #61) |
| `background` | **19** | `Nen*` · `Earth`/`Mars`/`Moon`/`Jupiter` · `Cloud_3` |
| `font` | **11** | `Coda_*` (chữ logo) · `GooTest_*` (chữ Google Play) |
| `ships` | **2** | `mini_ship`/`mini_ship_1` |
| `drones` | **2** | `drone_may_bay_cam` · `7.2` (ảnh 08 #14) |
| **cộng** | **1.049** | |

**Cảnh báo về chất lượng nhãn (đừng đọc "1.049" là "1.049 đúng"):** xem ảnh 03 cho thấy tên **không**
luôn mô tả nội dung — `Ghost` là **một con tàu**, `Enegry` là **lon nước tăng lực**, `Hand` là **cánh
tay robot**; ảnh 07 cho thấy `heart` (#7) thực ra là **bông tuyết**. Vì vậy luật
`Ghost`/`Light`/`Gate`/`Manh`/`DA-` chỉ ở mức **C**, và **mọi nhãn đều ghi rõ luật** trong cột `rule`
của CSV để người dùng kiểm lại từng cái.

### 4.1 Còn lại **505 `unknown`** — chia ba nhóm, mỗi nhóm một cách đóng

| nhóm | số | cách đóng |
|---|---:|---|
| `numeric` — tên là **số**: `1`, `7day`, `208.0` | **33** | xem contact sheet |
| `word` — tên là **từ đơn**: `About`, `Add`, `Bag1`, `Be`… | **204** | phần lớn là **khung/viền/nút UI** + icon — xem ảnh |
| `other` — có số + chữ: `10010Radar`, `Arow1`, `Beemap_0`, `BH1`, `Trap3`, `asteroid` | **268** | xem ảnh |

**448 họ tên** trong 505 unknown, trong đó **410** là **tên đơn lẻ** (không có `_n` đi kèm) ⇒ không
gom nhóm được, buộc phải xem từng tile. Mỗi dòng CSV có cột **`needs_eye` = `unclassified-NN.jpg#k`**.

### 4.2 Trạng thái xem ảnh — nói thẳng

| | |
|---|---:|
| contact sheet đã **xem bằng mắt** | **4/25** (`unclassified-01`, `-03`, `-07`, `-08`) |
| sprite trong 4 sheet đó | 256 |
| sheet còn lại **chưa xem** | **21** |
| trong số đó còn `unknown` | **17** |

8 sheet đã **hết** `unknown`: `-02`, `-03`, `-05`, `-07`, `-08`, `-09`, `-21`, `-22`. Riêng `-09` hết
**nhờ luật tên** (`Body*` · `Bone*` · `Bomb`/`Boom` · `Border*` · `Boss…Gray` · `Botro`), không tốn một
lần xem ảnh nào — nghĩa là **đọc tên trước, xem ảnh sau** vẫn là cách rẻ nhất.

Nhiều sheet còn unknown nhất: `-15` **46**, `-11`/`-18` **44**, `-06`/`-19`/`-24` **42**, `-12` **41**.

> **Vì sao không "xem 25 ảnh rồi xong" trong một lượt:** mỗi ảnh là 64 tile; gán nhãn bằng mắt cần
> đối chiếu *tên ↔ tile* (CSV có sẵn), nhưng một tile sai sẽ kéo theo nhãn sai trong cả một họ. Cách
> đang làm: **luật trước (được 1.049), mắt sau (từng sheet)** — mỗi vòng 2–5 sheet.

### 4.3 Phát hiện quan trọng: bản gốc **tháo rời tàu/enemy thành bộ phận**

Ảnh 07–08 (128 tile) cho thấy phần lớn "ảnh chưa phân loại" **không phải sprite hoàn chỉnh** mà là **bộ
phận**: cánh, khiên chữ V, vỏ giáp, khung thân, đầu máy bay, mũi khoan, khối năng lượng — tên chỉ là
số (`1.1`, `2.2d`, `211_0`, `212_3`, `Body3`) đúng như kiểu tên khi một prefab bị **explode** ra. Trong
danh sách có sẵn họ tên `sieuhopthe_tachbophan` = **"siêu hợp thể tách bộ phận"** xác nhận cách đặt tên này.

⇒ Hệ quả cho người dựng lại:

1. **Đừng** kỳ vọng tìm được "sprite hoàn chỉnh cho từng enemy/tàu" — bản gốc **ghép từ mảnh**.
2. Nếu muốn dùng lại: hoặc giữ mô hình ghép mảnh (`parts` + transform), hoặc **render lại** thành
   sprite hoàn chỉnh một lần rồi vứt phần rời.
3. Đây cũng là lý do **không thể** phân loại `parts` bằng tên: tên mảnh không nói mảnh thuộc tàu nào.

---

## 5. Việc cắt sheet — danh sách ngắn, làm được ngay

**17 sheet có ≥ 8 sprite** (tổng **184** sprite) — đây là chỗ cắt "thật". Trong đó **10** sheet nằm ở
nhóm `unclassified` (**113** sprite), 7 sheet còn lại đã có nhãn (`Bg1`/`Bg3`/`Bg4`/`Bg6`/`Bg7` nền,
`AppleInAppPurchase1lnWhite`/`GooglePlayWordmarkWhite` bản trắng):

| sheet | sprite | | sheet | sprite |
|---|---:|---|---|---:|
| `AppleInAppPurchase1ln` · `PVP10` | 15 + 15 | | `PVP7` · `Bg7` | 10 + 10 |
| `AppleInAppPurchase1lnWhite` | 15 | | `Bg4` | 9 |
| `PVP8` · `PVP9` | 13 + 13 | | `PVP4` · `PVP5` · `Coin` · `Bg1` · `Bg3` · `Bg6` | 8 each |
| `GooglePlayWordmarkWhite` | 13 | | `GooglePlayWordmark` | 11 |
| `PVP6` | 12 | | | |

**252/269** tên sheet chỉ có **1** sprite ⇒ không phải sheet thật, chỉ là dấu vết build — đừng cắt.

**2 sheet có lưới khai báo ngay trong tên** (kiểm được bằng phép nhân):

| sheet | lưới | ô kỳ vọng | ô đã tách |
|---|---|---:|---:|
| `1_5x2` | 5 × 2 | **10** | **0** |
| `k_1__2x3` | 2 × 3 | **6** | **0** |

⇒ **0/16** ô. Đây là hai việc cắt **chắc chắn đúng** (không cần đoán), làm trước.

---

## 6. Việc phải giao nhánh dữ liệu (không tự làm được)

**67 page `sactx-*`** (31,05 MB, chứa phần lớn 2.184 sprite runtime) **không cắt được** vì thiếu
**rect**: cần export `Sprite.m_RD.rect` + `m_RD.textureRect`/`settingsRaw` cho 2.185 `Sprite`.

- Nếu có rect ⇒ cắt đúng 2.185 sprite từ 67 page (thay vì đoán theo tên).
- Đồng thời trả lời luôn "**sprite nào thuộc page nào**" — thứ mà cột `atlas` hiện **không** nói được.

Đã ghi thành task **T9** trong `HANDOFF_ANIM_RAW.md` (cùng cơ chế `git show <sha>:<path>` + `verdict.json`).

---

## 7. Kết luận cho người dựng lại

- **Không cần** chờ phân loại hết 2.197 ảnh mới bắt đầu: 1.903 sprite đã có PNG riêng; **1.049** sprite nay
  đã có nhãn đề xuất (kèm mã luật để kiểm), **505** còn lại có toạ độ tile để xem.
- **Cần** cho việc dựng art mới: 13 nhóm đã phân loại (**643** asset: 132+109+80+73+69+67+32+31+25+13+8+4)
  là đủ để lấy tỉ lệ kích thước/phong cách; **không** cần cắt hết sheet.
- **Việc rẻ nhất, làm ngay:** cắt `1_5x2` + `k_1__2x3` (**16 ô**, lưới khai báo trong tên, không phải
  đoán) và dùng `sprites-classified.csv` thay cho `sprites-index.csv` khi cần tra nhãn.
- **Việc còn lại là "xem ảnh"**, không phải "đọc thêm raw": **21** contact sheet chưa xem hết, **505**
  tile (nhiều nhất `unclassified-15` **46**, rồi `-11`/`-18` **44**, `-06`/`-19`/`-24` **42**). Trừ khi có **rect** (T9)
  thì mới đóng được bằng máy.

## 8. Tự kiểm

```bash
python3 tools/classify-assets.py             # sinh lại sprites-classified.csv
python3 tools/verify-claims.py --only AB     # 5 claim của tài liệu này
python3 tools/verify-claims.py               # toàn bộ
```

| claim | nội dung |
|---|---|
| **AB1** | 2.197 asset · 1.554 `unclassified` · 132 sheet · 16 sheet có sprite · **116** chưa tách |
| **AB2** | 1.554 = **396** trong sheet + **1.158** rời |
| **AB3** | 17 sheet ≥ 8 sprite = **184** sprite (10 sheet / **113** sprite thuộc `unclassified`) · 2 sheet lưới = **16** ô, **0** ô đã tách |
| **AB4** | phân loại lại: **1.049** có nhãn (**863 A · 116 B · 70 C**) · **505** `unknown` (**33** numeric · **204** word · **268** other) |
| **AB5** | 505 unknown = **448** họ tên, **410** tên đơn lẻ; **17/25** contact sheet còn tile chưa gán |
