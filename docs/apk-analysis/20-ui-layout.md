# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **735**
- tổng node: **104575**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (58)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90705 |
| `SpriteRenderer` | 49304 |
| `MeshRenderer` | 15334 |
| `RectTransform` | 13870 |
| `TextMeshPro` | 13793 |
| `MeshFilter` | 12510 |
| `BoxCollider2D` | 7392 |
| `Animator` | 5384 |
| `ButtonEvents` | 5113 |
| `Button_Sound` | 4975 |
| `ParticleSystem` | 3621 |
| `ParticleSystemRenderer` | 3621 |
| `LanguageTextMeshPro` | 3550 |
| `ChangeSorting` | 2226 |
| `BgObjectScaler` | 1633 |
| `Popup_Notices` | 1263 |
| `Box_Rewards` | 1191 |
| `TMP_SubMesh` | 1037 |
| `UIObjectAnchors` | 754 |
| `Shop_Cell` | 697 |
| `FixUIShop` | 636 |
| `Rigidbody2D` | 346 |
| `ObjectPool` | 329 |
| `LineRenderer` | 280 |
| `Enemy_Datas` | 276 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 431 | 335 | 61 |
| `Board_Shop` | 2894 | 493 | 139 | 40 |
| `Board_PVP` | 2856 | 405 | 171 | 42 |
| `Board_FightBoss` | 2466 | 138 | 46 | 39 |
| `Board_SelectBoss` | 2158 | 113 | 17 | 30 |
| `Board_Arena` | 1937 | 276 | 121 | 31 |
| `Tab_Boss` | 1890 | 5 | 0 | 30 |
| `Board_Players` | 1767 | 209 | 79 | 29 |
| `Board_BattlePass` | 1648 | 228 | 59 | 17 |
| `Board_Ranks` | 1356 | 217 | 87 | 22 |
| `Board_Ranks` | 1322 | 196 | 85 | 20 |
| `Board_TechLab` | 1304 | 159 | 74 | 19 |
| `Board_Survival` | 1249 | 200 | 81 | 20 |
| `Board_Survival` | 1131 | 174 | 79 | 19 |
| `Board_Drones` | 1094 | 140 | 60 | 18 |
| `Board_Begin` | 982 | 128 | 46 | 15 |
| `Board_WinnerBenefits` | 933 | 134 | 50 | 14 |
| `Popup_WatchVideos` | 929 | 162 | 48 | 13 |
| `Board_Reborn` | 910 | 146 | 57 | 16 |
| `Popup_WatchVideos` | 898 | 161 | 45 | 13 |
| `Board_Combo` | 883 | 85 | 53 | 13 |
| `Board_GiftLogin` | 830 | 121 | 22 | 12 |
| `Board_Challange` | 820 | 141 | 55 | 13 |
| `Board_BattlePassPro` | 786 | 117 | 37 | 12 |
| `Board_MiniCombo` | 785 | 92 | 42 | 11 |
| `Board_Setting` | 767 | 98 | 63 | 12 |
| `Board_Endgame` | 765 | 103 | 47 | 14 |
| `Board_Stage` | 731 | 123 | 51 | 12 |
| `Board_Vip` | 706 | 99 | 25 | 10 |
| `Popup_ShipSalePack` | 660 | 16 | 7 | 10 |
| `Board_QuestRewards` | 660 | 82 | 27 | 9 |
| `Board_UserProfile` | 610 | 60 | 48 | 10 |
| `Popup_HolidayGift` | 547 | 67 | 10 | 7 |
| `Board_EventSeasonPass` | 526 | 97 | 28 | 9 |
| `Popup_HolidayGift` | 522 | 76 | 11 | 7 |
| `Board_EventSeasonPass` | 478 | 71 | 21 | 7 |
| `Board_Begin` | 382 | 33 | 15 | 5 |
| `Popup_WeekSales` | 380 | 59 | 14 | 6 |
| `Popup_PvPRankings` | 370 | 56 | 18 | 7 |
| `Popup_PvPRankings` | 370 | 54 | 17 | 7 |

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
