# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **55584**, màn (class): **117**, node: **8,435,335**
- dòng text/key: **1,205,512** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 80 | 10,315 | 345 | 95 | 704 | 218 | -12.39…12.24 | -22.6…676.38 |
| `Board_Shop` | 72 | 4,876 | 204 | 51 | 358 | 156 | -6.46…9.13 | -18.99…36.98 |
| `Board_SelectBoss` | 73 | 3,837 | 6 | 2 | 34 | 262 | -17.26…26.59 | -9.6…204.29 |
| `Board_PVP` | 78 | 3,789 | 207 | 72 | 341 | 164 | -7.15…16.09 | -60.21…8.9 |
| `Board_FightBoss` | 73 | 3,484 | 67 | 16 | 94 | 315 | -14.22…29.63 | -44.74…47.26 |
| `Tab_Boss` | 1246 | 2,649 | 7 | 2 | 2 | 255 | -14.22…29.63 | -44.74…47.26 |
| `Board_Arena` | 74 | 2,606 | 170 | 65 | 247 | 242 | -5.37…5.81 | -51.84…8.8 |
| `Board_BattlePass` | 68 | 2,469 | 44 | 17 | 159 | 88 | -7.23…5.13 | -94.51…8.19 |
| `Board_Players` | 76 | 2,276 | 119 | 31 | 160 | 142 | -11.2…16.9 | -9.6…14.69 |
| `Board_BigShop` | 76 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 149 | 2,000 | 142 | 63 | 187 | 128 | None…None | None…None |
| `Board_ShopCoins` | 75 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 313 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 747 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 805 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 1256 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 1513 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 812 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 373 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 151 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 151 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 33750 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 146 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 74 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 752 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 215 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 75 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 149 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 156 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Button` | 455 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 152 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_Survival` | 152 | 1,865 | 143 | 59 | 177 | 125 | -5.37…5.81 | -21.98…8.8 |
| `Tab_BattlePass` | 2168 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Board_TechLab` | 74 | 1,838 | 74 | 13 | 164 | 120 | -10.04…9.42 | -9.6…14.0 |
| `Popup_ArenaInfo` | 147 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 735 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 78 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 79 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_Drones` | 73 | 1,327 | 94 | 21 | 124 | 143 | -6.27…4.75 | -9.6…7.5 |
| `Board_Combo` | 73 | 1,306 | 45 | 25 | 131 | 95 | -12.41…8.48 | -50.29…8.25 |
| `Board_MiniCombo` | 67 | 1,306 | 45 | 25 | 131 | 95 | -12.41…8.48 | -50.29…8.25 |
| `Board_Begin` | 156 | 1,284 | 61 | 17 | 110 | 121 | -5.22…4.55 | -17.6…11.46 |
| `Board_WinnerBenefits` | 74 | 1,252 | 80 | 21 | 106 | 101 | -4.86…5.0 | -7.37…7.94 |
| `Board_BattlePassPro` | 73 | 1,200 | 68 | 23 | 87 | 112 | -5.42…12.58 | -22.6…10.16 |
| `Popup_DroneCraft` | 155 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Reborn` | 72 | 1,101 | 89 | 28 | 120 | 121 | -6.12…4.55 | -9.6…9.35 |
| `Board_Setting` | 69 | 1,074 | 58 | 42 | 135 | 90 | -4.5…4.76 | -25.75…20.0 |
| `Board_Endgame` | 73 | 1,070 | 90 | 38 | 102 | 133 | -6.84…5.21 | -9.6…10.04 |
| `Board_Reborn_IAP` | 221 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_GiftLogin` | 77 | 1,019 | 63 | 23 | 57 | 87 | -4.96…5.12 | -9.48…8.15 |
| `Board_Challange` | 80 | 995 | 77 | 22 | 106 | 108 | -5.23…10.2 | -9.6…7.25 |
| `Board_Stage` | 74 | 995 | 74 | 21 | 108 | 109 | -5.1…5.1 | -9.6…7.7 |
| `Board_Talents` | 222 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Tab_BattlePassMission` | 232 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 78 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Popup_BattlePassLevelUp` | 77 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_Vip` | 80 | 918 | 53 | 11 | 54 | 84 | -5.96…5.21 | -8.32…8.78 |
| `Popup_ShipSalePack` | 78 | 895 | 16 | 7 | 14 | 86 | -16.8…11.3 | -5.92…8.5 |
| `Board_UserProfile` | 70 | 893 | 53 | 31 | 100 | 82 | -5.37…5.81 | -21.98…8.8 |
| `Popup_LuckyStar` | 73 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 296 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Popup_BuySpeed` | 73 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_QuestRewards` | 74 | 813 | 50 | 11 | 54 | 78 | -4.5…4.76 | -7.69…7.5 |
| `Popup_About` | 73 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Board_ShopEnergy` | 73 | 755 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Popup_Community` | 69 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_SelectBenefits` | 76 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_SelectShipCombo` | 229 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 215 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Popup_ChangeLanguages` | 145 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Popup_SelectItemCombo` | 210 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 77 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 79 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_EventSeasonPass` | 155 | 659 | 42 | 17 | 58 | 81 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 147 | 609 | 31 | 10 | 19 | 71 | -4.82…4.76 | -7.0…8.0 |
| `Popup_WeekSales` | 71 | 532 | 24 | 13 | 25 | 55 | -5.95…4.76 | -7.0…8.0 |
| `Popup_Rename` | 73 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_ChangeAvatar` | 76 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 150 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_AccountSettings` | 70 | 428 | 26 | 12 | 34 | 58 | -3.99…4.14 | -4.65…5.4 |
| `Board_Quest` | 77 | 425 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Popup_VideoCards` | 74 | 365 | 38 | 12 | 34 | 77 | -4.86…4.55 | -8.05…9.1 |
| `Popup_UpgradeTechIAP` | 76 | 336 | 17 | 5 | 14 | 54 | -5.89…7.2 | -7.26…7.42 |
| `Board_Items` | 75 | 335 | 8 | 1 | 68 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Board_ShopGems` | 72 | 332 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Board_LinkAccount` | 71 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_EventLevelUp` | 160 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Popup_FirstPurchase` | 76 | 312 | 12 | 6 | 8 | 60 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 454 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 76 | 277 | 17 | 11 | 36 | 50 | -4.45…8.93 | -7.9…8.15 |
| `Board_Pause` | 70 | 235 | 33 | 25 | 26 | 51 | -5.24…4.55 | -9.6…9.6 |
| `Board_Devices` | 70 | 233 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_BlackBox` | 71 | 197 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 71 | 175 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 144 | 171 | 6 | 1 | 2 | 36 | -0.91…0.91 | -5.0…5.18 |
| `Board_SellDevices` | 73 | 144 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Board_RoomPVP` | 79 | 137 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `GP_Tutorials` | 1 | 126 | 20 | 19 | 4 | 18 | -3.93…6.9 | -5.76…7.51 |
| `Popup_QuitEvent` | 231 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 73 | 97 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 77 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 154 | 89 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 72 | 70 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tut_Settings` | 1 | 64 | 10 | 9 | 2 | 13 | -1.16…6.9 | -5.76…1.69 |
| `Tab_BattlePassPro` | 68 | 62 | 7 | 1 | 4 | 20 | -3.96…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 74 | 61 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 75 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 76 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 76 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 73 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Tut_Settings1` | 2 | 30 | 8 | 6 | 2 | 8 | 0.0…2.54 | 0.0…7.51 |
| `Popup_ConfirmRate` | 72 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 74 | 19 | 4 | 4 | 6 | 5 | -2.5…3.7 | -1.8…3.1 |
| `Popup_Update` | 71 | 19 | 4 | 3 | 4 | 6 | -3.63…2.25 | -2.0…3.4 |
| `Popup_InrerestExpired` | 73 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 77 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 79 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

## Hệ toạ độ (suy ra từ bbox, mức C)

- bề rộng bbox phổ biến: `[0.0, 1.8, 2.5] … [24.6, 28.1, 43.9]`
- chiều cao bbox phổ biến: `[0.0, 1.9, 3.2] … [102.7, 213.9, 699.0]`
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
| `Popup_Notices` | 275442 | 78069 | 28% |
| `Popup_BuyMoreGems` | 92310 | 9109 | 10% |
| `Popup_BuyMoreCoins` | 47060 | 10488 | 22% |
| `Board_Shop` | 45890 | 7095 | 15% |
| `Board_Maps` | 40762 | 8216 | 20% |
| `Board_Ranks` | 39446 | 9925 | 25% |
| `Board_Survival` | 36675 | 9013 | 25% |
| `Board_PVP` | 35608 | 7189 | 20% |
| `Popup_Profile` | 35145 | 10878 | 31% |
| `Popup_WatchVideos` | 28297 | 5072 | 18% |
| `Popup_PremiumDailyRewards` | 26177 | 2481 | 9% |
| `Board_Arena` | 22851 | 4866 | 21% |
| `Board_BattlePass` | 19219 | 3077 | 16% |
| `Tab_BattlePass` | 19216 | 3236 | 17% |
| `Board_Players` | 17314 | 3276 | 19% |
| `Board_EventSeasonPass` | 15097 | 3060 | 20% |
| `Board_Begin` | 14398 | 2057 | 14% |
| `Board_Reborn_IAP` | 14222 | 1309 | 9% |
| `Popup_BuyItem` | 13964 | 3747 | 27% |
| `Board_WinnerBenefits` | 12641 | 2599 | 21% |
| `Board_TechLab` | 12573 | 1617 | 13% |
| `Board_Challange` | 12556 | 2212 | 18% |
| `Board_Reborn` | 12531 | 2609 | 21% |
| `Popup_ChooseVersionDatas` | 12470 | 2665 | 21% |
| `Popup_PvPRankings` | 12215 | 3635 | 30% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
