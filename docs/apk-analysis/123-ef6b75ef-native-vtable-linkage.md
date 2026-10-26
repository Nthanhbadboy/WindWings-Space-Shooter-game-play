# 123 — original vtable linkage and real virtual methods behind graph populator

**Provisional / arena/ef6b75ef / #27.** Claim **6420235916**. Scientific **1d6fbcbb7e5f8ae35135ee098b5a4816ea9d4f84**. Follows122handoff6419944060. This replaces three synthetic virtual service sinks with **original vtable RELA slots and original native method bodies**, while retaining an explicit allocator, memset, stack-check and prepared manager/pool/TLS boundary. It is static native analysis, **not** observed game graph creation, original heap, serialized controller bootstrap, Unity readback or render.

## 1. From static RELA candidates to the selected original vtable

A bounded predicate scan for any8B-aligned `vptr` in `10b1000..10b1500` with RELA addends restricted to `0x6d0000..0x6d9000` at `+10/+18/+70` yields **53candidates** because the region is a dense function-pointer table and sliding windows create false positives. Separately, a `KNOWN_VPTRS` group check selects **3candidates** whose original `+10/+18` addends are reserve `571b3c` / notify `571a80`; these addends lie outside the first predicate band. **These are complementary scans, not a literal 53→3 subset narrowing:** their intersection is0 and selected `10b1150` is not among the53. Constructor byte proof below still selects `10b1150`.

| vptr | +10 | +18 | +70 |
|---|---|---|---|
|`10b1150`|`571b3c`|`571a80`|`6d5134`|
|`10b1240`|`571b3c`|`571a80`|`6d6c88`|
|`10b1330`|`571b3c`|`571a80`|`6d5134`|

Original constructor **6d2894..6d28f8** stores literal vptr `10b1150` (`ADRP10b1000; ADD#150; STR[x19]`). Factory **6d26d4..6d2740** calls this constructor. In the captured original graph-builder FDE **6cf7b4..6cff44**, two direct branches at **6cfc34** and **6cfc44** call graph populator6d2950 with manager objects created by6d26d4. Therefore **10b1150 is the selected vtable for those two graph-populator calls**. There are **0 RELA addends equal to6d2950**: the caller is direct, not itself a recovered vtable slot. The graph-builder FDE is captured but not executed; its serialized controller/state prerequisites remain open.

`10b1240` is the120node primary vtable and `10b1330` another constructor vtable; they share reserve/notify but differ at+70. No semantic class/method names are invented from proximity.

## 2. Three real virtual methods

Original graph populator `BLR` at6d2974,6d29c4 and5710b0 now targets actual captured ARM64:

- **+10 reserve**: `571b3c..571b58` checks negative W1, then tail-calls `571b58..571bb4`. That method reads a vector length/capacity at manager chunk+30/+38, grows only when capacity is insufficient and zero-fills new16B records via original PLT `109ace0`. On the declared bounded state it executes one native `memset` service call of `count×16` bytes; resize helper573a34/3f1cb4 is not executed.
- **+18 notify**: `571a80..571aa8` rejects negative S0, checks `index < length`, then writes `S0` at `chunk.data[index*16+8]`. Graph populator supplies S0=0. This is a real float store, not a synthetic record.
- **+70 register**: `6d5134..6d51a0` calls `6d6c88..6d6ca4`, which calls `57095c..570a44` and `570a70..570ab8`. Original57095c stores the new node pointer at `data[index*16]`, slot W3 at+0xC, ORs manager+38 with100hex and list-owner+AC withC8hex. `6d6c88` sets manager+100=1 then returns1; `6d81b0` later zeroes manager+100 and node+100 at PCs6d81c4/6d81c8. The virtual return1 causes57104c to skip its second570abc call. Bounded manager capacities at+140/+160 are prepared so original resize calls3f1d78 are not taken.

