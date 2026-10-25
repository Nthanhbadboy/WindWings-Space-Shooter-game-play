# COVERAGE_AUDIT — kiểm lại **toàn bộ** tài liệu: còn thiếu chỗ nào?

> **Tiêu chí (chủ dự án chốt):** *có đủ tài liệu game để **bắt chước tạo game mới*** — tức dựng lại
> **cơ chế** (L1), **không** cần khớp số, **không** cần art gốc.
>
> File này **không** đánh giá lại bằng cảm nhận. Mỗi dòng là một phép đếm chạy lại được bằng
> `tools/verify-claims.py` (nhóm **P**), hoặc trỏ thẳng vào file dữ liệu.
>
> **Quy mô hiện tại:** **40 tài liệu** trong `docs/spec/` (chưa kể file này) + **30 file dữ liệu**
> trong `datas/` + **176 claim** đã khoá (**174 PASS · 2 SKIP**; nhóm P → AP).

---

## 0. Trả lời ngắn

**Đủ để bắt đầu dựng, thiếu 6 chỗ — và 4/6 không chặn.**

| | Số | Ghi chú |
|---|---:|---|
| Vùng năng lực phải dựng | **14** | §1 |
| Vùng **đủ** (A/B, dựng được ngay) | **10** | vòng lặp · player · súng · enemy · boss · wave · map · độ khó · kinh tế · UI |
| Vùng **thiếu một phần** | **3** | animation điều kiện · FX · âm thanh trigger |
| Vùng **thiếu** | **1** | cảm giác (feel) — phải chạy máy |
| Việc còn thiếu **chặn** dựng | **2** | map→wave numbering · HP runtime theo chế độ |

Nói cách khác: **dựng được bản chơi thử ngay hôm nay**; hai chỗ chặn là **con số hiệu chỉnh**, không
phải **cơ chế**.

---

## 1. Mười bốn vùng năng lực

| # | Vùng | Đủ để dựng? | Bằng chứng (đếm được) | Còn thiếu |
|---:|---|---|---|---|
| 1 | **Vòng lặp / meta** | ✅ **A** | 3 vòng 30 s / 10 phút / 1 tuần · 7 `PlayMode` + 3 `PVPMode` (`GAMEPLAY.md`) | — |
| 2 | **Player / tàu / drone** | ✅ **A** | `Player_Get_Datas` 178 field · 13 drone · `StartHp 2500` | 3 bảng stat **device** (B1, 12 array *chưa chắc* là 12 device) |
| 3 | **Súng / đạn / DPS** | ✅ **A** | 458 `Gun_Attack` (319 thật) · 102 pattern · TTK trong `COMBAT.md` | damage boss ở 19 class director (B6) |
| 4 | **Enemy** | ✅ **A** | 109 prefab roster · 9 component/enemy · 399 đường bay · `Enemy_Movement` 3 nhánh | **điều kiện** chuyển state `Animator` (T4) |
| 5 | **Boss** | ✅ **A** | **46 boss** · 39 prefab `Boss-*` · 793 event có mốc · 8 tên entry + 5 nhánh (boss 1) | hành vi 12 handler (T2) |
| 6 | **Wave / spawn** | ✅ **A** | 282 wave · 11.089 dòng cấu hình · 22.451 entry · schema `Call_Data` 23 field | nghĩa `rate = 0` (B, không chặn) |
| 7 | **Map / stage** | 🟡 **B** | 299 stage · 2 chapter · `maps.json` **250** map | **đánh số map → wave**: chỉ **7/250** chắc (A6) |
| 8 | **Độ khó 3 chế độ** | ✅ **A** | `MaxModeIndex 4` · `kCount ≡ 1` · `pct[mode]` · `levelDelta` | hệ số **HP** theo chế độ (B8) |
| 9 | **Kinh tế / IAP** | ✅ **A** | **170 sản phẩm** (71 consumable + 99 non-consumable) · `stepCommon 0,18` · `DeltaStarCost 50` | — |
| 10 | **Nhiệm vụ / sao** | ✅ **A** | `pct[mode][slot] × countEnemies` · `PercentToCompleteMissions222` | — |
| 11 | **UI** | ✅ **A** cấu trúc · ✅ **A** luật thị giác · **B** cho *vẽ lại* | **125 lớp** · **797 màn** · **150.131 node** · **5.831 nút** · 55.584 file layout · **11 board có bộ đầu vào vẽ** (10.710 node, 100 % `local_pos`, 4.987/5.067 sprite *candidate*, 312/317 key Việt) · gate tutorial native 5/5 | **art** (D) — L1 làm art mới; overlay tutorial **đã có layout** (`UI.md` §9.3: 7 GO + 19 dòng text) — còn thiếu **pixel** (external font/sprite); `Board_Maps` nay **15.334 node / 473 nút** (bản `9edc21f4d`; trần 12.000 của bản trước là `node_limit` của walker ⇒ nay **đọc hết**, không còn là cận dưới) |
| 12 | **Animation** | 🟡 **B** cho **mốc** · **C** cho **điều kiện + hành vi** | 793 event có mốc **trong clip** (không phải thứ tự pha) · nhịp 0,17/0,33/1,0/5,0 s · hit flash 0,05 s | **thứ tự pha + điều kiện vào/thoát** (R1) · **hành vi** handler (T2) · **0/791 keyframe** (cố ý bỏ) |
| 13 | **FX** | 🟡 **B** | **4.845** `ParticleSystem` · ~23 module · scalar + `length_in_sec` + `looping` | **curve** module (chưa đọc) |
| 14 | **Âm thanh** | 🟡 **B** | **92 sound id** → **92/92** resolve ra file (83 sfx + 9 bgm) trên **69** `AudioClip` | **trigger**: âm nào phát ở sự kiện nào (chưa xref) |
| 15 | **Cảm giác (feel)** | ✅ **đóng — không còn thiếu** | **3/6 tồn tại và đã có số**: hit flash (alpha **0,5** + **0,05 s**) · rung (`Enemy_CameraVibrate` 241: **0,10/20 frame** phổ biến nhất) · tỉ lệ rơi (702 = 676 coin + 26 item · 246/2.094 slot · 6 loại) | **3/6 không tồn tại trong game**: hit stop (**0** hàm `timeScale`) · aim assist (**0** hàm aim) · input latency (không phải tính năng) — xem `DESIGN_READINESS.md` §4.1b |

