# D5 user-lead follow-up — premium, extra life, Health upgrade, and player data routes

**Claim:** PR12 `6427556449`, after the D5-residual handoff.
**Verdict:** `HEALTH_TECH_ROUTE_SUPPORTED; STARTER_PREMIUM_AND_EXTRA_LIFE_COUNT_NOT_BOUND; COMPONENT_OWNER_NOT_BOUND` (static-only). The user-provided 24-hour-premium / extra-life lead is treated as a hypothesis to test, not as established evidence.

## Findings

### 1. Health is a different upgrade path from ship upgrades

The existing static result in `docs/spec/DATA_SYNC.md` §7.29 / `docs/spec/OPEN_ISSUES.md` A1 gives `Player_Get_Datas.StartHp = 2500`. The published max-HP formula is `2500 × (1 + 0.18 × TechStatPoints(0) + 1 × GetNumberAbility(7))`; therefore 2500 is the base with Health-tech points and ability 7 both at zero, not an unconditional value after bonuses. The existing label mapping identifies stat 0 as **Health** on the **Basic** tech tab. Thus the supported path is `StartHp → TechStatPoints(0) → Player_Health.Start()`, not a per-ship `Player_Attack_N` damage-array lookup.

This does not mean every account starts at exactly 2500 after upgrades/ability bonuses, and it does not prove a serialized `Player_Health` component owner: the pinned serialized export set has no `Player_Health` CSV or TypeTree JSONL file. `Tech_Ability_Data` provides six serialized `TechAbility` records with `TypeIndex` values, but those rows alone do not label index 0 as Health; that semantic link is reused from the already-published static analysis.

`Board_Players.jsonl.gz` row 650952 (`Board_Players`) separately references `btnUpgradeByCoins` and `btnUpgradeByGems` and their cost labels. This is evidence of the ship-catalogue UI having coin/gem upgrade controls; it must not be mistaken for the Health-tech route.

### 2. The 24-hour premium and starter extra-life count remain unresolved

The captured `IAPProduct` object lists 71 consumable and 99 non-consumable product IDs, including `windwings.pro.1stpurchase`, `windwings.pro.week`, `windwings.pro.month`, `windwings.pro.forever`, and `windwings.timereward.forever`. This establishes catalogue strings only—not which offer is presented, a first-launch grant, its duration, or an account's entitlement state. The existing published UI metadata names a premium trial/day-trial and timer, but does not establish a 24-hour duration or a grant at game start.

The existing `Board_Reborn` API surface names free, energy, ad, gem, and premium continuation routes (including `IsFreeReborn` and `GetMaxRebornCount(vipLevel)`). This is consistent with there being paths other than ads/gems, but it does not establish the initial free-life stock, eligibility, or whether premium causes that stock. No `Board_Reborn` serialized record is present among these captured exports. Therefore both the claimed **24-hour starter premium** and the claimed **starting extra-life allowance** remain `NOT_BOUND` within the captured source set.

### 3. Use catalogue/array routes for Attack_N; keep Controller separate

The serialized `Data_Players` record (`path_id=580761`) contains 25 entries: IDs `10001`–`10024` and `10999`; the separate `Data_Drones` row has IDs `20001`–`20013`. Those IDs are useful roster evidence, but their parallel numbering is **not** used to join a `Player_Attack_N` class to a particular ship ID.

For attack data, reuse report 163's previously pinned `Player_Attack_N → N−1` class-to-static-array join and report 109's `Board_Players.GetPlayerPower` consumer of its own 24-entry UI arrays. These are separate evidence routes from `GP_Datas.player`; report 109's power-display result is **not** a combat-damage or component-owner claim.

For `Player_Controller`, reuse reports 85–87 only for their already-published method-flow results. The class inventory contains the identity, but the pinned serialized CSV/TypeTree set has no `Player_Controller` owner record. `Board_Players` references are UI controls and do not identify a `Player_Controller` instance. The residual owner join remains `NOT_BOUND`.

## Bounded source set and reproducibility

The receipt pins the complete captured export manifests (126 ScriptableObject CSVs and 140 TypeTree JSONL files) and the focal `Data_Players`, `Board_Players`, `Tech_Ability_Data`, and `IAPProduct` records. It records their exact path IDs, roster entries, button references, TypeIndex values, product IDs, and SHA-256 pins.

- Receipt: `datas/l3_a5_d5_user_lead_crosswalk.json`, SHA-256 `bde75c018dfa079c9e9900bf6c0136a08e98a1418c5f09737d5c5f7858cc3868`.
- Builder: `tools/build_a5_d5_user_lead_crosswalk.py`.
- Tests: `tests/test_a5_d5_user_lead_crosswalk.py`.
- Prior evidence reused without repeating inventories: reports 79–87, 109, 163, and 164.

No runtime readback/parity, native/FDE, AI-1 artifact, secret, or whole-build/global-absence claim was used. Any stronger conclusion about the 24-hour grant, starter lives, or component owner requires a source-pinned record that contains the relevant entitlement/stock and owner context.
