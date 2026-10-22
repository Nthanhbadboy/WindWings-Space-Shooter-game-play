# Hằng số bóc từ thân hàm IL2CPP

> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,
> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,
> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không
> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.

- .so: `libil2cpp.so` — aarch64
- class đích: **12**, method: **305**

## Getter: trả hằng số hay đọc dữ liệu?

Mỗi getter trong build này đều bị bọc bởi guard khởi tạo static của IL2CPP
(`ldrb`/`tbnz` → `bl <cctor>` → `strb`), nên ta cắt guard rồi phân loại **phần đuôi**:
`const` = trả ngay một số, `field` = đọc field static, `computed` = có phép tính,
`call` = nhảy sang hàm khác (`b`, tail-call).

> **Kết luận tạm thời:** nếu `const` = 0 thì bảng cân bằng **không nằm trong hằng số**
> của getter, mà nằm trong dữ liệu/asset — đúng với hướng đi của repo này.

| class | field | computed | call | const |
|---|---:|---:|---:|---:|
| `ArenaManager` | 0 | 4 | 13 | **1** |
| `Device_Get_Data` | 0 | 10 | 2 | **1** |
| `Droid_Data_Balance` | 0 | 7 | 3 | **2** |
| `Enemy_Data_Balance` | 0 | 4 | 1 | **3** |
| `GameDatas` | 19 | 8 | 38 | **7** |
| `IAP_Manager` | 0 | 16 | 18 | **0** |
| `Map_Get_Datas` | 0 | 6 | 3 | **0** |
| `Player_Datas` | 0 | 0 | 0 | **1** |
| `Player_Get_Datas` | 0 | 27 | 2 | **31** |
| `RankManager` | 0 | 2 | 8 | **0** |
| `Stage_Get_Datas` | 0 | 9 | 1 | **1** |
| `Tech_Datas` | 0 | 17 | 3 | **2** |
| **tổng** | 19 | 110 | 92 | **49** |

### Getter trả hằng số (nếu có)

| class | method | giá trị |
|---|---|---:|
| `ArenaManager` | `SetUserRandom` | None |
| `Device_Get_Data` | `GetStringName` | None |
| `Droid_Data_Balance` | `GetBaseDamage` | None |
| `Droid_Data_Balance` | `IsBought` | None |
| `Enemy_Data_Balance` | `GetBonusCoin` | None |
| `Enemy_Data_Balance` | `GetBonusExp` | 30 |
| `Enemy_Data_Balance` | `GetSurvivalScore` | 64 |
| `GameDatas` | `IsHasCheatResources` | None |
| `GameDatas` | `set_Gems` | None |
| `GameDatas` | `IsHasGiftLanguages` | 1 |
| `GameDatas` | `IsCountryPremium` | None |
| `GameDatas` | `IsProVersion` | 64 |
| `GameDatas` | `IsPremiumExpired` | None |
| `GameDatas` | `SetProExpiryDateTime` | 96 |
| `Player_Datas` | `ctor` | 96 |
| `Player_Get_Datas` | `GetMaxRebornCount` | 5 |
| `Player_Get_Datas` | `GetAllShipNoUnlock` | 48 |
| `Player_Get_Datas` | `GetRandomPlayerCard` | 10001 |
| `Player_Get_Datas` | `GetHpStatPercent` | None |
| `Player_Get_Datas` | `GetGainHpItem` | None |
| `Player_Get_Datas` | `GetGainHpItemAddOverTime` | None |
| `Player_Get_Datas` | `GetGainHpItemAddTime` | None |
| `Player_Get_Datas` | `TimeToImmuneOneHit` | None |
| `Player_Get_Datas` | `GetMainCannonStatPercent` | None |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | None |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | None |
| `Player_Get_Datas` | `GetWingCannonStatPercent` | None |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | None |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | None |
| `Player_Get_Datas` | `GetMagnetStatPercent` | None |
| `Player_Get_Datas` | `GetPercentDropFreeOverDriveEvery30Seconds` | None |
| `Player_Get_Datas` | `GetTimeFreeOverdrive` | None |
| `Player_Get_Datas` | `GainHpPercentWhenUseOverDrive` | None |
| `Player_Get_Datas` | `GetSecretWeaponStatPercent` | None |
| `Player_Get_Datas` | `GetSecretWeaponDuration` | None |
| `Player_Get_Datas` | `GetTalentBombDamage` | None |
| `Player_Get_Datas` | `GetTalentRocketDamage` | None |
| `Player_Get_Datas` | `GetTalentStunDamage` | None |
| `Player_Get_Datas` | `GetTalentStunRanger` | None |
| `Player_Get_Datas` | `GetTalentInvisibleRanger` | None |
| `Player_Get_Datas` | `GetTalentLaserDamage` | None |
| `Player_Get_Datas` | `GetTalentMegaBombDamage` | None |
| `Player_Get_Datas` | `GetTalentInvisible2Ranger` | None |
| `Player_Get_Datas` | `GetMaxChargeDuration` | None |
| `Player_Get_Datas` | `GetMaxCountRockets` | 3 |
| `Player_Get_Datas` | `GetMaxPowerUpPoints` | 6 |
| `Stage_Get_Datas` | `GetBonus` | None |
| `Tech_Datas` | `GetTechStatUpgradePrice` | None |
| `Tech_Datas` | `SetTechLabLevel` | 128 |


