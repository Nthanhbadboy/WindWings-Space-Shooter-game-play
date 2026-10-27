"""Cycle 134 verifier: the leaf layer behind the refresh / producer chain.

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
PROBE=('reverse-engineering/raw/owner134/probe.json.gz','08237392b0a5e53579712d8d61cbe73945ebf01d860215d3980e9f1f26907fac')
UPSTREAM={'129':('datas/l3_ef6b75ef129_native_owner_linkage.json.gz','217f8893799733f1f36c9d73ac93ab0b9ca903ead81501492b9bab89fb85071a'),
          '133':('datas/l3_ef6b75ef133_native_builder_helpers.json.gz','73542233a6fd80aeb3d13fde9aaae0f1e0a211bd4f04b202afa8c6682d825707')}
TOOLS=('tools/recovery/owner134.py','tools/verify/owner134.py')
ARTIFACT='datas/l3_ef6b75ef134_native_refresh_leaves.json.gz'
CLUSTER=(0x6b0000,0x6c0000)
ACC=0x6d14d4          # per-record word folded into +0x4b8
PRODUCER=0x6d017c     # node primary vtable +0xe0 implementation
APPLY=0x6b6fdc        # apply step of the full refresh
EVAL=0x6b6dec         # evaluate step
SKIN=0x6b2050         # skin step
CHILD=0x6b832c        # recursive child walk
MODE=0x6b22c8         # post-bind mode select
RESOLVER=0x6b6c40     # handle -> object resolver
FACTS={
    0x49fe74:('080c40f9','ldr x8, [x0, #0x18]','pair count at +0x18'),
    0x49fe78:('14200091','add x20, x0, #8','pair array at +8'),
    0x49fe98:('210940b9','ldr w1, [x9, #8]','second word of the pair'),
    0x49fe9c:('3f040031','cmn w1, #1','sentinel -1'),
    0x49feb4:('1f0500f9','str xzr, [x8, #8]','zero the first word'),
    0x49feb8:('171100b9','str w23, [x8, #0x10]','reset the second word to -1'),
    0x49fec4:('b5420091','add x21, x21, #0x10','stride 0x10'),
    0x5707d0:('001440f9','ldr x0, [x0, #0x28]','secondary handle at +0x28'),
    0x5707dc:('a9150094','bl #0x575e80','singleton getter'),
    0x5707e4:('801600f9','str x0, [x20, #0x28]','store the created handle'),
    0x5707e8:('141400f9','str x20, [x0, #0x28]','the singleton points back at the object'),
    0x5707f4:('680200f9','str x8, [x19]','first word of the returned pair'),
    0x5707f8:('690a00b9','str w9, [x19, #8]','version word of the returned pair'),
    0x57283c:('18010094','bl #0x572c9c','pre-check 572c9c'),
    0x572840:('68b64239','ldrb w8, [x19, #0xad]','flag byte at +0xad'),
    0x572844:('00010012','and w0, w8, #1','bit 0 is the answer'),
    0x572aa4:('000040f9','ldr x0, [x0]','wrapped pointer'),
    0x572aac:('68624039','ldrb w8, [x19, #0x18]','release flag byte at +0x18'),
    0x572ac4:('5d5af997','bl #0x3c9438','dealloc sink 3c9438, line 0x306'),
    0x572ad0:('7f0200f9','str xzr, [x19]','clear the pointer'),
    0x572ad4:('6006803d','str q0, [x19, #0x10]','16-byte fill from 0x143ff0'),
    0x576c70:('081840f9','ldr x8, [x0, #0x30]','handle word at +0x30'),
    0x576c80:('29791f12','and w9, w9, #0xfffffffe','version masked with ~1'),
    0x576c8c:('081540f9','ldr x8, [x8, #0x28]','payload at +0x28'),
    0x576c94:('09e14039','ldrb w9, [x8, #0x38]','flag byte at +0x38 of the payload'),
    0x576c98:('3f011f72','tst w9, #2','bit 1 tested'),
    0x576c9c:('00019f9a','csel x0, x8, xzr, eq','returns the payload only when bit 1 is clear'),
    0x5770fc:('081840f9','ldr x8, [x0, #0x30]','same handle word'),
    0x57710c:('29791f12','and w9, w9, #0xfffffffe','same mask'),
    0x577118:('001540f9','ldr x0, [x8, #0x28]','no flag test here: the payload is returned as is'),
    0x6b205c:('130441f9','ldr x19, [x0, #0x208]','graph object at +0x208'),
    0x6b2064:('08f040f9','ldr x8, [x0, #0x1e0]','child table at +0x1e0'),
    0x6b2070:('889e41b9','ldr w8, [x20, #0x19c]','mode word at +0x19c'),
    0x6b207c:('890643f9','ldr x9, [x20, #0x608]','controller handle at +0x608'),
    0x6b20a4:('c31240a9','ldp x3, x4, [x22]','two words from graph+0x48'),
    0x6b20ac:('f6060094','bl #0x6b3c84','formatted buffer helper 6b3c84'),
    0x6b20b8:('7a340094','bl #0x6bf2a0','float sampler 6bf2a0'),
    0x6b20c4:('11340094','bl #0x6bf108','int sampler 6bf108'),
    0x6b20d0:('3f340094','bl #0x6bf1cc','mixed sampler 6bf1cc'),
    0x6b20d4:('889241b9','ldr w8, [x20, #0x190]','mode word at +0x190'),
    0x6b20d8:('1f050071','cmp w8, #1','only mode 1 allocates'),
    0x6b20e8:('01088052','mov w1, #0x40','allocation size 0x40'),
    0x6b20f0:('cba1f997','bl #0x51a81c','allocator helper 51a81c'),
    0x6b2140:('87340094','bl #0x6bf35c','conditional 6bf35c call'),
    0x6b215c:('50b6f497','bl #0x3dfa9c','3dfa9c on animator+0x30 with the table at 0x10e8960'),
    0x6b2184:('e1350014','b #0x6bf908','tail branch into 6bf908'),
    0x6b22d8:('799df497','bl #0x3d98bc','gate 3d98bc'),
    0x6b22dc:('20030036','tbz w0, #0, #0x6b2340','bit 0 clear skips the whole loop'),
    0x6b22e0:('68264639','ldrb w8, [x19, #0x189]','byte at +0x189'),
    0x6b22f0:('688e41b9','ldr w8, [x19, #0x18c]','word at +0x18c'),
    0x6b22f8:('f5179f1a','cset w21, eq','mode is (word == 2) when the byte is clear'),
    0x6b231c:('e9fcfa97','bl #0x5716c0','one of two per-entry calls'),
    0x6b2324:('94fbfa97','bl #0x571174','the other per-entry call'),
    0x6b2a20:('a9310094','bl #0x6bf0c4','6bf0c4 walks the first container'),
    0x6b2a28:('7f0200f9','str xzr, [x19]','pointer cleared'),
    0x6b2a38:('29c12c91','add x9, x9, #0xb30','deleter vtable constant 0x10b0b30'),
    0x6b2a50:('00013fd6','blr x8','deleter callback from +0x10'),
    0x6b2a54:('7f0e00f9','str xzr, [x19, #0x18]','the slot object is cleared last'),
    0x6b3cbc:('480040b9','ldr w8, [x2]','count word at x2'),
    0x6b3d10:('81008052','mov w1, #4','element size 4'),
    0x6b3d18:('452a8052','mov w5, #0x152','source line 0x152'),
    0x6b3d24:('d256f497','bl #0x3c986c','allocator 3c986c'),
    0x6b3d4c:('e59b2794','bl #0x109ace0','fill 109ace0 with 0xff'),
    0x6b3d5c:('02730094','bl #0x6d0964','first transform 6d0964'),
    0x6b3d74:('56c20094','bl #0x6e46cc','second transform 6e46cc'),
    0x6b3d80:('63338052','mov w3, #0x19b','source line 0x19b'),
    0x6b3d8c:('ab55f497','bl #0x3c9438','temporary freed through 3c9438'),
    0x6b6c4c:('089c41b9','ldr w8, [x0, #0x19c]','handle at +0x19c'),
    0x6b6c54:('545100f0','adrp x20, #0x10e1000','registry page'),
    0x6b6c58:('945a44f9','ldr x20, [x20, #0x8b0]','registry pointer at 0x10e18b0'),
    0x6b6c74:('d057f397','bl #0x38cbb4','hashed lookup 38cbb4'),
    0x6b6ca8:('5b86f497','bl #0x3d8614','fallback 3d8614'),
    0x6b6e08:('8effff97','bl #0x6b6c40','resolver 6b6c40 first'),
    0x6b6e14:('8ffeff97','bl #0x6b6850','6b6850 second'),
    0x6b6e18:('689e41b9','ldr w8, [x19, #0x19c]','handle at +0x19c'),
    0x6b6e6c:('609e41b9','ldr w0, [x19, #0x19c]','fallback resolution through 3d8614'),
    0x6b6e78:('68be40f9','ldr x8, [x19, #0x178]','playable count'),
    0x6b6e7c:('1f0500f1','cmp x8, #1','the special path needs exactly one playable'),
    0x6b6e90:('085940f9','ldr x8, [x8, #0xb0]','vtable slot +0xb0'),
    0x6b6e94:('00013fd6','blr x8','indirect call'),
    0x6b6ebc:('61a21791','add x1, x19, #0x5e8','scratch object at animator+0x5e8'),
    0x6b6ec8:('8c030094','bl #0x6b7cf8','6b7cf8 builds the scratch object'),
    0x6b6ed4:('63400094','bl #0x6c7060','6c7060 consumes it with animator+0x1a0'),
    0x6b6f0c:('086140f9','ldr x8, [x8, #0xc0]','per-entry vtable slot +0xc0'),
    0x6b6f10:('00013fd6','blr x8','indirect call with animator+0x518'),
    0x6b6f30:('c0f3ff97','bl #0x6b3e30','the 133 destructor 6b3e30 releases the scratch object'),
    0x6b6f48:('b1eeff97','bl #0x6b2a0c','animator+0x208 is reset through 6b2a0c'),
    0x6b6f58:('908e0094','bl #0x6da998','6da998 with animator+0x228'),
    0x6b6f74:('1aefff97','bl #0x6b2bdc','6b2bdc takes a three-word descriptor'),
    0x6b6f90:('2895881a','csinc w8, w9, w8, ls','the +0x610 counter becomes 2 or keeps incrementing'),
    0x6b6fa0:('681206b9','str w8, [x19, #0x610]','store the counter'),
    0x6b6fa4:('51efff97','bl #0x6b2ce8','apply seed 6b2ce8'),
    0x6b6fa8:('68c64739','ldrb w8, [x19, #0x1f1]','condition byte at +0x1f1'),
    0x6b6fb0:('a80240f9','ldr x8, [x21]','graph pointer at +0x208'),
    0x6b6fb8:('e8079f1a','cset w8, ne','1 when the pointer is non-zero'),
    0x6b6fbc:('68220639','strb w8, [x19, #0x188]','the mirror byte +0x188 is written from it'),
    0x6b6fec:('14c00291','add x20, x0, #0xb0','first argument: animator+0xb0'),
    0x6b6ff0:('01e00691','add x1, x0, #0x1b8','second argument: animator+0x1b8'),
    0x6b6ff4:('02200891','add x2, x0, #0x208','third argument: animator+0x208'),
    0x6b6ff8:('04001991','add x4, x0, #0x640','fifth argument: animator+0x640'),
    0x6b7004:('39efff97','bl #0x6b2ce8','apply seed 6b2ce8'),
    0x6b7008:('78be40f9','ldr x24, [x19, #0x178]','playable count'),
    0x6b7010:('79b640f9','ldr x25, [x19, #0x168]','playable base'),
    0x6b7020:('46e9ff97','bl #0x6b1538','resolve each playable entry'),
    0x6b7030:('afefff97','bl #0x6b2eec','per-entry prepare 6b2eec'),
    0x6b7044:('084d40f9','ldr x8, [x8, #0x98]','per-entry vtable slot +0x98'),
    0x6b7048:('00013fd6','blr x8','indirect call with the driver vector at animator+0xb0'),
    0x6b7064:('695642f9','ldr x9, [x19, #0x4a8]','driver pair count'),
    0x6b7068:('7f461239','strb wzr, [x19, #0x491]','the accumulator byte is cleared first'),
    0x6b7080:('4b815ff8','ldur x11, [x10, #-8]','pair {handle, version}'),
    0x6b7090:('8c791f12','and w12, w12, #0xfffffffe','version masked with ~1'),
    0x6b709c:('6b1540f9','ldr x11, [x11, #0x28]','resolved object payload'),
    0x6b70a0:('6bb140f9','ldr x11, [x11, #0x160]','the flag tested on every resolved playable'),
    0x6b70a8:('eb079f1a','cset w11, ne','1 when the flag is non-zero'),
    0x6b70ac:('08010b2a','orr w8, w8, w11','OR-accumulated over the whole driver vector'),
    0x6b70b0:('68461239','strb w8, [x19, #0x491]','stores the accumulator at +0x491'),
    0x6b82f0:('000040f9','ldr x0, [x0]','same wrapped pointer'),
    0x6b82fc:('c8000037','tbnz w8, #0, #0x6b8314','same release flag'),
    0x6b8310:('4a44f497','bl #0x3c9438','same sink and line'),
    0x6b831c:('7f0200f9','str xzr, [x19]','same clear'),
    0x6b8320:('6006803d','str q0, [x19, #0x10]','same 16-byte fill'),
    0x6b8344:('086940f9','ldr x8, [x8, #0xd0]','vtable slot +0xd0 on the child'),
    0x6b8348:('00013fd6','blr x8','indirect call'),
    0x6b834c:('681a40f9','ldr x8, [x19, #0x30]','child holder at +0x30'),
    0x6b8350:('081940f9','ldr x8, [x8, #0x30]','child count at +0x30 of the holder'),
    0x6b836c:('487d0094','bl #0x6d788c','index accessor 6d788c'),
    0x6b8378:('edffff97','bl #0x6b832c','recursion on the returned child'),
    0x6bb944:('81008052','mov w1, #4','growth thunk: element size 4, alignment 4'),
    0x6bb94c:('39d9f417','b #0x3f1e30','tail branch into 3f1e30'),
    0x6bb95c:('152041a9','ldp x21, x8, [x0, #0x10]','count and capacity'),
    0x6bb96c:('df0648eb','cmp x22, x8, lsr #1','grow when count+1 exceeds capacity/2'),
    0x6bb97c:('880240f9','ldr x8, [x20]','value pointer'),
    0x6bb988:('080940b9','ldr w8, [x8, #8]','an int is read at value+8'),
    0x6bb9a4:('e8ffff97','bl #0x6bb944','growth thunk 6bb944'),
    0x6bf118:('081840f9','ldr x8, [x0, #0x30]','int channel count at +0x30'),
    0x6bf130:('37200191','add x23, x1, #0x48','table at sampler_input+0x48'),
    0x6bf134:('781e40f9','ldr x24, [x19, #0x38]','int channel data at +0x38'),
    0x6bf144:('682240b9','ldr w8, [x19, #0x20]','base index from +0x20'),
    0x6bf154:('215968b8','ldr w1, [x9, w8, uxtw #2]','an int is loaded from the table'),
    0x6bf158:('dba9ff97','bl #0x6a98c4','int test 6a98c4'),
    0x6bf1dc:('081040f9','ldr x8, [x0, #0x20]','mixed channel count at +0x20'),
    0x6bf1f4:('37200191','add x23, x1, #0x48','same table at sampler_input+0x48'),
    0x6bf1f8:('781640f9','ldr x24, [x19, #0x28]','mixed channel data at +0x28'),
    0x6bf20c:('1f2d0071','cmp w8, #0xb','kind 11 selects the other test'),
    0x6bf21c:('e2a9ff97','bl #0x6a99a4','kind test 6a99a4'),
    0x6bf22c:('f1a9ff97','bl #0x6a99f0','fallback float test 6a99f0'),
    0x6bf2b0:('080840f9','ldr x8, [x0, #0x10]','float channel count'),
    0x6bf2c8:('37e00091','add x23, x1, #0x38','table at sampler_input+0x38'),
    0x6bf2cc:('780e40f9','ldr x24, [x19, #0x18]','float channel data'),
    0x6bf2e4:('005976bc','ldr s0, [x8, w22, uxtw #2]','a float is loaded from the table'),
    0x6bf2e8:('c2a9ff97','bl #0x6a99f0','float test 6a99f0'),
    0x6bf308:('22aaff97','bl #0x6a9b90','release 6a9b90'),
    0x6d01a8:('080040f9','ldr x8, [x0]','node vptr'),
    0x6d01ac:('089d40f9','ldr x8, [x8, #0x138]','vtable slot +0x138'),
    0x6d01b0:('00013fd6','blr x8','indirect call: the same slot the accumulator uses'),
    0x6d01b4:('60000036','tbz w0, #0, #0x6d01c0','bit 0 clear returns 1 immediately'),
    0x6d01b8:('68b240f9','ldr x8, [x19, #0x160]','entry count of the node vector at +0x150'),
    0x6d01bc:('e80100b4','cbz x8, #0x6d01f8','a non-empty vector also returns 1: the body only runs on a fresh vector'),
    0x6d01f8:('608e40f9','ldr x0, [x19, #0x118]','source object at +0x118'),
    0x6d0204:('086540f9','ldr x8, [x8, #0xc8]','source object vtable slot +0xc8'),
    0x6d020c:('010840f9','ldr x1, [x0, #0x10]','source element count'),
    0x6d0220:('82008052','mov w2, #4','growth element size 4'),
    0x6d0224:('83008052','mov w3, #4','growth alignment 4'),
    0x6d0228:('e00314aa','mov x0, x20','destination vector at +0x150'),
    0x6d023c:('73be00f9','str x19, [x19, #0x178]','the node stores itself at +0x178 (a different class from the object whose +0x178 is a count)'),
    0x6d0244:('e85700b9','str w8, [sp, #0x54]','scratch record word 0x49'),
    0x6d0248:('e9230139','strb w9, [sp, #0x48]','scratch record byte 0x18'),
    0x6d024c:('ea430139','strb w10, [sp, #0x50]','scratch record byte 1'),
    0x6d0274:('570340b9','ldr w23, [x26]','each source element is an int'),
    0x6d02c4:('d420f497','bl #0x3d8614','int resolved to an object by 3d8614'),
    0x6d031c:('08a540f9','ldr x8, [x8, #0x148]','vtable slot +0x148 on the resolved object'),
    0x6d0320:('00013fd6','blr x8','indirect call'),
    0x6d037c:('088940f9','ldr x8, [x8, #0x110]','vtable slot +0x110'),
    0x6d0380:('00013fd6','blr x8','indirect call'),
    0x6d03b0:('22e4f397','bl #0x3c9438','temporary freed through 3c9438, line 0x206'),
    0x6d03b8:('018c40f9','ldr x1, [x0, #0x118]','the resolved object hands back another object at +0x118'),
    0x6d03c0:('3aa5fa97','bl #0x5798a8','test 5798a8 decides whether the int is kept'),
    0x6d03c8:('782256a9','ldp x24, x8, [x19, #0x160]','destination count and capacity'),
    0x6d03cc:('1c070091','add x28, x24, #1','count+1'),
    0x6d03d4:('88080054','b.hi #0x6d04e4','grow path when over capacity/2'),
    0x6d03d8:('68aa40f9','ldr x8, [x19, #0x150]','destination base'),
    0x6d03dc:('7cb200f9','str x28, [x19, #0x160]','store the new count'),
    0x6d03e0:('177938b8','str w23, [x8, x24, lsl #2]','append the int'),
    0x6d0464:('3badff97','bl #0x6bb950','slow path appends through 6bb950'),
    0x6d0474:('e87a78b8','ldr w8, [x23, x24, lsl #2]','the last appended int'),
    0x6d04d4:('a1078052','mov w1, #0x3d','argument 0x3d'),
    0x6d04d8:('083140f9','ldr x8, [x8, #0x60]','vtable slot +0x60 on the resolved object'),
    0x6d04dc:('00013fd6','blr x8','indirect call for the most recent element only'),
    0x6d04e8:('17adff97','bl #0x6bb944','growth thunk for 4-byte elements'),
    0x6d05b4:('1f0100f1','cmp x8, #0','return value is (count != 0)'),
    0x6d04f0:('e90500b5','cbnz x9, #0x6d05ac','source element count non-zero skips the warning'),
    0x6d04f4:('68b240f9','ldr x8, [x19, #0x160]','the warning needs a non-empty node vector'),
    0x6d04f8:('a80500b4','cbz x8, #0x6d05ac','empty vector skips it too'),
    0x6d0508:('36000094','bl #0x6d05e0','6d05e0 consumes the node vector first'),
    0x6d0514:('4cfaff97','bl #0x6cee44','6cee44 on node+0x120 / node+0xc0'),
    0x6d0520:('a0d0ffd0','adrp x0, #0xe6000','format string page'),
    0x6d0524:('002c1a91','add x0, x0, #0x68b','format string 0xe668b'),
    0x6d0528:('1f050071','cmp w8, #1','string object state check'),
    0x6d053c:('0877f997','bl #0x52e15c','52e15c materialises the message'),
    0x6d0588:('1f781194','bl #0xb2e604','logging sink b2e604'),
    0x6d05a8:('a4e3f397','bl #0x3c9438','message buffer freed, line 0x206'),
    0x6d05ac:('68b240f9','ldr x8, [x19, #0x160]','epilogue recomputes the return value'),
    0x6d05dc:('b9292794','bl #0x109acc0','stack-canary failure stub'),
    0x6d14d4:('fe4fbfa9','stp x30, x19, [sp, #-0x10]!','entry: the word that becomes the +0x4b8 maximum'),
    0x6d14d8:('080040f9','ldr x8, [x0]','entry vptr'),
    0x6d14e0:('089d40f9','ldr x8, [x8, #0x138]','vtable slot +0x138 (same offset the node uses as a boolean query)'),
    0x6d14e4:('00013fd6','blr x8','indirect call'),
    0x6d14e8:('80000036','tbz w0, #0, #0x6d14f8','bit 0 clear means "no value"'),
    0x6d14ec:('689640f9','ldr x8, [x19, #0x128]','value object at +0x128'),
    0x6d14f0:('000140b9','ldr w0, [x8]','the word is read through the pointer'),
    0x6d14f8:('e0031f2a','mov w0, wzr','fallback value 0'),
}
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
        va=by[entry]['entry'];n=by[entry]['extent']
        return [f['va'] for f in facts if va<=f['va']<va+n]
    def targets(e):return [c['target'] for c in by[e]['calls']]
    acc=dict(entry=ACC,extent=by[ACC]['extent'],
             guard=dict(slot=0x138,bit=0,clear_means='no value'),
             value_field=0x128,value_read='the word at [value]',
             note='the per-record word that 6b80e0 folds into the maximum at +0x4b8',
             resolved_guard_slot=slots.get(0x138),facts=facts_at(ACC))
    prod=dict(entry=PRODUCER,extent=by[PRODUCER]['extent'],
              guard=dict(slot=0x138,bit=0,body_requires_empty='[node+0x160] == 0'),
              source_field=0x118,source_virtual_slot=0xc8,source_count_field=0x10,element='int',
              resolve=0x3d8614,per_element_slots=[0x148,0x110],last_element_slot=0x60,
              last_element_arg=0x3d,last_element_before_push=True,
              vector=dict(base=0x150,count=0x160,grow=0x6bb944,grow_params=[4,4],push=0x6bb950),
              self_store_field=0x178,returns='bool ([node+0x160] != 0)',
              resolved_guard_slot=slots.get(0x138),facts=facts_at(PRODUCER))
    warn=dict(entry=PRODUCER,string_va=0xe668b,string_pc=0x6d0520,
              format='An animator Reset was caused during %s::Awake. This will lead to',
              captured_bytes=64,
              condition='source element count == 0 AND node vector count != 0',
              condition_pcs=[0x6d04f0,0x6d04f4,0x6d04f8],
              message=dict(materialise=0x52e15c,log=0xb2e604,free=0x3c9438,free_line=0x206),
              prefix_calls=[0x6d05e0,0x6cee44],
              note='the only string this cycle recovers; it is the warning path of the producer, '
                   'not part of the normal append loop')
    mirror=dict(pointer_field=0x208,condition_byte=0x1f1,mirror_byte=0x188,
                writer=EVAL,writer_pcs=[0x6b6fa8,0x6b6fb0,0x6b6fb8,0x6b6fbc],
                relation='mirror byte = (pointer field != 0), written only when the condition byte is set',
                links='cycle-133 unbind path gates the full refresh on bit 7 of +0x194 together with +0x188 != 0')
    apply_=dict(entry=APPLY,extent=by[APPLY]['extent'],seed=0x6b2ce8,
                seed_args=[0x1b8,0x208,0xb0,0x640],
                per_entry=[0x6b1538,0x6b2eec],per_entry_slot=0x98,
                accumulator_byte=0x491,driver_stride=0x10,driver_flag_field=0x160,
                driver_mask=0xfffffffe,facts=facts_at(APPLY))
    ev=dict(entry=EVAL,extent=by[EVAL]['extent'],first_calls=[0x6b6c40,0x6b6850],
            single_playable_path=dict(count_field=0x178,count_value=1,slot=0xb0),
            scratch=dict(field=0x5e8,builder=0x6b7cf8,consumer=0x6c7060,other=0x1a0,release=0x6b3e30),
            loop=dict(base=0x168,count=0x178,stride=0x28,resolve=0x6b1538,slot=0xc0,arg_field=0x518),
            counter_field=0x610,counter_values=[2,'increment'],apply_seed=0x6b2ce8,
            mirror_writer=0x6b6fbc,facts=facts_at(EVAL))
    skin=dict(entry=SKIN,extent=by[SKIN]['extent'],graph_field=0x208,child_table_field=0x1e0,
              steps=[0x6b3c84,0x6bf2a0,0x6bf108,0x6bf1cc],mode_field=0x190,mode_alloc=1,
              alloc=dict(helper=0x51a81c,size=0x40),conditional=0x6bf35c,
              lookup=dict(helper=0x3dfa9c,field=0x30,table=0x10e8960),tail=0x6bf908,
              facts=facts_at(SKIN))
    child=dict(entry=CHILD,extent=by[CHILD]['extent'],slot=0xd0,
               holder_field=0x30,count_offset=0x30,index_getter=0x6d788c,recursive=True,
               facts=facts_at(CHILD))
    mode=dict(entry=MODE,extent=by[MODE]['extent'],gate=0x3d98bc,gate_bit=0,
              branch_byte=0x189,mode_field=0x18c,mode_value=2,calls=[0x5716c0,0x571174],
              facts=facts_at(MODE))
    res=dict(entry=RESOLVER,extent=by[RESOLVER]['extent'],source_field=0x19c,
             registry=0x10e18b0,lookup=0x38cbb4,fallback=0x3d8614,facts=facts_at(RESOLVER))
    handles=dict(map_strict=dict(entry=0x576c70,handle_field=0x30,mask=0xfffffffe,
                                 payload_field=0x28,flag_byte=0x38,flag_bit=1,returns_zero_when_set=True),
                 map_plain=dict(entry=0x5770fc,handle_field=0x30,mask=0xfffffffe,payload_field=0x28,flag_test=False),
                 identity=dict(entry=0x5707c4,field=0x28,singleton=0x575e80,creator=0x575e8c,
                               back_pointer=0x28,pair_words=[0,8]),
                 bit_test=dict(entry=0x572834,pre=0x572c9c,byte=0xad,bit=0))
    reset=dict(entries=[0x572a9c,0x6b82e8],sink=0x3c9438,line=0x306,fill_const=0x143ff0,
               zeroed=[0,0x10],release_flag_byte=0x18)
    deleter=dict(entry=0x6b2a0c,walk=0x6bf0c4,vtable_const=0x10b0b30,callback_field=0x10,
                 cleared=[0,0x18])
    formatter=dict(entry=0x6b3c84,alloc=dict(helper=0x3c986c,line=0x152,element=4),
                   fill=dict(helper=0x109ace0,value=0xff),transforms=[0x6d0964,0x6e46cc],
                   free=dict(helper=0x3c9438,line=0x19b))
    pairs=dict(entry=0x49fe68,count_field=0x18,array_field=0x8,stride=0x10,sentinel=0xffffffff,
               leaf=0x49fdfc,tail=0x49fee4)
    samplers=[dict(entry=0x6bf2a0,kind='float',count_field=0x10,data_field=0x18,table_offset=0x38,
                   element_stride=0x20,load='ldr s0',test=0x6a99f0),
              dict(entry=0x6bf108,kind='int',count_field=0x30,data_field=0x38,table_offset=0x48,
                   element_stride=0x20,base_index_field=0x20,load='ldr w1',test=0x6a98c4),
              dict(entry=0x6bf1cc,kind='mixed',count_field=0x20,data_field=0x28,table_offset=0x48,
                   element_stride=0x20,kind_field=0x08,kind_value=0x0b,tests=[0x6a99a4,0x6a99f0])]
    notes=dict(mirror_definition='+0x188 is not a free-standing flag: 6b6dec writes it as ([+0x208] != 0) '
                                 'when the byte at +0x1f1 is set, so the 133 unbind gate "bit7 + [+0x188]" '
                                 'reads as "full refresh only while a graph is present".',
               offset_class_warning='+0x178 holds the node pointer in 6d017c but a count in the refresh '
                                    'family; the same offset number in two bodies is NOT the same field.',
               guard_slot_reuse='slot +0x138 is used as a boolean query on both the node (6d017c) and the '
                                'per-record value object (6d14d4); the cycle-129 membership resolves it for '
                                'the node table only, so no target is claimed for the value object.',
               no_execution='no instruction of libunity.so was executed, no object was fabricated and no '
                            'sink was invoked in this cycle.')
    slot_rows={str(k):v for k,v in sorted(slots.items())}
    out=dict(provisional=True,
        pins=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=LIBUNITY_SIZE,
                  probe=dict(path=path,sha256=sha(raw),size=len(raw)),
                  upstream={k:dict(path=v[0],sha256=v[1]) for k,v in UPSTREAM.items()},
                  tools={t:sha((ROOT/t).read_bytes()) for t in TOOLS}),
        cluster=list(CLUSTER),seeds=p['seeds'],order=p['order'],bodies=bodies,
        focus=dict(accumulator_word=acc,producer_impl=prod,reset_warning=warn,active_graph_mirror=mirror,
                   apply_step=apply_,evaluate_step=ev,skin_step=skin,child_walk=child,
                   mode_select=mode,resolver=res,handle_accessors=handles,vector_reset=reset,
                   deleter_slot=deleter,format_helper=formatter,reset_pairs=pairs,samplers=samplers),
        slot_resolution=dict(slots=slot_rows,source='cycle-129 vtable_family called_slots'),
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
                    windows_bytes=sum(b['window_bytes'] for b in bodies)),
        limits=['One follow level for in-cluster callees; 24 bodies, each capped at 0x800 bytes.',
                'Only BL/B, ADRP+ADD and single-register LDR/STR are decoded; ldp/stp are not field rows.',
                'Register-indirect calls are counted and their slot resolved only where a pinned table covers it.',
                'Field rows are raw bracket accesses on x0/x19/x20 and are not class evidence.',
                'Strings are original .rodata bytes; no symbol table is used.',
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
