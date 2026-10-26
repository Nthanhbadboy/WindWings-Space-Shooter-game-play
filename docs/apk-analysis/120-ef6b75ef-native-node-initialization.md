# 120 — original node constructor, native pool acquisition and source integration

**Provisional / arena/ef6b75ef / #27.** Claim **6417390505**. Scientific **10b46c13d32592953416389bdf2d0407a8fd434d**. This advances node initialization, **not observed game-side creation, graph binding, factory/handle attachment or active pose application**.119parent remains the same bounded no-pose chain.

## 1. Actual constructor and caller linkage

Original FDE **6d353c..6d35f8**,188B, enters at6d353cand returns at6d35f4. It invokes original base **6d6aa0**, which invokes **57054c**, and original member initializer **6a6ff4**. No manually staged constructor intervals or host setter substitutes are used.

Native stores install primary vptr **10b1240** atnode+0 and secondary vptr **10b1420** atnode+110. Original ELF RELA at **10b12c0 = primary+80** resolves **6d46a8**, the119parent. This establishes the constructor-installed table's link to the caller chain; it is NOT a captured game virtual dispatch or proof that a real graph selected this node.

Direct original constructor caller is **6d5e58..6d5ec8**: it calls allocation routine3c986c, calls6d353c, tests flags and calls handle-related570ff0/572a38. Its bytes are captured via original direct-branch/FDE recovery, but **the factory is not executed**. An incoming argument contributes to requested allocation size via+200; do not promote the minimum200B constructor footprint to a universal final allocation size. No API/class name is inferred merely from this proximity.

## 2. Base services: native execution over explicit prepared state

Base57054csets fields and calls57ef84with null argument, then original singleton getter **575e80** loads **116cb40**. Original **575c60** obtains a pool chunk through atomic-pop **53f36c**. All of these execute as captured ARM64 instructions, including exclusive load/store loops; no method/service sink is installed during construction.

The fixture explicitly supplies these external prerequisites:

-200B object storage, initially0xA5 (also0and0xFFvariants). This is not allocator execution.
- Synthetic global116cb40→service; service+450→prepared queue, queue→prepared chunk and tag. This is **not native service/bootstrap initialization or a captured Android process global**.
- Chunk has a32B array with encoded capacity8 (=4slots), prepared length0and queue-next null. Additional tests use old length3and tag41. Native acquisition resets length, then base constructor appends a null entry; the pre-acquisition length is not retained.
- Integer label supplied in W1 (94or7variants), copied natively into node+18. It is an input label, not asserted type/class ID.

Observed native effects: queue head becomes null; queue tag increments once; acquisition counter at service+43cincrements to1; chunk length becomes1and slot0becomes null; node+30points at that acquired chunk. Allocation fallback575b34and growth573a1care **not executed** because the supplied pool/capacity suffice. Their original bytes are captured, not globally dismissed as dead paths. Atomic behavior is tested single-threaded in Unicorn, not Android concurrency parity.

Each selected constructor run executes **174original instructions /0external substitutions**, reaches originalRET6d35f4and restores entrySP. `sinks` is forcibly empty during construction, so any accidental dependency on an inherited host bridge would fail instead of silently succeeding. Parent fixture's earlier clip-cache setup uses its inherited declared allocator, outside the constructor interval and its count.

## 3. What native code initializes — and what it preserves

Memory-write hooks record actual native write PCs/offsets/sizes. Over a200B footprint, **447unique byte offsets are written,65are untouched**. This does NOT mean447bytes are zero or65bytes are semantically padding. Some may be other fields; unnamed preserved offsets are retained as such.

| Field | Native constructor result |
|---|---|
|+0 /+110|primary10b1240 /secondary10b1420vptr|
|+18|incoming W1label|
|+30|acquired prepared pool chunk pointer|
|+3c DWORD|3|
|+60 double|0(current-clock field later read by context writer)|
|+118 /+120|0|
|+128 /+130 /+138|0|
|+150 /+158|0|
|+178 double|0(previous-clock field)|
|+184 float|1|
|+188 byte /+18c DWORD|0|
|+190 byte|1|
|+194 /+198 float|−1 /−1|
|+19c..19d|0|
|+1d0|0(clip pointer)|
|+1d8..1ef|member initializer zeroes24B|
|+1f0 byte|1|
|+1f1..1f8|0|
|+1fc float|−1|

Base+38DWORD is **read/modify/write**: low12bits become101hex, higher bits retain storage prefill. This is not a whole-object memset. Tests compare written bytes between A5andzero cases except retained upper bitfield bytes39..3b; all untouched offsets preserve their prefill. The artifact includes complete images, write events and coverage partition, so unnamed fields are not guessed from screenshots or host structures.

Constructor initialization replaces earlier harness-only defaults for these written fields, but it does not discover the subsequent original writers that attach a clip/cache/output or advance clocks.

## 4. Integration with unchanged source1609

A source fixture is constructed, its node storage is overwritten withA5, and the **original full constructor** runs on it. Only then the harness explicitly installs these four pointer bindings:

- node+118→prepared blob containing unchanged source words;
- node+128→prepared stream cache;
- node+130→prepared current-output holder;
- node+1d0→prepared native clip whose original duration vtable getter is retained.

Clock/control/loop settings are subsequently supplied by `configure_node`, still fixture inputs. These post-constructor writes are not concealed as original graph acquisition. Rig flags/descriptor/TLS remain synthetic and current-only/no-pose restrictions unchanged.

Ten original119parent calls on this initialized node produce **930DWORDs bit-equal to the pinned118artifact** for the same queries, including rewind/repeat/end boundaries. This is shared-lineage regression/composition, **not independent UnityFS extraction, a live node capture, or newly independent interpolation proof**. Source data and reference lineage remains115–119. No pose/apply/readback/render claim follows from constructor success.

Counts distinguish3standalone constructor cases,1constructor for source integration and10source-parent sample calls. Relocation/prefill/label/queue variants in tests are not added to those artifact-case counts.

## 5. Pins, recovery and checks

Final recovery **40332491334 SUCCESS**; recovery source **7715cb756**, raw commit **d6a33c2d5**. Earlier40332280677captured root constructors but not all base prerequisites; it is superseded by the bounded final raw.13originalFDEroots/dependencies, not whole-lib or whole-graph coverage. Both captures use the pinned original XAPK/cache fail-on-miss, no APK changes.

| Tool/input | SHA256 |
|---|---|
|raw/node120/probe.json.gz,4357B|`d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950`|
|datas/l3_ef6b75ef120_native_node_initialization.json.gz,6484B|`fe2c0997d2ecf28e2f2ea4f06376d7e51fecebe7c47d135e4523acbd0f498c0e`|
|tools/recovery/node120.py|`48fb0002d4d4aad006283a146e179d09ba1d0b4d3ac9ea52919d7161d4286e8c`|
|tools/verify/node120.py|`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`|
|tests/test_node120.py|`1b72b19e1479ee109b1482699f9e2b142b18027114bf6ba3353464c38f36cbd6`|
|tools/verify/parent119.py|`d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`|
|tools/verify/tag23_113_native.py|`6bbabc6eaa3934e81f0fc6659769b35fc372a3823b59ee6473ee7c5bdb307421`|
|118artifact|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|119artifact|`49eb74d14c974dafabae8dc5cbe30804f9872edee25807c2e16adaecd73de78f`|

Full raw path: `reverse-engineering/raw/node120/probe.json.gz`. XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7. All direct inputs are pinned in120artifact; inherited source/tools transitively pinned in118/119artifacts. No fresh source decode is claimed.

```sh
python3 -m tools.verify.node120 --check
python3 -m unittest tests.test_node120 -v
python3 -m unittest discover -s tests -v
```

**20focused PASS /1.133s; deterministic byte regeneration PASS**. Full suite/exact-head CI receipts will be appended after actual completion, not assumed from earlier119tests.

Review requested: FDE/entry/base/member/RET provenance; constructor vptr versus actual indirect dispatch; native pool pop/counter/append versus synthetic service initialization; write coverage/retained bitfields rather than memset; explicit post-constructor bindings and source-shared lineage; original factory not executed. **No selfACK/full#27closure.** Original allocator/factory/handle attachment and game graph creation, service/bootstrap, clip binding and clock/control writers, previous/activepose/conversion/blend/normalize/apply/Unityreadback/render remain OPEN. a5runtime/primary and8141386a#6rep ownership retained. Protected3/main/merge/release unaffected; no APK/original assets or file>5MB added.

## 6. Actual verification and external coordination

**20focusedPASS/1.133s; full1601PASS/277.824s; deterministic artifact`--check`PASS; Verify40332906465SUCCESS exactscientific10b46c13d32592953416389bdf2d0407a8fd434d.** Recovery40332491334SUCCESS/source7715cb756/rawd6a33c2d5. Actual compressed logs, RESTrun/jobs, local/check/recovery receipts in`reverse-engineering/raw/l3-ef6b75ef120-verification/`; protected3absent/unchanged. Full suite and full artifact regeneration were run sequentially, avoiding113memorythrashing. No preview/render/screenshot gate inserted.

External spec **6417392256 ACK/CLOSESbounded119** (artifactSHA49eb74d14c97,930DWORDs,29974instructions,3guards,node174 counterexample, reject active rig); it does NOT ACK120 or close#27. Receipt in120-verification/spec-ack119.json and appended to119 report. Independent120review pending.

Exact tool pins: verify/node120.py`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`, tests/test_node120.py`1b72b19e1479ee109b1482699f9e2b142b18027114bf6ba3353464c38f36cbd6`, recovery/node120.py`48fb0002d4d4aad006283a146e179d09ba1d0b4d3ac9ea52919d7161d4286e8c`. 174instructions/447written/65preserved are for each selected standalone constructor; 930DWORDs are across10sourcecalls and exclude3standalone source-check variants. Constructor standard test relocation/variant invocations are not counted as artifact source cases.

Official120HANDOFF **6417679550**; scientific10b46c13d/report81c9677eb/exact-headCI40332906465/1601localPASS. Independent review pending, no selfACK/full#27closure.
