# Đọc nhánh spec `arena/20330d0e` — **tham khảo, không merge**

> Ghi lại đúng những gì đọc được từ nhánh của AI kia, để lần sau không phải đọc lại
> và để phân biệt rõ **cái nào là dữ liệu của mình** với **cái nào là nhận định của họ**.
>
> - Nhánh: `arena/20330d0e-windwings-space-shooter-game-p`, commit cuối **`f3e36b7`**
> - Đã fetch về ref cục bộ `origin/other-ai` **chỉ để đọc** (`git show origin/other-ai:...`)
> - **Không merge, không cherry-pick.** Nhánh đó chỉ ghi trong `docs/spec/` (19 file, 7.693 dòng);
>   dữ liệu thô vẫn do nhánh này sinh ra.

## 1. Họ nói gì — 6 ý đáng dùng

| # | Ý | Nơi ghi | Mình kiểm lại được không |
|---:|---|---|---|
| 1 | `Enemy_Controller` là **hub**: mỗi enemy tự khai PathID của 9 script con (`dataScript`, `healthScript`, `physicsScript`…), ghép **981/981 = 100%** bằng khoá số | `DATA_SYNC.md` §7.7 | **Có** — đọc thẳng `raw/typetrees/Enemy_Controller.jsonl.gz`, thấy đúng 9 field PPtr |
| 2 | Cap **1.500** cắt 6 bảng sinh quân/đường bay (`Call_Data` 1.500/23.757 = 6,3%…) | §7.8 | **Có** — đúng là 6 bảng dừng ở 1.500 |
| 3 | `Enemy_Health.noDamage = True` **241/981 = 24,6%** | §7.8 | **Có** — số nằm trong typetree đã export |
| 4 | 5 mắt ghép 0% **cùng một nguyên nhân**: thiếu `Transform.m_Father`; `Transform` = **228.432** object chưa export | §7.9–7.10 | **Một phần** — đếm được `Transform` rất nhiều, nhưng con số 228.432 lấy từ log của họ |
| 5 | Step REA chiếm **460 s / 660 s ≈ 70%** thời gian run mà `05-rea.md` **không có dữ liệu game** | `PIPELINE_AUDIT.md` §9.2 | **Chưa** — cần xem log run; ước lượng khớp với thời gian run mình quan sát (10–12 phút) |
| 6 | 46% commit trên nhánh là `chore(re) [skip ci]` do bot sinh | §9.6 | **Có** — `git log` đếm được |

## 2. Ba thứ họ nói mà mình **kiểm lại thấy sai / thiếu căn cứ**

| Ý của họ | Kiểm lại |
|---|---|
| `uiScript` trỏ tới class `Enemy_UI` | **Không có class `Enemy_UI`** trong `reverse-engineering/il2cpp/class-index.json` (3.662 class). Field tên `uiScript` thì có, class đích thì không. Có thể là `Enemy_Hp_Bar`/`Enemy_Display` — **chưa xác định**, đừng ghi `Enemy_UI` vào tài liệu như thể tồn tại |
| `Call_Point` 23.757 instance, "có thể là bản đầy đủ của `Call_Data`" | Không tìm thấy class `Call_Point` trong class-index; con số 23.757 **trùng** với số dòng `Call_Data`, nên nhiều khả năng là **cùng dữ liệu đọc theo cách khác**, không phải bảng mới. Vẫn thêm tên vào `TARGETS` để lần chạy sau trả lời dứt điểm |
| "45.659 quân" | Chính họ ghi là **mức B** (§7.13). Không dùng làm số chuẩn |

## 3. Mình đã làm gì sau khi đọc (chỉ trên dữ liệu của mình)

Sửa `tools/apk-analyze/unity_data.py`:

1. **`TARGETS` mở rộng**: thêm 27 class `Enemy_*` (gồm `Enemy_Physics`, `Enemy_Destroy`,
   `Enemy_Burned`, `Enemy_Stun`, `Enemy_LookAtPlayer`, `Enemy_SpawnChilds`, `Enemy_DropGold`…)
   và `Call_Point`.
2. **`TARGET_SUFFIXES = ("_Director", "_MiniDirector", "ChildDirector", "_AttackPhases")`** —
   ghép theo hậu tố thay vì liệt kê tay 44 class đạo diễn boss.
