# Pipeline diagnostics

## Unity payload
```
total 336M
-rw-r--r-- 1 runner runner   11K Oct 22 21:12 RuntimeInitializeOnLoads.json
-rw-r--r-- 1 runner runner  3.9K Oct 22 21:12 ScriptingAssemblies.json
-rw-r--r-- 1 runner runner   120 Oct 22 21:12 _listing.txt
-rw-r--r-- 1 runner runner   61M Oct 22 21:12 data.unity3d
-rw-r--r-- 1 runner runner  8.3M Oct 22 21:12 global-metadata.dat
-rw-r--r-- 1 runner runner   45M Oct 22 21:12 libil2cpp.so
-rw-r--r-- 1 runner runner   17M Oct 22 21:12 libunity.so
-rw-r--r-- 1 runner runner  106M Oct 22 21:22 re-libil2cpp.asm
-rw-r--r-- 1 runner runner   17K Oct 22 21:22 re-libil2cpp.evidence.json
-rw-r--r-- 1 runner runner  6.0K Oct 22 21:22 re-libil2cpp.json
-rw-r--r-- 1 runner runner   75K Oct 22 21:22 re-libil2cpp.md
-rw-r--r-- 1 runner runner  872K Oct 22 21:22 re-libil2cpp.pdf
-rw-r--r-- 1 runner runner   92M Oct 22 21:23 re-libunity.asm
-rw-r--r-- 1 runner runner   17K Oct 22 21:22 re-libunity.evidence.json
-rw-r--r-- 1 runner runner  7.8K Oct 22 21:22 re-libunity.json
-rw-r--r-- 1 runner runner   49K Oct 22 21:23 re-libunity.md
-rw-r--r-- 1 runner runner  699K Oct 22 21:23 re-libunity.pdf
-rw-r--r-- 1 runner runner 1023K Oct 22 21:12 resources.arsc
-rw-r--r-- 1 runner runner  4.9M Oct 22 21:12 resources.resource
```

## assets/bin/Data listing (from APK)
```
    63881856  cached        assets/bin/Data/data.unity3d
     5105184  cached        assets/bin/Data/resources.resource
```

## UnityPy import smoke test
```
UnityPy 1.25.4
audio converter OK
typetree OK
```

## Export output
```
/tmp/apk/unity/export/Sprite             1903 files 47M
/tmp/apk/unity/export/Texture2D          614 files 60M
/tmp/apk/unity/export/AudioClip          69 files 48M
/tmp/apk/unity/audio                     70 files 48M
```

## Asset gallery
```
docs/assets:
total 416
drwxr-xr-x 3 runner runner   4096 Oct 22 21:12 .
drwxr-xr-x 5 runner runner   4096 Oct 22 21:12 ..
-rw-r--r-- 1 runner runner   2190 Oct 22 21:13 INDEX.md
-rw-r--r-- 1 runner runner   7275 Oct 22 21:13 audio-index.csv
drwxr-xr-x 2 runner runner   4096 Oct 22 21:13 contact-sheets
-rw-r--r-- 1 runner runner 169413 Oct 22 21:13 manifest.csv
-rw-r--r-- 1 runner runner 220632 Oct 22 21:13 sprites-index.csv
-rw-r--r-- 1 runner runner   5123 Oct 22 21:13 stats.json

docs/assets/contact-sheets:
total 13996
drwxr-xr-x 2 runner runner   4096 Oct 22 21:13 .
drwxr-xr-x 3 runner runner   4096 Oct 22 21:12 ..
-rw-r--r-- 1 runner runner 275298 Oct 22 21:13 atlas-01.jpg
-rw-r--r-- 1 runner runner 252528 Oct 22 21:13 atlas-02.jpg
-rw-r--r-- 1 runner runner 222282 Oct 22 21:13 atlas-03.jpg
-rw-r--r-- 1 runner runner 225186 Oct 22 21:13 atlas-04.jpg
-rw-r--r-- 1 runner runner 205562 Oct 22 21:13 atlas-05.jpg
-rw-r--r-- 1 runner runner 314050 Oct 22 21:13 atlas-06.jpg
-rw-r--r-- 1 runner runner 119265 Oct 22 21:13 atlas-07.jpg
-rw-r--r-- 1 runner runner 186939 Oct 22 21:13 background-01.jpg
-rw-r--r-- 1 runner runner 171009 Oct 22 21:13 background-02.jpg
-rw-r--r-- 1 runner runner  41576 Oct 22 21:13 background-03.jpg
-rw-r--r-- 1 runner runner 177267 Oct 22 21:13 bosses-01.jpg
-rw-r--r-- 1 runner runner 171755 Oct 22 21:13 bullet-01.jpg
-rw-r--r-- 1 runner runner  38495 Oct 22 21:13 bullet-02.jpg
-rw-r--r-- 1 runner runner 110716 Oct 22 21:13 drones-01.jpg
-rw-r--r-- 1 runner runner 119597 Oct 22 21:13 enemy-01.jpg
```

