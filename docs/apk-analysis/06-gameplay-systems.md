# Gameplay systems (from IL2CPP dump)

## Game modes

```csharp
// Namespace: 
public class GameMode : MonoBehaviour // TypeDefIndex: 253
{
	// Fields
	public static PlayMode playMode; // 0x0
	public static int indexBoss; // 0x4
	public static int waveIndex; // 0x8
	public static int indexChallange; // 0xC
	public static bool[] listChallangeMissionActived; // 0x10
	public static int indexTryPlayer; // 0x18
	public static int arenaRank; // 0x1C
	public static PVPMode pvpMode; // 0x20
	public static bool isPvPOnline; // 0x24
	public static bool isMaster; // 0x25
	public static int pvpMapIndex; // 0x28

	// Methods

	// RVA: 0x1327D58 Offset: 0x1323D58 VA: 0x1327D58
	public static bool IsActiveChallangeMissions(int _indexMission) { }

	// RVA: 0x1327E04 Offset: 0x1323E04 VA: 0x1327E04
	public void .ctor() { }

	// RVA: 0x1327E0C Offset: 0x1323E0C VA: 0x1327E0C
	private static void .cctor() { }
}

```




## Player / ship / drone / device classes

105 classes

| class | base |
|---|---|
| `Cards` |  |
| `Device` |  |
| `DeviceStats` | MonoBehaviour |
| `Device_Cell` | MonoBehaviour |
| `Device_Get_Data` | MonoBehaviour |
| `Device_Popup_Attention` | MonoBehaviour |
| `Device_Popup_Equip` | MonoBehaviour |
| `Device_Saved_Data` | MonoBehaviour |
| `Drone_Attack` | MonoBehaviour |
| `Drone_Attack1` | Drone_Attack |
| `Drone_Attack10` | Drone_Attack |
| `Drone_Attack11` | Drone_Attack |
| `Drone_Attack12` | Drone_Attack |
| `Drone_Attack2` | Drone_Attack |
| `Drone_Attack3` | Drone_Attack |
| `Drone_Attack4` | Drone_Attack |
| `Drone_Attack5` | Drone_Attack |
| `Drone_Attack6` | Drone_Attack |
| `Drone_Attack7` | Drone_Attack |
| `Drone_Attack8` | Drone_Attack |
| `Drone_Attack9` | Drone_Attack |
| `Drone_AutoRotate` | MonoBehaviour |
| `Drone_Childs` | MonoBehaviour |
| `Drone_Get_Datas` | MonoBehaviour |
| `Drone_Laser` | MonoBehaviour |
| `Drone_LerpStart` | MonoBehaviour |
| `Drone_Movement` | MonoBehaviour |
| `Drone_Saved_Datas` | MonoBehaviour |
| `Drone_Skill2_Lv1` | MonoBehaviour |
| `Player13_Clone` | MonoBehaviour |
| `Player14_Clone` | MonoBehaviour |
| `Player16TransformField` | MonoBehaviour |
| `Player19Laser` | MonoBehaviour |
| `Player21AttackZone` | MonoBehaviour |
| `Player23_Pumpkin` | MonoBehaviour |
| `Player24_TentaclePhysics` | MonoBehaviour |
| `Player24_Tentacles` | MonoBehaviour |
| `Player9_Clone` | MonoBehaviour |
| `Player_5_Lasers` | MonoBehaviour |
| `Player_Ability` | MonoBehaviour |
| `Player_Animations` | MonoBehaviour |
| `Player_Attack` | MonoBehaviour |
| `Player_Attack_1` | Player_Attack |
| `Player_Attack_10` | Player_Attack |
| `Player_Attack_11` | Player_Attack |
| `Player_Attack_12` | Player_Attack |
| `Player_Attack_13` | Player_Attack |
| `Player_Attack_14` | Player_Attack |
| `Player_Attack_15` | Player_Attack |
| `Player_Attack_16` | Player_Attack |
| `Player_Attack_17` | Player_Attack |
| `Player_Attack_17.Barrel` |  |
| `Player_Attack_18` | Player_Attack |
| `Player_Attack_19` | Player_Attack |
| `Player_Attack_2` | Player_Attack |
| `Player_Attack_20` | Player_Attack |
| `Player_Attack_21` | Player_Attack |
| `Player_Attack_22` | Player_Attack |
| `Player_Attack_23` | Player_Attack |
| `Player_Attack_24` | Player_Attack |
| `Player_Attack_3` | Player_Attack |
| `Player_Attack_4` | Player_Attack |
| `Player_Attack_5` | Player_Attack |
| `Player_Attack_6` | Player_Attack |
| `Player_Attack_7` | Player_Attack |
| `Player_Attack_8` | Player_Attack |
| `Player_Attack_9` | Player_Attack |
| `Player_Controller` | MonoBehaviour |
| `Player_Datas` | MonoBehaviour |
| `Player_Device_Saved_Datas` | MonoBehaviour |
| `Player_Effects` | MonoBehaviour |
| `Player_Get_Datas` | MonoBehaviour |
| `Player_Health` | MonoBehaviour |
| `Player_Ingame` | MonoBehaviour |
| `Player_Interfaces` | MonoBehaviour |
| `Player_Physics` | MonoBehaviour |
| `Player_Saved_Datas` | MonoBehaviour |
| `Player_Sounds` | MonoBehaviour |
| `Player_Talent` | MonoBehaviour |
| `Player_TouchAbility` | MonoBehaviour |
| `ShipBuffetPack` | MonoBehaviour |
| `ShipProtect` | MonoBehaviour |
| `ShipSalePack` | MonoBehaviour |
| `ShipSalePackItem` | MonoBehaviour |
| `ShipTrial` |  |
| `ShipTrialPack` | MonoBehaviour |
| `ShipTrialSalePack` | MonoBehaviour |
| `Ship_Physics` | MonoBehaviour |
| `Ship_Physics1` | MonoBehaviour |
| `Sub_Character` | Sub_Object, IHealth, IAlive, IDamageable |
| `Talent` | MonoBehaviour |
| `Talent_DropBomb` | MonoBehaviour |
| `Talent_Event` | MonoBehaviour |
| `Talent_Invisible` | MonoBehaviour |
| `Talent_Invisible1` | MonoBehaviour |
| `Talent_Lasers` | MonoBehaviour |
| `Talent_MegaBomb` | MonoBehaviour |
| `Talent_Stun` | MonoBehaviour |
| `Tech_Ability_Data` | ScriptableObject |
| `Tech_Basic` | MonoBehaviour |
| `Tech_Datas` | MonoBehaviour |
| `Tech_Display` | MonoBehaviour |
| `Tech_Popup` | MonoBehaviour |
| `Tech_Stat` | MonoBehaviour |
| `Tech_Talent` | MonoBehaviour |

### Key player classes

#### `Player_Ingame`

```csharp
// Namespace: SpaceShooter.Player
public class Player_Ingame : MonoBehaviour // TypeDefIndex: 1803
{
	// Fields
	[SerializeField]
	private GameObject fxSupperPower; // 0x20
	public bool IsBusy; // 0x28
	public bool IsTransforming; // 0x29
	private bool isSupperPower; // 0x2A
	public bool IsOnShield; // 0x2B
	private bool isAttacking; // 0x2C
	public bool skillActived; // 0x2D
	private static bool initOneHitShield; // 0x0
	public static bool hasOneHitShield; // 0x1
	private static int lv; // 0x4
	public float timeToResetSuperPowerUp; // 0x30
	private float superDuration; // 0x34
	public LayerMask targetLayer; // 0x38
	public Player_Attack currentPlayer; // 0x40
	public float[] timeDroneAbilityReady; // 0x48
	private bool isLockAll; // 0x50
	[SerializeField]
	private GameObject empEffect; // 0x58
	[SerializeField]
	private GameObject invisibleShield; // 0x60

	// Properties
	public bool IsPowerUp { get; set; }
	public bool IsAttacking { get; set; }
	public bool HasOneHitShield { get; }
	public int Level { get; set; }
	public float timeSuperPowerUp { get; }
	public bool IsLockAll { get; set; }

	// Methods

	// RVA: 0x14BB850 Offset: 0x14B7850 VA: 0x14BB850
	public bool get_IsPowerUp() { }

	// RVA: 0x14BB858 Offset: 0x14B7858 VA: 0x14BB858
	public void set_IsPowerUp(bool value) { }

	// RVA: 0x14B279C Offset: 0x14AE79C VA: 0x14B279C
	public bool get_IsAttacking() { }

	// RVA: 0x14BB8F4 Offset: 0x14B78F4 VA: 0x14BB8F4
	public void set_IsAttacking(bool value) { }

	// RVA: 0x14BB900 Offset: 0x14B7900 VA: 0x14BB900
	public void ResetStaticVariables() { }

	// RVA: 0x14BB960 Offset: 0x14B7960 VA: 0x14BB960
	public bool get_HasOneHitShield() { }

	// RVA: 0x14BBA4C Offset: 0x14B7A4C VA: 0x14BBA4C
	public void BreakShieldOneHit() { }

	// RVA: 0x14B1EB0 Offset: 0x14ADEB0 VA: 0x14B1EB0
	public int get_Level() { }

	// RVA: 0x14B21D8 Offset: 0x14AE1D8 VA: 0x14B21D8
	public void set_Level(int value) { }

	// RVA: 0x14BBAA4 Offset: 0x14B7AA4 VA: 0x14BBAA4
	public float get_timeSuperPowerUp() { }

	// RVA: 0x14BBCD8 Offset: 0x14B7CD8 VA: 0x14BBCD8
	public float GetDroneAbilityCooldown(int _indexSlot) { }

	// RVA: 0x14BBD50 Offset: 0x14B7D50 VA: 0x14BBD50
	public bool IsDroneAbilityReady(int _indexSlot) { }

	// RVA: 0x14BBDA0 Offset: 0x14B7DA0 VA: 0x14BBDA0
	public bool get_IsLockAll() { }

	// RVA: 0x14BBDA8 Offset: 0x14B7DA8 VA: 0x14BBDA8
	public void set_IsLockAll(bool value) { }

	// RVA: 0x14BBE38 Offset: 0x14B7E38 VA: 0x14BBE38
	public void ActiveInvisibleShield() { }

	// RVA: 0x14BBEC0 Offset: 0x14B7EC0 VA: 0x14BBEC0
	public void DeactiveInvisibleShield() { }

	// RVA: 0x14BBF48 Offset: 0x14B7F48 VA: 0x14BBF48
	public void OnDie() { }

	// RVA: 0x14BC008 Offset: 0x14B8008 VA: 0x14BC008
	public void OnReborn() { }

	// RVA: 0x14BC0C8 Offset: 0x14B80C8 VA: 0x14BC0C8
	public void .ctor() { }

	// RVA: 0x14BC138 Offset: 0x14B8138 VA: 0x14BC138
	private static void .cctor() { }
}

```

#### `Player_Attack`

```csharp
// Namespace: SpaceShooter.Player
public abstract class Player_Attack : MonoBehaviour // TypeDefIndex: 1744
{
	// Fields
	public int id; // 0x20
	public bool IsHpBelow30; // 0x24
	private Player_Ingame playerIngame; // 0x28
	[SerializeField]
	public bool demo; // 0x30
	private float timeInvisible; // 0x34
	protected float wingCannonPercent; // 0x38
	protected float mainCannonPercent; // 0x3C
	protected bool maincannonActived; // 0x40
	protected bool stopAttack; // 0x41
	protected int rank; // 0x44
	private float timeCanInvisible; // 0x48
	private Coroutine invisibleCoroutine; // 0x50
	public bool IsVictory; // 0x58
	protected float addPowerByDevice; // 0x5C
	protected float addRangeByDevice; // 0x60
	protected float addSpeedByDevice; // 0x64
	protected float addRateByDevice; // 0x68
	protected float addCritByDevice; // 0x6C
	protected float addPowerPerKill; // 0x70
	protected bool isAddPowerWhenKill; // 0x74

	// Properties
	protected Player_Ingame playerIngameScript { get; }
	public static int maxLv { get; }
	protected abstract float GetWingCannonDamage { get; }
	protected abstract float GetWingCannonMaxPowerDamage { get; }
	protected abstract float GetMainCannonDamage { get; }
	protected float xDmgByRank { get; }
	protected float dmgTechItem0 { get; }

	// Methods

	// RVA: 0x14793CC Offset: 0x14753CC VA: 0x14793CC
	protected Player_Ingame get_playerIngameScript() { }

	// RVA: 0x1479460 Offset: 0x1475460 VA: 0x1479460
	public static int get_maxLv() { }

	// RVA: -1 Offset: -1 Slot: 4
	protected abstract float get_GetWingCannonDamage();

	// RVA: -1 Offset: -1 Slot: 5
	protected abstract float get_GetWingCannonMaxPowerDamage();

	// RVA: -1 Offset: -1 Slot: 6
	protected abstract float get_GetMainCannonDamage();

	// RVA: 0x14794B0 Offset: 0x14754B0 VA: 0x14794B0
	protected float get_xDmgByRank() { }

	// RVA: 0x14794D8 Offset: 0x14754D8 VA: 0x14794D8 Slot: 7
	protected virtual void OnDisable() { }

	// RVA: 0x1479570 Offset: 0x1475570 VA: 0x1479570
	public bool IsInvisible() { }

	// RVA: 0x14795A8 Offset: 0x14755A8 VA: 0x14795A8
	public bool SetInvisible() { }

	// RVA: 0x14796FC Offset: 0x14756FC VA: 0x14796FC
	private IEnumerator IEInvisible() { }

	// RVA: 0x14794DC Offset: 0x14754DC VA: 0x14794DC
	private void ResetInvisible() { }

	// RVA: 0x1479784 Offset: 0x1475784 VA: 0x1479784 Slot: 8
	public virtual void SetPlayerRank(int _rank) { }

	// RVA: -1 Offset: -1 Slot: 9
	public abstract void StartAttack(bool _isStart = False);

	// RVA: -1 Offset: -1 Slot: 10
	public abstract void StopAttack();

	// RVA: -1 Offset: -1 Slot: 11
	public abstract void SkillOn(bool _touchAbility = False);

	// RVA: -1 Offset: -1 Slot: 12
	public abstract void SkillOff(bool _touchAbility = False);

	// RVA: -1 Offset: -1 Slot: 13
	public abstract void ResumeAttack();

	// RVA: -1 Offset: -1 Slot: 14
	public abstract void LevelUp();

	// RVA: 0x147978C Offset: 0x147578C VA: 0x147978C Slot: 15
	public virtual void KillEnemy() { }

	// RVA: 0x147980C Offset: 0x147580C VA: 0x147980C Slot: 16
	public virtual void SuperPowerUp() { }

	// RVA: 0x14798E8 Offset: 0x14758E8 VA: 0x14798E8
	public void UnlockSpecialCannon() { }

	// RVA: 0x14798F4 Offset: 0x14758F4 VA: 0x14798F4 Slot: 17
	protected virtual void Awake() { }

	// RVA: 0x1479B28 Offset: 0x1475B28 VA: 0x1479B28
	protected void CheckResetSuperPowerUp() { }

	// RVA: 0x1479BA4 Offset: 0x1475BA4 VA: 0x1479BA4 Slot: 18
	public virtual void OnResetSuperPowerUp() { }

	// RVA: 0x1479BA8 Offset: 0x1475BA8 VA: 0x1479BA8
	protected float get_dmgTechItem0() { }

	// RVA: 0x1479E34 Offset: 0x1475E34 VA: 0x1479E34
	protected void GetDeviceAddPowerPercent() { }

	// RVA: 0x147A034 Offset: 0x1476034 VA: 0x147A034
	protected void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x147A058 Offset: 0x1476058 VA: 0x147A058
	private bool <IEInvisible>b__27_0() { }
}

```

#### `Player_Attack_1`

```csharp
// Namespace: SpaceShooter.Player
public class Player_Attack_1 : Player_Attack // TypeDefIndex: 1746
{
	// Fields
	private int[] allNumberBullets; // 0x78
	private int numberSuper; // 0x80
	private Barrel[] mainCannonBarrels; // 0x88
	private int idBltNormal; // 0x90
	private int idBltPowerUp; // 0x94
	private float startShotRate; // 0x98
	private float startBltSpeed; // 0x9C
	private float superPowerUpShotRate; // 0xA0
	private float superPowerUpBltSpeed; // 0xA4
	private float timeRateMainCannon; // 0xA8
	private float speedMainCannonBlt; // 0xAC
	private int idMainCannonBlt; // 0xB0
	[SerializeField]
	private LayerMask targetLayer; // 0xB4
	private int numberNormal; // 0xB8
	private float timeToShot; // 0xBC
	private float timeToBarrelShot; // 0xC0
	private float shotRate; // 0xC4
	private float btlSpeed; // 0xC8
	private bool throughShield; // 0xCC
	private float timeDemo; // 0xD0
	private float angleDelta; // 0xD4
	private GameObject bulletObject; // 0xD8
	private Vector3 position; // 0xE0
	private int bCount; // 0xEC
	private float timeToPlaySound; // 0xF0
	[SerializeField]
	private Transform[] mainCannonPoints; // 0xF8
	private List<int> listIgroneEnemies; // 0x100
	private float minDistance; // 0x108
	private float timeToShotMainCannon; // 0x10C
	private GameObject bltMainCannon; // 0x110
	private float timeToShotMainCannonDelay; // 0x118
	private int numberAddMainCannonCount; // 0x11C
	private int turnMainCannonCount; // 0x120
	private float rateAddMainCannon; // 0x124

	// Properties
	protected override float GetWingCannonDamage { get; }
	protected override float GetWingCannonMaxPowerDamage { get; }
	protected override float GetMainCannonDamage { get; }

	// Methods

	// RVA: 0x147A290 Offset: 0x1476290 VA: 0x147A290
	private void SetupDatas() { }

	// RVA: 0x147A394 Offset: 0x1476394 VA: 0x147A394 Slot: 8
	public override void SetPlayerRank(int _rank) { }

	// RVA: 0x147A3C0 Offset: 0x14763C0 VA: 0x147A3C0 Slot: 4
	protected override float get_GetWingCannonDamage() { }

	// RVA: 0x147A4E4 Offset: 0x14764E4 VA: 0x147A4E4 Slot: 5
	protected override float get_GetWingCannonMaxPowerDamage() { }

	// RVA: 0x147A508 Offset: 0x1476508 VA: 0x147A508 Slot: 6
	protected override float get_GetMainCannonDamage() { }

	// RVA: 0x147A55C Offset: 0x147655C VA: 0x147A55C Slot: 17
	protected override void Awake() { }

	// RVA: 0x147A5DC Offset: 0x14765DC VA: 0x147A5DC
	private void OnEnable() { }

	// RVA: 0x147A6D4 Offset: 0x14766D4 VA: 0x147A6D4
	private void Update() { }

	// RVA: 0x147B264 Offset: 0x1477264 VA: 0x147B264 Slot: 9
	public override void StartAttack(bool _isStart = False) { }

	// RVA: 0x147B31C Offset: 0x147731C VA: 0x147B31C Slot: 11
	public override void SkillOn(bool _touchAbility = False) { }

	// RVA: 0x147B354 Offset: 0x1477354 VA: 0x147B354 Slot: 12
	public override void SkillOff(bool _touchAbility = False) { }

	// RVA: 0x147B38C Offset: 0x147738C VA: 0x147B38C Slot: 10
	public override void StopAttack() { }

	// RVA: 0x147B3B4 Offset: 0x14773B4 VA: 0x147B3B4 Slot: 13
	public override void ResumeAttack() { }

	// RVA: 0x147B52C Offset: 0x147752C VA: 0x147B52C Slot: 14
	public override void LevelUp() { }

	// RVA: 0x147B5F8 Offset: 0x14775F8 VA: 0x147B5F8 Slot: 16
	public override void SuperPowerUp() { }

	// RVA: 0x147B604 Offset: 0x1477604 VA: 0x147B604 Slot: 18
	public override void OnResetSuperPowerUp() { }

	// RVA: 0x147B3B8 Offset: 0x14773B8 VA: 0x147B3B8
	private void SetBarrels() { }

	// RVA: 0x147AD24 Offset: 0x1476D24 VA: 0x147AD24
	private void Shoot(int number, int idBlt) { }

	// RVA: 0x147B608 Offset: 0x1477608 VA: 0x147B608
	private void MainCannonAttack() { }

	// RVA: 0x147B8E0 Offset: 0x14778E0 VA: 0x147B8E0
	protected Transform FindAndAttackEnemy() { }

	// RVA: 0x147A894 Offset: 0x1476894 VA: 0x147A894
	private void MainCannonShoot() { }

	// RVA: 0x147BD1C Offset: 0x1477D1C VA: 0x147BD1C
	private void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x147BD20 Offset: 0x1477D20 VA: 0x147BD20
	private void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x147C1A8 Offset: 0x14781A8 VA: 0x147C1A8
	private void OnBulletMainCannonDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x147C1AC Offset: 0x14781AC VA: 0x147C1AC
	private void OnBulletMainCannonCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x147C3CC Offset: 0x14783CC VA: 0x147C3CC
	private void OnBulletMainCannonDestroyed2(GameObject obj, Vector3 pos) { }

	// RVA: 0x147C3D0 Offset: 0x14783D0 VA: 0x147C3D0
	private void OnBulletMainCannonCollided2(GameObject obj, Vector3 pos) { }

	// RVA: 0x147C5F8 Offset: 0x14785F8 VA: 0x147C5F8
	public void .ctor() { }
}

```

