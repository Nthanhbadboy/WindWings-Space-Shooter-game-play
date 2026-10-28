# DESIGN_READINESS — đã đủ để bắt tay thiết kế chưa?

> **SUPERSEDE TOÀN VĂN (lần 144 — theo re-review `8141386a` `6444324415`):** mọi câu summary/tally/absolute trong tài liệu này (gồm §4.1b, các dòng "không tồn tại/không có", "L2 KHÔNG còn thiếu số", "mọi việc tĩnh đã đóng") đọc đúng phạm vi = **L1 tĩnh theo mẫu 139 file asm**; residuals = deferred/UNKNOWN/RUNTIME_UNVERIFIED — không phải kết luận toàn cục. Chi tiết: `GATE1_CLOSURE_NOTES.md`.

> **Câu hỏi:** *"Đã OK để thiết kế game mới chưa?"*
>
> **Trả lời ngắn: ĐỦ — cho phạm vi đã chốt (L1: giống cơ chế, không cần giống số).**
> Và **không** đủ nếu đích là L2/L3 (khớp số / khớp trải nghiệm + art — xem `DONE.md` §2).
>
> **Kiểm lại toàn bộ 14 vùng năng lực:** xem **`COVERAGE_AUDIT.md`** — bản này trả lời *"đủ cho L1 chưa"*,
> bản kia trả lời *"còn thiếu chính xác chỗ nào"*. Kết luận khớp nhau: **0 chỗ chặn số** — 2 chỗ "chặn"
> cũ (map→wave · HP theo chế độ) **ĐÃ ĐÓNG 25/10**; sót 2 phép tái đối chiếu runtime (không chặn).

> **Mục đích dịch ngược** (khối đầu `START_HERE.md`): đủ thứ để **bắt chước bản gốc** — mọi thứ trừ
> art đã có đáp án; **việc thiết kế duy nhất là art**.
>
> **Cập nhật 25/10 — lần 3 (đồng bộ lần 7–10 của `DONE`):**
> ① **bind xong**: save/load = id−10001 · **combat = impl N → index N−1** (report 81/82: tàu 10001→2 · 10003→0) · bảng Map **11 cấu trúc / 614 mảng**
> (`DIFFICULTY_MODES` §7) · HP enemy **150 cặp theo id** (claim **WRH2**);
> ② **`kHp[mode]` không tồn tại** — chế độ đổi composition + thưởng, không nhân HP; `pct` đủ **3/3**;
> ③ **playback thật đã có** (phiên phone 23/10 trong repo) — "cần thiết bị" chỉ còn 2 tái đối chiếu;
> ④ **feel BỎ** theo quyết định (không thấy trong mẫu 139 file asm — supersede lần 143; quá nhỏ);
> ⑤ peer tới report **87 / 412 tests** (combat chain + receivers + extra-life + khiên/zone);
> ⑥ tally **✅ 33 · ⚠ 14 · ❌ 1** (lần 11 kéo lại từ 31/16/1 — lô lần 9 bị mất) · claim **211/209 PASS**. Số dưới đây đã đo lại theo trạng thái này.

