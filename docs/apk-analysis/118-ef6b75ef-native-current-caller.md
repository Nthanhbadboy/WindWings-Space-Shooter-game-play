# 118 — full native current caller, declared current-only/no-pose branch

**Provisional / arena/ef6b75ef / #27.** Claim **6416802429**. Scientific **79602dd6f221eac8f0289e522abbaff48ed15924**. External spec **6416823283** ACK/CLOSES117bounded clip-context; full#27 remains open.118addresses117's staged-caller boundary, not a re-export or a claim that all Animator paths now run.

## 1. New result: entry-to-RET, not three manual intervals

Original FDE **`0x6d38bc..0x6d3ebc`**,1536bytes, executes from entry to original **RET`0x6d3eb4`** and returns to harness sentinel. No manual intermediate entry/stop or host-computed phase injection. Original prologue/register saves/stack frame/TLS canary, context writer→real clip duration vtable, native time conversion, stream dispatcher/selector/evaluator, scratch initializer, phase store, branch guards and epilogue all execute on the selected input domain.

**Domain is explicit and enforced:**

| Prepared header byte | Value | Boundary |
|---|---:|---|
|frame parameters+0|0|No extra motion/conversion branch|
|frame parameters+`0x28`|0|No previous-time sample/output-clearing and related pose conversion|
|frame parameters+`0x29`|0|No later conversion/output path|
|rig-header+`0x80`|0|No corresponding pose path|
|rig-header+`0x82`|0|No corresponding optional rig domain|

These are **fixture values, not observed game flags**. Unsupported domains raise a fixture error instead of silently fabricating rig data. Native branch decisions themselves execute: tests show skipped previous-call site`0x6d3a1c` and skipped conversion bodies`0x6dc2e0`, `0xb94364`, `0x6d9394`, `0x6d32d0`, `0x6d31b0`. Rig index+`0x74` is not read on this branch. Rig flags/header are prepared without manufacturing geometry, poses or compiled controller mappings.

This closes manual staging **for this current-only/no-pose branch**, **NOT complete Animator scheduling/all caller paths, pose conversion/blending/application or readback/render**. Node clocks/controls/loop, object existence and field writers remain prepared/unobserved.

## 2. Native pieces and services

-117original context writer`0x6d3744` and original AnimationClip vtable duration getter`0xb6bf94` remain real code/data; no duration sink. The clip's muscle blob and node+`0x118` refer to the same **fixture** blob, not an observed graph binding.
-116native normalized time helper`0xb93158`, dispatcher`0x6df270`,115stream sampler`0x6df310`/selector`0x6df768` execute in the full parent call.
- Original scratch initializer **`0xb923ac..0xb923d8`** writes vector/identity-like defaults and flags into the caller's local scratch. This helper execution does **not** prove that pose output is applied; on the selected source branch, the external prepared pose-output buffer stays entirely at its nonzero0xA5prefill.
- Source output DWORDs are produced by native sampler into prepared current-channel storage, with returned phase stored natively at node+`0x170`.
- Normal successful sample calls reach **only declared host`modff`** (original PLT/GOT/name pin inherited116). No memcpy or stack-failure service is invoked on success. Initialization allocators remain declared in reused fixture; not counted as sample work.

No substitution for unimplemented conversion/scheduling/property application is installed. Bytes of some excluded code already exist in capture: the open prerequisite is real/validated controller-rig/frame/graph state and its acquisition, **not an asserted global absence of original code**.

## 3. TLS/canary: synthetic input, real guard, failure is not success

Original MRS TPIDR_EL0 and canary loads/comparison execute. Fixture supplies an explicit synthetic TLS page; offset**40 /0x28** contains**0x1122334455667788**. This is **not Android TLS, a captured thread, device session or runtime readback**. Stack pointer after every successful source call equals its prepared entry value; final executed original instruction is RET`0x6d3eb4`.

Failure binding is checked from original PLT instructions and ELF symbol:

- PLT **`0x109acc0`**, GOT **`0x10e3d00`**, symbol **`__stack_chk_fail`**.
- The registered failure sink **throws `StackCheckFailure` and never returns success**. Positive calls do not invoke it.
- One negative test mutates synthetic TLS canary at original PC`0x6d3e84`, after the prologue snapshot. Native comparison/branch reaches the original failure PLT; the sink raises. Artifact labels **`EXPECTED_FAILURE_NOT_SUCCESS`**, retains executed PCs/failure call; no successful caller receipt is claimed for that case.

The failure sink is not execution of Android libc's failure handler, and no host process abort/device-stack semantics are asserted. Its purpose is to reject fake-success handling and verify original control flow reaches the correctly named import.

## 4. Null blob fallback is also executed

Separate fixture sets node+`0x118` to null. Original path **`0x6d3600 → 0x6dacf0 → 0xb92414`** executes on the same no-pose header domain and returns normally: **87native instructions,0external substitutions**.

- Current-channel buffer is not sampled or zeroed; reset refers only to the touched output-structure fields. Does not call context writer/sampler; artifact context/sample-time fields are null, not fabricated zeros.
- Frame flag byte+24 is reset to0, even if node flag propagation first set it.
- Because fixture frame+16points to a non-null prepared output structure, original reset`0xb92414` executes. Defined word/vector/default fields are reset; **padding bytes are not claimed zeroed**. Tests check actual fields, not a fictitious whole-struct memset.
- This is a prepared null-blob branch test, not proof that any original source scene enters it or that graph/clip acquisition legitimately produced null.

On the normal current path, frame flag byte+24 is OR-updated: once set by node+`0x1f3`, a subsequent flag0call retains it. This is native field behavior in the fixture, not a general Animator event interpretation.

## 5. Original-source full-call receipts

Source inherited raw extraction: `reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz`, zero-based row140, `data.unity3d/resources.assets:1609`; raw object SHA**69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae**. **2262unchanged uint32 words/9048B**, packed SHA**a21ecdaa8cc6e10730d6de9aa1e45ba319ad05d31dbb3998def8d418d05f603c**. No new independent UnityFS/serialized-object decoding claim.

Source start0/stop6.9666666984558105/cycleOffset0; node clocks/controls/loop and no-pose flags prepared as declared.10source calls produce **930DWORDs**, all bit-equal to separate directed-context/time/f32-stream references. All10call traces include entry and RET, restore SP and pass native canary comparison.

| Requested normalized double (clock construction input) | Full native instructions |
|---:|---:|
|0|3154|
|0.25|3109|
|0.7|2450|
|1|3157|
|1.25|3109|
|−0.25|2473|
|−1|1644|
|0.7,rewind|5724|
|same|1497|
|0.99999999|3157|

Additionally8synthetic control cases run the complete same-domain caller, varying direction/negative-zero sign, offset, quantization and loop behavior. Combined **18successful samples /32862native instructions /18modff substitutions**, plus separate87instruction null fallback and1expected canary failure. Counts exclude initialization/failure work from successful sample totals. Captured code counts are not execution coverage.

No source DWORD is promoted to a resolved PPtr/Sprite; pose output remains unchanged on this selected branch.117's directed conversion still applies, including sub-end double query becoming f32one and looping tostart. This is a fixture precision/control-flow observation, not a claimed observed game bug.

## 6. Terminology and external disposition

External6416823283ACK117 accurately accepts the bits/result, but calls `.7→3f333334` “tie-away.” **Clarification posted and retained in `rounding-clarification.json`:117does not use tie-away rounding for that conversion.** Native context uses FCVT nearest then quotient comparison and one-ULP adjustment toward+∞ (with+FLT_MAX guard). **FRINTA tie-away belongs to116quantization in`0xb93158`**, a separate operation. No scientific source/code changed to match review wording.

117bounded context ACK is synchronized in117report/HANDOFF. Peer8141386a restart notice **6416880872** preserves their branch/receipts and#6replication claim; no takeover or reset/import here. Runtime vehicle work remains a5's lane. No independent validation of peer/native-TMP/atlas/runtime outputs is implied by this coordination update.

## 7. Tool/input pins

