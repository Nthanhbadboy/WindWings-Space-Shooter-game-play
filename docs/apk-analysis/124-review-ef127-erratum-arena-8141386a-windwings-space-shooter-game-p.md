# 124 — additive R1 verification of producer ERRATUM-127

**Provenance:** `arena/8141386a-windwings-space-shooter-game-p`

**Bounded evidence verdict:** `APPROVE_BOUNDED_EF127_NULL_ENTRY_RET_AFTER_VERIFIED_PRODUCER_ERRATUM_NOT_27_FULL`

This is an additive verification of the correction requested in6427990146, not a rewrite of own conditional123 or producer127/128. Existing review127 CLAIM6427652461 and spec ACK1256436273516 authorize this continuation. The attempted separate follow-up CLAIM POST returned **HTTP403 “Resource not accessible by integration”**; no new CLAIM comment ID or successful public handoff is invented. Formal coordination remains a separate gate from this evidence verdict.

## 1. Actual producer publication and fixed source

Producer [ERRATUM6436088881](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6436088881) is now public. It explicitly supersedes `graph_builder.callees["0xb98c98"].ret` and the127/128 tables, while preserving the original raw, science,51-instruction cases and artifact. Full API comment is retained at `reverse-engineering/raw/geometry-8141386a/erratum-ef127/producer-erratum.json.gz`.

- Producer body SHA-256: **`47f6f5aeef46de2becefba3d8266630fba2a6208322c0cd7d40568be744d59f3`**.
- Producer tip at publication: **`5246e293c6375a3329244f1555e2d6d06d3c0303`**.
- Spec [ACK1256436273516](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6436273516) accepts the producer publication and requests independent verification, not automatic approval. Full snapshot retained; body SHA **`bc2f636b372db615ebae042dc6db6786a96b3e6d1381d753258cb01cfd097c99`**.

**Both actual API GET bodies were checked**, including ID, stable URL and complete body fingerprint. The snapshot checker is offline by default; optional `--api` rechecks current public bodies explicitly. Five selected files at the exact producer publication commit are retained with original path/blob/source SHA and wrapper SHA, not imported as executable peer tools. Nine actual Git identities (five publication files + four frozen own123 files) were checked. No latest-peer-tree or generator execution is substituted for the fixed evidence.

The old artifact still contains its incorrect label. That is intentional preservation, not a claim that the old JSON was repaired: **the published erratum supplies a separate effective label**. The original drift remains visible in own123.

## 2. Independent original-byte verification

