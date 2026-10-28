# DIRECTOR MASTER PICTURE — toàn cảnh dự án + nguyên tắc điều phối theo nguyên mẫu (lần 156; duyệt cuối lần 157)

> **Lần 157 — user hiệu chỉnh vai director: "phải căn cứ theo phần APK đã dịch ngược để ra quyết định, không làm theo quán tính; vai director rất nặng — không chỉ nghiệm thu rồi ra lệnh máy móc; mandate ban đầu chỉ là khung, trong lúc làm phải dựa NGUYÊN MẪU để phát triển game."**
> ⇒ **Nguyên tắc chỉ đạo số 0 (trên mọi nguyên tắc khác): NGUYÊN MẪU LÀ THƯỚC.** Mỗi quyết định (roadmap, chấp-nhận, từ-chối, thứ-tự) phải truy được về dữ liệu APK đã decode (spec + datas) — ghi rõ anchor; chỗ nguyên mẫu KHÔNG trả lời (server-PVP, versioning, store-policy…) mới ghi INFERRED + hỏi user. Director không nghiệm-thu-máy-móc: trước khi duyệt/ra lệnh phải tự đọc tài liệu liên quan (lỗi lần 156 đã sửa).

> Viết theo lệnh user: *"chính bạn phải tự xem lại tất cả tài liệu để có một ý tưởng hoàn chỉnh thì mới điều phối chuẩn được — như này đóng các session sớm quá."* Đây là bản tự-rà của director: quy mô thật, vị trí thật, sai-lầm-lifecycle, và kế hoạch sửa.

## 1. Quy mô thật của sản phẩm (từ spec — con số đếm được)

| Hạng mục | Quy mô gốc WindWings | Coder đã có (M1–M4) | % đường |
|---|---|---:|---:|
| Wave PvE | **282** (236 campaign + 45 boss-wave + **1 lỗi**) · **23.757 spawner** (= Σ `copies`; khớp `class-inventory.csv`) · **11.089 dòng cấu hình** · **22.451 entry** · **45.659 instance enemy** (Σ len×copies) | **1** (Wave_0000, 150 enemies) | ~0,4% |
| Boss | 39 prefab + 1 mini · **795** event có mốc · 268 (prefab,clip) | 0 (chưa hệ boss) | 0% |
| Súng/đạn | **458** súng · 186 loại đạn · damage 40–1.200 | training-gun + 6 prefab gun-alt | ~2% |
| Enemy | 92 type · 150 cặp id→HP · 109 prefab trong wave | pipeline 1 wave | ~1% |
| Mode | **7 PlayMode + 3 PVPMode** (async, server) | 1 (campaign skeleton) | ~8% |
| UI | **797 màn · 150.131 node · 5.831 nút** · 53 board / 63 popup | HUD portrait thô | ~1% |
| Meta | 9 nhánh progression (tàu 25 · drone 13 · tech 12 stat · talent 23 · chapter 6 · arena/BP) | 0 | 0% |
| Kinh tế | 170 IAP SKU · 4+6 tiền tệ · 19 vị trí ads · Coin1/Coin2 | catalog + shop-band dữ liệu | ~15% |
| Âm thanh | 69 clip / 571,5s · 92 id · 15 rule | 0 | 0% |
| Save/live-ops | StarCount · quest 30 ngày · BP 85+39 mốc | 0 | 0% |
| Ngôn ngữ | 19 | 1 (mặc định) | ~5% |
| Art (in-game) | 788 đơn vị vẽ thật (planner) | đang redo 2.5D (A + B) | đỏi-đang-chạy |
| **Tổng cảm tính** | | | **~5–8% đường port** |

**Kết luận 1:** M1–M4 = **bộ xương + vòng lặp lõi chạy được trên 1 wave**. Port thật còn rất dài. Mọi nhận định "coder xong → đóng" là **sai thước đo** — M1–M4 chỉ là milestone đầu của giai đoạn build dài.

## 2. Sai lầm lifecycle của director (nhận lỗi)

