# Hằng số bóc từ thân hàm IL2CPP

> **Kết luận tạm thời.** Các giá trị dưới đây là hằng số *nhìn thấy trong mã máy*,
> chưa chắc là giá trị thiết kế cuối cùng: có thể là hằng số phụ (epsilon, clamp,
> hệ số nội suy), và có thể bị che bởi phép tính khác. Dùng để **đối chiếu**, không
> phải để chép nguyên. Dữ liệu thô: `reverse-engineering/raw/il2cpp-consts/`.

- .so: `libil2cpp.so` — aarch64
- class đích: **134**, method: **1662**

## Getter: trả hằng số hay đọc dữ liệu?

Mỗi getter trong build này đều bị bọc bởi guard khởi tạo static của IL2CPP
(`ldrb`/`tbnz` → `bl <cctor>` → `strb`), nên ta cắt guard rồi phân loại **phần đuôi**:
`const` = trả ngay một số, `field` = đọc field static, `computed` = có phép tính,
`call` = nhảy sang hàm khác (`b`, tail-call).

> **Kết luận tạm thời:** nếu `const` = 0 thì bảng cân bằng **không nằm trong hằng số**
> của getter, mà nằm trong dữ liệu/asset — đúng với hướng đi của repo này.

| class | field | computed | call | const |
|---|---:|---:|---:|---:|
| `ArenaManager` | 0 | 1 | 18 | **0** |
| `BoardManager` | 0 | 0 | 20 | **0** |
| `Board_Drones` | 0 | 2 | 75 | **0** |
| `Board_Endgame` | 0 | 3 | 72 | **0** |
| `Board_Endgame.<>c` | 0 | 0 | 2 | **3** |
| `Board_Endgame.<>c__DisplayClass123_0` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<>c__DisplayClass142_0` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<>c__DisplayClass142_1` | 0 | 0 | 4 | **0** |
| `Board_Endgame.<>c__DisplayClass143_0` | 0 | 0 | 5 | **0** |
| `Board_Endgame.<>c__DisplayClass144_0` | 0 | 0 | 1 | **0** |
| `Board_Endgame.<>c__DisplayClass144_1` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<CheckLoadingTimeOut>d__122` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<IEGetTimeOnline>d__144` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<IESetEndgameEndless>d__142` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<IETryGetRoomRankEndless>d__143` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<RewardCoins>d__164` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<RunMissions>d__162` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<SetShopPrices>d__193` | 0 | 0 | 2 | **0** |
| `Board_Endgame.<UnboxGifts>d__191` | 0 | 0 | 2 | **0** |
| `Board_Home` | 0 | 4 | 78 | **0** |
| `Board_Home.<>c` | 0 | 0 | 3 | **0** |
| `Board_Home.<>c__DisplayClass147_0` | 0 | 0 | 1 | **0** |
| `Board_Home.<>c__DisplayClass147_1` | 0 | 0 | 2 | **0** |
| `Board_Home.<AutoPopFeedback>d__175` | 0 | 0 | 2 | **0** |
| `Board_Home.<DelayFx>d__114` | 0 | 0 | 2 | **0** |
| `Board_Home.<HideGifts>d__202` | 0 | 0 | 2 | **0** |
| `Board_Home.<IECheckPackTimer>d__111` | 0 | 0 | 2 | **0** |
| `Board_Home.<IECheckSpecialDayGift>d__148` | 0 | 0 | 2 | **0** |
| `Board_Home.<IEGetTimeOnline>d__147` | 0 | 0 | 2 | **0** |
| `Board_Home.<UpdateTimers>d__170` | 0 | 0 | 2 | **0** |
| `Board_Maps` | 0 | 4 | 87 | **2** |
| `Board_Maps.<>c` | 0 | 0 | 1 | **0** |
| `Board_Maps.<>c__DisplayClass102_0` | 0 | 0 | 2 | **0** |
| `Board_Maps.<>c__DisplayClass88_0` | 0 | 0 | 2 | **0** |
| `Board_Maps.<>c__DisplayClass97_0` | 0 | 0 | 1 | **0** |
| `Board_Maps.<>c__DisplayClass97_1` | 0 | 0 | 2 | **0** |
| `Board_Maps.<HideGifts>d__91` | 0 | 0 | 2 | **0** |
| `Board_Maps.<HideRank>d__92` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IECheckOpenWinnerBenefits>d__116` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IECheckPackTimers>d__174` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IECheckStarterTimer>d__173` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IEGetTimeOnline>d__97` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IEOpenRank>d__102` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IEUpdateAbilityEventTimer>d__153` | 0 | 0 | 2 | **0** |
| `Board_Maps.<IEUpdateEventTimer>d__164` | 0 | 0 | 2 | **0** |
| `Board_Maps.<SetProcessBattlePass2>d__154` | 0 | 0 | 2 | **0** |
| `Board_Maps.<SetProcessBattlePass>d__160` | 0 | 0 | 2 | **0** |
| `Board_Maps.<UpdateTimers>d__167` | 0 | 0 | 2 | **0** |
| `Board_Players` | 0 | 1 | 70 | **0** |
| `Board_Stage` | 0 | 2 | 17 | **1** |
| `Board_Stage.<>c` | 0 | 0 | 1 | **1** |
| `Board_Stage.<CheckSpecInrerest>d__18` | 0 | 0 | 2 | **0** |
| `Board_Stage.<CheckTutStartItemToPlay>d__19` | 0 | 0 | 2 | **0** |
| `Boss1_AnimationEvents` | 0 | 0 | 1 | **0** |
| `Boss1_Director` | 0 | 0 | 21 | **0** |
| `Boss1_Director.<>c__DisplayClass25_0` | 0 | 2 | 1 | **0** |
| `Boss1_Director.<IEAttack1>d__25` | 0 | 0 | 2 | **0** |
| `Boss1_Director.<OffGun1Head>d__27` | 0 | 0 | 2 | **0** |
| `Boss1_Director.<OffGun1Static>d__26` | 0 | 0 | 2 | **0** |
| `Boss1_Director.<OnGun1Static>d__28` | 0 | 0 | 2 | **0** |
| `Boss1_Director.<RotateObject>d__29` | 0 | 0 | 2 | **0** |
| `Boss1_Director.<WarningBossAppear>d__15` | 0 | 0 | 2 | **0** |
| `BossAnimationEvents` | 0 | 0 | 3 | **1** |
| `BossSpineEventHandler` | 0 | 0 | 3 | **0** |
| `Boss_1_Animation` | 0 | 0 | 9 | **0** |
| `Boss_AttackPhases` | 0 | 0 | 5 | **0** |
| `Boss_AttackPhases.<>c__DisplayClass12_0` | 0 | 0 | 2 | **0** |
| `Boss_AttackPhases.<>c__DisplayClass13_0` | 0 | 0 | 1 | **0** |
| `Boss_AttackPhases.<>c__DisplayClass14_0` | 0 | 0 | 1 | **0** |
| `Boss_AttackPhases.<>c__DisplayClass15_0` | 0 | 0 | 1 | **0** |
| `Boss_AttackPhases.<IEAttackRound1>d__13` | 0 | 0 | 2 | **0** |
| `Boss_AttackPhases.<IEAttackRound2>d__14` | 0 | 0 | 2 | **0** |
| `Boss_AttackPhases.<IEAttackRound3>d__15` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes` | 0 | 0 | 16 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass10_0` | 0 | 0 | 3 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass12_0` | 0 | 0 | 3 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass13_0` | 0 | 0 | 3 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass14_0` | 0 | 0 | 3 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass2_0` | 0 | 0 | 5 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass2_1` | 0 | 0 | 5 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass2_2` | 0 | 0 | 5 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass2_3` | 0 | 0 | 5 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass2_4` | 0 | 0 | 5 | **0** |
| `Boss_AttackTypes.<>c__DisplayClass9_0` | 0 | 0 | 3 | **0** |
| `Boss_AttackTypes.<IEGunAttackArrangePositionX>d__13` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes.<IEGunAttackAutoCircle>d__11` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes.<IEGunAttackAutoCircleBase>d__12` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes.<IEGunAttackFixed>d__10` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes.<IEGunAttackRandomPositionX>d__14` | 0 | 0 | 2 | **0** |
| `Boss_AttackTypes.<IEGunCheckAttack>d__9` | 0 | 0 | 2 | **0** |
| `DataTutorials` | 0 | 0 | 4 | **0** |
| `Device_Get_Data` | 0 | 2 | 8 | **0** |
| `Droid_Data_Balance` | 0 | 0 | 9 | **0** |
| `Enemy_Appear` | 0 | 0 | 2 | **0** |
| `Enemy_Controller` | 0 | 0 | 32 | **0** |
| `Enemy_Data_Balance` | 0 | 0 | 7 | **1** |
| `Enemy_Destroy` | 0 | 0 | 10 | **0** |
| `Enemy_Display` | 0 | 0 | 6 | **0** |
| `Enemy_Get_Datas` | 0 | 0 | 4 | **0** |
| `Enemy_Health` | 0 | 3 | 1 | **0** |
| `Enemy_Movement` | 1 | 0 | 15 | **0** |
| `Enemy_Movement.<IELinearMove>d__37` | 0 | 0 | 2 | **0** |
| `Enemy_Rotate` | 0 | 0 | 2 | **0** |
| `Enemy_Sub` | 0 | 0 | 21 | **0** |
| `GP_Tutorials` | 1 | 2 | 19 | **0** |
| `GP_Tutorials.<>c` | 0 | 0 | 3 | **0** |
| `GP_Tutorials.<>c__DisplayClass39_0` | 0 | 0 | 4 | **0** |
| `GP_Tutorials.<>c__DisplayClass40_0` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<>c__DisplayClass55_0` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<>c__DisplayClass58_0` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<HideSettings>d__38` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutChangeGameSpeed>d__55` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutChangeGameSpeedBoss>d__58` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutDrones>d__48` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutLaserSkill>d__60` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutMoveFingers>d__40` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutTalents>d__52` | 0 | 0 | 2 | **0** |
| `GP_Tutorials.<TutTransform>d__42` | 0 | 0 | 2 | **0** |
| `GameDatas` | 23 | 3 | 39 | **1** |
| `IAP_Manager` | 0 | 0 | 33 | **0** |
| `Map_Get_Datas` | 0 | 0 | 10 | **0** |
| `Player_Ability` | 0 | 0 | 27 | **0** |
| `Player_Attack` | 0 | 2 | 11 | **1** |
| `Player_Datas` | 0 | 0 | 1 | **0** |
| `Player_Get_Datas` | 1 | 21 | 24 | **8** |
| `Player_Health` | 1 | 1 | 8 | **0** |
| `Player_Ingame` | 1 | 0 | 11 | **0** |
| `Player_Talent` | 1 | 2 | 18 | **0** |
| `RankManager` | 0 | 0 | 8 | **0** |
| `SkipTutorial` | 0 | 0 | 12 | **0** |
| `Stage_Get_Datas` | 0 | 0 | 11 | **0** |
| `Tech_Datas` | 0 | 7 | 16 | **0** |
| `Tut_Settings` | 0 | 0 | 2 | **0** |
| `Tut_Settings1` | 0 | 0 | 5 | **0** |
| **tổng** | 29 | 62 | 1069 | **19** |

