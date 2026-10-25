# ASSET_TRIAGE — bộ ảnh gốc còn **chưa phân loại** / **chưa tách** bao nhiêu?

> **Nguồn:** `docs/assets/sprites-index.csv` (import từ nhánh dữ liệu, commit `0a42eaa42`,
> blob **`d9e27f94a`**), `docs/assets/INDEX.md` (blob `72c9f12c3`), `docs/apk-analysis/04-asset-manifest.csv`.
> Mọi số dưới đây đọc lại được bằng `tools/verify-claims.py` (nhóm **AB**). Không dùng ảnh điện thoại.

**Trả lời ngắn: 2.197 asset · 1.554 chưa có nhãn · 132 sheet · 116 tên atlas không match · 67 page sactx.**
> ⚠ **116 KHÔNG phải "116 sheet chưa tách"** — đó là **số tên atlas không match theo tên** trong
> `sprites-index.csv`; nó **không** chứng minh texture đó chưa từng được cắt. Xem §2 (b) và review R3.
> **Cập nhật 25/10 (§9):** phân loại bằng số đo pixel ⇒ **1.857/2.197 có nhãn**, còn **340 `unresolved`**;
> lần đầu có **bảng tách sheet** (`sheet-splits.csv`: **307** entry · **4.250** mảnh · **98** texture page).
> Thêm: gợi ý kNN có **đo sai số** cho **89**/340 ca còn lại (§9.6) — không gộp vào nhãn.
> **Cập nhật 25/10 (report 62):** có **geometry thật** ⇒ **282**/340 ca nay biết **trang texture**, tự gán được **18** (§9.6b).
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


> **Chênh 56 vs 67 (ghi 25/10, review R3):** 67 là số texture `sactx-*` **theo tên** trong manifest;
> `sprites-index.csv` chỉ gắn `category=atlas` cho **56** trong số đó — **11 page bị luật tên xếp vào
> nhóm khác**. Đây là **lỗi nhãn**, không phải thay đổi dữ liệu; AB1 đếm theo **tên** nên vẫn 67.

## 2. Ba loại "chưa xong" — khác nhau

| loại | số | nghĩa | đóng bằng cách nào |
|---|---:|---|---|
| **(a) chưa đặt nhãn** | **1.554** sprite `unclassified` | có ảnh, không biết thuộc nhóm nào | luật tên + xem contact sheet (§4) |
| **(b) tách ảnh — CHƯA CHỨNG MINH** | **132** sheet `Texture2D`; **116** = `unmatched_atlas_name_count` = tên atlas **không match tên** trong index | ảnh gộp nhiều sprite (**giả thuyết**) | cần `Sprite.m_RD.textureRect` + `settingsRaw` + `rotation/trim` + manifest PNG (T9) |
| **(c) chưa có rect** | **67** page `sactx-*` (đếm theo **tên**; chỉ **56** trong số đó được gắn `category=atlas`) | atlas runtime; muốn cắt phải có `Sprite.m_RD.rect` | **giao nhánh dữ liệu** (§6) |

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
| **A** | tên tự mô tả **hoặc** đã xem contact sheet xác nhận | **848** |
| **B** | suy từ tên **nhóm** (nhiều sprite cùng họ, cùng ngữ nghĩa) | **131** |
| **C** | suy từ tên tương tự — **phải xem ảnh mới chắc** | **70** |
| **chưa gán** | không có bằng chứng nào | **505** |
| **cộng** | | **1.554** |

> **25/10 (review R4):** trước đây bảng này ghi **863 A / 116 B** và **643** nhãn lấy thẳng từ cột
> `category` bị **tự cấp A**. Nay 643 nhãn đó có `confidence` **rỗng** + `label_source=category_passthrough`
> — chúng **không** nằm trong 1.554 dòng này mà nằm ở nhóm sprite đã có `category` sẵn: đó là lý do
> `sprites-classified.csv` có **848 A · 131 B · 70 C** (chỉ tính phần phải phân loại) và **643** dòng
> passthrough riêng.

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
- **Việc rẻ nhất, làm ngay:** cắt thử `1_5x2` + `k_1__2x3` — **16 ô theo tên** (suffix `5x2` / `2x3`).
  ⚠ Tên chỉ là **gợi ý layout**: chưa biết `padding`, `margin`, `rotation`, `trim` và kích thước ảnh
  gốc thật, nên **16 ô chưa phải bằng chứng** là cắt đúng. Dùng `sprites-classified.csv` khi tra nhãn.
