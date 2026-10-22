# Chia việc phân tích WindWings — 2 phần

Repo: `Nthanhbadboy/WindWings-Space-Shooter-game-play`

Chia làm **2 phần độc lập**, không ghi trùng file, merge song song được:

| Phần | Ai làm | Sản phẩm | Đụng vào |
|---|---|---|---|
| **1 — Spec & thiết kế** | AI khác (chỉ đọc + viết docs) | `docs/spec/**` | chỉ Markdown/CSV |
| **2 — Data & pipeline** | phiên làm việc này | `datas/`, `i18n/`, `tools/`, `docs/apk-analysis/` | code + workflow + git |

Phần 2 phụ thuộc ngược vào phần 1 ở chỗ: bảng pathID → tên sprite do phần 2 sinh ra sẽ được
dùng lại để làm `datas/*.json`. Phần 1 **không** cần chờ phần 2, vì chỉ mô tả bằng id/pathID.

---

## Nguồn dữ liệu có sẵn (cả 2 phần đều đọc từ đây)

| File | Nội dung |
|---|---|
| `docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md` | Báo cáo tổng 12 mục, 451 dòng — đọc trước |
| `docs/apk-analysis/06-gameplay-systems.md` | 6.090 dòng — field/method class gameplay |
| `docs/apk-analysis/07-enums.md` | 5.230 dòng — 255 enum |
| `docs/apk-analysis/08-ui-map.md` | 15.296 dòng — 125 class Board/Popup/Tab |
| `docs/apk-analysis/09-numbers-and-formulas.md` | 78 class config |
| `docs/apk-analysis/10-scriptableobjects.md` | 149 instance bóc bằng typetree |
| `docs/apk-analysis/11-typetree-probe.md` | so sánh backend typetree |
| `docs/apk-analysis/12-localization.csv` | 1.416 key × 19 ngôn ngữ |
| `docs/apk-analysis/13-iap-products.csv` | 170 product ID |
| `docs/apk-analysis/14-{ships,drones,bosses,items}.csv` | roster |
| `docs/apk-analysis/15-enemy-hp.csv` | 981 Enemy_Datas: HP + prefab path |
| `docs/apk-analysis/class-inventory.csv` | ~1.000 class MonoBehaviour |
| `docs/apk-analysis/04-asset-manifest.csv` | 2.838 asset export (chưa có pathID) |
| `reverse-engineering/scriptableobjects/` | CSV thô từng class |
| `reverse-engineering/il2cpp/` | dump.cs.gz, class-index, stringliteral |
| `reverse-engineering/textassets/` | 26 Spine skeleton + atlas, charset |

APK gốc: draft release `windwings-apk-1.3.118` (asset `windwings.xapk` 142 MB).
Artifact `windwings-analysis` (tab Actions) giữ sprite/audio export.

---

## PHẦN 1 — AI khác: Spec & thiết kế

**Ghi vào duy nhất:** `docs/spec/`
**Đọc:** các file trong bảng trên
**Không** sửa `docs/apk-analysis/**`, `tools/**`, `.github/**`, `reverse-engineering/**`, `datas/**`.
**Không** commit ảnh/audio/APK. **Không** viết code (trừ script đọc CSV nếu thật cần, để ở `/tmp`).
**Không** push `main`, không đụng branch `arena/*` → mở **PR riêng**.

Sản phẩm gồm 4 nhóm:

### 1.1 `docs/spec/GAMEPLAY.md` — GDD
- One-pager: thể loại, vòng lặp 30 giây / 10 phút / 1 tuần, nền tảng.
- Core loop: di chuyển, auto-fire, wave, drop item, endgame, reborn.
- 7 `PlayMode` (`Normal, FightBoss, Challange, Survival, TryPlayer, Arena, PVP`) + 3 `PVPMode`
  (`Tournament, Solo, Hunter`): mục đích, thưởng, điều kiện mở.
- Progression: tàu → sao → device → drone → tech → talent → chapter → arena → battle pass.
- Economy: coin / gem / energy / star — bảng **source vs sink**, tốc độ tiến trình suy ra.
- Meta: battle pass, shop, quest, arena season, event.
- 20 boss chính + 2 mini-boss + 16 MB variant: phase, attack class, HP (dùng `15-enemy-hp.csv`).
- Build order đề xuất + ước lượng người-tuần.