### Float đọc từ literal pool (`.rodata`) — số thật, không phải suy luận

`adrp xN, #page` + `ldr sM, [xN, #off]` trỏ vào bảng float trong `.rodata`;
script đổi VA → offset qua `PT_LOAD` rồi đọc 4 byte, **chỉ trong segment read-only**
(bảng con trỏ metadata nằm ở segment ghi được — đọc vào đó ra rác như `288733`).
Đây là số **có thật trong file**, nhưng ý nghĩa (hệ số nào) vẫn phải đọc thêm control flow.

| class | method | giá trị | VA |
|---|---|---:|---|
| `BoardManager` | `LoadSingle` | 0.8 | `0x756c14` |
| `BoardManager` | `LoadSingle` | 0.2 | `0x75700c` |
| `BoardManager` | `LoadAdditive` | 0.8 | `0x756c14` |
| `BoardManager` | `LoadAdditive` | 0.2 | `0x75700c` |
| `BoardManager` | `LoadPopUp` | 0.8 | `0x756c14` |
| `BoardManager` | `LoadPopUp` | 0.2 | `0x75700c` |
| `BoardManager` | `FadeOff` | 0.8 | `0x756c14` |
| `BoardManager` | `FadeOff` | 0.1 | `0x756c78` |
| `Board_Drones` | `SetBounds` | 14.4 | `0x756dd8` |
| `Board_Drones` | `OnPressedButtonCell` | -0.1 | `0x757018` |
| `Board_Drones` | `SetActiveButtons` | 0.4 | `0x756fbc` |
| `Board_Drones` | `SetUpgradeCost` | 4.12 | `0x756de0` |
| `Board_Drones` | `SetUpgradeCost` | 0.65 | `0x756ddc` |
| `Board_Drones` | `CheckFocus` | 0.845 | `0x756d68` |
| `Board_Drones` | `CheckFocus` | -0.4 | `0x756de4` |
| `Board_Drones` | `CheckFocus` | 1.475 | `0x756f0c` |
| `Board_Drones` | `CheckFocus` | 0.567 | `0x756cb4` |
| `Board_Drones` | `CheckFocus` | 0.6 | `0x756c44` |
| `Board_Drones` | `SetPopupPlayer` | 0.86 | `0x756de8` |
| `Board_Drones` | `SetPopupPlayer` | -0.4 | `0x756de4` |
| `Board_Endgame` | `OnEnable` | 0.68 | `0x756ed0` |
| `Board_Endgame` | `OnEnable` | 0.8 | `0x756c14` |
| `Board_Endgame` | `OnEnable` | 3.95 | `0x756cf8` |
| `Board_Endgame` | `OnEnable` | 1.2 | `0x756cb8` |
| `Board_Endgame` | `OnEnable` | 0.95 | `0x756cfc` |
| `Board_Endgame` | `OnEnable` | 3.45 | `0x756ed4` |
| `Board_Endgame` | `OnEnable` | -0.89 | `0x756f8c` |
| `Board_Endgame` | `OnEnable` | -0.4 | `0x756de4` |
| `Board_Endgame` | `OnEnable` | 0.7 | `0x756cac` |
| `Board_Endgame` | `OnEnable` | 0.65 | `0x756ddc` |
| `Board_Endgame` | `OnEnable` | -0.1 | `0x757018` |
| `Board_Endgame` | `Init` | 0.91765 | `0x756e90` |
| `Board_Endgame` | `Init` | -0.1 | `0x757018` |
| `Board_Endgame` | `Init` | 3.2 | `0x756b40` |
| `Board_Endgame` | `Init` | 2.85 | `0x756dec` |
| `Board_Endgame` | `Init` | 1.2 | `0x756cb8` |
| `Board_Endgame` | `Init` | 2.15 | `0x756c18` |
| `Board_Endgame` | `Init` | 0.6 | `0x756c44` |
| `Board_Endgame` | `Init` | 0.64 | `0x756f58` |
| `Board_Endgame` | `Init` | 0.68 | `0x756ed0` |
| `Board_Endgame` | `Init` | 6.55 | `0x756a60` |
| `Board_Endgame` | `Init` | 6.64 | `0x756c80` |
| `Board_Endgame` | `Init` | -3.4 | `0x756b44` |
| `Board_Endgame.<CheckLoadingTimeOut>d__122` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Endgame.<UnboxGifts>d__191` | `MoveNext` | 0.1 | `0x756c78` |
| `Board_Home` | `CheckStarterTimer` | 0.86 | `0x756de8` |
| `Board_Home` | `CheckTutorialFocus` | -0.3 | `0x756e40` |
| `Board_Home.<IECheckPackTimer>d__111` | `MoveNext` | 0.86 | `0x756de8` |
| `Board_Home.<IECheckPackTimer>d__111` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Home.<UpdateTimers>d__170` | `MoveNext` | 0.01569 | `0x756bd0` |
| `Board_Home.<UpdateTimers>d__170` | `MoveNext` | 0.92157 | `0x756ae4` |
| `Board_Home.<UpdateTimers>d__170` | `MoveNext` | 5.37891 | `0x75811c` |
| `Board_Home.<UpdateTimers>d__170` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Maps` | `Refresh` | 0.7 | `0x756cac` |
| `Board_Maps` | `Refresh` | 0.65 | `0x756ddc` |
| `Board_Maps` | `Refresh` | -0.1 | `0x757018` |
| `Board_Maps` | `Collect` | 1.28 | `0x756f10` |
| `Board_Maps` | `Collect` | 0.8 | `0x756c14` |
| `Board_Maps` | `Collect` | 1.42 | `0x756b08` |
| `Board_Maps` | `GetRandomPosition` | 3.2 | `0x756b40` |
| `Board_Maps` | `GetRandomPosition` | 2.85 | `0x756dec` |
| `Board_Maps` | `CreateStages` | -3.6 | `0x756c88` |
| `Board_Maps.<IECheckPackTimers>d__174` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Maps.<IECheckStarterTimer>d__173` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Maps.<IEUpdateAbilityEventTimer>d__153` | `MoveNext` | 0.2 | `0x75700c` |
| `Board_Maps.<SetProcessBattlePass>d__160` | `MoveNext` | 4.15 | `0x756db0` |
| `Board_Maps.<SetProcessBattlePass>d__160` | `MoveNext` | 0.01 | `0x756fe0` |
| `Board_Maps.<SetProcessBattlePass>d__160` | `MoveNext` | 0.1 | `0x756c78` |
| `Board_Maps.<UpdateTimers>d__167` | `MoveNext` | 7.65918 | `0x7578ec` |
| `Board_Maps.<UpdateTimers>d__167` | `MoveNext` | 5.37891 | `0x75811c` |
| `Board_Players` | `SetBounds` | 14.4 | `0x756dd8` |
| `Board_Players` | `OnPressedButtonCell` | -0.1 | `0x757018` |
| `Board_Players` | `SetActiveButtons` | -1.8 | `0x756f64` |
| `Board_Players` | `SetActiveButtons` | 0.6 | `0x756c44` |
| `Board_Players` | `SetActiveButtons` | -0.4 | `0x756de4` |
| `Board_Players` | `SetPlayerInfo` | 2.44 | `0x756e64` |
| `Board_Players` | `SetAbilityInfo` | 0.667 | `0x756fe8` |
| `Board_Players` | `SetAbilities` | 0.4 | `0x756fbc` |
| `Board_Stage` | `OnEnable` | 0.7 | `0x756cac` |
| `Board_Stage` | `OnEnable` | 0.65 | `0x756ddc` |
| `Board_Stage` | `OnEnable` | -0.1 | `0x757018` |
| `Board_Stage.<CheckTutStartItemToPlay>d__19` | `MoveNext` | 0.1 | `0x756c78` |
| `Boss1_Director` | `Defeat` | 0.2 | `0x75700c` |
| `Boss1_Director` | `OnGunDie` | 0.12 | `0x756b38` |
| `Boss1_Director` | `ClearGuns` | 0.1 | `0x756c78` |
| `Boss1_Director.<WarningBossAppear>d__15` | `MoveNext` | 0.05 | `0x756e18` |
| `BossAnimationEvents` | `Vibrate` | 0.15 | `0x756a68` |
| `Boss_1_Animation` | `ClearGuns` | 0.1 | `0x756c78` |
| `Boss_AttackPhases` | `OnGunDie` | 0.15 | `0x756a68` |
| `Boss_AttackTypes.<IEGunAttackAutoCircleBase>d__12` | `MoveNext` | 0.01745 | `0x756ca8` |
| `Boss_AttackTypes.<IEGunAttackRandomPositionX>d__14` | `MoveNext` | -0.03141 | `0x77a20f` |
| `Boss_AttackTypes.<IEGunCheckAttack>d__9` | `MoveNext` | 57.29578 | `0x7570dc` |
| `Enemy_Controller` | `OnTakeDamage` | 0.4 | `0x756fbc` |
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
| `Enemy_Display` | `OnHit` | 0.05 | `0x756e18` |
| `Enemy_Display` | `ctor` | 1.0 | `0x757fa8` |
| `Enemy_Display` | `ctor` | 0.12 | `0x757fac` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.35 | `0x756b0c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.3 | `0x7570e0` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.02 | `0x756e14` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.129 | `0x756ee8` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.69 | `0x756ac8` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.36 | `0x756d0c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.168 | `0x756f34` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.335 | `0x756ce0` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.012 | `0x756c5c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.1689 | `0x756f48` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.2 | `0x75700c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.0125 | `0x756fa8` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 5.69 | `0x756a88` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.2 | `0x756cb8` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.89 | `0x7570d0` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.89 | `0x7574c0` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.56 | `0x7574c4` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.39 | `0x756bfc` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.35 | `0x756ab4` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 3.6 | `0x7570cc` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 2.68 | `0x756f6c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 2.2 | `0x75701c` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.689 | `0x756dfc` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 3.0 | `0x7581e8` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.5 | `0x7581ec` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 2.3 | `0x756edc` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.56 | `0x756eac` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.23 | `0x757000` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.05 | `0x756e18` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 1.1 | `0x756b50` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.68 | `0x756ed0` |
| `Enemy_Get_Datas` | `GetDamagePowered` | 0.369 | `0x756fd8` |
| `Enemy_Movement` | `SetMoveLinearly` | 3.14159 | `0x756a9c` |
| `Enemy_Movement` | `PathFollow` | 57.29578 | `0x7570dc` |
| `Enemy_Movement` | `RocketResumeMove` | 3.14159 | `0x756a9c` |
| `Enemy_Movement.<IELinearMove>d__37` | `MoveNext` | 0.01 | `0x756fe0` |
| `Enemy_Rotate` | `ctor` | 2.0 | `0x7571d0` |
| `Enemy_Rotate` | `ctor` | 80.0 | `0x7571d4` |
| `GP_Tutorials` | `Start` | -9.6 | `0x756d60` |
| `GP_Tutorials.<TutDrones>d__48` | `MoveNext` | 3.9 | `0x756e58` |
| `GP_Tutorials.<TutMoveFingers>d__40` | `MoveNext` | 0.8 | `0x756c14` |
| `GP_Tutorials.<TutTransform>d__42` | `MoveNext` | 0.1 | `0x756c78` |
| `GP_Tutorials.<TutTransform>d__42` | `MoveNext` | 0.05 | `0x756e18` |
| `Player_Ability` | `OnBulletDroneSkill6Destroyed` | 0.68 | `0x756ed0` |
| `Player_Attack` | `get_dmgTechItem0` | 0.3 | `0x7570e0` |
| `Player_Attack` | `ctor` | -1.0 | `0x757910` |
| `Player_Attack` | `ctor` | 1.0 | `0x757914` |
| `Player_Get_Datas` | `get_abi32Amount` | 20000.0 | `0x756d48` |
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
| `Player_Get_Datas` | `GainHpPercentWhenUseOverDrive` | 0.2 | `0x75700c` |
| `Player_Health` | `TakeDamage` | 0.3 | `0x7570e0` |
| `Player_Health` | `cctor` | 2000.0 | `0x7579f0` |
| `Player_Talent` | `OnActiveTalent` | 0.2 | `0x75700c` |
| `Player_Talent` | `GetDuration` | 0.2 | `0x75700c` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 0.86 | `0x756de8` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 0.689 | `0x756dfc` |
| `Tech_Datas` | `GetTechStatUpgradePrice` | 150000.0 | `0x756cc4` |
| `Tech_Datas` | `GetPlayerUpgradePrice` | 0.12 | `0x756b38` |
| `Tech_Datas` | `GetPlayerUpgradePrice` | 150000.0 | `0x756cc4` |
| `Tech_Datas` | `GetDroneUpgradePrice` | 0.12 | `0x756b38` |
| `Tech_Datas` | `GetDroneUpgradePrice` | 150000.0 | `0x756cc4` |
| `Tut_Settings1` | `Start` | 7.2 | `0x756e94` |
| `Tut_Settings1` | `<Start>b__11_0` | 7.2 | `0x756e94` |

