# Report 109 — Board_Players attack-array consumer — arena/a5a74747-windwings-space-shooter-game-p

**#20, claimed before investigation:** PR12 claim comment `6411807151`; expected artifact
`datas/l2_basic_attack_array_consumers.json.gz`.

## Conclusion

A real direct consumer is confirmed in the recovered ARM64 body:

- `Board_Players.GetPlayerPower(int _indexPlayer)` — RVA `0x12D5DFC` — loads the two
  **Board_Players** static arrays from offsets `0x10` and `0x18`, reads the indexed float values,
  calls `Player_Get_Datas.GetPlayerLevel` (`0x14E3B20`), and performs the float operation sequence
  `basic[i] × (1 + delta[i] × level)`.
- Its index is `_indexPlayer - this.indexDefault`; the code bounds-checks both arrays before reading.
- `Board_Players.SetPlayerInfo` (`0x12D1048`) calls `GetPlayerPower` at `0x12D13FC`, then sends
  the returned value to the `textPlayerPower` field (instance offset `0x40`). This proves a UI power
  display path; it does **not** establish combat damage, an in-game attack calculation, or a
  rank/balance interpretation.

The field-to-register binding is not inferred from names alone: `dump.cs.gz` declares
`allBasicAtk` at static offset `0x10` and `allDeltaAtk` at `0x18`; `Board_Players.cctor` stores the
first initialized 24-float array at `0x10` and the second at `0x18`; `GetPlayerPower` reads those same
static slots. The initialized arrays also cross-check as `[4640, 5120, …]` and `0.168 × 24`,
respectively. `Board_Drones` is a separate class and its separate 12-entry consumer is not used as
proof here.

**Scope boundary:** this is positive evidence of a direct reader in the recovered `Board_Players`
ARM64 body and its display caller. It does not assert that this is the only reader in all native or
dynamically generated code not represented in the available workspace. It is source/disassembly
evidence, not live runtime readback or a screenshot.

## Pinned evidence

Artifact `datas/l2_basic_attack_array_consumers.json.gz`: **2,717 bytes**, SHA-256
`79d7232db9fcadeb94a9cbe47346c097f87e684d1cf7b55c499b84a3607b90df`. It contains the exact
instruction windows, field/array binding, arithmetic anchors, scope limits, and source SHA pins.
The builder is `tools/verify/l2_basic_attack_array_consumers.py` (SHA-256
`80638e79cedd084e3787f03847fcd5cce5922591bf8e44d8af76a2a40f51100d`).

| Source | SHA-256 |
|---|---|
| `docs/apk-analysis/PHAN_TICH_WINDWINGS_APK.md` | `f799e2a25cb60c9957b29d8c11afd683c289e8c60ae400562e4bf8dec8bcb3bd` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `reverse-engineering/raw/il2cpp-consts/Board_Players.asm.txt` | `dd8e6e492e4e7d5c887088798e1fa43065340f376a1e16bdc5e0e88c99406001` |
| `reverse-engineering/il2cpp/ia-resolved.json` | `2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37` |

The pinned APK identity source note records base APK 1.3.118 / versionCode 312,
SHA-256 `6843e79347f5b0bb68e4a2f9e1b1a3152e31d0875d4821b9928ad5799a95e1e1`. The report generator
uses the committed ARM64/metadata exports; it does not reopen or independently disassemble the APK
bytes.

## Reproduction and tests

```sh
python3 tools/verify/l2_basic_attack_array_consumers.py
python3 -m unittest tests.test_l2_basic_attack_array_consumers -v
```

The test compares the saved artifact byte-for-byte with a fresh deterministic gzip build, checks
source pins and APK identity, validates both float[24] bindings and their initialization, checks the
direct read/level/math anchors and display caller, and guards against claiming runtime evidence or
global absence.

**Validation:** 177 local unit tests PASS. `verify-claims.py --only APKD1 --no-skip` and
`--only AI1 --no-skip` each PASS (76 reports / 107 CSV; 139 asm / 142,136 lines / 142 typetrees /
126 ScriptableObject tables / 42 sheets / 73 datas files). Full `verify-claims.py --no-skip` reports
208 PASS, 1 unrelated FAIL (`RD1`: `docs/spec/README.md` says 0 mismatches, measured 1), 2 SKIP,
0 ERROR. The README was not changed in this task; target needles APKD1 and AI1 are clean.
`tools/raw-audit.py` also reproduces **180 RAW · 3 DOC · 28 CONST / 211**.

**Sync:** updates `DATA_SYNC` and the live `BALANCE` / `MISSING_FOR_NEW_GAME` statements. The prior
report 91 statement that the Board_Players consumer was unresolved is superseded by this recovered
source trace; the remaining unknown is whether/how this displayed power relates to combat damage.

No edit to `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, or
`datas/player_start_stats.json`. No screenshot gate, no merge, no push to `main`, and no self-ACK.
