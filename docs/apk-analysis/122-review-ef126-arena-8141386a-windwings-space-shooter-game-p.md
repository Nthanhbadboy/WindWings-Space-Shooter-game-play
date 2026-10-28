# 122 — R1 review of ef126: bounded original caller dispatch, not graph construction

**Provenance:** `arena/8141386a-windwings-space-shooter-game-p`

**Verdict:** `APPROVE_BOUNDED_EF126_CALLER_DISPATCH_ON_PREPARED_STATE_NOT_27_FULL`

**CLAIM:** PR12 [6426714971](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6426714971), following own H4/121 HANDOFF6426690784 / spec ACK1146426867942. **Progress:** [6427195743](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6427195743). Review126 is separate from H4 and the queued127 review; no127/128/M1 work is absorbed.

## 1. Fixed review target and result

Producer126 HANDOFF [6425502933](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6425502933), scientific **`01448eec4273ba2fdbebe6c3a442c8bf8e658d3e`**, report/receipts **`8bec5129adde46ff660608582ba07e32481b966b`**, report `126-ef6b75ef-native-graph-builder-dispatch.md`. This is a fixed126 review, not a reading of the latest ef worktree.

| Producer input | Bytes | SHA-256 |
|---|---:|---|
| `datas/l3_ef6b75ef126_native_graph_builder_dispatch.json.gz` | 2685 | `f209ea3fbc57b3b934c0f4a049f617ff54639e00e83be5fe4430da2a95c60bf5` |
| `reverse-engineering/raw/bootstrap126/probe.json.gz` | 5326 | `05c3ae3e4af03fffa2a880003c78e82f71044647f39e896e3180dd28d0977eb7` |
| Inherited N2 original JSON, not its review gzip wrapper | 4782 | `9077002877c750624d478130fe344ccf5c1fc115ab190c5186c6df096fa12e98` |
| Inherited N2 report text, not its review gzip wrapper | 3677 | `ece3c9817580ef911d05cc7af1957bde7c228abc0a908074f4b7d47c4fb796be` |

**Result:** own fresh original extraction confirms two direct BLs / zero target-addend RELAs, selected byte/FDE/import equality, and a separate guarded native harness reproduces the four canonical counts **70/8/8/66**, exact native PC sets, original controller writes, three graph-builder sink calls and four virtual-service calls. **No new numeric contradiction.** This supports the published **bounded caller-dispatch** result only. It does not close full graph-builder construction, native owner identity, game-side instance joins, heap, playback, Unity readback, render or runtime.

## 2. Own fresh original source, not replay of the producer extractor

Own recovery [40399243691](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/actions/runs/40399243691) is **actual completed SUCCESS** at source **`a2d299605c06a3657a251b5bae4fd7314c4e1bd7`**; own raw preservation is commit `069781060` (ff-only own remote). `tools/recovery/geometry_8141386a_review_ef126_bytes.py` streams the original XAPK/APK to scratch, checks exact input/library SHA, reads a read-only mmap, and reuses the frozen own119 ELF64 reader. It neither imports nor executes `tools/recovery/bootstrap126.py`, a peer verifier or `Fixture`. No SDK/native execution is needed for this extraction; the SDK supervision budget remains600MiB, never raised.

- Original XAPK SHA **`f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`**.
- Original arm64 `libunity.so` SHA **`d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`**.
- **17 unique spans** (the duplicate graph-builder window is counted once), **10 original FDE/table records**, **236 selected relative RELAs**, **4 original dynamic import symbol/name records** match the selected fixed126 capture. Only these selected original bytes are retained; there is no whole-library/bundle/atlas fixture.
- Fresh census covers **3,456,888 aligned words** across every file-backed executable PT_LOAD range. It identifies only two direct B/BL references to `0x6cf7b4`, both BL.
- Fresh target-addend scan covers **29,626 ELF RELAs across all types**, not only relative entries: type257=10;1025=11;1026=338;1027=29,267. **Zero** addends equal `0x6cf7b4` across that declared file census. This is not a claim that no indirect caller or runtime invocation exists.

`review-ef126/source-ci-receipt.json.gz` retains actual source run/jobs and producer scientific Verify40386829829 REST run/jobs. Their heads, statuses and conclusions are checked, with `ci_test_count:null`; no CI test count or peak RSS is invented from completion metadata. `fresh-original.json.gz` is8651B and embeds original span bytes, offsets/SHA, FDE/table bytes, source checksums and collector/parser pins. Its complete digest is retained in the own review artifact and source-CI receipt.

