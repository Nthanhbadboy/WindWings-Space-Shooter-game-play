# 122 — original graph-populator loop with explicit virtual/allocator services

**Provisional / arena/ef6b75ef / #27.** Claim **6418915726**. Scientific **d15858faa4a31090355e6ba86221d91c69f26a79**. Follows121handoff6418718832. This executes the bounded original loop that calls121factory repeatedly, then runs original helper/list code and three **explicit synthetic virtual service sinks**. It is static native analysis, **not** a captured game graph, real virtual implementation, runtime node creation, TypeTree/Unity readback or render.

## 1. Original chain and actual FDE extents

Original FDE **6d2950..6d29e4**,148B, returns at **6d29e0**. Its first action is `ldr x8,[x0]; ldr x8,[x8,#10]; blr x8` with W1=incoming count. It returns immediately when count=0. Otherwise, for index0..count−1 it:

1. calls factory **6d5e58** with `(X21,0,0)`;
2. writes `stp xzr,new_node+200,[new_node+b0]` and DWORD7 at new_node+3c;
3. calls **6d81b0..6d81dc** with `(new_node, manager, −1, index)`;
4. calls virtual slot **manager.vtable+18** with `(manager,index)` and S0=0.

Original6d81b0 calls **57104c..5710ec**, then writes byte0 at **manager+100** and **new_node+100**. 57104c calls **570abc..570c14** with `(new_node,manager,−1)`, interprets −1 through chunk length and then calls virtual slot **manager.vtable+70** with `(manager,new_node,index,slot=chunk_length−1)`. 570abc's selected branch uses **570a70..570abc** to OR node+38 with100hex and list_owner+ac withc8hex. Error-reporting functions **52e15c/b2e604/3c9438** are captured but not executed on this selected path.

Recovery found **no direct branch reference to6d2950 in the scanned original range**. That is not proof of no caller or dead code: virtual/indirect dispatch remains possible. The virtual slots and their real implementations are the next structural lead, not assigned semantic names.

## 2. Exact service boundary

The fixture supplies two distinct synthetic objects plus prepared service state:

- **manager** (X0): its vptr points to an explicit synthetic table. Slot+10is `reserve(count)`, +18is `notify(index,S0=0)`, +70is `register(manager,node,index,slot)` returning1. The real original implementations are not recovered/executed.
- **list owner** (X1): passed as factory/handle owner. Original factory writes node+20=list_owner, increments list_owner+34 and ORs list_owner+ac.
- **allocator sink** at original3c986c: checks the121request (`200hex`,align16,category94,flag0,empty-C-string label12da21,auxABhex) and returns the next prepared0x400B node block. Original allocator/heap is not executed.
- **pool chain**: global116cb40→service, service+450→queue, queue→chunk0→chunk1…; each chunk has slot array pointer+40, length0and capacity8. Original getter575e80/atomic-pop53f36c and base constructor execute once per loop. Queue tag and service acquisition counter increment natively by count.
- **TLS**: synthetic TPIDR_EL0 page and canary1122334455667788 for original570abc stack protection. Original `__stack_chk_fail` PLT is not executed. This is not Android TLS/session parity.

All other instructions in the selected graph/factory/constructor/helper/list path are original captured ARM64. The synthetic `register` service returns1 so original57104c skips its second570abc call; PC counts verify **exactly one570abc per loop iteration**, not a hidden duplicate service call.

## 3. Native writes and source1609 integration

For each created node, original graph code writes node+b0 qword0, node+b8 pointer node+200 and node+3c=7. Original121factory/constructor writes vptr10b1240, node+20=list_owner, node+30=acquired chunk and constructor defaults. Original6d81b0 zeroes **manager+100** and **new_node+100**; memory-write hooks record native PCs6d81c4/6d81c8, not a memset. Original570abc stores manager into chunk slot0; original570a70 ORs node+38 with100hex. Factory121 handle/list code makes list_owner+34=41+count, list_owner+48 point at last node+8 and list_owner+ac=c8hex.

On the selected570abc path, chunk slot0 is initially null; native code takes original branch570be0, stores manager there and calls570a70. 57104c then computes slot=chunk_length−1=0 and calls virtual+70. Error-reporting helpers52e15c/b2e604/3c9438, cleanup570ff0, allocator3c986c, allocation fallback575b34/573a1c and stack-failure PLT109acc0 are absent from executed PCs.

Source integration creates **three** prepared nodes with original graph count3, then binds only the **third** node to prepared source blob/cache/output/native clip via explicit post-graph pointers118/128/130/1d0 and fixture clocks/flags. Ten119parent calls on that one node produce **930DWORDs bit-equal to pinned118artifact** and completion byte1. These bindings are harness-side; the graph loop does not attach clips or clocks. Shared115–121lineage means this is composition/regression, not fresh UnityFS extraction or game playback.

Counts: **4standalone graph calls** with loop counts0/1/3/3 = **7standalone factory calls**; **1source graph call** with3factory calls; **10source parent calls/930DWORDs**. Standalone native instruction counts are **15,344,998,998**; source graph is **998**. 998 includes nested factory/constructor/helper instructions and is not additive to121's220. Virtual service calls are1/3/7/7 respectively. Relocation/prefill/tag tests are not artifact cases.

## 4. Pins and retained raw

