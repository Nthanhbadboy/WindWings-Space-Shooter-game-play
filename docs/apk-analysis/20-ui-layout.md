# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **736**
- tổng node: **102010**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (57)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88344 |
| `SpriteRenderer` | 48177 |
| `MeshRenderer` | 15166 |
| `RectTransform` | 13666 |
| `TextMeshPro` | 13597 |
| `MeshFilter` | 12571 |
| `BoxCollider2D` | 7255 |
| `Animator` | 5215 |
| `ButtonEvents` | 4979 |
| `Button_Sound` | 4835 |
| `LanguageTextMeshPro` | 3608 |
| `ParticleSystem` | 3334 |
| `ParticleSystemRenderer` | 3334 |
| `ChangeSorting` | 2235 |
| `BgObjectScaler` | 1642 |
| `Popup_Notices` | 1268 |
| `Box_Rewards` | 1177 |
| `TMP_SubMesh` | 1051 |
| `UIObjectAnchors` | 755 |
| `Shop_Cell` | 666 |
| `FixUIShop` | 626 |
| `Rigidbody2D` | 334 |
| `LineRenderer` | 311 |
| `ObjectPool` | 309 |
| `Enemy_Datas` | 257 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4324 | 343 | 200 | 51 |
| `Board_Shop` | 2924 | 464 | 134 | 41 |
| `Board_PVP` | 2709 | 414 | 167 | 41 |
| `Board_FightBoss` | 2293 | 97 | 40 | 37 |
| `Board_SelectBoss` | 1892 | 100 | 17 | 27 |
| `Board_Players` | 1822 | 212 | 78 | 30 |
| `Board_BattlePass` | 1801 | 242 | 68 | 18 |
| `Tab_Boss` | 1758 | 5 | 0 | 27 |
| `Board_Arena` | 1634 | 211 | 98 | 27 |
| `Board_Ranks` | 1584 | 223 | 87 | 24 |
| `Board_Ranks` | 1501 | 225 | 90 | 23 |
| `Board_Survival` | 1442 | 193 | 88 | 22 |
| `Board_TechLab` | 1344 | 154 | 76 | 19 |
| `Board_Survival` | 1112 | 189 | 79 | 19 |
| `Board_Begin` | 1021 | 123 | 51 | 16 |
| `Board_Drones` | 974 | 140 | 60 | 16 |
| `Popup_WatchVideos` | 933 | 163 | 49 | 13 |
| `Board_Combo` | 931 | 96 | 55 | 14 |
| `Board_BattlePassPro` | 859 | 105 | 31 | 13 |
| `Board_Reborn` | 839 | 142 | 56 | 15 |
| `Board_Endgame` | 833 | 119 | 48 | 15 |
| `Board_Stage` | 823 | 145 | 54 | 13 |
| `Board_MiniCombo` | 799 | 84 | 40 | 12 |
| `Board_Challange` | 756 | 128 | 49 | 12 |
| `Popup_WatchVideos` | 751 | 100 | 39 | 10 |
| `Board_WinnerBenefits` | 738 | 133 | 55 | 12 |
| `Board_Setting` | 737 | 95 | 68 | 12 |
| `Board_GiftLogin` | 721 | 120 | 27 | 11 |
| `Board_Vip` | 714 | 82 | 27 | 11 |
| `Popup_ShipSalePack` | 681 | 17 | 6 | 9 |
| `Board_QuestRewards` | 649 | 84 | 26 | 9 |
| `Board_EventSeasonPass` | 566 | 89 | 28 | 10 |
| `Popup_HolidayGift` | 534 | 68 | 10 | 7 |
| `Board_EventSeasonPass` | 454 | 72 | 21 | 7 |
| `Board_UserProfile` | 451 | 51 | 47 | 7 |
| `Board_ShopEnergy` | 444 | 94 | 32 | 8 |
| `Popup_HolidayGift` | 438 | 70 | 9 | 6 |
| `Popup_PvPRankings` | 434 | 51 | 19 | 7 |
| `Popup_WeekSales` | 373 | 45 | 13 | 5 |
| `Popup_BuyMoreGems` | 357 | 69 | 15 | 5 |

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
