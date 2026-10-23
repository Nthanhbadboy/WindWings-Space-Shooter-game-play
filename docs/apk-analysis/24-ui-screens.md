# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **23711**, màn (class): **114**, node: **3,834,253**
- dòng text/key: **483,505** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 36 | 6,000 | 345 | 95 | 690 | 206 | -12.39…12.24 | -20.3…676.38 |
| `Board_Shop` | 28 | 3,898 | 204 | 51 | 336 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 34 | 3,005 | 207 | 72 | 329 | 162 | -5.45…16.09 | -60.21…8.9 |
| `Board_SelectBoss` | 29 | 2,692 | 6 | 2 | 34 | 234 | -17.24…11.76 | -9.6…204.29 |
| `Board_FightBoss` | 29 | 2,649 | 67 | 16 | 94 | 302 | -14.22…14.8 | -44.18…47.26 |
| `Board_Arena` | 31 | 2,088 | 170 | 65 | 241 | 234 | -5.28…5.81 | -51.84…8.8 |
| `Tab_Boss` | 509 | 2,035 | 7 | 2 | 2 | 255 | -14.22…29.63 | -44.18…47.26 |
| `Board_BigShop` | 32 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 62 | 2,000 | 142 | 63 | 185 | 124 | None…None | None…None |
| `Board_ShopCoins` | 31 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 138 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 311 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 328 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 522 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 646 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 336 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 156 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 64 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 64 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 14623 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 60 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 31 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 317 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 84 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 31 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 62 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 68 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Button` | 193 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 65 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 25 | 1,895 | 44 | 17 | 139 | 87 | -7.23…5.13 | -94.51…8.19 |
| `Board_Players` | 33 | 1,876 | 119 | 31 | 160 | 140 | -7.65…13.35 | -9.6…14.69 |
| `Tab_BattlePass` | 885 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Popup_ArenaInfo` | 60 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 305 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 34 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 35 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 31 | 1,459 | 74 | 13 | 158 | 118 | -10.04…9.0 | -9.6…14.0 |
| `Board_Survival` | 64 | 1,455 | 143 | 59 | 176 | 121 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 68 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Begin` | 69 | 1,101 | 61 | 17 | 104 | 115 | -5.22…4.51 | -17.6…11.46 |
| `Board_Drones` | 30 | 1,100 | 94 | 21 | 124 | 140 | -6.27…4.75 | -9.6…7.5 |
| `Board_BattlePassPro` | 30 | 1,039 | 68 | 23 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_WinnerBenefits` | 30 | 1,034 | 80 | 21 | 106 | 100 | -4.86…4.55 | -7.37…7.94 |
| `Board_Reborn_IAP` | 91 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_Combo` | 30 | 1,008 | 45 | 25 | 119 | 92 | -12.41…7.92 | -50.29…8.25 |
| `Board_Talents` | 91 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Board_MiniCombo` | 24 | 983 | 45 | 25 | 117 | 87 | -12.41…7.92 | -50.29…8.25 |
| `Board_Setting` | 26 | 980 | 58 | 42 | 135 | 87 | -4.5…4.76 | -25.75…20.0 |
| `Tab_BattlePassMission` | 101 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 34 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Popup_BattlePassLevelUp` | 34 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_Endgame` | 29 | 931 | 90 | 38 | 102 | 126 | -5.83…5.21 | -9.6…9.6 |
| `Board_Reborn` | 28 | 917 | 89 | 28 | 120 | 117 | -5.24…4.55 | -9.6…9.35 |
| `Board_GiftLogin` | 34 | 908 | 63 | 23 | 57 | 87 | -4.96…5.0 | -9.48…8.15 |
| `Board_Challange` | 36 | 866 | 77 | 22 | 106 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 30 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 123 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 30 | 823 | 74 | 21 | 108 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 30 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 36 | 792 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 30 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Board_UserProfile` | 27 | 757 | 53 | 31 | 100 | 80 | -5.37…5.81 | -21.98…8.8 |
| `Popup_Community` | 26 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_ShipSalePack` | 34 | 744 | 16 | 7 | 14 | 85 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectBenefits` | 33 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_SelectShipCombo` | 98 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_QuestRewards` | 31 | 720 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Board_Profile` | 86 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Popup_ChangeLanguages` | 58 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Popup_SelectItemCombo` | 81 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 33 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 35 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 30 | 645 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 67 | 601 | 42 | 17 | 58 | 76 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 61 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_Rename` | 30 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_WeekSales` | 28 | 494 | 24 | 13 | 25 | 55 | None…None | None…None |
| `Popup_ChangeAvatar` | 33 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 64 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 33 | 384 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 27 | 374 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 28 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_VideoCards` | 31 | 328 | 38 | 12 | 34 | 76 | -4.86…4.55 | -8.05…9.1 |
| `Popup_EventLevelUp` | 72 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 28 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 33 | 319 | 17 | 5 | 14 | 51 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 31 | 314 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_FirstPurchase` | 32 | 304 | 12 | 6 | 8 | 60 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 191 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 33 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 27 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 27 | 212 | 33 | 25 | 26 | 49 | -5.24…4.49 | -9.6…9.6 |
| `Board_BlackBox` | 28 | 185 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 28 | 174 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 58 | 162 | 6 | 1 | 2 | 35 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 35 | 135 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 30 | 132 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 101 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 29 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 34 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 66 | 87 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 29 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 25 | 61 | 7 | 1 | 4 | 20 | -3.96…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 31 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 32 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 32 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 32 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 30 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 29 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 31 | 19 | 4 | 4 | 6 | 5 | None…None | None…None |
| `Popup_Update` | 28 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 30 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 34 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 35 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

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
| `Popup_Notices` | 113437 | 32252 | 28% |
| `Popup_BuyMoreGems` | 37557 | 3680 | 10% |
| `Popup_BuyMoreCoins` | 18706 | 4158 | 22% |
| `Board_Maps` | 17419 | 3480 | 20% |
| `Board_Shop` | 16883 | 2606 | 15% |
| `Board_Ranks` | 15645 | 3930 | 25% |
| `Board_Survival` | 14613 | 3611 | 25% |
| `Board_PVP` | 14377 | 2921 | 20% |
| `Popup_Profile` | 14185 | 4395 | 31% |
| `Popup_WatchVideos` | 11876 | 2142 | 18% |
| `Popup_PremiumDailyRewards` | 10341 | 980 | 9% |
| `Board_Arena` | 9226 | 2010 | 22% |
| `Tab_BattlePass` | 7630 | 1302 | 17% |
| `Board_Players` | 7309 | 1375 | 19% |
| `Board_BattlePass` | 6991 | 1101 | 16% |
| `Board_EventSeasonPass` | 6275 | 1272 | 20% |
| `Board_Begin` | 5954 | 850 | 14% |
| `Board_Reborn_IAP` | 5552 | 527 | 9% |
| `Popup_BuyItem` | 5396 | 1446 | 27% |
| `Board_Challange` | 5367 | 959 | 18% |
| `Board_TechLab` | 4955 | 632 | 13% |
| `Popup_ChooseVersionDatas` | 4919 | 1058 | 22% |
| `Board_WinnerBenefits` | 4820 | 991 | 21% |
| `Popup_HolidayGift` | 4653 | 600 | 13% |
| `Board_GiftLogin` | 4595 | 736 | 16% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
