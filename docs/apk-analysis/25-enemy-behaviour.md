# 25 — Lớp hành vi enemy/boss + bảng `Transform` (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh từ dữ liệu thô trong `reverse-engineering/raw/typetrees/`
> (lần chạy `d84ea72`). Chưa đối chiếu runtime; các field vắng mặt ở đây nghĩa là
> **game không lưu trong prefab**, không phải "không có" — rất nhiều logic nằm trong code.

## 1. Đã export thêm gì

| Bảng | Dòng | File |
|---|---:|---|
| `Enemy_Physics` | **981** | `raw/typetrees/Enemy_Physics.jsonl.gz` |
| `Enemy_Destroy` | 971 | `…/Enemy_Destroy.jsonl.gz` |
| `Enemy_Burned` | 695 | |
| `Enemy_LookAtPlayer` | 391 | |
| `Enemy_Stun` | 140 | |
| `Enemy_Display` | 981 | |
| 26 class `Enemy_*` khác + 44 `*_Director` | — | ghép theo hậu tố `_Director` / `ChildDirector` / `_AttackPhases` |
| `Call_Data` **đầy đủ** | **23.757** (trước bị cắt 1.500) | |
| `Call_Point` | 23.757 | |
| `PointToPoint_Spawner` | 13.292 (trước 1.500) | |
| `PinMap_Spawner` / `Rocket_Spawner` / `PathCreator` / `Path_Spawner` | 3.165 / 2.019 / 1.714 / 1.688 | |
| **`transform-tree.tsv.gz`** | **228.432** | `path_id · gameobject · father` |
| `prefab-roots.csv` | 2.089 | tên prefab gốc + số con |

## 2. Kết quả lật ngược quan trọng: `Enemy_Physics` **rỗng**

Giả thuyết của nhánh spec: "thêm `Enemy_Physics` là mở 100% lớp hành vi". Kiểm bằng dữ liệu:

| | Số |
|---|---:|
| Dòng `Enemy_Physics` | 981 |
| Field serialize (ngoài `m_*`) | **2** (`autoCacheColliders`, `allColliders`) |
| Dòng có giá trị khác rỗng | **0 / 981** |

⇒ `Enemy_Physics` là **lớp đánh dấu**, va chạm lấy từ `BoxCollider2D` của object con lúc runtime,
không có số nào để bóc. **Không phải lỗi export** — export đã chạy và trả về đúng những gì có.

Ngược lại, các lớp **có** dữ liệu thật:

| Class | Field có nghĩa | Phân bố |
|---|---|---|
| `Enemy_Display` (chính là `uiScript`) | `appearOff` / `dieOff` / `hitableRenderers` | appearOff **921 đúng / 60 sai**; hitableRenderers: 1 renderer **531**, 0 **367**, 2–4 **70** |
| `Enemy_LookAtPlayer` | `offsetAngle`, `lerpAngleSpeed` | offset **90°** ở 360/391, `lerpAngleSpeed` **8.0** ở 316/391 |
| `Enemy_Burned` | `allDestroyEffects` | 695 dòng, effect id dạng số (`90002`…) |
| `Enemy_Stun` | `allCanStunMachineGunAttacks` | 140 dòng, mỗi dòng 1 PPtr |
| `Enemy_Destroy` | `pointBurst` | chỉ **48/971** có gán, còn lại null |

**Hệ quả thiết kế:** muốn tái tạo cảm giác "bắn vào chỗ nào cũng trúng", phải dựa vào
`Enemy_Health.noDamage` (241/981 = 24,6% bộ phận không ăn damage) **và** `hitableRenderers`
của `Enemy_Display`, không phải `Enemy_Physics`.

## 3. Sửa một kết luận sai của nhánh spec: `uiScript` **không** trỏ `Enemy_UI`

`Enemy_Controller.uiScript` → **`Enemy_Display`** (981/981). Trong 3.662 class của game
**không tồn tại class `Enemy_UI`**. Bảng ghép thật của 9 script con:

