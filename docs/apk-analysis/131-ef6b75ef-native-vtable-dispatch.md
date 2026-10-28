# 131 — who can dispatch the animator-side vtable slots (ef6b75ef, static)

Status: **provisional**. Static byte scan only: no instruction executed, no symbol used, no
class name claimed. This cycle answers review question 1 of the 130 handoff.

## 0. Pins

| item | value |
| --- | --- |
| XAPK SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| `libunity.so` SHA-256 / size | `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7` / 17783496 B |
| probe | `reverse-engineering/raw/owner131/probe.json.gz`, 29293 B, `a685acffa0c5b93f3c7392fe8ef2ac90cb0e288cf5ae742902050df699f852c9` |
| recovery tool | `tools/recovery/owner131.py` (SHA-256 in artifact pins) |
| verifier | `tools/verify/owner131.py` |
| artifact | `datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz`, 4749 B, `70cb303b9a306e7851d3911282ee81342e6d1d910be368fda039ac2590377198` |
| recovery run | 40406003345 on `700027eca` (after the ADD-half fix) |

## 1. Method

One pass over the single executable segment (`va 0x36c3a0`, 13827552 B) of the original
`libunity.so`:

1. every `ADRP` is paired with a following `ADD`/`LDR` on the same register within four
   instructions; the resolved address is compared with the nine animator-family vtables and the
   seven global containers already used by 130;
2. every 64-bit `LDR Xt,[Xb,#off]` whose offset equals one of the four slot offsets
   (2→`0x10`, 3→`0x18`, 31→`0xf8`, 33→`0x108`) is recorded, together with the nearest `BLR Xt`
   within eight instructions;
3. base-register provenance is classified as `vptr_from_x0` (the base itself was loaded from
   `[x0]` within six instructions), `adrp_base`, or `unknown`;
4. the owning FDE is resolved from the original `.eh_frame` table; one caller level (`BL`/`B`)
   is collected for the owners;
5. sites are kept if provenance is known or the owner lies inside `0x6b0000..0x6c0000`
   (the animator cluster); otherwise only a sample is kept so that exact match counts stay exact.

The verifier re-decodes the stored bytes: it recomputes every `ADRP+ADD` target, re-checks the
`LDR` offsets and re-checks that the `BLR` consumes the register the `LDR` wrote.

## 2. Result 1 — the vtable is materialised by the installer only

| table | `ADRP+ADD` references |
| --- | --- |
| `10b0c80` (animator, 35 slots) | 2 — `6b15f8` (owner `6b15d4`) and `6b9acc` (installer `6b9ac4`) |
| `10b0f98` (43) | 3 — `6ceb98`, `6d23e0`, `6d2444` |
| `10b1240` (28) | 3 — `6d3550`, `6d5bec`, `6d5c40` |
| `10b1330` (28) | 4 — `6d291c`, `6d5b30`, `6d5cf4`, `6d5d50` |
| `10b0f30` (11) | 1 — `6ce47c` |
| `10b1130` (2) | 1 — `6ceb94` |
| `10b1150` (28) | 1 — `6d28b4` |
| `10b1420` (2) | 1 — `6d3554` |
| `10b1100` (4) | **0** |

Total 16 materialisations. No code outside the installer/ctor cluster ever loads the animator
vtable address, so there is no dedicated dispatch stub that could serve as a static caller —
consistent with 130's "zero direct refs" for slots 2/3/10/31/33.

## 3. Result 2 — slot dispatch candidate pool

| slot | offset | loads | followed by `BLR` | qualified (stored) | distinct owners | inside cluster |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | `0x10` | 25214 | 1859 | 64 | 58 | 0 |
| 3 | `0x18` | 14770 | 3922 | 64 | 57 | 0 |
| 31 | `0xf8` | 537 | 61 | 21 | 16 | 0 |
| 33 | `0x108` | 885 | 223 | 64 | 58 | 1 |

For the update entry (slot 31), the 21 qualified sites split into 19 `vptr_from_x0` and 2
`adrp_base`; all 16 owners lie **outside** `0x6b0000..0x6c0000`, and one site has no FDE owner at
all. So the recovered update entry `6b947c` is reached only through generic
`ldr xN,[vptr,#0xf8]; blr xN` sequences spread across sixteen unrelated engine functions — the
binary contains no site that both belongs to the animator cluster and dispatches that slot.

This is a bounded negative: a unique dispatcher cannot be named from static slot-index matching
alone, because `0xf8` is a generic vtable index. Distinguishing "the engine's animation job
dispatcher" from any other interface call requires the object type at each site, which bytes
alone do not provide here.

## 4. Result 3 — container references

| container | references | distinct owners | note |
| --- | --- | --- | --- |
| `0x10e18b0` | ≥64 (capped) | 59 | widely shared registry, not animator-specific |
| `0x10e18f8` | ≥64 (capped) | 62 | same |
| `0x10e19c8` | ≥64 (capped) | 62 | same (also used by `3e079c`) |
| `0x10e18b8` | 63 | 54 | same |
| `0x10e19d0` | 32 | 29 | same |
| `0x10ecb08` | 10 | 10 | batch container used by `6b27dc` in 130 |

The batch container is the only one of these whose reference set is small enough to be
animator-specific; the others are shared engine globals, so the 130 reading of `0x10e18b0` as a
generic id→object registry is unchanged.

## 5. What did NOT run, and what is not claimed

- No instruction was executed; the scan is a byte pattern match plus FDE attribution.
- Slot-index matches are **not** class evidence: `0x10`, `0x18`, `0xf8`, `0x108` are ordinary
  vtable indices and appear in thousands of unrelated classes.
- Only 64 rows per slot are stored; the load/BLR counts are exact, the stored sample is not the
  full population.
- Base provenance is limited to a six-instruction lookback and two patterns; longer setup
  sequences are classified `unknown`.
- No dispatcher, no owner class, no runtime vtable identity and no job/scheduler object is
  named. `#27` full closure is still open.

## 6. Reproduce

```
python3 tools/recovery/owner131.py --xapk /tmp/apk/windwings.xapk
python3 tools/verify/owner131.py --write
python3 tools/verify/owner131.py --check
python3 -m unittest tests.test_owner131 -v
```

## 7. Verification (final)

| check | result |
| --- | --- |
| `python3 tools/verify/owner131.py --check` | PASS, artifact 4749 B `70cb303b9a306e7851d3911282ee81342e6d1d910be368fda039ac2590377198` |
| `python3 -m unittest tests.test_owner131 -v` | 15 tests, 0.079 s, OK |
| `python3 -m unittest discover -s tests` | 1870 tests, 297.232 s, OK |
| CI `Verify extracted tables` | run 40406194497, job `verify`, success on `f13f770dd` |
| recovery run | 40406003345 on `700027eca` (first attempt 40405384979 failed on a phdr offset bug, now diagnostic-captured) |
| receipts | `reverse-engineering/raw/l3-ef6b75ef131-verification/` (claim, ci, ci-jobs, check, local, focused.log.gz, full.log.gz, handoff) |
| official handoff | PR12 comment 6428104532 |
