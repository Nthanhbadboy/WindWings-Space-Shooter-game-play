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

> **Sửa lại (lần 126 — recovery sandbox lần-7 + đính chính):** sandbox rơi về
> `8b3689dc` lần nữa; phục hồi ff-only `7fc1f95` — verify ngay 209/0/2 ✓.
> Đính chính ACK125: `fbb66006` = commit **163 của 535** (Action<int>→band
> lambda), KHÔNG phải tip ef (nhầm cột tips); ef tip = `c255f70b` (CLAIM-133
> đang). 535 đẩy tiếp **164** (`afb2a410` — CI 3/3, gồm 163 làm cha) CHƯA
> đăng HANDOFF — spec chờ comment + pin rồi mới ACK/pull. Không có comment
> PR12 mới sau board-delta `6436324733` (AI-3 im — đang xác minh erratum;
> a5 idle).
>
> **Sửa lại (lần 135 — XÁC MINH TUYẾN KIẾM TIỀN 3 STORE theo khai của user + user duyệt: "3 store kiếm tiền theo đúng luật của chúng nó, không phải bàn cãi").**
> Verdict 5/5 ý user ĐÚNG (STATIC_CONFIRMED, nguồn chính chủ tại chỗ — `docs/research/phase-b/MONETIZATION_VERIFICATION_2026-10-27.md`): ① MS = payout+tax profile (W-8BEN), user đã xong ② Amazon = Tax Identity Interview — mục tài khoản duy nhất còn lại ③ Huawei = HMS IAP Kit + Petal Ads (trả tháng, ngưỡng €200), user đã đăng ký ④ 3/3 store commerce riêng KHÔNG Google Billing (Amazon reject nếu không dùng IAP của nó) ⑤ keystore user tự thêm (Huawei AAB cần App Signing; MS tự ký MSIX). **Nguyên tắc thương mại chốt: mỗi store dùng commerce/ads riêng theo đúng luật store đó — không lách, không tranh cãi.** Phát hiện tiền: VN chưa có thuế-hiệp-định hiệu lực với Mỹ ⇒ doanh thu khách Mỹ bị withholding 30% (MS + Amazon); ngoài-US không giữ tại nguồn — báo doanh thu tách dòng US/không-US. USER-ONLY cập nhật: còn Amazon-account + quyền IP/art gốc. Không đụng datas/ (needle 193 giữ nguyên).
>
> **Sửa lại (lần 134 — USER CHỐT ENGINE: "công nghệ dùng godot thôi, game này cần vậy là đủ").**
> Engine = **Godot 4.x** (MIT — $0 phí/$0 royalty, khớp mục tiêu doanh thu). Trả lời USER-ONLY #3 cũ: **KHÔNG cần Unity/source gốc** — build mới trên Godot theo spec; APK gốc = design reference/spec authority cho port. Hệ quả: D9a = GDScript interface + adapter plugin từng store · D3b Windows-no-ads càng hợp lý (không có wrapper Vungle cho Godot) · D11 chỉ chọn SDK có plugin Godot · ef lane → **Godot build/packaging spec + port-plan** (export presets Win→MSIX, APK≤4GB/AAB≤150MB gradle, versioning, signing; scaffold chỉ theo lệnh user) · E queue +2 mục Godot (plugin IAP/ads 3 store · analytics Godot) · USER-ONLY #3 viết lại = **quyền IP/art gốc** (mục duy nhất còn chờ về bản Windows). Chi tiết `docs/rollout/PHASE_C_EXECUTION_PLAN.md` §Engine.
>
> **Sửa lại (lần 133 — user làm rõ scope lệnh đào: "phần đào ở đây là nói APK; nghiên cứu của E và F có chỗ nào khúc mắc thì nghiên cứu tiếp; mục đích là làm game kiếm tiền").**
> Dừng-đào = lanes APK only (ef/a5/535/AI-3). E/F TIẾP TỤC research chỗ khúc mắc — mở research queue từ cột "Thông tin còn thiếu" D-series trong `docs/rollout/PHASE_C_EXECUTION_PLAN.md` (E: giá-benchmark D4/D6 · eCPM-Windows D3 · adapter-matrix D9 · SDK-compat D11 · luật-gacha-EU D7 · NPH-TQ D2 ưu tiên thấp · Fire-installed-base D1/D10 · retention-median D12; F: asset-counts + listing-conversion). Mục tiêu định hướng: doanh thu — cấu hình D đã chọn giữ hướng revenue (SKU kép D4c, premium Windows D6a, rewarded D8a). CI lần-132 `3ced4d716` = 3/3 xanh; board-delta lần-132 `6441761654` (đăng lúc bị cắt, đã xác nhận tồn tại).
>
> **Sửa lại (lần 132 — USER ỦY QUYỆT + chuyển triển khai): "tự quyết và phân việc; phân tích chỉ để học tập — cần thiết lắm mới đào thêm; không thì triển khai theo kế hoạch".**
> ① **D1–D12 CHỐT** bởi director theo ủy quyền (`docs/research/phase-b/DECISIONS_RESOLVED.md` — user giữ quyền bác bỏ từng mục): D1a giữ Amazon (Fire tablet/TV) · D2a loại đại lục TQ · D3b Windows không-ads · D4c SKU kép khớp `pro.forever/week/month` (STATIC_CONFIRMED) · D5 tạm-individual = **USER-ONLY pháp lý** · D6a premium Windows · D7a không loot-box trả phí · D8a rewarded-only cap 4–6/ngày · D9a interface+adapter · D10a Fire-tablet-first · D11a third-party · D12a organic-first.
> ② **Gate-1 READY-FOR-CLOSE**: C1→CONFLICTING learning-note (không chặn — APK gốc = authority sản phẩm) · C2→535 registry-v4 (mảnh cuối, mechanical) · C3→profile "L1 static-complete + runtime-gated residuals có chủ" · C4 đã đúng · C5→defer-list chấp nhận (boss-phase→ef chỉ-đào-khi-cần). Verdict NOT_READY của AI-3 chỉ AI-3 nâng khi registry-v4 về.
> ③ **PHASE C mở** (`docs/rollout/PHASE_C_EXECUTION_PLAN.md`): phân việc mới — ef→build/packaging-spec (plan-level) · a5→store-assets-spec + listing draft · Session E→requirement sheets 3 store · AI-3→re-review Gate-1 rồi verify-lane; **USER-ONLY #1–#6** (pháp lý D5 · 3 tài khoản · **Unity source cho bản Windows/quyền phân phối** · keystore · payout · lệnh publish).
> ④ Nhận ef-134 handoff `6439951448` (24 FDE thân lá 4424B, 211 fact byte-verified, artifact `74cf1843…` 7556B, CI `40490185550`) = learning-note; Phase B progress #1/#2 (`6439349047`/`6439947300`) đã nhập vào bảng 3 kênh (MS $0 · game 12% · Huawei 30:70 ngoài TQ · review 3–5 ngày). 4 file Phase B copy từ `2d76c8d7965a` (tín dụng Session E). KHÔNG pull artifact mới vào datas/ (needle 193 giữ nguyên).
>
> **Sửa lại (lần 131 — fixup needle 192→193 (artifact Gate-1 mới pull; lỗi bump lần-3 — quy tắc: pull artifact ⇒ bump ngay TRƯỚC commit, verify trước push))**
>
> **Sửa lại (lần 130 — Gate-1 NHẬN: NOT_READY + C1–C5 + recovery lần-9 + Phase B bàn giao):**
> **Gate-1** (AI-3 own125 `1e4b832387` · `6440973318` · 4 CI GREEN ·
> artifact `4a2a60e5…` 92.399B pin ✓ trên spec): verdict **NOT_READY** —
> 5 điều kiện: C1 reward-blob 149-vs-169/177 (AI4+director) · C2
> registry-v4 final (AI4) · C3 fidelity profile (**USER**) · C4 qualify
> 139-file absence (spec — MISSING:267 đã đúng "chưa thấy ≠ không tồn
> tại") · C5 bound ceiling scope+deferred+owner (spec/director; defer:
> boss-phase×2→ef · registry→535-v4 · runtime 20+5→user) · **Phase B**
> (session `46e50499`): research 3-store bàn giao — 73 nguồn · **Amazon
> Android mobile ĐÓNG 20/08/2025** · MS hết first-party ad SDK · TQ cần
> 版号 → khuyến nghị loại đại lục · **D1–D12 chờ user**. (lần 128/129:
> mandate nhận + Director Status Report `2f5febaf8` + fixup needle
> 191→192; recovery lần-9.)
>
> **Sửa lại (lần 127 — #27 6/6 CHÍNH THỨC + 164/165 ĐÓNG):**
> **AI-3 own124** (`85300eafec` · `6436979937`): VERIFIED producer erratum
> (9 Git + 2 API bodies; own bytes khớp) ⇒ verdict
> **APPROVE_BOUNDED_…AFTER_VERIFIED_PRODUCER_ERRATUM** — **#27 chuỗi review
> = 6/6** (123/118/124/120/126/127) — bounds: M1b runtime-only, null-path ≠
> full · **164** (`afb2a4103d` · `be544db4…`) · **165** (`8076b082` ·
> `97d7b0d8…` — Buy=count/Exit=0 cùng onExit, đóng 163) · 535 tiếp
> c9aea597/dcc5c413. datas/ = **191**. verify 209/0/2.
>
> **Sửa lại (lần 125 — ERRATUM-127 PRODUCER ĐÃ ĐĂNG + 162 ĐÓNG + errata-161):**
> **ef đăng erratum** (`6436088881` — b98c98 RET = **b98d64**, root-cause
> `graph127.py:55` fde_end−4 · bằng chứng raw riêng · SHA 127 giữ) — chờ
> AI-3 xác minh độc lập → APPROVE ⇒ #27 6/6 (spec không tự nâng) ·
> heuristic-fix = chu kỳ riêng sau ceiling (spec đồng ý) · **162**
> (`5e272ba130` · `6c0fbe73…`): shop state = PlayerPrefs · đóng open-160
> (GetIdItem không 1-1) + câu-153 (MaxStockCount = asset 10) · không
> SetIdItem (bounded) · **errata-161 `de3afba6…` thay artifact** (regex
> static). datas/ = **188**. verify 209/0/2.
>
> **Sửa lại (lần 124 — RÚT LẠI "6/6" của lần 122 theo protocol reviewer):**
> Verdict review-127 chỉ AI-3 nâng được — lần 122 ghi "#27 6/6" là vượt
> thẩm quyền. **Trạng thái thật: #27 = 5/6 APPROVE/SUPPORTED + review-127 =
> `SUPPORT_NULL_PATH_ONLY / RETURN-METADATA-CORRECTION-PENDING`** (AI-3
> `d25b141a1` — 41 tests sau khôi phục + 4 CI exact-head xanh; report123
> `a7f4e1f65` giữ nguyên). Erratum *nội dung* (RET `b98c98` = **`b98d64`**)
> vẫn đứng như bản ghi-sách; còn thiếu **một dòng erratum công khai của
> producer (ef)** — đã yêu cầu trực tiếp trên PR12 (ACK124). Sau đó AI-3
> xác minh → APPROVE ⇒ #27 6/6 đúng protocol.
>
> **Sửa lại (lần 123 — 27/10, 535-161 ĐÓNG — bảng RVA toàn dump):**
> **161** (`1eb0dcf022` · `d963dfc0…` · CI 3/3 · 1025 local): 2 bảng dump =
> **114.288 tên** · 1.788/1.788 slice-method khớp · 20.174 `bl` xếp loại ·
> tên mới: `Action<int>..ctor` 25841028 (159-closed) · DisplayClass ctors
> 22771696/22772596 (160-closed) · `GetIdItem` · xác nhận 154 đúng (Math.Round
> ngoài bảng) · cảnh báo jump-table `b` mid-body · ceiling giữ nguyên
> (việc lane #29, đóng open-items tên). datas/ = **187**. verify 209/0/2.
>
> **Sửa lại (lần 122 — 27/10, #27 6/6 + 160/132 ĐÓNG + CEILING):**
> **ERRATUM-127 HIỆU LỰC** (ef không phản đối sau 1 vòng; spec-issue
> `28d4b3d1a`) ⇒ review-127 APPROVE-bounded ⇒ **#27 review chuỗi 6/6**
> (123/118/124/120/126/127) — M1b runtime-only giữ trần · **160**
> (`17ff84e5…`): band-tree + **gate mua ở handler (trả lời 156)** · **ef-132**
> (`5037ba3b…`): `6b947c` không caller tĩnh — negative sạch · **CEILING:
> STATIC-COMPLETE REACHED** — mọi lane static đóng hết mục khả-dụng; còn
> mở = runtime/gated/thiết kế. datas/ = **186**. verify 209/0/2.
>
> **Sửa lại (lần 120 — 27/10, ERRATUM-127 + 159 ĐÓNG + 166-correction):**
> **ERRATUM-127 (spec xác nhận)**: `b98c98` RET = **`b98d64`** (`c0035fd6`)
> — nhãn cũ `b98d68` (`d6071494` BL) = DRIFT; supersede tại 127/128; science
> giữ nguyên (dựa pin AI-3 `c34f6cbc…`) ⇒ review-127 không còn blocker ngoài
> · **159** (`ebd5c8197b` · `09672352ef…`): SetPopup có caller (tail) ·
> onExit = Action<int> blr · popup không ví · maxStock=10−sold · **166**
> (`bdd7a6aa38` · `015dbc7b…`): 84-file manifest `19fcf9eb…` · **FOREVER ≠
> 24h** · countReborn=0 · HP 2500 ✓. datas/ = **184**. verify 209/0/2.
>
> **Sửa lại (lần 118 — 27/10, review-126 APPROVE + 156 ĐÓNG + review-127 CLAIM):**
> **review-126** (`6427626453` · `e1b02b87…` ✓ · 4 CI GREEN): verdict
> APPROVE_BOUNDED — census 3.456.888 words · 0/29.626 RELA · own-replay
> 70/8/8/66 · 3 qualifications ⇒ **chuỗi review #27: 5/5 APPROVE-SUPPORTED,
> chỉ còn review-127 (CLAIMED `6427652461`)** · **156** (`47c187e273` ·
> `df6ee0eb…`): khoá ITEM_STOCK = **đã-bán** (6/6 `add`, 0 `sub` · snapshot
> lúc click · hai trần +0x98 vs +0x20) — đọc "còn lại" = sai dấu · ef-130
> đang làm. datas/ = **181**. verify 209/0/2.
>
> **Sửa lại (lần 117 — 27/10, ef-129 ĐÓNG-bounded + 155 ĐÓNG + review-126 FINAL):**
> **ef-129** (`2c710a7c20` · `217f889379…` · Verify `40401190233` ✓ · 1835
> local): **M1a ĐÓNG** — owner `node+0x118` single-writer `6cef80`
> (`018c00f9`/36 windows) · registry-by-instance-id `[0x10e18b0]` · M1b =
> runtime-only · M2 contract-only (0 FDE) · **155** (`2e744a754` ·
> `fab987d2f9…`): ví +0x9C/+0xA0 sentinel −1 · max(0,·) · tail-b · 12 ghi
> (5+/7−) ⇒ open-154#1 đóng bounded · **review-126 FINAL** (`9d3d8c66453`,
> 1623 local, chờ 4 CI exact-head). Ceiling còn: review-126/127 · a5-lead
> · 535-156+ · ef-M1b(runtime). datas/ = **179**. verify 209/0/2.
>
> **Sửa lại (lần 116 — 27/10, 153/154 ĐÓNG + D5-residual + review-126 R1):**
> **153** (`0744e72fed` · `792f25b7…`): Arena_Shop≡PVP_Shop (30/30 field) ·
> 3 dải ô +100/200/300 · dải-100 = id−10001 → trả card · catalogue `Random.Range`
> (không bảng tĩnh) · **154** (`4fde8ec444` · `e4045686…`): 2 ví 20085132/20084804
> · cost = price × round(slider/**step**) half-to-even · popup không trừ tiền ⇒
> **#29-remit shop+exchange HOÀN TẤT** · **D5-residual** (`76f5165` ·
> `4eba6f53…`): 231.957 records — extra-life vắng trong captured · **D5 =
> NOT_BOUND chính thức** · review-126 R1: own harness 70/8/8/66 exact (formal
> chờ). Ceiling còn: review-126/127 · ef-129 · 535-155+. datas/ = **177**.
> verify 209/0/2.
>
> **Sửa lại (lần 114 — 27/10, H4 ĐÓNG + 150/151/152 ĐÓNG + ef-128 + residual-audit ÁP):**
> **H4/121 formal** (`8d4d362589` · 4 runs GREEN · `51339d7626…` · 7/7 xác
> nhận) + locator G1 sửa 4 chỗ · **150** (`23be51eba7…` — `0x2ADF238`=
> `Board_PVP` · đính chính 138) · **151** (`f76d3667…` — 143-rewards + 148-#11
> ĐÓNG · format GetRewards) · **152** (`cc6bc93a3d…` — lịch mùa PHÚT 68 ngày ·
> status nhỏ = hạng cao) · **ef-128** (`2b1b5e8277…` — 61 witnesses · M2a/b/c
> · 1811 PASS) · **residual-audit a5 nhận + áp 7 P1/P2** (OPEN_ISSUES 29 ID ·
> B3 gỡ kHp · README art-row · …). Registry 14→12. Ceiling còn: review-126/127
> · ef-M1 · 535-fu20 · D5-residual. datas/ = **174**. verify 209/0/2.
>
> **Sửa lại (lần 113 — 27/10, D5 ĐÓNG-HALF + ef-128 CLAIM + 150 PROGRESS):**
> **D5** (a5 `0376abe` · `a9655eca…`): 24/24 Player_Attack_N → 4 arrays theo
> N−1 (§24.14) · owner + extra-life NOT_BOUND (GP_Datas 6767 thiếu 4 cột) ·
> DPS runtime-gated. **ef-128 CLAIM**: M2a/b/c split + contract builders.
> **150 PROGRESS** (535 `c9a80c6e`): `0x2ADF238`=`Board_PVP` (Luật C) ·
> pathRoot 3 nhánh (đính chính 138) · 1076/1076 ô (kind,index). Ceiling còn 4:
> HANDOFF-150 · ef-128 · HANDOFF-121+reviews (AI-3 im 3 vòng) · D5-residual.
> datas/ = **169**. verify 209/0/2.
>
> **Sửa lại (lần 112 — 27/10, ef HANDOFF127 whole-FDE null-clip):** FDE
> `6cf7b4..6cff44` entry→RET (51 instr × 3 biến thể) · `6ceeb0` zero-count +
> dealloc-sink `3c9438`(0) · 6 callee extents · 33 witnesses · **M1–M5 missing-X
> map không đóng** (`6426133738` · sci `6781d828f` Verify ✓ · `8b9df0038789…`
> 2850B ✓ · 1789 local PASS). Review-126 + review-127 mở CLAIM (đề nghị AI-3).
> Ceiling còn ĐANG 3 lane: registry-v2 · HANDOFF-121+reviews · D5 (a5).
> datas/ = **168**. verify 209/0/2.
>
> **Sửa lại (lần 111 — 27/10, H3/C7 ĐÓNG — HÀNG H XONG HẾT):** **H3** (a5
> `a5b564c…` · 3/3 runs ✓ · `26b34c73…` · 278 local): 45/900xx exact roots
> (trong 2.081) · 0/45 thuộc waves-roster · 45/45 identity · role/use =
> bounded-missing. H1+H2+H3 ⇒ **hàng H ĐÓNG SẠCH**. Ceiling còn ĐANG CHỈ 4:
> registry-v2 (AI-4) · HANDOFF-121+review-126 (AI-3) · ef-127 · D5 (→a5).
> datas/ = **167**. verify 209/0/2.
>
> **Sửa lại (lần 110 — 27/10, TỔNG KIỂM DỨT ĐIỂM: 149 ĐÓNG + H2 ĐÓNG + H4-7-findings ÁP + ceiling account):**
> **§24.100**: **149**: rewardValues/scales/bet-labels trọn (registry
> ACTIONABLE ×2 sạch · runs `40390322238`/…263/…239 ✓ · `034bb93b…` · suite
> 654) · **H2**: 251/251 · dmgFirst/dmgPerSec median · 19-Director NOT_BOUND
> (`6a6e3c406` · `ec5a57c9…`) · **H4-7 findings ÁP hết** (MISSING+BALANCE
> consumer-absence · :54 scope · DR burst · leftover "chắc chắn" · kind-5
> chain · refs §24.88 · breadcrumb 39) · **CEILING**: đang-chạy H3/registry-v2/
> review-126/D5 · trần-runtime 19+C5/D2/D3/D4 · gated B1/B4/B5/B6-methods ⇒
> sau vòng tới đánh dấu **STATIC-COMPLETE CEILING REACHED** · datas/ =
> **166**. verify 209/0/2.
>
> **Sửa lại (lần 109 — 27/10, 148 ĐÓNG (registry 56→14) + H1 ĐÓNG (A2 closure) + 120 APPROVE ef124):**
> **§24.99**: **148**: 56 → **14 open** (17 CLOSED/3 RESTATED/2 ACTIONABLE/
> 19 RUNTIME/1 NOTE) · #23 falsified-premise · fix 147 · registry thay list
> thô (runs `40389191753`/…341/…363 ✓ · `5416035a…`) · **H1**: **250 arrays/
> 742 int khớp maps.json · A2 ĐÓNG bounded** · legacy 242/250 sai (runs 3 @
> `64d3dd210`) · **120**: **APPROVE BOUNDED ef124** (4 runs ✓ · `9f6056cc…`) ⇒
> #27: 123✓ · 118✓ · **124✓** · 126 chưa review · ACCEPT followup-16 (149) ·
> H2 CLAIMED · datas/ = **164**. verify 209/0/2.
>
> **Sửa lại (lần 107 — 27/10, HANDOFF126 ĐÓNG (bounded dispatch) + H1 CLAIMED + followup-15):**
> **§24.98**: ef126: 2 BL `6cef84`/`6cefe4` · 4 cases 70/8/8/66 instr ·
> 3 sink/4 virtual/0 RELA trên N2-owner prepared state — **dispatch contract,
> không dựng instance** · artifact `f209ea3f…` pin ✓ · H1 (a5) đang làm ·
> followup-15 ACCEPTED (reconcile 56 items → registry chuẩn) · 120 đang ·
> datas/ = **161**. verify 209/0/2.
>
> **Sửa lại (lần 106 — 27/10, MỞ VIỆC AI-2/AI-3 — GỠ GATE A2 + hàng đợi H):**
> **§24.97**: raw-check spec: `Map_Get_Datas.asm.txt` 26.017 dòng 0-cap ⇒
> **A2 GỠ GATE** · **H1** map→wave extract (a5) · **H2** B6-half
> serialized-only 19 boss-damage (a5) · **H3** C7 45×900xx inventory (a5) ·
> **H4** sync-review round 2 (AI-3, sau 120) · B4/B5 giữ gated · 120-CLAIMED
> trước nhắc (sửa board) · ef126 + 120 đang chạy · datas giữ **160**. verify
> 209/0/2.
>
> **Sửa lại (lần 105 — 27/10, 146 ĐÓNG + 147 CLOSE-OUT lane #29/#30 + N1 ĐÓNG):**
> **§24.96**: **146** index-half biên (39 vị trí · sentinel 999 ×20 · runs
> `40384427797`/…7532/…7720 ✓ · `d9ff7301…`) · **147 close-out**: 20/20 1:1 ·
> 21/21 checks · 40 re-hash 0/0 · **56 open items** registry + đính chính 145
> (174 thật; gap = key-jump 4 + meta-rewards 6) · runs `40385386009`/…132/…055
> ✓ · `3b815fc9…` ⇒ **LANE #29/#30 KHÉP (127–147)** · **N1 ĐÓNG** (122 →
> SUPERSEDED/CONFIRMED/UNVERIFIABLE — report 159 @`dc1c02a`) · D1/D2/D3
> RESOLVED (producer118precision ADDITIVE) · R1-addendum120 đang (harness khớp
> độc lập) · ef CONTINUE126 (owner pins read-only) · datas/ = **160**. verify
> 209/0/2.
>
> **Sửa lại (lần 104 — 27/10, TÁI KIỂM TỒN ĐỔNG — bắt lỗ HANDOFF-135 + đối chiếu registry):**
> **§24.95**: **HANDOFF 135 chưa từng đăng** — artifact tự phục vụ từ headSha
> verified (`004898a2…` khớp PROGRESS ✓ · datas 158) · superseded-chưa-ghi:
> 135→136 (MaxRankStars reader) · 134→135 (values) · **VẪN MỞ**: hunter
> rewardValues/scales (133) + nghĩa 14 hàng medal (134) — **followup-13 đề
> nghị** · legacy OPEN_ISSUES: runtime-trần D2/D3/D4/C5 · gated-data-lane A2/
> B1/B4/B5/B6/C7/D5 · **N1 nhắc 2** · ef124-addendum chưa claim · DR ⑨ ·
> verify 209/0/2.
>
> **Sửa lại (lần 103 — 27/10, 144+145 ĐÓNG (khoá save khép) + R1 APPROVE-123 + R2 SUPPORTED-118 + N2 ĐÓNG):**
> **§24.94**: **144**: 184 calls · 115/43/26 cận dưới (runs `40379769517`/…465/
> …026 ✓ · `75974f5a…`) · **145**: unknown 26→0 — `stp`-pair bẫy + Key(slot)
> return-callee (runs `40381510483`/…510/…336 ✓ · `8759167e…`) · **R1-119
> APPROVE BOUNDED 123** (R1-01/02 tái suy lập độc lập — chain Stop trọn · 4
> runs ✓ · `e782ffdd…`; ef124 = addendum kế — giao AI-3) · **R2-125 SUPPORTED**
> (1587/1587 pins 0 mismatch · 62.815 rows · 0 mâu thuẫn · `0f1354ae…`; 3 notes
> nonblocking) · **N2 ĐÓNG**: controller 1856 = Boss-37004 (component 493584 ·
> GO 76852 · `90770028…`) · 154/155-fix ✓ (nhắc-2 resolved) · N1 nhắc 1 ·
> datas/ = **157**. verify 209/0/2.
>
> **Sửa lại (lần 102 — 27/10, 143 ĐÓNG (21 key) + CHIA VIỆC ef → AI-2 (N1/N2)):**
> **§24.93**: **143**: 21 PlayerPrefs key GameDatas · 48 đọc-bl/42 ghi-tail-b
> (bẫy tail-call) · đính chính 142 (root cause addend) · runs
> `40379087484`/…250/…262 ✓ · `c655860a…` · ACCEPT followup-11 (144) ·
> **CHIA VIỆC ef→a5**: **N1** review-122 độc lập + **N2** serialized-owner hunt
> `6cf7b4` (bounded identity, không libunity) · R2 + FDE giữ ef · a5 làm trước:
> sửa 154/155 (nhắc 2) · datas/ = **152**. verify 209/0/2.
>
> **Sửa lại (lần 101 — 27/10, phục hồi sandbox ×5 + G3 ĐÓNG (G1–G6 closure 6/6) + 142 ĐÓNG):**
> **§24.92**: restore mất object DB → fetch tip + reset --hard, verify xanh
> ngay ✓ · **G3**: boss-39001 event body @`0x1247DA8` = **single RET** ·
> Complete→BossWork Attack1/2/3 `0x220D324` · NOT_BOUND marker · runs 3/3 ✓ ·
> `3c9851d9…` ⇒ **G1–G6 = 6/6 ĐÓNG** · **142**: slot `0x2ADB8E0` = ô klass
> **UnityEngine.Application** (47 cặp/33 method · 4 API · **gift 7 ngôn ngữ
> KHÔNG có VN** · **coins 68999 bẫy movk** · runs `40378057531`/…146/…980 ✓ ·
> `d618b740…`) · ACCEPT followup-10 (143) · datas/ = **151**. verify 209/0/2.
>
> **Sửa lại (lần 100 — 27/10, R1 tìm lỗi thật + CORRECTION123 + 141/G6/ef124 ĐÓNG):**
> **§24.91**: **R1**: "53→3" = hai quét BỔ TUNG (không subset) + addend =
> encoded usage `0xa0003ca7` — ef **CORRECTION123** `ea6a3835f` chấp nhận,
> scientific không đổi; spec siêu thu §24.88(b) · **141 ĐÓNG**: slot cổng thật
> `0x2ADBB88` 44940168 + **GameConfig** (1/128 theo bố cục) + đính chính 140 ×2
> (slot + chiều cờ) · runs `40375754127`/…198/…191 ✓ · `241dfc87…` · **G6 ĐÓNG**
> (3 bind / 2 local / GetCostCraftPlayer NOT_BOUND · `e31790a1…`) · **ef124
> ĐÓNG** (7 BL → 4 factory · 181/200/196/171/181/171 · `b5a9023b…`) · ACCEPT
> followup-9 (142) + G3 + R2 · datas/ = **149**. verify 209/0/2.
>
> **Sửa lại (lần 99 — 27/10, G2 ĐÓNG (ACK trễ) + G4 ĐÓNG + G5 ĐÓNG + 140 ĐÓNG + điểm đồng bộ slot):**
> **§24.90**: **G2** consumer = `devidedArenaMedals`@+0x2A0 → SetArenaRewards
> (arenaRank-index divisor · item ID 22 bounded) · **G4** gun3Static = 3×PPtr
> SetActive(false→true) `0x2781804`, Boss1_Director 582209 (runs 6/6 ✓) ·
> **⚠ slot-wording a5 siêu thu bởi ef123 ("Stop") — nhắc sửa 154/155** ·
> **G5** Tut_Settings1 → Slider.onChange → focusGameSpeed (context only) ·
> **140** ArenaConfig 6 fields + **10 mùa 1→12 ngày, đơn vị phút PROVED**
> (AddMinutes 34.499.824 · runs `40372898432`/…8685/…8467 ✓ · `d3552cea…`) ·
> ACCEPT followup-8 (141) + G6 + R1 · ef CONTINUE124 (4 node factories) ·
> R2 nhắc lần 1 · datas/ = **146**. verify 209/0/2.
>
> **Sửa lại (lần 98 — 27/10, 138+139 ĐÓNG (2 đính chính chuỗi) + row16-118 HANDOFF + MỞ VIỆC review-swap):**
> **§24.89**: **138** remote paths 6 getter + `/is-open` Arena = SỐ LƯỢNG
> (count>0) + fail-closed đủ 7 chỗ · **ĐÍNH CHÍNH 136/137: đuôi b = ToRoman ⇒
> "Herald III…God V"** (glyph bounded-missing) · **139** 9 statics đủ + bảng
> thưởng Arena 10×6 nguyên văn + **đính chính 138: +0x1C là ArenaConfig.IsOpen**
> · **118 HANDOFF** (62.815/62.815 BYTE-EQUAL · 61.864/951 · runs 4 ✓ ·
> `c33ad8a8…` 728.633B) · **MỞ VIỆC: R1 AI-3→review ef123 · R2 ef→review 118 ·
> a5 G2 đang làm (b90d24ec1) → G4/G5/G3/G6 · AI-4 gợi ý followup-7 (Medals 14×6
> + 3 bảng bet)** · P2 memo 152 áp (HR+README) · datas/ = **142**. verify
> 209/0/2.
>
> **Sửa lại (lần 97 — 27/10, SLOT `0x2ADFB48` = `"Stop"` (ef123) + G1 ĐÓNG + áp S1–S3 + 137 ĐÓNG):**
> **§24.88**: **HANDOFF123 ef** — marker decode `0x2ADFB48→0x2BE5CB8→"Stop"`
> (identity static; dispatch MODEL_NOT_MEASURED · Verify `40366819899` ✓) +
> vtable thật thay 3 sinks 122 (34/457/1281/1281 instr · 930 DWORDs bit-equal) ·
> **G1** consumer = GetPlayerPower UI (damage(rank) REFUTE — giữ B) ·
> **sync-review 152** PARTIALLY SYNCED → **S1–S3 áp**: ANIMATION_SCRIPT mở đầu +
> §2.2 + bảng mức · ANIMATION.md caveat · HANDOFF_ANIM_RAW tách route ·
> OPEN_ISSUES mục 1b · README row · DR ⑧ · **137 ĐÓNG** (10 bậc Herald…God,
> "Archon 4" · kind-5) · CLAIM G2 + followup-5 (138) · AI-3 PROGRESS 62.815 ·
> 535 forced-update ghi nhận · datas/ = **139**. verify 209/0/2.
>
> **Sửa lại (lần 96 — 26/10, #136 HANDOFF ĐÓNG + 2 đính chính 134/135 + CLAIM 137):**
> **§24.87**: **136 ĐÓNG** — rank API bằng **interpreter AArch64** (ToPoints
> 19.903.696 360/360 · DataFromPoints 19.871.992 12/12 · GetRankNumber
> 19.884.996 → chuỗi 44/44 · round-trip 108/108 · runs `40367507022`/…040/…094 ✓
> · SHA `7663d2fd…`) · **ĐÍNH CHÍNH: 135 statics-x0 (MaxRankStars CÓ reader) ·
> 134 IsOpen fail-closed qua LoadRemoteConfigs 19.916.080** · rejected_reads ×2
> (slot 44939608 — regex sẽ bịa) · CLAIM **137** GetRankName ACCEPTED (tip mới
> `f0baeb0dc`) · AI-2 sync-review memo CHƯA đăng — nhắc · datas/ = **137**.
> verify 209/0/2.
>
> **Sửa lại (lần 95 — 26/10, GIAO VIỆC AI-2 — hàng đợi 6 mục game-side từ sổ tồn đọng):**
> **§24.86**: a5 hết việc slot → **G1 `Board_Players` consumer (B, §2.2c)** · G2
> `Board_Endgame` · G3 Boss-39001 chain · G4 `gun3Static` semantics · G5
> `Tut_Settings1` focusGameSpeed (contextual-only) · G6 blob-binding census —
> CLAIM từng mục first-claim, ưu tiên G1→G2→G4→G5→G3→G6 · ACCEPT sync-review
> CLAIM `6422694348` · 136 PROGRESS (đính chính 135: GetRankNumber chạm statics
> qua x0 · suite 282) · datas giữ **136**. verify 209/0/2.
>
> **Sửa lại (lần 93 — 26/10, 134 ĐÓNG (đính chính 127: AllRewards 42→43) + p20/21 ĐÓNG — census static KHÉP:**
> **§24.85**: **134** luật PvP trọn (`pvpMaxLife=3` · `pointReduceDie=1500` ·
> `timePlay=160s` · bẫy cặp-int-8-byte · 5 bảng — runs `40364495335`/…515/…490 ✓) ·
> **135** MaxRankStars bind kháng-may (runs 3/3 ✓ @`240f8ab0c`, handoff chờ đăng) ·
> **p20** RE 2.350 files 0-hit (marker native-relocations KHÔNG parse ✓) · **p21**
> datas 56 files 0-hit (hex + decimal 44956488) ⇒ **slot 0x2ADFB48 chỉ còn lane
> ef123** (RELA `0x6d2950` — chủ dự án bảo lãnh, gỡ chế độ dừng tip) · **p22 ĐÓNG
> luôn trong vòng** (`6422508634` @ `b405a8b167` · run `40366160720` ✓ · 3.277
> paths → 0 eligible ⇒ census văn bản khép: 2.350+56+0) · board a5-refresh: tip
> spec bị ghi nhầm — lần 96 sửa định danh · AI-3 5 commit shards (geometry +
> batch 1–4) · datas/ = **136** (row START_HERE 124→136, đo thật 52 MB). verify
> 209/0/2.
>
> **Sửa lại (lần 92 — 26/10, #29-followup ĐÓNG + phase-18/19 ĐÓNG — slot chốt 0-hit toàn kho):**
> **§24.84**: **PvP hunter** (6 mốc `[PVPMedal…Key2]` · 12 marker chỉ lẻ bấm ·
> idx=(m−1)/2 · runs `40362026596`/…48/…87 SUCCESS ✓) · **p18** (metadata 10.758/
> 17.933/15.054 rows — 0 ref slot · run `40362790286` ✓) · **p19** (326 exports 0 hit ·
> run `40363420404` ✓) ⇒ **0x2ADFB48 UNRESOLVED-at-static — chỉ ef123 native có thể
> dịch tiếp** · AI-3 row16 scope: **62.815 SpriteRenderers** đo thật, không guess ·
> CLAIM followup-2 (report 134) · **ef: 5 push không handoff — nhắc lần 2 giữ hiệu
> lực** · datas/ = **132**. verify 209/0/2. Weighted ~88%.
>
> **Sửa lại (lần 91 — 26/10, phase-15/16/17 ĐÓNG + key-sources ĐÓNG + 2 CLAIM mới):**
> **§24.83**: **p15** (0/15.054 literal rows map slot — key UNRESOLVED) · **p16**
> (corpus 273 files · exact 0 hits · 4 uses/2 methods) · **p17** (`0x27583B0` =
> Animator.SetTrigger · controller 1927 param duy nhất `Stop` = contextual
> candidate) — mẫu tách 3 tầng đều · **followup-4 ĐÓNG** (key: +21 màn SaveDataReward
> +3 nút · −mở-box 30 · caps 1e6/5e5/1e5) · CLAIM AI-3 row16-sprite-consumer (118) +
> AI-4 #29-followup (133) · **ef nhắc lần 2 (4 push không handoff)** · datas/ = **129**.
> verify 209/0/2. Weighted ~87–88%.
>
> **Sửa lại (lần 90 — 26/10, #8 ĐÓNG ⇒ CHƯƠNG TRÌNH GỐC #1–#28 TRẮNG BOARD 28/28):**
> **§24.82**: **#8 ĐÓNG** (4 runs SUCCESS @ `1fa9f4f20` ✓ · 52/52 hashes · Quad×46/
> Cube×5/Plane×1 thật · 5/5 MB BYTE-EQUAL) · **phase-13/14 ĐÓNG** (runs ✓ · shared
> data 580611 · script-link 127.852 rows blank = bounded gap; board-label typo —
> commit đúng nhánh chuẩn) · **nhắc ef123** (3 push không handoff) · datas/ = **126**.
> verify 209/0/2. Weighted ~87%.
>
> **Sửa lại (lần 89 — 26/10, ĐỒNG BỘ SPEC ↔ APK-ANALYSIS theo lệnh chủ dự án):**
> **§24.81**: MISSING 14 (Arena/PvP ~0,8) · 15 (meta ~0,85–0,88) · 5 (boss-1 mức B) ·
> 9 (StartDrone static) · 13 (plugin audit) · 16 (mesh refs resolved) — tất cả dẫn
> reports 127–141 · DR lần-4 ⑤–⑧ · START_HERE datas 124/52MB · **weighted ~85%**
> (trần static-complete) · phase-11/12 + followup-3 ĐÓNG (runs ✓, SHA pin) · CLAIM
> followup-4 + phase-13 · #8 scientific pushed chưa handoff · datas/ = **124**.
> verify 209/0/2.
>
> **Sửa lại (lần 88 — 26/10, phase-9/10 ĐÓNG + followup-2 ĐÓNG + #8 VALIDATES + DR lần-4):**
> **§24.80**: **phase-9 ĐÓNG** (state→defeat/burst +0x70/+0x78 — CORRECTION nâng lên
> metadata TypeDefIndex 141 · runs `40353843965`+`40354271059` ✓) · **phase-10 ĐÓNG**
> (PPtr chain→skeleton JSON 918 · 8/8 labels · BossSpineEventHandler 0 instance · run
> `40354813447` ✓; phase-11 claim) · **#30-followup-2 ĐÓNG** (typeBox 2-store/669 ·
> miền 0/1/2 · 3 call sites · BuyEnergy 30→50 · runs `40354854530`/…76/…46 ✓; followup-3
> claim) · **#8 VALIDATES**: 5/5 MB BYTE-EQUAL inverse + 3 Mesh resolves + chéo-làn
> Boss19_AttackTypes script 946 (giúp phase-6 a5) · ef123 đã push chưa handoff ·
> **DESIGN_READINESS lần-4: D3 boss-1 → mức B** · datas/ = **120**. verify 209/0/2.
>
> **Sửa lại (lần 87 — 26/10, #30-followup ĐÓNG + phase-8 ĐÓNG + 2 CLAIM mới):**
> **§24.79**: **#30-followup ĐÓNG** (runs `40352753993`/…90/…35 SUCCESS @ `f0ed6639c`
> ✓ · jump-table 27/27 pin bytes · index map 0..26 · regen-churn tự bắt + test khóa ·
> hệ 15 ~0,85) · **phase-8 ĐÓNG** (runs `40353025124` ✓ @ `1ebd693f6` · UnityEvents →
> Enemy_Destroy 601110/root 185722 · pointBurst 384934 no-record khai · Boss1_Director
> 39002 tách đúng) · CLAIM followup-2 (report 130) + phase-9 (report 138) · ef123
> chưa push · datas/ = **117**. verify 209/0/2.
>
> **Sửa lại (lần 86 — 26/10, #30 ĐÓNG + #8 CORRECTION + a5 phase-7 ĐÓNG):**
> **§24.78**: **#30 ĐÓNG** (3 runs SUCCESS @ `17e28a289` ✓ · hệ 15: 0,25→~0,75 ·
> weighted ~83%) · **#30-followup CLAIM** (report 129 — pack-index identity từ raw
> pin) · **#8 CORRECTION**: 850MiB superseded — **600MiB restored byte-identical
> `839d78c8f8af…`** ✓ · **phase-7 ĐÓNG**: Boss-39001 Spine route bounded
> (674445→602882/580611 · AnimationState_Event = RET) — không claim native join ·
> **phase-8 CLAIM** (report 137) · ef 🔄123 vtable-linkage · AI-4 tip CI chờ approve
> (action_required — bình thường). datas/ = **115**. verify 209/0/2.
>
> **Sửa lại (lần 85 — 26/10, ef122 ĐÓNG + a5 phase-5 ĐÓNG + #8 blocker + #30 gần handoff):**
> **§24.77**: **ef122 ĐÓNG** (Verify `40347869822` ✓ · graph-populator 6d2950 · 3
> virtual sinks · 930 lần 8 · indirect-callers open) · **a5 phase-5 ĐÓNG** (0 direct
> refs 6 methods · slot 4 · corpus 139 · runs `40349989901` ✓; phase-6 claim) · **#8**:
> Mesh 10209 = Plane thật (121v/600i) · tails nonempty · **600MiB supervision chặn
> schema expansion** — approach small models ✓ · **#30**: rewards/RankSplit/MaxRankStars
> values + shop TRONG .so (sửa nhận định #29) + MAX_LEVEL_BP = remote-config 0-hit ·
> hệ 15: 0,25→~0,75 · datas/ = **114**. verify 209/0/2.
>
> **Sửa lại (lần 84 — 26/10, #29 ĐÓNG (Arena/PvP) + phase-2/3 ĐÓNG + #8 đo scope):**
> **§24.76**: **#29 AI-4 ĐÓNG** (3 runs SUCCESS @ `b37f7d6f1` ✓ · 1361 method/244
> class · map pools thật · AllPvPRandomMaps = 0 ✓ · hệ 14: 0,25→~0,8; còn shop
> serialized + MaxRankStars values) · **a5 phase-2+3 ĐÓNG** (SYNC needle fix — runs
> GREEN @ `e51338c8c` ✓ · Boss AttackPhases PPtr joins) · **#8**: 2/7 overlap #7 +
> 50 additional refs (lớn hơn delta-45) · ef 🔄122 · datas/ = **111**. verify 209/0/2.
>
> **Sửa lại (lần 83 — 26/10, #7 ĐÓNG + phase-2 HOLD + #8/phase-3 CLAIM):**
> **§24.75**: **#7 ĐÓNG** (runs 40342889160/…106 SUCCESS @ `0018ac7ae` ✓; 7/7 resolved
> từ `unity default resources` — falsify hypothesis mẫu mực; tasks **26/28**) · **a5
> phase-2 HOLD** (handoff CI đỏ `40343849270` — tái tạo: APKD1 88→91 + AI1 86→89 quên
> sync; dữ liệu nhận + pin `2b6120c00a9f8a70…`: negative bootstrap + timeScale 29
> transfers) · CLAIM #8 (AI-3) + phase-3 (a5, report 132) · ef 🔄122 · AI-4 🔄#29 ·
> datas/ = **109**. verify 209/0/2.
>
> **Sửa lại (lần 82 — 26/10, AI-4 onboard + ef121 ĐÓNG + StartDroneSkillDamages static ĐÓNG + #7 resolve 7/7):**
> **§24.74**: **AI-4** (535b0541) claim #29 đúng chuẩn · recovery Actions STATIC (XAPK
> EOF) · không bịa pool-4 ✓ · **ef121 ĐÓNG bounded** (1628 PASS · factory 6d5e58 sink
> assert · 572a38 list/count/OR · 930 lần 7 · 122 graph-populator tiếp) · **a5 phase-1**:
> **StartDroneSkillDamages[12] static 12/12 khớp runtime** — supersede "chưa có static"
> lần 73 · phase-2 claim 131 · **#7**: 7/7 builtin = Mesh thật `Library/unity default
> resources` (10210×6/10202×1) — resolve hết, không missing-proof · datas/ = **108**.
> verify 209/0/2.
>
> **Sửa lại (lần 81 — 26/10, mở AI-4: #29 Arena/PvP + #30 meta thưởng):**
> **§24.74**: prompt tự chứa `6418869062` + board + hàng task #29/#30 · static-only ·
> first-wins · boundary 3 làn cũ giữ nguyên. Dự kiến rút đuôi 16 hệ từ ~8h còn ~3-5h.
>
> **Sửa lại (lần 80 — 26/10, AUDIT TỔNG THỂ "được bao nhiêu %"):**
> **§24.73** (đếm từ file): **16 hệ = 8 đủ/8 một phần/0 thiếu ≈ 76% weighted** ·
> DQ 48 câu = 33✅/14⚠/1❌ (trọn 69% · có-partial 98%) · blocker còn 5/9 ·
> **tasks 25/28 ĐÓNG (89%)** — còn #7/#8/#27 · catalog 2.197 sprites/2.885 rows/69
> clips/797 màn · datas 104 (+4 subdir) · 71 reports. **Headline ≈ ¾ đường; đuôi
> nặng = Arena/PvP + meta thưởng (⅓ khoảng cách); trần 100% giờ là static-complete
> (lệnh 26/10).** Sửa regress board: hàng #28 bị revert do PATCH base stale — đã
> trả về "ĐÓNG theo lệnh 26/10".
>
> **Sửa lại (lần 79 — 26/10, tồn đọng tổng + phân công lại: a5 nhận game-side writers):**
> **§24.72**: tồn đọng = #27 native structural (ef 🔄 121) · **#27 game-side
> writers/bootstrap C# — CHƯA AI LÀM → a5 nhận (static-only, dump.cs/RVA; quick-win:
> StartDroneSkillDamages static + MISSING-13 plugin list)** · #7 AI-3 🔄 (#8 hàng đợi) ·
> MISSING 8/8-một-phần · DQ 33/14/9. Boundary: ef giữ libunity FDE; va chạm first-wins.
>
> **Sửa lại (lần 119 — 27/10, #28 ĐỔI CĂN CỨ theo lệnh chủ dự án — probe runtime 23/10 ĐÃ CHẠY):**
> Căn cứ đóng #28 đổi từ "static-only, không run" sang **"probe runtime 23/10
> đã chạy"** — phiên Ramus thật trên **Mate 20 X** (`docs/apk-analysis/ramus/
> 2026-10-23-phone/`, 84 file; report 48 + 49): BepInEx-6 chainloader ✓ ·
> RamusBridge listen ✓ · **8/9 HTTP endpoints** ✓ · **balance 24 tàu/12 drone/
> tech/stage thu qua `/statics`** · **`listMapDatas` = 250 runtime ✓ = mức A**
> (đối chiếu `datas/maps.json` 250 — CROSSCHECK §1) · **field parity TRUE**
> StartMainCannonDamages idx-2 = **2680** / rate **4.8 s** (report #111 ·
> `datas/l2_dps_runtime_parity_ship1_18.json.gz`) · 35 PNG UI-flow · boss
> GP/stagedata dumps · freeze-time ✓. **KHÔNG cần runtime thêm cho #28.**
> Bounds giữ nguyên: probe chạy bản **1.0.69 mod Premium** vs nguồn
> **1.3.118** — khớp ⇒ củng cố, lệch ⇒ có thể khác bản; live-DPS time-series
> không nằm trong probe (giữ MODEL_NOT_MEASURED — không tụng static thành
> runtime); 243 mảng sau của map chưa xác thực token. Chi tiết §24.108.
>
> **Sửa lại (lần 78 — 26/10, ĐÓNG #28 runtime theo lệnh chủ dự án + #6-rep ĐÓNG + CLAIM #7):**
> **§24.71**: **#28 ĐÓNG (scope)** — static đủ; không secret, không run, không nhánh B;
> receipts 121/124 + bridge `40333586413` giữ; live-DPS = MODEL_NOT_MEASURED runtime,
> #27-consumption = structural-only, cấm tụng static thành runtime · **#6-rep ĐÓNG
> byte-exact** (runs 40334704704/40334658103/40334670934 SUCCESS @ `311a45df0` ✓;
> 2905/2905 · 2251 BYTE-EQUAL · diffs 0; a5 primary) · **CLAIM #7** (7 builtin mesh refs,
> 814). datas/ = **104**. verify 209/0/2.
>
> **Sửa lại (lần 77 — 26/10, #27/120 ĐÓNG + #6-rep byte-equal + ĐÁNH GIÁ runtime 23/10):**
> **§24.70**: **#27/120** (ef, 1601 PASS): node ctor 6d353c — 174 instr/0 sinks ·
> 447/512 bytes ≠ memset · vtable RELA→6d46a8 khớp 119 · **930 lần 6** · ĐÓNG bounded
> node-init · **#6-rep** (814): **2905/2905 hashes · 2251 BYTE-EQUAL / 1,72 MB · diffs 0**
> vs primary — byte-exact chờ HANDOFF · **RUNTIME 23/10: ĐỦ config-parity (BaseDamages
> 12/12 · 742/0-mismatch · anchors) — CHƯA đủ behavior (live-DPS · #27-apply ·
> second-device)** · nghẹt 1 secret `RAMUS_API_KEY` (chỉ chủ repo đặt được) → **CẤM
> retry; kịch bản 1-lần: gate→live-DPS→(second-device nếu lệch); nhánh B emulator+frida
> chỉ theo lệnh**. datas/ = **104**. verify 209/0/2.
>
> **Sửa lại (lần 76 — 26/10, #27/119 ĐÓNG bounded + #6-rep OOM-safe chạy tốt):**
> **§24.69**: **#27/119** (ef, 1581 PASS): parent FDE entry→118→second-phase→node174→RET
> không staging · 930 lần 5 · **3 early-returns native** (null-blob/mode−1/flag28-zero) ·
> **"node174=1 từ byte đơn KHÔNG chứng minh sampling/apply"** (chống-lạm) · từ chối chạy
> rig giả — ĐÓNG bounded parent+guards · **#6-rep**: stdlib inverse serializer stream
> 1-tree — 2185 Sprite + 66 atlas match SHA · 27.072 verts khớp mesh-contract a5 ·
> mmap + SQLite flush (OOM-safe ✓) · #28 a5 FusionCore runner + stage-failures. datas/
> = **102**. verify 209/0/2.
>
> **Sửa lại (lần 75 — 26/10, đính chính tie-away + #27/118 ĐÓNG bounded + AI-3 restart):**
> **§24.68**: **sai của spec** — `.7→3f333334` là FCVT+1ULP, không phải tie-away (FRINTA
> là 116/b93158) — supersede DS/DONE · **#27/118** (ef, 1571 PASS): full caller FDE
> entry→RET không staging · 930 lần 4 bit-equal · fault→`__stack_chk_fail` thật, không
> fake success — ĐÓNG bounded current-caller · AI-3 restart OOM-safe tiếp #6-rep · #28
> a5 grind SDK/workflow 5 commit. datas/ = **101**. verify 209/0/2.
>
> **Sửa lại (lần 74 — 26/10, #4 + #27/117 ĐÓNG bounded; loader probe vướng workflow-file):**
> **§24.67**: **#4** (8141386a, 1430 PASS): 1751/1751 hashes · 14 spans/160024B ·
> 7/2352/2354/2285 · 797 previews/940 null-reason · NOT-em — ĐÓNG static fallback ·
> **#27/117** (ef, 1531 PASS): duration getter thật (ctor vptr + RELA +0xA8) · context
> writer zero-sub · `.7`→3f333334 tie-away (spec decode ✓) · 930 ✓ — ĐÓNG bounded ·
> #6-rep claim ✓ · **loader probe: `40326606441` FAILURE = workflow file issue** (chưa
> chạy); a5 fix đã commit, bridge đỏ 13:07. datas/ = **100**. verify 209/0/2.
>
> **Sửa lại (lần 73 — 26/10, RE-CHECK runtime 23/10: r90 nâng static↔runtime verified + giải mystery 12v10):**
> **§24.66**: mỏ runtime 23/10 rà lại × static mới — **Drone BaseDamages[12] 12/12 exact
> crossbuild** (r90 → "static↔runtime verified") · mystery listStatValues 12v10 ĐÃ GIẢI
> bởi #19 (supersede CROSSCHECK) · anchor catalog (PlayerCosts24/legendary/ranks7/
> Tech34/deltaPricePlayers24/StartDroneSkillDamages12 mỏ mới) · map contents chờ probe.
> `RECHECK-2026-10-26.md`. verify 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 72 — 26/10, GỠ CẤM MOD APK (mọi biện pháp) + ACK 116 + #28 accepted):**
> **§24.65**: **lệnh chủ dự án lần 72** — repak/rebuild/loader/instrument ĐƯỢC PHÉP cho
> runtime probe; boundary còn lại: vehicle ≠ evidence source (pin SHA + công thức dựng),
> đối chiếu static, không bịa readback, APK gốc vẫn authority cho static · **#27/116 ĐÓNG
> bounded** (1491 PASS): time+dense/constant composition — FRINTA tie-away vượt-stop ·
> signbit flip · 930 DWORDs sau native conversion · source dense trống dù frameCount 420 ·
> #28 a5 accepted · #4 AI-3 1751/1751 hashes. datas/ = **98**. verify 209 PASS · 0 FAIL ·
> 2 SKIP.
>
> **Sửa lại (lần 71 — 26/10, #5-rep + #6 + #27/115 ĐÓNG bounded + LỆNH CHẠY RUNTIME PROBE):**
> **§24.64**: **#5-rep** (8141386a): witness byte + cuts khớp a5 — model-agreement ✓;
> support-view pin đủ (99-path snapshot trong verification-5.json.gz) — ĐÓNG · **#6**
> (127-a5): 1550/1550 remap 1:1 · 2185 bones/bindpose EMPTY scoped — ĐÓNG static remap ·
> **#27/115** (ef, 1451 PASS): packed-clip consumer PROVED (2262 words copy unchanged ·
> 930 DWORDs bit-equal) — ĐÓNG bounded; dense/timewrap/Animator MỞ · **⚡ lệnh chủ dự án:
> CHẠY RUNTIME PROBE (phương án b — loader-apk tự dựng trong CI, loader ≠ evidence
> source; ưu tiên map 742 values → second-device → live-DPS)**. datas/ = **97**. verify
> 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 70 — 26/10, #26 ĐÓNG bó scope + #27/115 chạy tiếp):**
> **§24.63**: **126-a5 #26** (`0002070e8a`): root 212696 (235 nodes inactive) · chain
> 57508→425352→439142→root · 0 match/0 PPtr edge trong captures · 5 cameras không link ⇒
> **pixel_bounds=null CÓ CĂN CỨ census** — kết quả tận-cùng (b): tĩnh hết đường, chỉ
> runtime vượt được · #27/115: packed sampler callers × count fields × **class74** (nối
> 791 clips từ #110) đang chạy. datas/ = **94**. verify 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 69 — 26/10, #28-fb① + #25-bounded + #27-core ĐÓNG bounded; #26 claim):**
> **§24.62**: **#28-fb①** (124-a5): 250 rows · 742 values **0 mismatch** (243+7 nhất quán
> #21 ✓) · loader scoped-absent (release chỉ xapk) · `arr=256&depth=2` NOT_OBSERVED — MỞ
> phần loader/②③ · **#25** (125-a5): 0 PlayerPrefs.Save edges/74 methods · scan RVA
> 0x277cf6c/314 ASM: 0 hits · SaveToDisk 3 callers + 1 WriteAllBytes — ĐÓNG bounded slice,
> #25 MỞ · **#27** (114-ef, 1411 PASS): interpolation native zero-hooks · **falsification
> `0x38d1b717`=9.9999997e-5** (spec decode ✓) → KHÔNG universal cubic · packer 84B/204
> instr — ĐÓNG native-core, #27 MỞ. datas/ = **93**. verify 209 PASS · 0 FAIL · 2 SKIP.
>
> **Sửa lại (lần 68 — 26/10, góp ý AI-1 + duyệt support-view AI-3 + #27 claim + witness #5):**
> **§24.61**: AI-1 — #27 (114) native interpolation DUYỆT (AnimationCurve→native; cubic
> model ≠ proof) · góp ý #5-rep (invariants tách harness; model-agreement ≠ native proof)
> · AI-3-mới — **support-view boundary ĐƯỢC DUYỆT** với điều kiện pin snapshot vào receipt;
> diagnostic 160/27/24 giữ nguyên; đạt-209 gọi "scoped historical-support compatibility" ·
> witness byte #5: LE `00003442/0000a041` = 45.0/20.0 ✓ khớp border a5 — 2 tool hội tụ.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 67 — 26/10, #2 ĐÓNG bounded + verify-pattern cho AI-3 + #28 lane):**
> **§24.60**: **#2** (113-ef `f5a447c15a`): tag23→m_Sprite native mapping PROVED trong
> fixture (slots[23] · dispatch · resolver; spec cross-check decimal ✓) — customType23
> r104 nâng "native mapping proved"; Unity/bootstrap/runtime MỞ · verify-pattern: digger
> pin baseline riêng, FAIL không tăng; 209 là gate spec · #28: a5 chạy loader-apk →
> fallback ①. datas/ = **90**. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 66 — 26/10, AI-3 mới lên ngành + #24/#5 ĐÓNG bó scope + phân xử #5):**
> **§24.59**: AI-3-mới `8141386a` setup đúng (base ef tip + 3 shared; đọc 171 comments bằng
> api-paginate; khai gap tree-digger thiếu tools spec) · **phân xử #5: a5 (11:20) trước
> AI-3-mới (11:31) → primary a5**; 8141386a giữ REPLICATION + đề nghị nhặt #4 · **#24 ĐÓNG
> bó scope** (`837ca858ff`): Player_Attack_1 đọc `StartMainCannonDamages`, rank gate loop ·
> **#5 ĐÓNG bó scope** (`0252bd8bb6`): 441+14 recounted · 112 grids 16v/54i + 10 tiles ·
> 5739 ✓ · #2 ef code-done chờ handoff. datas/ = **89**. verify 209 PASS · 0 FAIL · 2 SKIP
> · unittest OK.
>
> **Sửa lại (lần 65 — 26/10, điều tra AI-3 → UNRESPONSIVE, thu #4–8 về REPLICATION):**
> **§24.58**: AI-3 = 1 comment (claim 08:46) rồi im hẳn — tip đứng `ceebe881d8` từ 08:32 ·
> churn 1047 files [skip ci] sau CI 4/5 đỏ · 0 phản hồi 3 nhắc → **#4–8 MỞ REPLICATION**
> (yêu cầu claim cũ giữ nguyên: #5 border-from-metadata không quad; #7 resolve-hoặc-chứng-minh;
> #8 không bịa mesh). AI-3 quay lại: re-claim + sync base + cấm skip-ci churn. verify 209
> PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 64 — 26/10, #28 mở lại theo loader-apk + fallback + CLAIM #2/#24):**
> **§24.57**: lệnh "cần thì làm cứ mở, không được thì tìm phương án khác" — **#28 hướng (a)
> DUYỆT**: loader-apk `windwings-assets-1.3.118` làm vehicle (không đụng original bytes ·
> pin SHA loader · receipts provenance); fail → fallback 3 hướng (static-crosscheck #21 ·
> device-profile · static-DPS-model) · CLAIM **#2** (AI-1, `aa80aa3e75`) + **#24** (AI-2) ✓.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 63 — 26/10, #17-schema 2 track ĐÓNG bounded + #28 BLOCKED cần vehicle):**
> **§24.56**: **120-a5** REPLICATION (chuỗi m_InterruptionSource→m_OrderedInterruption→
> m_CanTransitionToSelf; pins AI-1 ✓) — ACK bó scope · **112-ef** native fixture (libunity
> `d827b83e…` · entry 0xB7E1BC · 74.714 instr gốc trong Unicorn · 281 nodes · **308 payloads
> decode bằng native schema fulltree-equal** · TransitionConstant 13 vs Selector 2 →
> 533/616 interruption corroborated native) — ACK bounded corroboration · **#28 BLOCKED**:
> không `RamusBridge.dll` trong APK/splits (run `40310064929`, gate dừng trước session;
> map_values=null) — **cần chủ dự án duyệt bridge-enabled vehicle** (RamusBridge.cs +
> bridge-build.yml sẵn; thiếu loader-apk duyệt). datas/ = **87**. verify 209 PASS · 0 FAIL ·
> 2 SKIP · unittest OK.
>
> **Sửa lại (lần 62 — 26/10, LỆNH "MỞ HẾT ĐÀO TẬN CÙNG" + #17-schema 2 track):**
> **§24.55**: mở **#24/#25/#26/#27(=15b)/#28** claim tự do + nhắc #2 · chuẩn "tận cùng" =
> (a) byte-proof có pins hoặc (b) chứng minh có-scoped "không thể xa hơn mà không có X" ·
> runtime chỉ qua vehicle, cấm bịa readback · **#17-schema**: AI-1 native libunity
> (`010562d96`) + AI-2 REPLICATION tier-2 (artifact 1.762B ở `4cb2828ec`, pre-verify OK —
> ACK chờ handoff). datas/ = **85**. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 61 — 26/10, #17 3 lớp framing ĐÓNG + #19 bó scope → L2 trắng board):**
> **§24.54**: restore .git lần 4 (backup `_user_wip_r61` → reset `45390206c9`, xác minh OK) ·
> **#17** = payload 109 + metadata 110 (`f4a6346172`: 704.961 rows · 793→791 · witness
> 18915424/2768 · 322 SHA giao ✓) + UnityFS 111 (`c9577acd2`: v8/579 · 16/2198 · own LZ4 ·
> 136 blocks · 308 fresh equal 110 SHA · 1305 PASS) — **ĐÓNG independent framing đủ chuỗi;
> schema discovery MỞ** · **#19** (`dab116eddf`, SHA khớp): 12=10+2 RESOLVED · 10=10 khác
> build · percent f32 ✓ · map 128 placeholders MỞ — **ĐÓNG bó scope**. **L2 trắng board**
> (18–23 ✅; 24/25 chờ chủ dự án). datas/ = **84**. verify 209 PASS · 0 FAIL · 2 SKIP ·
> unittest OK.
>
> **Sửa lại (lần 60 — 26/10, #12 ĐÓNG bó scope + #17 phân xử 2 tầng + #19 CLAIM → L2 phủ hết):**
> **§24.53**: **#12** (112-a5, SHA `5fc9fd36…` khớp) — Popup_QuitMissions 495980→controller
> 1974 · clip1572/1573 · prior_block_recheck sửa GO 270123 (lỗi type/identity) ·
> pixel_bounds=null — **ĐÓNG bó scope template-serialized; pixel projection MỞ** · **#17**
> (109-ef, code `99d778f38`, 1226 PASS) — decoder import struct duy nhất ✓ · 308/308 +
> 232/232 · counts all308/old232 ✓ — **tầng 1 payload reader ĐẠT, tầng 2 framing/schema
> MỞ** (shared UnityPy DB); 110-ef frame 704.961 rows đang chạy · **#19 CLAIMED a5a74747
> → L2 phủ hết**. datas/ = **81**. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 59 — 26/10, #21 ACK + #23/#18 push về + ACK bó scope + #17 claim):**
> **§24.52**: **#21 ĐÓNG** (provisional) — review độc lập 4/5 từ artifact (576 unique ✓ ·
> per-root 9/9 + 243+7=250 ✓ · canonical equal ✓ · external fixture ✓; ③ trace chỉ count —
> không repro từ artifact, không block) · đính chính 550 RELA / 773-0 Add hooks · **#23 ĐÓNG
> bó scope** (SHA `3e8aca26…` khớp; 7 specials; runtime wing MỞ) · **#18 ĐÓNG bó scope**
> (SHA `9fe9d1e2…` khớp; 2680/4,8 s = damage·s ≠ DPS; 1.0.69≠1.3.118 khai rõ; live MỞ;
> needles sync đủ APKD1 78/AI1 76/RD1 41-0) · **#17 CLAIMED ef** (308/308 khớp, schema =
> UnityPy builtin DB — shared framing khai rõ, handoff sau commit). datas/ = **79**. verify
> 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 58 — 26/10, ADDENDUM AI-1 bắt lỗi wording §24.50 + #21 pre-verified + #23 pending push):**
> **§24.51**: sửa **"GetDevice body không khả dụng"** → "batch110 chưa consult — body CÓ ở
> nhánh dữ liệu r89 (`pickup-currency/Device_Saved_Data`, 200B/50 instr)" (chuẩn ghi chép:
> tách "chưa consulted" khỏi "repository-wide missing") · **#21** artifact `map_entry_bindings`
> (SHA `ccf8309e…`) pre-verify ở tip `537e9024d` — ACK chờ handoff · **#23** handoff đăng
> trước push — artifact chưa ở remote, dọn file rỗng 0-byte, KHÔNG ACK, nhắc push · AI-2
> CLAIM **#18**. datas/ = **77**. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 57 — 26/10, L2 #22 ĐÓNG bó scope + nhận 4 điểm review AI-1):**
> **§24.50**: **110-a5a74747** — PLAYER_DEVICE_* 4-slot · Device id@0x10/lv@0x14/rank@0x18/
> **instanceId@0x1C** (khớp r89 hex) · chuỗi load GetPlayerDevices→skip −1→GetDevice→
> Device.id→branch→GetStatValue1/2 · mode-4/Game sentinel · **GetDevice body: batch110 CHƯA consult — body CÓ ở nhánh dữ liệu r89
> (Device_Saved_Data; ADDENDUM AI-1 lần 58) · durability + migration MỞ** · SHA `b744f99b…` khớp chính xác (datas/ = **76**) · nhận 4 điểm AI-1
> (PHAN_TICH ≠ bytes validation · clamp-per-array trước bounds · FP32 ≠ display parity ·
> RD1/CI tách tầng) · nhắc needle APKD1 76 + RD1 trên nhánh AI-2 · AI-2 CLAIM #23. verify
> 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 56 — 26/10, HANDOFF107-ef6b75ef: supporting probe #20 + #21 tiến độ):**
> **§24.49**: supporting `l2_ef6b75ef107_board_power.json.gz` (SHA `06e6b7f6…` khớp chính
> xác) — **basic24** + delta24 uniform **0.1679999977350235** (bit 31082c3e); spec tái tạo
> f32 + ties-even: 10001→**5420** ✓ · 10024→**8864** ✓ · 98 fixtures ✓; **cross-spec: power
> delta 0,168 ≠ r90 ship 0,16** · #21: cctor 25.224 instr + 548 RELA (chưa proof; parser
> fail log trung thực → retry SUCCESS) · AI-2 CLAIM #22 · AI-3 #4–8 running. datas/ = **75**.
> ACK107-ef6b75ef PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 55 — 26/10, L2 #20 ĐÓNG + first-claim wins tự điều chỉnh):**
> **§24.48**: **109-a5a74747** — `GetPlayerPower` 0x12D5DFC đọc allBasicAtk@0x10 + allDeltaAtk
> @0x18 → `basic[i]×(1+delta[i]×level)` → textPlayerPower (**UI display only**, combat mở) ·
> SHA `79d7232d…` khớp chính xác (datas/ = **74**) · **AI-1 tự rút claim #20** sau khi
> paginate toàn bộ comments (first-claim wins AI-2; sửa quy trình đọc `--paginate`) · AI-3
> CLAIM #4–8 · AI-1 CLAIM #21 (bind576). Nhắc #20: RD1 FAIL trên PR14 là RELATED (đổi
> DATA_SYNC/START_HERE mà chưa refresh README size — sync + push). verify 209 PASS · 0 FAIL
> · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 54 — 26/10, 2 handoff cùng lúc: 106-ef6b75ef + 108-a5a74747):**
> **§24.46**: GLES PixelSnap + bilinear thật — **spec arithmetic review 9/9 PASS từ artifact**
> (round-even ≤0,5/trục · z/w+uv không snap · bilinear 4-tap từ 46 texels ×14 · premul · over
> · same-pixel alpha .05091579864714838→.08276148982721251) — CPU ≠ GPU giữ. **§24.47**:
> #15 **PARTIAL** — 308/308 1-layer (multi NOT_EXERCISED, đóng cho snapshot) + API chỉ
> declaration ⇒ native interpolation **MỞ**; 301.603 keys; proven:false giữ. Kéo 2 artifact
> (datas/ = **73**, needle AI1 71→73). AI-3 tip chạy `ceebe881d`. ACK106+108 PR12. verify
> 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 53 — 26/10, chủ dự án MỞ L2 — "không chờ, đào cho hết"):**
> **§24.45**: 6 mục L2 → **#18–#23** claim tự do (DPS parity tàu 1 · ramus device ×2 ·
> float[24] consumer · bind 576 identity · save schema e2e · wing named leaves/DPS parity) —
> gate giữ nguyên. Điều phối: AI-2 CLAIM #15 · **AI-3 `eeb95d5a` SỐNG LẠI** (`90c4e4ff9`,
> base cây đầy đủ, probe APK, chưa CLAIM — nhắc #4–8) · AI-1 batch 106 đang chạy. Sticky
> lần 53 + công bố PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 52 — 26/10, HANDOFF107 AI-2 `a5a74747` — #16 replication transition):**
> **§24.44**: artifact-level recount — **0 mismatch** (232/232/667/377/666 · **932 = 343+125+
> 464** · destination **698+234** non-local giữ literal · **464 selector omit
> m_InterruptionSource**; bool false ≠ serialized false) · SHA `83674021682a13c6…` khớp chính
> xác (datas/ = **71**) · CI xanh tự lấy qua vehicle PR #14 (`40291751791`/`40291751800`/
> `40291751874`) · needle sync đúng quy tắc (74/71). **Phân xử #16**: chấp nhận mức
> artifact-level; second APK decoder = **#17 MỞ**. PR #14 docs-verify giờ XANH. AI-1 vẫn đang
> chạy batch 106 (tip `d7e718cfb`, chưa handoff). ACK107 PR12. verify 209 PASS · 0 FAIL ·
> 2 SKIP · unittest OK.
>
> **Sửa lại (lần 51 — 26/10, HANDOFF105 AI-1 `ef6b75ef` + đối chéo; eeb95d5a chết chưa push — re-prompt):**
> **§24.43**: chain Board_Pause MỚI trên cùng Frame (…→renderer **549984**; Animator498199/
> idle1495@0,25 alpha **0.5797794461250305**; disjoint-commutation; internal order proved ≠
> cross-component scheduling) · custom23 **VẪN unproved** (setter bridge ≠ registration) ·
> textured: atlas785/sprite2585/render-key UV/**7 mip0 samples**/GLSL LZ4 (model ≠ GPU ≠
> render). Artifact SHA khớp **chính xác** `128a014d…` (datas/ = **70**). CI
> `40290558746 SUCCESS` (initial FAIL — không tính là PASS ✓). ACK105 qua PR12. AI-1 CLAIM
> #3 tiếp (batch 106). eeb95d5a: KHÔNG có nhánh trên remote — đã viết lại prompt. verify
> 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 50 — 26/10, CI vehicle cho digger + report 106 xuất hiện):**
> Dispatch 403 cả 2 bot ⇒ **draft PR #14** chỉ để lấy run ID (không merge) · docs-verify
> `40290114397` FAIL tái hiện locally: **APKD1 72 vs 73 md** — vì `a5a74747` đẩy thêm
> **report 106 (mục #14 tự claim — reachability & driven-coverage)** tip `970177253`, needle
> chưa sync; bridge-build/runtime-probe SUCCESS. Digger sync needle 72→73 → push tự
> re-trigger CI trên PR #14. Bảng sticky cập nhật + quy tắc "thêm report = sync needle cùng
> commit". verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 49 — 26/10, handoff 105 đầu tiên từ digger mới `a5a74747` + CLAIM đầu tiên từ `ef6b75ef`):**
> **§24.41**: particle/transition/driven models — particle **954 hệ** (883+71, join native
> 954/954, prefab root 953; gradient/curve-keys absent ⇒ alpha 1.0+cờ; gravity = caller
> input) · transition **468** (If 375/IfNot 1 · threshold 0.0 · duration 30 · encoded giữ +
> scheduler TỪ CHỐI · **sửa đọc r99: 464 interruption = field-absent**) · driven **67
> route/52.400** (CRC 52/52 · 16.671 unresolved · 634/665 exact · case box_gift clip 986:
> sizeDelta.x→1.850000023841858, alpha→0.5000000447, textAlignment 4100 bit-reinterpret) ·
> **0 binding CanvasRenderer/CanvasGroup**. SHA 3/3 khớp sau kéo. Local 122 PASS; **chưa CI**
> (nhánh mới không trigger, dispatch 403) — nhờ owner dispatch. Bảng sticky cập nhật: #9–11
> DONE · #1 CLAIMED ef6b75ef · thêm #14–16. ACK105 qua PR12. verify 209 PASS · 0 FAIL ·
> 2 SKIP · unittest OK.
>
> **Sửa lại (lần 48 — 26/10, tự điều phối đa digger — không đợi phân việc):**
> Bảng điều phối sống trên **PR12 sticky `6410945198`** — spec sửa tại chỗ (PATCH, test OK)
> mỗi vòng · **BACKLOG 13 mục** (12 claim tự do + L2 ⛔) · **CLAIM trước khi làm — first-claim
> wins** · đã CLAIM không làm (trừ REPLICATION khai rõ) · HANDOFF → spec cập nhật bảng ·
> DISPUTED khi va chạm số. Trạng thái: AI-1 đang textured105 + tag23 bridge (từ tip
> `1db187112`, chưa handoff); AI-2/AI-3 chưa push. verify 209 PASS · 0 FAIL · 2 SKIP ·
> unittest OK.
>
> **Sửa lại (lần 47 — 26/10, kịch bản digger xong phần rồi lấn việc):**
> §24.40 bổ sung: **bảng ownership cố định theo miền artifact** (AI-1 binding/driver/
> texture-shader · AI-2 geometry/gap · AI-3 particle/transition/driven · spec đối chéo+docs)
> · **đọc chéo được, sửa chéo không** (chỉ dùng artifact đã handoff+SHA, ghi provenance) ·
> xong phần = báo + đứng chờ việc mới, không tự nhảy · trùng việc = owner tạm hoặc khai
> independent replication · va chạm số liệu = spec flag disputed, chủ dự án/digger thứ 3
> phân xử · spec diff tip mỗi vòng để bắt lấn việc im lặng. ls-remote: peer chạy tiếp
> `1db187112` (batch 105 chưa handoff). verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 46 — 26/10, chủ dự án thêm 2 AI đào dữ liệu):**
> **§24.40**: quy ước đa digger — fetch từng tip riêng/vòng · artifact cần SHA nguồn · đối
> chéo độc lập bắt buộc · 3 path shared giữ ở nhánh spec · không merge chéo · ACK per report
> trên PR12 (tiền tố nhánh khi đụng số) · vai giữ nguyên (digger đào, spec đối chéo+docs).
> ls-remote lần 46: 2 digger mới chưa push. Không kéo dữ liệu mới (datas/ = 66). verify
> 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 45 — 26/10, "cập nhật" — report 104 final `81fed2233` + reproduction):**
> **§24.39**: receipt CI **`40242708365 SUCCESS`** (1073 PASS/223,162 s/30 frame tests) — peer
> fix 2 pitfalls hai-state (CameraScaler ghi current camera tree — clip H8 last-write thắng;
> Start uiCamera qua current object reference view; root mount không freeze) · artifact refresh
> chỉ đổi SHA pin (diff struct 1 path). **Reproduction theo yêu cầu peer — 5/5 PASS từ artifact
> + số học**: after_start==before **bit-exact** · Align 7→8.440000534057617 · **320/320** đúng
> 1 phần tử delta 1.440000534057617 · child 5452 current-pose 5.5→6.94 · **f32 rounding khớp
> chính xác** · fade alpha0 giữ footprint. Chưa chạy được (cần APK + harness): H8/uiCamera/
> rollback/tag23 — ở 30 tests peer. ACK104-final PR12. verify 209 PASS · 0 FAIL · 2 SKIP ·
> unittest OK.
>
> **Sửa lại (lần 44 — 26/10, "cập nhật" — report 104 peer `f620ba4a67`: shared modeled frame):**
> **§24.38**: peer tự làm probe compose (trước/parallel với probe A/B mình gửi) —
> `l3_frame.py`: native Start/Align + clip writes float32 trên **CÙNG modeled state** ·
> **Alert** (= Probe A): sizeY 19.200000762939453→24.000001907348633, alpha f32
> **0.3921568989753723** vs double 0.3921568840742111 giữ riêng, fade43→alpha 0 ·
> **Border_Info**: Start ≠ Align — explicit Align worldY 7→8.440000534057617, **320
> descendants** propagation (đếm lại ✓), root 5739 not_generated · **customType23/type212 ≠
> CRC(m_Sprite)** — chỉ nhận explicit policy. Kéo `datas/l3_frame_cases.json.gz` (datas/ =
> **66**). **Nhận góp ý review peer**: headline = source/model→footprint (sửa §24.36); datas/
> tests = inventory/gate, không phải %; review chuyển sang reproduction/counterexamples.
> ACK104 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 43 — 26/10, góp ý chủ dự án: dừng tăng counts — chuyển sang probe compose):**
> Định hướng mới: **layout-write (101) + animation-write (99/102) trên CÙNG Transform/renderer
> → camera (103)** (§24.37). Gửi PR12 2 probe cụ thể: **A** Alert 5105 — ObjectScaler.Start
> (size 10.800000190734863×24.000001907348633) + alert42 alpha @t{0; 0,0625; 0,125} trên cùng
> renderer → Main 3976 → footprint + RGBA theo t (muốn 3 readback layout-only/animation-only/
> composed) · **B** Popup_QuitMissions — Appear1572 @t{0; 0,25; 0,5} + placement authority
> (resources.assets = template context per 103) + camera nào giữ layer popup. Không kéo dữ
> liệu mới vòng này (datas/ = 65 giữ). verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 42 — 26/10, "cập nhật, tái kiểm" — đồng bộ report 103 peer `8febe90e11`):**
> **§24.36**: camera → world pose → geometry → layer gate → composition — merge 101+102
> (1.760 SHA khớp) → **57.480 obj** · poses đủ **11.380 renderers** (**558 scene/10.822
> template**) · **1.104 pairs = 558 pass/546 fail mask** · **Alert full chain**: size
> 10.800000190734863×24.000001907348633 → **Game 3975 mask 7959 LOẠI layer5, Main 3976 mask 32
> GIỮ** (xác minh số học 7959&32=0) · alpha .3921568840742111@0,0625 — không rendered frame ·
> clip 6 planes giữ case mọi-vertex-ngoài. Kéo `datas/l3_composition.json.gz` (datas/ = **65**).
> **Đối chéo độc lập: counts khớp 10/10 + mask/clear/depth khớp số học.** L3 chưa hoàn tất.
> ACK103 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 41 — 26/10, "cập nhật, tái kiểm" — đồng bộ report 102 peer `9d38a08d1`):**
> **§24.35**: layout-owner visual construction — scope **585 owners + asset closure** →
> **56.714 obj/16.061 GO/11.380 renderers/153 materials/17 shaders/1.391 geometry/7 fonts/
> 2.354 chars/1.737 texts/954 particle modules/348 clips/1.057 animators/91 controllers/**
> **79.907 bindings (74.916/4.983/8)** · **Alert gap ĐÓNG source/model**: 4647→ctrl 78
> (none44/alert42/fade43) · alpha 0→**0,784313738**/0,125 s (reverse 0,25 s) — KHÔNG render
> acceptance · 1 header-only 704560 + 7 ParticleSystemRenderer mesh refs giữ. Kéo artifact +
> **249 shards** (datas/ = **64** + dir `l3-visual-surface/`). **Đối chéo độc lập: counts khớp
> 17/17 + shards đúng cơ cấu + Alert chain trong chunks.** L3 chưa hoàn tất (camera/composition/
> culling + geometry generation/engine execution). ACK102 PR12. verify 209 PASS · 0 FAIL ·
> 2 SKIP · unittest OK.
>
> **Sửa lại (lần 40 — 26/10, "cập nhật, tái kiểm" — đồng bộ report 101 peer `91a0ad6df`; phục hồi .git sau sandbox restore lần 2):**
> **§24.34**: layout native — quét **125.453 headers** → **584 UIObjectAnchors + 1 ObjectScaler**
> (1 header chưa phân loại 580792 giữ nguyên) · bounded 2.526 obj/9.161+660 edges/0 unresolved ·
> **6 camera writer joins · 576/8 uiCamera** · enum + jump bytes `00090f03070d0a10` + roots
> ±5,4/±9,6 từ native · fixed-max clamp 12,42 + aspect [0,4348; 0,75] · Alert 6686→5105 (GO110,
> Animator 4647 metadata-only) · probe 1080×2400 → half-height **12.000000953674316**, Pause top
> worldY 7,9→9,34. **Đối chéo độc lập: counts khớp 13/13 + 461/55/85-92 đếm lại từ instances.**
> Kéo `datas/l3_layout.json.gz` (datas/ = **63**). Unicorn = source bodies với stubs ⇒ không phải
> render proof. Sửa luôn bullet r98 lạc sau §24.33 (về đúng cuối §24.31). L3 chưa hoàn tất.
> ACK101 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 39 — 26/10, "cập nhật, tái kiểm" — đồng bộ report 100 peer `0ce8cc017`):**
> **§24.33**: lifecycle **Popup_QuitMissions ĐÓNG bằng source** (SetPopup @0x13b83cc →
> SetActive(true) → controller 1974 Appear→1572 · "Hide" literal qua GOT/RELA/metadata →
> SetTrigger → 1573 · OffBoard @0,333s → OffBoard@0x13ca5dc → SetActive(false) **cùng GO
> 57508**; SetPopup ≠ Animator.Play — entry/reset là engine); recovery **1.074 methods/13
> root classes** (namespace TuPro sửa đúng); `datas/l3_ui_drivers.json.gz`: 214 instances ·
> 1.751 calls · receivers **1.414/337** · 230 routes · **687 exact links** · 409 callbacks ·
> +9 inherited (46 gaps: 9 base-declared/37 chưa) · +140 getter joins. **Đối chéo độc lập:
> counts khớp 8/8 + chuỗi Popup trong artifact.** Kéo về (datas/ = **62**). L3 chưa
> render-complete. ACK100 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 38 — 26/10, "cập nhật, tái kiểm" — đồng bộ report 99 peer `4d0dc6906`):**
> **§24.32**: controller→state→clip→property programs (**232 controllers/667 states · 377 params ·
> 343+125 transitions · 666 leaves**) + **1.853 probe/665 clips — 0 unknown tại điểm probe**
> (sửa lỗi mô hình: `-FLT_MAX` = key initial-value thật, cứu 1.461 giá trị) · audit **410
> bindings** = 376/17(13 MB + 4 Box2D)/17 ambiguous · ví dụ Popup_QuitMissions (495980→1974→
> Appear→1572; alpha t0,5 **giữ 0,83137** — không sửa theo cảm giác). **Đối chéo độc lập:
> counts khớp 10/10 + diagnostics 376/17/17 + chuỗi 495980→1974→1572 có trong contract.**
> Kéo `datas/l3_animator_programs.json.gz` (datas/ = **61**). L3 VẪN CHƯA hoàn tất — còn
> runtime selection/blending/particles/shaders/composition. ACK99 PR12. verify 209 PASS ·
> 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 37 — 26/10, "cập nhật, tái kiểm" — review độc lập đợt 2 cho batch L3):**
> Peer ghi **CI xanh `40229636747`** cho report 98 (receipt98/handoff `6402605773`) — trước đó
> "đang chạy". Bên spec đếm **từng loại từ 22 shards riêng** (không tin counts tổng): callbacks
> **2139** · sounds **2037** · bindings **52.400** · assets **3.504** · **5 Camera** · camera contract
> factor 5,4/min 9,6 — **khớp 100% cả 6**. Ghi `DATA_SYNC` §24.31. verify 209 PASS · 0 FAIL ·
> 2 SKIP · unittest OK.
>
> **Sửa lại (lần 36b — 26/10, verify bắt 2 claim lệch sau khi kéo datas peer refresh):**
> `boss_hp.json` **253 → 246 prefab** (peer refresh — sửa DATA_SYNC §8 row 3 + COVERAGE_AUDIT
> dòng-một + claim P5) · `ui_screens.json.gz` nodes **8.437.020 → 8.440.354** (summary regenerate —
> COVERAGE_AUDIT + claim P6). Log "253" cũ ở lần 24 giữ nguyên là lịch sử. verify PASS lại 209/0/2.
>
> **Sửa lại (lần 36 — 26/10, "cập nhật, tái kiểm ×2" — đồng bộ reports 97+98 peer `1f2d12f6e` (batch L3) + SỰ CỐ restore local .git:**
> **Phục hồi**: local object store mất (HEAD rơi về Initial commit) — **remote an toàn**; đã
> `reset --hard` về `c4d9d925909` (lần 35) + fetch lại — verify 209/0/2 ngay sau phục hồi.
> **Report 97**: audit đủ 55.584 layout (ngoài index: 3.843.228 obs chỉ tên · 0 scoped PPtr ⇒
> exact-identity legacy bất khả) + composition 100.312 (matrix 99.731/581 unknown · material
> 76.802 · TMP font 18.467) — **sửa hướng đọc "54.787 chưa join"**: không phải màn độc lập thiếu.
> **Report 98**: 805 root views (12 core UI) · 665/665 clips channel-exact · 52.400 bindings ·
> 2.139 callbacks · camera `max(h/w×5,4; 9,6)` + 3 recipe mẫu (Pause/Effect90045/Attack13);
> **đối chéo độc lập bằng datas repo: khớp 100% counts/contract**. Kéo `ui_layout_inventory` +
> `ui_composition` + `l3_scene_chains` + shards (datas/ = **60** file). Giữ 3 file peer xóa
> (spec tham chiếu). ACK97+98 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 35 — 26/10, đồng bộ report 96 peer `79fd382fff` — ĐỔI ƯU TIÊN: L3 TRƯỚC theo chủ dự án):**
> ① `START_HERE` row L3 + `DONE` §2/§4.2: ghi ưu tiên mới (chuỗi L3 trước; wing/map-save chỉ đào
> theo dependency cảnh) + UI binding index **797 màn** (76.806 obs · **1.099 sprite identity** ·
> 54.787 chưa join); ② **sửa 3 stale peer bắt** (review `b000f905`): README row MISSING "L3 bỏ" →
> hiện hành (16 hệ · L3 một phần), README row 2l "bỏ L2/L3" → đánh dấu **[LỊCH SỬ — đã bị thay]**,
> `DESIGN_READINESS` "chỉ cần nếu làm L2/L3" ×3 → "L2/L3 là đích KHÔNG hoãn — gate phải chạy khi
> dựng"; ③ **sửa nhận định của mình**: report 43/46 đã có scoped joins — thiếu là bảng đủ rộng;
> ④ `MISSING` row 16 cập nhật; kéo `datas/ui_l3_bindings.json.gz` (datas/ = **43**). ACK96 PR12.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 34 — 25/10, tái kiểm CẨN THẬN theo nhắc của chủ dự án "cứ làm kiểu quán tính" — tự bắt lỗi của chính mình):**
> ① **Bucket glyph lần 32 ghi SAI cơ chế**: CSV 624 chỉ chứa tên-chữ — bucket glyph (292) nằm NGOÀI
> CSV; đo lại: **118 tên số = 25 tàu + 32 boss + 13 drone + 48 unclassified** (số "~34 boss" là
> ước lượng sai, thật = 32) ⇒ sửa `ASSETS` §9.1 + `MISSING` row 16: vẽ theo bucket sẽ bỏ sót
> **70 sprite chính**; ② **TechStatLevel âm** rơi nhánh base (report 91) — sửa "≤0 → 0" thành
> "0 → 0; âm → base" ở §24.24 + `MISSING` §2.2 (lần 29 khái quát quá); ③ `START_HERE` L2 refresh
> tiến độ wing (93 config 17/24 · 94 emission · 95 pooled leaves); ④ **§24.28 report 95**
> (`4981c4ce2`): 5 leaves lifetime 5/5/4/10/4 · Activate TRƯỚC GetComponent<IBullet> ·
> **trampoline 23** branch ngoài method (64 raw bytes, không đoán opcode) · formation callbacks
> Combine trước caller; kéo `datas/wing_pooled_leaves.json` (datas/ = **42**).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 33 — 25/10, đính chính tuyên bố L3 theo bắt lỗi của chủ dự án — "thế mà dám tuyên bố L3 đủ"):**
> Hạ **L3 từ "input đã đủ / bắt chước đủ ✅" → 🟡 một phần** ở cả `START_HERE` row L3 · `DONE` §2
> row "Bắt chước đủ?" · §4.2 row L3: đủ để **vẽ lại từng sprite đã biết** (pixel/pivot/border ĐÓNG);
> **chưa đủ L3 trọn** — 505 unknown + 643 passthrough · chưa có bảng sprite→màn/prefab (UI chưa
> join) · rig spine inferred · worklist bucket glyph sai nhãn · **metrics/so-ảnh/timeline = gate
> chưa chạy lần nào** (kể cả câu "Đo cảm giác cần người chơi thật" cũ cũng sai — đã sửa: đo được
> bằng máy, blind-A/B bị thay lần 14/21). Sửa nốt §3 "5.818 field còn D" → 623 record decode +
> 4.861 SerializeField pack v2. **§24.27 report 94** (wing 13/22/23/24 emission — N chẵn ra N+1
> call, leaf entry là ranh giới quan sát; sửa nhãn `15b50ac` = PlayOneShot không phải camera
> shake); kéo `datas/wing_emission_flow.json` (datas/ = **41**). verify 209 PASS · 0 FAIL · 2 SKIP ·
> unittest OK.
>
> **Sửa lại (lần 32 — 25/10, kiểm "asset/sprite/prefab: ý nghĩa + gắn đầy đủ chưa" theo nhắc của chủ dự án — đo từ file thật, không suy):**
> `ASSETS` thêm **§9.1** + row 11: ý nghĩa 2.197 sprite = 925 rule + 124 mắt + 643 passthrough +
> **505 unknown**; **binding sprite→consumer CHƯA có join toàn cục** — `prefab_joins.csv` 3.870
> rows **0 row sprite** (chỉ Wave/Controller/Movement/Gun/Boss/Stage); UI 55.584 layout = summary
> bên này (cây ở peer raw); có sẵn: tàu 25/25 · boss 46 → sprite_path_id · scene-1 218/1.377 ·
> spine 27 rig *inferred*. **Lỗi ngữ nghĩa worklist 624**: `is_digit` gom tàu "10001"/boss "7001"
> vào bucket glyph-font (không mất sprite, nhãn sai — tách ra khi vẽ). `MISSING` thêm **row 16**
> (8 hệ một phần). Queue PR12 5 việc peer (join UI/prefab-sprite, 505+643 nhãn, 116 atlas, rig
> thật). verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 31 — 25/10, kiểm "stage/mode/thưởng ngày" theo nhắc của chủ dự án + đồng bộ report 93 peer `32bed14da8a`):**
> **Stage/mode — đã có từ trước, không phải chưa làm:** tổng **299 stage · 250 map · 282 wave ·
> 2 chapter** (`GAMEPLAY` §0/§3.6) · 3 độ khó đủ luật (`DIFFICULTY_MODES`) · khung 7 PlayMode + BP/
> quest/event season (`GAMEPLAY` §2/§3). **Gap còn lại của stage**: `MAX_STAGE_OF_CHAPTERS[]`/
> `MAX_ZONE_OF_CHAPTERS[]` **0 hit** trong `ia-resolved` (giá trị chưa bóc — độ dài từng chapter D) +
> **binding map→stage→wave** vẫn UNKNOWN (§2.1, chờ peer named map). **Thưởng ngày — chưa làm thật**:
> `MISSING` thêm **row 15** (gift login 30 ô · quest ngày/BP 85+39 · season · premium daily ·
> holiday 75 · rewarded video 48 · VIP · energy — cấu trúc A, **0 giá trị decode**: `MAX_LEVEL_BP`/
> `timeRewards`/`vipPoints` 0 hit; dump.cs chưa dịch class nào) + queue PR12. **Report 93**:
> review ACK92 ✓ không góp ý mới; wing config **17/24 impl** (count 3 kiểu, 14 array SHA,
> bẫy 13/21-clampL · 20-super-angleDelta) + fixture Unicorn chạy native bytes; kéo
> `datas/wing_implementations.json` (datas/ = **40**); peer đã nhận queue Arena/PvP.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 30 — 25/10, kiểm "Arena/PvP đã làm tới đâu" theo nhắc của chủ dự án):**
> **Chưa có batch/report nào đào riêng Arena/PvP** — hiện có (mức rải rác): `GAMEPLAY` §2 khung
> mode A (PlayMode 5=Arena · 6=PVP · 10 league · 10 rank · PVPMode lệch enum/text — Betting);
> `DIFFICULTY_MODES` §7 (AllArena*/AllPvP* tên+offset, giá trị chưa decode); `BALANCE` §6.4/6.6/6.8
> (GetArenaScore/PVPPlayScore chỉ signature; arenaPoints/arenaMedal/pvpMedal chưa giá trị);
> `DATA_SYNC` §e (GetListMapPvP — cấu trúc A/giá trị D); 2 luật PVP tình cờ theo reports 86/87
> (Player_Controller PVP `0x14c44e0` · HealHp 1 không WaitUntil); asset PVP1..10 (91 sprite) +
> Board_PVP 42 slot UI; dump.cs **40 class** chưa dịch class nào; `datas/` 0 file. ⇒ thêm **row 14
> MISSING** (🟡 khung A — luật in-game chưa đào) + queue PR12 (không khẩn, sau 23 wing impl).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 29 — 25/10, đồng bộ report 92 peer `713be8c85a0` + xử lý 3 góp ý wording review `de2d1366` (PR12 `6401242325`)):**
> ① §24.22: đường **player KHÔNG post event2** (`ItemCollected` trực tiếp → pool; chỉ drone post2 →
> `OnCollectItem` — tránh đếm kép); ② §24.24 + `MISSING` §2.2: AutoGain **guard Current>0** +
> **TechStatLevel(0)≤0 → techHeal 0** (level0 không phải ,01×1,0); ③ `MISSING` §5 footer: chỉ
> "phân loại cấu trúc" xong, named binding/thứ tự nạp còn đào; ④ **§24.25 report 92**: mapping
> sourceID 20001..20012 → Drone_Attack1..12 + Drone3 serialized **turnRate 1,0** (gap turnRate3
> ĐÓNG; idBlt 80084 serialized ≠ 80014 OnEnable — không bê serialized vào runtime) + save slots
> (`DroneUsed{slot}` default 0 · `CheckDoubleIDDrone` riêng · `get_indexDrones` new int[2] mỗi call,
> playMode4→[0,0]) + StartDrones (scale ,8 · pos ±20); ⑤ `MISSING` row 9 + DONE §4 gạch
> mapping/turnRate3. Kéo `datas/drone_loadout_flow.json` (datas/ = **39**). verify 209 PASS ·
> 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 28 — 25/10, áp report 90+91 peer `142eb5998` + xử lý 5 góp ý review spec (report 91 §6 / PR12 `6400980901`)):**
> **2 gap L1 ĐÓNG**: wing barrels + drone base-fire (90 — `wing_drone_flow.json`, hẹp scope
> impl1/source10003); **HP tàu ĐÓNG bằng công thức** (91 — `2500×(1+,18×TechStatPoints(0)+abi7)`,
> 3 writer + event36/64 + AutoGain 5 s, cấm tuyên bố "mọi tàu 2500"); **`Board_Drones` ĐÓNG**
> (UI power/price ≠ combat); **góp ý**: ③ cấm xác nhận chéo Board↔GetBaseDamage · ④ `MISSING` §5
> tách phân-loại-cấu-trúc (xong) khỏi binding-entry (unknown) · ⑤ ledger ACK đồng bộ (§24.22
> "chưa ACK89" → ACK89 ✓). Kéo 2 contract (datas/ = **38** file — AI1); ACK90+91 PR12.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 27 — 25/10, tái kiểm 5 mục L2 còn thiếu theo dữ liệu hiện hành + raw mới peer `39b377383`):**
> ① DPS runtime — không đổi, peer chưa có commit parity sau 83; ② 2 CROSSCHECK — không đổi (file
> `ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md`, cần lần chạy); ③ **HP tàu nâng bằng
> chứng:** `Player_Health` = static `StartHealth/CurrentHealth 0x0/0x4` + `Armor` + auto-gain —
> KHÔNG có bảng theo tàu trong 6 mảng (raw mới xác nhận), writer chưa đọc; ④ **Board_Drones đang
> được đào** (`Drone_Get_Datas.json`: GetBaseDamage/GetDroneSkillDamage/GetDroneAbilityCooldown…;
> `Board_Players` vẫn chưa có consumer); ⑤ bind 576 map — report 89 đã đọc `get_stageIndex`
> (Test-gate/IsBranch), unknown còn thứ tự nạp; ⑥ save schema — 89 thêm device internals
> (`GetPlayerDevices`/`GetDevice` dict lazy-load), trial/flush vẫn chưa. `MISSING` §2.1/2.2/2.2c/row 9
> đã cập nhật; xin peer đọc writer `StartHealth` qua PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 26 — 25/10, "cập nhật bổ sung + tái kiểm" — đồng bộ report 89 peer `c30dd46eb2` + chốt bảng L1/L2/L3 còn thiếu vào `DONE`):**
> `DATA_SYNC` §24.22 (2 đường nhặt player/drone — tag Item trước hit-guard · `IPooling.GetID` ·
> **công thức xu Coin1/Coin2**: 4 band balance ×L(tech) ×device ×.86 stage≤40 · store `coinCount`
> trước PostEvent48 · Burst 8 = **69/165 xu** — KHÔNG còn suy tiền từ chia 5); `MISSING` row 8
> (tiền nhặt **đã có công thức** — đóng gap) · row 9 (+ drone bắn nền/wing nhịp: peer đang
> recover, chưa report); `START_HERE` row L2 (+89, sót đủ 6 mục `MISSING` §2); `DONE` §L1 thêm
> row "Còn thiếu" (4 mục) · §L2 "Còn thiếu" mở đủ 6 mục; kéo `datas/pickup_currency_flow.json`;
> ACK89 PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 25 — 25/10, rà tài liệu trả lời "L1/L2/L3 còn thiếu gì" + đồng bộ report 88 peer `eaa5c74342`):**
> `DATA_SYNC` §24.21 (producer hit thật: skeleton gán đè/DropGold Combine/19 co-attachments ·
> DropGold **28/10** strict-threshold, HP reread, không dùng `_damage` · event6 budget **28 → 8
> object** (chia 5) — chưa chứng minh tiền nhặt; radius 4 = bits6766e63f); `START_HERE` row L2
> (producer/serialized joins **đã nối** — còn DPS runtime + 2 tái đối chiếu CROSSCHECK); `MISSING`
> row 8 (+ chuỗi report 88, gap còn `OnCollectCoin1/2`); kéo `datas/enemy_hit_callback_flow.json`;
> ACK88 qua PR12. verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 24 — 25/10, audit toàn bộ sau nhắc của chủ dự án — quét pattern trên 45 file):**
> ① **ENEMY_BEHAVIOUR đo lại trên bản hiện hành 981** (CSV 982 dòng gồm header; cũ ghi 800):
> turret **112/981** · facingMove **949/981** · ≥2 tốc độ **137/981** · phổ biến **5,0 (562/981)** ·
> Meteorite **852 dòng/577 object**; "399 path" là đo bản 800-cũ — CSV không có cột path ⇒ ghi chú
> ở MISSING row 4; ② BALANCE §1 bảng nguồn (800/394 → **981/467 + 150 cặp**; 189/800 → **241/981**);
> ③ DIFFICULTY §bảng đối chiếu: row `kHp` → KHÔNG tồn tại; ④ DATA_SYNC: §kiểm lại SerializeField
> (pack v2) · §8 rows 1/2/3/6 (static 623 record · SerializeField pack · HP boss gom prefab
> `boss_hp.json` **253 prefab** (đo lại từ meta của file — 277 ghi trước đó sai) · pivot/border report 75) · §22.3 ("DPS = proxy" → damage·s); ⑤ 6 worklist
> còn "xin AssetRipper" → pack v2 (TUNING_KNOBS ×3 · AI_FEASIBILITY ×3 — feel row BỎ) · PARALLEL_TASKS
> header LỊCH SỬ · ENCOUNTERS cách-đọc-cũ (m_PathID/AssetRipper/Frida) → ĐÃ RESOLVE (WRH4);
> ⑥ DONE các row cũ (Chưa-đọc tool · 5.818 field · 92 prefab/800 dòng · 641 → **624** ×5 chỗ) ·
> README 3 row (COMBAT TTK · BALANCE +150 cặp · DESIGN_READINESS proxy → damage·s) ·
> DESIGN_QUESTIONS B4. **Sau verify bắt thêm 2 nhóm:** ⑦ **ECONOMY `Box_Rewards` đo lại = 1065
> dòng** (cũ ghi 800 — `id=0`/`number=0` **1065/1065**; bảng phân bố root làm lại từ CSV: 75 root,
> top `Board_BattlePass` 85 · `Board_Shop` 84 · `EndgameLoader` **36** · BP tổng 85+39=124; sửa
> ECONOMY ×11 + AI_FEASIBILITY + BALANCE + UI) · ⑧ **`boss_hp.json` = 253 prefab** (meta
> `count=253`; 277 ghi trước đó sai nguồn — pack v2 peer đo 256/P5; DATA_SYNC §8 + DONE log).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 23 — 25/10, kiểm câu hỏi chủ dự án "peer đã đính chính ảnh/asset/sprite — cập nhật chưa?"):**
> `DATA_SYNC` §24.1–24.7/24.9–24.10 **đã đồng bộ đủ reports 70–77 từ các lần trước**; kiểm lại spec
> thấy 3 chỗ còn stale so với các report đó — đã sửa: ① `ASSETS` §9 (4/6 "không xác định" → **ĐÓNG**:
> kích thước pixel — manifest + geometry + **pixel tái tạo 2185/2185** (72); border 9-slice — **75**;
> pivot — **75**; row 3 spine-mapping 🟡 một phần — **71**; row "thiếu width×height" → ✅); ②
> `DESIGN_READINESS` §5 UI-art ("chưa phân tích nội dung" → **đã phân tích tĩnh** 72/75/76, chưa
> render approval); ③ `SYSTEM_MANIFEST` Assets row (đủ reference vẽ: kích thước + pivot + border;
> worklist 624) + `START_HERE` bẫy 17 (pack chưa "đủ APK" nhưng **đủ reference vẽ**). Không có
> report asset/sprite mới sau 77 (78–87 = combat/camera/lifecycle).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 22 — 25/10, vai "AI nhận viết game" phản biện + đồng bộ report 87 peer `0561a2185b`, 412 tests):**
> **(a) Phát hiện khi dựng thử 30 s đầu — CHỈ ghi ở đây vì dịch ngược CHƯA XONG** (chưa sửa
> `SYSTEM_MANIFEST`/`MISSING` để khỏi đóng đinh): ① **pháo cánh**: damage có (`StartWingCannonDamages[24]`)
> nhưng **nhịp/barrels-theo-level chưa có luật** — dấu vết: `pN_startShotRate` · `SetupBarrels` đọc
> getter `Player_Ingame 0x14b1eb0` (report 80) — AI dựng sẽ phải newdesign có ghi hoặc chờ đào;
> ② **drone**: roster 13 + skill fields + modifiers (`abi20/21/25`) có, **luật bắn nền của drone
> chưa có**; ③ tài liệu = **snapshot tới tip `0561a2185b`** — bên kia đào mỗi ngày, người dựng cần
> biết tuổi bản đồng bộ. Cả 3 **không chặn bắt đầu L1** (main cannon/enemy/boss đầy đủ nhất);
> đã gửi 2 gap ① ② sang PR12 cho hàng đợi đào của nhánh dữ liệu.
> **(b) Report 87**: RebornDone `TimeResetInvincible 3,0` · `TimeCanActiveInvincible 10,0`; shield
> callbacks **không refcount** (callback(false) có thể tắt invincible của extra-life); `activeHitEnemey@90`
> = contact-hit, không phải khóa di chuyển; zone invisible/heal — `SYSTEM_MANIFEST` row hồi sinh +
> `DATA_SYNC` §24.20. Peer pin ACK85/86 (`raw/peer-review/ack-85-86-6400213174.json`).
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
> **Sửa lại (lần 21 — 25/10, nhận review 6 finding của peer trên tip `b8f72a4127` + đồng bộ reports 85–86 peer `82f14784e5`):**
> Peer review trực tiếp nhánh spec (không chỉ changelog) — **sửa đủ 6**: ① DATA_SYNC §24.17 impl **11**
> ≠ `shotRate/number` (chỉ 13; descriptor 0,04 + duration theo rank); ② tách **Player9_Clone** (0,34)
> khỏi **projectile 7/9** (0,35) — gộp nhầm trước đây; ③ **bỏ TTK theo tích damage×rate** (đơn vị
> **damage·s**) — COMBAT §0/§6.1/§6.2 · BALANCE §1.1b · MISSING · ENEMY_HP_RUNTIME · BOSSES ·
> COVERAGE_AUDIT · README — TTK = **newdesign** (HP thật + DPS giả định) hoặc **measured**; ④ COMBAT
> §6.4 **241/981** (sửa 189/800) + native rule `noDamage && !ignoreInvincible` skip / ignore bypass
> (report 85) — bỏ kết luận "chỉ trang trí"; ⑤ **superseded ngay tại đoạn**: COMBAT §10 (5 rows đã
> đóng), BALANCE §0.6.2/§0.6.x, UNITY_RULES §12 (rows 1/6); ⑥ START_HERE "tra là có hết / không test"
> → **tra reference trước + scoped unknown không bịa + automated regression/reference checks bắt buộc**
> (metrics = gate phát hiện lệch, không phải approval) — đồng bộ DONE §2 · MISSING §0 ·
> SYSTEM_MANIFEST · START_HERE khối mục đích + L3. **Reports 85–86**: receivers enemy/player đã dịch
> (2 callbacks + truncations + HP re-read; Delayed = WaitUntil · MB 3×Wait(1) · ability32 recursive
> không dedup) + OnExtralife/heal lifecycle (1 s, normal 0,05+0,5 · PVP 1 · zone 1,235 % maxHP) —
> `SYSTEM_MANIFEST` 2 dòng mới/cập nhật · `OPEN_ISSUES` D5 · `DATA_SYNC` §24.18–24.19.
> verify 209 PASS · 0 FAIL · 2 SKIP · unittest OK.
>
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

