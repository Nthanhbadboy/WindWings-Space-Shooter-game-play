# 113 — tag23 → SpriteRenderer.m_Sprite: original native registration / dispatch / callbacks

**Provisional; provenance `arena/ef6b75ef`.** Branch `arena/ef6b75ef-windwings-space-shooter-game-p`. Claim PR12 **6414425266**. Scientific/code commit **f5a447c15** (full SHA in verification receipts). Đây là bước tiếp của gap #2 trong report105, không phải làm lại Pause/Home hay nhận phần geometry của người khác.

## Kết quả có giới hạn

Bản APK đang pin có chuỗi native cụ thể nối **class212 / SpriteRenderer + customType23 + attribute0 → m_Sprite**, với value type **class213 / Sprite**. Không còn chỉ dựa vào tên icall/setter wrapper như105. Đã chạy **original registry stores, indexed tag lookup và virtual callback dispatch** trong Unicorn, thay vì Python tự ghi kết quả vào registry.

Đây là **native-fixture evidence**, không phải Unity engine service/readback. Class-ID lookup, component lookup và phần engine sprite setter vẫn là các boundary được khai rõ dưới đây. Không tự ACK/đóng toàn bộ #2; đề nghị reviewer xét riêng native mapping gate. `Frame` mặc định vẫn từ chối; policy opt-in mới được dẫn xuất từ evidence native, không thay policy cũ bằng một suy đoán mặc định.

## 1. Nguồn và tái lập

- XAPK SHA256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`.
- Original ARM64 `libunity.so`: **17783496 bytes**, SHA256 `d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`.
- Raw `reverse-engineering/raw/tag23-113/probe.json.gz`: **32215 bytes**, SHA256 `b1370b5e691d6fa318a0ad22f5a03fbc1c9d81036f3cb6930d8a2ce145d74e8b`.
- Latest recovery **40313791590 SUCCESS**, source **289d273ce**, preserved raw commit **178644d4a**. REST receipt `reverse-engineering/raw/l3-ef6b75ef113-verification/recovery.json`; raw includes exact recovery-tool SHA, PT_LOAD mappings, original bytes, original RELA1027 slots/addends, strings and address contexts. No APK/library binary added to Git.
- Builder `tools/verify/tag23_113.py`; guarded executor `tools/verify/tag23_113_native.py`; **33** tests in `tests/test_tag23_113.py`.
- Artifact `datas/l3_ef6b75ef113_native_tag23.json.gz`: **34002 bytes**, SHA256 `af91630b507c877408427f5acad225ddcdf5e5429fa3f29069fc8b7b9af6036c`. `inputs` pins tools plus original object/link chunks and derived chunks actually loaded by the model bridge; no inherited unpinned asset values.

```sh
python -m tools.verify.tag23_113 --check
python -m unittest discover -s tests -p test_tag23_113.py -v
python -m unittest discover -s tests
```

Unicorn dependency is the same repository dependency used by preceding native fixtures. Generation is deterministic (`gzip mtime=0`), and `--check` compares full compressed artifact bytes.

## 2. Static type-info links: component ≠ referenced value

The original static records contain name pointer at record+24, integer class ID at+48, native-size word at+52 and descriptor pointer at+88. Report these as captured static type-info links, **not** initialized engine class-service readback:

| Static record | Original name | ID | Size word | Descriptor |
|---|---|---:|---:|---|
| `0x10f0628` | `SpriteRenderer` at `0x112ce9` | 212 | 592 | `0x10ead38` |
| `0x10ea010` | `Sprite` at `0x13710e` | 213 | 440 | `0x10e8fe0` |

Correction to an early candidate label in recovery: **`0x10e8fe0` is the Sprite value-type descriptor, not the component212 descriptor or the binding table**. Getter `0x946da0` returns it. Component registration instead passes **`0x10ead38`**. The prior immediate212 search is not proof: source/debug line numbers can also contain212. This deliverable uses the original linked static records, registration argument and callbacks, not immediate co-location.

## 3. Original registration really stores tag23

Entry **`0x940218`**:

1. Calls original service accessor **`0x492da8`**; absent service returns before allocation.
2. Allocates an **8-byte** handler through `0x3c9298` (fixture allocator boundary).
3. Stores original vptr **`0x10b9d80`** into handler and saves singleton at `0x1199a98`.
4. Passes **x1=`0x10ead38`, w2=`0x17` (=23), x3=handler** to registry virtual slot+8.

The registry service vptr is recovered from original RELA at GOT **`0x10e2a58`**, plus16 → **`0x10b09c0`**. Virtual slot+8 resolves to **`0x6a9d50`**, which reads manager singleton `0x1185350` and tail-calls **`0x6a97a0`**. Original manager code appends `(typeDescriptor,tag)` to its native vector and stores `handler` into **`slots[tag]`** at `0x6a97f0`.

Final fixture runs this entire chain: **57 native instructions**, with only allocator `0x3c9298` substituted. Registry accessor, virtual wrapper, vector append, tag indexing and stores are **not hooked**. Readback of that **fixture's** memory is mapLength1, descriptor=`0x10ead38`, tag23, slots[23]=handler, handler.vptr=`0x10b9d80`. Native instructions, visited PCs and original relocated-data reads are saved in artifact.

Synthetic prerequisites: allocated service object; native-layout empty vector with capacity64 encoded128 at+24; handler-slot array; manager and three BSS singleton values. Capacity is supplied, so native vector-growth helper does not execute. No claim that this initialized state was obtained from Unity bootstrap. With null service the native initializer executes8 instructions and performs no allocation/registration. Counterfactual original `mov w2,#24` writes24 and leaves fixture slot23 empty.

