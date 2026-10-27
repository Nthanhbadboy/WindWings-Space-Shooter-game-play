<!-- runtime-probe -->
# Runtime probe — skipped: the APK has no bridge

Searched `base.apk` and every split for `RamusBridge.dll` (plus `BepInEx/`, `Mods/`).
Nothing found, so a Ramus session would only burn a credential and 4–5 minutes to
reproduce the same `bridge-unreachable` verdict.

**Caveat, so this is not mistaken for proof:** FusionCore / NextBep inject into an
installed game and load plugins from the **launcher app's own storage**, not from the
game APK. If that is how you load the bridge, absence here does not mean it is missing.
In that case run with `allow_no_bridge: true`.

Build and embed the plugin first:

\`\`\`bash
# produces RamusBridge.dll for your loader (see runtime-probe/README.md §3)
./.github/scripts/build-bridge.sh --out dist
# → dist/bepinex6/RamusBridge.dll, dist/melon/RamusBridge.dll, dist/bepinex5/RamusBridge.dll
\`\`\`

Then install it into the build you upload (BepInEx: `BepInEx/plugins/`;
MelonLoader: `Mods/`) and re-run. To test only does the game start on this
  echo device in the meantime, run with `allow_no_bridge: true`.

<details><summary>APK inventory</summary>

\`\`\`
source:      windwings.xapk (142125649 bytes)
sha256:      f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e
fetched at:  2026-10-25T09:44:20Z

base.apk                                                117158131 B  manifest=1  abis=arm64-v8a                unitydata=11

kind:        xapk
base:        .ci/apk/base.apk (117 MB)
abis:        arm64-v8a   (x86_64 present: false)
install:     single APK
split marks: none
bridge:      no 
merge rc:    java exit 0; lib entries: 19 (need: 1); signed (java exit 0)   output: 117055794 B
  00.920 I: [MERGE] Buffering compress changed files ...
  03.378 I: [MERGE] Writing files: 1361
  03.543 I: [MERGE] Writing signature block ...
  03.604 I: [MERGE] Saved to: /tmp/tmp.ZbveqwMIYJ/universal.apk
splits:      none
package:     com.Wind.wings.Space.Shooter
\`\`\`
</details>
