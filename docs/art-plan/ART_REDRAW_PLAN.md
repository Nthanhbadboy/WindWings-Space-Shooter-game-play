# ART_REDRAW_PLAN — kế hoạch vẽ lại asset cho game mới (thuần kế hoạch)

> **Bàn giao: 1 report + 1 bảng planner. Không vẽ sprite nào, không sửa spec, không đụng runtime.**
>
> Nguồn đọc: nhánh `arena/20330d0e-windwings-space-shooter-game-p` — fetch refspec tường minh
> (`git fetch origin refs/heads/arena/20330d0e-…:refs/remotes/origin/arena/20330d0e-…`), tip **`12ccdc5`**.
> Đọc: `docs/spec/{ART_STUDY,ASSETS,ASSET_TRIAGE,VISUAL_DESIGN,START_HERE,MISSING_FOR_NEW_GAME,GAMEPLAY}.md`,
> `tools/{art-worklist,art-study}.py`, `docs/apk-analysis/04-asset-manifest.csv`,
> `docs/assets/{art-worklist,art-study,sprites-index,sprites-auto-classified,sprites-classified,sheet-splits}.csv`,
> và 3 contact sheet (`ships-01`, `ui-01`, `fx-01`).
>
> **Không sửa** file nào dưới `docs/spec/`, `datas/`, `tools/`, `tests/`, `reverse-engineering/`.
> **Không** chạy engine/runtime. **Không** dùng PNG/atlas/Spine/audio gốc làm asset (`ASSETS.md` §8).
> Ngày **2026-10-27**. Nhãn bằng chứng theo `DONE.md`: **(A)** = đếm/đo lại được từ file, **(C)** = ước lượng.
> **Bản v2 (cùng ngày):** đã **đo lại `reuse`** trên 1.901 sprite (I×U mặt nạ 32×32) — xem §3.6. Mọi con số
> lập kế hoạch dùng **cột v2** (`h_scope_v2` / `l2_h_v2`): scope B **1.610 h**, L2 **177 h**, full **4.388 h**.
> Số v1 vẫn để nguyên trong các bảng §2.2 / §3.3 / §5.2 để đối chiếu — **không** dùng để lập lịch.

---

## 0. TL;DR

| Câu hỏi | Trả lời ngắn |
|---|---|
| Vẽ lại bao nhiêu? | **2.185** bản ghi `Sprite` (A) ⇒ sau dedup **788 đơn vị vẽ** = **624 nhóm** worklist + **164 tên glyph** (A) |
| Nhóm thế nào? | **22 batch / 8 lane**: PLAYER 48 đơn vị · ENEMY 34 · BOSS 42 · UI 307 · FX 26 · BG 44 · ITEM 9 · EXCL 278 (A) |
| Khối lượng? | **L2 = 177 h** (prorate theo bản ghi) — **lập lịch bằng 206 h** (`l2_h_v3`, dòng `v2′` §5.2) · **L3 khuyến nghị = 1.610 h** (801 bản ghi) · **full parity = 4.388 h** (C, ±25 %) — **dùng bộ số v2 đã đo lại `reuse` (§3.6)**, không dùng bộ v1 149 / 1.264 / 3.916 |
| Chuẩn art? | 9 **công thức tô** đã kiểm bằng số (val · val_std · dark · chroma) + palette Ink & Ember đo HSV (A) |
| Thứ tự? | **S0 → W1 (L2) → W2 → W3 → W4 → W5**, mỗi cổng wave là một phép đo, không phải cảm nhận |
| File còn lại | [`art-planner.csv`](art-planner.csv) — **655 dòng** (629 đơn vị + 22 overhead + **4 dòng W0 listing**), **36 cột** (gồm `h_scope_v2` · `l2_h_v2` · `l2_h_v3` · `de_est` · `reuse_est` · `h_w0`), khớp từng nhóm worklist |
| Đơn hàng đã bung | [`W1_WORK_ORDER.md`](W1_WORK_ORDER.md) — **48 unit PLAYER**, 13 unit ở W1 = **34,0 h** (§6: W1 = **206,4 h**) · [`W0_LISTING_ASSETS.md`](W0_LISTING_ASSETS.md) — **27 slot** listing 3 store = **35 h**, sổ riêng |

**Một câu chốt:** kho hiện có **không phải** 2.197 sprite phải vẽ — nó là **2.185 bản ghi**, trong đó
**788 đơn vị vẽ thật**, và chỉ **801 bản ghi (37 %) là cần vẽ cho bản L3 khuyến nghị**; **1.451 h (37 %)**
của "full parity" nằm ở 3 lô mà kế hoạch này **gần như không vẽ** (brand 90 · parts 127 · triage 411 — chỉ giữ 12 mảnh parts).
Và sau khi đo lại (§3.6): trong 801 bản ghi đó **gần như không có bản ghi nào là "frame miễn phí"** — 17/18 nhóm
từng bị coi là "biến thể" hoá ra là **thiết kế riêng**, nên giá thật cao hơn bảng v1 **+346 h (28 %)**.

---

## 1. Đầu vào & đối soát — trước khi lập kế hoạch, phải khớp 4 con số

### 1.1 Bốn tập dữ liệu, bốn mẫu số khác nhau

| Tập | Dòng | Nội dung | Dùng cho |
|---|---:|---|---|
| `04-asset-manifest.csv` | **2.907** (A) | **2.185 `Sprite`** + 653 `Texture2D` + 69 `AudioClip`, có **`width`/`height`** | **đơn vị công việc** của plan này |
| `sprites-index.csv` | **2.197** (A) | 1.903 `Sprite` + **224 `Texture2D`** + 69 `AudioClip` + 1 `Font`; có `contact_sheet`/`tile` | tra ảnh, nối contact sheet |
| `sprites-auto-classified.csv` | 2.197 (A) | nhãn + provenance (`rule`/`confidence`/`label_source`) | **nhãn** dùng trong planner |
| `art-study.csv` | **2.112** (A) | mỗi tile 12 số đo trên contact sheet | **chuẩn art** (§4) |
| `art-worklist.csv` | **624** nhóm / 1.893 bản ghi (A) | base-name sau dedup + `variants` + `max_w/h` | khung phân rã batch |

**Đối soát kiểm được (A):** `1.890` sprite index + `221` Texture2D + `1` Font = **2.112** ô đã đo
⇒ 13 sprite index không đo được (ô trống/không có tile), 3 Texture2D không đo, 69 audio không có sheet.
Và `1.893` (worklist) + `292` (glyph) = **2.185** ✔.

> ⚠ **Ba số 2.197 / 2.185 / 2.112 không thay thế nhau.** 2.197 = *dòng index* (gồm 224 texture page
> + 69 audio); 2.185 = *sprite thật*; 2.112 = *ô đã đo*. Kế hoạch vẽ dùng **2.185**.

### 1.2 Nối worklist ↔ index: 42/624 tên lệch dấu cách (A)

`art-worklist.csv` ghi `base_name` bằng **dấu cách** (`banana`, `boss nhen doc xanh`), còn khoá tự nhiên
trong index là **gạch dưới**. Chuẩn hoá `' ' → '_'` thì khớp **624/624**; không chuẩn hoá thì **42 nhóm
lệch** (6,7 %) và 42 nhóm đó sẽ bị tính **hai lần** hoặc **bỏ sót** tuỳ chiều join. Đây là lỗi im lặng —
planner đã chuẩn hoá.

### 1.3 Bucket glyph: 292 bản ghi / **164 tên** — và 46 tên **không phải** glyph (A)

`tools/art-worklist.py` tách "glyph" theo luật *tên ≤ 2 ký tự **hoặc** toàn số* và **không** đưa vào 624.
Đo lại toàn bộ 292 bản ghi đó:

| Nhóm glyph | Tên | Bản ghi | Là gì |
|---|---:|---:|---|
| số `10001…10999` | 25 | 25 | **25 tàu** (category `ships`) |
| số `20001…20013` | 13 | 14 | **13 drone** |
| số `7001…9018` | 32 | 32 | **32 boss** (dải 7001–7018 thiếu 7007/7008 · 9002–9018 thiếu 9001/9016) |
| số khác (1…21, 207, 256, `1011–5015` ×5 bộ) | 48 | 164 | **không phải nhân vật** — tên `1,2,3…` bị lặp tới 19 bản ghi/tên |
| tên ngắn (`A, B, S, XS, On, ad, x, w1, k5, cá…`) | 46 | 57 | chủ yếu icon/nút/trang trí — **cũng ngoài 624** |

⇒ **Xác nhận** con số của spec: 118 tên số = 25 tàu + 32 boss + 13 drone + 48 khác (không phải 34 boss).
⇒ **Bổ sung** điều spec chưa ghi: **46 tên ngắn / 57 bản ghi** cũng nằm ngoài worklist ⇒ nếu ai vẽ đúng
624 dòng worklist thì **thiếu 292 bản ghi**, trong đó **70 sprite nhân vật chính** (25 tàu + 13 drone + 32 boss).

### 1.4 Nhãn: 624 nhóm chia 4 mức bằng chứng (A)

| Mức | Luật | Nhóm |
|---|---|---:|
| **G1** | ≥50 % bản ghi trong nhóm có `category` gốc đã xác nhận | **103** |
| **G2** | nhãn rule/eye với confidence A–B, không có C | **319** |
| **G3** | có ít nhất 1 nhãn confidence **C** (phải xem ảnh) | **18** |
| **G0** | không có bằng chứng (`unresolved`) | **184** |

Theo bản ghi (2.185): `ui` 766 · `unresolved` **370** · `bullet` 231 · `parts` 184 · `enemy` 151 ·
`background` 122 · `fx` 121 · `bosses` 119 · `items` 59 · `ships` 27 · `drones` 16 · `font` 15 · `unclassified` 4 (A).

**340 `unresolved` rơi vào 17/25 sheet** (A): `-15` 38 · `-24` 37 · `-06` 28 · `-19` 27 · `-01` 26 ·
`-23` 25 · `-18` 23 · `-14` 22 · `-10` 19 · `-12` 16 · `-25` 15 · `-17` 13 · `-20` 13 · `-13` 12 ·
`-16` 11 · `-11` 10 · `-04` 5. 8 sheet đã hết unknown ⇒ **triage = 17 sheet × ~20 mục**, một sprint 3 ngày.

### 1.5 Phát hiện khi mở contact sheet: lane `fx` bị nhiễm brand (A)

`fx-01.jpg` (80 ô) mở ra: **53/80 ô là chữ cái của logo thương hiệu** — `AppleInAppPurchase1lnWhite`
(16) · `GooTestWhite` (14, chữ Google Play) · `StripeWhite` (6) · `ApplePayWhite` (5) · `GooglePayWhite` (5) ·
`CodaWhite` (5) · `GooglePlayWordmarkWhite` (1) · `WebshopWhite` (1). **FX thật ≈ 27 ô**
(`Explosion`, `FireNew`, `CrossFire`, `Saw`, `Glow`, `Smoke`, `railgun_spark`…).

