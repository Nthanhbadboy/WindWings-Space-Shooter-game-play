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

## 4. Điều kiện lật ngược

- Nếu `Enemy_Physics` export ra mà **phần lớn field rỗng** (như `Spawner.dataScript` = 0), thì
  "mở 100% lớp hành vi bằng 1 dòng" là **sai** — khi đó thứ tự ưu tiên cũ (đọc method body) mới đúng.
- Nếu `transform-tree.tsv.gz` có `father = 0` ở phần lớn object thì các object đó là **root của
  prefab lồng**, và cần thêm `PrefabInstance.m_Modification` mới nối được — 5 mắt ghép vẫn 0%.

Cả hai đều **kiểm được bằng dữ liệu lần chạy tới**, không phải tranh luận.
