# Phân tích ngược WindWings: Space Shooter (APK 1.3.118)

> Trả lời ngắn: **Được.** Đã tải bản APK chính thức mới nhất (1.3.118, build 312) từ CDN APKPure,
> lưu thành **draft release** trong repo này, rồi chạy **REA** + **Il2CppDumper** + **UnityPy**
> để bóc tách engine, code C#, UI, asset, âm thanh, cấu hình và cả localization.
> Báo cáo thô nằm trong `docs/apk-analysis/`, dữ liệu bóc được nằm trong `reverse-engineering/`.

---

## 1. APK lấy từ đâu, lưu ở đâu

| Thông tin | Giá trị |
|---|---|
| Nguồn | `d.apkpure.net` (CDN của APKPure) — APK gốc, không mod |
| Định dạng | XAPK (base APK + split ABI) |
| Tên file | `windwings.xapk` |
| Dung lượng | 142.125.649 bytes (135,5 MB) |
| SHA-256 | `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` |
| Base APK | 118.135.473 bytes, sha256 `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1` |
| Split ABI | `config.arm64_v8a.apk` — 73.682.106 bytes (chỉ arm64-v8a) |
| Package | `com.Wind.wings.Space.Shooter` |
| Version | `1.3.118` (versionCode **312**) |
| minSdk / targetSdk | 24 / **36** |

**Đã lưu trên GitHub:**

- **Draft release** `windwings-apk-1.3.118` → asset `windwings.xapk` (142 MB).
  Draft nên chỉ người có quyền push vào repo thấy; muốn công khai thì publish, muốn bỏ thì xoá.
- **Actions artifact** `windwings-xapk` (XAPK + base APK + config APK + inventory, ~295 MB).
- **Actions artifact** `windwings-analysis` (~119 MB): `dump.cs`, `DummyDll/`, `script.json`,
  `stringliteral.json`, toàn bộ texture/sprite export, báo cáo REA.

Tải artifact về máy:

```bash
gh run download <run-id> -R Nthanhbadboy/WindWings-Space-Shooter-game-play -n windwings-analysis
```

> Lưu ý: sandbox của Arena chỉ ra được `github.com` / `api.github.com` / `pypi.org`, nên mọi thứ
> nặng (tải APK, Java, .NET, REA) chạy trên GitHub Actions; kết quả được commit ngược lại repo.
> Toàn bộ quy trình nằm trong `.github/workflows/` và `tools/apk-*`.

---

## 2. Hồ sơ kỹ thuật của game

| Hạng mục | Kết quả |
|---|---|
| Engine | **Unity 2022.3.62f3** (chuỗi version nằm trong `data.unity3d` và `libunity.so`) |
| Scripting backend | **IL2CPP**, `global-metadata.dat` **8.621.240 bytes**, metadata **version 31** |
| Kiến trúc | Chỉ **arm64-v8a** (`libil2cpp.so` 47 MB, `libunity.so` 17,8 MB) |
| Unity data | `assets/bin/Data/data.unity3d` **63,9 MB**; `resources.resource` 5,1 MB |
| DEX | 6 file `classes*.dex` (chủ yếu SDK Java: ads, Firebase, Facebook, billing) |
| Mã hoá metadata | **Không** — tên class/namespace/method đọc được 100% |
| Obfuscation | Không thấy obfuscator thương mại; tên class đặt rõ ràng (`Player_Attack_1`…`_24`, `Boss1_Director`…) |
| Tổng object Unity | ~238k GameObject, ~125k MonoBehaviour, 2.185 Sprite, 654 Texture2D, 69 AudioClip |
| Signature | APK chỉ ký v2/v3 (keytool báo “Not a signed jar file” là bình thường) |

**Nhận xét:** đây là bản build IL2CPP “sạch”, không mã hoá metadata, không pack native.
Với một game 10M+ lượt tải thì đây là bề mặt reverse rất mở: chỉ cần `Il2CppDumper` là có
toàn bộ danh sách class + method + RVA, còn asset thì `UnityPy` đọc trực tiếp.

---

## 3. REA (Reverse Engineering Assistant) — dùng được đến đâu?

Đã build **REA v7.1.0** từ `github.com/mytechnotalent/rea` (Rust, build trong Actions) và chạy:

```bash
rea analyze com.Wind.wings.Space.Shooter.apk
```

Kết quả: `docs/apk-analysis/05-rea.md` (+ JSON). REA nhận diện APK là **ZIP container**,
đọc 50.331 string, entropy 7.21, kết luận “không bị pack” (score 2), liệt kê indicator,
capability (base64, zlib, .NET assembly, MZ header…) và cryptographic constants.

