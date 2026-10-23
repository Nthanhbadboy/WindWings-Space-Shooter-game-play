# RUN 2026-10-23 — SỐ LIỆU RUNTIME TỪ ĐIỆN THOẠI THẬT (Mate 20 X, Android 10)

> ⚠️ Route điện thoại + NextBep launcher tự vá (commits `a64d04c`, `b4aa59a` — fork
> `Nthanhbadboy/BepInEx.Android.Launcher`). Target: `com.Gcenter.WindWings.SpaceShooter.Premium`
> (mod 1.0.69 đóng gói lại, Unity **2022.3.62f3**, IL2CPP).
> Tất cả JSON thô trong thư mục này đều là số liệu đọc từ game đang chạy thật, KHÔNG có số nào bịa.

## Kết quả cuối

| Thành phần | Trạng thái |
|---|---|
| BepInEx 6 chainloader trên phone | ✅ `Chainloader startup complete` |
| Plugin RamusBridge (bepinex6-phone, net10.0 + interop refs từ device) | ✅ `listening on http://127.0.0.1:8080` |
| HTTP probe endpoints | ✅ 8/9 hoạt động (`/screenshot` bị icall-strip — dùng `adb screencap` thay) |
| Freeze time (`POST /timescale?v=0.000001`) | ✅ `timeScale:0`, restore `v=1` OK |
| Số liệu balance game (ships 24 / drones 12 / tech / stage) | ✅ thu được qua `/statics` |

## Vì sao chạy được trên phone (kỹ thuật)

1. **Interop assemblies sinh ngay trên device** (bước "Generating IL2CPP Interop files" của
   chainloader NextBep) — 113 dll tại `BepInEx/interop/`. Pull về làm reference:
   `.ci/refs/bep6-refs-phone/` (core 39 + interop 113), upload dạng release asset
   `phone-refs` (~9.5 MB zip) để CI fetch (`fetch-loader-refs.sh`).
2. Runtime trên phone là **.NET 10** (`System.Runtime 10.0`) → target build `net10.0`.
3. `BridgeHost : MonoBehaviour` phải đăng ký qua
   `Il2CppInterop.Runtime.Injection.ClassInjector.RegisterTypeInIl2Cpp<T>()` (reflection-safe
   vì overload đổi theo fork) — nếu không sẽ `TypeLoadException: UnityEngine.MonoBehaviour`.
4. `Application.logMessageReceivedThreaded` không expose trên interop → sub qua reflection
   (`Delegate.CreateDelegate`); trên device này không có event nào được expose
   ("no Application event exposed") — capture log BepInEx bị tắt, dùng logcat mirror thay.
5. `Scene.path`, `ScreenCapture`, một số property (`Screen.dpi`, `Application.targetFrameRate`,
   `Application.platform` trong một số profiling bundle) là icall bị strip → mọi property
   Unity trong probe được bọc `Safe()` fallback.
6. `/statics` đọc qua **static properties của interop proxy** (deferred native call), KHÔNG qua
   `FieldInfo.GetValue` (đó chỉ trả `NativeFieldInfoPtr_… : IntPtr`). Mảng `Il2CppStructArray`
   được đọc qua `Length` + indexer reflection (cap 128 phần tử, prefix `_count`).

## Replay quy trình (từ đầu, phone)

```bash
# 1._Cấp quyền launcher (SAU MỖI adb install):
adb shell pm grant com.bepinex.android WRITE_EXTERNAL_STORAGE
adb shell pm grant com.bepinex.android READ_EXTERNAL_STORAGE
adb shell appops set com.bepinex.android SYSTEM_ALERT_WINDOW allow
# 2. Đặt plugin vào modpack (launcher ở vanilla mode sẽ xoá plugins/ thường):
#   /storage/emulated/0/BepInEx_Android/com.Gcenter.WindWings.SpaceShooter.Premium/
#     modpacks/Ramus/{modpack.json, plugins/RamusBridge.dll}
#   modpack.json: {"name":"Ramus","packageName":"com.Gcenter.WindWings.SpaceShooter.Premium",
#                  "createdAt":…,"modCount":1,"createShortcut":false}
# 3. Launcher UI: tab Modpacks → tick radio "Ramus" (Active) → tab Games → expand card → Launch
#    Tọa độ (viewport 720×1600): close-dialog (266,901) · tab Modpacks (360,1310) ·
#    rescan (665,128) · radio Ramus (605,578) · tab Games (120,1310) · card (360,365) · Launch (360,923)
# 4. Khi log có "[RamusBridge] listening on http://127.0.0.1:8080":
adb forward tcp:9099 tcp:8080
curl http://127.0.0.1:9099/health
```

## Endpoints đã xác nhận trên device

- `GET /health`, `GET /state` — PID, FPS, scene, device (`HUAWEI EVR-AL00`, Android 10,
  720×1429 @320dpi, 8 core, 5.6 GB, `.NET` runtime của BepInEx).
- `GET /scene`, `GET /hierarchy`, `GET /find?name=` — quét GameObject (scene `Game`:
  tháp boss, spaceship pool, `Menu_Manager`, `------------MANAGERS----------------`…).
