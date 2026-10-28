# VERIFY [Godot-coder] — `arena/ba257b36` @ `63361095371e9bd0aa86f32910b3aa89d63ad7e8` — CI: **không có run nào**

**Vai:** build-spec/verifier (`ef6b75ef`) · **Người viết ≠ người kiểm** · tôi **không sửa** file nào của
coder. Đây là báo cáo theo `VERIFIER_PROTOCOL_GODOT_PORT.md`, thực hiện đúng hạn chót director
`[DIRECTOR · lần 150]` (`6446085883`): *verification report M1–M4 của `game/` @`6336109`*.

**Phạm vi:** tầng **code + dữ liệu** của `game/` (M1–M4). **Không** phải bàn giao export: nhánh coder
không có `export_presets.cfg`, `version.json`, artifact build, log export, và **0 CI run** — nên V2/V3/V5/
V6/V7 ở tầng đóng gói là *chưa kiểm được*, không phải "đạt".

**Dụng cụ:** `gdtoolkit 4.5.0` (parser GDScript của Godot 4) · Python 3.11 · script + receipt:
`reverse-engineering/raw/verify-ef6b75ef-m1m4/verify_m1m4.py` (`94f77e9a…`) và `verify_m1m4.json`
(`7d94640b…`). Không có binary Godot trong sandbox.

## 1. Đầu vào bắt buộc (protocol §2)

| # | Mục | Trạng thái |
|---|---|---|
| 1 | branch + headSha | ✅ `arena/ba257b36…` @ `63361095371e9bd0aa86f32910b3aa89d63ad7e8` |
| 2 | CI run theo headSha | ❌ **0 run** cho nhánh này (API `actions/runs?branch=…` rỗng; 100 run gần nhất không có `ba257b36`) |
| 3 | `export_presets.cfg` + `version.json` | ❌ không có |
| 4 | `project.godot` | ✅ có (sha256 `4284f854…`) |
| 5 | danh sách asset + sha + nguồn | ✅ suy ra được: **38 file, 0 media**, toàn bộ vẽ bằng primitive |
| 6 | plugin ngoài engine | ✅ không có (0 `.gdap`, 0 `.aar`) |
| 7 | artifact build | ❌ không có |
| 8 | log export | ❌ không có |

## 2. Bộ kiểm V1–V9

| # | Kết quả | Bằng chứng đo được |
|---|---|---|
| V1 | **PASS** | 38 file, tổng 134.949 B, file lớn nhất 20.753 B; 0 `*.keystore/.jks/.pfx/.p12/.exe/.apk/.aab/.so/.dll`; 0 file ≥ 5 MB |
| V2 | **N/A** | không có preset để diff hợp đồng (`GODOT_EXPORT_PRESET_CONTRACT.json`) |
| V3 | **N/A** | không có `version.json`/`version/code` |
| V4 | **N/A (một phần)** | `project.godot:22-23` renderer `gl_compatibility` (không đụng ràng buộc Vulkan≥29); chưa có preset ⇒ không đọc được `min_sdk` |
| V5 | **UNVERIFIABLE** | không có Godot 4.7.2-stable trong sandbox ⇒ không import/launch |
| V6 | **N/A** | không có artifact |
| V7 | **N/A** | không có APK/AAB, không có `apksigner` |
| V8 | **PASS** | 0 file media (`.png/.wav/.ttf/…` = 0); 3 file dữ liệu **byte-identical** với `datas/` (bảng §3) |
| V9 | **PASS (có 2 ghi chú)** | 12/12 claim số học kiểm lại đúng; 10 file dữ liệu thiếu `source_sha256` (F3) và 5 file thiếu nhãn `evidence` (F4) |

## 3. Kiểm sâu thêm (ngoài V1–V9)