- **Việc còn lại là "xem ảnh"**, không phải "đọc thêm raw": **17/25** sheet `unclassified-*` còn
  ≥1 sprite **chưa có nhãn** (định nghĩa: "chưa xem hết" = còn `unresolved`, không phải "chưa mở ảnh").
  Trừ khi có **rect** (T9) thì mới đóng được bằng máy.

## 8. Tự kiểm

```bash
python3 tools/classify-assets.py             # sinh lại sprites-classified.csv
python3 tools/verify-claims.py --only AB     # 5 claim của tài liệu này
python3 tools/verify-claims.py               # toàn bộ
```

| claim | nội dung |
|---|---|
| **AB1** | 2.197 asset · 1.554 `unclassified` · 132 sheet · 16 sheet có sprite · **116** `unmatched_atlas_name_count` (**không** phải "chưa tách") |
| **AB2** | 1.554 = **396** trong sheet + **1.158** rời |
| **AB3** | 17 sheet ≥ 8 sprite = **184** sprite (10 sheet / **113** sprite thuộc `unclassified`) · 2 sheet lưới = **16** ô, **0** ô đã tách |
| **AB4** | phân loại lại: **1.049** có nhãn (**848 A · 131 B · 70 C**) · **643** passthrough **không có mức** · **505** `unknown` (**33** numeric · **204** word · **268** other) |
| **AB5** | 505 unknown = **448** họ tên, **410** tên đơn lẻ; **17/25** contact sheet còn tile chưa gán |

---

## 9. Vòng 2 (25/10) — phân loại bằng **số đo pixel** + bảng tách sheet

Vòng trước phân loại **bằng tên** (33 luật) được **1.692** sprite, còn **505** trống. Vòng này thêm
**số đo pixel** cho từng sprite nên gán thêm **165** ca (**81** theo tên + **84** theo số đo), còn **340**,
và lần đầu có **toạ độ cắt sheet**.


### 9.1 Đường đi của số

| | tên | làm gì |
|---|---|---|
| tool | `tools/art-study.py` | giải 42 contact sheet → mỗi ô: `ncomp` (số mảnh rời), `fill`, `sat`, `val`, `colors`, `dark_share`, `comps` (rect từng mảnh) |
| tool | `tools/classify-by-measure.py` | ghép 3 nguồn (index · manifest · art-study) → gán nhãn theo luật, xuất 2 bảng |
| vào | `sprites-classified.csv` (**1.692** nhãn vòng trước) · `04-asset-manifest.csv` (kích thước gốc) · `art-study.csv` | |
| ra | **`sprites-auto-classified.csv`** · **`sheet-splits.csv`** | |

### 9.2 Kết quả: **1.857/2.197 có nhãn**, còn **340**

| nhãn cuối | số | | nhãn cuối | số |
|---|---:|---|---|---:|
| `ui` | **715** | | `enemy` | 103 |
| `bullet` | **239** | | `audio` | 69 |
| `atlas` (texture page) | 132 | | `items` | 43 |
| `background` | 129 | | `ships` | 27 |
| `fx` | 126 | | `font` | **23** |
| `bosses` | 119 | | `drones` | 15 |
| `parts` | **117** | | **`unresolved`** | **340** |

Mức tin cậy: **A 929** (tên/id tự mô tả + 124 tile đã xem ảnh) · **B 215** (chỉ số đo/tên nhóm) ·
**C 70** (cần xem mắt) · **trống 643** = nhãn **passthrough** từ cột `category` · **— 340** (không luật nào khớp).

> ⚠ **643 nhãn đó KHÔNG phải mức A.** Bản trước gán `A` cho mọi row lấy từ cột `category` — đó là
> *chép nhãn cũ*, không phải *audit*. Từ 25/10 chúng có `confidence` rỗng + `label_source=category_passthrough`
> + `reviewed=false`. Muốn nâng lên A thì phải xem ảnh hoặc có luật (`review R4`).

### 9.3 Luật mới — và vì sao tin được

**Luật tên (A)** — dùng từ vựng đã có trong repo, không tự nghĩ. Cột `mới` là số ca **vòng này**
chiếm được; số 0 nghĩa là vòng trước **đã** phủ hết nhóm đó nên luật không có đất dùng:

| luật | nhãn | mới | dựa vào |
|---|---|---:|---|
| `^(Head|Gun|Wing|Body|Bone|Hand|Leg|Tail|Vai|Tay…)` | `parts` | **52** | `BOSSES.md` §5: boss **tháo rời thành bộ phận** |
| `^(Avatar|Btn|Board|Popup|Tab|Icon|Frame|Bg…)` | `ui` | **15** | tên chức năng UI |
| `^(Giam|Tang|Time|Sao|Star|Lock|Khoa|Hp)` | `ui` | 4 | nhãn/thanh UI (giảm·tăng·sao·khoá) |
| `^(Rank|PVP|Vip|Hotro)` | `ui` | 5 | huy hiệu/cấp/bảng |
| `^(CB|W1-|W2-|MB\d)` | `enemy` | 3 | id prefab enemy |
| `\d+Radar$` | `ui` | 2 | radar/minimap màn chọn |
| `^blt` · `^[Bb]oss.*Gray$` · `^boss_` · `^sieuhopthe` | `bullet` 148 · `ui` 15 · `bosses` 49 · `parts` 17 | 0 | vòng trước **đã** phủ (R01 · R26 · R03 · R04) |

**Luật số đo (B)** — chỉ dùng khi tên không nói gì. **84 ca** vòng này:

| luật | nhãn | số | ngưỡng |
|---|---|---:|---|
| lấp ≥60 % ô · ≤2 mảnh | `ui` | **30** | `fill ≥ 0,60` ⇒ nền nút/panel |
| ≥8 mảnh trong ≤256 px | `ui` | **27** | bộ icon ghép |
| gần vô sắc · sáng · thưa | `fx` | **22** | `sat ≤ 0,15`, `val ≥ 0,65`, `fill ≤ 0,25` |
| `dark_share` ≥0,30 · ≤3 mảnh | `bullet` | **4** | thân tối + viền sáng (đúng luật `ART_STUDY.md` §3.4) |
| ≥512 px · sáng ≤0,50 · bão hoà ≤0,45 | `background` | **1** | nền lớn, tối |

⇒ Cả vòng này chỉ thêm **165** nhãn (**81** theo tên + **84** theo số đo). Luật số đo **cố tình ít**: nó chỉ
nhận khi dấu hiệu trùng số đo trung vị của nhóm đó trong `ART_STUDY.md`, không đoán theo cảm giác.
Ca nào không khớp ⇒ để **`unresolved`**, không gán bừa.

### 9.4 Tách sheet — lần đầu có **toạ độ**

`sheet-splits.csv`: **307** sprite thật ra là **nhiều hình**, tổng **4.250 mảnh**, mỗi mảnh một rect
**theo pixel gốc** (đã nhân tỉ lệ từ ô 150 px lên `width/height` thật):

| nhóm | entry | mảnh |
|---|---:|---:|
| **texture page** (`category = atlas`) | **98** (trong đó **64** page `sactx`) | **1.387** |
| sprite thường nhưng nhiều mảnh | 209 | **2.863** |
| **cộng** | **307** | **4.250** |

Nhiều mảnh nhất: hai page `2048×2048` và `1024×1024` đều **47 mảnh**; `BGBox1` (256×256) **40 mảnh**.

`tools/classify-by-measure.py --crop DIR` cắt **thật** ra PNG trong suốt (nền caro → alpha 0, giữ outline đen),
mỗi mảnh một file + `crops.csv`. Chạy thử: **4.250** PNG · 3,44 Mpx · **11,8 s**. Nhưng đếm kích thước
mảnh thì lộ ra vấn đề: **792** mảnh ≥20×20 px, chỉ **158** mảnh ≥64×64 px ⇒ phần lớn "mảnh" là
**vụn glow/nhiễu JPEG**, không phải sprite. Vì vậy:

- **4.250 là CẬN TRÊN** của số hình (đã lọc ≥20 px nhưng 150 px/ô làm vụn dính nhau);
- con số dùng được là **792** mảnh "đủ to để là một hình" ⇒ 307 sheet chứa **~800–4.250** hình;
- ảnh cắt ra chỉ là **bản xem trước 150 px/ô** ⇒ **không** commit vào repo (nằm ngoài git, xem §9.7);
- **nền trong suốt chưa sạch 100 %**: lấy mẫu 200 mảnh ≥48×48 thì **113 (56 %)** còn **góc ô caro**
  chưa bị xoá. Nguyên nhân: flood fill chỉ ăn nền **nối với viền ô**, mà mảnh lớn hoặc page atlas thì
  vùng caro nằm **kín bên trong** — không nối ra viền được. Xem `docs/assets/sheet-splits-sample.png`
  (60 mảnh sạch nhất trong top 160) để thấy phần cắt **đúng** trông thế nào;