### Getter trả hằng số (nếu có)

| class | method | giá trị |
|---|---|---:|
| `Board_Endgame.<>c` | `<OnPressedButtonConfirmBuyX20>b__115_1` | 1 |
| `Board_Endgame.<>c` | `<LoadSceneHome>b__129_0` | 1 |
| `Board_Endgame.<>c` | `<LoadToLoading>b__130_0` | 2 |
| `Board_Maps` | `GetSpecIndexRandom` | 5 |
| `Board_Maps` | `IsCanActiveSpecInrerest` | 1 |
| `Board_Stage` | `IsNotStrongest` | 1 |
| `Board_Stage.<>c` | `<ThrowGetStrongest>b__29_0` | 2 |
| `BossAnimationEvents` | `Vibrate` | 30 |
| `Enemy_Data_Balance` | `GetBonusExp` | 6 |
| `GameDatas` | `IsPremiumExpired` | 1 |
| `Player_Attack` | `get_xDmgByRank` | 1.0 |
| `Player_Get_Datas` | `GetMaxRebornCount` | 5 |
| `Player_Get_Datas` | `GetGainHpItemAddTime` | 5.0 |
| `Player_Get_Datas` | `TimeToImmuneOneHit` | 25.0 |
| `Player_Get_Datas` | `AddPowerPercentWhenHpBelow30` | 0.5 |
| `Player_Get_Datas` | `GetPercentDropFreeOverDriveEvery30Seconds` | 1.0 |
| `Player_Get_Datas` | `GetTimeFreeOverdrive` | 60.0 |
| `Player_Get_Datas` | `GainHpPercentWhenUseOverDrive` | 0.25 |
| `Player_Get_Datas` | `GetMaxCountRockets` | 10 |


