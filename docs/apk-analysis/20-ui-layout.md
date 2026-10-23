# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **593**
- tổng node: **89184**
- dung lượng thô (gz): **1.7 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 77669 |
| `SpriteRenderer` | 42054 |
| `MeshRenderer` | 12740 |
| `RectTransform` | 11515 |
| `TextMeshPro` | 11467 |
| `MeshFilter` | 10405 |
| `BoxCollider2D` | 6143 |
| `Animator` | 4609 |
| `ButtonEvents` | 4266 |
| `Button_Sound` | 4146 |
| `ParticleSystem` | 3322 |
| `ParticleSystemRenderer` | 3322 |
| `LanguageTextMeshPro` | 2913 |
| `ChangeSorting` | 1824 |
| `BgObjectScaler` | 1329 |
| `Popup_Notices` | 1044 |
| `Box_Rewards` | 1019 |
| `TMP_SubMesh` | 843 |
| `UIObjectAnchors` | 625 |
| `Shop_Cell` | 568 |
| `FixUIShop` | 528 |
| `Rigidbody2D` | 384 |
| `ObjectPool` | 353 |
| `Enemy_Datas` | 302 |
| `Enemy_Health` | 302 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 448 | 345 | 61 |
| `Board_Shop` | 2704 | 430 | 125 | 39 |
| `Board_PVP` | 2680 | 377 | 163 | 40 |
| `Board_FightBoss` | 2543 | 119 | 44 | 40 |
| `Board_SelectBoss` | 2501 | 109 | 17 | 34 |
| `Board_Arena` | 2048 | 267 | 122 | 32 |
| `Tab_Boss` | 1839 | 6 | 0 | 28 |
| `Board_Players` | 1774 | 188 | 73 | 30 |
| `Board_BattlePass` | 1729 | 250 | 63 | 18 |
| `Board_Ranks` | 1428 | 241 | 92 | 23 |
| `Board_Survival` | 1289 | 165 | 86 | 21 |
| `Board_Survival` | 1271 | 160 | 83 | 21 |
| `Board_TechLab` | 1196 | 133 | 55 | 17 |
| `Board_Drones` | 1022 | 138 | 62 | 17 |
| `Board_Begin` | 974 | 131 | 49 | 16 |
| `Board_Combo` | 950 | 95 | 56 | 13 |
| `Board_BattlePassPro` | 933 | 127 | 41 | 14 |
| `Popup_WatchVideos` | 900 | 158 | 49 | 13 |
| `Popup_WatchVideos` | 898 | 167 | 48 | 13 |
| `Board_MiniCombo` | 875 | 87 | 52 | 13 |
| `Board_WinnerBenefits` | 874 | 143 | 57 | 14 |
| `Board_Challange` | 866 | 148 | 54 | 13 |
| `Board_Vip` | 777 | 104 | 27 | 11 |
| `Board_Stage` | 749 | 140 | 52 | 12 |
| `Board_GiftLogin` | 733 | 106 | 24 | 11 |
| `Popup_ShipSalePack` | 653 | 18 | 5 | 9 |
| `Board_UserProfile` | 626 | 63 | 48 | 10 |
| `Board_QuestRewards` | 594 | 96 | 25 | 9 |
| `Board_ShopEnergy` | 592 | 97 | 33 | 9 |
| `Board_EventSeasonPass` | 561 | 94 | 28 | 10 |
| `Popup_HolidayGift` | 533 | 64 | 11 | 7 |
| `Tab_Boss` | 532 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 499 | 70 | 10 | 7 |
| `Board_EventSeasonPass` | 410 | 64 | 19 | 6 |
| `Popup_PvPRankings` | 404 | 50 | 16 | 7 |
| `Board_Profile` | 389 | 26 | 16 | 5 |
| `Board_Profile` | 383 | 27 | 16 | 5 |
| `Board_Quest` | 360 | 105 | 39 | 5 |
| `Board_Begin` | 355 | 29 | 15 | 5 |
| `Popup_BuyMoreGems` | 352 | 66 | 15 | 5 |

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