#### `Player_Attack_10`

```csharp
// Namespace: SpaceShooter.Player
public class Player_Attack_10 : Player_Attack // TypeDefIndex: 1749
{
	// Fields
	[SerializeField]
	private SkeletonAnimation playerAnimation; // 0x78
	private Collider2D[] resuftCols; // 0x80
	private bool init; // 0x88
	private float timeRateMainCannon; // 0x8C
	private float timeDemo; // 0x90
	[SerializeField]
	private LayerMask layerOnlyEnemy; // 0x94
	private float timeToShotMainCannon; // 0x98
	private float timeToShotMainCannonDelay; // 0x9C
	private int numberAddMainCannonCount; // 0xA0
	private int turnMainCannonCount; // 0xA4
	private float rateAddMainCannon; // 0xA8
	private float timeToAttackNormal; // 0xAC
	private float attackNormalRate; // 0xB0
	private int idDestroyEfx; // 0xB4
	[SerializeField]
	private Animator[] allShotEffects; // 0xB8
	[SerializeField]
	private Transform rangeObject; // 0xC0
	private Coroutine updateRange; // 0xC8
	private float range; // 0xD0
	private int zoneNumber; // 0xD4

	// Properties
	protected override float GetWingCannonDamage { get; }
	protected override float GetWingCannonMaxPowerDamage { get; }
	protected override float GetMainCannonDamage { get; }
	private float rangeNormal { get; }
	private float rangeSupper { get; }

	// Methods

	// RVA: 0x147CDB8 Offset: 0x1478DB8 VA: 0x147CDB8 Slot: 4
	protected override float get_GetWingCannonDamage() { }

	// RVA: 0x147CF34 Offset: 0x1478F34 VA: 0x147CF34 Slot: 5
	protected override float get_GetWingCannonMaxPowerDamage() { }

	// RVA: 0x147CF50 Offset: 0x1478F50 VA: 0x147CF50 Slot: 6
	protected override float get_GetMainCannonDamage() { }

	// RVA: 0x147CFA4 Offset: 0x1478FA4 VA: 0x147CFA4
	private void SetupDatas() { }

	// RVA: 0x147D01C Offset: 0x147901C VA: 0x147D01C Slot: 8
	public override void SetPlayerRank(int _rank) { }

	// RVA: 0x147D048 Offset: 0x1479048 VA: 0x147D048 Slot: 17
	protected override void Awake() { }

	// RVA: 0x147D070 Offset: 0x1479070 VA: 0x147D070
	private void OnEnable() { }

	// RVA: 0x147D120 Offset: 0x1479120 VA: 0x147D120 Slot: 7
	protected override void OnDisable() { }

	// RVA: 0x147D124 Offset: 0x1479124 VA: 0x147D124
	private void Update() { }

	// RVA: 0x147D6A8 Offset: 0x14796A8 VA: 0x147D6A8 Slot: 9
	public override void StartAttack(bool _isStart = False) { }

	// RVA: 0x147D8E4 Offset: 0x14798E4 VA: 0x147D8E4 Slot: 11
	public override void SkillOn(bool _touchAbility = False) { }

	// RVA: 0x147D920 Offset: 0x1479920 VA: 0x147D920 Slot: 12
	public override void SkillOff(bool _touchAbility = False) { }

	// RVA: 0x147D95C Offset: 0x147995C VA: 0x147D95C Slot: 10
	public override void StopAttack() { }

	// RVA: 0x147D9EC Offset: 0x14799EC VA: 0x147D9EC Slot: 13
	public override void ResumeAttack() { }

	// RVA: 0x147DA88 Offset: 0x1479A88 VA: 0x147DA88 Slot: 14
	public override void LevelUp() { }

	// RVA: 0x147DB54 Offset: 0x1479B54 VA: 0x147DB54 Slot: 16
	public override void SuperPowerUp() { }

	// RVA: 0x147DB6C Offset: 0x1479B6C VA: 0x147DB6C Slot: 18
	public override void OnResetSuperPowerUp() { }

	// RVA: 0x147DB70 Offset: 0x1479B70 VA: 0x147DB70
	private bool TargetCanAttack(GameObject _target) { }

	// RVA: 0x147DC8C Offset: 0x1479C8C VA: 0x147DC8C
	private GameObject GetEnemy(Vector3 _pointCenter, float _radius, ref List<GameObject> _listContains) { }

	// RVA: 0x147D5FC Offset: 0x14795FC VA: 0x147D5FC
	private void MainCannonShoot() { }

	// RVA: 0x147E148 Offset: 0x147A148 VA: 0x147E148
	private void MainCannonAttack() { }

	// RVA: 0x147E168 Offset: 0x147A168 VA: 0x147E168
	private IEnumerator AttackMainCannon() { }

	// RVA: 0x147E1F0 Offset: 0x147A1F0 VA: 0x147E1F0
	private void OnBulletMainCannonDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x147E1F4 Offset: 0x147A1F4 VA: 0x147E1F4
	private void OnBulletMainCannonCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x147D2B8 Offset: 0x14792B8 VA: 0x147D2B8
	private void AttackNormal() { }

	// RVA: 0x147E8B4 Offset: 0x147A8B4 VA: 0x147E8B4
	private void AttackEnemy(Transform _enemy) { }

	// RVA: 0x147EE6C Offset: 0x147AE6C VA: 0x147EE6C
	private void ExpAttack(Transform obj, Vector3 pos) { }

	// RVA: 0x147EA00 Offset: 0x147AA00 VA: 0x147EA00
	private void HitEnemy(Transform obj, float mulDmg) { }

	// RVA: 0x147F01C Offset: 0x147B01C VA: 0x147F01C
	private void DestroyedEffect(Vector3 fxPosition) { }

	// RVA: 0x147E8F4 Offset: 0x147A8F4 VA: 0x147E8F4
	private void PlayShootEffect(int _gunIdx) { }

	// RVA: 0x147D724 Offset: 0x1479724 VA: 0x147D724
	private void UpdateRange() { }

	// RVA: 0x147F118 Offset: 0x147B118 VA: 0x147F118
	private IEnumerator IEUpdateRange(Vector3 scale) { }

	// RVA: 0x147F1C4 Offset: 0x147B1C4 VA: 0x147F1C4
	private void OnDrawGizmos() { }

	// RVA: 0x147F0C4 Offset: 0x147B0C4 VA: 0x147F0C4
	private float get_rangeNormal() { }

	// RVA: 0x147F0AC Offset: 0x147B0AC VA: 0x147F0AC
	private float get_rangeSupper() { }

	// RVA: 0x147E324 Offset: 0x147A324 VA: 0x147E324
	private List<List<Transform>> GetListCalculateAngleObjects() { }

	// RVA: 0x147F1F4 Offset: 0x147B1F4 VA: 0x147F1F4
	private int GetZoneAttackIndex(Vector3 _pointCenter, Vector3 _pointTarget, int _deviceCount = 12) { }

	// RVA: 0x147F388 Offset: 0x147B388 VA: 0x147F388
	public void .ctor() { }
}

```

#### `Player_Ability`

```csharp
// Namespace: SpaceShooter.Player
public class Player_Ability : MonoBehaviour // TypeDefIndex: 1742
{
	// Fields
	[SerializeField]
	private Transform parentPlayerSkills; // 0x20
	[SerializeField]
	private Transform parentDronesSkills; // 0x28
	[SerializeField]
	private GameObject shieldObject; // 0x30
	[SerializeField]
	private GameObject shieldDroidObject101; // 0x38
	[SerializeField]
	private GameObject shieldDroidObject103; // 0x40
	[SerializeField]
	private GameObject shieldOneHit; // 0x48
	private GameObject playerAbilityObject; // 0x50
	private Player_Ingame playerIngameScript; // 0x58
	public Action<bool> shieldActived; // 0x60
	public Action<bool> shieldDroidActived101; // 0x68
	public Action<bool> shieldDroidActived103; // 0x70
	public Action<bool> shieldOneHitActived; // 0x78
	[SerializeField]
	private bool demo; // 0x80
	private Coroutine runDemo; // 0x88
	private Coroutine coroutine; // 0x90
	[SerializeField]
	private LayerMask targetLayer; // 0x98
	private GameObject shieldDrone2; // 0xA0
	[SerializeField]
	private LayerMask layerEnemyAndBullet; // 0xA8
	[SerializeField]
	private LayerMask layerBullet; // 0xAC
	[SerializeField]
	private int[] revokeEfxIds; // 0xB0
	private GameObject droneChilds; // 0xB8
	private GameObject drone7SkillObject; // 0xC0
	private GameObject drone11SkillObject; // 0xC8

	// Methods

	// RVA: 0x14712B0 Offset: 0x146D2B0 VA: 0x14712B0
	private void Awake() { }

	// RVA: 0x147163C Offset: 0x146D63C VA: 0x147163C
	private void OnDisable() { }

	// RVA: 0x1471800 Offset: 0x146D800 VA: 0x1471800
	public void CheckItemShield() { }

	// RVA: 0x1471884 Offset: 0x146D884 VA: 0x1471884
	public void DestroyShieldOneHit() { }

	// RVA: 0x14719B0 Offset: 0x146D9B0 VA: 0x14719B0
	public void AttackSkill() { }

	// RVA: 0x1471C10 Offset: 0x146DC10 VA: 0x1471C10
	public void AttackDroneSkill(int indexSlot) { }

	// RVA: 0x14725CC Offset: 0x146E5CC VA: 0x14725CC
	public void DemoDroneSkill(int _droneIndex, int _rank) { }

	// RVA: 0x1472628 Offset: 0x146E628 VA: 0x1472628
	private IEnumerator RunDemo(int _droneIndex, int _rank) { }

	// RVA: 0x14726A4 Offset: 0x146E6A4 VA: 0x14726A4
	public void ActiveShieldDroid101(float duration) { }

	// RVA: 0x1472780 Offset: 0x146E780 VA: 0x1472780
	private void OffShieldDroid101() { }

	// RVA: 0x1472988 Offset: 0x146E988 VA: 0x1472988
	public void ActiveShieldDroid103(float duration) { }

	// RVA: 0x1472A64 Offset: 0x146EA64 VA: 0x1472A64
	private void OffShieldDroid103() { }

	// RVA: 0x1472AE0 Offset: 0x146EAE0 VA: 0x1472AE0
	private void OnPlasmaBeamImpact(Transform target) { }

	// RVA: 0x1471BA8 Offset: 0x146DBA8 VA: 0x1471BA8
	private IEnumerator SkillAttack() { }

	// RVA: 0x1472054 Offset: 0x146E054 VA: 0x1472054
	private IEnumerator DroneSkill1(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1472C9C Offset: 0x146EC9C VA: 0x1472C9C
	private void OnBulletDroneSkill1Destroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1472CA0 Offset: 0x146ECA0 VA: 0x1472CA0
	private void OnBulletDroneSkill1Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x14720C8 Offset: 0x146E0C8 VA: 0x14720C8
	private IEnumerator DroneSkill2(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1472E70 Offset: 0x146EE70 VA: 0x1472E70
	private void OnBulletDroneSkill2Lv2Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1473018 Offset: 0x146F018 VA: 0x1473018
	private void OnBulletDroneSkill2Lv3Destroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x147301C Offset: 0x146F01C VA: 0x147301C
	private void OnBulletDroneSkill2Lv3Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1473330 Offset: 0x146F330 VA: 0x1473330
	private void RevokeEffect(Vector3 _pos) { }

	// RVA: 0x1472140 Offset: 0x146E140 VA: 0x1472140
	private IEnumerator DroneSkill3(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x14733F0 Offset: 0x146F3F0 VA: 0x14733F0
	private void OnBulletDroneSkill3Destroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x14733F4 Offset: 0x146F3F4 VA: 0x14733F4
	private void OnBulletDroneSkill3Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x14721B4 Offset: 0x146E1B4 VA: 0x14721B4
	private IEnumerator DroneSkill4(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x14735C4 Offset: 0x146F5C4 VA: 0x14735C4
	private void OnImpact(Transform target) { }

	// RVA: 0x1472228 Offset: 0x146E228 VA: 0x1472228
	private IEnumerator DroneSkill5(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1473784 Offset: 0x146F784 VA: 0x1473784
	private void OnBulletDroneSkill5Destroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1473788 Offset: 0x146F788 VA: 0x1473788
	private void OnBulletDroneSkill5Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x147229C Offset: 0x146E29C VA: 0x147229C
	private IEnumerator DroneSkill6(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1473958 Offset: 0x146F958 VA: 0x1473958
	private void OnBulletDroneSkill6Destroyed(GameObject obj, Vector3 pos, int idFragment) { }

	// RVA: 0x1473DBC Offset: 0x146FDBC VA: 0x1473DBC
	private void OnBulletDroneSkill6Collided(GameObject obj, Vector3 pos) { }

	// RVA: 0x1472310 Offset: 0x146E310 VA: 0x1472310
	private IEnumerator DroneSkill7(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1472384 Offset: 0x146E384 VA: 0x1472384
	private IEnumerator DroneSkill8(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x14740E0 Offset: 0x14700E0 VA: 0x14740E0
	private void HitEnemy(GameObject obj) { }

	// RVA: 0x14723F8 Offset: 0x146E3F8 VA: 0x14723F8
	private IEnumerator DroneSkill9(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1472470 Offset: 0x146E470 VA: 0x1472470
	private IEnumerator DroneSkill10(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x1474404 Offset: 0x1470404 VA: 0x1474404
	private void OnBulletDroneSkill10ChildCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x14746D8 Offset: 0x14706D8 VA: 0x14746D8
	private void OnBulletDroneSkill10Destroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1472558 Offset: 0x146E558 VA: 0x1472558
	private IEnumerator DroneSkill11(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x14724E4 Offset: 0x146E4E4 VA: 0x14724E4
	private IEnumerator DroneSkill12(int droneIndex, int droneLv, int rank) { }

	// RVA: 0x147472C Offset: 0x147072C VA: 0x147472C
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x14747E0 Offset: 0x14707E0 VA: 0x14747E0
	private void <DroneSkill8>g__ExpAttack|57_0(Vector3 pos) { }

	[CompilerGenerated]
	// RVA: 0x1474914 Offset: 0x1470914 VA: 0x1474914
	internal static void <DroneSkill12>g__OnBulletDestroyed|65_0(GameObject obj, Vector3 pos) { }

	[CompilerGenerated]
	// RVA: 0x1474918 Offset: 0x1470918 VA: 0x1474918
	internal static void <DroneSkill12>g__OnBulletCollided|65_1(GameObject obj, Vector3 pos) { }
}

```

#### `Player_Saved_Datas`

```csharp
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

```

#### `Player_Get_Datas`

```csharp
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

```

#### `Player_Device_Saved_Datas`

```csharp
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

```

#### `Player_Sounds`

```csharp
// Namespace: 
public class Player_Sounds : MonoBehaviour // TypeDefIndex: 317
{
	// Methods

	// RVA: 0x14E6284 Offset: 0x14E2284 VA: 0x14E6284
	public void .ctor() { }
}

```

#### `Player_Animations`

```csharp
// Namespace: 
public class Player_Animations : MonoBehaviour // TypeDefIndex: 315
{
	// Fields
	private SkeletonAnimation playerOldAnimation; // 0x20
	private SkeletonAnimation playerNewAnimation; // 0x28
	private GameObject fxChangePlayer; // 0x30
	private Coroutine changePlayerCoroutine; // 0x38

	// Methods

	// RVA: 0x14E1720 Offset: 0x14DD720 VA: 0x14E1720
	public void DoChangePlayer(Transform playerOld, Transform playerNew) { }

	// RVA: 0x14E17CC Offset: 0x14DD7CC VA: 0x14E17CC
	private IEnumerator ChangePlayer() { }

	// RVA: 0x14E1854 Offset: 0x14DD854 VA: 0x14E1854
	public void .ctor() { }
}

```

#### `Ship_Physics`

```csharp
// Namespace: 
public class Ship_Physics : MonoBehaviour // TypeDefIndex: 320
{
	// Fields
	public Action<float> onHit; // 0x20
	private List<int> listStaticOneHitEnemies; // 0x28
	[SerializeField]
	private Collider2D[] allHitBoxes; // 0x30

	// Methods

	// RVA: 0x14E8224 Offset: 0x14E4224 VA: 0x14E8224
	private void OnTriggerEnter2D(Collider2D other) { }

	// RVA: 0x14E8504 Offset: 0x14E4504 VA: 0x14E8504
	public void ActiveCollider(bool active) { }

	// RVA: 0x14E856C Offset: 0x14E456C VA: 0x14E856C
	public void .ctor() { }
}

```

#### `Drone_Get_Datas`

```csharp
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

```

#### `Drone_Saved_Datas`

```csharp
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

```

#### `Device_Get_Data`

```csharp
// Namespace: 
public class Device_Get_Data : MonoBehaviour // TypeDefIndex: 580
{
	// Fields
	private static List<float[]> listStatValues; // 0x0
	private static float[] percentByLevels1; // 0x8
	private static float[] percentByLevels2; // 0x10

	// Properties
	public static bool IsNewDevice { get; set; }

	// Methods

	// RVA: 0x1256760 Offset: 0x1252760 VA: 0x1256760
	public static bool get_IsNewDevice() { }

	// RVA: 0x1252BF4 Offset: 0x124EBF4 VA: 0x1252BF4
	public static void set_IsNewDevice(bool value) { }

	// RVA: 0x124F6A4 Offset: 0x124B6A4 VA: 0x124F6A4
	public static bool IsDeviceNew(int _instanceId) { }

	// RVA: 0x124F7BC Offset: 0x124B7BC VA: 0x124F7BC
	public static void SetDeviceNew(int _instanceId, bool _new) { }

	// RVA: 0x12507C0 Offset: 0x124C7C0 VA: 0x12507C0
	public static string GetStringLv(int lv) { }

	// RVA: 0x124F318 Offset: 0x124B318 VA: 0x124F318
	public static string GetStringRank(int rank) { }

	// RVA: 0x12567D8 Offset: 0x12527D8 VA: 0x12567D8
	public static string GetStringStatus(int instanceId) { }

	// RVA: 0x12507CC Offset: 0x124C7CC VA: 0x12507CC
	public static int GetPlayerUse(int instanceId) { }

	// RVA: 0x12561E0 Offset: 0x12521E0 VA: 0x12561E0
	public static string GetStringName(int id) { }

	// RVA: 0x1256914 Offset: 0x1252914 VA: 0x1256914
	public static string GetStringShortName(int id) { }

	// RVA: 0x125001C Offset: 0x124C01C VA: 0x125001C
	public static float GetStatValue1(Device _data) { }

	// RVA: 0x1250134 Offset: 0x124C134 VA: 0x1250134
	public static float GetStatValue2(Device _data) { }

	// RVA: 0x12569D0 Offset: 0x12529D0 VA: 0x12569D0
	public void .ctor() { }

	// RVA: 0x12569D8 Offset: 0x12529D8 VA: 0x12569D8
	private static void .cctor() { }
}

```

#### `Device_Saved_Data`

```csharp
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

```