⇒ Nếu ai dựa vào cột `category=fx` để lập danh sách FX thì **2/3 danh sách là asset pháp lý không dùng được**.
Planner vì thế tách hẳn batch **`X-BRAND` (90 bản ghi)** và **không** tính giờ vẽ lại (chỉ 10 h chuẩn hoá + nhận brand kit).

`ui-01.jpg` (64 ô) cho thấy đúng thứ mà `ART_STUDY` đo: **vòng/gear/khung dày, nút chữ nhật, avatar, icon
xu/gem, logo IAP** — tức UI gốc **trộn** widget với brand. `ships-01.jpg`: 25 tàu **liền khối**, buồng lái
phát sáng, bão hoà cao, **không** có mảng "bộ phận rời" — xác nhận `ASSET_TRIAGE` §4.3 (tàu/enemy bị
*explode* thành `parts` nằm ở nhóm khác, không nằm trong sheet tàu).

---

## 2. Nhóm asset theo **gameplay-priority**

### 2.1 Định nghĩa 4 mức ưu tiên (dùng cho mọi bảng sau)

| Mức | Luật | Hệ quả |
|---|---|---|
| **P0** | xuất hiện trong **3 giây đầu** của một màn: tàu, đạn, enemy, thanh HP/số đếm | chặn L2 — không có thì không chơi được |
| **P1** | xuất hiện **trong 1 màn**: boss, nổ, lớp nền, item rơi | chặn L3 "giống trải nghiệm" |
| **P2** | chỉ xuất hiện **ngoài màn** (meta): shop, rank, icon, kit UI | chặn monetize/retention, **không** chặn gameplay |
| **P3** | **ngoài scope hoặc chờ dữ liệu**: brand (pháp lý), parts (mô hình lắp ghép), triage (chưa có nhãn) | **không vẽ** ở kế hoạch này |

### 2.2 Bảng batch (nguồn: `art-planner.csv` — 651 dòng đơn vị/overhead + 4 dòng W0 listing)

| Batch | Lane | P | Đơn vị | Bản ghi | MPx | Canvas đích | Giờ full | Giờ scope | Giờ L2 |
|---|---|---|---:|---:|---:|---|---:|---:|---:|
| `P-SHIP` | PLAYER | P0 | 25 | 25 | 0,36 | 256² | 113 | **75** | 13 |
| `P-DRONE` | PLAYER | P0 | 13 | 14 | 0,19 | 128² | 28 | **28** | 7 |
| `P-BULLET` | PLAYER | P0 | 8 | 33 | 0,55 | 32² | 11 | **11** | 2 |
| `P-FX` | PLAYER | P0 | 2 | 2 | 0,02 | 128² | 5 | **5** | 3 |
| `E-BODY` | ENEMY | P0 | 23 | 127 | 1,37 | 128² | 131 | **131** | 8 |
| `E-BULLET` | ENEMY | P0 | 11 | 185 | 1,65 | 64² | 48 | **32** | 2 |
| `B-BODY` | BOSS | P1 | 35 | 35 | 1,70 | 512² | 296 | **142** | 16 |
| `B-PART` | BOSS | P1 | 7 | 90 | 3,41 | 256² | 148 | **36** | 0 |
| `F-BOOM` | FX | P1 | 5 | 12 | 0,49 | 256² | 24 | **24** | 6 |
| `F-GLOW` | FX | P1 | 20 | 60 | 2,06 | 256² | 104 | **48** | 0 |
| `F-ENEMY` | FX | P1 | 1 | 11 | 0,04 | 128² | 11 | **0** | 0 |
| `G-PARALLAX` | BG | P1 | 26 | 106 | 11,16 | 1024² | 481 | **142** | 6 |
| `G-UI` | BG | P2 | 18 | 21 | 1,95 | 512² | 120 | **67** | 0 |
| `I-DROP` | ITEM | P2 | 9 | 54 | 1,97 | 128² | 36 | **19** | 5 |
| `U-HUD` | UI | P0 | 27 | 39 | 0,45 | 256² | 83 | **83** | 41 |
| `U-KIT` | UI | P2 | 97 | 155 | 6,53 | 256² | 310 | **168** | 0 |
| `U-ICON` | UI | P2 | 67 | 160 | 3,01 | 64² | 42 | **20** | 0 |
| `U-META` | UI | P2 | 54 | 297 | 11,30 | 256² | 257 | **58** | 0 |
| `U-SHOP` | UI | P2 | 62 | 131 | 5,12 | 256² | 216 | **95** | 0 |
| `X-BRAND` | EXCL | P3 | 18 | 90 | 0,24 | — | 28 | **10** | 0 |
| `X-PART` | EXCL | P3 | 46 | 127 | 4,72 | 256² | 242 | **39** | 0 |
| `X-TRIAGE` | EXCL | P3 | 214 | 411 | 14,58 | 256² | 1.181 | **0** | 0 |
| **Σ** | | | **788** | **2.185** | **65,4** | | **3.916** | **1.232** | **109** |

*Bảng này là **v1** (chưa cộng 32 h S0 ⇒ scope B = 1.264 h; cộng S0 thì full = 3.948 h). Sau khi đo lại `reuse` ở §3.6,
bảng v2 cao hơn **+346 h** — dùng cột `h_scope_v2` trong CSV, đừng dùng cột `h_scope` để lập kế hoạch.*

### 2.3 Rollup theo lane & theo priority (A)

| Lane | Đơn vị | Bản ghi | Giờ full | Giờ scope | Đọc ra |
|---|---:|---:|---:|---:|---|
| **PLAYER** | 48 | 74 | 156 | 118 | 3,4 % bản ghi, 4,0 % giờ — **rẻ nhất, đắt giá trị nhất** |
| **ENEMY** | 34 | 312 | 179 | 163 | 312 bản ghi nhưng chỉ ~40 thiết kế (biến thể 0,65) |
| **BOSS** | 42 | 125 | 444 | 178 | **đắt nhất/đơn vị**: 8,1 h/boss (1 bản ghi) · 5,3 h nếu tái dùng biến thể |
| **UI** | 307 | 782 | 908 | 424 | 36 % bản ghi, 23 % giờ full — nhưng phần lớn là **biến thể badge** |
| **FX** | 26 | 83 | 140 | 72 | sau khi bỏ brand chỉ còn 27 bản ghi thật |
| **BG** | 44 | 127 | 602 | 209 | 106 lớp nền — **khoản phình lớn nhất** của full parity |
| **ITEM** | 9 | 54 | 36 | 19 | rẻ, nhưng `head` (29 bản ghi) là **bộ phận boss** chứ không phải item |
| **EXCL** | 278 | 628 | 1.451 | 49 | 37 % giờ full — **đây là chỗ phải cắt** |

| Priority | Đơn vị | Bản ghi | Giờ full | Giờ scope | Giờ L2 |
|---|---:|---:|---:|---:|---:|
| **P0** | 109 | 425 | 418 | 365 | 76 |
| **P1** | 94 | 314 | 1.065 | 392 | 29 |
| **P2** | 307 | 818 | 982 | 427 | 5 |
| **P3** | 278 | 628 | 1.451 | 49 | 0 |

> **Đọc bảng này đúng:** P1 **đắt hơn P0 gấp 2,5 lần** dù ít bản ghi hơn — vì boss 512² và lớp nền 1024².
> Nếu chỉ có 1 artist thì **đừng** bắt đầu bằng boss; W1 (P0) cho ra bản chơi được trước.

---

## 3. Ước lượng khối lượng batch vẽ lại

### 3.1 Công thức (mở từng số, kiểm lại được)

```
giờ(1 đơn vị)   = rate(canvas) × mult(lane) × reuse × 1,20
reuse           = 0,65 nếu đơn vị có >1 bản ghi (frame/skin/biến thể) · 1,00 nếu chỉ 1
                  ⚠ công thức v1; §3.6 thay bằng: designs × 1,0 + variants × 0,25
giờ batch       = Σ giờ(đơn vị) + overhead(batch)
giờ L2 của unit = giờ scope(unit) × n_L2 / n_scope      (lát cắt tỉ lệ — xem giải thích dưới)
```

`1,20` = **review + sửa 1 vòng** (không phải buffer tuỳ ý: mỗi batch review 2 lượt, sửa trung bình 1 lần/asset).

**Vì sao L2 là *lát cắt tỉ lệ* của scope B, không phải một bảng giá riêng:** bản nháp đầu của kế hoạch này
tính L2 bằng `n_L2 × rate × mult × 1,15 × 1,20` ("design premium" vì không có mẫu để bám). Chạy thử thì
**sai về số học**: **23/29 đơn vị** có giờ L2 **lớn hơn** giờ scope của chính nó (nặng nhất `saw`: 6 bản ghi,
lấy 4 cho L2 ⇒ 11,0 h so với **9,4 h** của cả đơn vị), phần còn lại của lô thành **−1,6 h**, và tổng L2 phồng
lên **180,7 h** thay vì 108,9 h. "W1 ⊂ scope B" khi đó không còn đúng và bảng wave không cộng ra 1.232. Vì vậy:
- L2 lấy **đúng tỉ lệ** `n_L2 / n_scope` của cùng một công thức ⇒ `l2_h ≤ h_scope` **luôn đúng** (0 dòng âm),
  và `Σ wave = scope B` (kiểm bằng máy: 1.264,4 h).
- Giá scope B **đã** tính thiết kế trên **đơn vị**, không phải trên bản ghi, nên phần "premium" không biến mất —
  nó nằm trong `rate × mult` của bản ghi đầu tiên; `reuse 0,65` chỉ là chiết khấu cho các bản ghi **thêm**.
  Nếu đội thấy bản ghi đầu khó hơn thật, cộng 10–15 % vào W1 rồi **trừ đúng phần đó** ở W2–W5 (tổng không đổi).

`overhead(batch)` = 2–55 h: art direction, dựng file, contact sheet, export, review (cao nhất ở
`X-TRIAGE` 55 h vì phải xem ảnh).

### 3.2 Rate theo canvas & mult theo lane

| Canvas đích | Giờ/đơn vị | Dùng cho |
|---|---:|---|
| **≤ 32²** | 0,4 | đạn player, icon 32 |
| **33–64²** | 0,5 | đạn enemy, icon 64 |
| **65–128²** | 1,2 | enemy, drone, item, FX nhỏ |
| **129–256²** | 2,5 | tàu, boss part, nút/panel, badge meta |
| **257–512²** | 4,5 | boss 512², panel lớn |
| **> 512²** | 4,0 ⚠ | **chỉ** lớp nền phẳng nhiều lớp (style "paper cut"); nếu vẽ tay chi tiết thì **8–12 h/lớp** ⇒ `G-PARALLAX` ×2 |

