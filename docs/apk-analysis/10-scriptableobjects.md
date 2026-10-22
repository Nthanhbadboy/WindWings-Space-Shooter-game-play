# ScriptableObject / MonoBehaviour data (IL2CPP typetrees)

- source: `/tmp/apk/extract`
- Unity: `2022.3.62f3`

| class | instances |
|---|---:|
| `Enemy_Datas` | 981 |
| `SoundClip` | 92 |
| `SkeletonDataAsset` | 27 |
| `LanguageAssets` | 19 |
| `Tech_Ability_Data` | 6 |
| `RankManager` | 3 |
| `DataShopPack` | 2 |
| `Data_Players` | 2 |
| `GP_Datas` | 1 |
| `TMP_ColorGradient` | 1 |
| `Data_Items` | 1 |
| `Data_Boss` | 1 |
| `TMP_StyleSheet` | 1 |
| `TMP_Settings` | 1 |
| `IAPProduct` | 1 |
| `ArenaManager` | 1 |

## MonoBehaviour class inventory (top 40)

Toàn bộ class name trong `data.unity3d` (đầy đủ: `class-inventory.csv`)

| class | instances |
|---|---:|
| `Call_Point` | 23757 |
| `Call_Data` | 23757 |
| `PointToPoint_Spawner` | 13292 |
| `TextMeshPro` | 9789 |
| `PinMap_Spawner` | 3165 |
| `ButtonEvents` | 3139 |
| `Button_Sound` | 3008 |
| `LanguageTextMeshPro` | 2440 |
| `ObjectPool` | 2333 |
| `Rocket_Spawner` | 2019 |
| `PathCreator` | 1714 |
| `Path_Spawner` | 1688 |
| `Obj_Collider` | 1623 |
| `Spawner` | 1370 |
| `Waypoints_Spawner` | 1151 |
| `Enemy_EfxDestroyed` | 1134 |
| `ChangeSorting` | 1126 |
| `Box_Rewards` | 1065 |
| `Rotate` | 1044 |
| `Enemy_Sub` | 981 |
| `Enemy_Controller` | 981 |
| `Enemy_Display` | 981 |
| `Enemy_Movement` | 981 |
| `Enemy_Physics` | 981 |
| `Enemy_Health` | 981 |
| `Enemy_Datas` | 981 |
| `Enemy_Destroy` | 971 |
| `Enemy_Appear` | 914 |
| `Enemy_Hp_Bar` | 909 |
| `AirFree_Spawner` | 885 |
| `MeteoriteGenerator` | 852 |
| `BgObjectScaler` | 813 |
| `TMP_SubMesh` | 789 |
| `Item_Movement` | 702 |
| `Sub_Item` | 702 |
| `Item_Controller` | 702 |
| `Enemy_Burned` | 695 |
| `Wave` | 686 |
| `UIObjectAnchors` | 584 |
| `Popup_Notices` | 499 |

- error `script`: 1

