# 135 — the apply seed, the two backend writers and the channel sampler (ef6b75ef, static)

Status: **provisional**. Bytes only: no instruction of `libunity.so` was executed, no object was
fabricated, no sink was invoked, no symbol or class name is used. This cycle reads the layer that
sits between the refresh leaves of 134 and the setters that actually write a channel value.

## 0. Pins

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe | `reverse-engineering/raw/owner135/probe.json.gz`, 11743 B, `c11aedd5868e29ad9493b934ad0c57fb4ba7cda4dd0d0d3de4d79750854070dd` |
| recovery runs | 40507430140 (`53f6536dc`), evidence commit `52c664057` |
| upstream pins | cycle 129 `217f8893…`, cycle 133 `73542233…`, cycle 134 `74cf1843…` |
| tool pins | `tools/recovery/owner135.py` and `tools/verify/owner135.py`, both recorded inside the artifact |
| artifact | `datas/l3_ef6b75ef135_native_apply_seed.json.gz`, 10434 B, `5c6d7d85dceb25fc46b13a9d7d4d3f83f706b0979c9d7a76b4e25c3e3555b534` |

## 1. Method

Fifteen seeds are read from the pinned XAPK cache (fail-on-miss) — bodies that the earlier cycles
named but never read — plus nine followed callees in the same `0x6b0000`–`0x6c0000` cluster. The
verifier decodes all 24 bodies again from the stored hex, splits `BL`/`B` into calls, external tail
branches and intra-FDE branches, re-derives every indirect-call site from the `ldr` that feeds the
`blr`, and re-checks **297 annotated instruction facts** byte for byte.

Counts are all countable from the probe, not estimated:

| quantity | value |
| --- | --- |
| bodies / seeds / followed | 24 / 15 / 9 |
| captured bytes | 9952 (2488 instructions) |
| calls / of which `bl` | 177 / 89 |
| calls into the same cluster | 12 |
| indirect-call sites (deduplicated) / raw rows | 20 / 42 |
| field rows (raw `ldr`/`str` on x0/x19/x20) | 203 |
| annotated facts | 297 |
| bodies cut by the `0x800` cap | 3 |
| strings owned by these bodies | 0 |

| body | group | extent | window | calls | fields | dispatch | facts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `0x6b2ce8` | seed | 0x204 | 516 | 4 | 25 | 0 | 49 |
| `0x6b2eec` | seed | 0x84 | 132 | 2 | 3 | 2 | 11 |
| `0x6b6850` | seed | 0x100 | 256 | 5 | 13 | 1 | 17 |
| `0x6b2bdc` | seed | 0x10c | 268 | 10 | 8 | 0 | 18 |
| `0x6da998` | seed | 0x54 | 84 | 2 | 4 | 1 | 7 |
| `0x6b7cf8` | seed | 0x60 | 96 | 3 | 4 | 0 | 10 |
| `0x6c7060` | seed | 0x108c | 2048 | 39 | 70 | 1 | 13 |
| `0x6a99f0` | seed | 0x120 | 288 | 6 | 2 | 1 | 29 |
| `0x6a98c4` | seed | 0xe0 | 224 | 5 | 4 | 2 | 12 |
| `0x6a99a4` | seed | 0x2c | 44 | 0 | 2 | 0 | 6 |
| `0x6a9b90` | seed | 0x3c | 60 | 1 | 1 | 1 | 6 |
| `0x3dfa9c` | seed | 0x44 | 68 | 0 | 2 | 0 | 9 |
| `0x3d8614` | seed | 0x50 | 80 | 2 | 0 | 1 | 5 |
| `0x518b40` | seed | 0x44 | 68 | 2 | 4 | 0 | 5 |
| `0x6d788c` | seed | 0x40 | 64 | 1 | 3 | 0 | 8 |
| `0x6b6950` | callee | 0xa0 | 160 | 3 | 5 | 0 | 12 |
| `0x6b1538` | callee | 0x9c | 156 | 1 | 5 | 0 | 10 |
| `0x6bad24` | callee | 0xc | 12 | 1 | 0 | 0 | 3 |
| `0x6b784c` | callee | 0x344 | 836 | 27 | 20 | 0 | 17 |
| `0x6bd5c0` | callee | 0x8a4 | 2048 | 23 | 2 | 5 | 13 |
| `0x6be690` | callee | 0xa34 | 2048 | 30 | 22 | 4 | 10 |
| `0x6b7c14` | callee | 0x44 | 68 | 2 | 3 | 0 | 5 |
| `0x6bba14` | callee | 0xc | 12 | 1 | 0 | 0 | 3 |
| `0x6bc968` | callee | 0x13c | 316 | 7 | 1 | 1 | 19 |

