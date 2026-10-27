# VERIFY lại sau fix — `arena/ba257b36` @ `3f69db320` ("address independent verification findings")

**Vai:** build-spec/verifier (`ef6b75ef`). **Người viết ≠ người kiểm**; tôi không sửa file nào của coder.
**Trước đó:** báo cáo vòng 1 `docs/rollout/VERIFY_M1_M4_BA257B36.md` (`34b16798…`) @ `6336109`, phát hiện F1–F7.
**Lần này:** kiểm commit fix `3f69db320`, đóng/mở từng phát hiện + 4 kiểm mới (A/B/C/E) + **mutation test** cổng CI mới.

**Dụng cụ:** `gdtoolkit 4.5.0` (parser + linter GDScript Godot 4), Python 3.11, `git` đọc blob theo commit.
Receipts: `reverse-engineering/raw/verify-ef6b75ef-m1m4/verify_REFIX.py` (`1ec556ea…`),
`verify_3f69db3.json` (`f2117e00…`), `verify_m1m4.py` v2 (`aa51f059…`), `verify_m1m4_at_head.json` (`85828e63…`).
**Không có binary Godot** trong sandbox ⇒ mọi kết luận runtime vẫn `RUNTIME_UNVERIFIED`.

## 1. Đóng/mở từng phát hiện vòng 1

| # | Phát hiện vòng 1 | Trạng thái giờ | Bằng chứng đo được |
|---|---|---|---|
| F1 | nhánh coder **0 CI run** | **ĐÓNG (phạm vi static)** | run **40537106073** "Godot project static checks" `success` đúng head `3f69db320`; workflow 93 dòng, `permissions: contents: read` |
| F2 | thiếu `export_presets.cfg`/`version.json`/artifact/log | **CÒN MỞ** (ngoài phạm vi M1–M4) | vẫn không có file nào trong `game/`; Gate-4 P0.6 chưa đạt |
| F3 | 10 file dữ liệu thiếu `source_sha256` | **ĐÓNG** | 12/12 pin giải được **khớp tuyệt đối** với blob tại commit được dẫn (`8777bfa3e`), 0 pin sai, 0 pin cũ |
| F4 | 5 file thiếu nhãn `evidence` | **ĐÓNG 14/15** | 14 file có nhãn hợp lệ; còn `player_start_stats.json` (dùng `status: DECODED_INITIALIZEARRAY_HEX_TYPED_NOT_RUNTIME`) |
| F5 | `features` khai `4.3` vs engine pin 4.7.2 | **ĐÓNG** | `project.godot:9` `PackedStringArray("4.7.2", "GL Compatibility")` |
| F6 | viewport 720×1496 chưa gắn nhãn | **ĐÓNG** | chú thích `; INFERRED:` ngay trên khoá viewport + 1 dòng trong README §Evidence |
| F7 | dedup gun không ghi quy tắc | **ĐÓNG** | `dedup_rule` 11 trường + số cụ thể `30014 2→1`, `30018 4→2` + README mô tả đúng |

## 2. Kiểm mới (A/B/C/E)

### A. Bất biến payload — **PASS**
So 15 file JSON giữa `6336109` và `3f69db320` sau khi bỏ khoá metadata (`source`, `source_sha256`,
`evidence`, `note`, `dedup_rule`, `limitations`): **0 file đổi payload**. Tức commit fix **chỉ thêm
provenance**, không chỉnh một con số nào đã kiểm ở vòng 1.

### B. Độ phủ nhãn — **FAIL (1 file)**
15 file dữ liệu: **14** có `evidence` thuộc đúng 6 nhãn cho phép; `player_start_stats.json` không có.
Đề nghị: thêm `"evidence": "STATIC_CONFIRMED"` (blob il2cpp đã pin `2583a4c4…`) — hoặc khai rõ trường
`status` thay thế nhãn và cập nhật workflow.

### C. Tính toàn vẹn của pin — **PASS (12/12)**
Mỗi `source_sha256` được đối chiếu với **bytes thật** của đường dẫn tại commit ghi trong `source`
(`git show <commit>:<path>` → sha256):

| file | pin | nguồn | khớp |
|---|---|---|---|
| `drop_policy.json` | `1db2e6a4…` | `docs/spec/GAMEPLAY.md @ 8777bfa3e` | ✅ |
| `player_baseline.json` | `1b70435d…` | `docs/spec/BALANCE.md @ 8777bfa3e` | ✅ |
| `player_start_stats.json` | `2583a4c4…` | `reverse-engineering/il2cpp/ia-resolved.json @ 8777bfa3e` | ✅ |
| `pvp_reward_arrays.json` | `034bb93b…` | `datas/l2_535b0541_pvp_hunter_arrays.json.gz @ 8777bfa3e` | ✅ |
| `enemy_hp_by_id.json` | `e790bc71…` | `datas/enemy_hp_by_id.json @ 8777bfa3e` | ✅ |
| `iap_products.json` | `d0521bdc…` | `datas/iap_products.json @ 8777bfa3e` | ✅ |
| `items.json` | `c89d07bb…` | `datas/items.json @ 8777bfa3e` | ✅ |
| `wave_0000.json` | `dde00761…` | `datas/waves.json @ 8777bfa3e` | ✅ |
| `enemy_guns_wave_0000.json` | `cc9f6c8a…` | `Gun_Attack.csv @ 8777bfa3e` | ✅ |
| `training_gun.json` | `cc9f6c8a…` | `Gun_Attack.csv @ 8777bfa3e` | ✅ |
| `enemy_movement_wave_0000.json` | `3ac3ccf4…` | `Enemy_Movement.csv @ 8777bfa3e` | ✅ |
| `wave_0000_coin_manifest.json` | `01aca68a…` | `Item_Movement.csv @ 8777bfa3e` | ✅ |

