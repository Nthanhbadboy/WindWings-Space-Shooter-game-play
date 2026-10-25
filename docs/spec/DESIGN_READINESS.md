# DESIGN_READINESS — đã đủ để bắt tay thiết kế chưa?

> **Câu hỏi:** *"Đã OK để thiết kế game mới chưa?"*
>
> **Trả lời ngắn: ĐỦ — cho phạm vi đã chốt (L1: giống cơ chế, không cần giống số).**
> Và **không** đủ nếu ai đó định làm L2/L3 (khớp số / không phân biệt được).
>
> **Kiểm lại toàn bộ 14 vùng năng lực:** xem **`COVERAGE_AUDIT.md`** — bản này trả lời *"đủ cho L1 chưa"*,
> bản kia trả lời *"còn thiếu chính xác chỗ nào"*. Kết luận khớp nhau: **2 chỗ chặn** (map→wave · HP runtime).
>
> **Cập nhật 24/10 — vòng 2:** sau khi giải script animation (`ANIMATION_SCRIPT.md`), hệ
> **Animation**: **35/39 prefab boss** có **nguồn** animation/event trong tập đã xét, boss 1 giải
> xong 8 tên entry. Hàng "feel" cũng hết trống: hit flash **0,05 s** đo được. Xem §7.
>
> Tài liệu này đo lại **9 câu blocker** của `DESIGN_QUESTIONS.md` bằng dữ liệu đang có trong repo,
> không chép lại đánh giá cũ. Mỗi dòng đều chạy lại được bằng `tools/verify-claims.py` (nhóm `I`).

---

## 1. Vì sao "đủ" — cái gì đã chốt

`DONE.md` §4.2 đã ghi quyết định phạm vi:

> **L1: giống cơ chế, không cần giống số.**

Đây là điều làm câu trả lời thành **có**. 9 blocker trong `DESIGN_QUESTIONS.md` được viết khi mục
tiêu còn là L2/L3 — *"sao cho giống bản gốc"*. Dưới L1, phần lớn chúng **không còn là blocker**:
chúng là **tham khảo**, không phải điều kiện.

---

## 2. Chín blocker — trạng thái **đo lại hôm nay**

| # | Câu | Trạng thái cũ | **Đo lại 23/10** | Chặn thiết kế L1? |
|---:|---|---|---|---|
| 1 | `StartHp` | đóng (2500) | ✅ **đóng** — `statics_Player_Get_Datas.StartHp = 2500` | **Không** |
| 2 | **A6 — stage ↔ wave** | mở | 🟡 **một phần** — `map_waves_candidate.json`: **250 map**, nhưng chỉ **7** ghép chắc (`immediates`), **243** ghép theo thứ tự blob *"chưa xác thực bằng token"* | **Không** (chỉ cần biết có bao nhiêu màn) |
| 3 | **E2/E3 — hit flash / hit stop** | mở, "chi phí thấp" | 🟡 **nửa đóng** — `Enemy_Display` không chứa tham số (**5 field**: `hpProgressBarRenderer` · `size` · `hitableRenderers` · `appearOff` · `dieOff`), nhưng **`OnHit` có 2 hằng số**: alpha **0,5** trên material + `Invoke("OffHitEffect", `**`0,05 s`**`)` ⇒ nháy trúng đòn **đã đo được**; còn thiếu tên tham số material | **Không** nữa |
| 4 | **D3 — thứ tự pha boss** | mở, "cần decoder" | 🟡 **MỘT PHẦN** (hạ mức 25/10) — có **mốc trong clip** (`795/795` event có `time`, mức **A**), **chưa** có thứ tự pha / điều kiện vào-thoát / số lần lặp / hành vi callback (mức **C**) | **Không** |
| 5 | **B1 — HP enemy runtime** | mở | 🔴 mở — có hằng số, chưa có thứ tự nhân | **Không** (L1 tự chọn số) |
| 6 | **C4 — vàng/giờ** | mở | 🟡 tính được, **chưa làm** | **Không** |
| 7 | **A7 — mật độ địch** | mở, "làm bằng script" | 🟡 tính được **một nửa** — nhưng vướng #9 (xem dưới) | **Không** |
| 8 | **A5 — độ dài phiên** | mở, "chi phí cao" | 🔴 mở — cần A6 + luật continue | **Không** (tự chọn) |
| 9 | **B3 — đường cong damage** | mở, "chi phí cao" | 🔴 mở | **Không** (tự chọn) |