| Lỗi | Sự thật |
|---|---|
| Định **ĐÓNG coder `ba257b36` sau verify M1–M4** | Port mới ~5–8%. Coder phải chạy **M5→M12** (roadmap §4) — giai đoạn build là đợt dài nhất của dự án |
| Định **ĐÓNG `ef6b75ef` sau re-check F1** | Verifier cần cho **từng milestone**; chỉ ef giữ build-spec/preset-contract/size-budget phục vụ Gate-4; lại là người duy nhất có protocol kiểm độc lập |
| **ĐÓNG `46e50499` (E)** | Lane research hiện tại hết — nhưng Play-launch follow-up (G13), Gate-7 marketing/UA, giá theo vùng, submit-thật sẽ cần lại. Handoff `LANE_HANDOFF_46e50499.md` đầy đủ ⇒ **lý do tái-mở rõ ràng**, nhưng lần sau nên giữ **dormant** thay vì đóng |
| **ĐÓNG `535b0541`** | Đúng lúc cho lane ANALYSIS (Gate-1 khép) — nhưng port sẽ phát sinh nhu cầu decode mới (boss timing map vào gameplay, binding thêm, dữ liệu UI). **Recall trigger:** coder cần dữ liệu không có trong `datas/` ⇒ mở nhánh decode-mới (prompt có sẵn cơ chế) |
| `a5a74747` + `eeb95d5a` đóng | Đúng — inventory đã trao + lane đã chết. Không đổi |

**Nguyên nhân gốc:** tôi đo tiến độ bằng **milestone-lane** (xong lane → đóng) thay vì **giai đoạn sản phẩm** (Gate-4 build = đợt dài, cần đội thường trực). Sửa nguyên tắc: **chỉ đóng session khi (a) không còn vai trong giai đoạn kế tiếp VÀ (b) recall-trigger ghi rõ.** Giai đoạn build (hiện tại) cần đội thường trực: coder · verifier · planner · auditor · A · B · (curator khi đến lượt) · reviewer · director.

## 3. Vị trí thật trên bản đồ Gate

- **Gate-1: ĐÓNG** ✓ (Phase-A acceptance, sign-off user).
- **Gate-2/3 (kênh + kiếm tiền):** hồ sơ ĐỦ — G9–G17 chốt theo ủy quyền; chờ trình user gộp lúc build ổn định (không gấp — không chặn gì).
- **Gate-4 (kỹ thuật build):** coder F1–F7 fixed + CI xanh; **còn thiếu thật** = export_presets.cfg + version.json + artifact + export log (F2) — tức Gate-4 chỉ mở khi **game đủ nội dung đáng export** hoặc theo mốc build-thử. USER-only: keystore/SDK/quyết MSIX-vs-EXE/quyền IP.
- **Gate-5 (assets):** A/B đang redo theo 149+154; auditor calibrating; curator chờ sau auditor.
- **Gate-6 (submission):** kits đủ 3-store-A; sẽ cần refresh theo ngày nộp.
- **Gate-7:** chưa mở.

## 4. Roadmap build — mỗi mốc gắn ANCHOR NGUYÊN MẪU (chấp-nhận = khớp nguyên mẫu đo được, không phải "trông ổn")

