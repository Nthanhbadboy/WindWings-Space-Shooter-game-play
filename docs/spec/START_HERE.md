# START_HERE — dựng một game mới từ bộ spec này

> **Câu hỏi của bạn:** *"Bộ tài liệu này có đủ để AI làm game mới không, và có dữ liệu gốc đã
> phân tích để học cho đúng và đẹp không?"*
>
> **Trả lời ngắn:** **Đủ cho L1** (*giống cơ chế, khác art – level – nội dung*), và **có** dữ liệu
> gốc đã phân tích: **2.112 sprite, mỗi cái 12 cột số đo** · **42 contact sheet** · **35 ảnh chụp thật**
> · **54.019 layout** · **139 file asm (142.136 dòng)** · **126 bảng ScriptableObject** ·
> **~1.857 sprite đã phân loại**. Dùng để **học bằng số** rồi **vẽ/thiết kế mới** — không chép hình.
>
> Tài liệu này là **cửa vào**: nó chỉ đường, không chép lại số của 40 file khác. Mọi con số dưới
> đây đều có claim trong `tools/verify-claims.py`.

---

## 1. "Có dữ liệu gốc đã phân tích" — đúng, và nằm ở đây

| Kho | Có gì | Số lượng | Trả lời câu hỏi |
|---|---|---|---|
| `docs/apk-analysis/` | Báo cáo bóc APK + bảng CSV | **66** `.md` · **107** `.csv` · **83** ảnh chụp (35 dùng được để đo) | "Con số này ở đâu ra?" |
| `datas/` | JSON/CSV bóc trực tiếp | **31** file · 13 MB | wave, UI (**797** màn / **150.131** node), HP, boss, tàu, item, map, audio, text |
| `reverse-engineering/raw/typetrees/` | Typetree từng class | **142** file | "Field nào tồn tại, kiểu gì, mặc định bao nhiêu?" |
| `reverse-engineering/raw/il2cpp-consts/` | **Asm thật** của từng method | **139** file · **142.136** dòng | "Game *làm* gì, không chỉ *khai báo* gì" |
| `reverse-engineering/scriptableobjects/` | Bảng ScriptableObject | **126** CSV · 13 MB | số cân bằng: súng, enemy, stage, shop |
| `docs/assets/art-study.csv` | **Mỗi sprite 12 số đo** | **2.112** sprite | màu, bão hoà, gradient, outline, độ lấp |
| `docs/assets/design-metrics.json` | Số đo trên **ảnh chụp thật** | **35** ảnh | tỉ lệ khung, tương phản, ngân sách accent |
| `docs/assets/contact-sheets/` | 42 tờ ảnh cắt từ atlas gốc | **42** JPG | nhìn silhouette / tỉ lệ / cỡ chữ — **để học, không để chép** |
| `docs/assets/sprites-index.csv` | Danh mục sprite | **2.197** dòng | tra cứu nhanh theo tên/kích thước |
| `docs/assets/sheet-splits.csv` | Toạ độ cắt từng mảnh | **307** sheet · **4.250** mảnh | biết một "sprite" thật ra là mấy hình |
| `docs/assets/sprites-auto-classified.csv` | Nhãn + provenance | **1.857/2.197** có nhãn | biết cái nào là UI / đạn / FX / boss |
| `reverse-engineering/raw/sprite-geometry/` | **Geometry thật** của sprite (`m_RD`) | **2.185** sprite · **67** page `sactx` | cắt đúng chỗ, biết sprite nằm trang nào |
| `docs/assets/sprites-atlas-page.csv` | Trang texture thật của từng sprite | **282**/340 ca chưa nhãn biết trang | gán nhãn theo trang (đo precision trước) |
| `datas/opening_persistence.json` | **Contract save mở đầu** | **8 key family · 2 store · 7 limitation** | dựng first-run/tutorial/progression mà không đoán key |
| `reverse-engineering/raw/player-loadout/` | Mảng int + asm `Player_Saved_Datas` | **5 blob · 49 int · 5/5 sha256 OK** | giá craft/unlock, chứng cứ save |
| `docs/spec/RAW_AUDIT.md` | **Sổ kiểm claim ↔ raw** | **159 RAW · 2 DOC · 28 CONST / 189** | biết số nào tái đo được, số nào "đo một lần" |
| `tools/` | **9** script đo lại được | — | `verify-claims.py`, `art-study.py`, `classify-by-atlas.py`, … |

**Cộng kho đo được (đếm bằng `AI1`):** **139** file asm · **142.136** dòng asm · **142** typetree · **126** bảng ScriptableObject · **42** contact sheet · **31** file `datas/`.


