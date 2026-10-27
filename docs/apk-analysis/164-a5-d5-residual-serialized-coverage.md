# D5 residual — bounded serialized export coverage and unresolved player PPtr

**Claim:** PR12 `6426986645` (after central ACK114).
**Verdict:** `BOUNDED_MISSING — PLAYER OWNER / EXTRA-LIFE REWIRE NOT_BOUND` (evidence level B). This follow-up checks only the captured serialized CSV/TypeTree JSONL export surface. It does not redo reports 79–86, inspect method bodies, or establish runtime behavior.

## Export-surface result

The receipt fingerprints the available **126** `reverse-engineering/scriptableobjects/*.csv` files and **140** `reverse-engineering/raw/typetrees/*.jsonl.gz` files (**231,957** serialized rows scanned). `class-inventory.csv` contains 24 `Player_Attack_N` identities and the `Player_Health` / `Player_Controller` class identities, but those identities are not instance-owner records. Within the pinned export set:

- There is no CSV or TypeTree JSONL file named for `Player_Attack_N`, `Player_Health`, or `Player_Controller`.
- The only captured `GP_Datas` row is `path_id=6767`, `_gameobject=GP_Manager`. Its `player` pointer is `(m_FileID=0, m_PathID=2625)`.
- The TypeTree JSONL set contains **two** records encoding numeric PPtr pair `0:2625`: `GP_Datas.player` (row 6767) and `GP_Tutorials.player` (row 7123). The flat CSV set contains the `GP_Datas` edge. The class-split exports do not retain enough source-asset context to assert both `fileID=0` references resolve to the same object; neither record includes the target owner component.
- The same numeric path ID appears as an **own-row ID** in `Box_Rewards.csv` and `Box_Rewards.jsonl.gz`, in another object/file context. It is not a valid target join for either player pointer. No player component owner is established.
- The exact candidate field keys `countReborn`, `rebornNow`, `maxCountReborn`, and `listRebornUseItems` occur in none of the scanned CSV headers or TypeTree JSONL object keys. This is bounded to these captured exports; it is not a whole-build absence claim.

## Cross-export mismatch found

The flat CSV and TypeTree JSONL representations identify the same `GP_Datas` row (`6767`, `GP_Manager`) and agree on the `player` PPtr, but differ on one exported value:

| Field | `GP_Datas.csv` | `GP_Datas.jsonl.gz` |
|---|---|---|
| `listActiveEnemies` | `[0]` | `[]` |

Do not choose one representation as runtime truth or infer behavior from this discrepancy. It is an export-consistency question, not evidence of an extra-life field or player owner.

## Closure boundary

The captured export surface supports **neither** a concrete `Player_Attack_N`/`Player_Health` component-owner join nor extra-life serialized rewiring. D5’s class-to-static-array join from report 163 remains valid within its stated scope; the residual stays `NOT_BOUND`. To advance it would require a permitted, source-pinned serialized export that carries the target file context and player component chain, plus the relevant serialized lifecycle state. If that source is unavailable, keep the bounded-missing result and do not repeat the closed code/coroutine/receiver inventories.

## Pins and reproducibility

- Receipt: `datas/l3_a5_d5_residual_serialized_coverage.json`.
- Builder: `tools/build_a5_d5_residual_serialized_coverage.py`; tests: `tests/test_a5_d5_residual_serialized_coverage.py`.
- Export-set manifest SHA-256: ScriptableObject CSV set `2ccc90ddd13b8ee104d6fe3334dab26ebf5e58c5cbbaafb4b6c44e3122a9ebe2`; TypeTree JSONL set `36adee77c37556e2b55a4198e2249f0d5e68187b654d39c479d5c8de3c143f44`.
- Relevant file SHA-256 pins and exact counts are in the receipt. No runtime, DPS, native/FDE, AI-1 artifact, secret, or global-absence claim was used.
