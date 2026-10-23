# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **732**
- tổng node: **105162**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (61)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91310 |
| `SpriteRenderer` | 49488 |
| `MeshRenderer` | 15327 |
| `RectTransform` | 13852 |
| `TextMeshPro` | 13777 |
| `MeshFilter` | 12518 |
| `BoxCollider2D` | 7412 |
| `Animator` | 5411 |
| `ButtonEvents` | 5093 |
| `Button_Sound` | 4959 |
| `ParticleSystem` | 3810 |
| `ParticleSystemRenderer` | 3810 |
| `LanguageTextMeshPro` | 3622 |
| `ChangeSorting` | 2213 |
| `BgObjectScaler` | 1628 |
| `Popup_Notices` | 1252 |
| `Box_Rewards` | 1199 |
| `TMP_SubMesh` | 1013 |
| `UIObjectAnchors` | 753 |
| `Shop_Cell` | 668 |
| `FixUIShop` | 611 |
| `Rigidbody2D` | 387 |
| `ObjectPool` | 362 |
| `LineRenderer` | 320 |
| `Enemy_Datas` | 311 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 465 | 328 | 62 |
| `Board_Shop` | 3484 | 542 | 152 | 48 |
| `Board_PVP` | 2563 | 355 | 158 | 38 |
| `Board_FightBoss` | 2312 | 91 | 43 | 37 |
| `Board_SelectBoss` | 2001 | 93 | 16 | 28 |
| `Tab_Boss` | 1972 | 6 | 0 | 31 |
| `Board_Arena` | 1942 | 253 | 119 | 31 |
| `Board_Players` | 1876 | 209 | 79 | 30 |
| `Board_BattlePass` | 1619 | 230 | 66 | 16 |
| `Board_Ranks` | 1538 | 231 | 91 | 24 |
| `Board_Survival` | 1443 | 211 | 81 | 23 |
| `Board_Ranks` | 1359 | 180 | 88 | 21 |
| `Board_Survival` | 1303 | 186 | 86 | 21 |
| `Board_TechLab` | 1238 | 119 | 63 | 17 |
| `Board_Drones` | 1019 | 142 | 58 | 17 |
| `Popup_WatchVideos` | 958 | 177 | 50 | 14 |
| `Board_WinnerBenefits` | 952 | 141 | 57 | 14 |
| `Board_GiftLogin` | 889 | 127 | 28 | 13 |
| `Popup_WatchVideos` | 886 | 163 | 48 | 13 |
| `Board_Combo` | 886 | 86 | 52 | 13 |
| `Board_Begin` | 885 | 128 | 52 | 15 |
| `Board_Stage` | 817 | 140 | 51 | 13 |
| `Board_Setting` | 808 | 100 | 63 | 12 |
| `Board_Challange` | 804 | 124 | 52 | 13 |
| `Board_BattlePassPro` | 802 | 103 | 29 | 12 |
| `Board_Endgame` | 787 | 97 | 46 | 14 |
| `Board_Reborn` | 728 | 121 | 54 | 13 |
| `Board_QuestRewards` | 692 | 101 | 27 | 10 |
| `Board_Vip` | 668 | 80 | 26 | 10 |
| `Popup_ShipSalePack` | 641 | 16 | 5 | 9 |
| `Board_MiniCombo` | 589 | 69 | 36 | 9 |
| `Popup_HolidayGift` | 568 | 78 | 9 | 8 |
| `Board_EventSeasonPass` | 567 | 92 | 28 | 10 |
| `Popup_HolidayGift` | 538 | 68 | 11 | 7 |
| `Tab_Boss` | 529 | 4 | 1 | 7 |
| `Board_ShopEnergy` | 516 | 87 | 31 | 8 |
| `Popup_WeekSales` | 492 | 62 | 14 | 6 |
| `Board_UserProfile` | 488 | 60 | 50 | 8 |
| `Board_EventSeasonPass` | 476 | 70 | 20 | 7 |
| `Board_Quest` | 381 | 107 | 39 | 5 |

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
