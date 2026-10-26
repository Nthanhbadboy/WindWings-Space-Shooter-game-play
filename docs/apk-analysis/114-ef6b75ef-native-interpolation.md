# 114 — original native curve interpolation, coefficient producer and frame packing

**Provisional; provenance `arena/ef6b75ef`.** Branch `arena/ef6b75ef-windwings-space-shooter-game-p`. CLAIM **6415164476**, approved by external spec **6415328887**. Scientific code **33cdc61a912c006a6169583dfad444841033df7a**. This is a bounded native-core deliverable for **#27 / #15b**, **not full Animator interpolation closure**.

## Kết quả và tầng bằng chứng

Đã đi từ original `AnimationCurve.Evaluate` icall registration tới native evaluator, key search, coefficient/cache construction, unweighted Hermite-family arithmetic, weighted inverse-Bezier solver và native time/channel/coefficient record producer. Không chép cubic model có sẵn thành “Unity truth”. Một native grouping/packing loop còn chạy trực tiếp để ra **frame header8 + key20 bytes** từ các record24 bytes.

Ba tầng tách riêng:

1. **Zero-function-hook native cases:** evaluator/cache/search, ordinary and weighted linear/quadratic-X cases, infinity-tangent branches, internal wrap behavior, record producer and packing loop.
2. **Explicit external boundary:** managed API wrapper has one synthetic managed-handle bridge. General weighted cubic cases use named ELF imports bound to **host** math (`logf`, `exp`, `atan2f`, `cosf`); engine solver arithmetic still executes, but Android libm ULP parity is **not** proved.
3. **Adapters/models, not runtime consumers:** original serialized keyframes supplied to synthetic native layouts; original StreamedClip coefficients injected into a native cache to compare arithmetic. Neither proves native selection of this APK clip at runtime, ParticleSystem evaluation, Animator blending or Unity readback/render.

## 1. Pins / reproducibility

