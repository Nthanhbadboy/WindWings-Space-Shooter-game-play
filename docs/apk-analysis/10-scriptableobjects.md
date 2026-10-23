# ScriptableObject / MonoBehaviour data (IL2CPP typetrees)

- source: `/tmp/apk/extract`
- Unity: `2022.3.62f3`
- typetree backend: **AssetStudio**

| class | instances | dumped |
|---|---:|---:|
| `Path_Spawner` | 1688 | 1500 |
| `Call_Data` | 23757 | 1500 |
| `PinMap_Spawner` | 3165 | 1500 |
| `PathCreator` | 1714 | 1500 |
| `PointToPoint_Spawner` | 13292 | 1500 |
| `Rocket_Spawner` | 2019 | 1500 |
| `Spawner` | 1370 | 1370 |
| `Waypoints_Spawner` | 1151 | 1151 |
| `Box_Rewards` | 1065 | 1065 |
| `Enemy_Sub` | 981 | 981 |
| `Enemy_Controller` | 981 | 981 |
| `Enemy_Movement` | 981 | 981 |
| `Enemy_Health` | 981 | 981 |
| `Enemy_Datas` | 981 | 981 |
| `Enemy_Appear` | 914 | 914 |
| `AirFree_Spawner` | 885 | 885 |
| `MeteoriteGenerator` | 852 | 852 |
| `Item_Movement` | 702 | 702 |
| `Sub_Item` | 702 | 702 |
| `Wave` | 686 | 686 |
| `Gun_Attack` | 458 | 458 |
| `MapController` | 396 | 396 |
| `Shop_Cell` | 315 | 315 |
| `Stage_Behaviour` | 299 | 299 |
| `Boss_BodyPhysics` | 251 | 251 |
| `Bullet_Linearly` | 186 | 186 |
| `Boss4_ExplosionTimer` | 155 | 155 |
| `GridLayoutManager` | 133 | 133 |
| `Player19Laser` | 120 | 120 |
| `SoundClip` | 92 | 92 |
| `SkeletonDataAsset` | 27 | 27 |
| `LanguageAssets` | 19 | 19 |
| `Tech_Ability_Data` | 6 | 6 |
| `RankManager` | 3 | 3 |
| `DataShopPack` | 2 | 2 |
| `Data_Players` | 2 | 2 |
| `Bullet_SineWave` | 2 | 2 |
| `GP_Datas` | 1 | 1 |
| `TMP_ColorGradient` | 1 | 1 |
| `Data_Items` | 1 | 1 |
| `Data_Boss` | 1 | 1 |
| `TMP_StyleSheet` | 1 | 1 |
| `TMP_Settings` | 1 | 1 |
| `IAPProduct` | 1 | 1 |
| `ArenaManager` | 1 | 1 |

Ghi chú: các class sau bị **cắt bớt** (chỉ đọc mẫu, không dump hết):

- `Call_Data`: còn 22257 object chưa đọc
- `PointToPoint_Spawner`: còn 11792 object chưa đọc
- `PinMap_Spawner`: còn 1665 object chưa đọc
- `Rocket_Spawner`: còn 519 object chưa đọc
- `PathCreator`: còn 214 object chưa đọc
- `Path_Spawner`: còn 188 object chưa đọc

- error `script`: 1

## Raw typetree dump (giữ nguyên)

- thư mục: `/tmp/apk/unity/raw/typetrees` (`<Class>.jsonl.gz`, mỗi dòng 1 object, **không cắt field**)
- đây là dữ liệu thô để đối chiếu lại mọi kết luận sau này

| class | object | bytes (chưa nén) |
|---|---:|---:|
| `Path_Spawner` | 1500 | 393,075 |
| `Call_Data` | 1500 | 1,116,477 |
| `PinMap_Spawner` | 1500 | 389,883 |
| `PathCreator` | 1500 | 3,466,075 |
| `PointToPoint_Spawner` | 1500 | 393,241 |
| `Rocket_Spawner` | 1500 | 472,039 |
| `Spawner` | 1370 | 348,937 |
| `Waypoints_Spawner` | 1151 | 297,065 |
| `Box_Rewards` | 1065 | 631,968 |
| `Enemy_Sub` | 981 | 318,415 |
| `Enemy_Controller` | 981 | 676,935 |
| `Enemy_Movement` | 981 | 509,355 |
| `Enemy_Health` | 981 | 235,793 |
| `Enemy_Datas` | 981 | 374,290 |
| `Enemy_Appear` | 914 | 204,591 |
| `AirFree_Spawner` | 885 | 231,818 |
| `MeteoriteGenerator` | 852 | 425,384 |
| `Item_Movement` | 702 | 185,860 |
| `Sub_Item` | 702 | 239,547 |
| `Wave` | 686 | 216,575 |
| `Gun_Attack` | 458 | 324,330 |
| `MapController` | 396 | 343,597 |
| `Shop_Cell` | 315 | 231,345 |
| `Stage_Behaviour` | 299 | 340,238 |
| `Boss_BodyPhysics` | 251 | 87,965 |
| `Bullet_Linearly` | 186 | 145,907 |
| `Boss4_ExplosionTimer` | 155 | 49,219 |
| `GridLayoutManager` | 133 | 85,447 |
| `Player19Laser` | 120 | 57,931 |
| `SoundClip` | 92 | 22,765 |

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

