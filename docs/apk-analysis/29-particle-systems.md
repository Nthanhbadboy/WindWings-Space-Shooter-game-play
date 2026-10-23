# 29 — ParticleSystem: tóm tắt module (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh từ `reverse-engineering/raw/typetrees/native-types.jsonl.gz`
> (mục `ParticleSystem`, lần chạy `29c37783`). Chỉ giữ scalar + scalar một cấp trong từng
> module — đủ cho tham số chính, không gồm curve chi tiết.

## 1. Quy mô

| Chỉ số | Giá trị |
|---|---:|
| `ParticleSystem` | **4.845** (ghi đủ 4.845 tóm tắt) |
| Module có trong mỗi hệ | ~23 (`Initial`, `Emission`, `Shape`, `Velocity`, `Color`, `Size`, `Rotation`, `Noise`, `Collision`, `Trail`, `UV`…) |
| `EmissionModule.enabled` | **4.845 / 4.845** |

## 2. Tham số chính (top-level)

| Tham số | Phân bố |
|---|---|
| Thời lượng `lengthInSec` | **5,0 s** ở 2.430 hệ; 1,0 s: 687; 2,0 s: 606; 0,1 s: 347; median **5,0**, max 15,0 |
| `looping` | True **3.427** (70,7%) · False 1.418 |
| `playOnAwake` | True **4.809** (99,3%) |
| `simulationSpeed` | 1,0: 4.367 · **2,0: 428** · 3,0: 13 · 0,5: 10 |

## 2b. Số thiết kế trong module (MinMaxCurve)

| Tham số | Median | Phổ biến nhất |
|---|---:|---|
| Tuổi thọ hạt `startLifetime` | **1,0 s** | 1,0 (1.159 hệ) · 0,5 (639) · 0,8 (470) |
| Tốc độ đầu `startSpeed` | **0,0** | 0,0 ở **3.199/4.845** — hạt đứng yên rồi mới bị module khác đẩy; 5,0 (362) · 6,0 (306) |
| Kích thước đầu `startSize` | **1,0** | 0,5 (653) · 1,0 (612) · 0,7 (401) |
| Tỉ lệ phát `rateOverTime` | **0,0** | 0,0 ở 2.684 — phát theo burst, không phát đều; 4,0 (597) · 1,0 (302) |

Đọc ra (mức **B**): FX của game chủ yếu là **burst tại chỗ** (tốc độ đầu 0, tỉ lệ phát 0)
rồi dùng module lực/vận tốc riêng — không phải phun liên tục kiểu mưa sao băng.

## 3. Giới hạn

- Đã nối ParticleSystem → prefab gốc: **4.839 / 4.845 (99,9%)** → `datas/particle_systems.csv.gz`
  (tool `animator_joins.py`).
- Curve trong module (theo thời gian/tốc độ) chưa xuất; muốn dựng FX giống hệt phải đọc thêm.
- 4.845 là số **instance trong prefab**, không phải số hiệu ứng khác nhau.
