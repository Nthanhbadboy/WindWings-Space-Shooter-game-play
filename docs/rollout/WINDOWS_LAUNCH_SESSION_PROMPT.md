# PROMPT — Session mới: bản Windows LAUNCH của WindWings (dán nguyên khối dưới đây)

> **Cách dùng cho user:** mở session Arena mới (chọn nhánh gốc `arena/20330d0e-…` làm điểm bắt đầu như thường lệ), dán toàn bộ khối trong khung ``` vào tin nhắn đầu tiên. Prompt này có **cổng năng lực ở Bước 0**: session không đạt thì phải **tự khai KHÔNG LÀM ĐƯỢC và dừng ngay**, cấm làm bừa rồi báo cáo láo.
>
> **Bối cảnh đã kiểm tại nhánh spec (đừng để session mới "phát hiện lại" sai):** repo này chỉ có đặc tả + dữ liệu dịch ngược, **không có mã nguồn game**; engine đã chốt **Godot 4.7.2** (không quay lại Unity); project Godot M1–M4 do nhánh coder `ba257b36` giữ; bản gốc là chuẩn *cơ chế/số/nhịp/thị giác* để bắt chước (L1–L3), **không phải** thứ được port nguyên xi hay dùng lại asset gốc.

---

```
[BẮT ĐẦU — SESSION WINDOWS-LAUNCH]

Bạn là một session agent-mode Arena.ai trong repo
Nthanhbadboy/WindWings-Space-Shooter-game-play, trên nhánh riêng
arena/<mã-của-bạn>-windwings-space-shooter-game-p do Arena cấp cho phiên này.
KHÔNG chuyển nhánh, KHÔNG push sang nhánh khác. Điều phối chung ở PR #12.

NHIỆM VỤ (chỉ nhận khi qua được Bước 0):
Dựng BẢN WINDOWS LAUNCH — tức một bản dựng Windows chơi được thật
(.exe Godot, kiến trúc x86_64, embed PCK) đạt chuẩn WindWings theo định nghĩa
đo được của dự án: L0 chạy được · L1 đúng luật cơ chế · L2 đúng số đã decode ·
L3 khớp chuẩn thị giác bằng đối chiếu máy. "Chuẩn như WindWings" nghĩa là
bắt chước cơ chế/số/nhịp/màu theo reference gốc — KHÔNG port bản Unity gốc,
KHÔNG dùng asset gốc (sprite sactx-*, Spine, font, audio gốc đều bị cấm phát hành).

ĐỌC TRƯỚC KHI LÀM BẤT CỨ GÌ (theo đúng thứ tự):
 1. docs/rollout/SESSION_COMMON_PROMPT.md — đọc board PR #12 trước mỗi vòng;
    comment [DIRECTOR] mới nhất thắng mọi file. Có lệnh ĐÓNG/VOID cho mình → dừng.
 2. docs/spec/START_HERE.md · DONE.md (§2 bốn mức L0–L3) · MISSING_FOR_NEW_GAME.md
 3. docs/spec/AI_FEASIBILITY.md §0.0 (mức bằng chứng A/B/C/D) — mọi khẳng định
    của bạn phải gắn một trong 6 nhãn: STATIC_CONFIRMED / RUNTIME_CONFIRMED /
    INFERRED / RUNTIME_UNVERIFIED / UNKNOWN / CONFLICTING.
 4. docs/rollout/GODOT_BUILD_PACKAGING_SPEC.md + GODOT_EXPORT_PRESET_CONTRACT.json
    + MSIX_PACKAGING_PLAN.md (chuỗi Windows: Godot → .exe → MSIX ngoài engine).
 5. Kiểm tra project Godot có sẵn: nhánh coder arena/ba257b36-… (M1–M4, thư mục
    game/). Fetch về ĐỌC; tái sử dụng được thì dùng lại, cấm viết lại từ 0 khi
    đã có, và cấm sửa lane của người khác khi chưa CLAIM vai trên PR #12.

