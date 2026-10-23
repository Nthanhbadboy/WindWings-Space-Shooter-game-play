# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **734**
- tổng node: **104946**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (59)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91263 |
| `SpriteRenderer` | 49427 |
| `MeshRenderer` | 15125 |
| `RectTransform` | 13683 |
| `TextMeshPro` | 13615 |
| `MeshFilter` | 12307 |
| `BoxCollider2D` | 7467 |
| `Animator` | 5349 |
| `ButtonEvents` | 5188 |
| `Button_Sound` | 5040 |
| `ParticleSystem` | 3789 |
| `ParticleSystemRenderer` | 3789 |
| `LanguageTextMeshPro` | 3556 |
| `ChangeSorting` | 2234 |
| `BgObjectScaler` | 1642 |
| `Popup_Notices` | 1262 |
| `Box_Rewards` | 1198 |
| `TMP_SubMesh` | 1005 |
| `UIObjectAnchors` | 758 |
| `Shop_Cell` | 682 |
| `FixUIShop` | 617 |
| `ObjectPool` | 349 |
| `Rigidbody2D` | 342 |
| `Enemy_Datas` | 299 |
| `Enemy_Health` | 299 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 435 | 339 | 60 |
| `Board_Shop` | 3210 | 499 | 154 | 44 |
| `Board_FightBoss` | 2415 | 125 | 47 | 38 |
| `Board_PVP` | 2382 | 376 | 158 | 37 |
| `Board_SelectBoss` | 2205 | 110 | 17 | 30 |
| `Tab_Boss` | 1928 | 6 | 0 | 30 |
| `Board_Arena` | 1925 | 239 | 123 | 31 |
| `Board_Players` | 1811 | 176 | 80 | 30 |
| `Board_BattlePass` | 1602 | 223 | 58 | 17 |
| `Board_Ranks` | 1450 | 213 | 94 | 23 |
| `Board_Ranks` | 1351 | 176 | 90 | 22 |
| `Board_Survival` | 1340 | 161 | 79 | 21 |
| `Board_Survival` | 1325 | 196 | 84 | 21 |
| `Board_TechLab` | 1070 | 140 | 74 | 16 |
| `Board_Drones` | 1017 | 135 | 61 | 18 |
| `Board_Begin` | 964 | 143 | 49 | 15 |
| `Board_Combo` | 922 | 103 | 55 | 14 |
| `Board_WinnerBenefits` | 911 | 140 | 56 | 14 |
| `Board_MiniCombo` | 908 | 99 | 60 | 13 |
| `Board_Endgame` | 872 | 128 | 51 | 16 |
| `Board_Setting` | 871 | 97 | 66 | 13 |
| `Board_BattlePassPro` | 862 | 111 | 31 | 13 |
| `Board_Reborn` | 843 | 125 | 55 | 14 |
| `Board_Challange` | 829 | 151 | 52 | 13 |
| `Board_GiftLogin` | 828 | 130 | 27 | 12 |
| `Popup_WatchVideos` | 775 | 130 | 42 | 11 |
| `Popup_WatchVideos` | 758 | 117 | 39 | 11 |
| `Board_Vip` | 751 | 82 | 26 | 11 |
| `Board_Stage` | 748 | 133 | 51 | 12 |
| `Board_QuestRewards` | 716 | 101 | 27 | 10 |
| `Board_UserProfile` | 664 | 61 | 48 | 10 |
| `Popup_ShipSalePack` | 600 | 13 | 7 | 9 |
| `Tab_Boss` | 536 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 512 | 78 | 10 | 7 |
| `Popup_HolidayGift` | 512 | 58 | 10 | 7 |
| `Board_ShopEnergy` | 509 | 85 | 34 | 8 |
| `Board_EventSeasonPass` | 476 | 72 | 22 | 7 |
| `Board_EventSeasonPass` | 462 | 78 | 27 | 8 |
| `Popup_WeekSales` | 439 | 56 | 13 | 6 |
| `Popup_PvPRankings` | 416 | 49 | 16 | 7 |

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
