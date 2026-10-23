# WindWings-Space-Shooter-game-play

Reverse-engineering và đặc tả thiết kế cho *WindWings: Space Shooter* (Unity 2022.3.62f3, IL2CPP).
Repo **chỉ chứa tài liệu và công cụ** — không phát hành lại game, APK hay asset gốc.

- `docs/spec/` — đặc tả gameplay, UI, balance, animation… (mục lục: `docs/spec/README.md`)
- `runtime-probe/` — bridge C# nhúng trong APK: đọc scene / GameObject / static field / log khi game đang chạy
- `.github/workflows/ramus-probe.yml` — CI bật emulator cloud bằng Ramus, cài APK, chụp màn hình và gọi bridge
