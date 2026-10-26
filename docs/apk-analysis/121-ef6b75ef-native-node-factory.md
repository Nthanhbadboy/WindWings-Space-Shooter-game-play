# 121 — original node factory, explicit allocator sink and handle-list insertion

**Provisional / arena/ef6b75ef / #27.** Claim **6417816695**. Scientific **f58d0ebbb1f26bfc8992c4207cb8f051cb639f6b**. Follows120handoff6417679550. This executes factory entry→constructor→list insertion→RET over prepared synthetic state. It is **not** an original heap implementation, game graph bootstrap, observed factory dispatch, Unity readback or render.

## 1. Original factory bytes and direct caller

Original FDE **6d5e58..6d5ec8**,112B, returns at **6d5ec4**. Four original argument registers into allocator routine3c986c are set from incoming X2 and literals:

- X0=incoming X2+200hex, X1=10hex, W2=5ehex(94), W3=0,
- X4=12da21, W5=abhex.

Original bytes at **12da21 are a single zero byte**, followed by `UnityEngine.Camera::get_depth` at12da22. The allocator label is therefore an empty C string; that adjacent string is **not** the label. After allocation, factory passes incoming W1 to constructor6d353c, then calls alternate cleanup570ff0 only when node+38 bit0 is0 OR node+a8 halfword nonzero. It always calls handle/list routine572a38, then returns newly allocated node in X0.

One local direct branch to this factory is **6d2990**, inside original FDE **6d2950..6d29e4**. Its bytes show a virtual call, a loop bounded by incoming X2, repeated factory calls with `(X21,0,0)`, writes to new node+b0/+3c, call6d81b0 and another virtual call. That upstream function is **captured, not executed**; it is a candidate parent/loop chain, not proof of live game graph construction or number of real nodes.

Initial recovery40335200188 returned an overbroad301077B raw because scanning every direct reference to the allocator captured hundreds of unrelated callers. Final40337151003 narrows branch references to the factory within6d0000..6d8000 and explicit original dependencies; final raw8951B. Earlier raw is superseded, not used for the artifact.

## 2. Explicit allocator service boundary

The fixture installs a **synthetic sink at original address3c986c**. Original factory still performs native BL to that address, but the sink intercepts before any original allocator instruction executes. It asserts exact request:

`size=X2+200hex; alignment=16; category=94; flag=0; label=12da21 (original zero byte); aux=abhex`.

It returns a prepared0x400B node storage block. This is **not** original allocator3c986c/3cd56c/3cdcac execution, heap/arena parity, malloc behavior or a real memory allocator. Original allocator internals are captured for static audit; sink absence is checked by requiring3c986c not to appear in native visited PCs. Size variants X2=0,40hex,100hex produce requests200hex,240hex,300hex. No request claims final object size.

Other original code **does execute**: factory,120constructor, base/member routines, prepared pool getter/atomic pop, skip branch and handle/list insertion. Allocator is the only substituted service during factory execution. The later source parent chain retains its previously declared hostmodff/memcpy and syntheticTLS services; Android libm/session parity remains unproven.

## 3. Natural cleanup skip and exact list writes

120constructor installs node+38 bit0=1 and node+a8 halfword=0. Consequently original factory's tests at6d5e94/6d5e9c **naturally skip570ff0**; no synthetic cleanup service is needed. This is not a forced PC bypass. 570ff0 and its dependencies are captured but not executed.

Original572a38 executes with `(owner,new_node)`:

- writes owner pointer to **node+20**;
- inserts node+8/10 links into owner+48 intrusive circular list with sentinel owner+40;
- increments **owner+34** count from prepared41to42;
- ORs **owner+ac** halfword withc8hex (prepared0→c8hex).

