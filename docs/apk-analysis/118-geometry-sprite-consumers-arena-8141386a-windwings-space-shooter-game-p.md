# 118 — MISSING row16: original SpriteRenderer census → reverse Sprite consumers

provenance: **`arena/8141386a-windwings-space-shooter-game-p`**

CLAIM PR12 `6421533206`, accepted spec91 `6421838430`, after frozen#8 HANDOFF
`6421267527` / ACK `6421474597`. This is a **new bounded row16 follow-up**, not reopening
closed#16/96–98 or changing the original#4–8 geometry results.

## What was still missing, and what this slice actually closes

MISSING row16 still called the Sprite catalog adequate but the global Sprite→consumer
join missing. Raw98 and raw102 contain useful closures, but counting them as all
SpriteRenderers would hide most original objects. This report adds a **complete census
of original class212 SpriteRenderers across all bundle SerializedFiles**, then joins
its exact file-qualified Sprite PPtrs to the native catalog. Other consumer classes and
prefab/UI ancestry remain explicitly **captured-source slices**, not all-APK claims.

Artifact **`datas/l3_geometry_sprite_consumers_8141386a.json.gz`**, **728633B**, SHA256
**`c33ad8a80c35990cf5dd94165234878a62785a5bb39ddef5f2bb73752408019d`**.
The artifact retains a reverse row for every **2185 native Sprite identities**: original
name/hash, exact native renderer IDs grouped by owning file, separately tagged captured
references, exact captured UI/resource-root associations, and scoped negative results.
No meaning label is assigned from an image name (`meaning_label=null`).

| Scope | Measured result | Not claimed |
|---|---|---|
| Original native SpriteRenderer census | **62815/62815**, full supplied-schema decode + whole original inverse-byte equality; **12311740B** | Native execution or independently discovered engine schema |
| Original owning GameObjects | **62815 unique**, whole original inverse equality, literal name/layer/active-self + exact transform candidates | Asset semantics, active runtime instance, world placement/visibility |
| Native Sprite PPtrs | **61864 exact nonnull /951 null** | Null→default substitution, visible use |
| Native catalog coverage | **1802/2185** have at least one native renderer reference | All consumer classes covered |
| Plus tagged captured component/animation references | **1897/2185** have a scoped reference; **288** have none in these queried slices | “288 unused sprites” or missing assets |
| Captured root associations | **1250 Sprite rows /720 distinct root-kind-label tuples** | Automatically loaded prefabs/Resource.Load/runtime selection |

## Original authority and fresh recovery

Original recovery **40364305678 SUCCESS** on source
**`2beef6d63aba60732eb5b726ae4281f06f0c41bd`**, completed in10m3s. It reads the immutable
original package, not a reconstructed APK. Actual REST run/jobs are retained separately
from final scientific CI; no original CI raw-log/test-count/peak-RSS claim is made.

