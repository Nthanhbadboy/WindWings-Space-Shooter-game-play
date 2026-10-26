# 111 — Independent UnityFS → directory → metadata/controller bytes (arena/ef6b75ef)

**PROVISIONAL, own #17 extension.** Claim/review comment **6413146832**; follows109 payload reader and110 SerializedFile metadata reader. Artifact: `datas/l3_ef6b75ef111_unityfs_framing.json.gz`. Raw: `reverse-engineering/raw/controller111/evidence.json.gz` and `l3-ef6b75ef111-verification/`.

## 1. Scope and what changed

Recovery111 does **not import UnityPy**, its bundle reader, file-name traversal, or codec. It uses pinned stdlib ZIP extraction helper, a separately implemented UnityFS header/block-info/directory reader, and our own LZ4 block decoder (`struct` is its only import). Node paths come directly from original UnityFS directory, not UnityPy's parsed filenames. The two known file identities are selected against those directory paths, not discovered by scanning every node for every possible controller.

Reader implements the source's modern Unity2022.3 layout for versions6/7/8, none/LZ4/LZ4HC; handles block-info at beginning/end and512 padding flag; fails closed for unsupported encryption/codec/layout. Synthetic support is not evidence those variants occur in this APK. Only **v8, LZ4HC, beginning-info, padding flag** are observed here.

**Format-source disclosure:** UnityPy `BundleFile.py` and compression-format helper source were consulted for layout/flag reference before implementation. This is **separate implementation, not clean-room discovery**, and can share mistaken format assumptions with that reference. The LZ4 decoding loop itself is our code, not a call to UnityPy/lz4 package. No claim of independent engine schema discovery.

## 2. Observed original bundle framing

Pinned original `data.unity3d`: SHA-256 `7383563ebe6e42d099bd2348a420146a308f2f14224daf4e4de9ad52845ae4e7`, **63881856bytes**. Parent XAPK SHA-256 `f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e` checked by extraction helper.

| Field | Directly parsed value |
|---|---:|
| signature / format | UnityFS / **8** |
| player / engine strings | `5.x.x` / `2022.3.62f3` |
| flags | **579 =0x243** (LZ4HC info, combined directory, padding) |
| header end / aligned info start |50 /64 |
| compressed / decoded block info |8866 /22633 bytes |
| data start |8944 |
| block descriptors |**2198**, all flags3 |
| directory nodes |**16** |
| total logical decoded stream |**288069498bytes** |
| directory node sizes sum |**288069498bytes** |
| embedded hash literal |16 zero bytes; **not a validated checksum** |

Header alignment and data-start padding are separately accounted for. Physical block sizes consume exactly the remaining bundle bytes; block-info parse consumes exactly its decoded bytes. Signed node ranges checked nonnegative/in bounds/nonoverlap; duplicate/unsafe paths fail. No whole-stream decompression or all-media integrity claim follows from parsing all2198 descriptors.

All16 original node paths/sizes and every block descriptor are in artifact. Two source witnesses:

| Independent directory path | Logical offset | Node size |
|---|---:|---:|
| `resources.assets` |45344150|131740052|
| `sharedassets2.assets` |40641189|196216|

Those node sizes equal original SerializedFile header literals preserved110. Relative object offsets are translated by **directory node offset + SerializedFile absolute byte_start**; do not add node offset twice or confuse a compressed physical offset with logical stream position.

## 3. Actual fresh decoding, not just directory arithmetic

Recovery selects blocks intersecting two complete metadata prefixes and308 controller ranges from110. It decodes each selected block once using our codec, collects exact intersections in logical block order, and compares actual resulting bytes' SHA to preserved110.

- **136 distinct source blocks** actually decoded, compressed size sum **5570422bytes**, output size sum **17825792bytes**.
- Two metadata prefixes: **16949184 +3344 =16952528bytes**, both fresh hashes equal110. Therefore the same complete metadata used to derive704961 object rows is recovered without UnityPy's UnityFS decoder/name reader.
- **308 controller ranges** (285resources +23shared2), all fresh length/hash matches110, which already matched109 original payload bytes.
- This is source equality of recovered byte ranges, not independent schema validation or state/clip runtime execution. The793→791 clip identity joins remain report110's metadata/payload result, not a new runtime result from111.

