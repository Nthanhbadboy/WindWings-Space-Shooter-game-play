# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **614**
- tổng node: **83299**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 71899 |
| `SpriteRenderer` | 39659 |
| `MeshRenderer` | 12633 |
| `RectTransform` | 11400 |
| `TextMeshPro` | 11342 |
| `MeshFilter` | 10344 |
| `BoxCollider2D` | 6129 |
| `Animator` | 4371 |
| `ButtonEvents` | 4251 |
| `Button_Sound` | 4124 |
| `LanguageTextMeshPro` | 2847 |
| `ParticleSystem` | 2548 |
| `ParticleSystemRenderer` | 2548 |
| `ChangeSorting` | 1822 |
| `BgObjectScaler` | 1363 |
| `Popup_Notices` | 1055 |
| `Box_Rewards` | 954 |
| `TMP_SubMesh` | 845 |
| `Shop_Cell` | 584 |
| `UIObjectAnchors` | 575 |
| `FixUIShop` | 534 |
| `LineRenderer` | 213 |
| `AutoSetVipIcon` | 195 |
| `ObjectPool` | 179 |
| `Stage_Behaviour` | 177 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 416 | 337 | 61 |
| `Board_Shop` | 3578 | 616 | 172 | 50 |
| `Board_PVP` | 2529 | 365 | 164 | 38 |
| `Board_SelectBoss` | 1878 | 95 | 17 | 28 |
| `Board_Players` | 1752 | 198 | 80 | 29 |
| `Board_BattlePass` | 1739 | 240 | 64 | 17 |
| `Board_Arena` | 1736 | 210 | 106 | 30 |
| `Board_TechLab` | 1340 | 162 | 62 | 19 |
| `Board_Ranks` | 1331 | 193 | 92 | 21 |
| `Board_Survival` | 1239 | 202 | 76 | 21 |
| `Board_Survival` | 1142 | 188 | 84 | 19 |
| `Board_Drones` | 991 | 132 | 59 | 17 |
| `Board_Begin` | 925 | 126 | 52 | 16 |
| `Popup_WatchVideos` | 917 | 145 | 49 | 13 |
| `Popup_WatchVideos` | 912 | 164 | 48 | 13 |
| `Board_GiftLogin` | 855 | 129 | 29 | 13 |
| `Board_WinnerBenefits` | 850 | 130 | 54 | 14 |
| `Board_Endgame` | 813 | 114 | 50 | 14 |
| `Board_Reborn` | 767 | 134 | 57 | 14 |
| `Board_Vip` | 748 | 84 | 25 | 11 |
| `Board_QuestRewards` | 630 | 94 | 27 | 9 |
| `Popup_ShipSalePack` | 614 | 19 | 7 | 9 |
| `Board_Challange` | 576 | 104 | 44 | 10 |
| `Popup_HolidayGift` | 555 | 66 | 11 | 7 |
| `Popup_HolidayGift` | 495 | 70 | 9 | 7 |
| `Board_EventSeasonPass` | 441 | 64 | 18 | 7 |
| `Board_UserProfile` | 434 | 41 | 47 | 7 |
| `Board_Begin` | 383 | 33 | 14 | 5 |
| `Popup_WatchVideosOld` | 374 | 60 | 13 | 5 |
| `Board_Quest` | 359 | 104 | 39 | 5 |
| `Board_Talents` | 352 | 30 | 10 | 4 |
| `Popup_WatchVideosOld` | 348 | 59 | 12 | 5 |
| `Board_Talents` | 346 | 29 | 10 | 4 |
| `Board_Reborn_IAP` | 345 | 61 | 15 | 5 |
| `Popup_BuyMoreGems` | 342 | 66 | 15 | 5 |
| `Popup_Notices` | 341 | 66 | 15 | 5 |
| `Popup_BuyMoreGems` | 333 | 66 | 14 | 5 |
| `Popup_BuyMoreGems` | 331 | 56 | 15 | 5 |
| `Popup_BuyMoreGems` | 324 | 63 | 14 | 5 |
| `Popup_BuyMoreGems` | 322 | 65 | 15 | 5 |

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
