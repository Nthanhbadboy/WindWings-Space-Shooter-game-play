# 134 — the leaf layer behind refresh, apply and the producer (ef6b75ef, static)

Status: **provisional**. Bytes only: no instruction of `libunity.so` was executed, no object was
fabricated, no sink was invoked, no symbol or class name is used. This cycle opens the layer that
133 could only name as call targets.

## 0. Pins

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe | `reverse-engineering/raw/owner134/probe.json.gz`, 6495 B, `08237392b0a5e53579712d8d61cbe73945ebf01d860215d3980e9f1f26907fac` |
| recovery runs | 40489662914 (`a45b2dd4f`), evidence commit `c4bd75bc4` |
| upstream pins | cycle 129 artifact `217f8893…`, cycle 133 artifact `73542233…` |
| artifact | `datas/l3_ef6b75ef134_native_refresh_leaves.json.gz`, 7556 B, `74cf1843928d165058771269c2508337df33be9b4840edfd9c5e076e358062e6` |

## 1. Method

Fifteen seeds are recovered from the pinned XAPK cache (fail-on-miss), each one a callee that 133
named but never read; one follow level adds nine in-cluster bodies (24 functions max, bodies capped
at `0x800`). The verifier decodes all 24 bodies again from the stored hex, splits `BL`/`B` into
calls, external tail branches and intra-FDE branches, re-derives every indirect-call site with its
base register, and re-checks **211 annotated instruction facts** byte for byte. Slot numbers resolve
only where a pinned table covers them (cycle 129 membership).

Totals: **24 bodies**, 4424 B of original code, **108 direct transfers** (80 `bl`), **25 in-cluster
calls**, **11 indirect call sites** (24 raw `ldr`→`blr` rows, see §3), **1 string**, **110 field
rows**.

| entry | extent | role | bl | cluster | indirect | fields |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `0x6d017c` | 1124 | producer implementation: guard, per-int resolve, vector append, reset warning | 26 | 2 | 5 | 19 |
| `0x6d14d4` | 48 | per-record word folded into the `+0x4b8` maximum | 0 | 0 | 1 | 2 |
| `0x6b6dec` | 496 | evaluate: resolver, single-playable path, scratch object, counter, mirror byte | 13 | 9 | 2 | 14 |
| `0x6b6fdc` | 248 | apply: seed `6b2ce8`, per-entry `+0x98`, `+0x491` accumulator | 3 | 3 | 1 | 6 |
| `0x6b2050` | 312 | skin step of the full refresh | 7 | 6 | 0 | 11 |
| `0x6b832c` | 108 | recursive child walk through slot `+0xd0` | 2 | 0 | 1 | 2 |
| `0x6b22c8` | 136 | post-bind mode select between two per-entry calls | 4 | 1 | 0 | 5 |
| `0x6b6c40` | 132 | handle → object resolver (registry `0x10e18b0`, fallback `3d8614`) | 2 | 0 | 0 | 4 |
| `0x6b2a0c` | 88 | container reset with an explicit deleter callback | 1 | 1 | 1 | 6 |
| `0x6b82e8` | 68 | vector reset (same shape as `572a9c`) | 1 | 0 | 0 | 3 |
| `0x572a9c` | 68 | vector reset: free + zero + 16-byte fill | 1 | 0 | 0 | 3 |
| `0x5707c4` | 68 | identity pair (singleton fallback, back-pointer) | 2 | 0 | 0 | 6 |
| `0x576c70` | 60 | handle → payload, rejecting when payload flag bit 1 is set | 0 | 0 | 0 | 2 |
| `0x5770fc` | 44 | handle → payload without the flag test | 0 | 0 | 0 | 2 |
| `0x572834` | 28 | bit test on byte `+0xad` after `572c9c` | 1 | 0 | 0 | 0 |
| `0x49fe68` | 124 | pair array reset with the `-1` sentinel | 1 | 0 | 0 | 3 |
| `0x6bb950` | 92 | int vector append used by the producer | 1 | 1 | 0 | 4 |
| `0x6bb944` | 12 | growth thunk 4 / 4 → `3f1e30` | 0 | 0 | 0 | 0 |
| `0x6b3c84` | 320 | temporary buffer helper (alloc, `0xff` fill, two transforms, free) | 6 | 0 | 0 | 1 |
| `0x6bf2a0` | 188 | float channel sampler | 2 | 0 | 0 | 4 |
| `0x6bf108` | 196 | int channel sampler | 2 | 0 | 0 | 5 |
| `0x6bf1cc` | 212 | mixed channel sampler (kind `0x0b` branch) | 3 | 0 | 0 | 4 |
| `0x6bf35c` | 136 | table lookup-or-create A | 1 | 1 | 0 | 2 |
| `0x6bf908` | 116 | table lookup-or-create B (tail of the skin step) | 1 | 1 | 0 | 2 |