## `Board_Maps` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **116**, có hằng số: **104**
- float: `-22.0, -3.6, -1.25, -0.1, 0.65, 0.7, 0.8, 1.0, 1.25, 1.28, 1.42, 1.5, 2.0, 2.5, 2.85, 3.2, 3.5`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 19, 20, 21, 24, 25, 26, 27, 28, 30, 32, 34`
- hằng số dùng trong phép tính: `arith:fadd:-1.25, arith:fadd:1.25, arith:fadd:2.0, arith:fadd:3.2`

## `Board_Home` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **101**, có hằng số: **87**
- float: `-30.0, -28.0, -24.0, -22.0, -1.0, -0.3, 0.86, 1.0`
- int: `2, 3, 4, 5, 7, 8, 10, 12, 16, 17, 23, 24, 25, 28, 30, 31, 32, 36, 56, 57, 60, 64, 96, 112`
- hằng số dùng trong phép tính: `—`

## `Board_Drones` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **81**, có hằng số: **67**
- float: `-1.0, -0.5, -0.4, -0.25, -0.1, 0.4, 0.5, 0.567, 0.6, 0.65, 0.845, 0.86, 0.875, 1.0, 1.475, 1.5, 3.5, 4.12, 14.4`
- int: `2, 3, 4, 5, 8, 12, 16, 17, 20, 24, 28, 40, 48, 56, 60, 64, 80, 96, 112, 128, 272, 432, 448, 460`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:0.5, arith:fmul:4.12, arith:scvtf:0.65, arith:scvtf:4.12`

