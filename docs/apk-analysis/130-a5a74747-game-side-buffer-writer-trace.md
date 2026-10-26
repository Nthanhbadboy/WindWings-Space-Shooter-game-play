# Game-side buffer-writer trace — phase 1

**Scope:** PR12 round 79 `#27-GS` phase-1 claim. Static analysis only. This report traces Assembly-CSharp / IL2CPP control calls and tests whether the available game-side evidence reaches the native pose, clip, or previous-buffer inputs used by native reports 114–120. It does **not** enter AI-1's `libunity.so` FDE lane, perform runtime readback, or make geometry/render claims.

## Result

**Disposition: `NO_DIRECT_GAME_SIDE_BUFFER_WRITER_PROVEN / ANIMATOR_CONTROL_CALLS_IDENTIFIED`.** The inspected game-side methods issue `Animator.SetTrigger` calls. Those are statically evidenced animation-control requests, not stores to the native node's clip blob, pose output, cache, or previous-clock fields. The strongest resolved path ends at the Unity `Animator.SetTrigger` API. The following edge—from that API/controller state into the native node buffers discussed by reports 114–120—remains unresolved.

This is a bounded result, not a proof that no such writer exists anywhere in Assembly-CSharp. The main call inventory is the existing 272-method, direct-call-only `animation-audit/native-calls.json` set plus the tracked raw ASM files containing direct branches to the known `Animator.SetTrigger` RVA. It does not represent a whole-program indirect-call graph. No runtime work was performed.

## Confirmed game-side control path

`dump.cs.gz` identifies `Boss_AttackPhases` as TypeDefIndex **2045**. Its serialized `Animator` field is `animators` at managed object offset **`0x48`**. The same type declares:

| Game-side method | Dump anchor | Static evidence |
|---|---:|---|
| `Boss_AttackPhases.CallMixAnimation(string anim, Action callback)` | RVA `0x152E7EC` | Raw ASM checks `this+0x48`, moves the `anim` argument into the call argument register, then branches at `0x152E880` to `Animator.SetTrigger` (`0x27583B0`). |
| `Boss_AttackPhases.OnGunDie(GameObject go)` | RVA `0x1532390` | Raw ASM loads `this+0x48`, loads a string object from a static slot, and branches at `0x15326D0` to `Animator.SetTrigger` (`0x27583B0`). The literal's value is not resolved here. |
| `Boss_AttackPhases.<IEAttackRound1>d__13.MoveNext()` | TypeDefIndex 2042; RVA `0x1532BA8` | Raw ASM calls `CallMixAnimation` at `0x1532D28` and has a direct `SetTrigger` call at `0x1532F74`. |
| `Boss_AttackPhases.<IEAttackRound2>d__14.MoveNext()` | TypeDefIndex 2043; RVA `0x153305C` | Raw ASM calls `CallMixAnimation` at `0x15331DC` and has a direct `SetTrigger` call at `0x1533428`. |
| `Boss_AttackPhases.<IEAttackRound3>d__15.MoveNext()` | TypeDefIndex 2044; RVA `0x1533510` | Raw ASM calls `CallMixAnimation` at `0x1533778` and has three direct `SetTrigger` calls at `0x1533978`, `0x1533ABC`, and `0x1533BA8`. |

The API declaration is `UnityEngine.Animator.SetTrigger(string name)`, TypeDefIndex **10666**, RVA **`0x27583B0`**. The disassembly therefore supports a concrete C#-side control edge: the boss attack component (through its `Animator` reference) requests trigger changes. It does **not** show a C# assignment to native `node+0x118`, `+0x128`, `+0x130`, `+0x1D0`, `+0x60`, or `+0x178`.

`native-calls.json` contains seven direct `Animator.SetTrigger` calls in the five method rows above (three are in the round-3 iterator). The file explicitly labels itself provisional and direct-call-only. A normalized-address scan of tracked raw ASM found 13 unique direct `bl` callsite RVAs to `0x27583B0`; six further sites are in `GP_Starter.<StopLoopFxStart>d__9.MoveNext`, `Board_Maps.<SetProcessBattlePass>d__160.MoveNext`, `Tut_Settings1.<Start>b__11_0`, `Board_Players.SetPopUnlock`, `Board_Home.CheckGoodDealButtonStates`, and `Board_Drones.SetPopUnlock`. Mirrored ASM copies are deduplicated by callsite address in the companion artifact. These additional sites are also API-control calls, not buffer writes.

