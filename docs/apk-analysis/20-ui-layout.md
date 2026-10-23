# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **724**
- tổng node: **102474**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (69)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 88912 |
| `SpriteRenderer` | 48278 |
| `MeshRenderer` | 15035 |
| `RectTransform` | 13562 |
| `TextMeshPro` | 13487 |
| `MeshFilter` | 12364 |
| `BoxCollider2D` | 7287 |
| `Animator` | 5266 |
| `ButtonEvents` | 4989 |
| `Button_Sound` | 4838 |
| `ParticleSystem` | 3661 |
| `ParticleSystemRenderer` | 3661 |
| `LanguageTextMeshPro` | 3540 |
| `ChangeSorting` | 2173 |
| `BgObjectScaler` | 1608 |
| `Popup_Notices` | 1242 |
| `Box_Rewards` | 1215 |
| `TMP_SubMesh` | 1044 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 679 |
| `FixUIShop` | 611 |
| `Rigidbody2D` | 387 |
| `ObjectPool` | 361 |
| `Enemy_Datas` | 311 |
| `Enemy_Health` | 311 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4183 | 335 | 207 | 50 |
| `Board_Shop` | 3297 | 522 | 150 | 44 |
| `Board_PVP` | 2917 | 414 | 172 | 44 |
| `Board_FightBoss` | 2348 | 113 | 46 | 36 |
| `Board_SelectBoss` | 2114 | 108 | 14 | 28 |
| `Tab_Boss` | 1884 | 5 | 0 | 30 |
| `Board_Arena` | 1835 | 246 | 117 | 30 |
| `Board_Players` | 1695 | 187 | 74 | 29 |
| `Board_BattlePass` | 1646 | 233 | 59 | 17 |
| `Board_TechLab` | 1452 | 176 | 77 | 20 |
| `Board_Ranks` | 1390 | 196 | 87 | 21 |
| `Board_Survival` | 1333 | 189 | 83 | 20 |
| `Board_Survival` | 1246 | 160 | 67 | 20 |
| `Board_Ranks` | 1229 | 158 | 86 | 19 |
| `Board_WinnerBenefits` | 1044 | 152 | 55 | 15 |
| `Board_Drones` | 983 | 125 | 59 | 15 |
| `Board_Endgame` | 904 | 130 | 53 | 16 |
| `Board_BattlePassPro` | 902 | 117 | 41 | 13 |
| `Popup_WatchVideos` | 889 | 153 | 49 | 13 |
| `Popup_WatchVideos` | 864 | 150 | 48 | 13 |
| `Board_GiftLogin` | 860 | 124 | 26 | 13 |
| `Board_Setting` | 858 | 98 | 66 | 13 |
| `Board_Challange` | 785 | 124 | 50 | 12 |
| `Board_MiniCombo` | 779 | 90 | 47 | 12 |
| `Board_Reborn` | 768 | 114 | 60 | 14 |
| `Board_Stage` | 763 | 120 | 44 | 12 |
| `Board_Combo` | 740 | 82 | 41 | 12 |
| `Board_Begin` | 712 | 108 | 49 | 12 |
| `Board_Vip` | 700 | 96 | 26 | 11 |
| `Popup_ShipSalePack` | 675 | 16 | 7 | 10 |
| `Board_QuestRewards` | 638 | 96 | 27 | 9 |
| `Tab_Boss` | 561 | 7 | 1 | 7 |
| `Board_UserProfile` | 560 | 41 | 46 | 8 |
| `Popup_HolidayGift` | 555 | 78 | 10 | 8 |
| `Popup_HolidayGift` | 553 | 63 | 11 | 7 |
| `Board_EventSeasonPass` | 545 | 89 | 28 | 9 |
| `Board_EventSeasonPass` | 487 | 71 | 21 | 7 |
| `Board_ShopEnergy` | 487 | 91 | 30 | 8 |
| `Popup_WeekSales` | 448 | 58 | 14 | 6 |
| `Board_Profile` | 350 | 29 | 16 | 5 |

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
