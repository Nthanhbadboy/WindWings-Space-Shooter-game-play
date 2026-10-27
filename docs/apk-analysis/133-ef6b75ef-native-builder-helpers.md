# 133 — the graph builder's own helper chain (ef6b75ef, static)

Status: **provisional**. Bytes only: no instruction from the original binary was executed, no symbol
table and no class name is used. This cycle opens the chain that 132 stopped at — the two cluster
helpers the builder calls (`6b8054`, `6b80e0`) plus the per-node producer `6cefdc` — and follows
exactly one level of their in-cluster callees.

## 0. Pins

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe | `reverse-engineering/raw/owner133/probe.json.gz`, 4793 B, `8bb964b16017f2637b3403dacb0deb36788a5b36600d58fc25bedd3d74a90ee6` |
| recovery run | 40463822530 (`9bf7a391f`, `tools/recovery/owner133.py`) |
| upstream pins | cycle 129 artifact `217f8893…`, cycle 132 artifact `5037ba3b…` |
| artifact | `datas/l3_ef6b75ef133_native_builder_helpers.json.gz`, 5441 B, `73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707` |

## 1. Method

Eleven seeds are recovered from the pinned XAPK cache (fail-on-miss): the three builder callees left
open by 132 (`6b8054`, `6b80e0`, `6cefdc`), the two destructor-shaped helpers (`6b753c`, `6b3e30`),
the collector (`6b7c58`), the setter (`6ce4b4`) and four handle/list helpers outside the cluster
(`0x575e80`, `0x5752b0`, `0x570520`, `0x576a64`). One follow level adds 11 in-cluster callees
(`0x6b14ac`, `0x6b1538`, `0x6b6d60`, `0x6b92c4`, `0x6b9638`, `0x6b97d0`, `0x6b9994`, `0x6b9f6c`,
`0x6bb9ac`, `0x6bba08`, `0x6bbae4`), 24 max, bodies capped at `0x800`.

The verifier never trusts the probe: it decodes all 22 bodies again from the stored hex, splits
`BL`/`B` into calls, external tail branches and intra-FDE branches (FDE extent decides), pins cluster
membership to `0x6b0000..0x6c0000`, re-derives every `ldr [vptr,#slot]; blr` site with its base
register, and re-checks **144 annotated instruction facts** byte for byte.

Totals: **22 bodies**, 2716 B of original code, **73 direct transfers** — 55 `bl` (30 outside the
cluster, 25 into it) and 18 `b` (13 intra-FDE branches, 3 external tails, 2 in-cluster tails) — plus
**27 in-cluster calls**, **1 indirect call site** (2 raw rows, see §5), **2 strings** and
**90 field rows**. Slot numbers are resolved against the cycle-129 pinned vtable membership.