> Bảng có 15 dòng vì "Player" và "Súng/đạn" tách nhau; **14 vùng** ở §0 gộp chúng lại. Dòng 15 (feel)
> **không tính** — đã chốt bỏ theo chỉ đạo; tiêu chí nghiệm thu là **script**, không phải cảm giác.

---

## 2. **Sáu chỗ còn thiếu** — xếp theo "có chặn dựng không"

| # | Thiếu | Chặn? | Chi phí | Ai làm |
|---:|---|---|---|---|
| 1 | **Map → wave**: `maps.json` có **250** map nhưng **đánh số** và **ghép wave** chỉ chắc **7** | **CÓ** (số màn, độ dài phiên) | trung bình | **nhánh dữ liệu** (T6 mới, §2.1) |
| 2 | **HP runtime theo chế độ** (B8) + bảng `Enemy_Get_Datas` | **CÓ** (cân bằng) | thấp | nhánh dữ liệu (đã có 150 entry *tạm thời*) |
| 3 | **Hành vi 12 handler** `*_AnimationEvents` (T2) | không | thấp | nhánh dữ liệu |
| 4 | **Điều kiện `Animator`** của enemy (T4) | không | trung bình | nhánh dữ liệu |
| 5 | **Trigger âm thanh**: 92 id ↔ sự kiện trong code | không | trung bình | nhánh dữ liệu |
| 6 | **Curve `ParticleSystem`** (4.845 hệ) | không | cao | để sau — scalar đã đủ dựng |

**Không tính là thiếu (cố ý bỏ):** 0/791 keyframe Mecanim — hai reader độc lập đều ra **0**, curve
nằm trong `m_StreamedClip` nén. L1 làm art mới nên **không cần**.

### 2.1 Sáu việc này nối vào lô đã giao

`HANDOFF_ANIM_RAW.md` đã có T1–T5. Bảng trên thêm **T6 — map→wave numbering** (mục chặn thứ nhất):

> **Giả định:** `maps.json` (250 map, thứ tự zero-based theo `listMapDatas`) cộng `31-map-tables.md`
> (540 token `InitializeArray` đã giải, 0 token bó tay) là **đủ** để suy ra `map N ↔ sóng nào`.
> **Việc:** đối chiếu 250 mảng với 282 wave bằng **khoá nội dung** (số wave + tổng spawner), không
> bằng thứ tự. **Artifact:** `map-wave-join.json`: `[{map_index, wave_ids[], confidence}]`.
> **Tự kiểm:** số map ghép được **bằng chứng token** (hiện **7**) phải **tăng**, và mọi map ghép
> phải khớp tổng spawner của wave.
> **Lật ngược nếu:** sau khi đối chiếu vẫn **7/250** ⇒ nội dung `maps.json` **không** phải map→wave;
> khi đó phải dùng `14-Data_Boss.csv` (`idWave` per boss, **46 dòng**) làm mỏ neo ngược.

---

## 3. Cái **tưởng thiếu nhưng đã có** — đừng làm lại (mới nhất 24/10)

