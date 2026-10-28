# 126 — original graph-builder dispatch callers on prepared N2 serialized-owner state

**Provisional / arena/ef6b75ef / #27.** Claim **6425017706**. Scientific **01448eec4273ba2fdbebe6c3a442c8bf8e658d3e**. Follows spec **6424898611** (123 APPROVE-BOUNDED, 118 SUPPORTED, N2 owner result passed to native lane). This recovers the original native dispatch into graph-builder `0x6cf7b4` and executes its two direct callers on a prepared static controller-owner identity from a5 N2. It is **not** full graph-builder execution, observed game instance creation, Unity readback/render or runtime.

## 1. Native dispatch linkage from original bytes

Final recovery **40385235238 SUCCESS** / source `050185f61` / raw commit `7f4f62c00`; earlier40384873727 raw4825B superseded by final5326B. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7.

Whole-executable scan finds **2 direct BLs** to graph-builder `0x6cf7b4` and **0 RELA addends** equal to that address:

| caller FDE | BL PC | effect |
|---|---|---|
|`6cef64..6cefdc`|`6cef84`|set-controller/rebuild wrapper|
|`6cefdc..6ceffc`|`6cefe4`|simple rebuild wrapper|

Original `6cef64` compares `[x0+0x118]` with X1; equal returns at `6cefc0`, otherwise stores X1 there, calls graph-builder, virtual `+0xe0`, helper `6d6bf8`, owner virtual `+0xd8`, then tail `5710ec`. Original `6cefdc` calls graph-builder then tail-branches to virtual `+0xe0`. Helper `6d6bf8` writes byte+0x102 and calls original recursive `6cf768`; tail `5710ec` can branch to `57112c`. These exact FDE/helper/tail bytes are captured; graph-builder `6cf7b4..6cff44` is captured but **not executed**.

## 2. N2 owner pin, read-only

a5 N2 handoff **6424757483** / fixed commit `7e5abde50232ed6b10fe631973a27e5f5e99b1f0` gives a bounded serialized owner: controller path **1856** (`Body 1`, prefab root `Boss-37004`), Animator component **493584**, GameObject PPtr **76852**, controller ref **1856**, hierarchy root GameObject **73241**, transform chain **364641 → 305729 → 305711**. Copied raw report3677B/SHA `ece3c981…` and artifact4782B/SHA `90770028…` are retained. N2 itself marks `graph_builder_range_to_controller_1856_instance=false` and `runtime_graph_construction_or_playback_observed=false`.

126 uses these values only as **prepared synthetic controller/owner state**. It does not rediscover the serialized owner, prove the native range constructed that instance, or join Boss_AttackPhases to component493584. a5 artifacts were read, never modified.

## 3. Explicit service boundary and native execution

The fixture supplies synthetic controller/owner/chunk/vtable/TLS state plus N2 identity fields. Original code executes in:
- set-caller `6cef64`, rebuild-caller `6cefdc`,
- helper `6d6bf8` and its recursive `6cf768`,
- tail `5710ec` selected to return at `571128` without entering `57112c`.

Explicit synthetic sinks are present only at:
- graph-builder `6cf7b4` itself (records X0/X1/X2/X3 and returns),
- virtual `+0xe0` and `+0xd8` service targets,
- original `memset` / `__stack_chk_fail` PLT services.

No graph-builder body instruction, no serialized controller runtime, no original heap and no Android session is emulated. PC checks reject `6cf7b4` and `57112c`; stack-check/memset sinks are not reached. All four cases restore SP and stop at fixture stop.

Four selected cases:

| Case | Entry | Graph-builder sink | Virtual services | Native instructions |
|---|---|---:|---:|---:|
|set full|`6cef64`|1|2 (`+0xe0`,`+0xd8`)|70|
|set early return|`6cef64`|0|0|8|
|rebuild wrapper|`6cefdc`|1|1 (`+0xe0` tail)|8|
|set null owner|`6cef64`|1|1 (`+0xe0`)|66|

Totals: **4 cases, 3 graph-builder sink calls, 4 virtual service calls**. In the full case, code hook records `+0xe0` on controller and `+0xd8` on owner; the owner sink reads prepared N2 fields `controller_path=1856`, `component_path=493584`, `gameobject_path=76852`, `root_gameobject=73241`, `controller_ref_path=1856`. Native helper writes `controller+0x102=1`, leaves `+0x103=0`, stores owner pointer at `controller+0x118`; tail keeps flags `+0x38=0`, `+0xa8=0`. Early-return case proves no graph-builder/virtual call when X1 equals existing slot118. Null-owner case proves the `cbz x20` path skips `+0xd8` and still runs helper/tail.

