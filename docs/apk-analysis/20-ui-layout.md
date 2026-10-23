# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **743**
- tổng node: **107429**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (50)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 93132 |
| `SpriteRenderer` | 50635 |
| `MeshRenderer` | 15840 |
| `RectTransform` | 14297 |
| `TextMeshPro` | 14220 |
| `MeshFilter` | 12899 |
| `BoxCollider2D` | 7561 |
| `Animator` | 5499 |
| `ButtonEvents` | 5220 |
| `Button_Sound` | 5075 |
| `ParticleSystem` | 3773 |
| `ParticleSystemRenderer` | 3773 |
| `LanguageTextMeshPro` | 3627 |
| `ChangeSorting` | 2254 |
| `BgObjectScaler` | 1657 |
| `Popup_Notices` | 1272 |
| `Box_Rewards` | 1221 |
| `TMP_SubMesh` | 1093 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 701 |
| `FixUIShop` | 636 |
| `Rigidbody2D` | 376 |
| `ObjectPool` | 354 |
| `LineRenderer` | 320 |
| `Enemy_Datas` | 299 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 444 | 337 | 62 |
| `Board_Shop` | 3279 | 530 | 149 | 45 |
| `Board_PVP` | 2921 | 395 | 167 | 44 |
| `Board_FightBoss` | 2498 | 121 | 45 | 40 |
| `Board_Arena` | 2073 | 282 | 124 | 33 |
| `Board_BattlePass` | 1820 | 253 | 67 | 19 |
| `Board_SelectBoss` | 1785 | 108 | 15 | 24 |
| `Board_Players` | 1705 | 148 | 64 | 27 |
| `Tab_Boss` | 1701 | 1 | 0 | 27 |
| `Board_Ranks` | 1408 | 217 | 85 | 22 |
| `Board_TechLab` | 1404 | 147 | 70 | 19 |
| `Board_Survival` | 1381 | 203 | 84 | 22 |
| `Board_Ranks` | 1318 | 219 | 86 | 21 |
| `Board_Survival` | 1269 | 202 | 81 | 21 |
| `Board_Drones` | 1014 | 131 | 59 | 17 |
| `Board_WinnerBenefits` | 1012 | 151 | 53 | 15 |
| `Board_Begin` | 997 | 134 | 52 | 16 |
| `Board_BattlePassPro` | 960 | 131 | 43 | 15 |
| `Popup_WatchVideos` | 920 | 163 | 48 | 13 |
| `Board_Setting` | 899 | 100 | 65 | 13 |
| `Popup_WatchVideos` | 895 | 156 | 49 | 13 |
| `Board_Reborn` | 887 | 159 | 61 | 16 |
| `Board_Challange` | 829 | 143 | 51 | 13 |
| `Board_GiftLogin` | 816 | 125 | 27 | 12 |
| `Board_Endgame` | 812 | 125 | 52 | 15 |
| `Board_MiniCombo` | 778 | 82 | 44 | 11 |
| `Board_Combo` | 758 | 83 | 46 | 11 |
| `Popup_ShipSalePack` | 729 | 18 | 7 | 10 |
| `Board_QuestRewards` | 707 | 93 | 27 | 10 |
| `Board_Stage` | 703 | 112 | 52 | 11 |
| `Board_Vip` | 661 | 81 | 25 | 10 |
| `Board_UserProfile` | 631 | 40 | 50 | 9 |
| `Tab_Boss` | 562 | 9 | 1 | 7 |
| `Board_ShopEnergy` | 544 | 93 | 32 | 9 |
| `Popup_HolidayGift` | 515 | 73 | 10 | 7 |
| `Board_EventSeasonPass` | 506 | 95 | 27 | 9 |
| `Popup_HolidayGift` | 481 | 67 | 11 | 7 |
| `Popup_PvPRankings` | 401 | 54 | 18 | 7 |
| `Board_EventSeasonPass` | 393 | 69 | 21 | 6 |
| `Board_Reborn_IAP` | 387 | 73 | 15 | 6 |

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