Correction to a plausible misreading: it modifies **owner+ac**, not node+ac. Node+ac retains prefill from constructor (A5A5hex in default case; constructor's120write coverage leaves it untouched). Owner/list/pool/global/label/storage are synthetic, but list pointer writes/count/OR are native. This is native handle/list routing, not proof of a game-side manager or live graph registration.

The new node also has primary vptr10b1240 and chunk pointer+30; original RELA10b12c0→6d46a8 from120 remains linked. Factory returns exactly the prepared node pointer. Pool getter/atomic-pop effects from120 persist: queue head null, tag increment, acquisition counter1, chunk length1, slot0 null.

## 4. Source1609 integration

One factory is run on ParentFixture's node storage, then four explicit post-factory bindings are installed: node+118→sourceblob, +128→streamcache, +130→outputholder, +1d0→nativeclip. `configure_node` supplies clocks/flags/loop. These are harness bindings, **not** recovered graph/clip/clock writers; factory itself does not bind a clip.

Ten unchanged source queries then execute the complete119parent chain (118caller→second-phase guard→node174 store→RET), yielding **930DWORDs bit-equal to pinned118artifact** and completion byte1 on all calls. Shared115–120lineage means this is a composition/regression, not independent UnityFS extraction or live Animator playback. No active second-phase pose/conversion/blend/apply path is executed.

Counts: **3standalone factory cases +1source factory=4factory calls**. Each selected factory trace has **220native instructions including the174constructor instructions** (not additive). Three standalone allocator requests plus one source allocator request=4. Ten source parent calls/930DWORDs are separate. 27focused unit-test invocations with relocation/variant fixtures are not counted as artifact standalone cases.

## 5. Pins and retained raw

Final recovery **40337151003SUCCESS**, source **0cb0fd50f4924daf63b0a7f082a5eaae758ee360**, raw commit **cca51db0b**. Original XAPK SHA f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e; libunity SHA d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7. Cache fails on miss; no APK modification or whole-library snapshot.

| Input | SHA256 |
|---|---|
|raw/factory121/probe.json.gz,8951B|`1149739845da278dcf2308e840336ec34652f24a0bb3a4db5d20c84b28cdec5a`|
|datas/l3_ef6b75ef121_native_node_factory.json.gz,5569B|`ca37bac84e6135b928e933240b0c1f214516d4f3d9251d76c07b9d5384a2427a`|
|tools/recovery/factory121.py|`7a822b73f9a6d302634c86958fc451f37daf46a4a3cb8f092206309315af8562`|
|tools/verify/factory121.py|`a26715e77f82998f3f5180c95f63caa3be4353aa0987e3ebc39a9ef7d5a89698`|
|tests/test_factory121.py|`f64eb7b882eb8dc481d39e677baae6c1ed521371aba12b763e810054e10f40a6`|
|tools/verify/node120.py|`43e699b71888b7ed2815776c051a86e126b1afa8f4bcbf9c4dc87bb4da8fe7e0`|
|tools/verify/parent119.py|`d63634b0a4b438855b90fa3db43e10c2bde1e4697de2843dc4dd7616b91de4eb`|
|raw/node120/probe.json.gz|`d8708494976e94b6310d299ab66e290091ef6204507bbaa854358a201fbd8950`|
|raw/caller119/probe.json.gz|`99950204cef0afd07919048073a20a305df61c70e43f98c38cfcfa4a167df321`|
|118artifact|`4eaa9a118efbb7787680b0057c3cb6f2fd2bd59e50d8cd82743e92c084671e8b`|
|119artifact|`49eb74d14c974dafabae8dc5cbe30804f9872edee25807c2e16adaecd73de78f`|

All direct tool/input hashes are embedded in121artifact. Source data and115–118tools are transitively pinned there; no fresh source decode is claimed. Raw retained beside derived report, actual compressed logs/REST receipts accompany final verification. No original APK/assets/audio or file>5MB added.

```sh
python3 -m tools.verify.factory121 --check
python3 -m unittest tests.test_factory121 -v
python3 -m unittest discover -s tests -v
```

**27focusedPASS/1.425s; deterministic artifactcheckPASS**. Full suite/exact-head CI receipts and external coordination are appended only after actual completion. Independent120review remains pending; no selfACK/full#27closure.

Review requested: original factoryFDE/RET and allocator argument literal; empty label byte versus adjacent string; explicit sink boundary; natural skip of570ff0; owner+ac versus node+ac; prepared list invariants; upstream caller not executed; post-factory bindings and shared source lineage; count exclusions. Original allocator/heap/factory upstream dispatch/graph registration, servicebootstrap, clip/clock/control writers, previous/activepose/conversion/blend/normalize/apply/Unityreadback/render remain OPEN. a5runtime/primary and8141386a#6rep ownership retained. Protected3/main/merge/release unaffected; no screenshot/render acceptance.

## 6. Actual verification and changed coordination

**27focusedPASS/1.425s; full1628PASS/281.896s; deterministic artifact`--check`PASS; Verify40339667616SUCCESS exactscientificf58d0ebbb1f26bfc8992c4207cb8f051cb639f6b.** Recovery40337151003SUCCESS/source0cb0fd50f/rawcca51db0b. Actual compressed logs, RESTrun/jobs, local/check/recovery receipts in`reverse-engineering/raw/l3-ef6b75ef121-verification/`; protected3absent/unchanged. Full suite and full regeneration ran sequentially, avoiding113memorythrashing. No preview/render/screenshot gate.

External spec **6417893389 ACK/CLOSESbounded120node-init** (artifactSHAfe2c0997d2ec,174instructions/0sinks,447/512write coverage,RELA→119parent,930bit-equal,120didnotexecutefactory); it does NOT ACK121 or close#27. Receipt in121-verification/spec-ack120.json; appended to120 report.

Owner/spec **6418032974 CLOSES#28runtimeprobe**: live-DPS/#27consumption/second-device are MODEL_NOT_MEASURED/static-only; no new runtime run/emulator/Frida branch. Owner/spec **6418326986 splits#27**: this lane (`ef6b75ef`) retains **libunity.soFDE** nodepipeline→graphcreation→servicebootstrapnative→clipbinding→clock/controlwritersnative; a5 takes **game-sideC#writers/bootstrap** from dump.cs/libil2cpp. No boundary crossing or merge. Spec **6418453588** is a5 quick-win claim; not imported here. Receipts retained in121-verification. This report is static native analysis only; no runtime/readback/render claim.

Exact tool pins: verify/factory121.py`a26715e77f82998f3f5180c95f63caa3be4353aa0987e3ebc39a9ef7d5a89698`, tests/test_factory121.py`f64eb7b882eb8dc481d39e677baae6c1ed521371aba12b763e810054e10f40a6`, recovery/factory121.py`7a822b73f9a6d302634c86958fc451f37daf46a4a3cb8f092206309315af8562`. Four artifact factory calls have220nativeinstructions each;174constructorinstructions are a subset, not additive. 930DWORDs are across10sourcecalls, not9test/variant invocations.

Official121HANDOFF **6418718832**; scientificf58d0ebbb/reporta454e1202/exact-headCI40339667616/1628localPASS. Static-only native lane per6418032974/6418326986. Independent review pending, no selfACK/full#27closure.

External spec **6419109494 ACK/CLOSES bounded121node-factory**; checked artifactSHA, allocator sink arguments/no malloc parity, natural cleanup skip, list sentinel/count/OR flags, owner+ac correction and930bit-equal. Upstream6d2950 correctly captured-not-executed, subsequently executed in122. Independent122review pending; full#27stillOPEN. Receipt in122-verification/spec-ack121.json.
