# Hằng số bóc từ thân hàm IL2CPP

> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,
> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,
> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không
> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.

- .so: `libil2cpp.so` — aarch64
- class đích: **17**, method: **425**

## Getter: trả hằng số hay đọc dữ liệu?

Mỗi getter trong build này đều bị bọc bởi guard khởi tạo static của IL2CPP
(`ldrb`/`tbnz` → `bl <cctor>` → `strb`), nên ta cắt guard rồi phân loại **phần đuôi**:
`const` = trả ngay một số, `field` = đọc field static, `computed` = có phép tính,
`call` = nhảy sang hàm khác (`b`, tail-call).

> **Kết luận tạm thời:** nếu `const` = 0 thì bảng cân bằng **không nằm trong hằng số**
> của getter, mà nằm trong dữ liệu/asset — đúng với hướng đi của repo này.

| class | field | computed | call | const |
|---|---:|---:|---:|---:|
| `ArenaManager` | 0 | 1 | 17 | **0** |
| `Device_Get_Data` | 0 | 2 | 7 | **0** |
| `Droid_Data_Balance` | 0 | 1 | 8 | **0** |
| `Enemy_Data_Balance` | 0 | 1 | 6 | **1** |
| `GameDatas` | 23 | 3 | 40 | **1** |
| `IAP_Manager` | 0 | 0 | 32 | **0** |
| `Map_Get_Datas` | 0 | 0 | 9 | **0** |
| `Player_Ability` | 0 | 0 | 18 | **0** |
| `Player_Attack` | 0 | 2 | 11 | **1** |
| `Player_Get_Datas` | 0 | 23 | 22 | **9** |
| `Player_Health` | 2 | 0 | 7 | **0** |
| `Player_Ingame` | 0 | 0 | 14 | **0** |
| `Player_Talent` | 1 | 2 | 17 | **0** |
| `RankManager` | 0 | 0 | 8 | **0** |
| `Stage_Get_Datas` | 0 | 1 | 10 | **0** |
| `Tech_Datas` | 0 | 5 | 14 | **0** |
| **tổng** | 26 | 41 | 240 | **12** |

### Float đọc từ literal pool (`.rodata`) — số thật, không phải suy luận

`adrp xN, #page` + `ldr sM, [xN, #off]` trỏ vào bảng float trong `.rodata`;
script đổi VA → offset qua `PT_LOAD` rồi đọc 4 byte, **chỉ trong segment read-only**
(bảng con trỏ metadata nằm ở segment ghi được — đọc vào đó ra rác như `288733`).
Đây là số **có thật trong file**, nhưng ý nghĩa (hệ số nào) vẫn phải đọc thêm control flow.

