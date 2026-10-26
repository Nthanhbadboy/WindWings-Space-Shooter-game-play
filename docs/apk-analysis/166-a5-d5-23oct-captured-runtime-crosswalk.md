# Report 166 — expanded read-only crosswalk of the full 2026-10-23 capture folder

PR12 follow-up claim: `6427801423`.

## Amendment after reviewing the local source folder

The first pass read a selected subset and missed evidence in the other archived screenshots and the EndGame hierarchy. This expanded pass corrects that omission: the capture **does** contain direct Premium-related UI evidence. The screenshots display a Premium welcome modal saying **“member of Premium FOREVER”** and advertising **“FREE first revival”** among its benefits. The archived EndGame hierarchy also contains an active Premium-named popup.

That evidence is important, but it still does **not** show a 24-hour grant or an initial free-life stock. The visible copy says “FOREVER,” not “24 hours”; no expiry/countdown is shown. Nor does a screenshot of promotional UI validate account/backend entitlement or prove that a fresh account received a benefit. The capture is from the modded/repackaged package and visibly has substantial nonzero resource balances behind the modal, so it is not a verified clean first-launch state.

## Scope and provenance

This pass enumerated and pinned **all 84 files** in `docs/apk-analysis/ramus/2026-10-23-phone/` (**43 JSON, 35 PNG, 3 Markdown, 3 log files; 23,793,059 bytes**). The receipt stores each filename, byte size, SHA-256, and a directory-manifest SHA-256. The JSON capture snapshots and logs were read locally; relevant screenshot text below is a manual visual transcription of the listed, hash-pinned images. No capture source was altered.

Capture identity from the source summary: Huawei Mate 20 X / Android 10 / Unity 2022.3.62f3 IL2CPP; package `com.Gcenter.WindWings.SpaceShooter.Premium`, described as modded/repackaged **1.0.69**. The comparison source is official `com.Wind.wings.Space.Shooter` **1.3.118**. Comparisons remain **cross-build only**, not same-build runtime parity. No new probe, bridge, ADB, runtime-probe workflow, emulator, native/FDE, or secret workflow was run.

## What the additional files show

### Premium welcome and “free first revival” are visible UI claims

Eight archived EndGame/welcome screenshots reviewed in this pass display the same modal:

- `live_2_EndGame.png` through `live_5_EndGame.png`
- `victory_next1.png`, `victory_next2.png`, `victory_tapoutside.png`, and `screenshot_now.png`

Visible text includes:

> WELCOME TO PREMIUM VERSION
>
> Congratulations on being a member of Premium FOREVER
>
> NO ads. · FREE first revival. · UNLIMITED energy for play. · Get more X3 coin collected
>
> FREE

The reward cards visibly show `+20`, `+300`, and `+10`; this report does not assign an unverified item type to every card. The background top bar visibly shows energy `250/200`, 3 stars, 71,581 coins, and 510 diamonds. These are screenshot readings only and are not joined to the GP snapshots below.

Separately, `hierarchy_endgame.json` has scene `EndGame` and an active node at:

`/BOARD_MANAGER/BOARD_ENDGAME(Clone)/Popup_PremiumDailyCollect(PREMIUM)(Clone)`

Its attached component labels remain generic `Component`; it exposes no entitlement flag, expiry, or grant value. The captured scene tree therefore supports the presence of an active Premium-named popup, not the account state or the exact UI text as a field readback.

**Bounded conclusion:** Premium welcome/benefit copy is directly visible in this modded build, including an advertised **free first revival**. It does not establish that the offer is a new-player 24-hour trial, that the account is newly created, or that the advertised benefits were verified against a service/backend. The screen calls the membership “FOREVER”; no 24-hour duration/expiry appears in the inspected capture. This is stronger than the first report’s “no Premium UI evidence” wording, which is superseded by the screenshots above.

### Full set of captured GP snapshots

The original folder has seven GP-related outputs relevant to reborn state. Their raw values are kept separate because they are differently named capture files and not all contain the same fields:

| Source | Summary | `countReborn` | `rebornNow` | `maxCountReborn` | `listRebornUseItems` | `pvpLife` | Other captured context |
|---|---:|---:|---:|---:|---|---:|---|
| `statics_SpaceShooter_Gameplay_GP_Datas.json` | false | 0 | 0 | -1 | unread array placeholder | 3 | `coinCount=0`, `killCount=0` |
| `live_1_gp.json` | false | 0 | not present | not present | four `false` | 3 | `coinCount=540`, `killCount=276` |
| `live_2_gp.json` | true | 0 | not present | not present | four `false` | 3 | `coinCount=1632`, `killCount=278` |
| `live_3_gp.json` | true | 0 | not present | not present | four `false` | 3 | byte-identical to `live_2_gp.json` |
| `live_4_gp.json` | true | 0 | not present | not present | four `false` | 3 | byte-identical to `live_2_gp.json` |
| `live_5_gp.json` | true | 0 | not present | not present | four `false` | 3 | byte-identical to `live_2_gp.json` |
| `boss_boss_gp.json` | true | 0 | 0 | -1 | four `false` | 3 | `coinCount=1506`, `killCount=243` |