**Hạn chế cần nói thẳng:** REA là framework reverse đa nền tảng, phần Android của nó dừng ở
mức `AndroidManifest.xml` + `classes.dex` + native ELF; nó **không hiểu Unity IL2CPP** và
**không deserialize được asset Unity**. Vì vậy báo cáo APK của REA khá nông và có vài
“indicator” là rác từ dữ liệu nén. Để trả lời “game này có gì”, mình bổ sung:

1. **Il2CppDumper 6.7.46** → `dump.cs` 18,9 MB, 3.662 type, 15.053 string literal.
2. **UnityPy 1.25.4** → đọc `data.unity3d`, liệt kê/export texture, sprite, audio, text asset.
3. **TypeTreeGeneratorAPI** + metadata IL2CPP → đọc giá trị ScriptableObject (đang hoàn thiện).

Nếu chỉ dùng REA thì sẽ không thấy được kiến trúc game; còn Il2CppDumper + UnityPy mới là
phần “phân tích ngược các thứ của game” thực sự.

---

## 4. Kiến trúc code C# (từ `dump.cs`)

`dump.cs` có **3.662 type** (3.404 class, 113 struct, 145 interface), trong đó phần game
(không tính Unity/System/thư viện) khoảng **2.095 class**, **255 enum**.
Các namespace lõi:

| Namespace | Số type | Nội dung |
|---|---:|---|
| `SpaceShooter` | 44 | điều khiển gameplay, va chạm, drop, hiệu ứng |
| `SpaceShooter.Player` | 51 | 24 loại tàu, drone, skill, physics tàu |
| `SpaceShooter.EnemySystem` | 93 | boss, directior, spawner, attack pattern |
| `SpaceShooter.Bullet` | 33 | đạn, laser, rocket, beam, pooling |
| `SpaceShooter.SpawnSystem` | 9 | spawn theo path/waypoint/point-to-point/air-free |
| `SpaceShooter.Gameplay` | 15 | vòng đời trận, mode, camera, thời gian |
| `PVP` + `GamePVP` | ~10 | phòng PvP, item PvP, kết quả trận |
| `TuPro` | 6 | sound clip, tiện ích |

Các class “xương sống”:

- `GameMode` — static state của trận: `playMode`, `indexBoss`, `waveIndex`, `indexChallange`,
  `arenaRank`, `pvpMode`, `isPvPOnline`, `isMaster`, `pvpMapIndex`.
- `GameDatas` — toàn bộ tiền tệ + setting + cờ anti-cheat (xem mục 5).
- `BoardManager` / `BoardID` — điều hướng 49 board; `LoadBoardMode` = Single / Additive / PopUp.
- `Player_Get_Datas`, `Player_Saved_Datas`, `Player_Attack`, `Player_Attack_1..24`, `Player_Ability`,
  `Player_Ingame`, `Drone_Get_Datas`, `Drone_Saved_Datas`, `Device_Get_Data`, `Tech_Datas`, `Talent`.
- `Enemy_Data_Balance`, `Data_Boss`, `Boss1..Boss23`, `MiniBoss1/2`, `MB4..MB16`, `Boss*_Director`.
- `Stage_Get_Datas`, `Map_Get_Datas`, `Wave`, `Stage_Generator`, `Chapter` — campaign & wave.
- `ArenaManager`, `ArenaConfig`, `RankManager`, `Board_RoomPVP`, `PVP_Player`, `PlayerItemPVP`.
- `AdsCaller`, `IAP_Manager`, `IAPProduct`, `AdjustEventTracking`, `UserDataAnalysics`.
- `LanguageStringData`, `LanguageAssets` — localization **19 ngôn ngữ** (có tiếng Việt).

---

## 5. Gameplay & hệ thống (đọc từ code + enum + string)

### 5.1 Chế độ chơi — 7 mode

```csharp
enum PlayMode { Normal=0, FightBoss=1, Challange=2, Survival=3, TryPlayer=4, Arena=5, PVP=6 }
enum PVPMode { Tournament=0, Solo=1, Hunter=2 }
enum LoadBoardMode { Single=0, Additive=1, PopUp=2 }
```

