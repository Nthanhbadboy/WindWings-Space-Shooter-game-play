# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **732**
- tổng node: **104528**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (61)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90699 |
| `SpriteRenderer` | 49175 |
| `MeshRenderer` | 15308 |
| `RectTransform` | 13829 |
| `TextMeshPro` | 13761 |
| `MeshFilter` | 12502 |
| `BoxCollider2D` | 7382 |
| `Animator` | 5308 |
| `ButtonEvents` | 5091 |
| `Button_Sound` | 4943 |
| `ParticleSystem` | 3661 |
| `ParticleSystemRenderer` | 3661 |
| `LanguageTextMeshPro` | 3593 |
| `ChangeSorting` | 2220 |
| `BgObjectScaler` | 1624 |
| `Popup_Notices` | 1251 |
| `Box_Rewards` | 1173 |
| `TMP_SubMesh` | 1036 |
| `UIObjectAnchors` | 745 |
| `Shop_Cell` | 671 |
| `FixUIShop` | 616 |
| `Rigidbody2D` | 384 |
| `ObjectPool` | 350 |
| `LineRenderer` | 326 |
| `Enemy_Datas` | 297 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 433 | 329 | 60 |
| `Board_Shop` | 3082 | 483 | 147 | 44 |
| `Board_FightBoss` | 2171 | 64 | 36 | 36 |
| `Board_PVP` | 2158 | 313 | 152 | 34 |
| `Board_SelectBoss` | 2023 | 108 | 15 | 29 |
| `Board_Arena` | 1843 | 246 | 120 | 30 |
| `Board_Players` | 1709 | 167 | 77 | 29 |
| `Tab_Boss` | 1685 | 6 | 0 | 27 |
| `Board_Ranks` | 1459 | 226 | 93 | 23 |
| `Board_Survival` | 1383 | 207 | 82 | 23 |
| `Board_TechLab` | 1372 | 150 | 77 | 20 |
| `Board_Ranks` | 1331 | 224 | 91 | 22 |
| `Board_Combo` | 1111 | 111 | 62 | 15 |
| `Board_Survival` | 1047 | 173 | 81 | 17 |
| `Board_Begin` | 1036 | 135 | 52 | 16 |
| `Board_Drones` | 1006 | 130 | 59 | 17 |
| `Board_BattlePassPro` | 994 | 122 | 43 | 15 |
| `Board_WinnerBenefits` | 930 | 154 | 54 | 14 |
| `Popup_WatchVideos` | 930 | 170 | 50 | 13 |
| `Board_Endgame` | 913 | 140 | 54 | 16 |
| `Board_GiftLogin` | 841 | 116 | 29 | 12 |
| `Board_Reborn` | 839 | 137 | 57 | 15 |
| `Board_Stage` | 832 | 130 | 51 | 13 |
| `Popup_WatchVideos` | 820 | 149 | 45 | 12 |
| `Board_Vip` | 782 | 97 | 26 | 11 |
| `Board_Setting` | 767 | 89 | 61 | 12 |
| `Board_Challange` | 758 | 146 | 54 | 13 |
| `Board_MiniCombo` | 718 | 89 | 38 | 11 |
| `Board_QuestRewards` | 690 | 92 | 27 | 10 |
| `Board_BattlePass` | 690 | 94 | 18 | 9 |
| `Popup_ShipSalePack` | 654 | 18 | 7 | 10 |
| `Board_UserProfile` | 611 | 60 | 48 | 9 |
| `Board_ShopEnergy` | 607 | 107 | 33 | 9 |
| `Tab_Boss` | 596 | 8 | 1 | 8 |
| `Popup_HolidayGift` | 560 | 76 | 11 | 8 |
| `Board_EventSeasonPass` | 536 | 88 | 29 | 9 |
| `Popup_HolidayGift` | 534 | 65 | 9 | 7 |
| `Board_EventSeasonPass` | 488 | 72 | 22 | 7 |
| `Popup_PvPRankings` | 422 | 55 | 16 | 7 |
| `Popup_WeekSales` | 419 | 59 | 13 | 6 |

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