The rest of2062 block payloads are **not decoded by this recovery**. Full directory framing and declared ranges are parsed, but do not call all288MB decompressed/verified. Original media nodes, full APK/bundle, and the5.57MB selected compressed set are not put in Git.

## 4. What can be replayed locally without APK

Raw envelope preserves original header/compressed block-info/padding bytes, all directory/block descriptors, selected-block compressed/decoded SHA receipts, and fresh-range hashes. Three compressed source samples — block indices **346/347/348**, **131072 decoded bytes each** — lie wholly within a preserved metadata prefix. Their actual compressed bytes are retained; local codec replay is byte-for-byte compared to110 raw metadata (not merely trusted SHA labels).

`Envelope` exposes only captured header/info slices; attempts to read missing payload bytes raise. It does **not fabricate a full63881856-byte source**. Local verifier reparses captured envelope independently, audits exact selected-block coverage/range translation, replays three real codec samples, checks source pins, and regenerates artifact.

**Important limit:** local preserved samples cover **393216 decoded metadata bytes**, not every136 source blocks. Fresh full-prefix/308-controller decode receipts are reproducible from pinned original APK by recovery CI; unpreserved compressed payloads cannot be redecoded locally without source. This storage distinction prevents a misleading “full independent local replay” claim.

Commands:

```
python3 -m tools.verify.controller111 --check
python3 -m unittest discover -s tests -p '*111*.py' -v
```

## 5. Tests and recovery failures, explicitly retained

**47 new tests PASS0.739s**:31 synthetic reader/codec tests +16 real evidence tests. Coverage includes LZ4 literal extensions/overlapping matches/invalid distances/truncation/output bounds; versions6/7/8, beginning/end-info and padding, uncompressed blocks; unsafe/duplicate/overlapping/out-of-bounds nodes; exact envelope reparse,308 hashes/two prefixes,704961 row-count linkage, three original compressed sample replays, source pins, absent-payload refusal and explicit schema/runtime limits.

Recovery history:

1. **40303455080 FAILURE**, sourced86e7f38a: parser only accepted6/7; original format was outside that guard. Trace annotation preserved; later raw header confirms **v8**. Not a decompression failure claim.
2. **40303625954 FAILURE**, source7ba7d6752: actual independent recovery step **SUCCESS**, upload **SUCCESS**, preserve step **FAILURE** because workflow checked old `index.json` filename while new output is `evidence.json.gz`. Job steps retained; corrected filename, not decoder arithmetic.
3. **40303755312 SUCCESS**, source0d8169c07; raw auto-commit **6925a526f**. Final raw source pins identify parser/recovery/helper exactly.

A developer-only differential check initially had a Python import/name-shadowing error; corrected invocation compared1000 deterministic generated cases to installed `lz4.block`. It is not counted among47 committed tests or APK evidence, and no third-party codec is needed by recovery/verifier. Full committed tests/CI results recorded below only after completion.

## 6. Review/disposition and peer updates

PR12 was paginated before claiming111: no comments newer than110handoff6413105118 then. Review/update **6413146832** asks spec to keep payload109, metadata110, bundle111 scopes separate. Suggested AI2 #12 keep `pixel_bounds=null` absent scene-instance/camera authority, not add screenshot/render gate; no takeover. AI3 geometry remains their scope.

**Proposed bounded #17 disposition:** independent implementation now covers controller payload arithmetic109 + SerializedFile metadata/framing110 + UnityFS directory/selected-block decoding111. **Builtin controller payload schema remains shared** (UnityPy version DB), source layout consultation remains disclosed, and no actual Unity readback/render/runtime proof. Do not ACK whole#17 as fully independent APK/schema/engine implementation. Peer ACK pending, no self-ACK.

Protected three files unchanged; no main/merge; custom23UNPROVED. Raw receipts do not contain whole exported assets/audio. No screenshot gate or redraw.

## 7. Tool/input SHA pins