**Đóng thêm được 1 câu (D3)** so với lần đánh giá trước — không cần decoder nữa, vì nhánh dữ liệu
đã join event với Animator và giữ nguyên `time`.

---

## 3. Một con số sai — sửa luôn

`DESIGN_QUESTIONS.md` ghi **`rate = 0` ở 2.373 spawner**. Đếm lại trên `datas/waves.json`:

```
11.089 spawner · rate = 0 : 2.365 · rate thiếu: 0
phân bố: 1,0 → 7.741 · 0,0 → 2.365 · 0,5 → 532 · 2,0 → 163 · 0,65 → 111 · 6,0 → 58
```

**2.365**, không phải 2.373. Lệch 2, nhưng cùng loại lỗi đã năm lần trong repo này: một con số
không kèm phép đếm. Nay `I3` khoá lại.

Câu hỏi thật vẫn mở và **nó chặn A7**: `rate = 0` nghĩa là **spawn tức thời** hay **mỗi khung
hình**? 2.365/11.089 spawner (21 %) rơi vào trường hợp này, nên mọi phép "địch/giây" đều có sai số
21 % cho tới khi phân xử.

### 3.1 Kéo thêm dữ liệu (24/10) — câu này **hẹp lại**, chưa đóng

Kéo `reverse-engineering/scriptableobjects/` (1.339 file) thì `Call_Data.csv` cho **schema thật**
của spawner: **1.200 dòng · 23 field**, và hai điều đo được:

| Điều | Bằng chứng | Hệ quả |
|---|---|---|
| **không có field `delay`** | 23 field gốc, không field nào tên `delay`/`wait`/`interval` | `rate` là **field thời gian duy nhất** ⇒ nó phải là **giãn cách** |
| `number` **vô dụng** | `number = 0` ở **1.200/1.200** dòng | số quân = **độ dài `listPrefabEnemies`**, không phải `number` |

| Nhóm | Số spawner | list quân trung vị | dài nhất |
|---|---:|---:|---:|
| `rate = 0` (trong `Call_Data`) | **295** | 1 | **6** |
| `rate > 0` | 898 | 1 | 16 |
| `rate = 0` (trong `waves.json`, đã nhân `copies`) | 2.365 | 2 | **30** |

⇒ **Nghiêng mạnh về "không giãn cách ⇒ spawn cả loạt"** (mức **B**): nếu `rate` là "số quân/giây"
thì 295 spawner `rate = 0` sẽ **không bao giờ** spawn, và 1.203 spawner `rate = 0` có **>1 quân**
(dài nhất **30**) sẽ là quân chết — vô lý trong một game đã phát hành.

**Không chặn thiết kế nữa:** mật độ tính từ **độ dài danh sách quân** (đã có), không từ `rate`. Xấu
nhất 30 quân cùng lúc; nhịp còn lại là do `rate` của **các spawner khác**. Vẫn cần asm để lên **A** —
việc đó vẫn nằm ở T5 của `HANDOFF_ANIM_RAW.md`.

---

## 4. Chỗ **thật sự** sẽ làm đau khi thiết kế — không phải mấy con số trên