#### `DeviceStats`

```csharp
// Namespace: 
public class DeviceStats : MonoBehaviour // TypeDefIndex: 1267
{
	// Fields
	public TextMeshPro textStatHeader; // 0x20
	public TextMeshPro textStatDetail; // 0x28
	public SpriteRenderer statIcon; // 0x30

	// Methods

	// RVA: 0x13C1BF4 Offset: 0x13BDBF4 VA: 0x13C1BF4
	public void .ctor() { }
}

```

#### `Tech_Datas`

```csharp
// Namespace: 
public class Tech_Datas : MonoBehaviour // TypeDefIndex: 1190
{
	// Fields
	public static int MAX_LV_TECHLAB; // 0x0
	public static int[] CostUnlockStats; // 0x8
	private static float[] deltaPriceDroids; // 0x10
	private static int maxUpgradePlayer; // 0x18
	private static int maxUpgradeTech; // 0x1C
	private static int[] basePriceStatUpgrade; // 0x20
	private static float[] deltaPricePlayers; // 0x28
	private static float[] deltaPriceDrones; // 0x30
	private static int[] basePriceTechStatUpgrade; // 0x38
	private static float[] deltaPriceTechStats; // 0x40
	private static int DeltaStarCost; // 0x48
	private static int StartStarCost; // 0x4C
	private static int[] CostUpgradeTechLab; // 0x50

	// Methods

	// RVA: 0x1399AA4 Offset: 0x1395AA4 VA: 0x1399AA4
	public static int GetTechStatPoints(int index) { }

	// RVA: 0x139E690 Offset: 0x139A690 VA: 0x139E690
	public static void SetTechStatPoints(int index, int point) { }

	// RVA: 0x139D96C Offset: 0x139996C VA: 0x139D96C
	public static int GetTechStatLevel(int index) { }

	// RVA: 0x139E9FC Offset: 0x139A9FC VA: 0x139E9FC
	public static void SetTechStatLevel(int index, int lv) { }

	// RVA: 0x1397E00 Offset: 0x1393E00 VA: 0x1397E00
	public static bool IsStatUnlocked(int index) { }

	// RVA: 0x139E5EC Offset: 0x139A5EC VA: 0x139E5EC
	public static void UnlockStat(int index) { }

	// RVA: 0x13999AC Offset: 0x13959AC VA: 0x13999AC
	public static int GetTechLabLevel() { }

	// RVA: 0x139FBF0 Offset: 0x139BBF0 VA: 0x139FBF0
	public static void SetTechLabLevel(int lv) { }

	// RVA: 0x13A0C38 Offset: 0x139CC38 VA: 0x13A0C38
	public static int GetUnlockStatPrice(int index, int level) { }

	// RVA: 0x13A0C5C Offset: 0x139CC5C VA: 0x13A0C5C
	public static int GetDroidUpgradePrice(int _index, int _lv) { }

	// RVA: 0x13A0E4C Offset: 0x139CE4C VA: 0x13A0E4C
	public static int GetPlayerUpgradePrice(int _index, int _lv) { }

	// RVA: 0x13A1000 Offset: 0x139D000 VA: 0x13A1000
	public static int GetDroneUpgradePrice(int _index, int _lv) { }

	// RVA: 0x139A0C4 Offset: 0x13960C4 VA: 0x139A0C4
	public static int NumberTechStats() { }

	// RVA: 0x1399CD4 Offset: 0x1395CD4 VA: 0x1399CD4
	public static int GetTechStatUpgradePrice(int _index, int _lv) { }

	// RVA: 0x13A1264 Offset: 0x139D264 VA: 0x13A1264
	public static int GetMaxValueStatUpgrade() { }

	// RVA: 0x13A13B4 Offset: 0x139D3B4 VA: 0x13A13B4
	public static int GetUpgradeDronePriceGem(int _index, int level) { }

	// RVA: 0x13A1434 Offset: 0x139D434 VA: 0x13A1434
	public static int GetUpgradePlayerPriceGem(int _index, int level) { }

	// RVA: 0x13A14B8 Offset: 0x139D4B8 VA: 0x13A14B8
	public static int GetUpgradeDroidPriceGem(int _index, int level) { }

	// RVA: 0x13A15B0 Offset: 0x139D5B0 VA: 0x13A15B0
	public static string GetStringStatLevel(int index) { }

	// RVA: 0x13A1690 Offset: 0x139D690 VA: 0x13A1690
	public static string GetStringAbiInfo(int statIndex, int abiIndex, ref Tech_Ability_Data[] listStatAbilityDatas) { }

	// RVA: 0x13A19DC Offset: 0x139D9DC VA: 0x13A19DC
	public static string GetStringAbiName(int statIndex, int abiIndex, ref Tech_Ability_Data[] listStatAbilityDatas) { }

	// RVA: 0x139D788 Offset: 0x1399788 VA: 0x139D788
	public static int GetStarToUpgrade() { }

	// RVA: 0x139F240 Offset: 0x139B240 VA: 0x139F240
	public static int GetCostUpgrade() { }

	// RVA: 0x13A1B40 Offset: 0x139DB40 VA: 0x13A1B40
	public void .ctor() { }

	// RVA: 0x13A1B48 Offset: 0x139DB48 VA: 0x13A1B48
	private static void .cctor() { }
}

```

#### `Tech_Stat`

```csharp
// Namespace: 
public class Tech_Stat : MonoBehaviour // TypeDefIndex: 1194
{
	// Methods

	// RVA: 0x13A2430 Offset: 0x139E430 VA: 0x13A2430
	public void .ctor() { }
}

```

#### `Talent`

```csharp
// Namespace: 
public class Talent : MonoBehaviour // TypeDefIndex: 1172
{
	// Fields
	[SerializeField]
	private SpriteRenderer iconRenderer; // 0x20
	public SpriteRenderer circleRenderer; // 0x28
	public BoxCollider2D box; // 0x30
	[SerializeField]
	private TextMeshPro textTalentName; // 0x38
	public int indexTalent; // 0x40
	public float indexVip; // 0x44
	public Action<Talent> onClick; // 0x48

	// Methods

	// RVA: 0x1397F2C Offset: 0x1393F2C VA: 0x1397F2C
	public void SetTalent(Sprite _iconSpr, string _strName) { }

	// RVA: 0x1397F74 Offset: 0x1393F74 VA: 0x1397F74
	public void Select(bool _select, float _alpha = 0.6) { }

	// RVA: 0x1398FA0 Offset: 0x1394FA0 VA: 0x1398FA0
	public void OnPressedButtonTalent() { }

	// RVA: 0x1398FC0 Offset: 0x1394FC0 VA: 0x1398FC0
	private void OnDrawGizmos() { }

	// RVA: 0x1399080 Offset: 0x1395080 VA: 0x1399080
	public void .ctor() { }
}

```

## Enemy / boss classes

197 classes

| class | base |
|---|---|
| `Boss10_AnimationEvents` | MonoBehaviour |
| `Boss10_Director` | Enemy_Appear |
| `Boss11_AnimationEvents` | MonoBehaviour |
| `Boss11_Director` | Enemy_Appear |
| `Boss12_AnimationEvents` | MonoBehaviour |
| `Boss12_Director` | Enemy_Appear |
| `Boss13_AnimationEvents` | MonoBehaviour |
| `Boss13_Director` | Enemy_Appear |
| `Boss15_AnimationEvents` | MonoBehaviour |
| `Boss15_Director` | Enemy_Appear |
| `Boss15_Director.LaserPoint` |  |
| `Boss17_AnimationEvents` | MonoBehaviour |
| `Boss17_Director` | Enemy_Appear |
| `Boss18_AnimationEvents` | MonoBehaviour |
| `Boss18_Director` | Enemy_Appear |
| `Boss19_AttackPhases` | Boss_AttackPhases |
| `Boss19_AttackTypes` | Boss_AttackTypes |
| `Boss1_AnimationEvents` | MonoBehaviour |
| `Boss1_Director` | Enemy_Appear |
| `Boss1_PlasmaAttack` | MonoBehaviour |
| `Boss20_AttackPhases` | Boss_AttackPhases |
| `Boss20_AttackTypes` | Boss_AttackTypes |
| `Boss21_AttackPhases` | Boss_AttackPhases |
| `Boss21_AttackTypes` | Boss_AttackTypes |
| `Boss22_AttackPhases` | Boss_AttackPhases |
| `Boss22_AttackTypes` | Boss_AttackTypes |
| `Boss23_AttackPhases` | Boss_AttackPhases |
| `Boss23_AttackTypes` | Boss_AttackTypes |
| `Boss3_Director` | Enemy_Appear |
| `Boss3_Flamer` | MonoBehaviour |
| `Boss3_FootEvent` | MonoBehaviour |
| `Boss3_Plasma` | MonoBehaviour |
| `Boss3_PlasmaAnimEvent` | MonoBehaviour |
| `Boss4_AnimationEvents` | MonoBehaviour |
| `Boss4_BigLaser` | MonoBehaviour |
| `Boss4_Director` | Enemy_Appear |
| `Boss4_DirectorLite` | Enemy_Appear |
| `Boss4_DoubleTurret_Attack` | MonoBehaviour |
| `Boss4_ExplosionTimer` | MonoBehaviour |
| `Boss5_AnimationEvents` | MonoBehaviour |
| `Boss5_Director` | Enemy_Appear |
| `Boss5_RocketBurst` | Gun_Attack |
| `Boss6_AnimationEvents` | MonoBehaviour |
| `Boss6_Director` | Enemy_Appear |
| `Boss6_Mini_AnimationEvents` | MonoBehaviour |
| `Boss6_Mini_Director` | Enemy_Appear |
| `Boss6_RocketAttack` | Gun_Attack |
| `Boss6_Sword` | MonoBehaviour |
| `Boss7_AnimationEvents` | MonoBehaviour |
| `Boss7_Director` | Enemy_Appear |
| `Boss8_AnimationEvents` | MonoBehaviour |
| `Boss8_Director` | Enemy_Appear |
| `Boss8_Spawner` | MonoBehaviour |
| `Boss9_AnimationEvents` | MonoBehaviour |
| `Boss9_Director` | Enemy_Appear |
| `Boss9_MiniDirector1` | Enemy_Appear |
| `Boss9_MiniDirector2` | Enemy_Appear |
| `BossAnimationEvents` | MonoBehaviour |
| `BossLaser` | MonoBehaviour |
| `BossLaser_Attack` | MonoBehaviour |
| `BossSpineEventHandler` | MonoBehaviour |
| `Boss_1_Animation` | MonoBehaviour |
| `Boss_1_Attack` | MonoBehaviour |
| `Boss_Actions` | MonoBehaviour |
| `Boss_Animation2` | MonoBehaviour |
| `Boss_Appear` | Enemy_Appear |
| `Boss_Attack2` | MonoBehaviour |
| `Boss_AttackPhases` | MonoBehaviour |
| `Boss_AttackTypes` | MonoBehaviour |
| `Boss_BodyPhysics` | MonoBehaviour |
| `Boss_Director` | Enemy_Appear |
| `Boss_PlasmaBeam` | MonoBehaviour |
| `Boss_Rocket` | MonoBehaviour |
| `Bullet_AreaDestroy` | MonoBehaviour |
| `Bullet_Attack` | MonoBehaviour |
| `Bullet_Ball` | Bullet_Linearly |
| `Bullet_Circle` | Bullet_Linearly |
| `Bullet_Curve` | Bullet_Linearly |
| `Bullet_Drop` | Bullet_Linearly |
| `Bullet_DropDown` | Bullet_Linearly |
| `Bullet_EMP` | Bullet_Object |
| `Bullet_Flower` | Bullet_Object |
| `Bullet_Formation` | MonoBehaviour |
| `Bullet_Jump` | Bullet_Object |
| `Bullet_Jump1` | Bullet_Object |
| `Bullet_JumpCheckAuto` | Bullet_Object |
| `Bullet_Linearly` | Bullet_Object |
| `Bullet_MissileSine` | Bullet_Object |
| `Bullet_MoveToTarget` | Bullet_Object |
| `Bullet_Object` | Sub_Object, IBullet, ISpeed |
| `Bullet_Plasma` | Bullet_Linearly |
| `Bullet_Player3` | Bullet_Linearly |
| `Bullet_Player7` | Bullet_Object |
| `Bullet_Reflex` | Bullet_Linearly |
| `Bullet_Reflex1` | Bullet_Object |
| `Bullet_Rocket` | Bullet_Object |
| `Bullet_Sine` | Bullet_Object |
| `Bullet_SineWave` | Bullet_Object |
| `Bullet_SlowDown` | Bullet_Linearly |
| `Bullet_SpeedUp` | Bullet_Linearly |
| `Bullet_SpiderSilk` | Bullet_Object |
| `Bullet_Static` | Bullet_Object |
| `Bullet_Sword` | Bullet_Linearly, IBulletSword |
| `Bullet_Transform` | MonoBehaviour |
| `Bullet_Transforms` | MonoBehaviour |
| `Bullet_Wind` | Bullet_Object |
| `Data_Boss` | ScriptableObject |
| `Droid_Attack` | MonoBehaviour |
| `Droid_Attack` | MonoBehaviour |
| `Droid_Attack_1` | Droid_Attack |
| `Droid_Attack_2` | MonoBehaviour |
| `Droid_Attack_3` | Droid_Attack |
| `Droid_Controller` | MonoBehaviour |
| `Droid_Data_Balance` | MonoBehaviour |
| `Enemy_Appear` | MonoBehaviour |
| `Enemy_Attack` | MonoBehaviour |
| `Enemy_Attack_Event` | MonoBehaviour |
| `Enemy_BombDie` | MonoBehaviour |
| `Enemy_Burned` | MonoBehaviour |
| `Enemy_BurstBulletWhenDie` | MonoBehaviour |
| `Enemy_CameraVibrate` | MonoBehaviour |
| `Enemy_Data_Balance` | MonoBehaviour |
| `Enemy_Datas` | MonoBehaviour |
| `Enemy_Destroy` | MonoBehaviour |
| `Enemy_DestroyAttack` | MonoBehaviour |
| `Enemy_DestroyDelayed` | Enemy_Destroy |
| `Enemy_Display` | MonoBehaviour |
| `Enemy_DropGold` | MonoBehaviour |
| `Enemy_EfxDestroyed` | MonoBehaviour |
| `Enemy_Get_Datas` | MonoBehaviour |
| `Enemy_Health` | MonoBehaviour |
| `Enemy_Helicopter` | MonoBehaviour |
| `Enemy_HitSkeletonRenderer` | MonoBehaviour |
| `Enemy_Hp_Bar` | MonoBehaviour |
| `Enemy_Laser_Gun` | MonoBehaviour |
| `Enemy_LookAtPlayer` | MonoBehaviour |
| `Enemy_Movement` | MonoBehaviour |
| `Enemy_OffObjectWhenDestroy` | MonoBehaviour |
| `Enemy_Passive_Attack` | MonoBehaviour |
| `Enemy_Physics` | MonoBehaviour |
| `Enemy_Rocket_Attack` | MonoBehaviour |
| `Enemy_Rotate` | MonoBehaviour |
| `Enemy_SpawnChilds` | MonoBehaviour |
| `Enemy_Stun` | MonoBehaviour |
| `Enemy_Sync_Attack` | MonoBehaviour |
| `Enemy_Sync_Attack2` | MonoBehaviour |
| `Gun_Attack` | MonoBehaviour |
| `Gun_BurstWhenDestroy` | Gun_Attack |
| `Gun_Circle_Attack` | Gun_Attack |
| `Gun_RandomAngle_Attack` | Gun_Attack |
| `Gun_RndTime_Attack` | Gun_Attack |
| `Invader_Controller` | MonoBehaviour |
| `Laser` | MonoBehaviour |
| `Laser_Gun_Attack` | MonoBehaviour |
| `Laser_Physics` | MonoBehaviour |
| `MB10_Animations` | MonoBehaviour |
| `MB10_Director` | Enemy_Appear |
| `MB11_Animations` | MonoBehaviour |
| `MB11_Director` | Enemy_Appear |
| `MB12_Animations` | MonoBehaviour |
| `MB12_Director` | Enemy_Appear |
| `MB13_Animations` | MonoBehaviour |
| `MB13_Director` | Enemy_Appear |
| `MB14_Animations` | MonoBehaviour |
| `MB14_Director` | Enemy_Appear |
| `MB15_Animations` | MonoBehaviour |
| `MB15_Director` | Enemy_Appear |
| `MB16_Director` | Enemy_Appear |
| `MB19_Director` | Enemy_Appear |
| `MB2_Director` | Enemy_Appear |
| `MB3_Animations` | MonoBehaviour |
| `MB3_Director` | Enemy_Appear |
| `MB4_Animation` | MonoBehaviour |
| `MB4_Director` | Enemy_Appear |
| `MB5_Director` | Enemy_Appear |
| `MB6_ChildDirector` | Enemy_Appear |
| `MB6_Director` | Enemy_Appear |
| `MB6_GunBurst` | MonoBehaviour |
| `MB7_Animations` | MonoBehaviour |
| `MB7_Director` | Enemy_Appear |
| `MB8_Animations` | MonoBehaviour |
| `MB8_Director` | Enemy_Appear |
| `MB9_Animations` | MonoBehaviour |
| `MB9_Director` | Enemy_Appear |
| `Meteor_Movement` | MonoBehaviour |
| `Meteorite` | Sub_Object |
| `MeteoriteGenerator` | MonoBehaviour |
| `MiniBoss1_Animation` | MonoBehaviour |
| `MiniBoss1_Attack` | MonoBehaviour |
| `MiniBoss1_Director` | Enemy_Appear |
| `MiniBoss1_Events` | MonoBehaviour |
| `MiniBoss2_Animation` | MonoBehaviour |
| `MiniBoss2_Attack` | MonoBehaviour |
| `Mothership` | MonoBehaviour |
| `Wukong_Child1` | MonoBehaviour |
| `Wukong_Child2` | Wukong_Child1 |
| `Wukong_Shoot` | MonoBehaviour |

### Boss roster (methods/fields)

