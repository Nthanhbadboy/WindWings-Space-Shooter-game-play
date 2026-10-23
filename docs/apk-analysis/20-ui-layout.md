# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **725**
- tổng node: **106175**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (68)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92366 |
| `SpriteRenderer` | 50043 |
| `MeshRenderer` | 15273 |
| `RectTransform` | 13809 |
| `TextMeshPro` | 13743 |
| `MeshFilter` | 12493 |
| `BoxCollider2D` | 7425 |
| `Animator` | 5452 |
| `ButtonEvents` | 5125 |
| `Button_Sound` | 4975 |
| `ParticleSystem` | 3868 |
| `ParticleSystemRenderer` | 3868 |
| `LanguageTextMeshPro` | 3570 |
| `ChangeSorting` | 2214 |
| `BgObjectScaler` | 1635 |
| `Popup_Notices` | 1250 |
| `Box_Rewards` | 1224 |
| `TMP_SubMesh` | 1014 |
| `UIObjectAnchors` | 754 |
| `Shop_Cell` | 683 |
| `FixUIShop` | 617 |
| `Rigidbody2D` | 406 |
| `ObjectPool` | 367 |
| `LineRenderer` | 335 |
| `Enemy_Datas` | 319 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 448 | 334 | 62 |
| `Board_Shop` | 3269 | 497 | 151 | 45 |
| `Board_PVP` | 2902 | 415 | 170 | 42 |
| `Board_FightBoss` | 2557 | 118 | 42 | 40 |
| `Board_SelectBoss` | 2225 | 104 | 16 | 30 |
| `Board_Arena` | 2047 | 285 | 124 | 33 |
| `Tab_Boss` | 1857 | 5 | 0 | 29 |
| `Board_BattlePass` | 1749 | 240 | 64 | 19 |
| `Board_Players` | 1726 | 171 | 72 | 28 |
| `Board_Ranks` | 1342 | 197 | 89 | 21 |
| `Board_TechLab` | 1282 | 154 | 77 | 19 |
| `Board_Ranks` | 1268 | 189 | 87 | 20 |
| `Board_Survival` | 1145 | 178 | 77 | 19 |
| `Board_Survival` | 1123 | 166 | 85 | 18 |
| `Board_Begin` | 1105 | 144 | 55 | 17 |
| `Board_Drones` | 983 | 123 | 57 | 16 |
| `Board_Combo` | 954 | 98 | 58 | 14 |
| `Board_BattlePassPro` | 921 | 125 | 40 | 14 |
| `Board_WinnerBenefits` | 906 | 145 | 54 | 13 |
| `Popup_WatchVideos` | 876 | 149 | 48 | 13 |
| `Board_GiftLogin` | 858 | 128 | 29 | 13 |
| `Popup_WatchVideos` | 832 | 163 | 49 | 12 |
| `Board_MiniCombo` | 803 | 83 | 46 | 12 |
| `Board_Endgame` | 789 | 106 | 43 | 14 |
| `Board_Stage` | 784 | 135 | 54 | 12 |
| `Board_Challange` | 771 | 134 | 53 | 12 |
| `Board_Reborn` | 761 | 131 | 55 | 14 |
| `Board_Vip` | 723 | 85 | 26 | 11 |
| `Board_QuestRewards` | 690 | 105 | 27 | 10 |
| `Board_UserProfile` | 677 | 59 | 48 | 10 |
| `Popup_ShipSalePack` | 660 | 15 | 5 | 9 |
| `Board_Setting` | 619 | 80 | 47 | 10 |
| `Tab_Boss` | 537 | 6 | 1 | 7 |
| `Board_EventSeasonPass` | 531 | 95 | 27 | 9 |
| `Popup_HolidayGift` | 509 | 67 | 11 | 7 |
| `Popup_HolidayGift` | 500 | 72 | 11 | 7 |
| `Board_EventSeasonPass` | 483 | 71 | 22 | 7 |
| `Board_ShopEnergy` | 472 | 99 | 32 | 8 |
| `Popup_WeekSales` | 420 | 52 | 13 | 6 |
| `Board_Begin` | 407 | 33 | 14 | 5 |

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
