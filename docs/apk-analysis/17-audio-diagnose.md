# Audio diagnosis

- clips: **69**
- có `m_Resource` (FSB trong bundle): **69**
- streamed (`m_StreamData`): **0**
- xuất được WAV: **0**
- không xuất được: **69**
- tổng `m_Size` khai báo: **0 bytes**

## File trong bundle

```
/tmp/apk/extract/data.unity3d
resources.resource
```

## Từng clip (20 đầu)

| path_id | name | resource | streamed | size | samples | saved |
|---|---|---|---|---:|---:|---|
| 1689 | `Bắn Đạn Dính Trên Màn Hình` | True | None |  | 0 | — |
| 1690 | `Địch Đất Đỏ Bắn` | True | None |  | 0 | — |
| 1691 | `Sfx_Defeat` | True | None |  | 0 | — |
| 1692 | `Sfx_Destroy 12` | True | None |  | 0 | — |
| 1693 | `Bgm_Home 2` | True | None |  | 0 | — |
| 1694 | `Bgm_Home 1` | True | None |  | 0 | — |
| 1695 | `Sfx_Click 1` | True | None |  | 0 | — |
| 1696 | `wood-frog-sequence` | True | None |  | 0 | — |
| 1697 | `Địch Xanh Bắn Đạn Nhanh` | True | None |  | 0 | — |
| 1698 | `Sfx_CollectSupperPower` | True | None |  | 0 | — |
| 1699 | `Sfx_Transform2` | True | None |  | 0 | — |
| 1700 | `weapon_lightning_006` | True | None |  | 0 | — |
| 1701 | `nox-sound__whoosh-rope` | True | None |  | 0 | — |
| 1702 | `Sfx_Shoot 11` | True | None |  | 0 | — |
| 1703 | `impact_blaster_ice` | True | None |  | 0 | — |
| 1704 | `Sfx_CollectPower` | True | None |  | 0 | — |
| 1705 | `Sfx_Shoot 8` | True | None |  | 0 | — |
| 1706 | `Súng Máy Bắn nhiều Viên Liên Tục Tốc Độ ` | True | None |  | 0 | — |
| 1707 | `Sfx_Transform5` | True | None |  | 0 | — |
| 1708 | `Sfx_Destroy 7` | True | None |  | 0 | — |

## Typetree keys (mọi clip)

| key | số clip |
|---|---:|
| `m_Ambisonic` | 69 |
| `m_BitsPerSample` | 69 |
| `m_Channels` | 69 |
| `m_CompressionFormat` | 69 |
| `m_Frequency` | 69 |
| `m_IsTrackerFormat` | 69 |
| `m_Legacy3D` | 69 |
| `m_Length` | 69 |
| `m_LoadInBackground` | 69 |
| `m_LoadType` | 69 |
| `m_Name` | 69 |
| `m_PreloadAudioData` | 69 |
| `m_Resource` | 69 |
| `m_SubsoundIndex` | 69 |

Kết luận: nếu `m_Resource`/`m_Size` có nhưng `samples` = 0 thì dữ liệu FSB nằm
trong file audio riêng (`.resS`/`.resource`) chưa được extract — cần lấy thêm từ APK.