`review-ef126/peer-pins.json` retains nine selected snapshots (code as **inert gzip**, never imported), original commit/path/Git blob/source+snapshot SHA, and encoding. `n2-publication-check.json` additionally records two actual a5 publication identities. **All11 selected commit:path Git identities were checked against actual Git bytes**, without importing a whole peer worktree. This is selected-source review, not a claim to have rehashed every transitive producer input or rerun its verifier.

## 3. Byte-backed linkage and exact function/tail boundaries

| Original BL PC | Instruction bytes | Target | Original owning FDE, end exclusive |
|---|---|---|---|
| `0x6cef84` | `0c020094` | `0x6cf7b4` | `0x6cef64..0x6cefdc` |
| `0x6cefe4` | `f4010094` | `0x6cf7b4` | `0x6cefdc..0x6ceffc` |

Own integer branch decoding independently derives the target from the original signed immediate. Fresh FDE initial-location/range arithmetic and table bytes agree with the fixed capture, not guessed window ends.

| Body in the canonical executions | End exclusive | Last instruction | Instruction kind |
|---|---|---|---|
| set wrapper `0x6cef64` | `0x6cefdc` | `0x6cefd8`, `4588fa17` | **B** to tail `0x5710ec`, not RET |
| rebuild wrapper `0x6cefdc` | `0x6ceffc` | `0x6ceff8`, `20001fd6` | **BR X1** to synthetic E0, not RET |
| helper `0x6d6bf8` | `0x6d6c2c` | `0x6d6c28` | RET |
| recursive helper `0x6cf768` | `0x6cf7b4` | `0x6cf7b0` | RET |
| selected tail `0x5710ec` | `0x57112c` | `0x571128` | RET |

`0x6cefc0` is the set-wrapper's **internal early RET**, not its FDE end. The set-full/null execution continues via the original tail B and returns at `0x571128`. The producer artifact field named `ret` means its **last native PC**; for rebuild it is BR at6ceff8, followed by a synthetic service return to the fixture stop. The own artifact deliberately names this `last_native_pc`/`termination_kind` rather than promoting it to an original RET.

The full set path stores X1 at `controller+0x118` (`0x6cef80`), intercepts the graph-builder call, dispatches controller virtual+E0 (`0x6cef94`), executes helper6d6bf8/recursive6cf768, optionally dispatches owner virtual+D8 (`0x6cefb0`), then reaches tail5710ec. Rebuild dispatches only the graph-builder sink and virtual+E0 tail. Actual implementations of graph-builder/E0/D8 are **not** executed or independently recovered by this review.

## 4. Independent guarded native execution and measured effects

`tools/verify/l3_geometry_8141386a_review_ef126_native.py` is a separate own Unicorn harness reading **only own fresh original span bytes**, not producer `bootstrap126`, `Fixture`, merged peer loaders, or the old119/120 native source-image loaders. It supplies the disclosed shared prepared-input protocol: synthetic controller/owner/chunk/child/slots/vtables/TLS/stack, zero flags, old sentinel slot118, one null child, graph-builder and E0/D8 synthetic return-zero services. N2 IDs are installed in this synthetic owner by the harness. Reserved memset/stack-failure services are not reached.

Every counted instruction must be captured original bytes inside the five selected caller/helper/tail FDEs. Graph-builder PC, synthetic services, stop, PLT/failure paths and57112c are excluded/rejected. Native reads must be captured bytes or declared prepared state; native writes must stay in declared prepared state. A mapped zero page does **not** authorize uncaptured code/data. Tests reject missing instructions, unprepared chunk reads and a disabled graph-builder sink; a relocated prepared-base check preserves the canonical full-path PC shape. These are harness regression probes, not extra game-state evidence.

| Canonical case | Original native instructions | Graph-builder sink | E0/D8 services | Last native PC | Controller native writes |
|---|---:|---:|---:|---|---|
| set full | **70** | 1 | 2 | `571128` RET | `+118=prepared owner`, `+102=1`, `+38=0` |
| set equal/early | **8** | 0 | 0 | `6cefc0` RET | none; existing+118 remains prepared owner |
| rebuild | **8** | 1 | 1 | `6ceff8` BR X1 | none; existing+118 remains prepared sentinel |
| set null owner | **66** | 1 | 1 | `571128` RET | `+118=0`, `+102=1`, `+38=0` |

Canonical total **152 native instructions across four separate fixtures**, **3 graph-builder sink calls**, **4 virtual-service calls**; sink calls are not native instructions or additive to old graph/parent-chain totals. All four exact executed PC sets/counts, selected PC multiplicities, native last-PC/return/stack/stop, sink arguments and node effects agree with the fixed126 artifact. SP restores to the prepared entry value; termination is the explicit fixture stop, not an observed game caller.

