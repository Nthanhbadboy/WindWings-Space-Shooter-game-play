# W1 — Work order: 48 unit PLAYER (lát cắt L2)

> **Vai:** art-planner (`arena/1b836828`) · **Ngày:** 2026-10-27 · **Bước:** W1 = wave đầu, mục tiêu **L2 art-complete**.
> **Trạng thái:** đơn đặt hàng vẽ, **chưa vẽ gì**. Cặp file: `W1_WORK_ORDER.md` (quy trình) + `w1-work-order.csv` (48 unit + 4 overhead).
> **Nhãn bằng chứng:** `STATIC_CONFIRMED` = đọc trực tiếp từ CSV/ảnh trong repo · `INFERRED` = suy luận, có ghi cách suy.

---

## 0. TL;DR

| Câu | Trả lời |
|---|---|
| W1 vẽ gì | **48 unit** của lane PLAYER: 25 tàu · 13 drone · 8 nhóm đạn · 2 FX — nhưng **chỉ 13 unit** là L2 (5 tàu · 4 drone · 2 nhóm đạn · 2 FX) |
| Tốn bao nhiêu | art **34,0 h** (+ setup **7,2 h** của 4 batch) — phần còn lại của 48 unit (**67,9 h** art + **10,8 h** setup) nằm ở W2–W3 |
| Cả wave W1 | **206,4 h** = 32 S0 + **155,4 h** art (82 bản ghi / 29 dòng / 7 lane) + **16,6 h** overhead prorata + **2,35 h** setup `U-HUD` dồn về W1 — xem §6, **khác 177,3 h** trong plan |
| Xong khi nào | **6,4 tuần** (1 artist, 206,4/32) tính từ S0 thay vì 5,5 tuần; tổng 50,3 tuần **không đổi** (§6) |
| Điều kiện vào | S0 xong · palette Ink & Ember đã chốt (§4.4 plan) · quyền IP đã clear (W0-R4) · mở đúng **7 sheet nguồn**: `ships-01.jpg` · `drones-01.jpg` · `bullet-01.jpg` · `unclassified-07.jpg` · `unclassified-22.jpg` (`blt_player_5.`) · `unclassified-08.jpg` (afterburner) · `unclassified-18.jpg` (shooter) |
| Cổng ra | 13 unit L2 qua **A1–A9** + ảnh gameplay thật ở 720×1280 đo **G-C** (tương phản .45–.80) và **G-F** (đọc trong 0,2 s) |

---

## 1. W1 phải chứng minh cái gì

L2 không phải "vẽ ít cho nhanh" — nó là **lát cắt dọc**: một màn chơi được từ đầu đến chết, với **đủ 7 lane** để lộ lỗi
phối màu và lỗi pipeline *trước* khi mở W2 (537,5 h). Cụ thể W1 phải trả lời được 5 câu:

1. **Palette Ink & Ember có đọc được trong rổ đạn không?** (rủi ro **R3** trong plan) — đo trên ảnh gameplay, không đo trên asset rời.
2. **Pipeline atlas cắn được chưa?** 13 unit đầu phải export qua đúng script (32-px grid, alpha premultiplied = off, ETC2) — nếu sai, sai ở đây rẻ hơn sai ở 788 unit.
3. **Tỉ lệ canvas đã đúng chưa?** tàu 256², drone 128², đạn 24², laser 32×512 — vẽ ở đúng cỡ để không phải vẽ lại khi game scale.
4. **Silhouette 64 px có phân biệt được tàu/drone/đạn?** Nếu 3 thứ đọc ra như nhau ở 64 px thì cả lane PLAYER sai hướng.
5. **Tốc độ thật của 1 artist là bao nhiêu?** 13 unit / 34 h ⇒ đo được rate thực, đối chiếu bảng `rate` (§3.1 plan) trước khi cam kết W2.

> **W1 không phải** bản demo cho store, không phải trailer, không phải bản dịch — xem §7.

---

## 2. Lane PLAYER trong planner: 16 dòng = 48 unit

`STATIC_CONFIRMED` từ `art-planner.csv` (lọc `lane == PLAYER`):

