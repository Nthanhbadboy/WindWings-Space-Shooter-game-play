# MISSING — còn thiếu gì để **học lại và làm một game mới**

> Viết 25/10 sau khi kéo snapshot **`575113776`**. Mọi con số trong tài liệu này đều có claim trong
> `tools/verify-claims.py` (nhóm **AM**), chạy: `python3 tools/verify-claims.py --only AM`.
>
> **Định nghĩa "thiếu" ở đây** = thiếu **dữ liệu / thông số** để dựng lại một hệ, **không** phải thiếu
> ý tưởng thiết kế. Cái gì dữ liệu không có mà **tự chọn được** thì ghi là *lựa chọn thiết kế*, không
> ghi là thiếu — đúng mức L1 (*giống cơ chế, không cần giống số*).

---

## 0. Cách kiểm

Mỗi hệ trả lời 4 câu, không được bỏ câu nào:

1. **Để làm game mới cần gì?** (cần đúng cái gì, không phải "cần hiểu game")
2. **Đang có gì?** — file + claim, không chép báo cáo.
3. **Thiếu đúng cái gì?** — tên file/địa chỉ, không nói "còn mờ".
4. **Việc kế tiếp** + có cần **thiết bị** không.

---

## 1. Mười ba hệ — trạng thái

| # | Hệ | Đủ để dựng lại? | Đang có (bằng chứng) | Thiếu gì |
|---:|---|---|---|---|
| 1 | **Vòng lặp lõi** (30 s / 1 phiên / 1 tuần) | ✅ **đủ** | `GAMEPLAY.md` §0; 3 vòng lặp viết được thành design doc | — |
| 2 | **Điều khiển + va chạm** | ✅ **đủ** | kéo ngón để lái, nhấc tay đổi tàu; biên **20×25**, radius **15 unit** (`ENEMY_BEHAVIOUR.md`) | — (L1 tự chọn cảm giác) |
| 3 | **Súng / đạn / sát thương** | ✅ **đủ** cho L1 | **458 súng** · damage **40–1.200** (median 400) · **186 loại đạn** · burst 5 tham số (`COMBAT.md`) | **B3**: đường cong damage theo rank — xem §2.2 |
| 4 | **Enemy** | ✅ **đủ** | **109 prefab** (39 boss + 70) · 9 component · 399 đường bay · **150 HP id** (`datas/enemy_hp_by_id.json`) | — (B1 coi như đóng: HP theo **id**, không theo wave) |
| 5 | **Boss** | 🟡 **một phần** | 39 prefab `Boss-*` · **795 event** có mốc thời gian · 268 cặp (prefab, clip) · nhịp **0,17 / 0,33 / 1,0 / 5,0 s** | **D3**: thứ tự pha + điều kiện vào/thoát — có mốc, **chưa có** thứ tự (mức C) |
| 6 | **Wave / spawn** | ✅ **đủ** | **282 wave · 11.094 spawner · 22.482 slot** (`H2`, `I3`, `M3`) | — (`rate = 0` là "spawn cả loạt", mức B, đã ghi) |
| 7 | **Độ khó 3 chế độ** | ✅ **đủ** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · không nhân số quân | ngưỡng % riêng = tự chọn |
| 8 | **Kinh tế / rơi đồ** | ✅ **đủ** | 3 tầng rơi: **702** vật đặt sẵn (**676 coin / 26 item**) · **246/2.094** slot mang item · **6** loại (`AE1`–`AE3`) | trọng số chọn giữa 6 loại — **tự chọn** |
| 9 | **Meta: tàu / sao / talent / drone** | 🟡 **một phần** | **25 tàu** nhưng `Player_Info` **4 field**: `id` · `Sprite` · `Star` · `Actived` (claim **AM3**) ⇒ tàu **không** có HP/damage riêng; `Player_Talent` **23 method** · **13 drone** | giá nâng cấp theo sao (**dữ liệu có, chưa bóc**); công thức talent (C) |
| 10 | **UI** | ✅ **cấu trúc** · ✅ **luật thị giác** / ❌ **asset** | **797 màn · 150.131 node · 5.831 nút** (`N2`, `P6`); **55.584** layout file; khung hình **0,4813** · accent **≤10 %** · tương phản **0,45–0,80** (`VISUAL_DESIGN.md`, **AN1**, **AN2**) | asset gốc: **vẽ mới**; luật thì **đã có số** |
| 11 | **Âm thanh** | 🟡 **có dữ liệu, chưa có luật phát** | **69 clip / 571,5 s**, trong đó **5 vòng nhạc > 60 s** (`docs/assets/audio-index.csv`) | **ai phát cái gì, lúc nào** (`AudioSource`/`AudioManager` chưa bóc) |
| 12 | **Save / load + live-ops** | ❌ **thiếu** | **170 IAP** (2 nhóm); `MISSIONS_STARS.md`; `ui_text_keys` 1,25 M dòng | **schema save** (khoá, kiểu, mặc định) — **0** tài liệu; **chưa** trích bảng chuỗi |
| 13 | **Tech / build** | 🟡 **một phần** | Unity **2022.3.x** (`UNITY_RULES.md`) · Spine · DOTween · 3 loader trong repo này | plugin list đầy đủ + cấu hình build (lấy từ `dump.cs`/manifest, không cần thiết bị) |