| Kiểm | Kết quả | Số đo |
|---|---|---|
| Parse GDScript | **PASS** | **15/15** file parse bằng parser Godot 4 thật (gdtoolkit 4.5.0); 0 lỗi |
| Scene/resource | **PASS** | 6 `.tscn`, main scene `scenes/main.tscn` tồn tại; **0** đường dẫn `res://` gãy; 15 `class_name`, 0 trùng |
| Mạng/bí mật | **PASS** | 21 token nguy hiểm (HTTPRequest, OS.execute, JavaScriptBridge, keystore, secret…) × 15 file = 0 hit |
| Fail-closed monetization | **PASS** | `monetization_provider.gd:20` `is_available()` trả `false`; 3 stub `extends MonetizationProvider`; `monetization_config.json:4` `real_plugins_enabled: false`; `economy_panel.gd:557-563` chỉ ghi label, **không** cộng ví/cấp quyền lợi |
| Số học Wave_0000 | **PASS** | 42 row · `sum(copies)`=150 · `copies×len(enemies)`=883 · 15 prefab id; **deep-equal** với `datas/waves.json` (sha `dde00761…`) |
| HP/movement | **PASS** | HP map 150 entry; 15/15 prefab có HP **và** movement row; `_validate_wave_data` (`main.gd:331`) chặn khởi động nếu thiếu |
| Coin manifest | **PASS** | 49/49 đường dẫn khớp **đúng** `Item_Movement.csv` của nhánh spec (sha `01aca68a…`), id `{70011,70012}` |
| Gun alternatives | **PASS** | 6 prefab; đối chiếu chữ ký trường: `30014` 2 row→**1** biến thể (2 row trùng khít), `30018` 4 row→**2**, `31002/31003/31007/31008` 2→2; 0 lệch giá trị |
| `training_gun` | **PASS** | khớp row `CD-31002/Enemy_Ingame` bltId 80021: 400.0 dmg · speed 4.0 · life 8.0 · timeStart 1.0 |
| PvP arrays | **PASS (thiếu pin)** | 6/6 mảng bằng đúng `datas/l2_535b0541_pvp_hunter_arrays.json.gz` @ `8777bfa3e` (sha `034bb93b…`) — nhưng file **không** ghi `source_sha256` |
| `player_start_stats` | **PASS** | 6/6 mảng decode **byte-exact** từ blob il2cpp (`ia-resolved.json`): addr `0x14e5b3c` (24 int), `0x14e5e8c`, `0x14e5eb4`, `0x14e5edc` (24 float), `0x14e608c`, `0x14e6204` (3 float); 0 mảng tự đặt |
| IAP catalog | **PASS** | `count`=170 = 71 consumable + 99 non-consumable, 170 id duy nhất, **byte-identical** `datas/iap_products.json` |
| Shop contract | **PASS** | 3 band × **5 slot** (`player/drone/resource`, base 100/200/300); popup: start 1, step 1, max rule `available_stock - 1`, `MaxStockCount` để `UNKNOWN` |

## 4. Phát hiện (theo mức ưu tiên)

- **F1 — Không có CI (chặn bằng chứng).** Nhánh `arena/ba257b36` có **0 run** trong Actions. Protocol §2
  mục 2 yêu cầu CI theo headSha ⇒ mọi tuyên bố "đã chạy" hiện chỉ dựa trên máy coder.
  *Đề nghị:* push 1 commit chạm đường dẫn mà workflow thật sự theo dõi, hoặc nêu rõ trong handoff là
  "chưa có CI".
- **F2 — Thiếu đầu vào Gate-4.** Không có `export_presets.cfg`, `version.json`, artifact, log ⇒ V2/V3/V5/
  V6/V7 không thể chạy. `GATE4_BUILD_CHECKLIST.md` P0.6 (`version_code`) cũng chưa thoả.
- **F3 — 10 file dữ liệu thiếu `source_sha256`** (`drop_policy`, `enemy_guns_wave_0000`,
  `enemy_hp_by_id`, `enemy_movement_wave_0000`, `iap_products`, `items`, `player_baseline`,
  `player_start_stats`, `pvp_reward_arrays`, `training_gun`). Với `iap_products`/`items`/`enemy_hp_by_id`
  điều này **không** gây hại vì đã byte-identical với `datas/`; riêng `pvp_reward_arrays` cần thêm
  `source_sha256: 034bb93b…` vì nguồn nằm ở nhánh spec (`20330d0e`).
