# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **729**
- tổng node: **103417**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (64)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89687 |
| `SpriteRenderer` | 48545 |
| `MeshRenderer` | 15249 |
| `RectTransform` | 13730 |
| `TextMeshPro` | 13672 |
| `MeshFilter` | 12598 |
| `BoxCollider2D` | 7270 |
| `Animator` | 5235 |
| `ButtonEvents` | 5010 |
| `Button_Sound` | 4861 |
| `ParticleSystem` | 3674 |
| `ParticleSystemRenderer` | 3674 |
| `LanguageTextMeshPro` | 3596 |
| `ChangeSorting` | 2226 |
| `BgObjectScaler` | 1632 |
| `Popup_Notices` | 1258 |
| `Box_Rewards` | 1179 |
| `TMP_SubMesh` | 1069 |
| `UIObjectAnchors` | 744 |
| `Shop_Cell` | 692 |
| `FixUIShop` | 621 |
| `Rigidbody2D` | 383 |
| `ObjectPool` | 370 |
| `Enemy_Datas` | 317 |
| `Enemy_Health` | 317 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4185 | 341 | 201 | 52 |
| `Board_Shop` | 3007 | 506 | 153 | 42 |
| `Board_PVP` | 2872 | 418 | 169 | 43 |
| `Board_FightBoss` | 2424 | 118 | 46 | 38 |
| `Board_SelectBoss` | 2049 | 90 | 17 | 29 |
| `Tab_Boss` | 1869 | 6 | 0 | 29 |
| `Board_Arena` | 1815 | 245 | 117 | 29 |
| `Board_BattlePass` | 1784 | 242 | 64 | 18 |
| `Board_Players` | 1654 | 193 | 75 | 27 |
| `Board_Ranks` | 1459 | 208 | 93 | 23 |
| `Board_Survival` | 1417 | 196 | 81 | 23 |
| `Board_Ranks` | 1397 | 230 | 91 | 22 |
| `Board_Survival` | 1224 | 175 | 84 | 20 |
| `Board_TechLab` | 1205 | 136 | 65 | 18 |
| `Board_Drones` | 1004 | 128 | 60 | 17 |
| `Board_Begin` | 965 | 119 | 52 | 16 |
| `Popup_WatchVideos` | 916 | 166 | 47 | 13 |
| `Board_Combo` | 915 | 97 | 54 | 13 |
| `Board_BattlePassPro` | 914 | 113 | 31 | 13 |
| `Popup_WatchVideos` | 896 | 164 | 47 | 13 |
| `Board_Endgame` | 890 | 128 | 52 | 16 |
| `Board_Reborn` | 886 | 156 | 60 | 15 |
| `Board_Setting` | 838 | 99 | 64 | 13 |
| `Board_GiftLogin` | 825 | 120 | 21 | 12 |
| `Board_Challange` | 812 | 138 | 52 | 13 |
| `Board_WinnerBenefits` | 795 | 101 | 45 | 11 |
| `Board_Stage` | 749 | 118 | 51 | 12 |
| `Board_UserProfile` | 665 | 61 | 48 | 10 |
| `Popup_ShipSalePack` | 637 | 17 | 7 | 9 |
| `Board_Vip` | 634 | 91 | 27 | 10 |
| `Board_QuestRewards` | 632 | 72 | 26 | 9 |
| `Board_MiniCombo` | 613 | 73 | 35 | 10 |
| `Board_ShopEnergy` | 602 | 111 | 34 | 9 |
| `Tab_Boss` | 565 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 538 | 70 | 11 | 8 |
| `Board_EventSeasonPass` | 524 | 88 | 26 | 9 |
| `Popup_HolidayGift` | 502 | 65 | 11 | 7 |
| `Board_EventSeasonPass` | 458 | 69 | 22 | 7 |
| `Popup_PvPRankings` | 389 | 51 | 19 | 7 |
| `Board_Profile` | 376 | 25 | 16 | 5 |

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
