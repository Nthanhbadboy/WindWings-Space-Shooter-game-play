# 129 — owner-side linkage for the graph builder (M1)

**Provisional / arena/ef6b75ef / #27.** Claim **6426998422**. Follows official 128 handoff **6426561197**, whose stated next step was M1: identify the owner class/vtable behind `node+0x118` slots `+0xb0`/`+0xa8`. This cycle answers the *producer* half with original bytes and narrows the open half to runtime state that static data cannot carry. It executes **no** FDE and fabricates **no** object.

## 1. What this layer does and does not do

- **Three new pinned probes**, all from the fail-on-miss XAPK cache (`f5d3c7a1…`), never from a local symbol table: `owner129` (8 windows, caller/linkage BFS), `owner129b` (24 windows, producer bodies + ADRP+ADD vtable installers), `owner129c` (16 windows, node ctor, owner registry, rodata strings, full table region). No whole-library disassembly is stored; per-root FDE extents are capped at 0x1000 bytes.
- **No execution.** Every producer of `node+0x118` needs a live object registry; the one execution domain that exists (null owner, 127) is untouched.
- **New static result.** `node+0x118` is the node's **owner field**, zeroed by the constructor and written by exactly one instruction (`6cef80`). Its value is a registry lookup by a runtime instance id, not a serialized pointer. The node class itself is now identified by the three tables its constructor installs.
- **New calibration.** The 0x10b0a00–0x10b1900 region resolves to **23 RELA-dense tables**; nine of them form the family this chain touches (**181** relocation-backed slots).

## 2. `node+0x118`: one writer, no serialized producer

| fact | evidence |
|---|---|
| field initialised to zero by the node constructor | `6ceba4` `stp xzr, x9, [x19,#0x118]` (word `7fa611a9`) |
| exactly one store to any `+0x118` field in all 36 unique captured windows | `6cef80` `str x1,[x0,#0x118]` (word `018c00f9`) |
| that store lives in the set-owner wrapper | `6cef64`, 120 bytes / 30 instructions, `6cef6c` compares the old owner |
| the wrapper is called from exactly one place | `6b8268`, inside `6b81c4` (73 instructions) |
| the value is resolved before the node exists | `6b81d0` `bl 6b6c40` → `x20`; `6b81dc` keeps it |
| the resolver keys on a runtime id | `6b6c4c` `ldr w8,[x0,#0x19c]`; zero id → null at `6b6cb0` |
| the registry is a global map | `6b6c58` `ldr x20,[0x10e18b0]`; lookup thunk `38cbb4` at `6b6c74` |
| fallback path | `3d8614(id)` at `6b6ca8`; it checks the hook at `0x111dba0` first (`3d8620`) |
| no RELA addend points at any of these entries | 0 for `6cf7b4`, `6cef64`, `6cefdc`, `6bba20`, `6b6c40`, `6ceb88` |

The second producer path does not write the field at all: `6cefdc` (8 instructions) is called on node-class objects taken from the vector at `animator+0x498` (`0x10`-byte records), after the owner equality check at `6b7ff0` and the node virtual `+0x138` gate at `6b8000`.

## 3. The node class and how it is created

`6bba20` (28 instructions) is the allocating constructor:

| step | PC | detail |
|---|---|---|
| size | `6bba34` | `x0 = x2 + 0x1d0` (call site passes `x2=0`) |
| allocator | `6bba4c` | original sink `3c986c`, align `0x10`, tag `0x5e`, line `0xab`, label VA `0x12da21` (empty string) |
| constructor | `6bba58` | `6ceb88(node, w1)` |
| guard | `6bba5c..6bba68` | byte `+0x38` bit 0 and halfword `+0xa8 != 0`; otherwise cleanup `570ff0` |
| attach | `6bba7c` | `572a38(controller, node)`; 25-instruction helper writes `node+0x20 = controller`, bumps `controller+0x34`, sets `controller+0xac \|= 0xC8` |