## `GridLayoutManager` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 152,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 8841592832,
 "m_Name": "",
 "fixedColumnCount": 4,
 "cellSize.x": 2.200000047683716,
 "cellSize.y": 2.200000047683716,
 "spacing.x": 0.0,
 "spacing.y": 0.0,
 "padding.x": 0.0,
 "padding.y": 0.0,
 "padding.z": 0.0,
 "padding.w": 0.0,
 "flexible": false,
 "boxContent.m_FileID": 0,
 "boxContent.m_PathID": 0,
 "fixedBound.m_FileID": 0,
 "fixedBound.m_PathID": 0,
 "maskObject.m_FileID": 0,
 "maskObject.m_PathID": 0,
 "onDone.m_PersistentCalls.m_Calls": "[0]",
 "refresh": false,
 "_gameobject": "All_Abilities/Grid"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 1369,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 8841592832,
 "m_Name": "",
 "fixedColumnCount": 3,
 "cellSize.x": 3.3499999046325684,
 "cellSize.y": 3.75,
 "spacing.x": 0.0,
 "spacing.y": 0.0,
 "padding.x": 0.0,
 "padding.y": 0.0,
 "padding.z": 0.0,
 "padding.w": 0.0,
 "flexible": false,
 "boxContent.m_FileID": 0,
 "boxContent.m_PathID": 0,
 "fixedBound.m_FileID": 0,
 "fixedBound.m_PathID": 0,
 "maskObject.m_FileID": 0,
 "maskObject.m_PathID": 0,
 "onDone.m_PersistentCalls.m_Calls": "[0]",
 "refresh": false,
 "_gameobject": "Board_BeginPlay/Board_Talents/ParentBot/All_Talents"
}
```

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

## `Shop_Cell` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 871,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 28487712768,
 "m_Name": "",
 "iconRenderer.m_FileID": 0,
 "iconRenderer.m_PathID": 6061,
 "textValues.m_FileID": 0,
 "textValues.m_PathID": 6563,
 "textCost.m_FileID": 0,
 "textCost.m_PathID": 6599,
 "textBonus.m_FileID": 0,
 "textBonus.m_PathID": 6584,
 "textStock.m_FileID": 0,
 "textStock.m_PathID": 6483,
 "textPrice.m_FileID": 0,
 "textPrice.m_PathID": 0,
 "textVipPoint.m_FileID": 0,
 "textVipPoint.m_PathID": 6593,
 "textFirstPurchaseValue.m_FileID": 0,
 "textFirstPurchaseValue.m_PathID": 6460,
 "isVideoBox": false,
 "indexCell": 0,
 "fc.m_FileID": 0,
 "fc.m_PathID": 0,
 "_gameobject": "Board_RebornIAP/Parent/Group 1/Special_Packs/Btn_Cell (9)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 2126,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 28487712768,
 "m_Name": "",
 "iconRenderer.m_FileID": 0,
 "iconRenderer.m_PathID": 5507,
 "textValues.m_FileID": 0,
 "textValues.m_PathID": 6565,
 "textCost.m_FileID": 0,
 "textCost.m_PathID": 6602,
 "textBonus.m_FileID": 0,
 "textBonus.m_PathID": 6596,
 "textStock.m_FileID": 0,
 "textStock.m_PathID": 6612,
 "textPrice.m_FileID": 0,
 "textPrice.m_PathID": 0,
 "textVipPoint.m_FileID": 0,
 "textVipPoint.m_PathID": 6562,
 "textFirstPurchaseValue.m_FileID": 0,
 "textFirstPurchaseValue.m_PathID": 6557,
 "isVideoBox": false,
 "indexCell": 0,
 "fc.m_FileID": 0,
 "fc.m_PathID": 0,
 "_gameobject": "Board_BeginPlay/Board_RebornIAP/Parent/Group 1/Special_Packs/Btn_Cell (7)"
}
```

## `Box_Rewards` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 307,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15149826048,
 "m_Name": "",
 "textNumber.m_FileID": 0,
 "textNumber.m_PathID": 2295,
 "borderNumber.m_FileID": 0,
 "borderNumber.m_PathID": 2094,
 "grayRenderers": "[0]",
 "boxRenderer.m_FileID": 0,
 "boxRenderer.m_PathID": 2004,
 "iconRenderer.m_FileID": 0,
 "iconRenderer.m_PathID": 2138,
 "objCards.m_FileID": 0,
 "objCards.m_PathID": 397,
 "textBonus.m_FileID": 0,
 "textBonus.m_PathID": 0,
 "id": 0,
 "number": 0,
 "_gameobject": "EndgameLoader/Pack_Spec (0)/Parent/Parent_Rewards/Box_Gift (1)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 184,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15149826048,
 "m_Name": "",
 "textNumber.m_FileID": 0,
 "textNumber.m_PathID": 2350,
 "borderNumber.m_FileID": 0,
 "borderNumber.m_PathID": 1875,
 "grayRenderers": "[0]",
 "boxRenderer.m_FileID": 0,
 "boxRenderer.m_PathID": 2100,
 "iconRenderer.m_FileID": 0,
 "iconRenderer.m_PathID": 1915,
 "objCards.m_FileID": 0,
 "objCards.m_PathID": 484,
 "textBonus.m_FileID": 0,
 "textBonus.m_PathID": 0,
 "id": 0,
 "number": 0,
 "_gameobject": "Parent_Rewards/Box_Gift (7)"
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