### 1.2 `docs/spec/UI.md` + `docs/spec/screens.csv` — UI spec
- Mermaid screen graph: Home → Play / Shop / Upgrades / Drones / Devices / Cards / Quest /
  BattlePass / Arena / PvP / Settings (49 board + 63 popup + 8 tab).
- `screens.csv`: `class, board_id, mo_tu_dau, popup_con, data_can_load`.
- 63 popup phân loại: confirm / reward / offer / error; điều kiện bật.
- `LoadBoardMode {Single, Additive, PopUp}`, back stack, board destroy vs hide, `UIManager`.
- Wireframe note: bố cục vùng (header/tab/list/footer) **suy ra từ field**, không copy pixel.

### 1.3 `docs/spec/ASSETS.md` — brief cho art mới
- Art direction **đề xuất khác WindWings**: palette, silhouette tàu, tỉ lệ, mood.
- `sprite-list.csv`: nhóm UI/Enemy/Boss/Bullet/Drone/FX theo `04-asset-manifest.csv`,
  kích thước thật, đề xuất size mới, 9-slice hay không.
- Atlas plan: gom theo màn (thay `sactx-*`), budget VRAM.
- Spine spec: 26 skeleton — số bone, slot, skin, danh sách animation, `defaultMix` → spec rig lại.
- Audio: 69 clip phân loại BGM/SFX/UI/boss, ghi chú thay thế.
- Legal checklist: cái gì tuyệt đối không tái sử dụng.

### 1.4 `docs/spec/BALANCE.md` — số liệu
- Bảng HP enemy/boss gom theo prefab gốc (bỏ bản trùng trong `15-enemy-hp.csv`).
- Roster: 25 tàu, 13 drone, 46 boss (`idWave` 7001–7022 ch1, 9001–9024 ch2), 6 item.
- `Tech_Ability_Data`, `DataShopPack` (69 cột), `GP_Datas`, `RankManager`: cái nào dùng được, cái nào thiếu.
- **Danh sách field còn thiếu** mà phần 2 sẽ đi tìm: `Player_Get_Datas`, `Droid_Data_Balance`,
  `Tech_Datas`, `Stage_Get_Datas`, `Map_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas`.

### Chất lượng
- Tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh.
- Mỗi con số ghi nguồn: `nguồn: 14-ships.csv`. Suy đoán ghi rõ `> Giả định:`.
- Cuối mỗi file có mục **"Còn thiếu / phải đoán"**.
- Không bịa tên tàu/boss/nội dung text. Không có trong dump thì ghi "không xác định được từ APK".

---

## PHẦN 2 — Phiên này: Data & pipeline

Phạm vi (ghi vào `datas/`, `i18n/`, `tools/apk-analyze/`, `.github/workflows/`,
`docs/apk-analysis/`):

1. **`pathID → tên sprite`**: thêm `path_id` vào `04-asset-manifest.csv` (sửa
   `tools/apk-analyze/unity_assets.py`), join với `14-*.csv` → bảng tên thật cho tàu/drone/boss/item.
2. **Quét scene bundle còn thiếu**: `Player_Get_Datas`, `Droid_Data_Balance`, `Tech_Datas`,
   `Stage_Get_Datas`, `Map_Get_Datas`, `Enemy_Data_Balance`, `Device_Get_Data`, `GameDatas`
   trả về 0 instance trong `data.unity3d` → tìm ở các `.unity3d` / asset bundle khác trong split APK.
3. **Export AudioClip → WAV** + contact sheet sprite, đẩy vào artifact.
4. **Data pack**: `datas/*.json` + `i18n/{vi,en}.json` + `datas/validate.py` (dùng bảng tên ở bước 1).
5. **Báo cáo**: cập nhật `PHAN_TICH_WINDWINGS_APK.md` theo kết quả mới.
6. (tuỳ chọn, nếu còn thời gian) Ghidra `libil2cpp.so` để bóc công thức trong thân hàm.

Không giẫm phần 1: phần 2 **không** ghi vào `docs/spec/`.
