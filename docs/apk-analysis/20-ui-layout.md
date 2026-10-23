# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **728**
- tổng node: **102697**
- dung lượng thô (gz): **2.0 MB**

- bỏ qua: duplicate (class, root) (65)

## Component gặp nhiều nhất

| class | số node |
|---|---:|
| `Transform` | 89097 |
| `SpriteRenderer` | 48510 |
| `MeshRenderer` | 15055 |
| `RectTransform` | 13600 |
| `TextMeshPro` | 13525 |
| `MeshFilter` | 12276 |
| `BoxCollider2D` | 7241 |
| `Animator` | 5274 |
| `ButtonEvents` | 4940 |
| `Button_Sound` | 4782 |
| `LanguageTextMeshPro` | 3561 |
| `ParticleSystem` | 3496 |
| `ParticleSystemRenderer` | 3496 |
| `ChangeSorting` | 2178 |
| `BgObjectScaler` | 1603 |
| `Popup_Notices` | 1238 |
| `Box_Rewards` | 1220 |
| `TMP_SubMesh` | 1018 |
| `UIObjectAnchors` | 734 |
| `Shop_Cell` | 661 |
| `FixUIShop` | 584 |
| `Rigidbody2D` | 360 |
| `ObjectPool` | 354 |
| `Enemy_Datas` | 303 |
| `Enemy_Health` | 303 |

- node không đọc được component: **0**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Board_Maps` | 3724 | 274 | 182 | 45 |
| `Board_Shop` | 3365 | 509 | 158 | 44 |
| `Board_PVP` | 2765 | 357 | 174 | 40 |
| `Board_FightBoss` | 2578 | 120 | 41 | 41 |
| `Board_SelectBoss` | 2442 | 89 | 16 | 35 |
| `Board_Arena` | 2088 | 288 | 124 | 33 |
| `Board_Players` | 1826 | 198 | 78 | 30 |
| `Board_BattlePass` | 1691 | 232 | 62 | 18 |
| `Tab_Boss` | 1642 | 6 | 0 | 26 |
| `Board_Ranks` | 1526 | 223 | 91 | 24 |
| `Board_Ranks` | 1430 | 212 | 85 | 22 |
| `Board_TechLab` | 1291 | 151 | 67 | 19 |
| `Board_Survival` | 1204 | 189 | 79 | 20 |
| `Board_Survival` | 1105 | 123 | 70 | 17 |
| `Board_WinnerBenefits` | 1005 | 165 | 58 | 15 |
| `Popup_WatchVideos` | 972 | 165 | 48 | 14 |
| `Board_BattlePassPro` | 943 | 135 | 43 | 14 |
| `Board_Drones` | 928 | 114 | 61 | 15 |
| `Board_Endgame` | 912 | 127 | 51 | 16 |
| `Board_Begin` | 909 | 128 | 46 | 14 |
| `Popup_WatchVideos` | 894 | 159 | 47 | 13 |
| `Board_Combo` | 851 | 88 | 51 | 13 |
| `Board_Reborn` | 843 | 130 | 56 | 15 |
| `Board_Setting` | 837 | 102 | 64 | 13 |
| `Board_MiniCombo` | 836 | 83 | 47 | 13 |
| `Board_GiftLogin` | 803 | 122 | 27 | 12 |
| `Board_Stage` | 793 | 131 | 52 | 12 |
| `Board_Challange` | 771 | 134 | 51 | 12 |
| `Board_Vip` | 760 | 83 | 26 | 11 |
| `Board_UserProfile` | 712 | 63 | 50 | 10 |
| `Board_QuestRewards` | 650 | 75 | 25 | 9 |
| `Board_ShopEnergy` | 618 | 107 | 35 | 9 |
| `Board_EventSeasonPass` | 530 | 90 | 26 | 9 |
| `Popup_HolidayGift` | 523 | 66 | 11 | 7 |
| `Popup_HolidayGift` | 514 | 78 | 11 | 7 |
| `Popup_ShipSalePack` | 502 | 14 | 6 | 8 |
| `Board_EventSeasonPass` | 479 | 71 | 21 | 7 |
| `Popup_PvPRankings` | 417 | 56 | 15 | 7 |
| `Board_Quest` | 383 | 105 | 39 | 5 |
| `Board_Profile` | 374 | 26 | 16 | 5 |

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