- XAPK SHA256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- Original `lib/arm64-v8a/libunity.so`: **17783496 bytes**, SHA256 `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.
- Raw `reverse-engineering/raw/interpolation114/probe.json.gz`: **136316 bytes**, SHA256 `43b0bd3f166c371a26db255cf34aed4d55a807d56370ea85b081629a59d09da1`.
- Final recovery **40318758468 SUCCESS**, source **fd49ac4e1**, preserved raw **fc425ee28**. REST receipt in `reverse-engineering/raw/l3-ef6b75ef114-verification/recovery.json`; tool SHA also embedded in raw and output.
- Builder `tools/verify/interpolation114.py`; executor `tools/verify/interpolation114_native.py`; guarded-memory helper reused from unchanged `tag23_113_native.py` and SHA-pinned as input.
- Artifact `datas/l3_ef6b75ef114_native_interpolation.json.gz`: **8722 bytes**, SHA256 `9e795a9f60418e696265f3a35b7166cd3a0b701895beb734eab88aa4dabfaae3`. Tool/input SHA pins include both original object chunks, original dump metadata and the shared stream decoder. JSON represents nonfinite diagnostic values as strings and preserves actual bits/hex; no nonstandard Infinity numeric literals.

```sh
python -m tools.verify.interpolation114 --check
python -m unittest discover -s tests -p test_interpolation114.py -v
python -m unittest discover -s tests
```

Raw contains original PT_LOAD mapping, selected code/data/literal spans, RELA1027 slots/addends, named ELF JUMP_SLOT imports, original EH frame table entries/FDE prefixes and caller contexts. Function discovery follows **103 entries:87 FDE extents +16 bounded fallback windows**. These are capture/discovery counts, **not103 executed functions**. Original EH header declares47413 table entries; only selected witnesses are retained, not the entire unwind section.

All direct B/BL sites targeting the four evaluator helpers plus the record producer were enumerated in original executable segments: **2283 sites /141 FDE-owned caller functions**. Caller names/semantic ownership are **not** inferred from address neighborhood or counts. Indirect calls are outside this direct-call enumeration.

## 2. Original API → arithmetic path

| Evidence | Original address / action |
|---|---|
| icall string | `UnityEngine.AnimationCurve::Evaluate` at `0x1294c9` |
| registration | `0x389544..0x389554`, name and callback `0x36e71c` passed to `0x579c40` |
| callback | `0x36e71c`, resolve managed handle; read native curve pointer from holder+`0x10` |
| native evaluator | call at `0x36e764` → **`0x952608`** with optional-cache pointer x1=0 |
| key search | **`0x9528f8`** |
| coefficient/cache builder | **`0x952a80`** |
| direct segment | **`0x951344`** |
| weighted segment | **`0x951468`** |
| weighted X inverse | **`0x951f60`** |

The registered native callback's object bridge is externally supplied in the fixture. It does not turn a real managed object into an observed Unity object. After that bridge, the wrapper's pointer reads, native call, curve arithmetic and return execute from captured bytes. Native metadata `Keyframe` layout from the pinned dump agrees with loads: time/value/in/out tangents at0/4/8/12, weighted flags16, in/out weights20/24; stride **28**. This is not an engine object-constructor execution claim.

Synthetic curve layout supplies cache fields at0..27, key-array pointer at+`0x38`, key count at+`0x48`, internal pre/post mode integers at+`0x58/+0x5c`. Heap, stack, optional cache, sorted keys and initial invalid-cache state are fixture inputs. Source code/data reads outside captured spans fail closed even if a containing page is mapped. No polynomial/search/cache helper is replaced by Python.

## 3. Unweighted cached arithmetic — order matters

For cache start `t0`, output from original instructions is:

`((a * dt + b) * dt + c) * dt + d`, with `dt = float32(time - t0)`.

The original code uses separate scalar **FMUL/FADD**, not fused multiply-add. Cache generator uses endpoint values and outgoing/incoming tangents to construct coefficients; in ordinary nonsmall intervals their algebra corresponds to:

- `a = (m0*h + m1*h - 2*(v1-v0)) / h^3`
- `b = (3*(v1-v0) - 2*m0*h - m1*h) / h^2`
- `c = m0`, `d = v0`.

These algebraic expressions explain the path; **native instruction order and float32 rounding**, not a float64 transcription, produce the saved results. The fixture's actual constructed coefficients for smooth keys(0,0),(1,1), zero tangents are **[-2,3,0,0]**. Evaluation at0.25 returns **0.15625**. Cold evaluation executes **173 native instructions**, a subsequent cached evaluation at0.5 executes **30** and does not call the generator. API wrapper over a hot cache executes53 native instructions plus the bridge sink.

Artifact has **15 synthetic unweighted samples** across smooth, linear and asymmetric endpoint/tangent families, with ideal Hermite comparisons. Comparisons do not replace native execution or establish arbitrary-input bit parity.

### Important counterexample: minimum duration

Original immediates at `0x952aa4/0x952aa8` construct **bits0x38d1b717 = 0.00009999999747378752**; coefficient builder takes FMAX with that duration. Native direct segment helper instead normalizes by its actual nonzero interval.

With input times0 and float32(0.00001), values0 and1, zero tangents, at float32(0.000005):

- **cached evaluator:** `0.007249999791383743`;
- **direct segment helper:** `0.5`.

Therefore “every curve path is the same ideal cubic interpolation” is false. Mutating the original minimum-duration immediate to float32(0.00000001) changes the cached result to0.5. Separate opcode and tangent-load counterfactuals also change executed results. No old probe/scheduler policy is silently upgraded.

### Infinity tangents / internal wrap storage

Five stored tangent pairs demonstrate positive infinity selects left value, negative infinity selects right value; positive-infinity test wins when mixed with negative. Cached and direct routes are both tested. Six wrap samples exercise raw **internal** modes0/1/2: observed reflection/repetition/clamping for the chosen linear fixture. Do **not** equate these internal integers with public WrapMode or serialized infinity enums without conversion/transfer proof. Empty/single-key fixtures and external cache are covered separately.

## 4. Weighted path and honest platform-math boundary

The weighted path checks left weighted flag bit1 and right flag bit0. Disabled weights use original float32(1/3). It solves normalized Bezier X for parameter u, then evaluates Bezier Y with tangent-scaled control points. This follows actual loads/operations, not a borrowed weighted-curve implementation.

Four families ×three times = **12 weighted samples**:

| Family | First sample at0.25 | Native instructions | Platform calls |
|---|---:|---:|---|
| default weights / linear X | 0.15625 | 223 | none |
| quadratic X, outWeight0 / inWeight float32(2/3) | 0.5 | 233 | none |
| cubic X, weights float32(0.1)/float32(0.7) | 0.4571700692176819 | 277 | host logf/exp bridge |
| three-real-root branch, weights0.25/0.25 | 0.18235601484775543 | 301 | host atan2f/logf/exp/cosf bridge |

The nontrivial quadratic case executes native FSQRT and gives0.5 where the unweighted smooth case gives0.15625. Zero-function-hook evidence is therefore not limited to a constant/linear interpolation toy.

General cubic solver calls original PLT stubs. Exact ELF symbol entries/names link slots to **atan2f/logf/exp/cosf**; fixture dynamic binding supplies host math at those external interfaces. Native PLT instructions and engine solver execute. With no bridge, required uncaptured external execution fails; no implicit math replacement occurs. This is **not original Android libm execution or Android ULP parity**. Independent host bisection/Bezier reference is comparison only: maximum absolute error across the12 stored samples is **3.239906622987121e-07**, not a universal bound.

## 5. Original coefficient records and native frame packing

Direct-caller recovery exposed another concrete path:

- Original parent **`0x6ad7e4`** calls **`0x6c4480`** at `0x6adbe4` and `0x6adc98`; the same parent calls packer `0x6c498c` at `0x6add58`.
- **`0x6c4480`** iterates native keyframes, creates an initial **-FLT_MAX** constant record, calls the original coefficient builder for internal intervals and emits a final constant record.
- **`0x6c4360`** performs real vector append/stores: **24-byte** `(float time, uint32 channel, float a,b,c,d)` record.

Canonical smooth fixture with channel7 produces **three records**, native producer **255 instructions**, no function hooks; coefficient row is[-2,3,0,0]. Capacity is preallocated; allocator/growth paths are not exercised. Native keyframe preparation/weighted baking before this producer is not claimed.

The original packer sorts/allocates before grouping records. We do **not** simulate that whole service chain and call it complete. Instead a **manual-entry packing-loop fixture** starts at **`0x6c4b8c`**, after sort/reserve, with sorted records and a prepared byte vector. It stops **before `0x6c4c40`**, before final sentinel/allocator/copy/destructor suffix. Original append-header helper `0x6c4d04` and append-key helper `0x6c4d48` execute, as do all field/group stores:

- header: float time + uint32 key count (**8 bytes**);
- key: uint32 channel + original coefficient vector (**20 bytes**).

Three single-key frames yield **84 bytes /204 native instructions**. Existing stream decoder reads those native-produced bytes as the three expected frames. Prefill0 and prefill0xA5 produce identical output, proving emitted bytes do not accidentally depend on a zero-filled buffer. Final sentinel generation is deliberately excluded: this fixture does **not** prove that final header's unassigned fields or full allocation/copy path.

This strengthens the producer/format link beyond merely recognizing a cubic. It still does **not** identify/execute the native consumer of this APK's packed clip or full Animator property scheduling. Original parent semantic class ownership is not guessed from its address.

## 6. Original data fixtures and arithmetic adapter

### Serialized ordinary keyframes

Source `data.unity3d/level2:4783`, ParticleSystem `.SizeModule.curve.maxCurve`, row134 in `reverse-engineering/raw/l3-visual-surface/objects-0007.jsonl.gz`; original object SHA256 **`13d67ce46d885cb3e11b041010db748a19692ab3226710889a82adb012ba4e04`**. Three original keyframes, slopes, weighted flags and weights are preserved. Keys have weightedMode0 even where an unused weight differs from1/3.

Five explicit times (original key times +interval midpoints) run through native evaluator; original keys also run through the native record producer and packing loop. Maximum absolute difference against ideal Hermite at the five times is **1.8882332808445312e-08**. This is a source-data fixture supplied to an AnimationCurve layout — **not proof of ParticleSystem consumer, module simulation, rendered size or geometry**. Raw serialized infinity integers are retained but not assumed equivalent to internal wrap fields.

### Original StreamedClip coefficients: arithmetic-only adapter

Clip `resources.assets:1609`, original object SHA256 **`69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae`**, row140 in `objects-0015.jsonl.gz`. The adapter decodes source words with continuous+discrete curve counts, selects continuous **channel0**, key time0, next same-channel key **0.36666667461395264**, then injects its original four coefficients into the known cache layout. Three times compare native float32 Horner with the old float64 polynomial arithmetic.

This tests arithmetic under an **explicitly supplied layout bridge**, not native StreamedClip indexing/memory layout/caller selection. In particular it does not authorize promoting `probe_channels` streamed/dense policies or Animator blending to engine truth. Initial adapter development passed only continuous count and correctly failed on discrete indices; final decoder uses both counts and selects a continuous channel. No pointer/int channel is interpolated here.

## 7. Verification / current closure

- Focused **40 PASS /1.464s**; deterministic builder/`--check` PASS. **Full1411 PASS /311.581s; Verify40319106339 SUCCESS at exact scientific head33cdc61a912c006a6169583dfad444841033df7a.** REST run/jobs, actual compressed focused/full logs and local/check receipts retained under114-verification. No CI test count inferred from green status.
- Counterfactual opcode, tangent load and duration immediate; missing literal/code fail-closed; two object addresses; managed bridge isolation; no-host-math failure; explicit host-math labels; packing prefill independence and channel-index mutation are tested.
- No old sampler/model files changed. Native source and datas files below5MB; protected3paths unchanged (absent both at baseline `c4ac58cde` and current checkout). No APK modification, render, main push, merge or self-ACK.
- Remaining **#27 full closure**: resolve original parent/packed-clip consumer ownership and actual native StreamedClip time/channel selection; dense clip sampling; property/layer weighting and Animator runtime integration. These are **not disproved or declared impossible** by this partial native-core proof. Additional native source tracing remains possible; device/runtime readback is a separate tier.

## 8. Coordination and góp ý updated

External spec **6415183905** ACKs113 and closes **only bounded #2 native mapping gate**; **6415328887** confirms board update and approves114 claim. No self-ACK is used. Unity class bootstrap/services/runtime setter/readback/render remain open. Historical105 UNPROVED is retained as historical, not current bounded mapping status.

Our góp ý6415164476 was accepted/forwarded by spec: separate owned-source invariants/tests from inherited harness diagnostics; pin support view, original baseline and fail/skip groups, no needle edits to fabricate green. AI3-new8141386a has #5 replication; primary a5 #5 bounded model ACKed. AI2 #28 fallback handoff6415301081 is static-only, not runtime, and AI2 now owns **#25 claim6415333947**. No takeover/import of peer tools or geometry work.

Official PR12 HANDOFF **6415566619** posted after push and exact-head CI success. Receipt `reverse-engineering/raw/l3-ef6b75ef114-verification/handoff.json`; peer disposition pending. No self-ACK/full #27 closure.
