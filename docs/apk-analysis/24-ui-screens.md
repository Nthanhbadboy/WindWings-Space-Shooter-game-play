# 24 — Danh mục layout UI (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ **mọi** file trong `reverse-engineering/raw/ui/`,
> gồm cả file của các lần chạy trước. `_index.csv` chỉ có 630 file của lần chạy mới nhất →
> **16 màn bị thiếu trong báo cáo 20**, bảng dưới đây bù lại.

Đây là layout **trong prefab**. Runtime (layout group, safe area, code đặt vị trí) có thể
khác — chưa đối chiếu screenshot.

- file: **8990**, màn (class): **114**, node: **1,744,847**
- dòng text/key: **156,630** (CSV.gz: `datas/ui_text_keys.csv.gz`)

## Theo màn

| màn | file | node (max) | text | key | button | sprite | bbox x | bbox y |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `Board_Maps` | 15 | 6,000 | 338 | 91 | 689 | 198 | -12.39…12.24 | -22.6…676.38 |
| `Board_Shop` | 10 | 3,898 | 204 | 51 | 332 | 149 | -6.46…5.0 | -17.22…36.98 |
| `Board_PVP` | 14 | 3,005 | 207 | 72 | 327 | 161 | -5.45…16.09 | -60.21…8.9 |
| `Board_FightBoss` | 9 | 2,649 | 67 | 16 | 94 | 294 | -14.22…14.8 | -44.18…47.26 |
| `Board_SelectBoss` | 10 | 2,621 | 6 | 2 | 34 | 221 | -17.24…11.76 | -9.6…204.29 |
| `Board_Arena` | 11 | 2,049 | 170 | 65 | 240 | 229 | -5.28…5.81 | -51.84…8.8 |
| `Board_BigShop` | 13 | 2,000 | 29 | 0 | 26 | 85 | None…None | None…None |
| `Board_Ranks` | 22 | 2,000 | 142 | 63 | 183 | 122 | None…None | None…None |
| `Board_ShopCoins` | 12 | 2,000 | 26 | 2 | 18 | 91 | None…None | None…None |
| `Popup_AbilityEvent1` | 56 | 2,000 | 7 | 5 | 10 | 114 | None…None | None…None |
| `Popup_Ban` | 111 | 2,000 | 4 | 4 | 6 | 231 | None…None | None…None |
| `Popup_BuyItem` | 116 | 2,000 | 11 | 5 | 16 | 208 | None…None | None…None |
| `Popup_BuyMoreCoins` | 191 | 2,000 | 23 | 7 | 20 | 258 | None…None | None…None |
| `Popup_BuyMoreGems` | 247 | 2,000 | 36 | 6 | 30 | 257 | None…None | None…None |
| `Popup_ChooseVersionDatas` | 117 | 2,000 | 7 | 4 | 6 | 212 | None…None | None…None |
| `Popup_CrossLinks` | 56 | 2,000 | 1 | 1 | 1 | 106 | None…None | None…None |
| `Popup_Fotification` | 24 | 2,000 | 19 | 10 | 22 | 85 | None…None | None…None |
| `Popup_JoinRank` | 23 | 2,000 | 5 | 3 | 6 | 114 | None…None | None…None |
| `Popup_Notices` | 5687 | 2,000 | 189 | 80 | 30 | 257 | None…None | None…None |
| `Popup_PVPRewards` | 22 | 2,000 | 6 | 3 | 4 | 122 | None…None | None…None |
| `Popup_PVPShopExchange` | 10 | 2,000 | 6 | 0 | 8 | 125 | None…None | None…None |
| `Popup_Profile` | 116 | 2,000 | 36 | 19 | 28 | 214 | None…None | None…None |
| `Popup_PvPRankings` | 27 | 2,000 | 44 | 24 | 36 | 119 | None…None | None…None |
| `Popup_SeasonRewards` | 12 | 2,000 | 4 | 1 | 2 | 125 | None…None | None…None |
| `Popup_WatchVideosOld` | 23 | 2,000 | 15 | 9 | 23 | 85 | None…None | None…None |
| `Popup_WatchVideos` | 26 | 2,000 | 78 | 26 | 93 | 88 | None…None | None…None |
| `Tab_Boss` | 175 | 2,000 | 7 | 2 | 2 | 255 | None…None | None…None |
| `Tab_Button` | 72 | 2,000 | 7 | 6 | 3 | 92 | None…None | None…None |
| `Tab_Manager` | 26 | 2,000 | 7 | 6 | 14 | 87 | None…None | None…None |
| `Board_BattlePass` | 7 | 1,886 | 44 | 17 | 137 | 86 | -7.23…5.13 | -94.51…8.19 |
| `Tab_BattlePass` | 315 | 1,865 | 7 | 1 | 4 | 87 | None…None | None…None |
| `Board_Players` | 13 | 1,823 | 119 | 31 | 160 | 140 | -11.2…13.35 | -9.6…14.25 |
| `Popup_ArenaInfo` | 21 | 1,786 | 7 | 2 | 12 | 223 | None…None | None…None |
| `Popup_PremiumDailyRewards` | 105 | 1,689 | 20 | 6 | 8 | 84 | None…None | None…None |
| `Popup_InfoDevices` | 13 | 1,603 | 4 | 2 | 4 | 119 | None…None | None…None |
| `Popup_ArenaShopExchange` | 15 | 1,554 | 6 | 0 | 8 | 202 | None…None | None…None |
| `Board_TechLab` | 12 | 1,459 | 74 | 13 | 154 | 118 | -10.04…9.0 | -9.6…14.0 |
| `Board_Survival` | 24 | 1,375 | 143 | 59 | 173 | 118 | -5.37…5.81 | -21.98…8.8 |
| `Popup_DroneCraft` | 27 | 1,129 | 16 | 2 | 8 | 121 | None…None | None…None |
| `Board_Drones` | 9 | 1,093 | 94 | 21 | 124 | 134 | -5.62…4.75 | -9.6…7.5 |
| `Board_Begin` | 28 | 1,073 | 61 | 17 | 104 | 115 | -5.22…4.55 | -17.6…11.46 |
| `Board_Reborn_IAP` | 36 | 1,025 | 30 | 7 | 30 | 115 | None…None | None…None |
| `Board_WinnerBenefits` | 10 | 1,022 | 80 | 21 | 104 | 100 | -4.86…5.0 | -7.37…7.94 |
| `Board_Combo` | 10 | 991 | 45 | 25 | 119 | 88 | -12.41…7.92 | -49.65…8.25 |
| `Board_BattlePassPro` | 11 | 988 | 65 | 22 | 87 | 103 | -5.39…5.38 | -22.6…9.68 |
| `Board_Talents` | 32 | 984 | 4 | 0 | 20 | 104 | None…None | None…None |
| `Tab_BattlePassMission` | 41 | 979 | 12 | 2 | 8 | 99 | None…None | None…None |
| `Popup_ChangeMissions` | 13 | 962 | 3 | 2 | 4 | 106 | None…None | None…None |
| `Board_Setting` | 8 | 952 | 58 | 42 | 129 | 85 | -4.5…4.76 | -25.75…20.0 |
| `Popup_BattlePassLevelUp` | 14 | 952 | 3 | 1 | 2 | 97 | None…None | None…None |
| `Board_MiniCombo` | 7 | 925 | 45 | 25 | 105 | 85 | -5.62…5.61 | -44.41…8.25 |
| `Board_Reborn` | 10 | 913 | 89 | 28 | 120 | 117 | -6.12…4.55 | -9.6…9.35 |
| `Board_GiftLogin` | 15 | 908 | 63 | 23 | 57 | 86 | -4.96…5.0 | -9.48…8.15 |
| `Board_Endgame` | 9 | 889 | 88 | 37 | 99 | 122 | -5.83…5.21 | -9.6…9.6 |
| `Board_Challange` | 15 | 866 | 77 | 22 | 104 | 106 | -5.23…10.2 | -9.6…7.25 |
| `Popup_LuckyStar` | 10 | 848 | 10 | 0 | 8 | 112 | None…None | None…None |
| `Popup_TryShip` | 44 | 835 | 8 | 3 | 2 | 83 | None…None | None…None |
| `Board_Stage` | 10 | 823 | 74 | 21 | 106 | 106 | -5.1…5.1 | -9.6…7.7 |
| `Popup_BuySpeed` | 11 | 816 | 12 | 4 | 5 | 79 | None…None | None…None |
| `Board_Vip` | 15 | 789 | 53 | 11 | 54 | 83 | -5.96…5.21 | -8.32…8.78 |
| `Popup_About` | 10 | 766 | 1 | 1 | 2 | 80 | None…None | None…None |
| `Popup_Community` | 9 | 745 | 4 | 4 | 6 | 81 | None…None | None…None |
| `Popup_SelectBenefits` | 13 | 740 | 7 | 2 | 11 | 86 | None…None | None…None |
| `Popup_ShipSalePack` | 13 | 728 | 16 | 7 | 14 | 84 | -13.25…7.75 | -5.92…8.5 |
| `Popup_SelectShipCombo` | 40 | 724 | 8 | 6 | 10 | 82 | None…None | None…None |
| `Board_Profile` | 27 | 716 | 25 | 17 | 32 | 82 | None…None | None…None |
| `Board_QuestRewards` | 12 | 715 | 50 | 11 | 54 | 77 | -4.5…4.76 | -7.69…7.5 |
| `Popup_ChangeLanguages` | 21 | 714 | 3 | 2 | 42 | 76 | None…None | None…None |
| `Board_UserProfile` | 7 | 712 | 53 | 31 | 100 | 79 | -4.39…5.81 | -21.98…8.8 |
| `Popup_SelectItemCombo` | 21 | 704 | 14 | 8 | 20 | 77 | None…None | None…None |
| `Popup_GeneralSettings` | 13 | 696 | 9 | 9 | 10 | 71 | None…None | None…None |
| `Popup_BuyMoreChanceAbility` | 14 | 683 | 15 | 6 | 16 | 84 | None…None | None…None |
| `Board_ShopEnergy` | 11 | 622 | 64 | 18 | 66 | 80 | -4.86…4.33 | -7.37…7.94 |
| `Board_EventSeasonPass` | 25 | 587 | 42 | 17 | 58 | 76 | -6.22…5.34 | -22.6…8.71 |
| `Popup_HolidayGift` | 20 | 581 | 31 | 10 | 19 | 69 | -4.82…4.76 | -7.0…8.0 |
| `Popup_Rename` | 11 | 495 | 5 | 2 | 4 | 71 | None…None | None…None |
| `Popup_WeekSales` | 10 | 494 | 24 | 13 | 25 | 55 | None…None | None…None |
| `Popup_ChangeAvatar` | 14 | 459 | 2 | 2 | 52 | 62 | None…None | None…None |
| `Popup_Exchange` | 23 | 434 | 11 | 5 | 16 | 55 | None…None | None…None |
| `Board_Quest` | 12 | 376 | 26 | 12 | 78 | 23 | -4.58…3.98 | -9.48…8.02 |
| `Board_AccountSettings` | 9 | 330 | 26 | 12 | 34 | 57 | -3.99…4.14 | -4.65…5.4 |
| `Board_LinkAccount` | 10 | 329 | 6 | 0 | 8 | 58 | None…None | None…None |
| `Popup_EventLevelUp` | 30 | 323 | 3 | 2 | 0 | 55 | None…None | None…None |
| `Board_ShopGems` | 10 | 319 | 42 | 4 | 30 | 33 | -4.39…4.5 | -17.22…7.11 |
| `Popup_UpgradeTechIAP` | 12 | 319 | 17 | 5 | 14 | 51 | -4.5…7.2 | -7.26…7.42 |
| `Popup_VideoCards` | 10 | 313 | 38 | 12 | 34 | 71 | -4.86…4.55 | -8.05…9.1 |
| `Board_Items` | 10 | 300 | 8 | 1 | 64 | 22 | -4.67…5.22 | -15.1…7.45 |
| `Popup_FirstPurchase` | 12 | 300 | 12 | 6 | 8 | 58 | -4.5…4.76 | -7.0…8.0 |
| `Tab_Item` | 67 | 299 | 1 | 0 | 10 | 21 | None…None | None…None |
| `Board_Home` | 13 | 258 | 17 | 11 | 36 | 48 | -4.45…8.46 | -7.77…8.15 |
| `Board_Devices` | 7 | 215 | 35 | 17 | 62 | 32 | -5.0…5.0 | -9.6…10.0 |
| `Board_Pause` | 8 | 205 | 33 | 25 | 26 | 47 | None…None | None…None |
| `Board_BlackBox` | 9 | 182 | 20 | 12 | 48 | 31 | -4.76…4.26 | -9.6…10.0 |
| `Popup_FirstGiftFree` | 10 | 174 | 8 | 5 | 4 | 15 | -4.78…4.76 | -7.0…8.0 |
| `Popup_NewPlayer` | 20 | 162 | 6 | 1 | 2 | 34 | -0.91…0.91 | -5.0…5.18 |
| `Board_RoomPVP` | 14 | 134 | 3 | 0 | 2 | 10 | -10.34…10.34 | -8.75…5.52 |
| `Board_SellDevices` | 12 | 128 | 22 | 11 | 44 | 20 | -4.76…4.43 | -9.6…15.38 |
| `Popup_QuitEvent` | 42 | 106 | 7 | 5 | 6 | 24 | None…None | None…None |
| `Popup_CheatTime` | 10 | 95 | 15 | 10 | 24 | 13 | -2.2…4.11 | -3.86…5.2 |
| `Popup_Penalty` | 15 | 93 | 11 | 8 | 18 | 13 | None…None | None…None |
| `Popup_PVPContinue` | 24 | 86 | 11 | 6 | 18 | 19 | -3.85…4.42 | -5.5…6.1 |
| `Popup_BuyEnergy` | 11 | 68 | 10 | 4 | 8 | 15 | -3.87…4.33 | -3.25…4.5 |
| `Tab_BattlePassPro` | 8 | 61 | 7 | 1 | 4 | 20 | -3.89…4.17 | -0.91…1.0 |
| `Tab_LogIn` | 12 | 59 | 7 | 2 | 2 | 11 | -4.96…4.21 | -3.16…0.0 |
| `Popup_Rate` | 11 | 44 | 3 | 2 | 9 | 8 | -3.0…4.08 | -2.45…4.5 |
| `Popup_TrialExpried` | 11 | 32 | 6 | 2 | 4 | 10 | -0.04…4.41 | -5.0…5.97 |
| `Board_Chapters` | 13 | 30 | 4 | 1 | 6 | 8 | -4.15…4.59 | -9.6…5.94 |
| `Popup_PremiumExpired` | 11 | 30 | 8 | 4 | 6 | 6 | -1.8…4.26 | -2.85…5.45 |
| `Popup_ConfirmRate` | 10 | 26 | 5 | 5 | 8 | 7 | 0.0…4.08 | -3.0…5.5 |
| `Popup_QuitGame` | 12 | 19 | 4 | 4 | 6 | 5 | None…None | None…None |
| `Popup_Update` | 9 | 19 | 4 | 3 | 4 | 6 | None…None | None…None |
| `Popup_InrerestExpired` | 12 | 18 | 3 | 2 | 4 | 8 | -0.21…4.12 | -3.8…4.07 |
| `Popup_Support` | 13 | 18 | 3 | 3 | 4 | 6 | 0.0…4.08 | -2.27…4.5 |
| `Board_Cards` | 14 | 3 | 1 | 1 | 0 | 1 | 0.0…0.0 | 0.0…0.0 |