- cách sửa gốc: cắt từ **PNG có alpha** (không phải JPEG contact sheet), tức lại cần §9.7;
- muốn con số chính xác: cần `m_RD.rect` + PNG gốc — **nay đã có** (xem §9.9).

**Giới hạn phải nói rõ:** **4.250 không phải "số hình"** — nó là **số mảnh rời ≥20 px** đo trên ảnh
150 px/ô, và hai sai lệch chạy **ngược chiều nhau**:

| hiệu ứng | chiều | bằng chứng |
|---|---|---|
| hai sprite dính nhau ⇒ gộp 1 mảnh | **đếm thiếu** | sheet lưới 4×4 ô vuông đều bị gộp |
| glow/nhiễu JPEG tách thành nhiều mảnh | **đếm thừa** | chỉ **792** mảnh ≥20×20 px, **158** mảnh ≥64×64 px |

Vì hiệu ứng thứ hai áp đảo (4.250 → 792), con số dùng được để lập kế hoạch là **~790 mảnh "đủ to"**,
còn **4.250** là số **dòng CSV để cắt thử**, không phải số sprite. Ngoài ra rect sai số ~±2 px ở
kích thước gốc. Muốn cắt **chính xác** thì phải có `Sprite.m_RD.rect` — **nay đã có** (§9.9).

### 9.5 Còn **340** — chúng là gì

Số đo thật của 340 ca (p25 · p50 · p75):

| | p25 | **p50** | p75 |
|---|---:|---:|---:|
| `w`×`h` | 93×94 | **128×128** | 204×172 |
| `ncomp` | 3 | **4** | 5 |
| `fill` | 0,18 | **0,30** | 0,46 |
| `sat` | 0,38 | **0,58** | 0,75 |
| `val` | 0,50 | **0,61** | 0,73 |
| `dark` | 0,00 | **0,00** | 0,01 |

Đọc bảng này: chúng **không tối** (`dark` p75 = 0,01 ⇒ loại `bullet`), **không thưa-vô sắc**
(`sat` 0,58 ⇒ loại `fx`), **không đặc** (`fill` 0,30 ⇒ loại `ui`), và **≤5 mảnh** (⇒ loại bộ icon ghép).
Tức chúng là **một hình vừa phải, nhiều màu, ít mảnh** — đúng kiểu *icon/prefab* mà 13 nhóm hiện có
không có chỗ. Tên cũng vô nghĩa: `1011`, `11_0`, `128x128`.

- Phân bố: rải trên **sheet `unclassified-*.jpg`** (nhiều nhất `-15` 38 · `-24` 37 · `-06` 28).
- **282**/340 nay biết **trang texture thật** (report 62); trong đó chỉ **18** gán được bằng luật
  trang (§9.6b). Biết trang ≠ biết nhãn.
- Cách đóng: xem mắt 340 ô (đã nằm sẵn trên các sheet `unclassified-*`) rồi gán tay — **~2 giờ**;
  hoặc tách thành nhóm `misc` nếu L1 không cần.
- **Không** được coi `unresolved` là "đã xong": nó là **việc còn lại**, không phải nhãn.

### 9.6 340 ca còn lại — thử **hàng xóm gần nhất**, và đo sai số trước khi tin

Luật tay đã hết đất. Cách cuối không cần thêm dữ liệu: xếp 1.857 sprite **đã có nhãn** vào không
gian **10 số đo** (log w · log h · log màu · `fill` · `sat` · `val` · `dark` · log `ncomp` ·
log bytes · log tỉ lệ), chuẩn hoá z-score, lấy **3 hàng xóm gần nhất**, nhận khi **≥2/3 đồng ý**.

Điều quan trọng là **đo sai số trước, dùng sau** (leave-one-out: bỏ nhãn của chính nó rồi đoán lại):

| nhóm | recall | precision | n |
|---|---:|---:|---:|
| `audio` | **1,00** | **1,00** | 69 |
| `ui` | 0,95 | 0,85 | 337 |
| `bullet` | 0,94 | 0,89 | 107 |
| `fx` | 0,82 | **0,92** | 57 |
| `background` | 0,79 | 0,86 | 47 |
| `items` | 0,73 | 0,89 | 11 |
| `atlas` | 0,74 | 0,86 | 58 |
| `bosses` | 0,61 | 0,74 | 28 |
| `enemy` | 0,50 | 0,70 | 32 |
| **`parts`** | **0,24** | **0,50** | 21 |
| `font` | 0,75 | 1,00 | 4 |
| `drones` / `ships` | 1,00 | 0,50 | 1 · 1 |

