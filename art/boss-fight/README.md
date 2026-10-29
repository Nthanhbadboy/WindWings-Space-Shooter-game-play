# Boss-37001 fight — prototype for review

- `masters/`: separately generated raw images, including previous rejected candidates, `round2/` and `round3/`; `manifest.json` identifies the selected sources and SHA-256. Raw sources are not alpha exports.
- `exports/boss-bare-hull.png`, `exports/boss-composite.png`, `exports/boss-layers/`: common 512×512 transparent boss layers and fixed composite.
- `exports/effects/`: individual sprites; energy and missile 64×64, laser bullet 64×128, beam strip 64×256 with matched end rows.
- `boss-fight-preview.gif`: 10 s / 12 fps mockup, composited from these exports and the approved player. `boss-fight-frame-sheet.jpg`: 20 samples.
- `manifest.json` and `ANIMATION_NOTES.md`: layer order, tentative pivot/spawn coordinates and timing; `build-preview.py` reproduces this prototype.

**STATUS: CHƯA XONG / prototype needs review.** This is not a commercial-ready or engine-tested asset pack. The latest hull has a closed center and no protruding gun; the matching pods are independently generated. Attachment seams and rotating turret pivots remain unverified in engine. VFX matting and halo need visual QA, especially at gameplay scale and on light backgrounds. The GIF is a mockup, not code-driven gameplay; no planner pass is asserted. Earlier rejected attempts are retained for provenance in `masters/`; see `review/source-overview.jpg` and `review/round2-overview.jpg`.

## Round 4 update

The closed-armour hull and matching right pod replace the previous candidates; the preview and frame sheet have been rebuilt from the updated exports. Estimated turret pivots were moved upward toward the rotating bases and pod projectile spawn points were adjusted. `review/halo-64px.png` supplements the light/dark full-size check. User approval and in-engine verification remain outstanding.

`boss-fight-github.gif` is the smaller GitHub-viewing copy of the preview (320×467, 64-color palette, 120 frames, 10 s). This copy is reduced for browser display, not a replacement for the full-size source exports or `boss-fight-preview.gif`.