| field | class đích | khớp |
|---|---|---:|
| `dataScript` | `Enemy_Datas` | 981 / 981 |
| `healthScript` | `Enemy_Health` | 981 / 981 |
| `movementScript` | `Enemy_Movement` | 981 / 981 |
| `physicsScript` | `Enemy_Physics` | 981 / 981 (rỗng, xem §2) |
| `uiScript` | **`Enemy_Display`** | 981 / 981 |
| `destroyScript` | `Enemy_Destroy` 971 · `Enemy_DestroyDelayed` 3 · `MB_Destroy` 7 | 981 / 981 |
| `burnedScript` | `Enemy_Burned` | 689 / 981 |
| `stunScript` | `Enemy_Stun` | 137 / 981 |
| `appearScript` | `Enemy_Appear` 914 · **51 class `*_Director`** | 981 / 981 |

Phát hiện thêm: **boss không dùng `Enemy_Appear`** — `appearScript` của boss trỏ thẳng tới
`BossN_Director` / `MBN_Director` / `MB6_ChildDirector`. Đây là mắt nối **boss → đạo diễn**
mà trước đó phải ghép bằng tên.

## 4. `Call_Point` — không phải "bản đầy đủ của `Call_Data`"

| | `Call_Data` | `Call_Point` |
|---|---:|---:|
| Dòng | 23.757 | 23.757 |
| Field riêng | 22 (`spawnType`, `listPrefabEnemies`, `ySpawn`, `rate`, `pathScript`…) | **6** (`dataScript`, `warningPoints`) |
| `dataScript` trỏ tới | — | **`Call_Data`** 23.757 / 23.757 |

⇒ `Call_Point` là **lớp bọc mỏng** (1 điểm cảnh báo cho mỗi entry `Call_Data`), **không** chứa
dữ liệu bị cắt. Bản `Call_Data` 1.500 dòng trước đây mới là chỗ thiếu, giờ đã đủ 23.757.

## 5. Bảng `Transform` mở được bao nhiêu mắt ghép

| Mắt | Trước | Sau khi có `Transform` |
|---|---:|---:|
| `Gun_Attack.m_GameObject` → prefab gốc | 0% | **458 / 458 = 100%** |
| `Boss_BodyPhysics.m_GameObject` → prefab gốc | 0% | **251 / 251 = 100%** |
| `Enemy_Movement.parentRotate` → prefab gốc | 0% | **558 / 558 = 100%** |
| `Wave.startPoint/endPoint` → prefab gốc | 0% | **1.372 / 1.372 = 100%** (ra `Wave_XXXX`, không phải `PathCreator`) |
| `Stage_Behaviour.bossObj` | 0% | **250 / 250 = 100%** — nhưng cả 250 đều về root `Board_Maps`: `bossObj` là **icon boss trên bản đồ stage**, không phải prefab boss. Mắt này nối được nhưng nối vào UI |

Cấu trúc cây: **228.432** transform, **2.089** root (0,9%) — tức 99,1% object có `m_Father`,
nên lo ngại "prefab lồng làm đứt chuỗi" **không xảy ra** ở build này.

Ví dụ root nhận được: `Boss-37006`, `Wave_0005`, `Board_SelectBoss`, `Board_FightBoss`.
Súng trong `Board_SelectBoss`/`Board_FightBoss` là **súng preview trên UI**, không phải súng
trong trận — khi thống kê theo prefab phải loại hai board này ra.

## 6. Số của nhánh spec tính trên **800/981** — bảng đầy đủ ở đây

`docs/spec/ENEMY_BEHAVIOUR.md` (nhánh `20330d0e`) tính phân bố tốc độ trên **800 dòng**
(vì CSV bị cap 800 lúc đó). Bản đầy đủ **981 dòng**:

