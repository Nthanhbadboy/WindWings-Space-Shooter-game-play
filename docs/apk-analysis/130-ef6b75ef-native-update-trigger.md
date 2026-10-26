# 130 — native update/trigger driver of the animator-side object (ef6b75ef, static)

Status: **provisional**. This cycle reads original `libunity.so` bytes only. No instruction was
executed, no class name is claimed, and no runtime behaviour is asserted.

## 0. Pins (tool + input)

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe A | `reverse-engineering/raw/owner130/probe.json.gz`, 27223 B, `d3929b2e8d3302c47488eb69314e379c522355efb9133590b31c73e69b5c3466` |
| probe B | `reverse-engineering/raw/owner130b/probe.json.gz`, 4996 B, `7d5aacc5cae91f97e18a108c54d994e012cf662d4220967d2d1fee600c8adacb` |
| recovery tools | `tools/recovery/owner130.py`, `tools/recovery/owner130b.py` (SHA-256 recorded inside the artifact) |
| verifier | `tools/verify/owner130.py` |
| artifact | `datas/l3_ef6b75ef130_native_update_trigger.json.gz`, 7590 B, `6afffcec6902b22285f1b46c84fa3f2a0221967bd7ef2b3b45471b88299c8057` |

Both probes were produced in CI from the pinned XAPK cache (`fail-on-miss`, key
`windwings-xapk-1.3.118-f5d3…c7e`); the recovery workflows are
`.github/workflows/recover-owner130.yml` and `recover-owner130b.yml`.

## 1. Method

Probe A seeds 22 entries (the update/trigger functions and their participating slots), follows
direct `BL`/`B` references two caller levels with a 40-function and 0x1000-byte window cap, and
resolves each function extent from the original `.eh_frame` FDE table (falling back to a bounded
window when no FDE matches). Probe B runs the same machinery upward from nine seeds with a
32-function cap and also records `ADRP+ADD` references to six global containers. Both probes
record the raw instruction bytes; every claim in this report is a `pc → 4-byte instruction`
pair that the verifier re-checks against those bytes.

Countable scope of the two probes:

| quantity | value |
| --- | --- |
| followed functions (A / B) | 40 / 11 |
| distinct windows after merge | 40 |
| direct call sites (deduplicated, A∪B) | 70 (`bl` 55, `b` 15) |
| indirect call sites (`blr`) inside captured windows | 5 |
| vtable rows recovered for `10b0c80` | 5 of 35 slots |
| animator-object field offsets anchored in facts | 27 |
| non-object offsets recorded separately | 2 |
| driver-chain stages | 19 |
| byte-verified facts | 177 |

## 2. Who drives the rebuild (answer)

The object whose header is installed by `6b9acc` (slot write of `10b0c80` at `6b9ad8`) owns a
35-slot vtable. Five slots are answered by the recovered functions:

| slot | target | direct code refs | role (structural) |
| --- | --- | --- | --- |
| 2 | `6b1914` | 0 | rebuild-all: `6b1a00` reset, `6b1b1c` teardown, `6b1bb0`, descriptor copy via `6b9ed4` |
| 3 | `6b1c5c` | 0 | message entry: `3f9cf4(x0)`, if `w1==0x10` tail `6b1c98(x0,0)` |
| 10 | `3e079c` | 0 | accessor: `[x0+0x30]→+0x60`, else table at `[0x10e19c8]` |
| 31 | `6b947c` | 0 | update entry: resolve `+0x19c`, `6b7d58`/`6b81c4`, `6b1f04`, `6b22c8`, `571e64` |
| 33 | `6b6ab8` | 0 | parameter entry: resolve `+0x618`, tail `572c60` with `w1=0`/`3` |

All five have **zero direct call sites** in the two-level closure, i.e. they are reached through
the vtable, not through a `BL`. The caller of the vtable dispatch itself is therefore still not
recovered by static reference scanning and is explicitly out of this cycle's result.

The actual rebuild sequence is `6b2258`:

1. `ldrb w8,[x0,#0x194]` / `tbnz w8,#4` — bit 4 suppresses the whole body (`6b225c`, `6b2260`).
2. `ldr x0,[x0,#0x30]`; `3df584`; `tbz w0,#0` — second gate (`6b2268`, `6b2270`).
3. `6b1a00` — full field reset (writes `+0xb0=1`, zeroes `+0x108`, `+0x118`, `+0x150`,
   `+0x158`, and finally `+0x188=0`).
