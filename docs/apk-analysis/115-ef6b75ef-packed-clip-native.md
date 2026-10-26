# 115 — original packed StreamedClip consumer + native AnimationClip ownership

**Provisional / arena/ef6b75ef / #27.** Claim PR12 **6415645613**. Scientific commit **61de2d57ef4898fb753bdcb714706a68d71215c2**. Continues114, does not rebrand its AnimationCurve arithmetic adapter as playback. External spec **6415645102** ACK/CLOSES **114 bounded native-core only** and explicitly leaves #27 consumer/dense/weighting/runtime open. That is external disposition, not self-ACK.

## 1. New result and exact boundary

Original libunity functions **`0x6df270 → 0x6df310 → 0x6df768`** actually consume the packed stream: choose frames from time, copy keys into channel-indexed records, evaluate continuous scalar/SIMD cubics, and copy discrete DWORDs unchanged. No AnimationCurve cache injection is used for115. Native cache initialization **`0x6df02c`** also executes; its one allocator service is explicitly substituted. **No external function/service substitution during any sample.** Unicorn tracing/read guards remain enabled throughout.

For original `resources.assets:1609`, copy **all2262 uint32 words / 9048bytes** unchanged from the pinned raw extraction into native memory. Native sampler consumes **92continuous +1discrete channels** at **10sample calls**, including rewind and duplicate time: **930channel values**, all bit-equal to a separately evaluated f32 comparison. This is a native function/data-layout fixture, **NOT full AnimationClip playback, engine scheduling, Unity readback, Animator blending/application, or render**. Header pointers/cache/output are constructed fixture memory, not captured runtime objects. The source raw tree is inherited APK extraction, not a new independently decoded UnityFS/serialized-object receipt.

## 2. Ownership is a byte-level field/dataflow chain, not proximity

Original `AnimationClip` native type record **`0x10f29f0`** has classID**74**, native size**592**, name RELA at+24→`0xe7bdf` (`AnimationClip`), descriptor+88→`0x10e8b90`. The record is corroborating class identity; we do not claim to execute class registration/bootstrap.

| Original link | What bytes establish |
|---|---|
| Registration `0x399814` names `UnityEngine.AnimationClip::get_length`; callback address `0x398600` | Named AnimationClip native API entry |
| `0x39868c → 0xb6a84c → 0xb6bb88` | API's native method chain; at`0xb6bbd0` reads owner+`0x1e0` |
| `0xb6b944 BL 0x6ad7e4`, then `0xb6b948 STR x0,[x19,#0x1e0]` | Native compiler result stored in that owner field; caller FDE starts`0xb6ab88` |
| `0xb6dff0..0xb6e014` | Serializer uses exact string`m_MuscleClip` and passes owner+`0x1e0`; not merely an adjacent field-name reference |
| Accessor `0xb69cf4` | Loads owner+`0x1e0`, checks non-null and owner+`0x1e8` nonzero, returns blob or null; validity/version gating is preserved, not assumed universally valid |
| Parent `0x6ad7e4` | Creates0x48-byte ClipConstant through`0x6deeb8`; stream producer`0x6c4480` at`0x6adbe4/0x6adc98`, packer`0x6c498c` at`0x6add58` (114 evidence retained) |
| `0x6add6c → 0xb922a8` | Allocates0x960-byte muscle blob; original`0xb922e0..0xb92300` stores relative pointer to ClipConstant at blob+`0x5f0` |
| `0x6d2ee0..0x6d2f00` | Reads/resolves same relative pointer blob+`0x5f0`, calls ClipConstant dispatcher`0x6df270` |
| `0x6df2ac → 0x6df310`; `0x6df328 → 0x6df768` | Dispatcher calls actual streamed sampler, which calls actual packed frame selector |

`0x6d38bc` and`0x6d3ebc` statically call`0x6d2e94`; the latter resolves blob+`0x5f0` before dispatch. Other original direct caller sites are retained in raw. These caller bodies/time wrapping/blending are **not executed** in115. Thus the old ownership gap is materially narrowed by the named native API + serializer + compile result field + same blob-relative header + actual consumer chain; it is not an executed Animator object identity/scheduling proof.

## 3. Actual native layouts and selection

Addresses below are runtime layouts evidenced by instructions, **not serialized-file offsets**.