## `Bullet_Linearly` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 6707,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 30299652096,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 584365,
 "igroneRevoke": false,
 "target.m_FileID": 0,
 "target.m_PathID": 0,
 "actived": false,
 "stop": true,
 "throughShield": false,
 "throughAll": false,
 "parentPoints.m_FileID": 0,
 "parentPoints.m_PathID": 242104,
 "checkPoints": "[0]",
 "pointRadius": "[1]",
 "pointRadius[0]": 0.20000000298023224,
 "border.x": -10.0,
 "border.y": 10.0,
 "border.z": -15.0,
 "border.w": 15.0,
 "delayStartTime": 0.0,
 "delay": 0.0,
 "offLinecastMode": false,
 "fixedOnLinecast": false,
 "delayPool": 0.0,
 "bodyOffNow.m_FileID": 0,
 "bodyOffNow.m_PathID": 6462,
 "pointEfx.m_FileID": 0,
 "pointEfx.m_PathID": 243075,
 "idDestroyEfx": 91101,
 "_gameobject": "BLT_80096"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 6539,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 30299652096,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 584197,
 "igroneRevoke": false,
 "target.m_FileID": 0,
 "target.m_PathID": 0,
 "actived": false,
 "stop": true,
 "throughShield": true,
 "throughAll": false,
 "parentPoints.m_FileID": 0,
 "parentPoints.m_PathID": 241938,
 "checkPoints": "[0]",
 "pointRadius": "[1]",
 "pointRadius[0]": 0.15000000596046448,
 "border.x": -10.0,
 "border.y": 10.0,
 "border.z": -15.0,
 "border.w": 15.0,
 "delayStartTime": 0.0,
 "delay": 0.0,
 "offLinecastMode": false,
 "fixedOnLinecast": true,
 "delayPool": 0.0,
 "bodyOffNow.m_FileID": 0,
 "bodyOffNow.m_PathID": 0,
 "pointEfx.m_FileID": 0,
 "pointEfx.m_PathID": 0,
 "idDestroyEfx": 90003,
 "_gameobject": "BLT_80210"
}
```

## `Enemy_Sub` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 32447135744,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 580872,
 "controller.m_FileID": 0,
 "controller.m_PathID": 580873,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 32447135744,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 580925,
 "controller.m_FileID": 0,
 "controller.m_PathID": 580926,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun1/Gun4"
}
```

## `Enemy_Controller` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 20082327552,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 580881,
 "healthScript.m_FileID": 0,
 "healthScript.m_PathID": 580880,
 "appearScript.m_FileID": 0,
 "appearScript.m_PathID": 580879,
 "physicsScript.m_FileID": 0,
 "physicsScript.m_PathID": 580878,
 "movementScript.m_FileID": 0,
 "movementScript.m_PathID": 580877,
 "uiScript.m_FileID": 0,
 "uiScript.m_PathID": 580876,
 "destroyScript.m_FileID": 0,
 "destroyScript.m_PathID": 580875,
 "burnedScript.m_FileID": 0,
 "burnedScript.m_PathID": 580874,
 "stunScript.m_FileID": 0,
 "stunScript.m_PathID": 0,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 20082327552,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 580934,
 "healthScript.m_FileID": 0,
 "healthScript.m_PathID": 580933,
 "appearScript.m_FileID": 0,
 "appearScript.m_PathID": 580932,
 "physicsScript.m_FileID": 0,
 "physicsScript.m_PathID": 580931,
 "movementScript.m_FileID": 0,
 "movementScript.m_PathID": 580930,
 "uiScript.m_FileID": 0,
 "uiScript.m_PathID": 580929,
 "destroyScript.m_FileID": 0,
 "destroyScript.m_PathID": 580928,
 "burnedScript.m_FileID": 0,
 "burnedScript.m_PathID": 580927,
 "stunScript.m_FileID": 0,
 "stunScript.m_PathID": 0,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun1/Gun4"
}
```

## `Enemy_Movement` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 7012876288,
 "m_Name": "",
 "endOfPathInstruction": 2,
 "typeMoveEnded": 0,
 "moveEndedEvent.m_PersistentCalls.m_Calls": "[0]",
 "facingMove": true,
 "isTurret": false,
 "parentRotate.m_FileID": 0,
 "parentRotate.m_PathID": 0,
 "listSpeeds": "[1]",
 "listSpeeds[0]": 5.0,
 "border.x": -10.0,
 "border.y": 10.0,
 "border.z": -15.0,
 "border.w": 15.0,
 "fixedAngle": false,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 7012876288,
 "m_Name": "",
 "endOfPathInstruction": 2,
 "typeMoveEnded": 0,
 "moveEndedEvent.m_PersistentCalls.m_Calls": "[0]",
 "facingMove": true,
 "isTurret": false,
 "parentRotate.m_FileID": 0,
 "parentRotate.m_PathID": 0,
 "listSpeeds": "[1]",
 "listSpeeds[0]": 5.0,
 "border.x": -10.0,
 "border.y": 10.0,
 "border.z": -15.0,
 "border.w": 15.0,
 "fixedAngle": false,
 "_gameobject": "Gun1/Gun4"
}
```

## `Enemy_Appear` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 17716740096,
 "m_Name": "",
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 17716740096,
 "m_Name": "",
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun1/Gun4"
}
```

## `Enemy_Health` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4291,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 7834959872,
 "m_Name": "",
 "noDamage": false,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4341,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 7834959872,
 "m_Name": "",
 "noDamage": false,
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun1/Gun4"
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
 "_gameobject": "Boss-39006/Enemy_Ingame/Body/Than/Gun7/Gun6"
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
 "_gameobject": "Gun1/Gun4"
}
```

