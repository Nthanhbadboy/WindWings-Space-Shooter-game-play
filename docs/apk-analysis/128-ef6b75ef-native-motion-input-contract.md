# 128 — motion-set contract and the M2 serialized-vs-runtime split

**Provisional / arena/ef6b75ef / #27.** Claim **6426286596**. Follows official 127 handoff **6426133738**. This cycle answers the open review question in report 127 — *is any of M1/M2 reconstructible from already pinned raws?* — and it corrects one over-broad sentence in 127. It executes **no** FDE: the three builders consume a runtime object that no pinned artifact contains, so running them would require fabricating the object under test.

## 1. What this layer does and does not do

- **No new libunity bytes.** Every instruction word below comes from the pinned 127 recovery **40391655099 / source `b0a585e5e`** (`raw/graph127/probe.json.gz`, SHA `43adb19f…`).
- **No execution.** 127's null-clip whole-FDE result stands unchanged; 128 adds no PC hits.
- **New static content.** Full byte-witnessed contract for the three motion/binding builders `b98c98` / `b98db4` / `b99120` and the delivery tail `6cff44`: 4 FDE extents, **61 witnessed words**, 9 allocation sites, 6-word motion header, 7 child-record fields, 3 secondary-record fields, 4 derived objects, 1 delivery-target contract.
- **New data audit.** Exact, countable serialized content for controller **1856** (`Body 1`, `Boss-37004`): 8 clips, **402** generic bindings, **0** pptr mappings, **142** streamed frames, **177** constant values, **654** channels with exact binding coverage.

## 2. Builder contract from original bytes

| FDE | extent | RET | instructions | direct calls |
|---|---|---|---:|---|
|`b98c98`|`b98c98..b98d6c`|`b98d68`|53|`109acc0` (stack check)|
|`b98db4`|`b98db4..b98fc8`|`b98fc4`|133|`b98fc8`, `109ace0`, `6e42b4`, `6e2388`, `6ef940`|
|`b99120`|`b99120..b9944c`|`b99448`|203|`109ace0`×5, `6ef3e8`, `6dee90`, `6efc30`, `6efaf4`|
|`6cff44`|`6cff44..6d006c`|`6d0068`|74|`6d6d08`, `6d6d50`|

The motion set is read-only in all four: no store instruction targets the register that holds it (`x21` in the three builders, `x22` in the tail; store-base sets are recorded in the artifact). Only derived objects and stack slots are written.

**Motion header (6 fields).** `+0x00` u32 child count (also the delivery-loop bound), `+0x08` array of slot-relative int64 pointers to child records, `+0x10` u32 secondary count, `+0x18` array of slot-relative pointers to secondary records, `+0x20`/`+0x28` slot-relative merge pointers consumed by `6e42b4`/`6e2388`. Witnesses include `b98e08`, `b98e1c`, `6cf9b8`, `b98e98`, `b98ec8`.

**Child record (7 fields).** `+0x00` motion index (compared with the loop index at `6cfa9c`), `+0x04` slot index (written into the per-secondary slot array at `6cfcec`), `+0x18` count passed to graph populator `6d2950` (`6cfc28`), `+0x24` flag compared with 1 for `6d6d50` (`6d002c`), `+0x28` f32 weight copied into the N0-float array (`b98f1c`), `+0x30`/`+0x34` words copied into the 0x80 child object (`6ef9a8`/`6ef9b4`).

**Secondary record (3 fields).** `+0x00` sub-count, `+0x08` slot-relative pointer array (per-sub record built by `6efaf4`), `+0x34` curve count that bounds the per-child slot array and the running max.

**Derived objects.** `b98c98` → 0x20 header (`+0x00` = 1.0f, `+0x18` = count×0x18 zero-filled binding records, `b98cd8`/`b98d3c`); `b98db4` → 0x30 child/weight table; `b99120` → 0x28 container with two pointer arrays, a byte array and a max-sized float array; `6ef940` → 0x80 per-child object. Note that `b98c98` **zero-fills** the 24-byte records and copies no serialized binding value at this stage.

**Delivery tail.** `6cff44` loops over `motion+0x00`, dereferences `[[node+0x30]+0x20]` to the first qword (the delivery target, `6cff88`/`6cff8c`/`6cff90`), calls its virtual slot `+0x18` with the child index and weight (`6cfff0`/`6cfffc`), then `6d6d08` and `6d6d50` (`6d000c`/`6d0038`). `node+0x30` is a prepared synthetic chunk in 122–127; the real target identity is open.

## 3. Correction to 127's M2 wording

127 wrote that the build path needs "real serialized controller/clip bytes, which no pinned raw contains" and listed M2 as absent. That is exact for the **runtime object** and too broad for **serialized content**. The pinned raw does contain the serialized side:

- **M2a — serialized content: AVAILABLE.** `datas/l3-scene-chains/motion-000.json.gz` (SHA `b2036fe6…`) holds all 8 clips of controller 1856 with decoded bindings and stream arrays; `raw/typetrees/animator-controller-graphs.jsonl.gz` (SHA `48e26d21…`) holds the controller typetree. Counts are exact and asserted.
- **M2b — runtime motion-set object: MISSING.** The 6-word header plus N0 child records and N1 secondary records are a native heap object; no pinned raw captures a native instance, and no captured FDE constructs one.
- **M2c — producer: MISSING.** The only producer in the captured graph is the owner virtual `+0xa8` at `6cf810` on `node+0x118`; the owner class/vtable is still unidentified (M1). No BL among the 39 followed entries returns the motion set.

So the execution boundary from 127 does not move: `b98c98`, `b98db4`, `b99120`, `6cff44`, `6f15cc` and the merge/child builders remain **not run** (`not_run` in the artifact names the reason for each).

## 4. Serialized audit of controller 1856

Controller typetree: `m_ControllerSize` **4110**, 1 layer, 8 state constants, 8 blend-tree constants, 8 blend nodes, **0** child indices, clip IDs `[7,1,2,3,4,5,6,0]`, 6 parameters, no `m_ClipBindingConstant` in the controller itself.

| clip | path | bindings | pptr | streamed frames | constant values | channels | coverage |
|---|---:|---:|---:|---:|---:|---:|---|
|Setup|1391|8|0|1|24|24|exact|
|Xuathien|1392|8|0|8|0|24|exact|
|attack1|1393|13|0|24|12|35|exact|
|attack2|1394|17|0|26|12|49|exact|
|idlexuctu|1395|88|0|20|45|128|exact|
|idlexuctu2|1396|93|0|16|45|143|exact|
|xuctuthulai|1397|89|0|20|18|127|exact|
|xuctuxuathien|1398|86|0|27|21|124|exact|
|**total**|**8**|**402**|**0**|**142**|**177**|**654**|**8/8**|

Two consequences: (a) for this controller the `pptrCurveMapping` part of 127's M2 vocabulary is **empty** — the content is generic bindings plus streamed/constant channels; (b) every clip's `binding_channel_count` equals its `channel_count`, so the serialized side is internally complete even though the runtime side is absent.

**Negative checks (the two candidates named in the 127 checkpoint).** `controller-graphs.json.gz` (`72b9cfad…`, 52 controllers) carries `layers_raw` with only the `m_Binding` hash `756556552`; no `ClipBinding`/`pptrCurve` strings exist anywhere in its decompressed text. `enemy-clip-links.json.gz` (`fe001faf…`, 154 animators) carries per-clip membership and muscle byte counts (**72300** for these 8 clips) with `curves_decoded=false` on all 8. Neither carries binding blobs.

## 5. Pins

Original XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; libunity SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`. Recovery 40391655099 SUCCESS / source `b0a585e5e`.

| Input | SHA256 | bytes |
|---|---|---:|
|`reverse-engineering/raw/graph127/probe.json.gz`|`43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`|12454|
|`datas/l3-scene-chains/motion-000.json.gz`|`b2036fe60a7bfef7fc1e8324f4c33ccf4d597ba991c5e7422bda16e2c666fa7c`|3848652|
|`reverse-engineering/raw/typetrees/animator-controller-graphs.jsonl.gz`|`48e26d213b47e8f8e5d5bf9073534971b638a01c6a37679ba17936919ff4d309`|58287|
|`reverse-engineering/raw/animation-audit/controller-graphs.json.gz`|`72b9cfad8bb7f9e2f0e390ecc6ea680ed2ad6198dd8ad3c83d152f7b76860ae7`|34709|
|`reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz`|`fe001faf73dc727974156cdcc37d60b1a59463c00b867f7ded35b0ed2a2576b4`|35496|
|`datas/l3_ef6b75ef128_native_motion_input_contract.json.gz`|`2b1b5e8277469e3105ac1ae75af3b5c97a8e82bc4a8f85d364be3fe6551849d3`|6119|
|`tools/verify/motion128.py`|`16b4915a432ef9436a1e704b8fb294e2f6fd9bc57cde67a7174cea53d1fd1b16`|21003|
|`tests/test_motion128.py`|`ecdd1a2d562e1f10b00715ef0d5e662294a746fd8bc0e5f8b3d1d014167413df`|5598|

```sh
python3 -m tools.verify.motion128 --check
python3 -m unittest tests.test_motion128 -v
python3 -m unittest discover -s tests -v
```

**22 focused PASS / 0.979 s; full 1811 PASS / 312.217 s; deterministic `--check` PASS.** Exact-head CI receipts are appended after the actual run.

Review requested: the 61-word witness table and FDE extents; the read-only claim for the motion base; the 6/7/3-field header/child/secondary contract; the M2a/M2b/M2c split; the correction to 127's wording; whether the serialized audit numbers are sufficient to call M2a "available" without implying a runtime layout; and whether any pinned raw contains a producer that 128 missed (if so, 128 under-claims). Full graph-builder build path, owner class/vtable (M1), original heap, scheduling/registration/dispatch, clip/clock writers, pose/apply, Unity readback/render and #27-full remain OPEN. Static-only per 6418032974 / 6418326986; no runtime, no self-ACK, no lane takeover.