**781**/1.857 ca đủ tự tin · đúng **674** (**86,3 %**) · nền đoán-bừa (nhóm lớn nhất) là 39 %.

Áp lên 340 ca: gợi ý được **89** (`ui` 72 · `bullet` 8 · `enemy` 4 · `bosses` 4 · `parts` 1),
**251** vẫn để trống. Ghi ra `docs/assets/sprites-knn.csv` (cột `category_knn`, `margin`,
`precision_measured`) — **không** gộp vào `category_auto`.

Đọc đúng: `ui`/`bullet`/`audio`/`fx` là **gợi ý dùng được** (precision 0,85–1,00); `parts` precision
0,50 là **tung đồng xu** ⇒ đừng dùng; `drones`/`ships` n=1, không nói được gì. Ba nhóm cuối này
phải xem mắt, không có đường tắt.

**Đường cụt đã thử và loại:** dùng **tên atlas page** làm nhãn (sprite cùng page ⇒ cùng loại). Chỉ
**59**/340 ca có atlas, và **0** ca đạt đa số ≥60 % trong page — page `11`, `128x128`, `256` là
**page đánh số**, không mang ngữ nghĩa. Không thử lại **với cột `atlas` đó** — xem §9.6b: cột này lấy
từ tên sheet trong index, **không phải** trang texture thật.

### 9.6b Sửa lại sau report 62: **geometry cho biết trang thật**, gán được **18**

Report 62 giải `m_RD.m_Texture` cho **2.185** sprite ⇒ biết **trang texture thật** của từng sprite
(`reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz`), khác hẳn cột `atlas` của index.
Trang thật có tên **có nghĩa**: `sactx-…-Bullets-…`, `…-UI_Home-…`, `…-Boss6-…`.

Cách dùng — **đo trước, dùng sau** (`tools/classify-by-atlas.py`): gom sprite đã có nhãn A/B theo **họ
trang**, chỉ tin họ nào `n ≥ 10` **và** precision `≥ 0,95`, rồi mới áp lên 340 ca `unresolved`.

| | số |
|---|---:|
| `unresolved` có trang thật | **282**/340 (58 ca không có geometry) |
| họ trang đủ chuẩn (n≥10 · precision≥0,95) | **13** |
| ca tự gán được từ trang | **18** (`ui` 13 · `bullet` 3 · `parts` 2) |

Họ mạnh nhất: `Bullets` → `bullet` (prec 0,978 · n=136) · `ARENA`/`VIP`/`UIEvent`/`PVP*` → `ui`
(1,00) · `Boss6` → `parts` (1,00). Họ **không** đủ chuẩn (chỉ là gợi ý): `UI_Home` 0,56 ·
`QueenBee` 0,55 · `Boss39014` 0,36 — đúng như trực giác: page gộp nhiều thứ.

Đọc đúng: **18 ca là con số thật**, không phải "282 ⇒ gán được 282". 282 chỉ nói **biết nơi ở**;
282 − 18 = 264 ca vẫn phải xem mắt vì họ trang của chúng trộn nhãn. Ghi ra
`docs/assets/sprites-atlas-page.csv` (2.197 dòng, cột `texture_page` · `page_family` · `suggested_category`
· `precision` · `n_labeled` · `applied`) — **không** gộp vào `category_auto`.

| **trang atlas** | 2.197 asset · **340** `unresolved` · **282** có trang thật · **18** tự gán được · **13** họ trang đủ chuẩn |

> **Ranh giới bằng chứng:** geometry ở đây là **join metadata** (`PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`),
> không phải ảnh crop đã kiểm. Tên trang là bằng chứng **phân loại**, không phải bằng chứng **render**.


### 9.8 Luật bị che + provenance nhãn (sửa theo review R4)

Review `25c367aca` chỉ ra hai luật **không bao giờ thắng** vì bị luật đứng trước bắt hết:

| case | trước | sau | vì sao |
|---|---|---|---|
| `Coda_0..3` | `ui` (R14 `^(Coin\|Goigem\|Coda_)`) | **`font`** (R22) | `Coda` là **tên họ font**; R14 chỉ nên giữ `Coin`/`Goigem` |
| `XVideo_0..8` | `ui` (R18, đúng) | `ui` (R18) | `XVideo` **bị R18 bắt trước** R23 ⇒ nhánh `items` cho XVideo là **chết**, đã bỏ khỏi R23 |
| `CodaWhite*` | `fx` (giữ nhãn gốc) | `fx` (passthrough) | nằm ở cột `category` từ trước, **không** phải kết quả R22 |

