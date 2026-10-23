# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **732**
- tổng node: **105166**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (61)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91520 |
| `SpriteRenderer` | 49638 |
| `MeshRenderer` | 15149 |
| `RectTransform` | 13646 |
| `TextMeshPro` | 13584 |
| `MeshFilter` | 12414 |
| `BoxCollider2D` | 7390 |
| `Animator` | 5443 |
| `ButtonEvents` | 5101 |
| `Button_Sound` | 4963 |
| `ParticleSystem` | 3767 |
| `ParticleSystemRenderer` | 3767 |
| `LanguageTextMeshPro` | 3541 |
| `ChangeSorting` | 2198 |
| `BgObjectScaler` | 1631 |
| `Popup_Notices` | 1248 |
| `Box_Rewards` | 1206 |
| `TMP_SubMesh` | 1019 |
| `UIObjectAnchors` | 744 |
| `Shop_Cell` | 653 |
| `FixUIShop` | 605 |
| `Rigidbody2D` | 382 |
| `ObjectPool` | 367 |
| `LineRenderer` | 317 |
| `Enemy_Datas` | 317 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 443 | 336 | 62 |
| `Board_Shop` | 3456 | 527 | 159 | 47 |
| `Board_PVP` | 2526 | 358 | 163 | 37 |
| `Board_FightBoss` | 2426 | 123 | 46 | 38 |
| `Board_SelectBoss` | 2234 | 87 | 15 | 31 |
| `Board_Players` | 1861 | 190 | 75 | 30 |
| `Board_Arena` | 1794 | 206 | 105 | 30 |
| `Tab_Boss` | 1748 | 4 | 0 | 27 |
| `Board_BattlePass` | 1649 | 242 | 62 | 17 |
| `Board_TechLab` | 1470 | 173 | 76 | 20 |
| `Board_Ranks` | 1463 | 240 | 91 | 23 |
| `Board_Ranks` | 1416 | 220 | 87 | 22 |
| `Board_Survival` | 1253 | 186 | 78 | 21 |
| `Board_Survival` | 1147 | 158 | 71 | 17 |
| `Board_Drones` | 1048 | 139 | 58 | 17 |
| `Board_Combo` | 1037 | 104 | 63 | 15 |
| `Board_Begin` | 972 | 143 | 55 | 16 |
| `Board_WinnerBenefits` | 971 | 149 | 56 | 15 |
| `Board_BattlePassPro` | 920 | 121 | 41 | 14 |
| `Board_GiftLogin` | 895 | 129 | 28 | 13 |
| `Board_Endgame` | 888 | 128 | 48 | 16 |
| `Board_Reborn` | 869 | 146 | 60 | 15 |
| `Popup_WatchVideos` | 822 | 161 | 49 | 12 |
| `Board_Challange` | 820 | 139 | 54 | 13 |
| `Popup_WatchVideos` | 811 | 159 | 47 | 12 |
| `Board_Vip` | 763 | 98 | 26 | 11 |
| `Board_QuestRewards` | 729 | 102 | 27 | 10 |
| `Board_Stage` | 708 | 129 | 52 | 12 |
| `Popup_ShipSalePack` | 704 | 16 | 7 | 10 |
| `Board_Setting` | 689 | 90 | 63 | 10 |
| `Board_ShopEnergy` | 626 | 98 | 33 | 9 |
| `Board_EventSeasonPass` | 588 | 97 | 29 | 10 |
| `Board_UserProfile` | 565 | 48 | 48 | 9 |
| `Tab_Boss` | 560 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 555 | 73 | 11 | 8 |
| `Popup_HolidayGift` | 552 | 67 | 11 | 7 |
| `Board_MiniCombo` | 463 | 51 | 18 | 7 |
| `Board_EventSeasonPass` | 453 | 72 | 20 | 7 |
| `Popup_WeekSales` | 408 | 48 | 13 | 6 |
| `Board_Begin` | 385 | 33 | 15 | 5 |

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
