# Build APK/AAB từ web export (Capacitor)

Sandbox này **không** có Java/Android SDK và không truy cập được
`dl.google.com` / `services.gradle.org`, nên APK không build được tại đây.
Web export (`game/`, serve tĩnh) là deliverable chạy được ngay.
Quy trình dưới đây chạy trên máy dev có Android SDK + JDK 17.

## Một lần duy nhất

```bash
npm i -D @capacitor/core @capacitor/cli @capacitor/android
npx cap add android        # tạo android/ từ capacitor.config.json (webDir: game)
```

## Mỗi lần build

```bash
npx cap sync android       # copy game/ vào android/app/src/main/assets/public
cd android
./gradlew assembleDebug    # APK: android/app/build/outputs/apk/debug/app-debug.apk
./gradlew bundleRelease    # AAB (play store)
```

## Ghi chú

- Game là canvas 2D + ES modules thuần → WebView Android 7+ chạy 60 FPS;
  không plugin native nào cần thiết (audio placeholder silence).
- `capacitor.config.json` ở root repo đã trỏ `webDir: "game"`.
- Không dependency trả phí: Capacitor là MIT.