4. `6b7158`, then `ldr x8,[x19,#0x1b8]` / `cbz`.
5. `6b7d58` (build output), `6b81c4` (build controller), `6b6dec` (evaluate/collect),
   `6b6fdc` (apply), and tail `6b7c58(x0=x19, x1=x19+0x208)`.

The flush entry `6b1c98` takes `w1` as a mode bit: bit 0 set runs `6b2050` then `6b1b1c`, then
the `+0x194` bit-4 gate, `6b2258`, `6b1f04`, and tail `6b22c8`. The message entry `6b1c5c`
reaches exactly this flush with `w1=0`.

`6b4bfc` is the query form used by the playable-side callers (`6b3e78`, `6b4820`, `6b72e4`):
if `[+0x188]==0` it calls `6b2258`; then, when `w[+0x19c]!=0`, `[+0x608]!=0` and
`[[+0x608]+0x130]!=0`, it stores `s0` from `[+0x488]` through that pointer; it returns
`[+0x188]`.

`6b27dc` is the batch entry: it materialises the global container `0x10ecb08` via `3d9648`,
then per element sets bit 6 of `[+0x194]` (`orr #0x40`), calls `6b1c98(el, 0)`, and clears the
bit (`and #0xffffffbf`). Bit 6 is therefore a transient "inside batch" marker for the same
byte that carries the bit-4 suppression flag.

## 3. Field map (node-anchored only)

27 offsets have at least one bracket access on `x0/x19/x20/x23` that the annotated fact anchors
to the animator object. Highest-count rows:

| offset | loads | stores | notable anchors |
| --- | --- | --- | --- |
| `+0x608` | 5 | 0 | controller instance; `+0x130` used as float sink, `+0x128`/`+0x138` as instance ranges |
| `+0x188` | 3 | 3 | rebuild gate / initialized byte (`6b4bfc`, `6b6d60`, `6b6dec`) |
| `+0x19c` | 6 | 0 | controller id resolved through `[0x10e18b0]`/`38cbb4`/`3d8614` |
| `+0x194` | 3 | 0 | flags byte (bit 4 suppression, bit 6 batch marker — the writes live in the batch body) |
| `+0x178`, `+0x168` | 2 / 1 | 0 | entry-array count and base (`0x28` stride) |
| `+0x4a8`, `+0x498` | 2 / 2 | 0 | `0x10`-stride driver array walked by `6b6fdc` and `6b6cc4` |

Accesses whose base is a child object rather than the animator are kept out of this table and
appear as facts with an explicit different subject (`element+0x194` ×3, `entry_obj+0x20` ×1).

## 4. What did NOT run, and what is not claimed

- No original instruction was executed in this cycle; the artifact is a byte-verification of
  addresses, not an execution trace.
- The five `blr` sites (`6b19cc`, `6b1b80`, `6b6e94`, `6b6f10`, `6b7048`) were not resolved:
  their targets come from object vtables and remain unknown.
- The contents of the global registry `[0x10e18b0]`, the object behind the `+0x618` handle, and
  every class name remain unrecovered.
- The caller of the `10b0c80` vtable dispatch is not in the closure; no scheduler, job or frame
  loop is claimed.
- `6f15cc`, `6d81b0`, `6b3c84`, `6bf2a0`, `6bf108`, `6bf1cc`, `6bf35c`, `6bf908`, `571e64`,
  `572c60`, `6b3e30`, `6b2a0c`, `6da998`, `6b2bdc`, `6b2ce8` appear only as call targets; their
  bodies are not part of this cycle except where cited above.
- The animator-side rebuild is **not** the full Animator: clip evaluation, blend/pose, job
  scheduling and rendering remain outside this lane.

## 5. Reproduce

```
python3 tools/recovery/owner130.py  --xapk /tmp/apk/windwings.xapk   # writes raw/owner130
python3 tools/recovery/owner130b.py --xapk /tmp/apk/windwings.xapk   # writes raw/owner130b
python3 tools/verify/owner130.py    --write                           # writes the artifact
python3 tools/verify/owner130.py    --check                           # byte-identical or fails
python3 -m unittest tests.test_owner130 -v
```

The verifier refuses to build if either probe's SHA-256, the XAPK pin, the `libunity.so` pin or
any of the 177 facts disagrees with the pinned bytes.
