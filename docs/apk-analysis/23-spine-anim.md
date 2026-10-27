# 23 — Spine animation: timeline thật (kết luận tạm thời)

> **Kết luận tạm thời.** Bóc trực tiếp từ TextAsset JSON mà game nạp
> (`reverse-engineering/textassets/skeleton*.json`, `Saw.json`) — không vẽ lại, không
> đoán. Chưa đối chiếu runtime; thời điểm có thể lệch nếu game chỉnh `animation.timeScale`.

## Tổng quan

- rig: **27**, animation: **185**, keyframe: **12,274**
- event: **21**, loại curve: `0`×13, `0.157`×2, `0.168`×1, `0.243`×53, `0.244`×2, `0.245`×73, `0.248`×4, `0.25`×492, `0.252`×28, `0.258`×80, `0.273`×24, `0.28`×49, `0.283`×1, `0.284`×26, `0.305`×1, `0.31`×1, `0.311`×18, `0.315`×45, `0.319`×2, `0.32`×11, `0.321`×4, `0.322`×1, `0.325`×9, `0.326`×4, `0.327`×5, `0.328`×5, `0.329`×4, `0.33`×27, `0.331`×9, `0.333`×9, `0.335`×9, `0.337`×9, `0.338`×4, `0.339`×5, `0.34`×4, `0.341`×13, `0.343`×5, `0.344`×9, `0.345`×50, `0.346`×10, `0.349`×18, `0.35`×9, `0.351`×8, `0.355`×9, `0.363`×129, `0.364`×4, `0.369`×5, `0.372`×1, `0.373`×4, `0.375`×121, `0.378`×14, `0.381`×123, `0.516`×2, `0.62`×4, `0.637`×4, `0.652`×4, `0.776`×37, `linear`×9158, `stepped`×91

File máy đọc: `datas/spine_anim.json.gz` (timeline đầy đủ), `docs/apk-analysis/spine-events.csv` (mọi event).

## Rig lớn nhất

| rig | bone | slot | anim | keyframe | thời lượng max (s) |
|---|---:|---:|---:|---:|---:|
| `skeleton__13` | 170 | 19 | 6 | 2,499 | 1.0 |
| `skeleton__8` | 32 | 23 | 9 | 1,444 | 18.0 |
| `skeleton__21` | 39 | 31 | 10 | 993 | 33.3667 |
| `skeleton__9` | 29 | 31 | 6 | 850 | 1.0 |
| `skeleton__5` | 25 | 24 | 10 | 674 | 1.0 |
| `skeleton__2` | 23 | 20 | 6 | 412 | 1.0 |
| `skeleton__24` | 19 | 18 | 6 | 362 | 1.0 |
| `skeleton__25` | 12 | 11 | 7 | 360 | 5.6667 |
| `skeleton__17` | 37 | 24 | 18 | 334 | 1.0 |
| `skeleton__6` | 15 | 16 | 6 | 325 | 1.0 |
| `skeleton__7` | 13 | 12 | 6 | 315 | 1.0 |
| `skeleton` | 17 | 19 | 6 | 300 | 1.0 |

## Event trong animation (dùng để căn thời điểm bắn/va chạm)

| rig | animation | t (s) | event |
|---|---|---:|---|
| `skeleton__17` | `Attack01` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack02` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack03` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack04` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack05` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack06` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack07` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack08` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack09` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack10` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack11` | 0.3333 | `Shot` |
| `skeleton__17` | `Attack12` | 0.3333 | `Shot` |
| `skeleton__21` | `Attack3` | 0.6333 | `Stop` |
| `skeleton__21` | `Attack3` | 3.3 | `Stop` |
| `skeleton__21` | `Attack3` | 5.8667 | `Stop` |
| `skeleton__21` | `Attack3` | 8.2 | `Stop` |
| `skeleton__21` | `Attack3` | 10.6 | `Stop` |
| `skeleton__21` | `Attack4` | 0.7 | `Banplasma` |
| `skeleton__5` | `AttackSpec` | 0.2333 | `Spec` |
| `skeleton__5` | `AttackTopL` | 0.3 | `TopL` |
| `skeleton__5` | `AttackTopR` | 0.3 | `TopR` |

Đếm theo tên: `Shot`×12, `Stop`×5, `Banplasma`×1, `Spec`×1, `TopL`×1, `TopR`×1

## Còn thiếu

- Chưa map rig → đơn vị trong game (ship nào / boss nào) — cần đối chiếu `datas/spine.json`
  (`atlas_asset_name`) với prefab.
- `deform` / `drawOrder` chỉ đếm số mục, chưa xuất nội dung.
- Chưa có `timeScale` runtime, nên thời lượng có thể ngắn hơn khi chơi thật.
