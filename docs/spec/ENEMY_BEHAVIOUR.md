# ENEMY_BEHAVIOUR — di chuyển, hướng, đường bay, thiên thạch

> Vòng 2 (bổ sung). Nguồn sự thật: `reverse-engineering/scriptableobjects/*.csv`
> và `docs/apk-analysis/Enemy_Movement.csv`. Mỗi bảng ghi `(nguồn: <file>)`.
> Suy đoán đánh dấu `> Giả định:`.

File này trả lời câu hỏi mà `ENCOUNTERS.md` **không** trả lời được: *wave có bao nhiêu
spawner thì đã biết (`ENCOUNTERS.md`), nhưng enemy **bay thế nào**?*

---

## 0. TL;DR

| Chỉ số | Giá trị | Nguồn |
|---|---:|---|
| Instance `Enemy_Movement` | **981** (982 dòng CSV gồm header — đo lại 25/10 trên bản hiện hành) | `Enemy_Movement.csv` |
| Tốc độ di chuyển (`listSpeeds[0]`) | **0,2 – 30,0**, median **5,0** | `Enemy_Movement.csv` |
| Tốc độ phổ biến nhất | **5,0** (562/981 = 57,3% — đo lại 25/10) | `Enemy_Movement.csv` |
| Enemy **đứng yên bắn** (`isTurret`) | **112 / 981 (11,4%)** — đo lại 25/10 | `Enemy_Movement.csv` |
| Enemy có **≥2 tốc độ** (đổi tốc giữa chừng) | **137 / 981 (14,0%)** — đo lại 25/10 | `listSpeeds[1]` |
| Quay mặt theo hướng bay | `facingMove = True` **949 / 981 (96,7%)** — đo lại 25/10 | `Enemy_Movement.csv` |
| Khoá góc (không xoay) | `fixedAngle = True` **13** | `Enemy_Movement.csv` |
| Đường bay (`PathCreator`) | **399** path, **16** độ dài khác nhau | `PathCreator.csv` |
| Toạ độ đường bay | ❌ **không có** — chỉ có số anchor | `PathCreator.csv` |
| Spawner con (point/path/rocket/…) | 6 loại, **5 loại 0 cột dữ liệu** | `*_Spawner.csv` |
| Thiên thạch | **517** generator, chu kỳ 2–5 s, X −7…5, Y 12/15 | `MeteoriteGenerator.csv` |

---

## 1. `Enemy_Movement` — **981** instance (đo lại 25/10), 5 tham số thật

### 1.1 Phân bố tốc độ

| `listSpeeds[0]` | Số enemy | % | Ghi chú |
|---:|---:|---:|---|
| **5,0** | **473** | 59,1% | tốc độ chuẩn của game |
| 1,0 | 97 | 12,1% | chậm |
| **20,0** | 87 | 10,9% | lao nhanh gấp 4× |
| 3,5 | 61 | 7,6% | |
| 0,8 | 42 | 5,3% | rất chậm |
| 1,2 · 1,5 · 30,0 | 16 · 4 · **8** | 3,5% | 30,0 = nhanh nhất |
| Khác | 12 | 1,5% | |
| **Tổng** | **800** | 100% | |

Nguồn: `Enemy_Movement.csv` cột `listSpeeds[0]`, làm tròn 1 chữ số.

### 1.2 Tốc độ theo nhóm prefab

| Nhóm (theo root `_gameobject`) | n | Min | Median | Max |
|---|---:|---:|---:|---:|
| `Boss-xxxxx` | 170 | **0,2** | 5,0 | 20,0 |
| `Wave_NNNN/...` | 204 | 1,0 | **3,5** | **30,0** |
| Khác (prefab lẻ, `Boss`, `Body`…) | 426 | 0,8 | 5,0 | 20,0 |

Nguồn: `Enemy_Movement.csv`, nhóm theo tiền tố `_gameobject`.

> **Đọc ra:** enemy trong wave bay **chậm hơn** boss (median 3,5 vs 5,0) nhưng có
> **tốc độ đỉnh cao hơn** (30 vs 20) — đúng kiểu "enemy lao qua màn" so với "boss di chuyển
> có kiểm soát". Khi clone: đặt **nền 3,5**, boss **5,0**, và giữ **1-2 loại 20–30** làm
> "đòn bất ngờ".

