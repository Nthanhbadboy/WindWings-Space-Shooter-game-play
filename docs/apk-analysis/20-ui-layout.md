# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **586**
- tổng node: **76223**
- dung lượng thô (gz): **1.5 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 66188 |
| `SpriteRenderer` | 35816 |
| `MeshRenderer` | 11111 |
| `RectTransform` | 10035 |
| `TextMeshPro` | 9984 |
| `MeshFilter` | 9229 |
| `BoxCollider2D` | 5443 |
| `Animator` | 3827 |
| `ButtonEvents` | 3765 |
| `Button_Sound` | 3659 |
| `ParticleSystem` | 2718 |
| `ParticleSystemRenderer` | 2718 |
| `LanguageTextMeshPro` | 2630 |
| `ChangeSorting` | 1628 |
| `BgObjectScaler` | 1232 |
| `Popup_Notices` | 977 |
| `Box_Rewards` | 780 |
| `TMP_SubMesh` | 769 |
| `Shop_Cell` | 503 |
| `FixUIShop` | 464 |
| `UIObjectAnchors` | 461 |
| `Rigidbody2D` | 238 |
| `ObjectPool` | 207 |
| `CircleCollider2D` | 205 |
| `AutoSetVipIcon` | 181 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 430 | 337 | 60 |
| `Board_Shop` | 3495 | 558 | 160 | 48 |
| `Board_PVP` | 2814 | 416 | 171 | 43 |
| `Board_FightBoss` | 2391 | 114 | 45 | 38 |
| `Board_Players` | 1772 | 185 | 76 | 29 |
| `Tab_Boss` | 1731 | 6 | 0 | 27 |
| `Board_TechLab` | 1407 | 174 | 70 | 20 |
| `Board_Survival` | 1304 | 187 | 83 | 21 |
| `Board_Ranks` | 1236 | 191 | 84 | 20 |
| `Board_WinnerBenefits` | 945 | 145 | 54 | 14 |
| `Board_GiftLogin` | 888 | 128 | 27 | 13 |
| `Popup_WatchVideos` | 876 | 148 | 46 | 12 |
| `Board_Endgame` | 856 | 119 | 52 | 15 |
| `Board_Vip` | 772 | 90 | 25 | 11 |
| `Board_Begin` | 740 | 118 | 48 | 12 |
| `Popup_WatchVideos` | 725 | 109 | 39 | 10 |
| `Board_Setting` | 696 | 96 | 61 | 11 |
| `Board_QuestRewards` | 653 | 100 | 27 | 10 |
| `Board_Challange` | 624 | 135 | 53 | 11 |
| `Tab_Boss` | 577 | 7 | 1 | 7 |
| `Board_EventSeasonPass` | 575 | 91 | 27 | 10 |
| `Popup_ShipSalePack` | 531 | 14 | 5 | 8 |
| `Board_EventSeasonPass` | 523 | 76 | 22 | 8 |
| `Popup_HolidayGift` | 514 | 74 | 11 | 7 |
| `Popup_HolidayGift` | 490 | 68 | 11 | 7 |
| `Board_UserProfile` | 478 | 63 | 49 | 8 |
| `Board_MiniCombo` | 469 | 59 | 19 | 7 |
| `Popup_WeekSales` | 454 | 56 | 13 | 6 |
| `Popup_WatchVideosOld` | 355 | 56 | 13 | 5 |
| `Board_Reborn_IAP` | 353 | 68 | 14 | 5 |
| `Popup_BuyMoreGems` | 349 | 66 | 15 | 5 |
| `Popup_Notices` | 344 | 69 | 15 | 5 |
| `Popup_Notices` | 333 | 55 | 15 | 5 |
| `Popup_BuyMoreGems` | 328 | 59 | 14 | 5 |
| `Popup_Notices` | 327 | 67 | 15 | 5 |
| `Popup_BuyMoreGems` | 325 | 68 | 15 | 5 |
| `Board_Talents` | 323 | 28 | 9 | 4 |
| `Popup_Notices` | 322 | 60 | 14 | 5 |
| `Popup_BuyMoreGems` | 322 | 58 | 14 | 5 |
| `Popup_Notices` | 321 | 63 | 15 | 5 |

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