- **Normal**: campaign theo chapter/stage/wave.
- **FightBoss**: chọn boss (`Board_SelectBoss`), đánh theo `indexBoss`.
- **Challange**: nhiệm vụ challenge theo `indexChallange`, có `listChallangeMissionActived`.
- **Survival / Endless**: `Map_Get_Datas.listMapEndlessDatas`, điểm theo thời gian sống.
- **TryPlayer**: chơi thử tàu trước khi mua (`Popup_TryShip`, `Board_Players`).
- **Arena**: đấu rank bất đồng bộ qua Firebase, chia mùa (`ArenaManager.SeasonTimes`).
- **PVP**: phòng realtime, 3 kiểu Tournament / Solo / Hunter (`GameMode.isMaster` = chủ phòng).

### 5.2 UI — 49 board + 63 popup + 8 tab (+5 cell/screen = 125 class)

`BoardID` có 40 giá trị (0–39), ví dụ:

```
BoardHome=1, BoardUpgrades=2, BoardPlayers=3, BoardDrones=4, BoardMaps=5,
BoardStage=6, BoardPause=7, BoardEndgame=8, BoardReborn=9, BoardDevices=10,
BoardFusion=11, BoardSettings=12, BoardShopEnergy=13, BoardCards=14,
BoardDropItems=15, BoardQuest=16, BoardShopBig=17, BoardQuestRewards=18,
BoardBattlePass=19, BoardSelectBoss=20, BoardFightBoss=21, BoardBeginPlay=22,
BoardVip=23, BoardLogIn=24, BoardChallange=25, BoardSurvival=26, BoardObstacle=27,
BoardUserProfile=28, BoardRebornIAP=29, BoardArena=30, BoardPvP=31, BoardChapters=32,
BoardCombo=33, BoardEvent1=34, BoardRanks=35, BoardWinnerBenefits=36,
BoardBattlePass2=37, BoardTradeDevices=38, BoardMiniCombo=39
```

Danh sách đầy đủ + field/method từng board/popup: [`08-ui-map.md`](08-ui-map.md).

Các màn đáng chú ý: `Board_TechLab` (2 tab Basic/Talent), `Board_Talents` (7 talent:
DropBomb, Invisible, Lasers, MegaBomb, Stun, …), `Board_Devices` (trang bị theo tàu),
`Board_Drones` (12 drone), `Board_Cards` (card tàu), `Board_Fusion`, `Board_BattlePassPro`,
`Board_EventSeasonPass`, `Board_Arena`, `Board_RoomPVP`, `Board_Reborn_IAP`.

### 5.3 Kinh tế / tiến trình

`GameDatas` giữ:

- Tiền tệ: `Coins`, `Gems`, `Energy`, `StarCount`, `WingCoins`, `TimeRewards`, `CoinEvent1`,
  `KeyCount0/1/2`, `VipPoints`, `ArenaPoints`, `CampaignPoints`, `ArenaMedal`, `PvPMedal`.
- Meta: `GraphicsLevel`, `TypeControl`, `UILeftRight`, `AutoChangePlayer`, `AutoChangePosition`,
  `IsPremiumTag`, `CanCollectPremiumGift`, `CountThroughAds`, `Compensation`, `OverDrive`.
- **Cờ debug/cheat**: `isAdmin`, `antiCheat`, `maxCheat`, `maxCheatCoins`, `maxCheatGems`,
  `cheatCoins/Gems/Stars/DroneCards/PlayerCards/DroneExp/StageUnlocked/ZoneUnlocked/TutIndex`,
  `unlock`, `fixedStagePlay`.

Các hệ nâng cấp:

| Hệ | Class | Ghi chú |
|---|---|---|
| Tàu | `Player_Get_Datas`, `Player_Saved_Datas` | 24 tàu `Player_Attack_1..24`; `MaxLevelPerRanks`, `CardUpgrades`, `StartRanks`, `LastShipUnlocked`, `IndexPlayerOffer` |
| Drone | `Drone_Get_Datas`, `Drone_Saved_Datas`, `Droid_Data_Balance` | 12 drone; `MaxLevelUpgrade`, `BaseDamages`, `DroidTimeOut`, `UnlockCosts`, `UnlockStarCosts`, `GetUpgadeCostCoins/Gems` |
| Thiết bị | `Device_Get_Data`, `Device_Saved_Data`, `DeviceInfo`, `DeviceStats` | 5 slot?; `percentByLevels1/2`, stat theo level; equip/unequip theo tàu |
| Tech Lab | `Tech_Datas`, `Tech_Basic`, `Tech_Talent`, `Tech_Stat`, `Tech_Ability_Data` | `MAX_LV_TECHLAB`, `CostUnlockStats`, `basePriceStatUpgrade`, `deltaPriceTechStats`, `CostUpgradeTechLab` |
| Talent | `Talent`, `Talent_Event`, 6 class `Talent_*` | mở theo VIP (`listVipNeeds`), chọn 1 talent |
| Card | `Cards`, `Board_Cards` | card nâng sao tàu |
| Battle Pass | `Board_BattlePass`, `Board_BattlePassPro`, `Board_EventSeasonPass`, `Tab_BattlePassMission` | mùa, điểm, mission tuần, free/paid |
| Quest/Mission | `Board_Quest`, `Board_QuestRewards`, `Popup_ChangeMissions`, `Stage_Mission` | daily + challenge mission |
| Shop | `Board_ShopCoins/Gems/Energy`, `Board_BigShop`, `Arena_Shop`, `Shop_Pack`, `Shop_Gifts`, `ShipSalePack`, `ShipTrial` | shop thường, shop arena/PvP, pack tàu, trial |
| VIP | `Board_Vip`, `Popup_PremiumDailyRewards`, `Popup_PremiumExpired` | VIP point, premium daily gift |
| Rank/Arena | `RankManager`, `ArenaManager`, `ArenaUserProfile`, `RankStruct`, `SeasonRewards` | mùa giải, rank up/drop, thưởng mùa |

