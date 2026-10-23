# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **738**
- tổng node: **102146**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (55)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88251 |
| `SpriteRenderer` | 48400 |
| `MeshRenderer` | 15341 |
| `RectTransform` | 13895 |
| `TextMeshPro` | 13818 |
| `MeshFilter` | 12679 |
| `BoxCollider2D` | 7418 |
| `Animator` | 5289 |
| `ButtonEvents` | 5142 |
| `Button_Sound` | 4989 |
| `LanguageTextMeshPro` | 3592 |
| `ParticleSystem` | 3373 |
| `ParticleSystemRenderer` | 3373 |
| `ChangeSorting` | 2201 |
| `BgObjectScaler` | 1644 |
| `Popup_Notices` | 1270 |
| `Box_Rewards` | 1171 |
| `TMP_SubMesh` | 1046 |
| `UIObjectAnchors` | 699 |
| `Shop_Cell` | 688 |
| `FixUIShop` | 618 |
| `LineRenderer` | 282 |
| `Rigidbody2D` | 273 |
| `AutoSetVipIcon` | 228 |
| `SpriteMask` | 216 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 435 | 343 | 61 |
| `Board_Shop` | 3453 | 538 | 166 | 48 |
| `Board_PVP` | 2674 | 377 | 168 | 40 |
| `Board_FightBoss` | 2479 | 116 | 44 | 39 |
| `Board_BattlePass` | 1898 | 263 | 71 | 19 |
| `Board_Arena` | 1799 | 265 | 122 | 30 |
| `Board_Players` | 1698 | 198 | 74 | 28 |
| `Board_Ranks` | 1578 | 215 | 93 | 24 |
| `Tab_Boss` | 1563 | 6 | 0 | 25 |
| `Board_Ranks` | 1343 | 198 | 92 | 22 |
| `Board_Survival` | 1337 | 191 | 81 | 21 |
| `Board_TechLab` | 1309 | 182 | 76 | 19 |
| `Board_Survival` | 1294 | 186 | 86 | 21 |
| `Board_Drones` | 1017 | 136 | 58 | 17 |
| `Popup_WatchVideos` | 978 | 177 | 50 | 14 |
| `Board_WinnerBenefits` | 919 | 142 | 52 | 14 |
| `Board_Begin` | 907 | 120 | 51 | 15 |
| `Board_BattlePassPro` | 853 | 112 | 31 | 13 |
| `Board_GiftLogin` | 847 | 125 | 27 | 13 |
| `Board_Endgame` | 841 | 119 | 50 | 15 |
| `Popup_WatchVideos` | 815 | 148 | 46 | 12 |
| `Board_Reborn` | 777 | 137 | 57 | 15 |
| `Board_Setting` | 767 | 97 | 63 | 12 |
| `Board_Vip` | 754 | 95 | 25 | 11 |
| `Board_Stage` | 729 | 124 | 52 | 12 |
| `Board_Challange` | 722 | 126 | 55 | 12 |
| `Board_QuestRewards` | 691 | 97 | 25 | 10 |
| `Popup_ShipSalePack` | 677 | 17 | 7 | 10 |
| `Board_Combo` | 669 | 78 | 38 | 10 |
| `Popup_HolidayGift` | 569 | 78 | 11 | 8 |
| `Popup_HolidayGift` | 557 | 65 | 11 | 7 |
| `Board_EventSeasonPass` | 542 | 91 | 29 | 9 |
| `Board_EventSeasonPass` | 500 | 69 | 22 | 7 |
| `Popup_WeekSales` | 484 | 64 | 14 | 6 |
| `Board_UserProfile` | 462 | 31 | 45 | 7 |
| `Board_ShopEnergy` | 453 | 113 | 34 | 8 |
| `Board_MiniCombo` | 434 | 58 | 20 | 7 |
| `Board_Begin` | 411 | 32 | 12 | 5 |
| `Board_Reborn_IAP` | 371 | 70 | 15 | 5 |
| `Board_AccountSettings` | 362 | 31 | 16 | 5 |

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
