# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **579**
- tổng node: **78393**
- dung lượng thô (gz): **1.5 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 67949 |
| `SpriteRenderer` | 37184 |
| `MeshRenderer` | 11532 |
| `RectTransform` | 10444 |
| `TextMeshPro` | 10386 |
| `MeshFilter` | 9603 |
| `BoxCollider2D` | 5490 |
| `Animator` | 3875 |
| `ButtonEvents` | 3809 |
| `Button_Sound` | 3714 |
| `LanguageTextMeshPro` | 2680 |
| `ParticleSystem` | 2595 |
| `ParticleSystemRenderer` | 2595 |
| `ChangeSorting` | 1654 |
| `BgObjectScaler` | 1238 |
| `Popup_Notices` | 979 |
| `TMP_SubMesh` | 818 |
| `Box_Rewards` | 749 |
| `Shop_Cell` | 536 |
| `FixUIShop` | 507 |
| `UIObjectAnchors` | 501 |
| `Rigidbody2D` | 244 |
| `ObjectPool` | 229 |
| `Enemy_Datas` | 199 |
| `Enemy_Health` | 199 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 439 | 338 | 60 |
| `Board_PVP` | 2750 | 403 | 165 | 40 |
| `Board_SelectBoss` | 2425 | 111 | 17 | 32 |
| `Tab_Boss` | 1910 | 6 | 0 | 29 |
| `Board_Ranks` | 1548 | 223 | 91 | 24 |
| `Board_Ranks` | 1399 | 209 | 85 | 22 |
| `Board_Survival` | 1388 | 202 | 84 | 22 |
| `Board_Survival` | 1202 | 196 | 83 | 21 |
| `Board_TechLab` | 1201 | 141 | 57 | 17 |
| `Board_WinnerBenefits` | 989 | 146 | 56 | 14 |
| `Board_Drones` | 946 | 132 | 59 | 17 |
| `Board_Begin` | 925 | 134 | 49 | 15 |
| `Popup_WatchVideos` | 905 | 167 | 49 | 13 |
| `Board_Setting` | 865 | 99 | 63 | 13 |
| `Board_Endgame` | 852 | 123 | 50 | 15 |
| `Popup_WatchVideos` | 849 | 151 | 47 | 12 |
| `Board_Challange` | 795 | 133 | 52 | 13 |
| `Board_BattlePassPro` | 792 | 101 | 27 | 11 |
| `Board_Stage` | 730 | 127 | 51 | 12 |
| `Board_Vip` | 723 | 91 | 27 | 11 |
| `Popup_ShipSalePack` | 708 | 18 | 6 | 10 |
| `Board_QuestRewards` | 687 | 101 | 27 | 10 |
| `Board_ShopEnergy` | 645 | 107 | 33 | 10 |
| `Popup_HolidayGift` | 558 | 77 | 11 | 8 |
| `Board_EventSeasonPass` | 541 | 89 | 27 | 9 |
| `Board_UserProfile` | 540 | 60 | 45 | 8 |
| `Popup_HolidayGift` | 517 | 66 | 11 | 7 |
| `Popup_WeekSales` | 486 | 61 | 14 | 6 |
| `Board_EventSeasonPass` | 455 | 65 | 19 | 7 |
| `Popup_PvPRankings` | 412 | 56 | 18 | 7 |
| `Popup_BuyMoreGems` | 346 | 67 | 15 | 5 |
| `Board_Talents` | 345 | 32 | 9 | 4 |
| `Board_Begin` | 344 | 32 | 15 | 5 |
| `Popup_WatchVideosOld` | 340 | 56 | 13 | 5 |
| `Popup_Notices` | 340 | 68 | 15 | 5 |
| `Popup_WatchVideosOld` | 339 | 53 | 13 | 5 |
| `Popup_BuyMoreGems` | 330 | 68 | 14 | 5 |
| `Popup_BuyMoreGems` | 324 | 65 | 15 | 5 |
| `Popup_BuyMoreGems` | 324 | 60 | 14 | 5 |
| `Popup_BuyMoreGems` | 324 | 56 | 14 | 5 |

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
