# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **610**
- tổng node: **83908**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 72902 |
| `SpriteRenderer` | 39575 |
| `MeshRenderer` | 12181 |
| `RectTransform` | 11006 |
| `TextMeshPro` | 10947 |
| `MeshFilter` | 10063 |
| `BoxCollider2D` | 5831 |
| `Animator` | 4188 |
| `ButtonEvents` | 3975 |
| `Button_Sound` | 3859 |
| `ParticleSystem` | 3031 |
| `ParticleSystemRenderer` | 3031 |
| `LanguageTextMeshPro` | 2845 |
| `ChangeSorting` | 1794 |
| `BgObjectScaler` | 1322 |
| `Popup_Notices` | 1023 |
| `Box_Rewards` | 931 |
| `TMP_SubMesh` | 849 |
| `UIObjectAnchors` | 623 |
| `Shop_Cell` | 568 |
| `FixUIShop` | 503 |
| `ObjectPool` | 322 |
| `Rigidbody2D` | 309 |
| `Enemy_Datas` | 270 |
| `Enemy_Health` | 270 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 4114 | 367 | 203 | 52 |
| `Board_Shop` | 3454 | 599 | 172 | 47 |
| `Board_PVP` | 2538 | 373 | 163 | 39 |
| `Board_FightBoss` | 2474 | 131 | 47 | 39 |
| `Board_SelectBoss` | 2248 | 107 | 16 | 29 |
| `Board_Arena` | 1990 | 284 | 119 | 32 |
| `Tab_Boss` | 1879 | 6 | 0 | 29 |
| `Board_Players` | 1813 | 198 | 79 | 30 |
| `Board_TechLab` | 1297 | 138 | 59 | 19 |
| `Board_Ranks` | 1260 | 190 | 77 | 21 |
| `Board_Survival` | 1170 | 188 | 80 | 19 |
| `Board_Begin` | 1075 | 146 | 52 | 16 |
| `Board_BattlePassPro` | 988 | 132 | 43 | 15 |
| `Board_Drones` | 978 | 136 | 60 | 17 |
| `Popup_WatchVideos` | 890 | 167 | 48 | 13 |
| `Board_Reborn` | 859 | 155 | 61 | 15 |
| `Board_Challange` | 802 | 141 | 52 | 13 |
| `Popup_WatchVideos` | 797 | 146 | 44 | 12 |
| `Board_Vip` | 785 | 97 | 27 | 11 |
| `Board_Combo` | 752 | 85 | 40 | 11 |
| `Board_GiftLogin` | 698 | 118 | 28 | 11 |
| `Board_QuestRewards` | 663 | 86 | 24 | 10 |
| `Board_ShopEnergy` | 609 | 99 | 34 | 9 |
| `Board_UserProfile` | 596 | 59 | 48 | 9 |
| `Board_EventSeasonPass` | 557 | 94 | 29 | 10 |
| `Popup_HolidayGift` | 540 | 75 | 11 | 7 |
| `Popup_HolidayGift` | 525 | 69 | 10 | 7 |
| `Popup_ShipSalePack` | 515 | 17 | 7 | 8 |
| `Board_EventSeasonPass` | 456 | 68 | 20 | 7 |
| `Board_Begin` | 413 | 33 | 15 | 5 |
| `Popup_PvPRankings` | 387 | 43 | 19 | 7 |
| `Board_Reborn_IAP` | 362 | 69 | 15 | 5 |
| `Popup_WatchVideosOld` | 353 | 58 | 13 | 5 |
| `Popup_Notices` | 346 | 67 | 15 | 5 |
| `Popup_PvPRankings` | 343 | 44 | 16 | 6 |
| `Board_Profile` | 342 | 25 | 16 | 5 |
| `Popup_Notices` | 334 | 62 | 15 | 5 |
| `Board_Talents` | 334 | 30 | 9 | 4 |
| `Popup_BuyMoreGems` | 332 | 62 | 15 | 5 |
| `Popup_Notices` | 332 | 62 | 13 | 5 |

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
