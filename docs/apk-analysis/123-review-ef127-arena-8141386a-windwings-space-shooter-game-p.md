# 123 — R1 review127: original null-domain entry→RET, return-PC metadata finding

**Provenance:** `arena/8141386a-windwings-space-shooter-game-p`

**Verdict:** `SUPPORT_EF127_NULL_ENTRY_RET_ONLY_CALLEE_RET_METADATA_CORRECTION_PENDING_NOT_27_FULL`

CLAIM [6427652461](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6427652461); source progress6427854437; P1 finding/request [6427990146](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6427990146). After own126/report122 HANDOFF6427626453 / spec ACK1186427720195. This is a separate127 review, not a rewrite of126 or an independent128/129 native review.

## 1. Fixed target and current disposition

Producer127 HANDOFF6426133738; scientific **`6781d828f6e283d11e6508c051e3000df233714c`**, report/receipts **`f1d35dd7a69b355f6d824527b74bfc368781f3be`**. Original artifact2850B/SHA **`8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e`** and raw12454B/SHA **`43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`** are retained unchanged. The target is fixed127, not the latest ef tree.

**Supported:** the original uninterrupted null-domain entry→RET path, three canonical variants51/51/51, original canary comparison and cleanup with one explicit null-deallocator sink per case. **Not supported as written:** one callee-return metadata address. The return-PC drift is recorded explicitly rather than changing a failing expected word into a false RET. The33 published word witnesses and all six FDE end-exclusive extents agree with original bytes.

**P1:** `b98c98` has actual RET at **`0xb98d64`**, bytes **`c0035fd6`**. Fixed127 artifact `graph_builder.callees["0xb98c98"].ret` and report127/128 say **`0xb98d68`**, whose actual bytes **`d6071494`** decode to **BL `0x109acc0`**, not RET. Producer generator used `end-4` for all callees. Original end-exclusive **`0xb98d6c`** is correct. This is a metadata/description discrepancy; it does not alter the51-instruction null path, original FDE bytes, or original raw.

**Producer correction gate:** requested in6427990146. No producer correction is claimed verified by this preparation paragraph. An additive producer-owned correction must be pinned and checked separately; the original drift must remain visible, not silently rebased. Review-queue completion is not #27-full or implementation/runtime completion.

## 2. Own fresh original source and publication pins

Own recovery [40404773695](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/actions/runs/40404773695) is actual completedSUCCESS at **`6d7de553ae66a57dd8d880a536aa4dd6751bdb2d`**, raw-preservation **`3ab9b809c7272660ca71476c20022079b72d24f2`**, ff-only own remote. `tools/recovery/geometry_8141386a_review_ef127_bytes.py` uses streamed ZIP→scratch and read-only mmap with the frozen own119 ELF64 reader, not producer127 extraction code.