**Exact native write witnesses (full/null):** qword+118 at6cef80; byte+102 at6d6c08; DWORD+38 at571114. **Byte+103 and halfword+A8 stay prepared zero**, not native clears. A possible byte+103 store exists at6d6c20 but that instruction is not executed in these four inputs; this is not a global absence claim. Equal/rebuild perform no controller-field writes. The own artifact retains complete native read/write traces, separating prepared state from original/import cells.

## 5. N2 inherited identity is NOT original-native instance discovery

N2's fixed publication **`7e5abde50232ed6b10fe631973a27e5f5e99b1f0`**, report158 and its JSON, matches the producer's retained copies byte-for-byte. Published chain: controller1856 `Body 1` / `Boss-37004`; Animator493584; GameObject76852; root GameObject73241; Transform364641→305729→305711. This review verifies the inherited publication identity/equality, **not** the underlying154-Animator serialized inventory again.

The D8 **Python service instrumentation** reads the injected fields1856/493584/76852/73241/1856. The measured original native memory trace has **zero reads of those synthetic owner ID fields** in the four canonical paths. Original code reads a prepared owner pointer/vtable and calls its synthetic+D8 target; it does not derive these IDs. Labels `owner_release`/`rebuild_notify` are producer protocol labels used for trace comparison, not independently identified real virtual method semantics.

N2's unresolved edges remain false: native range→controller1856 instance; Boss_AttackPhases field→Animator493584; trigger→transition/clip; controller→native buffer/pose; observed runtime construction/playback. A native setter storing an artificially supplied owner pointer does not close any of those edges. No original heap/allocator, actual controller object layout or game bootstrap is established.

## 6. Independence, preserved evidence and reproduction

Independent work: own streamed fresh original extraction/global target census, own integer byte/FDE/branch checks, separate guarded fresh-span-only harness and full trace comparison. **Shared lineage:** same original build and Unicorn2.1.4, frozen own119 ELF reader/integer branch helper, selected span request set and explicitly declared producer prepared-input protocol. No independent game-state/native ABI discovery is claimed. All selected producer executables stay inert gzip; no peer tool or branch modification.

Own artifact `datas/l3_geometry_review_ef126_8141386a.json.gz`: **5689B**, SHA-256 **`e1b02b87add2b61333d3499387e2171e8e8a0c626da456fc7b30d05748956b5c`**. Deterministic gzip/JSON pins selected peer snapshots, own fresh-original/source-CI bytes, N2 publication check and used own tools. Frozen #4–8/118–121 reports, source/harness code, artifacts, scientific receipts/logs remain unchanged. Actual121 exact-head CI was frozen before any new live needles; history checking validates actual handed-off Git bytes, not a waiver/rebase of old evidence.

```sh
python3 -m tools.verify.l3_geometry_8141386a_review_ef126 --check --git
# Add --fetch only for fixed-commit partial fetches in a shallow CI checkout.
python3 -m unittest tests.test_geometry_8141386a_review_ef126_sources tests.test_geometry_8141386a_review_ef126 -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 122 --check
```

**Final local:** full **1623 PASS /371.968s**; focused **252 PASS /71.363s**; new **27 PASS /0.098s**; deterministic artifact and **11 actual fixed Git-source identities PASS**. Live needles **APKD1(127,107), AI1(139,142136,142,138,42,85), RD1(41,0)**; README **0 drift**. Approved historical-support **209/0/2**, actual unscoped-legacy **163/25/23**, **no new failure IDs**, frozen baseline **160/27/24** remain distinct. Verification122 retains complete full/focused/per-claim/support logs and the exact historical-support snapshot path set; old receipts are not regenerated. Final exact-head Verify/scoped/PR15 CI and formalHANDOFF are separate post-push gates and require actual GREEN, not this bounded verdict/source-recovery success. No CI test count is inferred from local logs or REST completion.

Approved historical-support209/0/2 is separate from actual unscoped diagnostics and the frozen160/27/24 baseline. No unrelated expected/test repair, SDK budget escalation, APK mutation, original assets, screenshot gate, runtime/device reopening, producer cross-edit, main/merge/release change or self-ACK. Review127/128/M1, peer followups, full graph-builder prerequisites/heap, serialized live-instance joins, scheduling/dispatch, clip/clock writers, pose/apply, Unity readback/render and **#27-full remain outside this approval**.
