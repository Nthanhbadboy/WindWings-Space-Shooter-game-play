# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **744**
- tổng node: **105132**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (49)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91219 |
| `SpriteRenderer` | 49421 |
| `MeshRenderer` | 15421 |
| `RectTransform` | 13913 |
| `TextMeshPro` | 13845 |
| `MeshFilter` | 12731 |
| `BoxCollider2D` | 7343 |
| `Animator` | 5470 |
| `ButtonEvents` | 5012 |
| `Button_Sound` | 4858 |
| `ParticleSystem` | 3876 |
| `ParticleSystemRenderer` | 3876 |
| `LanguageTextMeshPro` | 3578 |
| `ChangeSorting` | 2245 |
| `BgObjectScaler` | 1645 |
| `Popup_Notices` | 1277 |
| `Box_Rewards` | 1231 |
| `TMP_SubMesh` | 1069 |
| `UIObjectAnchors` | 744 |
| `Shop_Cell` | 697 |
| `FixUIShop` | 658 |
| `Rigidbody2D` | 395 |
| `ObjectPool` | 371 |
| `Enemy_Datas` | 316 |
| `Enemy_Health` | 316 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 3919 | 304 | 183 | 45 |
| `Board_Shop` | 3714 | 629 | 170 | 50 |
| `Board_FightBoss` | 2580 | 124 | 47 | 40 |
| `Board_PVP` | 2439 | 344 | 158 | 36 |
| `Board_SelectBoss` | 2164 | 87 | 16 | 31 |
| `Tab_Boss` | 1867 | 6 | 0 | 29 |
| `Board_BattlePass` | 1806 | 250 | 67 | 18 |
| `Board_Arena` | 1799 | 222 | 106 | 30 |
| `Board_Players` | 1712 | 180 | 72 | 28 |
| `Board_Survival` | 1408 | 204 | 85 | 22 |
| `Board_Ranks` | 1379 | 186 | 80 | 22 |
| `Board_Ranks` | 1351 | 195 | 89 | 22 |
| `Board_TechLab` | 1310 | 161 | 75 | 19 |
| `Board_Survival` | 1248 | 186 | 82 | 20 |
| `Board_Drones` | 1022 | 119 | 58 | 17 |
| `Board_WinnerBenefits` | 915 | 137 | 53 | 14 |
| `Board_MiniCombo` | 908 | 90 | 57 | 13 |
| `Board_BattlePassPro` | 898 | 131 | 42 | 14 |
| `Board_Combo` | 836 | 86 | 43 | 13 |
| `Board_GiftLogin` | 834 | 127 | 28 | 12 |
| `Board_Endgame` | 830 | 118 | 51 | 15 |
| `Board_Reborn` | 817 | 144 | 60 | 15 |
| `Popup_WatchVideos` | 816 | 136 | 47 | 12 |
| `Popup_WatchVideos` | 783 | 150 | 48 | 12 |
| `Board_Begin` | 773 | 117 | 53 | 13 |
| `Board_Stage` | 707 | 114 | 51 | 11 |
| `Board_Challange` | 697 | 140 | 48 | 12 |
| `Board_Vip` | 695 | 88 | 27 | 10 |
| `Popup_ShipSalePack` | 668 | 18 | 7 | 10 |
| `Board_UserProfile` | 647 | 60 | 48 | 10 |
| `Board_Setting` | 621 | 89 | 58 | 10 |
| `Board_ShopEnergy` | 606 | 106 | 33 | 9 |
| `Board_QuestRewards` | 586 | 99 | 25 | 9 |
| `Popup_HolidayGift` | 546 | 79 | 11 | 8 |
| `Board_EventSeasonPass` | 533 | 87 | 24 | 9 |
| `Popup_HolidayGift` | 529 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 498 | 76 | 22 | 8 |
| `Tab_Boss` | 463 | 9 | 1 | 6 |
| `Popup_WeekSales` | 434 | 55 | 14 | 6 |
| `Popup_PvPRankings` | 415 | 56 | 16 | 7 |

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
