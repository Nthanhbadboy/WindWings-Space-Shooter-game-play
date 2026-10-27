# Game-side static quick wins — StartDroneSkillDamages and MISSING row 13

**Scope:** PR12 round 79 AI-2 quick-win claim (static-only). This report does not enter AI-1's native `libunity.so` FDE lane and makes no new runtime claim.

## 1. `Drone_Get_Datas.StartDroneSkillDamages[12]`

### Static anchors

`reverse-engineering/il2cpp/dump.cs.gz` identifies `Drone_Get_Datas` as TypeDefIndex 291, with `private static float[] StartDroneSkillDamages` at static-field offset `0x28`. It also identifies `Drone_Get_Datas::.cctor` at RVA `0x14DADC4` and `GetDroneSkillDamage(int)` at RVA `0x14D8ED0`. This pins the field and initializer method identity, but the dump contains signatures/addresses rather than method bodies.

A search of the tracked initializer evidence does **not** pin an assignment from that `.cctor` to the named field:

- `reverse-engineering/il2cpp/ia-resolved.json` has no `Drone_Get_Datas.cctor` entry.
- `datas/wing_drone_flow.json` records `Drone_Get_Datas` numeric static stores and the `BaseDamages` static data blob, but no `StartDroneSkillDamages` array allocation / `InitializeArray` call / store edge.
- The native `Drone_Get_Datas` ASM/JSON paths named in that flow file's provenance are not present in this checkout, so the missing edge cannot be recovered from those raw files here.

### Static blob candidate and runtime value comparison

`reverse-engineering/il2cpp/field-defaults.json` contains one `<PrivateImplementationDetails>` field whose 48-byte float payload decodes to the exact vector recorded by the runtime snapshot:

| Index | Static metadata blob candidate (`float32`) | 23-Oct runtime snapshot |
|---:|---:|---:|
| 0 | 556 | 556 |
| 1 | 10000 | 10000 |
| 2 | 5600 | 5600 |
| 3 | 710 | 710 |
| 4 | 1999 | 1999 |
| 5 | 2650 | 2650 |
| 6 | 933 | 933 |
| 7 | 5500 | 5500 |
| 8 | 1085 | 1085 |
| 9 | 7200 | 7200 |
| 10 | 1868 | 1868 |
| 11 | 1199 | 1199 |

The candidate blob is `<PrivateImplementationDetails>.DD31A19166699453D31402C10BFF39162B50017CFF10513C5D8EB0660B8B290A`, `field_index=16951`, `data_index=28712`; its raw field-default record is 56 bytes, of which the first 48 bytes decode as the twelve values above and the trailing eight bytes are zero padding. The machine-readable artifact preserves the raw bytes and decoded values.

**Disposition: `STATIC_BLOB_MATCH / FIELD_INITIALIZER_EDGE_UNPROVEN`.** The candidate is static metadata evidence, and its values match the runtime vector value-for-value. The current tracked evidence does not connect this particular blob to `StartDroneSkillDamages` in `Drone_Get_Datas::.cctor`; therefore this is **not** a confirmed static initializer or static/runtime parity result. Do not cite it as parity until that edge is recovered.

The build boundary also remains explicit: the static analysis inputs identify official package `com.Wind.wings.Space.Shooter` **1.3.118 / versionCode 312**, XAPK SHA-256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e`; the 23-Oct runtime snapshot is documented as the repackaged mod **1.0.69** on a HUAWEI Mate 20 X. This is a cross-build value comparison, not same-build validation. The runtime JSON is not used as static-source proof.

## 2. MISSING row 13 — plugin/build inventory audit

### What repository evidence establishes

- The IL2CPP dump header enumerates **76 images** (indices 0–75, including `__Generated`). It directly establishes managed metadata images, not a complete list of Unity packages, Android SDKs, native libraries, or enabled build-time plugins.
- Directly visible non-engine/vendor managed images include `spine-unity.dll`; `MaxSdk.Scripts.dll`; `AppsFlyer.dll`; `Facebook.Unity.dll`, `.Settings.dll`, `.Android.dll`; `Firebase.App.dll`, `.Auth.dll`, `.Database.dll`, `.Platform.dll`, `.Messaging.dll`, `.Analytics.dll`; `Google.Play.Games.dll`; `Google.MiniJson.dll`; and `Newtonsoft.Json.dll`. The dump also has many `Unity.Purchasing.*` and `Unity.Services.*` images. The complete 76-image inventory is in the companion JSON artifact.
- The dump contains no `DOTween.dll` image and no `DG.Tweening`/`DOTween` text. `docs/spec/TUNING_KNOBS.md` attributes a 31-value `Ease` enum to DOTween, but that is indirect easing evidence rather than a dump/manifest plugin record. This is a **non-confirmation**, not proof the package was never used: code may be stripped, merged, or represented only indirectly.
- `docs/apk-analysis/01-apk-inventory.json` records the XAPK package/version, min/target SDK 24/36, base APK plus `config.arm64_v8a` split, permissions, and an ARM64 split with 19 `.so` entries. Its archived inventory does not preserve the full Android `AndroidManifest.xml` text or the complete native-library filename list. It is package/split evidence, not a complete Unity plugin manifest.
- The three loader families present in this repository (BepInEx 5, BepInEx 6, MelonLoader) are runtime-probe adapters/tooling. They are not evidence that those loaders ship in the game.
- Unity **2022.3.62f3** and IL2CPP metadata v31 are supported by the existing engine/metadata reports. The tracked evidence does not include Unity project `ProjectSettings`, complete Player Settings, plugin versions/configuration, a complete native plugin inventory, or the build pipeline settings.

### Audit result

Row 13 is correctly still **partial**. A useful evidence-backed managed-image inventory can now be named, and the package/split facts can be bounded. The requested “full plugin list + build configuration” is **not** recoverable from the current dump plus archived package-manifest summary alone. In particular, do not promote the 76 IL2CPP images to “all plugins,” do not count the repo's probe loaders as game plugins, and do not mark DOTween confirmed from this dump. No device/runtime inspection is needed for this audit; the remaining gaps are missing static build/package inputs.

## Provenance and verification

The companion `datas/l3_a5a74747_game_side_static_quickwins.json.gz` records source SHA-256 values, the full IL2CPP image-name list, the candidate bytes/vector, the runtime comparison vector, and explicit evidence-status flags. Main inputs are `dump.cs.gz`, `field-defaults.json`, `ia-resolved.json`, `datas/wing_drone_flow.json`, `docs/apk-analysis/01-apk-inventory.json`, and the archived 23-Oct runtime JSON. No APK was installed or launched, and no runtime probe was performed for this work.
