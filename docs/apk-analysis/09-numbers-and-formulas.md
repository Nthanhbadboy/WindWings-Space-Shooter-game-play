# Config classes, formulas and constants

IL2CPP dumps keep field names and method signatures but not inspector values.
This file lists every config surface worth reading from the serialized assets.

## Config-type classes (78)

| class | kind | base |
|---|---|---|
| `.ArenaConfig` | class |  |
| `.ArenaRankItem` | class | MonoBehaviour |
| `.ArenaRankSetup` | class |  |
| `.Board_Maps` | class | Board |
| `.Board_Ranks` | class | Board |
| `.Board_Reborn.SortPlayerLevelStruct` | class |  |
| `.Board_Settings` | class | Board |
| `.Bonus_Get_Datas` | class | MonoBehaviour |
| `SpaceShooter.Bullet.Bullet_SineWave` | class | Bullet_Object |
| `SpaceShooter.SpawnSystem.Call_Data` | class | MonoBehaviour |
| `.CameraMoveMap` | class | MonoBehaviour |
| `.CampaignRankStruct` | class |  |
| `.CreatMapArena` | class | MonoBehaviour |
| `.CreatMapPvp` | class | MonoBehaviour |
| `.CreatNewMap` | class | MonoBehaviour |
| `.CultureInfoConverter.CultureInfoMapper` | class |  |
| `.Data_Boss` | class | ScriptableObject |
| `.Data_Items` | class | ScriptableObject |
| `.Data_Players` | class | ScriptableObject |
| `.DatatypeImplementation.SchemaDatatypeMap` | class | IComparable |
| `.Device_Get_Data` | class | MonoBehaviour |
| `.Device_Saved_Data` | class | MonoBehaviour |
| `SpaceShooter.Droid_Data_Balance` | class | MonoBehaviour |
| `.Drone_Get_Datas` | class | MonoBehaviour |
| `.Drone_Saved_Datas` | class | MonoBehaviour |
| `.EndlessRankStruct` | class |  |
| `.Enemy_Data_Balance` | class | MonoBehaviour |
| `SpaceShooter.EnemySystem.Enemy_Datas` | class | MonoBehaviour |
| `SpaceShooter.EnemySystem.Enemy_Get_Datas` | class | MonoBehaviour |
| `.EnumMap.EnumMapMember` | class |  |
| `.FacetsChecker.FacetsCompiler.Map` | struct |  |
| `SpaceShooter.Gameplay.GP_Datas` | class | MonoBehaviour |
| `.GameDatas` | class | MonoBehaviour |
| `.GraphicsAutoQualityLevel` | class | MonoBehaviour |
| `.LowLevelDictionary.DefaultComparer<TKey, TValue, T>` | class | IEqualityComparer<T> |
| `.LowLevelDictionary.Entry<TKey, TValue>` | class |  |
| `.LowLevelListWithIList.Enumerator<T>` | struct | IEnumerator<T>, IDisposable, IEnumerator |
| `.MapController` | class | MonoBehaviour |
| `.Map_Get_Datas` | class | MonoBehaviour |
| `.ObjectReader.TopLevelAssemblyTypeResolver` | class |  |
| `.PVPRankDisplayer` | class | MonoBehaviour |
| `.PVPRankItem` | class | MonoBehaviour |
| `.ParameterizedStrings.LowLevelStack` | class |  |
| `SpaceShooter.SpawnSystem.PinMap_Spawner` | class | Spawner |
| `SpaceShooter.Player.Player_Datas` | class | MonoBehaviour |
| `.Player_Device_Saved_Datas` | class | MonoBehaviour |
| `.Player_Get_Datas` | class | MonoBehaviour |
| `.Player_Saved_Datas` | class | MonoBehaviour |
| `.Popup_BattlePassLevelUp` | class | Popup_Notices |
| `.Popup_EventLevelUp` | class | MonoBehaviour |
| `.Popup_JoinRank` | class | Popup_Notices |
| `.Popup_PvPRankings` | class | MonoBehaviour |
| `.RankManager` | class | MonoBehaviour |
| `.RankPreload` | class | Singleton<RankPreload> |
| `.Rank_Header` | class | MonoBehaviour |
| `.Rank_Rewards` | class | MonoBehaviour |
| `.RegexCharClass.LowerCaseMapping` | struct |  |
| `.RewardRank_Behaviour` | class | MonoBehaviour |
| `.ShockWave_WorldSpace.genericDelegate` | class | MulticastDelegate |
| `.Stage_Behaviour` | class | MonoBehaviour |
| `.Stage_Datas` | class | MonoBehaviour |
| `.Stage_Generator` | class | MonoBehaviour |
| `.Stage_Get_Datas` | class | MonoBehaviour |
| `.Stage_Mission` | class | MonoBehaviour |
| `.StringStringMap.StringStringMapEnumerator` | class | IEnumerator, IEnumerator<KeyValuePair<string, stri |
| `.TMP_Settings.LineBreakingTable` | class |  |
| `.Tech_Ability_Data` | class | ScriptableObject |
| `.Tech_Datas` | class | MonoBehaviour |
| `.Tech_Stat` | class | MonoBehaviour |
| `.Tut_Settings` | class | MonoBehaviour |
| `.Tut_Settings1` | class | MonoBehaviour |
| `.UmAlQuraCalendar.DateMapping` | struct |  |
| `.VariantVariantMap.VariantVariantMapEnumerator` | class | IEnumerator, IEnumerator<KeyValuePair<Variant, Var |
| `.Wave` | class | MonoBehaviour |
| `.XmlNamedNodeMap.SmallXmlNodeList.SingleObjectEnumerator` | class | IEnumerator |
| `.XmlToDatasetMap.TableSchemaInfo` | class |  |
| `.XmlToDatasetMap.XmlNodeIdentety` | class |  |
| `.string.ProbabilisticMap` | struct |  |

## Game-specific constants

### `NetEventSource.Keywords`

```csharp
public const EventKeywords Default = 1;
public const EventKeywords Debug = 2;
public const EventKeywords EnterExit = 4;
```

### `SoxAtkTentacle`

```csharp
public const float mc_freqMul = 0.01;
```
