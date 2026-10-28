# PLAN — Godot-coder scaffold + vertical slice S1–S5 → **Windows `.exe` chạy LOCAL**

> **Lần 160 · 2026-10-28.** User: *"Đây là đang lập kế hoạch nhé, **mày chỉ viết kế hoạch thôi**, trước tiên kế hoạch là **viết để chạy local**"*.
> **Kế hoạch này KHÔNG build, KHÔNG SDK, KHÔNG store.** Chỉ đặc tả công việc + nghiệm thu.

---

## 0. Chốt user 2026-10-28 — 8 mục

| # | Mục director nêu | **Chốt user** | Ghi vào kế hoạch |
|---|---|---|---|
| 1 | Build bản Windows runnable (vertical slice S1–S5) | **đồng ý** | ✅ **Lane chính của kế hoạch này** |
| 2 | MSIX + `Windows.Services.Store` GDExtension C++/WinRT | **để sau** | ❌ **Không trong kế hoạch này** |
| 3 | Reserve app name Partner Center + `Identity@Name/@Publisher` | **làm** | ✅ Kế hoạch phụ (§9) — **không chặn S0–S5** |
| 4 | CI cổng MSIX (MakeAppx · version · Publisher=cert CN · WACK) | **để sau** | ❌ Không trong kế hoạch này |
| 5 | IARC + privacy policy URL | **bỏ** — *"khi release trong MS phải tự điền"* | ❌ **Loại khỏi lane** |
| 6 | Tài khoản store | **"tài khoản tao có rồi"** — đã release **1 app**, hình thức **mua app để chơi** | ✅ Ghi nhận. ⚠ Lưu ý: app cũ là **paid**, game này là **F2P+IAP** ⇒ commerce flow khác (§9) |
| 7 | G10 — consumable vs subscription store | **mở** | ⚠ Mở — không chặn S0–S5 |
| 8 | Quyền IP / phân phối | **"MS sẽ cấp quyền đó riêng khi release"** | ⚠ **Ghi nhận + director cần lưu ý** — xem §9.3 |

---

## 1. Mục tiêu

**Một project Godot 4.x export ra `.exe` Windows, chạy được trên máy user, chơi được 1 wave + boss đầu tiên + save/load.**

Đó là **mục tiêu duy nhất** của kế hoạch này. **Không** phải game thương mại, **không** phải MS Store submission.

```
user cài Godot 4.7.2-stable (Windows editor)
  → mở project
  → export preset "Windows Desktop"
  → double-click .exe
  → thấy: menu → maps → battle → 1 wave enemy → boss → victory → save → reopen còn dữ liệu
```

---

## 2. Ranh giới — cái **KHÔNG** làm trong kế hoạch này

| Không làm | Vì sao | Làm khi nào |
|---|---|---|
| MSIX / AppxManifest / `makepri` / `MakeAppx pack` | user chốt **để sau** (mục 2) | khi bắt đầu IAP |
| `Windows.Services.Store` GDExtension C++/WinRT | user chốt **để sau** | khi bắt đầu IAP |
| CI cổng MakeAppx / WACK / Publisher=cert CN | user chốt **để sau** (mục 4) | lane MSIX |
| IARC questionnaire / privacy policy URL | user **bỏ** (mục 5) | khi submit store |
| Art thật (788 đơn vị vẽ) | session art chưa làm W1–W3 | Gate-5 |
| Store listing / screenshot Windows | không có build Windows + không có quyền | sau S0–S5 |
| Android export (APK/AAB) | lane khác | sau |
| Multi-wave 282 / boss 39+1 / meta / UI boards / audio | scope M5–M14 | sau vertical slice |

**Nguyên tắc:** nếu coder làm gì ngoài S0–S5, **đó là làm lạc lane** — verdict **FAIL**.

---

## 3. Inputs bắt buộc đọc trước khi viết code

