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
| "`enemies` trong wave **toàn bộ là `?`** (45.659)" | D | **22.462 entry**, **`?` = 0**, **109 prefab** | **A** |
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
| Spawner (đã dedup) | **11.099** (bản `8c6da25`; 11.093 ở `cd0372d`) |
| Entry enemy | **22.462** |
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
| Spawner sau dedup | 10.776 | **11.099** | 🟡 lệch **3%** (khác khoá dedup) |
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
> Nghĩa là **957 `static` field vẫn ở mức D** — chưa có giá trị nào.
>
> Đồng thời: chính `docs/conclusions.md` của nhánh kia xếp mục #12 ở mức **"B→C"**,
> và ghi *"cần đọc control flow, không chỉ hằng số"*.

---

## 6. Cái tôi phải rút lại — và cái **không** đổi

### 6.1 Rút lại

| Câu tôi viết | Vì sao sai |
|---|---|
| "0 `AudioClip` export được" | **69/69** export được, 571 s |
| "enemy trong wave không resolve được" | **22.462** entry, 109 prefab, 0 `?` |
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
| **957 `static` field chưa có giá trị** | ✅ **vẫn đúng** — bước IL2CPP thất bại |
| **4.861 `[SerializeField]` chưa có giá trị** | ✅ **vẫn đúng** — chưa ai chạy AssetRipper |

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
> `datas/waves.json` (22.462 entry) **không** bị ảnh hưởng: sinh bởi `wave_report.py`, script này không cap.

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
| `sum(len(listPrefabEnemies))` | **22.483** |
| `sum(len × copies)` | **45.659** |
| Khớp `45.659` đã ghi ở §7.13? | ✅ **chính xác 100%** |
| Spawner `copies = 2` | 9.790 / 11.099 |

⚠ **Trung thực về mức mới:** công thức `len(enemies) × copies` **đã có** trong `GAMEPLAY.md`.
Cái mới ở vòng này là **phép kiểm số học**: 22.483 × copies ra **đúng 45.659**, khớp con số đếm
độc lập từ `Call_Data` — nên `45.659` nay là **mức A**, không còn là *"mức B"* như nhánh dữ liệu
ghi trong `CROSS_BRANCH_20330d0e.md` §2.

⇒ **45.659 = quân thực tế**, **22.483 = quân khai báo**. Cả hai đúng, khác phạm vi — từ nay ghi rõ.

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
| 1 | Giá trị **957 `static`** | **D** | vòng 3 chạy nhưng **thu được 0 hằng số** (lỗi truyền `"ls"`) |
| 2 | Giá trị **4.861 `[SerializeField]`** | **D** | chưa chạy AssetRipper; prefab vẫn chưa đọc |
| 3 | **Đơn vị đếm** của "tổng HP boss" | **C** | 2 lần chạy lệch 11–71% — phải chốt đếm root hay đếm bộ phận |
| 4 | 23 `SoundClip` không có clip | **D** | 92 khai báo vs 69 thật |
| 5 | Loop point của 8 track nhạc | **D** | không có trong index |
| 6 | Pivot / border sprite | **D** | `sprites-index.csv` chỉ có `bytes`, không có `rect`/`pivot` |
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
| `_index.csv` | **797 instance · 117 lớp · 146.797 node · 5.831 nút** | `UI.md` §9 — độ sâu bố cục từng màn; giải thích luôn vì sao **117 ≠ 125** |

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