| Batch | Dòng planner | Đơn vị | Bản ghi | Kept | L2 (bản ghi) | `h_scope_v2` | `l2_h_v3` |
|---|---|---:|---:|---:|---:|---:|---:|
| `P-SHIP` | AP-0016 | 25 | 25 | 16 | 5 | 67,20 | 21,00 |
| `P-DRONE` | AP-0011 | 13 | 14 | 14 | 4 | 22,90 | 6,91 |
| `P-BULLET` | AP-0002…AP-0009 | 8 | 33 | 33 | 12 | 9,10 | 3,45 |
| `P-FX` | AP-0013, AP-0014 | 2 | 2 | 2 | 2 | 2,60 | 2,60 |
| overhead | AP-0001, AP-0010, AP-0012, AP-0015 | — | — | — | — | 18,00 | 7,23 |
| **Σ** | **16** | **48** | **74** | **65** | **23** | **119,80** | **41,19** |

*Cột `l2_h_v3` = `h_scope_v2 × (min(de,l2) + (l2 − min(de,l2)) × 0,25) / (de + (kept − de) × 0,25)` — tức **đơn giá của chính dòng đó**
× số thiết kế phải vẽ ở L2 (biến thể reuse chỉ 25 %). Công thức bảo đảm `l2_h_v3 ≤ h_scope_v2` **luôn đúng** (đã kiểm 651/651 dòng).
Đây là cột mới thêm vào planner (cùng `l2_de`) để mỗi unit trong work order có **một con số giờ riêng**; xem §6.*

L2 cần **23 bản ghi** nhưng chỉ **13 unit**: 10 bản ghi đạn `plasmagun` là 10 thiết kế trong **1 nhóm**, và 2 bản ghi
`blt_player_5.` là 2 trong 8 thiết kế của **1 nhóm** — nên "13 unit" không phải "13 lần vẽ", mà là 13 dòng công việc.

---

## 3. Bảng đơn hàng (48 unit)

### 3.1 Tàu — `P-SHIP`, 25 unit (vẽ 5 ở W1, 11 ở W2, **9 cắt**)

Nguồn: `ships-01.jpg`, tile 1–25 · glyph `10001…10999` · canvas đích **256×256** · giá **4,20 h/unit** · recipe `ship`
(val .483 / val_std .271 / dark .080 / chroma .209).

| ID | mã gốc | gốc | tile | wave | h |
|---|---|---|---|---:|---:|
| PS-01 | 10001 | 122×128 | 1 | **W1** | 4,20 |
| PS-02 | 10002 | 128×128 | 2 | **W1** | 4,20 |
| PS-03 | 10003 | 125×128 | 3 | **W1** | 4,20 |
| PS-04 | 10004 | 128×123 | 4 | **W1** | 4,20 |
| PS-05 | 10005 | 122×128 | 5 | **W1** | 4,20 |
| PS-06 | 10006 | 115×128 | 6 | W2 | 4,20 |
| PS-07 | 10007 | 128×127 | 7 | W2 | 4,20 |
| PS-08 | 10008 | 128×108 | 8 | W2 | 4,20 |
| PS-09 | 10009 | 107×128 | 9 | W2 | 4,20 |
| PS-10 | 10010 | 123×120 | 10 | W2 | 4,20 |
| PS-11 | 10011 | 128×93 | 11 | W2 | 4,20 |
| PS-12 | 10012 | 128×90 | 12 | W2 | 4,20 |
| PS-13 | 10013 | 122×128 | 13 | W2 | 4,20 |
| PS-14 | 10014 | 128×120 | 14 | W2 | 4,20 |
| PS-15 | 10015 | 128×118 | 15 | W2 | 4,20 |
| PS-16 | 10016 | 128×91 | 16 | W2 | 4,20 |
| PS-17…PS-25 | 10017…10024, 10999 | 100×128 … 128×125 | 17–25 | **cắt** (ngoài scope B) | 0 |

**Vì sao 5 tàu ở W1:** L2 cần **5 tàu phân biệt** (màn 1 + 3 tuỳ chọn + 1 biến thể) để kiểm silhouette 64 px trên 5 hình khác nhau;
5 là số tối thiểu để phát hiện "tàu nào cũng giống tàu nào".

