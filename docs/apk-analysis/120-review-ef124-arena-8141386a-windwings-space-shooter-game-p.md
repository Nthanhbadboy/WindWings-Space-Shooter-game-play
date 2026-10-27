# 120 — R1 addendum: độc lập kiểm tra ef124, không đóng #27-full

provenance: **`arena/8141386a-windwings-space-shooter-game-p`**

**Verdict: APPROVE BOUNDED ef124 — static mappings + sáu prepared-state native fixtures.** Không tìm thấy mâu thuẫn số mới trong phạm vi này. Đây là addendum **riêng**, không sửa/nâng scope report119 (ef123), không tự ACK, không review hành vi ef126 mới hơn. #27-full/bootstrap/runtime vẫn ngoài phạm vi. Đồng thời §6 công bố **đính chính lời văn D1/D2/D3 của producer118 theo R2-125**, không sửa bằng chứng118 đã chốt.

## 1. Target cố định, nguồn và mức độc lập

- Assignment spec `6424044328` / `6424230973` / `6424898611`; CLAIM `6424965656`, progress `6425064744`. R1-119 đã HANDOFF `6424767705`, spec ACK `6424898611`; không gộp124 vào119.
- Peer scientific commit **`98e5ba9666103ca354ce3fd6116ca295b497c30d`**; report/receipts **`ea6a3835f786306b07df9658262a6e3f6658f809`**, HANDOFF `6423892211`.
- Read-only selected snapshots + manifest tại `reverse-engineering/raw/geometry-8141386a/review-ef124/peer-pins.json`. Raw30708B SHA **`27645c8c3586d85a8e5bc93ea008577d2c57641bd93257ee676faa327bc5901a`**; peer artifact7107B SHA **`b5a9023bab54691e920afc71b8d483f2f3dc07732e0bea662ecb85bfe72f36ca`**. Không import/execute producer124 verifier hay `Fixture`, không sửa peer tree.
- **Fresh original static witness:** own recovery [40386262470](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/actions/runs/40386262470), actual REST run/jobs `completed/success`, source **`c0e25f963111136e1ff3ebe581b27b85a9b4e44f`**, bot **`457782c8701f85ba5dc9a6cbc7e249a9346098ef`**. Witness `fresh-original.json.gz` **13690B**, SHA **`8eaaff8d08f3f83f6418fb7d3daed8739ad331ec6a9b3af8d20d700d6848e4c0`**. REST receipt `source-ci-receipt.json.gz` also records actual peer Verify40374283338 SUCCESS at the fixed scientific commit. Đây không phải CI acceptance của own final120, không suy ra CI test count/RSS.
- Authority: original XAPK SHA `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; libunity SHA `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`. Read-only streamed ZIP + mmap, không SDK/Graph/full asset fixture/APK mod.

Fresh query dùng **frozen own119 ELF reader**, không producer extraction tool: đối chiếu **149 unique spans = 135 windows + 14 cells**, **132 original FDE/table records**, **64 relative slots của 4 vtable groups** trong29267 original relative relocations, và7 BL instructions. Raw có136 window entries (một duplicate) và132 followed entries; không gọi136 là136 unique windows. Không có global factory-use/absence census trong query này.

Own integer branch/ADRP/ADD/STR/FDE arithmetic và **separate own guarded Unicorn2.1.4 harness** đối chiếu byte-backed assertions. Harness reuse **frozen own119 sparse byte/RELA/import loader**, merge124 có conflict guards; cùng original build/raw/emulator và **cùng contract synthetic state** với producer. Đây không phải clean-room ABI, independent game-state/serialized owner discovery hay thiết bị thứ hai.

## 2. Factory/FDE/RET/constructor/vptr mappings

Tất cả địa chỉ/offset bảng dưới là hex; **FDE end exclusive**, RET là địa chỉ instruction cuối.

|Factory|FDE end exclusive|RET|Constructor|Constructor FDE end exclusive|Installed primary vptr|Allocator size|
|---|---|---|---|---|---|---|
|`6d25f4`|`6d2664`|`6d2660`|`6d6a1c`|`6d6aa0`|`10b1440`|`X2+178`|
|`6d2664`|`6d26d4`|`6d26d0`|`6d850c`|`6d8530`|`10b1730`|`X2+170`|
|`6d26d4`|`6d2744`|`6d2740`|`6d2894`|`6d28fc`|`10b1150`|`X2+180`|
|`6d2744`|`6d27b4`|`6d27b0`|`6d81f8`|`6d8254`|`10b1640`|`X2+120`|

Own checker decodes `ADRP+ADD+STR[x19]` primary-vptr stores at **6d6a68 / 6d8520 / 6d28e0 / 6d8244**, checks factory allocator/constructor/handle BLs, allocator `ADD X0,X2,#offset`, exact `RET` bytes and original FDE initial-location/size arithmetic. Each vptr group has16 non-null 8B `R_AARCH64_RELATIVE` records (type1027, symbol0); all64 raw RELA bytes/addends match original and producer. **No semantic class/node names inferred from these addresses.**

