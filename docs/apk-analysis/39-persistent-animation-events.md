# 39 — Serialized UnityEvent persistent calls (PROVISIONAL)

Quét đệ quy raw typetree hiện có; giữ cả field rỗng. Không suy ra dynamic listener.

```json
{
  "event_fields": 1333,
  "nonempty_fields": 109,
  "persistent_calls": 113,
  "relevant_enemy_boss_fields": 1200,
  "relevant_enemy_boss_calls": 112
}
```

| Owner class | Object | Field | Calls |
|---|---|---|---:|
| Boss20_AttackTypes | Boss-39020 | allDataFixedAttack[5].onDestroy | 1 |
| Boss20_AttackTypes | Boss-39020 | allDataFixedAttack[15].onDestroy | 1 |
| Enemy_Attack_Event | Enemy_Ingame/Body/CanhTrai/3/Gun3/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Enemy_Ingame/Body/CanhTrai/3/Gun3/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Boss-39006/Enemy_Ingame/Body/CanhTrai/3/Gun4/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Boss-39006/Enemy_Ingame/Body/CanhTrai/3/Gun4/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Gun3/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Gun3/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Tab (5)/Boss/Parent_Bosses/Boss 6/Boss 6/CanhTrai/3/Gun4/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Tab (5)/Boss/Parent_Bosses/Boss 6/Boss 6/CanhTrai/3/Gun4/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Boss-39010/Enemy_Ingame/Body/CanhTrai/3/Gun3/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Boss-39010/Enemy_Ingame/Body/CanhTrai/3/Gun3/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Boss-37004/Enemy_Ingame/Body/Head1/Gun332342 | startShootEvent | 1 |
| Enemy_Attack_Event | Boss-37004/Enemy_Ingame/Body/Head1/Gun332342 | stopShootEvent | 1 |
| Enemy_Attack_Event | Gun4/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Gun4/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Attack_Event | Gun3/Gun5/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Attack_Event | Gun3/Gun5/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Movement | CB-30014 | moveEndedEvent | 1 |
| Enemy_Movement | CB-30014 | moveEndedEvent | 1 |
| Enemy_Sync_Attack | Wave_0030/Circlex2/W2-30057/CD-31013/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0030/Circlex2/W2-30057/CD-31013/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/GameObject/W2-30041 (23)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/GameObject/W2-30041 (23)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (2)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (2)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016 (2)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016 (2)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (2)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (2)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | startShootEvent | 3 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | stopShootEvent | 3 |
| Enemy_Sync_Attack | CD-31013/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31013/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31013/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31013/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0030/Circlex2/W2-30057/CD-31013 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0030/Circlex2/W2-30057/CD-31013 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (21)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (21)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | W2-30036/CD-31004/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | W2-30036/CD-31004/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (25)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (25)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0029/W2-30036/CD-31004 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0029/W2-30036/CD-31004 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31007/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31007/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0031/Circlex2/W2-30057 (1)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0031/Circlex2/W2-30057 (1)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (3)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (3)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016 (3)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016 (3)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (3)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (3)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0031/Circlex2/W2-30057 (1)/CD-31015 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0031/Circlex2/W2-30057 (1)/CD-31015 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | W2-30041 (26)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | W2-30041 (26)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0028/W2-30036/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0028/W2-30036/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0020/CD-31016 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (1)/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016 (1)/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0027/W2-30036/CD-31013/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0027/W2-30036/CD-31013/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (24)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (24)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31016/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/CD-31016/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0004/GameObject (2)/CD-31016/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31004/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31004/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | CD-31004/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | CD-31004/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (27)/CD-31015/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0005/W2-30041 (27)/CD-31015/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0034/W2-30043/CD-31013/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Wave_0034/W2-30043/CD-31013/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack | Ship/Body/GunTop/Enemy_Ingame | startShootEvent | 1 |
| Enemy_Sync_Attack | Ship/Body/GunTop/Enemy_Ingame | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss-39003/Enemy_Ingame/Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 2 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss-39003/Enemy_Ingame/Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 2 | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 3 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 3 | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 2 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 2 | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 3 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 3 | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 1 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 1/SungTrai2 [Follower] 1 | stopShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss-39003/Enemy_Ingame/Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 1 | startShootEvent | 1 |
| Enemy_Sync_Attack2 | Boss-39003/Enemy_Ingame/Body/Boss 1/Skeleton/SkeletonUtility-SkeletonRoot/GUN 2/SungPhai2 [Follower] 1 | stopShootEvent | 1 |
| GridLayoutManager | Board_Shop/Parent/Board_BigShop/Parent/ScrollView/ObjectMove/Parent_Cells | onDone | 1 |

## Giới hạn

- UnityEvent chứa m_PersistentCalls inline, không phải asset PPtr riêng cần dereference.
- Mỗi m_Target trong call vẫn là PPtr; raw giữ nguyên method/mode/arguments/call state.
- Không tìm thấy call trong một class không chứng minh game chỉ nối bằng code.
- Class không được export hoặc instance tạo runtime không nằm trong phép đo này.