### 1.3 Cờ hành vi

| Cờ | True | False | Nghĩa |
|---|---:|---:|---|
| `isTurret` | **95** | 705 | **đứng yên, chỉ xoay để bắn** — 51 ở prefab lẻ, 44 trong `Wave_*`, **0 ở boss root** |
| `facingMove` | 775 | 25 | xoay sprite theo hướng bay (mặc định) |
| `fixedAngle` | 13 | 787 | giữ nguyên góc, không xoay |
| `endOfPathInstruction` | `2` ×752 · `0` ×48 | — | enum: dừng / lặp / xoá — **2 là mặc định** |
| `typeMoveEnded` | `0` ×750 · `1` ×50 | — | hành vi khi hết đường |
| `border.w` | **15,0** ×799 · 25,0 ×1 | — | **bán kính va chạm = 15 unit**, khớp `Bullet_Linearly.border.w` |

Nguồn: `Enemy_Movement.csv`.

> **15 unit là hằng số va chạm của toàn game**: đạn 15, enemy 15 (799/800). Chỉ 1 enemy
> dùng 25. Dùng đúng số này thì cảm giác "trúng/trượt" sẽ khớp bản gốc.

### 1.4 Hệ toạ độ thế giới (cùng với `ENCOUNTERS.md`)

| Mốc | Giá trị | Nguồn |
|---|---:|---|
| `y_spawn` mép trên | **9,6** (65,2% spawner) | `waves.json` |
| `y_spawn` ngoài màn | 12,0 (17,2%) | `waves.json` |
| `border` enemy (`Vector4` w/x/y/z) | **15,0 / −10,0 / 10,0 / −15,0** | `Enemy_Movement.border` |

`border` là **Vector4 = (w, x, y, z)** với giá trị gần như tuyệt đối:
`w = 15,0` (799/800) · `x = −10,0` (799) · `y = 10,0` (799) · `z = −15,0` (687) hoặc `−25,0` (113).
Biến thể duy nhất khác: `25 / −20 / 20 / −25` (1 dòng).

> **Giả định:** đây là **biên dựng của vùng chơi** (không phải hộp va chạm): ngang
> **−10…10 = 20 unit**, dọc **−15…10 = 25 unit**, `w` là nửa chiều rộng dùng cho wrap/despawn.
> Khớp với `y_spawn` 9,6–12 (mép trên) ⇒ vùng chơi cao **~25 unit**, rộng **20 unit**,
> tỉ lệ **4:5** (dọc). Đây là bộ số đủ để dựng camera orthographic đúng khung (`ASSETS.md` §3).
> Cần xác nhận bằng cách đo `Camera.orthographicSize` trong scene — chưa có trong CSV.

---

## 2. `PathCreator` — 399 đường bay, **không có toạ độ**

| Số anchor | Số path | % |
|---:|---:|---:|
| **7** | **254** | 31,8% |
| **10** | **174** | 21,8% |
| **16** | **111** | 13,9% |
| 4 | 91 | 11,4% |
| 13 | 83 | 10,4% |
| 28 | 25 | 3,1% |
| 19 | 16 | 2,0% |
| 34 | 12 | 1,5% |
| Khác (8 giá trị) | 34 | 4,3% |
| **Tổng** | **981 dòng** (đo lại 25/10; "399 path" là đo từ bản 800-cũ — CSV không có cột path để đếm lại) | 100% |

Nguồn: `PathCreator.csv`, cột `editorData._bezierPath.points` (mảng chỉ serialize **độ dài**).

> ⚠ **Đây là giới hạn cứng:** CSV có 30 cột của `editorData` nhưng **không có
> `points[i].x/y`** — chỉ có `localPosition`, `pivot`, `perAnchorNormalsAngle` và các cờ
> gizmo. Nghĩa là ta biết *"đường bay này có 7 điểm"*, **không biết nó cong thế nào**.
>
> Muốn lấy hình học path phải **parse binary `data.unity3d`** (MonoBehaviour
> `PathCreator` → `VertexPath`), không đọc CSV được.

**Hệ quả cho clone:** phải **tự thiết kế lại toàn bộ đường bay**. Cái giữ lại được chỉ là
**phân bố độ phức tạp**: 54% path có 7–10 điểm (đơn giản), 14% có 16 điểm, 5% có ≥19
(phức tạp). Dùng phân bố này làm *ngân sách công cụ path editor*.

