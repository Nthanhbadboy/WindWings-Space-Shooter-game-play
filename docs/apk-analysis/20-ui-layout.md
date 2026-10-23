# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **731**
- tổng node: **103094**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (62)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89419 |
| `SpriteRenderer` | 48736 |
| `MeshRenderer` | 15088 |
| `RectTransform` | 13675 |
| `TextMeshPro` | 13597 |
| `MeshFilter` | 12392 |
| `BoxCollider2D` | 7391 |
| `Animator` | 5363 |
| `ButtonEvents` | 5105 |
| `Button_Sound` | 4964 |
| `ParticleSystem` | 3540 |
| `ParticleSystemRenderer` | 3540 |
| `LanguageTextMeshPro` | 3517 |
| `ChangeSorting` | 2193 |
| `BgObjectScaler` | 1639 |
| `Popup_Notices` | 1261 |
| `Box_Rewards` | 1185 |
| `TMP_SubMesh` | 1022 |
| `UIObjectAnchors` | 701 |
| `Shop_Cell` | 674 |
| `FixUIShop` | 613 |
| `Rigidbody2D` | 328 |
| `LineRenderer` | 282 |
| `ObjectPool` | 266 |
| `Obj_Collider` | 233 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 442 | 329 | 61 |
| `Board_Shop` | 3737 | 573 | 160 | 50 |
| `Board_PVP` | 2578 | 366 | 164 | 39 |
| `Board_FightBoss` | 2437 | 95 | 43 | 39 |
| `Tab_Boss` | 1933 | 5 | 0 | 30 |
| `Board_Arena` | 1857 | 278 | 122 | 30 |
| `Board_Players` | 1758 | 205 | 76 | 29 |
| `Board_BattlePass` | 1677 | 227 | 63 | 18 |
| `Board_Ranks` | 1614 | 234 | 92 | 25 |
| `Board_TechLab` | 1503 | 177 | 79 | 20 |
| `Board_Ranks` | 1320 | 200 | 83 | 21 |
| `Board_Survival` | 1256 | 194 | 81 | 21 |
| `Board_Survival` | 1243 | 199 | 83 | 20 |
| `Board_Drones` | 1075 | 141 | 60 | 18 |
| `Board_WinnerBenefits` | 1042 | 139 | 55 | 15 |
| `Board_BattlePassPro` | 973 | 123 | 42 | 15 |
| `Board_MiniCombo` | 957 | 104 | 56 | 14 |
| `Board_Begin` | 901 | 130 | 50 | 15 |
| `Board_Endgame` | 873 | 124 | 53 | 15 |
| `Board_GiftLogin` | 864 | 119 | 26 | 12 |
| `Popup_WatchVideos` | 846 | 153 | 49 | 12 |
| `Board_Setting` | 819 | 96 | 67 | 12 |
| `Board_Reborn` | 812 | 153 | 58 | 15 |
| `Board_Vip` | 731 | 99 | 27 | 10 |
| `Board_Challange` | 721 | 120 | 54 | 12 |
| `Popup_WatchVideos` | 702 | 146 | 46 | 11 |
| `Board_Stage` | 632 | 61 | 44 | 10 |
| `Board_QuestRewards` | 602 | 85 | 26 | 9 |
| `Board_ShopEnergy` | 597 | 95 | 34 | 9 |
| `Board_Combo` | 583 | 75 | 32 | 9 |
| `Board_EventSeasonPass` | 582 | 95 | 28 | 10 |
| `Tab_Boss` | 581 | 7 | 1 | 7 |
| `Popup_ShipSalePack` | 573 | 17 | 7 | 8 |
| `Board_UserProfile` | 557 | 60 | 49 | 9 |
| `Popup_WeekSales` | 496 | 61 | 14 | 6 |
| `Popup_HolidayGift` | 482 | 75 | 11 | 7 |
| `Popup_HolidayGift` | 482 | 65 | 11 | 7 |
| `Board_EventSeasonPass` | 478 | 65 | 22 | 7 |
| `Popup_PvPRankings` | 431 | 56 | 17 | 7 |
| `Popup_WatchVideosOld` | 372 | 57 | 13 | 5 |

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