## `GP_Datas` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 404,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 22028484608,
 "m_Name": "",
 "player.m_FileID": 0,
 "player.m_PathID": 2625,
 "ship.m_FileID": 0,
 "ship.m_PathID": 0,
 "supplyCount": 0,
 "supplyGetCount": 0,
 "starCount": 0,
 "starGetCount": 0,
 "countEnemies": 0,
 "countAllEnemies": 0,
 "spawnCount": 0,
 "isTransforming": false,
 "isLockChange": false,
 "lockItemSuper": false,
 "startDropCard": false,
 "isUsingSkill": true,
 "listActiveEnemies": "[0]",
 "enemyLayer.m_Mask": 512,
 "_gameobject": "GP_Manager"
}
```

## `DataShopPack` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 261,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 671088640,
 "m_Name": "",
 "allSpriteRewards": "[27]",
 "allSpriteRewards[0].m_FileID": 3,
 "allSpriteRewards[0].m_PathID": 2328,
 "allSpriteRewards[1].m_FileID": 3,
 "allSpriteRewards[1].m_PathID": 2765,
 "allSpriteRewards[2].m_FileID": 3,
 "allSpriteRewards[2].m_PathID": 3476,
 "allSpriteRewards[3].m_FileID": 3,
 "allSpriteRewards[3].m_PathID": 2511,
 "allSpriteRewards[4].m_FileID": 3,
 "allSpriteRewards[4].m_PathID": 2358,
 "allRankSprites": "[7]",
 "allRankSprites[0].m_FileID": 3,
 "allRankSprites[0].m_PathID": 3061,
 "allRankSprites[1].m_FileID": 3,
 "allRankSprites[1].m_PathID": 2616,
 "allRankSprites[2].m_FileID": 3,
 "allRankSprites[2].m_PathID": 3508,
 "allRankSprites[3].m_FileID": 3,
 "allRankSprites[3].m_PathID": 2446,
 "allRankSprites[4].m_FileID": 3,
 "allRankSprites[4].m_PathID": 2999,
 "listSpriteDrones": "[12]",
 "listSpriteDrones[0].m_FileID": 3,
 "listSpriteDrones[0].m_PathID": 3657,
 "listSpriteDrones[1].m_FileID": 3,
 "listSpriteDrones[1].m_PathID": 3866,
 "listSpriteDrones[2].m_FileID": 3,
 "listSpriteDrones[2].m_PathID": 2445,
 "listSpriteDrones[3].m_FileID": 3,
 "listSpriteDrones[3].m_PathID": 3091,
 "listSpriteDrones[4].m_FileID": 3,
 "listSpriteDrones[4].m_PathID": 2614,
 "listSpritePlayers": "[24]",
 "listSpritePlayers[0].m_FileID": 3,
 "listSpritePlayers[0].m_PathID": 3581,
 "listSpritePlayers[1].m_FileID": 3,
 "listSpritePlayers[1].m_PathID": 3224,
 "listSpritePlayers[2].m_FileID": 3,
 "listSpritePlayers[2].m_PathID": 3527,
 "listSpritePlayers[3].m_FileID": 3,
 "listSpritePlayers[3].m_PathID": 3025,
 "listSpritePlayers[4].m_FileID": 3,
 "listSpritePlayers[4].m_PathID": 3285,
 "listAvatars": "[24]",
 "listAvatars[0].m_FileID": 3,
 "listAvatars[0].m_PathID": 2985,
 "listAvatars[1].m_FileID": 3,
 "listAvatars[1].m_PathID": 2477,
 "listAvatars[2].m_FileID": 3,
 "listAvatars[2].m_PathID": 2840,
 "listAvatars[3].m_FileID": 3,
 "listAvatars[3].m_PathID": 3145,
 "listAvatars[4].m_FileID": 3,
 "listAvatars[4].m_PathID": 2566,
 "cardPlayerRandomSprite.m_FileID": 3,
 "cardPlayerRandomSprite.m_PathID": 3554,
 "cardDroneRandomSprite.m_FileID": 3,
 "cardDroneRandomSprite.m_PathID": 3667,
 "itemRandomSprite.m_FileID": 3,
 "itemRandomSprite.m_PathID": 3927,
 "_gameobject": "DataShop"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 93891,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 671088640,
 "m_Name": "",
 "allSpriteRewards": "[27]",
 "allSpriteRewards[0].m_FileID": 0,
 "allSpriteRewards[0].m_PathID": 2328,
 "allSpriteRewards[1].m_FileID": 0,
 "allSpriteRewards[1].m_PathID": 2765,
 "allSpriteRewards[2].m_FileID": 0,
 "allSpriteRewards[2].m_PathID": 3476,
 "allSpriteRewards[3].m_FileID": 0,
 "allSpriteRewards[3].m_PathID": 2511,
 "allSpriteRewards[4].m_FileID": 0,
 "allSpriteRewards[4].m_PathID": 2358,
 "allRankSprites": "[7]",
 "allRankSprites[0].m_FileID": 0,
 "allRankSprites[0].m_PathID": 3061,
 "allRankSprites[1].m_FileID": 0,
 "allRankSprites[1].m_PathID": 2616,
 "allRankSprites[2].m_FileID": 0,
 "allRankSprites[2].m_PathID": 3508,
 "allRankSprites[3].m_FileID": 0,
 "allRankSprites[3].m_PathID": 2446,
 "allRankSprites[4].m_FileID": 0,
 "allRankSprites[4].m_PathID": 2999,
 "listSpriteDrones": "[12]",
 "listSpriteDrones[0].m_FileID": 0,
 "listSpriteDrones[0].m_PathID": 3657,
 "listSpriteDrones[1].m_FileID": 0,
 "listSpriteDrones[1].m_PathID": 3866,
 "listSpriteDrones[2].m_FileID": 0,
 "listSpriteDrones[2].m_PathID": 2445,
 "listSpriteDrones[3].m_FileID": 0,
 "listSpriteDrones[3].m_PathID": 3091,
 "listSpriteDrones[4].m_FileID": 0,
 "listSpriteDrones[4].m_PathID": 2614,
 "listSpritePlayers": "[24]",
 "listSpritePlayers[0].m_FileID": 0,
 "listSpritePlayers[0].m_PathID": 3581,
 "listSpritePlayers[1].m_FileID": 0,
 "listSpritePlayers[1].m_PathID": 3224,
 "listSpritePlayers[2].m_FileID": 0,
 "listSpritePlayers[2].m_PathID": 3527,
 "listSpritePlayers[3].m_FileID": 0,
 "listSpritePlayers[3].m_PathID": 3025,
 "listSpritePlayers[4].m_FileID": 0,
 "listSpritePlayers[4].m_PathID": 3285,
 "listAvatars": "[24]",
 "listAvatars[0].m_FileID": 0,
 "listAvatars[0].m_PathID": 2985,
 "listAvatars[1].m_FileID": 0,
 "listAvatars[1].m_PathID": 2477,
 "listAvatars[2].m_FileID": 0,
 "listAvatars[2].m_PathID": 2840,
 "listAvatars[3].m_FileID": 0,
 "listAvatars[3].m_PathID": 3145,
 "listAvatars[4].m_FileID": 0,
 "listAvatars[4].m_PathID": 2566,
 "cardPlayerRandomSprite.m_FileID": 0,
 "cardPlayerRandomSprite.m_PathID": 3554,
 "cardDroneRandomSprite.m_FileID": 0,
 "cardDroneRandomSprite.m_PathID": 3667,
 "itemRandomSprite.m_FileID": 0,
 "itemRandomSprite.m_PathID": 3927,
 "_gameobject": "DataShop"
}
```

