# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **745**
- tổng node: **105992**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (48)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91891 |
| `SpriteRenderer` | 49897 |
| `MeshRenderer` | 15577 |
| `RectTransform` | 14101 |
| `TextMeshPro` | 14024 |
| `MeshFilter` | 12841 |
| `BoxCollider2D` | 7495 |
| `Animator` | 5383 |
| `ButtonEvents` | 5160 |
| `Button_Sound` | 5012 |
| `ParticleSystem` | 3799 |
| `ParticleSystemRenderer` | 3799 |
| `LanguageTextMeshPro` | 3591 |
| `ChangeSorting` | 2254 |
| `BgObjectScaler` | 1667 |
| `Popup_Notices` | 1282 |
| `Box_Rewards` | 1212 |
| `TMP_SubMesh` | 1062 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 707 |
| `FixUIShop` | 640 |
| `Rigidbody2D` | 349 |
| `ObjectPool` | 339 |
| `LineRenderer` | 287 |
| `Enemy_Datas` | 285 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 453 | 334 | 61 |
| `Board_Shop` | 3425 | 548 | 162 | 46 |
| `Board_FightBoss` | 2537 | 122 | 45 | 40 |
| `Board_PVP` | 2532 | 349 | 163 | 38 |
| `Board_SelectBoss` | 2052 | 99 | 16 | 29 |
| `Tab_Boss` | 1924 | 6 | 0 | 30 |
| `Board_Arena` | 1814 | 212 | 115 | 29 |
| `Board_Players` | 1666 | 185 | 75 | 28 |
| `Board_BattlePass` | 1604 | 231 | 62 | 17 |
| `Board_TechLab` | 1451 | 177 | 75 | 20 |
| `Board_Ranks` | 1272 | 203 | 85 | 20 |
| `Board_Survival` | 1261 | 173 | 80 | 21 |
| `Board_Ranks` | 1146 | 185 | 82 | 20 |
| `Board_Survival` | 1114 | 198 | 83 | 19 |
| `Board_Begin` | 1064 | 135 | 52 | 17 |
| `Board_Drones` | 1004 | 131 | 60 | 16 |
| `Popup_WatchVideos` | 951 | 161 | 49 | 13 |
| `Board_WinnerBenefits` | 916 | 151 | 57 | 14 |
| `Board_Combo` | 900 | 86 | 50 | 13 |
| `Popup_WatchVideos` | 895 | 160 | 50 | 13 |
| `Board_BattlePassPro` | 890 | 121 | 37 | 13 |
| `Board_Setting` | 882 | 95 | 61 | 13 |
| `Board_GiftLogin` | 867 | 132 | 27 | 13 |
| `Board_Endgame` | 861 | 124 | 50 | 15 |
| `Board_Reborn` | 786 | 135 | 58 | 14 |
| `Board_Challange` | 754 | 128 | 51 | 12 |
| `Board_Stage` | 730 | 129 | 47 | 11 |
| `Board_UserProfile` | 723 | 60 | 48 | 10 |
| `Board_QuestRewards` | 611 | 81 | 23 | 9 |
| `Board_Vip` | 580 | 84 | 26 | 9 |
| `Tab_Boss` | 561 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 548 | 86 | 29 | 9 |
| `Popup_ShipSalePack` | 539 | 16 | 7 | 8 |
| `Popup_HolidayGift` | 530 | 68 | 11 | 7 |
| `Popup_HolidayGift` | 529 | 78 | 11 | 7 |
| `Board_EventSeasonPass` | 513 | 74 | 22 | 8 |
| `Board_ShopEnergy` | 478 | 102 | 32 | 8 |
| `Board_MiniCombo` | 471 | 55 | 21 | 8 |
| `Popup_PvPRankings` | 396 | 47 | 18 | 7 |
| `Popup_WatchVideosOld` | 384 | 62 | 13 | 5 |

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