## Hệ toạ độ (suy ra từ bbox, mức C)

- bề rộng bbox phổ biến: `[0.0, 1.8, 4.1] … [24.5, 24.6, 29.0]`
- chiều cao bbox phổ biến: `[0.0, 1.9, 3.2] … [102.7, 213.9, 699.0]`
- toạ độ là **unit world-space của prefab**, không phải pixel màn hình;
  muốn ra pixel phải nhân với `orthographicSize` của camera runtime (chưa bóc được).
- vì vậy mọi con số ở đây dùng để **so sánh tỉ lệ giữa các màn**, không phải để đặt pixel.

## Text & localization key

| màn | dòng text | có key | % có key |
|---|---:|---:|---:|
| `Popup_Notices` | 38715 | 10951 | 28% |
| `Popup_BuyMoreGems` | 12336 | 1188 | 10% |
| `Board_Maps` | 6370 | 1257 | 20% |
| `Popup_BuyMoreCoins` | 5908 | 1300 | 22% |
| `Board_PVP` | 5176 | 1055 | 20% |
| `Board_Shop` | 5139 | 794 | 15% |
| `Board_Ranks` | 4706 | 1180 | 25% |
| `Board_Survival` | 4697 | 1160 | 25% |
| `Popup_Profile` | 4469 | 1391 | 31% |
| `Popup_WatchVideos` | 3947 | 699 | 18% |
| `Popup_PremiumDailyRewards` | 3012 | 288 | 10% |
| `Board_Arena` | 2961 | 670 | 23% |
| `Board_Players` | 2712 | 513 | 19% |
| `Tab_BattlePass` | 2397 | 418 | 17% |
| `Board_Begin` | 2139 | 303 | 14% |
| `Board_EventSeasonPass` | 2065 | 422 | 20% |
| `Board_BattlePass` | 1995 | 319 | 16% |
| `Board_Reborn_IAP` | 1920 | 183 | 10% |
| `Board_Challange` | 1910 | 341 | 18% |
| `Board_GiftLogin` | 1752 | 274 | 16% |
| `Board_TechLab` | 1738 | 214 | 12% |
| `Popup_BuyItem` | 1568 | 417 | 27% |
| `Board_Stage` | 1462 | 261 | 18% |
| `Popup_ChooseVersionDatas` | 1445 | 303 | 21% |
| `Board_Reborn` | 1413 | 299 | 21% |

## Còn thiếu

- `_index.csv` (báo cáo 20) **không khớp** đĩa: thiếu 16 màn. Cần sửa `ui_layout.py`
  để lần chạy sau ghi đủ, hoặc dùng file này làm nguồn.
- Chưa có `orthographicSize`/độ phân giải tham chiếu → chưa quy ra pixel.
- Nhiều bản sao của cùng một màn (nhiều prefab instance); bảng chỉ lấy bản nhiều node nhất.