These are **real original virtual implementations**. The manager object, list owner, TLS/canary, pool chunks, node storage and manager chunk/vector are still prepared synthetic state. The allocator at3c986c remains an explicit sink; original PLT `memset` is bound to an exact ELF import name and a declared zero-fill sink. Original `__stack_chk_fail` PLT is bound to a fatal sink; it is not reached. No fabricated manager/graph class or serialized controller is claimed.

## 3. Native execution and source integration

Graph populator entry→RET6d29e0 is executed for standalone loop counts **0/1/3/3** with **34/457/1281/1281original instructions**. The source graph uses count3 and1281instructions. These include nested factory/constructor/helper/virtual instructions; do not add122's998,121's220 or120's174 again. Four standalone graph calls contain7factory calls; one source graph contains3. Ten source parent calls are separate.

PC counts prove exactly one reserve, one571b58 tail call, `count` notifies, `count` registers, `count`57095c, `count`6d6c88 manager byte writes and **2×count570a70** calls (one from570abc, one from57095c). Error helpers52e15c/b2e604/3c9438, cleanup570ff0, allocator3c986c, resize573a34/3f1d78 and stack-failure PLT109acc0 are absent. Original PLT109ace0 is visited for count>0.

Native write hooks record manager+100 transitions at6d6c9c (write1) and6d81c4 (write0), plus node+100 zero at6d81c8. Manager array records after execution contain `[new_node_pointer, float0, slot0]` per index. Manager chunk length becomes `count`, capacity remains `2×count`, manager+38 becomes100hex and manager+100 ends0. List owner count/head/flags, factory node fields and pool queue/tag/counter retain the original122 effects.

Source1609 integration creates3prepared nodes via the real-vtable graph, binds only the third to source blob/cache/output/native clip by explicit post-graph pointers118/128/130/1d0 and fixture clocks/flags, then runs ten119parent calls: **930DWORDs bit-equal to pinned118artifact**, completion byte1. Shared115–122lineage; no fresh UnityFS extraction, live graph or game-side writers. Real graph-builder6cf7b4 not executed.

## 4. Bounded native-relocation callback marker decode

Spec6422540134 and6422606755 assign this native lane as the final layer for a5's unresolved callback slot `0x2ADFB48` (decimal44956488) after a5 closed its permitted static text census. **123 now resolves the marker's static literal identity from already retained original raw artifacts; it does not prove a callback invocation or runtime event.**

- `reverse-engineering/raw/ui-audit/native-relocations.json.gz`,1460244B/SHA `4b55d064f7022f8b0e01f22dc2809d12e358324be312e2000280bee4089a4f3d`, source_run40180363840, native/libil2cpp SHA `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`, contains **288733** relocation entries. Exact key `0x2ADFB48` maps to addend `0x2BE5CB8`.
- `reverse-engineering/raw/drone-loadout/cells.json`,SHA `f1f39ce6f4f53c5452758f481ef529b5ef58de13b744f9bc4c6f72c794219ba2`, pins original XAPK/libil2cpp SHAs, original RELA bytes `48fbad02000000000304000000000000b85cbe0200000000` at `rela_file_offset`3563112, got/effective `0x2adfb48/0x2be5cb8`, and string literal index7763: pointeeVA `0x2be5cb8`, file_offset45980856, bytes `53746f70`, UTF-8 **`Stop`**.
- `reverse-engineering/raw/player-hp-board/cells.json`,SHA `09feca7701401f11fb4e14d28091c550a58c965f4626a5bb209ed9bb0f766a59`, and `reverse-engineering/raw/wing-drone/cells.json`,SHA `d0ed6b13082421407634c595122d1b298783ee9c84a8f6385d9581bdbbbb4482`, independently retain the **same exact RELA hex** for got0x2adfb48. `reverse-engineering/il2cpp/stringliteral.json` independently contains address `0x2BE5CB8` → value **`Stop`**.
- The selected vtable123 RELA window has **152** entries and **0** address/addend matches to0x2ADFB48; the callback marker belongs to the separate libil2cpp relocation/string-literal layer, not the libunity graph vtable window. Exact scan/decode receipts retained in123-verification/marker-scan.json and marker-decode.json.

