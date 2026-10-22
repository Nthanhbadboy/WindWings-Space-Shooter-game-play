# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **583**
- tổng node: **81854**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 70614 |
| `SpriteRenderer` | 38604 |
| `MeshRenderer` | 12382 |
| `RectTransform` | 11240 |
| `TextMeshPro` | 11186 |
| `MeshFilter` | 10232 |
| `BoxCollider2D` | 5902 |
| `Animator` | 4169 |
| `ButtonEvents` | 4082 |
| `Button_Sound` | 3969 |
| `LanguageTextMeshPro` | 2788 |
| `ParticleSystem` | 2762 |
| `ParticleSystemRenderer` | 2762 |
| `ChangeSorting` | 1778 |
| `BgObjectScaler` | 1330 |
| `Popup_Notices` | 1046 |
| `Box_Rewards` | 917 |
| `TMP_SubMesh` | 796 |
| `Shop_Cell` | 622 |
| `FixUIShop` | 556 |
| `UIObjectAnchors` | 530 |
| `Rigidbody2D` | 223 |
| `LineRenderer` | 199 |
| `AutoSetVipIcon` | 190 |
| `Stage_Behaviour` | 177 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 440 | 342 | 61 |
| `Board_Shop` | 3898 | 634 | 172 | 52 |
| `Board_FightBoss` | 2306 | 102 | 45 | 37 |
| `Board_PVP` | 2301 | 334 | 152 | 36 |
| `Board_Arena` | 1814 | 242 | 114 | 29 |
| `Board_Players` | 1761 | 184 | 75 | 28 |
| `Board_Survival` | 1356 | 184 | 80 | 21 |
| `Board_Survival` | 1282 | 205 | 83 | 21 |
| `Board_Ranks` | 1281 | 168 | 76 | 20 |
| `Board_Drones` | 968 | 133 | 57 | 17 |
| `Board_BattlePassPro` | 946 | 126 | 42 | 14 |
| `Board_Begin` | 908 | 114 | 44 | 15 |
| `Board_Combo` | 882 | 88 | 52 | 13 |
| `Board_GiftLogin` | 865 | 130 | 28 | 13 |
| `Popup_WatchVideos` | 856 | 167 | 47 | 13 |
| `Board_Endgame` | 798 | 112 | 42 | 14 |
| `Board_Stage` | 751 | 139 | 53 | 12 |
| `Board_Challange` | 749 | 132 | 54 | 12 |
| `Board_QuestRewards` | 715 | 105 | 27 | 10 |
| `Board_UserProfile` | 712 | 57 | 50 | 10 |
| `Board_Vip` | 706 | 85 | 26 | 10 |
| `Popup_WatchVideos` | 636 | 119 | 39 | 10 |
| `Popup_ShipSalePack` | 615 | 17 | 7 | 9 |
| `Board_ShopEnergy` | 608 | 116 | 32 | 9 |
| `Tab_Boss` | 549 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 542 | 69 | 8 | 7 |
| `Board_EventSeasonPass` | 529 | 87 | 28 | 9 |
| `Popup_WeekSales` | 483 | 61 | 14 | 6 |
| `Board_EventSeasonPass` | 481 | 72 | 22 | 7 |
| `Popup_HolidayGift` | 481 | 55 | 9 | 6 |
| `Board_Quest` | 365 | 99 | 39 | 5 |
| `Board_Profile` | 365 | 25 | 16 | 5 |
| `Board_Reborn_IAP` | 362 | 70 | 15 | 5 |
| `Popup_WatchVideosOld` | 355 | 58 | 13 | 5 |
| `Popup_Notices` | 340 | 65 | 15 | 5 |
| `Popup_BuyMoreGems` | 339 | 69 | 15 | 5 |
| `Popup_BuyMoreGems` | 338 | 61 | 15 | 5 |
| `Popup_BuyMoreGems` | 328 | 56 | 15 | 5 |
| `Popup_Notices` | 324 | 63 | 15 | 5 |
| `Board_Talents` | 322 | 29 | 9 | 4 |

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
