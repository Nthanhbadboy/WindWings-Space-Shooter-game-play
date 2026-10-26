# 124 — original specialized node factories and native constructor/vtable identities

**Provisional / arena/ef6b75ef / #27.** Claim **6423259070**. Scientific **98e5ba9666103ca354ce3fd6116ca295b497c30d**. Follows123handoff6422951255 and external ACK **6423047661** (bounded123 CLOSED; #27-full and independent122review still open). This advances the captured graph-builder one layer down: four specialized node factories, their native constructors and vtable RELA groups. It is static native analysis, **not** serialized controller bootstrap, observed game graph creation, original heap, Unity readback or render.

## 1. Graph-builder call sites and four original FDEs

Captured original graph-builder FDE **6cf7b4..6cff44** contains **7 direct BLs** to these factories inside its body:

| Factory | FDE | RET | Constructor | vptr installed | allocator size |
|---|---|---|---|---|---|
|`6d25f4`|`6d25f4..6d2664`|`6d2660`|`6d6a1c`|`10b1440`|`X2+178hex`|
|`6d2664`|`6d2664..6d26d4`|`6d26d0`|`6d850c`|`10b1730`|`X2+170hex`|
|`6d26d4`|`6d26d4..6d2744`|`6d2740`|`6d2894`|`10b1150`|`X2+180hex`|
|`6d2744`|`6d2744..6d27b4`|`6d27b0`|`6d81f8`|`10b1640`|`X2+120hex`|

Exact graph-builder call PCs are `6cf86c` (A), `6cfae4` (B), `6cfb44/6cfb60` (C), `6cfb7c/6cfc54/6cfc98` (D): counts **1/1/2/3**. The graph-builder body is captured but **not executed**; it still requires serialized controller state, virtual services and several external helpers. No semantic node/class names are invented from vtables or call sites.

Each factory has the same native skeleton: set allocator request `X0=X2+offset`, `X1=10hex`, `W2=5ehex(94)`, `W3=0`, `X4=12da21`, `W5=abhex`; `BL3c986c`; pass incoming W1 to its constructor; original cleanup test on node+38 bit0 / node+a8 halfword; `BL572a38`; return new node. Original bytes at **12da21 are one zero byte** — an empty C-string label, not the adjacent `UnityEngine.Camera::get_depth`.

## 2. Native constructors and vtable RELA groups

Original constructors install primary vptrs by literal `ADRP10b1000; ADD#offset; STR[x19]`:

- `6d6a1c`: vptr `10b1440` (`+440`), also sets node+118=4bhex, node+170=1, secondary vtables at+c0/+d0 and typed constants.
- `6d850c`: vptr `10b1730` (`+730`), clears byte+16c, calls base `6d28fc`.
- `6d2894`: vptr `10b1150` (`+150`), writes float1 (`3f800000`) at+16c, zero at+178, clears+110/+120/+148; this is the123 manager vtable.
- `6d81f8`: vptr `10b1640` (`+640`), clears node+118, sets+c0/+d0 secondary tables and+c8/+f8 type fields.

Four exact RELA-backed vtable groups are retained: `10b1150`, `10b1440`, `10b1640`, `10b1730`, each with16 8B slots. Their addends differ at destructor/virtual slots; no class names are assigned. Base constructors `6d6aa0/6d28fc/57054c` execute original stores and prepared pool acquisition. `570ff0` cleanup is naturally skipped because base constructor sets node+38 bit0=1 and node+a8=0; no forced PC bypass.

## 3. Explicit service boundary and native execution

For each selected factory call, the fixture supplies:

- **allocator sink** at original3c986c: asserts exact size `extra+factory_offset`, align16, category94, flag0, empty-string label12da21, auxABhex, then returns prepared0x400B node storage. Original allocator/heap is NOT executed.
- **PLT services**: original `memset` PLT109ace0 bound to exact ELF import and explicit zero-fill sink; original `__stack_chk_fail` PLT109acc0 bound to fatal sink. Neither is reached in these selected calls.
- **synthetic state**: TLS/canary, global116cb40→service, prepared queue→chunk→slots, owner/list object and node storage. Owner/list/pool/TLS are not observed game objects.

Everything else in the selected factory path is original ARM64: factory, constructor, base, pool getter/atomic pop, cleanup branch and handle/list insertion572a38. PC checks show the constructor, `57054c`, `572a38` and factory RET; `570ff0`, `3c986c`, `109acc0`, `109ace0`, growth helpers573a1c/575b34 are absent. Native owner+34 increments, owner+48 links new node+8 and owner+ac ORsC8hex. Pool queue head nulls, tag/counter increment and chunk length/slot0 become1/0.

Constructor-specific executed fields are checked: A node+118=4bhex and byte+170=1; B byte+16c=0; C float bits+16c=3f800000 and qword+178=0; D node+118=0. Common fields include node+18=incoming label, node+20=owner, node+30=acquired chunk, node+38 bit0=1, node+a8=0.

Six standalone factory calls execute **181/200/196/171/181/171 native instructions**: four default cases plus a zero-prefill/label7/extra40hex/tag41 variant of A and a relocated-base variant of D. These are whole factory traces including constructors/base/handle, not additive to123 graph-populator counts.

## 4. Source1609 integration

One factory-C (`6d26d4`, vptr10b1150) node is created by original native code, then explicitly bound to prepared source blob/cache/output/native clip via node+118/+128/+130/+1d0 and fixture clocks/flags. These are harness bindings, not recovered graph/clip/clock writers. Ten unchanged119parent calls on that node yield **930DWORDs bit-equal to pinned118artifact** and completion byte1. Shared115–123lineage means this is composition/regression, not fresh UnityFS extraction, live Animator playback or proof that game graph-builder selected this node.