| entry | extent | role | bl | cluster calls | field rows |
| --- | ---: | --- | ---: | ---: | ---: |
| `0x570520` | 44 | handle ctor for field +0x10 (singleton fallback) | 2 | 0 | 4 |
| `0x5752b0` | 132 | create 0xf8 object (ctor 571c48) and link at owner+0x378 | 2 | 0 | 3 |
| `0x575e80` | 12 | singleton getter (`[0x116cb40]`) | 0 | 0 | 0 |
| `0x576a64` | 48 | handle ctor for field +0x20 (creator 575f2c) | 1 | 0 | 4 |
| `0x6b14ac` | 140 | build 0x28-byte playable record | 3 | 0 | 10 |
| `0x6b1538` | 156 | two-level lookup (handle/version, then index) | 0 | 0 | 5 |
| `0x6b3e30` | 56 | release wrapper object (3c9438, line 0x306) | 1 | 0 | 3 |
| `0x6b6d60` | 140 | reset + rebuild driver side of the playable table | 5 | 4 | 5 |
| `0x6b753c` | 56 | release wrapper object (3c9438, line 0x306) | 1 | 0 | 3 |
| `0x6b7c58` | 160 | collect tag-0x16 values into +0x4e0 | 1 | 1 | 2 |
| `0x6b8054` | 140 | create output object (3c9298, 0xe0) and link at owner+0x78 | 2 | 0 | 2 |
| `0x6b80e0` | 228 | refresh: playable entry +0xa8 into +0x498, then max via 6d14d4 → +0x4b8 | 4 | 1 | 13 |
| `0x6b92c4` | 40 | full refresh composite (6b2050, 6b6d60, 6b6dec, tail 6b6fdc) | 3 | 4 | 0 |
| `0x6b9638` | 408 | unbind playable (guard bit4, compaction, refresh) | 10 | 3 | 9 |
| `0x6b97d0` | 452 | bind playable (guard bit4, dedupe, insert/append, refresh) | 14 | 9 | 3 |
| `0x6b9994` | 172 | insert 0x28-byte record at index (memmove 109ad20) | 2 | 1 | 9 |
| `0x6b9f6c` | 12 | growth thunk 0x28 / 8 → 3f1cb4 | 0 | 0 | 0 |
| `0x6bb9ac` | 92 | push int read at `[p+8]` onto a vector | 1 | 1 | 4 |
| `0x6bba08` | 12 | growth thunk 4 / 4 → 3f1e30 | 0 | 0 | 0 |
| `0x6bbae4` | 112 | push 0x28-byte record onto a vector | 1 | 1 | 8 |
| `0x6ce4b4` | 72 | set animator+0xd0: unbind old, store, bind new | 1 | 2 | 2 |
| `0x6cefdc` | 32 | run 6cf7b4 then tail-branch through node vtable +0xe0 | 1 | 0 | 1 |

## 2. The builder creates an output object and splices it into a list

`6b8054(type, controller)` is 140 B and has exactly two calls:

```
6b805c  adrp x3,#0x12d000 ; add x3,#0xa21       ; empty label 0x12da21, same as 127/129
6b806c  mov w0,#0xe0 ; mov w1,#0x5e ; mov w2,#8 ; mov w4,#0x56
6b807c  bl 3c9298                               ; original allocator(size, tag, align, label, line)
6b808c  bl 6ce464                               ; 129's output ctor (name, owner)
6b8090  add x9,x21,#0x78                        ; list anchor on the owner
```

The remaining 11 instructions are the same intrusive-list splice used elsewhere: if `[new+8]` is
null the node is cleared, then `head=[owner+0x78]`, `new[8]=head`, `new[0x10]=&owner+0x78`,
`head->prev = &new+8`, `tail->next = &new+8`. So **the builder's `+0x618` output object is created
here (size 0xe0, allocator line 0x56) and anchored at owner+0x78**.

`0x5752b0` repeats the identical idiom with a different size and anchor — `0xf8` bytes, tag `0x5e`,
line `0x2be`, ctor `571c48`, list anchor `owner+0x378` — which is why the pattern is reported as an
idiom, not as an output-specific fact.

## 3. The playable record and its three mutators

`6b14ac(record, playable)` writes the 0x28-byte element used by the whole family:

| offset | content | source |
| --- | --- | --- |
| `+0x00` | handle | `576a64(playable)` (falls back to the singleton at `[0x116cb40]` via `575f2c`) |
| `+0x08` | handle version | `w1` returned by the same call |
| `+0x10` | identity word | `5707c4` when `576c70(playable)` resolves, else `[[0x10e2248]]` |
| `+0x18` | identity version | the word after it (or `[[0x10e2248]+8]`) |
| `+0x20` | clamped word | `max([playable+0x44], 0)` via `bic w8,w8,w8,asr#31` |

Three writers exist, all operating on `{base=[vec], count=[vec+0x10], capacity=[vec+0x18]}`:

* `6bbae4` — push: grows through `6bbb54` when `count+1 > capacity>>1`, then copies 16 B + 8 B + 4 B
  + 4 B to `base + count*0x28`.
