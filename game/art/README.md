# Art drop-in folder

## Animation build variants (A / B / C)

The Windows build takes one parameter, `--variant A|B|C`, which picks both the
art folder and the animation mode (`game/tools/build_variant.py` writes
`game/data/animation_variant.json`; the exported .exe reads that file and the
main menu prints the label `ANIM-A` / `ANIM-B` / `ANIM-C`).

| Variant | Art package | Folder | Animation |
| --- | --- | --- | --- |
| A | generated clean layers | `game/art/A/` | layered: ship body + `-GLOW`, boss `-BODY/-GUN-L/-GUN-R/-CORE`, guns track the ship |
| B | inpainted flat image split into layers | `game/art/B/` | layered, identical rules to A |
| C | one flat image per sprite | `game/art/C/` | whole image: bob, bank, flash, shake, particles over the hull, guns fixed, flame on the hull |

Each package uses the same slot names and the same relative paths below; only the
root folder differs. The three folders now contain the DELIVERED packages from
`arena/215aa58f` @ `7aa3d08` (`art/animation-options/{A-clean,B-inpaint,C-flat}`),
copied byte for byte, together with their `ANIMATION_NOTES.md` and `manifest.json`
(package commits and hashes are recorded there; CI re-checks every hash). Lookup order is `res://art/<variant>/` → `user://art/<variant>/`
→ `res://art/` → `user://art/`, so a missing layer in a package falls back
instead of crashing, and a shared file can sit in the variant-independent root.

Slot files as delivered:

```
ships/PLAYER-10001.png
layers/ships/PLAYER-10001-canopy-glow.png     (A, B)
layers/ships/PLAYER-10001-nozzle-glow.png     (A only)
bosses/Boss-37001.png
layers/bosses/Boss-37001-turret-left.png      (A, B)
layers/bosses/Boss-37001-turret-right.png     (A, B)
layers/bosses/Boss-37001-core-glow.png        (A, B)
```

A package may ship `manifest.json`; its `pivot_pixels_inferred` block owns the
mount of each rotating part (boss turrets, ship canopy/nozzle). The loader turns
those pixels into canvas fractions, so a package is never forced to match a
pivot hardcoded in the engine. Pivot actually used is printed as
`ART_PIVOT <slot> manifest <x> <y>` in `BUILD_INFO.txt`.

Variant C ignores the optional layer slots (`PLAYER-*-GLOW`, `Boss-37001-BODY`,
`-GUN-L`, `-GUN-R`, `-CORE`) by design: it animates the single
`Boss-37001.png` / `PLAYER-*.png` image as one piece.

## Slot layout

Put contract-compliant PNGs here. The folder layout is fixed by
`game/data/art_slot_contract.json` (regenerate with
`python3 game/tools/build_art_slot_contract.py`):

```
game/art/
  ships/        PLAYER-10001.png  256×256   faces UP
  enemies/      CB-30001.png      128×128   faces DOWN
  bosses/       Boss-37001.png    512×512   faces DOWN
  background/   BG-FIELD.png      1024×1024
  projectiles/  BULLET-PLAYER.png 64×128 faces up
                BULLET-ENEMY.png  64×64  faces down
  fx/           FX-HIT.png        256×256
                FX-EXPLOSION.png  256×256
  ui/           UI-MENU-FRAME.png 1080×1920
```

Rules:

- PNG, RGBA8, transparent background, the subject centred (pivot 0.5/0.5).
- The game scales each slot by height, so keep the subject inside a centre-safe
  area and leave a few transparent pixels at the edges.
- Any missing file is fine: the game draws the vector fallback and logs the slot.
- Draw new art. Do not extract or copy sprites from the original game.
- `user://art/` is read after `res://art/`, which lets you test a PNG without
  rebuilding the executable.

Check what is currently shipped:

```bash
godot --headless --path game --script res://tools/art_report.gd
```