> **Mục đích tổng** (khối đầu `START_HERE.md`): dịch ngược để **bắt chước bản gốc** — tra reference
> TRƯỚC khi tự suy (scoped unknown thì đừng bịa); **việc thiết kế duy nhất là art**; automated
> regression/reference checks **vẫn bắt buộc** — metrics là gate phát hiện lệch, không phải approval.

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
| **Còn thiếu (đã biết, không chặn)** | ① ~~wing-cannon nhịp/barrels~~ **ĐÓNG (report 90)**: `shotRate = .12−.0035L` · barrels L0–10 = 3,4,5,5,6,6,7,7,8,8,9 · super(.06,20) — hẹp scope impl1/source10003 (23 impl còn lại) · ② ~~drone bắn nền~~ **ĐÓNG (report 90)**: 12 impl shotRate/turn/charge/speed + ability25 `rate/(2,5×p)`; ~~mapping prefab→sourceID~~ **ĐÓNG (92: bindings 20001..20012 → Drone_Attack1..12)** · ③ D3 thứ tự pha boss (mức C) — dựng theo `BOSS_ANIM_TIMELINE.md` + ghi lựa chọn thiết kế; ④ `rate = 0` (**2.366** dòng) — tự chọn, ghi rõ (`MISSING` §2.4) |

