# 132 — do the dispatch-candidate owners actually touch the animator? (ef6b75ef, static)

Status: **provisional**. Byte scan and FDE attribution only: nothing executed, no symbol used, no
class name claimed. This closes review question 1 of the 131 handoff and partly corrects 131's
reading of the batch container.

## 0. Pins

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe stage 1 | `reverse-engineering/raw/owner132/probe.json.gz`, 35063 B, `2a6ddfff033acca079842b7da2db8c359b9737f7b77c85ab252f015d3ceea69d` |
| probe stage 2 | `reverse-engineering/raw/owner132b/probe.json.gz`, 923 B, `89f39fdea833628c8162f808f7d4d4e7327925c26b5e4bdb7577d2f05f89c54b` |
| recovery runs | 40461994601 (`06783d220`), 40462227499 (`dd7c63d7a`) |
| upstream pins | cycle 130 artifact `6afffcec…`, cycle 131 artifact `70cb303b…` |
| artifact | `datas/l3_ef6b75ef132_native_dispatch_owners.json.gz`, 11962 B, `5037ba3b2641ca31c2860ec69cf142f69b8ab90591e6ad88d4838a1a66bc876d` |

## 1. Method

Stage 1 recovers the original FDE bodies (cap `0x1000`) of three sets of owners found by 131:

* **16** owners of qualified `ldr xN,[vptr,#0xf8]; blr xN` sites (the slot-31 pool),
* **10** owners of `ADRP+ADD` references to `0x10ecb08` (the batch container),
* the one in-cluster dispatch site owner `6b7d58`.

Each body is decoded again in the verifier from the raw bytes (not trusted from the probe): direct
`BL`/`B` transfers are split into `bl` (calls), external `b` (tail branches) and intra-FDE branches,
cluster membership is `0x6b0000..0x6c0000`, and every `ldr [vptr,#slot]; blr` site is re-decoded
with its vptr provenance. Stage 2 attributes 16 named callees to their FDEs.

Totals over the 27 bodies: **442 `bl`**, **6** external `b`, **169** intra-FDE branches, 56 dispatch
sites, 86 callers.

## 2. Answer: the slot-31 pool never touches the animator

| group | owners | `bl` | cluster calls | container refs | field hits | dispatch sites |
| --- | --- | --- | --- | --- | --- | --- |
| slot-31 dispatch owners | 16 | 266 | **0** | **0** | 1 (`0xe4515c` reads `+0x188`) | 52 |
| batch-container owners | 10 | 160 | 8 | 10 | 0 | 2 |
| in-cluster owner `6b7d58` | 1 | 16 | 2 | 0 | 1 | 2 |

None of the 16 slot-31 owners contains a `BL` into `0x6b0000..0x6c0000` and none references any of
the six containers. The single field hit is one load of `+0x188` inside `0xe4515c`, and `0x188` is a
generic offset, so it is not evidence of type. Combined with 131 (no animator-owned dispatch site
exists for slot 31), the honest statement is: **in this build the update entry `6b947c` has no
recoverable static caller**, only vtable membership plus 16 unrelated generic dispatch sites.

Their own dispatch profile is ordinary interface traffic: slots 31 shipped 24 times, 33 shipped 21
times, 2 three times, 3 twice, 10 twice.

## 3. The one real in-cluster dispatch: `6b7d58` on itself

`6b7d58` (the graph builder recovered in 129) reads its own vptr and dispatches two slots:

| site | instruction | slot | resolves to |
| --- | --- | --- | --- |
| `6b7e0c` / `6b7e10` | `ldr x8,[x8,#0x50]` / `blr x8` | 10 | `3e079c` (accessor, cycle 130) |
| `6b7f50` / `6b7f54` | `ldr x8,[x8,#0x108]` / `blr x8` | 33 | `6b6ab8` (parameter entry, cycle 130) |
| `6b7f04` / `6b7f08` | `ldr x8,[x8,#0x28]` / `blr x8` | output `+0x28` | not resolved (output vtable `10b0f30`) |

The receiver is the object itself: `6b7e00` and `6b7f48` are `ldr x8,[x19]` and `x19` is the
argument, whose `+0x19c`, `+0x608`, `+0x618`, `+0x628`, `+0x498`, `+0x4a8` fields are the animator
offsets from cycles 129–131. Slot resolution reuses the committed cycle-130 vtable membership, whose
SHA is pinned in this artifact.