## `Board_Endgame` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **79**, có hằng số: **70**
- float: `-3.75, -3.4, -3.25, -1.55, -1.1, -1.0, -0.89, -0.5, -0.4, -0.1, 0.45, 0.5, 0.6, 0.64, 0.65, 0.68, 0.7, 0.8, 0.91765, 0.95, 1.0, 1.2, 1.25, 1.28`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 24, 25, 26, 27, 28`
- hằng số dùng trong phép tính: `arith:fadd:-3.75, arith:fadd:-3.4, arith:fadd:-1.55, arith:fadd:2.15, arith:fadd:5.0, arith:fmul:-0.5, arith:fmul:0.5, arith:fmul:1.2, arith:fsub:6.55, arith:fsub:6.64, arith:fsub:10.5`

## `Board_Players` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **79**, có hằng số: **71**
- float: `-1.8, -1.0, -0.5, -0.4, -0.25, -0.1, 0.4, 0.5, 0.6, 0.667, 1.0, 1.5, 2.44, 3.5, 14.4`
- int: `2, 3, 4, 5, 6, 8, 10, 12, 16, 17, 20, 24, 28, 32, 37, 40, 48, 56, 60, 64, 80, 96, 128, 264`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:0.5, arith:fmul:1.0, arith:fmul:2.44`

## `GameDatas` — cờ save/anti-cheat, cheat counters

- method đọc được: **73**, có hằng số: **72**
- float: `—`
- int: `2, 3, 5, 6, 7, 8, 10, 14, 15, 16, 22, 23, 24, 26, 40, 64, 96, 100, 250, 500, 2139095040`
- hằng số dùng trong phép tính: `—`

## `Player_Get_Datas` — chỉ số tàu: HP, damage, tốc độ bắn, giá nâng cấp

- method đọc được: **62**, có hằng số: **61**
- float: `0.0111, 0.0125, 0.025, 0.03, 0.04, 0.05, 0.06, 0.075, 0.08, 0.1, 0.12, 0.15, 0.168, 0.1764, 0.18, 0.1932, 0.2, 0.22, 0.25, 0.3, 0.4, 0.5, 0.666, 0.8`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 21, 24, 30, 32, 48, 58, 64, 78, 96, 98, 100`
- hằng số dùng trong phép tính: `arith:fadd:0.05, arith:fadd:0.06, arith:fadd:0.1, arith:fadd:0.2, arith:fadd:1.0, arith:fdiv:1.8, arith:fdiv:3.5, arith:fmul:0.0111, arith:fmul:0.0125, arith:fmul:0.03, arith:fmul:0.1, arith:fmul:0.1932, arith:fmul:0.2, arith:fmul:0.22, arith:fmul:0.5, arith:fmul:1.15, arith:fmul:1.5, arith:fmul:1.6, arith:fmul:1.68, arith:fmul:1.8, arith:fmul:2.2, arith:fmul:2.6, arith:fmul:7.3, arith:fmul:1500.0`

## `GP_Tutorials` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **46**, có hằng số: **35**
- float: `-9.6, 1.0, 2.0, 3.0, 9.0`
- int: `2, 4, 6, 8, 12, 28, 29, 48`
- hằng số dùng trong phép tính: `arith:fadd:-9.6`

## `Player_Ability` — ability: khiên, drone skill, dodge

- method đọc được: **46**, có hằng số: **39**
- float: `-1.0, -0.5, 0.25, 0.68, 1.0, 2.5, 4.0, 5.0, 10.0, 17.0, 100.0, 16000.0`
- int: `2, 3, 4, 5, 6, 8, 11, 12, 16, 24, 28, 32, 96, 101, 312, 20001, 20002, 20003, 20004, 20005, 20006, 20007, 20008, 20009`
- hằng số dùng trong phép tính: `arith:fadd:-1.0, arith:fadd:-0.5, arith:fadd:1.0, arith:fmul:5.0`

## `IAP_Manager` — giá và product id runtime

- method đọc được: **35**, có hằng số: **34**
- float: `—`
- int: `2, 3, 4, 5, 7, 8, 12, 24, 48, 50, 64, 71`
- hằng số dùng trong phép tính: `—`

## `ArenaManager` — arena: rank, mùa, thưởng

- method đọc được: **34**, có hằng số: **27**
- float: `—`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 60, 64, 101, 112, 1000`
- hằng số dùng trong phép tính: `—`

## `Enemy_Controller` — enemy runtime: GetStartHealth/TakeDamage/UpdateHpBar

- method đọc được: **33**, có hằng số: **16**
- float: `0.4, 3.0, 6.0, 100.0`
- int: `2, 31, 34, 40, 100`
- hằng số dùng trong phép tính: `—`

## `Tech_Datas` — tech lab: giá, delta giá, sao

- method đọc được: **25**, có hằng số: **24**
- float: `0.12, 0.5, 0.689, 0.86, 150000.0`
- int: `2, 3, 4, 5, 7, 8, 10, 12, 13, 24, 28, 30, 31, 32, 34, 48, 64, 319, 369, 2000, 10001, 20001, 25000, 2139095040`
- hằng số dùng trong phép tính: `arith:fadd:150000.0, arith:fmul:0.12, arith:fmul:0.5, arith:fmul:0.689, arith:fmul:0.86`