## 2. `0x6b2ce8` — the apply context, and what `+0x610` finally means

134 recorded `[animator+0x610]` as "2 or increment" and left it undefined. This body defines it.

Call frame: `x0` = animator, `x1` = playable record, `x2` = source object, `x3` = context out,
`x4` = third argument forwarded to the tail. Two exits:

1. `[x2] == 0` → the context is written as an *invalid state*: first word `1`, the 16-byte zero
   stores cover `0x08`–`0x68`, the word at `0x68`, and the pointers at `0x90`, `0xa0`, `0xa8`, `0xb0`.
2. `[x2] != 0` and `context[0] == animator[+0x610]` → rebuild is skipped entirely.
3. Otherwise `animator[+0x610]` is stored into `context[0]` and the whole map is rebuilt.

So `context[0]` is a **version key borrowed from the live counter**, and `+0x610` is the change token
both refresh (134) and apply (135) agree on. The commit leaf mirrors the counter into `context[0x58]`
after a successful commit, which closes the loop.

Copy map (all reads are `[x2]`, `[x2+0x18]`, `[[x2]+0x48]`, `[[x2+0x18]+0x58]`):

| context | source |
| --- | --- |
| `+0x08`, `+0x10`, `+0x18`, `+0x58` | `[[source+0x48]+0]`, `[+8]`, `[+0x10]`, and the base itself |
| `+0x20` | `[playable]` |
| `+0x28 … +0x50` | six words of the vector at `[source+0x18]` |
| `+0x60`, `+0x68`, `+0x6c`, `+0x70` | `[[[source+0x18]+0x58]+8]` and its words at `0`, `0x18`, `0x1c` |
| `+0x74`, `+0x78`, `+0x7c` | words at `source+0x54`, `+0x58`, `+0x5c` |

Derived bytes/words:

* `+0x80 = ([src+0x54] & [src+0x58] & [src+0x5c]) != -1`
* `+0x81 = byte at [src+0x50]`
* `+0x82` = first nested table non-empty: `p = [[src+0x48][0]] + 0x28`, `q = [p] + p`,
  `r = [q+0x30]`, then `*(r + q + 0x30) != 0`
* `+0x84` = `-1`, or the word at `[[[src+0x48][0]]+0x50]` when the second nested table is empty
* `+0x88 = byte at [[playable+8]+0x11]`, after which `0x6d615c` binds `animator+0x40` as the context
  owner (`+0x90 = animator`, `+0x98 = animator+0x40`) and the tail branches into `0x6b6950`.

Note that the invalid path and the fresh path **both** reach the commit tail; only the rebuild differs.

## 3. `0x6b6950` — commit gate

Needs `context+0x08` and `context+0x20` to be set. If `context[0x58] == animator[+0x610]` it returns
without doing anything; otherwise it builds the descriptor `{0x10b0b30, 0x1e}` and calls `0x6d816c`
and `0x6d8118`, then stores the counter. This is the only place in the cycle where the two-word
descriptor constant appears, and it is a constant, not a pointer to a string table.