---

## 3. Spawner con — 6 loại, gần như **rỗng**

| File | Dòng | Cột dữ liệu thật | Kết luận |
|---|---:|---:|---|
| `Spawner.csv` | 800 | **0** | chỉ có ref, không có tham số |
| `PointToPoint_Spawner.csv` | 800 | **0** | " |
| `Path_Spawner.csv` | 800 | **0** | " |
| `AirFree_Spawner.csv` | 800 | **0** | " |
| `PinMap_Spawner.csv` | 800 | **0** | " |
| `Waypoints_Spawner.csv` | 800 | **0** | " |
| `Rocket_Spawner.csv` | 800 | 1 | **`typeRocket`: `1` ×421 · `3` ×235 · `0` ×144** |

Nguồn: 7 file `*_Spawner.csv`, đếm cột có giá trị số biến thiên (bỏ `m_*`, pathID).

> **Đọc ra:** toàn bộ tham số spawn (thời gian, tốc độ, hướng, số lượng) **không serialize**;
> chỉ `Rocket_Spawner` còn 1 enum. Vì vậy `ENCOUNTERS.md` §1.5 (`rate`/`speed`/`y_spawn`
> đọc từ `waves.json`) là **nguồn duy nhất** cho nhịp spawn — đừng tìm thêm trong CSV.

---

## 4. `MeteoriteGenerator` — 517 generator, 4 tham số thật

| Tham số | Giá trị | Số dòng |
|---|---|---:|
| `minY` / `maxY` | **12,0 / 12,0** · **15,0 / 15,0** | 538 · 262 |
| `minX` / `maxX` | **4,0 / 3,0** · 5,0 / 2,0 · **−7,0 / −1,0** · −5,0 / −2,0 | 138 · 137 · 135 · 133 |
| `minmaxSpdMove` | x `0,7–1,7` / y `1,0–2,0` | 800 |
| `minmaxSpdRotate` | **−15…15** (530) · −25…25 (270) độ/giây | 800 |
| `minmaxTime` | **2–4 s** (270) · 3–5 s (268) · 2–1 s (262) | 800 |
| `minmaxColor` | x 0,0–1,0 / y 0,3–0,8 (biến thiên màu) | 800 |

Nguồn: `MeteoriteGenerator.csv` (**852** dòng / **577** object — đo lại 25/10).

> **Đọc ra:** thiên thạch rơi **từ trên xuống (Y 12 hoặc 15)**, trong **2 dải X**:
> bên phải (2…5) và **bên trái (−7…−1)**. Trong 517 object đã đọc, **không có giá trị nào**
> rơi vào khoảng (−1…3) — nên thực tế thiên thạch chỉ rơi 2 bên mép, không rơi giữa màn.
> Đây là chi tiết thiết kế: chừa "đường sống" ở giữa cho người chơi.
> Tốc độ rơi 0,7–2,0 + xoay ±15…25°/s.

---

## 5. `Boss4_ExplosionTimer` — 138 object, nhịp nổ

| Tham số | Giá trị | Số dòng |
|---|---:|---:|
| `idFx` | **91003** ×118 · 91008 ×21 · 91006 ×16 | 155 |
| `timeMin` / `timeMax` | **0,5 / 6,8** (69) · 0,25 / 1,75 (29) · 0,0 / 0,0 (15) · 1,5 / 3,5 (10) | 155 |
| `fixedTime` | **−1** ×147 (ngẫu nhiên) · 0 ×7 · 1 ×1 | 155 |

Nguồn: `Boss4_ExplosionTimer.csv` (155 dòng / 138 object; root nhiều nhất: `Boss-39010` 30).

> **Đọc ra:** hiệu ứng nổ của boss được **hẹn giờ ngẫu nhiên 0,5–6,8 s** (69/155), tức
> boss **nổ lụi dần** trong ~7 giây sau khi chết — không phải nổ 1 phát. Đây là "juice"
> rẻ tiền mà hiệu quả: thêm rung + khói + nhiều tiếng nổ nhỏ.

---

## 6. `Enemy_Controller` — kiến trúc 1 enemy gồm 9 script