| Input | Bytes | SHA256 |
|---|---:|---|
| original XAPK |142125649| `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| base APK |117158131| `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1` |
| data.unity3d |63881856| `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7` |
| native source index |83719| `e2f9c523397c69b00184b4d6d61c74c84ed70baf0473bce16248ba1b5f20bd03` |
| source CI receipt gzip |2744| `6d25437d7a266309141bdbc9204c52f21fd72e7308f8de751cd71abc1243c0be` |
| native supplied schemas gzip |1182| `e012fd7ebf120864453f8a63d873d49f3b7bac3670f7eec43e712ede3fc4c0ec` |

Raw paths are under `reverse-engineering/raw/geometry-8141386a/sprite-consumers/`.
The file metadata is independently framed by the frozen ef110 reader; class212 counts
are measured again against **all12 original SerializedFiles /717262 metadata entries**,
not inferred from capture union. The native schemas are **supplied UnityPy1.25.4 TPK**,
matching each file's actual declared2022.3.62f3, not engine TypeTree readback.

| Original owning file | class212 objects |
|---|---:|
| level0 |8|
| level1 |4|
| level2 |1036|
| level3 |329|
| sharedassets0.assets |8|
| resources.assets |61430|
| other6 SerializedFiles |0|
| **Total** |**62815**|

Initial serialized scenes total **1377**; the other **61438** renderers are in asset files,
not automatically runtime-placed. `m_Enabled=true` appears **62426** times; this alone is
not current visibility/activity. Null Sprite objects are retained, not given a quad,
white pixel, nearest name, or arbitrary catalog ID.

## Byte proof and OOM-safe source storage

For every native SpriteRenderer, the inherited stdlib109 Reader consumes the whole
original object using an explicit supplied native schema; the frozen own#8 inverse
writer reproduces the original bytes. All **62815 renderer objects are196B**. Typed
`m_Sprite`/`m_GameObject` offset/size/SHA spans, PPtrs, whole-object hash, enabled/draw-mode/
color snapshot and original owning-file qualification are retained. Every nonnull
Sprite target is metadata class213 and belongs to the exact native Sprite catalog.

Every referenced GameObject is independently checked as original class1, fully decoded
and inverse-byte-equal. Its literal serialized name, original whole-object hash,
active-self/layer and metadata-qualified Transform/RectTransform candidates accompany
the renderer. This validates **identity**, not semantic art roles or live instances.

Source is **252 gzip JSONL shards of250 records** (last65), **14813405B total**.
These are new branch-owned byte witnesses, not a reformat/re-export of peer trees.
To obey the per-commit budget, source bot pushed four commits, each measured below4MB:

| Source commit | Files | Sum of new file bytes |
|---|---:|---:|
|3d76fb009|68|3952354|
|ccb6e42f2|67|3967760|
|3b4cf4d72|67|3940234|
|c2d6b08bc|51|3036776|

Fetched fast-forward only. Index committed last; no skip-ci, reset, rebase or peer import.
Each shard has its own compressed SHA/row count/first-last identity. The reverse artifact
is compact: renderer IDs are grouped by file; full proofs remain addressable in shards.

Original ZIP members stream to scratch disk. Bundle stays compressed/mmap-backed with
frozen#6 <=16 decoded blocks (each<=2MiB). Metadata is one SerializedFile at a time,
<=32MiB prefix; lookup/cache tables live in SQLite with4MiB page cache. One renderer and
one GO are decoded at a time; output flushes250 rows. No entire Graph, full decoded
atlas bundle, all2185 Sprite geometry fixture, managed SDK expansion or raised budget.

## Captured-source union: overlap checked, not double-counted

Raw98 initially contains **19440** SpriteRenderers and raw102 **8179**. Their union is
**26452**, not the sum and not the native total. Every overlapping captured native owner
hash agrees with fresh original recovery; **25998** captured nonnull `.m_Sprite` edges
agree with the fresh native PPtr. The remaining captured native renderers have null Sprite.

The disk-backed raw98/raw102 union measures:

- **173685 unique captured objects**; **11753 same-hash/type object overlaps**.
- **32330 unique captured Sprite edges**; **3245 same-pointer/target edge overlaps**.
- **805 indexed GameObject root aliases** (UI/resource kinds retained, not merged by name).
- Every captured Sprite target record that overlaps the native catalog has the same
  original object hash. Any object/edge/native disagreement raises; no repair-to-peer.

References are deliberately separated:

| Class/category | Unique fields | Treatment |
|---|---:|---|
| SpriteRenderer `.m_Sprite` |25998|Cross-check against complete original census, not counted twice|
| MonoBehaviour Sprite fields |3909|Captured serialized component references, class + exact field path retained|
| SpriteMask |81|Captured serialized component references, not active mask verdict|
| AnimationClip Sprite mappings |892|**Mapping, not active selection/playback**|
| SpriteAtlas memberships |1450|**Not usage**, excluded from “has scoped reference” coverage|

Captured MonoBehaviour/native header GameObject values override generated-header values
where present. FileID→external target qualification is exact; bare pathID collisions,
ambiguous parenting, same-name guesses or a default prefab assignment are not accepted.

### Exact parent/root context, with missing coverage preserved

Native GO hashes are compared to captured GOs where they overlap. Parent traversal uses
only captured Transform/RectTransform `m_Father` PPtrs and typed GO links, not object names.
Cycles, wrong GO links, hash disagreement and depth failures are explicit/rejected.

| Native renderer context status | Count |
|---|---:|
|Complete captured parent chain|19263|
|Partial captured chain|7189|
|Captured transform absent|36363|

Thus **36363 native renderers were outside these captured owner closures**, despite
fresh renderer/GO bytes being recovered. Do not manufacture missing parent/root context.
Root aliases can be attached directly only when their exact GO identity matches.
An association to `prefabs/players/...` means a serialized root/capture relationship,
not a live spawned ship, its main sprite, or an art semantic label.

## Practical probes, including a known closed#5 anchor

Sprite **`resources.assets:3564`, original name `Panel_Info`**, has **14 native renderers**:
level2:5739/5765 and twelve resources-file owners. Exact level2:5739→GO1414,
literal **`Border_Info`**, renderer SHA
`8576980d7a2c38514af83d6a5384c5721306305fb0e873adbe41347d7b6614c4`.
This independently reconnects the frozen#5 sliced root to the exact original Sprite;
it does not regenerate or change the sliced model.

The artifact also contains original Sprite name **`1`**, resources:2229, with56 native
renderer references. Two specific owners546173/565907 associate with captured root
resources:185018 /resource key **`prefabs/players/player_10019`**. This **does not** label
Sprite`1` as “ship10019”: it is a precisely scoped relation and the meaning remains null.

```sh
# Exact reverse Sprite identity (no name/PID-only fallback):
python3 -m tools.verify.l3_geometry_8141386a_consumers \
  --sprite-file resources.assets --sprite-id 3564