**Đọc bảng này theo đúng nghĩa:** 8 hệ **đủ** để dựng lại, 4 hệ **một phần**, 1 hệ **thiếu** (save/load).

---

## 2. Ba chỗ **chặn thật** — và địa chỉ để mở

Ba chỗ này khác hẳn 10 chỗ còn lại: chúng **không** phải "tự chọn được", vì nếu tự chọn thì game mới
sẽ **lệch cơ chế**, không phải lệch số.

### 2.1 A6 — một **stage** gồm mấy wave (chặn A5: độ dài phiên)

- **Có gì:** `Map_Get_Datas..cctor` **100.896 B · `ends_clean: true`** · **4.020** const · **576** `init_array`
  (claim **AM1**) — export **đầy đủ, không bị cắt**. Hàm `GetListWaves` **1.112 B**, trả `int[]`.
- **Thiếu gì:** **bytes** của 576 blob. Mỗi `init_array` đã có địa chỉ nguồn (`a:`), ví dụ
  `0x2bd4838` (len **36**), `0x2bd5488` (len **36**), `0x2bd58a8` (len **3**). Phân bố độ dài:
  **3 → 320 mảng**, **7 → 104**, **36 → 63**, 4 → 21, 5 → 12, 6 → 9.
- **Vì sao chặn:** 250 map ↔ 282 wave. Không biết map nào gồm wave nào thì **không** tính được một
  phiên dài bao lâu, và **không** kiểm được 299 stage ↔ 250 map.
- **Việc kế tiếp:** nhánh dữ liệu dump **576 blob** ở các địa chỉ `a:` (tổng chỉ vài KB) —
  **cùng cách** đã làm cho `stage23-rodata.json`. Không cần thiết bị, chỉ cần `libil2cpp.so`.
- **Sau khi có:** parse `int32[len]` → map × wave list → A5 tự đóng.

### 2.2 B3 — đường cong damage của **tàu** theo rank

- **Có gì:** `Player_Get_Datas..cctor` **2.492 B** · **6** `init_array` · mảng dài nhất **24** (claim **AM2**).
  Bốn mảng đó ứng với `StartMainCannonDamages` (`0x78`) · `StartMainCannonRate` (`0x80`) ·
  `StartWingCannonDamages` (`0x88`) — đọc offset từ `dump.cs.gz`.
- **Thiếu gì:** bytes của **4 mảng × 24 float** + 2 mảng × 3, tại `0x2bd5a40`, `0x2bd4d28`, `0x2bd5af8`,
  `0x2bd45c0`.
- **Vì sao chặn:** `Player_Info` **chỉ 4 field** (claim **AM3**) ⇒ **tàu không có damage riêng**. Toàn bộ
  khác biệt giữa 25 tàu nằm ở **rank** (`GetMainCannonDamage`) và ở `Star`. Không có mảng này thì
  DPS/TTK tuyệt đối **không** tính được, chỉ có damage **của đạn** (40–1.200).
- **Việc kế tiếp:** cùng một lần dump rodata với §2.1 (hai class, 6 blob).
- **Sau khi có:** `TTK` từ "tương đối" lên **số thật**; `COMBAT.md` §6 hết câu "chưa có số tuyệt đối".

### 2.3 Save / load — **0 tài liệu**