## `Path_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4298,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 34879832064,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0002/Path_CB3 (9)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4299,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 34879832064,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0005/Path_CB3 (9)"
}
```

## `Call_Data` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4298,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 6190792704,
 "m_Name": "",
 "editType": 0,
 "spawnType": 1,
 "listIdEnemies": "[0]",
 "listPrefabEnemies": "[8]",
 "listPrefabEnemies[0].m_FileID": 0,
 "listPrefabEnemies[0].m_PathID": 185636,
 "listPrefabEnemies[1].m_FileID": 0,
 "listPrefabEnemies[1].m_PathID": 185636,
 "listPrefabEnemies[2].m_FileID": 0,
 "listPrefabEnemies[2].m_PathID": 185636,
 "listPrefabEnemies[3].m_FileID": 0,
 "listPrefabEnemies[3].m_PathID": 185636,
 "listPrefabEnemies[4].m_FileID": 0,
 "listPrefabEnemies[4].m_PathID": 185636,
 "listBringItems": "[0]",
 "ySpawn": 9.600000381469727,
 "number": 0,
 "rate": 0.5,
 "pathScript.m_FileID": 0,
 "pathScript.m_PathID": 581513,
 "showGizmos": false,
 "color.r": 1.0,
 "color.g": 1.0,
 "color.b": 1.0,
 "color.a": 1.0,
 "radius": 0.10000000149011612,
 "parentPoints.m_FileID": 0,
 "parentPoints.m_PathID": 0,
 "speed": 0.0,
 "angle": 0.0,
 "minValX": 0.0,
 "maxValX": 0.0,
 "yStart": 0.0,
 "_gameobject": "Wave_0002/Path_CB3 (9)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4299,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 6190792704,
 "m_Name": "",
 "editType": 0,
 "spawnType": 1,
 "listIdEnemies": "[0]",
 "listPrefabEnemies": "[12]",
 "listPrefabEnemies[0].m_FileID": 0,
 "listPrefabEnemies[0].m_PathID": 185636,
 "listPrefabEnemies[1].m_FileID": 0,
 "listPrefabEnemies[1].m_PathID": 185636,
 "listPrefabEnemies[2].m_FileID": 0,
 "listPrefabEnemies[2].m_PathID": 185636,
 "listPrefabEnemies[3].m_FileID": 0,
 "listPrefabEnemies[3].m_PathID": 185636,
 "listPrefabEnemies[4].m_FileID": 0,
 "listPrefabEnemies[4].m_PathID": 185636,
 "listBringItems": "[0]",
 "ySpawn": 9.600000381469727,
 "number": 0,
 "rate": 0.5,
 "pathScript.m_FileID": 0,
 "pathScript.m_PathID": 581514,
 "showGizmos": false,
 "color.r": 1.0,
 "color.g": 1.0,
 "color.b": 1.0,
 "color.a": 1.0,
 "radius": 0.10000000149011612,
 "parentPoints.m_FileID": 0,
 "parentPoints.m_PathID": 0,
 "speed": 0.0,
 "angle": 0.0,
 "minValX": 0.0,
 "maxValX": 0.0,
 "yStart": 0.0,
 "_gameobject": "Wave_0005/Path_CB3 (9)"
}
```

