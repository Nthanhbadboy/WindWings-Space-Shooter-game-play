# 116 — native normalized clip time → streamed/dense/constant dispatcher

**Provisional / arena/ef6b75ef / #27.** Claim PR12 **6416092786**. Scientific **61f31ae26f23908ffa2b281e6dee6e1427c5fcb8**. This extends115's actual packed-stream consumer, not its old AnimationCurve arithmetic adapter.

External spec **6416110827** independently ACK/CLOSES **115 bounded packed-clip consumer**; full#27 remains open. It also assigns runtime loader/probe work to **a5a74747**, not this lane. No takeover, main push, merge, selfACK, device/readback/render claim.

## 1. What actually executes now

- Original **`0x6d2e94 → 0xb93158`** converts a normalized query into clip sample time, then original **`0x6d2f00 → 0x6df270`** dispatches streamed/dense/constant sampling. The blob+`0x5f0` relative pointer is negative in this fixture and is resolved by original instructions, not a host-selected target.
- Source `resources.assets:1609`: all**2262original uint32 words /9048bytes** are copied unchanged, with original serialized start/stop/cycle metadata placed at instruction-proved native offsets. **10queries ×93channels =930DWORDs** match separate-f32 comparison. Unlike115's seconds-only sampler calls, these queries pass through actual native time conversion first.
- Dense **`0x6df518 → 0x6df6c8`** executes on explicitly **synthetic nonempty dense arrays**. The source clip has **frameCount420, curveCount0, sampleArray[]**; its dense branch is skipped. Frame count alone is not a claim of missing420frames or nonempty dense observations.
- Mixed synthetic input proves dispatcher output order **stream continuous → stream discrete → dense → constant**, including a complete time→mixed call. Native constant helper`0x6d9200` reaches original memcpy PLT.
- Original aggregate cache initializer **`0x6deefc → 0x6df02c`** executes. Source requests **32B/alignment8** for cache and **1860B/alignment4** for93records, **632native instructions**, allocator substitutions only during initialization. Mixed fixture2stream channels requests32B and40B,86instructions; dense-only cache requests32B,60instructions. Nonzero prefill does not supply outputs.

### Explicit service tiers

**No zero-hook claim for116 time/dense calls.** Original ELF imports are bridged deliberately:

| Original PLT | Original GOT | Symbol | Substitution |
|---|---|---|---|
|`0x109b800`|`0x10e42a0`|`modff`|Host `math.modf`, write f32 integer part through original x0 pointer and return f32 fraction inS0; signed zero retained|
|`0x109acd0`|`0x10e3d08`|`memcpy`|Bounded exact byte copy into prepared output, source-read/destination bounds checked|

PLT instruction pattern/GOT address and exact ELF symbol entries are checked, not a generic unknown-call fallback. Only these two imports are bound. Original code before/after import calls runs natively. **Not Android-libm ULP parity or platform ABI/runtime proof.** Bulk copy is not an engine getter/setter/readback substitute. Tracing and original-data read guards remain active.

## 2. Data-layout and parameter provenance

Original string+transfer instructions in new raw:

- `m_StartTime`: `0xb704d0`, pointer at`0xb704d4`→blob+`0x5f8`.
- `m_StopTime`: `0xb70504`, pointer at`0xb70508`→blob+`0x5fc`.
- `m_CycleOffset`: `0xb705a0`, pointer at`0xb705a4`→blob+`0x608`; same offset corroborated by original reader at`0xb7548c`.
- Runtime caller`0x6d2e94` loads these exact three fields. Context+16 is added to blob cycle offset, then query is passed to`0xb93158`; start/stop also supplied directly.
- Dense header at ClipConstant+`0x18`: frameCount+0, curveCount+4, sampleRate+8, beginTime+12, sampleArrayCount+16, relative sample pointer+24.115's serializer anchors and116original `m_SampleRate`/`m_BeginTime` transfer captures corroborate sampleRate/begin offsets. Runtime helper directly uses these fields and frame-major indexing.

**Prepared context is not an observed Animator context.** Here context+8=1 supplies sign control; context+16=0 supplies offset; context+24=−1 disables quantization. The loop bit passed inW4 is explicitly adapted from source serialized `m_LoopTime=true`.116 does **not** prove higher caller acquired that bit/context from this source instance at runtime. Serialized clip sampleRate60 is **not automatically used as the context quantization control**. Synthetic control cases enable quantization explicitly.

Helper ABI from original dataflow: S0normalized query; S1start; S2stop; S3offset sum; S4raw sign control; S5quantization control; W0loop bit; X1phase-output pointer; X2cycle-output pointer; returnS0sample time. These are bounded native-function meanings, **not asserted public enum/API mapping**.

## 3. Native time behavior, including counterexamples

Let q=input query, offset=provided offset sum, D=stop−start, operations rounded to f32:

