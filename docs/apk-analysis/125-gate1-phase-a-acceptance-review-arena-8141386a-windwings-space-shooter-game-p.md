# 125 — Gate-1: independent acceptance-style Phase-A package review

**Provenance:** `arena/8141386a-windwings-space-shooter-game-p`

## Kết luận ngắn

**Verdict: `NOT_READY` — tại source-cut đã ghim.** Gói bằng chứng hiện tại còn **5 điều kiện chặn** để trở thành một đề xuất acceptance nhất quán: (1) phân xử149↔169/177 về blob thưởng PvP; (2) registry cuối/phân loại build-data vs served/runtime; (3) một profile acceptance L1/L2/L3 hiện hành; (4) gỡ kết luận vắng-mặt-toàn-game suy từ139 export; (5) giới hạn phát biểu ceiling theo scope và ghi rõ phần static còn giao/hoãn. **Không cần mở lại device/native lane để sửa những phát biểu này.**

Đây là review độc lập cho director/user, **không tự ACK Phase A, không tự duyệt Gate-1, không cho phép triển khai game/SDK hay phát hành**. Báo cáo này có thể được thảo luận tại Gate-1; `NOT_READY` nghĩa là gói nguồn chưa nhất quán để đề nghị chấp nhận vô điều kiện, không phải cấm research/plan đã được cho phép. User giữ quyền quyết định phạm vi và chấp nhận rủi ro.

CLAIM [6439774919](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6439774919); director assignment [6439014055④](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6439014055); progress [6440055528](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6440055528). Prior124 accepted by spec6438111504 / board6438111906: #27 review queue6/6 stays closed **bounded**, never full/runtime closure.

## 1. Source cut, authority and exact scope

- Current spec snapshot: **`12ccdc52006f898c6e67260910af23df18840c40`**. Its211-check source, all36 claim-target files, CI workflow and current mandate/readiness/director summaries are retained.
- Specialist publication cut: **`22a94737713e1509dcf983e6d4b83ed6c30773f4`**. Selected complete reports149/150/152/157/158/169–177 and four small published registry/result artifacts are retained, not their raw/native dependencies.
- **61 complete source snapshots**, original commit/path/Git blob/source+gzip SHA/size in `reverse-engineering/raw/geometry-8141386a/gate1-phase-a/peer-pins.json`. Actual `git show commit:path` bytes checked for all61; no peer checkout, whole-tree import or tool overwrite.
- Actual director mandate/assignment, accepted124 ACK and current producer numeric-table API snapshots are pinned separately. Spec CI40483833755 is actual completedSUCCESS at the pinned spec head; PR16 metadata is an actual OPEN+DRAFT vehicle snapshot at the specialist cut. **No CI test count is inferred.**

**Methods:** AST/literal-only catalogue of the whole declared check stream (producer code never imported/compiled/executed), exact row-order/CID comparison to the supplied published result table, review of the selected current normative/specialist publications, manual acceptance/evidence matrix and source-bound conflict receipts. **Not done:** fresh evaluation of producer measure callbacks, raw/native/controller/serialized/phone measurements, business/store research, or new game implementation. Existing regression tests remain tests, not new game evidence.

All211 declaration rows are catalogued, but this is not a claim that every source/data/runtime fact was independently rerun or that every overclaim anywhere in the repository was found. Identified current counterexamples suffice for `NOT_READY`. This review does not erase accepted prior static evidence merely because it is not remeasured here.

## 2. What “209 claims pass” actually means at this cut

| View | Exact count / scope |
|---|---|
| Literal top-level `claim(...)` registration rows | **211** |
| Distinct CID strings | **209** |
| Reported result rows | **209 PASS · 2 SKIP** (0 reportedFAIL/ERROR) |
| Distinct IDs with onlyPASS rows | **207** |
| Intentionally skipped IDs | **B9** loop/source metadata, **F4** Sprite-export assertion |
| Reused IDs | **GE1×2, GE2×2**, both occurrences preserved |
| Complete claim-target files | **36** |
| Producer measures independently rerun in125 | **0** |

The repeated GE anchor checks are not automatically invalid; they are **not four extra independent facts or fresh runtime proof**. The catalogue uses `CID#occurrence`, exact declaration lines/hash, original literal type/value, measure expression and function-object binding where applicable. It preserves both occurrences rather than losing rows in a dict keyed only byCID. Unknown lambda/global/factory inputs are not guessed as complete provenance.

Actual supplied table is comment6370275480, fingerprint **`24a80490968024da8af9c064250917d6cb41cf6c5e957c8fcfe42d4bb33ffe31`**, updated **2026-10-27T09:50:43Z**. Joining211rows by ordinal/CID proves table/declaration coverage, **not immutable code/data/input-head provenance or an independent rerun**. The table is an upsert without a complete per-input source manifest. The source workflow best-effort-fetches a mutable data ref, runs default local-first measurement and requires no-SKIP only for prefixesAB/AO/AP (FAIL/ERROR still fail across all selected rows). Both intentionalSKIPs remain visible.

Own approved **historical-support209/0/2** is a different frozen compatibility snapshot. It is never substituted for this current producer stream, Phase-A acceptance or native/runtime parity. “Review/check PASS” means reproducible catalogue/source/curation, not Gate-1 approval.

## 3. Evidence/acceptance matrix across Phase A

**Labels:** Six mandated labels grade the type/scope of cited published evidence and known gaps. Unless explicitly stated, underlying raw/physics facts are inherited publications, not independently rerun. Source/quote identity and catalogue coverage ARE checked here.

In the table below, `STATIC_CONFIRMED` / `RUNTIME_CONFIRMED` describe the bounded kind/applicability of the cited published evidence; `independent_remeasurement=false` is retained for every domain. Historical runtime remains cross-build-only and does not establish official1.3.118 parity. Conflicts are actual publication contradictions; this reviewer does not silently pick a raw derivation winner.