- Original XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; original arm64 libunity SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`. No APK/library modification.
- **104 unique selected spans /37 original FDE+table records /11 selected relative RELAs /56 original import symbol/name records** match fixed127. Two PLT entries109acc0/109ace0 are bounded windows without original FDEs, not two more complete functions. No new whole-executable branch census is claimed in this cycle.
- Fresh witness **16227B**, SHA **`74c1c83ff156605e5ee9b9f627122e5fe7a4853fdff6c99f81b55400b42bcda6`**, retained as `review-ef127/fresh-original.json.gz`; own collector/parser/input pins are embedded.
- Actual source run/jobs and exact producer scientific Verify40391943675 SUCCESS are retained in `source-ci-receipt.json.gz`; `ci_test_count:null`. Completion metadata supplies neither a CI test count nor peak RSS.
- No SDK/native execution during extraction, whole bundle/Graph/atlas decode or original assets retained; SDK supervision remains600MiB/no escalation.

`peer-pins.json` retains eight selected exact snapshots: six fixed127 raw/result/report/inert executable texts plus two full published context documents. All eight commit:path identities are checked against actual Git bytes. Context128 is report at **`34a97a99211de059e21cfcc08635791d1b94a5e0`**; context129 at **`2c710a7c20c123a65db45ddeca1f18c0807abe02`**. These two are **textual correction/context only**, not inspected128/129 raw artifacts, native verifiers, serialized records or new class/instance evidence. No whole-peer-tree import or peer edit.

## 3. Exact FDE/end/RET audit, including the failed published return label

| Callee | Original end exclusive | Published127 RET | Actual RET instruction | Disposition |
|---|---|---|---|---|
| `6ceeb0` | `6cef64` | `6cef60` | `6cef60` | MATCH |
| `b98c98` | `b98d6c` | `b98d68` | `b98d64` | CONFIRMED_RETURN_PC_METADATA_DRIFT |
| `b98db4` | `b98fc8` | `b98fc4` | `b98fc4` | MATCH |
| `b99120` | `b9944c` | `b99448` | `b99448` | MATCH |
| `6f15cc` | `6f16bc` | `6f16b8` | `6f16b8` | MATCH |
| `6cff44` | `6d006c` | `6d0068` | `6d0068` | MATCH |

Five callee-return labels match; the b98c98 row is **DRIFT**. It remains static-only here; its wrong return label cannot change a path that never calls it. Cleanup6ceeb0 **does** execute; the other five listed callees do not. Section3's blanket “captured, not executed here” heading in127 therefore needs this qualification. The captured deallocator body3c9438 is not executed: it is intercepted by the sole declared sink.

Graph-builder FDE is **`6cf7b4..6cff44`**,484 aligned words; actual selected-path RET is **`6cff3c`**, not end-4. The final word **`6cff40`** is the failure-path BL to109acc0. Cleanup FDE is **`6ceeb0..6cef64`**,45 words, RET6cef60. FDE/table bytes and initial-location/range arithmetic are checked from original ELF, not inferred from window sizes.

Own bounded integer decoder checks all **33 distinct published witness words and their operands/targets** (B/BL, CBZ, B.cond, BLR, RET, unsigned scalar loads/stores and register MOV subset). This is not a general ARM64 semantic analyzer. Eleven published required-field-role rows comprise **6 individual witness PCs and5 null/unasserted PCs**; word equality is not an assertion of complete ABI or role semantics for all11.

## 4. Separate native path: one original entry, no staged intervals

Own `l3_geometry_8141386a_review_ef127_native.py` reads only own fresh original spans, never imports/executes producer graph127/Fixture or merged producer loaders. Shared protocol:512-byte node prefilledA5/00; prepared null+118/+1a0/+1c0 and zero DWORD+1c8; TLS/stack; one explicit original-address3c9438 deallocator sink. Nonzero synthetic callee-saved X19–X29/D8/D9 sentinels add preservation checks, not real game-state evidence.

One `emu_start` at6cf7b4 per case. Original branches select cleanup and fallback. The **only host PC write** is the declared deallocator return to its original LR6cef48; there are no manual/staged native entry intervals. Every counted instruction must be captured original bytes in GB/cleanup FDEs. Reads/writes must be captured source or explicitly prepared node/TLS/stack. Mapped zero pages do not authorize missing code/data; the non-null build/failure/heap paths are rejected.

| Variant | Native instructions | GB unique words / FDE words | Cleanup unique words / FDE words | Null-deallocator sink | Last native PC |
|---|---:|---|---|---:|---|
| A5, base3000000 | 51 | 28/484 | 23/45 | 1 |6cff3c RET|
| 00, base3000000 | 51 | 28/484 | 23/45 | 1 |6cff3c RET|
| A5, base4000000 | 51 | 28/484 | 23/45 | 1 |6cff3c RET|

Canonical total **153 original instructions across three separate fixtures**, not additive to126 dispatch counts. Exact native PC sets/multiplicities, return0, SP restoration, service records and four original zero-domain node outputs match producer127. The native chronological edges are6cf7e4→6ceeb0;6ceec8→6ceee8;6ceef0→6cef30;6cef60→6cf7e8;6cf7ec→6cff0c. The original TLS/saved-canary loads and comparison run; a tampered-TLS regression probe naturally takes6cff40 and is rejected before PLT execution. This is a **whole-FDE selected entry→RET path**, not complete484-word body or build-path coverage.

At6cef44 the original BL passes object0, category from prepared DWORD+0xc8 (A5A5A5A5 or0), original empty-label VA12da21 and line0x24. The service records them and returns to LR; it does not execute the original heap/deallocator, infer allocator semantics or prove heap parity. No virtual, factory, non-null owner/motion object, memcpy/memset or binding/delivery builder is run.

## 5. Native stores vs untouched preparation — two P2 prose precisions

Only two native node stores occur: qword+1c0=0 at6cef48 and DWORD+1c8=0 at6cef4c. Both inputs were already0; this proves the original store instructions ran, not that a real heap allocation was freed. +118/+1a0 remain prepared null and are not cleared by this path.

**+128/+130/+138/+140/+180 remain A5A5A5A5A5A5A5A5 in A5/relocated cases**, and prepared0 in the zero-prefill case. No native store touches them. Therefore127 §4's “leaves empty” is at most “unavailable/unbuilt”, not literal native zeroing. Its “0x180-family” phrase is not another individually witnessed role in the11-row artifact. Likewise, only cleanup among the six-callee table runs; do not mark all six unexecuted. These precisions do not contradict51/51/51.

## 6. M1–M5 published supersession map, not fresh128/129 verification

`context-review.json` records five human prerequisite reconciliations plus two P2 precisions. The artifact retains **17 distinct exact quotes**, pinned commit/path/section/line/source SHA/quote SHA and complete source texts. Identity/locators/bookkeeping are machine-checked; the interpretation is a human review, not automatic semantic/native truth. M1–M5 is a high-level bounded map, **not proven sufficient/exhaustive ABI/build-path preconditions**.

| Label | Review disposition | Qualification |
|---|---|---|
| M1 | PUBLISHED_SUPERSESSION | 127's controller/clip and global-absence wording is historical. Published129 distinguishes owner producer/linkage M1a from runtime owner identity M1b: registry-by-instance-id is not a serialized N2 pointer or the126 synthetic owner model. This reviewer checks publication text/identity, not129's native registry/class evidence. No owner vtable/runtime instance is constructed here. [127-ef6b75ef-native-graph-builder-prelude.md:50–50](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L50-L50); [129-ef6b75ef-native-owner-linkage.md:95–95](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/2c710a7c20c123a65db45ddeca1f18c0807abe02/docs/apk-analysis/129-ef6b75ef-native-owner-linkage.md#L95-L95); [129-ef6b75ef-native-owner-linkage.md:97–97](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/2c710a7c20c123a65db45ddeca1f18c0807abe02/docs/apk-analysis/129-ef6b75ef-native-owner-linkage.md#L97-L97) |
| M2 | PUBLISHED_SUPERSESSION | Do not repeat127's no-pinned-serialized-data claim. Published128 says M2a serialized content AVAILABLE, M2b native runtime motion-set object MISSING, M2c producer MISSING; its controller1856 pptr mappings are empty. Published129 calls node+0x128 the runtime owner+0xa8 result. Serialized counts or a static producer edge do not instantiate that runtime object or justify executing non-null builders. None of128/129's raw/native/serialized audits is independently reproduced here. [127-ef6b75ef-native-graph-builder-prelude.md:30–30](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L30-L30); [128-ef6b75ef-native-motion-input-contract.md:37–39](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/34a97a99211de059e21cfcc08635791d1b94a5e0/docs/apk-analysis/128-ef6b75ef-native-motion-input-contract.md#L37-L39); [128-ef6b75ef-native-motion-input-contract.md:59–59](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/34a97a99211de059e21cfcc08635791d1b94a5e0/docs/apk-analysis/128-ef6b75ef-native-motion-input-contract.md#L59-L59); [129-ef6b75ef-native-owner-linkage.md:99–99](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/2c710a7c20c123a65db45ddeca1f18c0807abe02/docs/apk-analysis/129-ef6b75ef-native-owner-linkage.md#L99-L99) |
| M3 | RETAINED_BOUND_WITH_PUBLISHED_CONTEXT | The null-domain execution does not read owner/pool fields+0x20/+0x30 or bootstrap a real heap. Published128 leaves delivery-target identity open; published129 adds static node attachment context. Neither is an original pool/owner instance supplied to this harness. Controller/C/node labels must not convert the126 prepared protocol into ABI or game-instance identity. [127-ef6b75ef-native-graph-builder-prelude.md:52–52](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L52-L52); [128-ef6b75ef-native-motion-input-contract.md:31–31](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/34a97a99211de059e21cfcc08635791d1b94a5e0/docs/apk-analysis/128-ef6b75ef-native-motion-input-contract.md#L31-L31); [129-ef6b75ef-native-owner-linkage.md:38–38](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/2c710a7c20c123a65db45ddeca1f18c0807abe02/docs/apk-analysis/129-ef6b75ef-native-owner-linkage.md#L38-L38) |
| M4 | RETAINED_BOUND_WITH_PUBLISHED_CONTEXT | Original cleanup is checked only on null previous-list/array and zero count. Own native trace confirms the two zero stores, not any child construction or real deallocation. Runtime child/list creation is still outside this review; this is not an exhaustive precondition contract for all cleanup inputs. [127-ef6b75ef-native-graph-builder-prelude.md:53–53](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L53-L53); [127-ef6b75ef-native-graph-builder-prelude.md:7–7](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L7-L7) |
| M5 | RETAINED_BOUND_WITH_PUBLISHED_CONTEXT | 6f15cc and the non-null motion/binding builders remain unexecuted in this review. Published128 supplies a more precise contract but not a native runtime input object. Do not infer globally missing serialized content or sufficient native layout from127's M5 shorthand. [127-ef6b75ef-native-graph-builder-prelude.md:54–54](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/f1d35dd7a69b355f6d824527b74bfc368781f3be/docs/apk-analysis/127-ef6b75ef-native-graph-builder-prelude.md#L54-L54); [128-ef6b75ef-native-motion-input-contract.md:41–41](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/34a97a99211de059e21cfcc08635791d1b94a5e0/docs/apk-analysis/128-ef6b75ef-native-motion-input-contract.md#L41-L41) |

In particular: do not revive127's broad “no pinned serialized data” claim. **Published128** splits M2a serialized content AVAILABLE vs M2b runtime motion object/M2c producer MISSING; its pptr mappings for controller1856 are empty. **Published129** separates registry-by-runtime-instance-id M1a linkage from missing runtime owner identity/vtable M1b, and calls the motion object the owner+A8 result at node+128. These publications do not transform126's synthetic N2-owner protocol or fixture “controller/C” names into a real ABI, typed native owner or constructed controller1856. No128 serialized counts/native tables,129 class/registry, or130 update chain is independently reverified here.

## 7. Reproduction, preservation and pending final gates

Own artifact `datas/l3_geometry_review_ef127_8141386a.json.gz`: **12484B**, SHA **`c34f6cbcc4d0e4ebf37190547674b308e068bac3c7fad5319591d09ccfeca337`**. It retains original fixed-target return drift, fresh-source identity, three own traces,33-word decodes, field/coverage distinctions and published context receipts; no wrong BL is relabelled RET.

```sh
python3 -m tools.verify.l3_geometry_8141386a_review_ef127 --check --git
python3 -m unittest tests.test_geometry_8141386a_review_ef127_sources tests.test_geometry_8141386a_review_ef127 -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 123 --check
```

**Final local:** full **1655 PASS /389.073s**; focused **284 PASS /72.153s**; new **32 PASS /0.114s**; deterministic artifact and **8 actual selected Git identities PASS**. Live **APKD1(128,107), AI1(139,142136,142,138,42,86), RD1(41,0)**; README **0 drift**. Approved historical-support **209/0/2**, actual unscoped **163/25/23**, no new failure IDs, frozen baseline **160/27/24** remain separate. Complete verification123 logs/receipt are retained. **Test PASS means this review/checker works, NOT that the original producer RET label passes: one confirmed metadata DRIFT remains explicitly recorded.** Producer-owned correction and actual final exact-head Verify/scoped/PR15 remain separate outstanding gates; no full127/#27 closure or selfACK is inferred.

Frozen #4–8/118–122 reports/artifacts/source/harnesses/scientific receipts/logs remain immutable and checked against actual Git; actual122CI was frozen before any future needles. Approved historical-support209/0/2, actual unscoped diagnostics and frozen baseline160/27/24 remain distinct; no unrelated expected/test repair. Protected3 unchanged;600MiB unchanged; no original APK/assets, oversized file/commit, screenshot gate, runtime/device/secret reopening, peer edit, branch switch, main/merge/release or selfACK. **Review-queue completion is not #27-full/native/runtime/clone parity.**