## 4. `0x6b2bdc` — the backend choice, and why the writers stay unread

`0x6b2bdc` copies a three-word descriptor from `x1` into `record+0x08 … +0x18`, resolves a controller
through `0x6b784c`, then selects on flags:

| condition | target |
| --- | --- |
| byte `+0x5e5` set | `0x6bd5c0` |
| byte `+0x5e5` clear | `0x6be690` |
| `+0x48f` (legacy) and `+0x1b0` | `0x6e2388` on `[[+0x208]+0x48][8]` |
| otherwise | `0x6b7c14` |

and finishes with `0x6da8e4(desc)` and a tail into `0x6e2388`. Result goes to `record[0]`, descriptor
at `record+0x20`.

`0x6b784c` (the controller resolve) is worth naming separately: handle at `[x+0x638]`, registry
`0x10e18b0` through `0x38cbb4`, fallback `0x3d8614`, interval lookup `0x3dfa9c([x+0x30], 0x10e8960)`,
secondary handle `[x+0x198]`, then a chain of `0x6acb84` accesses whose slot is read as a
**relative** pointer (`obj + [obj]`, and `obj + 0x20` + `[obj+0x20]`) with the self sentinel
`[obj] == -obj` meaning empty. The leaf call is `0x6a7198(rel_a, rel_b, interval_entry, byte[x+0x5e5])`,
and the chosen id is written back into `[x+0x638]`.

Both writers share an entry shape: `0x6a7a08` first, then three stack descriptors (kind word `1`,
`-1` sentinel, 16-byte constant fill) inserted through `0x6bc968`, then a walk over their own arrays.
They differ immediately: `0x6bd5c0` passes **fourth argument 1** to the insert and fills an index array
from `[x+0x38]` through `0x3ff69c`, while `0x6be690` passes **0** and runs the `0x6bde64` pre-pass when
bit 0 of its flag is set. The two writers therefore do not build the same table entry even though the
insert callee is the same. Their interiors are cut at the `0x800` cap (`0x8a4`, `0xa34`) and are
**not** read here.

## 5. The channel setters — first place a write is compared with the old value

`0x6a99f0` is a switch on `kind = [x0+8]`, kinds `5..11`, dispatched through a **jump table at
0x152614** (`ldrb` per-kind offsets, `br x10`). Five shapes are visible in the captured bytes:

* raw float: store `s0`, `fcmp` against the old `s1`
* boolean window: upper constant `0x14be6c`, lower `0x14b9c8`, `> upper` / `< lower`, then a byte store
  and a forwarded call to `0x3dfd98` on `[x1+0x18]`
* unknown kind: delegate through `[x1+0x10]` (`ldr x8,[x8,#0x10]` + `blr`)
* int with rounding: `fadd 0.5`, sign mask `-0x40800001`, `fcsel`, `fcvtzs`, word store
* plain int: the float bits stored as a word

`0x6a98c4` handles kind 9 only: zero input short-circuits to null, otherwise the registry lookup
`0x38cbb4` → `[[entry]+0x10]`, fallback `0x3d8614`, value via `0x5888bc`, compare against the old
`[x19]`, `cset ne` as the return value, and a global hook `[[0x10e18a8]]` invoked with `(0, old, new)`.

`0x6a99a4` handles kind `0x0b`: it stores the word and returns `old != new`, and returns 0 for every
other kind. `0x6a9b90` releases: it calls slot `+0x18` with argument `0x10` and, when the global byte
at `0x10e18c0` is set, tail-branches to `0x4aa754`.

Helpers read in this cycle: `0x3dfa9c` (interval table: count `+0x40`, base `+0x30`, stride `0x10`,
match `(entry_start - key_start) unsigned < key_width`, payload `[entry+8]`), `0x3d8614` (0 → null,
hook `0x111dba0`, negative rejected, fallback `0x5d83b8(id, -1)`), `0x518b40` (lazy `[x0+0x38]`,
`0x494b04`/`0x493a24`, second word `+0x40`), `0x6d788c` (indexed child: holder `+0x30`, count `+0x30`,
base `+0x20`, entry count `+0x18`, chain index `ldrsw [slot+0xc]`).

