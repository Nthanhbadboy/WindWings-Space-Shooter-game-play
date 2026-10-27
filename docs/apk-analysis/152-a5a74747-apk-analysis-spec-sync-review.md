# APK analysis ↔ SPEC sync review

**Review base:** `b405a8b167ad92493e412f1b362e70e83a310915` · **Scope:** #27-GS Boss/Spine/animation analysis, reports 142–151, and the corresponding `docs/spec/` summary, animation, handoff, and issue-tracking documents. Static/document review only; no binaries, runtime workflow, native/FDE data, or new source evidence inspected.

## Verdict: partially synced, not safe to treat as fully reconciled

The artifact index in `docs/spec/START_HERE.md` is current through phases 11–22 and generally preserves the evidence limits. The detailed SPEC and its README are not fully aligned: the key driver split is corrected later in `ANIMATION_SCRIPT.md` but contradicted by its opening summary; the same file still promotes `Stop`/`Banplasma` from asset/UI candidates into a likely `BossSpineEventHandler` mapping; and `OPEN_ISSUES.md` has no tracked item for the unresolved Boss-39002 callback slot.

The analysis reports are more careful than some of the prose they are meant to inform. Fix those summary-level contradictions before using the SPEC as the implementation contract. This review records recommendations; it does not rewrite the existing SPEC sections.

## Findings and suggested edits

| Priority | SPEC location | Sync finding | Evidence and recommended correction |
|---|---|---|---|
| **P0** | `docs/spec/ANIMATION_SCRIPT.md:16–18`, contradicted by `:309–328`; `docs/spec/README.md:89` | Opening summary says Boss-39001 and Boss-39002 are both driven by `Boss1_Director`. The later §3.4 correctly says they are separate prefabs with separate drivers. README repeats the stale summary. | Reports 142–144 keep the routes separate: Boss-39001 has `Boss_1_Animation` at serialized path 674445, with `SkeletonAnimation` component 602882 and `parentDestroy` 601110; Boss-39002 has `Boss1_Director` at path 582209, `SkeletonAnimation` 664302, and `parentDestroy` 601111. Both reference the shared Spine asset, which does not merge their component identity. Keep §3.4’s route table and replace the opening/README wording with it. |
| **P0** | `docs/spec/ANIMATION_SCRIPT.md:164–185`, `:492` | The text says `attackEventName` is probably `Banplasma`, `preAttackEffectEventName` probably `Stop`, and that the two handler values “certainly” come from those two rig events. This is stronger than the evidence. | Reports 142–149 do not bind `BossSpineEventHandler` to a Boss-39002 instance or resolve slot `0x2ADFB48`. The `Stop` UI Animator match is explicitly contextual only (146–147); path-918 `Stop`/`Banplasma` markers are asset-level evidence. Phase 20 disclosed a marker in an explicitly excluded native-relocation export but did not parse/use it; phases 21–22 closed only the permitted text-source census. Replace slot-value assertions with **UNRESOLVED**; retain `Stop` and `Banplasma` only as unjoined candidates and do not transfer Boss-39001 handler assumptions to Boss-39002. |
| **P1** | `docs/spec/ANIMATION.md:106–121`, `:393–417` | The rig-level event inventory is useful, but “mốc bắn nằm ngay trong rig,” “đủ tên + thời lượng + mốc event,” and the one-prefab `skeleton__21` wording can be read as proving the callback/receiver path. | Keep the asset facts, but label them as **Spine TextAsset timeline only**. State that shared asset/rig identity is not listener binding, callback-key identity, playback, or runtime effect. Report 143 records both prefab references to asset 580611 / JSON 918 while retaining separate components. |
| **P1** | `docs/spec/HANDOFF_ANIM_RAW.md:40–89`; summary `docs/spec/README.md:95` | The handoff still presents the Boss-39001 `BossSpineEventHandler` value lookup and `Stop`/`Banplasma` falsification as though it could settle the Boss-39002 callback slot. The newly completed phase chain is not represented there. | Split the handoff’s open work by route: (a) Boss-39001 handler identity/instance/serialized values; (b) Boss-39002 `Boss1_Director` slot `0x2ADFB48`. Add the bounded result from 142–151 and say that repeating the same permitted corpus search is not a next step. Any new source must be identified and separately authorized; the excluded native-relocation item remains out of this review’s scope. |
| **P1** | `docs/spec/OPEN_ISSUES.md` (no `Boss-39002`, `BossSpineEventHandler`, or `0x2ADFB48` entry) | The primary unresolved callback-key result appears in the report index but not in the SPEC’s central open-issues list. | Add a scoped unknown: **Boss-39002 Spine callback event key — unresolved**; include checked scope (reports 143–151), `Stop` as candidate only, native-relocation boundary, and a “reopen only on new permitted/authorized evidence” condition. Do not mark this as a global-absence result. |
| **P2** | `docs/spec/README.md:89–95`; `docs/spec/START_HERE.md:64–75` | `START_HERE` indexes phases 11–22 accurately; README’s animation summaries do not reflect the separate drivers or the unresolved key. Its HANDOFF summary also says “4 tasks” while listing T1–T5, whereas the current file headings are T1–T4 plus T4b; reconcile task naming/count rather than preserving two incompatible lists. | After the P0/P1 corrections, refresh the README summaries and line/table counts. Preserve the current `START_HERE` phase rows; they are the best-synced part of this set. |

