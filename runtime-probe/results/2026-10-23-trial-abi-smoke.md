# Kết quả probe thật — trial, 23/10/2026

Nguyên văn comment CI của lượt chạy `39925095796` (job `ramus device probe`, session
`be4d1f5c-…`), giữ lại vì artifact của GitHub Actions không tải được từ môi trường này
(`gh run download` → EOF từ blob storage).

Bối cảnh: APK **không** chứa `RamusBridge.dll`, nên lượt này chạy với
`allow_no_bridge: true` + `force_trial: true` + `strict: false` — tức chỉ trả lời được
"app có khởi động trên thiết bị không", không đọc được `/scene` hay `/statics`.

---
# Runtime probe — abi-smoke

- **verdict:** `bridge-unreachable`
- **mode:** `trial` (anonymous trial — no adb)
- **transport:** `none` (none)
- **started:** 2026-10-23T08:31:39.485Z
- **session:** `c646657b-4ff0-430e-ad5b-5f34d1004459`
- **trial expires:** 2026-10-23T08:46:20.079Z

| metric | value |
| --- | --- |
| scene | `—` |
| fps | — |
| avg / max frame | — / — ms |
| frame count | — |
| uptime | — s |
| unity | `—` |
| platform | `—` |
| timeScale | — |
| root objects | 0 |
| objects named *Sub* | — |
| in-game log lines | 0 |
| logcat RAMUSB lines | 0 |

## Artifacts

- `screen-00.jpg`
- `screen-01.jpg`
- `summary.json` — full payloads (health, scene, hierarchy, logs)

## Did the app start?

| signal | seen in logcat |
| --- | --- |
| Unity banner | no |
| il2cpp | no |
| package mentioned | no |
| native load failure | no |
| fatal exception | no |
| activity started (Displayed/Start proc) | no |

app launch: ok
```
{
  "launched": "com.Wind.wings.Space.Shooter",
  "gen": 4,
  "next": "the screen changed — re-snapshot before acting (older refs are stale)"
}
```

| ui snapshot | value |
| --- | --- |
| before | 1466 B · packages: `—` · mentions app: no · looks like launcher: no |

<details><summary>logcat --filter package — 0 line(s)</summary>

```
```
</details>

<details><summary>logcat --filter unity — 0 line(s)</summary>

```
```
</details>

<details><summary>logcat --filter androidRuntime — 10 line(s)</summary>

```
08:33:16 system D/AndroidRuntime: >>>>>> START com.android.internal.os.RuntimeInit uid 2000 <<<<<<
08:33:16 system I/AndroidRuntime: Using default boot image
08:33:16 system I/AndroidRuntime: Leaving lock profiling enabled
08:33:16 system D/AndroidRuntime: Calling main entry com.android.commands.uiautomator.Launcher
08:33:17 system D/AndroidRuntime: Shutting down VM
08:33:18 system D/AndroidRuntime: >>>>>> START com.android.internal.os.RuntimeInit uid 2000 <<<<<<
08:33:18 system I/AndroidRuntime: Using default boot image
08:33:18 system I/AndroidRuntime: Leaving lock profiling enabled
08:33:19 system D/AndroidRuntime: Calling main entry com.android.commands.uiautomator.Launcher
08:33:20 system D/AndroidRuntime: Shutting down VM
```
</details>

<details><summary>logcat evidence — 500 line(s), 57408 B</summary>

tag histogram:
```
  140  FastPrintWriter
  118  AconfigPackage
   42  AccessibilityUserState
   24  WifiThroughputPredictor
   21  SatelliteController
   18  binder
   13  app_process
   12  AccessibilityManagerService
    9  WifiScoreCard
    7  AndroidRuntime
    7  WifiClientModeImpl
    6  nativeloader
```