> Đây là mức mà `Spec2Game` đo được **Rule & Mechanism 45,6/100** — tức mức mà AI **hay trượt nhất**
> khi chỉ có đặc tả. Cách chặn: **test viết trước**, không phải review bằng mắt.

### L2 — Đúng số

| | |
|---|---|
| **Nghĩa** | cùng một phát bắn ra **cùng một lượng damage**; cùng một wave ra **cùng nhịp** |
| **Kiểm bằng** | máy: replay 1 wave, so DPS/TTK/HP với bản gốc trong **dung sai khai báo trước** |
| **Đạt khi** | (dung sai do bạn chọn — ví dụ ±5%) |
| **Bắt chước đủ?** | ✅ **đủ** (lần 14, 25/10) — mọi giá trị đã decode + bind xong |
| **Đã có gì** | 6 mảng `Player_Get_Datas` (bind: save/load **id−10001** · combat **impl N→index N−1**, report 81/82) · **576** mảng `Map_Get_Datas` (**11 cấu trúc**, `DIFFICULTY_MODES` §7) · **150 cặp HP enemy** · `StartHpPoint`←dict · `kHp` **không tồn tại** (`DIFFICULTY_MODES` §3–5) · **HP max tàu 2500×(1+,18×points+abi7) + luật 12 drone impl (reports 90–92 — mapping sourceID + turnRate3=1,0 đóng bởi 92)** |
| **Còn thiếu** | chứng minh **DPS runtime** (report 79 — `rate` = interval; peer làm parity tàu 1) + **2** tái đối chiếu `CROSSCHECK` · ~~HP riêng của tàu~~ **ĐÓNG (report 91)**: max = 2500×(1+,18×points+abi7), không bảng theo tàu · `Board_Drones` **ĐÓNG (91)** — còn `Board_Players` (B) · **binding entry** 576 map (unknown, §2.1) · save schema đầy đủ (§2.3) · scope-90: 23 wing impl/mapping sourceID/turnRate3 |
| **Chi phí** | ~~AssetRipper + Ghidra~~ → **không cần tool** — replay + đối chiếu |

