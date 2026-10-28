# Phase C — store assets spec and listing-copy draft

**Owner:** @a5<br>
**Coordination:** Board-Delta132–135; claim [PR12 comment 6442380896](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6442380896)<br>
**Status:** planning draft; not an upload package, final artwork, or rights clearance<br>
**Copy language:** English working draft; localization and store character-limit checks are still required.

## 1. Scope and launch assumptions

This document prepares the asset handoff and draft copy for the three Phase C channels:

1. **Microsoft Store — Windows PC:** planned **free-to-play with in-app purchases, no ads**; no Windows build is present in this repository.
2. **Amazon Appstore — Fire tablet first:** mobile free-to-play, optional rewarded-first ads; Fire TV and Vega are deferred.
3. **Huawei AppGallery — outside mainland China:** mobile free-to-play, optional rewarded-first ads.

The planned port engine is Godot 4.x LTS; this is a plan, not a build in this repository ([Board-Delta134](https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-6441940333)). The launch configuration follows D1/D2/D3/D6/D7/D8/D10 in the Phase B decisions: no paid loot boxes; no Windows ads; Fire tablet first; mainland China excluded. These are product decisions, not proof that the release build already implements them. Listing copy must be re-checked against the submitted build before publication.

Store commerce must follow the relevant channel (Board-Delta135): Amazon IAP for Amazon digital purchases; HMS IAP Kit and Petal Ads for AppGallery; `Windows.Services.Store` for Microsoft Store. Do not imply Google Play Billing or an external checkout on these listings. The planned rewarded-first ad language is not a license to bypass each store's commerce or ad rules.

**Explicit boundaries:** no new APK/probe analysis; no new art or image exports; no modification of the 23-Oct capture; no SDK, account, signing, build, upload, or publishing work. Nothing here establishes rights to the `WindWings` name, GCenter art, or game content.

## 2. What the existing visual material can and cannot support

### Repository inventory

