# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **725**
- tổng node: **105205**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (68)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 91496 |
| `SpriteRenderer` | 49575 |
| `MeshRenderer` | 15164 |
| `RectTransform` | 13709 |
| `TextMeshPro` | 13635 |
| `MeshFilter` | 12298 |
| `BoxCollider2D` | 7367 |
| `Animator` | 5417 |
| `ButtonEvents` | 5080 |
| `Button_Sound` | 4927 |
| `ParticleSystem` | 3893 |
| `ParticleSystemRenderer` | 3893 |
| `LanguageTextMeshPro` | 3597 |
| `ChangeSorting` | 2207 |
| `BgObjectScaler` | 1619 |
| `Popup_Notices` | 1245 |
| `Box_Rewards` | 1215 |
| `TMP_SubMesh` | 1023 |
| `UIObjectAnchors` | 751 |
| `Shop_Cell` | 671 |
| `FixUIShop` | 615 |
| `Rigidbody2D` | 417 |
| `ObjectPool` | 385 |
| `Enemy_Datas` | 332 |
| `Enemy_Health` | 332 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 457 | 338 | 62 |
| `Board_Shop` | 3688 | 598 | 165 | 50 |
| `Board_SelectBoss` | 2570 | 112 | 17 | 36 |
| `Board_FightBoss` | 2534 | 118 | 45 | 39 |
| `Board_PVP` | 2458 | 322 | 167 | 38 |
| `Board_Arena` | 2104 | 286 | 125 | 33 |
| `Tab_Boss` | 1879 | 5 | 0 | 29 |
| `Board_Players` | 1734 | 183 | 73 | 28 |
| `Board_BattlePass` | 1628 | 224 | 61 | 17 |
| `Board_Ranks` | 1401 | 209 | 86 | 22 |
| `Board_Ranks` | 1319 | 208 | 88 | 21 |
| `Board_Survival` | 1217 | 216 | 81 | 20 |
| `Board_TechLab` | 1181 | 101 | 66 | 16 |
| `Board_Survival` | 1159 | 200 | 85 | 20 |
| `Board_Drones` | 1059 | 139 | 59 | 18 |
| `Board_WinnerBenefits` | 997 | 144 | 56 | 15 |
| `Popup_WatchVideos` | 911 | 157 | 49 | 13 |
| `Popup_WatchVideos` | 904 | 157 | 46 | 13 |
| `Board_GiftLogin` | 857 | 123 | 28 | 13 |
| `Board_Setting` | 852 | 94 | 63 | 13 |
| `Board_Begin` | 849 | 110 | 51 | 15 |
| `Board_Reborn` | 838 | 149 | 60 | 15 |
| `Board_MiniCombo` | 835 | 92 | 57 | 12 |
| `Board_Endgame` | 817 | 119 | 47 | 14 |
| `Board_Combo` | 791 | 87 | 48 | 12 |
| `Board_Vip` | 766 | 96 | 26 | 11 |
| `Board_Stage` | 739 | 120 | 52 | 12 |
| `Board_Challange` | 736 | 137 | 50 | 12 |
| `Board_BattlePassPro` | 735 | 102 | 26 | 11 |
| `Board_ShopEnergy` | 635 | 102 | 34 | 9 |
| `Board_QuestRewards` | 631 | 94 | 27 | 9 |
| `Tab_Boss` | 581 | 8 | 1 | 7 |
| `Popup_ShipSalePack` | 577 | 17 | 7 | 9 |
| `Popup_HolidayGift` | 543 | 65 | 10 | 7 |
| `Popup_HolidayGift` | 515 | 72 | 11 | 7 |
| `Board_EventSeasonPass` | 510 | 87 | 28 | 9 |
| `Board_EventSeasonPass` | 495 | 68 | 19 | 7 |
| `Board_UserProfile` | 446 | 52 | 46 | 8 |
| `Board_Begin` | 417 | 33 | 15 | 5 |
| `Board_Profile` | 372 | 25 | 16 | 5 |

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