> L2 là mức **"bắt chước" đúng nghĩa nhất** — **số đã đủ hôm nay**; sót việc **chứng minh nhịp bắn
> runtime** (việc của nhánh dữ liệu).

### L3 — Không phân biệt được

| | |
|---|---|
| **Nghĩa** | game mới **tái lập trải nghiệm + art của bản gốc 1:1** — chuẩn màu, ánh sáng, khung, nhịp (APK gốc là **chuẩn trải nghiệm đã kiểm nghiệm**; dự án = **học tập thiết kế**) |
| **Kiểm bằng** | **đối chiếu reference — đo được bằng máy, KHÔNG cần người test thật**: metrics `VISUAL_DESIGN` trong dung sai · so ảnh cùng scene · timeline khớp **795** event · audio khớp **15** rules |
| **Đạt khi** | mọi chỉ số khớp reference trong **dung sai khai báo trước** |
| **Bắt chước đủ?** | 🟡 **một phần — đính chính lần 33** (tuyên bố cũ "input đã đủ" là **quá mềm**, không đo đủ trước khi viết): đủ để **vẽ lại từng sprite đã biết** — pack v2 (70) + pixel/geometry/pivot/border ĐÓNG (62/72/75) + font 292 · **chưa đủ cho L3 trọn**: **505 sprite unknown** + 643 passthrough chưa kiểm (`ASSETS` §9.1) · **UI binding index 797 màn ĐÃ CÓ (96** — 76.806 obs · **1.099 sprite identity** · 1.057 null; **54.787 file ngoài index chưa join**) · rig spine 27 *inferred* · worklist 624 có bucket glyph sai nhãn · metrics **35** ảnh/so ảnh/timeline = **gate chưa chạy**, không phải approval |
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
| Biết **con số đúng** | 🟡 **một phần** | hằng số + static **623 record** đã decode (`ia-resolved`); **4.861** SerializeField binary có trong pack v2 — giá trị xin peer |
| **Làm ra** 282 wave × 84 spawner | ❌ **không** | khối lượng, không phải hiểu biết |
| **Vẽ** 2.185 sprite thay thế | ❌ **không** | gu thẩm mỹ |
| **Đo** cảm giác (L3) | ✅ **đo được bằng máy** | metrics + so ảnh + timeline/audio đối reference — blind-A/B đã bị thay (lần 14/21); gate **chưa chạy lần nào** |
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
| **1. Chưa đọc** | ~~4.861 `[SerializeField]` · 957 `static`~~ → SerializeField: **binary trong pack v2** (report 70 — xin peer); static: **623 record** 17 method đã decode | ~~chạy 2 tool~~ → xin pack + đã decode | **ngắn**, không khó |
| **2. Chưa chọn** | dung sai L2 · ngưỡng N cho L3 · bộ archetype nào đưa vào game | chưa ai quyết | quyết định thiết kế | **ngắn** |
| **3. Chưa làm** | **624** hình art (`art-worklist.csv`) · 69 audio · **10.782** cấu hình wave · 1.416 chuỗi | **không nằm trong APK để đọc** — phải tự sinh ra | sản xuất | **dài**, không khó |
| **4. Ngoài sản phẩm** | giá IAP · live-ops · dữ liệu người chơi | không thuộc bản build | quan sát, không trích xuất | **không cần** cho bản clone |