| File | Dùng cho |
|---|---|
| `docs/rollout/PORT_PLAN_SCENE_SYSTEM_MAP.md` §3 | **S1–S5** + nghiệm thu |
| `docs/rollout/GODOT_BUILD_PACKAGING_SPEC.md` §1, §4.2, §5 | pin engine + khoá preset Windows + version.json |
| `docs/rollout/VERIFIER_PROTOCOL_GODOT_PORT.md` §3 | bộ kiểm V1–V9 (chỉ phần local) |
| `docs/spec/GAMEPLAY.md`, `COMBAT.md`, `ENCOUNTERS.md` §2–3 | cơ chế bay/bắn/va-chạm/wave |
| `datas/waves.json` | **1 wave** (Wave_0000) |
| `datas/boss_anim_events.csv` | **boss đầu tiên** (không sửa file) |
| `docs/spec/ANIMATION.md`, `BOSSES.md` | event timeline + phase boss |
| `docs/apk-analysis/57-endgame-mission-stars-save-continue.md` + `65-opening-save-keys-cache-and-read-side-effects.md` + `docs/spec/DATA_SYNC.md` | key `StarCount`, `StarStageMaster{stage}_{mode}` — ngữ nghĩa giữ đúng |
| `docs/spec/DESIGN_READINESS.md` §3 | **`rate = 0` = spawn cả loạt (B)** — không phải mỗi frame |
| `docs/spec/BALANCE.md` §5.1 | damage/HP/coin công thức đã decode |

---

## 4. Làm theo thứ tự: S0 → S5

### **S0 — Scaffold project** (không có thì S1–S5 không chạy)

| Bước | Nội dung |
|---|---|
| 1 | `project.godot` — `config_version=5`, `engine="Godot 4.7.2-stable"`, main scene = `Main` |
| 2 | Cấu trúc folder: `scenes/`, `scripts/`, `resources/`, `data/` (chứa `waves.json` copy hoặc symlink — **không copy asset gốc**) |
| 3 | `export_presets.cfg` — preset **`Windows Desktop`** (khoá §5) |
| 4 | `version.json` — nguồn duy nhất cho version (§5) |
| 5 | Scene placeholder: `Main`, `Home`, `Maps`, `Battle`, `Endgame` (5 node/scene tối thiểu, **không art cuối**) |
| 6 | `.gitignore` — **che** `*.exe`, `*.pck`, `*.tmp`, Godot `.godot/` |

**Nghiệm thu S0:**
- `project.godot` mở được trong Godot 4.7.2-stable, không lỗi parse
- `godot --headless --check-only --path .` (hoặc editor import) **không lỗi**
- `export_presets.cfg` có preset `Windows Desktop` với **mọi khoá §5**
- `git ls-files` = **0** file `.exe`/`.pck` (V1)

### **S1 — 5 scene chuyển được**

`Main` → `Home` → `Maps` → `Battle` → `Endgame`

**Nghiệm thu:**
- 5 scene chuyển được (node change_scene hoặc SceneTree change)
- **0 asset gốc trong repo** (V8) — dùng placeholder node/sprite
- Keybinding: menu vào battle được

### **S2 — Player bay + auto-fire + 1 wave** ⭐ **cổng nặng nhất**

- Player di chuyển (mouse hoặc WASD/arrows)
- Auto-fire (hoặc fire theo input — ghi rõ chọn cái nào)
- Nạp **1 wave** từ `waves.json` (`Wave_0000`)

**Nghiệm thu (đếm được):**
- [ ] Số **spawner** = `len(wave.spawners)` khớp file
- [ ] Số **entry** = `Σ len(enemies)` khớp file
- [ ] Số **instance enemy** = `Σ len(enemies) × copies` khớp file
- [ ] **KHÔNG đọc field `count`** — field này **= 0 ở 11.089/11.089 dòng**; coder phải tính `len × copies`. **Nếu code đọc `count` ⇒ FAIL**
- [ ] `rate = 0` ⇒ **spawn cả loạt** (không phải mỗi frame) — theo `DESIGN_READINESS.md` §3 KHÉP 27/10
- [ ] Enemy có HP từ `datas/enemy_hp_by_id.json` theo id (150 cặp)
- [ ] Enemy chết ⇒ điểm/số vàng theo công thức decode (`BALANCE.md` §5.1 Coin1/Coin2) — **mức B**, có thể ghi `RUNTIME_UNVERIFIED`

### **S3 — 3 stage mở đầu + khuôn victory chung**

- 3 stage có **gate riêng**
- **khuôn victory chung** phủ cả 3 (đúng giả thuyết `spec §6`)

