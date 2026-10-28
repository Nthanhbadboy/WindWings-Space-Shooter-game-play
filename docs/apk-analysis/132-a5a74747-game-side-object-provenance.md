# Game-side object and asset provenance audit — phase 3

**Scope:** PR12 `#27-GS` phase-3 claim, extending reports 130–131 with static joins between managed components, serialized object references, Unity Animator/controller assets, and the tutorial speed UI. This is an asset/object-provenance audit, not a runtime activation claim. It does not enter AI-1's `libunity.so` lane or attempt to identify the native synthetic fixture in a game object.

## Result

**Disposition: `SERIALIZED_ANIMATOR_BINDINGS_PROVEN_FOR_THREE_BOSS_PREFAB_RECORDS / MANAGED_ACTIVATION_AND_NATIVE_JOIN_UNRESOLVED`.** For the serialized `Boss19_AttackPhases`, `Boss20_AttackPhases`, and `Boss21_AttackPhases` records, the inherited `animators` field joins to concrete Animator component records and controller assets under the corresponding prefab roots. Separately, the serialized `GP_Tutorials.tutSettings` references the same GameObject as a `Tut_Settings1` component with a `sliderTimeScale` reference.

These are static object/reference joins. They do not prove that the prefabs were instantiated, that `StartAttack` ran, that a derived coroutine reached `CallMixAnimation`, or that any Animator/controller state was applied to the native `116cb40` fixture. There is still no managed edge to native node clip/cache/output/clock fields.

## Boss attack component → Animator → controller joins

The `dump.cs.gz` declarations identify `Boss19_AttackPhases` (TypeDefIndex **2029**), `Boss20_AttackPhases` (**2071**), and `Boss21_AttackPhases` (**2083**) as subclasses of `Boss_AttackPhases` (TypeDefIndex **2045**). The base owns the serialized `Animator animators` field at `this+0x48`. The exported per-type records, native Animator records, prefab-root table, and animator/controller inventory agree on these three joins:

| Managed component | Serialized component / GameObject | Prefab root | Inherited `animators` PPtr | Animator's GameObject / controller |
|---|---|---|---|---|
| `Boss19_AttackPhases` | component `689448`, GameObject `230427`, `roundStart=1` | `Boss-39019` | Animator `498950` | GameObject `230437`; controller `1807` (`Body`) |
| `Boss20_AttackPhases` | component `634645`, GameObject `150162`, `roundStart=1` | `Boss-39020` | Animator `495696` | GameObject `150160`; controller `1813` (`Body`) |
| `Boss21_AttackPhases` | component `615301`, GameObject `230426`, `roundStart=1` | `Boss-39021` | Animator `498650` | GameObject `230436`; controller `1808` (`Body`) |

For each row, the attack-component PPtr equals an `Animator.path_id` in `native-types.jsonl.gz`; that Animator record carries the listed controller PPtr. `enemy-boss.json` independently groups those Animator IDs beneath the same named prefab roots. The root GameObject IDs are present in `prefab-roots.csv`. Controller graph records resolve the controller IDs to `Body` assets. This is a concrete serialized relationship for these three exported prefab records; it does not bind report 130's separate `Boss-37004` controller record to a `Boss_AttackPhases` component.

### What the code evidence does—and does not—connect

The base `Boss_AttackPhases.StartAttack()` (RVA **`0x15322AC`**) reads `roundStart` at `this+0x50`, selects a virtual entry, and invokes it indirectly with `BLR`. For `roundStart=1`, the first virtual slot is selected; metadata declares this as `IEAttackRound1` (slot 4), with overrides at RVA `0x152E124` (`Boss19`), `0x1537FF0` (`Boss20`), and `0x153A078` (`Boss21`). Thus the serialized values and metadata describe a plausible virtual-dispatch route if `StartAttack` is invoked on these objects.

The base `CallMixAnimation(string anim, Action callback)` (RVA **`0x152E7EC`**) checks the inherited Animator reference at `this+0x48` and calls Unity `Animator.SetTrigger` at `0x27583B0` with the incoming string. The three base iterator bodies call `CallMixAnimation` at `0x1532D28`, `0x15331DC`, and `0x1533778`.