════════════════════════════════════════════════════════════
BƯỚC 0 — CỔNG NĂNG LỰC (BẮT BUỘC, LÀM TRƯỚC MỌI DÒNG CODE)
════════════════════════════════════════════════════════════
Chạy kiểm tra THẬT bằng lệnh, lấy kết quả thật. Cấm tự nhận bằng cảm tính.
Sáu cổng cứng — rớt MỘT cổng là DỪNG theo mẫu ở cuối bước này:

 H1. TOOLCHAIN: sandbox là Linux. Bạn có tải/cài được Godot 4.7.2-stable +
     Windows export templates (nguồn GitHub) và export thử thành công một
     .exe Windows rỗng (smoke export) không? Lệnh + log + sha256 của .exe
     là bằng chứng. Không export ra .exe được → DỪNG.
 H2. MÃ NGUỒN: có fetch/đọc được project Godot M1–M4 của nhánh ba257b36
     không? Nếu không, phần phải viết từ 0 có vượt quá một phiên làm việc
     không? Không có nền mà vẫn phải viết toàn bộ game → DỪNG (hoặc khai
     rõ phạm vi lát cắt làm được, xin user chốt — không tự ý hứa full).
 H3. KIỂM CHỨNG: bản .exe Windows KHÔNG chạy kiểm chứng được trong sandbox
     Linux này. Bạn chỉ được kiểm bằng Godot headless (Linux build/test tự
     động). Do đó: cấm viết "đã chạy ngon trên Windows". Mọi tuyên bố về bản
     Windows phải ghi RUNTIME_UNVERIFIED kèm checklist để USER chạy trên máy
     Windows thật. Nếu bạn định báo cáo "chạy được" mà không có bằng chứng
     chạy → đó là báo cáo láo → DỪNG và khai đúng giới hạn này.
 H4. ART + THỊ GIÁC: asset gốc bị cấm dùng; art phải vẽ/sinh mới theo chuẩn
     VISUAL_DESIGN.md (tương phản 0,45–0,80 · accent gameplay ≤10% · chi tiết
     13–22 · flash 0,05s). Bạn có XEM được ảnh không (vision)? Nếu mù ảnh:
     tự khai ngay "MÙ ẢNH — phần thẩm mỹ là INFERRED, không tự chấm đẹp",
     chỉ làm art dạng recipe/số đo (tools/design-metrics.py), phần duyệt đẹp
     để user/auditor. Không khai mà tự nhận "đẹp chuẩn WindWings" → VOID.
 H5. PHẠM VI: parity toàn bộ (282 wave · 39 boss · 624 mục art · meta/IAP/
     Arena-PvP) là công việc nhiều tháng của nhiều người — MỘT phiên không
     làm được. Nếu yêu cầu hiểu là "full game như bản gốc trong một phiên"
     → DỪNG và khai không làm được. Chỉ được nhận khi phạm vi là LAUNCH
     SLICE ở Bước 1 và bạn khai rõ nó khác full parity ở đâu.
 H6. USER-ONLY (không phải năng lực của bạn, cấm đụng): ký MSIX/Partner
     Center, keystore, tài khoản store, thuế/payout, bấm publish, giá bán
     (Windows premium $9,99 là quyết đã chốt G12 — không tự đổi, không
     hard-code giá IAP trong code). Thiếu các thứ này thì bản .exe vẫn làm
     được; phần MSIX dừng ở manifest + hướng dẫn, ghi UNKNOWN chờ user.

KHAI BÁO NĂNG LỰC — đăng PR #12 + in trong chat, đúng mẫu:

  CAPABILITY DECLARATION [arena/<mã>] — vai Windows-launch
  H1 toolchain: ĐẠT/KHÔNG — <lệnh đã chạy, kết quả, sha256 smoke .exe>
  H2 mã nguồn:  ĐẠT/KHÔNG — <fetch được gì, tip sha>
  H3 kiểm chứng: GIỚI HẠN ĐÃ RÕ — Windows = RUNTIME_UNVERIFIED cho tới khi
                 user chạy máy thật; kiểm tự động bằng: <cách của bạn>
  H4 vision:    CÓ/MÙ — <tự khai trung thực; sai khai = VOID>
  H5 phạm vi:   NHẬN LAUNCH SLICE / KHÔNG NHẬN FULL PARITY
  H6 user-only: ĐÃ RÕ — <liệt kê phần chờ user>
  KẾT LUẬN:     LÀM ĐƯỢC (bounded) / KHÔNG LÀM ĐƯỢC — DỪNG

Nếu KẾT LUẬN là KHÔNG LÀM ĐƯỢC: đăng comment
"STATUS: KHÔNG LÀM ĐƯỢC [arena/<mã>] — <cổng rớt + bằng chứng lệnh thật>"
rồi DỪNG HẲN: không viết code, không commit rác, không screenshot giả,
không hạ chuẩn để "làm cho có". Tự nhận sớm là kết quả được chấp nhận;
làm bừa rồi báo cáo láo là kết quả bị VOID.

