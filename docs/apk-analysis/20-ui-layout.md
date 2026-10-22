# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **588**
- tổng node: **71795**
- dung lượng thô (gz): **1.1 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 61878 |
| `MonoBehaviour` | 32286 |
| `SpriteRenderer` | 32224 |
| `MeshRenderer` | 10953 |
| `RectTransform` | 9917 |
| `MeshFilter` | 9285 |
| `BoxCollider2D` | 5593 |
| `Animator` | 3633 |
| `ParticleSystem` | 2398 |
| `ParticleSystemRenderer` | 2398 |
| `LineRenderer` | 215 |
| `Rigidbody2D` | 212 |
| `CircleCollider2D` | 168 |
| `SpriteMask` | 156 |
| `PolygonCollider2D` | 55 |
| `TrailRenderer` | 40 |
| `CanvasRenderer` | 2 |
| `Canvas` | 1 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 2000 | 0 | 0 | 20 |
| `Board_FightBoss` | 2000 | 0 | 0 | 22 |
| `Board_Shop` | 2000 | 0 | 0 | 21 |
| `Board_PVP` | 2000 | 0 | 0 | 23 |
| `Tab_Boss` | 1867 | 0 | 0 | 19 |
| `Board_Arena` | 1829 | 0 | 0 | 21 |
| `Board_Ranks` | 1363 | 0 | 0 | 15 |
| `Board_Ranks` | 1311 | 0 | 0 | 14 |
| `Board_Survival` | 1183 | 0 | 0 | 14 |
| `Board_TechLab` | 1162 | 0 | 0 | 13 |
| `Board_Survival` | 1085 | 0 | 0 | 13 |
| `Board_Begin` | 987 | 0 | 0 | 12 |
| `Board_WinnerBenefits` | 876 | 0 | 0 | 9 |
| `Popup_WatchVideos` | 863 | 0 | 0 | 9 |
| `Board_Challange` | 862 | 0 | 0 | 10 |
| `Board_GiftLogin` | 821 | 0 | 0 | 8 |
| `Popup_WatchVideos` | 796 | 0 | 0 | 8 |
| `Board_Vip` | 744 | 0 | 0 | 8 |
| `Board_Endgame` | 741 | 0 | 0 | 9 |
| `Board_Stage` | 708 | 0 | 0 | 8 |
| `Board_QuestRewards` | 659 | 0 | 0 | 7 |
| `Popup_ShipSalePack` | 600 | 0 | 0 | 6 |
| `Popup_HolidayGift` | 526 | 0 | 0 | 5 |
| `Tab_Boss` | 500 | 0 | 0 | 5 |
| `Board_EventSeasonPass` | 439 | 0 | 0 | 5 |
| `Board_Begin` | 399 | 0 | 0 | 4 |
| `Board_Profile` | 375 | 0 | 0 | 4 |
| `Board_Quest` | 365 | 0 | 0 | 4 |
| `Board_Reborn_IAP` | 345 | 0 | 0 | 4 |
| `Popup_Notices` | 344 | 0 | 0 | 4 |
| `Popup_PvPRankings` | 343 | 0 | 0 | 5 |
| `Board_Talents` | 334 | 0 | 0 | 3 |
| `Popup_BuyMoreGems` | 330 | 0 | 0 | 4 |
| `Popup_Notices` | 329 | 0 | 0 | 3 |
| `Popup_Notices` | 319 | 0 | 0 | 4 |
| `Popup_PremiumDailyRewards` | 318 | 0 | 0 | 3 |
| `Popup_BuyMoreGems` | 316 | 0 | 0 | 4 |
| `Popup_BuyMoreGems` | 313 | 0 | 0 | 4 |
| `Popup_BuyMoreGems` | 310 | 0 | 0 | 3 |
| `Board_Reborn_IAP` | 310 | 0 | 0 | 4 |

## Cấu trúc mỗi node

```json
{"path": "Background/Star_01", "depth": 2, "active": 1,
 "anchor_min": [0,0], "anchor_max": [1,1], "anchored_pos": [0,0],
 "size_delta": [0,0], "pivot": [0.5,0.5], "scale": [1,1,1],
 "components": [{"class":"Image","sprite":"Star"},
                 {"class":"LanguageTextMeshPro","key":"txt_play","text":"Play"}]}
```

- Toạ độ là **local space của RectTransform cha**, đơn vị Unity
  (canvas tham chiếu thường 1080×1920 → 1 unit = 100 px).
- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.
- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.