> **Cập nhật 26/10 — lần 4 (đồng bộ `DATA_SYNC` §24.80, chương trình đào 4-digger):**
> ① **D3 (row 4) NÂNG cho boss-1** — route static Boss_1_Animation đã map được:
> `Boss_AttackPhases` (PPtr → Animator/controller Boss-39019/20/21) · state
> `stateRunAway/Baydi` + `stateDie/Dead` → **UnityEvent defeat +0x70** (offset trực tiếp từ
> TypeDefIndex 141 — đã CORRECT bằng metadata); **burst +0x78 = serialized field/target,
> KHÔNG phải invocation đã chứng minh** (report 157/DS24.92: Event callback = RET · không
> đọc burstEvent — H4-07) → receiver **Enemy_Destroy 601110** (root 185722, `destroyScript` cùng root) ·
> Spine chain 602882→580611→skeleton JSON 918 · **8/8 state labels khớp tên animation
> asset** · BossSpineEventHandler: có code, **0 instance** ⇒ không join. ⇒ *thứ tự pha
> boss-1 có chứng cứ static; còn 38 boss + điều kiện runtime (MODEL_NOT_MEASURED)* —
> vẫn 🟡 nhưng từ "mức C" lên **mức B (boss-1)**; ② **C4/kin tế tĩnh ĐẦY HƠN**: box
> (typeBox miền 0/1/2 · `KeyPrices[typeBox]×(BoxKeyCost−owned)` · **3 call site**) ·
> energy (**30 gem→50** guard `Gems>29` · video slot 14 → **+30**) · rewards mùa arena
> (`#1[Medal:680,Gems:250]`…) · RankSplit/SeasonTime/MaxRankStars values — số thưởng/
> giá tĩnh đủ để thiết kế L1 số-sanh; "vàng/giờ" runtime vẫn là sample 23/10 (2
> coin/kill); ③ **tasks**: 26/28 gốc ĐÓNG + toàn bộ task mới (#29 Arena/PvP · #30
> meta thưởng · followup · followup-2) ĐÓNG — còn mở đúng 2: **#8** (byte-equal 5 MBs
> — gần handoff) + **#27** (native 123 + game-side phase-11); ④ tally DQ giữ
> **33✅/14⚠/1❌** — chưa lật câu nào lần này, các nâng trên là độ sâu chứng cứ;
> ⑤ **followup-3**: 4 mảng hộp đầy đủ — **AllTimeAds = giây chứng minh**
> (18.000/259.200/691.200 = 5h/72h/192h, seconds-compare `IsTimeAdsReady`) ·
> BoxKeyCost 30×3 · KeyPrices 6/20/100 · NumberRewards 5/6/9 ⇒ kinh tế hộp trọn;
> ⑥ **phase-11/12**: skeleton JSON 918 = `textassets/skeleton__21.json` (SHA
> `89debb56…` · 60.897B) · 6 event keyframes (Attack3×5) · **Attack4: KHÔNG có
> static request** cho boss-1 — route ngày càng khép; ⑧ **ef123 (27/10)**: slot callback
> boss-39002 `0x2ADFB48` → literal **`Stop`** (identity static; dispatch `MODEL_NOT_MEASURED`) —
> key thiết kế event Spine chắc chắn, hiệu ứng/lúc-gọi vẫn là quyết thiết kế;
> ⑨ **lần-104 (27/10)**: **123 APPROVE-BOUNDED · 118 SUPPORTED** (2 review độc
> lập) + save-schema khép (**21 key GameDatas + 28 literal store-key** · 184
> calls phân loại unknown-0) — hạng "đối trập độc lập" & "persistence" của
> readiness TĂNG; còn hở thiết kế: hunter rewardValues/scales + nghĩa 14 hàng
> medal (followup-13) · ToRoman glyphs (gated raw) ⑦ **#8** (gần handoff,
> artifact `e928b36002c8…` 59.887B): 52 refs → **3 Mesh thật**, 5/5 MB BYTE-EQUAL
> — mesh refs hết missing; ⑧ **weighted tổng ~85%** (audit lần-80 76% → nay:
> hệ 14 ~0,8 · hệ 15 ~0,88 · row-5 boss-1 mức B · row-9 StartDrone static ĐÓNG).
>
> **Cập nhật 24/10 — vòng 2:** sau khi giải script animation (`ANIMATION_SCRIPT.md`), hệ
> **Animation**: **35/39 prefab boss** có **nguồn** animation/event trong tập đã xét, boss 1 giải
> xong 8 tên entry. Hàng "feel" đo được một phần (hit flash **0,05 s**) nhưng **đã ra khỏi phạm vi**
> theo chỉ đạo 25/10 ⇒ không còn là hàng phải chốt, không chặn nghiệm thu (tiêu chí là **script**).
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
| 2 | **A6 — stage ↔ wave** | mở | ✅ **ĐÃ BIND (25/10)** — trước: `map_waves_candidate.json` có **250 map**, nhưng chỉ **7** ghép chắc; nay bind **11 cấu trúc / 614 mảng** (320×len3 ↔ 3 mode · 118×len2 = stage→boss · 104×len7 ↔ 7 `PlayMode`, `DIFFICULTY_MODES` §7); peer ghép entry vào `map_table_segments.json` + `maps.json` | **Không** |
| 3 | **E2/E3 — hit flash / hit stop** | mở, "chi phí thấp" | ✅ **ĐÓNG — BỎ (quyết định 25/10)**: game gốc **không có** trên mẫu asm (`Enemy_Display` chỉ **5 field**: `hpProgressBarRenderer` `size` `hitableRenderers` `appearOff` `dieOff` — không có tham số flash) và cảm nhận quá nhỏ ⇒ game mới **không thêm**; số đo cũ (alpha 0,5 · 0,05 s) chỉ để tham khảo | **Không** |
| 4 | **D3 — thứ tự pha boss** | mở, "cần decoder" | 🟡 **MỘT PHẦN** (hạ mức 25/10; **nâng 26/10 lần-4**: boss-1 route static map xong — state→defeat/burst +0x70/+0x78 (TypeDefIndex 141) → Enemy_Destroy, Spine 8/8 labels — mức **B cho boss-1**; 38 boss còn lại + điều kiện runtime mức C) — có **mốc trong clip** (`795/795` event có `time`, mức **A**) | **Không** |
| 5 | **B1 — HP enemy runtime** | mở | ✅ **HP THEO ID (25/10)** — `datas/enemy_hp_by_id.json` **150 cặp** (`CB-30003` = 650, claim **WRH2**); dict dựng trong `.cctor`, 0 vòng lặp (claim **IAB1**); `kHp[mode]` **không tồn tại** | **Không** |
| 6 | **C4 — vàng/giờ** | mở | 🟡 **có mẫu runtime (25/10)** — phiên 23/10: **276 kill → 540 coin** Stage 1 (≈ 2 coin/kill, `live_1_gp.json`); công thức `GetBonusCoin` **100,0 · 20,0** | **Không** |
| 7 | **A7 — mật độ địch** | mở, "làm bằng script" | 🟡 tính được **một nửa** — nhưng vướng #9 (xem dưới) | **Không** |
| 8 | **A5 — độ dài phiên** | mở, "chi phí cao" | 🔴 mở — cần A6 + luật continue | **Không** (tự chọn) |
| 9 | **B3 — đường cong damage** | mở, "chi phí cao" | 🟡 **đã có 6 mảng + ngưỡng (25/10)** — damage/rate/wing/cost theo index; bind combat = impl N → index N−1 (report 81/82); còn **rẽ nhánh `stepLevel`** đầy đủ (mức C) | **Không** (tự chọn) |

