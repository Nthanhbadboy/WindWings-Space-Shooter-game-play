# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **31036**, màn (class): **114**, node: **4,890,769**
- dòng text/key: **648,589** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 46 | 6,000 | 345 | 95 | 690 | 206 | -12.39…12.24 | -20.3…676.38 |
| `Board_Shop` | 38 | 3,898 | 204 | 51 | 336 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 44 | 3,005 | 207 | 72 | 329 | 162 | -5.45…16.09 | -60.21…8.9 |
| `Board_SelectBoss` | 39 | 2,692 | 6 | 2 | 34 | 234 | -17.24…11.76 | -9.6…204.29 |
| `Board_FightBoss` | 39 | 2,649 | 67 | 16 | 94 | 303 | -14.22…14.8 | -44.18…47.26 |
| `Board_Arena` | 41 | 2,104 | 170 | 65 | 241 | 234 | -5.37…5.81 | -51.84…8.8 |
| `Tab_Boss` | 678 | 2,035 | 7 | 2 | 2 | 255 | -14.22…29.63 | -44.18…47.26 |
| `Board_BigShop` | 42 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 82 | 2,000 | 142 | 63 | 185 | 124 | None…None | None…None |
| `Board_ShopCoins` | 41 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 178 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 411 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 438 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 691 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 845 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 445 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 206 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 84 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 84 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 19016 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 80 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 41 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 417 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 114 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 41 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 82 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 88 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Button` | 253 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 85 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 35 | 1,940 | 44 | 17 | 141 | 87 | -7.23…5.13 | -94.51…8.19 |
| `Board_Players` | 43 | 1,915 | 119 | 31 | 160 | 140 | -7.65…13.35 | -9.6…14.69 |
| `Tab_BattlePass` | 1181 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Popup_ArenaInfo` | 80 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 405 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 44 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 45 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 41 | 1,459 | 74 | 13 | 158 | 118 | -10.04…9.0 | -9.6…14.0 |
| `Board_Survival` | 84 | 1,455 | 143 | 59 | 176 | 121 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 88 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Begin` | 89 | 1,101 | 61 | 17 | 108 | 117 | -5.22…4.51 | -17.6…11.46 |
| `Board_Drones` | 40 | 1,100 | 94 | 21 | 124 | 140 | -6.27…4.75 | -9.6…7.5 |
| `Board_BattlePassPro` | 40 | 1,039 | 68 | 23 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_WinnerBenefits` | 40 | 1,034 | 80 | 21 | 106 | 100 | -4.86…4.55 | -7.37…7.94 |
| `Board_Reborn_IAP` | 121 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_Combo` | 40 | 1,008 | 45 | 25 | 119 | 92 | -12.41…7.92 | -50.29…8.25 |
| `Board_Talents` | 121 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Board_MiniCombo` | 34 | 983 | 45 | 25 | 117 | 93 | -12.41…7.92 | -50.29…8.25 |
| `Board_Setting` | 36 | 980 | 58 | 42 | 135 | 87 | -4.5…4.76 | -25.75…20.0 |
| `Tab_BattlePassMission` | 131 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 44 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_GiftLogin` | 44 | 955 | 63 | 23 | 57 | 87 | -4.96…5.12 | -9.48…8.15 |
| `Popup_BattlePassLevelUp` | 44 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_Endgame` | 39 | 931 | 90 | 38 | 102 | 126 | -5.83…5.21 | -9.6…9.6 |
| `Board_Reborn` | 38 | 917 | 89 | 28 | 120 | 117 | -5.24…4.55 | -9.6…9.35 |
| `Board_Challange` | 46 | 866 | 77 | 22 | 106 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 40 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 163 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 40 | 823 | 74 | 21 | 108 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 40 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 46 | 792 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 40 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Board_UserProfile` | 37 | 757 | 53 | 31 | 100 | 81 | -5.37…5.81 | -21.98…8.8 |
| `Popup_Community` | 36 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_ShipSalePack` | 44 | 744 | 16 | 7 | 14 | 85 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectBenefits` | 43 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_SelectShipCombo` | 128 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_QuestRewards` | 41 | 720 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Board_Profile` | 116 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Popup_ChangeLanguages` | 78 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Popup_SelectItemCombo` | 111 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 43 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 45 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 40 | 645 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 87 | 601 | 42 | 17 | 58 | 77 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 81 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_WeekSales` | 38 | 496 | 24 | 13 | 25 | 55 | -5.95…4.76 | -7.0…8.0 |
| `Popup_Rename` | 40 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_ChangeAvatar` | 43 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 84 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 43 | 384 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 37 | 374 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 38 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_VideoCards` | 41 | 328 | 38 | 12 | 34 | 76 | -4.86…4.55 | -8.05…9.1 |
| `Popup_EventLevelUp` | 92 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 38 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 43 | 319 | 17 | 5 | 14 | 53 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 41 | 314 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_FirstPurchase` | 42 | 304 | 12 | 6 | 8 | 60 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 251 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 43 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 37 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 37 | 212 | 33 | 25 | 26 | 49 | -5.24…4.49 | -9.6…9.6 |
| `Board_BlackBox` | 38 | 185 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 38 | 175 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 78 | 162 | 6 | 1 | 2 | 35 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 45 | 135 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 40 | 134 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 131 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 39 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 44 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 86 | 87 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 39 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 35 | 61 | 7 | 1 | 4 | 20 | -3.96…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 41 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 42 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 42 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 42 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 40 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 39 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 41 | 19 | 4 | 4 | 6 | 5 | -2.5…3.7 | -1.8…3.1 |
| `Popup_Update` | 38 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 40 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 44 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 45 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

