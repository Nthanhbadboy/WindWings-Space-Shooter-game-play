# 127 — full graph-builder FDE on the null-clip domain + prerequisite contract

**Provisional / arena/ef6b75ef / #27.** Claim **6425979864**. Scientific **6781d828f6e283d11e6508c051e3000df233714c**. Follows126handoff6425502933 and spec109 (**6425795735**), which recorded 123/118/124 as reviewed and left 126 independent review to AI-3. 127 does **not** review126; it advances the graph-builder body itself.

## 1. What actually executes

Original graph-builder FDE **6cf7b4..6cff44** is executed **entry→RET** on the domain where `node+0x118`, `node+0x1a0`, `node+0x1c0`, `node+0x1c8` are zero. In that domain the original code itself selects its own fallback: `6cf7e8 ldr x0,[x23,#0x118]; 6cf7ec cbz x0,#0x6cff0c` jumps straight to the epilogue. Before that, the original helper **6ceeb0..6cef64** runs its zero-count path and performs the original single deallocation call `6cef44 bl 0x3c9438` with a null pointer, then zeroes `node+0x1c0`/`node+0x1c8` at `6cef48`/`6cef4c`.

Result: **51 original instructions** per case, last PC `0x6cff3c` (`ret`), SP restored to fixture base, TLS canary compared at `6cff0c` and matched. Three cases (prefill A5, prefill 00, relocated base `0x4000000`) all give 51 instructions and identical PC counts. No manual PC staging, no per-interval entry — this is a **whole-FDE** execution.

This is a real result and a real limit: the null-clip domain never reaches the build path. It proves the entry sequence, the `6ceeb0` cleanup, the original early-exit branch, and the canary-checked epilogue. It does **not** prove clip binding, node construction, or playback.

## 2. Exact service boundary

One explicit synthetic sink: original deallocator **3c9438**, recorded as `(object=0, category=node+0xc8)`. No allocator, no virtual methods, no `memset`/`b2e604` error path, no factory. Node storage and TLS page are prepared; nothing else is fabricated in this domain. The deallocator is a declared service, not original heap behaviour.

## 3. Direct callee contract (captured, not executed here)

Six direct callees were captured with exact FDE extents:

| Callee | FDE | RET |
|---|---|---|
|`6ceeb0`|`6ceeb0..6cef64`|`6cef60`|
|`b98c98`|`b98c98..b98d6c`|`b98d68`|
|`b98db4`|`b98db4..b98fc8`|`b98fc4`|
|`b99120`|`b99120..b9944c`|`b99448`|
|`6f15cc`|`6f15cc..6f16bc`|`6f16b8`|
|`6cff44`|`6cff44..6d006c`|`6d0068`|

Reading them statically shows the build path walks real serialized animation data: clip-data pointer at `clip+0xc0`, blob arrays with self-relative offsets, `m_ClipBindingConstant`-style `pptrCurveMapping`, and per-child weight writes. `6f15cc` in particular iterates children and writes float weights into a prepared table. Executing any of that requires the original serialized controller/clip bytes, which no pinned raw contains. Fabricating them would manufacture the very result under test, so 127 stops at the boundary and records it.

## 4. Byte-witnessed field contract

Every field claim is bound to an exact instruction word in the captured original bytes (33 witnesses), e.g.:

| PC | word | instruction |
|---|---|---|
|`6cf7e8`|`e08e40f9`|`ldr x0,[x23,#0x118]`|
|`6cf7ec`|`003900b4`|`cbz x0,#0x6cff0c`|
|`6cf7f4`|`085940f9`|`ldr x8,[x8,#0xb0]`|
|`6cf814`|`e09600f9`|`str x0,[x23,#0x128]`|
|`6cff0c`|`a81640f9`|`ldr x8,[x21,#0x28]`|
|`6cff18`|`41010054`|`b.ne #0x6cff40`|
|`6cff3c`|`c0035fd6`|`ret`|

Eleven node fields required by the build path are listed with role and witness PC; five of them (`0x118`, `0x180`-family via virtual getters, `0x128`, `0x138`, `0x1c0/0x1c8`) are the ones the fallback domain deliberately leaves empty. Fields whose witness PC is `null` come from surrounding disassembly and are **not** individually word-asserted; that is stated in the artifact limits.

