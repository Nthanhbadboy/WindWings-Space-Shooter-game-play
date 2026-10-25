# IL2CPP analysis

## global-metadata.dat

- size: 8621240 bytes
- sanity: `0xfab11baf`
- metadata version: **31**

## dump.cs

- size: 18860775 bytes
- classes/structs/enums/interfaces: **3662**
- kinds: class=3404, struct=113, interface=145

### Namespaces (top 60)

| namespace | types |
|---|---:|
| `(global)` | 1290 |
| `UnityEngine.UIElements` | 251 |
| `System.Xml.Schema` | 184 |
| `UnityEngine.Purchasing` | 122 |
| `System.Linq.Expressions.Interpreter` | 96 |
| `Facebook.Unity` | 96 |
| `SpaceShooter.EnemySystem` | 93 |
| `System.Xml` | 86 |
| `System.Linq.Expressions` | 81 |
| `System` | 63 |
| `System.Security.Cryptography` | 63 |
| `UnityEngine` | 61 |
| `System.ComponentModel` | 53 |
| `SpaceShooter.Player` | 51 |
| `System.Data` | 45 |
| `SpaceShooter` | 44 |
| `System.Net` | 35 |
| `System.Data.Common` | 35 |
| `Spine` | 34 |
| `SpaceShooter.Bullet` | 33 |
| `System.Xml.Serialization` | 31 |
| `UnityEngine.EventSystems` | 27 |
| `System.Threading` | 25 |
| `UnityEngine.UIElements.UIR` | 25 |
| `Unity.Properties` | 21 |
| `System.Threading.Tasks` | 18 |
| `Spine.Unity` | 18 |
| `System.Security.Cryptography.X509Certificates` | 17 |
| `UnityEngine.Purchasing.UseCases` | 16 |
| `SpaceShooter.Gameplay` | 15 |
| `Unity.Services.Core.Internal` | 15 |
| `System.Reflection` | 14 |
| `System.Dynamic` | 14 |
| `UnityEngine.Purchasing.PaymentProviderService` | 14 |
| `UnityEngine.UI` | 13 |
| `UnityEngine.Purchasing.LiveContentAdapterService` | 13 |
| `UnityEngine.Purchasing.WebshopService` | 13 |
| `Mono.Security.Cryptography` | 12 |
| `Newtonsoft.Json.Serialization` | 12 |
| `Unity.Properties.Internal` | 12 |
| `System.Xml.Linq` | 12 |
| `Mono.Net.Security` | 11 |
| `UnityEngine.Events` | 11 |
| `UnityEngine.UIElements.Internal` | 10 |
| `UnityEngine.Purchasing.Stores` | 10 |
| `Firebase` | 10 |
| `SpaceShooter.SpawnSystem` | 9 |
| `Firebase.Database` | 9 |
| `AppsFlyerSDK` | 9 |
| `Firebase.Auth` | 9 |
| `System.Text` | 8 |
| `System.Runtime.CompilerServices` | 8 |
| `MS.Internal.Xml.XPath` | 8 |
| `UnityEngine.Purchasing.Extension` | 8 |
| `System.Runtime.Serialization` | 7 |
| `System.IO` | 7 |
| `UnityEngine.Rendering` | 7 |
| `UnityEngine.Purchasing.Stores.Data.Insights.Models` | 7 |
| `Facebook.Unity.Canvas` | 7 |
| `TuPro` | 6 |

### Keyword matches: 1859 types