The missing links remain consequential:

1. The bounded tracked raw ASM scan found **no direct `BL` or tail-`B` caller** of `StartAttack` at `0x15322AC`. Indirect, event, reflection, or missing-corpus callers are not excluded.
2. Raw disassembly bodies for the `Boss19/20/21` override coroutines were not found. Their override declarations and serialized references do not show whether those bodies call `CallMixAnimation` or issue other Animator operations.
3. Accordingly, the serialized Animator binding is proven, but the exact route from these three prefab records through `StartAttack` and their derived bodies to `SetTrigger` is not proven as an executed call path.
4. Nothing in these joins identifies the native service/queue/chunk, the native node, or its clip/cache/output/current/previous-clock fields.

## Tutorial speed UI object join

The serialized `GP_Tutorials` component (TypeDefIndex **1892**, component path ID `7123`, GameObject ID `1902`) contains `tutSettings` and `tutSettings2` references that both point to GameObject path ID **634**. The `Tut_Settings1` component record (TypeDefIndex **257**, component `6825`) is on that same GameObject ID at `GP_Tutorials/TutSettings (1)` and has `sliderTimeScale` pointing to path ID `6826`. A second `Tut_Settings1` component record (`6861`) appears at `Board_BeginPlay/Parent/Bottom/Parent_Systems`, GameObject ID `780`, with its own slider reference `6656`.

This asset link complements phase 2: raw callers in `Tut_Settings1` read/write `TimeSlider.SaveSpeed`, while phase-2 evidence separately identifies global Unity `Time.timeScale` writers and the metadata-only `GP_Time` abstraction. The serialized `GP_Tutorials` → `Tut_Settings1` link does **not** establish that this slider writes `GP_Time.timeScale`, Unity's node clock, or any native node field. No `GP_Time` instance binding was recovered in this bounded per-type export.

## Spine candidate boundary

The bounded Spine prefab audit reports three resolved local-PPtr `SkeletonAnimation` components:

| Prefab | Component path ID | GameObject PPtr | Skeleton-data PPtr |
|---|---:|---:|---:|
| `Boss-39001` | `602882` | `163303` | `580611` |
| `Boss-39002` | `664302` | `163883` | `580611` |
| `Boss-39003` | `602881` | `163302` | `580613` |

The audit is explicitly provisional static asset evidence, not proof of runtime playback. `SkeletonMecanim` (TypeDefIndex **8602**) and its nested `MecanimTranslator` (TypeDefIndex **8601**) remain metadata-only candidates: no matching serialized `SkeletonMecanim` record or raw ASM body was found in the bounded sources. The listed Spine prefab components are `SkeletonAnimation`, not `SkeletonMecanim`.

A `Boss_1_Animation` typetree record has a `skeAnim` PPtr with numerical path ID `602882`, matching the `Boss-39001` component ID in the separate Spine-prefab export. Because these are separate per-type exports and same-file PPtr provenance is not pinned here, the number match is preserved as a candidate only—not promoted to cross-file object identity.

## Boundary against native `116cb40`

Peer native reports 120/121 (read-only peer tip `719f6e037`) describe `116cb40` service/queue/chunk state as prepared synthetic fixture inputs. They do not establish a game-side bootstrap caller. The managed object joins in this report stop at Unity components/controllers and tutorial UI; none reaches native node `+0x118` (clip blob), `+0x128` (cache), `+0x130` (output holder), `+0x1d0` (clip pointer), `+0x60` (current clock), or `+0x178` (previous clock).

Therefore the phase-3 result strengthens the **serialized game-side Animator ownership** evidence for three boss prefab records and the tutorial-settings object link, while leaving **runtime activation, derived-method control flow, native bootstrap, node-clock provenance, and pose application unresolved**. It is not runtime parity and does not imply that the prepared fixture originated in the game.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_object_provenance.json.gz` records the object IDs, PPtr/controller joins, metadata/RVA anchors, bounded negative searches, native boundary, and SHA-256 pins for the per-type exports, raw ASM, prior phase reports/artifacts, and supporting animation-audit files. Static-only: no runtime readback, emulator, Frida, parity, live-DPS, `libunity.so` FDE, geometry, or render analysis was performed.
