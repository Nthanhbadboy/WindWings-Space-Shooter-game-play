# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **733**
- tổng node: **103087**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (60)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89312 |
| `SpriteRenderer` | 47837 |
| `MeshRenderer` | 15234 |
| `RectTransform` | 13775 |
| `TextMeshPro` | 13699 |
| `MeshFilter` | 12544 |
| `BoxCollider2D` | 7247 |
| `Animator` | 5355 |
| `ButtonEvents` | 4939 |
| `Button_Sound` | 4786 |
| `ParticleSystem` | 3803 |
| `ParticleSystemRenderer` | 3803 |
| `LanguageTextMeshPro` | 3539 |
| `ChangeSorting` | 2213 |
| `BgObjectScaler` | 1623 |
| `Popup_Notices` | 1254 |
| `Box_Rewards` | 1246 |
| `TMP_SubMesh` | 1042 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 672 |
| `FixUIShop` | 625 |
| `Rigidbody2D` | 400 |
| `ObjectPool` | 381 |
| `Enemy_Datas` | 327 |
| `Enemy_Health` | 327 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Shop` | 3659 | 578 | 162 | 50 |
| `Board_PVP` | 2879 | 412 | 156 | 42 |
| `Board_SelectBoss` | 2458 | 91 | 13 | 34 |
| `Board_FightBoss` | 2436 | 125 | 45 | 39 |
| `Board_Maps` | 2152 | 296 | 144 | 36 |
| `Tab_Boss` | 1851 | 6 | 0 | 28 |
| `Board_Players` | 1834 | 193 | 76 | 29 |
| `Board_Arena` | 1800 | 199 | 102 | 29 |
| `Board_BattlePass` | 1786 | 244 | 68 | 18 |
| `Board_TechLab` | 1393 | 160 | 73 | 20 |
| `Board_Ranks` | 1367 | 192 | 85 | 22 |
| `Board_Ranks` | 1339 | 215 | 87 | 21 |
| `Board_Survival` | 1300 | 184 | 81 | 20 |
| `Board_Survival` | 1132 | 184 | 80 | 20 |
| `Board_Begin` | 1050 | 140 | 53 | 16 |
| `Board_Combo` | 1003 | 99 | 64 | 14 |
| `Board_BattlePassPro` | 977 | 129 | 42 | 15 |
| `Board_MiniCombo` | 921 | 92 | 51 | 13 |
| `Board_GiftLogin` | 883 | 122 | 29 | 13 |
| `Popup_WatchVideos` | 880 | 174 | 47 | 13 |
| `Board_Drones` | 876 | 133 | 60 | 16 |
| `Board_Challange` | 856 | 148 | 55 | 13 |
| `Board_Endgame` | 853 | 122 | 47 | 15 |
| `Board_WinnerBenefits` | 826 | 129 | 55 | 13 |
| `Board_Reborn` | 821 | 152 | 59 | 15 |
| `Popup_WatchVideos` | 814 | 154 | 47 | 12 |
| `Board_Vip` | 756 | 91 | 26 | 11 |
| `Board_Setting` | 726 | 79 | 46 | 11 |
| `Popup_ShipSalePack` | 723 | 14 | 7 | 10 |
| `Board_Stage` | 671 | 105 | 50 | 11 |
| `Board_QuestRewards` | 666 | 90 | 26 | 9 |
| `Board_ShopEnergy` | 595 | 109 | 35 | 9 |
| `Popup_HolidayGift` | 570 | 77 | 11 | 8 |
| `Tab_Boss` | 564 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 515 | 90 | 28 | 9 |
| `Board_UserProfile` | 505 | 56 | 46 | 8 |
| `Popup_HolidayGift` | 497 | 61 | 9 | 7 |
| `Board_EventSeasonPass` | 490 | 72 | 21 | 7 |
| `Popup_PvPRankings` | 437 | 50 | 18 | 7 |
| `Popup_PvPRankings` | 435 | 56 | 18 | 7 |

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
