# Spec local — snapshot cũ, không phải điểm bắt đầu triển khai

Đọc **[bàn giao AI viết game mới](../START_HERE_NEW_GAME.md)** trước.

Bốn spec local GAMEPLAY/UI/ASSETS/BALANCE không tương đương bộ spec mới trên
nhánh `arena/20330d0e-windwings-space-shooter-game-p`. Nhánh đó đã được đọc ở
`cf27b97553ef25107b45b039f316d9ca7850a885`; xem
[review cập nhật](../HANDOFF_REVIEW_cf27b9755.md) để biết phần đã sửa và phần còn lỗi.

Không dùng spec tóm tắt thay raw APK, không import/merge nguyên nhánh spec.
Không tự chốt engine/platform, schema save, art direction hay hằng số chưa có
bằng chứng. Phân biệt APK fact, derived data, quyết định game mới và unknown.

## Branch-owned verification-support index (8141386a)

provenance: `arena/8141386a-windwings-space-shooter-game-p`. Added spec files are
verification support pinned in the import receipt, not an APK re-export. Existing
GAMEPLAY/UI/ASSETS/BALANCE summaries above are retained, not replaced.

`verify-claims.py` uses an explicitly printed historical support view; only
APKD1 / AI1 / RD1 check the current own worktree. A scoped green result does
not assert that the current peer runtime-probe/raw sources passed historical claims.
Use `--unscoped-legacy` to see those inherited incompatibilities.

**Kiểm tự động (`RD1`):** **41 dòng · 0 lệch**

| Tài liệu support | Kích thước đo từ file hiện tại |
|---|---|
| `AI_FEASIBILITY.md` | 653 dòng · 32 bảng |
| `ANIMATION.md` | 433 dòng · 20 bảng |
| `ANIMATION_GAPS.md` | 371 dòng · 12 bảng |
| `ANIMATION_SCRIPT.md` | 521 dòng · 25 bảng |
| `ART_STUDY.md` | 140 dòng · 3 bảng |
| `ASM_INTEGRITY.md` | 293 dòng · 3 bảng |
| `ASSETS.md` | 409 dòng · 20 bảng |
| `ASSET_TRIAGE.md` | 519 dòng · 23 bảng |
| `BALANCE.md` | 662 dòng · 29 bảng |
| `BOSSES.md` | 586 dòng · 22 bảng |
| `BOSS_ANIM_TIMELINE.md` | 186 dòng · 8 bảng |
| `COMBAT.md` | 505 dòng · 20 bảng |
| `COVERAGE_AUDIT.md` | 139 dòng · 5 bảng |
| `DATA_INTEGRITY.md` | 136 dòng · 7 bảng |
| `DATA_SYNC.md` | 3853 dòng · 130 bảng |
| `DESIGN_QUESTIONS.md` | 175 dòng · 8 bảng |
| `DESIGN_READINESS.md` | 269 dòng · 12 bảng |
| `DIFFICULTY_MODES.md` | 479 dòng · 18 bảng |
| `DONE.md` | 1058 dòng · 21 bảng |
| `ECONOMY.md` | 394 dòng · 18 bảng |
| `ENCOUNTERS.md` | 717 dòng · 32 bảng |
| `ENEMY_BEHAVIOUR.md` | 248 dòng · 12 bảng |
| `ENEMY_HP_RUNTIME.md` | 244 dòng · 9 bảng |
| `EXTERNAL_REFS.md` | 169 dòng · 10 bảng |
| `GAMEPLAY.md` | 594 dòng · 26 bảng |
| `HANDOFF_ANIM_RAW.md` | 375 dòng · 5 bảng |
| `MISSING_FOR_NEW_GAME.md` | 339 dòng · 9 bảng |
| `MISSIONS_STARS.md` | 380 dòng · 11 bảng |
| `OPEN_ISSUES.md` | 433 dòng · 13 bảng |
| `PARALLEL_TASKS.md` | 292 dòng · 8 bảng |
| `PIPELINE_AUDIT.md` | 424 dòng · 26 bảng |
| `RAW_AUDIT.md` | 81 dòng · 3 bảng |
| `SCRIPTS.md` | 346 dòng · 15 bảng |
| `SYSTEM_MANIFEST.md` | 36 dòng · 1 bảng |
| `TUNING_KNOBS.md` | 312 dòng · 17 bảng |
| `UI.md` | 461 dòng · 17 bảng |
| `UNITY_RULES.md` | 387 dòng · 18 bảng |
| `VERIFY_ROUND1.md` | 252 dòng · 12 bảng |
| `VERIFY_ROUND2.md` | 220 dòng · 8 bảng |
| `VISUAL_DESIGN.md` | 130 dòng · 5 bảng |
| `WHERE_TO_LOOK.md` | 226 dòng · 9 bảng |