## Step logs (tail)
```
===== /tmp/apk/logs/audio.log
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
stats: {'clips': 69, 'has_resource': 69, 'res_bytes': 5105184, 'src:resources.resource': 69, 'samples_ok': 69}

===== /tmp/apk/logs/export.log
source files: ['/tmp/apk/extract/data.unity3d', '/tmp/apk/extract/resources.resource']
# Unity asset export

- Texture2D: 653 files, 64.1MB
- Sprite: 2185 files, 48.3MB
- AudioClip: 69 files, 47.6MB
- Font: 1 files, 0.0B

===== /tmp/apk/logs/gallery.log
assets found: 2587
# Asset tham chiếu — WindWings 1.3.118

- Tổng asset: **2587**  (148.5MB)
- Contact sheet: **47** file trong [`contact-sheets/`](contact-sheets/)
- Ảnh gốc full-size: artifact `windwings-analysis` (mục `/tmp/apk/unity/export`)
  và draft release `windwings-assets-1.3.118`.

## Nhóm asset

| nhóm | số lượng | mô tả | contact sheet |
|---|---:|---|---|
| `unclassified` | 1554 | Sprite không rõ nguồn (xem cột `atlas`) | [25 sheet](contact-sheets/unclassified-01.jpg) |
| `atlas` | 411 | Texture atlas gốc (UI + nhân vật gộp) | [7 sheet](contact-sheets/atlas-01.jpg) |
| `background` | 142 | Nền, tinh vân, hành tinh | [3 sheet](contact-sheets/background-01.jpg) |
| `fx` | 87 | Hiệu ứng, nổ, trail | [2 sheet](contact-sheets/fx-01.jpg) |
| `ui` | 87 | UI: icon, nút, panel, khung | [2 sheet](contact-sheets/ui-01.jpg) |
| `bullet` | 77 | Đạn, laser, tên lửa | [2 sheet](contact-sheets/bullet-01.jpg) |
| `audio` | 69 | Âm thanh | — |
| `ships` | 50 | Tàu người chơi (sprite id = ship id) | [1 sheet](contact-sheets/ships-01.jpg) |
| `enemy` | 36 | Enemy thường | [1 sheet](contact-sheets/enemy-01.jpg) |
sheets: 47, audio: 69

===== /tmp/apk/logs/probe.log
| SpriteAtlas | 66 |
| TextAsset | 64 |
| CanvasRenderer | 32 |
| BoxCollider | 7 |
| Camera | 6 |
| Canvas | 6 |
| PreloadData | 5 |
| AudioListener | 4 |
| RenderSettings | 4 |
| LightmapSettings | 4 |
| NavMeshSettings | 4 |
| Mesh | 2 |
| PlayerSettings | 1 |
| InputManager | 1 |
| TagManager | 1 |
| AudioManager | 1 |
| ScriptMapper | 1 |
| MonoManager | 1 |
| GraphicsSettings | 1 |
| TimeManager | 1 |
| DelayedCallManager | 1 |
| PhysicsManager | 1 |
| BuildSettings | 1 |
| QualitySettings | 1 |
| ResourceManager | 1 |

===== /tmp/apk/logs/text.log
source files: ['/tmp/apk/extract/data.unity3d', '/tmp/apk/extract/resources.resource']
exported 64 text assets, 1.2MB

===== /tmp/apk/logs/unity_data.log
| `Sub_Item` | 702 | 702 |
| `Wave` | 686 | 686 |
| `Gun_Attack` | 458 | 458 |
| `MapController` | 396 | 396 |
| `Shop_Cell` | 315 | 315 |
| `Stage_Behaviour` | 299 | 299 |
| `Boss_BodyPhysics` | 251 | 251 |
| `Bullet_Linearly` | 186 | 186 |
| `Boss4_ExplosionTimer` | 155 | 155 |
| `GridLayoutManager` | 133 | 133 |
| `Player19Laser` | 120 | 120 |
| `SoundClip` | 92 | 92 |
| `SkeletonDataAsset` | 27 | 27 |
| `LanguageAssets` | 19 | 19 |
| `Tech_Ability_Data` | 6 | 6 |
| `RankManager` | 3 | 3 |
| `DataShopPack` | 2 | 2 |
| `Data_Players` | 2 | 2 |
| `Bullet_SineWave` | 2 | 2 |
| `GP_Datas` | 1 | 1 |
| `TMP_ColorGradient` | 1 | 1 |
| `Data_Items` | 1 | 1 |
| `Data_Boss` | 1 | 1 |
| `TMP_StyleSheet` | 1 | 1 |
errors: {'script': 1}

===== /tmp/apk/logs/wave.log
# Wave composition (campaign maps)

- waves: **282**
- spawners: **11095**
- typetree backend: **AssetStudio**

- lỗi đọc: 1 object

## Spawn type

| type | số spawner |
|---|---:|
| `point_range` | 16498 |
| `point` | 4199 |
| `path` | 1688 |
| `special` | 686 |
| `boss` | 686 |

## Enemy prefab xuất hiện nhiều nhất

| prefab | số spawner dùng |
|---|---:|
| `CB-30003` | 4793 |
| `CB-30015` | 3740 |
| `CB-30024` | 3646 |

```

