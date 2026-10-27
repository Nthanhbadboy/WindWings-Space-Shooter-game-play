"""Cycle 135 verifier: the apply seed and the channel-sampler internals.

The 24 recovered bodies are decoded again from the pinned probe bytes (calls, indirect-call sites,
referenced strings, bracket accesses) and compared with what the probe recorded. Annotated facts are
re-checked byte for byte, and slot numbers are resolved against the pinned cycle-129 membership.
Nothing is executed and no class name is claimed.
"""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
LIBUNITY_SIZE=17783496
PROBE=('reverse-engineering/raw/owner135/probe.json.gz','c11aedd5868e29ad9493b934ad0c57fb4ba7cda4dd0d0d3de4d79750854070dd')
UPSTREAM={'129':('datas/l3_ef6b75ef129_native_owner_linkage.json.gz','217f8893799733f1f36c9d73ac93ab0b9ca903ead81501492b9bab89fb85071a'),
          '133':('datas/l3_ef6b75ef133_native_builder_helpers.json.gz','73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707'),
          '134':('datas/l3_ef6b75ef134_native_refresh_leaves.json.gz','74cf1843928d165058771269c2508337df33be9b4840edfd9c5e076e358062e6')}
TOOLS=('tools/recovery/owner135.py','tools/verify/owner135.py')
ARTIFACT='datas/l3_ef6b75ef135_native_apply_seed.json.gz'
CLUSTER=(0x6b0000,0x6c0000)
SEED=0x6b2ce8        # apply-context builder, called by both apply and evaluate
COMMIT=0x6b6950      # cache commit tail of the seed
BACKEND=0x6b2bdc     # backend select between two skin writers
PREPARE=0x6b2eec     # per-entry recursive prepare
COMPANION=0x6b6850   # evaluate companion
FLOAT=0x6a99f0       # float channel setter (jump table)
INT=0x6a98c4         # int channel setter
KIND11=0x6a99a4      # kind-0x0b setter
RELEASE=0x6a9b90     # channel release
INTERVAL=0x3dfa9c    # interval lookup
RESOLVE=0x3d8614     # int -> object
ORCREATE=0x518b40    # lookup-or-create
INDEX=0x6d788c       # indexed child accessor
FACTS={
    0x3d8614:('fe4fbfa9','stp x30, x19, [sp, #-0x10]!','zero id returns null'),
    0x3d861c:('286a00b0','adrp x8, #0x111d000','global resolver hook 0x111dba0'),
    0x3d8638:('00013fd6','blr x8','indirect hook call'),
    0x3d8640:('d300f837','tbnz w19, #0x1f, #0x3d8658','negative id is rejected'),
    0x3d8650:('fe4fc1a8','ldp x30, x19, [sp], #0x10','fallback 5d83b8(id, -1)'),
    0x3dfa9c:('0b2040f9','ldr x11, [x0, #0x40]','entry count at +0x40'),
    0x3dfaa0:('8b0100b4','cbz x11, #0x3dfad0','empty table returns null'),
    0x3dfaa4:('091840f9','ldr x9, [x0, #0x30]','entry base at +0x30'),
    0x3dfaa8:('28284629','ldp w8, w10, [x1, #0x30]','key words from x1+0x30'),
    0x3dfaac:('6bed7cd3','lsl x11, x11, #4','stride 0x10'),
    0x3dfab4:('2c815fb8','ldur w12, [x9, #-8]','entry start word'),
    0x3dfab8:('8c01084b','sub w12, w12, w8','entry start minus key start'),
    0x3dfac0:('c3000054','b.lo #0x3dfad8','unsigned below the key width means this entry covers the key'),
    0x3dfad8:('200140f9','ldr x0, [x9]','return the entry payload'),
    0x518b48:('141c40f9','ldr x20, [x0, #0x38]','lazily created object at +0x38'),
    0x518b58:('e00314aa','mov x0, x20','non-zero means it is populated'),
    0x518b60:('e9effd97','bl #0x494b04','494b04 with 0'),
    0x518b68:('afebfd97','bl #0x493a24','493a24 on it'),
    0x518b70:('612240f9','ldr x1, [x19, #0x40]','second word at +0x40'),
    0x6a98d0:('080840b9','ldr w8, [x0, #8]','kind word'),
    0x6a98dc:('1f250071','cmp w8, #9','only kind 9 is handled inline'),
    0x6a98e4:('f4030034','cbz w20, #0x6a9960','zero value short-circuits'),
    0x6a98ec:('b55a44f9','ldr x21, [x21, #0x8b0]','registry pointer 0x10e18b0'),
    0x6a9904:('ac8cf397','bl #0x38cbb4','hashed lookup'),
    0x6a9938:('37bbf497','bl #0x3d8614','fallback int to object'),
    0x6a9940:('600a40f9','ldr x0, [x19, #0x10]','other kinds delegate to +0x10'),
    0x6a9954:('00013fd6','blr x8','indirect call'),
    0x6a9964:('d67bfb97','bl #0x5888bc','5888bc on the object'),
    0x6a9978:('295544f9','ldr x9, [x9, #0x8a8]','compare with the previous object'),
    0x6a9988:('f3079f1a','cset w19, ne','changed flag'),
    0x6a998c:('20013fd6','blr x9','global hook call'),
    0x6a99a4:('080840b9','ldr w8, [x0, #8]','kind-11 channel test entry'),
    0x6a99a8:('1f2d0071','cmp w8, #0xb','only kind 0x0b'),
    0x6a99b0:('080040f9','ldr x8, [x0]','value slot'),
    0x6a99b8:('010100b9','str w1, [x8]','store the new value'),
    0x6a99c0:('e0079f1a','cset w0, ne','changed flag'),
    0x6a99c8:('e0031f2a','mov w0, wzr','other kinds never change'),
    0x6a99f4:('080840b9','ldr w8, [x0, #8]','channel kind at +8'),
    0x6a99fc:('08150051','sub w8, w8, #5','kinds 5..11 are handled'),
    0x6a9a00:('1f190071','cmp w8, #6','seven-case range'),
    0x6a9a08:('49d5ffb0','adrp x9, #0x152000','jump table at 0x152614'),
    0x6a9a14:('2b696838','ldrb w11, [x9, x8]','per-kind byte offset'),
    0x6a9a1c:('40011fd6','br x10','computed branch'),
    0x6a9a24:('010140bd','ldr s1, [x8]','float slot'),
    0x6a9a28:('000100bd','str s0, [x8]','store the new float'),
    0x6a9a2c:('2020201e','fcmp s1, s0','compare with the old one'),
    0x6a9a3c:('216d4ebd','ldr s1, [x9, #0xe6c]','upper threshold constant'),
    0x6a9a44:('22c949bd','ldr s2, [x9, #0x9c8]','lower threshold constant'),
    0x6a9a4c:('0020211e','fcmp s0, s1','value > upper'),
    0x6a9a54:('0020221e','fcmp s0, s2','value < lower'),
    0x6a9a60:('3f010a6b','cmp w9, w10','compare with the previous boolean'),
    0x6a9a68:('0a010039','strb w10, [x8]','store the boolean'),
    0x6a9a98:('c0d8f497','bl #0x3dfd98','boolean forwarded to 3dfd98'),
    0x6a9aa0:('200840f9','ldr x0, [x1, #0x10]','unknown kind: delegate to +0x10'),
    0x6a9aac:('00013fd6','blr x8','indirect call'),
    0x6a9ab8:('280040f9','ldr x8, [x1]','integer channel case'),
    0x6a9abc:('01102c1e','fmov s1, #0.50000000','0.5 rounding bias'),
    0x6a9ac0:('0910a812','mov w9, #-0x40800001','sign mask'),
    0x6a9ac4:('0028211e','fadd s0, s0, s1','value + 0.5'),
    0x6a9ad4:('0820201e','fcmp s0, #0.0','negative test'),
    0x6a9ad8:('00ac211e','fcsel s0, s0, s1, ge','select the biased or unbiased value'),
    0x6a9adc:('0a00381e','fcvtzs w10, s0','truncate toward zero'),
    0x6a9ae8:('0a0100b9','str w10, [x8]','store the rounded int'),
    0x6a9af4:('0a00261e','fmov w10, s0','plain int channel case'),
    0x6a9afc:('000100bd','str s0, [x8]','store the float word'),
    0x6a9b04:('e0079f1a','cset w0, ne','changed flag'),
    0x6a9b94:('080040f9','ldr x8, [x0]','object vptr'),
    0x6a9b98:('01028052','mov w1, #0x10','argument 0x10'),
    0x6a9ba0:('080d40f9','ldr x8, [x8, #0x18]','slot +0x18'),
    0x6a9ba4:('00013fd6','blr x8','indirect call'),
    0x6a9ba8:('c8510090','adrp x8, #0x10e1000','global byte at 0x10e8c0'),
    0x6a9bc0:('e502f817','b #0x4aa754','tail branch into 4aa754 when the global is set'),
    0x6b2be8:('280840f9','ldr x8, [x1, #0x10]','three-word descriptor from x1'),
    0x6b2c00:('480c00f9','str x8, [x2, #0x18]','copy into the frame record'),
    0x6b2c08:('11130094','bl #0x6b784c','context builder 6b784c'),
    0x6b2c0c:('a89e41b9','ldr w8, [x21, #0x19c]','handle at +0x19c'),
    0x6b2c18:('a80643f9','ldr x8, [x21, #0x608]','controller at +0x608'),
    0x6b2c20:('089540f9','ldr x8, [x8, #0x128]','its word at +0x128'),
    0x6b2c2c:('a9965739','ldrb w9, [x21, #0x5e5]','backend flag byte at +0x5e5'),
    0x6b2c4c:('5d2a0094','bl #0x6bd5c0','backend A: 6bd5c0'),
    0x6b2c68:('8a2e0094','bl #0x6be690','backend B: 6be690'),
    0x6b2c6c:('800200f9','str x0, [x20]','the backend result is stored'),
    0x6b2c70:('a83e5239','ldrb w8, [x21, #0x48f]','legacy flag at +0x48f'),
    0x6b2c88:('a8da40f9','ldr x8, [x21, #0x1b0]','object at +0x1b0'),
    0x6b2c9c:('bbbd0094','bl #0x6e2388','6e2388 with that object\'s second word'),
    0x6b2ca8:('db130094','bl #0x6b7c14','else 6b7c14 builds +0x1b0 first'),
    0x6b2cb0:('600a40f9','ldr x0, [x19, #0x10]','first word of the backend result'),
    0x6b2cc0:('099f0094','bl #0x6da8e4','6da8e4 with the descriptor at +0x20 of the record'),
    0x6b2cdc:('000540f9','ldr x0, [x8, #8]','second word of the backend result'),
    0x6b2ce4:('a9bd0014','b #0x6e2388','tail branch into 6e2388'),
    0x6b2cf4:('480040f9','ldr x8, [x2]','source object pointer'),
    0x6b2d04:('680b00b4','cbz x8, #0x6b2e70','no source: the context is written as the invalid state'),
    0x6b2d08:('890240b9','ldr w9, [x20]','cached version word in the context'),
    0x6b2d0c:('a81246b9','ldr w8, [x21, #0x610]','live counter at +0x610'),
    0x6b2d14:('e00d0054','b.eq #0x6b2ed0','same counter: the context is already fresh, nothing is rebuilt'),
    0x6b2d18:('880200b9','str w8, [x20]','adopt the counter as the context version'),
    0x6b2d1c:('480040f9','ldr x8, [x2]','source pointer again'),
    0x6b2d28:('880600f9','str x8, [x20, #8]','context+8 = [[source+0x48]+0]'),
    0x6b2d34:('080540f9','ldr x8, [x8, #8]','table word at +8'),
    0x6b2d38:('880a00f9','str x8, [x20, #0x10]','context+0x10'),
    0x6b2d3c:('280040f9','ldr x8, [x1]','playable record pointer argument'),
    0x6b2d40:('881200f9','str x8, [x20, #0x20]','context+0x20'),
    0x6b2d44:('490c40f9','ldr x9, [x2, #0x18]','second table at source+0x18'),
    0x6b2d4c:('891600f9','str x9, [x20, #0x28]','context+0x28 = table word 0'),
    0x6b2d58:('891a00f9','str x9, [x20, #0x30]','context+0x30 = table word 1'),
    0x6b2d64:('891e00f9','str x9, [x20, #0x38]','context+0x38 = table word 2'),
    0x6b2d70:('892200f9','str x9, [x20, #0x40]','context+0x40 = table word 3'),
    0x6b2d7c:('892600f9','str x9, [x20, #0x48]','context+0x48 = table word 4'),
    0x6b2d88:('892a00f9','str x9, [x20, #0x50]','context+0x50 = table word 5'),
    0x6b2d98:('892e00f9','str x9, [x20, #0x58]','context+0x58 = [[source+0x48]+0x10]'),
    0x6b2da4:('890e00f9','str x9, [x20, #0x18]','context+0x18 = [source+0x48] itself'),
    0x6b2da8:('490c40f9','ldr x9, [x2, #0x18]','third table = [[source+0x18]+0x58]'),
    0x6b2db4:('893200f9','str x9, [x20, #0x60]','context+0x60 = [third table + 8]'),
    0x6b2dc4:('896a00b9','str w9, [x20, #0x68]','context+0x68 = word [third table + 0]'),
    0x6b2dd4:('896e00b9','str w9, [x20, #0x6c]','context+0x6c = word [third table + 0x18]'),
    0x6b2de4:('897200b9','str w9, [x20, #0x70]','context+0x70 = word [third table + 0x1c]'),
    0x6b2df0:('897600b9','str w9, [x20, #0x74]','context+0x74 = source+0x54'),
    0x6b2dfc:('8a7a00b9','str w10, [x20, #0x78]','context+0x78 = source+0x58'),
    0x6b2e04:('4901090a','and w9, w10, w9','three mask words ANDed together'),
    0x6b2e08:('6b5d40b9','ldr w11, [x11, #0x5c]','source+0x5c'),
    0x6b2e10:('3f050031','cmn w9, #1','-1 means all three are set'),
    0x6b2e18:('8b7e00b9','str w11, [x20, #0x7c]','context+0x7c = the third mask word'),
    0x6b2e1c:('89020239','strb w9, [x20, #0x80]','context+0x80 = (mask != -1)'),
    0x6b2e28:('89060239','strb w9, [x20, #0x81]','context+0x81 = byte at [source+0x50]'),
    0x6b2e44:('5f010071','cmp w10, #0','a nested table exists'),
    0x6b2e4c:('8a0a0239','strb w10, [x20, #0x82]','context+0x82 = first nested table is non-empty'),
    0x6b2e64:('29020034','cbz w9, #0x6b2ea8','second nested table empty'),
    0x6b2e68:('08008012','mov w8, #-1','-1 marks the empty case'),
    0x6b2e70:('28008052','mov w8, #1','invalid state: version 1'),
    0x6b2e88:('8082803c','stur q0, [x20, #8]','zeroes context 0x08..0x18'),
    0x6b2e8c:('8082813c','stur q0, [x20, #0x18]','zeroes context 0x18..0x28'),
    0x6b2e94:('8082833c','stur q0, [x20, #0x38]','zeroes context 0x38..0x48'),
    0x6b2eac:('888600b9','str w8, [x20, #0x84]','context+0x84 = -1, or word [+0x50] of [[source+0x48]+0] when the second nested table is empty'),
    0x6b2eb0:('280440f9','ldr x8, [x1, #8]','second word of the playable record'),
    0x6b2ec0:('08454039','ldrb w8, [x8, #0x11]','byte at +0x11 of that record'),
    0x6b2ec4:('88220239','strb w8, [x20, #0x88]','context+0x88'),
    0x6b2ec8:('a58c0094','bl #0x6d615c','6d615c binds the context'),
    0x6b2ecc:('955a09a9','stp x21, x22, [x20, #0x90]','context+0x90 = animator, context+0x98 = animator+0x40'),
    0x6b2ed0:('e00315aa','mov x0, x21','tail branch into the commit helper 6b6950'),
    0x6b2ef8:('080040f9','ldr x8, [x0]','child vptr'),
    0x6b2f04:('086940f9','ldr x8, [x8, #0xd0]','slot +0xd0 first'),
    0x6b2f08:('00013fd6','blr x8','indirect call'),
    0x6b2f18:('086540f9','ldr x8, [x8, #0xc8]','slot +0xc8 second'),
    0x6b2f1c:('00013fd6','blr x8','indirect call with the same argument'),
    0x6b2f20:('681a40f9','ldr x8, [x19, #0x30]','child holder at +0x30'),
    0x6b2f24:('081940f9','ldr x8, [x8, #0x30]','child count'),
    0x6b2f28:('1f050071','cmp w8, #1','no children: skip the loop'),
    0x6b2f40:('53920094','bl #0x6d788c','index accessor 6d788c'),
    0x6b2f4c:('e8ffff97','bl #0x6b2eec','recursion on each child'),
    0x6b2f5c:('7f0e0439','strb wzr, [x19, #0x103]','byte +0x103 cleared on the way out'),
    0x6b6860:('17bc40f9','ldr x23, [x0, #0x178]','playable count'),
    0x6b686c:('78b640f9','ldr x24, [x19, #0x168]','playable base'),
    0x6b6870:('74a21791','add x20, x19, #0x5e8','scratch vector at +0x5e8'),
    0x6b6880:('2eebff97','bl #0x6b1538','resolve each playable entry'),
    0x6b6890:('084940f9','ldr x8, [x8, #0x90]','per-entry slot +0x90'),
    0x6b6894:('00013fd6','blr x8','indirect call with the scratch vector'),
    0x6b68b0:('60020191','add x0, x19, #0x40','lookup 6d6010 on animator+0x40'),
    0x6b68c8:('b6060091','add x22, x21, #1','scratch count+1'),
    0x6b68d8:('76fe02f9','str x22, [x19, #0x5f8]','append the object to the scratch vector'),
    0x6b68dc:('147935f8','str x20, [x8, x21, lsl #3]','store it at base+count*8'),
    0x6b68f0:('a80240f9','ldr x8, [x21]','each scratch entry'),
    0x6b68fc:('08d140f9','ldr x8, [x8, #0x1a0]','entry slot +0x1a0'),
    0x6b6904:('e8079f1a','cset w8, ne','non-zero pointer test'),
    0x6b6908:('2801082a','orr w8, w9, w8','OR into byte +0x48e'),
    0x6b690c:('683a1239','strb w8, [x19, #0x48e]','store the accumulator'),
    0x6b6914:('00610191','add x0, x8, #0x58','entry payload +0x58'),
    0x6b6918:('aca5f797','bl #0x49ffc8','49ffc8 on that payload'),
    0x6b695c:('480440f9','ldr x8, [x2, #8]','context+8 must be set'),
    0x6b696c:('080200b4','cbz x8, #0x6b69ac','otherwise nothing is committed'),
    0x6b6970:('681240f9','ldr x8, [x19, #0x20]','context+0x20 must be set'),
    0x6b6978:('685a40b9','ldr w8, [x19, #0x58]','context version word at +0x58'),
    0x6b697c:('891246b9','ldr w9, [x20, #0x610]','live counter at +0x610'),
    0x6b6984:('e0020054','b.eq #0x6b69e0','already committed for this counter'),
    0x6b6988:('c84f00d0','adrp x8, #0x10b0000','descriptor vtable constant 0x10b0b30'),
    0x6b6990:('c9038052','mov w9, #0x1e','descriptor word 0x1e'),
    0x6b69a4:('f2850094','bl #0x6d816c','6d816c with the descriptor'),
    0x6b69c0:('a80640f9','ldr x8, [x21, #8]','second descriptor target'),
    0x6b69d4:('d1850094','bl #0x6d8118','6d8118 commits the pair'),
    0x6b69dc:('685a00b9','str w8, [x19, #0x58]','context+0x58 = the counter just committed'),
    0x6b7c14:('fe4fbfa9','stp x30, x19, [sp, #-0x10]!','graph at +0x208'),
    0x6b7c2c:('000140f9','ldr x0, [x8]','second table at graph+0x48'),
    0x6b7c30:('a1b10094','bl #0x6e42b4','6e42b4 resolves the pair'),
    0x6b7c38:('60da00f9','str x0, [x19, #0x1b0]','store the result at +0x1b0'),
    0x6b7c48:('fe4fc1a8','ldp x30, x19, [sp], #0x10','tail branch into 6e2388'),
    0x6b7d00:('68d4ff90','adrp x8, #0x143000','constant fill 0x143ff0'),
    0x6b7d08:('1f0000f9','str xzr, [x0]','pointer zeroed'),
    0x6b7d0c:('020800b9','str w2, [x0, #8]','kind word from the caller'),
    0x6b7d14:('0004803d','str q0, [x0, #0x10]','16-byte fill'),
    0x6b7d18:('350840f9','ldr x21, [x1, #0x10]','source count'),
    0x6b7d1c:('340040f9','ldr x20, [x1]','source base'),
    0x6b7d2c:('e10315aa','mov x1, x21','count handed to the push thunk as the element count'),
    0x6b7d30:('390f0094','bl #0x6bba14','push count*8 elements through 6bba14'),
    0x6b7d40:('750a00f9','str x21, [x19, #0x10]','store the count'),
    0x6b7d54:('df8b2714','b #0x109acd0','tail memcpy of count*8 bytes'),
    0x6bad24:('01018052','mov w1, #8','growth thunk: element size 8, alignment 8'),
    0x6bad2c:('41dcf417','b #0x3f1e30','tail branch into 3f1e30'),
    0x6bba14:('03018052','mov w3, #8','insert thunk: element size 8, alignment 8'),
    0x6bba1c:('a6d8f417','b #0x3f1cb4','tail branch into 3f1cb4'),
    0x6bc97c:('680040f9','ldr x8, [x3]','key word at x3+0'),
    0x6bc980:('592441a9','ldp x25, x9, [x2, #0x10]','count and capacity at x2+0x10'),
    0x6bc9b8:('c80240b9','ldr w8, [x22]','key from x1'),
    0x6bc9c4:('e103282a','mvn w1, w8','stored key is the bitwise inverse'),
    0x6bc9c8:('210100b9','str w1, [x9]','key slot'),
    0x6bc9cc:('370500f9','str x23, [x9, #8]','value slot at +8'),
    0x6bc9e4:('8a1a40b9','ldr w10, [x20, #0x18]','second table at x3+0x18'),
    0x6bc9f0:('4a7daa0a','bic w10, w10, w10, asr #31','clamped count'),
    0x6bca04:('6b7968b8','ldr w11, [x11, x8, lsl #2]','scan the table for the key'),
    0x6bca14:('00050051','sub w0, w8, #1','index of the hit'),
    0x6bca1c:('00008012','mov w0, #-1','-1 when absent'),
    0x6bca28:('001100b9','str w0, [x8, #0x10]','store the index at +0x10'),
    0x6bca2c:('e84240f9','ldr x8, [x23, #0x80]','child count at +0x80'),
    0x6bca34:('f83a40f9','ldr x24, [x23, #0x70]','child array at +0x70'),
    0x6bca48:('082940f9','ldr x8, [x8, #0x50]','child slot +0x50'),
    0x6bca4c:('00013fd6','blr x8','indirect call'),
    0x6bca58:('90a9ff97','bl #0x6a7098','6a7098 on the key'),
    0x6bca74:('bdffff97','bl #0x6bc968','recursion per child'),
    0x6bca9c:('39240094','bl #0x6c5b80','growth for the 0x18 table'),
    0x6d788c:('081840f9','ldr x8, [x0, #0x30]','holder at +0x30'),
    0x6d7890:('091940f9','ldr x9, [x8, #0x30]','count at holder+0x30'),
    0x6d7894:('3f0101eb','cmp x9, x1','index bound check'),
    0x6d789c:('091140f9','ldr x9, [x8, #0x20]','base at holder+0x20'),
    0x6d78a4:('206968f8','ldr x0, [x9, x8]','entry pointer'),
    0x6d78ac:('081840b9','ldr w8, [x0, #0x18]','entry count at +0x18'),
    0x6d78b8:('081840f9','ldr x8, [x0, #0x30]','chain to the next holder'),
    0x6d78bc:('210d80b9','ldrsw x1, [x9, #0xc]','signed chain index at slot+0xc'),
    0x6da9a4:('280040f9','ldr x8, [x1]','target vtable'),
    0x6da9ac:('011040f9','ldr x1, [x0, #0x20]','second argument from +0x20'),
    0x6da9b4:('080540f9','ldr x8, [x8, #8]','slot +8 of the target'),
    0x6da9bc:('00013fd6','blr x8','indirect call'),
    0x6da9c8:('39270094','bl #0x6e46ac','6e46ac on the first member'),
    0x6da9d4:('5b250094','bl #0x6e3f40','6e3f40 on the second member'),
    0x6da9d8:('7f1200f9','str xzr, [x19, #0x20]','clear the three words'),
}
FACTS.update({
    0x6bad28:('02018052','mov w2, #8','alignment 8 for the same thunk'),
    0x6bba18:('04018052','mov w4, #8','alignment 8'),
    0x6bba1c:('a6d8f417','b #0x3f1cb4','tail branch into 3f1cb4'),
    0x6b1538:('8a5100b0','adrp x10, #0x10e2000','entry; key comes from x0'),
    0x6b153c:('090840f9','ldr x9, [x0, #0x10]','first key word at [x0+0x10]'),
    0x6b1540:('4a2541f9','ldr x10, [x10, #0x248]','global holder at 0x10e2248'),
    0x6b1550:('a1000054','b.ne #0x6b1564','key mismatch leaves the chain immediately'),
    0x6b156c:('2b2140b9','ldr w11, [x9, #0x20]','node+0x20 compared with the key word, lowest bit masked off'),
    0x6b157c:('201540f9','ldr x0, [x9, #0x28]','next holder at [node+0x28]'),
    0x6b158c:('082140b9','ldr w8, [x8, #0x20]','index word at [node+0x20], negative clamped to 0'),
    0x6b1598:('5f0108eb','cmp x10, x8','bound check against the holder count at +0x30'),
    0x6b15bc:('4811088b','add x8, x10, x8, lsl #4','signed chain index at slot+0xc drives the loop'),
    0x6b15c4:('2a1940f9','ldr x10, [x9, #0x30]','loop continues on the chained holder'),
    0x6b785c:('565100d0','adrp x22, #0x10e1000','global registry page 0x10e1000'),
    0x6b7860:('083846b9','ldr w8, [x0, #0x638]','controller handle at [x0+0x638]'),
    0x6b7864:('d65a44f9','ldr x22, [x22, #0x8b0]','registry pointer at 0x10e18b0'),
    0x6b786c:('28030034','cbz w8, #0x6b78d0','zero handle takes the compute path'),
    0x6b7870:('c00240f9','ldr x0, [x22]','handle looked up in the registry (38cbb4)'),
    0x6b78b4:('603a46b9','ldr w0, [x19, #0x638]','fallback resolution 3d8614 on the handle'),
    0x6b78d0:('601a40f9','ldr x0, [x19, #0x30]','interval lookup on [x19+0x30] with key 0x10e8960'),
    0x6b78e0:('689a41b9','ldr w8, [x19, #0x198]','secondary handle at [x19+0x198]'),
    0x6b7998:('7bd4ff97','bl #0x6acb84','first chain accessor 6acb84'),
    0x6b7a08:('e90300cb','neg x9, x0','self sentinel: [obj] == -obj means empty'),
    0x6b7a8c:('3f0100f1','cmp x9, #0','relative pointer [obj] resolved as obj + [obj]'),
    0x6b7af0:('080c42f8','ldr x8, [x0, #0x20]!','second relative pointer at [obj+0x20]'),
    0x6b7af4:('63965739','ldrb w3, [x19, #0x5e5]','backend flag byte [x19+0x5e5] becomes the fourth argument'),
    0x6b7b0c:('a3bdff97','bl #0x6a7198','6a7198(first rel, second rel, interval entry, flag)'),
    0x6b7b10:('1f0000f1','cmp x0, #0','a null result keeps the interval entry'),
    0x6b7b1c:('880a40b9','ldr w8, [x20, #8]','resolved id word at +8 of the chosen entry'),
    0x6b7b28:('683a06b9','str w8, [x19, #0x638]','chosen id stored back into [x19+0x638]'),
    0x6bd5c0:('ff4305d1','sub sp, sp, #0x150','prologue, 0x150 bytes of frame'),
    0x6bd5e4:('081540f9','ldr x8, [x8, #0x28]','stack guard word taken from tpidr_el0'),
    0x6bd600:('02a9ff97','bl #0x6a7a08','6a7a08 runs before anything is written'),
    0x6bd604:('880240f9','ldr x8, [x20]','source word from [x2] kept for later'),
    0x6bd61c:('09008012','mov w9, #-1','-1 sentinel word for the descriptor'),
    0x6bd640:('e8bb00b9','str w8, [sp, #0xb8]','kind word 1 written into each stack descriptor'),
    0x6bd64c:('e033803d','str q0, [sp, #0xc0]','16-byte constant fill of the three descriptors'),
    0x6bd65c:('c3fcff97','bl #0x6bc968','hash insert 6bc968 with fourth argument 1'),
    0x6bd660:('b81e40f9','ldr x24, [x21, #0x38]','handle at [x21+0x38]'),
    0x6bd67c:('0808f597','bl #0x3ff69c','3ff69c fills the index array from the handle'),
    0x6bd6b4:('0a696ab8','ldr w10, [x8, x10]','per-entry word from the array at [x21+0x40]'),
    0x6bd6e0:('287933b8','str w8, [x9, x19, lsl #2]','index word stored per entry'),
    0x6bd6f0:('40040054','b.eq #0x6bd778','-1 index means the entry has no table slot and is skipped'),
    0x6be690:('ffc305d1','sub sp, sp, #0x170','prologue, 0x170 bytes of frame'),
    0x6be6ac:('48d03bd5','mrs x8, tpidr_el0','stack guard word taken from tpidr_el0'),
    0x6be6d4:('cda4ff97','bl #0x6a7a08','6a7a08 runs before anything is written'),
    0x6be6f0:('e9cb00b9','str w9, [sp, #0xc8]','kind word 1 written into each stack descriptor'),
    0x6be6fc:('1f0100f1','cmp x8, #0','[x24] read as a relative offset'),
    0x6be730:('f32f00f9','str x19, [sp, #0x58]','hash insert 6bc968 with fourth argument 0'),
    0x6be738:('7c010036','tbz w28, #0, #0x6be764','bit 0 of the flag selects the 6bde64 pre-pass'),
    0x6be76c:('8a3240b9','ldr w10, [x20, #0x30]','equality of [x20+0x30] and [x20+0x38] becomes a flag'),
    0x6be788:('a80000b4','cbz x8, #0x6be79c','a non-zero [x20] advances the cursor by (v<<5) past the 0x60 base'),
    0x6be7b8:('890a40f9','ldr x9, [x20, #0x10]','second array pointer at [x20+0x10]'),
    0x6c7060:('e923b96d','stp d9, d8, [sp, #-0x70]!','prologue keeps d8/d9 as well as the callee-saved set'),
    0x6c70a0:('080840f9','ldr x8, [x0, #0x10]','element count at [x0+0x10]'),
    0x6c70a4:('16f17dd3','lsl x22, x8, #3','byte count = count * 8'),
    0x6c70b4:('1f3d1ff1','cmp x8, #0x7cf','more than 0x7cf bytes takes the heap path'),
    0x6c70c4:('08ed7c92','and x8, x8, #0xfffffffffffffff0','stack allocation rounded to 16 bytes'),
    0x6c710c:('680a00f9','str x8, [x19, #0x10]','6d9068 creates the record for that count'),
    0x6c7120:('091c00b9','str w9, [x0, #0x1c]','record word at +0x1c set to 4'),
    0x6c7124:('88050034','cbz w8, #0x6c71d4','zero first word skips the element loop'),
    0x6c7134:('167978f8','ldr x22, [x8, x24, lsl #3]','element pointer from the array at [x20]'),
    0x6c7140:('ed8a1294','bl #0xb69cf4','b69cf4 called on each element'),
    0x6c715c:('60010036','tbz w0, #0, #0x6c7188','bit test of the returned value selects b974b4'),
    0x6c7190:('88834039','ldrb w8, [x28, #0x20]','bit 0 of that test is OR-ed into the record byte at +0x20'),
    0x6c71a8:('1a7938f8','str x26, [x8, x24, lsl #3]','element pointer stored into the first stack array'),
})

