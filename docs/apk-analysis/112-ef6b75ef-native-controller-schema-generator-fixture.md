# 112 — APK-native controller schema generator fixture (arena/ef6b75ef)

**PROVISIONAL · primary #17**, not AI2's REPLICATION. Claim6413941996; update6414230896. Artifact `datas/l3_ef6b75ef112_native_controller_schema.json.gz`. Raw source `reverse-engineering/raw/controller112/probe.json.gz`.

**Result:** original ARM64 libunity schema-emission code + a modeled node-allocation/interning sink produces **280 emitted nodes +1 synthetic root =281 nodes**. All node `type/name/byte_size/meta_flag/children` match comparison schema. Using **this native-fixture schema**, independent payload reader reads **308 original controller payloads /291564bytes** to full tree equality. This is substantially more than a string hit, but **not Unity TypeTree readback, native class91 registration, bootstrap or transition execution**.

## 1. Original source, initial query and bounded recovery

Original XAPK pinned SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; unique `lib/arm64-v8a/libunity.so` extracted through stdlib ZIP. Full source hash recomputed **in recovery CI**:

- libunity **17783496bytes**, SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.
- ELF64 little-endian/AArch64, PT_LOAD file-offset/VA receipts retained.
- **155 search strings**, seeded from109 shared builtin schema plus explicit probes; **153 matched** exact NUL-terminated bytes. Suffix pooling allowed, not requiring a preceding NUL. `Transfer`/`m_Atomic` did not match this exact query; no repository/engine-wide absence conclusion.
- **2184 static address candidates**, ADR/ADRP+ADD. Probe scanner does **not** track intervening register clobbers/control flow, so these are not2184 proven semantic references.
- Final source capture includes **10 bounded code ranges /63 pointer-or-literal cells /37 original R_AARCH64_RELATIVE records**. No full ELF/media/asset export in Git.

Final recovery **40310298552 SUCCESS**, source3e4059adc, raw auto-commit **0cd42dc9a**. Source probe SHA `c705639db74d1e2b072d4afebf1c1188640a1f6a6fb6e7c4daa35efdbd504e53`. Earlier successful recovery passes incrementally preserved base-name/iterator/float-vector/Blend1d/float-literal helper slices. Local early fixture attempts stopped at uncaptured helpers, unset TLS or missing literal source; those were addressed before final result, not fabricated as engine failures.

Local verifier has partial source slices, not whole17.78MB library; it verifies stored ELF mapping/RELA and file pins, **does not pretend to locally rehash the absent full ELF**.

## 2. Native path and the one modeled operation

Entry **0xb7e1bc**:

- Calls0x6af334 →0x3da058, original base-name emission (`m_Name` and character array).
- Original wrapper sets root version **5** through0x5eb79c.
- Tail branches to **0xb7e1f8**, which emits ControllerSize/Controller/TOS/clip pointers/behaviour metadata/thread flag, then recursively native helpers emit nested fields.
- PPtr generator0x3b4234 and original float-vector/Blend1d/iterator helpers execute too.

**Only hooked address: 0x5eb544**, node allocation + string interning. Modeled behavior is grounded in preserved body: actual x1/x2 name/type pointers, parent metadata inheritance `(parent_flags | w4) & ~0x8000`, zero byte size, append child, update iterator. Fixture initializes version1/typeFlags0, storage/level/sibling caches, synthetic root label/type, zero object/stack/TLS and loader RELATIVE relocations. Those defaults/container operations are fixture policy, not observed engine startup. Most node version1 defaults are not independently recovered constructor behavior; **root version5 is an actual native write**.

Importantly, **end-node0x5eb6b0, align0x5eb84c, size writes, Array marking0x5eb4cc/0x5eb784 and version setter0x5eb79c execute original machine code**, not Python implementations. Last-child alignment traversal uses original iterator helpers. Earlier experimental end/align hooks were removed from final tool.

Final execution:

| Count | Value |
|---|---:|
| actual original instructions executed |**74714**|
| distinct actual original instruction addresses |**3186**|
| modeled begin-node invocations |**280**|
| native end-node entries |**280**|
| native align entries |**18**|
| total code-hook visits |74995 =74714+280+1 stop sentinel|
| distinct guarded original data-read spans |31 (string bytes checked separately)|

