# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **733**
- tổng node: **106428**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (60)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 92201 |
| `SpriteRenderer` | 50090 |
| `MeshRenderer` | 15752 |
| `RectTransform` | 14227 |
| `TextMeshPro` | 14153 |
| `MeshFilter` | 12796 |
| `BoxCollider2D` | 7513 |
| `Animator` | 5441 |
| `ButtonEvents` | 5209 |
| `Button_Sound` | 5056 |
| `ParticleSystem` | 3795 |
| `ParticleSystemRenderer` | 3795 |
| `LanguageTextMeshPro` | 3667 |
| `ChangeSorting` | 2232 |
| `BgObjectScaler` | 1647 |
| `Popup_Notices` | 1261 |
| `Box_Rewards` | 1226 |
| `TMP_SubMesh` | 1058 |
| `UIObjectAnchors` | 748 |
| `Shop_Cell` | 720 |
| `FixUIShop` | 651 |
| `Rigidbody2D` | 358 |
| `ObjectPool` | 345 |
| `LineRenderer` | 308 |
| `Enemy_Datas` | 293 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 444 | 332 | 62 |
| `Board_Shop` | 3569 | 596 | 170 | 48 |
| `Board_PVP` | 2730 | 423 | 170 | 42 |
| `Board_FightBoss` | 2548 | 117 | 46 | 40 |
| `Board_SelectBoss` | 2445 | 96 | 15 | 34 |
| `Tab_Boss` | 1877 | 6 | 0 | 30 |
| `Board_Arena` | 1875 | 274 | 123 | 31 |
| `Board_Players` | 1785 | 175 | 75 | 29 |
| `Board_BattlePass` | 1713 | 241 | 63 | 18 |
| `Board_TechLab` | 1374 | 157 | 74 | 19 |
| `Board_Survival` | 1342 | 187 | 80 | 22 |
| `Board_Ranks` | 1331 | 178 | 88 | 22 |
| `Board_Ranks` | 1307 | 201 | 91 | 21 |
| `Board_Survival` | 1263 | 184 | 84 | 20 |
| `Board_WinnerBenefits` | 969 | 134 | 54 | 14 |
| `Board_Begin` | 944 | 141 | 54 | 16 |
| `Board_MiniCombo` | 923 | 96 | 57 | 14 |
| `Board_Setting` | 920 | 105 | 66 | 13 |
| `Board_GiftLogin` | 893 | 127 | 29 | 13 |
| `Board_Combo` | 875 | 98 | 54 | 13 |
| `Popup_WatchVideos` | 837 | 158 | 47 | 13 |
| `Board_Reborn` | 834 | 129 | 58 | 15 |
| `Popup_WatchVideos` | 808 | 163 | 46 | 12 |
| `Board_Drones` | 797 | 121 | 52 | 14 |
| `Board_Endgame` | 783 | 108 | 42 | 14 |
| `Board_BattlePassPro` | 774 | 99 | 27 | 11 |
| `Board_Vip` | 771 | 92 | 27 | 11 |
| `Board_Challange` | 770 | 137 | 54 | 13 |
| `Board_Stage` | 689 | 113 | 52 | 11 |
| `Popup_ShipSalePack` | 661 | 17 | 7 | 9 |
| `Board_QuestRewards` | 611 | 92 | 26 | 9 |
| `Board_UserProfile` | 589 | 65 | 48 | 9 |
| `Popup_HolidayGift` | 557 | 77 | 11 | 8 |
| `Popup_HolidayGift` | 531 | 64 | 11 | 7 |
| `Board_EventSeasonPass` | 526 | 91 | 29 | 9 |
| `Board_ShopEnergy` | 502 | 106 | 33 | 8 |
| `Board_EventSeasonPass` | 496 | 72 | 22 | 7 |
| `Board_Quest` | 384 | 111 | 39 | 5 |
| `Popup_WatchVideosOld` | 371 | 59 | 13 | 5 |
| `Popup_WeekSales` | 370 | 50 | 13 | 6 |

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
