# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **720**
- tổng node: **101942**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (73)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88461 |
| `SpriteRenderer` | 48197 |
| `MeshRenderer` | 14920 |
| `RectTransform` | 13481 |
| `TextMeshPro` | 13410 |
| `MeshFilter` | 12264 |
| `BoxCollider2D` | 7282 |
| `Animator` | 5290 |
| `ButtonEvents` | 5028 |
| `Button_Sound` | 4879 |
| `ParticleSystem` | 3707 |
| `ParticleSystemRenderer` | 3707 |
| `LanguageTextMeshPro` | 3520 |
| `ChangeSorting` | 2196 |
| `BgObjectScaler` | 1621 |
| `Popup_Notices` | 1243 |
| `Box_Rewards` | 1223 |
| `TMP_SubMesh` | 1028 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 649 |
| `FixUIShop` | 613 |
| `Rigidbody2D` | 345 |
| `ObjectPool` | 327 |
| `Enemy_Datas` | 276 |
| `Enemy_Health` | 276 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 433 | 329 | 60 |
| `Board_Shop` | 3225 | 517 | 147 | 45 |
| `Board_FightBoss` | 2537 | 102 | 39 | 40 |
| `Board_PVP` | 2457 | 381 | 171 | 38 |
| `Board_SelectBoss` | 2119 | 115 | 16 | 29 |
| `Board_BattlePass` | 1868 | 254 | 71 | 18 |
| `Tab_Boss` | 1812 | 5 | 0 | 28 |
| `Board_Arena` | 1700 | 249 | 105 | 29 |
| `Board_Ranks` | 1438 | 217 | 93 | 23 |
| `Board_Ranks` | 1356 | 165 | 76 | 21 |
| `Board_Survival` | 1319 | 193 | 86 | 21 |
| `Board_TechLab` | 1197 | 142 | 62 | 18 |
| `Board_Players` | 1126 | 163 | 62 | 18 |
| `Board_Drones` | 1076 | 150 | 61 | 18 |
| `Board_Combo` | 1072 | 106 | 64 | 15 |
| `Board_Survival` | 1046 | 167 | 80 | 18 |
| `Board_WinnerBenefits` | 995 | 145 | 50 | 14 |
| `Board_BattlePassPro` | 929 | 125 | 43 | 14 |
| `Board_Begin` | 925 | 130 | 47 | 15 |
| `Board_GiftLogin` | 906 | 132 | 28 | 13 |
| `Popup_WatchVideos` | 834 | 159 | 49 | 13 |
| `Board_Reborn` | 822 | 146 | 59 | 15 |
| `Popup_WatchVideos` | 789 | 131 | 46 | 12 |
| `Board_Endgame` | 788 | 123 | 43 | 13 |
| `Board_Stage` | 745 | 122 | 49 | 12 |
| `Board_Challange` | 733 | 109 | 52 | 11 |
| `Board_Vip` | 707 | 88 | 25 | 11 |
| `Board_Setting` | 675 | 90 | 64 | 11 |
| `Board_MiniCombo` | 663 | 78 | 34 | 10 |
| `Popup_ShipSalePack` | 659 | 19 | 7 | 10 |
| `Board_QuestRewards` | 654 | 91 | 25 | 9 |
| `Board_EventSeasonPass` | 581 | 94 | 29 | 10 |
| `Tab_Boss` | 572 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 540 | 74 | 11 | 8 |
| `Popup_HolidayGift` | 532 | 65 | 10 | 7 |
| `Board_EventSeasonPass` | 508 | 75 | 22 | 7 |
| `Board_ShopEnergy` | 476 | 95 | 29 | 8 |
| `Popup_WeekSales` | 475 | 64 | 13 | 6 |
| `Board_UserProfile` | 450 | 36 | 50 | 7 |
| `Popup_PvPRankings` | 423 | 46 | 19 | 7 |

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