### 5.4 Enemy / boss

- **20 boss chính**: `Boss1`, `Boss3`–`Boss13`, `Boss15`, `Boss17`–`Boss23` (đánh số không liên tục).
- **2 mini-boss** (`MiniBoss1/2`) và **16 biến thể MB** (`MB2`–`MB16`, `MB19`).
- Mỗi boss có `*_Director` (state machine), `*_AnimationEvents` (đồng bộ animation),
  các attack riêng: `Boss1_PlasmaAttack`, `Boss3_Flamer`, `Boss4_BigLaser`, `Boss6_Sword`,
  `Boss8_Spawner`, `BossLaser`, `Wukong_Shoot`, `Energy_Shockwave`, `EMP`, `Beam`, `Saw_Physics`…
- `Data_Boss.allBosses` là mảng `Boss_Info { int idWave; Sprite Sprite; }` — map wave → sprite boss.
- `Enemy_Data_Balance` tính thưởng/điểm: `GetBonusCoin`, `GetBonusExp`, `GetSurvivalScore`,
  `GetArenaScore`, `GetPVPPlayScore`, `GetArenaPlayScore`.
- `Map_Get_Datas` giữ map cho từng mode: `AllArenaStartMaps`, `AllArenaRandomMaps`,
  `AllPvPStartMaps`, `listMapFightBossDatas`, `listMapChallangeDatas`, `listMapEndlessDatas`,
  `listMapObstacleDatas`; `GetNumberWaves()`, `GetListWaves(mapIndex)`.

### 5.5 Ads / IAP / analytics

- **Mediation**: AppLovin MAX + adapter cho Google AdMob/Ad Manager, Meta Audience Network,
  Pangle/ByteDance, Mintegral, InMobi, Unity Ads, Vungle, Fyber, ironSource.
  SDK Java tương ứng nằm trong DEX (`com.applovin`, `com.mbridge`, `com.bytedance.sdk`,
  `com.google.android.gms.ads`, `com.inmobi`, `com.facebook.ads`…).
- **Vị trí quảng cáo**: enum `AdPos` 19 giá trị — `XCoins`, `SupplyGift`, `Reborn`, `OpenBox`,
  `QuestBonus`, `XTimeRewards`, `FreeGems`, `BonusDay`, `BattlePass`, `Inrerest`, `FreeBooster`,
  `FreeItems`, `FreeDevices`, `FreeCards`, `ShopEnergy`, `QuestVideo`, `BoardItems`,
  `BonusOpenBox`, `Penalty`.
- **AdsCaller**: interstitial theo `TimeRate`, `CountShowInterstitial`, `CallEndgameInterstitial`,
  `CallHomeInterstitial`, rewarded ad, cờ `NoAds`/`IsNeverRequest…Ad`.
- **IAP**: Unity Purchasing (`Unity.Purchasing.*`), `IAPProduct` (ScriptableObject, `EnableTestMode=false`)
  chứa **99 product non-consumable + 71 product consumable = 170 ID**, tất cả cùng prefix
  `windwings.`: 72 `playerunlock*` (mở tàu, có bản `.s1/.ss1/.x1` cho từng season),
  12 `gems*`, 11 `gifts*`, 6 `shipfull*`, 4 `select*`, 4 `combo*`, 4 `pro*`, 3 `coins*` +
  3 `coinevent*`, `battlepass`/`battlepass2`, `vippack1..6`, `unlockzone`, `techlab`, `penalty`,
  `timereward.forever`, `winner1/2`, `droneunlock8`. Danh sách đầy đủ: `13-iap-products.csv`.
  `IAP_Manager` bind các product đó vào `proForeverProduct`, `timerewardForeverProduct`, `giftLogInXProduct`.