## `SkeletonDataAsset` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 33772535808,
 "m_Name": "skeleton_SkeletonData",
 "atlasAssets": "[1]",
 "atlasAssets[0].m_FileID": 0,
 "atlasAssets[0].m_PathID": 580610,
 "scale": 0.009999999776482582,
 "skeletonJSON.m_FileID": 0,
 "skeletonJSON.m_PathID": 918,
 "isUpgradingBlendModeMaterials": false,
 "blendModeMaterials.requiresBlendModeMaterials": false,
 "blendModeMaterials.applyAdditiveMaterial": false,
 "blendModeMaterials.additiveMaterials": "[0]",
 "blendModeMaterials.multiplyMaterials": "[0]",
 "blendModeMaterials.screenMaterials": "[0]",
 "skeletonDataModifiers": "[0]",
 "fromAnimation": "[1]",
 "fromAnimation[0]": "Attack1",
 "toAnimation": "[1]",
 "toAnimation[0]": "Baydi",
 "duration": "[1]",
 "duration[0]": 0.10000000149011612,
 "defaultMix": 0.20000000298023224,
 "controller.m_FileID": 0,
 "controller.m_PathID": 0
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 33772535808,
 "m_Name": "skeleton_SkeletonData",
 "atlasAssets": "[1]",
 "atlasAssets[0].m_FileID": 0,
 "atlasAssets[0].m_PathID": 580612,
 "scale": 0.009999999776482582,
 "skeletonJSON.m_FileID": 0,
 "skeletonJSON.m_PathID": 895,
 "isUpgradingBlendModeMaterials": false,
 "blendModeMaterials.requiresBlendModeMaterials": false,
 "blendModeMaterials.applyAdditiveMaterial": false,
 "blendModeMaterials.additiveMaterials": "[0]",
 "blendModeMaterials.multiplyMaterials": "[0]",
 "blendModeMaterials.screenMaterials": "[0]",
 "skeletonDataModifiers": "[0]",
 "fromAnimation": "[0]",
 "toAnimation": "[0]",
 "duration": "[0]",
 "defaultMix": 0.20000000298023224,
 "controller.m_FileID": 0,
 "controller.m_PathID": 0
}
```

## `TMP_ColorGradient` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 12264144896,
 "m_Name": "New TMP Color Gradient",
 "colorMode": 2,
 "topLeft.r": 1.0,
 "topLeft.g": 0.9980634450912476,
 "topLeft.b": 0.7688679099082947,
 "topLeft.a": 1.0,
 "topRight.r": 1.0,
 "topRight.g": 0.9980634450912476,
 "topRight.b": 0.7688679099082947,
 "topRight.a": 1.0,
 "bottomLeft.r": 1.0,
 "bottomLeft.g": 0.5886716246604919,
 "bottomLeft.b": 0.0,
 "bottomLeft.a": 1.0,
 "bottomRight.r": 1.0,
 "bottomRight.g": 0.5886716246604919,
 "bottomRight.b": 0.0,
 "bottomRight.a": 1.0
}
```

