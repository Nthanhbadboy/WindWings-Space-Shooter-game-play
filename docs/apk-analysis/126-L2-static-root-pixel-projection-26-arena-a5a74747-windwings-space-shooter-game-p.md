# 126 — #26 bounded static-root / pixel-projection evidence — arena/a5a74747-windwings-space-shooter-game-p

## Claim and result

PR12 #26 was claimed in comment `6415498086`. This report joins the exact serialized `Board_Pause` resource root and the `Popup_QuitMissions` template-local transform chain to the pinned initial-scene renderer and camera/context inventories.

**Result: bounded static evidence; `pixel_bounds = null`, `rendered = false`.** The available inputs establish a serialized `resources.assets` template, but do not join it to a particular `level0`–`level3` scene instance, placement override, or camera. Five serialized cameras exist in the four scene contexts; none is bound to this template in the inspected inputs. Choosing one would be a guess.

This is a scoped non-observation in the captures enumerated below. It is **not** proof that the template is absent from every scene/bundle, that runtime code never instantiates it, or that it is globally unreachable. No screenshot, redraw, device/session, runtime readback, or render approval was used.

## Exact template root and PPtr/transform chain

The pinned `reverse-engineering/raw/ui/Board_Pause__212696.json.gz` source identifies class/root `Board_Pause`, root path ID **212696**, serialized file `resources.assets`, **235** hierarchy nodes, and serialized root inactive. The matching local Transform-tree row is `439142 → GameObject 212696 → father 0`.

`Popup_QuitMissions` joins under that root as follows:

| Object | Serialized file | Path ID | Link / pose | Serialized active |
|---|---|---:|---|---:|
| `Board_Pause` Transform | `resources.assets` | 439142 | GO 212696; father 0 | 0 |
| `Popup_QuitMissions` Transform | `resources.assets` | 425352 | GO 57508; father Transform 439142; local `(0, 0, −2)` | 0 |
| `Popup_QuitMissions` GameObject | `resources.assets` | 57508 | class `Popup_Notices`; Animator 495980 is attached to the same GO | 0 |

The `Popup_Notices` template extract contains 19 nodes and agrees on the inactive root/local pose. Raw object chunks independently join Transform 425352, Animator 495980, and `Popup_Notices` MonoBehaviour 644901 to GO 57508. These are serialized template-local facts; they do not establish instantiation, runtime activation, or engine readback.

## Explicitly inventoried scene references

The pinned `scene-sprites` capture inventories initial `level0`–`level3` SpriteRenderer roots (Menu, Home, Game, EndGame), their recorded ancestor/linked-object closure, and raw links: **5,698 object records / 10,279 link rows**. Within that exact captured object-and-link set, the audit found **0** exact `Board_Pause` name / path-ID `212696` matches, **0** direct PPtr edges to `data.unity3d/resources.assets:212696`, and **0** captured `PrefabInstance`-typed rows.

The separate pinned `scene-context` capture contains **122 object records / 194 link rows** and five Camera objects in those four level files. The camera inventory is:

| Scene file | Camera GO / component | Name | Serialized orthographic size | Normalized viewport | Transform chain path IDs (leaf→root) |
|---|---|---|---:|---|---|
| `level0` / Menu | 1 / 58 | Main Camera | 9.600000381469727 | `(0,0,1,1)` | 31 |
| `level1` / Home | 3 / 39 | Main Camera | 9.600000381469727 | `(0,0,1,1)` | 22 |
| `level2` / Game | 279 / 3975 | Game Camera | 9.600000381469727 | `(0,0,1,1)` | 2385 → 2637 → 2215 |
| `level2` / Game | 777 / 3976 | Main Camera | 9.600000381469727 | `(0,0,1,1)` | 2824 → 2215 |
| `level3` / EndGame | 18 / 1308 | Main Camera | 9.600000381469727 | `(0,0,1,1)` | 730 → 717 |

Each camera joins its own serialized level context and has a null target texture in the pinned contract. No camera has a template-instance link in the artifact. A normalized viewport rectangle is not a pixel-resolution or camera-arbitration authority.

