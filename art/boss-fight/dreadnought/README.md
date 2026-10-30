# DREADNOUGHT — linh kiện Boss-37001 (Boss Book §3.2A)

Session **art-gen** (chỉ sinh hình linh kiện). Branch
`arena/227ffc0a-windwings-space-shooter-game-p`.
Hồ sơ nguồn: `docs/design/03_BOSS_BOOK.md` §3.2A + §3.5,
`04_COMBAT_FX_ART_ANIMATION.md` §4.3, `06_PRODUCTION_ROADMAP.md` §6.4.1–6.4.2
(đọc từ remote, branch `arena/020ecffe…` commit `2e9b0fc`).
Hồ sơ boss cũ đã đạt: `art/boss-fight/` @ commit `fd4f65a` (KHÔNG sinh lại).

## TRẠNG THÁI LÔ 1 — **1/10 món** (DỪNG vì 403)

| # | Món | Trạng thái | Canvas | Ghi chú |
|---|---|---|---|---|
| 01 | Thân Dreadnought trần (sạch) | **ĐÃ GIAO** | 512×512 | 9 bệ gắn cho đủ 11 điểm hỏa lực |
| 02 | Thân hư hại NHẸ | BỊ CHẶN 403 | — | chưa sinh |
| 03 | Thân hư hại VỪA | BỊ CHẶN 403 | — | chưa sinh |
| 04 | Thân hư hại NẶNG | BỊ CHẶN 403 | — | chưa sinh |
| 05 | Đầu ụ phụ (2 nòng) | BỊ CHẶN 403 | — | chưa sinh |
| 06 | Đế tĩnh ụ phụ | BỊ CHẶN 403 | — | chưa sinh |
| 07 | Đầu pháo quạt sát lõi | BỊ CHẶN 403 | — | chưa sinh |
| 08 | Đế pháo quạt | BỊ CHẶN 403 | — | chưa sinh |
| 09 | Vòng giáp lõi (MỞ) | BỊ CHẶN 403 | — | chưa sinh |
| 10 | Đế BigGun ĐÃ PHÁ | BỊ CHẶN 403 | — | chưa sinh |

Ảnh sheet tổng của lô: `review/LO1-sheet.png` (bản nửa cỡ: `LO1-sheet-half.png`).
Chi tiết lỗi: `INCIDENT-403.md`, `manifest.json` (mục `blocker`).

## Món 01 — thân Dreadnought trần

- **Master**: `masters/01-hull-clean.png` (1254×1254, sinh nguyên bản, nền đen).
- **Xuất**: `exports/01-hull-clean.png` (512×512, alpha), hash trong `manifest.json`.
- **Vì sao phải vẽ thân mới**: §3.2A.E cho phép đổi silhouette để chứa đủ 11
  điểm hỏa lực. Thân cũ (§3.2) hẹp, không có chỗ cho pod hông ngoài + 4 ụ phụ.
- **Bố cục**: pháo đài rộng, vai trên rộng, **mũi tàu dài hướng xuống** chiếm
  ~40% chiều cao. Mọi bệ gắn để **rỗng, lộ rõ** để cắm linh kiện lên.

### Toạ độ 11 điểm hỏa lực (đo trên `exports/01-hull-clean.png`, canvas 512)

| Điểm | x | y | Loại |
|---|---:|---:|---|
| ụ phụ vai trái / phải | 136 / 372 | 62 | bệ quay |
| lõi (core) | 246 | 118 | khoang lõi |
| BigGun trái / phải | 133 / 369 | 158 | bệ quay Ø lớn |
| pod tên lửa trái / phải | 37 / 476 | 188 | ray cứng ngoài |
| pháo quạt trái / phải | 193 / 316 | 229 | bệ **cố định** |
| ụ phụ hông trái / phải | 103 / 410 | 293 | bệ quay |

11 = 2 BigGun + 1 pháo giữa + 4 ụ phụ + 2 pod + 2 pháo quạt.

**Khác biệt so với "vùng thiết kế" §3.2A.A** (bảng đó là vùng tham chiếu, A ghi
rõ art tự đo toạ độ chính thức): thân mới **dồn cụm hỏa lực lên nửa trên** —
thân chiếm y≈20…400, mũi tàu y≈400…505. Vì vậy các bệ nằm cao hơn số trong bảng
(ví dụ vai 62 thay vì 142). Coder dùng **số đo trong file này**, không dùng số
trong bảng thiết kế. Nếu director muốn cụm hỏa lực hạ xuống đúng tỉ lệ bảng §3.2A
thì đây là việc **đổi silhouette** (thuộc phạm vi, không phải tay nghề) — báo lại
để director quyết, art không tự đổi.

## Tái dùng từ hồ sơ cũ (không sinh lại)

| Món | File nguồn @ `fd4f65a` |
|---|---|
| Đầu + đế BigGun trái/phải | `masters/02-left-turret.png`, `masters/round2/03-right-turret-redo.png` |
| Pháo chính / đầu phát tia | `masters/round3/04-cannon.png` |
| 2 pod tên lửa | `masters/round3/05-left-pod.png`, `masters/round4/06-right-pod.png` |
| Lõi glow | `masters/07-core.png` |
| Tia + sạc | `masters/round2/11-beam-strip.png`, `round3/13-charge-ring-redo.png` |
| Muzzle / tên lửa | `masters/round2/15-muzzle.png`, `round2/14-missile.png` |
| Bộ đạn 5 họ | `masters/10-laser-bullet.png`, `exports/bullet-B1/B2/B3` |

**Không tái dùng được**: 3 bậc hư hại **cũ** — chúng vẽ trên silhouette hẹp
§3.2, không khớp thân rộng mới, nên 02–04 của Lô 1 là món mới bắt buộc
(§3.2A.E yêu cầu vẽ lại cả đế cháy theo từng bậc).

## Kiểm chất lượng (tầng ART tự đóng)

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| Tách nền | flood-fill nền đen liên thông + ramp alpha + thu nhỏ **premultiplied** | `cutout-report.json` |
| Halo nền sáng/tối | **Không halo**: pixel nền sát hình đúng màu nền, 0 px vượt 240; viền alpha 20–200 có luminance TB 32,9 < thân 58,4 | `review/01-hull-clean--halo-{dark,light}.png` |
| Cỡ đọc thật | 205px vẫn đọc silhouette + 9 bệ | panel A của `LO1-sheet.png` |
| Alpha sạch | `bbox=(7,5,505,507)`, không còn viền đen | `manifest.json` |

## Tầng ENGINE (chờ coder QA, không chặn art)

Pivot chính thức từng ụ (đo khi đủ ụ của Lô 1–2), collider, khe né, muzzle
point trong runtime.

## Kỷ luật sinh ảnh — sự cố hiện tại

Xem `INCIDENT-403.md`. Tóm tắt: gọi sinh ảnh **lần 2** trả `403 PERMISSION_DENIED`
("account has been flagged for suspicious activity") lúc **2026-10-30 18:49 UTC**
⇒ dừng ngay, **không retry**, 9 món còn lại chờ USER gỡ cờ tài khoản.
