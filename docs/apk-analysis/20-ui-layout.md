# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **742**
- tổng node: **105377**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (51)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91405 |
| `SpriteRenderer` | 49764 |
| `MeshRenderer` | 15466 |
| `RectTransform` | 13972 |
| `TextMeshPro` | 13904 |
| `MeshFilter` | 12631 |
| `BoxCollider2D` | 7490 |
| `Animator` | 5275 |
| `ButtonEvents` | 5197 |
| `Button_Sound` | 5053 |
| `LanguageTextMeshPro` | 3616 |
| `ParticleSystem` | 3570 |
| `ParticleSystemRenderer` | 3570 |
| `ChangeSorting` | 2231 |
| `BgObjectScaler` | 1643 |
| `Popup_Notices` | 1268 |
| `Box_Rewards` | 1194 |
| `TMP_SubMesh` | 1045 |
| `UIObjectAnchors` | 758 |
| `Shop_Cell` | 698 |
| `FixUIShop` | 629 |
| `ObjectPool` | 339 |
| `Rigidbody2D` | 309 |
| `Enemy_Datas` | 286 |
| `Enemy_Health` | 286 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 440 | 343 | 61 |
| `Board_Shop` | 3564 | 604 | 168 | 48 |
| `Board_PVP` | 2833 | 386 | 171 | 42 |
| `Board_FightBoss` | 2620 | 125 | 45 | 41 |
| `Board_SelectBoss` | 1823 | 99 | 17 | 26 |
| `Board_Arena` | 1757 | 238 | 112 | 28 |
| `Tab_Boss` | 1705 | 6 | 0 | 27 |
| `Board_Ranks` | 1565 | 231 | 91 | 24 |
| `Board_Ranks` | 1522 | 216 | 88 | 24 |
| `Board_BattlePass` | 1476 | 217 | 57 | 16 |
| `Board_Survival` | 1235 | 178 | 87 | 21 |
| `Board_TechLab` | 1195 | 142 | 69 | 18 |
| `Board_Players` | 1191 | 183 | 74 | 21 |
| `Board_Drones` | 1095 | 144 | 61 | 18 |
| `Board_Survival` | 1064 | 180 | 79 | 18 |
| `Board_Setting` | 980 | 114 | 66 | 14 |
| `Board_BattlePassPro` | 947 | 115 | 35 | 14 |
| `Popup_WatchVideos` | 942 | 165 | 50 | 13 |
| `Board_Begin` | 929 | 129 | 50 | 15 |
| `Board_WinnerBenefits` | 914 | 148 | 57 | 14 |
| `Board_Endgame` | 871 | 126 | 53 | 16 |
| `Board_Reborn` | 859 | 135 | 58 | 15 |
| `Board_Challange` | 854 | 150 | 55 | 13 |
| `Board_Combo` | 827 | 95 | 48 | 13 |
| `Popup_WatchVideos` | 787 | 144 | 44 | 12 |
| `Board_Stage` | 762 | 115 | 52 | 12 |
| `Board_Vip` | 754 | 97 | 25 | 11 |
| `Board_MiniCombo` | 753 | 88 | 37 | 12 |
| `Board_GiftLogin` | 752 | 119 | 28 | 12 |
| `Board_QuestRewards` | 720 | 99 | 26 | 10 |
| `Board_UserProfile` | 588 | 54 | 50 | 9 |
| `Tab_Boss` | 577 | 9 | 1 | 8 |
| `Board_ShopEnergy` | 577 | 98 | 29 | 9 |
| `Board_EventSeasonPass` | 570 | 90 | 26 | 9 |
| `Popup_ShipSalePack` | 518 | 17 | 6 | 8 |
| `Popup_HolidayGift` | 516 | 76 | 9 | 7 |
| `Board_EventSeasonPass` | 489 | 73 | 22 | 7 |
| `Popup_HolidayGift` | 470 | 63 | 11 | 7 |
| `Popup_PvPRankings` | 416 | 50 | 19 | 7 |
| `Board_Begin` | 395 | 33 | 14 | 5 |

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
