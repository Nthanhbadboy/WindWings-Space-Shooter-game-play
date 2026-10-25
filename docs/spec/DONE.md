# DONE — "hoàn hảo" nghĩa là gì, và kiểm bằng gì

> Mục đích: biến chữ **"hoàn hảo"** từ một tính từ thành **4 mức kiểm được**.
> Không mức nào dùng % tự đánh giá. Số đếm được ghi **(A)**, ước lượng ghi **(C)**.
> Mục cuối: **Còn thiếu / phải đoán**.

> **Sửa lại (lần 4 — 25/10, audit toàn bộ 42 tài liệu `docs/spec/` + 71 `.md` apk-analysis):**
> câu **“chưa có giá trị / thiếu blob / 573 / 957 static mức D”** đã **sai**, và sai ở nhiều file.
> Hiện trạng đúng: `reverse-engineering/il2cpp/ia-resolved.json` có **17 method · 623 record**
> (**576** Map + **6** Player + 5 nhóm `Board_*` + Tech 7 + Device 12 + Droid 3 + Stage 2 + GameDatas 1).
> **Cái thiếu là `bind`, không phải `dump`.** Còn **thật sự** thiếu: ~~HP enemy (150 float trong
> `.rodata`)~~ — **gạch bỏ ở lần 5**, đã có bảng — coin/gem delta, thưởng hộp, trọng số rơi,
> ngưỡng VIP, mapping wave→stage.
> Đã sửa: `BALANCE` §6 (thêm §6.10), `DATA_SYNC` §18.2 + §23, `MISSING` §2.2c, `OPEN_ISSUES` B3,
> `ENEMY_HP_RUNTIME` §0, `AI_FEASIBILITY` §1.7, `apk-analysis/31`. Claim mới: **IA6 · IA7 · IAB1 ·
> IAB2 · APKD1 · IA8**.
>
> **Sửa lại (lần 5 — 25/10, rà nốt các câu "xin dump"):** phát hiện 3 nhóm câu **ảo** mà lần 4 bỏ sót.
> (1) `datas/enemy_hp_by_id.json` **đã có 150 cặp `id → HP`** từ chính `.cctor` đang bị "xin"; 3 file
> asm `Enemy_Get_Datas` / `Enemy_Controller` / `Enemy_Health` **đã có 41 method** ⇒ **không cần `.so`,
> không cần dump lại class**. (2) `15-enemy-hp.csv` là **field serialize** — `CB-*` **0/69** dòng > 0 —
> nên câu "109/109 prefab có HP" ở lần 4 là **ảo ngược**; sửa thành 981 dòng · **467** > 0, gộp dict
> được **108/109** prefab spawn có số HP. (3) `waves.json` hiện có **0** dấu `?` · **109** prefab tên
> thật ⇒ mọi câu "45.659 entry = `?`" là lịch sử. Claim mới: **WRH1–WRH5** (thay 2 claim WRH cũ).
> Đã sửa thêm: `ENEMY_HP_RUNTIME` §2/§4/§5/§6, `WHERE_TO_LOOK` §3/§4, `ENCOUNTERS` §9, `COMBAT` §6.1,
> `DESIGN_QUESTIONS`, `README` §5, `AI_FEASIBILITY` §1.7/§2.1, `START_HERE` bẫy 20, `HANDOFF_REPLY` §6,
> `CROSS_BRANCH` · `CROSSCHECK`.
>
> **Sửa lại (lần 6 — 25/10, đọc chọn lọc report 70–74 của nhánh dữ liệu `4fe0cef8e`, không kéo file):**
> (1) **khôi phục L2/L3**: không còn “❌ bỏ” — L2 **hoãn sau L1**, L3 là **đích cuối** sau L2
> (ý chủ dự án); (2) sửa hướng dẫn cắt sprite: **KHÔNG clamp** 40 rect — round từng biên + pad 1 px
> cho 9 case (report 72) — sửa 3 chỗ trong `ASSET_TRIAGE` §9; (3) sửa `txt_free_after` English thành
> “Free after” (lookup **first-index**, report 73) trong 2 CSV; (4) bổ sung nguồn font thật
> (7 TMP SDF + fallback chain) vào `ASSETS.md`; (5) pack **v2 identity-safe** bổ sung vào §21.2 +
> bẫy 17. Chi tiết + 6 việc peer giao: `DATA_SYNC.md` §24.
>
> **Sửa lại (lần 7 — 25/10, sau khi bị nhắc "bind xong lâu rồi"):** rút lại toàn bộ câu
> "việc kế tiếp = bind" trong `MISSING` §2/§4/§5 — **bind chính đã xong từ trước**: index↔tàu
> = **id − 10001** (T4), cấu trúc bảng Map = **11 cấu trúc / 614 mảng** đã phân loại
> (`DIFFICULTY_MODES` §7), chi tiết entry đã ghép (`map_table_segments.json` + `maps.json`).
> **Còn thiếu thật sự** (4): `kHp[mode]` · `missionKillPercent` 6/9 số · `StartHpPoint`←`Init`
> `0x1582f5c` (1 method asm) · kiểm runtime `rate` (cần thiết bị). Cập nhật thêm report **75**
> (mesh 2185/27.072 vertex, không quad/PPU mặc định, không clamp) — `DATA_SYNC` §24.7–24.8.
>
> **Sửa lại (lần 8 — 25/10, sau khi bị nhắc "cả 4 đều đã có"):** ⚠ *khối này ĐÃ RÚT ở lần 9 (ngay dưới) — đọc lần 9 trước.* Rút lại "còn thiếu thật sự (4)" của
> lần 7 — **cả 4 đều đã có theo dạng khác**: ① `kHp[mode]` **không tồn tại** như hệ số (chế độ đổi
> composition + thưởng; `DIFFICULTY_MODES` §3–5); ② `missionKillPercent` là **một** `float[3]` theo
> mission index — đủ **3/3**, "3×3 còn 6" là ảo đơn vị; ③ `StartHpPoint` ← dict **đã bind theo id**
> (dict là nguồn, `Init` chỉ plumbing); ④ `rate` = **giây delay theo nhánh** (report 53) — không phải
> *shot/giây*. Số sửa: `MISSING` §2/§4/§5 · `DIFFICULTY_MODES` §5.2/§5.5/§6/§8 · `OPEN_ISSUES` B8 ·
> `COMBAT` §6.1 · `DESIGN_QUESTIONS` · `ENEMY_HP_RUNTIME` §6 · `START_HERE` số 7 · `WHERE_TO_LOOK` ×2 ·
> `EXTERNAL_REFS` §7 · `UNITY_RULES` · `DATA_SYNC` §24.8 · `BALANCE` §6.0a.
>
> **Sửa lại (lần 9 — 25/10, chủ dự án xác nhận):** ⚠ *lô tài liệu của lần này
> (`DESIGN_QUESTIONS` · `OPEN_ISSUES` D1 · `MISSING` §3/§4 · `DIFFICULTY` §5.5 · `UNITY_RULES` #7)
> KHÔNG vào tree — script abort, chỉ DONE + README kịp ghi; "tally ✅ 31 · ⚠ 16 · ❌ 1" dưới đây là
> số định, lần 11 kéo lại với tally thật **33/14/1** (E2 và E3 là 2 dòng riêng, đều ĐÓNG-BỎ).*
> (1) **playback thật ĐÃ LÀM** — phiên phone
> 23/10 nằm sẵn trong repo (`ramus/2026-10-23-phone/`): bridge 8/9 endpoint, freeze/slow-mo,
> statics khi đang chơi, 7 lần chụp live với instance fields (`killCount` **276** · `coinCount`
> **540**), HP trong game khớp **2500** ⇒ mọi mục "cần thiết bị" chuyển thành "đọc JSON có sẵn";
> (2) **feel BỎ theo quyết định** — game gốc không có (0 site trên mẫu asm) và quá nhỏ ⇒ game mới
> không thêm (`OPEN_ISSUES` D1 · `DESIGN_QUESTIONS` hạng 3 · `MISSING` §3). Mở lại 3 câu cũ trong
> `DESIGN_QUESTIONS`: **A6 ✅** (bind map xong) · **B1 ✅** (HP theo id) · **C4 ⚠** (mẫu runtime
> 276→540) — tally mới **✅ 31 · ⚠ 16 · ❌ 1**. Runtime còn sót: 2 phép tái đối chiếu `CROSSCHECK`
> (Map content `&arr=256&depth=2` · device 12↔10) — làm khi có lần chạy, không chặn.
>
> **Sửa lại (lần 10 — 25/10, đồng bộ peer tới report 77 / `d66037d10`, peer 239 tests):** đọc chọn
> lọc report **76** (SpriteRenderer scene mở đầu: 1377 root, 218 typed Sprite, đếm activity ≠ visible)
> và **77** (5 Camera + 12 SpriteMask, ortho **9,6** khớp mốc spawn y=9,6 của mình, culling mask
> disjoint Game/UI, cutoff 0,2 raw) — `DATA_SYNC` §24.9–24.10 + task peer 3 nhóm. `START_HERE` số 5
> thêm khớp chéo ortho. Phía peer đang làm CameraScaler (chưa có report). 2 phép tái đối chiếu
> runtime bên mình **giữ nguyên** — report 76/77 không đụng Map-content và device 12↔10.

> **Sửa lại (lần 20 — 25/10, đồng bộ report 84 peer tip `c7f72fe22e`, 327 tests):** peer dịch đủ
> **25 combat coroutine** (CFG + jump-table + models chạy được) — 3 đính chính ghi vào
> `SYSTEM_MANIFEST` (nhịp bắn) + `OPEN_ISSUES` D5 + `DATA_SYNC` §24.17: `_delay` 7/9 **sau** attack ·
> 17 chờ theo cặp · **18 = toggle particle, không spawn đạn**; clone 0,34/pumpkin 2-1-4. Peer chờ
> ack (PR12 `6399840843`) — đã ack sau khi cập nhật. Khối "mục đích" bên dữ liệu **vẫn chưa được
> commit** (grep tip = 0) ⇒ refresh `docs/HANDOFF_DATA_PURPOSE_6144d7cb.md` **v2** với anchor mới
> (report 84 đã đổi 3 chỗ chèn) + nhắc lại trên PR12.
>
> **Sửa lại (lần 19 — 25/10, vai "AI tiếp nhận" soi tài liệu — thiếu/nhất quán):** ① **worklist art**
> (thiếu lớn nhất cho nhiệm vụ thiết kế duy nhất — vẽ art): có số "~641" nhưng **không có danh sách**
> ⇒ tạo `tools/art-worklist.py` + `docs/assets/art-worklist.csv` (**624 thứ phải vẽ + font 292 glyph**,
> luật pin tái tạo được; "~641" = ước lượng cũ chênh ≈2,7 %); ② SYSTEM_MANIFEST/DATA_SYNC đánh dấu
> 3 file hợp đồng combat **chỉ có ở nhánh dữ liệu** (`combat_chain_contract` · `combat_argument_audit` ·
> `combat_rate_consumers` — xin qua PR12); ③ GAMEPLAY §0: "800 instance HP" → **981 + 150 cặp id** +
> trỏ path đầy đủ; DONE art row 641→**624** + link; ④ TUNING_KNOBS: "chạy AssetRipper" → pack v2 bên
> peer đã chứa binary. Kiểm khác: §-trỏ từ SYSTEM_MANIFEST/START_HERE **0 lệch**; MISSING §6 gate
> victory đủ; GAMEPLAY §7 thứ tự build giữ nguyên.
>
> **Sửa lại (lần 18 — 25/10, đồng bộ reports 80–83 peer tip `23b1ceec31` — ĐÍNH CHÍNH bind):**
> ① **"id − 10001" bị hẹp scope**: peer CFG-proof **72/72** getter call (report 82) + source prefab
> (report 81) ⇒ **combat**: impl `Player_Attack_N` đọc mảng index **N−1**, tàu **10001 → index 2**
> (proxy 12.864) · **10003 → index 0** (proxy 21.600) · 10004–10024 → id−10001; công thức cũ
> (`0x14e2ce4`) **giữ nguyên ở consumer save/load**. Sửa 8 file: MISSING §2.2/row 9/§2-đầu/§6 ·
> COMBAT §0/§6.1 · BALANCE §1.1b/§5.2 · DESIGN_READINESS ①/B3 · README 2 dòng · SYSTEM_MANIFEST ·
> DATA_SYNC §22.3/§24.8. ② **Nhịp bắn đủ 24/24** (report 83): interval nhóm phát — dual deadline,
> N extra ⇒ N+1 entry, không catch-up (80), modifier tech tier 0/3/5/8/10/12 % (82), demo override
> 3,0/4,0; OPEN_ISSUES D5 cập nhật A/B. ③ **Luật mất máu enemy** (81 §E): armor factor ±, overkill
> clamp 0, IsCaAttack@0x2F, noDamage 241/981 (sửa 189/800 cũ), Shield_Sub riêng; COMBAT §6.2.
> ④ 38 ends_clean = coroutine Reset/OnDrawGizmos — không cắt (đừng xin dump). DATA_SYNC §24.13–24.16.
>
> **Sửa lại (lần 17 — 25/10, chuyển bổ sung "mục đích" sang nhánh dữ liệu):** chủ dự án yêu cầu
> cập nhật cả bên nhánh dữ liệu. Khuôn phiên chỉ push nhánh spec ⇒ giao bằng kênh chuẩn: file
> **`docs/HANDOFF_DATA_PURPOSE_6144d7cb.md`** (3 chỗ chèn paste-ready vào `START_HERE_NEW_GAME.md` ·
> `HANDOFF_AI_TASKS.md` · `datas/README.md`, anchor trích từ tip **`ffa9959c9e`** — peer đã lên
> report 82, sync đầy đủ để vòng sau) + comment PR12 yêu cầu peer tự commit theo quy trình bên đó.
> Không đụng luật bằng chứng (mức A/B/C, pin SHA) — chỉ bổ sung mục đích sản phẩm.
>
> **Sửa lại (lần 16 — 25/10, chủ dự án: "đừng đóng đinh mọi thứ — chỉ thiết kế lại art là được"):**
> viết lại các khối "mục đích" của lần 15 theo hướng **giảm việc, không thêm rào cản**: bỏ giọng cấm
> đoán ("không được lệch hướng / không suy diễn / không cải tiến") → nói điều dương: **mọi thứ trừ
> art bản gốc đã trả lời hết — tra reference là xong, không test không hỏi; việc thiết kế duy nhất
> là vẽ lại art, giữ chuẩn ở `VISUAL_DESIGN`**. Sửa 7 chỗ: `START_HERE` (khối đầu) · `DONE` §2 ·
> `MISSING` §0 · `DESIGN_READINESS` · `SYSTEM_MANIFEST` · `VISUAL_DESIGN` · `README`.
>
> **Sửa lại (lần 15 — 25/10, chủ dự án chốt mục đích — ghi vào mọi điểm vào):** *"dịch ngược để làm
> gì: để có các thứ để từ đó thiết kế game mới theo cách **bắt chước**, chứ không phải phát triển
> game mới theo kiểu **sáng tạo**. Để AI phát triển mà không bị lệch hướng hay sai logic hay sai art
> hay animation và tất cả mọi thứ — **đã có bản gốc đối chiếu, không test không hỏi lại, có bản gốc
> trả lời**. Cơ chế game đã có từ nghìn đời nay, tất cả đều bắt chước nhau, thiết kế lại hình ảnh cho
> khác thôi."* — Ghi nguyên khối ở **đầu `START_HERE.md`** + dòng dẫn ở `DONE` §2 · `MISSING` §0 ·
> `DESIGN_READINESS` đầu trang · `SYSTEM_MANIFEST` header · `VISUAL_DESIGN` header (hình khác —
> chuẩn giữ). Kèm sửa lệch sót của lần 11: `DESIGN_READINESS` header ⑥ tally 31/16/1 → **33/14/1**.
> verify 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 14 — 25/10, chủ dự án đổi định nghĩa nghiệm thu L3):** *"không cần người test thật
> vì APK gốc đã thiết kế chuẩn trải nghiệm, ta phải copy những trải nghiệm ấy; art cũng thế — chuẩn
> màu sắc, ánh sáng; dự án để học tập thiết kế, sao lại hoãn"*. ⇒ **L3 đổi nghĩa + đổi thứ tự**:
> (a) nghiệm thu = **đối chiếu reference đo được bằng máy** (metrics `VISUAL_DESIGN` + so ảnh cùng
> scene + timeline 795 event + audio 15 rules) — **bỏ blind A/B + playtest thống kê**; (b) **KHÔNG
> hoãn** — đích của dự án, bắt đầu khi L1 chạy được, **song song với L2** (câu "đích cuối sau L2" của
> sáng cùng ngày bị thay); (c) input xác nhận **đã đủ** (pack v2 + pixel/geometry/spine/font +
> metrics 35 ảnh). Sửa: `DONE` §2 (L2 + L3) · §4.1 · `START_HERE` §2 · `MISSING` §4 ·
> `DESIGN_READINESS` đầu trang + §5 · `VISUAL_DESIGN` mở đầu + §6. Cụm "playtest người thật" trong
> log lần 11 bên dưới là **lịch sử, không còn đúng**.
>
> **Sửa lại (lần 13 — 25/10, audit "còn chỗ nào ngu" trước khi bàn giao AI mới):** sửa 6 chỗ mâu
> thuẫn/stale mà verifier không bắt (không có claim neo): `START_HERE` §2 **L2** ("6 blob rodata
> chưa bóc" — sai, số đã decode/bind; sót DPS-runtime + 2 tái đối chiếu) và **L3** ("bỏ" → **HOÃN,
> không bỏ**) + 2×"40 file" → 43 + §4 thêm `SYSTEM_MANIFEST.md`; `README` row Damage ("còn thiếu
> bind" → xong + proxy) + "phải decompile" (strike); `BALANCE` §5.2 (bind xong); `UNITY_RULES` §11
> row 1 `kHp` (không tồn tại) · row 2 `pct` (đã đọc [0,2/0,6/0,98]) · row 4 feel (BỎ); `DATA_SYNC`
> §22.3 "Vẫn chưa" 3/4 mục đã xong. Kiểm lại: MISSING §1 tally **8 đủ · 5 một phần · 0 thiếu**
> khớp `START_HERE`; `AI_FEASIBILITY` mức-B `.so` giữ nguyên (đúng — có guard chống xin .so cho HP).
> verify **209** PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 12 — 25/10, đồng bộ report 78–79 peer `549a7b5b7c`, peer 250 tests):** peer review
> nhánh mình tại `029559d47` + đào native nhịp bắn tàu 1 (raw `player-firing`). P0 qua PR12:
> ① DPS/TTK — **sửa rồi**: report 79 chứng minh tàu 1 dùng `StartMainCannonRate` làm **interval đặt
> hạn bắn** (deadline `@0x10c = Time.time + rate @0xa8`) ⇒ `damage × rate` chỉ là **proxy**, không
> giao như DPS; kèm **đính chính report 53** (delay spawn) từng bị dùng đóng nhầm consumer player —
> sửa `MISSING` §2.2, `COMBAT` §0/§6.1/§6.2, `BALANCE` §1.1b, `DESIGN_QUESTIONS` B4 (còn stale
> "thiếu StartHp"), `BOSSES`, `ENEMY_HP_RUNTIME`, `COVERAGE_AUDIT` §1; ② bind "chưa bind" → **ĐÃ
> XONG** ở COMBAT/BALANCE; ③ CameraScaler **report 78**: `ortho = max(h/w × 5.4f, 9.6f)` — 9,6 là
> **sàn**, không cố định (`DATA_SYNC` §24.11 + `START_HERE` số 5); ④ **`SYSTEM_MANIFEST.md`** mới —
> bảng tối giản `hệ thống → raw → luật → tự chọn → test` (task ⑤); ⑤ `OPEN_ISSUES` thêm **D5**.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK. Reply PR12 sau push + CI.
>
> **Sửa lại (lần 11 — 25/10, audit "giao thiết kế được chưa" + cứu lô lần 9):** audit 4 tài liệu
> điểm vào (`START_HERE` → `MISSING` → `DESIGN_READINESS` → `COVERAGE_AUDIT`) bắt stale: tally cũ
> 29/15/4 + claim "151/149" (thật **211 claim · 209 PASS · 2 SKIP**), "2 chặn map→wave + HP runtime"
> (**ĐÃ ĐÓNG** — bind xong + `kHp` không tồn tại), L3 ghi "BỎ" (sửa lại **HOÃN — đích cuối, không
> bỏ**), UI-art "chưa kéo về" (stale — pack v2 report 70), MISSING row 11 audio (**15 luật** trong
> `datas/audio_rules.json`, report 67), START_HERE bẫy 17→**21**. Cùng lúc phát hiện lô lần 9 mất
> (xem khối lần 9) — kéo lại hết: `DESIGN_QUESTIONS` A6/B1 ✅ · C4 ⚠ · E2/E3 ✅ ĐÓNG-BỎ (tally
> **33/14/1**), `OPEN_ISSUES` D1 BỎ, `MISSING` §3/§4, `COVERAGE_AUDIT` §0/§2/§5. **Kết quả audit:
> L1 GIAO ĐƯỢC** — 0 chặn số; thiếu thật = 2 tái đối chiếu runtime + playtest người thật (sau L2).
> verify **209** PASS · 0 FAIL · 2 SKIP · unittest 45 OK.
>
> **Sửa lại (lần 3):** pipeline vòng 3 (nhánh `ef6b75ef`, commit `61d5385`) đã resolve
> **tên enemy trong wave** — **22.451** entry, **109** prefab, **0** `"?"`. Đây là mục
> tôi từng ghi là "chưa biết". Số mới ở `ENCOUNTERS.md` §2.6.
>
> **Sửa lại (lần 2):** bản đầu của file này phóng đại khối lượng. Sau khi đọc **tên gốc** spawner
> và **dedup**, con số thật nhỏ hơn nhiều: **48 archetype spawner**, **109 prefab enemy được spawn**,
> **11.089 dòng / 10.782 cấu hình khác nhau** (median **28,5 dòng/wave**), **boss là 45 wave riêng**. Xem §1.

