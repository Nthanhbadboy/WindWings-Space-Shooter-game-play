# Port-plan — map scene/systems từ spec sang Godot 4.x (plan-level)

**Trạng thái: PROVISIONAL.** Tài liệu này **không** tạo project Godot, không viết script, không chạy
engine. Nó chỉ chốt: *hệ nào → unit Godot nào → dữ liệu nào → kiểm bằng gì*. Hiện thực hoá chỉ khi user ra
lệnh scaffold (mandate Phase C).

Nguồn bắt buộc đọc trước: `docs/spec/START_HERE.md` → `MISSING_FOR_NEW_GAME.md` §1 (14 hệ + 2 hệ bổ sung)
→ `GAMEPLAY.md` §0–§7 → `UI.md` §2–§4 → `ENCOUNTERS.md` §1–§2 → `ECONOMY.md` §3–§5.
Learning-note native: `docs/rollout/LEARNING_NOTE_135_ANIMATOR_PORT.md`.

Nhãn: bảng dưới là **mapping đề xuất** (`INFERRED`); số liệu spec giữ nguyên nhãn của spec
(`STATIC_CONFIRMED` theo tài liệu, **không** phải tôi đo lại APK trong phiên này).

## 1. Kiến trúc tổng (đề xuất)

```
res://
  autoload/   GameData · SaveService · AudioService · EconomyService · IAPAdapter · AdsAdapter
  battle/     Battle scene: Player · BulletPool · EnemySpawner · Enemy · Boss · Pickup · HUD · Background
  ui/         Board scenes (Home/Maps/Begin/Endgame/Shop/Quest/BattlePass/Arena/PVP/Settings)
  data/       JSON/CSV -> Resource (.tres) qua converter chạy lúc build
```

Nguyên tắc: **luồng dữ liệu một chiều** từ `datas/*` (bản sao đã bóc) → `Resource` → scene. Không
hardcode số vào script; mọi bảng số phải trỏ về file nguồn.

## 2. Bảng map 16 hệ (theo `MISSING_FOR_NEW_GAME.md` §1)

