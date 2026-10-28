# Art drop-in folder

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
