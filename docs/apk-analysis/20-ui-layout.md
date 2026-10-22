# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **608**
- tổng node: **80806**
- dung lượng thô (gz): **1.4 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 69860 |
| `SpriteRenderer` | 39004 |
| `MeshRenderer` | 12074 |
| `RectTransform` | 10946 |
| `TextMeshPro` | 10887 |
| `MeshFilter` | 10020 |
| `BoxCollider2D` | 5796 |
| `Animator` | 4140 |
| `ButtonEvents` | 4052 |
| `Button_Sound` | 3931 |
| `LanguageTextMeshPro` | 2749 |
| `ParticleSystem` | 2288 |
| `ParticleSystemRenderer` | 2288 |
| `ChangeSorting` | 1733 |
| `BgObjectScaler` | 1308 |
| `Popup_Notices` | 997 |
| `Box_Rewards` | 883 |
| `TMP_SubMesh` | 822 |
| `Shop_Cell` | 566 |
| `FixUIShop` | 514 |
| `UIObjectAnchors` | 477 |
| `AutoSetVipIcon` | 193 |
| `LineRenderer` | 184 |
| `Stage_Behaviour` | 179 |
| `SpriteMask` | 146 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 0 | 340 | 58 |
| `Board_Shop` | 3441 | 0 | 163 | 42 |
| `Board_PVP` | 3005 | 0 | 173 | 40 |
| `Board_Players` | 1797 | 0 | 77 | 27 |
| `Board_Ranks` | 1480 | 0 | 88 | 20 |
| `Board_TechLab` | 1307 | 0 | 65 | 18 |
| `Board_Survival` | 1280 | 0 | 87 | 18 |
| `Board_BattlePassPro` | 988 | 0 | 44 | 14 |
| `Board_WinnerBenefits` | 975 | 0 | 56 | 13 |
| `Board_Begin` | 969 | 0 | 53 | 15 |
| `Board_Combo` | 931 | 0 | 56 | 13 |
| `Board_GiftLogin` | 906 | 0 | 28 | 12 |
| `Popup_WatchVideos` | 904 | 0 | 49 | 12 |
| `Board_Setting` | 850 | 0 | 64 | 12 |
| `Board_Reborn` | 799 | 0 | 58 | 13 |
| `Board_MiniCombo` | 794 | 0 | 46 | 11 |
| `Board_Challange` | 775 | 0 | 53 | 11 |
| `Popup_ShipSalePack` | 728 | 0 | 7 | 10 |
| `Board_Vip` | 724 | 0 | 23 | 10 |
| `Board_QuestRewards` | 673 | 0 | 25 | 9 |
| `Board_ShopEnergy` | 588 | 0 | 33 | 8 |
| `Board_UserProfile` | 550 | 0 | 48 | 7 |
| `Board_EventSeasonPass` | 466 | 0 | 21 | 6 |
| `Popup_WeekSales` | 452 | 0 | 12 | 6 |
| `Popup_HolidayGift` | 434 | 0 | 10 | 5 |
| `Popup_BuyMoreGems` | 359 | 0 | 15 | 5 |
| `Board_Quest` | 355 | 0 | 38 | 4 |
| `Popup_BuyMoreGems` | 347 | 0 | 15 | 5 |
| `Popup_WatchVideosOld` | 346 | 0 | 13 | 4 |
| `Popup_Notices` | 342 | 0 | 15 | 5 |
| `Board_Talents` | 341 | 0 | 10 | 4 |
| `Popup_Notices` | 341 | 0 | 15 | 5 |
| `Board_Profile` | 336 | 0 | 15 | 4 |
| `Popup_Notices` | 335 | 0 | 14 | 5 |
| `Popup_Notices` | 334 | 0 | 15 | 5 |
| `Popup_BuyMoreGems` | 333 | 0 | 15 | 5 |
| `Popup_BuyMoreGems` | 331 | 0 | 15 | 5 |
| `Board_Begin` | 328 | 0 | 15 | 4 |
| `Popup_BuyMoreGems` | 325 | 0 | 15 | 5 |
| `Popup_BuyMoreGems` | 324 | 0 | 15 | 5 |

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
