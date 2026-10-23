# Pipeline diagnostics

## Unity payload
```
total 137M
-rw-r--r-- 1 runner runner   11K Oct 23 03:26 RuntimeInitializeOnLoads.json
-rw-r--r-- 1 runner runner  3.9K Oct 23 03:26 ScriptingAssemblies.json
-rw-r--r-- 1 runner runner   120 Oct 23 03:26 _listing.txt
-rw-r--r-- 1 runner runner   61M Oct 23 03:26 data.unity3d
-rw-r--r-- 1 runner runner  8.3M Oct 23 03:26 global-metadata.dat
-rw-r--r-- 1 runner runner   45M Oct 23 03:26 libil2cpp.so
-rw-r--r-- 1 runner runner   17M Oct 23 03:26 libunity.so
-rw-r--r-- 1 runner runner 1023K Oct 23 03:26 resources.arsc
-rw-r--r-- 1 runner runner  4.9M Oct 23 03:26 resources.resource
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
total 364
drwxr-xr-x 3 runner runner   4096 Oct 23 03:26 .
drwxr-xr-x 5 runner runner   4096 Oct 23 03:26 ..
-rw-r--r-- 1 runner runner   2190 Oct 23 03:27 INDEX.md
-rw-r--r-- 1 runner runner   7275 Oct 23 03:27 audio-index.csv
drwxr-xr-x 2 runner runner   4096 Oct 23 03:27 contact-sheets
-rw-r--r-- 1 runner runner 146648 Oct 23 03:27 manifest.csv
-rw-r--r-- 1 runner runner 191560 Oct 23 03:27 sprites-index.csv
-rw-r--r-- 1 runner runner   4634 Oct 23 03:27 stats.json

docs/assets/contact-sheets:
total 7400
drwxr-xr-x 2 runner runner   4096 Oct 23 03:27 .
drwxr-xr-x 3 runner runner   4096 Oct 23 03:26 ..
-rw-r--r-- 1 runner runner 233344 Oct 23 03:27 atlas-01.jpg
-rw-r--r-- 1 runner runner 326577 Oct 23 03:27 atlas-02.jpg
-rw-r--r-- 1 runner runner  14242 Oct 23 03:27 atlas-03.jpg
-rw-r--r-- 1 runner runner 177064 Oct 23 03:27 background-01.jpg
-rw-r--r-- 1 runner runner 142920 Oct 23 03:27 background-02.jpg
-rw-r--r-- 1 runner runner 166141 Oct 23 03:27 bosses-01.jpg
-rw-r--r-- 1 runner runner 175411 Oct 23 03:27 bullet-01.jpg
-rw-r--r-- 1 runner runner  13861 Oct 23 03:27 bullet-02.jpg
-rw-r--r-- 1 runner runner  56140 Oct 23 03:27 drones-01.jpg
-rw-r--r-- 1 runner runner 104215 Oct 23 03:27 enemy-01.jpg
-rw-r--r-- 1 runner runner  31031 Oct 23 03:27 font-01.jpg
-rw-r--r-- 1 runner runner 204312 Oct 23 03:27 fx-01.jpg
-rw-r--r-- 1 runner runner  56927 Oct 23 03:27 fx-02.jpg
-rw-r--r-- 1 runner runner  16007 Oct 23 03:27 items-01.jpg
-rw-r--r-- 1 runner runner 125812 Oct 23 03:27 ships-01.jpg
```