| # | Hệ (spec) | Trạng thái spec | Unit Godot | Dữ liệu nguồn | Kiểm đếm được |
|---:|---|---|---|---|---|
| 1 | Vòng lặp lõi (30 s / phiên / tuần) | ✅ | `Main` + `Battle` + `Endgame` scene, `GameData` giữ vòng đời | `GAMEPLAY.md` §0 | 3 vòng lặp có trong build; 1 trận 2,5–4 phút (spec) |
| 2 | Điều khiển + va chạm | ✅ | `Player` (`Area2D`), kéo 1 ngón + 2 nút; biên 20×25, radius 15 unit | `ENEMY_BEHAVIOUR.md` | biên/radius đúng số; input cảm ứng + chuột |
| 3 | Súng / đạn / sát thương | ✅ L1 | `Weapon` Resource (458 khai báo) + `BulletPool` | `COMBAT.md` | 458 súng nạp được; damage 40–1.200; 186 loại đạn |
| 4 | Enemy | ✅ | `Enemy` scene + `EnemyBehaviour` Resource (48 archetype) | `ENCOUNTERS.md` §2.4, `datas/enemy_hp_by_id.json` | **92 type** (52+39+1) theo `ENCOUNTERS` §2.5 · **109** prefab có mặt trong wave / **178** prefab mang controller theo `BOSSES` §5 — xem §7.1; 150 cặp id→HP |
| 5 | Boss | 🟡 | `Boss` scene + state machine đọc event có mốc | `BOSSES.md` §2, `datas/boss_anim_events.csv` (**không sửa**) | 39 prefab boss + 1 mini-boss; 795 event có mốc; 268 cặp (prefab, clip); nhịp 0,17/0,33/1,0/5,0 s |
| 6 | Wave / spawn | ✅ | `EnemySpawner` đọc bảng wave, `Timer` theo `rate` | `datas/waves.json`, `ENCOUNTERS.md` §3 | 282 wave · 23.757 spawner · 22.451 entry (spec) |
| 7 | Độ khó 3 chế độ | ✅ | `Difficulty` Resource: `levelDelta [1,2,3.6,3.6]`, không nhân số quân | `DIFFICULTY_MODES.md` | 3 chế độ, 4 mốc delta |
| 8 | Kinh tế / rơi đồ | ✅ | `DropService` + `Pickup` + `EconomyService` | `datas/*coin*`, `ECONOMY.md` §1 | 676 coin/26 item đặt sẵn; công thức Coin1/Coin2 |
| 9 | Meta: tàu/sao/talent/drone | 🟡 | `Hangar` UI + `ShipStats` Resource | `datas/ships.json`, `datas/bosses.json` | 25 tàu · 13 drone · 23 method talent (spec) |
| 10 | UI | ✅ cấu trúc | Board scenes (Godot `Control`) theo 53 board/63 popup; 8 tab là widget | `UI.md` §3–§4, `docs/spec/screens.csv` | 797 màn · 150.131 node · 5.831 nút (spec) |
| 11 | Âm thanh | 🟡 | `AudioService` autoload + 15 rule | `datas/audio_rules.json`, `datas/audio_map.json` | 69 clip / 571,5 s · 92 id · 118 enum (spec) |
| 12 | Save / load + live-ops | 🟡 | `SaveService` (`user://save.json` + version field) | `MISSING_FOR_NEW_GAME.md` §2.3 | `StarCount`, `StarStageMaster{stage}_{mode}` giữ đúng ngữ nghĩa |
| 13 | Tech / build | 🟡 | `export_presets.cfg` + `version.json` | `GODOT_BUILD_PACKAGING_SPEC.md` | 3 preset đủ khoá (spec §9) |
| 14 | Arena / PvP | 🟡 luật đã decode | `ArenaService` + `Board_Arena`/`Board_PVP` | `datas/l2_535b0541_arena_pvp*.json.gz` | 10 league/10 rank · 6 dải reward (spec) |
| 15 | Meta thưởng ngày/tuần | 🟡 | `QuestService`, `BattlePassService`, `GiftService` | `docs/spec/DONE.md` mục #30 | 30 ô login · 85+39 mốc BP · 6 slot video (spec) |
| 16 | Sprite/prefab: ý nghĩa + binding | 🟡 | `SpriteLibrary` + atlas import | `datas/sprites.csv`, `datas/animator_map.csv.gz` | 2.197 index · 2.885 datas row · 925 rule (spec) |

Không hệ nào ở mức “thiếu hoàn toàn” theo spec (8 đủ · 8 một phần · 0 thiếu) — đó là lý do port-plan
được phép bắt đầu bằng **vertical slice**, không phải bằng chờ dữ liệu.

## 3. Vertical slice (Gate-4, đề xuất)

| Bước | Nội dung | Nghiệm thu đếm được |
|---|---|---|
| S1 | `Main` → `Home` → `Maps` → `Battle` → `Endgame` chạy được, không art cuối | 5 scene chuyển được; 0 asset gốc trong repo |
| S2 | Player bay + auto-fire + 1 wave theo `waves.json` | 1 wave nạp từ dữ liệu; số enemy/spawner khớp file |
| S3 | 3 stage mở đầu + **khuôn victory chung** (đúng giả thuyết spec §6) | 3 stage có gate riêng; victory chung phủ cả 3 |
| S4 | Boss đầu tiên theo event có mốc | ≥1 boss; event đọc từ `boss_anim_events.csv` (không sửa) |
| S5 | Save/load tối thiểu (`StarCount`, `StarStageMaster*`) | mở lại game còn dữ liệu; key đúng tên spec |

## 4. Ba rủi ro phải nêu trước khi scaffold