| keywords | type | base | methods | fields |
|---|---|---|---:|---:|
| Store, Load, Data, Ad , Mode | `UnityEngine.Purchasing.Stores.Data.Insights.Models.AppStorePayload` | `IStorePayload // TypeDefIndex: 8461` | 11 | 10 |
| Store, Load, Data, Ad , Mode | `UnityEngine.Purchasing.Stores.Data.Insights.Models.GooglePlayPayload` | `IStorePayload // TypeDefIndex: 8462` | 5 | 4 |
| Store, Data, Mode, Purchase, Event | `UnityEngine.Purchasing.Stores.Data.Insights.Models.PurchaseFailedEvent` | `IEventVariant // TypeDefIndex: 8448` | 5 | 4 |
| Store, Data, Mode, Purchase, Event | `UnityEngine.Purchasing.Stores.Data.Insights.Models.PurchaseFulfilledEvent` | `IEventVariant // TypeDefIndex: 8449` | 3 | 2 |
| Store, Data, Mode, Purchase, Event | `UnityEngine.Purchasing.Stores.Data.Insights.Models.PurchaseIntentStartEvent` | `IEventVariant // TypeDefIndex: 8446` | 1 | 0 |
| Store, Data, Mode, Purchase, Event | `UnityEngine.Purchasing.Stores.Data.Insights.Models.PurchasePaidEvent` | `IEventVariant // TypeDefIndex: 8447` | 3 | 2 |
| Level, Battle, Popup, Pass | `.Popup_BattlePassLevelUp` | `Popup_Notices // TypeDefIndex: 491` | 3 | 2 |
| Upgrade, Tech, IAP, Popup | `.Popup_UpgradeTechIAP` | `Popup // TypeDefIndex: 1179` | 8 | 10 |
| Store, Data, Purchase, Event | `UnityEngine.Purchasing.Stores.Data.Insights.PurchaseEventEmitter` | `IPurchaseEventEmitter // TypeDefIndex: 8434` | 21 | 3 |
| Store, Data, Mode, Event | `UnityEngine.Purchasing.Stores.Data.Insights.Models.PaymentOptionsShownEvent` | `IEventVariant // TypeDefIndex: 8451` | 2 | 4 |
| Tech, Analytics, Stat | `.AnalyticsSessionInfo.SessionStateChanged` | `MulticastDelegate // TypeDefIndex: 10800` | 2 | 0 |
| Load, Ads, Stat | `.AndroidAssetPacks.AssetPackManagerDownloadStatusCallback` | `AndroidJavaProxy // TypeDefIndex: 9803` | 2 | 2 |
| Config, Setting, Audio | `.AudioSettings.AudioConfigurationChangeHandler` | `MulticastDelegate // TypeDefIndex: 10775` | 2 | 0 |
| Event, Season, Pass | `.Board_EventSeasonPass` | `Board // TypeDefIndex: 692` | 47 | 61 |
| Boss, Event, Spin | `.BossSpineEventHandler` | `MonoBehaviour // TypeDefIndex: 114` | 3 | 5 |
| UI, Popup, Equip | `.Device_Popup_Equip` | `MonoBehaviour // TypeDefIndex: 586` | 4 | 4 |
| Save, Data, Drone | `.Drone_Saved_Datas` | `MonoBehaviour // TypeDefIndex: 292` | 14 | 0 |
| Item, Drop, Event | `.Dropdown.DropdownItem` | `MonoBehaviour, IPointerEnterHandler, IEventSystemHandler, IC` | 11 | 8 |
| Tech, Firebase, Stat | `.FirebaseAuth.StateChangedDelegate` | `MulticastDelegate // TypeDefIndex: 10449` | 2 | 0 |
| Player, Save, Data | `.Player_Device_Saved_Datas` | `MonoBehaviour // TypeDefIndex: 318` | 3 | 0 |
| Player, Save, Data | `.Player_Saved_Datas` | `MonoBehaviour // TypeDefIndex: 319` | 32 | 7 |
| Gem, Mission, Popup | `.Popup_ChangeMissions` | `Popup_Notices // TypeDefIndex: 492` | 1 | 3 |
| Level, Popup, Event | `.Popup_EventLevelUp` | `MonoBehaviour // TypeDefIndex: 524` | 2 | 8 |
| Reward, PvP, Popup | `.Popup_PVPRewards` | `MonoBehaviour // TypeDefIndex: 874` | 9 | 9 |
| Shop, PvP, Popup | `.Popup_PVPShopExchange` | `MonoBehaviour // TypeDefIndex: 875` | 8 | 11 |
| Reward, Daily, Popup | `.Popup_PremiumDailyRewards` | `MonoBehaviour // TypeDefIndex: 1052` | 14 | 19 |
| UI, Popup, Event | `.Popup_QuitEvent` | `Popup_Notices // TypeDefIndex: 525` | 2 | 6 |
| Reward, Popup, Season | `.Popup_SeasonRewards` | `Popup // TypeDefIndex: 876` | 4 | 5 |
| Mission, Battle, Pass | `.Tab_BattlePassMission` | `MonoBehaviour // TypeDefIndex: 494` | 5 | 23 |
| Data, Firebase, Event | `Firebase.Database.ChildChangedEventArgs` | `EventArgs // TypeDefIndex: 9979` | 6 | 6 |
| Data, Firebase, Event | `Firebase.Database.ValueChangedEventArgs` | `EventArgs // TypeDefIndex: 9993` | 5 | 4 |
| Config, IAP, Firebase | `Firebase.Platform.Default.AppConfigExtensions` | `IAppConfigExtensions // TypeDefIndex: 10560` | 5 | 6 |
| Player, Item, PvP | `GamePVP.PlayerItemPVPEndGame` | `MonoBehaviour // TypeDefIndex: 1575` | 2 | 6 |
| Player, Item, PvP | `PVP.PlayerItemPVP` | `MonoBehaviour // TypeDefIndex: 1595` | 5 | 13 |
| Enemy, Boss, Event | `SpaceShooter.EnemySystem.Boss3_FootEvent` | `MonoBehaviour // TypeDefIndex: 2109` | 9 | 5 |
| Enemy, Boss, Spawn | `SpaceShooter.EnemySystem.Boss8_Spawner` | `MonoBehaviour // TypeDefIndex: 2169` | 17 | 12 |
| Enemy, Boss, Laser | `SpaceShooter.EnemySystem.BossLaser_Attack` | `MonoBehaviour // TypeDefIndex: 2188` | 11 | 16 |
| Enemy, Laser, Drone | `SpaceShooter.EnemySystem.Drone_Laser` | `MonoBehaviour // TypeDefIndex: 2368` | 6 | 6 |
| Data, Mode, Spin | `Spine.Unity.BlendModeMaterialsAsset` | `SkeletonDataModifierAsset // TypeDefIndex: 8643` | 3 | 4 |
| Data, Event, Spin | `Spine.Unity.EventDataReferenceAsset` | `ScriptableObject // TypeDefIndex: 8575` | 4 | 5 |
| Load, Ads, Stat | `System.Linq.Expressions.Interpreter.LoadStaticFieldInstruction` | `FieldInstruction // TypeDefIndex: 6805` | 4 | 2 |
| Data, Security, UI | `System.Security.Cryptography.X509Certificates.X500DistinguishedName` | `AsnEncodedData // TypeDefIndex: 5837` | 7 | 2 |
| Store, Config, IAP | `UnityEngine.Purchasing.AppleConfiguration` | `IAppleConfiguration, IStoreConfiguration // TypeDefIndex: 91` | 1 | 0 |
| Load, Ad , Purchase | `UnityEngine.Purchasing.ApplePurchaseFulfilledPayload` | `IPurchaseFulfilledPayload // TypeDefIndex: 9125` | 11 | 10 |
| Load, Ad , Purchase | `UnityEngine.Purchasing.GooglePurchaseFulfilledPayload` | `IPurchaseFulfilledPayload // TypeDefIndex: 9126` | 5 | 4 |
| Data, IAP, Security | `UnityEngine.Purchasing.Security.InvalidPKCS7Data` | `IAPSecurityException // TypeDefIndex: 10495` | 1 | 0 |
| Data, IAP, Security | `UnityEngine.Purchasing.Security.InvalidRSAData` | `IAPSecurityException // TypeDefIndex: 10498` | 1 | 0 |
| Data, IAP, Security | `UnityEngine.Purchasing.Security.InvalidX509Data` | `IAPSecurityException // TypeDefIndex: 10492` | 1 | 0 |
| Support, IAP, Security | `UnityEngine.Purchasing.Security.UnsupportedSignerInfoVersion` | `IAPSecurityException // TypeDefIndex: 10496` | 1 | 0 |
| Store, IAP, Purchase | `UnityEngine.Purchasing.Services.AppleStoreExtendedPurchaseService` | `PurchaseService, IAppleStoreExtendedPurchaseService // TypeD` | 12 | 10 |
| Player, Store, Data | `UnityEngine.Purchasing.Stores.PlayerData` | `IPlayerData // TypeDefIndex: 8382` | 10 | 12 |
| Store, Mode, Billing | `UnityEngine.Purchasing.Stores.Android.GooglePlay.AAR.Models.BillingClient` | `BillingClientBase, IBillingClient, IBillingClientBase // Typ` | 26 | 10 |
| UI, Panel, Event | `UnityEngine.UIElements.AttachToPanelEvent` | `PanelChangedEventBase<AttachToPanelEvent> // TypeDefIndex: 4` | 2 | 0 |
| Data, Drop, UI | `UnityEngine.UIElements.DefaultDragAndDropClient` | `DragAndDropData, IDragAndDrop // TypeDefIndex: 4193` | 9 | 6 |
| UI, Panel, Event | `UnityEngine.UIElements.DetachFromPanelEvent` | `PanelChangedEventBase<DetachFromPanelEvent> // TypeDefIndex:` | 2 | 0 |
| Drop, UI, Popup | `UnityEngine.UIElements.DropdownField` | `PopupField<string> // TypeDefIndex: 4019` | 2 | 0 |
| Item, Drop, UI | `UnityEngine.UIElements.DropdownMenuAction` | `DropdownMenuItem // TypeDefIndex: 4220` | 7 | 9 |
| Item, Drop, UI | `UnityEngine.UIElements.DropdownMenuSeparator` | `DropdownMenuItem // TypeDefIndex: 4218` | 1 | 1 |
| Debug, UI, Event | `UnityEngine.UIElements.EventDebuggerLogCall` | `IDisposable // TypeDefIndex: 4267` | 2 | 0 |
| Debug, UI, Event | `UnityEngine.UIElements.EventDebuggerLogExecuteDefaultAction` | `IDisposable // TypeDefIndex: 4269` | 2 | 0 |
| Debug, UI, Event | `UnityEngine.UIElements.EventDebuggerLogIMGUICall` | `IDisposable // TypeDefIndex: 4268` | 2 | 0 |
| UI, Panel, Event | `UnityEngine.UIElements.PanelEventHandler` | `UIBehaviour, IPointerMoveHandler, IEventSystemHandler, IPoin` | 37 | 11 |
| Setting, UI, Panel | `UnityEngine.UIElements.PanelSettings` | `ScriptableObject // TypeDefIndex: 4410` | 52 | 52 |
| Setting, UI, Panel | `UnityEngine.UIElements.PanelTextSettings` | `TextSettings // TypeDefIndex: 4644` | 5 | 5 |
| UI, Event, Stat | `UnityEngine.UIElements.PointerStationaryEvent` | `PointerEventBase<PointerStationaryEvent> // TypeDefIndex: 43` | 4 | 0 |
| Save, Data, UI | `UnityEngine.UIElements.SavePersistentViewData` | `MulticastDelegate // TypeDefIndex: 4461` | 2 | 0 |
| UI, Screen, Event | `UnityEngine.UIElements.TouchScreenTextEditorEventHandler` | `TextEditorEventHandler // TypeDefIndex: 4065` | 11 | 3 |
| UI, Event, Wheel | `UnityEngine.UIElements.WheelEvent` | `MouseEventBase<WheelEvent> // TypeDefIndex: 4313` | 9 | 2 |
| Event, Stat | `.AnimationState.TrackEntryEventDelegate` | `MulticastDelegate // TypeDefIndex: 8505` | 2 | 0 |
| Data, Stat | `.AnimationStateData.AnimationPairComparer` | `IEqualityComparer<AnimationStateData.AnimationPair> // TypeD` | 4 | 1 |
| Battle, Pass | `.Board_BattlePass` | `Board // TypeDefIndex: 475` | 71 | 53 |
| Battle, Pass | `.Board_BattlePassPro` | `Board // TypeDefIndex: 488` | 101 | 91 |
| Reward, Quest | `.Board_QuestRewards` | `Board // TypeDefIndex: 930` | 25 | 38 |
| Shop, Coin | `.Board_ShopCoins` | `Board // TypeDefIndex: 1106` | 24 | 25 |
| Shop, Energy | `.Board_ShopEnergy` | `Board // TypeDefIndex: 683` | 20 | 15 |
| Shop, Gem | `.Board_ShopGems` | `Board // TypeDefIndex: 1113` | 57 | 66 |
| Boss, Event | `.Boss10_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 144` | 19 | 17 |
| Boss, Event | `.Boss11_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 145` | 13 | 11 |
| Boss, Event | `.Boss12_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 148` | 13 | 12 |
| Boss, Event | `.Boss13_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 153` | 1 | 0 |
| Boss, Event | `.Boss15_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 154` | 23 | 22 |
| Boss, Event | `.Boss17_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 155` | 15 | 14 |
| Boss, Event | `.Boss18_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 158` | 20 | 19 |
| Boss, Event | `.Boss1_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 143` | 13 | 12 |
| Boss, Event | `.Boss3_PlasmaAnimEvent` | `MonoBehaviour // TypeDefIndex: 120` | 6 | 6 |
| Boss, Event | `.Boss4_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 185` | 7 | 2 |
| Boss, Laser | `.Boss4_BigLaser` | `MonoBehaviour // TypeDefIndex: 186` | 8 | 11 |
| Boss, Event | `.Boss5_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 188` | 3 | 2 |
| Boss, Event | `.Boss6_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 189` | 7 | 6 |
| Boss, Event | `.Boss6_Mini_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 192` | 16 | 10 |
| Boss, Event | `.Boss7_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 193` | 12 | 10 |
| Boss, Event | `.Boss8_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 195` | 9 | 8 |
| Boss, Event | `.Boss9_AnimationEvents` | `MonoBehaviour // TypeDefIndex: 196` | 12 | 10 |
| Boss, Event | `.BossAnimationEvents` | `MonoBehaviour // TypeDefIndex: 205` | 5 | 3 |
| Bullet, Spawn | `.BridgeSpawnBullets` | `MonoBehaviour // TypeDefIndex: 1508` | 5 | 7 |
| Tech, Stat | `.CullingGroup.StateChanged` | `MulticastDelegate // TypeDefIndex: 7683` | 2 | 0 |
| Shop, Data | `.DataShopPack` | `MonoBehaviour // TypeDefIndex: 988` | 3 | 10 |
| Boss, Data | `.Data_Boss` | `ScriptableObject // TypeDefIndex: 769` | 1 | 1 |
| Item, Data | `.Data_Items` | `ScriptableObject // TypeDefIndex: 739` | 1 | 1 |
| Player, Data | `.Data_Players` | `ScriptableObject // TypeDefIndex: 815` | 1 | 1 |
| Save, Data | `.Device_Saved_Data` | `MonoBehaviour // TypeDefIndex: 583` | 17 | 4 |
| Laser, Drone | `.Drone10_Lasers` | `MonoBehaviour // TypeDefIndex: 285` | 6 | 11 |
| Data, Drone | `.Drone_Get_Datas` | `MonoBehaviour // TypeDefIndex: 291` | 21 | 56 |
| Bullet, Drop | `.Drop_AttackBulletCircle` | `MonoBehaviour // TypeDefIndex: 126` | 7 | 11 |
| Bullet, Drop | `.Drop_Bullet` | `MonoBehaviour // TypeDefIndex: 128` | 7 | 9 |
| Enemy, Data | `.Enemy_Data_Balance` | `MonoBehaviour // TypeDefIndex: 222` | 8 | 1 |
| Bullet, Event | `.EventBullet` | `MonoBehaviour // TypeDefIndex: 87` | 2 | 1 |
| Analytics, Firebase | `.FirebaseAnalyticsInternalPINVOKE.SWIGExceptionHelper.ExceptionArgumentDelegate` | `MulticastDelegate // TypeDefIndex: 10760` | 2 | 0 |
| Analytics, Firebase | `.FirebaseAnalyticsInternalPINVOKE.SWIGExceptionHelper.ExceptionDelegate` | `MulticastDelegate // TypeDefIndex: 10759` | 2 | 0 |
| Analytics, Firebase | `.FirebaseAnalyticsInternalPINVOKE.SWIGStringHelper.SWIGStringDelegate` | `MulticastDelegate // TypeDefIndex: 10763` | 2 | 0 |
| Data, Firebase | `.FirebaseDatabaseManager` | `MonoBehaviour // TypeDefIndex: 1485` | 20 | 2 |
| Data, Firebase | `.FirebaseDatabaseManager.WaitTask` | `CustomYieldInstruction // TypeDefIndex: 1480` | 2 | 2 |
| Firebase, Event | `.FirebaseHandler.ApplicationFocusChangedEventArgs` | `EventArgs // TypeDefIndex: 10551` | 2 | 2 |
| Shop, UI | `.FixUIShop` | `MonoBehaviour // TypeDefIndex: 1115` | 2 | 4 |
| Skin, UI | `.GUISkin.SkinChangedDelegate` | `MulticastDelegate // TypeDefIndex: 9549` | 2 | 0 |
| Chapter, Data | `.GenerateDataChapter2` | `MonoBehaviour // TypeDefIndex: 1509` | 5 | 5 |
| Config, Stat | `.InternalLiveContentAdapterService.<>c__DisplayClass6_0.<<GetConfigsContent>b__0>d` | `IAsyncStateMachine // TypeDefIndex: 10079` | 2 | 4 |
| Shop, Stat | `.InternalWebshopService.<>c__DisplayClass7_0.<<GetWebshopLink>b__0>d` | `IAsyncStateMachine // TypeDefIndex: 10213` | 2 | 4 |
| Data, Language | `.LanguageStringData` | `ScriptableObject // TypeDefIndex: 1441` | 1 | 1 |
| Language, UI | `.LanguageTextMeshProUI` | `MonoBehaviour // TypeDefIndex: 1373` | 6 | 2 |