- `GET /metrics` — avg/max frame ms.
- `GET /types?filter=` — liệt kê class (26013 type trông 175 asm).
- `GET /statics?type=<Class>` — **đọc static thật** (property interop + mảng).
- `POST /timescale?v=X` — freeze/slow-mo/test (đã test v=0.000001 → 0, restore v=1 → 1).
- `GET /logs` — hiện rỗng do capture event không có (xem mục 4); logcat `RAMUSB|{json}`
  và `RAMUSB-MARK|` vẫn hoạt động (`POST /mark?name=…`).
- `GET /screenshot` — ❌ `ICall …CaptureScreenshotAsTexture was not resolved` → dùng adb screencap.

## Số liệu runtime thu được (file JSON cùng thư mục)

### 24 SHIP (Player_Get_Datas + Player_Saved_Datas)
- `PlayerCosts` (coin mua): `[0,0,1050,3150,-1,3850,4550,2450,2450,-1,3850,-1,3150,4550,4550,-1,4550,2450,-1,4550,-1,4550,-1,-1]` — `-1` = không mua bằng coin (unlock khác).
- `StartMainCannonDamages`: `[4500,220,2680,8000,710,1650,255,800,500,95,336,3000,2350,400,515,3000,2689,1800,100,2250,100,2800,110,3300]`
- `StartMainCannonRate`: `[4.8,6.8,4.8,5.8,…,10.5]`
- `StartWingCannonDamages`: `[218,75,186,…,820]`
- `StartRanks` (rank khởi đầu): 24× `2` (rank "B")
- `listLegendaryPlayers` (ship legendary): `[10016,10019,10021,10024]`
- `PlayerStarCosts`, `PlayerTimeStars`: 24× `0` (chưa gate star)
- `LastShipUnlocked` mặc định save: `10003`
- Const chung: `StartHp=2500`, `StartMainCannonDamages[0]=4500`, `StartMagnetRange=3`,
  `PercentFreeOverDrive=0.1`, `StartSecretWeaponDamage=688`, `StartSecretWeaponDuration=5`,
  `stepCommon=0.18`, `TouchRanger=15`, `TimeResetInvincible=3`, `TimeCanActiveInvincible=10`.
- Rank scale `C,B,A,S,SS,X,XS` + `MaxLevelPerRanks=[10,20,30,60,120,250,500]` +
  `CardUpgrades=[0,20,50,80,250,500,800]`.

### 12 DRONE (Drone_Get_Datas)
- `UnlockNowCosts`: `[200,500,1500,2500,3500,3500,4000,5500,5500,4500,2500,5500]`
- `BaseDamages`: `[450,600,6000,135,935,315,650,1200,248,650,1200,2650]`
- `StartDroneSkillDamages`: `[556,10000,5600,710,1999,2650,933,5500,1085,7200,1868,1199]`
- `allAbiDroneCooldown`: `[90,90,90,90,110,100,110,100,90,90,90,90]`
- `dN_*` bullet config cho từng drone (turnRate/shotRate/shotSpeed/idBlt/turnNumber).

### STAGE / ZONE (Stage_Datas)
- `MAX_STAGE_INDEX=249`, `MAX_ZONE_INDEX=24`, `MaxModeIndex=4`,
  `CostOverDrive=50`, `XMissionUnlock=180`, `zoneUnlock=0`. (Ý nghĩa chính xác các index
  cần đối chiếu thêm với logic game; chỉ ghi số thô.)

### TECH LAB (Tech_Datas)
- `MAX_LV_TECHLAB=34`, `maxUpgradePlayer=250000`, `maxUpgradeTech=250000`,
  `DeltaStarCost=50`, `StartStarCost=30`, `CostUpgradeTechLab=(array)`.

### GOLD/CURRENCY runtime
- Không tìm thấy class "wallet". Balance coin là **instance** data (`GP_Datas.instance` tĩnh
  trỏ tới singleton — cần đọc instance-field, nằm ngoài scope /statics hiện tại).
- HP viewer trong game = 2500 khớp `StartHp`; coin HUD = 0 lúc bắt đầu Stage 1.
- `GP_Datas` statics khi đang Stage 1: `survivalScores=1101`, `countOverdrive=2`,
  `pvpLife=3`, `killCount=0→…` (xem `statics_SpaceShooter_Gameplay_GP_Datas.json`).
- Enemy drop coin là class `Enemy_DropGold` / `BurstGold` (visual).

## Giới hạn đã ghi nhận
- `/screenshot` icall-strip (dùng adb).
- `Application.*logMessageReceived*` không expose ⇒ `/logs` rỗng.
- `QualitySettings`/`vSync`/`targetFrameRate` trả fallback -1 (icall không resolve).
- Runtime trên phone là **.NET 10** → CI phải cài SDK 10 (`setup-dotnet` 8.0.x + 10.0.x).
- Đọc **instance** fields (ví dụ `GP_Datas.instance.player`, số dư coin) cần cơ chế follow
  object-graph — chưa có trong bridge bản này (để run kế tiếp).
