# 120 — L3 #17 bounded controller-schema replication — `arena/a5a74747-windwings-space-shooter-game-p`

**Status: REPLICATION · PARTIAL native serializer-sequence cross-check.** This report does **not** claim independent schema discovery or close #17. It follows claim comment **6414045217** and is intentionally narrower than the claimed bounded audit because the primary XAPK could not be retrieved in this sandbox.

## Result in one line

Two bounded AArch64 code windows preserved by AI-1 contain the same ordered references to the native string literals `m_InterruptionSource` → `m_OrderedInterruption` → `m_CanTransitionToSelf`, followed by calls to the respective same helper target within each path. I independently decoded those retained instruction bytes and literal-address calculations. This is a replication of a small native serialization sequence, **not** a recovered Unity TypeTree, owning-class identity, full field schema, or runtime readback.

## Provenance and source limits

- Coordination claim: PR12 comment **6414045217** (`REPLICATION #17 tier-2 schema discovery`).
- Pinned upstream raw evidence: `arena/ef6b75ef-windwings-space-shooter-game-p` commit **`72041a1d400be6b0972f5bfa9868efe3befaeca7`**, `reverse-engineering/raw/controller112/probe.json.gz`, SHA-256 **`0b541954d0f96de0b3d0bb08d3dd6382de5b31a9efe97944a814b8e9da2ece51`**.
- That peer artifact records the original XAPK SHA-256 **`f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`** and `libunity.so` SHA-256 **`d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7`** (17,783,496 bytes). These are **pins carried by the peer artifact**, not hashes I recalculated from a local APK.
- Direct `gh release download windwings-apk-1.3.118 -p windwings.xapk` failed with `EOF` at `release-assets.githubusercontent.com`; no local XAPK or `libunity.so` was available. The primary source therefore was not independently re-extracted in this run.
- The peer probe reports query-schema SHA-256 **`56849582948dba56cf4c6baf8924d0b5345349ba9a3cbcd2a4777391a486a9d1`** and explicitly states: “109 shared builtin schema used ONLY to choose search strings, not evidence of APK schema.” The three field names were seeded from that shared search list. Native strings/xrefs corroborate these names in the pinned peer evidence, but do not establish their owning serialized schema.
- This is **shared-evidence REPLICATION**: I did not run or modify AI-1's recovery tool. The compact raw input is retained at `reverse-engineering/raw/l3-controller-schema-replication-17/controller112_probe.json.gz` to make this bounded check reproducible.

## Bounded observations

The builder decodes the retained AArch64 `ADRP` + `ADD` sequences, confirms they resolve to the corresponding string-literal VAs in the same pinned evidence, and decodes the next `BL` target. Raw instruction words from the address setup through each helper call are retained in the output artifact.

| Literal name | Path A: reference → helper call | Path B: reference → helper call | Literal VA |
|---|---|---|---:|
| `m_InterruptionSource` | `0x00b7fcb0` → `0x00b7fccc` → `0x005eb544` | `0x00b851b8` → `0x00b851d4` → `0x005ebf2c` | `0x000f54c4` |
| `m_OrderedInterruption` | `0x00b7fcec` → `0x00b7fd08` → `0x005eb544` | `0x00b85230` → `0x00b8524c` → `0x005ebf2c` | `0x000ddfe9` |
| `m_CanTransitionToSelf` | `0x00b7fd24` → `0x00b7fd3c` → `0x005eb544` | `0x00b85290` → `0x00b852a8` → `0x005ebf2c` | `0x00142855` |

The three literal references occur in the same order in both retained paths. I do **not** label either helper call as read, write, or a particular serializer operation; the excerpt alone does not justify that direction or semantics.

## What this does not establish

- Not a clean-room scan of `libunity.so`; the candidate windows were selected and retained by AI-1's probe.
- Not an independent discovery of the controller TypeTree. No complete type tree, owning class, field types/widths, serialized field order, or offsets are claimed.
- Not proof these fields belong to a particular controller91 node merely because their names match the shared query list.
- Not Unity readback, runtime state, clip evaluation/interpolation, render, or same-build parity.
- No new screenshot or redraw gate was used.

The schema-discovery layer of #17 therefore remains **OPEN**. This result is only a small corroborating native-sequence replication, and must not be used to mark full #17 complete.

## Reproduction and checks

- Builder: `tools/build_l3_controller_schema_replication_17.py` — standard-library only; verifies the pinned compact input and re-decodes the bounded instructions.
- Focused regression: `tests/test_l3_controller_schema_replication_17.py` — **8 PASS**.
- Combined with the delivered #19 regression: **15 PASS**.
- Deterministic regeneration: `python tools/build_l3_controller_schema_replication_17.py --check` — PASS.
- `git diff --check` — PASS. Protected `datas/PROVENANCE.md`, `datas/boss_anim_events.csv`, and `datas/player_start_stats.json` unchanged. Every added file is below 5 MB.

## SHA-256 pins

| File | SHA-256 |
|---|---|
| `reverse-engineering/raw/l3-controller-schema-replication-17/controller112_probe.json.gz` | `0b541954d0f96de0b3d0bb08d3dd6382de5b31a9efe97944a814b8e9da2ece51` |
| `tools/build_l3_controller_schema_replication_17.py` | `1659289286b0b54ebf03b1db9d130fcce7c47f806f6070947c77e8d50f428b4c` |
| `tests/test_l3_controller_schema_replication_17.py` | `d0bf92dfbeab0fd4f5ee6d02e8faa06001b95f871c5bcbeebfa1c872afa0dd5b` |
| `datas/l3_controller_schema_replication_17.json.gz` | `d1734e5c1d9b3bdb132e807cff08d2957ce9009d84c8631393ed7b6e340eb16f` |

No merge, main push, or self-ACK.
