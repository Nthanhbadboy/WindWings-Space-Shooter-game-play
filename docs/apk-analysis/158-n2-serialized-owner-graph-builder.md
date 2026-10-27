# N2 — bounded serialized owner for the `Body 1` controller graph

**Assignment:** PR12 comment `6424382601`, N2 · **Evidence mode:** serialized/static only  
**Disposition:** `SERIALIZED_CONTROLLER_OWNER_IDENTIFIED / GRAPH_BUILDER_INVOCATION_LINK_UNPROVEN`

## Scope

This is the serialized-owner half of the open controller-state question noted by report 130. The native range `0x6cf7b4..0x6cff44` is referenced only as the assignment's identifier; this report does not inspect or interpret `libunity.so`, FDE, native constructors, or runtime behavior. The allowed evidence is the repository's serialized Animator/controller export and hierarchy/owner metadata.

## Owner result

The normalized serialized animation inventory contains one Animator component record whose `m_Controller` PPtr targets controller path ID `1856`:

| Object | Bounded identity | Serialized evidence |
|---|---|---|
| Controller graph | `Body 1`, path ID `1856`; controller inventory assigns prefab root `Boss-37004` | `controller-graphs.json.gz` entry `path_id=1856`; matching owner row in `enemy-clip-links.json.gz` |
| Owning component instance | Unity `Animator`, component path ID `493584` | `enemy-clip-links.json.gz` animator row; corroborated by `animator_map.csv.gz` |
| Component's GameObject reference | PPtr `{m_FileID: 0, m_PathID: 76852}` | `enemy-clip-links.json.gz` `gameobject_ref`; Animator map gives GameObject path ID `76852` |
| Controller reference | PPtr `{m_FileID: 0, m_PathID: 1856}` | `enemy-clip-links.json.gz` `controller_ref` |
| Hierarchy | GameObject `76852` has Transform path `364641` → parent Transform `305729` → root Transform `305711`; root GameObject path `73241` is named `Boss-37004` | `transform-tree.tsv.gz` and `prefab-roots.csv` |

The cross-check is unique **within the bounded 154-Animator inventory**: exactly one row references controller path `1856`, and the controller graph inventory has exactly one entry for that ID. Its metadata names the graph `Body 1` and lists `Boss-37004` as its prefab root. This establishes a serialized owner chain for the controller graph, not runtime use.

The normalized PPtrs record `m_FileID=0` and the target path IDs, but do not preserve the full serialized-file basename for this prefab/controller pair. The result therefore records the PPtr and component/instance paths rather than guessing an asset filename.

## Boundaries and remaining join

- Report 130's managed `Boss_AttackPhases.animators` field is a separate code-side reference. The checked serialized records do **not** bind a `Boss_AttackPhases` component instance/path to Animator component `493584`; no such field-to-instance edge is claimed.
- The available serialized exports identify the owner of controller path `1856`, but do not show that native range `0x6cf7b4..0x6cff44` executed against this particular controller instance. That address-to-instance construction link remains unproven at this permitted boundary.
- This does not establish a trigger-to-state/clip edge, native buffer/pose writer, callback execution, playback, runtime parity, or any live-DPS result. Boss-specific evidence is not transferred to another prefab.
- No native/FDE artifact, `libunity.so`, runtime probe, emulator, or AI-1 raw lane was inspected. `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Provenance

The companion receipt is `datas/l3_a5_n2_serialized_owner_graph_builder.json`. It pins the serialized animation-owner/controller exports, the GameObject/Transform hierarchy metadata, and the report-130 game-side context separately. The raw pins exclude native/FDE files; inventory counts and bounded uniqueness checks are reproduced in the receipt.