`6ceb88` (37 instructions) is the node constructor. It runs the 124 base constructor **`6d6aa0`** first, then installs three tables and clears the fields the graph builder later consumes:

| offset | value | witness |
|---|---|---|
| `+0x000` | `10b0f98` (43 slots) | `6cebb0` |
| `+0x110` | `10b1100` = primary + `0x168` (4 slots) | `6cebbc` |
| `+0x120` | `10b1130` = primary + `0x198` (2 slots) | `6ceba4` |
| `+0x118`/`+0x120` pair | owner = 0, table = `10b1130` | `6ceba4` |
| `+0x128`, `+0x138`, `+0x148` | cleared pairs | `6cebe0`, `6cebc4`, `6cebd4` |
| `+0x158` | `0x4b` | `6cebe4` |
| `+0x160` | 16-byte constant from `0x143ff0` | `6cebe8` |
| `+0x188..+0x1a7` | cleared | `6cebfc` |
| `+0x1c0`, `+0x1c8`, `+0x3c` | 0, 0, 3 | `6cec08`, `6cec0c`, `6cec10` |
| subobjects | `6c3dc8(node+0x170, node+0x110)`, `6a6ff4(node+0x1a8)` | `6cebec`, `6cec00` |

So the node is a **124-family derived class**: same base constructor, new primary table, and two additional interface tables packed immediately after the primary (offsets `+0x168`/`+0x198`), which is why the constructor's two extra pointers are plain arithmetic on the primary address.

## 4. Who reaches the two wrappers

`6b947c` (89 instructions) is the entry: it sits at table **`10b0c80` slot `+0xf8`** and has **0 direct BL/B references** in the whole-`.text` scan, i.e. it is reached only as a virtual member. From there:

```
10b0c80[+0xf8] = 6b947c
        ├── 6b7d58  (191 instr)  rebuild path → 6cefdc on each node in animator+0x498
        └── 6b81c4  ( 73 instr)  setup path   → 6bba20 node → 6cef64(node, owner)
```

`6b7d58` is the playable-graph rebuild and supplies the only two human-readable strings recovered from original rodata in this chain:

| VA | bytes | text |
|---|---|---|
| `0xc0fce` | 10 | `%s.Animator` |
| `0x101411` | 12 | `AnimatorOuput` |
| `0x12da21` | 0 | *empty* (allocation label) |

It builds the graph handle at `animator+0x618/+0x620`, an output object at `+0x628/+0x630` (allocator `3c9298`, 0xe0 bytes, constructor `6ce464` → vptr **`10b0f30`**, 11 slots, `+0xdc = -1`), then calls that output's slot `+0x28` with the node (`6b7f04`) and the animator's slot `+0x108` (`6b7f50`). `6b80e0` then walks the node vector: per node it calls a child's `+0xa8` and the max helper `6d14d4` (itself virtual `+0x138` then `*[node+0x128]`).

## 5. Resolved vtable family (9 tables, 181 slots)

| table | slots | install site | called slots |
|---|---:|---|---|
| `10b0f98` | 43 | `6ceb98` (node ctor), `6d23e0`, `6d2444` | `+0xe0`→`6d017c`, `+0x138`→`6d137c` |
| `10b1100` | 4 | `6cebbc` (node ctor) | — |
| `10b1130` | 2 | `6ceba4` as node data | — |
| `10b0c80` | 35 | `6b15f8`, `6b9acc` | `+0x50`→`3e079c` (name formatter), `+0x108`→`6b6ab8` |
| `10b0f30` | 11 | `6ce47c` (output ctor) | `+0x28`→`6ce4fc` |
| `10b1240` | 28 | `6d3550` (`6d353c`), `6d5bec`, `6d5c40` | RELA `+0x80`→`6d46a8` (120) |
| `10b1420` | 2 | `6d3554` (`6d353c`) | — |
| `10b1150` | 28 | `6d28b4` (`6d2894`) | — |
| `10b1330` | 28 | `6d291c`, `6d5cf4`, `6d5d50` | — |