**D3 KHÔNG đóng** (sửa 25/10, review R5). Trước đây câu này ghi *"đóng thêm 1 câu (D3), không cần
decoder nữa"* — **mâu thuẫn** với chính bảng §2 ở trên (D3 = 🟡 một phần). Cái đã có là **nguồn
animation**: nhánh dữ liệu join event ↔ Animator và giữ `time` (795/795 event, mức **A**).
Cái **chưa** có là **script sequence**: thứ tự pha, điều kiện vào/thoát, số lần lặp, callback.
Timestamp chỉ chứng minh **mốc cục bộ trong clip**, không chứng minh **control-flow runtime**.
⇒ Giữ D3 ở mức 🟡; không ghi "đã đóng" ở bất kỳ đâu.

---

## 3. Một con số sai — sửa luôn

`DESIGN_QUESTIONS.md` ghi **`rate = 0` ở 2.373 spawner**. Đếm lại trên `datas/waves.json`:

```
11.089 dòng cấu hình · rate = 0 : 2.366 · rate thiếu: 0
phân bố 6 giá trị lớn nhất: 1,0 → 7.740 · 0,0 → 2.366 · 0,5 → 532 · 2,0 → 163 · 0,65 → 111 · 6,0 → 58
(6 giá trị này = 10.970/11.089; còn 119 spawner có 20+ giá trị nhỏ khác — 0,6 / 3,0 / 1,5 / 0,18 / 0,9 / 0,23 / …)
```

**2.366**, không phải 2.373. Lệch 7, nhưng cùng loại lỗi đã năm lần trong repo này: một con số
không kèm phép đếm. Nay `I3` khoá lại. *(Trước ghi 2.371 ở 2 chỗ — số đó thuộc phép đếm cũ;
**2.366** là số đo được và khớp `count_spawners = 11089` trong file.)*

**Câu hỏi KHÉP ở mức thiết kế (27/10)** — giữ **🟡 một nửa / không chặn** (đúng §2, §6):