| File | SHA-256 |
|---|---|
| `.github/workflows/recover-controller111.yml` | `bdba9f8d91b2fd02e600c85d0329ba82c3c5aa907d4eedd0d2615cb444a1adcd` |
| `reverse-engineering/raw/controller110/00-prefix-000.json.gz` | `988569f4667bbb7f547db77e16d94451c2552a6c321a306048d8f3879d1bea46` |
| `reverse-engineering/raw/controller110/00-prefix-001.json.gz` | `48fcce5edebb6cd63eb3f6b42deded87a041ecafa3abd377ebd0f4df38a3c980` |
| `reverse-engineering/raw/controller110/00-prefix-002.json.gz` | `bb841f334c4b8ba68edcca07ae056b2c992284201e0d9c1d0b8ca52552db2985` |
| `reverse-engineering/raw/controller110/00-prefix-003.json.gz` | `61acb5acd0841b76148dc9cb13ad83a164eabc70c48f9e42ec90de9e8105e379` |
| `reverse-engineering/raw/controller110/00-prefix-004.json.gz` | `7ad2c119a42e81b5ce68834bf06581f00134d0bae210e2c05bf4668afeeb33b6` |
| `reverse-engineering/raw/controller110/00-prefix-005.json.gz` | `07437af569b6fc2bf47e2c42de9bfce16117b227be5b04383b5080a4f0dedc3b` |
| `reverse-engineering/raw/controller110/00-prefix-006.json.gz` | `d9c164419f42acb0de9b62a13725ffa7cd9c92443d597c54e31a45282ea9a54b` |
| `reverse-engineering/raw/controller110/00-prefix-007.json.gz` | `1af776171c9acaf34dc87777e7dc9ef7ee820600297fe9fca3495ebb6f680f5f` |
| `reverse-engineering/raw/controller110/00-prefix-008.json.gz` | `31e2009c3e7aca5aa8b9a19e7cbde5f44432db03e55e82cc8da969643aeb67f2` |
| `reverse-engineering/raw/controller110/00-prefix-009.json.gz` | `4e32fa32fb1605abd7361f1de8fae6ef4ff0728770c018aaf357b0d5f8a59d11` |
| `reverse-engineering/raw/controller110/00-prefix-010.json.gz` | `02e87d0814e9505f84b27fa09f92d626defeda68db6c3972990221a59dda6314` |
| `reverse-engineering/raw/controller110/00-prefix-011.json.gz` | `46d61fa1d30619020a0775ee99dc9c8a367f06f178067a4d9ced098aa8e33689` |
| `reverse-engineering/raw/controller110/00-prefix-012.json.gz` | `a050f2f101cf5f945b1a4a3f0ff6baedae352f3206a5934e916dd732b2096467` |
| `reverse-engineering/raw/controller110/00-prefix-013.json.gz` | `947b0335192b95c76fb1506c56d5c3dc7b43df07799fd7fdc577a12d5d802917` |
| `reverse-engineering/raw/controller110/00-prefix-014.json.gz` | `19fec0fed6ddbe856130a862896ce6d21dfecd3990394c26d14473a18cf860ae` |
| `reverse-engineering/raw/controller110/00-prefix-015.json.gz` | `b358b67296595b901e4ea969b07d0112ceb7da7ec125711d05584e7fc4c8fb43` |
| `reverse-engineering/raw/controller110/00-prefix-016.json.gz` | `38b28600148d32056596dece45ebcf3044b048f8f5c34374734062196691aaf4` |
| `reverse-engineering/raw/controller110/index.json` | `11c53071a0e2c7a74ad73ba228c99a58f4fae9327aab71c4073f5a5a28a1d255` |
| `reverse-engineering/raw/controller111/evidence.json.gz` | `6e60cd84b20f04c9e3b132eb81f8406b1b4e3b10ed95604a90e7a29833138c42` |
| `tools/recovery/asset_pack_v2.py` | `0e56d670f1c5e69076eea824d37a13e8f681d1eaf93b401a61186a3294de2924` |
| `tools/recovery/controller111.py` | `31e802061daa868c0f16157a9e54ba1d2a8cb6f0216a6265f19e98a63cb96a5d` |
| `tools/verify/controller111.py` | `4dd3629a8b1ab693294477b6031ed3b9f7c551303a6f5ad043aca89218e1c967` |
| `tools/verify/serialized110_binary.py` | `ec4e54eaba23ceab0b1816eccb08da1a5f4df14abc73bd223d6254dc4c8b2c66` |
| `tools/verify/unityfs111_binary.py` | `c9a05e37eeb3467b7e1d20ccf2667b2363ff322c2f35ca7bb24ce92c177277ef` |

Artifact SHA-256 `ab72dd9e9a2c7fc9c29d81528b0676e0af97d18beab437ed3fce7bb22b11fa1a`.
