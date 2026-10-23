# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **727**
- tổng node: **102650**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (66)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88724 |
| `SpriteRenderer` | 47601 |
| `MeshRenderer` | 15450 |
| `RectTransform` | 13926 |
| `TextMeshPro` | 13855 |
| `MeshFilter` | 12701 |
| `BoxCollider2D` | 7254 |
| `Animator` | 5283 |
| `ButtonEvents` | 4926 |
| `Button_Sound` | 4794 |
| `ParticleSystem` | 3810 |
| `ParticleSystemRenderer` | 3810 |
| `LanguageTextMeshPro` | 3635 |
| `ChangeSorting` | 2225 |
| `BgObjectScaler` | 1631 |
| `Popup_Notices` | 1257 |
| `Box_Rewards` | 1233 |
| `TMP_SubMesh` | 1057 |
| `UIObjectAnchors` | 759 |
| `Shop_Cell` | 700 |
| `FixUIShop` | 626 |
| `Rigidbody2D` | 407 |
| `ObjectPool` | 358 |
| `LineRenderer` | 320 |
| `Enemy_Datas` | 309 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Shop` | 3495 | 546 | 161 | 46 |
| `Board_PVP` | 2841 | 416 | 171 | 43 |
| `Board_SelectBoss` | 2608 | 102 | 17 | 36 |
| `Board_FightBoss` | 2546 | 105 | 41 | 40 |
| `Board_Arena` | 2037 | 275 | 124 | 33 |
| `Tab_Boss` | 1970 | 6 | 0 | 30 |
| `Board_Maps` | 1963 | 260 | 137 | 34 |
| `Board_Players` | 1817 | 190 | 73 | 29 |
| `Board_BattlePass` | 1698 | 241 | 65 | 17 |
| `Board_Ranks` | 1447 | 215 | 87 | 22 |
| `Board_Ranks` | 1431 | 229 | 92 | 23 |
| `Board_Survival` | 1387 | 206 | 85 | 23 |
| `Board_Survival` | 1371 | 210 | 85 | 22 |
| `Board_Drones` | 1100 | 138 | 61 | 18 |
| `Board_BattlePassPro` | 1013 | 128 | 42 | 15 |
| `Board_TechLab` | 989 | 114 | 51 | 16 |
| `Board_WinnerBenefits` | 988 | 141 | 56 | 15 |
| `Popup_WatchVideos` | 929 | 170 | 48 | 13 |
| `Board_Begin` | 910 | 125 | 50 | 15 |
| `Board_Reborn` | 896 | 147 | 59 | 15 |
| `Board_Combo` | 891 | 89 | 52 | 13 |
| `Board_GiftLogin` | 867 | 128 | 28 | 13 |
| `Popup_WatchVideos` | 851 | 159 | 45 | 13 |
| `Board_UserProfile` | 757 | 59 | 48 | 11 |
| `Board_Endgame` | 754 | 92 | 43 | 14 |
| `Board_Challange` | 742 | 132 | 54 | 12 |
| `Board_Vip` | 732 | 104 | 27 | 11 |
| `Board_Stage` | 687 | 123 | 52 | 11 |
| `Popup_ShipSalePack` | 686 | 15 | 7 | 10 |
| `Board_QuestRewards` | 651 | 73 | 25 | 9 |
| `Board_Setting` | 633 | 81 | 45 | 10 |
| `Tab_Boss` | 529 | 7 | 1 | 7 |
| `Board_MiniCombo` | 529 | 58 | 22 | 8 |
| `Popup_HolidayGift` | 527 | 67 | 11 | 7 |
| `Board_ShopEnergy` | 517 | 97 | 30 | 9 |
| `Popup_HolidayGift` | 500 | 78 | 11 | 7 |
| `Board_EventSeasonPass` | 489 | 84 | 27 | 8 |
| `Popup_WeekSales` | 484 | 64 | 14 | 6 |
| `Board_EventSeasonPass` | 430 | 64 | 19 | 6 |
| `Popup_PvPRankings` | 418 | 55 | 19 | 7 |

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