---

## 0. Trả lời ngắn

**"Game đơn giản" — đúng. "Bắt chước là ra" — đúng, nhưng chỉ tới một mức.**

| Mệnh đề | Đánh giá | Vì sao |
|---|---|---|
| Game **đơn giản về cơ chế** | ✅ **đúng** | 2.5D sprite · physics 2D · không netcode realtime · không navmesh · không rig 3D (§`AI_FEASIBILITY.md` §1.9) |
| **Bắt chước** cho ra game **chơi được** | ✅ **đúng** | cơ chế đã có đủ số; AI dựng được khung |
| Bắt chước cho ra game **hoàn hảo** | 🟡 **đúng một phần** | bắt chước giải quyết **thiết kế**, không giải quyết **khối lượng** và **kiểm chứng** |

> **Điểm cần tách:** *đơn giản* và *nhỏ* là **hai trục khác nhau**.
> Game này **đơn giản** (ít hệ thống phức tạp) nhưng **không nhỏ** (rất nhiều đơn vị nội dung).
> Bắt chước làm trục "đơn giản" rẻ đi gần như bằng 0. Nó **không** làm trục "khối lượng" rẻ đi.

---

## 1. Hoá đơn sản xuất — **sửa lại: nhỏ hơn tôi nói**

> ⚠ **Mục này bản trước sai** — nhưng sai vì **lẫn đơn vị**, không phải vì dữ liệu có bản trùng.
> `waves.json` có **11.089 dòng** (mỗi dòng = 1 `Call_Data`), và **23.757 lượt** (`Σ copies`).
> Câu "84,2 spawner/wave" là lấy **lượt/wave**; câu "1.015 cấu hình đặt tay" đúng (1.015 tên khác
> nhau), nhưng **1.015 tên rút về 53 tên gốc** — cả hai đều thật, ở hai mức khác nhau.

