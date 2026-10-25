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

## 4. Gợi ý nhãn cho 1.158 ảnh rời (theo **tên**, có đếm)

| luật | số sprite | gợi ý nhãn | mức |
|---|---:|---|---|
| `blt_*` | **133** | `bullet` (nhóm `bullet` đã có 67, cùng tiền tố) | **A** cho tiền tố, **B** cho việc gộp |
| `Hotro*` · `Vip*` · `Goigem*` · `Khung*` | **107** | `ui` (khung kỹ năng / huy hiệu VIP / gói gem) | **B** |
| `Rank*` | **94** | `ui` (huy hiệu rank) | **B** |
| `Boss*` · `boss_*` | **78** | `bosses` (đang có 32) | **B** |
| `CB*` · `cd*` · `E_*` | **58** | `enemy` (trùng tiền tố prefab `CB-30xxx` / `CD-31xxx`) | **B** |
| `ManhPlane*` · `XVideo*` · `Rock*` · `Head*` · `Foot*` | **48** | bộ phận / mảnh (cần xem) | **C** |
| **còn lại** | **640** | **chưa suy được từ tên** — phải xem contact sheet | — |

Với 640 còn lại, tín hiệu duy nhất đang có là **dung lượng**: **13** ảnh ≥ 100 KB (nghi background:
`Lv69` 462 KB · `SplashFree` 403 KB · `DF5_512x512` 378 KB · `Hotgirl2` 349 KB · `AvatarP9` 241 KB ·
`Map_ong` 234 KB …) và **69** ảnh ≤ 2 KB (nghi icon). Không đủ để gán nhãn — cần **xem 25 contact
sheet** `unclassified-01…25.jpg` (có ở nhánh dữ liệu, `docs/assets/contact-sheets/`).

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

- **Không cần** chờ đủ 2.197 ảnh mới bắt đầu: 1.903 sprite đã có PNG riêng, **1.554** trong đó chưa có
  nhãn nhưng **vẫn dùng được** nếu biết tên (contact sheet + `tile`).
- **Cần** cho việc dựng art mới: 13 nhóm đã phân loại (**643** asset: 132+109+80+73+69+67+32+31+25+13+8+4)
  là đủ để lấy tỉ lệ kích thước/phong cách; **không** cần cắt hết sheet.
- **Nên** làm ngay 2 việc rẻ: cắt `1_5x2` + `k_1__2x3` (16 ô), và áp 6 luật tên ở §4 (**518** sprite có nhãn
  mới) — đưa `unclassified` từ **1.554 → 1.036** mà không cần xem ảnh.

## 8. Tự kiểm

```bash
python3 tools/verify-claims.py --only AB      # 3 claim của tài liệu này
python3 tools/verify-claims.py               # toàn bộ
```

| claim | nội dung |
|---|---|
| **AB1** | 2.197 asset · 1.554 `unclassified` · 132 sheet · 16 sheet có sprite · **116** chưa tách |
| **AB2** | 1.554 = **396** trong sheet + **1.158** rời; luật tên phủ **518**, còn **640** chưa suy được |
| **AB3** | 17 sheet ≥ 8 sprite = **184** sprite (10 sheet / **113** sprite thuộc `unclassified`) · 2 sheet lưới = **16** ô, **0** ô đã tách |
