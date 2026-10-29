# Boss-37001 fight — prototype for review

- `masters/`: separately generated raw images, including previous rejected candidates, `round2/` and `round3/`; `manifest.json` identifies the selected sources and SHA-256. Raw sources are not alpha exports.
- `exports/boss-bare-hull.png`, `exports/boss-composite.png`, `exports/boss-layers/`: common 512×512 transparent boss layers and fixed composite.
- `exports/effects/`: individual sprites; energy and missile 64×64, laser bullet 64×128, beam strip 64×256 with matched end rows.
- `boss-fight-preview.gif`: 10 s / 12 fps mockup, composited from these exports and the approved player. `boss-fight-frame-sheet.jpg`: 20 samples.
- `manifest.json` and `ANIMATION_NOTES.md`: layer order, tentative pivot/spawn coordinates and timing; `build-preview.py` reproduces this prototype.

**STATUS: CHƯA XONG / prototype needs review.** This is not a commercial-ready or engine-tested asset pack. The two pods have very different designs; attachment seams and rotating turret pivots have not been validated. The bare hull has a dark central socket rather than a continuous armor plate, and its nose contains a fixed mechanical protrusion. VFX matting and halo need visual QA, especially at gameplay scale and on light backgrounds. The GIF is a mockup, not code-driven gameplay; no planner pass is asserted. Earlier rejected attempts are retained for provenance in `masters/`; see `review/source-overview.jpg` and `review/round2-overview.jpg`.