### 1.1 Quy luật spawn — có, và rất rõ

Tên spawner có dạng `TênGốc (n)` — **`(n)` chỉ là số thứ tự instance**, không phải cấu hình khác.
Bỏ hậu tố đó: **1.015 tên → 53 tên gốc**, trừ 5 marker (`StartPoint`/`EndPoint`/`CheckPlayerNo`/
`KhoaPlayer`/`Endpoint`) còn **48 archetype spawner thật**.

| Archetype | Số lần | `spawn_type` | `rate` | `y_spawn` |
|---|---:|---|---|---|
| `CB1 Nhanh` (nhanh) | 4.622 | point_range **100%** | **1,0 cho 4.622/4.622** | **9,6 cho 4.618** |
| `Point 1` | 4.192 | point / point_range | 1,0 (2.536) · 0,0 (1.656) | 12,0 (2.262) |
| `CB1 Vua` (vua) | 2.951 | point_range **100%** | **1,0 cho 2.951/2.951** | **9,6 cho 2.945** |
| `CB1 Cham` (chậm) | 1.487 | point_range **100%** | **1,0 cho 1.487/1.487** | **9,6 cho 1.487** |
| `6-CB09_Left` | 1.238 | point_range | 0,0 (1.172) | 9,6 (1.238) |
| `CB1` | 1.150 | point_range | 0,0 (953) | 12,0 (880) |
| `Path_CB3_5` | 1.130 | path **100%** | 0,5 (571) | 9,6 (1.114) |
| `Group` | 929 | point_range | 0,0 (929) | 0,0 (605) |
| `ChamNo` | 536 | point_range | 1,0 (536) | 9,6 (528) |
| `CB15` | 435 | point_range | 0,0 (359) | 0,0 (269) |
| `Point_H` | 387 | point | 0,0 (387) | 12,0 (387) |
| `CB1 Ban Vua` | 304 | point_range | 1,0 (304) | 9,6 (304) |

