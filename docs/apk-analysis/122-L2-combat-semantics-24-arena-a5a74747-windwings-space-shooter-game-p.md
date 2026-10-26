# 122 — #24 combat semantics: Board power vs attack damage and rank — REPLICATION — `arena/a5a74747-windwings-space-shooter-game-p`

**Result: bounded static separation, not all-ship closure.** The #20 `Board_Players` arrays are directly read by a display-power method. In the examined `Player_Attack_1` path, the main-cannon damage getter instead reads `Player_Get_Datas.StartMainCannonDamages`; inherited rank gates a separate guarded attack loop. This does not establish repository-wide non-use, actual hit damage, DPS, or TTK.

Claim: PR12 comment **6414447862**. Artifact: `datas/l2_combat_semantics_24.json.gz` (**7,278 bytes**, SHA-256 `33db7386bf6d54251c3f95ac8286965d68aac47abd0535e2be38b2dbcc37487b`). This report is explicitly **REPLICATION** because one bounded `Player_Attack_1` raw recovery is shared from the pinned `arena/ef6b75ef` branch; it is not a clean-room APK extraction.

## 1. The #20 arrays terminate at a display sink in the traced path

The pinned #20 receipt, `datas/l2_basic_attack_array_consumers.json.gz`, binds `Board_Players.allBasicAtk` and `allDeltaAtk` to separate static offsets **0x10** and **0x18**. Its `GetPlayerPower` window reads those arrays, calls `Player_Get_Datas.GetPlayerLevel`, and computes:

```text
basic[i] * (1 + delta[i] * GetPlayerLevel(_indexPlayer))
```

`Board_Players.SetPlayerInfo` calls that method and forwards the result to `textPlayerPower` (instance field **0x40**). This is positive display-path evidence; it does not make the returned string a combat damage value.

## 2. The examined attack path uses a different damage array and getter

The static declaration and initializer bind `Player_Get_Datas.StartMainCannonDamages` to static offset **0x78** (`float[24]`): the declaration is in `dump.cs.gz`; the local native initializer calls `InitializeArray` at `0x14e5e8c`, then stores the resulting array at `0x14e5e9c` to `[static_fields+0x78]`. `GetMainCannonDamage` loads that field at `0x14e3a78`, bounds-checks `playerIndex`, and loads the selected base at `0x14e3a90`.

The examined peer-recovered override `Player_Attack_1.get_GetMainCannonDamage` (`0x147a508`) passes literal argument **0** and tail-branches to `Player_Get_Datas.GetMainCannonDamage` (`0x14e3948`). That getter calls `GetPlayerLevel` after building an argument from `playerIndex + 0x2711`, calls `GetMainCannonStatPercent` (`0x14e3c40`), then combines the base with a level-dependent coefficient. A mode-dependent branch can zero the level term; this receipt does not assign that branch a broader game-mode meaning, and it does not decode the top-tier coefficient table.

In `OnBulletMainCannonCollided` (`0x147c1ac`), the bounded method body obtains a critical multiplier (1 or 2), dispatches the virtual main-cannon damage getter through the vtable slot, multiplies the two values, constructs `Damager`, then follows an indirect receiver dispatch. This shows the callback’s calculation when that body runs; it does **not** by itself prove that every loop iteration emits a bullet, every bullet collides, or the receiver applies the request. No actual HP delta was measured.

## 3. Rank controls a guarded loop in this implementation, not the getter's per-hit input

`Player_Attack.rank` is a base-class field at **0x44**. `Player_Attack_1.SetPlayerRank` writes its argument to that field (`0x147a39c`). `MainCannonAttack` reads the same offset (`0x147b678`): rank **3** selects a loop bound of **2**; rank **4 or greater** selects **4**; other values below 4 return before the loop. The counter is incremented and compared against that bound at `0x147b8ac..0x147b8b4`.

These are guarded iterations through pool/component/setup work and a virtual call—not a measured projectile count, hit count, or damage total. The bounded damage getter override uses literal index **0** and does not read rank; rank affects this method’s iteration bound rather than the traced per-hit getter formula. No all-24 rank rule is inferred.

## 4. Exact scope and evidence boundary

- The #20 Board receipt is from this branch; the attack implementation evidence is **REPLICATION** from peer commit `72041a1d400be6b0972f5bfa9868efe3befaeca7` on `arena/ef6b75ef-windwings-space-shooter-game-p`.
- The peer index identifies XAPK SHA-256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`, arm64 `libil2cpp.so` SHA-256 `9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99`, and metadata SHA-256 `449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69`. The receipt reproduces selected exported instruction windows and checks them against the peer raw index; it does not reopen the APK or native library bytes.
- The copied peer assembly is stored as gzip to preserve the exact source bytes, including trailing spaces. The builder verifies the archive SHA and verifies the decompressed source SHA against the peer index before extracting instruction windows.
- Only one recovered `Player_Attack_1` body is traced. The peer #82 all-24 / 72-getter-callsite argument audit is **not** reproduced here.
- No player-ID/index-to-prefab mapping is added. In particular, this report does not join the #20 selected-board index to a combat ship identity.
- No numeric static/runtime cross-build values from archived phone report 111 are used. No screenshot, redraw, live runtime readback, or DPS/TTK calculation was performed.
- This is not proof that no other consumer or attack implementation uses related values elsewhere.

## Reproduction

```sh
python tools/build_l2_combat_semantics_24.py
python tools/build_l2_combat_semantics_24.py --check
python -m unittest tests.test_l2_combat_semantics_24 -v
```

The builder checks all source hashes, the peer recovery index and decompressed assembly digest, the three peer method boundaries, relevant declarations, the #20 receipt, and the address-qualified instruction windows. The tests include deterministic rebuild and tamper rejection. **8 focused tests PASS**. No protected data file was modified; no merge, `main` push, or self-ACK.

## SHA-256 pins

| Source / artifact | SHA-256 |
|---|---|
| `datas/l2_combat_semantics_24.json.gz` | `33db7386bf6d54251c3f95ac8286965d68aac47abd0535e2be38b2dbcc37487b` |
| `datas/l2_basic_attack_array_consumers.json.gz` | `79d7232db9fcadeb94a9cbe47346c097f87e684d1cf7b55c499b84a3607b90df` |
| `reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt` | `dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001` |
| `reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt` | `aa6ae77306ea48255c2c6ba47c2828b4c5ce6cf8d7be6a27c7ac52241d2df86a` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `reverse-engineering/raw/l2-combat-semantics-24/peer-player-firing-index.json` | `2cec26c92f42b085364d08a46920ff00679b3b1340b0fbbaf75c5693654c2464` |
| `reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.asm.txt.gz` (archive) | `eacd421213aa399fc851ab71c3be2acc310f5b05301e1840303f990ab1fe7545` |
| Peer-index source `reverse-engineering/raw/player-firing/native/Player_Attack_1.asm.txt` (decompressed bytes) | `ebd749901548939bfc0970752f4a9fe65505c5861eeed6788dfac909691a662d` |
| `reverse-engineering/raw/l2-combat-semantics-24/peer-Player_Attack_1.json` | `abca290db8e63b5aaf4ce2237f2c1bba15cd369a6e6c874ea5ff5bb32254efd6` |
| `tools/build_l2_combat_semantics_24.py` | `22ab1ac877c53321d70e39ebca929aa927083bdce88e7bac421b4531999f2db2` |
| `tests/test_l2_combat_semantics_24.py` | `a9453a7892db73ea272a7ba3adf73e499a033d56f5ec0cb5c5d9bbceb871c7f2` |

No runtime receipt or measured attack output is claimed.