* `6bb9ac` — push int: same growth test, then stores `[[p]+8]` (0 when `[p]` is null).
* `6b9994` — insert at index: index recovered by the usual `0x28` magic multiply, grows through
  `6b9f6c`, shifts with `109ad20` (the same move routine used by unbind), then writes the record.

`6b9f6c`/`6bba08` are 3-instruction thunks (`mov w3,#0x28; mov w4,#8` / `mov w1,#4; mov w2,#4; b`),
i.e. the grow helper parameterised by element size and alignment.

## 4. Bind / unbind / set, and what bit 4 of `+0x194` means

`6ce4b4(animator, playable)` is the field setter for `animator+0xd0`:

```
6ce4c0  ldr x0,[x0,#0xd0] ; cbz -> skip
6ce4cc  mov x1,x19 ; bl 6b9638        ; unbind the previous playable
6ce4d4  str x20,[x19,#0xd0]           ; store the new one
6ce4ec  b 6b97d0                      ; tail-branch into bind
```

`6b97d0` (**bind**, 452 B) and `6b9638` (**unbind**, 408 B) both begin with the same guard:
`ldrb w,[x0,#0x194]; tbnz w,#4,<assert>`. The assert strings are attached to those exact branches:

| site | string VA | string |
| --- | --- | --- |
| `0x6b988c` | `0xcf1dc` | `Cannot bind playable while the Animator is being evaluated.` |
| `0x6b970c` | `0x126b27` | `Cannot unbind playable while the Animator is being evaluated.` |

So **bit 4 of `+0x194` is the "being evaluated" state** for this object — the first byte-level meaning
attached to that guard in this lane (130 only saw bit 6 set/cleared around the batch path, a different
bit). The assert path materialises a `52e15c` string object, calls `b2e604`, and frees through
`3c9438` with line `0x206`, then returns.

**Bind** (`6b97d0`), after the guard:

1. `x1 == 0` → return.
2. Walk the table: for each 0x28 element, resolve `value = [[handle]+0x20] & ~1 == version & ~1 ?
   [handle+0x28] : 0`; if `value == playable` the bind is a **no-op** (jump straight to the epilogue).
3. `576c70(playable)` → if it resolves to **nothing**, build a record and **append** (`6bbae4`), then
   return **without refreshing**.
4. If it resolves to `[x19+0x608]` (the current controller handle), build a record and **insert at
   index 0** (`6b9994` with `x1 = [table]`), so the controller's own playable comes first.
5. Otherwise build a record and **append**.
6. Both insert/append paths then run `6b6d60(x0)`, `6b22c8(x0)`, `6b80e0(x0)`.

**Unbind** (`6b9638`), after the guard:

1. Find the element whose resolved value equals the argument, `memmove(109ad20)` the tail over it and
   decrement `[+0x178]`.
2. `5770fc(playable)`; if it returns the current controller handle (`[+0x608]`), clear `[+0x5d8]`,
   clear `[+0x608]` and `49fe68(animator+0x540)`.
3. If the table is now non-empty **and** bit 7 of the guard word is set **and** `[+0x188] != 0` →
   full refresh `6b92c4`; otherwise `6b6d60` then `6b80e0`.

That is the first place where the two refresh shapes are separated by decoded code rather than by
guessing: **bit 7 + `+0x188` selects the full composite on the unbind path**, while bind always uses
the light `6b6d60 → 6b22c8 → 6b80e0` sequence.

## 5. What the builders actually push into the driver vector

`6b80e0` (228 B, 13 field rows) is the refresh that 132 could only name:

```
6b80ec  add x20,x0,#0x498 ; bl 572a9c        ; clear the driver vector
6b80fc  ldr x8,[x19,#0x178] ; cbz -> second loop
loop 1  entry=x21=[+0x168]; stride 0x28
        6b8110  bl 6b1538                    ; resolve the playable entry
        6b811c  ldr x0,[x22,#0x20]           ; payload
        6b8120  bl 572834 ; tbnz w0,#0,skip  ; one-bit test
        6b8128  ldr x8,[x22]                 ; entry vptr
        6b8134  ldr x8,[x8,#0xa8]
        6b8138  blr x8                       ; per-entry virtual call with the driver vector
loop 2  record=x20=[+0x498], count=[+0x4a8], stride 0x10
        6b8160  ldr x8,[x20] ; if 0 → 0
        6b8168  ldr w9,[x20,#8] ; and #0xfffffffe
        6b816c  ldr w10,[x8,#0x20] ; cmp ; b.ne → 0
        6b817c  ldr x0,[x8,#0x28]            ; resolved record value
        6b8188  bl 6d14d4
        6b819c  cmp w0,w8 ; csel w8,w0,w8,gt ; str w8,[x19,#0x4b8]
```

So the "driver vector" is a `0x10`-stride array of `{handle, version}` pairs written by each playable
entry through its own `+0xa8` slot; the second loop resolves those pairs with the **same** `& ~1`
version test used by bind/unbind and folds the per-record word returned by `6d14d4` into a running
maximum at `+0x4b8`. `6b8138` is one indirect call; the probe recorded two rows because both
`ldr x8,[x22]` and `ldr x8,[x8,#0xa8]` reach the same `blr`, and the verifier keeps only the nearest
one. The `+0xa8` slot belongs to the playable/entry class, not to any table pinned in 129, so no
target is claimed for it.

`6b7c58` is the collector that fills the other vector, `animator+0x4e0`:

```
requires [x0+0x208] != 0
container = [x1] ; count = [container+0x10] ; base = [container+0x18] ; stride 0x20
for each record: if [record+8] != 0x16 -> skip
                 value = [record+0x18]
                 if value == previous -> skip
                 push int [[value]+8] through 6bb9ac
```

`6b92c4` is the full composite — `6b2050(x0)`, `6b6d60(x0)`, `6b6dec(x0)`, tail `6b6fdc(x0)` — and
`6b6d60` is the "reset + rebuild" step: it clears `+0x188`, runs `6b82e8(+0x5e8)` and `6b2a0c(+0x208)`,
walks the playable table resolving each element with `6b1538`, skips entries whose payload passes the
`572834` bit-0 test, calls `6b832c(entry, animator+0xb0)` on the rest, then tail-branches `49fe68`
on `animator+0x518`.

## 6. The producer, and the slot it uses

`6cefdc` is 32 B and is fully decoded:

```
6cefe4  bl 6cf7b4        ; the graph-builder body from 127/129
6cefe8  ldr x8,[x19]     ; node vptr
6ceff0  ldr x1,[x8,#0xe0]
6ceff8  br x1            ; tail branch, never returns to the caller
```

`+0xe0` is a slot of the node **primary** table (`10b0c80`, 35 slots), and the cycle-129 pinned
membership resolves it to `0x6d017c` — the same target 129 reported for role "+0xe0". This is the
first time the slot is tied to a concrete caller: the per-node producer is `6cf7b4` followed by
`0x6d017c`. It is a tail branch, so from a caller's point of view `6cefdc` never returns.

## 7. Containers, and a correction to 132

`6b1538` is the lookup used by both refresh paths. It masks the version with `& ~1` at `+0x20`,
compares against the global `[0x10e2248]` first, then walks `[handle+0x28]` and indexes
`[resolved+0x30]+0x20` with `max([key+0x20],0)`, bounding by `[resolved+0x18]` and following a chain
through `ldrsw [slot+0xc]`. It returns 0 on any miss. The same `3c9298`/`6ce464`-style link idiom,
the same `& ~1` version masking and the same `max(…,0)` clamp recur in four different helpers, which
is why they are reported as shared conventions of this family.