- ClipConstant starts with StreamedClip: wordCount DWORD+0; data pointer is relative QWORD at+8 (relative to its own address); continuous count U16+`0x10`; discrete count U16+`0x12`. Dense member starts+`0x18`; constant member+`0x38`.
- Cache: records pointer+0; continuous/discrete U16+8/+10; last sampled f32 time+12; next packed-frame byte offset DWORD+16. Initializer clears **20bytes per channel** and sets last time to−Inf/next offset0. Source initialization requests **1860bytes/alignment4**, executes **597native instructions**, with one allocator substitution; it does not depend on prefilled zero memory.
- Packed frame: time f32 + keyCount DWORD = **8byte header**; each key **20bytes** `[channelIndex,a,b,c,d]`.
- Cache record is also20bytes but different: `[frameTime,a,b,c,d]`, indexed by channel. Selector`0x6df768` obtains record address from the **key's index**, not key position.
- Same time returns immediately from selector; increasing time resumes next frame cursor. Rewind resets cursor0 and replays frames. This does **not clear every record on rewind**; valid source initial frames populate channel history. No general malformed/incomplete-initial-frame semantics are claimed.
- A frame is applied when **frameTime ≤ sampleTime**. It advances by `8 + keyCount*20`, stopping when next frame time is greater than query. The source terminal+Inf header is at byte**9040**; finite samples leave it unconsumed.
- Continuous arithmetic is separate f32 multiply/add **`((a*dt+b)*dt+c)*dt+d`**, dt=`sampleTime−cachedFrameTime`. Scalar at`0x6df43c..0x6df478`; four-channel SIMD at`0x6df36c..0x6df42c`. This is the packed consumer's own instructions, **not proof by generic AnimationCurve equivalence**.
- Discrete channels copy coefficient d as an **unchanged DWORD**, scalar/vector paths. No polynomial, interpolation, float→int conversion or PPtr resolution is performed by this function. Synthetic NaN payload`0x7fc12345` is preserved. At source stop time, final discrete DWORD is**1084227584 /0x40a00000** (float reinterpretation5.0), **not an asserted integer object index or resolved Sprite**.
- Fixture API deliberately accepts only finite f32 sample times. +Inf would reach terminal sentinel handling outside this finite-domain proof; no engine endpoint policy is invented.

## 4. Original-source sample receipts

Raw location `reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz`, **zero-based row140**, serialized file`data.unity3d/resources.assets`, pathID**1609**, class`AnimationClip`. Original object SHA**69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae**. Packed data SHA**a21ecdaa8cc6e10730d6de9aa1e45ba319ad05d31dbb3998def8d418d05f603c**. Start0, stop6.9666666984558105. No decoded key or host-selected segment is supplied to the native sampler.

| Query f32 | Next native frame byte cursor | Native instructions, dispatcher included |
|---:|---:|---:|
|0|3656|2872|
|0.10000000149011612|3656|1213|
|0.20000000298023224|3656|1213|
|0.36666667461395264|4272|1504|
|0.5|4564|1367|
|1|6040|1953|
|3.4000000953674316|7700|2055|
|6.9666666984558105|9040|1929|
|0.10000000149011612, rewind|3656|2875|
|same time repeated|3656|1201|

**18182native sample instructions** for these10calls; initialization counted separately. Full artifact's synthetic families add25calls: channel splits1/0,3/2,4/4,5/5,8/8 exercise scalar, SIMD, tails, reordered keys, endpoint, rewind and same-time fast path. Combined35sample calls execute **23277native instructions**. These are measured hook-trace counts, not estimates, number of captured functions, or Unity frames.

Comparison code traverses packed data independently after defining input bytes, tracks latest key per channel, and rounds each multiply/add to f32. All930source DWORDs match; synthetic assertions and opcode counterfactuals independently test native dependence. This comparison is still a model/check, **not Android-device readback or a universal numerical bound**. No legacy sampler/model is changed.

## 5. Reproducibility / pins

Recovery **40321260553 SUCCESS**, source commit**d11ceabc9a84ccc426d05a6eb2d7832df2a05b41**, raw commit**7b4c31a87**. Workflow uses fail-on-miss original cached XAPK and preserves raw, no replacement APK/loader. XAPK SHA**f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e**; libunity SHA**d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7**.

- Raw `reverse-engineering/raw/packed115/probe.json.gz`: **147996bytes**, SHA**9b2b21a61fe9b459b4815ab5361576f036c873f36da9ecbce2a25ac618e1d364**.
- Artifact `datas/l3_ef6b75ef115_packed_clip_native.json.gz`: **12740bytes**, SHA**32f8105361ccd0f65c6fbe44f674ea48e88f42c541090c75c4b5fb979d559d20**.
- Recovery tool `tools/recovery/packed115.py`: SHA**4c0533581881f552f02c95b37ee7e5ea3396c405a9c1b6f02731aaf1058711c5**.
- Builder `tools/verify/packed115.py`: SHA**4984fce43063beaed12587e5f4c08f47708592a7f02d95576222821966a5ef1f**.
- Fixture `tools/verify/packed115_native.py`: SHA**ab67ac459ff6e701c60081a3712d828a7bfd59c39bacecc4590707672144755d**.
- Tests `tests/test_packed115.py`: SHA**7a0533c865a1d1993ac984bd215c7d5f2c0e93f8c505459cf24c6e6935cca276**.
- Source raw gzip SHA**cac775a419758a7ef51e74a9ad1d7a6e1040faaf69d28fb84d9311d978aec082**. Artifact additionally pins unchanged113guard/114float helpers. All input/tool SHA are in artifact and tested.

