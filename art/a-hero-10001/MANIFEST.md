# MANIFEST — hero PLAYER ID 10001 · hướng A Ink & Ember

- session: `arena/f2272cda-windwings-space-shooter-game-p` · lập ngày 2026-10-27 (UTC)
- vai: Art-designer-A (thay `5438fec9` đã bị USER đóng) · VISION-ATTEST: CÓ
- ID xác minh: `docs/assets/sprites-index.csv` dòng `ships,10001,Sprite,3581,10001,ships-01.jpg,1` + `datas/ships.json` `id 10001, sprite_path_id 3581` ⇒ ô #1 của ships-01.jpg.
- footprint: canvas 256×256 RGBA, subject chiếm 86.7% cạnh (=130/150 px ô gốc); master 1024×1024 RGBA lossless.
- tái lập: `python3 build_hero.py` (Pillow+numpy+scipy) từ `process/gen_raw_v4.png`; tham số grade là
  default trong script; prompt mọi pass trong `PROMPTS.md`.
- LICENSE: **UNKNOWN / chờ user xác nhận quyền** — ảnh sinh bằng công cụ AI trong session Arena,
  redesign theo reference contact-sheet của APK gốc (com.Wind.wings.Space.Shooter 1.3.118).
  KHÔNG khẳng định quyền thương mại; không publish/store.
- UNKNOWN khác: hue tím dư trong khe tối (nhìn thấy ở 4×); bản 64 chưa hand-tuned; chưa kiểm
  runtime/atlas bleed; CI chưa biết (ghi trong comment PR12).

## File · size · sha256

- `PROMPTS.md` · 4069 B · `2f00e7fe753ffacaab605b90c9499d9ea160e64f15025481f2ab101a02ab5bf3`
- `SELF_REVIEW.md` · 4754 B · `438bae5d51e7eebeb70289a55bdcce1cf82e28ebda7456b4548e480a9868f35d`
- `build_hero.py` · 13032 B · `3f65470ef2169f94bdd67f2a83c09b23bbfe2791c40cd8a64010983da1d4fd5a`
- `compare/compare_index.csv` · 1418 B · `8ab99eff909656a09ee31562f986e8cbb1d17f58d64ec32e5c3f84bd438d1924`
- `compare/pair1_true_10001.png` · 121570 B · `04fc696bdee0791b6216c0e75253a667d1de78ce98e25d4fcb6593dd3d54788c`
- `compare/pair2_analogue_10013.png` · 126611 B · `0f2abfa055047148cb7177aa0973970599ab17aafcad661f0ca77856aeaf91fb`
- `compare/pair3_analogue_10019.png` · 118995 B · `609865ef1064d75dbf07f36770dae96e959d96a559e63b9ca9254235fa6ec818`
- `compare/pair4_analogue_10020.png` · 120282 B · `bf11e3547fabf4406c679b91a474cb0a73196a0e62f34a86281bc6b8623ac7cd`
- `compare/vs_old_a_same_slot.png` · 95318 B · `47c4dfbeb02c4f0fb5fa45702801147dd7c89702b9b602b0d3b7828097d4b0df`
- `master/hero_10001_master_1024.png` · 728962 B · `da31f1a32515b6a1fbd5fe56923ef95a6c1a51a7d85c36c7498a78c97044f1dc`
- `measure/measure_raw_mine.txt` · 465 B · `8133350b59b3ead5f0928df3ed2e46446a122896be8909c3b5e246d3f854571e`
- `measure/measure_raw_oldA.txt` · 513 B · `03c061aec835f5418a9153287fb3e9239ca8d2e4109881b5afb179e8eb6faaa0`
- `measure/measure_raw_ungraded.txt` · 478 B · `db68f7c3b07a3b283ba4df796dbe02612925feae4384c389761b33f61f66feb7`
- `preview/alpha_silhouette_edge.png` · 16578 B · `6a4daf95138b47b3584223be29f31897d4e28f06af36922ae7e12d6ca62251ec`
- `preview/verify_64_true_size.png` · 41324 B · `2c67bd4c44bcb29bc4af28508ffcfb2f1c3156f644fc3e288372ca0fc5d12639`
- `preview/zoom_4x_and_256.png` · 70225 B · `42f95e8f2bb682d0896ecb4f19c400695423b0fb283ad5f42b71de2fd1a5cb9b`
- `process/gen_raw_v4.png` · 1510740 B · `3fffb78da0de9305d7a5d671f177009e8f364a5fe54f9aafa5f1257e2f0a5581`
- `process/old_a_player_ship_01_256.png` · 42544 B · `6fe996602a4e944e70bc2e47626a4ee4116cf452c00f3e3d57c1abfb56d9b697`
- `process/ref_tile01.png` · 24557 B · `efea3db8f59960162f41cacb385c7fb5f7cf20d46881905bc78c98639d53108c`
- `process/ref_tile13.png` · 25570 B · `d1847433c42d026f7792c638c33cb50e219f3457c03f2484ad2c76a6a481053a`
- `process/ref_tile19.png` · 24490 B · `a8975ac737caa1fecc6d321a3840385e76400f94a5740cbc90b920f13f65c537`
- `process/ref_tile20.png` · 25725 B · `bebc1e2009389fb838bb78a7700e4a41ffd877fc4ab57a6a2c0092df0fc8560d`
- `sprites/player_ship_10001_256@inkember.png` · 60144 B · `3a068b367a845d647313dce3a7fb5fafb5fd84609e37421e7d0b23625b377753`