| Lane | mult | Nghĩa |
|---|---:|---|
| PLAYER ship | 1,40 | silhouette + 110–160 màu + 3 biến thể livery |
| PLAYER drone | 1,20 | khối tròn + 1 chi tiết nhận dạng |
| BOSS | 1,50 | bất đối xứng + ≥1 khối phá được + phase |
| ENEMY | 1,00 | 30–60 màu, đọc được ở 64 px |
| BULLET | 0,60 | 1 màu + 1 viền, không gradient |
| UI (kit/hud/shop) | 0,70–0,80 | 9-slice + trạng thái (normal/hover/disabled) |
| UI (icon) | 0,50 | 1 ý tưởng/ô |
| UI (meta badge) | 0,40 | hệ badge: 1 mẫu + tint/scale runtime |
| FX | 0,80 | gần vô sắc, sáng bằng độ sáng |
| BG | 1,30 | 3 lớp parallax, tile được |
| ITEM | 0,60 | đọc ở 48 px trong rổ đạn |

### 3.3 Ba mức scope — chọn theo mục tiêu, không theo cảm hứng

| Scope | Bản ghi vẽ | Đơn vị | Giờ | Tuần @32 h (1 artist) | Tuần @32 h (2 artists) | Gồm |
|---|---:|---:|---:|---:|---:|---|
| **A. L2 — chơi được** | **82** | 29 | **148,9** (32 S0 + 8 overhead + 108,9 art) | 4,7 | 2,3 | S0 32 h + P0 slice |
| **B. L3 — khuyến nghị** | **801** (37 %) | 154 | **1.264** (gồm S0) | 39,5 | 19,8 | tất cả trừ phần lớn brand/parts/triage (giữ 12 parts) |
| **C. Full parity** | 2.185 | 788 | **3.948** (100 %, gồm S0) | 123 | 62 | gồm cả 3 lô B đã cắt: triage 1.181 h · parts 242 h · brand 28 h (= 1.451 h) |
| **B′. L3 sau khi đo lại `reuse`** | **801** | 154 | **1.610** | **50,3** | **25,2** | thay bảng giá bằng số đo §3.6 (+346 h) — **đây là số dùng để lập kế hoạch** |
| **C′. Full parity sau đo lại** | 2.185 | 788 | **4.388** | 137 | 69 | +439,9 h so với C |

*32 h/tuần = 40 h trừ 20 % họp/rework — dùng số này để lập kế hoạch, đừng dùng 40 h.*

**Vì sao B là khuyến nghị (không phải C):** B bỏ **1.384 bản ghi** (2.185 → 801) và **2.683 h** (3.916 → 1.232).
Ba nhóm cắt, cộng lại khớp đúng từng bản ghi và từng giờ:

| Nhóm cắt | Lô (bản ghi bỏ) | Bản ghi bỏ | Giờ tiết kiệm | Lý do (không phải "lười") |
|---|---|---:|---:|---|
| **1. Không vẽ** | `X-TRIAGE` 411 · `X-BRAND` 90 · `F-ENEMY` 11 | **512** | **1.210,4** | triage: 340 `unresolved` **chưa có nhãn** (vẽ trước = vẽ sai 30 % khối lượng) · brand: logo Apple/Google/Stripe/Coda **không được vẽ lại**, phải dùng brand kit chính thức · `F-ENEMY` là hiệu ứng trúng đạn, suy ra từ `F-GLOW` bằng tint + shader |
| **2. Giữ 1 mẫu, biến thể bằng tint/scale runtime** | `U-META` 233 · `U-ICON` 88 · `U-SHOP` 67 · `U-KIT` 59 · `F-GLOW` 32 · `I-DROP` 30 · `G-UI` 9 | **518** | **610,8** | badge/rank/shop cell trong mẫu gốc là **cùng 1 khung, khác màu chữ** (`ART_STUDY` §3.6 `fill` 0,87) ⇒ vẽ 1 mẫu + 3 trạng thái, phần còn lại do runtime |
| **3. Cắt theo số màn/boss thật** | `X-PART` 115 · `G-PARALLAX` 74 · `B-PART` 72 · `B-BODY` 19 · `E-BULLET` 65 · `P-SHIP` 9 | **354** | **862,3** | bản mới có **3 màn** (không phải 106 lớp nền), **16 boss** (không phải 35) và **không** dựng lại mô hình "tàu explode thành 127 mảnh" (`ASSET_TRIAGE` §4.3) — chỉ giữ **12** mảnh có gameplay |
| **Σ** | | **1.384** | **2.683,5** | = 3.915,8 − 1.232,4 ✔ |

### 3.4 Độ nhạy — ba chỗ số có thể sai và sai bao nhiêu

| # | Rủi ro | Tác động lên scope B | Xử lý |
|---|---|---|---|
| **S1** | ~~Worklist gộp quá tay~~ → **ĐÃ ĐO, ĐÃ ĐÓNG: không phải gộp quá tay** — 17/18 nhóm `over_merge` là **thiết kế riêng** (tỉ lệ `designs/kept` = 0,93–1,00); chỉ `hotro` (0,42) là họ biến thể thật | **+346,0 h** (đo được, không còn là khoảng): scope B **1.232,4 → 1.578,4 h**; scope C **3.915,8 → 4.355,7 h** | **đã xử lý** ở §3.6: thay `reuse 0,65` bằng `designs + variants × 0,25`; 2 cột mới `de_est` / `reuse_est` trong planner |
| **S2** | Rate canvas sai ±25 % | scope B **1.011–1.580 h** | hiệu chỉnh sau **pilot 16 asset** ở S0 (§5.7 — đo giờ thật/asset, ghi vào planner) |
| **S3** | Triage lật nhãn: 1 phần trong 411 bản ghi hoá ra là **nhân vật/enemy** | scope B **+60…+180 h** (⇒ 1.324–1.444 h) | triage sprint trước W2; chỉ ảnh hưởng `X-TRIAGE`, không đụng W1 |

Ngoài ra: `F-PRESET` (particle 954 hệ — claim từ `START_HERE`) **không** nằm trong 2.185 sprite ⇒ kế hoạch
này **không** tính giờ cho particle; đó là việc của tech-art (shader/curve), ghi ở §6 R7.

### 3.5 Kích thước batch & nhịp review

| Luật | Số | Vì sao |
|---|---:|---|
| 1 batch ≤ **40 h** (trừ 3 batch lớn: `U-KIT`, `X-TRIAGE`, `G-PARALLAX`) | 40 | batch lớn hơn thì review thành "xem lại cả tháng" |
| 1 lượt review ≤ **10 asset** cùng lane | 10 | để so silhouette cạnh nhau |
| 1 wave = **2–6 sprint** (sprint = 2 tuần = 64 h) | 64–384 h | wave là đơn vị **bàn giao + đo**; wave dài hơn 6 sprint thì tách (xem §5.6) |
| Không mở wave mới khi cổng wave trước **chưa đo** | — | tránh 3 wave cùng sai một lỗi palette |

### 3.6 Đo lại `reuse` (S1) — **đã đóng**: 17/18 nhóm là **thiết kế riêng**, không phải biến thể

17/18 dòng ở đây = 17/18 dòng **đo được**; 1 dòng (`boss dong ho real`) không có mẫu trên contact sheet nên vẫn là (C).

S1 (§3.4) là rủi ro lớn nhất của kế hoạch: nếu các "biến thể" trong worklist thật ra là **asset khác nhau**
thì chiết khấu `reuse 0,65` là sai. Lần này **đo được**, không phải đoán.

**Cách đo (chạy được lại):** lấy 1.901/1.903 sprite `kind = Sprite` có `contact_sheet`+`tile`, tách nền caro
(bằng 2 tông nền phổ biến nhất của ô, ngưỡng 26), cắt **hình bao** của sprite, chuẩn hoá về lưới
**32×32**, rồi so từng cặp trong cùng nhóm bằng **IoU** mặt nạ. Hai sprite có `IoU ≥ 0,90` ⇒ **cùng một thiết
kế** (biến thể: đổi màu / phóng / lật); dưới ngưỡng ⇒ **thiết kế riêng**. Đơn vị dùng để tính giờ:
`designs × giá đầy đủ + variants × 0,25 × giá đầy đủ`.

| Kiểm chuẩn (nhóm **đã biết** là biến thể) | n | designs đo được | Đúng? |
|---|---:|---:|---|
| `coda` · `codawhite` · `applepay` · `applepaywhite` · `evolution` · `manhplane` | 4·4·4·4·3·6 | **4·3·4·4·2·2** | ✔ gộp đúng (τ = 0,90); ở τ = 0,85 `codawhite` gộp 4→1 **quá tay** ⇒ chọn 0,90 |
| `pvp` · `bg` · `cd` · `blt` · `head` | 91·65·15·122·13 | **91·65·15·119·13** | ✔ **không** gộp nhầm (đã mở ảnh xác nhận: 91 huy hiệu rank khác nhau, 65 nền khác nhau) |

**Kết quả trên 18 dòng `over_merge = cao` có `kept_records > 0`:**

| Tỉ lệ `designs / kept_records` | Số dòng | Nhóm |
|---|---:|---|
| **1,00** (mỗi bản ghi một thiết kế) | **14** | `pvp` 64 · `bg` 32 · `cd` 28 · `cb` 22 · `head` 17 · `ships` 16 · `circle` 15 · `cb-` 15 · `droid` 14 · `boss` 13 · `da` 12 · `xvideo` 12 · `body` 12 · `plasmagun` 10 |
| **0,93–0,97** (gần như riêng) | 2 | `blt` 117/120 · `drone` 13/14 |
| **0,42** (đúng là họ biến thể) | **1** | **`hotro` 15/36** — 36 icon cùng khung badge, khác icon+chữ |
| **không đo được** | 1 | `boss dong ho real` (0/19 mẫu nằm trên contact sheet) — giữ nguyên giá v1 |

⇒ **S1 lo ngược chiều.** Rủi ro không phải "worklist gộp quá tay" mà là **bảng giá của kế hoạch đã chiết
khấu 35 % cho những asset thực ra là thiết kế riêng**. `hotro` là họ biến thể duy nhất, và nó lại đang bị
tính **đắt** hơn thực tế (7,0 → 6,1 h).

**Re-baseline (v2) — số dùng để lập kế hoạch từ giờ:**

| | v1 (như đã lập) | **v2 (đo lại)** | Δ |
|---|---:|---:|---:|
| Scope B — giờ art (1.232,4) | 1.232,4 | **1.578,4** | **+346,0 (+28,1 %)** |
| Scope B — gồm S0 32 h | 1.264,4 | **1.610,4** | +346,0 |
| Scope B — tuần 1 artist / 2 artists | 39,5 / 19,8 | **50,3 / 25,2** | +10,8 / +5,4 |
| Scope A (L2) — giờ art (108,9) | 108,9 | **137,3** | +28,4 |
| Scope A (L2) — gồm S0 + overhead | 148,9 | **177,3** | +28,4 |
| Scope C — giờ art (3.915,8) | 3.915,8 | **4.355,7** | +439,9 |

