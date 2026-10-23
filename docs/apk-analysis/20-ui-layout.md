# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **730**
- tổng node: **103556**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (63)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90102 |
| `SpriteRenderer` | 48694 |
| `MeshRenderer` | 14896 |
| `RectTransform` | 13454 |
| `TextMeshPro` | 13392 |
| `MeshFilter` | 12204 |
| `BoxCollider2D` | 7264 |
| `Animator` | 5325 |
| `ButtonEvents` | 4978 |
| `Button_Sound` | 4842 |
| `ParticleSystem` | 3785 |
| `ParticleSystemRenderer` | 3785 |
| `LanguageTextMeshPro` | 3555 |
| `ChangeSorting` | 2204 |
| `BgObjectScaler` | 1621 |
| `Popup_Notices` | 1253 |
| `Box_Rewards` | 1185 |
| `TMP_SubMesh` | 987 |
| `UIObjectAnchors` | 743 |
| `Shop_Cell` | 657 |
| `FixUIShop` | 600 |
| `Rigidbody2D` | 392 |
| `ObjectPool` | 366 |
| `LineRenderer` | 311 |
| `Enemy_Datas` | 309 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 441 | 342 | 61 |
| `Board_Shop` | 3510 | 561 | 169 | 48 |
| `Board_FightBoss` | 2638 | 110 | 40 | 42 |
| `Board_PVP` | 2621 | 373 | 167 | 39 |
| `Board_SelectBoss` | 2117 | 92 | 15 | 30 |
| `Tab_Boss` | 2035 | 5 | 0 | 31 |
| `Board_Arena` | 1820 | 220 | 108 | 30 |
| `Board_Players` | 1704 | 190 | 74 | 29 |
| `Board_BattlePass` | 1669 | 225 | 66 | 17 |
| `Board_Ranks` | 1428 | 190 | 90 | 22 |
| `Board_TechLab` | 1404 | 173 | 75 | 20 |
| `Board_Ranks` | 1370 | 201 | 90 | 22 |
| `Board_Survival` | 1065 | 178 | 79 | 19 |
| `Board_Survival` | 1039 | 180 | 78 | 17 |
| `Board_Drones` | 1039 | 133 | 61 | 17 |
| `Board_Begin` | 992 | 132 | 52 | 16 |
| `Board_WinnerBenefits` | 979 | 130 | 54 | 14 |
| `Board_BattlePassPro` | 924 | 126 | 42 | 14 |
| `Board_GiftLogin` | 908 | 129 | 28 | 13 |
| `Popup_WatchVideos` | 877 | 148 | 47 | 13 |
| `Board_Endgame` | 821 | 124 | 49 | 15 |
| `Board_Stage` | 811 | 130 | 54 | 12 |
| `Board_Setting` | 790 | 82 | 48 | 12 |
| `Board_Reborn` | 786 | 125 | 57 | 14 |
| `Popup_WatchVideos` | 778 | 150 | 43 | 12 |
| `Board_Challange` | 752 | 120 | 47 | 12 |
| `Board_QuestRewards` | 703 | 99 | 27 | 10 |
| `Board_MiniCombo` | 680 | 72 | 38 | 10 |
| `Board_Vip` | 641 | 42 | 17 | 8 |
| `Board_UserProfile` | 580 | 56 | 48 | 9 |
| `Board_EventSeasonPass` | 560 | 89 | 29 | 10 |
| `Popup_ShipSalePack` | 549 | 14 | 5 | 8 |
| `Popup_HolidayGift` | 528 | 71 | 11 | 7 |
| `Board_EventSeasonPass` | 502 | 71 | 22 | 7 |
| `Board_ShopEnergy` | 486 | 96 | 33 | 8 |
| `Popup_HolidayGift` | 484 | 68 | 11 | 7 |
| `Board_Combo` | 449 | 57 | 22 | 7 |
| `Tab_Boss` | 419 | 8 | 1 | 6 |
| `Board_Begin` | 389 | 33 | 13 | 5 |
| `Popup_PvPRankings` | 376 | 47 | 16 | 7 |

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