## `SoundClip` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31373393920,
 "m_Name": "Bgm_Boss1",
 "soundClip.m_FileID": 0,
 "soundClip.m_PathID": 1735
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31373393920,
 "m_Name": "Bgm_Boss2",
 "soundClip.m_FileID": 0,
 "soundClip.m_PathID": 1735
}
```

## `Data_Players` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 16525557760,
 "m_Name": "Data_Drones",
 "allPlayers": "[13]",
 "allPlayers[0].id": 20001,
 "allPlayers[0].Sprite.m_FileID": 0,
 "allPlayers[0].Sprite.m_PathID": 3657,
 "allPlayers[0].Star": 1.0,
 "allPlayers[0].Actived": true,
 "allPlayers[1].id": 20002,
 "allPlayers[1].Sprite.m_FileID": 0,
 "allPlayers[1].Sprite.m_PathID": 3866,
 "allPlayers[1].Star": 1.5,
 "allPlayers[1].Actived": true,
 "allPlayers[2].id": 20003,
 "allPlayers[2].Sprite.m_FileID": 0,
 "allPlayers[2].Sprite.m_PathID": 2445,
 "allPlayers[2].Star": 2.5,
 "allPlayers[2].Actived": true,
 "allPlayers[3].id": 20004,
 "allPlayers[3].Sprite.m_FileID": 0,
 "allPlayers[3].Sprite.m_PathID": 3091,
 "allPlayers[3].Star": 3.0,
 "allPlayers[3].Actived": true,
 "allPlayers[4].id": 20005,
 "allPlayers[4].Sprite.m_FileID": 0,
 "allPlayers[4].Sprite.m_PathID": 2614,
 "allPlayers[4].Star": 3.5,
 "allPlayers[4].Actived": true
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 16525557760,
 "m_Name": "Data_Players",
 "allPlayers": "[25]",
 "allPlayers[0].id": 10001,
 "allPlayers[0].Sprite.m_FileID": 0,
 "allPlayers[0].Sprite.m_PathID": 3581,
 "allPlayers[0].Star": 2.0,
 "allPlayers[0].Actived": true,
 "allPlayers[1].id": 10002,
 "allPlayers[1].Sprite.m_FileID": 0,
 "allPlayers[1].Sprite.m_PathID": 3224,
 "allPlayers[1].Star": 2.5,
 "allPlayers[1].Actived": true,
 "allPlayers[2].id": 10003,
 "allPlayers[2].Sprite.m_FileID": 0,
 "allPlayers[2].Sprite.m_PathID": 3527,
 "allPlayers[2].Star": 2.509999990463257,
 "allPlayers[2].Actived": true,
 "allPlayers[3].id": 10004,
 "allPlayers[3].Sprite.m_FileID": 0,
 "allPlayers[3].Sprite.m_PathID": 3025,
 "allPlayers[3].Star": 3.5,
 "allPlayers[3].Actived": true,
 "allPlayers[4].id": 10005,
 "allPlayers[4].Sprite.m_FileID": 0,
 "allPlayers[4].Sprite.m_PathID": 3285,
 "allPlayers[4].Star": 5.050000190734863,
 "allPlayers[4].Actived": true
}
```