Raw retains113followed entries,340FDE extents in selected runtime region,41structural candidate functions,18direct caller sites,165byte windows and276literal/metadata cells. **Capture counts are not execution coverage**; candidates outside the proved chain are not accepted by structural resemblance. Full original FDE records/table bytes are retained. No captured-page implicit-zero fallback: fixture guards original code/data spans; synthetic regions/allocator are explicit. Recovery ADRP discovery remains candidate-only until exact operand/dataflow inspection.

Reproduce (Python3.11/3.12, capstone5.0.3, unicorn2.1.4; full suite also Pillow12.0.0):

```sh
python3 -m tools.verify.packed115 --check
python3 -m unittest tests.test_packed115 -v
python3 -m unittest discover -s tests -v
```

**40focused tests PASS in1.061s**, deterministic byte-for-byte `--check` PASS. Tests include exact native instructions/field linkage, original FDE extents, nonzero prefill, scalar/SIMD/tails, sparse/reordered channel keys, rewind/same-time behavior, source930DWORD equality, two native opcode counterfactuals, altered packed key index, relocated fixture base and discrete NaN payload preservation. Full regression/CI receipt is recorded below after completion, not inferred from workflow status.

## 6. Remaining #27 / review requests

1. **Dense** function`0x6df518 → 0x6df6c8` is identified in original byte capture but **unexecuted here**. The helper calls ELF import at`0x109b800`; do not silently replace it with ideal linear math. Constant channel/helper branches also are not exercised by this source's streamed-only dispatcher fixture.
2. `0x6d2e94` time conversion invokes`0xb93158` before dispatcher; loop/start/stop semantics and higher-level clip time ownership are **not executed**. No automatic equivalence to serialized/public wrap enums.
3. Quaternion handling, clip weights, Animator state/layer scheduling, blend/normalization, property/PPtr application, class bootstrap/services and Unity readback/render remain open. Previous113bounded mapping ACK is not runtime application proof.
4. Producer/packer parent is statically linked;115 does not retroactively execute114's excluded sort/reserve/final-sentinel/allocator/destructor suffix. Original source stream includes terminal sentinel; that is not full-packer execution proof.
5. Independent review requested: owner+`0x1e0`/blob+`0x5f0` correspondence; original/header adaptation versus serialized widths; equality boundary/rewind/cache assumptions; scalar/SIMD separate arithmetic; discrete raw-bit meaning; counts and coverage tiers. **No self-ACK/full#27 closure.**

Coordination: external6415645102 also ACKs a5's bounded#25 slice and#28fallback①; broad durability/cloud/runtime and loader②③ remain theirs/open. Peer handoff6415743906 handles#26Board_Pause static-root/projection audit; it is not imported or taken over here. No peer geometry/driven/simulation work. Protected `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, `datas/player_start_stats.json` unchanged/absent at115baseline and current tree. No file>5MB added, APK/assets committed, release change, main push, merge, screenshot/redraw or render acceptance.

## Final verification receipt

- **Full local1451tests PASS /263.951s**, actual compressed log `reverse-engineering/raw/l3-ef6b75ef115-verification/full.log.gz`; focused40PASS/1.061s retained alongside it.
- **Verify40321809391 completed SUCCESS at exact scientific61de2d57ef4898fb753bdcb714706a68d71215c2**. REST run/jobs saved as`ci.json`/`ci-jobs.json`; local test counts are from actual logs, not inferred from CI status.
- Deterministic artifact check PASS, `git diff --check` PASS, protected3paths absent/unchanged and no new file>5MB. `local.json` retains tool versions and compressed-log hashes; actual local Python3.11.2, capstone5.0.3, unicorn2.1.4, Pillow12.0.0. Source/model heavy jobs were run sequentially.
- Independent115review pending;114externalACK6415645102 synchronized in114report/HANDOFF. No selfACK/full#27closure.

Official PR12 HANDOFF **6416031711** posted after push/exact-head CI. Receipt `reverse-engineering/raw/l3-ef6b75ef115-verification/handoff.json`; independent disposition pending, no selfACK.