| class | base |
|---|---|
| `Boss10_AnimationEvents` | MonoBehaviour |
| `Boss10_Director` | Enemy_Appear |
| `Boss11_AnimationEvents` | MonoBehaviour |
| `Boss11_Director` | Enemy_Appear |
| `Boss12_AnimationEvents` | MonoBehaviour |
| `Boss12_Director` | Enemy_Appear |
| `Boss13_AnimationEvents` | MonoBehaviour |
| `Boss13_Director` | Enemy_Appear |
| `Boss15_AnimationEvents` | MonoBehaviour |
| `Boss15_Director` | Enemy_Appear |
| `Boss15_Director.LaserPoint` |  |
| `Boss17_AnimationEvents` | MonoBehaviour |
| `Boss17_Director` | Enemy_Appear |
| `Boss18_AnimationEvents` | MonoBehaviour |
| `Boss18_Director` | Enemy_Appear |
| `Boss19_AttackPhases` | Boss_AttackPhases |
| `Boss19_AttackTypes` | Boss_AttackTypes |
| `Boss1_AnimationEvents` | MonoBehaviour |
| `Boss1_Director` | Enemy_Appear |
| `Boss1_PlasmaAttack` | MonoBehaviour |
| `Boss20_AttackPhases` | Boss_AttackPhases |
| `Boss20_AttackTypes` | Boss_AttackTypes |
| `Boss21_AttackPhases` | Boss_AttackPhases |
| `Boss21_AttackTypes` | Boss_AttackTypes |
| `Boss22_AttackPhases` | Boss_AttackPhases |
| `Boss22_AttackTypes` | Boss_AttackTypes |
| `Boss23_AttackPhases` | Boss_AttackPhases |
| `Boss23_AttackTypes` | Boss_AttackTypes |
| `Boss3_Director` | Enemy_Appear |
| `Boss3_Flamer` | MonoBehaviour |
| `Boss3_FootEvent` | MonoBehaviour |
| `Boss3_Plasma` | MonoBehaviour |
| `Boss3_PlasmaAnimEvent` | MonoBehaviour |
| `Boss4_AnimationEvents` | MonoBehaviour |
| `Boss4_BigLaser` | MonoBehaviour |
| `Boss4_Director` | Enemy_Appear |
| `Boss4_DirectorLite` | Enemy_Appear |
| `Boss4_DoubleTurret_Attack` | MonoBehaviour |
| `Boss4_ExplosionTimer` | MonoBehaviour |
| `Boss5_AnimationEvents` | MonoBehaviour |
| `Boss5_Director` | Enemy_Appear |
| `Boss5_RocketBurst` | Gun_Attack |
| `Boss6_AnimationEvents` | MonoBehaviour |
| `Boss6_Director` | Enemy_Appear |
| `Boss6_Mini_AnimationEvents` | MonoBehaviour |
| `Boss6_Mini_Director` | Enemy_Appear |
| `Boss6_RocketAttack` | Gun_Attack |
| `Boss6_Sword` | MonoBehaviour |
| `Boss7_AnimationEvents` | MonoBehaviour |
| `Boss7_Director` | Enemy_Appear |
| `Boss8_AnimationEvents` | MonoBehaviour |
| `Boss8_Director` | Enemy_Appear |
| `Boss8_Spawner` | MonoBehaviour |
| `Boss9_AnimationEvents` | MonoBehaviour |
| `Boss9_Director` | Enemy_Appear |
| `Boss9_MiniDirector1` | Enemy_Appear |
| `Boss9_MiniDirector2` | Enemy_Appear |
| `BossAnimationEvents` | MonoBehaviour |
| `BossLaser` | MonoBehaviour |
| `BossLaser_Attack` | MonoBehaviour |
| `BossSpineEventHandler` | MonoBehaviour |
| `Boss_1_Animation` | MonoBehaviour |
| `Boss_1_Attack` | MonoBehaviour |
| `Boss_Actions` | MonoBehaviour |
| `Boss_Animation2` | MonoBehaviour |
| `Boss_Appear` | Enemy_Appear |
| `Boss_Attack2` | MonoBehaviour |
| `Boss_AttackPhases` | MonoBehaviour |
| `Boss_AttackTypes` | MonoBehaviour |
| `Boss_BodyPhysics` | MonoBehaviour |
| `Boss_Director` | Enemy_Appear |
| `Boss_PlasmaBeam` | MonoBehaviour |
| `Boss_Rocket` | MonoBehaviour |
| `MB10_Animations` | MonoBehaviour |
| `MB10_Director` | Enemy_Appear |
| `MB11_Animations` | MonoBehaviour |
| `MB11_Director` | Enemy_Appear |
| `MB12_Animations` | MonoBehaviour |
| `MB12_Director` | Enemy_Appear |
| `MB13_Animations` | MonoBehaviour |
| `MB13_Director` | Enemy_Appear |
| `MB14_Animations` | MonoBehaviour |
| `MB14_Director` | Enemy_Appear |
| `MB15_Animations` | MonoBehaviour |
| `MB15_Director` | Enemy_Appear |
| `MB16_Director` | Enemy_Appear |
| `MB19_Director` | Enemy_Appear |
| `MB2_Director` | Enemy_Appear |
| `MB3_Animations` | MonoBehaviour |
| `MB3_Director` | Enemy_Appear |
| `MB4_Animation` | MonoBehaviour |
| `MB4_Director` | Enemy_Appear |
| `MB5_Director` | Enemy_Appear |
| `MB6_ChildDirector` | Enemy_Appear |
| `MB6_Director` | Enemy_Appear |
| `MB6_GunBurst` | MonoBehaviour |
| `MB7_Animations` | MonoBehaviour |
| `MB7_Director` | Enemy_Appear |
| `MB8_Animations` | MonoBehaviour |
| `MB8_Director` | Enemy_Appear |
| `MB9_Animations` | MonoBehaviour |
| `MB9_Director` | Enemy_Appear |
| `MiniBoss1_Animation` | MonoBehaviour |
| `MiniBoss1_Attack` | MonoBehaviour |
| `MiniBoss1_Director` | Enemy_Appear |
| `MiniBoss1_Events` | MonoBehaviour |
| `MiniBoss2_Animation` | MonoBehaviour |
| `MiniBoss2_Attack` | MonoBehaviour |

### Enemy data & balance

#### `Enemy_Data_Balance`

```csharp
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

```

#### `Data_Boss`

```csharp
// Namespace: 
public class Data_Boss : ScriptableObject // TypeDefIndex: 769
{
	// Fields
	public Boss_Info[] allBosses; // 0x18

	// Methods

	// RVA: 0x12BFD48 Offset: 0x12BBD48 VA: 0x12BFD48
	public void .ctor() { }
}

```

#### `Data_Items`

```csharp
// Namespace: 
public class Data_Items : ScriptableObject // TypeDefIndex: 739
{
	// Fields
	public ItemSprites[] allDropItems; // 0x18

	// Methods

	// RVA: 0x12B1B2C Offset: 0x12ADB2C VA: 0x12B1B2C
	public void .ctor() { }
}

```

#### `Droid_Data_Balance`

```csharp
// Namespace: SpaceShooter
public class Droid_Data_Balance : MonoBehaviour // TypeDefIndex: 1623
{
	// Fields
	public static int MaxLevelUpgrade; // 0x0
	public static float[] BaseDamages; // 0x8
	private static float[] DroidTimeOut; // 0x10
	private static int[] UnlockCosts; // 0x18
	private static int[] UnlockStarCosts; // 0x20
	private static int[] StartRanks; // 0x28

	// Methods

	// RVA: 0x14518D8 Offset: 0x144D8D8 VA: 0x14518D8
	public static float GetDroidTimeOut(int _droidIndex) { }

	// RVA: 0x1450928 Offset: 0x144C928 VA: 0x1450928
	public static float GetBaseDamage(int _droidIndex) { }

	// RVA: 0x1451994 Offset: 0x144D994 VA: 0x1451994
	public static int GetUnlockCost(int _droidIndex) { }

	// RVA: 0x1451A14 Offset: 0x144DA14 VA: 0x1451A14
	public static int GetUnlockStarCost(int _droidIndex) { }

	// RVA: 0x1451A94 Offset: 0x144DA94 VA: 0x1451A94
	public static int GetUpgadeCostCoins(int _droidIndex, int _droidLv) { }

	// RVA: 0x1451AFC Offset: 0x144DAFC VA: 0x1451AFC
	public static int GetUpgradeCostGems(int _droidIndex, int _droidLv) { }

	// RVA: 0x1451B64 Offset: 0x144DB64 VA: 0x1451B64
	public static int GetDroidRank(int _droidIndex) { }

	// RVA: 0x1451BE4 Offset: 0x144DBE4 VA: 0x1451BE4
	public static int GetDroidLevel(int _droidIndex) { }

	// RVA: 0x1451BEC Offset: 0x144DBEC VA: 0x1451BEC
	public static void SetDroidLevel(int _droidIndex, int _lv) { }

	// RVA: 0x1451C94 Offset: 0x144DC94 VA: 0x1451C94
	public static bool IsBought(int _droidIndex) { }

	// RVA: 0x1451DC4 Offset: 0x144DDC4 VA: 0x1451DC4
	public static void SetBought(int _droidIndex) { }

	// RVA: 0x1451E78 Offset: 0x144DE78 VA: 0x1451E78
	public void .ctor() { }

	// RVA: 0x1451E80 Offset: 0x144DE80 VA: 0x1451E80
	private static void .cctor() { }
}

```

#### `Enemy_Hp_Bar`

```csharp
// Namespace: 
public class Enemy_Hp_Bar : MonoBehaviour // TypeDefIndex: 225
{
	// Fields
	[SerializeField]
	private SpriteRenderer hpProgressBarRenderer; // 0x20
	[SerializeField]
	private float width; // 0x28
	[SerializeField]
	private float height; // 0x2C

	// Methods

	// RVA: 0x1321B5C Offset: 0x131DB5C VA: 0x1321B5C
	private void Update() { }

	// RVA: 0x1321BC4 Offset: 0x131DBC4 VA: 0x1321BC4
	public void SetHpBar(float percent) { }

	// RVA: 0x1321BEC Offset: 0x131DBEC VA: 0x1321BEC
	public void .ctor() { }
}

```

#### `Enemy_Attack_Event`

```csharp
// Namespace: SpaceShooter
public class Enemy_Attack_Event : MonoBehaviour // TypeDefIndex: 1634
{
	// Fields
	[SerializeField]
	private Gun_Attack attackScript; // 0x20
	[SerializeField]
	private UnityEvent startShootEvent; // 0x28
	[SerializeField]
	private UnityEvent stopShootEvent; // 0x30

	// Methods

	// RVA: 0x1455A7C Offset: 0x1451A7C VA: 0x1455A7C
	private void Start() { }

	// RVA: 0x1455C1C Offset: 0x1451C1C VA: 0x1455C1C
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1455C24 Offset: 0x1451C24 VA: 0x1455C24
	private void <Start>b__3_0() { }

	[CompilerGenerated]
	// RVA: 0x1455C38 Offset: 0x1451C38 VA: 0x1455C38
	private void <Start>b__3_1() { }
}

```

#### `Gun_Attack`

```csharp
// Namespace: SpaceShooter
public class Gun_Attack : MonoBehaviour // TypeDefIndex: 1639
{
	// Fields
	[SerializeField]
	private Transform iCanAttackParent; // 0x20
	[SerializeField]
	private float timeStart; // 0x28
	[SerializeField]
	private Gun_Attack.GunType gunType; // 0x2C
	[SerializeField]
	private Transform parentBarrels; // 0x30
	[SerializeField]
	private GunData[] allGunDatas; // 0x38
	[SerializeField]
	protected BulletForceType forceType; // 0x40
	[SerializeField]
	protected LayerMask targetLayer; // 0x44
	[SerializeField]
	protected int bltId; // 0x48
	[SerializeField]
	protected float bltSpeed; // 0x4C
	[SerializeField]
	protected float bltLifetime; // 0x50
	[SerializeField]
	protected float bltDamage; // 0x54
	[SerializeField]
	protected bool bltPinToMap; // 0x58
	[SerializeField]
	private AllClipName shootAudioClipName; // 0x5C
	protected int countShots; // 0x60
	protected float timeShot; // 0x64
	protected float timeReload; // 0x68
	protected float timeRounds; // 0x6C
	protected int countMags; // 0x70
	protected bool infinityRounds; // 0x74
	protected ICanAttack iCanAttack; // 0x78
	protected float timeToStart; // 0x80
	protected float timeToShot; // 0x84
	protected float timeToReload; // 0x88
	protected float timeToRounds; // 0x8C
	protected int countOfMags; // 0x90
	protected int countOfBlts; // 0x94
	protected GameObject goBlt; // 0x98
	protected Damager bltDamager; // 0xA0
	protected Vector3 position; // 0xA8
	protected Vector3 eulerAngles; // 0xB4
	protected IBullet iBlt; // 0xC0
	public bool isStunned; // 0xC8
	public Action<bool> startEvent; // 0xD0
	public Action shotEvent; // 0xD8
	public Action magStartEvent; // 0xE0
	public Action magEndedEvent; // 0xE8
	public Action roundEndedEvent; // 0xF0
	public Action<Vector3> onBulletDestroyed; // 0xF8
	public Action<GameObject, Vector3> onBulletNormalDestroyed; // 0x100
	private bool isRoundStart; // 0x108
	private bool isReadyToShoot; // 0x109
	private bool isAuto; // 0x10A

	// Methods

	// RVA: 0x1456474 Offset: 0x1452474 VA: 0x1456474
	private void Awake() { }

	// RVA: 0x1456504 Offset: 0x1452504 VA: 0x1456504 Slot: 4
	protected virtual void OnEnable() { }

	// RVA: 0x1456828 Offset: 0x1452828 VA: 0x1456828
	private void FixedUpdate() { }

	// RVA: 0x145697C Offset: 0x145297C VA: 0x145697C
	public void StartSyncAttack(bool _infinityRound = False) { }

	// RVA: 0x14569F0 Offset: 0x14529F0 VA: 0x14569F0
	public void StopSyncAttack() { }

	// RVA: 0x14569F8 Offset: 0x14529F8 VA: 0x14569F8
	public void StopAutoAttack() { }

	// RVA: 0x1456A00 Offset: 0x1452A00 VA: 0x1456A00
	public void ResumeAutoAttack() { }

	// RVA: 0x14568F8 Offset: 0x14528F8 VA: 0x14568F8
	private void GunAttack() { }

	// RVA: 0x14569AC Offset: 0x14529AC VA: 0x14569AC
	private void SyncAttack() { }

	// RVA: 0x1456A0C Offset: 0x1452A0C VA: 0x1456A0C
	private void AutoAttack() { }

	// RVA: 0x1456C34 Offset: 0x1452C34 VA: 0x1456C34 Slot: 5
	protected virtual void Shoot(Transform _barrel) { }

	// RVA: 0x145634C Offset: 0x145234C VA: 0x145634C
	public void ReadyToShoot() { }

	// RVA: 0x1456F6C Offset: 0x1452F6C VA: 0x1456F6C
	public void ShootOnBarrel(Transform _barrel) { }

	// RVA: 0x1456FAC Offset: 0x1452FAC VA: 0x1456FAC
	private void ShootDefault() { }

	// RVA: 0x1456FDC Offset: 0x1452FDC VA: 0x1456FDC Slot: 6
	protected virtual void MagEnded() { }

	// RVA: 0x145707C Offset: 0x145307C VA: 0x145707C Slot: 7
	protected virtual void OnBulletNormalDestroyed(GameObject obj, Vector3 pos) { }

	// RVA: 0x1457110 Offset: 0x1453110 VA: 0x1457110 Slot: 8
	protected virtual void OnBulletNormalCollided(GameObject obj, Vector3 pos) { }

	// RVA: 0x14572C8 Offset: 0x14532C8 VA: 0x14572C8
	public void .ctor() { }
}

```

## Economy / shop / progression classes

43 classes

| class | base |
|---|---|
| `Arena_Shop` | MonoBehaviour |
| `Board_BigShop` | Board |
| `Board_Reborn_IAP` | Board |
| `Board_Shop` | Board |
| `Board_ShopCoins` | Board |
| `Board_ShopEnergy` | Board |
| `Board_ShopGems` | Board |
| `Data_Items` | ScriptableObject |
| `GiftCode` |  |
| `GiftCodeGUI` | MonoBehaviour |
| `GiftCodeStruct` |  |
| `Gift_Behaviour` | MonoBehaviour |
| `Gift_Pack` | MonoBehaviour |
| `IAP_Manager` | MonoBehaviour |
| `ItemAbility` | MonoBehaviour |
| `ItemBuffetPack` | MonoBehaviour |
| `Item_Slot` | MonoBehaviour |
| `Popup_BuyEnergy` | Popup |
| `Popup_BuyItem` | MonoBehaviour |
| `Popup_BuyMoreChanceAbility` | MonoBehaviour |
| `Popup_BuyMoreCoins` | MonoBehaviour |
| `Popup_BuyMoreGems` | MonoBehaviour |
| `Popup_BuySpeed` | Popup |
| `Popup_Exchange` | MonoBehaviour |
| `Popup_FirstGiftFree` | MonoBehaviour |
| `Popup_FirstPurchase` | Popup |
| `PurchaseData` |  |
| `PurchaseValidator` |  |
| `Quest_Bar` | MonoBehaviour |
| `RankManager` | MonoBehaviour |
| `RankPreload` | Singleton<RankPreload> |
| `Rank_Header` | MonoBehaviour |
| `Rank_Rewards` | MonoBehaviour |
| `RewardRank_Behaviour` | MonoBehaviour |
| `ShipBuffetPack` | MonoBehaviour |
| `ShipSalePack` | MonoBehaviour |
| `ShipSalePackItem` | MonoBehaviour |
| `ShipTrial` |  |
| `ShipTrialPack` | MonoBehaviour |
| `ShipTrialSalePack` | MonoBehaviour |
| `Shop_Cell` | MonoBehaviour |
| `Shop_Gifts` | MonoBehaviour |
| `Shop_Pack` |  |

### Currencies & saved profile

#### `GameDatas`