first 6 lines:
```
08:33:16 system W/app_process: Unexpected CPU variant for x86: x86_64.
08:33:16 system W/app_process: Known variants: atom, sandybridge, silvermont, goldmont, goldmont-plus, goldmont-without-sha-xsaves, tremont, kabylake, alderlake, pantherlake, default
08:33:16 system W/app_process: ClassLoaderContext shared library size mismatch. Expected=2, found=0 (PCL[]{PCL[/system/framework/android.test.base.jar*736588042]#PCL[/system/framework/android.test.moc
08:33:16 system W/app_process: ClassLoaderContext classpath size mismatch. expected=0, found=1 (PCL[]{PCL[/system/framework/android.test.runner.jar*805256125]{PCL[/system/framework/android.test.base.j
08:33:16 system D/nativeloader: Load libframework-connectivity-tiramisu-jni.so using APEX ns com_android_tethering for caller /apex/com.android.tethering/javalib/framework-connectivity-t.jar: ok
08:33:16 system D/AndroidRuntime: Calling main entry com.android.commands.uiautomator.Launcher
```
last 25 lines:
```
08:33:23 system D/SatelliteController: isSatelliteAttachSupportedViaConfigupdater: return null (satelliteConfig is null)
08:33:23 system D/SatelliteController: getSatellitePerPlmnConfiguration: invalid subId or not supported via carrier.
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectType: config: null
08:33:23 system D/TelephonyConfigUpdateInstallReceiver: getConfigParser: domain=satellite
08:33:23 system V/SatelliteController: satelliteConfigParser is not ready
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectTypeViaConfigUpdater: return null (satelliteConfig is null)
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectType: Falling back to global carrier config connect type: 0
08:33:23 system D/TelephonyConfigUpdateInstallReceiver: getConfigParser: domain=satellite
08:33:23 system V/SatelliteController: satelliteConfigParser is not ready
08:33:23 system D/SatelliteController: isSatelliteAttachSupportedViaConfigupdater: return null (satelliteConfig is null)
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectType: Checking connect type from PLMN config for subId: 1
08:33:23 system D/TelephonyConfigUpdateInstallReceiver: getConfigParser: domain=satellite
08:33:23 system V/SatelliteController: satelliteConfigParser is not ready
08:33:23 system D/SatelliteController: isSatelliteAttachSupportedViaConfigupdater: return null (satelliteConfig is null)
08:33:23 system D/SatelliteController: getSatellitePerPlmnConfiguration: invalid subId or not supported via carrier.
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectType: config: null
08:33:23 system D/TelephonyConfigUpdateInstallReceiver: getConfigParser: domain=satellite
08:33:23 system V/SatelliteController: satelliteConfigParser is not ready
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectTypeViaConfigUpdater: return null (satelliteConfig is null)
08:33:23 system D/SatelliteController: getCarrierRoamingNtnConnectType: Falling back to global carrier config connect type: 0
08:33:23 system D/TelephonyConfigUpdateInstallReceiver: getConfigParser: domain=satellite
08:33:23 system V/SatelliteController: satelliteConfigParser is not ready
08:33:23 system D/SatelliteController: isSatelliteAttachSupportedViaConfigupdater: return null (satelliteConfig is null)
08:33:23 system I/adbd: adbd service requested 'shell,v2,raw:settings get global private_dns_mode'
08:33:23 system I/adbd: adbd service requested 'shell,v2,raw:dumpsys activity activities | grep topResumedActivity= ; true'
```
</details>

> **Not proven:** no Unity or package line appeared in the last 500 logcat lines.
> That is consistent with the game never starting, but it does not identify the
> cause. Candidates, none confirmed by this run:
>
> - ABI mismatch — this build ships `lib/arm64-v8a` only and Ramus documents
>   x86_64 emulators (ABI in this APK: `arm64-v8a`);
> - the launcher never started the activity (`ramus app launch` is best effort);
> - the process died before Unity initialised, with the crash outside the captured
>   window — `logcat` only returns the last 500 lines.
>
> To decide it, capture `adb logcat` on a device that has adb, or read
> `logcat.txt` in the artifact in full.

## Notes

- anonymous trial: no adb tunnel, so the bridge is read through logcat mirrors
- trial credential expires at 2026-10-23T08:46:20.079Z
- bridge HTTP not reachable at http://127.0.0.1:8080 (expected on a trial: no adb) — reading logcat
- sent `app launch` because no bridge line appeared yet

## Errors

- no RAMUSB logcat line found: is RamusBridge.dll inside this APK? see runtime-probe/README.md

---

Generated by `runtime-probe/` (embedded C# bridge + `ramus-probe.mjs`).

<details><summary>APK inventory</summary>

```
source:      windwings.xapk (142125649 bytes)
sha256:      f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e
fetched at:  2026-10-23T08:31:10Z

base.apk                                                117158131 B  manifest=1  abis=arm64-v8a                unitydata=11

kind:        xapk
base:        .ci/apk/base.apk (117 MB)
abis:        arm64-v8a   (x86_64 present: false)
install:     single APK
split marks: none
bridge:      no 
merge rc:    java exit 0; lib entries: 19 (need: 1); signed (java exit 0)   output: 117055794 B
  00.747 I: [MERGE] Buffering compress changed files ...
  03.648 I: [MERGE] Writing files: 1361
  03.828 I: [MERGE] Writing signature block ...
  03.861 I: [MERGE] Saved to: /tmp/tmp.JQ9kP9s6fp/universal.apk
splits:      none
package:     com.Wind.wings.Space.Shooter
```

</details>