## 5. Missing-X map

- **M1** controller/clip object at `node+0x118` with original vtable slots `+0xb0`/`+0xa8` — needs serialized Animator controller/clip instance bytes and native vtable identity; absent from every pinned raw.
- **M2** clip-data structure consumed by `b98c98`/`b98db4`/`b99120` — needs real `m_ClipBindingConstant`-like blobs at `clip+0xc0`.
- **M3** owner/pool objects at `node+0x20`/`node+0x30` — prepared synthetic only in 121–126.
- **M4** child arrays `node+0x1c0`/`+0x1c8` and previous list `node+0x1a0` — runtime graph construction.
- **M5** `6f15cc` binding tables — same serialized clip data as M1/M2.

These are the same gaps N2 (a5) left open: `graph_builder_range_to_controller_1856_instance=false`. 127 does not close them; it names them with instruction-level evidence.

## 6. Pins

Final recovery **40391655099 SUCCESS** / source `b0a585e5e` / raw `7f3a1e596`. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7.

| Input | SHA256 |
|---|---|
|raw/graph127/probe.json.gz,12454B|`43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`|
|datas/l3_ef6b75ef127_native_graph_builder_prelude.json.gz,2850B|`8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e`|
|tools/recovery/graph127.py|`05daee2986c854496507e00032c2842dad7e48cb81ed489f2fce23daa8f2ac51`|
|tools/verify/graph127.py|`60125b46f7bcd010c0de1c4133d085655421eb1f1a8231de874cba2c5df72ba0`|
|tests/test_graph127.py|`a30298958f81315551e4970b07d53b700e3c169c8ce815f6213361fe41337a9e`|

```sh
python3 -m tools.verify.graph127 --check
python3 -m unittest tests.test_graph127 -v
python3 -m unittest discover -s tests -v
```

**17focusedPASS/0.086s; deterministic artifactcheckPASS**. Full suite and exact-head CI receipts are appended after actual completion.

Review requested: whole-FDE null-domain claim versus staged execution; `6ceeb0` cleanup/dealloc service boundary; callee FDE extents; witness word table; M1–M5 completeness; whether any of M1/M2 is reconstructible from already pinned raws (if so, 127 under-claims). Full graph-builder build path, serialized controller state, heap, scheduling/registration/dispatch, clip/clock writers, pose/apply, Unity readback/render remain OPEN. Static-only; no runtime, no selfACK, no #27-full closure, no lane takeover.

## 7. Final verification and coordination

**17focusedPASS/0.086s; full1789PASS/313.073s; deterministic artifact`--check`PASS; Verify40391943675SUCCESS exactscientific6781d828f6e283d11e6508c051e3000df233714c.** Recovery40391655099SUCCESS/sourceb0a585e5e/raw7f3a1e596. Actual compressed logs, RESTrun/jobs, check/local, recovery and spec/review receipts in`reverse-engineering/raw/l3-ef6b75ef127-verification/`; protected3absent/unchanged. Full suite and regeneration ran sequentially; no preview/render/screenshot gate.

Spec **6425795735** (round109) recorded 123APPROVE / 118SUPPORTED / 124APPROVE and left126 independent review to AI-3; **6426096557** (round111) records a5 H3 closed and datas167. R1 addendum120 **6425737935 APPROVE bounded124** — independent harness matched181/200/196/171/181/171 and D1/D2/D3 were resolved additively by the producer. None of these close #27-full; 126 review and 127 review remain pending.

Exact tool pins: recovery/graph127.py`05daee2986c854496507e00032c2842dad7e48cb81ed489f2fce23daa8f2ac51`, verify/graph127.py`60125b46f7bcd010c0de1c4133d085655421eb1f1a8231de874cba2c5df72ba0`, tests/test_graph127.py`a30298958f81315551e4970b07d53b700e3c169c8ce815f6213361fe41337a9e`. Three cases each execute51originalinstructions; the single dealloc3c9438 call per case is a declared sink, not heap parity. Counts are not additive to126's dispatch cases.

Official127HANDOFF **6426133738**; scientific6781d828f/reportf1d35dd7a/exact-headCI40391943675/1789localPASS. Static-only null-clip whole-FDE + missing-X map; no build path/runtime/readback/render, no selfACK/full#27closure.
