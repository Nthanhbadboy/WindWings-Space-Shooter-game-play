# Boss-37001 — animation prototype

**Review prototype, not a runtime capture or gameplay implementation.** The source artworks were generated separately; `manifest.json` lists source SHA-256, paths, 512×512 registration, estimated pivots and spawns. Boss-layer PNGs share one canvas and are ordered hull → left pod → right pod → left turret → right turret → core → cannon. Damage overlay and effects are additional; the charge ring is drawn on top of the boss in telegraphs. The hull center is closed by generated armor. Left/right pods are independently generated and now visually similar; seams, rotation and fit still need art review. Pivot and muzzle coordinates are approximate and should be rechecked by the coder in the real engine.

## Preview timeline (120 frames / 10 seconds / 12 fps)

- **0.00–1.50 s:** boss enters from above, charge-ring warning. Boss settles at 1.10 s.
- **1.50–3.25 s:** twin side turrets oscillate ±18° and fire four alternating energy orbs and short laser bolts, every 0.48 s. Charge precedes this first attack.
- **3.00–4.00 s:** visible ring warns of the main beam (the last short-burst projectile overlaps the start of this warning).
- **4.00–5.90 s:** continuous beam sweeps from −25° to +25° around estimated cannon muzzle; origin effect overlays its base.
- **5.90–6.45 s:** charge ring warns of missile launch.
- **6.45–8.25 s:** both pods launch four missile pairs every 0.33 s, flying downward and outward.
- **8.00–8.35 s:** low-health warning ring; 8.00–10.00 s damage/smoke overlay and blinking core. **8.35–10.00 s:** fast alternating short burst at 0.30 s intervals. Player ship follows a programmed dodge path throughout; no collision or AI simulation. The player uses a 34 px canvas on a 480 px playfield (approximately 1.4 / 20).

`boss-fight-preview.gif` is a mockup using the final exported PNGs and the approved player export, not a recording of gameplay. GIF uses centisecond durations 80/90/80 ms, repeated, totaling 10.00 s; `boss-fight-frame-sheet.jpg` samples every sixth frame (20 frames). The visual construction uses `build-preview.py` with Pillow, NumPy and SciPy. UI bars and labels are explanatory only. Ring/shockwave/beam effects have transparency reconstructed from dark-background intensities and may need production VFX blending. The beam source was crossfaded at its vertical ends; exported strip has equal end rows, but runtime filtering and tiling have not been tested. Low-health smoke is composited twice for greater visibility; it still needs art review at gameplay scale. No claim of planner pass, in-engine hitbox correctness, or seamless turret rotation.