**Đọc ra:** mỗi archetype có **bộ tham số gần như hằng số**. `CB1 Nhanh` = "nhanh, một nhịp,
xuất hiện ở y 9,6" — chạy 4.622 lần với đúng cùng tham số. Đây là **quy luật**, không phải
đặt tay từng cái. **Bạn đúng.**

### 1.2 Ba đơn vị — và con số đúng cho từng câu hỏi

| Câu hỏi | Số đúng | Đơn vị |
|---|---:|---|
| Có bao nhiêu **cấu hình** spawn? | **11.089** | dòng = 1 `Call_Data` component |
| Có bao nhiêu **lượt sinh quân**? | **23.757** | `Σ copies` (bảng cũ ghi số này) |
| Bỏ marker thì còn bao nhiêu lượt? | **22.385** | `Σ copies` của dòng không phải `StartPoint`/`EndPoint` |
| Bao nhiêu **cấu hình khác nhau** (gộp `tên + type + rate + speed + y` trong từng wave)? | **10.782** | dòng, dedup **trong từng wave** (đo 25/10) |
| Median mỗi wave | **28,5 dòng** · **62 lượt** | — |

> **Cái từng bị gọi là "bản trùng export" thực ra là `copies`** — một field của dữ liệu, không
> phải lỗi export. Sau khi gộp theo 5 trường, **10.782 / 23.757 = 45,4 %** lượt là *cấu hình mới*;
> phần còn lại là **cùng cấu hình chạy nhiều lần** (`copies`).
>
> `> Nhận định (mức B):` nội dung wave **không phải** 23.757 lần đặt tay — mà là **~10.800 lần**
> chọn-trong-**48 archetype**-và-đặt-vị-trí (53 tên gốc − 5 marker). Đây là phần **tự động hoá được
> gần hết**.