- **F4 — 5 file thiếu nhãn `evidence`** (`enemy_guns_wave_0000`, `enemy_hp_by_id`, `iap_products`, `items`,
  `monetization_config`). README có gắn nhãn trong văn xuôi, nhưng máy đọc không thấy. *Đề nghị:* thêm
  `"evidence": "STATIC_CONFIRMED"` (hoặc `UNKNOWN` cho phần chưa decode).
- **F5 — `project.godot:9` khai `features = ("4.3", …)`** trong khi spec pin engine **4.7.2-stable**
  (`ed1daf0b…`). Mở bằng 4.7.2 sẽ đi qua đường nâng cấp project ⇒ V3/V5 cần chốt lại sau khi save bằng
  đúng engine đã pin.
- **F6 — Viewport `720×1496` chưa gắn nhãn và không trùng mẫu thiết bị nào đã mô hình hoá.** Công thức
  camera gốc (`datas/camera_scaler_contract.json`): `max((Screen.height/Screen.width)*5.4, 9.6)`; các mẫu
  đã mô hình hoá là 1080×1920, 1080×2400, 1920×1080, 720×1280 — tỉ lệ 720×1496 = 2,078 vượt mọi mẫu
  9:16 (1,778). Đây là **lựa chọn thiết kế**, không phải lỗi, nhưng phải ghi `INFERRED` + lý do.
- **F7 — `enemy_guns_wave_0000.json` dedup row trùng khít mà không ghi quy tắc** (30014: 2→1, 30018:
  4→2). Tôi đã tự kiểm là dedup **đúng** (cùng chữ ký 11 trường), nhưng cần 1 dòng `note` để lần kiểm sau
  không phải suy lại.

## 5. Verdict nội bộ

**APPROVE-BOUNDED** — tầng code + dữ liệu của M1–M4 đạt: parse 15/15, 0 asset gốc, 0 đường dẫn gãy,
0 mạng/bí mật, fail-closed monetization đúng như README khai, và **mọi con số dẫn xuất từ APK đều tái tạo
được** (wave/HP/movement/coin/gun/IAP/PvP/player-stats). Không đạt ở tầng **bàn giao export** (F1, F2).

Không phải "APPROVE" đầy đủ vì: không CI, không artifact, và 3 chỗ thiếu pin/nhãn (F3, F4, F7).

## 6. Những gì báo cáo này **không** kiểm

- Godot import/launch, cảm giác chơi, hiệu năng trên Fire tablet/Windows ARM (không có engine/thiết bị).
- Export/đóng gói/chữ ký (F2) — thuộc Gate-4, USER-ONLY phần SDK/keystore.
- Chất lượng art (thuộc art-designer/art-curator), quyết định Gate (thuộc reviewer `8141386a`).
- Nhánh `ba257b36` có thể đã đổi sau commit này — báo cáo chỉ đúng cho `63361095371e9b…`.

## 7. Tái lập

```bash
git archive 63361095371e9bd0aa86f32910b3aa89d63ad7e8 | tar -x -C /tmp/verify-m1m4
git show origin/peer-20330d0e:reverse-engineering/scriptableobjects/Item_Movement.csv > /tmp/peercsv/Item_Movement.csv
git show origin/peer-20330d0e:reverse-engineering/scriptableobjects/Enemy_Movement.csv > /tmp/peercsv/Enemy_Movement.csv
git show origin/peer-20330d0e:reverse-engineering/scriptableobjects/Gun_Attack.csv > /tmp/peercsv/Gun_Attack.csv
PYTHONPATH=/tmp/gdt python3 reverse-engineering/raw/verify-ef6b75ef-m1m4/verify_m1m4.py \
  --target /tmp/verify-m1m4 --canonical . --peer-csv-dir /tmp/peercsv --out /tmp/verify_m1m4.json
```

Kỳ vọng `summary`: 10 mục `PASS`, `engine_boundaries = UNVERIFIABLE`.