## String literals

- count: **15053**

### URLs (53)

- `http://`
- `http://james.newtonking.com/projects/json`
- `http://microsoft.com/wsdl/types/`
- `http://play.google.com/store/apps/dev?id=6177492284961668428`
- `http://schemas.microsoft.com/ws/2008/06/identity/claims/role`
- `http://schemas.xmlsoap.org/soap/encoding/`
- `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name`
- `http://schemas.xmlsoap.org/wsdl/`
- `http://www.google.com`
- `http://www.w3.org/`
- `http://www.w3.org/1999/XMLSchema-instance`
- `http://www.w3.org/2000/09/xmldsig#dsa-sha1`
- `http://www.w3.org/2000/09/xmldsig#hmac-sha1`
- `http://www.w3.org/2000/09/xmldsig#rsa-sha1`
- `http://www.w3.org/2000/09/xmldsig#sha1`
- `http://www.w3.org/2000/10/XMLSchema-instance`
- `http://www.w3.org/2000/xmlns/`
- `http://www.w3.org/2001/04/xmldsig-more#hmac-ripemd160`
- `http://www.w3.org/2001/04/xmldsig-more#hmac-sha256`
- `http://www.w3.org/2001/04/xmldsig-more#hmac-sha384`
- `http://www.w3.org/2001/04/xmldsig-more#hmac-sha512`
- `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256`
- `http://www.w3.org/2001/04/xmldsig-more#rsa-sha384`
- `http://www.w3.org/2001/04/xmldsig-more#rsa-sha512`
- `http://www.w3.org/2001/04/xmldsig-more#sha384`
- `http://www.w3.org/2001/04/xmlenc#sha256`
- `http://www.w3.org/2001/04/xmlenc#sha512`
- `http://www.w3.org/2001/XMLSchema`
- `http://www.w3.org/2001/XMLSchema#string`
- `http://www.w3.org/2001/XMLSchema-instance`
- `http://www.w3.org/2003/11/xpath-datatypes`
- `http://www.w3.org/XML/1998/namespace`
- `https://connect.facebook.net`
- `https://developers.facebook.com/tools/accesstoken/?app_id={0}`
- `https://fb.com/102822501559770`
- `https://fb.com/1704897876310415`
- `https://fb.com/2042575349375682`
- `https://fb.com/815662392331651`
- `https://gcenterstudio.com/privacy-policy/`
- `https://graph.{0}/{1}/`
- `https://iap-stg.services.api.unity.com`
- `https://iap.services.api.unity.com`
- `https://localhost/`
- `https://play.google.com/store/apps/details?id=`
- `https://prd.insights.analytics.unity3d.com/v1/ingest/producer`
- `https://services.api.unity.com/live-content/client/v1`
- `https://services.api.unity.com/schema-registry/v1/schemas/UnityRemoteCatalog`
- `https://services.api.unity.com/schema-registry/v1/schemas/UnityRemoteCatalogWebshop`
- `https://staging.services.api.unity.com/live-content/client/v1`
- `https://us-central1-universe-invader2-alien-war.cloudfunctions.net/validatePurchase`
- `https://webshop-stg.services.api.unity.com`
- `https://webshop.services.api.unity.com`
- `https://www.gstatic.com/firebase/ssl/roots.pem`

