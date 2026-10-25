# Pipeline diagnostics

## Unity payload
```
total 137M
-rw-r--r-- 1 runner runner   11K Oct 25 13:41 RuntimeInitializeOnLoads.json
-rw-r--r-- 1 runner runner  3.9K Oct 25 13:41 ScriptingAssemblies.json
-rw-r--r-- 1 runner runner   120 Oct 25 13:41 _listing.txt
-rw-r--r-- 1 runner runner   61M Oct 25 13:41 data.unity3d
-rw-r--r-- 1 runner runner  8.3M Oct 25 13:41 global-metadata.dat
-rw-r--r-- 1 runner runner   45M Oct 25 13:41 libil2cpp.so
-rw-r--r-- 1 runner runner   17M Oct 25 13:41 libunity.so
-rw-r--r-- 1 runner runner 1023K Oct 25 13:41 resources.arsc
-rw-r--r-- 1 runner runner  4.9M Oct 25 13:41 resources.resource
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
/tmp/apk/unity/export/Sprite             30 files 1.1M
/tmp/apk/unity/export/Texture2D          594 files 49M
/tmp/apk/unity/export/AudioClip          0 files 
/tmp/apk/unity/audio                     0 files 
```

## Asset gallery
```
docs/assets:
total 5176
drwxr-xr-x 3 runner runner    4096 Oct 25 13:41 .
drwxr-xr-x 6 runner runner    4096 Oct 25 13:41 ..
-rw-r--r-- 1 runner runner    4982 Oct 25 13:41 INDEX.md
-rw-r--r-- 1 runner runner    7275 Oct 25 13:41 audio-index.csv
drwxr-xr-x 2 runner runner    4096 Oct 25 13:41 contact-sheets
-rw-r--r-- 1 runner runner 1802879 Oct 25 13:41 font-browser.html
-rw-r--r-- 1 runner runner  146648 Oct 25 13:41 manifest.csv
-rw-r--r-- 1 runner runner 1657293 Oct 25 13:41 pack-browser-v2.html
-rw-r--r-- 1 runner runner 1456125 Oct 25 13:41 pack-browser.html
-rw-r--r-- 1 runner runner  191560 Oct 25 13:41 sprites-index.csv
-rw-r--r-- 1 runner runner    4634 Oct 25 13:41 stats.json

docs/assets/contact-sheets:
total 7400
drwxr-xr-x 2 runner runner   4096 Oct 25 13:41 .
drwxr-xr-x 3 runner runner   4096 Oct 25 13:41 ..
-rw-r--r-- 1 runner runner 233344 Oct 25 13:41 atlas-01.jpg
-rw-r--r-- 1 runner runner 326577 Oct 25 13:41 atlas-02.jpg
-rw-r--r-- 1 runner runner  14242 Oct 25 13:41 atlas-03.jpg
-rw-r--r-- 1 runner runner 177064 Oct 25 13:41 background-01.jpg
-rw-r--r-- 1 runner runner 142920 Oct 25 13:41 background-02.jpg
-rw-r--r-- 1 runner runner 166141 Oct 25 13:41 bosses-01.jpg
-rw-r--r-- 1 runner runner 175411 Oct 25 13:41 bullet-01.jpg
-rw-r--r-- 1 runner runner  13861 Oct 25 13:41 bullet-02.jpg
-rw-r--r-- 1 runner runner  56140 Oct 25 13:41 drones-01.jpg
-rw-r--r-- 1 runner runner 104215 Oct 25 13:41 enemy-01.jpg
-rw-r--r-- 1 runner runner  31031 Oct 25 13:41 font-01.jpg
-rw-r--r-- 1 runner runner 204312 Oct 25 13:41 fx-01.jpg
```

## Step logs (tail)
```
===== /tmp/apk/logs/export.log

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

```

## Audio diagnose
```
```