### 1.3 Chỉ có **92 prefab enemy** — không phải hàng trăm

Đếm từ `Enemy_Datas.csv` theo **root của prefab path** (bỏ sub-object `Gun5`/`HP`/`Child2`):

| Họ | Số prefab | Dải id | Vai trò |
|---|---:|---|---|
| `CB` (30xxx) | **26** | 30001–30060 | enemy thường chương 1 |
| `CD` (31xxx) | **13** | 31002–31016 | " |
| `GD` (33xxx) | **4** | 33002–33005 | " |
| `XB` (34xxx) | **4** | 34003–34006 | " |
| `BB` (36xxx) | **3** | 36001–36004 | " |
| `H` (38xxx) | **2** | 38001–38002 | " |
| **Tổng enemy thường** | **52** | | |
| `Boss` (37xxx + 39xxx) | **39** | 37001–39021 | boss |
| `MB` (39xxx) | **1** | 39005 | mini-boss |
| **Tổng** | **92** | | |

**Bạn đúng lần nữa:** **52 loại enemy thường** + **40 boss-family**. Không phải 690 GameObject
như tôi ghi trước đó — 690 là **mọi** object trong prefab (súng, hitbox, con, hiệu ứng).

> ⚠ **Ba số "enemy" khác nhau — đừng tráo:**
> **92** = prefab có script `Enemy_Datas` (bảng trên) · **109** = tên prefab **thực sự được spawn**
> trong `waves.json` (đo 25/10) · **189** = mọi GameObject có HP trong `datas/enemy_hp.json`.
> Khi nói "game có bao nhiêu loại quân" thì dùng **109**; **92** là số *loại có script HP*.

> **Đã resolve (vòng 3):** **22.451** entry · **109** prefab · **0** `"?"` — xem `ENCOUNTERS.md` §2.6.
> Trần nội dung enemy là **109 prefab**, không phải hàng chục nghìn.

### 1.4 Boss là **màn riêng** — xác nhận

| Nhóm wave | Số wave | Vai trò |
|---|---:|---|
| `Wave_00xx` – `Wave_02xx` | **236** | campaign thường |
| `Wave_70xx` | **22** | **boss chương 1** — màn riêng |
| `Wave_90xx` | **23** | **boss chương 2** — màn riêng |
| `unknown` | 1 | lỗi export |
| **Tổng** | **282** | |

Board cũng tách: `Stage_Behaviour.stageType` = Normal **199** · **Combat 49** · Boss **26** ·
MiniBoss **25** (nguồn: `Stage_Behaviour.csv`).

> **Sửa lỗi đọc trước:** tôi từng ghi "686 spawner `spawn_type = boss`". Sai — `boss` ở đây là
> **marker `EndMapPoint`**: **327 dòng = 686 lượt**, có ở **gần như mọi** wave; `special` là
> **`StartPoint`**: **281 dòng = 686 lượt** (hai số 686 trùng nhau, đừng đọc thành một).
> Nội dung boss nằm ở **45 wave riêng** (`70xx`/`90xx`).

### 1.6 Art cũng co lại — **2.185 sprite → ~641 thứ phải vẽ**

Đếm từ `04-asset-manifest.csv` (2.185 Sprite), bỏ hậu tố `(n)`/`_n`/số cuối:

| Nhóm | Số | Ghi chú |
|---|---:|---|
| Sprite ghi nhận | **2.185** | |
| Glyph / ký tự (1–2 ký tự hoặc toàn số) | **292** | `%` `+` `1`…`9` — **một bộ bitmap font**, không phải 292 hình |
| Sprite còn lại | **1.893** | |
| **Tên gốc sau dedup** | **~641** | biến thể màu/frame gộp về một |
| **Tỉ lệ nén** | **~3,4×** | |

**Hệ quả:** hoá đơn art là **~641 hình + 1 bộ font**, không phải 2.185.
**Danh sách thật để vẽ (lần 19):** `docs/assets/art-worklist.csv` — **624 thứ phải vẽ + 1 bộ font
292 glyph**, sinh bằng `tools/art-worklist.py` từ `docs/apk-analysis/04-asset-manifest.csv`
(luật pin: glyph = ≤2 ký tự/toàn số; gốc = lowercase + bỏ `(n)` + bỏ đuôi số ×2; số "~641" ở bảng
trên là **ước lượng cũ** — chênh 624 vs 641 ≈ 2,7 %, dùng danh sách cho việc vẽ).
Với năng suất 10 hình/ngày, đó là **~64 ngày làm việc** — khớp với ước lượng
**2–3 tháng/1 artist** đã ghi ở `AI_FEASIBILITY.md` §6. **Ước lượng đó giữ nguyên**, nhưng
lý do đúng hơn: không phải vì "2.185 hình" mà vì **641 hình + sửa đi sửa lại**.

> `> Nhận định (mức B):` đây là lần thứ **ba** trong phiên này mà một con số lớn co lại khi
> đọc đúng tên gốc (spawner 1.015→53 · enemy 690→92 · sprite 2.185→641). Quy luật: **dữ liệu
> export đếm theo instance, không theo loại.** Con số "loại" luôn nhỏ hơn nhiều.

### 1.5 Hoá đơn còn lại

| Hạng mục | Số lượng (A) | Nguồn |
|---|---:|---|
| Wave | **282** = 236 campaign + 45 boss + 1 lỗi | `waves.json` |
| Cấu hình khác nhau **sau dedup** | **10.782** | tính lại §1.2 |
| Archetype spawner | **48** (+5 marker) | tính lại §1.1 |
| Prefab enemy | **92** = 52 thường + 39 boss + 1 MB | `Enemy_Datas.csv` §1.3 |
| Stage trên board | **299** (Normal 199 · Combat 49 · Boss 26 · MiniBoss 25) | `Stage_Behaviour.csv` |
| `Gun_Attack` → cấu hình súng | **458 → 420** | `Gun_Attack.csv` |
| Ô shop | **315** trên **20** board | `Shop_Cell.csv` |
| Class UI | **125** | `class-inventory.csv` |
| Sprite ghi nhận | **2.185** | `docs/apk-analysis/04-asset-manifest.csv` |
| **Art phải vẽ (sau dedup)** | **624** tên gốc + **1 bộ font 292 glyph** | `docs/assets/art-worklist.csv` (`tools/art-worklist.py`; §1.6) |
| Atlas page | **67** · 31,0 MB | `04-asset-manifest.csv` |
| AudioClip | **69** | `04-unity-assets.md` |
| Chuỗi localization | **1.416** | `12-localization.csv` |
| SKU IAP | **170** | `IAPProduct.csv` |

## 2. Bốn mức "hoàn hảo" — và mỗi mức kiểm bằng gì

> **Mục đích tổng** (khối đầu `START_HERE.md`): dịch ngược để **bắt chước bản gốc** — mọi thứ trừ
> art đã có đáp án sẵn (tra reference là xong, không test không hỏi); **việc thiết kế duy nhất là art**.