Final bounded recovery **40328588214 SUCCESS**, source **353d890ae6640bb9885bd59607f8a111ddfa5b1d**, raw commit**2aba8a5fd**. Initial recovery40328234858also succeeded but unnecessarily captured many global stack-check caller sites; selector was narrowed, final scientific artifact pins only the bounded final raw. Original XAPK cache fail-on-miss; no APK mutation/replacement. XAPK SHA**f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e**; libunity SHA**d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7**.

| Tool/input | SHA256 |
|---|---|
|`reverse-engineering/raw/caller118/probe.json.gz` (4808B)|`b1c46fe69e117a9b9b8d79eddd90b8a448b257a8389c12417f25d972d260eabb`|
|`datas/l3_ef6b75ef118_native_current_caller.json.gz` (6091B)|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|`tools/recovery/caller118.py`|`8d0e2f9b536f1ca98318758888798f370667b32545c7bccd151f63f2410f8136`|
|`tools/verify/caller118.py`|`3aa29abb96c903ee4dbe1341f2a9dce40a3180eacd5b75d5a742f660f8dba2e4`|
|`tools/verify/caller118_native.py`|`5e0326661787f5e03788716bb69f74be17325e6fe89f2cbe27b26af5e32e4864`|
|`tests/test_caller118.py`|`67c85efc7aaef1ffcd34b4075c685f8277ab7121c22c7309e96886677ca7c9d4`|
|Reused117raw|`9bfa2fdd7f0a015b9a1ea17306c7fef8627a6410f845b4940aa19ea708d2bf60`|
|Reused116raw|`1dfa2ca9ab5851d75e969d75428d4f96891464ddc7a6ba583103b87833539c31`|
|Reused115raw|`9b2b21a61fe9b459b4815ab5361576f036c873f36da9ecbce2a25ac618e1d364`|
|Inherited source gzip|`cac775a419758a7ef51e74a9ad1d7a6e1040faaf69d28fb84d9311d978aec082`|

Artifact pins all reused fixture/reference/guard tools too. Final new raw has4root entries (3original FDE,1labelled bounded PLT window),1selected direct caller site,8windows and49literal/import cells. No original-code implicit-zero fallback. TLS/objects/containers are explicitly synthetic; inherited original guards are unchanged.

```sh
python3 -m tools.verify.caller118 --check
python3 -m unittest tests.test_caller118 -v
python3 -m unittest discover -s tests -v
```

**40focused PASS /2.261s; deterministic byte-for-byte check PASS.** Tests cover exact FDE/entry/RET/SP/TLS, canary failure import and rejection, actual native duration/context/time/stream/scratch, skipped domains and guard rejection, frame flag OR/reset, null/reset defined fields and no substitutions, stack-prefill invariance, source930DWORDs/rewind/repeat, relocated base and no full-Animator promotion. **Full1571PASS274.031s; Verify40329033477SUCCESS exactscientific79602dd6f221eac8f0289e522abbaff48ed15924.** Actual compressed logs/REST/local/check receipts retained under118-verification.

## 8. What remains open

Actual engine node/clip creation, graph binding and game-side state/clock/control writers remain unobserved. Previous-time branch, real rig/controller/frame data, pose/channel conversion, weighting/blending/normalization, property/PPtr application, services/bootstrap, Unity readback/render and device TLS/libm parity remain open. Closing current-only caller entry-to-RET does not close those paths.

Independent review requested: flag-domain enforcement versus native branch traces; full function entry/RET/stack restoration; synthetic TLS with real failure-control flow; scratch/reset defined fields versus padding; source/current output versus applied pose/property; counts and inherited/provisional lineage. **No selfACK/full#27closure.** Protected3paths (`datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, `datas/player_start_stats.json`) absent/unchanged at118baseline/current. No original APK/assets or file>5MB added, main push, merge, release/vehicle changes, screenshot/redraw or render acceptance.

Official118HANDOFF **6417057892** posted with scientific79602dd6f / report9f2f42770 / exact-head GREEN and1571localPASS. Independent review pending; no selfACK/full#27closure.