## `PinMap_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4322,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 8506048512,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0098/Point 1 (4)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4323,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 8506048512,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0098/Point 1 (4)"
}
```

## `PathCreator` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4423,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 16391340032,
 "m_Name": "",
 "editorData._bezierPath.points": "[10]",
 "editorData._bezierPath.isClosed": false,
 "editorData._bezierPath.localPosition.x": 0.0,
 "editorData._bezierPath.localPosition.y": 0.0,
 "editorData._bezierPath.localPosition.z": 0.0,
 "editorData._bezierPath.space": 1,
 "editorData._bezierPath.controlMode": 0,
 "editorData._bezierPath.autoControlLength": 0.30000001192092896,
 "editorData._bezierPath.boundsUpToDate": true,
 "editorData._bezierPath.pivot.x": 4.939835548400879,
 "editorData._bezierPath.pivot.y": -6.521292209625244,
 "editorData._bezierPath.pivot.z": 0.0,
 "editorData._bezierPath.rotation.x": 0.0,
 "editorData._bezierPath.rotation.y": 0.0,
 "editorData._bezierPath.rotation.z": 0.0,
 "editorData._bezierPath.rotation.w": 1.0,
 "editorData._bezierPath.scale.x": 1.0,
 "editorData._bezierPath.scale.y": 1.0,
 "editorData._bezierPath.scale.z": 1.0,
 "editorData._bezierPath.perAnchorNormalsAngle": "[3]",
 "editorData._bezierPath.perAnchorNormalsAngle[0]": 0.0,
 "editorData._bezierPath.perAnchorNormalsAngle[1]": 0.0,
 "editorData._bezierPath.perAnchorNormalsAngle[2]": 0.0,
 "editorData._bezierPath.globalNormalsAngle": 0.0,
 "editorData._bezierPath.flipNormals": false,
 "editorData.vertexPathUpToDate": true,
 "editorData.vertexPathMaxAngleError": 0.30000001192092896,
 "editorData.vertexPathMinVertexSpacing": 0.009999999776482582,
 "editorData.pathTransformationEnabled": false,
 "editorData.showPathBounds": false,
 "editorData.showPerSegmentBounds": false,
 "editorData.displayAnchorPoints": true,
 "editorData.displayControlPoints": true,
 "editorData.bezierHandleScale": 1.0,
 "editorData.globalDisplaySettingsFoldout": false,
 "editorData.keepConstantHandleSize": true,
 "editorData.vertexHandleSize": 0.20000000298023224,
 "editorData.showNormalsInVertexMode": false,
 "editorData.showDisplayOptions": true,
 "editorData.showPathOptions": true,
 "editorData.showVertexPathDisplayOptions": false,
 "editorData.showVertexPathOptions": true,
 "editorData.showNormals": false,
 "editorData.showNormalsHelpInfo": false,
 "editorData.tabIndex": 0,
 "initialized": true,
 "hideGizmos": false,
 "drawGizmos": true,
 "colorGizmos.r": 0.922553300857544,
 "colorGizmos.g": 1.0,
 "colorGizmos.b": 0.2705882787704468,
 "colorGizmos.a": 1.0,
 "_gameobject": "Wave_0002/Path_CB3 (10)/Path"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4424,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 16391340032,
 "m_Name": "",
 "editorData._bezierPath.points": "[7]",
 "editorData._bezierPath.isClosed": false,
 "editorData._bezierPath.localPosition.x": 0.0,
 "editorData._bezierPath.localPosition.y": 0.0,
 "editorData._bezierPath.localPosition.z": 0.0,
 "editorData._bezierPath.space": 1,
 "editorData._bezierPath.controlMode": 0,
 "editorData._bezierPath.autoControlLength": 0.30000001192092896,
 "editorData._bezierPath.boundsUpToDate": true,
 "editorData._bezierPath.pivot.x": 3.0372378826141357,
 "editorData._bezierPath.pivot.y": -5.957509517669678,
 "editorData._bezierPath.pivot.z": 0.0,
 "editorData._bezierPath.rotation.x": 0.0,
 "editorData._bezierPath.rotation.y": 0.0,
 "editorData._bezierPath.rotation.z": 0.0,
 "editorData._bezierPath.rotation.w": 1.0,
 "editorData._bezierPath.scale.x": 1.0,
 "editorData._bezierPath.scale.y": 1.0,
 "editorData._bezierPath.scale.z": 1.0,
 "editorData._bezierPath.perAnchorNormalsAngle": "[2]",
 "editorData._bezierPath.perAnchorNormalsAngle[0]": 0.0,
 "editorData._bezierPath.perAnchorNormalsAngle[1]": 0.0,
 "editorData._bezierPath.globalNormalsAngle": 0.0,
 "editorData._bezierPath.flipNormals": false,
 "editorData.vertexPathUpToDate": true,
 "editorData.vertexPathMaxAngleError": 0.30000001192092896,
 "editorData.vertexPathMinVertexSpacing": 0.009999999776482582,
 "editorData.pathTransformationEnabled": false,
 "editorData.showPathBounds": false,
 "editorData.showPerSegmentBounds": false,
 "editorData.displayAnchorPoints": true,
 "editorData.displayControlPoints": true,
 "editorData.bezierHandleScale": 1.0,
 "editorData.globalDisplaySettingsFoldout": false,
 "editorData.keepConstantHandleSize": true,
 "editorData.vertexHandleSize": 0.20000000298023224,
 "editorData.showNormalsInVertexMode": false,
 "editorData.showDisplayOptions": true,
 "editorData.showPathOptions": true,
 "editorData.showVertexPathDisplayOptions": false,
 "editorData.showVertexPathOptions": true,
 "editorData.showNormals": false,
 "editorData.showNormalsHelpInfo": false,
 "editorData.tabIndex": 0,
 "initialized": true,
 "hideGizmos": false,
 "drawGizmos": true,
 "colorGizmos.r": 0.922553300857544,
 "colorGizmos.g": 1.0,
 "colorGizmos.b": 0.2705882787704468,
 "colorGizmos.a": 1.0,
 "_gameobject": "Wave_0005/Path_CB3 (10)/Path"
}
```

## `Gun_Attack` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 4454,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 20736638976,
 "m_Name": "",
 "iCanAttackParent.m_FileID": 0,
 "iCanAttackParent.m_PathID": 413073,
 "timeStart": 1.0,
 "gunType": 2,
 "parentBarrels.m_FileID": 0,
 "parentBarrels.m_PathID": 239850,
 "allGunDatas": "[1]",
 "allGunDatas[0].countShots": 0,
 "allGunDatas[0].timeShot": 0.07999999821186066,
 "allGunDatas[0].timeReload": 0.800000011920929,
 "allGunDatas[0].timeRounds": 3.0,
 "allGunDatas[0].countMags": 1,
 "forceType": 0,
 "targetLayer.m_Mask": 256,
 "bltId": 80288,
 "bltSpeed": 6.0,
 "bltLifetime": 8.0,
 "bltDamage": 600.0,
 "bltPinToMap": true,
 "shootAudioClipName": 69,
 "isStunned": false,
 "_gameobject": "CD-31007/GameObject"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 70402,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 20736638976,
 "m_Name": "",
 "iCanAttackParent.m_FileID": 0,
 "iCanAttackParent.m_PathID": 0,
 "timeStart": 0.0,
 "gunType": 0,
 "parentBarrels.m_FileID": 0,
 "parentBarrels.m_PathID": 247540,
 "allGunDatas": "[1]",
 "allGunDatas[0].countShots": 0,
 "allGunDatas[0].timeShot": 0.0,
 "allGunDatas[0].timeReload": 0.0,
 "allGunDatas[0].timeRounds": 10.0,
 "allGunDatas[0].countMags": 1,
 "forceType": 0,
 "targetLayer.m_Mask": 256,
 "bltId": 80078,
 "bltSpeed": 8.0,
 "bltLifetime": 5.0,
 "bltDamage": 500.0,
 "bltPinToMap": false,
 "shootAudioClipName": 0,
 "isStunned": false,
 "_gameobject": "Hand6/Sword/Gun3.1"
}
```

## `Boss_BodyPhysics` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 159270,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 19763560448,
 "m_Name": "",
 "layerMask.m_Mask": 256,
 "dmgPerSec": 100.0,
 "dmgFirst": 1500.0,
 "isTrigger": false,
 "isFirstTrigger": false,
 "_gameobject": "Boss-37018/Enemy_Ingame/Parent/Collider"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 35569,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 19763560448,
 "m_Name": "",
 "layerMask.m_Mask": 256,
 "dmgPerSec": 240.0,
 "dmgFirst": 0.0,
 "isTrigger": true,
 "isFirstTrigger": false,
 "_gameobject": "Boss-39004/Enemy_Ingame/Body/Body1/Tayxoay/TayR/Tayxoay3/Tayxoay2/Tayxoay1/Cucxoay"
}
```