The RELA addend `0x2be5cb8` itself contains encoded metadata usage `0xa0003ca7` (kind5/index7763/lowbit1), not raw UTF-8 `Stop` bytes; `Stop` is the metadata literal payload at index7763. Therefore the bounded static answer is: **callback slot0x2ADFB48 resolves through original RELA to string literal `Stop`.** This is a literal identity, **not** a decoded native method pointer, a proven `RegisterEvents` delegate, a game-side caller, a runtime invocation or a Unity readback. Callback registration/dispatch/live state remain `MODEL_NOT_MEASURED runtime`. No whole-library absence claim is made and no a5 artifact was modified.

## 5. Pins, raw and deterministic checks

Multiple bounded recovery iterations were needed because the first dependency-following scan exceeded its120-function budget; the workflow now preserves diagnostics on failure and final roots are explicit. Final recovery **40363114036SUCCESS**, source **ee1143bd8341d3f24f31abe2c49946de4035dd55**, raw commit **128cdeebf**. Earlier40351688629/40353699604/40355139959/40356142028/40356850009/40358497338/40359965727/40360904445/40361709211 are superseded; REST history and bounded-count diagnostic retained in123-verification. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7. Cache fails on miss; no APK modification or whole-library snapshot.

| Input | SHA256 |
|---|---|
|raw/vtable123/probe.json.gz,21548B|`f194160b8a19989a7d368bc84c46b7934f8dabb7d4faa42d8c72819af12ae77e`|
|datas/l3_ef6b75ef123_native_vtable_graph.json.gz,7082B|`190864db435ee7ed32536ee75b8a10af20deabe288e5514bb3801977950aaf0c`|
|tools/recovery/vtable123.py|`b7771cbbed99b1d1321436ced0737d83c2576a745b3b82001ed061c280108f36`|
|tools/verify/vtable123.py|`d47d1f6a4135cb991ec0d3948ee55e4eebc6201dd2887631aa16dbb7c58eef78`|
|tests/test_vtable123.py|`645d0466acad91a326e1cf8d4dbfe00c2739b98af75bb9d89f575bd297a42c73`|
|tools/verify/graph122.py|`acd741ba9cee69e86846e9b1b2bad3f6f40676918094be80e1e0d7c56530740d`|
|tools/verify/factory121.py|`a26715e77f82998f3f5180c95f63caa3be4353aa0987e3ebc39a9ef7d5a89698`|
|tools/verify/node120.py|`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`|
|tools/verify/parent119.py|`d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`|
|raw/graph122/probe.json.gz|`014c74e6ed2fca8884697c61b870f8bd2d03c07e766ec9f1ac288b7248b90a39`|
|raw/factory121/probe.json.gz|`1149739845da278dcf2308e840336ec34652f24a0bb3a4db5d20c84b28cdec5a`|
|raw/node120/probe.json.gz|`d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950`|
|raw/caller119/probe.json.gz|`99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321`|
|118artifact|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|121artifact|`ca37bac84e6135b928e933240b0c1f214516d4f3d9251d76c07b9d5384a2427a`|

All direct tool/input hashes are embedded in123artifact; source/tools from115–118 are transitively pinned there. Raw retained beside derived report; actual compressed logs/REST receipts accompany final verification. No original APK/assets/audio or file>5MB added.

```sh
python3 -m tools.verify.vtable123 --check
python3 -m unittest tests.test_vtable123 -v
python3 -m unittest discover -s tests -v
```

**36focusedPASS/1.967s; deterministic artifactcheckPASS**. Full suite/exact-head CI receipts and external coordination are appended only after actual completion. Independent122review pending; no selfACK/full#27closure.