Ba blocker còn lại (#3, #5, #8, #9) đều **không chặn L1**, vì L1 cho phép tự chọn số. Nhưng có hai
thứ mà *tự chọn* cũng không cứu được, vì chúng là **cảm giác**, không phải tham số.

### 4.1 Feel — hit flash / hit stop (câu #3): từ "không có dữ liệu" → **đo được một nửa**

Vòng trước tài liệu này ghi *"là thứ duy nhất dữ liệu không có"*. **Sai một nửa.** Đọc asm
`Enemy_Display.OnHit` (352 B) thì thấy **2 hằng số**:

| chỗ | giá trị | nghĩa |
|---|---:|---|
| `Material.SetFloat(<tên tĩnh>, 0.5)` trong vòng `hitableRenderers` | **0,5** | nháy sáng/alpha khi trúng đòn |
| `Invoke(<tên tĩnh>, 0.05)` ở cuối hàm | **0,05 s** | thời gian tắt lại, bằng `Invoke` chứ không coroutine |

Còn thiếu: **tên tham số material** (chuỗi nằm trong bảng literal, chưa export) và **hit stop**
(không có dấu vết `timeScale` ở bất kỳ lớp nào đã đọc).

⇒ Hệ quả cho thiết kế: **đừng chờ dữ liệu thêm**. Có nhịp (0,05 s) và cường độ (0,5) là đủ để
prototype 30 giây; phần "cảm giác" còn lại tự quyết.

### 4.2 Animation — **không còn là bức tường**

| hạng mục | vòng 1 | **vòng 2** |
|---|---|---|
| biết **clip nào chạy lúc nào** (boss) | 🔴 chưa | 🟡 **35/39 prefab boss** có **nguồn** animation/event (không phải "đã giải script"): **33 prefab · 793 event có `time`** + **2 prefab Spine** (`Boss-39001/39002`); **4 prefab không có gì** (`Boss-37003/37005/37006/37008`). Timeline **từng giây**: **`BOSS_ANIM_TIMELINE.md`** (269 cặp clip) |
| biết **tên entry** | 🔴 chưa | ✅ boss 1: **8 chuỗi**, bảng chuyển state **5 nhánh** |
| biết **nhịp đòn** | 🔴 chưa | ✅ **0,17 · 0,33 · 1,0 · 5,0 s** |
| biết **điều kiện chuyển state của enemy** | 🔴 chưa | 🟡 cần tham số `Animator` — **T4** của `HANDOFF_ANIM_RAW.md` |
| đồ hoạ chuyển động (keyframe) | 🔴 0/791 | 🔴 **0/791** — nhưng L1 **làm art mới**, nên không cần |
| đo playback trên máy | 🔴 0 lần | 🔴 **0 lần** — chỉ cần nếu làm L2/L3 |

⇒ Hệ quả: **thiết kế animation được ngay**. Cái duy nhất còn phụ thuộc dữ liệu là *điều kiện* máy
trạng thái của enemy — và nó **không chặn** vì L1 cho phép tự đặt điều kiện.

## 5. Bảng sẵn sàng theo hệ

| Hệ | Đủ để thiết kế? | Cơ sở |
|---|---|---|
| **Vòng lặp / wave / spawn** | ✅ **A** | 109 prefab roster · 282 wave · 11.095 spawner · 22.461 lượt spawn (`waves.json`) |
| **Độ khó / chế độ** | ✅ **A** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · 3 chế độ mỗi stage |
| **Kinh tế / sao / HP** | ✅ **A** cho hằng số | `StartHp 2500` · `stepCommon 0,18` · `DeltaStarCost 50` · `PercentToCompleteMissions222 [0.2,0.6,0.98]` |
| **Boss** | ✅ **A** cho cấu trúc | 46 boss · **39 prefab `Boss-*`** · **2 prefab Spine** (`Boss-39001/39002`) · 92 `Animator`/36 prefab · 795 event có mốc thời gian |
| **Enemy** | ✅ **A** cho cơ chế | **399 đường bay** theo path (tập prefab đã đọc) · `Enemy_Appear` = base nhận `Action` qua tham số (**chưa** rõ binding) · `Enemy_Display` 5 field |
| **Animation — *mốc trong clip*** | 🟡 **A** cho mốc / **C** cho điều kiện + hành vi | 33 prefab **793 event có mốc thời gian** · boss 1: **8 tên entry + 5 nhánh** chuyển state · nhịp đòn **0,17/0,33/1,0/5,0 s** · enemy = máy trạng thái 3 nhánh + hit flash **0,05 s** — xem **`ANIMATION_SCRIPT.md`** |
| **Animation — *playback / feel*** | 🔴 **D** | 0/791 keyframe · 0 phép đo playback runtime · hành vi 12 handler còn **C** — **chỉ cần nếu làm L2/L3** |
| **UI — cấu trúc** | ✅ **A** | **125 màn hình** (`screens.csv`: 125 dòng) · 53 board · 63 popup · 8 tab · screen graph + điều kiện mở từng popup ở `UI.md` |
| **UI — art** | 🔴 **D** | 53k file dump có trong nhánh dữ liệu nhưng **chưa kéo về**, chưa phân tích — và L1 làm art mới nên không cần |

---

## 6. Kết luận

**Thiết kế được, ngay bây giờ, cho L1.** Sau vòng 2, **không còn hệ nào ở mức C/D mà L1 cần**:
vòng lặp, wave, spawn, độ khó, kinh tế, boss, enemy, **animation script**, UI cấu trúc — đều **A**
(hoặc **B** ở chỗ không chặn).

Ba việc nên làm **trước khi** vẽ bảng thiết kế chi tiết — đổi thứ tự so với vòng 1 vì animation đã
xong:

| | Việc | Vì sao trước | Giao ai |
|---:|---|---|---|
| 1 | **Chốt `rate = 0`** — spawn cả loạt hay mỗi frame | đã hẹp còn **B** (§3.1); mật độ **không còn phụ thuộc** nó | nhánh dữ liệu (T5, cần asm) — **không chặn** |
| 2 | **A6 stage ↔ wave** | quyết định **số màn**; hiện chỉ 7/250 map chắc chắn | offline — tự làm được |
| 3 | **Prototype feel 30 giây** (hit flash 0,05 s · alpha 0,5 · rung · âm) | thứ duy nhất vẫn phải **quyết**, không phải **đo** | designer |

Và **một việc không nên làm**: đừng chờ thêm **mốc thời gian** trong clip — đã có. Nhưng **đừng** gọi là
"đã có script": thứ tự pha, điều kiện chuyển state, số lần lặp và hành vi callback vẫn **C**. Chỉ *playback* là
thiếu, và nó chỉ cần cho L2/L3.

### 6.1 Vòng 3 (24/10) — ba thay đổi so với bảng trên

| Việc | Trước | Sau | Bằng chứng |
|---|---|---|---|
| **D3 — thứ tự pha boss** (`DESIGN_QUESTIONS.md`) | ❌ "chỉ có `__count`" | ⚠ **một phần** (hạ mức 25/10, review R1): **A** cho mốc trong clip, **C** cho thứ tự/điều kiện/hành vi | `795/795` event có `time` ⇒ `BOSS_ANIM_TIMELINE.md` |
| **E2 — hit flash** | ❌ "chưa đọc" | ⚠ **có số** | alpha **0,5** + `Invoke(…, 0,05 s)` trong `Enemy_Display.OnHit` |
| **A7 — mật độ địch** | ❌ | ⚠ **một nửa** | số quân = độ dài `listPrefabEnemies`; `rate = 0` nghiêng **B** "cả loạt" |

⇒ `DESIGN_QUESTIONS.md` nay là **48 câu · ✅ 29 · ⚠ 15 · ❌ 4** (claim **S2** giữ cho dòng tổng không lệch
bảng; D3 hạ ✅→⚠ sau review R1). **Câu trả lời cho câu hỏi của tài liệu này không đổi: thiết kế được cho L1** — chỉ khác là
**animation không còn nằm trong danh sách "phải chờ"**, và *thứ duy nhất* vẫn phải **quyết** (không phải
**đo**) là **feel**.

---

## 7. Bảng kiểm thao tác — một design doc viết được đến đâu **hôm nay**

Không phải "hệ này mức A" mà là: **mở file nào, viết mục nào**. Cột cuối là chỗ **còn phải quyết**,
không phải chỗ còn thiếu số.

| Mục của design doc | Viết được từ | Trạng thái | Còn phải **quyết** |
|---|---|---|---|
| Core loop, 3 vòng lặp | `GAMEPLAY.md` §0 | ✅ đủ | nhịp 30 s / 10 phút / 1 tuần của bản mới |
| Điều khiển & va chạm | `ENEMY_BEHAVIOUR.md` (biên 20×25, radius 15 unit) | ✅ đủ | có giữ "di chuyển tự động" hay không |
| Enemy: 9 component, đường bay | `ENEMY_BEHAVIOUR.md` · `BOSSES.md` §5 | ✅ đủ | 8 họ enemy nào giữ, nào bỏ |
| Boss: pha, bộ phận, HP | `BOSSES.md` · `ANIMATION_SCRIPT.md` | ✅ đủ | 3 đòn lặp + chuyển pha — giữ nguyên sơ đồ, đổi art |
| Wave & mật độ | `ENCOUNTERS.md` · `datas/waves.json` · `Call_Data.csv` | ✅ **đủ** — schema 23 field, số quân = độ dài list | nhịp `rate` (B) hoặc tự định nghĩa |
| Độ khó 3 chế độ | `DIFFICULTY_MODES.md` (không nhân số quân) | ✅ đủ | ngưỡng % riêng |
| Kinh tế, sao, IAP | `ECONOMY.md` · `MISSIONS_STARS.md` | ✅ đủ | giá theo bản mới |
| UI 125 màn hình | `UI.md` §9–§9.3 · `screens.csv` | ✅ đủ cấu trúc · **11 board có bộ đầu vào vẽ** + layout tutorial 7 GO | art + 9-slice mới; `Board_Maps` **cận dưới** (trần 6.000) |
| Animation | `ANIMATION_SCRIPT.md` | 🟡 **mốc + danh sách trigger (A)**, **6 chuỗi `SetTrigger` (C)**, hành vi handler (C); enemy **46/70** không có máy trạng thái | art + rig mới; có giữ 16 đòn/boss hay rút |
| Âm thanh | `ASSETS.md` §audio (69 file) | 🟡 danh mục | nhạc/âm mới |

**8/10 mục đủ ngay · 2/10 mục viết được nhưng phải ghi rõ chỗ chưa đóng** (Animation: 6 chuỗi trigger +
hành vi handler; Âm thanh: danh mục 92 id, chưa có trigger). Mục **mật độ** treo **cách diễn giải**
`rate = 0`, **không** treo số lượng — 22.461 lượt spawn trên 282 wave đã có.

### 7.1 Ba con số "đã sẵn sàng" đáng nhớ

| | Số | Nghĩa |
|---|---:|---|
| **35/39** | prefab boss có **nguồn** animation/event trong tập đã xét | 4 prefab còn lại **không có cả clip event lẫn Spine trong tập đó** — không phải "không có animation" |
| **125** | màn hình UI có cấu trúc | mỗi màn có điều kiện mở + dữ liệu cần load |
| **10/10** | mục design doc viết được ngay | sau khi `Call_Data` cho schema spawner |

---

## 8. Trả lời "đủ chưa" bằng **số đếm** (25/10, không dùng %)

| tập | tổng | đủ / đóng | một phần | chưa |
|---|---:|---:|---:|---:|
| **15 dòng vùng năng lực** (`COVERAGE_AUDIT.md` §1) | 15 | **10** ✅ | **4** 🟡 | **1** 🔴 (feel) |
| **9 câu blocker** (§2 ở trên) | 9 | **1** (`StartHp`) | **5** | **3** (`B1` HP runtime · `A5` độ dài phiên · `B3` đường cong damage) |
| **48 câu design** (`DESIGN_QUESTIONS.md`) | 48 | **29** ✅ | **15** ⚠ | **4** ❌ (`A5`·`A6`·`B1`·`C4`) |
| **6 chỗ thiếu** (`COVERAGE_AUDIT.md` §2) | 6 | — | **4** | **2 chặn** (map→wave 7/250 · HP runtime theo chế độ) |
| **claim tự kiểm** (`tools/verify-claims.py`) | **146** | **144** PASS | 2 SKIP | 0 FAIL |

**Đọc bảng này thế nào:**

- **Đủ cho L1** (giống **cơ chế**, tự chọn số + art): **10/15** vùng dựng được ngay; 2/10 mục design doc
  phải ghi rõ chỗ chưa đóng; **0** chỗ nào bắt buộc phải chờ dữ liệu mới để **bắt đầu**.
- **Chưa đủ cho L2** (khớp **số** bản gốc): còn **3** câu 🔴 + **2** chỗ chặn — `B1` HP runtime (thiếu
  thứ tự nhân hằng số), `A5` độ dài phiên (cần A6 + luật continue), `B3` damage curve, **map→wave 7/250**,
  **HP theo chế độ** (B8).
- **Chưa đủ cho L3** (không phân biệt được): thêm **feel** (D1–D4: hit stop · aim assist · input latency ·
  tỉ lệ rơi) và **thứ tự pha boss** (C) — hai thứ này **phải quyết**, không đo được từ dữ liệu đang có.