### IPs (30)

- `0.0.0.0`
- `127.0.0.1`
- `2.5.29.10`
- `2.5.29.14`
- `2.5.29.15`
- `2.5.29.17`
- `2.5.29.18`
- `2.5.29.19`
- `2.5.29.20`
- `2.5.29.21`
- `2.5.29.35`
- `2.5.29.37`
- `2.5.4.10`
- `2.5.4.11`
- `2.5.4.12`
- `2.5.4.13`
- `2.5.4.17`
- `2.5.4.18`
- `2.5.4.20`
- `2.5.4.24`
- `2.5.4.3`
- `2.5.4.4`
- `2.5.4.42`
- `2.5.4.43`
- `2.5.4.46`
- `2.5.4.5`
- `2.5.4.6`
- `2.5.4.7`
- `2.5.4.8`
- `2.5.4.9`

### Emails (1)

- `support@gcenterstudio.com`

### JSON-looking literals: 315

- `
	{0}: {1}`
- `
{0}:`
- ` 	
{}[],:"`
- ` [`
- ` [0x{0:x5}]`
- ` [Non-matching signature algorithms in CRL]`
- ` {
`
- ` { `
- ` {0:D}h`
- ` {0:D}m`
- ` {0:D}s`
- ` {0}`
- ` {0} isn't a valid Sort string entry.`
- ` {0}-{1}`
- ` {0}/{1}<sprite=3>`
- ` {M: GPUL.HEC} - Google BillingResponseCode = `
- ` {M: GPUL.OPF}`
- ` {code: `
- `[`
- `[ <length-percentage> ]{1,4}`
- `[ <length-percentage> | auto ]{1,2} | cover | contain`
- `[ <length-percentage> | auto ]{1,4}`
- `[ <length> | <percentage> | left | center | right | top | bottom ] | [ [ <length> | <percentage>  | left | center | right ] && [ <length> | <percentage>  | top | center | bottom ] ] <length>?`
- `[ [ <resource> | <url> ] [ <integer> <integer> ]? ] | [ arrow | text | resize-vertical | resize-horizontal | link | slide-arrow | resize-up-right | resize-up-left | move-arrow | rotate-arrow | scale-arrow | arrow-plus | arrow-minus | pan | orbit | zoom | fps | split-resize-up-down | split-resize-lef`
- `[ [ left | center | right | top | bottom | <length-percentage> ] | [ left | center | right | <length-percentage> ] [ top | center | bottom | <length-percentage> ] | [ center | [ left | right ] <length-percentage>? ] && [ center | [ top | bottom ] <length-percentage>? ] ]`
- `[ center | [ [ left | right ]? <length-percentage>? ] ]`
- `[ center | [ [ top | bottom ]? <length-percentage>? ] ]`
- `[ none | <single-transition-property> ] || <time> || <easing-function> || <time>`
- `['`
- `[*]`
- `[+]`
- `[-]`
- `[.]`
- `[/]`
- `[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}`
- `[0]`
- `[1]`
- `[2]`
- `[3]`
- `[4]`
- `[5]`
- `[6]`
- `[7]`
- `[8]`
- `[9]`
- `[=]`
- `[Achievement] id={0}, name={1}, desc={2}, type={3}, revealed={4}, unlocked={5}, steps={6}/{7}`
- `[AdInfo adUnitIdentifier: `
- `[Alert: {0}:{1}]`
- `[Analytic] LogEvent {0}/{1}`
- `[Analytic] LogEvent {0}: {1}`
- `[Analytic] LogEvent {0}: {1}/{2}`
- `[Android] Wind Wings`
- `[Android] Wind Wings Premium`
- `[BoundingBox]`
- `[BufferOffsetSize: {0} {1}]`
- `[CDATA[`
- `[CheckEntitlement] Missing request for product id: `
- `[DISPID=0]`
- `[E-`
- `[E-{0}] {1}`
- `[ErrorInfo code: `
- `[Extensions]`
- `[Fixed]Backup new data failled!`
- `[Fixed]Backup new data success!`
- `[Fixed]Delete old data success!`
- `[Fixed]Failed to sign in firebase!`
- `[Fixed]Failled to delete old data!`
- `[Fixed]Failled to link Firebase user!`
- `[Fixed]Linked Firebase user:`
- `[Fixed]Restore failled!.`
- `[Fixed]Restore from new struct data.`
- `[Fixed]Restore success!.`
- `[Fixed]Restored data!`
- `[Fixed]Set profile to display!`
- `[Fixed]Signed In User: `
- `[Fixed]Start backup new data!`
- `[Fixed]Start create new data!`
- `[Fixed]Start delete old data!`
- `[Fixed]create new data failled!`
- `[Fixed]create new data success!`
- `[Fixed]has old struct data!`
- `[Fixed]no old struct data!`
- `[IAP] Another purchase is already in progress.`
- `[IAP] ConfirmPurchase failed; the processed transaction can be confirmed on redelivery. `
- `[IAP] Fulfillment callback failed. Purchase remains pending: `
- `[IAP] IAPProduct resource was not found. IAP cannot be initialized.`
- `[IAP] No product IDs were configured.`
- `[IAP] Pending order has no product and was not confirmed.`
- `[IAP] Product fetch failed: `
- `[IAP] Products fetched: `
- `[IAP] Purchase deferred; waiting for store approval: `
- `[IAP] Purchase failed: `
- `[IAP] Purchase fetch failed: `
- `[IAP] PurchaseProduct failed: `
- `[IAP] Queued purchase failed: `
- `[IAP] Recovered pending purchase is waiting for its fulfillment callback: `
- `[IAP] Recovered purchase fulfilled: `
- `[IAP] Restore failed: `
- `[IAP] Store Connect completed but the store is not connected.`

