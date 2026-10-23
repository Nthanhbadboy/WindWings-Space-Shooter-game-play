# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **730**
- tổng node: **104743**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (63)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90854 |
| `SpriteRenderer` | 49299 |
| `MeshRenderer` | 15355 |
| `RectTransform` | 13889 |
| `TextMeshPro` | 13820 |
| `MeshFilter` | 12486 |
| `BoxCollider2D` | 7432 |
| `Animator` | 5455 |
| `ButtonEvents` | 5130 |
| `Button_Sound` | 4976 |
| `ParticleSystem` | 3645 |
| `ParticleSystemRenderer` | 3645 |
| `LanguageTextMeshPro` | 3607 |
| `ChangeSorting` | 2212 |
| `BgObjectScaler` | 1637 |
| `Popup_Notices` | 1255 |
| `Box_Rewards` | 1247 |
| `TMP_SubMesh` | 1020 |
| `UIObjectAnchors` | 753 |
| `Shop_Cell` | 672 |
| `FixUIShop` | 623 |
| `Rigidbody2D` | 392 |
| `ObjectPool` | 356 |
| `Enemy_Datas` | 306 |
| `Enemy_Health` | 306 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 438 | 325 | 61 |
| `Board_Shop` | 3762 | 611 | 167 | 51 |
| `Board_PVP` | 2812 | 407 | 164 | 43 |
| `Board_FightBoss` | 2449 | 108 | 44 | 39 |
| `Board_SelectBoss` | 2066 | 110 | 17 | 28 |
| `Board_Arena` | 1954 | 241 | 124 | 31 |
| `Tab_Boss` | 1872 | 4 | 0 | 29 |
| `Board_Players` | 1840 | 211 | 79 | 30 |
| `Board_BattlePass` | 1664 | 234 | 68 | 18 |
| `Board_Ranks` | 1562 | 210 | 90 | 24 |
| `Board_Ranks` | 1457 | 194 | 83 | 21 |
| `Board_Survival` | 1314 | 185 | 86 | 21 |
| `Board_TechLab` | 1244 | 152 | 74 | 18 |
| `Board_Survival` | 1092 | 188 | 76 | 19 |
| `Board_WinnerBenefits` | 1065 | 154 | 58 | 16 |
| `Board_Drones` | 992 | 129 | 60 | 17 |
| `Board_BattlePassPro` | 984 | 123 | 43 | 15 |
| `Board_Begin` | 920 | 134 | 51 | 15 |
| `Board_MiniCombo` | 877 | 88 | 54 | 13 |
| `Popup_WatchVideos` | 853 | 151 | 48 | 13 |
| `Popup_WatchVideos` | 830 | 132 | 44 | 12 |
| `Board_Reborn` | 824 | 139 | 60 | 15 |
| `Board_Endgame` | 811 | 115 | 44 | 14 |
| `Board_Vip` | 799 | 98 | 27 | 11 |
| `Board_GiftLogin` | 781 | 129 | 27 | 12 |
| `Board_Stage` | 743 | 132 | 53 | 12 |
| `Board_Challange` | 742 | 113 | 50 | 12 |
| `Board_UserProfile` | 610 | 53 | 50 | 9 |
| `Board_Setting` | 605 | 86 | 65 | 10 |
| `Board_QuestRewards` | 596 | 83 | 26 | 9 |
| `Popup_ShipSalePack` | 594 | 18 | 5 | 9 |
| `Board_ShopEnergy` | 588 | 110 | 33 | 9 |
| `Board_Combo` | 576 | 71 | 34 | 10 |
| `Tab_Boss` | 566 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 535 | 91 | 29 | 9 |
| `Popup_HolidayGift` | 529 | 73 | 11 | 7 |
| `Board_EventSeasonPass` | 505 | 71 | 22 | 8 |
| `Popup_HolidayGift` | 493 | 65 | 9 | 7 |
| `Popup_WeekSales` | 462 | 61 | 13 | 6 |
| `Popup_PvPRankings` | 448 | 57 | 18 | 7 |

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
