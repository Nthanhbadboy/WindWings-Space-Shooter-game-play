# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **743**
- tổng node: **108033**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (50)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 93903 |
| `SpriteRenderer` | 50979 |
| `MeshRenderer` | 15633 |
| `RectTransform` | 14130 |
| `TextMeshPro` | 14060 |
| `MeshFilter` | 12677 |
| `BoxCollider2D` | 7536 |
| `Animator` | 5617 |
| `ButtonEvents` | 5183 |
| `Button_Sound` | 5051 |
| `ParticleSystem` | 3981 |
| `ParticleSystemRenderer` | 3981 |
| `LanguageTextMeshPro` | 3620 |
| `ChangeSorting` | 2240 |
| `BgObjectScaler` | 1653 |
| `Popup_Notices` | 1273 |
| `Box_Rewards` | 1263 |
| `TMP_SubMesh` | 1034 |
| `UIObjectAnchors` | 762 |
| `Shop_Cell` | 700 |
| `FixUIShop` | 626 |
| `Rigidbody2D` | 415 |
| `ObjectPool` | 376 |
| `LineRenderer` | 338 |
| `Enemy_Datas` | 327 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 433 | 345 | 60 |
| `Board_Shop` | 3622 | 586 | 162 | 49 |
| `Board_PVP` | 2804 | 398 | 168 | 42 |
| `Board_FightBoss` | 2555 | 129 | 47 | 40 |
| `Board_SelectBoss` | 2496 | 115 | 15 | 33 |
| `Board_Arena` | 1942 | 246 | 121 | 32 |
| `Tab_Boss` | 1930 | 5 | 0 | 29 |
| `Board_Players` | 1726 | 175 | 76 | 29 |
| `Board_BattlePass` | 1707 | 234 | 61 | 18 |
| `Board_Ranks` | 1361 | 212 | 88 | 22 |
| `Board_Survival` | 1342 | 194 | 81 | 22 |
| `Board_Ranks` | 1283 | 171 | 83 | 20 |
| `Board_TechLab` | 1269 | 149 | 72 | 18 |
| `Board_Survival` | 1226 | 171 | 81 | 20 |
| `Board_Begin` | 1062 | 140 | 49 | 16 |
| `Board_Combo` | 1008 | 100 | 60 | 15 |
| `Popup_WatchVideos` | 984 | 179 | 49 | 14 |
| `Board_Drones` | 963 | 148 | 60 | 17 |
| `Popup_WatchVideos` | 943 | 163 | 49 | 13 |
| `Board_Endgame` | 931 | 128 | 54 | 16 |
| `Board_BattlePassPro` | 920 | 111 | 31 | 14 |
| `Board_WinnerBenefits` | 901 | 139 | 53 | 14 |
| `Board_MiniCombo` | 833 | 88 | 49 | 12 |
| `Board_GiftLogin` | 814 | 124 | 27 | 12 |
| `Board_Reborn` | 802 | 144 | 57 | 14 |
| `Board_Setting` | 766 | 97 | 63 | 12 |
| `Board_Stage` | 761 | 120 | 47 | 12 |
| `Board_Challange` | 752 | 130 | 46 | 12 |
| `Board_Vip` | 736 | 89 | 26 | 11 |
| `Board_QuestRewards` | 711 | 103 | 27 | 10 |
| `Popup_ShipSalePack` | 650 | 14 | 7 | 9 |
| `Board_ShopEnergy` | 618 | 109 | 35 | 9 |
| `Board_UserProfile` | 585 | 60 | 50 | 9 |
| `Tab_Boss` | 566 | 9 | 1 | 7 |
| `Popup_HolidayGift` | 559 | 78 | 11 | 8 |
| `Board_EventSeasonPass` | 557 | 92 | 28 | 10 |
| `Popup_HolidayGift` | 531 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 512 | 73 | 21 | 7 |
| `Popup_WeekSales` | 458 | 61 | 14 | 6 |
| `Board_Begin` | 393 | 36 | 11 | 5 |

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