## Candidate methods not promoted to traced writers

The metadata dump also declares:

- `FunPlayAnimation.OnClick()` — TypeDefIndex 450, RVA `0x15C4860`, serialized `Animator` field at `0x20`.
- `UIShowAnimation.OnEnable()` — TypeDefIndex 990, RVA `0x133F0C8`; `UIShowAnimation.PlayAnimation()` — RVA `0x133F184`; serialized `Animator` field at `0x20`.

These declarations identify plausible animation-control wrappers, but their method bodies/call sites are not present in the inspected direct-call inventory. They are not counted as confirmed `SetTrigger`, clip, clock, or buffer writers.

The dump also declares `Animator.Play` overloads (RVAs `0x2758970`, `0x2758980`, `0x2758A10`) and `Animator.set_speed` (RVA `0x2758924`). No direct branches to those wrapper RVAs were found in the searched tracked raw ASM corpus. That limited negative search does not rule out indirect calls or callsites outside the corpus.

## Native consumer boundary and unresolved edges

The peer native reports 114–120 (read-only peer tip `f58d0ebbb1f26bfc8992c4207cb8f051cb639f6b`) describe native-side inputs including node `+0x118` (clip blob), `+0x128` (cache), `+0x130` (output holder), `+0x1D0` (clip pointer), and current/previous clock fields `+0x60` / `+0x178`. Those reports provide native consumer-side context, not game-side provenance:

1. No pointer/dataflow edge was recovered from a `Boss_AttackPhases` `Animator` reference or `SetTrigger` string to the native node or its clip blob.
2. No Assembly-CSharp method in this evidence slice was shown storing the node's clip pointer, output holder, cache, pose, or previous-time fields.
3. The Unity wrapper metadata supplies API signatures/RVAs, not the native implementation or its internal buffer writes. Following that implementation would cross the excluded `libunity.so` lane.
4. Existing serialized controller/clip inventories are separate static evidence. For example, controller graph path ID 1856 (`Body 1`, prefab root `Boss-37004`) lists parameters/states and clip links, but the inspected records do not bind that graph to this exact `Boss_AttackPhases.animators` instance or connect it to the native node fixture. No trigger-to-clip-to-buffer edge is asserted.
5. Native 118's prepared current-only/no-pose fixture, native 119's second-phase prerequisites, and native 120's synthetic service/queue/chunk constructor remain harness/native-side evidence. None establishes original game-side creation, caller, or writer provenance.

Accordingly, pose/clip/previous-buffer production remains **unresolved** in this phase. The positive finding is limited to game-side trigger-control calls. It must not be restated as a pose application, sampled buffer write, previous-clock writer, runtime parity, or evidence that the prepared native fixture originated in the game.

## Next static steps (outside this phase-1 finding)

- Expand callsite coverage beyond the 272-method direct-call set and the currently tracked raw ASM hits; preserve indirect-call uncertainty.
- Trace serialized component ownership for the relevant boss Animator/controller and compare parameter names only where a component-to-prefab binding is evidenced.
- Continue the broader `#27-GS` tasks separately: game-side bootstrap/callers for the prepared service/queue/chunk and C# clock/control writers. Do not merge those into the present buffer-writer claim without new evidence.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_buffer_writer_trace.json.gz` records the native-consumer boundary, API/method anchors, normalized direct-call inventory, explicit unresolved edges, and SHA-256 pins for the dump, call inventory, controller/clip context, and raw ASM sources. The normalized matcher lowercases target addresses before comparison, so `0x27583B0` and `0x27583b0` are treated as the same target. The artifact preserves the direct-only/provisional coverage warning. No device, emulator, Frida, runtime probe, or `libunity.so` FDE analysis was used.