### 3.2 Drone — `P-DRONE`, 13 unit + 1 biến thể (vẽ 4 ở W1, 9 ở W2)

Nguồn: `drones-01.jpg`, tile 1–13 · glyph `20001…20013` · canvas **128×128** · **1,73 h/unit** · **biến thể = 0,43 h** (25 %)
· recipe `drone` (.476 / .243 / 0 / .202).

| ID | mã gốc | gốc | tile | wave | h |
|---|---|---|---|---:|---:|
| PD-01 | 20001 | 68×128 | 1 | **W1** | 1,73 |
| PD-02 | 20002 | 128×116 | 2 | **W1** | 1,73 |
| PD-03 | 20003 | 128×126 | 3 | **W1** | 1,73 |
| PD-04 | 20004 | 128×101 | 4 | **W1** | 1,73 |
| PD-05 | 20005 | 111×128 | 5 | W2 | 1,73 |
| PD-06 | 20006 | 147×256 | 6 | W2 | 1,73 |
| PD-07 | 20006 *(biến thể)* | 75×128 | 6 | W2 | 0,43 |
| PD-08…PD-14 | 20007…20013 | 88×82 … 128×126 | 7–13 | W2 | 1,73 ×7 |

> `20006` có **2 bản ghi cùng tile 6** (147×256 và 75×128) ⇒ 1 thiết kế + 1 biến thể. Đây là ca duy nhất trong lane;
> đừng "phát hiện" thêm biến thể nếu mắt thấy khác — đo bằng mask IoU ≥ 0,90 (§3.6 plan) rồi hãy tách.

### 3.3 Đạn — `P-BULLET`, 8 nhóm / 33 bản ghi (vẽ 12 bản ghi ở W1)

Canvas **24×24** cho đạn nhỏ, **64×64** cho orb lớn (`plasmagun` gốc 128², `blt_player_5.` gốc 256²) và **32×512** cho laser
· **0,29 h/bản ghi** · recipe `bullet` (.279 / .185 / .450 / .120 —
đạn là lane **tối nhất**, vì phải nổi trên nền ink-900).

| ID | nhóm | bản ghi | L2 | canvas | h (scope) | h (L2) | wave |
|---|---|---:|---:|---|---:|---:|---|
| PB-01 | `plasmagun` | 10 | **10** | 24² / 64² (orb) | 2,88 | **2,88** | **W1** |
| PB-02 | `blt_player_5.` | 8 | **2** | 24² / 64² (orb) | 2,30 | **0,58** | **W1** |
| PB-03 | `laserbeam_player` | 5 | 0 | 32×512 | 1,44 | 0 | W2 |
| PB-04 | `plasma_beam_flare_green` | 4 | 0 | 128×128 | 0,75 | 0 | W2 |
| PB-05 | `drone_laser` | 3 | 0 | 32×512 | 0,86 | 0 | W2 |
| PB-06 | `laser` | 1 | 0 | 32×512 | 0,29 | 0 | W2 |
| PB-07 | `rocket` | 1 | 0 | 24×24 | 0,29 | 0 | W2 |
| PB-08 | `drone_laser_child` | 1 | 0 | 24×24 | 0,29 | 0 | W2 |

> `plasmagun` 10 bản ghi = **10 thiết kế** (`de_est` = 10) — nhóm đạn **không** có reuse, mỗi viên là một hình khác.
> Ngược lại `blt_player_5.` 8 bản ghi nhưng chỉ 8 thiết kế ⇒ 2 viên L2 lấy từ 2 thiết kế đó.

### 3.4 FX — `P-FX`, 2 unit (cả 2 ở W1)

| ID | base | bản ghi | L2 | canvas | h | recipe |
|---|---|---:|---:|---|---:|---|
| PF-01 | `afterburner` | 1 | 1 | 128×128 | 1,30 | `fx` (.875 / .174 / 0 / .063) |
| PF-02 | `shooter` | 1 | 1 | 128×128 | 1,30 | `fx` |

**FX là lane sáng nhất** (val .875) — cố ý: hiệu ứng phải sáng hơn tàu để đọc được hướng bay. Đừng "hạ cho đồng bộ".