**Correction to 132.** 132 described `6b08c0`, `6b08d8`, `6b08e4` as three identical argument thunks
(`mov w1,#8; mov w2,#8; b 0x3f1e30`). This cycle shows the same byte shape in-cluster:
`6bba08` = `mov w1,#4; mov w2,#4; b 0x3f1e30` and `6b9f6c` = `mov w3,#0x28; mov w4,#8; b 0x3f1cb4`,
and it shows what the shape is for: `6bb9ac` and `6bbae4` call these thunks **only** on the grow path
(`count+1 > capacity>>1`). So the correct reading is *container-growth thunks parameterised by
element size and alignment*, not "generic temporary thunks". The 132 numbers themselves (8 cluster
calls, 10 container refs) are unchanged; only the interpretation of those three callees changes.

## 8. Small helpers

* `575e80` is a 3-instruction getter: `return [0x116cb40]`. It is the singleton both handle ctors use
  as a fallback.
* `570520(obj)` → field `+0x10`; `576a64(obj)` → field `+0x20`. Both fetch/instantiate the singleton,
  store it, then write `[singleton+0x28] = obj` and read `w1 = [singleton+0x20]`. So a handle is
  `{field, version}` and the singleton gets a back-pointer.
* `6b753c(obj)` and `6b3e30(obj)` are the same release shape: if the wrapped pointer at `+0` is
  non-null and bit 0 of the word at `+0x18` is clear, call `3c9438(ptr, size, 0x12da21, 0x306)` and
  clear the slot. `3c9438` is the dealloc sink already named in 127.

## 9. What did NOT run, and what is not claimed

* **No instruction of `libunity.so` was executed in this cycle.** There is no emulator, no synthetic
  object, no injected service and no sink invocation: every number above comes from decoding the
  original bytes read out of the pinned XAPK. The list of "synthetic services" for this cycle is
  therefore empty, and the list of original code that did not run is *all of it*.
* Bodies are capped at `0x800` and no body here was truncated (largest extent 452 B).
* One follow level only: `6b22c8`, `6b2050`, `0x6b6dec`, `0x6b6fdc`, `0x6b82e8`, `0x6b2a0c`,
  `0x6b832c`, `0x572a9c`, `0x572834`, `0x5707c4`, `0x576c70`, `0x5770fc`, `0x575ee0`, `0x575f2c`,
  `0x571c48`, `0x3c9298`, `0x3c9438`, `0x49fe68`, `0x52e15c`, `0x109ad20`, `0x109acc0`, `0xb2e604`
  are named only as call targets; their own bodies are not read here.
* `ldp`/`stp` are not decoded as field rows, so a multi-register access is invisible in the field
  counts; the 90 field rows count single-register `ldr`/`str` on `x0`/`x19`/`x20` only.
* Field offsets are raw bracket accesses. None of them, and none of the strings, is a class name or
  an Animator-wide statement. "Playable", "driver" and "controller" are labels taken from the
  recovered strings and field usage, not from symbols.
* `+0x188`, `+0x5d8`, `+0x608`, `+0x4b8`, `+0x4e0`, `+0x498` are offsets in *one* object whose class
  identity is still unknown; only `[+0x194]` bit 4 gets a meaning from the recovered assert text.

## 10. Reproduce

```
python3 tools/recovery/owner133.py --xapk /tmp/apk/windwings.xapk
python3 tools/verify/owner133.py --write
python3 tools/verify/owner133.py --check
python3 -m unittest tests.test_owner133 -v
```

## 11. Verification (final)

| check | result |
| --- | --- |
| `python3 tools/verify/owner133.py --check` | PASS, artifact 5441 B `73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707` |
| `python3 -m unittest tests.test_owner133 -v` | 22 tests, 0.096 s, OK |
| `python3 -m unittest discover -s tests` | 1912 tests, 341.625 s, OK |
| CI `Verify extracted tables` | run 40464366790, job `verify`, success on `da1df8ef5` |
| recovery run | 40463822530 (`9bf7a391f`) |
| receipts | `reverse-engineering/raw/l3-ef6b75ef133-verification/` (claim, ci, ci-jobs, check, local, focused.log.gz, full.log.gz, handoff) |
| official handoff | PR12 comment 6435908363 |
