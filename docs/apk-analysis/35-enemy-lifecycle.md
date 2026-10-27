# 35 — Enemy appearance/death: native lifecycle (PROVISIONAL)

Source: APKPure build under analysis, Actions **39993084480 success**.
Raw asm: Enemy_Appear / Enemy_Destroy / Enemy_Sub / Enemy_Rotate now exported.
Do not use phone Premium-mod runtime values as proof for this build.

## Base Enemy_Appear is synchronous, not an animation implementation

Appear @0x1582108 checks Action argument x1. Non-null: loads delegate target,
instance/method context and tail-jumps at 0x1582120. Null goes to helper
0x110d250 (the exporter identifies as null-exception path by usage; not a noop).
No wait, no animation API, no transform updates in this 32-byte method.
Therefore no serialized fields in the base type do NOT prove that all enemy
appearance visuals are implemented here. Look at overrides and the caller.
Enemy_Controller.Appear ends with virtual dispatch through its appearance
component; do not collapse this call into the base implementation.

## Death events: order is observed

Enemy_Destroy dump fields:
- +0x20 Action onDestroyed
- +0x28 Action<GameObject> onDead

OnDestroyByZeroHp @0x15856cc:
1. If onDead != null, fetch this.gameObject and invoke onDead(gameObject),
   call-site 0x1585724.
2. If onDestroyed != null, invoke at 0x1585744; then enter subsequent item/
   destruction/notification handling. If absent, return at 0x15857e0 path.

This confirms a GameObject-carrying death callback exists. It does NOT alone
prove the delegate is Boss1_Director.OnGunDie. That still requires resolving
registration metadata/interface dispatch from SetHpSource/Attack2/Attack3.
Also OnDestroyByZeroHp is virtual; derived destroy classes may override it.

7 native instruction checks saved by tools/verify/enemy_lifecycle.py, with
source SHA256 in raw/animation-audit/enemy-lifecycle.json.
