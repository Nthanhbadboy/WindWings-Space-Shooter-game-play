# Motion evidence — ANIM-A launch slice

Frames rendered from the real scenes by `game/tools/motion_capture.gd` on the CI
runner (xvfb + llvmpipe, `--fixed-fps 60`, captured at the frame rate below).
Each GIF is the acceptance clip; the `-sheet.png` file is the same frames laid out
in order, so the motion can be read without playing the GIF.

- Variant: ANIM-A - layered animation (ship body + glow layer, boss body/gun-l/gun-r/core, guns track the ship)
- Art source: placeholder (no art package delivered yet, so these frames show the fallback art)
- Capture rate: 12 fps
- Frame width: 288px

| Segment | Frames | Simulated seconds | GIF | Frame sheet |
|---|---:|---:|---|---|
| boss | 92 | 7.58 | `boss.gif` | `boss-sheet.png` |
| flight | 32 | 2.58 | `flight.gif` | `flight-sheet.png` |
| hangar | 37 | 3.00 | `hangar.gif` | `hangar-sheet.png` |

Scenes: `hangar` = ship idle animation (float, breathing shadow, glow pulse,
idle flame), `flight` = ship gliding and firing (banking, engine plume), `boss`
= boss descent, warning bar, aiming guns, core telegraph and the Attack2 volley
with the player taking hits.
