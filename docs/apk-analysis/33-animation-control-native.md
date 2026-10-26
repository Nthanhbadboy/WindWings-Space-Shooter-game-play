# 33 — Script điều khiển animation: kiểm thân native (PROVISIONAL)

Nguồn duy nhất: dump.cs + libil2cpp.so tái xuất bởi Actions **39922578757**.
Không chạy game, không suy hình từ screenshot. Raw asm giữ nguyên trong
`reverse-engineering/raw/il2cpp-consts/`; call-site audit tại
`reverse-engineering/raw/animation-audit/native-calls.json`.

## 1. Chuỗi đã chứng minh: Boss1_Director → Boss-39002

Prefab Boss-39002 gắn Boss1_Director (raw Boss1_Director.jsonl.gz).
`Start`: 0x14ff7bc → AnimationState.add_Event, 0x14ff804 → add_Complete.
`SkeletonAnimation_AnimationState_Complete`: 0x14ff9d8 gọi BossWork.
`BossWork` so tên entry bằng String.op_Equality; field offsets đối chiếu dump
và giá trị serialized của prefab:

| So entryName với field | Giá trị prefab | Hành động khi bằng |
|---|---|---|
| +0x28 stateAppear | Xuathien | 0x14ffa0c Attack1; SetAnimation(stateAttack1 +0x40) |
| +0x58 statePreAttack2 | Chuyensangattack2 | 0x14ffa44 Attack2; SetAnimation(stateAttack2 +0x48) |
| +0x60 statePreAttack3 | Chuyensangattack3 | 0x14ffa7c Attack3; SetAnimation(stateAttack3 +0x50) |
| +0x30 / +0x38 | Baydi / Dead | nhánh tail-call Defeat ở 0x14ffae4 |

SetAnimation chung tại 0x14ffaac: w1=0 (track 0), w3=1 (loop=true).
Không suy rằng Attack1→Attack2 tự chuyển chỉ vì tên: trigger chuyển pha khi
mất súng/HP còn phải trace OnGunDie cùng các callback.

## 2. Event Spine → charge FX → gameplay

`BossSpineEventHandler.HandleEvent` @0x1242290:
- Event.Data.Name được so với attackEventName (+0x20), tại 0x12422b8.
- Bằng: chargeEffect (+0x40).SetActive(false), rồi onAttack (+0x38).Invoke.
  Call-sites: 0x12422d0 / tail-call 0x12422e8.
- Không bằng: so với preAttackEffectEventName (+0x28), tại 0x1242300.
- Bằng preAttack: chargeEffect.SetActive(true), tail-call 0x1242320.
- Hai tên cùng bằng thì nhánh attack được ưu tiên (if / else-if).

Đây là cơ chế class; chưa chứng minh mọi boss đều có component này. Tên event
cụ thể phải nối prefab field với Spine timeline, không gán chung 'Shot'.

## 3. Coroutine đã xuất, chưa diễn giải timing hoàn chỉnh

Exporter bổ sung nested compiler-generated types của Boss1_Director,
Boss_AttackPhases, Boss_AttackTypes, Boss_1_Animation và Enemy_Movement.
Audit hiện có **272 method**, trong đó **16 MoveNext**. Float constants chỉ
là evidence: không tự biến 4.0/2.0 thành delay nếu chưa lần tới WaitForSeconds
và yield state tương ứng. Các class generic/indirect calls chưa resolve đầy đủ.

## 4. Việc kế tiếp

1. Trace OnGunDie → chuyển pha, điều kiện số súng/HP và coroutine yield.
2. Nối callback/UnityEvent với gun data và Spine event times, kiểm tên event.
3. Tái kiểm AnimatorController→clip refs/events mới giữ ở exporter.
4. Mở rộng sang các Director khác sau khi hoàn thành chuỗi Boss-39002.

`tools/verify/animation_calls.py` tái sinh audit offline; giữ danh sách candidate
khi nhiều method dùng chung RVA, không cưỡng ép một tên. `b` có thể là nhảy
nội bộ nên chỉ candidate có RVA method mới dùng làm bằng chứng tail-call.
