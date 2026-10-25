# PROVENANCE — nguồn gốc dữ liệu trong `datas/` và `reverse-engineering/`

Bản sao **nguyên văn** của bộ phân tích, kéo từ nhánh dữ liệu để bộ kiểm
(`tools/verify-claims.py`) không phụ thuộc vào một nhánh có thể biến mất.

| | |
|---|---|
| nguồn | `arena/ef6b75ef-windwings-space-shooter-game-p` |
| commit | `019e704d1` (kéo lần 2); lần đầu `6dc5c4bf5` |
| ngày kéo | 23/10/2026 |
| cách kéo | `git archive <ref> <path>… \| tar -x` — không merge, không checkout |
| số file | 383 · 18,77 MB |

## Vì sao kéo

Trước đó mọi phép kiểm phải `git show <ref>:<path>`. Nghĩa là nếu nhánh kia bị xoá, **toàn bộ
500+ con số trong `docs/spec/` mất khả năng kiểm chứng**. Giờ bộ kiểm đọc bản local trước, chỉ
rơi về `git show` khi thiếu — và chạy được cả khi không có nhánh.

## Đã kéo

| đường dẫn | nội dung |
|---|---|
| `datas/` | data pack (27 file) — spine, anim_clips, animator_map, bosses, waves, HP … |
| `reverse-engineering/textassets/` | 27 rig Spine + `Saw` (JSON gốc) |
| `reverse-engineering/raw/typetrees/` | 129 typetree: `Enemy_Appear`, `Enemy_Movement`, `transform-tree`, `prefab-roots`, `native-types` … |
| `reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/` | 20 instance — **nguồn của phép ghép rig ↔ prefab** |
| `reverse-engineering/raw/il2cpp-consts/` | 133 file: asm + method table của 69 class |
| `reverse-engineering/raw/animation-audit/` | 8 file: 154 animator → clip/event · `spine-prefabs.json` (3 component Spine trên boss, PPtr thật) · `event-receivers.json.gz` (795 event use) |
| `reverse-engineering/il2cpp/dump.cs.gz` | 2,64 MB — cây lớp, nguồn của đếm 39 lớp con |
| `docs/apk-analysis/37-`, `38-` | báo cáo của nhánh dữ liệu cho hai file audit trên |

## Một chỗ dễ đọc nhầm

`reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/` có **20 file**, nhưng đó
**không phải** toàn bộ component trong game. `spine-prefabs.json` cho thấy có **ít nhất 21**:
component `664302` (của `Boss-39002`) không nằm trong thư mục đó.

⇒ Đừng đọc "không có trong 20 file" thành "không tồn tại". Đây đúng là lỗi đã xảy ra một lần
(`ANIMATION_GAPS.md` §3.1′).

## KHÔNG kéo — và vì sao

| file | cỡ | lý do |
|---|---:|---|
| `datas/ui_text_keys.csv.gz` | 7,00 MB | vượt mức 5 MB/file; là chuỗi i18n, không phép kiểm nào dùng |
| `reverse-engineering/raw/ui/` | 53.318 file | dump hierarchy UI, không cần cho bất kỳ claim nào |

Khôi phục `ui_text_keys.csv.gz`:

```bash
git fetch origin arena/ef6b75ef-windwings-space-shooter-game-p
git show FETCH_HEAD:datas/ui_text_keys.csv.gz > datas/ui_text_keys.csv.gz
```

## Toàn vẹn

`sha256` (16 ký tự đầu) của từng file, để phát hiện sửa tay:

```

```
e79a022b84c8ab16  34408  datas/PROVENANCE.md
ec7d6432b62f6409  2316  datas/README.md
c1f73dd0b957ed98  9921  datas/anim_clips.json.gz
2e0b212d0ca1792a  53173  datas/animator_map.csv.gz
60687485d5328125  24755  datas/audio_map.json
7c12f56bf0b0077b  27493  datas/boss_hp.json
57bc0bd6b78408a2  5778  datas/bosses.json
ab8084254128ffad  3732  datas/device_table.json
f7f2aed70a697835  1663  datas/drones.json
43caf93ef260c869  92810  datas/enemy_hp.json
e790bc719f6402f7  3079  datas/enemy_hp_by_id.json
f8c2a527429315c4  26873  datas/formula_traces.json.gz
d0521bdc6e2859e0  5394  datas/iap_products.json
c89d07bb1182e3b2  1238  datas/items.json
1b6fe5a776419b18  231233  datas/map_segments_full.json
3ca0070da9d6dac6  70632  datas/map_table_segments.json
4c0fe9e87ad554c7  18752  datas/map_waves_candidate.json
93f8670dd3960d3f  7769  datas/maps.json
97d1446bf95f3aba  40877  datas/particle_systems.csv.gz
3202bb5ac07b1459  31226  datas/prefab_joins.csv.gz
2236a75429857b52  3096  datas/ships.json
e365ad3015498d75  51070  datas/spine.json
11e0b43e624880f6  44326  datas/spine_anim.json.gz
607086bae9268fdd  167177  datas/sprites.csv
92399847f455932f  1575225  datas/ui_screens.json.gz
33a381c7700f8819  3058  datas/validate.py
90e6ecad31702daf  2512  datas/verify_checks.json
9b786c385904ae89  2798437  datas/waves.json
e08f23fb6c90e072  2769105  reverse-engineering/il2cpp/dump.cs.gz
6d77c270b925fa25  2109  reverse-engineering/raw/animation-audit/boss1-conditions.json
d6796cd966db40a8  30354  reverse-engineering/raw/animation-audit/enemy-boss.json
fe001faf73dc7279  35496  reverse-engineering/raw/animation-audit/enemy-clip-links.json.gz
1995d580385ff985  758  reverse-engineering/raw/animation-audit/enemy-lifecycle.json
6513788e7f0d4e8f  15298  reverse-engineering/raw/animation-audit/event-receivers.json.gz
e1ad28f7f609afed  374478  reverse-engineering/raw/animation-audit/native-calls.json
eeed1a1953c4cb65  189893  reverse-engineering/raw/animation-audit/script-declarations.json
bd16f12f4cc4dc4e  3589  reverse-engineering/raw/animation-audit/spine-prefabs.json
4f2ca5b76a56b89a  64777  reverse-engineering/raw/il2cpp-consts/ArenaManager.asm.txt
a8130a2bfb6f2f89  22186  reverse-engineering/raw/il2cpp-consts/ArenaManager.json
39799bf3a49f613c  3855  reverse-engineering/raw/il2cpp-consts/Boss1_AnimationEvents.asm.txt
12677c256927e602  4094  reverse-engineering/raw/il2cpp-consts/Boss1_AnimationEvents.json
d48a67481d3e21a0  11633  reverse-engineering/raw/il2cpp-consts/Boss1_Director._IEAttack1_d__25.asm.txt
56a5e54edad9b962  6258  reverse-engineering/raw/il2cpp-consts/Boss1_Director._IEAttack1_d__25.json
d39abbb6136040f0  3200  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OffGun1Head_d__27.asm.txt
473508b76003e3f0  2423  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OffGun1Head_d__27.json
c9d066d6b93c1cd7  3654  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OffGun1Static_d__26.asm.txt
33a3e864e321677a  2756  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OffGun1Static_d__26.json
38108869ffb9be45  3540  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OnGun1Static_d__28.asm.txt
4c3cfd6483945b8d  3030  reverse-engineering/raw/il2cpp-consts/Boss1_Director._OnGun1Static_d__28.json
e4a4d557feeba571  5021  reverse-engineering/raw/il2cpp-consts/Boss1_Director._RotateObject_d__29.asm.txt
80e49e7adcc2b0e0  3030  reverse-engineering/raw/il2cpp-consts/Boss1_Director._RotateObject_d__29.json
f3aff263b8ca8c2c  6293  reverse-engineering/raw/il2cpp-consts/Boss1_Director._WarningBossAppear_d__15.asm.txt
5d9b58f60d1e0065  5129  reverse-engineering/raw/il2cpp-consts/Boss1_Director._WarningBossAppear_d__15.json
5585bd3f76d74b45  682  reverse-engineering/raw/il2cpp-consts/Boss1_Director.__c__DisplayClass25_0.asm.txt
f642a97fcc8b5315  1766  reverse-engineering/raw/il2cpp-consts/Boss1_Director.__c__DisplayClass25_0.json
1bd71db64554fdfd  57723  reverse-engineering/raw/il2cpp-consts/Boss1_Director.asm.txt
d7accd7e4f53a5d0  25166  reverse-engineering/raw/il2cpp-consts/Boss1_Director.json
2e876d787d4970d3  5884  reverse-engineering/raw/il2cpp-consts/BossAnimationEvents.asm.txt
0b5afd43a7721a27  3375  reverse-engineering/raw/il2cpp-consts/BossAnimationEvents.json
90594500e79d2e28  8510  reverse-engineering/raw/il2cpp-consts/BossSpineEventHandler.asm.txt
5e2041eb45898370  1510  reverse-engineering/raw/il2cpp-consts/BossSpineEventHandler.json
bc9514a4f7ea3496  24138  reverse-engineering/raw/il2cpp-consts/Boss_1_Animation.asm.txt
163a49271bea19ce  6736  reverse-engineering/raw/il2cpp-consts/Boss_1_Animation.json
1fa6c825d0207b7d  12133  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound1_d__13.asm.txt
434edb10b9aa8e8b  4528  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound1_d__13.json
9b49c0e010c6c879  12133  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound2_d__14.asm.txt
198c03eb170b843e  4528  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound2_d__14.json
a5feadf138b31d6f  19331  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound3_d__15.asm.txt
62076fd5aabfc56f  5840  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases._IEAttackRound3_d__15.json
28c34a41ba84164f  4320  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass12_0.asm.txt
3c737d1ababc77dc  2461  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass12_0.json
13f0aeeb6c25aaf6  695  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass13_0.asm.txt
4a9cdd5ad650f2e9  1929  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass13_0.json
e34831bcdba3882f  695  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass14_0.asm.txt
196342842fe76e12  1929  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass14_0.json
d8038bf501bad7f5  1289  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass15_0.asm.txt
f9ef913421c84fc5  3493  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.__c__DisplayClass15_0.json
9b971b3558286db6  17145  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.asm.txt
250ea5e6bb332faa  8455  reverse-engineering/raw/il2cpp-consts/Boss_AttackPhases.json
da1c9cc7e4fc7009  12902  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackArrangePositionX_d__13.asm.txt
f013de0421ded48f  5215  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackArrangePositionX_d__13.json
3266ef1416f7fb81  14867  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackAutoCircleBase_d__12.asm.txt
3931ff062944f200  5781  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackAutoCircleBase_d__12.json
d10200a49f8eec0e  3786  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackAutoCircle_d__11.asm.txt
3526f69df77c89a1  2594  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackAutoCircle_d__11.json
632e1a0dd50af6e5  13852  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackFixed_d__10.asm.txt
4998908c0e559525  4813  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackFixed_d__10.json
448e379bfcc735ad  14216  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackRandomPositionX_d__14.asm.txt
779497e9ff4dc003  4839  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunAttackRandomPositionX_d__14.json
2a0bf663c40cec3d  17426  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunCheckAttack_d__9.asm.txt
1d304057505fc3f7  5473  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes._IEGunCheckAttack_d__9.json
4670a31764d05a0c  3334  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass10_0.asm.txt
5f3d91e52b990e00  1372  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass10_0.json
e361f6b637d69647  3370  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass12_0.asm.txt
63f43ab8d0d59d8f  1408  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass12_0.json
1fba4c60df72e2f0  3378  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass13_0.asm.txt
374fc4f346e6133d  1416  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass13_0.json
8232e2061e9dccfd  3374  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass14_0.asm.txt
a2447a0318e35667  1412  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass14_0.json
bbdbeb988f688146  1861  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_0.asm.txt
0780081854134ec9  1619  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_0.json
be16aeb8da8193ec  1781  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_1.asm.txt
22f3eb7d18a3b436  1619  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_1.json
3b92418ad108edb3  1785  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_2.asm.txt
22151dfd69832599  1623  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_2.json
b16b50ed50986c0d  1789  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_3.asm.txt
53288e1941c28681  1627  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_3.json
f7eebbd1afb938d2  1789  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_4.asm.txt
2cb64c6311985aa6  1627  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass2_4.json
49d9cd16bc149743  3334  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass9_0.asm.txt
3d01e23f88320b14  1371  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.__c__DisplayClass9_0.json
a82474af64545aa3  69598  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.asm.txt
bd2dfa3db4207802  17526  reverse-engineering/raw/il2cpp-consts/Boss_AttackTypes.json
a72bee63f4395887  38855  reverse-engineering/raw/il2cpp-consts/Device_Get_Data.asm.txt
8b65838ea58cedb1  23365  reverse-engineering/raw/il2cpp-consts/Device_Get_Data.json
132a69686a6e9301  22419  reverse-engineering/raw/il2cpp-consts/Droid_Data_Balance.asm.txt
f54ecaea669b1893  12576  reverse-engineering/raw/il2cpp-consts/Droid_Data_Balance.json
5af67ff05f70527a  467  reverse-engineering/raw/il2cpp-consts/Enemy_Appear.asm.txt
7229c8e045926431  712  reverse-engineering/raw/il2cpp-consts/Enemy_Appear.json
b569a3c2c29a89d7  32034  reverse-engineering/raw/il2cpp-consts/Enemy_Controller.asm.txt
e83adc223fef5246  15027  reverse-engineering/raw/il2cpp-consts/Enemy_Controller.json
183057cb2bd34d41  40049  reverse-engineering/raw/il2cpp-consts/Enemy_Data_Balance.asm.txt
593ddf2ea0e35b9d  38048  reverse-engineering/raw/il2cpp-consts/Enemy_Data_Balance.json
f8107461f153e347  32256  reverse-engineering/raw/il2cpp-consts/Enemy_Destroy.asm.txt
ffba03dda48b881f  10845  reverse-engineering/raw/il2cpp-consts/Enemy_Destroy.json
54a7d0028b5f4d04  15483  reverse-engineering/raw/il2cpp-consts/Enemy_Display.asm.txt
3667d92fc23c714a  6544  reverse-engineering/raw/il2cpp-consts/Enemy_Display.json
606c1b752f058bc0  54585  reverse-engineering/raw/il2cpp-consts/Enemy_Get_Datas.asm.txt
bf00bee509c982a4  47496  reverse-engineering/raw/il2cpp-consts/Enemy_Get_Datas.json
9ecd400b6c3eb0a3  2857  reverse-engineering/raw/il2cpp-consts/Enemy_Health.asm.txt
2e50ce0ea904b544  1729  reverse-engineering/raw/il2cpp-consts/Enemy_Health.json
b395903e20402983  6774  reverse-engineering/raw/il2cpp-consts/Enemy_Movement._IELinearMove_d__37.asm.txt
bc0f583c94b036f6  3090  reverse-engineering/raw/il2cpp-consts/Enemy_Movement._IELinearMove_d__37.json
bfc7b41980ebb9d2  37932  reverse-engineering/raw/il2cpp-consts/Enemy_Movement.asm.txt
5ac208259f0b5cf7  16691  reverse-engineering/raw/il2cpp-consts/Enemy_Movement.json
6500c69ba0b40d39  1876  reverse-engineering/raw/il2cpp-consts/Enemy_Rotate.asm.txt
d714f1363a3bfc9c  1453  reverse-engineering/raw/il2cpp-consts/Enemy_Rotate.json
25a7783ac98307ae  12628  reverse-engineering/raw/il2cpp-consts/Enemy_Sub.asm.txt
f8dfccffa98efbb7  8311  reverse-engineering/raw/il2cpp-consts/Enemy_Sub.json
61a4130eff925ebb  170319  reverse-engineering/raw/il2cpp-consts/GameDatas.asm.txt
a8e4824124a118f6  59153  reverse-engineering/raw/il2cpp-consts/GameDatas.json
8babff9463ed30d9  81641  reverse-engineering/raw/il2cpp-consts/IAP_Manager.asm.txt
3cf0b3a2e0dde63b  37853  reverse-engineering/raw/il2cpp-consts/IAP_Manager.json
a95539643a1d0a17  958529  reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt
1b588f39932d2ffe  705566  reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.json
f481feafc6d496b9  132364  reverse-engineering/raw/il2cpp-consts/Player_Ability.asm.txt
bea851727e1f6502  56117  reverse-engineering/raw/il2cpp-consts/Player_Ability.json
26d50d790a50b3af  30797  reverse-engineering/raw/il2cpp-consts/Player_Attack.asm.txt
65b6ed8838d1f811  16007  reverse-engineering/raw/il2cpp-consts/Player_Attack.json
97c79c42e3a4aba2  101  reverse-engineering/raw/il2cpp-consts/Player_Datas.asm.txt
490f483b57518461  370  reverse-engineering/raw/il2cpp-consts/Player_Datas.json
aa6ae77306ea4825  168985  reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt
0950f5a903b484f7  106564  reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.json
badd5311dfc2a7b5  47941  reverse-engineering/raw/il2cpp-consts/Player_Health.asm.txt
6e43abd36acf9a92  19617  reverse-engineering/raw/il2cpp-consts/Player_Health.json
9f1491372a6bfe4a  26531  reverse-engineering/raw/il2cpp-consts/Player_Ingame.asm.txt
a87dbdf4299f90b4  13306  reverse-engineering/raw/il2cpp-consts/Player_Ingame.json
69241429b66bbb1c  76661  reverse-engineering/raw/il2cpp-consts/Player_Talent.asm.txt
a01c5c7722af6f86  29758  reverse-engineering/raw/il2cpp-consts/Player_Talent.json
837b95fb99999f64  28590  reverse-engineering/raw/il2cpp-consts/RankManager.asm.txt
0085459778b3483b  9645  reverse-engineering/raw/il2cpp-consts/RankManager.json
fd109b4d24099e45  110513  reverse-engineering/raw/il2cpp-consts/Stage_Get_Datas.asm.txt
7cf91fc047a41a4d  73268  reverse-engineering/raw/il2cpp-consts/Stage_Get_Datas.json
c2392d85a275f945  74000  reverse-engineering/raw/il2cpp-consts/Tech_Datas.asm.txt
165e665828e1e115  39373  reverse-engineering/raw/il2cpp-consts/Tech_Datas.json
cf45a8f220c003b1  4705  reverse-engineering/raw/il2cpp-consts/_probe_110d028.asm.txt
451c6aae60b8d1a3  4772  reverse-engineering/raw/il2cpp-consts/_probe_110d09c.asm.txt
cffb9f4de1e422a2  4871  reverse-engineering/raw/il2cpp-consts/_probe_110d240.asm.txt
3d3d26b8432a0f11  4739  reverse-engineering/raw/il2cpp-consts/_probe_1bd768c.asm.txt
8c3f270b406f069c  4763  reverse-engineering/raw/il2cpp-consts/_probe_1bd7e58.asm.txt
4038c2812db2f16d  8441  reverse-engineering/raw/typetrees/AirFree_Spawner.jsonl.gz
827d66cf64e02b51  187  reverse-engineering/raw/typetrees/ArenaManager.jsonl.gz
dde08e795ed5bf00  310  reverse-engineering/raw/typetrees/Boss10_AnimationEvents.jsonl.gz
0507a4db932383ad  756  reverse-engineering/raw/typetrees/Boss10_Director.jsonl.gz
969fca110ac08e45  290  reverse-engineering/raw/typetrees/Boss11_AnimationEvents.jsonl.gz
0f4bfd3e62f152e4  753  reverse-engineering/raw/typetrees/Boss11_Director.jsonl.gz
51ab89544e9e8251  329  reverse-engineering/raw/typetrees/Boss12_AnimationEvents.jsonl.gz
f848df7374108396  751  reverse-engineering/raw/typetrees/Boss12_Director.jsonl.gz
190ea0814375d82d  335  reverse-engineering/raw/typetrees/Boss15_AnimationEvents.jsonl.gz
9289bc6566a41018  723  reverse-engineering/raw/typetrees/Boss15_Director.jsonl.gz
b17a3c16ae1ad34c  303  reverse-engineering/raw/typetrees/Boss17_AnimationEvents.jsonl.gz
fcee91c3def37c0b  1008  reverse-engineering/raw/typetrees/Boss17_Director.jsonl.gz
06d5d2ce5d304646  314  reverse-engineering/raw/typetrees/Boss18_AnimationEvents.jsonl.gz
1df6616c3cb8a8eb  734  reverse-engineering/raw/typetrees/Boss18_Director.jsonl.gz
22d563d41ce2d3ad  305  reverse-engineering/raw/typetrees/Boss19_AttackPhases.jsonl.gz
5a04848e4c4146ef  440  reverse-engineering/raw/typetrees/Boss1_Director.jsonl.gz
cba88dd70651d5d0  308  reverse-engineering/raw/typetrees/Boss20_AttackPhases.jsonl.gz
deae09ef4ea43719  1464  reverse-engineering/raw/typetrees/Boss20_AttackTypes.jsonl.gz
a844578747a84fc6  302  reverse-engineering/raw/typetrees/Boss21_AttackPhases.jsonl.gz
de76d0d0a27bf0eb  971  reverse-engineering/raw/typetrees/Boss21_AttackTypes.jsonl.gz
526f8737f8a00e8c  644  reverse-engineering/raw/typetrees/Boss3_Director.jsonl.gz
2edce451496e42e5  296  reverse-engineering/raw/typetrees/Boss4_AnimationEvents.jsonl.gz
5c15046b280e734b  553  reverse-engineering/raw/typetrees/Boss4_Director.jsonl.gz
8c411b7b939b84f0  2594  reverse-engineering/raw/typetrees/Boss4_ExplosionTimer.jsonl.gz
b3aea21539528d31  274  reverse-engineering/raw/typetrees/Boss5_AnimationEvents.jsonl.gz
783a94784f768e73  553  reverse-engineering/raw/typetrees/Boss5_Director.jsonl.gz
1b5b1f498f9ce8a9  329  reverse-engineering/raw/typetrees/Boss6_AnimationEvents.jsonl.gz
e255d6f176adb52a  497  reverse-engineering/raw/typetrees/Boss6_Director.jsonl.gz
0f90cebba52bb220  226  reverse-engineering/raw/typetrees/Boss6_Mini_AnimationEvents.jsonl.gz
092af566c1290ed5  395  reverse-engineering/raw/typetrees/Boss6_Mini_Director.jsonl.gz
3acd0a01d42f3c91  309  reverse-engineering/raw/typetrees/Boss7_AnimationEvents.jsonl.gz
2daed0c4fff1a7b5  524  reverse-engineering/raw/typetrees/Boss7_Director.jsonl.gz
fde3a75e70505216  259  reverse-engineering/raw/typetrees/Boss8_AnimationEvents.jsonl.gz
2f1570f5936077de  639  reverse-engineering/raw/typetrees/Boss8_Director.jsonl.gz
5653d11d2710f12e  389  reverse-engineering/raw/typetrees/Boss9_AnimationEvents.jsonl.gz
aad04db5de3c73cf  554  reverse-engineering/raw/typetrees/Boss9_Director.jsonl.gz
5dc84a198e214760  282  reverse-engineering/raw/typetrees/BossAnimationEvents.jsonl.gz
176615bde7d0a67a  4946  reverse-engineering/raw/typetrees/Boss_BodyPhysics.jsonl.gz
7288798be66ca9d8  273  reverse-engineering/raw/typetrees/Boss_Director.jsonl.gz
1435b846a308cc4a  41948  reverse-engineering/raw/typetrees/Box_Rewards.jsonl.gz
57b9477e7ecc2776  4579  reverse-engineering/raw/typetrees/Bullet_Linearly.jsonl.gz
0459dbb56251df64  324  reverse-engineering/raw/typetrees/Bullet_SineWave.jsonl.gz
8cc15a1e2f565a7c  451695  reverse-engineering/raw/typetrees/Call_Data.jsonl.gz
eca8f708e8e32121  317062  reverse-engineering/raw/typetrees/Call_Point.jsonl.gz
76ebc34b2a96e885  833  reverse-engineering/raw/typetrees/DataShopPack.jsonl.gz
99cf6ad21c65a04b  477  reverse-engineering/raw/typetrees/Data_Boss.jsonl.gz
4264fe6cff1c080c  371  reverse-engineering/raw/typetrees/Data_Items.jsonl.gz
137543d4c0e0eb3c  669  reverse-engineering/raw/typetrees/Data_Players.jsonl.gz
0dd6910fd7cb9b8d  13125  reverse-engineering/raw/typetrees/Enemy_Appear.jsonl.gz
310cb4f93e71f8fd  837  reverse-engineering/raw/typetrees/Enemy_Attack.jsonl.gz
b1f1c0ecc85423e2  739  reverse-engineering/raw/typetrees/Enemy_Attack_Event.jsonl.gz
d94e15100136cfa8  10733  reverse-engineering/raw/typetrees/Enemy_Burned.jsonl.gz
d0789a2c2d62ffe4  268  reverse-engineering/raw/typetrees/Enemy_BurstBulletWhenDie.jsonl.gz
f3644ce85b00dc2d  3720  reverse-engineering/raw/typetrees/Enemy_CameraVibrate.jsonl.gz
3f43c7418bd31618  48896  reverse-engineering/raw/typetrees/Enemy_Controller.jsonl.gz
5131a2760a5db2d4  17097  reverse-engineering/raw/typetrees/Enemy_Datas.jsonl.gz
2bed57c8b9b96d93  14904  reverse-engineering/raw/typetrees/Enemy_Destroy.jsonl.gz
86899daa7b7dae27  355  reverse-engineering/raw/typetrees/Enemy_DestroyAttack.jsonl.gz
b97effbcc6c48f0b  289  reverse-engineering/raw/typetrees/Enemy_DestroyDelayed.jsonl.gz
a073965bdac67302  24259  reverse-engineering/raw/typetrees/Enemy_Display.jsonl.gz
b286b46954daa675  198  reverse-engineering/raw/typetrees/Enemy_DropGold.jsonl.gz
3d1996cb11087aba  19134  reverse-engineering/raw/typetrees/Enemy_EfxDestroyed.jsonl.gz
307166979addb58b  14447  reverse-engineering/raw/typetrees/Enemy_Health.jsonl.gz
e12d0fc068235bb0  270  reverse-engineering/raw/typetrees/Enemy_Helicopter.jsonl.gz
5143ff468d4c3be5  691  reverse-engineering/raw/typetrees/Enemy_HitSkeletonRenderer.jsonl.gz
55b60fc43e3e3c2e  17730  reverse-engineering/raw/typetrees/Enemy_Hp_Bar.jsonl.gz
6b617ee6e1981149  9382  reverse-engineering/raw/typetrees/Enemy_LookAtPlayer.jsonl.gz
23baafc554f055c1  21381  reverse-engineering/raw/typetrees/Enemy_Movement.jsonl.gz
84988e28f000289f  1368  reverse-engineering/raw/typetrees/Enemy_OffObjectWhenDestroy.jsonl.gz
d3366e72b5838e38  276  reverse-engineering/raw/typetrees/Enemy_Passive_Attack.jsonl.gz
08b7aab279b3117c  14521  reverse-engineering/raw/typetrees/Enemy_Physics.jsonl.gz
e66fc7cd181bf139  612  reverse-engineering/raw/typetrees/Enemy_Rocket_Attack.jsonl.gz
d1661b1228f35a7d  763  reverse-engineering/raw/typetrees/Enemy_Rotate.jsonl.gz
36b4f987e489c44e  222  reverse-engineering/raw/typetrees/Enemy_SpawnChilds.jsonl.gz
597195e5d4056a2b  2759  reverse-engineering/raw/typetrees/Enemy_Stun.jsonl.gz
fc1081b2f39181c9  22529  reverse-engineering/raw/typetrees/Enemy_Sub.jsonl.gz
44cbc298597091de  2123  reverse-engineering/raw/typetrees/Enemy_Sync_Attack.jsonl.gz
15a64c547e92760a  637  reverse-engineering/raw/typetrees/Enemy_Sync_Attack2.jsonl.gz
aa7e9165890c0190  331  reverse-engineering/raw/typetrees/GP_Datas.jsonl.gz
1b19c756f8112fcc  3809  reverse-engineering/raw/typetrees/GridLayoutManager.jsonl.gz
be5af3326ae68fa4  16543  reverse-engineering/raw/typetrees/Gun_Attack.jsonl.gz
5c771f3763bce4d5  771  reverse-engineering/raw/typetrees/IAPProduct.jsonl.gz
12d17fc699ec57d8  8349  reverse-engineering/raw/typetrees/Item_Movement.jsonl.gz
6efa44c0d18300b3  382499  reverse-engineering/raw/typetrees/LanguageAssets.jsonl.gz
bf9e2e3e13242133  311  reverse-engineering/raw/typetrees/MB10_Director.jsonl.gz
c8d74ca2e6851d3a  447  reverse-engineering/raw/typetrees/MB11_Director.jsonl.gz
94f4895041d5d0f9  496  reverse-engineering/raw/typetrees/MB12_Director.jsonl.gz
d57b8d8267b3a789  436  reverse-engineering/raw/typetrees/MB13_Director.jsonl.gz
e18f5e90e3b510a1  463  reverse-engineering/raw/typetrees/MB14_Director.jsonl.gz
c9e73d4c745f17c4  529  reverse-engineering/raw/typetrees/MB15_Director.jsonl.gz
10ff524dea09ea87  438  reverse-engineering/raw/typetrees/MB16_Director.jsonl.gz
cefd4c58c300daa5  352  reverse-engineering/raw/typetrees/MB19_Director.jsonl.gz
f0d5ffcc3f0361b0  186  reverse-engineering/raw/typetrees/MB2_Director.jsonl.gz
d695d50e450e343d  287  reverse-engineering/raw/typetrees/MB3_Director.jsonl.gz
e4c9302bfaaf72b7  304  reverse-engineering/raw/typetrees/MB4_Director.jsonl.gz
eb43924a61e3a85c  538  reverse-engineering/raw/typetrees/MB5_Director.jsonl.gz
6666ce776ceedb92  633  reverse-engineering/raw/typetrees/MB6_ChildDirector.jsonl.gz
f2e53b23158efb93  502  reverse-engineering/raw/typetrees/MB6_Director.jsonl.gz
9f80c264f33d20c0  319  reverse-engineering/raw/typetrees/MB7_Director.jsonl.gz
fd6389c00a0ad893  360  reverse-engineering/raw/typetrees/MB8_Director.jsonl.gz
412a43b1353d1e63  470  reverse-engineering/raw/typetrees/MB9_Director.jsonl.gz
7ab8be13601592dc  16760  reverse-engineering/raw/typetrees/MapController.jsonl.gz
514c9f285d340daf  12035  reverse-engineering/raw/typetrees/MeteoriteGenerator.jsonl.gz
284346bf6c98c63e  290  reverse-engineering/raw/typetrees/MiniBoss1_Director.jsonl.gz
efdb44a3803e647d  199  reverse-engineering/raw/typetrees/MiniBoss1_Events.jsonl.gz
6394b6c03c08f8c2  222818  reverse-engineering/raw/typetrees/PathCreator.jsonl.gz
5a5ecbc808409047  15127  reverse-engineering/raw/typetrees/Path_Spawner.jsonl.gz
db690bb80212bda5  28639  reverse-engineering/raw/typetrees/PinMap_Spawner.jsonl.gz
12526e7eaa5dbc11  3658  reverse-engineering/raw/typetrees/Player19Laser.jsonl.gz
7e3d909107b58530  126614  reverse-engineering/raw/typetrees/PointToPoint_Spawner.jsonl.gz
4646b7609cddecba  339  reverse-engineering/raw/typetrees/RankManager.jsonl.gz
b97d57c1cf3cf048  20258  reverse-engineering/raw/typetrees/Rocket_Spawner.jsonl.gz
5d49f49db83dc288  14946  reverse-engineering/raw/typetrees/Shop_Cell.jsonl.gz
bda5375a21253374  3329  reverse-engineering/raw/typetrees/SkeletonAnimation.jsonl.gz
f01cfd77376e0ef2  818  reverse-engineering/raw/typetrees/SkeletonDataAsset.jsonl.gz
33e4d29c6b3d716c  1059  reverse-engineering/raw/typetrees/SoundClip.jsonl.gz
30335d8b79640a54  11792  reverse-engineering/raw/typetrees/Spawner.jsonl.gz
2f891524aaca4feb  12824  reverse-engineering/raw/typetrees/Stage_Behaviour.jsonl.gz
d83d97e990fce34e  13726  reverse-engineering/raw/typetrees/Sub_Item.jsonl.gz
23144e483676c870  290  reverse-engineering/raw/typetrees/TMP_ColorGradient.jsonl.gz
42919773b266711e  616  reverse-engineering/raw/typetrees/TMP_Settings.jsonl.gz
82fe030c81726af1  954  reverse-engineering/raw/typetrees/TMP_StyleSheet.jsonl.gz
6668fccc6e469b21  489  reverse-engineering/raw/typetrees/Tech_Ability_Data.jsonl.gz
7f93ab7acb0ff663  10063  reverse-engineering/raw/typetrees/Wave.jsonl.gz
1d18f01206a67077  10474  reverse-engineering/raw/typetrees/Waypoints_Spawner.jsonl.gz
bdc8c9dd0a7edef3  739143  reverse-engineering/raw/typetrees/native-types.jsonl.gz
cd997d3ebf5a6d3b  57667  reverse-engineering/raw/typetrees/prefab-roots.csv
db83bb00382037ee  755169  reverse-engineering/raw/typetrees/script-links.jsonl.gz
3d42caadd29a2358  1792869  reverse-engineering/raw/typetrees/transform-tree.tsv.gz
935fa7aacce6d2a7  831  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/2511.json
c24ab8f9edc7b91e  837  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/583038.json
26ba4e172e4331d7  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/587165.json
74a9eb3909c2f904  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/588220.json
04895e05c189c6b1  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/588560.json
6e9f9f929e47841c  838  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/590310.json
c13fceb0e2e1b91d  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/594231.json
10f5d463b1fc155a  844  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/594944.json
873b2eed90024ea4  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/595880.json
f57fcfc1ce524aea  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/599252.json
7ce1304910a011a7  838  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/601782.json
bf40eea08d5bea90  835  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/602881.json
6d3fad8dace2c704  835  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/602882.json
3a4360e0aca0620a  838  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/604396.json
c71fe0cfe4bbcfde  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/604765.json
61a2b6f36029c458  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/606343.json
bbdbf6d6f93ccfa2  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/606491.json
37684e70c6496480  843  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/607725.json
df83400269b664f3  838  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/607821.json
8180ddcff4e139fe  844  reverse-engineering/scriptableobjects/Spine.Unity.SkeletonAnimation/608696.json
7763a439481596fd  660  reverse-engineering/textassets/Arabic-Character.txt
7b15cfeef90aebae  29  reverse-engineering/textassets/BillingMode.json
8d678c30a99af31d  38230  reverse-engineering/textassets/Chinese-Character.txt
f5bec8b0496f137c  68  reverse-engineering/textassets/Currency-Characters.txt
7d58e2fe1ab037de  134  reverse-engineering/textassets/Cyrillic-Character.txt
8cff8c17e93f1370  874  reverse-engineering/textassets/Korean-Character.txt
9f9b310d4e353f1d  470  reverse-engineering/textassets/Latin-Characters.txt
3a73e5ffe2510756  269  reverse-engineering/textassets/LineBreaking_Following_Characters.txt
89fcc8f7b3d33a5a  107  reverse-engineering/textassets/LineBreaking_Leading_Characters.txt
ff5b400e06752859  706  reverse-engineering/textassets/Saw.atlas.txt
1ea402e47749ce1b  27985  reverse-engineering/textassets/Saw.json
4d85cb6c4d12c9d9  198  reverse-engineering/textassets/Thai-Character.txt
1616dad7950e5698  2104  reverse-engineering/textassets/skeleton.atlas.txt
e9081af50dcee534  2486  reverse-engineering/textassets/skeleton.atlas__10.txt
6a700fc6548f98b0  1749  reverse-engineering/textassets/skeleton.atlas__11.txt
39b64c529f33add4  1398  reverse-engineering/textassets/skeleton.atlas__12.txt
a03e0225e458333f  1858  reverse-engineering/textassets/skeleton.atlas__13.txt
afd84e45e303d745  4124  reverse-engineering/textassets/skeleton.atlas__14.txt
b2c7bec7d5c4df12  2183  reverse-engineering/textassets/skeleton.atlas__15.txt
b57d2cfdba549239  2544  reverse-engineering/textassets/skeleton.atlas__16.txt
ef18d06bf338e355  3913  reverse-engineering/textassets/skeleton.atlas__17.txt
81ec75759efd17df  2467  reverse-engineering/textassets/skeleton.atlas__18.txt
7bc3096fe3af3c08  1563  reverse-engineering/textassets/skeleton.atlas__19.txt
0892034d4c65710d  1570  reverse-engineering/textassets/skeleton.atlas__2.txt
0b56e54793203f15  2928  reverse-engineering/textassets/skeleton.atlas__20.txt
eeefd394f4881d36  2948  reverse-engineering/textassets/skeleton.atlas__21.txt
b321503838d20ec8  1868  reverse-engineering/textassets/skeleton.atlas__22.txt
bf840eb92c3de89c  1456  reverse-engineering/textassets/skeleton.atlas__23.txt
ce5348398e97f19c  2340  reverse-engineering/textassets/skeleton.atlas__24.txt
b6e515dde5dc13d7  1167  reverse-engineering/textassets/skeleton.atlas__25.txt
f5dcd3ee1183b39e  2847  reverse-engineering/textassets/skeleton.atlas__26.txt
39edf4dc7378c648  1993  reverse-engineering/textassets/skeleton.atlas__3.txt
c69a4eee9f762dea  2135  reverse-engineering/textassets/skeleton.atlas__4.txt
a37ad8a296fd009a  3156  reverse-engineering/textassets/skeleton.atlas__5.txt
7b344ca4d3ab773a  1484  reverse-engineering/textassets/skeleton.atlas__6.txt
cfc58c502d73e755  1828  reverse-engineering/textassets/skeleton.atlas__7.txt
5010e651366410ef  1853  reverse-engineering/textassets/skeleton.atlas__8.txt
24a97bfb53cb48f0  3598  reverse-engineering/textassets/skeleton.atlas__9.txt
a4ace8189ed401fc  24477  reverse-engineering/textassets/skeleton.json
103195357950e05b  16362  reverse-engineering/textassets/skeleton__10.json
2ed2eb0bf439684b  21683  reverse-engineering/textassets/skeleton__11.json
44789ac52ed352a3  20013  reverse-engineering/textassets/skeleton__12.json
8e48bdddf91a8984  498689  reverse-engineering/textassets/skeleton__13.json
6013023150e9915f  13586  reverse-engineering/textassets/skeleton__14.json
0d4879efb7f74592  21563  reverse-engineering/textassets/skeleton__15.json
464dba9567c3efec  12638  reverse-engineering/textassets/skeleton__16.json
c5e9ef2ad7d872b9  27022  reverse-engineering/textassets/skeleton__17.json
d11c317b8ad3c546  11425  reverse-engineering/textassets/skeleton__18.json
4d785263cc05d64c  23993  reverse-engineering/textassets/skeleton__19.json
5b14f33d09524854  32139  reverse-engineering/textassets/skeleton__2.json
4ccb08739a52bf74  18663  reverse-engineering/textassets/skeleton__20.json
89debb56f5b926cc  60897  reverse-engineering/textassets/skeleton__21.json
fb766502eee2746e  17757  reverse-engineering/textassets/skeleton__22.json
6707fbaf2186b232  20502  reverse-engineering/textassets/skeleton__23.json
dcf896ad8f26cde2  32524  reverse-engineering/textassets/skeleton__24.json
23bc43d75daf116f  23961  reverse-engineering/textassets/skeleton__25.json
3134fd32e5a9b23e  16133  reverse-engineering/textassets/skeleton__26.json
889c8f3dbb3ecac3  18033  reverse-engineering/textassets/skeleton__3.json
31f9f0ef10e8754f  20048  reverse-engineering/textassets/skeleton__4.json
bbc25b9e7f8467b5  41837  reverse-engineering/textassets/skeleton__5.json
491c2bcaa6aa51cd  25579  reverse-engineering/textassets/skeleton__6.json
a401be18291ecd3c  21725  reverse-engineering/textassets/skeleton__7.json
6f21fd7dd6050165  63389  reverse-engineering/textassets/skeleton__8.json
6247d9233fd2233a  58413  reverse-engineering/textassets/skeleton__9.json
```

## Đợt kéo 25/10 — nhánh dữ liệu `94da165ca` (audio rules + loadout contracts)

Mỗi dòng: `sha256[0:16]  size  path` của **file trên đĩa** (file `.gz` là hash của byte nén).

```text
f7eba4832f119c67 257 reverse-engineering/raw/audio-rules/array-blobs.json.gz
60d1d716a9f36ac6 4934 reverse-engineering/raw/audio-rules/index.json
b60bd01ea2d8578c 2178 reverse-engineering/raw/audio-rules/native/AudioBehaviour2.asm.txt
5c8dc7261001db33 5338 reverse-engineering/raw/audio-rules/native/AudioBehaviour2.json
d18b3cab68a43a81 4182 reverse-engineering/raw/audio-rules/native/AudioManager._DelayFreeSource_d__27.asm.txt
83d58fc6827ff25c 2459 reverse-engineering/raw/audio-rules/native/AudioManager._DelayFreeSource_d__27.json
646cdfb19f96cf39 7908 reverse-engineering/raw/audio-rules/native/AudioManager._SmoothMusic_d__32.asm.txt
95943550d450382e 2764 reverse-engineering/raw/audio-rules/native/AudioManager._SmoothMusic_d__32.json
96112449377bfbb7 795 reverse-engineering/raw/audio-rules/native/AudioManager.__c__DisplayClass27_0.asm.txt
08d911cc48a8f912 869 reverse-engineering/raw/audio-rules/native/AudioManager.__c__DisplayClass27_0.json
49127a231fa05142 48124 reverse-engineering/raw/audio-rules/native/AudioManager.asm.txt
5faba8b26ee81412 14428 reverse-engineering/raw/audio-rules/native/AudioManager.json
2f0e0b1c61579db5 3239 reverse-engineering/raw/audio-rules/native/Button_Sound.asm.txt
a848c0fb8ebb5e6e 1629 reverse-engineering/raw/audio-rules/native/Button_Sound.json
4f5984ea879d5ddc 10041 reverse-engineering/raw/audio-rules/native/GP_SoundTracks._Start_d__0.asm.txt
d331a0a5f5d35566 6902 reverse-engineering/raw/audio-rules/native/GP_SoundTracks._Start_d__0.json
44f72e62a9229dbd 982 reverse-engineering/raw/audio-rules/native/GP_SoundTracks.asm.txt
816ad197cdade82e 820 reverse-engineering/raw/audio-rules/native/GP_SoundTracks.json
db947b33fb05b732 101 reverse-engineering/raw/audio-rules/native/Player_Sounds.asm.txt
4f7f4e87ff88288f 373 reverse-engineering/raw/audio-rules/native/Player_Sounds.json
fba28a13996260dd 101 reverse-engineering/raw/audio-rules/native/SoundClip.asm.txt
d004d26fed70ae2b 369 reverse-engineering/raw/audio-rules/native/SoundClip.json
03d6fdb1f57268de 1104 reverse-engineering/raw/player-loadout/array-blobs.json.gz
045dd36ff3f81eb4 38818 reverse-engineering/raw/player-loadout/contracts.json.gz
f3a049c8c6f43809 1587 reverse-engineering/raw/player-loadout/index.json
4cd845eca6efa22b 9370 reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.asm.txt
a410ecc45e6956f5 4854 reverse-engineering/raw/player-loadout/native/Player_Device_Saved_Datas.json
bf90fe4d926e0007 75758 reverse-engineering/raw/player-loadout/native/Player_Saved_Datas.asm.txt
e4c5e1a37f8e0768 32292 reverse-engineering/raw/player-loadout/native/Player_Saved_Datas.json
```