| Domain | Evidence type / acceptance scope | Qualification |
|---|---|---|
| D01 Core loop / win-loss / tutorial | STATIC_CONFIRMED / SUPPORTED_BOUNDED | Published static flow/predicates are usable reference; no new same-build gameplay execution here. [GAMEPLAY.md:1–1](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/GAMEPLAY.md#L1-L1) |
| D02 Controls / feel / feature absence | CONFLICTING / CONFLICTING | Design exclusion is distinct from global original-feature absence; G1-04. [DESIGN_READINESS.md:173–173](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L173-L173); [DESIGN_READINESS.md:174–174](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L174-L174) |
| D03 Combat / balance / DPS | RUNTIME_UNVERIFIED / PARTIAL | Published constants/index mappings are not live DPS/TTK/time-series parity. [COVERAGE_AUDIT.md:37–37](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L37-L37) |
| D04 Enemy roster / trajectories / state | STATIC_CONFIRMED / SUPPORTED_BOUNDED | Counts/captured paths do not establish full timing/state coverage. [COVERAGE_AUDIT.md:38–38](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L38-L38) |
| D05 Boss phases / delegates / callbacks | UNKNOWN / PARTIAL | Static source/entry names present; six trigger strings/twelve delegate bindings and conditions remain scoped gaps. [DESIGN_READINESS.md:264–264](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L264-L264) |
| D06 Waves / maps / spawn timing | INFERRED / PARTIAL | Published mapping/census useful; rate0 same-frame/scheduling and current coverage summaries must stay separate. [START_HERE.md:109–111](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/START_HERE.md#L109-L111) |
| D07 Persistence / first-run schema | STATIC_CONFIRMED / SUPPORTED_BOUNDED | Eight-family contract is explicitly partial, not complete live save/migration schema. [START_HERE.md:49–49](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/START_HERE.md#L49-L49) |
| D08 Economy / reward arrays / progression | CONFLICTING / CONFLICTING | 149 vs169/177 must be reconciled before authoritative economy appendix. [149-535b0541-pvp-hunter-arrays.md:48–48](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/149-535b0541-pvp-hunter-arrays.md#L48-L48); [149-535b0541-pvp-hunter-arrays.md:49–49](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/149-535b0541-pvp-hunter-arrays.md#L49-L49) |
| D09 Shop defaults vs served state | CONFLICTING / CONFLICTING | Static defaults and runtime overrides cannot be collapsed to globally served-only/absent data. [170-535b0541-audit-refresh.md:75–75](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/170-535b0541-audit-refresh.md#L75-L75); [157-535b0541-shop-ctor-timer.md:25–25](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/157-535b0541-shop-ctor-timer.md#L25-L25) |
| D10 UI layout / visual policy | STATIC_CONFIRMED / SUPPORTED_BOUNDED | Layout/source metrics are reference, not rendering approval or future new-product UI decision. [COVERAGE_AUDIT.md:45–45](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L45-L45) |
| D11 Assets / pixel / geometry / nativeL3 | RUNTIME_UNVERIFIED / PARTIAL | Own accepted bounded sources/fixtures remain evidence, not full native object/renderer/runtime completion. [START_HERE.md:87–87](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/START_HERE.md#L87-L87) |
| D12 Audio / FX trigger and curves | UNKNOWN / PARTIAL | Asset/scalar inventory exists; trigger/curve conditions remain scoped unknown. [COVERAGE_AUDIT.md:47–47](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L47-L47); [COVERAGE_AUDIT.md:48–48](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L48-L48) |
| D13 Archived runtime corroboration | RUNTIME_CONFIRMED / SUPPORTED_BOUNDED | Historical1.0.69 capture only; official1.3.118 target parity remains RUNTIME_UNVERIFIED. [CROSSCHECK-static-vs-runtime.md:13–16](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/apk-analysis/ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md#L13-L16) |
| D14 Registry / coverage / ceiling | CONFLICTING / CONFLICTING | Final registry and literal ceiling/readiness scope are not coherent acceptance metadata yet. [DESIGN_READINESS.md:307–307](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L307-L307); [175-535b0541-report-table.md:17–17](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/175-535b0541-report-table.md#L17-L17) |
| D15 Product scope and gate authority | INFERRED / REQUIRES_USER_DECISION | Research permitted; PhaseA acceptance, ProductBrief/business/architecture/MVP/release still user decisions. [PROJECT_DIRECTOR_MANDATE.md:58–66](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/PROJECT_DIRECTOR_MANDATE.md#L58-L66) |
| D16 Validation stream and reproducibility | STATIC_CONFIRMED / SUPPORTED_BOUNDED | Complete declaration/report-status catalogue, not raw-fact or gameplay remeasurement. [docs-verify.yml:79–79](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/.github/workflows/docs-verify.yml#L79-L79) |

## 4. Five blocking source/scope conditions, eight total findings

**P1 conditions below require a producer/director resolution or an explicitly proposed user decision, not invented data, forced measurement expectations or unauthorized runtime reopening.** P2 items are precision/reproducibility recommendations; they do not reopen closed scientific reviews.

### G1-01 — P1 / BLOCKING — PvP build arrays: decoded149 versus unbound169/177 on shared declared inputs

**Evidence label:** `CONFLICTING` · **Owner:** AI-4 producer, reconciled by director · **Condition:** `G1-C1`

Published149 explicitly supplies rewardValues/rewardScales for ctor19796420 at offsets416/424. Published169/177 say the same blobs are unbound and require metadata usage. Both artifacts declare the same relevant input digests. This review does not choose which derivation is correct or independently re-decode raw.

**Exit / requested correction:** Publish an authoritative source-bound reconciliation/erratum for149 vs169/177, retain historical outputs, and propagate the chosen scope to final registry/economy appendix. Do not invent fresh numbers or reopen device probing merely to resolve published evidence.

**Exact pinned sources:** [149-535b0541-pvp-hunter-arrays.md:48–48](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/149-535b0541-pvp-hunter-arrays.md#L48-L48); [149-535b0541-pvp-hunter-arrays.md:49–49](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/149-535b0541-pvp-hunter-arrays.md#L49-L49); [149-535b0541-pvp-hunter-arrays.md:33–33](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/149-535b0541-pvp-hunter-arrays.md#L33-L33); [169-535b0541-pvp-reward-arrays.md:23–23](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/169-535b0541-pvp-reward-arrays.md#L23-L23); [177-535b0541-pvp-array-init.md:59–59](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/177-535b0541-pvp-array-init.md#L59-L59)

### G1-02 — P1 / BLOCKING — Registry verdict/index freshness is not the final Phase-A gap ledger

**Evidence label:** `CONFLICTING` · **Owner:** AI-4 registry producer + director · **Condition:** `G1-C2`

170/3b782ffa is explicitly a snapshot. Current audit contracts still assign shop data to served payload and PvP blob links to POLICY;177 says PIN-RAW and157/158 publish static constructor defaults. Report175 filling the report-name index does not change verdict bytes. Final registry-v4/open count is assigned but not yet a valid final handoff at this cut.

**Exit / requested correction:** Publish one versioned final registry with authoritative closures/restatements and separate shipped defaults, served overrides, missing source and policy/runtime states. Keep old registry historical; do not use index49/43 coverage as semantic closure proof. Final open need not be zero.

**Exact pinned sources:** [170-535b0541-audit-refresh.md:75–75](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/170-535b0541-audit-refresh.md#L75-L75); [175-535b0541-report-table.md:17–17](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/175-535b0541-report-table.md#L17-L17); [177-535b0541-pvp-array-init.md:49–49](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/177-535b0541-pvp-array-init.md#L49-L49); [157-535b0541-shop-ctor-timer.md:25–25](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/22a94737713e1509dcf983e6d4b83ed6c30773f4/docs/apk-analysis/157-535b0541-shop-ctor-timer.md#L25-L25)

### G1-03 — P1 / BLOCKING — Acceptance target and all-non-art/all-number completion statements conflict with declared limitations

**Evidence label:** `CONFLICTING` · **Owner:** Director/spec; user decides target and waivers · **Condition:** `G1-C3`

START_HERE says art is the only design work; DESIGN_READINESS declares no numbers missing forL2, yet the same source retains limited/cross-build playback, partial boss conditions and L3 gates not run. The new mandate requires reviewed findings, Product Brief/business/architecture/MVP approvals before implementation. Technical L1 readiness is not authorization or a full L2/L3 evidence contract.

**Exit / requested correction:** Publish one current acceptance profile: which L1/L2/L3 claims are findings, proposed new-design choices or deferred unknowns; remove universal all-number/only-art wording unless narrowly scoped. Preserve user authority and planning-only boundary; do not silently downgrade target or reopen runtime.

**Exact pinned sources:** [START_HERE.md:11–13](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/START_HERE.md#L11-L13); [DESIGN_READINESS.md:295–296](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L295-L296); [DESIGN_READINESS.md:264–264](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L264-L264); [PROJECT_DIRECTOR_MANDATE.md:58–66](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/PROJECT_DIRECTOR_MANDATE.md#L58-L66)

### G1-04 — P1 / BLOCKING — A139-file method-name/timeScale census is promoted to whole-game feature absence

**Evidence label:** `CONFLICTING` · **Owner:** Spec/acceptance summary producer · **Condition:** `G1-C4`

AF2/AF3 check zero token/name matches in139 exported asm files. DESIGN_READINESS turns that bounded evidence into global hit-stop/aim-assist absence and says three features do not exist. A user decision to omit feel is a design exclusion and may stand, but is not proof of absence in the original whole game.

**Exit / requested correction:** Qualify absence to the inspected export/name/token scope; keep unmeasured gameplay/runtime evidence UNKNOWN or RUNTIME_UNVERIFIED and retain feel omission as an explicit user/design decision. No new runtime measurement is required to correct the text.

**Exact pinned sources:** [DESIGN_READINESS.md:173–173](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L173-L173); [DESIGN_READINESS.md:174–174](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L174-L174); [DESIGN_READINESS.md:177–177](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L177-L177); [verify-claims.py:3574–3574](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/tools/verify-claims.py#L3574-L3574); [verify-claims.py:4142–4142](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/tools/verify-claims.py#L4142-L4142)

### G1-05 — P1 / BLOCKING — Literal no-static-work ceiling conflicts with named remaining static questions

**Evidence label:** `CONFLICTING` · **Owner:** Director/spec; assigned specialists retain their own lanes · **Condition:** `G1-C5`

The readiness ceiling says every doable static item is closed and static analysis cannot increase readiness, while the same section names six SetTrigger strings and twelve delegate assignments; the director explicitly assigns those static tasks and registry finalization. Review#27 6/6 is valid bounded review completion, not proof that every static gameplay question or L3 build path is complete.

**Exit / requested correction:** Qualify ceiling to the reviewed scope/evidence tier and list deferred/assigned static work with impact and owner. Do not reopen accepted#27 science or require endless analysis; explicitly ask user whether residuals are accepted exclusions before Phase-A acceptance.

**Exact pinned sources:** [DESIGN_READINESS.md:307–307](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L307-L307); [DESIGN_READINESS.md:305–305](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L305-L305); [6439014055:6–6](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6439014055)

### G1-06 — P2 / PRECISION — Current coverage/readiness denominators and historical headers are inconsistent

**Evidence label:** `CONFLICTING` · **Owner:** Spec summary producer · **Condition:** `G1-Q1`

COVERAGE_AUDIT opens with43docs/30data/176checks and14 regions10/3/1, whereas its table/readiness tally has15 rows11/4/0 and the current check stream has211 evaluations. Table rows for map/HP and later paragraphs disagree about closed vs missing. These are not new data discrepancies; the acceptance summary must distinguish old snapshots from current metrics.

**Exit / requested correction:** Issue one current dated coverage table with explicit row/exclusion definitions; label old counts and superseded map/HP blockers historical. Do not change source data or expected values to match stale prose.

**Exact pinned sources:** [COVERAGE_AUDIT.md:9–10](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L9-L10); [COVERAGE_AUDIT.md:21–21](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L21-L21); [COVERAGE_AUDIT.md:41–41](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L41-L41); [COVERAGE_AUDIT.md:42–42](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/COVERAGE_AUDIT.md#L42-L42); [DESIGN_READINESS.md:285–285](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L285-L285)

### G1-07 — P2 / PRECISION — 209PASS is211 evaluations/209IDs, with two SKIPs and no immutable table-to-input binding

**Evidence label:** `UNKNOWN` · **Owner:** Spec verification/reporting producer · **Condition:** `G1-Q2`

The source has211 registrations,209 unique IDs, GE1/GE2 each twice; the supplied numeric table reports209PASS/2SKIP. Unique passed IDs are207, B9/F4 are SKIP. The CI fetches a mutable data-branch name best-effort and runs the default local-first checker with required no-skip prefixesAB/AO/AP. The mutable upsert table has no exact code/data input manifest in its body. Actual CI success is confirmed, not all209 independent/raw/runtime facts.

**Exit / requested correction:** Use occurrence-qualified row keys and explicit evaluation-vs-unique counts. Preserve both SKIPs; attach a versioned source/ref/provenance receipt to the acceptance package or explicitly label the table reported/not rebound. Do not treat own historical-support209/0/2 as current-producer or native acceptance.

**Exact pinned sources:** [docs-verify.yml:50–58](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/.github/workflows/docs-verify.yml#L50-L58); [docs-verify.yml:79–79](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/.github/workflows/docs-verify.yml#L79-L79); [verify-claims.py:82–82](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/tools/verify-claims.py#L82-L82); [6370275480:224–224](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6370275480)

### G1-08 — P2 / PRECISION — Boss summary still needs serialized-field vs callback-invocation precision

**Evidence label:** `INFERRED` · **Owner:** Spec acceptance-summary producer · **Condition:** `G1-Q3`

DESIGN_READINESS top correctly qualifies burst+78 as serialized field/target, not proven invocation, but row4 still abbreviates the state route as defeat/burst arrow. Carry the accepted H4/#27 qualifications into the acceptance matrix: names/serialized routes are not complete boss sequences, handler binding or runtime delivery.

**Exit / requested correction:** Use explicit static/serialized route and not-invocation wording in the table too. Preserve accepted bounded findings, without new native/runtime work or reopening old reviews.

**Exact pinned sources:** [DESIGN_READINESS.md:28–30](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L28-L30); [DESIGN_READINESS.md:89–89](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/DESIGN_READINESS.md#L89-L89)

## 5. Detailed PvP conflict receipt — same context, no winner selected

Published149 `034bb93b…` assigns `rewardValues=[100,10000,10,100,10,10]` and f32 `rewardScales=[1,1,.6,1,.6,.8]` in ctor19796420, offsets416/424. Published169 `cb3711ec…` instead leaves four float candidates/unread blob links;177 narrows the blocker to PIN-RAW/build data but still explicitly says specific values are NOT_BOUND. The exact constructor/store/field context agrees.

Both result records **declare** matching input digests (not a fresh rehash by this review):

| Common declared input | SHA-256 |
|---|---|
| `datas/l2_535b0541_pvp_hunter_reward_table.json.gz` | `4649f273aacb59fa063e691d5d2726aab932bc8da48174668963887fa5bdfa79` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `reverse-engineering/il2cpp/field-defaults.json` | `05a51c9bc32bd5f0c42ef4822e36f838dab931ec2213298a56d3aaf6e7be4d27` |
| `reverse-engineering/raw/arena-pvp-535b0541/native.json.gz` | `3197425a010a0c60c94e01bc23043af9c8cdb924f48bafab7958fee9e0e8cfb8` |
| `reverse-engineering/raw/key-grant-535b0541/native.json.gz` | `3f43642ab14858f205d99a6b63c93ba5fa601d3ae1318e1f2b3948a729c23ffb` |

`982` PID fields in169 versus `740` in149 is not by itself proof of conflicting data: the published census scopes may differ and are not adjudicated here. The blocking inconsistency is **published binding/value availability** for the same constructor/offset/source identities, not a naïve difference in denominators. Later report177 does not explicitly reconcile/overturn149; exact source snapshots remain available for producer adjudication. **Do not feed either side as authoritative to the Phase-B economy appendix until the published conflict is resolved.** No raw token map/native decoder was rerun here.

## 6. Boundaries that remain accepted

- **Accepted#27 review queue6/6 stays bounded** (`STATIC_CONFIRMED`): Actual specACK124 records independent erratum verification and6/6 review queue with null-path/heap/runtime limits. This acceptance review does not reopen or promote it. [6438111504:3–4](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6438111504)
- **Historical capture is cross-build only** (`RUNTIME_CONFIRMED`): The published CROSSCHECK explicitly names runtime1.0.69 vs static1.3.118 and says agreement corroborates, not same-build parity. Preserve that scope; no device session is opened here. [CROSSCHECK-static-vs-runtime.md:13–16](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/apk-analysis/ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md#L13-L16)
- **User authority and research-only mandate are explicit** (`STATIC_CONFIRMED`): Mandate keeps current phaseA, approvals/gates and research-only planning before implementation/SDK/release. Gate1 recommendation is not selfACK. [PROJECT_DIRECTOR_MANDATE.md:20–20](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/PROJECT_DIRECTOR_MANDATE.md#L20-L20); [PROJECT_DIRECTOR_MANDATE.md:88–88](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/PROJECT_DIRECTOR_MANDATE.md#L88-L88)
- **L3 source/model/inventory is not render approval** (`STATIC_CONFIRMED`): START_HERE distinguishes modeled/source-only arithmetic, unknown identities and gates not run. Preserve those caveats rather than using counts/CI as completion percentages. [START_HERE.md:13–14](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/spec/START_HERE.md#L13-L14)
- **PR16 remains a draft CI vehicle, not merge/acceptance evidence** (`STATIC_CONFIRMED`): Actual PR16 metadata is OPEN+DRAFT and body says not for merge; director describes it as a vehicle. A stale body/report number does not invalidate accepted specialist evidence or authorize merge. [DIRECTOR_STATUS_2026-10-27.md:42–42](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/12ccdc52006f898c6e67260910af23df18840c40/docs/DIRECTOR_STATUS_2026-10-27.md#L42-L42)

PR16 is OPEN+DRAFT with a historical127-era body and newer head; “CI green”/a PR existing is not acceptance or merge authorization. Its meaningful content must be referenced through the correct scoped publications/handoffs. Invalid `@/tmp/…` comments do not publish the missing handoff text. File presence alone is not an ACK. The new product three-store commercial work remains in its assigned research lane and is not revalidated here.

## 7. Recommended Gate-1 exit/decision checklist

| Required before coherent acceptance proposal | Owner / exact exit |
|---|---|
| G1-C1 (G1-01) | AI-4 producer, reconciled by director: Publish an authoritative source-bound reconciliation/erratum for149 vs169/177, retain historical outputs, and propagate the chosen scope to final registry/economy appendix. Do not invent fresh numbers or reopen device probing merely to resolve published evidence. |
| G1-C2 (G1-02) | AI-4 registry producer + director: Publish one versioned final registry with authoritative closures/restatements and separate shipped defaults, served overrides, missing source and policy/runtime states. Keep old registry historical; do not use index49/43 coverage as semantic closure proof. Final open need not be zero. |
| G1-C3 (G1-03) | Director/spec; user decides target and waivers: Publish one current acceptance profile: which L1/L2/L3 claims are findings, proposed new-design choices or deferred unknowns; remove universal all-number/only-art wording unless narrowly scoped. Preserve user authority and planning-only boundary; do not silently downgrade target or reopen runtime. |
| G1-C4 (G1-04) | Spec/acceptance summary producer: Qualify absence to the inspected export/name/token scope; keep unmeasured gameplay/runtime evidence UNKNOWN or RUNTIME_UNVERIFIED and retain feel omission as an explicit user/design decision. No new runtime measurement is required to correct the text. |
| G1-C5 (G1-05) | Director/spec; assigned specialists retain their own lanes: Qualify ceiling to the reviewed scope/evidence tier and list deferred/assigned static work with impact and owner. Do not reopen accepted#27 science or require endless analysis; explicitly ask user whether residuals are accepted exclusions before Phase-A acceptance. |

**Separate user decisions (not made by this review):**

- **U1** — Choose and approve the current fidelity/acceptance profile (L1/L2/L3), known exclusions and consequences for the future product; do not infer from old labels.
- **U2** — Accept or defer named runtime/same-build/owner/playback gaps without silently reopening the owner-closed device lane.
- **U3** — Only after reviewed findings decide Phase-A acceptance; ProductBrief/business model/architecture/MVP/implementation/release retain separate later approval gates.

Allowed while resolving these conditions: versioned documentary reconciliation, registry finalization, Product-Brief/commercial/economy research already authorized, and preparing a decision package. **Not authorized by a review result:** new-game implementation, ads/payments/production analytics integration, original-game re-release, runtime/device/secrets work, merging/closing PRs, or user acceptance. Do not turn “static ceiling” into an instruction to invent raw values or launch prohibited probes.

## 8. Deterministic artifact and validation

Artifact `datas/l3_geometry_gate1_phase_a_8141386a.json.gz`: **92399B**, SHA-256 **`4a2a60e52123ab6ccaa6c6a9c75da78da7e8d0997b209e995b8608485b5887ae`**. Includes all211 original declaration/result rows,8findings/5blocking conditions,5preserved boundaries,16domain rows,59exact quote receipts, common-input publication comparison and metadata scope. The source/quote checker validates identity/coverage/bookkeeping; human acceptance judgments are deliberately not claimed as machine semantic truth.

```sh
python3 -m tools.verify.l3_geometry_8141386a_gate1_phase_a --check --git
python3 -m unittest tests.test_geometry_8141386a_gate1_phase_a -v
python3 -m tools.verify.geometry_8141386a_history --fetch
python3 -m unittest discover -s tests -v
python3 tools/refresh-readme-sizes.py --check
python3 tools/verify-claims.py --require APKD1,AI1,RD1
python3 -m tools.verify.geometry_8141386a_item_receipt --item 125 --check
```

**Final local:** full **1710 PASS /391.054s**; focused **339 PASS /87.819s**; new **33 PASS /16.284s**; deterministic artifact and **61 actual selected Git source identities PASS**. Current own live **APKD1(130,107), AI1(139,142136,142,138,42,88), RD1(41,0)**; README **0 drift**. Approved historical-support **209/0/2**, actual own unscoped **163/25/23**, no new failure IDs, frozen baseline **160/27/24** remain separate from the producer211-row stream. Verification125 retains complete logs/per-claim support results and exact historical-support snapshot/path set. Final exact-headCI/formalHANDOFF remain post-push gates. Passing reviewer/checker CI is compatible with `NOT_READY`: it proves reproducibility, NOT that acceptance conditions are satisfied or that a user Gate/PhaseA approval occurred.

Original124 actual exact-head CI is frozen before new live needles in `scientific-ci-124.json.gz`, preserving spec127 externalACK of the bounded#27review6/6. Closed #4–8/118–124 evidence/code/artifacts/scientific receipts/logs remain immutable and actual-Git checked; no old receipt regeneration or unrelated expected/test repair. Protected3 unchanged; SDK600MiB unchanged; no original APK/assets, wholeGraph/atlas fixture, peer tool overwrite/checkout, implementation, screenshot gate, runtime/device reopening, branch switch, merge/close/release or selfACK.

## Appendix A — whole declared-check catalogue (NOT raw fact remeasurement)

Every row below is the producer check design plus its **reported** result. It is not a fresh measurement or an independent Gate-1 truth label. Full original declaration/measure expression/quoted status/hash is in the artifact; this compact table truncates display only.

| Key | Reported | Target | Stated literal | Measurement design (display) |
|---|---|---|---|---|
| A1#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 21 | lambda: len(phone_files_with_fields()) |
| A2#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 575 | lambda: len(reals()) |
| A3#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 88 | lambda: sum(1 for _, _, v in reals() if is_type_only(v)) |
| A4#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 10 | lambda: (phone_json("statics_Device_Get_Data.json") or {})       .get("fields", {}).get("listStatValues_count") |
| A5#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 250 | lambda: (phone_json("statics_Map_Get_Datas.json") or {})       .get("fields", {}).get("listMapDatas_count") |
| A6#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 128 | lambda: len((phone_json("statics_Map_Get_Datas.json") or {})                   .get("fields", {}).get("listMapDatas") or []) |
| A7#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | [0.5,0.6,0.4,0.8,1] | lambda: (phone_json("statics_Device_Get_Data.json") or {})       .get("fields", {}).get("percentByLevels1") |
| A8#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | [0.1,0.1,0.3,0.4,0.5] | lambda: (phone_json("statics_Device_Get_Data.json") or {})       .get("fields", {}).get("percentByLevels2") |
| A9#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/SUMMARY_vi.md` | 65 | lambda: len((phone_json("statics_GP_Datas.json") or {}).get("fields", {})) |
| A10#1 | PASS | `docs/apk-analysis/ramus/2026-10-23-phone/CROSSCHECK-static-vs-runtime.md` | 10 | lambda: (phone_json("statics_Device_Get_Data.json") or {})       .get("fields", {}).get("listStatValues_count") |
| B1#1 | PASS | `docs/spec/ANIMATION.md` | 27 | lambda: agg(ref_json(SPINE), lambda d: len(d.get("rigs", []))) |
| B2#1 | PASS | `docs/spec/ANIMATION.md` | 185 | lambda: agg(spine_totals(), lambda t: t.get("animations")) |
| B2b#1 | PASS | `docs/spec/ANIMATION.md` | 180 | lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(           len(r.get("animations") or {}) for k, r in d.get("rigs", {}).items() if k != "Saw")) |
| B3#1 | PASS | `docs/spec/PIPELINE_AUDIT.md` | 12274 | lambda: agg(spine_totals(), lambda t: t.get("keyframes")) |
| B3b#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 12274 | lambda: agg(spine_totals(), lambda t: t.get("keyframes")) |
| B4#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 21 | lambda: agg(spine_totals(), lambda t: t.get("events")) |
| B5#1 | PASS | `docs/spec/ANIMATION.md` | 616 | lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(           int(r.get("bones_total") or 0) for r in d.get("rigs", {}).values())) |
| B6#1 | PASS | `docs/spec/ANIMATION.md` | 446 | lambda: agg(ref_json(SPINE_ANIM), lambda d: sum(           int(r.get("slots_total") or 0) for r in d.get("rigs", {}).values())) |
| B7#1 | PASS | `docs/spec/ANIMATION.md` | 791 | lambda: agg(clips(), len) |
| B8#1 | PASS | `docs/spec/ANIMATION.md` | 226 | lambda: agg(clips(), lambda cs: len({c.get("name") for c in cs})) |
| B9#1 | SKIP | `docs/spec/ANIMATION.md` | 251 | lambda: (_ for _ in ()).throw(NoSource(           "không nguồn: anim_clips.json không có trường loop, typetree native-types "           "có m_Wra |
| B10#1 | PASS | `docs/spec/ANIMATION.md` | 318 | lambda: agg(clips(), lambda cs: sum(1 for c in cs if c.get("events"))) |
| B11#1 | PASS | `docs/spec/ANIMATION.md` | 793 | lambda: agg(clips(), lambda cs: sum(len(c.get("events") or []) for c in cs)) |
| B12#1 | PASS | `docs/spec/ANIMATION.md` | 1.9 | lambda: agg(clips(), lambda cs: round(           statistics.median([c["duration"] for c in cs if "duration" in c]), 1)) |
| B13#1 | PASS | `docs/spec/ANIMATION.md` | 75.0 | lambda: agg(clips(), lambda cs: max(c["duration"] for c in cs if "duration" in c)) |
| B14#1 | PASS | `docs/spec/ANIMATION.md` | [203,87] | animators_on_roster |
| B15#1 | PASS | `docs/spec/ANIMATION.md` | 109 | lambda: None if wave_roster() is None else len(wave_roster()) |
| B16#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | [154,63] | lambda: agg(amap_rows(), lambda rows: (           sum(1 for r in rows if len(r) > 2 and re.match(r"^(CB-\|Boss-\|MB-)", r[2])),           len({r[2] |
| B17#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | [92,36] | lambda: agg(amap_rows(), lambda rows: (           sum(1 for r in rows if len(r) > 2 and r[2].startswith("Boss-")),           len({r[2] for r in r |
| C1#1 | PASS | `docs/spec/ANIMATION.md` | 27 | rig_assets |
| C2#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 4 | attack_rigs |
| C3#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 23 | lambda: None if attack_rigs() is None else 27 - (attack_rigs() or 0) |
| C4#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 18 | lambda: (bone_match() or (None, None))[0] |
| C5#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 914 | lambda: (appear_stats() or (None, None))[0] |
| C5b#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 0 | lambda: (appear_stats() or (None, None))[1] |
| C6#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 17 | lambda: count_lines("reverse-engineering/raw/typetrees/Enemy_HitSkeletonRenderer.jsonl.gz") |
| C7#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | true | lambda: None if ref_lines("reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz") is None else True |
| F1#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 981 | lambda: count_lines("reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz") |
| F2#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 46 | lambda: (ref_json("datas/bosses.json") or {}).get("count") |
| F3#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 39 | boss_prefab_roots |
| F4#1 | SKIP | `docs/spec/ANIMATION.md` | 2185 | lambda: (_ for _ in ()).throw(NoSource(           "không nguồn: native-types chỉ có 5 loại type (Animator/ParticleSystem/"           "AnimationCl |
| C8#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 26 | lambda: None if ta_names() is None else len(           [n for n in ta_names() if n.startswith("skeleton") and n.endswith(".json")]) |
| D1#1 | PASS | `runtime-probe/RamusBridge.cs` | true | lambda: local_has(BRIDGE, 'case "GET /anim"') |
| D2#1 | PASS | `runtime-probe/collect.sh` | true | lambda: local_has(COLLECT, 'get "/anim?max=') |
| D3#1 | PASS | `runtime-probe/collect.sh` | true | lambda: local_has(COLLECT, '"playback":["anim-ingame.json"]') |
| D4#1 | PASS | `.github/scripts/build-bridge.sh` | 5 | lambda: sum(1 for ln in (open(os.path.join(ROOT, BUILD), encoding="utf-8")                                .read().splitlines() if os.path.isfile( |
| D5#1 | PASS | `runtime-probe/README.md` | true | lambda: local_has("runtime-probe/README.md", "/anim?name=") |
| E1#1 | PASS | `docs/spec/DIFFICULTY_MODES.md` | 4 | lambda: pfield_where(STAGE, "boss_boss_stagedata.json")("MaxModeIndex") |
| E2#1 | PASS | `docs/spec/BALANCE.md` | [1,2,3.6,3.6] | pfield(STAGE_GET, "levelDelta") |
| E3#1 | PASS | `docs/spec/BALANCE.md` | 2500 | pfield(PLAYER, "StartHp") |
| E4#1 | PASS | `docs/spec/BALANCE.md` | 0.18 | pfield(PLAYER, "stepCommon") |
| E5#1 | PASS | `docs/spec/BALANCE.md` | [1.35,1.6,1.86] | pfield(PLAYER, "shipCloneDamage") |
| E6#1 | PASS | `docs/spec/BALANCE.md` | 50 | pfield(TECH, "DeltaStarCost") |
| E7#1 | PASS | `docs/spec/BALANCE.md` | 30 | pfield(TECH, "StartStarCost") |
| E8#1 | PASS | `docs/spec/BALANCE.md` | [10,20,30,60,120,250,500] | pfield(DRONE, "MaxLevelPerRanks") |
| E9#1 | PASS | `docs/spec/MISSIONS_STARS.md` | [0.2,0.6,0.98] | pfield(PLAYER, "PercentToCompleteMissions222") |
| E11#1 | PASS | `docs/spec/MISSIONS_STARS.md` | 31 | lambda: len(pfield(STAGE_GET, "listIgroneEnemies")() or []) |
| E12#1 | PASS | `docs/spec/MISSIONS_STARS.md` | 31 | lambda: len(pfield(STAGE_GET, "listIgroneEnemies")() or []) |
| G1#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 20 | lambda: None if spine_instance_paths() is None else len(spine_instance_paths()) |
| G2#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | ["Boss-39001"] | lambda: rig_prefab(580611) |
| G3#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | ["Boss-39003"] | lambda: rig_prefab(580613) |
| G4#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | ["Popup_UnlockShip"] | lambda: rig_prefab(580619) |
| G5#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | ["Popup_UnlockShip"] | lambda: rig_prefab(580623) |
| G6#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 39 | appear_subclasses |
| G7#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | true | appear_asm_is_delegate |
| G8#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 580611 | lambda: boss_rig("Boss-39002") |
| G10#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 3 | lambda: None if spine_prefabs() is None else len(spine_prefabs()) |
| G11#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 580611 | lambda: boss_rig("Boss-39001") |
| G12#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | 580613 | lambda: boss_rig("Boss-39003") |
| G13#1 | PASS | `docs/apk-analysis/37-animation-event-receivers.md` | 711 | lambda: (event_receiver_stats() or (None, None, None))[1] |
| G14#1 | PASS | `docs/apk-analysis/37-animation-event-receivers.md` | 84 | lambda: (event_receiver_stats() or (None, None, None))[2] |
| G9#1 | PASS | `docs/spec/ANIMATION_GAPS.md` | ["Boss-39002"] | lambda: _boss1_director_root() |
| H1#1 | PASS | `docs/spec/ANIMATION.md` | [39,33] | lambda: None if wave_roster() is None else tuple(           sum(1 for e in wave_roster() if e.startswith(p)) for p in ("Boss-", "CB-")) |
| H2#1 | PASS | `docs/spec/ANIMATION.md` | [22451,282,11089] | lambda: _wave_counts() |
| H3#1 | PASS | `docs/spec/ANIMATION.md` | 182 | lambda: enemy_prefab_roots() |
| I1#1 | PASS | `docs/spec/DESIGN_READINESS.md` | 5 | display_fields |
| I2#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [795,795] | events_with_time |
| I3#1 | PASS | `docs/spec/DESIGN_READINESS.md` | 2366 | lambda: (spawner_rate_zero() or (None, None, None))[1] |
| I4#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [250,7] | map_candidates |
| J1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [33,793,2] | _boss_events |
| J2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [146,137,56,50] | lambda: _boss_fn_counts(("OnStartAttack", "OnAnimationEndedEvent",                                "OnStateExit", "OnStopAttack")) |
| J3#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 129 | boss_fn_distinct |
| J4#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [268,61] | clip_pairs |
| J5#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 0 | boss1_clip_events |
| J6#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 5 | boss_work_compares |
| J7#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [12,28] | boss1_event_handlers |
| J8#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [38,12,26] | wait_for_seconds |
| J9#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [0.5,0.05] | enemy_hit_flash |
| J10#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 3 | enemy_move_branches |
| K1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | ["Xuathien","Baydi","Dead","Attack1","Attack2","Attack3","Chuyensangattack2","Chuyensangattack3"] | boss1_states |
| K2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | "0x28=Xuathien · 0x30=Baydi · 0x38=Dead · 0x40=Attack1 · 0x48=Attack2 · 0x50=Attack3 · 0x58=Chuyensangattack2  | boss1_offset_names |
| K3#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | "0x28,0x58,0x60,0x30,0x38" | boss_work_compare_offsets |
| K4#1 | PASS | `docs/spec/HANDOFF_ANIM_RAW.md` | true | complete_calls_bosswork |
| K5#1 | PASS | `docs/spec/HANDOFF_ANIM_RAW.md` | 2 | missing_typetrees |
| K6#1 | PASS | `docs/spec/HANDOFF_ANIM_RAW.md` | [12,32,120] | boss1_handler_offsets |
| L1#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [35,4,39] | boss_script_coverage |
| L2#1 | PASS | `docs/spec/DESIGN_READINESS.md` | 125 | ui_screens |
| L3#1 | PASS | `docs/spec/DESIGN_READINESS.md` | ["Boss-37003","Boss-37005","Boss-37006","Boss-37008"] | boss_script_missing |
| M1#1 | PASS | `docs/spec/DATA_SYNC.md` | [1200,23,false] | call_data_schema |
| M2#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [295,6] | call_data_rate0 |
| M3#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [1202,30] | waves_rate0_big |
| N1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [21,6,2] | spine_event_stats |
| N2#1 | PASS | `docs/spec/DATA_SYNC.md` | [797,117,150131,5831] | ui_index_stats |
| N3#1 | PASS | `docs/spec/UI.md` | [11,4,7] | ui_class_gap |
| N5#1 | PASS | `docs/spec/UI.md` | [117,125,114,11,3] | ui_class_overlap |
| P1#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | 43 | doc_inventory |
| P2#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | [2885,2816,2907,2838] | sprite_sizes |
| P3#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | [1416,19,1416] | localization_stats |
| P4#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | [170,71,99] | iap_stats |
| P5#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | [4845,92,150,246,250] | data_counts |
| P6#1 | PASS | `docs/spec/COVERAGE_AUDIT.md` | [55584,8440354,797,150131] | ui_two_levels |
| Q1#1 | PASS | `docs/spec/ASSETS.md` | [67,31.05,60.0] | atlas_pages |
| Q2#1 | PASS | `docs/spec/ASSETS.md` | [632,62.95,111.3] | atlas_totals |
| Q3#1 | PASS | `docs/spec/ASSETS.md` | [18.87,9.0,16.04,7.65] | atlas_capacity |
| Q5#1 | PASS | `docs/spec/ASSETS.md` | [653,632,21] | texture_size_coverage |
| Q4#1 | PASS | `docs/spec/ASSETS.md` | [88,60,28] | oversized_assets |
| R1#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [34,795,97,269,130] | timeline_shape |
| R2#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [534,215,46] | timeline_fn_split |
| R3#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [146,137,56,339] | timeline_top_state |
| R4#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [93,0.17] | timeline_cadence |
| R5#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [3.52,73.17,6.0] | timeline_lengths |
| R6#1 | PASS | `docs/spec/BOSS_ANIM_TIMELINE.md` | [2,1.5,33] | timeline_enemy_row |
| S2#1 | PASS | `docs/spec/DESIGN_QUESTIONS.md` | [48,33,14,1] | design_question_tally |
| S1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [17,17,145,34] | handler_class_join |
| T1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [8,1,8] | boss1_state_values |
| T2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [12,32,120] | delegate_field_names |
| T3#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [5,32,64,2] | spine_handler_fields |
| T4#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [18,16,13] | director_matrix |
| U1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [1335,111,115,1202,114] | persistent_event_stats |
| U2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [52,63,303,395,357,302] | controller_graph_stats |
| W1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [7,5] | settrigger_sites |
| W2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [288,15,49] | trigger_param_stats |
| W3#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [30,23,22,20] | trigger_top_names |
| W4#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 57.29578 | pathfollow_deg |
| W5#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 0.01745 | circle_rad_step |
| W6#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [38,12,26] | waits_seconds_stats |
| X1#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [109,39,70,51,27,19] | enemy_anim_split |
| X2#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | [14,11,10] | enemy_controller_gap |
| X3#1 | PASS | `docs/spec/ANIMATION_SCRIPT.md` | 12 | cd31002_cluster |
| Y1#1 | PASS | `docs/spec/UI.md` | [11,10710,10710,4987,5067,312,317] | drawing_inputs_stats |
| Y2#1 | PASS | `docs/spec/UI.md` | [6,6,6] | tutorial_gate_stats |
| Z1#1 | PASS | `docs/spec/UI.md` | [19,7,6,13,17] | tutorial_text_stats |
| Z2#1 | PASS | `docs/spec/UI.md` | [15,14730,7087,1913,1] | visual_coverage_stats |
| Z3#1 | PASS | `docs/spec/UI.md` | [1,true,true] | endgame_callback_ref |
| AA1#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [15,11,4,0] | coverage_region_tally |
| AA2#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [9,4,4,1] | blocker_tally |
| AB6#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [17,25] | unresolved_sheets_stats |
| AQ4#1 | PASS | `docs/spec/ENCOUNTERS.md` | [11089,23757,45659] | encounters_units |
| AQ5#1 | PASS | `docs/spec/ENCOUNTERS.md` | [150,42,331,190,72,36,36,18,54,27,622,257,42,21,84,42,6,3] | wave_copy_identity |
| AQ6#1 | PASS | `docs/spec/ENCOUNTERS.md` | [16498,4199,1688,686,686] | encounters_types_copies |
| AQ1#1 | PASS | `docs/spec/ENCOUNTERS.md` | [11089,282,22451,1015] | encounters_totals |
| AQ2#1 | PASS | `docs/spec/ENCOUNTERS.md` | [7536,2084,861,327,281] | encounters_types |
| AQ3#1 | PASS | `docs/spec/ENCOUNTERS.md` | [149,149,0,3] | wave_call_data_identity |
| AQ7#1 | PASS | `docs/spec/ENCOUNTERS.md` | [23757,23757,11089] | wave_unit_crosscheck |
| WR7#1 | PASS | `docs/spec/DATA_SYNC.md` | [22451,45659,11089,2,63,603] | wave_unit_stats |
| CM6#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [15,33,43,6,8] | loadout_contract_counts |
| CM7#1 | PASS | `docs/spec/DATA_SYNC.md` | [21,5,0] | raw_manifest_ok |
| IA1#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [576,6,0] | ia_counts |
| IA3#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [5154,253,0] | player_arrays |
| IA2#1 | PASS | `docs/spec/BALANCE.md` | 6 | player_offset_stores |
| IA4#1 | PASS | `docs/spec/BALANCE.md` | [4500,4.8,24,24,1.35,1.86] | player_values |
| IA5#1 | PASS | `docs/spec/BALANCE.md` | [16,8] | player_costs |
| IA6#1 | PASS | `docs/spec/DATA_SYNC.md` | [576,6] | peer_comparison |
| IA7#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [17,623,576,6] | ia_method_records |
| IAB1#1 | PASS | `docs/spec/ENEMY_HP_RUNTIME.md` | [150,30001,38001,150] | enemy_hp_inserts |
| WRH1#1 | PASS | `docs/spec/ENEMY_HP_RUNTIME.md` | [981,865,467] | enemy_hp_csv |
| WRH2#1 | PASS | `docs/spec/ENEMY_HP_RUNTIME.md` | [150,30001,38001,650.0] | enemy_hp_by_id |
| WRH3#1 | PASS | `docs/spec/WHERE_TO_LOOK.md` | [3,41] | enemy_asm_methods |
| WRH4#1 | PASS | `docs/spec/ENCOUNTERS.md` | [0,109] | wave_name_resolution |
| WRH5#1 | PASS | `docs/spec/ENEMY_HP_RUNTIME.md` | [109,108] | spawned_hp_coverage |
| IAB2#1 | PASS | `docs/spec/BALANCE.md` | [5,4,1.0,2.0,3.6] | stage_arrays |
| APKD1#1 | PASS | `docs/spec/START_HERE.md` | [71,107] | apk_doc_counts |
| IA8#1 | PASS | `docs/spec/START_HERE.md` | 0 | hardcoded_pass_counts |
| AU1#1 | PASS | `docs/spec/DATA_SYNC.md` | [65,25,15] | audio_rule_counts |
| AP2#1 | PASS | `docs/spec/DATA_SYNC.md` | [2652,151,321,320] | asset_pack_counts |
| GE1#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [2185,654,66,2185,0] | sprite_geometry_stats |
| GE2#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [144,1550,40,6] | sprite_rotation_stats |
| RD1#1 | PASS | `docs/spec/README.md` | [41,0] | readme_sizes |
| AB1#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [2197,1554,132,16,116,67] | asset_triage_stats |
| AT1#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [2197,340,282,18,13] | atlas_page_stats |
| AB2#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [396,1158] | asset_unclassified_split |
| AB3#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [17,184,16,0,10,113] | asset_sheet_worklist |
| AB4#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [1049,848,131,70,505,33,204,268] | asset_classified_stats |
| AB5#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [448,410,17] | asset_unknown_families |
| AE1#1 | PASS | `docs/spec/ECONOMY.md` | [702,676,26,529,145,14] | drop_placed |
| AE2#1 | PASS | `docs/spec/ECONOMY.md` | [411,23757,246,2094] | drop_spawner_flags |
| AE3#1 | PASS | `docs/spec/ECONOMY.md` | 6 | drop_catalog |
| AF1#1 | PASS | `docs/spec/TUNING_KNOBS.md` | [241,185,46,6,3,1] | camera_vibrate |
| AF2#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [0,139] | timescale_hits |
| AO1#1 | PASS | `docs/spec/ART_STUDY.md` | [2112,12,55,0.483] | art_study_stats |
| AO4#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [781,674,89,0.863] | knn_stats |
| AI1#1 | PASS | `docs/spec/START_HERE.md` | [139,142136,142,126,42,192] | data_inventory |
| AP1#1 | PASS | `docs/spec/DATA_INTEGRITY.md` | [412,272,140] | provenance_check |
| AO2#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [1857,2197,340,165] | classify_stats |
| AO3#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [307,4250,98,64] | split_stats |
| AN1#1 | PASS | `docs/spec/VISUAL_DESIGN.md` | [35,0.4813,0.0571,17.26] | design_metrics |
| AN2#1 | PASS | `docs/spec/VISUAL_DESIGN.md` | [54019,4.05,7.5,0.67] | ui_bbox_stats |
| AM1#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [100896,4020,576] | map_cctor_arrays |
| GE1#2 | PASS | `docs/spec/ASSET_TRIAGE.md` | [2185,654,66,2185,0] | sprite_geometry_stats |
| GE3#1 | PASS | `docs/spec/ASSET_TRIAGE.md` | [1795,390,0] | sprite_rect_fields |
| GE2#2 | PASS | `docs/spec/ASSET_TRIAGE.md` | [144,1550,40,6] | sprite_rotation_stats |
| RB1#1 | PASS | `docs/spec/RAW_AUDIT.md` | [180,3,28,211] | raw_audit_counts |
| CM4#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [8,2,7] | save_contract_stats |
| CM5#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [5,49,5] | player_array_blobs |
| CM1#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [3,13,1] | scene_map_flow_stats |
| CM2#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [1,1,1] | main_cannon_damage_asm |
| CM3#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [3,21,18] | tutorial_gate_stats |
| AM2#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | [2492,6,24] | player_cctor_arrays |
| AM3#1 | PASS | `docs/spec/MISSING_FOR_NEW_GAME.md` | 4 | player_info_fields |
| AG1#1 | PASS | `docs/spec/SCRIPTS.md` | [4,-1] | tutorial_cctor_consts |
| AF3#1 | PASS | `docs/spec/DESIGN_READINESS.md` | [0,139] | aim_hits |