## `GameDatas` — cờ save/anti-cheat, cheat counters

- method đọc được: **73**, có hằng số: **72**
- float: `—`
- int: `2, 3, 5, 6, 7, 8, 10, 14, 15, 16, 22, 23, 24, 26, 40, 64, 96, 100, 250, 500, 2139095040`
- hằng số dùng trong phép tính: `—`

## `Player_Get_Datas` — chỉ số tàu: HP, damage, tốc độ bắn, giá nâng cấp

- method đọc được: **62**, có hằng số: **61**
- float: `-1.0, 0.25, 0.5, 1.0, 1.25, 1.5, 2.25, 2.5, 3.0, 3.5, 5.0, 8.0, 9.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 21, 24, 30, 48, 58, 64, 78, 98, 108`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fdiv:3.5, arith:fmul:0.5, arith:fmul:1.5, arith:fmul:8.0, arith:fsub:1.0, arith:scvtf:1.25`

## `IAP_Manager` — giá và product id runtime

- method đọc được: **35**, có hằng số: **34**
- float: `—`
- int: `2, 3, 4, 5, 7, 8, 12, 24, 48, 50, 64, 71`
- hằng số dùng trong phép tính: `—`

## `ArenaManager` — arena: rank, mùa, thưởng

- method đọc được: **34**, có hằng số: **27**
- float: `—`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 32, 40, 60, 64, 101, 112, 1000`
- hằng số dùng trong phép tính: `—`

## `Tech_Datas` — tech lab: giá, delta giá, sao

- method đọc được: **25**, có hằng số: **24**
- float: `-4.0, -1.0, 0.0625, 0.5, 1.0, 5.0, 60.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 24, 28, 30, 31, 32, 34, 40, 43, 44, 48, 60, 63`
- hằng số dùng trong phép tính: `arith:fadd:-4.0, arith:fmul:0.5`

## `RankManager` — rank: ngưỡng điểm, thời gian

- method đọc được: **19**, có hằng số: **17**
- float: `10.0`
- int: `2, 8, 16`
- hằng số dùng trong phép tính: `arith:fadd:10.0`

## `Device_Get_Data` — device: stat, giá

- method đọc được: **14**, có hằng số: **13**
- float: `-5.0, 0.5, 1.0, 5.0, 25.0, 30.0, 40.0, 45.0, 55.0, 60.0, 70.0, 75.0, 100.0`
- int: `2, 3, 4, 5, 8, 9, 11, 12, 17, 24, 28, 32, 38, 48, 56, 57, 96, 999, 1000, 10001, 4294967295`
- hằng số dùng trong phép tính: `arith:fmul:-5.0, arith:fmul:0.5, arith:fmul:5.0, arith:fsub:1.0`

## `Droid_Data_Balance` — drone: damage, timeout, giá unlock/upgrade

- method đọc được: **13**, có hằng số: **11**
- float: `1.0, 3.0, 4.0, 15.0, 100.0, 360.0, 500.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 30, 32, 50, 56, 68, 101, 102, 103, 312, 500, 800`
- hằng số dùng trong phép tính: `arith:fadd:1.0`

## `Stage_Get_Datas` — stage: bonus, delta level/coin/gem, số enemy

- method đọc được: **11**, có hằng số: **10**
- float: `1.0, 1.25, 1.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 29, 32, 36, 40, 59, 60, 112, 312, 30009, 30015, 30016, 30029, 30030, 30039, 31011, 38001`
- hằng số dùng trong phép tính: `arith:fmul:1.0, arith:fmul:1.25, arith:fmul:5.0`

## `Map_Get_Datas` — map: wave, danh sách map theo mode

- method đọc được: **10**, có hằng số: **8**
- float: `—`
- int: `2, 3, 4, 6, 9, 10`
- hằng số dùng trong phép tính: `—`

## `Enemy_Data_Balance` — enemy: bonus coin/exp, điểm survival/arena/pvp

- method đọc được: **8**, có hằng số: **7**
- float: `0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 6.0, 9.0, 11.0, 15.0, 20.0, 23.0, 25.0, 30.0, 40.0, 56.0, 65.0, 85.0, 100.0, 180.0, 230.0, 300.0, 350.0, 500.0`
- int: `2, 6, 8, 10, 15, 21, 23, 29, 30, 59, 64, 120, 200, 250, 387, 450, 998, 30010, 30014, 30015, 30016, 30029, 30031, 30032`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:9.0, arith:fmul:11.0, arith:fmul:25.0`

## `Player_Datas` — dữ liệu runtime của player

- method đọc được: **1**, có hằng số: **1**
- float: `100.0`
- int: `30, 36, 64, 96`
- hằng số dùng trong phép tính: `—`

## Đọc tiếp

- Mỗi class có file JSON: `reverse-engineering/raw/il2cpp-consts/<Class>.json`
  (từng method, từng hằng số, kèm địa chỉ).
- Disassembly có chú thích: `<Class>.asm.txt`.
- Hằng số chỉ có nghĩa khi đọc cùng control flow — file `.asm.txt` để đối chiếu.
