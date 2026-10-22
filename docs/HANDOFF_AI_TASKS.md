# Chia việc phân tích — WindWings

Tài liệu này để **giao việc cho AI/người khác** làm song song, không giẫm chân lên pipeline
(`tools/`, `.github/`, `docs/apk-analysis/`, `reverse-engineering/`).

## Quy tắc chung (áp dụng cho MỌI task)

1. **Chỉ đọc**, không sửa: `docs/apk-analysis/**`, `reverse-engineering/**`, `tools/**`, `.github/**`.
2. **Chỉ ghi** vào thư mục được giao của mình (bên dưới). Không sửa file của task khác.
3. **Không commit**: APK/XAPK, ảnh/âm thanh gốc, `dump.cs` chưa nén, bất kỳ file > 5 MB.
4. Mọi con số/kết luận phải **ghi rõ nguồn**: tên file + mục trong `docs/apk-analysis/`.
   Không suy đoán rồi trình bày như sự thật — chỗ nào là giả định thì ghi `> Giả định:`.
5. Viết tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh.
6. Khi xong: mở **PR riêng** vào `main`, tiêu đề `docs(<task>): ...`, mô tả ngắn những gì đọc từ đâu.
   Không push trực tiếp vào `main`, không push vào branch `arena/*`.

### Nguồn dữ liệu đã có sẵn trong repo

| File | Nội dung |
|---|---|
| `docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md` | Báo cáo tổng 12 mục (đọc cái này trước) |
| `docs/apk-analysis/06-gameplay-systems.md` | 6.090 dòng — field/method class gameplay |
| `docs/apk-analysis/07-enums.md` | 5.230 dòng — 255 enum |
| `docs/apk-analysis/08-ui-map.md` | 15.296 dòng — 125 class Board/Popup/Tab + field/method |
| `docs/apk-analysis/09-numbers-and-formulas.md` | 78 class config |
| `docs/apk-analysis/12-localization.csv` | 1.416 key × 19 ngôn ngữ |
| `docs/apk-analysis/13-iap-products.csv` | 170 product ID |
| `docs/apk-analysis/14-ships/drones/bosses/items.csv` | roster tàu/drone/boss/item |
| `docs/apk-analysis/15-enemy-hp.csv` | 981 Enemy_Datas có HP + đường dẫn prefab |
| `docs/apk-analysis/class-inventory.csv` | ~1.000 class MonoBehaviour trong `data.unity3d` |
| `reverse-engineering/scriptableobjects/*.csv` | CSV thô từng class (DataShopPack 69 cột, GP_Datas, RankManager…) |
| `reverse-engineering/textassets/` | 26 Spine skeleton + atlas, charset, billing |

APK gốc: **draft release** `windwings-apk-1.3.118` (asset `windwings.xapk`, 142 MB).
Artifact `windwings-analysis` giữ sprite/audio export (chỉ tải được từ tab Actions, cần quyền repo).

---

## Task A — GDD / gameplay spec

**Ghi vào:** `docs/game-design/`  •  **Đọc:** 06, 07, 09, PHAN_TICH (mục 4–6)

Mục tiêu: biến dump C# thành **thiết kế game đọc được**, đủ để dev khác implement mà không cần đọc dump.

- `00-overview.md` — one-pager: thể loại, vòng lặp 30 giây / 10 phút / 1 tuần, target platform.
- `01-core-loop.md` — vòng lặp gameplay: di chuyển, auto-fire, enemy wave, drop item, end-game.
- `02-progression.md` — tàu → sao → device → drone → tech → talent → chapter → arena → battle pass.
  Mỗi bước: mở khoá bằng gì, chi phí dạng gì (coin/gem/star), có time-gate không.
- `03-economy.md` — các nguồn tiêu thụ coin/gem/energy; bảng sink/source; suy ra tốc độ tiến trình.
- `04-modes.md` — 7 PlayMode (`Normal, FightBoss, Challange, Survival, TryPlayer, Arena, PVP`)
  + 3 PVPMode; mỗi mode: mục đích, thưởng, điều kiện mở.
- `05-bosses.md` — 20 boss + 2 mini-boss + 16 MB variant: phase, attack, HP (dùng `15-enemy-hp.csv`).
- `06-meta.md` — battle pass, shop, quest, rank/arena season, event.
- `07-implementation-order.md` — thứ tự build đề xuất + ước lượng (người-tuần).

**Definition of done:** mỗi mục có sơ đồ (mermaid) hoặc bảng; mỗi khẳng định có nguồn;
có mục "những gì còn thiếu / cần đoán" ở cuối mỗi file.

---

## Task B — Data pack + i18n

**Ghi vào:** `datas/` và `i18n/`  •  **Đọc:** 12, 13, 14-*, `reverse-engineering/scriptableobjects/`

Mục tiêu: JSON hoá dữ liệu để dùng trực tiếp trong engine mới (Godot/Unity/three.js).