### 3.5 Setup — 4 overhead của lane PLAYER

| ID | batch | giờ (đầy đủ) | giờ vào W1 | Nội dung |
|---|---|---:|---:|---|
| OH-SHIP | `P-SHIP` | 8,00 | 2,50 | grid 32 px · pivot tàu (mũi tàu = +Y) · 5 mask va chạm |
| OH-DRONE | `P-DRONE` | 4,00 | 1,14 | khung 128² · neo animation lơ lửng (2 keyframe) |
| OH-BULLET | `P-BULLET` | 4,00 | 1,45 | script export 24/32/512 · pivot giữa · additive test trên nền ink-900 |
| OH-FX | `P-FX` | 2,00 | 2,00 | sheet 128² 4 frame · loop 12 fps |

---

## 4. Nghiệm thu từng unit

Mỗi dòng CSV có cột `accept` (mã `A-L2-xx`) + `gates_l2` / `gates_full`. Một unit **chỉ được tick `DONE`** khi qua **đủ** cổng của wave nó thuộc.

### 4.1 Bộ cổng

| Mã | Cổng | Ngưỡng đo được | Cách đo |
|---|---|---|---|
| **A1** | Alpha đúng | PNG RGBA, alpha thẳng (premultiplied = off), **0 pixel quầng trắng** ở mép | `tools/design-metrics.py --alpha`; soi mép trên nền ink-900 |
| **A2** | Đúng recipe palette lane | tỉ lệ val/val_std/dark/chroma lệch **≤ 5 pp** so với §4.5 plan | script đếm pixel theo 4 rổ |
| **A3** | 3 tông | mỗi khối ≤ **3 tông**, chênh **18–22 % V**, không gradient mượt | mắt + histogram |
| **A4** | Silhouette 64 px | thu còn 64 px vẫn nhận ra **đúng lớp** (tàu/drone/đạn/FX), không lẫn lớp khác | montage 64 px, nhìn 1 giây |
| **A5** | 1 nguồn sáng | sáng **trên-trái 30°**, ≤ **2 sub-block**, AO chỉ trong khe | mắt, kiểm 4 unit/lô |
| **A6** | Canvas | đúng bảng §4.6 plan (tàu 256 · drone 128 · đạn 24 · laser 32×512 · FX 128) | script kiểm kích thước file |
| **A7** | Tên file | `<lane>_<role>_<variant>_<size>@<colour>.png` | script regex |
| **A8** | Nhiễu | grain ≤ **6 %** biên độ, không noise trên vùng phẳng | FFT nhanh hoặc mắt trên 3 vùng |
| **A9** | Tương phản | **0,45–0,80**, accent nóng ≤ **10 %** diện tích | `tools/design-metrics.py` (G-C) |
| **A10** | Đọc trong game | thấy rõ trong **0,2 s** ở 720×1280, không chìm vào rổ đạn | ảnh gameplay thật (G-F) |

### 4.2 Cổng theo wave

| Wave | Unit phải qua | Ghi chú |
|---|---|---|
| **W1 (L2)** | **A1 · A2 · A4 · A5 · A6 · A7 · A9** | A3/A8/A10 để L3 — nhưng **A4 + A9 là bắt buộc**, vì đó là 2 cổng hay hỏng nhất |
| **W2 (phần còn lại)** | **A1–A10** | thêm A3 (3 tông), A8 (nhiễu), A10 (đọc trong game) |
| **Cắt** | — | PS-17…PS-25 **không vẽ**; chỉ vẽ nếu scope B được nâng (xem plan §3.3) |

### 4.3 Điểm review (không phải cổng, nhưng chặn)

1. **Sau PS-01 + PS-02:** review palette trên **2 tàu cạnh nhau** — nếu 2 tàu trông cùng một thiết kế ⇒ dừng, sửa recipe trước khi vẽ 3 tàu còn lại.
2. **Sau PF-01:** test afterburner **trên nền ink-900 trong game**, không test trên nền trắng Photoshop.
3. **Sau PB-01:** test 10 viên `plasmagun` **trong rổ đạn 30 viên** — đạn phải tách khỏi nhau, không thành 1 vệt.
4. **Cuối W1:** chụp 5 ảnh gameplay thật, đo **G-C** + **G-F**; kết quả ghi vào `ART_REDRAW_PLAN.md` §5.6 (nếu trượt, W2 mở bằng việc sửa palette, không phải vẽ thêm).

