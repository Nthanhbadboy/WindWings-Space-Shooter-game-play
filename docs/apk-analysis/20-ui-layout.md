# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **718**
- tổng node: **104330**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (75)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90728 |
| `SpriteRenderer` | 49070 |
| `MeshRenderer` | 15071 |
| `RectTransform` | 13602 |
| `TextMeshPro` | 13539 |
| `MeshFilter` | 12313 |
| `BoxCollider2D` | 7321 |
| `Animator` | 5272 |
| `ButtonEvents` | 5067 |
| `Button_Sound` | 4923 |
| `ParticleSystem` | 3713 |
| `ParticleSystemRenderer` | 3713 |
| `LanguageTextMeshPro` | 3520 |
| `ChangeSorting` | 2196 |
| `BgObjectScaler` | 1604 |
| `Popup_Notices` | 1235 |
| `Box_Rewards` | 1144 |
| `TMP_SubMesh` | 1037 |
| `UIObjectAnchors` | 743 |
| `Shop_Cell` | 694 |
| `FixUIShop` | 630 |
| `Rigidbody2D` | 386 |
| `ObjectPool` | 365 |
| `Enemy_Datas` | 320 |
| `Enemy_Health` | 320 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 450 | 338 | 62 |
| `Board_Shop` | 3001 | 506 | 147 | 42 |
| `Board_PVP` | 2609 | 363 | 159 | 39 |
| `Board_FightBoss` | 2570 | 128 | 46 | 41 |
| `Board_SelectBoss` | 2276 | 97 | 15 | 31 |
| `Board_Arena` | 1946 | 250 | 121 | 30 |
| `Board_BattlePass` | 1730 | 238 | 68 | 18 |
| `Tab_Boss` | 1667 | 6 | 0 | 26 |
| `Board_Players` | 1646 | 172 | 73 | 28 |
| `Board_Ranks` | 1252 | 178 | 87 | 21 |
| `Board_TechLab` | 1237 | 140 | 64 | 17 |
| `Board_Survival` | 1232 | 164 | 85 | 20 |
| `Board_Ranks` | 1218 | 197 | 87 | 19 |
| `Board_Survival` | 1172 | 179 | 77 | 19 |
| `Board_Drones` | 1068 | 149 | 61 | 18 |
| `Board_Begin` | 1046 | 133 | 52 | 16 |
| `Board_BattlePassPro` | 1035 | 128 | 42 | 16 |
| `Board_WinnerBenefits` | 944 | 157 | 58 | 15 |
| `Board_Reborn` | 847 | 143 | 56 | 15 |
| `Popup_WatchVideos` | 835 | 152 | 48 | 12 |
| `Board_Endgame` | 828 | 130 | 54 | 15 |
| `Board_Setting` | 795 | 94 | 63 | 12 |
| `Board_Challange` | 792 | 135 | 52 | 13 |
| `Popup_WatchVideos` | 788 | 141 | 45 | 12 |
| `Board_GiftLogin` | 777 | 120 | 21 | 12 |
| `Board_Stage` | 770 | 116 | 52 | 12 |
| `Board_Vip` | 713 | 76 | 26 | 11 |
| `Board_MiniCombo` | 697 | 76 | 41 | 11 |
| `Board_UserProfile` | 688 | 63 | 49 | 10 |
| `Board_QuestRewards` | 679 | 93 | 25 | 9 |
| `Board_ShopEnergy` | 586 | 95 | 33 | 9 |
| `Popup_ShipSalePack` | 567 | 14 | 7 | 8 |
| `Tab_Boss` | 559 | 8 | 0 | 7 |
| `Popup_HolidayGift` | 557 | 67 | 11 | 7 |
| `Popup_HolidayGift` | 550 | 75 | 11 | 8 |
| `Board_EventSeasonPass` | 519 | 88 | 25 | 9 |
| `Board_EventSeasonPass` | 501 | 70 | 21 | 7 |
| `Board_Combo` | 470 | 54 | 21 | 7 |
| `Board_Begin` | 397 | 36 | 13 | 5 |
| `Popup_WeekSales` | 375 | 43 | 12 | 6 |

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
