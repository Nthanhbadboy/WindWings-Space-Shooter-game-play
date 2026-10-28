# Variant C — single flat image per sprite (whole-image animation).

Drop the package PNGs here, using exactly the relative paths from
`game/data/art_slot_contract.json` (same names as the shared `game/art/` folder):

```
ships/PLAYER-10001.png  ships/PLAYER-10001-GLOW.png  ...
bosses/Boss-37001.png   bosses/Boss-37001-BODY.png   ...
```

Nothing is required: every slot is optional. A missing slot is logged as
`ART_SLOT <slot> fallback vector` in `BUILD_INFO.txt` and the build keeps the
vector drawing.

This folder currently holds no art, so every build of this variant ships the
placeholder vector art and says so in `BUILD_INFO.txt`
(`ART_VARIANT_PLACEHOLDER`).