Mỗi `Enemy_Controller` (**981** instance — đo lại 25/10) tham chiếu tới **9 MonoBehaviour con**:

| Script | Vai trò | Có dữ liệu trong CSV? |
|---|---|---|
| `appearScript` | điều kiện xuất hiện | ❌ (`Enemy_Appear.csv` chỉ có ref) |
| `dataScript` | chỉ số (HP…) | ✅ `Enemy_Datas.csv` |
| `healthScript` | HP / `noDamage` | ✅ `Enemy_Health.csv` |
| `movementScript` | bay | ✅ `Enemy_Movement.csv` |
| `physicsScript` | va chạm | ⚠ `Boss_BodyPhysics.csv` (chỉ boss) |
| `uiScript` | thanh máu | ❌ |
| `destroyScript` | hiệu ứng chết | ❌ |
| `burnedScript` | trạng thái cháy | ❌ |
| `stunScript` | choáng | ❌ |

Nguồn: `Enemy_Controller.csv` (**981** dòng — đo lại 25/10).

> **Đây là blueprint kiến trúc tốt nhất trong cả bộ spec**: 1 enemy = 9 component tách rời,
> ghép bằng reference. Khi clone, dựng đúng 9 component này thì mọi loại enemy chỉ còn là
> **cấu hình**, không phải code mới.

---

## 7. `GridLayoutManager` — 108 object, lưới UI

| Tham số | Giá trị phổ biến | Nguồn |
|---|---|---|
| `cellSize` | 2,0 × 2,5 · 2,5 × 2,5 · 2,3 × 2,3 | `GridLayoutManager.csv` |
| `fixedColumnCount` | **4** (73) · 5 (44) · 3 (10) | " |
| `padding` | 0,8 / 0,2 / 0,0 | " |

Dùng cho `ScrollView` (14), `ObjectMove` (12), `Board_PVP` (7), `Drop-Items` (6), `Board_Shop` (5).
⇒ Lưới shop/roster là **4 cột** (chuẩn), 5 cột cho danh sách dài.

---

## 8. Còn thiếu / phải đoán

| # | Điều | Trạng thái | Cách lấy |
|---:|---|---|---|
| 1 | **Hình học đường bay** (`points[i].x/y`) | **D** — CSV chỉ có độ dài mảng | parse binary `data.unity3d` |
| 2 | Tham số 6 spawner con (thời gian, hướng…) | **D** — 0 cột dữ liệu | đọc `libil2cpp.so` |
| 3 | `endOfPathInstruction` / `typeMoveEnded` ý nghĩa chính xác | **C** — enum 2–3 giá trị | `dump.cs` + test |
| 4 | `appearScript` (điều kiện xuất hiện) | **D** — `Enemy_Appear.csv` rỗng | IL2CPP |
| 5 | Hành vi `destroyScript`/`burnedScript`/`stunScript` | **D** | IL2CPP |
| 6 | `isTurret` xoay theo player hay theo hướng cố định | **C** — suy từ tên | test |
| 7 | Tốc độ 30,0 thuộc enemy nào | **C** — 8 dòng, chưa map prefab → wave | cần `Enemy_Data_Balance` |
| 8 | `border.w = 25` duy nhất ở đâu | **C** — 1/800 | tra `_gameobject` |

---

## 9. Nguồn

`reverse-engineering/scriptableobjects/`: `Enemy_Movement.csv` · `Enemy_Controller.csv` ·
`Enemy_Sub.csv` · `Enemy_Appear.csv` · `PathCreator.csv` · `Spawner.csv` ·
`PointToPoint_Spawner.csv` · `Path_Spawner.csv` · `Rocket_Spawner.csv` ·
`AirFree_Spawner.csv` · `PinMap_Spawner.csv` · `Waypoints_Spawner.csv` ·
`MeteoriteGenerator.csv` · `Boss4_ExplosionTimer.csv` · `GridLayoutManager.csv` ·
`Enemy_Datas.csv` · `Enemy_Health.csv`
`docs/apk-analysis/`: `Enemy_Movement.csv` · `Enemy_Controller.csv` · `MeteoriteGenerator.csv`
`datas/waves.json` (đối chiếu `y_spawn`)
`reverse-engineering/il2cpp/dump.cs.gz`: `class Enemy_Movement`, `class PathCreator`,
enum `EndOfPathInstruction`.