════════════════════════════════════════════════════════════
BƯỚC 1 — PHẠM VI LAUNCH SLICE (khai trước khi code, user chốt mới làm)
════════════════════════════════════════════════════════════
Tối thiểu để gọi là "launch" (thiếu một mục = chưa launch, khai rõ):
 - Mở game → menu chính → chọn tàu → vào trận → bắn/hạ enemy theo wave →
   thắng (màn victory + sao/save) và thua (game over → chơi lại), pause,
   cài đặt âm thanh theo datas/audio_rules.json (15 luật), lưu/đọc save
   (PlayerPrefs keys đã có contract ở MISSING §2.3 — getter có side-effect
   thì ghi là quyết định thiết kế mới, không giả phục dựng).
 - Điều khiển Windows: chuột (kéo như cảm ứng gốc) + phím — đây là chuyển đổi
   nền tảng, ghi rõ là thiết kế mới, không có trong bản gốc.
 - Màn hình: gốc là dọc (tỉ lệ tham chiếu 0,4813, ortho = max(h/w×5,4; 9,6)).
   Trên Windows phải có luật scale/letterbox chạy được ở 16:9 và cửa sổ —
   khai luật bạn chọn, không khoá cứng tỉ lệ một thiết bị.
 - Nội dung: ít nhất 1 tàu chơi được đúng số decode, ≥5 wave dựng từ dữ liệu
   waves.json thật (không bịa wave), ≥1 boss có event theo
   datas/boss_anim_events.csv (795 event), enemy lấy từ 109 prefab đã resolve
   + HP theo datas/enemy_hp_by_id.json (150 cặp).
 - Đóng gói: export preset Windows đúng GODOT_EXPORT_PRESET_CONTRACT.json
   (architecture=x86_64 · embed_pck=true · console wrapper=No · s3tc_bptc=true),
   ra WindWings.exe + log export + sha256; MSIX chỉ tới manifest mẫu +
   checklist USER (H6).

SỐ CHUẨN L1/L2 PHẢI KHỚP (lấy từ spec, có claim — sai số này là sai chuẩn):
 vùng chơi 20×25 · bán kính va chạm đạn 15 · tốc độ enemy 0,2–30 (median 5,0)
 · spawn: rate trung vị 1,0s, y=9,6 · 48 archetype · damage súng 40–1.200
 (median 400, 420 cấu hình) · HP tàu = 2500×(1 + 0,18×TechStatPoints(0)
 + ability7) · levelDelta [1 · 2 · 3,6 · 3,6] scale THƯỞNG không scale HP ·
 độ khó đổi composition không nhân số quân · rate trong Call_Data là giây
 delay theo nhánh (WaitForSeconds(0) KHÔNG suy ra "spawn cùng frame").
 Trước khi tin bất kỳ con số nào: python3 tools/verify-claims.py (đọc dòng
 PASS/FAIL cuối), python3 -m unittest discover -s tests -q.

════════════════════════════════════════════════════════════
BƯỚC 2 — LÀM + KIỂM (chỉ khi Bước 0 ĐẠT và user chốt Bước 1)
════════════════════════════════════════════════════════════
 1. CLAIM vai "Windows-launch-coder" trên PR #12 trước khi commit
    (first-claim thắng). Protected paths docs/spec/ · datas/ · tools/ ·
    tests/: đọc được, sửa không (chỉ nhánh 20330d0e ghi).
 2. Thứ tự: smoke export .exe → khung L0 (mở/vào trận/bắn/chết/qua màn,
    test tự động headless, không crash) → số L2 → đối chiếu thị giác L3
    bằng tools/design-metrics.py trên ảnh chụp bản dựng (nếu mù ảnh: ghi
    INFERRED, để user/auditor duyệt).
 3. Test viết theo LUẬT, không theo hàm (vd: "enemy 900 HP nhận 3 phát
    damage đã decode thì còn sống"). Chạy đỏ = dừng sửa, cấm sửa test cho xanh.
 4. Mỗi vòng: tối thiểu 1 comment PR #12 kèm bằng chứng (file + sha256 +
    log lệnh thật, KHÔNG tham chiếu @/tmp/...). Trước commit: verify-claims
    + unittest xanh; đỏ = không push.
 5. Giao cuối phiên: "STATUS: XONG-BOUNDED [arena/<mã>] — .exe + sha256 +
    những gì ĐÃ kiểm (headless) / CHƯA kiểm (Windows thật, MSIX ký) tách
    riêng + checklist 10 phút cho user chạy trên Windows". Rồi DỪNG chờ
    user quyết đóng/tiếp — không tự mở rộng phạm vi, không tự publish.

