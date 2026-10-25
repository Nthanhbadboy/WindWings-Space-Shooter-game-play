# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **738**
- tổng node: **103137**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (55)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89296 |
| `SpriteRenderer` | 48603 |
| `MeshRenderer` | 15386 |
| `RectTransform` | 13841 |
| `TextMeshPro` | 13778 |
| `MeshFilter` | 12680 |
| `BoxCollider2D` | 7315 |
| `Animator` | 5293 |
| `ButtonEvents` | 5017 |
| `Button_Sound` | 4872 |
| `ParticleSystem` | 3648 |
| `ParticleSystemRenderer` | 3648 |
| `LanguageTextMeshPro` | 3615 |
| `ChangeSorting` | 2224 |
| `BgObjectScaler` | 1638 |
| `Popup_Notices` | 1264 |
| `Box_Rewards` | 1228 |
| `TMP_SubMesh` | 1066 |
| `UIObjectAnchors` | 749 |
| `Shop_Cell` | 687 |
| `FixUIShop` | 617 |
| `Rigidbody2D` | 350 |
| `ObjectPool` | 320 |
| `LineRenderer` | 297 |
| `Enemy_Datas` | 265 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4237 | 357 | 208 | 52 |
| `Board_Shop` | 3451 | 515 | 153 | 46 |
| `Board_PVP` | 2712 | 392 | 169 | 41 |
| `Board_FightBoss` | 2388 | 103 | 41 | 39 |
| `Board_SelectBoss` | 2018 | 97 | 15 | 27 |
| `Tab_Boss` | 1809 | 5 | 0 | 28 |
| `Board_Players` | 1790 | 205 | 77 | 29 |
| `Board_Arena` | 1726 | 285 | 115 | 28 |
| `Board_BattlePass` | 1722 | 233 | 63 | 18 |
| `Board_Ranks` | 1401 | 202 | 88 | 22 |
| `Board_Ranks` | 1324 | 200 | 87 | 20 |
| `Board_TechLab` | 1301 | 136 | 61 | 19 |
| `Board_Survival` | 1281 | 204 | 78 | 21 |
| `Board_Survival` | 1264 | 189 | 79 | 21 |
| `Board_Begin` | 1018 | 142 | 55 | 16 |
| `Board_Drones` | 976 | 140 | 59 | 17 |
| `Board_WinnerBenefits` | 972 | 143 | 54 | 15 |
| `Board_MiniCombo` | 940 | 98 | 60 | 13 |
| `Board_BattlePassPro` | 887 | 113 | 39 | 13 |
| `Popup_WatchVideos` | 869 | 155 | 47 | 13 |
| `Board_Reborn` | 837 | 139 | 58 | 14 |
| `Board_Combo` | 832 | 85 | 47 | 12 |
| `Board_Endgame` | 822 | 128 | 49 | 15 |
| `Board_GiftLogin` | 820 | 121 | 27 | 12 |
| `Board_Stage` | 802 | 139 | 50 | 12 |
| `Board_Vip` | 790 | 104 | 25 | 11 |
| `Board_Setting` | 783 | 104 | 66 | 12 |
| `Popup_WatchVideos` | 777 | 123 | 48 | 11 |
| `Board_Challange` | 776 | 130 | 50 | 12 |
| `Popup_ShipSalePack` | 679 | 17 | 7 | 10 |
| `Board_QuestRewards` | 677 | 100 | 27 | 10 |
| `Board_UserProfile` | 546 | 62 | 48 | 9 |
| `Board_EventSeasonPass` | 519 | 65 | 22 | 8 |
| `Board_EventSeasonPass` | 497 | 89 | 27 | 9 |
| `Popup_HolidayGift` | 493 | 66 | 11 | 7 |
| `Popup_HolidayGift` | 474 | 67 | 11 | 7 |
| `Board_ShopEnergy` | 469 | 79 | 29 | 8 |
| `Popup_WeekSales` | 403 | 50 | 12 | 6 |
| `Board_Reborn_IAP` | 369 | 65 | 15 | 5 |
| `Board_Begin` | 357 | 33 | 13 | 5 |

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
