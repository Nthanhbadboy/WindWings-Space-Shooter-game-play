# Boss-37001 — animation prototype

**Review prototype, not a runtime capture or gameplay implementation.** The generated sources and SHA-256 hashes are in `manifest.json`. The 512×512 layers are drawn hull → left pod → right pod → left turret → right turret → core → cannon; damage and effects are additional. Pivot and muzzle coordinates are estimates and need validation in-engine. Both pods are independently generated; attachment seams need review.

## Timeline (216 frames / 18 seconds / 12 fps)

- **0.00–1.50 s:** boss enters with a charge-ring warning.
- **1.50–3.25 s:** side turrets oscillate and fire energy/laser bursts. PLAYER starts counter-fire at 1.70 s; each player shot travels to the core and produces an impact.
- **3.00–4.00 s:** boss charges its beam; a thin guide marks the sweep's starting direction.
- **4.00–5.90 s:** beam sweeps from −25° to +25° around the cannon muzzle.
- **5.90–6.45 s:** lock-on reticle marks the position the missiles will target, and charge ring warns of launch. **6.45–9.10 s:** four missile pairs travel toward that locked position; PLAYER continues moving.
- **8.00–8.35 s:** low-health warning; smoke and blinking core. **8.35–10.30 s:** another fast cannon burst.
- **10.30–11.20 s:** pulse warning. **11.20–12.80 s:** expanding boss shockwave.
- **12.80–15.45 s:** PLAYER continues counterattacking; each impact reduces the displayed health bar. After the last hit, **15.45–17.00 s** shows the boss explosion and fading shockwave; the remainder allows the ending to read.

`boss-fight-preview.gif` uses exported PNG layers, generated VFX and the approved PLAYER export. The 34 px player canvas on a 480 px field approximates the requested 1.4/20 proportion. Its path and projectiles are staged, not actual AI, collision or gameplay. GIF uses 80/90/80 ms delay pattern, totaling 18.00 s; the 36-frame sheet samples every sixth frame. `build-preview.py` uses Pillow, NumPy and SciPy. The smaller `boss-fight-github.gif` is for browser viewing only. Effects use reconstructed transparency and may need production blending; the beam's end rows match but engine filtering has not been tested. No planner pass, hitbox correctness or seamless rotation is asserted.
