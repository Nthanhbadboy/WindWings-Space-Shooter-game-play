# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **7173**, màn (class): **114**, node: **1,493,737**
- dòng text/key: **117,245** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 12 | 6,000 | 338 | 91 | 689 | 198 | -12.39…12.24 | -22.6…676.38 |
| `Board_Shop` | 8 | 3,898 | 203 | 51 | 332 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 11 | 3,005 | 207 | 72 | 327 | 161 | -5.45…16.09 | -60.21…8.9 |
| `Board_FightBoss` | 7 | 2,649 | 67 | 16 | 94 | 294 | -14.22…14.8 | -44.18…47.26 |
| `Board_SelectBoss` | 8 | 2,621 | 6 | 2 | 34 | 216 | -17.24…11.76 | -9.6…204.29 |
| `Board_Arena` | 9 | 2,049 | 170 | 65 | 240 | 224 | -5.28…5.81 | -51.84…8.8 |
| `Board_BigShop` | 10 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 17 | 2,000 | 142 | 63 | 183 | 122 | None…None | None…None |
| `Board_ShopCoins` | 10 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 45 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 89 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 92 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 151 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 195 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 94 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 45 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 18 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 19 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 4537 | 2,000 | 188 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 19 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 8 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 96 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 24 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 11 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 17 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 21 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Boss` | 136 | 2,000 | 7 | 2 | 2 | 255 | None…None | None…None |
| `Tab_Button` | 57 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 22 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Tab_BattlePass` | 250 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Board_Players` | 10 | 1,823 | 119 | 31 | 160 | 140 | -11.2…13.35 | -9.6…14.25 |
| `Popup_ArenaInfo` | 16 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Board_BattlePass` | 4 | 1,750 | 44 | 17 | 137 | 85 | -7.23…5.13 | -94.51…8.19 |
| `Popup_PremiumDailyRewards` | 86 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 10 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 12 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 9 | 1,407 | 74 | 13 | 154 | 117 | -10.04…9.42 | -9.6…14.0 |
| `Board_Survival` | 19 | 1,375 | 143 | 59 | 173 | 118 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 21 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Drones` | 7 | 1,093 | 94 | 21 | 124 | 134 | -5.62…4.75 | -9.6…7.5 |
| `Board_Reborn_IAP` | 28 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_Begin` | 22 | 1,009 | 61 | 17 | 104 | 115 | -5.22…4.55 | -17.6…11.46 |
| `Board_BattlePassPro` | 8 | 988 | 65 | 22 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_Talents` | 27 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Tab_BattlePassMission` | 33 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Board_WinnerBenefits` | 8 | 975 | 80 | 21 | 104 | 100 | -4.86…5.0 | -7.37…7.94 |
| `Popup_ChangeMissions` | 10 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_Combo` | 8 | 958 | 45 | 25 | 119 | 88 | -6.27…7.92 | -50.29…8.25 |
| `Board_Setting` | 8 | 952 | 58 | 42 | 129 | 85 | -4.5…4.76 | -25.75…20.0 |
| `Popup_BattlePassLevelUp` | 12 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_MiniCombo` | 7 | 925 | 45 | 25 | 105 | 85 | -5.62…5.61 | -44.41…8.25 |
| `Board_Reborn` | 8 | 913 | 89 | 28 | 120 | 117 | -6.12…4.55 | -9.6…9.35 |
| `Board_GiftLogin` | 12 | 908 | 63 | 23 | 57 | 86 | -4.96…5.0 | -9.48…8.15 |
| `Board_Challange` | 12 | 866 | 77 | 22 | 104 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Board_Endgame` | 6 | 856 | 88 | 37 | 99 | 117 | -4.85…5.21 | -9.6…9.6 |
| `Popup_LuckyStar` | 7 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 35 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 8 | 823 | 74 | 21 | 106 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 9 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 12 | 784 | 53 | 11 | 54 | 83 | None…None | None…None |
| `Popup_About` | 7 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Popup_Community` | 7 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_SelectBenefits` | 10 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_ShipSalePack` | 11 | 728 | 16 | 7 | 14 | 84 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectShipCombo` | 31 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 22 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Board_QuestRewards` | 10 | 715 | 50 | 11 | 54 | 77 | -4.5…4.76 | -7.69…7.5 |
| `Popup_ChangeLanguages` | 18 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Board_UserProfile` | 6 | 712 | 53 | 31 | 100 | 79 | -4.39…5.81 | -21.98…8.8 |
| `Popup_SelectItemCombo` | 13 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 11 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 12 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 8 | 622 | 64 | 18 | 64 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 19 | 587 | 42 | 17 | 58 | 76 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 17 | 555 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_Rename` | 9 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_WeekSales` | 8 | 494 | 24 | 13 | 25 | 55 | None…None | None…None |
| `Popup_ChangeAvatar` | 12 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 18 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 9 | 376 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 8 | 330 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 8 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_EventLevelUp` | 24 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 9 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_VideoCards` | 9 | 313 | 38 | 12 | 34 | 71 | -4.86…4.55 | -8.05…9.1 |
| `Popup_UpgradeTechIAP` | 10 | 304 | 17 | 5 | 14 | 51 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 9 | 300 | 8 | 1 | 62 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Tab_Item` | 54 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Popup_FirstPurchase` | 10 | 296 | 12 | 6 | 8 | 58 | -4.5…4.76 | -7.0…8.0 |
| `Board_Home` | 10 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 5 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 7 | 205 | 33 | 25 | 26 | 47 | None…None | None…None |
| `Board_BlackBox` | 6 | 182 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 8 | 174 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 16 | 162 | 6 | 1 | 2 | 34 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 12 | 134 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 9 | 128 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 33 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 8 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 12 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 19 | 86 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 9 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 6 | 61 | 7 | 1 | 4 | 20 | -3.89…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 9 | 59 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 9 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 9 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 10 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 9 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 8 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 10 | 19 | 4 | 4 | 6 | 5 | None…None | None…None |
| `Popup_Update` | 8 | 19 | 4 | 3 | 4 | 6 | None…None | None…None |
| `Popup_InrerestExpired` | 9 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 10 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 11 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

