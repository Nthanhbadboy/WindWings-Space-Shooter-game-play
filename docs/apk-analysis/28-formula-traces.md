# 28 — Truy vết công thức trong method cân bằng (kết luận tạm thời)

> **Kết luận tạm thời.** Sinh offline từ `raw/il2cpp-consts/*.json` + `*.asm.txt`
> bằng `tools/apk-analyze/formula_trace.py`. Cột `flow` là hằng số theo **thứ tự địa chỉ**
> trong thân hàm; còn rẽ nhánh (`b.ne`, `csel`…) nên đây là **nguyên liệu** để đọc công thức,
> chưa phải công thức. Đích `bl` có `~` nghĩa là nằm giữa thân method khác (generic dùng chung).

- method có trace: **1662**, method đáng đọc trước: **114**

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
| `Enemy_Get_Datas.GetDamagePowered` | 1.5, 0.3, 0.89, 0.56, 3.6, 3.0, 2.68, 2.2 | fmul, fdiv, fadd, fadd, fmul, fadd, fmul, fmul |  |
| `Board_Endgame.Init` | 1.0, 0.91765, 12.0, -0.1, 5.0, 3.2, -0.1, 2.85 | fmul, fadd, fadd, fmul, fsub, fsub, fsub, fadd | Board_Endgame.IESetEndgameEndless, Board_Endgame.SetMissions, Board_Endgame.SetObjectEndgame, Board_Endgame.SetRewards |
| `Enemy_Get_Datas.cctor` | 1000.0, 6800.0, 650.0, 4200.0, 75000.0, 14200.0, 12000.0, 9000.0 |  |  |
| `Board_Endgame.OnEnable` | 1.0, 0.68, 0.8, 1.0, 1.0, 1.0, 1.0, 3.95 |  | Board_Endgame.Init, Board_Endgame.IsVideoLoaded, Board_Endgame.OpenRate, Board_Endgame.SetShopPrices |
| `Enemy_Data_Balance.GetPVPPlayScore` | 5.0, 2.0, 1.0, 0.2, 0.5, 0.01, 2.3, 0.1 | fmul, fmul |  |
| `Stage_Get_Datas.GetBonus` | 60.0, 50.0, 40.0, 50.0, 20.0, 40.0, 30.0, 15.0 | fmul, fmul, fmul |  |
| `Player_Get_Datas.cctor` | 3.0, 10.0, 0.18, 2500.0, 18.0, 5.6, 0.4, 1.5 |  |  |
| `Board_Endgame.SetChallangeRewards` | -1.0, -1.0, 1.0, 1.0, -1.1, 1.0, 1.0, 1.0 | fmul | GameDatas.get_Coins, GameDatas.get_Gems, GameDatas.get_WingCoins, GameDatas.set_Coins |
| `Board_Maps.<SetProcessBattlePass>d__160.MoveNext` | 1.0, 0.01, 1.0, 0.01, 0.1, 0.1 | fmul, fmul, fmul, fdiv, fdiv, fmul |  |
| `Board_Players.SetActiveButtons` | 1.0, 1.0, -1.8, 3.5, -1.8, 3.5, -0.5, 0.6 |  | Board_Maps.get_IsBattlePassProUnlocked, Board_Players.CheckUnlockStarButton, Board_Players.GetPlayerUsed, Board_Players.IsPlayerBought |
| `Board_Endgame.SetGiftInfo` | 1.0, 0.8, 1.0, 1.28, 1.42, 1.25, 0.8, 1.5 |  | Board_Endgame.SaveDataReward, Player_Get_Datas.GetRandomPlayerCard |
| `Enemy_Data_Balance.GetArenaPlayScore` | 5.0, 2.0, 1.0, 0.2, 0.5, 300.0, 25.0, 65.0 | fmul |  |
| `Enemy_Data_Balance.GetSurvivalScore` | 6.0, 3.0, 1.1, 0.2, 0.5, 500.0, 23.0, 40.0 |  |  |
| `Board_Endgame.SetRewards` | 100.0, 100.0, 100.0, 1.0, 1.0, 100.0, 39.0, 86.0 |  | Board_Endgame.GetMissionCompleted, Board_Endgame.GetNewGift, Board_Endgame.RewardCoins, Board_Endgame.SetArenaRewards |
| `Player_Health.TakeDamage` | 100.0, 0.3, 90.0, 100.0, 100.0, 100.0, 1.0 | fadd, fsub, fsub | Player_Attack.IsInvisible, Player_Attack.SetInvisible, Player_Get_Datas.TimeToImmuneOneHit |
| `Board_Home.<UpdateTimers>d__170.MoveNext` | 0.01569, 0.92157, 1.0, 1.0, 1.0, -4.0, 0.2 | fadd, fdiv |  |
| `Board_Maps.Collect` | 1.28, 0.8, 1.42, 1.0, 1.0, 1.25, 1.25, 1.5 |  | Board_Maps.SaveDataReward, Player_Get_Datas.GetListCards |
| `Board_Maps.OnClickStageButton` | 1.25, -1.25, 1.25, -1.25 | fadd, fadd, fadd, fadd, fadd | Board_Maps.get_ChapterIndex, Board_Maps.get_parentZones, Board_Maps.set_ScrollviewActive, GP_Tutorials.get_IndexTutorial |
| `Player_Get_Datas.GetTalentMegaBombDamage` | 3.9, 2.2, 3.0, 3.45 | fmul, fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Board_Drones.CheckFocus` | 0.845, -0.4, 0.875, 1.475, 0.567, 0.6, 1.5 |  | Board_Drones.GetIndexCell, GameDatas.get_StarCount |
| `Player_Ability.OnBulletDroneSkill6Destroyed` | 0.68, 17.0, 1.0, 0.25, 5.0, 10.0, 4.0 |  |  |
| `Player_Get_Datas.GetSecretWeaponStatPercent` | 3.0, 0.666, 0.9, 1.3, 2.25, 2.86 | fmul | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTimeFreeOverdrive` | 9.0, 60.0, 100.0, 60.0, 70.0, 80.0, 90.0 |  | Tech_Datas.GetTechStatLevel |
| `Board_Drones.SetActiveButtons` | 1.0, -0.5, -0.5, 3.5, 0.4, 1.0 |  | Board_Drones.CheckUnlockStarButton |
| `Boss1_Director.<WarningBossAppear>d__15.MoveNext` | 3.0, 2.0, 1.0, 0.05, 3.0, 0.5 |  |  |
| `Player_Get_Datas.GetMaxChargeDuration` | 1.0, 0.5, 0.4, 0.3 | fsub, fmul | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetSecretWeaponDuration` | 0.8, 0.2, 0.15, 0.12 | fadd, fadd | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetTalentBombDamage` | 2.5, 1.6, 2.3 | fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTalentLaserDamage` | 1.5 | scvtf, fmul, fmul, fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.GetTalentStunDamage` | 1.2, 1.4, 1000.0, 1.8 | fmul, fadd | Tech_Datas.GetTechStatPoints |
| `Player_Get_Datas.TimeToImmuneOneHit` | 25.0, 30.0, 40.0, 35.0, 50.0, 45.0 |  | Tech_Datas.GetTechStatLevel |
| `Board_Drones.SetUpgradeCost` | 1.0, 0.65 | scvtf, scvtf, fmul | Board_Drones.GetPlayerPower |
| `Board_Maps.GetRandomPosition` | 3.5, 2.85, 1.5, 2.5 | fadd |  |
| `Boss_AttackTypes.<IEGunCheckAttack>d__9.MoveNext` | -6.0, 6.0, 1.0, -1.0 | fmul |  |
| `Enemy_Controller.OnTakeDamage` | 3.0, 100.0, 100.0, 0.4, 6.0 |  | Enemy_Controller.OnDieWhenZeroHp, Enemy_Controller.UpdateHpBar, Enemy_Health.CalculateDamage |
| `Enemy_Data_Balance.GetBonusCoin` | 100.0, 20.0 | fmul, fadd, fmul |  |
| `Player_Get_Datas.AddPowerPercentWhenHpBelow30` | 0.5, 0.1, 0.4, 0.3, 0.2 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GainHpPercentWhenUseOverDrive` | 0.25, 0.2, 0.3, 0.1, 0.15 |  | Tech_Datas.GetTechStatLevel |
| `Player_Get_Datas.GetGainHpItemAddOverTime` | 0.2, 0.2, 200.0 | fadd, fmul | Player_Get_Datas.GetStartHp |
| `Player_Get_Datas.GetHpRecoverSpeed` | 1.0, 0.1, 0.08 | fadd, fmul | Tech_Datas.GetTechStatLevel |

## Giới hạn

- `bl` vào giữa thân method (generic IL2CPP dùng chung) chỉ ghi gần đúng bằng `~`.
- Hằng số `compare` có thể là ngưỡng cấp, ID item hoặc enum — phải đọc ngữ cảnh rẽ nhánh.
- Muốn công thức chắc chắn: đọc `.asm.txt` của từng method trong bảng trên, hoặc Ghidra.