Thay vì tranh luận, định nghĩa **4 mức tăng dần**, mỗi mức có **bài kiểm cụ thể**.

### L0 — Chạy được

| | |
|---|---|
| **Nghĩa** | build mở được, vào màn, bắn, chết, qua màn |
| **Kiểm bằng** | máy: chạy 30 phút không crash, không log error |
| **Đạt khi** | 100% màn chơi không exception |
| **Bắt chước đủ?** | ✅ **đủ** — đây là mức AI làm tốt nhất |
| **Chi phí** | thấp |

### L1 — Đúng luật

| | |
|---|---|
| **Nghĩa** | cơ chế hành xử đúng như spec, không chỉ "giống giống" |
| **Kiểm bằng** | máy: **test tự động** đối chiếu từng con số đã có (mức A) |
| **Ví dụ test cụ thể** | wave 0163 spawn **622** spawner · `rate` mặc định **1,0** (16.173 spawner) · `y_spawn` **9,6** (15.485) · vùng chơi **20×25** unit · bán kính va chạm đạn **15** · `border.w` 15 cho **799/800** |
| **Đạt khi** | **100%** test pass |
| **Bắt chước đủ?** | ✅ **đủ cho phần đã có số** — nhưng phải **viết test**, bắt chước không sinh ra test |
| **Chi phí** | trung bình |

> Đây là mức mà `Spec2Game` đo được **Rule & Mechanism 45,6/100** — tức mức mà AI **hay trượt nhất**
> khi chỉ có đặc tả. Cách chặn: **test viết trước**, không phải review bằng mắt.

### L2 — Đúng số

| | |
|---|---|
| **Nghĩa** | cùng một phát bắn ra **cùng một lượng damage**; cùng một wave ra **cùng nhịp** |
| **Kiểm bằng** | máy: replay 1 wave, so DPS/TTK/HP với bản gốc trong **dung sai khai báo trước** |
| **Đạt khi** | (dung sai do bạn chọn — ví dụ ±5%) |
| **Bắt chước đủ?** | ✅ **đủ** (lần 14, 25/10) — mọi giá trị đã decode + bind xong |
| **Đã có gì** | 6 mảng `Player_Get_Datas` (bind: save/load **id−10001** · combat **impl N→index N−1**, report 81/82) · **576** mảng `Map_Get_Datas` (**11 cấu trúc**, `DIFFICULTY_MODES` §7) · **150 cặp HP enemy** · `StartHpPoint`←dict · `kHp` **không tồn tại** (`DIFFICULTY_MODES` §3–5) |
| **Còn thiếu** | chứng minh **DPS runtime** (report 79 — `rate` = interval; peer làm parity tàu 1) + **2** tái đối chiếu `CROSSCHECK` |
| **Chi phí** | ~~AssetRipper + Ghidra~~ → **không cần tool** — replay + đối chiếu |

> L2 là mức **"bắt chước" đúng nghĩa nhất** — **số đã đủ hôm nay**; sót việc **chứng minh nhịp bắn
> runtime** (việc của nhánh dữ liệu).

### L3 — Không phân biệt được

| | |
|---|---|
| **Nghĩa** | game mới **tái lập trải nghiệm + art của bản gốc 1:1** — chuẩn màu, ánh sáng, khung, nhịp (APK gốc là **chuẩn trải nghiệm đã kiểm nghiệm**; dự án = **học tập thiết kế**) |
| **Kiểm bằng** | **đối chiếu reference — đo được bằng máy, KHÔNG cần người test thật**: metrics `VISUAL_DESIGN` trong dung sai · so ảnh cùng scene · timeline khớp **795** event · audio khớp **15** rules |
| **Đạt khi** | mọi chỉ số khớp reference trong **dung sai khai báo trước** |
| **Bắt chước đủ?** | ✅ **có** — input đã đủ: pack v2 (report 70) + pixel/geometry/spine/font contract + metrics **35** ảnh chụp thật |
| **Chi phí** | sản xuất art + đối chiếu — **không cần playtest** |

