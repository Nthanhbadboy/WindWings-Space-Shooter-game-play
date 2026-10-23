# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **732**
- tổng node: **106162**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (61)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92214 |
| `SpriteRenderer` | 49966 |
| `MeshRenderer` | 15407 |
| `RectTransform` | 13948 |
| `TextMeshPro` | 13883 |
| `MeshFilter` | 12569 |
| `BoxCollider2D` | 7473 |
| `Animator` | 5502 |
| `ButtonEvents` | 5153 |
| `Button_Sound` | 5004 |
| `ParticleSystem` | 3852 |
| `ParticleSystemRenderer` | 3852 |
| `LanguageTextMeshPro` | 3589 |
| `ChangeSorting` | 2242 |
| `BgObjectScaler` | 1649 |
| `Popup_Notices` | 1266 |
| `Box_Rewards` | 1224 |
| `TMP_SubMesh` | 1020 |
| `UIObjectAnchors` | 746 |
| `Shop_Cell` | 691 |
| `FixUIShop` | 634 |
| `Rigidbody2D` | 380 |
| `ObjectPool` | 367 |
| `LineRenderer` | 317 |
| `Enemy_Datas` | 317 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 446 | 337 | 62 |
| `Board_Shop` | 3270 | 479 | 152 | 45 |
| `Board_PVP` | 2835 | 400 | 165 | 43 |
| `Board_SelectBoss` | 2691 | 116 | 16 | 39 |
| `Board_FightBoss` | 2276 | 105 | 42 | 37 |
| `Board_Arena` | 1918 | 269 | 118 | 31 |
| `Board_BattlePass` | 1902 | 272 | 71 | 19 |
| `Tab_Boss` | 1702 | 4 | 0 | 27 |
| `Board_Players` | 1690 | 186 | 72 | 27 |
| `Board_Ranks` | 1426 | 207 | 89 | 22 |
| `Board_Ranks` | 1355 | 205 | 91 | 22 |
| `Board_Survival` | 1354 | 201 | 89 | 22 |
| `Board_Survival` | 1296 | 206 | 83 | 21 |
| `Board_TechLab` | 1162 | 139 | 63 | 17 |
| `Board_BattlePassPro` | 1009 | 124 | 40 | 16 |
| `Board_Drones` | 1001 | 127 | 54 | 16 |
| `Board_WinnerBenefits` | 990 | 148 | 55 | 14 |
| `Popup_WatchVideos` | 923 | 163 | 49 | 13 |
| `Board_Begin` | 911 | 119 | 45 | 15 |
| `Board_Reborn` | 829 | 127 | 61 | 15 |
| `Board_Endgame` | 827 | 123 | 54 | 15 |
| `Board_Setting` | 823 | 93 | 61 | 12 |
| `Board_MiniCombo` | 819 | 89 | 50 | 12 |
| `Board_GiftLogin` | 815 | 118 | 27 | 12 |
| `Board_Vip` | 775 | 96 | 27 | 11 |
| `Board_Challange` | 774 | 142 | 47 | 12 |
| `Popup_WatchVideos` | 752 | 114 | 37 | 11 |
| `Board_Stage` | 713 | 122 | 51 | 12 |
| `Popup_ShipSalePack` | 696 | 16 | 7 | 10 |
| `Board_Combo` | 676 | 80 | 42 | 11 |
| `Board_QuestRewards` | 647 | 86 | 26 | 9 |
| `Board_ShopEnergy` | 601 | 107 | 35 | 9 |
| `Board_EventSeasonPass` | 554 | 87 | 27 | 9 |
| `Popup_HolidayGift` | 535 | 68 | 10 | 7 |
| `Tab_Boss` | 520 | 9 | 1 | 7 |
| `Popup_WeekSales` | 507 | 63 | 14 | 6 |
| `Popup_HolidayGift` | 502 | 72 | 11 | 7 |
| `Board_UserProfile` | 459 | 30 | 46 | 6 |
| `Popup_PvPRankings` | 448 | 57 | 17 | 7 |
| `Board_EventSeasonPass` | 437 | 71 | 21 | 7 |

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
