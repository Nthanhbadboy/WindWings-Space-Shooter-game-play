# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **731**
- tổng node: **106448**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (62)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92422 |
| `SpriteRenderer` | 49949 |
| `MeshRenderer` | 15592 |
| `RectTransform` | 14026 |
| `TextMeshPro` | 13957 |
| `MeshFilter` | 12769 |
| `BoxCollider2D` | 7454 |
| `Animator` | 5401 |
| `ButtonEvents` | 5122 |
| `Button_Sound` | 4967 |
| `ParticleSystem` | 3792 |
| `ParticleSystemRenderer` | 3792 |
| `LanguageTextMeshPro` | 3611 |
| `ChangeSorting` | 2227 |
| `BgObjectScaler` | 1653 |
| `Popup_Notices` | 1262 |
| `Box_Rewards` | 1174 |
| `TMP_SubMesh` | 1098 |
| `UIObjectAnchors` | 747 |
| `Shop_Cell` | 693 |
| `FixUIShop` | 645 |
| `Rigidbody2D` | 431 |
| `ObjectPool` | 405 |
| `Enemy_Datas` | 352 |
| `Enemy_Health` | 352 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 454 | 341 | 61 |
| `Board_Shop` | 3598 | 621 | 177 | 49 |
| `Board_SelectBoss` | 2692 | 109 | 17 | 38 |
| `Board_PVP` | 2552 | 326 | 148 | 38 |
| `Board_FightBoss` | 2411 | 107 | 45 | 38 |
| `Board_Arena` | 1946 | 287 | 123 | 31 |
| `Tab_Boss` | 1837 | 6 | 0 | 28 |
| `Board_Players` | 1743 | 201 | 73 | 29 |
| `Board_BattlePass` | 1738 | 245 | 67 | 18 |
| `Board_Ranks` | 1533 | 216 | 91 | 24 |
| `Board_Ranks` | 1368 | 199 | 88 | 22 |
| `Board_TechLab` | 1319 | 153 | 73 | 19 |
| `Board_Survival` | 1225 | 146 | 74 | 19 |
| `Board_Survival` | 1165 | 191 | 81 | 20 |
| `Board_BattlePassPro` | 1020 | 125 | 42 | 16 |
| `Board_Drones` | 999 | 126 | 58 | 18 |
| `Board_Begin` | 891 | 119 | 45 | 13 |
| `Board_WinnerBenefits` | 882 | 140 | 56 | 14 |
| `Board_Setting` | 874 | 100 | 63 | 13 |
| `Board_Reborn` | 871 | 145 | 59 | 15 |
| `Board_GiftLogin` | 847 | 127 | 27 | 12 |
| `Popup_WatchVideos` | 832 | 142 | 45 | 12 |
| `Board_Challange` | 827 | 146 | 52 | 13 |
| `Board_Endgame` | 791 | 115 | 50 | 14 |
| `Board_Stage` | 775 | 132 | 49 | 13 |
| `Popup_WatchVideos` | 726 | 138 | 45 | 11 |
| `Board_QuestRewards` | 686 | 91 | 26 | 10 |
| `Popup_ShipSalePack` | 670 | 17 | 7 | 10 |
| `Board_Vip` | 584 | 41 | 17 | 8 |
| `Board_EventSeasonPass` | 580 | 93 | 26 | 10 |
| `Board_ShopEnergy` | 556 | 91 | 32 | 9 |
| `Tab_Boss` | 534 | 7 | 1 | 7 |
| `Popup_HolidayGift` | 532 | 78 | 10 | 8 |
| `Popup_HolidayGift` | 528 | 67 | 11 | 7 |
| `Board_MiniCombo` | 481 | 57 | 20 | 8 |
| `Board_EventSeasonPass` | 426 | 65 | 16 | 6 |
| `Board_Combo` | 387 | 47 | 16 | 6 |
| `Board_Quest` | 384 | 112 | 39 | 5 |
| `Board_Reborn_IAP` | 381 | 70 | 15 | 6 |
| `Popup_WatchVideosOld` | 381 | 58 | 13 | 5 |

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
