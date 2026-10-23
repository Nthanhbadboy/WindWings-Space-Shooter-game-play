# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **730**
- tổng node: **105642**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (63)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91813 |
| `SpriteRenderer` | 49781 |
| `MeshRenderer` | 15328 |
| `RectTransform` | 13829 |
| `TextMeshPro` | 13757 |
| `MeshFilter` | 12481 |
| `BoxCollider2D` | 7393 |
| `Animator` | 5369 |
| `ButtonEvents` | 5136 |
| `Button_Sound` | 4982 |
| `ParticleSystem` | 3747 |
| `ParticleSystemRenderer` | 3747 |
| `LanguageTextMeshPro` | 3667 |
| `ChangeSorting` | 2223 |
| `BgObjectScaler` | 1623 |
| `Popup_Notices` | 1250 |
| `Box_Rewards` | 1195 |
| `TMP_SubMesh` | 1047 |
| `UIObjectAnchors` | 756 |
| `Shop_Cell` | 672 |
| `FixUIShop` | 607 |
| `Rigidbody2D` | 360 |
| `ObjectPool` | 347 |
| `LineRenderer` | 300 |
| `Enemy_Datas` | 294 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 442 | 336 | 61 |
| `Board_Shop` | 3051 | 466 | 143 | 42 |
| `Board_PVP` | 2673 | 382 | 163 | 40 |
| `Board_FightBoss` | 2556 | 119 | 43 | 41 |
| `Board_SelectBoss` | 2272 | 113 | 16 | 31 |
| `Board_BattlePass` | 1895 | 253 | 68 | 19 |
| `Board_Players` | 1775 | 198 | 77 | 29 |
| `Board_Arena` | 1686 | 218 | 119 | 28 |
| `Tab_Boss` | 1634 | 5 | 0 | 26 |
| `Board_Ranks` | 1387 | 204 | 84 | 22 |
| `Board_Survival` | 1357 | 188 | 80 | 22 |
| `Board_Ranks` | 1344 | 221 | 89 | 22 |
| `Board_TechLab` | 1294 | 163 | 61 | 19 |
| `Board_Survival` | 1283 | 188 | 83 | 21 |
| `Board_BattlePassPro` | 976 | 127 | 44 | 15 |
| `Board_Begin` | 954 | 142 | 50 | 16 |
| `Popup_WatchVideos` | 910 | 152 | 48 | 13 |
| `Board_WinnerBenefits` | 890 | 125 | 56 | 14 |
| `Board_Drones` | 881 | 126 | 59 | 15 |
| `Board_Endgame` | 861 | 132 | 52 | 16 |
| `Popup_WatchVideos` | 857 | 145 | 48 | 13 |
| `Board_Setting` | 829 | 103 | 65 | 13 |
| `Board_MiniCombo` | 828 | 93 | 50 | 12 |
| `Board_Challange` | 825 | 145 | 49 | 13 |
| `Board_Reborn` | 817 | 131 | 61 | 15 |
| `Board_GiftLogin` | 807 | 131 | 27 | 12 |
| `Board_Stage` | 795 | 135 | 52 | 12 |
| `Board_Combo` | 735 | 82 | 42 | 11 |
| `Board_Vip` | 700 | 86 | 24 | 10 |
| `Board_UserProfile` | 657 | 59 | 49 | 10 |
| `Popup_ShipSalePack` | 623 | 13 | 7 | 9 |
| `Board_QuestRewards` | 622 | 75 | 25 | 9 |
| `Board_ShopEnergy` | 587 | 102 | 34 | 9 |
| `Board_EventSeasonPass` | 563 | 88 | 26 | 9 |
| `Tab_Boss` | 561 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 558 | 73 | 11 | 8 |
| `Popup_HolidayGift` | 469 | 66 | 11 | 7 |
| `Popup_WeekSales` | 466 | 60 | 14 | 6 |
| `Board_EventSeasonPass` | 450 | 72 | 22 | 7 |
| `Popup_PvPRankings` | 391 | 47 | 17 | 7 |

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