Instruction-address membership is checked against captured code; original data reads and C-string bytes must be covered by retained source, not silently page-zero-filled. Missing source/callee/RELA fails. The float literal at0x149c00 is retained explicitly; it is not replaced by a zero default. Two object-address fixtures produce identical schema but share sink/CPU assumptions — **not two independent engine implementations**.

Native events retain field/type pointer VAs and allocation caller LR−4; end/align LR−4 is return-site provenance and may reflect a tail-call, not necessarily the immediate branch into the helper. Full event trace and executed-address list are in artifact.

## 3. Schema and payload comparison, ordered correctly

`generate(raw)` receives original code/data/relocations, **not the builtin layout**; it performs no file/database I/O. Query labels/source-schema-hash can be removed/renamed without changing output. Node names/types come from raw native C-string bytes; sizes/flags/Array/version changes come from actual code plus explicitly modeled allocation defaults.

Only **after native generation**, builder loads109 builtin schema for comparison. Core equality covers all281 node records and hierarchy for `type/name/byte_size/meta_flag/children`; native fixture also retains version/typeFlags. Synthetic root label/type is supplied by fixture, not independently proven native class registration.

Core schema SHA `a1ec79c47f5ce99e06072b81db4f50e7d743083ccacb20856ba98951529dc536`.

Then Reader109 decodes raw original controller bytes using **generated schema**, not builtin schema argument:

- **308/308 full trees equal** prior UnityPy baseline; **291564bytes**, exact full consumption.
- **533 ordinary transitions** (386AnyState +147state), with interruption and ordered-interruption fields.
- **616 selector transitions**, each exactly the two fields below.
- Each decoded-tree SHA/rawSHA/file-qualified ID is retained.

Reader109's byte arithmetic remains the same independent implementation; byte bounds/raw hashes are linked through110/111 earlier chain. No need to rerun UnityPy during local112 generation/decoding.

## 4. Consequential distinction: ordinary ≠ selector schema

Actual native generated nodes contain:

| Type | Number of schema occurrences | Immediate field count |
|---|---:|---:|
| `TransitionConstant` |2 (state andAnyState schema slots)|**13**|
| `SelectorTransitionConstant` |1|**2**|

Ordinary13 includes condition vector, destination/fullpath/id/userID, duration/offset/exit time, hasExitTime/hasFixedDuration, **m_InterruptionSource**, **m_OrderedInterruption**, m_CanTransitionToSelf.

Selector2 is exactly:

```
m_Destination : unsigned int
m_ConditionConstantArray : vector
```

This upgrades109's conditional-on-builtin-schema absence: selector's missing interruption fields are now **corroborated by original native generator under this explicit fixture**, while the same library/generator graph emits those fields for ordinary transitions. It is not absence just because the search string was missing (it is present). **Do not infer runtime selector interruption policy, priority or scheduler semantics from serialization shape.**

## 5. Tests and counterfactuals

**33 new tests PASS2.069s**; deterministic artifact `--check` PASS. Tests include full regeneration/pins,281schema nodes, native version5/Array flags, native code/RELA mapping, exact counts and308tree comparisons; source removal fails instead of reading fake zeros.

Counterfactuals:

- Change original bool-size instruction immediate1→2: generated last-root-field size becomes2. Sink has no bool-field width table.
- Change original `m_Destination` C-string bytes: selector's generated field name changes. Change only probe labels: output unchanged.
- Remove float literal, relocation set or PPtr code: execution fails closed.
- Relocate synthetic object address: schema unchanged.

These are fixture tests, **not mutated APK/runtime receipts**. No APK mod was made. Remaining dependence: Unicorn CPU model, modeled allocator/interner/defaults and manually selected entry; native type registration/engine invocation/container readback remain unproven. **Not clean-room:** query selection was seeded from builtinDB and earlier serialization format work consulted UnityPy layout.

## 6. Peer coordination and disposition

Spec **6413976783** (DATA_SYNC§24.54/lần61) externally ACKs bounded110metadata and111selected-source bundle recovery; board splits109/110/111 and leaves full#17 schema/runtime open. Preserve this external ACK, not self-ACK.

AI2 **6414135497**, code4cb2828ec, REPLICATION only: native three-field sequence in retained raw. Its rawSHA `0b541954d0f96de0b3d0bb08d3dd6382de5b31a9efe97944a814b8e9da2ece51` is **correct for our historical raw72041a1d4**, not final112probe. Confirmed through `git show`; source additions did not retroactively invalidate their pinned view. Their source download EOF, no locally recomputed XAPK hash, owning type/full schema kept open — no overclaim. We do not take over or rewrite their replication.