**Scope caution:** these are renderer/context closures, not a complete all-class `level0`–`level3` GameObject or PrefabInstance census. In particular, the capture limits say Transform children and other GameObject components are retained as raw pointers rather than recursively followed. Therefore the zero-match result above is strictly limited to the inventoried rows and links; it is not an all-bundle or repository-wide absence proof. Resources/sharedassets prefab renderer roots are also not expanded as scene instances by the scene-sprite contract.

## Projection disposition

The preceding #12 artifact already recorded `pixel_bounds = null` because the selected root is a `resources.assets` template rather than an attached `level0`–`level3` instance. This audit independently confirms the same boundary using the current pinned scene renderer/context captures. The output preserves:

- `pixel_bounds = null`
- `rendered = false`
- `runtime_readback = NOT_OBSERVED`
- no chosen camera and no guessed placement/viewport transform

Additional pixel projection would require an explicit scene-instance/parent/placement authority, an associated concrete camera path, and a destination pixel-resolution/render-target context. No such join was supplied by the inspected sources.

## Source provenance and pins

Raw UI, scene-sprites, scene-context, and selected L3 object sources (**68 files / 732,176 bytes**) were read byte-for-byte from peer branch `arena/ef6b75ef-windwings-space-shooter-game-p` at commit `33cdc61a912c006a6169583dfad444841033df7a`, then copied to this branch. The local `reverse-engineering/raw/typetrees/transform-tree.tsv.gz` was used as a separate, current-branch corroboration. The source capture index lists the package entries and hashes, but the original APK/package was **not** independently retrieved or decoded during this #26 audit.

Primary pins:

| Input | SHA-256 |
|---|---|
| `reverse-engineering/raw/ui/Board_Pause__212696.json.gz` | `160b13048ac3ed8e3554da5996b25ed4a4b2977c5bb2a4f2cdc538595fb877ac` |
| `reverse-engineering/raw/ui/Popup_Notices__57508.json.gz` | `b2a7ceb9ed49ab88e774ca2ea300fd29227c9afefed2ef9bf0cf56fa299aaf87` |
| `reverse-engineering/raw/typetrees/transform-tree.tsv.gz` | `30624c3e69a64559d0b790d48a6aa06db725edbcb9687e1457e72e7311c76ae2` |
| `datas/scene_sprite_contract.json.gz` | `6f46fe33303aac2adbe16cbd9889568fa7e0d9ce3439d75cef6c6bc404696095` |
| `datas/scene_render_context_contract.json.gz` | `312f71154e6c17469a37c2fc9063ea46c600d381bc7cd3a884a9842a4fe3b8f3` |
| prior #12 artifact `datas/l3_composition_viewport_engine_transition_12.json.gz` | `5fc9fd3673949948a9535ce119b8ac24334c428c96a054b1858346df92294f20` |

The artifact embeds the SHA-256 and byte size for all **72** selected inputs (including every raw capture shard and links file); manifest SHA-256: `e25ebebef425f9bbafd9d7887c8097231c195fb7f3b8f0a75283ef38465748c8`.

Artifact: `datas/l2_a5a74747_26_static_root_projection.json.gz` — **7,305 bytes**, SHA-256 `e0fe9b1aea3926df3d66046873ccc103aa2950b1b2dc2b4d25e717c254daade9`.

Builder: `tools/build_l2_a5a74747_26_static_root_projection.py` — SHA-256 `977e2ada7afcc6ee32c847cb34641df912da9e1a1c53d20b9ec8d41d8ccb8aab`.
Tests: `tests/test_l2_a5a74747_26_static_root_projection.py` — **8 tests**, SHA-256 `a275b472f4d856dde2e8bb27e15365aba264a0800903fd5caf56eb81b50676cd`.

Rebuild / verify:

```bash
python3 tools/build_l2_a5a74747_26_static_root_projection.py
python3 tools/build_l2_a5a74747_26_static_root_projection.py --check
python3 -m unittest tests.test_l2_a5a74747_26_static_root_projection -v
```

## Limits

- Static serialized evidence only; no screenshot, redraw, device/session, runtime readback, or render.
- Zero matches are limited to the pinned renderer/context object-and-link records, not every serialized object class, bundle, dynamic load, or runtime instance.
- Camera fields are separate scene snapshots; no camera was assigned to this asset template.
- No pixel bounds, visibility, native runtime layout, viewport arbitration, or rendered-frame equivalence is claimed.
