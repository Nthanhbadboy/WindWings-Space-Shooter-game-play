# UI layout (số đo bóc từ prefab)

> **Kết luận tạm thời.** Đây là giá trị *serialize trong prefab*. Runtime có thể
> ghi đè (layout group, safe area, code set anchor), nên chỉ dùng làm khung tham
> chiếu. Dữ liệu thô: `reverse-engineering/raw/ui/*.json.gz`.

- màn hình dump được: **548**
- tổng node: **593028**
- dung lượng thô (gz): **6.6 MB**

## Màn hình nhiều node nhất

| class | node | text | button | KB |
|---|---:|---:|---:|---:|
| `Popup_Notices` | 2000 | 0 | 0 | 22 |
| `Popup_Notices` | 2000 | 0 | 0 | 22 |
| `Popup_BuyMoreGems` | 2000 | 0 | 0 | 22 |
| `Popup_Notices` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 21 |
| `Popup_Notices` | 2000 | 0 | 0 | 23 |
| `Popup_AbilityEvent1` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Fotification` | 2000 | 0 | 0 | 20 |
| `Popup_Profile` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 21 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Profile` | 2000 | 0 | 0 | 23 |
| `Popup_JoinRank` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 22 |
| `Popup_BuyMoreCoins` | 2000 | 0 | 0 | 20 |
| `Board_Maps` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_SeasonRewards` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 23 |
| `Tab_Boss` | 2000 | 0 | 0 | 21 |
| `Popup_WatchVideos` | 2000 | 0 | 0 | 20 |
| `Popup_PvPRankings` | 2000 | 0 | 0 | 23 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |
| `Popup_Notices` | 2000 | 0 | 0 | 20 |

## Cấu trúc mỗi node

```json
{"path": "Background/Star_01", "depth": 2, "active": 1,
 "anchor_min": [0,0], "anchor_max": [1,1], "anchored_pos": [0,0],
 "size_delta": [0,0], "pivot": [0.5,0.5], "scale": [1,1,1],
 "components": [{"class":"Image","sprite":"Star"},
                 {"class":"LanguageTextMeshPro","key":"txt_play","text":"Play"}]}
```

- Toạ độ là **local space của RectTransform cha**, đơn vị Unity
  (canvas tham chiếu thường 1080×1920 → 1 unit = 100 px).
- `anchor_min`/`anchor_max` quyết định responsive: `[0,0]`–`[1,1]` = full stretch.
- `size_delta` = kích thước khi anchor không stretch; khi stretch thì là phần cộng thêm.
