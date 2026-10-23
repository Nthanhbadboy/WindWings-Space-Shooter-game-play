# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **630**
- tổng node: **84194**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 73503 |
| `SpriteRenderer` | 39524 |
| `MeshRenderer` | 11867 |
| `RectTransform` | 10691 |
| `TextMeshPro` | 10633 |
| `MeshFilter` | 9706 |
| `BoxCollider2D` | 5772 |
| `Animator` | 4228 |
| `ButtonEvents` | 3964 |
| `Button_Sound` | 3861 |
| `ParticleSystem` | 2999 |
| `ParticleSystemRenderer` | 2999 |
| `LanguageTextMeshPro` | 2898 |
| `ChangeSorting` | 1756 |
| `BgObjectScaler` | 1288 |
| `Popup_Notices` | 1013 |
| `Box_Rewards` | 881 |
| `TMP_SubMesh` | 817 |
| `UIObjectAnchors` | 622 |
| `Shop_Cell` | 508 |
| `FixUIShop` | 472 |
| `Rigidbody2D` | 348 |
| `ObjectPool` | 344 |
| `Enemy_Datas` | 308 |
| `Enemy_Health` | 308 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4171 | 346 | 195 | 52 |
| `Board_PVP` | 2743 | 385 | 165 | 41 |
| `Board_FightBoss` | 2649 | 126 | 46 | 41 |
| `Board_SelectBoss` | 1975 | 105 | 17 | 26 |
| `Tab_Boss` | 1871 | 6 | 0 | 29 |
| `Board_Players` | 1746 | 193 | 76 | 29 |
| `Board_BattlePass` | 1729 | 235 | 69 | 18 |
| `Board_Ranks` | 1642 | 230 | 88 | 25 |
| `Board_Arena` | 1541 | 195 | 104 | 27 |
| `Board_TechLab` | 1166 | 142 | 64 | 18 |
| `Board_Survival` | 1026 | 184 | 76 | 17 |
| `Board_Begin` | 1009 | 129 | 47 | 15 |
| `Board_BattlePassPro` | 987 | 133 | 43 | 15 |
| `Board_Combo` | 950 | 106 | 50 | 14 |
| `Popup_WatchVideos` | 943 | 159 | 49 | 13 |
| `Board_GiftLogin` | 908 | 132 | 27 | 13 |
| `Board_Endgame` | 816 | 119 | 49 | 15 |
| `Board_Reborn` | 810 | 127 | 58 | 14 |
| `Board_Stage` | 795 | 134 | 53 | 13 |
| `Board_Vip` | 777 | 90 | 27 | 11 |
| `Board_MiniCombo` | 772 | 82 | 44 | 11 |
| `Board_Setting` | 764 | 110 | 65 | 12 |
| `Board_Challange` | 752 | 133 | 53 | 12 |
| `Popup_ShipSalePack` | 678 | 14 | 7 | 10 |
| `Board_QuestRewards` | 630 | 95 | 26 | 9 |
| `Board_ShopEnergy` | 612 | 96 | 32 | 9 |
| `Board_UserProfile` | 564 | 60 | 46 | 8 |
| `Tab_Boss` | 542 | 6 | 1 | 7 |
| `Popup_HolidayGift` | 507 | 62 | 11 | 7 |
| `Popup_PvPRankings` | 402 | 53 | 19 | 7 |
| `Popup_PvPRankings` | 397 | 59 | 19 | 7 |
| `Board_Quest` | 375 | 102 | 39 | 5 |
| `Popup_WatchVideosOld` | 374 | 61 | 13 | 5 |
| `Board_EventSeasonPass` | 370 | 64 | 17 | 6 |
| `Board_Reborn_IAP` | 350 | 68 | 15 | 5 |
| `Board_Talents` | 340 | 28 | 8 | 4 |
| `Board_Reborn_IAP` | 336 | 63 | 15 | 5 |
| `Popup_Notices` | 335 | 63 | 14 | 5 |
| `Popup_BuyMoreGems` | 334 | 61 | 13 | 5 |
| `Popup_BuyMoreGems` | 326 | 57 | 14 | 5 |

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