```csharp
// Namespace: 
public class GameDatas : MonoBehaviour // TypeDefIndex: 249
{
	// Fields
	public static bool isAdmin; // 0x0
	public static int antiCheat; // 0x4
	public static int maxCheat; // 0x8
	public static int maxCheatCoins; // 0xC
	public static int maxCheatGems; // 0x10
	private static int cheatCoins; // 0x14
	private static int cheatGems; // 0x18
	private static int cheatStars; // 0x1C
	public static int cheatDroneCards; // 0x20
	public static int cheatPlayerCards; // 0x24
	public static int cheatDroneExp; // 0x28
	public static int cheatStageUnlocked; // 0x2C
	public static int cheatZoneUnlocked; // 0x30
	public static int cheatTutIndex; // 0x34
	public static bool fixedStagePlay; // 0x38
	public static bool unlock; // 0x39
	private static int energy; // 0x3C
	private static int itemPowerup; // 0x40
	private static int coins; // 0x44
	private static int gems; // 0x48
	private static int starCount; // 0x4C
	private static int keyCount0; // 0x50
	private static int keyCount1; // 0x54
	private static int keyCount2; // 0x58
	private static int wingCoins; // 0x5C
	private static int timeRewards; // 0x60
	private static int coinEvent1; // 0x64
	private static int typeControl; // 0x68
	private static int uiLeftRight; // 0x6C
	private static int autoChangePlayer; // 0x70
	private static int autoChangePosition; // 0x74
	private static int graphicsLv; // 0x78
	private static int w; // 0x7C
	private static int h; // 0x80
	private static float[] percentGraphics; // 0x88
	private static int vipPoints; // 0x90
	private static int arenaPoints; // 0x94
	private static int campaignPoints; // 0x98
	private static int arenaMedal; // 0x9C
	private static int pvpMedal; // 0xA0

	// Properties
	public static int Compensation { get; set; }
	public static int Energy { get; set; }
	public static int OverDrive { get; set; }
	public static int Coins { get; set; }
	public static int Gems { get; set; }
	public static int StarCount { get; set; }
	public static int KeyCount0 { get; set; }
	public static int KeyCount1 { get; set; }
	public static int KeyCount2 { get; set; }
	public static int WingCoins { get; set; }
	public static int TimeRewards { get; set; }
	public static int CoinEvent1 { get; set; }
	public static int TypeControl { get; set; }
	public static int UILeftRight { get; set; }
	public static int AutoChangePlayer { get; set; }
	public static int AutoChangePosition { get; set; }
	public static int width { get; }
	public static int height { get; }
	public static int GraphicsLevel { get; set; }
	public static int PlayerVipLevel { get; }
	public static int VipPoints { get; set; }
	public static bool IsCollectPremiumDailyGift { get; set; }
	public static bool CanCollectPremiumGift { get; set; }
	public static bool IsPremiumTag { get; set; }
	public static int CountThroughAds { get; set; }
	public static int LastArenaPoints { get; set; }
	public static int ArenaPoints { get; set; }
	public static int CampaignPoints { get; set; }
	public static int ArenaMedal { get; set; }
	public static int PvPMedal { get; set; }

	// Methods

	// RVA: 0x132373C Offset: 0x131F73C VA: 0x132373C
	public static int get_Compensation() { }

	// RVA: 0x13237A8 Offset: 0x131F7A8 VA: 0x13237A8
	public static void set_Compensation(int value) { }

	// RVA: 0x1323818 Offset: 0x131F818 VA: 0x1323818
	public static bool IsHasCheatResources() { }

	// RVA: 0x132452C Offset: 0x132052C VA: 0x132452C
	public static bool IsHasGiftLanguages() { }

	// RVA: 0x1324650 Offset: 0x1320650 VA: 0x1324650
	public static bool IsCountryPremium() { }

	// RVA: 0x1325320 Offset: 0x1321320 VA: 0x1325320
	public static double GetInstallDays() { }

	// RVA: 0x13253E4 Offset: 0x13213E4 VA: 0x13253E4
	public static void RefreshDatas() { }

	// RVA: 0x1323E60 Offset: 0x131FE60 VA: 0x1323E60
	public static int get_Energy() { }

	// RVA: 0x1323F28 Offset: 0x131FF28 VA: 0x1323F28
	public static void set_Energy(int value) { }

	// RVA: 0x1325454 Offset: 0x1321454 VA: 0x1325454
	public static int get_OverDrive() { }

	// RVA: 0x132551C Offset: 0x132151C VA: 0x132551C
	public static void set_OverDrive(int value) { }

	// RVA: 0x1323C8C Offset: 0x131FC8C VA: 0x1323C8C
	public static int get_Coins() { }

	// RVA: 0x1323DE4 Offset: 0x131FDE4 VA: 0x1323DE4
	public static void set_Coins(int value) { }

	// RVA: 0x1323A28 Offset: 0x131FA28 VA: 0x1323A28
	public static int get_Gems() { }

	// RVA: 0x1323B7C Offset: 0x131FB7C VA: 0x1323B7C
	public static void set_Gems(int value) { }

	// RVA: 0x132559C Offset: 0x132159C VA: 0x132559C
	public static int get_StarCount() { }

	// RVA: 0x13256F0 Offset: 0x13216F0 VA: 0x13256F0
	public static void set_StarCount(int value) { }

	// RVA: 0x1325770 Offset: 0x1321770 VA: 0x1325770
	public static int GetStarCount() { }

	// RVA: 0x1324154 Offset: 0x1320154 VA: 0x1324154
	public static int get_KeyCount0() { }

	// RVA: 0x132421C Offset: 0x132021C VA: 0x132421C
	public static void set_KeyCount0(int value) { }

	// RVA: 0x132429C Offset: 0x132029C VA: 0x132429C
	public static int get_KeyCount1() { }

	// RVA: 0x1324364 Offset: 0x1320364 VA: 0x1324364
	public static void set_KeyCount1(int value) { }

	// RVA: 0x13243E4 Offset: 0x13203E4 VA: 0x13243E4
	public static int get_KeyCount2() { }

	// RVA: 0x13244AC Offset: 0x13204AC VA: 0x13244AC
	public static void set_KeyCount2(int value) { }

	// RVA: 0x1323FA8 Offset: 0x131FFA8 VA: 0x1323FA8
	public static int get_WingCoins() { }

	// RVA: 0x13240D4 Offset: 0x13200D4 VA: 0x13240D4
	public static void set_WingCoins(int value) { }

	// RVA: 0x13258C0 Offset: 0x13218C0 VA: 0x13258C0
	public static int get_TimeRewards() { }

	// RVA: 0x1325988 Offset: 0x1321988 VA: 0x1325988
	public static void set_TimeRewards(int value) { }

	// RVA: 0x1325A08 Offset: 0x1321A08 VA: 0x1325A08
	public static int get_CoinEvent1() { }

	// RVA: 0x1325AD0 Offset: 0x1321AD0 VA: 0x1325AD0
	public static void set_CoinEvent1(int value) { }

	// RVA: 0x1325B50 Offset: 0x1321B50 VA: 0x1325B50
	public static int get_TypeControl() { }

	// RVA: 0x1325C18 Offset: 0x1321C18 VA: 0x1325C18
	public static void set_TypeControl(int value) { }

	// RVA: 0x1325C94 Offset: 0x1321C94 VA: 0x1325C94
	public static int get_UILeftRight() { }

	// RVA: 0x1325D5C Offset: 0x1321D5C VA: 0x1325D5C
	public static void set_UILeftRight(int value) { }

	// RVA: 0x1325DD8 Offset: 0x1321DD8 VA: 0x1325DD8
	public static int get_AutoChangePlayer() { }

	// RVA: 0x1325EA0 Offset: 0x1321EA0 VA: 0x1325EA0
	public static void set_AutoChangePlayer(int value) { }

	// RVA: 0x1325F1C Offset: 0x1321F1C VA: 0x1325F1C
	public static int get_AutoChangePosition() { }

	// RVA: 0x1325FE4 Offset: 0x1321FE4 VA: 0x1325FE4
	public static void set_AutoChangePosition(int value) { }

	// RVA: 0x1326060 Offset: 0x1322060 VA: 0x1326060
	public static int get_width() { }

	// RVA: 0x132610C Offset: 0x132210C VA: 0x132610C
	public static int get_height() { }

	// RVA: 0x13261B8 Offset: 0x13221B8 VA: 0x13261B8
	public static int get_GraphicsLevel() { }

	// RVA: 0x1326280 Offset: 0x1322280 VA: 0x1326280
	public static void set_GraphicsLevel(int value) { }

	// RVA: 0x13263A4 Offset: 0x13223A4 VA: 0x13263A4
	public static int get_PlayerVipLevel() { }

	// RVA: 0x13264BC Offset: 0x13224BC VA: 0x13264BC
	public static int GetVipLevel(int _vipPoints) { }

	// RVA: 0x13263F4 Offset: 0x13223F4 VA: 0x13263F4
	public static int get_VipPoints() { }

	// RVA: 0x1326588 Offset: 0x1322588 VA: 0x1326588
	public static void set_VipPoints(int value) { }

	// RVA: 0x1326608 Offset: 0x1322608 VA: 0x1326608
	public static bool get_IsCollectPremiumDailyGift() { }

	// RVA: 0x1326680 Offset: 0x1322680 VA: 0x1326680
	public static void set_IsCollectPremiumDailyGift(bool value) { }

	// RVA: 0x13266FC Offset: 0x13226FC VA: 0x13266FC
	public static bool IsProVersion() { }

	// RVA: 0x13268D4 Offset: 0x13228D4 VA: 0x13268D4
	public static bool IsProVersionActived() { }

	// RVA: 0x13269B8 Offset: 0x13229B8 VA: 0x13269B8
	public static bool IsPremiumExpired() { }

	// RVA: 0x1326B88 Offset: 0x1322B88 VA: 0x1326B88
	public static TimeSpan GetProExpiryDateTime() { }

	// RVA: 0x1326D1C Offset: 0x1322D1C VA: 0x1326D1C
	public static void ClearPremium() { }

	// RVA: 0x1326D9C Offset: 0x1322D9C VA: 0x1326D9C
	public static void SetProExpiryDateTime(double _addSeconds) { }

	// RVA: 0x13271F4 Offset: 0x13231F4 VA: 0x13271F4
	public static void SetProExpiryDateTimeFromNow(double _addSeconds) { }

	// RVA: 0x13272FC Offset: 0x13232FC VA: 0x13272FC
	public static bool get_CanCollectPremiumGift() { }

	// RVA: 0x132737C Offset: 0x132337C VA: 0x132737C
	public static void set_CanCollectPremiumGift(bool value) { }

	// RVA: 0x1327100 Offset: 0x1323100 VA: 0x1327100
	public static bool get_IsPremiumTag() { }

	// RVA: 0x1327178 Offset: 0x1323178 VA: 0x1327178
	public static void set_IsPremiumTag(bool value) { }

	// RVA: 0x13273FC Offset: 0x13233FC VA: 0x13273FC
	public static int get_CountThroughAds() { }

	// RVA: 0x1327468 Offset: 0x1323468 VA: 0x1327468
	public static void set_CountThroughAds(int value) { }

	// RVA: 0x13274D8 Offset: 0x13234D8 VA: 0x13274D8
	public static int get_LastArenaPoints() { }

	// RVA: 0x1327544 Offset: 0x1323544 VA: 0x1327544
	public static void set_LastArenaPoints(int value) { }

	// RVA: 0x13275B4 Offset: 0x13235B4 VA: 0x13275B4
	public static int get_ArenaPoints() { }

	// RVA: 0x132767C Offset: 0x132367C VA: 0x132767C
	public static void set_ArenaPoints(int value) { }

	// RVA: 0x13276FC Offset: 0x13236FC VA: 0x13276FC
	public static int get_CampaignPoints() { }

	// RVA: 0x13277C4 Offset: 0x13237C4 VA: 0x13277C4
	public static void set_CampaignPoints(int value) { }

	// RVA: 0x1327844 Offset: 0x1323844 VA: 0x1327844
	public static int get_ArenaMedal() { }

	// RVA: 0x132790C Offset: 0x132390C VA: 0x132790C
	public static void set_ArenaMedal(int value) { }

	// RVA: 0x132798C Offset: 0x132398C VA: 0x132798C
	public static int get_PvPMedal() { }

	// RVA: 0x1327A54 Offset: 0x1323A54 VA: 0x1327A54
	public static void set_PvPMedal(int value) { }

	// RVA: 0x1327AD4 Offset: 0x1323AD4 VA: 0x1327AD4
	public void .ctor() { }

	// RVA: 0x1327ADC Offset: 0x1323ADC VA: 0x1327ADC
	private static void .cctor() { }
}

```

#### `IAP_Manager`

```csharp
// Namespace: 
public class IAP_Manager : MonoBehaviour // TypeDefIndex: 1392
{
	// Fields
	private static IAPSystem s_iapSystem; // 0x0
	private static int[] allCostProducts; // 0x8
	private static int multipleVipPoint; // 0x10
	public static int proForverVipPoint; // 0x14
	public static int timerewardForverVipPoint; // 0x18
	public static int[][] PlayerFakePriceForVipPoints; // 0x20
	public static int[][] DroneFakePriceForVipPoints; // 0x28

	// Properties
	public static string timerewardForeverProduct { get; }
	public static string proForeverProduct { get; }
	public static string giftLogInXProduct { get; }
	public static bool IsPaidUser { get; set; }

	// Methods

	[RuntimeInitializeOnLoadMethod]
	// RVA: 0x13F880C Offset: 0x13F480C VA: 0x13F880C
	private static void CreateInstance() { }

	// RVA: 0x13F8928 Offset: 0x13F4928 VA: 0x13F8928
	private void Awake() { }

	// RVA: 0x13F8A10 Offset: 0x13F4A10 VA: 0x13F8A10
	public static bool IsInitialized() { }

	// RVA: 0x13F8A74 Offset: 0x13F4A74 VA: 0x13F8A74
	public static bool InitiateProductIDPurchase(int _index) { }

	// RVA: 0x13F8AE4 Offset: 0x13F4AE4 VA: 0x13F8AE4
	public static bool InitiateProductIDPurchase(string _productId) { }

	// RVA: 0x13F8B50 Offset: 0x13F4B50 VA: 0x13F8B50
	public static void BuyProductConsumable(int _index, Action<string, string> _callback) { }

	// RVA: 0x13F8E0C Offset: 0x13F4E0C VA: 0x13F8E0C
	public static void BuyProductConsumable(string _productId, Action<string, string> _callback) { }

	// RVA: 0x13F8BE8 Offset: 0x13F4BE8 VA: 0x13F8BE8
	private static void RegisterPurchaseCallback(ref Action<string, string> _callback) { }

	// RVA: 0x13F8F08 Offset: 0x13F4F08 VA: 0x13F8F08
	public static string GetConsumablePriceString(int _index) { }

	// RVA: 0x13F8F78 Offset: 0x13F4F78 VA: 0x13F8F78
	public static string GetConsumablePriceString(string _productId) { }

	// RVA: 0x13F8FE4 Offset: 0x13F4FE4 VA: 0x13F8FE4
	public static string GetIsoCurrencyCode(int _index) { }

	// RVA: 0x13F9064 Offset: 0x13F5064 VA: 0x13F9064
	public static string GetIsoCurrencyCode(string _productId) { }

	// RVA: 0x13F90D0 Offset: 0x13F50D0 VA: 0x13F90D0
	public static int GetVipPoint(int _index) { }

	// RVA: 0x13F9188 Offset: 0x13F5188 VA: 0x13F9188
	public static int GetPlayerVipPoint(int _index, int _rank) { }

	// RVA: 0x13F9310 Offset: 0x13F5310 VA: 0x13F9310
	public static int GetDroneVipPoint(int _index, int _rank) { }

	// RVA: 0x13F9498 Offset: 0x13F5498 VA: 0x13F9498
	public static string get_timerewardForeverProduct() { }

	// RVA: 0x13F95B8 Offset: 0x13F55B8 VA: 0x13F95B8
	public static string get_proForeverProduct() { }

	// RVA: 0x13F961C Offset: 0x13F561C VA: 0x13F961C
	public static string get_giftLogInXProduct() { }

	// RVA: 0x13F9680 Offset: 0x13F5680 VA: 0x13F9680
	public static Decimal GetConsumablePriceDecimal(int _index) { }

	// RVA: 0x13F96F0 Offset: 0x13F56F0 VA: 0x13F96F0
	public static Decimal GetConsumablePriceDecimal(string _productId) { }

	// RVA: 0x13F975C Offset: 0x13F575C VA: 0x13F975C
	public static Decimal GetPlayerUnlockPriceDecimal(int _index, int _rank) { }

	// RVA: 0x13F991C Offset: 0x13F591C VA: 0x13F991C
	public static string GetDroneUnlockPrice(int _index, int _rank) { }

	// RVA: 0x13F9ADC Offset: 0x13F5ADC VA: 0x13F9ADC
	public static Decimal GetDroneUnlockPriceDecimal(int _index, int _rank) { }

	// RVA: 0x13F9C5C Offset: 0x13F5C5C VA: 0x13F9C5C
	public static void BuyProductDroneUnlock(int _index, int _rank, Action<string, string> _callback) { }

	// RVA: 0x13F9E3C Offset: 0x13F5E3C VA: 0x13F9E3C
	public static string GetPlayerUnlockPrice(int _index, int _rank) { }

	// RVA: 0x13F9FFC Offset: 0x13F5FFC VA: 0x13F9FFC
	public static string GetPlayerUnlockRankPrice(int _index, int _rank) { }

	// RVA: 0x13F94FC Offset: 0x13F54FC VA: 0x13F94FC
	private static string GetProductId(string id) { }

	// RVA: 0x13FA16C Offset: 0x13F616C VA: 0x13FA16C
	public static void BuyProductPlayerUnlock(int _index, int _rank, Action<string, string> _callback) { }

	// RVA: 0x13FA34C Offset: 0x13F634C VA: 0x13FA34C
	public static void RemoveAds(Action<string, string> _callback) { }

	// RVA: 0x13FA3E8 Offset: 0x13F63E8 VA: 0x13FA3E8
	public static void RestorePurchase() { }

	// RVA: 0x13FA44C Offset: 0x13F644C VA: 0x13FA44C
	public static bool NetworkNotReachable() { }

	// RVA: 0x13F8E90 Offset: 0x13F4E90 VA: 0x13F8E90
	public static bool get_IsPaidUser() { }

	// RVA: 0x13FA4A8 Offset: 0x13F64A8 VA: 0x13FA4A8
	public static void set_IsPaidUser(bool value) { }

	// RVA: 0x13FA5F4 Offset: 0x13F65F4 VA: 0x13FA5F4
	public void .ctor() { }

	// RVA: 0x13FA5FC Offset: 0x13F65FC VA: 0x13FA5FC
	private static void .cctor() { }
}

```

#### `Board_ShopGems`

```csharp
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

```

#### `Board_ShopCoins`

```csharp
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

```

#### `Board_ShopEnergy`

```csharp
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

```

#### `Board_BigShop`

```csharp
// Namespace: 
public class Board_BigShop : Board // TypeDefIndex: 1100
{
	// Fields
	private int[] resetCosts; // 0x20
	private int[] deviceRate0; // 0x28
	private int[] deviceRate1; // 0x30
	private int[] deviceRate2; // 0x38
	private int[] deviceRate3; // 0x40
	public static BoardID backBoard; // 0x0
	[SerializeField]
	private Sprite[] listSpriteResourcePacks; // 0x48
	[SerializeField]
	private Sprite[] listSpriteDevicePacks; // 0x50
	[SerializeField]
	private Transform parentResources; // 0x58
	[SerializeField]
	private Transform parentDevices; // 0x60
	[SerializeField]
	private Transform parentDrones; // 0x68
	[SerializeField]
	private Shop_Cell[] listCellResourcePacks; // 0x70
	[SerializeField]
	private Shop_Cell[] listCellDevicePacks; // 0x78
	[SerializeField]
	private Shop_Cell[] listCellDronePacks; // 0x80
	[SerializeField]
	private TextMeshPro textTimer; // 0x88
	[SerializeField]
	private TextMeshPro textCostReset; // 0x90
	[SerializeField]
	private Popup_Notices popupConfirmBuy; // 0x98
	private Dictionary<int, Sprite> allDeviceIcons; // 0xA0
	[SerializeField]
	private TextMeshPro textGroup1; // 0xA8
	[SerializeField]
	private TextMeshPro textGroup2; // 0xB0
	[SerializeField]
	private TextMeshPro textGroup3; // 0xB8
	[SerializeField]
	private GameObject objMenu; // 0xC0
	[SerializeField]
	private BoxCollider2D boxBound; // 0xC8
	[SerializeField]
	private BoxCollider2D boxContent; // 0xD0
	[SerializeField]
	private Transform parentView; // 0xD8
	private bool isVideoReady; // 0xE0
	[SerializeField]
	private SpriteRenderer[] headerRenderers; // 0xE8
	private Coroutine focusDevice; // 0xF0
	[SerializeField]
	private Popup_Notices popupNoCoins; // 0xF8
	[SerializeField]
	private Popup_Notices popupNoGems; // 0x100
	[SerializeField]
	private UnboxingBoxDevice unboxing; // 0x108
	[SerializeField]
	private ScrollView scrollView; // 0x110
	[SerializeField]
	private Animator btnResetAnim; // 0x118
	private GameObject m_popupPremium; // 0x120
	[SerializeField]
	private Popup_Notices popupVideoNotReady; // 0x128
	[SerializeField]
	private Popup_Notices popupNetworkNotConnected; // 0x130
	[SerializeField]
	private SpriteRenderer iconPopupDevice; // 0x138
	[SerializeField]
	private TextMeshPro textPopupCost; // 0x140
	private const string keySysTime = "ShopTimer";
	private double totalSecs; // 0x148
	private double maxTime; // 0x150

	// Properties
	private static int resetCount { get; set; }
	private GameObject popupPremium { get; }

	// Methods

	// RVA: 0x1373528 Offset: 0x136F528 VA: 0x1373528
	public static void ResetDaily() { }

	// RVA: 0x1373598 Offset: 0x136F598 VA: 0x1373598
	private static int get_resetCount() { }

	// RVA: 0x1373604 Offset: 0x136F604 VA: 0x1373604
	private static void set_resetCount(int value) { }

	// RVA: 0x1373674 Offset: 0x136F674 VA: 0x1373674
	private void OnDrawGizmos() { }

	// RVA: 0x13737B4 Offset: 0x136F7B4 VA: 0x13737B4
	private void Awake() { }

	// RVA: 0x1373B88 Offset: 0x136FB88 VA: 0x1373B88
	private void OnEnable() { }

	// RVA: 0x13746F8 Offset: 0x13706F8 VA: 0x13746F8
	private void OnDisable() { }

	// RVA: 0x1374744 Offset: 0x1370744 VA: 0x1374744 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x13747D8 Offset: 0x13707D8 VA: 0x13747D8 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x13749E8 Offset: 0x13709E8 VA: 0x13749E8 Slot: 9
	public override void Escape() { }

	// RVA: 0x13749EC Offset: 0x13709EC VA: 0x13749EC
	public void OnPressedButtonBack() { }

	// RVA: 0x1374BCC Offset: 0x1370BCC VA: 0x1374BCC
	public void OnPressedButtonResetShop() { }

	// RVA: 0x13746B8 Offset: 0x13706B8 VA: 0x13746B8
	private void FocusDeviceTab() { }

	// RVA: 0x1374F18 Offset: 0x1370F18 VA: 0x1374F18
	private IEnumerator FocusDevice() { }

	// RVA: 0x1374FA0 Offset: 0x1370FA0 VA: 0x1374FA0
	private void NoCoins() { }

	// RVA: 0x1374E74 Offset: 0x1370E74 VA: 0x1374E74
	private void NoGems() { }

	// RVA: 0x1375044 Offset: 0x1371044 VA: 0x1375044
	private void SetEffect(int _number, Sprite _sprite, Transform _parent) { }

	// RVA: 0x13750F8 Offset: 0x13710F8 VA: 0x13750F8
	private int GetRandomIndex(int[] _percents) { }

	// RVA: 0x13751A0 Offset: 0x13711A0 VA: 0x13751A0
	private void UnboxingBoxDevice(int _cellIndex, int _id, Sprite _sprite) { }

	// RVA: 0x13755AC Offset: 0x13715AC VA: 0x13755AC
	private bool Purchased(int _groupIndex, int _indexPack, DataPack _dataPack) { }

	// RVA: 0x13759AC Offset: 0x13719AC VA: 0x13759AC
	private void OnClickBuyResourcePack(Shop_Cell _cell) { }

	// RVA: 0x1375F74 Offset: 0x1371F74 VA: 0x1375F74
	private GameObject get_popupPremium() { }

	// RVA: 0x1376070 Offset: 0x1372070 VA: 0x1376070
	private void CheckAndPurchaseResources(Shop_Cell _cell, DataPack dataPack, int _stockCount, int _maxStock) { }

	// RVA: 0x1376720 Offset: 0x1372720 VA: 0x1376720
	private void OnClickBuyDevicePack(Shop_Cell _cell) { }

	// RVA: 0x1376CFC Offset: 0x1372CFC VA: 0x1376CFC
	private void CheckAndPurchaseDevices(Shop_Cell _cell, DataPack dataPack, int _stockCount, int _maxStock, int _price) { }

	// RVA: 0x1377058 Offset: 0x1373058 VA: 0x1377058
	private void OnClickBuyDronePack(Shop_Cell _cell) { }

	// RVA: 0x13774BC Offset: 0x13734BC VA: 0x13774BC
	private void CheckAndPurchaseDroneCards(Shop_Cell _cell, DataPack dataPack, int _stockCount, int _maxStock) { }

	// RVA: 0x1374168 Offset: 0x1370168 VA: 0x1374168
	private void ResetShop(bool _reset = True) { }

	// RVA: 0x1377924 Offset: 0x1373924 VA: 0x1377924
	private void ResetGroup(int _groupIndex, ref DataPack[] _listDataPacks, ref Sprite[] _listSprites, ref Shop_Cell[] _listCells, Action<Shop_Cell> _onClick, float _freePercent, bool _reset = True) { }

	// RVA: 0x1378E68 Offset: 0x1374E68 VA: 0x1378E68
	public static bool HasFreeDevice() { }

	// RVA: 0x1378B7C Offset: 0x1374B7C VA: 0x1378B7C
	private static int GetCellIndex(int _groupIndex, int _index) { }

	// RVA: 0x1378C34 Offset: 0x1374C34 VA: 0x1378C34
	private void SetCellIndex(int _groupIndex, int _index, int _packIndex) { }

	// RVA: 0x13754F4 Offset: 0x13714F4 VA: 0x13754F4
	private static int GetDeviceCountValue(int _groupIndex, int _index) { }

	// RVA: 0x1378DAC Offset: 0x1374DAC VA: 0x1378DAC
	private void SetDeviceCountValue(int _groupIndex, int _index, int _val) { }

	// RVA: 0x13758F4 Offset: 0x13718F4 VA: 0x13758F4
	private static int GetCellSaleOff(int _groupIndex, int _index) { }

	// RVA: 0x1378CF0 Offset: 0x1374CF0 VA: 0x1378CF0
	private void SetCellSaleOff(int _groupIndex, int _index, int _saleOff) { }

	// RVA: 0x1375EBC Offset: 0x1371EBC VA: 0x1375EBC
	private static int GetCellStockCount(int _groupIndex, int _index) { }

	// RVA: 0x1376664 Offset: 0x1372664 VA: 0x1376664
	private void SetCellStockCount(int _groupIndex, int _index, int _stockCount) { }

	// RVA: 0x1373F94 Offset: 0x136FF94 VA: 0x1373F94
	private bool reset() { }

	// RVA: 0x1378F34 Offset: 0x1374F34 VA: 0x1378F34
	private void CheckTimer() { }

	// RVA: 0x1378FE4 Offset: 0x1374FE4 VA: 0x1378FE4
	public void .ctor() { }

	// RVA: 0x1379184 Offset: 0x1375184 VA: 0x1379184
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x13791D0 Offset: 0x13751D0 VA: 0x13791D0
	private void <Awake>b__29_0(object <p0>) { }

	[CompilerGenerated]
	// RVA: 0x1379338 Offset: 0x1375338 VA: 0x1379338
	private void <NoCoins>b__44_0() { }

	[CompilerGenerated]
	// RVA: 0x1379358 Offset: 0x1375358 VA: 0x1379358
	private void <NoGems>b__46_0() { }

	[CompilerGenerated]
	// RVA: 0x1379378 Offset: 0x1375378 VA: 0x1379378
	private void <UnboxingBoxDevice>b__51_0() { }
}

```

