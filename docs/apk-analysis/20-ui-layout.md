# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **748**
- tổng node: **104592**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (45)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 90554 |
| `SpriteRenderer` | 49443 |
| `MeshRenderer` | 15567 |
| `RectTransform` | 14038 |
| `TextMeshPro` | 13968 |
| `MeshFilter` | 12808 |
| `BoxCollider2D` | 7526 |
| `Animator` | 5399 |
| `ButtonEvents` | 5227 |
| `Button_Sound` | 5083 |
| `LanguageTextMeshPro` | 3665 |
| `ParticleSystem` | 3529 |
| `ParticleSystemRenderer` | 3529 |
| `ChangeSorting` | 2222 |
| `BgObjectScaler` | 1659 |
| `Popup_Notices` | 1281 |
| `Box_Rewards` | 1176 |
| `TMP_SubMesh` | 1093 |
| `UIObjectAnchors` | 701 |
| `Shop_Cell` | 690 |
| `FixUIShop` | 632 |
| `Rigidbody2D` | 301 |
| `LineRenderer` | 276 |
| `ObjectPool` | 250 |
| `AutoSetVipIcon` | 230 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 440 | 338 | 61 |
| `Board_Shop` | 3676 | 595 | 176 | 49 |
| `Board_PVP` | 3051 | 445 | 169 | 45 |
| `Board_FightBoss` | 2317 | 117 | 45 | 37 |
| `Tab_Boss` | 1907 | 5 | 0 | 29 |
| `Board_BattlePass` | 1860 | 248 | 69 | 19 |
| `Board_Players` | 1801 | 187 | 79 | 29 |
| `Board_Arena` | 1801 | 207 | 110 | 30 |
| `Board_Ranks` | 1378 | 192 | 89 | 22 |
| `Board_Ranks` | 1371 | 200 | 85 | 22 |
| `Board_Survival` | 1340 | 182 | 77 | 22 |
| `Board_Drones` | 1115 | 133 | 60 | 19 |
| `Board_TechLab` | 1102 | 136 | 66 | 17 |
| `Board_Survival` | 1006 | 170 | 79 | 18 |
| `Board_Begin` | 940 | 133 | 49 | 16 |
| `Board_BattlePassPro` | 921 | 119 | 43 | 14 |
| `Board_Endgame` | 911 | 136 | 53 | 16 |
| `Popup_WatchVideos` | 892 | 155 | 45 | 13 |
| `Board_MiniCombo` | 891 | 103 | 53 | 14 |
| `Board_WinnerBenefits` | 871 | 125 | 54 | 14 |
| `Popup_WatchVideos` | 865 | 137 | 46 | 12 |
| `Board_GiftLogin` | 836 | 125 | 29 | 12 |
| `Board_Reborn` | 825 | 153 | 61 | 15 |
| `Board_Stage` | 817 | 143 | 54 | 13 |
| `Board_Combo` | 803 | 80 | 45 | 11 |
| `Board_Setting` | 800 | 102 | 65 | 12 |
| `Board_Challange` | 765 | 129 | 50 | 12 |
| `Board_QuestRewards` | 699 | 102 | 27 | 10 |
| `Board_Vip` | 659 | 95 | 26 | 10 |
| `Board_ShopEnergy` | 630 | 115 | 33 | 9 |
| `Popup_ShipSalePack` | 622 | 16 | 7 | 9 |
| `Board_EventSeasonPass` | 592 | 93 | 29 | 10 |
| `Board_UserProfile` | 568 | 34 | 49 | 8 |
| `Tab_Boss` | 548 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 531 | 65 | 11 | 7 |
| `Popup_HolidayGift` | 518 | 76 | 11 | 7 |
| `Board_EventSeasonPass` | 476 | 69 | 22 | 7 |
| `Board_Quest` | 369 | 106 | 39 | 5 |
| `Board_AccountSettings` | 360 | 30 | 16 | 5 |
| `Popup_PvPRankings` | 355 | 45 | 15 | 6 |

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
