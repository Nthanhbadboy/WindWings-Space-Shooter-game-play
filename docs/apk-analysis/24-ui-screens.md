# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **35452**, màn (class): **114**, node: **5,522,688**
- dòng text/key: **747,431** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 52 | 6,000 | 345 | 95 | 690 | 206 | -12.39…12.24 | -20.3…676.38 |
| `Board_Shop` | 44 | 3,898 | 204 | 51 | 346 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 50 | 3,005 | 207 | 72 | 329 | 162 | -5.45…16.09 | -60.21…8.9 |
| `Board_SelectBoss` | 45 | 2,692 | 6 | 2 | 34 | 234 | -17.24…11.76 | -9.6…204.29 |
| `Board_FightBoss` | 45 | 2,649 | 67 | 16 | 94 | 303 | -14.22…14.8 | -44.18…47.26 |
| `Board_Arena` | 47 | 2,104 | 170 | 65 | 241 | 234 | -5.37…5.81 | -51.84…8.8 |
| `Tab_Boss` | 779 | 2,035 | 7 | 2 | 2 | 255 | -14.22…29.63 | -44.18…47.26 |
| `Board_BigShop` | 48 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 94 | 2,000 | 142 | 63 | 185 | 124 | None…None | None…None |
| `Board_ShopCoins` | 47 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 202 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 471 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 503 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 793 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 965 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 511 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 236 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 96 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 96 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 21673 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 92 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 47 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 477 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 132 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 47 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 94 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 100 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Button` | 289 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 97 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 41 | 1,940 | 44 | 17 | 141 | 88 | -7.23…5.13 | -94.51…8.19 |
| `Board_Players` | 49 | 1,915 | 119 | 31 | 160 | 140 | -7.65…13.35 | -9.6…14.69 |
| `Tab_BattlePass` | 1360 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Popup_ArenaInfo` | 92 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 464 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 50 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 51 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 47 | 1,503 | 74 | 13 | 158 | 118 | -10.04…9.42 | -9.6…14.0 |
| `Board_Survival` | 96 | 1,455 | 143 | 59 | 176 | 121 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 100 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Begin` | 101 | 1,101 | 61 | 17 | 108 | 117 | -5.22…4.51 | -17.6…11.46 |
| `Board_Drones` | 46 | 1,100 | 94 | 21 | 124 | 140 | -6.27…4.75 | -9.6…7.5 |
| `Board_BattlePassPro` | 46 | 1,067 | 68 | 23 | 87 | 107 | -5.42…12.58 | -22.6…10.16 |
| `Board_WinnerBenefits` | 46 | 1,065 | 80 | 21 | 106 | 100 | -4.86…5.0 | -7.37…7.94 |
| `Board_Combo` | 46 | 1,037 | 45 | 25 | 125 | 94 | -12.41…7.92 | -50.29…8.25 |
| `Board_Reborn_IAP` | 139 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_Talents` | 139 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Board_MiniCombo` | 40 | 983 | 45 | 25 | 117 | 93 | -12.41…7.92 | -50.29…8.25 |
| `Board_Setting` | 42 | 980 | 58 | 42 | 135 | 87 | -4.5…4.76 | -25.75…20.0 |
| `Tab_BattlePassMission` | 149 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 50 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_GiftLogin` | 50 | 955 | 63 | 23 | 57 | 87 | -4.96…5.12 | -9.48…8.15 |
| `Popup_BattlePassLevelUp` | 50 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_Endgame` | 45 | 931 | 90 | 38 | 102 | 126 | -5.83…5.21 | -9.6…9.6 |
| `Board_Reborn` | 44 | 917 | 89 | 28 | 120 | 117 | -5.24…4.55 | -9.6…9.35 |
| `Board_Challange` | 52 | 866 | 77 | 22 | 106 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 46 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 187 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 46 | 823 | 74 | 21 | 108 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 46 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 52 | 799 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 46 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Board_UserProfile` | 43 | 757 | 53 | 31 | 100 | 82 | -5.37…5.81 | -21.98…8.8 |
| `Popup_Community` | 42 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_ShipSalePack` | 50 | 744 | 16 | 7 | 14 | 85 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectBenefits` | 49 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Board_QuestRewards` | 47 | 729 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Popup_SelectShipCombo` | 146 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 134 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Popup_ChangeLanguages` | 90 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Popup_SelectItemCombo` | 129 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 49 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 51 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 46 | 645 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 99 | 601 | 42 | 17 | 58 | 77 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 93 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_WeekSales` | 44 | 496 | 24 | 13 | 25 | 55 | -5.95…4.76 | -7.0…8.0 |
| `Popup_Rename` | 46 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_ChangeAvatar` | 49 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 96 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 49 | 384 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 43 | 374 | 26 | 12 | 34 | 58 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 44 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_VideoCards` | 47 | 328 | 38 | 12 | 34 | 76 | -4.86…4.55 | -8.05…9.1 |
| `Popup_EventLevelUp` | 104 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 44 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 49 | 319 | 17 | 5 | 14 | 53 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 47 | 314 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_FirstPurchase` | 48 | 304 | 12 | 6 | 8 | 60 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 286 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 49 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 43 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 43 | 212 | 33 | 25 | 26 | 49 | -5.24…4.49 | -9.6…9.6 |
| `Board_BlackBox` | 44 | 185 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 44 | 175 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 90 | 163 | 6 | 1 | 2 | 36 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 51 | 135 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 46 | 134 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 149 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 45 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 50 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 98 | 87 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 45 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 41 | 61 | 7 | 1 | 4 | 20 | -3.96…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 47 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 48 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 48 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 48 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 46 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 45 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 47 | 19 | 4 | 4 | 6 | 5 | -2.5…3.7 | -1.8…3.1 |
| `Popup_Update` | 44 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 46 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 50 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 51 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

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
| `Popup_Notices` | 172540 | 49018 | 28% |
| `Popup_BuyMoreGems` | 57536 | 5677 | 10% |
| `Popup_BuyMoreCoins` | 29158 | 6494 | 22% |
| `Board_Shop` | 27352 | 4244 | 16% |
| `Board_Maps` | 26057 | 5167 | 20% |
| `Board_Ranks` | 24401 | 6137 | 25% |
| `Board_Survival` | 22483 | 5537 | 25% |
| `Board_PVP` | 21938 | 4452 | 20% |
| `Popup_Profile` | 21624 | 6709 | 31% |
| `Popup_WatchVideos` | 17880 | 3179 | 18% |
| `Popup_PremiumDailyRewards` | 16202 | 1536 | 9% |
| `Board_Arena` | 14229 | 3051 | 21% |
| `Tab_BattlePass` | 11958 | 2033 | 17% |
| `Board_BattlePass` | 11580 | 1845 | 16% |
| `Board_Players` | 11042 | 2079 | 19% |
| `Board_EventSeasonPass` | 9472 | 1923 | 20% |
| `Board_Begin` | 9013 | 1288 | 14% |
| `Board_Reborn_IAP` | 8688 | 809 | 9% |
| `Popup_BuyItem` | 8549 | 2292 | 27% |
| `Board_Challange` | 7931 | 1402 | 18% |
| `Board_TechLab` | 7761 | 998 | 13% |
| `Popup_ChooseVersionDatas` | 7727 | 1657 | 21% |
| `Board_WinnerBenefits` | 7695 | 1580 | 21% |
| `Board_Reborn` | 7463 | 1554 | 21% |
| `Popup_HolidayGift` | 7253 | 942 | 13% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
