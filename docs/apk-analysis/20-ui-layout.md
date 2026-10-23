# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **597**
- tổng node: **82148**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 71433 |
| `SpriteRenderer` | 38849 |
| `MeshRenderer` | 11924 |
| `RectTransform` | 10715 |
| `TextMeshPro` | 10674 |
| `MeshFilter` | 9887 |
| `BoxCollider2D` | 5539 |
| `Animator` | 4185 |
| `ButtonEvents` | 3794 |
| `Button_Sound` | 3699 |
| `ParticleSystem` | 3029 |
| `ParticleSystemRenderer` | 3029 |
| `LanguageTextMeshPro` | 2716 |
| `ChangeSorting` | 1727 |
| `BgObjectScaler` | 1286 |
| `Popup_Notices` | 1012 |
| `Box_Rewards` | 925 |
| `TMP_SubMesh` | 844 |
| `Shop_Cell` | 530 |
| `UIObjectAnchors` | 497 |
| `FixUIShop` | 495 |
| `Rigidbody2D` | 317 |
| `ObjectPool` | 303 |
| `Enemy_Datas` | 258 |
| `Enemy_Health` | 258 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 439 | 336 | 62 |
| `Board_Shop` | 3333 | 474 | 143 | 45 |
| `Board_PVP` | 2661 | 402 | 163 | 40 |
| `Board_FightBoss` | 2491 | 109 | 45 | 39 |
| `Board_SelectBoss` | 2388 | 104 | 16 | 33 |
| `Board_BattlePass` | 1743 | 233 | 62 | 18 |
| `Board_Ranks` | 1563 | 225 | 90 | 24 |
| `Tab_Boss` | 1454 | 6 | 0 | 24 |
| `Board_Ranks` | 1399 | 211 | 91 | 22 |
| `Board_TechLab` | 1239 | 157 | 64 | 18 |
| `Board_Survival` | 1148 | 186 | 80 | 19 |
| `Board_Players` | 1104 | 172 | 60 | 18 |
| `Board_Begin` | 1073 | 146 | 50 | 16 |
| `Board_Endgame` | 889 | 125 | 51 | 15 |
| `Board_GiftLogin` | 856 | 131 | 27 | 13 |
| `Popup_WatchVideos` | 841 | 149 | 48 | 13 |
| `Board_BattlePassPro` | 826 | 103 | 28 | 12 |
| `Board_Vip` | 785 | 100 | 27 | 11 |
| `Board_Challange` | 772 | 130 | 49 | 12 |
| `Board_Reborn` | 765 | 129 | 51 | 14 |
| `Board_Stage` | 731 | 125 | 51 | 11 |
| `Popup_ShipSalePack` | 634 | 17 | 7 | 9 |
| `Board_ShopEnergy` | 608 | 107 | 33 | 9 |
| `Popup_HolidayGift` | 581 | 76 | 11 | 8 |
| `Tab_Boss` | 561 | 7 | 1 | 7 |
| `Board_EventSeasonPass` | 512 | 84 | 26 | 9 |
| `Board_EventSeasonPass` | 490 | 68 | 22 | 7 |
| `Popup_WeekSales` | 472 | 59 | 13 | 6 |
| `Board_Begin` | 391 | 35 | 15 | 5 |
| `Board_Quest` | 374 | 109 | 38 | 5 |
| `Popup_WatchVideosOld` | 359 | 60 | 13 | 5 |
| `Board_Reborn_IAP` | 344 | 68 | 15 | 5 |
| `Popup_BuyMoreGems` | 342 | 67 | 15 | 5 |
| `Board_Talents` | 340 | 30 | 10 | 4 |
| `Popup_Notices` | 337 | 64 | 15 | 5 |
| `Popup_BuyMoreGems` | 335 | 67 | 15 | 5 |
| `Popup_BuyMoreGems` | 332 | 65 | 15 | 5 |
| `Popup_Notices` | 332 | 58 | 15 | 5 |
| `Popup_PremiumDailyRewards` | 326 | 35 | 4 | 5 |
| `Tab_Boss` | 320 | 9 | 1 | 5 |

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