## Hệ toạ độ (suy ra từ bbox, mức C)

- bề rộng bbox phổ biến: `[0.0, 1.8, 4.1] … [24.5, 24.6, 29.0]`
- chiều cao bbox phổ biến: `[0.0, 1.9, 3.2] … [102.7, 213.9, 699.0]`
- toạ độ là **unit world-space của prefab**, không phải pixel màn hình;
  muốn ra pixel phải nhân với `orthographicSize` của camera runtime (chưa bóc được).
- vì vậy mọi con số ở đây dùng để **so sánh tỉ lệ giữa các màn**, không phải để đặt pixel.

## Text & localization key

| màn | dòng text | có key | % có key |
|---|---:|---:|---:|
| `Popup_Notices` | 29117 | 8202 | 28% |
| `Popup_BuyMoreGems` | 9127 | 876 | 10% |
| `Board_Maps` | 4761 | 946 | 20% |
| `Popup_BuyMoreCoins` | 4311 | 945 | 22% |
| `Board_Shop` | 3937 | 602 | 15% |
| `Board_PVP` | 3709 | 751 | 20% |
| `Popup_Profile` | 3526 | 1093 | 31% |
| `Board_Survival` | 3482 | 867 | 25% |
| `Board_Ranks` | 3351 | 837 | 25% |
| `Popup_WatchVideos` | 2989 | 533 | 18% |
| `Board_Arena` | 2375 | 531 | 22% |
| `Popup_PremiumDailyRewards` | 2327 | 227 | 10% |
| `Board_Players` | 2124 | 393 | 19% |
| `Tab_BattlePass` | 1790 | 317 | 18% |
| `Board_Begin` | 1555 | 231 | 15% |
| `Board_EventSeasonPass` | 1468 | 295 | 20% |
| `Board_Challange` | 1444 | 260 | 18% |
| `Board_Reborn_IAP` | 1334 | 126 | 9% |
| `Board_GiftLogin` | 1323 | 206 | 16% |
| `Board_TechLab` | 1206 | 149 | 12% |
| `Board_Stage` | 1153 | 208 | 18% |
| `Board_BattlePass` | 1149 | 182 | 16% |
| `Popup_BuyItem` | 1132 | 303 | 27% |
| `Popup_PvPRankings` | 1088 | 319 | 29% |
| `Popup_ChooseVersionDatas` | 1086 | 230 | 21% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