1. **Animation/Spine**: spec đếm 4 rig có animation đòn + 22 rig không có (`ANIMATION.md` §2.1–§2.2) và
   **791 clip Animator chưa đọc curve** (§3.3–§3.5). Godot không có runtime Spine chính thức trong engine;
   plugin Spine cho Godot là bên thứ ba, **giấy phép + phiên bản là `UNKNOWN`** ⇒ quyết định “dùng plugin
   nào / bake sang atlas+animation tự viết” phải chốt ở Gate-4, không mặc định.
2. **UI scope**: 53 board + 63 popup + 8 tab là bản gốc; slice chỉ cần khoảng 6 board. Mapping
   board→scene phải khai rõ board nào **bỏ** trong slice, tránh “port nửa vời mà tưởng đủ”.
3. **IP/asset**: mọi sprite/audio gốc thuộc GCenter — không đưa vào build; art mới do session art-designer
   theo `ART_REDRAW_PLAN.md` (Gate-5). Port-plan này chỉ dùng **số** (kích thước, nhịp, tỉ lệ).

## 5. Ranh giới với lane native (đã dừng)

- Lane `ef6b75ef` **dừng đào APK** theo lệnh user 132/133 + board lần 138. Learning-note 135 là bàn giao
  cuối của lane native; nếu Godot-coder cần thêm số native, phải có lệnh user mới.
- `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, `datas/player_start_stats.json` **giữ nguyên**,
  không sửa trong mọi nhánh port (protected paths chỉ nhánh `20330d0e` được ghi).

## 7. Chỗ spec lệch nhau — phải chốt trước khi code

| # | Lệch | Nguồn | Cách xử lý đề xuất |
|---:|---|---|---|
| 7.1 | **Số enemy**: 92 type · 109 prefab trong wave · 178 prefab mang `Enemy_Controller` | `ENCOUNTERS.md` §2.5 (92, đếm root `_gameobject`) · `BOSSES.md` §5 (178/109) · `MISSING_FOR_NEW_GAME.md` §1 hàng 4 (109 = 39 boss + 70) | Port lấy **“type dùng trong wave”** làm đơn vị thiết kế; 92 và 109 **không** phải mâu thuẫn số học mà là hai vũ trụ đếm khác nhau (type vs prefab). Ghi rõ đơn vị trong mọi bảng sau |
| 7.2 | **Số màn UI**: 797 “màn” vs 53 board + 63 popup + 8 tab | `MISSING` §1 hàng 10 (797 màn · 55.584 layout) vs `UI.md` §3–§5 | 797 là **screen node** đo từ layout; **116** board+popup (53+63, 8 tab là widget con) là đơn vị thiết kế. Slice dùng 116 làm đơn vị, 797 chỉ để đối chiếu độ phủ |
| 7.3 | **Đường bay enemy**: “399 đường bay (đo từ bản 800-cũ — CSV hiện hành 981 dòng, chưa có cột path để đếm lại)” | `MISSING` §1 hàng 4 | Không dùng 399 như số hiện hành; port đọc path từ `datas/waves.json`/`map*` và **đếm lại** khi có dữ liệu, ghi ngày đo |

Ba mục trên là `CONFLICTING` ở mức *đơn vị đếm*, không phải sai dữ liệu — nên xử lý bằng cách khai báo
đơn vị, không bằng chọn một con số rồi bỏ con số kia.

## 8. Kiểm tra tính đúng của bảng này (khi có lệnh scaffold)

- Mỗi dòng bảng §2 phải có **đúng 1 unit Godot** và **đúng 1 nguồn dữ liệu**; dòng nào 2 nguồn thì tách.
- Mỗi con số trong cột “Kiểm” phải đọc lại được từ file nguồn (script đếm, không gõ tay).
- Dòng nào spec ghi 🟡 thì unit Godot tương ứng phải có **cờ cấu hình** cho phần chưa chắc, không giả
  định hành vi.