Review requested: complementary53-candidate predicate scan versus three-vtable KNOWN_VPTRS check (intersection0); constructor6d2894→vptr10b1150 selection; two direct graph-builder BLs not virtual RELA; three real virtual method bodies and exact PLT/service bindings; manager/vector capacity bounds; PC counts and zero-write transitions; source-shared lineage; bounded marker literal decode and its invocation boundary; exact count exclusions. Real game graph-builder/serialized controller state, original allocator/heap, servicebootstrap, clip/clock/control writers, previous/activepose/conversion/blend/normalize/apply/Unityreadback/render remain OPEN.

Coordination preserved: owner/spec6418032974 static-only and6418326986 lane split retained. Spec6422540134/6422606755 explicitly assign the final native-relocation marker layer to this lane; 123 reads already retained raw evidence and resolves the static literal without editing or taking over a5 artifacts. Runtime invocation remains unproven. Peer8141386a, AI-4 and a5 lanes untouched. Protected3/main/merge/release unaffected; no screenshot/render acceptance.

## 6. Final verification and coordination

**36focusedPASS/1.967s; full1694PASS/284.247s; deterministic artifact`--check`PASS; Verify40366819899SUCCESS exactscientific1d6fbcbb7e5f8ae35135ee098b5a4816ea9d4f84.** Recovery40363114036SUCCESS/sourceee1143bd8/raw128cdeebf. Actual compressed logs, RESTrun/jobs, check/local, recoveryhistory/diagnostic, markerdecode/scan and spec receipts in`reverse-engineering/raw/l3-ef6b75ef123-verification/`; protected3absent/unchanged. Full suite and full regeneration ran sequentially, avoiding113memorythrashing. No preview/render/screenshot gate.

Spec **6422540134/6422606755** assign the native-relocation marker layer to this lane; spec **6422747515** records tip1d6fbcbb7e and "no further action needed" while work was in progress. The official123handoff below supersedes that status and supplies the bounded static decode: `0x2ADFB48→0x2BE5CB8→"Stop"`. Callback invocation/dispatch remains MODEL_NOT_MEASURED runtime. No external ACK/CLOSE of122 observed before this handoff; independent122review remains pending. a5 phase20–22 static census is retained, not modified.

Exact tool pins: verify/vtable123.py`d47d1f6a4135cb991ec0d3948ee55e4eebc6201dd2887631aa16dbb7c58eef78`, recovery/vtable123.py`b7771cbbed99b1d1321436ced0737d83c2576a745b3b82001ed061c280108f36`, tests/test_vtable123.py`645d0466acad91a326e1cf8d4dbfe00c2739b98af75bb9d89f575bd297a42c73`. Four standalone graph calls have34/457/1281/1281nativeinstructions; source graph1281. These include nested methods; do not add earlier chain counts again. 930DWORDs are across10sourcecalls only.

Official123HANDOFF **6422951255**; scientific1d6fbcbb/report8ac0c7ab6/exact-headCI40366819899/1694localPASS. Static-only native lane; callback literal `Stop` resolved, invocation unproven. Independent review pending, no selfACK/full#27closure.

## 7. External ACK and R1 review-progress correction

External spec **6423047661 ACK/CLOSESbounded123**: slot identity `Stop` resolved statically, dispatch/invocation `MODEL_NOT_MEASURED runtime`, #27-full and independent122review still open. R1 review progress **6423751973** correctly notes the original report wording implied a literal53→3 subset narrowing; section1 and review wording are corrected above. It also notes the RELA addend is encoded metadata usage rather than direct UTF-8 bytes; section4 is clarified. Scientific123 bytes/artifact/handoff are unchanged; only descriptive wording changes. R1 full review remains pending; no selfACK/full#27closure.

R1 wording correction posted as **6423891421** with report corrections in124 documentation pass; scientific123 bytes unchanged.
