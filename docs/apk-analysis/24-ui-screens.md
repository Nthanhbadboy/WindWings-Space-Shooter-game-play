# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **17840**, màn (class): **114**, node: **2,993,403**
- dòng text/key: **351,345** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 28 | 6,000 | 344 | 94 | 689 | 206 | -12.39…12.24 | -20.3…676.38 |
| `Board_Shop` | 20 | 3,898 | 204 | 51 | 336 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 26 | 3,005 | 207 | 72 | 329 | 162 | -5.45…16.09 | -60.21…8.9 |
| `Board_SelectBoss` | 21 | 2,692 | 6 | 2 | 34 | 234 | -17.24…11.76 | -9.6…204.29 |
| `Board_FightBoss` | 21 | 2,649 | 67 | 16 | 94 | 302 | -14.22…14.8 | -44.18…47.26 |
| `Board_Arena` | 23 | 2,088 | 170 | 65 | 241 | 234 | -5.28…5.81 | -51.84…8.8 |
| `Tab_Boss` | 374 | 2,035 | 7 | 2 | 2 | 255 | -14.22…29.63 | -44.18…47.26 |
| `Board_BigShop` | 24 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 46 | 2,000 | 142 | 63 | 185 | 124 | None…None | None…None |
| `Board_ShopCoins` | 23 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 106 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 231 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 241 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 386 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 486 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 248 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 116 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 48 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 48 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 11100 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 44 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 23 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 237 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 60 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 23 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 46 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 52 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Button` | 145 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 49 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 17 | 1,886 | 44 | 17 | 139 | 87 | -7.23…5.13 | -94.51…8.19 |
| `Tab_BattlePass` | 647 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Board_Players` | 25 | 1,826 | 119 | 31 | 160 | 140 | -7.65…13.35 | -9.6…14.69 |
| `Popup_ArenaInfo` | 44 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 225 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 26 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 27 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 23 | 1,459 | 74 | 13 | 158 | 118 | -10.04…9.0 | -9.6…14.0 |
| `Board_Survival` | 48 | 1,455 | 143 | 59 | 176 | 119 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 52 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Begin` | 53 | 1,101 | 61 | 17 | 104 | 115 | -5.22…4.51 | -17.6…11.46 |
| `Board_Drones` | 22 | 1,093 | 94 | 21 | 124 | 136 | -5.62…4.75 | -9.6…7.5 |
| `Board_BattlePassPro` | 22 | 1,039 | 68 | 23 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_WinnerBenefits` | 22 | 1,026 | 80 | 21 | 106 | 100 | -4.86…5.0 | -7.37…7.94 |
| `Board_Reborn_IAP` | 67 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_Combo` | 22 | 1,005 | 45 | 25 | 119 | 92 | -12.41…8.48 | -50.29…8.25 |
| `Board_Talents` | 67 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Board_MiniCombo` | 16 | 983 | 45 | 25 | 117 | 87 | -12.41…7.92 | -50.29…8.25 |
| `Tab_BattlePassMission` | 77 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 26 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_Setting` | 18 | 952 | 58 | 42 | 135 | 87 | -4.5…4.76 | -25.75…20.0 |
| `Popup_BattlePassLevelUp` | 26 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_Endgame` | 21 | 926 | 88 | 37 | 102 | 124 | -6.84…5.21 | -9.6…9.6 |
| `Board_Reborn` | 20 | 913 | 89 | 28 | 120 | 117 | -6.12…4.55 | -9.6…9.35 |
| `Board_GiftLogin` | 26 | 908 | 63 | 23 | 57 | 86 | -4.96…5.0 | -9.48…8.15 |
| `Board_Challange` | 28 | 866 | 77 | 22 | 106 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 22 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 91 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 22 | 823 | 74 | 21 | 108 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 22 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 28 | 792 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 22 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Popup_Community` | 18 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_ShipSalePack` | 26 | 744 | 16 | 7 | 14 | 85 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectBenefits` | 25 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Board_UserProfile` | 19 | 724 | 53 | 31 | 100 | 80 | -5.37…5.81 | -21.98…8.8 |
| `Popup_SelectShipCombo` | 74 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 62 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Board_QuestRewards` | 23 | 715 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Popup_ChangeLanguages` | 42 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Popup_SelectItemCombo` | 57 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 25 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 27 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 22 | 645 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 51 | 601 | 42 | 17 | 58 | 76 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 45 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_Rename` | 22 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_WeekSales` | 20 | 494 | 24 | 13 | 25 | 55 | None…None | None…None |
| `Popup_ChangeAvatar` | 25 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 48 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 25 | 384 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 19 | 352 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 20 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_EventLevelUp` | 56 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 20 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 25 | 319 | 17 | 5 | 14 | 51 | -4.5…7.2 | -7.26…7.42 |
| `Board_Items` | 23 | 314 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_VideoCards` | 23 | 313 | 38 | 12 | 34 | 74 | -4.86…4.55 | -8.05…9.1 |
| `Popup_FirstPurchase` | 24 | 304 | 12 | 6 | 8 | 59 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 143 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 25 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 19 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 19 | 212 | 33 | 25 | 26 | 49 | -5.24…4.49 | -9.6…9.6 |
| `Board_BlackBox` | 20 | 185 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 20 | 174 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 42 | 162 | 6 | 1 | 2 | 35 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 27 | 134 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 22 | 128 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 77 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 21 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 26 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 50 | 87 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 21 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 17 | 61 | 7 | 1 | 4 | 20 | -3.89…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 23 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 24 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 24 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 24 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 22 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 21 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 23 | 19 | 4 | 4 | 6 | 5 | None…None | None…None |
| `Popup_Update` | 20 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 22 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 26 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 27 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

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
| `Popup_Notices` | 84078 | 23854 | 28% |
| `Popup_BuyMoreGems` | 27342 | 2658 | 10% |
| `Popup_BuyMoreCoins` | 13481 | 2975 | 22% |
| `Board_Maps` | 13243 | 2646 | 20% |
| `Board_Shop` | 11715 | 1810 | 15% |
| `Board_Ranks` | 11224 | 2815 | 25% |
| `Board_Survival` | 10657 | 2634 | 25% |
| `Board_PVP` | 10568 | 2140 | 20% |
| `Popup_Profile` | 10532 | 3256 | 31% |
| `Popup_WatchVideos` | 8731 | 1582 | 18% |
| `Popup_PremiumDailyRewards` | 7414 | 704 | 9% |
| `Board_Arena` | 6836 | 1482 | 22% |
| `Board_Players` | 5444 | 1026 | 19% |
| `Tab_BattlePass` | 5439 | 930 | 17% |
| `Board_BattlePass` | 4776 | 753 | 16% |
| `Board_EventSeasonPass` | 4667 | 944 | 20% |
| `Board_Begin` | 4406 | 626 | 14% |
| `Board_Challange` | 4036 | 718 | 18% |
| `Board_Reborn_IAP` | 3958 | 377 | 10% |
| `Popup_BuyItem` | 3815 | 1018 | 27% |
| `Board_TechLab` | 3656 | 458 | 13% |
| `Popup_ChooseVersionDatas` | 3534 | 759 | 21% |
| `Board_WinnerBenefits` | 3422 | 685 | 20% |
| `Board_GiftLogin` | 3410 | 548 | 16% |
| `Board_Stage` | 3341 | 586 | 18% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