## 2. The two numbers 133 left dangling now have definitions

**`+0x188` is not a free flag.** `6b6dec` (evaluate) ends with:

```
0x6b6fa8  ldrb w8,[x19,#0x1f1]     ; condition byte
0x6b6fb0  ldr  x8,[x21]            ; x21 = x19+0x208, the graph pointer
0x6b6fb8  cset w8, ne
0x6b6fbc  strb w8,[x19,#0x188]     ; mirror byte = (graph pointer != 0)
```

So the 133 unbind gate — bit 7 of `+0x194` **and** `[+0x188] != 0` → full refresh `6b92c4` — reads
as *"full refresh only while a graph is actually present"*. Nothing in this cycle extends that to a
claim about what the graph is.

**`+0x4b8` is a maximum over a specific word.** `6d14d4` is 48 B:

```
0x6d14d8  ldr x8,[x0] ; 0x6d14e0 ldr x8,[x8,#0x138] ; blr     ; boolean query, slot +0x138
0x6d14e8  tbz w0,#0 -> 0                                       ; no value when bit 0 is clear
0x6d14ec  ldr x8,[x19,#0x128] ; 0x6d14f0 ldr w0,[x8]          ; the word at [value]
```

so the accumulator in `6b80e0` (`csel w8,w0,w8,gt; str w8,[x19,#0x4b8]`) folds the **word found at
`[entry+0x128]`**, gated by the same slot `+0x138` that the node uses as a boolean query. `+0x128`
was already labelled "clip-data result of virtual `+0xa8`" in 127's field map, so this is the first
byte-level tie between 133's maximum and a clip-data object.

## 3. What the producer implementation does (slot `+0xe0`)

`6cefdc` runs the graph-builder body and tail-branches through `[vptr+0xe0]`; the 129 membership
resolves that slot to `0x6d017c`, so this is the code a per-node producer actually ends in.

```
0x6d01ac  ldr x8,[x8,#0x138] ; blr        ; same boolean query as the accumulator
0x6d01b4  tbz w0,#0 -> return 1           ; bit 0 clear => nothing to do
0x6d01b8  ldr x8,[x19,#0x160] ; cbz -> body
                                          ; non-empty own vector => return 1
body  0x6d01f8  ldr x0,[x19,#0x118]       ; source object
      0x6d0204  ldr x8,[x8,#0xc8] ; blr   ; source virtual slot +0xc8 -> element view
      0x6d020c  ldr x1,[x0,#0x10]         ; source element count
      0x6d0220  mov w2,#4 ; mov w3,#4     ; grow with element size 4, alignment 4
      0x6d023c  str x19,[x19,#0x178]      ; the node stores itself at +0x178
loop  0x6d0274  ldr w23,[x26]             ; each source element is an int
      0x6d02c4  bl 3d8614                 ; int -> object
      0x6d0320  blr [obj vptr +0x148]
      0x6d0380  blr [obj vptr +0x110]
      0x6d03c0  bl 5798a8                 ; keep/skip decision on [obj+0x118]
      0x6d03e0  str w23,[base,count,lsl#2]  ; append (fast path)
      0x6d04d8  blr [obj vptr +0x60] with w1 = 0x3d   ; only for the newest element
```