| Hạng mục | Tài liệu cũ nói | **Thực tế trong repo** |
|---|---|---|
| Kích thước sprite | `DATA_SYNC` §8 #4: *"bị chặn"* | `datas/sprites.csv`: **2.885** sprite, **2.816** có `width/height`; `04-asset-manifest.csv`: **2.907** asset, **2.838** có kích thước |
| Bản địa hoá | chưa có | `12-localization.csv`: **1.416 key × 19 ngôn ngữ**, **1.416** có bản tiếng Việt |
| IAP | "170 SKU" (chưa đối chiếu) | `datas/iap_products.json` = **170**, khớp `13-iap-products.csv` (**71** consumable + **99** non-consumable) |
| Âm thanh | `ASSETS.md`: 69 file | đúng **69** `AudioClip`, nhưng **92 sound id** trỏ vào chúng ⇒ 23 id **dùng chung file** |
| FX | "`ParticleSystem` 4.845 chưa đọc" | `datas/particle_systems.csv.gz`: **4.845** dòng, có `length_in_sec` + `looping` |
| UI layout | "53k file chưa kéo về" | `datas/ui_screens.json.gz`: **55.584** file · **8.437.020** node; `_index.csv`: **797** màn · **150.131** node |
| Boss ↔ wave | "chưa có" | `14-Data_Boss.csv`: **46** boss, mỗi boss có `idWave` |
| Bảng map | "chỉ 7 ghép chắc" | vẫn đúng, nhưng `31-map-tables.md`: **540/540** token có blob, **0** token bó tay ⇒ *nội dung* map là **A−**, chỉ **đánh số** là chưa |

**Một dòng để nhớ `datas/` đang có gì:** **4.845** hệ hạt · **92/92** âm thanh · **150** HP id · **253** boss HP · **250** map · **170** IAP · **1.416** chuỗi.

---

## 4. Bốn cặp số **dễ tráo** — đừng trộn tập rồi ghi một dòng

Đây là lỗi đã xảy ra **6 lần** trong repo này. Bốn cặp dưới đây là chỗ dễ tái phạm nhất:

| Cặp | Số đúng | Nghĩa | Đừng viết |
|---|---|---|---|
| **UI** | **797** màn / 150.131 node | màn **cấp cao** (mỗi dòng = 1 màn) | "797 file layout" — file layout là **55.584** (8,44 M node) |
| **Audio** | **69** `AudioClip` | file trên đĩa | "69 âm thanh" — id mà code dùng là **92** |
| **Sprite** | **2.885** dòng `sprites.csv` | mọi asset đồ hoạ kèm `png` | "2.885 sprite" — trong đó **2.184** `Sprite`, **632** `Texture2D`, **69** `AudioClip` (dòng) |
| **Art** | **62,95 MB** toàn bộ texture | 632 `Texture2D` = **67** page `sactx-*` (31,05 MB) + **565** texture rời (31,94 MB) | "giảm 53 %" — con số đó chỉ đúng cho **page**; tính cả texture rời là **31,05 → 9,0 MB (−71 %)** trên phần page và **62,95 → 40,9 MB (−35 %)** trên toàn bộ. Chi tiết `ASSETS.md` §4.5 |

**Ba mẫu số khác nhau, đừng cộng chéo:** `04-asset-manifest.csv` **2.907** dòng (`Sprite` **2.185** ·
`Texture2D` **653** · `AudioClip` **69**) vs `sprites.csv` **2.885** dòng (**2.184** · **632** · **69**).
Chênh **22 dòng** = 1 `Sprite` + 21 `Texture2D` **không có kích thước**. Muốn nói "bao nhiêu asset" thì
phải nói rõ **file nào**; muốn nói "bao nhiêu px²" thì chỉ dùng `sprites.csv` và ghi rõ là **cận dưới**.

---

## 5. Kết luận

**Đủ để bắt chước dựng game mới ở mức cơ chế.** Bằng chứng không phải lời: **14 vùng** ở §1 có
nguồn dữ liệu đếm được, **10** vùng đã A/B (14 vùng trong phạm vi; feel ⛔ **ngoài phạm vi**), và **6 chỗ thiếu** đều đã có người nhận (5 giao nhánh dữ
liệu qua T2/T4/T5/T6 + âm thanh trigger; 1 để sau).

Hai chỗ **chặn dựng** cần chốt trước khi khoá bảng cân bằng:

1. **map → wave** (T6) — quyết định **số màn** và **độ dài phiên**.
2. **HP runtime theo chế độ** (B8) — quyết định **cảm giác khó**, dù L1 cho phép tự chọn số.

Cả hai đều là **việc của nhánh dữ liệu**, không cần thiết bị. Việc **duy nhất** cần thiết bị vẫn là
**feel** (D1–D4), và nó chỉ cần cho L2/L3.

**Đã hết số ước lượng.** Bản trước §4 của `ASSETS.md` ghi "12 page = 14,7 MB, giảm 53 %" mà **không có
phép đo nào phía sau**; nay đo bằng kích thước thật trong `sprites.csv`: 12 page chứa **18,87 M px² =
9,0 MB** (4 bpp), tức **17 %** lượng px² art của bản gốc. Kế hoạch 12 page **vẫn đúng** — nhưng chỉ khi
**565 texture rời giữ nguyên dạng rời**, và câu "giảm 53 %" phải thay bằng **−71 % cho page / −35 % cho
toàn bộ**. Xem `ASSETS.md` §4.5.
