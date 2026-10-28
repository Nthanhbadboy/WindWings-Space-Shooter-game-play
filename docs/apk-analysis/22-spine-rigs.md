# Spine rigs — tàu / boss

> **Kết luận tạm thời.** Ghép theo `path_id`; tên rig suy ra từ tên region trong
> atlas, không phải tên do dev đặt.

- rig: **27**
- animation: **185**

## Tổng quan

| rig (path_id) | bone | slot | skin | anim | atlas page | hint |
|---|---:|---:|---:|---:|---|---|
| `580619` | 37 | 24 | 6 | 18 | skeleton.png | 1, 1.2, 1.3, 1.4, 1.5 |
| `580611` | 39 | 31 | 1 | 10 | skeleton.png | BigGun, Body, Enegry, Gun, Gun2 |
| `580623` | 25 | 24 | 6 | 10 | skeleton.png | 1, 1.2, 1.3, 10, 10.2 |
| `580613` | 32 | 23 | 1 | 9 | skeleton.png | 1, 2, 3, 4, 5 |
| `580617` | 12 | 11 | 5 | 7 | skeleton.png | Enegry, Enegry-2, Enegry-3, Gun, Gun-3 |
| `580621` | 13 | 34 | 5 | 6 | skeleton.png | 1, 1.3, 2, 2.2, 2.3 |
| `580625` | 13 | 12 | 5 | 6 | skeleton.png | 1, 1.2, 1.3, 2, 2.2 |
| `580627` | 15 | 16 | 6 | 6 | skeleton.png | 1, 1.2, 1.3, 10, 2 |
| `580629` | 14 | 10 | 6 | 6 | skeleton.png | A, A2, A3, B, B3 |
| `580631` | 9 | 8 | 5 | 6 | skeleton.png | A2, A3, B1, B2, B3 |
| `580633` | 10 | 23 | 6 | 6 | skeleton.png | A, A2, A3, B, C |
| `580635` | 12 | 11 | 5 | 6 | skeleton.png | A, A2, A3, B, B2 |
| `580637` | 13 | 12 | 5 | 6 | skeleton.png | A, A2, A3, B, B2 |
| `580639` | 10 | 9 | 6 | 6 | skeleton.png | Body, Body-1, Body-2, Body2, Body3 |
| `580641` | 12 | 11 | 5 | 6 | skeleton.png | A, A3, B, B2, C |
| `580643` | 9 | 8 | 5 | 6 | skeleton.png | A, A2, A3, B, B2 |
| `580645` | 19 | 18 | 5 | 6 | skeleton.png | 1, 1.2, 1.3, 10, 10.2 |
| `580647` | 29 | 31 | 5 | 6 | skeleton.png | 1a, 1b, 1c, 1d, 1e |
| `580649` | 170 | 19 | 5 | 6 | skeleton.png | Canh_Duoi_Ranh_3, Canh_Nho_Phu_Ranh_1, C |
| `580651` | 13 | 12 | 6 | 6 | skeleton.png | Body1, Body1-2, Body1-3, Body2, Body2-2 |
| `580653` | 14 | 13 | 5 | 6 | skeleton.png | Body, Body.2, Body.3, Enegry, Enegry.2 |
| `580655` | 17 | 19 | 6 | 6 | skeleton.png | 1, 1.2, 1.3, 10, 2 |
| `580657` | 15 | 17 | 5 | 6 | skeleton.png | 1, 1.3, 10, 10.2, 11.3 |
| `580659` | 23 | 20 | 5 | 6 | skeleton.png | 1, 1.2, 1.3, 10, 10.2 |
| `580661` | 12 | 14 | 5 | 6 | skeleton.png | 1, 1.2, 1.3, 2, 2.2 |
| `580663` | 11 | 10 | 5 | 6 | skeleton.png | 1, 1.2, 1.3, 2, 2.2 |
| `580615` | 18 | 6 | 1 | 5 | Saw.png | Cricle, L_Glow, R_GLow, Saw_01, Saw_02 |

## Animation theo rig

- **580619** — 18 anim: `Attack01` (0.4s), `Attack02` (0.4s), `Attack03` (0.4s), `Attack04` (0.4s), `Attack05` (0.4s), `Attack06` (0.4s), `Attack07` (0.4s), `Attack08` (0.4s), `Attack09` (0.4s), `Attack10` (0.4s), `Attack11` (0.4s), `Attack12` (0.4s), `Hide` (0.333s), `Idle`
- **580611** — 10 anim: `Attack1` (33.367s), `Attack2` (10.0s), `Attack3` (12.667s), `Attack4` (1.0s), `Baydi` (3.0s), `Chuyensangattack2` (1.067s), `Chuyensangattack3` (2.2s), `Dead` (2.333s), `UIShow` (3.667s), `Xuathien` (1.833s)
- **580623** — 10 anim: `AttackSpec` (0.433s), `AttackSuper` (0.5s), `AttackTopL` (0.6s), `AttackTopR` (0.6s), `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580613** — 9 anim: `Attack1` (9.0s), `Attack2` (9.0s), `Attack3` (18.0s), `Chuyensangattack2` (4.4s), `Chuyensangattack3` (6.667s), `Die` (4.833s), `UiShow` (9.0s), `Xuanhien` (3.0s), `Xuanhien2` (4.0s)
- **580617** — 7 anim: `Hide` (0.333s), `Idle`, `Idle2` (5.667s), `Idle3` (0.667s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580621** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580625** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580627** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580629** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580631** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580633** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580635** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580637** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580639** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (0.667s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580641** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580643** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580645** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580647** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580649** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)
- **580651** — 6 anim: `Hide` (0.333s), `Idle`, `Idle2` (1.0s), `Left` (0.333s), `Right` (0.333s), `Show` (0.667s)

## Dùng để làm gì

- `datas/spine.json` là spec rig cho bản mới: cùng bộ animation (Idle/Attack/…) nhưng
  xương/skin do bạn vẽ lại.
- `atlas.pages[].size` cho biết VRAM mỗi nhân vật chiếm bao nhiêu.
- Tên region tiếng Việt (`Canh_Duoi_…`) cho thấy team gốc đặt tên theo bộ phận —
  hữu ích khi rig lại.