### 1.1 Ranh giới duy nhất — và nó **không** hạ chuẩn

| Được (khuyến khích) | Cấm |
|---|---|
| Đọc **số đo** (màu, tương phản, tỉ lệ, nhịp) rồi vẽ mới theo đúng các số đó | Phát hành **file gốc**: atlas `sactx-*`, sprite, font, Spine, audio (trong build hay trong repo) |
| Xem contact sheet để hiểu **cách tổ chức thị giác** (mật độ, thứ bậc, silhouette ở 64 px) | Cắt sprite từ contact sheet rồi dùng làm asset game mới |
| Đo ảnh chụp thật để lấy **ngân sách accent / tương phản / vignette** | Chép nguyên palette hoặc dựng lại từng khung hình 1:1 |

> **"Không tái lập 1:1" KHÔNG phải lý do để làm art xấu.** Chất lượng thị giác là **yêu cầu riêng**
> và **có số** — `VISUAL_DESIGN.md` §1–§5 + test bằng máy ở §5. Lệch khỏi 4 khoảng số đó thì **sửa
> art**, không sửa số.

---

## 2. Làm cho **ĐÚNG** — tám con số xương sống

**Trước hết, bốn mức "xong"** (định nghĩa đầy đủ ở `DONE.md` §2 — dùng đúng tên này khi báo cáo):

| Mức | Nghĩa | Kiểm bằng | Phạm vi đã chốt |
|---|---|---|---|
| **L0** | chạy được: mở, vào màn, bắn, chết, qua màn | chạy 30 phút không crash | ✅ bắt buộc |
| **L1** | đúng **luật** cơ chế, không cần giống số | chơi thử theo checklist cơ chế | ✅ **mục tiêu của bộ spec này** |
| **L2** | đúng **số** (DPS, HP, nhịp spawn khớp bản gốc) | so bảng số | ❌ chưa (6 blob rodata chưa bóc) |
| **L3** | người chơi **không phân biệt được** | test mù | ❌ bỏ |

> ⚠ **"Bỏ L3" chỉ có nghĩa là bỏ tái lập 1:1 asset/cảm giác** — **không** phải bỏ chất lượng.
> Chất lượng thị giác **vẫn bắt buộc** và có test bằng máy: `VISUAL_DESIGN.md` §5.

Không cần đọc hết 40 file trước khi bắt đầu. Tám con số này đủ để dựng khung chơi được:

