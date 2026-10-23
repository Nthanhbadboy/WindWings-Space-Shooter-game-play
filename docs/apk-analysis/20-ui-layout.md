# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **726**
- tổng node: **104902**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (67)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90937 |
| `SpriteRenderer` | 49510 |
| `MeshRenderer` | 15417 |
| `RectTransform` | 13965 |
| `TextMeshPro` | 13897 |
| `MeshFilter` | 12591 |
| `BoxCollider2D` | 7359 |
| `Animator` | 5455 |
| `ButtonEvents` | 5071 |
| `Button_Sound` | 4932 |
| `ParticleSystem` | 3691 |
| `ParticleSystemRenderer` | 3691 |
| `LanguageTextMeshPro` | 3614 |
| `ChangeSorting` | 2225 |
| `BgObjectScaler` | 1627 |
| `Popup_Notices` | 1253 |
| `Box_Rewards` | 1213 |
| `TMP_SubMesh` | 1032 |
| `UIObjectAnchors` | 755 |
| `Shop_Cell` | 670 |
| `FixUIShop` | 620 |
| `Rigidbody2D` | 359 |
| `ObjectPool` | 321 |
| `LineRenderer` | 306 |
| `Enemy_Datas` | 266 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 443 | 338 | 60 |
| `Board_Shop` | 3416 | 536 | 168 | 47 |
| `Board_PVP` | 2811 | 416 | 164 | 42 |
| `Board_FightBoss` | 2241 | 102 | 43 | 36 |
| `Board_SelectBoss` | 1817 | 100 | 15 | 26 |
| `Board_Players` | 1776 | 185 | 74 | 30 |
| `Board_Arena` | 1737 | 188 | 102 | 28 |
| `Board_BattlePass` | 1700 | 236 | 67 | 17 |
| `Tab_Boss` | 1607 | 6 | 0 | 25 |
| `Board_Ranks` | 1410 | 201 | 90 | 22 |
| `Board_TechLab` | 1401 | 157 | 79 | 19 |
| `Board_Ranks` | 1270 | 215 | 83 | 20 |
| `Board_Survival` | 1200 | 168 | 83 | 19 |
| `Board_Survival` | 1074 | 132 | 77 | 18 |
| `Board_Begin` | 1027 | 141 | 56 | 16 |
| `Board_Drones` | 981 | 116 | 56 | 17 |
| `Board_BattlePassPro` | 960 | 124 | 40 | 15 |
| `Board_WinnerBenefits` | 925 | 130 | 53 | 13 |
| `Board_Endgame` | 886 | 133 | 53 | 16 |
| `Popup_WatchVideos` | 877 | 153 | 45 | 13 |
| `Popup_WatchVideos` | 859 | 150 | 43 | 13 |
| `Board_Reborn` | 830 | 140 | 57 | 14 |
| `Board_Setting` | 830 | 102 | 65 | 12 |
| `Board_GiftLogin` | 810 | 117 | 25 | 12 |
| `Board_Stage` | 798 | 120 | 52 | 13 |
| `Board_Combo` | 720 | 84 | 36 | 11 |
| `Popup_ShipSalePack` | 693 | 18 | 7 | 10 |
| `Board_QuestRewards` | 648 | 94 | 25 | 9 |
| `Board_Challange` | 645 | 134 | 52 | 11 |
| `Board_Vip` | 615 | 85 | 24 | 9 |
| `Board_EventSeasonPass` | 583 | 92 | 29 | 10 |
| `Board_MiniCombo` | 574 | 81 | 31 | 10 |
| `Board_ShopEnergy` | 571 | 106 | 33 | 9 |
| `Tab_Boss` | 558 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 505 | 63 | 9 | 6 |
| `Popup_HolidayGift` | 499 | 65 | 10 | 7 |
| `Popup_WeekSales` | 493 | 65 | 14 | 6 |
| `Board_EventSeasonPass` | 447 | 71 | 20 | 7 |
| `Board_Begin` | 400 | 36 | 14 | 5 |
| `Board_Profile` | 377 | 26 | 16 | 5 |

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