1. Always calls`modff(q+offset,&cycles)`, even for nonloop mode.
2. If loop bit0: phase=`clamp(q,0,1)` (unshifted q), cycles=0. Nonloop phase therefore ignores offset.
3. If loop bit1: uses modff fraction/integer. When **q+offset<0**, adds1to fraction and subtracts1from cycles. This also applies to exact negative integers.
4. Extracts **sign bit ofS4**, not the predicate`S4<0`: negative sign flips phase to1−phase and negates cycles for loop mode. **−0.0 flips direction**, unlike+0.0.
5. Sample time=`start + D*phase`. If **D>0 andS5>0**, original **FRINTA** rounds sampleTime*S5 to nearest integer with ties away from zero, then divides byS5. Returned phase is recomputed/clamped0..1 after quantization; **returned sample time itself is not clamped back to start/stop**.

Counted native helper samples include:

| Fixture inputs | Original result |
|---|---|
|loop q=1,start0,stop1|sample0,phase0,cycles1|
|loop q=−1|**sample1,phase1,cycles−2**, not Python`−1%1=0`|
|loop q=−0.25|phase0.75,cycles−1|
|q0.25,offset0.5,loop|phase0.75|
|same,nonloop|phase0.25|
|q0.25,S4=−0.0|phase0.75|
|q0.25,start2,stop4|sample2.5: confirms normalized-unit input, not seconds|
|q0.25,S5=2|sample0.5: tie-away rounding, not banker rounding|
|nonloop q1,start0.1,stop0.9,S5=2|**sample1.0 >stop0.9**, phase1|
|q0.25,start=stop=2,S5=2|sample2,phase0.25; guarded quantization not selected|

Do not replace this with a universal `%duration` or clamp-time model. These are finite-input fixture results in original instructions with declared modff service. No universal special-value/FP exception or Android-libm bound is claimed.

## 4. Native dense behavior is not unconditional endpoint clamping

Helper`0x6df6c8` computes f32 u=`(time−begin)*rate`, calls`modff`, truncates its integer part, selects two frame rows with clamped indices, and returns the **original signed fractional part**. Sampler`0x6df518` executes f32`left + fraction*(right−left)` independently for each curve. It does not clamp that fraction.

Synthetic fixture:3frames ×2curves, rate2, begin0.5, frame-major values`[0,10, 10,20, 20,30]`.

| Time | u | Output |
|---:|---:|---|
|0|−1|[0,10]|
|0.25|−0.5|**[−5,5]**, backward extrapolation because trunc(−0.5)=0, rows0/1, fraction−0.5|
|0.5|0|[0,10]|
|0.75|0.5|[5,15]|
|1|1|[10,20]|
|1.25|1.5|[15,25]|
|1.5|2|[20,30]|
|2|3|[20,30], both rows at last|

Thus the stronger statement “negative dense time always clamps values to first frame” is false for this native function. **Not a claimed observed game bug**: nonempty dense values here are synthetic, and game callers may constrain time domains. Source1609has zero dense curves.

Mixed synthetic fixture has1continuous +1discrete +2dense +2constant. At t0.25 output is `[bits(0.15625),1001,bits(5),bits(15),bits(77),0x7fc12345]`; arbitrary discrete/constant DWORDs retain bit identity, including NaN payload. No resolved PPtr, Sprite, quaternion normalization or property application is inferred.

## 5. Original-source full-chain receipts

Inherited raw tree: `reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz`, zero-based row140, `data.unity3d/resources.assets:1609`. Original object SHA**69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae**; unchanged packed data SHA**a21ecdaa8cc6e10730d6de9aa1e45ba319ad05d31dbb3998def8d418d05f603c**. Not a new independent UnityFS/serialized-object decoder receipt.

Serialized start0,stop6.9666666984558105,cycleOffset0,looptrue. Context1/0/−1and W4loop mapping are declared fixture adapters, not captured runtime state.

| Normalized query | Native stream sample time | Returned phase | Native instructions, full caller included |
|---:|---:|---:|---:|
|0|0|0|2984|
|0.25|1.7416666746139526|0.25|2939|
|0.5|3.4833333492279053|0.5|1799|
|0.75|5.224999904632568|0.75|1830|
|1|0|0|2987|
|1.25|1.7416666746139526|0.25|2939|
|−0.25|5.224999904632568|0.75|2303|
|−1|6.9666666984558105|1|1474|
|0.25,rewind|1.7416666746139526|0.25|4600|
|same query|1.7416666746139526|0.25|1313|

Each call executes actual time helper, dispatcher, packed selector/evaluator; original930output DWORDs agree with independent separate-f32 traversal at independently computed time. Exact loop boundary1now returns first-frame output; −1reaches endpoint output. This does not contradict115's stop-time sample:115query was **seconds**,116query is **normalized**.

Artifact counts: **24helper +8dense +5mixed +10source =47sample calls**, **29126native sample instructions**, **48modff +5memcpy substitutions** (one mixed full time call uses modff twice). Initialization is counted separately. Capture sizes/function counts are not execution counts.

## 6. Pins / reproducibility

Recovery **40323651044 SUCCESS**, source **99dcfc08ccd3feeac8e01997277ec7cd9f3d12e3**, raw commit**7a2a64fde**. Original cache fail-on-miss; no APK mutation/replacement. XAPK SHA**f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e**; libunity SHA**d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7**.

