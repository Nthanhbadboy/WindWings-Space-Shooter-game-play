# Audio diagnosis

- clips: **69**
- có `m_Resource` (FSB trong bundle): **69**
- streamed (`m_StreamData`): **0**
- xuất được WAV: **69**
- không xuất được: **0**
- tổng `m_Size` khai báo: **0 bytes**

## File trong bundle

```
/tmp/apk/extract/data.unity3d
/tmp/apk/extract/resources.resource
```

## Từng clip (20 đầu)

| path_id | name | resource | streamed | size | samples | saved |
|---|---|---|---|---:|---:|---|
| 1689 | `Bắn Đạn Dính Trên Màn Hình` | True | None |  | 1 | Bắn_Đạn_Dính_Trên_Màn_Hình_Bắn_Đạn_Dính_Trên_Màn_Hình.wav.wav |
| 1690 | `Địch Đất Đỏ Bắn` | True | None |  | 1 | Địch_Đất_Đỏ_Bắn_Địch_Đất_Đỏ_Bắn.wav.wav |
| 1691 | `Sfx_Defeat` | True | None |  | 1 | Sfx_Defeat_Sfx_Defeat.wav.wav |
| 1692 | `Sfx_Destroy 12` | True | None |  | 1 | Sfx_Destroy_12_Sfx_Destroy_12.wav.wav |
| 1693 | `Bgm_Home 2` | True | None |  | 1 | Bgm_Home_2_Bgm_Home_2.wav.wav |
| 1694 | `Bgm_Home 1` | True | None |  | 1 | Bgm_Home_1_Bgm_Home_1.wav.wav |
| 1695 | `Sfx_Click 1` | True | None |  | 1 | Sfx_Click_1_Sfx_Click_1.wav.wav |
| 1696 | `wood-frog-sequence` | True | None |  | 1 | wood-frog-sequence_wood-frog-sequence.wav.wav |
| 1697 | `Địch Xanh Bắn Đạn Nhanh` | True | None |  | 1 | Địch_Xanh_Bắn_Đạn_Nhanh_Địch_Xanh_Bắn_Đạn_Nhanh.wav.wav |
| 1698 | `Sfx_CollectSupperPower` | True | None |  | 1 | Sfx_CollectSupperPower_Sfx_CollectSupperPower.wav.wav |
| 1699 | `Sfx_Transform2` | True | None |  | 1 | Sfx_Transform2_Sfx_Transform2.wav.wav |
| 1700 | `weapon_lightning_006` | True | None |  | 1 | weapon_lightning_006_weapon_lightning_006.wav.wav |
| 1701 | `nox-sound__whoosh-rope` | True | None |  | 1 | nox-sound__whoosh-rope_nox-sound__whoosh-rope.wav.wav |
| 1702 | `Sfx_Shoot 11` | True | None |  | 1 | Sfx_Shoot_11_Sfx_Shoot_11.wav.wav |
| 1703 | `impact_blaster_ice` | True | None |  | 1 | impact_blaster_ice_impact_blaster_ice.wav.wav |
| 1704 | `Sfx_CollectPower` | True | None |  | 1 | Sfx_CollectPower_Sfx_CollectPower.wav.wav |
| 1705 | `Sfx_Shoot 8` | True | None |  | 1 | Sfx_Shoot_8_Sfx_Shoot_8.wav.wav |
| 1706 | `Súng Máy Bắn nhiều Viên Liên Tục Tốc Độ ` | True | None |  | 1 | Súng_Máy_Bắn_nhiều_Viên_Liên_Tục_Tốc_Độ_Nhanh_Súng_Máy_Bắn_nhiều_Viên_Liên_Tục_Tốc_Độ_Nhanh.wav.wav |
| 1707 | `Sfx_Transform5` | True | None |  | 1 | Sfx_Transform5_Sfx_Transform5.wav.wav |
| 1708 | `Sfx_Destroy 7` | True | None |  | 1 | Sfx_Destroy_7_Sfx_Destroy_7.wav.wav |

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
