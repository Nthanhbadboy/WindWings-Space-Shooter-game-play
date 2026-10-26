# 119 — original parent caller and second-phase guards

**Provisional; arena/ef6b75ef; #27.** Claim6417082119. Scientific **b9e6765fa6266ae87e628d7f43f716147f74ba44**. Follows118handoff6417057892; no external acceptance inferred. The new execution is a parent chain on the same declared no-pose domain, **not execution of active second-phase pose math**.

## Original-byte link and extents

118recovery directly preserved `BL6d38bc` at `6d46c4` inside original FDE **6d46a8..6d46f4**,76B.119captures that parent again and the next callee **6d3ebc..6d442c**,1392B, both original EH-frame-bounded functions. Parent restores the same four arguments after first call, calls second phase at`6d46d8`, writes literal1to **node+174** at`6d46e0`, restores registers and returns at`6d46f0`.

This is a native byte/field-order result. “Completion byte” is a fixture label for this store, **not a recovered semantic name, observed game event, actual scheduling completion or a Unity state readback**. Recovery found no direct immediate branch to6d46a8in its scanned executable segments; that does NOT prove no callers or dead code (indirect dispatch remains possible).

## Second phase: exact early-return gates

Full second-phase entry executes prologue, synthetic TLS read and stack canary snapshot, followed by:

1. `6d3ee4`: load node+118blob; `6d3ee8 CBZ` returns if null.
2. `6d3eec`: load **parameters+10 descriptor pointer**; load signed-mode DWORD at descriptor+4; `CMN#1 / B.EQ6d43f8` returns when bitsFFFFFFFF (−1).
3. `6d3f00`: load parameters+28byte; `CBZ6d43f8` returns when0.
4. Otherwise active body begins at6d3f08, **not executed here**.

Thus even with parameter28=0, a non-null valid descriptor is required before that flag check.119supplies an explicit synthetic16B descriptor at fixturebase+62000and binds parameters+10to it. Mode0is prepared; not evidence of an original descriptor's mode. Nullblob returns before reading descriptor. The three guard cases are executed separately from original entry through RET6d4424, with distinct PCs proving the early exits and no external calls or pose-buffer writes.

The parent enforces118's no-pose domain (parameters0/28/29=0, rig80/82=0). Active domain is rejected, not silently zero-filled or bypassed. Nonzero28is allowed ONLY for standalone second-phase tests where nullblob or mode−1already guarantees original early return; it is never enabled in a full parent run. TLS is the synthetic fixture TPIDR_EL0/canary, not Android/device state. Real original compare/guard/epilogue executes in both children.

## Actual source execution

Ten source1609calls execute **parent entry→118complete caller→second-phase guard/epilogue→native node174store→parent RET**. Stack nesting moves118context from base+1eea0to **base+1ee70**, matching the parent's0x30B stack save; no manual PC stages or independent phase injection. Original source words/start/stop/cycle remain inherited through118/115. The new descriptor is synthetic; source extraction is **not independently repeated/revalidated**.

All **930DWORDs**, normalized-context fields and native stored phases match the pinned118artifact for its10queries including rewind/repeat/boundaries. This is a regression/composition comparison with shared lineage, **not a second independent stream algorithm**. Every call reaches parentRET6d46f0and writes byte174=1. External pose buffer stays0xA5; the only successful source external service is inherited hostmodff, not Android-libm parity.

**10source parent calls /29974native instructions /930DWORDs**. Three standalone second-phase guard cases and one separate null-parent execution are not included in those source totals. Null parent still writes node174=1after native nullfallback and second guard; this demonstrates why that byte alone cannot prove actual clip sampling or pose application.

Tests additionally cover rejection of active/unsupported flags, relocated fixturebase and nonzero stack prefill. **10focused tests PASS /1.382s**; deterministic artifact `--check` PASS. Full suite/exact-head CI disposition appended only after completion.

## What the unexecuted active body actually requires

This is a positive original-byte prerequisite map, not an assertion that original code is missing:

