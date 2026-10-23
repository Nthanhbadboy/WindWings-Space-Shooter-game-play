# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **720**
- tổng node: **105712**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (73)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91824 |
| `SpriteRenderer` | 49745 |
| `MeshRenderer` | 15385 |
| `RectTransform` | 13888 |
| `TextMeshPro` | 13820 |
| `MeshFilter` | 12508 |
| `BoxCollider2D` | 7440 |
| `Animator` | 5490 |
| `ButtonEvents` | 5141 |
| `Button_Sound` | 4988 |
| `ParticleSystem` | 3815 |
| `ParticleSystemRenderer` | 3815 |
| `LanguageTextMeshPro` | 3579 |
| `ChangeSorting` | 2212 |
| `BgObjectScaler` | 1631 |
| `Popup_Notices` | 1250 |
| `Box_Rewards` | 1224 |
| `TMP_SubMesh` | 1043 |
| `UIObjectAnchors` | 749 |
| `Shop_Cell` | 688 |
| `FixUIShop` | 627 |
| `Rigidbody2D` | 405 |
| `ObjectPool` | 377 |
| `Enemy_Datas` | 328 |
| `Enemy_Health` | 328 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 440 | 341 | 61 |
| `Board_Shop` | 3538 | 582 | 170 | 48 |
| `Board_SelectBoss` | 2413 | 109 | 16 | 33 |
| `Board_PVP` | 2370 | 347 | 162 | 34 |
| `Board_FightBoss` | 2365 | 110 | 42 | 38 |
| `Board_Arena` | 1906 | 279 | 115 | 31 |
| `Board_BattlePass` | 1717 | 233 | 68 | 17 |
| `Tab_Boss` | 1658 | 6 | 0 | 26 |
| `Board_Players` | 1576 | 134 | 68 | 26 |
| `Board_Ranks` | 1396 | 193 | 81 | 22 |
| `Board_Survival` | 1387 | 204 | 86 | 23 |
| `Board_TechLab` | 1364 | 159 | 79 | 19 |
| `Board_Ranks` | 1333 | 222 | 93 | 22 |
| `Board_Survival` | 1248 | 200 | 80 | 20 |
| `Board_Combo` | 1005 | 100 | 58 | 15 |
| `Board_Begin` | 995 | 145 | 52 | 16 |
| `Board_BattlePassPro` | 982 | 131 | 42 | 15 |
| `Popup_WatchVideos` | 950 | 155 | 50 | 13 |
| `Popup_WatchVideos` | 950 | 165 | 49 | 13 |
| `Board_WinnerBenefits` | 908 | 156 | 52 | 14 |
| `Board_Endgame` | 908 | 128 | 52 | 16 |
| `Board_Reborn` | 844 | 157 | 59 | 15 |
| `Board_Setting` | 815 | 99 | 65 | 12 |
| `Board_MiniCombo` | 814 | 88 | 46 | 12 |
| `Board_Challange` | 811 | 133 | 53 | 13 |
| `Board_Stage` | 806 | 140 | 52 | 12 |
| `Board_GiftLogin` | 793 | 126 | 28 | 12 |
| `Board_Drones` | 748 | 85 | 47 | 13 |
| `Popup_ShipSalePack` | 744 | 17 | 7 | 11 |
| `Board_Vip` | 738 | 96 | 27 | 11 |
| `Board_QuestRewards` | 655 | 87 | 26 | 9 |
| `Board_EventSeasonPass` | 583 | 86 | 27 | 10 |
| `Tab_Boss` | 579 | 9 | 1 | 8 |
| `Board_ShopEnergy` | 576 | 92 | 32 | 9 |
| `Popup_HolidayGift` | 541 | 68 | 10 | 7 |
| `Popup_HolidayGift` | 534 | 73 | 9 | 7 |
| `Board_EventSeasonPass` | 446 | 74 | 22 | 7 |
| `Popup_PvPRankings` | 384 | 36 | 16 | 6 |
| `Popup_WatchVideosOld` | 374 | 60 | 13 | 5 |
| `Board_Begin` | 373 | 34 | 15 | 5 |

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
