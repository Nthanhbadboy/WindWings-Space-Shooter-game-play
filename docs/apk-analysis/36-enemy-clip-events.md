# 36 — Enemy/boss: controller → clip → events (PROVISIONAL)

Nối PPtr local bằng path_id; từ chối path_id trùng. Không dùng khớp tên.

```json
{
  "prefab_roots": 63,
  "animator_instances": 154,
  "statuses": {
    "resolved": 154
  },
  "unique_resolved_clips": 393,
  "unique_clip_events": 731,
  "unique_looping_clips": 87
}
```

## Event timeline theo clip duy nhất

| Clip path_id | Clip | Time (s) | Function | int / float / string |
|---|---|---:|---|---|
| 1009 | Appear | 1.0833333730697632 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1015 | appear | 5.5 | OnStateExit | [0, 0.0, ''] |
| 1016 | attack1 | 1.5333333015441895 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1016 | attack1 | 2.0 | OnStartAttack | [0, 0.0, 'Attack1.3'] |
| 1016 | attack1 | 3.0 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1016 | attack1 | 4.516666889190674 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1016 | attack1 | 5.5 | OnStateExit | [0, 0.0, ''] |
| 1017 | attack2 | 1.0 | OnStartAttack | [0, 0.0, 'Attack1.5'] |
| 1017 | attack2 | 1.5 | OnStartAttack | [0, 0.0, 'Attack1.6'] |
| 1017 | attack2 | 5.5 | OnStateExit | [0, 0.0, ''] |
| 1018 | attack3 | 2.4833333492279053 | OnStartAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 3.3333332538604736 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1018 | attack3 | 4.483333110809326 | OnStopAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 6.133333206176758 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1018 | attack3 | 7.5 | OnStartAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 8.333333015441895 | OnStartAttack | [0, 0.0, 'Attack3.3.2R'] |
| 1018 | attack3 | 9.5 | OnStopAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 11.316666603088379 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1018 | attack3 | 12.316666603088379 | OnStartAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 13.050000190734863 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1018 | attack3 | 14.316666603088379 | OnStopAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 15.933333396911621 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1018 | attack3 | 16.983333587646484 | OnStartAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 17.766666412353516 | OnStartAttack | [0, 0.0, 'Attack3.3.2R'] |
| 1018 | attack3 | 18.983333587646484 | OnStopAttack | [0, 0.0, 'Attack2.1'] |
| 1018 | attack3 | 19.883333206176758 | OnStartAttack | [0, 0.0, 'Attack1.4'] |
| 1018 | attack3 | 20.0 | OnStateExit | [0, 0.0, ''] |
| 1019 | attack4 | 0.9166666865348816 | OnStartAttack | [0, 0.0, 'Attack2.4'] |
| 1019 | attack4 | 8.533333778381348 | OnStopAttack | [0, 0.0, 'Attack2.4'] |
| 1019 | attack4 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1020 | attack5 | 0.5 | OnStartAttack | [0, 0.0, 'Attack3.2'] |
| 1020 | attack5 | 6.0 | OnStartAttack | [0, 0.0, 'Attack3.2'] |
| 1020 | attack5 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1021 | attack6 | 1.0 | OnStartAttack | [0, 0.0, 'Attack3.3.1'] |
| 1021 | attack6 | 2.5 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1021 | attack6 | 3.4833333492279053 | OnStartAttack | [0, 0.0, 'Attack3.3.2R'] |
| 1021 | attack6 | 4.5 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1021 | attack6 | 8.016666412353516 | OnStartAttack | [0, 0.0, 'Attack3.3.2R'] |
| 1021 | attack6 | 9.016666412353516 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1021 | attack6 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1022 | attack7 | 2.049999952316284 | OnStartAttack | [0, 0.0, 'Attack3.4'] |
| 1022 | attack7 | 3.8499999046325684 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1022 | attack7 | 4.883333206176758 | OnStartAttack | [0, 0.0, 'Attack1.3'] |
| 1022 | attack7 | 6.0 | OnStartAttack | [0, 0.0, 'Attack3.3.2L'] |
| 1022 | attack7 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1023 | attack8 | 5.0 | OnStateExit | [0, 0.0, ''] |
| 1024 | chuyen sang dot 2 | 4.0 | OnStateExit | [0, 0.0, ''] |
| 1025 | chuyen sang dot 3 | 4.0 | OnStateExit | [0, 0.0, ''] |
| 1026 | dead | 5.5 | OnStateExit | [0, 0.0, ''] |
| 1027 | idle | 1.0 | OnStartAttack | [0, 0.0, 'Attack1.1'] |
| 1027 | idle | 3.0 | OnStartAttack | [0, 0.0, 'Attack1.2'] |
| 1027 | idle | 4.0 | OnStartAttack | [0, 0.0, 'Attack1.1'] |
| 1027 | idle | 5.5333333015441895 | OnStartAttack | [0, 0.0, 'Attack1.2'] |
| 1027 | idle | 7.0 | OnStartAttack | [0, 0.0, 'Attack1.1'] |
| 1027 | idle | 8.516666412353516 | OnStartAttack | [0, 0.0, 'Attack1.2'] |
| 1027 | idle | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1028 | idle2 | 1.0166666507720947 | OnStartAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 2.0166666507720947 | OnStopAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 2.8499999046325684 | OnStartAttack | [0, 0.0, 'Attack2.3'] |
| 1028 | idle2 | 4.183333396911621 | OnStartAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 4.516666889190674 | OnStopAttack | [0, 0.0, 'Attack2.3'] |
| 1028 | idle2 | 5.183333396911621 | OnStopAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 6.4666666984558105 | OnStartAttack | [0, 0.0, 'Attack2.3'] |
| 1028 | idle2 | 7.5 | OnStartAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 8.016666412353516 | OnStopAttack | [0, 0.0, 'Attack2.3'] |
| 1028 | idle2 | 8.5 | OnStopAttack | [0, 0.0, 'Attack2.2'] |
| 1028 | idle2 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1029 | idle3 | 0.5 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 1.0 | OnStartAttack | [0, 0.0, 'Attack3.1.2'] |
| 1029 | idle3 | 2.0166666507720947 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 3.5166666507720947 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 5.0 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 6.5 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 8.016666412353516 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 9.0 | OnStopAttack | [0, 0.0, 'Attack3.1.2'] |
| 1029 | idle3 | 9.5 | OnStartAttack | [0, 0.0, 'Attack3.1.1'] |
| 1029 | idle3 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1032 | attack1 | 0.0 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 5.0333333015441895 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 10.033333778381348 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 15.050000190734863 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 20.03333282470703 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 25.03333282470703 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 30.049999237060547 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 35.0 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1032 | attack1 | 40.66666793823242 | OnStateExit | [0, 0.0, ''] |
| 1033 | attack2 | 0.5 | OnStartAttack | [0, 0.0, 'Attack1-1.1'] |
| 1033 | attack2 | 1.0333333015441895 | OnStartAttack | [0, 0.0, 'Attack1-4.1'] |
| 1033 | attack2 | 3.049999952316284 | OnStartAttack | [0, 0.0, 'Attack1-4.1'] |
| 1033 | attack2 | 5.083333492279053 | OnStartAttack | [0, 0.0, 'Attack1-4.1'] |
| 1033 | attack2 | 7.5 | OnStateExit | [0, 0.0, ''] |
| 1034 | attack3 | 0.5 | OnStartAttack | [0, 0.0, 'Attack2-3.1'] |
| 1034 | attack3 | 1.5 | OnStartAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 1.6666666269302368 | OnStartAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 2.0 | OnStopAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 2.1666667461395264 | OnStopAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 5.0 | OnStartAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 5.166666507720947 | OnStartAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 5.5 | OnStopAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 5.666666507720947 | OnStopAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 8.5 | OnStartAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 8.666666984558105 | OnStartAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 9.0 | OnStopAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 9.166666984558105 | OnStopAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 11.166666984558105 | OnStartAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 11.333333015441895 | OnStartAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 11.666666984558105 | OnStopAttack | [0, 0.0, 'Attack2-2.2L'] |
| 1034 | attack3 | 11.833333015441895 | OnStopAttack | [0, 0.0, 'Attack2-2.2R'] |
| 1034 | attack3 | 13.0 | OnStateExit | [0, 0.0, ''] |
| 1035 | attack4.1 | 8.0 | OnStateExit | [0, 0.0, ''] |
| 1036 | attack4 | 1.0166666507720947 | OnStartAttack | [0, 0.0, 'Attack2-3.1'] |
| 1036 | attack4 | 7.0333333015441895 | OnStopAttack | [0, 0.0, 'Attack2-3.1'] |
| 1036 | attack4 | 8.0 | OnStateExit | [0, 0.0, ''] |
| 1037 | attack5 | 3.3333332538604736 | OnStartAttack | [0, 0.0, 'Attack3-1.2'] |
| 1037 | attack5 | 7.5 | OnStopAttack | [0, 0.0, 'Attack3-1.2'] |
| 1037 | attack5 | 8.0 | OnStateExit | [0, 0.0, ''] |
| 1038 | attack6 | 1.0 | OnStartAttack | [0, 0.0, 'Attack2-3.1'] |
| 1038 | attack6 | 14.5 | OnStopAttack | [0, 0.0, 'Attack2-3.1'] |
| 1038 | attack6 | 15.0 | OnStateExit | [0, 0.0, ''] |
| 1039 | chuyen sang dot 2 | 4.0 | OnStateExit | [0, 0.0, ''] |
| 1040 | dead | 4.0 | OnStateExit | [0, 0.0, ''] |
| 1041 | idle | 0.3499999940395355 | OnStartAttack | [0, 0.0, 'Attack1-1.1'] |
| 1041 | idle | 1.3666666746139526 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1041 | idle | 2.5 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1041 | idle | 3.0 | OnStopAttack | [0, 0.0, 'Attack1-1.1'] |
| 1041 | idle | 5.5 | OnStopAttack | [0, 0.0, 'Attack1-1.3'] |
| 1041 | idle | 6.016666889190674 | OnStartAttack | [0, 0.0, 'Attack1-1.1'] |
| 1041 | idle | 7.0333333015441895 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1041 | idle | 8.5 | OnStartAttack | [0, 0.0, 'Attack1-1.3'] |
| 1041 | idle | 9.0 | OnStopAttack | [0, 0.0, 'Attack1-1.1'] |
| 1041 | idle | 12.016666412353516 | OnStateExit | [0, 0.0, ''] |
| 1042 | idle2 | 1.0333333015441895 | OnStartAttack | [0, 0.0, 'Attack2-1.1'] |
| 1042 | idle2 | 2.9833333492279053 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 4.016666889190674 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 7.016666889190674 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 8.050000190734863 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 11.0 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 12.033333778381348 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 15.016666412353516 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 16.049999237060547 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 19.049999237060547 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 20.083332061767578 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 23.0 | OnStartAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 24.03333282470703 | OnStopAttack | [0, 0.0, 'Attack1-1.2'] |
| 1042 | idle2 | 25.100000381469727 | OnStopAttack | [0, 0.0, 'Attack2-1.1'] |
| 1042 | idle2 | 27.0 | OnStateExit | [0, 0.0, ''] |
| 1043 | idle3 | 0.5 | OnStartAttack | [0, 0.0, 'Attack3-1.1'] |
| 1043 | idle3 | 3.0 | OnStartAttack | [0, 0.0, 'Attack3-1.1'] |
| 1043 | idle3 | 5.516666889190674 | OnStartAttack | [0, 0.0, 'Attack3-1.1'] |
| 1043 | idle3 | 8.0 | OnStartAttack | [0, 0.0, 'Attack3-1.1'] |
| 1043 | idle3 | 9.5 | OnStateExit | [0, 0.0, ''] |
| 1044 | xuat hien | 7.5 | OnStateExit | [0, 0.0, ''] |
| 1052 | Launch | 0.5 | ShootOut | [0, 0.0, ''] |
| 1053 | attack1 | 2.5833332538604736 | OnStartAttack | [0, 0.0, 'Attack2-2'] |
| 1053 | attack1 | 3.5 | OnStartAttack | [0, 0.0, 'Attack2-1'] |
| 1053 | attack1 | 8.016666412353516 | OnStartAttack | [0, 0.0, 'Attack2-2'] |
| 1053 | attack1 | 8.883333206176758 | OnStartAttack | [0, 0.0, 'Attack2-1'] |
| 1053 | attack1 | 13.316666603088379 | OnStateExit | [0, 0.0, ''] |
| 1054 | attack2 | 2.0 | OnStartAttack | [0, 0.0, 'AttackSilk'] |
| 1054 | attack2 | 9.0 | OnStateExit | [0, 0.0, ''] |
| 1055 | attack3 | 1.0 | OnStartAttack | [0, 0.0, '2Attack2-1'] |
| 1055 | attack3 | 3.5 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 3.8333332538604736 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 4.333333492279053 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 4.666666507720947 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 5.166666507720947 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 5.499999523162842 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 6.5 | OnStartAttack | [0, 0.0, '2Attack2-1'] |
| 1055 | attack3 | 8.5 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 8.833333015441895 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 9.333333969116211 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 9.666666030883789 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 10.166666030883789 | OnStartAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 10.5 | OnStopAttack | [0, 0.0, '2Attack2-2'] |
| 1055 | attack3 | 11.683333396911621 | OnStartAttack | [0, 0.0, '2Attack2-1'] |
| 1055 | attack3 | 13.316666603088379 | OnStateExit | [0, 0.0, ''] |
| 1056 | attack4 | 0.9833333492279053 | OnStartAttack | [0, 0.0, '2Attack3-1'] |
| 1056 | attack4 | 2.0333333015441895 | OnStartAttack | [0, 0.0, '2Attack3-2'] |
| 1056 | attack4 | 6.0333333015441895 | OnStartAttack | [0, 0.0, '2Attack3-2'] |
| 1056 | attack4 | 8.016666412353516 | OnStopAttack | [0, 0.0, '2Attack3-1'] |
| 1056 | attack4 | 9.0 | OnStateExit | [0, 0.0, ''] |
| 1057 | attack5 | 3.0166666507720947 | OnStartAttack | [0, 0.0, '3Attack1-2'] |
| 1057 | attack5 | 8.0 | OnStopAttack | [0, 0.0, '3Attack2-3'] |
| 1057 | attack5 | 8.0 | OnStateExit | [0, 0.0, ''] |
| 1058 | attack6 | 2.0333333015441895 | OnStartAttack | [0, 0.0, '3Attack3-1'] |
| 1058 | attack6 | 4.983333110809326 | OnStartAttack | [0, 0.0, '3Attack3-1'] |
| 1058 | attack6 | 8.5 | OnStartAttack | [0, 0.0, '3Attack3-1'] |
| 1058 | attack6 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1059 | chuyen sang dot 2 | 6.666666507720947 | OnStateExit | [0, 0.0, ''] |
| 1060 | dead | 4.0 | OnStateExit | [0, 0.0, ''] |
| 1061 | idle1 | 0.1666666716337204 | OnStartAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 1.0 | OnStopAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 2.0 | OnStartAttack | [0, 0.0, 'Attack1-2'] |
| 1061 | idle1 | 3.0 | OnStartAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 3.8333332538604736 | OnStopAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 5.333333492279053 | OnStartAttack | [0, 0.0, 'Attack1-2'] |
| 1061 | idle1 | 6.133333206176758 | OnStartAttack | [0, 0.0, 'Attack1-3'] |
| 1061 | idle1 | 7.150000095367432 | OnStartAttack | [0, 0.0, 'Attack1-2'] |
| 1061 | idle1 | 8.166666984558105 | OnStartAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 8.833333015441895 | OnStopAttack | [0, 0.0, 'Attack1-3'] |
| 1061 | idle1 | 9.0 | OnStopAttack | [0, 0.0, 'Attack1-1'] |
| 1061 | idle1 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1062 | idle2 | 0.1666666716337204 | OnStartAttack | [0, 0.0, '2Attack1-2'] |
| 1062 | idle2 | 0.5 | OnStartAttack | [0, 0.0, 'Attack2-1'] |
| 1062 | idle2 | 3.0 | OnStartAttack | [0, 0.0, '2Attack1-2'] |
| 1062 | idle2 | 3.5166666507720947 | OnStartAttack | [0, 0.0, 'Attack2-1'] |
| 1062 | idle2 | 6.0 | OnStartAttack | [0, 0.0, '2Attack1-2'] |
| 1062 | idle2 | 6.5 | OnStartAttack | [0, 0.0, 'Attack2-1'] |
| 1062 | idle2 | 7.616666793823242 | OnStartAttack | [0, 0.0, '2Attack1-3'] |
| 1062 | idle2 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1063 | idle3 | 1.0333333015441895 | OnStartAttack | [0, 0.0, '3Attack1-1'] |
| 1063 | idle3 | 2.066666603088379 | OnStartAttack | [0, 0.0, '3Attack1-2'] |
| 1063 | idle3 | 6.0 | OnStartAttack | [0, 0.0, 'Attack2-2'] |
| 1063 | idle3 | 7.516666889190674 | OnStartAttack | [0, 0.0, '3Attack1-2'] |
| 1063 | idle3 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1065 | xuat hien | 6.0 | OnStateExit | [0, 0.0, ''] |
| 1066 | Lite_Appear | 0.0 | OnVibrateInfinity | [0, 0.0, ''] |
| 1066 | Lite_Appear | 25.016666412353516 | OffVibrateInfinity | [0, 0.0, ''] |
| 1066 | Lite_Appear | 40.75 | OnBigPlasma | [0, 0.0, ''] |
| 1066 | Lite_Appear | 44.0 | OffBigPlasma | [0, 0.0, ''] |
| 1066 | Lite_Appear | 61.16666793823242 | OnBigPlasma | [0, 0.0, ''] |
| 1066 | Lite_Appear | 65.66666412353516 | OffBigPlasma | [0, 0.0, ''] |
| 1066 | Lite_Appear | 73.16666412353516 | OnEndedDie | [0, 0.0, ''] |
| 1071 | chuyensangattack2 | 20.75 | OnBigPlasma | [0, 0.0, ''] |
| 1071 | chuyensangattack2 | 24.0 | OffBigPlasma | [0, 0.0, ''] |
| 1071 | chuyensangattack2 | 41.16666793823242 | OnBigPlasma | [0, 0.0, ''] |
| 1071 | chuyensangattack2 | 45.66666793823242 | OffBigPlasma | [0, 0.0, ''] |
| 1072 | chuyensangattack3 | 11.0 | OnBigPlasma | [0, 0.0, ''] |
| 1072 | chuyensangattack3 | 16.049999237060547 | OffBigPlasma | [0, 0.0, ''] |
| 1073 | die | 0.0 | OnVibrateInfinity | [0, 0.0, ''] |
| 1073 | die | 8.5 | OnDie | [0, 0.0, ''] |
| 1073 | die | 8.949999809265137 | OffVibrateInfinity | [0, 0.0, ''] |
| 1073 | die | 9.0 | OnEndedDie | [0, 0.0, ''] |
| 1075 | xuathien | 0.0 | OnVibrateInfinity | [0, 0.0, ''] |
| 1075 | xuathien | 24.0 | OffVibrateInfinity | [0, 0.0, ''] |
| 1076 | Die | 1.3333333730697632 | OnBoomBoom | [0, 0.0, ''] |
| 1076 | Die | 1.7999999523162842 | OnDefeat | [0, 0.0, ''] |
| 1078 | Attack | 2.4666666984558105 | OnStartAttack | [0, 0.0, ''] |
| 1078 | Attack | 7.0 | OnEndedAttack | [0, 0.0, ''] |
| 1079 | EndShoot | 2.0999999046325684 | OnEnded | [0, 0.0, ''] |
| 1081 | StartShoot | 3.1666667461395264 | OnShooting | [0, 0.0, ''] |
| 1082 | Xuathien | 0.8333333134651184 | OnAppeared | [0, 0.0, ''] |
| 1091 | Walk | 0.05000000074505806 | OnFoot2 | [0, 0.0, ''] |
| 1091 | Walk | 1.0499999523162842 | OnFoot1 | [0, 0.0, ''] |
| 1091 | Walk | 1.899999976158142 | OnStartWalk | [0, 0.0, ''] |
| 1092 | Xuathien | 0.0 | OnStopMap | [0, 0.0, ''] |
| 1092 | Xuathien | 0.5 | OnFootAll | [0, 0.0, ''] |
| 1092 | Xuathien | 3.5 | OnStartMap | [0, 0.0, ''] |
| 1094 | attack1 | 9.083333015441895 | OnAttackEnded | [0, 0.0, ''] |
| 1095 | attack2 | 10.0 | OnAttackEnded | [0, 0.0, ''] |
| 1096 | attack3 | 8.649999618530273 | OnAttackEnded | [0, 0.0, ''] |
| 1097 | attack4 | 8.649999618530273 | OnAttackEnded | [0, 0.0, ''] |
| 1100 | chuyensangattack6 | 10.0 | OnAttackEnded | [0, 0.0, ''] |
| 1101 | die | 2.5999999046325684 | OnDie | [0, 0.0, ''] |
| 1104 | Dead | 3.0 | OnDie | [0, 0.0, ''] |
| 1108 | attack1 | 4.599999904632568 | OnAttackEnded | [0, 0.0, ''] |
| 1109 | attack2 | 4.0 | OnAttackEnded | [0, 0.0, ''] |
| 1110 | attack3 | 13.300000190734863 | OnAttackEnded | [0, 0.0, ''] |
| 1111 | attack4.2 | 20.575000762939453 | OnAttackEnded | [0, 0.0, ''] |
| 1112 | attack4 | 20.866666793823242 | OnAttackEnded | [0, 0.0, ''] |
| 1113 | attack5 | 3.2666666507720947 | OnPunch | [0, 0.0, ''] |
| 1113 | attack5 | 5.816666603088379 | OnPunch | [0, 0.0, ''] |
| 1113 | attack5 | 8.316666603088379 | OnPunch | [0, 0.0, ''] |
| 1113 | attack5 | 10.800000190734863 | OnPunch | [0, 0.0, ''] |
| 1113 | attack5 | 13.600000381469727 | OnPunch | [0, 0.0, ''] |
| 1113 | attack5 | 18.0 | OnAttackEnded | [0, 0.0, ''] |
| 1114 | attack6 | 0.949999988079071 | GunSwordRightAttack | [0, 0.0, ''] |
| 1114 | attack6 | 2.0333333015441895 | OnAttackEnded | [0, 0.0, ''] |
| 1115 | attack7 | 0.949999988079071 | GunSwordLeftAttack | [0, 0.0, ''] |
| 1115 | attack7 | 1.850000023841858 | OnAttackEnded | [0, 0.0, ''] |
| 1116 | attack8 | 0.6666666865348816 | OnSpawnSwords | [0, 0.0, ''] |
| 1120 | chuyensangattack6 | 1.2833333015441895 | OnAttackEnded | [0, 0.0, ''] |
| 1121 | xuathien | 1.3333333730697632 | OnAttackEnded | [0, 0.0, ''] |
| 1122 | Death | 2.3499999046325684 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1125 | Xuathien | 5.816666603088379 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1126 | attack1 | 2.4833333492279053 | Attack1HandLeft | [0, 0.0, ''] |
| 1126 | attack1 | 2.9833333492279053 | Attack2HandRight | [0, 0.0, ''] |
| 1126 | attack1 | 6.25 | Attack2HandRight | [0, 0.0, ''] |
| 1126 | attack1 | 6.666666507720947 | Attack1HandLeft | [0, 0.0, ''] |
| 1126 | attack1 | 10.283333778381348 | Attack3TwoHands | [0, 0.0, ''] |
| 1126 | attack1 | 13.716666221618652 | Attack1HandLeft | [0, 0.0, ''] |
| 1126 | attack1 | 14.216666221618652 | Attack2HandRight | [0, 0.0, ''] |
| 1126 | attack1 | 17.483333587646484 | Attack2HandRight | [0, 0.0, ''] |
| 1126 | attack1 | 17.899999618530273 | Attack1HandLeft | [0, 0.0, ''] |
| 1126 | attack1 | 21.516666412353516 | Attack3TwoHands | [0, 0.0, ''] |
| 1126 | attack1 | 22.66666603088379 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1127 | attack2 | 8.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1128 | attack3 | 10.800000190734863 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1129 | attack4 | 2.8333332538604736 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1130 | attack5 | 0.5 | OnAttackBomb | [0, 0.0, ''] |
| 1130 | attack5 | 1.4166666269302368 | OnAttackBomb | [0, 0.0, ''] |
| 1130 | attack5 | 2.3333332538604736 | OnAttackBomb | [0, 0.0, ''] |
| 1130 | attack5 | 2.8333332538604736 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1131 | attack6 | 0.4333333373069763 | OnAttackReflexBullet | [0, 0.0, ''] |
| 1131 | attack6 | 1.7666666507720947 | OnAttackReflexBullet | [0, 0.0, ''] |
| 1131 | attack6 | 3.0999999046325684 | OnAttackReflexBullet | [0, 0.0, ''] |
| 1131 | attack6 | 6.599999904632568 | Attack3TwoHands | [0, 0.0, ''] |
| 1131 | attack6 | 8.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1132 | attack7 | 0.5 | OnCallAttack7StartEvent | [0, 0.0, ''] |
| 1132 | attack7 | 5.833333492279053 | OnCallAttack7EndEvent | [0, 0.0, ''] |
| 1132 | attack7 | 6.150000095367432 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1133 | attack8 | 4.25 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1134 | attack9 | 0.5 | OnCallAttack9StartEvent | [0, 0.0, ''] |
| 1134 | attack9 | 7.0 | OnCallAttack9EndEvent | [0, 0.0, ''] |
| 1134 | attack9 | 8.300000190734863 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1135 | idle | 0.5 | AttackBigBullet | [0, 0.0, ''] |
| 1135 | idle | 5.333333492279053 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1136 | Attack2Mix | 2.3333332538604736 | OnAttackEnded | [0, 0.0, ''] |
| 1137 | Dead | 2.5 | OnDieFx | [0, 0.0, ''] |
| 1137 | Dead | 3.0999999046325684 | OnDie | [0, 0.0, ''] |
| 1140 | Xuathien | 0.5833333134651184 | OnJumpAppear | [0, 0.0, ''] |
| 1141 | attack1 | 1.1666666269302368 | OnAttackEnded | [0, 0.0, ''] |
| 1142 | attack2 | 0.75 | OnAttack2 | [0, 0.0, ''] |
| 1142 | attack2 | 1.6333333253860474 | OnAttackEnded | [0, 0.0, ''] |
| 1143 | attack2L | 1.0 | OnStompingLeft | [0, 0.0, ''] |
| 1143 | attack2L | 1.9833333492279053 | OnAttackEnded | [0, 0.0, ''] |
| 1144 | attack2R | 1.0 | OnStompingRight | [0, 0.0, ''] |
| 1144 | attack2R | 1.9833333492279053 | OnAttackEnded | [0, 0.0, ''] |
| 1145 | attack3 | 4.0 | OnAttackEnded | [0, 0.0, ''] |
| 1146 | attacknhay1 | 0.0 | OnJumpStart | [0, 0.0, ''] |
| 1146 | attacknhay1 | 2.0 | OnJumpDown | [0, 0.0, ''] |
| 1146 | attacknhay1 | 2.299999952316284 | OnJumpEnded | [0, 0.0, ''] |
| 1147 | attacknhay3 | 0.0 | OnJumpStart | [0, 0.0, ''] |
| 1147 | attacknhay3 | 2.25 | OnJumpDown | [0, 0.0, ''] |
| 1147 | attacknhay3 | 3.549999952316284 | OnJumpDown | [0, 0.0, ''] |
| 1147 | attacknhay3 | 4.833333492279053 | OnJumpDown | [0, 0.0, ''] |
| 1147 | attacknhay3 | 5.066666603088379 | OnJumpEnded | [0, 0.0, ''] |
| 1148 | Chuyensangdot2 | 2.8499999046325684 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1149 | Chuyensangdot3 | 2.1666667461395264 | OnDestroyLantern | [0, 0.0, ''] |
| 1149 | Chuyensangdot3 | 3.9000000953674316 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1154 | attack1 | 0.6666666865348816 | Attack1HandLeft | [0, 0.0, ''] |
| 1154 | attack1 | 1.9666666984558105 | Attack1HandRight | [0, 0.0, ''] |
| 1154 | attack1 | 2.9000000953674316 | Attack1HandLeft | [0, 0.0, ''] |
| 1154 | attack1 | 3.8333332538604736 | Attack1HandRight | [0, 0.0, ''] |
| 1154 | attack1 | 4.75 | Attack1HandLeft | [0, 0.0, ''] |
| 1154 | attack1 | 5.666666507720947 | Attack1HandRight | [0, 0.0, ''] |
| 1154 | attack1 | 6.616666793823242 | Attack1HandLeft | [0, 0.0, ''] |
| 1154 | attack1 | 8.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1155 | attack10 | 0.6666666865348816 | StartAttack10 | [0, 0.0, ''] |
| 1155 | attack10 | 2.049999952316284 | EndAttack10 | [0, 0.0, ''] |
| 1155 | attack10 | 2.4166667461395264 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1156 | attack11 | 1.0 | OnGetPower | [0, 0.0, ''] |
| 1156 | attack11 | 4.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1157 | attack12 | 0.5 | Attack12HandRight | [0, 0.0, ''] |
| 1157 | attack12 | 1.3166667222976685 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1158 | attack13 | 1.0 | StartAttack2 | [0, 0.0, ''] |
| 1158 | attack13 | 2.5 | EndAttack2 | [0, 0.0, ''] |
| 1158 | attack13 | 2.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1159 | attack14 | 0.7833333611488342 | Attack16TwoHand | [0, 0.0, ''] |
| 1159 | attack14 | 2.383333444595337 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1160 | attack15 | 1.5833333730697632 | Attack15HandLeft | [0, 0.0, ''] |
| 1160 | attack15 | 2.683333396911621 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1161 | attack16 | 1.5833333730697632 | Attack15HandLeft | [0, 0.0, ''] |
| 1161 | attack16 | 2.066666603088379 | Attack12HandRight | [0, 0.0, ''] |
| 1161 | attack16 | 2.866666555404663 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1162 | attack2 | 1.0 | StartAttack2 | [0, 0.0, ''] |
| 1162 | attack2 | 2.5 | EndAttack2 | [0, 0.0, ''] |
| 1162 | attack2 | 3.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1163 | attack3 | 0.7833333611488342 | Attack3HandRight | [0, 0.0, ''] |
| 1163 | attack3 | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1164 | attack4 | 0.800000011920929 | Attack3HandLeft | [0, 0.0, ''] |
| 1164 | attack4 | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1165 | attack5 | 0.7833333611488342 | Attack3HandRight | [0, 0.0, ''] |
| 1165 | attack5 | 1.2666666507720947 | Attack3HandLeft | [0, 0.0, ''] |
| 1165 | attack5 | 1.6333333253860474 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1166 | attack6 | 0.6666666865348816 | StartAttack6 | [0, 0.0, ''] |
| 1166 | attack6 | 4.666666507720947 | EndAttack6 | [0, 0.0, ''] |
| 1166 | attack6 | 5.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1167 | attack7 | 0.7833333611488342 | Attack3HandLeft | [0, 0.0, ''] |
| 1167 | attack7 | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1168 | attack8 | 1.0 | StartAttack2 | [0, 0.0, ''] |
| 1168 | attack8 | 2.5 | EndAttack2 | [0, 0.0, ''] |
| 1168 | attack8 | 3.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1169 | attack9.2 | 0.8333333134651184 | OnCallAttack92Event | [0, 0.0, ''] |
| 1169 | attack9.2 | 1.7999999523162842 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1170 | attack9 | 0.75 | OnCallAttack9Event | [0, 0.0, ''] |
| 1170 | attack9 | 2.133333444595337 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1171 | dead | 2.316666603088379 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1172 | idle | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1173 | idle2 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1174 | idle3 | 0.5 | Attack1HandLeft | [0, 0.0, ''] |
| 1174 | idle3 | 1.0 | Attack1HandLeft | [0, 0.0, ''] |
| 1174 | idle3 | 1.5 | Attack1HandLeft | [0, 0.0, ''] |
| 1174 | idle3 | 2.0 | Attack1HandLeft | [0, 0.0, ''] |
| 1174 | idle3 | 2.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1176 | Attack | 0.9166666865348816 | OnAttack1RightStartEvent | [0, 0.0, ''] |
| 1176 | Attack | 5.616666793823242 | OnAttack1RightStopEvent | [0, 0.0, ''] |
| 1176 | Attack | 6.5333333015441895 | OnAttack1Left1Event | [0, 0.0, ''] |
| 1176 | Attack | 7.333333492279053 | OnAttack1Left2Event | [0, 0.0, ''] |
| 1177 | Attack2 | 0.5 | OnAttack2CStartEvent | [0, 0.0, ''] |
| 1177 | Attack2 | 13.0 | OnAttack2CStopEvent | [0, 0.0, ''] |
| 1178 | Attack3 | 0.46666666865348816 | OnAttack3Event | [0, 0.0, ''] |
| 1179 | Dead | 1.3333333730697632 | CallSoundBossDead | [0, 0.0, ''] |
| 1179 | Dead | 6.449999809265137 | OnDie | [0, 0.0, ''] |
| 1179 | Dead | 7.5 | Pool | [0, 0.0, ''] |
| 1183 | Xuathien | 9.199999809265137 | CallSoundBossAppear | [0, 0.0, ''] |
| 1183 | Xuathien | 12.75 | CallSoundBreakPlatforms | [0, 0.0, ''] |
| 1183 | Xuathien | 14.083333015441895 | CallSoundBossReady | [0, 0.0, ''] |
| 1183 | Xuathien | 15.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1184 | Attack1 | 0.8333333134651184 | AttackHandRight | [0, 0.0, ''] |
| 1184 | Attack1 | 1.6333333253860474 | AttackHandLeft | [0, 0.0, ''] |
| 1184 | Attack1 | 2.683333396911621 | AttackCircle | [0, 0.0, ''] |
| 1184 | Attack1 | 4.133333206176758 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1185 | Attack2 | 0.25 | FireStart | [0, 0.0, ''] |
| 1185 | Attack2 | 1.0666667222976685 | FireStop | [0, 0.0, ''] |
| 1185 | Attack2 | 1.149999976158142 | FireStart | [0, 0.0, ''] |
| 1185 | Attack2 | 2.066666603088379 | FireStop | [0, 0.0, ''] |
| 1185 | Attack2 | 2.1500000953674316 | FireStart | [0, 0.0, ''] |
| 1185 | Attack2 | 3.066666603088379 | FireStop | [0, 0.0, ''] |
| 1185 | Attack2 | 3.1500000953674316 | FireStart | [0, 0.0, ''] |
| 1185 | Attack2 | 4.066666603088379 | FireStop | [0, 0.0, ''] |
| 1185 | Attack2 | 4.150000095367432 | FireStart | [0, 0.0, ''] |
| 1185 | Attack2 | 5.233333110809326 | FireStop | [0, 0.0, ''] |
| 1186 | Attack3 | 0.44999998807907104 | AttackDropDown | [0, 0.0, ''] |
| 1187 | Attack4 | 0.46666666865348816 | AttackHandRight | [0, 0.0, ''] |
| 1188 | Attack5 | 0.44999998807907104 | AttackHandLeft | [0, 0.0, ''] |
| 1189 | Attack6 | 0.6833333373069763 | AttackCore | [0, 0.0, ''] |
| 1189 | Attack6 | 1.6833332777023315 | AttackCore | [0, 0.0, ''] |
| 1189 | Attack6 | 2.683333396911621 | AttackCore | [0, 0.0, ''] |
| 1189 | Attack6 | 3.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1190 | Die1 | 1.3333333730697632 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1192 | Mix | 0.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1195 | Xuathien | 7.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1196 | Xuathien2 | 2.9666666984558105 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1198 | attack1-1 | 1.0 | AttackHandRight | [0, 0.0, ''] |
| 1198 | attack1-1 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1199 | attack1 | 1.0 | AttackHandLeft | [0, 0.0, ''] |
| 1199 | attack1 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1200 | attack2-2 | 1.0 | AttackHandLeft | [0, 0.0, ''] |
| 1200 | attack2-2 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1201 | attack2 | 1.0 | AttackHandRight | [0, 0.0, ''] |
| 1201 | attack2 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1202 | attack3-2 | 1.0 | AttackHandLeft | [0, 0.0, ''] |
| 1202 | attack3-2 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1203 | attack3-3 | 1.0 | AttackHandRight | [0, 0.0, ''] |
| 1203 | attack3-3 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1204 | attack3 | 0.5833333134651184 | AttackDropDown | [0, 0.0, ''] |
| 1204 | attack3 | 2.5 | AttackCore | [0, 0.0, ''] |
| 1204 | attack3 | 3.066666603088379 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1205 | chuyensangattack1 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1206 | chuyensangattack2 | 2.0166666507720947 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1207 | chuyensangattack3 | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1209 | xuathien | 2.1666667461395264 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1210 | Die | 3.1666667461395264 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1211 | Xuathien | 1.9166666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1212 | attack | 0.8333333134651184 | OnStartAttack | [0, 0.0, ''] |
| 1212 | attack | 10.366666793823242 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1213 | Chuyensangdot2 | 3.5166666507720947 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1214 | Chuyensangdot3 | 1.4166666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1217 | Idle2 | 1.5 | OnSpawnChilds | [0, 0.0, ''] |
| 1217 | Idle2 | 5.016666889190674 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1218 | Idle3 | 0.5 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 0.5833333134651184 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 1.0 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 1.0833333730697632 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 1.5 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 1.5833333730697632 | AttackBigBullet | [0, 0.0, ''] |
| 1218 | Idle3 | 3.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1219 | IdleMix2 | 5.016666889190674 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1220 | Attack1 | 1.5833333730697632 | Shoot | [0, 0.0, ''] |
| 1220 | Attack1 | 2.25 | Shoot | [0, 0.0, ''] |
| 1220 | Attack1 | 5.900000095367432 | Shoot | [0, 0.0, ''] |
| 1220 | Attack1 | 8.566666603088379 | Shoot | [0, 0.0, ''] |
| 1220 | Attack1 | 12.066666603088379 | Shoot | [0, 0.0, ''] |
| 1227 | attack1 | 15.949999809265137 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1228 | attack2 | 10.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1229 | attack3 | 10.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1230 | attack4 | 17.53333282470703 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1231 | attack5 | 10.483333587646484 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1232 | attack6 | 12.883333206176758 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1233 | attack7 | 15.166666984558105 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1234 | attack8 | 10.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1235 | attack9 | 16.483333587646484 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1238 | attack1 | 0.6000000238418579 | Attack1HandLeft | [0, 0.0, ''] |
| 1238 | attack1 | 0.9333333373069763 | Attack2HandRight | [0, 0.0, ''] |
| 1238 | attack1 | 1.2666666507720947 | Attack1HandLeft | [0, 0.0, ''] |
| 1238 | attack1 | 1.600000023841858 | Attack2HandRight | [0, 0.0, ''] |
| 1238 | attack1 | 1.9333332777023315 | Attack1HandLeft | [0, 0.0, ''] |
| 1238 | attack1 | 2.2666666507720947 | Attack2HandRight | [0, 0.0, ''] |
| 1238 | attack1 | 2.933333396911621 | Attack3TwoHands | [0, 0.0, ''] |
| 1238 | attack1 | 3.1666667461395264 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1239 | attack2 | 0.4166666567325592 | AttackBigBullet | [0, 0.0, ''] |
| 1239 | attack2 | 0.9166666865348816 | AttackBigBullet | [0, 0.0, ''] |
| 1239 | attack2 | 1.4166666269302368 | AttackBigBullet | [0, 0.0, ''] |
| 1239 | attack2 | 1.9166666269302368 | AttackBigBullet | [0, 0.0, ''] |
| 1239 | attack2 | 2.4166667461395264 | AttackBigBullet | [0, 0.0, ''] |
| 1239 | attack2 | 2.5999999046325684 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1241 | attack3-2 | 0.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1242 | attack3 | 0.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1243 | Chuyensangdot2 | 0.6666666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1244 | Chuyensangdotcuoi | 6.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1245 | Die | 2.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1248 | Xuathien | 3.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1249 | attack1 | 0.36666667461395264 | AttackHand1Left | [0, 0.0, ''] |
| 1249 | attack1 | 0.6499999761581421 | AttackHand1Right | [0, 0.0, ''] |
| 1249 | attack1 | 0.9333333373069763 | AttackHand1Left | [0, 0.0, ''] |
| 1249 | attack1 | 1.2166666984558105 | AttackHand1Right | [0, 0.0, ''] |
| 1249 | attack1 | 1.5 | AttackHand1Left | [0, 0.0, ''] |
| 1249 | attack1 | 1.7666666507720947 | AttackHand1Right | [0, 0.0, ''] |
| 1249 | attack1 | 2.049999952316284 | AttackHand1Left | [0, 0.0, ''] |
| 1249 | attack1 | 2.3333332538604736 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1250 | attack10 | 0.8166666626930237 | KnifeLeft | [0, 0.0, ''] |
| 1250 | attack10 | 1.2000000476837158 | KnifeRight | [0, 0.0, ''] |
| 1250 | attack10 | 1.9833333492279053 | KnifeLeft | [0, 0.0, ''] |
| 1250 | attack10 | 2.366666555404663 | KnifeRight | [0, 0.0, ''] |
| 1250 | attack10 | 3.2666666507720947 | KnifeLeft | [0, 0.0, ''] |
| 1250 | attack10 | 3.6500000953674316 | KnifeRight | [0, 0.0, ''] |
| 1250 | attack10 | 4.516666889190674 | AttackCircle | [0, 0.0, ''] |
| 1250 | attack10 | 5.849999904632568 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1251 | attack11 | 0.3333333432674408 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1252 | attack12.1 | 0.3333333432674408 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1253 | attack12 | 2.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1254 | attack2 | 0.75 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 0.9166666865348816 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.0833333730697632 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.25 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.4166666269302368 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.5833333730697632 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.75 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 1.9166666269302368 | AttackHandLeft | [0, 0.0, ''] |
| 1254 | attack2 | 6.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1255 | attack3 | 0.75 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 0.9166666865348816 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.0833333730697632 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.25 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.4166666269302368 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.5833333730697632 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.75 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 1.9166666269302368 | AttackHandRight | [0, 0.0, ''] |
| 1255 | attack3 | 6.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1256 | attack4 | 9.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1257 | attack5 | 2.5 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 2.8333332538604736 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 3.1666667461395264 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 3.8333332538604736 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 4.166666507720947 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 4.5 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 5.166666507720947 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 5.5 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 5.833333492279053 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 6.5 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 6.833333492279053 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 7.166666507720947 | AttackHand5Left | [0, 0.0, ''] |
| 1257 | attack5 | 8.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1258 | attack6 | 2.5 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 2.8333332538604736 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 3.1666667461395264 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 3.8333332538604736 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 4.166666507720947 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 4.5 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 5.166666507720947 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 5.5 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 5.833333492279053 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 6.5 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 6.833333492279053 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 7.166666507720947 | AttackHand5Right | [0, 0.0, ''] |
| 1258 | attack6 | 8.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1259 | attack7 | 0.9666666388511658 | On2HandStartAttack | [0, 0.0, ''] |
| 1259 | attack7 | 4.800000190734863 | On2HandStopAttack | [0, 0.0, ''] |
| 1259 | attack7 | 6.116666793823242 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1260 | attack8 | 0.6000000238418579 | StartAttack8 | [0, 0.0, ''] |
| 1260 | attack8 | 4.766666889190674 | StopAttack8 | [0, 0.0, ''] |
| 1260 | attack8 | 5.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1261 | attack9 | 0.6333333253860474 | StartAttack9 | [0, 0.0, ''] |
| 1261 | attack9 | 3.299999952316284 | StopAttack9 | [0, 0.0, ''] |
| 1261 | attack9 | 4.483333110809326 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1262 | idle1 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1264 | Chuyensangattack3 | 1.0666667222976685 | OnAttackEnded | [0, 0.0, ''] |
| 1266 | Dead | 2.5 | OnDie | [0, 0.0, ''] |
| 1269 | Bansung2 | 0.1666666716337204 | ShootDefault | [0, 0.0, ''] |
| 1271 | attack2.1 | 0.0 | OnDroidStartAttack | [0, 0.0, ''] |
| 1271 | attack2.1 | 1.5 | OnRocketAttack | [0, 0.0, ''] |
| 1271 | attack2.1 | 8.0 | OnAttackEnded | [0, 0.0, ''] |
| 1275 | attack2.2 | 0.0 | OnDroidStartAttack | [0, 0.0, ''] |
| 1275 | attack2.2 | 1.5 | OnRocketAttack | [0, 0.0, ''] |
| 1275 | attack2.2 | 8.0 | OnAttackEnded | [0, 0.0, ''] |
| 1276 | attack2 | 0.0 | OnDroidStartAttack | [0, 0.0, ''] |
| 1276 | attack2 | 1.0 | OnDroidStopAttack | [0, 0.0, ''] |
| 1276 | attack2 | 6.0 | OnAttackEnded | [0, 0.0, ''] |
| 1277 | attack3 | 1.2000000476837158 | OnFlashAttack | [0, 0.0, ''] |
| 1277 | attack3 | 1.25 | OnAttackEnded | [0, 0.0, ''] |
| 1278 | attack3_1 | 0.6166666746139526 | OnFlashAttack | [0, 0.0, ''] |
| 1278 | attack3_1 | 0.6666666865348816 | OnAttackEnded | [0, 0.0, ''] |
| 1280 | attack4.2 | 6.0 | OnAttackEnded | [0, 0.0, ''] |
| 1281 | attack4.3 | 6.0 | OnAttackEnded | [0, 0.0, ''] |
| 1282 | attack4.4 | 6.0 | OnAttackEnded | [0, 0.0, ''] |
| 1283 | attack4 | 0.0 | Attack4IdleStart | [0, 0.0, ''] |
| 1283 | attack4 | 1.5166666507720947 | Attack4IdleStop | [0, 0.0, ''] |
| 1284 | Die | 2.683333396911621 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1291 | attack1 | 0.44999998807907104 | Attack1HandLeft | [0, 0.0, ''] |
| 1291 | attack1 | 0.8125 | Attack1StartCheckShoot | [0, 0.0, ''] |
| 1291 | attack1 | 1.3125 | Attack12Shoot | [0, 0.0, ''] |
| 1291 | attack1 | 1.6749999523162842 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1292 | attack10 | 2.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1293 | attack2 | 0.44999998807907104 | Attack2HandRight | [0, 0.0, ''] |
| 1293 | attack2 | 0.8125 | Attack2StartCheckShoot | [0, 0.0, ''] |
| 1293 | attack2 | 1.3125 | Attack12Shoot | [0, 0.0, ''] |
| 1293 | attack2 | 1.6749999523162842 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1294 | attack3 | 0.6000000238418579 | Attack3TwoHands | [0, 0.0, ''] |
| 1294 | attack3 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1295 | attack4 | 0.5833333134651184 | OnCallAttack4Event | [0, 0.0, ''] |
| 1295 | attack4 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1296 | attack6 | 0.7833333611488342 | OnCallAttack6Event | [0, 0.0, ''] |
| 1296 | attack6 | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1297 | attack7 | 4.583333492279053 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1298 | attack8 | 5.633333206176758 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1299 | attack9 | 0.8333333134651184 | OnCallAttack9StartEvent | [0, 0.0, ''] |
| 1299 | attack9 | 1.8333333730697632 | OnCallAttack9EndEvent | [0, 0.0, ''] |
| 1299 | attack9 | 2.25 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1300 | chuyensangdot2 | 2.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1301 | chuyensangdot3 | 2.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1302 | idle | 0.8823529481887817 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1303 | idle2 | 0.6666666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1304 | idle3 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1305 | xuathien | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1312 | Xuathien | 1.6666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1313 | attack1 | 0.6666666865348816 | Attack1HandLeft | [0, 0.0, ''] |
| 1313 | attack1 | 0.9166666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1314 | attack2 | 0.6666666865348816 | Attack1HandRight | [0, 0.0, ''] |
| 1314 | attack2 | 0.9166666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1315 | attack3 | 0.6666666865348816 | OnCallAttack3Event | [0, 0.0, ''] |
| 1315 | attack3 | 0.9166666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1316 | attack4-1 | 0.30000001192092896 | OnCallAttack5Event | [0, 0.0, ''] |
| 1316 | attack4-1 | 0.6666666865348816 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1317 | attack4-2 | 0.3333333432674408 | OnCallAttack41StartEvent | [0, 0.0, ''] |
| 1317 | attack4-2 | 7.583333492279053 | OnCallAttack41EndEvent | [0, 0.0, ''] |
| 1317 | attack4-2 | 8.083333015441895 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1318 | attack4-back | 0.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1319 | attack4 | 0.25 | OnCallAttack4StartEvent | [0, 0.0, ''] |
| 1319 | attack4 | 3.8333332538604736 | OnCallAttack4EndEvent | [0, 0.0, ''] |
| 1319 | attack4 | 9.333333015441895 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1320 | attack5 | 0.5 | OnCallAttack5Event | [0, 0.0, ''] |
| 1320 | attack5 | 0.8166666626930237 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1321 | attack6 | 1.5833333730697632 | OnCallAttack78StartEvent | [0, 0.0, ''] |
| 1321 | attack6 | 5.316666603088379 | OnCallAttack78EndEvent | [0, 0.0, ''] |
| 1321 | attack6 | 6.333333492279053 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1322 | attack7 | 1.600000023841858 | OnCallAttack78StartEvent | [0, 0.0, ''] |
| 1322 | attack7 | 5.316666603088379 | OnCallAttack78EndEvent | [0, 0.0, ''] |
| 1322 | attack7 | 6.333333492279053 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1323 | die | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1324 | idle | 1.2333333492279053 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1327 | Attack1.2 | 9.5 | OnAttack1Ended | [0, 0.0, ''] |
| 1328 | Attack1 | 8.0 | OnAttack1Ended | [0, 0.0, ''] |
| 1329 | Attack2.1 | 4.0 | OnAttack2Ended | [0, 0.0, ''] |
| 1330 | Attack2.2 | 3.5 | OnAttack2Ended | [0, 0.0, ''] |
| 1331 | Attack2.3 | 8.0 | OnAttack2Ended | [0, 0.0, ''] |
| 1332 | Attack2 | 8.0 | OnAttack2Ended | [0, 0.0, ''] |
| 1338 | Appear | 1.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1342 | Xuathien | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1347 | Attack3 | 0.5833333134651184 | AttackThrowLeft | [0, 0.0, ''] |
| 1347 | Attack3 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1348 | Attack3R | 0.5833333134651184 | AttackThrowRight | [0, 0.0, ''] |
| 1348 | Attack3R | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1349 | Attack4 | 0.3333333432674408 | AttackSpawnWallLeft | [0, 0.0, ''] |
| 1349 | Attack4 | 0.6666666865348816 | AttackSlideWallLeft | [0, 0.0, ''] |
| 1349 | Attack4 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1350 | Attack5 | 0.3333333432674408 | AttackSpawnWallRight | [0, 0.0, ''] |
| 1350 | Attack5 | 0.6666666865348816 | AttackSlideWallRight | [0, 0.0, ''] |
| 1350 | Attack5 | 1.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1353 | Attack8 | 0.25 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 0.3333333432674408 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 0.4166666567325592 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 0.5 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 0.5833333134651184 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 0.6666666865348816 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 0.75 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 0.8333333134651184 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 0.9166666865348816 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 1.0 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 1.0833333730697632 | AttackHandLeft | [0, 0.0, ''] |
| 1353 | Attack8 | 1.1666666269302368 | AttackHandRight | [0, 0.0, ''] |
| 1353 | Attack8 | 1.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1355 | Transform | 1.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1359 | Xuathien | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1363 | Xuathien | 1.1666666269302368 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1365 | Appear | 2.1666667461395264 | OnStateExit | [0, 0.0, ''] |
| 1366 | Attack1 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1367 | Attack2 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1368 | Attack3 | 10.0 | OnStateExit | [0, 0.0, ''] |
| 1369 | Attack4 | 1.0 | OnStateExit | [0, 0.0, ''] |
| 1370 | Die | 1.0 | OnStateExit | [0, 0.0, ''] |
| 1371 | Idle | 2.0 | OnStateExit | [0, 0.0, ''] |
| 1373 | MixAttack4 | 1.0 | OnStateExit | [0, 0.0, ''] |
| 1375 | Appear | 1.75 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1376 | Attack1 | 3.5 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1377 | Attack2 | 2.8333332538604736 | OnStartAttack | [0, 0.0, ''] |
| 1377 | Attack2 | 3.200000047683716 | OnStartAttack | [0, 0.0, ''] |
| 1377 | Attack2 | 3.616666555404663 | OnStartAttack | [0, 0.0, ''] |
| 1377 | Attack2 | 4.183333396911621 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1379 | Appear | 2.5999999046325684 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1382 | Appear | 0.0 | OnAnimationEndedEvent | [0, 0.0, ''] |
| 1387 | Attack2 | 0.46666666865348816 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 0.9333333373069763 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 1.4166666269302368 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 1.899999976158142 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 2.366666555404663 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 2.866666555404663 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 3.316666603088379 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 3.8499999046325684 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 4.266666889190674 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 4.766666889190674 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 5.2166666984558105 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 5.683333396911621 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 6.166666507720947 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 6.599999904632568 | Shoot | [0, 0.0, ''] |
| 1387 | Attack2 | 6.833333492279053 | EndShoot | [0, 0.0, ''] |
| 1387 | Attack2 | 7.0 | CallAttack2 | [0, 0.0, ''] |
| 1388 | Attack3 | 8.0 | CallAttack2 | [0, 0.0, ''] |
| 1389 | Attack4 | 8.0 | CallAttack2 | [0, 0.0, ''] |
| 1390 | Spawn | 1.6666666269302368 | OnTranslateAttackDone | [0, 0.0, ''] |
| 1397 | xuctuthulai | 0.0 | OnEndTails | [0, 0.0, ''] |
| 1397 | xuctuthulai | 1.8333333730697632 | OnEndAttack | [0, 0.0, ''] |
| 1398 | xuctuxuathien | 1.6666666269302368 | OnStartTails | [0, 0.0, ''] |
| 1398 | xuctuxuathien | 2.0 | OnStartAttack | [0, 0.0, ''] |
| 1477 | Attack | 0.8333333134651184 | Shoot | [0, 0.0, ''] |
| 1477 | Attack | 1.0 | EndShoot | [0, 0.0, ''] |
| 1478 | Shoot | 0.05000000074505806 | Shoot | [0, 0.0, ''] |
| 1478 | Shoot | 0.1666666716337204 | EndShoot | [0, 0.0, ''] |
| 1498 | Die | 1.5 | Attack | [0, 0.0, ''] |
| 1524 | Appear | 1.5 | OnStateExit | [0, 0.0, ''] |
| 1525 | Attack1 | 4.2166666984558105 | OnStateExit | [0, 0.0, ''] |
| 1526 | Attack2 | 11.0 | OnStateExit | [0, 0.0, ''] |
| 1527 | Attack3 | 0.6666666865348816 | OnStartAttack | [0, 0.0, 'Slash'] |
| 1527 | Attack3 | 1.3333333730697632 | OnStateExit | [0, 0.0, ''] |
| 1528 | Die | 5.166666507720947 | OnStateExit | [0, 0.0, ''] |
| 1529 | Idle | 0.8333333134651184 | OnStartAttack | [0, 0.0, 'AutoGun'] |
| 1529 | Idle | 1.3333333730697632 | OnStopAttack | [0, 0.0, 'AutoGun'] |
| 1529 | Idle | 1.6666666269302368 | OnStartAttack | [0, 0.0, 'Rocket'] |
| 1529 | Idle | 1.8333333730697632 | OnStopAttack | [0, 0.0, 'Rocket'] |
| 1529 | Idle | 2.6666667461395264 | OnStateExit | [0, 0.0, ''] |
| 1530 | Move | 1.3333333730697632 | OnStateExit | [0, 0.0, ''] |