Captured graph-builder **6cf7b4..6cff44 end-exclusive** contains7 direct BLs to the four factories:

|Factory|BL PCs|Count|
|---|---|---|
|A `6d25f4`|`6cf86c`|1|
|B `6d2664`|`6cfae4`|1|
|C `6d26d4`|`6cfb44`, `6cfb60`|2|
|D `6d2744`|`6cfb7c`, `6cfc54`, `6cfc98`|3|

These are **static call sites**, not observed invocations. Own review does **not execute graph-builder6cf7b4**, reconstruct its serialized state, or prove which node the game actually selected.

## 3. Own six guarded factory replays

New own module `tools/verify/l3_geometry_8141386a_review_ef124_native.py` executes captured factory/constructor/base/pool/list bytes; instruction/data-read coverage must be retained or explicitly prepared, native writes must stay in declared state. Uncaptured PCs/data reads, unexpected memset/stack failure, wrong return/canary/stack or allocator request fail closed. Own builder compares **instruction counts, exact executed-address sets, selected-PC multiplicities, common/specific node fields, owner/pool effects and allocator arguments** against pinned124 artifact.

|Case|Prepared variation|Own native instruction count|Matches peer|
|---|---|---:|---|
|A|prefillA5, label94, extra0, tag0, base3000000|181|yes|
|B|same defaults|200|yes|
|C|same defaults|196|yes|
|D|same defaults|171|yes|
|A variant|prefill0, label7, extra40hex, tag41decimal|181|yes|
|D variant|base4000000, other defaults|171|yes|

**Boundary:** original allocator entry3c986c is an **explicit asserted sink**, returns prepared node storage; original heap/allocator not run. Its exact arguments are `[extra+offset,16,94,0,0x12da21,0xab]`; original byte at12da21 is zero (empty C-string), not adjacent Camera text. Incoming W1 label goes to node+18, not allocator label pointer. A-extra40 asks for440decimal/1b8hex bytes, node label7; tag41→42. TLS/canary, service116cb40→queue→chunk→slots, owner/list and node are **synthetic**, not recovered live game objects.

`57054c` and `572a38` execute; cleanup570ff0 is **naturally skipped** because node+38 bit0=1 and node+a8=0, not forced PC bypass. Native owner+34=42 (prepared41+1), owner+48=node+8, owner+ac=C8; pool head0, tag+1, acquired1, chunk length1, slot0=0. Common node+18=label, +20=owner, +30=chunk match. Constructor-specific fields: A +118=4b / byte+170=1; B byte+16c=0; C floatbits+16c=3f800000 / qword+178=0; D dword+118=0. Zero is an executed store, not assumed zero-prefill.

Instruction counts exclude allocator-sink hook, stop sentinel, and unexecuted PLT/sinks/cleanup/growth paths. Original memset109ace0/stack-check109acc0 imports are explicitly bound but **neither reached**; growth573a1c/575b34 absent. These are six **whole standalone factory paths**, not additive to119/123 populator counts, not all input/lifecycle coverage.

## 4. Shared source1609 integration: checked equality, not independent extraction

Producer124 records one factory-C node followed by **harness bindings at node+118/+128/+130/+1d0**, then10 parent-chain calls. Own addendum compares their **930 output DWORDs** against the pinned shared118 source artifact and checks completion byte1; all equal. The pointer/control/clip bindings are explicitly supplied harness state, not recovered writers or graph-builder bootstrap.

**Own120 does not re-execute these10 parent calls**, freshly extract source1609, independently recover animation data, or upgrade shared115–123 lineage to runtime/Animator playback. This is a pinned composition/regression check only. Own standalone-C replay validates the factory path separately; the source-case relocation/bindings remain the producer's declared fixture contract.

## 5. Review result and exact remaining missing-X

