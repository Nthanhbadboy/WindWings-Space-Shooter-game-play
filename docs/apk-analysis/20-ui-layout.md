# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **723**
- tổng node: **104702**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (70)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90812 |
| `SpriteRenderer` | 49031 |
| `MeshRenderer` | 15363 |
| `RectTransform` | 13890 |
| `TextMeshPro` | 13818 |
| `MeshFilter` | 12589 |
| `BoxCollider2D` | 7420 |
| `Animator` | 5259 |
| `ButtonEvents` | 5156 |
| `Button_Sound` | 5003 |
| `ParticleSystem` | 3859 |
| `ParticleSystemRenderer` | 3859 |
| `LanguageTextMeshPro` | 3590 |
| `ChangeSorting` | 2210 |
| `BgObjectScaler` | 1619 |
| `Popup_Notices` | 1254 |
| `Box_Rewards` | 1167 |
| `TMP_SubMesh` | 1019 |
| `UIObjectAnchors` | 754 |
| `Shop_Cell` | 710 |
| `FixUIShop` | 639 |
| `Rigidbody2D` | 371 |
| `ObjectPool` | 368 |
| `LineRenderer` | 320 |
| `Enemy_Datas` | 320 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 434 | 334 | 60 |
| `Board_Shop` | 3160 | 518 | 155 | 44 |
| `Board_PVP` | 2605 | 401 | 172 | 40 |
| `Board_SelectBoss` | 2382 | 100 | 17 | 33 |
| `Board_FightBoss` | 2374 | 117 | 45 | 37 |
| `Tab_Boss` | 1990 | 5 | 0 | 31 |
| `Board_Arena` | 1820 | 234 | 122 | 30 |
| `Board_BattlePass` | 1680 | 238 | 63 | 18 |
| `Board_Players` | 1674 | 197 | 78 | 28 |
| `Board_Ranks` | 1443 | 198 | 92 | 23 |
| `Board_TechLab` | 1429 | 154 | 72 | 20 |
| `Board_Ranks` | 1420 | 221 | 85 | 23 |
| `Board_Survival` | 1160 | 146 | 69 | 18 |
| `Board_BattlePassPro` | 1067 | 129 | 44 | 16 |
| `Board_Survival` | 1057 | 173 | 84 | 18 |
| `Board_Drones` | 1010 | 137 | 61 | 16 |
| `Board_Begin` | 950 | 125 | 53 | 16 |
| `Popup_WatchVideos` | 910 | 170 | 49 | 13 |
| `Board_WinnerBenefits` | 908 | 152 | 56 | 14 |
| `Board_Combo` | 905 | 95 | 54 | 13 |
| `Board_GiftLogin` | 889 | 126 | 27 | 13 |
| `Board_Reborn` | 871 | 133 | 59 | 15 |
| `Popup_WatchVideos` | 859 | 156 | 47 | 12 |
| `Board_Endgame` | 771 | 112 | 45 | 14 |
| `Board_Challange` | 734 | 120 | 48 | 12 |
| `Board_Vip` | 730 | 84 | 25 | 11 |
| `Board_Stage` | 729 | 116 | 51 | 11 |
| `Board_Setting` | 714 | 101 | 63 | 11 |
| `Board_QuestRewards` | 698 | 98 | 27 | 10 |
| `Board_UserProfile` | 682 | 63 | 48 | 10 |
| `Board_MiniCombo` | 642 | 78 | 39 | 10 |
| `Popup_ShipSalePack` | 589 | 16 | 7 | 8 |
| `Board_ShopEnergy` | 565 | 107 | 34 | 9 |
| `Tab_Boss` | 559 | 6 | 1 | 7 |
| `Popup_HolidayGift` | 515 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 508 | 83 | 24 | 9 |
| `Board_EventSeasonPass` | 483 | 73 | 22 | 7 |
| `Popup_HolidayGift` | 466 | 73 | 9 | 7 |
| `Popup_WeekSales` | 411 | 49 | 14 | 6 |
| `Board_Begin` | 390 | 37 | 15 | 5 |

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
