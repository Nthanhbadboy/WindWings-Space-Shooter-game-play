# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **753**
- tổng node: **107346**
- dung lượng thô (gz): **2.1 MB**

- bỏ qua: duplicate (class, root) (40)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 93167 |
| `SpriteRenderer` | 50625 |
| `MeshRenderer` | 15679 |
| `RectTransform` | 14179 |
| `TextMeshPro` | 14107 |
| `MeshFilter` | 12810 |
| `BoxCollider2D` | 7585 |
| `Animator` | 5528 |
| `ButtonEvents` | 5239 |
| `Button_Sound` | 5093 |
| `ParticleSystem` | 3788 |
| `ParticleSystemRenderer` | 3788 |
| `LanguageTextMeshPro` | 3683 |
| `ChangeSorting` | 2262 |
| `BgObjectScaler` | 1674 |
| `Popup_Notices` | 1289 |
| `Box_Rewards` | 1212 |
| `TMP_SubMesh` | 1048 |
| `UIObjectAnchors` | 757 |
| `Shop_Cell` | 679 |
| `FixUIShop` | 645 |
| `Rigidbody2D` | 376 |
| `ObjectPool` | 352 |
| `LineRenderer` | 306 |
| `Enemy_Datas` | 299 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 438 | 338 | 61 |
| `Board_Shop` | 3715 | 627 | 184 | 51 |
| `Board_SelectBoss` | 2610 | 104 | 17 | 36 |
| `Board_FightBoss` | 2535 | 125 | 47 | 40 |
| `Board_PVP` | 2407 | 333 | 149 | 38 |
| `Tab_Boss` | 1847 | 6 | 0 | 28 |
| `Board_Players` | 1785 | 199 | 78 | 29 |
| `Board_BattlePass` | 1784 | 255 | 66 | 18 |
| `Board_Arena` | 1764 | 217 | 104 | 29 |
| `Board_Ranks` | 1403 | 207 | 88 | 22 |
| `Board_Survival` | 1348 | 188 | 80 | 22 |
| `Board_Ranks` | 1281 | 199 | 90 | 20 |
| `Board_Survival` | 1239 | 206 | 87 | 21 |
| `Board_TechLab` | 1117 | 139 | 67 | 17 |
| `Board_Drones` | 1080 | 148 | 60 | 18 |
| `Board_Begin` | 1002 | 146 | 54 | 16 |
| `Board_Combo` | 945 | 98 | 57 | 14 |
| `Board_WinnerBenefits` | 918 | 143 | 46 | 13 |
| `Popup_WatchVideos` | 894 | 167 | 50 | 13 |
| `Popup_WatchVideos` | 864 | 155 | 48 | 13 |
| `Board_Endgame` | 836 | 117 | 49 | 15 |
| `Board_Setting` | 835 | 94 | 59 | 12 |
| `Board_Challange` | 834 | 143 | 53 | 13 |
| `Board_Reborn` | 825 | 144 | 58 | 15 |
| `Board_BattlePassPro` | 800 | 102 | 28 | 11 |
| `Board_GiftLogin` | 784 | 122 | 26 | 12 |
| `Board_MiniCombo` | 757 | 99 | 44 | 12 |
| `Board_Vip` | 709 | 88 | 25 | 11 |
| `Board_QuestRewards` | 701 | 98 | 25 | 10 |
| `Board_UserProfile` | 693 | 50 | 50 | 10 |
| `Board_Stage` | 688 | 120 | 52 | 11 |
| `Popup_ShipSalePack` | 673 | 18 | 7 | 9 |
| `Board_ShopEnergy` | 627 | 103 | 34 | 9 |
| `Board_EventSeasonPass` | 527 | 89 | 28 | 9 |
| `Popup_HolidayGift` | 524 | 77 | 11 | 7 |
| `Popup_HolidayGift` | 491 | 67 | 11 | 7 |
| `Board_EventSeasonPass` | 465 | 70 | 21 | 7 |
| `Board_Begin` | 383 | 32 | 14 | 5 |
| `Popup_WeekSales` | 360 | 48 | 12 | 5 |
| `Board_Reborn_IAP` | 357 | 73 | 15 | 5 |

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