| Batch | v1 | v2 | Δ | Batch | v1 | v2 | Δ |
|---|---:|---:|---:|---|---:|---:|---:|
| `G-PARALLAX` | 141,8 | 211,7 | **+69,9** | `X-PART` | 38,7 | 48,8 | +10,1 |
| `U-KIT` | 168,2 | 227,4 | **+59,3** | `F-BOOM` | 24,4 | 32,8 | +8,4 |
| `E-BODY` | 131,4 | 188,9 | **+57,5** | `G-UI` | 66,9 | 72,8 | +6,0 |
| `U-SHOP` | 95,4 | 140,8 | **+45,5** | `I-DROP` | 19,0 | 24,7 | +5,8 |
| `U-META` | 57,9 | 84,8 | +26,9 | `P-BULLET` | 10,5 | 13,1 | +2,6 |
| `F-GLOW` | 47,7 | 71,2 | +23,5 | `U-ICON` | 20,1 | 22,6 | +2,6 |
| `U-HUD` | 82,8 | 97,9 | +15,1 | `P-DRONE` | 28,2 | 26,9 | **−1,3** |
| `E-BULLET` | 32,1 | 46,4 | +14,3 | **15 batch đổi** | **964,9** | **1.310,9** | **+346,0** |

*7 batch không đổi (267,5 h): `P-SHIP` 75,2 · `B-BODY` 141,6 · `B-PART` 36,1 · `X-BRAND` 10,0 · `P-FX` 4,6 ·
`F-ENEMY` 0 · `X-TRIAGE` 0 (4 batch đầu không có đơn vị nào đo được ≥2 mẫu, 3 batch sau có 0 bản ghi được vẽ).
964,9 + 267,5 = 1.232,4 ✔ và 1.310,9 + 267,5 = 1.578,4 ✔.*

| Wave (gồm overhead + S0) | W1 (L2) | W2 | W3 | W4 | W5 | P3 | Σ |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | 148,9 | 398,8 | 175,9 | 134,6 | 357,4 | 48,7 | 1.264,4 |
| **v2** | **177,3** | **537,5** | **181,0** | **166,7** | **489,1** | **58,8** | **1.610,4** |
| tuần 1 artist (cộng dồn) | 5,5 | 22,3 | 28,0 | 33,2 | 48,5 | 50,3 | — |
| **v2′** (W1 theo `l2_h_v3`) | **206,4** | 511,0 | 178,5 | 166,7 | 489,1 | 58,8 | **1.610,4** |
| tuần 1 artist (cộng dồn) | **6,4** | 22,4 | 28,0 | 33,2 | 48,5 | 50,3 | — |

*Dòng **v2′** là bản dùng để **lập lịch**: W1 tính theo `l2_h_v3` (giá đầy đủ từng unit, không chiết khấu reuse) thay vì
prorate theo bản ghi ⇒ **+29,1 h vào W1**, bù lại **W2 −26,5 h** và **W3 −2,5 h**; **tổng không đổi**. Xem
`W1_WORK_ORDER.md` §6.*

**Ba giới hạn của phép đo này (ghi để không đọc quá số):**

1. **Độ phủ 705/801 bản ghi (88 %).** 12 đơn vị chỉ đo được một phần (`cd` 15/28 · `cb` 17/22 ·
   `body` 6/12 · `xvideo` 9/12 · `gd` 4/8 · `tieude` 5/8 …) nên `designs` của chúng là **ngoại suy tỉ lệ**;
   riêng 12 đơn vị đó chiếm **+75,9 h** trong số +346,0 h.
2. **Mặt nạ hình bao, không phải hình học thật.** Hai sprite cùng silhouette nhưng khác chi tiết bên trong
   (cùng khung, khác hoa văn) vẫn bị tính là **2 thiết kế** ⇒ v2 là **cận trên** của mức tăng.
   Đã kiểm 5 nhóm UI nghi ngờ đúng kiểu này (`tieude` `gd` `ong` `goigem` `selectmap_gioihan`) bằng mắt:
   **cả 5 đều là art khác nhau**, không phải chữ khác nhau ⇒ không trừ lại.
3. **Giá biến thể 0,25 là giả định.** Nếu biến thể đắt bằng 0,35 giá đầy đủ thì tổng chỉ tăng **+2,4 h**
   (1.612,8 thay vì 1.610,4) — tức kết luận **không** phụ thuộc tham số này.

⇒ **Việc phải làm:** dùng **v2** cho mọi con số lập kế hoạch; `over_merge` không còn là "cảnh báo phải kiểm"
mà đã được **thay bằng số đo** trong 2 cột `de_est` (số thiết kế) và `reuse_est` (`designs / kept_records`).

---

## 4. Chuẩn art cho bản mới (theo `ART_STUDY.md`, có đối chiếu `ASSETS.md` §1)

### 4.1 Nguyên tắc

`ART_STUDY` §6 nói rõ: mẫu gốc là **nguồn để đo**, art mới là **hình vẽ mới** dựng theo đúng các số đó.
Vì vậy chuẩn dưới đây là **bảng số để vẽ theo + để chấm**, không phải bảng mô tả lại WindWings.

### 4.2 Ba va chạm phải giải trước khi vẽ (nếu không, mỗi artist sẽ tự quyết một kiểu)

**V1 — "outline đen dày 3–4 px" (ASSETS §1.1) vs `dark_share` 0,009–0,017 (ART_STUDY §3.5).**
Số thắng: **không** outline đen toàn cục. Viền chỉ dùng cho: bullet (bắt buộc), chữ, và **một số** icon UI.

**V2 — palette Ink & Ember dùng `#0B0E14` (V = 0,078) làm nền khối, nhưng `ART_STUDY` §4 đòi
`dark_share` sprite thường ≤ 0,03.** Đo thử một công thức "tàu" trộn 10 % `ink-900` + 20 % `ink-700` cho
`dark = 0,30` — **gấp 10 lần** ngưỡng. Kết luận: **không** dùng `ink-900` làm **thân** nhân vật; chỉ dùng
cho **nền, khe, viền âm**. Đây là quy tắc cứng của bản mới.

**V3 — `val` của mẫu (ships 0,55 · enemy 0,76 · bg 0,33) không tái lập được với palette tối.**
Đây là **lệch có chủ đích** (style "tĩnh, cô đơn, nguy hiểm" — `ASSETS` §1.1). Phải **ghi lại** và
**đo lại baseline** thay vì lặng lẽ trượt: bảng §4.3 là baseline mới, và cổng đo dùng **dải mới**,
không dùng số cũ để phán xét.

### 4.3 Bảng mục tiêu theo nhóm — số cũ (mẫu) vs số mới (bản mới)

| Nhóm | Mẫu: màu · val · val_std · dark (`ART_STUDY` §2) | **Mục tiêu bản mới** (màu · val · val_std · dark · chroma) | Lệch có ghi lý do |
|---|---|---|---|
| `ships` | 136 · 0,55 · 0,22 · 0,017 | **110–160 · 0,46–0,52 · 0,24–0,30 · ≤0,10 · 0,19–0,23** | tối hơn −0,06; dark cao hơn vì viền âm thay outline |
| `drones` | 114 · 0,66 · 0,23 · 0,012 | **100–130 · 0,45–0,52 · 0,22–0,26 · ≤0,08 · 0,18–0,22** | −0,16: bớt "đồ chơi", tăng "thiết bị" |
| `bosses` | 130 · 0,54 · 0,21 · 0,009 | **110–160 · 0,45–0,52 · 0,20–0,24 · ≤0,10 · 0,18–0,23** | gần như giữ; thêm 1 khối phá được phát sáng |
| `enemy` | 30 · 0,76 · 0,23 · 0,008 | **30–60 · 0,58–0,65 · 0,23–0,27 · ≤0,06 · 0,14–0,17** | −0,13: enemy sáng nhất **trong** khung tối, không cần trắng |
| `bullet` | 39 · **0,26** · 0,24 · **0,493** | **24–40 · 0,25–0,30 · 0,18–0,26 · ≥0,40 · ≤0,12** | giữ `val`/`dark` (mẫu đúng 100 %); **hạ màu 39 → 24–40** vì canvas 24² chỉ giữ 2 tông + viền |
| `ui` | 52 · 0,41 · 0,26 · 0,095 | **40–70 · 0,38–0,44 · 0,24–0,28 · ≤0,12 · ≤0,14** | giữ; thêm luật chroma ≤ 0,14 (xem §4.4) |
| `fx` | 35 · 0,72 · 0,24 · 0,015 | **3–10 · 0,70–0,90 · 0,15–0,25 · ≤0,02 · ≤0,08** | giữ `val`/`dark`; **màu 35 → 3–10** (glow gần trắng — `ART_STUDY` §3.4 `sat` 0,12) |
| `background` | 37 · 0,33 · 0,12 · 0,074 | **30–50 · 0,15–0,25 · 0,18–0,22 · ≥0,55 · ≤0,12** | **tối nhất** — nền là "giấy cắt nhiều lớp, tối dần" |
| `items` | 70 · 0,64 · 0,22 · 0,009 | **50–80 · 0,62–0,70 · 0,22–0,28 · ≤0,05 · 0,25–0,30** | giữ: item phải rực nhất trong khung (accent duy nhất) |

> **`val_std` là số tương đối** (`ART_STUDY` §3.2 + §5): nó đo trên **contact sheet JPEG 150 px**, không
> phải texel. Dùng để **so giữa các nhóm trong cùng một bộ**, **không** để chấm tuyệt đối một ảnh.

### 4.4 Palette — đo HSV từng màu (A), không phải "cảm giác"

| Vai | Hex | H | S | V | **C = S·V** | Dùng cho |
|---|---|---:|---:|---:|---:|---|
| `ink-900` | `#0B0E14` | 220 | 0,450 | 0,078 | 0,035 | nền sâu, khe, viền âm — **không** làm thân nhân vật |
| `ink-700` | `#161C26` | 218 | 0,421 | 0,149 | 0,063 | panel, khối tối |
| `ink-500` | `#2A3442` | 215 | 0,364 | 0,259 | 0,094 | **thân chính** của tàu/enemy |
| `ink-300` | `#4A566B` | 218 | 0,308 | 0,420 | 0,129 | khối sáng nhất của nhân vật |
| `paper` | `#E8E3D9` | 40 | 0,065 | 0,910 | 0,059 | highlight, chữ, FX lõi |
| `ember` | `#FF5A2B` | 13 | 0,831 | 1,000 | **0,831** | **chỉ** thứ gây sát thương (đạn, HP, CTA) |
| `ember-dim` | `#8C2F17` | 12 | 0,836 | 0,549 | 0,459 | viền đạn, hover |
| `teal` | `#4FD1C5` | 175 | 0,622 | 0,820 | 0,510 | shield/ally/thông tin |
| `gold` | `#F5C518` | 47 | 0,902 | 0,961 | 0,867 | thưởng, coin, rank cao |
| `danger` | `#E23A3A` | 0 | 0,743 | 0,886 | 0,659 | máu, cảnh báo |

