# 121 — #28 Map `arr=256&depth=2` runtime attempt — `arena/a5a74747-windwings-space-shooter-game-p`

**Status: BLOCKED BEFORE SESSION.** This is not a Map runtime receipt and supplies no Map values. Claim: PR12 comment **6414225859**. The blocker is scoped to one pinned PR14 vehicle run; it is not a repository-wide assertion that no other bridge or runtime evidence exists.

## Measured outcome

PR14 runtime-probe run **40310064929**, head `4cb2828ec5731d68100f7319ac40b48bb34e08c6`, prepared the official XAPK, then stopped at its bridge-presence gate:

| `ramus device probe` step | Outcome |
|---|---|
| Prepare APK | success |
| Gate on bridge presence | success as a workflow gate step; inventory says `bridge: no` |
| Trial-limit check | skipped |
| Pre-session checks | skipped |
| Credentials | skipped |
| Start session | skipped |
| Upload/install, launch, app wait | skipped |
| Probe game state | skipped |
| End session | skipped |

The workflow/job conclusion is `success`, but the live session path did **not** run. Accordingly `Map_Get_Datas.listMapDatas` with `arr=256&depth=2` was **not requested** in this run; `runtime_readback.status=NOT_OBSERVED`, `map_values=null`, and `session_started=false` in the artifact.

The PR12 preflight comment **6411232160**, updated **2026-10-26 10:48:02Z**, records XAPK SHA-256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, base APK size **117,158,131 bytes**, ABI `arm64-v8a`, and `bridge: no`. Its size note says 117,158,131 bytes is below the 150 MB trial ceiling, but the run's trial-limit step was skipped; this was not a trial eligibility test. The workflow also warns Ramus uses x86_64, so ABI compatibility was not tested either.

## Why I did not retry with `allow_no_bridge`

The pinned workflow defines `allow_no_bridge=true` as a **device/ABI smoke test only** and explicitly says it cannot read `/scene` or `/statics` without the bridge. It would not produce the requested Map values. I did not spend a session on a smoke-only path or attempt an APK modification.

The workflow’s bridge-build job can compile `RamusBridge.dll`, but the runtime job has no bridge-artifact download or plugin-install step; its gate checks only the prepared APK/splits. The current collected code supports `/statics` parameters `arr` and `depth` (`runtime-probe/RamusBridge.cs` and `runtime-probe/collect.sh`), but that capability cannot be exercised until an approved vehicle path loads the bridge without modifying the source APK, or a separately authorized bridge-enabled runtime is supplied.

## Relation to #19 and evidence boundary

Report 119 already records static `Map_Get_Datas.listMapDatas` length **250** and the archived phone receipt’s **128 type-name placeholders**; it explicitly does not claim nested-value parity. This PR14 run adds **no** Map values and does not change that conclusion. It is a concrete, run-scoped explanation for why this vehicle attempt yielded no new readback—not proof the values do not exist elsewhere.

No screenshot, visual inference, or redraw was used. No credentials or session were created. A valid next runtime attempt needs a provenance-bound bridge-enabled path that can invoke the nested `/statics` read; until then Map nested content remains open.

## Reproduction

- Builder: `tools/build_l2_runtime_map_depth2_28.py` (stdlib only).
- Regression: `tests/test_l2_runtime_map_depth2_28.py` — **7 PASS**.
- Combined with #19 and #17 focused regressions: **22 PASS**.
- Deterministic rebuild: `python tools/build_l2_runtime_map_depth2_28.py --check` — PASS.
- `git diff --check` — PASS. Protected `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, and `datas/player_start_stats.json` unchanged. All new files below 5 MB.

## SHA-256 pins

| File / evidence | SHA-256 |
|---|---|
| `reverse-engineering/raw/l2-runtime-map-depth2-28/run-40310064929.json` | `467c6b7d54dbee8f87dae7f40b8fb5710022e18f703b5d2805b312421781d169` |
| `reverse-engineering/raw/l2-runtime-map-depth2-28/jobs-40310064929.json` | `51f0689a2b6b81b2ff8f6982a31b7e23c63186a80c61d6d4a81d98ebaeeeb4c6` |
| `reverse-engineering/raw/l2-runtime-map-depth2-28/pr12-runtime-preflight-6411232160.json` | `aec77bd8b3ea789d73738093cfe38d05890b92c246fd4676fd8e37fb08d52f2e` |
| `.github/workflows/ramus-probe.yml` | `0bbdf214940d9125b5867320f1c44100f72630c8fb1312941da7696161d93af8` |
| `.github/scripts/probe-inputs.sh` | `aff9510b781fbd4fe6daa7416c3125e8fdd6acc2dc63ff6f603fdd191d7a1b63` |
| `.github/scripts/prepare-apk.sh` | `8b9d5bb83037fb1570722af2ac7f4c36b4ed586723742ae91bdea6e315e71118` |
| `runtime-probe/RamusBridge.cs` | `d1a20f7a243e1a3baa381f3c6c188556f3c2c325a72e51b8cb869eb2e62ac9e9` |
| `runtime-probe/collect.sh` | `c6199c05432f1ad56d3495292aa1b53dbee9dbc33830c0ff3fc993e1eb8a69df` |
| `docs/apk-analysis/119-L2-Ramus-device-crosscheck-arena-a5a74747-windwings-space-shooter-game-p.md` | `7666ea83074d9828a5e1430123f01fc634219540e08657ddfd752982c0a23e0b` |
| `datas/l2_ramus_device_crosscheck_19.json.gz` | `d9f85f085008a86cf600fe47134e2bce435cd52580a7ea19dad650a623dc8046` |
| `tools/build_l2_runtime_map_depth2_28.py` | `4703d10105bdb7d26e95dd3fd4b0cac2f75c5de8a391333e8b62befa509bc011` |
| `tests/test_l2_runtime_map_depth2_28.py` | `ad74b43026f78751ab301524cde77551e1c7e7b47581f8e21ec1a088c4f64ae1` |
| `datas/l2_runtime_map_depth2_28.json.gz` | `72830d6befa91fa1fca608514191f3e50f83dbb451cf8d74afeff53254da8e54` |

No merge, main push, or self-ACK.