- **Analytics**: Firebase (Analytics/RemoteConfig/Messaging/Auth/Database), AppsFlyer,
  `AdjustEventTracking`, Facebook SDK. Purchase được xác thực server-side qua
  `https://us-central1-universe-invader2-alien-war.cloudfunctions.net/validatePurchase`
  (backend dùng chung template với game Universe Invader 2 của cùng publisher).

### 5.6 Anti-cheat / bảo mật

- `GameDatas.antiCheat`, `maxCheat`, `maxCheatCoins/Gems` + đếm `cheatCoins`, `cheatGems`,
  `cheatStars`, `cheatStageUnlocked`… → cơ chế phát hiện sửa tiền/save và ban.
- `Popup_Ban`, `Popup_CheatTime`, `Popup_Penalty` — UI xử lý vi phạm.
- Manifest `<queries>` liệt kê **Magisk, SuperSU, Superuser** → kiểm tra root/emulator.
- Server time check (`RankManager.GetTimeOnline`, `GetTimeSpan`) chống đổi giờ máy.
- Một phần logic PvP/Arena dựa vào Firebase Realtime Database, không có game server riêng;
  `ArenaManager.pathRoot`, `/arena---datas/rank-configs/...`, `/profile/pvpDatas`.
- Không thấy mã hoá metadata hay pack native — nghĩa là **bảo vệ chủ yếu là anti-cheat phía client**,
  rất dễ bypass nếu chỉ chơi offline.

---

## 6. Dữ liệu & công thức (những gì đọc được)

### 6.0 Bảng dữ liệu bóc trực tiếp từ ScriptableObject

Ở lần chạy này, typetree sinh từ metadata v31 bằng backend **AssetStudio** (backend mặc định
`AssetsTools` của `TypeTreeGeneratorAPI` fail toàn bộ với metadata v31 — xem
`11-typetree-probe.md`) nên đọc được **159 instance** trong 8 class:

| Class | Instance | Ý nghĩa |
|---|---:|---|
| `Data_Players` | 25 (+13 `Data_Drones`) | roster tàu / drone (`id`, `Star`, `Actived`, `Sprite`) |
| `Data_Boss` | 46 | `Boss_Info { idWave, Sprite }` |
| `Data_Items` | 6 | item rơi (`index`, `iconSprite`, `allStatSprites[5]`) |
| `IAPProduct` | 1 | 170 product ID |
| `LanguageAssets` | 19 | 1.416 key × 19 ngôn ngữ |
| `Tech_Ability_Data` | 6 | dữ liệu tech/ability |
| `SoundClip` | 92 | map âm thanh |
| `SkeletonDataAsset` | 27 | cấu hình Spine |
| `(1 error)` | — | `Player_Attack_1` — backend không sinh được typetree cho class này |

Roster tàu (`14-ships.csv`): id `10001`–`10024` + `10999` (chưa mở — `Actived=False`),
`Star` từ 2.0 → 5.11 dùng làm hệ số sức mạnh/sao.
Drone (`14-drones.csv`): id `20001`–`20012` + `20013` (chưa mở), `Star` 1.0 → 5.02.
Boss (`14-bosses.csv`): `idWave` **7001–7022** (chapter 1) và **9001–9024** (chapter 2),
tổng 46 wave-boss; 4 wave (`7007`, `9001`, `9015`, `9016`) có `Sprite = 0` (boss đặc biệt/spawn).
Item (`14-items.csv`): 6 loại, index `1,2,3,4,5,101`; mỗi loại 1 icon + đúng 5 sprite stat.

> Muốn xem toàn bộ giá trị: `reverse-engineering/scriptableobjects/` (JSON đã dump, 19 language
> asset + 5 bảng data) và `docs/apk-analysis/14-*.csv`.

`docs/apk-analysis/06-gameplay-systems.md` chứa nguyên văn field/method của các class then chốt.
Một số điểm cụ thể:

- `Player_Get_Datas`:
  `StartHp`, `TouchRanger`, `TimeResetInvincible`, `TimeCanActiveInvincible`,
  `StartMainCannonDamages[]`, `StartMainCannonRate[]`, `StartWingCannonDamages[]`,
  `StartMagnetRange`, `PercentFreeOverDrive`, `StartSecretWeaponDamage/Duration`,
  `PlayerCosts[]`, `PlayerTimeStars[]`, `PlayerStarCosts[]`,
  `listLegendaryPlayers`, `listStarToTryLegendaryPlayers`, `listStarToBuyLegendaryPlayers`.
  Mỗi tàu có bộ `pN_idBltNormal`, `pN_idBltPowerUp`, `pN_startShotRate`, `pN_startBltSpeed`,
  `pN_superPowerUpShotRate`, `pN_superPowerUpBltSpeed`, `pN_speedMainCannonBlt`, `pN_radiusCheck`.
- `Player_Attack`: `id`, `rank`, `IsHpBelow30`, `wingCannonPercent`, `mainCannonPercent`,
  `addPowerByDevice`, `addRangeByDevice`, `addSpeedByDevice`, `addRateByDevice`,
  `addCritByDevice`, `addPowerPerKill`, `isAddPowerWhenKill`, `IsVictory`.
- `Player_Ability`: shield thường, `shieldDroidObject101/103`, `shieldOneHit`,
  skill drone 7 và 11, `targetLayer`, `layerEnemyAndBullet`, `layerBullet`, `revokeEfxIds`.
- `Droid_Data_Balance`: `MaxLevelUpgrade`, `BaseDamages[]`, `DroidTimeOut[]`, `UnlockCosts[]`,
  `UnlockStarCosts[]`, `StartRanks[]`, `GetUpgadeCostCoins`, `GetUpgradeCostGems`.
- `Tech_Datas`: `MAX_LV_TECHLAB`, `CostUnlockStats[]`, `basePriceStatUpgrade[]`,
  `deltaPriceTechStats[]`, `CostUpgradeTechLab[]`, `DeltaStarCost`, `StartStarCost`.
- `Stage_Get_Datas`: `startBonusValues[]`, `coinDelta`, `gemDelta`, `levelDelta[]`,
  `listIgroneEnemies`; hàm `GetCountEnemies`, `GetCountSpecialEnemies`, `GetCountSupplyNormal`,
  `GetCountAllEnemies`, `GetBonus`, `GetStringNameBranch`, `GetStringInfo`.
- `ArenaManager`: `MaxRoomCount`, `MinUserCount`, `SeasonSummaryTime`, `SeasonTimes[]`,
  `RankMapsIndex`, `RankUpIndexs[]`, `RankDropIndexs[]`, `rewards[]`, `MyRank`.
- `GameMode`: `indexBoss`, `waveIndex`, `indexChallange`, `indexTryPlayer`, `arenaRank`,
  `pvpMode`, `isPvPOnline`, `isMaster`, `pvpMapIndex`.

> Giá trị số cụ thể (máu boss, damage, giá nâng cấp…) không nằm trong `dump.cs` vì chúng là
> hằng số trong thân hàm IL2CPP hoặc field serialize của prefab/ScriptableObject.
> Phần đọc được bằng typetree nằm ở mục 6.0 bên dưới, `docs/apk-analysis/10-scriptableobjects.md`
> và `reverse-engineering/scriptableobjects/`.

---

## 7. Asset — game vẽ bằng gì?

Từ `data.unity3d`:

| Loại | Số lượng | Ghi chú |
|---|---:|---|
| Texture2D | 654 | atlas ETC2 (ASTC/ETC2), tên `sactx-…-UIEvent`, `UI_Stage`, `UI_Home`, `UI_FightBoss`, `VIP`, `ARENA`, `Bullets`, `Drones`, `Boss3+7`, `Boss4+8`, `Enemy_Air`, `EnemyChapter2`, `Shop_Cell`, `ThemeBee`, `Holiday`… |
| Sprite | 2.185 | UI, icon, tàu, đạn, enemy, effect; export ra PNG trong artifact |
| AudioClip | 69 | BGM Home/Boss/Game, SFX bắn/nổ/biến hình/khiên/nhặt item; tên có cả tiếng Việt |
| TextAsset | 64 | **Spine 3.8.99**: 26 skeleton + atlas (tàu, boss, Saw…), bảng ký tự font, `BillingMode.json` |
| AnimatorController | 308 | animation state machine cho UI/boss |
| AnimationClip | 791 | clip animation |
| Shader | 70 | shader game + Spine/TMP |
| Font | 1 | `NotoSansSC-Medium SDF` + fallback TMP cho CJK/Thái/Ả Rập |

**Phát hiện quan trọng:** tàu/boss dùng **Spine skeletal animation** (không phải frame sequence).
Ví dụ `skeleton.json` có 17 bone, 19 slot, 4 skin (`Skin1..3`), animation `Idle`, `Idle2`,
`Left`, `Right`, `Show`, `Hide`; `Saw.json` có 18 bone, animation `Fly`, `Fly_Idle`, `Teleport`.
Muốn clone đúng cảm giác, nên dùng Spine runtime (hoặc Godot Skeleton2D) thay vì sprite sheet.