| class | method | giá trị | VA |
|---|---|---:|---|
| `Device_Get_Data` | `GetStatValue2` | 14.4 | `0x756dd8` |
| `Droid_Data_Balance` | `GetBaseDamage` | 0.6 | `0x756c44` |
| `Enemy_Data_Balance` | `GetBonusCoin` | 0.1 | `0x756c78` |
| `Enemy_Data_Balance` | `GetSurvivalScore` | 1.1 | `0x756b50` |
| `Enemy_Data_Balance` | `GetSurvivalScore` | 0.2 | `0x75700c` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 0.2 | `0x75700c` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 0.01 | `0x756fe0` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 2.3 | `0x756edc` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 0.1 | `0x756c78` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 0.56 | `0x757060` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.8 | `0x756b54` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.6 | `0x756db8` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.7 | `0x756c90` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 2.8 | `0x756fc0` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 4.2 | `0x756bd4` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.4 | `0x756bd8` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.3 | `0x756be0` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.2 | `0x756cb8` |
| `Enemy_Data_Balance` | `GetPVPPlayScore` | 1.1 | `0x756b50` |
| `Enemy_Data_Balance` | `GetArenaPlayScore` | 0.2 | `0x75700c` |
| `GameDatas` | `cctor` | 7.0 | `0x757368` |
| `Player_Ability` | `OnBulletDroneSkill6Destroyed` | 0.68 | `0x756ed0` |
| `Player_Ability` | `_1` | 0.0225 | `0x756d38` |
| `Player_Attack` | `get_dmgTechItem0` | 0.3 | `0x7570e0` |
| `Player_Attack` | `ctor` | -1.0 | `0x757910` |
| `Player_Attack` | `<IEInvisible>b__27_0` | 0.06 | `0x756cc8` |
| `Player_Attack` | `<IEInvisible>b__27_0` | 0.03 | `0x756ecc` |
| `Player_Get_Datas` | `get_abi32Amount` | 20000.0 | `0x756d48` |
| `Player_Get_Datas` | `get_abi32Amount` | 57.29578 | `0x7570dc` |
| `Player_Get_Datas` | `stepLevel` | 0.168 | `0x756f34` |
| `Player_Get_Datas` | `stepLevel` | 1.05 | `0x756d8c` |
| `Player_Get_Datas` | `stepLevel` | 1.15 | `0x7570c8` |
| `Player_Get_Datas` | `GetGainHpItem` | 0.15 | `0x756a68` |
| `Player_Get_Datas` | `GetGainHpItemAddOverTime` | 0.2 | `0x75700c` |
| `Player_Get_Datas` | `GetHpRecoverSpeed` | 0.1 | `0x756c78` |
| `Player_Get_Datas` | `GetHpRecoverSpeed` | 0.08 | `0x75706c` |
| `Player_Get_Datas` | `GetHpRecoverSpeed` | 0.06 | `0x756cc8` |
| `Player_Get_Datas` | `GetHpRecoverSpeed` | 0.03 | `0x756ecc` |
| `Player_Get_Datas` | `GetMainCannonDamage` | 0.168 | `0x756f34` |
| `Player_Get_Datas` | `GetMainCannonDamage` | 0.1764 | `0x756e84` |
| `Player_Get_Datas` | `GetMainCannonDamage` | 0.1932 | `0x756ea0` |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | 0.03 | `0x756ecc` |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | 0.12 | `0x756b38` |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | 0.1 | `0x756c78` |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | 0.08 | `0x75706c` |
| `Player_Get_Datas` | `GetMainCannonRatePercent` | 0.05 | `0x756e18` |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | 0.1 | `0x756c78` |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | 0.2 | `0x75700c` |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | 0.18 | `0x756b98` |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | 0.15 | `0x756a68` |
| `Player_Get_Datas` | `GetMainCannonCritPercent` | 0.05 | `0x756e18` |
| `Player_Get_Datas` | `GetWingCannonDamage` | 0.168 | `0x756f34` |
| `Player_Get_Datas` | `GetWingCannonDamage` | 0.1764 | `0x756e84` |
| `Player_Get_Datas` | `GetWingCannonDamage` | 0.1932 | `0x756ea0` |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.1 | `0x756c78` |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.4 | `0x756fbc` |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.3 | `0x7570e0` |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.2 | `0x75700c` |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | 0.04 | `0x756ec8` |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | 0.1 | `0x756c78` |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | 0.075 | `0x757074` |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | 0.06 | `0x756cc8` |
| `Player_Get_Datas` | `KillPercentWhenEnemyHpBelow30` | 0.025 | `0x756ac4` |
| `Player_Get_Datas` | `GetMagnetRange` | 1.8 | `0x756b54` |
| `Player_Health` | `OnChangeDataDevice` | 0.05 | `0x756e18` |
| `Player_Health` | `GainHealth` | 0.02 | `0x756e14` |
| `Player_Health` | `GainHealth` | 0.01235 | `0x756b7c` |
| `Player_Health` | `GainHealth` | 0.2 | `0x75700c` |
| `Player_Health` | `GainHealth` | 1.4 | `0x756bd8` |
| `Player_Health` | `TakeDamage` | 0.3 | `0x7570e0` |
| `Player_Health` | `cctor` | 2000.0 | `0x7579f0` |
| `Player_Health` | `<Start>b__14_1` | 0.2 | `0x75700c` |
| `Player_Ingame` | `get_IsAttacking` | 0.1 | `0x756c78` |
| `Player_Ingame` | `get_IsAttacking` | 2.689 | `0x756f38` |
| `Player_Ingame` | `get_IsAttacking` | 0.3 | `0x7570e0` |
| `Player_Ingame` | `get_IsAttacking` | -0.4 | `0x756de4` |
| `Player_Ingame` | `get_IsAttacking` | 0.2 | `0x75700c` |
| `Player_Ingame` | `cctor` | -9.6 | `0x756d60` |
| `Player_Talent` | `OnActiveTalent` | 0.2 | `0x75700c` |
| `Player_Talent` | `GetDuration` | 0.2 | `0x75700c` |
| `Player_Talent` | `<SetZoneInvisible2>b__31_0` | 0.01745 | `0x756ca8` |
| `Player_Talent` | `<SetZoneInvisible2>b__31_0` | 0.02 | `0x756e14` |
| `Tech_Datas` | `IsStatUnlocked` | 0.6 | `0x756c44` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 0.86 | `0x756de8` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 0.689 | `0x756dfc` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 150000.0 | `0x756cc4` |
| `Tech_Datas` | `NumberTechStats` | 0.2 | `0x75700c` |
| `Tech_Datas` | `NumberTechStats` | -0.2 | `0x756f50` |
| `Tech_Datas` | `SetTechStatPoints` | 2.55 | `0x756e98` |
| `Tech_Datas` | `SetTechStatLevel` | 0.4 | `0x756fbc` |
| `Tech_Datas` | `SetTechStatLevel` | 1.48 | `0x756a80` |
| `Tech_Datas` | `SetTechStatLevel` | 0.57 | `0x756ee0` |
| `Tech_Datas` | `SetTechStatLevel` | -0.1 | `0x757018` |
| `Tech_Datas` | `GetCostUpgrade` | 2.55 | `0x756e98` |
| `Tech_Datas` | `SetTechLabLevel` | 0.05 | `0x756e18` |
| `Tech_Datas` | `SetTechLabLevel` | 0.3 | `0x7570e0` |
| `Tech_Datas` | `GetPlayerUpgradePrice` | 0.12 | `0x756b38` |
| `Tech_Datas` | `GetPlayerUpgradePrice` | 150000.0 | `0x756cc4` |
| `Tech_Datas` | `GetDroneUpgradePrice` | 0.12 | `0x756b38` |
| `Tech_Datas` | `GetDroneUpgradePrice` | 150000.0 | `0x756cc4` |

