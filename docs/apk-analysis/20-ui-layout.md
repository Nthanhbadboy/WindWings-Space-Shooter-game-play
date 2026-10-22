# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **621**
- tổng node: **86201**
- dung lượng thô (gz): **1.7 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 74967 |
| `SpriteRenderer` | 40452 |
| `MeshRenderer` | 12404 |
| `RectTransform` | 11234 |
| `TextMeshPro` | 11168 |
| `MeshFilter` | 10185 |
| `BoxCollider2D` | 6062 |
| `Animator` | 4362 |
| `ButtonEvents` | 4195 |
| `Button_Sound` | 4077 |
| `ParticleSystem` | 3284 |
| `ParticleSystemRenderer` | 3284 |
| `LanguageTextMeshPro` | 2994 |
| `ChangeSorting` | 1800 |
| `BgObjectScaler` | 1350 |
| `Popup_Notices` | 1048 |
| `Box_Rewards` | 919 |
| `TMP_SubMesh` | 852 |
| `UIObjectAnchors` | 608 |
| `Shop_Cell` | 534 |
| `FixUIShop` | 507 |
| `Rigidbody2D` | 364 |
| `ObjectPool` | 331 |
| `Enemy_Datas` | 289 |
| `Enemy_Health` | 289 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 431 | 336 | 61 |
| `Board_PVP` | 2456 | 384 | 164 | 38 |
| `Board_FightBoss` | 2272 | 106 | 47 | 37 |
| `Board_SelectBoss` | 2157 | 88 | 15 | 31 |
| `Tab_Boss` | 1870 | 5 | 0 | 29 |
| `Board_Players` | 1823 | 212 | 79 | 30 |
| `Board_BattlePass` | 1750 | 242 | 65 | 18 |
| `Board_Arena` | 1722 | 209 | 106 | 29 |
| `Board_Survival` | 1375 | 196 | 80 | 22 |
| `Board_Ranks` | 1355 | 209 | 90 | 22 |
| `Board_Survival` | 1262 | 195 | 79 | 21 |
| `Board_TechLab` | 1192 | 145 | 72 | 18 |
| `Board_Begin` | 964 | 126 | 52 | 16 |
| `Board_BattlePassPro` | 911 | 126 | 42 | 14 |
| `Popup_WatchVideos` | 908 | 164 | 47 | 13 |
| `Board_WinnerBenefits` | 908 | 148 | 56 | 14 |
| `Popup_WatchVideos` | 871 | 151 | 47 | 13 |
| `Board_GiftLogin` | 853 | 128 | 26 | 12 |
| `Board_Stage` | 823 | 139 | 53 | 13 |
| `Board_MiniCombo` | 823 | 88 | 51 | 12 |
| `Board_Endgame` | 821 | 120 | 50 | 14 |
| `Board_Reborn` | 783 | 138 | 53 | 14 |
| `Board_Vip` | 762 | 78 | 24 | 11 |
| `Board_Challange` | 753 | 121 | 48 | 12 |
| `Board_Combo` | 712 | 80 | 36 | 11 |
| `Popup_ShipSalePack` | 681 | 15 | 7 | 10 |
| `Board_Setting` | 649 | 102 | 64 | 11 |
| `Tab_Boss` | 563 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 524 | 73 | 9 | 7 |
| `Board_EventSeasonPass` | 480 | 77 | 22 | 7 |
| `Board_ShopEnergy` | 472 | 114 | 34 | 8 |
| `Popup_WatchVideosOld` | 364 | 58 | 12 | 5 |
| `Popup_WatchVideosOld` | 356 | 60 | 13 | 5 |
| `Board_Profile` | 349 | 27 | 16 | 5 |
| `Board_Begin` | 339 | 29 | 14 | 5 |
| `Popup_BuyMoreGems` | 335 | 63 | 13 | 5 |
| `Popup_Notices` | 335 | 64 | 15 | 5 |
| `Popup_BuyMoreGems` | 334 | 61 | 15 | 5 |
| `Popup_Notices` | 330 | 58 | 14 | 5 |
| `Popup_Notices` | 329 | 64 | 14 | 5 |

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
