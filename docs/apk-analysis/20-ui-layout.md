# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **729**
- tổng node: **106206**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (64)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92125 |
| `SpriteRenderer` | 50083 |
| `MeshRenderer` | 15600 |
| `RectTransform` | 14081 |
| `TextMeshPro` | 14013 |
| `MeshFilter` | 12798 |
| `BoxCollider2D` | 7449 |
| `Animator` | 5405 |
| `ButtonEvents` | 5165 |
| `Button_Sound` | 5036 |
| `ParticleSystem` | 3765 |
| `ParticleSystemRenderer` | 3765 |
| `LanguageTextMeshPro` | 3609 |
| `ChangeSorting` | 2242 |
| `BgObjectScaler` | 1635 |
| `Popup_Notices` | 1261 |
| `Box_Rewards` | 1185 |
| `TMP_SubMesh` | 1081 |
| `UIObjectAnchors` | 757 |
| `Shop_Cell` | 703 |
| `FixUIShop` | 642 |
| `Rigidbody2D` | 375 |
| `ObjectPool` | 328 |
| `LineRenderer` | 297 |
| `Enemy_Datas` | 274 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 438 | 334 | 61 |
| `Board_Shop` | 3215 | 510 | 147 | 44 |
| `Board_PVP` | 2778 | 415 | 168 | 42 |
| `Board_FightBoss` | 2582 | 128 | 43 | 40 |
| `Board_Players` | 1796 | 194 | 75 | 29 |
| `Board_Arena` | 1786 | 230 | 120 | 29 |
| `Tab_Boss` | 1718 | 5 | 0 | 26 |
| `Board_BattlePass` | 1678 | 233 | 63 | 18 |
| `Board_SelectBoss` | 1643 | 93 | 17 | 24 |
| `Board_Ranks` | 1488 | 207 | 91 | 23 |
| `Board_Ranks` | 1442 | 205 | 88 | 23 |
| `Board_Survival` | 1348 | 193 | 85 | 22 |
| `Board_TechLab` | 1283 | 143 | 66 | 18 |
| `Board_Survival` | 1174 | 137 | 71 | 19 |
| `Board_Drones` | 1042 | 133 | 57 | 18 |
| `Board_WinnerBenefits` | 1025 | 150 | 50 | 14 |
| `Board_Begin` | 981 | 140 | 50 | 16 |
| `Popup_WatchVideos` | 977 | 177 | 50 | 14 |
| `Board_BattlePassPro` | 970 | 126 | 38 | 15 |
| `Board_Combo` | 957 | 91 | 57 | 13 |
| `Board_Reborn` | 917 | 156 | 62 | 15 |
| `Board_GiftLogin` | 854 | 123 | 23 | 12 |
| `Board_MiniCombo` | 846 | 91 | 45 | 13 |
| `Board_Setting` | 820 | 102 | 67 | 13 |
| `Popup_WatchVideos` | 790 | 138 | 47 | 12 |
| `Board_Endgame` | 773 | 123 | 48 | 14 |
| `Board_Vip` | 771 | 83 | 25 | 11 |
| `Board_Challange` | 727 | 115 | 45 | 11 |
| `Board_Stage` | 720 | 112 | 49 | 12 |
| `Board_QuestRewards` | 704 | 94 | 27 | 10 |
| `Board_UserProfile` | 672 | 64 | 49 | 10 |
| `Popup_ShipSalePack` | 656 | 17 | 7 | 9 |
| `Board_ShopEnergy` | 569 | 95 | 34 | 9 |
| `Tab_Boss` | 562 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 547 | 77 | 11 | 8 |
| `Board_EventSeasonPass` | 542 | 93 | 27 | 9 |
| `Board_EventSeasonPass` | 507 | 72 | 22 | 7 |
| `Popup_HolidayGift` | 504 | 67 | 11 | 7 |
| `Popup_WeekSales` | 434 | 56 | 13 | 6 |
| `Popup_PvPRankings` | 379 | 50 | 19 | 7 |

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
