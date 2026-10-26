# 119 — R1 independent review of ef HANDOFF123

provenance: **`arena/8141386a-windwings-space-shooter-game-p`**

Assigned spec98 `6423276716`; CLAIM `6423376382`. Review target **scientific
`1d6fbcbb7e5f8ae35135ee098b5a4816ea9d4f84`**, original report/receipts commit
`8ac0c7ab6`; verified subsequent documentation correction
**`ea6a3835f786306b07df9658262a6e3f6658f809`**. Not a review of mutable124/newer behavior.

## Verdict, findings, and what “independent” means

**APPROVE the bounded123 evidence after the two producer documentation corrections,
verified independently. NOT a #27-full ACK, game/runtime acceptance, or peer self-ACK.**

| ID | Finding | Disposition |
|---|---|---|
| R1-01 | “53→3 narrowing” was not a subset operation: different predicates, disjoint result sets | Producer acknowledged and corrected; selected-vptr byte proof remains valid |
| R1-02 | RELA addend points to an **encoded metadata-usage cell**, not direct UTF-8 `Stop` bytes | Producer acknowledged and corrected; full static token→metadata-payload chain independently verified |
| R1-N1 | Loop-count0 preserves manager+0x100=`0xA5`; count>0 writes1 then0 | Artifact/code correct; review preserves the conditional state effect, no universal zero claim |
| R1-N2 | Original FDE end is exclusive; several report ranges name final RET inclusive | Review supplies explicit end/RET distinction; not a new byte-extraction discrepancy |

Independent parts: own ELF64/metadata parser and **fresh original APK byte-read CI**;
own integer instruction checks; own Unicorn harness, guarded retained-byte reads and
write/value hooks. No producer123/122 verifier or producer Fixture is imported.
Shared parts: same original build/retained dependency bytes, same Unicorn2.1.4 backend,
and explicitly shared prepared fixture contract. Source118/119 ten-call output lineage
is **compared, not re-extracted/re-executed**. No clean-room ABI, independent game-state
source, original allocator/heap, Android session or Unity readback is claimed.

Artifact **`datas/l3_geometry_review_ef123_8141386a.json.gz`**, **9178B**, SHA256
**`e782ffdd7ebe08b7d315979784c0afa1836621a7c80f14a4219563215f6b94b1`**.
It contains the computed sets, original byte/FDE evidence, own four native fixture
replays, exact PC multiplicities/write values, marker decode, and explicit findings.

## 1. Review pins and read-only peer handling

| Target/proof | SHA256 |
|---|---|
| ef123 raw,21548B | `f194160b8a19989a7d368bc84c46b7934f8dabb7d4faa42d8c72819af12ae77e` |
| ef123 scientific artifact,7082B | `190864db435ee7ed32536ee75b8a10af20deabe288e5514bb3801977950aaf0c` |
| own fresh-original gzip,12991B | `571622a8de392f3c029f37340da4ec2923e85146c076bd8e5104db6cf6d803b2` |
| own original/peer CI receipt gzip,3436B | `c4872e801bbac642be87fdaa2c1f1a4e61af572bd9ce1c7cf352517796c9347d` |
| selected corrected-report gzip,6802B | `48b0b60e190315925e232416b3a291dad496f849067d3107cbaa1d653a15a8e0` |

Selected snapshots and `peer-pins.json` are under
`reverse-engineering/raw/geometry-8141386a/review-ef123/`. Only named byte artifacts,
small dependency probes, report/code snapshots for review and actual correction/CI
receipts were consulted/copied. Existing own files are reused only when exactly
SHA-equal to the pinned peer version. **No whole peer-tree import, tool overwrite,
peer-branch edit/push, or modified original artifact.** Report/code snapshots are inputs
for review, not executed producer tools or instructions.

The sandbox resumed at old own8b3689dcb; work was restored **ff-only from own remote**
e3fbb4dbc before review, never reset/rebased/synced from ef. Historical cache absence was
not interpreted as lost scientific evidence; actual historical118 CI run/jobs were
re-fetched and frozen separately before later live needle changes.

## 2. Fresh original static byte read — independent of retained projections

Own recovery **40378132845 SUCCESS**, exact setup source
**`c11405d772310dcbeda564e752041d76c27775dc`**, bot **`ab93f0718`** fetched ff-only.
It streams nested APK members to scratch, mmaps each original library, parses ELF64
program/section headers/RELA/EH header and reads only selected output spans. No original
ARM64 is executed in this recovery; native fixture replay is a separate stage.

Original authority:

- XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- libunity SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.
- libil2cpp SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`.
- metadata SHA `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`.

Measured fresh libunity corpus: **29626 RELA entries /29267 type1027 relative entries**;
**146** relative entries in vtable region`0x10B1000..0x10B1500`, **113** after the stated
code-band predicate. **106 unique peer windows** match fresh original bytes exactly
(the107 retained windows include duplicate6d2950). **104 selected original FDE/table
records** match retained source bytes and exclusive bounds. No window-byte/FDE mismatch.

A whole executable-segment B/BL scan independently finds exactly two direct graph calls,
while a whole-library relative-RELA scan finds **0 addends equal7154000 (`0x6D2950`)**.
This global-zero result is fresh-source checked, not extrapolated from the152 selected
probe relocations. Exact peer scientific Verify **40366819899 SUCCESS** on1d6fbcbb7 was
also checked through actual REST metadata; that is not own final review CI.

## 3. R1-01 — the53 and3 results have no intersection

The original recovery has **two different procedures**:

1. Sliding8B bases in`0x10B1000..0x10B1500`, requiring +0x10/+0x18/+0x70 relative addends
   all in **`0x6D0000..0x6D9000`** → **53** candidates.
2. Separate known-vptr check, requiring reserve **`0x571B3C`** and notify **`0x571A80`**
   at +0x10/+0x18 (outside that code band) → **3** matching vtables.

Own computation on both retained and fresh RELA maps yields:

| vptr | +0x10 | +0x18 | +0x70 | in naive53? |
|---|---|---|---|---|
|`0x10B1150`|`0x571B3C`|`0x571A80`|`0x6D5134`|**No**|
|`0x10B1240`|`0x571B3C`|`0x571A80`|`0x6D6C88`|**No**|
|`0x10B1330`|`0x571B3C`|`0x571A80`|`0x6D5134`|**No**|

**Intersection=0**; selected10B1150 is not one of53. Thus the original phrase
“53→3 narrowing” is misleading, even though the selected-vptr conclusion can stand on
other evidence. Progress review **6423751973** reported this directly. Producer
**6423891421** accepted it and corrected report123 inea6a3835 without changing scientific
artifact/raw. Correction verified in the pinned corrected text. This review does not
retroactively relabel the original predicate or force the sets to agree.

### Constructor/factory and direct-caller proof still holds

Own ADRP/ADD/store arithmetic on original constructor bytes:

- PC`0x6D28B4`: ADRP`0x10B1000`; PC`0x6D28C0`: ADD`0x150`.
- PC`0x6D28E0`, bytes **`690200f9`**: store value **`0x10B1150`** to`[x19+0]`.
- Factory`0x6D26D4` has direct BL to constructor`0x6D2894` at`0x6D270C`.
- Graph-builder direct BLs to`0x6D2950` occur at **7142452/7142468**
  (`0x6CFC34/0x6CFC44`), words`0x94000B47/0x94000B43`.

This is original static linkage, not execution of the graph-builder with serialized
controller/bootstrap state. That remains open.

## 4. Own native fixture replay — no producer verifier imports

An own Unicorn harness loads checked retained original windows/cells/relocations from
123 and explicit121/122/120/119 dependencies. Overlapping byte/RELA disagreements raise.
Every native instruction and static-data read must be covered; zero-mapped pages do
not authorize unknown code/metadata. Native writes must remain in declared prepared
state. Explicit sinks are allocator`0x3C986C`, import-bound memset, fatal stack-canary
failure; they are not mistaken for executed original service/heap implementations.

Shared fixture inputs are declared, not inferred game state: manager/list owner,
service global`0x116CB40`, pool queue/chunks/slots, vector capacity2×count, TLS/canary,
node storage/prefill and stack. The own code uses the same Unicorn backend but imports
**none** of producer vtable123/graph122/Fixture code.

| loop count /node prefill | own original instruction count | peer count | result |
|---|---:|---:|---|
|0 /0xA5|34|34|exact|
|1 /0xA5|457|457|exact|
|3 /0xA5|1281|1281|exact|
|3 /0x00|1281|1281|exact|

Own unique-PC sets and every peer-reported PC multiplicity match. Exact hooks confirm
per nonzero loop: reserve once globally, register+notify once/item,57095c and6d6c88
once/item, **570a70 twice/item**. Original PLT memset has one declared zero-fill service
call ofcount×16B when count>0; failure/resize/cleanup branches are not reached under the
prepared bounded capacities. Four standalone cases create **7** nodes total; do not add
nested120/121/122 instruction totals again.

### Write values and zero-loop exception

Own hooks record actual byte values, not just addresses:

1. PC`0x6D6C9C` writes **1** to manager+0x100.
2. PC`0x6D81C4` writes **0** to manager+0x100.
3. PC`0x6D81C8` writes **0** to node+0x100.

One loop gives3 writes; three loops9. **Zero loops gives0 writes and manager+0x100
remains0xA5**, matching producer artifact/code. Review records this explicitly rather
than generalizing “manager ends zero” to all four cases.

The ten source-parent calls' **930 DWORDs** are independently compared against the
pinned118 output artifact and all match/completion1. **This is a shared-lineage bit
comparison only**: parent119/source clip is not freshly parsed or re-executed by this
review. Graph-builder/controller/bootstrap, original allocator/heap, actual game
manager, active pose/apply/readback/render are not accepted by this fixture replay.

## 5. R1-02 — exact marker → token → metadata literal chain

The static identity **`Stop` is confirmed**, with an encoding precision correction:

1. Original libil2cpp RELA at file offset **3563112**, bytes
   `48fbad02000000000304000000000000b85cbe0200000000` → address **44956488**
   (`0x2ADFB48`), type **1027** (`R_AARCH64_RELATIVE`), symbol0, addend **46030008**
   (`0x2BE5CB8`).
2. Original file offset **45980856** at that addend contains **`a73c00a000000000`**,
   i.e. encoded usage **`0xA0003CA7`**, **not** UTF-8`Stop`.
3. For metadata version31: kind=`encoded>>29`=**5**; lowbit=1; index=
   `(encoded & 0x1FFFFFFF)>>1`=**7763**.
4. Original metadata literal table offset256, definition file offset **62360**:
   `040000009b3a0300` → length4/data-relative offset211611.
5. Metadata literal-data offset120712 +211611 = **332323**; actual payload
   **`53746f70` → UTF-8 `Stop`**.

The legacy288733-entry libil2cpp relocation projection independently recounts the exact
slot→addend mapping; three retained cell receipts contain the exact same RELA bytes.
They share extractor/build lineage, **not three clean-room parsers**. The15054-row
managed string index independently matches address`0x2BE5CB8`→`Stop`; fresh original
metadata has120456/8=**15057 literal definitions**, so export-row count is not asserted
as the complete metadata table count.

Producer accepted the precision issue in6423891421 and corrected report123 inea6a3835.
Original static literal identity stands. **A metadata usage/string identity is not a
method pointer, delegate/registration proof, delivered event, callback invocation or
runtime readback.** The152 selected libunity relocations are a separate library/window;
0 marker matches there is not a whole-lib-il2cpp negative assertion.

## 6. Bounds, provenance and reviewer scope

Fresh FDE exclusive ends include ctor`6D2894→6D28FC` (RET6D28F8), factory
`6D26D4→6D2744` (RET6D2740), populator`6D2950→6D29E4` (RET6D29E0), notify
`571A80→571AAC` (RET571AA8), register`6D5134→6D51A4` (RET6D51A0). Several original prose
ranges use final RET as the endpoint. Review keeps exclusive bounds explicit rather
than introducing a four-byte coverage error.

Original ZIP parts stream to scratch; libraries mmap read-only, metadata is a bounded
original file, output only selected spans/summary. Native replay uses sparse original
bytes +small declared state. No decoded bundle/Graph/Sprite fixture, managed SDK,
budget escalation, APK modification, original code execution on Android, device,
credential, preview/render/screenshot gate, or peer modifications. No source-CI/full
suite peak-memory claim. Instruction counts are **fixture instruction counts**, not
performance measurements or game frames.

Spec100/101 (`6424044328`/`6424230973`) additionally requests ef124 review as the next
R1 addendum. This119 deliverable closes only the pinned123 review slice;124 is explicitly
accepted as follow-on work, not silently reviewed here.

This review approves **bounded123**, including the now-corrected descriptions and
explicit source/fixture limits. It does **not** review124, decide #27-full closure,
replace independent122review, or manufacture missing actual game state.

## 7. Verification / formal review handoff

- Source checkpoint: **10focusedPASS/0.137s;1542fullPASS/374.083s**, not final review CI.
- New R1 regression checks: **20PASS/3.413s** before final combined/full run.
- Final combined focused: **181 PASS /70.546s** (closed#4–8/118/support +20R1checks).
- Final full discovery: **1552 PASS /375.323s**, complete log ends `OK`.
- Same-report live needles: **APKD1 124/107; AI1 (139,142136,142,138,42,82); RD1 41/0**; README refresh/check **0 drift**.
- **Scoped historical-support209/0/2**, current unscoped **163/25/23(exit1)** with no new FAIL IDs versus frozen160/27/24; exact results retained separately.

`verification-119.json.gz` plus four complete logs preserve the original160/27/24
baseline and approved historical-support209/0/2 separately from current unscoped
results. This support view is **not** all-current-ef/native/scientific/runtime acceptance.
Local counts are not CI counts. Own exact-head Verify/scoped/PR15 must actually be GREEN
before formal `review:` handoff on PR12; device/session gate skip is not runtime proof.

Closed#4–#8/118 code/reports/artifacts/receipts and protected3 remain byte-unchanged;
SCI118 was re-fetched from actual completed exact-source run/jobs and frozen as history.
No reset/rebase/whole-peer-tree import/main/spec/peer push/merge/skip-ci/self-ACK.
Only shared deltas: same-report three live needles/import hashes and own review119
scoped gate/tests. Original peer correction belongs to ef, not a cross-edit here.

```sh
python3 -m tools.verify.l3_geometry_8141386a_review_ef123 --check
python3 -m unittest tests.test_geometry_8141386a_review_ef123_sources tests.test_geometry_8141386a_review_ef123 -v
python3 -m tools.verify.geometry_8141386a_history
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
```