#### `Board_BattlePass`

```csharp
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

```

#### `Board_BattlePassPro`

```csharp
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

```

#### `Board_Quest`

```csharp
// Namespace: 
public class Board_Quest : Board // TypeDefIndex: 925
{
	// Fields
	public static Board_Quest instance; // 0x0
	[SerializeField]
	private Transform spriteMask; // 0x20
	[SerializeField]
	private UIObjectAnchors pointTopAnchors; // 0x28
	[SerializeField]
	private UIObjectAnchors pointBotAnchors; // 0x30
	[SerializeField]
	private TextMeshPro[] textCountKeys; // 0x38
	[SerializeField]
	private TextMeshPro[] textTimeOpenFree; // 0x40
	[SerializeField]
	private Transform[] allBtnOpen; // 0x48
	[SerializeField]
	private Transform parentQuests; // 0x50
	[SerializeField]
	private TextMeshPro textQuestTimer; // 0x58
	[SerializeField]
	private TextMeshPro textCAQKeyCount; // 0x60
	[SerializeField]
	private TextMeshPro textCAQRemain; // 0x68
	[SerializeField]
	private TextMeshPro textCAQRemainCount; // 0x70
	[SerializeField]
	private GameObject textCAQCompleted; // 0x78
	[SerializeField]
	private TextMeshPro textCAQBtnCollect; // 0x80
	[SerializeField]
	private SpriteRenderer iconCAQBtnCollect; // 0x88
	[SerializeField]
	private ScrollView scrollView; // 0x90
	[SerializeField]
	private TextMeshPro textQuestClear; // 0x98
	private int keyMuliple; // 0xA0
	private Coroutine updateKey0; // 0xA8
	private int key0; // 0xB0
	private Coroutine updateKey1; // 0xB8
	private int key1; // 0xC0
	private Coroutine updateKey2; // 0xC8
	private int key2; // 0xD0
	[SerializeField]
	private SpriteRenderer btnWatchVideo; // 0xD8
	public static int countFx; // 0x8
	public static float zMax; // 0xC
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0xE0
	[SerializeField]
	private Popup_Notices popupNoVideo; // 0xE8
	private GameObject m_popupPremium; // 0xF0
	[SerializeField]
	private BoxCollider2D boxBound; // 0xF8
	[SerializeField]
	private BoxCollider2D boxContent; // 0x100
	private bool isHasVideo; // 0x108
	[SerializeField]
	private GameObject parentCollect; // 0x110
	private Coroutine focusCoroutine; // 0x118
	private double totalSecs; // 0x120
	private static int timeUpdate; // 0x10
	private GameObject[] boxFocus; // 0x128
	public static List<int> listQuestIndexs; // 0x18
	private static List<Bonus_Quest[]> allQuestBonus; // 0x20
	private static Bonus_Quest bonusClearAllQuests; // 0x28
	private static List<int[]> allQuestMaxValues; // 0x30
	public static int[] BoxKeyCost; // 0x38
	public static int[] KeyPrices; // 0x40
	public static int[] NumberRewards; // 0x48
	public static double[] AllTimeAds; // 0x50

	// Properties
	public static bool IsFirstResetQuest { get; set; }
	private GameObject popupPremium { get; }
	private int getQuestActiveCount { get; }
	public static int TotalGemSpend { get; set; }

	// Methods

	// RVA: 0x130756C Offset: 0x130356C VA: 0x130756C
	private void Start() { }

	// RVA: 0x1307988 Offset: 0x1303988 VA: 0x1307988
	public static bool get_IsFirstResetQuest() { }

	// RVA: 0x1307A00 Offset: 0x1303A00 VA: 0x1307A00
	public static void set_IsFirstResetQuest(bool value) { }

	// RVA: 0x1307A7C Offset: 0x1303A7C VA: 0x1307A7C
	private void OnEnable() { }

	// RVA: 0x1307D18 Offset: 0x1303D18 VA: 0x1307D18
	private void OnDisable() { }

	// RVA: 0x1307D70 Offset: 0x1303D70 VA: 0x1307D70 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x1307D94 Offset: 0x1303D94 VA: 0x1307D94 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x1307DB8 Offset: 0x1303DB8 VA: 0x1307DB8 Slot: 9
	public override void Escape() { }

	// RVA: 0x1307DBC Offset: 0x1303DBC VA: 0x1307DBC
	public void OnPressedButtonBack() { }

	// RVA: 0x1307E28 Offset: 0x1303E28 VA: 0x1307E28
	public void OnPressedButtonOpenBox(int _index) { }

	// RVA: 0x1307ED0 Offset: 0x1303ED0 VA: 0x1307ED0
	public void OnPressedButtonCAQCollect(Transform _pointCollect) { }

	// RVA: 0x1307B98 Offset: 0x1303B98 VA: 0x1307B98
	private void CheckKey0() { }

	// RVA: 0x1308E44 Offset: 0x1304E44 VA: 0x1308E44
	private IEnumerator UpdateKey0() { }

	// RVA: 0x1307BD8 Offset: 0x1303BD8 VA: 0x1307BD8
	private void CheckKey1() { }

	// RVA: 0x1308ECC Offset: 0x1304ECC VA: 0x1308ECC
	private IEnumerator UpdateKey1() { }

	// RVA: 0x1307C18 Offset: 0x1303C18 VA: 0x1307C18
	private void CheckKey2() { }

	// RVA: 0x1308F54 Offset: 0x1304F54 VA: 0x1308F54
	private IEnumerator UpdateKey2() { }

	// RVA: 0x1307CB8 Offset: 0x1303CB8 VA: 0x1307CB8
	private IEnumerator CheckQuestButtons() { }

	// RVA: 0x1309004 Offset: 0x1305004 VA: 0x1309004
	private void OnQuestGo(Quest_Bar _quest) { }

	// RVA: 0x13092B4 Offset: 0x13052B4 VA: 0x13092B4
	public static void OnUpdateQuestValue(int _questIndex, int _value = 1) { }

	// RVA: 0x1309D70 Offset: 0x1305D70 VA: 0x1309D70
	private void GoWatchVideo() { }

	// RVA: 0x130923C Offset: 0x130523C VA: 0x130923C
	private void GoBoard(BoardID _boardId) { }

	// RVA: 0x130A064 Offset: 0x1306064 VA: 0x130A064
	private bool IsVideoLoaded() { }

	// RVA: 0x130A0B4 Offset: 0x13060B4 VA: 0x130A0B4
	private GameObject get_popupPremium() { }

	// RVA: 0x130A1B0 Offset: 0x13061B0 VA: 0x130A1B0
	private void OnQuestCollect(Quest_Bar _quest) { }

	// RVA: 0x13081C0 Offset: 0x13041C0 VA: 0x13081C0
	private int get_getQuestActiveCount() { }

	// RVA: 0x1308398 Offset: 0x1304398 VA: 0x1308398
	private void ResfreshQuests() { }

	// RVA: 0x130B4B0 Offset: 0x13074B0 VA: 0x130B4B0
	private void SetStateCAQ() { }

	// RVA: 0x130A71C Offset: 0x130671C VA: 0x130A71C
	private void FocusCAQTextCount() { }

	// RVA: 0x130B524 Offset: 0x1307524 VA: 0x130B524
	private IEnumerator FocusCAQText() { }

	// RVA: 0x130B5AC Offset: 0x13075AC VA: 0x130B5AC
	public static bool IsFocus() { }

	// RVA: 0x130BA94 Offset: 0x1307A94 VA: 0x130BA94
	public static int get_TotalGemSpend() { }

	// RVA: 0x130BB00 Offset: 0x1307B00 VA: 0x130BB00
	public static void set_TotalGemSpend(int value) { }

	// RVA: 0x130BB70 Offset: 0x1307B70 VA: 0x130BB70
	public static void ResetDailyQuest(bool _newDay = False) { }

	// RVA: 0x130BE84 Offset: 0x1307E84 VA: 0x130BE84
	public static void ClearDatas() { }

	// RVA: 0x1307C58 Offset: 0x1303C58 VA: 0x1307C58
	private IEnumerator AdsTimer() { }

	// RVA: 0x130B970 Offset: 0x1307970 VA: 0x130B970
	private static bool IsTimeAdsReady(int _type) { }

	// RVA: 0x130811C Offset: 0x130411C VA: 0x130811C
	private static int GetQuestValue(int _indexQuest) { }

	// RVA: 0x13082F0 Offset: 0x13042F0 VA: 0x13082F0
	private static void SetQuestValue(int _indexQuest, int _value) { }

	// RVA: 0x130A584 Offset: 0x1306584 VA: 0x130A584
	public Bonus_Quest GetBonusQuest(int _indexQuest) { }

	// RVA: 0x130A678 Offset: 0x1306678 VA: 0x130A678
	private static int GetQuestCollectIndex(int _indexQuest) { }

	// RVA: 0x130BD84 Offset: 0x1307D84 VA: 0x130BD84
	private static void SetQuestCollectIndex(int _indexQuest, int _value) { }

	// RVA: 0x13098B8 Offset: 0x13058B8 VA: 0x13098B8
	private static int GetQuestCheckCollectIndex(int _indexQuest) { }

	// RVA: 0x130995C Offset: 0x130595C VA: 0x130995C
	private static void SetQuestCheckCollectIndex(int _indexQuest, int _value) { }

	// RVA: 0x130ACA8 Offset: 0x1306CA8 VA: 0x130ACA8
	private static int GetQuestMaxValue(int _indexQuest) { }

	// RVA: 0x130AC08 Offset: 0x1306C08 VA: 0x130AC08
	private static string GetQuestName(int _indexQuest) { }

	// RVA: 0x1309A04 Offset: 0x1305A04 VA: 0x1309A04
	private static string GetQuestInfo(int _indexQuest, int _indexCollect = 0) { }

	// RVA: 0x130BF54 Offset: 0x1307F54 VA: 0x130BF54
	public void .ctor() { }

	// RVA: 0x130BFBC Offset: 0x1307FBC VA: 0x130BFBC
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x130D3FC Offset: 0x13093FC VA: 0x130D3FC
	private void <Start>b__17_0(object <p0>) { }
}

```

#### `Popup_PremiumDailyRewards`

```csharp
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

```

#### `Popup_FirstPurchase`

```csharp
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

```

#### `Board_Vip`

```csharp
// Namespace: 
public class Board_Vip : Board // TypeDefIndex: 1223
{
	// Fields
	public static BoardID backBoard; // 0x0
	public static Board_Vip instance; // 0x8
	[SerializeField]
	private Transform parentVipPlayers; // 0x20
	[SerializeField]
	private TextMeshPro textTip; // 0x28
	[SerializeField]
	private TextMeshPro textVipProgress; // 0x30
	[SerializeField]
	private SpriteRenderer vipProgressRenderer; // 0x38
	[SerializeField]
	private TextMeshPro textVipCrtLevel; // 0x40
	[SerializeField]
	private Transform parentVipPreview; // 0x48
	[SerializeField]
	private TextMeshPro[] allTextInfo; // 0x50
	[SerializeField]
	private TextMeshPro textPrice1; // 0x58
	[SerializeField]
	private SpriteRenderer iconBtnFreeRenderer; // 0x60
	[SerializeField]
	private SpriteRenderer iconBtnRenderer; // 0x68
	[SerializeField]
	private TextMeshPro textBtnFreePrice; // 0x70
	[SerializeField]
	private TextMeshPro textBtnPrice; // 0x78
	[SerializeField]
	private TextMeshPro textVipLevel; // 0x80
	[SerializeField]
	private GameObject btnNext; // 0x88
	[SerializeField]
	private GameObject btnPrev; // 0x90
	[SerializeField]
	private TextMeshPro textUnlockSpecial; // 0x98
	[SerializeField]
	private TextMeshPro textLimitPurchase; // 0xA0
	[SerializeField]
	private Popup_Notices popupNoGems; // 0xA8
	public static int[] listVipPointNeeds; // 0x10
	[SerializeField]
	private GameObject vipLocked; // 0xB0
	private int vipIndexShow; // 0xB8
	private int[] allCostSaleVipRewards; // 0xC0
	private int[] allCostFakeVipRewards; // 0xC8
	[SerializeField]
	private GameObject btnIAP; // 0xD0
	[SerializeField]
	private GameObject btnGems; // 0xD8
	[SerializeField]
	private SpriteRenderer btnIAPRend; // 0xE0
	[SerializeField]
	private Transform parentRewardsSpecial; // 0xE8
	[SerializeField]
	private Transform parentRewardsFree; // 0xF0
	public static float[] TimeFreeItems; // 0x18
	[SerializeField]
	private TextMeshPro txtTimeFreeItems; // 0xF8
	private GameObject m_popupPremium; // 0x100
	[SerializeField]
	private GameObject coverRewards; // 0x108
	[SerializeField]
	private Transform listRewards; // 0x110
	[SerializeField]
	private GameObject boxRewardTimeItem; // 0x118
	[SerializeField]
	private TextMeshPro txtRewardTimeFreeItems; // 0x120
	private bool isGetFree; // 0x128
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x130
	[SerializeField]
	private Popup_Notices popupInitialize; // 0x138
	[SerializeField]
	private GameObject loadingObject; // 0x140
	[SerializeField]
	private TextMeshPro textPrice; // 0x148
	[SerializeField]
	private TextMeshPro textVipPoint; // 0x150
	private string[] allPrices; // 0x158
	private int currentIndex; // 0x160
	private static int[] allIdPacks; // 0x20
	private Coroutine checkTimeOut; // 0x168

	// Properties
	private GameObject popupPremium { get; }
	public static bool IsGetVipFree { get; set; }

	// Methods

	// RVA: 0x13AE158 Offset: 0x13AA158 VA: 0x13AE158
	private void Awake() { }

	// RVA: 0x13AE1B4 Offset: 0x13AA1B4 VA: 0x13AE1B4
	private void OnEnable() { }

	// RVA: 0x13AE800 Offset: 0x13AA800 VA: 0x13AE800 Slot: 7
	public override void OpenBoard() { }

	// RVA: 0x13AE824 Offset: 0x13AA824 VA: 0x13AE824 Slot: 8
	public override void CloseBoard() { }

	// RVA: 0x13AE910 Offset: 0x13AA910 VA: 0x13AE910 Slot: 9
	public override void Escape() { }

	// RVA: 0x13AE914 Offset: 0x13AA914 VA: 0x13AE914
	public void OnPressedButtonBack() { }

	// RVA: 0x13AE984 Offset: 0x13AA984 VA: 0x13AE984
	public void OnPressedButtonVipNext() { }

	// RVA: 0x13AEE48 Offset: 0x13AAE48 VA: 0x13AEE48
	public void OnPressedButtonVipPrev() { }

	// RVA: 0x13AEEA4 Offset: 0x13AAEA4 VA: 0x13AEEA4
	public void OnPressedButtonVipTopUp() { }

	// RVA: 0x13AEF48 Offset: 0x13AAF48 VA: 0x13AEF48
	public void OnPressedButtonVipBuyRewards() { }

	// RVA: 0x13AFE78 Offset: 0x13ABE78 VA: 0x13AFE78
	public void OnPressedButtonVipPurchaseRewards() { }

	// RVA: 0x13B031C Offset: 0x13AC31C VA: 0x13B031C
	public void OnPressedButtonVipBuyRewardsFree() { }

	// RVA: 0x13AE2AC Offset: 0x13AA2AC VA: 0x13AE2AC
	private void SetPlayerVip() { }

	// RVA: 0x13AEA68 Offset: 0x13AAA68 VA: 0x13AEA68
	private void SetDisplayVip(int _index, int _reverse) { }

	// RVA: 0x13B139C Offset: 0x13AD39C VA: 0x13B139C
	public void SetPrices() { }

	// RVA: 0x13AE740 Offset: 0x13AA740 VA: 0x13AE740
	private IEnumerator UpdateTimer() { }

	// RVA: 0x13B0440 Offset: 0x13AC440 VA: 0x13B0440
	private void SetRewardsSpecial(int _indexVip) { }

	// RVA: 0x13B0AE8 Offset: 0x13ACAE8 VA: 0x13B0AE8
	public void SetRewardsFree(int _indexVip) { }

	// RVA: 0x13AF0A0 Offset: 0x13AB0A0 VA: 0x13AF0A0
	private bool IsBoughtVipRewards(int _indexVip) { }

	// RVA: 0x13B1DE8 Offset: 0x13ADDE8 VA: 0x13B1DE8
	private void SetBoughtVipRewards(int _indexVip) { }

	// RVA: 0x13B1E8C Offset: 0x13ADE8C VA: 0x13B1E8C
	private GameObject get_popupPremium() { }

	// RVA: 0x13B1F88 Offset: 0x13ADF88 VA: 0x13B1F88
	public void OnPressedButtonExitRewardCover() { }

	// RVA: 0x13AF14C Offset: 0x13AB14C VA: 0x13AF14C
	private void OnBuyVipRewards(int _indexVip, bool _free = False) { }

	// RVA: 0x13B2074 Offset: 0x13AE074 VA: 0x13B2074
	private void SaveDataReward(int _index, int _value, Device _device, int _idDrone = 0) { }

	// RVA: 0x13B258C Offset: 0x13AE58C VA: 0x13B258C
	public static int ReachVip(int _addPoint) { }

	// RVA: 0x13B2630 Offset: 0x13AE630 VA: 0x13B2630
	public static void ResetVipFree() { }

	// RVA: 0x13B03C8 Offset: 0x13AC3C8 VA: 0x13B03C8
	public static bool get_IsGetVipFree() { }

	// RVA: 0x13B2510 Offset: 0x13AE510 VA: 0x13B2510
	public static void set_IsGetVipFree(bool value) { }

	// RVA: 0x13AE7A0 Offset: 0x13AA7A0 VA: 0x13AE7A0
	private IEnumerator IESetPrices() { }

	// RVA: 0x13AFFD8 Offset: 0x13ABFD8 VA: 0x13AFFD8
	private void OnBuy() { }

	// RVA: 0x13AFF2C Offset: 0x13ABF2C VA: 0x13AFF2C
	private static bool IsDailyBought(int indexVip) { }

	// RVA: 0x13B27F4 Offset: 0x13AE7F4 VA: 0x13B27F4
	private static void SetDailyBought(int indexVip, bool bought) { }

	// RVA: 0x13B2A10 Offset: 0x13AEA10 VA: 0x13B2A10
	public void .ctor() { }

	// RVA: 0x13B2AC8 Offset: 0x13AEAC8 VA: 0x13B2AC8
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x13B2C00 Offset: 0x13AEC00 VA: 0x13B2C00
	private void <OnPressedButtonExitRewardCover>b__56_0() { }

	[CompilerGenerated]
	// RVA: 0x13B2D20 Offset: 0x13AED20 VA: 0x13B2D20
	private void <IESetPrices>g__OnInitialized|77_1() { }

	[CompilerGenerated]
	// RVA: 0x13B28C4 Offset: 0x13AE8C4 VA: 0x13B28C4
	private IEnumerator <OnBuy>g__IECheckLoadingTimeOut|78_2() { }

	[CompilerGenerated]
	// RVA: 0x13B2924 Offset: 0x13AE924 VA: 0x13B2924
	private void <OnBuy>g__Purchase|78_3(int _id, Action<int, bool> _callback) { }

	[CompilerGenerated]
	// RVA: 0x13B2F88 Offset: 0x13AEF88 VA: 0x13B2F88
	private void <OnBuy>g__OnPurchased|78_4(int _idProduct, bool _successed) { }
}

```