Bản export đầy đủ (653 texture + 2.185 sprite, ~112 MB) nằm trong artifact `windwings-analysis`
(mục `/tmp/apk/unity/export`). Không commit ảnh gốc vào repo vì lý do bản quyền.

---

## 8. Localization & chuỗi UI

`LanguageStringData.Item` khai báo `Keys` + **19 ngôn ngữ**; ngoài ra `LanguageAssets` có 19
asset `Language Assets <tên ngôn ngữ>`, mỗi asset chứa 2 mảng song song `listKey`/`listValue`
(cùng 1.416 key). Ngôn ngữ gồm (có **tiếng Việt**):

```
Keys, English, Vietnamese, Russian, Spanish, French, Portuguese, Arabic,
Indonesian, Thai, Romanian, Italian, Japanese, German, Czech, Dutch,
SerboCroatian, Korean, Turkish, ChineseSimplified
```

Ngoài ra `LanguageAssets` giữ cặp `listKey`/`listValue` để tra cứu nhanh.
Bảng trích xuất: `docs/apk-analysis/12-localization.csv` (**1.416 key × 19 ngôn ngữ**),
`12-localization-vi.csv` (Key / English / Vietnamese) và `12-localization.md` (mẫu 120 dòng).
Ví dụ vài dòng:

| Key | English | Vietnamese |
|---|---|---|
| `Local` | English | Tiếng Việt |
| `txt_menu_version` | Version | Phiên bản |
| `txt_menu_taptostart` | Tap to start | Chạm để bắt đầu |

Chuỗi PlayerPrefs/asset path đáng chú ý (từ 15.053 string literal):

- `BATTLEPASS_UNLOCKED`, `BATTLEPASS_PRO_VIP_UNLOCKED`, `BATTLE_PASS_WEEK_COUNT`,
  `BATTLEPASS_MISSION_ID/TYPE/POINT/DONE/UNLOCK`
- `ARENA_SHOP_ITEM_ID`, `ARENA_SHOP_ITEM_STOCK`, `PVP_SHOP_ITEM_ID`, `PVP_SHOP_ITEM_STOCK`
- `DRONECARD_SAVE_COUNT`, `DEVICE_SAVE_COUNT`, `TECHLAB_LV`, `TECH_STATBASIC_CURRENT`
- `Datas/Drones/Data_Drones`, `Datas/Device`, `Datas/TechAbility`,
  `Datas/Maps/Map_FightBosses/Map-`, `Datas/Maps/Chapter2/Waves/Wave_`
- `Boards/Popup_Common/Popup_PremiumDailyCollect`, `Boards/.../Popup_WatchVideos`

---

## 9. Đối chiếu với bản clone trong repo này

Bản clone hiện có (các nhánh prototype/Godot) đã có 3D galaxy shooter, 8 tàu, 5 nhánh nâng cấp,
drone… So với game thật, khoảng cách lớn nhất là **chiều sâu meta**, không phải gameplay core:

| Hệ của WindWings | Bản clone đã có? | Việc cần làm nếu muốn giống |
|---|---|---|
| 7 mode (Normal, FightBoss, Challenge, Survival, TryPlayer, Arena, PvP) | một phần | thêm state machine `PlayMode`, màn chọn mode, map riêng từng mode |
| 49 board + 63 popup | chưa | dựng screen graph theo `BoardID`, popup dùng chung `Popup`/`Popup_Notices` |
| 24 tàu, mỗi tàu bộ đạn/rate/speed riêng | 8 tàu | tách `Player_Attack_N` thành data-driven (ScriptableObject) thay vì class cứng |
| 12 drone + skill drone 7/11 | có drone cơ bản | thêm `Drone_Get_Datas`, timeout, unlock cost, skill riêng |
| Device 5 stat (power/range/speed/rate/crit) + crit | chưa | thêm `DeviceStats`, equip theo tàu, percent theo level |
| Tech Lab 2 tab + talent 7 loại | chưa | thêm `Tech_Datas`, `Talent`, mở theo VIP |
| Card nâng sao, fusion | chưa | thêm `Board_Cards`, `Board_Fusion` |
| Battle Pass + Pro + Event Season Pass | chưa | thêm mùa, điểm tuần, mission, free/paid track |
| Shop 4 loại + pack tàu + trial + lucky star | chưa | thêm `Shop_Pack`, `ShipSalePack`, `ShipTrial`, `Popup_LuckyStar` |
| Arena rank + PvP phòng (Firebase) | chưa | thêm `ArenaManager`, mùa giải, rank up/drop, room PvP |
| Localization 21 ngôn ngữ | chưa | dùng `LanguageStringData`/`LanguageAssets`, CSV đã bóc |
| Spine animation cho tàu/boss | chưa | dùng Spine runtime/Godot Skeleton2D, atlas đã có trong artifact |
| Ads 19 vị trí + mediation | không cần cho prototype | chỉ cần interface `AdsCaller` giả lập |
| Anti-cheat client + Firebase | không cần | giữ save local, thêm kiểm tra đơn giản |