## `Data_Items` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 7801405440,
 "m_Name": "Data_Items",
 "allDropItems": "[6]",
 "allDropItems[0].index": 1,
 "allDropItems[0].iconSprite.m_FileID": 0,
 "allDropItems[0].iconSprite.m_PathID": 2376,
 "allDropItems[0].allStatSprites": "[5]",
 "allDropItems[1].index": 2,
 "allDropItems[1].iconSprite.m_FileID": 0,
 "allDropItems[1].iconSprite.m_PathID": 3944,
 "allDropItems[1].allStatSprites": "[5]",
 "allDropItems[2].index": 3,
 "allDropItems[2].iconSprite.m_FileID": 0,
 "allDropItems[2].iconSprite.m_PathID": 3427,
 "allDropItems[2].allStatSprites": "[5]",
 "allDropItems[3].index": 101,
 "allDropItems[3].iconSprite.m_FileID": 0,
 "allDropItems[3].iconSprite.m_PathID": 3442,
 "allDropItems[3].allStatSprites": "[5]",
 "allDropItems[4].index": 102,
 "allDropItems[4].iconSprite.m_FileID": 0,
 "allDropItems[4].iconSprite.m_PathID": 2920,
 "allDropItems[4].allStatSprites": "[5]"
}
```

## `Data_Boss` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 5536481280,
 "m_Name": "BossSprites",
 "allBosses": "[46]",
 "allBosses[0].idWave": 7001,
 "allBosses[0].Sprite.m_FileID": 0,
 "allBosses[0].Sprite.m_PathID": 3869,
 "allBosses[1].idWave": 7002,
 "allBosses[1].Sprite.m_FileID": 0,
 "allBosses[1].Sprite.m_PathID": 2341,
 "allBosses[2].idWave": 7003,
 "allBosses[2].Sprite.m_FileID": 0,
 "allBosses[2].Sprite.m_PathID": 3323,
 "allBosses[3].idWave": 7004,
 "allBosses[3].Sprite.m_FileID": 0,
 "allBosses[3].Sprite.m_PathID": 2994,
 "allBosses[4].idWave": 7005,
 "allBosses[4].Sprite.m_FileID": 0,
 "allBosses[4].Sprite.m_PathID": 3928
}
```

## `Tech_Ability_Data` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 25165824000,
 "m_Name": "TechAbility1",
 "listDatas": "[10]",
 "listDatas[0].Sprite.m_FileID": 0,
 "listDatas[0].Sprite.m_PathID": 3893,
 "listDatas[0].Level": 1,
 "listDatas[0].TypeIndex": 2,
 "listDatas[1].Sprite.m_FileID": 0,
 "listDatas[1].Sprite.m_PathID": 2700,
 "listDatas[1].Level": 2,
 "listDatas[1].TypeIndex": 1,
 "listDatas[2].Sprite.m_FileID": 0,
 "listDatas[2].Sprite.m_PathID": 2700,
 "listDatas[2].Level": 3,
 "listDatas[2].TypeIndex": 1,
 "listDatas[3].Sprite.m_FileID": 0,
 "listDatas[3].Sprite.m_PathID": 3893,
 "listDatas[3].Level": 2,
 "listDatas[3].TypeIndex": 2,
 "listDatas[4].Sprite.m_FileID": 0,
 "listDatas[4].Sprite.m_PathID": 2700,
 "listDatas[4].Level": 4,
 "listDatas[4].TypeIndex": 1
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 25165824000,
 "m_Name": "TechAbility2",
 "listDatas": "[10]",
 "listDatas[0].Sprite.m_FileID": 0,
 "listDatas[0].Sprite.m_PathID": 2543,
 "listDatas[0].Level": 1,
 "listDatas[0].TypeIndex": 0,
 "listDatas[1].Sprite.m_FileID": 0,
 "listDatas[1].Sprite.m_PathID": 2543,
 "listDatas[1].Level": 2,
 "listDatas[1].TypeIndex": 0,
 "listDatas[2].Sprite.m_FileID": 0,
 "listDatas[2].Sprite.m_PathID": 2463,
 "listDatas[2].Level": 1,
 "listDatas[2].TypeIndex": 0,
 "listDatas[3].Sprite.m_FileID": 0,
 "listDatas[3].Sprite.m_PathID": 2543,
 "listDatas[3].Level": 3,
 "listDatas[3].TypeIndex": 0,
 "listDatas[4].Sprite.m_FileID": 0,
 "listDatas[4].Sprite.m_PathID": 2463,
 "listDatas[4].Level": 2,
 "listDatas[4].TypeIndex": 0
}
```

## `LanguageAssets` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 24746393600,
 "m_Name": "Language Assets Arabic",
 "listKey": "[1426]",
 "listKey[0]": "Local",
 "listKey[1]": "Menu",
 "listKey[2]": "txt_menu_version",
 "listKey[3]": "txt_menu_taptostart",
 "listKey[4]": "Home",
 "listValue": "[1426]",
 "listValue[0]": "\u0639\u0631\u0628\u0649",
 "listValue[1]": "Menu",
 "listValue[2]": "\u0627\u0644\u0625\u0635\u062f\u0627\u0631",
 "listValue[3]": "\u0627\u0644\u0645\u0633 \u0644\u0644\u0628\u062f\u0621",
 "listValue[4]": "Home"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 24746393600,
 "m_Name": "Language Assets ChineseSimplified",
 "listKey": "[1426]",
 "listKey[0]": "Local",
 "listKey[1]": "Menu",
 "listKey[2]": "txt_menu_version",
 "listKey[3]": "txt_menu_taptostart",
 "listKey[4]": "Home",
 "listValue": "[1426]",
 "listValue[0]": "\u7b80\u4f53\u4e2d\u6587",
 "listValue[1]": "Menu",
 "listValue[2]": "\u7248",
 "listValue[3]": "\u89e6\u6478\u5373\u53ef\u5f00\u59cb",
 "listValue[4]": "Home"
}
```