## 4. Native serialized-tag lookup and virtual routing

Original dispatch entry **`0x6a9674`**, custom branch **`0x6a94f0`**:

- Reads custom-tag byte at native GenericBinding+`0x10` and class-ID word at+`0xc`.
- Requests class descriptor via `0x3d5670`; obtains component via `0x3dfa9c`.
- Loads original registry `slots[tag]` at **`0x6a9624`**.
- Calls handler virtual slot+`0x28` → **`0x946da0`**, returning **Sprite descriptor `0x10e8fe0`**.
- Copies native binding result containing attribute0, tag23, selected handler and native-object pointer into output.

Runs **69 native instructions** after registration. Class-ID and component service hooks are explicit; the class service answers from the **captured static record**, not a hard-coded guessed class association. Native class-service initialization/lookup internals are **not** executed. Non-MonoBehaviour custom branch is exercised; no claims about unrelated dispatch branches.

Original binding readers/writers then use the same selected handler:

| Path | Native dispatcher | Vtable slot | Actual callback | Evidence |
|---|---|---|---|---|
| reader | `0x6a9898` | +`0x18` | `0x946d00` | loads native object at binding+`0x18`, reads word object+`0x1f0`; **11 native instructions** including dispatcher |
| writer | `0x6a98c4` | +`0x10` | `0x946ce4` | routes 32-bit input to original setter **`0x93b09c`**; **28 native instructions** before/after setter sink |
| value type | custom lookup | +`0x28` | `0x946da0` | returns Sprite descriptor213 |
| property resolver | callback | +`0x20` | `0x946d0c` | exact original `m_Sprite` comparison and attribute0 write |

Native word test input `0x12345678` is synthetic. No equality between an APK serialized PathID and an engine runtime reference word is assumed; the later PPtr mapping model is a separate evidence layer.

The writer reaches an instrumented setter **sink**; the full sprite setter/body, reference-ID service, asset lifetime notifications and Unity object changes do not execute. Independent captured icall wrapper `0x3869f8` calls the **same** setter at `0x386afc`; writer calls it at `0x946cf4`. That wrapper is supplementary, not the numeric-tag proof.

Negative tag22 is an empty slot in the **isolated tag23 fixture**, not proof that the actual game has no tag22 handler. Foreign class214 is absent from the fixture's supplied class/component service, not an engine-wide rejection verdict. Two fixture base addresses reproduce mapping/reading behavior. A reader-offset opcode mutation and a relocated reader-pointer mutation change results, demonstrating execution dependence on captured code/RELA rather than host-side property assignment.

## 5. Exact property resolver, without semantic guesses about raw flags

Callback **`0x946d0c`** compares against original C string **`m_Sprite` at `0x138aef`**. Successful lookup requires raw **w2 bit0**; it returns1 and writes a 32-bit zero only at out+4. Native fixture executes **96 instructions** for the accepted exact name in either string representation, with **zero function hooks**.

