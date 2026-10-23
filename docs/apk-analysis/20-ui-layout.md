# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **742**
- tổng node: **105350**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (51)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91501 |
| `SpriteRenderer` | 49748 |
| `MeshRenderer` | 15320 |
| `RectTransform` | 13849 |
| `TextMeshPro` | 13773 |
| `MeshFilter` | 12577 |
| `BoxCollider2D` | 7442 |
| `Animator` | 5420 |
| `ButtonEvents` | 5125 |
| `Button_Sound` | 4984 |
| `LanguageTextMeshPro` | 3603 |
| `ParticleSystem` | 3541 |
| `ParticleSystemRenderer` | 3541 |
| `ChangeSorting` | 2249 |
| `BgObjectScaler` | 1659 |
| `Popup_Notices` | 1277 |
| `Box_Rewards` | 1182 |
| `TMP_SubMesh` | 1046 |
| `UIObjectAnchors` | 749 |
| `Shop_Cell` | 669 |
| `FixUIShop` | 636 |
| `Rigidbody2D` | 362 |
| `ObjectPool` | 328 |
| `LineRenderer` | 291 |
| `Enemy_Datas` | 276 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 433 | 333 | 59 |
| `Board_Shop` | 3206 | 515 | 165 | 44 |
| `Board_PVP` | 2429 | 294 | 144 | 36 |
| `Board_FightBoss` | 2300 | 117 | 43 | 37 |
| `Board_SelectBoss` | 2213 | 101 | 16 | 31 |
| `Tab_Boss` | 1905 | 5 | 0 | 29 |
| `Board_Arena` | 1786 | 209 | 103 | 30 |
| `Board_Players` | 1740 | 208 | 78 | 29 |
| `Board_BattlePass` | 1599 | 214 | 62 | 17 |
| `Board_Ranks` | 1361 | 187 | 88 | 21 |
| `Board_Survival` | 1297 | 178 | 83 | 21 |
| `Board_Ranks` | 1291 | 205 | 89 | 21 |
| `Board_Survival` | 1256 | 170 | 82 | 20 |
| `Board_TechLab` | 1064 | 117 | 60 | 16 |
| `Board_Begin` | 1013 | 137 | 51 | 16 |
| `Board_Drones` | 964 | 106 | 54 | 16 |
| `Board_WinnerBenefits` | 924 | 154 | 53 | 14 |
| `Board_Setting` | 917 | 101 | 67 | 13 |
| `Board_Endgame` | 883 | 132 | 51 | 16 |
| `Popup_WatchVideos` | 880 | 165 | 45 | 13 |
| `Board_BattlePassPro` | 840 | 101 | 27 | 11 |
| `Board_Combo` | 829 | 90 | 43 | 13 |
| `Board_Reborn` | 809 | 134 | 58 | 14 |
| `Board_GiftLogin` | 792 | 135 | 29 | 12 |
| `Board_Vip` | 778 | 101 | 27 | 11 |
| `Board_Challange` | 775 | 130 | 50 | 12 |
| `Popup_WatchVideos` | 746 | 119 | 40 | 11 |
| `Popup_ShipSalePack` | 701 | 18 | 7 | 10 |
| `Board_QuestRewards` | 684 | 87 | 25 | 10 |
| `Board_Stage` | 676 | 127 | 50 | 11 |
| `Board_UserProfile` | 661 | 61 | 50 | 10 |
| `Board_MiniCombo` | 657 | 78 | 39 | 10 |
| `Board_ShopEnergy` | 635 | 100 | 35 | 9 |
| `Board_EventSeasonPass` | 538 | 90 | 28 | 9 |
| `Popup_HolidayGift` | 510 | 63 | 10 | 7 |
| `Board_EventSeasonPass` | 497 | 69 | 22 | 7 |
| `Popup_HolidayGift` | 482 | 79 | 11 | 7 |
| `Popup_PvPRankings` | 439 | 56 | 18 | 7 |
| `Board_Begin` | 383 | 35 | 13 | 5 |
| `Board_Profile` | 382 | 28 | 15 | 5 |

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
