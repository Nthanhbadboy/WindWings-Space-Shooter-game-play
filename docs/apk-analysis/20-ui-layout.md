# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **733**
- tổng node: **103227**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (60)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89315 |
| `SpriteRenderer` | 48473 |
| `MeshRenderer` | 15386 |
| `RectTransform` | 13912 |
| `TextMeshPro` | 13837 |
| `MeshFilter` | 12618 |
| `BoxCollider2D` | 7459 |
| `Animator` | 5307 |
| `ButtonEvents` | 5152 |
| `Button_Sound` | 5012 |
| `ParticleSystem` | 3597 |
| `ParticleSystemRenderer` | 3597 |
| `LanguageTextMeshPro` | 3558 |
| `ChangeSorting` | 2214 |
| `BgObjectScaler` | 1654 |
| `Popup_Notices` | 1269 |
| `Box_Rewards` | 1167 |
| `TMP_SubMesh` | 1047 |
| `UIObjectAnchors` | 717 |
| `Shop_Cell` | 712 |
| `FixUIShop` | 656 |
| `Rigidbody2D` | 327 |
| `LineRenderer` | 302 |
| `ObjectPool` | 277 |
| `Obj_Collider` | 237 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 434 | 341 | 61 |
| `Board_Shop` | 3375 | 603 | 170 | 47 |
| `Board_PVP` | 2773 | 368 | 161 | 42 |
| `Board_FightBoss` | 2431 | 102 | 46 | 38 |
| `Tab_Boss` | 1966 | 6 | 0 | 30 |
| `Board_BattlePass` | 1897 | 263 | 70 | 19 |
| `Board_Arena` | 1889 | 280 | 116 | 31 |
| `Board_Players` | 1660 | 159 | 67 | 27 |
| `Board_Survival` | 1419 | 201 | 83 | 22 |
| `Board_Ranks` | 1416 | 197 | 92 | 22 |
| `Board_Ranks` | 1358 | 193 | 91 | 21 |
| `Board_Survival` | 1126 | 183 | 83 | 18 |
| `Board_TechLab` | 1088 | 107 | 46 | 16 |
| `Board_Begin` | 1063 | 138 | 51 | 16 |
| `Board_Combo` | 984 | 101 | 58 | 14 |
| `Board_WinnerBenefits` | 937 | 139 | 54 | 14 |
| `Board_BattlePassPro` | 933 | 109 | 31 | 14 |
| `Board_GiftLogin` | 882 | 128 | 28 | 13 |
| `Board_Reborn` | 869 | 140 | 59 | 15 |
| `Board_Endgame` | 861 | 119 | 50 | 15 |
| `Board_Stage` | 857 | 143 | 52 | 13 |
| `Board_Drones` | 834 | 131 | 57 | 15 |
| `Popup_WatchVideos` | 823 | 157 | 48 | 12 |
| `Popup_WatchVideos` | 751 | 109 | 40 | 11 |
| `Board_Setting` | 739 | 98 | 66 | 12 |
| `Board_QuestRewards` | 698 | 98 | 26 | 10 |
| `Board_MiniCombo` | 684 | 82 | 38 | 11 |
| `Board_Vip` | 645 | 69 | 23 | 10 |
| `Board_UserProfile` | 586 | 53 | 49 | 9 |
| `Board_Challange` | 584 | 106 | 43 | 10 |
| `Popup_ShipSalePack` | 575 | 17 | 7 | 8 |
| `Popup_HolidayGift` | 558 | 80 | 10 | 8 |
| `Popup_HolidayGift` | 548 | 64 | 10 | 7 |
| `Tab_Boss` | 541 | 7 | 1 | 7 |
| `Board_EventSeasonPass` | 515 | 84 | 28 | 8 |
| `Board_ShopEnergy` | 471 | 84 | 32 | 8 |
| `Board_EventSeasonPass` | 448 | 65 | 21 | 7 |
| `Popup_WeekSales` | 427 | 53 | 14 | 6 |
| `Popup_WatchVideosOld` | 368 | 56 | 13 | 5 |
| `Popup_WatchVideosOld` | 366 | 54 | 13 | 5 |

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