## 5. Pins and raw

Recovery **40371804376SUCCESS**, source **f92c75fbaf3ef4f41d80886361890023964ff25a**, raw commit **0db96cba3**. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7. Cache fails on miss; no APK modification or whole-library snapshot.

| Input | SHA256 |
|---|---|
|raw/nodefactories124/probe.json.gz,30708B|`27645c8c3586d85a8e5bc93ea008577d2c57641bd93257ee676faa327bc5901a`|
|datas/l3_ef6b75ef124_native_specialized_node_factories.json.gz,7107B|`b5a9023bab54691e920afc71b8d483f2f3dc07732e0bea662ecb85bfe72f36ca`|
|tools/recovery/nodefactories124.py|`97652de3fc1d12fdc65cd7eb1f8ec90b9365efd15318575417fc4b69ca5a88d8`|
|tools/verify/nodefactories124.py|`f226bd35cf6ce144be7531be52117801fac127f037a4ff02d99c925b11bf2aa9`|
|tests/test_nodefactories124.py|`9c34ebf71ac1837bb5e15326171619d6502ce6f3974999047378342cacfe06a3`|
|tools/verify/vtable123.py|`d47d1f6a4135cb991ec0d3948ee55e4eebc6201dd2887631aa16dbb7c58eef78`|
|tools/verify/graph122.py|`acd741ba9cee69e86846e9b1b2bad3f6f40676918094be80e1e0d7c56530740d`|
|tools/verify/factory121.py|`a26715e77f82998f3f5180c95f63caa3be4353aa0987e3ebc39a9ef7d5a89698`|
|tools/verify/node120.py|`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`|
|tools/verify/parent119.py|`d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`|
|raw/vtable123/probe.json.gz|`f194160b8a19989a7d368bc84c46b7934f8dabb7d4faa42d8c72819af12ae77e`|
|raw/graph122/probe.json.gz|`014c74e6ed2fca8884697c61b870f8bd2d03c07e766ec9f1ac288b7248b90a39`|
|raw/factory121/probe.json.gz|`1149739845da278dcf2308e840336ec34652f24a0bb3a4db5d20c84b28cdec5a`|
|raw/node120/probe.json.gz|`d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950`|
|raw/caller119/probe.json.gz|`99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321`|
|118artifact|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|121artifact|`ca37bac84e6135b928e933240b0c1f214516d4f3d9251d76c07b9d5384a2427a`|

All direct tool/input hashes are embedded in124artifact; source/tools from115–118 are transitively pinned there. Raw retained beside derived report; actual compressed logs/REST receipts accompany final verification. No original APK/assets/audio or file>5MB added.

```sh
python3 -m tools.verify.nodefactories124 --check
python3 -m unittest tests.test_nodefactories124 -v
python3 -m unittest discover -s tests -v
```

**33focusedPASS/2.353s; deterministic artifactcheckPASS**. Full suite/exact-head CI receipts and external coordination are appended only after actual completion. Independent122review remains pending; no selfACK/full#27closure.

Review requested: four factoryFDE/RET/constructor/vptr mappings; graph-builder direct BL counts1/1/2/3; exact allocator size offsets and empty label; four vtable RELA groups without invented class names; natural cleanup skip; explicit allocator/PLT/TLS/pool boundary; constructor-specific fields; source-shared lineage; exact count exclusions. Original serialized controller graph-builder execution, original allocator/heap, servicebootstrap, clip/clock/control writers, previous/activepose/conversion/blend/normalize/apply/Unityreadback/render remain OPEN.

Coordination: spec6423047661 ACK/CLOSES bounded123 and records slot identity `Stop` resolved statically; it does not close #27-full or replace independent review. Owner/spec6418032974 static-only and6418326986 lane split retained. a5 G1/G2/G4, AI-4 follow-ups and AI-3 row16 lanes untouched. Protected3/main/merge/release unaffected; no screenshot/render acceptance.

## 6. Final verification and coordination

**33focusedPASS/2.353s; full1727PASS/288.642s; deterministic artifact`--check`PASS; Verify40374283338SUCCESS exactscientific98e5ba9666103ca354ce3fd6116ca295b497c30d.** Recovery40371804376SUCCESS/sourcef92c75fba/raw0db96cba3. Actual compressed logs, RESTrun/jobs, check/local, recovery and spec/review receipts in`reverse-engineering/raw/l3-ef6b75ef124-verification/`; protected3absent/unchanged. Full suite and full regeneration ran sequentially, avoiding113memorythrashing. No preview/render/screenshot gate.

External spec **6423047661 ACK/CLOSESbounded123**; spec **6423276716** assigns R2 review-118 to this lane, spec **6423721976** records CONTINUE124 and a first R2 reminder. R1 review progress **6423751973** found a real description issue in report123; report123 wording is corrected in this pass (complementary scans, encoded metadata usage). R1 full review and independent122review remain pending. Official124handoff and R2 claim below update spec99 status; #27-full still not closed.

Exact tool pins: recovery/nodefactories124.py`97652de3fc1d12fdc65cd7eb1f8ec90b9365efd15318575417fc4b69ca5a88d8`, verify/nodefactories124.py`f226bd35cf6ce144be7531be52117801fac127f037a4ff02d99c925b11bf2aa9`, tests/test_nodefactories124.py`9c34ebf71ac1837bb5e15326171619d6502ce6f3974999047378342cacfe06a3`. Six standalone factory calls have181/200/196/171/181/171nativeinstructions; source1609 integration has one factory-C call plus10parentcalls/930DWORDs, not additive.
