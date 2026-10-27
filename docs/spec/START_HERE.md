# START_HERE — dựng một game mới từ bộ spec này

> ## Mục đích của bộ spec này — đọc trước khi làm
>
> **Dịch ngược để có đủ thứ để thiết kế game mới theo cách BẮT CHƯỚC bản gốc** — dự án này không
> sáng tạo cơ chế mới. Điều này **giảm việc cho bạn, không phải thêm rào cản**:
>
> - **Cơ chế · logic · số · animation · nhịp · màu · ánh sáng: tra reference TRƯỚC khi tự suy** —
>   đa số đã có đáp án trong repo (`datas/` · hợp đồng · report). Chỗ tài liệu ghi **scoped unknown**
>   thì **đừng bịa** — ghi rõ như tài liệu và cần thêm đào mới hỏi bên nhánh dữ liệu.
> - **Việc thiết kế duy nhất là ART**: vẽ lại hình ảnh cho khác (worklist **624** mục —
>   `docs/assets/art-worklist.csv`), giữ chuẩn khung/màu/ánh sáng/nhịp theo `VISUAL_DESIGN.md`.
>   **Metrics là gate phát hiện lệch, chưa phải approval** — nghiệm thu = chạy automated
>   regression/reference checks và ĐẠT, không phải "tin là giống".
> - Cơ chế thể loại **đã có từ nghìn đời nay — mọi game trong thể loại bắt chước nhau**; cái làm
>   game nổi bật là hình ảnh. Chỗ tài liệu ghi "tự chọn" thì mới chọn — còn lại làm theo reference
>   là xong.

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
| `docs/apk-analysis/` | Báo cáo bóc APK + bảng CSV | **116** `.md` · **107** `.csv` · **83** ảnh chụp (35 dùng được để đo) | "Con số này ở đâu ra?" |
| `datas/` | JSON/CSV bóc trực tiếp | **34** file · 13 MB | wave, UI (**797** màn / **150.131** node), HP, boss, tàu, item, map, audio, text |
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
| `reverse-engineering/il2cpp/ia-resolved.json` | **Hex thật của mọi `InitializeArray`** | **576** mảng map · **6** mảng `Player_Get_Datas` (0 record lỗi) | **damage/rate/cost từng tàu**, danh sách wave của bảng map |
| `datas/player_start_stats.json` | 6 mảng đã decode + damage × rate (proxy — report 79) | **24** tàu · **16** bán được · **8** giá `−1` | dựng bảng cân bằng tàu, không đoán |
| `reverse-engineering/raw/player-loadout/` | Mảng int + asm `Player_Saved_Datas` | **5 blob · 49 int · 5/5 sha256 OK** | giá craft/unlock, chứng cứ save |
| `docs/spec/RAW_AUDIT.md` | **Sổ kiểm claim ↔ raw** | **180 RAW · 3 DOC · 28 CONST / 211** | biết số nào tái đo được, số nào "đo một lần" |
| `tools/` | **9** script đo lại được | — | `verify-claims.py`, `art-study.py`, `classify-by-atlas.py`, … |

**Cộng kho đo được (đếm bằng `AI1`):** **139** file asm · **142.136** dòng asm · **142** typetree · **126** bảng ScriptableObject · **42** contact sheet · **148** file `datas/`.

