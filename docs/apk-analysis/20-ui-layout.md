# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **723**
- tổng node: **104076**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (70)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90521 |
| `SpriteRenderer` | 49140 |
| `MeshRenderer` | 15016 |
| `RectTransform` | 13555 |
| `TextMeshPro` | 13472 |
| `MeshFilter` | 12364 |
| `BoxCollider2D` | 7334 |
| `Animator` | 5387 |
| `ButtonEvents` | 5080 |
| `Button_Sound` | 4934 |
| `ParticleSystem` | 3642 |
| `ParticleSystemRenderer` | 3642 |
| `LanguageTextMeshPro` | 3537 |
| `ChangeSorting` | 2191 |
| `BgObjectScaler` | 1620 |
| `Popup_Notices` | 1237 |
| `Box_Rewards` | 1208 |
| `TMP_SubMesh` | 1032 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 638 |
| `FixUIShop` | 603 |
| `Rigidbody2D` | 378 |
| `ObjectPool` | 352 |
| `LineRenderer` | 311 |
| `Enemy_Datas` | 298 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 442 | 328 | 62 |
| `Board_Shop` | 2764 | 462 | 134 | 39 |
| `Board_PVP` | 2760 | 398 | 171 | 42 |
| `Board_FightBoss` | 2554 | 109 | 44 | 40 |
| `Board_SelectBoss` | 2201 | 110 | 17 | 30 |
| `Board_Arena` | 1759 | 177 | 102 | 28 |
| `Tab_Boss` | 1680 | 6 | 0 | 27 |
| `Board_BattlePass` | 1665 | 248 | 65 | 17 |
| `Board_Players` | 1652 | 171 | 74 | 27 |
| `Board_Ranks` | 1437 | 199 | 88 | 23 |
| `Board_Ranks` | 1404 | 197 | 89 | 22 |
| `Board_TechLab` | 1339 | 159 | 76 | 19 |
| `Board_Survival` | 1176 | 167 | 79 | 19 |
| `Board_Survival` | 1095 | 193 | 79 | 19 |
| `Board_Begin` | 1075 | 145 | 55 | 17 |
| `Board_BattlePassPro` | 1026 | 129 | 42 | 15 |
| `Board_Drones` | 1013 | 136 | 60 | 17 |
| `Board_WinnerBenefits` | 912 | 144 | 57 | 14 |
| `Board_Combo` | 882 | 94 | 52 | 13 |
| `Board_Endgame` | 863 | 130 | 53 | 16 |
| `Board_MiniCombo` | 852 | 89 | 45 | 13 |
| `Popup_WatchVideos` | 845 | 153 | 49 | 12 |
| `Board_Setting` | 824 | 106 | 67 | 13 |
| `Board_GiftLogin` | 808 | 124 | 26 | 12 |
| `Board_Vip` | 757 | 81 | 25 | 11 |
| `Board_Reborn` | 740 | 133 | 58 | 14 |
| `Board_Stage` | 705 | 114 | 52 | 11 |
| `Board_Challange` | 694 | 122 | 48 | 11 |
| `Popup_WatchVideos` | 691 | 134 | 45 | 11 |
| `Popup_ShipSalePack` | 678 | 15 | 7 | 9 |
| `Board_UserProfile` | 669 | 63 | 47 | 10 |
| `Board_QuestRewards` | 661 | 101 | 27 | 10 |
| `Board_ShopEnergy` | 607 | 100 | 32 | 9 |
| `Tab_Boss` | 549 | 6 | 1 | 7 |
| `Board_EventSeasonPass` | 527 | 95 | 29 | 9 |
| `Popup_HolidayGift` | 523 | 65 | 11 | 7 |
| `Popup_HolidayGift` | 507 | 79 | 11 | 7 |
| `Board_EventSeasonPass` | 489 | 73 | 21 | 7 |
| `Popup_WeekSales` | 469 | 63 | 14 | 6 |
| `Board_Begin` | 407 | 32 | 13 | 5 |

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