## Prefab → controller → clips

| Prefab | Animator | Controller | Clip names |
|---|---:|---|---|
| Boss-37001 | 494213 | MB-39005 | Spawn, Attack1, Attack2, Attack3, Attack4 |
| Boss-37002 | 498808 | Enemy_Ingame | Appear, Shoot |
| Boss-37002 | 499021 | Enemy_Ingame | Appear, Shoot |
| Boss-37002 | 499066 | Enemy_Ingame | Appear, Attack1, PreAttack1, Setup, Attack1.2, Attack2, Attack2.1, Attack2.2, Attack2.3, Die |
| Boss-37003 | 496885 | Enemy_Ingame | Setup |
| Boss-37004 | 493584 | Body 1 | Xuathien, attack1, xuctuxuathien, idlexuctu, xuctuthulai, attack2, idlexuctu2, Setup |
| Boss-37006 | 495921 | Enemy_Ingame | Appear, Shoot |
| Boss-37006 | 498245 | Parent 1 | Magictouch1 |
| Boss-37009 | 498446 | Parent | Appear, Attack1, Attack2, Setup |
| Boss-37010 | 495399 | Parent | Appear, Idle, Setup |
| Boss-37011 | 498167 | Snake | Setup, Appear |
| Boss-37012 | 498447 | Parent | Setup, Appear |
| Boss-37013 | 494622 | GunR | GunIdle, GunAttack |
| Boss-37013 | 495434 | Parent | Idle, Appear, Transform1, Transform2 |
| Boss-37013 | 497168 | GunR | GunIdle, GunAttack |
| Boss-37014 | 496024 | Parent | idle, Appear, Attack1, Attack2, Transform, Setup, Attack3, Attack4, Attack5, Attack3R, Attack6, Attack7, Attack8, UIShow |
| Boss-37015 | 495400 | Parent | Xuathien, idle, Setup |
| Boss-37016 | 496198 | Parent | Xuathien, idle, Setup |
| Boss-37017 | 494162 | Plasma_beam_reflex (2) | Active |
| Boss-37017 | 494458 | Plasma_beam_reflex (2) | Active |
| Boss-37017 | 494957 | Plasma_beam_reflex (2) | Active |
| Boss-37017 | 495061 | Plasma_beam_reflex (2) | Active |
| Boss-37017 | 495458 | Parent | Xuathien, idle, Setup, AttackLaser |
| Boss-37018 | 495831 | Body | Attack1, Idle, Setup, Attack2, Attack3, Die, Appear, Move |
| Boss-37019 | 496564 | Body | Setup, Appear, Idle, Die, Attack1, Attack2, Attack3, Attack4, Idle2, MixAttack4 |
| Boss-39001 | 496466 | Afterburner | idle |
| Boss-39001 | 496748 | Afterburner | idle |
| Boss-39001 | 497224 | Afterburner | idle |
| Boss-39001 | 498764 | Afterburner | idle |
| Boss-39003 | 493892 | Rocket | Launch, Attack |
| Boss-39003 | 495241 | Rocket | Launch, Attack |
| Boss-39003 | 495488 | Rocket | Launch, Attack |
| Boss-39003 | 495917 | Rocket | Launch, Attack |
| Boss-39003 | 496222 | Rocket | Launch, Attack |
| Boss-39003 | 496450 | Rocket | Launch, Attack |
| Boss-39003 | 496751 | Rocket | Launch, Attack |
| Boss-39003 | 497082 | Rocket | Launch, Attack |
| Boss-39003 | 497954 | Rocket | Launch, Attack |
| Boss-39003 | 498054 | Rocket | Launch, Attack |
| Boss-39003 | 498215 | Rocket | Launch, Attack |
| Boss-39003 | 498926 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 498927 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 498928 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 498929 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 498930 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 498931 | SungTrai2 [Follower] | Appear, Attack, Shoot |
| Boss-39003 | 499048 | Rocket | Launch, Attack |
| Boss-39004 | 494919 | Body | xuathien, attack1, attack2, attack3, attack4, attack6, attack5, chuyensangattack6, die, setup, UIShow |
| Boss-39005 | 496209 | Parent | Walk, Idle, Xuathien, Test, Die, Setup, UIShow |
| Boss-39005 | 498136 | BODY | Attack1, ChuyensangAttack2, Attack2, Chuyensangattack3, Attack3 |
| Boss-39005 | 498137 | Plasmagun | Attack, Xuathien, StartShoot, Shooting, EndShoot |
| Boss-39006 | 498280 | Body | xuathien, attack1, chuyensangattack2, attack3, attack2, chuyensangattack3, die, setup, UIShow, Lite_Appear |
| Boss-39007 | 494060 | Body | xuathien, attack1, attack2, attack3, chuyensangattack3, chuyensangattack4, attack4, attack4.2, attack5, attack6, chuyensangattack6, attack7, attack8, attack9, Dead, Setup, UIShow, UILock |
| Boss-39008 | 498020 | Body | Xuathien, attack1, attacknhay1, attack2, attack2L, attack2R, attacknhay3, attack3, Dead, Setup, Attack2Mix, UIShow |
| Boss-39009 | 494343 | New | attack1, attack2, attack3, Xuathien, Chuyensangattack2, attack2.1, attack2.2, Chuyensangattack3, attack3_1, Chuyensangattack4, attack4, Dead, Setup, attack4.1, attack4.2, attack4.3, attack4.4, UIShow |
| Boss-39009 | 497480 | TayPhai | Bansung, Bansung2, SetupR |
| Boss-39009 | 497481 | TayPhai | Bansung, Bansung2, SetupR |
| Boss-39010 | 498281 | Body | xuathien, attack1, chuyensangattack2, attack3, attack2, chuyensangattack3, die, setup, UIShow, Lite_Appear |
| Boss-39011 | 493916 | Enemy_Ingame | lol |
| Boss-39011 | 495787 | Boss | Xuathien, Attack1, Attack2, Attack3, Die1, Attack4, Attack5, Attack6, Die2, Xuathien2, Setup, Mix, UIShow |
| Boss-39011 | 495890 | Mini1 | xuathien, attack1, attack2, chuyensangattack2, attack2-2, attack1-1, chuyensangattack3, attack3, chuyensangattack1, attack3-2, attack3-3, Die |
| Boss-39011 | 496568 | Boss | Xuathien, attack, Die |
| Boss-39012 | 494536 | Boss 1 | Xuathien, attack1, idle1, attack2, attack3, attack4, attack5, attack6, attack7, attack8, attack9, Chuyensangdotcuoi, Chuyensangdot2, attack10, attack11, Die, Setup, attack12, attack12.1, UIShow |
| Boss-39013 | 493593 | Boss | idle, Xuathien, attack1, attack2, attack3, attack4, attack4-1, attack4-back, attack4-2, attack5, attack6, attack7, die, DIEHARD, setup, UIShow |
| Boss-39014 | 497153 | Boss | idle, attack1, attack2, attack3, attack4, chuyensangdot2, idle2, chuyensangdot3, idle3, attack6, attack7, attack8, attack9, attack10, Die, xuathien, Setup, UIShow |
| Boss-39015 | 496407 | Body 2 | XuatHien, idle, attack1, attack2, attack3, attack4, attack5, attack6, attack7, Chuyensangdot2, idle2, attack8, attack9, attack10, attack11, Chuyensangdot3, attack12, idle3, attack13, attack14, attack15, test, dead, attack16, None, attack9.2, UIShow, UIMap |
| Boss-39016 | 497295 | Body | Xuathien, Attack, Attack2, Attack3, Dead, Setup, Dead2, Dead3 |
| Boss-39017 | 494095 | Wing | idle |
| Boss-39017 | 494096 | Wing | idle |
| Boss-39017 | 494408 | Wing | idle |
| Boss-39017 | 494413 | Body | Test, Xuathien, Idle, Chuyensangdot2, Idle2, attack1, attack2, attack3, Chuyensangdot3, Idle3, attack3-1, attack3-2, Dead, IdleMix2, UIShow |
| Boss-39017 | 495306 | Wing | idle |
| Boss-39017 | 495756 | Wing | idle |
| Boss-39017 | 495821 | Wing | idle |
| Boss-39017 | 496075 | Mini | None, Attack1, Attack2 |
| Boss-39017 | 496486 | Wing | idle |
| Boss-39017 | 496611 | Wing | idle |
| Boss-39017 | 497322 | Wave | attack1, attack2, attack3, attack4, attack5, attack6, attack7, attack8, attack9, None |
| Boss-39017 | 497364 | Wing | idle |
| Boss-39017 | 497548 | Wing | idle |
| Boss-39017 | 497941 | Wing | idle |
| Boss-39017 | 497983 | Wing | idle |
| Boss-39017 | 498607 | Wing | idle |
| Boss-39017 | 498758 | Wing | idle |
| Boss-39017 | 498920 | Wing | idle |
| Boss-39017 | 499055 | Wing | idle |
| Boss-39017 | 499176 | Wing | idle |
| Boss-39018 | 493933 | Body | idle, attack1, attack2, attack3, attack4, attack5, attack6, attack7, Xuathien, attack8, Death, None, attack9, UIShow |
| Boss-39019 | 498950 | Body | idle, appear, attack1, attack2, chuyen sang dot 2, idle2, attack3, attack4, chuyen sang dot 3, idle3, attack5, attack6, attack7, attack8, dead, setup |
| Boss-39020 | 495696 | Body | idle1, attack1, attack2, chuyen sang dot 2, idle2, attack3, attack4, idle3, attack5, attack6, dead, xuat hien, setup, idle1 |
| Boss-39020 | 495993 | Web | Web |
| Boss-39021 | 498650 | Body | xuat hien, idle, attack1, attack2, chuyen sang dot 2, attack3, idle2, attack4.1, attack4, idle3, attack5, attack6, dead, Setup |
| CB-30001 | 493605 | Afterburner | idle |
| CB-30001 | 493618 | Afterburner | idle |
| CB-30002 | 493612 | Afterburner | idle |
| CB-30002 | 493637 | Afterburner | idle |
| CB-30004 | 493598 | Afterburner | idle |
| CB-30004 | 493602 | Afterburner | idle |
| CB-30005 | 493595 | Afterburner | idle |
| CB-30005 | 493642 | Afterburner | idle |
| CB-30006 | 493617 | Afterburner | idle |
| CB-30006 | 493651 | Afterburner | idle |
| CB-30007 | 493611 | Afterburner | idle |
| CB-30007 | 493627 | Afterburner | idle |
| CB-30008 | 493599 | Afterburner | idle |
| CB-30008 | 493622 | Afterburner | idle |
| CB-30010 | 493628 | Afterburner | idle |
| CB-30010 | 493634 | Afterburner | idle |
| CB-30010 | 493938 | Afterburner | idle |
| CB-30010 | 493939 | Afterburner | idle |
| CB-30010 | 495499 | Afterburner | idle |
| CB-30010 | 495500 | Afterburner | idle |
| CB-30010 | 498657 | Afterburner | idle |
| CB-30010 | 498658 | Afterburner | idle |
| CB-30011 | 493620 | Afterburner | idle |
| CB-30011 | 493653 | Afterburner | idle |
| CB-30012 | 493630 | Afterburner | idle |
| CB-30012 | 493643 | Afterburner | idle |
| CB-30013 | 493646 | Afterburner | idle |
| CB-30013 | 493649 | Afterburner | idle |
| CB-30014 | 493600 | Afterburner | idle |
| CB-30014 | 493601 | Afterburner | idle |
| CB-30017 | 493603 | Afterburner | idle |
| CB-30017 | 495738 | MegaBomb | attack |
| CB-30019 | 493623 | Afterburner | idle |
| CB-30019 | 495739 | MegaBomb | attack |
| CB-30020 | 493631 | Afterburner | idle |
| CB-30020 | 493645 | Afterburner | idle |
| CB-30021 | 493606 | Afterburner | idle |
| CB-30021 | 493629 | Afterburner | idle |
| CB-30022 | 493597 | Afterburner | idle |
| CB-30022 | 493638 | Afterburner | idle |
| CB-30023 | 493625 | Afterburner | idle |
| CB-30023 | 493648 | Afterburner | idle |
| CB-30024 | 493624 | Afterburner | idle |
| CB-30024 | 493652 | Afterburner | idle |
| CB-30025 | 493626 | Afterburner | idle |
| CB-30025 | 493640 | Afterburner | idle |
| CB-30026 | 493608 | Afterburner | idle |
| CB-30026 | 493610 | Afterburner | idle |
| CB-30028 | 493614 | Afterburner | idle |
| CB-30028 | 493632 | Afterburner | idle |
| CB-30038 | 495355 | Body | Move, Idle |
| CB-30038 | 495356 | Body | Move, Idle |
| CB-30040 | 493609 | Afterburner | idle |
| CB-30040 | 493639 | Afterburner | idle |
| CB-30040 | 494099 | Enemy_Ingame | Idle, Die |
| CB-30040 | 494100 | Enemy_Ingame | Idle, Die |
| CB-30058 | 493619 | Afterburner | idle |
| CB-30058 | 493641 | Afterburner | idle |
| CB-30059 | 493604 | Afterburner | idle |
| CB-30059 | 493644 | Afterburner | idle |
| CB-30060 | 493621 | Afterburner | idle |
| CB-30060 | 493647 | Afterburner | idle |

## Giới hạn

- Danh sách clip thuộc controller không phải transition graph; m_TOS chỉ là bảng tên/hash.
- Event chỉ chứng minh callback được serialize ở mốc clip-time, chưa chứng minh runtime đã phát.
- Chưa nối receiver component trên chính GameObject; chưa suy tên function thành loại đòn.
- Chưa decode transform/float curves; không dựng lại chuyển động từ duration/event.
- Đếm event theo clip path_id duy nhất, không nhân theo số instance dùng chung controller.
- loop đọc từ m_MuscleClip.m_LoopTime, không dùng m_WrapMode làm thay thế.