### Anti-cheat / debug / emulator strings: 99

- `
Proxy-Authorization: `
- `
Proxy-Connection: keep-alive`
- ` <c# proxy java object>`
- ` [Non-matching signature algorithms in CRL]`
- `(407) Proxy Authentication Required`
- `---------ResetCheat`
- `---------ResetCheat:`
- `After Root Level Attribute`
- `AndroidJNIHelper.GetSignature: using Byte parameters is obsolete, use SByte parameters instead`
- `Boards/Popup_Common/Popup_CheatForceQuit`
- `Boards/Popup_Common/Popup_CheatTime`
- `CHEAT`
- `CHECK_PLAYER_CHEAT_TIME_BACK`
- `Clip update roots	: `
- `Could not find rootVisualContainer...`
- `DTD must be defined before the document root element.`
- `Data at the root level is invalid.`
- `Digital Signature`
- `Document does not have a root element.`
- `EndRootElement`
- `Expected schema root. Make sure the root element is <schema> and the namespace is 'http://www.w3.org/2001/XMLSchema' for an XSD schema or 'urn:schemas-microsoft-com:xml-data' for an XDR schema.`
- `Field {0} or type signature {1} not found`
- `Friday`
- `HAS_CHEAT_TIME`
- `Invalid BinaryXml signature.`
- `Invalid MAC - file may have been tampered with!`
- `Invalid URI: A Dos path must be rooted, for example, 'c:\\'.`
- `JNI: Unknown signature for type '`
- `JSON root object has multiple properties. The root object must have a single property in order to create a valid XML document. Consider specifying a DeserializeRootElementName.`
- `JSON root object has property '{0}' that will be converted to an attribute. A root object cannot have any attribute properties. Consider specifying a DeserializeRootElementName.`
- `MMSignature`
- `Method {0}.{1}() specified by XmlSchemaProviderAttribute has invalid signature: return type must be compatible with System.Xml.XmlQualifiedName.`
- `No such proxy method: `
- `Opacity update roots	: `
- `Proxy`
- `Proxy Authentication Required`
- `Proxy scheme not supported.`
- `Proxy support not available.`
- `Proxy-Authenticate`
- `Proxy-Authorization`
- `Proxy-Connection`
- `Root`
- `Root Level Attribute Value`
- `Root Level Base64 Attribute Value`
- `Root Level Special Attribute Value`
- `Root element is missing.`
- `Root element name must match the DocType name.`
- `Signature`
- `Signature CA`
- `Signature2`
- `SkeletonUtility-SkeletonRoot`
- `SoxAtkJiggleboneProxyAlign_`
- `SoxAtkJiggleboneProxyLook_`
- `SoxAtkJiggleboneTargetRoot_`
- `System.Security.Cryptography.DSASignatureDeformatter`
- `System.Security.Cryptography.DSASignatureFormatter`
- `System.Security.Cryptography.RSAPKCS1SignatureDeformatter`
- `System.Security.Cryptography.RSAPKCS1SignatureFormatter`
- `The SyncRoot property may not be used for the synchronization of concurrent collections.`
- `The group ref to 'all' is not the root particle, or it is being used as an extension.`
- `The method signature cannot be null.`
- `The object {0} is being remoted by a proxy that does not support interface discovery.  This type of remoted object is not supported.`
- `The root element of a W3C XML Schema should be <schema> and its namespace should be 'http://www.w3.org/2001/XMLSchema'.`
- `There are multiple root elements.`
- `This method is not supported on signature types.`
- `Use Proxy`
- `Visual update roots	: `
- `VisualElement Generic Menu needs a target to find a root to attach to.`
- `Xform update roots	: `
- `XmlRoot and XmlType attributes may not be specified for the type `
- `[Signature Algorithm]`
- `_ProxyAddress`
- `__MethodSignature`
- `com.google.games.bridge.PayloadCallbackProxy`
- `com/google/games/bridge/ConnectionLifecycleCallbackProxy$Callback`
- `com/google/games/bridge/EndpointDiscoveryCallbackProxy$Callback`
- `com/google/games/bridge/PayloadCallbackProxy$Callback`
- `couldn't compute signature verification`
- `excludeFromFocusRing should only be set on composite roots.`
- `getFieldSignature`
- `getSignature`
- `https://www.gstatic.com/firebase/ssl/roots.pem`
- `invalid signature length`
- `newProxyInstance`
- `proxy`
- `rgbSignature`
- `root`
- `signature`
- `signatureJws`
- `system.security.cryptography.dsasignaturedeformatter`
- `system.security.cryptography.dsasignaturedescription`
- `system.security.cryptography.dsasignatureformatter`
- `system.security.cryptography.rsapkcs1sha1signaturedescription`
- `system.security.cryptography.rsapkcs1sha256signaturedescription`
- `system.security.cryptography.rsapkcs1sha384signaturedescription`
- `system.security.cryptography.rsapkcs1sha512signaturedescription`
- `system.security.cryptography.rsapkcs1signaturedeformatter`
- `system.security.cryptography.rsapkcs1signatureformatter`
- `unity-ui-document__root`
```
Initializing metadata...
Metadata Version: 31
Initializing il2cpp file...
Applying relocations...
WARNING: find JNI_OnLoad
ERROR: This file may be protected.
Il2Cpp Version: 31
Searching...
CodeRegistration : 2996ef8
MetadataRegistration : 2a55ea0
Dumping...
Done!
Generate struct...
Done!
Generate dummy dll...
Done!
Press any key to exit...
Unhandled exception. System.InvalidOperationException: Cannot read keys when either application does not have a console or when console input has been redirected. Try Console.Read.
   at System.ConsolePal.ReadKey(Boolean intercept)
   at Il2CppDumper.Program.Main(String[] args) in C:\projects\il2cppdumper\Il2CppDumper\Program.cs:line 110
```