Cách kiểm tự động: `tools/classify-assets.py` chạy `shadowed_rules()` — luật nào **có tên khớp nhưng
0 tên thắng** thì in cảnh báo. Hiện tại **0 luật bị che**.

Cột provenance — `sprites-classified.csv` (đầu vào, 4 cột) và `sprites-auto-classified.csv` (đầu ra,
2 cột mà nó **tự** ghi):

| cột | có ở | nghĩa |
|---|---|---|
| `label_source` | cả hai | `rule` 925 · `eye` 124 · `category_passthrough` 643 · `unknown` 505 (đầu vào); `rule:name` 81 · `rule:measure` 84 · `none` 340 (đầu ra) |
| `rule_id` | đầu vào | `R14`, `R22`… để truy ngược |
| `evidence_ref` | đầu vào | luật / ảnh contact sheet / cột `category` |
| `reviewed` | cả hai | `true` chỉ khi có luật A/B hoặc đã xem ảnh; **643 passthrough là `false`** |

Cột `rule` của đầu ra ghi **nguyên văn** luật đã bắn (kể cả `(giữ nhãn gốc)`), nên truy được từng nhãn
mà không cần `rule_id`; `rule_id` chỉ tồn tại ở bảng của vòng đặt tên.

⇒ Số đọc đúng: **1.049** nhãn do luật/ảnh (848 A · 131 B · 70 C) + **643** nhãn chép lại (không mức)
+ **505** unknown. Không cộng 643 vào "A".
### 9.9 **Đã có toạ độ thật** (report 62) — cắt được chính xác, không cần đoán từ ảnh 150 px

`reverse-engineering/raw/sprite-geometry/resolved-geometry.json.gz` (268 KB, commit trong repo):
**2.185** `Sprite` · **654** `Texture2D` · **66** `SpriteAtlas`; resolve **2.185/2.185**, `unresolved` = **[]**
(claim **GE1**).

| Đường resolve | số sprite |
|---|---:|
| `sprite_render_data` (trực tiếp) | **635** |
| `atlas_pointer_and_render_key` (qua atlas) | **1.550** |

Và các con số quyết định **cách cắt**:

| | số | hệ quả |
|---|---:|---|
| `packed` (nằm trong atlas) | **1.550** | phải cắt trong page, không phải ảnh rời |
| mã xoay/lật `0` | **2.041** | cắt thẳng |
| mã xoay/lật `1 · 2 · 3` | **53 · 54 · 37** = **144** | **144 sprite phải lật/xoay** sau khi cắt — cắt thẳng là **sai** |
| `rect_outside` (rect vượt texture) | **40** | vượt **0,0000019 – 0,9963 px** ⇒ phải **clamp**, không coi là lỗi dữ liệu |
| `sources` (hash file nguồn) | **6** | 6 chunk nguồn **chưa kéo** ⇒ chưa tự kiểm `sha256` |

> **Trạng thái trong file:** `PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION` ⇒ đây là **join
> metadata đúng**, **chưa** phải bằng chứng "đã crop ra 2.185 ảnh đúng". Muốn thành bằng chứng phải crop
> thật rồi so pixel với atlas gốc.
>
> ⇒ **Việc phải làm khi cắt:** (1) đọc `source_rect`; (2) **áp mã xoay** cho 144 sprite; (3) **clamp** 40 rect;
> (4) crop từ **PNG/alpha gốc** chứ không từ contact sheet JPEG. Khi đó `sheet-splits.csv` (4.250 mảnh ước
> lượng) chỉ còn là **bản cũ để đối chiếu**, không phải nguồn.

### 9.7 Việc giao nhánh dữ liệu

~~Export `Sprite.m_RD.rect` (x,y,w,h) + `settingsRaw` cho **2.185** sprite và **67** page `sactx`.~~ **ĐÃ CÓ** (§9.9). Còn xin: 6 chunk nguồn + validate crop. Đổi lại:
(a) cắt sheet **chính xác** thay vì scale từ 150 px; (b) mở luôn 67 page đang thiếu rect; (c) `9-slice`
border (`ASSETS.md` §5) lấy được **số thật** thay vì đề xuất 8/12/16 px.