| Original PC | Data dependency / effect observed statically |
|---|---|
|6d3f08..6d3f54|blob+5f0relative displacement selects another structure; zero produces null pointer, NOT a fabricated valid structure|
|6d3f64..6d3f84|reads selected structure+10/+12uint16 and+1c/+38DWORDs; sums for native6df218container sizing|
|6d3f14,6d3f74|node+120, node+150/+158containers/pointers|
|6d3f78|frame-holder→frame+10output pointer|
|6d3f90..6d3fac|descriptor+8float drives6d2e94time/stream path, distinct from118current-context query|
|6d4034|calls6e5cdcfor local storage initialization|
|6d4038..6d4050|rig+74/+78indices feed6dc2e0conversion|
|6d4054..6d4080|callsb94364with native data, rig82flag and local outputs|
|6d4098..6d40a4|writes3vectors at output+120/+130/+140|
|6d40a8..6d40e0|optional rig82and descriptor-mode-dependent b97514path|
|6d42c8..6d43f4|reads node+138transform-like vectors, SIMD operations/reciprocal refinement and writes same output range|

These instructions alone do not validate a complete memory layout or prove semantic bone/motion/property assignment. No arbitrary zero counts/identity rig geometry or dummy converters are substituted to make the active body return.119raw does not recursively capture every active callee; original code may already exist in earlier captures, but that is not proof of valid native inputs or execution. Actual valid structure/rig/controller/frame/descriptor provenance and game-side writers remain an evidence prerequisite, not screenshot/render acceptance.

## Pins and reproducibility

Recovery **40330141486 SUCCESS**, source9b1a55f663afae60721da3d209382d5da8b05fe9, rawcommit42b05ba61. Raw `reverse-engineering/raw/caller119/probe.json.gz`: **2249B/SHA99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321**. Recovery tool SHA **d0de4b9e36395c1da93509a4e64b68a1a5db4a25d3e073a73597dd6f0b311759**. Both original FDE roots captured without recursive dependency guessing. Original XAPK/libunity pins match118; cache fails on miss, no local APK modification.

Derived `datas/l3_ef6b75ef119_native_parent_guards.json.gz`: **3623B/SHA49eb74d14c974dafabae8dc5cbe30804f9872edee25807c2e16adaecd73de78f**. Exact119tool/test/raw and118raw/artifact hashes are in its `inputs`;118artifact transitively pins reused115–118tools/raw/source. Shared-source/reference lineage is deliberate and explicit. The retained raw and verification receipts accompany the derived report; no standalone binary APK/assets committed.

```sh
python3 -m tools.verify.parent119 --check
python3 -m unittest tests.test_parent119 -v
python3 -m unittest discover -s tests -v
```

Independent review requested: original parentargument restoration/store ordering; guard order and descriptor-before-flag requirement; context stack relocation; source composition versus independent extraction; inactive second phase versus real pose application; mode/flag provenance and exact count exclusions. **No selfACK/full#27closure.** Actual node creation/graph acquisition, game-side clocks/control/descriptor writers, previous-time/active second-phase rig conversion, weighting/blending/normalization/application/bootstrap/Unity readback/render remain OPEN. a5runtimevehicle and8141386a#6rep lanes untouched. Protected3unchanged, no main push/merge/release changes.

## Final verification and coordination

Full **1581tests PASS/280.259s**; exactscientific **Verify40330340745SUCCESS**. Actual compressed logs/REST/check/local receipts in119-verification. External spec **6417186640 ACK/CLOSES118bounded current-caller**, not full#27; also accepts rounding clarification and preserves peer/runtime lanes. Independent119review pending.

Tool SHA256: parent119.py `d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`; tests/test_parent119.py `431e27ec1a0b9179df431ec4031ce27ff20ce8f18aeaf93dd98374ea700aaf2d`. Standalone null/mode/flag guard traces execute24/29/31instructions respectively, excluded from29974sourceinstructions.