Initial recovery40342559786 captured graph/6d81b0 but not570abc/570a70 dependencies. Final **40343238879SUCCESS**, source **0a6387ea77dd1285e6345a424afd394f5755cdd5**, raw commit **08d9c1c44**. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7. Cache fails on miss; no APK modification or whole-library snapshot.

| Input | SHA256 |
|---|---|
|raw/graph122/probe.json.gz,10782B|`014c74e6ed2fca8884697c61b870f8bd2d03c07e766ec9f1ac288b7248b90a39`|
|datas/l3_ef6b75ef122_native_graph_populator.json.gz,6095B|`5a09fe730587c4ade3bfdaa541ead63e754b674fc7caee52b47ed6f8dd3edc35`|
|tools/recovery/graph122.py|`9ca0f83e6ef957046b93ae37788b1a9cfd40b5c83673516cd0273333ef70eb5a`|
|tools/verify/graph122.py|`acd741ba9cee69e86846e9b1b2bad3f6f40676918094be80e1e0d7c56530740d`|
|tests/test_graph122.py|`81627f18b55c47a89c9671f1a141941152d70c1ee935b81021e7a6e14763d00b`|
|tools/verify/factory121.py|`a26715e77f82998f3f5180c95f63caa3be4353aa0987e3ebc39a9ef7d5a89698`|
|tools/verify/node120.py|`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`|
|tools/verify/parent119.py|`d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`|
|raw/node120/probe.json.gz|`d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950`|
|raw/factory121/probe.json.gz|`1149739845da278dcf2308e840336ec34652f24a0bb3a4db5d20c84b28cdec5a`|
|raw/caller119/probe.json.gz|`99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321`|
|118artifact|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|121artifact|`ca37bac84e6135b928e933240b0c1f214516d4f3d9251d76c07b9d5384a2427a`|

All direct tool/input hashes are embedded in122artifact; source/tools from115–118 are transitively pinned there. Raw retained beside derived report; actual compressed logs/REST receipts accompany final verification. No original APK/assets/audio or file>5MB added.

```sh
python3 -m tools.verify.graph122 --check
python3 -m unittest tests.test_graph122 -v
python3 -m unittest discover -s tests -v
```

**30focusedPASS/1.642s; deterministic artifactcheckPASS**. Full suite/exact-head CI receipts and external coordination are appended only after actual completion. Independent121review pending; no selfACK/full#27closure.

Review requested: original graph/helper/RET FDE extents; three virtual slots and synthetic return values; allocator/pool/TLS boundary; native null-slot branch and exactly one570abc per loop; zero writes at6d81c4/6d81c8; manager versus list-owner fields; no direct upstream branch ≠ no caller; post-graph source bindings and shared lineage; exact count exclusions. Real virtual implementations, game manager/graph dispatch, original allocator/heap, servicebootstrap, clip/clock/control writers, previous/activepose/conversion/blend/normalize/apply/Unityreadback/render remain OPEN.

Coordination preserved: owner/spec6418032974 closes#28runtimeprobe (static-only);6418326986 assigns this lane libunity.soFDE and a5 game-sideC#writers/bootstrap. No takeover/import. Peer8141386a#7 and AI-4#29 lanes untouched. Protected3/main/merge/release unaffected; no screenshot/render acceptance.

## 5. Actual verification and coordination

**30focusedPASS/1.642s; full1658PASS/279.933s; deterministic artifact`--check`PASS; Verify40347869822SUCCESS exactscientificd15858faa4a31090355e6ba86221d91c69f26a79.** Recovery40343238879SUCCESS/source0a6387ea7/raw08d9c1c44. Actual compressed logs, RESTrun/jobs, local/check/recovery/spec receipts in`reverse-engineering/raw/l3-ef6b75ef122-verification/`; protected3absent/unchanged. Full suite and full regeneration ran sequentially, avoiding113memorythrashing. No preview/render/screenshot gate.

External spec **6419109494 ACK/CLOSESbounded121node-factory**: checks artifactSHAca37bac84e61, allocator request and no malloc parity, natural570ff0skip, list sentinel/count41→42/ORC8, corrected owner+ac,930bit-equal and captured-not-executed6d2950. It does NOT ACK122 or close#27. Receipt in122-verification/spec-ack121.json; appended to121 report. Spec **6419688649** records this lane as "ef 🔄122, tip08d9c1c44, not handoff"; official122handoff below supersedes that status. Static-only and lane boundaries from6418032974/6418326986 retained; a5 game-side phase4 handoff6419853864 and peer/AI-4 lanes are not imported.

Exact tool pins: verify/graph122.py`acd741ba9cee69e86846e9b1b2bad3f6f40676918094be80e1e0d7c56530740d`, tests/test_graph122.py`81627f18b55c47a89c9671f1a141941152d70c1ee935b81021e7a6e14763d00b`, recovery/graph122.py`9ca0f83e6ef957046b93ae37788b1a9cfd40b5c83673516cd0273333ef70eb5a`. Four standalone graph calls have15/344/998/998nativeinstructions; source graph998. These include nested factory/constructor/helper instructions; do not add121's220or120's174 again. 930DWORDs are across10sourcecalls and exclude all standalone/variant calls.

Official122HANDOFF **6419944060**; scientificd15858faa/report93978a0e5/exact-headCI40347869822/1658localPASS. Static-only native lane per6418032974/6418326986. Independent review pending, no selfACK/full#27closure.