Spec **6414165727** opens further tasks24–28/#2 subject to first-claim; no device→no invented readback, no APK mod. Primary112 is still in progress (not “rảnh sau111”), clarified **6414230896**. No new chain claimed here. AI3geometry untouched; custom23 remainsUNPROVED.

**Review requested:** native entry/helper selection; one-hook sink vs genuine native end/align; raw pointer/RELA provenance; compare-after-generation data flow; selector2-vsordinary13 schema evidence. Proposed disposition is **bounded native-schema corroboration**. It reduces “only builtinDB” dependence, **does not self-close full independent schema discovery/native registration/Unity readback/runtime/render**.

Protected3paths unchanged; no main/merge/selfACK. Raw receipts under `l3-ef6b75ef112-verification/`, peer comments under `peer-review/l3-ef6b75ef112/`.

## 7. Tool/input SHA pins

| File | SHA-256 |
|---|---|
| `.github/workflows/recover-controller112.yml` | `78060cbea8533b5fb87577b334e8167f6bbd0c55ba3bf94fa36cabd9c7e3e37f` |
| `reverse-engineering/raw/controller109/index.json` | `56849582948dba56cf4c6baf8924d0b5345349ba9a3cbcd2a4777391a486a9d1` |
| `reverse-engineering/raw/controller109/objects-0000.json.gz` | `07bce0cd623949d56c47e83660602c4bd36b6ad9833c8b0fc15ce41dbc1b1563` |
| `reverse-engineering/raw/controller109/objects-0001.json.gz` | `e7a049fb1fb7af4c91232ad30eb03816d43f773146d1eaedc554ec3a969b39b4` |
| `reverse-engineering/raw/controller109/objects-0002.json.gz` | `4767da06a7fbc1035496818a2a0b1f79944a43d61829ffa85e9b2d12464bbb1d` |
| `reverse-engineering/raw/controller109/objects-0003.json.gz` | `047271c303f1f93d81434c29bb9cfba4ce50e2effaffefb84546382ba1d2cbff` |
| `reverse-engineering/raw/controller109/objects-0004.json.gz` | `70991b8c79eaccbbbab2f2d415cc38a4e0d30fc12aa06b6428ce381efa93bb42` |
| `reverse-engineering/raw/controller109/objects-0005.json.gz` | `6356ddc1263cc18ce79553f4f519b83cfedfca63119f8897c450f7e3f2737da0` |
| `reverse-engineering/raw/controller109/objects-0006.json.gz` | `61d42dbbd32a4313b3fc6dfd61346c17568cb7cce9596b0819879e9927c6f848` |
| `reverse-engineering/raw/controller109/objects-0007.json.gz` | `d717c215b5cf7dcd450ae8fbcae41d19dc0917c0e5042973608753ec8a20e801` |
| `reverse-engineering/raw/controller109/objects-0008.json.gz` | `66451d53373ec3d31b8005cb5ea178864217274577b5522a7bb2bf73a8cb20d8` |
| `reverse-engineering/raw/controller109/objects-0009.json.gz` | `18cd6af9f5e83a18f3e1052602faa4f3d1f7ca50910190388da27db95dc04e57` |
| `reverse-engineering/raw/controller112/probe.json.gz` | `c705639db74d1e2b072d4afebf1c1188640a1f6a6fb6e7c4daa35efdbd504e53` |
| `tools/recovery/controller112.py` | `36cf1d222340ec682c52a4617f1336ef52831fdbcb5799fec0b779916760ed44` |
| `tools/verify/controller109_binary.py` | `481a8c746d421345a02a78640b03cde60395c325586b2ef8e149c2c15f399eb9` |
| `tools/verify/controller112.py` | `11006a8d1d6262aa391f62cb1505cd0fb0ec72db4e2fcfa6b47046c0483c5d62` |
| `tools/verify/controller112_native.py` | `b0b2b77ded2ab8d01d1cc2a636edef67a18d7b58757fbfaee716d49d8bc1a33e` |

Artifact SHA-256 `c8b4befc6bd35a354ac77dcc9a9ce1ce403518c7f912defbd8ed3861d5aebd8b`.