The 43 byte-verified facts in the artifact track the body in order: id gate at `6b7d7c`/`6b7d84`,
handle creation `6b7dfc` → `6b7e74`, `"%s.Animator"` at `0xc0fce`, output creation `6b7ec8` with
`"AnimatorOuput"` at `0x101411`, `+0xdc = -1` at `6b7eec`, output-slot call at `6b7f08`, mode word
`+0x190` → `cinc` at `6b7f34`/`6b7f40`, the slot-33 self-dispatch at `6b7f50`, the driver-array walk
`6b7f60..6b8028`, the per-node producer call `6cefdc` at `6b8010`, and a stack-canary failure path
`6b8050` → `0x109acc0`.

## 4. Correction to 131: `0x10ecb08` is not animator-specific

131 called `0x10ecb08` "the only container small enough to be animator-specific". The bodies say
otherwise: **9 of its 10 referencing owners never call into the animator cluster** and never read an
animator field. What is true is narrower — within `6b27dc`, the container is iterated and each
element is flushed with `6b1c98(el, 0)`, so the container *can hold* animator objects; it is a shared
engine global, not an animator registry.

The three cluster callees that group revealed, `6b08c0` / `6b08d8` / `6b08e4`, are three 3-instruction
thunks of identical shape (`mov w1, #8`, `mov w2, #8`, `b 0x3f1e30`), each called with `x0 = sp+offset`
on an early-exit path of `b6ab88`. They are generic temporary/argument thunks, not animator logic.

## 5. Callee attribution (stage 2)

| address | owning FDE | extent | note |
| --- | --- | --- | --- |
| `6ce4b4` | itself | `0x48` | **not** interior to `6ce464`; the graph builder calls a different ctor than 129 assumed |
| `6ce464` | itself | `0x34` | the output ctor of cycle 129 |
| `6ce4fc` | itself | `0x5c` | output vtable `+0x28` target |
| `6b7fe8` | `6b7d58` | offset 656 | interior address — an intra-function branch, not a call |
| `109acc0` | **none** | — | lies in the executable segment but no FDE covers it (canary failure stub) |
| `6b08c0/8d8/8e4` | themselves | `0xc` each | the three thunks above |

## 6. What did NOT run, and what is not claimed

- Nothing was executed; every number is a byte decode.
- Slot numbers come from a fixed offset map and are not class evidence; the 16 slot-31 owners stay
  anonymous.
- Bodies are capped at `0x1000` bytes; `0x8b3644`, `0xef4c68` and `0xf1d6bc` have larger extents and
  were truncated.
- The output vtable `10b0f30` slot `+0x28` is not resolved here; its 129 target `6ce4fc` is named only
  as the callee that stage 2 attributed.
- No Animator-wide closure, no scheduler, no render, no runtime state.

## 7. Reproduce

```
python3 tools/recovery/owner132.py  --xapk /tmp/apk/windwings.xapk
python3 tools/recovery/owner132b.py --xapk /tmp/apk/windwings.xapk
python3 tools/verify/owner132.py --write
python3 tools/verify/owner132.py --check
python3 -m unittest tests.test_owner132 -v
```

## 8. Verification (final)

| check | result |
| --- | --- |
| `python3 tools/verify/owner132.py --check` | PASS, artifact 11962 B `5037ba3b2641ca31c2860ec69cf142f69b8ab90591e6ad88d4838a1a66bc876d` |
| `python3 -m unittest tests.test_owner132 -v` | 20 tests, 0.078 s, OK |
| `python3 -m unittest discover -s tests` | 1890 tests, 338.578 s, OK |
| CI `Verify extracted tables` | run 40462435663, job `verify`, success on `5ba12c56c` |
| recovery runs | 40461994601 (`06783d220`), 40462227499 (`dd7c63d7a`) |
| receipts | `reverse-engineering/raw/l3-ef6b75ef132-verification/` (claim, ci, ci-jobs, check, local, focused.log.gz, full.log.gz, handoff) |
| official handoff | PR12 comment 6435624425 |
