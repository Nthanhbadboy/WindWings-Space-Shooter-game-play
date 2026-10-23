# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **563**
- tổng node: **85471**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 74672 |
| `SpriteRenderer` | 40064 |
| `MeshRenderer` | 11949 |
| `RectTransform` | 10799 |
| `TextMeshPro` | 10753 |
| `MeshFilter` | 9599 |
| `BoxCollider2D` | 5820 |
| `Animator` | 4414 |
| `ButtonEvents` | 4020 |
| `Button_Sound` | 3903 |
| `ParticleSystem` | 3257 |
| `ParticleSystemRenderer` | 3257 |
| `LanguageTextMeshPro` | 2835 |
| `ChangeSorting` | 1765 |
| `BgObjectScaler` | 1278 |
| `Popup_Notices` | 1020 |
| `Box_Rewards` | 886 |
| `TMP_SubMesh` | 783 |
| `UIObjectAnchors` | 594 |
| `Shop_Cell` | 531 |
| `FixUIShop` | 482 |
| `Rigidbody2D` | 390 |
| `ObjectPool` | 363 |
| `Enemy_Datas` | 316 |
| `Enemy_Health` | 316 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 452 | 339 | 62 |
| `Board_Shop` | 3048 | 523 | 143 | 45 |
| `Board_PVP` | 2859 | 405 | 168 | 43 |
| `Board_FightBoss` | 2478 | 115 | 46 | 39 |
| `Board_SelectBoss` | 2472 | 100 | 14 | 34 |
| `Board_Arena` | 1967 | 277 | 126 | 32 |
| `Tab_Boss` | 1871 | 6 | 0 | 29 |
| `Board_BattlePass` | 1869 | 263 | 70 | 19 |
| `Board_Players` | 1761 | 171 | 73 | 29 |
| `Board_Ranks` | 1509 | 232 | 91 | 24 |
| `Board_Ranks` | 1457 | 205 | 90 | 23 |
| `Board_Survival` | 1430 | 200 | 82 | 23 |
| `Board_Survival` | 1310 | 204 | 80 | 21 |
| `Board_TechLab` | 1302 | 153 | 76 | 19 |
| `Board_Drones` | 1047 | 133 | 60 | 17 |
| `Popup_WatchVideos` | 929 | 154 | 48 | 13 |
| `Board_Combo` | 923 | 96 | 54 | 14 |
| `Popup_WatchVideos` | 888 | 156 | 42 | 13 |
| `Board_WinnerBenefits` | 876 | 124 | 53 | 13 |
| `Board_Endgame` | 838 | 124 | 50 | 15 |
| `Board_Begin` | 829 | 111 | 50 | 15 |
| `Board_Stage` | 764 | 132 | 52 | 12 |
| `Board_Vip` | 686 | 84 | 27 | 10 |
| `Board_Challange` | 660 | 125 | 52 | 11 |
| `Popup_ShipSalePack` | 635 | 16 | 7 | 9 |
| `Board_UserProfile` | 567 | 61 | 49 | 9 |
| `Tab_Boss` | 555 | 7 | 1 | 7 |
| `Board_EventSeasonPass` | 550 | 92 | 29 | 10 |
| `Popup_HolidayGift` | 542 | 74 | 11 | 8 |
| `Popup_HolidayGift` | 529 | 61 | 9 | 7 |
| `Board_EventSeasonPass` | 494 | 72 | 22 | 7 |
| `Board_Begin` | 406 | 34 | 15 | 5 |
| `Popup_PvPRankings` | 367 | 47 | 14 | 7 |
| `Popup_WatchVideosOld` | 363 | 56 | 13 | 5 |
| `Board_Talents` | 339 | 29 | 10 | 4 |
| `Popup_BuyMoreGems` | 333 | 62 | 15 | 5 |
| `Board_Talents` | 324 | 31 | 10 | 4 |
| `Popup_BuyMoreGems` | 324 | 57 | 14 | 5 |
| `Popup_Notices` | 324 | 56 | 15 | 5 |
| `Board_Reborn_IAP` | 323 | 60 | 14 | 5 |

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