## `Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 148695,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 2600468480,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0150/EndPoint"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 148696,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 2600468480,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0010/EndPoint"
}
```

## `Item_Movement` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 14418,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 1996488704,
 "m_Name": "",
 "isCoin": true,
 "idle": true,
 "_gameobject": "Wave_0000/Coin_Arrow/GameObject (3)/Item-70012 (2)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 15275,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 1996488704,
 "m_Name": "",
 "isCoin": true,
 "idle": true,
 "_gameobject": "Coin_Arrow/GameObject (13)/Item-70012 (1)"
}
```

## `Sub_Item` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 90016,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 1157627904,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 645071,
 "movementScript.m_FileID": 0,
 "movementScript.m_PathID": 627891,
 "_gameobject": "GameObject (7)/Item-70012 (2)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 89446,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 1157627904,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 644899,
 "movementScript.m_FileID": 0,
 "movementScript.m_PathID": 628026,
 "_gameobject": "GameObject (13)/Item-70011 (2)"
}
```

## `MeteoriteGenerator` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 113663,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 26474446848,
 "m_Name": "",
 "minmaxSpdMove.x": 0.699999988079071,
 "minmaxSpdMove.y": 1.0,
 "minmaxSpdRotate.x": -15.0,
 "minmaxSpdRotate.y": 15.0,
 "minmaxZ.x": 0.0,
 "minmaxZ.y": 0.0,
 "minmaxColor.x": 0.0,
 "minmaxColor.y": 0.30000001192092896,
 "minmaxTime.x": 2.0,
 "minmaxTime.y": 1.0,
 "minX": 7.0,
 "maxX": 1.0,
 "minY": 15.0,
 "maxY": 15.0,
 "_gameobject": "Map-0000/Parent_Static/Met (3.2)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 189815,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 26474446848,
 "m_Name": "",
 "minmaxSpdMove.x": 1.7000000476837158,
 "minmaxSpdMove.y": 2.0,
 "minmaxSpdRotate.x": -15.0,
 "minmaxSpdRotate.y": 15.0,
 "minmaxZ.x": 0.0,
 "minmaxZ.y": 0.0,
 "minmaxColor.x": 1.0,
 "minmaxColor.y": 0.800000011920929,
 "minmaxTime.x": 4.0,
 "minmaxTime.y": 5.0,
 "minX": -4.0,
 "maxX": -3.0,
 "minY": 12.0,
 "maxY": 12.0,
 "_gameobject": "Map-0046/Parent_Static/Met (1)"
}
```

