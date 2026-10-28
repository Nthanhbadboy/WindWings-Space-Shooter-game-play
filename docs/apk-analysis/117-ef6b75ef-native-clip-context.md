# 117 — original clip vtable duration, native context writer, staged caller

**Provisional / arena/ef6b75ef / #27.** Claim PR12 **6416392949**. Scientific **7f182db37d0a8232bf429fb20b8427fa076fc062**. Continues116/115 without calling prepared state a live Animator observation. External **6416406730** ACK/CLOSES **116 bounded time+dense/constant composition**, not full#27. No selfACK.

## 1. New proof and boundary

Original context function **`0x6d3744`** executes completely. It follows node+`0x1d0` to a prepared native AnimationClip instance, dispatches through **original vtable+`0xa8`** to **`0xb6bf94`**, reads duration from the **same muscle blob** used by time conversion/sampling, normalizes double clocks with native directed f32 conversion, and copies direction/offset/quantization/flag fields into context.

**No duration service stub or mock vtable.** The actual vtable bytes/RELA and method instructions come from original libunity. Context acquisition executes with **0external substitutions**. The node, clip instance, clock values and other fields still are **prepared fixture state**, not engine-created or live-captured objects.

The native context is then consumed without a host-computed query injection by **three explicitly staged original caller intervals**, followed by116time conversion and115stream selection/evaluation. This is **not a complete execution of caller`0x6d38bc`**, scheduler, Animator context acquisition from real game state, blending or property application.

## 2. Original ownership/dataflow, replacing an incorrect candidate

| Original bytes/RELA | Established link |
|---|---|
|Constructor`0xb69d14`, ADRP/ADD at`0xb69d38/0xb69d40`, STR at`0xb69d4c`|Native clip constructor stores vptr **`0x10c3fa8`** at instance+0|
|Original RELA address **`0x10c4050`**, addend **`0xb6bf94`**|Vtable+`0xa8` points to actual duration method|
|`0x6d3750` loads node+`0x1d0`;`0x6d375c..0x6d3764`|Context writer loads vptr, loads+`0xa8`, performs native BLR|
|`0xb6bf94..0xb6bfb4`|Loads clip+`0x1e0`; null→0; otherwise reads blob+`0x5fc` stop and+`0x5f8` start, returns native f32 **stop−start**|
|115native AnimationClip record/API/serializer field join;116time fields|Corroborates this constructor/layout as AnimationClip: class74/native592 and same clip+`0x1e0` muscle blob. Class registration/bootstrap not executed|
|`0x6d3924` loads node+`0x118`|Original caller selects blob used downstream; fixture sets this and clip+`0x1e0` to the same source-adapted blob|

Early discovery considered`0xb6a838` by address proximity. Original bytes show **B.LT inside another function, not an FDE entry/getter**. It was rejected, removed from final recovery roots, and never executed scientifically. The real vtable was recovered from the constructor store and original RELA, not by substituting the nearest AnimationClip API method. The direct API getter`0xb6a84c` is **not** used as the virtual duration target.

Two selected original FDEs are retained and tested:
- Context writer **`0x6d3744..0x6d38bc`**.
- Actual duration getter **`0xb6bf94..0xb6bfb4`**.

The constructor/vtable are static byte evidence; no claim to execute full AnimationClip/node constructors, registration, object lookup or scheduling.

## 3. Native context fields and conversion behavior

Input node fields and output context offsets:

| Input | Native operation | Context |
|---|---|---|
|node+`0x60` f64|Divide by native duration converted to f64, then directed f32 adjustment|+0current normalized f32|
|node+`0x178` f64|Same independent operation|+4previous normalized f32|
|node+`0x184` f32|Exact bits copied|+8raw sign control|
|node+`0x188` byte|Raw byte copied|+12flag|
|node+`0x18c` f32|Exact bits copied|+16offset control|
|parameter block+`0x29` byte|Raw byte copied|+20flag|
|node+`0x1f1` byte|Raw byte copied|+21flag|
|node+`0x1fc` f32|Exact bits copied|+24quantization control|

The native constructor at`0x6d353c` statically initializes relevant defaults, including sign control1, offset0 and quantization−1; it is not executed here. Fixture clock/control writes remain explicit inputs, not proof their game-side writers ran. Context padding/gaps are not promoted to meaningful initialized values. Nonzero-prefill tests compare the **defined fields**, not padding.

### Directed f64→f32 is not plain nearest rounding

For each double quotient q, original code converts to nearest f32 v, then compares the double quotient to double(v). If q>v, it advances v to the next representable value toward+∞, including a positive subnormal from underflowed+0. The **+FLT_MAX special guard** prevents incrementing that exact converted value. Duration0 writes both normalized fields0 and still copies the other fields.

Measured fixture cases:

| Input / duration | Native normalized output |
|---|---|
|current0.7 /1|bits**`0x3f333334`**, value**0.7000000476837158**, not nearest f32`0x3f333333`|
|current−0.7 /1|nearest f32 is already above the double quotient; retained|
|current1e−50 /1|bits**1**, smallest positive subnormal, not0|
|current−1e−50 /1|bits**`0x80000000`**, negative zero|
|current0.5, start2/stop4|duration2, normalized0.25; actual virtual stop−start, not stop4|
|duration0, nonzero current/previous|both0|

