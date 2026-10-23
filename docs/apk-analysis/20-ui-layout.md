# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **726**
- tổng node: **102875**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (67)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89228 |
| `SpriteRenderer` | 48185 |
| `MeshRenderer` | 15104 |
| `RectTransform` | 13647 |
| `TextMeshPro` | 13578 |
| `MeshFilter` | 12391 |
| `BoxCollider2D` | 7406 |
| `Animator` | 5230 |
| `ButtonEvents` | 5079 |
| `Button_Sound` | 4936 |
| `ParticleSystem` | 3792 |
| `ParticleSystemRenderer` | 3792 |
| `LanguageTextMeshPro` | 3523 |
| `ChangeSorting` | 2207 |
| `BgObjectScaler` | 1627 |
| `Popup_Notices` | 1251 |
| `Box_Rewards` | 1200 |
| `TMP_SubMesh` | 1010 |
| `UIObjectAnchors` | 743 |
| `Shop_Cell` | 682 |
| `FixUIShop` | 618 |
| `ObjectPool` | 383 |
| `Rigidbody2D` | 371 |
| `Enemy_Datas` | 335 |
| `Enemy_Health` | 335 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 450 | 335 | 63 |
| `Board_Shop` | 3165 | 508 | 156 | 44 |
| `Board_SelectBoss` | 2462 | 90 | 16 | 36 |
| `Board_PVP` | 2394 | 338 | 165 | 35 |
| `Board_FightBoss` | 2353 | 117 | 45 | 38 |
| `Board_Arena` | 1939 | 245 | 124 | 31 |
| `Tab_Boss` | 1886 | 6 | 0 | 29 |
| `Board_Players` | 1723 | 167 | 69 | 29 |
| `Board_BattlePass` | 1690 | 241 | 63 | 18 |
| `Board_Survival` | 1425 | 206 | 81 | 23 |
| `Board_Ranks` | 1339 | 194 | 85 | 20 |
| `Board_Ranks` | 1282 | 178 | 84 | 20 |
| `Board_TechLab` | 1233 | 141 | 65 | 18 |
| `Board_Survival` | 1102 | 172 | 72 | 17 |
| `Board_Begin` | 999 | 140 | 53 | 16 |
| `Board_Drones` | 968 | 117 | 58 | 17 |
| `Board_WinnerBenefits` | 930 | 124 | 51 | 14 |
| `Popup_WatchVideos` | 906 | 161 | 49 | 13 |
| `Board_BattlePassPro` | 906 | 111 | 36 | 13 |
| `Board_Setting` | 899 | 100 | 61 | 13 |
| `Board_MiniCombo` | 887 | 88 | 53 | 13 |
| `Board_Reborn` | 867 | 142 | 61 | 15 |
| `Board_GiftLogin` | 841 | 123 | 26 | 12 |
| `Board_Endgame` | 835 | 126 | 54 | 15 |
| `Popup_WatchVideos` | 828 | 155 | 46 | 12 |
| `Board_Vip` | 774 | 103 | 27 | 11 |
| `Board_Challange` | 769 | 134 | 52 | 13 |
| `Board_Stage` | 763 | 134 | 50 | 12 |
| `Board_QuestRewards` | 702 | 102 | 27 | 10 |
| `Board_EventSeasonPass` | 557 | 93 | 28 | 10 |
| `Popup_HolidayGift` | 548 | 75 | 11 | 8 |
| `Tab_Boss` | 545 | 6 | 1 | 7 |
| `Board_ShopEnergy` | 528 | 90 | 31 | 9 |
| `Popup_HolidayGift` | 521 | 68 | 11 | 7 |
| `Board_UserProfile` | 521 | 38 | 50 | 8 |
| `Board_EventSeasonPass` | 513 | 74 | 22 | 8 |
| `Popup_ShipSalePack` | 494 | 19 | 7 | 8 |
| `Popup_PvPRankings` | 417 | 40 | 19 | 7 |
| `Board_Begin` | 414 | 37 | 14 | 5 |
| `Popup_WeekSales` | 408 | 56 | 13 | 6 |

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