3. **`CAP_OVERRIDES`**: 6 bảng bị cắt 1.500 nay đọc đủ (`Call_Data` 30k, `PointToPoint_Spawner` 14k,
   `PinMap_Spawner` 3,4k, `Rocket_Spawner` 2,2k, `PathCreator`/`Path_Spawner` 1,8k).
4. **`export_transform_tree()`**: xuất `transform-tree.tsv.gz` (`path_id · gameobject · father`) +
   `prefab-roots.csv` (tên prefab gốc) — đây là bảng mở 5 mắt ghép còn 0%.
5. **`script-links.jsonl.gz`**: mọi PPtr tên `*Script` + class đích, để biết field nào trỏ class nào
   mà không phải đoán.

Sửa `.github/workflows/analyze-apk.yml`:

- `concurrency: analyze-apk-<ref>` + `cancel-in-progress` → hết cảnh 3 run chạy song song cùng nội dung.
- Step **REA chỉ chạy khi `workflow_dispatch` với `run_rea=true`** (mặc định tắt). Báo cáo cũ
  `05-rea.md` **không bị ghi đè** khi bỏ qua.

Sửa `tools/apk-analyze/ui_layout.py`: ghi `_skipped.csv` (class × lý do bỏ) — trước đây chỉ có tổng,
không biết **màn nào** biến mất giữa hai lần chạy (16 màn chỉ còn ở file cũ, xem `24-ui-screens.md`).

## 3b. Kết quả kiểm lại sau khi export (lần chạy `d84ea72`)

| Ý của nhánh spec | Kết quả thật |
|---|---|
| "`Enemy_Physics` 981, thêm 1 dòng là mở 100% lớp hành vi" | Export **được 981 dòng**, nhưng class chỉ có **2 field** và **0/981** dòng có giá trị ⇒ **giả thuyết sai**: va chạm nằm ở `BoxCollider2D` runtime |
| "`uiScript` → `Enemy_UI`" | Thực tế → **`Enemy_Display`**; class `Enemy_UI` **không tồn tại** |
| "`Call_Point` có thể là bản đầy đủ của `Call_Data`" | `Call_Point.dataScript → Call_Data` (23.757/23.757) ⇒ là **lớp bọc**, không phải bảng mới |
| "`Transform` 228.432 object mở 5 mắt ghép" | **Đúng**: xuất đủ **228.432** dòng, 2.089 root; mở **4/5 mắt** lên 100% (458 súng · 251 hitbox · 558 `parentRotate` · 1.372 đường bay). Mắt còn lại `Stage_Behaviour.bossObj` **không** phải vấn đề Transform |
| "981 enemy" | 981 dòng khớp 3 bảng, nhưng **204 nằm dưới prefab `Board_*`** (126 ở màn chọn boss) ⇒ enemy trong trận ≈ 777–855 |
| ENEMY_BEHAVIOUR.md tính trên 800 dòng | Bản đủ 981: **tỉ lệ gần như không đổi**, số tuyệt đối thiếu ~18% (xem `25-enemy-behaviour.md` §6) |
| "Step REA chiếm 70% thời gian" | Đã tắt mặc định → run **11 phút → 4 phút 01** (đo run `39879117958`) |

## 3c. Đọc thêm 3 commit mới của họ (`d8e61c2`, `d303cc0`, `a6a4081`, 00:47)

- Họ **tự sửa** đúng ba điểm mục 3b (`Enemy_Physics` rỗng, `uiScript → Enemy_Display`,
  981 là số bản ghi) và ghi rõ "tôi đã sai" — hai nhánh độc lập cho **cùng kết quả**, tăng độ tin.
- Họ giải mã `spawnType` bằng khớp tỉ lệ với `waves.json`. Mình **đếm lại độc lập** trên
  `Call_Data` đầy đủ: khớp từng con số (16.498/4.199/1.688/686/686, tổng 45.659) → đã ghi vào
  `25-enemy-behaviour.md` §8 kèm hệ quả `number = 0` ở 100%.

## 3d. Đọc thêm 3 commit (`7818043`, `857259c`, `6278f9e`, 01:00)

- Sổ mắt ghép của họ: **11 mắt 100%** — khớp với `prefab_joins` của mình (7 mắt) cộng các mắt PathID cũ.
- Số họ đếm `ParticleSystem` **4.845** · `Animator` **5.792**: mình export xong thì **khớp đúng từng số**.
- Nhãn "458 súng kể cả preview, 319 thật": mình tính lại từ `prefab_joins` — 139/458 dưới `Board_*`
  (73 `SelectBoss` + 66 `FightBoss`) nên ghi khoảng **319–385** thay vì một số cứng, đã sửa `25` §5.