### Getter trả hằng số (nếu có)

| class | method | giá trị |
|---|---|---:|
| `Enemy_Data_Balance` | `GetBonusExp` | 6 |
| `GameDatas` | `IsPremiumExpired` | 1 |
| `Player_Attack` | `get_xDmgByRank` | 1.0 |
| `Player_Get_Datas` | `GetMaxRebornCount` | 5 |
| `Player_Get_Datas` | `GetAllShipNoUnlock` | 1 |
| `Player_Get_Datas` | `GetGainHpItemAddTime` | 5.0 |
| `Player_Get_Datas` | `TimeToImmuneOneHit` | 25.0 |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.5 |
| `Player_Get_Datas` | `GetPercentDropFreeOverDriveEvery30Seconds` | 1.0 |
| `Player_Get_Datas` | `GetTimeFreeOverdrive` | 60.0 |
| `Player_Get_Datas` | `GainHpPercentWhenUseOverDrive` | 0.25 |
| `Player_Get_Datas` | `GetMaxCountRockets` | 10 |


## `GameDatas` — cờ save/anti-cheat, cheat counters

- method đọc được: **73**, có hằng số: **72**
- float: `7.0`
- int: `2, 3, 5, 6, 7, 8, 10, 14, 15, 16, 22, 23, 24, 26, 40, 64, 96, 100, 250, 500, 2139095040`
- hằng số dùng trong phép tính: `—`

## `Player_Get_Datas` — chỉ số tàu: HP, damage, tốc độ bắn, giá nâng cấp

