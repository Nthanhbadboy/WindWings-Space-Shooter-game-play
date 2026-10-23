# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **631**
- tổng node: **82394**
- dung lượng thô (gz): **1.6 MB**

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 71124 |
| `SpriteRenderer` | 39098 |
| `MeshRenderer` | 12435 |
| `RectTransform` | 11270 |
| `TextMeshPro` | 11207 |
| `MeshFilter` | 10344 |
| `BoxCollider2D` | 5984 |
| `ButtonEvents` | 4141 |
| `Animator` | 4069 |
| `Button_Sound` | 4065 |
| `LanguageTextMeshPro` | 2923 |
| `ParticleSystem` | 2485 |
| `ParticleSystemRenderer` | 2485 |
| `ChangeSorting` | 1786 |
| `BgObjectScaler` | 1333 |
| `Popup_Notices` | 1050 |
| `TMP_SubMesh` | 871 |
| `Box_Rewards` | 796 |
| `Shop_Cell` | 597 |
| `UIObjectAnchors` | 590 |
| `FixUIShop` | 551 |
| `LineRenderer` | 194 |
| `AutoSetVipIcon` | 186 |
| `Stage_Behaviour` | 178 |
| `ObjectPool` | 176 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 6000 | 425 | 340 | 61 |
| `Board_SelectBoss` | 2621 | 114 | 17 | 36 |
| `Board_PVP` | 2437 | 335 | 156 | 37 |
| `Board_Arena` | 2049 | 278 | 123 | 32 |
| `Board_Players` | 1763 | 187 | 79 | 28 |
| `Board_Ranks` | 1532 | 226 | 89 | 24 |
| `Board_Ranks` | 1504 | 211 | 91 | 23 |
| `Board_TechLab` | 1288 | 145 | 66 | 18 |
| `Board_Survival` | 1205 | 180 | 82 | 20 |
| `Board_Drones` | 1083 | 137 | 61 | 18 |
| `Popup_WatchVideos` | 964 | 172 | 49 | 14 |
| `Board_Setting` | 952 | 107 | 65 | 13 |
| `Board_Begin` | 941 | 120 | 46 | 15 |
| `Board_Reborn` | 899 | 155 | 61 | 15 |
| `Board_Challange` | 851 | 138 | 53 | 13 |
| `Board_BattlePassPro` | 836 | 116 | 40 | 13 |
| `Board_GiftLogin` | 835 | 111 | 26 | 12 |
| `Board_Stage` | 784 | 140 | 52 | 12 |
| `Board_Vip` | 758 | 101 | 27 | 11 |
| `Board_Combo` | 688 | 71 | 33 | 10 |
| `Board_QuestRewards` | 654 | 90 | 24 | 9 |
| `Board_EventSeasonPass` | 587 | 97 | 29 | 10 |
| `Popup_HolidayGift` | 520 | 65 | 11 | 7 |
| `Board_MiniCombo` | 513 | 64 | 25 | 8 |
| `Board_EventSeasonPass` | 482 | 71 | 22 | 7 |
| `Popup_WeekSales` | 478 | 57 | 14 | 6 |
| `Board_Reborn_IAP` | 376 | 69 | 15 | 5 |
| `Popup_PvPRankings` | 375 | 51 | 18 | 7 |
| `Popup_WatchVideosOld` | 362 | 60 | 13 | 5 |
| `Board_Profile` | 360 | 24 | 12 | 5 |
| `Popup_BuyMoreGems` | 346 | 67 | 15 | 5 |
| `Board_Quest` | 343 | 90 | 37 | 4 |
| `Board_Reborn_IAP` | 343 | 64 | 15 | 5 |
| `Popup_Notices` | 340 | 62 | 15 | 5 |
| `Board_Talents` | 339 | 32 | 10 | 4 |
| `Popup_Notices` | 338 | 61 | 14 | 5 |
| `Board_Talents` | 338 | 30 | 8 | 4 |
| `Popup_BuyMoreGems` | 336 | 61 | 15 | 5 |
| `Board_Begin` | 335 | 21 | 6 | 4 |
| `Popup_Notices` | 334 | 59 | 15 | 5 |

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
