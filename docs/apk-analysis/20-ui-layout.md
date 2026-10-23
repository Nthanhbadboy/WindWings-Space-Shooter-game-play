# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **733**
- tổng node: **105774**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (60)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91780 |
| `SpriteRenderer` | 49966 |
| `MeshRenderer` | 15472 |
| `RectTransform` | 13994 |
| `TextMeshPro` | 13919 |
| `MeshFilter` | 12638 |
| `BoxCollider2D` | 7438 |
| `Animator` | 5449 |
| `ButtonEvents` | 5126 |
| `Button_Sound` | 4989 |
| `ParticleSystem` | 3718 |
| `ParticleSystemRenderer` | 3718 |
| `LanguageTextMeshPro` | 3569 |
| `ChangeSorting` | 2224 |
| `BgObjectScaler` | 1638 |
| `Popup_Notices` | 1264 |
| `Box_Rewards` | 1210 |
| `TMP_SubMesh` | 1040 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 699 |
| `FixUIShop` | 652 |
| `Rigidbody2D` | 366 |
| `ObjectPool` | 325 |
| `LineRenderer` | 318 |
| `Enemy_Datas` | 276 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 430 | 333 | 61 |
| `Board_Shop` | 3526 | 606 | 178 | 49 |
| `Board_PVP` | 2551 | 304 | 150 | 39 |
| `Board_FightBoss` | 2496 | 109 | 43 | 40 |
| `Board_SelectBoss` | 2065 | 107 | 15 | 29 |
| `Board_Arena` | 1904 | 244 | 124 | 30 |
| `Tab_Boss` | 1738 | 5 | 0 | 27 |
| `Board_BattlePass` | 1725 | 242 | 63 | 18 |
| `Board_Players` | 1695 | 169 | 70 | 28 |
| `Board_Survival` | 1455 | 221 | 82 | 23 |
| `Board_Ranks` | 1325 | 195 | 86 | 20 |
| `Board_Ranks` | 1259 | 178 | 86 | 20 |
| `Board_Survival` | 1194 | 165 | 78 | 19 |
| `Board_TechLab` | 1180 | 143 | 66 | 17 |
| `Board_Drones` | 1030 | 135 | 58 | 18 |
| `Board_MiniCombo` | 983 | 105 | 54 | 14 |
| `Board_Begin` | 951 | 131 | 51 | 15 |
| `Board_BattlePassPro` | 947 | 117 | 37 | 14 |
| `Board_Combo` | 934 | 97 | 54 | 14 |
| `Board_Endgame` | 886 | 125 | 51 | 15 |
| `Popup_WatchVideos` | 875 | 149 | 45 | 13 |
| `Board_GiftLogin` | 860 | 123 | 26 | 13 |
| `Board_WinnerBenefits` | 848 | 144 | 54 | 14 |
| `Popup_WatchVideos` | 846 | 153 | 49 | 12 |
| `Board_Reborn` | 835 | 139 | 56 | 14 |
| `Board_Setting` | 803 | 102 | 67 | 12 |
| `Board_Challange` | 801 | 133 | 51 | 12 |
| `Board_Vip` | 740 | 88 | 26 | 11 |
| `Board_Stage` | 712 | 113 | 50 | 11 |
| `Popup_ShipSalePack` | 609 | 16 | 6 | 9 |
| `Board_ShopEnergy` | 605 | 97 | 32 | 9 |
| `Board_UserProfile` | 603 | 55 | 45 | 9 |
| `Board_QuestRewards` | 602 | 79 | 26 | 9 |
| `Tab_Boss` | 589 | 7 | 1 | 8 |
| `Board_EventSeasonPass` | 543 | 84 | 28 | 9 |
| `Popup_HolidayGift` | 537 | 80 | 10 | 8 |
| `Popup_HolidayGift` | 513 | 67 | 11 | 7 |
| `Board_EventSeasonPass` | 511 | 72 | 22 | 8 |
| `Board_Begin` | 415 | 35 | 15 | 5 |
| `Popup_WeekSales` | 376 | 44 | 12 | 5 |

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
