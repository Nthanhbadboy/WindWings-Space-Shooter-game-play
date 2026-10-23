# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **720**
- tổng node: **102245**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (73)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88542 |
| `SpriteRenderer` | 48261 |
| `MeshRenderer` | 15135 |
| `RectTransform` | 13703 |
| `TextMeshPro` | 13637 |
| `MeshFilter` | 12422 |
| `BoxCollider2D` | 7306 |
| `Animator` | 5187 |
| `ButtonEvents` | 5067 |
| `Button_Sound` | 4917 |
| `LanguageTextMeshPro` | 3502 |
| `ParticleSystem` | 3394 |
| `ParticleSystemRenderer` | 3394 |
| `ChangeSorting` | 2173 |
| `BgObjectScaler` | 1614 |
| `Popup_Notices` | 1240 |
| `Box_Rewards` | 1135 |
| `TMP_SubMesh` | 1020 |
| `UIObjectAnchors` | 714 |
| `Shop_Cell` | 665 |
| `FixUIShop` | 621 |
| `LineRenderer` | 286 |
| `Rigidbody2D` | 283 |
| `ObjectPool` | 236 |
| `AutoSetVipIcon` | 223 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 439 | 334 | 61 |
| `Board_Shop` | 3712 | 631 | 173 | 50 |
| `Board_PVP` | 2821 | 385 | 172 | 42 |
| `Board_FightBoss` | 2403 | 108 | 43 | 38 |
| `Tab_Boss` | 1936 | 6 | 0 | 29 |
| `Board_Players` | 1892 | 198 | 77 | 30 |
| `Board_Ranks` | 1571 | 227 | 90 | 24 |
| `Board_Arena` | 1542 | 194 | 100 | 27 |
| `Board_TechLab` | 1447 | 178 | 76 | 20 |
| `Board_Survival` | 1380 | 224 | 86 | 23 |
| `Board_Ranks` | 1353 | 172 | 81 | 21 |
| `Board_Survival` | 1115 | 183 | 84 | 19 |
| `Board_Drones` | 1032 | 140 | 60 | 18 |
| `Board_WinnerBenefits` | 1011 | 146 | 56 | 15 |
| `Board_Begin` | 953 | 129 | 50 | 15 |
| `Board_BattlePassPro` | 904 | 118 | 43 | 13 |
| `Board_Reborn` | 902 | 146 | 54 | 15 |
| `Popup_WatchVideos` | 898 | 149 | 48 | 13 |
| `Board_Endgame` | 860 | 126 | 48 | 15 |
| `Board_Setting` | 858 | 106 | 66 | 13 |
| `Popup_WatchVideos` | 841 | 154 | 49 | 12 |
| `Board_Vip` | 810 | 89 | 27 | 12 |
| `Board_Combo` | 802 | 86 | 41 | 12 |
| `Board_GiftLogin` | 781 | 130 | 28 | 12 |
| `Board_MiniCombo` | 746 | 89 | 43 | 12 |
| `Board_Challange` | 741 | 136 | 48 | 12 |
| `Popup_ShipSalePack` | 695 | 18 | 7 | 10 |
| `Board_Stage` | 661 | 129 | 53 | 11 |
| `Board_BattlePass` | 656 | 91 | 18 | 9 |
| `Board_QuestRewards` | 646 | 86 | 23 | 9 |
| `Board_ShopEnergy` | 640 | 104 | 35 | 9 |
| `Popup_HolidayGift` | 515 | 73 | 9 | 7 |
| `Popup_HolidayGift` | 508 | 63 | 11 | 7 |
| `Board_EventSeasonPass` | 506 | 74 | 26 | 8 |
| `Board_EventSeasonPass` | 484 | 68 | 22 | 7 |
| `Popup_WeekSales` | 452 | 63 | 14 | 6 |
| `Board_Begin` | 421 | 36 | 15 | 5 |
| `Popup_PvPRankings` | 402 | 40 | 17 | 7 |
| `Popup_WatchVideosOld` | 376 | 61 | 13 | 5 |
| `Board_Quest` | 376 | 107 | 39 | 5 |

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
