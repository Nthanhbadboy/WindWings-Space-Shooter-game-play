# 121 — H4 docs-only sync-review, round 2

**Provenance:** `arena/8141386a-windwings-space-shooter-game-p`
**Disposition:** `PARTIALLY_SYNCED_NOT_A_RECONCILED_IMPLEMENTATION_CONTRACT`
**Assignment:** PR12 [6425374777④](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6425374777) · **CLAIM:** [6425778321](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6425778321) · **Producer-directed progress:** [6425919499](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6425919499).

## 1. Result and evidence boundary

**20 human-reviewed text assertions: 13 SYNCED, 4 DRIFT, 3 PARTIALLY_SYNCED; 0 OUT_OF_SCOPE assertions counted. Seven producer-actionable assertions (4 P1, 3 P2).** No P0/new numeric refutation. This is not a declaration that the implementation spec is fully reconciled.

Most DATA_SYNC correction chains are properly recorded. The material gaps are stale implementation-facing summaries: missing Board consumers; sole-driver wording after the route split; a readiness arrow mixing serialized burstEvent presence with the completion branch; and certainty/effect claims for unjoined handler fields. Three lower-priority precision issues concern encoded usage, wrong section links, and the historical43/51 breadcrumb.

**This review compares published text, not its underlying native proof.** Original APK remains authority, but H4 does not open it or peer raw/native/serialized artifacts, import peer tools, disassemble, execute a new harness, infer live values, or reopen device/runtime work. `SYNCED` means the compared assertions agree within their stated bounds, not that native/serialized bytes were independently reproduced. The mechanical checker verifies pinned Markdown/Git bytes, exact quotations, locators and bookkeeping; it does **not** infer natural-language truth.

No #27-full ACK, runtime/readback/render acceptance, cross-edit or self-ACK. Corrections belong to the spec producer. This artifact does not claim the producer has applied them. It audits the **fixed baseline below**, not an unobserved later tip. Frozen #4–8/118–120 scientific reports/artifacts/receipts remain unchanged; the actual120 exact-head CI capsule is added before live-needle changes. Existing frozen119/120 harnesses may run as regression gates; those are not new H4 native findings.

## 2. Fixed text inputs, selection and provenance

| Source lane | Exact commit | Selected full texts | Review role |
|---|---|---:|---|
| Spec producer | `e301feb409c75527f4c796a4a548093d4b2bf95d` | 13 | Current producer spec, not this branch’s historical copies |
| a5 | `64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6` | 8 | Report152 template; reports153–159 assertion inputs |
| AI4 | `97f989f389784db59b6627756055676314011423` | 12 | Published136–147 correction-chain text only |
| Corrected ef text | `ea6a3835f786306b07df9658262a6e3f6658f809` | 2 | Published123/124 text, not a new native review |

Archived spec selection: `DATA_SYNC`, `GAMEPLAY`, `BALANCE`, `ANIMATION`, `ANIMATION_GAPS`, `ANIMATION_SCRIPT`, `OPEN_ISSUES`, `START_HERE`, `README`, `HANDOFF_ANIM_RAW`, `MISSING_FOR_NEW_GAME`, `DONE`, `DESIGN_READINESS` under `docs/spec/`.

`reverse-engineering/raw/geometry-8141386a/docs-sync-round2/peer-pins.json` records original path, full commit, Git blob ID, full-source SHA-256, gzip SHA-256, size and line count for **35** snapshots. `review-map.json` records the human decisions and exact unique text selectors. The artifact expands **72 citations** with original file/section/line range, full quotation SHA-256 and pinned GitHub link. All35 snapshots were compared with actual `git show commit:path` bytes locally. No whole peer worktree was imported.

All35 complete texts are retained for context, **not** a claim that every sentence was reviewed. Archived sources without assertion-level citations are listed separately in the artifact. AI4 report148+ residual-registry updates, followups149+, a5 H1–H3/report160+, ef126 and native/instance work are outside this fixed review; report147’s historical56-open registry is not asserted to be the current residual truth.

DATA_SYNC24.85–96 is selected by **exact heading**, not a contiguous line span:24.87 is physically appended after24.98. The checker finds all12 headings and retains their original line positions.

## 3. Assertion matrix

Line numbers below belong to the exact commits above. Complete quote text/hashes and recommendations are in the artifact and §4. **A GREEN checker does not change a human DRIFT verdict to SYNCED.**

