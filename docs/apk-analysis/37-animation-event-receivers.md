# 37 — Animation event → receiver component (PROVISIONAL)

Method khai báo trên component cùng GameObject với Animator; không dùng match tên toàn game.

```json
{
  "event_uses": 795,
  "candidate_event_uses": 711,
  "unresolved_event_uses": 84,
  "prefab_roots_with_candidates": 23
}
```

Event uses tính mỗi Animator/clip-reference/event; khác 731 event theo clip duy nhất ở report 36.

| Prefab | Component class | Callback | Event uses |
|---|---|---|---:|
| Boss-37001 | Enemy_Passive_Attack | EndShoot | 1 |
| Boss-37001 | Enemy_Passive_Attack | Shoot | 14 |
| Boss-37001 | Gun_Attack | Shoot | 14 |
| Boss-37002 | MiniBoss1_Events | OnAttack1Ended | 2 |
| Boss-37002 | MiniBoss1_Events | OnAttack2Ended | 4 |
| Boss-37018 | BossAnimationEvents | OnStartAttack | 3 |
| Boss-37018 | BossAnimationEvents | OnStateExit | 7 |
| Boss-37018 | BossAnimationEvents | OnStopAttack | 2 |
| Boss-37019 | BossAnimationEvents | OnStateExit | 8 |
| Boss-39003 | Enemy_Sync_Attack2 | EndShoot | 12 |
| Boss-39003 | Enemy_Sync_Attack2 | Shoot | 12 |
| Boss-39004 | Boss5_AnimationEvents | OnAttackEnded | 5 |
| Boss-39004 | Boss5_AnimationEvents | OnDie | 1 |
| Boss-39006 | Boss4_AnimationEvents | OffBigPlasma | 5 |
| Boss-39006 | Boss4_AnimationEvents | OffVibrateInfinity | 3 |
| Boss-39006 | Boss4_AnimationEvents | OnBigPlasma | 5 |
| Boss-39006 | Boss4_AnimationEvents | OnDie | 1 |
| Boss-39006 | Boss4_AnimationEvents | OnEndedDie | 2 |
| Boss-39006 | Boss4_AnimationEvents | OnVibrateInfinity | 3 |
| Boss-39007 | Boss6_AnimationEvents | GunSwordLeftAttack | 1 |
| Boss-39007 | Boss6_AnimationEvents | GunSwordRightAttack | 1 |
| Boss-39007 | Boss6_AnimationEvents | OnAttackEnded | 10 |
| Boss-39007 | Boss6_AnimationEvents | OnDie | 1 |
| Boss-39007 | Boss6_AnimationEvents | OnPunch | 5 |
| Boss-39007 | Boss6_AnimationEvents | OnSpawnSwords | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnAttack2 | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnAttackEnded | 6 |
| Boss-39008 | Boss7_AnimationEvents | OnDie | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnDieFx | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnJumpAppear | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnJumpDown | 4 |
| Boss-39008 | Boss7_AnimationEvents | OnJumpEnded | 2 |
| Boss-39008 | Boss7_AnimationEvents | OnJumpStart | 2 |
| Boss-39008 | Boss7_AnimationEvents | OnStompingLeft | 1 |
| Boss-39008 | Boss7_AnimationEvents | OnStompingRight | 1 |
| Boss-39009 | Boss8_AnimationEvents | Attack4IdleStart | 1 |
| Boss-39009 | Boss8_AnimationEvents | Attack4IdleStop | 1 |
| Boss-39009 | Boss8_AnimationEvents | OnAttackEnded | 9 |
| Boss-39009 | Boss8_AnimationEvents | OnDie | 1 |
| Boss-39009 | Boss8_AnimationEvents | OnDroidStartAttack | 3 |
| Boss-39009 | Boss8_AnimationEvents | OnDroidStopAttack | 1 |
| Boss-39009 | Boss8_AnimationEvents | OnFlashAttack | 2 |
| Boss-39009 | Boss8_AnimationEvents | OnRocketAttack | 2 |
| Boss-39009 | Gun_Attack | ShootDefault | 2 |
| Boss-39010 | Boss4_AnimationEvents | OffBigPlasma | 5 |
| Boss-39010 | Boss4_AnimationEvents | OffVibrateInfinity | 3 |
| Boss-39010 | Boss4_AnimationEvents | OnBigPlasma | 5 |
| Boss-39010 | Boss4_AnimationEvents | OnDie | 1 |
| Boss-39010 | Boss4_AnimationEvents | OnEndedDie | 2 |
| Boss-39010 | Boss4_AnimationEvents | OnVibrateInfinity | 3 |
| Boss-39011 | Boss9_AnimationEvents | AttackCircle | 1 |
| Boss-39011 | Boss9_AnimationEvents | AttackCore | 4 |
| Boss-39011 | Boss9_AnimationEvents | AttackDropDown | 2 |
| Boss-39011 | Boss9_AnimationEvents | AttackHandLeft | 5 |
| Boss-39011 | Boss9_AnimationEvents | AttackHandRight | 5 |
| Boss-39011 | Boss9_AnimationEvents | FireStart | 5 |
| Boss-39011 | Boss9_AnimationEvents | FireStop | 5 |
| Boss-39011 | Boss9_AnimationEvents | OnAnimationEndedEvent | 20 |
| Boss-39011 | Boss9_AnimationEvents | OnStartAttack | 1 |
| Boss-39012 | Boss10_AnimationEvents | AttackCircle | 1 |
| Boss-39012 | Boss10_AnimationEvents | AttackHand1Left | 4 |
| Boss-39012 | Boss10_AnimationEvents | AttackHand1Right | 3 |
| Boss-39012 | Boss10_AnimationEvents | AttackHand5Left | 12 |
| Boss-39012 | Boss10_AnimationEvents | AttackHand5Right | 12 |
| Boss-39012 | Boss10_AnimationEvents | AttackHandLeft | 8 |
| Boss-39012 | Boss10_AnimationEvents | AttackHandRight | 8 |
| Boss-39012 | Boss10_AnimationEvents | KnifeLeft | 3 |
| Boss-39012 | Boss10_AnimationEvents | KnifeRight | 3 |
| Boss-39012 | Boss10_AnimationEvents | On2HandStartAttack | 1 |
| Boss-39012 | Boss10_AnimationEvents | On2HandStopAttack | 1 |
| Boss-39012 | Boss10_AnimationEvents | OnAnimationEndedEvent | 18 |
| Boss-39012 | Boss10_AnimationEvents | StartAttack8 | 1 |
| Boss-39012 | Boss10_AnimationEvents | StartAttack9 | 1 |
| Boss-39012 | Boss10_AnimationEvents | StopAttack8 | 1 |
| Boss-39012 | Boss10_AnimationEvents | StopAttack9 | 1 |
| Boss-39013 | Boss11_AnimationEvents | Attack1HandLeft | 1 |
| Boss-39013 | Boss11_AnimationEvents | Attack1HandRight | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnAnimationEndedEvent | 13 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack3Event | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack41EndEvent | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack41StartEvent | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack4EndEvent | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack4StartEvent | 1 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack5Event | 2 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack78EndEvent | 2 |
| Boss-39013 | Boss11_AnimationEvents | OnCallAttack78StartEvent | 2 |
| Boss-39014 | Boss12_AnimationEvents | Attack12Shoot | 2 |
| Boss-39014 | Boss12_AnimationEvents | Attack1HandLeft | 1 |
| Boss-39014 | Boss12_AnimationEvents | Attack1StartCheckShoot | 1 |
| Boss-39014 | Boss12_AnimationEvents | Attack2HandRight | 1 |
| Boss-39014 | Boss12_AnimationEvents | Attack2StartCheckShoot | 1 |
| Boss-39014 | Boss12_AnimationEvents | Attack3TwoHands | 1 |
| Boss-39014 | Boss12_AnimationEvents | OnAnimationEndedEvent | 16 |
| Boss-39014 | Boss12_AnimationEvents | OnCallAttack4Event | 1 |
| Boss-39014 | Boss12_AnimationEvents | OnCallAttack6Event | 1 |
| Boss-39014 | Boss12_AnimationEvents | OnCallAttack9EndEvent | 1 |
| Boss-39014 | Boss12_AnimationEvents | OnCallAttack9StartEvent | 1 |
| Boss-39015 | Boss15_AnimationEvents | Attack12HandRight | 2 |
| Boss-39015 | Boss15_AnimationEvents | Attack15HandLeft | 2 |
| Boss-39015 | Boss15_AnimationEvents | Attack16TwoHand | 1 |
| Boss-39015 | Boss15_AnimationEvents | Attack1HandLeft | 8 |
| Boss-39015 | Boss15_AnimationEvents | Attack1HandRight | 3 |
| Boss-39015 | Boss15_AnimationEvents | Attack3HandLeft | 3 |
| Boss-39015 | Boss15_AnimationEvents | Attack3HandRight | 2 |
| Boss-39015 | Boss15_AnimationEvents | EndAttack10 | 1 |
| Boss-39015 | Boss15_AnimationEvents | EndAttack2 | 3 |
| Boss-39015 | Boss15_AnimationEvents | EndAttack6 | 1 |
| Boss-39015 | Boss15_AnimationEvents | OnAnimationEndedEvent | 23 |
| Boss-39015 | Boss15_AnimationEvents | OnCallAttack92Event | 1 |
| Boss-39015 | Boss15_AnimationEvents | OnCallAttack9Event | 1 |
| Boss-39015 | Boss15_AnimationEvents | OnDestroyLantern | 1 |
| Boss-39015 | Boss15_AnimationEvents | OnGetPower | 1 |
| Boss-39015 | Boss15_AnimationEvents | StartAttack10 | 1 |
| Boss-39015 | Boss15_AnimationEvents | StartAttack2 | 3 |
| Boss-39015 | Boss15_AnimationEvents | StartAttack6 | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | CallSoundBossAppear | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | CallSoundBossDead | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | CallSoundBossReady | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | CallSoundBreakPlatforms | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAnimationEndedEvent | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack1Left1Event | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack1Left2Event | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack1RightStartEvent | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack1RightStopEvent | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack2CStartEvent | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack2CStopEvent | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnAttack3Event | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | OnDie | 1 |
| Boss-39016 | Boss6_Mini_AnimationEvents | Pool | 1 |
| Boss-39017 | Boss17_AnimationEvents | Attack1HandLeft | 3 |
| Boss-39017 | Boss17_AnimationEvents | Attack2HandRight | 3 |
| Boss-39017 | Boss17_AnimationEvents | Attack3TwoHands | 1 |
| Boss-39017 | Boss17_AnimationEvents | AttackBigBullet | 11 |
| Boss-39017 | Boss17_AnimationEvents | OnAnimationEndedEvent | 9 |
| Boss-39017 | Boss17_AnimationEvents | OnSpawnChilds | 1 |
| Boss-39018 | Boss18_AnimationEvents | Attack1HandLeft | 4 |
| Boss-39018 | Boss18_AnimationEvents | Attack2HandRight | 4 |
| Boss-39018 | Boss18_AnimationEvents | Attack3TwoHands | 3 |
| Boss-39018 | Boss18_AnimationEvents | AttackBigBullet | 1 |
| Boss-39018 | Boss18_AnimationEvents | OnAnimationEndedEvent | 12 |
| Boss-39018 | Boss18_AnimationEvents | OnAttackBomb | 3 |
| Boss-39018 | Boss18_AnimationEvents | OnAttackReflexBullet | 3 |
| Boss-39018 | Boss18_AnimationEvents | OnCallAttack7EndEvent | 1 |
| Boss-39018 | Boss18_AnimationEvents | OnCallAttack7StartEvent | 1 |
| Boss-39018 | Boss18_AnimationEvents | OnCallAttack9EndEvent | 1 |
| Boss-39018 | Boss18_AnimationEvents | OnCallAttack9StartEvent | 1 |
| Boss-39019 | BossAnimationEvents | OnStartAttack | 50 |
| Boss-39019 | BossAnimationEvents | OnStateExit | 15 |
| Boss-39019 | BossAnimationEvents | OnStopAttack | 11 |
| Boss-39020 | BossAnimationEvents | OnStartAttack | 46 |
| Boss-39020 | BossAnimationEvents | OnStateExit | 13 |
| Boss-39020 | BossAnimationEvents | OnStopAttack | 16 |
| Boss-39021 | BossAnimationEvents | OnStartAttack | 41 |
| Boss-39021 | BossAnimationEvents | OnStateExit | 13 |
| Boss-39021 | BossAnimationEvents | OnStopAttack | 21 |
| CB-30040 | Enemy_DestroyAttack | Attack | 2 |

## Giới hạn

- Candidate chưa chứng minh overload phù hợp tham số, receiver enabled hay runtime playback.
- Không tìm được receiver không có nghĩa event vô hiệu: component có thể chưa được export, method có thể kế thừa.
- Không dò method trên object cha/con để gán bừa vào event của Animator.
- Raw giữ PPtr, component path_id, method RVA/signature, event time và tham số.

## Ví dụ cụ thể: Boss-39020

Animator trên GameObject body chứa BossAnimationEvents. Clip `idle1` có
OnStartAttack(string) tại 0.16666667 s (`Attack1-1`), 2 s (`Attack1-2`),
3 s (`Attack1-1`), 5.33333349 s (`Attack1-2`)… `attack2` có `AttackSilk`
tại 2 s. Như vậy tên `idle1` không có nghĩa không gọi bắn.
Đây là clip-local time, không tự đổi sang thời gian trận (speed/transition
có thể thay đổi). Controller còn tham chiếu `idle1` lặp lại; raw giữ nguyên
thứ tự reference, không đếm đó thành hai clip duy nhất.
