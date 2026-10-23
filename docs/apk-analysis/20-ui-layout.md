# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **747**
- tổng node: **106868**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (46)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92881 |
| `SpriteRenderer` | 50271 |
| `MeshRenderer` | 15520 |
| `RectTransform` | 13987 |
| `TextMeshPro` | 13914 |
| `MeshFilter` | 12681 |
| `BoxCollider2D` | 7540 |
| `Animator` | 5434 |
| `ButtonEvents` | 5198 |
| `Button_Sound` | 5042 |
| `ParticleSystem` | 3915 |
| `ParticleSystemRenderer` | 3915 |
| `LanguageTextMeshPro` | 3623 |
| `ChangeSorting` | 2236 |
| `BgObjectScaler` | 1661 |
| `Popup_Notices` | 1277 |
| `Box_Rewards` | 1210 |
| `TMP_SubMesh` | 1065 |
| `UIObjectAnchors` | 751 |
| `Shop_Cell` | 697 |
| `FixUIShop` | 634 |
| `Rigidbody2D` | 392 |
| `ObjectPool` | 376 |
| `Enemy_Datas` | 320 |
| `Enemy_Health` | 320 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 428 | 335 | 61 |
| `Board_Shop` | 3580 | 620 | 168 | 49 |
| `Board_FightBoss` | 2507 | 116 | 46 | 39 |
| `Board_PVP` | 2497 | 336 | 166 | 37 |
| `Board_SelectBoss` | 2292 | 101 | 17 | 33 |
| `Tab_Boss` | 1870 | 5 | 0 | 29 |
| `Board_Arena` | 1838 | 256 | 122 | 30 |
| `Board_BattlePass` | 1783 | 246 | 63 | 18 |
| `Board_Players` | 1741 | 174 | 71 | 29 |
| `Board_Ranks` | 1536 | 201 | 91 | 23 |
| `Board_Ranks` | 1353 | 179 | 91 | 21 |
| `Board_Survival` | 1311 | 201 | 86 | 22 |
| `Board_Survival` | 1177 | 157 | 80 | 19 |
| `Board_TechLab` | 1103 | 138 | 62 | 17 |
| `Board_Drones` | 1052 | 138 | 59 | 17 |
| `Board_WinnerBenefits` | 1028 | 156 | 55 | 15 |
| `Board_BattlePassPro` | 999 | 125 | 38 | 15 |
| `Board_Combo` | 989 | 104 | 60 | 15 |
| `Board_Begin` | 985 | 138 | 45 | 14 |
| `Popup_WatchVideos` | 896 | 176 | 50 | 13 |
| `Popup_WatchVideos` | 890 | 151 | 47 | 13 |
| `Board_GiftLogin` | 863 | 127 | 28 | 13 |
| `Board_Endgame` | 823 | 125 | 49 | 14 |
| `Board_Reborn` | 808 | 148 | 58 | 14 |
| `Board_Setting` | 807 | 98 | 64 | 12 |
| `Board_Vip` | 762 | 96 | 27 | 11 |
| `Board_Stage` | 702 | 97 | 49 | 11 |
| `Board_QuestRewards` | 692 | 105 | 27 | 10 |
| `Popup_ShipSalePack` | 679 | 17 | 7 | 9 |
| `Board_Challange` | 670 | 133 | 51 | 12 |
| `Board_ShopEnergy` | 593 | 101 | 35 | 9 |
| `Tab_Boss` | 570 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 567 | 78 | 11 | 8 |
| `Popup_HolidayGift` | 540 | 65 | 10 | 7 |
| `Board_EventSeasonPass` | 528 | 73 | 21 | 8 |
| `Board_EventSeasonPass` | 508 | 84 | 24 | 9 |
| `Board_MiniCombo` | 469 | 55 | 22 | 7 |
| `Board_UserProfile` | 429 | 49 | 47 | 7 |
| `Popup_WeekSales` | 429 | 54 | 13 | 6 |
| `Board_Begin` | 394 | 33 | 15 | 5 |

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