**Nghiệm thu:** clear 3 stage ⇒ victory frame xuất hiện; 3 stage không share frame riêng

### **S4 — Boss đầu tiên theo event có mốc**

- **≥1 boss**
- Event đọc từ `boss_anim_events.csv` — **KHÔNG SỬA file**
- Timeline theo mốc `time`

**Nghiệm thu:**
- Boss có ≥1 phase; pha đúng theo event có `time`
- Boss có HP theo bảng (`BALANCE.md` §2.2)
- Chết boss ⇒ chuyển state đúng (đang **mức C** — ghi rõ chỗ chưa đóng)

### **S5 — Save/load tối thiểu**

- Key **đúng tên spec**: `StarCount`, `StarStageMaster{stage}_{mode}`
- Mở lại game ⇒ dữ liệu còn

**Nghiệm thu:** set giá trị → quit → reopen → giá trị còn; key không lệch tên

---

## 5. Kỹ thuật — pin + khoá preset

### 5.1 Engine pin (STATIC_CONFIRMED)

- **Godot `4.7.2-stable`**, commit `ed1daf0bf001b61586d9930840f2f1394092c079`, publish 2026-08-18
- **Không dùng** bản khác — GameAnalytics/AdMob Poing cần ≥ 4.5 (G6), và spec đã pin 4.7.2

### 5.2 Khoá preset `Windows Desktop` (theo `GODOT_BUILD_PACKAGING_SPEC.md` §4.2)

| Khoá | Giá trị | Ghi chú |
|---|---|---|
| `binary_format/architecture` | `x86_64` | bản store đầu |
| `binary_format/embed_pck` | `true` | **1 file `.exe`** — dễ đóng MSIX sau này |
| `debug/export_console_wrapper` | **`0`** | ⚠ **phải ghi rõ** — default thật của Godot là **`1` (Debug Only)**, spec ghi `0` là **đề xuất** chứ không phải default. **Nếu không ghi = console mở** |
| `texture_format/s3tc_bptc` | `true` | |
| `codesign/enable` | `false` | bản local; lane MSIX **để sau** |
| `application/modify_resources` | `true` | |
| `application/product_name` | `<tên game>` | ⚠ **IP — xem §9.3** |
| `application/company_name` | `<USER-ONLY>` | pháp nhân — **user xác nhận** |
| `application/file_version` / `product_version` | từ `version.json` | MSIX `Version` là **4 thành phần** ⇒ chuẩn hoá (§5 spec) |
| `application/icon` | **TẠM** | ⚠ session art **chưa làm W0-listing** ⇒ icon chưa có. **Local build không cần icon**; MSIX **sau này cần** — ghi `TODO (Gate-5 art)` |

### 5.3 `version.json` — một nguồn

```json
{ "version_name": "0.1.0", "version_code": 1, "channel": "local" }
```
`version/code` trong preset **bằng** `version_code` (V3).

### 5.4 Command export

```
godot --headless --export-release "Windows Desktop" windwings_local.exe
```
Hoặc editor GUI: **Project → Export → Export Windows Desktop**.

**User chạy trên máy Windows của user** — sandbox director **không có** Windows SDK/Godot binary ⇒ **không tái lập build được** (V5 = `RUNTIME_UNVERIFIED` ở đây). **Người kiểm runtime là user.**

---

## 6. Bằng chứng yêu cầu mỗi vòng

Mỗi slice nộp kèm:

1. **PR comment** — 1 comment/PR (theo luật session), ghi rõ slice nào + file thay đổi
2. **Log export** — output của `--export-release` (hoặc screenshot editor export)
3. **Bằng chứng chạy** — user test trên máy Windows, chụp/ghi:
   - S1: 5 scene chuyển được
   - S2: số spawner/entry/instance **khớp số đo từ `waves.json`** (coder in số này ra log)
   - S4: boss pha theo event có mốc
   - S5: reopen ⇒ dữ liệu còn
4. **Claim gắn nguồn** — mọi con số trong báo cáo phải có file+dòng (STATIC) hoặc log (RUNTIME) — **V9**

---

## 7. Verifier