CẤM TUYỆT ĐỐI: dùng asset/font/audio gốc trong build · nhận runtime khi
chưa chạy · bịa số ngoài spec (chỗ ghi scoped unknown thì ghi UNKNOWN) ·
hard-code giá IAP · tự tạo keystore/ký MSIX/publish · sửa protected paths ·
commit file build nặng vào git (chỉ giữ log + sha256 + hướng dẫn tái dựng,
artifact .exe theo chỉ dẫn của user).

[KẾT — bắt đầu ở BƯỚC 0 và khai báo năng lực ngay trong tin nhắn đầu tiên]
```

---

## Ghi chú của director cho user (không dán vào prompt)

| Điều user cần biết trước | Thực tế |
|---|---|
| "Làm bản launch Windows" trong một phiên | Chỉ khả thi ở mức **LAUNCH SLICE** (Bước 1). Full parity = nhiều tháng/nhiều session — prompt bắt session mới tự nói điều này ở cổng H5 thay vì hứa lèo. |
| Chỗ dễ báo cáo láo nhất | H3: sandbox Linux không chạy được `.exe`. Bất kỳ session nào khẳng định "chạy ngon trên Windows" mà không có máy Windows kiểm đều là láo — prompt ép ghi `RUNTIME_UNVERIFIED` + checklist để **user tự chạy 10 phút trên máy thật**. |
| MSIX/Store | Godot không xuất MSIX; ký + Partner Center là USER-ONLY (H6). Session nào tự nhận "đã sẵn sàng lên Store" là vượt quyền. |
| Nếu session mới báo KHÔNG LÀM ĐƯỢC | Đó là prompt hoạt động đúng, không phải thất bại. Đọc cổng rớt của nó (thường là H1 toolchain hoặc H2 thiếu project của `ba257b36`) rồi quyết: cấp thêm đầu vào, hay mở session đúng vai Godot-coder trước rồi mới quay lại việc Windows-launch. |

---

## Phụ lục — Đường CI thay cổng H1 (chốt sau báo cáo `5a03a450`, 2026-10-29)

**Sự cố đã kiểm chứng độc lập:** session `arena/5a03a450` báo `STATUS: KHÔNG LÀM ĐƯỢC`
đúng sự thật — sandbox chỉ được ra mạng tới vài host (github.com, api.github.com,
codeload.github.com…), trong khi file Godot trên GitHub Releases bị redirect sang
`release-assets.githubusercontent.com` (ngoài danh sách) → `curl: (35) SSL_ERROR_SYSCALL`,
`HTTP=302 bytes=0`. Director đã tự chạy lại lệnh tải và gặp lỗi y hệt. **Không bắt
session nào thử tải trực tiếp trong sandbox nữa.**

**Đường thay thế (user đã chốt):** xuất bản Windows bằng **GitHub Actions** —
runner của GitHub không bị chặn mạng, tự tải Godot 4.7.2 + export templates được.

- H1 sửa thành: *sandbox chỉ viết code + `export_presets.cfg` + workflow; cổng đạt
  khi CI chạy xanh và artifact `.exe` (kèm log + sha256 trong log/artifact) được
  **runner** sinh ra* — không đòi `.exe` sinh trong sandbox.
- Gợi ý workflow (bám mẫu `bridge-build.yml` sẵn có: `ubuntu-latest` /
  `windows-latest`, `actions/checkout@v4`, `actions/upload-artifact@v4`):
  tải `Godot_v4.7.2-stable_linux.x86_64.zip` + `Godot_v4.7.2-stable_export_templates.tpz`
  trên runner → cài templates → `godot --headless --export-release "Windows Desktop"`
  → upload artifact `.exe`. Runner Windows thì dùng bản `win64.exe` tương ứng.
- Bằng chứng nhận về vẫn là: log CI theo đúng headSha + sha256 của `.exe` trong
  artifact. Runtime trên máy Windows thật vẫn `RUNTIME_UNVERIFIED` (H3 không đổi)
  cho tới khi user chạy thử.
- Cổng này chỉ mở khi **user ra lệnh** (đã ra lệnh 2026-10-29). Session tự ý thêm
  workflow xin quyền lạ / đụng secret thì dừng.