## `Waypoints_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 233148,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15888023552,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0069/Group (25)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 233149,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15888023552,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0219/Group (25)"
}
```

## `Stage_Behaviour` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 7895,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 29175578624,
 "m_Name": "",
 "stageType": 0,
 "lineTransform.m_FileID": 0,
 "lineTransform.m_PathID": 243264,
 "parentStars.m_FileID": 0,
 "parentStars.m_PathID": 243260,
 "stageRenderer.m_FileID": 0,
 "stageRenderer.m_PathID": 510106,
 "stageNormalSprites": "[2]",
 "stageNormalSprites[0].m_FileID": 0,
 "stageNormalSprites[0].m_PathID": 3620,
 "stageNormalSprites[1].m_FileID": 0,
 "stageNormalSprites[1].m_PathID": 2847,
 "stageMiniBossSprites": "[2]",
 "stageMiniBossSprites[0].m_FileID": 0,
 "stageMiniBossSprites[0].m_PathID": 2542,
 "stageMiniBossSprites[1].m_FileID": 0,
 "stageMiniBossSprites[1].m_PathID": 2623,
 "stageBossSprites": "[2]",
 "stageBossSprites[0].m_FileID": 0,
 "stageBossSprites[0].m_PathID": 2542,
 "stageBossSprites[1].m_FileID": 0,
 "stageBossSprites[1].m_PathID": 2623,
 "stageCombatSprites": "[2]",
 "stageCombatSprites[0].m_FileID": 0,
 "stageCombatSprites[0].m_PathID": 3181,
 "stageCombatSprites[1].m_FileID": 0,
 "stageCombatSprites[1].m_PathID": 3340,
 "stageSSprites": "[2]",
 "stageSSprites[0].m_FileID": 0,
 "stageSSprites[0].m_PathID": 3409,
 "stageSSprites[1].m_FileID": 0,
 "stageSSprites[1].m_PathID": 2839,
 "stageXSprites": "[2]",
 "stageXSprites[0].m_FileID": 0,
 "stageXSprites[0].m_PathID": 2978,
 "stageXSprites[1].m_FileID": 0,
 "stageXSprites[1].m_PathID": 3420,
 "textStageIndex.m_FileID": 0,
 "textStageIndex.m_PathID": 635779,
 "rootLine.m_FileID": 0,
 "rootLine.m_PathID": 0,
 "refresh": false,
 "bossObj.m_FileID": 0,
 "bossObj.m_PathID": 176880,
 "_gameobject": "Board_Maps/Parent/ScrollView-Chap 1/ObjectMove/Parent_Stages/Stage_Normal (72)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 8869,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 29175578624,
 "m_Name": "",
 "stageType": 0,
 "lineTransform.m_FileID": 0,
 "lineTransform.m_PathID": 244194,
 "parentStars.m_FileID": 0,
 "parentStars.m_PathID": 244200,
 "stageRenderer.m_FileID": 0,
 "stageRenderer.m_PathID": 510341,
 "stageNormalSprites": "[2]",
 "stageNormalSprites[0].m_FileID": 0,
 "stageNormalSprites[0].m_PathID": 3620,
 "stageNormalSprites[1].m_FileID": 0,
 "stageNormalSprites[1].m_PathID": 2847,
 "stageMiniBossSprites": "[2]",
 "stageMiniBossSprites[0].m_FileID": 0,
 "stageMiniBossSprites[0].m_PathID": 2542,
 "stageMiniBossSprites[1].m_FileID": 0,
 "stageMiniBossSprites[1].m_PathID": 2623,
 "stageBossSprites": "[2]",
 "stageBossSprites[0].m_FileID": 0,
 "stageBossSprites[0].m_PathID": 2542,
 "stageBossSprites[1].m_FileID": 0,
 "stageBossSprites[1].m_PathID": 2623,
 "stageCombatSprites": "[2]",
 "stageCombatSprites[0].m_FileID": 0,
 "stageCombatSprites[0].m_PathID": 3181,
 "stageCombatSprites[1].m_FileID": 0,
 "stageCombatSprites[1].m_PathID": 3340,
 "stageSSprites": "[2]",
 "stageSSprites[0].m_FileID": 0,
 "stageSSprites[0].m_PathID": 3409,
 "stageSSprites[1].m_FileID": 0,
 "stageSSprites[1].m_PathID": 2839,
 "stageXSprites": "[2]",
 "stageXSprites[0].m_FileID": 0,
 "stageXSprites[0].m_PathID": 2978,
 "stageXSprites[1].m_FileID": 0,
 "stageXSprites[1].m_PathID": 3420,
 "textStageIndex.m_FileID": 0,
 "textStageIndex.m_PathID": 636176,
 "rootLine.m_FileID": 0,
 "rootLine.m_PathID": 0,
 "refresh": false,
 "bossObj.m_FileID": 0,
 "bossObj.m_PathID": 175830,
 "_gameobject": "Parent/ScrollView-Chap 2/ObjectMove/Parent_Stages/Stage_Normal (221)"
}
```

## `PointToPoint_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 203839,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 10200547328,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0010/CB1 Vua"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 203840,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 10200547328,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0072/CB1 Vua"
}
```

## `Rocket_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 74724,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 14847836160,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "typeRocket": 3,
 "showBoundaryRocketPoints": true,
 "_gameobject": "Wave_0190/6-CB09_Left (21)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 74725,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 14847836160,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "typeRocket": 3,
 "showBoundaryRocketPoints": true,
 "_gameobject": "Wave_0190/6-CB09_Left (21)"
}
```

## `MapController` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 71443,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 26189234176,
 "m_Name": "",
 "allMoveLayers": "[4]",
 "allMoveLayers[0].parentLayer.m_FileID": 0,
 "allMoveLayers[0].parentLayer.m_PathID": 299772,
 "allMoveLayers[0].speed": 0.25,
 "allMoveLayers[1].parentLayer.m_FileID": 0,
 "allMoveLayers[1].parentLayer.m_PathID": 349667,
 "allMoveLayers[1].speed": 1.0,
 "allMoveLayers[2].parentLayer.m_FileID": 0,
 "allMoveLayers[2].parentLayer.m_PathID": 385154,
 "allMoveLayers[2].speed": 0.05000000074505806,
 "allMoveLayers[3].parentLayer.m_FileID": 0,
 "allMoveLayers[3].parentLayer.m_PathID": 276000,
 "allMoveLayers[3].speed": 0.25,
 "enemyParentMove.parentLayer.m_FileID": 0,
 "enemyParentMove.parentLayer.m_PathID": 0,
 "enemyParentMove.speed": 0.0,
 "parentWaves.m_FileID": 0,
 "parentWaves.m_PathID": 349667,
 "parentMaps.m_FileID": 0,
 "parentMaps.m_PathID": 299772,
 "isMoveEnemyLayer": false,
 "IndexWaveArena": 0,
 "IndexWavePvP": 0,
 "worked": true,
 "_gameobject": "Map-0003"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 86259,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 26189234176,
 "m_Name": "",
 "allMoveLayers": "[5]",
 "allMoveLayers[0].parentLayer.m_FileID": 0,
 "allMoveLayers[0].parentLayer.m_PathID": 427220,
 "allMoveLayers[0].speed": 0.20000000298023224,
 "allMoveLayers[1].parentLayer.m_FileID": 0,
 "allMoveLayers[1].parentLayer.m_PathID": 363852,
 "allMoveLayers[1].speed": 1.0,
 "allMoveLayers[2].parentLayer.m_FileID": 0,
 "allMoveLayers[2].parentLayer.m_PathID": 349457,
 "allMoveLayers[2].speed": 0.10000000149011612,
 "allMoveLayers[3].parentLayer.m_FileID": 0,
 "allMoveLayers[3].parentLayer.m_PathID": 437329,
 "allMoveLayers[3].speed": 0.5,
 "allMoveLayers[4].parentLayer.m_FileID": 0,
 "allMoveLayers[4].parentLayer.m_PathID": 392274,
 "allMoveLayers[4].speed": 0.2199999988079071,
 "enemyParentMove.parentLayer.m_FileID": 0,
 "enemyParentMove.parentLayer.m_PathID": 0,
 "enemyParentMove.speed": 0.0,
 "parentWaves.m_FileID": 0,
 "parentWaves.m_PathID": 363852,
 "parentMaps.m_FileID": 0,
 "parentMaps.m_PathID": 427220,
 "isMoveEnemyLayer": false,
 "IndexWaveArena": 0,
 "IndexWavePvP": 0,
 "worked": true,
 "_gameobject": "Map-0043"
}
```