**Không cũ:** 11 nguồn trên (trừ `l2_…gz` kiểm riêng) có bytes **y hệt** ở peer tip hiện tại `4686d733b`
⇒ pin trỏ `8777bfa3e` vẫn đúng dữ liệu đang dùng, không phải ảnh cũ.

### E. Audit workflow thêm bởi nhánh — **REVIEW (xem F8)**

## 3. Mutation test cổng CI mới — cổng **có răng**

Tôi trích nguyên khối python trong `godot-project-checks.yml` và chạy 3 lần:

| Biến thể | Kết quả |
|---|---|
| cây gốc `3f69db320` | `PASS: 15 JSON files; 10 pinned sources; 15 resource links; main=scenes/main.tscn` (exit 0) |
| xoá `game/scenes/pickup.tscn` | `AssertionError: broken resource references: game/scripts/main.gd: res://scenes/pickup.tscn` (exit 1) |
| bỏ `source_sha256` của `enemy_hp_by_id.json` | `AssertionError: enemy_hp_by_id.json: missing/invalid source_sha256` (exit 1) |

⇒ Cổng không phải hình thức: nó chặn được cả link gãy lẫn pin bị xoá.

**Nhưng** còn một lỗ: workflow chỉ kiểm **hình dạng** hash (`^[0-9a-f]{64}$`) + 1 hash hard-code
(`034bb93b…`), **không** so hash với bytes nguồn. Hôm nay 12/12 pin đúng là nhờ tôi kiểm bằng `git show`;
nếu coder sửa 1 chữ số trong dữ liệu mà quên đổi pin, CI vẫn xanh. Đề nghị nâng cấp: thêm bước resolve
pin (như `verify_REFIX.py` mục C) vào `godot-project-checks.yml`.

## 4. Phát hiện mới

- **F8 — 4 workflow không liên quan Godot bị thêm vào nhánh (1.359 dòng).**
  `ramus-probe.yml` 970 dòng, `bridge-build.yml` 134, `docs-verify.yml` 113, `recover-player-loadout.yml` 49.
  Cả 4 **không tồn tại** trên `main` (merge-base `8b3689dcb`) lẫn trên nhánh spec; chúng thuộc lane
  runtime-probe/docs-verify khác.
  - 3 file xin quyền ghi: `pull-requests: write` (bridge-build), `pull-requests: write` + `issues: write`
    (docs-verify), `contents: write` (recover-player-loadout).
  - 4/4 trỏ tới đường dẫn **không có** trên nhánh: `runtime-probe/RamusBridge.cs`, `tools/verify-claims.py`,
    `tools/raw-audit.py`, `tools/verify/*`, `tools/apk-probe/player_loadout_native.py`,
    `runtime-probe/{README.md,app.apk,app.xapk}`, `tools/{APKEditor.jar,uber-apk-signer.jar}`.
  - `recover-player-loadout.yml` có guard cứng `test "$GITHUB_REF_NAME" = 'arena/ef6b75ef-…'` ⇒ chạy trên
    nhánh coder **luôn fail**, và nó ghi thẳng vào **nhánh của tôi**.
  *Đề nghị:* gỡ 4 file khỏi nhánh coder (giữ `godot-project-checks.yml`); nếu muốn giữ, mở PR riêng kèm
  các file đích và giải thích quyền ghi.
- **F9 — `player_start_stats.json` thiếu nhãn `evidence`** (mục B). Sửa 1 dòng.
- **F10 — CI kiểm hình dạng hash, không kiểm giá trị** (mục 3). Đề nghị thêm bước resolve pin.

## 5. Verdict nội bộ

**APPROVE-BOUNDED (giữ nguyên mức, lý do đã khác).**
- Tầng code + dữ liệu: **11/12 kiểm PASS** ở head mới (parse 15/15 + gdilnt **0 phát hiện**, 0 media,
  0 mạng/bí mật, fail-closed đúng, 42/150/883, coin 49/49, gun 6/6, PvP 6/6, il2cpp 6/6 byte-exact,
  IAP 170, shop 3×5, **payload bất biến**, **pin 12/12**).
- Lý do vẫn bounded: `engine_boundaries` **UNVERIFIABLE** (không Godot) và F2 (chưa có tầng export).
- **Không** nâng lên APPROVE vì còn F8 (workflow lạ + quyền ghi) và F9/F10.

## 6. Không kiểm
Godot import/launch/export, chữ ký, hiệu năng thiết bị, cảm giác chơi, chất lượng art, quyết định Gate
(thuộc `8141386a`). Báo cáo chỉ đúng cho `3f69db320`; coder push tiếp thì phải chạy lại.

## 7. Tái lập

```bash
git fetch origin arena/ba257b36-windwings-space-shooter-game-p
git archive 3f69db320 | tar -x -C /tmp/newtree
git archive 63361095371e9bd0aa86f32910b3aa89d63ad7e8 game | tar -x -C /tmp/ba_old
PYTHONPATH=/tmp/gdt python3 reverse-engineering/raw/verify-ef6b75ef-m1m4/verify_REFIX.py \
  --new-tree /tmp/newtree --old-tree /tmp/ba_old --canonical . --peer-csv-dir /tmp/peercsv \
  --peer-tip 4686d733b --head 3f69db320 --out /tmp/verify_3f69db3.json
```

Kỳ vọng `summary`: 13 `PASS`, `B_evidence_coverage = FAIL` (1 file), `E_workflow_audit = REVIEW`,
`engine_boundaries = UNVERIFIABLE`.
