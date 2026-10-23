# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **714**
- tổng node: **105081**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (79)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90947 |
| `SpriteRenderer` | 49340 |
| `MeshRenderer` | 15655 |
| `RectTransform` | 14134 |
| `TextMeshPro` | 14062 |
| `MeshFilter` | 12832 |
| `BoxCollider2D` | 7408 |
| `Animator` | 5360 |
| `ButtonEvents` | 5124 |
| `Button_Sound` | 4980 |
| `ParticleSystem` | 3771 |
| `ParticleSystemRenderer` | 3771 |
| `LanguageTextMeshPro` | 3602 |
| `ChangeSorting` | 2227 |
| `BgObjectScaler` | 1631 |
| `Popup_Notices` | 1253 |
| `Box_Rewards` | 1206 |
| `TMP_SubMesh` | 1067 |
| `UIObjectAnchors` | 747 |
| `Shop_Cell` | 711 |
| `FixUIShop` | 651 |
| `Rigidbody2D` | 372 |
| `ObjectPool` | 333 |
| `LineRenderer` | 317 |
| `Enemy_Datas` | 288 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 425 | 331 | 60 |
| `Board_Shop` | 3391 | 574 | 159 | 48 |
| `Board_FightBoss` | 2398 | 110 | 39 | 38 |
| `Board_PVP` | 2345 | 342 | 156 | 36 |
| `Board_SelectBoss` | 2125 | 100 | 15 | 27 |
| `Board_Arena` | 1907 | 256 | 118 | 30 |
| `Board_Players` | 1769 | 209 | 77 | 29 |
| `Tab_Boss` | 1689 | 5 | 0 | 27 |
| `Board_TechLab` | 1569 | 188 | 80 | 21 |
| `Board_BattlePass` | 1526 | 213 | 62 | 17 |
| `Board_Ranks` | 1464 | 228 | 90 | 23 |
| `Board_Survival` | 1250 | 218 | 82 | 21 |
| `Board_Survival` | 1119 | 195 | 83 | 19 |
| `Board_Ranks` | 1090 | 187 | 84 | 18 |
| `Board_WinnerBenefits` | 975 | 130 | 56 | 15 |
| `Board_Drones` | 964 | 133 | 59 | 17 |
| `Board_MiniCombo` | 949 | 98 | 57 | 13 |
| `Board_BattlePassPro` | 931 | 124 | 42 | 14 |
| `Board_Begin` | 924 | 147 | 53 | 15 |
| `Board_GiftLogin` | 912 | 134 | 25 | 13 |
| `Popup_WatchVideos` | 856 | 152 | 49 | 12 |
| `Popup_WatchVideos` | 854 | 158 | 47 | 12 |
| `Board_Challange` | 815 | 136 | 51 | 13 |
| `Board_Endgame` | 808 | 120 | 49 | 14 |
| `Board_Reborn` | 785 | 144 | 58 | 14 |
| `Board_Stage` | 785 | 132 | 52 | 12 |
| `Board_Setting` | 745 | 80 | 48 | 11 |
| `Board_Vip` | 720 | 83 | 25 | 11 |
| `Popup_ShipSalePack` | 695 | 17 | 7 | 10 |
| `Board_QuestRewards` | 636 | 94 | 24 | 9 |
| `Board_UserProfile` | 592 | 58 | 50 | 9 |
| `Board_ShopEnergy` | 569 | 100 | 32 | 9 |
| `Popup_HolidayGift` | 566 | 78 | 11 | 8 |
| `Tab_Boss` | 560 | 9 | 1 | 7 |
| `Board_EventSeasonPass` | 546 | 91 | 28 | 9 |
| `Popup_HolidayGift` | 524 | 63 | 9 | 7 |
| `Board_Combo` | 483 | 57 | 22 | 7 |
| `Board_EventSeasonPass` | 466 | 70 | 22 | 7 |
| `Popup_WeekSales` | 404 | 54 | 13 | 6 |
| `Popup_PvPRankings` | 379 | 55 | 16 | 7 |

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