- **Vai:** `ef6b75ef` (theo `SESSION_PROMPTS.md` — **Godot-coder là vai MỚI, CLAIM khi user ra lệnh scaffold**)
- **Protocol:** `VERIFIER_PROTOCOL_GODOT_PORT.md` §3 — **chỉ phần local**:

| # | Kiểm | Áp dụng ở đây | Đạt khi |
|---|---|---|---|
| V1 | Vệ sinh repo | ✅ | 0 `.exe`/`.pck` trong repo; mọi file < 5 MB |
| V2 | Hợp đồng preset | ✅ | 100% khoá §5 khớp; không khoá lạ |
| V3 | Version nhất quán | ✅ | `version.json` ↔ preset ↔ `file_version` |
| V4 | Ràng buộc engine | ✅ | C1–C6 (AAB⇒gradle **không áp dụng** lane Windows) |
| V5 | Tái lập build | ⚠ **RUNTIME_UNVERIFIED** | sandbox **không có** Windows/Godot ⇒ **user kiểm trên máy** |
| V6 | Cổng kích thước | ⚠ | `.exe` ukuran — **không có ngưỡng store** (không phải APK/AAB) |
| V7 | Chữ ký | ⚠ `RUNTIME_UNVERIFIED` | bản local **không ký** (lane MSIX để sau) |
| V8 | Provenance asset | ✅ | **0 asset gốc**; mọi asset có nguồn khai báo |
| V9 | Kiểm claim | ✅ | 0 claim không nguồn |

**QUAN TRỌNG:** V8 là **cổng sống còn** — repo chứa **0 asset gốc** của GCenter. Nếu coder pull art từ APK gốc ⇒ **FAIL ngay**.

---

## 8. Rủi ro + việc phải chốt

### 8.1 ⚠ `rate = 0` — đã KHÉP (không phải rủi ro nữa)

`DESIGN_READINESS.md` §3 — **27/10 KHÉP = B (spawn cả loạt)**, **2.366/11.089 dòng (21,3 %)**.
**Coder phải implement "spawn cả loạt"**, không phải "mỗi frame". Nếu coder làm sai ⇒ mật độ địch sai ⇒ S2 FAIL.
Còn cần **asm** để lên mức **A** — nằm ở T5 của `HANDOFF_ANIM_RAW.md`, **không chặn** thiết kế.

### 8.2 ⚠ Art — **0 asset thật**

- Session art **chưa làm** W1–W3 (chỉ có planner, **plan-only**)
- Kế hoạch này dùng **placeholder** — chấp nhận được vì **mục tiêu là "chạy local để test"**
- **Không được** import art từ APK gốc (V8)

### 8.3 ⚠ Spine/animation — **chưa đóng**

- 4 rigs có attack animation, 22 không có, **791 clips unread**
- Godot **không có** official runtime Spine — licence/version **UNKNOWN**
- Kế hoạch này **không làm Spine** — boss dùng event timeline + placeholder
- Ghi rõ chỗ chưa đóng ở S4

### 8.4 ⚠ `count` field — **không dùng được**

`count = 0` ở **11.089/11.089** dòng. **Coder phải tính `len(enemies) × copies`.** Đây là **cổng S2**.

### 8.5 ⚠ Runtime verification — **user là người kiểm**

Sandbox director **không có** Windows/Godot binary ⇒ **không tái lập build**.
**User chạy `.exe` trên máy Windows và báo kết quả.** Kế hoạch này **không thể tự verify** phần "chạy được".

### 8.6 ⚠ Engine pin vs plugin

GameAnalytics (GDExtension) + AdMob Poing cần **≥ 4.5** ⇒ pin **4.7.2-stable** (G6).
**Kế hoạch này không tích hợp analytics/ads** — chỉ pin engine.

---

## 9. Kế hoạch phụ — reserve app name + Identity (mục 3, **làm**)

**Không chặn S0–S5** — làm **song song** hoặc **trước khi bắt đầu lane MSIX** (mục 2).

### 9.1 Reserve app name (Partner Center)

1. Sign in Partner Center (user đã có account — mục 6)
2. **Reserve name** cho game Windows
3. Ghi lại `Identity@Name` + `Publisher` (phải **khớp** signing cert CN — nhưng MSIX ký sau này, MS re-sign)
4. Đợi **tên được giữ** trong Partner Center

