# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **742**
- tổng node: **105831**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (51)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91917 |
| `SpriteRenderer` | 49754 |
| `MeshRenderer` | 15401 |
| `RectTransform` | 13914 |
| `TextMeshPro` | 13841 |
| `MeshFilter` | 12497 |
| `BoxCollider2D` | 7495 |
| `Animator` | 5419 |
| `ButtonEvents` | 5185 |
| `Button_Sound` | 5031 |
| `ParticleSystem` | 3778 |
| `ParticleSystemRenderer` | 3778 |
| `LanguageTextMeshPro` | 3654 |
| `ChangeSorting` | 2242 |
| `BgObjectScaler` | 1655 |
| `Popup_Notices` | 1269 |
| `Box_Rewards` | 1230 |
| `TMP_SubMesh` | 1011 |
| `UIObjectAnchors` | 761 |
| `Shop_Cell` | 678 |
| `FixUIShop` | 618 |
| `Rigidbody2D` | 380 |
| `ObjectPool` | 366 |
| `Enemy_Datas` | 315 |
| `Enemy_Health` | 315 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 434 | 338 | 61 |
| `Board_Shop` | 3258 | 535 | 155 | 45 |
| `Board_PVP` | 2519 | 402 | 169 | 39 |
| `Board_FightBoss` | 2471 | 121 | 44 | 40 |
| `Board_SelectBoss` | 2231 | 103 | 15 | 30 |
| `Tab_Boss` | 1975 | 5 | 0 | 31 |
| `Board_Arena` | 1834 | 251 | 120 | 30 |
| `Board_Players` | 1784 | 202 | 77 | 29 |
| `Board_BattlePass` | 1711 | 224 | 68 | 18 |
| `Board_Ranks` | 1481 | 202 | 90 | 23 |
| `Board_Ranks` | 1391 | 211 | 89 | 22 |
| `Board_Survival` | 1305 | 200 | 81 | 21 |
| `Board_Survival` | 1266 | 179 | 83 | 21 |
| `Board_TechLab` | 1235 | 169 | 75 | 18 |
| `Board_BattlePassPro` | 1039 | 133 | 42 | 16 |
| `Board_WinnerBenefits` | 1026 | 150 | 57 | 15 |
| `Board_Begin` | 1014 | 132 | 50 | 15 |
| `Popup_WatchVideos` | 977 | 171 | 50 | 14 |
| `Board_Endgame` | 911 | 127 | 54 | 16 |
| `Board_Reborn` | 866 | 152 | 59 | 15 |
| `Board_MiniCombo` | 863 | 90 | 52 | 13 |
| `Board_Setting` | 847 | 107 | 68 | 13 |
| `Board_GiftLogin` | 842 | 127 | 27 | 12 |
| `Board_Challange` | 832 | 156 | 55 | 13 |
| `Board_Combo` | 811 | 90 | 51 | 12 |
| `Board_Drones` | 777 | 117 | 59 | 15 |
| `Popup_WatchVideos` | 771 | 121 | 40 | 11 |
| `Board_Vip` | 770 | 96 | 26 | 11 |
| `Board_Stage` | 710 | 125 | 51 | 12 |
| `Board_QuestRewards` | 668 | 87 | 26 | 10 |
| `Popup_ShipSalePack` | 620 | 19 | 7 | 8 |
| `Board_EventSeasonPass` | 601 | 97 | 29 | 10 |
| `Tab_Boss` | 564 | 7 | 1 | 7 |
| `Board_ShopEnergy` | 526 | 100 | 32 | 9 |
| `Popup_HolidayGift` | 502 | 65 | 10 | 7 |
| `Board_UserProfile` | 494 | 35 | 48 | 7 |
| `Popup_HolidayGift` | 470 | 74 | 11 | 7 |
| `Popup_WeekSales` | 448 | 62 | 12 | 6 |
| `Board_EventSeasonPass` | 440 | 73 | 22 | 7 |
| `Popup_WatchVideosOld` | 376 | 61 | 13 | 5 |

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
