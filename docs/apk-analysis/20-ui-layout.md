# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **721**
- tổng node: **106092**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (72)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92027 |
| `SpriteRenderer` | 50020 |
| `MeshRenderer` | 15566 |
| `RectTransform` | 14065 |
| `TextMeshPro` | 13991 |
| `MeshFilter` | 12676 |
| `BoxCollider2D` | 7431 |
| `Animator` | 5416 |
| `ButtonEvents` | 5124 |
| `Button_Sound` | 4968 |
| `ParticleSystem` | 3805 |
| `ParticleSystemRenderer` | 3805 |
| `LanguageTextMeshPro` | 3546 |
| `ChangeSorting` | 2231 |
| `BgObjectScaler` | 1630 |
| `Popup_Notices` | 1249 |
| `Box_Rewards` | 1205 |
| `TMP_SubMesh` | 1042 |
| `UIObjectAnchors` | 753 |
| `Shop_Cell` | 699 |
| `FixUIShop` | 627 |
| `Rigidbody2D` | 375 |
| `ObjectPool` | 365 |
| `Enemy_Datas` | 310 |
| `Enemy_Health` | 310 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 447 | 339 | 60 |
| `Board_Shop` | 3359 | 537 | 163 | 45 |
| `Board_PVP` | 2701 | 382 | 172 | 40 |
| `Board_FightBoss` | 2491 | 139 | 46 | 39 |
| `Board_SelectBoss` | 2041 | 106 | 16 | 26 |
| `Board_Arena` | 2000 | 259 | 123 | 31 |
| `Board_Players` | 1784 | 196 | 78 | 29 |
| `Tab_Boss` | 1776 | 6 | 0 | 27 |
| `Board_BattlePass` | 1627 | 247 | 62 | 17 |
| `Board_Survival` | 1379 | 202 | 82 | 22 |
| `Board_Survival` | 1366 | 197 | 87 | 21 |
| `Board_Ranks` | 1361 | 151 | 80 | 21 |
| `Board_TechLab` | 1350 | 159 | 65 | 19 |
| `Board_Ranks` | 1243 | 192 | 85 | 20 |
| `Board_Begin` | 1050 | 135 | 49 | 16 |
| `Popup_WatchVideos` | 968 | 167 | 49 | 13 |
| `Board_BattlePassPro` | 953 | 125 | 41 | 14 |
| `Board_WinnerBenefits` | 911 | 126 | 53 | 14 |
| `Board_Setting` | 910 | 107 | 64 | 13 |
| `Board_Endgame` | 897 | 133 | 52 | 16 |
| `Board_Drones` | 884 | 126 | 57 | 15 |
| `Board_GiftLogin` | 874 | 130 | 28 | 13 |
| `Board_Reborn` | 825 | 152 | 60 | 15 |
| `Board_Challange` | 812 | 156 | 54 | 13 |
| `Board_Combo` | 786 | 87 | 42 | 12 |
| `Board_Vip` | 766 | 90 | 25 | 11 |
| `Board_Stage` | 749 | 121 | 51 | 12 |
| `Popup_WatchVideos` | 720 | 144 | 47 | 11 |
| `Popup_ShipSalePack` | 720 | 19 | 7 | 10 |
| `Board_QuestRewards` | 671 | 97 | 27 | 10 |
| `Board_MiniCombo` | 660 | 80 | 34 | 11 |
| `Board_UserProfile` | 600 | 61 | 49 | 9 |
| `Tab_Boss` | 552 | 8 | 1 | 7 |
| `Board_ShopEnergy` | 539 | 84 | 31 | 8 |
| `Popup_HolidayGift` | 537 | 70 | 11 | 7 |
| `Board_EventSeasonPass` | 529 | 91 | 28 | 9 |
| `Popup_HolidayGift` | 491 | 66 | 11 | 7 |
| `Board_EventSeasonPass` | 483 | 74 | 22 | 7 |
| `Popup_WeekSales` | 470 | 64 | 14 | 6 |
| `Popup_WatchVideosOld` | 371 | 62 | 12 | 5 |

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
