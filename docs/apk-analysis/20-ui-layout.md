# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **743**
- tổng node: **105985**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (50)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92022 |
| `SpriteRenderer` | 49769 |
| `MeshRenderer` | 15438 |
| `RectTransform` | 13963 |
| `TextMeshPro` | 13882 |
| `MeshFilter` | 12635 |
| `BoxCollider2D` | 7504 |
| `Animator` | 5406 |
| `ButtonEvents` | 5144 |
| `Button_Sound` | 5000 |
| `ParticleSystem` | 3850 |
| `ParticleSystemRenderer` | 3850 |
| `LanguageTextMeshPro` | 3664 |
| `ChangeSorting` | 2234 |
| `BgObjectScaler` | 1646 |
| `Popup_Notices` | 1273 |
| `Box_Rewards` | 1205 |
| `TMP_SubMesh` | 1042 |
| `UIObjectAnchors` | 745 |
| `Shop_Cell` | 689 |
| `FixUIShop` | 625 |
| `ObjectPool` | 377 |
| `Rigidbody2D` | 373 |
| `Enemy_Datas` | 328 |
| `Enemy_Health` | 328 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 432 | 334 | 62 |
| `Board_Shop` | 3569 | 557 | 160 | 48 |
| `Board_PVP` | 2718 | 394 | 167 | 39 |
| `Board_FightBoss` | 2439 | 107 | 40 | 39 |
| `Board_SelectBoss` | 2313 | 99 | 17 | 32 |
| `Board_Players` | 1915 | 206 | 78 | 31 |
| `Tab_Boss` | 1839 | 6 | 0 | 28 |
| `Board_BattlePass` | 1721 | 238 | 63 | 18 |
| `Board_Arena` | 1500 | 194 | 106 | 24 |
| `Board_Ranks` | 1487 | 209 | 83 | 23 |
| `Board_Ranks` | 1399 | 231 | 91 | 23 |
| `Board_Survival` | 1358 | 202 | 86 | 22 |
| `Board_TechLab` | 1199 | 137 | 73 | 17 |
| `Board_Survival` | 1148 | 184 | 85 | 19 |
| `Board_Drones` | 953 | 119 | 57 | 16 |
| `Board_BattlePassPro` | 925 | 124 | 42 | 14 |
| `Board_Begin` | 919 | 118 | 49 | 15 |
| `Board_Reborn` | 912 | 153 | 62 | 16 |
| `Popup_WatchVideos` | 862 | 155 | 48 | 13 |
| `Board_GiftLogin` | 843 | 116 | 26 | 12 |
| `Board_Setting` | 821 | 97 | 62 | 12 |
| `Popup_WatchVideos` | 815 | 154 | 43 | 12 |
| `Board_Challange` | 806 | 150 | 54 | 13 |
| `Board_WinnerBenefits` | 798 | 131 | 53 | 13 |
| `Board_Endgame` | 780 | 103 | 49 | 13 |
| `Board_MiniCombo` | 774 | 89 | 45 | 13 |
| `Board_Stage` | 751 | 135 | 50 | 12 |
| `Board_Vip` | 721 | 95 | 26 | 11 |
| `Board_QuestRewards` | 612 | 86 | 27 | 9 |
| `Board_ShopEnergy` | 579 | 100 | 34 | 9 |
| `Popup_HolidayGift` | 557 | 65 | 11 | 7 |
| `Tab_Boss` | 539 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 532 | 73 | 10 | 7 |
| `Board_EventSeasonPass` | 483 | 82 | 23 | 9 |
| `Popup_ShipSalePack` | 461 | 15 | 7 | 7 |
| `Board_Combo` | 457 | 65 | 21 | 7 |
| `Popup_WeekSales` | 437 | 54 | 14 | 6 |
| `Board_UserProfile` | 386 | 44 | 47 | 7 |
| `Board_Quest` | 370 | 102 | 39 | 5 |
| `Board_EventSeasonPass` | 369 | 62 | 19 | 6 |

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