## `TMP_StyleSheet` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 24410849280,
 "m_Name": "Default Style Sheet",
 "m_StyleList": "[10]",
 "m_StyleList[0].m_Name": "H1",
 "m_StyleList[0].m_HashCode": 2425,
 "m_StyleList[0].m_OpeningDefinition": "<size=2em><b><#40ff80>*",
 "m_StyleList[0].m_ClosingDefinition": "*</size></b></color>",
 "m_StyleList[0].m_OpeningTagArray": "[23]",
 "m_StyleList[0].m_OpeningTagArray[0]": 60,
 "m_StyleList[0].m_OpeningTagArray[1]": 115,
 "m_StyleList[0].m_OpeningTagArray[2]": 105,
 "m_StyleList[0].m_OpeningTagArray[3]": 122,
 "m_StyleList[0].m_OpeningTagArray[4]": 101,
 "m_StyleList[0].m_ClosingTagArray": "[20]",
 "m_StyleList[0].m_ClosingTagArray[0]": 42,
 "m_StyleList[0].m_ClosingTagArray[1]": 60,
 "m_StyleList[0].m_ClosingTagArray[2]": 47,
 "m_StyleList[0].m_ClosingTagArray[3]": 115,
 "m_StyleList[0].m_ClosingTagArray[4]": 105,
 "m_StyleList[0].m_OpeningTagUnicodeArray": "[23]",
 "m_StyleList[0].m_OpeningTagUnicodeArray[0]": 60,
 "m_StyleList[0].m_OpeningTagUnicodeArray[1]": 115,
 "m_StyleList[0].m_OpeningTagUnicodeArray[2]": 105,
 "m_StyleList[0].m_OpeningTagUnicodeArray[3]": 122,
 "m_StyleList[0].m_OpeningTagUnicodeArray[4]": 101,
 "m_StyleList[0].m_ClosingTagUnicodeArray": "[20]",
 "m_StyleList[0].m_ClosingTagUnicodeArray[0]": 42,
 "m_StyleList[0].m_ClosingTagUnicodeArray[1]": 60,
 "m_StyleList[0].m_ClosingTagUnicodeArray[2]": 47,
 "m_StyleList[0].m_ClosingTagUnicodeArray[3]": 115,
 "m_StyleList[0].m_ClosingTagUnicodeArray[4]": 105,
 "m_StyleList[1].m_Name": "Quote",
 "m_StyleList[1].m_HashCode": 93368250,
 "m_StyleList[1].m_OpeningDefinition": "<i><size=75%><margin=10%>",
 "m_StyleList[1].m_ClosingDefinition": "</i></size></width></margin>",
 "m_StyleList[1].m_OpeningTagArray": "[25]",
 "m_StyleList[1].m_OpeningTagArray[0]": 60,
 "m_StyleList[1].m_OpeningTagArray[1]": 105,
 "m_StyleList[1].m_OpeningTagArray[2]": 62,
 "m_StyleList[1].m_OpeningTagArray[3]": 60,
 "m_StyleList[1].m_OpeningTagArray[4]": 115,
 "m_StyleList[1].m_ClosingTagArray": "[28]",
 "m_StyleList[1].m_ClosingTagArray[0]": 60,
 "m_StyleList[1].m_ClosingTagArray[1]": 47,
 "m_StyleList[1].m_ClosingTagArray[2]": 105,
 "m_StyleList[1].m_ClosingTagArray[3]": 62,
 "m_StyleList[1].m_ClosingTagArray[4]": 60,
 "m_StyleList[1].m_OpeningTagUnicodeArray": "[25]",
 "m_StyleList[1].m_OpeningTagUnicodeArray[0]": 60,
 "m_StyleList[1].m_OpeningTagUnicodeArray[1]": 105,
 "m_StyleList[1].m_OpeningTagUnicodeArray[2]": 62,
 "m_StyleList[1].m_OpeningTagUnicodeArray[3]": 60,
 "m_StyleList[1].m_OpeningTagUnicodeArray[4]": 115,
 "m_StyleList[1].m_ClosingTagUnicodeArray": "[28]",
 "m_StyleList[1].m_ClosingTagUnicodeArray[0]": 60,
 "m_StyleList[1].m_ClosingTagUnicodeArray[1]": 47,
 "m_StyleList[1].m_ClosingTagUnicodeArray[2]": 105,
 "m_StyleList[1].m_ClosingTagUnicodeArray[3]": 62,
 "m_StyleList[1].m_ClosingTagUnicodeArray[4]": 60,
 "m_StyleList[2].m_Name": "Link",
 "m_StyleList[2].m_HashCode": 2656128,
 "m_StyleList[2].m_OpeningDefinition": "<u><#40a0ff><link=\"ID_01\">",
 "m_StyleList[2].m_ClosingDefinition": "</u></color></link>",
 "m_StyleList[2].m_OpeningTagArray": "[26]",
 "m_StyleList[2].m_OpeningTagArray[0]": 60,
 "m_StyleList[2].m_OpeningTagArray[1]": 117,
 "m_StyleList[2].m_OpeningTagArray[2]": 62,
 "m_StyleList[2].m_OpeningTagArray[3]": 60,
 "m_StyleList[2].m_OpeningTagArray[4]": 35,
 "m_StyleList[2].m_ClosingTagArray": "[19]",
 "m_StyleList[2].m_ClosingTagArray[0]": 60,
 "m_StyleList[2].m_ClosingTagArray[1]": 47,
 "m_StyleList[2].m_ClosingTagArray[2]": 117,
 "m_StyleList[2].m_ClosingTagArray[3]": 62,
 "m_StyleList[2].m_ClosingTagArray[4]": 60,
 "m_StyleList[2].m_OpeningTagUnicodeArray": "[26]",
 "m_StyleList[2].m_OpeningTagUnicodeArray[0]": 60,
 "m_StyleList[2].m_OpeningTagUnicodeArray[1]": 117,
 "m_StyleList[2].m_OpeningTagUnicodeArray[2]": 62,
 "m_StyleList[2].m_OpeningTagUnicodeArray[3]": 60,
 "m_StyleList[2].m_OpeningTagUnicodeArray[4]": 35,
 "m_StyleList[2].m_ClosingTagUnicod