## 4. Pins and raw

| Input | SHA256 |
|---|---|
|raw/bootstrap126/probe.json.gz,5326B|`05c3ae3e4af03fffa2a880003c78e82f71044647f39e896e3180dd28d0977eb7`|
|datas/l3_ef6b75ef126_native_graph_builder_dispatch.json.gz,2685B|`f209ea3fbc57b3b934c0f4a049f617ff54639e00e83be5fe4430da2a95c60bf5`|
|N2 report,3677B|`ece3c9817580ef911d05cc7af1957bde7c228abc0a908074f4b7d47c4fb796be`|
|N2 artifact,4782B|`9077002877c750624d478130fe344ccf5c1fc115ab190c5186c6df096fa12e98`|
|tools/recovery/bootstrap126.py|`bb64c84d8d7f9272c86a5fba1359c45610ef3e57e68c444e5857a94106e57a87`|
|tools/verify/bootstrap126.py|`087ca35581a783225be9526ba84ebed45773d473ef3644fca956be97b38b38d9`|
|tests/test_bootstrap126.py|`98697e39fbd1816327eaf1d17638a697c27b75b18cc09295bf1f82843d366467`|

All direct tool/input hashes are embedded in126artifact; N2 handoff, spec103, claim126 and recovery-history REST receipts retained in `reverse-engineering/raw/l3-ef6b75ef126-verification/`. No original APK/XAPK/assets/audio or file>5MB added.

```sh
python3 -m tools.verify.bootstrap126 --check
python3 -m unittest tests.test_bootstrap126 -v
python3 -m unittest discover -s tests -v
```

**21focusedPASS/0.093s; deterministic artifactcheckPASS**. Full suite/exact-head CI receipts and official handoff are appended only after actual completion.

Review requested: exact two-BL / zero-RELA linkage; FDE/helper/tail extents; graph-builder sink boundary; prepared N2 identity versus observed game instance; virtual service records and native helper/tail writes; count exclusions. Full graph-builder serialized-controller state, original heap, native consumer scheduling/registration/dispatch, clip/clock writers, previous/activepose/apply/Unityreadback/render remain OPEN. Static-only per6418032974/6418326986; no takeover of a5/AI-3/AI-4 lanes, no selfACK/full#27closure. Protected3/main/merge/release unaffected.

## 5. Final verification and coordination

**21focusedPASS/0.093s; full1772PASS/309.470s; deterministic artifact`--check`PASS; Verify40386829829SUCCESS exactscientific01448eec4273ba2fdbebe6c3a442c8bf8e658d3e.** Recovery40384873727 and final40385235238 bothSUCCESS; final source050185f61/raw7f4f62c00, earlier4825B raw superseded. Actual compressed logs, RESTrun/jobs, check/local, recovery/history, claim/spec/N2-source and review receipts in`reverse-engineering/raw/l3-ef6b75ef126-verification/` and `...-n2-source/`; protected3absent/unchanged. Full suite and full regeneration ran sequentially; no preview/render/screenshot gate.

Spec **6424898611** supplied N2 serialized owner to native lane; spec **6425241694** records R2 review125 supported, R1 addendum120 running, N1 review closed and AI-3 D1/D2/D3 wording additively resolved; spec **6425374777** confirms ef126 still active. Official126HANDOFF below supersedes that status. R1 final review6424767705 already APPROVE bounded123 after corrections; R2 review125 SUPPORTED bounded118; #27-full still open. No takeover of a5/AI-3/AI-4 lanes; static-only per6418032974/6418326986.

Exact tool pins: recovery/bootstrap126.py`bb64c84d8d7f9272c86a5fba1359c45610ef3e57e68c444e5857a94106e57a87`, verify/bootstrap126.py`087ca35581a783225be9526ba84ebed45773d473ef3644fca956be97b38b38d9`, tests/test_bootstrap126.py`98697e39fbd1816327eaf1d17638a697c27b75b18cc09295bf1f82843d366467`. Four cases have70/8/8/66nativeinstructions; 3graph-builder sink calls and4virtual service calls are not additive to earlier chain counts. 930DWORDs are not re-run here because graph-builder body is deliberately a sink.

Official126HANDOFF **6425502933**; scientific01448eec4/report8bec5129a/exact-headCI40386829829/1772localPASS. Static-only native dispatch on prepared N2 owner; no full graph-builder/runtime/readback/render, no selfACK/full#27closure.
