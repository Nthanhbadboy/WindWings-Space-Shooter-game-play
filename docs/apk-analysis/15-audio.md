# Audio (69 AudioClip)

- Nguồn: `data.unity3d` — `AudioClip.samples` export bằng UnityPy (`tools/apk-analyze/unity_assets.py export`)
- File WAV nằm trong artifact `windwings-analysis` → `/tmp/apk/unity/export/AudioClip/` (không commit vào repo vì bản quyền)
- Danh sách dưới đây lấy từ `04-unity-assets.md` (probe UnityPy)

## Nhạc nền / track dài (4)

| tên | kênh | Hz |
|---|---:|---:|
| `Action Dynamic Track #2 1 MP3  ` | 1 | 44100 |
| `Bgm_Boss 1` | 1 | 44100 |
| `Bgm_Home 1` | 1 | 44100 |
| `Bgm_Home 2` | 1 | 44100 |

## Hiệu ứng âm thanh (65)

| tên | kênh | Hz |
|---|---:|---:|
| `Boss nhện đỏ laze` | 1 | 44100 |
| `Buzz Saw` | 1 | 44100 |
| `Bắn Đạn Dính Trên Màn Hình` | 1 | 44100 |
| `Energy Rock Track #2 (looped) 1` | 1 | 44100 |
| `Energy Rock Track #2 (looped) 2` | 1 | 44100 |
| `Energy Rock Track #3 (looped)` | 1 | 44100 |
| `Heavy Riff 5 (Looped)` | 1 | 44100 |
| `Sfx_Alarm 2` | 1 | 44100 |
| `Sfx_BossAppear 1` | 1 | 44100 |
| `Sfx_Change` | 1 | 48000 |
| `Sfx_Click 1` | 1 | 16000 |
| `Sfx_Click 2` | 1 | 48000 |
| `Sfx_CollectCoin` | 1 | 48000 |
| `Sfx_CollectDroid` | 1 | 48000 |
| `Sfx_CollectHp` | 1 | 48000 |
| `Sfx_CollectOverdrive` | 1 | 44100 |
| `Sfx_CollectPower` | 1 | 16000 |
| `Sfx_CollectSupperPower` | 1 | 48000 |
| `Sfx_Defeat` | 1 | 44100 |
| `Sfx_Destroy 1` | 1 | 44100 |
| `Sfx_Destroy 10` | 1 | 24000 |
| `Sfx_Destroy 12` | 1 | 16000 |
| `Sfx_Destroy 2` | 1 | 44100 |
| `Sfx_Destroy 3` | 1 | 44100 |
| `Sfx_Destroy 4` | 1 | 44100 |
| `Sfx_Destroy 5` | 1 | 44100 |
| `Sfx_Destroy 6` | 1 | 44100 |
| `Sfx_Destroy 7` | 1 | 44100 |
| `Sfx_Destroy 8` | 1 | 44100 |
| `Sfx_Destroy 9` | 1 | 44100 |
| `Sfx_Fly` | 1 | 44100 |
| `Sfx_Gun` | 1 | 44100 |
| `Sfx_RocketFire 1` | 1 | 16000 |
| `Sfx_RocketFire 2` | 1 | 44100 |
| `Sfx_Shoot 1` | 1 | 44100 |
| `Sfx_Shoot 10` | 1 | 48000 |
| `Sfx_Shoot 11` | 1 | 44100 |
| `Sfx_Shoot 6` | 1 | 44100 |
| `Sfx_Shoot 8` | 1 | 44100 |
| `Sfx_SwordAttack` | 1 | 44100 |
| `Sfx_Transform1` | 1 | 48000 |
| `Sfx_Transform2` | 1 | 48000 |
| `Sfx_Transform3` | 1 | 22050 |
| `Sfx_Transform4` | 1 | 48000 |
| `Sfx_Transform5` | 1 | 44100 |
| `Sfx_TurnOnShield` | 1 | 44100 |
| `Sfx_Victory` | 1 | 48000 |
| `Shot` | 1 | 44100 |
| `SungBanNhanh` | 1 | 44100 |
| `S£ng Boss VÖng` | 1 | 44100 |
| `Súng Máy Bắn nhiều Viên Liên Tục Tốc Độ Nhanh` | 1 | 44100 |
| `carmsie__you-cannot-harm-me` | 1 | 44100 |
| `energy-magic-shot` | 1 | 44100 |
| `impact_blaster_ice` | 1 | 44100 |
| `nox-sound__whoosh-rope` | 1 | 48000 |
| `robot-ready` | 1 | 44100 |
| `robotlaughing` | 1 | 44100 |
| `sfx_Destroy 11` | 1 | 48000 |
| `sword-02` | 1 | 48000 |
| `weapon_flame_001` | 1 | 44100 |
| `weapon_lightning_006` | 1 | 44100 |
| `wood-frog-sequence` | 1 | 44100 |
| `Âm Nổ Player` | 1 | 22050 |
| `Địch Xanh Bắn Đạn Nhanh` | 1 | 22050 |
| `Địch Đất Đỏ Bắn` | 1 | 44100 |

## Ghi chú

- Toàn bộ clip đều mono 44.1 kHz (1 kênh) — nhẹ, phù hợp mobile.
- Một số tên viết bằng tiếng Việt không dấu/không chuẩn (ví dụ `Súng`, `Bắn`, `Địch`) → nội dung do dev Việt Nam làm, khớp với publisher GCenter.
- `SoundClip` (92 instance) là ScriptableObject map id → clip, nối với `AudioSource` tên `Bgm_*`/`Sfx_*` trong scene.