## `Enemy_Sub` — enemy appear/death/callback control — pending native verification

- method đọc được: **23**, có hằng số: **6**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Player_Talent` — talent: cây điểm, invisible, stun

- method đọc được: **23**, có hằng số: **19**
- float: `0.2`
- int: `2, 3, 4, 5, 6, 8, 12, 14, 16, 18, 24, 28, 48, 64, 83, 100, 147, 312`
- hằng số dùng trong phép tính: `arith:fadd:0.2`

## `BoardManager` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **22**, có hằng số: **20**
- float: `-25.0, -10.0, -2.0, 0.1, 0.2, 0.8`
- int: `2, 3, 4, 7, 8, 9, 10, 16, 29, 32, 40, 56, 57, 58, 59, 96, 112, 128, 312, 1413, 1422`
- hằng số dùng trong phép tính: `arith:fmul:-2.0, arith:fsub:-25.0, arith:fsub:-10.0`

## `Board_Stage` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **22**, có hằng số: **19**
- float: `-0.1, 0.65, 0.7, 2.5, 6.0, 8.0, 10.0`
- int: `2, 3, 4, 5, 6, 8, 10, 12, 13, 36, 56, 57, 60, 858993459`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **22**, có hằng số: **18**
- float: `-0.5, 0.1, 0.12, 0.2, 1.0`
- int: `2, 3, 4, 8, 12, 15, 16, 20, 50, 80, 200, 312, 3108`
- hằng số dùng trong phép tính: `arith:fadd:-0.5`

## `Boss_AttackTypes` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **22**, có hằng số: **18**
- float: `—`
- int: `3, 4, 8, 16, 48, 312`
- hằng số dùng trong phép tính: `—`

## `Enemy_Movement` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **21**, có hằng số: **16**
- float: `-1.0, 1.0, 3.14159, 57.29578, 90.0, 180.0`
- int: `2, 3, 8, 12, 30, 32, 64, 96`
- hằng số dùng trong phép tính: `arith:fmul:3.14159, arith:fmul:57.29578`

## `Player_Ingame` — trạng thái trong trận: level, power-up theo tàu

- method đọc được: **20**, có hằng số: **17**
- float: `1.0, 20.0, 100.0`
- int: `2, 3`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fadd:20.0, arith:fmul:1.0`

## `Player_Attack` — bắn trong trận: nhịp, đạn, overdrive

- method đọc được: **19**, có hằng số: **15**
- float: `-1.0, 0.3, 1.0, 2.0, 2.5, 3.0, 100.0`
- int: `2, 3, 4, 5, 8, 17, 32, 37, 38, 64, 999, 1496, 2000, 3000, 4000, 4294967295`
- hằng số dùng trong phép tính: `arith:fadd:2.0, arith:fadd:3.0`

## `RankManager` — rank: ngưỡng điểm, thời gian

- method đọc được: **19**, có hằng số: **16**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass142_0` — 

- method đọc được: **15**, có hằng số: **6**
- float: `—`
- int: `2, 3, 4, 8, 12, 80`
- hằng số dùng trong phép tính: `—`

## `SkipTutorial` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **15**, có hằng số: **11**
- float: `-3.0, -1.0`
- int: `4, 12, 64`
- hằng số dùng trong phép tính: `arith:fadd:-3.0, arith:fadd:-1.0`

## `Board_Endgame.<>c` — 

- method đọc được: **14**, có hằng số: **5**
- float: `—`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `Device_Get_Data` — device: stat, giá

- method đọc được: **14**, có hằng số: **13**
- float: `100.0`
- int: `2, 3, 4, 5, 12, 32, 48, 10001`
- hằng số dùng trong phép tính: `—`

## `Boss1_AnimationEvents` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **13**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Droid_Data_Balance` — drone: damage, timeout, giá unlock/upgrade

- method đọc được: **13**, có hằng số: **11**
- float: `1.0, 15.0, 100.0`
- int: `2, 3, 4, 5, 6, 12, 30, 32, 50, 101, 500, 800`
- hằng số dùng trong phép tính: `arith:fadd:1.0`

## `Enemy_Destroy` — enemy appear/death/callback control — pending native verification

- method đọc được: **12**, có hằng số: **9**
- float: `3.0, 100.0`
- int: `2, 3, 4, 5, 6, 8, 16, 19, 32, 48, 79, 128, 312`
- hằng số dùng trong phép tính: `—`

## `Player_Health` — HP runtime: StartHp gán ở đâu, hồi máu, nhận damage

- method đọc được: **12**, có hằng số: **11**
- float: `-1.0, 0.3, 1.0, 2.0, 5.0, 90.0, 100.0, 2000.0`
- int: `2, 4, 6, 8, 9, 10, 12, 16, 18, 21, 22, 28, 30, 32, 35, 36, 39, 48, 58, 64, 96, 128, 312, 999`
- hằng số dùng trong phép tính: `arith:fadd:-1.0, arith:fadd:1.0, arith:fadd:5.0, arith:fsub:1.0, arith:fsub:2.0`

## `Stage_Get_Datas` — stage: bonus, delta level/coin/gem, số enemy

- method đọc được: **11**, có hằng số: **10**
- float: `1.0, 1.25, 1.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0`
- int: `2, 3, 4, 5, 6, 8, 12, 16, 29, 32, 36, 40, 59, 60, 112, 312, 30009, 30015, 30016, 30029, 30030, 30031, 30032, 30033`
- hằng số dùng trong phép tính: `arith:fmul:1.0, arith:fmul:1.25, arith:fmul:5.0`

## `Boss_1_Animation` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **10**, có hằng số: **6**
- float: `-0.5, 0.1, 1.0`
- int: `2, 3, 15, 80, 200, 3108`
- hằng số dùng trong phép tính: `arith:fadd:-0.5`

## `Map_Get_Datas` — map: wave, danh sách map theo mode

- method đọc được: **10**, có hằng số: **9**
- float: `—`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass143_0` — 

- method đọc được: **9**, có hằng số: **5**
- float: `—`
- int: `3, 4, 8, 12, 16, 20, 24, 28, 112, 128`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **9**, có hằng số: **9**
- float: `0.15, 1.0`
- int: `2, 3, 4, 39, 50`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<>c__DisplayClass15_0` — 