## Recommended small-task breakdown

Keep synchronization and evidence acquisition separate so documentation work does not imply new analysis.

| Task | Scope / output | Dependency | Done when |
|---|---|---|---|
| **S1 — Correct route summary (docs-only, first)** | Update `ANIMATION_SCRIPT.md` opening summary and README to use the existing two-row driver table from §3.4. | None; reports 142–144 already contain the evidence. | No summary says both prefab routes use `Boss1_Director`; shared Spine asset is stated separately from component/driver identity. |
| **S2 — Correct event-key confidence (docs-only, first)** | Rewrite `ANIMATION_SCRIPT.md` §2.2 and the confidence table; add a short asset-vs-callback caveat to `ANIMATION.md`. | S1 is independent; use reports 145–149. | No exact value is assigned to `0x2ADFB48`; `Stop`/`Banplasma` are explicitly candidates only; no delivery/playback claim. |
| **S3 — Repair tracking and handoff (docs-only)** | Add the unresolved item to `OPEN_ISSUES.md`; separate Boss-39001 from Boss-39002 in `HANDOFF_ANIM_RAW.md`; refresh `docs/spec/README.md`. | S1/S2 wording agreed. | Open work has distinct route, scope, owner/dependency, and acceptance criteria; no duplicate search of the closed corpus is queued. |
| **E1 — Boss-39001 handler binding (separate evidence task)** | Resolve handler script/instance/value only for the Boss-39001 route, or record a bounded unresolved result. | A new eligible serialized source/export from the responsible data lane; do not reuse Boss-39002 evidence. | Component/prefab identity and values are either directly joined and source-pinned, or explicitly remain unknown. |
| **E2 — Boss-39002 slot resolution (blocked, not assigned to this branch)** | Seek a new, permitted source for `0x2ADFB48`; otherwise leave it unresolved. | New source provenance and explicit authorization if it touches the native-relocation/FDE lane. | A direct slot-to-literal mapping is demonstrated from an allowed source; otherwise the status remains `UNRESOLVED`. No runtime or AI-1 native work under current constraints. |
| **E3 — Runtime binding/playback (separate gate, currently closed)** | No task now. Only reopen by a new project decision and approved vehicle/evidence path. | Explicit authorization; not a dependency for S1–S3. | If reopened, report runtime readback separately from static asset markers. Until then, do not claim delivery, playback, effect, or DPS. |

### Suggested order

1. Land S1–S3 as one small documentation synchronization change (no raw export and no change to the analysis findings).
2. Keep E1 and E2 as independent, source-gated requests; do not combine them merely because the prefabs share Spine asset 580611.
3. Leave E3 closed. The existing evidence supports an asset timeline and a conditional callback body, not a runtime behavior claim.

## Source-of-truth pointers

- Current analysis: `docs/apk-analysis/142-...` through `151-...`; especially reports 143 (separate prefab routes), 147 (no metadata slot bridge), 149 (allowed text-corpus boundary), 150 (baseline `datas/`), and 151 (no residual eligible export).
- Current artifact index: `docs/spec/START_HERE.md:64–75`.
- SPEC sections needing review: `ANIMATION_SCRIPT.md:16–18, 141–190, 309–328, 489–503`; `ANIMATION.md:106–121, 393–422`; `HANDOFF_ANIM_RAW.md:40–89`; `OPEN_ISSUES.md`; `docs/spec/README.md:89–98`.
