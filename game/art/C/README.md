# Variant C - single flat image per sprite (whole-image animation)

Delivered package: `art/animation-options/C-flat` from commit `7aa3d08`
(branch `arena/215aa58f`), copied here byte for byte - pixels untouched.

```
ships/PLAYER-10001.png
```
```
bosses/Boss-37001.png
```

`ANIMATION_NOTES.md` (the artist's caveats) and `manifest.json` (per-file
SHA-256 plus `pivot_pixels_inferred`) ship unchanged next to the images. CI
re-hashes every file against that manifest before building, and the loader uses
the manifest pivots for the rotating parts, so a package never has to match a
mount hardcoded in the engine.

Not every slot has art: enemies, bullets, FX, the background and the menu frame
still draw the vector fallback (reported slot by slot in `BUILD_INFO.txt`).
Do not edit these PNGs here - fixes go back to the art branch and arrive as a
new package commit.