- method đọc được: **62**, có hằng số: **61**
- float: `-1.0, 0.0111, 0.0125, 0.025, 0.03, 0.04, 0.05, 0.06, 0.075, 0.08, 0.1, 0.12, 0.15, 0.168, 0.1764, 0.18, 0.1932, 0.2, 0.22, 0.25, 0.3, 0.4, 0.5, 0.666`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 21, 24, 30, 48, 58, 64, 78, 98, 108`
- hằng số dùng trong phép tính: `arith:fadd:0.05, arith:fadd:0.06, arith:fadd:0.1, arith:fadd:0.2, arith:fadd:1.0, arith:fdiv:1.8, arith:fdiv:3.5, arith:fmul:0.0111, arith:fmul:0.0125, arith:fmul:0.03, arith:fmul:0.1, arith:fmul:0.1932, arith:fmul:0.2, arith:fmul:0.22, arith:fmul:0.5, arith:fmul:1.15, arith:fmul:1.5, arith:fmul:1.6, arith:fmul:1.68, arith:fmul:1.8, arith:fmul:2.2, arith:fmul:2.6, arith:fmul:7.3, arith:fmul:8.0`

## `Player_Ability` — ability: khiên, drone skill, dodge

- method đọc được: **46**, có hằng số: **39**
- float: `-1.0, -0.5, 0.0225, 0.25, 0.68, 1.0, 2.5, 4.0, 5.0, 10.0, 17.0, 100.0, 16000.0`
- int: `2, 3, 4, 5, 6, 8, 11, 12, 16, 24, 28, 32, 96, 101, 112, 312, 1016, 20001, 20002, 20003, 20004, 20005, 20006, 20007`
- hằng số dùng trong phép tính: `arith:fadd:-1.0, arith:fadd:-0.5, arith:fadd:1.0, arith:fmul:5.0`

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
- float: `-4.0, -1.0, -0.2, -0.1, 0.05, 0.0625, 0.12, 0.2, 0.3, 0.4, 0.5, 0.57, 0.6, 0.689, 0.86, 1.0, 1.48, 2.55, 5.0, 60.0, 150000.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 24, 28, 30, 31, 32, 34, 40, 43, 44, 48, 60, 63`
- hằng số dùng trong phép tính: `arith:fadd:-4.0, arith:fadd:0.2, arith:fadd:150000.0, arith:fmul:0.12, arith:fmul:0.5, arith:fmul:0.689, arith:fmul:0.86`

## `Player_Talent` — talent: cây điểm, invisible, stun

- method đọc được: **23**, có hằng số: **19**
- float: `0.01745, 0.02, 0.2, 8.0, 18.0`
- int: `2, 3, 4, 5, 6, 8, 12, 14, 15, 16, 18, 24, 28, 48, 64, 83, 100, 147, 312`
- hằng số dùng trong phép tính: `arith:fadd:0.2, arith:fmul:0.01745`

## `Player_Ingame` — trạng thái trong trận: level, power-up theo tàu

- method đọc được: **20**, có hằng số: **18**
- float: `-9.6, -0.5, -0.4, 0.1, 0.2, 0.25, 0.3, 0.5, 1.0, 1.25, 2.689, 3.0, 4.0, 5.0, 20.0, 100.0`
- int: `2, 3, 4, 5, 8, 12, 16, 134, 160, 296, 312`
- hằng số dùng trong phép tính: `arith:fadd:-9.6, arith:fadd:-0.5, arith:fadd:-0.4, arith:fadd:0.25, arith:fadd:0.5, arith:fadd:1.0, arith:fadd:2.689, arith:fadd:3.0, arith:fadd:5.0, arith:fadd:20.0, arith:fmul:0.1, arith:fmul:0.3, arith:fmul:1.0, arith:fmul:4.0, arith:fsub:1.0`

## `Player_Attack` — bắn trong trận: nhịp, đạn, overdrive

- method đọc được: **19**, có hằng số: **16**
- float: `-1.0, -0.5, 0.03, 0.06, 0.25, 0.3, 1.0, 2.0, 2.5, 3.0, 50.0, 100.0`
- int: `2, 3, 4, 5, 6, 8, 17, 32, 37, 38, 64, 999, 1496, 2000, 3000, 4000, 4294967295`
- hằng số dùng trong phép tính: `arith:fadd:-0.5, arith:fadd:0.25, arith:fadd:2.0, arith:fadd:3.0, arith:fsub:1.0`

## `RankManager` — rank: ngưỡng điểm, thời gian

- method đọc được: **19**, có hằng số: **17**
- float: `10.0`
- int: `2, 8, 16`
- hằng số dùng trong phép tính: `arith:fadd:10.0`

## `Device_Get_Data` — device: stat, giá

- method đọc được: **14**, có hằng số: **13**
- float: `-5.0, 0.5, 1.0, 5.0, 14.4, 25.0, 30.0, 40.0, 45.0, 55.0, 60.0, 70.0, 75.0, 100.0`
- int: `2, 3, 4, 5, 8, 9, 11, 12, 17, 24, 28, 32, 38, 48, 56, 57, 96, 999, 1000, 10001, 4294967295`
- hằng số dùng trong phép tính: `arith:fmul:-5.0, arith:fmul:0.5, arith:fmul:5.0, arith:fsub:1.0`

## `Droid_Data_Balance` — drone: damage, timeout, giá unlock/upgrade

- method đọc được: **13**, có hằng số: **11**
- float: `0.6, 1.0, 3.0, 4.0, 15.0, 100.0, 360.0, 500.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 30, 32, 50, 56, 68, 101, 102, 103, 312, 500, 800`
- hằng số dùng trong phép tính: `arith:fadd:1.0`

## `Player_Health` — HP runtime: StartHp gán ở đâu, hồi máu, nhận damage

- method đọc được: **12**, có hằng số: **11**
- float: `-1.0, -0.5, 0.01235, 0.02, 0.05, 0.2, 0.3, 0.5, 1.0, 1.4, 2.0, 4.0, 5.0, 10.0, 90.0, 100.0, 2000.0`
- int: `2, 3, 4, 6, 7, 8, 9, 10, 12, 16, 18, 21, 22, 28, 30, 32, 35, 36, 39, 48, 58, 64, 96, 128`
- hằng số dùng trong phép tính: `arith:fadd:-1.0, arith:fadd:-0.5, arith:fadd:1.0, arith:fadd:5.0, arith:fdiv:0.02, arith:fmul:0.01235, arith:fmul:4.0, arith:fmul:10.0, arith:fsub:1.0, arith:fsub:1.4, arith:fsub:2.0`

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
- float: `0.01, 0.1, 0.2, 0.5, 0.56, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.3, 2.8, 3.0, 4.2, 5.0, 6.0, 9.0, 11.0, 15.0`
- int: `2, 6, 8, 10, 15, 21, 23, 29, 30, 59, 64, 120, 200, 250, 387, 450, 998, 30010, 30014, 30015, 30016, 30029, 30031, 30032`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:0.1, arith:fmul:9.0, arith:fmul:11.0, arith:fmul:25.0`

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
