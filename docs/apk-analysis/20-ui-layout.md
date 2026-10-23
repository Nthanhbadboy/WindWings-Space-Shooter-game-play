# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **731**
- tổng node: **106407**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (62)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92179 |
| `SpriteRenderer` | 49755 |
| `MeshRenderer` | 15794 |
| `RectTransform` | 14228 |
| `TextMeshPro` | 14150 |
| `MeshFilter` | 12868 |
| `BoxCollider2D` | 7523 |
| `Animator` | 5482 |
| `ButtonEvents` | 5181 |
| `Button_Sound` | 5050 |
| `ParticleSystem` | 3839 |
| `ParticleSystemRenderer` | 3839 |
| `LanguageTextMeshPro` | 3641 |
| `ChangeSorting` | 2245 |
| `BgObjectScaler` | 1641 |
| `Popup_Notices` | 1267 |
| `Box_Rewards` | 1237 |
| `TMP_SubMesh` | 1113 |
| `UIObjectAnchors` | 743 |
| `Shop_Cell` | 684 |
| `FixUIShop` | 632 |
| `Rigidbody2D` | 395 |
| `ObjectPool` | 359 |
| `Enemy_Datas` | 311 |
| `Enemy_Health` | 311 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 455 | 330 | 61 |
| `Board_Shop` | 3793 | 672 | 173 | 51 |
| `Board_PVP` | 2656 | 355 | 151 | 42 |
| `Board_FightBoss` | 2463 | 118 | 40 | 39 |
| `Board_SelectBoss` | 2330 | 105 | 16 | 31 |
| `Board_Arena` | 2059 | 272 | 124 | 32 |
| `Tab_Boss` | 1869 | 5 | 0 | 29 |
| `Board_BattlePass` | 1845 | 274 | 64 | 19 |
| `Board_Players` | 1696 | 200 | 73 | 28 |
| `Board_Ranks` | 1513 | 218 | 84 | 23 |
| `Board_TechLab` | 1341 | 155 | 66 | 19 |
| `Board_Ranks` | 1333 | 219 | 89 | 22 |
| `Board_Survival` | 1196 | 191 | 84 | 20 |
| `Board_Begin` | 1105 | 155 | 53 | 17 |
| `Board_Survival` | 1084 | 171 | 78 | 18 |
| `Board_BattlePassPro` | 989 | 125 | 42 | 15 |
| `Popup_WatchVideos` | 917 | 153 | 49 | 13 |
| `Board_MiniCombo` | 892 | 89 | 50 | 13 |
| `Board_Endgame` | 890 | 130 | 53 | 16 |
| `Board_Drones` | 880 | 87 | 51 | 15 |
| `Board_WinnerBenefits` | 871 | 132 | 55 | 13 |
| `Board_GiftLogin` | 870 | 134 | 29 | 13 |
| `Board_Combo` | 848 | 100 | 55 | 12 |
| `Board_Reborn` | 824 | 136 | 55 | 14 |
| `Popup_WatchVideos` | 806 | 148 | 45 | 12 |
| `Board_Stage` | 796 | 128 | 54 | 13 |
| `Board_Setting` | 769 | 100 | 62 | 12 |
| `Board_UserProfile` | 696 | 57 | 50 | 10 |
| `Board_Vip` | 691 | 76 | 26 | 10 |
| `Popup_ShipSalePack` | 675 | 17 | 7 | 9 |
| `Board_Challange` | 656 | 127 | 48 | 11 |
| `Board_ShopEnergy` | 601 | 101 | 33 | 9 |
| `Board_QuestRewards` | 579 | 81 | 26 | 9 |
| `Tab_Boss` | 552 | 8 | 1 | 7 |
| `Board_EventSeasonPass` | 545 | 83 | 25 | 9 |
| `Popup_HolidayGift` | 543 | 63 | 11 | 7 |
| `Popup_HolidayGift` | 540 | 78 | 10 | 8 |
| `Board_EventSeasonPass` | 512 | 70 | 22 | 7 |
| `Popup_WeekSales` | 450 | 57 | 13 | 6 |
| `Popup_WatchVideosOld` | 362 | 54 | 13 | 5 |

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