`0x6b6850` (evaluate companion) uses all of these in one loop: playable `+0x168`/count `+0x178`,
stride `0x28`, per-entry resolve `0x6b1538`, scratch `+0x5e8` (`+0x5f8` count, `+0x600` capacity,
growth thunk `0x6bad24`), each scratch entry's slot `+0x1a0` OR-ed into byte `+0x48e`, then
`0x49ffc8(entry+0x58)`.

`0x6b1538` is **not** a simple resolver: it is a chain walk. Key words `[x0+0x10]` and `[x0+0x18]`
are compared with `[node+0x20] & ~1` and `[global+8]`, the next node comes from `[node+0x28]`, and the
index into the next holder is read from `slot+0xc` while staying below the holder count at `+0x30`.

## 6. `0x6c7060` — bulk builder, prefix only

`0x6c7060` allocates `count*8` bytes from `[x+0x10]` on the stack (16-byte aligned) unless the byte
count exceeds `0x7cf`, in which case it takes the heap path at `0x6c748c`. It then calls
`0x6d9068(count, x1)`, sets record word `+0x1c = 4`, keeps a per-element accumulator byte at `+0x20`
(OR of a `0xb97454` bit test, with `0xb974b4` on the taken branch) and fills two parallel stack arrays
from the pointer array at `[x0]`. Only the first `0x150` bytes of this `0x108c` body are annotated;
the remainder is outside the `0x800` window and is not described.

## 7. Corrections this cycle makes

* `+0x610` is not a free-running counter with unknown meaning: it is the version key of the apply
  context, compared in `0x6b2ce8` and mirrored in `0x6b6950`.
* The invalid-state description "zero q0 to `+0x58`, xzr `+0x90`/`+0xa8`/`+0xa0`" was incomplete: the
  six 16-byte stores cover `0x08`–`0x68` and the word at `0x68` is zeroed separately.
* `context+0x84` is `-1` **or** the word at `[[[src+0x48][0]]+0x50]` when the second nested table is
  empty; it is not "the playable byte".
* `0x6b1538` was labelled a resolver; it is a tagged chain walk (see §5).
* The recovery tool labels `0x6bc968` as depth 1 although its parent `0x6bd5c0` is itself a followed
  callee. The artifact reports it under `follow_depth.level2` instead of hiding it.
* The two backend writers were previously only names. Their entry sequences now differ in the insert
  argument, but their bodies remain truncated and unexplained — this is a limit, not a result.

## 8. What did NOT run, and what is not claimed

* No instruction of `libunity.so` was executed; no object was fabricated; no sink was called.
* No class, type or symbol name is asserted anywhere. Field offsets are raw bracket accesses.
* The jump table at `0x152614` is described from the dispatch code; its target bytes are not decoded.
* `0x6bd5c0`, `0x6be690` and `0x6c7060` are truncated by the capture cap; their rows cover a prefix.
* `0x6c7060` is annotated only for its first `0x150` bytes.
* This is a selected branch of one chain, not a complete Animator: it covers apply/evaluate/backend
  selection and the channel setters, not skinning, not rendering, not any runtime readback.

## 9. Reproduce

```
PYTHONPATH=/home/user/.cache/deps115:. python3 tools/verify/owner135.py            # counts
PYTHONPATH=/home/user/.cache/deps115:. python3 tools/verify/owner135.py --check     # artifact bytes
PYTHONPATH=/home/user/.cache/deps115:. python3 -m unittest tests.test_owner135 -v   # 41 tests
```

## 10. Verification (final)

Filled by the verification receipts under `reverse-engineering/raw/l3-ef6b75ef135-verification/`.
