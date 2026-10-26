# H3 — 45 exact `900xx` prefab-root identities outside the waves roster

**Verdict:** `ROOT_METADATA_IDENTITIES_PRESENT · OUTSIDE_CURRENT_ROSTER · ASSET_ROLES_NOT_ASSIGNED`  
**Evidence:** static serialized metadata only (bounded, level B). This inventory identifies root records; it does not infer what any item is for.

## Counting rule and coverage

- `reverse-engineering/raw/typetrees/prefab-roots.csv` has **2,081** root records. Exact root-name rule: `^900\d{2}$` (five digits, no suffix). It yields **45** unique roots.
- The broader prefix expression `^900\d\d` yields **48** records. The three prefix-only names `90030 [Quest_Notice]`, `90036-Lasers`, and `90053-Laser` are excluded from the exact five-digit inventory.
- The serialized waves roster in `datas/waves.json` has **109** distinct enemy names. Exact string comparison finds **0/45** of these root names in that roster; therefore all **45** are outside this roster snapshot.
- For all 45 exact roots, the export contains the root name, Transform path ID, GameObject path ID, and serialized direct-child count: **45/45 root metadata records present; 0 bounded-missing root identities**. Component-level identity, art identity, intended asset role, use outside this roster, and per-stage usage are not established here and remain bounded-missing/not assessed.

## Metadata-qualified inventory

`children` is copied as a serialized direct-child count. It is not interpreted as an asset type or function. All rows have `asset_role = NOT_ASSIGNED` in the machine receipt.

| Root name | Transform path ID | GameObject path ID | Serialized children |
|---|---:|---:|---:|
| `90017` | 430592 | 184387 | 1 |
| `90018` | 430591 | 184386 | 1 |
| `90019` | 430589 | 184384 | 1 |
| `90020` | 430597 | 184392 | 1 |
| `90021` | 430590 | 184385 | 1 |
| `90022` | 430593 | 184388 | 1 |
| `90023` | 430594 | 184389 | 1 |
| `90024` | 430596 | 184391 | 2 |
| `90026` | 430595 | 184390 | 2 |
| `90027` | 301073 | 82183 | 2 |
| `90028` | 242521 | 6839 | 3 |
| `90029` | 242498 | 6816 | 3 |
| `90031` | 242499 | 6817 | 0 |
| `90032` | 242524 | 6842 | 0 |
| `90033` | 242510 | 6828 | 0 |
| `90034` | 242529 | 6847 | 1 |
| `90035` | 242518 | 6836 | 0 |
| `90037` | 242496 | 6814 | 0 |
| `90040` | 242527 | 6845 | 1 |
| `90043` | 242512 | 6830 | 4 |
| `90044` | 462439 | 34677 | 1 |
| `90045` | 301075 | 82185 | 2 |
| `90046` | 301076 | 82186 | 1 |
| `90047` | 301072 | 82182 | 2 |
| `90048` | 392155 | 163831 | 2 |
| `90049` | 392157 | 163833 | 2 |
| `90050` | 301074 | 82184 | 2 |
| `90051` | 392156 | 163832 | 2 |
| `90052` | 242505 | 6823 | 0 |
| `90056` | 242530 | 6848 | 1 |
| `90057` | 242511 | 6829 | 1 |
| `90058` | 242504 | 6822 | 1 |
| `90059` | 242533 | 6851 | 1 |
| `90060` | 242508 | 6826 | 1 |
| `90061` | 242515 | 6833 | 2 |
| `90062` | 242503 | 6821 | 1 |
| `90063` | 242522 | 6840 | 1 |
| `90064` | 242523 | 6841 | 2 |
| `90065` | 242514 | 6832 | 2 |
| `90066` | 242497 | 6815 | 1 |
| `90067` | 449610 | 70805 | 3 |
| `90068` | 417805 | 25966 | 3 |
| `90069` | 417806 | 25967 | 1 |
| `90070` | 449609 | 70804 | 4 |
| `90071` | 449612 | 70807 | 3 |

Child-count distribution: **0 → 6**, **1 → 20**, **2 → 12**, **3 → 5**, **4 → 2**.

## Pins and limits

- `reverse-engineering/raw/typetrees/prefab-roots.csv` — SHA-256 `cd997d3ebf5a6d3bc82131bce443b5541ab722045eb6e11b674627e9d96285a6` (57,667 bytes).
- `datas/waves.json` — SHA-256 `dde007618b7cbc83f0702298f7744609f8b25b2d7479ab15964b1fb6fa8abc73` (2,796,955 bytes).
- Receipt: `datas/l3_a5_h3_root_900xx_outside_roster.json`; builder: `tools/build_a5_h3_root_900xx_inventory.py`; tests: `tests/test_a5_h3_root_900xx_inventory.py`.
- Roster exclusion means exact-name absence in this pinned waves roster only; it is not proof of global non-use. No asset-role, runtime, native/FDE, or behavior claim is made.