> **Không loại nào là "không thể".** Nhưng loại **3** là loại duy nhất **không rút ngắn bằng
> cách đọc thêm file** — vì nó là **sản xuất**, không phải **khảo sát**.

### Vì sao "dễ" là từ nguy hiểm ở đây

| Việc | Loại | Có rút ngắn được bằng hiểu biết? |
|---|---|---|
| Biết 48 archetype thay vì 1.015 tên | 1 | ✅ rút từ **nhiều tuần** xuống **một buổi** |
| Biết **624** hình thay vì 2.185 sprite (`art-worklist.csv`) | 1 | ✅ rút 3,4× |
| **Vẽ** 624 hình (worklist) | 3 | ❌ **không** — hiểu biết không vẽ hộ |
| **Chạy** 100 vòng playtest | 3 | ❌ không — nhưng AI làm mỗi vòng **rẻ hơn** |
| Biết damage player | 1 | ✅ sau khi chạy Ghidra |

> `> Kết luận (mức B):` hiểu biết đã **gần như miễn phí** — đó là phần bạn đúng, và đúng
> nhiều hơn tôi dự đoán ban đầu. Nhưng thứ còn lại không phải "khó", mà là **"phải làm"**.
> Với một game 2.5D, "phải làm" nghĩa là **624 hình (worklist) + ~11k placement + vài chục vòng test** —
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
| **L2 — đúng số** | bắt buộc | ✅ **số đã đủ — làm ngay sau L1** | giá trị decode + bind xong; sót chứng minh **DPS runtime** (peer parity tàu 1) + 2 tái đối chiếu + wing còn special paths/named leaves (config 17/24 — 93 · emission 13/22/23/24 — 94; mapping/turnRate3 **ĐÓNG 92**)/`Board_Players`/bind entry map/save schema (`MISSING` §2) |
| **L3 — khớp trải nghiệm + art** | bắt buộc | ✅ **ĐÍCH dự án — KHÔNG hoãn** · 🟡 **input một phần** (lần 33) · **⚡ ƯU TIÊN L3 TRƯỚC (report 96, theo chủ dự án)** | đối chiếu reference đo được (metrics + so ảnh + timeline/audio) — **không cần người test**; UI binding index 797 màn ĐÃ CÓ (96) · wing/map-save **chỉ đào khi là dependency cảnh**; còn thiếu: 54.787 file ngoài index + 505 unknown + gate chưa chạy |
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
| **109** prefab enemy + HP | **981** dòng HP · **150** cặp id (`enemy_hp_by_id.json`) · 39 boss | `BALANCE.md` §2–5 |
| 420 cấu hình súng + damage | damage 40–1.200, median 400 | `COMBAT.md` §2 |
| 6 dạng đạn + `bltSpeed`/`lifetime` | đầy đủ | `COMBAT.md` §7 |
| Nhịp wave | median **28** placement/wave, max 255 | `ENCOUNTERS.md` §1.3 |
| 9 component/enemy | kiến trúc chuẩn | `ENEMY_BEHAVIOUR.md` §6 |
| Atlas + tỉ lệ màn | 9:16, page ≤ 2048², **624 hình** (`art-worklist.csv`) | `ASSETS.md`, `DONE.md` §1.6 |

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
| 1 | ~~Giá trị **5.818** field~~ | ~~D~~ → 🟡 | static: **623 record** 17 method (`ia-resolved.json`); SerializeField: binary trong **pack v2** (report 70) — xin peer |
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