```

## `TMP_Settings` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 5284823040,
 "m_Name": "TMP Settings",
 "m_enableWordWrapping": true,
 "m_enableKerning": true,
 "m_enableExtraPadding": false,
 "m_enableTintAllSprites": false,
 "m_enableParseEscapeCharacters": true,
 "m_EnableRaycastTarget": true,
 "m_GetFontFeaturesAtRuntime": true,
 "m_missingGlyphCharacter": 0,
 "m_warningsDisabled": true,
 "m_defaultFontAsset.m_FileID": 4,
 "m_defaultFontAsset.m_PathID": 105,
 "m_defaultFontAssetPath": "Fonts & Materials/",
 "m_defaultFontSize": 6.0,
 "m_defaultAutoSizeMinRatio": 0.5,
 "m_defaultAutoSizeMaxRatio": 2.0,
 "m_defaultTextMeshProTextContainerSize.x": 2.0,
 "m_defaultTextMeshProTextContainerSize.y": 0.5,
 "m_defaultTextMeshProUITextContainerSize.x": 200.0,
 "m_defaultTextMeshProUITextContainerSize.y": 50.0,
 "m_autoSizeTextContainer": false,
 "m_IsTextObjectScaleStatic": false,
 "m_fallbackFontAssets": "[1]",
 "m_fallbackFontAssets[0].m_FileID": 0,
 "m_fallbackFontAssets[0].m_PathID": 0,
 "m_matchMaterialPreset": true,
 "m_defaultSpriteAsset.m_FileID": 0,
 "m_defaultSpriteAsset.m_PathID": 580787,
 "m_defaultSpriteAssetPath": "Sprite Assets/",
 "m_enableEmojiSupport": true,
 "m_MissingCharacterSpriteUnicode": 0,
 "m_defaultColorGradientPresetsPath": "Color Gradient Presets/",
 "m_defaultStyleSheet.m_FileID": 0,
 "m_defaultStyleSheet.m_PathID": 580788,
 "m_StyleSheetsResourcePath": "",
 "m_leadingCharacters.m_FileID": 0,
 "m_leadingCharacters.m_PathID": 924,
 "m_followingCharacters.m_FileID": 0,
 "m_followingCharacters.m_PathID": 933,
 "m_UseModernHangulLineBreakingRules": false
}
```