`rate = 0` nghĩa là **spawn cả loạt** (mức **B**), **không** phải "mỗi khung hình". **2.366/11.089**
dòng cấu hình (**21,3 %**) rơi vào trường hợp này. Lý do: `Call_Data` **không có field
`delay`/`wait`/`interval`** (§3.1) ⇒ `rate` là **field thời gian duy nhất** ⇒ phải là **giãn cách**; nếu
`rate` là "quân/giây" thì 295 spawner `rate = 0` sẽ **không bao giờ** spawn, và 1.206 spawner `rate = 0`
có **>1 quân** (dài nhất **30**) sẽ là quân chết — vô lý trong game đã phát hành.

⇒ mật độ tính từ **độ dài danh sách quân** (`len(enemies) × copies`, **đã có**), **không** từ `rate`.
Xấu nhất 30 quân cùng lúc; nhịp còn lại do `rate` của các spawner khác. Vẫn cần **asm** để lên mức
**A** — nằm ở T5 của `HANDOFF_ANIM_RAW.md`.

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
| `rate = 0` (trong `waves.json`) | **2.366** | 2 | **30** |

⇒ **Nghiêng mạnh về "không giãn cách ⇒ spawn cả loạt"** (mức **B**): nếu `rate` là "số quân/giây"
thì 295 spawner `rate = 0` sẽ **không bao giờ** spawn, và 1.206 spawner `rate = 0` có **>1 quân**
(dài nhất **30**) sẽ là quân chết — vô lý trong một game đã phát hành.

**Không chặn thiết kế nữa:** mật độ tính từ **độ dài danh sách quân** (đã có), không từ `rate`. Xấu
nhất 30 quân cùng lúc; nhịp còn lại là do `rate` của **các spawner khác**. Vẫn cần asm để lên **A** —
việc đó vẫn nằm ở T5 của `HANDOFF_ANIM_RAW.md`.

---

## 4. Chỗ **thật sự** sẽ làm đau khi thiết kế — không phải mấy con số trên

