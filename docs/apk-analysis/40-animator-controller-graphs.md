# 40 — Enemy/boss Animator graph (PROVISIONAL)

Nguồn ControllerConstant đầy đủ, không suy transition từ m_TOS.

```json
{
  "controllers": 52,
  "prefab_roots": 63,
  "parameters": 303,
  "states": 395,
  "transitions": 357,
  "conditional_transitions": 302
}
```

| Controller path_id | Name | Prefab count | Parameters (name:type-code) | States |
|---|---|---:|---|---:|
| 1805 | GunR | 1 | Action:9 | 2 |
| 1806 | Parent | 1 | Appear:9, Transform1:9, Transform2:9 | 4 |
| 1807 | Body | 1 | Appear:9, Idle1:9, Attack1:9, Attack2:9, Mix2:9, Idle2:9, Attack3:9, Attack4:9, Mix3:9, Idle3:9, Attack5:9, Attack6:9, Attack7:9, Attack8:9, Die:9 | 16 |
| 1808 | Body | 1 | Appear:9, Idle1:9, Idle2:9, Idle3:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Attack6:9, Mix2:9, Attack4.1:9, Die:9 | 14 |
| 1812 | Rocket | 1 | Launch:9, Attack:9 | 2 |
| 1813 | Body | 1 | Appear:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Attack6:9, Mix2:9, Idle1:9, Idle2:9, Idle3:9, Die:9 | 15 |
| 1814 | Body | 2 | Attack2:9, Attack3:9, Die:9, Appear:9, Lite_Appear:9, UIShow:4 | 10 |
| 1815 | Parent | 1 | Setup:9, Appear:9, Die:9, UIShow:4 | 7 |
| 1816 | Plasmagun | 1 | Attack1:9, StartShoot:9, EndShoot:9 | 5 |
| 1817 | BODY | 1 | Attack1:9, PreAttack2:9, Attack2:9, PreAttack3:9, Attack3:9 | 5 |
| 1818 | Body | 1 | Appear:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Attack6:9, Die:9, UIShow:4 | 11 |
| 1819 | Body | 1 | Appear:9, Attack1:9, Attack2:9, Attack3:9, PreAttack4:9, Attack4:9, Attack4.2:9, Attack5:9, Attack6:9, Die:9, UIShow:4 | 18 |
| 1820 | Body | 1 | Appear:9, Idle:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Attack6:9, Attack7:9, Attack8:9, Die:9, Attack9:9, UIShow:4 | 14 |
| 1821 | Body | 1 | Appear:9, Attack2:9, IsMix:4, Jump1:9, Jump3:9, Attack3:9, AttackMix:9, Attack2L:9, Attack2R:9, Die:9, UIShow:4 | 12 |
| 1822 | Body 2 | 1 | Appear:9, Idle:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Transform2:9, Attack6:9, Attack7:9, Attack8:9, Idle2:9, Attack9:9, Attack10:9, Attack11:9, Attack12:9, Transform3:9, Idle3:9, Attack13:9, Attack14:9, Attack15:9, Attack16:9, Die:9, Attack9.2:9, UIShow:4, UIMap:9 | 28 |
| 1823 | Body | 1 | Appear:9, Die:9 | 8 |
| 1824 | Boss | 1 | Attack1:9, Appear:9, Attack4:9, Attack5:9, Attack2:9, Attack3:9, Attack6:9, Die1:9, Die2:9, UIShow:4 | 13 |
| 1825 | Enemy_Ingame | 1 |  | 1 |
| 1826 | Mini1 | 1 | Attack1L:9, Attack1R:9, Attack2L:9, Attack2R:9, Attack3L:9, Attack3R:9, Attack3C:9, Mix1:9, Mix2:9, Mix3:9, Die:9 | 12 |
| 1827 | Boss | 1 | Attack:9, Die:9 | 3 |
| 1828 | Body | 1 | Appear:9, Transform1:9, Attack1:9, Attack2:9, Attack3:9, Mix2:9, Transform2:9, Idle3:9, Hunt:9, CancelHunt:9, Die:9, UIShow:4 | 15 |
| 1829 | Mini | 1 | Attack:9 | 3 |
| 1831 | Wave | 1 | Attack1:9, Attack2:9, Attack3:9, Attack4:9, Attack5:9, Attack6:9, Attack7:9, Attack8:9, Attack9:9 | 10 |
| 1832 | Wing | 1 |  | 1 |
| 1833 | Boss 1 | 1 | Appear:9, Mix1:9, Attack1:9, Attack2:9, Attack3:9, Transform2:9, Transform3:9, Attack4:9, Attack5:9, Attack6:9, Attack7:9, Attack8:9, Attack9:9, Attack10:9, Attack11.0:9, Attack11.1:9, Attack11.2:9, Die:9, UIShow:4 | 20 |
| 1834 | New | 1 | Appear:9, Attack2:9, Attack2.1:9, Attack2.2:9, Attack2HasMix:9, Attack3HasMix:9, Attack3:9, Die:9, Attack4.2:9, Attack4.3:9, Attack4.4:9, UIShow:4 | 18 |
| 1835 | TayPhai | 1 | Attack:9 | 3 |
| 1836 | Boss | 1 | Appear:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Idle1:9, Mix2:9, Idle2:9, Mix3:9, Idle3:9, Attack6:9, Attack7:9, Attack8:9, Attack9:9, Attack10:9, Die:9, UIShow:4 | 18 |
| 1839 | Boss | 1 | Appear:9, Idle:9, Attack1:9, Attack2:9, Attack3:9, Attack4.0:9, Attack4.1:9, Attack4.2:9, Attack4.MixToIdle:9, Attack5:9, Attack6:9, Attack7:9, Die:9, DieEnd:9, UIShow:4 | 16 |
| 1841 | Enemy_Ingame | 2 | Shoot:9 | 2 |
| 1842 | Enemy_Ingame | 1 | Appear:9, Attack1.2:9, Attack2:9, Attack2.0:9, Attack2.1:9, Attack2.2:9, Attack2.3:9, Die:9 | 10 |
| 1843 | Parent | 1 | Appear:9 | 2 |
| 1844 | Enemy_Ingame | 1 |  | 1 |
| 1845 | Parent | 1 | Appear:9 | 3 |
| 1846 | Parent | 1 | Appear:9, Transform:9, ThrowL:9, ThrowR:9, SlideL:9, SlideR:9, Punch:9, UIShow:4 | 14 |
| 1847 | Parent | 1 | Appear:9 | 3 |
| 1848 | Parent | 1 | Appear:9, Attack:9 | 4 |
| 1849 | Body | 1 | Appear:9, Attack1:9, Attack2:9, Attack3:9, Attack4:9, Die:9, Idle:9, Ide2:9, Mix4:9 | 10 |
| 1850 | Parent | 1 | Appear:9, Attack1:9, Attack2:9 | 4 |
| 1851 | Parent | 1 | Appear:9 | 3 |
| 1852 | Snake | 1 | Appear:9 | 2 |
| 1855 | MB-39005 | 1 | Attack1:9, Attack2:9, Attack3:9, Attack4:9 | 5 |
| 1856 | Body 1 | 1 | DrawBack:9, IdleAttack1:9, IdleAttack2:9, Attack1:9, Attack2:9, Appear:9 | 8 |
| 1906 | Body | 1 | Move:9, Idle:9 | 2 |
| 1912 | SungTrai2 [Follower] | 1 | Attack:9, Shoot:9 | 3 |
| 1929 | Enemy_Ingame | 1 | Die:9 | 2 |
| 1933 | Afterburner | 27 |  | 1 |
| 1945 | Web | 1 |  | 1 |
| 1946 | Body | 1 | Appear:9, Idle:9, Attack1:9, Attack2:9, Attack3:9, Die:9, Move:9 | 8 |
| 1956 | Plasma_beam_reflex (2) | 1 |  | 1 |
| 1957 | Parent 1 | 1 |  | 1 |
| 1959 | MegaBomb | 2 |  | 1 |

Parameter type-code giữ numeric gốc; raw có threshold/mode/hasExitTime/default state/speed.
Không có parameter không chứng minh script gọi Play: có thể tự phát default state/exit-time transition.
ClipID được giữ cùng raw blend-node; clip_ref_candidate chưa phải playback trace.
Tập này là 63 prefab theo filter CB-/Boss-/MB-, không đồng nhất roster 109 của nhánh spec.
