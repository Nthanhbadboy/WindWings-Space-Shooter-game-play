# 28 — Truy vết công thức trong method cân bằng (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ `raw/il2cpp-consts/*.json` + `*.asm.txt`
> bằng `tools/apk-analyze/formula_trace.py`. Cột `flow` là hằng số theo **thứ tự địa chỉ**
> trong thân hàm; còn rẽ nhánh (`b.ne`, `csel`…) nên đây là **nguyên liệu** để đọc công thức,
> chưa phải công thức. Đích `bl` có `~` nghĩa là nằm giữa thân method khác (generic dùng chung).

- method có trace: **425**, method đáng đọc trước: **59**

## Đọc thử một method

`Player_Get_Datas.GetWingCannonDamage` — flow theo địa chỉ:

```
`cmp 4` → load **0.168** → `cmp 58` → load **0.1764** → `cmp 118` → load **0.1932** (fmul)
→ `cmp 248` → **fadd 1.0**
```

Đọc ra (mức **B**): hệ số damage chọn theo **ngưỡng** của một giá trị so sánh
(4 / 58 / 118 / 248 — khả năng là cấp tech hoặc chỉ số cộng dồn), 0.1764 = 0.168 × 1.05
và 0.1932 = 0.168 × 1.15, cuối cùng có `+ 1.0` kiểu `(1 + x)`. Chưa chắc cho đến khi
đọc rẽ nhánh đầy đủ trong `.asm.txt`.

## Method đáng đọc trước (nhiều float pool / phép tính nhất)

