# Build Packaging Icons Supplement (`ICO-06` & `ICO-07`) — Variant B (`Solar Neon Arcade-Pop`)

- **Role / Branch:** `Art-designer-B` · `arena/eca8588b-windwings-space-shooter-game-p`
- **Why a separate folder (`art/w0-build-icons-b/`):** Per user standing instruction, `art/w0-listing-b/` preserves the **exact 25 store-listing files** matching `art/w0-listing/W0_MANIFEST.md` untouched. The 2 non-store packaging icon outputs added in controller `docs/art-plan/w0-listing-slots.csv` (`ICO-06` & `ICO-07`) are exported here from `art/w0-listing-b/masters/icon_master.png` for Godot Windows/MSIX (`ba257b36`) and Android APK/AAB (`ef6b75ef`) builds.
- **License:** `chờ user xác nhận quyền tên/art (Phase C USER-ONLY #3)`
- **Author:** `arena/eca8588b-windwings-space-shooter-game-p`

| Slot ID | File | Dimensions / Layers | Source Master | Recipe |
|---|---|---|---|---|
| `MASTER` | `masters/icon_master_1024.png` | `1024×1024` RGBA PNG | `art/w0-listing-b/masters/icon_master.png` | Lanczos 1024px normalized master |
| `ICO-06` | `windwings.ico` | Multi-res Windows `.ico`: `16×16`, `24×24`, `32×32`, `48×48`, `256×256` | `masters/icon_master_1024.png` | Pillow multi-frame ICO |
| `ICO-07` | `mipmap-mdpi/ic_launcher.png` | `48×48` RGBA PNG | `masters/icon_master_1024.png` | Lanczos Android `mdpi` |
| `ICO-07` | `mipmap-hdpi/ic_launcher.png` | `72×72` RGBA PNG | `masters/icon_master_1024.png` | Lanczos Android `hdpi` |
| `ICO-07` | `mipmap-xhdpi/ic_launcher.png` | `96×96` RGBA PNG | `masters/icon_master_1024.png` | Lanczos Android `xhdpi` |
| `ICO-07` | `mipmap-xxhdpi/ic_launcher.png` | `144×144` RGBA PNG | `masters/icon_master_1024.png` | Lanczos Android `xxhdpi` |
| `ICO-07` | `mipmap-xxxhdpi/ic_launcher.png` | `192×192` RGBA PNG | `masters/icon_master_1024.png` | Lanczos Android `xxxhdpi` |