## Audio diagnose
```
{
 "stats": {
  "clips": 69,
  "has_resource": 69,
  "res_bytes": 5105184,
  "src:resources.resource": 69,
  "samples_ok": 69
 },
 "clips": [
  {
   "path_id": 1689,
   "name": "B\u1eafn \u0110\u1ea1n D\u00ednh Tr\u00ean M\u00e0n H\u00ecnh",
   "keys": [
    "m_Ambisonic",
    "m_BitsPerSample",
    "m_Channels",
    "m_CompressionFormat",
    "m_Frequency",
    "m_IsTrackerFormat",
    "m_Legacy3D",
    "m_Length",
    "m_LoadInBackground",
    "m_LoadType",
    "m_Name",
    "m_PreloadAudioData",
    "m_Resource",
    "m_SubsoundIndex"
   ],
   "has_resource": true,
   "streamed": null,
   "size_bytes": null,
   "samples": 1,
   "saved": "B\u1eafn_\u0110\u1ea1n_D\u00ednh_Tr\u00ean_M\u00e0n_H\u00ecnh_B\u1eafn_\u0110\u1ea1n_D\u00ednh_Tr\u00ean_M\u00e0n_H\u00ecnh.wav.wav",
   "error": null,
   "resource": {
    "m_Source": "resources.resource",
    "m_Offset": 0,
    "m_Size": 6720
   }
  },
  {
   "path_id": 1690,
   "name": "\u0110\u1ecbch \u0110\u1ea5t \u0110\u1ecf B\u1eafn",
   "keys": [
    "m_Ambisonic",
    "m_BitsPerSample",
    "m_Channels",
    "m_CompressionFormat",
    "m_Frequency",
    "m_IsTrackerFormat",
    "m_Legacy3D",
    "m_Length",
    "m_LoadInBackground",
    "m_LoadType",
    "m_Name",
    "m_PreloadAudioData",
    "m_Resource",
    "m_SubsoundIndex"
   ],
   "has_resource": true,
   "streamed": null,
   "size_bytes": null,
   "samples": 1,
   "saved": "\u0110\u1ecbch_\u0110\u1ea5t_\u0110\u1ecf_B\u1eafn_\u0110\u1ecbch_\u0110\u1ea5t_\u0110\u1ecf_B\u1eafn.wav.wav",
   "error": null,
   "resource": {
    "m_Source": "resources.resource",
    "m_Offset": 6720,
    "m_Size": 6080
   }
  },
  {
   "path_id": 1691,
   "name": "Sfx_Defeat",
   "keys": [
    "m_Ambisonic",
    "m_BitsPerSample",
    "m_Channels",
    "m_CompressionFormat",
    "m_Frequency",
    "m_IsTrackerFormat",
    "m_Legacy3D",
    "m_Length",
    "m_LoadInBackground",
    "m_LoadType",
    "m_Name",
    "m_PreloadAudioData",
    "m_Resource",
    "m_SubsoundIndex"
   ],
   "has```
