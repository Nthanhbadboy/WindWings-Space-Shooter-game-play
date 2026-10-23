# Runtime probe — re-startup-executable-fix

- **verdict:** `bridge-unreachable`
- **mode:** `trial` (anonymous trial — no adb)
- **transport:** `none` (none)
- **started:** 2026-10-23T08:52:51.549Z
- **session:** `b2163f36-c9c0-4ebf-81fe-623a56825331`
- **trial expires:** 2026-10-23T09:07:33.554Z

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
  "gen": 3,
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
08:54:24 system D/AndroidRuntime: >>>>>> START com.android.internal.os.RuntimeInit uid 2000 <<<<<<
08:54:24 system I/AndroidRuntime: Using default boot image
08:54:24 system I/AndroidRuntime: Leaving lock profiling enabled
08:54:24 system D/AndroidRuntime: Calling main entry com.android.commands.uiautomator.Launcher
08:54:25 system D/AndroidRuntime: Shutting down VM
08:54:27 system D/AndroidRuntime: >>>>>> START com.android.internal.os.RuntimeInit uid 2000 <<<<<<
08:54:27 system I/AndroidRuntime: Using default boot image
08:54:27 system I/AndroidRuntime: Leaving lock profiling enabled
08:54:27 system D/AndroidRuntime: Calling main entry com.android.commands.uiautomator.Launcher
08:54:28 system D/AndroidRuntime: Shutting down VM
```
</details>

<details><summary>logcat evidence — 500 line(s), 56264 B</summary>

tag histogram:
```
  140  FastPrintWriter
  103  AconfigPackage
   42  AccessibilityUserState
   39  libbinder.IPCThreadState
   24  WifiThroughputPredictor
   21  SatelliteController
   12  AccessibilityManagerService
   10  binder
    9  WifiScoreCard
    9  app_process
    7  WifiClientModeImpl
    6  UiAutomation
```

first 6 lines:
```
08:54:24 system I/AconfigPackage: android.telecom.flags is mapped to com.android.telephonycore
08:54:24 system I/AconfigPackage: com.android.internal.telecom.flags is mapped to com.android.telephonycore
08:54:24 system I/AconfigPackage: com.android.telephony.flags is mapped to com.android.telephonycore
08:54:24 system I/AconfigPackage: com.android.media.extractor.flags is mapped to com.android.media
08:54:24 system I/AconfigPackage: com.android.media.metrics.flags is mapped to com.android.media
08:54:24 system I/AconfigPackage: com.android.media.mainline.flags is mapped to com.android.media
```
last 25 lines:
```
08:54:32 system W/FastPrintWriter: at com.android.server.ServiceThread.run(ServiceThread.java:46)
08:54:32 system W/FastPrintWriter: Caused by: android.system.ErrnoException: write failed: EPIPE (Broken pipe)
08:54:32 system W/FastPrintWriter: at libcore.io.Linux.writeBytes(Native Method)
08:54:32 system W/FastPrintWriter: at libcore.io.Linux.write(Linux.java:342)
08:54:32 system W/FastPrintWriter: at libcore.io.ForwardingOs.write(ForwardingOs.java:970)
08:54:32 system W/FastPrintWriter: at libcore.io.BlockGuardOs.write(BlockGuardOs.java:463)
08:54:32 system W/FastPrintWriter: at libcore.io.IoBridge.write(IoBridge.java:646)
08:54:32 system W/FastPrintWriter: ... 25 more
08:54:32 system D/WifiClientModeImpl[527297:wlan0]: updateLinkLayerStatsRssiSpeedFrequencyCapabilities rssi=-50 TxLinkspeed=6 freq=2437 RxLinkSpeed=2
08:54:32 system D/WifiDataStall: tx tput in kbps: 37000
08:54:32 system D/WifiDataStall: rx tput in kbps: 37000
08:54:32 system V/WifiConfigManager: Updating scan detail cache freq=2437 BSSID=02:15:b2:00:00:01 RSSI=-50 for "AndroidWifi"NONE
08:54:32 system D/WifiThroughputPredictor: utilization (LLS) 80 isBluetoothConnected: false final utilization: 80
08:54:32 system D/WifiThroughputPredictor: BW: 0 RSSI: -50 Nss: 1 Mode: 1 symDur: 4000 snrDb 30 bitPerTone: 4500 rate: 54 throughput: 37
08:54:32 system D/WifiThroughputPredictor: utilization (LLS) 80 isBluetoothConnected: false final utilization: 80
08:54:32 system D/WifiThroughputPredictor: BW: 0 RSSI: -50 Nss: 1 Mode: 1 symDur: 4000 snrDb 30 bitPerTone: 4500 rate: 54 throughput: 37
08:54:32 system D/WifiThroughputPredictor: utilization (LLS) 80 isBluetoothConnected: false final utilization: 80
08:54:32 system D/WifiThroughputPredictor: BW: 0 RSSI: -50 Nss: 1 Mode: 1 symDur: 4000 snrDb 30 bitPerTone: 4500 rate: 54 throughput: 37
08:54:32 system D/WifiThroughputPredictor: utilization (LLS) 80 isBluetoothConnected: false final utilization: 80
08:54:32 system D/WifiThroughputPredictor: BW: 0 RSSI: -50 Nss: 1 Mode: 1 symDur: 4000 snrDb 30 bitPerTone: 4500 rate: 54 throughput: 37
08:54:32 system I/HalDevMgr: bestIfaceCreationProposal is null, requestIface=STA, existingIface=[name=wlan0 type=STA]
08:54:32 system D/WifiScoreCard: BSSID update SIGNAL_POLL ID: 1520746878 SSID: "AndroidWifi", BSSID: 02:15:b2:00:00:01, MAC: 02:16:3a:00:00:00, IP: /10.0.2.16, Security type: 0, Supplicant state: COMP
08:54:32 system D/WifiScoreCard: txRate: 1 txSpeed: 6
08:54:32 system D/WifiScoreCard: network update SIGNAL_POLL "AndroidWifi" ID: 2119497376 RSSI -50 txSpeed -1
08:54:32 system D/WifiClientModeImpl[527297:wlan0]: ClientModeImpl$L2ConnectedState screen=on 1 0 "AndroidWifi" 02:15:b2:00:00:01 rssi=-50 f=2437 sc=100 link=6 tx=0.0, 0.0, 0.0 rx=0.0 bcn=0 [on:0 tx:0
```
</details>

streams returned: system=500

> **Transport limitation, not a result.** Every line came from the `system`
> buffer; Unity, ActivityManager and crash reports go to `main`/`crash`.
> With no `main` lines, "no Unity" / "no package" says nothing about the game —
> it only says this transport never looked at the buffer where the game logs.

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
- trial credential expires at 2026-10-23T09:07:33.554Z
- bridge HTTP not reachable at http://127.0.0.1:8080 (expected on a trial: no adb) — reading logcat
- sent `app launch` because no bridge line appeared yet

## Errors

- no RAMUSB logcat line found: is RamusBridge.dll inside this APK? see runtime-probe/README.md

---

Generated by `runtime-probe/` (embedded C# bridge + `ramus-probe.mjs`).
