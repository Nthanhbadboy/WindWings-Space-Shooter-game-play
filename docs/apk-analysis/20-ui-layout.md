# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **735**
- tổng node: **105794**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (58)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91862 |
| `SpriteRenderer` | 49875 |
| `MeshRenderer` | 15403 |
| `RectTransform` | 13932 |
| `TextMeshPro` | 13862 |
| `MeshFilter` | 12590 |
| `BoxCollider2D` | 7517 |
| `Animator` | 5469 |
| `ButtonEvents` | 5192 |
| `Button_Sound` | 5040 |
| `ParticleSystem` | 3771 |
| `ParticleSystemRenderer` | 3771 |
| `LanguageTextMeshPro` | 3594 |
| `ChangeSorting` | 2214 |
| `BgObjectScaler` | 1639 |
| `Popup_Notices` | 1263 |
| `Box_Rewards` | 1239 |
| `TMP_SubMesh` | 1032 |
| `UIObjectAnchors` | 756 |
| `Shop_Cell` | 695 |
| `FixUIShop` | 632 |
| `Rigidbody2D` | 365 |
| `ObjectPool` | 352 |
| `LineRenderer` | 321 |
| `Enemy_Datas` | 298 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 431 | 335 | 61 |
| `Board_Shop` | 3705 | 625 | 174 | 51 |
| `Board_PVP` | 2708 | 377 | 166 | 40 |
| `Board_FightBoss` | 2459 | 118 | 44 | 39 |
| `Board_SelectBoss` | 2063 | 119 | 17 | 28 |
| `Board_Arena` | 1990 | 280 | 118 | 32 |
| `Board_Players` | 1848 | 195 | 76 | 30 |
| `Tab_Boss` | 1759 | 6 | 0 | 28 |
| `Board_BattlePass` | 1685 | 233 | 64 | 18 |
| `Board_Ranks` | 1585 | 215 | 88 | 24 |
| `Board_Survival` | 1426 | 184 | 83 | 22 |
| `Board_TechLab` | 1424 | 170 | 77 | 20 |
| `Board_Survival` | 1270 | 171 | 82 | 20 |
| `Board_Ranks` | 1206 | 193 | 86 | 19 |
| `Board_Drones` | 1025 | 128 | 59 | 17 |
| `Board_Combo` | 994 | 102 | 59 | 14 |
| `Board_Begin` | 987 | 139 | 53 | 16 |
| `Board_GiftLogin` | 955 | 134 | 29 | 14 |
| `Board_BattlePassPro` | 933 | 115 | 36 | 13 |
| `Board_Endgame` | 876 | 125 | 52 | 15 |
| `Board_Setting` | 869 | 96 | 63 | 13 |
| `Popup_WatchVideos` | 868 | 164 | 50 | 13 |
| `Board_MiniCombo` | 807 | 86 | 45 | 12 |
| `Board_Challange` | 796 | 132 | 52 | 12 |
| `Board_WinnerBenefits` | 796 | 116 | 52 | 12 |
| `Board_Reborn` | 787 | 130 | 48 | 13 |
| `Popup_WatchVideos` | 784 | 149 | 48 | 12 |
| `Board_Vip` | 723 | 89 | 24 | 11 |
| `Board_Stage` | 692 | 123 | 50 | 12 |
| `Board_QuestRewards` | 648 | 83 | 25 | 9 |
| `Board_ShopEnergy` | 632 | 113 | 32 | 9 |
| `Tab_Boss` | 548 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 532 | 65 | 11 | 7 |
| `Popup_HolidayGift` | 509 | 76 | 11 | 7 |
| `Board_EventSeasonPass` | 507 | 87 | 27 | 9 |
| `Popup_WeekSales` | 496 | 67 | 14 | 6 |
| `Board_EventSeasonPass` | 490 | 73 | 22 | 7 |
| `Popup_ShipSalePack` | 490 | 14 | 5 | 7 |
| `Board_UserProfile` | 481 | 57 | 50 | 8 |
| `Popup_PvPRankings` | 367 | 54 | 19 | 7 |

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