## Step logs (tail)
```
===== /tmp/apk/logs/anim_curves.log
AnimationClip: 791 đọc được, 0 có keyframe, 0 keyframe -> datas/anim_clips.json.gz

===== /tmp/apk/logs/animator_joins.log
ParticleSystem: 4845, nối được prefab gốc 4839 -> datas/particle_systems.csv.gz
Animator: 5792, nối được prefab gốc 5686, tên controller 5603 -> datas/animator_map.csv.gz
controller phổ biến: [('Box_Gift (0)', 936), ('Body', 790), ('Parent', 766), ('Popup_Network', 663), ('A', 516), ('BossObject', 251), ('Tail', 156), ('Star Fill', 135)]

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

===== /tmp/apk/logs/audio_map.log
# Audio map — sound id → file

> **Kết luận tạm thời.** Join theo `path_id`; asset name lấy từ manifest export.

- tiếng trong registry (`SoundClip`): **92**
- resolve được ra file: **92**
- nhóm: sfx 83, bgm 9

| sound id | clip | giây | file |
|---|---|---:|---|
| `Bgm_Boss1` | Bgm_Boss 1 | 32.26 | `AudioClip/Bgm_Boss_1__Bgm_Boss_1.wav` |
| `Bgm_Boss2` | Bgm_Boss 1 | 32.26 | `AudioClip/Bgm_Boss_1__Bgm_Boss_1.wav` |
| `Bgm_Game1` | Action Dynamic Track #2 1 MP3   | 80.09 | `AudioClip/Action_Dynamic_Track_2_1_MP3___Action_Dynamic_Track_2_1_MP3_.wav` |
| `Bgm_Game2` | Energy Rock Track #2 (looped) 1 | 71.58 | `AudioClip/Energy_Rock_Track_2_looped_1__Energy_Rock_Track_2_looped_1.wav` |
unresolved: 0

===== /tmp/apk/logs/consts.log

===== /tmp/apk/logs/export.log
source files: ['/tmp/apk/extract/data.unity3d', '/tmp/apk/extract/resources.resource']
# Unity asset export

- Texture2D: 653 files, 64.1MB
- Sprite: 2185 files, 48.3MB
- AudioClip: 69 files, 47.6MB
- Font: 1 files, 0.0B

===== /tmp/apk/logs/formula_trace.log
425 method, 223 bl giải đúng tên -> datas/formula_traces.json.gz

===== /tmp/apk/logs/gallery.log
assets found: 2197
# Asset tham chiếu — WindWings 1.3.118

- Tổng asset: **2197**  (133.6MB)
- Contact sheet: **42** file trong [`contact-sheets/`](contact-sheets/)
- Ảnh gốc full-size: artifact `windwings-analysis` (mục `/tmp/apk/unity/export`)
  và draft release `windwings-assets-1.3.118`.

## Nhóm asset

| nhóm | số lượng | mô tả | contact sheet |
|---|---:|---|---|
| `unclassified` | 1554 | Sprite không rõ nguồn (xem cột `atlas`) | [25 sheet](contact-sheets/unclassified-01.jpg) |
| `atlas` | 132 | Texture atlas gốc (UI + nhân vật gộp) | [3 sheet](contact-sheets/atlas-01.jpg) |
| `background` | 109 | Nền, tinh vân, hành tinh | [2 sheet](contact-sheets/background-01.jpg) |
| `fx` | 80 | Hiệu ứng, nổ, trail | [2 sheet](contact-sheets/fx-01.jpg) |
| `ui` | 73 | UI: icon, nút, panel, khung | [2 sheet](contact-sheets/ui-01.jpg) |
| `audio` | 69 | Âm thanh | — |
| `bullet` | 67 | Đạn, laser, tên lửa | [2 sheet](contact-sheets/bullet-01.jpg) |
| `bosses` | 32 | Boss theo wave (idWave) | [1 sheet](contact-sheets/bosses-01.jpg) |
| `enemy` | 31 | Enemy thường | [1 sheet](contact-sheets/enemy-01.jpg) |
sheets: 42, audio: 69

===== /tmp/apk/logs/prefab_joins.log
Boss_BodyPhysics.m_GameObject: hit 251
Enemy_Controller.m_GameObject: hit 981
Enemy_Movement.parentRotate: hit 558
Gun_Attack.m_GameObject: hit 458
Stage_Behaviour.bossObj: hit 250
Wave.endPoint: hit 686
Wave.startPoint: hit 686
3870 dòng -> datas/prefab_joins.csv.gz

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

===== /tmp/apk/logs/spine.log
typetree ready: AssetStudio
TextAssets: 64, SkeletonDataAssets: 27
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

===== /tmp/apk/logs/spine_anim.log
27 rig, 185 animation, 12274 keyframe, 21 event -> datas/spine_anim.json.gz (0.04 MB gz)

===== /tmp/apk/logs/text.log
source files: ['/tmp/apk/extract/data.unity3d', '/tmp/apk/extract/resources.resource']
exported 64 text assets, 1.2MB

===== /tmp/apk/logs/ui_index.log
23711 file, 114 màn, 3,834,253 node, 483,505 dòng text/key -> datas/ui_screens.json.gz

===== /tmp/apk/logs/ui_layout.log
typetree generator ready: AssetStudio
class map: 125452 MonoBehaviours
screen candidates: 793
skipped: {'duplicate (class, root)': 50}
# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **743**
- tổng node: **105985**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (50)

## Component gặp nhiều nhất

| class | số node |
|---|---:|

===== /tmp/apk/logs/unity_data.log
| `Enemy_Destroy` | 971 | 971 |
| `Enemy_Appear` | 914 | 914 |
| `Enemy_Hp_Bar` | 909 | 909 |
| `AirFree_Spawner` | 885 | 885 |
| `MeteoriteGenerator` | 852 | 852 |
| `Item_Movement` | 702 | 702 |
| `Sub_Item` | 702 | 702 |
| `Enemy_Burned` | 695 | 695 |
| `Wave` | 686 | 686 |
| `Gun_Attack` | 458 | 458 |
| `MapController` | 396 | 396 |
| `Enemy_LookAtPlayer` | 391 | 391 |
| `Shop_Cell` | 315 | 315 |
| `Stage_Behaviour` | 299 | 299 |
| `Boss_BodyPhysics` | 251 | 251 |
| `Enemy_CameraVibrate` | 241 | 241 |
| `Bullet_Linearly` | 186 | 186 |
| `Boss4_ExplosionTimer` | 155 | 155 |
| `Enemy_Stun` | 140 | 140 |
| `GridLayoutManager` | 133 | 133 |
| `Player19Laser` | 120 | 120 |
| `SoundClip` | 92 | 92 |
| `Enemy_Sync_Attack` | 72 | 72 |
| `Enemy_OffObjectWhenDestroy` | 56 | 56 |
errors: {'script': 1}

===== /tmp/apk/logs/wave.log
# Wave composition (campaign maps)

- waves: **282**
- spawners: **11092**
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