---

## 5. Thứ tự làm trong W1 (13 unit, 34,0 h)

| Bước | Việc | Unit | h | Vì sao thứ tự này |
|---|---|---|---:|---|
| 1 | Setup 4 batch (OH-*) | 4 | 7,23 | grid/pivot/export phải có **trước** unit đầu tiên, nếu không phải export lại |
| 2 | **PS-01, PS-02** | 2 | 8,40 | 2 tàu đầu = chốt palette + silhouette; đây là **cổng review #1** |
| 3 | **PF-01, PF-02** | 2 | 2,60 | FX sáng nhất ⇒ test nền ink-900 sớm nhất có thể |
| 4 | **PB-01** (10 viên) | 1 | 2,88 | đạn là thứ nhiều bản ghi nhất ở L2; làm sớm để lộ lỗi export 24 px |
| 5 | **PB-02** (2 viên) | 1 | 0,58 | bổ sung nhóm đạn thứ 2 (khác màu) |
| 6 | **PS-03, PS-04, PS-05** | 3 | 12,60 | 3 tàu còn lại, đã có palette chốt ở bước 2 |
| 7 | **PD-01…PD-04** | 4 | 6,92 | drone cuối vì 4 hình nhỏ, dễ nhất — nhưng **vẫn phải qua A4** (64 px) |
| **Σ** | | **13** | **33,96 → 34,0** | + 7,23 setup = **41,19 h** cho lane PLAYER trong W1 |

---

## 6. Đối chiếu số: 177,3 h (plan) vs 206,4 h (work order)

`STATIC_CONFIRMED` — cả hai đều tính từ `art-planner.csv`, khác nhau ở **cách chia lát L2**:

| Thành phần | Plan v2 (`l2_h_v2`) | Work order (`l2_h_v3`) | Vì sao khác |
|---|---:|---:|---|
| Art L2 (82 bản ghi) | 137,29 | **155,41** | `l2_h_v2 = h_scope_v2 × l2_n / **n_records**` — chia cho *tổng* bản ghi nên phạt 2 lần cho dòng có `kept < n_records`. Ví dụ `G-PARALLAX bg`: l2 3, kept **32**, n_records 64 ⇒ 199,68 × 3/64 = **9,35 h**, nhưng 3 nền đó là **3 thiết kế** ⇒ 18,72 h |
| Overhead prorata | 8,0 (plan ghi *"+ 8 h overhead"*, **không nêu cách tính**) | **16,62** | 8,0 ≈ setup của 4 batch PLAYER (7,23, làm tròn) ⇒ plan **chỉ tính overhead của lane này**; đúng phải prorata theo tỉ lệ giờ L2 của **cả 11 batch** có L2 (W1 có 6 lane khác cùng chạy) |
| Setup `U-HUD` dồn W1 | 0 | **2,35** | dòng `AP-0017` (`U-HUD/overhead`, 6,00 h) có `wave_done = W1` trong khi **cả 12 dòng `U-HUD` đều là W5** ⇒ phần setup còn lại sau prorata bị tính vào W1. Giữ nguyên dữ liệu plan, chỉ ghi nhận |
| S0 | 32,0 | 32,0 | không đổi |
| **W1** | **177,3** | **206,4** | **+29,1 h (+16 %)** |

**Đây là phân bổ lại, không phải tăng tổng:** 29,1 h chuyển từ các wave sau về W1 — **W2 −26,5 h** (537,5 → 511,0),
**W3 −2,5 h** (181,0 → 178,5), W4/W5 gần như không đổi. Rollup theo `wave_done`: W1 **206,4** · W2 **511,0** · W3 **178,5** ·
W4 **166,7** · W5 **489,1** · P3 **58,8** = **1.610,4**.
`Σ h_scope_v2` vẫn **1.578,4 h**, scope B vẫn **1.610,4 h**, scope C vẫn **4.355,7 h**.

