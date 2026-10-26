# DATA_SYNC — đồng bộ với pipeline vòng 3 (nhánh `arena/ef6b75ef`)

> **asm-check** (bản `6109008c`): **16/17 PASS** · `size_capped` **0/425** · ❌ `RankManager` thiếu **8 B** (`ctor` rỗng) — xem **`ASM_INTEGRITY.md`**. Mọi kết luận phủ định trong file này chỉ đúng trong **17 class đã export**.

> **Không merge.** File này là **kết quả đọc dữ liệu** của nhánh
> `arena/ef6b75ef-windwings-space-shooter-game-p`, commit **`61d5385`**
> (`feat(re): IL2CPP constant extraction (capstone), UI layout dump, raw typetree archive…`).
> Mục đích: ghi lại **cái gì trong `docs/spec/` đã sai** so với dữ liệu mới, và **cái gì vẫn chưa có**.
>
> Áp dụng quy ước `AI_FEASIBILITY.md` §0.0: **A** đo được · **B** suy ra · **C** ước lượng · **D** chưa biết.
> Mục cuối: **Còn thiếu / phải đoán**.

---

## 0. Tóm tắt: pipeline mới bác bỏ 3 kết luận của tôi

| Tôi đã viết | Mức cũ | **Dữ liệu vòng 3** | Mức mới |
|---|---|---|---|
| "69 `AudioClip` nhưng **0 file export được** (FSB5 trong `.resS`)" | D | **69/69 export được WAV** · **571 giây** · **47,6 MB** | **A** |
| "`enemies` trong wave **toàn bộ là `?`** (45.659)" | D | **22.451 entry** (`Σ len`; **45.659** quân khi ×`copies`), **`?` = 0**, **109 prefab** | **A** |
| "Wave `Call_Data` → **không biết enemy nào**" | D | **median 6 prefab/wave** (min 2 · max 28) | **A** |

> Cả ba đều nằm ở nhóm tôi từng gọi là "chưa có đường lấy". **Không phải** — chỉ là **pipeline cũ chưa chạy đúng**.
> Đây là **lần thứ tư** trong phiên tôi kết luận sớm rồi bị dữ liệu lật lại.

---

## 1. Audio — từ "0" lên "đủ dùng"

Nguồn: `docs/assets/audio-index.csv` (69 dòng), `docs/apk-analysis/17-audio-diagnose.md`,
log `18-pipeline-diagnostics.md`.

| Chỉ số | Giá trị (**A**) |
|---|---:|
| Clip | **69** |
| Có `m_Resource` (FSB trong bundle) | **69 / 69** |
| Streamed (`m_StreamData`) | **0** |
| Xuất được WAV | **69** |
| Không xuất được | **0** |
| Tổng thời lượng | **571 s = 9,5 phút** |
| Tổng dung lượng | **47,6 MB** |
| Sample rate | **44.100 Hz** · 1 kênh (mono) |
| Clip dài nhất | **80,09 s** `Action_Dynamic_Track_2_1_MP3` |
| Clip ngắn nhất | **0,08 s** `Sfx_Click_1` |

### 1.1 Nhạc nền — phần đắt nhất — có đủ

| Nhóm | Số clip | Thời lượng |
|---|---:|---:|
| BGM / track nhạc | **8** | **7,9 phút** |

Chi tiết: `Energy_Rock_Track_2_looped_1` 71,6 s · `Energy_Rock_Track_3_looped` 66,5 s ·
`Energy_Rock_Track_2_looped_2` 63,7 s · `Heavy_Riff_5_Looped` 61,8 s ·
`Bgm_Home_1` 51,8 s · `Bgm_Home_2` 44,4 s · `Bgm_Boss_1` 32,3 s · `Action_Dynamic_Track_2_1` 80,1 s.

> **Hệ quả cho kế hoạch:** dòng "thu âm/mua license audio mới" trong `ASSETS.md` §8 **vẫn giữ**
> (bản quyền), nhưng **không còn là ẩn số**: đã biết chính xác cần **9,5 phút**, trong đó
> **7,9 phút nhạc nền** + **~1,6 phút SFX**. Đây là **brief mua/thu chính xác**, không phải ước lượng.

### 1.2 Còn thiếu trong chính dữ liệu audio

| # | Thiếu | Vì sao |
|---:|---|---|
| 1 | `m_Size` khai báo = **0 bytes** cho cả 69 clip | field không serialize; kích thước thật lấy từ FSB header |
| 2 | **23** `SoundClip` không có `AudioClip` tương ứng | 92 entry khai báo vs 69 clip thật — chưa rõ trỏ đâu |
| 3 | Vòng lặp / loop point | không có trong index; cần đọc FSB |

---

## 2. Enemy trong wave — đã resolve

Nguồn: `datas/waves.json` nhánh `ef6b75ef` (ghi ở `docs/conclusions.md` #8).

| Chỉ số | Giá trị (**A**) |
|---|---:|
| Wave | **282** |
| Spawner (đã dedup) | **11.089** (`count_spawners` ở `6ababbd31`; 11.099 ở `8c6da25`) |
| Entry enemy (`Σ len`) | **22.451** |
| Quân thật (`Σ len × copies`) | **45.659** |
| `"?"` | **0** |
| **Prefab enemy khác nhau** | **109** |
| Entry enemy / wave | min **2** · median **63** · max **603** |
| Prefab / wave | min **2** · median **6** · max **28** |

Phân bố 109 prefab: **Boss 39** · CB 33 · CD 15 · W2 6 · XB 5 · GD 4 · BB 4 · H 2 · W1 1.

> **5 prefab phổ biến nhất chiếm 39,0%** tổng entry ⇒ độ đa dạng thật **rất thấp**.
> Chi tiết + top 12: `ENCOUNTERS.md` §2.6.

### 2.1 Khớp với số tôi tự tính

| Chỉ số | Tôi tính (từ bản cũ) | Vòng 3 | Khớp? |
|---|---:|---:|---|
| Dòng cấu hình sau dedup | 10.776 | **11.099** | 🟡 lệch **3%** (khác khoá dedup) — đo lại 25/10 trên `622b700e5`: **10.782** / **11.089** |
| `Boss-` root | 39 | **39** | ✅ |
| Prefab enemy | 92 (đếm từ `Enemy_Datas`) | **109** (đếm từ usage) | 🟡 vòng 3 nhiều hơn **17** |

> Lệch 92 vs 109 là **hợp lý**: 92 là prefab **có dòng trong `Enemy_Datas`**, 109 là prefab
> **được wave tham chiếu**. Hiệu = **17 prefab có trong wave nhưng không có bản ghi HP riêng**
> ⇒ `> Nhận định (mức B):` dùng **109** làm danh sách đầy đủ, **92** làm danh sách có HP.

---

## 3. HP — số dòng tăng 800 → 981, và **tổng HP boss đổi**

Nguồn: `docs/apk-analysis/15-enemy-hp.csv` vòng 3.

| Chỉ số | Bản cũ (`ww-src2`) | **Vòng 3** | Ghi chú |
|---|---:|---:|---|
| Dòng | 800 | **981** | pipeline mới bắt thêm **181** dòng |
| Root prefab | 220 | **258** | +38 |
| **Root `Boss-`** | **39** | **39** | ✅ không đổi |
| Dòng có HP > 0 | 394 | **467** | |
| Median HP | 600.000 | **600.000** | ✅ không đổi |
| HP lớn nhất (1 dòng) | 10.000.000 (`CB(TEST)`) | **10.000.000** (`CB(TEST)`) | ⚠ **object test**, không phải boss |

### 3.1 ⚠ Tổng HP theo boss **thay đổi giữa hai lần chạy**

| Boss | Tổng HP bản cũ | Tổng HP vòng 3 | Lệch |
|---|---:|---:|---:|
| `Boss-39017` | 12.100.000 (15 dòng) | **13.500.000** (21 dòng) | **+11,6%** |
| `Boss-39006` | 11.235.000 (16 dòng) | **13.480.000** (18 dòng) | **+20,0%** |
| `Boss-39015` | 8.500.000 (4 dòng) | **14.500.000** (6 dòng) | **+70,6%** |

> **Đây là bài học quan trọng nhất của file này:** số HP **không ổn định giữa các lần export**.
> Chính `docs/conclusions.md` của nhánh kia ghi: *"Mọi kết luận trong repo này là TẠM THỜI"*.
>
> `> Nhận định (mức B):` nguyên nhân nhiều khả năng là pipeline sau gom **nhiều sub-object hơn**
> vào cùng một root (dòng tăng 15→21, 16→18, 4→6). Nghĩa là **cả hai con số đều đúng** —
> chúng đếm **số bộ phận khác nhau** của cùng một boss.
> ⇒ Không dùng "tổng HP" để so sánh nếu chưa chốt **đơn vị đếm**.

---

## 4. Asset — phân loại thật, thay cho bảng atlas của tôi

Nguồn: `docs/assets/stats.json`, `manifest.csv`, `sprites-index.csv`.

| Nhóm | Số lượng (**A**) |
|---|---:|
| **Tổng asset** | **2.197** · 133,6 MB |
| `unclassified` | **1.554** |
| `atlas` (Texture2D gộp) | **132** |
| `background` | 109 |
| `fx` | 80 |
| `ui` | 73 |
| `audio` | 69 |
| `bullet` | 67 |
| `bosses` | 32 |
| `enemy` | 31 |
| `ships` | **25** |
| `drones` | 13 |
| `font` | 8 |
| `items` | 4 |

Export thật: **Sprite 2.185** file / 48,3 MB · **Texture2D 653** / 64,1 MB ·
**AudioClip 69** / 47,6 MB · **Font 1**.
Contact sheet: **42** ảnh (dùng để review art bằng mắt — tôi chưa có bước này).

> **`ships` = 25 · `drones` = 13 · `bosses` = 32 · `enemy` = 31 · `bullet` = 67 · `items` = 4.**
> Đây là **brief art chính xác** — chính xác hơn bảng `sprite-list.csv` của tôi (163 dòng theo atlas).
> `> Nhận định (mức B):` với L1, brief art nên bám **6 nhóm này** (25+13+32+31+67+4 = **172**
> sprite có vai trò rõ) + `ui` 73 + `fx` 80 + `background` 109 ⇒ **~434** hình có nhãn.
> Khớp với con số **~641** ở `DONE.md` §1.6 (641 là sau khi dedup tên; 434 là số **đã phân loại**).

---

## 5. IL2CPP constants — **vòng 3 thất bại**, không phải thành công

Nguồn: `docs/apk-analysis/19-il2cpp-constants.md`, `reverse-engineering/raw/il2cpp-consts/GameDatas.json`.

| Chỉ số | Giá trị |
|---|---|
| `.so` | **`ls`** ← lỗi: truyền **chuỗi `"ls"`** vào thay vì đường dẫn `libil2cpp.so` |
| Class đích | **1** (`GameDatas`) |
| Method đọc được | **1** (`GetUpgradeCost`) |
| **Hằng số bóc được** | **0** |
| `offset` / `rva` | **0x1000 / 0x1000** — giá trị **mặc định**, không phải địa chỉ thật |
| `bytes` | 1024 — **độ dài buffer mặc định** |

> **Kết luận (mức A):** bước này **chưa chạy đúng**. `GameDatas.GetUpgradeCost` thật nằm ở RVA
> khác (trong `dump.cs`), và `0x1000` là offset của **header ELF**, không phải thân hàm.
> Nghĩa là **bước IL2CPP đó** không đọc được gì — nhưng **đừng** suy ra “957 static không có giá trị”:
> từ 25/10 đường khác **đã đọc được** — `reverse-engineering/il2cpp/ia-resolved.json` có
> **17 method · 623 record** (Player **6/6**, Map **576**, Tech **7**, Device **12**, Droid **3**,
> Stage **2**, GameDatas **1**, `Board_*` **5**). Câu dưới đây là **bản ghi lịch sử**, đã bị thay thế.
>
> Đồng thời: chính `docs/conclusions.md` của nhánh kia xếp mục #12 ở mức **"B→C"**,
> và ghi *"cần đọc control flow, không chỉ hằng số"*.

---

## 6. Cái tôi phải rút lại — và cái **không** đổi

### 6.1 Rút lại

| Câu tôi viết | Vì sao sai |
|---|---|
| "0 `AudioClip` export được" | **69/69** export được, 571 s |
| "enemy trong wave không resolve được" | **22.451** entry, 109 prefab, 0 `?` |
| "`15-enemy-hp.csv` 800 dòng" (như số cố định) | lần chạy mới ra **981**; số này **phụ thuộc pipeline** |
| "HP max boss `39006` = 11.235.000" (như số cố định) | lần chạy mới ra **13.480.000** — cùng boss, khác số bộ phận |

### 6.2 Không đổi

| Điều | Trạng thái |
|---|---|
| **39 root boss** | ✅ giữ nguyên qua 2 lần chạy |
| **Median HP 600.000** | ✅ giữ nguyên |
| **458 `Gun_Attack` → 420 cấu hình** | ✅ không đổi |
| **2.185 Sprite / 653 Texture2D** | ✅ không đổi |
| **9 mesh?** → **2 `Mesh`**, 2.5D | ✅ không đổi |
| **48 archetype spawner** (tôi tự tính) | ✅ khớp với `count_spawners` 11.099 của họ (sai số 3%) |
| ~~**957 `static` field chưa có giá trị**~~ | ❌ **SAI (25/10)** — **623 record** của 17 method đã decode; còn thiếu **bind** + các field vô hướng |
| **4.861 `[SerializeField]` chưa có giá trị** | 🟡 **một phần** — binary nằm trong **pack v2** (report 70); xin giá trị cụ thể qua PR12 |

---

## 7. Ghép chuỗi `wave → prefab → bộ phận` — đứt ở đâu và **vì sao**

Mệnh đề cần kiểm: *"phân tích ngược xong ghép lại là ra hết"*. Kiểm bằng cách **ghép thật**
trên 282 wave, không suy đoán. Kết quả: chuỗi **không đứt ở chỗ tôi tưởng**, và có **hai nguyên nhân khác nhau**
— một cái là **cap của tool**, một cái là **giới hạn dữ liệu thật**.

### 7.1 Bảng ghép thật (282 wave, 109 prefab enemy)

| Mắt ghép | Nguồn | Ghép được | Tỷ lệ | Mức |
|---|---|---:|---:|---|
| wave → prefab enemy | `datas/waves.json` | **109 / 109** | **100%** | **A** |
| prefab → HP | `15-enemy-hp.csv` (981 dòng, bản vòng 3) | **109 / 109** | **100%** | **A** |
| prefab → `Enemy_Datas` | `Enemy_Datas.csv` (981 dòng) | **109 / 109** | **100%** | **A** |
| prefab → movement | `Enemy_Movement.csv` (981 dòng) | **109 / 109** | **100%** | **A** |
| prefab → body physics | `Boss_BodyPhysics.csv` (251 dòng) | **30 / 109** | **27,5%** | **A** |
| prefab → súng | `Gun_Attack.csv` (458 dòng) | **40 / 109** | **36,7%** | **A** |
| **HP + Datas + movement** | | **109 / 109** | **100%** | **A** |
| **HP + movement + physics** | | **30 / 109** | **27,5%** | **A** |
| **đủ cả 4 mảnh** | | **15 / 109** | **13,8%** | **A** |

### 7.1.1 Một lỗi regex đã làm tôi báo sai 93,6% — và cách phát hiện

Bản trước của mục này ghi **102/109 (93,6%)** và kết luận "7 prefab `W1`/`W2` vắng bản chất".
**Sai.** Nguyên nhân: regex nhận mã prefab tôi dùng là

```
^[A-Za-z]{1,4}-\d{5}        # SAI với W1-30031
```

`W1-30031` có **chữ số trước dấu gạch**, nên `[A-Za-z]{1,4}` khớp `W`, rồi đòi `-` nhưng gặp `1` ⇒ **trượt**.
Sửa thành `^[A-Za-z]{1,4}\d{0,2}-\d{5}` thì cả 7 prefab hiện ra, và **HP = 109/109**.

> **Đây là bài học đắt nhất trong phiên:** con số "thiếu 7" trông rất hợp lý, lại khớp đúng một nhóm tên
> cùng họ (`W1`/`W2`) nên tôi đã tin nó là "vắng bản chất". Thực tế là **lỗi của chính phép đếm**.
> Từ đây, mọi phép ghép đều phải thử **đếm số prefab khớp trước khi tính tỷ lệ** — nếu tỷ lệ không phải
> số tròn và nhóm thiếu lại trùng một họ tên, phải nghi regex trước, nghi dữ liệu sau.

> Mắt "súng" phải ghi rõ **đơn vị đếm**, vì hai cách đếm cho hai số khác nhau:
> theo **prefab** = 40/109 (36,7%); theo **dòng component** = 159/458 có path đầy đủ (34,7%),
> cộng 89 dòng đoán được bằng tên con duy nhất ⇒ **248/458 = 54,1%**.
>
> ⚠ **Và mắt này không phải chỗ thiếu cần vá.** `Gun_Attack` là component **dùng chung** cho cả hai phe:
> 172/458 dòng nằm trong prefab enemy (**122 `Boss-*`**, 31 `CD-*`, 16 `CB-*`, 1 `MB-*`, 2 tên số `90048`/`90049`),
> 284 dòng còn lại là path cắt. Về mặt cân bằng, súng của tàu (kể cả drone) chỉ dùng để **ra một con số damage**;
> không cần biết boss nào cầm súng nào để dựng lại cơ chế. Vì vậy **36,7% ở đây là chỉ số phụ**, không phải
> mục tiêu cần đạt 100%.

### 7.2 Nguyên nhân thứ nhất: **cap 800 của `unity_data.py`** — không phải thiếu dữ liệu

Đọc code `tools/apk-analyze/unity_data.py`:

```
MAX_READ_PER_CLASS = int(os.environ.get("MAX_READ_PER_CLASS", "800"))   # dòng 100
MAX_CSV_ROWS       = int(os.environ.get("MAX_CSV_ROWS", "1200"))        # dòng 102
...
if counts[cls] >= MAX_READ_PER_CLASS:      # dòng 222
    skipped_cap[cls] += 1
    continue                                # ← object thứ 801 trở đi BỊ BỎ, không đọc typetree
```

⚠ **Phải tách hai bản dữ liệu** — bản trước tôi gộp làm một và vì thế kết luận sai:

| Class | Tổng thật (`class-inventory`) | **Bản cũ** `821efc5` (`docs/apk-analysis/`) | **Bản vòng 3** (`/tmp/v3`) |
|---|---:|---:|---:|
| `Enemy_Datas` | 981 | 800 (81,5%) | **981 (100%)** ✅ |
| `Enemy_Movement` | 981 | 800 (81,5%) | **981 (100%)** ✅ |
| `Call_Data` | **23.757** | 800 (3,4%) | **1.200 (5,0%)** ⚠ |
| `Gun_Attack` | 458 | 458 (100%) | **458 (100%)** ✅ |
| `Boss_BodyPhysics` | 251 | 251 (100%) | **251 (100%)** ✅ |
| `PointToPoint_Spawner` | **13.292** | 800 (6,0%) | không có file |
| `Path_Spawner` · `PathCreator` · `Spawner` | 1.688 · 1.714 · 1.370 | 800 mỗi bảng | không có file |
| `Enemy_Health` · `Enemy_Controller` · `Enemy_Appear` | 981 · 981 · 914 | 800 | không có file |

**Kết luận đúng:** `MAX_READ_PER_CLASS` **đã được nâng ở vòng 3** — bằng chứng là `Enemy_*` ra **981 > 800**.
Nhưng `MAX_CSV_ROWS = 1200` **vẫn còn cắt `Call_Data`**: 1.200/23.757 = **5,0%**.

> **Nhận định (mức A):** mô tả "cap 800 làm mất enemy" chỉ đúng với **bản cũ**. Trên bản vòng 3,
> ba bảng `Enemy_Datas`/`Enemy_Movement`/`15-enemy-hp` đã **đủ 981 dòng**, và ghép prefab đạt **102/109**.
> Chỗ còn cắt thật là **`Call_Data`** — bảng mô tả **cách wave sinh quân** — và ba bảng spawner không có file vòng 3.
> `datas/waves.json` (22.451 entry) **không** bị ảnh hưởng: sinh bởi `wave_report.py`, script này không cap.

**Điều kiện lật ngược:** nếu `Call_Data` ở vòng 3 thật sự chỉ có 1.200 instance trong file (không phải do cap)
thì `class-inventory` 23.757 đang đếm cả object rỗng — phải đối chiếu `path_id` duy nhất.

### 7.3 Nguyên nhân thứ hai: `gameobject_path(go, depth=10)` — chỉ ảnh hưởng mắt "súng"

`Gun_Attack` **không bị cap** (458/458), vậy 54,1% là **giới hạn thật của dữ liệu path**:

```
def gameobject_path(go, depth=10):           # unity_data.py:128
    tr = _component_transform(go)
    while tr is not None and len(names) < depth:   # ← chặn cứng 10 cấp
        ...
        tr = tr.m_Father.deref_parse_as_object()   # ← dừng khi deref ném lỗi/null
```

Đo trên 458 dòng `Gun_Attack`:

| Chỉ số | Số | Nghĩa |
|---|---:|---|
| path có **tiền tố mã prefab** (`^[A-Za-z]{1,4}-\d{5}`) | **159 / 458 (34,7%)** | ghép trực tiếp được |
| path cắt · tên con **duy nhất 1 prefab** | 89 / 284 (31,3%) | đoán được ⇒ tổng **54,1%** |
| path cắt · tên con **nhập nhằng >1 prefab** | 103 (36,3%) | không quyết được |
| path cắt · tên con **không có trong HP** | 107 (37,7%) | không quyết được |
| path cắt dồn **đúng 10 cấp** | **44 / 284 (15,5%)** | dấu vết `depth=10` |
| độ sâu trung bình path cắt | **5,17 cấp** | phần lớn **không** phải do `depth` |
| `m_GameObject.m_FileID` | **0 ở 100% dòng** | **bác** giả thuyết "parent nằm file khác" |
| `m_GameObject.m_PathID` | **có ở 100% dòng** | khoá join vẫn còn nguyên |

> **Nhận định (mức B):** chỉ **15,5%** path cắt là do chặn 10 cấp; phần còn lại là `m_Father` deref thất bại
> giữa chuỗi (path dừng ở 1–5 cấp). Nâng `depth` lên 50 sẽ chỉ cứu được ~44 dòng, **không** đưa về 100%.
> Điều kiện lật ngược: chạy lại với `depth=50` mà số path đầy đủ tăng **đúng 44** ⇒ xác nhận; tăng nhiều hơn ⇒ sai.

### 7.4 Cái thiếu để mắt "súng" ghép 100% — và nó **lấy được**

Thiếu **một bảng duy nhất**: `Transform` — mỗi instance gồm `path_id`, `m_GameObject.m_PathID`, `m_Father.m_PathID`.
Có bảng đó thì chuỗi là: component → `m_GameObject.m_PathID` → Transform → chuỗi `m_Father` → root → tên prefab.

Căn cứ **lấy được** (mức B, **chưa chạy**):

- **100%** dòng trong cả 5 CSV đều có `m_GameObject.m_PathID` — khoá nối còn nguyên, không phải đoán.
- `m_GameObject.m_FileID` = **0 ở 100%** dòng ⇒ toàn bộ object nằm trong `data.unity3d`, **không có bundle ngoài** phải tải thêm.
- `Transform` + `m_Father` là component chuẩn Unity và **chính tool đã đọc `m_Father`** (dòng 142).
- `reverse-engineering/raw/` hiện **chỉ có 1 file** (`il2cpp-consts/GameDatas.json`) ⇒ bảng Transform **chưa từng được export**, không phải export rồi mất.

**Điều kiện lật ngược:** nếu export bảng Transform xong mà vẫn còn dòng không có `m_Father`, thì các dòng đó là
**prefab lồng** (prefab B nằm trong prefab A) — khi đó phải ghép theo **instance**, cần thêm `PrefabInstance.m_Modification`,
chứ không sửa được bằng `depth`.

### 7.5 Ví dụ dễ ảo tưởng nhất: `CB-30003` dùng súng gì

- `CB-30003` là prefab nhiều nhất game: **2.283 entry** (mức A, `waves.json`).
- Trong `Gun_Attack.csv`: **0 dòng** có path bắt đầu bằng `CB-30003`.
- `Gun_Attack` chỉ có **46 root** (không phải 42 — số cũ đếm thiếu 4 tên có hậu tố/không theo mẫu):
  **26 `Boss-*`**, **11 `CB-*`**, **11 `CD-*`**, **1 `MB-`**, **2 tên số** (`90048`, `90049`), cộng `CD-31005 (1)` và `CD-31002 (1)`.

> **Không được viết "`CB-30003` không có súng".** Mức **B**: `Gun_Attack` đủ 458/458 nên *nếu* `CB-30003`
> có `Gun_Attack` thì nó **phải** nằm trong 458 dòng; nhưng path của nó có thể đã bị cắt nên **không nhìn thấy**.
> Hai khả năng chưa tách được: (a) `CB-30003` không có component `Gun_Attack` (bắn bằng cơ chế khác);
> (b) có, nhưng path cắt nên 0 dòng khớp.
> **Lật ngược:** export bảng Transform rồi join theo `m_PathID`; cái nào ra thì chốt.

### 7.6 Tổng kết: chuỗi đứt ở đâu

| Mắt | Trạng thái | Nguyên nhân | Cách xử |
|---|---|---|---|
| wave → prefab | ✅ 100% | — | — |
| prefab → HP / movement | ✅ 100% | — | — |
| prefab → **HP / movement / Datas** | ✅ **100% (109/109)** | — | — |
| prefab → **body physics** | ⚠ 27,5% (30/109) | boss chỉ 27/39 có component này | không phải lỗi ghép |
| prefab → **súng** | ⚠ 36,7% — **chỉ số phụ** | component dùng chung; súng chỉ để ra damage | không cần vá cho enemy |
| wave → **`Call_Data` chi tiết** | ⚠ 5,0% mẫu | **`MAX_CSV_ROWS=1200`** | chạy lại với `MAX_CSV_ROWS=40000` |
| enemy/boss → **hành vi, đòn đánh** | ❌ **chưa đọc** | 87 class / **7.036 instance** chưa có CSV | xem `BOSSES.md` §6 |

> Hai nguyên nhân **độc lập**. Cap 800 sửa bằng **biến môi trường**, không cần tool mới.
> Bảng `Transform` phải **thêm một bước export**, không có sẵn. Cả hai đều **chưa chạy** — nên đây là
> *"chưa ghép"*, **không phải** *"không ghép được"*.

---

### 7.7 Dữ liệu mới `9033cf7`: `Enemy_Controller` là **hub** — ghép **100%** không cần tên

Bản `9033cf7` thêm **`reverse-engineering/raw/typetrees/*.jsonl.gz`**: 45 class · **24.706 dòng** typetree raw.

Trong đó `Enemy_Controller` **981 dòng** (**981 `path_id` duy nhất** — 1 controller cho 1 enemy).
Mỗi controller khai báo PathID của **9 script con**:

| Field | Trỏ tới | PathID khác nhau | Khớp bảng đã có |
|---|---|---:|---|
| `dataScript` | `Enemy_Datas` | 981 | **981 / 981 = 100%** |
| `healthScript` | `Enemy_Health` | 981 | **981 / 981 = 100%** |
| `movementScript` | `Enemy_Movement` | 981 | **981 / 981 = 100%** |
| `appearScript` | `Enemy_Appear` | 981 | 914 / 981 = **93,2%** |
| `physicsScript` | `Enemy_Physics` | 981 | 0 — chưa export |
| `destroyScript` | `Enemy_Destroy` | 981 | 0 — chưa export |
| `uiScript` | **`Enemy_Display`** | 981 | **981 / 981 = 100%** ⚠ (tôi từng ghi `Enemy_UI` — **class đó không tồn tại**) |
| `burnedScript` | `Enemy_Burned` | 689 | 0 — chưa export |
| `stunScript` | `Enemy_Stun` | 137 | 0 — chưa export |

`appearScript` **93,2% là thật, không phải lỗi**: **67 / 981** enemy không gắn `Enemy_Appear` —
hiện ra ngay, không có hiệu ứng xuất hiện.

`Enemy_Sub` (981 dòng) cũng trỏ `controller` → khớp **981 / 981 = 100%**.

> **Nhận định (mức A) — lật ngược §7.1–§7.6:** không cần `gameobject_path`, không cần `depth=10`,
> không cần bảng `Transform`. Mỗi enemy **tự khai báo PathID của từng bộ phận**.
> Ghép là **tra bảng theo khoá số**, không phải đoán theo tên.
>
> **Hệ quả trực tiếp:** lớp kịch bản #4 (`Enemy_Physics`, trước đây 0%) đã có **981 PathID biết trước**.
> Chỉ cần export `Enemy_Physics` (981 dòng) là lớp đó **0% → 100%**, không phải ghép lại gì.

Bằng chứng phụ: `Enemy_Controller._gameobject` chỉ **378 / 981 (38,5%)** có tiền tố mã prefab —
tức nếu vẫn ghép theo chuỗi tên thì **61,5% sẽ mất**, trong khi ghép theo PathID được **100%**.

### 7.8 Bản `9033cf7`: cap **1.500**, và chỉ còn cắt lớp sinh quân

| Bảng | Tổng thật | `821efc5` | `/tmp/v3` | `9033cf7` |
|---|---:|---:|---:|---:|
| `Enemy_Datas` · `Enemy_Movement` · `Enemy_Sub` | 981 | 800 | 981 | **981** ✅ |
| `Enemy_Health` | 981 | 800 | — | **981** ✅ |
| `Enemy_Controller` | 981 | 800 | — | **981** ✅ |
| `Enemy_Appear` | 914 | 800 | — | **914** ✅ |
| `Wave` | 686 | 800 | — | **686** ✅ |
| `Spawner` | 1.370 | 800 | — | **1.370 (100%)** ✅ |
| `Call_Data` | 23.757 | 800 | 1.200 | **1.500 (6,3%)** ⚠ |
| `PointToPoint_Spawner` | 13.292 | 800 | — | **1.500 (11,3%)** ⚠ |
| `PinMap_Spawner` | 3.165 | 800 | — | **1.500 (47,4%)** ⚠ |
| `Rocket_Spawner` | 2.019 | 800 | — | **1.500 (74,3%)** ⚠ |
| `PathCreator` | 1.714 | 800 | — | **1.500 (87,5%)** ⚠ |
| `Path_Spawner` | 1.688 | 800 | — | **1.500 (88,9%)** ⚠ |

Cap **không còn là 800 mà là 1.500** (6 bảng đúng 1.500 dòng — dấu vết cắt).

> **Nhận định (mức A):** cả 6 bảng bị cắt đều thuộc **lớp sinh quân + đường bay**;
> **không bảng nào thuộc enemy/boss**. Vì `waves.json` đã đếm đủ **23.757 = `Call_Data`**,
> phần cắt này **không làm sai số quân** — chỉ thiếu chi tiết từng spawner.

Hai bảng mới đáng chú ý chưa từng dùng:

| Bảng | Dòng | Field đáng chú ý |
|---|---:|---|
| `Enemy_Health` | 981 | **`noDamage` = True 241 / False 740** ⇒ **24,6%** bộ phận enemy **không nhận damage** |
| `Wave` | 686 | `indexWave` (toàn 0) · `startPoint` + `endPoint` (686/686 có PathID) — đường bay **điểm đầu → điểm cuối** |

`noDamage` là số **chưa có trong bất kỳ file spec nào**: gần **1/4** bộ phận enemy là khiên/giáp/trang trí
không ăn damage — giải thích vì sao bắn vào một số chỗ không mất máu.

### 7.9 Audit mắt ghép — bảng quyết định (bản `de8d9f4`)

Kiểm **bằng phép giao tập PathID**, không suy đoán. 13 mắt, chia 3 nhóm.

**Nhóm A — ghép được 100% (khoá số, không cần tên):**

| # | Mắt ghép | Khoá | Kết quả |
|---:|---|---|---|
| 1 | `Call_Data` → prefab enemy | `listPrefabEnemies[i].m_PathID` ↔ `Enemy_Controller.m_GameObject` | **90 / 90 = 100%** |
| 2 | `Enemy_Controller` → `Enemy_Datas` | `dataScript` | **981 / 981 = 100%** |
| 3 | `Enemy_Controller` → `Enemy_Health` | `healthScript` | **981 / 981 = 100%** |
| 4 | `Enemy_Controller` → `Enemy_Movement` | `movementScript` | **981 / 981 = 100%** |
| 5 | `Enemy_Controller` → `Enemy_Appear` | `appearScript` | 914 / 981 = **93,2%** |
| 6 | `Enemy_Sub` → `Enemy_Controller` | `controller.m_PathID` | **981 / 981 = 100%** |
| 7 | `Call_Data` → `PathCreator` | `pathScript` | 96 / 120 = **80%** |

**Nhóm B — ghép 0%, cùng **một** nguyên nhân: thiếu `Transform`**

| # | Mắt ghép | Thử khoá | Khớp | Thiếu vì |
|---:|---|---|---:|---|
| 8 | `Gun_Attack` (446 GO) → enemy | `m_GameObject` · `parentBarrels` · `iCanAttackParent` | **0** | súng là **object con**, controller nằm ở **object gốc** |
| 9 | `Boss_BodyPhysics` (251 GO) → enemy | `m_GameObject` | **0** | bộ phận là object con |
| 10 | `Stage_Behaviour.bossObj` (250) → enemy | `bossObj.m_PathID` | **0** | trỏ tới object con |
| 11 | `Enemy_Movement.parentRotate` (558) → enemy | `parentRotate.m_PathID` | **0** | trỏ tới object con |
| 12 | `Wave.startPoint` / `endPoint` (686) → `PathCreator` | `startPoint.m_PathID` | **0** | trỏ tới `Transform`, không phải `PathCreator` |

Đã thử **mọi cặp** trong 36 bảng: **không bảng nào chia sẻ `m_GameObject` với `Gun_Attack`**
hay `Boss_BodyPhysics`. Hai bảng này nằm trong **không gian object riêng**, chỉ nối được qua **chuỗi cha–con**.

**Nhóm C — chưa có dữ liệu (không phải lỗi ghép):**

| # | Thứ còn thiếu | Số lượng | Ghi chú |
|---:|---|---:|---|
| 13 | `Enemy_Physics` · `Enemy_Destroy` · `Enemy_Burned` · `Enemy_Stun` | 981 · 971 · 689 · 137 | ✅ **đã export** — xem §7.14 |
| 14 | 34 `*_Director` + 3 `AttackPhases` | **63** | **đã đọc bằng typetree** (§7.22) — không cần chạy pipeline: 112 field damage lấy được ngay |
| 15 | `AnimationClip` · `AnimatorController` | **791** · **308** | manifest chỉ có Sprite + Texture2D |
| 16 | ~~Toạ độ đường bay~~ | — | **ĐÃ CÓ trong raw** — xem §7.11 (CSV chỉ ghi `[10]`) |
| 17 | `Spawner.dataScript` | 1.200 dòng | **cột rỗng** — 0 giá trị, không nối được gì |
| 18 | `Call_Data` đầy đủ | 1.200 / 23.757 = **5,0%** | chỉ phủ **182 / 282 wave** (64,5%) |

### 7.10 Vì sao vẫn còn 5 mắt 0% — và một bảng mở hết

Cả 5 mắt nhóm B đều hỏi cùng một câu: *"object con này thuộc prefab nào?"*.

Chuỗi ghép đúng là: `component` → `m_GameObject` → `Transform` → `m_Father` → … → root → tên prefab.
Bước **`m_Father`** là bước duy nhất chưa có, vì bảng `Transform` (**228.432** object) chưa export.

Bằng chứng nó **lấy được**, không phải phải đoán:

| Kiểm chứng | Số | Ý nghĩa |
|---|---:|---|
| `m_GameObject.m_FileID` | **0 ở 100%** dòng, mọi bảng | object nằm cùng file, không có bundle ngoài |
| path có mã prefab | **37,7–38,4%** ở 5 bảng enemy | tool đã đi lên được một phần |
| path cắt dồn đúng 10 cấp | 44 / 284 = **15,5%** | phần còn lại đứt vì deref, không vì `depth` |
| `Transform` trong `data.unity3d` | **228.432** | đã đếm được, chỉ chưa export |

> **Nhận định (mức B):** một bảng `Transform` (`path_id` · `m_GameObject` · `m_Father`) mở **5 mắt**:
> 458 súng + 251 hitbox boss + 250 `bossObj` + 558 `parentRotate` + 686 điểm đầu/cuối đường bay.
> Đây là **mắt ghép lớn nhất còn thiếu**, và nó không nằm trong lớp kịch bản — nó nằm ở lớp **cấu trúc**.
>
> **Điều kiện lật ngược:** nếu export `Transform` mà `m_Father` vẫn null ở nhiều dòng thì các object đó là
> **root của prefab lồng** (`PrefabInstance`) — khi đó cần thêm `PrefabInstance.m_Modification` mới nối được.

**Cách ghép hiện tại nếu không có `Transform`:** dùng chuỗi `_gameobject` → chỉ **~38%**, và **38% là trần
cứng**, không phải 54% như tôi từng báo (con số 54,1% là *trong tập có path*, không phải *toàn bộ 458*).

### 7.11 Dữ liệu thô vs CSV — CSV **làm phẳng list**, raw thì không

Một phần "thiếu" trước đây là do **bộ ghi CSV**, không phải do dữ liệu. Kiểm bằng cách đọc lại
`reverse-engineering/raw/typetrees/*.jsonl.gz` (cùng object, chỉ khác cách xuất).

| Trường | CSV | Raw JSONL | Chênh |
|---|---|---|---|
| `PathCreator.editorData._bezierPath.points` | **`[10]`** (chỉ số phần tử) | **10 × `{x, y, z}`** đầy đủ | **mất toàn bộ hình học** |
| `Enemy_Movement.listSpeeds` | `listSpeeds[0]` = 5,0 | `[5.0]` hoặc **`[5.0, 12.0]`** | mất **137** trường hợp đổi tốc độ |
| `Gun_Attack` | 39 cột phẳng | có `allGunDatas` lồng + `shootAudioClipName` + `isStunned` | — |

### 7.11.1 Đường bay — đọc được **đầy đủ toạ độ**

`PathCreator` **1.500** bản ghi (tổng thật 1.714 — bị cap), **0 bản ghi thiếu `points`**.

| Thuộc tính | Số |
|---|---|
| Số điểm/đường | 4 (**186**) · 7 (**441**) · 10 (**401**) · 13 (**120**) · 16 (**196**) · 19–55 (phần còn lại) |
| Nhiều điểm nhất | **55** (16 đường) |
| Độ dài đường | min **2,77** · median **38,7** · max **228,7** đơn vị Unity |
| Tổng chiều dài | **68.422** đơn vị |

Điểm đầu của đường thứ nhất: `(8,12, 7,37)` — nằm **trong** khung chơi 20×25, đúng như một điểm khởi hành.

**Quy ra thời gian bay** (chia cho tốc độ, `Enemy_Movement.listSpeeds`) — đây là số quyết định *cảm giác*:

| Tốc độ | Đường median 38,7 | Đường dài nhất 228,7 |
|---:|---:|---:|
| 1,0 | **38,7 s** | 228,7 s |
| 5,0 (median) | **7,7 s** | 45,7 s |
| 20,0 | 1,9 s | 11,4 s |

> **Nhận định (mức A):** một con enemy bay hết đường median mất **7,7 giây** ở tốc độ 5,0.
> Cộng nhịp spawn **1,0 s** ⇒ trên màn hình luôn có **~7–8 con** cùng lúc. Đây là con số dựng lại
> được **cảm giác** mà không cần chạy game.

### 7.11.2 `listSpeeds` — **137 con đổi tốc độ giữa đường**

| Số phần tử `listSpeeds` | Số enemy |
|---|---:|
| 1 | **844** |
| 2 | **137** |

CSV chỉ xuất `listSpeeds[0]` ⇒ 137 con này bị đọc thành **một tốc độ duy nhất**, mất khúc tăng/giảm tốc.
Raw giữ cả mảng.

> **Điều kiện lật ngược:** nếu 2 phần tử là `[tốc độ, thời điểm]` chứ không phải 2 chặng, thì đây là
> **thời gian chờ**, không phải đổi tốc độ. Cần đọc `Enemy_Movement` thân hàm để chốt — hiện chỉ có field.

### 7.11.3 Nối đường bay vào wave — chỉ 8,3%

| Mắt | Số | Khớp |
|---|---:|---|
| `Call_Data` có `pathScript` | 124 / 1.500 = **8,3%** | — |
| `pathScript` → `PathCreator.path_id` | 124 | **100 (80,7%)** |

Khớp với `waves.json`: chỉ **861 / 11.099 spawner** là `spawn_type = path` (**7,8%**) — cùng bậc độ lớn.
⇒ **92% enemy không đi theo đường Bezier**, chúng đi theo `point_range`/`point` (thẳng tới điểm đích).

Ba lớp spawner (`Spawner` 1.370 · `Path_Spawner` 1.500 · `Waypoints_Spawner` 1.151) đều có
**`dataScript` = 0 ở 100% dòng** ⇒ liên kết spawner → dữ liệu **được gán lúc chạy**, không serialize.
Đây là mắt ghép **thật sự thiếu**, không phải do cap.

### 7.12 Đã dịch ngược được bao nhiêu — **5 thước đo**, không có một con số duy nhất

Cùng một kho dữ liệu, tuỳ **đơn vị đếm** mà ra 5 tỷ lệ khác nhau. Tất cả đều tính từ số đếm được,
không phải tự đánh giá.

| # | Thước đo | Tổng | Đã đọc | % |
|---:|---|---:|---:|---:|
| 1 | **Class** (theo `class-inventory`) | **677** | **45** | **6,6%** |
| 2 | **Instance `MonoBehaviour`** | **125.452** | **61.341** | **48,9%** |
| 3 | **Object trong `data.unity3d`** (mọi type) | **717.262** | **64.312** | **9,0%** |
| 4 | **Lớp enemy/boss** (16 class) | **11.081** | **6.528** | **58,9%** |
| 5 | **Method body IL2CPP** | **68.893** | **305** | **0,44%** |

Nguồn: `class-inventory.csv` (677 class / 125.452 instance) · `04-unity-assets.md` (717.262 object) ·
`reverse-engineering/raw/typetrees/` (45 class) · `19-il2cpp-constants.md` (12 class / 305 method).

**Vì sao 5 con số lệch nhau xa:**

- **6,6%** thấp vì 677 class gồm **~590 class UI/utility** (nút, text, pool) — đọc hết cũng không giúp hiểu gameplay.
- **48,9%** cao vì vài class được đọc có **rất nhiều instance** (`Enemy_*` 981 × 5, `Call_Data` 1.500…).
- **9,0%** thấp vì `Transform` (**228.432**) và `SpriteRenderer` (**62.815**) chiếm 40,6% số object và **chưa đọc**.
- **58,9%** là thước đo **đúng nhất cho câu hỏi "hiểu enemy/boss chưa"**.
- **0,44%** là thước đo **hành vi**: biết field ≠ biết công thức. Đây là trần thật của "hiểu game".

### 7.12.1 Lớp enemy/boss — 58,9%, và 41,1% còn lại là gì

| Class | Instance | Trạng thái |
|---|---:|---|
| `Enemy_Controller` · `Enemy_Datas` · `Enemy_Health` · `Enemy_Movement` · `Enemy_Sub` | 981 × 5 | ✅ đọc |
| `Enemy_Appear` | 914 | ✅ đọc |
| `Gun_Attack` | 458 | ✅ đọc |
| `Boss_BodyPhysics` | 251 | ✅ đọc |
| **`Enemy_EfxDestroyed`** | **1.134** | ❌ chưa |
| **`Enemy_Physics`** | **981** | ❌ chưa — **PathID đã có** |
| **`Enemy_Destroy`** | **971** | ❌ chưa — PathID đã có |
| **`Enemy_Burned`** | **695** | ❌ chưa — PathID đã có |
| `Enemy_LookAtPlayer` | 391 | ❌ chưa |
| `Enemy_CameraVibrate` | 241 | ❌ chưa |
| `Enemy_Stun` | 140 | ❌ chưa — PathID đã có |

### 7.12.2 63,2% instance chưa đọc — nhưng phần lớn **không phải gameplay**

| Class chưa đọc | Instance | Loại |
|---|---:|---|
| `Call_Point` | **23.757** | **gameplay** — cùng số với `Call_Data`, nghi 1 điểm spawn / 1 `Call_Data` |
| `TextMeshPro` | 9.789 | UI text |
| `ButtonEvents` · `Button_Sound` | 6.147 | UI |
| `LanguageTextMeshPro` | 2.440 | UI đa ngữ |
| `ObjectPool` | 2.333 | hạ tầng |
| `Obj_Collider` | 1.623 | va chạm phụ |
| `Enemy_EfxDestroyed` | 1.134 | hiệu ứng chết |

⇒ Trong 8 class chưa đọc lớn nhất, chỉ **2** là gameplay (`Call_Point`, `Enemy_EfxDestroyed`);
**6** là UI/hạ tầng.

### 7.12.3 Nếu tính theo **lớp dữ liệu gameplay** (bảng, không phải class)

| Nhóm bảng | Tổng dòng | Đã đọc | % |
|---|---:|---:|---:|
| Enemy/boss (5 bảng chính) | 4.905 | **4.905** | **100%** |
| Súng + va chạm | 709 | **709** | **100%** |
| Wave | 686 | **686** | **100%** |
| Đường bay | 1.714 | 1.500 | **87,5%** |
| Sinh quân (`Call_Data` + 5 bảng spawner) | **45.291** | **8.870** | **19,6%** |

> **Nhận định (mức A):** bức tranh phụ thuộc **câu hỏi**, không phụ thuộc "độ hoàn chỉnh":
> **enemy/boss = 58,9%** (thiếu lớp hành vi), **dữ liệu tĩnh của enemy = 100%**,
> **sinh quân = 19,6%** (cap), **hành vi = 0,44%**.

> **Điều kiện lật ngược:** nếu `Call_Point` chứa chính nội dung mà `Call_Data` bị cắt, thì đọc nó
> đưa **sinh quân từ 19,6% lên ~100%** mà không cần bỏ cap. Chưa kiểm vì `Call_Point` chưa vào `TARGETS`.

### 7.13 ⚠ Con số **45.659 quân** là mức B, không phải mức A

`copies` trong `waves.json` = **số spawner giống hệt nhau bị gộp** (dedupe), và
"quân" = `len(listPrefabEnemies) × copies`. Nhưng phân bố list cho thấy vấn đề:

| Số prefab trong `listPrefabEnemies` | Số spawner (đã nhân `copies`) |
|---|---:|
| 0 (list rỗng) | **688** |
| **1** | **18.261 (76,9%)** |
| 2 | 874 |
| 3–10 | 3.363 |
| 11–68 | 571 |

⇒ **4.808 spawner khai báo list ≥ 2**, có cái tới **68 prefab**. Hai cách đọc:

- **Nếu list là danh sách spawn tuần tự** → **45.659 quân** (cách tôi đang ghi).
- **Nếu list là pool để chọn** → chỉ **23.757 quân** (1 con/spawner), hoặc pool chọn N.

`number` (field đếm) = **0 ở toàn bộ 23.757 spawner**, nên **không có số lượng tường minh**
để phân xử. Cần thân hàm `Spawner`/`Call_Data` — hiện chỉ có field.

> **Điều kiện lật ngược:** nếu 76,9% spawner chỉ có 1 prefab thì sai số chỉ nằm ở 23,1% còn lại;
> nhưng nếu list là pool thì **mọi con số quân** (45.659 · 22.417 entry · 131,5 quân/wave) **phải chia lại**.
> Chưa kết luận được — và đây là chỗ dễ tự phong nhất trong toàn bộ hồ sơ.

### 7.14 Bản `bb97453`+`d84ea72`: Transform tree + lớp hành vi — **kết quả chạy thật**

Nhánh dữ liệu áp dụng **toàn bộ** audit: thêm lớp hành vi vào `TARGETS`, ghép Director theo
hậu tố, nâng cap, xuất `Transform`, sửa CI. Run `39879117958` xong trong **4 phút 01 giây**
(trước **11 phút 00**) — **−63%**, vì `REA` chuyển thành opt-in.

`typetree` từ **45 → 110 class**. Dưới đây là số đọc từ dữ liệu đó.

#### 7.14.1 `Transform` — mở được mắt ghép nhưng **không phải 100%**

`transform-tree.tsv.gz`: **228.432** Transform · **2.089** root (`m_Father = 0`).

| Mắt | Trước | Sau | Cách ghép |
|---|---:|---:|---|
| `Gun_Attack` → có Transform | 0 | **458 / 458 = 100%** | tra `m_GameObject` |
| `Boss_BodyPhysics` → có Transform | 0 | **251 / 251 = 100%** | nt |
| `Enemy_Sub` → `Enemy_Controller` | 100% | **981 / 981 = 100%** | tổ tiên |
| **`Gun_Attack` → `Enemy_Controller`** | **0** | **438 / 458 = 95,6%** | leo tổ tiên |
| **`Boss_BodyPhysics` → `Enemy_Controller`** | **0** | **189 / 251 = 75,3%** | leo tổ tiên |
| (cách khác) ghép theo **root tuyệt đối** | — | Gun **455 (99,3%)** · Body **219 (87,3%)** | |

Hai cách cho kết quả **khác nhau** vì một số Transform nằm trong prefab lồng: leo tổ tiên thấy
controller ở giữa chuỗi, còn root tuyệt đối thì vượt quá. **Không cách nào 100%.**

20 súng không ghép được nằm ở `Board_FightBoss/…/Parent_Bosses/Boss 3/…` — súng **trên màn UI
chọn boss**, không thuộc enemy nào. Tức phần lớn "không ghép được" là **dương tính giả của bộ đếm**,
không phải dữ liệu thiếu.

> **Nhận định (mức A):** kết luận `> 1 bảng Transform mở cả 5 mắt` của tôi (§7.10) **đúng một nửa**:
> nó mở được chuỗi, nhưng **không đạt 100%** vì prefab lồng và vì có object UI dùng chung kiểu component.
> Mức đúng là **75–99%**, không phải 100%.

#### 7.14.2 ⚠ `Enemy_Physics` — đọc rồi mới biết **nó không chứa damage**

| Class | Dòng | Field | Giá trị thật |
|---|---:|---|---|
| `Enemy_Physics` | **981** | **2** | `autoCacheColliders = False` **981/981** · **`allColliders = []` 981/981** |
| `Enemy_Destroy` | 971 | 3 | `pointBurst` · `isNoPool` · `delayDestroy` |
| `Enemy_Burned` | 695 | 2 | `pointEffect` · `allDestroyEffects` |
| `Enemy_Stun` | 140 | 3 | danh sách `Gun_Attack` gây choáng |
| `Enemy_LookAtPlayer` | 391 | **14** | `lerpAngleSpeed` · `lerpSpeed` · `minAngle`/`maxAngle` · `offsetAngle` |

**`Enemy_Physics` rỗng.** Mảng collider **không được serialize** — nó được cache lúc chạy
(`autoCacheColliders`). Damage va chạm **không nằm ở đây**; nó nằm trên `Collider2D`/`Damager`
hoặc trong `Enemy_Datas`.

> **Nhận định (mức A) — tôi đã sai:** tôi khẳng định "export `Enemy_Physics` mở khoá **85,8% entry**
> damage". Đọc xong thì class này **0 field damage**. Điều kiện lật ngược tôi tự đặt ra ở §7.12
> (*"nếu field rỗng thì lớp này không cứu được"*) **đã xảy ra**.
>
> Bài học ghi lại: **PathID có sẵn ≠ nội dung có sẵn.** Một class tồn tại 981 lần không có nghĩa
> nó chứa số; phải đọc mới biết.

#### 7.14.3 `Call_Point` — **mắt nối lớn nhất đã tìm ra**

| Số | Giá trị |
|---|---:|
| `Call_Point` | **23.757** |
| Có `dataScript` trỏ tới | **23.757 / 23.757 = 100%** |
| Khớp `Call_Data.path_id` | **23.757 / 23.757 = 100%** |
| Khớp `Spawner` / `Path_Spawner` / `PointToPoint_Spawner` | **0** |
| `warningPoints` | 2 field còn lại |

⇒ Mỗi `Call_Data` có **đúng 1** `Call_Point`, và `Call_Point` **không** trỏ tới spawner nào.
Nghĩa là `Call_Data` (bị cap 1.500/23.757) **là** bảng gốc, và `Call_Point` chỉ là **điểm đánh dấu
trên bản đồ** — không chứa phần dữ liệu bị cắt.

> **Điều kiện lật ngược trong §7.12.3 đã được trả lời:** đọc `Call_Point` **không** đưa sinh quân
> từ 19,6% lên 100%. Muốn đủ 23.757 vẫn phải **bỏ cap** `Call_Data` (đã nâng lên 30.000 trong `CAP_OVERRIDES`).

#### 7.14.4 37 Director — **63 instance, và đúng là bảng pha**

| Field xuất hiện nhiều nhất | Số Director có |
|---|---:|
| `animatorParent` | **37 / 37** |
| `animEvents` | 33 |
| `parentDestroy` | 28 |
| `targetLayer` | 27 |
| `lookatPlayer` | 24 |
| `allHpParents` | 21 |
| `allObjColliders` | 19 |

Danh sách dài nhất: `Boss11_Director.allHandPoints` **12** · `MB9_Director.listChilds` 11 ·
`Boss17_Director.allBeeAttack4/5` 10.

⇒ `animatorParent` ở **cả 37** ⇒ mọi Director đều có **state machine riêng** điều khiển pha.
`animEvents` 33/37 ⇒ **33 boss pha được điều bằng animation event**, khớp §3 của `ANIMATION.md`.

**Vẫn thiếu:** Director **không** chứa thời lượng pha — nó giữ **tham chiếu** (`animatorParent`,
`animEvents`) trỏ tới `AnimatorController` (308) và `AnimationClip` (791), hai loại **chưa export**.
Lớp pha boss giờ **biết cấu trúc nhưng chưa biết nhịp**.

### 7.15 ⚠ **981 không phải "981 enemy"** — và tôi đã trích sai suốt 3 vòng

Với `transform-tree` + `prefab-roots.csv` (2.081 root), lần đầu **leo được 100%** `Enemy_Controller`
về prefab gốc. Kết quả đổi cách hiểu cả bộ số:

| Nơi chứa `Enemy_Controller` | Số | Loại |
|---|---:|---|
| **`Boss-*`** | **318** | prefab boss |
| **`Wave_*`** | **288** | prefab wave (enemy giữ sẵn trong wave) |
| **`Board_SelectBoss`** | **126** | ⚠ **mô hình trưng bày ở màn CHỌN boss** — không xuất hiện trong trận |
| `Board_FightBoss` | **70** | màn đánh boss |
| `Board_Players` · `Board_Maps` | 8 | UI |
| prefab lẻ khác | 171 | lẻ |
| **Tổng** | **981** | leo được **981 / 981 = 100%** |

> **Nhận định (mức A) — tôi phải rút lại cách gọi "981 enemy":** 981 là **số instance
> `Enemy_Controller` trong prefab**, không phải số enemy trong trận. **≥126 (12,8%) là mô hình UI**.
> Con số "enemy dùng được" nằm trong khoảng **777–855** cho tới khi đối chiếu `Board_FightBoss` runtime.
>
> Chỗ này **không đổi** kết luận thiết kế (phân bố tốc độ, turret, `Stop` 94,2%) — đổi **nhãn**:
> mọi bảng `Enemy_*` về sau phải ghi *"981 dòng dữ liệu, trong đó ≥126 là mô hình UI"*.

**Hệ quả cho các số đã công bố:**

| Số đã ghi | Đúng/Không |
|---|---|
| `listSpeeds[0]`: 562 × 5,0 · 123 × 1,0 · 118 × 20,0 · median 5,0 · max 30,0 | ✅ **đúng, xác nhận lại trên 981** |
| `isTurret` 112 · `facingMove` 949 | ✅ đúng |
| `listSpeeds` 2 phần tử = **137** | ✅ đúng |
| "**981 enemy**" | ❌ **sai nhãn** — 981 bản ghi, ≥126 là mô hình UI |

### 7.16 `uiScript` → `Enemy_Display`, **không có class `Enemy_UI`**

| Kiểm | Kết quả |
|---|---|
| `Enemy_Controller.uiScript` (981 PathID) ∩ `Enemy_Display` | **981 / 981 = 100%** |
| `Enemy_UI` trong 677 class | **KHÔNG TỒN TẠI** |

⇒ Chữ "UI" trong tên field `uiScript` nghĩa là **hiển thị trong game** (renderer, thanh máu), không phải UI menu.
Tôi suy class từ tên field — **sai**. Bài học: **không suy tên class từ tên field**.

`Enemy_Display` (981) có dữ liệu thật, chưa từng đọc:

| Field | Phân bố |
|---|---|
| `appearOff` | **921 True** · 60 False ⇒ **93,9%** enemy tắt hiệu ứng xuất hiện |
| `hitableRenderers` | **0 → 367** · **1 → 531** · 2 → 33 · 3 → 23 · 4 → 14 · 5 → 3 · 13 → 6 · 31 → 4 |

> **Nhận định (mức A):** **367 / 981 (37,4%) enemy có 0 renderer "có thể bắn trúng"**.
> Cộng `Enemy_Health.noDamage = True` **241/981 (24,6%)** ⇒ đây là hai cơ chế **khác nhau**:
> một cái quyết định **có bắn trúng được không**, một cái quyết định **trúng rồi có mất máu không**.
> Muốn tái tạo cảm giác "bắn vào đâu cũng trúng" phải dùng **cả hai**, không phải `Enemy_Physics`.

### 7.17 `appearScript` → **51 class `*_Director`** — mắt nối boss → đạo diễn

`Enemy_Controller.appearScript` không chỉ trỏ `Enemy_Appear`:

| Class đích | Số |
|---|---:|
| `Enemy_Appear` | **914** |
| **51 class `*_Director`** (`BossN_Director` · `MBN_Director` · `MB6_ChildDirector`) | **67** |
| Tổng | **981** |

⇒ **Boss không dùng `Enemy_Appear`** — nó trỏ thẳng tới đạo diễn pha. Đây là mắt nối
**boss → Director** mà trước đó phải ghép bằng tên prefab.

**Vì sao quan trọng:** giờ biết **chính xác boss nào dùng Director nào**, không đoán.
37 class Director / 63 instance đã export (§7.14.4) — ghép được vào từng `Boss-*`.

### 7.18 `Call_Data` **đầy đủ 23.757** — và map được enum `spawnType`

Cap đã nâng, dữ liệu đã về đủ:

| Kiểm | Số |
|---|---:|
| `Call_Data` | **23.757** (trước 1.500) |
| Tổng `len(listPrefabEnemies)` | **45.659** — khớp đúng số tôi tính từ `waves.json` |
| `number` = 0 | **23.757 / 23.757** (100%) |
| `editType` = 0 | **23.757 / 23.757** (100%) |
| Số wave khác nhau | **281** |

**`spawnType` — map được sang nhãn trong `waves.json`:**

| `spawnType` | Số | % | Nhãn tương ứng (`waves.json`) |
|---:|---:|---:|---|
| **2** | **16.498** | 69,4% | `point_range` (68,0%) |
| **0** | **4.199** | 17,7% | `point` (18,8%) |
| **1** | **1.688** | 7,1% | `path` (7,8%) |
| **6** | **686** | 2,9% | `boss` (2,9%) |
| **5** | **686** | 2,9% | `special` (2,5%) |

Tỷ lệ khớp trong sai số 1,4 điểm ⇒ **enum `spawnType` đã giải mã**: `0 = point` · `1 = path` ·
`2 = point_range` · `5 = special` · `6 = boss`. Đây là mục §7 câu hỏi #5 của `SCRIPTS.md` — **đóng**.

> **Nhận định (mức A):** `number = 0` ở **toàn bộ 23.757** và `editType = 0` ở toàn bộ.
> Nghĩa là **không có số lượng tường minh** trong bất kỳ spawner nào ⇒ câu hỏi
> "45.659 quân hay 23.757 quân" (§7.13) **không giải được bằng dữ liệu serialize**;
> phải đọc thân hàm. Mức vẫn là **B**.

### 7.19 `prefab_joins` (bản `e162065`) — 7 mắt ghép **100%**, và 18% trong đó là **UI**

`datas/prefab_joins.csv.gz`: **3.870 dòng** · cột `class · field · component_path_id · target_path_id · prefab_root`.

| Class.field | Dòng | Tỉ lệ |
|---|---:|---:|
| `Enemy_Controller.m_GameObject` | **981** | **100%** |
| `Wave.startPoint` | **686** | 100% |
| `Wave.endPoint` | **686** | 100% |
| `Enemy_Movement.parentRotate` | **558** | 100% |
| `Gun_Attack.m_GameObject` | **458** | 100% |
| `Boss_BodyPhysics.m_GameObject` | **251** | 100% |
| `Stage_Behaviour.bossObj` | **250** | 100% ⚠ **cả 250 đều thuộc `Board_Maps`** — là **icon boss trên bản đồ stage**, không phải prefab boss |
| **Tổng** | **3.870** | |

**453 prefab root khác nhau.** Trong đó **699 / 3.870 = 18,1%** thuộc `Board_*`.

> ⚠ **Mắt `Stage_Behaviour.bossObj` nối được nhưng nối vào UI:** **250 / 250** đều có root
> `Board_Maps`, và target khớp **100%** cột `gameobject` của `transform-tree` ⇒ đây là **icon boss
> trên bản đồ chọn màn**, không phải boss trong trận. Đừng dùng nó để đếm boss.

#### 7.19.1 ⚠ 30% số súng là **súng preview trên màn UI**

| Nguồn `Gun_Attack` | Số | % |
|---|---:|---:|
| `Board_SelectBoss` (màn **chọn** boss) | **73** | 15,9% |
| `Board_FightBoss` (màn đánh boss) | **66** | 14,4% |
| **Tổng UI preview** | **139** | **30,3%** |
| **Prefab thật (trong trận)** | **319** | **69,7%** |

Tương tự `Boss_BodyPhysics`: **251 → 185 thật** (66 dòng là hitbox trên màn UI).
`Enemy_Controller`: **981 → 777** không thuộc `Board_*`.

#### 7.19.2 Sửa số súng theo prefab: **42 → 68**

| | Số cũ (spec) | Số đúng (bản `e162065`) |
|---|---:|---:|
| Prefab **boss** có súng | 21 | **26** |
| Prefab **không phải boss** có súng | 19 + 2 object = 21 | **42** |
| **Tổng prefab có súng** | **42** | **68** |
| Tổng súng | 458 (gồm UI) | **319 thật** (+139 UI) |

Phân họ 68 prefab thật: **Boss 26** · `Wave_*` + `BLT_*` **22** · `CD` 13 · `CB` 6 · `BB` 1.

> **Nhận định (mức A):** số cũ 42 sai vì tôi đếm theo **tiền tố tên trong `_gameobject`** — chỉ phủ **38%** số dòng.
> Ghép theo `Transform` cho ra **68**, và phát hiện thêm: **súng nằm cả trong prefab `Wave_*`**
> (`Wave_0005` có **12** súng) — điều mà cách ghép theo tên **không thể thấy**.
>
> Top prefab nhiều súng: `Boss-37006` **41** · `Boss-39006` 29 · `Boss-39010` 29 · `Boss-39004` 18 ·
> `Wave_0005` 12 · `Boss-39002` 12.

**Điều kiện lật ngược:** nếu súng trong `Board_FightBoss` thật sự là súng boss dùng trong trận
(boss được đặt sẵn trên màn thay vì spawn) thì 66 dòng đó **không phải nhiễu** — khi đó 319 là **thiếu**,
phải cộng lại. Cần đối chiếu runtime.

### 7.20 Hệ quả của `transform-tree`: **turret có hai tầng**, và 69 prefab chưa từng xuất hiện

Ghép `Enemy_Movement` về prefab gốc qua `Enemy_Controller.movementScript` → `prefab_root`
(**981/981 map được, 0 dòng mồ côi**).

#### 7.20.1 178 prefab gốc mang `Enemy_Controller` — chia đúng 6 nhóm

| Nhóm | Số | Ghi chú |
|---|---:|---|
| **Xuất hiện trong wave** | **109** | khớp **chính xác** 109 tên prefab trong `Call_Data` |
| `Wave_*` container | **35** | màn chơi mang sẵn enemy/turret, không phải prefab spawn |
| **Họ enemy nhưng chưa dùng** | **22** | xem §7.20.3 |
| Mã số `900xx` (effect) | 7 | `90027` · `90045` · `90047` · `90048` · `90049` · `90050` · `90051` |
| `BLT_*` (đạn) | 3 | `80109` · `80177` · `80178` |
| `CB(TEST)` + `Ship` | 2 | |
| **Tổng** | **178** | |

`109` khớp đúng danh sách wave ⇒ `Call_Data` và `transform-tree` **kiểm chéo lẫn nhau**, không có prefab nào bị bỏ sót.

#### 7.20.2 Turret — **112 component, 44 prefab, hai tầng**

| Tầng | Prefab | Component | Sinh ra thế nào |
|---|---:|---:|---|
| **Spawn qua `Call_Data`** | **21** | **41** | như enemy thường |
| **Đặt sẵn trong prefab `Wave_*`** | **23** | **71** | gắn thẳng vào màn, **không** spawn |

Tầng spawn: `CD` **15** (`31002`–`31016`) · `GD` **4** (`33002`–`33005`) · `H` **2** (`38001`, `38002`).
Tầng đặt sẵn: **21 prefab `Wave_*`** + `Ship` + `CD-31017` (có turret, **chưa dùng ở wave nào**).

Dày nhất: `Wave_0005` **22 turret** · `Wave_0004` **14** · `Wave_0020` **4**.

> **Nhận định (mức A):** **71 / 112 turret (63,4%) không do wave sinh ra.**
> Đọc `Call_Data` **không thấy** chúng — chỉ đọc `Enemy_Movement` của prefab `Wave_*` mới thấy.
> Đây là lý do bản trước của tôi (đếm theo tên prefab trong wave) chỉ ra **22 prefab**: nó **không thấy tầng đặt sẵn**.

#### 7.20.3 Ba số turret phải sửa

| Tôi đã ghi | Đúng | Vì sao sai |
|---|---|---|
| **22 prefab** turret | **21** spawn (+ `CD-31017` dự phòng) | đếm `CD-31017` dù nó không xuất hiện ở wave nào |
| "`W2` có **1** turret" | **`W2` không có turret nào** — cả **24** prefab `W2` đều `False` | suy từ 1 dòng 800-cũ, chưa kiểm lại |
| **7.570** quân turret | **7.568** | lệch 2 do gộp `copies` khác đường |

**Xác nhận đúng:** `7.568 / 45.659 = 16,6%` — tỷ lệ cũ **vẫn đúng**, chỉ thành phần sai.

| `isTurret` | Prefab | Quân | % |
|---|---:|---:|---:|
| True | 21 | **7.568** | **16,6%** |
| False — enemy thường | 49 | 37.991 | 83,2% |
| False — boss | 39 | 90 | 0,2% |

#### 7.20.4 Tỷ lệ turret đổi khi bỏ mô hình UI

Denominator cũ là **981** (gồm 204 dòng `Board_*`), thực tế là **777**:

| Cách tính | Tử | Mẫu | % |
|---|---:|---:|---:|
| Theo **bản ghi** (cũ) | 112 | 981 | 11,4% |
| Theo **prefab thật** | **112** | **777** | **14,4%** |

**Toàn bộ 112 turret đều là prefab thật** — không có turret nào trong 204 dòng `Board_*`.
⇒ Tỷ lệ turret **thực** cao hơn bản tôi công bố: **14,4%**, không phải 11,4%.

#### 7.20.5 Hai mươi hai prefab chưa từng xuất hiện

| Prefab | Controller | Ghi chú |
|---|---:|---|
| `W2-30041` … `W2-30057` (**17 cái**) | 1 mỗi cái | dải mã **không có trong wave**; `W2-30032`–`30037` mới được dùng |
| **`W2-30053 Mau`** | **6** | tên có hậu tố tiếng Việt "Màu" — bản thử màu |
| `CB-30005` · `CB-30017` · `CB-30019` | 2 · 1 · 1 | |
| `CD-31017` | 2 | turret dự phòng |

> **Nhận định (mức B):** `W2-30041…30057` + `W2-30053 Mau` (17+1) là **nội dung bị cắt hoặc bản thử**:
> cùng họ `W2` nhưng nằm ngoài dải mã đang dùng (`30032`–`30037`), và có một bản ghi rõ là "Màu".
> Chiếm **22/178 = 12,4%** prefab mang `Enemy_Controller`.
>
> **Điều kiện lật ngược:** nếu các wave bị **cắt bởi cap cũ** (182/282 wave từng có) dùng tới chúng thì đây
> là nội dung **có thật nhưng chưa thấy**. Kiểm bằng `Call_Data` **đầy đủ 23.757** — đã đủ, và **không**
> có tên nào trong 22 cái trên ⇒ loại trừ được khả năng này.

### 7.22 Damage **khai báo trong `*_Director`** — 112 field, và `Enemy_Physics` rỗng

Bản `cd0372d`. Ba phép đo độc lập, cùng một kết luận.

**a) Quét toàn bộ 109 class tìm field damage** (`dmg` / `damage` / `dame`, không phân biệt hoa thường):

| Class | Instance | Field damage |
|---|---:|---:|
| `Gun_Attack` | 458 | `bltDamage` |
| `Boss_BodyPhysics` | 251 | `dmgFirst` · `dmgPerSec` |
| **19 class `*_Director`** | **27** | **112 field** — mỗi đòn một field |
| `Enemy_Rocket_Attack` | 5 | `damage` |
| `Enemy_DestroyAttack` | 2 | `bltDamage` |
| `Enemy_BurstBulletWhenDie` | 1 | `bltDamage` |
| `Enemy_Health` | 981 | `noDamage` (**bool**, không phải damage) |

⇒ **24 class có field damage**, trên **109 class đã dump**.

**b) `Enemy_Physics` — đã đọc, và nó rỗng:**

| | |
|---|---|
| Instance | **981** |
| Field | **2** (`allColliders` · `autoCacheColliders`) |
| `allColliders = []` | **981 / 981** |
| `autoCacheColliders = false` | **981 / 981** |
| Biến thể tree | **1** — cả 981 giống hệt |

⇒ **Không có damage va chạm nào trong `Enemy_Physics`.** Damage của enemy thường **chỉ** đến từ
`Gun_Attack.bltDamage` (458 dòng). Đây là kết quả **phủ định có bằng chứng**, không phải "chưa đọc".

**c) Nối `appearScript` → `*_Director` → prefab** (trước đây chưa làm, nên tưởng 5 boss trống):

| Kênh | Boss |
|---|---:|
| `Gun_Attack` | 26 / 39 |
| `Boss_BodyPhysics` | 33 / 39 |
| `*_Director` (instance) | 36 / 39 |
| `*_Director` có damage số | 18 / 39 |
| **Không kênh nào** | **0 / 39** |

**d) Kiểm chứng độc lập thứ ba cho 45.659:** `listPrefabEnemies` (23.757 `Call_Data`) có
**45.659** phần tử; map qua `prefab-roots.csv` (2.081 dòng, `gameobject_path_id` → `name`) được
**45.659 / 45.659 = 100,0%**, **0 phần tử không map**. Và **0** phần tử thuộc 16 prefab hazard.

**e) `prefab_joins` có 453 prefab gốc, không phải 178:**

| Nhóm | Số |
|---|---:|
| Có `Enemy_Controller` | 182 (178 thật + 4 `Board_*` cùng tên) |
| `Wave_*` container | 246 |
| Không `Enemy_Controller`, có `Boss_BodyPhysics` | **25** (9 `BLT_*` + 13 `900xx` + 3 `Expl-*`) |

⇒ Từ nay mọi câu "toàn bộ enemy" phải ghi **178 = prefab có AI**; tổng prefab gốc **453**.

---

### 7.23 Bản `8c6da25`: `copies` giải 45.659 · `animator_map` · wave thứ 282 là `unknown`

**a) `copies` — đã biết ở `GAMEPLAY.md`, nhưng chưa từng kiểm chứng số học**

| | |
|---|---:|
| `sum(len(listPrefabEnemies))` | **22.482** |
| `sum(len × copies)` | **45.659** |
| Khớp `45.659` đã ghi ở §7.13? | ✅ **chính xác 100%** |
| Spawner `copies = 2` | 9.790 / 11.099 |

⚠ **Trung thực về mức mới:** công thức `len(enemies) × copies` **đã có** trong `GAMEPLAY.md`.
Cái mới ở vòng này là **phép kiểm số học**: 22.482 × copies ra **đúng 45.659**, khớp con số đếm
độc lập từ `Call_Data` — nên `45.659` nay là **mức A**, không còn là *"mức B"* như nhánh dữ liệu
ghi trong `CROSS_BRANCH_20330d0e.md` §2.

⇒ **45.659 = quân thực tế**, **22.482 = quân khai báo**. Cả hai đúng, khác phạm vi — từ nay ghi rõ.

**b) 282 wave chia 3 nhóm — hết mục mở "wave thứ 282"**

| Nhóm | Wave | Quân | Spawner |
|---|---:|---:|---:|
| Campaign `Wave_0000`–`0235` | 236 | **45.050** | 10.896 |
| Boss `Wave_7xxx`/`9xxx` | 45 | **484** | 178 |
| **`unknown`** | **1** | **125** | 25 |
| **Tổng** | **282** | **45.659** | **11.099** |

⚠ **Sửa hai số cũ:** campaign **45.076 → 45.050**; boss **90 → 484** (90 là số **`Boss-*`
instance**, không phải tổng quân wave boss). Wave `unknown` có 25 spawner, thành phần chính
`CB-30002` (34) · `CB-30015` (12) · `W2-30032` (7).

`count_spawners` trong `waves.json` cũng đổi: **11.094 → 11.099** (do `CAP_OVERRIDES` đọc đủ
`Path_Spawner`/`PinMap_Spawner`).

**c) `datas/animator_map.csv.gz` — mắt ghép Animator → prefab**

| | |
|---|---:|
| Dòng | **5.792** |
| `prefab_root` khác nhau | **494** |
| Có `controller_path_id ≠ 0` | **5.778 = 99,8%** |
| `controller_name` khớp `AnimatorController.m_Name` (308 class) | **5.603 / 5.792 = 96,7%** |
| 175 lệch | đều do CSV ghi **rỗng** còn native có tên — **không mâu thuẫn** |
| `path_id` không có trong 308 controller | 14 |

⚠ **Giới hạn:** `AnimatorController` trong typetree **chỉ có `__count`**, không có mảng PathID
của clip ⇒ **không nối được controller → từng clip cụ thể**. Mắt ghép dừng ở
**prefab → animator → controller → số clip**.

**d) `Enemy_Physics` — xác nhận độc lập lần 2:** nhánh dữ liệu (`docs/CROSS_BRANCH_20330d0e.md`
§3b) ghi *"class chỉ có 2 field và **0/981** dòng có giá trị"*. Tôi đo độc lập: **981/981**
`allColliders = []`, **1 biến thể tree** (§7.22 b). **Hai nhánh, cùng kết quả.**

---

### 7.24 Bản `4539709`: `formula_traces` — hằng số **bên trong method**, và 299 stage

**a) `datas/formula_traces.json.gz` — 305 method, 43 method đáng đọc trước**

Đây là lần đầu có **hằng số nằm trong thân hàm** (không chỉ float pool): `flow` ghi từng
`load`/`compare`/`arith` **theo thứ tự địa chỉ**. Bốn method quan trọng nhất:

| Method | Flow đọc được | Đọc ra (mức B) |
|---|---|---|
| `Player_Get_Datas.stepLevel(int playerLv)` | `load 0.168` → `cmp 30` → `load 1.0` → `cmp 58` → `load 1.05` → `cmp 118` → `fmul 1.15` → `cmp 248` | **4 bậc cấp 30/58/118/248**, hệ số **0,168 · 1,0 · 1,05 · 1,15** |
| `Player_Get_Datas.GetMainCannonDamage` | cùng 4 ngưỡng, `0.168` · `0.1764` · `0.1932` · `fadd 1.0` | `base × (1 + k)` với 0,1764 = 0,168×1,05 và 0,1932 = 0,168×1,15 |
| `Tech_Datas.GetCostUpgrade` | `cmp 8` → `1.0` → `1.0` → `cmp 5` → **`2.55`** → return | hệ số nhân giá **2,55**, có 2 nhánh |
| `Tech_Datas.NumberTechStats` | `60.0` · `0.2` · `0.2` · `-4.0` · `-0.2` | **60 tech stat**, có phụ phí `0,2` và `−0,2` |

⚠ **Chưa phải công thức:** `flow` là **nguyên liệu theo địa chỉ**; rẽ nhánh chưa đọc nên **thứ tự
nhân chưa chắc**. Muốn chắc phải đọc `.asm.txt` từng method.

**b) `Player_Get_Datas.GetStartHp` — chỉ có `fadd 1.0`**

Không có hằng số HP nào trong thân hàm ⇒ HP gốc **không nằm trong method này**. `Data_Players`
(2 instance) chỉ có `id` · `Star` · `Actived` · `Sprite` ⇒ **HP player không có trong 110 class
đã dump**. Đây là **câu chặn số 1** của `DESIGN_QUESTIONS.md`.

**c) `Stage_Behaviour.csv` — cấu trúc màn**

| Chỉ số | Số |
|---|---:|
| Dòng | **299** |
| Chapter | **2** (`Chap 1`: 229 · `Chap 2`: 55) |
| `Stage_Normal` | **199** |
| `Stage_Combat` | **49** |
| `Stage_MiniBoss` | **25** |
| `Stage_Boss` | **26** |
| Cột `stageType` có giá trị | **100 / 299** (giá trị 1 · 2 · 3) |

⚠ **Không có cột `wave`** ⇒ **chưa nối được stage → wave**. 299 stage vs **281 wave** (236 + 45)
lệch **18** — phải đọc `Parent_Stages` trong `Board_Maps` hoặc `textStageIndex` → `Text`.

---

### 7.25 HP player — chuỗi **đầy đủ** đọc từ arm64 (không phải từ ScriptableObject)

Đây là lớp dữ liệu **không có trong bất kỳ CSV nào**: HP player **tính lúc chạy**.
Đọc `raw/il2cpp-consts/Player_Get_Datas.asm.txt` + `dump.cs.gz`.

**a) Công thức (mức A — đọc từng lệnh):**

```
GetStartHp()       = StartHp × (1 + GetHpStatPercent())
GetHpStatPercent() = stepCommon × Tech_Datas.GetTechStatPoints(0)
                   + abi7AddPlayerStartHp × GP_Datas.GetNumberAbility(7)
```

| Bằng chứng | Địa chỉ | Lệnh |
|---|---|---|
| `StartHp` đọc từ `@0x6C` | `0x14e3168` | `ldr s8, [x8, #0x6c]` |
| `1 + pct` | `0x14e3178`–`0x14e317c` | `fmov s1, #1.0` · `fadd s0, s0, s1` |
| **nhân** | `0x14e3180` | **`fmul s0, s8, s0`** |
| `GetTechStatPoints(0)` | `0x14e3200` | `bl #0x1399aa4` (RVA → method qua `dump.cs`) |
| `stepCommon` `@0x68` | `0x14e3228` | `ldr s8, [x8, #0x68]` |
| `abi7AddPlayerStartHp` `@0x314` | `0x14e3230` | `ldr s9, [x8, #0x314]` |
| `GP_Datas.GetNumberAbility(7)` | `0x14e3244` | `bl #0x14c7758`, `w0 = 7` |
| cộng 2 nguồn | `0x14e3260` | `fadd s0, s0, s1` |

**b) Vai trò từng field:**

| Field | Class | Offset | Vai trò |
|---|---|---|---|
| `StartHp` | `Player_Get_Datas` | `0x6C` | HP gốc = **2500,0** (đọc từ `.cctor`, `6109008c`) |
| `stepCommon` | `Player_Get_Datas` | `0x68` | **0,18** — % mỗi điểm stat (**KHÔNG** dùng chung với `stepLevel` = 0,168) |
| `abi7AddPlayerStartHp` | `Player_Get_Datas` | `0x314` | % mỗi bậc ability 7 |
| `StartHealth` | `Player_Health` | `0x0` (**static**) | = `GetStartHp()` lúc vào màn |
| `CurrentHealth` | `Player_Health` | `0x4` (**static**) | HP hiện tại |
| `Armor` | `Player_Health` | `0x20` | **giảm damage nhận**, không cộng HP |
| `reduceDamageByDevice` | `Player_Health` | `0x58` | giảm damage theo thiết bị |
| `HasShieldOneHit` · `Invincible` · `timeToImmuneOneHit` | `Player_Health` | `0x31` · `0x30` · `0x2C` | khiên 1 đòn · bất tử · miễn thương |

**c) `Damager` chỉ có 2 field:** `float damage` + `Action<GameObject> killEvent` ⇒ **giáp bị trừ bên
trong `Player_Health.TakeDamage`**, không nằm ở `Damager`.

**d) Vì sao dữ liệu tĩnh không có:** `Player_Get_Datas..cctor` **không gán** `StartHp` — toàn file asm
**chỉ 3 lệnh đọc** `[.., #0x6c]`, **0 lệnh ghi**. ⇒ `StartHp` mặc định **0** và gán lúc chạy ở class
**không nằm trong 11 class có asm**.

**e) Cái đã đóng so với `DESIGN_QUESTIONS` B2:** câu hỏi chuyển từ ❌ sang **⚠** — còn **1 hằng số**,
không còn là "không có dữ liệu".

**f) HP theo tàu hay không — phải tách hai lớp, và lớp thứ hai CHƯA kiểm được:**

| Field | Kiểu | Kết luận |
|---|---|---|
| `StartHp` | `float` | **dùng chung mọi tàu** |
| `StartMainCannonDamages` · `StartWingCannonDamages` · `StartMainCannonRate` | `float[]` | **riêng từng tàu** |
| `Device { id, lv, rank, instanceId }` | – | device cho `reduceDamageByDevice` + `amountAutoGainHpByDevice` ⇒ **giảm damage / hồi HP**, không tăng HP tối đa |

⇒ **Lớp serialize (mức A):** không có bảng HP theo tàu; tàu chỉ có **damage + nhịp bắn** là mảng.
`Data_Players` (25 tàu) chỉ có `id · Sprite · Star · Actived` — **0 field HP**.

⚠ **Lớp runtime (mức C):** `StartHp` là `float` **đơn** nên nó **có thể bị gán lại mỗi lần chọn tàu**
trước khi `Player_Health.Start()` chạy. **Không có asm của `Player_Health`** ⇒ **chưa kết luận được**.
Muốn chốt: dump `Player_Health.asm.txt` (RVA `0x14C6B5C`), tìm lệnh **ghi** `#0x6c` trên `Player_Get_Datas`.
Đây là chỗ câu "HP không theo tàu" **không được** viết như kết luận.

**g) Hai ứng viên cho `playerLv` của `stepLevel`:** `Player_Ingame.lv` (`private static int @0x4`,
có property `Level`) hoặc `Player_Saved_Datas.MaxLevelPerRanks` (`int[]`) + `MAX_RANK_INDEX`.
Ngưỡng **30/58/118/248** quá cao cho một màn ⇒ nghiêng về **cấp tài khoản/rank** (mức C).

---

### 7.26 Kiểm chứng 3 giả thuyết về HP — và phát hiện `Map_Get_Datas.GetListWaves`

Bản `03aacac`. Kiểm bằng **chữ ký hàm** + **API của từng hệ**, không bằng suy luận.

**a) "Talent và nâng cấp chung cho mọi tàu" — ĐÚNG, mức A**

`Player_Get_Datas` có **40 method** trả `float`/`int`:

| Loại | Số | Gồm |
|---|---:|---|
| Nhận **`playerIndex`** | **7** | 5 stat **damage/nhịp bắn** (`GetMainCannonDamage` · `GetMainCannonRate` · `GetWingCannonDamage` · `…ByBase` · `…ByTech`) + 2 **giá mở tàu** |
| **Không tham số** | **33** | HP (9) · talent (8) · crit/% (4) · overdrive/thời gian (5) · từ/nam châm (4) + 3 lẻ |

⇒ **Không có method HP nào nhận `playerIndex`.** Đổi tàu chỉ đổi **damage + nhịp bắn**.

**b) "Né hay invisible theo tài năng" — ĐÚNG MỘT NỬA**

| Cơ chế | Hệ thật | Bằng chứng |
|---|---|---|
| **Invisible** | ✅ **talent** | `Player_Talent`: `List<Talent_Invisible> allZoneInvisible` · `listShipInvisible` · `SetInvisible(GameObject zone, Transform p, bool invisible, bool heal)` |
| **Né (dodge)** | ❌ **ability 8**, không phải talent | `abi8AddDodgeRate` (`Player_Get_Datas` §2.6 `TUNING_KNOBS`) |

Cả hai đều **không** nhận `playerIndex` ⇒ **dùng chung mọi tàu**.

**c) `Ability` và `Talent` là hai hệ khác nhau — trước đây gộp sai**

| `Player_Ability` | `Player_Talent` |
|---|---|
| **skill runtime**: `shieldObject` · `shieldOneHit` · `shieldDroidObject101/103` · `drone7SkillObject` · `drone11SkillObject` | **cây điểm mua bằng coin**: `talentIndex` · `pointCount` · `points` · `coinPerPoint` · `Talent_Invisible` |

**d) "Drone / danh hiệu / buff cộng vào HP" — KHÔNG có đường nào, mức A**

| Hệ | Số method | Có method trả HP? |
|---|---:|---|
| `Droid_Data_Balance` | **11** | ❌ 0 — chỉ damage, timeout, giá, rank, bought |
| `RankManager` | **14** | ❌ 0 — **toàn bộ là leaderboard online** (`IECheckCampaignRankings`, `IESetCampaignRankings`, `IETryGetRoomRankCampaign`…) |
| `Stage_Get_Datas` | **10** | ❌ 0 — `GetBonus` trả **`int`** = **phần thưởng**, không phải buff HP |
| class `Buff` / `PowerUp` | — | ❌ **không tồn tại**; `p1_idBltPowerUp` · `p1_superPowerUpShotRate`… là **power-up riêng từng tàu** |

**e) `Map_Get_Datas` — mắt ghép **map → wave** chưa từng dùng**

| Method | Chữ ký | Ý nghĩa |
|---|---|---|
| `GetListWaves` | `static int[] GetListWaves(int mapIndex)` | **danh sách wave của một map** ← nối được `mapIndex` → wave |
| `GetNumberWaves` | `static int GetNumberWaves()` | tổng số wave |
| `GetListBossWaveNormal` | `static List<int> GetListBossWaveNormal()` | danh sách wave boss |
| `GetListMapPvP` · `GetListMapPvPRandom` · `…Arena…` | `int[]` / `int` | map theo rank PvP/Arena |

⚠ **Giá trị chưa lấy được:** `GetListWaves` đọc một **mảng static** nạp trong `.cctor` của
`Map_Get_Datas`, mà **`.cctor` không nằm trong asm đã export** (8 method, không có `.cctor`).
⇒ **Cấu trúc biết (A), giá trị chưa (D).** Cách lấy: export `.cctor` của `Map_Get_Datas` hoặc đọc
`w.Data.waves` XML gốc.

**f) `GetStartHp` chỉ được **2 method** gọi:** `GetGainHpItem` và `GetGainHpItemAddOverTime`
(cả hai là **item hồi máu**). `Player_Health.Start()` gọi nó nhưng **không có asm** ⇒
**không thấy được lời gọi thứ ba**.

---

### 7.27 Device — giải mã công thức, và **sửa lại lỗi của tôi** về HP

Bản `8871068a`. `Device_Get_Data.asm.txt` + `dump.cs.gz`.

**a) `GetStatValue1` — công thức đầy đủ (mức A):**

```
type  = device.id / 100 − 1        // magic 0x10624DD3 ⇒ chia 100
base  = listStatValues[type][device.rank]
pct   = percentByLevels1[type] × (device.lv + 1)
value = base + pct
if (type == 4) value /= 100        // 0x42C80000 = 100.0
```

`GetStatValue2` giống hệt nhưng dùng **`percentByLevels2`**, và **cũng** có nhánh `type == 4`.

**b) 5 loại × 2 stat** — `.cctor` tạo mảng `mov w1, #5` (5 phần tử) · `cmp w20, #4` (index 0…4) ·
2 hàm `GetStatValue*` ⇒ **5 loại device, mỗi loại 2 stat, type 4 là stat phần trăm**.

**c) ⚠ SỬA LỖI — device **có** ảnh hưởng HP:**

| Lần viết | Nội dung | Đúng? |
|---|---|---|
| lần 1 | "device ❌ không cộng HP tối đa" | ❌ **sai** |
| lần 2 | vẫn giữ "không cộng HP tối đa" | ❌ **vẫn sai** |
| **lần này** | **`Player_Health.OnChangeDataDevice(int _idPlayer)`** — hàm chạy khi đổi device | ✅ bằng chứng **device → HP** |

`Player_Health` có **3 đường** device: `OnChangeDataDevice` · `amountAutoGainHpByDevice` ·
`reduceDamageByDevice`.

⇒ HP tối đa = `StartHp × (1 + tech% + ability7%)` **rồi** `OnChangeDataDevice()` điều chỉnh tiếp.
**Hai hệ song song**, không phải một.

> **Điều kiện lật ngược:** nếu `OnChangeDataDevice` chỉ hồi đầy `CurrentHealth` mà **không** đổi
> `StartHealth` thì device **không** tăng HP tối đa. Cần `Player_Health.asm.txt` (`@0x0` vs `@0x4`).

**d) Giá trị số chưa có:** 3 bảng static được nạp bằng `RuntimeHelpers.InitializeArray` từ **field
RVA data** — không có trong `dump.cs` lẫn asm. Biết **công thức + 5 loại**, chưa biết **hệ số**.

---

### 7.28 `Player_Health` **không** thiếu asm — và vòng đời HP

Bản `8871068a`.

**a) ⚠ SỬA LẠI điều tôi ghi trong `DATA_SYNC` cũ:** tôi đã ghi *"thiếu `Player_Health.asm.txt` ⇒ cần
xin phép dump thêm"*. **Sai** — dumper dump **liền mạch theo địa chỉ**, nên `Player_Datas.asm.txt`
(257 dòng, chỉ 1 header `;;; ctor`) chứa **6 hàm liên tiếp**:

| Địa chỉ | Hàm thật | Thuộc class |
|---|---|---|
| `0x14c6b4c` | `.ctor` | `Player_Datas` |
| `0x14c6b5c` | **`Start()`** | `Player_Health` |
| `0x14c6ca0` | **`ResetStaticVariables()`** | `Player_Health` |
| `0x14c6cfc` | `GainHealth(float, float, float)` | `Player_Health` |
| `0x14c6d70` | `GainHealthOverTime` | `Player_Health` |
| `0x14c6de4` | **`TakeDamage`** | `Player_Health` |

⇒ **Bài học phương pháp:** không tin tên file asm; **tra RVA trong `dump.cs`** rồi tìm địa chỉ đó
**trong mọi file**. Cơ chế này có thể còn cứu được nhiều class khác tưởng là "thiếu".

**b) Ba kết quả đọc được:**

```
ResetStaticVariables():   StartHealth(@0x0) → CurrentHealth(@0x4)      // chỉ chép
Start():                  mainModule = fxHealHpBar.main + tạo lambda   // ⚠ SAI — xem đính chính dưới
TakeDamage():             5 cổng chặn trước khi trừ giáp
```

**c) `StartHealth` là `static`** ⇒ HP tối đa là **một biến toàn cục**, không phải field per-tàu.
Hồi sinh (`ResetStaticVariables`) **chép lại**, **không** tính lại stat.

> ⚠ **ĐÍNH CHÍNH (bản `6109008c`):** dòng `// không đụng HP` ở khối (b) là **SAI** — nó viết khi
> asm còn cụt. Thân lambda `<Start>b__14_1` (604 B) **gọi `GetStartHp()`** rồi `stp s0,s1,[x8]`
> ghi `StartHealth@0x0` + `CurrentHealth@0x4`. Xem `BALANCE` §0.6.15 và `ASM_INTEGRITY` §1.
> `ResetStaticVariables()` vẫn chỉ **chép** — phần đó giữ nguyên.

**d) `Player_Device_Saved_Datas.GetPlayerDevices(int playerIndex)`** — device lưu **theo từng tàu**.
Đây là mắt ghép cuối của giả thuyết *"HP là của tàu"*: `StartHp` **không** theo tàu, nhưng
**device thì có** ⇒ HP hiệu dụng **vẫn khác nhau giữa các tàu**, qua đường device.

**e) `TakeDamage` — cổng chặn theo thứ tự (A):**
`CurrentHealth <= 0` → `invisible (@0x49)` → `damager == null` → `IsVictory (@0x4A)` →
`Invincible (@0x30) && !ignoreInvincible` (nếu qua được: `GetNumberAbility(30) >= 1` + `Random(0,100)`).

---

### 7.29 ⚠ **Asm export bị cắt cụt** — mọi kết luận âm tính phải rút lại

Bản `8871068a`. Đây là **lỗi phương pháp nghiêm trọng nhất** tìm được tới giờ, và nó **không** đến từ
dữ liệu game mà từ **công cụ export**.

**a) Bằng chứng:** 12 file `il2cpp-consts/*.asm.txt`. Chỉ `ArenaManager` kết thúc bằng `ret`.

| File | Method | Lệnh | Lệnh cuối |
|---|---|---|---|
| `ArenaManager` | 27 | 1.880 | `ret` ✅ |
| `Device_Get_Data` | 13 | 4.393 | `bl #0x1bd7e58` ❌ |
| `Droid_Data_Balance` | 11 | 1.618 | `mov x0, x20` ❌ |
| `Enemy_Data_Balance` | 7 | 927 | `mov x0, x19` ❌ |
| `GameDatas` | 72 | 4.582 | `ldr x8, [x8, #0xd98]` ❌ |
| `IAP_Manager` | 34 | 2.170 | `ldp x30, x21, [sp], #0x20` ❌ |
| `Map_Get_Datas` | 8 | 772 | `bl #0x110d258` ❌ |
| `Player_Datas` | 1 | 256 | `ldr x9, [x0, #0xb8]` ❌ |
| `Player_Get_Datas` | 61 | 5.341 | `ldr x22, [x22, #0x858]` ❌ |
| `RankManager` | 17 | 1.010 | `bl #0x122787c` ❌ |
| `Stage_Get_Datas` | 10 | 2.328 | `ldr x8, [x8, #0xc0]` ❌ |
| `Tech_Datas` | 24 | 7.348 | `mov x2, x20` ❌ |

> **Đính chính 25/10:** bảng trên là bản `8871068a`. Bản `6109008c` **hết cụt**
> (§7.31 ngay dưới), `Stage_Get_Datas` đã decode **2/2 mảng**. Đừng đọc cột ❌ thành hiện trạng.

**b) Cái bị cắt:** đuôi của **method cuối theo thứ tự địa chỉ**. Ở **8/12 file** method cuối là
**`.cctor`** — tức là đúng chỗ **gán các giá trị khởi tạo**.

**c) Ba kết luận phải rút lại (trước đây tôi đã trình bày như bằng chứng phủ định):**

| Kết luận cũ | Trạng thái |
|---|---|
| "`Player_Get_Datas..cctor` không gán `StartHp`" | ❌ **vô hiệu** — `.cctor` dừng giữa chừng ở `0x14e5cc4` |
| "Không có lệnh ghi `#0x314` (abi7) trong bất kỳ asm nào" | ❌ **vô hiệu** |
| "`GetStartHp` chỉ được 2 method gọi" | ⚠ **không đầy đủ** — caller có thể ở phần cụt |

**d) Vẫn đứng vững** (vì đọc từ `dump.cs` / JSONL đầy đủ, **không** phụ thuộc asm):
`StartHp` là `float` đơn · `ships.json` **25 tàu không có field HP** · `Player_Saved_Datas` chỉ `int[]` ·
`script-links` 127.659 dòng không có `StartHp`.

**e) Bài học ghi vào quy trình:** trước khi dùng asm để **phủ định**, phải kiểm **file có kết thúc
bằng `ret` không**; nếu không, chỉ được nói *"không thấy trong phần đã export"*.

**f) Yêu cầu dump hẹp nhất còn lại:** **200 lệnh sau `0x14e5cc4`** của `Player_Get_Datas..cctor`.

---

### 7.30 Tech stat id 0 = **Health** — và enemy thường có **HP = 0**

**a) HP người chơi là một **đường nâng cấp** (A).** `12-localization.csv` có **24 khoá**
`txt_techstat_label_*` / `txt_techstat_desc_*`, id **0–11**:

| id | label | desc |
|---|---|---|
| **0** | **Health** | **"Increase health points"** |
| 1–11 | Special cannon · Normal cannon · Magnet · Laser weapon · Bomb · Rocket Barrage · Stun · Invisible · Super Lazer · Mega Bomb · Invisible II | tăng power / hiệu ứng |

Nhãn tab: **`txt_basic` = "Basic / Cơ bản"**; nhiệm vụ `txt_upgrade_full_tech_lv`.
⇒ khớp **chính xác** với `GetHpStatPercent = 0,168 × TechStatPoints(0) + …` (`BALANCE` §0.6.1).
⇒ **HP không thuộc tàu** — đây là lý do `ships.json` 25 tàu **không có field HP**, và đó **không**
phải chỗ thiếu dữ liệu.

**b) Hai loại tàu (A).** `Player_Ingame` (main) + **`Sub_Player : Sub_Character, IPlayerTypes, …`**
(support). `Sub_Player` có `private Player_Health heathScript; // 0x28` ⇒ **support ship có HP riêng**.
Cả hai đều có `ChangePlayerTypes(Action)`; bộ điều phối là **`GP_ChangePlayerTypes.Init(Transform)`**.
**4 slot device/tàu** khớp **2 main + 2 support**.

**c) `Enemy_Datas.csv` — 981 dòng, 72 giá trị HP khác nhau:**

| Chỉ số | Giá trị |
|---|---|
| `StartHealthPoint > 0` | **467 / 981** |
| `StartHpPoint` | **0 ở 981/981** ⇒ **field chết** |
| `CurrentHealthPoint` | **0 ở 981/981** ⇒ **field chết** |
| `Boss-*` có HP | **45 / 45 (100%)** |
| `CB-*` (enemy thường) có HP | **1 / 37** — chỉ `CB(TEST)` |
| `CB-30003` · `CB-30015` · `CD-31002` | **0,0** · **0,0** · **0,0** |

**d) Phủ định `Wave` có scale độ khó:** class `Wave` chỉ có **3 field**
(`indexWave`, `startPoint`, `endPoint`) ⇒ **không** có chỗ chứa hệ số độ khó.

**e) `Stage_Get_Datas.levelDelta` (float[]) scale **phần thưởng**, không scale HP** — dùng trong
`GetBonus(stageIndex, stageLevel, missionIndex)` (`fmul s0,s8,s0`).

**f) Đường cong độ khó thật = HP boss.** Tổng HP mỗi wave (cộng mọi bộ phận):

| Wave | có HP | median | max |
|---|---|---|---|
| 0–239 | **5 / 240** | 0 | 4.272.000 |
| 240–259 | 20/20 | **4.300.000** | 7.290.000 |
| 260–279 | 20/20 | **7.760.000** | 13.390.000 |
| 280–281 | 1/2 | 10.500.000 | 10.500.000 |

---

### 7.31 Bản `6109008c` — **asm hết cụt**, 5 class mới, và số liệu **đổi**

**a) Công cụ đã sửa:** kích thước method lấy từ **method kế tiếp trong dump**, trần **128 KB**
(trước: cắt ở 4.608 B/method). Kết quả: **11/12 file trước đây bị cụt → nay đủ**.

| File | Trước | Sau |
|---|---|---|
| `Map_Get_Datas.asm.txt` | 772 lệnh, **không có `.cctor`** | **26.013 dòng**, có **`.cctor`** |
| `Player_Get_Datas.asm.txt` | 5.341 lệnh, `.cctor` cụt | **đủ** (`.cctor` 2.492 B, 97 hằng) |

**5 class asm/json MỚI:** `Player_Ability` · `Player_Attack` · `Player_Health` · `Player_Ingame` · `Player_Talent`.

**b) Ba mục tôi từng để mở — nay đóng (A):**

| Mục | Kết quả |
|---|---|
| **A1 `StartHp`** | **2500** · `stepCommon` **0,18** · `BaseHpRecoverSpeed` **0,01** — đọc từ **cặp `ldr d`** rồi `str d0, [x8,#0x68]` ghi **2 float liền** |
| **A3 `OnChangeDataDevice`** | đọc đủ 452 B: **KHÔNG** ghi `StartHealth`; chỉ đặt `reduceDamageByDevice` + `amountAutoGainHpByDevice` (`BALANCE` §0.6.7d) |
| **A4 caller của `GetStartHp`** | **`Player_Health.<Start>b__14_1`** → ghi `StartHealth` (`BALANCE` §0.6.15) |

**c) ⚠ ĐÍNH CHÍNH số đã công bố** (do `enemy_hp.json` + `waves.json` được tái export):

| Số | Cũ | `6109008c` | **`68ce86a7`** |
|---|---|---|---|
| `Boss-*` **root** có HP > 0 | 45/45 | — | **38/39** (`39003` = 0) |
| Prefab **root** trong `15-enemy-hp.csv` | 246 | 251 | **249** (249 root, **115** có tổng HP > 0) |
| `count_spawners` | 11.099 | 11.095 | **11.092** |
| Wave có HP > 0 | 46 | 45 | **45** |
| Tổng HP toàn game | 241.598.000 | 496.410.000 | **480.892.000** |
| Median HP wave 240–259 | 4.300.000 | 8.600.000 | **8.600.000** |
| Median HP wave 260–279 | 7.760.000 | 16.230.000 | **15.400.000** |
| Wave 280+ | 10.500.000 | 20.600.000 | **18.300.000** |
| Tỉ lệ / 20 wave cuối | 1,8× | 1,89× | **1,79×** |

⇒ **đường cong độ khó ≈ 1,79× mỗi 20 wave** ở đoạn cuối. ⚠ Con số **đổi theo từng lần export**
(`15-enemy-hp.csv`: 251 → **249** root, **70** root đổi giá trị) nên **hạ nhãn A → B**;
định nghĩa phép tính ở `BALANCE` §2 và `VERIFY_ROUND1` §4.2. **Điều kiện lật ngược:** export sau
trả lại các instance đã mất ⇒ tổng về ≈496 M và tỉ lệ về 1,89×.

**d) `waves.json` nay có `copies` là field hiện:** `Σ len(enemies)` = 22.471 → **22.457** ·
`Σ len × copies` = **45.659** (không đổi qua cả 3 bản export) ⇒ **45.659 vẫn đúng**, chỉ là trước phải
tự nhân. Median quân/wave 130,5 → **131,5**; max **951**; **109** prefab. **Bản `68ce86a7`.**

**e) `Count` vẫn = 0 ở 100% spawner** — không đổi.

---

## 8. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | ~~Giá trị 957 `static`~~ | ~~D~~ → 🟡 | **623 record** của 17 method đã decode (`ia-resolved.json` — HP/damage/giá/hệ số); còn literal store + field vô hướng |
| 2 | ~~Giá trị 4.861 `[SerializeField]`~~ | ~~D~~ → 🟡 | **binary đã có** trong pack v2 (report 70) — xin giá trị qua PR12, không cần tự chạy |
| 3 | ~~Đơn vị đếm tổng HP boss~~ | ~~C~~ → **A** | ✅ chốt: gom theo **prefab gốc** — `datas/boss_hp.json` **246 prefab** (peer refresh 26/10 — cũ 253; `hp_max` = bản mạnh nhất; bảng đối chiếu lịch sử: 254→256 report 78/P5, 253→246 §17.1) |
| 4 | 23 `SoundClip` không có clip | **D** | 92 khai báo vs 69 thật |
| 5 | Loop point của 8 track nhạc | **D** | không có trong index |
| 6 | ~~Pivot / border sprite~~ | ~~D~~ → **A** | ✅ **ĐÓNG (report 75 peer)** — `sprite_mesh_contract` giữ source rect/pivot/border/PPU từng sprite |
| 7 | 22.957 mẫu `Call_Data` (96,6%) | **A** (là cap) | `unity_data.py` dừng ở `MAX_READ_PER_CLASS=800`; chưa chạy lại với cap cao |
| 8 | 12.492 mẫu `PointToPoint_Spawner` (94,0%) | **A** (là cap) | như trên |
| 9 | Bảng `Transform` (`m_Father`) cho toàn bộ `data.unity3d` | **B** | chưa export lần nào; là mảnh duy nhất còn thiếu để ghép súng/xác |
| 9b | **HP enemy thường** (68/70 prefab = 0) | **A** (không có trong prefab) | nằm trong thân hàm `Enemy_Health.Init`; xem `BOSSES.md` §6 |
| 10 | **87 class enemy/boss** (7.036 instance): `Enemy_Physics` 981 · `Enemy_Display` 981 · `Enemy_Destroy` 971 · `Enemy_Hp_Bar` 909 · `Enemy_Burned` 695 · `Enemy_LookAtPlayer` 391 · `Enemy_CameraVibrate` 241 · `Enemy_Stun` 140 · `Enemy_Sync_Attack` 72 · `Enemy_Attack` 51 · `Boss3_Plasma` 75 · `Boss_PlasmaBeam` 68 · 17 `Boss*_Director` | **D** | chưa có CSV nào; đây là phần **hành vi** chứ không phải số |



> Không có mục nào ở đây là "không thể". #1 và #2 là **bug/chưa chạy**, #3 là **chưa chốt định nghĩa**,
> #7 và #8 là **cap của tool sửa bằng biến môi trường**, #9 là **thiếu một bước export**.
> Bốn nhóm này khác nhau, và chỉ #1/#2 mới thật sự cần chạy lại IL2CPP/AssetRipper.

---

## 9. Sổ theo dõi mắt ghép — trạng thái sau bản `cd0372d`

**Mắt ghép mới đóng ở vòng này (§7.22):**

| Mắt | Trạng thái | Bằng chứng |
|---|---|---|
| `appearScript` → `*_Director` → prefab boss | ✅ **36/36** map được | 63 instance / 37 class |
| Duyệt toàn bộ class tìm field damage | ✅ **109/109** class | 24 class có field |
| `Enemy_Physics` | ✅ **981/981** đọc — **rỗng** | 1 biến thể tree |
| `listPrefabEnemies` → tên prefab | ✅ **45.659/45.659 = 100%** | `prefab-roots.csv` 2.081 |
| `_gameobject` trong CSV scriptableobject | ✅ có **đường dẫn đầy đủ** (`Wave_0005/GameObject/…/CD-31015`) | dùng cho §8.4.1 |

Cập nhật cuối: 2026-10-23 01:00. Mọi mục dưới đây **đã đo**, không suy đoán.

### 9.1 Đã đóng (100%)

| # | Mắt ghép | Số | Ghi chú |
|---:|---|---:|---|
| 1 | `Call_Data` → prefab enemy | 90 / 90 | qua `Enemy_Controller.m_GameObject` |
| 2 | `Enemy_Controller` → 5 script con (Datas · Health · Movement · Display · Physics) | **981 / 981** mỗi cái | khoá = PathID |
| 3 | `Enemy_Controller` → `Destroy` / `Appear` | 981 / 981 | `Destroy` 971 + 3 + 7 |
| 4 | `Enemy_Sub` → `Enemy_Controller` | **981 / 981** | |
| 5 | `Gun_Attack` → prefab gốc | **458 / 458** | qua `Transform` |
| 6 | `Boss_BodyPhysics` → prefab gốc | **251 / 251** | |
| 7 | `Enemy_Movement.parentRotate` → prefab gốc | **558 / 558** | |
| 8 | `Wave.startPoint` + `endPoint` → prefab | **686 + 686** | |
| 9 | `Stage_Behaviour.bossObj` | **250 / 250** | ⚠ nối vào `Board_Maps` = icon bản đồ |
| 10 | `Enemy_Controller` → `*_Director` (qua `appearScript`) | **67** | boss không dùng `Enemy_Appear` |
| 11 | `Call_Point` → `Call_Data` | **23.757 / 23.757** | lớp bọc mỏng |

**Không còn mắt ghép cấu trúc nào dưới 100%.**

### 9.2 Còn mở — 6 mục, xếp theo chi phí

| # | Thiếu | Chi phí | Ảnh hưởng |
|---:|---|---|---|
| 1 | **Curve 791 `AnimationClip`** | viết decoder `m_StreamedClip` | dáng chuyển động Mecanim (nhịp **đã có**) |
| 2 | **`ParticleSystem`** 4.845 | thêm type như `Transform` | FX |
| 3 | **`Animator` 5.792 → prefab** | thêm type | map controller → boss |
| 4 | **`width × height` sprite** | tải `manifest-full.csv` (bị chặn) | hình học sprite rời |
| 5 | **Số con mỗi lượt spawn** | đọc thân hàm | 45.659 vs 23.757 |
| 6 | **Method body** (0,44%) | Ghidra/IDA | công thức HP, điều kiện thắng |

### 9.3 Ba con số phải nói kèm nhãn

| Số | Nghĩa đúng | Đừng viết |
|---|---|---|
| **981** | số **bản ghi** `Enemy_*` | "981 enemy" — **204 là trên `Board_*`** |
| **45.659** | tổng **phần tử** `listPrefabEnemies` | "45.659 quân" — cách sinh chưa chắc |
| **458** | số khẩu `Gun_Attack` **kể cả preview UI** | "458 khẩu trong trận" — **319** là thật |

> Ba nhãn này là kết quả của 3 lần tôi bị dữ liệu mới sửa lại. Ghi ở đây để không lặp.

---

## 10. Kéo bản `019e704d1` — **1.339 file `scriptableobjects/`** (24/10)

`git fetch` nhánh dữ liệu: **ref của tôi khi đó vẫn là `019e704d1`** (⚠️ **cách nói sai** — xem §12:
refspec thiếu nên ref không tự cập nhật; nhánh dữ liệu **đã** có commit mới). Vẫn kéo thêm một cây
chưa từng lấy: `reverse-engineering/scriptableobjects/`.

| Cây | File | Dung lượng | Lấy? |
|---|---:|---:|---|
| `reverse-engineering/scriptableobjects/` | **1.339** | **7,8 MB** | ✅ lấy |
| `reverse-engineering/raw/ui/` | 53.318 | **142,7 MB** | ❌ **không** — vượt hạn mức snapshot, và cấu trúc UI đã có ở `UI.md` + `screens.csv` |

`scriptableobjects/` gồm **một CSV phẳng cho mỗi lớp** (mọi instance, mọi field) + JSON từng asset:

| Nhóm | Ví dụ | Giá trị |
|---|---|---|
| Dữ liệu spawn | `Call_Data.csv` · `Wave.csv` · `Spawner.csv` · `Call_Point.csv` | **tên field thật** của dữ liệu wave |
| Nhân vật/boss | `Boss1_Director.csv` · 23 file `Boss*_AnimationEvents.csv` · `Enemy_*.csv` | field serialized của từng lớp |
| Rig | `SkeletonAnimation.csv` · `SkeletonDataAsset.csv` | nối rig ↔ prefab |
| Khác | `Gun_Attack.csv` · `Sub_Item.csv` · `language.LanguageAssets/` | súng, item, chuỗi ngôn ngữ |

### 10.1 Cái nó **trả lời được ngay**: schema của spawner

`Call_Data.csv` = **1.200 dòng · 23 field** — đúng bảng mà `datas/waves.json` được giải ra từ đó:

```
angle · color.rgba · editType · listBringItems · listIdEnemies · listPrefabEnemies ·
maxValX · minValX · number · radius · rate · showGizmos · spawnType · speed · ySpawn · yStart
```

Hai điều đọc được:

1. **không có field `delay`** — `rate` là **field thời gian duy nhất** của một spawner.
2. `number` = **0 ở 1.200/1.200** dòng ⇒ trường "số lượng" **không được dùng**; số quân thật sự nằm ở
   **độ dài `listPrefabEnemies`**.

⇒ Thu hẹp câu `rate = 0` (blocker #1 của `DESIGN_READINESS.md`): khi chỉ có một field thời gian và
`rate = 0` xuất hiện **295/1.200** spawner, thì khả năng cao `rate` là **giãn cách**, và `rate = 0`
= **không giãn cách** (spawn cả loạt) — chứ không phải "không bao giờ spawn". Nhưng **chưa đóng**:
vẫn có thể là "số quân/giây" với 0 = không spawn. Xem `DESIGN_READINESS.md` §3.

### 10.2 Cái nó **không** trả lời

- `Spawner.csv`: `dataScript` **null** trên mọi instance (đúng như `UNITY_RULES` C3) ⇒ dữ liệu spawn
  không nằm trong prefab, phải đọc từ `Call_Data`/blob.
- **Không có** `Animator` / `AnimatorController` (vẫn là T4 của `HANDOFF_ANIM_RAW.md`).
- **Không có** `Boss1_AnimationEvents` trong `scriptableobjects/` (chỉ có asm của nó) ⇒ T2 vẫn nguyên.
- 23 file `*_AnimationEvents.csv` chỉ có **field serialized**; field **delegate** không serialize nên
  **không** xuất hiện ⇒ không giúp tìm "ai gán delegate".

### 10.3 Kéo tiếp cùng đỉnh `019e704d1` (24/10, lần 2)

Ghi chú lúc đó: "vẫn không có commit mới" — ⚠️ **sai** (xem §12/§13: ref của tôi chưa cập nhật, nhánh
dữ liệu **đã** đi tiếp). Đã lấy thêm **phần nhỏ nhưng nặng thông tin**:

| Cây | Lấy | Bỏ | Vì sao |
|---|---|---|---|
| `docs/apk-analysis/**` (md + csv) | **140 file · 6,5 MB** | ảnh `.png` | báo cáo gốc + CSV; ảnh đã có contact-sheet riêng |
| `reverse-engineering/raw/ui/_index.csv` · `_skipped.csv` | **2 file** | 53.316 file `.json.gz` (142,7 MB) | **manifest** cho biết từng màn có bao nhiêu node/nút — đủ để thiết kế, không cần asset |

Hai món mở được ngay:

| Món | Số | Dùng vào đâu |
|---|---|---|
| `spine-events.csv` | **21 dòng** (rig × animation × time × event) | xác nhận rig boss 1 **chỉ có 2 tên event** (`Stop` ×5 trong `Attack3`, `Banplasma` trong `Attack4`) ⇒ `ANIMATION_SCRIPT.md` §2.2 lên **A** cho *tập ứng viên* |
| `_index.csv` | **797 instance · 117 lớp · 150.131 node · 5.831 nút** | `UI.md` §9 — độ sâu bố cục từng màn; giải thích luôn vì sao **117 ≠ 125** |

**Một điều phải ghi:** `_index.csv` (117 lớp) là **tập con** của `screens.csv` (125 lớp); 8 lớp
thiếu gồm 4 tên lớp lồng và 7 màn/popup **không có instance nào trong dump**. Đừng tráo hai số.

---

## 11. Kéo bản thứ hai (24/10) — **74 file / 5,1 MB**, không kéo 53.316 file raw

Ref của tôi khi đó vẫn là `019e704d1` (⚠️ **sai** — nhánh dữ liệu **đã** đi tiếp; xem §12/§13. Đây đúng là
lỗi "báo không có commit mới" mà handoff nhánh dữ liệu đã bắt). Nhưng `git ls-tree`
so hai cây cho thấy **nội dung của cùng commit đó mà ta chưa có**: **171 file** ngoài
`reverse-engineering/raw/`. Đã kéo **72 file** (thêm 2 file sửa):

| Nhóm | File | Vì sao kéo |
|---|---:|---|
| `docs/apk-analysis/*_Director.csv` | **16** | field **serialize thật** của từng lớp đạo diễn: `stateAppear`…, `gun1..3Slots`, `allHand8/9Points`, `allHpParents` |
| `docs/apk-analysis/*_AnimationEvents.csv` | **14** | instance + `_gameobject` ⇒ **ghép prefab ↔ lớp handler** |
| `docs/apk-analysis/Boss*_AttackPhases.csv` · `_AttackTypes` · `_ExplosionTimer` | **7** | bộ phận boss có HP riêng + kiểu đòn |
| `docs/apk-analysis/*.json` · `03-il2cpp-*` | 9 | inventory/strings của bản APK |
| `reverse-engineering/il2cpp/interesting-classes.cs` | 1 | **dump lớp có tên field + offset** (T2) |
| `reverse-engineering/il2cpp/{stringliteral,field-defaults,ia-*}.json` | 4 | literal + `fieldDefaultValues` từ `global-metadata.dat` |
| `docs/CROSS_BRANCH_20330d0e.md` · `HANDOFF_AI_TASKS.md` | 2 | nhánh kia viết về **ta**; 2 nhận định của họ về ta đã kiểm |

**Không kéo (có lý do, ghi lại):**

| Bỏ | Dung lượng | Vì sao |
|---|---:|---|
| `reverse-engineering/raw/ui/**` 53.316 file `.gz` | 142,7 MB | chỉ cần 2 manifest `.csv` đã kéo từ trước |
| `datas/ui_text_keys.csv.gz` | **7,1 MB** | vượt trần 5 MB/file; nội dung là key text UI, `12-localization.csv` đã đủ dùng |
| `tools/**` (34 file) · `tests/**` (3) · `.github/workflows` (6) | ~0,3 MB | là **pipeline của họ**; ta không chạy lại được mà dễ lệch với tool của ta |

### 11.1 Ba thứ **đóng được** ngay nhờ 74 file này

| Trước | Sau | Bằng chứng |
|---|---|---|
| 8 tên entry boss 1: **suy từ offset** | ✅ **đọc thẳng giá trị** `stateAppear = Xuathien` … (`Boss-39002`, **1** instance) | claim **T1** |
| 12 handler: chỉ biết **offset** `0x20…0x78` | ✅ **biết tên field**: `onAnimationEndedEvent` · `die` · `onCallAttack1Event` … `onAttack9EndEvent` | claim **T2** |
| `BossSpineEventHandler`: "2 slot chuỗi **chưa biết tên**" | ✅ **5 field**: `attackEventName` `0x20` · `preAttackEffectEventName` `0x28` · `skeletonAnimation` `0x30` · `onAttack` `0x38` (`UnityEvent`) · `chargeEffect` `0x40` ⇒ **cơ chế đọc trọn**: event trước đòn **bật** hiệu ứng, event đòn **tắt + gọi `UnityEvent`** | claim **T3** |

Và **ma trận** `*_Director` ↔ `*_AnimationEvents` trên **39 prefab `Boss-*`**: **18** có director ·
**16** có lớp handler · **13** có cả hai (claim **T4**). Tên lớp **không** theo số prefab
(`Boss-39012` → `Boss10_*`), nên mọi phép ghép phải dùng `_gameobject`.

### 11.2 Ba thứ **vẫn** chưa

1. **Giá trị 2 chuỗi** của `BossSpineEventHandler` — class vẫn **0 instance export**. Ứng viên duy nhất
   trong rig `skeleton__21` là `Stop` / `Banplasma` (`spine-events.csv`, **21 dòng** dữ liệu).
2. **Ai gán 12 delegate** — T2 của `HANDOFF_ANIM_RAW.md` **hẹp lại** còn đúng câu này (tên + offset đã có).
3. **`Boss_1_Animation`** (lớp 5 lần `String.op_Equality`) vẫn không có trong `interesting-classes.cs`
   (file này **lọc theo từ khoá**, không phải dump toàn bộ) và không có instance export.

---

## 12. Đồng bộ thật (25/10) — **"không có commit mới" là sai**, lỗi ở refspec của tôi

### 12.1 Lỗi gốc: `remote.origin.fetch` chỉ theo dõi **2 nhánh**

```console
$ git config --get-all remote.origin.fetch
+refs/heads/main:refs/remotes/origin/main
+refs/heads/arena/20330d0e-...:refs/remotes/origin/arena/20330d0e-...
```

Nhánh dữ liệu **không** nằm trong refspec ⇒ `git fetch origin` **không bao giờ** cập nhật
`origin/arena/ef6b75ef-…`. Bốn lần trước tôi chạy `fetch` rồi `git log origin/arena/ef6b75ef-…` và thấy
"0 commit mới" — thực chất là đang đọc một **ref đóng băng ở `019e704d1`**, không phải remote.

| kiểm | lúc chưa sửa | sau khi sửa refspec |
|---|---|---|
| `git ls-remote origin` (remote thật) | `9aed767b1…` | `9aed767b1…` |
| `git rev-parse origin/arena/ef6b75ef-…` | **`019e704d1`** ❌ | **`9aed767b1`** ✅ |

`ls-remote` nói một đằng, ref local nói một nẻo ⇒ **`ls-remote` là nguồn, ref local chỉ là cache**.
Từ nay: báo "không có commit mới" **phải** kèm `ls-remote` cùng thời điểm.

### 12.2 Nhánh dữ liệu có **10 commit** sau `019e704d1`

| commit | nội dung |
|---|---|
| `1250a8a82` | audit `UnityEvent` persistent + giữ **full controller graph** ⇒ **T3 · T4** |
| `d1efb610e` | giải controller graph, xác minh callback Inspector, **instance `Boss_1_Animation`** |
| `7f3158c12` | `HANDOFF_SPEC_REVIEW_71b1e9861.md` — **review lỗi suy luận của nhánh này** |
| `921dc909b` · `daa2c3a03` | export native/typetree **UI đầu game** + **thân coroutine** |
| `d06046eec` | phủ **stage 1–3**, report 42 |
| `d05a147f0` | gate tutorial, **drawing inputs**, report 43 |
| `c570485c5` · `03195916e` · `b1…` (bot) | raw cho lượt export mới |
| `9aed767b1` | `HANDOFF_DATA_SYNC.md` — chỉ ra đúng lỗi refspec + lỗi verifier dưới đây |

### 12.3 Sáu con số **đổi** giữa hai snapshot (đã cập nhật doc theo `9aed767b1`)

| chỉ số | `019e704d1` (doc cũ) | **`9aed767b1` (nay)** | ai bắt được |
|---|---:|---:|---|
| lượt spawn / spawner | 22.461 / 11.095 | **22.452 / 11.089** | claim **H2** |
| `rate = 0` | 2.371 | **2.365** | claim **I3** |
| `boss_hp.json` | 254 | **256** | claim **P5** |
| `_index.csv` (UI) | 733 · 114 lớp · 103.227 node · 5.174 nút | **797 · 117 · 146.797 · 5.831** | claim **N2** |
| `ui_screens.json.gz` | 52.583 file · 7.980.772 node | **54.787 · 8.290.223** | claim **P6** |
| lớp `*_AnimationEvents` export | 14 lớp · 16 prefab | **18 lớp · 17 prefab** (còn **145/795** event chưa rõ lớp) | claim **S1 · T4** |

⇒ UI là chỗ **tăng nhiều nhất**: +64 màn, +37.570 node, +537 nút. Không phải "dữ liệu đứng yên".

### 12.4 Lỗi verifier: `ref_blob()` **local-first** — đã sửa

Bản trước đọc **file local trước**, chỉ vắng mới `git show ref` ⇒ `--ref <sha mới>` vẫn có thể trả dữ
liệu **cũ** mà không nói gì. Nay:

| cờ | việc |
|---|---|
| `--ref <sha>` | đọc **ref trước**; local chỉ để fallback và bị ghi là `local-fallback` |
| `--provenance` | in bảng `nguồn · blob SHA · byte · path` cho **mọi** input |
| `--provenance-log F` | ghi JSONL để dán vào báo cáo |
| `--strict-ref` | thoát **2** nếu có input **dữ liệu** nào không đọc từ ref |
| `--self-test` | dựng `datas/sprites.csv` **giả** trong thư mục tạm rồi kiểm chế độ explicit-ref **bỏ qua** nó |

Chạy thật: `python3 tools/verify-claims.py --self-test` → **PASS** ("bỏ qua bản local giả").
Đối chiếu hai chế độ sau khi đồng bộ: **125 PASS · 0 FAIL · 2 SKIP** ở **cả** local và
`--ref 9aed767b1 --strict-ref` (0 input dữ liệu nào là local).

### 12.5 Đã kéo gì (snapshot `9aed767b1`)

| Nhóm | Số | Dung lượng | Ghi chú |
|---|---:|---:|---|
| `docs/apk-analysis/*.md` mới (39–43) + `HANDOFF_*` | 7 | ~90 KB | report T3/T4/UI + **review của họ về ta** |
| `docs/apk-analysis/*.csv` (Director/AnimationEvents/Board…) | 107 | 5,18 MB | có **`Boss_1_Animation.csv`** — lớp tưởng chết |
| `datas/*` (trừ `ui_text_keys`) | 27 | 4,8 MB | `waves.json`, `ui_screens.json.gz`, `boss_hp`, `enemy_hp` |
| `reverse-engineering/raw/{animation-audit,typetrees,ui-audit}` | 20 | 2,5 MB | controller graph + persistent calls + UI audit |
| `reverse-engineering/raw/ui/_index.csv` · `_skipped.csv` | 2 | 52 KB | manifest UI **797** màn |
| **Không kéo** | — | — | `raw/ui/*.gz` (53.316 file, 142,7 MB) · `datas/ui_text_keys.csv.gz` (**7,7 MB** > trần 5 MB) |

### 12.6 Trạng thái bàn giao sau snapshot này

| task | trạng thái | bằng chứng |
|---|---|---|
| **T1** 3 lớp thiếu instance | 🟡 **2/3 xong**: `Boss_1_Animation` **1 instance** (`Boss-39001`), 8 field `state*`; còn `Boss1_AnimationEvents` · `BossSpineEventHandler` | `Boss_1_Animation.csv`, report 41 |
| **T2** ai gán 12 delegate | 🔴 **mở** — nhánh kia nói rõ: chưa có **typed xref toàn binary**, `str [xN,#0x20]` không đủ nếu chưa biết type của `xN` | report 41 §T2 |
| **T3** UnityEvent | ✅ **xong** — 1.335 field · 111 không rỗng · 115 call (114 nhóm enemy/boss) | report 39 |
| **T4** Animator graph | ✅ **có raw** — 52 controller / 63 prefab / 303 param / 357 transition (302 condition) — **chưa** phải 87/87 | report 40 · `animator-controller-graphs.jsonl.gz` |

Ngoài ra nhánh kia **bắt hai lỗi của tài liệu này**, đã sửa:
`Boss-39001` dùng **`Boss_1_Animation`** (UnityEvent `defeatEvent`→`OnDefeated`, `burstEvent`→`OnBusrtItems`),
`Boss-39002` mới dùng `Boss1_Director` — xem `ANIMATION_SCRIPT.md` §3.4.

---

## 13. Đồng bộ **ba snapshot** `9aed767b1` → `1989defc2` → `0a42eaa42` (25/10, sau bàn giao `HANDOFF_DATA_SYNC.md`)

Bàn giao của nhánh dữ liệu (`docs/HANDOFF_DATA_SYNC.md`, blob `1c88a027`) nói rõ: **cấm** lặp lại
"nhánh dữ liệu không có commit"; phải so **`ls-remote` với `rev-parse` sau fetch**; nếu bot đẩy tiếp
thì **ghi hai snapshot**. Đây là bản ghi đúng.

### 13.1 Kiểm ref — **ba** mốc, không phải một

| lúc | `git ls-remote origin refs/heads/arena/ef6b75ef-…` | `git rev-parse origin/arena/ef6b75ef-…` | khớp |
|---|---|---|---|
| trước fetch #1 | `9aed767b1313690d29b3c3ff764f838a8f4c4ebd` | `9aed767b1…` | ✅ |
| **sau fetch #1** | **`1989defc281461cee18a4352078ab5e67a2c8516`** | **`1989defc2…`** | ✅ |
| **sau fetch #2** (bot đẩy tiếp) | **`0a42eaa422d961c0de1f86252e86a0810b21cf7d`** | **`0a42eaa42…`** | ✅ |

⇒ **ref của nhánh dữ liệu là mục tiêu di động** (bot đẩy trong lúc tôi đang đọc). Đúng như handoff dặn:
ghi **nhiều snapshot**, không kết luận "không có commit". Số commit sau `019e704d1`: **12** (tại
`1989defc2`) rồi **14** (tại `0a42eaa42`).

Hai lần `git fetch` in ra:

```
9aed767b1..1989defc2  arena/ef6b75ef-… -> origin/arena/ef6b75ef-…
1989defc2..0a42eaa42  arena/ef6b75ef-… -> origin/arena/ef6b75ef-…
```

⇒ **có** commit mới ở **cả hai** lần. Đếm: `019e704d1..9aed767b1` = 10 · `9aed767b1..1989defc2` = 2 ·
`1989defc2..0a42eaa42` = 2 ⇒ **14 commit** sau `019e704d1`.

| commit | nội dung | ảnh hưởng nhánh spec |
|---|---|---|
| `1989defc2` | `fix(ui): expose traversal truncation and expand capped map layout` | chỉ `tools/apk-analyze/ui_layout.py` — **ngoài phạm vi**, không có dữ liệu mới |
| `a2fac1df7` | `research(ui): preserve scoped font material camera context and sprite geometry` | chỉ `tools/apk-analyze/ui_render_context.py` + `ui_layout.py` — **ngoài phạm vi** |
| `9aed767b1` | `docs: clarify data branch updates and stale local-first verifier inputs` | **đã đọc** (xem 13.2) |
| `c570485c5` | report 39–43 + raw lượt kế | đã kéo/đọc một phần |
| `d05a147f0` | gate tutorial + `43-ui-drawing-readiness.md` | **đã đọc**, đã import vào `UI.md` §9.2 |
| `d06046eec` | coverage stage 1–3, report 42 | đã đọc |
| `0a42eaa42` | tutorial panel + Endgame callback, report 44, `visual-coverage.json` | **đã import 5 file** (13.4) |
| `e690da837` | re-export `03-il2cpp-files`, `04-unity-assets`, `18-pipeline-diagnostics`, `dump.cs.gz` | **chưa** đọc bản mới — ghi "chưa đồng bộ" |
| `921dc909b` · `daa2c3a03` | export native/typetree early UI | `early-native-gates.json` đã có |

### 13.2 Đã đọc thật — kiểm bằng blob SHA-1, không bằng "verifier PASS"

`git hash-object <file local>` so với `git rev-parse 9aed767b1:<file>`:

| file | blob | kết quả |
|---|---|---|
| `docs/HANDOFF_DATA_SYNC.md` | `1c88a027` | **SAME** — bàn giao đọc đúng bản của `9aed767b1` |
| `docs/apk-analysis/43-ui-drawing-readiness.md` | `a169e628` | **SAME** |
| `reverse-engineering/raw/ui-audit/early-native-gates.json` | `e3119293` | **SAME** |
| `reverse-engineering/raw/ui-audit/drawing-inputs.json.gz` | `3dec031b` | **SAME** |
| `reverse-engineering/raw/ui-audit/early-stage-coverage.json.gz` | `751e4160` | **SAME** |

⇒ 5/5 file của snapshot `9aed767b1` trùng **byte-for-byte** với bản local ⇒ số liệu import từ chúng
là của snapshot đó, không phải của `019e704d1`.

### 13.3 Chạy verifier trên **ref mới** (không local-first)

`python3 tools/verify-claims.py --ref 1989defc2 --strict-ref` — chế độ này đọc `git show` **trước**,
mọi input **dữ liệu** rơi về local đều **exit 2**. Kết quả: **139 PASS · 0 FAIL · 2 SKIP**, `exit 0`.

`--provenance` lúc đó: **186 input = `ref:1989defc2`** · **0 input dữ liệu local** · **1
`local-fallback`** — chính là `docs/spec/DESIGN_QUESTIONS.md`, file **của nhánh spec** (không tồn tại
trên nhánh dữ liệu nên buộc phải đọc local; `local_inputs()` chỉ tính `datas/`,
`reverse-engineering/`, `docs/apk-analysis/`).

### 13.4 Snapshot thứ ba `0a42eaa42` — import thật (5 file, ghi source SHA)

`git checkout 0a42eaa42 -- <path>` cho 5 file, mỗi file ghi blob:

| file | blob tại `0a42eaa42` | nội dung |
|---|---|---|
| `docs/apk-analysis/44-ui-tutorial-panels-and-gaps.md` | `a97fc0ce` | **layout tutorial đã có** (8 ref / 7 GO) + callback Endgame `0x126d3cc` |
| `reverse-engineering/raw/ui-audit/tutorial-texts.csv` | `f8c27aa8` | 19 dòng · 7 field · 6 GO · 13 key · 17 dòng có tiếng Việt |
| `reverse-engineering/raw/ui-audit/visual-coverage.json` | `cdd9455f` | 15 màn · 14.730 node · 7.087 `SpriteRenderer` · 1.913 TMP · `Board_Maps` **chạm trần 6.000** |
| `reverse-engineering/raw/ui-audit/early-native-gates.json` | `4ef70ddc` | thêm check `endgame_callback_reveals_continue_and_increments_tutorial` ⇒ **6/6 PASS**, 6 call target |
| `docs/HANDOFF_AI_TASKS.md` | `141202503` | việc kế: Map **chưa** full coverage (đạt trần), raw mới phải nghiệm thu trước khi bỏ OPEN |

**Đã cập nhật vào:** `UI.md` **§9.2** (cảnh báo trần 6.000) + **§9.3** (bảng 7 panel tutorial + nhánh
Endgame), `COVERAGE_AUDIT.md` hàng UI. Claim **Y2** sửa `5/5 → 6/6`, thêm **Z1–Z3**.

### 13.4b Đã import từ snapshot thứ hai

| việc | vào đâu |
|---|---|
| 11 board có bộ đầu vào vẽ (10.710 node · 100 % `local_pos` · 4.987/5.067 sprite candidate · 312/317 key Việt) | `UI.md` **§9.2** |
| gate tutorial native (`hasTutStage1/2/3`, delay **9 / 2 / 3 s**, 5/5 check PASS) | `UI.md` **§9.2** |
| 107 CSV `docs/apk-analysis/*.csv` + 5 report 39–43 | commit `bc0e11bf2` |

### 13.5 Chưa đồng bộ (ghi đúng chữ "chưa", không suy)

- `1989defc2` / `a2fac1df7`: **chỉ sửa `tools/apk-analyze/**`** ⇒ không có file dữ liệu/tài liệu để kéo;
  nếu sau này exporter đó xuất raw **mới** thì phải kiểm lại `_index.csv` (đang là 797 dòng).
- `early-stage-coverage.json.gz` (1,99 MB): **chưa** phân tích — report 42/43 mới đọc phần kết luận.
- `Board_Maps`: **chưa** có độ sâu đầy đủ (đạt trần 6.000 ở snapshot này) ⇒ mọi số của `Board_Maps`
  phải ghi **cận dưới**; `handoff AI tasks` nói phải chờ raw tái xuất rồi mới bỏ OPEN.

---

## 14. Kéo bản `55bd18ac8` (25/10, sau khi tự chốt *"feel bỏ, script là đủ"*)

**Refspec:** `git fetch origin arena/ef6b75ef-windwings-space-shooter-game-p` → `FETCH_HEAD` = **`55bd18ac8`**
(kiểm bằng `git rev-parse FETCH_HEAD`; `ls-remote` xác nhận trước khi kéo). **Không** merge, không đổi nhánh.

**Đã kéo 44 file** (`--diff-filter=AM`, chỉ `datas/` + `docs/apk-analysis/`, **không** kéo `reverse-engineering/raw`
= 53.320 file ~142 MB):

| nhóm | file |
|---|---|
| `datas/` **mới** | **`ui_text_keys.csv.gz`** ← đóng đúng phần *"thiếu text key tutorial"* |
| `datas/` cập nhật | `waves.json` · `boss_hp.json` · `enemy_hp.json` · `ui_screens.json.gz` · `anim_clips.json.gz` · `animator_map.csv.gz` · `spine_anim.json.gz` · `formula_traces.json.gz` · `particle_systems.csv.gz` · `prefab_joins.csv.gz` |
| **CSV lớp script (mới)** | `Boss1_Director.csv` · `Boss4_Director.csv` · `Boss5_Director.csv` · `Boss6_Director.csv` · `Boss12_Director.csv` · `Boss15_Director.csv` · `Boss18_Director.csv` · + **16** `Boss*_AnimationEvents.csv` (gồm `Boss6_Mini_`) · `Boss4_ExplosionTimer.csv` · `AirFree_Spawner.csv` |
| report mới | `45-ui-routing-and-persistence.md` · `46-ui-render-context-validation.md` · `47-scoped-ui-and-home-loader.md` |

### 14.1 Năm con số **đổi** vì dữ liệu mới (đã sửa doc + claim, không nới claim)

| chỉ số | trước | **sau (`55bd18ac8`)** | claim | sửa ở |
|---|---:|---:|---|---|
| spawner | 11.089 | **11.092** | **H2**, **I3** | `ANIMATION.md` §4, `DESIGN_READINESS.md` §3 |
| `rate = 0` | 2.365 | **2.370** | **I3** | `DESIGN_READINESS.md` §3, bảng §3.1 |
| lượt spawn | 22.452 | **22.460** | **H2** | `ANIMATION.md` §4 |
| HP id boss | 256 | **253** | **P5** | `COVERAGE_AUDIT.md` §3 |
| UI layout file / node | 54.787 / 8.290.223 | **55.584 / 8.435.335** | **P6** | `COVERAGE_AUDIT.md` §3–§4, `UI.md` |
| `*_Director` ↔ `*_AnimationEvents` | 18 / 18 (lệch 3) | **18 / 16 (lệch 5 + 3)** | **T4** | `ANIMATION_SCRIPT.md` §3.2 |

⇒ **Bài học lặp lại lần thứ sáu:** mỗi lần kéo dữ liệu là một lần **5–6 con số phải sửa**. Vì vậy mọi con số
trong `docs/spec/` đều phải nằm trong `tools/verify-claims.py`; nếu không, lần kéo sau sẽ lại "phát hiện" nó sai.

### 14.2 Cái **không** đổi (để khỏi làm lại)

- 797 màn cấp cao · 146.797 node · 5.831 nút · 125 lớp · 117 lớp trong `_index.csv` (**P6**, **N2**).
- 250 map (**I4**), 282 wave (**H2**), 39 prefab `Boss-*` (**T4**, **X1**).
- 1.554 `unclassified` / 2.197 asset (**AB1**) — bộ asset **không** được xuất lại trong bản này.

### 14.3 Chưa đồng bộ (ghi đúng chữ "chưa")

- `reverse-engineering/raw/**` của `55bd18ac8`: **chưa** kéo (142 MB, 53.320 file) — chỉ kéo khi có task raw cụ thể.
- `.github/**` của bản đó: **chưa** kéo (workflow khác với CI đang chạy 5 check của nhánh này).
- `docs/handoff/**`: **chưa** đọc bản `55bd18ac8`.

---

## 15. Đồng bộ `9edc21f4d` (25/10) — kéo **phần lớn**, từ chối **phần bị thoái hoá**

`ls-remote` = `9edc21f4d5a9f8be57094e863f81e11100a6fb21`; `git rev-parse FETCH_HEAD` khớp. Chặng này
dài **11 commit** sau `55bd18ac8`, **1.125 file** thay đổi. Nguyên tắc giữ nguyên: **fetch đúng ref,
`git checkout FETCH_HEAD -- <file>`, không merge / không rebase** — nhánh này không có commit nào của
nhánh dữ liệu.

### 15.1 Đã kéo (**425** file)

| nhóm | nội dung | ghi chú |
|---|---|---|
| `datas/` | `waves.json` · `ui_screens.json.gz` · `ui_text_keys.csv.gz` | xem §15.3 |
| manifest UI | `reverse-engineering/raw/ui/_index.csv` | **797 · 117 · 150.131 node · 5.831 nút** |
| bằng chứng native | `raw/ui-audit/` (**253** file: 34 mới trong chặng này, 219 file đã có ở `55bd18ac8` nhưng nhánh này **chưa từng kéo**) · `raw/ui/render-context/` (**5**) · `raw/ui-flow-review/` (**2**) · `raw/runtime-probe/` (**15**) | ~7,1 MB; **275 thêm / 1 sửa**, không đè dữ liệu đã dùng |
| report **mới** | `docs/apk-analysis/48-runtime-probe-review.md` · `49-visual-ui-stage-flow.md` · `50-stage2-stage3-ui-from-raw.md` + 3 contact sheet | 3 JPG ≈ 1,2 MB |
| **asm bổ sung** | `reverse-engineering/raw/il2cpp-consts/` từ **69 → 139** file `.asm.txt` (**140 file**, 2,47 MB) — gồm **`GP_Tutorials`** (46 method), `Board_Maps`, `Board_Stage`, `Board_Home`, `Board_Endgame`, `Board_Drones`, `DataTutorials`, `SkipTutorial`, `Tut_Settings*` | đây là **lần đầu** nhánh này có thân hàm tutorial |

### 15.2 **Từ chối** kéo — và bằng chứng tại sao

Bản mới chạy lại dumper với **cách xác định gốc cây khác**, nên nhiều file *cùng ruột* nhưng
`gameobject` bị **cắt cụt hoặc đổi gốc**. Đã kiểm từng nhóm:

| nhóm | phát hiện | ví dụ đo được | quyết định |
|---|---|---|---|
| `raw/typetrees/` (**20** file khác) | **chỉ** khác trường `gameobject`; bỏ trường này thì 20/20 file **giống tuyệt đối** (đã so bằng JSON sort) | — | **không kéo** (không thêm thông tin) |
| `reverse-engineering/scriptableobjects/` (**71** CSV) | cùng dạng: giá trị giữ nguyên, đường dẫn bị cắt | `Tab (5)/Boss/…/Gun5/Gun1/Gun5` → `Gun1/Gun5` | **không kéo** |
| `docs/apk-analysis/*_Director.csv` · `*AnimationEvents.csv` | cùng dạng; **nhưng** đổi gốc làm **T4 nhảy (18, 16, 13) → (18, 19, 16)** | 3 prefab `Boss-*` “mới” chỉ vì dòng CSV còn lại đúng tên gốc | **không kéo** — không phải thêm event thật |
| `datas/boss_hp.json` | gộp theo gốc ⇒ **gốc bị cắt làm sai phép gộp** | `Boss-37004`: cũ **6 instance / hp_max 4.000.000** ([68.000, 4.000.000]) → mới **4 instance / 68.000** | **không kéo** |
| `datas/enemy_hp.json` | HP **không đổi** (981 dòng, cùng `path_id`), chỉ `path` đổi: 268 dòng **đầy hơn** (`Board_FightBoss/Parent/…`) nhưng một số **cụt hơn** (`ScrollView/…` thay cho `Tab (5)/…`) | `Tab (5)/Boss/…/HP3` ⇄ `ScrollView/…/HP3` | **không kéo** — trộn hai kiểu gốc là tự tạo lỗi |

⇒ Năm nhóm trên **giữ bản `55bd18ac8`**. Hệ quả kiểm chứng: `--ref 9edc21f4d --strict-ref` **FAIL đúng 2
claim** là **P5** (253 → 244 boss HP) và **T4** (16 → 19 AnimationEvents) — cả hai đều đọc file đã từ chối.
`--ref 55bd18ac8 --strict-ref` thì FAIL đúng 5 claim vừa cập nhật (H2 · I3 · M3 · N2 · P6).
**Không có chế độ ref nào làm cả 157 claim cùng đúng** — vì cây làm việc là **lai có chủ ý**; chạy
local (`python3 tools/verify-claims.py`) cho **155 PASS · 0 FAIL · 2 SKIP**. Đây là lần đầu tiên **không** kéo toàn bộ một snapshot:
lý do là *dữ liệu mới không nhất quán*, không phải *lười*. Nếu nhánh dữ liệu sửa lại cách lấy gốc
(một gốc duy nhất cho mọi object), kéo lại cả 4 nhóm là việc của một lệnh.

### 15.3 Năm con số **đổi** (đã sửa doc + claim)

| chỉ số | `55bd18ac8` | **`9edc21f4d`** | claim | sửa ở |
|---|---:|---:|---|---|
| node UI (`_index.csv`) | 146.797 | **150.131** | **N2**, **P6** | `UI.md` §9, `COVERAGE_AUDIT.md` §1/§3/§4, `README.md`, `DATA_SYNC.md` §13 |
| text node UI | 17.066 | **17.276** | — | `UI.md` §9 |
| node UI lớn nhất | 12.000 (**trần walker**) | **15.334** | **P6** | `UI.md` §9, `COVERAGE_AUDIT.md` §1 |
| node layout (`ui_screens.json.gz`) | 8.435.335 | **8.437.020** | **P6** | `COVERAGE_AUDIT.md` §3 |
| dòng cấu hình / lượt spawn | 11.092 / 22.460 | **11.094 / 22.482** | **H2**, **I3**, **M3** | `ANIMATION.md` §4, `DESIGN_READINESS.md` §3, `ENCOUNTERS`-related |

> ⚠ Bảng trên là **log của vòng 3** (`61d5385`). Số hiện hành (bản `622b700e5`) ở **§17.1** và §17.2:
> **11.089** dòng cấu hình · **23.757** spawner (`Σ copies`) · **22.451** entry · `rate = 0` **2.366**.

Hai hệ quả phụ, cũng đã sửa: `rate = 0` **2.370 → 2.371**; `rate = 0` **và** >1 quân
**1.203 → 1.206**. `rate` histogram mới: `1,0 → 7.740 · 0,0 → 2.371 · 0,5 → 532 · 2,0 → 163 ·
0,65 → 111 · 6,0 → 58`.

**Vì sao node UI tăng:** file cũ của `Board_Maps` ghi `walk_diagnostics = {node_limit: 12000,
truncated: true, pending_transforms: 2760}`; bản mới `{node_limit: 50000, truncated: false,
pending_transforms: 0}`. Nói cách khác **12.000 là trần của walker**, và mọi tổng node trước đây là
**cận dưới**. Nay `Board_Maps` **15.334/15.334** node ⇒ tổng **150.131** là số đọc hết, không phải cận.

**Vì sao wave tăng 2:** **wave 2** thêm 2 spawner **mới** `Left`/`Right` (`point_range`, 7 × `CB-30002`,
`rate = 0`) = +14 slot; **wave 281** từ **47 → 55** quân (một spawner được ghi lại với 8 slot) = +8.
Bảy wave còn lại (25 · 26 · 49 · 104 · 137 · 163 · 198) chỉ **đổi tên** spawner trùng tên
(`CB1 (20)` ⇄ `CB1 (35)`…) — **multiset không đổi**. Tập prefab **109 → 109**, không mất tên nào.

### 15.4 Hai con số **tăng vì asm nhiều hơn** (không phải vì game đổi)

| chỉ số | 69 file asm | **139 file asm** | claim | ghi chú |
|---|---:|---:|---|---|
| `WaitForSeconds` (site · hằng · biến) | 22 · 4 · 18 | **38 · 12 · 26** | **J8**, **W6** | **+16 site mới** nằm trong các lớp chờ của UI/tutorial (`Board_Home`, `Board_Maps`, `Board_Endgame`, `GP_Tutorials`); 4 hằng vẫn là **0,5 / 1 / 2 / 3 s** |
| `timeScale` / method aim | 0 / 0 | **0 / 0** | **AF2**, **AF3** | mẫu số tăng, kết luận **không đổi**: hit stop và aim assist vẫn **không có** |

**Claim mới AG1** (mức **A**): `.cctor` của `GP_Tutorials` tại **`0x14fb4e0`** đặt
`MaxIndexTutorial = 4` (offset `0x4`) và `indexTut = −1` (offset `0x10`) ⇒ tutorial đúng **5 bước
(0…4)**, trạng thái “chưa bước nào” là **−1**. Trước bản này chỉ suy từ **5 field `tutobj*`**; nay có
**giá trị thật trong asm**. Chi tiết ở `SCRIPTS.md` §0.5.1.

### 15.5 Ghi chú dữ liệu

- `datas/ui_text_keys.csv.gz`: **+96 dòng / −70** (net +26) — chủ yếu là `Board_Maps/.../TextStageIndex`
  của các stage **81–92** mà bản cũ **không thấy vì bị cắt ở 12.000 node**. Đây là bằng chứng phụ
  cho việc trần cũ làm **mất dữ liệu thật**.
- `datas/ui_screens.json.gz` (55.584 màn) **vẫn** có `Board_Maps = 12.000` ⇒ **dataset này vẫn bị
  chặn ở 12.000**; chỉ `_index.csv` (đi từ `raw/ui`) là đọc hết. **Đừng tráo hai nguồn**: 8.437.020
  là tổng của dataset bị chặn, 150.131 là tổng của walker không chặn.
- `reverse-engineering/il2cpp/dump.cs.gz`: khác **header gzip**, nội dung **y hệt** (SHA-1 sau khi giải
  nén trùng) ⇒ không kéo.

### 15.6 Chưa đồng bộ (ghi đúng chữ "chưa")

- **803** file `reverse-engineering/raw/ui/*.json.gz` (mỗi màn một file; cả cây là **55.591 file /
  142 MB**) — vẫn chỉ giữ **manifest** `_index.csv` như chính sách cũ. Muốn xem bố cục một màn cụ thể
  thì kéo **đúng file đó**.
- `.github/**`, `tools/verify/*.py`, `tests/` của bản `9edc21f4d`: **chưa** kéo (là mã của nhánh kia).
- `docs/HANDOFF_AI_TASKS.md` của bản đó: **chưa** đọc.

### 15.7 Kéo tiếp tới **`575113776`** (cùng ngày)

Trong lúc đang ghi §15, nhánh dữ liệu đi thêm **7 commit** (`9edc21f4d` → **`575113776`**). Đã fetch +
`ls-remote` khớp, rồi kéo **83 file**: `raw/ui-audit/` (+**80 file**: `MapController` **2.584 dòng asm**,
`ScenesManager`, `stage23-rodata.json` +254 dòng, `tutorial-consumer-flow.json.gz`), cập nhật
`50-stage2-stage3-ui-from-raw.md` và thêm **`51-tutorial-consumer-equipment-continue.md`**.

Điểm quan trọng: cửa sổ này **không** đụng `datas/` hay CSV lớp script nào ⇒ **0 con số phải sửa**,
verifier vẫn **156 PASS · 0 FAIL · 2 SKIP**. Đây là lần đầu một lần kéo **không** phá con số nào —
vì thứ được thêm là **thân hàm native**, không phải dữ liệu serialize.

Còn **chưa** kéo (giữ nguyên chính sách): `.github/**`, `tools/verify/*.py`, `tests/`, `docs/HANDOFF_AI_TASKS.md`
của nhánh dữ liệu.

## 16. Kéo **bằng chứng review** từ `7e0da2ee3` (25/10) — phục vụ R1/R2

Review `25c367aca` (PR #12) kết luận dựa trên raw ở nhánh dữ liệu. Để **sửa được chứ không phải tin lời**,
kéo đúng những file review dùng làm bằng chứng:

| nhóm | file | cỡ |
|---|---:|---:|
| báo cáo phân tích | `docs/apk-analysis/52-…` → `58-…` | 7 file · 62 KB |
| template wave đầy đủ | `reverse-engineering/raw/early-waves/` | 18 file · 852 KB |
| luồng mission/endgame | `reverse-engineering/raw/endgame-missions/` | 4 file · 536 KB |
| mission exit từ UI | `reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz` | 1 file · 19 KB |

`ls-remote` khớp `7e0da2ee3b07`; kéo bằng `git show <ref>:<path> > <path>` — **không merge, không checkout**.

### 16.1 `sha256` (16 ký tự đầu) — để phát hiện sửa tay

| file | bytes | sha256 |
|---|---:|---|
| `reverse-engineering/raw/early-waves/datas_maps_chapter2_waves_wave_0005__38205.json.gz` | 16,619 | `9ccd2e75616058ff` |
| `reverse-engineering/raw/early-waves/datas_maps_chapter2_waves_wave_0113__21456.json.gz` | 42,654 | `f700f510f4d211cf` |
| `reverse-engineering/raw/early-waves/datas_maps_chapter2_waves_wave_0164__148637.json.gz` | 48,425 | `19c40be50f46278e` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_branch_evade_wave_0005__154465.json.gz` | 473,672 | `e78264fc00046185` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_branch_help_wave_0005__57863.json.gz` | 8,280 | `e58f766ed4822c47` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_branch_protect_wave_0005__213990.json.gz` | 9,101 | `a8bf0cfedc8cbac1` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_branch_specialenemies_wave_0005__213925.json.gz` | 11,690 | `087aeefccd730be3` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_challange0_wave_0005__213945.json.gz` | 9,090 | `bbca1cc286fa2047` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_challange1_wave_0005__57870.json.gz` | 8,284 | `fe1a3244ad629f95` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_challange2_wave_0005__57817.json.gz` | 13,138 | `4dbbfea6fa621b7d` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_challange3_wave_0005__109344.json.gz` | 19,226 | `c5400bcdcf2f2ad5` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_wave_0005__38187.json.gz` | 16,630 | `f8fbc687233e10df` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_wave_0113__21468.json.gz` | 42,616 | `0849781fab7d9db2` |
| `reverse-engineering/raw/early-waves/datas_maps_waves_wave_0164__148604.json.gz` | 48,355 | `965cdfb6e88ede69` |
| `reverse-engineering/raw/early-waves/default-enemy-components.json.gz` | 19,575 | `a4b69066d303f48b` |
| `reverse-engineering/raw/early-waves/index.json` | 5,259 | `4b232f4ad990bdb5` |
| `reverse-engineering/raw/early-waves/mission-denominators.json.gz` | 25,998 | `6b7f5299dc0f414d` |
| `reverse-engineering/raw/early-waves/resolved-default-waves.json.gz` | 6,632 | `51bd86535b8ee1af` |
| `reverse-engineering/raw/endgame-missions/boards_board_endgame__113205.json.gz` | 447,285 | `36032ed7b4949fa4` |
| `reverse-engineering/raw/endgame-missions/false-result-reachability.json.gz` | 28,728 | `33a8994ab9362030` |
| `reverse-engineering/raw/endgame-missions/index.json` | 558 | `b5b84ac0c06c20b1` |
| `reverse-engineering/raw/endgame-missions/mission-progress-flow.json.gz` | 57,210 | `7be31909326d5407` |
| `reverse-engineering/raw/ui-audit/enemy-exit-missions.json.gz` | 19,662 | `5d164df061397e99` |
| `docs/apk-analysis/52-game-scene-to-stage-map-waves.md` | 8,195 | `8bace55e66e3cca2` |
| `docs/apk-analysis/53-wave-spawner-endgame-gates.md` | 9,695 | `86b28aa1f1d20828` |
| `docs/apk-analysis/54-exact-early-wave-resource-prefabs.md` | 6,246 | `922ddaeb0039f380` |
| `docs/apk-analysis/55-enemy-pool-active-list-mission-thresholds.md` | 7,825 | `4dc12e08653c32f7` |
| `docs/apk-analysis/56-early-stage-mission-denominators.md` | 9,268 | `7172bf41e2d3ad2a` |
| `docs/apk-analysis/57-endgame-mission-stars-save-continue.md` | 11,650 | `e754d8abee4926f3` |
| `docs/apk-analysis/58-false-result-target-advance-reachability.md` | 9,380 | `d92094bcd97e1069` |

### 16.2 Vì sao kéo đúng mấy file này

| review | cần gì | file |
|---|---|---|
| **R1** fallback mode + mảng `pct` + mẫu số | mẫu số stage 2/3, luồng mission, `GetStarStage*` | `mission-denominators`, `mission-progress-flow`, `enemy-exit-missions`, report 56/57 |
| **R2** dedup theo tên | **cùng wave khác `root`** (normal vs Chapter2) + `Call_Data` pathID | 3 cặp `datas_maps_[chapter2_]waves_wave_*` |

### 16.3 **KHÔNG con số nào đổi — chỉ đổi đơn vị** (tự sửa lần 2, 25/10)

Lần đầu tôi viết ở đây "dữ liệu cũ sai, export nhân đôi". **Sai.** Đo lại thì ra:

| cột cũ | thực ra là | bằng chứng |
|---|---|---|
| "Spawner 23.757" | **`Σ copies`** (lượt sinh) | 9/9 wave trong bảng cũ khớp `Σ copies` hôm nay (**AQ5**), và `Σcopies` của **cả** `waves.json` ở `8c6da25` **và** bản hiện tại đều = **23.757** |
| "median 62" | median **lượt**/wave | median dòng = 28,5; median lượt = **62** (**AQ4**) |
| "`point_range` 16.498" | số **lượt** | theo lượt: 16.498 / 4.199 / 1.688 / 686 / 686 — **khớp đúng** dãy `CROSS_BRANCH` §3c ghi từ trước (**AQ6**) |
| "`Wave_0163` 621" | lượt của wave đó | 257 dòng × `copies` = **621** ở snapshot cũ; **`622`** từ `622b700e5` (§17.1, **AQ5**) |

⇒ Bảng cũ **đúng số, sai nhãn cột**. Việc phải làm là **ghi rõ đơn vị**, không phải "sửa số".
`ENCOUNTERS.md` §1.1/§1.4/§1.5/§3 giờ in **cả hai cột**.

**Một chỗ vẫn là suy diễn:** `copies` (→ 45.659 "quân") **không có field tương ứng** trong raw
`Call_Data` đã kéo (`number` + `rate` thôi), nên mức bằng chứng là **B**, không phải A. Báo cáo `54`
bên nhánh dữ liệu cũng viết *"không coi `copies` là số đợt"*.

Kiểm bằng máy: **AQ1–AQ6**. AQ3 đếm `Call_Data` vs pathID trên 3 wave normal: **149 / 149 / 0 trùng**.

### 16.3b Các số 22.462 / 22.483 ở §9–§12 là **của snapshot cũ**

Đo lại trên `6ababbd31` (`datas/waves.json`): `Σ len(spawner.enemies)` = **22.451** (109 prefab, 0 `?`);
nhân `copies` = **45.659 quân**; **11.089** dòng spawner. Log cũ giữ nguyên số của lúc đó —
**đừng** lấy 22.462/22.483 làm hiện trạng.

| đại lượng | 22.462 (cũ) | hôm nay | vì sao đổi |
|---|---:|---:|---|
| `Σ len` entry | 22.462 | **22.451** | 3 wave `7xxx/9xxx` bị export lại (`DATA_SYNC` §17) |
| `Σ len × copies` = quân | 45.659 | **45.659** | **không đổi** — 7 entry chuyển từ `campaign` sang `unknown` |
| dòng spawner | 11.099 | **11.089** | dedup + chuyển đơn vị (§17.2) |

Min/median/max **không đổi**: `Σ len` 2 · 63 · 603; số dòng spawner 3 · 28,5 · 257.

### 16.4 Chưa kéo

- `tools/verify/peer_spec_review.py`, `tests/` của nhánh dữ liệu (mã của họ — chỉ đọc, không chép).
- Toàn bộ `docs/apk-analysis/` khác.
- `raw/ui/*` (803 file) — đã kéo ở §14, không kéo lại.

---

## 17. Đồng bộ lại 25/10 — nhánh dữ liệu `622b700e5` (11:33 UTC)

> **Nguồn:** `origin/arena/ef6b75ef-…-game-p` = **`622b700e5`**, fetch + `rev-parse` xác nhận, không merge.
> `git diff --stat 7e0da2ee3 622b700e5` = **1.121 file, +20.279 / −7.211**.
> File đã kéo về working tree: `datas/waves.json` · `reverse-engineering/raw/sprite-geometry/{index.json,
> resolved-geometry.json.gz}` · `raw/early-waves/movement-completion.json.gz` · `docs/apk-analysis/62-raw-audit-and-sprite-geometry.md`.

### 17.1 Wave: **tổng không đổi, nội dung 9 wave đã đổi**

Đo cả hai bản (`git show 35dceaa37:datas/waves.json` ↔ bản `622b700e5`):

| | bản `35dceaa37` | bản `622b700e5` |
|---|---:|---:|
| Wave | 282 | **282** |
| Dòng cấu hình | 11.094 | **11.089** |
| **Spawner** (`Σ copies` = `Call_Data` object) | 23.757 | **23.757** |
| Quân (`Σ len × copies`, mức B) | 45.659 | **45.659** |
| Enemy entry (`Σ len`) | 22.482 | **22.451** |
| `boss_hp.json` | 253 item | **246** |
| `enemy_hp.json` | 981 item · 73 hp | 981 · 73 (**không đổi**) |

⚠ **Tổng khớp không có nghĩa là dữ liệu không đổi.** Đo theo từng wave, **9 wave + `unknown`** đã đổi
`copies`/quân, và các thay đổi **bù trừ nhau**:

| Wave | Dòng | Lượt (`Σ copies`) | Quân |
|---|---:|---:|---:|
| `Wave_0002` | 127 → **125** | 250 → **248** | 787 → **768** |
| `Wave_0025` | 233 | 561 → **560** | 576 → **575** |
| `Wave_0026` | 42 | 84 → **83** | 225 → **224** |
| `Wave_0027` | 36 | 71 → **72** | 116 → **117** |
| `Wave_0048` | 10 | 18 | 111 → **116** |
| `Wave_0049` | 9 | 16 → **17** | 120 → **129** |
| `Wave_0137` | 48 | 235 → **229** | 233 → **227** |
| `Wave_0163` | 257 | 621 → **622** | 619 → **620** |
| `Wave_0198` | 13 | 457 | 715 → **713** |
| `unknown` | 20 → **17** | 56 → **63** | 103 → **116** |

⇒ Đây là lý do mọi bảng trong `ENCOUNTERS.md` phải **in cả dòng và lượt**, và lý do **không** được
dùng "tổng khớp" làm bằng chứng "không đổi". Mức: **A** cho số, **D** cho nguyên nhân (chưa đọc commit
nào trong 24 commit của nhánh sửa wave).

### 17.2 Sửa đơn vị lần 3: **11.089 là dòng cấu hình, KHÔNG phải spawner**

Đối chiếu chéo `class-inventory.csv` (`Call_Data` = **23.757** instance) với `Σ copies` trong
`waves.json` = **23.757** ⇒ hai nguồn khớp. Vậy:

- **spawner** = **23.757** `Call_Data` object;
- **dòng `waves.json`** = **11.089** — export gộp object trùng thành 1 dòng + cột `copies`;
- **quân** = 45.659 tham chiếu (mức **B**: `copies` không có field trong raw `Call_Data`).

Claim **AQ7** kiểm bằng máy (23757, 23757, 11089). Bản sáng 25/10 gọi 11.089 là "spawner" — **sai**,
đã sửa trong `ENCOUNTERS.md` §0/§1.1 và nhãn các bảng.

### 17.3 Sprite geometry (report 62) — **có toạ độ, chưa phải bằng chứng render**

`resolved-geometry.json.gz`: **2.185** Sprite · **66** SpriteAtlas · **654** Texture2D; route `m_RD`
trực tiếp **635** + qua atlas **1.550** = **2.185/2.185 resolve** (`unresolved` = 0). `packed` 1.550 ·
rotation `0: 2.041 · 1: 53 · 2: 54 · 3: 37` (**144** sprite cần lật/xoay) · downscale toàn bộ = 1.
**40** rect lọt ngoài texture (0,0000019–0,9963 px, đều route `m_RD`) — **chưa** kết luận nguyên nhân.

> Status trong file: `PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION` ⇒ đây là **join metadata**,
> **không** phải 2.185 ảnh crop đã kiểm. Dùng để: (a) biết **trang texture thật** của từng sprite
> (⇒ gán nhãn, `ASSET_TRIAGE.md` §9.6b: **282**/340 ca biết trang, **18** gán được); (b) biết sprite nào
> cần flip/rotation; (c) chuẩn bị cắt chính xác. **Không** dùng để nói "ảnh đã cắt đúng".

### 17.4 Chưa kéo (ghi rõ để không ai tưởng đã đồng bộ)

- 6 chunk `raw/sprite-geometry/objects-00N.jsonl.gz` (~0,9 MB) + `toolchain/` ⇒ **không** tự kiểm lại
  được `sha256_decompressed` trong `sources`.
- Report **59** (movement completion & pooling) · **60** (BB-36001 streamed animation) · **61** (BB pool
  parent/scroll/gun lifecycle) — mới kéo **62**.
- `raw/process-audit/` · `raw/balloon-animation/` · `raw/animation-audit/` · `raw/runtime-probe/` ·
  `raw/il2cpp-consts/` (273) · `raw/ui-audit/` (407) · tools/tests mới (`sprite_geometry.py`,
  `balloon_animation.py`, `enemy_move_completion.py`, 6 test).

---

## 18. Nhánh dữ liệu lên **`7c7c9f064`** — review N1–N5 và phần đã sửa

> **Tip mới:** `622b700e5 → 7c7c9f064` (3 commit). `git diff --stat 622b700e5 7c7c9f064` = **23 file,
> +976 / −6**. Không merge. Kéo về: report **52 · 53 · 57 · 63 · 64** + raw `ui-audit/scene-map-flow.json.gz`
> · `endgame-missions/shared-stage-victory.json.gz` · `balloon-animation/movement-state-writers.json.gz`
> (ghi **source SHA** = `7c7c9f064`).

### 18.1 Bên đó review snapshot `cf27b9755` của mình — 5 điểm, trạng thái sửa

| # | Review nói gì | Mình đã sửa | Bằng chứng |
|---|---|---|---|
| **N1** | Map→wave bị ghi là blocker chưa bóc, dù campaign list đã resolve | `MISSING` §2.1: **3/576 entry đã resolve** (`[25,9010]` · `[164]` · `[113,5]`), tách rõ phần chưa decode; bỏ "phải bóc lại APK" | report 52 + `scene-map-flow.json.gz`, claim **CM1** |
| **N2** | Suy "tàu không có HP/damage riêng" từ 4 field là **không hợp lệ** | `MISSING` §1 hàng 9 + §2.2: `GetMainCannonDamage(index)` đọc **mảng `0x78` theo `playerIndex`** ⇒ damage **có** phụ thuộc tàu; HP để **D** | asm `14e3a78..14e3a90`, claim **CM2** |
| **N3** | Proxy ảnh bị nâng thành định luật art + "máy chấm đẹp" | `START_HERE` §3, `VISUAL_DESIGN` §1/§3/§4/§5, `ART_STUDY` §3.2: gọi là **tham khảo trên mẫu JPEG**, nêu phản ví dụ `background 0,12` / `font 0,09`, 54.019 là **bbox dẫn xuất**, tỉ lệ screenshot **không** phải canvas | sửa câu chữ + cảnh báo trong 3 file |
| **N4** | Default/0-xref bị biến thành luật toàn game | `MISSING` §2.4 mới + `START_HERE` §2 (ghi chú 8 số) + bẫy #13/#14 + `MISSING` §3: 139 asm = **mẫu**; `rate = 0` chưa suy thứ tự | `WaitForSeconds` (report 53) |
| **N5** | Save "0 tài liệu"; thiếu contract tutorial/result | `MISSING` §2.3: key **`StarCount`** · **`StarStageMaster{stage}_{mode}`** + model `savedStars`; **§6 mới**: gate 3 stage + khuôn victory chung | report 57 · 64, claim **CM3** |

### 18.2 Cái **chưa** sửa (đừng đọc §18.1 thành "xong hết")

- ~~**573/576** blob `Map_Get_Datas` vẫn chưa dump; **6 blob** `Player_Get_Datas` vẫn chưa có~~
  **SAI — đính chính 25/10:** **576/576** mảng Map + **6/6** mảng Player **đã có** trong
  `reverse-engineering/il2cpp/ia-resolved.json` (17 method · 623 record). **L2 vẫn CHƯA**, nhưng lý do
  đúng là **thiếu bind** (`playerIndex`→ID tàu, mảng Map→(chapter, stage, mode)) — xem §23.
- **HP enemy — không thiếu:** `datas/enemy_hp_by_id.json` có **150 cặp `id → HP`** (parse trực tiếp
  `.cctor`, claim **WRH2**). `15-enemy-hp.csv` là field **serialize**: 981 dòng · 865 tên · **467** dòng
  > 0 (claim **WRH1**), `CB-*` **0/69** dòng > 0 ⇒ **không** tự nó nuôi TTK. Gộp hai nguồn **108/109**
  prefab spawn có số HP (claim **WRH5**); 3 file asm enemy đã có (claim **WRH3**) ⇒ **`.so` không cần**.
- Save: chưa có **schema đầy đủ**, chưa chứng minh **flush đĩa**.
- Report **59 · 60 · 61** + 6 chunk `sprite-geometry/objects-*.jsonl.gz` vẫn **chưa kéo** (như §17.4).
- Review của họ là **tĩnh trên snapshot đã pin**, không chạy suite của mình; mình cũng **chưa** chạy suite của họ.

### 18.3 Điều đáng giữ nhất từ review này

**"Tổng khớp ≠ không đổi"** và **"field vắng ≠ không tồn tại"** — hai câu này vừa lật một kết luận của mình
(§17.1) và một kết luận khác (§18.1 N2). Cả hai đều đã thành claim máy kiểm (`AQ7`, `CM2`).

---

## 19. `7c7c9f064 → 6ababbd31` — player loadout + save contract, và **sổ kiểm raw**

> **Tip mới:** **`6ababbd31`** (4 commit). Kéo về (nguồn **`6ababbd31`**):
> `reverse-engineering/raw/player-loadout/{index.json,array-blobs.json.gz,native/*}` ·
> `reverse-engineering/raw/persistence/opening-contracts.json.gz` · `datas/opening_persistence.json` ·
> report **65** · `tools/verify/opening_persistence.py`.

### 19.1 Đã tự kiểm **sha256** của 5/5 file (không tin lời)

`raw/player-loadout/index.json` ghi `sha256_decompressed` cho từng file. Đo lại trên máy này:

| file | sha256 (16 ký tự đầu) | khớp |
|---|---|---|
| `Player_Device_Saved_Datas.asm.txt` | `4cd845eca6efa22b` | ✅ |
| `Player_Device_Saved_Datas.json` | `a410ecc45e6956f5` | ✅ |
| `Player_Saved_Datas.asm.txt` | `bf90fe4d926e0007` | ✅ |
| `Player_Saved_Datas.json` | `e4c5e1a37f8e07682` | ✅ |
| `array-blobs.json.gz` | `2ff95f6464eeb0c5` | ✅ |

⇒ **Lần đầu** một artifact raw của nhánh dữ liệu được kiểm hash **trong repo này** (claim **CM5**).
Trước đó `sprite-geometry` không kiểm được vì thiếu chunk nguồn.

### 19.2 Cái **mở ra**, và cái **vẫn đóng**

| Việc | Trước | Sau `6ababbd31` |
|---|---|---|
| Save contract | 2 key, suy từ report 57 | **8 key family · 2 store · 7 limitation** (claim **CM4**), có asm + 41 method + 25 check |
| Getter có side effect | chưa biết | **biết**: `get_StageTarget` **tăng 1** mỗi lần đọc; `get_IndexTutorial` tự ghi `TUTORIAL=6` |
| Mảng int của `Player_Saved_Datas` | — | **5 blob · 49 int** (giá craft/unlock), **5/5 sha256** |
| ~~4 mảng **float** damage theo tàu~~ | thiếu | **vẫn thiếu tại `6ababbd31`** ⇒ B3 còn mở *lúc đó*. **Đã decode sau này** (25/10): thực tế là **6 mảng** — `PlayerCosts` int[24] · damage/rate/wing float[24] · 2× float[3] — trong `ia-resolved.json` (`BALANCE` §1.1b, `MISSING` §2.2). Cái còn thiếu là **bind** `playerIndex` → ID tàu, **không** phải giá trị |
| Field binding của blob int | — | **chưa chốt** (`PROVISIONAL_METADATA_ARRAY_BLOBS_NOT_ALL_FIELD_BINDINGS`) |

> ⚠ **Đừng gộp hai thứ:** blob int `[0,0,0,6500,8500,9500,12500]` là **giá craft** (chưa bind field),
> **không** phải damage. Nếu game mới dùng nó làm giá thì ghi **B**, không ghi **A**.

### 19.3 Sổ kiểm mới: `RAW_AUDIT.md` — trả lời "nói mồm hay dựa raw?"

`tools/raw-audit.py` phân loại **từng claim** theo source của hàm đo:

| loại | số | nghĩa |
|---|---:|---|
| **RAW** | **180** | mở file trong `datas/` · `reverse-engineering/` · `docs/assets/` ⇒ tái đo được |
| **DOC** | **3** | chỉ đọc `docs/**` ⇒ kiểm nhất quán tài liệu, không phải dữ liệu |
| **CONST** | **28** | không mở file ⇒ **đo một lần** |

Claim **RB1** khoá đúng 4 số trên; **chạy lại `python3 tools/raw-audit.py` là biết ngay** nếu ai thêm
một hằng số rồi gọi nó là bằng chứng. Danh sách 37 CONST nằm trong file — toàn bộ nhóm `A*` (phiên điện
thoại), `D*` (script bridge), `E*` (vài hằng balance), `R*` (timeline boss), `W4/W5`.

### 19.4 Đã **chạy được** verifier và unit test của nhánh dữ liệu

Đây là khác biệt so với các lượt trước: không chỉ đọc report, mà **import code của bạn vào repo này** rồi chạy.

| việc | file | kết quả (chạy tại `9a70d30c9`) |
|---|---|---|
| save contract | `tools/verify/opening_persistence.py` | **41 method · 25 check · 8 key family** — đúng bằng số trong report 65 |
| test persistence | `tests/test_opening_persistence.py` | **11 test OK** (gồm side effect `StageTarget +1`, `TUTORIAL=6`, 2 store, callback guard) |
| test loadout | `tests/test_player_loadout_recovery.py` | 3 test OK (mask giữ 3 method boundary, sha APK `f5d3c7a1…`, workflow **không** gọi `analyze-apk.yml`) |
| toàn bộ `tests/` | — | **16 test OK** |
| module phụ phải kéo theo | `tools/verify/{early_ui_native,ui_loader_analysis,ui_routing}.py` | 232 dòng, để `opening_persistence.py` import được |

Raw phải kéo thêm để chạy được (đều từ `6ababbd31`, sha256 ghi lại):

| file | sha256 (16) | vì sao cần |
|---|---|---|
| `ui-audit/extra-native/GameDatas.{asm.txt,json}` | `61a4130eff925ebb` · `cbc1dc4760eb2e80` | class `GameDatas` — 9/388 file `extra-native` còn thiếu |
| `ui-audit/endgame-rodata.json` | `d51e3459816bf782` | rodata đuôi game |
| `ui-audit/tutorial-consumer-flow.json.gz` | `6a23f9f81ed6cfdc` | consumer tutorial |
| `ui-audit/wave-spawn-flow.json.gz` | `07ec43d00d8c5848` | luồng spawn |

> **Sửa một dòng cũ:** §17.4 từng ghi `raw/ui-audit (407) · raw/il2cpp-consts (273)` là *chưa kéo*. Sai:
> `il2cpp-consts` **đã có 273 file** và `ui-audit/extra-native` **đã có 320/388**, nay thêm 5 file còn thiếu.
> Chỉ `raw/animation-audit` + `runtime-probe` là chưa cần.

**Workflow của bạn** `.github/workflows/recover-player-loadout.yml` được chép vào, **khác đúng 1 chỗ**:
`on:` chỉ còn `workflow_dispatch` (bản gốc chạy khi push vào nhánh `arena/ef6b75ef-…` và **commit thẳng**
vào đó). Giữ nguyên `on: push` thì mỗi lần mình sửa tài liệu là một job đỏ vì thiếu cache XAPK — vô nghĩa.
Test `test_scoped_workflow_not_full_analyze` vẫn pass vì nó kiểm nội dung job, không kiểm trigger.

`docs-verify` nay chạy thêm 2 bước: `tools/raw-audit.py` (tái sinh sổ kiểm) và
`tools/verify/opening_persistence.py` (41 method/25 check).

### 19.5 Chưa kéo

Report **59 · 60 · 61** chưa đọc; 6 chunk `sprite-geometry/objects-*.jsonl.gz` chưa có;
`raw/animation-audit` + `raw/runtime-probe` chưa cần cho tài liệu.

---

## 20. Nhánh dữ liệu đi tiếp: `94da165ca` (audio rules + loadout contracts)

Sau `6ababbd31`, nhánh dữ liệu có thêm 1 commit. Kéo **raw trước**, rồi mới đọc chữ:

| việc | kết quả |
|---|---|
| file lấy về | `raw/audio-rules/` (**22** file, 119 KB) · `raw/player-loadout/contracts.json.gz` (38 KB) |
| kiểm sha256 tại chỗ | **21/21** file `audio-rules` + **5/5** file loadout khớp `index.json` (**0 lệch**) |
| verify của họ chạy được | `tools/verify/player_loadout_persistence.py` → **33 method · 43 check · 15 key family** |
| verify cũ vẫn chạy | `tools/verify/opening_persistence.py` → **41 method · 25 check · 8 key family** |
| test toàn repo | **30 test OK** (thêm 14 test mới của họ) |
| `datas/` | thêm `player_loadout_persistence.json` (15 contract · 6 bảng rank · 8 limitation) + `README.md` |

**Nội dung đáng dùng cho game mới** (đã vào `MISSING_FOR_NEW_GAME.md` §2.3b): default từng key
(`PlayerUsed` slot0 **10001** / slot khác **10002**; `PLAYER_RANK` **2**; `PLAYER_DEFAULT_SKIN` **−1** là hợp lệ;
`PLAYER_DEVICE` **4 slot**), bảng rank `MaxLevelPerRanks` **[10, 20, 30, 60, 120, 250, 500]** /
`CardUpgrades` **[0, 20, 50, 80, 250, 500, 800]** / `StartRanks` **24 × 2** / `MAX_RANK_INDEX` **6**.

> **Vẫn là mô tả tĩnh:** status trong file `PROVISIONAL_PINNED_NATIVE_RECOVERY_NOT_RUNTIME` và
> `PROVISIONAL_STATIC_PARTIAL_PLAYER_LOADOUT_NOT_RUNTIME`. Chưa có runtime, chưa có atomicity/migration/cloud.

**Đã thêm vào `datas/PROVENANCE.md`:** 29 dòng cho đợt kéo này ⇒ bảng **412** dòng, **272** khớp,
**140** lệch (file kéo lại sau 23/10). `DATA_INTEGRITY.md` đã cập nhật theo (claim **AP1**).

---

## 21. Đồng bộ `a91695a0d` — report 67 (audio) và 68 (asset pack có va chạm tên)

Kéo raw trước, đọc chữ sau, như các lượt trước:

| việc | kết quả |
|---|---|
| raw mới | `raw/audio-rules/contracts.json.gz` · `raw/asset-pack/{catalog.json.gz, manifest-full.csv}` (460 KB) |
| file phải kéo thêm để chạy | `raw/ui-audit/extra-native/Machine_Gun_Attack.{asm.txt,json}` · `datas/audio_rules.json` · `datas/validate.py` |
| chạy verify của họ | `tools/verify/audio_rules.py` → **65 method · 25 checks · 15 rules** (claim **AU1**) |
| test | **40 test OK** (thêm 7 test audio + 2 test asset pack) |
| browser metadata | sinh `docs/assets/pack-browser.html` (1,4 MB) từ catalog — **không** chứa PNG/WAV gốc |

### 21.1 Audio — cái đo được

- `MUTE_AUDIO` **int default 0**, chỉ `stored == 1` là mute.
- `VolumeSound` missing-default **≈ 0,73** (pool `0x756dd4`), `VolumeMusic` **≈ 0,30** (pool `0x7570e0`) —
  dấu ≈ vì exporter lưu **decimal đã làm tròn**, không phải bit IEEE.
- `AudioManager.Pause` = wrapper `AudioListener.pause`, **không** phải `Time.timeScale`; **không** có saved key
  trong hai body đã đọc ⇒ đừng suy “pause = slow-mo”.

### 21.2 Asset pack — **zip hợp lệ KHÔNG có nghĩa là đủ asset**

| hạng mục | số |
|---|---:|
| file thật trong archive | **2.652** |
| manifest row | **2.907** |
| path bị nhiều row cùng dùng | **151** |
| row vượt quá unique path | **321** |
| row có size khác file | **320** (thuộc 150 path) |
| CRC toàn bộ entry | **PASS** |
| `manifest path→identity` injective | **FAIL** |
| `complete APK reference` | **NOT ESTABLISHED** |

Claim **AP2**: **2.652** file · **151** path va chạm · **321** row vượt unique path · **320** size mismatch.

> **Đừng nói “0 missing path ⇒ đủ asset”**: 321 row bị gộp đường dẫn, và 320 size mismatch nghĩa là **không thể
> phục hồi từng row chỉ bằng đọc file hiện tại**. Muốn biết ảnh nào thật sự khác nhau phải so **pixel**, không
> phải so tên.
>
> **Cập nhật 25/10 — pack v2 của nhánh dữ liệu (report 70, HEAD `4fe0cef8e`):** `assets-v2.zip`
> (175.684.102 B, SHA256 `4b18cc23…`) xuất **3.038/3.039** object của **6 loại** (Sprite **2185** PNG ·
> Texture2D **653/654** · AudioClip **69** WAV · TextAsset **64** · Font **1** TTF · SpriteAtlas **66**)
> với tên `<type>__<SHA256-đường-dẫn>__<pathID>` ⇒ **lỗi ghi đè 151 path của v1 đã loại** (v1 giữ nguyên
> làm bằng chứng lịch sử). Audit độc lập tải lại archive: **2.838** PNG decode đủ ảnh, **69** WAV =
> 571,465 s, TTF **258 glyph**. Vẫn chỉ **6 loại object** ⇒ `complete APK reference` **vẫn NOT
> ESTABLISHED**. Câu “phải so pixel” ở trên đã có lời đáp — xem §24.3.

---

## 22. Sửa lớn: **dữ liệu “còn thiếu” đã nằm trong repo** — `ia-resolved.json`

Lượt này có một phát hiện làm đổi cả phần “còn thiếu” của bộ spec: **hex của mọi `InitializeArray` đã có sẵn**
trong `reverse-engineering/il2cpp/ia-resolved.json` (264 KB) — **cả hai nhánh**, không phải chờ dump lại APK.
Trước đó `MISSING_FOR_NEW_GAME.md` viết *“573 blob còn lại chưa dump”* và **xin nhánh dữ liệu dump thêm**.
Đó là **kết luận sai**, và sai vì **không grep repo trước khi xin**.

### 22.1 Số thật

| thứ | số | ở đâu |
|---|---:|---|
| `Map_Get_Datas.cctor` record | **576** | `ia-resolved.json` |
| `Player_Get_Datas.cctor` record | **6** | cùng file |
| record `length_valid` sai | **0** | cùng file |
| tổng giá trị int trong 576 mảng map | **5.154** | cùng file |
| wave id khác nhau · id không có trong `waves.json` | **253** · **0** | đối chiếu `datas/waves.json` |
| offset field có store ngay sau `InitializeArray` | **6/6** | asm `Player_Get_Datas.asm.txt` |

### 22.2 Hai lỗi của mình, ghi để không lặp

| lỗi | đúng | vì sao |
|---|---|---|
| **“573 = 576 − 3 blob còn lại”** | **576 mảng**, **không** trừ 3 | 3 entry mở đầu dựng bằng **literal store**, không nằm trong 576 `InitializeArray`; và 576 mảng **không** phải 576 stage |
| **“4 mảng × 24 float damage”** | **1 int[24]** (`PlayerCosts`) + **3 float[24]** (damage/rate/wing) + **2 float[3]** (clone, mission %) | cột `ints` của file là **bit pattern**; float phải unpack `<f` theo kiểu field |

### 22.3 Giá trị đã dùng được (chi tiết ở `BALANCE.md` §1.1b)

`PlayerCosts` = `0, 0, 1050, 3150, −1, 3850, …` (**16/24** bán được, **8** giá `−1`) ·
`StartMainCannonDamages[0]` = **4500**, `StartMainCannonRate[0]` = **4,8** ·
`StartWingCannonDamages[0]` = **218** · `shipCloneDamage` = **1,35/1,6/1,86** ·
`PercentToCompleteMissions222` = **0,2/0,6/0,98**. Dẫn xuất: `datas/player_start_stats.json`.

> **Cập nhật 25/10 (lần 13; sửa lần 18)** — 3/4 mục "vẫn chưa" ở đây **đã xong**: ~~`playerIndex` →
> ID tàu~~ ✅ (id − 10001 — **hẹp scope: chỉ save/load; combat = impl N → index N−1, tàu 10001→2 ·
> 10003→0, report 81/82 peer**) · ~~576 mảng map → (chapter, stage, mode)~~ ✅ bind cấu trúc
> (**11 bảng / 614 mảng**, `DIFFICULTY_MODES` §7) · ~~`rate` có phải *shot/giây*~~ ✅ **interval đặt hạn
> bắn** tàu 1 (report 79 peer; **tích damage×rate không dùng** — đơn vị damage·s, review peer).
> Còn: **HP riêng của tàu** (D) + parity phát phụ/nòng.
> Đó là việc **bind + kiểm runtime**, không phải việc **dump**.

---

## 23. Đồng bộ `3ac2faa45` — report 69: **blob đã có**, và so khớp hai nhánh

Nhánh dữ liệu tự kiểm chính điều mình vừa phát hiện và **pin phép so sánh**:

| việc | kết quả |
|---|---|
| `raw/initialize-arrays/peer-comparison.json` | so **từng record** hai nhánh cho 2 nhóm: **576** và **6**, `exact_record_equality=true`, `all_length_valid=true`, kèm `canonical_records_sha256` (**IA6**) |
| `raw/initialize-arrays/typed-inventory.json.gz` | bản **typed** (thêm `values`, `payload length`, `trailing bytes`), chạy `tools/verify/initialize_array_inventory.py` tái tạo **giống hệt** (decompressed) |
| `il2cpp/ia-resolved.json` của họ | **superset**: **17 nhóm · 623 record** (thêm `Board_Drones`, `Board_Players`, `Board_Endgame`) — claim **IA7** |
| phạm vi so khớp | **chỉ 2 nhóm**, không phải toàn file — đúng như report 69 ghi |

**Đã đổi trong repo này:** lấy `ia-resolved.json` **17 nhóm** (thay bản 12 nhóm), thêm 2 file raw trên,
thêm `tools/verify/initialize_array_inventory.py` + test của họ (**5 test**, tổng **45**).

### 23.1 Vì sao chuyện này quan trọng

`ia-resolved.json` **đã nằm trong repo từ trước**, nhưng bộ spec lại đi **xin dump** — tức là sai ở khâu
**kiểm tra cái mình đang có**. Từ nay luật số **4** của `RAW_AUDIT.md` bắt buộc: *grep `reverse-engineering/`
trước khi xin dữ liệu*.

### 23.2 Cái mới thực sự dùng được

`Board_Players.allBasicAtk` (float[24]) và `allDeltaAtk` (float[24] = **0,168** × 24) — **tên field đã bind
theo asm**, nhưng **consumer chưa đọc** ⇒ ghi **B**, chưa gọi là “damage theo rank”. Chi tiết: `MISSING` §2.2c.

---

## 24. Đọc **chọn lọc** nhánh dữ liệu `4fe0cef8e` — report 70–74 (không kéo file)

> 25/10: đọc 5 report mới **bằng `git show` từ FETCH_HEAD**, không bê cây dữ liệu về repo này.
> Số dưới đây là báo cáo của nhánh kia (static APK evidence, **chưa** nghiệm thu runtime/render);
> nhánh kia cũng đã thấy nhánh mình ở `2d0a0e139` — *“không lấy ‘chưa có Map/Player blob’ làm blocker nữa”*.

### 24.1 Report 70 — pack v2 identity-safe, “zero font texture” có chủ đích

- 3.038/3.039 object của 6 loại; exception duy nhất: Texture2D `pathID 535` **“Font Texture” 0×0,
  `image data=[]`** — nguồn serialize **không chứa pixel**, không tự vẽ thay thế; cơ chế runtime font
  atlas **chưa chứng minh** (đáp án ở report 73: TMP SDF atlas).
- 27 atlas text: **0 trang** giải được identity chỉ bằng tên page (26 trang × 26 candidate + 1 trang × 2).

### 24.2 Report 71 — Spine: 27 rig bound **file-scoped** (hết bài toán basename)

- **27 SkeletonDataAsset → 27 SpineAtlasAsset → 27 atlas TextAsset → 27 page Texture2D**; graph
  **167 objects / 168 links** (54 MB + 54 TextAsset + 29 Material + 27 Texture2D + 3 shader projections);
  **185 animation names**; format **26×3.8.99 + 1×3.8.84** (khớp `ANIMATION.md` §1).
- Loader native `MaterialsTextureLoader.Load` **0x222f580**: page→material qua **mảng `materials` của
  owning atlas** + `get_mainTexture` + so tên, first match, duplicate reject — **không tìm toàn cục**.
- **7 atlas header 1024×1024 nhưng texture 512×512** (pathID 540·565·259·646·601·273·666):
  `dimension_match=false`, **không resize, không sửa toạ độ** — loader giữ parsed dimensions.
- Settings: scale ≈0,01 · defaultMix 0,2 (Saw = **0,5**) · 1 rig có additive/blend replacement
  (material 38/39 → texture 413). Reference folder mỗi rig 1 ZIP (`spine-reference-v1.zip`,
  110 members) — **source-associated**, chưa import/render.

### 24.3 Report 72 — sprite: tái tạo pixel 2185/2185, và **KHÔNG clamp**

- Auditor riêng (không dùng UnityPy helper) tái tạo từ raw geometry: **2185/2185 sprite khớp size +
  toàn bộ RGBA bytes** với PNG v2. Đóng câu “so pixel” của §21.2 **ở mức export pipeline** — chưa
  nghiệm thu Unity renderer.
- **40 rect vượt page ≠ 40 PNG hỏng**: 9 case round xong cần **pad 1 px** (8 top: pathID
  2072·2099·2114·2134·2169·4006·4050·4085; 1 right: 4092), 31 case round xong vẫn trong page.
  Clamp thay vì pad ⇒ **sai size** (counterfactual kiểm từng case).
- **517 PNG bị trim** (output ≠ full canvas) ⇒ **đừng gắn pivot chuẩn hoá của source rect vào PNG đã
  trim**; muốn đặt đúng chỗ phải đọc consumer (`datas/sprite_export_contract.json.gz` giữ
  source_rect/pivot/offset riêng).
- Flip: 2041/53/54/37 (khớp GE2). Separate alpha 0, mesh UV0 0 (đi polygon mask).

### 24.4 Report 73 — font TMP + localization **first-index**

- **7 TMP font assets**, đều **Static + SDFAA**, `sourceFontFile=null`: main **105 AGENCYB SDF**
  (512×256, 234 glyph) + fallback **105→110→106→108→109→111→107** (Roboto-Currency · Agency-Cyrillic ·
  Amiri-Bold · NotoSansKR · NotoSansSC · SDF-Thai; tổng 2352 glyph row / **2285** codepoint union).
  Global `m_fallbackFontAssets=[null]` **không** có nghĩa là không fallback — fallback nằm **trên từng
  asset**. **7 SDF ≠ 1 TTF** exported — đừng suy “1 font toàn game”.
- Census: **9797** TMP component (9796 → font 105, 1 null `resources.assets:699094`), RTL false toàn bộ;
  2442 `Language*` wrapper gọi `LanguageManager.GetText`.
- Localization: **19 LanguageAssets × 1426 row; 1415 key nonempty**; `GetText` dùng
  `IndexOf` ⇒ **duplicate dùng occurrence ĐẦU** (không last-wins). CSV cũ của chính mình đã collapse
  last-wins ⇒ **sai 1 giá trị English**: `txt_free_after` = “**Free after**” (index 690), không phải
  “Free After” (1243). Vietnamese không lệch key nào. Đã sửa 2 CSV ở repo này.
- Chọn ngôn ngữ: preference `Language`; mặc định theo **systemLanguage → bảng 32 int native**
  (`0x779fb8`, ví dụ **Vietnamese 39→1**, Arabic 1→6, zh-CN 40→18); fallback value rỗng → English(0) → trả key.
- Coverage delta (chuỗi tĩnh vs 2285 codepoint): vi thiếu **1** (U+0340) — **chưa phải** kết luận
  glyph thiếu lúc render.

### 24.5 Report 74 — gói font tham khảo tự chứa

`font-reference-v1.zip` (1.627.375 B · 19 members · SHA256 `1c20bda1…`): 7 folder
(atlas.png exact-byte + JSON glyph/character/fallback/kerning) + **1 TTF** (56.312 B, Font object 2044,
`globalgamemanagers.assets`) + `index.html`. Kerning serialized **0 entries** ở cả 7. JSON là **reference
projection, không import thẳng**; TTF giữ inventory riêng, **không** gán thành sourceFontFile.

### 24.6 Việc peer giao nhánh này (report 73) — đã xử lý trong commit này

| Task peer | Trạng thái |
|---|---|
| 1. Spec nguồn font: main 105 + 6 fallback, cấm “global null → no fallback” / “1 font toàn game” | ✅ `ASSETS.md` mục checklist font + §24.4 |
| 2. Lookup first-index; sửa `txt_free_after` nếu đã copy CSV last-wins | ✅ sửa 2 CSV `12-localization*.csv` + §24.4 |
| 3. Không nhét SDF PNG vào CSS @font-face như TTF | ✅ ghi ở `ASSETS.md` (không có chỗ nào làm vậy) |
| 4. Refresh summary gap/asset counts theo 67–73 | ✅ đối chiếu: 2185/654/69/64/1/66 đã khớp từ trước; thêm pixel/spine/font ở §24 + `ASSET_TRIAGE` §9.9 |

### 24.7 Report 75 — mesh gốc + origin (HEAD mới của peer: `be112f36c`)

- `datas/sprite_mesh_contract.json.gz` (peer): **2185** Sprite · **27.072** vertex · **24.375** triangle,
  float32 position / uint16 index giữ nguyên — **không đoán pivot từ PNG đã trim**.
- **1652 mesh ≠ quad** · **497 giá trị PPU** (980 Sprite = 100) ⇒ **đừng mặc định quad/PPU100**.
- Mesh-AABB origin ≠ source pivot (>1e-5): **467**; **7** ngoài AABB (2146·2316·2692·2836·3050·3304·3687)
  — **không clamp, không recenter**. Submesh localAABB serialized **0 ở cả 2185** ≠ measured bounds.
- Winding: negative **24.013** / positive **17** / zero **345** — chưa phải GPU culling verdict,
  không repair.
- **Task peer mới (4 ý):** dùng typed mesh + PPU thật khi cần geometry; phân biệt source pivot /
  mesh origin / serialized AABB / registration PNG trim; quad-recenter = **new design**; UV/renderer/
  placement còn mở.

### 24.8 Chốt “bind” — đã xong, đừng lặp TODO cũ

| Bind | Trạng thái |
|---|---|
| `playerIndex` ↔ ID tàu | ✅ **save/load: index = id − 10001** (asm `0x14e2ce4`, T4) — **combat: impl N → index N−1** (report 81/82, xem §24.14) |
| Cấu trúc bảng Map (614 mảng → 11 cấu trúc) | ✅ `DIFFICULTY_MODES` §7: 320×len3 ↔ 3 mode · 118×len2 = stage→boss · 104×len7 ↔ 7 PlayMode |
| Chi tiết entry từng mảng campaign | ✅ nhánh dữ liệu ghép xong (`datas/map_table_segments.json` + `maps.json`) |
| `kHp[mode]` | ✅ **KHÔNG TỒN TẠI** — chế độ không nhân HP (chỉ `levelDelta` thưởng; 0/5 hàm `stageLevel` liên quan HP); khác biệt = composition bảng len-3 |
| `missionKillPercent` | ✅ **đủ 3/3** — MỘT `float[3]` [0.2/0.6/0.98] theo **mission index**; "3×3" là ảo đơn vị (sửa 25/10) |
| `StartHpPoint` ← dict 150 cặp | ✅ **đã bind theo id** — dict là nguồn (`GetStartHealthPoint(id)`); `Init` `0x1582f5c` chỉ là plumbing, không chặn số nào |
| Playback thật | ✅ **phiên phone 23/10** (`ramus/2026-10-23-phone/`): statics khi chơi · freeze/slow-mo · 7 live chụp instance (kill 276 / coin 540) · HP khớp 2500 — *(dòng này sót từ lần 9 do script abort, bổ sung lần 10)*. Sót: 2 phép tái đối chiếu `CROSSCHECK` |

### 24.9 Report 76 — SpriteRenderer của scene mở đầu + chuỗi ancestor (peer → `e5ed7d070`, **232 tests**)

- Raw `scene-sprites/` (5698 object, **0 read error / 0 unresolved link**); **1377** renderer-root
  chỉ ở level 0–3; 61.438 renderer trong `resources/sharedassets` **chỉ đếm, không mở rộng** ⇒
  không gọi là "population runtime".
- `datas/scene_sprite_contract.json.gz` (peer): Renderer→GO→Transform→ancestor; **218** typed Sprite
  khớp mesh-source hash + PNG ref; 7 material projection đầy đủ / 6 shader identity.
- Thứ tự scene `Menu/Home/Game/EndGame` (BuildSettings) ⇒ root **8 / 4 / 1036 / 329**; gate
  `activity AND` cho **8 / 4 / 1036 / 3** — **đếm ≠ visible**.
- Trạng thái numeric: `NullSprite` **56** · disabled **26** · alpha-zero **43**; **78** instance đếm
  bằng activity+AND có đúng 1 null-Sprite ⇒ **đừng coi 78 là "sprite visible"**.
- FlipX **68** / FlipY **10**; ancestor negative-scale **14** / zero-scale **4**; RectTransform chain
  43 (depth max 10); DrawMode numeric 0:922 · 1:441 · 2:14 — **giữ nguyên size/flags, không suy
  geometry cuối**; SortingLayerID = 0 cả 1377 ⇒ **không** là draw order cuối. Mask interaction
  None **1074** / Inside **302** / Outside **1**; **303** instance phụ thuộc mask cần ngữ cảnh
  SpriteMask/camera (report 77).

### 24.10 Report 77 — camera scene + SpriteMask + layer predicate (peer `0f7ae8853`→`d66037d10`, **239 tests**)

- **5 Camera + 12 SpriteMask** là scene-root; **0 read error**; 191 mask trong `resources` + 1 camera
  shared **ngoài scope root**; catalog 0 serialized `SortingGroup` **không** chứng minh runtime vắng.
- `datas/scene_render_context_contract.json.gz` (peer): camera source **ortho 9,600000381469727**,
  full viewport, targetTexture null — **khớp chéo với spec mình**: vùng thấy cao **19,2** unit,
  mép trên đúng mốc spawn **y = 9,6** (`SCRIPTS` §3 · `START_HERE` số 5).
- Culling mask **disjoint**: camera Game (`3975`) loại UI, giữ Map; camera UI (`3976`) chỉ UI
  — hai namespace **layer name** và **camera mask** phải giữ riêng, đừng gộp.
- 12 mask dùng cùng typed Sprite `sharedassets0:37` (source hash → mesh 75); **3** mask serialized
  active (6373/6375/6377), **9** custom-range active, cutoff ≈ **0,2** (giữ raw float, không làm tròn).
- **Task peer (report 76+77):** (1) import typed scene-chain, đọc numeric state đúng scope —
  source mesh/pivot/PPU ≠ draw-mode/UV/transform hiệu lực, **không double-flip**, không coi 78 là
  visible hay 61.438 là asset thiếu; (2) import typed render-context — không gộp namespace,
  giữ mask range; depth/clear/native writer **chưa biết**; (3) không nâng bool predicate thành
  "visible list", không coi 191 mask bị loại là "asset missing".
- Đang làm tiếp bên peer (chưa có report): **CameraScaler** — camera binding + native resize writer,
  raw giữ float-pool byte gốc thay vì hằng số làm tròn.

### 24.11 Report 78 — `CameraScaler.Awake` ghi orthoSize theo tỉ lệ màn hình (peer `f844627702`→`c34d19034f`)

- **ortho 9,6 của report 77 KHÔNG cố định mọi màn hình**: `CameraScaler.Awake → ResizeCameras` tính
  `ortho = max((float)Screen.height / (float)Screen.width × 5.4f, 9.6f)` — **9,6 chỉ là sàn**.
  Cả hai chiều chuyển **float trước khi chia** (SCVTF/FDIV) — không mô phỏng bằng integer division C#.
- **5 scaler / 6 camera ref**, cả **5 scene camera** của report 77 đều bind (level0:89→58 · level1:52→39 ·
  level2:6678→{3976 UI, 3975 Game} · level3:2391→1308 · sharedassets0:121→79 — 79 là serialized ref,
  chưa chứng minh spawn). Camera array field `0x20`, duyệt length−1 → 0.
- Native: Awake `0x141d70c` → ResizeCameras `0x141d710`; `Screen.get_height 0x27665e4` · `get_width
  0x27665bc`; `set_orthographicSize 0x275e1b0`; float-pool bytes gốc giữ trong raw (`camera-scaler/`).
- ⇒ **khớp chéo y = 9,6** ở số 5 (`START_HERE`) đúng cho màn ≤ 16:9; màn dài hơn (điện thoại 20:9)
  ortho = h/w × 5,4 > 9,6. Đã ghi bổ sung ở `START_HERE` số 5.

### 24.12 Report 79 — review nhánh spec + nhịp bắn tàu 1 (peer `2842bf5f0b`→`9aa2d7e6fc`, **250 tests**)

- Peer fetch nhánh mình tại **`029559d47`** (trước commit audit `343c74a2`); snapshot 4 tài liệu để ở
  `raw/peer-review/update-029559d47.json.gz` (peer docs, không phải APK evidence). Task P0 gửi PR12
  comment `6399017163`: ① đồng bộ bảng tổng audio/assets; ② sửa claim DPS/TTK; ③ player-ID binding;
  ④ CameraScaler 78; ⑤ tách lựa chọn thiết kế khỏi thông số APK.
- **Lỗ hổng peer bắt đúng:** `MISSING` §2.2 từng dùng report **53** (delay spawn Path/Waypoints) để đóng
  `StartMainCannonRate` — **hai consumer/field khác nhau**; `COMBAT` ghi `damage × rate` là DPS.
- **Chuỗi tàu 1 (Player_Attack_1, native, static):** `SetupDatas 0x147a364` gọi `GetMainCannonRate(0)`
  (getter `0x14e3cd8` đọc `@0x80`, nhân `(1 − GetMainCannonRatePercent())`), store `@0xa8`
  (`timeRateMainCannon`; nhánh demo literal 3); `MainCannonShoot 0x147a920` đọc `Time.get_time 0x2786dc0`,
  gate `@0x10c`, **deadline `@0x10c = now + @0xa8`** (`0x147a988..990`) ⇒ rate là **interval**;
  phát phụ `@0x118/@0x124` + counters `@0x11c/@0x120`; nòng duyệt array `@0x88`.
- **Đã sửa bên mình (commit này):** `MISSING` §2.2 (đính chính report 53 + proxy) · `COMBAT` §0/§6.1/§6.2 ·
  `BALANCE` §1.1b (bảng đổi nhãn proxy + bind xong) · `START_HERE` số 5/`datas` · `DESIGN_QUESTIONS` B4 ·
  `OPEN_ISSUES` D5 (mới) · `BOSSES` · `ENEMY_HP_RUNTIME` · `COVERAGE_AUDIT` §1 row 3 · README.
- **Bàn giao mới:** `SYSTEM_MANIFEST.md` — bảng tối giản `hệ thống → raw/hợp đồng → luật → tự chọn →
  test` (đúng task ⑤ của peer). Reply trên PR12 sau khi push + CI.

### 24.13 Report 80 — phát phụ, emitter, damage callback (peer, scope `Player_Attack_1`)

- **Không phải mỗi lần gọi đều phát**: dual gate — main deadline `@0x10c` + extra deadline
  `@0x118` (`rateAddMainCannon @0x124`); extra count từ `GetNumberAbility(4)` (OnEnable; ctor
  default 1 · 0,2 s không chứng minh runtime); **N extra ⇒ N+1 entry emitter**; **không có
  catch-up timer** (gọi muộn chỉ đặt deadline tương lai). `N / interval` **không** phải rate.
- Emitter phụ `MainCannonAttack` theo **rank `@0x44`**: rank 3 → 2 vòng · ≥4 → 4 vòng · <3 → return.
- Damage tính **trong callback** `OnBulletMainCannonCollided`: `Random.Range(0,1) ≤
  GetMainCannonCritPercent` ⇒ multiplier **2**, ngược lại **1**; nhân vào `GetMainCannonDamage`
  rồi `Damager(float, Action)` → `IDamageable.TakeDamage(ignoreInvincible=false)`.
- Model `player_main_cannon_timer.py` chỉ trả `entered_emitter` — không phải bullet/hit/DPS.

### 24.14 Report 81 — combat-chain family 24 implementation → bullet → receiver ⚠ **sửa bind bên mình**

- Raw `raw/combat-chain/`: **123 class · 1563 method · 24 ships · 4133 component**, capped 0;
  498 GOT cells nối qua **ELF RELA**; `datas/combat_chain_contract.json.gz` = hợp đồng
  (⚠ cùng `combat_argument_audit.json` · `combat_rate_consumers.json`: **file nằm ở nhánh dữ
  liệu `arena/ef6b75ef…` — repo này không có**; xin qua PR12 khi cần đối chiếu địa chỉ).
- **Hậu tố class ≠ ID tàu**: impl1 (`Player_Attack_1`) source **10003** · impl2→10002 ·
  **impl3 → 10001** · impl4–24 → 10004–10024. Report 82 CFG-proof **72/72** getter call truyền
  **N−1** ⇒ **bên spec đã sửa mọi claim "id − 10001" sang scope save/load** (`MISSING` §2.2 ·
  `COMBAT` §0/§6.1 · `BALANCE` §1.1b/§5.2 · `DESIGN_READINESS` ①/B3 · `README` · `SYSTEM_MANIFEST` ·
  `DATA_SYNC` §22.3/§24.8). Lưu ý report 82: source impl2 còn chỉ đọc prefix (4 EOF typetree).
- **Luật mất máu enemy (§E)**: `factor = 100/(100+armor)` nếu `armor ≥ 0`, else `2 − 100/(100−armor)`
  (armor −100 ⇒ ×1,5); overkill clamp 0; `loss` = HP re-read **sau** `hitCallback`; gate
  `currentHP@0x28` + flag (report 82 đặt tên **`IsCaAttack@0x2F`**); **1.623 collider** → 1.472
  `Enemy_Sub` + 76 `Shield_Sub` (không dùng công thức enemy) + 6 `Sub_Player` + 1 `Sub_ShipProtect`;
  68 root không receiver = 64 null + 4 root không Mono. `armor` **private runtime, không serialize**
  — không bịa default 0. `noDamage`: 740 false / **241 true** (981).
- Typed bullet: main `80003` → **Bullet_Plasma**, pool `88004` → **Homing_Missile** — không áp
  hành vi `Bullet_Linearly` base cho override.

### 24.15 Report 82 — audit chứng cứ: đóng caveat, không để "chưa runtime" thay việc đọc native

- **72/72** đối số getter CFG-proved (must-value, cả hai nhánh, back edge): `w0 = N−1` — đóng
  candidate-index của 81; **cấm áp mù `id−10001` thay chuỗi source→implementation→argument**.
- **Modifier rate ĐÓNG**: `rate = base × (1 − percent)`; percent = `GetTechStatLevel(1)` tier:
  ≤0 → 0 · 1 → 0,03 · 2–3 → 0,05 · 4–6 → 0,08 · 7–8 → 0,10 · ≥9 → 0,12 (binary32 literals giữ raw).
- 38 `ends_clean=false` audit xong: **36 coroutine Reset throw NotSupportedException + 2
  OnDrawGizmos** — **không phải body bị cắt, không xin dump lại**; 132 overlap clip bằng next-RVA.

### 24.16 Report 83 + tip `23b1ceec31` — main-rate → deadline → dispatch đủ 24

- Cả **24 SetupDatas** gọi getter, đọc `demo bool@0x30` (`fcsel`), ghi `timeRateMainCannon`;
  demo=true → **3,0** (impl 1–23) / **4,0** (impl 24). **4 access/impl** (ctor ghi · SetupDatas ghi ·
  MainCannonShoot đọc · StartAttack đọc) — **48 read site** vào đúng 2 consumer; giá trị getter là
  **interval** cho main deadline, không phải số đạn/s.
- 25 `MoveNext` + 14 `WaitForSeconds` inventoried; tip: **coroutine byte jump-tables pinned**
  (`raw/combat-chain/coroutine-jump-tables.json`) — scheduler từng family đọc/implement được.
- Bên spec đã cập nhật theo 80–83: `COMBAT` §0/§6.1–6.2 (TTK + luật mất máu) · `BALANCE` §1.1b/§5.2 ·
  `MISSING` §2.2/row 9/§2-đầu/§6 · `OPEN_ISSUES` D5 · `SYSTEM_MANIFEST` 3 dòng · `DESIGN_READINESS` ①/B3 ·
  `README` 2 dòng · mục này.

### 24.17 Report 84 — dịch control-flow đủ 25 combat coroutine (peer `58ef9809ac`→`c7f72fe22e`, 327 tests)

- `datas/combat_coroutine_flow.json`: **25 MoveNext** dịch đủ (không còn inventory-only) — branch
  edges, **3 computed BR từ 9 byte jump-table** (`coroutine-jump-tables.json`, pin lib SHA), **14 wait
  sites** nối nguồn + resume, 7 factory parameter-copy; raw `combat-delegates/` thêm clone/pumpkin
  (+2 iterator, 30 method). Models **chạy được**: `tools/verify/combat_coroutine_models.py`
  (10/11/12/13/14/17/18/23/24 + 7/9) — phân biệt helper dispatch / wait / frame / callback / particle.
- **Ba đính chính cho spec:** ① `_delay` impl **7/9** = chờ **sau attack hold** (byte-table chứng minh
  state0 ≠ state2 — không đọc state theo vị trí code); ② impl **17** chờ **sau cặp** vị trí
  (`i % 2 == 1` ⇒ wait 0,2 ⇒ floor(N/2) wait, không phải N); ③ impl **18** `IESpawnHeart` = **toggle
  particle** `rateOverDistance` 2→0 (0,5 s/1,0 s) — **không** spawn projectile (câu hỏi "heart spawn
  loop" của §24.16 hết). Số wait = **không** tự thành cadence/hit/DPS.
- Chi tiết dùng để implement: 10 = round theo rank (1/2/3), wait 0,25 kể cả round cuối · **13**
  (ShotAllBarrels) = `shotRate/number` clamp 0,05 (FMINNM) — **11 thì KHÔNG**: descriptor rate =
  f32(0,04), duration theo rank/deadline (sửa theo review peer 25/10) · 23/24 = `shotRate/childCount`
  đọc lại sau helper ·
  6 = điều khiển đạn có sẵn (radius 10/20, speed 15/12) · **đừng gộp hai chuỗi của impl 9** (review
  peer): **Player9_Clone** StopAttack → cleanup wait **0,34** → pool; **projectile** 7/9 outbound
  ≤0,1 → hold **0,35** → optional delay → return ≤0,5 → pool+ended · pumpkin: deadline active **2**/
  charge **1**/duration **4** + callback→Hide.
- **Việc kế tiếp của peer:** callback→damage request→HP re-read (không suy helper event = hit).
  Bên spec đã cập nhật: `SYSTEM_MANIFEST` (nhịp bắn) · `OPEN_ISSUES` D5 · mục này; ack qua PR12.

### 24.18 Report 85 — dịch enemy + player receivers qua mutable-HP callbacks + death dispatch (peer `035a64f440`→`e84272e3a9`)

- **44 receiver/helper walks · 3485 instructions**, raw `220fa2d53`, recovery SUCCESS; 48 checks mới,
  full **375 PASS**. Đóng luôn việc "callback→damage→HP" còn treo ở D5.
- **Enemy**: `CalculateDamage` chạy **cả hai callbacks** (`hitCallback` + `hitDamageCallback`) và
  capture HP qua **ref**; controller **HP re-read** sau callback (loss ≠ raw damage — như §24.14).
- **Player**: **2 truncations** (damage bị cắt về int?) rồi synchronous events **21/39** → HP re-read
  qua extra-life/death.
- **Death overrides đã phục hồi (đính chính các phỏng đoán cũ):** `Delayed` = **`WaitUntil(condition)`**,
  **KHÔNG** phải delayTime 2; `MB` = **3× Wait(1)**, không có base Pool tail; **ability 32 `Destroyed`
** issue **recursive damage requests**, **không dedup** receiver.
- Bên spec cập nhật: `SYSTEM_MANIFEST` (Enemy row + row "Chết — hồi sinh") · `OPEN_ISSUES` D5 ·
  COMBAT §6.4 (noDamage native rule) · mục này.

### 24.19 Report 86 — extra-life/heal lifecycle + review 6 finding trên nhánh spec (peer `25734422b2`→`82f14784e5`)

- **Peer review trực tiếp tip `b8f72a4127` của spec — 6 finding, đã sửa hết (commit này):**
  ① DATA_SYNC §24.17 impl **11** không phải `shotRate/number` (chỉ 13) — descriptor 0,04 + duration
  theo rank; ② tách **Player9_Clone** (0,34) khỏi **projectile 7/9** (0,35) — trước đây gộp nhầm;
  ③ **bỏ TTK theo tích damage×rate** (đơn vị damage·s) — COMBAT §0/§6.1/§6.2, BALANCE §1.1b, MISSING,
  ENEMY_HP_RUNTIME, BOSSES, COVERAGE_AUDIT, README; ④ COMBAT §6.4 **189/800 → 241/981** + native rule
  `noDamage && !ignoreInvincible` skip / ignore bypass — bỏ kết luận "chỉ trang trí"; ⑤ đánh dấu
  **superseded ngay tại đoạn**: COMBAT §10, BALANCE §0.6.2/§0.6.x, UNITY_RULES §12; ⑥ START_HERE
  "tra là có hết/không test" → đúng mức **tra trước + scoped unknown không bịa + automated checks
  bắt buộc** (metrics = gate, không phải approval) — đồng bộ DONE/MISSING/SYSTEM_MANIFEST/VISUAL_DESIGN.
- **Report 86 (nội dung):** GOT `2ae8480` → RELA `2bc83d0` → **`OnExtralife`** chốt; `destroyShieldOneHit`
  + noTouch wrapper chốt. **Heal lifecycle:** hồi **1 s** sau hết mạng, KHÔNG full ngay — normal:
  resume timeScale **0,05** + `HealHp` **0,5**; PVP: `HealHp` **1** không WaitUntil; zone heal =
  **1,235 % maxHP** sau wait 0,2. Raw `2738ad848`, recovery SUCCESS, 19 checks mới.
- Peer đã tự cập nhật 3 cửa vào nhánh dữ liệu với định hướng (bản của họ), không chép "coverage đủ/
  không test" thành APK fact — đúng hướng; khối "mục đích" (v2 anchors) **vẫn chờ commit** bên đó.

### 24.20 Report 87 — Invoke→RebornDone, khiên, invisible-zone (peer `691f225b8`→`0561a2185b`, **412 tests**)

- **Invoke không đoán theo tên**: GOT `2ae8560` → RELA → metadata literal → **`RebornDone`**
  (root `Player_Controller.RebornDone 0x14c4d5c`). Normal `0x14c6130` + PVP `0x14c44e0` đều
  `IsInvoking → CancelInvoke → Invoke(name, TimeResetInvincible)`.
- **Initializer**: `TimeResetInvincible = 3,0` · `TimeCanActiveInvincible = 10,0` (2 field 32-bit
  static+8, store64 tại `0x14e5b0c`) — giá trị khởi tạo, Invoke đọc live field.
- **Đính chính 85/86**: `Player_Physics.activeHitEnemey@0x90` (giữ typo gốc) = cờ **enemy-contact
  hit** — write false khi chết/extra-life là tắt va-chạm-damage, **không phải** khóa di chuyển
  (model `Lifecycle.move_enabled` → `hit_enemy_enabled`); `Controller+48` = `playerTalentScript`,
  write false trỏ `Player_Talent.reborning@0x20`.
- **RebornDone**: clear `inReborning@a8`, particle, bone TimeScale → 1; flag block — cả 4 flag false
  mới ghi `invincible=false` + contact-hit=true; skill/droid101 giữ giá trị trước; one-hit contact
  = `!droid103`. Một-hit-only với invincible đã false → **giữ false**, không bật lại.
- **Shield callbacks không refcount** (`OnShieldActive`/`Droid101`/`Droid103`/`OneHit`): ghi flag
  rồi tính aggregate skill OR 101 OR 103; onehit không cộng vào aggregate và không gate
  `inReborning` ⇒ callback(false) có thể tắt invincible của extra-life — static store/order.
- **SetInvisible**: list add/remove; heal 1,235 % maxHP (86) qua `IEHealInZoneInvisible`; **đọc lại
  `inReborning` sau helper** — đang reborn thì return trước khi ghi invisible.
- Models `player_shield_models.py`; raw `raw/player-invincibility/invoke.json`. Bên spec đã cập
  nhật: `SYSTEM_MANIFEST` (row hồi sinh) · mục này; peer pin ACK85/86 của mình
  (`raw/peer-review/ack-85-86-6400213174.json`).

### 24.21 Report 88 — producer hit-callback thật → FX và gold burst (peer `0981352791`→`eaa5c74342`, **450 tests**)

- **Producer thật, không đoán theo tên component** (census 6.765.005 ARM64 words, đọc
  constructor/store từng producer — không dùng candidate làm proof): **Skeleton.Start gán đè**
  `Enemy_Health.hitCallback@20` (`Enemy_HitSkeletonRenderer.OnHit 1321a1c`) · **DropGold.Start
  Combine** `hitDamageCallback@28` (`Enemy_DropGold.DropGold 1581828`) · `Test_Enemy` chỉ là
  component test (không phải producer gameplay) · listener event6 = `Items_Manager.OnBurstGolds`
  (AddListener từ Start).
- **19 serialized co-attachments** trong `data.unity3d/resources.assets`: 17
  `Enemy_HitSkeletonRenderer` (trên Gun/Boss parts) + 2 `Enemy_DropGold`, enabled 1, health snapshot
  `noDamage=false` — join bằng GO-pointer + component membership, **không** join pathID đơn lẻ.
  Không suy 19 root là cả game hay prefab đã spawn ở stage nào.
- **Skeleton OnHit**: property **`_Black`** (không phải `_Color`), SetColor `hitColor` serialized
  từng instance → Invoke **`CancelEffect`** delay f32(.01) — CancelEffect ghi **RGBA(0,0,0,1)**,
  không restore `hitColor`.
- **DropGold**: ctor load64 `1c0000000a000000` = 2 int32 **burstCoins=28 · totalP=10** (`iPlus=1`,
  không thuộc serialized record); đọc **tỉ lệ HP hiện tại** (`GetCurrentHealth`/`GetStartHealth`),
  **không dùng `_damage`**; ngưỡng strict `lost > iPlus × 10` (lost=11 mới phát đầu); **1
  event/lần gọi** — không while-catch-up các mốc bị vượt; heal về `lost < 10` reset `iPlus=1`.
- **Event6 → budget spawn — KHÔNG phải số tiền nhặt được**: `Items_Manager` chia budget `n/5`:
  **28 → 3×70001 + 5×70002 = 8 object**; `q≥2 ∧ r=0` → `5×70001 + (q−1)×70002`; radius theo
  `q+r`: 1→bits9a99193e(≈.15) · 2–3→.75 · 4→bits6766e63f (**1.8000000715255737**, khác nearest
  1,8 một ULP) · >4→2,4; ellipse helper (eccentricity 0, minRadius) → pool → `IItem.BurstOut` →
  SetActive. **Chia 5 là luật chia budget — chưa chứng minh 70002 = +5 tiền khi nhặt** ⇒ pickup
  branch tiếp: `Player_Physics.ItemCollected 14bc328` / `OnTriggerEnter2D 14bc9c0` →
  `OnCollectCoin1/2` (`MISSING` row 8).
- **Kéo về:** `datas/enemy_hit_callback_flow.json` (4 bindings + 6 typed joins + 19
  co-attachments · 16 method ranges/1256 instr/56 anchors). Raw `raw/enemy-hit-callbacks/` +
  `raw/pickup-currency/` (Item_Movement · Player_Physics · Sub_Item · Tech_Datas ·
  Droid_Movement1 · GP_Setup · Device_*) giữ ở nhánh peer.
- **Queue peer đã ghi nhận request của mình** (wing-cannon `SetBarrels`/getter `14b1eb0` + drone
  base-fire — `DONE` lần 22): peer "review raw đã có trước khi nhận thành thiếu dữ liệu". ACK87 ✓;
  **chưa ACK88** ⇒ ACK bằng comment PR12.
- Models `enemy_hit_callback_models.py` (**38 tests mới**); full **450 PASS**; code `16748ccc3` ·
  Verify `40213772726 SUCCESS 55s`.

### 24.22 Report 89 — pickup → callback thật → số xu được cộng (peer `eaa5c74342`→`c30dd46eb2`, **500 tests**)

- **Hai đường nhặt — KHÔNG đều post event2** (sửa theo góp ý review `de2d1366`, PR12 `6401242325`):
  **player** — `OnTriggerEnter2D 14bc9c0` check tag **Item** TRƯỚC `activeHitEnemey@0x90`/
  invisible@0x91 → gọi **`ItemCollected` TRỰC TIẾP** → pool — **không post event2** (thêm post2 vào
  đường player = đếm kép) · **drone** — `Droid_Movement1.Update/CollectItems`: distance<5 →
  `CollectTo` (chỉ set force flag, chưa post); distance<0,5 → **post2** → receiver `OnCollectItem` →
  `ItemCollected` (receiver này **không** pool); cả hai **strict**; `Item_Movement` cleanup y<−25
  chỉ pool, **không** cộng xu.
- `ItemCollected` định ID qua **`IPooling.GetID` slot 0** (interface — không theo tên prefab); byte
  table `77a086`, 13 entries `70001..70013`; alias coin **70001=70011 · 70002=70012** → Coin1/Coin2
  callbacks (**gán đè**, không Combine); callback null vẫn gọi `PlaySoundCoins` (helper có Time.time
  gate riêng — không suy "mỗi item phát một tiếng").
- **Công thức xu — KHÔNG còn suy từ chia 5** (đọc `GP_Datas.coinCount static+20`): `g =
  trunc((stage+10)/10)`; **Coin1** `A = min(1,5g;16)+2,5` · **Coin2** `B = min(3g;23)+12`; hệ số tech
  `L` (≤14 → 1; ≥15 → `1+(tech−14)/3`, f32 không int-div); **4 band strict theo balance**
  (FCMP `threshold,balance` — không đảo dấu): >5500L → **1/2** · >4300L → A×.25 / B/6 · >3300L →
  A/3 / B×.25 · >2500L → A×.5 / B×.5 · ≤2500L → A/B; ×(1+`addPercentCoinByDevice@54`) — device
  **id 5000..5999** → `GetStatValue2`/100; **×.86 nếu stage≤40** (bits `f6285c3f`
  = .8600000143051147); truncate → **ADD vào coinCount TRƯỚC** PostEvent48 `AddCoin` — delta 0
  vẫn store/post, không minimum 1; post đồng bộ, listener có thể reenter.
- **Mốc dễ sai**: stage41/tech0/device0 — balance2500 = (10,27) · 5501 = **(1,2)**; **không ép xu
  tối thiểu 1**; tech17 → L=2 (thresholds ×2); stage40 khác stage41 ở hệ số .86. Burst 8 item của
  88 thu đủ từ 0: stage1 = **69 xu** · stage41 = **165 xu** — conditional example, không fixed
  payout, mỗi pickup đọc balance mới. `coinCount` = ledger gameplay, **không** đồng nhất wallet
  persistent.
- Nguồn stage/tech có mode gate: `get_stageIndex` (Test → `mapCurrentPlayTest`) ·
  `GetTechLabLevel` (mode==4 ∧ scene "Game" → 0). `GetStatValue2`: `row =
  listStatValues[trunc(id/1000)+4]`, row[rank]=0 → 0; **bảng số trong test là synthetic**, không
  phải bảng APK mới trích.
- Kéo về: `datas/pickup_currency_flow.json` (**20 method ranges/3530 instructions** · 63 anchors ·
  124 arithmetic rows · 4 callback bindings · 6 type joins · 3 literals · **36 payout pairs**).
  Full **500 tests PASS**; code `0a700993d` · Verify `40214936072 SUCCESS 55s`; findings peer giao
  PR12 comment `6400594184`.
- ACK87 ✓ · **ACK89 ✓** (PR12 comment `6400668714`).

### 24.23 Report 90 — Level → wing barrels + luật bắn 12 drone hiện hành (peer `39b377383`→`bf4827ae2`, **592 tests**)

- **Level là shared, không đọc từ prefab**: `Player_Ingame.get_Level 14b1eb0` (static+4, cache −1 →
  `GetStartPowerUpPoints 14e5404`) · tech tier 0–4 · `cap = 6 + min(techTier + abi12 + 2·abi13, 4)` ·
  `startLevel = min(startTier + UseItems[3] (cộng 3, xóa cờ), cap)` — không thêm lower clamp.
- **Wing (chỉ impl1/source10003, binding 81)**: ctor int[10] **[3,4,5,6,7,8,9,12,13,14]** (SHA-bound);
  `SetBarrels`: `index = L>2 ? (L−2)/2+2 : max(L,0)` ⇒ bảng L0–10 = **3,4,5,5,6,6,7,7,8,8,9**;
  `shotRate = .12 − .0035L` · `speed = min(14 + 1,1L; 42)` · `angle = min(3·trunc(L/10)+5; 15)`;
  super(.06, 20) · `numberSuper = 20` riêng, không tráo; Shoot dual-timer — nhịp barrel =
  `((shotRate−.01)×.3)/10` (**mẫu số 10 = độ dài array**, không phải numberNormal); StartAttack BC =
  +,168 (`31082c3e`).
- **Drone 12 impl hiện hành** (`Drone_Get_Datas 2adbd90`, **không** dùng legacy `Droid_Attack`):
  shotRate/turn/charge/speed/projectile từng impl (1–12); **Drone3 `turnRate8` chỉ là ctor default —
  serialized live = 1,0 (report 92: offset 100, bytes `0000803f`; OnEnable không ghi lại)** ·
  Drone4 turnRate=0 do **OnEnable ghi** · Drone9 width10 cũng serialized được bóc (92). **ability25**: `newRate = baseRate / (2,5 × abi25 đọc lại)` — **không phải**
  `/(1+2,5×)`, không giảm 2,5 %. Scheduler: families 2/3/5/6/8/10/11/12 (charge → shot deadline →
  đếm từng barrel tới `turnNumber` → charge); sweep4 (quay 20°/s theo phase ±16) và laser 7/9
  (timer strict >, laser 7 tick hết hạn **không damage** vì Check thấy actived đã clear) — riêng từng
  cái, không quy về projectile loop.
- **Damage drone**: `GetBaseDamage 14da6f0` = `BaseDamages[sourceID−20001]` × (1 + ,16×GetDroneLevel)
  × (1+rankExtra: r1 0 · r2 ,2 · r3 ,35 · r4 ,5 · else ,56) × (1 + 2,5×abi21);
  **BaseDamages[12] = [450, 600, 6000, 135, 935, 315, 650, 1200, 248, 650, 1200, 2650]**.
- **Scope giữ đúng**: sourceID→impl/spawn **chưa mapping** (class suffix không tự chứng minh source
  ID); 23 wing impl còn lại; `turnRate3` serialized live value; DPS closure — chưa.
  Kéo về: `datas/wing_drone_flow.json` (**73 ranges/6041 instr** · 68 anchors · 44 numeric fields ·
  9 projectile-loop proofs). 92 tests mới; full **592 PASS**; code `bf4827ae2` · CI `40216724849`.

### 24.24 Report 91 — trả lời request spec: HP writer + consumer `Board_Drones` (peer `142eb5998`, **648 tests**)

- **HP max tàu = công thức chung, KHÔNG bảng theo tàu**: `GetStartHp 14e311c→14e318c` =
  **2500 × (1 + 0,18 × TechStatPoints(0) + 1 × ability7)** (f32 từng phép; point1/ability0 =
  2950.000244140625 — không ép int; ability7=1 → 5000; wrapper tech mode4/scene Game → 0 cho
  index0). `Player_Health.cctor 14c7cd8`: default **StartHealth=2000/Current=0**; tàu 1 đo runtime
  **2500** = 0 point/0 abi7 — **không universal**.
- **3 loại writer**: `ResetStaticVariables 14c6ca0` (Current=Start, không post21) · callback
  **event36** (payload==7 → chỉ ghi StartHealth — mất bonus có thể Current>Start mới) · **event64**
  (`playMode==1 ∧ waveIndex≠0` → giữ tỉ lệ Current/Start rồi post21; else reset) — điều kiện là
  **waveIndex**, không phải index tàu. **`OnChangeDataDevice 14c58ec` không ghi max** — chỉ
  `reduceDamageByDevice` (Device.id 1000–1999, `GetStatValue1`/100) + `deviceHeal` (5000–5999,
  `StartHealth×GetStatValue1`/100), reset trước null-check, không clamp.
- **Auto-gain**: `AutoGainHealth 14c7bc8` mỗi **5 s** (InvokeRepeating literal đã decode) — **guard
  `CurrentHealth > 0`** (không hồi sinh tàu đã chết; clamp-đầy + post21 không thay guard) =
  techHeal + deviceHeal, clamp StartHealth, **không nhân deltaTime**; `GetHpRecoverSpeed` theo
  **TechStatLevel(0): 0 → 0** (level0 KHÔNG phải ,01×1,0; **âm rơi nhánh base** — report 91, không tự thêm ≤0) · 1→,01 · 2→,01×1,03 ·
  3–4→,01×1,06 · 5–7→,01×1,08 · ≥8→,01×1,10; `TimeToImmuneOneHit`: ≤0→MaxValue · 1–3→50 · 4–5→45 ·
  6→40 · 7–8→35 · 9→30 · ≥10→25.
- **`Board_Drones` 3 bảng UI có consumer thật** (≠ combat): ctor float[24] = **`playerPriceMultipleA`
  @238** → `SetUpgradeCost` (giá nâng cấp UI, index = cellIndex − 20001); static10/18 =
  **allBasicAtk/allDeltaAtk** (12 float `[500,600,800,1250,1500,1800,2300,2800,2535,2500,1251,2680]`
  / ,16×12) → `GetPlayerPower 1263860` → `SetPlayerInfo` → `textDispDamage`: `power =
  round-half-even(basic[i] × (1 + delta[i] × GetDroneLevel))`. **UI power ≠ combat
  `GetBaseDamage`** (20001: UI 500 vs combat 450 · 20003: UI 800 vs combat 6000) — cấm xác nhận chéo.
  `Board_Players.allBasicAtk/allDeltaAtk` (24 float) **vẫn chưa có consumer**.
- Kéo về: `datas/player_hp_board_flow.json` (**20 ranges/1589 instr** · 80 anchors · 5 joins · 3 array
  bindings · 1 literal). 56 tests mới; full **648 PASS**; code `4b7a01a69` · Verify `40217833652`.
- **Góp ý 5 điểm của peer vào spec (report 91 §6) — đã xử lý hết ở lần 28 này**: ① áp 90 đúng scope;
  ② HP writer thay mức D bằng công thức; ③ không xác nhận chéo Board↔GetBaseDamage; ④ tách
  "phân loại cấu trúc 576 (xong)" khỏi "binding entry (unknown)" ở `MISSING` §5; ⑤ ledger ACK
  đồng bộ (đã sửa "chưa ACK89" ở §24.22). ACK90+91 qua PR12.

### 24.25 Report 92 — 12 modern drone: save → getter → resource → prefab → serialized (peer `713be8c85a0`, **683 tests**)

- **Mapping sourceID → implementation ĐÓNG** (không còn đoán theo suffix): `StartDrones 14f2864`
  ghép literal **`Prefabs/Drones/Drone_`** + ID; ResourceManager keys lowercase; **12 bindings
  20001..20012 → `Drone_Attack1..12`** (root GO + component pathID + MonoScript, đều trong
  `resources.assets`); mỗi class có thêm **2 bản UI** (`boards/board_drones`,
  `popup_common/popup_newdrone`) — giữ riêng 3 context, không lấy UI thay gameplay prefab; 5 legacy
  `Droid_Attack*` không thuộc bộ 12.
- **Drone3 serialized** (component 627384/GO 26346, 124 B): id=20003@32 · barrels 1@84 ·
  **turnRate 1,0@100** (`0000803f`) · shotRate 2,0@104 · shotSpeed 24@108 · idBlt **80084@112** ·
  turnNumber 3@116 · damage 0@120. ⚠ **Không bê serialized vào runtime**: idBlt 80084 nhưng OnEnable
  cấu hình **80014**; Drone4 serialized turnRate 1 nhưng OnEnable ghi 0; Drone8/11/12 nhiều field 0
  được OnEnable cấu hình lại. ⇒ **gap `turnRate3` ĐÓNG: live = 1,0** (chargeDeadline = now + 1).
- **Save slots**: `GetDroneUsed(slot)` key `DroneUsed{slot}` default **0 = không drone** (không
  20001); âm → SetInt 0 rồi đọc lại; `SetDroneUsed` arg2 = **drone resource ID** (không phải player
  impl index); `CheckDoubleIDDrone` là **routine riêng** (2 slot bằng nhau ∧ slot0≥1 → duyệt 20001+,
  ≠ slot1 ∧ unlocked → ghi slot0; **không cap 20012**). `get_indexDrones 14f2a2c`: **new int[2]
  mỗi call**; playMode≠4 → [slot0, slot1]; **playMode4 → [0,0] không đọc save** (không có scene gate).
- **StartDrones**: gọi getter **lại từng slot** (không snapshot dùng chung); ID<1 skip; Load +
  Instantiate dưới `parentDrones.GetChild(slot)`; scale **(0,8 · 0,8 · 1)** exact f32 (`cdcc4c3f`);
  localPosition slot0 **(−20,−20,0)** · slot1 **(+20,−20,0)**; SetActive true; không range-check/
  dedup trong method (ID dương không tồn tại vẫn đi tới resource-load attempt).
- Kéo về: `datas/drone_loadout_flow.json` (**5 ranges/319 instr** · 29 anchors · 4 RELA joins · 36
  serialized IDs đối chéo raw bytes). 35 tests mới; full **683 PASS**; code `8bb7bd717` · Verify
  `40219912118`; review độc lập `de2d1366` của peer: 3 sửa 91 **ĐÚNG** + 3 góp ý wording (đã xử lý
  hết ở lần 29 này); ACK92 qua PR12. **Còn: 23 wing impl** + named map/save consumers.

### 24.26 Report 93 — review ACK92 ✓ + đọc rộng 24 wing, cấu hình SetBarrels 17 impl (peer `32bed14da8a`, **761 tests**)

- **Review `c80b1c50dfd` ĐÚNG hết** (3 góp ý 92 xử lý đúng, không pending ACK) — không góp ý mới.
- **Đọc rộng**: raw `wing-implementations/method-bytes.json.gz` — **876 method bodies/24 impl+class
  lồng nhau · 66.845 instructions** disassemble Cap 5.0.3 đối từng instruction (0 decode gap); sửa
  collector giữ GOT load offset **decimal `#8`**. Kéo về: `datas/wing_implementations.json` (24 rows ·
  14 constructor-array joins · 85 vtable-load sites/83 CFG must-owner · 7 named special paths).
- **Cấu hình normal SetBarrels: 17/24 impl** (impl1 cũ + **16 mới**): `S−kL` (k ,001–,03, có floor
  ,02–,2) · `min(V+cL, cap 38–45)` · angleDelta riêng từng impl (impl19 không có speed field ·
  3/18 chọn barrel-list). **Count 3 kiểu**: compressed two-read (index 0,1,2,2,3,3,4,4,5,5,6) —
  1/3/11/16/17/18/20/22/23/24 · **L−1** — 5/7/9/14 (không upper-clamp trước bounds) ·
  **clamp(L)** — 13/21. **14 constructor arrays** đã nối SHA (vd impl7 `3,5,5,7,7,7,9,9,9,9` ·
  impl20 `6,6,8,8,10,10,12,12,14,14` · impl14/16/23/24 toàn 1 — **không** kết luận 1 đạn/volley).
  ⚠ Bẫy đã bắt: 13/21 dùng clampL **không phải** L−1; **impl20 super vẫn ghi angleDelta** (không
  universal "super bỏ qua SetBarrels").
- **Fixture Unicorn2.1.4 chạy nguyên native bytes** (FPCR=0, adapter 6 dependency): 78 tests mới ·
  full **761 PASS**; impl2=10002 giữ proof raw prefix (id@byte32 ×4 objects).
- **Còn**: 7 special paths named (2 particle · 4 FindAndAttack · 6/8 saw · 10 AttackNormal/Enemy ·
  12 sync/animation-event · 15 laser `GunCheckEnemies` — 2 site chưa must-owner proof, ghi false rõ)
  + super branches + các impl thuộc special — **không** báo đóng toàn bộ 23 firing impl.
  ACK93 qua PR12; peer **đã nhận queue Arena/PvP** (`arena-pvp-queue-6401593117.json`).

### 24.27 Report 94 — wing 13/22/23/24: Shoot → coroutine → packet geometry (peer `e03fdb1515`, **814 tests**)

- **4 Shoot chain** (đúng thứ tự, không cache "now"): 13 `StartCoroutine` **trước** rồi mới ghi
  deadline; 22 loop đồng bộ đọc `childCount` sống — mỗi child 1 Basic packet; 23/24 ghi deadline
  trước rồi coroutine, **đọc lại rate/childCount sau mỗi packet** + trailing yield. Callback sửa
  shotRate trong StartCoroutine ảnh hưởng deadline 13, **không hồi tố** 23/24; 22 không child vẫn
  tiêu deadline; barrel null có thể throw **sau** khi ghi.
- **13 IBullet → SetBullet/SetActive**: 2 sides/yield · x ± width·i · angle ±4·i · lifetime **2**
  (không damage) · `through = super ∧ throughShield` — nhánh IBullet PRESENT đã chạy tới SDK adapter.
- **Basic 22/23/24**: N chẵn + spacingX = 0 ra **N+1 terminal calls** (N=0 có thể center); Circle
  dùng worldXYZ và **không** lọc id−1. **Leaf ENTRY = ranh giới quan sát** — không suy pool/hit/DPS.
- **Sửa nhãn sai của collector**: `15b50ac` = `PlayOneShot(AllClipName, float)` clip 5 (super ,04 /
  normal ,08) — **không phải camera shake**.
- Kéo về: `datas/wing_emission_flow.json` (**39 method bodies/3.208 instructions** · pool 8 bytes
  VA `7575e0` = f32(.04), f32(.08)). 53 tests mới; full **814 PASS**; code `589e1f588`; ACK93 ✓
  (`6401658709`), spec mới chưa bị review độc lập. Tiếp peer: named firing leaves/consumers →
  named map/save → Arena/PvP (giữ thứ tự, không chờ ACK94).

### 24.28 Report 95 — 5 pooled leaves Basic/Circle 22/23/24 + trampoline (peer `4981c4ce2`, **854 tests**)

- **5 leaves KHÔNG chung lifetime/speed**: 22 Basic `14a3f50` (**5**/owner.btlSpeed) · 22 Circle
  `14a3d80` (**5**/speed arg) · 23 Basic `14a5d2c` (**4**/owner + **có formation**) · 23 Circle
  `14a58b4` (**10**/speed arg) · 24 Basic `14a8420` (**4**/owner + formation). Force 1 · target null ·
  mask = `owner.targetLayer`. **throughShield = owner trực tiếp** cả 5 (khác 13: super ∧
  throughShield ở consumer — không từ leaf suy xuyên shield).
- **Rotation/pool**: Basic = `point.eulerAngles.z + packetAngle` → FromEulerRad; Circle = packetAngle
  thôi; **SetBullet đọc lại pooled `eulerAngles.z`** (không truyền packetAngle làm startAngle);
  Pool null → throw (không silent-skip).
- **Activate TRƯỚC khi biết IBullet** (khác 13): cả 5 leaf SetActive(true) rồi mới GetComponent —
  thiếu IBullet: 22/23-Circle return **không** PoolObject · 23/24-Basic **có** PoolObject.
- **Trampoline 23** `14a6008` **branch ra ngoài method** → `2990890`: peer không đoán opcode —
  recovery `40223486658` lấy 64 raw bytes (`ldr x10,[x10,#0xbf0]; b #0x14a600c`), fixture chạy
  nguyên bytes, lân cận giữ raw **không** gọi là code đã đi qua.
- **Basic23/24 formation callbacks**: Combine **formation.OnCollided/OnDestroyed trước, caller sau**
  (GOT `2ae8020/28`); `CreateBullets(force, null, layer, btlSpeed, 4, caller-collision-gốc)` đọc
  speed/mask **lại** sau SetBullet. N=2 spacing 0 đi **3 leaf/3 SetBullet thật** (không chỉ entry);
  Circle id−1 vẫn Pool với bitpattern `ffffffff` (Pool thật xử lý là việc riêng).
- Kéo về: `datas/wing_pooled_leaves.json` (**5 bodies/837 instructions** · 4 RELA joins).
  40 tests mới; full **854 PASS**; code `772839187a`. **Chưa chạy bên trong** (ghi rõ consumer tiếp):
  PoolManager, engine transform, IBullet concrete, `Bullet_Formation.CreateBullets 123d98c` (raw có
  ở combat-chain) — không lấy 95 làm giấy đóng 23 wing hay DPS/hit. (⚠ giữ `datas/PROVENANCE.md`
  · `boss_anim_events.csv` · `player_start_stats.json` bên mình dù peer xóa ở nhánh họ — spec
  tham chiếu trực tiếp; tổ chức datas hai bên có thể khác.)

### 24.29 Report 96 — Đưa L3 lên ưu tiên chính + UI screen→node→sprite index (peer `79fd382fff`, code `8789ef433`)

- **Đổi ưu tiên theo chủ dự án**: **hoàn thiện chuỗi L3 trước** (hình trong đúng cảnh · bố cục ·
  thứ lớp · ánh sáng · chuyển động · nhịp FX/âm); wing/map-save chỉ đào khi là **dependency cụ thể**
  của cảnh/hiệu ứng cần dựng. Không lấy export/test xanh/số native kết luận L3 đủ; không blind-A/B.
- **Bảng 6 mắt xích L3** (§1) — mỗi mắt ghi "thiếu cần làm", cấm đổi thành "đủ": identity/meaning →
  **asset→UI/cảnh** → composited (hierarchy/material/blend/light/particle trong cảnh) → motion/juice
  (ghép object/state, transitions, camera/feedback) → sound-đi-với-hình → **đối chiếu đầu ra** (gate
  chưa chứng nhận; cùng metric ≠ cùng hình).
- **Review spec `b000f905`**: lần 33 đính chính L3 **ĐÚNG** ✓ — nhưng còn stale: README mục "L3 bỏ"/
  "bỏ L2/L3" + `DESIGN_READINESS` câu "chỉ cần nếu làm L2/L3" ⇒ đã sửa ở lần 35 này (đánh dấu
  LỊCH SỬ / hiện hành). Đếm 505/643/27 của mình = **peer audit, chưa đo mới** — giữ nguyên nhãn.
- **UI binding index — ĐÓNG một phần gap lần 32**: `datas/ui_l3_bindings.json.gz` tra theo
  `sources`/`uses` (source index · node/component index · path · position/scale/rotation/size ·
  activeSelf · visual_properties raw); identity exact = **(serialized_file, path_id)** qua PPtr +
  externals, **không join tên toàn cục** (name_candidate_only không nâng thành exact). Đo:
  **797 sources/117 class** (thuộc `_index.csv`) · **76.806** sprite component observations ·
  **75.749** resolve nonnull · **1.057** null PPtr (không phải failed join) · **1.099 sprite identity
  khác nhau**; **54.787 file ngoài index chưa join** — không âm thầm gộp coverage. ⚠ **Sửa nhận định
  của mình**: report 43/46 **đã có** scoped joins — thiếu là bảng đủ rộng đưa cho design, không phải
  "chưa từng có". 12 tests binding mới; Verify `40224533473 SUCCESS`.
- **Queue L3 (thứ tự mới)**: ① UI reference chain (mở rộng ngoài index theo owner-scope: parent
  effective state, sorting/material/font, selected/pressed/disabled; đi Home → chọn màn/tàu/drone →
  HUD → pause/reborn → kết trận) ② gameplay appearance chain (player/drone/enemy/boss/bullet/
  pickup/background → prefab → SpriteRenderer/mesh/material/particle/Spine → clip/state/event).

### 24.30 Report 97 — audit đủ 55.584 layout + composition (peer `06ab4ef2b`, tests UI mới)

- **Không bỏ 54.787 file ngoài index — cũng không coi là 54.787 màn thiếu**: full scan
  (`ui_layout_inventory.py`, ~132 s + hash regression toàn file) → `datas/ui_layout_inventory.json.gz`
  + 4 shards: ngoài index **3.843.228** sprite-obs **chỉ còn tên** · **0** scoped `m_Sprite` ·
  **1.003.504** TMP không font PPtr (schema legacy không giữ) ⇒ **exact identity từ layout legacy
  là bất khả** — muốn exact phải về serialized source; 30.827 topology groups · 14.081 file match
  indexed (409 groups) · 30.418 groups không candidate. ⚠ **Sửa hướng đọc report 96 của mình**:
  "54.787 chưa join" ≠ "54.787 màn độc lập chưa biết" — cùng 117 class label có trong index.
- **Composition** (`datas/ui_composition.json.gz` + 6 shards): **100.312** visual-component obs ·
  **99.731** matrix TRS (581 ambiguous — không thay bằng identity) · activity 89.754 F / 10.409 T /
  149 unknown · **76.802** material exact scoped join · **18.467** TMP font + sharedMaterial.
- **Bẫy slash thật**: node `TMP SubMesh [TextMeshPro/Sprite]` chứa `/` — split cuối bịa thêm cấp,
  mất 1.478 parent matches; sửa bằng suffix `/` + name; **160 ambiguous parents** giữ nguyên.
- ⚠ **renderer_enabled = unknown** (exporter whitelist không có m_Enabled) — không default true.
- Backlog đổi từ file-sang **source/scene chains**: ① recovery PPtr identity + m_Enabled ② ghép
  font/material/renderer + camera/Canvas theo flow Home→chọn→HUD→pause/reborn→kết trận
  ③ gameplay appearance chain ④ sau khi đủ chuỗi mới dựng/đối chiếu output.

### 24.31 Report 98 — chuỗi APK → scene recipe → hình/motion/VFX/audio (peer `1f2d12f6e`, **921 tests**)

- **Root views: 805** (12 core UI: Maps/Players/Drones/Reborn/Endgame/Stage, 3 Reborn_IAP, Home,
  Pause, GP_Tutorials + 793 resource GO) · 37.766 logical/25.536 visual nodes · 3.504 typed assets ·
  1.587 animators · **665/665 clips numeric channel-exact** (301.603 streamed keys; đã sửa 31 sprite
  clips: cộng `discreteCurveCount`; sprite keys giữ mapping rời rạc, không blend pointer) ·
  **52.400 bindings** (51.990 unique / 393 unresolved / 17 ambiguous) · **2.139 callbacks** (904
  persistent + 1.235 anim-event) · 2.037 AllClipName · 92 SoundClip. Raw 128.724 objects /
  345.090 edges; 0 read failure; 5 header-only (GunEventCatcher, Player_Attack_2…) giữ rõ.
- **3 recipe mẫu** (CLI `tools/verify/l3_recipe.py`, `--include-raw`, header thắng raw cũ):
  **Board_Pause** root10 — 235 nodes/404 assets/4 Animator/5 clips (Appear 0,5 s · Hide 0,333 s)/
  15 callbacks/26 sound fields; `Button_Sound.soundClickDown=1 → Sfx_ClickDown → AudioClip:1695`,
  native `OnDown@0x141fdc4`/`OnClick@0x141fddc` nối đúng class+field; **Effect90045** root402 —
  48 nodes/68 assets/310 bindings, ParticleSystem giữ serialized modules; **Player_Attack_13**
  root769 — 33 nodes, bridge enum5 `Sfx_Shot1 → AudioClip:1752` (khớp `wing_emission_flow`).
- **Camera không bị bỏ**: 5 Camera + 1 Canvas (level0) + native size writers nối qualified identity
  với `datas/camera_scaler_contract.json` (SHA pin): `max(h/w × 5,4; 9,6)` — không nhầm
  CameraScaler (game) với CanvasScaler (Unity).
- Kéo về: `datas/l3_scene_chains.json.gz` + 37 shards `l3-scene-chains/` · `ui_layout_inventory` +
  `ui_composition`. **Đối chéo độc lập bằng datas trong repo (lần 36): counts khớp 100% report 98 ·
  camera contract + composition + inventory totals khớp 97.**
- **Review độc lập đợt 2 (lần 37 — peer ghi CI xanh `40229636747 SUCCESS` @ receipt98/handoff
  `6402605773`)**: đếm **từng loại từ 22 shards riêng** (không tin `counts` tổng) — callbacks
  **2139** ✓ (904 persistent + 1.235 anim-event) · sounds **2037** ✓ · animation_bindings **52400** ✓ ·
  assets **3504** ✓ · scene_context **5 Camera** ✓ (+1 Canvas) · `camera_scaler_contract.json` chứa
  formula + factor 5,4/min 9,6 ✓ — **khớp 100% cả 6 điểm đo được**. 5 điểm nhờ review: header
  authority/ambiguity/discrete-keys = proof gốc ở raw (bên peer); camera ownership + callback/sound
  gates **đã xác mức data**. ACK97/98 ✓ (comment `6402657559`); batch L3 **CI xanh toàn chuỗi**.
- **Không phải**: rendered approval · 805 views ≠ 805 prefab độc lập · batch 12 core không nhận công
  797. Tiếp: recipe → composition/playback, không thêm vòng inventory.

### 24.32 Report 99 — Animator programs + property probes (peer `4d0dc6906`→code `5c3ba250d`, CI `40230913183 SUCCESS`, **940 tests**)

- **Controller → state → clip → thuộc tính đúng object** (không còn controller là raw blob):
  **232 controllers/232 machines/667 states** (mỗi controller 1 layer) · **1.587 Animator** nối
  direct `m_Controller` (không nối vì trùng clip/name) · **377 parameters** (tên theo `m_TOS`,
  typed default slot) · **343 AnyState + 125 state transitions** (destination/điều kiện/eventID/
  threshold/exit-time/duration/interruption — giữ source) · **666 motion leaves** nối hết đúng
  scoped clip; 1 empty machine + 1 state không motion **không tự chèn**; destination encoded
  30001/30000/UINT_MAX giữ là selector/exit (không ép index).
- **Probe 665/665 clips** đầu/giữa/cuối — **1.853 clip-time probes**: 86.905 streamed + 51.926
  constant + 69 discrete + **1.461 initial-constant** (lỗi mô hình đã sửa: frame `-FLT_MAX` là
  key initial-value thật a=b=c=0, d = giá trị ban đầu — không phải unknown giả; sprite clip 965:
  mapping 0 có sẵn từ frame 0, key đầu 0,2333 s mới đổi) — **0 unknown tại các điểm probe**
  (không suy thành mọi timestamp). Kết quả = arithmetic model, **không** phải readback Unity.
- **Ví dụ Popup_QuitMissions** (Board_Pause): GO57508 → Animator **495980** → controller
  **1974** (tên Popup_Network reused — tên không đổi identity) → default state **Appear** → clip
  **1572**; probe: t0 scale 0/0 alpha 0 · t0,25 scale ~1,0304 alpha ~0,83137 · t0,5 scale 1/1,
  alpha **giữ ~0,83137** (serialized curve — không sửa thành 1 theo cảm giác).
- **Audit 410 non-unique bindings** = **376 path không có trong subtree + 17 thiếu hẳn component
  class** (13 cần MonoBehaviour mà GO chỉ có Transform/SpriteRenderer; 4 cần BoxCollider2D —
  *wording 98 sửa: không phải inheritance mismatch*) + **17 ambiguous giữ nguyên**.
- Kéo về: `datas/l3_animator_programs.json.gz`. **Đối chéo độc lập (lần 38): counts khớp
  10/10** (232/232/667/377/343/125/666/1587/410/1) · diagnostics **376/17/17** ✓ · Animator
  495980 → controller 1974 (324 refs) → clip 1572 (62 refs) ✓; probe values sống ở CLI output +
  raw `local99.json` (bên peer), không trong contract.
- **L3 VẪN CHƯA hoàn tất** (peer ghi rõ): còn script-driven runtime selection · transition
  scheduler/layer blending · driven RectTransform · particle sim · shader/stencil/culling ·
  composition qua viewport. Bước phải đi: **program/property model → composition/playback thực
  với external original assets**. ACK99 qua PR12.

### 24.33 Report 100 — script UI → activation → state/clip → event → deactivation (peer `0ce8cc017`, code `ad986c7b9`, CI `40232850860 SUCCESS`, **957 tests**)

- **Chuỗi Popup_QuitMissions (Board_Pause) ĐÓNG đủ bằng source** — lifecycle thật, không
  "chọn state bằng tay": GO **57508** inactive + `Popup_Notices.SetPopup@0x13b83cc` →
  **SetActive(true)** @0x13b83f4 → Animator **495980** → controller **1974** (tên Popup_Network
  reused) — **SetPopup ≠ Animator.Play(Appear)** (entry/reset là engine, chưa readback);
  `OnPressedButtonExit@0x13c5370` đọc `anim+0x20` → literal **"Hide"** (GOT→RELA→metadata, không
  tìm chữ trong disassembly) → `Animator.SetTrigger` → transition condition → state Hide → clip
  **1573**; event **OffBoard @0,333 s** → same-GO receiver **644901** →
  `Popup_Notices.OffBoard@0x13ca5dc` → exitAction + **SetActive(false) cùng GO 57508**.
  Guard `exitAfterConfirm+0x38` giữ symbolic (không gọi mọi confirm là đóng vô điều kiện).
- **Recovery native UI**: **1.074 methods/13 root classes** (namespace thật **TuPro** cho
  `UIObjectAnchors` — lần recover fail đã sửa đúng, không bỏ class); bytes dùng next-distinct-RVA
  + `span_decode_status` (không giả padding là instruction).
- **Counts** (`datas/l3_ui_drivers.json.gz`): **214 UI instances · 1.751 potential calls ·
  receivers 1.414 resolved / 337 unresolved** (không resolve ≠ source thiếu) · **230 animator
  routes · 687 exact receiver+RVA links · 409 callback/effects · +9 inherited candidates** (46
  old anim-event gaps: 9 có base-declared qua `Popup_QuitEvent : Popup_Notices`, 37 chưa).
  Sửa model getter: **+140 receiver joins** qua `get_transform`/`get_gameObject` edges (thiếu
  transfer function, không phải APK thiếu).
- Kéo về: `datas/l3_ui_drivers.json.gz`. **Đối chéo độc lập (lần 39): counts khớp 8/8** ·
  chuỗi Popup CÓ trong artifact (57508 ×24 · 495980 · 1974 · 644901 · 1573 · OffBoard ×168 ·
  13ca5dc · 13b83cc) ✓.
- **L3 CHƯA render-complete** (peer ghi rõ): CFG là over-approximation, chưa transition
  scheduler/runtime delegate/particles/shaders/composition; 5 header-only + 52 default-mesh
  giữ nguyên. Bước tiếp: composition/playback thực. ACK100 qua PR12.

### 24.34 Report 101 — camera → safe-area → UI anchors/renderer → recipe (peer `91a0ad6df`→code `b18e783a7`, CI `40236171639 SUCCESS`, **984 tests**)

- **Quét toàn APK 125.453 MonoBehaviour headers**: **584 TuPro.UIObjectAnchors + 1 ObjectScaler**
  (= 585 typed instances); **1 header chưa phân loại giữ nguyên** (`resources.assets:580792` —
  thiếu `unity default resources`, không coi là chắc chắn không có target class); typed read
  errors 0. Bounded context **2.526 objects · 9.161 edges resolved / 660 null · 0 unresolved**;
  parent poses đủ 585 targets; 0 pose errors; 0 unmodeled affine bridges.
- **Camera**: 6 camera nối đúng **6 native CameraScaler writer bindings**; 4 MainCamera-tag
  candidates thuộc scene khác nhau (không phải 4 camera đồng thời); **576 anchors thiếu
  serialized uiCamera / 8 explicit** — không tự chọn Camera.main từ danh sách global. Native
  Start gán Camera.main qua `op_Implicit`; **gọi ObjectAnchor trực tiếp KHÔNG tự chạy Start**
  (guard playOnStart). 461 playOnStart=true / 55 fixed-max (flags có thể runtime đổi).
- **Semantics lấy từ native**: enum None0…Right9; GetRootAnchor jump bytes `00090f03070d0a10`;
  roots ±5,4/±9,6 đọc literal + kiểm bằng execution. General path ghi world rồi restore local.z;
  Left/Right chỉ sửa world-X, **không restore local.z**. Fixed-max: min(UI half-height,
  clampCamSize default **12.420000076293945** — static mutable, CLI hỗ trợ override finite) +
  aspect clamp [0,43478259444236755; 0,75]. Top/bottom dùng SafeArea của Camera.main; cache chỉ
  recompute khi top/bottom có 0.
- **Alert (level2)**: ObjectScaler **6686 → SpriteRenderer 5105**, cùng owner **GO110 `Alert`**
  (+ Animator **4647** — metadata-only, KHÔNG có attachment trong bank animator-programs); H14
  full/clamp: height **24.84000015258789**; drawMode1/width 10,8; sprite `sharedassets2.assets:114`
  · material `globalgamemanagers.assets:2` — size/identity chain, KHÔNG phải render proof.
  Join bank100: **92 call links / 85 anchors** (không phải complete census); Pause:
  callsite 0x12cb150→597593 (top) · 0x12cb160→616420 (bottom).
- **Probe synthetic** 1080×2400, safeRect [0,96,1080,2208] → half-height
  **12.000000953674316**; Pause top 597593 worldY 7,9→**9,34** (model = native); H14 → 11,18
  (raw, không gán cho máy thật). Unicorn chạy source bodies NHƯNG metadata/engine stubs + dùng
  chung float64 affine bridge ⇒ **không phải Unity transform/render proof**.
- Kéo về: `datas/l3_layout.json.gz`. **Đối chéo độc lập (lần 40): counts khớp 13/13**
  (2.526 · 9.161+660 · 585=584+1 · 6 cameras · 4 candidates · 576+8 · 20+4 native checks ·
  0 pose · 0 read · 1 header error đúng 580792) + **461 playOnStart / 55 fixed / 85 anchors-92
  links đếm lại từ instances** ✓ · chuỗi Alert 6686→5105/4647 + Pause 597593/616420/690342 +
  callsites ✓ (sprite/material lưu tách field file+path_id). **L3 CHƯA hoàn tất** (peer): tiếp
  geometry/material/font + particle/shader/composition + engine transition/blending. ACK101
  qua PR12.

### 24.35 Report 102 — layout-owner visual construction (peer `9d38a08d1`→code `d1a65f01d`, CI `40238106907 SUCCESS`, **1012 tests**)

- **Scope: descendants dưới 585 layout owners + asset closure** — KHÔNG phải toàn APK, KHÔNG
  phải cả 797 recipe roots; recipes công bố coverage/out-of-scope IDs.
- **Đào visual thật từ source**: **56.714 objects / 16.061 GO · 11.380 renderers · 153
  materials · 17 shaders** (parsed + decompiled-analysis — **KHÔNG phải replacement shader hợp
  lệ**) · **1.389 sprites + 2 meshes** decode geometry số (không phải render) · **7 fonts /
  7 atlases / 2.354 character entries · 1.737 texts · 954 particle modules** (data có, simulation
  KHÔNG claim) · **đủ 348 clips** decode đúng channel widths · **1.057 animators / 91 controllers /
  79.907 bindings (74.916 unique / 4.983 unresolved / 8 ambiguous)**. 0 read failures; **1
  header-only** giữ nguyên (Player_Attack_2 `resources.assets:704560`); **7 unresolved builtin
  ParticleSystemRenderer mesh refs** (`unity default resources`) giữ — không bịa default mesh.
- **Alert gap (101) ĐÓNG mức source/model**: level2 GO110 scaler 6686 → renderer 5105 / sprite
  `sharedassets2.assets:114` / material `:2` / shader `Sprites/Default`; animator **4647 →
  controller `sharedassets2.assets:78`** với states **none44 / alert42 / fade43**; binding
  path0/type212 → cùng `renderer.m_Color.a`; clip alpha **0 → 0,784313738 trong 0,125 s**,
  reverse trong 0,25 s; params Alert/Fade giữ. **KHÔNG** state scheduling / trigger delivery /
  blending / render acceptance.
- Kéo về: `datas/l3_visual_surface.json.gz` + **249 shards** `l3-visual-surface/` (3 animators ·
  200 bindings · 1 controllers · 1 fonts · 4 geometry · 1 materials · 1 motion · 3 particles ·
  29 renderers · 1 shaders · 5 texts). **Đối chéo độc lập (lần 41): counts khớp 17/17** (gồm GO
  16.061 đếm lại từ `source_gameobjects` · header-only đúng 704560 · unresolved_edges đúng
  ParticleSystemRenderer/.m_Mesh) + **249 shards đúng cơ cấu** + **Alert chain trong chunks**:
  controller 78 tên "Alert" · clips none44/alert42/fade43 · alert42 chứa 784313738 + 0.125 ·
  fade43 chứa 784313738 ✓.
- Xin audit: MeshHelper coords/UV/index vs không sign-flip OBJ; live-atlas/sliced/tiled/
  skinning/TMP procedural; integer-list buffer redaction; glyph rect/atlas bounds + static
  fallback; source-qualified Alpha CRC binding; recipe scope coverage. **L3 CHƯA hoàn tất**:
  tiếp camera/composition/culling + actual geometry generation/engine execution. ACK102 qua PR12.

### 24.36 Report 103 — camera → world pose → geometry → layer gate/clip → composition (peer `8febe90e11`→code `dddd75aed8`, CI `40240026886 SUCCESS`, **1043 tests**)

- **Merge raw101+102** (không recovery mới): qualified file/pathID, kiểm **1.760 overlapping
  bodies cùng raw SHA** + pointer edges không xung đột → **57.480 objects** trong merged graph.
- **11.380 renderer world poses** dựng đủ từ typed Transform/RectTransform parent PPtrs (gồm
  root local TRS — khác matrix layout-root frame r95); parent thiếu/cycle KHÔNG thay bằng
  identity. Phân loại: **558 thuộc serialized scene level0–3 · 10.822 asset templates** (không
  tự coi đã instantiate).
- **6 camera** đầy đủ pose/projection/mask/clear/depth/display/target + writer bank101
  (sharedassets0:79 vẫn là template). **1.104 same-scene pairs = 558 pass / 546 fail layer
  mask** — chưa cộng footprint/alpha/shader, không gọi là visible; không tạo total draw-order
  từ sortingLayerID; không coi camera khác scene là một live stack.
- **Alert chain (source/model đến footprint — siết wording theo góp ý peer, lần 44)**: 1080×2400 → half **12.000000953674316** → native ObjectScaler size
  **10.800000190734863 × 24.000001907348633** → position-only zero-border sliced rect (border≠0/
  tiled = not_generated, không dựng quad thay) → world z=1 → depth 11/21 ở Game 3975 (z=−10) /
  Main 3976 (z=−20); footprint giao viewport ở cả hai NHƯNG **mask 7959 (Game) LOẠI layer5 ·
  mask 32 (Main) GIỮ**; Main footprint ~full viewport
  [0.000033378598385258584, 0, 1079.9999666214017, 2400]; alpha alert42@0,0625 =
  **0.3921568840742111** (từ 102) — không apply trigger, không thành rendered frame.
- Geometry/clip làm thật: affine inverse + uint32 layer test + ortho projection (+Z forward);
  triangle clip **6 planes** giữ case mọi vertex ngoài mà triangle vẫn cắt màn hình; simple
  sprite dùng decoded vertices; TMP/procedural/skinned/particle/line/trail + UV/live-atlas/
  skinning/vertex shader/raster/occlusion/depth/blend CHƯA áp; float64 + non-rigid camera từ
  chối; probe từ chối template/cross-scene khi thiếu explicit full override matrix.
- Kéo về: `datas/l3_composition.json.gz`. **Đối chéo độc lập (lần 42): counts khớp 10/10**
  (11.380 · 6 · 1.760 · 57.480 · 558+10.822 · 1.104 = 558+546) + **mask xác minh bằng số học**:
  7959 & 32 = 0 (Game loại layer5) · 32 & 32 = 32 (Main giữ) · depth −1/0 + clearFlags 2/3 ✓.
  Probe values (10.8×24.0 · alpha .3921 · footprint) sống ở CLI/raw bên peer, KHÔNG trong
  contract. Recipe10 +8 template composition records. **L3 CHƯA hoàn tất**: tiếp actual
  geometry/driver application + shader/particle/text/spine execution. ACK103 qua PR12.

### 24.37 Định hướng vòng kế (chủ dự án — lần 43): probe compose thay vì tăng counts

Dừng mở rộng counts/contract riêng lẻ. Bước kế: **layout-write (101) + animation-write
(99/102) tác động lên CÙNG trạng thái Transform/renderer, rồi đưa trạng thái đó qua camera
(103)**. Đã gửi peer 2 probe cụ thể qua PR12 (dùng lại 101/102/103, không recovery mới,
không render):

- **Probe A — Alert 5105 (same-state compose)**: layout-write `ObjectScaler.Start` → size
  [10.800000190734863, 24.000001907348633] + anchor/parent pose GO110 → world transform;
  animation-write clip alert42 tại t ∈ {0; 0,0625; 0,125} → `m_Color.a` theo đường
  0 → 0.784313738/0,125 s (@0,0625 = 0.3921568840742111 từ 103) — xác nhận hai write chạm
  **khác field của cùng renderer**, không ghi đè; composed qua **Main 3976** (mask 32 giữ
  layer5, depth 21) → footprint px + camera-local depth + RGBA theo t. Đầu ra mong muốn:
  **3 dòng readback cùng một t** (layout-only / animation-only / composed).
- **Probe B — Popup_QuitMissions (Board_Pause root10)**: Appear (clip1572) tại
  t ∈ {0; 0,25; 0,5} → scale {0; ~1,0304; 1} · alpha {0; ~0,83137; giữ 0,83137}; popup
  GO57508 + Canvas thuộc resources.assets — theo phân loại 103 là **template context**: peer
  cho biết **placement authority** (override matrix tường minh hay scene2 instance) rồi camera
  nào trong 6 có mask giữ layer popup (nhiều pass thì depth/clear nào thắng theo snapshot,
  không tự tạo stack); xuất footprint theo t.

Câu hỏi kèm: harness Unicorn (101) + math (103) trả được composed state mức model không, hay
cần stub thêm? Ranh giới giữ nguyên: model ≠ readback Unity ≠ render — probe là **gate
  compose-state**, không phải render approval. Không kéo dữ liệu mới vòng này (datas/ = 65).

### 24.38 Report 104 — shared modeled frame: layout write + clip write trên CÙNG state (peer `f620ba4a67`, local **1072 tests PASS**; peer LÀM TRƯỚC/song song với probe A/B mình gửi — đúng hướng)

- **Peer review nhánh spec mình** (`raw/peer-review/l3-23bf66c7/` — snapshot DATA_SYNC +
  DESIGN_READINESS SHA-pinned): ① ACK giúp phát hiện sai sync nhưng **không thay
  numerical/native audit**; ② headline "Alert chain full"/"geometry làm thật" = **source/model
  đến footprint**, không phải full visual/runtime (đã siết §24.36); ③ **không dùng số file
  datas/ hay số tests như tỷ lệ hoàn thiện bộ mặt game** (bên mình: đó là inventory/gate
  verify, không phải % — giữ đúng nghĩa đó); ④ review chuyển sang **reproduction/
  counterexamples** (Start false vs direct Align, propagation, cache khi camera đổi, f32
  rounding, rollback, encoded pointer binding).
- `tools/verify/l3_frame.py` tạo **một shared modeled state**: explicit modeled Camera.main →
  CameraScaler half-height; **native bounded Start/ObjectAnchor/ObjectScaler chạy thật**
  (harness101) → writes persist vào state; clip-local channels → typed writes **float32
  store**; world matrices đọc lại từ overlay (không stale); projection dùng current
  size/color/pose/mask. Start explicit ≠ Unity đã dispatch khi inactive.
- **Case Alert = Probe A thực tế** (camera 3976, 1080×2400): serialized sau camera-resize
  sizeY **19.200000762939453** → native scaler **24.000001907348633** + alert42@0,0625 alpha
  store **0.3921568989753723 (float32)** — coefficient double **0.3921568840742111** giữ RIÊNG
  (không gọi là mismatch); projected 240.000038→2159.999961 rồi 0→2400; fade43@0,25 tiếp theo
  → alpha 0 (geometry KHÔNG bị xoá). Hai writer chạm khác field cùng renderer 5105.
- **Case Border_Info (mới)**: `level2:7048` GO1414/renderer5739 playOnStart=false — native
  Start chỉ bind camera, KHÔNG ghi position; explicit Align → worldY 7→**8.440000534057617**,
  **320 descendants** nhận cùng delta (đếm lại 320/320 ✓); child sprite 5452 px bottom
  1717.700156805613→1861.7001987672797; root 5739 border≠0 → **not_generated** (không dựng
  quad giả); safeArea cache dùng chung per-Frame, không tự refresh.
- **Pointer quan trọng**: sprite bindings attribute0/customType23/type212 (Animator4695 /
  resources clip1609) **KHÔNG thể gọi là CRC(m_Sprite)** — default writer từ chối; chỉ nhận
  explicit per-binding policy `m_Sprite` (log `explicit_custom_binding_field_policy`, sống ở
  tool/tests, không trong artifact); pointer override = runtime qualified ref, không bịa
  fileID. Clip transaction atomic = **bảo đảm của tool**, không phải Unity semantics.
- Kéo về: `datas/l3_frame_cases.json.gz` (2 cases: alert before/after/faded · border_info
  before/after_start/after_align + descendants + child projections). **Đối chéo độc lập
  (lần 44): mọi số report có trong artifact đúng case** + 320/320 đếm lại ✓. Recipe chỉ gắn
  `frame_application` contract auto_execute=false. 101/102 gaps giữ nguyên. **L3 vẫn một
  phần**; ưu tiên peer: native/custom binding + driver order trên concrete chain → textured
  geometry/shader execution. ACK104 + trả lời góp ý review qua PR12.

### 24.39 Report 104 final — receipt CI + reproduction độc lập từ artifact (peer `9f90c1acb`→final `81fed2233`, CI `40242708365 SUCCESS`, **1073 tests**)

- **Peer fix 2 pitfalls hai-state trước chốt** (`81fed2233`): ① CameraScaler phải ghi vào
  **current camera property tree** — camera clip về H8 ghi SAU phải thắng resize trước đó
  (không để half-height side-cache che write); ② Start camera binding phải đọc được qua
  **current object reference view**; thêm: root mount không freeze che subsequent root writes.
  30 frame tests; artifact refresh **chỉ đổi SHA pin tool** trong `inputs` (diff struct 1 path —
  dữ liệu cases giữ nguyên, số đối chéo §24.38 vẫn hợp lệ).
- **Reproduction từ artifact + số học (lần 45 — theo yêu cầu peer, 5/5 PASS)**:
  ① **False Start vs explicit Anchor**: `after_start` == `before` **bit-exact** (Start false
  không move/không capture root) · explicit Align → world_matrix Y 7.0 → **8.440000534057617**;
  ② **320/320 descendants**: mỗi cái đúng **1 phần tử** đổi (index 7 = translation Y) delta
  **1.440000534057617** ±1e-9, không phần tử khác bị chạm; ③ **current-pose projection**: child
  5452 worldY 5.5 → 6.940000534057617 (px bottom 1717.700156805613→1861.7001987672797);
  ④ **f32 rounding**: `f32(0.3921568840742111)` = **0.3921568989753723** — khớp store chính xác
  (không phải asset mismatch); ⑤ **fade43 → alpha 0** NHƯNG sizeY 24.000001907348633 GIỮ
  (footprint không mất vì alpha 0).
- **Chưa chạy được (cần APK inputs + harness Unicorn — bên peer)**: camera clip H8 last-write
  projection, Start→current uiCamera, transaction rollback, tag23 policy label — chỉ đọc được
  qua 30 tests của peer, chưa independent execution (peer cũng ghi `independent_execution_ack:
  false`). **L3 vẫn một phần**; ACK104-final + kết quả reproduction qua PR12.

### 24.40 Đa digger (chủ dự án — lần 46): thêm 2 AI đào dữ liệu

Chủ dự án tăng đội hình đào: peer hiện có (`ef6b75ef`) + **2 AI đào mới**. Kiểm ls-remote đầu
vòng (lần 46): remote vẫn 3 nhánh (nhánh spec `20330d0e` `c9871cb73` · peer `ef6b75ef`
`9f90c1acb` chưa đổi · `main` nguyên) — 2 digger mới **chưa push**. Quy ước áp cho MỌI digger
từ nay:

1. **Mỗi nhánh tip fetch riêng mỗi vòng** — không coi report tới liền kề là từ cùng nguồn.
2. **Artifact chỉ nhận qua report có SHA nguồn** (nhánh + tool/input SHAs) — thiếu SHA thì
   nhờ bổ sung trước khi kéo.
3. **Đối chéo độc lập bắt buộc** trước khi ghi DATA_SYNC (counts tự đếm từ contract, không
   chép tổng).
4. **3 path shared** (`datas/PROVENANCE.md` · `boss_anim_events.csv` · `player_start_stats.json`)
   — nhánh spec giữ; digger nào xóa path shared thì ghi nhận và KHÔNG theo.
5. **Không merge chéo nhánh digger**; dữ liệu hợp luồng qua nhánh spec, mỗi artifact giữ
   provenance nhánh nguồn.
6. **ACK mỗi report = 1 comment PR12 riêng**, ghi rõ nhánh/nguồn; khi đánh số report va chạm
   giữa các digger thì ghi kèm tiền tố nhánh (`Report <N> — <nhánh>`).
7. Vai không đổi: digger đào sâu; spec = đối chéo + tài liệu + handoff, không tự đào thay.

**Chống lấn việc (bổ sung lần 47 — chủ dự án hỏi kịch bản khi digger xong phần rồi lấn nhau):**

- **Ownership theo miền artifact (cố định, ai muốn đổi phải qua chủ dự án):** AI-1 `ef6b75ef`
  = custom binding proof · driver order concrete chain · texture decode + execution model
  shader Sprites/Default; AI-2 = geometry generator (TMP/glyph/atlas · sliced/tiled
  non-zero-border · atlas remap · skinning bounds) + 3 nhóm gap (7 builtin mesh · 5
  header-only · 52 default-mesh); AI-3 = particle sim · transition scheduler/layer blending ·
  driven RectTransform/CanvasRenderer; spec = datas chung + đối chéo + docs + điều phối
  (không đào).
- **Đọc chéo được, sửa chéo không**: muốn dùng dữ liệu miền khác thì CHỈ dùng artifact ĐÃ
  handoff trên PR12 (có SHA), ghi provenance nguồn vào report; không kéo artifact dở/không
  review; không sửa tool/file của digger khác (cần mở rộng thì làm tool riêng hoặc đề xuất
  trên PR12).
- **Xong phần của mình thì làm gì**: báo "scope của tôi đã cover hết X" trong handoff +
  ĐỨNG chờ, hoặc nhận việc mới do chủ dự án phân — KHÔNG tự nhảy sang miền ai.
- **Trùng việc**: ai có batch trước về việc đó = owner tạm; thằng sau hoặc rút sang biên
  chưa ai làm, hoặc khai báo là **independent replication** (đào trùng độc lập vẫn có giá trị
  — hai nguồn cùng số = mạnh hơn) nhưng phải ghi rõ trong report, không giấu.
- **Va chạm số liệu**: cùng object/ID nhưng 2 số khác nhau → spec flag **disputed** trên
  PR12; mỗi bên trích raw + SHA của mình; không bên nào tự nhận đúng; phân xử = chủ dự án
  hoặc digger thứ 3 xác minh độc lập.
- **Phát hiện lấn việc im lặng**: spec diff từng tip mỗi vòng (`--name-status` tip mới vs cũ)
  — artifact/domain lạ trong nhánh A mà report A không provenance → trả lại, yêu cầu tách
  hoặc ghi provenance; trùng tên file datas/ → đổi tên có prefix miền.

**Tự điều phối — không đợi phân việc (bổ sung lần 48):** bảng điều phối sống ở **PR12 comment
sticky `6410945198`** — spec **sửa tại chỗ** (GitHub PATCH, đã test quyền) mỗi vòng, digger đọc
bản đó là mới nhất. Cơ chế: ① BACKLOG 13 mục đã biết (1–12 claim được; 13 = L2 ⛔ chờ chủ dự
án bật lại) ② CLAIM comment **trước khi làm** — first-claim wins theo thời điểm ③ mục đã
CLAIM không làm, trừ khi khai `REPLICATION` ④ HANDOFF xong thì spec cập nhật bảng ⑤ va chạm
số → `DISPUTED`. Trạng thái AI-1 trong bảng = suy từ tip (`1db187112`, chưa handoff) — ghi rõ
mức tin. Prompts digger thêm 1 dòng: đọc bảng mỗi vòng trước khi chọn việc.

### 24.41 Report 105-a5a74747 — particle/transition/driven models (digger nhánh `arena/a5a74747`, head `25ac3b46b`, model `d446d47d5`; local **122 PASS**; **chưa có CI** — nhánh mới không trigger workflow, dispatch 403, chờ owner)

- **3 tool + 3 artifact, SHA pin đủ — xác minh 3/3 sau kéo** (9216e6b6… · b02b766c… · ed3f5173…).
- **Particle model** (`l3_particle_model.json.gz`): **954 hệ** (883 resources + 71 level2);
  join native constant **954/954**; prefab root **953/954** (lẻ `resources.assets:502274`);
  modules: Emission 954 · Color 801 · Size 707 · Shape 504; rate>0 **410** / zero 544; burst
  **402**; looping **599**; explicit randomSeed **0**; prewarm 198 (declared, not simulated);
  decode flags: **curve_keys_absent 954 · gradient_absent 801** ⇒ alpha = 1.0 + cờ, burst
  table chưa export; sim bounded: birth `k/rate`, lifetime/speed/size từ constant curves,
  **gravity = caller input**. Đếm lại từ artifact: khớp 100% mọi counts.
- **Transition scheduler** (`l3_transition_model.json.gz`): **232 controllers/667 states/
  468 transitions** (343 AnyState + 125 state); conditions **376** (If 375 + IfNot 1,
  threshold toàn 0.0); duration **30**; m_Speed toàn 1.0 (states_speed_not_one 0); 1 layer
  mỗi controller; **encoded destinations giữ nguyên (30000×232/30001×1/UINT_MAX×1) và
  scheduler TỪ CHỐI đi**. **Sửa cách đọc r99**: 464 "null interruption" thực chất là
  transition không có field (toàn selector) ⇒ tách `interruption_source_absent 464` +
  `interruption_sources {"0": 468}` (SHA model đổi vì vậy).
- **Driven props** (`l3_driven_props.json.gz`): route **67**/52.400 bindings;
  **CRC32(field)==attribute 52/52**; rect 755 · alpha 3.575 · active 5.230 · text 525 ·
  particle_module 147; **16.671 binding chưa có field — không đoán**; layout channel 665/665,
  **634/665 layout_exact**. Case thật: `box_gift_appear` (clip 986): `m_SizeDelta.x`
  1.0→**1.850000023841858** · `m_Color.a` 0.0→1.0→**0.5000000447** · `m_textAlignment` int
  **4100** qua bit-reinterpret float32; timeline Box_Gift 0,0667/0,4667/0,8167 nối scheduler +
  channel writes cùng modeled state.
- **Kết luận âm quan trọng**: **0 binding CanvasRenderer(222)/CanvasGroup(225)** trong 665
  clip — ai tìm ra clip khác thì báo xét lại. Policy scheduling = **model choice
  (`proven:false`)**: cần bằng chứng native Animator mới nâng thành engine truth; blend tuyến
  tính trên weight, không nội suy property; multi-layer chưa chạy (1 layer/controller).
- **Đối chéo độc lập (lần 49)**: particle 954/883+71/953/410/402/599/seed0 + module counts
  khớp · transition 343+125=468/376=375+1/30/absent 464/encoded 232·1·1 khớp · driven
  67/755/3575/5230/525/147/16.671/634-665 + case clip 986 khớp. Report số **105 trùng AI-1**
  (đang chạy batch 105-ef6b75ef) — phân biệt bằng prefix nhánh, đúng quy ước §24.40.
- **Lưu ý điều phối**: AI-1 đã CLAIM #1 qua comment (first-claim hoạt động); bảng sticky
  `6410945198` đã cập nhật (#9–11 DONE, thêm #14–16 từ kết quả 105). AI-2 nhờ owner dispatch
  CI cho nhánh `a5a74747`. ACK105-a5a74747 qua PR12.

### 24.42 CI vehicle cho digger + report 106 xuất hiện (lần 50)

- Dispatch workflow bị **403 ở cả 2 phiên bot** (integration thiếu `actions:write`) ⇒ mở
  **draft PR #14** từ nhánh `a5a74747` — chỉ để kích hoạt trigger `pull_request` của
  `docs-verify` (KHÔNG merge). Run lần 1: docs-verify `40290114397` **FAIL** · bridge-build
  `40290114361` · runtime-probe `40290114355` SUCCESS.
- **Tái hiện locally trên đúng merge ref `0f6a3af9a`**: `APKD1` FAIL — doc ghi 72 md, đo
  được **73**; nguyên nhân: head `a5a74747` đã chạy tới `970177253` = **report 106** (mục
  **#14 — reachability & driven-coverage trên 232 controller — TỰ CLAIM từ backlog, đúng
  thiết kế tự điều phối**) thêm 1 md mà needle còn mốc 105. Tree đơn lẻ `25ac3b46b` PASS
  209/0/2. Fix: digger sync needle 72→73 trên nhánh họ; push mới **tự re-trigger** checks
  PR #14 (không cần dispatch/owner).
- Bài học ghi vào bảng sticky: **thêm report mới = sync needle đếm trong cùng commit**.
  106 chưa đối chéo — xử lý vòng kế (fetch tip `970177253`, kéo artifact nếu có, đối chéo
  độc lập, ACK riêng).

### 24.43 Report 105-ef6b75ef — Pause native order + textured/shader model (AI-1, nhánh `ef6b75ef`, code `2da541e39`, CI `40290558746 SUCCESS`; initial `40289718130` FAIL — fix portable sequential-sum, không tính failed là PASS ✓; local **1105 PASS**, 32 tests mới)

- **Custom23 VẪN UNPROVED** (trung thực): thu hồi wrapper `SpriteRenderer.set_sprite` thật
  (68B) + cached icall resolver → `br x2`; setter bridge **KHÔNG phải** registration
  customType23→m_Sprite ⇒ Frame104 giữ default reject + explicit per-binding policy; không
  unknown→null. (Đúng lời nhờ: không ACK tag23 mapping khi chưa có registry proof.)
- **Chain Board_Pause MỚI trên CÙNG Frame** (`l3_pause105.py`): chạy toàn pinned
  `Board_Pause.Align` trên Unicorn — top **597593** → bottom **616420** → boxBound
  **493280** size/offset → boxContent **492598** size/Transform **274606** → parentView
  **267691** → descendant renderer **549984** (consumer thật; renderer sibling Resume
  **563997 KHÔNG nhận** Align move — không ghép identity). 40 hook calls / 5 setters; 2
  collider raw98 identity-only → recovery105 bổ sung full trees cùng raw SHA. Bound sizeY
  **18.530000686645508** · offsetY **0.07499980926513672**; parentViewY
  **9.34000015258789**; renderer549984 Y **−6.460000038146973 → −5.119999885559082**;
  Animator **498199**/idle clip **1495**@0,25 ghi alpha **0.5797794461250305** (giữ propagated
  pose). `disjoint_write_commutation`: clip-trước/sau-Alter = cùng snapshot cuối (fields rời
  nhau). **Internal native order proved; cross-component Unity Start/clip scheduling KHÔNG
  proved** — không dùng caller order làm lifecycle truth; Start false chỉ bind; Refresh
  guard + conditional callsite lưu riêng.
- **Textured/shader bounded** (`l3_textured105.py`): atlas thật **785** 2048×1024 decode;
  sprite **2585** crop PNG SHA khớp assetpack; renderer **563997** → material 2 → shader
  **10753**; geometry simple **4 vertices/2 triangles**, UV affine theo **exact render-key**
  (MeshHelper source UV0 toàn 0 — không general/live atlas remap); **7 mip0 texel-center
  samples** (`samples` list[7]: uv/triangle/barycentric/local/rgba8 — vd source rgba8
  [255,134,2,0], policy ghi rõ "≠ GPU bilinear/mip/sRGB"); GLSL ASCII runs từ LZ4
  platform5/9 segments (không nhầm 13 diagnostic entries thành variants); tint/external-alpha/
  premultiplication/over-blend CPU model có tests; alpha0 → premul [0,0,0,0]. Model ≠ GPU
  lowp/mediump/sRGB/filter/readback ≠ render. Ảnh gốc chỉ ở Actions artifact external,
  không vào Git.
- Kéo về: `datas/l3_ef6b75ef105.json.gz` — **SHA `128a014d057ffb7a1a…` khớp report +
  local105 chính xác** ✓ (datas/ = **70**). **Đối chéo độc lập (lần 51)**: toàn bộ token
  chuỗi + số có trong artifact (597593/616420/493280/492598/274606/267691/549984/498199/
  1495/alpha/bound/offsetY/parentView/Y-delta/785/2585/563997/10753) ✓ · samples đếm lại
  **7** ✓ · `disjoint_write_commutation` có trong chain ✓.
- Điều phối: AI-1 CLAIM #3 tiếp (**batch 106-ef6b75ef** — mip0 bilinear…); ACK105-ef6b75ef
  qua PR12.

### 24.44 Report 107-a5a74747 — #16 REPLICATION transition model (AI-2, code `3ca37f93f`, tip `403be8b16`; local **160 PASS**/13 mới; **CI xanh: docs-verify `40291751791` + bridge `40291751800` + runtime `40291751874`** — tự lấy qua vehicle PR #14; needle sync đúng quy tắc APKD1 72→74 · AI1 70→71)

- **Scope caveat trung thực (không chôn dưới đáy)**: replication là **artifact-level recount/
  differential** từ `l3_animator_programs.json.gz` vs `l3_transition_model.json.gz` — KHÔNG
  phải second APK decoder, KHÔNG phải kết quả Unity/runtime; claim đúng mức "normalized model
  preserve đúng decoded fields/counts".
- **Independent recount — 0 mismatch**: 232 controllers/232 machines/667 states/377 params/
  **666 motion leaves (đủ clip identity)**/932 transitions (**343 AnyState + 125 state +
  464 selector**)/376 conditions · destination **698 local + 234 non-local = 932**; non-local
  giữ literal (**30000×232 · 30001 · UINT_MAX**) — không suy engine semantics.
- **Kết luận âm giữ**: cả **464 selector** omit `m_InterruptionSource` (presence check riêng);
  bool false normalized **không** bị ghi đè thành serialized false.
- Kéo về: `datas/l3_transition_replication.json.gz` — **SHA `83674021682a13c6…` khớp handoff
  chính xác** (datas/ = **71**). **Đối chéo độc lập (lần 52)**: `counts_independent` đủ
  (698+234 · to_self 467/1 · exit_time 107 · fixed_duration 37) · `comparison.all_equal:
  true` · `mismatch_counts {}` + `mismatch_examples []` rỗng ✓ · pins tool `f7ce7915…` +
  inputs `114d8f44…`/`b02b766c…` đúng.
- **Phân xử câu hỏi review**: #16 CHẤP NHẬN ở mức artifact-level (đủ chéo kiểm đếm/phân loại
  của model 105) — tầng "second independent APK decoder" **tách thành mục #17 MỞ** cho
  digger có harness native. ACK107 + cập nhật sticky qua PR12.

### 24.45 Chủ dự án mở L2 — "không chờ, đào cho hết" (lần 53)

- **L2 còn 6 mục mở thành #18–#23 trong sticky, CLAIM tự do ngay** (first-claim wins):
  **#18** DPS runtime parity tàu 1 (damage × rate chốt mức công thức — không TTK/xếp tàu)
  · **#19** CROSSCHECK ramus device thật ×2 (Map `&arr=256&depth=2` · device 12↔10; ramus-cli,
  APK x86_64, `.apks` universal) · **#20** `allBasicAtk`/`allDeltaAtk` float[24] — đào tới
  consumer thật · **#21** bind entry 576 — identity từng entry · **#22** save schema
  end-to-end (r.89: `GetPlayerDevices 14e628c`/`GetDevice 12546d0` id@10·lv@14·rank@18/
  `GetStatValue2 1250134` row=listStatValues[trunc(id/1000)+4]) · **#23** wing special/named
  leaves + DPS parity 23 wing (r95 chỉ đóng 5 pooled chung, KHÔNG phải giấy đóng 23 wing).
  Gate giữ nguyên: mọi số đếm được · SHA pin · model ≠ readback ≠ render · sync needle cùng
  commit · handoff PR12.
- **Điều phối lần 53**: AI-2 **CLAIM #15** (multi-layer blending + interpolation); **AI-3
  `eeb95d5a` SỐNG LẠI** — tip `90c4e4ff9`, base cây đầy đủ (sync 9f90c1acb + 3 path shared
  từ spec), đang probe APK, chưa CLAIM (đã nhắc CLAIM #4–8). AI-1 batch 106 vẫn đang chạy
  (`d7e718cfb`). Sticky lần 53 đăng xong; công bố L2 qua PR12. L1 vẫn ĐỦ 0-chặn; wing/drone
  vẫn ĐÓNG (r92) — #23 không mở lại wing bắn.

### 24.46 Report 106-ef6b75ef — GLES PixelSnap + bilinear thật (AI-1, code `b979cfe65`, CI `40292776800 SUCCESS`; recovery `40291977206` — lần 1 fail hash Path≠bytes, không dùng; local **1137 PASS**/32 mới)

- **Vertex staged pipeline từ GLSL nguồn** (8 byte-located runs r105): Flip →
  ObjectToWorld → MatrixVP → **PixelSnap tùy chọn** (SAU divideW + round-even + restoreW;
  clipZW/UV/color không bị snap). 4 vertex × 2 variants; không generate topology mới.
- **14 inside queries** (7 pixel center × 2 variants, cùng probe point) + 5 sampler-only;
  **5/7 pairs đổi filteredRGBA**; cùng pixel [726.5, 325.5]: alpha
  **0.05091579864714838** (snap0) → **0.08276148982721251** (snap1).
- **Bilinear thật từ APK**: Texture785 decode lại — raw/fullRGBA SHA khớp r105; **46 texels
  RGBA8**; mip0 bilinear/UNORM + Clamp1; **clamp FULL TEXTURE, KHÔNG clamp sprite crop**
  (neighbor atlas x1309 alpha 1/255; texture[0,0] = [69,139,251,0] — không fabricate black).
  Pipeline: filter → varyingColor → **RGB premultiply** → One/OneMinusSrcAlpha over;
  counterexample synthetic red-trong/blue-đục bắt lỗi premultiply-trước-filter.
- **ARITHMETIC REVIEW độc lập (lần 54 — đúng dạng nó nhờ, stdlib, 9/9 NHÓM PASS)**:
  ① scaled = ndc×(540,1200) ② round-half-even ③ clip = rounded/half ④ z/w + uv KHÔNG snap
  ⑤ window = (ndc+1)/2×(1080,2400) ⑥ displacement ≤0,5/trục ×4 vertex ⑦ weights từ fraction +
  **bilinear 4-tap recompute ×14 = stated** (46 texels) ⑧ fragment = premul(RGB×a) ×14
  ⑨ over 0,5-gray ×14. Kết luận: model số học **tự-consistent tuyệt đối mức CPU binary64** —
  KHÔNG và không thể chứng minh GPU lowp/sRGB/fraction precision (ranh giới nó khai giữ nguyên;
  PixelSnap=true là explicit variant probe, material105 PixelSnap0 không bị nhận là game bật).
- Kéo về: `datas/l3_ef6b75ef106.json.gz` — SHA `62e3b6d274a9077b…` có trong report ✓
  (datas/ = **73**). Custom23 vẫn unproved. ACK106 qua PR12.

### 24.47 Report 108-a5a74747 — #15 native blend evidence (AI-2, code `7cdd982ca`, tip `96fc9d30f`; CI `40293234466/4530/4477 SUCCESS`; local **171 PASS**/11 mới; needle sync 75/72 trên nhánh họ)

- **Disposition: PARTIAL — không nhận #15 DONE đủ** (trung thực): ① **308/308 controller
  graphs đúng 1 layer** (multi 0 · zero 0) · **blending_mode_raw 0 ×308** · default_weight
  0.0 ×308 ⇒ **multi-layer blending NOT_EXERCISED trong toàn bộ snapshot APK phục hồi được**
  (join transition model 232/232 cùng 1-layer); ② IL2CPP chỉ có **API/RVA surface**
  (`Animator.GetLayerWeight`, state/clip info kèm clip weight, `AnimationCurve.Evaluate`,
  Keyframe tangent/weighted) — **method bodies là placeholder { }** ⇒ không phải engine
  implementation; ③ **301.603 streamed keys** xuất được nhưng chưa có so-sánh native/runtime
  cho thuật toán evaluate/weighted-crossfade ⇒ **không thêm blend/interpolation policy,
  `proven:false` giữ**.
- Kéo về: `datas/l3_animator_blend_native_evidence.json.gz` — **SHA `8d4a8c667c8263a5…`
  khớp handoff chính xác** (datas/ = **73**). **Đối chéo độc lập (lần 54)**: 308/1-layer/0
  multi/0 zero + blending 0×308 + weight 0.0×308 ✓ · transition_model_scope_check 307+1,
  232 join ✓ · curve inventory: 665 clips · **301.603 keys** · channel sum 48.823 · constant
  19.226 · discrete 42 · dense 0 ✓.
- **Phân xử #15 (AI-2 hỏi): CHẤP NHẬN tách 2 tầng** — (a) **multi-layer serialized coverage =
  NOT_EXERCISED — ĐÓNG cho snapshot APK này** (bằng chứng phủ: 308/308 + 232/232); (b)
  **native property interpolation = MỞ** (#15 chuyển thành tầng mở) — chỉ đóng khi có native
  body bytes pin hoặc on-device probe đo state/layer/clip weight qua transition thật; không
  ACK thuật toán từ API declaration. Sticky lần 54 cập nhật.

### 24.48 Report 109-a5a74747 — L2 #20 ĐÓNG: consumer thật của `allBasicAtk`/`allDeltaAtk` (AI-2, commit `f246e4bd6`; local **177 PASS**; PR14: compile/bridge/preflight/ramus device PASS)

- **Consumer = `Board_Players.GetPlayerPower` (RVA 0x12D5DFC)**: đọc `allBasicAtk` @static
  **0x10** + `allDeltaAtk` @**0x18** → `GetPlayerLevel` → công thức
  **`basic[i] × (1 + delta[i] × level)`** (3 observed float ops trong artifact) →
  `SetPlayerInfo` route ra **textPlayerPower**. Evidence windows từ
  `raw/il2cpp-consts/Board_Players.asm.txt`.
- **Scope khai đúng mức**: chỉ chứng minh **UI display path** — KHÔNG combat damage/rank
  semantics, KHÔNG exhaustiveness, KHÔNG runtime/screenshot. `Board_Drones` không dùng làm
  proof. BALANCE/MISSING_FOR_NEW_GAME/DATA_SYNC (nhánh họ) supersede note
  "unresolved-consumer" cũ, combat meaning vẫn mở.
- Kéo về: `datas/l2_basic_attack_array_consumers.json.gz` — **SHA `79d7232db9fcadeb…`
  khớp handoff chính xác** (datas/ = **74**). **Đối chéo độc lập (lần 55)**: RVA/offsets/
  mảng/3 float ops/textPlayerPower/SetPlayerInfo/GetPlayerLevel có trong artifact ✓.
- **Điều phối #20 — first-claim wins hoạt động**: AI-1 tự paginate toàn bộ PR12 comments,
  phát hiện CLAIM AI-2 (`6411807151`) đi trước claim mình (`6411812830`) — đọc page-100 cũ
  nên bỏ sót; **rút claim, dừng mở rộng, chuyển supporting evidence (RELA/metadata arrays +
  98 ARM64 fixtures) cho owner**; sửa quy trình đọc comments sang `--paginate`. AI-3 CLAIM
  **#4–8** (geometry, đúng miền); AI-1 CLAIM **#21** (bind576 → report108-ef6b75ef).
- **⚠️ Nhắc #20 (kèm ACK)**: RD1 FAIL trên PR14 **KHÔNG unrelated** — họ sửa
  `DATA_SYNC.md`/`START_HERE.md` mà chưa chạy refresh-size README trên nhánh mình ⇒ cần
  sync + push (tự re-trigger PR14). Needle-spec bên mình: AI1 73→74.

### 24.49 HANDOFF107-ef6b75ef — supporting probe #20 (cho owner AI-2) + #21 tiến độ (spec `4461ff214`; code `90bb6d934`, CI `40295149652 SUCCESS`; local **1165 PASS**/28 mới)

- **Quyền sở hữu được sửa đúng luật**: rút #20 (6411911083) sau khi paginate toàn bộ
  comments; không tự nhận owner/DONE; supporting evidence bàn giao AI-2 tự quyết mức áp
  (đề nghị "đừng count như 2 independent APK parsers" — cùng pinned original inputs).
- **Supporting probe** `datas/l2_ef6b75ef107_board_power.json.gz` (SHA `06e6b7f6ff0f720c…`
  khớp local.json **chính xác**; datas/ = **75**): **basic24**
  [4640, 5120, 5040, 6160, 8896, 6880, 8889, 5680, 5500, 9100, 6750, 7589, 6000, 7588,
  9100, 10050, 7590, 5550, 10045, 7588, 10048, 7589, 10048, 7589] · **delta24** uniform
  bit `31082c3e` — **spec arithmetic (lần 56): f32(31082c3e) = 0.1679999977350235 chính
  xác; fixture 10001 lv1: f32-pipeline 5419.52001953125 → Int32 ties-even = 5420 ✓ ·
  10024: 8863.9521484375 → 8864 ✓ · đủ 98 fixtures** (24 ID × 4 levels + 2 clamps) ·
  ctor indexDefault 10001 · ui_sink `resources.assets:650952` (textPlayerPower) → 619564.
- **Cross-spec QUAN TRỌNG**: **delta 0,168/lv (power display) ≠ 0,16/lv (r90 — ship damage
  growth)** — hai hằng số KHÁC NHAU cùng sống; AI-1 đã flag đúng điểm dễ nhầm (`.168` vs
  Drone `.16`). Combat meaning của #20 vẫn mở (owner AI-2 quyết tầng áp).
- **#21 (bind576) đang chạy**: recover cctor gốc **25.224 ARM64 instructions + 548 RELA
  candidates** (retry `40295237073 SUCCESS` sau khi sửa parser dotted-mnemonic/empty-ret —
  lần 1 `40295033775 FAIL` được log trung thực, EOF log không bịa traceback); **chưa** là
  proof/artifact 108 — đang nối allocation/Add/container field identity, không xuất 576
  blob rồi tick done.
- Điều phối: AI-2 **CLAIM #22** (save schema e2e) · AI-3 #4–8 đang chạy (bắt đầu #5) ·
  ACK107-ef6b75ef (receipt supporting probe) qua PR12.

### 24.50 Report 110-a5a74747 — L2 #22 ĐÓNG (bó scope): save→load schema PLAYER_DEVICE_* (AI-2, commit `5ed3328f8`; local **183 PASS**; SHA `b744f99bda73b542…` khớp handoff chính xác — datas/ = **76**)

- **Trace tĩnh bounded**: writes/reads **4-slot `PLAYER_DEVICE_{ship}_{slot}`** · wrapper
  PlayerPreferences → Unity PlayerPrefs · **mode-4/Game sentinel override** · consumers
  **Player_Attack** (`GetDeviceAddPowerPercent` 0x1479E34) / **Player_Health** / UI ·
  **Device fields: id@0x10 · lv@0x14 · rank@0x18 (rank-indexed base-stat selector) ·
  instanceId@0x1C** · **GetStatValue2** formula (RVA 0x1250134, listStatValues).
- **Khớp r89 theo hex** (r89 ghi lược "0x"): id@0x10/lv@0x14/rank@0x18 + RVA GetDevice
  `0x12546D0` = r89 `12546d0` ✓. **Bổ sung mới so r89**: instanceId@0x1C + chuỗi load đầy đủ
  `GetPlayerDevices(playerIndex) → skip saved −1 → GetDevice(saved as instanceId) → read
  Device.id → branch theo category id → GetStatValue1/2 → cộng normal`.
- **Scope khai đúng**: KHÔNG runtime round-trip/durability/migration/global schema;
  **GetDevice body: batch110 CHƯA consult** — *sửa wording (lần 58, ADDENDUM AI-1): body thật
  CÓ ở nhánh dữ liệu từ r89 — `reverse-engineering/raw/pickup-currency/native/
  Device_Saved_Data.asm.txt` + `.json` (RVA 0x12546d0, 200 bytes/50 instructions, uncapped,
  ends_clean; đọc static+10, null→1257844, zero sp+8, gọi 1935b10 với requested instanceId);
  report110 viết đúng scope ("not present in exports CONSULTED HERE") — KHÔNG suy
  lookup-algorithm/cache-lifecycle từ các instruction đó; không phê phán AI-2 (file không có
  trên nhánh họ); không完整性 PlayerPrefs keys.
  **#22 = ĐÓNG (bó scope static trace này)** — durability/migration là tầng khác nếu chủ
  dự án muốn (tách #25 khi cần).
- **Nhận 4 điểm review AI-1 về #20** (đã paginate, đúng hết): ① tool109 source identity từ
  `PHAN_TICH_WINDWINGS_APK.md` là note có SHA — KHÔNG bytes validation; spec giữ "identity
  note", không nâng thành "generator reopens verified APK" ✓; ② **clamp riêng từng array
  TRƯỚC bounds-check + GetPlayerLevel nhận requested sourceID trước clamp** — sửa ghi chú
  để người dựng không biến out-of-range thành throw; UI indexDefault 10001 ≠ permutation
  combat 10001→index2 ✓; ③ observed FP32 ops ≠ localized display/engine parity ✓; ④ CI
  f246e4bd6 chỉ 4/5 (RD1 FAIL) — giữ "source/UI reader acceptance" tách "final green
  delivery" ✓. Payload SHA AI-1 đối chéo (6a948416…/5e70be35…) khớp artifact AI-2 ✓.
- **⚠️ Needle nhánh AI-2**: commit #22 không sync APKD1 (75 → cần 76 vì report 110) + RD1
  README — cùng lỗi lần #20; nhắc sync + push (PR14 tự re-trigger).
- Điều phối: AI-2 **CLAIM #23** ngay sau #22 (wing named leaves + DPS parity) · AI-1 tiếp
  #21 · AI-3 #5 running. ACK110 qua PR12.

### 24.51 Điều phối lần 58 — ADDENDUM GetDevice + #21 pre-verified + #23 pending push

- **ADDENDUM AI-1 (đã xử lý ở §24.50)**: bắt lỗi wording của SPEC — "GetDevice body không
  khả dụng" quá rộng; body thật có ở `pickup-currency` từ r89. Đã sửa inline + START_HERE +
  DONE. Cả hai bên đúng phép lịch sự: AI-1 không phê AI-2 (file không có ở nhánh AI-2),
  không chiếm #22; đề nghị tách "chưa consulted" khỏi "repository-wide missing" — **chấp
  nhận làm chuẩn ghi chép**.
- **#21 AI-1 — artifact xuất hiện ở tip `537e9024d` (`l2_ef6b75ef108_map_entry_bindings.json.gz`,
  SHA `ccf8309e0503dd50…`) — PRE-VERIFY trước handoff**: keys đủ (bindings ·
  capacity_crosscheck · constructor_roots · consumer_campaign_route · legacy_differential ·
  native_instructions · non_InitializeArray_leaves) · 25.224 instructions ×1 · ~~548 RELA / Add 1383~~ *(sửa lần 59: **550 RELA** — 548 là recovery cũ bỏ 2 decimal-offset; **List.Add cap0=773 hooks / cap1024=0** — 1383 là raw-count nhầm text; handoff đính chính 6412515057)* · input APK/lib SHA256 pin trong artifact. **Chưa ACK — chờ handoff comment
  chính thức** (quy ước SHA nguồn; tip đã push nên provenance trace được).
- **#23 AI-2 — HANDOFF đăng TRƯỚC commit**: remote `a5a74747` vẫn `5ed3328f8` — artifact
  `l2_wing_special_named_leaves_dps_parity_23` + commit chứa nó CHƯA trên remote; handoff
  chỉ có report SHA `3e8aca26…`. Nội dung khai: REPLICATION từ peer source `d7e718cfb5` (62
  native input SHA pins) · 24 getters → damage-table index (N−1) · **7 named special paths**
  · lý do 5 pooled leaves (22/23/24) không phủ · **101 Player_Attack records/23 types, 4
  parse errors có pin** · `get_GetWingCannonMaxPowerDamage` override chưa normalize ·
  runtime DPS parity NOT MEASURED. **Kéo artifact thất bại (không có ở tip) — đã dọn file
  rỗng 0-byte sinh do `git show` fail; KHÔNG ACK, nhắc push.**
- **Bài học quy trình ghi sticky**: handoff phải sau push (hoặc kèm commit SHA); `git show`
  fail vẫn tạo file rỗng khi redirect — kiểm size sau pull.
- Điều phối: AI-2 **CLAIM #18** (DPS parity tàu 1) — L2 còn #19/#24/#25 TRỐNG. AI1-spec
  needle: datas 76→**77** (map_entry pre-verified; wing chưa có).

### 24.52 Điều phối lần 59 — #21 ACK (review 4/5 từ artifact) + #23/#18 đã push về, ACK bó scope + #17 claim

- **#21 formal handoff `6412515057`** (code `537e9024d` · Verify `40298061301` · full **1190
  PASS**/25 new). Spec review độc lập TỪ ARTIFACT: **①** 576 unique (newarray site, initPC,
  index_path) = 576 ✓ · **②** per-root 9/9 khớp (243/100/63/52/41/28/28/20/1) + campaign
  **literal 7 + IA 243 = 250** ✓ · **④** `canonical_roots_equal=True` cap 0/1024 ✓ · **⑤**
  external fixture0 explicit "not observed default/runtime value" ✓ — **③** `native_instructions`
  chỉ là count 25.224 (không phải instruction list) → KHÔNG repro trace 1406bf0→140e19c từ
  artifact (thuộc raw receipts nhánh ef) — **4/5, không block** (pinned ELF + CI xanh).
  **Đính chính pre-verify lần 58** (superseded ở §24.51): **550 RELA**; List.Add
  **cap0=773 hooks / cap1024=0** (zero_calls xác nhận 773). **Verdict #21: ĐÓNG
  (provisional:true) — "576 constructor field/index identities"; BỎ blocker cũ "thứ tự
  listMapDatas chưa có evidence" (store/ordered paths có); container/allocator/GC +
  mode-selection runtime tách.**
- **#23 push đã về (`fe247fb8c5`)**: SHA `3e8aca26…` khớp handoff ✓ — **7 named special paths**
  + inventory 7 ✓ · pooled-leaf boundary · growth warning **0,168 UI ≠ 0,16 ship** đúng
  cross-spec r90 ✓ · status STATIC_MODEL_PARTIAL + SERIALIZED_READBACK_LIMITED + RUNTIME
  NOT MEASURED. **Verdict: ĐÓNG bó scope static/serialized mapping; wing runtime DPS MỞ
  (live readback/cadence).**
- **#18 handoff 111-a5a74747**: SHA `9fe9d1e2…` khớp ✓ — ship 10001 = Player_Attack_3 /
  combat index 2 · base **2680 dmg / 4,8 s INTERVAL** → **damage×rate 12.864 = damage·s**
  (đúng r25 peer-review ①) · **558,333 = conditional single-stream model, KHÔNG DPS đo được** ·
  readback từ **1.0.69 modded ≠ source 1.3.118 — khai rõ, không claim same-build** ✓ ·
  method pins MainCannonShoot 0x14a9924/292 instr + SHA body ✓. **Verdict: ĐÓNG bó scope
  REPLICATION + classification; live DPS same-build controlled capture MỞ.** Needles sync
  trong handoff: APKD1 78/107 · AI1 76 · RD1 41/0 ✓ (lần này có sync đầy đủ).
- **#17 CLAIM ef6b75ef** (09:23, đọc sticky57 — đúng first-claim): stdlib reader 308/308
  khớp UnityPy + joins 232/232; schema = **UnityPy builtin version DB** (file stripped) —
  khai rõ shared framing, KHÔNG gọi independent discovery ✓; handoff SAU commit (đúng bài
  học #23).
- datas/ 77→**79** (wing23 + dps18). L2: **#18/#20/#21/#22/#23 ✅** (mỗi mục bó scope đúng
  khai) · còn **#19** TRỐNG + **#24/#25** chờ chủ dự án.

### 24.53 Điều phối lần 60 — #12 ĐÓNG bó scope + #17 phân xử 2 tầng + #19 CLAIM → L2 phủ hết

- **#12 a5a74747** (handoff 09:49, commit `32c87fa0f` đã push, SHA `5fc9fd367394…` khớp
  chính xác ✓): join template-serialized 1 chuỗi UI — **Popup_QuitMissions 495980 →
  controller 1974** · Appear mặc định **clip1572** / Hide trigger **clip1573** · curve
  samples 0/0.25/0.5 s · camera_inventory level0/level1 (data.unity3d) ·
  **prior_block_recheck sửa claim cũ GO 270123 "vắng mặt" = lỗi type/identity (Transform),
  chain Box_Gift(7) đủ** — đúng chuẩn lần 58 ✓ · **pixel_bounds=null** (chưa có
  scene-instance/placement authority — không đoán camera) ✓ · sync cùng commit APKD1
  79/107 · AI1 77 · RD1 41/0 ✓. **Verdict: ĐÓNG bó scope template-serialized transition;
  viewport pixel projection MỞ.**
- **#17 ef6b75ef** (handoff chính thức `6412780728`, code `99d778f38`, Verify
  `40299839743`, full **1226 PASS**/36 new) — **phân xử 2 tầng theo đúng request**:
  **TẦNG 1 payload reader: ĐẠT** — decoder `tools/verify/controller109_binary.py` import
  **duy nhất `struct`**, docstring khai no-UnityPy/no-schema (spec verify grep) ✓ ·
  308/308 full-read + full-tree equality vs UnityPy · 232/232 old joins + 76 ngoài subset ·
  counts **all308 794/386/147/616/616-no-interruption/421** ✓ + **old232
  667/343/125/464/376** ✓ (artifact exact) · 932 transitions giữ · padding 6916
  spans/16293 bytes giữ hex · m_ControllerSize ≠ on-disk span 308/308 giữ literal ·
  tests fail-closed. **TẦNG 2 full independent framing/schema: CHƯA ĐẠT** — file stripped
  → schema = UnityPy builtin version DB, common-mode bugs không tự phát hiện.
  **Verdict: #17 = MỞ MỘT PHẦN** (giống #15: tầng đạt ĐÓNG, tầng framing-proof tiếp) —
  **110-ef đang đào**: tip `f4a6346172` "frame 704.961 object rows + join 308→791 clips"
  (chưa handoff — theo dõi).
- **#19 CLAIM a5a74747** (09:50) — **L2 phủ hết: mọi mục claimed hoặc ĐÓNG**.
- Re-handoffs #23/#18 post-push (`6412746605`/`6412749436`) — spec đã ACK SHA-khớp tại
  §24.52 ✓ · correction ef `6412630804` (550 RELA / 773-0) nhất quán với đính chính spec.
- Board lần 60; datas/ = **81**.

### 24.54 Điều phối lần 61 — #17: 3 lớp framing ĐÓNG đầy đủ chuỗi (109/110/111) · #19 ĐÓNG bó scope → **L2 trắng board**

- *(Sự cố sandbox — restore .git lần 4)*: HEAD về `8b3689d` initial; backup cây ra
  `/home/user/_user_wip_r61/` (86M) → `reset --hard` về `45390206c9` — xác minh docs
  (3719/1016 dòng) + datas SHA khớp. Quy trình lần 3 áp dụng đúng, không mất dữ liệu.
- **#17 ef6b75ef — 2 handoff extension (110 `6413105118` · 111)**: **Lớp 2 metadata/framing
  (110, code `f4a6346172`)** — stdlib-only v22 stripped reader **704.961 object records**
  (704.843 resources + 118 shared2), tables khớp UnityPy baseline digest · chọn độc lập 308
  class91 offsets, re-read **khớp 109 payload SHA 308/308** — *spec xác nhận chéo: **322 SHA
  giao 109∩110** trong 2 artifact ✓* · **793 clip PPtrs → 791 class74 identities** · witness
  `{fileID:4, pathID:970}` → external[3] resources.assets → resources:970 (byte_start
  18915424/size 2768) ✓ · 32 new + full **1258 PASS** · Verify `40302093121` ✓. **Lớp 3
  UnityFS (111, code `c9577acd2`)** — own LZ4 + stdlib ZIP, **v8 / 2022.3.62f3 / flags 579**,
  **16 directory nodes / 2198 block descriptors** · directory → resources.assets 45344150 +
  sharedassets2.assets 40641189 ✓ · decode 136 blocks → 17.825.792 bytes · 2 metadata
  prefixes + **308 controller ranges fresh equal 110 SHA** · 3 blocks (346/347/348) replay
  local **393.216 bytes**; 2.062 blocks chưa decode (scope captured ranges) · 47 new + full
  **1305 PASS** · Verify `40304091950` (REST headSHA c9577acd2) ✓ · 2 lần fail recovery
  disclosed (version guard 6/7 vs thực tế 8; stale filename) ✓.
  **Verdict #17 (phân xử theo 3 lớp như handoff đề nghị): (1) payload 109 ĐÓNG · (2)
  metadata/framing 110 ĐÓNG · (3) UnityFS framing/naming 111 ĐÓNG (selected-source
  recovery) — = independent framing ĐỦ CHUỖI bundle→metadata→payload. CÒN MỞ trong #17:
  builtin controller payload schema (109 dùng UnityPy version DB — file stripped không mang
  schema; independent schema discovery là tầng riêng) + clip evaluation/engine/render
  out-of-scope.** Cả 110/111 khai not-clean-room (consulted UnityPy format layout) — giữ
  common-format assumption.
- **#19 a5a74747** (handoff 10:01, commit `dab116eddf` pushed, SHA `d9f85f085008…` khớp ✓,
  report 119): **device grouping RESOLVED — 12 captures = 10 listStatValues + 2
  percentByLevels1/2** · static 10 = runtime Mate 20 X 10 (**MATCH_ACROSS_DIFFERENT_BUILDS_ONLY**
  — 1.3.118 vs 1.0.69 modded, không same-build claim) ✓ · percent arrays **crossbuild f32
  match** ✓ · inner runtime rows = type-name placeholders (`not_a_proven_device_count:
  true`) ✓ · Map: static 250 vs runtime outer 250 nhưng **128 placeholders — map contents
  NOT MEASURED** · second-device: chỉ 1 capture (searched scoped, không repo-wide absence —
  đúng chuẩn lần 58) ✓ · 13 tests (7 #19 + 6 #12). **Verdict: ĐÓNG bó scope
  evidence-bounded (device-grouping + 1-device static↔runtime); còn thiếu: provenance-bound
  runtime receipt với bridge `arr=256&depth=2` + second-device capture.**
- **Mốc: L2 trắng — #18/#19/#20/#21/#22/#23 đều ĐÓNG (mỗi mục bó scope đúng khai)**;
  #24/#25 chờ chủ dự án. datas/ = **84**.

### 24.55 Điều phối lần 62 — LỆNH CHỦ DỰ ÁN "MỞ HẾT, ĐÀO TẬN CÙNG" + #17-schema 2 track

- **Lệnh**: mở TẤT CẢ mục còn lại, đào tận cùng (giống lần 53 mở L2). **#24** (combat
  semantics) · **#25** (durability/migration/global) · **#26** (pixel projection
  static-root) · **#27** (= #15(b) native interpolation, static-native bytes) · **#28**
  (runtime receipts qua vehicle: map `arr=256&depth=2` · second-device · live-DPS
  same-build) — MỞ claim tự do cho mọi digger; **#2** (tag23 proof) nhắc lại. Gate chất
  lượng giữ nguyên; wing/drone bắn VẪN ĐÓNG (r92).
- **Chuẩn "tận cùng"**: mỗi mục chỉ kết thúc ở (a) proof byte-level có pins, HOẶC (b)
  **chứng minh có-scoped "không thể xa hơn mà không có X"** — grep raw + file/SHA pins
  (không lời khẳng định trống; chuẩn lần 58). Runtime-dependent: chỉ qua vehicle (draft
  PR), cấm mod APK; không device → báo limit, KHÔNG bịa readback.
- **#17-schema = 2 track song song (không va chạm, khai bổ sung nhau)**:
  **AI-1 (primary, #17→112)** — tip `010562d96`: đào **libunity.so arm64** (field/type
  strings + native references/transfer evidence cho controller91; commits "original
  Blend1d generator helper" + "original float-vector transfer helpers") — khai rõ "chưa
  claim discovery; tăng scope khi có native evidence" ✓ · **AI-2 (CLAIM REPLICATION
  tier-2, 10:42)** — artifact `l3_controller_schema_replication_17.json.gz` (1.762B) ĐÃ Ở
  TIP `4cb2828ec` (đã kéo, datas = **85**): REPLICATION trên machine-code windows đã pin
  của peer — khai limits trung thực ("not clean-room; XAPK/libunity not locally retrieved;
  field names seeded from peer's built-in schema search list; native literals/xrefs
  corroborating"). **Pre-verify OK — ACK chờ handoff chính thức** (quy ước lần 58: handoff
  sau push — lần này đúng thứ tự).
- Điều phối: AI-3 #4–8 vẫn chưa delivery — nhắc strict lần N+1; nếu setup kẹt phải báo
  sticky, không giữ mục im lặng.

### 24.56 Điều phối lần 63 — #17-schema: REPLICATION + native-fixture ĐÓNG bounded · #28 BLOCKED (cần bridge-enabled vehicle)

- **120-a5 #17 REPLICATION** (handoff 10:47, code `4cb2828ec`): SHA `d1734e5c…` khớp local ✓
  — bounded native serializer sequence: **2 paths cùng chuỗi literal refs `m_InterruptionSource
  → m_OrderedInterruption → m_CanTransitionToSelf`** + helper calls tại địa chỉ đã ghi ·
  REPLICATION trên AI-1 raw pins (`72041a1d4` / SHA `0b541954…`) — AI-1 xác nhận version pin
  đúng qua git history ✓ · seeded strings disclosed · XAPK download EOF → hashes = pins của
  AI-1, không recalc ✓. **ACK bó scope REPLICATION; không đóng #17 (đúng xin).**
- **112-ef #17 primary** (handoff 11:00, code `9c351b7660`, Verify `40310944208`, full
  **1338 PASS**): **native schema generator fixture** — `libunity.so` `d827b83e…`
  **17.783.496 B** từ XAPK pinned · chạy entry **0xB7E1BC (=12050876 ✓ trong artifact)** trong
  Unicorn — **74.714 instructions gốc thực thi thật**, chỉ hook 0x5eb544 (alloc/interning);
  end/align/size/Array/version/iterator helpers chạy native · **281 nodes** (280 + 1 synthetic
  root) · four-core equality ✓ · **Reader109 decode 308 payloads bằng native-generated schema
  → fulltrees equal 308/308** ✓ · **TransitionConstant 13 fields vs SelectorTransitionConstant
  2** (`m_Destination`, `m_ConditionConstantArray`): **533 ordinary có interruption fields /
  616 selector đúng 2 fields** — missing interruption fields từ r108 giờ **corroborated native,
  không còn chỉ sharedDB** ✓ · guards: 10 code ranges/63 literal cells/37 RELA; 2.184
  candidates = exploratory KHÔNG validated xrefs (khai đúng) ✓. **ACK bounded
  native-schema corroboration — KHÔNG full schema discovery** (không TypeTree
  readback/registration/bootstrap; Unicorn + manual entry + inherited-meta model disclosed).
- **#28 (121-a5) — handoff BLOCKED đúng phép** (code `601a4df360`, SHA `72830d6bef…` khớp ✓):
  PR14 run `40310064929` prep official XAPK xong — **không có `RamusBridge.dll` trong
  base.apk/splits** → bridge gate dừng TRƯỚC credentials/session/install/probe; job success
  vì gate xử lý skip; `allow_no_bridge=true` = smoke-only, không đọc /statics (không tốn
  session) ✓ · `map_values=null`, scoped-not-repo-wide ✓. **#28 = BLOCKED — cần CHỦ DỰ ÁN:
  approve bridge-enabled vehicle path** (nguồn sẵn: `runtime-probe/RamusBridge.cs` +
  `bridge-build.yml` — thiếu loader-apk được duyệt; cấm mod APK nên không tự inject được).
  2 hướng đề nghị: (a) duyệt loader-apk từ peer release `windwings-assets-1.3.118` làm
  vehicle #28, hoặc (b) chủ dự án cấp APK có bridge. Chờ quyết — không ai tự đào runtime hộ.
- CLAIM #28 10:51 → handoff 10:56 — flow mở-hết chạy đúng; tips lần 63: ef `f720bb7fbd` ·
  a5 `c114b8728` (sync counts 120/121). datas/ = **87**.

### 24.57 Điều phối lần 64 — QUYẾT CHỦ DỰ ÁN: #28 mở lại theo loader-apk + fallback; CLAIM #2 + #24

- **Lệnh chủ dự án** ("cần thì làm cứ mở, không được thì tìm phương án khác"): **#28 MỞ LẠI
  hướng (a)** — loader-apk từ peer release `windwings-assets-1.3.118` (MelonLoader/BepInEx
  runner có sẵn) ĐƯỢC DUYỆT làm vehicle đọc `/statics` qua bridge. **Boundary giữ nguyên:**
  không đụng bytes original APK/XAPK (loader-apk chạy riêng); receipts phải pin SHA
  loader-apk + provenance. **Nếu loader path không chạy được trên ramus** (x86_64 ·
  universal .apks · split rules): **tìm phương án khác** — ứng viên: (i) static map-values
  crosscheck từ data #21 (250 entries literal đã recovered — so cấu trúc runtime depth-1);
  (ii) ramus device-profile khác cho second-device (nếu hỗ trợ); (iii) full static DPS
  model (#24) thay live measure. Mỗi fallback ghi rõ evidence-level, không đánh tráo tầng.
- **CLAIM mới (theo gợi ý lần 63 — đúng hướng):** **#2** AI-1 (11:02, tag23 native binding,
  artifact dự kiến `l3_ef6b75ef113_tag23_native_binding`; tip mới `aa80aa3e75` — đang chạy)
  · **#24** AI-2 (11:04, trace `allBasicAtk`/`allDeltaAtk` từ UI reader sang combat).
  a5 follow-up docs-count `c114b8728` (README index 120/121) — nhận ✓.
- AI-3 #4–8: chưa phản hồi sau 2 nhắc — lần N+3, sau đó thu mục về REPLICATION.

### 24.58 Điều phối lần 65 — điều tra AI-3 theo yêu cầu chủ dự án → UNRESPONSIVE, thu #4–8 về REPLICATION

- **Bằng chứng (fetch + paginate toàn bộ 167 comment)**: AI-3 chỉ có **1 comment** (CLAIM
  `#4–8` 08:46 `…Bfi29Iw` — kế hoạch đúng, #5 root `level2:5739` border-from-metadata) —
  sau đó **0 comment · 0 commit · 0 artifact**; tip `ceebe881d8` đứng từ 08:32; artifact
  `l3_geometry_bounds.json.gz` không tồn tại; không phản hồi 3 nhắc (N+1/N+2/N+3).
- **Pattern vòng lặp trước claim**: base-sync 08:27 CI **4/5 FAILURE** → `ceebe881d`
  **1047 files · +6443/−6439** (churn gần đối xứng — re-run tool đổi format/thứ tự) với
  **`[skip ci]`**; base tree sync từ ef `9f90c1acb` (cũ — ef hiện `aa80aa3e75`). Kết luận:
  session chết hoặc kẹt regenerate-loop, không hội tụ về deliverable.
- **Quyết (theo nghị quyết công bố từ lần 62)**: **#4–8 → MỞ REPLICATION** — yêu cầu giữ
  nguyên từ claim cũ (#5 border serialize từ sprite metadata, KHÔNG quad thay thế, đủ
  border/vertices/UV/indices + invariants + SHA; #7 resolve-hoặc-chứng-minh; #8 không bịa
  default mesh; claim từng mục được). **AI-3 quay lại phải: re-claim + sync base ef tip +
  cấm regen-1047-files-[skip-ci] (thay đổi file chung phải giải thích + CI thật).**
- Tips lần 65: ef `aa80aa3e75` (#2 đang chạy) · a5 `c114b8728` (#24 đang chạy) · AI-3
  `ceebe881d8` (đứng yên). datas/ = **87**.

### 24.59 Điều phối lần 66 — AI-3 mới lên ngành (#5 va chạm phân xử) · #24 + #5 ĐÓNG bó scope

- **AI-3 mới (`arena/8141386a`)** — setup ĐÚNG quy trình: base `600a4a340b` từ ef tip
  `f5a447c15a` + nguyên 3 shared từ spec tip `0e2af55f4b`; đọc TOÀN BỘ 171 comments bằng
  `gh api --paginate` (gh 2.23 không có `pr view --paginate` — ghi chú môi trường); khai
  overlap với claim của a5 trước. **Setup issue khai thật**: tree đồng bộ từ ef KHÔNG có
  `docs/spec/` + `tools/verify-claims.py` + `refresh-readme-sizes.py` → chấp nhận phương án
  của họ: tự dựng needle-verify có provenance trên nhánh mình, KHÔNG bịa 209-PASS, CI thật,
  handoff sau push.
- **PHÂN XỬ #5 (first-claim wins)**: a5 CLAIM **11:20:43** (`6414763120`) < AI-3-mới
  **11:31:02** (`…BflxZQA`) → **primary #5 = a5**. Làn REPLICATION của 8141386a hợp lệ
  (đã khai, tool/artifact riêng, không import WIP của a5) — đề nghị: làm REPLICATION nhanh
  rồi nhặt **#4 (còn trống) làm primary**.
- **#24 a5** (handoff 11:18, code `837ca858ff`, SHA `33db7386bf6d…` khớp ✓, report 122):
  status `BOUNDED_STATIC_REPLICATION_NOT_RUNTIME` — kết luận: **mảng #20 nằm trên
  display-power path; `Player_Attack_1` main-cannon path đọc mảng KHÁC
  `Player_Get_Datas.StartMainCannonDamages`, rank kế thừa gate số vòng lặp có điều kiện** ✓
  (đúng cross-spec 0,16/lv r90 — không trộn 0,168 UI) · REPLICATION pins peer source +
  raw bytes ✓ · 30 focused tests. **ACK bó scope static; runtime/hit-delta vẫn MỞ (#28 lane).**
- **#5 a5** (handoff 11:32, code `0252bd8bb6`, SHA `b2f6ffc408…` khớp ✓, report 123):
  REPLICATION inputs từ ef receipt `f5a447c15a` pin ✓ — **re-count 441 sliced + 14 tiled;
  model 112 nonzero-border sliced grids (16 vertices/54 indices mỗi grid) + 10 borderless
  tiles; loại 1 undersized; loại 123 atlas-backed + 4; không có bordered tiled row trong 4
  scenes** · `level2:5739` có mặt ✓ · conventions khai (pivot/clipping = model conventions)
  · mở: atlas/undersized/bordered-tile behavior + native generator. **ACK bó scope
  serialized-geometry model; KHÔNG native-generator recovery/render.**
- **#2 ef**: tip `f5a447c15a` "Prove tag23 native registration, dispatch and SpriteRenderer
  sprite callbacks in guarded fixtures" — code-level xong, handoff chưa đăng → theo dõi,
  không pre-ACK.
- datas/ 87→**89** (#24 + #5).

### 24.60 Điều phối lần 67 — #2 ĐÓNG bounded (tag23 native mapping PROVED) · trả lời AI-3 verify-pattern · #28 lane chạy

- **113-ef #2** (code `f5a447c15a`, Verify `40314713081`, full **1371 PASS**; SHA
  `af91630b507c…` khớp ✓; raw 32215B `b1370b5e…` ✓): chuỗi native thật — registry wrapper
  6a9d50→6a97a0 · **slots[23]** stores (57 instr, allocator-only hook) · lookup
  6a9674→6a94f0 dispatch virtual callbacks (69 instr) · resolver 946d0c nhận `m_Sprite`
  (96 instr, zero hooks) · type records SpriteRenderer/212→10ead38 · Sprite/213→10e8fe0.
  *Spec đối chéo theo decimal trong artifact: handler_vtable 17538432 = 0x10B9D80 ✓ ·
  descriptor 17739064 = 0x10EAD38 ✓ · 0x93B09C ✓ · libunity `d827b83e` ✓.* Model bridge:
  opt-in `m_Sprite` native-derived (Finger2 5922; refs 3799/2633 alternating · 51 writes —
  modeled, không render). **Verdict: ĐÓNG bounded native mapping gate — customType23
  (counterexample r104) NÂNG LÊN "native mapping ĐÃ CHỨNG MINH trong fixture"; vẫn MỞ:
  Unity bootstrap/services/readback/runtime + full setter; r105-UNPROVED giữ historical.**
- **Trả lời AI-3-mới (verify-pattern)**: 160/27/24 khai thật = đúng chuẩn. Quy định: (1)
  209/0/2 là gate NHÁNH SPEC — digger KHÔNG bắt buộc tái tạo; (2) nhánh digger giữ docs
  import ở commit riêng "verification-only" (đã làm) + pin **baseline snapshot của mình**
  (160/27/24 + lý do từng FAIL) vào `_verify_baseline.json` → regression gate = FAIL
  không TĂNG qua các report; (3) focused tests của mình phải xanh; (4) nếu đồng bộ đủ docs
  spec hiện hành thì mới đối chiếu needle như a5. Không bắt buộc thêm.
- **#28 lane**: a5 CLAIM (11:40) — loader-apk trước, fail thì **fallback ①**
  STATIC_CROSSCHECK_NOT_RUNTIME từ data #21 (report 124, giữ receipt 121). Đúng 2 nhánh
  lệnh lần 64.

### 24.61 Điều phối lần 68 — góp ý AI-1 (#5-rep/#27) + DUYỆT support-view AI-3 + witness byte #5 hội tụ

- **Góp ý AI-1 (11:43 `…Bfl-kPA`)**: ① nhắc board mốc "chưa handoff" — board lần 67 (11:46)
  đã cập nhật #2 ✅ trước khi họ đọc ACK67 — xác nhận, không phải lỗi mới. ② **#27 CLAIM
  (114-ef)** — native interpolation từ AnimationCurve.Evaluate registration → native
  callback; scope khai đúng mức (phân biệt API vs clip streamed/dense vs Animator blending;
  cubic model sẵn có KHÔNG là proof; equivalence chỉ mở khi có caller/data-layout evidence)
  → **DUYỆT claim, đúng miền "đào tận cùng"** (tips `725ec4d75`→`293ec53f59`: original
  unwind extents + weighted inverse solver + exact ELF math import identities — đang chạy).
  ③ **Góp ý #5-rep chuyển tiếp AI-3**: tách source-owned invariants vs inherited harness
  diagnostics; cấm "chữa" 160/27/24 bằng đổi needle; atlas Panel_Info phải kiểm
  transform/rotation/packing từ exact render-key + UV continuity; **model-agreement 2 tool
  ≠ native generator/readback** — đúng chuẩn, đã đưa vào duyệt boundary dưới.
- **DUYỆT support-view boundary của AI-3-mới (11:46)**: (a) giữ diagnostic gốc
  **160/27/24 nguyên trạng, KHÔNG sửa expected** ✓; (b) *verification support view* tách
  namespace, pin path-set từ spec `0e2af55f4b` (historical docs/receipts/CSV) ✓; (c)
  **APKD1/AI1/RD1 đo own worktree, sync cùng report commit** ✓; (d) nếu đạt 209 phải gọi
  "**scoped historical-support compatibility**", KHÔNG gọi "current ef data qua 209" hay
  geometry accepted ✓. **Điều kiện bắt buộc thêm: pin snapshot support-view (path-set +
  commit pin + kết quả từng nhóm) vào artifact/receipt của report #5-rep** để spec tái
  kiểm được mà không cần dựng lại view. Đây là pattern chuẩn cho mọi digger sau này.
- **#5 hai tool hội tụ (chưa handoff, pre-note)**: a5 model cutsX [-5,-4.55,4.55,5] từ
  receipts ef · AI-3 byte witness recovery CI `40316865222` (XAPK SHA verified, 4 root-chain
  hash khớp raw102): object offset40 LE `00003442 0000a041 ×2` — *spec decode: 45.0/20.0 ✓
  = border [45,20,45,20] khớp a5; PPU offset56→100 · pivot [.5,.5] · cutsX = 5−45/100 =
  4,55 ✓*. 26 tiled rows reject-có-reason ✓. **Chờ handoff chính thức (#5-rep) rồi ACK.**
- ef không lấy #4–8/#28 — ghi nhận; #4/#6/#7/#8 vẫn mở cho AI-3-mới sau #5-rep.

### 24.62 Điều phối lần 69 — #28-fallback① + #25-bounded + #27-core ĐÓNG bounded · #26 CLAIM

- **#28 fallback① a5** (code `bb22d6c599`, report 124, SHA `434fc2db2abf…` — handoff không
  khai SHA, spec ghi từ pull): loader lane kiểm scoped — release chỉ có `windwings.xapk`
  (không .apk/.apks tracked ở cả 2 peer tree) → **không tự lấy loader** (đúng boundary,
  không global-absence) ✓. **STATIC_CROSSCHECK_NOT_RUNTIME**: 250 rows (243 IA + 7 inline)
  crosscheck — **742 integer values, 0 mismatch** với runtime outer 250 (#19); 243+7=250
  nhất quán độc lập với #21 (spec đối chéo 2 artifact) ✓; `arr=256&depth=2` = NOT_OBSERVED;
  receipt 121 giữ nguyên. **Verdict: ĐÓNG bó scope fallback①; loader lane (chờ chủ dự án
  cung cấp) + fallback②③ KHÔNG dùng — #28 vẫn MỞ phần đó.**
- **#25 a5** (code `70adfa68d0`, report 125, SHA `6283991693cf…`): **74 methods từ pinned
  persistence receipts: 0 direct `PlayerPrefs.Save()` edges** · direct B/BL scan RVA
  `0x277cf6c` qua **314 raw ASM files (7.823.314 B, inventory SHA pinned): 0 hits** ·
  `PlayerPreferences.SaveToDisk`: **3 callers + 1 `File.WriteAllBytes` edge** · migration
  search 0 signals · `schema_version=1` là analysis-pack ≠ game save version. **Verdict:
  ĐÓNG bounded slice (scoped non-observation có pins); #25 VẪN MỞ** (platform
  durability/crash-atomicity/cloud/migration/runtime round-trip).
- **#27 ef 114** (scientific `33cdc61a9`, Verify `40319106339`, full **1411 PASS**; SHA
  `9e795a9f6041…` khớp ✓): chuỗi native interpolation **zero function hooks** — icall
  389544 → callback 36e71c → evaluator 952608 → search/cache/segment/weighted/inverse ·
  **FALSIFICATION: duration-floor bits `0x38d1b717` = 9.999999747378752e-05** *(spec decode
  struct: khớp chính xác ✓)* — float32(0.00001) midpoint → cached **0.007249999791383743**
  ≠ direct segment 0.5 ⇒ **KHÔNG universal ideal cubic** (hủy cách đọc cũ float64 sampler
  = engine truth) · weighted quadratic 233 instr (0.5 vs unweighted 0.15625) · host ELF
  math (atan2f/logf/exp/cosf) ≠ Android-libm ULP · **native producer 6c4480 + packer:
  84 bytes/204 instructions, frame-header 8/key 20** (StreamedClip coefficients native!) ·
  tiers tách rõ: ≠ ParticleSystem consumer, ≠ packed-clip indexing, ≠ Animator blending.
  **Verdict: ĐÓNG bounded native-core; #27 MỞ** (packed-clip ownership/consumer/dense/
  weighting/runtime).
- **#26 CLAIM a5** (12:01, report 126) — đang làm; #4/#6/#7/#8 chờ AI-3 #5-rep.
- datas/ 90→**93**.

### 24.63 Điều phối lần 70 — #26 ĐÓNG bó scope (static-root pixel-projection) · #27/115 tiếp packed-clip

- **126-a5 #26** (code `0002070e8a`, SHA `e0fe9b1aea39…` khớp ✓, 57 tests): chuỗi đầy đủ
  hơn #12 — **Board_Pause root `resources.assets:212696` (235 nodes, serialized inactive)**
  · Popup_QuitMissions GO 57508/Transform 425352 → parent 439142 → root, local (0,0,−2) ·
  **trong renderer/context captures pinned: 0 name/pathID match + 0 PPtr edge tới root** ·
  **5 cameras (level0–3) không link template** ⇒ `pixel_bounds=null · rendered=false` —
  không đoán camera (chuẩn #12, giờ có census template_root 235 nodes làm nền) ✓ ·
  boundary khai: không all-class census/PrefabInstance/runtime-instantiation proof ✓.
  **Verdict: ĐÓNG bó scope static-root audit — pixel projection cần RUNTIME instantiation
  (scene instance + placement authority) — mặt bằng dữ liệu tĩnh đã hết đường, điều này
  LÀ kết quả tận-cùng (b), đúng chuẩn lệnh lần 62.** Chỉ runtime (#28 lane khi có
  loader/device) mới vượt được.
- **#27/115 ef** (12:09, tips `86d1f0682e` · `d11ceabc9a`): compiled clip runtime code
  region + original type-record backreferences + **packed sampler callers × serialized
  count fields × class74 record** (class74 = clip identities từ #110 — nối được chuỗi
  791 clips!) — khai đúng: cache adapter ≠ consumer proof. Đang chạy, chờ handoff.

### 24.64 Điều phối lần 71 — #5-rep + #6 + #27/115 ĐÓNG bounded · LỆNH CHẠY RUNTIME PROBE

- **#5-rep 8141386a** (code `c86db3ee5`, CI GREEN `40320393140`+`40320393233`, full **1410
  PASS**; SHA `0b77e656d264…` khớp ✓): byte witness recovery `40316865222` (XAPK SHA
  verified, 4 object hash khớp raw102) → border [45,20,45,20] · **16 vertices/54
  indices/18 triangles**, cutsX [-5,-4.55,4.55,5], cutsY [-2.5,-2.3,2.3,2.5] · UV
  source-pixel cuts · 26 tiled rows not_generated-có-reason · **model-agreement với a5**
  (2 tool độc lập cùng số) — KHÔNG suy native generator/readback (cả 2 khai shared
  lineage) ✓. **Support-view pin ĐỦ theo điều kiện lần 68**: baseline 160/27/24 frozen +
  current 163/25/23 (không FAIL mới) + scoped 209/0/2 · `verification-5.json.gz` giữ
  99-path snapshot + spec commit + per-group FAIL/SKIP + logs — tái kiểm được ✓.
  **ACK ĐÓNG #5-rep; PRIMARY #5 (a5) + REPLICATION (8141386a) cùng ĐÓNG.**
- **#6 a5** (code `af518716b7`, report 127, SHA `8d320f1458f8…` khớp ✓): **1550/1550
  atlas-backed sprites resolve 1:1** (owning-file PPtr + renderDataKey; 66 atlases map
  rows/packed PPtrs/names khớp hết) · 635 direct `m_RD` · **2185 sprites: m_Bones +
  m_Bindpose EMPTY (scoped)** · mesh contract 27.072 static verts/2185 AABBs ·
  localAABB zero · boundary: atlasRequested/atlasRegistered chỉ DECLARED (IL2CPP dump),
  chưa có subscription/runtime remap ✓. **ACK ĐÓNG bó scope static remap; runtime remap
  MỞ (thuộc runtime lane).**
- **#27/115 ef** (scientific `61de2d57ef`, Verify `40321809391`, full **1451 PASS**; SHA
  `32f8105361cc…` khớp ✓): **packed-clip consumer native chain PROVED bounded** —
  owner+0x1e0 → blob+0x5f0 → 6d2e94→6df270→6df310→6df768 · **2262 uint32 words/9048B từ
  resources.assets:1609 copy UNCHANGED (không inject coefficient)** · **92 continuous +
  1 discrete ×10 samples = 930 DWORDs bit-equal separate-f32** · +Inf terminal header
  byte 9040 · initializer 6df02c 597 instr (1 allocator sub duy nhất) · discrete
  0x40a00000 = raw DWORD (không suy sprite index) ✓. **ACK ĐÓNG bounded consumer; #27
  MỞ: dense 6df518 (unexecuted) · timewrap b93158 · Animator blending/bootstrap/
  readback/render.**
- **⚡ LỆNH CHỦ DỰ ÁN (lần 71): CHẠY RUNTIME PROBE — duyệt phương án (b)**: digger (a5,
  có vehicle PR14) **tự dựng loader-apk trong CI** từ components pin (MelonLoader/
  BepInEx + `RamusBridge.dll` từ repo, CI bridge-build PASS sẵn) → cài ramus → thu
  receipts. **Boundary bắt buộc:** loader ≠ evidence source (receipts pin SHA loader +
  provenance; original XAPK bytes KHÔNG đụng); session ưu tiên: ① map
  `arr=256&depth=2` (đối chiếu 742 values) ② second-device ③ live-DPS same-build;
  fail → báo blocker thật, không bịa; mỗi receipt = artifact riêng + report.

### 24.65 Điều phối lần 72 — GỠ CẤM MOD APK (mọi biện pháp) · ACK 116 · #28 accepted · #4 progress

- **⚡ LỆNH CHỦ DỰ ÁN (lần 72): "bỏ cấm mod APK, cho phép dùng mọi biện pháp".** Quy đổi
  từ nay: **APK gốc vẫn là authority cho mọi static evidence** (SHA XAPK/APK vẫn pin như
  cũ) — nhưng **repak/rebuild/loader/instrument (APKEditor, merge splits, inject
  bridge/dll, smali patch…) ĐƯỢC PHÉP** cho mục đích chạy runtime probe. **Boundary còn
  lại (integrity, không phải công cụ):** ① package đã mod = **vehicle, không phải evidence
  source** — mọi receipt pin SHA vehicle + công thức dựng (components + commit); ② dữ
  liệu runtime đọc được phải đối chiếu được với static data đã ĐÓNG (742 values…);
  ③ KHÔNG bịa readback — fail báo đúng bước; ④ không tự ACK/main/merge; ⑤ static analysis
  tiếp tục trên APK gốc (không đổi nguồn đào tĩnh). Lệnh này gỡ blocker #28 loader —
  a5 đã accept (12:42) và giờ có thêm mọi biện pháp nếu loader thuần không đủ.
- **#27/116 ef** (scientific `61f31ae26f`, Verify `40324149097` exact head, full
  **1491 PASS**; SHA `bcde214305db…` khớp ✓): **clip-time native chain + dense/constant
  thực thi**: 6d2e94→b93158→6df270→stream 6df310/dense 6df518/constant 6d9200 · serializer
  fields pin m_StartTime+0x5f8/m_StopTime+0x5fc/m_CycleOffset+0x608 · **counterexamples
  từ instruction gốc**: loop −1→phase1/cycles−2 (không `%1`) · S4 negative-zero flips
  phase qua signbit · **FRINTA tie-away có thể trả sample VƯỢT stop trong khi phase
  clamp** · dense clamp row-index nhưng KHÔNG clamp fractional (u−0.5→[-5,5]) · 1609
  2262 words + start/stop/cycle/loop adapt → **930 DWORDs khớp separate-f32 SAU native
  time conversion** · **source dense curveCount=0/sampleArray[] dù frameCount=420 →
  branch skipped (data thật)** · subs khai: modff (PLT 17414144) + memcpy host — *spec
  cross-check decimal: đủ địa chỉ · counts 24+8+5+10=47 calls/29.126 instr/48 modff/
  5 memcpy ✓.* **Verdict: ĐÓNG bounded time+dense/constant composition; #27 MỞ: Animator
  context/bootstrap/blend/readback.**
- **#28**: a5 accept probe 12:42 (receipt `l2_a5a74747_28_loader_runtime_map` + report
  128; giữ 121/124) — chờ push. **#4**: AI-3 PROGRESS 12:42 — recovery `40322602149`
  **1751/1751 object hash khớp** · 7 fonts/2352 glyph/2354 char/2285 unicode · artifact
  local SHA `9cec092de…` · 59 focused PASS — handoff chờ push+CI.

### 24.67 Điều phối lần 74 — #4 ĐÓNG bounded + #27/117 ĐÓNG bounded · loader probe vướng workflow · RECHECK-2 độc lập

- **#4 8141386a** (scientific `7ec2f9484e`, Verify `40325454253` + scoped gate
  `40325454263`, full **1430 PASS**; SHA `9cec092ded27…` khớp ✓): byte proof — recovery
  `40322602149` **1751/1751 object hashes** · **14 table spans/160024B** unique aligned ·
  **7 fonts / 2352 glyph rows (52B) / 2354 char rows (16B) / 2285 Unicode union** ·
  **797 metric previews (768 nonempty/1608 quads) + 940 null-có-reason** · layout
  52/16B = seeded corroboration (raw102/Graph/111/110/font73 lineage — disclosed) ·
  **coordinates = pointSize-normalized design units, NOT em (allUnitsPerEM 0)** ·
  Level0:86 → 28 vertices/28 UVs/42 indices · null-font 699094 ≠ default-assign · tab
  693185 = control-unknown ≠ visible-missing ✓. **ACK ĐÓNG bó scope static fallback
  geometry; native TMP parser/SDF quads/runtime text MỞ.** (#6-rep CLAIM đúng thứ tự
  #5→#4→#6 — ghi board.)
- **#27/117 ef** (scientific `7f182db37d`, Verify `40326789273`, full **1531 PASS**; SHA
  `ef1d97806f66…` khớp ✓): **duration virtual getter thật** — clip ctor `b69d14` store
  vptr `10c3fa8` · RELA `10c4050(+0xA8)→b6bf94` trả `stop(0x5fc)−start(0x5f8)` từ
  clip+0x1e0 muscle blob · **context writer 6d3744 zero substitutions** · counterexamples
  gốc: `.7` double→bits **3f333334** (=0,7000000476837158 — *spec decode ✓*; *sửa lần 75
  theo đính chính ef: **KHÔNG phải tie-away** — 6d3744 FCVT gần nhất rồi tăng 1 ULP về +∞
  nếu quotient f64 > f32 (guard FLT_MAX); **FRINTA tie-away = nhánh quantization
  116/b93158, tách riêng**) · underflow dương→min-subnormal, âm→−0 · duration 0→cả hai 0 ·
  FSUB→FADD mutation đổi normalization · staged caller 6d3924 (native blob→writer→cache
  ptr→116-time→115-stream→phase) — **930 DWORDs khớp lần nữa** · 12 context cases/718
  instr/0 subs · 18 staged/31272 instr/18 modff. **ACK ĐÓNG bounded; Node creation/
  game-side writers/full caller/weighting/apply MỞ.**
- **Loader probe #28**: run `40326606441` **FAILURE = "workflow file issue"** (GitHub
  không parse workflow — probe CHƯA chạy, không phải bridge/session gãy) · a5 đã commit
  fix "integrate probe into PR CI" (`cea0090cca7` 13:07) — nhưng bridge-build ĐỎ ở commit
  đó, cần xem lại. RECHECK độc lập của a5 trùng kết luận spec (thêm: chuẩn hóa float32
  bit-pattern + pins SHA XAPK/libil2cpp/wing_drone_flow/runtime statics).
- datas 98→**100** (#4 + #117).

### 24.68 Điều phối lần 75 — đính chính tie-away + #27/118 ĐÓNG bounded + AI-3 restart + #28 grind SDK

- **Đính chính ACK117 (ef đúng, spec sai)**: `.7→3f333334` **KHÔNG phải tie-away** —
  6d3744 dùng FCVT gần nhất rồi **tăng 1 ULP về +∞ nếu quotient f64 > f32** (guard
  FLT_MAX); opcode mutation 6d3798 kiểm điều này. **FRINTA tie-away = nhánh quantization
  116/b93158** — hai cơ chế khác nhau, đã sửa DS/DONE (supersede inline).
- **#27/118 ef** (scientific `79602dd6f2`, Verify `40329033477`, full **1571 PASS**; SHA
  `4eaa9a118efb…` khớp ✓): **full original caller FDE 6d38bc..6d3ebc chạy entry→RET
  6d3eb4 KHÔNG staging thủ công** — prologue/TLS/context→duration vtable→time→stream→
  scratch/phase→guards/epilogue · domain enforced: frame 0/28/29=0, rig 80/82=0
  (synthetic inputs — khai rõ) · unsupported previous/pose **reject thay vì bịa** ✓ ·
  **10 source × 93 = 930 DWORDs bit-equal (lần 4)** · 18 samples/32.862 instr/18 modff ·
  scratch b923ac thật · null-blob fallback 6d3600→6dacf0→b92414: 87 instr/0 subs ·
  fault-injection tới **PLT `__stack_chk_fail` thật — failure rõ ràng, không fake
  success** ✓ · synthetic TPIDR_EL0 ≠ Android TLS (khai) ✓. *Spec cross-check decimal:
  6d38bc/6d3ebc/b923ac/930/32862/stack_chk đủ ✓.* **ACK ĐÓNG bounded current-caller;
  #27 MỞ: node creation/game-side writers/graph bindings/pose/weighting/apply.**
  (ef đã CONTINUE119: parent 6d46a8→6d38bc→6d3ebc→writes node174 — nhịp ~1 report/15 phút.)
- **AI-3 8141386a RESTART sau OOM** (update 13:17): tip giữ `7ec2f9484e` (receipts #5/#4
  nguyên vẹn), tiếp **#6-rep** theo claim cũ — đã áp OOM-safe: **streaming shard + batched
  records, không giữ full Graph/atlas trong RAM** ✓ đúng prompt. #7/#8 chưa đụng.
- **#28 a5**: 5 commit fix workflow liên tiếp (pin SDK action Node24 · job paths ·
  pipefail · split installs) — đang nhồi CI infra; probe chưa chạy lại thành công, receipt
  121/124 giữ. Chờ run xanh.
- datas 100→**101** (#118).

### 24.69 Điều phối lần 76 — #27/119 ĐÓNG bounded (parent + guards) · #6-rep OOM-safe chạy tốt · #28 tiếp SDK

- **#27/119 ef** (scientific `b9e6765fa6`, Verify `40330340745`, full **1581 PASS**; SHA
  `49eb74d14c97…` khớp ✓): **parent FDE 6d46a8..6d46f4 entry→118-caller→second-phase
  6d3ebc→node174=1→RET 6d46f0, không staging** · **10 calls/930 DWORDs/29.974 instr khớp
  pinned 118 outputs** (lần 5) · **3 early-returns native**: null-blob 24 instr ·
  descriptor mode −1 = 29 · flag28-zero = 31 — đều RET 6d4424, output không đổi ·
  **Null-parent vẫn ghi node174=1 ⇒ "byte đơn chứng minh SAMPLING/APPLY là suy — phải có
  input/writer thật"** (điểm chống-lạm quan trọng) · second-phase active BỊ TỪ CHỐI chạy
  với rig giả ✓ · context-stack base 1ee70 verified vs 118. *Spec cross-check decimal:
  6d46a8/6d3ebc/6d4424/930/29974 đủ ✓ (1ee70 ghi dạng khác trong artifact — không phải
  lệch).* **ACK ĐÓNG bounded parent+guards; #27 MỞ: node/game-writers/pose/weighting/
  blend/apply/bootstrap.** Nhịp ef: 5 reports (#114–118) + #119 trong ~85 phút, mỗi bản
  1 tầng mới có counterexample — đáng kể nhất chuỗi.
- **#6-rep 8141386a OOM-safe CHẠY ĐƯỢC** (checkpoint `b1b88beb78` push + PROGRESS 13:33,
  không handoff): stdlib inverse serializer **stream 1 tree/lần** — full bytes match
  capture SHA cho **2185 Sprite + 66 atlas** · decoder riêng đếm **27.072 vertices** (khớp
  mesh-contract a5) · 17 new focused/1447 full local · scoped 209/0/2 giữ · XAPK EOF lại
  ở release-host → **mmap compressed bundle + ≤16 decoded blocks/lần + SQLite flush
  250-record** (đúng prompt OOM) · recovery CI đang chạy — không claim byte-corroboration
  trước receipt. ✓✓
- **#28 a5**: tiếp grind runner — `Use FusionCore CI runner Android SDK` + expose
  stage-failures (`f9b4695a98`) — chẩn đoán tách tầng trước, sau đó mới run lại. Chưa
  có run probe xanh mới.

### 24.70 Điều phối lần 77 — #27/120 ĐÓNG bounded · #6-rep byte-equal · ĐÁNH GIÁ runtime probe 23/10: ĐỦ config-parity, CHƯA đủ behavior — lối đào nghẹt 1 secret

- **#27/120 ef** (scientific `10b46c13d3`, Verify `40332906465`, full **1601 PASS**; SHA
  `fe2c0997d2ec…` 6484B khớp ✓): **node constructor FDE 6d353c..6d35f4 entry→base
  6d6aa0→57054c→member 6a6ff4→RET** — **174 instr gốc / 0 service sinks** (sinks rỗng
  cưỡng bức chặn bridge-substitution) · pool get/atomic-pop 53f36c + counter/queue-tag/
  chunk-append chạy thật · **write-coverage 447/512 bytes viết / 65 preserved ≠ memset**
  · primary vtable 10b1240 (+80 RELA 10b12c0 → **parent 6d46a8 — khớp 119**) · secondary
  10b1420 · defaults clock/current/previous/flag/weight từ store thật · **10 parent calls/
  930 DWORDs bit-equal — lần 6** ✓. Caller 6d5e58..6d5ec8 recovered, KHÔNG execute
  (incoming size +200 cấm claim universal size) ✓. *Spec cross-check decimal: 6d353c/
  6d35f4(RET)/6d6aa0/57054c/6a6ff4/53f36c/vtables đủ ✓; service 116cb40 = harness
  prerequisite — không nằm trong artifact (đúng vì là input harness).* CONTINUE121 đang
  đào factory 6d5e58 (allocator 3c986c→ctor→handle 570ff0/572a38).
- **#6-rep 8141386a — scientific `311a45df04`** (SHA `361354d6b7ac…` 1.195.537B khớp ✓,
  full 1467 PASS): recovery `40331600575` SUCCESS — **2905/2905 object hashes**
  (2185 Sprite/66 Atlas/654 Texture2D) · **2251 whole-object BYTE-EQUAL inverse
  serialization / 1.720.744 B** · static riêng khớp a5-primary TOÀN BỘ (1550 joins + 635
  direct · bounds 2185 · 27.072 verts · overlap 1389/44) — **diffs 0**. Replication chạm
  mức byte-exact trên Sprite+Atlas — chờ exact-head Verify/scoped/PR15 GREEN rồi HANDOFF.
  Peak builder 27.992 KiB (OOM-safe giữ vững). ✓
- **ĐÁNH GIÁ RUNTIME PROBE 23/10 (lệnh chủ dự án: "đủ chưa? nếu chưa thì đào, đừng cố
  nhiều lần") — kết luận: ĐỦ cho config-parity, CHƯA đủ cho behavior, lối đào nghẹt ĐÚNG
  1 secret:**
  - **ĐỦ (đã KHÓA tĩnh↔chạy):** BaseDamages[12] 12/12 crossbuild 1.0.69↔1.3.118 ·
    12v10 giải (#19) · map 250 rows/742 values 0-mismatch (#28-fb①) · anchor catalog
    (PlayerCosts/legendary/ranks/prices/StartDroneSkillDamages/Stage 249≈250) — mọi câu
    hỏi "giá trị config" đã có chứng cứ 2 chiều; đào thêm trong vùng này = lặp.
  - **CHƯA ĐỦ (3 câu hỏi chỉ runtime trả lời được):** ① **live-DPS/bắn drone·wing**
    (static r92 ĐÓNG, runtime chưa đo) ② **#27 consumption thật** (node174→pose
    apply→readback — ef đang đóng cấu trúc native, runtime phải chứng minh game THẬT
    consume) ③ **second-device** (receipts 121/124 pin 1 thiết bị).
  - **Nghẹt 1 điểm duy nhất — CHỈ chủ dự án gỡ được:** run `40333586413` bridge-build
    **GREEN** (loader `d946aa3015…` · bridge `3817256d80…` · source XAPK `f5d3c7a188…`
    khớp RECHECK ✓) nhưng map-gate dừng `BLOCKED_NO_ADB_CREDENTIAL` — secret
    **`RAMUS_API_KEY`** chưa cấu hình trong Actions. **CẤM mọi run mới trước khi secret
    có mặt (chắc chắn BLOCKED — đúng lệnh "đừng cố nhiều lần mất công"); a5 giữ
    receipts 121/124, không tự retry.**
  - **KỊCH BẢN 1-LẦN khi secret sẵn sàng** (one-shot có ủy quyền, KHÔNG retry-loop):
    ① transport gate pass → ② **live-DPS/firing capture** (giá trị cao nhất) → ③
    second-device CHỈ nếu ② ra lệch. Fail ở bước nào → dừng, báo đúng bước (lần 71 giữ
    nguyên). **Nhánh B** (chỉ khi chủ dự án không muốn đặt key): pivot emulator x86_64 +
    frida-il2cpp-bridge (công cụ đã mở §24.65) — phải có lệnh chủ dự án mới chuyển.

### 24.71 Điều phối lần 78 — LỆNH CHỦ DỰ ÁN: ĐÓNG #28 runtime probe (static đủ) · #6-rep ĐÓNG byte-exact · CLAIM #7

- **⚡ LỆNH CHỦ DỰ ÁN (26/10): "bỏ 28 runtime, phân tích tĩnh được rồi"** — hiệu lực ngay:
  ① **#28 runtime probe ĐÓNG theo quyết định scope** — không đặt `RAMUS_API_KEY`, không
  run mới, nhánh B (emulator+frida) KHÔNG chuyển; ② **receipts giữ nguyên như historical**:
  121/124 (23/10) + bridge-build `40333586413` GREEN — vehicle vẫn là minh chứng
  config-parity và loader-pin, không xóa; ③ **3 câu hỏi behavior chuyển mức chứng cứ
  static-only**: live-DPS = **MODEL_NOT_MEASURED runtime** (đã đóng tĩnh r92: damage×rate
  ≠ DPS, wing/drone bắn ĐÓNG tĩnh) · #27-consumption = cấu trúc native đóng dần (ef),
  readback runtime KHÔNG claim · second-device = không thực hiện; ④ mọi kết luận tương
  lai về 3 câu này phải ghi "chưa đo runtime" — cấm tụng static thành runtime.
  @a5a74747: dừng #28, không đốt run; nhận việc mới theo bảng.
- **#6-rep 8141386a ĐÓNG** (HANDOFF `6417920301`, spec kiểm runs thật: Verify
  `40334704704` + scoped `40334658103` + PR15 vehicle `40334670934` đều **SUCCESS trên
  head `311a45df0`** ✓): **2905/2905 hashes · 2251 Sprite+Atlas BYTE-EQUAL / 1.720.744 B
  · 1550+635 maps · 27.072 verts/73.125 indices/2185 AABB · 4370 zero-counts · diffs 0
  vs primary** — replication chạm mức byte-exact, **a5 giữ primary #6**. Ghi nhận đúng
  phép: "vehicle bridge-gate skip ≠ runtime evidence" + Texture2D hash-only (không decode
  ảnh) + "not live-remapped" (live/deformed outputs null — MISSING-X native consumer
  tiếp tục MỞ đúng biên). Peak 27.992 KiB — OOM-safe giữ vững.
- **CLAIM #7 8141386a** (`6417945015`, first-wins registered): 7 ParticleSystemRenderer
  builtin mesh refs — resolve từ packaged objects HOẶC scoped missing-X có pins; #8
  untouched đến khi handoff #7.

### 24.72 Điều phối lần 79 — TỒN ĐỌNG tổng + PHÂN CÔNG LẠI: ef giữ chuỗi native, a5 nhận miền game-side (C#/il2cpp)

- **⚡ Lệnh chủ dự án (26/10): "còn gì tồn đọng? AI-1 nhiều việc — phân ra để AI-2 có
  việc làm."** Rà tồn đọng từ FILE (26/10):
  1. **#27 native structural** (ef 🔄 121 factory — probe intermediate `cca51db0b7`,
     chưa handoff): còn graph creation/service bootstrap (native)/clip binding/clock+
     control writers native/previous+active pose/conversion→blend→normalize→apply/
     readback/render.
  2. **#27 game-side writers + bootstrap (libil2cpp/Assembly-CSharp) — CHƯA AI LÀM** →
     tách cho a5 (bảng dưới).
  3. **#7** AI-3 🔄 (954 PSR · 17 nonnull = 10 other/local + 7 builtin, raw 7/7
     unresolved → Library/unity default resources, không đoán Quad/Cube ✓) · **#8** hàng
     đợi sau #7.
  4. **MISSING_FOR_NEW_GAME 8 đủ / 8 một phần** — câu còn: Boss pha (D3: thứ tự pha +
     điều kiện vào/thoát) · Meta (23 wing impl + DPS closure → runtime nay
     MODEL_NOT_MEASURED) · save schema đầy đủ + flush đĩa · Tech plugin list (row 13,
     "không cần thiết bị") · Arena/PvP · meta thưởng ngày/tuần · sprite/prefab-binding
     luật số/join.
  5. **DESIGN_QUESTIONS 33 ❌ / 14 ⚠ / 9 blocker** — lớp thiết kế, không thuộc đào data.
  6. **StartDroneSkillDamages[12] "chưa có static — mỏ digger kế tiếp"** (RECHECK lần
     73; runtime `[556,10000,5600,710,1999,2650,933,5500,1085,7200,1868,1199]` đã biết).
- **PHÂN CÔNG MỚI (hiệu lực ngay):**
  - **ef (AI-1) GIỮ**: chuỗi native libunity node-pipeline structural (121 factory →
    graph creation → service bootstrap native → clip binding → clock/control writers
    native). Miền: `libunity.so` FDE — không đổi.
  - **a5 (AI-2) NHẬN MIỀN MỚI — game-side writers/bootstrap, static-only**:
    ① method C# GHI pose/clip/previous buffer (từ node174/clip input ngược lên game
    side) ② bootstrap game-side cấp service/queue/chunk — đối chéo `116cb40`-harness
    của ef ③ clock/control writers C#. Công cụ: dump.cs + il2cpp metadata + RVA pin
    (thế mạnh #28/r90 của a5). **Quick-win phụ khi chờ phản biện**: ④ static mỏ
    StartDroneSkillDamages (đối chiếu 12 giá trị runtime) ⑤ MISSING row 13 plugin list.
    Boundary: **KHÔNG đụng libunity FDE (ef)**; va chạm → CLAIM first-wins trên board;
    artifact/report/datas riêng; static-only (lệnh 26/10) — cấm tụng thành runtime.
- Supersede dòng cũ RECHECK "Map contents placeholders — chờ probe CI": #28 ĐÓNG theo
  lệnh 26/10 — giữ placeholders, không chờ probe nữa.

### 24.73 AUDIT TỔNG THỂ (lần 80, 26/10) — "được bao nhiêu % rồi?" — chỉ đếm từ FILE

- **Lớp 1 — 16 hệ MISSING_FOR_NEW_GAME (mục tiêu dựng lại):** đếm trọn: **8 đủ (50%) ·
  8 một phần (50%) · 0 thiếu**. Weighted theo cột "thiếu gì" (ước lượng công khai):
  1,0/1,0/0,95/0,95/0,8/0,95/1,0/0,95/0,7/0,85/0,7/0,5/0,7/0,25/0,25/0,65 →
  **12,2/16 ≈ 76%**. Đuôi nặng nhất: Arena/PvP (0,25) · meta thưởng (0,25 — 0 giá trị
  decode, 40 class chưa dịch) · save schema (0,5) · sprite→consumer join (0,65) ·
  Boss pha (0,8) · 23 wing impl (0,7).
- **Lớp 2 — DESIGN_QUESTIONS:** A–F **48 câu: 33 ✅ (69%) · 14 ⚠ (29%) · 1 ❌** — có
  đáp án đủ-hoặc-một-phần **47/48 (98%)**, trọn **33/48 (69%)**. Blocker: **còn 5/9**
  (file tự ghi: A5/A6 phụ thuộc, C4 vàng/giờ, A7 mật độ, B3 damage-curve).
- **Lớp 3 — Chương trình đào #1–#28:** **25/28 ĐÓNG (89%)** — còn mở: #7 🔄 (AI-3),
  #8 (hàng đợi sau #7), #27 🔄 (structural: ef native-lane + a5 game-side-lane).
  #28 ✅ theo scope (lệnh 26/10).
- **Lớp 4 — Tài nguyên/catalog:** sprites-index **2.197** (100% index/classified) ·
  sprites.csv **2.885** · audio **69 clips** indexed + 15 rules · UI **797 màn /
  55.584 layout** cataloged · 42 contact sheets · geometry/pivot/border ĐÓNG (62/72/75).
  Gap duy nhất lớp này: **sprite→consumer join toàn cục** (prefab_joins 3.870 rows,
  0 sprite) — đã là việc của #16/lane a5-AI-3.
- **Lớp 5 — Kho evidence:** datas/ **104 file top-level (+4 subdir ~296 file)** ·
  **71 report** docs/apk-analysis · DONE **79 khối** · 13/16 hệ có artifact `datas/`.
- **LỆNH CHỦ DỰ ÁN 26/10: mở digger thứ 4 (AI-4)** → prompt tự chứa đăng `6418869062`
  + board + hàng task **#29** (Arena/PvP decode — 40 class dump.cs · map pools
  AllArena*/AllPvP* · GetArenaScore/GetPVPPlayScore/GetArenaPlayScore · medal/shop) và
  **#30** (meta thưởng — MAX_LEVEL_BP/timeRewards/vipPoints/giá ô gift-quest-video ·
  Board_QuestRewards/TimeFreeRewardPack/SeasonRewards; CLAIM sau handoff #29).
  Static-only tuyệt đối (lệnh 26/10); boundary: không libunity FDE (ef) / #27-GS (a5) /
  #7-#8 (AI-3); report `127-arena-pvp-<hash8>.md`; needle APKD1/AI1/RD1 sync cùng commit.
- **KẾT LUẬN HEADLINE: ≈ ¾ đường — 76% weighted / 50% nếu chỉ đếm hệ trọn / 89% theo
  task ledger.** Phần còn lại KHÔNG đều nhau: 2 hệ (Arena/PvP + meta thưởng) chiếm ~⅓
  khoảng cách. **Trần 100% đã đổi định nghĩa từ 26/10:** các câu runtime (live-DPS,
  audio-trigger, second-device) **tĩnh-chốt** — % sẽ kẹt ở mức "data-complete static"
  trừ khi chủ dự án mở lại runtime. Việc nâng % kế tiếp (theo độ lớn): ① a5 dịch
  Arena/PvP class → +hệ 14 ② meta thưởng decode → +hệ 15 ③ #7/#8 xong → +task 2 ④
  save schema → row 12 ⑤ ef+a5 đóng #27 → task 89%→100%.

### 24.66 RE-CHECK 26/10 — mỏ runtime 23/10 (Mate 20 X) × static mới: r90 NÂNG static↔runtime verified

- **Yêu cầu chủ dự án**: "thư mục runtime-probe… kiểm xem rút ra được gì". Spec rà toàn bộ
  số thật trong `docs/apk-analysis/ramus/2026-10-23-phone/` — kết quả trong
  **`RECHECK-2026-10-26.md`** (cùng thư mục):
  1. **✅ `Drone_Get_Datas.BaseDamages[12]` runtime `[450,600,6000,135,935,315,650,1200,
     248,650,1200,2650]` == r90 static BaseDamages[12] — 12/12 exact, đúng thứ tự,
     crossbuild (1.0.69 ↔ 1.3.118)** → r90 NÂNG "static-only" → **"static ↔ runtime
     verified"** (mức-A thứ hai sau 250=250).
  2. **✅ Mystery 12-vs-10 (CROSSCHECK 23/10 gọi "lỗ hổng thật") ĐÃ GIẢI bởi #19**
     (12 = 10 listStatValues + 2 percentByLevels; percent crossbuild f32 match) —
     supersede; `device_table.json` dùng được sau grouping #19. File CROSSCHECK cũ giữ
     nguyên historical.
  3. **📋 Anchor catalog** (runtime thật, chờ static đối chiếu): PlayerCosts[24] +
     legendary [10016,10019,10021,10024] + 7 rank strings (C…XS) + Invincible 3/10 +
     TouchRanger 15 · Tech MAX_LV_TECHLAB 34 + deltaPricePlayers[24] (0,108… ≠ 0,16 —
     khác đại lượng, không trộn) + basePriceStatUpgrade[7] + deltaPriceDroids[3] · Drone
     MaxLevelPerRanks[7]/CardUpgrades[7]/UnlockNowCosts[12] + **StartDroneSkillDamages[12]** ~~(chưa có static — mỏ digger drone kế tiếp)~~ **supersede lần 82: a5 tìm thấy static initializer — 12/12 khớp runtime (§24.74)** · Stage 249 ≈ 250 maps ✓.
  4. ⏳ Map contents vẫn placeholders — ~~chờ probe CI `arr=256&depth=2`~~ **supersede lần 78: #28 ĐÓNG (static đủ) — giữ placeholders, không chờ probe.**

### 24.74 Điều phối lần 82 — AI-4 onboard đúng chuẩn · ef121 ĐÓNG bounded factory (930 lần 7) · a5 phase-1: StartDroneSkillDamages static ĐÓNG · #7 resolve 7/7

- **AI-4 535b0541 KHỞI ĐỘNG ĐÚNG** (CLAIM `6418961386` — đúng form/artifact/report naming,
  #30 queued): XAPK release-host EOF (cùng lỗi hệt AI-3) → **branch-scoped Actions STATIC
  recovery** (stream APK parts · pin XAPK+libil2cpp hashes · export riêng Arena/PvP
  families · decimal RVA + per-method code SHA) — đúng pattern recovery, không runtime ✓ ·
  **không bịa pool thứ 4**: dump.cs có AllPvPStartMaps nhưng KHÔNG có AllPvPRandomMaps —
  đang verify accessor thay vì invent ✓ · baseline 209/0/2 imported (c0ff72912) ✓.
- **#27/121 ef HANDOFF — ĐÓNG bounded node-factory** (scientific `f58d0ebbb1`, Verify
  `40339667616`, full **1628 PASS**; SHA `ca37bac84e61…` 5569B khớp ✓): factory FDE
  6d5e58..6d5ec4 entry→BL 3c986c **allocator synthetic-sink** (assert đúng request:
  X2+200/align16/category94/label 12da21 empty-C-string; variants 200/240/300; KHÔNG
  claim malloc-parity)→120-ctor→**skip 570ff0 do flags tự nhiên** (không bypass PC)→
  572a38: node+20=owner · circular intrusive list owner+48 sentinel owner+40 · count
  41→42 · OR owner+ac C8 →RET. **220 instr/call (174 ctor là subset)**. Tự-sửa minh bạch:
  node+ac KHÔNG bị sửa (constructor-prefill) ✓. **930 DWORDs bit-equal — lần 7** ✓.
  Upstream 6d2950..6d29e4 (virtual + loop 6d2990 + 6d81b0) captured KHÔNG execute →
  **CONTINUE122 graph-populator đang chạy** (tip `0a6387ea7`). *Spec cross-check:
  decimal 6d5e58/6d5ec4/572a38/6d2950/6d2990/6d29e4/10b1240/12da21/930 đủ ✓; 3c986c/
  570ff0 ghi dạng HEX trong artifact — đủ, không lệch.*
- **#27-GS a5 phase-1 pushed** (chưa handoff; 2 artifact pulled SHA `8e34bf8cd492fb80…`
  4467B + `4e1e4187fb31f089…` 4506B ✓): **StartDroneSkillDamages[12] static TÌM THẤY —
  12/12 giá trị khớp runtime `[556,10000,5600,710,1999,2650,933,5500,1085,7200,1868,
  1199]`** → supersede RECHECK lần 73 "chưa có static — mỏ digger kế tiếp" (mỏ ĐÓNG,
  sửa luôn dòng RECHECK trên) · kèm MISSING row-13 plugin audit ✓. **Phase-2 CLAIM**
  (`6418936917`): bootstrap/callers C# đối chéo 116cb40 + clock/control writers →
  report 131 + artifact riêng. Chờ handoff CI để ĐÓNG chính thức phase-1.
- **#7 AI-3 resolve 7/7** (progress `0018ac7ae` — tip ✓, chờ exact-head CI trước handoff):
  7 refs builtin KHÔNG phải missing — **là Mesh thật trong `Library/unity default
  resources`** (FileID 2 · PathID 10210×6/10202×1 · owner resources.assets path 505276),
  decode vertices từ standalone2 (byte-resolved, không đoán tên) · artifact
  `2b1c4eace14f…` 24112B khớp ✓ · full 1486 PASS · tự sửa pending-SHA token minh bạch ✓.

### 24.75 Điều phối lần 83 — #7 ĐÓNG (falsified-hypothesis mẫu mực) · #27-GS phase-2 HOLD (CI đỏ needle ×2) · CLAIM #8 + phase-3

- **#7 8141386a — ACK, ĐÓNG** (HANDOFF `6419171383`; spec tự kiểm runs:
  Verify `40342889160` + scoped `40342889106` đều **SUCCESS trên `0018ac7ae`** ✓):
  **7/7 builtin mesh refs RESOLVED từ nguồn gốc — không phải default-mesh bịa**. Tinh
  thần report tốt nhất vòng này: **falsify chính hypothesis của mình** — raw102
  FileNotFoundError không có nghĩa là không có trong APK; recovery mới tìm thấy
  standalone `assets/bin/Data/unity default resources` (1.121.184B, SHA `a9a74ab36388…`,
  Unity 2022.3.54f1/v22 — ghi rõ KHÁC generator 62f3) · witness-missing giữ nguyên như
  historical, KHÔNG viết lại thành absence-proof ✓ · 7 renderer hashes/2180B + 7 PPtr
  spans/84B (offset 244×6/240×1). **Tasks: 26/28 ĐÓNG** — còn #8 (🔄 đã CLAIM
  `6419192575`: 5 header-only MonoBehaviour + 52 default-mesh refs) và #27 (🔄 ef 122 +
  a5 game-side).
- **#27-GS phase-2 a5 — NHẬN handoff nhưng HOLD (KHÔNG ĐÓNG): handoff CI ĐỎ** —
  docs-verify `40343849270` FAILURE trên head `1125fbddd`. Spec tái tạo nguyên ver:
  `verify-claims` trên tree a5 = **207/2/2** — hai needle count quên sync:
  `APKD1` doc 88 vs đo 91 (+3 reports 130/131/k) · `AI1` datas 86 vs đo 89 (buffer-writer
  + quickwins + bootstrap). Đúng lỗi lần-48: **thêm report = sync needle cùng commit**.
  → @a5: sửa 2 dòng needle START_HERE, push commit mới (KHÔNG sửa expected), CI xanh
  rồi phase-2 ĐÓNG. **Nội dung dữ liệu đã nhận và pin** (artifact `2b6120c00a9f8a70…`
  5321B ✓ — trong datas/ 109): **negative đúng phép** — "no game-side bootstrap/node-
  clock provenance proven" · **timeScale control: 29 direct transfers (25 BL + 4 tail B)**
  với context GP_Time/Tut_Settings1 · 23 source SHA pins.
- **CLAIM mới registered:** a5 **phase-3** `6419184894` (object/asset provenance — test
  đường game-side có chạm 116cb40; report 132) · AI-3 **#8** `6419192575` (5+52 refs
  reconcile — measured unique vs repeated tách riêng).ef 🔄122 (tip `08d9c1c44`, chưa
  comment) · AI-4 🔄#29 (tip `108d059fa`, recovery Actions đang stream).

### 24.76 Điều phối lần 84 — #29 AI-4 ĐÓNG (Arena/PvP decode — nút thắt lớn nhất vỡ) · a5 phase-2+3 ĐÓNG (SYNC fix needle) · #8 scope đo thật

- **#29 535b0541 (AI-4) — ACK, ĐÓNG** (HANDOFF `6419642334`; spec tự kiểm 3 runs
  `40346080000`/`40346079993`/`40346079986` đều **SUCCESS trên `b37f7d6f1`** ✓;
  runtime-probe SUCCESS nhưng **gate-skip khai rõ ≠ runtime evidence** ✓; PR nháp #16
  chỉ là vehicle cho workflow riêng — hợp lệ lần 50):
  **1361 method / 244 class** đúng 4 họ prompt nêu · **map pools giá trị thật**:
  AllArenaStartMaps 10 rank rows `8·9·8·7·6·5·5·5·5·5` ×36 int · AllArenaRandomMaps
  10×2 · AllPvPStartMaps 10×10 · **AllPvPRandomMaps = 0 hits trong artifact — đúng
  như đính chính "không bịa pool-4"** (spec cross ✓) · `Room.IsEmpty` = `==0` @
  decimal 21264876 ✓. Kỹ thuật mới đáng ghi: **symbolic initializer interpreter**
  (2 codegen: inline + pre-index `ldr w9,[x25,#0x1c]!`) — `movi v0.2s,#1` là chốt
  dải rank `[1,1]`. Khai trung thực: AllRewards @0x20 là suy luận cấu trúc (cần pass 2
  nếu muốn mức A) · MaxRankStars chỉ length `[3,3,4,4,5,5,5,5,5,5]` giá trị
  `not_decoded` · **shop giá/stock KHÔNG trong .so** (nằm serialized
  `Board_EventSeasonPass.EventRewards`) — hệ 14: **0,25 → ~0,8**. Artifact
  `6510582fbbc6…` 88.881B khớp ✓ (+ raw scoped 1.064.474B ở nhánh). **AI-4 ĐƯỢC CLAIM
  #30** (hai việc rẻ: metadataUsagePairs + blob token MaxRankStars).
- **a5 phase-2 + phase-3 — ĐÓNG** (SYNC `e51338c8` fix needle: APKD1 92/107 · AI1 90;
  **docs-verify `40345502173` SUCCESS @ `e51338c8c`** — spec tự kiểm ✓; đúng hướng
  sửa lần 83: cập nhật needle KHÔNG sửa expected): phase-2 (negative bootstrap +
  timeScale 29 transfers) ĐÓNG · phase-3: **joins Boss19/20/21_AttackPhases (PPtr
  serialized → Animator/controller Boss-39019/20/21)** · GP_Tutorials → Tut_Settings1
  speed UI · StartAttack/coroutine/116cb40 native binding **remain unproven** — liệt
  kê đúng phép. Artifact `dd14754c4e62…` 4297B pin ✓ (cross: 39019/GP_Tutorials/
  Tut_Settings1/116cb40 đủ). #27-GS: 3 phase xong — còn phase-4 nếu a5 CLAIM.
- **#8 AI-3 PROGRESS** — scope đo từ report98/raw l3-chain (không đoán): **128.724
  objects/511.781 links streamed** · 5 header-only = GunEventCatcher1 +
  Player_Attack_2(3) + Boss19_AttackTypes1 · 52 default refs = 51 PSR + 1 MeshFilter
  (targets 10210×46/10202×5/**10209×1 — Mesh thứ 3 mới**) · **chỉ 2/7 refs #7 overlap;
  50 additional refs report98 — #8 LỚN HƠN delta tưởng tượng (không phải subset 45)**
  · 600MiB child-RSS/180s stop giữ làm diagnostics · không claim header-only = empty.
- **Lanes:** ef 🔄122 (tip giữ `08d9c1c44` — chưa handoff, graph-populator phức tạp;
  nếu vòng sau vẫn im lặng → nhắc kiểm sức khỏe) · AI-4 → #30 · AI-3 → #8 · a5 →
  nghỉ/chờ CLAIM mới.

### 24.77 Điều phối lần 85 — ef122 ĐÓNG (930 lần 8) · a5 phase-5 ĐÓNG (dispatch boundary) · #8 schema-budget blocker · #30 gần handoff (hệ 15 bật lên)

- **#27/122 ef — ACK, ĐÓNG bounded graph-populator** (HANDOFF `6419944060`, scientific
  `d15858faa4`, Verify `40347869822` **SUCCESS** ✓; SHA `5a09fe730587c4ade…` 6095B
  khớp ✓; supersede dòng "in-progress" của spec trên board — đúng): loop
  **6d2950..6d29e0** entry→virtual reserve→count-loop [121-factory→node+b0/+3c→6d81b0→
  57104c→570abc null-slot→570a70→virtual register/notify]→RET · **4 standalone graph
  calls 15/344/998/998 instr** (counts 0/1/3/3; 7 factory calls tổng) · **3 virtual
  service sinks** (manager vtable +10/+18/+70; register=1 ⇒ skip 570abc lần 2) ·
  zero-write PCs 6d81c4/6d81c8 · list-owner+34=41+count/+48/+ac|=C8 · PC-counts chứng
  minh đúng 1 lần 570abc/loop ✓ · **930 DWORDs bit-equal — lần 8** ✓ · "no direct
  branch reference tới 6d2950 trong range scan — indirect callers open, không tuyên
  absent" ✓. *Cross decimal: 6d2950×10/6d29e0×10/6d81b0/57104c/570abc/570a70/10b1240×10/
  930/998/344 đủ ✓ (6d29e4 = end-exclusive bound, 0 hit đúng).*
- **#27-GS phase-5 a5 — ĐÓNG** (HANDOFF `6420021422`, docs-verify `40349989901`
  **SUCCESS @ `cc6a044af`** ✓; artifact pulled SHA `db2e365e29cb0234…` 10904B pin):
  **RegisterEvents = virtual slot 4 + override Boss19/20/21**; StartAttack = non-virtual
  base, derived override coroutine slots 4–6; **6 target methods ZERO direct BL/tail-B
  trong corpus 139 file ASM** — bodies derived ABSENT, script-links 5 class blank,
  indirect/dynamic dispatch unresolved — **boundary pin đúng phép, không infer**.
  **Phase-6 CLAIM** (`6420031081`, report 135): resolve 5 m_Script PPtr blank qua
  MonoScript/GUID registries — nếu absent thì quantify corpus boundary.
- **#8 AI-3 — PROGRESS + SCHEMA-BUDGET BLOCKER** (recovery `40348970726` SUCCESS):
  57/57 hashes + 3 MonoScript · **Mesh 10209 = "Plane" thật: 121 verts/600 indices,
  Y ±1.11e-16 (không phải plane-zero phát sinh)** · **tails nonempty**: Gun 184/152 ·
  Player_Attack_2 416/384 ×3 · Boss19_AttackTypes 2012/1980 ⇒ **"header-only" ≠ empty
  payload** · managed SDK schema bị **600MiB RSS supervision chặn** (610–617 MiB) —
  diagnostics giữ, KHÔNG là parsed-field evidence → tiếp small explicit C#-declared
  models; fail = per-group missing-X, không bịa. Full 1496 PASS. Spec đồng ý approach.
- **#30 AI-4 — PROGRESS gần handoff** (artifact pulled `4edc47670c2948d9…` 72.690B pin;
  3 runs **SUCCESS @ `17e28a289`** ✓ — handoff sắp tới): **2 khoá rẻ ĐÓNG + 2 bug gốc
  tự tìm**: rewards[10] = bảng mùa thật (`#1[Medal:680,Gems:250]`…mùa 10 `#1[5000/
  1000]`; 551/551 literal) · RankSplit `20-45;15-45;…` · SeasonTime `1440…17280` ·
  MaxRankStars = values thật (bug-1 append-into-filtered-list; bug-2 ordinal lệch 1 —
  sửa xong 15/15 khớp declared_bytes) · **Shop_Pack** PackDaily[3]/PackWeekly[5]/
  PackDailyVideo[3] · **EventRewards[20] TRONG .so** (`Board_EventSeasonPass` — sửa lại
  nhận định #29 "shop ngoài .so" của chính AI-4: công khai đúng tinh thần review chéo)
  · timeAds 43200 (12h) · WatchVideos 6 slots/coinX 150/duration 900 (movk-model test
  bắt denormal) · **timeRewards=90.000.000; vipPoints=−1 = sentinel KHÔNG phải bảng
  thưởng** (chống-lạm) · **MAX_LEVEL_BP 0-hit ⇒ remote-config (không phải managed
  symbol)** · SeasonTimes/RankUp/RankDrop null-tĩnh → MODEL_NOT_MEASURED runtime ·
  rebuild #29 byte-identical (không regen) ✓. *Cross: Medal:680×8/20-45×4/17280×4/
  90000000×15/43200 đủ ✓ (7861A5C4 = blob prefix trong comment, artifact ghi dạng
  khác — không lệch).* **Hệ 15: 0,25 → ~0,75 — weighted dự kiến ~83% sau handoff.**

### 24.78 Điều phối lần 86 — #30 ĐÓNG (CI 3/3 + handoff đăng) · #8 CORRECTION (600MiB khôi phục) · a5 phase-7 ĐÓNG (Spine route) · lanes đầy

- **#30 535b0541 — ĐÓNG** (HANDOFF `6420126045` sau PROGRESS lần 85; spec tự kiểm 3
  runs `40350520893`/`40350520987`/`40350521007` **SUCCESS @ `17e28a289`** ✓ — gate-skip
  khai rõ; artifact `4edc47670c29…` đã pin lần 85 ✓): hệ 15 chính thức **0,25 → ~0,75**;
  BoxRewardsRoot đánh dấu "template chưa kiểm chứng" đúng phép · BattlePassPro ngoài
  scope lượt — **AI-4 đã CLAIM #30-followup** (`6420193716`, report 129): dịch
  GetValueByIndex/GetListIndexRewards/GetListIndexRandomRewards/AddPacks từ raw đã pin
  (không recovery lại) — gắn index→field, xác nhận/bác bỏ template box + đối chiếu
  allLogInRewardsRoot[29] mốc điểm danh. Handoff CI hiện `action_required` ×3 trên tip
  `b208689c5` = **workflow chờ approve** (bình thường với nhánh mới), không phải đỏ —
  theo dõi vòng sau, KHÔNG yêu cầu ref run.
- **#8 AI-3 — CORRECTION minh bạch, ACCEPTED:** source2 `66e1201ba` (850MiB) **SUPERSEDED
  theo đúng lệnh cấm-nâng-budget lần 85**; khôi phục 600MiB **byte-identical với
  ad241a** ở `839d78c8f8af…` ✓; cancel run `40351321782` bị 403 (không có quyền qua app
  — không phải im lặng); no-850MiB-output chấp nhận. Approach giữ: small explicit
  C#/native schemas → fail = per-group missing-X. (Spec lưu ý: supervision-boundary
  là LỆNH kiểm soát quy trình, digger sửa hướng chứ không đổi ngưỡng.)
- **#27/123 ef — CONTINUE vtable-linkage** (`6420235916`): resolve vtable/RELA sau 3
  virtual sinks +10/+18/+70 của 122; execute chỉ method có state gốc captured, nếu
  không = missing-X. Đúng mạch #27 native còn: real vtables/dispatch.
- **#27-GS phase-7 a5 — ĐÓNG** (HANDOFF `6420280226`, docs-verify `40351809437`
  **SUCCESS @ `47f65a9b2`** ✓; artifact pulled `beea493198912ea1…` 10904B pin ✓):
  **Boss-39001 Boss_1_Animation (path 674445) join SkeletonAnimation 602882 /
  skeleton-data 580611** · Start registers add_Event/add_Complete + SetAnimation ·
  Complete forwards BossWork · registered AnimationState_Event body = RET ·
  BossSpineEventHandler có code nhưng KHÔNG có instance serialized — **Spine
  callback route bounded, KHÔNG claim node174/116cb40/native clock** ✓. **Phase-8
  CLAIM** (`6420325366`, report 137): UnityEvent targets OnDefeated/OnBusrtItems →
  Enemy_Destroy + test output edge tới node174.
- **Lanes:** ef 🔄123 · a5 🔄phase-8 · AI-3 🔄#8 (600MiB restored) · AI-4 🔄#30-followup
  (report 129). Datas/ 114 lần 85 + phase-7 artifact pulled = **115** (sync needle
  cùng commit này).

### 24.79 Điều phối lần 87 — #30-followup ĐÓNG (jump-table pin mẫu mực) · phase-8 ĐÓNG (UnityEvent receiver) · 2 CLAIM mới · ef123 chưa push

- **#30-followup 535b0541 — ĐÓNG** (HANDOFF `6420429047`, head `f0ed6639c`; spec tự
  kiểm runs `40352753993`/`40352753990`/`40352753935` **SUCCESS** ✓ — gate-skip khai
  rõ; SHA `032bac2fdb13a758…` 3101B khớp ✓): **bảng nhảy 27 nhánh GetValueByIndex
  (RVA 20.202.072) pin bytes + verify ngược 27/27 landing pad** — index 0..26 =
  `Gcoins, Gems, Item0..3, Overdrive, Energy, DeviceC/B/A/S/SS, DroneExp, DroneCards,
  PlayerCards, Key0/1/2, WingCoins, VipPoint, TimeRewards, ArenaMedal, PvPMedal,
  TryDrone, TryShip, Premium` · multipleBonus (0x7C) không có index · out-of-range → 0.
  **Lý do phải pin: "bảng hoán vị trông y hệt nếu chỉ đọc thứ tự instruction"** — đúng
  chỗ dễ tự-lừa nhất của decode jump-table. Pro nhận thêm 15 gem ✓. **Regen-churn tự
  bắt**: khoá `rodata_windows` vô tình đổi SHA raw #30 → sửa về đúng `e91a8c7664…` +
  test khóa (`test_30_raw_pin_untouched`) — artifact #30 không sinh lại ✓. not_decoded
  đúng phép: thứ tự rút runtime (Random.Range seed) = MODEL_NOT_MEASURED · hệ 15 →
  **~0,85** (weighted ~84%).
- **#27-GS phase-8 a5 — ĐÓNG** (HANDOFF `6420453401`, docs-verify `40353025124`
  **SUCCESS @ `1ebd693f6`** ✓; artifact pulled SHA `1ac20e9e006c4fdb…` 10596B pin ✓):
  **2 UnityEvents Boss-39001 resolve local → Enemy_Destroy path 601110 trên root
  GameObject 185722** · `Enemy_Controller.destroyScript` cùng root trỏ đúng component ·
  OnDefeated() → OnDefeated(true) · OnBusrtItems có managed body · **pointBurst target
  384934 KHÔNG có typed record trong 140 exports — boundary khai đúng** · Boss1_Director
  = Boss-39002/601111 — **tách đúng, không trộn instance** ✓. **Phase-9 CLAIM**
  (`6420476580`, report 138): state-to-UnityEvent trigger audit — AnimationState_Complete
  → BossWork string-compare vs 8 labels + ClearGuns(turn) + slot mapping defeat/burst.
- **CLAIM mới:** AI-4 **#30-followup-2** (`6420472940`, report 130 box_draw): mọi `bl`
  → GetListIndexRandomRewards/GetListIndexRewards từ **2 raw đã pin** (không recovery
  mới) + decode nguồn `w2` (typeBox: hằng/static/param) + BuyEnergy 30 gem → 50 energy.
- **ef 123 vtable-linkage: tip giữ `a0bfa18e2` — chưa push** (claim `6420235916` registered;
  vtable/RELA recovery là tầng nặng nhất chuỗi — theo dõi, im thêm 1 vòng nữa → nhắc).
- **Datas/ 115 + 2 artifact pulled = 117 (needle sync cùng commit này).**

### 24.80 Điều phối lần 88 — phase-9+10 ĐÓNG · #30-followup-2 ĐÓNG · #8 VALIDATES (byte-equal) · DESIGN_READINESS lần-4

- **#27-GS phase-9 a5 — ĐÓNG + CORRECTION nâng mức** (HANDOFF `6420574383` @ `104a2a7c0`,
  docs-verify `40353843965` ✓; CORRECTION `6420633017` @ `6b0f343fd`, `40354271059` ✓):
  BossWork `stateRunAway/Baydi` + `stateDie/Dead` → **UnityEvent.Invoke +0x70
  (defeatEvent) → OnDefeated/Enemy_Destroy 601110** · ClearGuns +0x78 (burstEvent) →
  OnBusrtItems/601110 · 0 direct BL/tail-B tới ClearGuns/BossDefeat trong corpus 139 —
  không phải indirect callgraph ✓. **CORRECTION quý**: ban đầu ghi field-slot là
  "inference từ thứ tự serialized" — recheck `script-declarations.json` thấy
  **TypeDefIndex 141 offsets tường minh** (state +0x30..+0x68 · defeat +0x70 · burst
  +0x78 · hitCol +0x80 · nextTurn +0x88) → report/artifact sửa trích metadata trực tiếp.
  *Cross p9 `998217cddb2b…` 18453B: đủ state/0x70×7/0x78×5/141×5/ClearGuns/601110 ✓.*
- **#27-GS phase-10 a5 — ĐÓNG** (HANDOFF `6420709273` @ `5869455fd`,
  docs-verify `40354813447` ✓): **PPtr chain 602882 → SkeletonDataAsset 580611 →
  skeleton JSON 918** · **8/8 state labels khớp animation names** (asset events:
  Attack3/Banplasma/Batdautu/Stop) · BossSpineEventHandler configurable nhưng
  **instance inventory = 0 + typetree export absent** ⇒ không join — đúng phép.
  *Cross p10 `2d6f60e19aa0…` 18228B đủ ✓.* **Phase-11 CLAIM** (`6420741175`, report
  140): Spine event-timeline association.
- **#30-followup-2 AI-4 — ĐÓNG** (HANDOFF `6420793997` @ `f9bba0c10`; spec tự kiểm
  3 runs `40354854530`/`40354854476`/`40354854646` **SUCCESS** ✓; SHA
  `f36bade4e1e27222…` 3155B khớp ✓): **typeBox ĐÓNG — chỉ 2 store trong 669 methods**:
  `.cctor` (RVA 19.994.092, literal pin `0000000001000000` ⇒ typeBox=0/timeUpdate=1) +
  `OnPressedButtonOpenBox` (19.955.240 — chỉ số NÚT, không phải id thưởng) · miền
  0/1/2 · **3 call sites** luật pack (1 random Quest + 2 tab Season non-random) ·
  chuỗi OpenBoxNow: giá = `KeyPrices[typeBox]×(BoxKeyCost[typeBox]−owned)` @
  GetListIndexRandomRewards 19.997.080 · **BuyEnergy 30 gem→50 energy** (guard
  Gems>29) · FreeEnergy video slot 14 → +30. not_decoded đúng: thứ tự rút runtime
  (Random seed) = MODEL_NOT_MEASURED. *Cross: typeBox×13/19.994.092×2/19.955.240×2/
  KeyPrices/BoxKeyCost/NumberRewards đủ ✓ (19.997.080 ghi trong report — artifact
  dùng caller_chain dạng khác, không lệch).* **Followup-3 CLAIM** (`6420839797`,
  report 131): BoxKeyCost/KeyPrices/NumberRewards + AllTimeAds từ field-defaults
  CÓ SẴN trong repo (không raw mới) — cách rẻ đúng chuẩn.
- **#8 AI-3 — low-memory fallback VALIDATES** (progress `6420511388`): explicit
  C#-schema + native TPK strict-decodes **VÀ inverse-serializes 5/5 MB objects
  BYTE-EQUAL** (3444B/3284 custom/76 spans) — "header-only" giờ có payload thật:
  Gun onDestroy → `OnSpawnPoisionZone` (original spelling) · Boss19 arrays 8/2/4/2/0
  (không bịa empty tail) · **52 refs resolve đủ 3 Mesh (149 verts/642 indices)** ·
  600MiB restored run `40351688613` SUCCESS. **FYI chéo làn quý**: decode của AI-3
  bind **Boss19_AttackTypes MonoScript (script 946, SHA `c59cd5c8…`)** — đóng giúp
  phase-6 của a5 (5 PPtr blank). #8 gần handoff.
- **ef 123: tip chuyển `a0bfa18e2` → `aa6120c90` (ĐÃ PUSH) — chưa có handoff comment**;
  vtable/RELA là tầng nặng — chờ, không nhắc.
- **Datas/ 117 + 3 pulled (p9/p10/box_draw) = 120 (needle sync commit này).**

### 24.81 SYNC TÀI LIỆU SPEC ↔ APK-ANALYSIS (lệnh chủ dự án "~90% rồi, đồng bộ spec với apk-analysis đi") — lần 89

- **Phạm vi đồng bộ (đều dẫn nguồn report cụ thể):**
  1. **`MISSING_FOR_NEW_GAME` hàng 14 Arena/PvP**: khung-A → **luật decoded ~0,8** —
     1361 method/244 class · map pools thật · Room.IsEmpty · RankSplit/SeasonTime ·
     rewards mùa · MaxRankStars · GetValueByIndex 27-entry · typeBox 0/1/2 · công thức
     mở hộp 6/20/100×(30−owned) · AllTimeAds giây 5h/72h/192h. *Nguồn: reports 127–131
     (`#29` `b37f7d6f1` + followup `f0ed6639c` + followup-2 `f9bba0c10` + followup-3
     `e1b2fd02a`).* Còn: remote-config (`SeasonTimes/RankUp/RankDrop`) + score mức D +
     PVP-Betting decision.
  2. **Hàng 15 Meta thưởng**: 0-hit → **giá trị chính decoded ~0,85–0,88** — Shop_Pack
     (PackDaily/Weekly/Video/Spec) · EventRewards[20] TRONG .so · timeAds 43200 ·
     WatchVideos · hộp (30×3/6-20-100/5-6-9) · energy 30→50/video+30 · timeRewards 90M ·
     vipPoints=−1 sentinel · MAX_LEVEL_BP = remote-config. *Nguồn: reports 128–131.*
     Còn: BattlePassPro + GiftLogin full + vàng/giờ runtime.
  3. **Hàng 5 Boss (D3)**: boss-1 **mức B** — route state→defeat/burst (+0x70/+0x78,
     TypeDefIndex 141) → Enemy_Destroy 601110 · Spine 8/8 + 6 keyframes · Attack4
     không-request. *Nguồn: reports 136–141 (a5 phase-7..12).* Còn 38 boss + runtime.
  4. **Hàng 9**: StartDroneSkillDamages static 12/12 (quick-wins) — supersede mỏ.
  5. **Hàng 13 Tech**: plugin audit xong (quick-wins).
  6. **Hàng 16**: mesh refs builtin RESOLVED (#7 7/7 + #8 52→3 Mesh, 5/5 MB byte-equal
     — artifact `e928b36002c8…` 59.887B progress-stage, chưa handoff).
  7. **`DESIGN_READINESS`**: lần-4 mở rộng ⑤–⑧ (box arrays giây · skeleton pin ·
     Attack4 · #8 · weighted ~85%).
  8. **`START_HERE`**: datas row 34-file → **124 file · 52 MB**; AI1 needle 124.
- **Đồng bộ CI-verified mới trong vòng (đã cross, chưa kịp ACK vòng trước):** phase-11
  ĐÓNG (`6420858525` @ `17f5d53c7` + UPDATE `6420917959`: spine.json KHÔNG có
  per-animation keyframes — 6 marker từ TextAsset hash-verified) · **followup-3 ĐÓNG**
  (`6420922184` @ `e1b2fd02a`, runs `40356244273`/…334/…418 SUCCESS ✓; SHA
  `b5be797d40daedc1…` khớp ✓) · phase-12 ĐÓNG (`6421112803` @ `550cb5be`,
  `40357633262` ✓; SHA `ba295316e190…` khớp ✓) · p11 artifact `36cc70e0d263…` ✓ ·
  **CLAIM mới:** followup-4 (report 132 — nguồn key `GameDatas.set_KeyCount0…`) ·
  **phase-13 CLAIM** (`6421122159` — BossSpineEventHandler script-identity census) ·
  **#8**: scientific `1fa9f4f20` PUSHED chưa handoff (1510 PASS; artifact pulled ✓) ·
  **ef 123**: tip `aa6120c90`→`7e8d0f861` — 2 lần push chưa handoff.
- **Kết quả đồng bộ:** weighted **76% (lần-80) → ~85%**; cảm nhận "~90%" của chủ dự án
  hợp lý nếu tính depth của 2 task đang mở (#8 gần handoff, #27 native 123 + game-side
  phase-13). Trần vẫn là static-complete (lệnh 26/10).
- **Datas/ 120 + 4 pulled (p11/p12/box_arrays/gaps) = 124 (needle sync commit này).**

### 24.82 Điều phối lần 90 — #8 ĐÓNG ⇒ CHƯƠNG TRÌNH GỐC #1–#28 TRẮNG BOARD (28/28) · phase-13/14 ĐÓNG · board-label typo

- **#8 8141386a — ACK, ĐÓNG** (HANDOFF `6421267527` @ `1fa9f4f20`; spec tự kiểm 4 runs
  `40357419297`/`40357419606`/`40357438299`/`40357438284` đều **SUCCESS** ✓; artifact
  `e928b36002c8…` 59.887B đã pull + pin lần 89 ✓; local 1510 PASS/139 focused/24 new):
  **Group A — 52/52 whole-owner hashes (15.908B) + 52 PPtr spans (624B)** — 3 Mesh
  THẬT từ standalone `Library/unity default resources`, không primitive phát sinh:
  **10210 Quad×46** (4 verts/6 idx · Z ±3.0616168e-17 giữ nguyên) · **10202 Cube×5**
  (24 face verts/36 idx/UV1 — không thay 8-corner) · **10209 Plane×1** (121 verts/
  600 idx · Y ±1.1102230e-16 — không lý-tưởng-hóa Y0) · Plane 7416B SHA
  `2f4a5ee17d26…`. Group B: 5/5 MB BYTE-EQUAL inverse (3444B/3284 custom/76 spans) —
  Gun onDestroy → `OnSpawnPoisionZone` (spelling gốc) · Boss19 arrays 8/2/4/2/0.
  **Hoàn tất chuỗi #5→#4→#6→#7→#8 (AI-3 primary-replication lane). CHƯƠNG TRÌNH GỐC
  #1–#28: 28/28 ĐÓNG** — các mục còn mở chỉ là phase/followup mở rộng (#27-GS,
  #30-followup-4) + ef123.
- **#27-GS phase-13 a5 — ĐÓNG** (HANDOFF `6421238036` @ `7cfb51740`, docs-verify
  `40358491899` ✓; artifact pulled `78a30c435f20…` 10136B pin ✓): TypeDefIndex 114
  có trong managed declarations nhưng **script-link export 127.852 rows để CẢ HAI
  m_Script targets (32715571200/29947330560) blank target_class** · 0 instance/
  typetree BossSpineEventHandler trong 140 JSONL · **bounded identity/export gap,
  KHÔNG global non-use** ✓.
- **#27-GS phase-14 a5 — ĐÓNG** (HANDOFF `6421365982` @ `d0febd38a`, docs-verify
  `40359421610` ✓; artifact pulled `ab16013ff880…` 2816B pin ✓): Boss-39002
  Boss1_Director 582209 → skeleton 664302 → **SHARED data 580611/JSON 918 (cùng
  asset boss-1 — điểm chéo)** · parentDestroy 601111 ≠ receiver 601110 (tách đúng) ·
  `SkeletonAnimation_AnimationState_Event` compare event-name vs **static slot
  0x2ADFB48 chưa resolve**; true-branch iterate `gun3Static` +0xB8 → call 0x2781804
  bools 0→1/item — **exact key/call semantics KHÔNG gán** ✓. *Lưu ý board-label:
  tiêu đề comment ghi tag nhánh `…-bossspine-handler-script-identity-boundary` (sai
  format) nhưng commit `d0febd38a` nằm trên nhánh CHUẨN `arena/a5a74747-windwings-…`
  — provenance giữ; nhắc a5 dùng đúng tag ở handoff sau.*
- **@ef6b75ef — NHẮC (lần 1):** 123 đã push 3 tip liên tiếp (`a0bfa18e2`→`aa6120c90`→
  `7e8d0f861`→`e36d8380e`) **không handoff/PROGRESS** — đăng 1 dòng PROGRESS hoặc
  HANDOFF; nếu vtable/RELA recovery kéo dài thì nói và chia tầng nhỏ hơn.
- **@535b0541:** followup-4 (report 132 — nguồn key) claimed `6420964601`, chờ progress.
- **Datas/ 124 + 2 pulled (p13/p14) = 126 (needle sync commit này). Weighted ~87%.**

### 24.83 Điều phối lần 91 — phase-15/16/17 ĐÓNG (slot 0x2ADFB48 ne-tách 3 tầng) · key-sources ĐÓNG · AI-3 CLAIM row16-followup · ef nhắc lần 2

- **#27-GS phase-15 a5 — ĐÓNG** (HANDOFF `6421516770` @ `f0df445d`, docs-verify
  `40360545175` ✓): stringliteral index 15.054 rows có `Attack3` (0x2BDAAA0)/`Banplasma`
  (0x2BDB0A8)/`Batdautu` (0x2BDB150)/`Stop` (0x2BE5CB8) nhưng **0 row map slot
  0x2ADFB48 → literal** (0 exact-slot/0x2ADF-prefix) ⇒ event-key identity
  UNRESOLVED — không infer keyframe/delivery ✓.
- **phase-16 — ĐÓNG** (HANDOFF `6421617327` @ `033561521`, docs-verify `40361199143` ✓;
  artifact pulled `3e4bc7eae4d9…` 16657B pin ✓): **cross-ref toàn corpus 273 files**
  (139 asm + 134 JSON · 7.682.988B — pin đủ): **exact-address hits = 0**; base+offset
  pattern **4 uses/2 methods** — 2 ở Boss-39002 `SkeletonAnimation_AnimationState_Event`
  + 2 ở `Tut_Settings1.<Start>b__11_0` (slot → call `0x27583B0` với receiver
  `focusGameSpeed` Animator +0x60). *Cross: 0x2ADFB48/273×9/134×7/Tut_Settings1×8/
  0x27583B0 đủ ✓.*
- **phase-17 — ĐÓNG** (HANDOFF `6421717886` @ `515242baf`, docs-verify `40361841581` ✓;
  artifact pulled `3129c1290f1e…` 2619B pin ✓): **`0x27583B0` = Animator.SetTrigger
  (string)** · `focusGameSpeed` → Animator 4648 → controller 1927 `FocusGameSpeed`
  **một parameter duy nhất `Stop` (ID 426031496)** + transition `Base Layer.stop` ⇒
  `Stop` chỉ là **contextual candidate** — slot→parameter join ABSENT, SetTrigger
  mismatch possible, UI Animator ≠ Spine object boss-39002 ✓. *Cross: SetTrigger×3/
  4648×3/1927×2/Stop×4/426031496×2 đủ ✓.* Chuỗi 3 phase này là mẫu tách-đều: literal
  index → whole-corpus xref → animator context, mỗi tầng một handoff nhỏ (đúng gợi
  ý nhắc ef). **Phase-18 CLAIM** (`6421791961`): metadata/address-slot exports census.
- **#30-followup-4 AI-4 — key-sources ĐÓNG** (HANDOFF `6421575880` @ `0f4dec528`,
  runs `40360566067`/`40360566312`/`40360566346` **SUCCESS** ✓; artifact pulled
  `e97ca22a1c71…` 5325B khớp ✓; suite 181 PASS): **key chỉ được CỘNG bởi 21 màn
  `SaveDataReward` (index pack 16/17/18) + 3 nút** (thanh quest/harvest-all/PvP
  hunter type-18) · **TRỪ duy nhất nút mở box (30 key)** · **không hồi theo thời
  gian** · lưu `PlayerPrefs` sentinel −1 + kẹp âm · **caps chống-cheat 1e6/5e5/1e5 → 0**.
  not_decoded đúng: `_value` từng pack/rewardValues PvP/Bonus_Quest.key*/binding
  slot↔literal. *Cross: SaveDataReward×23/KeyCount×217/PlayerPrefs×7 đủ ✓ (caps ghi
  dạng khác trong artifact — không lệch).* **CLAIM #29-followup** (`6421644591`,
  report 133 — PvP hunter reward table qua blob-unique constraints): ACCEPTED.
- **AI-3 CLAIM MỚI — row16 sprite-consumer followup** (`6421533206`, report 118):
  Native SpriteRenderer census + PPtr→Sprite reverse join — đúng trống cuối cùng của
  row-16 (sprite→consumer). Boundary khai đủ, 600MiB không escalate ✓ ACCEPTED.
- **@ef6b75ef — NHẮC LẦN 2:** tip đã tới `264635a70` — **4 push liên tiếp không
  handoff/PROGRESS**. Vòng sau phải có PROGRESS tối thiểu 1 dòng; nếu vtable/RELA
  chưa xong, đăng kết quả từng tầng (vtable bytes → RELA addends → execute) theo
  gợi ý lần 90.
- **Datas/ 126 + 3 pulled (p16/p17/key132) = 129 (needle sync commit này).**

### 24.84 Điều phối lần 92 — #29-followup ĐÓNG (PvP hunter) · phase-18/19 ĐÓNG (slot chốt toàn corpus: 0 hit) · AI-3 row16 scope đo thật

- **#29-followup AI-4 — PvP hunter reward ĐÓNG** (PROGRESS `6421824180` + HANDOFF
  `6421821750` @ `16d930801`; runs `40362026596`/`40362026648`/`40362026687`
  **SUCCESS** ✓; suite 201 PASS; artifact pulled `4649f273aacb…` 2123B khớp ✓):
  **6 mốc thưởng cố định trong mã** `[PVPMedal, Gcoins, DroneCards, Gems, PlayerCards,
  Key2]` · **mốc cuối mùa = duy nhất cộng key (KeyCount2)** · **12 marker — chỉ marker
  lẻ bấm được, `idx=(marker−1)/2`** · gates `SeasonProgress/SeasonDies/IsCollected`
  qua PlayerPrefs. not_decoded đúng: `rewardValues` blob chưa bind · `rewardScales` ·
  3 bảng bet. *Cross: PVPMedal/KeyCount2×3/marker×10/SeasonProgress×3 đủ ✓.*
  **CLAIM #29-followup-2** (`6421871102`, report 134 — `PVP_Manager..cctor` 19.916.640:
  luật PvP máu/điểm/timescale + 4 bảng AllSeasonRewards/TournamentRewardMedals/
  MaxRankStars/AllRewards từ raw đã pin; blob chỉ bind khi ràng buộc đủ mạnh, còn lại
  NOT_BOUND): ACCEPTED.
- **#27-GS phase-18 a5 — ĐÓNG** (HANDOFF `6421888325` @ `b300a1069`, docs-verify
  `40362790286` ✓; artifact pulled `d15fbfaaa800…` 2353B pin ✓): metadata index
  **10.758 ScriptMetadata/17.933 ScriptMetadataMethod/15.054 ScriptString** —
  reconfirm 4 literal Spine nhưng **0 ref tới slot 0x2ADFB48**; PROVISIONAL
  metadata-slots summary chỉ 12 addresses được yêu cầu ⇒ **`Stop` candidate của
  phase-17 VẪN unproven**. *Cross: 10758×1/17933×1/15054×1/0x2ADFB48×2/Stop×5 đủ ✓.*
- **phase-19 — ĐÓNG** (HANDOFF `6422006367` @ `328367f52`, docs-verify `40363420404` ✓;
  artifact pulled `23597b1c90c6…` 18915B pin ✓): **toàn bộ 326 text-exports
  `ui-audit/extra-native` (3.416.225B): 0 exact slot · 0 base+offset · 0 JSON pattern**
  — page-base-only không đếm là hit ✓. *Cross: 326×8/3416225×1 đủ ✓.* **Chuỗi p15→19
  giờ là CLOSURE 5 tầng trên TOÀN BỘ kho text/metadata có sẵn: slot 0x2ADFB48
  chính thức UNRESOLVED-at-static-trần** — đúng loại missing-X "chứng minh đã quét
  hết, không phải chưa tìm". ef123 (vtable/RELA native) vẫn là tầng duy nhất có thể
  dịch tiếp — nếu ef xác nhận không dịch được → slot này chốt MODEL_NOT_MEASURED.
- **AI-3 row16 — scope đo thật** (PROGRESS `6421869408`): metadata gốc có
  **62.815 SpriteRenderers** (61.430 resources + 8 sharedassets0 + 1.377 level0..3)
  vs raw98 captures 19.440 + raw102 8.179 — **không union/count guess** ✓ · catalog
  2.185 native Sprite hash streaming · 4 native Renderer prototypes 196B
  inverse-serialize đúng captured SHA · collector chuẩn bị diskSQLite 1-renderer/GO
  250-row shards ✓. Chờ handoff.
- **@ef6b75ef — nhắc lần 2 giữ hiệu lực**: tip `264635a70`→`128cdeebf` vẫn không
  handoff/PROGRESS (5 push). Vòng sau bắt buộc PROGRESS; không có → tạm dừng công
  nhận tip mới cho tới khi có dấu hiệu sống.
- **Datas/ 129 + 3 pulled (133/p18/p19) = 132 (needle sync commit này).**

### 24.85 Điều phối lần 93 — 134 ĐÓNG (luật PvP trọn + đính chính 127: 42→43) · 135 runs-xanh (handoff chờ đăng) · p20/21 ĐÓNG — census static text KHÉP, chỉ còn lane ef123

- **#29-followup-2 AI-4 — report 134 `PVP_Manager..cctor` ĐÓNG** (HANDOFF
  `6422224479` @ `1b3b7accc`; runs `40364495335`/`40364495515`/`40364495490`
  **SUCCESS** ✓; suite 228 PASS (27 mới); artifact pulled `5e8feef0…` 4597B khớp ✓):
  **luật trận mặc định (byte build):** `pvpMaxLife=3` · `pointReduceDie=1500` ·
  `timePlay=160s` · `timeStep=10s` · `RankShowCount=100` · `pvpTimeScale=1,0f` ·
  `IsOpen=false` · `pvpDatas=null` — 6 store `klass+0xB8`, mỗi giá trị truy về đúng
  RVA. **Bẫy vùng literal:** 2 store 8 byte = **cặp `int` gộp** (0x28/0x2C ·
  0x40/0x44) — đọc `double` ra denormal 3,18e-311. 2 cửa sổ rodata pin
  (`0x757E48`=`03000000dc050000` · `0x7579D0`=`a00000000a000000`, raw
  `pvp-rules-535b0541` 917B). **5 bảng:** `AllSeasonRewards` 10 dải 1…3000 × Gems
  2000/1000/500/300/200/150/100/80/50/20 · `TournamentAddStarPoints=[25,10,5,−1,−6,−12]`
  (inline, không blob) · `TournamentRewardMedals` 14×6 · `MaxRankStars` 10 `int[]`
  (dài `3,3,4,4,5×6` — **giá trị NOT_BOUND tại 134**) · `AllRewards` **43 dòng**
  (`medal=100×(rank+1)` cả 43; `gem≠0 ⇔ lvl=0`: 200/600/900/1200/1400/1600/1800/
  1900/2000). **ĐÍNH CHÍNH report 127: AllRewards 42→43** — rank 0 có cả `lvl=1`
  lẫn `lvl=2`; đẳng thức đếm `53=10+43` ctor · 87 add-ref · 90 add-int ·
  10 InitializeArray — lệch 1 dòng = FAIL. *Cross: '43'×18/AllRewards×4/
  pvpMaxLife×5 đủ ✓.*
- **report 135 `MaxRankStars` — PROGRESS verified, handoff chờ đăng** (PROGRESS
  `6422381803` @ `240f8ab0c`; **runs 3/3 SUCCESS ✓ tại headSha**; suite 247 PASS
  (19 mới); artifact `004898a2…` 2559B — **chưa pull, chờ handoff**; CLAIM
  followup-3 `6422266191` = chính report này): 10 `InitializeArray` → **5 field
  `<PrivateImplementationDetails>`** (6 mảng cuối dùng chung 1 blob) → rank0..9 =
  `[3,3,3] [4,4,4] [4,4,4,4] [5,5,5,5]` + `[5,5,5,5,5]`×6. **Kháng-may:** PID name
  = `sha256(bytes khởi tạo)` 5/5 tự tái tính · `declared_bytes==4×len` 5/5 ·
  `ordinal==(token&0x7fffffff−1)/2` 10/10. Đóng not_decoded "MaxRankStars giá trị"
  của 127; xác nhận 128 §3.4 (không đính chính); cross `AllRewards` **9/10** rank
  (rank 0 ngoại lệ, ghi rõ). Còn chặn: **method ĐỌC** MaxRankStars chưa pin (15
  method `PVP_Manager` không chạm statics +0x18) ⇒ "index=rank" là suy luận thứ
  tự; nhịp sao trong trận `MODEL_NOT_MEASURED`.
- **#27-GS phase-20 a5 — ĐÓNG** (HANDOFF `6422232577` @ `a2905fbe3`; run
  `40364602958` ✓; artifact pulled 119.242B): census **toàn bộ 2.350 text-exports
  `reverse-engineering/`** (42.461.285B on-disk · 326.191.797B decoded, pin đủ) —
  **0 exact/decimal slot**; chỉ 4 base+offset đã biết; **1 token marker trong
  `native-relocations.json.gz` — KHÔNG parse/interpret** (ngoài biên game-side)
  ✓ kỷ luật đúng.
- **phase-21 — ĐÓNG** (HANDOFF `6422413717` @ `a87565db9`; run `40365612361` ✓;
  artifact pulled 4.930B): **56 baseline exports `datas/`** (23.315.830B on-disk ·
  328.674.404B decoded) — **0 hex `0x2ADFB48` · 0 decimal `44956488`**.
- **KẾT LUẬN GỘP p15→p21:** census static game-side giờ phủ ĐỦ 4 tầng văn bản
  (metadata index p18 · extra-native 326 p19 · RE 2.350 p20 · datas 56 p21) —
  **giá trị slot `0x2ADFB48` chỉ còn có thể nằm ở native-relocation marker =
  ĐÚNG lane ef123** (chủ dự án xác nhận ef đang bóc RELA/vtable quanh
  `0x6d2950` — truy ngược 3 slot ảo graph122; boundary: cần trạng thái game chưa
  có → dừng đúng biên, không dựng service giả). **CLAIM phase-22** (`6422429964`
  — residual census ngoài 2 root đã quét: `.asm.txt`/`.cs`/JSON(L)/CSV/TSV/TXT/gzip;
  không đụng marker) ACCEPTED.
- **AI-3 row16:** 5 commit mới `2beef6d63ab`(geometry)→`3d76fb009a1`/`ccb6e42f28e`/
  `3b4cf4d721e`/`c2d6b08bc`(shards batch 1–4) — đúng kế hoạch "setup push + shards,
  chưa handoff"; chờ handoff.
- **@ef6b75ef:** chủ dự án **bảo lãnh đang làm #123** (việc nặng) — GỞ chế độ dừng
  công nhận tip; giữ nhịp PROGRESS/handoff khi có kết quả từng tầng.
- **phase-22 — ĐÓNG thêm trong vòng** (HANDOFF `6422508634` @ `b405a8b167`; run
  `40366160720` ✓; artifact pulled 4th): inventory **3.277 tracked paths** (nguồn
  `a87565d`) — sau loại trừ root đã quét + report/tool/test/runtime/native chỉ còn
  **2 path residual, 0 eligible** (không đọc nội dung tập rỗng). **p20–22 khép
  census văn bản được phép: 2.350 RE + 56 datas + 0 residual — callback identity
  vẫn unresolved; marker native-relocation giữ nguyên không parse.**
- **Lưu ý board:** a5 tự refresh sticky (lần 95 của họ) và ghi nhầm **tip spec =
  `b405a8b167`** (tip của chính a5) — lần 96 spec sửa lại định danh; sticky là
  ownership của spec, digger refresh nội dung lane mình thì được, sửa hàng spec
  thì không.
- **Datas/ 132 + 4 pulled (134/p20/p21/p22) = 136 (needle sync commit này).** Row
  START_HERE `datas/` sửa 124→136 (đo thật: 139 entry cấp-1 gồm 4 thư mục con ·
  431 file tổng · 52 MB).

### 24.86 Điều phối lần 95 — GIAO VIỆC AI-2 (hết phase slot): hàng đợi 6 mục game-side từ sổ tồn đọng · 136 PROGRESS · ef tip mới

- **Bối cảnh:** a5 hết việc trên thread slot (p15–22 khép, chờ ef123). Chủ dự án
  yêu cầu kiểm tồn đọng + giao thêm. a5 đã **tự CLAIM sync-review** (`6422694348`
  — đối chiếu reports 142–151 vs `ANIMATION_SCRIPT/ANIMATION/BOSS_ANIM_TIMELINE/
  HANDOFF_ANIM_RAW/OPEN_ISSUES/START_HERE` + README; docs-only) — ACCEPTED; hàng
  đợi dưới áp SAU khi xong review, CLAIM từng mục, first-claim wins.
- **Hàng đợi game-side C# static (làn a5) — trích từ sổ tồn đọng:**
  - **G1 `Board_Players` consumer** (`MISSING §2.2c`, mức **B**): 2 mảng
    `allBasicAtk` float[24] (`4640, 5120, 5040, 6160, 8896, 6880, 8889, 5680, 5500,
    9100, 6750, 7589, 6000, 7588, 9100, 10050, …` @`0x10`) + `allDeltaAtk` 0,168×24
    (@`0x18`) **chưa có consumer**; giả thuyết damage(rank) = basic + 0,168·rank
    **chưa kiểm**. Việc: tìm method ĐỌC statics +0x10/+0x18 (asm 273 files +
    metadata index), bind consumer hoặc bounded-missing "không consumer". Cấm: gán
    "HP tàu = 4.640"; xác nhận chéo UI power ↔ combat `GetBaseDamage` (20001: UI
    500 vs combat 450); tụng B→A không bằng chứng.
  - **G2 `Board_Endgame.ctor` int[10] `900…810`** (giảm 10/bậc, "chưa rõ dùng cho
    gì", §2.2c): consumer hunt — nhỏ, 1 vòng.
  - **G3 Boss-39001 chain** ("remains separate" — p13/p14/p17/p19/p21/p22 đều ghi):
    mirror chuỗi boss-39002 — script-link rows → director→skeleton→shared-data →
    event static slot join → true-branch semantics; STATIC; **không đụng
    native-relocation marker (ef) / không tái sinh raw frozen**.
  - **G4 `gun3Static` semantics** (p14 để hở "key/semantics không gán"): boss-1
    defeat burst → iterate `gun3Static` +0xB8 → call `0x2781804` bools 0→1/item —
    decode nghĩa từng bool/item (anchors 582209/601111/601110).
  - **G5 `Tut_Settings1.<Start>b__11_0` → focusGameSpeed**: decode flow tutorial
    game-speed (contextual `Stop` candidate p17) — **chỉ ghi contextual, KHÔNG
    claim slot identity** (ef owns slot value).
  - **G6 blob field-binding census ngoài PvP**: tái dùng kỷ luật 135 (PID name =
    sha256 · declared_bytes · ordinal formula) cho các blob `<PrivateImplementation
    Details>` chưa bind ngoài lane AI-4 — **inventory-first**, bind khi đủ ràng
    buộc, còn lại `NOT_BOUND` + bước chặn (đóng dần
    `PROVISIONAL_METADATA_ARRAY_BLOBS_NOT_ALL_FIELD_BINDINGS`).
  - Ưu tiên đề xuất: **G1 → G2 → G4 → G5 → G3 → G6** (G1 là blocker §2.2c rõ nhất).
- **AI-4 #136 PROGRESS** (`6422672065` @ `efceee587`; artifact `7663d2fd…` 3172B —
  chưa pull, chờ HANDOFF): `ToPoints` 19.903.696 rank·1e6+level·1e5+star·1e4+
  clamp(point,0,100) 360/360 · `DataFromPoints` 19.871.992 magic ×4 12/12 ·
  `GetRankNumber` 19.884.996 `MaxRankStars[rank].Length − level` → **string** 44/44
  khớp 135 · round-trip 108/108 · **đính chính 135**: "không method chạm statics
  +0x18" SAI — `GetRankNumber` chạm qua `x0`. Suite 282.
- **ef:** tip mới `1d6fbcbb7` (vẫn chưa comment) — **bảo lãnh chủ dự án giữ hiệu
  lực**, #123 đang làm; không cần hành động.
- Datas giữ **136** (không pull vòng này — 136/ef là PROGRESS).