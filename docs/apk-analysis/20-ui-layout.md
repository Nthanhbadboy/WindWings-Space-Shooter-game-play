# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **635**
- tổng node: **78867**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 68399 |
| `SpriteRenderer` | 37263 |
| `MeshRenderer` | 11589 |
| `RectTransform` | 10468 |
| `TextMeshPro` | 10416 |
| `MeshFilter` | 9721 |
| `BoxCollider2D` | 5778 |
| `ButtonEvents` | 4022 |
| `Animator` | 3918 |
| `Button_Sound` | 3918 |
| `LanguageTextMeshPro` | 2860 |
| `ParticleSystem` | 2424 |
| `ParticleSystemRenderer` | 2424 |
| `ChangeSorting` | 1730 |
| `BgObjectScaler` | 1308 |
| `Popup_Notices` | 1026 |
| `TMP_SubMesh` | 801 |
| `Box_Rewards` | 777 |
| `Shop_Cell` | 521 |
| `UIObjectAnchors` | 497 |
| `FixUIShop` | 483 |
| `Rigidbody2D` | 190 |
| `AutoSetVipIcon` | 188 |
| `Stage_Behaviour` | 173 |
| `SpriteMask` | 171 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 451 | 334 | 61 |
| `Board_FightBoss` | 2395 | 113 | 41 | 38 |
| `Board_Arena` | 1976 | 251 | 124 | 31 |
| `Board_Players` | 1698 | 194 | 78 | 28 |
| `Board_Survival` | 1418 | 222 | 87 | 23 |
| `Board_Ranks` | 1388 | 189 | 91 | 22 |
| `Board_Drones` | 1036 | 148 | 60 | 17 |
| `Board_WinnerBenefits` | 994 | 136 | 54 | 14 |
| `Board_BattlePassPro` | 893 | 123 | 40 | 13 |
| `Popup_WatchVideos` | 880 | 164 | 48 | 13 |
| `Board_Endgame` | 841 | 119 | 47 | 15 |
| `Popup_WatchVideos` | 827 | 134 | 47 | 12 |
| `Board_GiftLogin` | 815 | 129 | 28 | 12 |
| `Board_Reborn` | 810 | 135 | 56 | 15 |
| `Board_Stage` | 784 | 133 | 50 | 13 |
| `Board_Challange` | 750 | 122 | 45 | 12 |
| `Board_Setting` | 746 | 97 | 67 | 12 |
| `Board_Vip` | 710 | 90 | 25 | 11 |
| `Board_MiniCombo` | 692 | 78 | 42 | 11 |
| `Board_QuestRewards` | 656 | 91 | 26 | 10 |
| `Board_UserProfile` | 636 | 58 | 48 | 10 |
| `Popup_ShipSalePack` | 577 | 17 | 7 | 9 |
| `Board_EventSeasonPass` | 574 | 82 | 28 | 9 |
| `Board_Combo` | 561 | 77 | 27 | 9 |
| `Popup_HolidayGift` | 535 | 76 | 11 | 7 |
| `Popup_HolidayGift` | 535 | 64 | 8 | 7 |
| `Board_ShopEnergy` | 534 | 80 | 33 | 8 |
| `Tab_Boss` | 532 | 9 | 1 | 7 |
| `Board_EventSeasonPass` | 450 | 73 | 22 | 7 |
| `Board_Begin` | 391 | 34 | 14 | 5 |
| `Popup_WatchVideosOld` | 364 | 57 | 12 | 5 |
| `Board_Reborn_IAP` | 362 | 72 | 15 | 5 |
| `Board_Profile` | 343 | 26 | 15 | 5 |
| `Board_Talents` | 339 | 31 | 9 | 4 |
| `Board_Profile` | 339 | 26 | 16 | 5 |
| `Popup_WeekSales` | 337 | 48 | 13 | 5 |
| `Board_Profile` | 336 | 31 | 16 | 5 |
| `Popup_BuyMoreGems` | 334 | 60 | 14 | 5 |
| `Popup_Notices` | 333 | 60 | 15 | 5 |
| `Popup_BuyMoreGems` | 332 | 62 | 15 | 5 |

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
