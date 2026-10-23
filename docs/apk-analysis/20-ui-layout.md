# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **607**
- tổng node: **79801**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 69439 |
| `SpriteRenderer` | 37394 |
| `MeshRenderer` | 11471 |
| `RectTransform` | 10362 |
| `TextMeshPro` | 10312 |
| `MeshFilter` | 9337 |
| `BoxCollider2D` | 5753 |
| `Animator` | 4002 |
| `ButtonEvents` | 3983 |
| `Button_Sound` | 3873 |
| `LanguageTextMeshPro` | 2814 |
| `ParticleSystem` | 2750 |
| `ParticleSystemRenderer` | 2750 |
| `ChangeSorting` | 1697 |
| `BgObjectScaler` | 1268 |
| `Popup_Notices` | 1028 |
| `TMP_SubMesh` | 765 |
| `Box_Rewards` | 741 |
| `UIObjectAnchors` | 532 |
| `Shop_Cell` | 507 |
| `FixUIShop` | 460 |
| `Rigidbody2D` | 288 |
| `ObjectPool` | 227 |
| `CircleCollider2D` | 215 |
| `LineRenderer` | 211 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 433 | 335 | 61 |
| `Board_PVP` | 2667 | 368 | 169 | 40 |
| `Board_FightBoss` | 2493 | 124 | 46 | 39 |
| `Board_Arena` | 1929 | 263 | 122 | 31 |
| `Tab_Boss` | 1778 | 6 | 0 | 28 |
| `Board_BattlePass` | 1667 | 237 | 62 | 17 |
| `Board_Players` | 1642 | 183 | 73 | 28 |
| `Board_Ranks` | 1429 | 219 | 91 | 23 |
| `Board_Survival` | 1323 | 202 | 83 | 22 |
| `Board_Survival` | 1293 | 191 | 88 | 21 |
| `Board_Ranks` | 1227 | 169 | 80 | 20 |
| `Board_Drones` | 962 | 124 | 57 | 16 |
| `Board_WinnerBenefits` | 950 | 153 | 56 | 15 |
| `Board_Endgame` | 926 | 136 | 54 | 16 |
| `Popup_WatchVideos` | 866 | 149 | 49 | 12 |
| `Board_GiftLogin` | 793 | 123 | 25 | 12 |
| `Board_Challange` | 774 | 128 | 52 | 12 |
| `Board_Vip` | 747 | 98 | 27 | 11 |
| `Board_Begin` | 732 | 81 | 42 | 11 |
| `Board_Stage` | 724 | 136 | 51 | 12 |
| `Popup_WatchVideos` | 670 | 91 | 30 | 9 |
| `Board_Combo` | 667 | 82 | 48 | 10 |
| `Popup_ShipSalePack` | 645 | 16 | 7 | 9 |
| `Board_EventSeasonPass` | 576 | 90 | 29 | 10 |
| `Tab_Boss` | 559 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 534 | 65 | 11 | 7 |
| `Board_EventSeasonPass` | 483 | 71 | 22 | 7 |
| `Board_Begin` | 353 | 26 | 5 | 4 |
| `Popup_WatchVideosOld` | 352 | 57 | 13 | 5 |
| `Popup_WatchVideosOld` | 348 | 56 | 13 | 5 |
| `Board_Profile` | 343 | 24 | 16 | 5 |
| `Popup_BuyMoreGems` | 340 | 64 | 15 | 5 |
| `Popup_Notices` | 340 | 68 | 15 | 5 |
| `Popup_BuyMoreGems` | 331 | 65 | 15 | 5 |
| `Popup_Notices` | 330 | 59 | 14 | 5 |
| `Popup_Notices` | 329 | 65 | 15 | 5 |
| `Popup_Notices` | 328 | 70 | 14 | 5 |
| `Popup_BuyMoreGems` | 326 | 60 | 14 | 5 |
| `Board_Talents` | 325 | 29 | 10 | 4 |
| `Popup_Notices` | 323 | 68 | 15 | 5 |

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
