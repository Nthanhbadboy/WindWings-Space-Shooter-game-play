# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **588**
- tổng node: **84225**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 72925 |
| `SpriteRenderer` | 39799 |
| `MeshRenderer` | 12488 |
| `RectTransform` | 11300 |
| `TextMeshPro` | 11255 |
| `MeshFilter` | 10192 |
| `BoxCollider2D` | 6090 |
| `Animator` | 4364 |
| `ButtonEvents` | 4234 |
| `Button_Sound` | 4125 |
| `ParticleSystem` | 2945 |
| `ParticleSystemRenderer` | 2945 |
| `LanguageTextMeshPro` | 2882 |
| `ChangeSorting` | 1821 |
| `BgObjectScaler` | 1372 |
| `Popup_Notices` | 1057 |
| `Box_Rewards` | 985 |
| `TMP_SubMesh` | 801 |
| `UIObjectAnchors` | 593 |
| `Shop_Cell` | 588 |
| `FixUIShop` | 533 |
| `Rigidbody2D` | 266 |
| `ObjectPool` | 254 |
| `LineRenderer` | 221 |
| `Enemy_Datas` | 210 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 423 | 332 | 60 |
| `Board_Shop` | 3409 | 536 | 169 | 47 |
| `Board_PVP` | 2562 | 363 | 171 | 39 |
| `Board_SelectBoss` | 2508 | 98 | 16 | 37 |
| `Board_Arena` | 1880 | 240 | 113 | 32 |
| `Tab_Boss` | 1698 | 6 | 0 | 27 |
| `Board_Players` | 1620 | 162 | 74 | 27 |
| `Board_BattlePass` | 1582 | 212 | 61 | 17 |
| `Board_Ranks` | 1538 | 208 | 89 | 24 |
| `Board_TechLab` | 1459 | 168 | 77 | 20 |
| `Board_Survival` | 1209 | 175 | 74 | 19 |
| `Board_Survival` | 1116 | 166 | 80 | 19 |
| `Board_Drones` | 1034 | 138 | 62 | 17 |
| `Board_Begin` | 1010 | 137 | 50 | 16 |
| `Board_Combo` | 991 | 104 | 57 | 14 |
| `Board_BattlePassPro` | 975 | 123 | 37 | 15 |
| `Board_WinnerBenefits` | 928 | 137 | 52 | 14 |
| `Popup_WatchVideos` | 888 | 168 | 45 | 13 |
| `Popup_WatchVideos` | 886 | 161 | 46 | 13 |
| `Board_Reborn` | 884 | 145 | 56 | 15 |
| `Board_Stage` | 810 | 131 | 53 | 13 |
| `Board_Endgame` | 779 | 110 | 49 | 14 |
| `Board_Challange` | 733 | 121 | 46 | 12 |
| `Board_GiftLogin` | 719 | 119 | 21 | 10 |
| `Board_Vip` | 713 | 92 | 25 | 11 |
| `Board_QuestRewards` | 659 | 103 | 27 | 9 |
| `Board_UserProfile` | 636 | 34 | 47 | 8 |
| `Board_ShopEnergy` | 545 | 96 | 33 | 9 |
| `Board_EventSeasonPass` | 541 | 86 | 25 | 9 |
| `Popup_HolidayGift` | 501 | 65 | 10 | 7 |
| `Popup_WeekSales` | 472 | 65 | 14 | 6 |
| `Board_EventSeasonPass` | 384 | 69 | 17 | 6 |
| `Board_Begin` | 373 | 33 | 13 | 5 |
| `Board_Reborn_IAP` | 352 | 70 | 15 | 5 |
| `Popup_BuyMoreGems` | 351 | 66 | 15 | 5 |
| `Popup_WatchVideosOld` | 346 | 55 | 13 | 5 |
| `Popup_Notices` | 345 | 66 | 15 | 5 |
| `Popup_BuyMoreGems` | 340 | 65 | 15 | 5 |
| `Board_Reborn_IAP` | 334 | 56 | 13 | 5 |
| `Board_Talents` | 330 | 28 | 9 | 4 |

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
