# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **598**
- tổng node: **83053**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 72050 |
| `SpriteRenderer` | 38762 |
| `MeshRenderer` | 12165 |
| `RectTransform` | 11003 |
| `TextMeshPro` | 10951 |
| `MeshFilter` | 10090 |
| `BoxCollider2D` | 5950 |
| `Animator` | 4189 |
| `ButtonEvents` | 4137 |
| `Button_Sound` | 4039 |
| `ParticleSystem` | 3000 |
| `ParticleSystemRenderer` | 3000 |
| `LanguageTextMeshPro` | 2946 |
| `ChangeSorting` | 1776 |
| `BgObjectScaler` | 1321 |
| `Popup_Notices` | 1046 |
| `TMP_SubMesh` | 821 |
| `Box_Rewards` | 763 |
| `Shop_Cell` | 540 |
| `UIObjectAnchors` | 530 |
| `FixUIShop` | 525 |
| `Rigidbody2D` | 301 |
| `ObjectPool` | 277 |
| `LineRenderer` | 271 |
| `Enemy_Datas` | 233 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 444 | 340 | 60 |
| `Board_Shop` | 3129 | 490 | 137 | 44 |
| `Board_SelectBoss` | 2194 | 103 | 17 | 29 |
| `Tab_Boss` | 1967 | 5 | 0 | 30 |
| `Board_Arena` | 1799 | 198 | 104 | 29 |
| `Board_Players` | 1777 | 196 | 76 | 28 |
| `Board_Ranks` | 1540 | 231 | 92 | 24 |
| `Board_Ranks` | 1395 | 209 | 90 | 22 |
| `Board_TechLab` | 1358 | 156 | 77 | 19 |
| `Board_Survival` | 1217 | 174 | 81 | 19 |
| `Board_Survival` | 1148 | 188 | 82 | 19 |
| `Board_Drones` | 1013 | 123 | 58 | 16 |
| `Board_Combo` | 958 | 96 | 60 | 14 |
| `Board_Begin` | 957 | 139 | 53 | 16 |
| `Board_MiniCombo` | 925 | 100 | 53 | 14 |
| `Board_Reborn` | 913 | 147 | 62 | 16 |
| `Popup_WatchVideos` | 909 | 161 | 50 | 13 |
| `Board_GiftLogin` | 904 | 124 | 29 | 13 |
| `Popup_WatchVideos` | 836 | 150 | 50 | 12 |
| `Board_Setting` | 808 | 93 | 65 | 12 |
| `Board_Challange` | 805 | 138 | 50 | 13 |
| `Board_WinnerBenefits` | 773 | 149 | 54 | 13 |
| `Board_Stage` | 773 | 132 | 49 | 12 |
| `Board_Vip` | 681 | 82 | 23 | 10 |
| `Board_QuestRewards` | 631 | 93 | 23 | 9 |
| `Board_EventSeasonPass` | 576 | 92 | 29 | 10 |
| `Tab_Boss` | 566 | 8 | 1 | 7 |
| `Popup_ShipSalePack` | 564 | 16 | 7 | 8 |
| `Popup_HolidayGift` | 477 | 67 | 11 | 7 |
| `Popup_WeekSales` | 476 | 55 | 14 | 6 |
| `Board_EventSeasonPass` | 474 | 74 | 22 | 7 |
| `Board_Begin` | 412 | 36 | 14 | 5 |
| `Board_ShopEnergy` | 385 | 95 | 32 | 7 |
| `Board_Quest` | 376 | 108 | 39 | 5 |
| `Popup_WatchVideosOld` | 367 | 58 | 13 | 5 |
| `Board_Reborn_IAP` | 353 | 65 | 15 | 5 |
| `Board_Reborn_IAP` | 348 | 68 | 15 | 5 |
| `Board_Profile` | 343 | 25 | 16 | 5 |
| `Popup_BuyMoreGems` | 340 | 62 | 15 | 5 |
| `Popup_Notices` | 331 | 62 | 14 | 5 |

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
