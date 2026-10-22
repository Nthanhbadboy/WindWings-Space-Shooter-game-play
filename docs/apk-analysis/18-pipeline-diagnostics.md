# Pipeline diagnostics

## Unity payload
```
total 336M
-rw-r--r-- 1 runner runner   11K Oct 22 20:36 RuntimeInitializeOnLoads.json
-rw-r--r-- 1 runner runner  3.9K Oct 22 20:36 ScriptingAssemblies.json
-rw-r--r-- 1 runner runner   120 Oct 22 20:36 _listing.txt
-rw-r--r-- 1 runner runner   61M Oct 22 20:36 data.unity3d
-rw-r--r-- 1 runner runner  8.3M Oct 22 20:36 global-metadata.dat
-rw-r--r-- 1 runner runner   45M Oct 22 20:36 libil2cpp.so
-rw-r--r-- 1 runner runner   17M Oct 22 20:36 libunity.so
-rw-r--r-- 1 runner runner  106M Oct 22 20:46 re-libil2cpp.asm
-rw-r--r-- 1 runner runner   17K Oct 22 20:46 re-libil2cpp.evidence.json
-rw-r--r-- 1 runner runner  6.0K Oct 22 20:46 re-libil2cpp.json
-rw-r--r-- 1 runner runner   75K Oct 22 20:47 re-libil2cpp.md
-rw-r--r-- 1 runner runner  872K Oct 22 20:47 re-libil2cpp.pdf
-rw-r--r-- 1 runner runner   92M Oct 22 20:47 re-libunity.asm
-rw-r--r-- 1 runner runner   17K Oct 22 20:47 re-libunity.evidence.json
-rw-r--r-- 1 runner runner  7.8K Oct 22 20:47 re-libunity.json
-rw-r--r-- 1 runner runner   49K Oct 22 20:47 re-libunity.md
-rw-r--r-- 1 runner runner  699K Oct 22 20:47 re-libunity.pdf
-rw-r--r-- 1 runner runner 1023K Oct 22 20:36 resources.arsc
-rw-r--r-- 1 runner runner  4.9M Oct 22 20:36 resources.resource
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
/tmp/apk/unity/export/AudioClip          0 files 4.0K
/tmp/apk/unity/audio                     1 files 56K
```

## Asset gallery
```
docs/assets:
total 320
drwxr-xr-x 3 runner runner   4096 Oct 22 20:38 .
drwxr-xr-x 5 runner runner   4096 Oct 22 20:38 ..
-rw-r--r-- 1 runner runner   1953 Oct 22 20:38 INDEX.md
drwxr-xr-x 2 runner runner   4096 Oct 22 20:38 contact-sheets
-rw-r--r-- 1 runner runner 130193 Oct 22 20:38 manifest.csv
-rw-r--r-- 1 runner runner 168842 Oct 22 20:38 sprites-index.csv
-rw-r--r-- 1 runner runner   4695 Oct 22 20:38 stats.json

docs/assets/contact-sheets:
total 8740
drwxr-xr-x 2 runner runner   4096 Oct 22 20:38 .
drwxr-xr-x 3 runner runner   4096 Oct 22 20:38 ..
-rw-r--r-- 1 runner runner 275298 Oct 22 20:38 atlas-01.jpg
-rw-r--r-- 1 runner runner 252528 Oct 22 20:38 atlas-02.jpg
-rw-r--r-- 1 runner runner 222282 Oct 22 20:38 atlas-03.jpg
-rw-r--r-- 1 runner runner 225186 Oct 22 20:38 atlas-04.jpg
-rw-r--r-- 1 runner runner 205562 Oct 22 20:38 atlas-05.jpg
-rw-r--r-- 1 runner runner 314050 Oct 22 20:38 atlas-06.jpg
-rw-r--r-- 1 runner runner 119265 Oct 22 20:38 atlas-07.jpg
-rw-r--r-- 1 runner runner 186939 Oct 22 20:38 background-01.jpg
-rw-r--r-- 1 runner runner 171009 Oct 22 20:38 background-02.jpg
-rw-r--r-- 1 runner runner  41576 Oct 22 20:38 background-03.jpg
-rw-r--r-- 1 runner runner 177267 Oct 22 20:38 bosses-01.jpg
-rw-r--r-- 1 runner runner 171755 Oct 22 20:38 bullet-01.jpg
-rw-r--r-- 1 runner runner  38495 Oct 22 20:38 bullet-02.jpg
-rw-r--r-- 1 runner runner 110716 Oct 22 20:38 drones-01.jpg
-rw-r--r-- 1 runner runner 119597 Oct 22 20:38 enemy-01.jpg
-rw-r--r-- 1 runner runner  31031 Oct 22 20:38 font-01.jpg
```

## Audio diagnose
```
{
 "stats": {
  "clips": 69,
  "has_resource": 69,
  "res_bytes": 5105184,
  "src:resources.resource": 69,
  "samples_error": 69,
  "converter_error": 69,
  "silent": 69
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
   "samples": 0,
   "saved": null,
   "error": null,
   "resource": {
    "m_Source": "resources.resource",
    "m_Offset": 0,
    "m_Size": 6720
   },
   "samples_error": "ValueError('seek of closed file')",
   "converter_error": "ValueError('seek of closed file')"
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
   "samples": 0,
   "saved": null,
   "error": null,
   "resource": {
    "m_Source": "resources.resource",
    "m_Offset": 6720,
    "m_Size": 6080
   },
   "samples_error": "ValueError('seek of closed file')",
   "converter_error": "ValueError('seek of closed file')"
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
    "m_Resour```