This is separate native logic for current **and previous** clocks. Tests mutate original branch`0x6d3798` to bypass the adjustment:0.7reverts to nearest f32. A second mutation changes duration FSUB toFADD: a nonzero-start fixture no longer normalizes by stop−start. No original scientific bytes were changed; mutations are test-only counterfactuals.

These finite cases use Unicorn/default FP state and declared fixture values. No universal NaN/overflow/exception/flush-to-zero policy or Android-device FPCR parity is asserted.

## 4. Staged original caller — exact manual-entry boundary

The fixture does **not** silently reimplement the caller or pretend to run it all. It executes:

1. **Entry`0x6d3924`, stop before`0x6d3960`**: native node+`0x118` blob load; native stack context defaults; native context-writer call, including actual duration BLR.
2. **Entry`0x6d39bc`, stop before`0x6d39c0`**: original LDP reads cache/output-holder pointers from node+`0x128`/+`0x130`.
3. **Entry`0x6d3a20`, stop before`0x6d3a48`**: original node+`0x19d` loop-byte read; **original LDR S0,[SP,#0x1a0]** reads the newly generated current query; passes context/blob/cache/output to`0x6d2e94`; native time→dispatcher→stream executes; original STR stores returned phase into node+`0x170`.

SP matches the original local layout; callee-saved registers node/parameter inputs and prepared node fields are explicit. No host-decoded key, frame selection or computed phase is fed into sampling. The source blob pointer and current query are loaded by original instructions. Cached state/output pointers are still prepared fixture containers.

Excluded: prologue/TLS canary, intervening previous-time branch and its optional evaluation/output clearing, later channel conversions/pose handling, full caller control flow, blending/scheduling/application. These manual intervals are **not** a full-call or engine receipt. Each entry/stop and trace is stored in artifact.

## 5. Original-source staged receipts

Inherited APK extraction `reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz`, zero-based row140, `data.unity3d/resources.assets:1609`. Original object SHA**69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae**; **2262unchanged words/9048B**, packed SHA**a21ecdaa8cc6e10730d6de9aa1e45ba319ad05d31dbb3998def8d418d05f603c**. Original source raw-tree lineage is inherited, not a new independent serialized-object/UnityFS decoder.

Blob start0/stop6.9666666984558105/cycleOffset0. Prepared clip's blob and node's blob are the **same address**. Prepared node double clocks are generated as requested normalized-double×native-f32duration; direction1,offset0,quantization−1,loop byte adapted from serializedtrue. Those clock/control values remain fixture inputs, not live node values.

| Requested normalized double | Native current f32 bits | Native sample-time bits | Staged native instructions |
|---:|---:|---:|---:|
|0|0|0|3065|
|0.25|1048576000|1071574767|3020|
|0.7|1060320052|1083968936|2361|
|1|1065353216|0|3068|
|1.25|1067450368|1071574767|3020|
|−0.25|3196059648|1084699443|2384|
|−1|3212836864|1088351983|1555|
|0.7,rewind|1060320052|1083968936|5635|
|same|1060320052|1083968936|1408|
|**0.99999999**|**1065353216 (=1.0)**|**0**, loop boundary|3068|

All**10×93=930DWORDs** match separately computed directed conversion,116time reference and115separate-f32 packed traversal. Query0.99999999is below1in double but context becomesf32one and native loop samplesstart. This is a fixture counterexample to treating double time as exact native normalized phase, **not an observed game timing bug**.

Counts from traces: **12standalone context cases /718native instructions /0external substitutions**; **10source+8synthetic staged samples /31272native instructions /18modff substitutions**. Context prefixes use no duration hook. Only native time conversion's explicitly bridged`modff` is reached during these samples; no memcpy because these sample inputs are streamed-only. Initialization allocations and excluded caller instructions are not included in sample counts.

Synthetic controls separately test raw negative-zero sign, direction/offset, quantization and loop effects through the writer and staged consumer. The original game's nonempty dense/constant usage is not asserted (116source1609dense curves0 remains scoped to that clip).

## 6. Pins / reproducibility

Recovery **40326227797 SUCCESS**, source **aed9131437d55e358e00cd2919c703b7d63bab61**, raw commit**ca1a449a8**. Original cache fail-on-miss, no static evidence from a modded vehicle. XAPK SHA**f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e**; libunity SHA**d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7**.

| Tool/input | SHA256 |
|---|---|
|`reverse-engineering/raw/context117/probe.json.gz` (36176B)|`9bfa2fdd7f0a015b9a1ea17306c7fef8627a6410f845b4940aa19ea708d2bf60`|
|`datas/l3_ef6b75ef117_native_clip_context.json.gz` (5925B)|`ef1d97806f66c54daa4399237fc5df6e72950facd805b6093733644b55e40e85`|
|`tools/recovery/context117.py`|`7be70a946fa2b821cd125e6ef69f9f4c95a734afc32e7bbab2c730190b238809`|
|`tools/verify/context117.py`|`5bc97417f7305d1ad3de469f3417b752e2a05b2e22d578402f7298a2685ffc4f`|
|`tools/verify/context117_native.py`|`1e117ee1aa2c29539fd69a316d451ed7add98edd8ea44e4aa6e00af3253a8e4c`|
|`tests/test_context117.py`|`a76764704eb0cd9b80c1d051760cbd3717308e370de267bb62685517ce218a73`|
|Reused115raw|`9b2b21a61fe9b459b4815ab5361576f036c873f36da9ecbce2a25ac618e1d364`|
|Reused116raw|`1dfa2ca9ab5851d75e969d75428d4f96891464ddc7a6ba583103b87833539c31`|
|Inherited source gzip|`cac775a419758a7ef51e74a9ad1d7a6e1040faaf69d28fb84d9311d978aec082`|

Artifact also pins reused116fixture/reference,115reference,114float helpers and113guard. No old source/model is changed. New raw retains2original FDE followed entries,7selected direct caller sites,18selected windows and46metadata/literal cells;18selected string/function RELA backreferences include vtable neighborhoods. Capture counts/candidates are **not executed-function coverage**. Exact constructor operands/RELA/method bytes, not just adjacent ADRP references, establish vtable dispatch. No implicit original-page zero fallback.

```sh
python3 -m tools.verify.context117 --check
python3 -m unittest tests.test_context117 -v
python3 -m unittest discover -s tests -v
```

**40focused PASS /2.351s**, deterministic byte-for-byte artifact check PASS. Tests cover pins/FDE, constructor/vtable/slot read, real duration/null/subtraction, directed conversion/current+previous/subnormals/negativezero, raw field copies/nonzero prefill, exact stage entries/native query load/native phase store, source930DWORD equality and rewind/boundaries, controls, two opcode counterfactuals, base relocation and refusal to promote to observed Animator state. Full/CI receipts appended after completion, no inferred CI count.

## 7. Remaining #27 and coordination

- Native context **materialization from prepared node** is now executed. Actual node creation, game-side clock/direction/offset/quantization/loop field writers, graph setup, state/layer/transition scheduling and source-instance acquisition are still **not observed/proved end-to-end**.
- Full caller`0x6d38bc`, optional previous-time handling, downstream channel/pose conversion, quaternion normalization, weighting/blending, property/PPtr application, bootstrap/readback/render remain open. Staged source sampling is not full Animator playback.
- Exact public `AnimationClipPlayable` icall-name searches and managed-name references are retained as discovery only; no public-runtime type identity is inferred from name proximity. Clip constructor/vtable and context dataflow are the actual proof here.
- Independent review requested: constructor→vtable+A8→duration blob linkage, directed f64→f32 edge/guard behavior, actual copied field offsets, staged-entry register/context boundaries, same-blob source reuse, numeric counts and service tiers. **No selfACK/full#27closure.**

Coordination from external6416406730:116bounded composition ACKed; vehicle modification permissions widened by spec but original APK remains static authority and runtime vehicle lane remainsa5's. No vehicle work/modification performed here. The spec's dense observation is retained **only for clip1609**, not adopted as a global all-build dead-path claim. External6416527317cross-build runtime catalog is reported by spec, not independently revalidated in this batch. Peer#4handoff6416546977and#6replicationclaim6416555265stay owned by8141386a; no glyph/atlas/runtime tools imported or overwritten. Protected3paths remain absent/unchanged at117baseline/current. No original APK/assets/file>5MB committed, release changes, main push, merge, screenshot/redraw or render acceptance.

## Final verification receipt

- **Full local1531tests PASS /275.071s**; focused40PASS/2.351s. Actual compressed logs retained under `reverse-engineering/raw/l3-ef6b75ef117-verification/`, not hashes only.
- **Verify40326789273 completed SUCCESS at exact scientific7f182db37d0a8232bf429fb20b8427fa076fc062**. REST run/jobs saved as`ci.json`/`ci-jobs.json`; local counts from actual logs, no invented CI count.
- Deterministic byte-for-byte artifact check PASS; `git diff --check` PASS; protected3paths absent/unchanged, new files<5MB. Local Python3.11.2/capstone5.0.3/unicorn2.1.4/Pillow12.0.0 saved in`local.json`; local heavy jobs sequential.
-116externalACK6416406730 synchronized;117independent disposition pending, no selfACK/full#27closure.

Official PR12 HANDOFF **6416723856** posted after push/remote confirmation/exact-head CI. Receipt `reverse-engineering/raw/l3-ef6b75ef117-verification/handoff.json`; independent disposition pending, no selfACK.

External disposition update: spec **6416823283** independently ACK/CLOSES **117bounded clip-context**, not full#27. Receipt retained in `reverse-engineering/raw/l3-ef6b75ef118-verification/spec-ack117.json`. Clarification posted/retained in`rounding-clarification.json`:117conversion is nearest FCVT followed by directed ULP adjustment, **not tie-away**;116FRINTAquantization is separate.118executes complete current-only/no-pose caller without117manual intervals; actual game node/flag/rig/graph state remainsunobserved.