**Ba luật rút ra từ bảng này (kiểm được bằng máy):**

1. **UI phải ở dải `C ≤ 0,14`** — chỉ `ink-*` + `paper` đạt; mọi màu accent đều **> 0,45** ⇒ UI **không**
   được lấy accent làm nền, chỉ làm chi tiết ≤ 5 % diện tích.
2. **`C` là thước đo đúng cho "không tranh với gameplay"**, không phải `S`: `ink-900` có `S = 0,45`
   trông như "bão hoà cao" nhưng `C = 0,035` — gần như vô sắc. Đo `S` trên pixel tối là **bẫy**.
3. **1 accent nóng / khung** (`ASSETS` §1.2): `ember` = sát thương, `gold` = thưởng, `teal` = shield.
   Ba màu này **không** xuất hiện cùng nhau quá 3 % khung (khớp ngân sách accent ≤ 10 % của `VISUAL_DESIGN` §2).

### 4.5 Chín **công thức tô** đã kiểm bằng số (A — kiểm bằng phép trộn, không cần vẽ)

Mỗi dòng là tỉ lệ diện tích trên một sprite. Cột phải là số **đạt được** khi trộn theo tỉ lệ đó.

| Recipe | Tỉ lệ | val | val_std | dark | chroma | Hợp với |
|---|---|---:|---:|---:|---:|---|
| `ship` | ink300 40 · ink500 25 · ink700 8 · paper 10 · ember 12 · emberdim 5 | **0,483** | 0,271 | 0,080 | 0,209 | tàu player |
| `enemy` | ink300 50 · paper 30 · teal 15 · ink700 5 | **0,613** | 0,250 | 0,050 | 0,162 | enemy thường |
| `drone` | ink300 50 · ink500 30 · gold 12 · paper 8 | **0,476** | 0,243 | 0,000 | 0,202 | drone/droid |
| `boss` | ink300 50 · ink500 15 · paper 10 · emberdim 15 · ember 6 · ink900 4 | **0,485** | 0,226 | 0,040 | 0,205 | boss |
| `bullet` | ink900 45 · ink300 45 · emberdim 10 | **0,279** | 0,185 | **0,450** | 0,120 | **đạn** — đúng luật "thân tối + viền sáng" |
| `ui` | ink500 50 · ink300 25 · ink700 8 · paper 12 · ember 5 | **0,405** | 0,253 | 0,080 | 0,133 | icon/nút/panel |
| `fx` | paper 55 · white 30 · ink300 12 · teal 3 | **0,875** | 0,174 | 0,000 | 0,063 | nổ/hit/glow |
| `bg` | ink900 40 · ink700 20 · ink500 30 · teal 10 | **0,221** | 0,213 | **0,600** | 0,106 | lớp nền parallax |
| `item` | ink300 45 · gold 25 · paper 25 · ink500 5 | **0,669** | 0,269 | 0,000 | 0,294 | item rơi |

> Đây là **cách kiểm rẻ nhất trước khi vẽ**: trộn theo tỉ lệ → tính `val/val_std/dark/chroma` → so dải §4.3.
> Sai thì sửa **tỉ lệ**, không sửa bảng.

**Đã tái lập bằng máy, không phải chỉ công bố:** `python3 docs/art-plan/measure_asset.py --recipe` dựng lại 9 mẫu
từ **hex palette §4.4 + tỉ lệ diện tích** rồi đo theo giao thức §4.9 ⇒ **9/9 khớp tới 3 chữ số** với bảng trên
(`val` 0,483/0,613/… · `val_std` · `dark` · `chroma`) **và 9/9 nằm trong dải §4.3** trên cả 4 chỉ số đo được.
Lưu ý: `colors` (ngân sách 3–160 màu) **không** kiểm được bằng phép trộn — nó chỉ đếm được trên art thật, vì
gradient/anti-alias sinh ra hàng trăm màu. Đổi hex palette thì **phải** chạy lại lệnh này trước khi sửa bảng. (`bg` có `val_std` 0,213 > mục tiêu 0,18–0,22 — do 1 nguồn sáng teal;
> chấp nhận, sẽ đo lại ở pilot.)

### 4.6 Gradient, viền, hình khối

| Thành phần | Luật | Kiểm bằng |
|---|---|---|
| **Số tông** | **3 tông** (shade / base / light) + 1 accent ≤ 15 % + 1 rim ≤ 5 % | đếm màu sau lượng tử hoá 32 bậc |
| **Bước sáng** | mỗi tông lệch **±18–22 % V** so với base (không dùng 3 tông cách nhau 40 %) | `val_std` **theo dải từng nhóm §4.3 (0,15–0,30)** — **không** dùng một dải chung; `ART_STUDY` §4 ghi 0,20–0,26 cho 5 nhóm chủ thể, đó là **dải tham khảo** cho tàu/boss/drone/enemy/ui, không áp cho `fx`/`bg`/`bullet` (`ART_STUDY` §3.2 tự nói `val_std` không phải ngưỡng tuyệt đối) |
| **Hướng sáng** | **1 nguồn duy nhất**, từ trên-trái 30°; **không** rim 2 phía | mắt + 1 ảnh/asset |
| **Outline** | **không** viền đen toàn cục; thay bằng **viền âm** (1–2 px @ 256², màu `ink-900` **chỉ ở cạnh khuất sáng**) | `dark ≤ 0,10` (nhân vật) |
| **Silhouette** | thu 64 px, tô đen 100 %: 5 tàu bất kỳ vẫn phân biệt được | test 5 mẫu/wave |
| **Chi tiết** | 1 khối thân + **≤ 2 khối phụ**; boss **≥ 1 khối phá được tách rời** | đếm khối |
| **Nhiễu/giấy** | noise ≤ 6 % opacity, **không** dùng noise làm chi tiết | `val_std` không vượt 0,30 |

### 4.7 Canvas, 9-slice, pivot, đặt tên

| Hạng mục | Chuẩn | Nguồn |
|---|---|---|
| Tàu | **256×256**, PPU giữ nguyên theo sprite gốc | `ASSETS` §3 |
| Drone / enemy | **128×128** | `ASSETS` §3 |
| Boss | **512×512** hoặc Spine (region 100–570 px) | `ASSETS` §3 + §6 |
| Đạn / laser | 24×24 · laser **32×512** tile dọc · *orb gốc ≥128 px (2 nhóm ở W1): chờ duyệt **64×64** — deviation khỏi `ASSETS` §3, xem `W1_WORK_ORDER.md` §8 #6* | `ASSETS` §3 |
| Nút / panel / ô shop / ô quà | 200×64 border 24 · 720×1080 bo 32 · 240×320 border 16 · 160×160 border 12 | `ASSETS` §3 + §5 |
| Nền | 1024×1024 (giữ), **3 lớp** parallax 0,2× / 0,5× | `ASSETS` §1.4 |
| 9-slice | border theo bảng `ASSETS` §5 (10 asset); **không** 9-slice nếu hoa văn chạy dọc viền | `ASSETS` §5 |
| Pivot / border | **không** suy từ PNG đã trim — đọc `sprite_mesh_contract` (source rect/offset/border/PPU) | `ASSETS` §9 #2/#4 (ĐÓNG) |
| Đặt tên | `<lane>_<vai>_<biến thể>_<size>@<màu>` — snake_case, không dấu, không tên gốc | mới |
| Metadata | mỗi asset có `source`, `license`, `author`, `recipe` | `ASSETS` §8 #10 |

### 4.8 Đóng gói atlas

Giữ nguyên **12 page** của `ASSETS` §4.2 + 4 luật packing §4.3 (padding 4 px, PoT, ≤ 2048², trống ≤ 15 %).
Bổ sung từ `ART_STUDY` §3.6: **pack theo hình bao** cho `fx` (`fill` 0,08), `enemy` (0,10), `bullet` (0,22) —
**không** lưới đều; chỉ `ui` (`fill` 0,87) mới dùng ô đều.

**Ngân sách atlas — có một con số phải kiểm lại (ghi ở đây để không phát hiện muộn):** 12 page của §4.2
là **18,87 Mpx bề mặt** ⇒ 9,0 MB ETC2 4 bpp (đúng như §4.2). Diện tích **hình bao** (A, `width×height`
trong manifest) là **65,4 Mpx** cho cả 2.185 sprite và **≈ 22,2 Mpx** cho scope B — tức **lớn hơn** bề mặt
18,87 Mpx nếu tính theo hình bao. Nhưng diện tích **đặc** (alpha > 0,5) thường chỉ 50–60 % hình bao với
tàu/enemy và ~87 % với UI, nên nhiều khả năng vẫn vừa 12 page.
⇒ **Không kết luận ở đây**: `fill` thật phải đo ở **pilot 16 asset (S0, §5.7)**. Nếu `Σ area / 0,85 > 18,87 Mpx`
thì tăng lên **14–16 page** (thêm 2–4 page 2048² = **+4,2…8,4 MB**) và **ghi vào `ASSETS` §4.2** — đây là
thay đổi **duy nhất về atlas** mà kế hoạch này đề xuất, và chỉ sau khi có số đo.

### 4.9 Giao thức đo (chốt trước khi vẽ, không chốt sau)

| Bước | Luật | Vì sao khác `art-study.py` |
|---|---|---|
| 1 | đo trên **PNG có alpha**, không JPEG | JPEG làm `dark_share` và `colors` thành **cận dưới** (`ART_STUDY` §5) |
| 2 | mask = `alpha > 0,5` | bỏ flood-fill caro (nguồn sai số thứ 2) |
| 3 | lượng tử **32 bậc/kênh** rồi đếm màu | giữ để so được với mẫu |
| 4 | `sat` **chỉ** trên pixel `V ≥ 0,25`; thêm **`chroma = S·V`** | `S` trên pixel tối là vô nghĩa (§4.4 luật 2) |
| 5 | `dark` = tỉ lệ pixel `max(R,G,B) < 45` | giữ nguyên định nghĩa mẫu |
| 6 | `fill` = diện tích sprite / diện tích ô atlas | dùng để quyết packing |

**Đã cài thành script:** `docs/art-plan/measure_asset.py` — `--recipe` kiểm 9 công thức (không cần Pillow),
`--dir <thư mục> --class <nhóm>` đo từng PNG và chấm theo dải §4.3, in ra đúng metric nào lệch.
Không thay `tools/art-study.py` (đo mẫu gốc trên contact sheet); script này đo **art mới** trên PNG có alpha.

### 4.10 Bốn cổng máy + hai cổng mắt

