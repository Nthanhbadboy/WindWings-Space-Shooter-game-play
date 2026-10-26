// ===== keywords: Store, Load, Data, Ad , Mode
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class AppStorePayload : IStorePayload // TypeDefIndex: 8461
{
	// Fields
	[CompilerGenerated]
	private string <AppReceipt>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <JwsRepresentation>k__BackingField; // 0x18
	[CompilerGenerated]
	private string <OriginalTransactionId>k__BackingField; // 0x20
	[CompilerGenerated]
	private string <AppAccountToken>k__BackingField; // 0x28
	[CompilerGenerated]
	private OwnershipType <OwnershipType>k__BackingField; // 0x30

	// Properties
	public string AppReceipt { get; set; }
	public string JwsRepresentation { get; set; }
	public string OriginalTransactionId { get; set; }
	public string AppAccountToken { get; set; }
	public OwnershipType OwnershipType { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C0430 Offset: 0x26BC430 VA: 0x26C0430
	public string get_AppReceipt() { }

	[CompilerGenerated]
	// RVA: 0x26C0438 Offset: 0x26BC438 VA: 0x26C0438
	public void set_AppReceipt(string value) { }

	[CompilerGenerated]
	// RVA: 0x26C0440 Offset: 0x26BC440 VA: 0x26C0440
	public string get_JwsRepresentation() { }

	[CompilerGenerated]
	// RVA: 0x26C0448 Offset: 0x26BC448 VA: 0x26C0448
	public void set_JwsRepresentation(string value) { }

	[CompilerGenerated]
	// RVA: 0x26C0450 Offset: 0x26BC450 VA: 0x26C0450
	public string get_OriginalTransactionId() { }

	[CompilerGenerated]
	// RVA: 0x26C0458 Offset: 0x26BC458 VA: 0x26C0458
	public void set_OriginalTransactionId(string value) { }

	[CompilerGenerated]
	// RVA: 0x26C0460 Offset: 0x26BC460 VA: 0x26C0460
	public string get_AppAccountToken() { }

	[CompilerGenerated]
	// RVA: 0x26C0468 Offset: 0x26BC468 VA: 0x26C0468
	public void set_AppAccountToken(string value) { }

	[CompilerGenerated]
	// RVA: 0x26C0470 Offset: 0x26BC470 VA: 0x26C0470
	public OwnershipType get_OwnershipType() { }

	[CompilerGenerated]
	// RVA: 0x26C0478 Offset: 0x26BC478 VA: 0x26C0478
	public void set_OwnershipType(OwnershipType value) { }

	// RVA: 0x26BB388 Offset: 0x26B7388 VA: 0x26BB388
	public void .ctor() { }
}


// ===== keywords: Store, Load, Data, Ad , Mode
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class GooglePlayPayload : IStorePayload // TypeDefIndex: 8462
{
	// Fields
	[CompilerGenerated]
	private string <OriginalJson>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <Signature>k__BackingField; // 0x18

	// Properties
	public string OriginalJson { get; set; }
	public string Signature { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C0480 Offset: 0x26BC480 VA: 0x26C0480
	public string get_OriginalJson() { }

	[CompilerGenerated]
	// RVA: 0x26C0488 Offset: 0x26BC488 VA: 0x26C0488
	public void set_OriginalJson(string value) { }

	[CompilerGenerated]
	// RVA: 0x26C0490 Offset: 0x26BC490 VA: 0x26C0490
	public string get_Signature() { }

	[CompilerGenerated]
	// RVA: 0x26C0498 Offset: 0x26BC498 VA: 0x26C0498
	public void set_Signature(string value) { }

	// RVA: 0x26BB3A8 Offset: 0x26B73A8 VA: 0x26BB3A8
	public void .ctor() { }
}


// ===== keywords: Store, Data, Mode, Purchase, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class PurchaseFailedEvent : IEventVariant // TypeDefIndex: 8448
{
	// Fields
	[CompilerGenerated]
	private FailureReason <FailureReason>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <FailureMessage>k__BackingField; // 0x18

	// Properties
	public FailureReason FailureReason { get; set; }
	public string FailureMessage { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C02A4 Offset: 0x26BC2A4 VA: 0x26C02A4
	public FailureReason get_FailureReason() { }

	[CompilerGenerated]
	// RVA: 0x26C02AC Offset: 0x26BC2AC VA: 0x26C02AC
	public void set_FailureReason(FailureReason value) { }

	[CompilerGenerated]
	// RVA: 0x26C02B4 Offset: 0x26BC2B4 VA: 0x26C02B4
	public string get_FailureMessage() { }

	[CompilerGenerated]
	// RVA: 0x26C02BC Offset: 0x26BC2BC VA: 0x26C02BC
	public void set_FailureMessage(string value) { }

	// RVA: 0x26BCFF4 Offset: 0x26B8FF4 VA: 0x26BCFF4
	public void .ctor() { }
}


// ===== keywords: Store, Data, Mode, Purchase, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class PurchaseFulfilledEvent : IEventVariant // TypeDefIndex: 8449
{
	// Fields
	[CompilerGenerated]
	private IStorePayload <Payload>k__BackingField; // 0x10

	// Properties
	public IStorePayload Payload { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C02C4 Offset: 0x26BC2C4 VA: 0x26C02C4
	public IStorePayload get_Payload() { }

	[CompilerGenerated]
	// RVA: 0x26C02CC Offset: 0x26BC2CC VA: 0x26C02CC
	public void set_Payload(IStorePayload value) { }

	// RVA: 0x26BD790 Offset: 0x26B9790 VA: 0x26BD790
	public void .ctor() { }
}


// ===== keywords: Store, Data, Mode, Purchase, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class PurchaseIntentStartEvent : IEventVariant // TypeDefIndex: 8446
{
	// Methods

	// RVA: 0x26BDE48 Offset: 0x26B9E48 VA: 0x26BDE48
	public void .ctor() { }
}


// ===== keywords: Store, Data, Mode, Purchase, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class PurchasePaidEvent : IEventVariant // TypeDefIndex: 8447
{
	// Fields
	[CompilerGenerated]
	private IStorePayload <Payload>k__BackingField; // 0x10

	// Properties
	public IStorePayload Payload { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C0294 Offset: 0x26BC294 VA: 0x26C0294
	public IStorePayload get_Payload() { }

	[CompilerGenerated]
	// RVA: 0x26C029C Offset: 0x26BC29C VA: 0x26C029C
	public void set_Payload(IStorePayload value) { }

	// RVA: 0x26BE5E4 Offset: 0x26BA5E4 VA: 0x26BE5E4
	public void .ctor() { }
}


// ===== keywords: Level, Battle, Popup, Pass
// Namespace: 
public class Popup_BattlePassLevelUp : Popup_Notices // TypeDefIndex: 491
{
	// Fields
	[SerializeField]
	private TextMeshPro textLevel; // 0x58
	[SerializeField]
	private GameObject btnExit; // 0x60

	// Methods

	// RVA: 0x15D7D8C Offset: 0x15D3D8C VA: 0x15D7D8C
	public void LevelUp(int oldLv, int crtLv) { }

	// RVA: 0x15DB204 Offset: 0x15D7204 VA: 0x15DB204
	private IEnumerator IEUpdateText(int oldLv, int crtLv) { }

	// RVA: 0x15DB29C Offset: 0x15D729C VA: 0x15DB29C
	public void .ctor() { }
}


// ===== keywords: Upgrade, Tech, IAP, Popup
// Namespace: 
public class Popup_UpgradeTechIAP : Popup // TypeDefIndex: 1179
{
	// Fields
	[SerializeField]
	private TextMeshPro[] allTextStatLevels; // 0x30
	[SerializeField]
	private TextMeshPro textTechLevel; // 0x38
	[SerializeField]
	private TextMeshPro textPrice; // 0x40
	[SerializeField]
	private TextMeshPro textVipPoint; // 0x48
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x50
	[SerializeField]
	private GameObject loadingObject; // 0x58
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x60
	public Action upgradeConfirm; // 0x68
	private int idProduct; // 0x70
	private Coroutine checkTimeOut; // 0x78

	// Methods

	// RVA: 0x139A188 Offset: 0x1396188 VA: 0x139A188
	private void OnEnable() { }

	// RVA: 0x139A31C Offset: 0x139631C VA: 0x139A31C
	private IEnumerator IESetPrices() { }

	// RVA: 0x139A3A4 Offset: 0x13963A4 VA: 0x139A3A4
	public void OnPressedButtonUpgrade() { }

	// RVA: 0x139A7AC Offset: 0x13967AC VA: 0x139A7AC
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x139A7BC Offset: 0x13967BC VA: 0x139A7BC
	private void <IESetPrices>g__OnInitialized|11_1() { }

	[CompilerGenerated]
	// RVA: 0x139A660 Offset: 0x1396660 VA: 0x139A660
	private IEnumerator <OnPressedButtonUpgrade>g__IECheckLoadingTimeOut|12_2() { }

	[CompilerGenerated]
	// RVA: 0x139A6C0 Offset: 0x13966C0 VA: 0x139A6C0
	private void <OnPressedButtonUpgrade>g__Purchase|12_3(int _id, Action<int, bool> _callback) { }

	[CompilerGenerated]
	// RVA: 0x139A9F0 Offset: 0x13969F0 VA: 0x139A9F0
	private void <OnPressedButtonUpgrade>g__OnPurchased|12_4(int _idProduct, bool _successed) { }
}


// ===== keywords: Store, Data, Purchase, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights
internal sealed class PurchaseEventEmitter : IPurchaseEventEmitter // TypeDefIndex: 8434
{
	// Fields
	private readonly IPlayerData m_PlayerData; // 0x10
	private readonly ICoreRegistryHelper m_CoreRegistry; // 0x18
	private readonly string m_StoreName; // 0x20

	// Methods

	[Preserve]
	// RVA: 0x26BAEF4 Offset: 0x26B6EF4 VA: 0x26BAEF4
	public void .ctor(IPlayerData playerData, ICoreRegistryHelper coreRegistry, IStoreWrapper storeWrapper) { }

	[AsyncStateMachine(typeof(PurchaseEventEmitter.<SendPurchaseIntentStartEvent>d__4))]
	// RVA: 0x26BAFE8 Offset: 0x26B6FE8 VA: 0x26BAFE8 Slot: 4
	public void SendPurchaseIntentStartEvent(ICart cart) { }

	[AsyncStateMachine(typeof(PurchaseEventEmitter.<SendPurchasePaidEvent>d__6))]
	// RVA: 0x26BB080 Offset: 0x26B7080 VA: 0x26BB080 Slot: 5
	public void SendPurchasePaidEvent(PendingOrder order, IPurchaseFulfilledPayload payload) { }

	[AsyncStateMachine(typeof(PurchaseEventEmitter.<SendPurchaseFailedEvent>d__7))]
	// RVA: 0x26BB124 Offset: 0x26B7124 VA: 0x26BB124 Slot: 6
	public void SendPurchaseFailedEvent(FailedOrder order) { }

	[AsyncStateMachine(typeof(PurchaseEventEmitter.<SendPurchaseFulfilledEvent>d__8))]
	// RVA: 0x26BB1BC Offset: 0x26B71BC VA: 0x26BB1BC Slot: 7
	public void SendPurchaseFulfilledEvent(ConfirmedOrder order, IPurchaseFulfilledPayload payload) { }

	// RVA: 0x26BB260 Offset: 0x26B7260 VA: 0x26BB260
	private static void LogEmissionFailure(string variant, Exception e) { }

	// RVA: 0x26BB264 Offset: 0x26B7264 VA: 0x26BB264
	private static IStorePayload MapPayload(IPurchaseFulfilledPayload payload) { }

	// RVA: 0x26BB3F8 Offset: 0x26B73F8 VA: 0x26BB3F8
	internal static void Forward(IAPSDKEvent iaps) { }

	// RVA: 0x26BB5C4 Offset: 0x26B75C4 VA: 0x26BB5C4
	private static void ForwardGateway(byte[] body) { }

	// RVA: 0x26BB90C Offset: 0x26B790C VA: 0x26BB90C
	private IAPSDKEvent BuildEnvelope(CartItem cartItem, string transactionId, PlayerIdentity pps, IEventVariant variant) { }

	// RVA: 0x26BBCAC Offset: 0x26B7CAC VA: 0x26BBCAC
	internal static DeviceInfo BuildSdkDeviceInfo(RuntimePlatform platform) { }

	// RVA: 0x26BC0C0 Offset: 0x26B80C0 VA: 0x26BC0C0
	private static Store DeriveStore(string storeName) { }

	// RVA: 0x26BBDC0 Offset: 0x26B7DC0 VA: 0x26BBDC0
	internal static ConsentState ParseConsent(string s) { }

	// RVA: 0x26BBE74 Offset: 0x26B7E74 VA: 0x26BBE74
	private PlayerIdentity MapIdentity(PlayerIdentity pps) { }

	// RVA: 0x26BC228 Offset: 0x26B8228 VA: 0x26BC228
	internal static PlayerIdentity MapIdentity(PlayerIdentity pps, ICoreRegistryHelper coreRegistry) { }

	// RVA: 0x26BBE84 Offset: 0x26B7E84 VA: 0x26BBE84
	internal static DeviceInfo MapDeviceInfo(DeviceInfo sdk) { }

	// RVA: 0x26BC1A4 Offset: 0x26B81A4 VA: 0x26BC1A4
	private static OrderData BuildOrder(CartItem cartItem, string transactionId) { }

	// RVA: 0x26BC470 Offset: 0x26B8470 VA: 0x26BC470
	private static Sku BuildSku(CartItem cartItem) { }

	// RVA: 0x26BC734 Offset: 0x26B8734 VA: 0x26BC734
	private static ProductType MapProductType(ProductType v) { }

	// RVA: 0x26BC74C Offset: 0x26B874C VA: 0x26BC74C
	private static FailureReason MapFailureReason(PurchaseFailureReason v) { }

	// RVA: 0x26BB390 Offset: 0x26B7390 VA: 0x26BB390
	private static OwnershipType MapOwnership(OwnershipType v) { }
}


// ===== keywords: Store, Data, Mode, Event
// Namespace: UnityEngine.Purchasing.Stores.Data.Insights.Models
internal sealed class PaymentOptionsShownEvent : IEventVariant // TypeDefIndex: 8451
{
	// Fields
	[CompilerGenerated]
	private List<PaymentOption> <OptionsShown>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <OptionsDefaultProvider>k__BackingField; // 0x18

	// Properties
	public List<PaymentOption> OptionsShown { get; }
	public string OptionsDefaultProvider { get; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26C02D4 Offset: 0x26BC2D4 VA: 0x26C02D4
	public List<PaymentOption> get_OptionsShown() { }

	[CompilerGenerated]
	// RVA: 0x26C02DC Offset: 0x26BC2DC VA: 0x26C02DC
	public string get_OptionsDefaultProvider() { }
}


// ===== keywords: Tech, Analytics, Stat
// Namespace: 
public sealed class AnalyticsSessionInfo.SessionStateChanged : MulticastDelegate // TypeDefIndex: 10800
{
	// Methods

	// RVA: 0x298B25C Offset: 0x298725C VA: 0x298B25C
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x298B2E8 Offset: 0x29872E8 VA: 0x298B2E8 Slot: 12
	public virtual void Invoke(AnalyticsSessionState sessionState, long sessionId, long sessionElapsedTime, bool sessionChanged) { }
}


// ===== keywords: Load, Ads, Stat
// Namespace: 
private class AndroidAssetPacks.AssetPackManagerDownloadStatusCallback : AndroidJavaProxy // TypeDefIndex: 9803
{
	// Fields
	private Action<AndroidAssetPackInfo> m_Callback; // 0x20
	private string[] m_AssetPacks; // 0x28

	// Methods

	// RVA: 0x2757454 Offset: 0x2753454 VA: 0x2757454
	public void .ctor(Action<AndroidAssetPackInfo> callback, string[] assetPacks) { }

	[Preserve]
	// RVA: 0x27574D8 Offset: 0x27534D8 VA: 0x27574D8
	private void onStatusUpdate(string assetPackName, int assetPackStatus, long assetPackSize, long assetPackBytesDownloaded, int assetPackTransferProgress, int assetPackErrorCode) { }
}


// ===== keywords: Config, Setting, Audio
// Namespace: 
public sealed class AudioSettings.AudioConfigurationChangeHandler : MulticastDelegate // TypeDefIndex: 10775
{
	// Methods

	// RVA: 0x275A19C Offset: 0x275619C VA: 0x275A19C
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x275A228 Offset: 0x2756228 VA: 0x275A228 Slot: 12
	public virtual void Invoke(bool deviceWasChanged) { }
}


// ===== keywords: Event, Season, Pass
// Namespace: 
public class Board_EventSeasonPass : Board // TypeDefIndex: 692
{
	// Fields
	private static Board_EventSeasonPass.EventRewards[] eventRewards; // 0x0
	public static BoardID backBoard; // 0x8
	[SerializeField]
	private Transform parentTabs; // 0x20
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0x28
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0x30
	[SerializeField]
	private TextMeshPro textCoinEvent; // 0x38
	[SerializeField]
	private TextMeshPro[] textIAPPrices; // 0x40
	[SerializeField]
	private TextMeshPro[] textIAPValues; // 0x48
	[SerializeField]
	private TextMeshPro[] textVipPoints; // 0x50
	[SerializeField]
	private TextMeshPro textTimeEvent; // 0x58
	[SerializeField]
	private GameObject panelIAP; // 0x60
	[SerializeField]
	private Transform pointPanelTop; // 0x68
	[SerializeField]
	private Transform pointPanelBot; // 0x70
	[SerializeField]
	private SpriteRenderer panel; // 0x78
	[SerializeField]
	private TextMeshPro textXEvent; // 0x80
	[SerializeField]
	private Animator animTime; // 0x88
	[SerializeField]
	private ScrollView scrollView; // 0x90
	[SerializeField]
	private BoxCollider2D boxBound; // 0x98
	[SerializeField]
	private BoxCollider2D boxContent; // 0xA0
	[SerializeField]
	private Transform parentView; // 0xA8
	private TabEventPass[] allTabs; // 0xB0
	private static int mapUnlock; // 0xC
	private static string KeyStart; // 0x10
	private static string KeyEnd; // 0x18
	private static string KeyToOpen; // 0x20
	[SerializeField]
	private Transform spriteMask; // 0xB8
	private bool isAutoPop; // 0xC0
	[SerializeField]
	private GameObject objectDouble; // 0xC8
	[SerializeField]
	private TextMeshPro textTimeDouble; // 0xD0
	[SerializeField]
	private TextMeshPro textComboPrice; // 0xD8
	[SerializeField]
	private TextMeshPro textComboVipPoint; // 0xE0
	private int[] listIdPurchase; // 0xE8
	public static Action exitEvent; // 0x28
	[SerializeField]
	private Popup_Notices popupInfo; // 0xF0
	[SerializeField]
	private Popup_Notices popupBuyEventCoins; // 0xF8
	[SerializeField]
	private Sprite[] droneCardSprites; // 0x100
	[SerializeField]
	private Sprite[] shipCardSprites; // 0x108
	[SerializeField]
	private Sprite[] allBorderSprites; // 0x110
	[SerializeField]
	private Align align; // 0x118
	[SerializeField]
	private Transform parentRewards; // 0x120
	[SerializeField]
	private GameObject coverRewards; // 0x128
	private Data_Players listPlayers; // 0x130
	private List<Player_Info> allDataPlayers; // 0x138
	private Data_Players listDrones; // 0x140
	private List<Player_Info> allDataDrones; // 0x148
	private int[] iapValues; // 0x150
	[SerializeField]
	private Popup_Notices popupNoNetwork; // 0x158
	private Coroutine checkTimeOut; // 0x160
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x168
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x170
	[SerializeField]
	private GameObject loadingObject; // 0x178
	[SerializeField]
	private Transform[] allPackPoints; // 0x180
	[SerializeField]
	private Transform cointPoint; // 0x188
	[SerializeField]
	private GameObject buttonBuyCombo; // 0x190
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x198
	private int lastProductRewards; // 0x1A0
	[SerializeField]
	private Popup_Exchange popupExchange; // 0x1A8
	private int indexExchange; // 0x1B0

	// Properties
	public static bool IsDoubleCoinEvent { get; }
	public static bool IsFirstTimeEvent { get; set; }
	public static bool IsBuyCombo { get; set; }

	// Methods

	// RVA: 0x128922C Offset: 0x128522C VA: 0x128922C
	public static bool get_IsDoubleCoinEvent() { }

	// RVA: 0x1289384 Offset: 0x1285384 VA: 0x1289384
	public static TimeSpan GetTimeRemain() { }

	// RVA: 0x12894C0 Offset: 0x12854C0 VA: 0x12894C0
	public static bool get_IsFirstTimeEvent() { }

	// RVA: 0x1289538 Offset: 0x1285538 VA: 0x1289538
	public static void set_IsFirstTimeEvent(bool value) { }

	// RVA: 0x12895B8 Offset: 0x12855B8 VA: 0x12895B8
	public static bool IsOpen() { }

	// RVA: 0x1289CFC Offset: 0x1285CFC VA: 0x1289CFC
	public static void SetTimeOpen() { }

	// RVA: 0x1289B74 Offset: 0x1285B74 VA: 0x1289B74
	private static bool IsEventStarted() { }

	// RVA: 0x1289BEC Offset: 0x1285BEC VA: 0x1289BEC
	private static void SetComboStarted(bool isStarted) { }

	// RVA: 0x1289EC8 Offset: 0x1285EC8 VA: 0x1289EC8
	private void Awake() { }

	// RVA: 0x128A04C Offset: 0x128604C VA: 0x128A04C
	private void Start() { }

	// RVA: 0x128AD84 Offset: 0x1286D84 VA: 0x128AD84
	private void SetTimeEvents() { }

	// RVA: 0x128AD88 Offset: 0x1286D88 VA: 0x128AD88
	private void SetAlignPanel() { }

	// RVA: 0x128B3C0 Offset: 0x12873C0 VA: 0x128B3C0
	private void OnEnable() { }

	// RVA: 0x128B7B8 Offset: 0x12877B8 VA: 0x128B7B8
	private IEnumerator IEUpdateEventTime() { }

	// RVA: 0x128B8EC Offset: 0x12878EC VA: 0x128B8EC
	public static bool IsDoubleTime() { }

	// RVA: 0x128B758 Offset: 0x1287758 VA: 0x128B758
	private IEnumerator IECheckDoubleCoins() { }

	// RVA: 0x128B6F8 Offset: 0x12876F8 VA: 0x128B6F8
	private IEnumerator SetPrices() { }

	// RVA: 0x128BCE8 Offset: 0x1287CE8 VA: 0x128BCE8
	private void OnInitialized() { }

	// RVA: 0x128C004 Offset: 0x1288004 VA: 0x128C004
	public void OnPressedButtonBack() { }

	// RVA: 0x128C108 Offset: 0x1288108 VA: 0x128C108 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x128C12C Offset: 0x128812C VA: 0x128C12C Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x128C1A8 Offset: 0x12881A8 VA: 0x128C1A8 Slot: 9
	public override void Escape() { }

	// RVA: 0x128C1AC Offset: 0x12881AC VA: 0x128C1AC
	public static int GetStock(int index) { }

	// RVA: 0x1289E20 Offset: 0x1285E20 VA: 0x1289E20
	public static void SetStock(int index, int stock) { }

	// RVA: 0x128C250 Offset: 0x1288250 VA: 0x128C250
	public void OnPressedButtonInfo() { }

	// RVA: 0x128B818 Offset: 0x1287818 VA: 0x128B818
	public void OnPressedButtonBuyMoreEventCoins() { }

	// RVA: 0x128A064 Offset: 0x1286064 VA: 0x128A064
	private void SetEventRewardTabs() { }

	// RVA: 0x128B044 Offset: 0x1287044 VA: 0x128B044
	private void UpdateBounds() { }

	// RVA: 0x128C4E4 Offset: 0x12884E4 VA: 0x128C4E4
	private void OnBuy(int index, int count) { }

	// RVA: 0x128A8FC Offset: 0x12868FC VA: 0x128A8FC
	private void CacheDatas() { }

	// RVA: 0x128DE68 Offset: 0x1289E68 VA: 0x128DE68
	public void OnPressedButtonBuyMoreCoinEvent(int index) { }

	// RVA: 0x128AFCC Offset: 0x1286FCC VA: 0x128AFCC
	public static bool get_IsBuyCombo() { }

	// RVA: 0x128E1A8 Offset: 0x128A1A8 VA: 0x128E1A8
	public static void set_IsBuyCombo(bool value) { }

	// RVA: 0x128E224 Offset: 0x128A224 VA: 0x128E224
	public void OnPressedButtonBuyCombo() { }

	// RVA: 0x128E500 Offset: 0x128A500 VA: 0x128E500
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x128E148 Offset: 0x128A148 VA: 0x128E148
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x128E58C Offset: 0x128A58C VA: 0x128E58C
	private void OnPurchased(string id, string receipt) { }

	// RVA: 0x128C8E0 Offset: 0x12888E0 VA: 0x128C8E0
	private void SetRewards(int index, int count) { }

	// RVA: 0x128C2FC Offset: 0x12882FC VA: 0x128C2FC
	private void UpdateBtnStatus() { }

	// RVA: 0x128F0F4 Offset: 0x128B0F4 VA: 0x128F0F4
	private void OnClick(int index) { }

	// RVA: 0x128F6C0 Offset: 0x128B6C0 VA: 0x128F6C0
	public void .ctor() { }

	// RVA: 0x128F7E0 Offset: 0x128B7E0 VA: 0x128F7E0
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x12901F8 Offset: 0x128C1F8 VA: 0x12901F8
	private void <OnPressedButtonInfo>b__61_0() { }

	[CompilerGenerated]
	// RVA: 0x1290218 Offset: 0x128C218 VA: 0x1290218
	private void <OnPressedButtonBuyMoreEventCoins>b__63_0() { }

	[CompilerGenerated]
	// RVA: 0x1290238 Offset: 0x128C238 VA: 0x1290238
	private void <CheckLoadingTimeOut>b__90_0() { }

	[CompilerGenerated]
	// RVA: 0x128EC58 Offset: 0x128AC58 VA: 0x128EC58
	private void <SetRewards>g__SaveDataReward|97_0(int _index, int _value, Device _device, int _idDrone = 0) { }

	[CompilerGenerated]
	// RVA: 0x1290258 Offset: 0x128C258 VA: 0x1290258
	private void <OnClick>b__101_0(int count) { }
}


// ===== keywords: Boss, Event, Spin
// Namespace: 
public class BossSpineEventHandler : MonoBehaviour // TypeDefIndex: 114
{
	// Fields
	public string attackEventName; // 0x20
	public string preAttackEffectEventName; // 0x28
	public SkeletonAnimation skeletonAnimation; // 0x30
	public UnityEvent onAttack; // 0x38
	[SerializeField]
	private GameObject chargeEffect; // 0x40

	// Methods

	// RVA: 0x1242028 Offset: 0x123E028 VA: 0x1242028
	private void Start() { }

	// RVA: 0x1242290 Offset: 0x123E290 VA: 0x1242290
	private void HandleEvent(TrackEntry trackEntry, Event e) { }

	// RVA: 0x1242334 Offset: 0x123E334 VA: 0x1242334
	public void .ctor() { }
}


// ===== keywords: UI, Popup, Equip
// Namespace: 
public class Device_Popup_Equip : MonoBehaviour // TypeDefIndex: 586
{
	// Fields
	[SerializeField]
	private Device_Cell[] listEquipSlot; // 0x20
	private Action<int> confirmAction; // 0x28
	private Action exitAction; // 0x30
	private GameObject efxFocusButton; // 0x38

	// Methods

	// RVA: 0x1255008 Offset: 0x1251008 VA: 0x1255008
	public void SetPopup(int currentIndexPlayer, int playerIndex, ref Sprite[] allRankSprites, ref Sprite cellSpriteDefault, ref Dictionary<int, Sprite> allDeviceIcons, Action<int> confirmAction, Action exitAction) { }

	// RVA: 0x12521A4 Offset: 0x124E1A4 VA: 0x12521A4
	public void OnPressedButtonExit() { }

	// RVA: 0x1257F04 Offset: 0x1253F04 VA: 0x1257F04
	public void OnPressedButtonSlot(int index) { }

	// RVA: 0x1257F68 Offset: 0x1253F68 VA: 0x1257F68
	public void .ctor() { }
}


// ===== keywords: Save, Data, Drone
// Namespace: 
public class Drone_Saved_Datas : MonoBehaviour // TypeDefIndex: 292
{
	// Methods

	// RVA: 0x14D9AA8 Offset: 0x14D5AA8 VA: 0x14D9AA8
	public static bool IsDroneUnlocked(int droneIndex) { }

	// RVA: 0x14DB13C Offset: 0x14D713C VA: 0x14DB13C
	public static void SetDroneUnlocked(int droneIndex, PurchaseType type) { }

	// RVA: 0x14DABD4 Offset: 0x14D6BD4 VA: 0x14DABD4
	public static int GetDroneUsed(int slotIndex) { }

	// RVA: 0x14DB228 Offset: 0x14D7228 VA: 0x14DB228
	public static void SetDroneUsed(int slotIndex, int playerIndex) { }

	// RVA: 0x14DB2D0 Offset: 0x14D72D0 VA: 0x14DB2D0
	public static void CheckDoubleIDDrone() { }

	// RVA: 0x14DA8AC Offset: 0x14D68AC VA: 0x14DA8AC
	public static int GetDroneLevel(int droneIndex) { }

	// RVA: 0x14DB35C Offset: 0x14D735C VA: 0x14DB35C
	public static void SetDroneLevel(int droneIndex, int level) { }

	// RVA: 0x14D9F70 Offset: 0x14D5F70 VA: 0x14D9F70
	public static int GetDroneRank(int droneIndex) { }

	// RVA: 0x14DB404 Offset: 0x14D7404 VA: 0x14DB404
	public static void SetDroneRank(int droneIndex, int level) { }

	// RVA: 0x14DB4E0 Offset: 0x14D74E0 VA: 0x14DB4E0
	public static int GetDroneCards(int droneIndex) { }

	// RVA: 0x14DB620 Offset: 0x14D7620 VA: 0x14DB620
	public static void SetDroneCards(int droneIndex, int cards) { }

	// RVA: 0x14DB6C8 Offset: 0x14D76C8 VA: 0x14DB6C8
	public static int GetDroneExp() { }

	// RVA: 0x14DB7D0 Offset: 0x14D77D0 VA: 0x14DB7D0
	public static void SetDroneExp(int exp) { }

	// RVA: 0x14DB840 Offset: 0x14D7840 VA: 0x14DB840
	public void .ctor() { }
}


// ===== keywords: Item, Drop, Event
// Namespace: 
protected internal class Dropdown.DropdownItem : MonoBehaviour, IPointerEnterHandler, IEventSystemHandler, ICancelHandler // TypeDefIndex: 8673
{
	// Fields
	[SerializeField]
	private Text m_Text; // 0x20
	[SerializeField]
	private Image m_Image; // 0x28
	[SerializeField]
	private RectTransform m_RectTransform; // 0x30
	[SerializeField]
	private Toggle m_Toggle; // 0x38

	// Properties
	public Text text { get; set; }
	public Image image { get; set; }
	public RectTransform rectTransform { get; set; }
	public Toggle toggle { get; set; }

	// Methods

	// RVA: 0x2808558 Offset: 0x2804558 VA: 0x2808558
	public Text get_text() { }

	// RVA: 0x2808560 Offset: 0x2804560 VA: 0x2808560
	public void set_text(Text value) { }

	// RVA: 0x2808568 Offset: 0x2804568 VA: 0x2808568
	public Image get_image() { }

	// RVA: 0x2808570 Offset: 0x2804570 VA: 0x2808570
	public void set_image(Image value) { }

	// RVA: 0x2808578 Offset: 0x2804578 VA: 0x2808578
	public RectTransform get_rectTransform() { }

	// RVA: 0x2808580 Offset: 0x2804580 VA: 0x2808580
	public void set_rectTransform(RectTransform value) { }

	// RVA: 0x2808588 Offset: 0x2804588 VA: 0x2808588
	public Toggle get_toggle() { }

	// RVA: 0x2808590 Offset: 0x2804590 VA: 0x2808590
	public void set_toggle(Toggle value) { }

	// RVA: 0x2808598 Offset: 0x2804598 VA: 0x2808598 Slot: 6
	public virtual void OnPointerEnter(PointerEventData eventData) { }

	// RVA: 0x2808614 Offset: 0x2804614 VA: 0x2808614 Slot: 7
	public virtual void OnCancel(BaseEventData eventData) { }

	// RVA: 0x28086C0 Offset: 0x28046C0 VA: 0x28086C0
	public void .ctor() { }
}


// ===== keywords: Tech, Firebase, Stat
// Namespace: 
internal sealed class FirebaseAuth.StateChangedDelegate : MulticastDelegate // TypeDefIndex: 10449
{
	// Methods

	// RVA: 0x16615F8 Offset: 0x165D5F8 VA: 0x16615F8
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x1662E6C Offset: 0x165EE6C VA: 0x1662E6C Slot: 12
	public virtual void Invoke(IntPtr authCPtr) { }
}


// ===== keywords: Player, Save, Data
// Namespace: 
public class Player_Device_Saved_Datas : MonoBehaviour // TypeDefIndex: 318
{
	// Methods

	// RVA: 0x14E628C Offset: 0x14E228C VA: 0x14E628C
	public static int[] GetPlayerDevices(int playerIndex) { }

	// RVA: 0x14E64A4 Offset: 0x14E24A4 VA: 0x14E64A4
	public static void SetPlayerDevices(int playerIndex, int[] devices) { }

	// RVA: 0x14E6660 Offset: 0x14E2660 VA: 0x14E6660
	public void .ctor() { }
}


// ===== keywords: Player, Save, Data
// Namespace: 
public class Player_Saved_Datas : MonoBehaviour // TypeDefIndex: 319
{
	// Fields
	public static int[] MaxLevelPerRanks; // 0x0
	public static int[] CardUpgrades; // 0x8
	public static int[] StartRanks; // 0x10

	// Properties
	public static int LastShipUnlocked { get; set; }
	public static int IndexPlayerOffer { get; set; }
	public static int IndexPlayerRankOffer { get; set; }
	public static int MAX_RANK_INDEX { get; }

	// Methods

	// RVA: 0x14E6668 Offset: 0x14E2668 VA: 0x14E6668
	public static void CheckOffer() { }

	// RVA: 0x14E6F58 Offset: 0x14E2F58 VA: 0x14E6F58
	public static int get_LastShipUnlocked() { }

	// RVA: 0x14E7030 Offset: 0x14E3030 VA: 0x14E7030
	public static void set_LastShipUnlocked(int value) { }

	// RVA: 0x14E6FC4 Offset: 0x14E2FC4 VA: 0x14E6FC4
	public static int get_IndexPlayerOffer() { }

	// RVA: 0x14E6C2C Offset: 0x14E2C2C VA: 0x14E6C2C
	public static void set_IndexPlayerOffer(int value) { }

	// RVA: 0x14E7230 Offset: 0x14E3230 VA: 0x14E7230
	public static int get_IndexPlayerRankOffer() { }

	// RVA: 0x14E6C9C Offset: 0x14E2C9C VA: 0x14E6C9C
	public static void set_IndexPlayerRankOffer(int value) { }

	// RVA: 0x14E24FC Offset: 0x14DE4FC VA: 0x14E24FC
	public static bool IsPlayerUnlocked(int playerIndex) { }

	// RVA: 0x14E729C Offset: 0x14E329C VA: 0x14E729C
	public static void SetPlayerUnlocked(int playerIndex, PurchaseType type) { }

	// RVA: 0x14E70A0 Offset: 0x14E30A0 VA: 0x14E70A0
	public static int GetPlayerUsed(int slotIndex) { }

	// RVA: 0x14E73BC Offset: 0x14E33BC VA: 0x14E73BC
	public static void SetPlayerUsed(int slotIndex, int playerIndex) { }

	// RVA: 0x14E3B20 Offset: 0x14DFB20 VA: 0x14E3B20
	public static int GetPlayerLevel(int _playerIndex) { }

	// RVA: 0x14E7464 Offset: 0x14E3464 VA: 0x14E7464
	public static void CheckDoubleIDShip() { }

	// RVA: 0x14E7600 Offset: 0x14E3600 VA: 0x14E7600
	public static void SetPlayerLevel(int _playerIndex, int _level) { }

	// RVA: 0x14E6D74 Offset: 0x14E2D74 VA: 0x14E6D74
	public static int GetPlayerRank(int _playerIndex) { }

	// RVA: 0x14E76A8 Offset: 0x14E36A8 VA: 0x14E76A8
	public static void SetPlayerRank(int _playerIndex, int _level) { }

	// RVA: 0x14E77FC Offset: 0x14E37FC VA: 0x14E77FC
	public static int GetPlayerDefaultSkin(int _playerIndex) { }

	// RVA: 0x14E78A0 Offset: 0x14E38A0 VA: 0x14E78A0
	public static void SetPlayerDefaultSkin(int _playerIndex, int _level) { }

	// RVA: 0x14E7948 Offset: 0x14E3948 VA: 0x14E7948
	public static int GetPlayerCards(int _playerIndex) { }

	// RVA: 0x14E7A88 Offset: 0x14E3A88 VA: 0x14E7A88
	public static void SetPlayerCards(int _playerIndex, int _cards) { }

	// RVA: 0x14E6D0C Offset: 0x14E2D0C VA: 0x14E6D0C
	public static int get_MAX_RANK_INDEX() { }

	// RVA: 0x14E7B30 Offset: 0x14E3B30 VA: 0x14E7B30
	public static int GetCostCraftPlayer(int _playerIndex) { }

	// RVA: 0x14E7CC4 Offset: 0x14E3CC4 VA: 0x14E7CC4
	public static int GetUpgadeCostCoins(int _index, int lv) { }

	// RVA: 0x14E7D2C Offset: 0x14E3D2C VA: 0x14E7D2C
	public static int GetUpgradeCostGems(int _index, int lv) { }

	// RVA: 0x14E7D94 Offset: 0x14E3D94 VA: 0x14E7D94
	public static int GetTechStatPoints(int statIndex) { }

	// RVA: 0x14E7E38 Offset: 0x14E3E38 VA: 0x14E7E38
	public static void SetTechStatPoints(int index, int point) { }

	// RVA: 0x14E7EE0 Offset: 0x14E3EE0 VA: 0x14E7EE0
	public static int GetTechStatLevel(int statIndex) { }

	// RVA: 0x14E7F84 Offset: 0x14E3F84 VA: 0x14E7F84
	public static void SetTechStatLevel(int index, int lv) { }

	// RVA: 0x14E802C Offset: 0x14E402C VA: 0x14E802C
	public static int GetTechLabLevel() { }

	// RVA: 0x14E8098 Offset: 0x14E4098 VA: 0x14E8098
	public static void SetTechLabLevel(int lv) { }

	// RVA: 0x14E8108 Offset: 0x14E4108 VA: 0x14E8108
	public void .ctor() { }

	// RVA: 0x14E8110 Offset: 0x14E4110 VA: 0x14E8110
	private static void .cctor() { }
}


// ===== keywords: Gem, Mission, Popup
// Namespace: 
public class Popup_ChangeMissions : Popup_Notices // TypeDefIndex: 492
{
	// Fields
	public SpriteRenderer boxRenderer; // 0x58
	public SpriteRenderer iconRenderer; // 0x60
	public TextMeshPro textPrice; // 0x68

	// Methods

	// RVA: 0x15DB3E0 Offset: 0x15D73E0 VA: 0x15DB3E0
	public void .ctor() { }
}


// ===== keywords: Level, Popup, Event
// Namespace: 
public class Popup_EventLevelUp : MonoBehaviour // TypeDefIndex: 524
{
	// Fields
	[SerializeField]
	private TextMeshPro textLevel; // 0x20
	[SerializeField]
	private SpriteRenderer[] allIconAbility; // 0x28
	[SerializeField]
	private Sprite[] allAbilitySprites; // 0x30
	[SerializeField]
	private AlignCenter alignCenter; // 0x38
	[SerializeField]
	private bool dropEvent; // 0x40
	[SerializeField]
	private Sprite defaultSprite; // 0x48
	[SerializeField]
	private GameObject parentLevel0; // 0x50
	[SerializeField]
	private GameObject parentLevels; // 0x58

	// Methods

	// RVA: 0x15EA988 Offset: 0x15E6988 VA: 0x15EA988
	public void SetPopup() { }

	// RVA: 0x15EACD4 Offset: 0x15E6CD4 VA: 0x15EACD4
	public void .ctor() { }
}


// ===== keywords: Reward, PvP, Popup
// Namespace: 
public class Popup_PVPRewards : MonoBehaviour // TypeDefIndex: 874
{
	// Fields
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0x20
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0x28
	[SerializeField]
	private BoxCollider2D boxBound; // 0x30
	[SerializeField]
	private BoxCollider2D boxContent; // 0x38
	[SerializeField]
	private Transform parentView; // 0x40
	[SerializeField]
	private Transform btnBack; // 0x48
	[SerializeField]
	private Transform parentRewards; // 0x50
	[SerializeField]
	private Align align; // 0x58
	public Action onExit; // 0x60

	// Methods

	// RVA: 0x12F5338 Offset: 0x12F1338 VA: 0x12F5338
	private void OnEnable() { }

	// RVA: 0x12F56D4 Offset: 0x12F16D4 VA: 0x12F56D4
	private void SetRewards() { }

	// RVA: 0x12F61AC Offset: 0x12F21AC VA: 0x12F61AC
	private IEnumerator IEShow() { }

	// RVA: 0x12F6234 Offset: 0x12F2234 VA: 0x12F6234
	public static bool IsHasRewards() { }

	// RVA: 0x12F6008 Offset: 0x12F2008 VA: 0x12F6008
	private static bool IsCollected(int index) { }

	// RVA: 0x12F6404 Offset: 0x12F2404 VA: 0x12F6404
	public void OnExit() { }

	// RVA: 0x12F6448 Offset: 0x12F2448 VA: 0x12F6448
	private void OnClickCollect(PVP_TabReward tab) { }

	// RVA: 0x12F68C0 Offset: 0x12F28C0 VA: 0x12F68C0
	private IEnumerator TryCollect(Action callback) { }

	// RVA: 0x12F6948 Offset: 0x12F2948 VA: 0x12F6948
	public void .ctor() { }
}


// ===== keywords: Shop, PvP, Popup
// Namespace: 
public class Popup_PVPShopExchange : MonoBehaviour // TypeDefIndex: 875
{
	// Fields
	[SerializeField]
	private TextMeshPro textHeader; // 0x20
	[SerializeField]
	private TextMeshPro textStock; // 0x28
	[SerializeField]
	private TextMeshPro textCost; // 0x30
	[SerializeField]
	private TextMeshPro textCoinEvent; // 0x38
	[SerializeField]
	private SpriteRenderer btnIcon; // 0x40
	[SerializeField]
	private Slider slider; // 0x48
	public Action<int> onExit; // 0x50
	private int count; // 0x58
	private int maxStock; // 0x5C
	private Board_EventSeasonPass.EventRewards rewards; // 0x60
	[SerializeField]
	private Box_Rewards boxReward; // 0x68

	// Methods

	// RVA: 0x12F7694 Offset: 0x12F3694 VA: 0x12F7694
	private void OnChange(float amount) { }

	// RVA: 0x12F7A14 Offset: 0x12F3A14 VA: 0x12F7A14
	public void SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward, Action<int> exit) { }

	// RVA: 0x12F7E58 Offset: 0x12F3E58 VA: 0x12F7E58
	private void SetEventRewardTabs() { }

	// RVA: 0x12F8298 Offset: 0x12F4298 VA: 0x12F8298
	public void OnPressedButtonExit() { }

	// RVA: 0x12F82E0 Offset: 0x12F42E0 VA: 0x12F82E0
	public void OnPressedButtonBuy() { }

	// RVA: 0x12F8398 Offset: 0x12F4398 VA: 0x12F8398
	public void OnPressedButtonMinus() { }

	// RVA: 0x12F83D0 Offset: 0x12F43D0 VA: 0x12F83D0
	public void OnPressedButtonAdd() { }

	// RVA: 0x12F840C Offset: 0x12F440C VA: 0x12F840C
	public void .ctor() { }
}


// ===== keywords: Reward, Daily, Popup
// Namespace: 
public class Popup_PremiumDailyRewards : MonoBehaviour // TypeDefIndex: 1052
{
	// Fields
	[SerializeField]
	private TextMeshPro textHeader; // 0x20
	[SerializeField]
	private TextMeshPro textPremiumTimer; // 0x28
	[SerializeField]
	private TextMeshPro textBonusValue0; // 0x30
	[SerializeField]
	private TextMeshPro textBonusValue1; // 0x38
	[SerializeField]
	private TextMeshPro textBonusValue2; // 0x40
	[SerializeField]
	private TextMeshPro textInfo0; // 0x48
	[SerializeField]
	private TextMeshPro textInfo1; // 0x50
	[SerializeField]
	private TextMeshPro textInfo2; // 0x58
	[SerializeField]
	private TextMeshPro textInfo3; // 0x60
	[SerializeField]
	private Animator anim; // 0x68
	[SerializeField]
	private bool trial; // 0x70
	public int dayTrial; // 0x74
	protected bool appear; // 0x78
	private bool claimed; // 0x79
	public Action exitEvent; // 0x80
	[SerializeField]
	private GameObject loadingObject; // 0x88
	[SerializeField]
	private Transform parentRewards; // 0x90
	[SerializeField]
	private GameObject coverRewards; // 0x98
	[SerializeField]
	private GameObject popupPrefabs; // 0xA0

	// Methods

	// RVA: 0x135903C Offset: 0x135503C VA: 0x135903C
	private void OnEnable() { }

	// RVA: 0x13591A8 Offset: 0x13551A8 VA: 0x13591A8
	public void SetDayTrial(int days) { }

	// RVA: 0x13592A4 Offset: 0x13552A4 VA: 0x13592A4
	public void SetTextTrial(int day) { }

	// RVA: 0x135937C Offset: 0x135537C VA: 0x135937C
	private void Start() { }

	// RVA: 0x135982C Offset: 0x135582C VA: 0x135982C
	public void SetPopup(Action _exitCallback) { }

	// RVA: 0x1359854 Offset: 0x1355854 VA: 0x1359854
	public void OnPressedButtonClaim() { }

	// RVA: 0x135A3E8 Offset: 0x13563E8 VA: 0x135A3E8
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x135A450 Offset: 0x1356450 VA: 0x135A450
	private IEnumerator DelayExitClaimRewards() { }

	// RVA: 0x1359148 Offset: 0x1355148 VA: 0x1359148
	private IEnumerator UpdateTimer() { }

	// RVA: 0x1359920 Offset: 0x1355920 VA: 0x1359920
	private void ClaimRewards() { }

	// RVA: 0x135A500 Offset: 0x1356500 VA: 0x135A500
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x135A99C Offset: 0x135699C VA: 0x135A99C
	private void Appear() { }

	// RVA: 0x135A9A8 Offset: 0x13569A8 VA: 0x135A9A8
	private void Hide() { }

	// RVA: 0x135A9EC Offset: 0x13569EC VA: 0x135A9EC
	public void .ctor() { }
}


// ===== keywords: UI, Popup, Event
// Namespace: 
public class Popup_QuitEvent : Popup_Notices // TypeDefIndex: 525
{
	// Fields
	[SerializeField]
	private AbilityEventTab currentLevel; // 0x58
	[SerializeField]
	private AbilityEventTab nextLevel; // 0x60
	[SerializeField]
	private Sprite[] allAbilitySprites; // 0x68
	[SerializeField]
	private Sprite defaultSprite; // 0x70
	[SerializeField]
	private GameObject[] allHeaders; // 0x78
	private bool isNoIcon; // 0x80

	// Methods

	// RVA: 0x15EACDC Offset: 0x15E6CDC VA: 0x15EACDC
	private void Start() { }

	// RVA: 0x15EB27C Offset: 0x15E727C VA: 0x15EB27C
	public void .ctor() { }
}


// ===== keywords: Reward, Popup, Season
// Namespace: 
public class Popup_SeasonRewards : Popup // TypeDefIndex: 876
{
	// Fields
	[SerializeField]
	private TextMeshPro textHeader; // 0x30
	[SerializeField]
	private TextMeshPro textInfo; // 0x38
	[SerializeField]
	private Transform parentRewards; // 0x40
	[SerializeField]
	private GameObject buttonOk; // 0x48
	[SerializeField]
	private GridLayoutManager gridLayout; // 0x50

	// Methods

	// RVA: 0x12F8414 Offset: 0x12F4414 VA: 0x12F8414
	public void Setup(List<Gift> gifts, string header, string info) { }

	// RVA: 0x12F90F8 Offset: 0x12F50F8 VA: 0x12F90F8
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x12F9594 Offset: 0x12F5594 VA: 0x12F9594
	public void OnClaim() { }

	// RVA: 0x12F95A0 Offset: 0x12F55A0 VA: 0x12F95A0
	public void .ctor() { }
}


// ===== keywords: Mission, Battle, Pass
// Namespace: 
public class Tab_BattlePassMission : MonoBehaviour // TypeDefIndex: 494
{
	// Fields
	public int Index; // 0x20
	public int Reward; // 0x24
	public SpriteRenderer tabBg; // 0x28
	public SpriteRenderer boxRend; // 0x30
	public SpriteRenderer iconRend; // 0x38
	public TextMeshPro textName; // 0x40
	public TextMeshPro textInfo; // 0x48
	public TextMeshPro textNumber; // 0x50
	public TextMeshPro textProcess; // 0x58
	public TextMeshPro textUnlock; // 0x60
	public SpriteRenderer processBar; // 0x68
	public SpriteRenderer processBg; // 0x70
	public GameObject blackCover; // 0x78
	public GameObject lockObject; // 0x80
	public GameObject doneObject; // 0x88
	public GameObject buttonCollect; // 0x90
	public GameObject buttonGo; // 0x98
	public GameObject buttonUnlock; // 0xA0
	public GameObject buttonChange; // 0xA8
	public Action<int, int> onGo; // 0xB0
	public Action<int, int> onClaim; // 0xB8
	public Action<int, int> onUnlock; // 0xC0
	public Action<int, int, Sprite, Sprite> onChange; // 0xC8

	// Methods

	// RVA: 0x15DB498 Offset: 0x15D7498 VA: 0x15DB498
	public void OnPressedButtonClaim() { }

	// RVA: 0x15DB4B8 Offset: 0x15D74B8 VA: 0x15DB4B8
	public void OnPressedButtonGo() { }

	// RVA: 0x15DB4D8 Offset: 0x15D74D8 VA: 0x15DB4D8
	public void OnPressedButtonUnlock() { }

	// RVA: 0x15DB4F8 Offset: 0x15D74F8 VA: 0x15DB4F8
	public void OnPressedButtonChange() { }

	// RVA: 0x15DB580 Offset: 0x15D7580 VA: 0x15DB580
	public void .ctor() { }
}


// ===== keywords: Data, Firebase, Event
// Namespace: Firebase.Database
public sealed class ChildChangedEventArgs : EventArgs // TypeDefIndex: 9979
{
	// Fields
	[CompilerGenerated]
	private DataSnapshot <Snapshot>k__BackingField; // 0x10
	[CompilerGenerated]
	private DatabaseError <DatabaseError>k__BackingField; // 0x18
	[CompilerGenerated]
	private string <PreviousChildName>k__BackingField; // 0x20

	// Properties
	public DataSnapshot Snapshot { get; set; }
	private DatabaseError DatabaseError { set; }
	private string PreviousChildName { set; }

	// Methods

	// RVA: 0x1664F54 Offset: 0x1660F54 VA: 0x1664F54
	internal void .ctor(DataSnapshot snapshot, string previousChildName) { }

	// RVA: 0x1664FC8 Offset: 0x1660FC8 VA: 0x1664FC8
	internal void .ctor(DatabaseError error) { }

	[CompilerGenerated]
	// RVA: 0x1665034 Offset: 0x1661034 VA: 0x1665034
	public DataSnapshot get_Snapshot() { }

	[CompilerGenerated]
	// RVA: 0x166503C Offset: 0x166103C VA: 0x166503C
	private void set_Snapshot(DataSnapshot value) { }

	[CompilerGenerated]
	// RVA: 0x1665044 Offset: 0x1661044 VA: 0x1665044
	private void set_DatabaseError(DatabaseError value) { }

	[CompilerGenerated]
	// RVA: 0x166504C Offset: 0x166104C VA: 0x166504C
	private void set_PreviousChildName(string value) { }
}


// ===== keywords: Data, Firebase, Event
// Namespace: Firebase.Database
public sealed class ValueChangedEventArgs : EventArgs // TypeDefIndex: 9993
{
	// Fields
	[CompilerGenerated]
	private DataSnapshot <Snapshot>k__BackingField; // 0x10
	[CompilerGenerated]
	private DatabaseError <DatabaseError>k__BackingField; // 0x18

	// Properties
	public DataSnapshot Snapshot { get; set; }
	private DatabaseError DatabaseError { set; }

	// Methods

	// RVA: 0x166ABDC Offset: 0x1666BDC VA: 0x166ABDC
	internal void .ctor(DataSnapshot snapshot) { }

	// RVA: 0x166AC48 Offset: 0x1666C48 VA: 0x166AC48
	internal void .ctor(DatabaseError error) { }

	[CompilerGenerated]
	// RVA: 0x166ACB4 Offset: 0x1666CB4 VA: 0x166ACB4
	public DataSnapshot get_Snapshot() { }

	[CompilerGenerated]
	// RVA: 0x166ACBC Offset: 0x1666CBC VA: 0x166ACBC
	private void set_Snapshot(DataSnapshot value) { }

	[CompilerGenerated]
	// RVA: 0x166ACC4 Offset: 0x1666CC4 VA: 0x166ACC4
	private void set_DatabaseError(DatabaseError value) { }
}


// ===== keywords: Config, IAP, Firebase
// Namespace: Firebase.Platform.Default
internal class AppConfigExtensions : IAppConfigExtensions // TypeDefIndex: 10560
{
	// Fields
	private static readonly Uri DefaultUpdateUrl; // 0x0
	private static readonly string Default; // 0x8
	private static readonly object Sync; // 0x10
	private static AppConfigExtensions _instance; // 0x18
	private static readonly Dictionary<int, Dictionary<string, string>> SStringState; // 0x20

	// Properties
	public static IAppConfigExtensions Instance { get; }

	// Methods

	// RVA: 0x167AC2C Offset: 0x1676C2C VA: 0x167AC2C
	public static IAppConfigExtensions get_Instance() { }

	// RVA: 0x167D4C4 Offset: 0x16794C4 VA: 0x167D4C4
	protected void .ctor() { }

	// RVA: 0x167D4CC Offset: 0x16794CC VA: 0x167D4CC Slot: 5
	public virtual string GetDatabaseUrl(IFirebaseAppPlatform app) { }

	// RVA: -1 Offset: -1
	private static T GetState<T>(IFirebaseAppPlatform app, int state, Dictionary<int, Dictionary<string, T>> store) { }
	/* GenericInstMethod :
	|
	|-RVA: 0x17894C8 Offset: 0x17854C8 VA: 0x17894C8
	|-AppConfigExtensions.GetState<object>
	|
	|-RVA: 0x1789824 Offset: 0x1785824 VA: 0x1789824
	|-AppConfigExtensions.GetState<__Il2CppFullySharedGenericType>
	*/

	// RVA: 0x167D638 Offset: 0x1679638 VA: 0x167D638
	private static void .cctor() { }
}


// ===== keywords: Player, Item, PvP
// Namespace: GamePVP
public class PlayerItemPVPEndGame : MonoBehaviour // TypeDefIndex: 1575
{
	// Fields
	[SerializeField]
	private TextMeshPro scoreText; // 0x20
	[SerializeField]
	private TextMeshPro playerNameText; // 0x28
	[SerializeField]
	private TextMeshPro rankText; // 0x30
	[SerializeField]
	private GameObject mineObj; // 0x38
	[SerializeField]
	private GameObject deadObj; // 0x40
	private string[] texts; // 0x48

	// Methods

	// RVA: 0x1445CF0 Offset: 0x1441CF0 VA: 0x1445CF0
	public void Setup(PlayerScore playerScore, int rank) { }

	// RVA: 0x1445E78 Offset: 0x1441E78 VA: 0x1445E78
	public void .ctor() { }
}


// ===== keywords: Player, Item, PvP
// Namespace: PVP
public class PlayerItemPVP : MonoBehaviour // TypeDefIndex: 1595
{
	// Fields
	[SerializeField]
	private TextMeshPro scoreText; // 0x20
	[SerializeField]
	private TextMeshPro playerNameText; // 0x28
	[SerializeField]
	private TextMeshPro rankText; // 0x30
	[SerializeField]
	private TextMeshPro messageText; // 0x38
	[SerializeField]
	private GameObject mineObj; // 0x40
	[SerializeField]
	private GameObject deadObj; // 0x48
	[SerializeField]
	private GameObject zzzObj; // 0x50
	[SerializeField]
	private GameObject[] allMyHealthObj; // 0x58
	[SerializeField]
	private SpriteRenderer bgMessage; // 0x60
	[SerializeField]
	private Animator anim; // 0x68
	[SerializeField]
	private Animator messageAnim; // 0x70
	private string[] texts; // 0x78
	public string id; // 0x80

	// Methods

	// RVA: 0x144C2A8 Offset: 0x14482A8 VA: 0x144C2A8 Slot: 4
	public virtual void Setup(PlayerScore playerScore, int rank, bool isMine) { }

	// RVA: 0x144C470 Offset: 0x1448470 VA: 0x144C470
	public void ShowMessage(string message) { }

	// RVA: 0x144C52C Offset: 0x144852C VA: 0x144C52C
	private void Awake() { }

	// RVA: 0x144C57C Offset: 0x144857C VA: 0x144C57C
	public void Show() { }

	// RVA: 0x144C5D0 Offset: 0x14485D0 VA: 0x144C5D0
	public void .ctor() { }
}


// ===== keywords: Enemy, Boss, Event
// Namespace: SpaceShooter.EnemySystem
public class Boss3_FootEvent : MonoBehaviour // TypeDefIndex: 2109
{
	// Fields
	[SerializeField]
	private Transform[] posFoot1; // 0x20
	[SerializeField]
	private Transform[] posFoot2; // 0x28
	public Action onStartMap; // 0x30
	public Action onStartWalk; // 0x38
	public Action onDefeat; // 0x40

	// Methods

	// RVA: 0x154096C Offset: 0x153C96C VA: 0x154096C
	private void OnFoot1() { }

	// RVA: 0x1540AC4 Offset: 0x153CAC4 VA: 0x1540AC4
	private void OnFoot2() { }

	// RVA: 0x1540C1C Offset: 0x153CC1C VA: 0x1540C1C
	private void OnFootAll() { }

	// RVA: 0x1540C78 Offset: 0x153CC78 VA: 0x1540C78
	private void OnStopMap() { }

	// RVA: 0x1540CCC Offset: 0x153CCCC VA: 0x1540CCC
	private void OnStartMap() { }

	// RVA: 0x1540D48 Offset: 0x153CD48 VA: 0x1540D48
	private void OnStartWalk() { }

	// RVA: 0x1540D64 Offset: 0x153CD64 VA: 0x1540D64
	private void OnDefeat() { }

	// RVA: 0x1540D80 Offset: 0x153CD80 VA: 0x1540D80
	private void OnBoomBoom() { }

	// RVA: 0x1540D90 Offset: 0x153CD90 VA: 0x1540D90
	public void .ctor() { }
}


// ===== keywords: Enemy, Boss, Spawn
// Namespace: SpaceShooter.EnemySystem
public class Boss8_Spawner : MonoBehaviour // TypeDefIndex: 2169
{
	// Fields
	[SerializeField]
	private Rotate rotateScript; // 0x20
	[SerializeField]
	private bool auto; // 0x28
	[SerializeField]
	private Transform root; // 0x30
	[SerializeField]
	private Transform parentRotate; // 0x38
	[SerializeField]
	private int idMeteor; // 0x40
	[SerializeField]
	private int number; // 0x44
	[SerializeField]
	private float startAngle; // 0x48
	[SerializeField]
	private float deltaAngle; // 0x4C
	[SerializeField]
	private float radiusMin; // 0x50
	[SerializeField]
	private float radiusMax; // 0x54
	[SerializeField]
	private Dictionary<GameObject, int> allMeteors; // 0x58
	[SerializeField]
	private LayerMask targetLayer; // 0x60

	// Methods

	// RVA: 0x1551800 Offset: 0x154D800 VA: 0x1551800
	private void Start() { }

	// RVA: 0x154E548 Offset: 0x154A548 VA: 0x154E548
	public void StopSpawn() { }

	// RVA: 0x154EE30 Offset: 0x154AE30 VA: 0x154EE30
	public void FlashAttack(bool _firstTime = False) { }

	// RVA: 0x1551830 Offset: 0x154D830 VA: 0x1551830
	private IEnumerator Spawn() { }

	// RVA: 0x1550EF8 Offset: 0x154CEF8 VA: 0x1550EF8
	public void AttackOneTurn() { }

	// RVA: 0x1551920 Offset: 0x154D920 VA: 0x1551920
	private IEnumerator MeteorAttack() { }

	// RVA: 0x15519A8 Offset: 0x154D9A8 VA: 0x15519A8
	private IEnumerator MeteorAttackOld() { }

	// RVA: 0x1551890 Offset: 0x154D890 VA: 0x1551890
	private Vector3 GetRotation(Transform _objMeteor, Transform _player) { }

	// RVA: 0x1551A30 Offset: 0x154DA30 VA: 0x1551A30
	private Vector3 GetRotation(Vector3 _v1, Vector3 _v2) { }

	// RVA: 0x1551B80 Offset: 0x154DB80 VA: 0x1551B80
	private IEnumerator AttackPlayer(Transform _objMeteor, Transform _player) { }

	// RVA: 0x1551DB0 Offset: 0x154DDB0 VA: 0x1551DB0
	private void OnMeteorDestroyed(GameObject obj) { }

	// RVA: 0x1551E8C Offset: 0x154DE8C VA: 0x1551E8C
	private IEnumerator MoveObject(Transform _moveObj, Vector3 _targetPos, bool _setParent = True, Action<Transform> _callback) { }

	// RVA: 0x1551F60 Offset: 0x154DF60 VA: 0x1551F60 Slot: 4
	protected virtual void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1551F64 Offset: 0x154DF64 VA: 0x1551F64 Slot: 5
	protected virtual void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1552138 Offset: 0x154E138 VA: 0x1552138 Slot: 6
	protected virtual void OnFlashDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x155213C Offset: 0x154E13C VA: 0x155213C Slot: 7
	protected virtual void OnFlashCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1552310 Offset: 0x154E310 VA: 0x1552310
	public void .ctor() { }
}


// ===== keywords: Enemy, Boss, Laser
// Namespace: SpaceShooter.EnemySystem
public class BossLaser_Attack : MonoBehaviour // TypeDefIndex: 2188
{
	// Fields
	[SerializeField]
	private Transform parentBarrels; // 0x20
	[SerializeField]
	private int idBlt; // 0x28
	[SerializeField]
	private float bltSpeed; // 0x2C
	[SerializeField]
	private float bulletLifetime; // 0x30
	[SerializeField]
	private LayerMask targetLayer; // 0x34
	[SerializeField]
	private bool fixedAngle; // 0x38
	[SerializeField]
	private float angleFixed; // 0x3C
	[SerializeField]
	protected float damage; // 0x40
	private GameObject bulletObject; // 0x48
	private Vector3 position; // 0x50
	private Damager damager; // 0x60
	private Vector2 point; // 0x68
	[SerializeField]
	private Vector2 size; // 0x70
	private Collider2D resuftColliders; // 0x78
	[SerializeField]
	private Transform plasmaPoint; // 0x80
	private bool laserActived; // 0x88

	// Methods

	// RVA: 0x1559E84 Offset: 0x1555E84 VA: 0x1559E84
	private void Start() { }

	// RVA: 0x1559F24 Offset: 0x1555F24 VA: 0x1559F24
	public void AttackPlasmaOneShot() { }

	// RVA: 0x155A21C Offset: 0x155621C VA: 0x155A21C
	public void CheckLaserStart() { }

	// RVA: 0x155A228 Offset: 0x1556228 VA: 0x155A228
	public void CheckLaserEnded() { }

	// RVA: 0x155A230 Offset: 0x1556230 VA: 0x155A230
	private void FixedUpdate() { }

	// RVA: 0x155A430 Offset: 0x1556430 VA: 0x155A430
	private void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x155A434 Offset: 0x1556434 VA: 0x155A434
	private void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x155A234 Offset: 0x1556234 VA: 0x155A234
	private void CheckLaserCollision() { }

	// RVA: 0x155A574 Offset: 0x1556574 VA: 0x155A574
	protected void OnLaserCollided(Collider2D obj) { }

	// RVA: 0x155A6E4 Offset: 0x15566E4 VA: 0x155A6E4
	private void OnDrawGizmos() { }

	// RVA: 0x155A998 Offset: 0x1556998 VA: 0x155A998
	public void .ctor() { }
}


// ===== keywords: Enemy, Laser, Drone
// Namespace: SpaceShooter.EnemySystem
public class Drone_Laser : MonoBehaviour // TypeDefIndex: 2368
{
	// Fields
	[SerializeField]
	private int idDrone; // 0x20
	private Damager damager; // 0x28
	private Vector2 point; // 0x30
	[SerializeField]
	private Vector2 size; // 0x38
	private Collider2D[] resuftColliders; // 0x40
	[SerializeField]
	private LayerMask targetLayer; // 0x48

	// Methods

	// RVA: 0x1588808 Offset: 0x1584808 VA: 0x1588808
	private void OnEnable() { }

	// RVA: 0x15888A8 Offset: 0x15848A8 VA: 0x15888A8
	private void Update() { }

	// RVA: 0x15888AC Offset: 0x15848AC VA: 0x15888AC
	private void CheckLaserCollision() { }

	// RVA: 0x1588B0C Offset: 0x1584B0C VA: 0x1588B0C
	protected void OnLaserCollided(Collider2D obj) { }

	// RVA: 0x1588D74 Offset: 0x1584D74 VA: 0x1588D74
	private void OnDrawGizmos() { }

	// RVA: 0x1589054 Offset: 0x1585054 VA: 0x1589054
	public void .ctor() { }
}


// ===== keywords: Data, Mode, Spin
// Namespace: Spine.Unity
public class BlendModeMaterialsAsset : SkeletonDataModifierAsset // TypeDefIndex: 8643
{
	// Fields
	public Material multiplyMaterialTemplate; // 0x18
	public Material screenMaterialTemplate; // 0x20
	public Material additiveMaterialTemplate; // 0x28
	public bool applyAdditiveMaterial; // 0x30

	// Methods

	// RVA: 0x224BBE4 Offset: 0x2247BE4 VA: 0x224BBE4 Slot: 4
	public override void Apply(SkeletonData skeletonData) { }

	// RVA: 0x224BBFC Offset: 0x2247BFC VA: 0x224BBFC
	public static void ApplyMaterials(SkeletonData skeletonData, Material multiplyTemplate, Material screenTemplate, Material additiveTemplate, bool includeAdditiveSlots) { }

	// RVA: 0x224C434 Offset: 0x2248434 VA: 0x224C434
	public void .ctor() { }
}


// ===== keywords: Data, Event, Spin
// Namespace: Spine.Unity
public class EventDataReferenceAsset : ScriptableObject // TypeDefIndex: 8575
{
	// Fields
	private const bool QuietSkeletonData = True;
	[SerializeField]
	protected SkeletonDataAsset skeletonDataAsset; // 0x18
	[SerializeField]
	protected string eventName; // 0x20
	private EventData eventData; // 0x28

	// Properties
	public EventData EventData { get; }

	// Methods

	// RVA: 0x222D9C8 Offset: 0x22299C8 VA: 0x222D9C8
	public EventData get_EventData() { }

	// RVA: 0x222D9EC Offset: 0x22299EC VA: 0x222D9EC
	public void Initialize() { }

	// RVA: 0x222DB6C Offset: 0x2229B6C VA: 0x222DB6C
	public static EventData op_Implicit(EventDataReferenceAsset asset) { }

	// RVA: 0x222DB98 Offset: 0x2229B98 VA: 0x222DB98
	public void .ctor() { }
}


// ===== keywords: Load, Ads, Stat
// Namespace: System.Linq.Expressions.Interpreter
internal sealed class LoadStaticFieldInstruction : FieldInstruction // TypeDefIndex: 6805
{
	// Properties
	public override string InstructionName { get; }
	public override int ProducedStack { get; }

	// Methods

	// RVA: 0x2289F98 Offset: 0x2285F98 VA: 0x2289F98
	public void .ctor(FieldInfo field) { }

	// RVA: 0x2289FC0 Offset: 0x2285FC0 VA: 0x2289FC0 Slot: 9
	public override string get_InstructionName() { }

	// RVA: 0x228A000 Offset: 0x2286000 VA: 0x228A000 Slot: 5
	public override int get_ProducedStack() { }

	// RVA: 0x228A008 Offset: 0x2286008 VA: 0x228A008 Slot: 8
	public override int Run(InterpretedFrame frame) { }
}


// ===== keywords: Data, Security, UI
// Namespace: System.Security.Cryptography.X509Certificates
public sealed class X500DistinguishedName : AsnEncodedData // TypeDefIndex: 5837
{
	// Fields
	private string name; // 0x20
	private byte[] canonEncoding; // 0x28

	// Methods

	// RVA: 0x258F7C8 Offset: 0x258B7C8 VA: 0x258F7C8
	public void .ctor(byte[] encodedDistinguishedName) { }

	// RVA: 0x258F9B0 Offset: 0x258B9B0 VA: 0x258F9B0
	public string Decode(X500DistinguishedNameFlags flag) { }

	// RVA: 0x258FB78 Offset: 0x258BB78 VA: 0x258FB78 Slot: 5
	public override string Format(bool multiLine) { }

	// RVA: 0x258FB00 Offset: 0x258BB00 VA: 0x258FB00
	private static string GetSeparator(X500DistinguishedNameFlags flag) { }

	// RVA: 0x258F8CC Offset: 0x258B8CC VA: 0x258F8CC
	private void DecodeRawData() { }

	// RVA: 0x258FBD4 Offset: 0x258BBD4 VA: 0x258FBD4
	private static string Canonize(string s) { }

	// RVA: 0x258FDB0 Offset: 0x258BDB0 VA: 0x258FDB0
	internal static bool AreEqual(X500DistinguishedName name1, X500DistinguishedName name2) { }
}


// ===== keywords: Store, Config, IAP
// Namespace: UnityEngine.Purchasing
internal class AppleConfiguration : IAppleConfiguration, IStoreConfiguration // TypeDefIndex: 9129
{
	// Methods

	// RVA: 0x26463BC Offset: 0x26423BC VA: 0x26463BC
	public void .ctor() { }
}


// ===== keywords: Load, Ad , Purchase
// Namespace: UnityEngine.Purchasing
internal sealed class ApplePurchaseFulfilledPayload : IPurchaseFulfilledPayload // TypeDefIndex: 9125
{
	// Fields
	[CompilerGenerated]
	private string <JwsRepresentation>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <OriginalTransactionId>k__BackingField; // 0x18
	[CompilerGenerated]
	private OwnershipType <Ownership>k__BackingField; // 0x20
	[CompilerGenerated]
	private string <AppReceipt>k__BackingField; // 0x28
	[CompilerGenerated]
	private string <AppAccountToken>k__BackingField; // 0x30

	// Properties
	public string JwsRepresentation { get; set; }
	public string OriginalTransactionId { get; set; }
	public OwnershipType Ownership { get; set; }
	public string AppReceipt { get; set; }
	public string AppAccountToken { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x264613C Offset: 0x264213C VA: 0x264613C
	public string get_JwsRepresentation() { }

	[CompilerGenerated]
	// RVA: 0x2646144 Offset: 0x2642144 VA: 0x2646144
	public void set_JwsRepresentation(string value) { }

	[CompilerGenerated]
	// RVA: 0x264614C Offset: 0x264214C VA: 0x264614C
	public string get_OriginalTransactionId() { }

	[CompilerGenerated]
	// RVA: 0x2646154 Offset: 0x2642154 VA: 0x2646154
	public void set_OriginalTransactionId(string value) { }

	[CompilerGenerated]
	// RVA: 0x264615C Offset: 0x264215C VA: 0x264615C
	public OwnershipType get_Ownership() { }

	[CompilerGenerated]
	// RVA: 0x2646164 Offset: 0x2642164 VA: 0x2646164
	public void set_Ownership(OwnershipType value) { }

	[CompilerGenerated]
	// RVA: 0x264616C Offset: 0x264216C VA: 0x264616C
	public string get_AppReceipt() { }

	[CompilerGenerated]
	// RVA: 0x2646174 Offset: 0x2642174 VA: 0x2646174
	public void set_AppReceipt(string value) { }

	[CompilerGenerated]
	// RVA: 0x264617C Offset: 0x264217C VA: 0x264617C
	public string get_AppAccountToken() { }

	[CompilerGenerated]
	// RVA: 0x2646184 Offset: 0x2642184 VA: 0x2646184
	public void set_AppAccountToken(string value) { }

	// RVA: 0x264618C Offset: 0x264218C VA: 0x264618C
	public void .ctor() { }
}


// ===== keywords: Load, Ad , Purchase
// Namespace: UnityEngine.Purchasing
internal sealed class GooglePurchaseFulfilledPayload : IPurchaseFulfilledPayload // TypeDefIndex: 9126
{
	// Fields
	[CompilerGenerated]
	private string <OriginalJson>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <Signature>k__BackingField; // 0x18

	// Properties
	public string OriginalJson { get; set; }
	public string Signature { get; set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x2646194 Offset: 0x2642194 VA: 0x2646194
	public string get_OriginalJson() { }

	[CompilerGenerated]
	// RVA: 0x264619C Offset: 0x264219C VA: 0x264619C
	public void set_OriginalJson(string value) { }

	[CompilerGenerated]
	// RVA: 0x26461A4 Offset: 0x26421A4 VA: 0x26461A4
	public string get_Signature() { }

	[CompilerGenerated]
	// RVA: 0x26461AC Offset: 0x26421AC VA: 0x26461AC
	public void set_Signature(string value) { }

	// RVA: 0x2631174 Offset: 0x262D174 VA: 0x2631174
	public void .ctor() { }
}


// ===== keywords: Data, IAP, Security
// Namespace: UnityEngine.Purchasing.Security
public class InvalidPKCS7Data : IAPSecurityException // TypeDefIndex: 10495
{
	// Methods

	// RVA: 0x266C2E0 Offset: 0x26682E0 VA: 0x266C2E0
	public void .ctor() { }
}


// ===== keywords: Data, IAP, Security
// Namespace: UnityEngine.Purchasing.Security
public class InvalidRSAData : IAPSecurityException // TypeDefIndex: 10498
{
	// Methods

	// RVA: 0x266E158 Offset: 0x266A158 VA: 0x266E158
	public void .ctor() { }
}


// ===== keywords: Data, IAP, Security
// Namespace: UnityEngine.Purchasing.Security
public class InvalidX509Data : IAPSecurityException // TypeDefIndex: 10492
{
	// Methods

	// RVA: 0x266CE48 Offset: 0x2668E48 VA: 0x266CE48
	public void .ctor() { }
}


// ===== keywords: Support, IAP, Security
// Namespace: UnityEngine.Purchasing.Security
public class UnsupportedSignerInfoVersion : IAPSecurityException // TypeDefIndex: 10496
{
	// Methods

	// RVA: 0x266DDC0 Offset: 0x2669DC0 VA: 0x266DDC0
	public void .ctor() { }
}


// ===== keywords: Store, IAP, Purchase
// Namespace: UnityEngine.Purchasing.Services
internal class AppleStoreExtendedPurchaseService : PurchaseService, IAppleStoreExtendedPurchaseService // TypeDefIndex: 9331
{
	// Fields
	private readonly IAppReceiptUseCase m_AppReceiptUseCase; // 0x98
	private readonly IContinuePromotionalPurchasesUseCase m_ContinuePromotionalPurchasesUseCase; // 0xA0
	private readonly IPresentCodeRedemptionSheetUseCase m_PresentCodeRedemptionSheetUseCase; // 0xA8
	private readonly IRestoreTransactionsUseCase m_RestoreTransactionsUseCase; // 0xB0
	private readonly ISetPromotionalPurchaseInterceptorCallbackUseCase m_SetPromotionalPurchaseInterceptorCallbackUseCase; // 0xB8
	private readonly ISimulateAskToBuyUseCase m_SimulateAskToBuyUseCase; // 0xC0
	private readonly IOnEntitlementRevokedUseCase m_OnEntitlementRevokedUseCase; // 0xC8
	private readonly IRefreshAppReceiptUseCase m_RefreshAppReceiptUseCase; // 0xD0
	private readonly IPurchaseEventEmitter m_PurchaseEvent; // 0xD8

	// Properties
	public string appReceipt { get; }

	// Methods

	[Preserve]
	// RVA: 0x26DEFEC Offset: 0x26DAFEC VA: 0x26DEFEC
	internal void .ctor(IAppReceiptUseCase appReceiptUseCase, IContinuePromotionalPurchasesUseCase continuePromotionalPurchasesUseCase, IPresentCodeRedemptionSheetUseCase presentCodeRedemptionSheetUseCase, IRestoreTransactionsUseCase restoreTransactionsUseCase, ISetPromotionalPurchaseInterceptorCallbackUseCase setPromotionalPurchaseInterceptorCallbackUseCase, ISimulateAskToBuyUseCase simulateAskToBuyUseCase, IFetchPurchasesUseCase fetchPurchasesUseCase, IPurchaseUseCase purchaseUseCase, IConfirmOrderUseCase confirmOrderUseCase, ICheckEntitlementUseCase checkEntitlementUseCase, IOnEntitlementRevokedUseCase onEntitlementRevokedUseCase, IAppleStoreCallbacks appleStoreCallbacks, IStoreWrapper storeWrapper, IAnalyticsClient analyticsClient, IRefreshAppReceiptUseCase refreshAppReceiptUseCase, IPurchaseEventEmitter purchaseEvent) { }

	// RVA: 0x26DF22C Offset: 0x26DB22C VA: 0x26DF22C
	private void OnExpiredPurchaseFinished(PendingOrder pendingOrder, ConfirmedOrder confirmedOrder) { }

	// RVA: 0x26DF310 Offset: 0x26DB310 VA: 0x26DF310 Slot: 23
	internal override void SendPurchaseIntentStartEvent(ICart cart) { }

	// RVA: 0x26DF3B8 Offset: 0x26DB3B8 VA: 0x26DF3B8 Slot: 24
	internal override void SendPurchasePaidEvent(PendingOrder order) { }

	// RVA: 0x26DF814 Offset: 0x26DB814 VA: 0x26DF814 Slot: 25
	internal override void SendPurchaseFailedEvent(FailedOrder order) { }

	// RVA: 0x26DF8C0 Offset: 0x26DB8C0 VA: 0x26DF8C0 Slot: 26
	internal override void SendPurchaseFulfilledEvent(ConfirmedOrder order) { }

	// RVA: 0x26DF474 Offset: 0x26DB474 VA: 0x26DF474
	private static ApplePurchaseFulfilledPayload BuildApplePayload(Order order) { }

	// RVA: 0x26DF98C Offset: 0x26DB98C VA: 0x26DF98C
	private void OnEntitlementRevokedUseCaseOnOnEntitlementRevoked(string productId) { }

	// RVA: 0x26DFE58 Offset: 0x26DBE58 VA: 0x26DFE58
	private static bool DoesOrderContainAnyRevokedProductIds(string productId, Order order) { }

	// RVA: 0x26DFFB0 Offset: 0x26DBFB0 VA: 0x26DFFB0 Slot: 28
	public string get_appReceipt() { }

	// RVA: 0x26E0050 Offset: 0x26DC050 VA: 0x26E0050 Slot: 27
	protected override void RestoreTransactionsInternal(Action<bool, string> callback) { }

	// RVA: 0x26E00F8 Offset: 0x26DC0F8 VA: 0x26E00F8 Slot: 29
	public void SetRefreshAppReceipt(bool refreshAppReceipt) { }
}


// ===== keywords: Player, Store, Data
// Namespace: UnityEngine.Purchasing.Stores
internal class PlayerData : IPlayerData // TypeDefIndex: 8382
{
	// Fields
	[CompilerGenerated]
	private string <DisplayName>k__BackingField; // 0x10
	private readonly ICoreRegistryHelper m_CoreRegistry; // 0x18
	private readonly IUtil m_Util; // 0x20
	private readonly IStoreLocationContext m_StoreLocationContext; // 0x28
	private IGoogleAdvertisingIdClient m_AdvertisingIdClient; // 0x30
	private INativeAppleStore m_NativeStore; // 0x38

	// Properties
	public string DisplayName { get; }
	private string m_SessionId { get; }
	private string m_AnalyticsId { get; }
	public string Locale { get; }
	public string RegionCode { get; }
	public string CurrencyCode { get; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x26A85F4 Offset: 0x26A45F4 VA: 0x26A85F4 Slot: 4
	public string get_DisplayName() { }

	// RVA: 0x26A85FC Offset: 0x26A45FC VA: 0x26A85FC
	private string get_m_SessionId() { }

	// RVA: 0x26A8644 Offset: 0x26A4644 VA: 0x26A8644
	private string get_m_AnalyticsId() { }

	[Preserve]
	// RVA: 0x26A864C Offset: 0x26A464C VA: 0x26A864C
	internal void .ctor(ICoreRegistryHelper coreRegistry, IUtil util, IStoreLocationContext storeLocationContext) { }

	[AsyncStateMachine(typeof(PlayerData.<CreatePlayerIdentityAsync>d__17))]
	// RVA: 0x26A86C4 Offset: 0x26A46C4 VA: 0x26A86C4 Slot: 8
	public Task<PlayerIdentity> CreatePlayerIdentityAsync(string impressionId) { }

	// RVA: 0x26A87AC Offset: 0x26A47AC VA: 0x26A87AC Slot: 5
	public string get_Locale() { }

	// RVA: 0x26A8894 Offset: 0x26A4894 VA: 0x26A8894 Slot: 6
	public string get_RegionCode() { }

	// RVA: 0x26A89E0 Offset: 0x26A49E0 VA: 0x26A89E0 Slot: 7
	public string get_CurrencyCode() { }

	// RVA: 0x26A87B0 Offset: 0x26A47B0 VA: 0x26A87B0
	private string GetCurrentLocaleCodeIfValid() { }

	// RVA: 0x26A8958 Offset: 0x26A4958 VA: 0x26A8958
	private RegionInfo GetDefaultRegionInfo() { }
}


// ===== keywords: Store, Mode, Billing
// Namespace: UnityEngine.Purchasing.Stores.Android.GooglePlay.AAR.Models
internal sealed class BillingClient : BillingClientBase, IBillingClient, IBillingClientBase // TypeDefIndex: 8464
{
	// Fields
	private static AndroidJavaClass s_PendingPurchasesParamsClass; // 0x0
	private static AndroidJavaClass s_QueryPurchasesParamsClass; // 0x8
	private static AndroidJavaClass s_AndroidQueryProductDetailsParamsClassName; // 0x10
	private static AndroidJavaClass s_AndroidProductClassName; // 0x18
	private static AndroidJavaClass s_ProductDetailsParamsClass; // 0x20
	private static AndroidJavaClass s_BillingFlowParamsClass; // 0x28
	private static AndroidJavaClass s_SubscriptionUpdateParamsClass; // 0x30
	private static AndroidJavaClass s_ConsumeParamsClass; // 0x38
	private static AndroidJavaClass s_AcknowledgePurchaseParamsClass; // 0x40
	private static AndroidJavaClass s_GetBillingConfigParamsClass; // 0x48

	// Methods

	[Preserve]
	// RVA: 0x26C04A0 Offset: 0x26BC4A0 VA: 0x26C04A0
	internal void .ctor(IGooglePurchasesUpdatedListener googlePurchasesUpdatedListener, IUtil util, ITelemetryDiagnostics telemetryDiagnostics) { }

	// RVA: 0x26C0CA8 Offset: 0x26BCCA8 VA: 0x26C0CA8 Slot: 6
	public void QueryPurchasesAsync(string productType, Action<IGoogleBillingResult, IEnumerable<AndroidJavaObject>> onQueryPurchasesResponse) { }

	// RVA: 0x26C1138 Offset: 0x26BD138 VA: 0x26C1138 Slot: 7
	public void QueryProductDetailsAsync(List<string> products, string type, Action<IGoogleBillingResult, List<AndroidJavaObject>> onProductDetailsResponseAction) { }

	// RVA: 0x26C1858 Offset: 0x26BD858 VA: 0x26C1858 Slot: 8
	public AndroidJavaObject LaunchBillingFlow(AndroidJavaObject productDetails, string oldPurchaseToken, Nullable<GooglePlayReplacementMode> replacementMode) { }

	// RVA: 0x26C2594 Offset: 0x26BE594 VA: 0x26C2594 Slot: 9
	public void ConsumeAsync(string purchaseToken, Action<IGoogleBillingResult> onConsume) { }

	// RVA: 0x26C2B98 Offset: 0x26BEB98 VA: 0x26C2B98 Slot: 10
	public void AcknowledgePurchase(string purchaseToken, Action<IGoogleBillingResult> onAcknowledge) { }

	// RVA: 0x26C319C Offset: 0x26BF19C VA: 0x26C319C Slot: 5
	public void GetBillingConfigAsync(Action<IGoogleBillingResult, string> onBillingConfigResponse) { }

	// RVA: 0x26C0DE4 Offset: 0x26BCDE4 VA: 0x26C0DE4
	private static AndroidJavaObject QueryPurchasesParams(string productType) { }

	// RVA: 0x26C3704 Offset: 0x26BF704 VA: 0x26C3704
	private static AndroidJavaClass GetQueryPurchasesParamsClass() { }

	// RVA: 0x26C13CC Offset: 0x26BD3CC VA: 0x26C13CC
	private static AndroidJavaObject QueryProductDetailsParams(List<string> products, string type) { }

	// RVA: 0x26C383C Offset: 0x26BF83C VA: 0x26C383C
	private static AndroidJavaObject QueryProductDetailsParamsProductList(List<string> products, string type) { }

	// RVA: 0x26C3954 Offset: 0x26BF954 VA: 0x26C3954
	private static AndroidJavaObject QueryProductDetailsParamsProduct(string type, string product) { }

	// RVA: 0x26C3D44 Offset: 0x26BFD44 VA: 0x26C3D44
	private static AndroidJavaClass GetProductParamsClass() { }

	// RVA: 0x26C220C Offset: 0x26BE20C VA: 0x26C220C
	private static AndroidJavaClass GetProductDetailsParamsClass() { }

	// RVA: 0x26C22A8 Offset: 0x26BE2A8 VA: 0x26C22A8
	private AndroidJavaObject MakeBillingFlowParams(AndroidJavaObject productDetailsParamsList, string oldPurchaseToken, Nullable<GooglePlayReplacementMode> replacementMode) { }

	// RVA: 0x26C3DE0 Offset: 0x26BFDE0 VA: 0x26C3DE0
	private static AndroidJavaClass GetBillingFlowParamClass() { }

	// RVA: 0x26C4464 Offset: 0x26C0464 VA: 0x26C4464
	private static AndroidJavaClass GetSubscriptionUpdateParamClass() { }

	// RVA: 0x26C404C Offset: 0x26C004C VA: 0x26C404C
	private static AndroidJavaObject BuildSubscriptionUpdateParams(string oldPurchaseToken, GooglePlayReplacementMode replacementMode) { }

	// RVA: 0x26C3F64 Offset: 0x26BFF64 VA: 0x26C3F64
	private AndroidJavaObject SetObfuscatedProfileIdIfNeeded(AndroidJavaObject billingFlowParams) { }

	// RVA: 0x26C3E7C Offset: 0x26BFE7C VA: 0x26C3E7C
	private AndroidJavaObject SetObfuscatedAccountIdIfNeeded(AndroidJavaObject billingFlowParams) { }

	// RVA: 0x26C2AFC Offset: 0x26BEAFC VA: 0x26C2AFC
	private static AndroidJavaClass GetConsumeParamsClass() { }

	// RVA: 0x26C3100 Offset: 0x26BF100 VA: 0x26C3100
	private static AndroidJavaClass GetAcknowledgePurchaseParamsClass() { }

	// RVA: 0x26C097C Offset: 0x26BC97C VA: 0x26C097C
	private static AndroidJavaObject PendingPurchasesParams() { }

	// RVA: 0x26C37A0 Offset: 0x26BF7A0 VA: 0x26C37A0
	private static AndroidJavaClass GetQueryProductDetailsParamsParamsClass() { }

	// RVA: 0x26C4500 Offset: 0x26C0500 VA: 0x26C4500
	private static AndroidJavaClass GetPendingPurchasesParamsClass() { }

	// RVA: 0x26C3668 Offset: 0x26BF668 VA: 0x26C3668
	private static AndroidJavaClass GetBillingConfigParamsClass() { }
}


// ===== keywords: UI, Panel, Event
// Namespace: UnityEngine.UIElements
public class AttachToPanelEvent : PanelChangedEventBase<AttachToPanelEvent> // TypeDefIndex: 4343
{
	// Methods

	// RVA: 0x28F7594 Offset: 0x28F3594 VA: 0x28F7594
	private static void .cctor() { }

	// RVA: 0x28F7678 Offset: 0x28F3678 VA: 0x28F7678
	public void .ctor() { }
}


// ===== keywords: Data, Drop, UI
// Namespace: UnityEngine.UIElements
internal class DefaultDragAndDropClient : DragAndDropData, IDragAndDrop // TypeDefIndex: 4193
{
	// Fields
	private readonly Hashtable m_GenericData; // 0x10
	private Label m_DraggedInfoLabel; // 0x18
	private DragVisualMode m_VisualMode; // 0x20
	private IEnumerable<Object> m_UnityObjectReferences; // 0x28

	// Properties
	public override object source { get; }
	public DragAndDropData data { get; }

	// Methods

	// RVA: 0x28DF7B4 Offset: 0x28DB7B4 VA: 0x28DF7B4 Slot: 5
	public override object get_source() { }

	// RVA: 0x28DF804 Offset: 0x28DB804 VA: 0x28DF804 Slot: 4
	public override object GetGenericData(string key) { }

	// RVA: 0x28DF868 Offset: 0x28DB868 VA: 0x28DF868 Slot: 6
	public void StartDrag(StartDragArgs args, Vector3 pointerPosition) { }

	// RVA: 0x28DFF20 Offset: 0x28DBF20 VA: 0x28DFF20 Slot: 7
	public void UpdateDrag(Vector3 pointerPosition) { }

	// RVA: 0x28E00B4 Offset: 0x28DC0B4 VA: 0x28E00B4 Slot: 8
	public void AcceptDrag() { }

	// RVA: 0x28E00B8 Offset: 0x28DC0B8 VA: 0x28E00B8 Slot: 10
	public void SetVisualMode(DragVisualMode mode) { }

	// RVA: 0x28E00C0 Offset: 0x28DC0C0 VA: 0x28E00C0 Slot: 9
	public void DragCleanup() { }

	// RVA: 0x28E0104 Offset: 0x28DC104 VA: 0x28E0104 Slot: 11
	public DragAndDropData get_data() { }

	// RVA: 0x28DF754 Offset: 0x28DB754 VA: 0x28DF754
	public void .ctor() { }
}


// ===== keywords: UI, Panel, Event
// Namespace: UnityEngine.UIElements
public class DetachFromPanelEvent : PanelChangedEventBase<DetachFromPanelEvent> // TypeDefIndex: 4345
{
	// Methods

	// RVA: 0x28F7774 Offset: 0x28F3774 VA: 0x28F7774
	private static void .cctor() { }

	// RVA: 0x28F7858 Offset: 0x28F3858 VA: 0x28F7858
	public void .ctor() { }
}


// ===== keywords: Drop, UI, Popup
// Namespace: UnityEngine.UIElements
public class DropdownField : PopupField<string> // TypeDefIndex: 4019
{
	// Methods

	// RVA: 0x2844498 Offset: 0x2840498 VA: 0x2844498
	public void .ctor() { }

	// RVA: 0x28444A0 Offset: 0x28404A0 VA: 0x28444A0
	public void .ctor(string label) { }
}


// ===== keywords: Item, Drop, UI
// Namespace: UnityEngine.UIElements
public class DropdownMenuAction : DropdownMenuItem // TypeDefIndex: 4220
{
	// Fields
	[CompilerGenerated]
	private readonly string <name>k__BackingField; // 0x10
	[CompilerGenerated]
	private DropdownMenuAction.Status <status>k__BackingField; // 0x18
	[CompilerGenerated]
	private DropdownMenuEventInfo <eventInfo>k__BackingField; // 0x20
	[CompilerGenerated]
	private object <userData>k__BackingField; // 0x28
	private readonly Action<DropdownMenuAction> actionCallback; // 0x30
	private readonly Func<DropdownMenuAction, DropdownMenuAction.Status> actionStatusCallback; // 0x38

	// Properties
	private DropdownMenuAction.Status status { set; }
	private DropdownMenuEventInfo eventInfo { set; }
	private object userData { set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x28E8AE8 Offset: 0x28E4AE8 VA: 0x28E8AE8
	private void set_status(DropdownMenuAction.Status value) { }

	[CompilerGenerated]
	// RVA: 0x28E8AF0 Offset: 0x28E4AF0 VA: 0x28E8AF0
	private void set_eventInfo(DropdownMenuEventInfo value) { }

	[CompilerGenerated]
	// RVA: 0x28E8AF8 Offset: 0x28E4AF8 VA: 0x28E8AF8
	private void set_userData(object value) { }

	// RVA: 0x28E8B00 Offset: 0x28E4B00 VA: 0x28E8B00
	public static DropdownMenuAction.Status AlwaysEnabled(DropdownMenuAction a) { }

	// RVA: 0x28E8B08 Offset: 0x28E4B08 VA: 0x28E8B08
	public static DropdownMenuAction.Status AlwaysDisabled(DropdownMenuAction a) { }

	// RVA: 0x28E8B10 Offset: 0x28E4B10 VA: 0x28E8B10
	public void .ctor(string actionName, Action<DropdownMenuAction> actionCallback, Func<DropdownMenuAction, DropdownMenuAction.Status> actionStatusCallback, object userData) { }

	// RVA: 0x28E8B54 Offset: 0x28E4B54 VA: 0x28E8B54
	public void UpdateActionStatus(DropdownMenuEventInfo eventInfo) { }
}


// ===== keywords: Item, Drop, UI
// Namespace: UnityEngine.UIElements
public class DropdownMenuSeparator : DropdownMenuItem // TypeDefIndex: 4218
{
	// Fields
	[CompilerGenerated]
	private readonly string <subMenuPath>k__BackingField; // 0x10

	// Methods

	// RVA: 0x28E8AC0 Offset: 0x28E4AC0 VA: 0x28E8AC0
	public void .ctor(string subMenuPath) { }
}


// ===== keywords: Debug, UI, Event
// Namespace: UnityEngine.UIElements
internal struct EventDebuggerLogCall : IDisposable // TypeDefIndex: 4267
{
	// Methods

	// RVA: 0x28EF1BC Offset: 0x28EB1BC VA: 0x28EF1BC
	public void .ctor(Delegate callback, EventBase evt) { }

	// RVA: 0x28EF1C0 Offset: 0x28EB1C0 VA: 0x28EF1C0 Slot: 4
	public void Dispose() { }
}


// ===== keywords: Debug, UI, Event
// Namespace: UnityEngine.UIElements
internal struct EventDebuggerLogExecuteDefaultAction : IDisposable // TypeDefIndex: 4269
{
	// Methods

	// RVA: 0x28EF1CC Offset: 0x28EB1CC VA: 0x28EF1CC
	public void .ctor(EventBase evt) { }

	// RVA: 0x28EF1D0 Offset: 0x28EB1D0 VA: 0x28EF1D0 Slot: 4
	public void Dispose() { }
}


// ===== keywords: Debug, UI, Event
// Namespace: UnityEngine.UIElements
internal struct EventDebuggerLogIMGUICall : IDisposable // TypeDefIndex: 4268
{
	// Methods

	// RVA: 0x28EF1C4 Offset: 0x28EB1C4 VA: 0x28EF1C4
	public void .ctor(EventBase evt) { }

	// RVA: 0x28EF1C8 Offset: 0x28EB1C8 VA: 0x28EF1C8 Slot: 4
	public void Dispose() { }
}


// ===== keywords: UI, Panel, Event
// Namespace: UnityEngine.UIElements
public class PanelEventHandler : UIBehaviour, IPointerMoveHandler, IEventSystemHandler, IPointerUpHandler, IPointerDownHandler, ISubmitHandler, ICancelHandler, IMoveHandler, IScrollHandler, ISelectHandler, IDeselectHandler, IPointerExitHandler, IPointerEnterHandler, IRuntimePanelComponent, IPointerClickHandler // TypeDefIndex: 8791
{
	// Fields
	private BaseRuntimePanel m_Panel; // 0x20
	private readonly PanelEventHandler.PointerEvent m_PointerEvent; // 0x28
	private float m_LastClickTime; // 0x30
	private bool m_Selecting; // 0x34
	private Event m_Event; // 0x38
	private static EventModifiers s_Modifiers; // 0x0

	// Properties
	public IPanel panel { get; set; }
	private GameObject selectableGameObject { get; }
	private EventSystem eventSystem { get; }
	private bool isCurrentFocusedPanel { get; }
	private Focusable currentFocusedElement { get; }

	// Methods

	// RVA: 0x297BC2C Offset: 0x2977C2C VA: 0x297BC2C Slot: 30
	public IPanel get_panel() { }

	// RVA: 0x297BC34 Offset: 0x2977C34 VA: 0x297BC34 Slot: 28
	public void set_panel(IPanel value) { }

	// RVA: 0x297C040 Offset: 0x2978040 VA: 0x297C040
	private GameObject get_selectableGameObject() { }

	// RVA: 0x297C058 Offset: 0x2978058 VA: 0x297C058
	private EventSystem get_eventSystem() { }

	// RVA: 0x297C12C Offset: 0x297812C VA: 0x297C12C
	private bool get_isCurrentFocusedPanel() { }

	// RVA: 0x297C1F4 Offset: 0x29781F4 VA: 0x297C1F4
	private Focusable get_currentFocusedElement() { }

	// RVA: 0x297C22C Offset: 0x297822C VA: 0x297C22C Slot: 5
	protected override void OnEnable() { }

	// RVA: 0x297C248 Offset: 0x2978248 VA: 0x297C248 Slot: 7
	protected override void OnDisable() { }

	// RVA: 0x297BE8C Offset: 0x2977E8C VA: 0x297BE8C
	private void RegisterCallbacks() { }

	// RVA: 0x297BCD8 Offset: 0x2977CD8 VA: 0x297BCD8
	private void UnregisterCallbacks() { }

	// RVA: 0x297C264 Offset: 0x2978264 VA: 0x297C264
	private void OnPanelDestroyed() { }

	// RVA: 0x297C26C Offset: 0x297826C VA: 0x297C26C
	private void OnElementFocus(FocusEvent e) { }

	// RVA: 0x297C354 Offset: 0x2978354 VA: 0x297C354
	private void OnElementBlur(BlurEvent e) { }

	// RVA: 0x297C358 Offset: 0x2978358 VA: 0x297C358 Slot: 24
	public void OnSelect(BaseEventData eventData) { }

	// RVA: 0x297C3D0 Offset: 0x29783D0 VA: 0x297C3D0 Slot: 25
	public void OnDeselect(BaseEventData eventData) { }

	// RVA: 0x297C3E4 Offset: 0x29783E4 VA: 0x297C3E4 Slot: 17
	public void OnPointerMove(PointerEventData eventData) { }

	// RVA: 0x297C734 Offset: 0x2978734 VA: 0x297C734 Slot: 18
	public void OnPointerUp(PointerEventData eventData) { }

	// RVA: 0x297C950 Offset: 0x2978950 VA: 0x297C950 Slot: 19
	public void OnPointerDown(PointerEventData eventData) { }

	// RVA: 0x297CBDC Offset: 0x2978BDC VA: 0x297CBDC Slot: 26
	public void OnPointerExit(PointerEventData eventData) { }

	// RVA: 0x297CF04 Offset: 0x2978F04 VA: 0x297CF04 Slot: 27
	public void OnPointerEnter(PointerEventData eventData) { }

	// RVA: 0x297CF58 Offset: 0x2978F58 VA: 0x297CF58 Slot: 29
	public void OnPointerClick(PointerEventData eventData) { }

	// RVA: 0x297CF74 Offset: 0x2978F74 VA: 0x297CF74 Slot: 20
	public void OnSubmit(BaseEventData eventData) { }

	// RVA: 0x297D2CC Offset: 0x29792CC VA: 0x297D2CC Slot: 21
	public void OnCancel(BaseEventData eventData) { }

	// RVA: 0x297D4DC Offset: 0x29794DC VA: 0x297D4DC Slot: 22
	public void OnMove(AxisEventData eventData) { }

	// RVA: 0x297D710 Offset: 0x2979710 VA: 0x297D710 Slot: 23
	public void OnScroll(PointerEventData eventData) { }

	// RVA: 0x297C6D0 Offset: 0x29786D0 VA: 0x297C6D0
	private void SendEvent(EventBase e, BaseEventData sourceEventData) { }

	// RVA: 0x297D904 Offset: 0x2979904 VA: 0x297D904
	private void SendEvent(EventBase e, Event sourceEvent) { }

	// RVA: 0x297D924 Offset: 0x2979924 VA: 0x297D924
	internal void Update() { }

	// RVA: 0x297D980 Offset: 0x2979980 VA: 0x297D980
	private void LateUpdate() { }

	// RVA: 0x297D184 Offset: 0x2979184 VA: 0x297D184
	private void ProcessImguiEvents(Focusable target) { }

	// RVA: 0x297D988 Offset: 0x2979988 VA: 0x297D988
	private void ProcessKeyboardEvent(Event e, Focusable target) { }

	// RVA: 0x297DA08 Offset: 0x2979A08 VA: 0x297DA08
	private void ProcessTabEvent(Event e, Focusable target) { }

	// RVA: 0x297DE90 Offset: 0x2979E90 VA: 0x297DE90
	private void SendTabEvent(Event e, NavigationMoveEvent.Direction direction, Focusable target) { }

	// RVA: 0x297DA70 Offset: 0x2979A70 VA: 0x297DA70
	private void SendKeyUpEvent(Event e, Focusable target) { }

	// RVA: 0x297DC80 Offset: 0x2979C80 VA: 0x297DC80
	private void SendKeyDownEvent(Event e, Focusable target) { }

	// RVA: 0x297C590 Offset: 0x2978590 VA: 0x297C590
	private bool ReadPointerData(PanelEventHandler.PointerEvent pe, PointerEventData eventData, PanelEventHandler.PointerEventType eventType = 0) { }

	// RVA: 0x297E560 Offset: 0x297A560 VA: 0x297E560
	public void .ctor() { }
}


// ===== keywords: Setting, UI, Panel
// Namespace: UnityEngine.UIElements
public class PanelSettings : ScriptableObject // TypeDefIndex: 4410
{
	// Fields
	private const int k_DefaultSortingOrder = 0;
	private const float k_DefaultScaleValue = 1;
	internal const string k_DefaultStyleSheetPath = "Packages/com.unity.ui/PackageResources/StyleSheets/Generated/Default.tss.asset";
	[SerializeField]
	private ThemeStyleSheet themeUss; // 0x18
	[SerializeField]
	private RenderTexture m_TargetTexture; // 0x20
	[SerializeField]
	private PanelScaleMode m_ScaleMode; // 0x28
	[SerializeField]
	private float m_ReferenceSpritePixelsPerUnit; // 0x2C
	[SerializeField]
	private float m_Scale; // 0x30
	private const float DefaultDpi = 96;
	[SerializeField]
	private float m_ReferenceDpi; // 0x34
	[SerializeField]
	private float m_FallbackDpi; // 0x38
	[SerializeField]
	private Vector2Int m_ReferenceResolution; // 0x3C
	[SerializeField]
	private PanelScreenMatchMode m_ScreenMatchMode; // 0x44
	[SerializeField]
	private float m_Match; // 0x48
	[SerializeField]
	private float m_SortingOrder; // 0x4C
	[SerializeField]
	private int m_TargetDisplay; // 0x50
	[SerializeField]
	private bool m_ClearDepthStencil; // 0x54
	[SerializeField]
	private bool m_ClearColor; // 0x55
	[SerializeField]
	private Color m_ColorClearValue; // 0x58
	private PanelSettings.RuntimePanelAccess m_PanelAccess; // 0x68
	internal UIDocumentList m_AttachedUIDocumentsList; // 0x70
	[SerializeField]
	private DynamicAtlasSettings m_DynamicAtlasSettings; // 0x78
	[SerializeField]
	private Shader m_AtlasBlitShader; // 0x80
	[SerializeField]
	private Shader m_RuntimeShader; // 0x88
	[SerializeField]
	private Shader m_RuntimeWorldShader; // 0x90
	[SerializeField]
	public PanelTextSettings textSettings; // 0x98
	private Rect m_TargetRect; // 0xA0
	private float m_ResolvedScale; // 0xB0
	private StyleSheet m_OldThemeUss; // 0xB8
	[CompilerGenerated]
	private float <ScreenDPI>k__BackingField; // 0xC0
	private Func<Vector2, Vector2> m_AssignedScreenToPanel; // 0xC8

	// Properties
	public ThemeStyleSheet themeStyleSheet { get; set; }
	public RenderTexture targetTexture { get; set; }
	public PanelScaleMode scaleMode { get; set; }
	public float referenceSpritePixelsPerUnit { get; set; }
	public float scale { get; set; }
	public float referenceDpi { get; set; }
	public float fallbackDpi { get; set; }
	public Vector2Int referenceResolution { get; set; }
	public PanelScreenMatchMode screenMatchMode { get; set; }
	public float match { get; set; }
	public float sortingOrder { get; set; }
	public int targetDisplay { get; set; }
	public bool clearDepthStencil { get; set; }
	public float depthClearValue { get; }
	public bool clearColor { get; set; }
	public Color colorClearValue { get; set; }
	internal BaseRuntimePanel panel { get; }
	internal bool isInitialized { get; }
	internal VisualElement visualTree { get; }
	public DynamicAtlasSettings dynamicAtlasSettings { get; set; }
	private float ScreenDPI { get; set; }

	// Methods

	// RVA: 0x2900FD8 Offset: 0x28FCFD8 VA: 0x2900FD8
	public ThemeStyleSheet get_themeStyleSheet() { }

	// RVA: 0x2900FE0 Offset: 0x28FCFE0 VA: 0x2900FE0
	public void set_themeStyleSheet(ThemeStyleSheet value) { }

	// RVA: 0x2901148 Offset: 0x28FD148 VA: 0x2901148
	public RenderTexture get_targetTexture() { }

	// RVA: 0x2901150 Offset: 0x28FD150 VA: 0x2901150
	public void set_targetTexture(RenderTexture value) { }

	// RVA: 0x29011AC Offset: 0x28FD1AC VA: 0x29011AC
	public PanelScaleMode get_scaleMode() { }

	// RVA: 0x29011B4 Offset: 0x28FD1B4 VA: 0x29011B4
	public void set_scaleMode(PanelScaleMode value) { }

	// RVA: 0x29011BC Offset: 0x28FD1BC VA: 0x29011BC
	public float get_referenceSpritePixelsPerUnit() { }

	// RVA: 0x29011C4 Offset: 0x28FD1C4 VA: 0x29011C4
	public void set_referenceSpritePixelsPerUnit(float value) { }

	// RVA: 0x29011CC Offset: 0x28FD1CC VA: 0x29011CC
	public float get_scale() { }

	// RVA: 0x29011D4 Offset: 0x28FD1D4 VA: 0x29011D4
	public void set_scale(float value) { }

	// RVA: 0x29011DC Offset: 0x28FD1DC VA: 0x29011DC
	public float get_referenceDpi() { }

	// RVA: 0x29011E4 Offset: 0x28FD1E4 VA: 0x29011E4
	public void set_referenceDpi(float value) { }

	// RVA: 0x2901210 Offset: 0x28FD210 VA: 0x2901210
	public float get_fallbackDpi() { }

	// RVA: 0x2901218 Offset: 0x28FD218 VA: 0x2901218
	public void set_fallbackDpi(float value) { }

	// RVA: 0x2901244 Offset: 0x28FD244 VA: 0x2901244
	public Vector2Int get_referenceResolution() { }

	// RVA: 0x290124C Offset: 0x28FD24C VA: 0x290124C
	public void set_referenceResolution(Vector2Int value) { }

	// RVA: 0x2901254 Offset: 0x28FD254 VA: 0x2901254
	public PanelScreenMatchMode get_screenMatchMode() { }

	// RVA: 0x290125C Offset: 0x28FD25C VA: 0x290125C
	public void set_screenMatchMode(PanelScreenMatchMode value) { }

	// RVA: 0x2901264 Offset: 0x28FD264 VA: 0x2901264
	public float get_match() { }

	// RVA: 0x290126C Offset: 0x28FD26C VA: 0x290126C
	public void set_match(float value) { }

	// RVA: 0x2901274 Offset: 0x28FD274 VA: 0x2901274
	public float get_sortingOrder() { }

	// RVA: 0x290127C Offset: 0x28FD27C VA: 0x290127C
	public void set_sortingOrder(float value) { }

	// RVA: 0x290129C Offset: 0x28FD29C VA: 0x290129C
	internal void ApplySortingOrder() { }

	// RVA: 0x29012E8 Offset: 0x28FD2E8 VA: 0x29012E8
	public int get_targetDisplay() { }

	// RVA: 0x29012F0 Offset: 0x28FD2F0 VA: 0x29012F0
	public void set_targetDisplay(int value) { }

	// RVA: 0x290134C Offset: 0x28FD34C VA: 0x290134C
	public bool get_clearDepthStencil() { }

	// RVA: 0x2901354 Offset: 0x28FD354 VA: 0x2901354
	public void set_clearDepthStencil(bool value) { }

	// RVA: 0x2901360 Offset: 0x28FD360 VA: 0x2901360
	public float get_depthClearValue() { }

	// RVA: 0x290136C Offset: 0x28FD36C VA: 0x290136C
	public bool get_clearColor() { }

	// RVA: 0x2901374 Offset: 0x28FD374 VA: 0x2901374
	public void set_clearColor(bool value) { }

	// RVA: 0x2901380 Offset: 0x28FD380 VA: 0x2901380
	public Color get_colorClearValue() { }

	// RVA: 0x290138C Offset: 0x28FD38C VA: 0x290138C
	public void set_colorClearValue(Color value) { }

	// RVA: 0x2901398 Offset: 0x28FD398 VA: 0x2901398
	internal BaseRuntimePanel get_panel() { }

	// RVA: 0x29014E8 Offset: 0x28FD4E8 VA: 0x29014E8
	internal bool get_isInitialized() { }

	// RVA: 0x2901518 Offset: 0x28FD518 VA: 0x2901518
	internal VisualElement get_visualTree() { }

	// RVA: 0x2901544 Offset: 0x28FD544 VA: 0x2901544
	public DynamicAtlasSettings get_dynamicAtlasSettings() { }

	// RVA: 0x290154C Offset: 0x28FD54C VA: 0x290154C
	public void set_dynamicAtlasSettings(DynamicAtlasSettings value) { }

	// RVA: 0x2901554 Offset: 0x28FD554 VA: 0x2901554
	private void .ctor() { }

	// RVA: 0x290161C Offset: 0x28FD61C VA: 0x290161C
	private void OnEnable() { }

	// RVA: 0x29018B8 Offset: 0x28FD8B8 VA: 0x29018B8
	private void OnDisable() { }

	// RVA: 0x2901904 Offset: 0x28FD904 VA: 0x2901904
	internal void DisposePanel() { }

	[CompilerGenerated]
	// RVA: 0x2901930 Offset: 0x28FD930 VA: 0x2901930
	private float get_ScreenDPI() { }

	[CompilerGenerated]
	// RVA: 0x2901938 Offset: 0x28FD938 VA: 0x2901938
	private void set_ScreenDPI(float value) { }

	// RVA: 0x2901724 Offset: 0x28FD724 VA: 0x2901724
	internal void UpdateScreenDPI() { }

	// RVA: 0x2900FEC Offset: 0x28FCFEC VA: 0x2900FEC
	private void ApplyThemeStyleSheet(VisualElement root) { }

	// RVA: 0x2901740 Offset: 0x28FD740 VA: 0x2901740
	private void InitializeShaders() { }

	// RVA: 0x2901940 Offset: 0x28FD940 VA: 0x2901940
	internal void ApplyPanelSettings() { }

	// RVA: 0x29021E0 Offset: 0x28FE1E0 VA: 0x29021E0
	public void SetScreenToPanelSpaceFunction(Func<Vector2, Vector2> screentoPanelSpaceFunction) { }

	// RVA: 0x2902004 Offset: 0x28FE004 VA: 0x2902004
	internal float ResolveScale(Rect targetRect, float screenDpi) { }

	// RVA: 0x2901F0C Offset: 0x28FDF0C VA: 0x2901F0C
	internal Rect GetDisplayRect() { }

	// RVA: 0x2902210 Offset: 0x28FE210 VA: 0x2902210
	internal void AttachAndInsertUIDocumentToVisualTree(UIDocument uiDocument) { }

	// RVA: 0x29026CC Offset: 0x28FE6CC VA: 0x29026CC
	internal void DetachUIDocument(UIDocument uiDocument) { }
}


// ===== keywords: Setting, UI, Panel
// Namespace: UnityEngine.UIElements
public class PanelTextSettings : TextSettings // TypeDefIndex: 4644
{
	// Fields
	private static PanelTextSettings s_DefaultPanelTextSettings; // 0x0
	internal static Func<string, Object> EditorGUIUtilityLoad; // 0x8
	internal static Func<SystemLanguage> GetCurrentLanguage; // 0x10
	internal static readonly string s_DefaultEditorPanelTextSettingPath; // 0x18

	// Properties
	internal static PanelTextSettings defaultPanelTextSettings { get; }

	// Methods

	// RVA: 0x295833C Offset: 0x295433C VA: 0x295833C
	internal static PanelTextSettings get_defaultPanelTextSettings() { }

	// RVA: 0x2958470 Offset: 0x2954470 VA: 0x2958470
	internal static void UpdateLocalizationFontAsset() { }

	// RVA: 0x2958A2C Offset: 0x2954A2C VA: 0x2958A2C
	internal FontAsset GetCachedFontAsset(Font font) { }

	// RVA: 0x2958A34 Offset: 0x2954A34 VA: 0x2958A34
	public void .ctor() { }

	// RVA: 0x2958A3C Offset: 0x2954A3C VA: 0x2958A3C
	private static void .cctor() { }
}


// ===== keywords: UI, Event, Stat
// Namespace: UnityEngine.UIElements
public sealed class PointerStationaryEvent : PointerEventBase<PointerStationaryEvent> // TypeDefIndex: 4362
{
	// Methods

	// RVA: 0x28FA66C Offset: 0x28F666C VA: 0x28FA66C
	private static void .cctor() { }

	// RVA: 0x28FA750 Offset: 0x28F6750 VA: 0x28FA750 Slot: 12
	protected override void Init() { }

	// RVA: 0x28FA7A0 Offset: 0x28F67A0 VA: 0x28FA7A0
	private void LocalInit() { }

	// RVA: 0x28FA8A4 Offset: 0x28F68A4 VA: 0x28FA8A4
	public void .ctor() { }
}


// ===== keywords: Save, Data, UI
// Namespace: UnityEngine.UIElements
internal sealed class SavePersistentViewData : MulticastDelegate // TypeDefIndex: 4461
{
	// Methods

	// RVA: 0x290B5CC Offset: 0x29075CC VA: 0x290B5CC
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x290B654 Offset: 0x2907654 VA: 0x290B654 Slot: 12
	public virtual void Invoke() { }
}


// ===== keywords: UI, Screen, Event
// Namespace: UnityEngine.UIElements
internal class TouchScreenTextEditorEventHandler : TextEditorEventHandler // TypeDefIndex: 4065
{
	// Fields
	private IVisualElementScheduledItem m_TouchKeyboardPoller; // 0x20
	private bool m_TouchKeyboardAllowsInPlaceEditing; // 0x28
	private bool m_IsClicking; // 0x29

	// Methods

	// RVA: 0x28B5B18 Offset: 0x28B1B18 VA: 0x28B5B18
	public void .ctor(TextElement textElement, TextEditingUtilities editingUtilities) { }

	// RVA: 0x28B5B4C Offset: 0x28B1B4C VA: 0x28B5B4C
	private void PollTouchScreenKeyboard() { }

	// RVA: 0x28B5D88 Offset: 0x28B1D88 VA: 0x28B5D88
	private void DoPollTouchScreenKeyboard() { }

	// RVA: 0x28B66AC Offset: 0x28B26AC VA: 0x28B66AC
	private void UpdateStringPositionFromKeyboard() { }

	// RVA: 0x28B65C8 Offset: 0x28B25C8 VA: 0x28B65C8
	private void CloseTouchScreenKeyboard() { }

	// RVA: 0x28B691C Offset: 0x28B291C VA: 0x28B691C
	private void OpenTouchScreenKeyboard() { }

	// RVA: 0x28B6E24 Offset: 0x28B2E24 VA: 0x28B6E24 Slot: 4
	public override void ExecuteDefaultActionAtTarget(EventBase evt) { }

	// RVA: 0x28B7000 Offset: 0x28B3000 VA: 0x28B7000
	private void OnPointerDownEvent() { }

	// RVA: 0x28B71C0 Offset: 0x28B31C0 VA: 0x28B71C0
	private void OnPointerUpEvent(PointerUpEvent evt) { }

	// RVA: 0x28B71E0 Offset: 0x28B31E0 VA: 0x28B71E0
	private void OnFocusInEvent() { }

	// RVA: 0x28B7360 Offset: 0x28B3360 VA: 0x28B7360
	private void OnFocusOutEvent(FocusOutEvent evt) { }
}


// ===== keywords: UI, Event, Wheel
// Namespace: UnityEngine.UIElements
public class WheelEvent : MouseEventBase<WheelEvent> // TypeDefIndex: 4313
{
	// Fields
	[CompilerGenerated]
	private Vector3 <delta>k__BackingField; // 0xB8

	// Properties
	public Vector3 delta { get; set; }

	// Methods

	// RVA: 0x28F3DB0 Offset: 0x28EFDB0 VA: 0x28F3DB0
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x28F3E94 Offset: 0x28EFE94 VA: 0x28F3E94
	public Vector3 get_delta() { }

	[CompilerGenerated]
	// RVA: 0x28F3EA0 Offset: 0x28EFEA0 VA: 0x28F3EA0
	private void set_delta(Vector3 value) { }

	// RVA: 0x28F3EAC Offset: 0x28EFEAC VA: 0x28F3EAC
	public static WheelEvent GetPooled(Event systemEvent) { }

	// RVA: 0x28DE450 Offset: 0x28DA450 VA: 0x28DE450
	internal static WheelEvent GetPooled(Vector3 delta, Vector3 mousePosition, EventModifiers modifiers = 0) { }

	// RVA: 0x28F3F28 Offset: 0x28EFF28 VA: 0x28F3F28
	internal static WheelEvent GetPooled(Vector3 delta, IPointerEvent pointerEvent) { }

	// RVA: 0x28F3FA0 Offset: 0x28EFFA0 VA: 0x28F3FA0 Slot: 12
	protected override void Init() { }

	// RVA: 0x28F3FF0 Offset: 0x28EFFF0 VA: 0x28F3FF0
	private void LocalInit() { }

	// RVA: 0x28F4050 Offset: 0x28F0050 VA: 0x28F4050
	public void .ctor() { }
}


// ===== keywords: Event, Stat
// Namespace: 
public sealed class AnimationState.TrackEntryEventDelegate : MulticastDelegate // TypeDefIndex: 8505
{
	// Methods

	// RVA: 0x220E3DC Offset: 0x220A3DC VA: 0x220E3DC
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x220E4E0 Offset: 0x220A4E0 VA: 0x220E4E0 Slot: 12
	public virtual void Invoke(TrackEntry trackEntry, Event e) { }
}


// ===== keywords: Data, Stat
// Namespace: 
public class AnimationStateData.AnimationPairComparer : IEqualityComparer<AnimationStateData.AnimationPair> // TypeDefIndex: 8514
{
	// Fields
	public static readonly AnimationStateData.AnimationPairComparer Instance; // 0x0

	// Methods

	// RVA: 0x220ED08 Offset: 0x220AD08 VA: 0x220ED08 Slot: 4
	private bool System.Collections.Generic.IEqualityComparer<Spine.AnimationStateData.AnimationPair>.Equals(AnimationStateData.AnimationPair x, AnimationStateData.AnimationPair y) { }

	// RVA: 0x220ED20 Offset: 0x220AD20 VA: 0x220ED20 Slot: 5
	private int System.Collections.Generic.IEqualityComparer<Spine.AnimationStateData.AnimationPair>.GetHashCode(AnimationStateData.AnimationPair obj) { }

	// RVA: 0x220ED74 Offset: 0x220AD74 VA: 0x220ED74
	public void .ctor() { }

	// RVA: 0x220ED7C Offset: 0x220AD7C VA: 0x220ED7C
	private static void .cctor() { }
}


// ===== keywords: Battle, Pass
// Namespace: 
public class Board_BattlePass : Board // TypeDefIndex: 475
{
	// Fields
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private Transform parentTabs; // 0x20
	[SerializeField]
	private TextMeshPro textLvMax; // 0x28
	[SerializeField]
	private TextMeshPro textKills; // 0x30
	[SerializeField]
	private ParticleSystem fxBuyVip; // 0x38
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0x40
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0x48
	private Tab_BattlePass[] allTabs; // 0x50
	[SerializeField]
	private Transform parentInfoKills; // 0x58
	[SerializeField]
	private BoxCollider2D boxBound; // 0x60
	[SerializeField]
	private BoxCollider2D boxContent; // 0x68
	[SerializeField]
	private Transform parentView; // 0x70
	[SerializeField]
	private Popup_Notices popupInfo; // 0x78
	[SerializeField]
	private ScrollView scrollViewInfo; // 0x80
	[SerializeField]
	private BoxCollider2D boxContentInfo; // 0x88
	[SerializeField]
	private Transform parentViewInfo; // 0x90
	private bool isAppearBp; // 0x98
	[SerializeField]
	private TextMeshPro textTimeReset; // 0xA0
	private double totalSecs; // 0xA8
	private static int timeUpdate; // 0x4
	public static double timeToReset; // 0x8
	public static double timeToStart; // 0x10
	[SerializeField]
	private SpriteRenderer processRenderer; // 0xB0
	public static int[] allLevelKillsCount; // 0x18
	[SerializeField]
	private GameObject coverRewards; // 0xB8
	[SerializeField]
	private ScrollView scrollView; // 0xC0
	[SerializeField]
	private Transform parentRewards; // 0xC8
	[SerializeField]
	private Sprite[] boxSprites; // 0xD0
	[SerializeField]
	private TextMeshPro textPrice; // 0xD8
	[SerializeField]
	private TextMeshPro textVipPoint; // 0xE0
	private int idProduct; // 0xE8
	private Coroutine checkTimeOut; // 0xF0
	[SerializeField]
	private GameObject loadingObject; // 0xF8
	[SerializeField]
	private Popup_Notices popupConfirmBuy; // 0x100
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x108
	[SerializeField]
	private Popup_Notices popupNoVideo; // 0x110
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x118
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x120
	[SerializeField]
	private GameObject btnBuyBattlePass; // 0x128
	[SerializeField]
	private GameObject textPurchased; // 0x130
	[SerializeField]
	private Popup_PremiumDailyRewards popupPremiumRewards; // 0x138
	[SerializeField]
	private SpriteRenderer[] grayRenderers; // 0x140
	[SerializeField]
	private BoxCollider2D btnGetFreePremium; // 0x148
	[SerializeField]
	private GameObject parentFreePremium; // 0x150

	// Properties
	public static bool IsSeasonOpen { get; set; }
	public static bool IsSeasonClose { get; set; }
	public static int DailyShowPromoIAP { get; set; }
	public static bool IsVipUnlocked { get; set; }
	public static bool IsVipUnlockedForever { get; set; }
	public static int TotalKillsCount { get; set; }
	public static int TotalKillsCountOld { get; set; }
	public static int IndexUnlocked { get; set; }
	public static bool IsBattlePassGetFreePremium { get; set; }

	// Methods

	// RVA: 0x15C7C18 Offset: 0x15C3C18 VA: 0x15C7C18
	public void OnPressedButtonBack() { }

	// RVA: 0x15C7E28 Offset: 0x15C3E28 VA: 0x15C7E28 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x15C7E4C Offset: 0x15C3E4C VA: 0x15C7E4C Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x15C7EC8 Offset: 0x15C3EC8 VA: 0x15C7EC8 Slot: 9
	public override void Escape() { }

	// RVA: 0x15C7F08 Offset: 0x15C3F08 VA: 0x15C7F08
	private void Awake() { }

	// RVA: 0x15C8020 Offset: 0x15C4020 VA: 0x15C8020
	public void OnPressedButtonOpenInfo() { }

	// RVA: 0x15C80CC Offset: 0x15C40CC VA: 0x15C80CC
	private void Start() { }

	// RVA: 0x15C85E4 Offset: 0x15C45E4 VA: 0x15C85E4
	private void OnEnable() { }

	// RVA: 0x15C85E8 Offset: 0x15C45E8 VA: 0x15C85E8
	private void Refresh() { }

	// RVA: 0x15CA310 Offset: 0x15C6310 VA: 0x15CA310
	public static bool hasGet() { }

	// RVA: 0x15C9B60 Offset: 0x15C5B60 VA: 0x15C9B60
	private IEnumerator UpdateTimers() { }

	// RVA: 0x15CA434 Offset: 0x15C6434 VA: 0x15CA434
	public static bool CheckSeasonOpening() { }

	// RVA: 0x15CA508 Offset: 0x15C6508 VA: 0x15CA508
	public static bool get_IsSeasonOpen() { }

	// RVA: 0x15CA848 Offset: 0x15C6848 VA: 0x15CA848
	public static void set_IsSeasonOpen(bool value) { }

	// RVA: 0x15CA6C4 Offset: 0x15C66C4 VA: 0x15CA6C4
	public static bool get_IsSeasonClose() { }

	// RVA: 0x15CA8C4 Offset: 0x15C68C4 VA: 0x15CA8C4
	public static void set_IsSeasonClose(bool value) { }

	// RVA: 0x15CA0D4 Offset: 0x15C60D4 VA: 0x15CA0D4
	public static int get_DailyShowPromoIAP() { }

	// RVA: 0x15CA140 Offset: 0x15C6140 VA: 0x15CA140
	public static void set_DailyShowPromoIAP(int value) { }

	// RVA: 0x15CA940 Offset: 0x15C6940 VA: 0x15CA940
	public static void ClearDatas() { }

	// RVA: 0x15CA9AC Offset: 0x15C69AC VA: 0x15CA9AC
	public static void ResetSeason() { }

	// RVA: 0x15CA7C8 Offset: 0x15C67C8 VA: 0x15CA7C8
	private static void StartSeason() { }

	// RVA: 0x15CA628 Offset: 0x15C6628 VA: 0x15CA628
	public static void CloseSeason() { }

	// RVA: 0x15CA73C Offset: 0x15C673C VA: 0x15CA73C
	public static bool IsSeasonStarted() { }

	// RVA: 0x15CA580 Offset: 0x15C6580 VA: 0x15CA580
	public static bool IsTimeSpecExpired() { }

	// RVA: 0x15CAF48 Offset: 0x15C6F48 VA: 0x15CAF48
	private static int GetLevelBattlePass(int _killCount) { }

	// RVA: 0x15C8F50 Offset: 0x15C4F50 VA: 0x15C8F50
	private void CheckUnlockBattlePass() { }

	// RVA: 0x15C9454 Offset: 0x15C5454 VA: 0x15C9454
	public static bool get_IsVipUnlocked() { }

	// RVA: 0x15CAAA4 Offset: 0x15C6AA4 VA: 0x15CAAA4
	public static void set_IsVipUnlocked(bool value) { }

	// RVA: 0x15CB0E4 Offset: 0x15C70E4 VA: 0x15CB0E4
	public static bool get_IsVipUnlockedForever() { }

	// RVA: 0x15CB15C Offset: 0x15C715C VA: 0x15CB15C
	public static void set_IsVipUnlockedForever(bool value) { }

	// RVA: 0x15CB078 Offset: 0x15C7078 VA: 0x15CB078
	public static int get_TotalKillsCount() { }

	// RVA: 0x15CAB9C Offset: 0x15C6B9C VA: 0x15CAB9C
	public static void set_TotalKillsCount(int value) { }

	// RVA: 0x15CB1D8 Offset: 0x15C71D8 VA: 0x15CB1D8
	public static int get_TotalKillsCountOld() { }

	// RVA: 0x15CAB20 Offset: 0x15C6B20 VA: 0x15CAB20
	public static void set_TotalKillsCountOld(int value) { }

	// RVA: 0x15C93E8 Offset: 0x15C53E8 VA: 0x15C93E8
	public static int get_IndexUnlocked() { }

	// RVA: 0x15CAC18 Offset: 0x15C6C18 VA: 0x15CAC18
	public static void set_IndexUnlocked(int value) { }

	// RVA: 0x15C9658 Offset: 0x15C5658 VA: 0x15C9658
	public static bool IsCollectedFree(int _index) { }

	// RVA: 0x15CADF8 Offset: 0x15C6DF8 VA: 0x15CADF8
	private static void SetCollectedVideoFree(int _index, int _value = 1) { }

	// RVA: 0x15C9500 Offset: 0x15C5500 VA: 0x15C9500
	public static bool IsCollectedVideoFree(int _index) { }

	// RVA: 0x15CAD50 Offset: 0x15C6D50 VA: 0x15CAD50
	private static void SetCollectedFree(int _index, int _value = 1) { }

	// RVA: 0x15C95AC Offset: 0x15C55AC VA: 0x15C95AC
	public static bool IsCollectedVip(int _index) { }

	// RVA: 0x15CAEA0 Offset: 0x15C6EA0 VA: 0x15CAEA0
	private static void SetCollectedVip(int _index, int _value = 1) { }

	// RVA: 0x15CB244 Offset: 0x15C7244 VA: 0x15CB244
	private void OnClickFree(int _index) { }

	// RVA: 0x15CBAB4 Offset: 0x15C7AB4 VA: 0x15CBAB4
	private void OnClickVip(int _index) { }

	// RVA: 0x15CB5A4 Offset: 0x15C75A4 VA: 0x15CB5A4
	private void CollectAll(int _indexTab, int _indexPack, int _multiple = 1, bool _isVideo = False) { }

	// RVA: 0x15CC7D8 Offset: 0x15C87D8 VA: 0x15CC7D8
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x15CC83C Offset: 0x15C883C VA: 0x15CC83C
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x15C9704 Offset: 0x15C5704 VA: 0x15C9704
	private void SetTabInfo(ref Box_Rewards _box, Shop_Pack _pack, int _index) { }

	// RVA: 0x15C9BC8 Offset: 0x15C5BC8 VA: 0x15C9BC8
	private IEnumerator SetShopPrices() { }

	// RVA: 0x15CCCD8 Offset: 0x15C8CD8 VA: 0x15CCCD8
	private void OnInitialized() { }

	// RVA: 0x15CCEF0 Offset: 0x15C8EF0 VA: 0x15CCEF0
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x15CCF58 Offset: 0x15C8F58 VA: 0x15CCF58
	public void OnBuy() { }

	// RVA: 0x15CD15C Offset: 0x15C915C VA: 0x15CD15C
	private void Purchase(int _id, Action<int, bool> _callback) { }

	// RVA: 0x15CD244 Offset: 0x15C9244 VA: 0x15CD244
	private void OnPurchased(int _idProduct, bool _successed) { }

	// RVA: 0x15CA1B0 Offset: 0x15C61B0 VA: 0x15CA1B0
	public void OnPressedButtonBuyBattlePass() { }

	// RVA: 0x15CD4D4 Offset: 0x15C94D4 VA: 0x15CD4D4
	public void OnPressedButtonGetPremiumFree() { }

	// RVA: 0x15CD608 Offset: 0x15C9608 VA: 0x15CD608
	public static bool get_IsBattlePassGetFreePremium() { }

	// RVA: 0x15CD680 Offset: 0x15C9680 VA: 0x15CD680
	public static void set_IsBattlePassGetFreePremium(bool value) { }

	// RVA: 0x15C9C30 Offset: 0x15C5C30 VA: 0x15C9C30
	private void SetPremiumBonusStates() { }

	// RVA: 0x15CD6FC Offset: 0x15C96FC VA: 0x15CD6FC
	public void .ctor() { }

	// RVA: 0x15CD70C Offset: 0x15C970C VA: 0x15CD70C
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x15CD7C0 Offset: 0x15C97C0 VA: 0x15CD7C0
	private void <OnPressedButtonOpenInfo>b__21_0() { }

	[CompilerGenerated]
	// RVA: 0x15CBBB4 Offset: 0x15C7BB4 VA: 0x15CBBB4
	private void <CollectAll>g__SetCollected|76_0(int _t, int _p, int _m, bool _v) { }

	[CompilerGenerated]
	// RVA: 0x15CBFD8 Offset: 0x15C7FD8 VA: 0x15CBFD8
	private void <CollectAll>g__SetCollectRewards|76_1(Shop_Pack _pack, ref int _box, string _strBonus) { }

	[CompilerGenerated]
	// RVA: 0x15CD7E0 Offset: 0x15C97E0 VA: 0x15CD7E0
	private void <CheckLoadingTimeOut>b__91_0() { }

	[CompilerGenerated]
	// RVA: 0x15CD800 Offset: 0x15C9800 VA: 0x15CD800
	private void <OnBuy>b__96_0() { }

	[CompilerGenerated]
	// RVA: 0x15CD820 Offset: 0x15C9820 VA: 0x15CD820
	private void <OnBuy>b__96_1() { }

	[CompilerGenerated]
	// RVA: 0x15CD840 Offset: 0x15C9840 VA: 0x15CD840
	private void <OnPurchased>b__99_0() { }

	[CompilerGenerated]
	// RVA: 0x15CD8DC Offset: 0x15C98DC VA: 0x15CD8DC
	private void <OnPressedButtonBuyBattlePass>b__102_0() { }

	[CompilerGenerated]
	// RVA: 0x15CD908 Offset: 0x15C9908 VA: 0x15CD908
	private void <OnPressedButtonBuyBattlePass>b__102_1() { }

	[CompilerGenerated]
	// RVA: 0x15CD928 Offset: 0x15C9928 VA: 0x15CD928
	private void <OnPressedButtonGetPremiumFree>b__103_0() { }
}


// ===== keywords: Battle, Pass
// Namespace: 
public class Board_BattlePassPro : Board // TypeDefIndex: 488
{
	// Fields
	private static int MaxLevel; // 0x0
	private static int[] allCoinPoints; // 0x8
	private static int[] allGemPoints; // 0x10
	public static BoardID backBoard; // 0x18
	public static int currentTab; // 0x1C
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0x20
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0x28
	[SerializeField]
	private ScrollView scrollView; // 0x30
	[SerializeField]
	private BoxCollider2D boxBound; // 0x38
	[SerializeField]
	private BoxCollider2D boxContent; // 0x40
	[SerializeField]
	private Transform parentView; // 0x48
	[SerializeField]
	private Transform parentTabs; // 0x50
	[SerializeField]
	private Align parentTabAlign; // 0x58
	[SerializeField]
	private float heightShipPack; // 0x60
	[SerializeField]
	private Transform parentShipPack; // 0x68
	[SerializeField]
	private Transform levelShipPack; // 0x70
	private Tab_BattlePassPro[] allTabs; // 0x78
	[SerializeField]
	private Popup_Notices popupInfo; // 0x80
	[SerializeField]
	private ScrollView scrollViewInfo; // 0x88
	[SerializeField]
	private BoxCollider2D boxContentInfo; // 0x90
	[SerializeField]
	private Transform parentViewInfo; // 0x98
	[SerializeField]
	private Transform parentInfoKills; // 0xA0
	[SerializeField]
	private GameObject parentBattlePass; // 0xA8
	[SerializeField]
	private GameObject parentMissions; // 0xB0
	[SerializeField]
	private GameObject[] coverTabButton; // 0xB8
	[SerializeField]
	private Transform parentTabDailyMissions; // 0xC0
	[SerializeField]
	private Transform parentTabWeekMissions; // 0xC8
	[SerializeField]
	private Align alignTabDailyMissions; // 0xD0
	[SerializeField]
	private Align alignTabWeekMissions; // 0xD8
	[SerializeField]
	private Transform headerDaily; // 0xE0
	[SerializeField]
	private Transform headerWeek; // 0xE8
	[SerializeField]
	private Transform headerIAP; // 0xF0
	[SerializeField]
	private TextMeshPro textTimeDaily; // 0xF8
	[SerializeField]
	private TextMeshPro textTimeWeek; // 0x100
	private static string KeyWeekTime; // 0x20
	[SerializeField]
	private Sprite[] allTalents; // 0x108
	[SerializeField]
	private GameObject focusBPMission; // 0x110
	[SerializeField]
	private GameObject focusBPLevel; // 0x118
	[SerializeField]
	private Tab_BattlePassMission tabSpecMission; // 0x120
	[SerializeField]
	private Sprite iconIAP; // 0x128
	[SerializeField]
	private Color[] colorBgProcess; // 0x130
	[SerializeField]
	private Sprite[] bgSprites; // 0x138
	[SerializeField]
	private Popup_ChangeMissions popupChangeMissions; // 0x140
	[SerializeField]
	private Popup_Notices popupResuftChange; // 0x148
	[SerializeField]
	private TextMeshPro textResuftChange; // 0x150
	[SerializeField]
	private GameObject btnUp; // 0x158
	[SerializeField]
	private GameObject btnDown; // 0x160
	private Coroutine updateButton; // 0x168
	public static int idShipReward; // 0x28
	[SerializeField]
	private Sprite[] allShipPilots; // 0x170
	[SerializeField]
	private Popup_Notices popupChangeRewards; // 0x178
	[SerializeField]
	private Box_Rewards[] allBonus; // 0x180
	[SerializeField]
	private Popup_BattlePassLevelUp popupBattlePassLevelUp; // 0x188
	private Popup_NewPlayer popup_NewPlayerObj; // 0x190
	private int[] allIndexMissions; // 0x198
	private static int[] allValueMissions; // 0x30
	private static int[] allPointMissions; // 0x38
	private bool isAppearBp; // 0x1A0
	[SerializeField]
	private ParticleSystem fxBuyVip; // 0x1A8
	[SerializeField]
	private Transform parentRewards; // 0x1B0
	[SerializeField]
	private GameObject coverRewards; // 0x1B8
	[SerializeField]
	private TextMeshPro textTimeReset; // 0x1C0
	private double totalSecs; // 0x1C8
	private static int timeUpdate; // 0x40
	public static double timeToReset; // 0x48
	public static double timeToStart; // 0x50
	[SerializeField]
	private TextMeshPro textProcess; // 0x1D0
	[SerializeField]
	private TextMeshPro textBPLevel; // 0x1D8
	[SerializeField]
	private TextMeshPro textPurchased; // 0x1E0
	private static int NumberDailyMissions; // 0x58
	private static int NumberWeekMissions; // 0x5C
	[SerializeField]
	private Popup_Notices popupBuyBattlePass; // 0x1E8
	[SerializeField]
	private Popup_Notices popupNoVideo; // 0x1F0
	[SerializeField]
	private GameObject loadingObject; // 0x1F8
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x200
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x208
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x210
	[SerializeField]
	private TextMeshPro textPrice; // 0x218
	[SerializeField]
	private TextMeshPro textVipPoint; // 0x220
	private int productIdBattlePassPack; // 0x228
	private Coroutine checkTimeOut; // 0x230

	// Properties
	public static int WeekCount { get; set; }
	public static int StateClaimShip { get; set; }
	private Popup_NewPlayer popup_NewPlayer { get; }
	public static bool IsBoughtBattlePassVipPack { get; set; }
	public static int CurrentBattlePassPoints { get; set; }
	public static int SavedBattlePassPoints { get; set; }
	public static int CurrentLevel { get; set; }
	public static bool IsOpenTime { get; set; }
	public static bool IsPreTime { get; set; }
	public static bool IsShowVipPack { get; set; }

	// Methods

	// RVA: 0x15CE780 Offset: 0x15CA780 VA: 0x15CE780
	public static Shop_Pack GetBPRewards(int index, bool isFree) { }

	// RVA: 0x15CE908 Offset: 0x15CA908 VA: 0x15CE908
	public void OnPressedButtonBack() { }

	// RVA: 0x15CE9EC Offset: 0x15CA9EC VA: 0x15CE9EC Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x15CFE74 Offset: 0x15CBE74 VA: 0x15CFE74
	public void OnPressedButtonOpenInfo() { }

	// RVA: 0x15CFF20 Offset: 0x15CBF20 VA: 0x15CFF20
	private void Start() { }

	// RVA: 0x15D05A8 Offset: 0x15CC5A8 VA: 0x15D05A8
	public void OnDisable() { }

	// RVA: 0x15D05B4 Offset: 0x15CC5B4 VA: 0x15D05B4 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x15D0630 Offset: 0x15CC630 VA: 0x15D0630 Slot: 9
	public override void Escape() { }

	// RVA: 0x15D0634 Offset: 0x15CC634 VA: 0x15D0634
	public void OnPressedButtonTab(int index) { }

	// RVA: 0x15D06D0 Offset: 0x15CC6D0 VA: 0x15D06D0
	public void OnPressedButtonFocusBattlePassScrView() { }

	// RVA: 0x15CFA68 Offset: 0x15CBA68 VA: 0x15CFA68
	private void CheckTab() { }

	// RVA: 0x15D0DF8 Offset: 0x15CCDF8 VA: 0x15D0DF8
	public static void CheckDailyReset() { }

	// RVA: 0x15CEAD8 Offset: 0x15CAAD8 VA: 0x15CEAD8
	public static int get_WeekCount() { }

	// RVA: 0x15CEB44 Offset: 0x15CAB44 VA: 0x15CEB44
	public static void set_WeekCount(int value) { }

	// RVA: 0x15CFE14 Offset: 0x15CBE14 VA: 0x15CFE14
	private IEnumerator IECheckTime() { }

	// RVA: 0x15D09A8 Offset: 0x15CC9A8 VA: 0x15D09A8
	private void SetTabMissions() { }

	// RVA: 0x15D2708 Offset: 0x15CE708 VA: 0x15D2708
	private void OnChange(int index, int reward, Sprite boxSpr, Sprite iconSpr) { }

	// RVA: 0x15D290C Offset: 0x15CE90C VA: 0x15D290C
	private int GetCostChange(int index, int reward) { }

	// RVA: 0x15D0E90 Offset: 0x15CCE90 VA: 0x15D0E90
	public static bool IsLevelUp() { }

	// RVA: 0x15D2A50 Offset: 0x15CEA50 VA: 0x15D2A50
	public static bool IsHasMissionDone() { }

	// RVA: 0x15D2ED8 Offset: 0x15CEED8 VA: 0x15D2ED8
	public static int get_StateClaimShip() { }

	// RVA: 0x15D2F44 Offset: 0x15CEF44 VA: 0x15D2F44
	public static void set_StateClaimShip(int value) { }

	// RVA: 0x15D2FB4 Offset: 0x15CEFB4 VA: 0x15D2FB4
	private void CheckShipReward() { }

	// RVA: 0x15D0948 Offset: 0x15CC948 VA: 0x15D0948
	private IEnumerator IECheckScrollViewPositions() { }

	// RVA: 0x15D3644 Offset: 0x15CF644 VA: 0x15D3644
	private Popup_NewPlayer get_popup_NewPlayer() { }

	// RVA: 0x15D088C Offset: 0x15CC88C VA: 0x15D088C
	private void SetTabBattlePass() { }

	// RVA: 0x15D3EE0 Offset: 0x15CFEE0 VA: 0x15D3EE0
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x15D3F44 Offset: 0x15CFF44 VA: 0x15D3F44
	private void CollectAll(int _indexTab, int _indexPack, int _multiple = 1, bool _isVideo = False) { }

	// RVA: 0x15D53D8 Offset: 0x15D13D8 VA: 0x15D53D8
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x15D5874 Offset: 0x15D1874 VA: 0x15D5874
	public void OnPressedButtonBuyBattlePass() { }

	// RVA: 0x15CFD54 Offset: 0x15CBD54 VA: 0x15CFD54
	private IEnumerator IEUpdateTimers() { }

	// RVA: 0x15D03F4 Offset: 0x15CC3F4 VA: 0x15D03F4
	private static int GetLevelUpPoints(int index) { }

	// RVA: 0x15D3784 Offset: 0x15CF784 VA: 0x15D3784
	private void CheckUnlockBattlePass() { }

	// RVA: 0x15CEBB4 Offset: 0x15CABB4 VA: 0x15CEBB4
	public static void ResetDailyMissions() { }

	// RVA: 0x15D5C48 Offset: 0x15D1C48 VA: 0x15D5C48
	public static bool ResetMission(int index) { }

	// RVA: 0x15CF23C Offset: 0x15CB23C VA: 0x15CF23C
	public static void ResetWeekMissions() { }

	// RVA: 0x15CF9D4 Offset: 0x15CB9D4 VA: 0x15CF9D4
	public static void ResetIAPMissions() { }

	// RVA: 0x15D0EF4 Offset: 0x15CCEF4 VA: 0x15D0EF4
	public static Board_BattlePassPro.BattlePassMission GetMissionInfo(int index) { }

	// RVA: 0x15D5A68 Offset: 0x15D1A68 VA: 0x15D5A68
	public static void SetMissionInfo(int index, Board_BattlePassPro.BattlePassMission mission) { }

	// RVA: 0x15D2C64 Offset: 0x15CEC64 VA: 0x15D2C64
	public static bool get_IsBoughtBattlePassVipPack() { }

	// RVA: 0x15D63DC Offset: 0x15D23DC VA: 0x15D63DC
	public static void set_IsBoughtBattlePassVipPack(bool value) { }

	// RVA: 0x15D0820 Offset: 0x15CC820 VA: 0x15D0820
	public static int get_CurrentBattlePassPoints() { }

	// RVA: 0x15D6458 Offset: 0x15D2458 VA: 0x15D6458
	public static void set_CurrentBattlePassPoints(int value) { }

	// RVA: 0x15D64D4 Offset: 0x15D24D4 VA: 0x15D64D4
	public static int get_SavedBattlePassPoints() { }

	// RVA: 0x15D6540 Offset: 0x15D2540 VA: 0x15D6540
	public static void set_SavedBattlePassPoints(int value) { }

	// RVA: 0x15D07B4 Offset: 0x15CC7B4 VA: 0x15D07B4
	public static int get_CurrentLevel() { }

	// RVA: 0x15D4870 Offset: 0x15D0870 VA: 0x15D4870
	public static void set_CurrentLevel(int value) { }

	// RVA: 0x15D49D4 Offset: 0x15D09D4 VA: 0x15D49D4
	public static bool IsCollectedFree(int _index) { }

	// RVA: 0x15D6664 Offset: 0x15D2664 VA: 0x15D6664
	private static void SetCollectedVideoFree(int _index, int _value = 1) { }

	// RVA: 0x15D4A80 Offset: 0x15D0A80 VA: 0x15D4A80
	public static bool IsCollectedVideoFree(int _index) { }

	// RVA: 0x15D65BC Offset: 0x15D25BC VA: 0x15D65BC
	private static void SetCollectedFree(int _index, int _value = 1) { }

	// RVA: 0x15D4B2C Offset: 0x15D0B2C VA: 0x15D4B2C
	public static bool IsCollectedVip(int _index) { }

	// RVA: 0x15D670C Offset: 0x15D270C VA: 0x15D670C
	private static void SetCollectedVip(int _index, int _value = 1) { }

	// RVA: 0x15D67B4 Offset: 0x15D27B4 VA: 0x15D67B4
	public static void SetKillCount(int idShip, int killCount) { }

	// RVA: 0x15D6978 Offset: 0x15D2978 VA: 0x15D6978
	public static void SetDroneSkillLaunchCount(int idDrone, int count) { }

	// RVA: 0x15D6B3C Offset: 0x15D2B3C VA: 0x15D6B3C
	public static void SetTalentLaunchCount(int idTalent, int count) { }

	// RVA: 0x15D6D34 Offset: 0x15D2D34 VA: 0x15D6D34
	public static void SetIAPCount() { }

	// RVA: 0x15D6DEC Offset: 0x15D2DEC VA: 0x15D6DEC
	public static bool CheckSeasonOpening() { }

	// RVA: 0x15D6EC0 Offset: 0x15D2EC0 VA: 0x15D6EC0
	public static bool get_IsOpenTime() { }

	// RVA: 0x15D7200 Offset: 0x15D3200 VA: 0x15D7200
	public static void set_IsOpenTime(bool value) { }

	// RVA: 0x15D707C Offset: 0x15D307C VA: 0x15D707C
	public static bool get_IsPreTime() { }

	// RVA: 0x15D727C Offset: 0x15D327C VA: 0x15D727C
	public static void set_IsPreTime(bool value) { }

	// RVA: 0x15D72F8 Offset: 0x15D32F8 VA: 0x15D72F8
	public static bool get_IsShowVipPack() { }

	// RVA: 0x15D7370 Offset: 0x15D3370 VA: 0x15D7370
	public static void set_IsShowVipPack(bool value) { }

	// RVA: 0x15D73EC Offset: 0x15D33EC VA: 0x15D73EC
	public static void ClearDatas() { }

	// RVA: 0x15D7450 Offset: 0x15D3450 VA: 0x15D7450
	public static void ResetSeason() { }

	// RVA: 0x15D7180 Offset: 0x15D3180 VA: 0x15D7180
	private static void StartSeason() { }

	// RVA: 0x15D6FE0 Offset: 0x15D2FE0 VA: 0x15D6FE0
	public static void CloseSeason() { }

	// RVA: 0x15D70F4 Offset: 0x15D30F4 VA: 0x15D70F4
	public static bool IsSeasonStarted() { }

	// RVA: 0x15D6F38 Offset: 0x15D2F38 VA: 0x15D6F38
	public static bool IsTimeSpecExpired() { }

	// RVA: 0x15D2930 Offset: 0x15CE930 VA: 0x15D2930
	public static int GetLevelBattlePass(int _killCount) { }

	// RVA: 0x15CFDB4 Offset: 0x15CBDB4 VA: 0x15CFDB4
	private IEnumerator IESetPrices() { }

	// RVA: 0x15D7580 Offset: 0x15D3580 VA: 0x15D7580
	private void OnBuyBattlePass() { }

	// RVA: 0x15D78D0 Offset: 0x15D38D0 VA: 0x15D78D0
	public void .ctor() { }

	// RVA: 0x15D7964 Offset: 0x15D3964 VA: 0x15D7964
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x15D7B1C Offset: 0x15D3B1C VA: 0x15D7B1C
	private void <OnPressedButtonOpenInfo>b__25_0() { }

	[CompilerGenerated]
	// RVA: 0x15D2410 Offset: 0x15CE410 VA: 0x15D2410
	private void <SetTabMissions>g__SetScrollViewContentSize|58_0() { }

	[CompilerGenerated]
	// RVA: 0x15D1110 Offset: 0x15CD110 VA: 0x15D1110
	private void <SetTabMissions>g__SetTabMission|58_1(Tab_BattlePassMission tab, Board_BattlePassPro.BattlePassMission mission) { }

	[CompilerGenerated]
	// RVA: 0x15D7B3C Offset: 0x15D3B3C VA: 0x15D7B3C
	private void <SetTabMissions>b__58_2(int _index, int _reward) { }

	[CompilerGenerated]
	// RVA: 0x15D7EA0 Offset: 0x15D3EA0 VA: 0x15D7EA0
	private void <SetTabMissions>b__58_3(int _index, int _reward) { }

	[CompilerGenerated]
	// RVA: 0x15D7FA4 Offset: 0x15D3FA4 VA: 0x15D7FA4
	private void <SetTabMissions>b__58_4(int _index, int _reward) { }

	[CompilerGenerated]
	// RVA: 0x15D2CDC Offset: 0x15CECDC VA: 0x15D2CDC
	internal static int <IsHasMissionDone>g__GetValue|65_0(int _index, int _type) { }

	[CompilerGenerated]
	// RVA: 0x15D3C4C Offset: 0x15CFC4C VA: 0x15D3C4C
	private void <SetTabBattlePass>g__SetRewardInfo|86_0() { }

	[CompilerGenerated]
	// RVA: 0x15D85C8 Offset: 0x15D45C8 VA: 0x15D85C8
	private void <SetTabBattlePass>g__SetScrollViewContentSize|86_1() { }

	[CompilerGenerated]
	// RVA: 0x15D7FA8 Offset: 0x15D3FA8 VA: 0x15D7FA8
	private void <SetTabBattlePass>g__SetTabRewards|86_2(int _index, Tab_BattlePassPro _tab, ref Board_BattlePassPro.<>c__DisplayClass86_0 ) { }

	[CompilerGenerated]
	// RVA: 0x15D9000 Offset: 0x15D5000 VA: 0x15D9000
	private void <SetTabBattlePass>g__OnClickFree|86_3(int _index) { }

	[CompilerGenerated]
	// RVA: 0x15D93A8 Offset: 0x15D53A8 VA: 0x15D93A8
	private void <SetTabBattlePass>b__86_8() { }

	[CompilerGenerated]
	// RVA: 0x15D93C8 Offset: 0x15D53C8 VA: 0x15D93C8
	private void <SetTabBattlePass>g__OnClickVip|86_4(int _index) { }

	[CompilerGenerated]
	// RVA: 0x15D8AEC Offset: 0x15D4AEC VA: 0x15D8AEC
	internal static void <SetTabBattlePass>g__SetTabInfo|86_5(ref Box_Rewards _box, Shop_Pack _pack) { }

	[CompilerGenerated]
	// RVA: 0x15D444C Offset: 0x15D044C VA: 0x15D444C
	private void <CollectAll>g__SetCollected|91_0(int _t, int _p, int _m, bool _v) { }

	[CompilerGenerated]
	// RVA: 0x15D4BD8 Offset: 0x15D0BD8 VA: 0x15D4BD8
	private void <CollectAll>g__SetCollectRewards|91_1(Shop_Pack _pack, ref int _box, string _strBonus) { }

	[CompilerGenerated]
	// RVA: 0x15D9504 Offset: 0x15D5504 VA: 0x15D9504
	private void <OnPressedButtonBuyBattlePass>b__93_0() { }

	[CompilerGenerated]
	// RVA: 0x15D9530 Offset: 0x15D5530 VA: 0x15D9530
	private void <OnPressedButtonBuyBattlePass>b__93_1() { }

	[CompilerGenerated]
	// RVA: 0x15D9550 Offset: 0x15D5550 VA: 0x15D9550
	private void <IESetPrices>g__OnInitialized|163_1() { }

	[CompilerGenerated]
	// RVA: 0x15D9768 Offset: 0x15D5768 VA: 0x15D9768
	private void <OnBuyBattlePass>b__164_0() { }

	[CompilerGenerated]
	// RVA: 0x15D9788 Offset: 0x15D5788 VA: 0x15D9788
	private void <OnBuyBattlePass>b__164_1() { }

	[CompilerGenerated]
	// RVA: 0x15D7784 Offset: 0x15D3784 VA: 0x15D7784
	private IEnumerator <OnBuyBattlePass>g__IECheckLoadingTimeOut|164_2() { }

	[CompilerGenerated]
	// RVA: 0x15D97D0 Offset: 0x15D57D0 VA: 0x15D97D0
	private void <OnBuyBattlePass>b__164_5() { }

	[CompilerGenerated]
	// RVA: 0x15D77E4 Offset: 0x15D37E4 VA: 0x15D77E4
	private void <OnBuyBattlePass>g__Purchase|164_3(int _id, Action<int, bool> _callback) { }

	[CompilerGenerated]
	// RVA: 0x15D97F8 Offset: 0x15D57F8 VA: 0x15D97F8
	private void <OnBuyBattlePass>g__OnPurchased|164_4(int _idProduct, bool _successed) { }

	[CompilerGenerated]
	// RVA: 0x15D9A88 Offset: 0x15D5A88 VA: 0x15D9A88
	private void <OnBuyBattlePass>b__164_7() { }
}


// ===== keywords: Reward, Quest
// Namespace: 
public class Board_QuestRewards : Board // TypeDefIndex: 930
{
	// Fields
	public static int typeBox; // 0x0
	[SerializeField]
	private GameObject[] allBoxes; // 0x20
	[SerializeField]
	private Transform[] allBtnOpen; // 0x28
	[SerializeField]
	private Animator[] boxAnimators; // 0x30
	[SerializeField]
	private TextMeshPro textLabelBtnOpenNow; // 0x38
	[SerializeField]
	private TextMeshPro textLabelBtnOpenNow2; // 0x40
	[SerializeField]
	private TextMeshPro textLabelOpenFree; // 0x48
	[SerializeField]
	private TextMeshPro textTimeOpenFree; // 0x50
	[SerializeField]
	private TextMeshPro textKeyCount; // 0x58
	[SerializeField]
	private GameObject skipVideo; // 0x60
	[SerializeField]
	private GameObject skipVideo2; // 0x68
	[SerializeField]
	private Popup_Notices popupBuyKeys; // 0x70
	[SerializeField]
	private TextMeshPro textPriceKeys; // 0x78
	[SerializeField]
	private Box_Rewards boxKeyBuy; // 0x80
	private bool isVideoReady; // 0x88
	[SerializeField]
	private GameObject loadingObject; // 0x90
	private GameObject m_popupPremium; // 0x98
	[SerializeField]
	private Popup_Notices popupNoGems; // 0xA0
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0xA8
	[SerializeField]
	private Popup_Notices popupNoVideo; // 0xB0
	[SerializeField]
	private GameObject btnCollect; // 0xB8
	[SerializeField]
	private GameObject btnBonusWatchAds; // 0xC0
	private Dictionary<int, Sprite> allDeviceIcons; // 0xC8
	private bool isOpening; // 0xD0
	protected bool isBonus; // 0xD1
	private Coroutine openCoroutine; // 0xD8
	[SerializeField]
	private GameObject coverRewards; // 0xE0
	[SerializeField]
	private Transform listRewards; // 0xE8
	[SerializeField]
	private GameObject coverUi; // 0xF0
	private int vipPointsReward; // 0xF8
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x100
	[SerializeField]
	private SpriteRenderer btnFreeRenderer; // 0x108
	private bool isTimeOk; // 0x110
	private double totalSecs; // 0x118
	private static int timeUpdate; // 0x4
	private GameObject focusVideo; // 0x120
	private GameObject focusOpen; // 0x128

	// Properties
	private GameObject popupPremium { get; }

	// Methods

	// RVA: 0x130EE7C Offset: 0x130AE7C VA: 0x130EE7C
	private void Awake() { }

	// RVA: 0x130EFA4 Offset: 0x130AFA4 VA: 0x130EFA4
	private void OnEnable() { }

	// RVA: 0x130F4A8 Offset: 0x130B4A8 VA: 0x130F4A8 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x130FDFC Offset: 0x130BDFC VA: 0x130FDFC Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x130FE20 Offset: 0x130BE20 VA: 0x130FE20 Slot: 9
	public override void Escape() { }

	// RVA: 0x130FE7C Offset: 0x130BE7C VA: 0x130FE7C
	public void OnPressedButtonBack() { }

	// RVA: 0x1310278 Offset: 0x130C278 VA: 0x1310278
	public void OnPressedButtonOpenNow() { }

	// RVA: 0x1310A5C Offset: 0x130CA5C VA: 0x1310A5C
	public void OnPressedButtonOpenFree() { }

	// RVA: 0x1310F4C Offset: 0x130CF4C VA: 0x1310F4C
	public void OnPressedButtonBonusWatchAds() { }

	// RVA: 0x1310E50 Offset: 0x130CE50 VA: 0x1310E50
	private GameObject get_popupPremium() { }

	// RVA: 0x130FFD0 Offset: 0x130BFD0 VA: 0x130FFD0
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x1310A24 Offset: 0x130CA24 VA: 0x1310A24
	private void OpenBoxNow() { }

	// RVA: 0x130F28C Offset: 0x130B28C VA: 0x130F28C
	private void SetButtonStates() { }

	// RVA: 0x1310FF8 Offset: 0x130CFF8 VA: 0x1310FF8
	private IEnumerator OpenBox() { }

	// RVA: 0x1311080 Offset: 0x130D080 VA: 0x1311080
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x130F088 Offset: 0x130B088 VA: 0x130F088
	private bool IsVideoLoaded() { }

	// RVA: 0x1310DA4 Offset: 0x130CDA4 VA: 0x1310DA4
	private void UpdateStateButton() { }

	// RVA: 0x130F22C Offset: 0x130B22C VA: 0x130F22C
	private IEnumerator AdsTimer() { }

	// RVA: 0x130F0D8 Offset: 0x130B0D8 VA: 0x130F0D8
	private bool IsTimeAdsReady() { }

	// RVA: 0x130F5DC Offset: 0x130B5DC VA: 0x130F5DC
	private void ResfreshRewards() { }

	// RVA: 0x1311524 Offset: 0x130D524 VA: 0x1311524
	public void .ctor() { }

	// RVA: 0x13115A8 Offset: 0x130D5A8 VA: 0x13115A8
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x13115F8 Offset: 0x130D5F8 VA: 0x13115F8
	private void <OnPressedButtonOpenFree>b__23_0(bool b) { }

	[CompilerGenerated]
	// RVA: 0x13116B4 Offset: 0x130D6B4 VA: 0x13116B4
	private void <OnPressedButtonBonusWatchAds>b__24_0(bool b) { }

	[CompilerGenerated]
	// RVA: 0x13116C4 Offset: 0x130D6C4 VA: 0x13116C4
	private void <OnPressedButtonExitRewardCover>b__28_0() { }
}


// ===== keywords: Shop, Coin
// Namespace: 
public class Board_ShopCoins : Board // TypeDefIndex: 1106
{
	// Fields
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private Transform parentCells; // 0x20
	[SerializeField]
	private Transform parentIAPCells; // 0x28
	private Shop_Cell[] allShopcells; // 0x30
	private Shop_Cell[] allShopIAPCells; // 0x38
	[SerializeField]
	private Sprite[] listSprites; // 0x40
	[SerializeField]
	private Popup_Notices popupNoGems; // 0x48
	[SerializeField]
	private ScrollView scrollView; // 0x50
	[SerializeField]
	private BoxCollider2D boxBound; // 0x58
	[SerializeField]
	private BoxCollider2D boxContent; // 0x60
	public static float[] allCosts; // 0x8
	public static float[] allValues; // 0x10
	public static float[] allIAPValues; // 0x18
	public static int lvBigSale; // 0x20
	[SerializeField]
	private Transform parentView; // 0x68
	private int startIndexIAP; // 0x70
	[SerializeField]
	private GameObject bigSaleCoins; // 0x78
	[SerializeField]
	private TextMeshPro textBonusCoins; // 0x80
	private bool videoActived; // 0x88
	private int cellID; // 0x8C
	private Coroutine checkTimeOut; // 0x90
	[SerializeField]
	private Popup_Notices popupNetworkNotConnected; // 0x98
	[SerializeField]
	private Popup_Notices popupInitialize; // 0xA0
	[SerializeField]
	private Popup_Notices popupReachVip; // 0xA8
	[SerializeField]
	private GameObject loadingObject; // 0xB0

	// Methods

	// RVA: 0x1379A88 Offset: 0x1375A88 VA: 0x1379A88
	private void Awake() { }

	// RVA: 0x1379BC0 Offset: 0x1375BC0 VA: 0x1379BC0
	private string GetShortNumber(int number) { }

	// RVA: 0x1379CAC Offset: 0x1375CAC VA: 0x1379CAC
	private void OnEnable() { }

	// RVA: 0x1379CB0 Offset: 0x1375CB0 VA: 0x1379CB0
	private void Refresh() { }

	// RVA: 0x137A63C Offset: 0x137663C VA: 0x137A63C
	private IEnumerator IECheckVideoActiveEffect() { }

	// RVA: 0x137A6A4 Offset: 0x13766A4 VA: 0x137A6A4 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x137A6C8 Offset: 0x13766C8 VA: 0x137A6C8 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x137A6EC Offset: 0x13766EC VA: 0x137A6EC Slot: 9
	public override void Escape() { }

	// RVA: 0x137A6F0 Offset: 0x13766F0 VA: 0x137A6F0
	public void OnPressedButtonBack() { }

	// RVA: 0x137A744 Offset: 0x1376744 VA: 0x137A744
	private void OnClickPurchaseIAPPacks(Shop_Cell _cell) { }

	// RVA: 0x137AA00 Offset: 0x1376A00 VA: 0x137AA00
	private void CheckPopup() { }

	// RVA: 0x137A91C Offset: 0x137691C VA: 0x137A91C
	private void Purchase(int _id, Action<bool> _callback) { }

	// RVA: 0x137AB04 Offset: 0x1376B04 VA: 0x137AB04
	private void OnPurchased(bool _successed) { }

	// RVA: 0x137AF2C Offset: 0x1376F2C VA: 0x137AF2C
	private void OnClickBuy(Shop_Cell _cell) { }

	// RVA: 0x137A5D4 Offset: 0x13765D4 VA: 0x137A5D4
	private IEnumerator SetShopPrices() { }

	// RVA: 0x137B250 Offset: 0x1377250 VA: 0x137B250
	private void OnInitialized() { }

	// RVA: 0x137A8BC Offset: 0x13768BC VA: 0x137A8BC
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x137B3C8 Offset: 0x13773C8 VA: 0x137B3C8
	public void .ctor() { }

	// RVA: 0x137B3E0 Offset: 0x13773E0 VA: 0x137B3E0
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x137B508 Offset: 0x1377508 VA: 0x137B508
	private void <CheckPopup>b__30_0() { }

	[CompilerGenerated]
	// RVA: 0x137B528 Offset: 0x1377528 VA: 0x137B528
	private void <CheckPopup>b__30_1() { }

	[CompilerGenerated]
	// RVA: 0x137B548 Offset: 0x1377548 VA: 0x137B548
	private void <OnPurchased>b__32_0() { }

	[CompilerGenerated]
	// RVA: 0x137B5F4 Offset: 0x13775F4 VA: 0x137B5F4
	private void <OnClickBuy>b__33_0() { }

	[CompilerGenerated]
	// RVA: 0x137B614 Offset: 0x1377614 VA: 0x137B614
	private void <CheckLoadingTimeOut>b__41_0() { }
}


// ===== keywords: Shop, Energy
// Namespace: 
public class Board_ShopEnergy : Board // TypeDefIndex: 683
{
	// Fields
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private Popup_Notices popupNoGems; // 0x20
	[SerializeField]
	private TextMeshPro textValueBuyEnergy; // 0x28
	[SerializeField]
	private TextMeshPro textValueFreeEnergy; // 0x30
	[SerializeField]
	private TextMeshPro textCostBuyEnergy; // 0x38
	[SerializeField]
	private TextMeshPro textTimeAds; // 0x40
	[SerializeField]
	private Premium_Pack premiumPackScript; // 0x48
	[SerializeField]
	private GameObject popupVideoNotReady; // 0x50
	[SerializeField]
	private GameObject popupNoInternet; // 0x58
	private double totalSecs; // 0x60
	private const string keySysTime = "TimeFreeEnergy";
	private static int timeUpdate; // 0x4
	private double timeAds; // 0x68
	[SerializeField]
	private GameObject coverAds; // 0x70
	private Coroutine adsCoroutine; // 0x78

	// Methods

	// RVA: 0x1287C44 Offset: 0x1283C44 VA: 0x1287C44
	private void OnEnable() { }

	// RVA: 0x1287EB0 Offset: 0x1283EB0 VA: 0x1287EB0 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x1287ED4 Offset: 0x1283ED4 VA: 0x1287ED4 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x1287EF8 Offset: 0x1283EF8 VA: 0x1287EF8 Slot: 9
	public override void Escape() { }

	// RVA: 0x1287EFC Offset: 0x1283EFC VA: 0x1287EFC
	public void OnPressedButtonBack() { }

	// RVA: 0x1287F6C Offset: 0x1283F6C VA: 0x1287F6C
	public void OnPressedButtonBuyPremiumPack() { }

	// RVA: 0x1288004 Offset: 0x1284004 VA: 0x1288004
	public void OnPressedButtonBuyEnergy() { }

	// RVA: 0x12881E4 Offset: 0x12841E4 VA: 0x12881E4
	public void OnPressedButtonFreeEnergy() { }

	// RVA: 0x1287CDC Offset: 0x1283CDC VA: 0x1287CDC
	private void Refresh() { }

	// RVA: 0x12882F4 Offset: 0x12842F4 VA: 0x12882F4
	private bool IsVideoLoaded() { }

	// RVA: 0x12881D4 Offset: 0x12841D4 VA: 0x12881D4
	private static int GetCostBuyEnergy() { }

	// RVA: 0x12881DC Offset: 0x12841DC VA: 0x12881DC
	private static int GetValueBuyEnergy() { }

	// RVA: 0x12883C0 Offset: 0x12843C0 VA: 0x12883C0
	public static int GetExchangeGemsFromEnergy(int _energy) { }

	// RVA: 0x12883B8 Offset: 0x12843B8 VA: 0x12883B8
	private int GetValueFreeEnergy() { }

	// RVA: 0x1287E50 Offset: 0x1283E50 VA: 0x1287E50
	private IEnumerator AdsTimer() { }

	// RVA: 0x1288344 Offset: 0x1284344 VA: 0x1288344
	private bool IsTimeAdsReady() { }

	// RVA: 0x1288490 Offset: 0x1284490 VA: 0x1288490
	public void .ctor() { }

	// RVA: 0x12884A4 Offset: 0x12844A4 VA: 0x12884A4
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x12884F4 Offset: 0x12844F4 VA: 0x12884F4
	private void <OnPressedButtonBuyPremiumPack>b__12_0(bool <p0>) { }

	[CompilerGenerated]
	// RVA: 0x1288560 Offset: 0x1284560 VA: 0x1288560
	private void <OnPressedButtonFreeEnergy>b__16_0(bool b) { }
}


// ===== keywords: Shop, Gem
// Namespace: 
public class Board_ShopGems : Board // TypeDefIndex: 1113
{
	// Fields
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private Shop_Cell[] allShopcells; // 0x20
	[SerializeField]
	private Sprite[] listSprites; // 0x28
	[SerializeField]
	private TextMeshPro textTimeAds; // 0x30
	[SerializeField]
	private TextMeshPro textFirstPurchase; // 0x38
	[SerializeField]
	private TextMeshPro textComboCoins; // 0x40
	[SerializeField]
	private ScrollView scrollView; // 0x48
	[SerializeField]
	private GameObject parentFirstSpec; // 0x50
	[SerializeField]
	private GameObject parentSaleSpec; // 0x58
	private float[] allValues; // 0x60
	private float[] allValuesCoins; // 0x68
	private float[] allValues2; // 0x70
	private int[] allIdPurchases; // 0x78
	private static bool isActived; // 0x4
	private static int MaxStockFreeGems; // 0x8
	public static double timePurchaseLimit; // 0x10
	public static double timePurchaseLimit2; // 0x18
	private static double m_timeToReset; // 0x20
	private static double m_timeToStart; // 0x28
	[SerializeField]
	private GameObject parentSpecialPacks; // 0x80
	[SerializeField]
	private GameObject skipVideo; // 0x88
	[SerializeField]
	private Transform parentNormalPacks; // 0x90
	[SerializeField]
	private BoxCollider2D boxContent; // 0x98
	[SerializeField]
	private TextMeshPro textCountSpecialQuantity; // 0xA0
	[SerializeField]
	private TextMeshPro textTimeFirstPurchase; // 0xA8
	[SerializeField]
	private TextMeshPro textTimePurchaseLimit; // 0xB0
	private bool isPopSpecTab0; // 0xB8
	private bool isPopSpecTab1; // 0xB9
	[SerializeField]
	private GameObject headerFirstPurchase; // 0xC0
	[SerializeField]
	private GameObject[] tagHotSales; // 0xC8
	[SerializeField]
	private Transform parentView; // 0xD0
	[SerializeField]
	private BoxCollider2D boxBound; // 0xD8
	public static int maxStockSpecial; // 0x30
	private Vector2 contentSize; // 0xE0
	private Vector2 contentOffset; // 0xE8
	private Vector3 posOld; // 0xF0
	public static bool IsVisitShopGems; // 0x34
	private static int countPurchaseSpecialPacks; // 0x38
	private Coroutine checkTimeOut; // 0x100
	[SerializeField]
	private GameObject loadingObject; // 0x108
	private GameObject focus; // 0x110
	[SerializeField]
	private Animator animSpecTab; // 0x118
	private static double totalSecs; // 0x40
	private static string keySysTime; // 0x48
	private static int timeUpdate; // 0x50
	[SerializeField]
	private GameObject parentFreeGems; // 0x120
	[SerializeField]
	private GameObject parentFreeLimited; // 0x128
	[SerializeField]
	private GameObject statusFreeGemsAdd; // 0x130
	[SerializeField]
	private GameObject statusFreeGemsNor; // 0x138
	[SerializeField]
	private SpriteRenderer boxFreeGems; // 0x140
	[SerializeField]
	private Sprite[] spriteBoxFreeGems; // 0x148
	private Coroutine adsCoroutine; // 0x150
	private int cellID; // 0x158
	[SerializeField]
	private Popup_Notices popupVideoNotReady; // 0x160
	[SerializeField]
	private Popup_Notices popupNetworkNotConnected; // 0x168
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x170
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x178

	// Properties
	public static double timeToReset { get; set; }
	public static double timeToStart { get; set; }
	public static int countActiveFirstPurchase { get; set; }
	public static bool IsPaid { get; set; }
	public static bool IsHasSalePacks { get; set; }
	public static bool IsFirstPurchase { get; set; }
	public static int CountPurchaseSpecialPacks { get; set; }
	private static double timeAds { get; }
	public static int FreeGemStocks { get; set; }

	// Methods

	// RVA: 0x137BCE4 Offset: 0x1377CE4 VA: 0x137BCE4
	public static bool IsHasVideo() { }

	// RVA: 0x137BF14 Offset: 0x1377F14 VA: 0x137BF14
	public static double get_timeToReset() { }

	// RVA: 0x137C10C Offset: 0x137810C VA: 0x137C10C
	public static void set_timeToReset(double value) { }

	// RVA: 0x137C004 Offset: 0x1378004 VA: 0x137C004
	private static float GetRandomLifeTimeSaleGemPacks() { }

	// RVA: 0x137C1B4 Offset: 0x13781B4 VA: 0x137C1B4
	public static double get_timeToStart() { }

	// RVA: 0x137C2A8 Offset: 0x13782A8 VA: 0x137C2A8
	public static void set_timeToStart(double value) { }

	// RVA: 0x137C350 Offset: 0x1378350 VA: 0x137C350
	public static int get_countActiveFirstPurchase() { }

	// RVA: 0x137C3BC Offset: 0x13783BC VA: 0x137C3BC
	public static void set_countActiveFirstPurchase(int value) { }

	// RVA: 0x137C42C Offset: 0x137842C VA: 0x137C42C
	public static float FirstPurchaseAmount() { }

	// RVA: 0x137C4C4 Offset: 0x13784C4 VA: 0x137C4C4
	public static bool get_IsPaid() { }

	// RVA: 0x137C53C Offset: 0x137853C VA: 0x137C53C
	public static void set_IsPaid(bool value) { }

	// RVA: 0x137C5B8 Offset: 0x13785B8 VA: 0x137C5B8
	public static bool get_IsHasSalePacks() { }

	// RVA: 0x137C630 Offset: 0x1378630 VA: 0x137C630
	public static void set_IsHasSalePacks(bool value) { }

	// RVA: 0x137C6AC Offset: 0x13786AC VA: 0x137C6AC
	public static bool get_IsFirstPurchase() { }

	// RVA: 0x137C9EC Offset: 0x13789EC VA: 0x137C9EC
	public static void set_IsFirstPurchase(bool value) { }

	// RVA: 0x137CA6C Offset: 0x1378A6C VA: 0x137CA6C
	private void Awake() { }

	// RVA: 0x137CB58 Offset: 0x1378B58 VA: 0x137CB58
	private void OnEnable() { }

	// RVA: 0x137D8DC Offset: 0x13798DC VA: 0x137D8DC
	private void SetShopInfo() { }

	// RVA: 0x137D87C Offset: 0x137987C VA: 0x137D87C
	private IEnumerator UpdateTimers() { }

	// RVA: 0x137D2B0 Offset: 0x13792B0 VA: 0x137D2B0
	private void CheckFirstPurchaseBonus() { }

	// RVA: 0x137CEC8 Offset: 0x1378EC8 VA: 0x137CEC8
	private void CheckSpecialPacks() { }

	// RVA: 0x137EDBC Offset: 0x137ADBC VA: 0x137EDBC
	public static bool IsCheckSaleSpecialPacks() { }

	// RVA: 0x137EEB0 Offset: 0x137AEB0 VA: 0x137EEB0
	public static bool IsCheckFirstSpecialPacks() { }

	// RVA: 0x137EFC4 Offset: 0x137AFC4 VA: 0x137EFC4
	public static bool IsHasFirstSpecialPacks() { }

	// RVA: 0x137F0CC Offset: 0x137B0CC VA: 0x137F0CC
	public static int get_CountPurchaseSpecialPacks() { }

	// RVA: 0x137F1B8 Offset: 0x137B1B8 VA: 0x137F1B8
	public static void set_CountPurchaseSpecialPacks(int value) { }

	// RVA: 0x137E9F4 Offset: 0x137A9F4 VA: 0x137E9F4
	private void CheckSpecialPacks2() { }

	// RVA: 0x137CC68 Offset: 0x1378C68 VA: 0x137CC68
	private void SetContent() { }

	// RVA: 0x137E96C Offset: 0x137A96C VA: 0x137E96C
	private IEnumerator SetShopPrices() { }

	// RVA: 0x137F280 Offset: 0x137B280 VA: 0x137F280
	private void OnInitialized() { }

	// RVA: 0x137F498 Offset: 0x137B498 VA: 0x137F498
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x137E2A8 Offset: 0x137A2A8 VA: 0x137E2A8
	private void CheckFocusVideo() { }

	// RVA: 0x137F61C Offset: 0x137B61C VA: 0x137F61C
	private void OnDisable() { }

	// RVA: 0x137F67C Offset: 0x137B67C VA: 0x137F67C Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x137F6A0 Offset: 0x137B6A0 VA: 0x137F6A0 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x137F6E0 Offset: 0x137B6E0 VA: 0x137F6E0 Slot: 9
	public override void Escape() { }

	// RVA: 0x137F6E4 Offset: 0x137B6E4 VA: 0x137F6E4
	public void OnPressedButtonBack() { }

	// RVA: 0x137BEA8 Offset: 0x1377EA8 VA: 0x137BEA8
	private static double get_timeAds() { }

	// RVA: 0x137DCB0 Offset: 0x1379CB0 VA: 0x137DCB0
	private IEnumerator AdsTimer() { }

	// RVA: 0x137DD10 Offset: 0x1379D10 VA: 0x137DD10
	private void UpdateVideoButton() { }

	// RVA: 0x137F520 Offset: 0x137B520 VA: 0x137F520
	protected bool IsTimeAdsReady() { }

	// RVA: 0x137F804 Offset: 0x137B804 VA: 0x137F804
	private void OnClickBuy(Shop_Cell _cell) { }

	// RVA: 0x137BE3C Offset: 0x1377E3C VA: 0x137BE3C
	public static int get_FreeGemStocks() { }

	// RVA: 0x13805F4 Offset: 0x137C5F4 VA: 0x13805F4
	public static void set_FreeGemStocks(int value) { }

	// RVA: 0x1380664 Offset: 0x137C664 VA: 0x1380664
	public static void DailyReset() { }

	// RVA: 0x137FCBC Offset: 0x137BCBC VA: 0x137FCBC
	private void CheckPopup() { }

	// RVA: 0x137FBD8 Offset: 0x137BBD8 VA: 0x137FBD8
	private void Purchase(int _id, Action<bool> _callback) { }

	// RVA: 0x137FDB8 Offset: 0x137BDB8 VA: 0x137FDB8
	private void OnPurchased(bool _successed) { }

	// RVA: 0x13808A4 Offset: 0x137C8A4 VA: 0x13808A4
	public void .ctor() { }

	// RVA: 0x13809B8 Offset: 0x137C9B8 VA: 0x13809B8
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x1380A54 Offset: 0x137CA54 VA: 0x1380A54
	private void <CheckLoadingTimeOut>b__77_0() { }

	[CompilerGenerated]
	// RVA: 0x1380A74 Offset: 0x137CA74 VA: 0x1380A74
	private void <OnClickBuy>b__102_0() { }

	[CompilerGenerated]
	// RVA: 0x1380A94 Offset: 0x137CA94 VA: 0x1380A94
	private void <OnClickBuy>b__102_1(bool ok) { }

	[CompilerGenerated]
	// RVA: 0x1380AA4 Offset: 0x137CAA4 VA: 0x1380AA4
	private void <OnClickBuy>b__102_2() { }

	[CompilerGenerated]
	// RVA: 0x1380AC4 Offset: 0x137CAC4 VA: 0x1380AC4
	private void <CheckPopup>b__107_0() { }

	[CompilerGenerated]
	// RVA: 0x1380AE4 Offset: 0x137CAE4 VA: 0x1380AE4
	private void <CheckPopup>b__107_1() { }

	[CompilerGenerated]
	// RVA: 0x1380B04 Offset: 0x137CB04 VA: 0x1380B04
	private void <OnPurchased>b__109_0() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss10_AnimationEvents : MonoBehaviour // TypeDefIndex: 144
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action on2HandAttackStartEvent; // 0x30
	public Action on2HandAttackEndedEvent; // 0x38
	public Action onAttack8StartEvent; // 0x40
	public Action onAttack8EndedEvent; // 0x48
	public Action onAttack9StartEvent; // 0x50
	public Action onAttack9EndedEvent; // 0x58
	public Action onKnifeLeft; // 0x60
	public Action onKnifeRight; // 0x68
	public Action<bool> onHandAttackEvent; // 0x70
	public Action<bool> onHandAttack1Event; // 0x78
	public Action<bool> onHandAttack5Event; // 0x80
	public Action onCircleAttackEvent; // 0x88
	public Action onDropAttackEvent; // 0x90
	public Action onCoreAttackEvent; // 0x98
	public Action onHandShootOneHitEvent; // 0xA0

	// Methods

	// RVA: 0x1248720 Offset: 0x1244720 VA: 0x1248720
	private void OnAnimationEndedEvent() { }

	// RVA: 0x124873C Offset: 0x124473C VA: 0x124873C
	private void OnDie() { }

	// RVA: 0x1248758 Offset: 0x1244758 VA: 0x1248758
	private void OnHandShootOneHit() { }

	// RVA: 0x1248774 Offset: 0x1244774 VA: 0x1248774
	private void On2HandStartAttack() { }

	// RVA: 0x1248790 Offset: 0x1244790 VA: 0x1248790
	private void On2HandStopAttack() { }

	// RVA: 0x12487AC Offset: 0x12447AC VA: 0x12487AC
	private void AttackHandLeft() { }

	// RVA: 0x12487CC Offset: 0x12447CC VA: 0x12487CC
	private void AttackHandRight() { }

	// RVA: 0x12487EC Offset: 0x12447EC VA: 0x12487EC
	private void AttackHand1Left() { }

	// RVA: 0x124880C Offset: 0x124480C VA: 0x124880C
	private void AttackHand1Right() { }

	// RVA: 0x124882C Offset: 0x124482C VA: 0x124882C
	private void AttackHand5Left() { }

	// RVA: 0x124884C Offset: 0x124484C VA: 0x124884C
	private void AttackHand5Right() { }

	// RVA: 0x124886C Offset: 0x124486C VA: 0x124886C
	private void StartAttack8() { }

	// RVA: 0x1248888 Offset: 0x1244888 VA: 0x1248888
	private void StopAttack8() { }

	// RVA: 0x12488A4 Offset: 0x12448A4 VA: 0x12488A4
	private void StartAttack9() { }

	// RVA: 0x12488C0 Offset: 0x12448C0 VA: 0x12488C0
	private void StopAttack9() { }

	// RVA: 0x12488DC Offset: 0x12448DC VA: 0x12488DC
	private void KnifeLeft() { }

	// RVA: 0x12488F8 Offset: 0x12448F8 VA: 0x12488F8
	private void KnifeRight() { }

	// RVA: 0x1248914 Offset: 0x1244914 VA: 0x1248914
	private void AttackCircle() { }

	// RVA: 0x1248930 Offset: 0x1244930 VA: 0x1248930
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss11_AnimationEvents : MonoBehaviour // TypeDefIndex: 145
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action<bool> onHandAttack1Event; // 0x30
	public Action onCallAttack3Event; // 0x38
	public Action onAttack4StartEvent; // 0x40
	public Action onAttack4EndedEvent; // 0x48
	public Action onAttack41StartEvent; // 0x50
	public Action onAttack41EndedEvent; // 0x58
	public Action onAttack78StartEvent; // 0x60
	public Action onAttack78EndedEvent; // 0x68
	public Action onCallAttack5Event; // 0x70

	// Methods

	// RVA: 0x1248938 Offset: 0x1244938 VA: 0x1248938
	private void OnAnimationEndedEvent() { }

	// RVA: 0x1248954 Offset: 0x1244954 VA: 0x1248954
	private void OnDie() { }

	// RVA: 0x1248970 Offset: 0x1244970 VA: 0x1248970
	private void OnCallAttack3Event() { }

	// RVA: 0x124898C Offset: 0x124498C VA: 0x124898C
	private void OnCallAttack5Event() { }

	// RVA: 0x12489A8 Offset: 0x12449A8 VA: 0x12489A8
	private void Attack1HandLeft() { }

	// RVA: 0x12489C8 Offset: 0x12449C8 VA: 0x12489C8
	private void Attack1HandRight() { }

	// RVA: 0x12489E8 Offset: 0x12449E8 VA: 0x12489E8
	private void OnCallAttack4StartEvent() { }

	// RVA: 0x1248A04 Offset: 0x1244A04 VA: 0x1248A04
	private void OnCallAttack4EndEvent() { }

	// RVA: 0x1248A20 Offset: 0x1244A20 VA: 0x1248A20
	private void OnCallAttack41StartEvent() { }

	// RVA: 0x1248A3C Offset: 0x1244A3C VA: 0x1248A3C
	private void OnCallAttack41EndEvent() { }

	// RVA: 0x1248A58 Offset: 0x1244A58 VA: 0x1248A58
	private void OnCallAttack78StartEvent() { }

	// RVA: 0x1248A74 Offset: 0x1244A74 VA: 0x1248A74
	private void OnCallAttack78EndEvent() { }

	// RVA: 0x1248A90 Offset: 0x1244A90 VA: 0x1248A90
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss12_AnimationEvents : MonoBehaviour // TypeDefIndex: 148
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onCallAttack1Event; // 0x30
	public Action onCallAttack2Event; // 0x38
	public Action onCallAttack3Event; // 0x40
	public Action onCallAttack1CheckEvent; // 0x48
	public Action onCallAttack2CheckEvent; // 0x50
	public Action onCallAttack12ShootEvent; // 0x58
	public Action onAttack4Event; // 0x60
	public Action onAttack6Event; // 0x68
	public Action onAttack9StartEvent; // 0x70
	public Action onAttack9EndEvent; // 0x78

	// Methods

	// RVA: 0x1248E08 Offset: 0x1244E08 VA: 0x1248E08
	private void OnAnimationEndedEvent() { }

	// RVA: 0x1248E24 Offset: 0x1244E24 VA: 0x1248E24
	private void OnDie() { }

	// RVA: 0x1248E40 Offset: 0x1244E40 VA: 0x1248E40
	private void Attack1HandLeft() { }

	// RVA: 0x1248E5C Offset: 0x1244E5C VA: 0x1248E5C
	private void Attack2HandRight() { }

	// RVA: 0x1248E78 Offset: 0x1244E78 VA: 0x1248E78
	private void Attack3TwoHands() { }

	// RVA: 0x1248E94 Offset: 0x1244E94 VA: 0x1248E94
	private void Attack1StartCheckShoot() { }

	// RVA: 0x1248EB0 Offset: 0x1244EB0 VA: 0x1248EB0
	private void Attack2StartCheckShoot() { }

	// RVA: 0x1248ECC Offset: 0x1244ECC VA: 0x1248ECC
	private void Attack12Shoot() { }

	// RVA: 0x1248EE8 Offset: 0x1244EE8 VA: 0x1248EE8
	private void OnCallAttack4Event() { }

	// RVA: 0x1248F04 Offset: 0x1244F04 VA: 0x1248F04
	private void OnCallAttack6Event() { }

	// RVA: 0x1248F20 Offset: 0x1244F20 VA: 0x1248F20
	private void OnCallAttack9StartEvent() { }

	// RVA: 0x1248F3C Offset: 0x1244F3C VA: 0x1248F3C
	private void OnCallAttack9EndEvent() { }

	// RVA: 0x1248F58 Offset: 0x1244F58 VA: 0x1248F58
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss13_AnimationEvents : MonoBehaviour // TypeDefIndex: 153
{
	// Methods

	// RVA: 0x1249DC8 Offset: 0x1245DC8 VA: 0x1249DC8
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss15_AnimationEvents : MonoBehaviour // TypeDefIndex: 154
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onSpawnChilds; // 0x30
	public Action onCallAttack1LEvent; // 0x38
	public Action onCallAttack1REvent; // 0x40
	public Action onCallAttack1TwoEvent; // 0x48
	public Action onStartAttack2Event; // 0x50
	public Action onEndAttack2Event; // 0x58
	public Action onCallAttack3LEvent; // 0x60
	public Action onCallAttack3REvent; // 0x68
	public Action onCallAttack3TwoEvent; // 0x70
	public Action onStartAttack6Event; // 0x78
	public Action onEndAttack6Event; // 0x80
	public Action onAttack10StartEvent; // 0x88
	public Action onAttack10EndEvent; // 0x90
	public Action onGetPower; // 0x98
	public Action onDestroyLantern; // 0xA0
	public Action onAttack9Event; // 0xA8
	public Action onAttack92Event; // 0xB0
	public Action onCallAttack12Event; // 0xB8
	public Action onCallAttack15Event; // 0xC0
	public Action onCallAttack16Event; // 0xC8

	// Methods

	// RVA: 0x1249DD0 Offset: 0x1245DD0 VA: 0x1249DD0
	protected void OnAnimationEndedEvent() { }

	// RVA: 0x1249DEC Offset: 0x1245DEC VA: 0x1249DEC
	protected void OnDie() { }

	// RVA: 0x1249E08 Offset: 0x1245E08 VA: 0x1249E08
	protected void Attack1HandLeft() { }

	// RVA: 0x1249E24 Offset: 0x1245E24 VA: 0x1249E24
	protected void Attack1HandRight() { }

	// RVA: 0x1249E40 Offset: 0x1245E40 VA: 0x1249E40
	protected void Attack1TwoHands() { }

	// RVA: 0x1249E5C Offset: 0x1245E5C VA: 0x1249E5C
	protected void StartAttack2() { }

	// RVA: 0x1249E78 Offset: 0x1245E78 VA: 0x1249E78
	protected void EndAttack2() { }

	// RVA: 0x1249E94 Offset: 0x1245E94 VA: 0x1249E94
	protected void Attack3HandLeft() { }

	// RVA: 0x1249EB0 Offset: 0x1245EB0 VA: 0x1249EB0
	protected void Attack3HandRight() { }

	// RVA: 0x1249ECC Offset: 0x1245ECC VA: 0x1249ECC
	protected void Attack3TwoHands() { }

	// RVA: 0x1249EE8 Offset: 0x1245EE8 VA: 0x1249EE8
	protected void StartAttack6() { }

	// RVA: 0x1249F04 Offset: 0x1245F04 VA: 0x1249F04
	protected void EndAttack6() { }

	// RVA: 0x1249F20 Offset: 0x1245F20 VA: 0x1249F20
	protected void StartAttack10() { }

	// RVA: 0x1249F3C Offset: 0x1245F3C VA: 0x1249F3C
	protected void EndAttack10() { }

	// RVA: 0x1249F58 Offset: 0x1245F58 VA: 0x1249F58
	protected void OnCallAttack9Event() { }

	// RVA: 0x1249F74 Offset: 0x1245F74 VA: 0x1249F74
	protected void OnCallAttack92Event() { }

	// RVA: 0x1249F90 Offset: 0x1245F90 VA: 0x1249F90
	protected void OnSpawnChilds() { }

	// RVA: 0x1249FAC Offset: 0x1245FAC VA: 0x1249FAC
	protected void OnGetPower() { }

	// RVA: 0x1249FC8 Offset: 0x1245FC8 VA: 0x1249FC8
	protected void OnDestroyLantern() { }

	// RVA: 0x1249FE4 Offset: 0x1245FE4 VA: 0x1249FE4
	protected void Attack12HandRight() { }

	// RVA: 0x124A000 Offset: 0x1246000 VA: 0x124A000
	protected void Attack15HandLeft() { }

	// RVA: 0x124A01C Offset: 0x124601C VA: 0x124A01C
	protected void Attack16TwoHand() { }

	// RVA: 0x124A038 Offset: 0x1246038 VA: 0x124A038
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss17_AnimationEvents : MonoBehaviour // TypeDefIndex: 155
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onSpawnChilds; // 0x30
	public Action onCallAttack1Event; // 0x38
	public Action onCallAttack2Event; // 0x40
	public Action onCallAttack3Event; // 0x48
	public Action onCallAttackBigBulletEvent; // 0x50
	public Action onCallAttack1CheckEvent; // 0x58
	public Action onCallAttack2CheckEvent; // 0x60
	public Action onCallAttack12ShootEvent; // 0x68
	public Action onAttack4Event; // 0x70
	public Action onAttack6Event; // 0x78
	public Action onAttack9StartEvent; // 0x80
	public Action onAttack9EndEvent; // 0x88

	// Methods

	// RVA: 0x124A040 Offset: 0x1246040 VA: 0x124A040
	private void OnAnimationEndedEvent() { }

	// RVA: 0x124A05C Offset: 0x124605C VA: 0x124A05C
	private void OnDie() { }

	// RVA: 0x124A078 Offset: 0x1246078 VA: 0x124A078
	private void Attack1HandLeft() { }

	// RVA: 0x124A094 Offset: 0x1246094 VA: 0x124A094
	private void Attack2HandRight() { }

	// RVA: 0x124A0B0 Offset: 0x12460B0 VA: 0x124A0B0
	private void Attack3TwoHands() { }

	// RVA: 0x124A0CC Offset: 0x12460CC VA: 0x124A0CC
	private void AttackBigBullet() { }

	// RVA: 0x124A0E8 Offset: 0x12460E8 VA: 0x124A0E8
	private void Attack1StartCheckShoot() { }

	// RVA: 0x124A104 Offset: 0x1246104 VA: 0x124A104
	private void Attack2StartCheckShoot() { }

	// RVA: 0x124A120 Offset: 0x1246120 VA: 0x124A120
	private void Attack12Shoot() { }

	// RVA: 0x124A13C Offset: 0x124613C VA: 0x124A13C
	private void OnCallAttack4Event() { }

	// RVA: 0x124A158 Offset: 0x1246158 VA: 0x124A158
	private void OnCallAttack6Event() { }

	// RVA: 0x124A174 Offset: 0x1246174 VA: 0x124A174
	private void OnCallAttack9StartEvent() { }

	// RVA: 0x124A190 Offset: 0x1246190 VA: 0x124A190
	private void OnCallAttack9EndEvent() { }

	// RVA: 0x124A1AC Offset: 0x12461AC VA: 0x124A1AC
	protected void OnSpawnChilds() { }

	// RVA: 0x124A1C8 Offset: 0x12461C8 VA: 0x124A1C8
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss18_AnimationEvents : MonoBehaviour // TypeDefIndex: 158
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onSpawnChilds; // 0x30
	public Action onCallAttack1Event; // 0x38
	public Action onCallAttack2Event; // 0x40
	public Action onCallAttack3Event; // 0x48
	public Action onCallAttackBigBulletEvent; // 0x50
	public Action onTargetPlayer; // 0x58
	public Action onAttackReflexBullet; // 0x60
	public Action onAttackBomb; // 0x68
	public Action onCallAttack1CheckEvent; // 0x70
	public Action onCallAttack2CheckEvent; // 0x78
	public Action onCallAttack12ShootEvent; // 0x80
	public Action onAttack4Event; // 0x88
	public Action onAttack6Event; // 0x90
	public Action onAttack7StartEvent; // 0x98
	public Action onAttack7EndEvent; // 0xA0
	public Action onAttack9StartEvent; // 0xA8
	public Action onAttack9EndEvent; // 0xB0

	// Methods

	// RVA: 0x124A210 Offset: 0x1246210 VA: 0x124A210
	private void OnAnimationEndedEvent() { }

	// RVA: 0x124A22C Offset: 0x124622C VA: 0x124A22C
	private void OnDie() { }

	// RVA: 0x124A248 Offset: 0x1246248 VA: 0x124A248
	private void Attack1HandLeft() { }

	// RVA: 0x124A264 Offset: 0x1246264 VA: 0x124A264
	private void Attack2HandRight() { }

	// RVA: 0x124A280 Offset: 0x1246280 VA: 0x124A280
	private void Attack3TwoHands() { }

	// RVA: 0x124A29C Offset: 0x124629C VA: 0x124A29C
	private void AttackBigBullet() { }

	// RVA: 0x124A2B8 Offset: 0x12462B8 VA: 0x124A2B8
	private void Attack1StartCheckShoot() { }

	// RVA: 0x124A2D4 Offset: 0x12462D4 VA: 0x124A2D4
	private void Attack2StartCheckShoot() { }

	// RVA: 0x124A2F0 Offset: 0x12462F0 VA: 0x124A2F0
	private void Attack12Shoot() { }

	// RVA: 0x124A30C Offset: 0x124630C VA: 0x124A30C
	private void OnCallAttack4Event() { }

	// RVA: 0x124A328 Offset: 0x1246328 VA: 0x124A328
	private void OnCallAttack6Event() { }

	// RVA: 0x124A344 Offset: 0x1246344 VA: 0x124A344
	protected void OnCallAttack7StartEvent() { }

	// RVA: 0x124A360 Offset: 0x1246360 VA: 0x124A360
	protected void OnCallAttack7EndEvent() { }

	// RVA: 0x124A37C Offset: 0x124637C VA: 0x124A37C
	protected void OnCallAttack9StartEvent() { }

	// RVA: 0x124A398 Offset: 0x1246398 VA: 0x124A398
	protected void OnCallAttack9EndEvent() { }

	// RVA: 0x124A3B4 Offset: 0x12463B4 VA: 0x124A3B4
	protected void OnSpawnChilds() { }

	// RVA: 0x124A3D0 Offset: 0x12463D0 VA: 0x124A3D0
	protected void OnTargetPlayer() { }

	// RVA: 0x124A3EC Offset: 0x12463EC VA: 0x124A3EC
	protected void OnAttackReflexBullet() { }

	// RVA: 0x124A408 Offset: 0x1246408 VA: 0x124A408
	protected void OnAttackBomb() { }

	// RVA: 0x124A424 Offset: 0x1246424 VA: 0x124A424
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss1_AnimationEvents : MonoBehaviour // TypeDefIndex: 143
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onCallAttack1Event; // 0x30
	public Action onCallAttack2Event; // 0x38
	public Action onCallAttack3Event; // 0x40
	public Action onCallAttack1CheckEvent; // 0x48
	public Action onCallAttack2CheckEvent; // 0x50
	public Action onCallAttack12ShootEvent; // 0x58
	public Action onAttack4Event; // 0x60
	public Action onAttack6Event; // 0x68
	public Action onAttack9StartEvent; // 0x70
	public Action onAttack9EndEvent; // 0x78

	// Methods

	// RVA: 0x12485C8 Offset: 0x12445C8 VA: 0x12485C8
	private void OnAnimationEndedEvent() { }

	// RVA: 0x12485E4 Offset: 0x12445E4 VA: 0x12485E4
	private void OnDie() { }

	// RVA: 0x1248600 Offset: 0x1244600 VA: 0x1248600
	private void Attack1HandLeft() { }

	// RVA: 0x124861C Offset: 0x124461C VA: 0x124861C
	private void Attack2HandRight() { }

	// RVA: 0x1248638 Offset: 0x1244638 VA: 0x1248638
	private void Attack3TwoHands() { }

	// RVA: 0x1248654 Offset: 0x1244654 VA: 0x1248654
	private void Attack1StartCheckShoot() { }

	// RVA: 0x1248670 Offset: 0x1244670 VA: 0x1248670
	private void Attack2StartCheckShoot() { }

	// RVA: 0x124868C Offset: 0x124468C VA: 0x124868C
	private void Attack12Shoot() { }

	// RVA: 0x12486A8 Offset: 0x12446A8 VA: 0x12486A8
	private void OnCallAttack4Event() { }

	// RVA: 0x12486C4 Offset: 0x12446C4 VA: 0x12486C4
	private void OnCallAttack6Event() { }

	// RVA: 0x12486E0 Offset: 0x12446E0 VA: 0x12486E0
	private void OnCallAttack9StartEvent() { }

	// RVA: 0x12486FC Offset: 0x12446FC VA: 0x12486FC
	private void OnCallAttack9EndEvent() { }

	// RVA: 0x1248718 Offset: 0x1244718 VA: 0x1248718
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss3_PlasmaAnimEvent : MonoBehaviour // TypeDefIndex: 120
{
	// Fields
	[SerializeField]
	private BoxCollider2D boxHit; // 0x20
	[SerializeField]
	private Enemy_LookAtPlayer plasmaGunLookat; // 0x28
	public Action onAppeared; // 0x30
	public Action onEnded; // 0x38
	public Action onShooting; // 0x40
	private AudioSource sfxLaser; // 0x48

	// Methods

	// RVA: 0x1243080 Offset: 0x123F080 VA: 0x1243080
	private void OnStartAttack() { }

	// RVA: 0x12430B8 Offset: 0x123F0B8 VA: 0x12430B8
	private void OnEndedAttack() { }

	// RVA: 0x12430F0 Offset: 0x123F0F0 VA: 0x12430F0
	private void OnAppeared() { }

	// RVA: 0x124310C Offset: 0x123F10C VA: 0x124310C
	private void OnEnded() { }

	// RVA: 0x12431A8 Offset: 0x123F1A8 VA: 0x12431A8
	private void OnShooting() { }

	// RVA: 0x1243288 Offset: 0x123F288 VA: 0x1243288
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss4_AnimationEvents : MonoBehaviour // TypeDefIndex: 185
{
	// Fields
	private AudioSource sfxLaser; // 0x20
	public Action die; // 0x28

	// Methods

	// RVA: 0x131B04C Offset: 0x131704C VA: 0x131B04C
	private void OnDie() { }

	// RVA: 0x131B0B8 Offset: 0x13170B8 VA: 0x131B0B8
	private void OnEndedDie() { }

	// RVA: 0x131B154 Offset: 0x1317154 VA: 0x131B154
	private void OnVibrateInfinity() { }

	// RVA: 0x131B1B0 Offset: 0x13171B0 VA: 0x131B1B0
	private void OffVibrateInfinity() { }

	// RVA: 0x131B200 Offset: 0x1317200 VA: 0x131B200
	private void OnBigPlasma() { }

	// RVA: 0x131B300 Offset: 0x1317300 VA: 0x131B300
	private void OffBigPlasma() { }

	// RVA: 0x131B3B0 Offset: 0x13173B0 VA: 0x131B3B0
	public void .ctor() { }
}


// ===== keywords: Boss, Laser
// Namespace: 
public class Boss4_BigLaser : MonoBehaviour // TypeDefIndex: 186
{
	// Fields
	[SerializeField]
	private float damage; // 0x20
	private Damager damager; // 0x28
	private Vector2 point; // 0x30
	[SerializeField]
	private Vector2 size; // 0x38
	private Collider2D resuftColliders; // 0x40
	[SerializeField]
	private Transform plasmaPoint; // 0x48
	[SerializeField]
	private LayerMask targetLayer; // 0x50
	private bool laserActived; // 0x54
	[SerializeField]
	private float offsetAngle; // 0x58
	[SerializeField]
	private bool random; // 0x5C
	[SerializeField]
	private Transform parentParticle; // 0x60

	// Methods

	// RVA: 0x131B3B8 Offset: 0x13173B8 VA: 0x131B3B8
	private void OnEnable() { }

	// RVA: 0x131B458 Offset: 0x1317458 VA: 0x131B458
	public void CheckLaserStart() { }

	// RVA: 0x131B464 Offset: 0x1317464 VA: 0x131B464
	public void CheckLaserEnded() { }

	// RVA: 0x131B46C Offset: 0x131746C VA: 0x131B46C
	private void FixedUpdate() { }

	// RVA: 0x131B470 Offset: 0x1317470 VA: 0x131B470
	private void CheckLaserCollision() { }

	// RVA: 0x131B664 Offset: 0x1317664 VA: 0x131B664
	protected void OnLaserCollided(Collider2D obj) { }

	// RVA: 0x131B7D4 Offset: 0x13177D4 VA: 0x131B7D4
	private void OnDrawGizmos() { }

	// RVA: 0x131BC04 Offset: 0x1317C04 VA: 0x131BC04
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss5_AnimationEvents : MonoBehaviour // TypeDefIndex: 188
{
	// Fields
	public Action onAttackEnded; // 0x20
	public Action die; // 0x28

	// Methods

	// RVA: 0x131BDA8 Offset: 0x1317DA8 VA: 0x131BDA8
	private void OnAttackEnded() { }

	// RVA: 0x131BDC4 Offset: 0x1317DC4 VA: 0x131BDC4
	private void OnDie() { }

	// RVA: 0x131BDE0 Offset: 0x1317DE0 VA: 0x131BDE0
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss6_AnimationEvents : MonoBehaviour // TypeDefIndex: 189
{
	// Fields
	public Action onAttackEnded; // 0x20
	public Action onPunch; // 0x28
	public Action onSpawnSwords; // 0x30
	public Action die; // 0x38
	[SerializeField]
	private Gun_Attack gunAttack1; // 0x40
	[SerializeField]
	private Gun_Attack gunAttack2; // 0x48

	// Methods

	// RVA: 0x131BDE8 Offset: 0x1317DE8 VA: 0x131BDE8
	private void OnAttackEnded() { }

	// RVA: 0x131BE04 Offset: 0x1317E04 VA: 0x131BE04
	private void OnDie() { }

	// RVA: 0x131BE20 Offset: 0x1317E20 VA: 0x131BE20
	private void OnPunch() { }

	// RVA: 0x131BE3C Offset: 0x1317E3C VA: 0x131BE3C
	private void OnSpawnSwords() { }

	// RVA: 0x131BE58 Offset: 0x1317E58 VA: 0x131BE58
	private void GunSwordLeftAttack() { }

	// RVA: 0x131BE88 Offset: 0x1317E88 VA: 0x131BE88
	private void GunSwordRightAttack() { }

	// RVA: 0x131BEB8 Offset: 0x1317EB8 VA: 0x131BEB8
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss6_Mini_AnimationEvents : MonoBehaviour // TypeDefIndex: 192
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action onDieEvent; // 0x28
	public Action onAttack1RightStartEvent; // 0x30
	public Action onAttack1RightStopEvent; // 0x38
	public Action onAttack1Left1Event; // 0x40
	public Action onAttack1Left2Event; // 0x48
	public Action onAttack2CStartEvent; // 0x50
	public Action onAttack2CStopEvent; // 0x58
	public Action onAttack3Event; // 0x60
	[SerializeField]
	protected GameObject parent; // 0x68

	// Methods

	// RVA: 0x131C7A0 Offset: 0x13187A0 VA: 0x131C7A0
	protected void OnAnimationEndedEvent() { }

	// RVA: 0x131C7BC Offset: 0x13187BC VA: 0x131C7BC
	protected void OnDie() { }

	// RVA: 0x131C7D8 Offset: 0x13187D8 VA: 0x131C7D8
	protected void OnAttack1RightStartEvent() { }

	// RVA: 0x131C7F4 Offset: 0x13187F4 VA: 0x131C7F4
	protected void OnAttack1RightStopEvent() { }

	// RVA: 0x131C810 Offset: 0x1318810 VA: 0x131C810
	protected void OnAttack1Left1Event() { }

	// RVA: 0x131C82C Offset: 0x131882C VA: 0x131C82C
	protected void OnAttack1Left2Event() { }

	// RVA: 0x131C848 Offset: 0x1318848 VA: 0x131C848
	protected void OnAttack2CStartEvent() { }

	// RVA: 0x131C864 Offset: 0x1318864 VA: 0x131C864
	protected void OnAttack2CStopEvent() { }

	// RVA: 0x131C880 Offset: 0x1318880 VA: 0x131C880
	protected void OnAttack3Event() { }

	// RVA: 0x131C89C Offset: 0x131889C VA: 0x131C89C
	protected void CallSoundBreakPlatforms() { }

	// RVA: 0x131C908 Offset: 0x1318908 VA: 0x131C908
	protected void CallSoundBossAppear() { }

	// RVA: 0x131C918 Offset: 0x1318918 VA: 0x131C918
	protected void CallSoundBossReady() { }

	// RVA: 0x131C928 Offset: 0x1318928 VA: 0x131C928
	protected void CallSoundBossLaughing() { }

	// RVA: 0x131C938 Offset: 0x1318938 VA: 0x131C938
	protected void CallSoundBossDead() { }

	// RVA: 0x131C948 Offset: 0x1318948 VA: 0x131C948
	protected void Pool() { }

	// RVA: 0x131C9B4 Offset: 0x13189B4 VA: 0x131C9B4
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss7_AnimationEvents : MonoBehaviour // TypeDefIndex: 193
{
	// Fields
	public Action onAttackEnded; // 0x20
	public Action die; // 0x28
	public Action dieFx; // 0x30
	public Action onJumpDown; // 0x38
	public Action onJumpStart; // 0x40
	public Action onJumpEnded; // 0x48
	public Action onStompingLeft; // 0x50
	public Action onStompingRight; // 0x58
	public Action onAttack2; // 0x60
	public Action onMixDone; // 0x68

	// Methods

	// RVA: 0x131C9BC Offset: 0x13189BC VA: 0x131C9BC
	private void OnAttackEnded() { }

	// RVA: 0x131C9D8 Offset: 0x13189D8 VA: 0x131C9D8
	private void OnDie() { }

	// RVA: 0x131C9F4 Offset: 0x13189F4 VA: 0x131C9F4
	private void OnDieFx() { }

	// RVA: 0x131CA10 Offset: 0x1318A10 VA: 0x131CA10
	private void OnJumpAppear() { }

	// RVA: 0x131CA6C Offset: 0x1318A6C VA: 0x131CA6C
	private void OnJumpStart() { }

	// RVA: 0x131CA88 Offset: 0x1318A88 VA: 0x131CA88
	private void OnJumpDown() { }

	// RVA: 0x131CB0C Offset: 0x1318B0C VA: 0x131CB0C
	private void OnJumpEnded() { }

	// RVA: 0x131CB28 Offset: 0x1318B28 VA: 0x131CB28
	private void OnAttack2() { }

	// RVA: 0x131CB44 Offset: 0x1318B44 VA: 0x131CB44
	private void OnStompingLeft() { }

	// RVA: 0x131CB60 Offset: 0x1318B60 VA: 0x131CB60
	private void OnStompingRight() { }

	// RVA: 0x131CB7C Offset: 0x1318B7C VA: 0x131CB7C
	private void OnMixDone() { }

	// RVA: 0x131CB98 Offset: 0x1318B98 VA: 0x131CB98
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss8_AnimationEvents : MonoBehaviour // TypeDefIndex: 195
{
	// Fields
	public Action onAttackEnded; // 0x20
	public Action die; // 0x28
	public Action onDroidAttack; // 0x30
	public Action onDroidStopAttack; // 0x38
	public Action onRocketAttack; // 0x40
	public Action onFlashAttack; // 0x48
	public Action onAttack4IdleStart; // 0x50
	public Action onAttack4IdleStop; // 0x58

	// Methods

	// RVA: 0x131D000 Offset: 0x1319000 VA: 0x131D000
	private void OnAttackEnded() { }

	// RVA: 0x131D01C Offset: 0x131901C VA: 0x131D01C
	private void OnDie() { }

	// RVA: 0x131D038 Offset: 0x1319038 VA: 0x131D038
	private void OnDroidStartAttack() { }

	// RVA: 0x131D054 Offset: 0x1319054 VA: 0x131D054
	private void OnDroidStopAttack() { }

	// RVA: 0x131D070 Offset: 0x1319070 VA: 0x131D070
	private void OnRocketAttack() { }

	// RVA: 0x131D08C Offset: 0x131908C VA: 0x131D08C
	private void OnFlashAttack() { }

	// RVA: 0x131D0A8 Offset: 0x13190A8 VA: 0x131D0A8
	private void Attack4IdleStart() { }

	// RVA: 0x131D0C4 Offset: 0x13190C4 VA: 0x131D0C4
	private void Attack4IdleStop() { }

	// RVA: 0x131D0E0 Offset: 0x13190E0 VA: 0x131D0E0
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class Boss9_AnimationEvents : MonoBehaviour // TypeDefIndex: 196
{
	// Fields
	public Action onAnimationEndedEvent; // 0x20
	public Action die; // 0x28
	public Action onAttackStartEvent; // 0x30
	public Action onAttackEndedEvent; // 0x38
	public Action<bool> onHandAttackEvent; // 0x40
	public Action onCircleAttackEvent; // 0x48
	public Action onDropAttackEvent; // 0x50
	public Action onCoreAttackEvent; // 0x58
	[SerializeField]
	private ParticleSystem fireParticle; // 0x60
	private AudioSource sfxFire; // 0x68

	// Methods

	// RVA: 0x131D0E8 Offset: 0x13190E8 VA: 0x131D0E8
	private void OnAnimationEndedEvent() { }

	// RVA: 0x131D104 Offset: 0x1319104 VA: 0x131D104
	private void OnDie() { }

	// RVA: 0x131D120 Offset: 0x1319120 VA: 0x131D120
	private void OnStartAttack() { }

	// RVA: 0x131D13C Offset: 0x131913C VA: 0x131D13C
	private void OnStopAttack() { }

	// RVA: 0x131D158 Offset: 0x1319158 VA: 0x131D158
	private void FireStart() { }

	// RVA: 0x131D234 Offset: 0x1319234 VA: 0x131D234
	private void FireStop() { }

	// RVA: 0x131D2D0 Offset: 0x13192D0 VA: 0x131D2D0
	private void AttackHandLeft() { }

	// RVA: 0x131D2F0 Offset: 0x13192F0 VA: 0x131D2F0
	private void AttackHandRight() { }

	// RVA: 0x131D310 Offset: 0x1319310 VA: 0x131D310
	private void AttackCircle() { }

	// RVA: 0x131D32C Offset: 0x131932C VA: 0x131D32C
	private void AttackDropDown() { }

	// RVA: 0x131D348 Offset: 0x1319348 VA: 0x131D348
	private void AttackCore() { }

	// RVA: 0x131D364 Offset: 0x1319364 VA: 0x131D364
	public void .ctor() { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class BossAnimationEvents : MonoBehaviour // TypeDefIndex: 205
{
	// Fields
	public Action onStateExit; // 0x20
	public Dictionary<string, Action> allStartAttackActions; // 0x28
	public Dictionary<string, Action> allStopAttackActions; // 0x30

	// Methods

	// RVA: 0x131DA8C Offset: 0x1319A8C VA: 0x131DA8C
	protected void OnStateExit() { }

	// RVA: 0x131DAA8 Offset: 0x1319AA8 VA: 0x131DAA8
	protected void OnStartAttack(string animName) { }

	// RVA: 0x131DB98 Offset: 0x1319B98 VA: 0x131DB98
	protected void OnStopAttack(string animName) { }

	// RVA: 0x131DC88 Offset: 0x1319C88 VA: 0x131DC88
	protected void Vibrate() { }

	// RVA: 0x131DCE4 Offset: 0x1319CE4 VA: 0x131DCE4
	public void .ctor() { }
}


// ===== keywords: Bullet, Spawn
// Namespace: 
public class BridgeSpawnBullets : MonoBehaviour // TypeDefIndex: 1508
{
	// Fields
	public RopeBridge ropeBridge; // 0x20
	[SerializeField]
	private int idBullet; // 0x28
	[SerializeField]
	private LayerMask targetLayer; // 0x2C
	[SerializeField]
	private float speed; // 0x30
	[SerializeField]
	private float lifetime; // 0x34
	[SerializeField]
	private float dmg; // 0x38
	[SerializeField]
	private int turnCount; // 0x3C

	// Methods

	// RVA: 0x1431724 Offset: 0x142D724 VA: 0x1431724
	private IEnumerator Start() { }

	// RVA: 0x14317AC Offset: 0x142D7AC VA: 0x14317AC
	private IEnumerator IESpawnBullet(float delay, Vector3 pos) { }

	// RVA: 0x1431860 Offset: 0x142D860 VA: 0x1431860
	protected void OnBulletCollided(GameObject obj, Vector3 pos, float dmg) { }

	// RVA: 0x1431A00 Offset: 0x142DA00 VA: 0x1431A00
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1431A1C Offset: 0x142DA1C VA: 0x1431A1C
	private void <IESpawnBullet>b__8_0(GameObject obj, Vector3 pos) { }
}


// ===== keywords: Tech, Stat
// Namespace: 
public sealed class CullingGroup.StateChanged : MulticastDelegate // TypeDefIndex: 7683
{
	// Methods

	// RVA: 0x275ED48 Offset: 0x275AD48 VA: 0x275ED48
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x275EDD4 Offset: 0x275ADD4 VA: 0x275EDD4 Slot: 12
	public virtual void Invoke(CullingGroupEvent sphere) { }
}


// ===== keywords: Shop, Data
// Namespace: 
public class DataShopPack : MonoBehaviour // TypeDefIndex: 988
{
	// Fields
	public static DataShopPack instance; // 0x0
	public Sprite[] allSpriteRewards; // 0x20
	public Sprite[] allRankSprites; // 0x28
	public Sprite[] listSpriteDrones; // 0x30
	public Sprite[] listSpritePlayers; // 0x38
	public Sprite[] listAvatars; // 0x40
	public Dictionary<int, Sprite> allDeviceIcons; // 0x48
	public Sprite cardPlayerRandomSprite; // 0x50
	public Sprite cardDroneRandomSprite; // 0x58
	public Sprite itemRandomSprite; // 0x60

	// Methods

	// RVA: 0x133EB84 Offset: 0x133AB84 VA: 0x133EB84
	private void Awake() { }

	// RVA: 0x133ECCC Offset: 0x133ACCC VA: 0x133ECCC
	public Sprite GetBoxSpriteGeneral(int _indexReward) { }

	// RVA: 0x133ED8C Offset: 0x133AD8C VA: 0x133ED8C
	public void .ctor() { }
}


// ===== keywords: Boss, Data
// Namespace: 
public class Data_Boss : ScriptableObject // TypeDefIndex: 769
{
	// Fields
	public Boss_Info[] allBosses; // 0x18

	// Methods

	// RVA: 0x12BFD48 Offset: 0x12BBD48 VA: 0x12BFD48
	public void .ctor() { }
}


// ===== keywords: Item, Data
// Namespace: 
public class Data_Items : ScriptableObject // TypeDefIndex: 739
{
	// Fields
	public ItemSprites[] allDropItems; // 0x18

	// Methods

	// RVA: 0x12B1B2C Offset: 0x12ADB2C VA: 0x12B1B2C
	public void .ctor() { }
}


// ===== keywords: Player, Data
// Namespace: 
public class Data_Players : ScriptableObject // TypeDefIndex: 815
{
	// Fields
	public Player_Info[] allPlayers; // 0x18

	// Methods

	// RVA: 0x12DCA70 Offset: 0x12D8A70 VA: 0x12DCA70
	public void .ctor() { }
}


// ===== keywords: Save, Data
// Namespace: 
public class Device_Saved_Data : MonoBehaviour // TypeDefIndex: 583
{
	// Fields
	public static string strDatas; // 0x0
	private static string key; // 0x8
	private static Dictionary<int, Device> allDevices; // 0x10
	public static int DeviceLevelDefault; // 0x18

	// Methods

	// RVA: 0x12572D0 Offset: 0x12532D0 VA: 0x12572D0
	public static void RefreshDatas() { }

	// RVA: 0x124F954 Offset: 0x124B954 VA: 0x124F954
	public static int GetDeviceLevelMax() { }

	// RVA: 0x1257328 Offset: 0x1253328 VA: 0x1257328
	private static void CheckRemoveDevices() { }

	// RVA: 0x12503FC Offset: 0x124C3FC VA: 0x12503FC
	public static List<Device> GetListDevices(FilterType typeFilter, int type = -1, bool onlyNotUse = False) { }

	// RVA: 0x12546D0 Offset: 0x12506D0 VA: 0x12546D0
	public static Device GetDevice(int instanceId) { }

	// RVA: 0x124E670 Offset: 0x124A670 VA: 0x124E670
	public static bool IsInUse(int instanceId) { }

	// RVA: 0x124E6D0 Offset: 0x124A6D0 VA: 0x124E6D0
	public static int GetPlayerUse(int instanceId) { }

	// RVA: 0x124D068 Offset: 0x1249068 VA: 0x124D068
	public static void Backup() { }

	// RVA: 0x1257A94 Offset: 0x1253A94 VA: 0x1257A94
	public static Dictionary<int, Device> GetAllDevices(string _strDatas) { }

	// RVA: 0x1257844 Offset: 0x1253844 VA: 0x1257844
	private static Dictionary<int, Device> GetAllDevices() { }

	// RVA: 0x124CE50 Offset: 0x1248E50 VA: 0x124CE50
	public static void AddDevice(Device device, bool newInstanceId = True) { }

	// RVA: 0x124F864 Offset: 0x124B864 VA: 0x124F864
	public static void RemoveDevice(Device device) { }

	// RVA: 0x124FA60 Offset: 0x124BA60 VA: 0x124FA60
	public static int GetNewInstanceId() { }

	// RVA: 0x1257468 Offset: 0x1253468 VA: 0x1257468
	private static List<Device> GetListSortDefault() { }

	// RVA: 0x1257C0C Offset: 0x1253C0C VA: 0x1257C0C
	private static void SortByLevel(ref List<Device> datas, int l, int r) { }

	// RVA: 0x1257DF8 Offset: 0x1253DF8 VA: 0x1257DF8
	public void .ctor() { }

	// RVA: 0x1257E00 Offset: 0x1253E00 VA: 0x1257E00
	private static void .cctor() { }
}


// ===== keywords: Laser, Drone
// Namespace: 
public class Drone10_Lasers : MonoBehaviour // TypeDefIndex: 285
{
	// Fields
	private bool moving; // 0x20
	private Vector3 dicrection; // 0x24
	private Vector3 end; // 0x30
	private float speed; // 0x3C
	[SerializeField]
	private LayerMask layerMask; // 0x40
	[SerializeField]
	private SpriteRenderer laser; // 0x48
	[SerializeField]
	private SpriteRenderer lightPoint; // 0x50
	[SerializeField]
	private SpriteRenderer hitPoint; // 0x58
	[SerializeField]
	private BoxCollider2D box; // 0x60
	[SerializeField]
	protected LayerMask targetLayer; // 0x68
	[SerializeField]
	private float width; // 0x6C

	// Methods

	// RVA: 0x141B7C4 Offset: 0x14177C4 VA: 0x141B7C4
	public void SetLaser(Vector3 start, Vector3 end, int direct) { }

	// RVA: 0x141BA7C Offset: 0x1417A7C VA: 0x141BA7C
	private void Update() { }

	// RVA: 0x141BB6C Offset: 0x1417B6C VA: 0x141BB6C
	private void OnTriggerStay2D(Collider2D other) { }

	// RVA: 0x141C060 Offset: 0x1418060 VA: 0x141C060
	private void AttackLaser() { }

	// RVA: 0x141BC64 Offset: 0x1417C64 VA: 0x141BC64
	private void OnBulletCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x141C4D4 Offset: 0x14184D4 VA: 0x141C4D4
	public void .ctor() { }
}


// ===== keywords: Data, Drone
// Namespace: 
public class Drone_Get_Datas : MonoBehaviour // TypeDefIndex: 291
{
	// Fields
	public static int[] MaxLevelPerRanks; // 0x0
	public static int[] CardUpgrades; // 0x8
	public static int[] StartRanks; // 0x10
	private static int[] UnlockNowCosts; // 0x18
	public static float[] BaseDamages; // 0x20
	private static float[] StartDroneSkillDamages; // 0x28
	private static int[] PlayerTimeStars; // 0x30
	private static int[] UnlockStarCosts; // 0x38
	private static float[] allAbiDroneCooldown; // 0x40
	public static float d1_shotRate; // 0x48
	public static float d1_shotSpeed; // 0x4C
	public static int d1_idBlt; // 0x50
	public static float d2_turnRate; // 0x54
	public static float d2_shotRate; // 0x58
	public static float d2_shotSpeed; // 0x5C
	public static int d2_idBlt; // 0x60
	public static int d2_turnNumber; // 0x64
	public static float d3_shotRate; // 0x68
	public static float d3_shotSpeed; // 0x6C
	public static int d3_idBlt; // 0x70
	public static int d3_turnNumber; // 0x74
	public static float d4_shotRate; // 0x78
	public static int d4_turnNumber; // 0x7C
	public static float d5_turnRate; // 0x80
	public static float d5_shotRate; // 0x84
	public static float d5_shotSpeed; // 0x88
	public static int d5_idBlt; // 0x8C
	public static int d5_turnNumber; // 0x90
	public static float d6_turnRate; // 0x94
	public static float d6_shotRate; // 0x98
	public static float d6_shotSpeed; // 0x9C
	public static int d6_idBlt; // 0xA0
	public static int d6_turnNumber; // 0xA4
	public static float d8_turnRate; // 0xA8
	public static float d8_shotRate; // 0xAC
	public static float d8_shotSpeed; // 0xB0
	public static int d8_idBlt; // 0xB4
	public static int d8_turnNumber; // 0xB8
	public static float d10_turnRate; // 0xBC
	public static float d10_shotRate; // 0xC0
	public static float d10_shotSpeed; // 0xC4
	public static int d10_idBlt; // 0xC8
	public static int d10_turnNumber; // 0xCC
	public static float d11_turnRate; // 0xD0
	public static float d11_shotRate; // 0xD4
	public static float d11_shotSpeed; // 0xD8
	public static int d11_idBlt; // 0xDC
	public static int d11_turnNumber; // 0xE0
	public static float d12_turnRate; // 0xE4
	public static float d12_shotRate; // 0xE8
	public static float d12_shotSpeed; // 0xEC
	public static int d12_idBlt; // 0xF0
	public static int d12_turnNumber; // 0xF4

	// Properties
	public static int CountDrones { get; }
	public static int MAX_RANK_INDEX { get; }
	public static bool IsOpenBoardDrone { get; set; }

	// Methods

	// RVA: 0x14D96FC Offset: 0x14D56FC VA: 0x14D96FC
	public static int get_CountDrones() { }

	// RVA: 0x14D9760 Offset: 0x14D5760 VA: 0x14D9760
	public static List<Cards> GetListCards(int number, int count, bool unlocked = False) { }

	// RVA: 0x14D9CA4 Offset: 0x14D5CA4 VA: 0x14D9CA4
	public static int get_MAX_RANK_INDEX() { }

	// RVA: 0x14D9D0C Offset: 0x14D5D0C VA: 0x14D9D0C
	public static int GetCostCraftDrone(int _droneIndex) { }

	// RVA: 0x14DA154 Offset: 0x14D6154 VA: 0x14DA154
	public static int GetUpgadeCostCoins(int _index, int lv) { }

	// RVA: 0x14DA1BC Offset: 0x14D61BC VA: 0x14DA1BC
	public static int GetUpgradeCostGems(int _index, int lv) { }

	// RVA: 0x14DA224 Offset: 0x14D6224 VA: 0x14DA224
	public static int GetUpgradeCostExp(int lv) { }

	// RVA: 0x14DA240 Offset: 0x14D6240 VA: 0x14DA240
	public static bool IsNoStarUnlock(int _droneIndex) { }

	// RVA: 0x14DA250 Offset: 0x14D6250 VA: 0x14DA250
	public static bool IsCanUnlockIAP(int _droneIndex) { }

	// RVA: 0x14DA260 Offset: 0x14D6260 VA: 0x14DA260
	public static bool IsNoUnlockGem(int _droneIndex) { }

	// RVA: 0x14DA270 Offset: 0x14D6270 VA: 0x14DA270
	public static int GetTimeStarUnlocks(int _droneIndex) { }

	// RVA: 0x14DA354 Offset: 0x14D6354 VA: 0x14DA354
	public static bool get_IsOpenBoardDrone() { }

	// RVA: 0x14DA3CC Offset: 0x14D63CC VA: 0x14DA3CC
	public static void set_IsOpenBoardDrone(bool value) { }

	// RVA: 0x14DA448 Offset: 0x14D6448 VA: 0x14DA448
	public static int GetUnlockStarCost(int _droneIndex) { }

	// RVA: 0x14DA60C Offset: 0x14D660C VA: 0x14DA60C
	public static int GetUnlockNowCost(int _droneIndex) { }

	// RVA: 0x14DA6F0 Offset: 0x14D66F0 VA: 0x14DA6F0
	public static float GetBaseDamage(int droneIndex, int rank = -1) { }

	// RVA: 0x14D8ED0 Offset: 0x14D4ED0 VA: 0x14D8ED0
	public static float GetDroneSkillDamage(int droneIndex) { }

	// RVA: 0x14DA9CC Offset: 0x14D69CC VA: 0x14DA9CC
	public static float GetDroneAbilityCooldown(int _indexSlot) { }

	// RVA: 0x14DAD0C Offset: 0x14D6D0C VA: 0x14DAD0C
	public static float GetDroneSkillAttackDuration(int _indexDrone) { }

	// RVA: 0x14DADBC Offset: 0x14D6DBC VA: 0x14DADBC
	public void .ctor() { }

	// RVA: 0x14DADC4 Offset: 0x14D6DC4 VA: 0x14DADC4
	private static void .cctor() { }
}


// ===== keywords: Bullet, Drop
// Namespace: 
public class Drop_AttackBulletCircle : MonoBehaviour // TypeDefIndex: 126
{
	// Fields
	[SerializeField]
	private Damager bltDamager; // 0x20
	[SerializeField]
	private int idFragment; // 0x28
	[SerializeField]
	private int numberFragment; // 0x2C
	[SerializeField]
	private float bltDamage; // 0x30
	[SerializeField]
	private float bltChildSpeed; // 0x34
	[SerializeField]
	private float bltChildLifetime; // 0x38
	[SerializeField]
	private float radius; // 0x3C
	[SerializeField]
	private LayerMask targetLayer; // 0x40
	[SerializeField]
	private int idFxDestroy; // 0x44
	[SerializeField]
	private float dist; // 0x48
	[SerializeField]
	private float rate; // 0x4C

	// Methods

	// RVA: 0x1243ABC Offset: 0x123FABC VA: 0x1243ABC
	private void Start() { }

	// RVA: 0x1243B5C Offset: 0x123FB5C VA: 0x1243B5C
	protected void Attack() { }

	// RVA: 0x1243E2C Offset: 0x123FE2C VA: 0x1243E2C Slot: 4
	protected virtual void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1243EAC Offset: 0x123FEAC VA: 0x1243EAC Slot: 5
	protected virtual void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1244020 Offset: 0x1240020 VA: 0x1244020
	private void OnEnable() { }

	// RVA: 0x1244040 Offset: 0x1240040 VA: 0x1244040
	private IEnumerator IEControlAttack() { }

	// RVA: 0x12440C8 Offset: 0x12400C8 VA: 0x12440C8
	public void .ctor() { }
}


// ===== keywords: Bullet, Drop
// Namespace: 
public class Drop_Bullet : MonoBehaviour // TypeDefIndex: 128
{
	// Fields
	[SerializeField]
	private Damager bltDamager; // 0x20
	[SerializeField]
	private int idFragment; // 0x28
	[SerializeField]
	private float bltDamage; // 0x2C
	[SerializeField]
	private float bltChildSpeed; // 0x30
	[SerializeField]
	private float bltChildLifetime; // 0x34
	[SerializeField]
	private LayerMask targetLayer; // 0x38
	[SerializeField]
	private int idFxDestroy; // 0x3C
	[SerializeField]
	private Transform parentPoints; // 0x40
	[SerializeField]
	private float rate; // 0x48

	// Methods

	// RVA: 0x1244418 Offset: 0x1240418 VA: 0x1244418
	private void Start() { }

	// RVA: 0x12444B8 Offset: 0x12404B8 VA: 0x12444B8
	protected void Attack() { }

	// RVA: 0x1244720 Offset: 0x1240720 VA: 0x1244720 Slot: 4
	protected virtual void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x12447A0 Offset: 0x12407A0 VA: 0x12447A0 Slot: 5
	protected virtual void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1244914 Offset: 0x1240914 VA: 0x1244914
	private void OnEnable() { }

	// RVA: 0x1244934 Offset: 0x1240934 VA: 0x1244934
	private IEnumerator IEControlAttack() { }

	// RVA: 0x12449BC Offset: 0x12409BC VA: 0x12449BC
	public void .ctor() { }
}


// ===== keywords: Enemy, Data
// Namespace: 
public class Enemy_Data_Balance : MonoBehaviour // TypeDefIndex: 222
{
	// Fields
	public static List<int> listStaticEmemies; // 0x0

	// Methods

	// RVA: 0x132075C Offset: 0x131C75C VA: 0x132075C
	public static int GetBonusCoin(int id) { }

	// RVA: 0x1320984 Offset: 0x131C984 VA: 0x1320984
	public static int GetBonusExp(int id) { }

	// RVA: 0x13209B0 Offset: 0x131C9B0 VA: 0x13209B0
	public static int GetSurvivalScore(int id) { }

	// RVA: 0x1320C14 Offset: 0x131CC14 VA: 0x1320C14
	public static int GetArenaScore(int idE, float timeLife) { }

	// RVA: 0x1320CC4 Offset: 0x131CCC4 VA: 0x1320CC4
	private static int GetPVPPlayScore(int idE, float timeLife) { }

	// RVA: 0x1320FBC Offset: 0x131CFBC VA: 0x1320FBC
	private static int GetArenaPlayScore(int idE, float timeLife) { }

	// RVA: 0x13211D8 Offset: 0x131D1D8 VA: 0x13211D8
	public void .ctor() { }

	// RVA: 0x13211E0 Offset: 0x131D1E0 VA: 0x13211E0
	private static void .cctor() { }
}


// ===== keywords: Bullet, Event
// Namespace: 
public class EventBullet : MonoBehaviour // TypeDefIndex: 87
{
	// Fields
	public Action<GameObject> destroyCallback; // 0x20

	// Methods

	// RVA: 0x123E3AC Offset: 0x123A3AC VA: 0x123E3AC
	public void OnDestroyed(GameObject a, Vector3 p) { }

	// RVA: 0x123E3E4 Offset: 0x123A3E4 VA: 0x123E3E4
	public void .ctor() { }
}


// ===== keywords: Analytics, Firebase
// Namespace: 
public sealed class FirebaseAnalyticsInternalPINVOKE.SWIGExceptionHelper.ExceptionArgumentDelegate : MulticastDelegate // TypeDefIndex: 10760
{
	// Methods

	// RVA: 0x1643020 Offset: 0x163F020 VA: 0x1643020
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x16430D4 Offset: 0x163F0D4 VA: 0x16430D4 Slot: 12
	public virtual void Invoke(string message, string paramName) { }
}


// ===== keywords: Analytics, Firebase
// Namespace: 
public sealed class FirebaseAnalyticsInternalPINVOKE.SWIGExceptionHelper.ExceptionDelegate : MulticastDelegate // TypeDefIndex: 10759
{
	// Methods

	// RVA: 0x1642F84 Offset: 0x163EF84 VA: 0x1642F84
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x16430C0 Offset: 0x163F0C0 VA: 0x16430C0 Slot: 12
	public virtual void Invoke(string message) { }
}


// ===== keywords: Analytics, Firebase
// Namespace: 
public sealed class FirebaseAnalyticsInternalPINVOKE.SWIGStringHelper.SWIGStringDelegate : MulticastDelegate // TypeDefIndex: 10763
{
	// Methods

	// RVA: 0x164329C Offset: 0x163F29C VA: 0x164329C
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x1643338 Offset: 0x163F338 VA: 0x1643338 Slot: 12
	public virtual string Invoke(string message) { }
}


// ===== keywords: Data, Firebase
// Namespace: 
public class FirebaseDatabaseManager : MonoBehaviour // TypeDefIndex: 1485
{
	// Fields
	public static FirebaseDatabaseManager Instance; // 0x0
	private FirebaseDatabase firebaseDatabase; // 0x20

	// Methods

	// RVA: 0x142B5E4 Offset: 0x14275E4 VA: 0x142B5E4
	private void Awake() { }

	// RVA: 0x142B6D4 Offset: 0x14276D4 VA: 0x142B6D4
	private void Init() { }

	// RVA: 0x142B754 Offset: 0x1427754 VA: 0x142B754
	public static bool CanActive() { }

	// RVA: 0x142B7B0 Offset: 0x14277B0 VA: 0x142B7B0
	public void DeleteDatabase(string path, Action<bool> onComplete) { }

	// RVA: 0x142B7D0 Offset: 0x14277D0 VA: 0x142B7D0
	private IEnumerator IEDeleteDatabase(string path, Action<bool> onComplete) { }

	// RVA: 0x142B86C Offset: 0x142786C VA: 0x142B86C
	public void UploadDatabase(string path, string jsonValue, Action<bool> onComplete) { }

	// RVA: 0x142B960 Offset: 0x1427960 VA: 0x142B960
	private IEnumerator IEUploadDatabase(string path, string jsonValue, Action<bool> onComplete) { }

	// RVA: 0x142BA08 Offset: 0x1427A08 VA: 0x142BA08
	public void UploadDatabaseObj(string path, object obj, Action<bool> onComplete) { }

	// RVA: 0x142BAFC Offset: 0x1427AFC VA: 0x142BAFC
	private IEnumerator IEUploadDatabaseObj(string path, object obj, Action<bool> onComplete) { }

	// RVA: 0x142BBA4 Offset: 0x1427BA4 VA: 0x142BBA4
	public Coroutine DownloadDatabase(string path, Action<DataSnapshot> onComplete) { }

	// RVA: 0x142BD04 Offset: 0x1427D04 VA: 0x142BD04
	public void DownloadDatabaseQueryRank(string path, string property, int limited, Action<DataSnapshot> onComplete) { }

	// RVA: 0x142BE38 Offset: 0x1427E38 VA: 0x142BE38
	public void DownloadDatabaseQueryRankStartAt(string path, int score, string key, string property, int limited, Action<DataSnapshot> onComplete) { }

	// RVA: 0x142BF98 Offset: 0x1427F98 VA: 0x142BF98
	public void DownloadDatabaseQueryRankEndAt(string path, int score, string key, string property, int limited, Action<DataSnapshot> onComplete) { }

	// RVA: 0x142BC98 Offset: 0x1427C98 VA: 0x142BC98
	private IEnumerator IEDownloadDatabse(Query query, Action<DataSnapshot> onComplete) { }

	// RVA: 0x142C120 Offset: 0x1428120 VA: 0x142C120
	public Query Query(string path) { }

	// RVA: 0x142C13C Offset: 0x142813C VA: 0x142C13C
	public void AddEventOnChangeValue(string path, EventHandler<ValueChangedEventArgs> ValueChanged) { }

	// RVA: 0x142C16C Offset: 0x142816C VA: 0x142C16C
	public void RemoveEventOnChangeValue(string path, EventHandler<ValueChangedEventArgs> ValueChanged) { }

	// RVA: 0x142C19C Offset: 0x142819C VA: 0x142C19C
	public void AddEventOnChangeChild(string path, EventHandler<ChildChangedEventArgs> ChildChanged) { }

	// RVA: 0x142C1CC Offset: 0x14281CC VA: 0x142C1CC
	public void RemoveEventOnChangeChild(string path, EventHandler<ChildChangedEventArgs> ChildChanged) { }

	// RVA: 0x142C1FC Offset: 0x14281FC VA: 0x142C1FC
	public void .ctor() { }
}


// ===== keywords: Data, Firebase
// Namespace: 
private class FirebaseDatabaseManager.WaitTask : CustomYieldInstruction // TypeDefIndex: 1480
{
	// Fields
	private Task task; // 0x10

	// Properties
	public override bool keepWaiting { get; }

	// Methods

	// RVA: 0x142C204 Offset: 0x1428204 VA: 0x142C204
	public void .ctor(Task task) { }

	// RVA: 0x142C22C Offset: 0x142822C VA: 0x142C22C Slot: 7
	public override bool get_keepWaiting() { }
}


// ===== keywords: Firebase, Event
// Namespace: 
internal class FirebaseHandler.ApplicationFocusChangedEventArgs : EventArgs // TypeDefIndex: 10551
{
	// Fields
	[CompilerGenerated]
	private bool <HasFocus>k__BackingField; // 0x10

	// Properties
	public bool HasFocus { set; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x167BF78 Offset: 0x1677F78 VA: 0x167BF78
	public void set_HasFocus(bool value) { }

	// RVA: 0x167BE40 Offset: 0x1677E40 VA: 0x167BE40
	public void .ctor() { }
}


// ===== keywords: Shop, UI
// Namespace: 
public class FixUIShop : MonoBehaviour // TypeDefIndex: 1115
{
	// Fields
	[SerializeField]
	private GameObject packName; // 0x20
	[SerializeField]
	private Transform textObject; // 0x28
	[SerializeField]
	private float yIOS; // 0x30
	[SerializeField]
	private float yAndroid; // 0x34

	// Methods

	// RVA: 0x1381A6C Offset: 0x137DA6C VA: 0x1381A6C
	private void Start() { }

	// RVA: 0x1381C18 Offset: 0x137DC18 VA: 0x1381C18
	public void .ctor() { }
}


// ===== keywords: Skin, UI
// Namespace: 
internal sealed class GUISkin.SkinChangedDelegate : MulticastDelegate // TypeDefIndex: 9549
{
	// Methods

	// RVA: 0x27AE950 Offset: 0x27AA950 VA: 0x27AE950
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x27AE9D8 Offset: 0x27AA9D8 VA: 0x27AE9D8 Slot: 12
	public virtual void Invoke() { }
}


// ===== keywords: Chapter, Data
// Namespace: 
public class GenerateDataChapter2 : MonoBehaviour // TypeDefIndex: 1509
{
	// Fields
	public string pathEnemyChapter1; // 0x20
	public string pathEnemyChapter2; // 0x28
	public string pathWaveChapter1; // 0x30
	public string pathWaveChapter2; // 0x38
	public bool copy; // 0x40

	// Methods

	// RVA: 0x1431EBC Offset: 0x142DEBC VA: 0x1431EBC
	private void OnDrawGizmos() { }

	// RVA: 0x143203C Offset: 0x142E03C VA: 0x143203C
	private void ChangeEnemiesID() { }

	// RVA: 0x1431ED0 Offset: 0x142DED0 VA: 0x1431ED0
	private void CopyDatas() { }

	// RVA: 0x1432044 Offset: 0x142E044 VA: 0x1432044
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1432040 Offset: 0x142E040 VA: 0x1432040
	internal static void <CopyDatas>g__EditPrefabs|7_0(GameObject copy) { }
}


// ===== keywords: Config, Stat
// Namespace: 
private struct InternalLiveContentAdapterService.<>c__DisplayClass6_0.<<GetConfigsContent>b__0>d : IAsyncStateMachine // TypeDefIndex: 10079
{
	// Fields
	public int <>1__state; // 0x0
	public AsyncTaskMethodBuilder<List<ConfigContentData>> <>t__builder; // 0x8
	public InternalLiveContentAdapterService.<>c__DisplayClass6_0 <>4__this; // 0x20
	private TaskAwaiter<Response<List<ClientFileWithContent>>> <>u__1; // 0x28

	// Methods

	// RVA: 0x264C964 Offset: 0x2648964 VA: 0x264C964 Slot: 4
	private void MoveNext() { }

	[DebuggerHidden]
	// RVA: 0x264CC58 Offset: 0x2648C58 VA: 0x264CC58 Slot: 5
	private void SetStateMachine(IAsyncStateMachine stateMachine) { }
}


// ===== keywords: Shop, Stat
// Namespace: 
private struct InternalWebshopService.<>c__DisplayClass7_0.<<GetWebshopLink>b__0>d : IAsyncStateMachine // TypeDefIndex: 10213
{
	// Fields
	public int <>1__state; // 0x0
	public AsyncTaskMethodBuilder<WebshopLinkData> <>t__builder; // 0x8
	public InternalWebshopService.<>c__DisplayClass7_0 <>4__this; // 0x20
	private TaskAwaiter<Response<WebshopLink>> <>u__1; // 0x28

	// Methods

	// RVA: 0x26C9B58 Offset: 0x26C5B58 VA: 0x26C9B58 Slot: 4
	private void MoveNext() { }

	[DebuggerHidden]
	// RVA: 0x26C9EBC Offset: 0x26C5EBC VA: 0x26C9EBC Slot: 5
	private void SetStateMachine(IAsyncStateMachine stateMachine) { }
}


// ===== keywords: Data, Language
// Namespace: 
public class LanguageStringData : ScriptableObject // TypeDefIndex: 1441
{
	// Fields
	public LanguageStringData.Item[] m_Items; // 0x18

	// Methods

	// RVA: 0x1423820 Offset: 0x141F820 VA: 0x1423820
	public void .ctor() { }
}


// ===== keywords: Language, UI
// Namespace: 
public class LanguageTextMeshProUI : MonoBehaviour // TypeDefIndex: 1373
{
	// Fields
	[SerializeField]
	private string key; // 0x20
	[SerializeField]
	private TextMeshProUGUI text; // 0x28

	// Methods

	// RVA: 0x13F12B4 Offset: 0x13ED2B4 VA: 0x13F12B4
	public void SetKey(string newKey) { }

	// RVA: 0x13F13D8 Offset: 0x13ED3D8 VA: 0x13F13D8
	private void OnDrawGizmos() { }

	// RVA: 0x13F142C Offset: 0x13ED42C VA: 0x13F142C
	private void Start() { }

	// RVA: 0x13F1524 Offset: 0x13ED524 VA: 0x13F1524
	private void OnDestroy() { }

	// RVA: 0x13F12BC Offset: 0x13ED2BC VA: 0x13F12BC
	private void SetText() { }

	// RVA: 0x13F1618 Offset: 0x13ED618 VA: 0x13F1618
	public void .ctor() { }
}


// ===== keywords: Data, UI
// Namespace: 
internal sealed class MeshBuilder.AllocMeshData.Allocator : MulticastDelegate // TypeDefIndex: 4819
{
	// Methods

	// RVA: 0x286DDD8 Offset: 0x2869DD8 VA: 0x286DDD8
	public void .ctor(object object, IntPtr method) { }

	// RVA: 0x286DE64 Offset: 0x2869E64 VA: 0x286DE64 Slot: 12
	public virtual MeshWriteData Invoke(uint vertexCount, uint indexCount, ref MeshBuilder.AllocMeshData allocatorData) { }
}


// ===== keywords: Boss, Event
// Namespace: 
public class MiniBoss1_Events : MonoBehaviour // TypeDefIndex: 217
{
	// Fields
	public Action onAttack1Ended; // 0x20
	public Action onAttack2Ended; // 0x28

	// Methods

	// RVA: 0x131F2BC Offset: 0x131B2BC VA: 0x131F2BC
	private void OnAttack1Ended() { }

	// RVA: 0x131F2D8 Offset: 0x131B2D8 VA: 0x131F2D8
	private void OnAttack2Ended() { }

	// RVA: 0x131F2F4 Offset: 0x131B2F4 VA: 0x131F2F4
	public void .ctor() { }
}


// ===== keywords: Root, Pass
// Namespace: 
private class ObjectStorage.TempAssemblyComparer : IEqualityComparer<KeyValuePair<Type, XmlRootAttribute>> // TypeDefIndex: 6477
{
	// Fields
	internal static readonly IEqualityComparer<KeyValuePair<Type, XmlRootAttribute>> s_default; // 0x0

	// Methods

	// RVA: 0x23932CC Offset: 0x238F2CC VA: 0x23932CC
	private void .ctor() { }

	// RVA: 0x23932D4 Offset: 0x238F2D4 VA: 0x23932D4 Slot: 4
	public bool Equals(KeyValuePair<Type, XmlRootAttribute> x, KeyValuePair<Type, XmlRootAttribute> y) { }

	// RVA: 0x2393400 Offset: 0x238F400 VA: 0x2393400 Slot: 5
	public int GetHashCode(KeyValuePair<Type, XmlRootAttribute> obj) { }

	// RVA: 0x239345C Offset: 0x238F45C VA: 0x239345C
	private static void .cctor() { }
}


// ===== keywords: PvP, Mode
// Namespace: 
public class PVPMode_Hunter : MonoBehaviour // TypeDefIndex: 879
{
	// Fields
	[SerializeField]
	private ScrollView scrollView; // 0x20

	// Methods

	// RVA: 0x12F95F8 Offset: 0x12F55F8 VA: 0x12F95F8
	private void OnEnable() { }

	// RVA: 0x12F9680 Offset: 0x12F5680 VA: 0x12F9680
	public void .ctor() { }
}


// ===== keywords: Player, PvP
// Namespace: 
public class PVPRankDisplayer : MonoBehaviour // TypeDefIndex: 883
{
	// Fields
	[SerializeField]
	private GameObject loading; // 0x20
	[SerializeField]
	private Transform rankParent; // 0x28
	public int rank; // 0x30
	public int level; // 0x34
	public int stars; // 0x38
	private static bool isLoaded; // 0x0
	private static PVPLogo[] allObjRanks; // 0x8

	// Methods

	// RVA: 0x12F9688 Offset: 0x12F5688 VA: 0x12F9688
	private void LoadObjRanks() { }

	// RVA: 0x12F5F6C Offset: 0x12F1F6C VA: 0x12F5F6C
	public IEnumerator IELoadRanks(int index, Action<PVPRankDisplayer, PVPLogo> callback, int rank = 0, int level = 0, int stars = 0) { }

	// RVA: 0x12F98A8 Offset: 0x12F58A8 VA: 0x12F98A8
	public void .ctor() { }
}


// ===== keywords: Item, PvP
// Namespace: 
public class PVPRankItem : MonoBehaviour // TypeDefIndex: 886
{
	// Fields
	[SerializeField]
	private SpriteRenderer[] bgRens; // 0x20
	[SerializeField]
	private Color[] bgColors; // 0x28
	[SerializeField]
	private Sprite sprMine; // 0x30
	[SerializeField]
	private Sprite sprDefault; // 0x38
	[SerializeField]
	private TextMeshPro textRankNum; // 0x40
	[SerializeField]
	private SpriteRenderer boxRankNumRen; // 0x48
	[SerializeField]
	private Sprite[] rankSprs; // 0x50
	[SerializeField]
	private TextMeshPro textName; // 0x58
	[SerializeField]
	private Color[] nameColors; // 0x60
	[SerializeField]
	private SpriteRenderer avatarRen; // 0x68
	[SerializeField]
	private PVPRankDisplayer parentRanks; // 0x70
	[SerializeField]
	private GameObject loadingAvatar; // 0x78
	public Action<PVPRankItem> onClick; // 0x80
	public string id; // 0x88

	// Methods

	// RVA: 0x12F9D6C Offset: 0x12F5D6C VA: 0x12F9D6C
	public void OnClick() { }

	// RVA: 0x12F39F4 Offset: 0x12EF9F4 VA: 0x12F39F4
	public void Setup(string id, UserPointDataLeagues datas, int rank, bool isMine = False, bool autoLoadAvatar = True) { }

	// RVA: 0x12F51D4 Offset: 0x12F11D4 VA: 0x12F51D4
	public void LoadAvatar(Action callback) { }

	// RVA: 0x12F9D94 Offset: 0x12F5D94 VA: 0x12F9D94
	public void .ctor() { }
}


// ===== keywords: Item, PvP
// Namespace: 
public class PVPSummaryItem : MonoBehaviour // TypeDefIndex: 888
{
	// Fields
	[SerializeField]
	private SpriteRenderer[] bgRens; // 0x20
	[SerializeField]
	private Color[] bgColors; // 0x28
	[SerializeField]
	private Sprite sprMine; // 0x30
	[SerializeField]
	private Sprite sprDefault; // 0x38
	[SerializeField]
	private TextMeshPro textRankNum; // 0x40
	[SerializeField]
	private SpriteRenderer boxRankNumRen; // 0x48
	[SerializeField]
	private Sprite[] rankSprs; // 0x50
	[SerializeField]
	private TextMeshPro textName; // 0x58
	[SerializeField]
	private Color[] nameColors; // 0x60
	[SerializeField]
	private SpriteRenderer avatarRen; // 0x68
	[SerializeField]
	private TextMeshPro textScore; // 0x70
	[SerializeField]
	private TextMeshPro textReward; // 0x78
	[SerializeField]
	private GameObject loading; // 0x80
	public string id; // 0x88

	// Methods

	// RVA: 0x12FA248 Offset: 0x12F6248 VA: 0x12FA248
	public void Setup(string id, int rank, int score, int point, int medal, bool isMine = False) { }

	// RVA: 0x12FA740 Offset: 0x12F6740 VA: 0x12FA740
	public void .ctor() { }
}


// ===== keywords: Shop, PvP
// Namespace: 
public class PVP_Shop : MonoBehaviour // TypeDefIndex: 912
{
	// Fields
	[SerializeField]
	private TextMeshPro textMedal; // 0x20
	[SerializeField]
	private TextMeshPro textTimeReset; // 0x28
	[SerializeField]
	private Transform parentPlayer; // 0x30
	[SerializeField]
	private Transform parentDrone; // 0x38
	[SerializeField]
	private Transform parentItems; // 0x40
	[SerializeField]
	private Transform parentMedal; // 0x48
	[SerializeField]
	private ScrollView scrollView; // 0x50
	[SerializeField]
	private BoxCollider2D bound; // 0x58
	public Action onExit; // 0x60
	[SerializeField]
	private Shop_Cell[] listItemPlayers; // 0x68
	[SerializeField]
	private Shop_Cell[] listItemDrones; // 0x70
	[SerializeField]
	private Shop_Cell[] listItemResources; // 0x78
	[SerializeField]
	private Transform parentItemPlayers; // 0x80
	[SerializeField]
	private Transform parentItemDrones; // 0x88
	[SerializeField]
	private Transform parentItemResources; // 0x90
	private int MaxStockCount; // 0x98
	private int ItemPlayerValue; // 0x9C
	private int ItemPlayerCost; // 0xA0
	private int ItemDroneValue; // 0xA4
	private int ItemDroneCost; // 0xA8
	private int[] ItemResourceValues; // 0xB0
	private int[] ItemResourceCost; // 0xB8
	[SerializeField]
	private Popup_PVPShopExchange popupExchange; // 0xC0
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0xC8
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0xD0
	[SerializeField]
	private Transform pointMedalTop; // 0xD8
	[SerializeField]
	private Transform pointMedalBot; // 0xE0
	[SerializeField]
	private SpriteRenderer cover; // 0xE8
	[SerializeField]
	private SpriteRenderer shopCover; // 0xF0
	private double timeToReset; // 0xF8

	// Methods

	// RVA: 0x130364C Offset: 0x12FF64C VA: 0x130364C
	private void OnEnable() { }

	// RVA: 0x1304748 Offset: 0x1300748 VA: 0x1304748
	public void OnPressedButtonEsc() { }

	// RVA: 0x130485C Offset: 0x130085C VA: 0x130485C
	private void OnDrawGizmos() { }

	// RVA: 0x1303F40 Offset: 0x12FFF40 VA: 0x1303F40
	public void InitShop() { }

	// RVA: 0x1303868 Offset: 0x12FF868 VA: 0x1303868
	private void ResetShop() { }

	// RVA: 0x130499C Offset: 0x130099C VA: 0x130499C
	private int GetIdItem(int index) { }

	// RVA: 0x12F7DB4 Offset: 0x12F3DB4 VA: 0x12F7DB4
	public static int GetStockItem(int index) { }

	// RVA: 0x1304A40 Offset: 0x1300A40 VA: 0x1304A40
	private void SetStockItem(int index, int stock) { }

	// RVA: 0x1304AE8 Offset: 0x1300AE8 VA: 0x1304AE8
	private void OnClickPlayerItem(Shop_Cell cell) { }

	// RVA: 0x13047E4 Offset: 0x13007E4 VA: 0x13047E4
	private IEnumerator IEShopHide(Action callback) { }

	[SerializeField]
	// RVA: 0x13046E0 Offset: 0x13006E0 VA: 0x13046E0
	private IEnumerator IEShopAppear() { }

	// RVA: 0x130504C Offset: 0x130104C VA: 0x130504C
	private IEnumerator IEFadeCover(float alphaTo, Action callback) { }

	// RVA: 0x13050D4 Offset: 0x13010D4 VA: 0x13050D4
	private IEnumerator IEMoveObject(Transform objMove, Vector3 target, Action callback) { }

	// RVA: 0x1305170 Offset: 0x1301170 VA: 0x1305170
	private IEnumerator IEUpdateTime() { }

	// RVA: 0x13051D8 Offset: 0x13011D8 VA: 0x13051D8
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x13052B0 Offset: 0x13012B0 VA: 0x13052B0
	private void <OnPressedButtonEsc>b__10_0() { }

	[CompilerGenerated]
	// RVA: 0x13052F8 Offset: 0x13012F8 VA: 0x13052F8
	internal static void <OnClickPlayerItem>g__SetEffect|31_0(int _number, Sprite _sprite, Transform _parent) { }
}


// ===== keywords: Reward, PvP
// Namespace: 
public class PVP_TabReward : MonoBehaviour // TypeDefIndex: 913
{
	// Fields
	public TextMeshPro textRank; // 0x20
	public PVPRankDisplayer parentRanks; // 0x28
	public Box_Rewards[] allRewards; // 0x30
	public SpriteRenderer btnIcon; // 0x38
	public GameObject dot; // 0x40
	public Action<PVP_TabReward> onClick; // 0x48

	// Methods

	// RVA: 0x13071FC Offset: 0x13031FC VA: 0x13071FC
	public void OnClick() { }

	// RVA: 0x130721C Offset: 0x130321C VA: 0x130721C
	public void SetCollected(bool isCollected) { }

	// RVA: 0x1307270 Offset: 0x1303270 VA: 0x1307270
	public void .ctor() { }
}


// ===== keywords: Panel, Event
// Namespace: 
private class PanelEventHandler.PointerEvent : IPointerEvent // TypeDefIndex: 8790
{
	// Fields
	[CompilerGenerated]
	private int <pointerId>k__BackingField; // 0x10
	[CompilerGenerated]
	private string <pointerType>k__BackingField; // 0x18
	[CompilerGenerated]
	private bool <isPrimary>k__BackingField; // 0x20
	[CompilerGenerated]
	private int <button>k__BackingField; // 0x24
	[CompilerGenerated]
	private int <pressedButtons>k__BackingField; // 0x28
	[CompilerGenerated]
	private Vector3 <position>k__BackingField; // 0x2C
	[CompilerGenerated]
	private Vector3 <localPosition>k__BackingField; // 0x38
	[CompilerGenerated]
	private Vector3 <deltaPosition>k__BackingField; // 0x44
	[CompilerGenerated]
	private float <deltaTime>k__BackingField; // 0x50
	[CompilerGenerated]
	private int <clickCount>k__BackingField; // 0x54
	[CompilerGenerated]
	private float <pressure>k__BackingField; // 0x58
	[CompilerGenerated]
	private float <tangentialPressure>k__BackingField; // 0x5C
	[CompilerGenerated]
	private float <altitudeAngle>k__BackingField; // 0x60
	[CompilerGenerated]
	private float <azimuthAngle>k__BackingField; // 0x64
	[CompilerGenerated]
	private float <twist>k__BackingField; // 0x68
	[CompilerGenerated]
	private Vector2 <tilt>k__BackingField; // 0x6C
	[CompilerGenerated]
	private PenStatus <penStatus>k__BackingField; // 0x74
	[CompilerGenerated]
	private Vector2 <radius>k__BackingField; // 0x78
	[CompilerGenerated]
	private Vector2 <radiusVariance>k__BackingField; // 0x80
	[CompilerGenerated]
	private EventModifiers <modifiers>k__BackingField; // 0x88

	// Properties
	public int pointerId { get; set; }
	public string pointerType { get; set; }
	public bool isPrimary { get; set; }
	public int button { get; set; }
	public int pressedButtons { get; set; }
	public Vector3 position { get; set; }
	public Vector3 localPosition { get; set; }
	public Vector3 deltaPosition { get; set; }
	public float deltaTime { get; set; }
	public int clickCount { get; set; }
	public float pressure { get; set; }
	public float tangentialPressure { get; set; }
	public float altitudeAngle { get; set; }
	public float azimuthAngle { get; set; }
	public float twist { get; set; }
	public Vector2 tilt { get; set; }
	public PenStatus penStatus { get; set; }
	public Vector2 radius { get; set; }
	public Vector2 radiusVariance { get; set; }
	public EventModifiers modifiers { get; set; }
	public bool shiftKey { get; }
	public bool ctrlKey { get; }
	public bool commandKey { get; }
	public bool altKey { get; }
	public bool actionKey { get; }

	// Methods

	[CompilerGenerated]
	// RVA: 0x297E5FC Offset: 0x297A5FC VA: 0x297E5FC Slot: 4
	public int get_pointerId() { }

	[CompilerGenerated]
	// RVA: 0x297E604 Offset: 0x297A604 VA: 0x297E604
	private void set_pointerId(int value) { }

	[CompilerGenerated]
	// RVA: 0x297E60C Offset: 0x297A60C VA: 0x297E60C Slot: 5
	public string get_pointerType() { }

	[CompilerGenerated]
	// RVA: 0x297E614 Offset: 0x297A614 VA: 0x297E614
	private void set_pointerType(string value) { }

	[CompilerGenerated]
	// RVA: 0x297E61C Offset: 0x297A61C VA: 0x297E61C Slot: 6
	public bool get_isPrimary() { }

	[CompilerGenerated]
	// RVA: 0x297E624 Offset: 0x297A624 VA: 0x297E624
	private void set_isPrimary(bool value) { }

	[CompilerGenerated]
	// RVA: 0x297E630 Offset: 0x297A630 VA: 0x297E630 Slot: 7
	public int get_button() { }

	[CompilerGenerated]
	// RVA: 0x297E638 Offset: 0x297A638 VA: 0x297E638
	private void set_button(int value) { }

	[CompilerGenerated]
	// RVA: 0x297E640 Offset: 0x297A640 VA: 0x297E640 Slot: 8
	public int get_pressedButtons() { }

	[CompilerGenerated]
	// RVA: 0x297E648 Offset: 0x297A648 VA: 0x297E648
	private void set_pressedButtons(int value) { }

	[CompilerGenerated]
	// RVA: 0x297E650 Offset: 0x297A650 VA: 0x297E650 Slot: 9
	public Vector3 get_position() { }

	[CompilerGenerated]
	// RVA: 0x297E65C Offset: 0x297A65C VA: 0x297E65C
	private void set_position(Vector3 value) { }

	[CompilerGenerated]
	// RVA: 0x297E668 Offset: 0x297A668 VA: 0x297E668 Slot: 10
	public Vector3 get_localPosition() { }

	[CompilerGenerated]
	// RVA: 0x297E674 Offset: 0x297A674 VA: 0x297E674
	private void set_localPosition(Vector3 value) { }

	[CompilerGenerated]
	// RVA: 0x297E680 Offset: 0x297A680 VA: 0x297E680 Slot: 11
	public Vector3 get_deltaPosition() { }

	[CompilerGenerated]
	// RVA: 0x297E68C Offset: 0x297A68C VA: 0x297E68C
	private void set_deltaPosition(Vector3 value) { }

	[CompilerGenerated]
	// RVA: 0x297E698 Offset: 0x297A698 VA: 0x297E698 Slot: 12
	public float get_deltaTime() { }

	[CompilerGenerated]
	// RVA: 0x297E6A0 Offset: 0x297A6A0 VA: 0x297E6A0
	private void set_deltaTime(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E6A8 Offset: 0x297A6A8 VA: 0x297E6A8 Slot: 13
	public int get_clickCount() { }

	[CompilerGenerated]
	// RVA: 0x297E6B0 Offset: 0x297A6B0 VA: 0x297E6B0
	private void set_clickCount(int value) { }

	[CompilerGenerated]
	// RVA: 0x297E6B8 Offset: 0x297A6B8 VA: 0x297E6B8 Slot: 14
	public float get_pressure() { }

	[CompilerGenerated]
	// RVA: 0x297E6C0 Offset: 0x297A6C0 VA: 0x297E6C0
	private void set_pressure(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E6C8 Offset: 0x297A6C8 VA: 0x297E6C8 Slot: 15
	public float get_tangentialPressure() { }

	[CompilerGenerated]
	// RVA: 0x297E6D0 Offset: 0x297A6D0 VA: 0x297E6D0
	private void set_tangentialPressure(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E6D8 Offset: 0x297A6D8 VA: 0x297E6D8 Slot: 16
	public float get_altitudeAngle() { }

	[CompilerGenerated]
	// RVA: 0x297E6E0 Offset: 0x297A6E0 VA: 0x297E6E0
	private void set_altitudeAngle(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E6E8 Offset: 0x297A6E8 VA: 0x297E6E8 Slot: 17
	public float get_azimuthAngle() { }

	[CompilerGenerated]
	// RVA: 0x297E6F0 Offset: 0x297A6F0 VA: 0x297E6F0
	private void set_azimuthAngle(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E6F8 Offset: 0x297A6F8 VA: 0x297E6F8 Slot: 18
	public float get_twist() { }

	[CompilerGenerated]
	// RVA: 0x297E700 Offset: 0x297A700 VA: 0x297E700
	private void set_twist(float value) { }

	[CompilerGenerated]
	// RVA: 0x297E708 Offset: 0x297A708 VA: 0x297E708 Slot: 19
	public Vector2 get_tilt() { }

	[CompilerGenerated]
	// RVA: 0x297E710 Offset: 0x297A710 VA: 0x297E710
	private void set_tilt(Vector2 value) { }

	[CompilerGenerated]
	// RVA: 0x297E718 Offset: 0x297A718 VA: 0x297E718 Slot: 20
	public PenStatus get_penStatus() { }

	[CompilerGenerated]
	// RVA: 0x297E720 Offset: 0x297A720 VA: 0x297E720
	private void set_penStatus(PenStatus value) { }

	[CompilerGenerated]
	// RVA: 0x297E728 Offset: 0x297A728 VA: 0x297E728 Slot: 21
	public Vector2 get_radius() { }

	[CompilerGenerated]
	// RVA: 0x297E730 Offset: 0x297A730 VA: 0x297E730
	private void set_radius(Vector2 value) { }

	[CompilerGenerated]
	// RVA: 0x297E738 Offset: 0x297A738 VA: 0x297E738 Slot: 22
	public Vector2 get_radiusVariance() { }

	[CompilerGenerated]
	// RVA: 0x297E740 Offset: 0x297A740 VA: 0x297E740
	private void set_radiusVariance(Vector2 value) { }

	[CompilerGenerated]
	// RVA: 0x297E748 Offset: 0x297A748 VA: 0x297E748 Slot: 23
	public EventModifiers get_modifiers() { }

	[CompilerGenerated]
	// RVA: 0x297E750 Offset: 0x297A750 VA: 0x297E750
	private void set_modifiers(EventModifiers value) { }

	// RVA: 0x297E758 Offset: 0x297A758 VA: 0x297E758 Slot: 24
	public bool get_shiftKey() { }

	// RVA: 0x297E764 Offset: 0x297A764 VA: 0x297E764 Slot: 25
	public bool get_ctrlKey() { }

	// RVA: 0x297E770 Offset: 0x297A770 VA: 0x297E770 Slot: 26
	public bool get_commandKey() { }

	// RVA: 0x297E77C Offset: 0x297A77C VA: 0x297E77C Slot: 27
	public bool get_altKey() { }

	// RVA: 0x297E788 Offset: 0x297A788 VA: 0x297E788 Slot: 28
	public bool get_actionKey() { }

	// RVA: 0x297E084 Offset: 0x297A084 VA: 0x297E084
	public void Read(PanelEventHandler self, PointerEventData eventData, PanelEventHandler.PointerEventType eventType) { }

	// RVA: 0x297E548 Offset: 0x297A548 VA: 0x297E548
	public void SetPosition(Vector3 positionOverride, Vector3 deltaOverride) { }

	// RVA: 0x297E5F4 Offset: 0x297A5F4 VA: 0x297E5F4
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x297E81C Offset: 0x297A81C VA: 0x297E81C
	internal static bool <Read>g__InRange|90_0(int i, int start, int count) { }
}


// ===== keywords: Item, Panel
// Namespace: 
public class Panel_Items : MonoBehaviour // TypeDefIndex: 1125
{
	// Fields
	[SerializeField]
	private TextMeshPro textInfo; // 0x20
	[SerializeField]
	private Transform parentItems; // 0x28
	[SerializeField]
	private Transform itemSelected; // 0x30
	[SerializeField]
	private Popup_BuyItem popupScript; // 0x38
	[SerializeField]
	protected GameObject popupFollowTut; // 0x40
	private Item_Slot[] listSlots; // 0x48
	private Transform oldSlot; // 0x50
	private GameObject efxFocusButton; // 0x58
	[SerializeField]
	private SpriteRenderer iconBtnPlayRenderer; // 0x60
	private int countItemSelected; // 0x68

	// Properties
	public static bool IsVipFreeItems { get; set; }
	public static int IndexItemFree { get; set; }

	// Methods

	// RVA: 0x1385E54 Offset: 0x1381E54 VA: 0x1385E54
	public static bool get_IsVipFreeItems() { }

	// RVA: 0x1385ECC Offset: 0x1381ECC VA: 0x1385ECC
	public static void set_IsVipFreeItems(bool value) { }

	// RVA: 0x1385F48 Offset: 0x1381F48 VA: 0x1385F48
	public static int get_IndexItemFree() { }

	// RVA: 0x1385FB4 Offset: 0x1381FB4 VA: 0x1385FB4
	public static void set_IndexItemFree(int value) { }

	// RVA: 0x1386024 Offset: 0x1382024 VA: 0x1386024
	public static void AddTimeFree(double duration) { }

	// RVA: 0x1386230 Offset: 0x1382230 VA: 0x1386230
	private void Awake() { }

	// RVA: 0x1386348 Offset: 0x1382348 VA: 0x1386348
	private void OnEnable() { }

	// RVA: 0x138769C Offset: 0x138369C VA: 0x138769C
	private IEnumerator IEUpdateTimeFree() { }

	// RVA: 0x13876FC Offset: 0x13836FC VA: 0x13876FC
	public static void ResetFreeItem() { }

	// RVA: 0x1386CAC Offset: 0x1382CAC VA: 0x1386CAC
	public void OnPressedButtonItem(Transform button) { }

	// RVA: 0x1386ADC Offset: 0x1382ADC VA: 0x1386ADC
	private int GetItemCount() { }

	// RVA: 0x1387C68 Offset: 0x1383C68 VA: 0x1387C68
	private void OnEndBuyItems() { }

	// RVA: 0x1386B54 Offset: 0x1382B54 VA: 0x1386B54
	private void Refresh() { }

	// RVA: 0x13875FC Offset: 0x13835FC VA: 0x13875FC
	private string GetStringItemInfo(int itemIndex) { }

	// RVA: 0x1387414 Offset: 0x1383414 VA: 0x1387414
	private bool IsCanPlay() { }

	// RVA: 0x1387D60 Offset: 0x1383D60 VA: 0x1387D60
	public void .ctor() { }
}


// ===== keywords: Mission, Panel
// Namespace: 
public class Panel_Missions : MonoBehaviour // TypeDefIndex: 1127
{
	// Fields
	[SerializeField]
	private Stage_Mission[] listMissions; // 0x20
	[SerializeField]
	private Stage_Mission specialMission; // 0x28
	[SerializeField]
	private TextMeshPro textHeader; // 0x30
	[SerializeField]
	private Transform parentModes; // 0x38
	[SerializeField]
	private Transform modeSelected; // 0x40
	[SerializeField]
	private SpriteRenderer[] modeBorders; // 0x48
	[SerializeField]
	private Sprite[] modeSprs; // 0x50
	[SerializeField]
	private GameObject parentMissionNormals; // 0x58
	[SerializeField]
	private GameObject parentMissionSpecials; // 0x60
	[SerializeField]
	private TextMeshPro textCostForPlay; // 0x68
	[SerializeField]
	private SpriteRenderer iconBtnPlayRenderer; // 0x70
	[SerializeField]
	private SpriteRenderer header; // 0x78
	[SerializeField]
	private SpriteRenderer bgRen; // 0x80
	[SerializeField]
	private Sprite[] headerSprites; // 0x88
	[SerializeField]
	private Sprite[] bgSprites; // 0x90
	[SerializeField]
	private GameObject lightForBoss; // 0x98
	[SerializeField]
	private GameObject[] allExtendStarParents; // 0xA0
	[SerializeField]
	private GameObject btnNextLevel; // 0xA8
	[SerializeField]
	private GameObject btnPrevLevel; // 0xB0
	private int maxLvl; // 0xB8

	// Methods

	// RVA: 0x1388108 Offset: 0x1384108 VA: 0x1388108
	private void OnEnable() { }

	// RVA: 0x1388E9C Offset: 0x1384E9C VA: 0x1388E9C
	private void Start() { }

	// RVA: 0x1388F24 Offset: 0x1384F24 VA: 0x1388F24
	public void OnPressedButtonMode(Transform mode) { }

	// RVA: 0x1389038 Offset: 0x1385038 VA: 0x1389038
	public void OnPressedButtonNextLevel() { }

	// RVA: 0x1389618 Offset: 0x1385618 VA: 0x1389618
	public void OnPressedButtonPrevLevel() { }

	// RVA: 0x13890D0 Offset: 0x13850D0 VA: 0x13890D0
	private void UpdateButtons() { }

	// RVA: 0x1388C80 Offset: 0x1384C80 VA: 0x1388C80
	private void RefreshMissions() { }

	// RVA: 0x138835C Offset: 0x138435C VA: 0x138835C
	private void SetModes() { }

	// RVA: 0x13898BC Offset: 0x13858BC VA: 0x13898BC
	private IEnumerator DelaySetMode(int _modeMax) { }

	// RVA: 0x1384FAC Offset: 0x1380FAC VA: 0x1384FAC
	public void CheckStateButtonPlay() { }

	// RVA: 0x1389954 Offset: 0x1385954 VA: 0x1389954
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1389964 Offset: 0x1385964 VA: 0x1389964
	private void <Start>b__21_0(object obj) { }
}


// ===== keywords: Item, Panel
// Namespace: 
public class Panel_SelectItems : MonoBehaviour // TypeDefIndex: 1130
{
	// Fields
	[SerializeField]
	private Transform parentItems; // 0x20
	[SerializeField]
	private Popup_BuyItem popupScript; // 0x28
	private Item_Slot[] listSlots; // 0x30
	private Transform oldSlot; // 0x38
	[SerializeField]
	private GameObject cover; // 0x40
	[SerializeField]
	private BoxCollider2D box; // 0x48

	// Methods

	// RVA: 0x138A7B0 Offset: 0x13867B0 VA: 0x138A7B0
	private void Awake() { }

	// RVA: 0x138A8C8 Offset: 0x13868C8 VA: 0x138A8C8
	private void OnEnable() { }

	// RVA: 0x138AD10 Offset: 0x1386D10 VA: 0x138AD10
	public void OnPressedButtonItem(Transform button) { }

	// RVA: 0x138ACB0 Offset: 0x1386CB0 VA: 0x138ACB0
	private IEnumerator IEUpdateTimeFree() { }

	// RVA: 0x138B050 Offset: 0x1387050 VA: 0x138B050
	private void OnEndBuyItems() { }

	// RVA: 0x138AACC Offset: 0x1386ACC VA: 0x138AACC
	private void Refresh() { }

	// RVA: 0x138B1D8 Offset: 0x13871D8 VA: 0x138B1D8
	public void .ctor() { }
}


// ===== keywords: Player, Laser
// Namespace: 
public class Player19Laser : MonoBehaviour // TypeDefIndex: 309
{
	// Fields
	private float timeToHide; // 0x20
	private bool active; // 0x24
	private bool demo; // 0x25
	private bool isAttack; // 0x26
	private Transform target; // 0x28
	[SerializeField]
	private Transform parentRotate; // 0x30
	[SerializeField]
	private LineRenderer line; // 0x38
	[SerializeField]
	private GameObject lightObject; // 0x40
	[SerializeField]
	private Player_Attack_19 playerAttack; // 0x48
	[SerializeField]
	private LayerMask targetLayer; // 0x50
	private float checkRange; // 0x54

	// Methods

	// RVA: 0x14DF994 Offset: 0x14DB994 VA: 0x14DF994
	public void SetLaser(float duration, bool demo) { }

	// RVA: 0x14DF9D0 Offset: 0x14DB9D0 VA: 0x14DF9D0
	private void OnEnable() { }

	// RVA: 0x14DFB40 Offset: 0x14DBB40 VA: 0x14DFB40
	private IEnumerator IEMoveTo(Transform moveObj, Vector3 lPos, Action callback, float spd = 24) { }

	// RVA: 0x14DFC00 Offset: 0x14DBC00 VA: 0x14DFC00
	private void Update() { }

	// RVA: 0x14E0220 Offset: 0x14DC220 VA: 0x14E0220
	private void Off() { }

	// RVA: 0x14E009C Offset: 0x14DC09C VA: 0x14E009C
	public void Hide() { }

	// RVA: 0x14DFCD0 Offset: 0x14DBCD0 VA: 0x14DFCD0
	private void RotateToTarget() { }

	// RVA: 0x14DFF7C Offset: 0x14DBF7C VA: 0x14DFF7C
	private void AttackLaser() { }

	// RVA: 0x14E0244 Offset: 0x14DC244 VA: 0x14E0244
	private void Check() { }

	// RVA: 0x14E084C Offset: 0x14DC84C VA: 0x14E084C
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x14E0878 Offset: 0x14DC878 VA: 0x14E0878
	private void <OnEnable>b__4_0() { }

	[CompilerGenerated]
	// RVA: 0x14E0884 Offset: 0x14DC884 VA: 0x14E0884
	private void <Hide>b__9_0() { }
}


// ===== keywords: Player, Event
// Namespace: 
public class PlayerInputNew : MonoBehaviour, IBeginDragHandler, IEventSystemHandler, IDragHandler, IEndDragHandler, IPointerDownHandler, IPointerUpHandler, IPointerExitHandler, IPointerEnterHandler // TypeDefIndex: 1430
{
	// Fields
	[SerializeField]
	private Camera cam; // 0x20
	public bool dragOnSurfaces; // 0x28
	private RectTransform m_DraggingPlane; // 0x30
	private bool touching; // 0x38

	// Methods

	// RVA: 0x141FE10 Offset: 0x141BE10 VA: 0x141FE10 Slot: 4
	public void OnBeginDrag(PointerEventData eventData) { }

	// RVA: 0x141FE14 Offset: 0x141BE14 VA: 0x141FE14 Slot: 5
	public void OnDrag(PointerEventData eventData) { }

	// RVA: 0x141FE18 Offset: 0x141BE18 VA: 0x141FE18
	private void SetDraggedPosition(PointerEventData data, int state) { }

	// RVA: 0x14201F4 Offset: 0x141C1F4 VA: 0x14201F4 Slot: 6
	public void OnEndDrag(PointerEventData eventData) { }

	// RVA: -1 Offset: -1
	public static T FindInParents<T>(GameObject go) { }
	/* GenericInstMethod :
	|
	|-RVA: 0x1740DD4 Offset: 0x173CDD4 VA: 0x1740DD4
	|-PlayerInputNew.FindInParents<object>
	*/

	// RVA: 0x142002C Offset: 0x141C02C VA: 0x142002C
	private void OnBegan(Vector3 position) { }

	// RVA: 0x14200C4 Offset: 0x141C0C4 VA: 0x14200C4
	private void OnMoved(Vector3 position) { }

	// RVA: 0x142015C Offset: 0x141C15C VA: 0x142015C
	private void OnEnded(Vector3 position) { }

	// RVA: 0x14201F8 Offset: 0x141C1F8 VA: 0x14201F8 Slot: 7
	public void OnPointerDown(PointerEventData eventData) { }

	// RVA: 0x1420214 Offset: 0x141C214 VA: 0x1420214 Slot: 8
	public void OnPointerUp(PointerEventData eventData) { }

	// RVA: 0x142022C Offset: 0x141C22C VA: 0x142022C Slot: 10
	public void OnPointerEnter(PointerEventData eventData) { }

	// RVA: 0x1420230 Offset: 0x141C230 VA: 0x1420230
	private void Update() { }

	// RVA: 0x1420284 Offset: 0x141C284 VA: 0x1420284 Slot: 9
	public void OnPointerExit(PointerEventData eventData) { }

	// RVA: 0x142029C Offset: 0x141C29C VA: 0x142029C
	public void .ctor() { }
}


// ===== keywords: Player, Data
// Namespace: 
public class Player_Get_Datas : MonoBehaviour // TypeDefIndex: 316
{
	// Fields
	public static string[] listRankStrings; // 0x0
	public static float TimeResetInvincible; // 0x8
	public static float TimeCanActiveInvincible; // 0xC
	public static float TouchRanger; // 0x10
	private static List<Player_Info> listAllPlayers; // 0x18
	private static List<int> listIdPlayerActived; // 0x20
	private static List<int> listIdPlayers; // 0x28
	private static Data_Players listPlayers; // 0x30
	private static int[] PlayerCosts; // 0x38
	public static List<int> listLegendaryPlayers; // 0x40
	public static Dictionary<int, int> listStarToTryLegendaryPlayers; // 0x48
	public static Dictionary<int, int> listStarToBuyLegendaryPlayers; // 0x50
	private static int[] PlayerTimeStars; // 0x58
	private static int[] PlayerStarCosts; // 0x60
	private static float stepCommon; // 0x68
	public static float StartHp; // 0x6C
	private static float BaseHpRecoverSpeed; // 0x70
	private static float[] StartMainCannonDamages; // 0x78
	private static float[] StartMainCannonRate; // 0x80
	private static float[] StartWingCannonDamages; // 0x88
	private static float StartMagnetRange; // 0x90
	private static float PercentFreeOverDrive; // 0x94
	private static float StartSecretWeaponDamage; // 0x98
	private static float StartSecretWeaponDuration; // 0x9C
	private static float StartMaxDuration; // 0xA0
	public static int p1_idBltNormal; // 0xA4
	public static int p1_idBltPowerUp; // 0xA8
	public static float p1_startShotRate; // 0xAC
	public static float p1_startBltSpeed; // 0xB0
	public static float p1_superPowerUpShotRate; // 0xB4
	public static float p1_superPowerUpBltSpeed; // 0xB8
	public static float p1_speedMainCannonBlt; // 0xBC
	public static float p1_radiusCheck; // 0xC0
	public static ParticleSystem.MinMaxCurve p2_normalLifetime; // 0xC8
	public static ParticleSystem.MinMaxCurve p2_normalSize; // 0xE8
	public static ParticleSystem.MinMaxCurve p2_supermodeLifetime; // 0x108
	public static float p2_speedMainCannonBlt; // 0x128
	public static int p3_idBltNormal; // 0x12C
	public static int p3_idBltPowerUp; // 0x130
	public static float p3_startShotRate; // 0x134
	public static float p3_startBltSpeed; // 0x138
	public static float p3_superPowerUpShotRate; // 0x13C
	public static float p3_superPowerUpBltSpeed; // 0x140
	public static float p3_speedMainCannonBlt; // 0x144
	public static float p4_radiusCheck; // 0x148
	public static float p4_radiusCheckMainCannon; // 0x14C
	public static float p4_speedMainCannonBlt; // 0x150
	public static int p5_idBltNormal; // 0x154
	public static int p5_idBltPowerUp; // 0x158
	public static float p5_startShotRate; // 0x15C
	public static float p5_startBltSpeed; // 0x160
	public static float p5_superPowerUpShotRate; // 0x164
	public static float p5_superPowerUpBltSpeed; // 0x168
	public static float p5_speedMainCannonBlt; // 0x16C
	public static int p6_idBltNormal; // 0x170
	public static int p6_idBltPowerUp; // 0x174
	public static float p6_startShotRate; // 0x178
	public static float p6_startBltSpeed; // 0x17C
	public static float p6_superPowerUpShotRate; // 0x180
	public static float p6_superPowerUpBltSpeed; // 0x184
	public static float p6_speedMainCannonBlt; // 0x188
	public static int p7_idBltNormal; // 0x18C
	public static int p7_idBltPowerUp; // 0x190
	public static float p7_startShotRate; // 0x194
	public static float p7_startBltSpeed; // 0x198
	public static float p7_superPowerUpShotRate; // 0x19C
	public static float p7_superPowerUpBltSpeed; // 0x1A0
	public static float p7_speedMainCannonBlt; // 0x1A4
	public static int p9_idBltNormal; // 0x1A8
	public static int p9_idBltPowerUp; // 0x1AC
	public static float p9_startShotRate; // 0x1B0
	public static float p9_startBltSpeed; // 0x1B4
	public static float p9_superPowerUpShotRate; // 0x1B8
	public static float p9_superPowerUpBltSpeed; // 0x1BC
	public static float p9_speedMainCannonBlt; // 0x1C0
	public static float shipCloneLifeTime; // 0x1C4
	public static float[] shipCloneDamage; // 0x1C8
	public static int p11_idBltNormal; // 0x1D0
	public static int p11_idBltPowerUp; // 0x1D4
	public static float p11_startShotRate; // 0x1D8
	public static float p11_startBltSpeed; // 0x1DC
	public static float p11_superPowerUpShotRate; // 0x1E0
	public static float p11_superPowerUpBltSpeed; // 0x1E4
	public static float p11_speedMainCannonBlt; // 0x1E8
	public static int p13_idBltNormal; // 0x1EC
	public static int p13_idBltPowerUp; // 0x1F0
	public static float p13_startShotRate; // 0x1F4
	public static float p13_startBltSpeed; // 0x1F8
	public static float p13_superPowerUpShotRate; // 0x1FC
	public static float p13_superPowerUpBltSpeed; // 0x200
	public static float p13_speedMainCannonBlt; // 0x204
	public static int p14_idBltNormal; // 0x208
	public static int p14_idBltPowerUp; // 0x20C
	public static float p14_startShotRate; // 0x210
	public static float p14_startBltSpeed; // 0x214
	public static float p14_superPowerUpShotRate; // 0x218
	public static float p14_superPowerUpBltSpeed; // 0x21C
	public static float p14_speedMainCannonBlt; // 0x220
	public static int p16_idBltNormal; // 0x224
	public static int p16_idBltPowerUp; // 0x228
	public static float p16_startShotRate; // 0x22C
	public static float p16_startBltSpeed; // 0x230
	public static float p16_superPowerUpShotRate; // 0x234
	public static float p16_superPowerUpBltSpeed; // 0x238
	public static float forceFieldDuration; // 0x23C
	public static int p17_idBltNormal; // 0x240
	public static int p17_idBltPowerUp; // 0x244
	public static float p17_startShotRate; // 0x248
	public static float p17_startBltSpeed; // 0x24C
	public static float p17_superPowerUpShotRate; // 0x250
	public static float p17_superPowerUpBltSpeed; // 0x254
	public static float p17_speedMainCannonBlt; // 0x258
	public static int p18_idBltNormal; // 0x25C
	public static int p18_idBltPowerUp; // 0x260
	public static float p18_startShotRate; // 0x264
	public static float p18_startBltSpeed; // 0x268
	public static float p18_superPowerUpShotRate; // 0x26C
	public static float p18_superPowerUpBltSpeed; // 0x270
	public static float p18_speedMainCannonBlt; // 0x274
	public static float p19_startShotRate; // 0x278
	public static float p19_superPowerUpShotRate; // 0x27C
	public static float p21_zoneDuration; // 0x280
	public static int p20_idBltNormal; // 0x284
	public static int p20_idBltPowerUp; // 0x288
	public static float p20_startShotRate; // 0x28C
	public static float p20_startBltSpeed; // 0x290
	public static float p20_superPowerUpShotRate; // 0x294
	public static float p20_superPowerUpBltSpeed; // 0x298
	public static float p20_speedMainCannonBlt; // 0x29C
	public static int p21_idBltNormal; // 0x2A0
	public static int p21_idBltPowerUp; // 0x2A4
	public static float p21_startShotRate; // 0x2A8
	public static float p21_startBltSpeed; // 0x2AC
	public static float p21_superPowerUpShotRate; // 0x2B0
	public static float p21_superPowerUpBltSpeed; // 0x2B4
	public static float p21_speedMainCannonBlt; // 0x2B8
	public static int p22_idBltNormal; // 0x2BC
	public static int p22_idBltPowerUp; // 0x2C0
	public static float p22_startShotRate; // 0x2C4
	public static float p22_startBltSpeed; // 0x2C8
	public static float p22_superPowerUpShotRate; // 0x2CC
	public static float p22_superPowerUpBltSpeed; // 0x2D0
	public static int p23_idBltNormal; // 0x2D4
	public static int p23_idBltPowerUp; // 0x2D8
	public static float p23_startShotRate; // 0x2DC
	public static float p23_startBltSpeed; // 0x2E0
	public static float p23_superPowerUpShotRate; // 0x2E4
	public static float p23_superPowerUpBltSpeed; // 0x2E8
	public static int p24_idBltNormal; // 0x2EC
	public static int p24_idBltPowerUp; // 0x2F0
	public static float p24_startShotRate; // 0x2F4
	public static float p24_startBltSpeed; // 0x2F8
	public static float p24_superPowerUpShotRate; // 0x2FC
	public static float p24_superPowerUpBltSpeed; // 0x300
	public static float[] PercentToCompleteMissions222; // 0x308
	public static float abi5GainHp; // 0x310
	public static float abi7AddPlayerStartHp; // 0x314
	public static float abi8AddDodgeRate; // 0x318
	public static float abi9ReduceREDDmg; // 0x31C
	public static float abi10ReduceREDDmg; // 0x320
	public static float abi11AddWingCannonDmg; // 0x324
	public static float abi14ReduceCooldown; // 0x328
	public static float abi17AddPowerPerKill; // 0x32C
	public static float abi19ReduceEnemyShotRate; // 0x330
	public static float abi20AddDmgSkillDrone; // 0x334
	public static float abi21AddDmgDrone; // 0x338
	public static float abi22AddAgilityRate; // 0x33C
	public static float abi23AddItemRate; // 0x340
	public static float abi24CritRate; // 0x344
	public static float abi25AddDroneShotRate; // 0x348
	public static float abi26AddDmgMelee; // 0x34C
	public static float abi27AddDmgMelee; // 0x350
	public static float abi29Amount; // 0x354
	public static float abi30Rate; // 0x358
	public static float abi30Amount; // 0x35C
	public static float abi31Rate; // 0x360
	public static float abi32Rate; // 0x364
	public static float abi34Rate; // 0x368

	// Properties
	public static bool IsOpenBoardPlayer { get; set; }
	public static float abi32Amount { get; }

	// Methods

	// RVA: 0x14E1B4C Offset: 0x14DDB4C VA: 0x14E1B4C
	private static bool IsRichCountry() { }

	// RVA: 0x14E1C40 Offset: 0x14DDC40 VA: 0x14E1C40
	public static int GetCostReborn(int _countReborn) { }

	// RVA: 0x14E1D48 Offset: 0x14DDD48 VA: 0x14E1D48
	public static int GetCostReborn2(int _countReborn) { }

	// RVA: 0x14E1E50 Offset: 0x14DDE50 VA: 0x14E1E50
	public static int GetMaxRebornCount(int vipLevel) { }

	// RVA: 0x14E1E80 Offset: 0x14DDE80 VA: 0x14E1E80
	public static List<int> GetListAllIdPlayers() { }

	// RVA: 0x14E22EC Offset: 0x14DE2EC VA: 0x14E22EC
	public static List<int> GetListAllIdPlayerActived() { }

	// RVA: 0x14E2348 Offset: 0x14DE348 VA: 0x14E2348
	public static List<int> GetAllShipNoUnlock() { }

	// RVA: 0x14E26F0 Offset: 0x14DE6F0 VA: 0x14E26F0
	public static bool IsUnlockedAll() { }

	// RVA: 0x14E27F8 Offset: 0x14DE7F8 VA: 0x14E27F8
	public static List<Cards> GetListCards(int number, int count, bool unlocked = False) { }

	// RVA: 0x14E1EDC Offset: 0x14DDEDC VA: 0x14E1EDC
	private static void GetListPlayers() { }

	// RVA: 0x14E2BB8 Offset: 0x14DEBB8 VA: 0x14E2BB8
	public static int GetRandomPlayerCard(bool unlocked = False) { }

	// RVA: 0x14E2CB8 Offset: 0x14DECB8 VA: 0x14E2CB8
	public static int GetCostUnlockPlayer(int _playerIndex) { }

	// RVA: 0x14E2D70 Offset: 0x14DED70 VA: 0x14E2D70
	public static double GetTimeStarUnlocks(int _playerIndex) { }

	// RVA: 0x14E2E34 Offset: 0x14DEE34 VA: 0x14E2E34
	public static bool get_IsOpenBoardPlayer() { }

	// RVA: 0x14E2EAC Offset: 0x14DEEAC VA: 0x14E2EAC
	public static void set_IsOpenBoardPlayer(bool value) { }

	// RVA: 0x14E2F28 Offset: 0x14DEF28 VA: 0x14E2F28
	public static int GetCostStarUnlockPlayer(int _playerIndex) { }

	// RVA: 0x14E30B8 Offset: 0x14DF0B8 VA: 0x14E30B8
	private static float stepLevel(int playerLv) { }

	// RVA: 0x14E311C Offset: 0x14DF11C VA: 0x14E311C
	public static float GetStartHp() { }

	// RVA: 0x14E318C Offset: 0x14DF18C VA: 0x14E318C
	public static float GetHpStatPercent() { }

	// RVA: 0x14E326C Offset: 0x14DF26C VA: 0x14E326C
	public static float GetGainHpItem() { }

	// RVA: 0x14E351C Offset: 0x14DF51C VA: 0x14E351C
	public static float GetGainHpItemAddOverTime() { }

	// RVA: 0x14E3784 Offset: 0x14DF784 VA: 0x14E3784
	public static float GetGainHpItemAddTime() { }

	// RVA: 0x14E378C Offset: 0x14DF78C VA: 0x14E378C
	public static float GetHpRecoverSpeed() { }

	// RVA: 0x14E3890 Offset: 0x14DF890 VA: 0x14E3890
	public static float TimeToImmuneOneHit() { }

	// RVA: 0x14E3948 Offset: 0x14DF948 VA: 0x14E3948
	public static float GetMainCannonDamage(int playerIndex) { }

	// RVA: 0x14E3C40 Offset: 0x14DFC40 VA: 0x14E3C40
	public static float GetMainCannonStatPercent() { }

	// RVA: 0x14E3CD8 Offset: 0x14DFCD8 VA: 0x14E3CD8
	public static float GetMainCannonRate(int playerIndex) { }

	// RVA: 0x14E3D6C Offset: 0x14DFD6C VA: 0x14E3D6C
	public static float GetMainCannonRatePercent() { }

	// RVA: 0x14E3E24 Offset: 0x14DFE24 VA: 0x14E3E24
	public static float GetMainCannonCritPercent() { }

	// RVA: 0x14E3EDC Offset: 0x14DFEDC VA: 0x14E3EDC
	public static float GetWingCannonDamage(int playerIndex) { }

	// RVA: 0x14E414C Offset: 0x14E014C VA: 0x14E414C
	public static float GetWingCannonDamageByBase(int playerIndex) { }

	// RVA: 0x14E41C8 Offset: 0x14E01C8 VA: 0x14E41C8
	public static float GetWingCannonDamageByTech(int playerIndex) { }

	// RVA: 0x14E40B4 Offset: 0x14E00B4 VA: 0x14E40B4
	public static float GetWingCannonStatPercent() { }

	// RVA: 0x14E4254 Offset: 0x14E0254 VA: 0x14E4254
	public static float AddPowerPercentWhenHpBelow30() { }

	// RVA: 0x14E4304 Offset: 0x14E0304 VA: 0x14E4304
	public static float KillPercentWhenEnemyHpBelow30() { }

	// RVA: 0x14E43BC Offset: 0x14E03BC VA: 0x14E43BC
	public static float GetMagnetRange() { }

	// RVA: 0x14E4438 Offset: 0x14E0438 VA: 0x14E4438
	public static float GetMagnetStatPercent() { }

	// RVA: 0x14E44E0 Offset: 0x14E04E0 VA: 0x14E44E0
	public static float GetPercentDropFreeOverDriveEvery30Seconds() { }

	// RVA: 0x14E453C Offset: 0x14E053C VA: 0x14E453C
	public static float GetTimeFreeOverdrive() { }

	// RVA: 0x14E4630 Offset: 0x14E0630 VA: 0x14E4630
	public static float GainHpPercentWhenUseOverDrive() { }

	// RVA: 0x14E46E0 Offset: 0x14E06E0 VA: 0x14E46E0
	public static float GetSecretWeaponDamage() { }

	// RVA: 0x14E4750 Offset: 0x14E0750 VA: 0x14E4750
	public static float GetSecretWeaponStatPercent() { }

	// RVA: 0x14E48FC Offset: 0x14E08FC VA: 0x14E48FC
	public static float GetSecretWeaponDuration() { }

	// RVA: 0x14E4A24 Offset: 0x14E0A24 VA: 0x14E4A24
	public static float GetTalentBombDamage() { }

	// RVA: 0x14E4B84 Offset: 0x14E0B84 VA: 0x14E4B84
	public static float GetTalentRocketDamage() { }

	// RVA: 0x14E4CDC Offset: 0x14E0CDC VA: 0x14E4CDC
	public static float GetTalentStunDamage() { }

	// RVA: 0x14E4E38 Offset: 0x14E0E38 VA: 0x14E4E38
	public static float GetTalentStunRanger() { }

	// RVA: 0x14E4EB4 Offset: 0x14E0EB4 VA: 0x14E4EB4
	public static float GetTalentInvisibleRanger() { }

	// RVA: 0x14E4F2C Offset: 0x14E0F2C VA: 0x14E4F2C
	public static float GetTalentLaserDamage() { }

	// RVA: 0x14E508C Offset: 0x14E108C VA: 0x14E508C
	public static float GetTalentMegaBombDamage() { }

	// RVA: 0x14E51F0 Offset: 0x14E11F0 VA: 0x14E51F0
	public static float GetTalentInvisible2Ranger() { }

	// RVA: 0x14E5268 Offset: 0x14E1268 VA: 0x14E5268
	public static float GetMaxChargeDuration() { }

	// RVA: 0x14E5380 Offset: 0x14E1380 VA: 0x14E5380
	public static int GetMaxCountRockets() { }

	// RVA: 0x14E5404 Offset: 0x14E1404 VA: 0x14E5404
	public static int GetStartPowerUpPoints() { }

	// RVA: 0x14E553C Offset: 0x14E153C VA: 0x14E553C
	public static int GetMaxPowerUpPoints() { }

	// RVA: 0x14E5618 Offset: 0x14E1618 VA: 0x14E5618
	public static float[] GetKillPercentMissionComplete(int _modeIndex) { }

	// RVA: 0x14E56D4 Offset: 0x14E16D4 VA: 0x14E56D4
	public static float[] GetBranchPercent2(int _modeIndex) { }

	// RVA: 0x14E5790 Offset: 0x14E1790 VA: 0x14E5790
	public static float[] GetBranchPercent1(int _modeIndex) { }

	// RVA: 0x14E5828 Offset: 0x14E1828 VA: 0x14E5828
	public static float[] GetBranchPercent3(int _modeIndex) { }

	// RVA: 0x14DBC84 Offset: 0x14D7C84 VA: 0x14DBC84
	public static float get_abi32Amount() { }

	// RVA: 0x14E58C0 Offset: 0x14E18C0 VA: 0x14E58C0
	public void .ctor() { }

	// RVA: 0x14E58C8 Offset: 0x14E18C8 VA: 0x14E58C8
	private static void .cctor() { }
}


// ===== keywords: Player, Sound
// Namespace: 
public class Player_Sounds : MonoBehaviour // TypeDefIndex: 317
{
	// Methods

	// RVA: 0x14E6284 Offset: 0x14E2284 VA: 0x14E6284
	public void .ctor() { }
}


// ===== keywords: Battle, Pass
// Namespace: 
public class PointBattlePass : MonoBehaviour // TypeDefIndex: 489
{
	// Fields
	public TextMeshPro textLevel; // 0x20
	public TextMeshPro textKill; // 0x28

	// Methods

	// RVA: 0x15DB1FC Offset: 0x15D71FC VA: 0x15DB1FC
	public void .ctor() { }
}


// ===== keywords: Popup, Event
// Namespace: 
public class Popup_AbilityEvent1 : MonoBehaviour // TypeDefIndex: 520
{
	// Fields
	[SerializeField]
	private AbilityEventTab[] allTabs; // 0x20
	[SerializeField]
	private Popup_Notices popupInfo; // 0x28
	[SerializeField]
	private Sprite[] allAbilitySprites; // 0x30
	[SerializeField]
	private Sprite defaultSprite; // 0x38
	[SerializeField]
	private TextMeshPro textTimer; // 0x40
	public Action exit; // 0x48
	[SerializeField]
	private bool noDisplayIcon; // 0x50

	// Methods

	// RVA: 0x15E8EE4 Offset: 0x15E4EE4 VA: 0x15E8EE4
	private void Start() { }

	// RVA: 0x15E927C Offset: 0x15E527C VA: 0x15E927C
	private void OnEnable() { }

	// RVA: 0x15E929C Offset: 0x15E529C VA: 0x15E929C
	private IEnumerator IEUpdateTimer() { }

	// RVA: 0x15E9324 Offset: 0x15E5324 VA: 0x15E9324
	public void OnPressedButtonExit() { }

	// RVA: 0x15E9368 Offset: 0x15E5368 VA: 0x15E9368
	public void OnPressedButtonInfo() { }

	// RVA: 0x15E9458 Offset: 0x15E5458 VA: 0x15E9458
	public void .ctor() { }
}


// ===== keywords: Shop, Popup
// Namespace: 
public class Popup_ArenaShopExchange : MonoBehaviour // TypeDefIndex: 466
{
	// Fields
	[SerializeField]
	private TextMeshPro textHeader; // 0x20
	[SerializeField]
	private TextMeshPro textStock; // 0x28
	[SerializeField]
	private TextMeshPro textCost; // 0x30
	[SerializeField]
	private TextMeshPro textCoinEvent; // 0x38
	[SerializeField]
	private SpriteRenderer btnIcon; // 0x40
	[SerializeField]
	private Slider slider; // 0x48
	public Action<int> onExit; // 0x50
	private int count; // 0x58
	private int maxStock; // 0x5C
	private Board_EventSeasonPass.EventRewards rewards; // 0x60
	[SerializeField]
	private Box_Rewards boxReward; // 0x68

	// Methods

	// RVA: 0x15C6E74 Offset: 0x15C2E74 VA: 0x15C6E74
	private void OnChange(float amount) { }

	// RVA: 0x15C71F4 Offset: 0x15C31F4 VA: 0x15C71F4
	public void SetPopup(int index, Board_EventSeasonPass.EventRewards eventReward, Action<int> exit) { }

	// RVA: 0x15C7598 Offset: 0x15C3598 VA: 0x15C7598
	private void SetEventRewardTabs() { }

	// RVA: 0x15C79D8 Offset: 0x15C39D8 VA: 0x15C79D8
	public void OnPressedButtonExit() { }

	// RVA: 0x15C7A20 Offset: 0x15C3A20 VA: 0x15C7A20
	public void OnPressedButtonBuy() { }

	// RVA: 0x15C7AD8 Offset: 0x15C3AD8 VA: 0x15C7AD8
	public void OnPressedButtonMinus() { }

	// RVA: 0x15C7B10 Offset: 0x15C3B10 VA: 0x15C7B10
	public void OnPressedButtonAdd() { }

	// RVA: 0x15C7B4C Offset: 0x15C3B4C VA: 0x15C7B4C
	public void .ctor() { }
}


// ===== keywords: Energy, Popup
// Namespace: 
public class Popup_BuyEnergy : Popup // TypeDefIndex: 685
{
	// Fields
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private TextMeshPro textValueBuyEnergy; // 0x30
	[SerializeField]
	private TextMeshPro textValueFreeEnergy; // 0x38
	[SerializeField]
	private TextMeshPro textCostBuyEnergy; // 0x40
	[SerializeField]
	private TextMeshPro textTimeAds; // 0x48
	[SerializeField]
	private Premium_Pack premiumPackScript; // 0x50
	[SerializeField]
	private GameObject popupIAP; // 0x58
	[SerializeField]
	private GameObject popupVideoNotReady; // 0x60
	private double totalSecs; // 0x68
	private const string keySysTime = "TimeFreeEnergy";
	private static int timeUpdate; // 0x4
	private double timeAds; // 0x70
	private Coroutine adsCoroutine; // 0x78

	// Methods

	// RVA: 0x128883C Offset: 0x128483C VA: 0x128883C
	private void OnEnable() { }

	// RVA: 0x1288A40 Offset: 0x1284A40 VA: 0x1288A40
	public void OnPressedButtonBuyPremiumPack() { }

	// RVA: 0x1288AD8 Offset: 0x1284AD8 VA: 0x1288AD8
	public void OnPressedButtonBuyEnergy() { }

	// RVA: 0x1288C38 Offset: 0x1284C38 VA: 0x1288C38
	public void OnPressedButtonFreeEnergy() { }

	// RVA: 0x128886C Offset: 0x128486C VA: 0x128886C
	private void Refresh() { }

	// RVA: 0x1288D10 Offset: 0x1284D10 VA: 0x1288D10
	private bool IsVideoLoaded() { }

	// RVA: 0x1288C28 Offset: 0x1284C28 VA: 0x1288C28
	private static int GetCostBuyEnergy() { }

	// RVA: 0x1288C30 Offset: 0x1284C30 VA: 0x1288C30
	private static int GetValueBuyEnergy() { }

	// RVA: 0x1288DDC Offset: 0x1284DDC VA: 0x1288DDC
	public static int GetExchangeGemsFromEnergy(int _energy) { }

	// RVA: 0x1288DD4 Offset: 0x1284DD4 VA: 0x1288DD4
	private int GetValueFreeEnergy() { }

	// RVA: 0x12889E0 Offset: 0x12849E0 VA: 0x12889E0
	private IEnumerator AdsTimer() { }

	// RVA: 0x1288D60 Offset: 0x1284D60 VA: 0x1288D60
	private bool IsTimeAdsReady() { }

	// RVA: 0x1288EAC Offset: 0x1284EAC VA: 0x1288EAC
	public void .ctor() { }

	// RVA: 0x1288EC0 Offset: 0x1284EC0 VA: 0x1288EC0
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x1288F10 Offset: 0x1284F10 VA: 0x1288F10
	private void <OnPressedButtonBuyPremiumPack>b__8_0(bool <p0>) { }

	[CompilerGenerated]
	// RVA: 0x1288FA4 Offset: 0x1284FA4 VA: 0x1288FA4
	private void <OnPressedButtonFreeEnergy>b__11_0(bool b) { }
}


// ===== keywords: Item, Popup
// Namespace: 
public class Popup_BuyItem : MonoBehaviour // TypeDefIndex: 1133
{
	// Fields
	[SerializeField]
	private TextMeshPro textHeader; // 0x20
	[SerializeField]
	private TextMeshPro textInfo; // 0x28
	[SerializeField]
	private TextMeshPro textNumber; // 0x30
	[SerializeField]
	private TextMeshPro textCost; // 0x38
	[SerializeField]
	private TextMeshPro textCost2; // 0x40
	[SerializeField]
	private TextMeshPro textCostFree; // 0x48
	[SerializeField]
	private TextMeshPro textLabelCost; // 0x50
	[SerializeField]
	private TextMeshPro textLabelCost2; // 0x58
	[SerializeField]
	private TextMeshPro textLabelCostFree; // 0x60
	[SerializeField]
	private SpriteRenderer boxNumberRenderer; // 0x68
	[SerializeField]
	private SpriteRenderer iconItemRenderer; // 0x70
	[SerializeField]
	private SpriteRenderer iconBtnBuyRenderer; // 0x78
	[SerializeField]
	private SpriteRenderer iconBtnBuyRenderer2; // 0x80
	[SerializeField]
	private SpriteRenderer iconBtnBuyRendererFree; // 0x88
	[SerializeField]
	private Sprite[] listIconSprites; // 0x90
	public Action exit; // 0x98
	[SerializeField]
	private Popup_Notices popupNoGems; // 0xA0
	[SerializeField]
	private GameObject popupIAP; // 0xA8
	[SerializeField]
	private Transform btnFree; // 0xB0
	[SerializeField]
	private Transform btnBuy2; // 0xB8
	private int itemIndex; // 0xC0
	private int number; // 0xC4
	private int addNumber2; // 0xC8
	[SerializeField]
	private Popup_Notices popupVideoNotReady; // 0xD0
	[SerializeField]
	private Popup_Notices popupNetworkNotConnected; // 0xD8
	private bool isVideoReady; // 0xE0
	private bool waiting; // 0xE1

	// Methods

	// RVA: 0x138B5C4 Offset: 0x13875C4 VA: 0x138B5C4
	private void Awake() { }

	// RVA: 0x1387798 Offset: 0x1383798 VA: 0x1387798
	public void SetPopup(int itemIndex, Action exit) { }

	// RVA: 0x138B9DC Offset: 0x13879DC VA: 0x138B9DC
	public void OnPressedButtonExit() { }

	// RVA: 0x138BA20 Offset: 0x1387A20 VA: 0x138BA20
	public void OnPressedButtonBuyItems(int _number) { }

	// RVA: 0x138BCF0 Offset: 0x1387CF0 VA: 0x138BCF0
	public void OnPressedButtonFreeItems() { }

	// RVA: 0x138BF60 Offset: 0x1387F60 VA: 0x138BF60
	private IEnumerator IECounter(int time, TextMeshPro txtDisp, Action callback) { }

	// RVA: 0x138B64C Offset: 0x138764C VA: 0x138B64C
	private string GetStringItemInfo(int itemIndex) { }

	// RVA: 0x138B6EC Offset: 0x13876EC VA: 0x138B6EC
	private void Refresh() { }

	// RVA: 0x138C000 Offset: 0x1388000 VA: 0x138C000
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x138C010 Offset: 0x1388010 VA: 0x138C010
	private void <Awake>b__23_0(object <p0>) { }

	[CompilerGenerated]
	// RVA: 0x138C014 Offset: 0x1388014 VA: 0x138C014
	private void <OnPressedButtonFreeItems>b__30_1(bool ok) { }

	[CompilerGenerated]
	// RVA: 0x138C214 Offset: 0x1388214 VA: 0x138C214
	private void <OnPressedButtonFreeItems>b__30_3() { }
}


// ===== keywords: Coin, Popup
// Namespace: 
public class Popup_BuyMoreCoins : MonoBehaviour // TypeDefIndex: 1272
{
	// Fields
	[SerializeField]
	private TextMeshPro[] allTextValues; // 0x20
	[SerializeField]
	private TextMeshPro[] allTextVipPoint; // 0x28
	[SerializeField]
	private TextMeshPro[] allTextPrices; // 0x30
	[SerializeField]
	private GameObject packMedium; // 0x38
	[SerializeField]
	private GameObject packBig; // 0x40
	private int[] allValues; // 0x48
	private int[] allProducts; // 0x50
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x58
	private Coroutine checkTimeOut; // 0x60
	[SerializeField]
	private GameObject loadingObject; // 0x68
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x70
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x78

	// Methods

	// RVA: 0x13C1BFC Offset: 0x13BDBFC VA: 0x13C1BFC
	private void OnEnable() { }

	// RVA: 0x13C1E34 Offset: 0x13BDE34 VA: 0x13C1E34
	public void OnPressedButtonBuyPack(int index) { }

	// RVA: 0x13C2168 Offset: 0x13BE168 VA: 0x13C2168
	private void Purchase(int _id, Action<int, bool> _callback) { }

	// RVA: 0x13C2288 Offset: 0x13BE288 VA: 0x13C2288
	private void OnPurchased(int _idProduct, bool _successed) { }

	// RVA: 0x13C26A0 Offset: 0x13BE6A0 VA: 0x13C26A0
	private void CollectVip(int _point, Transform _pos) { }

	// RVA: 0x13C2108 Offset: 0x13BE108 VA: 0x13C2108
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x13C1DD4 Offset: 0x13BDDD4 VA: 0x13C1DD4
	private IEnumerator SetShopPrices() { }

	// RVA: 0x13C288C Offset: 0x13BE88C VA: 0x13C288C
	private void OnInitialized() { }

	// RVA: 0x13C2A08 Offset: 0x13BEA08 VA: 0x13C2A08
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x13C2AC0 Offset: 0x13BEAC0 VA: 0x13C2AC0
	private void <OnPurchased>b__11_0() { }
}


// ===== keywords: Gem, Popup
// Namespace: 
public class Popup_BuyMoreGems : MonoBehaviour // TypeDefIndex: 1279
{
	// Fields
	[SerializeField]
	private TextMeshPro textPriceCombo; // 0x20
	[SerializeField]
	private TextMeshPro textVipPointCombo; // 0x28
	[SerializeField]
	private TextMeshPro textValueGemCombo; // 0x30
	[SerializeField]
	private TextMeshPro textValueCoinCombo; // 0x38
	[SerializeField]
	private TextMeshPro[] allTextPackGemPrices; // 0x40
	[SerializeField]
	private TextMeshPro[] allTextPackGemVipPoints; // 0x48
	[SerializeField]
	private TextMeshPro[] allTextPackGemValues; // 0x50
	[SerializeField]
	private GameObject header; // 0x58
	[SerializeField]
	private GameObject[] allGroups; // 0x60
	[SerializeField]
	private GameObject[] tagHotSales; // 0x68
	private int valGemCombo; // 0x70
	private int valCoinCombo; // 0x74
	private int[] allPackGemValues; // 0x78
	private int idCombo; // 0x80
	private int[] idGemPacks; // 0x88
	[SerializeField]
	private TextMeshPro textTimePurchaseLimit; // 0x90
	[SerializeField]
	private TextMeshPro textCountSpecialQuantity; // 0x98
	private int indexPack; // 0xA0
	[SerializeField]
	private Popup_Notices popupReachVip; // 0xA8
	private Coroutine checkTimeOut; // 0xB0
	[SerializeField]
	private GameObject loadingObject; // 0xB8
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0xC0
	[SerializeField]
	private Popup_Notices popupInitialize; // 0xC8
	[SerializeField]
	private Shop_Cell[] allCells; // 0xD0

	// Methods

	// RVA: 0x13C3240 Offset: 0x13BF240 VA: 0x13C3240
	private void OnEnable() { }

	// RVA: 0x13C37B4 Offset: 0x13BF7B4 VA: 0x13C37B4
	private IEnumerator UpdateTimers(int group) { }

	// RVA: 0x13C3814 Offset: 0x13BF814 VA: 0x13C3814
	private bool IsCheckSaleSpecialPacks() { }

	// RVA: 0x13C3690 Offset: 0x13BF690 VA: 0x13C3690
	private bool IsCheckFirstSpecialPacks() { }

	// RVA: 0x13C3984 Offset: 0x13BF984 VA: 0x13C3984
	public void OnPressedButtonComboPack() { }

	// RVA: 0x13C3DB0 Offset: 0x13BFDB0 VA: 0x13C3DB0
	public void OnPressedButtonGemPack(int index) { }

	// RVA: 0x13C3C98 Offset: 0x13BFC98 VA: 0x13C3C98
	private void Purchase(int _id, Action<int, bool> _callback) { }

	// RVA: 0x13C4090 Offset: 0x13C0090 VA: 0x13C4090
	private void OnPurchased(int _idProduct, bool _successed) { }

	// RVA: 0x13C4EC4 Offset: 0x13C0EC4 VA: 0x13C4EC4
	private void CollectVip(int _point, Transform _pos) { }

	// RVA: 0x13C3C38 Offset: 0x13BFC38 VA: 0x13C3C38
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x13C4854 Offset: 0x13C0854 VA: 0x13C4854
	private void CheckFirstPurchaseBonus() { }

	// RVA: 0x13C3630 Offset: 0x13BF630 VA: 0x13C3630
	private IEnumerator SetShopPrices() { }

	// RVA: 0x13C50B0 Offset: 0x13C10B0 VA: 0x13C50B0
	private void OnInitialized() { }

	// RVA: 0x13C52AC Offset: 0x13C12AC VA: 0x13C52AC
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x13C4E70 Offset: 0x13C0E70 VA: 0x13C4E70
	private void <OnPurchased>g__ExitDone|26_0() { }
}


// ===== keywords: Speed, Popup
// Namespace: 
public class Popup_BuySpeed : Popup // TypeDefIndex: 709
{
	// Fields
	[SerializeField]
	private TextMeshPro[] textVipPoints; // 0x30
	[SerializeField]
	private TextMeshPro[] textPrices; // 0x38
	[SerializeField]
	private TextMeshPro textDuration; // 0x40
	public Action onBuy; // 0x48
	private double[] addDurations; // 0x50
	private int idPurchase; // 0x58
	private static double totalSecs; // 0x0
	private static int timeUpdate; // 0x8
	private static string keySysTime; // 0x10
	private static int MaxStockFreeGems; // 0x18
	[SerializeField]
	private TextMeshPro textTimeAds; // 0x60
	[SerializeField]
	private TextMeshPro textFreeCost; // 0x68
	private Coroutine checkTimeOut; // 0x70
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x78
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x80
	[SerializeField]
	private Popup_Notices popupVideoNotReady; // 0x88
	[SerializeField]
	private GameObject loadingObject; // 0x90
	[SerializeField]
	private Popup_Notices popupReachVip; // 0x98
	private bool isForeverPack; // 0xA0

	// Properties
	private static double timeAds { get; }
	public static int FreeGemStocks { get; set; }

	// Methods

	// RVA: 0x129E8A8 Offset: 0x129A8A8 VA: 0x129E8A8
	private void OnEnable() { }

	// RVA: 0x129E8E0 Offset: 0x129A8E0 VA: 0x129E8E0
	private IEnumerator IESetPrices() { }

	// RVA: 0x129E9C8 Offset: 0x129A9C8 VA: 0x129E9C8
	private void OnInitialized() { }

	// RVA: 0x129EC34 Offset: 0x129AC34 VA: 0x129EC34
	private static double get_timeAds() { }

	// RVA: 0x129E940 Offset: 0x129A940 VA: 0x129E940
	private IEnumerator IEAdsTimer() { }

	// RVA: 0x129ECC8 Offset: 0x129ACC8 VA: 0x129ECC8
	public static int get_FreeGemStocks() { }

	// RVA: 0x129ED34 Offset: 0x129AD34 VA: 0x129ED34
	public static void set_FreeGemStocks(int value) { }

	// RVA: 0x129EDA4 Offset: 0x129ADA4 VA: 0x129EDA4
	private void UpdateVideoButton() { }

	// RVA: 0x129F3FC Offset: 0x129B3FC VA: 0x129F3FC
	protected bool IsTimeAdsReady() { }

	// RVA: 0x129F4F8 Offset: 0x129B4F8 VA: 0x129F4F8
	public void OnPressedButtonWatchVideo() { }

	// RVA: 0x129F940 Offset: 0x129B940 VA: 0x129F940
	public void OnPressedButtonMonthPack() { }

	// RVA: 0x129FC60 Offset: 0x129BC60 VA: 0x129FC60
	public void OnPressedButtonForeverPack() { }

	// RVA: 0x129FC00 Offset: 0x129BC00 VA: 0x129FC00
	private IEnumerator CheckLoadingTimeOut() { }

	// RVA: 0x129FF58 Offset: 0x129BF58 VA: 0x129FF58
	private void OnPurchased(string id, string receipt) { }

	// RVA: 0x12A02E0 Offset: 0x129C2E0 VA: 0x12A02E0
	public void .ctor() { }

	// RVA: 0x12A0374 Offset: 0x129C374 VA: 0x12A0374
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x12A03E8 Offset: 0x129C3E8 VA: 0x12A03E8
	private void <OnPressedButtonWatchVideo>b__23_1(bool ok) { }

	[CompilerGenerated]
	// RVA: 0x129F80C Offset: 0x129B80C VA: 0x129F80C
	private void <OnPressedButtonWatchVideo>g__OnVideoSuccess|23_3() { }
}


// ===== keywords: Language, Popup
// Namespace: 
public class Popup_ChangeLanguages : MonoBehaviour // TypeDefIndex: 1011
{
	// Fields
	[SerializeField]
	private Transform parentItems; // 0x20
	[SerializeField]
	private Color activeColor; // 0x28
	[SerializeField]
	private Color deactiveColor; // 0x38
	[SerializeField]
	private ItemLanguage[] listItemLanguage; // 0x48
	[SerializeField]
	private GameObject itemTemplateObject; // 0x50
	private Transform btnCurrent; // 0x58
	private Language defaultLanguage; // 0x60
	private bool isApplying; // 0x64
	[SerializeField]
	private ScrollView scrollView; // 0x68

	// Methods

	// RVA: 0x1346E54 Offset: 0x1342E54 VA: 0x1346E54
	private void OnEnable() { }

	// RVA: 0x1347190 Offset: 0x1343190 VA: 0x1347190
	public void OnPressedButtonBack() { }

	// RVA: 0x13471C4 Offset: 0x13431C4 VA: 0x13471C4
	public void OnPressedButtonChooseLanguage(Transform btn) { }

	// RVA: 0x13472B4 Offset: 0x13432B4 VA: 0x13472B4
	public void OnPressedButtonApplyLanguage() { }

	// RVA: 0x1346E6C Offset: 0x1342E6C VA: 0x1346E6C
	private void SetBoard() { }

	// RVA: 0x1347464 Offset: 0x1343464 VA: 0x1347464
	public void .ctor() { }
}


// ===== keywords: Cheat, Popup
// Namespace: 
public class Popup_CheatTime : MonoBehaviour // TypeDefIndex: 1281
{
	// Fields
	[SerializeField]
	private TextMeshPro textTime; // 0x20
	public TextMeshPro textNotice; // 0x28
	[SerializeField]
	private Popup_Notices popupPay; // 0x30

	// Methods

	// RVA: 0x13C6244 Offset: 0x13C2244 VA: 0x13C6244
	private void OnEnable() { }

	// RVA: 0x13C6684 Offset: 0x13C2684 VA: 0x13C6684
	private IEnumerator IEUpdateTime() { }

	// RVA: 0x13C670C Offset: 0x13C270C VA: 0x13C670C
	public void OnPressedButtonPayFine() { }

	// RVA: 0x13C6290 Offset: 0x13C2290 VA: 0x13C6290
	private void ResetCheat() { }

	// RVA: 0x13C6738 Offset: 0x13C2738 VA: 0x13C6738
	public void .ctor() { }
}


// ===== keywords: Data, Popup
// Namespace: 
public class Popup_ChooseVersionDatas : Popup // TypeDefIndex: 46
{
	// Fields
	[SerializeField]
	private TextMeshPro textFBVersion; // 0x30
	[SerializeField]
	private TextMeshPro textFBGems; // 0x38
	[SerializeField]
	private TextMeshPro textFBCoins; // 0x40
	[SerializeField]
	private TextMeshPro textFBStars; // 0x48
	[SerializeField]
	private TextMeshPro textFBVipLvl; // 0x50
	[SerializeField]
	private Transform parentAllVip1; // 0x58
	[SerializeField]
	private TextMeshPro textDeVersion; // 0x60
	[SerializeField]
	private TextMeshPro textDeGems; // 0x68
	[SerializeField]
	private TextMeshPro textDeCoins; // 0x70
	[SerializeField]
	private TextMeshPro textDeStars; // 0x78
	[SerializeField]
	private TextMeshPro textDeVipLvl; // 0x80
	[SerializeField]
	private Transform parentAllVip2; // 0x88
	private Action<int> callback; // 0x90

	// Methods

	// RVA: 0x122DFAC Offset: 0x1229FAC VA: 0x122DFAC
	public void Setup(DataStruct serverDatas, DataStruct deviceDatas, Action<int> callback) { }

	// RVA: 0x1237050 Offset: 0x1233050 VA: 0x1237050
	public void OnPressedButtonChooseDataOnServer() { }

	// RVA: 0x1237088 Offset: 0x1233088 VA: 0x1237088
	public void OnPressedButtonChooseDataOnDevice() { }

	// RVA: 0x12370C0 Offset: 0x12330C0 VA: 0x12370C0
	public void .ctor() { }
}


// ===== keywords: Drone, Popup
// Namespace: 
public class Popup_DroneCraft : MonoBehaviour // TypeDefIndex: 607
{
	// Fields
	[SerializeField]
	private SpriteRenderer[] boxRenderers; // 0x20
	[SerializeField]
	private SpriteRenderer[] iconRenderers; // 0x28
	[SerializeField]
	private TextMeshPro textHeader; // 0x30
	[SerializeField]
	private TextMeshPro textUpgradeHeader; // 0x38
	[SerializeField]
	private TextMeshPro textMaxLvl; // 0x40
	[SerializeField]
	private TextMeshPro textDamage; // 0x48
	[SerializeField]
	private TextMeshPro textAbility; // 0x50
	[SerializeField]
	private TextMeshPro textProgress; // 0x58
	[SerializeField]
	private TextMeshPro textToCraft; // 0x60
	[SerializeField]
	private TextMeshPro textLabelCraft; // 0x68
	[SerializeField]
	private TextMeshPro textLabelCraftNow; // 0x70
	[SerializeField]
	private TextMeshPro textLabelCraftNowFake; // 0x78
	[SerializeField]
	private TextMeshPro textLabelCraftNowVipPoint; // 0x80
	[SerializeField]
	private SpriteRenderer btnCraftRenderer; // 0x88
	[SerializeField]
	private SpriteRenderer btnCraftNowRenderer; // 0x90
	[SerializeField]
	private SpriteRenderer progressRenderer; // 0x98
	[SerializeField]
	private string[] listColorHexStrings; // 0xA0
	[SerializeField]
	private Color[] toCraftColors; // 0xA8
	[SerializeField]
	private GameObject[] slots; // 0xB0
	[SerializeField]
	private GameObject evolveEffect; // 0xB8
	[SerializeField]
	private GameObject parentCraftNow; // 0xC0
	[SerializeField]
	private Transform boardParent; // 0xC8
	[SerializeField]
	private SpriteRenderer[] allBgParent; // 0xD0
	[SerializeField]
	private TextMeshPro textNoCards; // 0xD8
	[SerializeField]
	private Animator animBtnUpRank; // 0xE0
	private float[] playerPriceMultipleS; // 0xE8
	private float[] playerPriceMultipleSS; // 0xF0
	private float[] playerPriceMultipleX; // 0xF8
	private float[] playerPriceMultipleXX; // 0x100
	[SerializeField]
	private TextMeshPro textTimeOffer; // 0x108

	// Methods

	// RVA: 0x1267214 Offset: 0x1263214 VA: 0x1267214
	private void Start() { }

	// RVA: 0x12672A4 Offset: 0x12632A4 VA: 0x12672A4
	public void SetPopup(int _droneIndex, Sprite _avatar, ref Sprite[] listBoxSprites) { }

	// RVA: 0x126873C Offset: 0x126473C VA: 0x126873C
	private bool HasOffer(int _index, int _rank) { }

	// RVA: 0x1268860 Offset: 0x1264860 VA: 0x1268860
	private IEnumerator SetPrice(int _index, int _rank, int _maxRank) { }

	// RVA: 0x1268800 Offset: 0x1264800 VA: 0x1268800
	private IEnumerator SetTimer() { }

	// RVA: 0x1268934 Offset: 0x1264934 VA: 0x1268934
	public void .ctor() { }
}


// ===== keywords: Purchase, Popup
// Namespace: 
public class Popup_FirstPurchase : Popup // TypeDefIndex: 1049
{
	// Fields
	public Action eventExit; // 0x30
	[SerializeField]
	private TextMeshPro textTimeFirstPurchase; // 0x38
	[SerializeField]
	private TextMeshPro textXGems; // 0x40
	[SerializeField]
	private TextMeshPro textDesc; // 0x48

	// Methods

	// RVA: 0x1358A5C Offset: 0x1354A5C VA: 0x1358A5C
	private void OnEnable() { }

	// RVA: 0x1358C28 Offset: 0x1354C28 VA: 0x1358C28
	public void OnPressedButtonGo() { }

	// RVA: 0x1358CD8 Offset: 0x1354CD8 VA: 0x1358CD8 Slot: 5
	protected override void OffBoard() { }

	// RVA: 0x1358BC8 Offset: 0x1354BC8 VA: 0x1358BC8
	private IEnumerator UpdateTimers() { }

	// RVA: 0x1358D34 Offset: 0x1354D34 VA: 0x1358D34
	public void .ctor() { }
}