## `Player19Laser` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 53511,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 30047993856,
 "m_Name": "",
 "parentRotate.m_FileID": 0,
 "parentRotate.m_PathID": 292689,
 "line.m_FileID": 0,
 "line.m_PathID": 499581,
 "lightObject.m_FileID": 0,
 "lightObject.m_PathID": 49545,
 "playerAttack.m_FileID": 0,
 "playerAttack.m_PathID": 641750,
 "targetLayer.m_Mask": 512,
 "_gameobject": "AllDrones/Drone (9)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 158211,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 30047993856,
 "m_Name": "",
 "parentRotate.m_FileID": 0,
 "parentRotate.m_PathID": 376709,
 "line.m_FileID": 0,
 "line.m_PathID": 499820,
 "lightObject.m_FileID": 0,
 "lightObject.m_PathID": 165863,
 "playerAttack.m_FileID": 0,
 "playerAttack.m_PathID": 616561,
 "targetLayer.m_Mask": 512,
 "_gameobject": "Parent/Panel_Info/Player_Demo/Player_Types/Player_10019/AllDrones/Drone (10)"
}
```

## `Boss4_ExplosionTimer` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 181391,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15049162752,
 "m_Name": "",
 "idFx": 91003,
 "fixedTime": -1.0,
 "timeMin": 0.25,
 "timeMax": 1.75,
 "_gameobject": "Boss-39010/Enemy_Ingame/Body/FxDie/Fx (19)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 9735,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 15049162752,
 "m_Name": "",
 "idFx": 91003,
 "fixedTime": -1.0,
 "timeMin": 0.5,
 "timeMax": 6.800000190734863,
 "_gameobject": "Board_FightBoss/Parent/Tab (5)/Boss/Parent_Bosses/Boss 6/Boss 6/FxDie/Fx (29)"
}
```

## `AirFree_Spawner` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 203787,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 33520877568,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0231/CheckPlayerNo (21)"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 203788,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 33520877568,
 "m_Name": "",
 "dataScript.m_FileID": 0,
 "dataScript.m_PathID": 0,
 "_gameobject": "Wave_0231/CheckPlayerNo (21)"
}
```

## `Wave` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 214656,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 32799457280,
 "m_Name": "",
 "indexWave": 0,
 "startPoint.m_FileID": 0,
 "startPoint.m_PathID": 288457,
 "endPoint.m_FileID": 0,
 "endPoint.m_PathID": 340237,
 "_gameobject": "Wave_0011"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 214657,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 32799457280,
 "m_Name": "",
 "indexWave": 0,
 "startPoint.m_FileID": 0,
 "startPoint.m_PathID": 288458,
 "endPoint.m_FileID": 0,
 "endPoint.m_PathID": 340238,
 "_gameobject": "Wave_0011"
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
 "_gameobject": "Board_Maps/Board_Ranks"
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

## `Bullet_SineWave` samples

```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 168196,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 3825205248,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 666268,
 "igroneRevoke": false,
 "target.m_FileID": 0,
 "target.m_PathID": 0,
 "height": 1.0,
 "speed": 12.0,
 "igroneShieldCollider": false,
 "fxDestroyIndex": 90003,
 "border.x": -6.0,
 "border.y": 6.0,
 "border.z": -20.0,
 "border.w": 10.0,
 "_gameobject": "BLT_80104"
}
```
```json
{
 "m_GameObject.m_FileID": 0,
 "m_GameObject.m_PathID": 168200,
 "m_Enabled": 1,
 "m_Script.m_FileID": 16777216,
 "m_Script.m_PathID": 3825205248,
 "m_Name": "",
 "m_OPScript.m_FileID": 0,
 "m_OPScript.m_PathID": 666272,
 "igroneRevoke": false,
 "target.m_FileID": 0,
 "target.m_PathID": 0,
 "height": 1.0,
 "speed": 12.0,
 "igroneShieldCollider": false,
 "fxDestroyIndex": 90003,
 "border.x": -6.0,
 "border.y": 6.0,
 "border.z": -20.0,
 "border.w": 10.0,
 "_gameobject": "BLT_80105"
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