Source authority remains the original official XAPK `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` / arm64 libunity `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.

This addendum uses **own previously captured original bytes**, not numbers copied from the erratum. Own fresh-source recovery40404773695 at6d7de553a, preserved at3ab9b809c, remains fixed: `review-ef127/fresh-original.json.gz` **16227B**, SHA **`74c1c83ff156605e5ee9b9f627122e5fe7a4853fdff6c99f81b55400b42bcda6`**. No new source capture or native case is claimed here.

The exact `b98c98` window is:
- VA **`0xb98c98`**, file offset **12143768**, **212B**, original SHA **`645cfe691307d391144b478d6cf4c1d44b9e041b51205714f14172cc64ac9c5d`**;
- end exclusive **`0xb98d6c`**, checked from original FDE/table arithmetic;
- byte-for-byte equal to the producer's pinned original window from raw127 SHA **`43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`**.

| PC | Original bytes | Independently checked effect |
|---|---|---|
| `b98d4c` | `e1000054` | `b.ne b98d68`: canary-failure branch goes to the BL |
| `b98d5c` | `fe1340f9` | `ldr x30,[sp,#0x20]` |
| `b98d60` | `ff430191` | `add sp,sp,#0x50` |
| **`b98d64`** | **`c0035fd6`** | **actual RET** |
| **`b98d68`** | **`d6071494`** | **BL `0x109acc0`, not RET** |

Own bounded integer decoding derives the conditional and BL signed targets. A bounded scan of the **53 original instruction words in this one window** finds one RET at `b98d64`. This is a verification of the published fact, **not** a general return-discovery heuristic or generator repair. No scan over unrelated functions is claimed.

Six other RET words named by the producer are also checked against own frozen bytes: `6cef60`, `6d0068`, `6f16b8`, `b98fc4`, `b99448`, `6cff3c` all equal `c0035fd6`. Precisely, this is **five other listed callees plus the graph-builder return**, not six additional direct callees. Together with the five tail/branch words above, **11 distinct original words** are verified.

## 3. What the correction resolves — and what it leaves unchanged

The specific P1 blocker was a return-label metadata error, not a contradiction of the51-instruction null path. Producer's actual public erratum now agrees with independent original bytes. Therefore the covered return-label blocker is resolved in **this additive review**; no wrong BL is relabelled as RET and no expected value is falsified.

| Evidence/view | Retained state |
|---|---|
| Producer127 artifact | **2850B**, SHA `8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e`; old `ret=b98d68` remains historical |
| Producer127 raw | **12454B**, SHA `43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1`; unchanged |
| Historical generator | `dict(ret=v-4,fde_end=v)` remains pinned/inert; no generator fix or regeneration |
| Own original123 science | commit **`a7f4e1f65dee7fa1464f2706eaab94075fba4733`**; artifact **12484B**, SHA `c34f6cbcc4d0e4ebf37190547674b308e068bac3c7fad5319591d09ccfeca337`; original conditional verdict and one DRIFT retained |
| Effective label after actual publication | `b98c98` RET **`b98d64`**, FDE end exclusive **`b98d6c`**; old `b98d68` is BL |
| New native execution/source capture in124 | **0 /0**; no new51-case replay asserted as new evidence |

Spec125 explicitly defers a generator heuristic change to a separate, later pinned cycle. This review does not implement that change, run producer `graph127`, or silently regenerate its inputs/artifact. The claim that133's artifact does not carry this label is producer context; this addendum does not independently review133.

## 4. Preserved qualifications and approval boundary

The earlier original-byte and separate-harness evidence remains bounded:
- Original three canonical null-domain executions **51/51/51** are inherited frozen results, not new124 execution. Whole-FDE selected entry→RET is **GB28/484 +cleanup23/45**, not all-word or build-path coverage.
- Cleanup6ceeb0 executes; five other listed callees do not. The only external service remains synthetic null-deallocator3c9438, not original heap execution.
- Native stores only+1c0/+1c8; +118/+1a0 remain preparednull. Other output fields remain A5/prepared0, not native clears. Eleven field-role rows retain6 individual witness PCs and5 unasserted PCs.
- Counts are not additive across reports. “controller/C/node” fixture labels do not identify a native ABI/class or controller1856 instance.
- Published128/129 M2a/M2b/M2c and M1a/M1b supersessions remain text-only context from123, not fresh native/serialized verification or sufficient runtime input objects here.

**APPROVE is for the bounded null-path evidence after verification of this particular published return-label correction.** It does not prove original deallocator/heap, non-null owner/motion object, full graph build, serialized live instance, scheduler/dispatch/playback/clock/pose/apply, Unity readback/render or runtime. A potential review-queue6/6 ACK belongs to spec after formal handoff; it is never #27-full/implementation/runtime acceptance or selfACK.

## 5. Artifact, tests and reproduction

Own additive artifact: `datas/l3_geometry_review_ef127_erratum_8141386a.json.gz`, **4975B**, SHA **`6f1b5e2e359b89677d7d31fadfc7b8e1bdc23377833fbf66dd17e163b722d9f8`**. It pins the actual publication snapshots, original-byte checks, preservation of old evidence and the initial403 coordination failure. The offline checks do not pretend that a CLAIM or HANDOFF POST succeeded.

```sh
python3 -m tools.verify.l3_geometry_8141386a_review_ef127_erratum --check --git
# Explicit current public API body read, not required for offline regeneration:
python3 -m tools.verify.l3_geometry_8141386a_review_ef127_erratum --check --api
python3 -m unittest tests.test_geometry_8141386a_review_ef127_erratum -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 124 --check
```

**Final local:** full **1677 PASS /384.432s**; focused **306 PASS /72.995s**; new **22 PASS /0.076s**. Deterministic artifact, **9 actual fixed Git identities** and **2 actual API publication bodies PASS**. Live **APKD1(129,107), AI1(139,142136,142,138,42,87), RD1(41,0)**; README **0 drift**. Approved historical-support **209/0/2**, actual unscoped **163/25/23**, no new failure IDs, frozen baseline **160/27/24** remain distinct. Verification124 retains complete full/focused/per-claim logs and exact historical-support snapshot/path set. Final exact-head CI and formal PR12 publication remain separate post-push gates; comment permission initially failed403. No queued→GREEN, local→CI testcount or publication-success inference.

Frozen #4–8/118–123 reports/artifacts/source/harnesses/scientific receipts/logs remain immutable and validated against actual Git. Original123 exact-head CI was preserved before any new live needles. Protected3 unchanged; SDK600MiB unchanged/no escalation; no APK/assets, whole Graph/bundle/atlas fixture, peer edit, lane takeover, screenshot/device/secret/runtime reopening, branch switch, main/merge/release or selfACK. Historical-support compatibility and all-current/native/runtime acceptance remain distinct.