> **Đây là đích của dự án — KHÔNG hoãn** (lần 14, 25/10, chủ dự án: *"không cần người test thật vì
> APK gốc đã thiết kế chuẩn trải nghiệm, ta phải copy những trải nghiệm ấy; art cũng thế — chuẩn màu
> sắc, ánh sáng; để học tập thiết kế, sao lại hoãn"*). Bắt đầu ngay khi **L1 chạy được**, làm **song
> song với L2**. Reference dùng để **đo và vẽ lại**; repo spec không lưu asset (pack do peer giữ).
> Định nghĩa blind-A/B cũ chỉ còn giá trị tham khảo — **đã bị thay**.

---

## 3. Bắt chước giải quyết cái gì — bằng số

| Việc | Bắt chước có giúp? | Vì sao |
|---|---|---|
| Biết **cần làm gì** | ✅ **gần hết** | 22.451 entry enemy, 109 prefab, 48 archetype, 420 súng — **đã có danh sách** |
| Biết **con số đúng** | 🟡 **một phần** | 25 hằng số đọc ngay; 5.818 field còn ở mức D |
| **Làm ra** 282 wave × 84 spawner | ❌ **không** | khối lượng, không phải hiểu biết |
| **Vẽ** 2.185 sprite thay thế | ❌ **không** | gu thẩm mỹ |
| **Đo** cảm giác (L3) | ❌ **không** | cần người chơi thật |
| Chọn **bỏ gì, thêm gì** | ❌ **không** | quyết định thiết kế |

> **Cách nói chính xác:** bắt chước biến **"không biết làm gì"** thành **"biết phải làm gì, rất nhiều"**.
> Đó là một bước rất lớn — nhưng nó **không** làm bước "làm" biến mất.

---

## 4. Chỗ tôi đồng ý với bạn, và chỗ tôi phải nói khác

### Đồng ý

- Game này **đơn giản** — so với 3D open world hay realtime PvP, nó **dễ hơn nhiều lần**.
- **Bắt chước là chiến lược đúng** — không phải đạo đức giả; rất nhiều game mobile thành công
  là "cùng thể loại, khác art". Đó là **bình thường** trong ngành.
- Một đội 3 người + AI **có thể** ra sản phẩm **người chơi thấy tương đương**. Đó là mục tiêu thật.

### Nói khác

- **"Hoàn hảo" phải định nghĩa ở mức nào** — L0/L1/L2/L3 ở trên. Không có định nghĩa thì không
  kiểm được, và cái gì không kiểm được thì không biết đã đạt chưa.
- **Đơn giản và nhỏ — cả hai đều đúng ở đây.** 48 archetype + 92 prefab enemy là **bộ từ vựng nhỏ**.
  Khối lượng thật là **11.089 dòng** (**10.782** cấu hình khác nhau), median **28,5 dòng/wave** — không phải 84.
- **Đã resolve xong:** pipeline vòng 3 đọc được **22.451** entry · **109** prefab · **0** `"?"`.
  Trần nội dung enemy là **109 prefab** — không phải 45.659 thiết kế mới.

> `> Kết luận (mức B):` bắt chước đưa bạn tới **L1** nhanh. **L2** cần 2 tool. **L3** cần
> vòng playtest. Ba mức này **không loại trừ nhau** — chúng là **ba khoản chi phí khác nhau**,
> và không khoản nào là "không cần làm".

---

## 4.1 "Không có gì là không thể" — đúng ở đâu, và chữ "dễ" che mất gì

Sau ba lần số co lại (spawner · enemy · sprite), có thể kết luận: **chưa tìm thấy bức tường nào**.
Nhưng "không có gì không thể" là câu về **khả năng**; "quá dễ dàng" là câu về **thời gian**.
Hai câu khác nhau, và cái thứ hai mới là cái quyết định.

### Phân loại phần còn lại — theo **lý do** thiếu, không theo độ khó

| Loại | Nội dung | Vì sao còn thiếu | Cách xử lý | Bản chất |
|---|---|---|---|---|
| **1. Chưa đọc** | 4.861 `[SerializeField]` · 957 `static` | chưa chạy AssetRipper/Ghidra | chạy 2 tool | **ngắn**, không khó |
| **2. Chưa chọn** | dung sai L2 · ngưỡng N cho L3 · bộ archetype nào đưa vào game | chưa ai quyết | quyết định thiết kế | **ngắn** |
| **3. Chưa làm** | ~641 hình art · 69 audio · **10.782** cấu hình wave · 1.416 chuỗi | **không nằm trong APK để đọc** — phải tự sinh ra | sản xuất | **dài**, không khó |
| **4. Ngoài sản phẩm** | giá IAP · live-ops · dữ liệu người chơi | không thuộc bản build | quan sát, không trích xuất | **không cần** cho bản clone |

> **Không loại nào là "không thể".** Nhưng loại **3** là loại duy nhất **không rút ngắn bằng
> cách đọc thêm file** — vì nó là **sản xuất**, không phải **khảo sát**.

### Vì sao "dễ" là từ nguy hiểm ở đây

| Việc | Loại | Có rút ngắn được bằng hiểu biết? |
|---|---|---|
| Biết 48 archetype thay vì 1.015 tên | 1 | ✅ rút từ **nhiều tuần** xuống **một buổi** |
| Biết 641 hình thay vì 2.185 sprite | 1 | ✅ rút 3,4× |
| **Vẽ** 641 hình | 3 | ❌ **không** — hiểu biết không vẽ hộ |
| **Chạy** 100 vòng playtest | 3 | ❌ không — nhưng AI làm mỗi vòng **rẻ hơn** |
| Biết damage player | 1 | ✅ sau khi chạy Ghidra |

> `> Kết luận (mức B):` hiểu biết đã **gần như miễn phí** — đó là phần bạn đúng, và đúng
> nhiều hơn tôi dự đoán ban đầu. Nhưng thứ còn lại không phải "khó", mà là **"phải làm"**.
> Với một game 2.5D, "phải làm" nghĩa là **~641 hình + ~11k placement + vài chục vòng test** —
> đó là **lịch**, không phải **rào cản**.

## 4.2 Phạm vi đã chốt — **L1: giống cơ chế, không cần giống số**

> **Quyết định của chủ dự án (ghi lại nguyên văn ý):** bắt chước + sáng tạo đôi chút;
> **không cần** test cho giống bản gốc; **giống cơ chế là đủ**.
>
> Đây là **mục tiêu L1**, và nó **hợp lệ** — không phải nhượng bộ. Nhiều game thành công
> đi đúng con đường này. Mục này ghi lại **cái gì rơi khỏi kế hoạch** khi chọn L1.

### Cái gì rơi khỏi kế hoạch

| Mục | Trước (mục tiêu L3) | **Sau khi chốt L1** | Hệ quả |
|---|---|---|---|
| **L2 — đúng số** | bắt buộc | ✅ **số đã đủ — làm ngay sau L1** | giá trị decode + bind xong; sót chứng minh **DPS runtime** (peer parity tàu 1) + 2 tái đối chiếu |
| **L3 — khớp trải nghiệm + art** | bắt buộc | ✅ **ĐÍCH dự án — KHÔNG hoãn** | đối chiếu reference đo được (metrics + so ảnh + timeline/audio) — **song song L2** sau khi L1 chạy được, **không cần người test** |
| Giá trị **4.861** `[SerializeField]` | phải có | 🟡 **tuỳ chọn** | dùng làm **tham khảo**, không phải để khớp |
| Giá trị **957** `static` | phải có | 🟡 **tuỳ chọn** | " |
| **45.659** tham chiếu enemy | phải resolve | 🟡 **tuỳ chọn** | danh sách **109 prefab** (đã resolve) đủ để chọn |
| 1.416 chuỗi localization | phải có | 🟡 **có sẵn** | **1.415 key nonempty, lookup first-index** (report 73 peer `4fe0cef8e`) — dùng hoặc viết riêng đều được |
| 170 SKU IAP | phải khớp | ❌ **bỏ** | tự thiết kế shop |
| 282 wave | phải đủ | 🟡 **tự chọn số** | 20–40 wave là đủ cho bản đầu |

### Cái gì **vẫn** phải có — vì L1 cần

Đây là phần **không đọc được ở đâu khác**, và cũng là phần **đã có sẵn trong spec**:

| Cần | Đã có | Nguồn |
|---|---|---|
| Vùng chơi | **20 × 25** unit, `border` 15/−10/10/−15 | `ENEMY_BEHAVIOUR.md` §1 |
| Bán kính va chạm đạn | **15** unit (799/800) | `COMBAT.md` |
| Tốc độ enemy | **0,2–30**, median **5,0**; wave 3,5 · boss 5,0 | `ENEMY_BEHAVIOUR.md` §1 |
| 48 archetype spawn + tham số | bảng đầy đủ (`rate` 1,0 · `y` 9,6 · `spawn_type`) | `ENCOUNTERS.md` §2.4 |
| 92 prefab enemy + HP | 800 dòng HP, 39 boss | `BALANCE.md` §2–5 |
| 420 cấu hình súng + damage | damage 40–1.200, median 400 | `COMBAT.md` §2 |
| 6 dạng đạn + `bltSpeed`/`lifetime` | đầy đủ | `COMBAT.md` §7 |
| Nhịp wave | median **28** placement/wave, max 255 | `ENCOUNTERS.md` §1.3 |
| 9 component/enemy | kiến trúc chuẩn | `ENEMY_BEHAVIOUR.md` §6 |
| Atlas + tỉ lệ màn | 9:16, page ≤ 2048², **~641 hình** | `ASSETS.md`, `DONE.md` §1.6 |

> **Không có dòng nào trong bảng trên cần chạy thêm tool.** Toàn bộ đã nằm trong 14 file spec.

### Vậy thứ duy nhất còn lại là gì

| Việc | Có bắt buộc? | Ghi chú |
|---|---|---|
| Dựng khung gameplay theo 9 component + 48 archetype | ✅ **bắt buộc** | AI làm được, spec đủ số |
| Tự chọn **damage/HP player** | ✅ bắt buộc | không cần khớp bản gốc — **tự cân** |
| Tự chọn **số wave** (khuyến nghị 20–40) | ✅ bắt buộc | không cần 282 |
| Vẽ **~641 hình** (hoặc ít hơn nếu giảm phạm vi) | ✅ bắt buộc | **đường găng thật** |
| Viết text riêng + audio riêng | ✅ bắt buộc | |
| Playtest **để tự thấy ổn**, không để khớp bản gốc | ✅ bắt buộc | rẻ hơn nhiều so với L3 |
| Chạy AssetRipper/Ghidra | ❌ **không** | chỉ khi tò mò một thông số cụ thể |

> `> Kết luận (mức B):` chọn L1 làm **rơi khỏi kế hoạch toàn bộ loại 1 và 2** ở §4.1
> (chưa đọc · chưa chọn) — tức **hai tool và mọi tranh luận về dung sai**.
> Phần còn lại là **loại 3: sản xuất**, và quy mô do bạn tự đặt, không do bản gốc áp.
> **L2/L3 không bị bỏ** (sửa 25/10): L2 **làm ngay sau L1** — số đã decode + bind xong.
> **L3 KHÔNG hoãn** (lần 14, 25/10): APK gốc là chuẩn trải nghiệm đã kiểm nghiệm ⇒ nghiệm thu =
> **đối chiếu reference đo được** (không cần blind A/B/playtest); bắt đầu khi L1 chạy được, song song L2.

## 5. Còn thiếu / phải đoán

| # | Thứ | Mức | Ghi chú |
|---:|---|---|---|
| 1 | Giá trị **5.818** field (`4.861` serialized + `957` static) | **D** | chưa chạy AssetRipper/Ghidra |
| 2 | ~~45.659 tham chiếu enemy~~ | ~~D~~ → **A** | ✅ **đã resolve** (`ENCOUNTERS.md` §2.6): 22.451 entry · 109 prefab |
| 3 | Ngưỡng N người cho test L3 | **C** | phải tự chọn; chưa ai trong dự án đo |
| 4 | Dung sai cho L2 | **C** | phải tự chọn (đề xuất ±5%, chưa có cơ sở) |
| 5 | Thời gian làm 282 wave | **C** | không đoán ở đây; phụ thuộc công cụ authoring |

> Không có dòng nào trong bảng này là "không thể". Cả 5 dòng đều là **"chưa chọn"** hoặc
> **"chưa chạy"** — hai trạng thái khác nhau, và cả hai đều **đổi được**.
>
> **Sau khi chốt phạm vi L1 (§4.2):** dòng 1, 2 và 4 **không còn là yêu cầu** — chúng chỉ còn
> là thông tin tham khảo. Dòng 3 và 5 vẫn phải chọn, nhưng chọn **theo ý mình**, không theo bản gốc.

---

## 12. Cập nhật 25/10 (lần 3) — đơn vị spawner, và geometry có toạ độ

| Việc | Trước | **Sau (đo lại)** | Bằng chứng |
|---|---|---|---|
| "spawner" là gì | 11.089 (gọi là spawner) | **spawner = 23.757 `Call_Data` object**; 11.089 = **dòng cấu hình** (đã gộp object trùng, mỗi dòng mang `copies`) | `Σ copies` = 23.757 = `class-inventory.csv` → **AQ7** |
| Dòng thật (bỏ mốc wave) | 10.493 | **10.481** (bỏ **608** dòng `StartPoint`/`EndPoint`) | `spawn_type` boss 327 + special 281 = 608 |
| Tổng có đổi khi đồng bộ `622b700e5`? | tưởng "không đổi" | **9 wave + `unknown` đã đổi** (`Σ copies` vẫn 23.757) | `DATA_SYNC.md` §17.1 |
| Sprite có toạ độ chưa | chưa | **2.185** sprite resolve `m_RD` · **40** rect lọt ngoài texture · **144** cần lật/xoay | report 62, `DATA_SYNC.md` §17.3 |
| 340 `unresolved` | 0 ca dùng được trang atlas | **282** ca biết trang thật, **18** gán được (precision ≥ 0,95) | `ASSET_TRIAGE.md` §9.6b (**AT1**) |

> ⚠ Geometry là **join metadata** (`PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`) — **không**
> phải bằng chứng "ảnh đã cắt đúng". 6 chunk `objects-*.jsonl.gz` **chưa kéo** ⇒ chưa tự kiểm `sha256`.

---

## 13. Cập nhật 25/10 (lần 4) — **chạy code**, không chỉ đọc report

Lượt này khác hẳn 3 lượt trước: chép **code của nhánh dữ liệu** vào rồi chạy trên raw đã kéo.

| việc | trước | nay |
|---|---|---|
| Save contract | đọc report 57, 2 key | **chạy** `tools/verify/opening_persistence.py` ⇒ **41 method · 25 check · 8 key family** (claim **OP1**) |
| Test của nhánh dữ liệu | không có | **16 test OK** trong repo này (claim **TS1**) — gồm side effect `StageTarget +1`, `TUTORIAL=6`, 2 store |
| Geometry | report 62: 2.185 sprite | **GE1/GE2/GE3**: 2.185/654/66 · `unresolved` **rỗng** · 144 lật-xoay · 40 `textureRect` vượt page ≤0,9963 px · **1.795** sprite có `source_rect ≠ texture_rect` ⇒ crop theo **`texture_rect`** |
| Sổ kiểm claim | người viết tự khai | **RB1 tự đồng bộ**: `tools/raw-audit.py` ghi lại 4 số vào doc **và** vào verifier ⇒ **151 RAW · 4 DOC · 37 CONST / 192** |
| README 39 dòng | sửa tay hay quên | **RD1** đo lại từng file + `tools/refresh-readme-sizes.py` |

**Số đã sai và đã sửa lượt này** (ghi lại vì cùng loại lỗi đã lặp 4 lần):

| Số cũ | Số đúng | Vì sao |
|---|---|---|
| "11.094 spawner" | **11.089** dòng cấu hình (**23.757** spawner khi ×`copies`) | vẫn là lỗi đơn vị; nay có `WR7` khoá **cả ba** đơn vị: 22.451 `Σ len` · 45.659 quân · 11.089 dòng |
| "Wave_0163 = 622 entry" | **620** | export lại ở `6ababbd31`; 45.659 quân **không đổi** |
| "`raw/ui-audit` chưa kéo" | **đã có** 320/388 `extra-native` + 273 `il2cpp-consts` | câu cũ sai, đã sửa ở `DATA_SYNC` §19.4 |
| "crop theo `source_rect`" | **`texture_rect`** | 1.795/2.185 sprite có hai rect khác nhau |

> Vẫn **chưa** kiểm pixel: 6 chunk nguồn của geometry chưa kéo, nên `status` của file vẫn là
> `PROVISIONAL_GEOMETRY_JOINS_NOT_PIXEL_CROP_VALIDATION`. Crop thử 1 page `sactx-*` là việc tiếp theo.
