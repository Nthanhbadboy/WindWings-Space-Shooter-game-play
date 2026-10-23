# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **10814**, màn (class): **114**, node: **1,986,015**
- dòng text/key: **194,595** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 18 | 6,000 | 344 | 94 | 689 | 206 | -12.39…12.24 | -22.6…676.38 |
| `Board_Shop` | 11 | 3,898 | 204 | 51 | 332 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 16 | 3,005 | 207 | 72 | 327 | 162 | -5.45…16.09 | -60.21…8.9 |
| `Board_FightBoss` | 11 | 2,649 | 67 | 16 | 94 | 294 | -14.22…14.8 | -44.18…47.26 |
| `Board_SelectBoss` | 12 | 2,621 | 6 | 2 | 34 | 221 | -17.24…11.76 | -9.6…204.29 |
| `Board_Arena` | 13 | 2,049 | 170 | 65 | 240 | 229 | -5.28…5.81 | -51.84…8.8 |
| `Board_BigShop` | 15 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 26 | 2,000 | 142 | 63 | 183 | 122 | None…None | None…None |
| `Board_ShopCoins` | 14 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 67 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 135 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 141 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 227 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 295 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 144 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 68 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 29 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 28 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 6844 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 26 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 13 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 139 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 33 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 13 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 27 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 32 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Boss` | 212 | 2,000 | 7 | 2 | 2 | 255 | None…None | None…None |
| `Tab_Button` | 87 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 30 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 7 | 1,886 | 44 | 17 | 137 | 86 | -7.23…5.13 | -94.51…8.19 |
| `Tab_BattlePass` | 374 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Board_Players` | 15 | 1,823 | 119 | 31 | 160 | 140 | -11.2…13.35 | -9.6…14.25 |
| `Popup_ArenaInfo` | 25 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 130 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 16 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 18 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 14 | 1,459 | 74 | 13 | 154 | 118 | -10.04…9.0 | -9.6…14.0 |
| `Board_Survival` | 28 | 1,418 | 143 | 59 | 173 | 118 | -4.68…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 32 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Drones` | 12 | 1,093 | 94 | 21 | 124 | 134 | -5.62…4.75 | -9.6…7.5 |
| `Board_Begin` | 33 | 1,075 | 61 | 17 | 104 | 115 | -5.22…4.55 | -17.6…11.46 |
| `Board_Reborn_IAP` | 41 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_WinnerBenefits` | 12 | 1,022 | 80 | 21 | 104 | 100 | -4.86…5.0 | -7.37…7.94 |
| `Board_Combo` | 12 | 991 | 45 | 25 | 119 | 88 | -12.41…7.92 | -49.65…8.25 |
| `Board_BattlePassPro` | 14 | 988 | 66 | 22 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_Talents` | 40 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Tab_BattlePassMission` | 48 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 16 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_Setting` | 10 | 952 | 58 | 42 | 133 | 85 | -4.5…4.76 | -25.75…20.0 |
| `Popup_BattlePassLevelUp` | 16 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_MiniCombo` | 8 | 925 | 45 | 25 | 105 | 85 | -5.62…5.61 | -44.41…8.25 |
| `Board_Reborn` | 12 | 913 | 89 | 28 | 120 | 117 | -6.12…4.55 | -9.6…9.35 |
| `Board_GiftLogin` | 17 | 908 | 63 | 23 | 57 | 86 | -4.96…5.0 | -9.48…8.15 |
| `Board_Endgame` | 11 | 889 | 88 | 37 | 99 | 122 | -5.83…5.21 | -9.6…9.6 |
| `Board_Challange` | 18 | 866 | 77 | 22 | 104 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 12 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 52 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 12 | 823 | 74 | 21 | 106 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 14 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 18 | 789 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 12 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Popup_Community` | 10 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_SelectBenefits` | 16 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_ShipSalePack` | 16 | 728 | 16 | 7 | 14 | 84 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectShipCombo` | 45 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 33 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Board_QuestRewards` | 15 | 715 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Popup_ChangeLanguages` | 25 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Board_UserProfile` | 10 | 712 | 53 | 31 | 100 | 80 | -4.39…5.81 | -21.98…8.8 |
| `Popup_SelectItemCombo` | 28 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 16 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 17 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 14 | 645 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 31 | 587 | 42 | 17 | 58 | 76 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 26 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_Rename` | 12 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_WeekSales` | 12 | 494 | 24 | 13 | 25 | 55 | None…None | None…None |
| `Popup_ChangeAvatar` | 17 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 28 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 15 | 376 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 10 | 330 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 11 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_EventLevelUp` | 36 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 11 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 15 | 319 | 17 | 5 | 14 | 51 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 13 | 314 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_VideoCards` | 13 | 313 | 38 | 12 | 34 | 74 | -4.86…4.55 | -8.05…9.1 |
| `Popup_FirstPurchase` | 14 | 300 | 12 | 6 | 8 | 59 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 84 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 16 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 9 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 10 | 205 | 33 | 25 | 26 | 47 | None…None | None…None |
| `Board_BlackBox` | 12 | 185 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 11 | 174 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 23 | 162 | 6 | 1 | 2 | 35 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 17 | 134 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 13 | 128 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 48 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 12 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 17 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 30 | 86 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 13 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 9 | 61 | 7 | 1 | 4 | 20 | -3.89…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 15 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 14 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 14 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 15 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 13 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 13 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 14 | 19 | 4 | 4 | 6 | 5 | None…None | None…None |
| `Popup_Update` | 11 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 14 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 16 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 17 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

## Hệ toạ độ (suy ra từ bbox, mức C)

- bề rộng bbox phổ biến: `[0.0, 1.8, 4.1] … [24.5, 24.6, 29.0]`
- chiều cao bbox phổ biến: `[0.0, 1.9, 3.2] … [102.7, 213.9, 699.0]`
- toạ độ là **unit world-space của prefab**, không phải pixel màn hình;
  muốn ra pixel phải nhân với `orthographicSize` của camera runtime (chưa bóc được).
- vì vậy mọi con số ở đây dùng để **so sánh tỉ lệ giữa các màn**, không phải để đặt pixel.

## Text & localization key

| màn | dòng text | có key | % có key |
|---|---:|---:|---:|
| `Popup_Notices` | 48513 | 13722 | 28% |
| `Popup_BuyMoreGems` | 15357 | 1481 | 10% |
| `Board_Maps` | 7958 | 1588 | 20% |
| `Popup_BuyMoreCoins` | 7312 | 1616 | 22% |
| `Board_PVP` | 6140 | 1243 | 20% |
| `Board_Shop` | 5843 | 899 | 15% |
| `Board_Ranks` | 5798 | 1461 | 25% |
| `Board_Survival` | 5759 | 1414 | 25% |
| `Popup_Profile` | 5607 | 1746 | 31% |
| `Popup_WatchVideos` | 5081 | 904 | 18% |
| `Popup_PremiumDailyRewards` | 3920 | 371 | 9% |
| `Board_Arena` | 3635 | 809 | 22% |
| `Board_Players` | 3185 | 594 | 19% |
| `Tab_BattlePass` | 2936 | 503 | 17% |
| `Board_EventSeasonPass` | 2649 | 535 | 20% |
| `Board_Begin` | 2570 | 355 | 14% |
| `Board_Challange` | 2389 | 424 | 18% |
| `Board_Reborn_IAP` | 2254 | 215 | 10% |
| `Board_TechLab` | 2056 | 253 | 12% |
| `Board_GiftLogin` | 2048 | 323 | 16% |
| `Popup_BuyItem` | 2025 | 543 | 27% |
| `Board_BattlePass` | 1995 | 319 | 16% |
| `Popup_ChooseVersionDatas` | 1857 | 390 | 21% |
| `Popup_HolidayGift` | 1798 | 222 | 12% |
| `Board_Drones` | 1796 | 308 | 17% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
