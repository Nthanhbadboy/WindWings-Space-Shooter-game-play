# 32 — Kiểm animation enemy/boss (tạm thời)

Nguồn: Animator prefab joins + raw MonoBehaviour fields. Không coi khớp tên là khớp clip.

- 63 prefab root có Animator, 154 instance (lọc CB-/Boss-/MB- + id).
- 1 component có serialized state/animation-name fields.
- Chưa decode Unity keyframe; chưa xác minh state machine transition hoặc runtime playback.
- Raw đối chiếu: `reverse-engineering/raw/animation-audit/enemy-boss.json`.

## State được serialize trực tiếp

| Object | Component source | Fields |
|---|---|---|
| Boss-39002 | Boss1_Director.jsonl.gz | stateAppear=Xuathien; stateRunAway=Baydi; stateDie=Dead; stateAttack1=Attack1; stateAttack2=Attack2; stateAttack3=Attack3; statePreAttack2=Chuyensangattack2; statePreAttack3=Chuyensangattack3 |

## Animator theo prefab

| Prefab | Instances | Controller names (không phải clip) |
|---|---:|---|
| Boss-37001 | 1 | MB-39005 |
| Boss-37002 | 3 | Enemy_Ingame |
| Boss-37003 | 1 | Enemy_Ingame |
| Boss-37004 | 1 | Body 1 |
| Boss-37006 | 2 | Enemy_Ingame, Parent 1 |
| Boss-37009 | 1 | Parent |
| Boss-37010 | 1 | Parent |
| Boss-37011 | 1 | Snake |
| Boss-37012 | 1 | Parent |
| Boss-37013 | 3 | GunR, Parent |
| Boss-37014 | 1 | Parent |
| Boss-37015 | 1 | Parent |
| Boss-37016 | 1 | Parent |
| Boss-37017 | 5 | Parent, Plasma_beam_reflex (2) |
| Boss-37018 | 1 | Body |
| Boss-37019 | 1 | Body |
| Boss-39001 | 4 | Afterburner |
| Boss-39003 | 18 | Rocket, SungTrai2 [Follower] |
| Boss-39004 | 1 | Body |
| Boss-39005 | 3 | BODY, Parent, Plasmagun |
| Boss-39006 | 1 | Body |
| Boss-39007 | 1 | Body |
| Boss-39008 | 1 | Body |
| Boss-39009 | 3 | New, TayPhai |
| Boss-39010 | 1 | Body |
| Boss-39011 | 4 | Boss, Enemy_Ingame, Mini1 |
| Boss-39012 | 1 | Boss 1 |
| Boss-39013 | 1 | Boss |
| Boss-39014 | 1 | Boss |
| Boss-39015 | 1 | Body 2 |
| Boss-39016 | 1 | Body |
| Boss-39017 | 20 | Body, Mini, Wave, Wing |
| Boss-39018 | 1 | Body |
| Boss-39019 | 1 | Body |
| Boss-39020 | 2 | Body, Web |
| Boss-39021 | 1 | Body |
| CB-30001 | 2 | Afterburner |
| CB-30002 | 2 | Afterburner |
| CB-30004 | 2 | Afterburner |
| CB-30005 | 2 | Afterburner |
| CB-30006 | 2 | Afterburner |
| CB-30007 | 2 | Afterburner |
| CB-30008 | 2 | Afterburner |
| CB-30010 | 8 | Afterburner |
| CB-30011 | 2 | Afterburner |
| CB-30012 | 2 | Afterburner |
| CB-30013 | 2 | Afterburner |
| CB-30014 | 2 | Afterburner |
| CB-30017 | 2 | Afterburner, MegaBomb |
| CB-30019 | 2 | Afterburner, MegaBomb |
| CB-30020 | 2 | Afterburner |
| CB-30021 | 2 | Afterburner |
| CB-30022 | 2 | Afterburner |
| CB-30023 | 2 | Afterburner |
| CB-30024 | 2 | Afterburner |
| CB-30025 | 2 | Afterburner |
| CB-30026 | 2 | Afterburner |
| CB-30028 | 2 | Afterburner |
| CB-30038 | 2 | Body |
| CB-30040 | 4 | Afterburner, Enemy_Ingame |
| CB-30058 | 2 | Afterburner |
| CB-30059 | 2 | Afterburner |
| CB-30060 | 2 | Afterburner |

## Script điều khiển tìm thấy trực tiếp trong dump.cs

- `BossSpineEventHandler`: SkeletonAnimation, attackEventName,
  preAttackEffectEventName, UnityEvent onAttack, chargeEffect; methods
  Start/HandleEvent. Có adapter event animation → gameplay trong metadata;
  chưa đọc body nên chưa khẳng định nhánh xử lý/timing cụ thể.
- `Boss_1_Animation` và `Boss1_Director`: giữ các state Spine, callback
  AnimationState_Complete / AnimationState_Event, BossWork(entryName).
  Boss1_Director còn Attack1/2/3, OnGunDie, Defeat và coroutine IEAttack1.
- `Boss1_AnimationEvents`: callback Attack1HandLeft, Attack2HandRight,
  Attack3TwoHands, Attack12Shoot, OnDie; Action fields tương ứng.
  Chưa nối callback với event clip cụ thể.
- `Boss_AttackPhases`: Animator + BossAnimationEvents, StartAttack,
  CallMixAnimation(anim,callback), IEAttackRound1/2/3, OnGunDie.
- `Boss_AttackTypes`: RegisterEvents, coroutine bắn fixed/circle/check/
  arrange/random-X; chứng cứ có tầng điều phối bắn riêng với animation.
- `Enemy_Movement`: FixedUpdate, PathFollow, MovePointToPoint, MoveLinearly,
  waypoint/VertexPath, facingMove/parentRotate. Chuyển động có thể do script;
  không suy ra toàn bộ nằm trong AnimationClip.
- Có hai class `Enemy_Attack` khác namespace; không gộp chúng thành một.

Raw: `raw/animation-audit/script-declarations.json`, giữ declaration và RVA.
Các method `{ }` trong dump là placeholder, **không phải thân hàm rỗng**.
Đã thêm 9 class tiêu biểu vào native exporter; chờ CI để kiểm thân asm.
Coroutine factory chưa đủ: logic theo frame có thể nằm ở MoveNext của các
class compiler-generated, cần export bổ sung trước khi chốt chuỗi pha.
