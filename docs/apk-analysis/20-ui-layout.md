# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **797**
- tổng node: **145112**
- dung lượng thô (gz): **4.0 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 126682 |
| `SpriteRenderer` | 72535 |
| `MeshRenderer` | 20943 |
| `RectTransform` | 18430 |
| `TextMeshPro` | 18340 |
| `MeshFilter` | 16987 |
| `BoxCollider2D` | 8244 |
| `Animator` | 6657 |
| `ButtonEvents` | 5686 |
| `Button_Sound` | 5524 |
| `ParticleSystem` | 5012 |
| `ParticleSystemRenderer` | 5012 |
| `LanguageTextMeshPro` | 4904 |
| `ChangeSorting` | 2342 |
| `BgObjectScaler` | 1744 |
| `TMP_SubMesh` | 1732 |
| `Popup_Notices` | 1335 |
| `Box_Rewards` | 1324 |
| `Shop_Cell` | 801 |
| `UIObjectAnchors` | 772 |
| `FixUIShop` | 723 |
| `Rigidbody2D` | 563 |
| `ObjectPool` | 456 |
| `Obj_Collider` | 440 |
| `LineRenderer` | 416 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 10315 | 614 | 353 | 130 |
| `Board_Shop` | 4876 | 848 | 190 | 96 |
| `Board_SelectBoss` | 3837 | 144 | 17 | 73 |
| `Board_PVP` | 3789 | 540 | 180 | 82 |
| `Board_FightBoss` | 3484 | 149 | 47 | 72 |
| `Tab_Boss` | 2649 | 6 | 0 | 51 |
| `Board_Arena` | 2606 | 357 | 129 | 61 |
| `Board_BattlePass` | 2469 | 381 | 80 | 34 |
| `Board_Players` | 2276 | 255 | 80 | 53 |
| `Board_Ranks` | 1976 | 281 | 94 | 45 |
| `Board_Ranks` | 1976 | 281 | 94 | 45 |
| `Board_Survival` | 1865 | 267 | 89 | 43 |
| `Board_Survival` | 1848 | 268 | 87 | 43 |
| `Board_TechLab` | 1838 | 219 | 82 | 36 |
| `Board_Drones` | 1327 | 179 | 62 | 34 |
| `Board_MiniCombo` | 1306 | 132 | 66 | 27 |
| `Board_Combo` | 1306 | 132 | 66 | 27 |
| `Board_Begin` | 1284 | 169 | 56 | 29 |
| `Board_WinnerBenefits` | 1252 | 184 | 58 | 29 |
| `Board_BattlePassPro` | 1200 | 157 | 44 | 29 |
| `Popup_WatchVideos` | 1113 | 198 | 50 | 24 |
| `Popup_WatchVideos` | 1113 | 198 | 50 | 24 |
| `Board_Reborn` | 1101 | 188 | 62 | 29 |
| `Board_Setting` | 1074 | 119 | 68 | 23 |
| `Board_Endgame` | 1070 | 160 | 54 | 28 |
| `Board_GiftLogin` | 1019 | 146 | 29 | 23 |
| `Board_Challange` | 995 | 175 | 55 | 24 |
| `Board_Stage` | 995 | 162 | 54 | 23 |
| `Board_Vip` | 918 | 116 | 27 | 21 |
| `Popup_ShipSalePack` | 895 | 19 | 7 | 17 |
| `Board_UserProfile` | 893 | 72 | 50 | 19 |
| `Board_QuestRewards` | 813 | 115 | 27 | 18 |
| `Board_ShopEnergy` | 755 | 129 | 35 | 17 |
| `Tab_Boss` | 723 | 9 | 1 | 11 |
| `Board_EventSeasonPass` | 659 | 106 | 29 | 18 |
| `Popup_HolidayGift` | 609 | 81 | 11 | 13 |
| `Popup_HolidayGift` | 593 | 69 | 11 | 12 |
| `Board_EventSeasonPass` | 572 | 82 | 22 | 13 |
| `Popup_WeekSales` | 532 | 69 | 14 | 10 |
| `Popup_PvPRankings` | 520 | 65 | 19 | 13 |

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
  không gán một tỉ lệ px/unit cố định nếu chưa resolve camera/runtime viewport).
- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.
- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.
