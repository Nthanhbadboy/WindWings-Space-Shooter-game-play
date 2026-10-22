# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **573**
- tổng node: **81706**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 71278 |
| `SpriteRenderer` | 38534 |
| `MeshRenderer` | 11481 |
| `RectTransform` | 10428 |
| `TextMeshPro` | 10377 |
| `MeshFilter` | 9396 |
| `BoxCollider2D` | 5760 |
| `Animator` | 4132 |
| `ButtonEvents` | 3918 |
| `Button_Sound` | 3820 |
| `ParticleSystem` | 3040 |
| `ParticleSystemRenderer` | 3040 |
| `LanguageTextMeshPro` | 2704 |
| `ChangeSorting` | 1731 |
| `BgObjectScaler` | 1291 |
| `Popup_Notices` | 1001 |
| `Box_Rewards` | 899 |
| `TMP_SubMesh` | 703 |
| `Shop_Cell` | 549 |
| `UIObjectAnchors` | 546 |
| `FixUIShop` | 487 |
| `Rigidbody2D` | 366 |
| `ObjectPool` | 311 |
| `Enemy_Datas` | 279 |
| `Enemy_Health` | 279 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 435 | 331 | 61 |
| `Board_Shop` | 3622 | 607 | 176 | 49 |
| `Board_PVP` | 2597 | 362 | 169 | 38 |
| `Board_FightBoss` | 2548 | 128 | 47 | 40 |
| `Board_SelectBoss` | 2163 | 101 | 15 | 31 |
| `Tab_Boss` | 1939 | 5 | 0 | 30 |
| `Board_Players` | 1694 | 188 | 79 | 28 |
| `Board_Arena` | 1694 | 245 | 124 | 29 |
| `Board_Ranks` | 1410 | 201 | 88 | 22 |
| `Board_Survival` | 1346 | 207 | 85 | 22 |
| `Board_Ranks` | 1134 | 204 | 89 | 19 |
| `Board_Drones` | 1093 | 140 | 60 | 18 |
| `Board_Begin` | 950 | 123 | 53 | 15 |
| `Popup_WatchVideos` | 937 | 160 | 49 | 13 |
| `Popup_WatchVideos` | 927 | 162 | 50 | 13 |
| `Board_GiftLogin` | 904 | 129 | 26 | 13 |
| `Board_Setting` | 851 | 100 | 65 | 12 |
| `Board_BattlePassPro` | 832 | 111 | 34 | 12 |
| `Board_Reborn` | 830 | 139 | 60 | 15 |
| `Board_Challange` | 791 | 135 | 49 | 13 |
| `Board_QuestRewards` | 694 | 96 | 27 | 10 |
| `Popup_ShipSalePack` | 689 | 18 | 7 | 10 |
| `Board_Stage` | 654 | 121 | 51 | 11 |
| `Board_ShopEnergy` | 622 | 96 | 32 | 9 |
| `Board_Vip` | 586 | 42 | 15 | 8 |
| `Tab_Boss` | 555 | 7 | 1 | 7 |
| `Board_EventSeasonPass` | 544 | 86 | 28 | 9 |
| `Popup_HolidayGift` | 532 | 67 | 11 | 7 |
| `Popup_HolidayGift` | 519 | 71 | 9 | 7 |
| `Popup_PvPRankings` | 454 | 51 | 18 | 7 |
| `Board_EventSeasonPass` | 444 | 64 | 16 | 7 |
| `Board_Begin` | 407 | 36 | 14 | 5 |
| `Popup_WatchVideosOld` | 355 | 51 | 13 | 5 |
| `Board_Reborn_IAP` | 344 | 69 | 15 | 5 |
| `Board_Talents` | 340 | 30 | 10 | 4 |
| `Popup_Notices` | 338 | 64 | 14 | 5 |
| `Popup_Notices` | 324 | 58 | 14 | 5 |
| `Popup_BuyMoreGems` | 322 | 54 | 14 | 5 |
| `Board_Talents` | 321 | 28 | 8 | 4 |
| `Popup_Notices` | 320 | 55 | 14 | 5 |

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