| Cổng | Đo cái gì | Ngưỡng | Lệnh |
|---|---|---|---|
| **G-A** | `val/val_std/dark/chroma` từng asset | dải §4.3, sai ≤ 1 chỉ số | script đo (mới, 40 dòng) |
| **G-B** | silhouette 64 px | 5/5 tàu phân biệt được | mắt (bắt buộc) |
| **G-C** | khung hình: tương phản **0,45–0,80** · accent gameplay **≤ 10 %** · chi tiết **13–22** | `VISUAL_DESIGN` §5 | `python3 tools/design-metrics.py <thư mục ảnh>` |
| **G-D** | 9-slice: kéo 3 kích thước (nhỏ/chuẩn/lớn) không mép giả | mắt, 3 ảnh/asset | — |
| **G-E** | pháp lý: không logo bên thứ ba, không hình gốc, không tên gốc | `ASSETS` §8 | checklist |
| **G-F** | đọc được ở 0,2 s: ảnh gameplay 2× chồng lên nền tối | mắt, 1 ảnh/wave | — |

**Ánh xạ sang đơn hàng vẽ (`W1_WORK_ORDER.md` §4 có A1–A13 cho từng unit):**
`A4 ↔ G-B` · `A9 ↔ G-C` · `A10 ↔ G-F` · `A12/A13 ↔ G-A` · `A11` (ngân sách màu) là cổng lô, đo cùng G-A.
`G-D` (9-slice) và `G-E` (pháp lý) là cổng **theo asset UI/brand**, không nằm trong A1–A13 của sprite — đừng trộn.

### 4.11 Đối chiếu **9 luật** của `ART_STUDY` §4 với chuẩn của bản mới (truy vết 1–1)

Mục đích: chứng minh **không luật nào của spec bị bỏ quên**, và mọi chỗ lệch đều có tên + lý do + chỗ kiểm —
thay vì để người review tự phát hiện. `STATIC_CONFIRMED` cho cột "spec" (đọc `ART_STUDY` §4 ngày 2026-10-27).

| # | Luật `ART_STUDY` §4 | Số của spec | Bản mới (§4.3 / §4.5 / §4.8) | Trạng thái | Kiểm ở đâu |
|---|---|---|---|---|---|
| 1a | Màu — **chủ thể chính** (tàu/boss/drone) | **110–160** | ship 110–160 · boss 110–160 · drone **100–130** | **KHỚP** (drone lệch −10 ở cận dưới) | G-A; pilot: nếu drone < 110 thì thêm 1 lớp vân |
| 1b | Màu — **sprite phụ** | **30–60** | enemy 30–60 ✔ · bg 30–50 ✔ · ui 40–70 · item 50–80 · **bullet 24–40** · **fx 3–10** | **LỆCH CÓ LÝ DO** (4 nhóm ra ngoài dải) | G-A; lý do ghi ngay ở cột 5 của §4.3 |
| 2 | `val_std` mọi sprite | **0,20–0,26** | theo nhóm: **0,15–0,30** | **LỆCH CÓ LÝ DO** — `ART_STUDY` §3.2 + §5 nói rõ *"không dùng làm ngưỡng tuyệt đối"*; `fx`/`bg`/`bullet` phẳng hơn mẫu | dùng dải §4.3, **không** dùng 0,20–0,26 để phán |
| 3 | `val` nền **≤ 0,35** · nhân vật **0,50–0,80** | — | nền 0,15–0,25 ✔ · enemy 0,58–0,65 ✔ · **tàu/drone/boss 0,45–0,52** | **LỆCH CÓ LÝ DO** (§4.2 **V3** — palette tối, đã ghi baseline mới) | pilot S0: nếu tàu không đọc được trong rổ đạn → nâng cận dưới lên **0,50** |
| 4 | `sat` UI **≤ 0,30** · nhân vật **0,50–0,60** | — | UI **C ≤ 0,14** · nhân vật **C 0,19–0,23** | **ÁP DỤNG KHÁC ĐƠN VỊ** — dùng `C = S·V` thay `S` (§4.4 luật 2: `S` trên pixel tối là bẫy) | G-A theo `chroma`; quy đổi: `ink-500` S 0,364 → C 0,094 |
| 5 | FX: `sat` **≤ 0,15** · `val` **≥ 0,65** | — | C 0,063 · val 0,70–0,90 | **KHỚP** | G-A |
| 6 | Bullet: `val` **0,22–0,30** · `dark` **≥ 0,35** | — | 0,25–0,30 · **≥ 0,40** | **KHỚP** (nhóm duy nhất mẫu đúng 100 %) | G-A |
| 7 | `dark_share` sprite thường **≤ 0,03** | — | ≤ 0,05…0,12 theo nhóm (viền âm `ink-900` — **V2**) | **LỆCH CÓ LÝ DO** | pilot: `dark > 0,03` **và** mắt thấy viền nặng ⇒ bỏ viền âm ở cạnh sáng |
| 8 | Không viền đen toàn cục | — | ✔ §4.6 | **KHỚP** | G-B + mắt |
| 9 | Pack theo hình bao cho fx/enemy/bullet (`fill` 0,08–0,28) | — | ✔ §4.8 | **KHỚP** | `fill` đo ở pilot 16 asset (S0, §5.7) |

**Kết quả truy vết: 5 khớp · 4 lệch có lý do (đã đăng ký ở §4.2 V2/V3 + §4.3) · 1 khác đơn vị đo.**
Không có luật nào "quên". Ba luật **đo được bằng máy** nhưng trước đây chưa có cổng riêng — `colors` (1),
`val_std` (2), `dark_share` (7) — nay thành **A11 · A12 · A13** trong `W1_WORK_ORDER.md` §4.

---

## 5. Thứ tự sản xuất L2 → L3

### 5.1 L2 và L3 cần gì từ art (định nghĩa theo `START_HERE` §2)

**L2** = "đúng **số**" ⇒ art chỉ cần **đúng kích thước, đúng silhouette, đúng vị trí pivot**, màu được
phép xấp xỉ. Không cần biến thể, không cần FX đẹp, **không cần** boss nhiều phase.
**L3** = "khớp trải nghiệm + **art**" ⇒ đủ biến thể/phase/FX/nền + đạt 4 cổng đo.

⇒ Vì thế **W1 phải là P0** và **phải vẽ chưa tới 4 %** tổng bản ghi (82/2.185, tức 10 % scope B) — đủ cho một bản chơi được.

### 5.2 Bảng wave

| Wave | Mức | Batch | Bản ghi | Giờ | Cổng ra (exit criteria) |
|---|---|---|---:|---:|---|
| **S0** | setup | — | — | **32** | art bible 1 trang · 9 recipe trong file mẫu · script đo chạy được · **pilot 16 asset** (§5.7 — đo giờ thật, đo `fill` cho atlas) |
| **W1** | **L2** | `P-SHIP` 5 · `P-DRONE` 4 · `P-BULLET` 12 · `P-FX` 2 · `E-BODY` 8 · `E-BULLET` 12 · `B-BODY` 2 · `U-HUD` 24 · `F-BOOM` 4 · `G-PARALLAX` 3 · `I-DROP` 6 | **82** | **148,9** (gồm S0 32) | chơi 1 màn không thiếu sprite · **G-A/G-C** đạt trên 3 ảnh gameplay · rate đã hiệu chỉnh |
| **W2** | L3-1 | `P-SHIP` +11 · `P-DRONE` +10 · `P-BULLET` +21 · `E-BODY` +119 · `E-BULLET` +108 · `F-BOOM` +8 · `G-PARALLAX` +29 | **306** | **398,8** | 3 màn có nền 3 lớp + đủ enemy · G-C trên 6 ảnh |
| **W3** | L3-2 | `B-BODY` +14 · `B-PART` 18 · `I-DROP` +18 | **50** | **175,9** | 1 boss đủ 3 phase + 2 khối phá được · G-B/G-D |
| **W4** | L3-3 | `U-ICON` 72 · `F-GLOW` 28 · `G-UI` 12 | **112** | **134,6** | toàn bộ icon trong 1 flow UI thật |
| **W5** | L3-4 | `U-HUD` +15 · `U-KIT` 96 · `U-META` 64 · `U-SHOP` 64 | **239** | **357,4** | 3 màn meta (shop/rank/battle-pass) chạy đủ trạng thái |
| **P3** | không vẽ | `X-BRAND` 0 · `X-PART` 12 · `X-TRIAGE` 0 | 12 | **48,7** | brand: chỉ **nhận brand kit**; parts: 12 mảnh gameplay; triage: chỉ vẽ **sau** sprint xem ảnh |
| **Σ B** | | | **801** | **1.264,4** = 1.232,4 art + 32 S0 | |

*Bảng trên là **v1**. Sau khi đo lại `reuse` (§3.6), cột giờ đổi thành: W1 **177,3** · W2 **537,5** · W3 **181,0** ·
W4 **166,7** · W5 **489,1** · P3 **58,8** ⇒ **Σ 1.610,4 h** (+346,0). Thứ tự wave, batch và cổng ra **không đổi** —
chỉ khối lượng mỗi wave tăng.*

*“+n” = phần còn lại của batch sau khi W1 đã lấy lát L2; số cộng theo cột phải khớp `kept_records` của planner.
Cột `wave` trong CSV = wave **xuất hiện đầu tiên**; cột `wave_done` = wave **hoàn thành phần còn lại** —
rollup giờ theo `wave_done` mới ra đúng bảng này (overhead của batch dồn về wave chứa ≥60 % bản ghi còn lại).*

### 5.3 Vì sao thứ tự này (không phải "theo lane cho gọn")

1. **W1 chứng minh cả pipeline** trên 7 lane trong 1 wave — nếu chờ xong player rồi mới làm UI thì lỗi
   palette sẽ nằm trong 500 asset trước khi bị phát hiện.
2. **W2 nặng nhất (537 h, 33 % scope B)** đặt ngay sau W1 vì đó là lúc rate còn "nóng"; **W3 (boss) tách riêng**
   vì boss cần review riêng từng phase.
3. **UI (W4–W5, 656 h theo v2) đẩy về cuối** vì UI phụ thuộc **luồng màn hình** — sửa luồng thì vẽ lại, còn enemy thì không.
4. **Triage không nằm trên đường găng**: 411 bản ghi chưa nhãn, vẽ bây giờ = 30 % rủi ro vẽ sai. Sprint xem
   17 sheet (3 ngày) đặt **song song S0**, kết quả đổ vào `X-TRIAGE` và mở khoá phần còn lại.

### 5.4 Lịch (1 artist / 2 artist, 32 h/tuần)

| Mốc | Giờ | 1 artist (tuần) | 2 artists (tuần) | Ghi chú |
|---|---:|---:|---:|---|
| **S0** (bible + 9 recipe + script đo + pilot 16 asset) | 32 | **1,0** | 0,5 | chưa tính triage |
| **Triage sprint** (17 sheet, 340 mục) | — | 0,6 | 0,3 | chạy **song song** S0 nếu có người thứ 2 |
| **W1 = L2 art-complete** | 148,9 | **4,7** (cộng dồn) | **2,3** | mốc bàn giao đầu tiên |
| W2 (2a+2b) | 398,8 | 12,5 | 6,2 | wave dài nhất — xem §5.6 |
| W3 | 175,9 | 5,5 | 2,7 | boss + item |
| W4 | 134,6 | 4,2 | 2,1 | icon + glow + BG UI |
| W5 (5a+5b) | 357,4 | 11,2 | 5,6 | phụ thuộc luồng UI (§6 R5) |
| P3 (parts lẻ + nhận brand kit) | 48,7 | 1,5 | 0,8 | không gồm triage vẽ |
| **Tổng scope B** | **1.264,4** | **39,5** | **19,8** | mốc **L3 art-complete** |