**Hệ quả lịch:** mốc 1 = **6,4 tuần** (206,4/32) thay vì 5,5; cộng dồn các mốc sau gần như không đổi (50,3 tuần / 25,2 tuần cho 2 artist).

**Cách dùng:** lập lịch bằng **206,4**; con số 177,3 trong plan giữ nguyên như "kịch bản có reuse" và chỉ dùng để so sánh.
Nếu W1 xong sớm hơn 206,4 thì phần chênh chính là reuse thật đo được — ghi vào §3.6 plan.

---

## 7. Không nằm trong W1

| Thứ | Vì sao |
|---|---|
| 35 unit còn lại của lane PLAYER (PS-06…PS-16, PD-05…PD-14, PB-03…PB-08) | thuộc W2–W3 — **67,9 h art** (+10,8 h setup còn lại), không cộng vào W1 |
| 9 tàu `10017…10999` | **cắt** khỏi scope B (plan §3.3); chỉ vẽ nếu nâng scope |
| 121,4 h art L2 của 6 lane khác (UI 55,9 · BG 18,7 · BOSS 16,2 · ENEMY 15,8 · FX 9,6 · ITEM 5,2) | cùng wave W1 nhưng **không thuộc lane này** — xem §2 để biết ai làm |
| Icon / key art / screenshot | **W0**, `W0_LISTING_ASSETS.md` — 35 h, sổ riêng |
| 954 particle system · 27 Spine rig · 577 region · 7 TMP SDF font | out-of-scope (plan §1) |
| Boss, enemy body, UI kit, store, meta, brand | W2–W5 |

---

## 8. Việc cần chốt trước khi vẽ unit đầu

1. **Quyền IP** (W0-R4, `USER-ONLY`): art gốc + tên `WindWings` — **chặn**, không vẽ trước khi clear.
2. **Palette đã ký chưa**: 9 recipe ở plan §4.5 là **đề xuất**, không phải đã duyệt. Art director phải ký **trước** PS-01,
   nếu không 13 unit W1 có nguy cơ vẽ lại toàn bộ (rủi ro R3).
3. **Ai làm 6 lane còn lại của W1** (121,4 h) — nếu chỉ 1 artist thì W1 = 206,4 h là **của một người**, và lịch 6,4 tuần chỉ đúng khi không ai khác chờ.
4. **Canvas 256² cho tàu** có đúng với build không: nếu game render tàu ở 128 px thì giảm canvas xuống 128² để tiết kiệm ~15 % giờ lane PLAYER (`INFERRED`, cần đọc build).
5. **Chốt cách đo A2** (đếm pixel theo 4 rổ) — hiện là script đề xuất, chưa có trong `tools/`.
6. **Canvas cho đạn orb**: `ASSETS` §3 (spec, read-only) quy định **24×24** cho *mọi* đạn, nhưng `plasmagun` gốc 128² và
   `blt_player_5.` gốc 256² — nếu kích thước hiển thị thật ≥ 32 px thì phải **64×64**, tức **deviation khỏi spec**.
   Work order đang để `24²/64²`; **cần art director duyệt**, không tự đổi chuẩn.

---

## 9. File liên quan

| File | Nội dung |
|---|---|
| `w1-work-order.csv` | 53 dòng = **48 unit** (`kind = unit`, 1 `variant`) + 4 overhead; cột `scope` = W1/W2/out, `h_l2`, `h_full`, `gates_l2`, `gates_full`, `accept` |
| `art-planner.csv` | 655 dòng (651 + 4 W0) × **36 cột**; thêm `l2_de` · `l2_h_v3` · `h_w0` · `w0_slots` |
| `ART_REDRAW_PLAN.md` | báo cáo chính — §3.6 (đo reuse), §4 (chuẩn art), §5 (wave), §7.3 (cách lọc L2) |
| `verify_numbers.py` | `python3 docs/art-plan/verify_numbers.py` — đối chiếu planner + work order + 3 tài liệu; exit 0 = khớp hết |
| `W0_LISTING_ASSETS.md` | 27 slot listing cho 3 store, 35 h, sổ riêng |
