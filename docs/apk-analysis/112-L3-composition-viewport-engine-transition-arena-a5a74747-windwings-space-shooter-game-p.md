# 112 — L3 composition/viewport + engine-transition evidence — arena/a5a74747-windwings-space-shooter-game-p

## Claim and disposition

- PR12 claim #12: comment `6412753449`; claim preceded this batch.
- `REPLICATION`: independent join of the checked-in hierarchy, motion, animation-binding, Animator-program, transition-model, composition, and frame artifacts, with a raw transform-tree cross-check from the known raw branches.
- Outcome is **bounded/partial**: a template-local composition state and serialized transition path are reproduced. A runtime scene placement and active camera are not established, so this report does **not** project viewport pixels or claim a rendered frame.
- Source branch tip at start: `fe247fb8c586161284130d044db8af33dd6cacdd`.

## Correcting the earlier #12 blocker

The earlier comment `6411194637` described the parent of `Box_Gift (7)` as “GO 270123” and said it was missing from the node index. That is a type/identity error: **270123 is a Transform**, owned by GameObject **226561** (`Parent_Rewards`). The current checked-in `nodes-005.json.gz` contains the complete chain:

`Transform 277770 / GO 96185 Box_Gift (7)` → `270123 / GO 226561 Parent_Rewards` → `339888 / GO 62705 Parent` → `417314 / GO 120127 Pack_Spec (2)` → `369060 / GO 139738 Board_Players` → root.

The three known raw branches were all searched before making an availability statement. Under each `reverse-engineering/raw/` tree, every tracked file was enumerated, gzip files decompressed, and literal `270123` searched. Results: `arena/a5a74747` — 857 files / 280,733,641 decoded bytes / one matching path; `arena/ef6b75ef` — 58,858 files / 4,364,634,182 decoded bytes / 20 matching paths; `arena/20330d0e` — 857 files / 280,733,641 decoded bytes / one matching path. Their transform-tree rows confirm the chain above. This is a correction of the earlier blocker, **not** a repository-wide missing-artifact assertion.

## Popup_QuitMissions: template-local state joined to the Animator graph

The second concrete chain is `resources.assets` root view 10 (`Board_Pause`, GO 212696; 235 nodes) → `Popup_QuitMissions` (GO 57508, Transform 425352). The serialized local transform is `(0, 0, −2)` under the `Board_Pause` root at identity; both the popup and the Board_Pause asset root are serialized inactive. The full local chain is present in the artifact and independently agrees with raw transform-tree rows `425352 → 439142 → 0`.

Animator **495980** on GO 57508 references controller **1974** (`Popup_Network`, reused controller identity). The serialized default state is **Appear** (state 0, clip 1572, 0.5 s). The graph has an AnyState transition to **Hide** (state 1, clip 1573) gated by trigger `Hide`, with serialized duration 0 and no exit-time gate. The independent transition-model artifact agrees on the controller/default state. This is graph/model evidence, not proof that Unity scheduled or played either state.

The two Appear bindings resolve uniquely for this Animator: `Parent` local scale (`Transform`, attribute 3) and `Cover` `SpriteRenderer.m_Color.a` (attribute 304273561). Serialized-curve arithmetic samples are:

| Clip time | Parent local scale | Cover alpha | Basis |
|---:|---:|---:|---|
| 0.00 s | `[0, 0, 1]` | `0` | exact serialized stream record |
| 0.25 s | `[1.0303999185562134, 1.0303999185562134, 1]` | `0.8313725590705872` | cubic segment from 0.05 s; exact alpha key; FP32 store |
| 0.50 s | `[1, 1, 1]` | `0.8313725590705872` | exact scale record; hold-last alpha model policy |

These are **serialized curve/model samples**, not Unity readback values. In particular, the 0.50 s alpha uses the declared hold-last curve policy; it is not asserted as the actual engine state.

## Viewport boundary

The selected `Board_Pause` root and `Popup_QuitMissions` are in `resources.assets`, i.e. a serialized UI asset/template chain. The current joined artifacts do not attach that template to a specific level-scene instance and camera. The composition contract lists 6 camera references, while the scene context contains 5 serialized Camera objects; they belong to separate `level0`–`level3` contexts. Choosing one as the runtime camera for this template would be an unsupported assumption. Therefore `pixel_bounds = null`, `rendered = false`, and viewport projection remains open until an explicit instance/placement authority and camera context are supplied.

No screenshot or redraw was used. Model ≠ readback ≠ render.

