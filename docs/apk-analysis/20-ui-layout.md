# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **743**
- tổng node: **107022**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (50)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 93006 |
| `SpriteRenderer` | 50419 |
| `MeshRenderer` | 15505 |
| `RectTransform` | 14016 |
| `TextMeshPro` | 13950 |
| `MeshFilter` | 12607 |
| `BoxCollider2D` | 7529 |
| `Animator` | 5500 |
| `ButtonEvents` | 5194 |
| `Button_Sound` | 5046 |
| `ParticleSystem` | 3925 |
| `ParticleSystemRenderer` | 3925 |
| `LanguageTextMeshPro` | 3620 |
| `ChangeSorting` | 2239 |
| `BgObjectScaler` | 1643 |
| `Popup_Notices` | 1271 |
| `Box_Rewards` | 1245 |
| `TMP_SubMesh` | 1040 |
| `UIObjectAnchors` | 754 |
| `Shop_Cell` | 692 |
| `FixUIShop` | 624 |
| `Rigidbody2D` | 385 |
| `ObjectPool` | 383 |
| `Enemy_Datas` | 328 |
| `Enemy_Health` | 328 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 427 | 342 | 60 |
| `Board_Shop` | 3272 | 534 | 156 | 45 |
| `Board_FightBoss` | 2599 | 120 | 46 | 41 |
| `Board_SelectBoss` | 2565 | 106 | 15 | 35 |
| `Board_PVP` | 2438 | 373 | 164 | 37 |
| `Board_Arena` | 2059 | 270 | 125 | 33 |
| `Board_Players` | 1808 | 177 | 73 | 29 |
| `Tab_Boss` | 1681 | 4 | 0 | 26 |
| `Board_BattlePass` | 1666 | 226 | 63 | 18 |
| `Board_Ranks` | 1513 | 226 | 88 | 23 |
| `Board_Survival` | 1377 | 201 | 84 | 22 |
| `Board_Ranks` | 1319 | 203 | 90 | 22 |
| `Board_Survival` | 1317 | 193 | 87 | 21 |
| `Board_TechLab` | 1107 | 142 | 66 | 17 |
| `Board_Begin` | 1046 | 140 | 51 | 17 |
| `Board_Drones` | 1011 | 133 | 59 | 17 |
| `Board_BattlePassPro` | 917 | 117 | 42 | 14 |
| `Board_WinnerBenefits` | 914 | 140 | 55 | 14 |
| `Popup_WatchVideos` | 910 | 168 | 48 | 13 |
| `Board_Combo` | 908 | 88 | 58 | 13 |
| `Popup_WatchVideos` | 881 | 152 | 47 | 13 |
| `Board_Reborn` | 878 | 145 | 59 | 15 |
| `Board_Challange` | 836 | 143 | 51 | 13 |
| `Board_MiniCombo` | 811 | 88 | 44 | 12 |
| `Board_GiftLogin` | 801 | 130 | 27 | 12 |
| `Board_Stage` | 784 | 133 | 48 | 12 |
| `Board_Vip` | 766 | 89 | 26 | 11 |
| `Board_UserProfile` | 761 | 60 | 50 | 11 |
| `Board_Endgame` | 724 | 116 | 50 | 13 |
| `Board_Setting` | 707 | 99 | 65 | 11 |
| `Board_QuestRewards` | 670 | 89 | 26 | 10 |
| `Popup_ShipSalePack` | 608 | 19 | 7 | 9 |
| `Board_ShopEnergy` | 545 | 103 | 34 | 9 |
| `Board_EventSeasonPass` | 541 | 94 | 28 | 9 |
| `Popup_HolidayGift` | 538 | 77 | 11 | 8 |
| `Tab_Boss` | 534 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 517 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 456 | 74 | 22 | 7 |
| `Popup_WeekSales` | 432 | 57 | 14 | 6 |
| `Board_Begin` | 375 | 33 | 15 | 5 |

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