*32 h/tuần = 40 h trừ 20 % họp/rework. Chia 2 artist chỉ đúng khi tách được theo lane (§5.5) — W3 (boss) và W5 (UI) khó chia đôi hơn W2.*
*Số tuần trên là **v1** (1.264 h / 3.948 h). Bản **v2** dùng để lập kế hoạch (§3.6): **W1 = 5,5 tuần** (1 artist, cổng L2) — hoặc **6,4 tuần** nếu lấy `l2_h_v3`
(giá đầy đủ từng unit, `W1_WORK_ORDER.md` §6; tổng 50,3 tuần không đổi),
**tổng scope B = 50,3 tuần** (1 artist) / **25,2 tuần** (2 artists), scope C = 137 / 69 tuần. Chưa gồm thời gian chờ: code chạy được (L1), luồng UI chốt (§6 R5), và quyết định boss dùng Spine (§8 #6).*

### 5.5 Song song hoá (khi có ≥ 2 artist)

| Lane A (character) | Lane B (UI/FX) | Chia sẻ bắt buộc |
|---|---|---|
| ship → enemy → boss | HUD → icon → kit → shop → FX | 9 recipe (§4.5) · 1 file mẫu · 1 script đo · 1 buổi review/tuần |
| **Không** đổi recipe giữa wave | **Không** đổi border 9-slice giữa wave | nếu buộc đổi → **đo lại toàn bộ wave** trước khi merge |

### 5.6 Điểm cắt khi chỉ có 1 artist (W2 và W5 dài hơn 6 sprint)

| Nửa wave | Batch | Giờ v1 | **Giờ v2** | Sprint v2 | Vì sao cắt ở đây |
|---|---|---:|---:|---:|---|
| **W2a** | `E-BODY` · `E-BULLET` · `P-BULLET` · `F-BOOM` | 180,1 | **253,1** | 4,0 | toàn bộ "thứ bắn & bị bắn" — đo G-C trên ảnh gameplay ngay sau nửa này |
| **W2b** | `P-SHIP` · `P-DRONE` · `G-PARALLAX` | 218,8 | **284,5** | 4,4 | tàu + nền: hai thứ nặng nhất về silhouette và diện tích |
| **W5a** | `U-HUD` · `U-KIT` | 204,2 | **263,4** | 4,1 | HUD + kit: bộ khung màn hình, dùng chung 9-slice |
| **W5b** | `U-META` · `U-SHOP` | 153,3 | **225,6** | 3,5 | màn meta: phụ thuộc luồng, tách được khỏi HUD |

*Số trong bảng = `h_scope − h_l2` (+ overhead đã dồn về đúng wave) ⇒ v1 cộng lại 398,9 / 357,5 · v2 cộng lại
**537,6 / 489,0**, khớp bảng wave ở §3.6 (lệch 0,1 do làm tròn). **W2 và W5 giờ đều dài hơn 6 sprint ⇒ cắt là bắt buộc**,
không còn là tuỳ chọn.*

### 5.7 Gói pilot S0 — **16 asset cụ thể** (sổ: `s0-pilot-pack.csv`)

S0 không phải "làm quen": nó phải trả về **4 thứ** — ① art bible 1 trang · ② 9 recipe đã hiệu chỉnh bằng số ·
③ script đo chạy được trên PNG thật · ④ **16 asset pilot** đã đo, đủ để biết bảng giá lệch bao nhiêu.
Không có ④ thì cả lịch 50,3 tuần là số chưa kiểm.

| # | Batch | Asset | Chế độ | Giờ | Chứng minh điều gì |
|---|---|---|---:|---:|---|
| S0-01 | `P-SHIP` | `10001` | **full** | 4,20 | recipe `ship` · A11 110–160 · A12 · A13 ≤ 0,10 · A4 |
| S0-02 | `P-SHIP` | `10002` | blockout 20 % | 0,84 | **A4**: 2 tàu phải phân biệt được ở **64 px** |
| S0-03 | `B-BODY` | `bosss` | blockout 20 % | 1,62 | A4 + A6 (canvas 512) + ≥ 1 khối phá được tách rời |
| S0-04 | `G-UI` | `bghome` | blockout 30 % | 1,78 | A13 nền `dark ≥ 0,55` · A9 tương phản khung · 3 lớp parallax |
| S0-05 | `P-DRONE` | `20001` | full | 1,73 | A11 100–130 · A12 · A5 (1 nguồn sáng trên-trái) |
| S0-06 | `E-BODY` | `14_2` | full | 1,44 | A11 30–60 · A13 ≤ 0,06 |
| S0-07 | `E-BODY` | `212_1` | full | 1,44 | A4 cặp enemy (2 hình khác nhau) |
| S0-08 | `P-BULLET` | `plasmagun #1` | full | 0,29 | A2 **thân tối + viền sáng** · A13 ≥ 0,40 · canvas 24² |
| S0-09 | `P-BULLET` | `rocket` | full | 0,29 | A6 + A13 — đạn không được chói |
| S0-10 | `P-BULLET` | `laser` | full | 0,29 | A6 (**32×512**) + A13 |
| S0-11 | `P-FX` | `afterburner` | full | 1,30 | A11 3–10 · A12 0,15–0,25 · đọc được trên nền `ink-900` |
| S0-12 | `P-FX` | `shooter` | full | 1,30 | A6 + A11 (fx 3–10 màu) |
| S0-13 | `F-BOOM` | `bomb` | full | 2,40 | A12 + A9 trên **khung gameplay thật** |
| S0-14 | `U-ICON` | `exp` | full | 0,30 | A9 — UI không tranh gameplay (**C ≤ 0,14**) |
| S0-15 | `U-ICON` | `eye` | full | 0,30 | A13 ≤ 0,12 + A7 đặt tên |
| S0-16 | `I-DROP` | `05_0` | full | 0,86 | A11 50–80 · chroma 0,25–0,30 (**ngân sách accent**) |
| | | **Σ art** | | **20,38** | |

| Phần còn lại của S0 | Giờ |
|---|---:|
| Art bible 1 trang (palette + 9 recipe + 6 luật hình khối) | 3,00 |
| Hiệu chỉnh 9 recipe sau khi đo pilot (sửa tỉ lệ, không sửa bảng) | 3,00 |
| Chạy `measure_asset.py --dir` cho 16 asset + điền bảng `val/val_std/dark/chroma/fill` | 2,50 |
| Test đóng atlas: `Σ area / fill` ⇒ quyết 12 hay **14–16 page** (§4.8) | 1,50 |
| Review với art director (chốt 9 recipe + dải §4.3) | 1,00 |
| Buffer làm lại 1 asset (gần như chắc chắn có) | 0,62 |
| **Σ chuẩn bị** | **11,62** |
| **Σ S0** | **32,00** |

**Ba luật của S0** (nếu vi phạm thì pilot vô nghĩa):

1. **Pilot không vào build.** 16 asset nằm ở `art/_pilot/`, không copy vào atlas. Giá trị của chúng là **số đo**, không phải hình.
2. **Blockout không được dùng để chấm `colors`** — S0-02/03/04 chỉ chấm A4 · A6 · A9 · A13. Vì vậy **`boss` và `bg` chưa được
   xác nhận ngân sách màu ở S0**; hai cổng bắt buộc: **1 bg full ở đầu W2**, **1 boss full ở đầu W3** (chính là asset
   đầu tiên của wave đó — không cộng thêm giờ).
3. **Đo xong phải sửa bảng giá nếu lệch > 25 %** (rủi ro **S2**): ghi `giờ thật / giờ kế hoạch` từng asset vào planner
   (cột `rule_hint` của dòng tương ứng), rồi **chỉnh `rate` §3.2 một lần** — không chỉnh lẻ từng dòng.

---

## 6. Rủi ro & giả định

| # | Rủi ro | Xác suất | Tác động | Giảm thiểu |
|---|---|---|---|---|
| **R1** | ~~Worklist gộp quá tay~~ **ĐÃ ĐÓNG (§3.6)** — thực tế 17/18 nhóm là thiết kế riêng, và bảng giá v1 đã chiết khấu sai 35 % | đã xảy ra | **+346,0 h** (đã cộng vào v2) | dùng `h_scope_v2` / `l2_h_v2`; `de_est` thay cho việc xem ảnh |
| **R2** | Triage lật 411 bản ghi | cao | +60…180 h | sprint 17 sheet trước W2; **không** vẽ khi chưa có nhãn |
| **R3** | Style Ink & Ember quá tối → khó đọc trong rổ đạn | trung bình | vẽ lại 20 % W1 | W1 đo G-C + G-F trên ảnh gameplay thật, **trước** khi mở W2 |
| **R4** | Boss 512² + 3 phase vượt 8 h/unit | trung bình | +60 h ở W3 | tách "khối phá được" thành asset riêng (đã có `B-PART`) |
| **R5** | UI phụ thuộc luồng màn hình chưa chốt | cao | vẽ lại 30 % U-KIT | W4–W5 chỉ mở khi luồng UI chốt; trước đó chỉ vẽ **icon** (ít phụ thuộc) |
| **R6** | Nền 1024² phình (nếu đổi style vẽ tay) | trung bình | +300 h | chốt "phẳng nhiều lớp" ở S0; nếu đổi → tách scope riêng |
| **R7** | Particle 954 hệ **không** nằm trong 2.185 sprite | cao (chắc chắn) | ngoài ước lượng | tech-art làm shader/curve; art chỉ cấp texture 64×64/128×128 |
| **R8** | Spine 27 rig / 577 region cũng **không** nằm trong 2.185 | cao | ngoài ước lượng | `ASSETS` §6 đã có spec rig lại; cộng riêng khi chốt boss dùng Spine |
| **R9** | Asset trôi sang repo (vi phạm §8 legal) | thấp | chặn phát hành | G-E + `.gitignore` + metadata license |
| **R10** | Ước lượng giờ là **(C)**, không phải đo | — | ±25 % | hiệu chỉnh sau pilot 20 asset; ghi lại giờ thật vào planner |

**Giả định đã dùng (tất cả là (C)):** 1 artist làm được 32 h/tuần có ích · rate §3.2 đúng với đội
biết dùng vector + raster · không có asset nào phải làm lại vì đổi art direction giữa đường ·
brand kit lấy được từ Apple/Google (nếu không, cắt toàn bộ IAP visual) · **bản mới có 3 màn, 16 boss,
16 tàu** — đây là *phạm vi sản phẩm* (không phải số đo); đổi 3 → 5 màn thì cộng thêm ở nhóm cắt 3
(`G-PARALLAX` ≈ +45 h/màn, `B-BODY` ≈ +8 h/boss, `I-DROP` ≈ +5 h/màn).

---

## 7. Bàn giao, cách dùng, và những gì **không** bị đụng

### 7.1 File

| File | Nội dung |
|---|---|
| `docs/art-plan/ART_REDRAW_PLAN.md` | report này |
| `docs/art-plan/art-planner.csv` | **655 dòng** = 629 đơn vị vẽ (624 nhóm worklist + 5 bucket glyph) + 22 dòng overhead + **4 dòng W0 listing**; **36 cột** (v1 + 4 cột v2 + `l2_de` · `l2_h_v3` · `h_w0` · `w0_slots`) |

### 7.2 Từ điển cột planner

| Cột | Nghĩa |
|---|---|
| `row_id` | `AP-####` |
| `batch_id` | 1 trong 22 batch §2.2 — dùng để pivot |
| `lane` · `priority` · `wave` · `wave_done` | PLAYER/ENEMY/BOSS/UI/FX/BG/ITEM/EXCL · P0–P3 · wave **xuất hiện đầu tiên** · wave **hoàn thành phần còn lại** |
| `base_name` | base-name của worklist (**giữ nguyên**, chỉ thêm 5 dòng `GLYPH-*`) |
| `unit` | `group` (nhóm worklist) · `glyph` (bucket id) · `overhead` |
| `n_units` | số tên riêng trong đơn vị (glyph: 25 tàu… ; group: 1) |
| `n_records` | số bản ghi `Sprite` (manager) phủ bởi đơn vị này |
| `kept_records` | số bản ghi **nằm trong scope B** (0 = không vẽ) |
| `target_px` · `tier_rate_h` · `lane_mult` | canvas đích · rate §3.2 · mult §3.2 |
| `area_mpx` · `max_w` · `max_h` | diện tích (triệu px) · kích thước gốc lớn nhất trong nhóm — dùng để chọn rate |
| `l2_slice` · `l2_n` · `l2_h` | đơn vị này có bản ghi trong lát L2 không (yes/no) · số bản ghi lấy cho L2 · giờ L2 |
| `evidence` | G1/G2/G3/G0 (§1.4) |
| `recipe` | trỏ tới 9 recipe §4.5 |
| `h_full` · `h_scope` | giờ cho scope C và scope B theo bảng giá **v1** (§3.3); `l2_h ≤ h_scope` luôn đúng |
| `h_scope_v2` · `l2_h_v2` | **giờ đã đo lại** (§3.6) — dùng 2 cột này để lập kế hoạch; `h_scope_v2 ≥ 0` và `Σ = 1.578,4` |
| `l2_de` · `l2_h_v3` | lát L2 tính **theo unit**: số thiết kế phải vẽ cho L2 (`min(de_est, l2_n)`) · giờ L2 **không chiết khấu reuse**; dùng để **lập lịch wave 1** (`W1_WORK_ORDER.md` §6) |
| `h_w0` · `w0_slots` | giờ + số slot của **W0 listing** (4 dòng `lane = LISTING`, mọi cột `h_*` khác = 0 để tổng scope B không đổi) — `W0_LISTING_ASSETS.md` |
| `de_est` · `reuse_est` | **số thiết kế riêng** đo được (`IoU ≥ 0,90`) · `de_est / kept_records` — 1,00 = mỗi bản ghi một thiết kế |
| `over_merge` | `cao` = **37 dòng** (32 nhóm + 5 bucket glyph) có ≥10 bản ghi/đơn vị, **kiểm `reuse` trước khi vẽ** |
| `contact_sheet` · `sample_names` · `rule_hint` | tra ảnh + tên mẫu + luật nhãn gốc |

### 7.3 Cách dùng (3 việc, theo thứ tự)

1. **Lọc `l2_n > 0`** (29 dòng) → đó là W1/L2 (82 bản ghi = **137,3 h art (v2)** + 8 h overhead, cộng 32 h S0 = **177,3 h**).
   Không cần đọc phần còn lại.
   ⚠ **Nhưng đừng lập lịch bằng 177,3.** Chia đều theo bản ghi làm **thiếu** giờ L2: nền `G-PARALLAX` lấy 3/74 bản ghi
   nên chỉ bị tính 9,35 h, trong khi 3 nền đó là **3 thiết kế khác nhau** ⇒ thật là 18,72 h. Cộng `l2_h_v3`:
   art **155,4 h** + overhead **16,6 h** + 32 S0 = **204,0 h**; cộng 2,35 h setup `U-HUD` mà `wave_done` xếp vào W1 ⇒ **206,4 h**.
   Đây là **chuyển 29,1 h từ W2–W3 sang W1**, tổng scope B
   vẫn 1.610,4 h — chi tiết và bảng đối chiếu ở `W1_WORK_ORDER.md` §6.
2. **Lọc `over_merge = cao`** → 37 dòng từng bị gắn cờ; **`de_est` đã thay việc phải xem ảnh** (§3.6), chỉ còn `hotro`
   là họ biến thể thật — không cần xem lại.
3. **Lọc `kept_records = 0`** → danh sách **không vẽ** (brand/parts/triage) — đưa cho người quyết định
   scope, kèm lý do trong §3.3.

### 7.4 Không đụng gì

- **Không** sửa `docs/spec/**` (kể cả `ART_STUDY.md`, `ASSETS.md`, `art-worklist.csv`).
- **Không** sửa `datas/**`, `tools/**`, `tests/**`, `reverse-engineering/**`.
- **Không** copy / cắt / upscale bất kỳ PNG, atlas `sactx-*`, Spine, font hay audio từ APK.
- **Không** chạy runtime, không build, không sửa scene/prefab.
- Report **không** tuyên bố "đã xong art" — nó là **kế hoạch**; giờ là ước lượng **(C)**, chỉ số đếm là **(A)**.

### 7.5 Cách sinh lại planner (để người khác kiểm)

1. `04-asset-manifest.csv` → lọc `type = Sprite` (**2.185**).
2. Ghép nhãn theo `path_id` với `sprites-auto-classified.csv` / `sprites-classified.csv` (fallback theo `name`).
3. Tách glyph: `len(name) ≤ 2 or name.isdigit()` → **292 bản ghi / 164 tên**; còn lại dedup theo
   `tools/art-worklist.py` (**624 nhóm / 1.893 bản ghi**), chuẩn hoá `' ' → '_'` khi so với worklist.
4. Gán batch theo bảng luật §2.2 (thứ tự ưu tiên: brand → FX enemy → bullet player → boss part → boss →
   enemy → FX → UI meta → HUD → shop → icon → kit → BG → item → parts → triage).
5. Áp công thức §3.1; chọn scope B bằng xếp hạng `(evidence, n_records)` trong batch; **lát L2** =
   `h_scope × n_L2 / n_scope` (không dùng bảng giá riêng — lý do ở §3.1); gán `wave_done` theo §5.2
   (overhead dồn về wave chứa ≥ 60 % bản ghi còn lại).
6. Kiểm 9 tổng: `Σ n_records` = **2.185** · `Σ n_units`(group) + `Σ n_units`(glyph) = **788** ·
   `Σ kept_records` = **801** · `Σ l2_n` = **82** · `Σ h_scope` = **1.232,4** · `Σ l2_h` = **108,9** ·
   `Σ h_full` = **3.915,8** · `Σ h_scope_v2` = **1.578,4** · `Σ l2_h_v2` = **137,3**.
   Lệch bất kỳ số nào = lỗi join, không phải lỗi làm tròn.
7. **`de_est`** (nếu muốn tái lập §3.6): đọc từng ô contact sheet, tách nền theo 2 tông phổ biến nhất
   (ngưỡng 26), cắt hình bao, chuẩn hoá 32×32, IoU từng cặp trong nhóm, gộp khi `IoU ≥ 0,90`;
   `de_est = số cụm`, ngoại suy `× kept_records / n_đo_được` cho nhóm đo thiếu.
8. **Kiểm lại toàn bộ**: `python3 docs/art-plan/verify_numbers.py` — script đối chiếu planner, `w1-work-order.csv`
   và 3 tài liệu markdown (36 cột · 655 dòng · 12 tổng bất biến · wave `v2′` · 48 unit PLAYER). Exit 0 = khớp;
   mọi con số trong báo cáo này đều qua được script đó, không có số nào nhập tay.

---

## 8. Còn thiếu / phải đoán (ghi để không ảo tưởng)

| # | Điều | Trạng thái | Cách đóng |
|---|---|---|---|
| 1 | Giờ/asset thật của đội | **(C)** — chưa có mẫu | pilot 20 asset ở S0, ghi giờ thực |
| 2 | ~~`reuse` thật của 32 nhóm biến thể lớn~~ | **ĐÓNG (A)** — đo bằng IoU mặt nạ trên 1.901 sprite (§3.6): 17/18 nhóm là thiết kế riêng, chỉ `hotro` là họ biến thể | đã thay vào `de_est` / `reuse_est`; re-baseline v2 = +346,0 h |
| 3 | 340 `unresolved` là gì | **chưa biết** | sprint 17 sheet (§1.4) |
| 4 | 12 mảnh `B-PART` nào là khối phá được | **(C)** | chốt với designer ở W3 |
| 5 | Có cần 25 tàu hay 12 | **quyết định sản phẩm** | scope B giả định 16 (12 + 4 khoá) |
| 6 | Boss dùng Spine hay sprite | **quyết định kỹ thuật** | `ASSETS` §6 sẵn spec; nếu Spine thì cộng ~2 tuần rig (ngoài bảng này) |
| 7 | Font: dùng font thương mại nào | **chưa chốt** | không dùng 7 TMP SDF gốc (`ASSETS` §8 #6) |
| 8 | Đo lại baseline "mẫu" bằng PNG (không JPEG) | **chưa làm** | cần export PNG — hiện repo chỉ có contact sheet JPEG |
| 9 | Số boss thật của bản mới | **quyết định sản phẩm** | scope B giả định **16** (mẫu có 35); +1 boss ≈ +8 h ở `B-BODY` + 3–4 h `B-PART` |
| 10 | Có bao nhiêu màn | **quyết định sản phẩm** | scope B giả định **3**; +1 màn ≈ +45 h `G-PARALLAX` + 5 h `I-DROP` + 3 h `G-UI` |
| 11 | `de_est` của **12 đơn vị đo chưa đủ** (`cd` `cb` `body` `xvideo` `gd` `tieude` …) | **ngoại suy** — 129 bản ghi, +75,9 h | đo nốt 12 đơn vị (1 buổi); nằm trong pilot S0 |
| 12 | Mặt nạ **hình bao** coi "cùng khung khác hoa văn" là 2 thiết kế | **cận trên** của mức tăng | đã kiểm 5 nhóm UI bằng mắt: không có trường hợp nào cần trừ lại; nếu W1 thấy khác thì hạ `de_est` cho đúng nhóm đó |