#### `RankManager`

```csharp
// Namespace: 
public class RankManager : MonoBehaviour // TypeDefIndex: 654
{
	// Fields
	[SerializeField]
	private GameObject loadingObject; // 0x20
	[SerializeField]
	private Popup_Notices popupNoInternet; // 0x28
	[SerializeField]
	private Popup_Notices popupUploadFailed; // 0x30
	private Coroutine getTimeOnline; // 0x38
	[SerializeField]
	private GameObject btnExitCover; // 0x40

	// Properties
	public static bool IsUpdateRankPoint { get; set; }
	public static bool IsWaitSummaryRank { get; set; }

	// Methods

	// RVA: 0x127BF4C Offset: 0x1277F4C VA: 0x127BF4C
	public static bool get_IsUpdateRankPoint() { }

	// RVA: 0x127BFC4 Offset: 0x1277FC4 VA: 0x127BFC4
	public static void set_IsUpdateRankPoint(bool value) { }

	// RVA: 0x127C040 Offset: 0x1278040 VA: 0x127C040
	public static bool get_IsWaitSummaryRank() { }

	// RVA: 0x127C0B8 Offset: 0x12780B8 VA: 0x127C0B8
	public static void set_IsWaitSummaryRank(bool value) { }

	// RVA: 0x127C134 Offset: 0x1278134 VA: 0x127C134
	public void OnClickExit() { }

	// RVA: 0x127C154 Offset: 0x1278154 VA: 0x127C154
	private void GetTimeOnline(Action<DateTime> callback) { }

	// RVA: 0x127C1A4 Offset: 0x12781A4 VA: 0x127C1A4
	private IEnumerator IEGetTimeOnline(Action<DateTime> callback) { }

	// RVA: 0x127C22C Offset: 0x127822C VA: 0x127C22C
	public IEnumerator IECheckCampaignRankings(int rankPoints, Action<bool> resuft) { }

	// RVA: 0x127C2CC Offset: 0x12782CC VA: 0x127C2CC
	private IEnumerator IEAutoActiveExitCover() { }

	// RVA: 0x127C354 Offset: 0x1278354 VA: 0x127C354
	public IEnumerator IESetCampaignRankings(int rankPoints, Action<bool> resuft) { }

	// RVA: 0x127C3F4 Offset: 0x12783F4 VA: 0x127C3F4
	private IEnumerator IETryGetRoomRankCampaign(RankStruct user, string seed, Action<string> callback) { }

	// RVA: 0x127C49C Offset: 0x127849C VA: 0x127C49C
	private IEnumerator IECheckRankReadyToUploadPoint(Action<bool> ready) { }

	// RVA: 0x127C534 Offset: 0x1278534 VA: 0x127C534
	private IEnumerator IECheckRankOpen(Action<bool, bool> resuft) { }

	// RVA: 0x127C5CC Offset: 0x12785CC VA: 0x127C5CC
	private void GetGameConfig(Action<bool> success) { }

	// RVA: 0x127C774 Offset: 0x1278774 VA: 0x127C774
	private void CheckUserRequestAccess(Action<bool> resuft) { }

	// RVA: 0x127C958 Offset: 0x1278958 VA: 0x127C958
	private void CheckBanStatus(string uid, Action<bool, BanAccount> callback) { }

	// RVA: 0x127C834 Offset: 0x1278834 VA: 0x127C834
	private void CheckUserSignInOrRestoreYourDatas(Action<bool> resuftCallback) { }

	// RVA: 0x127CB84 Offset: 0x1278B84 VA: 0x127CB84
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x127CB24 Offset: 0x1278B24 VA: 0x127CB24
	internal static IEnumerator <CheckUserSignInOrRestoreYourDatas>g__IESignInOrRestoreYourDatas|23_1(Action<bool> eventCallback) { }
}

```

## PvP / arena

39 classes

| class | base |
|---|---|
| `ArenaConfig` |  |
| `ArenaDatabaseCleaner` | MonoBehaviour |
| `ArenaHub` | MonoBehaviour |
| `ArenaManager` | MonoBehaviour |
| `ArenaManager.SummaryStruct` |  |
| `ArenaManager.WaitTask` | CustomYieldInstruction |
| `ArenaRankItem` | MonoBehaviour |
| `ArenaRankSetup` |  |
| `ArenaUserProfile` |  |
| `ArenaUserStruct` |  |
| `Arena_Shop` | MonoBehaviour |
| `Board_Arena` | Board |
| `Board_Arena.ArenaRewards` |  |
| `Board_PVP` | Board |
| `Board_RoomPVP` | MonoBehaviour |
| `ConfigLeagues` |  |
| `PVPLauncher` | Singleton<PVPLauncher> |
| `PVPLogo` | MonoBehaviour |
| `PVPManager` |  |
| `PVPMode_Hunter` | MonoBehaviour |
| `PVPPlayDatas` |  |
| `PVPRankDisplayer` | MonoBehaviour |
| `PVPRankItem` | MonoBehaviour |
| `PVPReward` |  |
| `PVPSummaryItem` | MonoBehaviour |
| `PVP_Endgame` | MonoBehaviour |
| `PVP_Manager` | MonoBehaviour |
| `PVP_Player` | MonoBehaviour |
| `PVP_Shop` | MonoBehaviour |
| `PVP_TabReward` | MonoBehaviour |
| `Player` | PlayGamesUserProfile |
| `PlayerChat` |  |
| `PlayerItemPVP` | MonoBehaviour |
| `PlayerItemPVPEndGame` | MonoBehaviour |
| `PlayerPlayDatas` |  |
| `PlayerScore` |  |
| `Room` |  |
| `UserDataLeagues` | UserPointDataLeagues |
| `UserPointDataLeagues` |  |

#### `ArenaManager`

```csharp
// Namespace: 
public class ArenaManager : MonoBehaviour // TypeDefIndex: 401
{
	// Fields
	public static bool IsOpen; // 0x0
	public static int MaxRoomCount; // 0x4
	public static int MinUserCount; // 0x8
	public static double SeasonSummaryTime; // 0x10
	public static int[] SeasonTimes; // 0x18
	public static int RankMapsIndex; // 0x20
	public static int[] RankUpIndexs; // 0x28
	public static int[] RankDropIndexs; // 0x30
	public static string[] rewards; // 0x38

	// Properties
	public static string pathRoot { get; }
	public static int MyRank { get; set; }

	// Methods

	// RVA: 0x15A27EC Offset: 0x159E7EC VA: 0x15A27EC
	public static string get_pathRoot() { }

	// RVA: 0x15A28B8 Offset: 0x159E8B8 VA: 0x15A28B8
	public static int get_MyRank() { }

	// RVA: 0x15A2924 Offset: 0x159E924 VA: 0x15A2924
	public static void set_MyRank(int value) { }

	// RVA: 0x15A2994 Offset: 0x159E994 VA: 0x15A2994
	public void SetUserProfile(ArenaUserProfile userProfile, Action callback) { }

	// RVA: 0x15A29B4 Offset: 0x159E9B4 VA: 0x15A29B4
	private IEnumerator IESetUserProfile(ArenaUserProfile userProfile, Action callback) { }

	// RVA: 0x15A2A48 Offset: 0x159EA48 VA: 0x15A2A48
	public void CheckLogInRank(string userID, string userName, Action<int, ArenaUserProfile, int> callback) { }

	// RVA: 0x15A2AD0 Offset: 0x159EAD0 VA: 0x15A2AD0
	private IEnumerator IECheckUserStatus(string userId, string userName, Action<int, ArenaUserProfile, int> callback) { }

	// RVA: 0x15A2B78 Offset: 0x159EB78 VA: 0x15A2B78
	public void GetTimeSpan(int rank, Action<DateTime> callback) { }

	// RVA: 0x15A2B98 Offset: 0x159EB98 VA: 0x15A2B98
	private IEnumerator IEGetTimeSpan(int rank, Action<DateTime> callback) { }

	// RVA: 0x15A2C38 Offset: 0x159EC38 VA: 0x15A2C38
	private IEnumerator SummaryRank(ArenaUserProfile userProfile, Action<ArenaUserProfile, bool, int> callback) { }

	// RVA: 0x15A2CD4 Offset: 0x159ECD4 VA: 0x15A2CD4
	private IEnumerator IEResetSeason(int rank, DateTime timeUTC, Action<bool> callback) { }

	// RVA: 0x15A2D74 Offset: 0x159ED74 VA: 0x15A2D74
	private void SetSummaryDatas(int season, int rank, int roomIndex, Dictionary<string, object> listRanks, Action<bool> callback) { }

	// RVA: 0x15A2FF8 Offset: 0x159EFF8 VA: 0x15A2FF8
	private void DeleteRoom(int rank, int roomIndex, Action<bool> callback) { }

	// RVA: 0x15A311C Offset: 0x159F11C VA: 0x15A311C
	private IEnumerator TryToUploadRankDatas(ArenaUserProfile userProfile, ArenaUserStruct userStruct, Action<ArenaUserProfile> resuft) { }

	// RVA: 0x15A31C4 Offset: 0x159F1C4 VA: 0x15A31C4
	private void BackUpDatas(Action<bool> callback) { }

	// RVA: 0x15A3438 Offset: 0x159F438 VA: 0x15A3438
	private IEnumerator IECheckLogInRank(string userId, Action<ArenaUserProfile> callback) { }

	// RVA: 0x15A34CC Offset: 0x159F4CC VA: 0x15A34CC
	public void GetRankList(ArenaUserProfile arenaUserProfile, Action<List<ArenaUserStruct>> callback) { }

	// RVA: 0x15A34EC Offset: 0x159F4EC VA: 0x15A34EC
	private IEnumerator IEDownloadRank(ArenaUserProfile arenaUserProfile, Action<List<ArenaUserStruct>> callback) { }

	// RVA: 0x15A3588 Offset: 0x159F588 VA: 0x15A3588
	private void QuickSort(ref List<ArenaUserStruct> datas, int l, int r) { }

	// RVA: 0x15A3748 Offset: 0x159F748 VA: 0x15A3748
	public void SetUserRank(ArenaUserProfile profile, ArenaUserStruct userStruct, Action<int> callback) { }

	// RVA: 0x15A37D4 Offset: 0x159F7D4 VA: 0x15A37D4
	private IEnumerator IEGetRoom(ArenaUserProfile profile, ArenaUserStruct userStruct, Action<int> callback, int timeOut) { }

	// RVA: 0x15A3888 Offset: 0x159F888 VA: 0x15A3888
	private IEnumerator IEFixLastRoom(ArenaUserProfile profile, ArenaUserStruct userStruct, int roomIndex, int timeOut, Action<int> callback) { }

	// RVA: 0x15A3948 Offset: 0x159F948 VA: 0x15A3948
	private IEnumerator IECheckAndAddUserToRoom(ArenaUserProfile profile, ArenaUserStruct userStruct, int roomIndex, Action<int> callback, int timeOut) { }

	// RVA: 0x15A3A0C Offset: 0x159FA0C VA: 0x15A3A0C
	public void ResetUserStatus(ArenaUserProfile userProfile, int count, Action<ArenaUserProfile, bool> callback) { }

	// RVA: 0x15A3A2C Offset: 0x159FA2C VA: 0x15A3A2C
	private IEnumerator IEResetUserProfileStatus(ArenaUserProfile userProfile, int count, Action<ArenaUserProfile, bool> callback) { }

	// RVA: 0x15A3AD8 Offset: 0x159FAD8 VA: 0x15A3AD8
	public void LoadRankSetups(int rank, Action<ArenaRankSetup> callback) { }

	// RVA: 0x15A3AF8 Offset: 0x159FAF8 VA: 0x15A3AF8
	private IEnumerator IELoadRankSetups(int rank, Action<ArenaRankSetup> callback) { }

	// RVA: 0x15A3B90 Offset: 0x159FB90 VA: 0x15A3B90
	public void SetRankSetups() { }

	// RVA: 0x15A3BB0 Offset: 0x159FBB0 VA: 0x15A3BB0
	private IEnumerator IESetRankSetups() { }

	// RVA: 0x15A3C30 Offset: 0x159FC30 VA: 0x15A3C30
	public void SetUserRandom() { }

	// RVA: 0x15A3F44 Offset: 0x159FF44 VA: 0x15A3F44
	private IEnumerator IESetUserRandom(ArenaUserProfile userProfile, ArenaUserStruct userStruct) { }

	// RVA: 0x15A3FE0 Offset: 0x159FFE0 VA: 0x15A3FE0
	public void LoadRemoteConfigs(Action<bool> initResuft) { }

	// RVA: 0x15A420C Offset: 0x15A020C VA: 0x15A420C
	public void .ctor() { }

	// RVA: 0x15A4214 Offset: 0x15A0214 VA: 0x15A4214
	private static void .cctor() { }
}

```

#### `ArenaConfig`

```csharp
// Namespace: 
public class ArenaConfig // TypeDefIndex: 402
{
	// Fields
	public static string RankSplit; // 0x0
	public static string SeasonTime; // 0x8
	public static int MaxRoomCount; // 0x10
	public static int MinRoomCount; // 0x14
	public static float SummaryTime; // 0x18
	public static bool IsOpen; // 0x1C

	// Methods

	// RVA: 0x15AC7F0 Offset: 0x15A87F0 VA: 0x15AC7F0
	private static void .cctor() { }
}

```

#### `ArenaUserProfile`

```csharp
// Namespace: 
public class ArenaUserProfile // TypeDefIndex: 406
{
	// Fields
	public string id; // 0x10
	public int creditPoints; // 0x18
	public int arenaRank; // 0x1C
	public int roomIndex; // 0x20
	public int season; // 0x24
	public int status; // 0x28

	// Methods

	// RVA: 0x15A15E0 Offset: 0x159D5E0 VA: 0x15A15E0
	public void .ctor(string id, int creditPoints, int arenaRank, int roomIndex, int season, int status) { }
}

```

#### `Board_RoomPVP`

```csharp
// Namespace: PVP
public class Board_RoomPVP : MonoBehaviour // TypeDefIndex: 1594
{
	// Fields
	[SerializeField]
	private Animator anim; // 0x20
	[SerializeField]
	private Transform player; // 0x28
	[SerializeField]
	private TextMeshPro textTimer; // 0x30
	[SerializeField]
	private PVP_Player mine; // 0x38
	[SerializeField]
	private PVP_Player[] allOpponents; // 0x40
	private float timeCount; // 0x48
	private Coroutine waiting; // 0x50
	private List<PVPPlayDatas> listOpponentDatas; // 0x58
	[SerializeField]
	private GameObject btnCancel; // 0x60
	[SerializeField]
	private TextMeshPro textRoomName; // 0x68
	private bool isStarted; // 0x70
	private GP_StateAnimPlayer gpStateAnimPlayer; // 0x78
	private Coroutine movePlayer; // 0x80

	// Methods

	// RVA: 0x1445F48 Offset: 0x1441F48 VA: 0x1445F48
	private void OnEnable() { }

	// RVA: 0x1446114 Offset: 0x1442114 VA: 0x1446114
	private IEnumerator LoadOpponents() { }

	// RVA: 0x1446174 Offset: 0x1442174 VA: 0x1446174
	private IEnumerator IELoadDataPlay() { }

	// RVA: 0x1446224 Offset: 0x1442224 VA: 0x1446224
	private void GetRooms(Action<List<Room>> onGetRooms) { }

	// RVA: 0x1446368 Offset: 0x1442368 VA: 0x1446368
	private IEnumerator IEJoinRoom() { }

	// RVA: 0x14463F0 Offset: 0x14423F0 VA: 0x14463F0
	private IEnumerator IECreateRoom() { }

	// RVA: 0x1446478 Offset: 0x1442478 VA: 0x1446478
	private void Setup(Room room) { }

	// RVA: 0x1446830 Offset: 0x1442830 VA: 0x1446830
	private void UISetup(Room room) { }

	// RVA: 0x1446E20 Offset: 0x1442E20 VA: 0x1446E20
	private void StartPlay() { }

	// RVA: 0x144708C Offset: 0x144308C VA: 0x144708C
	private void OnDestroy() { }

	// RVA: 0x144718C Offset: 0x144318C VA: 0x144718C
	private IEnumerator IELoadRandomOpponent(int number = 5) { }

	// RVA: 0x1447224 Offset: 0x1443224 VA: 0x1447224
	private IEnumerator IESetupOpponents(List<PVPPlayDatas> listOpponents, Player[] listProfile) { }

	// RVA: 0x14460B4 Offset: 0x14420B4 VA: 0x14460B4
	private IEnumerator IEWaitOpponents() { }

	// RVA: 0x1446E7C Offset: 0x1442E7C VA: 0x1446E7C
	public void ShowPlayer() { }

	// RVA: 0x14472E8 Offset: 0x14432E8 VA: 0x14472E8
	private IEnumerator ShowPlayer(Action _callback) { }

	// RVA: 0x144737C Offset: 0x144337C VA: 0x144737C
	private IEnumerator RotatePlayer() { }

	// RVA: 0x1447404 Offset: 0x1443404 VA: 0x1447404
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1447480 Offset: 0x1443480 VA: 0x1447480
	private void <ShowPlayer>b__25_0() { }
}

```

