# Art slots — ANIM-A

`ANIM_VARIANT variant=A mode=layered art=res://art/A source=package package_commit=7aa3d08`

`ART_PACKAGE res://art/A/manifest.json package= status=EXPERIMENTAL_FOR_THREE_BUILD_COMPARISON license=UNKNOWN`

`ART_CONTRACT slots=32 art_root=res://art/A`

**Present 7 / 32 slots; 25 fall back to vector art.**

| Slot | Art | Detail |
|---|---|---|
| `PLAYER-10001` | present | res://art/A/ships/PLAYER-10001.png |
| `PLAYER-10001-GLOW` | present | res://art/A/layers/ships/PLAYER-10001-canopy-glow.png |
| `PLAYER-10001-NOZZLE` | present | res://art/A/layers/ships/PLAYER-10001-nozzle-glow.png |
| `PLAYER-10003` | **fallback** | vector fallback |
| `PLAYER-10003-GLOW` | **fallback** | vector fallback |
| `PLAYER-10003-NOZZLE` | **fallback** | vector fallback |
| `PLAYER-10004` | **fallback** | vector fallback |
| `PLAYER-10004-GLOW` | **fallback** | vector fallback |
| `PLAYER-10004-NOZZLE` | **fallback** | vector fallback |
| `CD-31002` | **fallback** | vector fallback |
| `GD-33004` | **fallback** | vector fallback |
| `CB-30009` | **fallback** | vector fallback |
| `H-38001` | **fallback** | vector fallback |
| `CD-31005` | **fallback** | vector fallback |
| `GD-33002` | **fallback** | vector fallback |
| `CB-30024` | **fallback** | vector fallback |
| `XB-34001` | **fallback** | vector fallback |
| `CB-30023` | **fallback** | vector fallback |
| `CB-30001` | **fallback** | vector fallback |
| `CD-31004` | **fallback** | vector fallback |
| `CB-30002` | **fallback** | vector fallback |
| `CB-30003` | **fallback** | vector fallback |
| `Boss-37001` | present | res://art/A/bosses/Boss-37001.png |
| `Boss-37001-TURRET-L` | present | res://art/A/layers/bosses/Boss-37001-turret-left.png |
| `Boss-37001-TURRET-R` | present | res://art/A/layers/bosses/Boss-37001-turret-right.png |
| `Boss-37001-CORE` | present | res://art/A/layers/bosses/Boss-37001-core-glow.png |
| `BG-FIELD` | **fallback** | vector fallback |
| `BULLET-PLAYER` | **fallback** | vector fallback |
| `BULLET-ENEMY` | **fallback** | vector fallback |
| `FX-HIT` | **fallback** | vector fallback |
| `FX-EXPLOSION` | **fallback** | vector fallback |
| `UI-MENU-FRAME` | **fallback** | vector fallback |

Enemy, bullet, FX, background and menu slots have no art in the delivered
packages; they are listed as fallback on purpose rather than hidden.