- Native inline small-string mode byte at+`0x20` is **1**, length=`24-byte[+0x18]`; pointer form has mode0, pointer at+0 and length at+`0x10`. This corrects an early unexecuted layout hypothesis.
- Sixteen stored cases cover inline/pointer forms and exact name, missing low bit, other bit, low+other bit, wrong property, truncated name, suffix and empty name.
- Flags0/2 fail; flags1/3 succeed. **Do not rename raw bit0 to an engine flag enum without caller proof.** Reference-value semantics here are established separately by Sprite descriptor213 and native PPtr reader/writer routing.
- Reject leaves output sentinel unchanged; success changes only out+4..7 tozero.
- Counterfactual original string `m_Colour` makes `m_Sprite` fail and `m_Colour` succeed. Missing string/required relocation fails closed, not mapped-page zero success.

## 6. Apply the bounded proof to the original unresolved clip

Same inherited target, now joined to native registration rather than icall spelling:

- Clip **`data.unity3d/resources.assets:1609`**, original object SHA256 `69ccddde268b8335b5fb47c75775f2560a756ded282336de390a6f325ac64fae`.
- Raw location `reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz`, row140.
- Animator **`data.unity3d/level2:4695`**; binding index **48**; path hash **2345408111** → source path **`Finger 2`**; unique component **`data.unity3d/level2:5922`**, class212.
- Exact generic binding: attribute0/customType23/typeID212/isPPtrCurve1/isIntCurve0/isSerializeReferenceCurve0/script null. Raw clip's `m_PPtrCurves` is empty: no property-name shortcut from that list.
- `binding_policy` validates source-derived native registration, component class, attribute, tag, pointer flags and null script before returning **`m_Sprite`**. Foreign target/changed binding fail. This bounded adapter does **not** assert Unity rejects the same mutations in every engine branch.

Existing `Frame` code and its default denial remain unchanged. First application without policy is rejected atomically. Explicit source-proved policy is then supplied for binding48 only. Six model transactions sample original PPtr key times (initial sentinel sampled at clip start): **0, 3.4166667461395264, 3.549999952316284, 3.700000047683716, 3.8499999046325684, 3.9833333492279053**. Each transaction contains **51 modeled binding writes**, including exactly one Sprite reference. Modeled `m_Sprite` readback alternates source resources assets **3799,2633,3799,2633,3799,2633**.

This is the existing decoded/discrete clip **model**, not newly independent interpolation, engine playback or Unity readback. Viewport fixture1×1 merely satisfies `Frame` constructor; **no projection/render is invoked** and it is not a claimed device viewport. No screenshots/redraw/preview or render acceptance gate introduced.

## 7. Verification / handoff

- Focused **33 PASS / 0.615s**; exact-head Verify **40314713081 SUCCESS** at **f5a447c15a117ca4571e2768f0274d1ad4f20b39** (REST `ci.json`). **Local full-suite1371 PASS /316.344s**, receipt `local.json`; CI logs download returned EOF, so no CI test count is invented from its green status.
- Deterministic generation/`--check`; input SHA checks; no added file over5MB; protected `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, `datas/player_start_stats.json` unchanged against `c4ac58cde` (all three absent both at baseline and current checkout; no files fabricated).
- Initial fixture-development failure: allocator hook address was not mapped, so Unicorn rejected instruction fetch before hook entry. Final fixture maps the explicit synthetic sink and intercepts it; native source pages are not silently filled to compensate. An initial full-suite run was deliberately stopped to expand model bridge from two redundant sample times to all six source PPtr keys; a second concurrent full-suite/`--check` attempt was stopped after resource contention. Final runs are sequential; only completed final-run counts will be reported. This is not a reported test failure or a completed suite.
- Coordination saved: spec **6414685378** reopened former AI3 #4–8; AI2 subsequently claimed **#5 in6414763120**. **Do not take #5**. AI2 #24 handoff and historical112 peer review remain separate. No changed peer decisions are silently overridden.
- Review requested: static type-info link interpretation; native registry/vector/table stores and virtual slot semantics; explicit service/allocator/setter boundaries; policy refusal outside the exact proof; fixture/model ≠ Unity service/readback ≠ render. No self-ACK, merge or main push.
