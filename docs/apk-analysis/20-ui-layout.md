# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **736**
- tổng node: **102365**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (57)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88625 |
| `SpriteRenderer` | 48319 |
| `MeshRenderer` | 15229 |
| `RectTransform` | 13740 |
| `TextMeshPro` | 13673 |
| `MeshFilter` | 12703 |
| `BoxCollider2D` | 7287 |
| `Animator` | 5165 |
| `ButtonEvents` | 5012 |
| `Button_Sound` | 4859 |
| `LanguageTextMeshPro` | 3501 |
| `ParticleSystem` | 3472 |
| `ParticleSystemRenderer` | 3472 |
| `ChangeSorting` | 2202 |
| `BgObjectScaler` | 1649 |
| `Popup_Notices` | 1266 |
| `Box_Rewards` | 1164 |
| `TMP_SubMesh` | 1067 |
| `UIObjectAnchors` | 711 |
| `Shop_Cell` | 709 |
| `FixUIShop` | 658 |
| `Rigidbody2D` | 285 |
| `ObjectPool` | 264 |
| `LineRenderer` | 244 |
| `AutoSetVipIcon` | 230 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4044 | 336 | 200 | 50 |
| `Board_Shop` | 3573 | 580 | 172 | 50 |
| `Board_PVP` | 2653 | 391 | 166 | 40 |
| `Board_FightBoss` | 2536 | 103 | 44 | 40 |
| `Tab_Boss` | 1882 | 5 | 0 | 29 |
| `Board_Arena` | 1829 | 218 | 106 | 30 |
| `Board_Players` | 1669 | 190 | 74 | 27 |
| `Board_BattlePass` | 1644 | 221 | 62 | 18 |
| `Board_Ranks` | 1457 | 199 | 88 | 22 |
| `Board_Survival` | 1457 | 211 | 84 | 23 |
| `Board_Ranks` | 1444 | 196 | 92 | 21 |
| `Board_TechLab` | 1279 | 158 | 67 | 18 |
| `Board_Survival` | 1146 | 157 | 85 | 19 |
| `Board_BattlePassPro` | 1051 | 128 | 43 | 16 |
| `Board_Drones` | 1039 | 142 | 59 | 17 |
| `Board_Begin` | 1007 | 143 | 50 | 16 |
| `Board_WinnerBenefits` | 988 | 153 | 57 | 15 |
| `Popup_WatchVideos` | 909 | 146 | 47 | 13 |
| `Popup_WatchVideos` | 898 | 156 | 48 | 13 |
| `Board_Endgame` | 875 | 127 | 53 | 16 |
| `Board_GiftLogin` | 823 | 122 | 27 | 12 |
| `Board_Challange` | 818 | 131 | 55 | 13 |
| `Board_Reborn` | 804 | 135 | 45 | 13 |
| `Board_Stage` | 787 | 119 | 52 | 12 |
| `Board_Vip` | 707 | 93 | 25 | 10 |
| `Board_QuestRewards` | 690 | 100 | 27 | 10 |
| `Board_Setting` | 684 | 95 | 58 | 11 |
| `Board_Combo` | 647 | 67 | 35 | 10 |
| `Tab_Boss` | 574 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 544 | 88 | 29 | 9 |
| `Popup_ShipSalePack` | 534 | 15 | 7 | 8 |
| `Popup_HolidayGift` | 531 | 64 | 11 | 7 |
| `Board_ShopEnergy` | 528 | 70 | 27 | 8 |
| `Popup_HolidayGift` | 521 | 77 | 11 | 7 |
| `Board_UserProfile` | 508 | 42 | 48 | 8 |
| `Popup_WeekSales` | 411 | 55 | 12 | 6 |
| `Board_EventSeasonPass` | 393 | 70 | 21 | 6 |
| `Board_MiniCombo` | 385 | 54 | 21 | 6 |
| `Popup_PvPRankings` | 383 | 51 | 19 | 7 |
| `Popup_WatchVideosOld` | 360 | 58 | 13 | 5 |

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