| Source | Observed inventory | Use in this plan |
|---|---|---|
| `docs/apk-analysis/ramus/2026-10-23-phone/` | Report 166 pins 84 files: 43 JSON, 35 PNG, 3 Markdown, 3 logs. All 35 PNGs are 720×1496 portrait. Capture package is a modded/repackaged 1.0.69 build; official comparison assets are 1.3.118. | Private visual references only. The screenshots are not same-build proof for the planned Windows, Fire, or Huawei releases. Do not publish them as final store screenshots. |
| `docs/assets/contact-sheets/` | 42 JPEG preview sheets, each 1200 px wide; sheet heights vary. | Internal layout/color references only; the sheets are not source-resolution store art. |
| `docs/assets/INDEX.md` | Indexes 2,197 assets (133.6 MB) and points to a separate full-size artifact/release. It explicitly says the original images/audio are copyrighted by GCenter and are design references, not package content. | Do not retrieve, crop, trace, export, or package the original art until the user confirms rights for the name, art, and game content (Phase C USER-ONLY #3). |

The capture-folder manifest remains the one recorded in Report 166: 84 files, 23,793,059 bytes, SHA-256 `19fcf9eb4792651993f61400de9c4167dd11cd820473fbcf2c9f3c8793871787`. No source image has been changed for this task.

### Candidate references — not cleared for publication

| Purpose | Internal reference | Assessment |
|---|---|---|
| First gameplay-frame concept | `live_1_Game.png` (720×1496) | Clear gameplay composition with player ship and planetary horizon; use only to understand framing. Re-capture from the release build after rights clearance. |
| Action-frame concept | `live_6_Game.png` (720×1496) | Enemy formation and active combat are visible without a tutorial card; useful as a framing reference, not a final image. Re-capture on each target device/build. |
| Ship/icon composition study | `docs/assets/contact-sheets/ships-01.jpg` with `background-01.jpg` | A small ship silhouette against a distinct space field is a legible composition direction. Do not cut out or reuse these copyrighted sprites. |
| Wide promotional composition study | `ships-01.jpg`, `bosses-01.jpg`, `background-01.jpg`, and `fx-01.jpg` | A single readable ship, one boss/formation, and restrained effects could work as a wide composition if the rights holder approves. This is a layout note only; no composite or new artwork was made. |

**Exclude from any listing draft or future asset pick:** tutorial-overlay captures (`screenshot_running_stage1.png`, `p_2_Game.png`, `r2_1_Game.png`); the Premium welcome screenshots (`boss_now.png`, `live_2_EndGame.png`–`live_5_EndGame.png`, and the `victory_*` set); and any image that implies an entitlement, price, reward, performance, or feature not present in the release build. The Premium text belongs to the modded capture and is not validated as a live offer or entitlement.

## 3. Store asset specification — requirements intentionally left source-verifiable

Exact current pixel dimensions, file formats, screenshot counts, and feature-graphic availability are **UNVERIFIED** in the available asset index and Phase C assignment snapshot. Do not substitute remembered or third-party numbers. Session F should fill the numeric columns from each store's current official listing guidance, record the source URL and access date, and check requirements for the actual product type and target devices before art production.

| Store / launch target | Required asset slots to verify | Composition and capture direction | Current blockers |
|---|---|---|---|
| **Microsoft Store / Windows PC** | Confirm Partner Center icon/logo slots, accepted formats, screenshot count and pixel ranges; confirm whether this product type requires or accepts a separate hero/feature image. Record exact values and source. | Use landscape Windows gameplay captures from the submitted Windows build; show clean combat and a readable ship/boss scale. Prepare a square icon as a separate asset, not a screenshot crop. No Windows gameplay capture exists in the 23-Oct folder. | Final Windows build and user confirmation of IP/distribution rights. Do not convert the 720×1496 phone screenshots into purported Windows screenshots. |
| **Amazon Appstore / Fire tablet** | Confirm Fire Appstore icon, screenshot count/orientation/resolution, and any feature-graphic/promotional slots for a tablet listing. Record exact values and source. | Capture on the supported Fire tablet target. Lead with legible in-game action; use a separate square icon. Do not reuse phone captures as tablet evidence without a final-device recapture. | Fire-target build/testing; exact current listing requirements; user confirmation of IP/distribution rights. Fire TV/Vega are not launch targets in this plan. |
| **Huawei AppGallery / outside mainland China** | Confirm AppGallery icon, screenshot count/orientation/resolution, and any promotional-image slots for the applicable markets and language. Record exact values and source. | Capture the final HMS build on supported phone/tablet targets; keep screenshots free of tutorial prompts and unverified offers. Use a separate square icon and only create a wide promo image if the current listing requires one. | Final HMS build/testing; exact current listing requirements; user confirmation of IP/distribution rights. Mainland China is out of launch scope. |

### Design and quality rules for Session F

- Keep app icon, gameplay screenshots, and any wide promo/feature image as distinct deliverables; do not repurpose a contact sheet as a listing image.
- Use only art with documented distribution rights. The existing index identifies the current reference art as GCenter-copyrighted; until the user clears rights, all references stay internal and no export is allowed.
- Use release-build captures for screenshots. Capture each target platform/device after the actual build exists; do not imply that the 23-Oct modded Android capture is the Windows, Fire, or HMS release.
- Prefer clean, uncluttered gameplay. No tutorial overlays, Premium welcome modal, fake device frames, fabricated ratings, price badges, unsupported rewards, or unimplemented control/feature claims.
- Keep text minimal and readable at thumbnail size. Avoid putting required store copy inside the image; preserve platform-specific safe areas once F verifies them.
- Do not promise cross-device/cloud-save support, offline play, controller support, localization, frame rate, or a specific content count: none is cleared for this listing draft.

## 4. English listing-copy drafts

The working title **WindWings** is subject to Phase C USER-ONLY #3 rights confirmation and store-title availability. The copy below is product-plan copy, not a statement that any build is release-ready. Do not submit it until the final build, platform requirements, and rights are checked.

### Microsoft Store — Windows PC (free-to-play + IAP, no ads)

**Title:** WindWings *(working title; rights clearance required)*

**Short description:**

A free-to-play vertical arcade shooter with no ads. Pilot a starfighter, weave through enemy fire, and face boss encounters. Optional in-app purchases unlock progress and convenience; no paid loot boxes.

**Long description:**

Take command of a starfighter in a vertically scrolling arcade shooter. Dodge enemy formations, fire through incoming waves, and face boss encounters. The planned Windows edition is a free-to-play release with in-app purchases and no ads. No paid loot boxes.

**Do not add yet:** any price (app or in-app), supported Windows versions, controller or cloud-save claims, exact stage/ship counts, or a feature graphic whose requirement has not been verified.

### Amazon Appstore — Fire tablet (free-to-play, rewarded-first)

**Title:** WindWings *(working title; rights clearance required)*

**Short description:**

Pilot a starfighter through fast vertical battles. Dodge enemy fire, clear formations, and challenge boss encounters. Optional rewarded video.

**Long description:**

Launch into a vertical arcade space shooter. Pilot your starfighter through enemy formations, dodge incoming fire, and take on boss encounters. The planned Fire tablet release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.

**Do not add yet:** Fire TV/Vega availability, forced-ad claims beyond the approved rewarded-only design, price/SKU details, device-compatibility lists, or unverified tablet-specific features.

### Huawei AppGallery — outside mainland China (free-to-play, rewarded-first)

**Title:** WindWings *(working title; rights clearance required)*

**Short description:**

Pilot a starfighter through fast vertical battles. Dodge enemy fire, clear formations, and challenge boss encounters. Optional rewarded video.

**Long description:**

Launch into a vertical arcade space shooter. Pilot your starfighter through enemy formations, dodge incoming fire, and take on boss encounters. The planned AppGallery release is free to play, with optional, opt-in rewarded video ads. No paid loot boxes.

**Do not add yet:** mainland-China availability, price/SKU details, HMS device-compatibility claims, or named ad/IAP providers. Exact market/language coverage and privacy disclosures remain subject to the per-store requirements work.

## 5. Session F handoff / next checks

1. Confirm current official listing requirements for each store and product type: image slots, counts, minimum/maximum pixel dimensions, aspect ratios, file formats, alpha/transparency, localization rules, and any hero/feature-image slot. Record URL and access date; mark inaccessible or conflicting guidance `UNVERIFIED`.
2. Turn the slot matrix above into a per-store export checklist only after those requirements are source-checked.
3. Request user confirmation of name/art/content distribution rights before selecting or exporting original GCenter assets. If rights are not cleared, replace them with user-owned/licensed assets; do not trace the contact sheets.
4. Once a final Windows/Fire/HMS build exists, capture truthful platform/device-specific gameplay and review the copy against the build. No capture from the modded 1.0.69 package is an acceptable substitute.
5. Session F retains the separate conversion-research queue (genre CTR/A-B thumbnail benchmarks and listing-transition checklist); this a5 deliverable does not invent or claim conversion uplift.
6. Present final artwork and copy for user approval at Gate 5. Do not upload or publish without the user's explicit action/authorization.

## 6. Readiness

- **Spec and three listing drafts:** prepared.
- **Exact per-store image dimensions/counts/formats:** `UNVERIFIED`; pending official-source check by the asset planner.
- **Final art and screenshots:** blocked by rights confirmation and final target builds.
- **Publishing/submission:** user-only; not authorized by this document.
