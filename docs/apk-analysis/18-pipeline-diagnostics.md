# Pipeline diagnostics

## Unity payload
```
total 336M
-rw-r--r-- 1 runner runner   11K Oct 22 20:49 RuntimeInitializeOnLoads.json
-rw-r--r-- 1 runner runner  3.9K Oct 22 20:49 ScriptingAssemblies.json
-rw-r--r-- 1 runner runner   120 Oct 22 20:49 _listing.txt
-rw-r--r-- 1 runner runner   61M Oct 22 20:49 data.unity3d
-rw-r--r-- 1 runner runner  8.3M Oct 22 20:49 global-metadata.dat
-rw-r--r-- 1 runner runner   45M Oct 22 20:49 libil2cpp.so
-rw-r--r-- 1 runner runner   17M Oct 22 20:49 libunity.so
-rw-r--r-- 1 runner runner  106M Oct 22 20:57 re-libil2cpp.asm
-rw-r--r-- 1 runner runner   17K Oct 22 20:57 re-libil2cpp.evidence.json
-rw-r--r-- 1 runner runner  6.0K Oct 22 20:57 re-libil2cpp.json
-rw-r--r-- 1 runner runner   75K Oct 22 20:58 re-libil2cpp.md
-rw-r--r-- 1 runner runner  872K Oct 22 20:58 re-libil2cpp.pdf
-rw-r--r-- 1 runner runner   92M Oct 22 20:58 re-libunity.asm
-rw-r--r-- 1 runner runner   17K Oct 22 20:58 re-libunity.evidence.json
-rw-r--r-- 1 runner runner  7.8K Oct 22 20:58 re-libunity.json
-rw-r--r-- 1 runner runner   49K Oct 22 20:58 re-libunity.md
-rw-r--r-- 1 runner runner  699K Oct 22 20:58 re-libunity.pdf
-rw-r--r-- 1 runner runner 1023K Oct 22 20:49 resources.arsc
-rw-r--r-- 1 runner runner  4.9M Oct 22 20:49 resources.resource
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
/tmp/apk/unity/export/Sprite             0 files 
/tmp/apk/unity/export/Texture2D          0 files 
/tmp/apk/unity/export/AudioClip          0 files 
/tmp/apk/unity/audio                     0 files 
```

## Asset gallery
```
docs/assets:
total 320
drwxr-xr-x 3 runner runner   4096 Oct 22 20:49 .
drwxr-xr-x 5 runner runner   4096 Oct 22 20:49 ..
-rw-r--r-- 1 runner runner   1953 Oct 22 20:49 INDEX.md
drwxr-xr-x 2 runner runner   4096 Oct 22 20:49 contact-sheets
-rw-r--r-- 1 runner runner 130193 Oct 22 20:49 manifest.csv
-rw-r--r-- 1 runner runner 168842 Oct 22 20:49 sprites-index.csv
-rw-r--r-- 1 runner runner   4695 Oct 22 20:49 stats.json

docs/assets/contact-sheets:
total 8740
drwxr-xr-x 2 runner runner   4096 Oct 22 20:49 .
drwxr-xr-x 3 runner runner   4096 Oct 22 20:49 ..
-rw-r--r-- 1 runner runner 275298 Oct 22 20:49 atlas-01.jpg
-rw-r--r-- 1 runner runner 252528 Oct 22 20:49 atlas-02.jpg
-rw-r--r-- 1 runner runner 222282 Oct 22 20:49 atlas-03.jpg
-rw-r--r-- 1 runner runner 225186 Oct 22 20:49 atlas-04.jpg
-rw-r--r-- 1 runner runner 205562 Oct 22 20:49 atlas-05.jpg
-rw-r--r-- 1 runner runner 314050 Oct 22 20:49 atlas-06.jpg
-rw-r--r-- 1 runner runner 119265 Oct 22 20:49 atlas-07.jpg
-rw-r--r-- 1 runner runner 186939 Oct 22 20:49 background-01.jpg
-rw-r--r-- 1 runner runner 171009 Oct 22 20:49 background-02.jpg
-rw-r--r-- 1 runner runner  41576 Oct 22 20:49 background-03.jpg
-rw-r--r-- 1 runner runner 177267 Oct 22 20:49 bosses-01.jpg
-rw-r--r-- 1 runner runner 171755 Oct 22 20:49 bullet-01.jpg
-rw-r--r-- 1 runner runner  38495 Oct 22 20:49 bullet-02.jpg
-rw-r--r-- 1 runner runner 110716 Oct 22 20:49 drones-01.jpg
-rw-r--r-- 1 runner runner 119597 Oct 22 20:49 enemy-01.jpg
-rw-r--r-- 1 runner runner  31031 Oct 22 20:49 font-01.jpg
```

## Audio diagnose
```
```