- method đọc được: **9**, có hằng số: **4**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Enemy_Data_Balance` — enemy: bonus coin/exp, điểm survival/arena/pvp

- method đọc được: **8**, có hằng số: **7**
- float: `0.01, 0.1, 0.2, 0.5, 0.56, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0, 2.3, 2.8, 3.0, 4.2, 5.0, 6.0, 9.0, 11.0, 15.0`
- int: `2, 6, 8, 10, 15, 21, 23, 29, 30, 59, 64, 120, 200, 250, 387, 450, 998, 30010, 30014, 30015, 30016, 30029, 30031, 30032`
- hằng số dùng trong phép tính: `arith:fadd:1.0, arith:fmul:0.1, arith:fmul:9.0, arith:fmul:11.0, arith:fmul:25.0`

## `Board_Endgame.<CheckLoadingTimeOut>d__122` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.2, 60.0`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<IEGetTimeOnline>d__144` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `2, 3, 3193`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<IESetEndgameEndless>d__142` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `2, 3, 4, 5, 6, 7, 8, 9, 3198, 2139095040`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<IETryGetRoomRankEndless>d__143` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.5`
- int: `2, 3, 4, 3218`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<RewardCoins>d__164` — 

- method đọc được: **6**, có hằng số: **2**
- float: `1.0`
- int: `2, 24, 28, 30, 31, 36, 60, 96`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<RunMissions>d__162` — 

- method đọc được: **6**, có hằng số: **2**
- float: `-1.0, 0.5`
- int: `2, 3, 4, 6, 8, 12, 60, 64`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<SetShopPrices>d__193` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<UnboxGifts>d__191` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.1`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<>c` — 

- method đọc được: **6**, có hằng số: **3**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<AutoPopFeedback>d__175` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<DelayFx>d__114` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.5`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<HideGifts>d__202` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<IECheckPackTimer>d__111` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.2, 0.86`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<IECheckSpecialDayGift>d__148` — 

- method đọc được: **6**, có hằng số: **2**
- float: `—`
- int: `8, 48`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<IEGetTimeOnline>d__147` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `2, 3, 3193`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<UpdateTimers>d__170` — 

- method đọc được: **6**, có hằng số: **2**
- float: `-4.0, -2.0, 0.01569, 0.2, 0.92157, 1.0, 5.37891`
- int: `2, 3, 4, 5, 8, 12, 40, 48, 96`
- hằng số dùng trong phép tính: `arith:fadd:-2.0, arith:fdiv:5.37891`

## `Board_Maps.<HideGifts>d__91` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<HideRank>d__92` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IECheckOpenWinnerBenefits>d__116` — 

- method đọc được: **6**, có hằng số: **2**
- float: `—`
- int: `2, 8, 24, 80`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IECheckPackTimers>d__174` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.2`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IECheckStarterTimer>d__173` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.2`
- int: `2, 3, 32, 4294967295`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IEGetTimeOnline>d__97` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `2, 3, 3193`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IEOpenRank>d__102` — 

- method đọc được: **6**, có hằng số: **1**
- float: `-22.0, 1.0`
- int: `2, 5`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IEUpdateAbilityEventTimer>d__153` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.2`
- int: `2, 8`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<IEUpdateEventTimer>d__164` — 

- method đọc được: **6**, có hằng số: **2**
- float: `—`
- int: `2, 8, 24, 128`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<SetProcessBattlePass2>d__154` — 

- method đọc được: **6**, có hằng số: **2**
- float: `—`
- int: `12, 16, 24, 40, 112`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<SetProcessBattlePass>d__160` — 

- method đọc được: **6**, có hằng số: **2**
- float: `0.01, 0.1, 1.0, 4.15, 24.0`
- int: `2, 3, 4, 8, 32, 40, 128, 3454, 2139095040`
- hằng số dùng trong phép tính: `arith:fdiv:24.0, arith:fmul:1.0, arith:fmul:4.15`

## `Board_Maps.<UpdateTimers>d__167` — 

- method đọc được: **6**, có hằng số: **2**
- float: `5.37891, 7.65918`
- int: `2, 3, 4, 8, 12, 80`
- hằng số dùng trong phép tính: `arith:fdiv:5.37891, arith:fdiv:7.65918`

## `Board_Stage.<CheckSpecInrerest>d__18` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `Board_Stage.<CheckTutStartItemToPlay>d__19` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.1`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<IEAttack1>d__25` — 

- method đọc được: **6**, có hằng số: **1**
- float: `1.0, 4.0`
- int: `2, 3, 4`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<OffGun1Head>d__27` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<OffGun1Static>d__26` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<OnGun1Static>d__28` — 

- method đọc được: **6**, có hằng số: **1**
- float: `2.0`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<RotateObject>d__29` — 

- method đọc được: **6**, có hằng số: **1**
- float: `16.0, 180.0, 360.0`
- int: `2`
- hằng số dùng trong phép tính: `arith:fnmul:16.0`

## `Boss1_Director.<WarningBossAppear>d__15` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.05, 0.5, 1.0, 2.0, 3.0`
- int: `2, 3, 24, 31, 150, 355`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<IEAttackRound1>d__13` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `2, 3`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<IEAttackRound2>d__14` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `2, 3`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<IEAttackRound3>d__15` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `2, 3, 4, 498`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<IEGunAttackArrangePositionX>d__13` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.5, 5.0, 6.0, 180.0`
- int: `2, 3, 4, 8, 16, 312, 503`
- hằng số dùng trong phép tính: `arith:fmul:0.5`

## `Boss_AttackTypes.<IEGunAttackAutoCircle>d__11` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<IEGunAttackAutoCircleBase>d__12` — 

- method đọc được: **6**, có hằng số: **2**
- float: `-0.5, 0.01745, 90.0`
- int: `2, 3, 4, 8, 16, 144, 312, 503`
- hằng số dùng trong phép tính: `arith:fadd:-0.5, arith:fmul:0.01745`

## `Boss_AttackTypes.<IEGunAttackFixed>d__10` — 

- method đọc được: **6**, có hằng số: **1**
- float: `6.0`
- int: `2, 3, 4, 8, 16, 312, 507`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<IEGunAttackRandomPositionX>d__14` — 

- method đọc được: **6**, có hằng số: **1**
- float: `-0.03141, 180.0`
- int: `2, 3, 4, 8, 16, 312, 507`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<IEGunCheckAttack>d__9` — 

- method đọc được: **6**, có hằng số: **1**
- float: `-6.0, -1.0, 1.0, 6.0, 57.29578`
- int: `2, 3, 4, 8, 16, 312, 503`
- hằng số dùng trong phép tính: `arith:fmul:57.29578`

## `Enemy_Display` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **6**, có hằng số: **6**
- float: `0.05, 0.12, 0.5, 1.0`
- int: `3, 4, 257, 4294967295`
- hằng số dùng trong phép tính: `arith:fmul:1.0`

## `Enemy_Movement.<IELinearMove>d__37` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.01, 5.0`
- int: `—`
- hằng số dùng trong phép tính: `arith:fmul:0.01`