`181` is the sum of RELA-backed slots in these nine tables; the region as a whole has **23** such tables. Slot counts are dense-run lengths, so unrelocated slots are *unknown*, not null.

## 6. M1 split and the M2 contract that follows

**M1a — producer linkage: CLOSED by byte evidence.** The field, its single writer, the value's origin (`6b6c40` → registry by `[animator+0x19c]`), the node class (`10b0f98`/`10b1100`/`10b1130`), its allocator (`3c986c`, `0x1d0` bytes) and its attachment (`572a38`) are all pinned.

**M1b — owner identity: OPEN, runtime-only.** Missing: the instance id stored at `animator+0x19c`, the registry contents behind `0x10e18b0`, and the owner object's vtable. No recovered code installs an owner vtable. Shape constraints only: the owner exposes slots `+0xb0()` (no args), `+0xa8(bool)` and `+0xd8()`, and a list head at `+0x38` that `49ffc8` splices against `animator+0x540`. The two strings are consistent with an Animator-side owner, but **no class name is asserted**.

**M2 — contract only.** The graph builder's motion object is the return of the owner slot `+0xa8` called with `w1=1` (`6cf80c`/`6cf810`), stored at `node+0x128` (`6cf814`); a null return selects the original error path at `6cf8f0`. Its `+0x10` is the count of `0x10`-byte records (`6cf8a4`/`6cf8b8`), allocated through `node+0xc0`'s vtable slot 0 with size `count<<4` and align 8 (`6cf8cc`). The three pinned builders `b98c98`/`b98db4`/`b99120` then receive `(motion_object, node+0xc0)` and fill `node+0x130`/`+0x138`/`+0x140`. Since the object arrives through a runtime owner slot, every builder input would have to be fabricated — so this cycle still runs none of them.

## 7. Pins

Original XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; libunity SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.

| Input | SHA256 | bytes |
|---|---|---:|
|`reverse-engineering/raw/owner129/probe.json.gz`|`565e276dd18e49c468868ec3955f0f76b18b6699a62ab7659dc898b4a25d73b6`|13911|
|`reverse-engineering/raw/owner129b/probe.json.gz`|`1e6e0792546a436814ae913d75f0369222ffd5e427f4be826749a8a485c6154c`|9411|
|`reverse-engineering/raw/owner129c/probe.json.gz`|`778b001b5dea6e994a5cd71a40013a3239417729858d7ab5156c4e16083591c1`|12372|
|`reverse-engineering/raw/graph127/probe.json.gz`|`43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`|12454|

Recovery runs: **40399193071** (`9707d26a5`), **40399523874** (`b39baaf17`), **40399754616** (`5076e2fb7`), all SUCCESS, fail-on-miss cache, evidence commit `[skip ci]`.

## 8. Limits, and what did not run

- Static bytes only. No FDE from this chain is executed: `6bba20` needs the original allocator service, `6ceb88` needs a real allocation plus two subobject constructors, `6b6c40` needs the live registry, `6cef64`/`6cefdc` need a real owner, and `6cf7b4`'s non-null branch needs the owner's `+0xa8` output. The eight `not_run` entries in the artifact carry the per-entry reason.
- No class names, no RTTI, no symbol claims; table identity is only the installed address and the RELA-resolved slot contents.
- No Unity readback, no render, no live Animator, no game instance, no #27-full closure. The M2 runtime object and the owner identity remain outside the static lane.

## 9. Coordination

Claim **6426998422**. Review requested: the single-writer argument for `node+0x118` (36 unique windows, word `018c00f9`), the owner=registry claim versus the 126 synthetic-owner model, the 124-lineage reading of `6ceb88`→`6d6aa0`, the `+0x168`/`+0x198` interface-table arithmetic, the nine-table slot counts, and the M1a/M1b boundary. #27 remains OPEN (M1b runtime owner, scheduler/dispatch, clip/clock writers, pose/blend/apply, Unity readback/render). No merge, no main push, no self-ACK; protected3 unchanged.
