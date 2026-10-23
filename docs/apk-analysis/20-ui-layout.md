# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **723**
- tổng node: **104955**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (70)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91004 |
| `SpriteRenderer` | 49573 |
| `MeshRenderer` | 15493 |
| `RectTransform` | 13951 |
| `TextMeshPro` | 13882 |
| `MeshFilter` | 12702 |
| `BoxCollider2D` | 7297 |
| `Animator` | 5312 |
| `ButtonEvents` | 5031 |
| `Button_Sound` | 4877 |
| `LanguageTextMeshPro` | 3638 |
| `ParticleSystem` | 3588 |
| `ParticleSystemRenderer` | 3588 |
| `ChangeSorting` | 2206 |
| `BgObjectScaler` | 1619 |
| `Popup_Notices` | 1243 |
| `Box_Rewards` | 1193 |
| `TMP_SubMesh` | 1075 |
| `UIObjectAnchors` | 750 |
| `Shop_Cell` | 712 |
| `FixUIShop` | 639 |
| `Rigidbody2D` | 400 |
| `ObjectPool` | 348 |
| `LineRenderer` | 312 |
| `Obj_Collider` | 296 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4188 | 350 | 200 | 52 |
| `Board_Shop` | 3317 | 564 | 161 | 46 |
| `Board_PVP` | 2814 | 412 | 168 | 42 |
| `Board_FightBoss` | 2499 | 111 | 46 | 40 |
| `Board_SelectBoss` | 2029 | 106 | 17 | 29 |
| `Board_Arena` | 1984 | 281 | 124 | 32 |
| `Tab_Boss` | 1922 | 5 | 0 | 30 |
| `Board_Players` | 1764 | 176 | 73 | 28 |
| `Board_BattlePass` | 1677 | 236 | 60 | 18 |
| `Board_Ranks` | 1414 | 218 | 91 | 23 |
| `Board_TechLab` | 1310 | 145 | 77 | 19 |
| `Board_Ranks` | 1257 | 189 | 89 | 20 |
| `Board_Survival` | 1185 | 201 | 82 | 20 |
| `Board_Survival` | 1043 | 134 | 73 | 17 |
| `Board_Begin` | 1030 | 147 | 51 | 16 |
| `Board_WinnerBenefits` | 993 | 153 | 54 | 15 |
| `Board_Drones` | 977 | 137 | 56 | 16 |
| `Board_Setting` | 925 | 103 | 68 | 13 |
| `Board_GiftLogin` | 864 | 130 | 29 | 13 |
| `Board_BattlePassPro` | 863 | 117 | 38 | 13 |
| `Board_Endgame` | 836 | 114 | 52 | 15 |
| `Board_Reborn` | 831 | 131 | 56 | 15 |
| `Popup_WatchVideos` | 798 | 143 | 48 | 12 |
| `Board_Combo` | 785 | 84 | 49 | 11 |
| `Board_Stage` | 781 | 131 | 51 | 12 |
| `Board_MiniCombo` | 777 | 76 | 42 | 11 |
| `Board_Challange` | 769 | 131 | 50 | 12 |
| `Popup_WatchVideos` | 768 | 164 | 49 | 12 |
| `Board_Vip` | 746 | 75 | 23 | 11 |
| `Board_UserProfile` | 652 | 53 | 49 | 9 |
| `Popup_ShipSalePack` | 645 | 14 | 6 | 9 |
| `Board_QuestRewards` | 645 | 75 | 26 | 9 |
| `Board_ShopEnergy` | 585 | 113 | 31 | 9 |
| `Tab_Boss` | 576 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 543 | 61 | 10 | 7 |
| `Popup_HolidayGift` | 518 | 71 | 11 | 7 |
| `Board_EventSeasonPass` | 481 | 86 | 27 | 8 |
| `Popup_WeekSales` | 467 | 62 | 14 | 6 |
| `Board_EventSeasonPass` | 437 | 71 | 22 | 7 |
| `Popup_PvPRankings` | 403 | 50 | 16 | 7 |

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