## `GP_Tutorials.<HideSettings>d__38` — 

- method đọc được: **6**, có hằng số: **2**
- float: `16.0`
- int: `128`
- hằng số dùng trong phép tính: `arith:fmul:16.0`

## `GP_Tutorials.<TutChangeGameSpeed>d__55` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<TutChangeGameSpeedBoss>d__58` — 

- method đọc được: **6**, có hằng số: **1**
- float: `-0.5`
- int: `2`
- hằng số dùng trong phép tính: `arith:fadd:-0.5`

## `GP_Tutorials.<TutDrones>d__48` — 

- method đọc được: **6**, có hằng số: **1**
- float: `3.9`
- int: `2, 3, 4, 8, 80, 88, 328`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<TutLaserSkill>d__60` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<TutMoveFingers>d__40` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.8`
- int: `—`
- hằng số dùng trong phép tính: `arith:fadd:0.8`

## `GP_Tutorials.<TutTalents>d__52` — 

- method đọc được: **6**, có hằng số: **1**
- float: `—`
- int: `2, 5, 7`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<TutTransform>d__42` — 

- method đọc được: **6**, có hằng số: **1**
- float: `0.05, 0.1, 1.0`
- int: `2, 3, 4, 5, 6, 7, 8, 16, 257, 312, 334`
- hằng số dùng trong phép tính: `—`

## `BossAnimationEvents` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **5**, có hằng số: **3**
- float: `0.15`
- int: `8, 30, 3624`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<>c__DisplayClass13_0` — 

- method đọc được: **5**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<>c__DisplayClass14_0` — 

- method đọc được: **5**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass2_0` — 

- method đọc được: **5**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass2_1` — 

- method đọc được: **5**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass2_2` — 

- method đọc được: **5**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass2_3` — 

- method đọc được: **5**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass2_4` — 

- method đọc được: **5**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<>c` — 

- method đọc được: **5**, có hằng số: **4**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Tut_Settings1` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **5**, có hằng số: **4**
- float: `-1.0, 1.0, 6.0, 7.2`
- int: `2, 3, 4, 12, 2139095040`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass142_1` — 

- method đọc được: **4**, có hằng số: **3**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<>c__DisplayClass102_0` — 

- method đọc được: **4**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Stage.<>c` — 

- method đọc được: **4**, có hằng số: **2**
- float: `—`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `Boss1_Director.<>c__DisplayClass25_0` — 

- method đọc được: **4**, có hằng số: **3**
- float: `—`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `DataTutorials` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **4**, có hằng số: **4**
- float: `—`
- int: `2, 3`
- hằng số dùng trong phép tính: `—`

## `Enemy_Get_Datas` — enemy: HP khởi đầu theo prefab (Dictionary dựng ở .cctor)

- method đọc được: **4**, có hằng số: **3**
- float: `-15.0, 0.012, 0.0125, 0.02, 0.05, 0.1, 0.129, 0.168, 0.1689, 0.2, 0.23, 0.3, 0.35, 0.36, 0.369, 0.5, 0.56, 0.68, 0.689, 0.69, 0.89, 1.0, 1.1, 1.2`
- int: `2, 3, 4, 5, 6, 8, 12, 15, 16, 21, 24, 26, 48, 51, 60, 61, 71, 91, 101, 121, 161, 191, 240, 30001`
- hằng số dùng trong phép tính: `arith:fadd:-15.0, arith:fadd:0.2, arith:fadd:0.3, arith:fadd:0.36, arith:fadd:0.5, arith:fadd:1.0, arith:fadd:1.2, arith:fadd:1.335, arith:fadd:2.5, arith:fadd:5.69, arith:fdiv:1.89, arith:fdiv:2.3, arith:fdiv:12.0, arith:fdiv:15.0, arith:fmul:0.012, arith:fmul:0.0125, arith:fmul:0.02, arith:fmul:0.05, arith:fmul:0.129, arith:fmul:0.168, arith:fmul:0.1689, arith:fmul:0.23, arith:fmul:0.35, arith:fmul:0.5`

## `Enemy_Health` — enemy runtime: armor/noDamage, nhận damage

- method đọc được: **4**, có hằng số: **1**
- float: `2.0, 100.0`
- int: `—`
- hằng số dùng trong phép tính: `arith:fsub:2.0`

## `GP_Tutorials.<>c__DisplayClass39_0` — 

- method đọc được: **4**, có hằng số: **3**
- float: `5.0`
- int: `2`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass144_1` — 

- method đọc được: **3**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<>c__DisplayClass147_1` — 

- method đọc được: **3**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<>c` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<>c__DisplayClass97_1` — 

- method đọc được: **3**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `BossSpineEventHandler` — animation control: event, state, phase or movement (pending asm verification)

- method đọc được: **3**, có hằng số: **3**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass10_0` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass12_0` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass13_0` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass14_0` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackTypes.<>c__DisplayClass9_0` — 

- method đọc được: **3**, có hằng số: **2**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Enemy_Rotate` — enemy appear/death/callback control — pending native verification

- method đọc được: **3**, có hằng số: **2**
- float: `2.0, 80.0`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass123_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<>c__DisplayClass88_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `3`
- hằng số dùng trong phép tính: `—`

## `Boss_AttackPhases.<>c__DisplayClass12_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `3, 4, 8, 16, 312`
- hằng số dùng trong phép tính: `—`

## `Enemy_Appear` — enemy appear/death/callback control — pending native verification

- method đọc được: **2**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<>c__DisplayClass40_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<>c__DisplayClass55_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `GP_Tutorials.<>c__DisplayClass58_0` — 

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Tut_Settings` — early-stage UI/tutorial gates — pending native verification

- method đọc được: **2**, có hằng số: **1**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Endgame.<>c__DisplayClass144_0` — 

- method đọc được: **1**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Home.<>c__DisplayClass147_0` — 

- method đọc được: **1**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Board_Maps.<>c__DisplayClass97_0` — 

- method đọc được: **1**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## `Player_Datas` — dữ liệu runtime của player

- method đọc được: **1**, có hằng số: **0**
- float: `—`
- int: `—`
- hằng số dùng trong phép tính: `—`

## Đọc tiếp

- Mỗi class có file JSON: `reverse-engineering/raw/il2cpp-consts/<Class>.json`
  (từng method, từng hằng số, kèm địa chỉ).
- Disassembly có chú thích: `<Class>.asm.txt`.
- Hằng số chỉ có nghĩa khi đọc cùng control flow — file `.asm.txt` để đối chiếu.
