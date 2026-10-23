# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **745**
- tổng node: **105122**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (48)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91299 |
| `SpriteRenderer` | 49744 |
| `MeshRenderer` | 15302 |
| `RectTransform` | 13823 |
| `TextMeshPro` | 13749 |
| `MeshFilter` | 12612 |
| `BoxCollider2D` | 7409 |
| `Animator` | 5383 |
| `ButtonEvents` | 5096 |
| `Button_Sound` | 4955 |
| `ParticleSystem` | 3695 |
| `ParticleSystemRenderer` | 3695 |
| `LanguageTextMeshPro` | 3573 |
| `ChangeSorting` | 2227 |
| `BgObjectScaler` | 1644 |
| `Popup_Notices` | 1268 |
| `Box_Rewards` | 1198 |
| `TMP_SubMesh` | 1047 |
| `UIObjectAnchors` | 746 |
| `Shop_Cell` | 676 |
| `FixUIShop` | 623 |
| `Rigidbody2D` | 378 |
| `ObjectPool` | 333 |
| `LineRenderer` | 318 |
| `Enemy_Datas` | 283 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 432 | 334 | 60 |
| `Board_Shop` | 3311 | 498 | 153 | 45 |
| `Board_PVP` | 2572 | 380 | 165 | 38 |
| `Board_FightBoss` | 2540 | 124 | 45 | 40 |
| `Board_Arena` | 2017 | 295 | 125 | 32 |
| `Board_SelectBoss` | 1785 | 98 | 16 | 26 |
| `Tab_Boss` | 1756 | 5 | 0 | 27 |
| `Board_Players` | 1741 | 182 | 72 | 29 |
| `Board_BattlePass` | 1736 | 239 | 63 | 18 |
| `Board_Survival` | 1420 | 212 | 85 | 23 |
| `Board_Survival` | 1392 | 199 | 88 | 22 |
| `Board_Ranks` | 1362 | 196 | 85 | 22 |
| `Board_TechLab` | 1314 | 164 | 65 | 19 |
| `Board_Ranks` | 1129 | 184 | 85 | 19 |
| `Board_Drones` | 1030 | 136 | 59 | 18 |
| `Board_Begin` | 934 | 124 | 49 | 15 |
| `Board_Setting` | 930 | 102 | 63 | 13 |
| `Popup_WatchVideos` | 897 | 164 | 47 | 13 |
| `Board_WinnerBenefits` | 891 | 117 | 56 | 13 |
| `Popup_WatchVideos` | 834 | 156 | 44 | 12 |
| `Board_GiftLogin` | 815 | 120 | 27 | 12 |
| `Board_Reborn` | 813 | 153 | 56 | 15 |
| `Board_Endgame` | 803 | 115 | 45 | 14 |
| `Board_Combo` | 783 | 74 | 42 | 11 |
| `Board_Challange` | 771 | 132 | 50 | 12 |
| `Board_Stage` | 762 | 126 | 52 | 12 |
| `Board_Vip` | 761 | 92 | 26 | 11 |
| `Board_BattlePassPro` | 750 | 99 | 28 | 11 |
| `Board_QuestRewards` | 638 | 81 | 23 | 9 |
| `Board_ShopEnergy` | 624 | 105 | 34 | 9 |
| `Board_UserProfile` | 594 | 60 | 50 | 9 |
| `Popup_ShipSalePack` | 578 | 16 | 7 | 8 |
| `Tab_Boss` | 557 | 6 | 1 | 7 |
| `Popup_HolidayGift` | 545 | 79 | 11 | 8 |
| `Popup_HolidayGift` | 525 | 67 | 11 | 7 |
| `Board_EventSeasonPass` | 487 | 69 | 21 | 7 |
| `Board_MiniCombo` | 442 | 55 | 20 | 7 |
| `Board_EventSeasonPass` | 429 | 81 | 24 | 8 |
| `Popup_WeekSales` | 428 | 55 | 12 | 6 |
| `Board_Begin` | 377 | 34 | 14 | 5 |

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