## SHA-256 pins

Artifact: `datas/l3_composition_viewport_engine_transition_12.json.gz` — **5fc9fd3673949948a9535ce119b8ac24334c428c96a054b1858346df92294f20** (5,084 bytes).

Builder: `tools/build_l3_composition_viewport_engine_transition_12.py` — **790db6c172a5d8b3b0ac749b7fb1cd7f92ac004658df2b36d615605825bfd3c8**.

Current-branch inputs (all pins are also embedded in the JSON artifact):

| Input | SHA-256 |
|---|---|
| `datas/l3-scene-chains/nodes-005.json.gz` | `eb16956d36f8fedbc587735e7c26c9e77512bc66e64796b0da985e3d906fa477` |
| `datas/l3-scene-chains/nodes-007.json.gz` | `2e5070efc3edbbf414fb76a40b81d06eee450884b99001cd68c1a29f36397c94` |
| `datas/l3-scene-chains/motion-000.json.gz` | `b2036fe60a7bfef7fc1e8324f4c33ccf4d597ba991c5e7422bda16e2c666fa7c` |
| `datas/l3-scene-chains/animation_bindings-006.json.gz` | `81e6f32e7f355c6e24668da03f555e01ad335cd023a4f7c7f996f2aaed66bd5f` |
| `datas/l3_scene_chains.json.gz` | `3be47092c0967c40c5f9abf1ec28eeba401bb1bf2cf0bec003a627e982d62eeb` |
| `datas/l3_animator_programs.json.gz` | `114d8f442e07a0733b0a68538ce71c78288cb2c36565bb3ec186f17dd032cd44` |
| `datas/l3_transition_model.json.gz` | `b02b766ceb15ba6b363457a727c08c027caf36568528e44d745d51aea5a990e9` |
| `datas/l3_composition.json.gz` | `d54eb354fc42a8419c1e71fe52be33c5461dec695385fc4deb2a6399c900bae7` |
| `datas/l3_frame_cases.json.gz` | `daf9f0d335863635ec577bdbe1b1ca122bb272a7668dc474d9be0157fad05016` |
| `datas/l3_driven_props.json.gz` | `ed3f51739a89df3a0b2e13e36e39d0c4210e00551dc9920df2581db7f68b2310` |

Raw-source corroboration from `arena/ef6b75ef` commit `d7e718cfb5466fd7bd03e2d8357400d744b108cb`:

| Raw input | SHA-256 of Git blob bytes |
|---|---|
| `reverse-engineering/raw/typetrees/transform-tree.tsv.gz` | `92b2eef703c71593833f32e390256a5a318e4121749d523eec2fefcaf4f0aac6` |
| `reverse-engineering/raw/ui/Board_Pause__212696.json.gz` | `160b13048ac3ed8e3554da5996b25ed4a4b2977c5bb2a4f2cdc538595fb877ac` |
| `reverse-engineering/raw/ui/Popup_Notices__57508.json.gz` | `b2a7ceb9ed49ab88e774ca2ea300fd29227c9afefed2ef9bf0cf56fa299aaf87` |
| `reverse-engineering/raw/l3-chain/objects-0353.jsonl.gz` | `368ab3b174848927cd4ffb405b8745cef1da2fa13ece6a71a35a8fb520db393f` |
| `reverse-engineering/raw/l3-chain/objects-0425.jsonl.gz` | `fdfba84b9068e4cda7270707bc10069a499ee32af6c02051543375c8bc30a2fe` |
| `reverse-engineering/raw/l3-chain/objects-0601.jsonl.gz` | `4e51f0e55d179b26d0b7dacc37bc693a99d9991bbdb27e7971b044aa8b29e195` |
| `reverse-engineering/raw/l3-ui-native/native/Popup_Notices.json` | `ef706d5b9aaf71364204152fd5322ece348947c9d499ee5e9dfee33149479c95` |
| `reverse-engineering/raw/l3-ui-native/method-bytes.json.gz` | `e25b39d8293b2d2c45b90d39b697b1c57b5a876f82c0820330a9be65d0dde8ed` |

Verifier tests: `tests/test_l3_composition_viewport_engine_transition_12.py` — 6 tests, SHA-256 `3e7a3b3518153a444970fd4fcc27da442a87ef869700b839bc7615473d24ffa8`. Rebuild with `python3 tools/build_l3_composition_viewport_engine_transition_12.py`; run with `python3 -m unittest tests.test_l3_composition_viewport_engine_transition_12 -v`.
