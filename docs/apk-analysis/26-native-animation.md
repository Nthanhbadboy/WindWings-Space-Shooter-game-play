# 26 — Animation gốc của Unity: `AnimationClip` + `AnimatorController` (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh từ `reverse-engineering/raw/typetrees/native-types.jsonl.gz`
> (lần chạy `e2c77ce`, tool `export_native_types` trong `unity_data.py`).
> Đây là lớp animation **thứ hai** ngoài Spine (27 rig / 185 animation — `23-spine-anim.md`).

## 1. Cái đã bóc được

| Loại | Số object | Nội dung ghi lại |
|---|---:|---|
| `AnimationClip` | **791** | tên, `path_id`, thời lượng (`m_MuscleClip.m_StopTime`), `m_LoopTime`, số event, sample rate |
| `AnimatorController` | **308** | tên, số clip tham chiếu (`m_AnimationClips`), số state-machine behaviour |
| `ParticleSystem` | **4.845** (chỉ `path_id`) | typetree ~30 module — chưa xuất chi tiết |
| `Animator` | **5.792** instance | nối được prefab gốc **5.686 (98,2%)**, tên controller **5.603 (96,7%)** → `datas/animator_map.csv.gz` |

## 2. Số liệu rút ra

| Chỉ số | Giá trị |
|---|---:|
| Tên clip khác nhau | **226** (791 clip — nhiều bản sao theo prefab) |
| Tên phổ biến nhất | `Idle` 82 · `idle` 80 · `Xuathien` 41 · `Setup` 37 · `Appear` 26 · `attack1/2/3` 18/18/16 |
| Clip có thời lượng > 0 | **707 / 791** |
| Thời lượng median | **1,9 s**; dài nhất `Lite_Appear` **75 s** |
| Clip lặp (`m_LoopTime`) | **251** |
| Clip có event | 318, tổng **793 event** |
| Controller tham chiếu clip | tổng **793** lượt, max 28 clip/controller, chỉ 1 controller rỗng |
| Tên controller phổ biến | `Body` 54 · `Parent` 37 · `Trap_Brick` 9 · `Icon` 6 · `Enemy_Ingame` 5 |
| Sample rate | 60 fps (các clip đã kiểm) |

## 3. Giới hạn thật — curve chưa đọc được bằng typetree

Mọi clip đều có `m_FloatCurves / m_PositionCurves / m_RotationCurves … = 0` trong typetree.
Curve của build này nằm trong **dữ liệu clip dạng stream** (`m_StreamedClip` /
binding constant), không nằm ở các list trên — nên muốn lấy keyframe phải dùng reader
chuyên cho AnimationClip (UnityPy `parse_as_object()` → `AnimationClip` samples),
chưa làm.

Hệ quả: lớp này hiện mới ở mức **danh mục + nhịp** (tên, độ dài, lặp, event),
chưa ở mức **dựng lại chuyển động** như Spine. Với clone, Spine + số liệu nhịp ở đây là đủ
để đặt timing; curve Mecanim chỉ cần khi có boss dùng Mecanim thay Spine.

## 4. Còn thiếu

| # | Thứ | Cách làm tiếp |
|---:|---|---|
| 1 | Keyframe curve của 791 clip | ❌ đã thử 2 cách (typetree + UnityPy reader, `27-anim-curves.md`): đều 0. Phải giải mã streamed clip thủ công |
| 2 | `ParticleSystem` chi tiết | xuất riêng các module chính (emission/shape) dạng tóm tắt |
| 3 | ~~Map controller → prefab~~ | ✅ xong: `Animator` → prefab gốc 5.686/5.792, controller 5.603/5.792 (175 cái trỏ file ngoài `m_FileID 2/3/4`, 14 cái không gán). Controller phổ biến: `Box_Gift (0)` 936 · `Body` 790 · `Parent` 766 · `Popup_Network` 663 · `A` 516 · `BossObject` 251 |