**Ưu tiên nếu mục tiêu là “giống WindWings”**: (1) screen graph + popup chung, (2) data-driven
tàu/đạn, (3) drone/device/tech/talent, (4) battle pass + shop + rank, (5) Spine.

---

## 10. Cách đọc kết quả

| File | Nội dung |
|---|---|
| `01-apk-inventory.md` / `.json` | cây file APK, dung lượng, manifest, quyền, SDK, chứng chỉ |
| `02-unity-engine.md` | Unity version, danh sách assembly (`Assembly-CSharp`, `spine-unity`, `Firebase`, `AppsFlyer`, `Unity.Purchasing`…) |
| `03-il2cpp.md` | thống kê `dump.cs`, namespace, URL/IP/email, string anti-cheat |
| `03-il2cpp-strings.json` | URL, IP, email, JSON literal, chuỗi đáng ngờ |
| `04-unity-assets.md` | loại object, TextAsset, texture, audio, MonoBehaviour |
| `04-asset-manifest.csv` | 2.839 file asset đã export (tên, loại, kích thước) |
| `05-rea.md` / `.json` | báo cáo REA trên APK |
| `06-gameplay-systems.md` | field/method của player, enemy, boss, economy, PvP… |
| `07-enums.md` | 255 enum game (PlayMode, BoardID, AdPos, PurchaseType…) |
| `08-ui-map.md` | 49 board + 63 popup + 8 tab (125 class UI) + toàn bộ field/method |
| `09-numbers-and-formulas.md` | class config + hằng số |
| `10-scriptableobjects.md` | kết quả đọc ScriptableObject bằng typetree (159 instance) |
| `11-typetree-probe.md` | so sánh 3 backend typetree (AssetsTools / AssetStudio / AssetRipper) |
| `12-localization.md` / `.csv` / `-vi.csv` | 1.416 key × 19 ngôn ngữ |
| `13-iap-products.md` / `.csv` | 170 product ID IAP |
| `14-data-tables.md` + `14-ships/drones/bosses/items.csv` | roster tàu, drone, boss, item |
| `15-audio.md` | 69 AudioClip (tên, kênh, sample rate) |
| `reverse-engineering/il2cpp/dump.cs.gz` | toàn bộ 18,9 MB dump C# (nén còn 2,7 MB) |
| `reverse-engineering/il2cpp/class-index.json` | index 3.662 type |
| `reverse-engineering/il2cpp/interesting-classes.cs` | 150 class game kèm keyword |
| `reverse-engineering/il2cpp/stringliteral.json` | 15.053 string literal |
| `reverse-engineering/textassets/` | 64 TextAsset (Spine skeleton/atlas, charset, billing) |
| `reverse-engineering/scriptableobjects/` | JSON các ScriptableObject bóc được (nếu có) |

---

## 11. Lưu ý pháp lý

- APK và asset thuộc bản quyền **GCenter / GCENTER VIET NAM TECHNOLOGY JOINT STOCK COMPANY**.
- Mục đích ở đây là **nghiên cứu/ interoperability** cho dự án clone của chính bạn, không phải
  phát hành lại game.
- APK đang để ở **draft release** (không public). Đừng publish release này nếu không muốn
  phân phối lại APK; nếu cần chia sẻ nội bộ thì dùng artifact/private.
- Asset export (texture/sprite/audio) chỉ nên dùng làm tham chiếu thiết kế; đừng đóng gói vào
  bản phát hành thương mại.

---

## 12. Tái lập

```bash
# 1) tải + inventory + draft release
gh workflow run ingest-apk.yml -R Nthanhbadboy/WindWings-Space-Shooter-game-play
# 2) dump IL2CPP + asset + REA
gh workflow run analyze-apk.yml -R Nthanhbadboy/WindWings-Space-Shooter-game-play
# 3) xem kết quả
git pull
less docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md
```