- Họ cũng kết luận `parse_as_object` cho 0 keyframe → cần decoder streamed clip. Trùng `27-anim-curves.md`.

## 3e. Đọc thêm 2 commit (`a2cb074d`, `6ba892f0`, 01:12)

- **`copies` giải quyết số quân**: họ kiểm `sum(len × copies) = 45.659`. Mình tính lại trên
  `datas/waves.json` của mình: **45.659 khớp tuyệt đối** (dedupe lệch nhỏ: 11.101 vs 11.099 spawner,
  22.475 vs 22.483 entry — không đổi tích). Từ nay: 45.659 = quân thật, ~22,5k = lượt khai báo.
- **Damage khai báo trong Director**: họ báo 112 field/18 boss (55–2.800). Mình quét nhanh
  34 file `*Director*.jsonl.gz` đã export: thấy 64 giá trị damage dạng số (`laserDamage`,
  `damageRocket` 600, `damageBulletArea` 1200…) — **khớp về chất**, số đếm khác do cách tính.
- `animator_map` của mình họ cũng đối chiếu: 5.792 dòng / 494 prefab gốc / 96,7% có tên controller.

## 3f. Đọc thêm 2 commit (`662e2b27`, `88579a3f`)

- **HP campaign = 0**: họ nói `StartHealthPoint = 0` ở 514/981 — mình đếm lại: **đúng 514/981 (52,4%)**,
  còn lại tối đa 10.000.000. Độ khó campaign do công thức runtime, không nằm ở prefab.
- Mục mở "width × height sprite" và "ParticleSystem" trong sổ của họ: phía mình đã đóng cả hai
  (`sprites.csv` 2.816/2.885 có kích thước; `29-particle-systems.md`).

## 3g. Đọc thêm 3 commit (`13befdd3`, `deeead9b`, `52f329ad`, 01:27)

- Họ bắt đầu **đọc sâu arm64** và ra công thức đầy đủ cho HP người chơi:
  `GetStartHp = StartHp × (1 + stepCommon×TechStatPoints(0) + abi7×GetNumberAbility(7))`.
  Kiểm bằng trace của mình: `GetStartHp` đúng là có **fadd 1.0** và gọi `GetHpStatPercent`
  → cấu trúc `(1 + …)` **khớp**; hệ số chi tiết là phần họ đọc sâu hơn, mức **B**.
- Họ tách lại mức tin: "không có bảng HP theo tàu trong serialize" (**A**) vs
  "runtime gán lúc chọn tàu" (**C**, chưa kiểm) — cách ghi này đúng quy ước của mình.

## 3h. Commit `d76108b4` (01:35) + điều kiện lật ngược của họ đã được đáp

- Họ kiểm bằng chữ ký: chỉ 7–8 method nhận `playerIndex`, **không có method HP nào**.
  Mình đếm lại trên JSON của mình: **8 method có `playerIndex`** (5 damage/rate + 3 giá/thời gian mở tàu),
  47 method float/int còn lại không tham số ⇒ kết luận **khớp**.
- Họ ghi điều kiện lật ngược: *"export `Player_Health.asm.txt` đầy đủ"*. Phía mình đã thêm
  **5 class** vào scan (`Player_Health`, `Player_Talent`, `Player_Ability`, `Player_Ingame`,
  `Player_Attack`) — asm + JSON + trace đã có, tổng 425 method / 324 `bl` giải được tên.
  Kết quả đầu tiên: `Player_Health` gọi `GetStartHp` trong lambda của `Start`, không thấy
  đường gán HP theo tàu trong các class đã quét (mức B — chưa đọc hết rẽ nhánh).

## 4. Điều kiện lật ngược

- Nếu `Enemy_Physics` export ra mà **phần lớn field rỗng** (như `Spawner.dataScript` = 0), thì
  "mở 100% lớp hành vi bằng 1 dòng" là **sai** — khi đó thứ tự ưu tiên cũ (đọc method body) mới đúng.
- Nếu `transform-tree.tsv.gz` có `father = 0` ở phần lớn object thì các object đó là **root của
  prefab lồng**, và cần thêm `PrefabInstance.m_Modification` mới nối được — 5 mắt ghép vẫn 0%.

Cả hai đều **kiểm được bằng dữ liệu lần chạy tới**, không phải tranh luận.
