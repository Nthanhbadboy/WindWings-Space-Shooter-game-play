# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **632**
- tổng node: **84737**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 73543 |
| `SpriteRenderer` | 39780 |
| `MeshRenderer` | 12444 |
| `RectTransform` | 11194 |
| `TextMeshPro` | 11147 |
| `MeshFilter` | 10297 |
| `BoxCollider2D` | 6091 |
| `Animator` | 4242 |
| `ButtonEvents` | 4237 |
| `Button_Sound` | 4119 |
| `LanguageTextMeshPro` | 2950 |
| `ParticleSystem` | 2754 |
| `ParticleSystemRenderer` | 2754 |
| `ChangeSorting` | 1811 |
| `BgObjectScaler` | 1371 |
| `Popup_Notices` | 1087 |
| `TMP_SubMesh` | 892 |
| `Box_Rewards` | 766 |
| `UIObjectAnchors` | 578 |
| `Shop_Cell` | 558 |
| `FixUIShop` | 521 |
| `Rigidbody2D` | 252 |
| `LineRenderer` | 231 |
| `AutoSetVipIcon` | 191 |
| `CircleCollider2D` | 182 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 436 | 333 | 61 |
| `Board_PVP` | 2866 | 398 | 170 | 42 |
| `Board_FightBoss` | 2509 | 85 | 42 | 39 |
| `Board_BattlePass` | 1886 | 264 | 68 | 19 |
| `Board_Arena` | 1794 | 207 | 104 | 30 |
| `Tab_Boss` | 1757 | 6 | 0 | 27 |
| `Board_Players` | 1608 | 134 | 68 | 26 |
| `Board_Survival` | 1352 | 188 | 78 | 22 |
| `Board_Survival` | 1310 | 207 | 80 | 22 |
| `Board_Ranks` | 1303 | 169 | 80 | 20 |
| `Board_TechLab` | 1222 | 142 | 75 | 17 |
| `Board_Ranks` | 1145 | 199 | 82 | 19 |
| `Board_WinnerBenefits` | 1022 | 141 | 56 | 15 |
| `Board_Begin` | 1012 | 127 | 48 | 16 |
| `Board_Drones` | 954 | 131 | 56 | 16 |
| `Board_BattlePassPro` | 951 | 116 | 39 | 15 |
| `Popup_WatchVideos` | 879 | 161 | 50 | 13 |
| `Popup_WatchVideos` | 833 | 153 | 48 | 12 |
| `Board_GiftLogin` | 825 | 111 | 24 | 12 |
| `Board_Vip` | 789 | 97 | 24 | 11 |
| `Board_Endgame` | 769 | 104 | 42 | 14 |
| `Board_Challange` | 751 | 134 | 52 | 12 |
| `Popup_ShipSalePack` | 696 | 19 | 7 | 10 |
| `Board_QuestRewards` | 650 | 93 | 27 | 9 |
| `Board_ShopEnergy` | 618 | 113 | 35 | 9 |
| `Board_EventSeasonPass` | 552 | 94 | 29 | 9 |
| `Popup_HolidayGift` | 526 | 67 | 11 | 7 |
| `Board_Combo` | 517 | 65 | 23 | 8 |
| `Board_Begin` | 407 | 34 | 14 | 5 |
| `Board_EventSeasonPass` | 388 | 69 | 21 | 6 |
| `Board_Quest` | 376 | 101 | 39 | 5 |
| `Popup_WatchVideosOld` | 361 | 55 | 13 | 5 |
| `Board_Reborn_IAP` | 360 | 70 | 15 | 5 |
| `Popup_Notices` | 357 | 68 | 15 | 5 |
| `Popup_BuyMoreGems` | 346 | 65 | 15 | 5 |
| `Popup_Notices` | 341 | 61 | 15 | 5 |
| `Popup_WatchVideosOld` | 333 | 52 | 13 | 5 |
| `Popup_BuyMoreGems` | 332 | 61 | 15 | 5 |
| `Popup_Notices` | 331 | 62 | 15 | 5 |
| `Popup_BuyMoreGems` | 325 | 69 | 15 | 5 |

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