## Hệ toạ độ (suy ra từ bbox, mức C)

- bề rộng bbox phổ biến: `[0.0, 1.8, 4.1] … [24.6, 29.0, 43.9]`
- chiều cao bbox phổ biến: `[0.0, 1.9, 3.2] … [102.7, 213.9, 696.7]`
- toạ độ là **unit world-space của prefab**, không phải pixel màn hình;
  muốn ra pixel phải nhân với `orthographicSize` của camera runtime (chưa bóc được).
- vì vậy mọi con số ở đây dùng để **so sánh tỉ lệ giữa các màn**, không phải để đặt pixel.

## Camera (đo từ prefab, mức A)

- số Camera trong build: **6**, tất cả orthographic
- `orthographicSize` = **9.6** → chiều cao vùng thấy được = **19.2 world-unit**
- khớp mốc spawn `y = 9,6` trong dữ liệu wave: quân hiện ở đúng mép trên màn hình.
- đổi sang pixel: `px = world / (2 × 9,6) × screenHeight`.

## Text & localization key

| màn | dòng text | có key | % có key |
|---|---:|---:|---:|
| `Popup_Notices` | 150489 | 42756 | 28% |
| `Popup_BuyMoreGems` | 50077 | 4932 | 10% |
| `Popup_BuyMoreCoins` | 25248 | 5623 | 22% |
| `Board_Shop` | 23243 | 3611 | 16% |
| `Board_Maps` | 22806 | 4539 | 20% |
| `Board_Ranks` | 21049 | 5288 | 25% |
| `Board_Survival` | 19586 | 4821 | 25% |
| `Board_PVP` | 19171 | 3886 | 20% |
| `Popup_Profile` | 18889 | 5853 | 31% |
| `Popup_WatchVideos` | 15609 | 2785 | 18% |
| `Popup_PremiumDailyRewards` | 14038 | 1331 | 9% |
| `Board_Arena` | 12413 | 2667 | 21% |
| `Tab_BattlePass` | 10319 | 1757 | 17% |
| `Board_BattlePass` | 9858 | 1565 | 16% |
| `Board_Players` | 9591 | 1804 | 19% |
| `Board_EventSeasonPass` | 8265 | 1679 | 20% |
| `Board_Begin` | 7857 | 1120 | 14% |
| `Board_Reborn_IAP` | 7506 | 700 | 9% |
| `Popup_BuyItem` | 7407 | 1991 | 27% |
| `Board_Challange` | 6996 | 1235 | 18% |
| `Board_TechLab` | 6697 | 867 | 13% |
| `Popup_ChooseVersionDatas` | 6686 | 1438 | 22% |
| `Board_WinnerBenefits` | 6568 | 1346 | 20% |
| `Board_Reborn` | 6375 | 1329 | 21% |
| `Popup_HolidayGift` | 6277 | 810 | 13% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