> **Đừng "sửa" 142.136 thành 142.131:** `wc -l *.asm.txt` cho **142.131** vì **`wc` đếm ký tự
> newline**, còn `AI1` đếm **dòng** (`sum(1 for _ in fh)` = `splitlines()`). **5** file
> `_probe_*.asm.txt` không có newline ở cuối ⇒ hơn **đúng 5** dòng. Cả hai số đều đúng, khác định
> nghĩa; verifier dùng số **142.136** (claim **AI1**).


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
| **L2** | đúng **số** (giá trị + nhịp spawn khớp bản gốc) | so bảng số | ⚠ **số đã decode + bind xong**; receivers 85–87 · producer/serialized **88** · công thức xu **89** · **wing barrels + 12 drone impl (90)** · **HP max tàu + `Board_Drones` consumer (91)** — sót: **DPS runtime** + **2 tái đối chiếu** `CROSSCHECK` · wing còn special/named leaves (mapping 12 drone + turnRate3 **ĐÓNG 92** · config 17/24 — 93 · Shoot/coroutine 13/22/23/24 — 94 · 5 pooled leaves — 95) · `Board_Players` · bind entry map · save schema (`MISSING` §2) |
| **L3** | khớp **trải nghiệm + art** bản gốc (chuẩn màu/sáng/nhịp) | đối chiếu reference: metrics + so ảnh + timeline/audio — **không cần người test** | 🎯 **ĐÍCH dự án — KHÔNG hoãn** · 🟡 **một phần** (đính chính lần 33): contract pixel/pivot/border đủ **vẽ lại từng sprite đã biết**; **chưa đủ L3 trọn** — 505 sprite unknown · chưa có bảng sprite→màn/prefab (UI chưa join) · rig spine inferred · metrics/so-ảnh/timeline là **gate chưa chạy**; bắt đầu phần đã biết **song song L2** sau khi L1 chạy được · **đổi ưu tiên (report 96 — theo chủ dự án): L3 TRƯỚC** — wing/map-save chỉ đào khi là dependency cảnh · **recipes L3 ĐÃ CÓ (97/98)**: inventory đủ **55.584** layout + composition **100.312** component (matrix 99.731) + **805 root views**/665 clips channel-exact/2.139 callbacks — xuất recipe: `l3_recipe.py --label Board_Pause` · **programs + probes (99)**: 232 controllers/667 states/343+125 transitions/666 leaves + **1.853 probe điểm trên đủ 665 clips, 0 unknown tại điểm probe** · **script-driven lifecycle (100)**: chuỗi Popup_QuitMissions ĐÓNG bằng source (SetPopup→SetActive→trigger Hide→event OffBoard→SetActive(false), cùng GO) + `l3_ui_drivers` (1.414/337 receivers · 687 exact links) · **layout native (101)**: quét 125.453 headers → **584 anchors + 1 scaler** · 6 camera writer joins · 576/8 uiCamera · probe 1080×2400 → half-height 12.000000953674316 (model = native) · **visual surface (102)**: scope 585 owners → 56.714 obj/11.380 renderers/**348 clips**/**79.907 bindings** · **Alert ĐÓNG mức source/model**: 4647→ctrl 78 (none44/alert42/fade43, alpha 0→0,784313738/0,125 s) · **composition (103)**: merge 101+102 → 57.480 obj · poses đủ 11.380 renderers (**558 scene / 10.822 template**) · 6 camera · **1.104 pairs = 558 pass/546 fail mask** · Alert: Game 3975 mask 7959 LOẠI layer5, Main 3976 mask 32 GIỮ — chưa render · **hướng kế (lần 43, chủ dự án): dừng tăng counts — compose layout-write + animation-write trên cùng Transform/renderer → camera, 2 probe cụ thể đã gửi PR12** · **frame compose (104 — peer làm trước/parallel)**: shared modeled state — native Start/Align + clip writes float32 trên CÙNG renderer (Alert: sizeY 19.200000762939453→24.000001907348633 + alpha f32 0.3921568989753723, double 0.3921568840742111 giữ riêng; Border_Info: Align worldY 7→8.440000534057617, propagation 320 descendants; customType23 ≠ CRC(m_Sprite); final `81fed2233` CI `40242708365` — fix camera-clip last-write + Start uiCamera current-ref; **reproduction từ artifact 5/5 PASS: after_start==before bit-exact · 320/320 delta 1.44 · f32(0.3921568840742111)=0.3921568989753723 · fade alpha0 giữ footprint**) · review = reproduction/counterexamples — datas/tests = inventory/gate, không phải % hoàn thiện · **runtime models (105-a5a74747)**: particle 954 hệ (join native 954/954, gradient/curve-keys chưa decode ⇒ alpha 1.0+cờ) · transition 468 (encoded giữ, scheduler từ chối; sửa đọc: 464 interruption = field-absent) · driven 67 route/52.400 (CRC 52/52; case box_gift clip 986) · **0 binding CanvasRenderer/CanvasGroup (kết luận âm)** · **108 (#15 PARTIAL)**: 308/308 graphs 1-layer + blending 0 + weight 0.0 ⇒ multi-layer NOT_EXERCISED (snapshot); API chỉ declaration — native interpolation MỞ (cần native bytes/on-device probe) · **106-ef6b75ef**: PixelSnap (round-even sau divideW, z/w+uv không snap) + **bilinear thật 46 texels** (clamp FULL texture ≠ crop) · spec **arithmetic review 9/9 PASS** (snap/bilinear/premul/over ×14, same-pixel alpha .05091579864714838→.08276148982721251) — CPU binary64 ≠ GPU · **109 (#20 L2 ĐÓNG)**: `Board_Players.GetPlayerPower` 0x12D5DFC đọc allBasicAtk@0x10/allDeltaAtk@0x18 → **basic[i]×(1+delta[i]×level)** → textPlayerPower — UI display path, combat semantics vẫn mở · **107-ef6b75ef (supporting #20)**: basic24 + delta24 **0,168/lv** — **KHÁC r90 ship-damage 0,16/lv** (2 hằng sống song song); spec f32+ties-even tái tạo 5420/8864 ✓ · **110 (#22 ĐÓNG bó scope)**: PLAYER_DEVICE_{ship}_{slot} 4-slot · Device id@0x10/lv@0x14/rank@0x18/instanceId@0x1C (khớp r89 hex) · chuỗi load → GetStatValue1/2; **GetDevice body CÓ ở nhánh dữ liệu r89 (Device_Saved_Data — batch110 chưa consult; sửa wording lần 58 theo ADDENDUM AI-1)**; durability/migration MỞ · #21 **ĐÓNG** (108-ef, provisional): 576 constructor field/index identities + 550 RELA + cap0/1024 canonical equal (review 4/5; container/mode-selection runtime tách) · **#18 ĐÓNG bó scope** (111-a5: 2680 dmg/4,8 s = damage·s; live MỞ) · **#23 ĐÓNG bó scope** (7 named specials; wing runtime MỞ) · #17: **3 lớp framing ĐÓNG** — payload 109 + metadata 110 (704.961 rows · 793→791 class74 · 322 SHA giao 109∩110) + UnityFS 111 (v8/2022.3.62f3 · own LZ4 · 136 blocks · fresh equal 110 SHA); **schema discovery MỞ** (builtin UnityPy DB) — **2 track ĐÓNG bounded**: AI-1 native fixture (112-ef `9c351b7660`: 0xB7E1BC·74.714 instr · 281 nodes · 308 fulltree-equal bằng native schema · 533/616 interruption corroborated) + AI-2 REPLICATION (120-a5: chuỗi 3 literal refs, pins AI-1) — schema discovery full vẫn MỞ (không TypeTree readback) · **#19 ĐÓNG bó scope** (119-a5: 12=10+2 RESOLVED · 10=10 khác build · map contents MỞ) → **L2 trắng board** · **#12 ĐÓNG bó scope** (112-a5: Popup_QuitMissions 495980→1974, clip1572/1573; **pixel projection MỞ**) · #19 CLAIMED a5 → **L2 phủ hết** · **105-ef6b75ef**: chain Board_Pause MỚI cùng Frame (597593→616420→493280→492598→274606→267691→**549984**; clip idle1495 alpha 0.5797794461250305, disjoint-commutation cùng snapshot; internal order proved ≠ Unity scheduling; custom23 VẪN unproved) + textured: atlas785/sprite2585/shader10753, UV render-key, **7 mip0 samples** (≠ GPU), GLSL từ LZ4) · **107-a5a74747 (#16 replication)**: artifact-level recount transition — **0 mismatch** (932 = 343+125+464 · 698+234 destination · 464 selector omit m_InterruptionSource; KHÔNG phải second APK decoder — tầng đó = #17 MỞ); còn: exact-identity legacy bất khả (peer đào tiếp theo chuỗi) · renderer_enabled unknown · gate chưa chạy |

> ⚠ **L3 là ĐÍCH của dự án học tập thiết kế — KHÔNG hoãn** (lần 14, 25/10; siết措 từ review peer
> lần 21): APK gốc là **chuẩn đã kiểm nghiệm** ⇒ **không cần blind A/B/playtest người thật**, nhưng
> **automated regression + reference checks vẫn bắt buộc** — metrics (`VISUAL_DESIGN` §5) là **gate
> phát hiện lệch**, đạt gate mới gọi khớp, không tự approval. Art vẽ lại theo chuẩn gốc; file asset
> gốc không lưu trong repo này (pack do peer giữ).

Không cần đọc hết 43 file trước khi bắt đầu. Tám con số này đủ để dựng khung chơi được:

| # | Cái gì | Số | Ở đâu (claim) |
|---:|---|---|---|
| 1 | Khung hình dọc | tỉ lệ **0,4813** (≈ 9:18,7) — **tham chiếu trên một thiết bị**, không phải canvas bắt buộc | `VISUAL_DESIGN.md` §1 (**AN1**) |
| 2 | Điều khiển | kéo ngón để lái · biên **20×25** · radius **15** unit | `GAMEPLAY.md` §1 |
| 3 | Súng / đạn | **458** cấu hình · damage **40–1.200** (median **400**) · **186** loại đạn | `COMBAT.md` §0 |
| 4 | Wave | **282** wave · **11.089** dòng · median **28,5** dòng/wave · **109** prefab enemy | `ENCOUNTERS.md` §1 (**AQ1/AQ4**) |
| 5 | Spawn | `rate` trung vị **1,0 s** · `y` **9,6** · radius **0,1** · **68 %** là `point_range` (**số đo, không phải luật**) — **khớp chéo runtime 25/10:** camera ortho **9,6** (report 77 peer `d66037d10`) ⇒ mép trên khung nhìn **= 9,6**; **report 78 peer `549a7b5b7c`:** ortho = `max(h/w × 5.4f, 9.6f)` — 9,6 là **sàn**, không cố định mọi màn hình | `SCRIPTS.md` §3 (**AQ6**) · `DATA_SYNC` §24.10–24.11 |
| 6 | Độ khó | **3** chế độ · `MaxModeIndex = 4` · `levelDelta [1, 2, 3.6, 3.6]` · **không** nhân số quân | `DIFFICULTY_MODES.md` §5 (**E1/E2**) |
| 7 | HP | HP bar trên **109/109** prefab · HP theo **id** (150 cặp) · **không có** `kHp[mode]` — chế độ đổi composition, không nhân HP | `ENEMY_HP_RUNTIME.md` §0 · `DIFFICULTY_MODES.md` §3–5 |
| 8 | Rơi đồ | **702** vật đặt sẵn (**676** coin / **26** item) · **246/2.094** slot có item · **6** loại | `ECONOMY.md` (**AE1–AE3**) |

> ⚠ **Đọc 8 số này đúng cách:** chúng là **mô tả phân bố** của bản gốc, **không** phải luật engine.
> `rate = 0` **chưa** chứng minh "spawn cả loạt cùng frame": report 53 cho thấy Path/Waypoints đưa `rate`
> vào `WaitForSeconds`, và 0 chỉ là một nhánh — **không** suy thứ tự thực thi. Muốn khác cũng được,
> nhưng phải **ghi là lựa chọn thiết kế**, không giả làm "đúng bản gốc".

Thứ tự dựng đề xuất + hoá đơn sản xuất: `GAMEPLAY.md` §7 · `DONE.md` · cái gì **chưa** có:
`MISSING_FOR_NEW_GAME.md` (13 hệ: **8 đủ · 5 một phần · 0 thiếu hoàn toàn**). Bộ **48 câu hỏi thiết kế**
phải tự trả lời (33 câu đã có số): `DESIGN_QUESTIONS.md`.

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

## 4. Đọc theo vai (đừng đọc tuần tự 43 file)

| Vai | Thứ tự |
|---|---|
| **AI/agent dựng game** | file này → `SYSTEM_MANIFEST.md` (hợp đồng 15 hệ: luật đã chứng minh vs tự chọn) → `MISSING_FOR_NEW_GAME.md` (13 hệ + **§6 gate 3 stage & khuôn victory**) → `GAMEPLAY.md` §0+§7 → `TUNING_KNOBS.md` → `ENEMY_BEHAVIOUR.md` §6 |
| **Designer / cân bằng** | `GAMEPLAY.md` §0 → `BALANCE.md` §0 → `COMBAT.md` §0 → `ECONOMY.md` §0 → `TUNING_KNOBS.md` |
| **Engineer gameplay** | `GAMEPLAY.md` → `COMBAT.md` → `ENCOUNTERS.md` → `UI.md` → `MISSIONS_STARS.md` |
| **Art / tech art** | `ART_STUDY.md` (số đo mẫu gốc) → `VISUAL_DESIGN.md` (luật khung) → `ASSETS.md` §1 (art direction) + §7 (atlas plan) |
| **Producer** | `COVERAGE_AUDIT.md` → `DONE.md` → `MISSING_FOR_NEW_GAME.md` → `AI_FEASIBILITY.md` §2 |

---

## 5. Hai mươi mốt cái bẫy — đọc trước khi viết design doc riêng

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
| 15 | **“573 blob còn lại cần dump”** | **576** là số `InitializeArray`; 3 entry mở đầu dựng bằng **literal store** ⇒ **không** trừ. Và hex đã có trong `reverse-engineering/il2cpp/ia-resolved.json` — thiếu là phần **bind**, không phải phần **dump** |
| 16 | **Cột `ints` = damage** | Cột đó là **bit pattern**. `PlayerCosts` là **int[24]**; ba mảng damage/rate là **float[24]**; hai mảng **float[3]** ⇒ phải unpack theo kiểu field |
| 17 | **Zip CRC PASS ⇒ đủ asset** | Pack draft có **151** path bị nhiều row cùng dùng · **321** row gộp path · **320** size mismatch; `complete APK reference` = **NOT ESTABLISHED** (`DATA_SYNC.md` §21.2). **Pack v2 identity-safe đã loại ghi đè** (3.038 object · 6 loại, report 70 peer `4fe0cef8e`) — vẫn chưa “đủ APK” *(runtime/visual approval)*; **nhưng đủ làm reference VẼ**: pixel tái tạo **2185/2185** (report 72) · mesh/pivot/border (75) · spine reference (71) · font reference (73/74) |
| 18 | **“Thiếu blob, phải xin nhánh kia dump lại”** | `ia-resolved.json` **đã có** **576** mảng Map + **6** mảng Player + 5 nhóm `Board_*` (17 method · **623** record). Thiếu là **decode + bind**, không phải dump. Trước khi xin dữ liệu: `grep reverse-engineering/` trước (`RAW_AUDIT` luật 4) |
| 19 | **`levelDelta` = 2,1 (hoặc 3,6 đọc bằng mắt)** | Float32 `0x40666666` = **3,6**; giải đúng ra **`[1, 0 · 2,0 · 3,6 · 3,6]`** — và nó scale **phần thưởng**, **không** scale HP (`BALANCE` §6.4, claim **IAB2**) |
| 20 | **“Thiếu bảng HP enemy, phải xin `.so`”** | 981 là **số prefab serialize**, không phải số dòng bảng. **HP đã có**: `datas/enemy_hp_by_id.json` = **150 cặp `id → HP`** (claim **WRH2**), parse từ `.cctor` **150 insert · 0 vòng lặp · 30001–38001** (claim **IAB1**). `15-enemy-hp.csv` chỉ là serialize (981 dòng · **467** > 0, `CB-*` 0/69 — claim **WRH1**); gộp lại **108/109** prefab spawn có số HP (claim **WRH5**). 3 class enemy đã có asm (claim **WRH3**) ⇒ `.so` **không** phải blocker |
| 21 | **“5 nhóm `Board_*` đã hiểu”** | Mới bind được **2** field (`allBasicAtk` float[24], `allDeltaAtk` = 0,168×24); 3 nhóm còn lại (Drones ×2, Endgame, Players.ctor) **chưa có consumer** ⇒ mức **B**, cấm gán “HP tàu = 4.640” (`MISSING` §2.2c) |


---

## 6. Tự kiểm trước khi tin bất kỳ con số nào

```bash
python3 tools/verify-claims.py                 # đọc dòng cuối: PASS/FAIL/SKIP/ERROR (đừng chép số vào đây)
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