# One actual native owner proof, fresh literal GO and raw shard locator:
python3 -m tools.verify.l3_geometry_8141386a_consumers \
  --renderer-file level2 --renderer-id 5739
```

The **288** no-reference rows remain queryable with
`NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED`. Future closure
requires an original census of other consumer classes/asset fields and/or validated
additional captures, not a guessed name join. Legacy55584 UI exports with zero scoped
PPtrs cannot become exact-identity proof by matching names. Runtime use/instantiation/
world or pixel bounds/render remain unobserved and outside this static-only lane.

## Performance and disclosed lineage

Actual standalone local reverse-join builder: **32832KiB peak RSS /26.042693893999967s**,
deterministic output SHA match. `build-performance-local.json` SHA
`1fa97694d84b77658797dbe0e77f158e977843f0ab5c8c36ef759ce96db55fcb` pins measured code and
output. **Not source-CI/whole-suite memory**; no measured original recovery RSS claimed.

Lineage: shared native Sprite-geometry capture + frozen#6 original hash corroboration;
ef111/110 framing; own bounded compressed reader; native TPK schemas/std109 Reader;
frozen own#8 inverse writer; shared raw98/raw102 captures and indexed roots; new own
SQLite union/reverse join. **Not clean-room schema discovery, native engine execution,
Unity TypeTree readback or render approval.** Original source hashes strengthen this
specific census, not every other consumer class or all captured hierarchy completeness.

## Verification / handoff boundary

- Source checkpoint: **8focusedPASS/0.338s;1518fullPASS/337.870s** (not final science).
- New report118 regression tests: **22PASS/28.764s** before final combined/full run.
- Final combined focused: **161 PASS /64.114s** (closed#4–8/support +22new118).
- Final full discovery: **1532 PASS /370.452s**, complete log ends `OK`.
- Same-report live needles: **APKD1 123/107; AI1 (139,142136,142,138,42,81); RD1 41/0**; README refresh/check **0 drift**.
- **Scoped historical-support209/0/2** vs current unscoped **163/25/23(exit1)**, no new failure IDs versus frozen160/27/24; exact per-claim/per-group evidence retained.

`verification-118.json.gz` + four full compressed logs preserve frozen160/27/24,
current unscoped diagnostic and explicitly scoped historical-support209/0/2, with
per-claim/per-group/snapshot evidence. **Not all-current-ef/scientific/runtime acceptance.**
Local test counts are not independently extracted CI test counts. Scientific/report
code must be pushed/literal-remote-confirmed/exact-head GREEN before PR12 HANDOFF;
actual CI IDs belong to the post-push handoff and separate CI record. PR15 bridge gate
skip is not runtime evidence.

Closed#4–#8 reports/artifacts/pinned code/verification receipts stay byte-unchanged;
#8 actual exact-head CI is now retained as immutable history, not regenerated for new
needles. Protected3 unchanged; no main/spec/peer/revoked-branch push/merge/self-ACK.
Shared changes are only same-report live3needles/import hashes and own scoped118 gate/
tests. New source shards are required original byte evidence in small commits, not
broad formatting churn or duplicated peer-tree imports.

Reproduce with bounded inputs:

```sh
python3 -m tools.verify.geometry_8141386a_consumers_sources --check
python3 -m tools.verify.l3_geometry_8141386a_consumers --check
python3 -m unittest tests.test_geometry_8141386a_consumers_sources tests.test_geometry_8141386a_consumers -v
python3 -m tools.verify.geometry_8141386a_history
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
```
