# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **732**
- tổng node: **103850**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (61)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89828 |
| `SpriteRenderer` | 48998 |
| `MeshRenderer` | 15528 |
| `RectTransform` | 14022 |
| `TextMeshPro` | 13950 |
| `MeshFilter` | 12723 |
| `BoxCollider2D` | 7459 |
| `Animator` | 5418 |
| `ButtonEvents` | 5144 |
| `Button_Sound` | 5000 |
| `LanguageTextMeshPro` | 3603 |
| `ParticleSystem` | 3593 |
| `ParticleSystemRenderer` | 3593 |
| `ChangeSorting` | 2224 |
| `BgObjectScaler` | 1648 |
| `Popup_Notices` | 1262 |
| `Box_Rewards` | 1242 |
| `TMP_SubMesh` | 1078 |
| `UIObjectAnchors` | 749 |
| `Shop_Cell` | 689 |
| `FixUIShop` | 637 |
| `Rigidbody2D` | 328 |
| `ObjectPool` | 314 |
| `LineRenderer` | 273 |
| `Enemy_Datas` | 266 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 436 | 335 | 60 |
| `Board_Shop` | 3400 | 524 | 153 | 47 |
| `Board_PVP` | 2457 | 341 | 159 | 37 |
| `Board_SelectBoss` | 2163 | 99 | 14 | 30 |
| `Tab_Boss` | 1940 | 3 | 0 | 30 |
| `Board_Players` | 1736 | 177 | 73 | 28 |
| `Board_BattlePass` | 1646 | 237 | 63 | 18 |
| `Board_Ranks` | 1493 | 211 | 90 | 24 |
| `Board_Arena` | 1488 | 240 | 109 | 24 |
| `Board_Ranks` | 1426 | 210 | 88 | 22 |
| `Board_Survival` | 1316 | 200 | 87 | 21 |
| `Board_Survival` | 1307 | 180 | 84 | 20 |
| `Board_TechLab` | 1233 | 155 | 71 | 18 |
| `Board_WinnerBenefits` | 1034 | 151 | 55 | 15 |
| `Board_Begin` | 1001 | 148 | 53 | 16 |
| `Board_Drones` | 956 | 137 | 60 | 17 |
| `Popup_WatchVideos` | 940 | 163 | 46 | 13 |
| `Board_MiniCombo` | 923 | 92 | 54 | 13 |
| `Popup_WatchVideos` | 921 | 166 | 49 | 13 |
| `Board_Endgame` | 893 | 127 | 53 | 16 |
| `Board_Reborn` | 858 | 152 | 61 | 15 |
| `Board_GiftLogin` | 812 | 127 | 29 | 12 |
| `Board_BattlePassPro` | 794 | 102 | 28 | 11 |
| `Board_Stage` | 792 | 138 | 52 | 12 |
| `Board_Challange` | 790 | 143 | 53 | 13 |
| `Board_Combo` | 777 | 79 | 43 | 11 |
| `Board_Vip` | 742 | 91 | 25 | 11 |
| `Board_FightBoss` | 714 | 117 | 45 | 11 |
| `Board_Setting` | 647 | 80 | 45 | 11 |
| `Board_QuestRewards` | 640 | 84 | 27 | 9 |
| `Board_UserProfile` | 618 | 34 | 50 | 9 |
| `Popup_ShipSalePack` | 609 | 15 | 5 | 9 |
| `Tab_Boss` | 554 | 8 | 1 | 7 |
| `Board_ShopEnergy` | 549 | 101 | 33 | 9 |
| `Popup_HolidayGift` | 543 | 67 | 11 | 7 |
| `Board_EventSeasonPass` | 534 | 88 | 26 | 9 |
| `Popup_HolidayGift` | 473 | 72 | 11 | 7 |
| `Board_EventSeasonPass` | 465 | 73 | 22 | 7 |
| `Popup_WeekSales` | 460 | 57 | 14 | 6 |
| `Board_Begin` | 383 | 36 | 14 | 5 |

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