#### `PVP_Player`

```csharp
// Namespace: PVP
public class PVP_Player : MonoBehaviour // TypeDefIndex: 1607
{
	// Fields
	[SerializeField]
	private TextMeshPro playerNameText; // 0x20
	[SerializeField]
	private TextMeshPro rankText; // 0x28
	[SerializeField]
	private GameObject loadingObj; // 0x30
	[SerializeField]
	private GameObject activeObj; // 0x38
	[SerializeField]
	private SpriteRenderer avatarRen; // 0x40
	[SerializeField]
	private GameObject loadingAvatar; // 0x48
	public string id; // 0x50
	[SerializeField]
	private TextMeshPro messageText; // 0x58
	[SerializeField]
	private SpriteRenderer bgMessage; // 0x60
	[SerializeField]
	private Animator messageAnim; // 0x68
	private string message; // 0x70

	// Methods

	// RVA: 0x1446B54 Offset: 0x1442B54 VA: 0x1446B54
	public void Setup(Player player) { }

	// RVA: 0x144C79C Offset: 0x144879C VA: 0x144C79C
	public void ShowMessage(string message) { }

	// RVA: 0x144C898 Offset: 0x1448898 VA: 0x144C898
	private string GetRankString(int rank, int level) { }

	// RVA: 0x144C978 Offset: 0x1448978 VA: 0x144C978
	public void .ctor() { }
}

```

#### `PlayerItemPVP`

```csharp
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

```

## Ads / IAP / analytics

#### `AdsCaller`

```csharp
// Namespace: 
public class AdsCaller : MonoBehaviour // TypeDefIndex: 1490
{
	// Fields
	private static AdsCaller Instance; // 0x0
	private static readonly float TimeRate; // 0x8
	private static float TimeActiveAds; // 0xC
	private static float TimeToInterstitialReady; // 0x10

	// Properties
	public static bool IsNeverRequestGoogleRewardedAd { get; }
	public static bool IsCanRequestGoogleRewardedAd { get; }
	public static bool IsNeverRequestGoogleInterstitialAd { get; }
	public static bool IsCanRequestGoogleInterstitialAd { get; }
	public static bool IsSkipRewardedAd { get; }
	public static int CountShowInterstitial { get; set; }
	public static int CountEndgameCallInterstitial { get; set; }
	public static bool NoAds { get; }

	// Methods

	[RuntimeInitializeOnLoadMethod]
	// RVA: 0x142CD18 Offset: 0x1428D18 VA: 0x142CD18
	private static void CreateInstance() { }

	// RVA: 0x142CE34 Offset: 0x1428E34 VA: 0x142CE34
	private void Awake() { }

	// RVA: 0x142CFA0 Offset: 0x1428FA0 VA: 0x142CFA0
	public static bool HasAdsInterstitial() { }

	// RVA: 0x142D128 Offset: 0x1429128 VA: 0x142D128
	public static bool get_IsNeverRequestGoogleRewardedAd() { }

	// RVA: 0x142D188 Offset: 0x1429188 VA: 0x142D188
	public static bool get_IsCanRequestGoogleRewardedAd() { }

	// RVA: 0x142D1F0 Offset: 0x14291F0 VA: 0x142D1F0
	public static bool get_IsNeverRequestGoogleInterstitialAd() { }

	// RVA: 0x142D280 Offset: 0x1429280 VA: 0x142D280
	public static bool get_IsCanRequestGoogleInterstitialAd() { }

	// RVA: 0x142D310 Offset: 0x1429310 VA: 0x142D310
	public static bool get_IsSkipRewardedAd() { }

	// RVA: 0x142D370 Offset: 0x1429370 VA: 0x142D370
	public static void CallEndgameInterstitial(Action removeAdsEvent, Action exitEvent) { }

	// RVA: 0x142DCA0 Offset: 0x1429CA0 VA: 0x142DCA0
	public static void CallHomeInterstitial(Action removeAdsEvent) { }

	// RVA: 0x142DC84 Offset: 0x1429C84 VA: 0x142DC84
	private static void CheckRequest() { }

	// RVA: 0x142DA28 Offset: 0x1429A28 VA: 0x142DA28
	public static int get_CountShowInterstitial() { }

	// RVA: 0x142DA94 Offset: 0x1429A94 VA: 0x142DA94
	public static void set_CountShowInterstitial(int value) { }

	// RVA: 0x142D94C Offset: 0x142994C VA: 0x142D94C
	public static int get_CountEndgameCallInterstitial() { }

	// RVA: 0x142D9B8 Offset: 0x14299B8 VA: 0x142D9B8
	public static void set_CountEndgameCallInterstitial(int value) { }

	// RVA: 0x142D0CC Offset: 0x14290CC VA: 0x142D0CC
	public static bool get_NoAds() { }

	// RVA: 0x142E0F8 Offset: 0x142A0F8 VA: 0x142E0F8
	public static void ShowRewardedVideo(AdPos position, Action onStart, Action<bool> onFinish) { }

	// RVA: 0x142E3DC Offset: 0x142A3DC VA: 0x142E3DC
	public static bool IsRewardedVideoReady() { }

	// RVA: 0x142E3E0 Offset: 0x142A3E0 VA: 0x142E3E0
	public void .ctor() { }

	// RVA: 0x142E3E8 Offset: 0x142A3E8 VA: 0x142E3E8
	private static void .cctor() { }

	[CompilerGenerated]
	// RVA: 0x142DBC8 Offset: 0x1429BC8 VA: 0x142DBC8
	internal static void <CallEndgameInterstitial>g__ShowIntersAd|17_0() { }

	[CompilerGenerated]
	// RVA: 0x142D7D0 Offset: 0x14297D0 VA: 0x142D7D0
	internal static void <CallEndgameInterstitial>g__ShowCrossAd|17_1(ref AdsCaller.<>c__DisplayClass17_0 ) { }
}

```

#### `AdjustEventTracking`

```csharp
// Namespace: 
public class AdjustEventTracking : MonoBehaviour // TypeDefIndex: 1
{
	// Methods

	// RVA: 0x12246A4 Offset: 0x12206A4 VA: 0x12246A4
	public static void TrackEvent(string eventToken) { }

	// RVA: 0x12246A8 Offset: 0x12206A8 VA: 0x12246A8
	public static void TrackInAppRevenue(double price, string currency, string transactionID) { }

	// RVA: 0x12246AC Offset: 0x12206AC VA: 0x12246AC
	public static void TrackMAXAdRevenue(double amount, string adRevenueNetwork, string adRevenueUnit, string adRevenuePlacement) { }

	// RVA: 0x12246B0 Offset: 0x12206B0 VA: 0x12246B0
	public void .ctor() { }
}

```

#### `UserDataAnalysics`

```csharp
// Namespace: 
public class UserDataAnalysics : MonoBehaviour // TypeDefIndex: 13
{
	// Fields
	public List<string> allListIds; // 0x20
	public List<UserDataAnalysics.SortUser> listUserSorted; // 0x28
	public string resuft; // 0x30
	public int minStageTarget; // 0x38
	public int maxStageTarget; // 0x3C
	public int minTechLvl; // 0x40
	public int maxTechLvl; // 0x44

	// Methods

	// RVA: 0x1225C44 Offset: 0x1221C44 VA: 0x1225C44
	private void SortUsers() { }

	// RVA: 0x1225DCC Offset: 0x1221DCC VA: 0x1225DCC
	private IEnumerator IESortUserByStageTarget(List<string> allUsers) { }

	// RVA: 0x1225E60 Offset: 0x1221E60 VA: 0x1225E60
	private void OnGUI() { }

	// RVA: 0x1225EFC Offset: 0x1221EFC VA: 0x1225EFC
	public void .ctor() { }

	[CompilerGenerated]
	// RVA: 0x1225FC8 Offset: 0x1221FC8 VA: 0x1225FC8
	private void <SortUsers>b__2_0(DataSnapshot dataSnapshot) { }
}

```

#### `LogInFirebase`

```csharp
// Namespace: 
public class LogInFirebase : MonoBehaviour // TypeDefIndex: 464
{
	// Fields
	[SerializeField]
	private Popup_ChooseVersionDatas popupChooseVersionDatas; // 0x20
	[SerializeField]
	private Popup_Notices popupConfirmBackup; // 0x28

	// Methods

	// RVA: 0x15C4B90 Offset: 0x15C0B90 VA: 0x15C4B90
	public void CheckAndLogInFirebaseWithGooglePlayGames(Action<int> callback) { }

	// RVA: 0x15C4C4C Offset: 0x15C0C4C VA: 0x15C4C4C
	private void SignInGooglePlayGames(Action<bool> callback) { }

	// RVA: 0x15C4DC4 Offset: 0x15C0DC4 VA: 0x15C4DC4
	private void CheckAndGetOldDatas(Action<int, string, string> callback) { }

	// RVA: 0x15C5060 Offset: 0x15C1060 VA: 0x15C5060
	private void CheckAndLogInFirebaseWithGPG(Action<int, FirebaseUser> callback) { }

	// RVA: 0x15C5538 Offset: 0x15C1538 VA: 0x15C5538
	private void CheckAndFixDatas(string json, FirebaseUser user, Action<int> callback) { }

	// RVA: 0x15C57EC Offset: 0x15C17EC VA: 0x15C57EC
	private void DeleteOldDatas(string path, Action<bool> callback) { }

	// RVA: 0x15C5994 Offset: 0x15C1994 VA: 0x15C5994
	private void BackupDatas(string id, Action<bool> callback) { }

	// RVA: 0x15C5710 Offset: 0x15C1710 VA: 0x15C5710
	private void ChooseVersion(DataStruct svDatas, DataStruct dvDatas, Action<int> callback) { }

	// RVA: 0x15C5B80 Offset: 0x15C1B80 VA: 0x15C5B80
	private void QuestionBackup(Action<int> callback) { }

	// RVA: 0x15C5C84 Offset: 0x15C1C84 VA: 0x15C5C84
	public void .ctor() { }
}

```

#### `IAPSystem`

```csharp
// Namespace: 
public class IAPSystem // TypeDefIndex: 1339
{
	// Fields
	private const int MaxProductFetchRetries = 2;
	private const string ProcessedTransactionKeyPrefix = "IAP_PROCESSED_";
	private const string AppsFlyerTransactionKeyPrefix = "IAP_AF_TRACKED_";
	private static StoreController m_StoreController; // 0x0
	private static IAPSystem s_SingletonInstance; // 0x8
	private static bool s_EnableTestMode; // 0x10
	private static string[] s_NonConsumableProducts; // 0x18
	private static string[] s_ConsumableProducts; // 0x20
	private readonly Dictionary<string, List<PendingOrder>> m_RecoveredPendingOrders; // 0x10
	private readonly HashSet<string> m_ProcessingTransactions; // 0x18
	private bool m_IsInitializing; // 0x20
	private bool m_IsConnected; // 0x21
	private bool m_ConnectFailedDuringAttempt; // 0x22
	private bool m_ProductsFetchInProgress; // 0x23
	private bool m_ProductsFetchFinished; // 0x24
	private bool m_PurchasesFetchInProgress; // 0x25
	private bool m_PurchasesFetchFinished; // 0x26
	private bool m_PurchaseInProgress; // 0x27
	private bool m_RestoreInProgress; // 0x28
	private int m_ProductFetchRetryCount; // 0x2C
	private string m_ActivePurchaseProductId; // 0x30
	private Action<string, string> m_RestorePurchaseSuccess; // 0x38
	private Action<bool> m_RestoreComplete; // 0x40
	private IAPSystem.QueuedPurchase m_QueuedPurchase; // 0x48
	public Action<string, string> onPurchaseSuccess; // 0x50

	// Methods

	// RVA: 0x13E41AC Offset: 0x13E01AC VA: 0x13E41AC
	public void .ctor() { }

	[AsyncStateMachine(typeof(IAPSystem.<Initialize>d__28))]
	// RVA: 0x13E44C4 Offset: 0x13E04C4 VA: 0x13E44C4
	public void Initialize() { }

	[AsyncStateMachine(typeof(IAPSystem.<InitializeGameServicesSafeAsync>d__30))]
	// RVA: 0x13E4554 Offset: 0x13E0554 VA: 0x13E4554
	private static Task InitializeGameServicesSafeAsync() { }

	[AsyncStateMachine(typeof(IAPSystem.<InitializePurchasing>d__31))]
	// RVA: 0x13E4610 Offset: 0x13E0610 VA: 0x13E4610
	public void InitializePurchasing() { }

	// RVA: 0x13E469C Offset: 0x13E069C VA: 0x13E469C
	private void SubscribeStoreEvents() { }

	// RVA: 0x13E4B00 Offset: 0x13E0B00 VA: 0x13E4B00
	private void UnsubscribeStoreEvents() { }

	// RVA: 0x13E4F4C Offset: 0x13E0F4C VA: 0x13E4F4C
	private List<ProductDefinition> BuildProductDefinitions() { }

	// RVA: 0x13E5228 Offset: 0x13E1228 VA: 0x13E5228
	private void FetchProducts(List<ProductDefinition> definitions) { }

	// RVA: 0x13E52D4 Offset: 0x13E12D4 VA: 0x13E52D4
	private void FetchPurchases() { }

	// RVA: 0x13E534C Offset: 0x13E134C VA: 0x13E534C
	public bool IsInitialized() { }

	// RVA: 0x13E5454 Offset: 0x13E1454 VA: 0x13E5454
	public string GetConsumableProductByIndex(int index) { }

	// RVA: 0x13E54D0 Offset: 0x13E14D0 VA: 0x13E54D0
	public bool IsAvailableToPurchase(string requestedProductId) { }

	// RVA: 0x13E55F8 Offset: 0x13E15F8 VA: 0x13E55F8
	public void Purchase(string requestedProductId, Action<string, string> purchaseSuccess) { }

	// RVA: 0x13E57A4 Offset: 0x13E17A4 VA: 0x13E57A4
	private void BeginPurchase(string requestedProductId, Action<string, string> purchaseSuccess) { }

	// RVA: 0x13E6048 Offset: 0x13E2048 VA: 0x13E6048
	public void RestorePurchases() { }

	// RVA: 0x13E6054 Offset: 0x13E2054 VA: 0x13E6054
	public void RestorePurchases(Action<string, string> purchaseSuccess, Action<bool> onComplete) { }

	// RVA: 0x13E61D8 Offset: 0x13E21D8 VA: 0x13E61D8
	public string GetPriceString(string requestedProductId) { }

	// RVA: 0x13E6228 Offset: 0x13E2228 VA: 0x13E6228
	public string GetIsoCurrencyCode(string requestedProductId) { }

	// RVA: 0x13E6250 Offset: 0x13E2250 VA: 0x13E6250
	public Decimal GetPriceValue(string requestedProductId) { }

	// RVA: 0x13E6200 Offset: 0x13E2200 VA: 0x13E6200
	private Product GetAvailableProduct(string requestedProductId) { }

	// RVA: 0x13E556C Offset: 0x13E156C VA: 0x13E556C
	private Product GetProduct(string requestedProductId) { }

	// RVA: 0x13E62DC Offset: 0x13E22DC VA: 0x13E62DC
	private void OnStoreConnected() { }

	// RVA: 0x13E62E8 Offset: 0x13E22E8 VA: 0x13E62E8
	private void OnStoreDisconnected(StoreConnectionFailureDescription failure) { }

	// RVA: 0x13E6390 Offset: 0x13E2390 VA: 0x13E6390
	private void OnProductsFetched(List<Product> products) { }

	[AsyncStateMachine(typeof(IAPSystem.<OnProductsFetchFailed>d__54))]
	// RVA: 0x13E6468 Offset: 0x13E2468 VA: 0x13E6468
	private void OnProductsFetchFailed(ProductFetchFailed failure) { }

	// RVA: 0x13E6504 Offset: 0x13E2504 VA: 0x13E6504
	private void OnPurchasesFetched(Orders orders) { }

	// RVA: 0x13E7030 Offset: 0x13E3030 VA: 0x13E7030
	private void OnPurchasesFetchFailed(PurchasesFetchFailureDescription failure) { }

	// RVA: 0x13E711C Offset: 0x13E311C VA: 0x13E711C
	private void OnPurchasePending(PendingOrder order) { }

	// RVA: 0x13E5AC0 Offset: 0x13E1AC0 VA: 0x13E5AC0
	private void HandlePendingOrder(PendingOrder order, bool recoveredFromFetch) { }

	// RVA: 0x13E74A4 Offset: 0x13E34A4 VA: 0x13E74A4
	private void ConfirmOrder(PendingOrder order) { }

	// RVA: 0x13E78B0 Offset: 0x13E38B0 VA: 0x13E78B0
	private void OnPurchaseFailed(FailedOrder order) { }

	// RVA: 0x13E7A04 Offset: 0x13E3A04 VA: 0x13E7A04
	private void OnPurchaseDeferred(DeferredOrder order) { }

	// RVA: 0x13E7AA8 Offset: 0x13E3AA8 VA: 0x13E7AA8
	private void OnPurchaseConfirmed(Order order) { }

	// RVA: 0x13E6AF8 Offset: 0x13E2AF8 VA: 0x13E6AF8
	private void RestoreConfirmedOrder(ConfirmedOrder order) { }

	// RVA: 0x13E6FC0 Offset: 0x13E2FC0 VA: 0x13E6FC0
	private void CompleteRestore(bool success) { }

	// RVA: 0x13E53D4 Offset: 0x13E13D4 VA: 0x13E53D4
	private bool HasAnyFetchedProduct() { }

	// RVA: 0x13E7B7C Offset: 0x13E3B7C VA: 0x13E7B7C
	private List<ProductDefinition> GetMissingProductDefinitions() { }

	// RVA: 0x13E6FF0 Offset: 0x13E2FF0 VA: 0x13E6FF0
	private void TryExecuteQueuedPurchase() { }

	// RVA: 0x13E7D98 Offset: 0x13E3D98 VA: 0x13E7D98
	private void FailQueuedPurchase(string reason) { }

	// RVA: 0x13E6038 Offset: 0x13E2038 VA: 0x13E6038
	private void ClearActivePurchase() { }

	// RVA: 0x13E76BC Offset: 0x13E36BC VA: 0x13E76BC
	private void CacheRecoveredPending(string productId, PendingOrder order) { }

	// RVA: 0x13E59A0 Offset: 0x13E19A0 VA: 0x13E59A0
	private PendingOrder TakeRecoveredPending(string productId) { }

	// RVA: 0x13E75DC Offset: 0x13E35DC VA: 0x13E75DC
	private void RemoveRecoveredPending(string productId, PendingOrder order) { }

	// RVA: 0x13E7124 Offset: 0x13E3124 VA: 0x13E7124
	private static Product GetFirstProduct(PendingOrder order) { }

	// RVA: 0x13E72AC Offset: 0x13E32AC VA: 0x13E72AC
	private static bool IsTransactionProcessed(string transactionId) { }

	// RVA: 0x13E7834 Offset: 0x13E3834 VA: 0x13E7834
	private static void MarkTransactionProcessed(string transactionId) { }

	// RVA: 0x13E7E58 Offset: 0x13E3E58 VA: 0x13E7E58
	private static bool IsAppsFlyerTransactionTracked(string transactionId) { }

	// RVA: 0x13E7ED4 Offset: 0x13E3ED4 VA: 0x13E7ED4
	private static void MarkAppsFlyerTransactionTracked(string transactionId) { }

	// RVA: 0x13E7328 Offset: 0x13E3328 VA: 0x13E7328
	private static void TrackAppsFlyerAfterValidation(PendingOrder order, Product product) { }

	// RVA: 0x13E7F50 Offset: 0x13E3F50 VA: 0x13E7F50
	private static void SendAppsFlyerPurchase(Product product, string transactionId) { }

	[CompilerGenerated]
	// RVA: 0x13E83B0 Offset: 0x13E43B0 VA: 0x13E83B0
	private void <RestorePurchases>b__44_0(bool success, string message) { }
}

```