| class.method | float từ pool | phép tính | gọi tới (đã giải tên) |
|---|---|---|---|
| `Enemy_Data_Balance.GetPVPPlayScore` | 5.0, 2.0, 1.0, 0.2, 0.5, 0.01, 2.3, 0.1 | fmul, fmul |  |
| `Stage_Get_Datas.GetBonus` | 60.0, 50.0, 40.0, 50.0, 20.0, 40.0, 30.0, 15.0 | fmul, fmul, fmul |  |
| `Player_Get_Datas.get_abi32Amount` | 20000.0, 5.0, 1.0, 1.0, -1.0, 360.0, 180.0, 1.0 | fmul, fmul |  |
| `Droid_Data_Balance.GetBaseDamage` | 100.0, 0.6, 3.0, 3.0, 100.0, 0.6, 3.0, 4.0 | fadd, fadd, fadd, fadd |  |
| `Player_Health.GainHealth` | 100.0, 1.0, 0.2, 1.0, 1.0 | fdiv, fmul, fsub, fmul, fmul, fsub, fsub, fmul | Player_Health.GainHealth |
| `Player_Ingame.get_IsAttacking` | 1.25, 1.0, 1.0, 0.2 | fmul, fadd, fadd, fadd, fadd, fadd, fmul, fadd | Player_Attack.SuperPowerUp, Player_Attack.get_maxLv, Player_Attack.get_playerIngameScript, Player_Get_Datas.AddPowerPercentWhenHpBelow30 |
| `Tech_Datas.IsStatUnlocked` | 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0 |  | GameDatas.get_PlayerVipLevel, Tech_Datas.GetTechStatPoints, Tech_Datas.IsStatUnlocked |
| `Enemy_Data_Balance.GetArenaPlayScore` | 5.0, 2.0, 1.0, 0.2, 0.5, 300.0, 25.0, 65.0 | fmul |  |
| `Enemy_Data_Balance.GetSurvivalScore` | 6.0, 3.0, 1.1, 0.2, 0.5, 500.0, 23.0, 40.0 |  |  |
| `Player_Health.TakeDamage` | 100.0, 0.3, 90.0, 100.0, 100.0, 100.0, 1.0 | fadd, fsub, fsub | Player_Attack.IsInvisible, Player_Attack.SetInvisible, Player_Get_Datas.TimeToImmuneOneHit |
| `Device_Get_Data.GetPlayerUse` | 30.0, 70.0, 45.0, 55.0, 60.0, 40.0, 75.0, 25.0 |  |  |
| `Device_Get_Data.GetStringName` | 1.0, 1.0, 1.0 | fmul, fmul, fmul, fmul, fsub |  |
| `Player_Get_Datas.GetTalentMegaBombDamage` | 3.9, 2.2, 3.0, 3.45 | fmul, fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Ingame.set_Level` | 1.0 | fsub, fadd, fadd, fadd, fadd, fmul, fadd | Player_Attack.OnDisable, Player_Attack.get_playerIngameScript |
| `Player_Ability.OnBulletDroneSkill6Destroyed` | 0.68, 17.0, 1.0, 0.25, 5.0, 10.0, 4.0 |  |  |
| `Player_Attack.<IEInvisible>b__27_0` | 0.06, 50.0, 0.03, 3.0 | fadd, fsub, fadd | Player_Attack.GetDeviceAddPowerPercent, Player_Attack.ResetInvisible, Player_Attack.get_dmgTechItem0, Player_Attack.get_playerIngameScript |
| `Player_Get_Datas.GetSecretWeaponStatPercent` | 3.0, 0.666, 0.9, 1.3, 2.25, 2.86 | fmul | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTimeFreeOverdrive` | 9.0, 60.0, 100.0, 60.0, 70.0, 80.0, 90.0 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetMaxChargeDuration` | 1.0, 0.5, 0.4, 0.3 | fsub, fmul | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetSecretWeaponDuration` | 0.8, 0.2, 0.15, 0.12 | fadd, fadd | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetTalentBombDamage` | 2.5, 1.6, 2.3 | fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTalentLaserDamage` | 1.5 | scvtf, fmul, fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTalentStunDamage` | 1.2, 1.4, 1000.0, 1.8 | fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.TimeToImmuneOneHit` | 25.0, 30.0, 40.0, 35.0, 50.0, 45.0 |  | Tech_Datas.GetTechStatLevel |
| `Player_Health.OnChangeDataDevice` | 100.0, 1.0, 0.05, 0.5 | fadd, fadd | Device_Get_Data.GetStatValue1, Player_Health.GainHealth |
| `Enemy_Data_Balance.GetBonusCoin` | 100.0, 20.0 | fmul, fadd, fmul |  |
| `Player_Get_Datas.AddPowerPercentWhenHpBelow30` | 0.5, 0.1, 0.4, 0.3, 0.2 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GainHpPercentWhenUseOverDrive` | 0.25, 0.2, 0.3, 0.1, 0.15 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetGainHpItemAddOverTime` | 0.2, 0.2, 200.0 | fadd, fmul | Player_Get_Datas.GetStartHp |
| `Player_Get_Datas.GetHpRecoverSpeed` | 1.0, 0.1, 0.08 | fadd, fmul | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetMainCannonCritPercent` | 0.1, 0.2, 0.18, 0.15, 0.05 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetMainCannonRatePercent` | 0.03, 0.12, 0.1, 0.08, 0.05 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetTalentRocketDamage` |  | scvtf, fmul, fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.KillPercentWhenEnemyHpBelow30` | 0.04, 0.1, 0.075, 0.06, 0.025 |  | Tech_Datas.GetTechStatLevel |
| `Tech_Datas.NumberTechStats` | 60.0, 0.2, -0.2 | fadd, fadd | GameDatas.get_VipPoints, IAP_Manager.GetConsumablePriceString, IAP_Manager.GetVipPoint, IAP_Manager.InitiateProductIDPurchase |
| `Tech_Datas.SetTechLabLevel` | 0.05, 0.3, 5.0, 0.0625, 0.0625 |  | Tech_Datas.GetTechLabLevel, Tech_Datas.SetTechLabLevel, Tech_Datas.SetTechStatLevel, Tech_Datas.SetTechStatPoints |
| `Tech_Datas.SetTechStatLevel` | 0.4, 1.0, 1.48, 0.57, -0.1 |  | GameDatas.get_Gems, GameDatas.get_StarCount, Tech_Datas.GetCostUpgrade, Tech_Datas.GetStarToUpgrade |
| `Player_Ability.OffShieldDroid101` | 100.0, 16000.0 | fadd, fadd |  |
| `Player_Get_Datas.GetGainHpItem` | 0.15, 1.0, 1.0, 100.0 |  | Player_Get_Datas.GetStartHp |
| `Player_Get_Datas.GetMainCannonDamage` | 0.168, 0.1764 | fmul, fadd | Player_Get_Datas.GetMainCannonStatPercent |

## Giới hạn

- `bl` vào giữa thân method (generic IL2CPP dùng chung) chỉ ghi gần đúng bằng `~`.
- Hằng số `compare` có thể là ngưỡng cấp, ID item hoặc enum — phải đọc ngữ cảnh rẽ nhánh.
- Muốn công thức chắc chắn: đọc `.asm.txt` của từng method trong bảng trên, hoặc Ghidra.
