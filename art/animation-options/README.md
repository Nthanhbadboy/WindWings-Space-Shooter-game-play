# Three animation options — build-comparison prototypes

Three directories each contain their own `game/art/` slot tree, optional `game/art/layers/`, `manifest.json`, `ANIMATION_NOTES.md`, images on gameplay and 64px previews, and raw planner metrics. They share byte-identical copies of the original player and boss masters. A is a regenerated style-reference variant, B uses masked generative inpainting and original pixels outside mapped masks, C copies existing flat exports byte-for-byte.

**Not a Godot build.** The existing coder contract discovers the two base slot paths; it does not automatically load the new layer paths, animate turrets or switch option trees. Coder must explicitly wire those layers and build each option separately. Pivot estimates and layer registration are unverified in-engine.

A is not literally a clean, identical reconstruction: regenerated player is visually flatter than the approved source and A hulls retain some highlights / amber lights baked into the base; extracted layers cannot remove those. B has visible reconstructed regions, estimated pivots and no proof of seamless motion. C is one flattened original with fixed glow/flame. See each option's notes and metrics; all 6 asset measurements return exit 1. User reviews pictures; no self-claim of L3. License UNKNOWN.