### 9.2 `Identity@Name` / `@Publisher` / Version

- `Identity@Name` = tên reserved (hoặc tên game — **IP xem §9.3**)
- `Identity@Publisher` = `CN=<publisher>` — **phải khớp** Partner Center publisher
- `Identity@Version` = **4 thành phần**, thành phần 4 = **0**
- `runFullTrust` capability (game là Win32 desktop)
- `packagedClassiveApp` + `mediumIL`
- `TargetDeviceFamily@MinVersion` = **UNKNOWN** — cần chốt (Win10 17763 hay khác)

### 9.3 ⚠ Director cần lưu ý về IP (mục 8)

User chốt: *"MS sẽ cấp quyền đó riêng khi release"*.

**MS cấp cái này:** code signing (re-sign MSIX), hosting, Store distribution, app-name reservation, IARC rating, Store commerce. **MS không cấp** quyền dùng **tên/art/nội dung của GCenter**.

**Nhưng vì kế hoạch này là reimplementation original:**
- **Cơ chế** (bay/bắn/wave/boss/drop) — **không** chịu copyright ⇒ dùng được
- **Art/audio/font gốc** — **KHÔNG** được (V8 = 0 asset gốc)
- **Tên "WindWings"** — **cần clearance**. Đây là **phần còn lại của Gate-4**.

**Giải pháp đơn giản nhất:** dùng **tên mới** (original) ⇒ câu hỏi IP **chỉ còn art/audio** (vốn đã bị chặn vì V8). Nếu giữ tên "WindWings" ⇒ cần **lấy phép từ GCenter** hoặc **dự đoán rủi ro pháp lý**.

**⇒ Việc phải chốt (USER-ONLY):** giữ tên `WindWings` hay đổi tên mới? **Không giải bằng kỹ thuật.**

---

## 10. Định dạng báo cáo cuối (kế hoạch này xong)

```
## Báo cáo — vertical slice Windows LOCAL (S0–S5)
Engine: Godot 4.7.2-stable (ed1daf0b)
Preset: Windows Desktop (khoá §5) — coder/verifier đã so

[S0] project.godot OK · export_presets.cfg OK · .gitignore OK
[S1] 5 scene: Main→Home→Maps→Battle→Endgame ✅ (bằng chứng: log/screenshot)
[S2] spawner=N (file: M) · entry=N (file: M) · instance=N (file: M) — KHỚP ✅
     field `count` KHÔNG dùng ✅ · rate=0 = spawn cả loạt ✅
[S3] 3 stage gate riêng + victory chung ✅
[S4] boss ≥1, event theo boss_anim_events.csv (không sửa) ✅ — ghi rõ chỗ mức C
[S5] StarCount, StarStageMaster* — reopen còn dữ liệu ✅

V1..V9: [từ verifier]
Bản local: .exe = <byte> — user test trên Windows: <kết quả>
TODO chuyển lane: MSIX + Windows.Services.Store (mục 2 — để sau)
```

---

## 11. Xong khi nào

- [ ] S0–S5 **mỗi slice có nghiệm thu §4** + bằng chứng §6
- [ ] **V1–V4, V8, V9** xanh (V5/V7 = `RUNTIME_UNVERIFIED` có lý do, không im lặng)
- [ ] **V8 = 0 asset gốc** — cổng sống còn
- [ ] **User chạy `.exe` trên Windows và báo "chạy được"** — **không ai khác làm được việc này**
- [ ] **XÓA khỏi lane:** MSIX, Store IAP, CI MSIX, IARC, privacy policy, art thật, Android export, multi-wave 282

---

## 12. Liên kết

| Vai | Nhánh | Trạng thái |
|---|---|---|
| Godot-coder | **MỚI** — CLAIM khi user ra lệnh scaffold | **MỞ** |
| `ef6b75ef` | build/packaging spec + verifier | giữ |
| `20330d0e` | director / spec / tích hợp | giữ |
| `1b836828` | art planner | giữ (Gate-5) |
| Art-designer `5438fec9` / `-B` | **MỞ** | Gate-5 cần art thật |

**Branch session:** `arena/e235c1c0-windwings-space-shooter-game-p`
**Nền:** tip `f9566558` + corrections lần 160 (commit `4447746`)
