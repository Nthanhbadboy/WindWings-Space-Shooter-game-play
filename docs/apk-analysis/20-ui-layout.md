# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **736**
- tổng node: **103930**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (57)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90485 |
| `SpriteRenderer` | 49022 |
| `MeshRenderer` | 14849 |
| `RectTransform` | 13445 |
| `TextMeshPro` | 13373 |
| `MeshFilter` | 12121 |
| `BoxCollider2D` | 7308 |
| `Animator` | 5388 |
| `ButtonEvents` | 5001 |
| `Button_Sound` | 4858 |
| `ParticleSystem` | 3784 |
| `ParticleSystemRenderer` | 3784 |
| `LanguageTextMeshPro` | 3581 |
| `ChangeSorting` | 2205 |
| `BgObjectScaler` | 1627 |
| `Popup_Notices` | 1259 |
| `Box_Rewards` | 1220 |
| `TMP_SubMesh` | 972 |
| `UIObjectAnchors` | 747 |
| `Shop_Cell` | 616 |
| `FixUIShop` | 589 |
| `Rigidbody2D` | 396 |
| `ObjectPool` | 373 |
| `Enemy_Datas` | 322 |
| `Enemy_Health` | 322 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 428 | 328 | 62 |
| `Board_Shop` | 3672 | 594 | 164 | 51 |
| `Board_FightBoss` | 2503 | 118 | 44 | 40 |
| `Board_PVP` | 2422 | 335 | 144 | 38 |
| `Board_SelectBoss` | 2294 | 109 | 15 | 30 |
| `Tab_Boss` | 1915 | 6 | 0 | 29 |
| `Board_Players` | 1719 | 190 | 74 | 29 |
| `Board_BattlePass` | 1665 | 222 | 60 | 18 |
| `Board_Arena` | 1610 | 162 | 93 | 28 |
| `Board_Survival` | 1453 | 219 | 83 | 23 |
| `Board_Ranks` | 1403 | 197 | 90 | 22 |
| `Board_Survival` | 1241 | 138 | 76 | 19 |
| `Board_Ranks` | 1202 | 166 | 74 | 19 |
| `Board_TechLab` | 1143 | 140 | 58 | 17 |
| `Board_Combo` | 999 | 110 | 60 | 14 |
| `Board_Begin` | 942 | 123 | 52 | 16 |
| `Board_Drones` | 933 | 128 | 58 | 16 |
| `Board_BattlePassPro` | 920 | 120 | 40 | 14 |
| `Popup_WatchVideos` | 892 | 165 | 46 | 13 |
| `Board_Endgame` | 876 | 122 | 50 | 15 |
| `Board_Challange` | 837 | 151 | 54 | 13 |
| `Board_WinnerBenefits` | 827 | 97 | 47 | 12 |
| `Popup_WatchVideos` | 818 | 159 | 47 | 12 |
| `Board_GiftLogin` | 802 | 118 | 26 | 12 |
| `Board_Reborn` | 764 | 133 | 59 | 14 |
| `Board_Vip` | 744 | 82 | 23 | 11 |
| `Board_UserProfile` | 721 | 52 | 47 | 10 |
| `Board_Setting` | 701 | 84 | 54 | 10 |
| `Board_MiniCombo` | 652 | 83 | 33 | 10 |
| `Popup_ShipSalePack` | 600 | 13 | 5 | 9 |
| `Board_Stage` | 594 | 116 | 45 | 10 |
| `Board_QuestRewards` | 588 | 82 | 23 | 9 |
| `Tab_Boss` | 568 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 564 | 85 | 25 | 9 |
| `Popup_HolidayGift` | 552 | 78 | 11 | 8 |
| `Board_ShopEnergy` | 533 | 75 | 30 | 8 |
| `Popup_HolidayGift` | 528 | 67 | 11 | 7 |
| `Board_EventSeasonPass` | 507 | 71 | 20 | 8 |
| `Popup_PvPRankings` | 429 | 58 | 18 | 7 |
| `Popup_WeekSales` | 393 | 56 | 14 | 6 |

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
