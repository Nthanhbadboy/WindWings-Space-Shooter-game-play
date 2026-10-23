# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **730**
- tổng node: **106748**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (63)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92724 |
| `SpriteRenderer` | 50180 |
| `MeshRenderer` | 15485 |
| `RectTransform` | 14024 |
| `TextMeshPro` | 13951 |
| `MeshFilter` | 12729 |
| `BoxCollider2D` | 7509 |
| `Animator` | 5439 |
| `ButtonEvents` | 5165 |
| `Button_Sound` | 5016 |
| `ParticleSystem` | 3885 |
| `ParticleSystemRenderer` | 3885 |
| `LanguageTextMeshPro` | 3598 |
| `ChangeSorting` | 2231 |
| `BgObjectScaler` | 1649 |
| `Popup_Notices` | 1264 |
| `Box_Rewards` | 1213 |
| `TMP_SubMesh` | 1021 |
| `UIObjectAnchors` | 751 |
| `Shop_Cell` | 680 |
| `FixUIShop` | 634 |
| `Rigidbody2D` | 412 |
| `ObjectPool` | 392 |
| `Enemy_Datas` | 339 |
| `Enemy_Health` | 339 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 436 | 339 | 61 |
| `Board_Shop` | 3250 | 509 | 145 | 44 |
| `Board_FightBoss` | 2505 | 125 | 44 | 40 |
| `Board_PVP` | 2498 | 355 | 167 | 37 |
| `Board_SelectBoss` | 2113 | 78 | 16 | 31 |
| `Tab_Boss` | 1953 | 5 | 0 | 30 |
| `Board_Arena` | 1742 | 210 | 102 | 29 |
| `Board_BattlePass` | 1702 | 232 | 65 | 18 |
| `Board_Players` | 1689 | 171 | 75 | 28 |
| `Board_Ranks` | 1392 | 211 | 86 | 22 |
| `Board_TechLab` | 1353 | 177 | 71 | 19 |
| `Board_Ranks` | 1325 | 202 | 90 | 21 |
| `Board_Survival` | 1275 | 170 | 80 | 20 |
| `Board_Survival` | 1222 | 187 | 85 | 20 |
| `Board_Begin` | 1101 | 150 | 51 | 17 |
| `Board_Drones` | 1043 | 125 | 59 | 17 |
| `Board_WinnerBenefits` | 1022 | 146 | 57 | 15 |
| `Board_MiniCombo` | 970 | 108 | 59 | 14 |
| `Board_BattlePassPro` | 899 | 122 | 38 | 14 |
| `Board_GiftLogin` | 857 | 125 | 28 | 13 |
| `Popup_WatchVideos` | 856 | 163 | 48 | 13 |
| `Popup_WatchVideos` | 818 | 159 | 50 | 12 |
| `Board_Stage` | 817 | 128 | 51 | 13 |
| `Board_Challange` | 804 | 148 | 54 | 13 |
| `Board_Endgame` | 794 | 120 | 50 | 14 |
| `Board_Vip` | 792 | 102 | 27 | 11 |
| `Board_Reborn` | 782 | 139 | 58 | 15 |
| `Board_Setting` | 728 | 91 | 62 | 11 |
| `Board_UserProfile` | 724 | 64 | 50 | 11 |
| `Board_Combo` | 720 | 81 | 41 | 11 |
| `Board_QuestRewards` | 709 | 104 | 27 | 10 |
| `Popup_ShipSalePack` | 695 | 17 | 7 | 10 |
| `Popup_HolidayGift` | 570 | 73 | 11 | 8 |
| `Popup_HolidayGift` | 549 | 66 | 11 | 7 |
| `Board_ShopEnergy` | 535 | 96 | 35 | 9 |
| `Tab_Boss` | 531 | 9 | 1 | 7 |
| `Board_EventSeasonPass` | 512 | 91 | 28 | 9 |
| `Popup_WeekSales` | 491 | 58 | 14 | 6 |
| `Board_EventSeasonPass` | 469 | 69 | 21 | 7 |
| `Board_Begin` | 367 | 32 | 14 | 5 |

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