| ID | Verdict | Compared assertion / bounded conclusion | Key pinned locators |
|---|---|---|---|
| H4-01 | DRIFT | G2 consumer bound in log, still missing in implementation summaries | [spec-MISSING_FOR_NEW_GAME.md:169–170](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/MISSING_FOR_NEW_GAME.md#L169-L170); [a5-report153.md:3–4](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/153-g2-board-endgame-consumer.md#L3-L4) |
| H4-02 | SYNCED | G4 corrected slot identity is Stop, not runtime delivery | [spec-OPEN_ISSUES.md:71–74](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/OPEN_ISSUES.md#L71-L74); [a5-report154.md:4–4](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/154-g4-gun3static-setactive-semantics.md#L4-L4) |
| H4-03 | SYNCED | G4 false-then-true same-index calls, not stable receiver identity | [spec-DATA_SYNC.md:4958–4964](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4958-L4964); [a5-report154.md:21–21](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/154-g4-gun3static-setactive-semantics.md#L21-L21) |
| H4-04 | SYNCED | G5 contextual controller match plus independently supplied literal | [spec-DATA_SYNC.md:4972–4975](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4972-L4975); [a5-report155.md:16–16](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/155-g5-tut-settings1-focusgamespeed-flow.md#L16-L16) |
| H4-05 | SYNCED | G6 five captured blobs, three field binds, one dynamic site still NOT_BOUND | [spec-DATA_SYNC.md:5026–5030](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5026-L5030); [a5-report156.md:8–8](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/156-g6-array-blob-field-binding-census.md#L8-L8) |
| H4-06 | PARTIALLY_SYNCED | S1 route split fixed at top, sole-driver assertion persists | [spec-ANIMATION_SCRIPT.md:17–21](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L17-L21); [a5-report157.md:10–10](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L10-L10) |
| H4-07 | DRIFT | G3 completion path versus serialized burstEvent field | [spec-DESIGN_READINESS.md:26–31](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DESIGN_READINESS.md#L26-L31); [a5-report157.md:46–46](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L46-L46) |
| H4-08 | DRIFT | S2 handler-slot certainty survived the summary repair | [spec-ANIMATION_SCRIPT.md:190–193](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L190-L193); [a5-report157.md:12–12](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L12-L12) |
| H4-09 | SYNCED | N2 serialized owner is bounded identity, not native instance construction | [spec-DATA_SYNC.md:5168–5173](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5168-L5173); [a5-report158.md:22–24](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/158-n2-serialized-owner-graph-builder.md#L22-L24) |
| H4-10 | SYNCED | N1 public-document review is not raw reproduction | [spec-DATA_SYNC.md:5243–5249](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5243-L5249); [a5-report159.md:8–8](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/159-a5-n1-report122-independent-review.md#L8-L8) |
| H4-11 | SYNCED | 135 reader absence superseded by136 statics-x0 reader | [spec-DATA_SYNC.md:5349–5351](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5349-L5351); [ai4-report136.md:19–20](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/136-535b0541-rank-api.md#L19-L20) |
| H4-12 | SYNCED | 136/137 decimal display superseded by138 ToRoman target | [spec-DATA_SYNC.md:4895–4899](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4895-L4899); [ai4-report136.md:20–20](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/136-535b0541-rank-api.md#L20-L20) |
| H4-13 | SYNCED | 138 Arena gate field owner corrected by139 | [spec-DATA_SYNC.md:4913–4917](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4913-L4917); [ai4-report139.md:126–126](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/139-535b0541-arena-statics.md#L126-L126) |
| H4-14 | SYNCED | 140 slot and branch polarity corrected by141 | [spec-DATA_SYNC.md:5017–5024](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5017-L5024); [ai4-report140.md:100–101](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/140-535b0541-arena-config.md#L100-L101) |
| H4-15 | SYNCED | 141 unknown Application cell resolved by142, distinct from GameConfig | [spec-DATA_SYNC.md:5067–5071](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5067-L5071); [ai4-report142.md:15–16](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/142-535b0541-application-cell.md#L15-L16) |
| H4-16 | SYNCED | 142 missing currency keys corrected by143 addend lookup | [spec-DATA_SYNC.md:5091–5097](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5091-L5097); [ai4-report143.md:16–19](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/143-535b0541-economy-keys.md#L16-L19) |
| H4-17 | SYNCED | 145 count attribution corrected by147 and accepted in24.96 | [spec-DATA_SYNC.md:5235–5239](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5235-L5239); [ai4-report145.md:20–20](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/145-535b0541-store-key-callers.md#L20-L20) |
| H4-18 | PARTIALLY_SYNCED | Stop identity correct, normative encoding explanation lags R1 correction | [spec-ANIMATION_SCRIPT.md:170–176](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L170-L176); [ef-report123.md:48–48](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/ea6a3835f786306b07df9658262a6e3f6658f809/docs/apk-analysis/123-ef6b75ef-native-vtable-linkage.md#L48-L48) |
| H4-19 | DRIFT | Broken internal locators: slot/vtable correction points to rank section24.87 | [spec-DATA_SYNC.md:4970–4970](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4970-L4970); [spec-DATA_SYNC.md:4818–4819](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4818-L4819) |
| H4-20 | PARTIALLY_SYNCED | 145 residual says43 computed although same paragraph and146 say51 | [spec-DATA_SYNC.md:5140–5146](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5140-L5146); [ai4-report146.md:1–4](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/97f989f389784db59b6627756055676314011423/docs/apk-analysis/146-535b0541-computed-key-index.md#L1-L4) |

### Historical supersessions that are NOT new drift

- **135→136**: GetRankNumber supplies the MaxRankStars reader through statics-x0; DATA_SYNC24.87/24.95 explicitly supersede the reader-absence premise.
- **136/137→138**: decimal/ToString and Archon4 prose is explicitly superseded by the MyLibrary.ToRoman target in24.89. The glyph implementation remains bounded-missing; no execution or Roman glyph values are measured by H4.
- **138→139**: the+1C gate belongs to ArenaConfig.IsOpen, not ArenaManager.IsOpen+0.
- **140→141→142**: real gate slot2ADBB88=44940168/GameConfig; isEmpty true reloads, false reaches versions. Slot2ADB8E0=44939488 is the distinct Application cell, not a contradiction or interchangeable slot.
- **142→143**: addend lookup supplies GCoins/Gems/StarCount/WingCoins;21GameDatas keys/48reads+42tail writes are not a universal dynamic-schema count.
- **145→147 /24.96**: the published correction is174, not170;184−174=10=4key-jump+6meta-rewards. H4 checks stated arithmetic, not the original store scan. Unknown0 does not close dynamic indices, configured values or runtime.

### Bounded synchronized results retained

- G4/report154: three PPtrs, false→reload→true, same index but not guaranteed receiver identity under mutation; external Stop identity ≠ delivered callback or defeat/burst assignment.
- G5/report155: Slider.onChange→guarded SetTrigger; independent literal identity followed by static controller-name equality, not a transition result or transfer to either Spine route.
- G6/report156: published table lengths4+7+7+7+24=49; three named fields/two locals. Ordinal1@14E7C78 is NOT_BOUND; generic fallback is not its selected24-handle family. H4 reads the table, not blob bytes.
- G3/report157: Boss39001 Event callback is published as RET; separate Complete→BossWork→SetAnimation/defeatEvent path. No event-slot/handler join or burstEvent branch is supplied.
- N2/report158: controller1856/Body1→Animator493584→GO76852→Boss37004/root73241 is published bounded owner identity, not graph-builder→live-instance execution; no guessed serialized-file basename.
- N1/report159: the published16-row table has9CONFIRMED/6SUPERSEDED/1UNVERIFIABLE. Confirmation is text support, with original virtual methods superseding sinks/totals and raw/test pins explicitly not rehashed by that reviewer.

## 4. Producer-owned correction queue with exact quote receipts

Each SHA below covers the **entire displayed quotation, including original newlines**, not a paraphrase. Source/heading ancestry/full-source SHA and all72 quotations remain in the machine artifact. Recommendations are this human reviewer’s bounded interpretation, not an automatic native verifier result.

### H4-01 — P1 / DRIFT: G2 consumer bound in log, still missing in implementation summaries

DATA_SYNC24.90 and report153 bind the Endgame array to a rank-index divisor and positive item22 quantity. MISSING2.2c and BALANCE6.10 still say no consumer/unknown threshold or HP-attack candidate. Board_Players UI consumer is also acknowledged in24.88, not combat damage.

**Suggested producer-owned correction:** Replace consumer-absence/purpose guesses in MISSING2.2c and BALANCE6.10 with separate Board_Players UI-power and Endgame divisor consumers. Retain B for unbound combat semantics; do not name item22 from the misspelled field.

**[docs/spec/MISSING_FOR_NEW_GAME.md:169–170](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/MISSING_FOR_NEW_GAME.md#L169-L170)** · quote SHA-256 `4b772f596aa8df94da53961834f138b7204b9a219fed77d06c7017eafa8c2494`

> | `Board_Endgame.ctor` | **int[10]** | `900, 890, 880, 870, 860, 850, 840, 830, 820, 810` | giảm đều **10** mỗi bậc — dải ngưỡng, chưa rõ dùng cho gì |
> | `Board_Players.ctor` | float[24] | **1,0** × 24 | baseline |

**[docs/spec/MISSING_FOR_NEW_GAME.md:174–177](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/MISSING_FOR_NEW_GAME.md#L174-L177)** · quote SHA-256 `7172c4a8f6a900092bcc552970e8809a34f78923d83d78a05b8d3ede18220a8c`

> > **6000** — hai nguồn số khác consumer, không damage×rate proxy. `Board_Players.allBasicAtk/
> > allDeltaAtk` (float[24], `4640…`/`,168`) **vẫn chưa có consumer** ⇒ giữ mức **B**, B3
> > damage-theo-rank của tàu chưa chốt.
>

**[docs/spec/BALANCE.md:1586–1586](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/BALANCE.md#L1586-L1586)** · quote SHA-256 `58a2662ecb27bd91f179113df707b8b1cf80bcb1c06cb3ede3f438db2ae72022`

> | `Board_*` | 5 | `Board_Players.allBasicAtk` float[24] `4640 5120 5040 6160 8896 …` · `allDeltaAtk` = **0,168** × 24 · `Board_Drones` float[12] `500 600 800 1250 …` · `Board_Endgame` int[10] `900…810` | **ứng viên HP/atk theo hạng** — chưa có consumer ⇒ **B** |

**[docs/spec/DATA_SYNC.md:4951–4956](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4951-L4956)** · quote SHA-256 `c631913cabe135572ab0c76ccf7543eaff14589fc5b0b7be4898bb4678c25cfe`

>   consumer TRỰC TIẾP — `Board_Endgame.ctor` int[10] `900…810` →
>   **`devidedArenaMedals` @`this+0x2A0`** → `SetArenaRewards`: `GameMode.arenaRank`
>   index divisor cho `Board_Endgame.arenaPoints`; thương dương → `SetGiftInfo`
>   **item ID 22 quantity** (nghĩa item không assert). Receipt pulled
>   `258293f5…` 4000B khớp ✓. §2.2c: cả 2 mục treo của row 21 giờ có consumer
>   (G1 + G2); còn hở "item ID 22 là gì" — bounded.

**[docs/spec/DATA_SYNC.md:4846–4850](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4846-L4850)** · quote SHA-256 `3d06d2913a1aae9d92824db1aec8ad2691e26a0f76f5e5b6bc2eccb1760c1eee`

>   +0x10/+0x18** → `basic[i]×(1+delta[i]×GetPlayerLevel)` → `SetPlayerInfo` →
>   `textPlayerPower` (report 109) — **UI power only**; giả thuyết
>   `damage(rank)=basic+0,168·rank` **REFUTE** (report 122: `Player_Attack_1` đọc
>   `StartMainCannonDamages`@+0x78, rank chỉ gate loop); **giữ mức B**, `4640` =
>   board-power entry ≠ HP tàu — guard tôn trọng đúng. a5 tự sửa

### H4-06 — P1 / PARTIALLY_SYNCED: S1 route split fixed at top, sole-driver assertion persists

ANIMATION_SCRIPT opening and README now distinguish Boss39001/Boss_1_Animation from Boss39002/Boss1_Director. The same normative file54 still calls Boss1_Director the sole animation-calling class, inconsistent with report157 completion actions.

**Suggested producer-owned correction:** Scope section2/table to Boss39002 and replace sole-driver wording with the separate Boss39001 completion-to-BossWork route. Shared asset does not merge drivers.

**[docs/spec/ANIMATION_SCRIPT.md:54–55](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L54-L55)** · quote SHA-256 `20e4df4d1789425f525aafb7a51b4272d8b321738b226d32a1191ccd25e09e1f`

> `Boss1_Director` là lớp duy nhất trong 3 lớp boss 1 thật sự **gọi** animation. Bảng method:
>

**[docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md:43–45](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L43-L45)** · quote SHA-256 `0a9ec47d9c901085a2e28bf88532bfb1be94a8b03e299ef3fdb944cb49140d96`

> | `stateAppear` (`Xuathien`) | `0x1247C6C–0x1247CB0` | If `nextTurn` (`+0x88`) is non-null, calls its delegate; if the `skeAnim`/state path is non-null, passes `stateAttack1` (`+0x48`) to the known Spine `SetAnimation` target `0x220D324`, track index `0`, loop flag `1` |
> | `statePreAttack2` (`Chuyensangattack2`) | `0x1247CB4–0x1247CF8` | Same optional `nextTurn` delegate path; passes `stateAttack2` (`+0x50`) to `0x220D324`, track `0`, loop flag `1` |
> | `statePreAttack3` (`Chuyensangattack3`) | `0x1247CFC–0x1247D54` | Same optional `nextTurn` delegate path; passes `stateAttack3` (`+0x58`) to `0x220D324`, track `0`, loop flag `1` |

### H4-07 — P1 / DRIFT: G3 completion path versus serialized burstEvent field

DATA_SYNC24.92 correctly records the Boss39001 Event callback RET and no burstEvent read in the separate completion path. DESIGN_READINESS update4 still draws Baydi/Dead to defeat+70/burst+78 together. Serialized presence/target of burstEvent is not a demonstrated completion-branch invocation.

**Suggested producer-owned correction:** Rewrite the readiness arrow: Event callback RET; Complete->BossWork Baydi/Dead reads defeatEvent+70 only. Retain burstEvent+78 as serialized field/target with no marker/delivery branch proven.

**[docs/spec/DESIGN_READINESS.md:26–31](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DESIGN_READINESS.md#L26-L31)** · quote SHA-256 `a1568be03dd503a768ed11df6190aac90d46663f19218f401dc30d2ab833fcab`

> > `Boss_AttackPhases` (PPtr → Animator/controller Boss-39019/20/21) · state
> > `stateRunAway/Baydi` + `stateDie/Dead` → **UnityEvent defeat +0x70 / burst +0x78**
> > (offset **trực tiếp từ TypeDefIndex 141**, ban đầu ghi là inference — đã CORRECT bằng
> > metadata) → receiver **Enemy_Destroy 601110** (root 185722, `destroyScript` cùng root) ·
> > Spine chain 602882→580611→skeleton JSON 918 · **8/8 state labels khớp tên animation
> > asset** · BossSpineEventHandler: có code, **0 instance** ⇒ không join. ⇒ *thứ tự pha

**[docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md:46–46](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L46-L46)** · quote SHA-256 `03c56d3782cec68ec5d14bd2a7fec0bebdf7f93e376c4a69edc7b2d14b8e48ea`

> | `stateRunAway` (`Baydi`) or `stateDie` (`Dead`) | `0x1247D58–0x1247DA4` | If the `defeatEvent` field (`+0x70`) is non-null, passes it to helper target `0x278EF98`; this branch does not read `burstEvent` (`+0x78`) |

### H4-08 — P1 / DRIFT: S2 handler-slot certainty survived the summary repair

ANIMATION_SCRIPT190-193 still declares both BossSpineEventHandler slots certainly drawn from Stop/Banplasma at levelA and interprets the timing as a toggle. Report157 has no joined handler instance; report154 only identifies Boss39002 comparison Stop. This does not bind either generic-handler field or a marker occurrence.

**Suggested producer-owned correction:** Remove certainty/field assignments and gameplay toggle inference. State only asset marker names; Boss39002 comparison literal Stop is a separate proven identity. Boss39001 handler fields, marker delivery and effects stay NOT_BOUND.

**[docs/spec/ANIMATION_SCRIPT.md:190–193](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L190-L193)** · quote SHA-256 `79a8876959679836968c9ebcde04e70e26abfc1bce2a441be73dc30084d912c8`

> ⇒ Với rig boss 1, **chỉ tồn tại 2 tên**: `Stop` và `Banplasma` — nên 2 slot chuỗi của
> `BossSpineEventHandler` **chắc chắn** lấy từ tập này (mức **A** cho *tập ứng viên*). Còn **slot nào
> là tên nào** thì vẫn **B**. Đọc thêm: `Stop` nằm trong `Attack3` (12,667 s) cách nhau ~2,4 s ⇒ nó là
> nhịp **tắt/bật một bộ phận** giữa đòn, khớp với hành vi `set_enabled` ở bảng trên.

**[docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md:12–12](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/64d3dd21054b6e8756abd8a1b9b5c83ec7133cc6/docs/apk-analysis/157-g3-boss39001-spine-callback-completion-boundary.md#L12-L12)** · quote SHA-256 `b17f8613652981a4cb3f14288b16f396df0b1447ed3213f5dbd57ea7aa92d74d`

> **The event-name-slot join remains unresolved.** The checked serialized `m_Script` pointers have blank `target_class` values, and the bounded instance inventory has no `BossSpineEventHandler` instance/value set on Boss-39001. The shared Spine data path alone does not supply that missing handler/callback identity.

### H4-18 — P2 / PARTIALLY_SYNCED: Stop identity correct, normative encoding explanation lags R1 correction

ANIMATION_SCRIPT169-176 correctly retains static Stop and unmeasured invocation, but still describes kind5 addend as literal address without the encoded-usage step. Corrected ef123 and DATA_SYNC24.91 say the addend cell holds a0003ca7/kind5/index7763, not rawUTF8. No literal-value reversal is needed.

**Suggested producer-owned correction:** Clarify RELA->encoded usage cell->metadata literal payload->Stop, retaining the same identity and dispatch boundary. Do not globally reinterpret other literal records from this one slot.

**[docs/spec/ANIMATION_SCRIPT.md:170–176](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/ANIMATION_SCRIPT.md#L170-L176)** · quote SHA-256 `2db926bd35dd8ec670de73a40e95f4dcb79360754eeb125e9af6b2ee6d84d373`

> qua RELA gốc → literal **`Stop`** (report **123-ef6b75ef**: native-relocations 288.733 entries
> pin `0x2ADFB48→0x2BE5CB8` · 3 cells.json cùng RELA hex `48fbad02…b85cbe02…` @offset 3.563.112 ·
> `stringliteral.json` độc lập `0x2BE5CB8→"Stop"` · literal index 7763 bytes `53746f70`; join 1-1
> theo địa chỉ, kind-5 addend = địa chỉ literal). **Chỉ là literal identity** — KHÔNG phải method
> pointer / delegate đã đăng ký / invocation / runtime event ⇒ **dispatch = `MODEL_NOT_MEASURED
> runtime`**. `Banplasma` vẫn **chưa bind** slot nào (asset-level marker). `BossSpineEventHandler`
> vẫn **0 instance export** ⇒ §T1 của `HANDOFF_ANIM_RAW.md`.

**[docs/apk-analysis/123-ef6b75ef-native-vtable-linkage.md:48–48](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/ea6a3835f786306b07df9658262a6e3f6658f809/docs/apk-analysis/123-ef6b75ef-native-vtable-linkage.md#L48-L48)** · quote SHA-256 `ff15d8b7f4d98ebd74356e1b29395465f6b2df2519d5296b49e6f2a0f6654633`

> The RELA addend `0x2be5cb8` itself contains encoded metadata usage `0xa0003ca7` (kind5/index7763/lowbit1), not raw UTF-8 `Stop` bytes; `Stop` is the metadata literal payload at index7763. Therefore the bounded static answer is: **callback slot0x2ADFB48 resolves through original RELA to string literal `Stop`.** This is a literal identity, **not** a decoded native method pointer, a proven `RegisterEvents` delegate, a game-side caller, a runtime invocation or a Unity readback. Callback registration/dispatch/live state remain `MODEL_NOT_MEASURED runtime`. No whole-library absence claim is made and no a5 artifact was modified.

### H4-19 — P2 / DRIFT: Broken internal locators: slot/vtable correction points to rank section24.87

DATA_SYNC24.90 points resolved Stop to24.87 and24.91 says correction applied at24.87(b); DONE repeats24.87(b). Header24.87 is rank API, while slot/vtable subsection(b) is24.88. The separate MaxRankStars link to24.87 is correct.

**Suggested producer-owned correction:** Change only the two wrong DATA_SYNC references and DONE recap to24.88 (b where relevant). Preserve valid rank-API24.87 references. Header24.87 is physically appended after24.98; resolve by heading, not file order.

**[docs/spec/DATA_SYNC.md:4970–4970](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4970-L4970)** · quote SHA-256 `2d0f929c184fddcd03bf1ec1ab77e542cf08177184e6012ab3be0957bbb302d6`

>   họ (spec-side đã ghi RESOLVED ở §24.87/mục 1b OPEN_ISSUES).

**[docs/spec/DATA_SYNC.md:5013–5015](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5013-L5015)** · quote SHA-256 `527421f374ad84b044ce15bdfdc48c2dd2137a46dedaaaf957747b9b97f71b9b`

>   artifact/handoff): chấp nhận cả 2 điểm ✓. **Spec áp supersede tại đoạn §24.87
>   (b)** — review-swap R1/R2 chứng minh đúng thiết kế.
> - **AI-4 141 GameConfig — ĐÓNG** (HANDOFF `6423847486` @ `a067e254`; runs

**[docs/spec/DONE.md:140–142](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DONE.md#L140-L142)** · quote SHA-256 `5ebd6c17914362ff15568b91427b2dec58e1c10adb58daf32527c8e817327fe0`

> > encoded usage `0xa0003ca7` — ef **CORRECTION123** `ea6a3835f` chấp nhận,
> > scientific không đổi; spec siêu thu §24.87(b) · **141 ĐÓNG**: slot cổng thật
> > `0x2ADBB88` 44940168 + **GameConfig** (1/128 theo bố cục) + đính chính 140 ×2

**[docs/spec/DATA_SYNC.md:5326–5328](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5326-L5328)** · quote SHA-256 `6353c9cf51d61e7abd5f2a9ce10d9e980513fa9bbb1ec465404843fcc9c3023b`

> ### 24.87 Điều phối lần 96 — #136 HANDOFF ĐÓNG (rank API interpreter + 2 đính chính 134/135) · CLAIM 137 · AI-2 memo chưa tới
>
> - **#29-followup AI-4 — HANDOFF #136 `6422732465` @ `efceee587` — ĐÓNG** (runs

**[docs/spec/DATA_SYNC.md:4818–4819](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L4818-L4819)** · quote SHA-256 `80d80fe5531ed82abc8bbde2da74c49b0612bc94f440d86bc5a97c4eb0dff9fc`

> ### 24.88 Điều phối lần 97 — HANDOFF123 ef: SLOT `0x2ADFB48` = `"Stop"` (identity static) · G1 ĐÓNG · sync-review 152 ĐÓNG + áp S1–S3 · 137 ĐÓNG
>

### H4-20 — P2 / PARTIALLY_SYNCED: 145 residual says43 computed although same paragraph and146 say51

DATA_SYNC24.94 correctly reports133/51/0 but leaves an index43computed residual label from144. DATA_SYNC24.96/report146 correctly use51records=39sites. This is a historical breadcrumb inconsistency, not a new numeric/source failure or currently unknown26 calls.

**Suggested producer-owned correction:** Annotate the old residual as superseded51computed; keep51records versus39unique sites and caller/serialized bounds distinct. Runtime values remain unmeasured.

**[docs/spec/DATA_SYNC.md:5140–5146](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5140-L5146)** · quote SHA-256 `63c1a18f308942368a3b69dea92ee4af1d357dec48c700a67a1194ecf56a2068`

>   **literal 133 · computed 51 · unknown 0** · keys 25→28 · prefix 11→12.
>   2 cơ chế: return-of-callee `TimeFreeRewardPack.Key(int slot)` **19.187.948**
>   → `SLOT_FREE_CARDS_` ×8; **static-field ×18 — `stp`-pair là mấu chốt**:
>   `TIME_EVENT_ENDED`+`TIME_EVENT_OPEN` ghi bằng MỘT cặp `stp` (19.464.596) từ
>   `Board_EventSeasonPass..cctor` **19.462.112** — bảng static chỉ đọc `str` thì
>   còn 2 khoá trống (verifier xử lý `str`+`stp` +0/+8). followup-12
>   (`6424465381`) = chính 145 — ACCEPTED. not_decoded còn: index 43 computed +

**[docs/spec/DATA_SYNC.md:5222–5227](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/e301feb409c75527f4c796a4a548093d4b2bf95d/docs/spec/DATA_SYNC.md#L5222-L5227)** · quote SHA-256 `452aaf0e3cf18f045a5cf20ac923e4ca48d93874da96ecd0c6351bde1c35d26a`

>   (23 mới); artifact pulled `d9ff7301…` 4470B khớp ✓): 51 computed = **39 vị
>   trí** (12 nằm 2 raw) — band 12 · parameter 19 · helper 4 · static-field 3 ·
>   struct-field 1; dải shop `i+{100,200,300}` guard rva Arena 22.729.088/
>   22.728.800 · PVP 19.938.144/19.937.856; literal **999** ×20 = **sentinel
>   slot** (không phải quest id). **Đóng = chứng minh biên, KHÔNG liệt kê đủ:**
>   10/14 tiền tố index do caller/dữ liệu ⇒ cần serialized decode. *Cross 999×15/

## 5. Reproduction, local gates and handoff boundary

Artifact: `datas/l3_geometry_docs_sync_round2_8141386a.json.gz` **35847B**, SHA-256 **`51339d7626cadac29b9c6d0e29277c643c15600389ee55efe0bfdf6869d9757f`**. Deterministic gzip/JSON; no timestamps or current branch tip in the text artifact. Source commit identities are fixed, never moved to make a finding disappear.

```sh
python3 -m tools.verify.l3_geometry_8141386a_docs_sync_round2 --check --git
# In a shallow CI checkout only: add --fetch for the four fixed commits, no peer checkout.
python3 -m unittest tests.test_geometry_8141386a_docs_sync_round2 -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 121 --check
```

**Final local:** full **1596 PASS /380.769s**; focused **225 PASS /72.863s**; new H4 **24 PASS /0.391s**; deterministic artifact + all **35 actual pinned Git texts PASS**. Live needles **APKD1(126,107), AI1(139,142136,142,138,42,84), RD1(41,0)**; README **0 drift**. Approved historical-support **209/0/2**, actual unscoped-legacy **163/25/23** (no new failure IDs), frozen baseline **160/27/24** stay separate. Complete final logs and per-claim results are retained in verification121, not substituted for old receipts. Final exact-head CI remains a separate post-push gate; no CI test count is inferred from local totals.

**Local correction history:** the first1596-test full run had one support-adapter SHA failure because the two measured live count blocks were updated but their declared post-import SHA pins were not yet refreshed. Only those declared adapter hashes were updated from actual file bytes; original unrelated expectations/tests were not changed. The subsequent full1596 and focused225 runs above passed. The initial failed log is retained as `reverse-engineering/raw/geometry-8141386a/verification-121-initial-full-failed.log.gz`; it is not presented as a successful gate.

Historical-support209/0/2 is a separate approved compatibility view, not all-current/native/runtime acceptance. The frozen160/27/24 baseline is not rewritten. Preserve120/119/118 scientific receipts and actual CI capsules; no SDK budget change (600MiB), protected-file changes, screenshot gate, runtime/device dispatch, peer edit or branch takeover. Final formal PR12 `review:` HANDOFF requires pushed exact-head Verify/scoped/PR15 actual GREEN; device skips never count as runtime proof.

## 6. Additive producer response — baseline matrix is not rewritten

After the baseline review and final local suites, producer [ACK110/6425974530](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6425974530) reported all7 fixes. A **separate manual text-only follow-up** checked the six affected spec documents at **`6d501153e825a6935f1d4d1a48e32a0b394f751a`** against actual Git bytes. The requested substantive edits are present in all7 cases; this is not a new native review or a complete spec audit. The main35-document/20-assertion/72-citation artifact and its13/4/3 baseline classifications stay frozen; its no-applied-correction limitation describes that original baseline, not this later supplement.

| Original item | Observed producer text at fixed6d501153e |
|---|---|
| H4-01 | Requested substantive edit present; [MISSING_FOR_NEW_GAME.md:164–164](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/MISSING_FOR_NEW_GAME.md#L164-L164); [MISSING_FOR_NEW_GAME.md:169–169](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/MISSING_FOR_NEW_GAME.md#L169-L169); [BALANCE.md:1586–1586](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/BALANCE.md#L1586-L1586) |
| H4-06 | Requested substantive edit present; [ANIMATION_SCRIPT.md:54–54](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/ANIMATION_SCRIPT.md#L54-L54) |
| H4-07 | Requested substantive edit present; [DESIGN_READINESS.md:27–30](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/DESIGN_READINESS.md#L27-L30) |
| H4-08 | Requested substantive edit present; [ANIMATION_SCRIPT.md:191–195](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/ANIMATION_SCRIPT.md#L191-L195) |
| H4-18 | Requested substantive edit present; [ANIMATION_SCRIPT.md:172–175](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/ANIMATION_SCRIPT.md#L172-L175) |
| H4-19 | Requested substantive edit present; [DATA_SYNC.md:4970–4970](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/DATA_SYNC.md#L4970-L4970); [DATA_SYNC.md:5013–5014](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/DATA_SYNC.md#L5013-L5014); [DONE.md:161–161](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/DONE.md#L161-L161) |
| H4-20 | Requested substantive edit present; [DATA_SYNC.md:5146–5147](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/6d501153e825a6935f1d4d1a48e32a0b394f751a/docs/spec/DATA_SYNC.md#L5146-L5147) |

**Remaining P2 citation cleanup, not a new behavior finding:** MISSING/BALANCE newly label G1 as `153/G1` or `153/G1+G2`. Selected153 is the Endgame/G2 report. Cite G1 HANDOFF6422888569 at`3122c4ac6175460151c50adfde99fee54ed40a00`, DATA_SYNC24.88 and prior109/122 for Board_Players UI; retain153/G2 for Endgame. This does not reverse the consumer or combat boundary. No new claim is made about later spec heads.

Supplement `reverse-engineering/raw/geometry-8141386a/docs-sync-round2/producer-followup.json.gz`: **298690B**, SHA-256 **`b239d9332f92eeca137153dc8ffa0962f5ef1c7895c15a998074bebda32d5917`**. It retains six complete after-texts with commit/blob/SHA/line identities and11 exact quote receipts. This supplement was checked manually with `git show` plus quote/line/hash reconstruction; the baseline automatic checker intentionally does not claim those extra texts as its35 inputs. Producer/source ownership and #27/runtime limits remain unchanged.