Ba blocker còn lại (#3, #5, #8, #9) đều **không chặn L1**, vì L1 cho phép tự chọn số. Nhưng có hai
thứ mà *tự chọn* cũng không cứu được, vì chúng là **cảm giác**, không phải tham số.

### 4.1 Feel — hit flash / hit stop (câu #3): đo được một nửa → **ĐÓNG — BỎ (25/10)**

Vòng trước tài liệu này ghi *"là thứ duy nhất dữ liệu không có"*. **Sai một nửa.** Đọc asm
`Enemy_Display.OnHit` (352 B) thì thấy **2 hằng số**:

| chỗ | giá trị | nghĩa |
|---|---:|---|
| `Material.SetFloat(<tên tĩnh>, 0.5)` trong vòng `hitableRenderers` | **0,5** | nháy sáng/alpha khi trúng đòn |
| `Invoke(<tên tĩnh>, 0.05)` ở cuối hàm | **0,05 s** | thời gian tắt lại, bằng `Invoke` chứ không coroutine |

Còn thiếu: **tên tham số material** (chuỗi nằm trong bảng literal, chưa export).

#### 4.1b Soi lại 4 mục "feel" còn lại (25/10) — **3 mục không thấy trong mẫu 139 file asm**

> **SUPERSEDE (lần 143 — theo re-review Gate-1 `8141386a` comment `6444229646`):** mọi ô ⛔ "không tồn tại/không thấy trong game" dưới đây đọc đúng là **"không thấy trong mẫu 139 file asm đã bóc"** — KHÔNG phải bằng chứng vắng mặt toàn game (`MISSING_FOR_NEW_GAME.md:267`, `START_HERE.md:186`). Quyết định bản Godot không thêm hit-stop/aim-assist là **lựa chọn thiết kế mới**, không phải tái tạo trạng thái gốc.

Người chơi xác nhận *"chơi thật không thấy"*. Kiểm lại bằng dữ liệu thì **đúng**:

| mục | kết luận | bằng chứng |
|---|---|---|
| **hit flash** | ✅ **CÓ** | `Enemy_Display.OnHit`: alpha **0,5** + `Invoke(…, 0,05 s)` (claim **J9**) |
| **rung màn hình** | ✅ **CÓ** | `Enemy_CameraVibrate` **241** instance: `lvVibr` **0,05 / 0,10 / 0,15** · `timeVibr` **15 / 20 / 30 / 40** frame; phổ biến nhất **0,10 · 20 frame** (185/241) (claim **AF1**) |
| **tỉ lệ rơi đồ** | ✅ **CÓ** | 3 tầng đều đếm được — `ECONOMY.md` §8.1 (claim **AE1–AE3**) |
| **hit stop** | ⛔ **không thấy trong game** | chuỗi `timeScale` xuất hiện **0 lần** trong **139** file asm đã bóc (claim **AF2**). `GP_Controller.timeSlowed = 0,1` có trong `field-defaults.json` nhưng **không** có file asm cho `GP_Controller` ⇒ **chưa chứng minh** được nó bị dùng; người chơi không thấy ⇒ coi như **không có** |
| **aim assist** | ⛔ **không tồn tại** | **0** method khớp `aim · autoAim · targetLock · lockTarget` trong 139 file asm; `Player_Attack` (19 hàm) **không có** hàm chọn/bám mục tiêu — đạn đi thẳng |
| **input latency** | ⛔ **không phải tính năng** | thuộc input system + frame, không lớp nào trong game cấu hình |

⇒ Với 4 mục bị nghi là "feel phải đo", **3 mục không tồn tại** và **1 mục (rung) có số**. Nghĩa là
"feel" **không còn là khoảng trống tài liệu**: cái tồn tại đã có tham số, cái không tồn tại thì không
cần dựng lại. **Quyết định 25/10: BỎ feel** — game mới **không thêm** mục nào trong bảng này; mọi số
đo ở trên chỉ để tham khảo.

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
| đo playback trên máy | 🔴 0 lần | 🔴 **0 lần** — L2/L3 là **đích, KHÔNG hoãn** (lần 14 · report 96: **ưu tiên L3 trước**) ⇒ gate này **phải chạy** khi dựng cảnh/anim, không phải "nếu làm" |

⇒ Hệ quả: **thiết kế animation được ngay**. Cái duy nhất còn phụ thuộc dữ liệu là *điều kiện* máy
trạng thái của enemy — và nó **không chặn** vì L1 cho phép tự đặt điều kiện.

## 5. Bảng sẵn sàng theo hệ

| Hệ | Đủ để thiết kế? | Cơ sở |
|---|---|---|
| **Vòng lặp / wave / spawn** | ✅ **A** | 109 prefab roster · 282 wave · 11.089 dòng cấu hình · 22.451 entry spawn (`waves.json`) |
| **Độ khó / chế độ** | ✅ **A** | `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · 3 chế độ mỗi stage |
| **Kinh tế / sao / HP** | ✅ **A** cho hằng số | `StartHp 2500` · `stepCommon 0,18` · `DeltaStarCost 50` · `PercentToCompleteMissions222 [0.2,0.6,0.98]` |
| **Boss** | ✅ **A** cho cấu trúc | 46 boss · **39 prefab `Boss-*`** · **2 prefab Spine** (`Boss-39001/39002`) · 92 `Animator`/36 prefab · 795 event có mốc thời gian |
| **Enemy** | ✅ **A** cho cơ chế | **399 đường bay** theo path (tập prefab đã đọc) · `Enemy_Appear` = base nhận `Action` qua tham số (**chưa** rõ binding) · `Enemy_Display` 5 field |
| **Animation — *mốc trong clip*** | 🟡 **A** cho mốc / **C** cho điều kiện + hành vi | 33 prefab **793 event có mốc thời gian** · boss 1: **8 tên entry + 5 nhánh** chuyển state · nhịp đòn **0,17/0,33/1,0/5,0 s** · enemy = máy trạng thái 3 nhánh + hit flash **0,05 s** — xem **`ANIMATION_SCRIPT.md`** |
| **Animation — *playback / feel*** | ⛔ **ngoài phạm vi** (feel bỏ; *script* đã có) | 0/791 keyframe · 0 phép đo playback runtime · hành vi 12 handler còn **C** — **L2/L3 là đích KHÔNG hoãn** (lần 14 · report 96): playback = gate phải chạy khi dựng |
| **UI — cấu trúc** | ✅ **A** | **125 màn hình** (`screens.csv`: 125 dòng) · 53 board · 63 popup · 8 tab · screen graph + điều kiện mở từng popup ở `UI.md` |
| **UI — art** | 🟡 **B** | asset pack v2 **đã xuất bản** (release `windwings-assets-1.3.118`, **175.684.102 B**, SHA `4b18cc23…`, report 70 — `DATA_SYNC` §21) + **đã phân tích tĩnh tới mức pixel/mesh/scene**: pixel tái tạo **2185/2185** (report 72) · mesh/pivot/PPU/border (report 75) · **1377** SpriteRenderer scene mở đầu + 5 camera (reports 76/77); **chưa render/import approval**; **không bê file về repo này** (cấm) — L1 làm art mới nên **không cần** |

---

## 6. Kết luận

**Thiết kế được, ngay bây giờ, cho L1.** Sau vòng 2, **không còn hệ nào ở mức C/D mà L1 cần**:
vòng lặp, wave, spawn, độ khó, kinh tế, boss, enemy, **animation script**, UI cấu trúc — đều **A**
(hoặc **B** ở chỗ không chặn).

Ba việc nên làm **trước khi** vẽ bảng thiết kế chi tiết — đổi thứ tự so với vòng 1 vì animation đã
xong:

| | Việc | Vì sao trước | Giao ai |
|---:|---|---|---|
| 1 | ~~Chốt `rate = 0`~~ — **KHÉP 27/10** = **spawn cả loạt** (§3) | đã hẹp còn **B**; mật độ **không còn phụ thuộc** nó | nhánh dữ liệu (T5, cần asm) để lên mức **A** — **không chặn** |
| 2 | **A6 stage ↔ wave** | quyết định **số màn**; hiện chỉ 7/250 map chắc chắn | offline — tự làm được |
| 3 | ~~Prototype feel 30 giây~~ | **đã bỏ** theo chỉ đạo 25/10 (*"feel bỏ rồi, script là đủ"*) ⇒ không còn việc này | — |

Và **một việc không nên làm**: đừng chờ thêm **mốc thời gian** trong clip — đã có. Nhưng **đừng** gọi là
"đã có script": thứ tự pha, điều kiện chuyển state, số lần lặp và hành vi callback vẫn **C**. Chỉ *playback* là
thiếu — và L2/L3 là đích KHÔNG hoãn (lần 14 · report 96 ⇒ **ưu tiên L3 trước**): playback/feel phải được đo bằng máy khi dựng cảnh.

### 6.1 Vòng 3 (24/10) — ba thay đổi so với bảng trên

| Việc | Trước | Sau | Bằng chứng |
|---|---|---|---|
| **D3 — thứ tự pha boss** (`DESIGN_QUESTIONS.md`) | ❌ "chỉ có `__count`" | ⚠ **một phần** (hạ mức 25/10, review R1): **A** cho mốc trong clip, **C** cho thứ tự/điều kiện/hành vi | `795/795` event có `time` ⇒ `BOSS_ANIM_TIMELINE.md` |
| **E2 — hit flash** | ❌ "chưa đọc" | ✅ **ĐÓNG — BỎ (25/10)** | alpha **0,5** + `Invoke(…, 0,05 s)` trong `Enemy_Display.OnHit` — game mới không thêm |
| **A7 — mật độ địch** | ❌ | ⚠ **một nửa** — `rate = 0` **KHÉP (27/10)** | số quân = độ dài `listPrefabEnemies`; `rate = 0` = **2.366/11.089** (21,3 %) ⇒ **B: spawn cả loạt** — **không chặn** mật độ |

⇒ `DESIGN_QUESTIONS.md` nay là **48 câu · ✅ 33 · ⚠ 14 · ❌ 1** (claim **S2** giữ cho dòng tổng không lệch
bảng; lần 11 — 25/10: A6/B1 ✅ bind xong · C4 ⚠ mẫu runtime · E2/E3 ✅ ĐÓNG-BỎ). **Câu trả lời cho câu hỏi của tài liệu này không đổi: thiết kế được cho L1** — chỉ khác là
**animation không còn nằm trong danh sách "phải chờ"**, và **feel đã ra khỏi phạm vi** (chỉ đạo 25/10:
*bỏ feel, script là đủ*) ⇒ không còn hạng mục nào phải "quyết thay vì đo".

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
hành vi handler; Âm thanh: danh mục 92 id, chưa có trigger). Mục **mật độ** **không còn treo** `rate = 0` —
**27/10 đã KHÉP** = spawn cả loạt (§3). Số lượng đã có: **22.451 entry** / **45.659 quân thật** trên 282 wave.

### 7.1 Ba con số "đã sẵn sàng" đáng nhớ

| | Số | Nghĩa |
|---|---:|---|
| **35/39** | prefab boss có **nguồn** animation/event trong tập đã xét | 4 prefab còn lại **không có cả clip event lẫn Spine trong tập đó** — không phải "không có animation" |
| **125** | màn hình UI có cấu trúc | mỗi màn có điều kiện mở + dữ liệu cần load |
| **10/10** | mục design doc viết được ngay | `Call_Data` **23 field** đã có schema (`waves.json` + `SCRIPTS.md` §3) |

---

## 8. Trả lời "đủ chưa" bằng **số đếm** (cập nhật 25/10 lần 2 — không dùng %)

| tập | tổng | đủ / đóng | một phần | chưa |
|---|---:|---:|---:|---:|
| **15 dòng vùng năng lực** (`COVERAGE_AUDIT.md` §1) | 15 | **11** ✅ | **4** 🟡 | **0** 🔴 · **0** ⛔ (feel **đã đóng** — 3/6 mục có số, 3/6 không thấy trong mẫu 139 file asm (supersede 143), xem §4.1b) |
| **9 câu blocker** (§2 ở trên) | 9 | **4** ✅ (`StartHp` · `A6` · `B1` · feel-bỏ) | **4** 🟡 (`D3` · `C4` · `A7` · `B3`) | **1** 🔴 (`A5` — cần luật continue) |
| **48 câu design** (`DESIGN_QUESTIONS.md`) | 48 | **33** ✅ | **14** ⚠ | **1** ❌ (`A5`) |
| **6 chỗ thiếu** (`COVERAGE_AUDIT.md` §2) | 6 | **2** ✅ ĐÃ ĐÓNG | **4** | **0 chặn số** — sót 2 tái đối chiếu runtime (không chặn) |
| **claim tự kiểm** (`tools/verify-claims.py`) | **211** | **200** PASS | **11** SKIP | 0 FAIL *(đo lại 27/10 trên tip `f9566558`)* |

**Đọc bảng này thế nào:**

- **Đủ cho L1** (giống **cơ chế**, tự chọn số + art): **0** chỗ bắt buộc chờ dữ liệu mới; AI làm game
  mới bắt đầu được ngay từ `START_HERE.md` + `datas/`. Số theo **từng tàu/enemy/mode** đều có (bind xong).
- **L2 (khớp số bản gốc): KHÔNG còn thiếu số** — mọi giá trị đã decode + bind; **playback thật đã có**
  (phiên phone 23/10). Việc còn lại của L2 = **replay đối chiếu** khi có lần chạy mới (2 mục `CROSSCHECK`).
- **L3 (khớp trải nghiệm + art bản gốc): ĐÍCH của dự án học tập thiết kế — KHÔNG hoãn** (lần 14,
  25/10, chủ dự án: *"APK gốc đã thiết kế chuẩn trải nghiệm, phải copy; art cũng thế — chuẩn màu
  sắc, ánh sáng; sao lại hoãn"*). Nghiệm thu = **đối chiếu reference đo được bằng máy — KHÔNG cần
  playtest người thật**: `VISUAL_DESIGN.md` (khung **0,4813** · tương phản **0,45–0,80** · accent
  **≤10 %** gameplay / **~47 %** khung thưởng · chi tiết **13–22** · juice **0,05 s** + **0,10 · 20
  frame**; claim **AN1**, **AN2**) + so ảnh cùng scene + timeline **795** event + audio **15** rules.
  Input **đã đủ** (pack v2 + pixel/geometry/spine/font + metrics **35** ảnh). Bắt đầu khi **L1 chạy
  được**, **song song với L2**; art **vẽ lại theo chuẩn gốc**, file asset không lưu trong repo này.
  Phần tĩnh còn mở nhỏ nhất: **thứ tự pha boss** (C, 2 việc: 6 chuỗi `SetTrigger` + ai gán 12 delegate).

> **⛔ STATIC-COMPLETE CEILING REACHED (27/10, lần 122 — DS §24.111):** mọi hạng mục tĩnh-làm-được đã đóng (#1–#28 · #27 review 6/6 · #29 decode 149–160 · hàng H+D5+audit). Phần còn mở = runtime-gated (chỉ chủ dự án mở lại) / gated-cần-export / quyết-định-thiết-kế. Readiness không tăng thêm bằng phân tích tĩnh — các gate L2/L3 là việc sản phẩm.