`live_2_gp.json`–`live_5_gp.json` have the same SHA-256 and identical bytes; they are one repeated payload, not four independent observations. The files where reborn is represented show no reborn counted/marked used in those captured states. The `live_2..5` snapshots do not contain `rebornNow` or `maxCountReborn`; “not present” must not be read as zero. The `/statics` placeholder is not a decoded array.

**What this adds:** the UI advertises **one free first revival as a Premium benefit**. It still does not show how many free revivals a new account starts with, whether Premium is required to claim the first one, whether the shown package had an active entitlement, or whether the free benefit was ever consumed. `maxCountReborn=-1` remains an uninterpreted raw value. `pvpLife=3` is a distinct field and is not extra-life stock. `countVideoBox=0` in these snapshots does not establish reborn ad eligibility.

### Timeline, hierarchy, and account-state limitations

`ramus_mirror_timeline.log` records the captured session transitioning Menu → Game → EndGame, with EndGame beginning at 21:45:42.592 local time. `live_2_EndGame.png`–`live_5_EndGame.png` are EndGame-named visual captures, but no timestamp record binds each image to an exact GP JSON sample. `logcat_tail.log` records Google Play Games authentication as `InternalError`; this is not evidence about Premium itself, but it is another reason not to claim a verified signed-in account entitlement from this capture.

The separate Game hierarchy shows `Pack_Premium`, `Board_Reborn(Clone)`, and `Board_RebornIAP(Clone)` inactive in that captured scene. Their existence/active state is UI structure, not an entitlement or allowance readback. In EndGame, the PremiumDailyCollect-named popup is active, as noted above.

The type files are explicitly narrow filters: `types_data.json` is filtered by `_Data`; the `Wallet` and `Purse` filters return no matches, while the `Currency` filter includes framework/Facebook currency types. None is a complete live component or wallet inventory, and none binds the player, Health, Attack, Controller, or account entitlement instance.

## Health and attack/controller boundary, after the full-folder check

- `screenshot_running_stage1.png`, `p_1_Game.png`, and `r2_1_Game.png` visibly show HUD HP **2500**.
- Archived runtime `/statics` `statics_Player_Get_Datas.json` independently reports `StartHp=2500`; its main-cannon damage/rate and wing-cannon damage arrays each have 24 entries. Example at zero-based index 2: damage 2680 and rate 4.8.
- `health_game.json` separately records scene `Game`, uptime 88.0177 seconds, frame 4574. The screenshot and this scene-state JSON are not asserted to be the same instant.
- This is direct captured-run HUD and static-data readback, not a live `Player_Health` owner join. The 24-element arrays are data readbacks, not proof of a `Player_Attack_N` instance firing or measured per-object damage. The hierarchy still uses generic component labels and does not bind a live `Player_Controller`.
- Report 111 independently says runtime DPS is not measured. `Live-DPS` remains `MODEL_NOT_MEASURED`.

## Result

| Claim | Status after checking the full local folder |
|---|---|
| Premium UI | **OBSERVED** — Premium welcome modal says “member of Premium FOREVER.” This is UI text in a modded build, not backend verification. |
| New-player 24-hour Premium grant | **NOT MEASURED** — no 24-hour wording, timer, expiry, fresh-account state, or grant receipt. The visible text says “FOREVER.” |
| Free first revival | **UI_ADVERTISED** — explicitly listed as a Premium benefit. Starting life stock, eligibility, and actual use remain **NOT MEASURED**. |
| Reborn used in the recorded GP snapshots | No captured snapshot records one as used; repeated GP payloads are deduplicated. This does not establish initial allowance. |
| HUD HP / `StartHp` | **2500 / 2500 observed** in the captured modded 1.0.69 run. |
| Health/Attack/Controller component ownership | **NOT_BOUND** in these runtime artifacts. |
| Same-build parity / DPS | **NOT ESTABLISHED / MODEL_NOT_MEASURED**. |

The full-folder receipt is `datas/l3_a5_d5_23oct_runtime_crosswalk.json`; builder `tools/build_a5_d5_23oct_runtime_crosswalk.py`; tests `tests/test_a5_d5_23oct_runtime_crosswalk.py`. Its complete source-directory manifest is SHA-256 `19fcf9eb4792651993f61400de9c4167dd11cd820473fbcf2c9f3c8793871787`. This is still an archival read-only analysis and does not reopen or authorize rerunning the runtime lane.
