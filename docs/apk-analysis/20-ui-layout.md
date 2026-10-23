# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **733**
- tổng node: **110482**
- dung lượng thô (gz): **2.1 MB**

- bỏ qua: duplicate (class, root) (60)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 95909 |
| `SpriteRenderer` | 52137 |
| `MeshRenderer` | 16161 |
| `RectTransform` | 14573 |
| `TextMeshPro` | 14505 |
| `MeshFilter` | 13122 |
| `BoxCollider2D` | 7593 |
| `Animator` | 5665 |
| `ButtonEvents` | 5264 |
| `Button_Sound` | 5121 |
| `ParticleSystem` | 3945 |
| `ParticleSystemRenderer` | 3945 |
| `LanguageTextMeshPro` | 3762 |
| `ChangeSorting` | 2256 |
| `BgObjectScaler` | 1651 |
| `Popup_Notices` | 1272 |
| `Box_Rewards` | 1238 |
| `TMP_SubMesh` | 1090 |
| `UIObjectAnchors` | 759 |
| `Shop_Cell` | 726 |
| `FixUIShop` | 653 |
| `Rigidbody2D` | 406 |
| `ObjectPool` | 381 |
| `Enemy_Datas` | 327 |
| `Enemy_Health` | 327 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 450 | 341 | 62 |
| `Board_Shop` | 3208 | 504 | 156 | 44 |
| `Board_PVP` | 2864 | 429 | 170 | 42 |
| `Board_SelectBoss` | 2505 | 115 | 17 | 35 |
| `Board_FightBoss` | 2502 | 116 | 41 | 40 |
| `Tab_Boss` | 1980 | 5 | 0 | 31 |
| `Board_Arena` | 1969 | 279 | 122 | 32 |
| `Board_BattlePass` | 1940 | 288 | 71 | 20 |
| `Board_Players` | 1720 | 174 | 75 | 29 |
| `Board_Ranks` | 1500 | 214 | 92 | 23 |
| `Board_Ranks` | 1442 | 208 | 93 | 23 |
| `Board_Survival` | 1426 | 219 | 83 | 23 |
| `Board_TechLab` | 1350 | 155 | 74 | 19 |
| `Board_Survival` | 1272 | 193 | 84 | 21 |
| `Board_Drones` | 1020 | 142 | 62 | 17 |
| `Board_Begin` | 1003 | 146 | 53 | 16 |
| `Board_BattlePassPro` | 982 | 120 | 40 | 14 |
| `Board_WinnerBenefits` | 967 | 146 | 57 | 14 |
| `Board_Combo` | 915 | 100 | 59 | 13 |
| `Board_Endgame` | 911 | 131 | 53 | 16 |
| `Popup_WatchVideos` | 903 | 157 | 49 | 13 |
| `Board_GiftLogin` | 882 | 128 | 28 | 13 |
| `Board_MiniCombo` | 878 | 106 | 51 | 13 |
| `Popup_WatchVideos` | 865 | 146 | 45 | 13 |
| `Board_Reborn` | 834 | 129 | 58 | 15 |
| `Board_Stage` | 780 | 115 | 52 | 12 |
| `Board_Challange` | 761 | 145 | 53 | 12 |
| `Board_Setting` | 711 | 85 | 47 | 11 |
| `Board_Vip` | 691 | 95 | 26 | 10 |
| `Popup_ShipSalePack` | 674 | 17 | 7 | 10 |
| `Board_QuestRewards` | 654 | 97 | 27 | 9 |
| `Board_UserProfile` | 636 | 58 | 49 | 9 |
| `Board_EventSeasonPass` | 596 | 96 | 29 | 10 |
| `Popup_HolidayGift` | 564 | 79 | 11 | 8 |
| `Tab_Boss` | 543 | 9 | 1 | 7 |
| `Board_ShopEnergy` | 536 | 115 | 35 | 9 |
| `Popup_HolidayGift` | 531 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 512 | 67 | 20 | 7 |
| `Popup_WeekSales` | 447 | 59 | 13 | 6 |
| `Popup_WatchVideosOld` | 373 | 59 | 13 | 5 |

## Cấu trúc mỗi node

```json
{"path": "Background/Star_01", "depth": 2, "active": 1,
 "anchor_min": [0,0], "anchor_max": [1,1], "anchored_pos": [0,0],
 "size_delta": [0,0], "pivot": [0.5,0.5], "scale": [1,1,1],
 "components": [{"class":"Image","sprite":"Star"},
                 {"class":"LanguageTextMeshPro","key":"txt_play","text":"Play"}]}
```

- **UI của game này phần lớn là SpriteRenderer trong world space** (chỉ 1 Canvas),
  nên dùng `local_pos` + `scale` là chính; `anchor_*` chỉ có ở node RectTransform.
- `local_pos` là **local space của Transform cha**, đơn vị Unity
  (canvas tham chiếu thường 1080×1920 → 1 unit = 100 px).
- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.
- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.