Supported within fixed scope: four factory/constructor/FDE/RET/vptr/allocator mappings; seven graph BLs1/1/2/3; four RELA groups/64 slots total; six counts181/200/196/171/181/171 and prepared-state effects; natural cleanup skip; explicit synthetic allocator/PLT/TLS/pool/owner boundary; **no new numeric contradiction**.

Still **outside acceptance**: original serialized-controller bootstrap/graph-builder execution; original allocator/heap/service construction; original clip/clock/control writers; previous/active pose conversion/blend/normalize/apply; Android/Unity/game readback/render. Required next evidence is captured original caller/dispatch bytes plus exact prepared-state/prerequisite proof (or bounded missing-X), independently reviewed—not a screenshot or inference from static calls. ef owns newer native work; a5 owns serialized owner/N1, AI-4 owns economy/save. No takeover, #27-full closure or self-ACK here.

## 6. Additive producer118 wording clarification (R2 D1/D2/D3)

R2-125 comment **6424830494**, accepted by spec103, found no numeric contradiction and SUPPORTS118. These are **producer-side wording clarifications**, not data corrections. Frozen118 report/artifact/code/receipts remain byte-identical at scientific **e3fbb4dbc679c5d07ff8c520f8e13827baeae53c**; artifact728633B SHA **`c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d`**. The additive machine-readable note is `reverse-engineering/raw/geometry-8141386a/review-ef124/producer-118-precision.json`, embedded in120artifact.

- **D1 — scope of new witness:** branch-owned/non-peer-reexport applies to **252 fresh original native-renderer witness shards**, not every input to the reverse artifact. Of1587 pinned inputs, measured inherited groups include **901 raw/l3-chain, 411 raw/l3-visual-surface, 7 raw/sprite-geometry, 10 tools**; these retain their disclosed shared/raw98/raw102/source/tool lineage.
- **D2 — class/schema evidence:** original collector `tools/recovery/geometry_8141386a_consumers_bytes.py::gameobject` checks target metadata **class1** and supplied-schema inverse equality. Sparse native-renderer rows **do not repeat per-row class_id/type-table bytes**. Supplied-schema/inverse proof and the original-source CI/tool contract are checkable; sparse rows alone do **not independently rediscover every GameObject class**. Do not overstate R2 corroboration as independent schema discovery.
- **D3 — no reference is not no related record:** **115 of288** `NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED` rows still have **atlas memberships**. Membership deliberately is **not usage**. The negative label means no native-renderer/captured-component/animation-mapping reference in queried slices—not global unused, no atlas membership, or absence of every related record. Own builder remeasures115/288 from frozen118artifact.

No change to118 measured62815 renderers /61864 non-null /951 null, Sprite union1897/2185, or288 scoped-negative rows. Original #4–8/118/119 evidence is not regenerated/rebased; historical receipts are checked against **actual pinned scientific Git blobs** while only live needles/workflow are updated for120.

## 7. Artifact, verification and handoff boundary

Own artifact: `datas/l3_geometry_review_ef124_8141386a.json.gz` **10793B**, SHA **`9f6056cc586e89af10d817c303a967075e523927b3ccd8e47cff9efc943cfd24`**. It pins selected peer snapshots, source-CI/fresh-original bytes, own tools, reused frozen119 checks/loader, source118 comparison and additive notes. Builder is deterministic and rejects altered span hashes/FDE extents/RELA type/BL PCs/allocator request.

```sh
python3 -m tools.verify.l3_geometry_8141386a_review_ef124 --check
python3 -m unittest tests.test_geometry_8141386a_review_ef124_sources tests.test_geometry_8141386a_review_ef124 -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 120 --check
```

**Final local: full1572 PASS /362.268s; focused201 PASS /72.453s; new20 PASS /1.299s; deterministic artifact check PASS.** Complete logs/verification120 receipt are separate from frozen119. Live needles **APKD1(125,107), AI1(139,142136,142,138,42,83), RD1(41,0)** and README0drift. **Approved historical-support209/0/2; current-unscoped163/25/23, no newFAIL; frozen baseline160/27/24** remain distinct—the historical-support gate is not all-current/native/runtime acceptance. Final exact-head Verify/scoped/PR15 REST checks and formal PR12 `review:` HANDOFF follow only after actual push and GREEN, not inferred from source recovery or this verdict. Protected3 unchanged, SDK600MiB supervision unchanged, no runtime device lane reopened.
