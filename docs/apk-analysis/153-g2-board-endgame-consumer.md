# Report 153 — G2 `Board_Endgame` constructor array consumer — `arena/a5a74747-windwings-space-shooter-game-p`

**Result: direct consumer bound in recovered ARM64 code.** The `int[10]` initialized by `Board_Endgame.ctor` is the instance field `devidedArenaMedals` at `this+0x2A0`. In `Board_Endgame.SetArenaRewards`, the current `GameMode.arenaRank` selects an element; that element divides `Board_Endgame.arenaPoints`, and a positive quotient is passed as the quantity for item ID 22 to `SetGiftInfo`. This is a source-level consumer binding, not a live reward readback or proof that a reward was applied.

PR12 claim: **6422900026** (queue assignment **6422747515**). Data receipt: [`datas/l2_board_endgame_consumer_g2.json`](../../datas/l2_board_endgame_consumer_g2.json).

## 1. Constructor array → field

The dump declares `private int[] devidedArenaMedals; // 0x2A0` on `Board_Endgame` (`TypeDefIndex 623`). The recovered constructor window allocates an int array with length 10, calls `InitializeArray`, and stores the returned array at `[this+0x2A0]`:

```text
0x12760f4: mov      w1, #0xa
0x12760f8: bl       #0x110d09c
0x12760fc: ldr      x1, [x21]
0x1276100: mov      x2, xzr
0x1276104: mov      x20, x0
0x1276108: bl       #0x205b07c
0x127610c: str      x20, [x19, #0x2a0]
```

`reverse-engineering/il2cpp/ia-resolved.json` joins the initializer at `0x1276108` to the 10-element blob and decodes its int32 values as:

```text
[900, 890, 880, 870, 860, 850, 840, 830, 820, 810]
```

The exact blob bytes are pinned in the JSON receipt. These values alone do not establish their purpose; the consumer below supplies the meaning.

## 2. Direct reader and downstream use

`Board_Endgame.SetArenaRewards` is bounded at RVA `0x1275610` (340 bytes, clean end in the local method index). In this method:

1. It checks `GameMode.playMode == 5` (`0x1275668–0x1275674`) and returns on other values.
2. It loads `Board_Endgame.arenaPoints` from static offset `0x2C` (`0x1275694–0x127569c`) and returns when the value is below 1.
3. It reads `devidedArenaMedals` from the receiver at `this+0x2A0` (`0x12756c0`). `GameMode.arenaRank` at static offset `0x1C` selects the array element; the code checks the index against the array length before loading the int32 (`0x12756d8–0x12756f0`).
4. `sdiv w20, w21, w8` at `0x12756f4` computes signed integer `arenaPoints / devidedArenaMedals[arenaRank]`. If the quotient is below 1, the method skips this gift path.
5. Otherwise it calls `GetNewGift` (`0x1275700`), then calls `SetGiftInfo` (`0x127571c`) with item-ID argument `0x16` (=22) and the quotient as `_number` (`0x127570c–0x1275718`).

The code therefore uses this array as a **per-arena-rank divisor to derive the quantity passed to the arena reward gift path**. The receipt does not identify the broader economy meaning of item ID 22, and does not infer that the reward is a medal solely from the field's misspelled name.

The method-name and class-field bindings come from the local dump; the two relevant type-info slots are qualified by the pinned metadata-slot mapping (`0x2adc840 → GameMode_TypeInfo`, `0x2adc6b0 → Board_Endgame_TypeInfo`). `GameMode.playMode` and `GameMode.arenaRank` are declared at static offsets `0x0` and `0x1C`; `Board_Endgame.arenaPoints` is declared at `0x2C`.

## 3. Evidence scope

- This is positive direct-reader evidence in the recovered `Board_Endgame` method body; it is **not** an exhaustive whole-program cross-reference for all code outside the recovered workspace exports.
- Static disassembly and metadata only. No runtime readback, screenshot, reward grant, or runtime parity is claimed.
- The original APK bytes were not reopened by this receipt. The source is pinned to the workspace exports and their recorded hashes below.
- No native/FDE lane, protected raw source, or runtime-probe workflow was touched.

## Source SHA-256 pins

| Source | SHA-256 |
|---|---|
| `reverse-engineering/raw/il2cpp-consts/Board_Endgame.asm.txt` | `261016b5acf88b30d7fa7ee02d0338a7ec63198e5109c14ad152766c9c4abd7a` |
| `reverse-engineering/raw/il2cpp-consts/Board_Endgame.json` | `04b46de2ca323df8f100dd13b1722fe44caf014c96ce175487c38b9c327f0999` |
| `reverse-engineering/il2cpp/dump.cs.gz` | `e08f23fb6c90e07288e5b202e0ce1e7c5e82a7feb5ccae7aa08aaec3ad166454` |
| `reverse-engineering/il2cpp/ia-resolved.json` | `2583a4c472400fe85f96b96f0a8d2839963eddae95760483424119501d989e37` |
| `reverse-engineering/raw/ui-audit/metadata-slots.json` | `dac076ab3fb5eda6fa2855fb5cee2062124bc821ad1ce78df4e086534059ebc4` |
| `docs/apk-analysis/45-ui-routing-and-persistence.md` (slot-name cross-reference) | `32a6412d4b6ec12ce3ccff0b8523a7661a1f5acedce513139baf8b136a9f72e7` |
| `datas/l2_board_endgame_consumer_g2.json` | `258293f505235eff46e81b0c93c659dc32895d0cb044fb0a999fecbaaf6d7048` |