Schema tối thiểu (giữ nguyên tên field gốc, thêm `_note` nếu cần):

```json
// datas/ships.json
{ "source": "Data_Players.allPlayers", "count": 25,
  "items": [{ "id": 10001, "sprite_path_id": 3581, "star": 2.0, "actived": true }] }

// datas/bosses.json
{ "source": "Data_Boss.allBosses", "count": 46,
  "items": [{ "id_wave": 7001, "chapter": 1, "sprite_path_id": 3869 }] }

// datas/items.json
{ "source": "Data_Items.allDropItems", "count": 6,
  "items": [{ "index": 1, "icon_sprite_path_id": 2376, "stat_sprite_path_ids": [2854, 3416, 3916, 2832, 3209] }] }
```

Kèm:
- `datas/drones.json`, `datas/boss_hp.json` (981 dòng, gom theo prefab gốc, bỏ bản trùng),
- `datas/tech_abilities.json`, `datas/shop_packs.json` (từ `DataShopPack.csv`, 69 cột),
- `datas/iap_products.json` (170 ID, tách consumable / non-consumable),
- `datas/schema.md` — giải thích từng field + field nào là pathID (chưa resolve ra tên sprite).
- `i18n/vi.json`, `i18n/en.json` — từ `12-localization.csv`; key giữ nguyên, **chỉ 2 ngôn ngữ**;
  thêm `i18n/_keys.md` đếm key theo nhóm tiền tố (`txt_menu_`, `txt_shop_`…).

**Definition of done:** JSON parse được, có script `datas/validate.py` kiểm tra schema + đếm,
mọi file < 2 MB, không có dữ liệu bịa.

---

## Task C — UI spec & screen graph

**Ghi vào:** `docs/ui-spec/`  •  **Đọc:** 08, 07 (`BoardID`, `AdPos`, `PurchaseType`), PHAN_TICH mục 5.2

- `01-screen-graph.md` — sơ đồ mermaid: Home → từng nhánh (Play, Shop, Upgrades, Drones, Devices,
  Cards, Quest, BattlePass, Arena, PvP, Settings), 49 board + 63 popup.
- `02-screens.csv` — một dòng / board: `class,board_id,mở từ đâu,popup con,data cần load`.
- `03-popups.md` — 63 popup: loại (confirm/reward/offer/error), điều kiện bật, nút nào.
- `04-navigation-rules.md` — `LoadBoardMode {Single, Additive, PopUp}`, back stack, khi nào
  board bị destroy vs ẩn, ai giữ state (`UIManager`).
- `05-wireframe-notes.md` — cho mỗi board chính: vùng bố cục (header/tab/list/footer) suy ra
  từ field `RectTransform`/`ButtonEvents` trong dump — **không** copy pixel từ game.

**Definition of done:** mọi board trong `08-ui-map.md` đều xuất hiện trong `02-screens.csv`;
graph không có node treo; ghi rõ chỗ nào chỉ là suy luận.

---

## Task D — Art / audio spec cho bản clone (art mới, không copy)

**Ghi vào:** `docs/asset-spec/`  •  **Đọc:** 04, PHAN_TICH mục 7, `reverse-engineering/textassets/`

Mục tiêu: biến inventory asset thành **brief cho hoạ sĩ/vẽ art mới**.

- `01-art-brief.md` — art direction đề xuất (khác WindWings): palette, silhouette tàu, tỉ lệ.
- `02-sprite-list.csv` — từ `04-asset-manifest.csv`: nhóm asset (UI/Enemy/Boss/Bullet/Drone/FX),
  kích thước thật, đề xuất kích thước mới, có cần 9-slice không.
- `03-atlas-plan.md` — gom atlas theo màn (thay `sactx-*` cũ), số atlas mục tiêu, budget VRAM.
- `04-spine-rigs.md` — 26 skeleton: số bone, slot, skin, danh sách animation, `defaultMix`.
  Đây là spec để rig lại tàu/boss mới cùng bộ animation.
- `05-audio-list.csv` — 69 clip: phân loại (BGM/SFX/UI/boss), độ dài ước tính, ghi chú thay thế.
- `06-legal.md` — checklist: cái gì tuyệt đối không tái sử dụng.

**Definition of done:** hoạ sĩ đọc xong vẽ được mà không cần mở game; mọi asset gốc chỉ được
mô tả bằng **số liệu** (kích thước, số bone, tên animation), không nhúng file.

---

## Phối hợp

- 4 task không ghi trùng thư mục ⇒ merge được độc lập, không conflict.
- Ai xong trước mở PR trước; review chéo: Task A ↔ C (mode ↔ board), B ↔ D (id ↔ sprite).
- Việc còn lại của pipeline (map pathID → tên sprite, quét scene bundle còn thiếu
  `Player_Get_Datas`/`Droid_Data_Balance`, Ghidra công thức) **không** giao ở đây — cần sửa
  workflow, sẽ làm ở branch `arena/ef6b75ef-…`.