| Chỉ số | Nhánh spec (800) | Bản đủ (981) |
|---|---:|---:|
| tốc độ `listSpeeds[0]` = **5,0** | 473 (59,1%) | **562 (57,3%)** |
| = 1,0 | 97 | **123** |
| = 20,0 | 87 (10,9%) | **118 (12,0%)** |
| = 3,5 | 61 | **83** |
| = 30,0 | 8 | **8** (không đổi) |
| median / min / max | 5,0 / 0,2 / 30,0 | **5,0 / 0,2 / 30,0** (không đổi) |
| `isTurret` | 95 (11,9%) | **112 (11,4%)** |
| `facingMove` | 775 | **949 (96,7%)** |
| `fixedAngle` | 13 | **19** |
| đổi tốc giữa đường | 104 | **137 (14,0%)** |
| `border` = 15/−10/10/−15 | 799 | **841** (còn 139 dùng `z = −25`, 1 dòng `25/−20/20/−25`) |

⇒ **Tỉ lệ gần như không đổi, số tuyệt đối thiếu ~18%**. Kết luận thiết kế của họ
(nền 3,5 / boss 5,0 / vài con 20–30) **vẫn đúng**.

Nhóm theo **prefab gốc** (dùng `transform-tree`, không dùng chuỗi `_gameobject` ~38%):

| nhóm | n | min | median | max |
|---|---:|---:|---:|---:|
| `Boss-*` | **318** (họ báo 170) | 0,2 | 5,0 | 20,0 |
| `Wave_*` | **288** (họ báo 204) | 1,0 | 3,5 | 30,0 |
| `Board_SelectBoss` | 126 | 0,8 | 5,0 | 20,0 |
| `Board_FightBoss` | 70 | 5,0 | 5,0 | 5,0 |
| prefab lẻ khác | 171 | 0,8 | 5,0 | 20,0 |

### ⚠ 981 không phải "981 enemy trong trận"

| Nơi chứa `Enemy_Controller` | Số |
|---|---:|
| `Boss-*` | 318 |
| `Wave_*` | 288 |
| `Board_SelectBoss` (màn **chọn** boss — mô hình trưng bày) | **126** |
| `Board_FightBoss` (màn đánh boss — nhiều khả năng là enemy thật) | 70 |
| `Board_Players` + `Board_Maps` | 8 |
| prefab lẻ khác | 171 |

**Kết luận tạm thời (mức B):** `Enemy_Datas` / `Enemy_Health` / `Enemy_Controller` đều **981 dòng
và khớp 981/981 với nhau**, nhưng **≥126 dòng là mô hình ở màn chọn boss**, không phải enemy
xuất hiện trong trận. Số enemy "dùng được" nằm trong khoảng **777–855** cho tới khi đối chiếu
`Board_FightBoss` bằng runtime. Đừng trích "981 enemy" như số tuyệt đối.

## 7. Còn thiếu

| # | Thứ | Trạng thái | Cách làm tiếp |
|---:|---|---|---|
| 1 | ~~`Stage_Behaviour.bossObj`~~ | ✅ xong | hoá ra trỏ thẳng GameObject (250/250 khớp cột `gameobject` của transform-tree) và đều thuộc `Board_Maps` — là icon bản đồ, không cần nối tiếp. Bảng nối tái lập được: `datas/prefab_joins.csv.gz` (`tools/apk-analyze/prefab_joins.py`, 3.870 dòng, 7 mắt đều 100%) |
| 2 | `AnimationClip` (791) · `AnimatorController` (308) | ✅ danh mục xong | xem `26-native-animation.md` — còn thiếu keyframe curve (streamed clip) |
| 3 | `ParticleSystem` | chưa dump | thêm vào `unity_data.py` như `Transform` |
| 4 | Số quân 45.659 | chưa kiểm | tính lại từ `Call_Data` 23.757 dòng đầy đủ + `number` |
| 5 | Ý nghĩa `editType` / `spawnType` / `warningPoints` | chưa map | đối chiếu `dump.cs` + 10 method trong `19-il2cpp-constants.md` |
