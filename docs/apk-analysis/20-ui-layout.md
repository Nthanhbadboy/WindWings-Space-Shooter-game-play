# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **735**
- tổng node: **106351**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (58)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92371 |
| `SpriteRenderer` | 50116 |
| `MeshRenderer` | 15484 |
| `RectTransform` | 13980 |
| `TextMeshPro` | 13915 |
| `MeshFilter` | 12565 |
| `BoxCollider2D` | 7467 |
| `Animator` | 5502 |
| `ButtonEvents` | 5172 |
| `Button_Sound` | 5030 |
| `ParticleSystem` | 3841 |
| `ParticleSystemRenderer` | 3841 |
| `LanguageTextMeshPro` | 3606 |
| `ChangeSorting` | 2237 |
| `BgObjectScaler` | 1637 |
| `Popup_Notices` | 1262 |
| `Box_Rewards` | 1228 |
| `TMP_SubMesh` | 1037 |
| `UIObjectAnchors` | 755 |
| `Shop_Cell` | 678 |
| `FixUIShop` | 629 |
| `Rigidbody2D` | 381 |
| `ObjectPool` | 358 |
| `Enemy_Datas` | 307 |
| `Enemy_Health` | 307 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 466 | 338 | 62 |
| `Board_Shop` | 3612 | 584 | 166 | 50 |
| `Board_PVP` | 2682 | 352 | 160 | 40 |
| `Board_FightBoss` | 2597 | 130 | 45 | 40 |
| `Board_SelectBoss` | 2036 | 98 | 17 | 27 |
| `Board_Arena` | 1909 | 264 | 113 | 30 |
| `Board_BattlePass` | 1746 | 238 | 65 | 18 |
| `Board_Players` | 1692 | 187 | 77 | 28 |
| `Tab_Boss` | 1670 | 6 | 0 | 25 |
| `Board_Ranks` | 1534 | 235 | 92 | 24 |
| `Board_Ranks` | 1493 | 204 | 85 | 23 |
| `Board_TechLab` | 1381 | 170 | 78 | 19 |
| `Board_Survival` | 1300 | 198 | 81 | 21 |
| `Board_Survival` | 1157 | 184 | 83 | 20 |
| `Board_BattlePassPro` | 991 | 126 | 43 | 15 |
| `Board_Begin` | 980 | 124 | 49 | 16 |
| `Board_Drones` | 961 | 127 | 60 | 16 |
| `Board_MiniCombo` | 939 | 101 | 60 | 14 |
| `Board_WinnerBenefits` | 923 | 136 | 53 | 14 |
| `Board_Reborn` | 885 | 151 | 59 | 15 |
| `Popup_WatchVideos` | 866 | 149 | 50 | 13 |
| `Board_Endgame` | 832 | 125 | 52 | 15 |
| `Board_Combo` | 819 | 88 | 47 | 12 |
| `Board_GiftLogin` | 817 | 132 | 28 | 12 |
| `Board_Stage` | 798 | 128 | 52 | 12 |
| `Board_Challange` | 772 | 141 | 51 | 13 |
| `Popup_WatchVideos` | 756 | 152 | 46 | 12 |
| `Board_Vip` | 755 | 89 | 23 | 11 |
| `Board_Setting` | 722 | 81 | 43 | 11 |
| `Popup_ShipSalePack` | 684 | 17 | 7 | 9 |
| `Board_UserProfile` | 582 | 29 | 50 | 8 |
| `Board_ShopEnergy` | 578 | 91 | 33 | 9 |
| `Popup_HolidayGift` | 565 | 76 | 11 | 8 |
| `Tab_Boss` | 538 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 532 | 82 | 27 | 9 |
| `Board_QuestRewards` | 491 | 46 | 17 | 7 |
| `Board_EventSeasonPass` | 488 | 70 | 21 | 7 |
| `Popup_HolidayGift` | 471 | 64 | 11 | 7 |
| `Popup_WeekSales` | 441 | 50 | 12 | 6 |
| `Popup_PvPRankings` | 408 | 52 | 19 | 7 |

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