| Tool/input | SHA256 |
|---|---|
|`reverse-engineering/raw/cliptime116/probe.json.gz` (22100B)|`1dfa2ca9ab5851d75e969d75428d4f96891464ddc7a6ba583103b87833539c31`|
|`datas/l3_ef6b75ef116_native_clip_time_dense.json.gz` (6108B)|`bcde214305db2c739d1d48bad8670c1fbfb15138dcd93ebfd0bf607e2beec966`|
|`tools/recovery/cliptime116.py`|`c04e3ae8aeb356944fb2489ceea52bf6984889ce4fb322d20c38bee922b66540`|
|`tools/verify/cliptime116.py`|`f2cd4298ed2ef13c181482f543efc118b884b580ac40465232fb60b41d93fb31`|
|`tools/verify/cliptime116_native.py`|`6bf64922d2fe349802115246d61cb9faf5aa347d35a21e8aa47ef6cf85846652`|
|`tests/test_cliptime116.py`|`7948a7b67d6cddde3120689295487571d94c4954e38dbe1138a74b3bcd16962e`|
|Reused115raw|`9b2b21a61fe9b459b4815ab5361576f036c873f36da9ecbce2a25ac618e1d364`|
|Inherited source raw gzip|`cac775a419758a7ef51e74a9ad1d7a6e1040faaf69d28fb84d9311d978aec082`|

Artifact pins these and reused115builder/113guard/114float helpers. New raw has5followed entries:3original FDE extents and2labelled bounded PLT windows;15direct caller sites and20field references. Those are capture counts, not executed-function coverage. ADRP discovery remains candidates until precise operand/dataflow inspection. No implicitly zero-filled original-code/data fallback.

```sh
python3 -m tools.verify.cliptime116 --check
python3 -m unittest tests.test_cliptime116 -v
python3 -m unittest discover -s tests -v
```

**40focused PASS /1.249s; deterministic artifact check PASS.** Initial focused test expectation incorrectly omitted`loop=False` in the quantized-endpoint case; corrected test and explicit helper case, regenerated artifact, final40PASS above. No native byte/source result changed to accommodate it. Tests cover original FDE/import/field pins, helper branches/sign-bit/rounding counterexamples, native dense extrapolation/row selection, aggregate initializer/order/constant payload, original source930DWORDs, missing import rejection, two native opcode counterfactuals, prefill and negative relative pointer. Full/CI receipts appended after completion, not inferred.

## 7. Still open / independent review

- Actual Animator context acquisition/direction/offset/loop bit/quantization, state/layer timing and transition scheduling are **not proved** by prepared context values.
- Clip weighting, quaternion interpolation/normalization, Animator blending, property/PPtr application, bootstrap/services, Unity readback/render remain open.115native arithmetic +116time/dense composition ≠ full playback.
- Nonempty dense/constant data here is synthetic; no assertion any original game clip uses it. Source1609dense branch is explicitly skipped, despite420declared frames.
- Host modff/memcpy +allocator service substitutions remain explicit; no Android-libm parity or device session evidence. Raw/source lineage and adapter assumptions remain testable, provisional.
- Request independent review of m_Start/Stop/Cycle offsets, context ABI boundary, negative-exact-integer loop result, sign-bit−0.0, FRINTA outside-stop result, dense fractional extrapolation, mixed ordering and counts/service tiers. **No selfACK/full#27closure.**

Coordination updated from spec6416110827:115bounded consumer ACK/CLOSED; #5replication and#6static remap bounded scopes ACKed; #4primary/other geometry work stays peer-owned. Runtime loader/probe instruction is explicitly assigned to a5a74747, not imported or attempted by this lane. Protected3paths (`datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, `datas/player_start_stats.json`) remain absent/unchanged at116baseline/current. No original APK/assets or file>5MB added, release changes, main push, merge, screenshots/redraw or render acceptance.

## Final verification receipt

- **Full local1491tests PASS /262.153s**; focused40PASS/1.249s. Actual compressed logs retained under `reverse-engineering/raw/l3-ef6b75ef116-verification/`, not only log hashes.
- **Verify40324149097 completed SUCCESS at exact scientific61f31ae26f23908ffa2b281e6dee6e1427c5fcb8**. REST run/jobs saved in`ci.json`/`ci-jobs.json`; local test counts come from logs, not inferred CI count.
- Deterministic byte-for-byte artifact check PASS; `git diff --check` PASS; protected3paths absent/unchanged, new file sizes<5MB. Local Python3.11.2/capstone5.0.3/unicorn2.1.4/Pillow12.0.0 pinned in`local.json`. Heavy local work sequential, no concurrent full/model builder memory thrash.
-116independent disposition pending;115externalACK6416110827 synchronized; no selfACK/full#27closure.

Official PR12 HANDOFF **6416337983** posted after push/remote confirmation/exact-head CI. Receipt `reverse-engineering/raw/l3-ef6b75ef116-verification/handoff.json`; independent disposition pending, no selfACK.