- **Có gì:** **170 IAP** (2 nhóm), mission/sao, 1,25 M dòng text UI.
- **Thiếu gì:** tên khoá lưu, kiểu, giá trị mặc định, thứ tự migrate. `03-il2cpp-strings.json` có
  **15.053** chuỗi nhưng chỉ expose `urls · ips · emails · suspicious · json` ⇒ **chưa** tra được
  `PlayerPrefs.*` / tên file save.
- **Vì sao chặn:** nếu làm game mới, **tự đặt schema** là được — nhưng khi đó **không** giữ được
  hành vi "mất dữ liệu thì mất gì" (điều ảnh hưởng trực tiếp tới kinh tế: 170 gói IAP).
- **Việc kế tiếp:** (a) export **toàn bộ** 15.053 chuỗi; (b) grep `PlayerPrefs|Save|Load` trong asm
  **tất cả** 139 file (đã có sẵn trong repo). Không cần thiết bị.

---

## 3. Cái **không phải** thiếu (đừng đi tìm nữa)

| Thứ | Vì sao không thiếu |
|---|---|
| **feel** (hit stop · aim assist · input latency) | **không tồn tại trong build** — 0 site `timeScale`, 0 method `aim` trên **139** file asm (**AF2**, **AF3**). Cái có thật đã có số: hit flash **0,5 / 0,05 s** (`J9`), rung **241** prefab (`AF1`) |
| **art, font, atlas (bản gốc)** | L1 **vẽ mới**. Cái **không** bỏ là **luật thị giác**: khung hình · ba chế độ sáng · ngân sách accent · vignette khung thưởng · mật độ chi tiết — đã đo và ghi ở `VISUAL_DESIGN.md` |
| **số cân bằng cụ thể** (giá, tốc độ, mật độ) | L1 cho phép tự chọn; cái phải giữ là **cơ chế** (3 chế độ, không nhân quân, rơi đồ 3 tầng) |
| **thứ tự pha boss (D3)** | Có **795 event + mốc thời gian**; thứ tự là **lựa chọn thiết kế**, dữ liệu chỉ cần đủ để biết "mỗi pha có đòn gì" |
| **13 class "chưa phân loại" trong ASSET_TRIAGE** | vẫn còn **1.554** `unclassified` / 2.197 — nhưng đây là việc **phân loại ảnh**, không chặn dựng game (L1 vẽ mới) |

---

## 4. Trả lời "đủ chưa" — theo L1 / L2 / L3

- **L1 (làm game **giống cơ chế**, art mới, số tự chọn): ĐỦ.** 8/13 hệ đủ, 4 hệ một phần nhưng phần
  thiếu đều **không chặn** (D3 = chọn thiết kế; audio = tự chọn; talent = tự chọn giá).
- **L2 (giống **số** đến mức chơi thấy tương đương): CHƯA.** Cần đúng **§2.1 + §2.2** (6 blob rodata).
  Ngoài ra cần playback thật để so cảm giác — việc này cần **thiết bị**.
- **L3 (tái lập **1:1 asset** gốc): BỎ** — art pack, font, shader, physics không tái lập từ APK.
  **Không** có nghĩa là bỏ "thiết kế cho đẹp": phần đó là `VISUAL_DESIGN.md` (khung hình **0,4813**,
  tương phản **0,45–0,80**, accent **≤10 %** gameplay / **~47 %** khung thưởng, chi tiết **13–22**,
  juice **0,05 s** + **0,10 · 20 frame**) và **kiểm được bằng máy**.

---

## 5. Nếu chỉ làm được **một** việc tiếp theo

Xin nhánh dữ liệu **một lần dump rodata** gồm 6 blob của `Player_Get_Datas` và 576 blob của
`Map_Get_Datas` (tất cả địa chỉ đã có trong `init_array.a`). Đổi lại:

| được gì | mở khoá |
|---|---|
| 4 mảng 24 float | **B3** đóng → TTK tuyệt đối, cân bằng súng theo rank |
| 576 mảng int | **A6** đóng → **A5** đóng → biết một phiên dài bao lâu |

Đó là **hai** trong **bốn** câu ❌ cuối cùng của `DESIGN_QUESTIONS.md` (48 câu: **29 ✅ · 15 ⚠ · 4 ❌**,
claim **S2**), và cả hai đều **không cần thiết bị**.