## `IAPProduct` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 0,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 17548967936,
 "m_Name": "IAPProduct",
 "EnableTestMode": false,
 "NonConsumableProducts": "[99]",
 "NonConsumableProducts[0]": "windwings.pro.forever",
 "NonConsumableProducts[1]": "windwings.timereward.forever",
 "NonConsumableProducts[2]": "windwings.droneunlock8",
 "NonConsumableProducts[3]": "windwings.playerunlock1",
 "NonConsumableProducts[4]": "windwings.playerunlock.s1",
 "ConsumableProducts": "[71]",
 "ConsumableProducts[0]": "windwings.gems0",
 "ConsumableProducts[1]": "windwings.gems2",
 "ConsumableProducts[2]": "windwings.gems3",
 "ConsumableProducts[3]": "windwings.gems4",
 "ConsumableProducts[4]": "windwings.gems5"
}
```

## `Enemy_Datas` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31054626816,
 "m_Name": "",
 "StartHealthPoint": 1100000.0,
 "StartHpPoint": 0.0,
 "CurrentHealthPoint": 0.0,
 "IsAlive": false,
 "IsInvisible": false,
 "IsBringItems": false,
 "IsCaAttack": true,
 "_gameobject": "Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31054626816,
 "m_Name": "",
 "StartHealthPoint": 650000.0,
 "StartHpPoint": 0.0,
 "CurrentHealthPoint": 0.0,
 "IsAlive": false,
 "IsInvisible": false,
 "IsBringItems": false,
 "IsCaAttack": true,
 "_gameobject": "Gun4"
}
```

## `RankManager` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 158489,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31239176192,
 "m_Name": "",
 "loadingObject.m_FileID": 0,
 "loadingObject.m_PathID": 229192,
 "popupNoInternet.m_FileID": 0,
 "popupNoInternet.m_PathID": 674905,
 "popupUploadFailed.m_FileID": 0,
 "popupUploadFailed.m_PathID": 0,
 "btnExitCover.m_FileID": 0,
 "btnExitCover.m_PathID": 0,
 "_gameobject": "Board_Ranks"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 113205,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 31239176192,
 "m_Name": "",
 "loadingObject.m_FileID": 0,
 "loadingObject.m_PathID": 236733,
 "popupNoInternet.m_FileID": 0,
 "popupNoInternet.m_PathID": 619965,
 "popupUploadFailed.m_FileID": 0,
 "popupUploadFailed.m_PathID": 656840,
 "btnExitCover.m_FileID": 0,
 "btnExitCover.m_PathID": 110977,
 "_gameobject": "BOARD_ENDGAME"
}
```

## `ArenaManager` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 143959,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 8019509248,
 "m_Name": "",
 "_gameobject": "Board_Arena"
}
```