| # | Cái gì | Số | Ở đâu (claim) |
|---:|---|---|---|
| 1 | Khung hình dọc | tỉ lệ **0,4813** (≈ 9:18,7) — **tham chiếu trên một thiết bị**, không phải canvas bắt buộc | `VISUAL_DESIGN.md` §1 (**AN1**) |
| 2 | Điều khiển | kéo ngón để lái · biên **20×25** · radius **15** unit | `GAMEPLAY.md` §1 |
| 3 | Súng / đạn | **458** cấu hình · damage **40–1.200** (median **400**) · **186** loại đạn | `COMBAT.md` §0 |
| 4 | Wave | **282** wave · **11.089** dòng · median **28,5** dòng/wave · **109** prefab enemy | `ENCOUNTERS.md` §1 (**AQ1/AQ4**) |
| 5 | Spawn | `rate` trung vị **1,0 s** · `y` **9,6** · radius **0,1** · **68 %** là `point_range` (**số đo, không phải luật**) | `SCRIPTS.md` §3 (**AQ6**) |
| 6 | Độ khó | **3** chế độ · `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · **không** nhân số quân | `DIFFICULTY_MODES.md` §5 (**E1/E2**) |
| 7 | HP | HP bar trên **109/109** prefab · HP thật = bảng × `kHp[mode]` | `ENEMY_HP_RUNTIME.md` §0 |
| 8 | Rơi đồ | **702** vật đặt sẵn (**676** coin / **26** item) · **246/2.094** slot có item · **6** loại | `ECONOMY.md` (**AE1–AE3**) |

> ⚠ **Đọc 8 số này đúng cách:** chúng là **mô tả phân bố** của bản gốc, **không** phải luật engine.
> `rate = 0` **chưa** chứng minh "spawn cả loạt cùng frame": report 53 cho thấy Path/Waypoints đưa `rate`
> vào `WaitForSeconds`, và 0 chỉ là một nhánh — **không** suy thứ tự thực thi. Muốn khác cũng được,
> nhưng phải **ghi là lựa chọn thiết kế**, không giả làm "đúng bản gốc".

Thứ tự dựng đề xuất + hoá đơn sản xuất: `GAMEPLAY.md` §7 · `DONE.md` · cái gì **chưa** có:
`MISSING_FOR_NEW_GAME.md` (13 hệ: **8 đủ · 5 một phần · 0 thiếu hoàn toàn**). Bộ **48 câu hỏi thiết kế**
phải tự trả lời (29 câu đã có số): `DESIGN_QUESTIONS.md`.

---

## 3. Làm cho **ĐẸP** — lấy số từ mẫu gốc, không lấy hình

Hai tầng số, đều đo trên dữ liệu gốc:

**a) Bản thân sprite — "vẽ dày bao nhiêu chi tiết"** (`ART_STUDY.md` §2–§3, claim **AO1**)

| Nhóm | **Số màu** (p50) | Bão hoà | Gradient | Outline (`dark`) | Độ lấp (`fill`) |
|---|---:|---:|---:|---:|---:|
| `enemy` (nhỏ) | **30** | 0,53 | 0,23 | 0,008 | **0,10** |
| `fx` | **35** | 0,12 | 0,24 | 0,015 | **0,08** |
| `bullet` | **39** | 0,53 | 0,24 | **0,493** | 0,22 |
| `ui` | **52** | 0,29 | 0,26 | 0,095 | **0,87** |
| `drones` / `bosses` / `ships` | **114 / 130 / 136** | 0,55 / 0,58 / 0,50 | 0,23 / 0,21 / 0,22 | ≤0,017 | 0,24–0,31 |

⇒ Dùng được: **nền/nhỏ 30–60 màu · chủ thể chính 110–160 màu**; outline đen chỉ **~1 %** — đừng vẽ viền dày.
Gradient p50 **0,20–0,26** ở 5 nhóm chủ thể, **nhưng** `background` **0,12** và `font` **0,09** ⇒ đây là
**mô tả theo nhóm trên mẫu**, **không** phải hằng số toàn cục. `val_std` cũng **không** đồng nghĩa
"độ sâu gradient bóng" — nó chỉ là độ lệch chuẩn độ sáng trên **contact sheet JPEG đã resize**.

**b) Khung hình — "đẹp" ở mức cả màn** (`VISUAL_DESIGN.md` §1–§5, claim **AN1/AN2**)

| Số đo | Giá trị | Đọc thế nào (trên **35 ảnh chụp**, không phải mọi máy) |
|---|---:|---|
| Tương phản (p95−p05) | **0,45 – 0,80** | dưới 0,4 = phẳng · trên 0,8 = chói |
| Accent gameplay | **≤ 10 %** pixel | panel thưởng mới được **~45 %** |
| Độ chi tiết (|ΔRGB| kề) | **13 – 22** | dưới 10 = trống · trên 25 = nhiễu |
| Panel | tỉ lệ **0,67** (≈ 2:3 dọc) | p95 cao **28,4** ⇒ phải chịu danh sách cuộn |
| Juice | flash **0,05 s** · shake **0,10 / 20 frame** · nhịp đòn **0,17 – 0,33 s** | 0 site `timeScale` trên **139** file asm = **mẫu**, không phải toàn build ⇒ **không** kết luận "bản gốc không có slow-mo". Dùng thì ghi là **lựa chọn thiết kế** |

**Test "đẹp" chạy bằng máy** (không cần người chấm): chụp 10 khung gameplay + 3 khung thưởng rồi
`python3 tools/design-metrics.py <thư mục ảnh>` — đạt 4 khoảng ở `VISUAL_DESIGN.md` §5 là đạt.

> Muốn **đổi phong cách** (ví dụ "Ink & Ember" ở `ASSETS.md` §1) thì đổi **hình khối/palette**, nhưng
> **giữ nguyên** bốn chỉ số trên. Đổi cả bốn là làm game khác, không phải làm đẹp hơn.

---

## 4. Đọc theo vai (đừng đọc tuần tự 40 file)

| Vai | Thứ tự |
|---|---|
| **AI/agent dựng game** | file này → `MISSING_FOR_NEW_GAME.md` (13 hệ + **§6 gate 3 stage & khuôn victory**) → `GAMEPLAY.md` §0+§7 → `TUNING_KNOBS.md` → `ENEMY_BEHAVIOUR.md` §6 |
| **Designer / cân bằng** | `GAMEPLAY.md` §0 → `BALANCE.md` §0 → `COMBAT.md` §0 → `ECONOMY.md` §0 → `TUNING_KNOBS.md` |
| **Engineer gameplay** | `GAMEPLAY.md` → `COMBAT.md` → `ENCOUNTERS.md` → `UI.md` → `MISSIONS_STARS.md` |
| **Art / tech art** | `ART_STUDY.md` (số đo mẫu gốc) → `VISUAL_DESIGN.md` (luật khung) → `ASSETS.md` §1 (art direction) + §7 (atlas plan) |
| **Producer** | `COVERAGE_AUDIT.md` → `DONE.md` → `MISSING_FOR_NEW_GAME.md` → `AI_FEASIBILITY.md` §2 |

---

## 5. Mười bốn cái bẫy — đọc trước khi viết design doc riêng

Đây là những chỗ **bộ spec này từng sai thật**, đã sửa; đừng lặp lại:

| # | Bẫy | Đúng |
|---:|---|---|
| 1 | **23.757 "spawner"** | **23.757 = `Σ copies` = số `Call_Data` object** (`class-inventory.csv` khớp); **11.089 = số dòng cấu hình**. Đừng đổi chỗ hai số |
| 2 | "Spawner bị nhân đôi trong export" | Không có. Đó là field `copies`. **Đừng chia 2, đừng dedup theo tên** |
| 3 | `45.659 "quân"` | Chỉ đúng **nếu** `copies` = số bản sao — **mức B** (raw `Call_Data` không có field này) |
| 4 | **92 / 109 / 189 enemy** | 92 = prefab có `Enemy_Datas` · **109 = được spawn** (dùng cái này) · 189 = mọi GO có HP |
| 5 | **67 vs 56 page `sactx`** | 67 theo **tên**; 56 page có `category=atlas` (11 page bị luật tên xếp nhầm) |
| 6 | **4.250 "mảnh"** | **Cận trên**: chỉ **792** mảnh ≥20 px, **158** ≥64 px; 56 % mảnh lớn còn góc caro |
| 7 | `savedStars` = kills | `IsMissionCompleted` = **`savedStars > i`**; kills là đại lượng khác |
| 8 | fallback nhiệm vụ = mode 0 | Fallback là nhánh **`0xb78`** (`csel`), **không** rơi về `0xb80` |
| 9 | "PASS = hiểu hành vi" | PASS chỉ là **số khớp**. Hành vi cần asm/consumer (claim ghi rõ mức A/B/C/D) |
| 10 | 0 xref = không tồn tại | ⇔ **chưa thấy chỗ dùng**, không phải không có |
| 11 | `WaitForSeconds(0)` = cùng frame | **Không** suy được thứ tự thực thi từ đó |
| 12 | "Có timestamp = đã giải script" | Timestamp **chỉ là mốc**, không phải thứ tự/điều kiện (D3 vẫn 🟡) |
| 13 | **0 site trong 139 file asm = không tồn tại** | 139 file là **mẫu**, không phải whole-build closure. Nói "chưa thấy", không nói "không có" — và **cấm** dùng nó để cấm tính năng |
| 14 | **Tỉ lệ 0,4813 = canvas bắt buộc** | Đó là **một thiết bị** (720×1496). Game mới phải **responsive + safe-area**; giữ *quan hệ* (dọc, panel 2:3), không khoá cứng số |

---

## 6. Tự kiểm trước khi tin bất kỳ con số nào

```bash
python3 tools/verify-claims.py                 # 180 PASS · 0 FAIL · 2 SKIP · 0 ERROR
python3 tools/verify-claims.py --only AQ       # riêng nhóm wave/đơn vị
python3 -m unittest discover -s tests -q       # 5 test luật phân loại
python3 tools/data-integrity.py; echo $?       # 0 = không có file gốc nào bị sửa tay
python3 tools/raw-audit.py                     # sổ claim↔raw (RAW/DOC/CONST)
python3 tools/art-study.py                     # dựng lại art-study.csv (2.112 sprite)
python3 tools/design-metrics.py <ảnh>          # đo khung hình bản mới
```

Quy ước mức chắc chắn (**A/B/C/D**) ở `AI_FEASIBILITY.md` §0.0 — mọi dòng trong bộ spec phải ghi
mức, và **số không có mức là số chưa được kiểm**.

> **Luật số (25/10):** số dùng để **quyết định thiết kế** phải là claim **RAW** (tái đo được từ
> `datas/` · `reverse-engineering/` · `docs/assets/`). Số **CONST** trong `RAW_AUDIT.md` là *"đo một lần"* —
> được trích để tham khảo, **không** được dùng để bác một kết luận khác.