def sha(b):return hashlib.sha256(b).hexdigest()
def sg(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def bl_target(w,pc):
    if w&0x7C000000!=0x14000000:return None
    return pc+(sg(w&0x3FFFFFF,26)<<2)
def adrp(w,pc):
    if w&0x9F000000!=0x90000000:return None
    return (w&31,(pc&~0xFFF)+(sg(((w>>5)&0x7FFFF)<<2|((w>>29)&3),21)<<12))
def add_imm(w):
    if w&0xFFC00000!=0x91000000:return None
    return (w>>5)&31,((w>>10)&0xFFF)<<(12 if w&(1<<22) else 0)
def ldr_off(w):
    if w&0xFFC00000==0xF9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*8)
    if w&0xFFC00000==0xB9400000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*4)
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    if w&0xFFE00C00 in (0xB8400000,0xB8400400,0xB8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def store_off(w):
    if w&0xFFC00000==0xF9000000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*8)
    if w&0xFFC00000==0xB9000000:return (w&31,(w>>5)&31,((w>>10)&0xFFF)*4)
    if w&0xFFE00C00 in (0xF8000000,0xF8000400,0xF8000C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    if w&0xFFE00C00 in (0xB8000000,0xB8000400,0xB8000C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def is_blr(w):return w&0xFFFFFC1F==0xD63F0000
def decode(code,entry,extent):
    words=list(struct.unpack_from('<%dI'%(len(code)//4),code))
    calls=[];dispatch=[];fields=[]
    for i,w in enumerate(words):
        pc=entry+i*4
        t=bl_target(w,pc)
        if t is not None:
            intra=entry<=t<entry+extent
            calls.append(dict(pc=pc,target=t,kind='bl' if w>>31 else 'b',intra=intra,
                              in_cluster=(not intra) and CLUSTER[0]<=t<CLUSTER[1]))
            continue
        ld=ldr_off(w);st=store_off(w)
        if ld and ld[1] in (0,19,20) and abs(ld[2])<0x800:
            fields.append(dict(pc=pc,kind='load',base='x%d'%ld[1],offset=ld[2]))
        if st and st[1] in (0,19,20) and abs(st[2])<0x800:
            fields.append(dict(pc=pc,kind='store',base='x%d'%st[1],offset=st[2]))
        if ld:
            rt,rn,off=ld
            for k in range(1,9):
                if i+k>=len(words):break
                nxt=words[i+k]
                if is_blr(nxt) and ((nxt>>5)&31)==rt:
                    cand=dict(ldr_pc=pc,blr_pc=entry+(i+k)*4,slot=off,base_reg='x%d'%rn)
                    prev=[d for d in dispatch if d['blr_pc']==cand['blr_pc']]
                    if prev:
                        if cand['ldr_pc']>prev[0]['ldr_pc']:
                            dispatch[dispatch.index(prev[0])]=cand
                    else:
                        dispatch.append(cand)
                    break
    dispatch.sort(key=lambda d:d['blr_pc'])
    return calls,dispatch,fields
def build():
    path,pin=PROBE;raw=(ROOT/path).read_bytes()
    if sha(raw)!=pin:raise SystemExit('probe sha mismatch')
    p=json.load(gzip.open(path))
    if p['xapk_sha256']!=XAPK_SHA or p['libunity_sha256']!=LIBUNITY_SHA or p['libunity_size']!=LIBUNITY_SIZE:
        raise SystemExit('probe pin mismatch')
    up={}
    for k,(path2,pin2) in UPSTREAM.items():
        b=(ROOT/path2).read_bytes()
        if sha(b)!=pin2:raise SystemExit('upstream pin mismatch: '+path2)
        up[k]=json.loads(gzip.decompress(b))
    slots={}
    for table in up['129']['vtable_family']:
        for cs in table['called_slots']:slots[cs['offset']]=cs['target']
    bodies=[]
    for f in p['functions']:
        code=bytes.fromhex(f['hex'])
        calls,dispatch,fields=decode(code,f['entry'],f['extent'])
        if (len(calls),len(fields))!=(len(f['calls']),len(f['fields'])):
            raise SystemExit('probe/decode disagreement for %#x'%f['entry'])
        if {d['blr_pc'] for d in dispatch}!={d['blr_pc'] for d in f['dispatch']}:
            raise SystemExit('dispatch site disagreement for %#x'%f['entry'])
        bodies.append(dict(entry=f['entry'],group=f['group'],depth=f['depth'],parent=f['parent'],
                           extent=f['extent'],window_bytes=f['window_bytes'],file_offset=f['file_offset'],
                           truncated=f['window_bytes']<f['extent'],
                           body_sha256=sha(code),words=len(code)//4,
                           calls=calls,call_count=len(calls),
                           bl_count=sum(1 for c in calls if c['kind']=='bl'),
                           cluster_calls=[c for c in calls if c['in_cluster']],
                           intra=sum(1 for c in calls if c['intra']),
                           dispatch=[dict(d,resolved_target=slots.get(d['slot'])) for d in dispatch],
                           dispatch_rows_raw=len(f['dispatch']),
                           fields=fields,field_count=len(fields),
                           strings=f['strings'],ret_count=f['ret_count']))
    by={b['entry']:b for b in bodies}
    wins={f['entry']:bytes.fromhex(f['hex']) for f in p['functions']}
    facts=[]
    for va,(hx,text,note) in sorted(FACTS.items()):
        code=None;base=0
        for e,w in wins.items():
            if e<=va<e+len(w):code=w;base=e;break
        ok=code is not None and code[va-base:va-base+4].hex()==hx
        if not ok:raise SystemExit('fact missing at %#x'%va)
        facts.append(dict(va=va,bytes_hex=hx,instruction=text,note=note,verified=True))
    def facts_at(entry):
        va=by[entry]['entry'];n=by[entry]['window_bytes']
        return [f['va'] for f in facts if va<=f['va']<va+n]
    def targets(e):return [c['target'] for c in by[e]['calls']]
    ctx=dict(entry=SEED,extent=by[SEED]['extent'],
             call_frame=dict(x0='animator',x1='playable record',x2='source object',x3='context out',
                             x4='third argument, forwarded to the commit tail'),
             version_key=dict(context_word=0x00,live_counter=0x610,
                              rule='context is valid only while context[0] == animator[+0x610]; '
                                   'the equal case skips the rebuild and still runs the commit tail'),
             invalid_state=dict(first_word=1,zero_qword_ranges=[[0x08,0x18],[0x18,0x28],[0x28,0x38],
                                                               [0x38,0x48],[0x48,0x58],[0x58,0x68]],
                                zero_words=[0x68],zero_pointers=[0x90,0xa0,0xa8,0xb0]),
             copied_fields=[0x08,0x10,0x18,0x20,0x28,0x30,0x38,0x40,0x48,0x50,
                            0x58,0x60,0x68,0x6c,0x70,0x74,0x78,0x7c],
             derived_fields=dict(byte_0x80='([src+0x54] & [src+0x58] & [src+0x5c]) != -1',
                                 byte_0x81='byte at [src+0x50]',
                                 byte_0x82='first nested table non-empty: p=[src+0x48][0]+0x28, '
                                           'q=[p]+p, r=[q+0x30], *(r+q+0x30) != 0',
                                 word_0x84='-1, or word [[src+0x48][0]+0x50] when the second nested '
                                           'table is empty',
                                 byte_0x88='byte at [[playable+8]+0x11]'),
             self_refs=dict(animator=0x90,animator_plus_0x40=0x98),
             bind_call=0x6d615c,tail=COMMIT,
             facts=facts_at(SEED))
    commit=dict(entry=COMMIT,extent=by[COMMIT]['extent'],
                requires=[0x08,0x20],version_word=0x58,counter_field=0x610,
                descriptor=dict(vtable_const=0x10b0b30,word=0x1e),
                calls=[0x6d816c,0x6d8118],
                rule='commits only when both members are set and context[0x58] != animator[+0x610], '
                     'then mirrors the counter into context[0x58]',
                facts=facts_at(COMMIT))
    back=dict(entry=BACKEND,extent=by[BACKEND]['extent'],
              descriptor_from='x1 (three words)',context_builder=0x6b784c,
              backend_flag=0x5e5,backends=dict(plus_0x5e5_set=0x6bd5c0,plus_0x5e5_clear=0x6be690),
              legacy_flag=0x48f,legacy_path=dict(direct=0x6e2388,builder=0x6b7c14,built_field=0x1b0),
              store=dict(result='x2+0x00',descriptor_at='x2+0x20'),
              post=[0x6da8e4,0x6e2388],facts=facts_at(BACKEND))
    prep=dict(entry=PREPARE,extent=by[PREPARE]['extent'],slots=[0xd0,0xc8],
              holder_field=0x30,count_offset=0x30,index=INDEX,recursive=True,
              cleared_byte=0x103,facts=facts_at(PREPARE))
    comp=dict(entry=COMPANION,extent=by[COMPANION]['extent'],loop=dict(base=0x168,count=0x178,stride=0x28,
               resolve=0x6b1538,slot=0x90,arg=0x5e8),
              scratch=dict(field=0x5e8,count=0x5f8,capacity=0x600,grow=0x6bad24),
              lookup=dict(helper=0x6d6010,base=0x40),
              accumulator_byte=0x48e,entry_slot=0x1a0,payload_offset=0x58,release=0x49ffc8,
              facts=facts_at(COMPANION))
    fl=dict(entry=FLOAT,extent=by[FLOAT]['extent'],kind_field=0x08,kind_range=[5,11],
            jump_table=0x152614,table_kind='per-kind byte offset into a 0x152614 table',
            cases=['float write + compare','threshold booleans (2 constants)','delegate to +0x10',
                   'int with 0.5 rounding','plain int store'],
            thresholds=[0x14be6c,0x14b9c8],rounding='fadd 0.5 / fadd sign-mask / fcvtzs',
            delegate_slot=0x10,delegate_arg='0x18 field for the boolean case',facts=facts_at(FLOAT))
    it=dict(entry=INT,extent=by[INT]['extent'],kind_field=0x08,kind=9,registry=0x10e18b0,
            lookup=0x38cbb4,fallback=RESOLVE,delegate_slot=0x10,compare=0x5888bc,
            global_hook=0x10e18a8,returns='changed flag',facts=facts_at(INT))
    k11=dict(entry=KIND11,extent=by[KIND11]['extent'],kind_field=0x08,kind=0x0b,
             returns='old != new',other_kinds='always 0',facts=facts_at(KIND11))
    rel=dict(entry=RELEASE,extent=by[RELEASE]['extent'],slot=0x18,arg=0x10,
             global_byte=0x10e18c0,tail=0x4aa754,facts=facts_at(RELEASE))
    iv=dict(entry=INTERVAL,extent=by[INTERVAL]['extent'],count_field=0x40,base_field=0x30,
            stride=0x10,key_from='x1+0x30',match='(entry_start - key_start) unsigned < key_width',
            payload='[entry+8]',facts=facts_at(INTERVAL))
    rs=dict(entry=RESOLVE,extent=by[RESOLVE]['extent'],zero_returns=0,hook=0x111dba0,
            hook_arg=0x111dba8,negative_rejected=True,fallback=dict(entry=0x5d83b8,
            args='(id, -1)',pre=0x5d6644),facts=facts_at(RESOLVE))
    oc=dict(entry=ORCREATE,extent=by[ORCREATE]['extent'],field=0x38,populated_when='[x0+0x38] != 0',
            calls=[0x494b04,0x493a24],second_word=0x40,facts=facts_at(ORCREATE))
    ix=dict(entry=INDEX,extent=by[INDEX]['extent'],holder=0x30,count=0x30,base=0x20,
            entry_count=0x18,chain_index='ldrsw [slot+0xc]',facts=facts_at(INDEX))
    thunks=[dict(address=0x6bad24,element=8,align=8,target=0x3f1e30,kind='growth'),
            dict(address=0x6bba14,element=8,align=8,target=0x3f1cb4,kind='insert')]
    notes=dict(
        counter_definition='134 stored "+0x610 = 2 or increment" without a meaning. Here the same word is '
                           'the version key of the apply context: 6b2ce8 rebuilds the ~0x90-byte context only '
                           'when context[0] != animator[+0x610], and 6b6950 mirrors the counter into '
                           'context[0x58] after committing. So +0x610 is the change token both refresh and '
                           'apply agree on.',
        two_backends='6b2bdc selects between two complete writers on the byte at +0x5e5 (set -> 6bd5c0, '
                     'clear -> 6be690), and separately gates a legacy path on +0x48f. Both writers are larger '
                     'than the 0x800 window and are truncated in this capture, so their internals are NOT read here.',
        channel_writes='6a99f0 is a seven-case jump table (kinds 5..11) that stores a float / boolean / '
                       'rounded int into the channel and returns "changed"; 6a98c4 handles kind 9 through the '
                       'same registry as the resolver; 6a99a4 handles kind 0x0b by comparing the stored value. '
                       'This is the first place in the lane where a written value is compared with the previous '
                       'one, which is what a dirty/change detection looks like.',
        truncation='three bodies were cut at the 0x800 cap: 0x6c7060 (0x108c), 0x6bd5c0 (0x8a4), '
                   '0x6be690 (0xa34). Their call/field rows describe only the captured prefix.',
        no_execution='no instruction of libunity.so was executed, no object was fabricated and no sink was '
                     'invoked in this cycle.')
    out=dict(provisional=True,
        pins=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=LIBUNITY_SIZE,
                  probe=dict(path=path,sha256=sha(raw),size=len(raw)),
                  upstream={k:dict(path=v[0],sha256=v[1]) for k,v in UPSTREAM.items()},
                  tools={t:sha((ROOT/t).read_bytes()) for t in TOOLS}),
        cluster=list(CLUSTER),seeds=p['seeds'],order=p['order'],bodies=bodies,
        focus=dict(apply_context=ctx,context_commit=commit,backend_select=back,entry_prepare=prep,
                   evaluate_companion=comp,float_setter=fl,int_setter=it,kind_0b_setter=k11,
                   channel_release=rel,interval_lookup=iv,int_resolver=rs,lookup_or_create=oc,
                   index_accessor=ix,growth_thunks=thunks,
                   controller_resolve=dict(entry=0x6b784c,extent=by[0x6b784c]['extent'],
                        handle_field=0x638,secondary_handle=0x198,registry=0x10e18b0,
                        registry_lookup=0x38cbb4,fallback=RESOLVE,interval_source=0x30,
                        interval_key=0x10e8960,chain=0x6acb84,
                        self_sentinel='[obj] == -obj is read as an empty slot',
                        relative_pointers=['obj+[obj]','obj+0x20 then [obj+0x20]'],
                        leaf_call=dict(entry=0x6a7198,args='(rel_a, rel_b, interval_entry, byte[x+0x5e5])'),
                        store='resolved word at [chosen+8] written back to [x+0x638]',
                        facts=facts_at(0x6b784c)),
                   node_chain=dict(entry=0x6b1538,extent=by[0x6b1538]['extent'],
                        key_source='[x0+0x10] and the word at [x0+0x18]',global_holder=0x10e2248,
                        node_fields=dict(next=0x28,tag=0x20,count=0x30,base=0x20,index=0x0c),
                        rule='walk [node+0x28] while the masked tag matches the key word and the index stays '
                             'below the holder count; the index comes from slot+0xc',
                        facts=facts_at(0x6b1538)),
                   backend_entry=dict(
                        both=dict(pre_call=0x6a7a08,descriptor_words=3,stack_kind_word=1,
                                  sentinel_word=-1,insert=0x6bc968,constant_page=0x143000),
                        writer_a=dict(entry=0x6bd5c0,frame=0x150,insert_flag=1,index_fill=0x3ff69c,
                                      handle_field=0x38,word_array=0x40),
                        writer_b=dict(entry=0x6be690,frame=0x170,insert_flag=0,
                                      flag_pre_pass=0x6bde64,state_words=[0x30,0x38],
                                      cursor_fields=[0x00,0x20,0x10],base=0x60),
                        difference='the same insert helper is called with fourth argument 1 and 0, so the two '
                                   'writers do not build the same table entry',
                        truncated='both bodies are cut at the 0x800 cap; only the entry sequences above are read',
                        facts=facts_at(0x6bd5c0)+facts_at(0x6be690)),
                   builder_head=dict(entry=0x6c7060,extent=by[0x6c7060]['extent'],
                        count_field=0x10,element_bytes=8,stack_limit=0x7cf,align=16,
                        heap_path=0x6c748c,record_factory=0x6d9068,record_kind_word=dict(offset=0x1c,value=4),
                        per_element=[0xb69cf4,0xb97454,0xb974b4],accumulator_byte=0x20,
                        element_array_source='[x20]',note='only the first 0x150 bytes of the 0x108c body are '
                                                         'annotated; the rest is outside the 0x800 window',
                        facts=facts_at(0x6c7060))),
        slot_resolution=dict(slots={str(k):v for k,v in sorted(slots.items())},
                             source='cycle-129 vtable_family called_slots'),
        truncated=[hex(b['entry']) for b in bodies if b['truncated']],
        follow_depth=dict(level1=sum(1 for b in bodies if b['group']=='cluster_callee' and
                                     by[b['parent']]['group']=='seed'),
                          level2=[hex(b['entry']) for b in bodies if b['group']=='cluster_callee'
                                  and by[b['parent']]['group']=='cluster_callee'],
                          note='one callee of a callee (0x6bc968, seen from 0x6bd5c0) was captured as well; '
                               'its rows are labelled depth 1 by the recovery tool and are reported as a '
                               'second level here instead of being hidden.'),
        notes=notes,
        counts=dict(bodies=len(bodies),facts=len(facts),
                    seeds=sum(1 for b in bodies if b['group']=='seed'),
                    followed=sum(1 for b in bodies if b['group']=='cluster_callee'),
                    calls=sum(b['call_count'] for b in bodies),
                    bl=sum(b['bl_count'] for b in bodies),
                    cluster_calls=sum(len(b['cluster_calls']) for b in bodies),
                    dispatch=sum(len(b['dispatch']) for b in bodies),
                    dispatch_rows_raw=sum(b['dispatch_rows_raw'] for b in bodies),
                    strings=sum(len(b['strings']) for b in bodies),
                    fields=sum(b['field_count'] for b in bodies),
                    truncated=sum(1 for b in bodies if b['truncated']),
                    windows_bytes=sum(b['window_bytes'] for b in bodies)),
        limits=['One follow level for in-cluster callees; 24 bodies, each capped at 0x800 bytes.',
                'Three bodies are truncated by that cap and are flagged; their rows cover the prefix only.',
                'Only BL/B, ADRP+ADD and single-register LDR/STR are decoded; ldp/stp are not field rows.',
                'The jump table at 0x152614 is described from the dispatch code, its target bytes are not decoded.',
                'Field rows are raw bracket accesses on x0/x19/x20 and are not class evidence.',
                'One callee of a callee (0x6bc968) is present; follow_depth reports it instead of calling it depth 1.',
                'Only the first 0x150 bytes of 0x6c7060 are annotated; later captured rows carry no note.',
                'Static only: nothing here is a runtime observation.'])
    return out
def render(res):return gzip.compress((json.dumps(res,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true')
    a=ap.parse_args();res=build();blob=render(res);out=ROOT/ARTIFACT
    if a.write:out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob);print('wrote',out,len(blob),sha(blob))
    if a.check:
        if out.read_bytes()!=blob:raise SystemExit('artifact drift')
        print('check ok',ARTIFACT,len(blob),sha(blob))
    if not a.write and not a.check:print(json.dumps(res['counts'],sort_keys=True))
if __name__=='__main__':main()
