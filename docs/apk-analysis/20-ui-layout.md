# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **740**
- tổng node: **104945**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (53)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90936 |
| `SpriteRenderer` | 49582 |
| `MeshRenderer` | 15575 |
| `RectTransform` | 14009 |
| `TextMeshPro` | 13938 |
| `MeshFilter` | 12750 |
| `BoxCollider2D` | 7342 |
| `Animator` | 5284 |
| `ButtonEvents` | 5002 |
| `Button_Sound` | 4855 |
| `LanguageTextMeshPro` | 3658 |
| `ParticleSystem` | 3578 |
| `ParticleSystemRenderer` | 3578 |
| `ChangeSorting` | 2248 |
| `BgObjectScaler` | 1652 |
| `Popup_Notices` | 1276 |
| `Box_Rewards` | 1198 |
| `TMP_SubMesh` | 1105 |
| `UIObjectAnchors` | 749 |
| `Shop_Cell` | 695 |
| `FixUIShop` | 630 |
| `Rigidbody2D` | 344 |
| `ObjectPool` | 338 |
| `Enemy_Datas` | 287 |
| `Enemy_Health` | 287 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4381 | 356 | 205 | 53 |
| `Board_Shop` | 3784 | 619 | 172 | 51 |
| `Board_PVP` | 2705 | 401 | 170 | 41 |
| `Board_FightBoss` | 2470 | 108 | 46 | 39 |
| `Board_SelectBoss` | 2295 | 110 | 17 | 30 |
| `Board_Arena` | 1950 | 280 | 117 | 31 |
| `Tab_Boss` | 1926 | 5 | 0 | 29 |
| `Board_Players` | 1880 | 211 | 78 | 30 |
| `Board_BattlePass` | 1733 | 244 | 65 | 18 |
| `Board_Ranks` | 1451 | 195 | 91 | 22 |
| `Board_Survival` | 1449 | 209 | 83 | 23 |
| `Board_TechLab` | 1339 | 149 | 67 | 19 |
| `Board_Survival` | 1296 | 198 | 84 | 21 |
| `Board_Ranks` | 1205 | 211 | 90 | 20 |
| `Board_Begin` | 1013 | 131 | 50 | 16 |
| `Board_WinnerBenefits` | 963 | 146 | 55 | 14 |
| `Popup_WatchVideos` | 891 | 151 | 44 | 13 |
| `Board_Setting` | 874 | 102 | 67 | 13 |
| `Board_Reborn` | 859 | 154 | 58 | 15 |
| `Board_Endgame` | 813 | 115 | 51 | 15 |
| `Board_GiftLogin` | 811 | 117 | 23 | 12 |
| `Popup_WatchVideos` | 802 | 145 | 48 | 12 |
| `Board_Drones` | 794 | 83 | 44 | 12 |
| `Board_BattlePassPro` | 776 | 104 | 28 | 11 |
| `Board_Challange` | 769 | 138 | 52 | 12 |
| `Board_Stage` | 766 | 121 | 51 | 12 |
| `Board_Vip` | 625 | 67 | 22 | 9 |
| `Board_ShopEnergy` | 622 | 108 | 34 | 9 |
| `Board_QuestRewards` | 604 | 81 | 23 | 9 |
| `Popup_ShipSalePack` | 583 | 18 | 7 | 9 |
| `Board_Combo` | 575 | 66 | 32 | 9 |
| `Popup_HolidayGift` | 545 | 73 | 10 | 8 |
| `Popup_HolidayGift` | 521 | 64 | 11 | 7 |
| `Board_EventSeasonPass` | 503 | 86 | 26 | 9 |
| `Board_EventSeasonPass` | 462 | 66 | 21 | 7 |
| `Board_UserProfile` | 446 | 52 | 46 | 7 |
| `Board_MiniCombo` | 435 | 52 | 19 | 7 |
| `Popup_WatchVideosOld` | 379 | 59 | 13 | 5 |
| `Board_Quest` | 378 | 109 | 38 | 5 |
| `Board_Begin` | 378 | 31 | 15 | 5 |

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
