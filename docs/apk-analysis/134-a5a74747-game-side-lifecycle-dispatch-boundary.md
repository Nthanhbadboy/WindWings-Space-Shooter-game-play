# Game-side lifecycle and virtual-dispatch boundary — phase 5

**Scope:** PR12 `#27-GS` phase-5 claim `6419867990`, a bounded static follow-up to report 133. It resolves the available IL2CPP class/method metadata, selected lifecycle declarations, virtual override slots, the serialized script-link slice, and direct branch references to the unresolved boss/tutorial entrypoints. It does not enter AI-1's native lane.

## Result

**Disposition: `CONCRETE_VIRTUAL_OVERRIDES_AND_METHOD_METADATA_PROVEN / ENTRYPOINT_ACTIVATION_UNRESOLVED`.** `Boss_AttackTypes.RegisterEvents()` is virtual slot 4, and the available metadata declares concrete overrides on `Boss19_AttackTypes`, `Boss20_AttackTypes`, and `Boss21_AttackTypes`. `Boss_AttackPhases.StartAttack()` is a separate, non-virtual base method; the three boss phase subclasses override the three coroutine slots, not `StartAttack()`.

This resolves *which managed override would be selected if the relevant virtual method were invoked*. It does not recover an invocation into `StartAttack`, `RegisterEvents`, or `GP_Tutorials.StartTutChangeGameSpeedBoss`. No runtime dispatch is claimed.

## Type and slot resolution

The exact class declarations and method RVAs in `dump.cs.gz` establish this bounded map:

| Type | TypeDefIndex / base type | Relevant method declarations |
|---|---|---|
| `Boss_AttackPhases` | `2045` / `MonoBehaviour` | `StartAttack()` RVA `0x15322AC` (non-virtual); virtual `IEAttackRound1/2/3` slots 4/5/6 |
| `Boss19_AttackPhases` | `2029` / `Boss_AttackPhases` | overrides slots 4/5/6 at `0x152E124`, `0x152E1AC`, `0x152E234` |
| `Boss20_AttackPhases` | `2071` / `Boss_AttackPhases` | overrides slots 4/5/6 at `0x1537FF0`, `0x1538078`, `0x1538100` |
| `Boss21_AttackPhases` | `2083` / `Boss_AttackPhases` | overrides slots 4/5/6 at `0x153A078`, `0x153A100`, `0x153A188` |
| `Boss_AttackTypes` | `2062` / `MonoBehaviour` | virtual `RegisterEvents()` slot 4 at `0x1533CC4`; virtual `Stop()` slot 5 |
| `Boss19_AttackTypes` | `2037` / `Boss_AttackTypes` | `RegisterEvents()` override slot 4 at `0x152F414`; `Stop()` override slot 5 |
| `Boss20_AttackTypes` | `2076` / `Boss_AttackTypes` | `RegisterEvents()` override slot 4 at `0x1539050` |
| `Boss21_AttackTypes` | `2084` / `Boss_AttackTypes` | `RegisterEvents()` override slot 4 at `0x153B0D0` |

The metadata for these exact boss class blocks declares no `Awake`, `Start`, `OnEnable`, or `OnDisable` method. Their method lists expose the virtual override structure but not a lifecycle caller. Unity/native lifecycle dispatch, reflection, delegates, external code, and omitted method bodies remain possible and are not excluded by that observation.

The three serialized `Boss*_AttackPhases` and the exported Boss20/21 `Boss*_AttackTypes` records are the same file-scoped components joined in report 133. The bounded `script-links.jsonl.gz` slice has five matching `m_Script` edges for those component records, but each has `target_class=""`; it therefore does not independently resolve those script asset PPtrs to class names. Boss19's `attackTypes` target remains without a matching `Boss19_AttackTypes` type-tree export.

## Bounded direct-call and body-availability audit

A direct-branch scan over all **139** top-level `reverse-engineering/raw/il2cpp-consts/*.asm.txt` files checked `BL` and tail-`B` targets for:

- `Boss_AttackPhases.StartAttack` (`0x15322AC`);
- base and Boss19/20/21 `Boss_AttackTypes.RegisterEvents` (`0x1533CC4`, `0x152F414`, `0x1539050`, `0x153B0D0`); and
- `GP_Tutorials.StartTutChangeGameSpeedBoss` (`0x14FA54C`).

**Result: zero direct branch references** to those six targets in that bounded corpus. The separate `native-calls.json` inventory also reports zero matching direct-call targets among its 272 entries, but labels itself `PROVISIONAL: direct calls only; aliases retained; no inferred indirect calls`; it is corroboration, not a global call graph.

The tracked raw-ASM corpus contains the base `Boss_AttackTypes` and `GP_Tutorials` files, but no per-type raw-ASM file matching any of `Boss19/20/21_AttackPhases` or `Boss19/20/21_AttackTypes`. Consequently, the six derived classes' declared method RVAs and virtual slots are metadata evidence only here; their individual method bodies and callsites inside those bodies cannot be inspected from this corpus. Existing base-method evidence remains as described in reports 132–133. Indirect `BLR`/vtable calls, Unity event dispatch, reflection, generated/runtime listeners, and missing corpus coverage are outside this direct-branch result.

## Tutorial entrypoint boundary

`GP_Tutorials` (TypeDefIndex `1892`) declares both `Awake()` (`0x14F9BD4`) and `Start()` (`0x14F9C30`), and the public `StartTutChangeGameSpeedBoss()` (`0x14FA54C`). The bounded scan found no direct branch to the public method. Report 133's body-level evidence remains narrower: once that public entrypoint is reached, it calls the coroutine builder at `0x14FA6B8` and proceeds to Unity `StartCoroutine`; that internal path does not establish a caller into the public entrypoint. The provisional persistent-call inventory still has no matching target and excludes dynamic listeners.

## Native boundary and limits

The metadata and object links stop at managed boss/tutorial components. They establish no path to native fixture `116cb40`, no native node or clock binding, and no pose/application edge. This phase makes no runtime playback/readback, parity, live-DPS, geometry/render, emulator, Frida, or `libunity.so` FDE claim and does not modify AI-1's lane. PPtr IDs remain scoped to their exporting file; missing class-name mappings and missing per-type bodies are left unresolved.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_lifecycle_dispatch_boundary.json.gz` contains the exact type/method map, filtered script-link records, per-target direct-branch results, bounded call-inventory cross-check, raw-ASM corpus availability, source SHA-256 pins, and explicit inference limits. It reuses report 133's pinned 139-file ASM source set and adds pins for `dump.cs.gz` and `script-links.jsonl.gz`.