| M# | Nội dung | ANCHOR trong nguyên mẫu (dữ liệu đã decode) | Chấp-nhận khi |
|---|---|---|---|
| M5 | Multi-wave loader + stage/map flow | `datas/waves.json` **282 wave · 11.089 dòng cấu hình · 23.757 spawner (Σ copies) · 22.451 entry · 45.659 instance enemy (Σ len×copies)**; Map/Stage CSV (250 map/299 stage); rate×spawner ⇒ trận 2,5–4 phút | loader nạp đủ 282; tổng spawner/entry/instance khớp từng wave; **field `count` = 0 ở 11.089/11.089 dòng ⇒ quân tính `len(enemies)×copies`, không đọc `count`**; 5 wave lấy mẫu replay đúng thứ-tự spawn (đo) |
| M6 | Boss system | `datas/boss_anim_events.csv` **795 event · 268 (prefab,clip)** · nhịp 0,17/0,33/1,0/5,0s · 39+1 boss; HP theo bảng | mỗi boss giữ event-map đúng mốc thời gian; sampling 3 boss khớp trình tự |
| M7 | Difficulty + endgame + reborn | `DIFFICULTY_MODES`: levelDelta [1, 2, 3.6, 3.6] **không nhân số quân**; endgame coin+exp+rank; luật reborn §1.6 | delta đúng 4 mốc; số quân không đổi theo mode (đo) |
| M8 | Meta tàu/drone/tech | **25 tàu · 13 drone** (14-ships/drones.csv) · **12 stat** tech · 6 chapter · talent 23 method theo VIP | đủ 25/13 profile; 12 stat cất/đọc đúng; nâng cấp theo mức decode |
| M9 | Quest/BP/gift + save | 30 ô login · **85+39 mốc BP** · Key0-2 · hộp quà; `StarCount` + `StarStageMaster{stage}_{mode}` ngữ nghĩa gốc | chu kỳ ngày/tuần đúng; save field giữ ngữ nghĩa |
| M10 | UI boards subset chơi-được | 53 board/63 popup · 8 tab · luồng Home→Maps→Begin→Endgame→Shop→Quest→Settings | luồng chơi-được liền; số board của subset khớp danh sách trong UI.md |
| M11 | Âm thanh | **69 clip/571,5s · 92 id · 15 rule** | 92 id map đủ; rule bắn/trúng/nổ đúng event |
| M12 | Art + juice integration | art/final-listing (curator) + profile Fire | không drop frame theo ngưỡng; art đúng bộ duyệt |
| M13 | Arena/PVP-local-mock | `l2_535b0541_arena_pvp*.json`: 10 league/10 rank · 6 dải reward · SeasonTime phút ⇒ 10 mùa 68 ngày | mock khớp league/rank/reward; **server thật = INFERRED → hỏi USER backend** |
| M14 | Export-ready Gate-4 | build-spec ef: preset 4.7.2 · APK≤2,5GB(Amazon)/AAB≤150MB(Huawei) · version.json | artifact + log + apksigner đủ theo checklist P0–P2 |

Nguyên tắc gán việc: **coder không tự nghĩ cờ-hình/balance — mọi bảng số trỏ file nguồn; chỗ datas trống ⇒ quay director, director quyết decode-thêm (535 recall) hoặc INFERRED-hỏi-user.**
Ước lượng relative: M5–M7 nhanh (dữ liệu đặc tả dày) · M8–M10 nặng nhất · M13 có thể launch-sau.

## 5. Điều phối sửa lại (đề xuất — chờ user gật)

| Session | Trước (sai) | Sau (đúng) |
|---|---|---|
| `ba257b36` | ĐÓNG sau verify | **Tiếp tục M5→M14** — vai coder thường trực |
| `ef6b75ef` | ĐÓNG sau re-check F1 | **Verifier thường-trực**: re-check F1 (việc nhỏ, vẫn làm) → verify từng M# |
| `65f8a31f` (auditor) | — | giữ: calibration → chấm mọi lô A/B |
| `1b836828` · `5438fec9` · `eca8588b` | — | giữ: planner cổng + A/B redo theo finding auditor |
| `8141386a` | — | giữ reviewer |
| `535b0541` · `46e50499` | ĐÃ ĐÓNG | giữ nguyên trạng thái đóng (không mở lại vô ích) — **ghi recall-trigger**: 535 = khi coder cần decode mới; E = khi Play-leg/submit-thật/Gate-7. Khi trigger bắn, user mở session mới dùng lại prompt + handoff có sẵn |
| curator | — | mở khi auditor xác nhận 1 trong 2 bộ ĐẠT |

## 6. Việc tôi đề xuất NGAY sau khi user gật (không làm trước)

1. Commit master-picture này + đăng board **hủy lệnh ĐÓNG coder/ef** + công bố roadmap M5–M14.
2. ef re-check F1 (không đóng gì) → coder mở M5.
3. Auditor tiếp calibration; A/B nhận finding.
4. Không mở session mới nào cho tới auditor có kết quả calibration (tránh đội hình thừa).