It returns `bool ([node+0x160] != 0)`. The vector is `{base +0x150, count +0x160}` grown by
`6bb944` (`mov w1,#4; mov w2,#4; b 3f1e30` — the same growth-thunk family as 133's `6bba08`) and
appended by `6bb950`, which is the same push idiom as 133's `6bb9ac` (identical `ldp`/`cmp`/`str`/`ldr`/`str` sequence, differing only in which growth thunk it calls).

**The one string in this cycle lives on the warning path**, not in the append loop:

```
0x6d04f0  cbnz x9 -> epilogue            ; source element count != 0 => no warning
0x6d04f4  ldr x8,[x19,#0x160] ; cbz -> epilogue
0x6d0520  adrp x0,#0xe6000 ; 0x6d0524 add x0,#0x68b      ; string 0xe668b
0x6d053c  bl 52e15c                       ; materialise
0x6d0588  bl b2e604                       ; log
0x6d05a8  bl 3c9438 (line 0x206)          ; free the message buffer
```

The first 64 original bytes at `0xe668b` are
`An animator Reset was caused during %s::Awake. This will lead to` — captured at the probe cap, so
the sentence continues beyond the capture and is **not** quoted further. The condition is exact and
narrow: *the source object has zero elements while the node's own vector is non-empty*.

## 4. Apply, evaluate, skin

**Apply (`6b6fdc`)**: seed `6b2ce8(animator, +0x1b8, +0x208, +0xb0, +0x640)`; then for every
playable entry: resolve (`6b1538`), prepare (`6b2eec`), call virtual `+0x98` with the driver vector
`+0xb0`; then walk the `0x10`-stride driver pairs, apply the `& ~1` version mask, read
`[[resolved]+0x160]`, and OR the non-null result into **`+0x491`** — a byte that says "at least one
driver target carries that pointer".

**Evaluate (`6b6dec`)**: `6b6c40` (resolver) then `6b6850`; if there is **exactly one** playable, a
separate path runs virtual `+0xb0` on the resolver result. Otherwise it builds a scratch object at
`+0x5e8` through `6b7cf8`, consumes it with `+0x1a0` through `6c7060`, walks the playable table
calling virtual `+0xc0` with `+0x518`, releases the scratch object with 133's destructor `6b3e30`,
resets `+0x208` through `6b2a0c`, calls `6da998`/`6b2bdc`, maintains a counter at `+0x610` (2 or
increment), seeds apply `6b2ce8`, and finally writes the `+0x188` mirror.

**Skin (`6b2050`)**: requires `[+0x208]` and `[+0x1e0]`; when `[+0x19c]` and `[+0x608]` both resolve,
it formats a buffer with `6b3c84`; then it runs the three channel samplers in order — float
(`6bf2a0`), int (`6bf108`), mixed (`6bf1cc`) — each of which walks its own count/`0x20`-stride data
and consults a table at `sampler_input+0x38` or `+0x48`; mode `[+0x190] == 1` allocates a `0x40`-byte
object through `51a81c`; then `6bf35c`, a lookup through `3dfa9c` against the table at `0x10e8960`,
and a tail branch into `6bf908`.

The three samplers are the same skeleton with different shapes:

| entry | kind | count | data | table | extra |
| --- | --- | --- | --- | --- | --- |
| `0x6bf2a0` | float | `+0x10` | `+0x18` | input`+0x38` | `ldr s0`, test `6a99f0` |
| `0x6bf108` | int | `+0x30` | `+0x38` | input`+0x48` | base index `+0x20`, `ldr w1`, test `6a98c4` |
| `0x6bf1cc` | mixed | `+0x20` | `+0x28` | input`+0x48` | kind `+0x08 == 0x0b` selects `6a99a4` else `6a99f0` |

## 5. Handles, resets and the recursive walk

* `6b6c40` (already named as the resolver in 129) is byte-documented here: handle at `+0x19c` →
  hashed lookup `38cbb4` in the registry `[0x10e18b0]` → fallback `3d8614`.
* `576c70` maps a handle at `+0x30` to its payload at `+0x28` **only when bit 1 of `[payload+0x38]`
  is clear**; `5770fc` is the same lookup with no flag test. The two differ in exactly one branch,
  which is why 133's "which of the two does bind use" question has a byte answer.
* `5707c4` builds an identity pair: `[obj+0x28]` or the singleton through `575e80`/`575e8c`, writes
  the back-pointer `[handle+0x28] = obj`, and returns `{handle, [handle+0x20]}` in `x8`.
* `572a9c` and `6b82e8` are the same vector reset: free the wrapped pointer through `3c9438` (line
  `0x306`) unless bit 0 of `+0x18` is set, clear the pointer, and fill 16 bytes from `0x143ff0`.
* `6b2a0c` resets a container, then invokes a **deleter callback** from `+0x10` with a two-word
  descriptor whose first word is the constant `0x10b0b30`, and clears the slot last.
* `6b832c` walks children recursively: virtual `+0xd0` on the node, child count at `[[+0x30]+0x30]`,
  index accessor `6d788c`, then calls **itself** on each child.
* `6b22c8` picks between two per-entry calls: gate `3d98bc` bit 0, then `+0x189` byte and
  `+0x18c == 2` choose `5716c0` or `571174`.
* `49fe68` resets a `0x10`-stride pair array, writing the `-1` sentinel into the second word and
  delegating the first word to `49fdfc` unless the sentinel is present.

## 6. Corrections and warnings

* 133 read `[animator+0x178]` as a playable **count**. `6d017c` writes `self` into `[node+0x178]`.
  The same offset number in two bodies is **not** the same field: the node and the refresh object are
  different classes, and this cycle keeps them separate everywhere (the note is stored in the
  artifact).
* Slot `+0x138` is used as a boolean query on both the **node** (`6d017c`) and the **per-record value
  object** (`6d14d4`). The cycle-129 membership resolves it for the node's primary table only
  (`0x6d137c`), so no target is claimed for the value object.
* Indirect-call rows: the probe recorded 24 `ldr`→`blr` rows, the verifier keeps **11** sites because
  several `ldr`s feed the same `blr`. Both numbers are stored.

## 7. What did NOT run, and what is not claimed

* **No instruction of `libunity.so` was executed** — no emulator, no fabricated object, no injected
  service and no sink invocation. The list of synthetic services for this cycle is empty, and the
  original code that did not run is *all of it*.
* One follow level only. `6b6850`, `6b7cf8`, `6c7060`, `6da998`, `6b2bdc`, `6b2ce8`, `6b2eec`,
  `6b1538`, `5798a8`, `3d8614`, `51a81c`, `3dfa9c`, `6d0964`, `6e46cc`, `3c986c`, `109ace0`, `6f0c4`
  (`6bf0c4`), `518b40`, `6a98c4`, `6a99a4`, `6a99f0`, `6a9b90`, `6d788c`, `49fdfc`, `49fee4`,
  `572c9c`, `575e8c`, `575e80`, `6cee44`, `6d05e0`, `52e15c`, `b2e604`, `3c9438` are only named as
  call targets; their own bodies are not read here.
* `ldp`/`stp` are not decoded as field rows, so the 110 field rows count single-register `ldr`/`str`
  on `x0`/`x19`/`x20` only.
* Field offsets are raw bracket accesses and are not class evidence. "Playable", "driver", "graph"
  and "channel" are working labels taken from usage and from the recovered string; no class name is
  claimed.
* The `0xe668b` string is quoted only for the 64 bytes the probe captured; the sentence continues
  beyond that cap.
* Still open for #27-full: dispatcher/owner class, heap, scheduling, clip/clock writer,
  pose/blend/apply readback, render.

## 8. Reproduce

```
python3 tools/recovery/owner134.py --xapk /tmp/apk/windwings.xapk
python3 tools/verify/owner134.py --write
python3 tools/verify/owner134.py --check
python3 -m unittest tests.test_owner134 -v
```

## 9. Verification (final)

| check | result |
| --- | --- |
| `python3 tools/verify/owner134.py --check` | PASS, artifact 7556 B `74cf1843928d165058771269c2508337df33be9b4840edfd9c5e076e358062e6` |
| `python3 -m unittest tests.test_owner134 -v` | _pending_ |
| `python3 -m unittest discover -s tests` | _pending_ |
| CI `Verify extracted tables` | _pending_ |
| recovery runs | 40489662914 (`a45b2dd4f`) |
| receipts | `reverse-engineering/raw/l3-ef6b75ef134-verification/` |
| official handoff | PR12 comment _pending_ |
