# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **726**
- tổng node: **103816**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (67)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89975 |
| `SpriteRenderer` | 48816 |
| `MeshRenderer` | 15340 |
| `RectTransform` | 13841 |
| `TextMeshPro` | 13770 |
| `MeshFilter` | 12610 |
| `BoxCollider2D` | 7387 |
| `Animator` | 5227 |
| `ButtonEvents` | 5099 |
| `Button_Sound` | 4964 |
| `ParticleSystem` | 3656 |
| `ParticleSystemRenderer` | 3656 |
| `LanguageTextMeshPro` | 3550 |
| `ChangeSorting` | 2204 |
| `BgObjectScaler` | 1640 |
| `Popup_Notices` | 1255 |
| `Box_Rewards` | 1151 |
| `TMP_SubMesh` | 1044 |
| `UIObjectAnchors` | 740 |
| `Shop_Cell` | 690 |
| `FixUIShop` | 628 |
| `Rigidbody2D` | 362 |
| `ObjectPool` | 331 |
| `LineRenderer` | 310 |
| `Enemy_Datas` | 278 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 430 | 338 | 61 |
| `Board_Shop` | 3163 | 513 | 151 | 44 |
| `Board_FightBoss` | 2631 | 126 | 44 | 42 |
| `Board_PVP` | 2580 | 371 | 171 | 39 |
| `Board_SelectBoss` | 1883 | 90 | 14 | 26 |
| `Board_Players` | 1836 | 203 | 79 | 30 |
| `Tab_Boss` | 1693 | 6 | 0 | 27 |
| `Board_BattlePass` | 1676 | 227 | 61 | 18 |
| `Board_Arena` | 1667 | 253 | 118 | 28 |
| `Board_Survival` | 1415 | 195 | 77 | 22 |
| `Board_Ranks` | 1367 | 222 | 87 | 22 |
| `Board_TechLab` | 1319 | 153 | 72 | 19 |
| `Board_Survival` | 1186 | 186 | 81 | 19 |
| `Board_Ranks` | 1066 | 185 | 84 | 19 |
| `Board_Begin` | 1021 | 138 | 50 | 16 |
| `Board_Drones` | 1020 | 138 | 59 | 17 |
| `Board_WinnerBenefits` | 982 | 162 | 56 | 15 |
| `Board_BattlePassPro` | 916 | 118 | 35 | 14 |
| `Popup_WatchVideos` | 902 | 161 | 47 | 13 |
| `Board_Endgame` | 902 | 123 | 53 | 16 |
| `Board_GiftLogin` | 842 | 131 | 28 | 13 |
| `Popup_WatchVideos` | 778 | 148 | 48 | 12 |
| `Board_MiniCombo` | 772 | 96 | 38 | 11 |
| `Board_Reborn` | 769 | 149 | 57 | 14 |
| `Board_Setting` | 758 | 94 | 62 | 12 |
| `Board_Vip` | 725 | 92 | 24 | 11 |
| `Board_Stage` | 687 | 118 | 49 | 11 |
| `Board_ShopEnergy` | 635 | 108 | 33 | 9 |
| `Board_Challange` | 621 | 133 | 51 | 11 |
| `Board_EventSeasonPass` | 576 | 91 | 28 | 9 |
| `Popup_ShipSalePack` | 572 | 14 | 7 | 8 |
| `Tab_Boss` | 572 | 8 | 1 | 7 |
| `Popup_HolidayGift` | 551 | 79 | 11 | 8 |
| `Board_QuestRewards` | 548 | 68 | 27 | 8 |
| `Popup_HolidayGift` | 520 | 65 | 11 | 7 |
| `Board_EventSeasonPass` | 501 | 70 | 22 | 7 |
| `Board_Combo` | 495 | 55 | 22 | 8 |
| `Board_UserProfile` | 396 | 32 | 46 | 7 |
| `Popup_WatchVideosOld` | 377 | 58 | 13 | 5 |
| `Board_Begin` | 368 | 30 | 15 | 5 |

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
