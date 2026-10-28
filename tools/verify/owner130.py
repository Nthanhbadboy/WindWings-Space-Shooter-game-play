"""Cycle 130 verifier: static map of the animator-side update/trigger chain.

The artifact is a byte-verified statement set: every row cites a virtual address and
the exact instruction bytes that must be present in the pinned recovery probes.
No instruction is executed and no class name is inferred.
"""
import argparse,gzip,hashlib,json,re,sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
PROBES={'owner130':('reverse-engineering/raw/owner130/probe.json.gz','d3929b2e8d3302c47488eb69314e379c522355efb9133590b31c73e69b5c3466'),
        'owner130b':('reverse-engineering/raw/owner130b/probe.json.gz','7d5aacc5cae91f97e18a108c54d994e012cf662d4220967d2d1fee600c8adacb')}
TOOLS=('tools/recovery/owner130.py','tools/recovery/owner130b.py','tools/verify/owner130.py')
ARTIFACT='datas/l3_ef6b75ef130_native_update_trigger.json.gz'
VTABLE=0x10b0c80
ROLES={2:'rebuild-all / reset entry (calls 6b1a00, 6b1b1c, 6b1bb0, 6b9ed4)',
       3:'message entry: checks w1==0x10, then 6b1c98(x0,0)',
       10:'accessor: [x0+0x30] -> +0x60, else global table [0x10e19c8]',
       31:'update entry: bind controller by +0x19c, then 6b1f04, 6b22c8, 571e64',
       33:'parameter entry: resolves +0x618 and tails 572c60 with w1=0 or 3'}
NOTES={
    0x6b950c:('60000054','b.eq #0x6b9518','skips the 6b7d58 rebuild when the resolved controller equals the cached handle'),
    0x6b9ad0:('08013291','add x8, x8, #0xc80','adds 0xc80 to the 0x10b0000 page (vtable address)'),
    0x6b9b50:('48510090','adrp x8, #0x10e1000','page of the secondary header 0x10e19e0'),
}
CHAIN=(
 ('install',0x6b9acc,(0x6b9acc,0x6b9ad0,0x6b9ad8,0x6b9b50,0x6b9b5c,0x6b9b60)),
 ('reset',0x6b1a00,(0x6b1a0c,0x6b1a10,0x6b1a1c,0x6b1a5c,0x6b1a68,0x6b1a84,0x6b1a88,0x6b1a8c,0x6b1b08)),
 ('teardown',0x6b1b1c,(0x6b1b2c,0x6b1b34,0x6b1b50,0x6b1b58,0x6b1b64,0x6b1b68,0x6b1b84,0x6b1b8c,0x6b1b90,0x6b1b9c)),
 ('rebind-check',0x6b1ce0,(0x6b1cec,0x6b1cf4,0x6b1cf8,0x6b1d60,0x6b1d6c)),
 ('message',0x6b1c5c,(0x6b1c6c,0x6b1c70,0x6b1c8c,0x6b1c94)),
 ('flush',0x6b1c98,(0x6b1ca0,0x6b1ca8,0x6b1cb0,0x6b1cb4,0x6b1cb8,0x6b1cc0,0x6b1cc8,0x6b1cd4)),
 ('rebuild',0x6b2258,(0x6b225c,0x6b2260,0x6b2268,0x6b2270,0x6b227c,0x6b2284,0x6b2288,0x6b2294,0x6b229c,0x6b22a4,0x6b22ac,0x6b22b0,0x6b22bc)),
 ('query-rebuild',0x6b4bfc,(0x6b4c00,0x6b4c08,0x6b4c10,0x6b4c14,0x6b4c1c,0x6b4c24,0x6b4c2c,0x6b4c30,0x6b4c34)),
 ('batch',0x6b27dc,(0x6b27f0,0x6b27f8,0x6b2810,0x6b282c,0x6b2830,0x6b2834,0x6b283c,0x6b2848,0x6b284c)),
 ('reset-if-needed',0x6b1f04,(0x6b1f0c,0x6b1f14,0x6b1f18,0x6b1f20,0x6b1f24,0x6b1f38,0x6b1f44,0x6b1f4c,0x6b1f5c)),
 ('reset-variant',0x6b1f68,(0x6b1f70,0x6b1f78,0x6b1f7c,0x6b1f88,0x6b1f90,0x6b1f9c)),
 ('skin',0x6b2050,(0x6b205c,0x6b2064,0x6b2070,0x6b207c,0x6b2084,0x6b2094,0x6b20ac,0x6b20b8,0x6b20c4,0x6b20d0,0x6b20d4,0x6b20f0,0x6b2110,0x6b2140,0x6b2144,0x6b2184)),
 ('per-entry',0x6b22c8,(0x6b22d8,0x6b22e0,0x6b22f0,0x6b22fc,0x6b2304,0x6b2310,0x6b231c,0x6b2324)),
 ('update',0x6b947c,(0x6b9488,0x6b9490,0x6b94f4,0x6b950c,0x6b9514,0x6b9518,0x6b9524,0x6b952c,0x6b9538,0x6b9540,0x6b95cc)),
 ('evaluate',0x6b6dec,(0x6b6e08,0x6b6e14,0x6b6e18,0x6b6e78,0x6b6e90,0x6b6e94,0x6b6ec8,0x6b6ed4,0x6b6efc,0x6b6f0c,0x6b6f10,0x6b6f30,0x6b6f48,0x6b6f58,0x6b6f74,0x6b6fa4,0x6b6fbc)),
 ('apply',0x6b6fdc,(0x6b6ff0,0x6b6ff4,0x6b6ff8,0x6b6ffc,0x6b7004,0x6b701c,0x6b7030,0x6b7044,0x6b7048,0x6b7064,0x6b7068,0x6b7070,0x6b70a0,0x6b70b0)),
 ('clear',0x6b6d60,(0x6b6d70,0x6b6d78,0x6b6d80,0x6b6d9c,0x6b6da8,0x6b6dac,0x6b6dbc)),
 ('destroy',0x6b6cc4,(0x6b6ccc,0x6b6cd8,0x6b6d00,0x6b6d1c,0x6b6d24,0x6b6d28,0x6b6d2c,0x6b6d38,0x6b6d40,0x6b6d50)),
 ('parameter',0x6b6ab8,(0x6b6ab8,0x6b6adc,0x6b6af0)),
)
FACTS={
    0x6b9acc:('a84f00f0','adrp x8, #0x10b0000','class install begins: adrp/add of 0x10b0c80 then store into [x0]'),
    0x6b9ad0:('08013291','add x8, x8, #0xc80',''),
    0x6b9ad8:('080000f9','str x8, [x0]','vtable header 0x10b0c80 stored at object+0'),
    0x6b9b50:('48510090','adrp x8, #0x10e1000',''),
    0x6b9b5c:('08410091','add x8, x8, #0x10','secondary add of 0x10e19e0+0x10'),
    0x6b9b60:('680200f9','str x8, [x19]','final [x0] overwritten with 0x10e19e0+0x10 (base-class header)'),
    0x6b9488:('08e44039','ldrb w8, [x0, #0x39]','reads object+0x39 before any work'),
    0x6b9490:('089c41b9','ldr w8, [x0, #0x19c]','reads controller id word object+0x19c'),
    0x6b94f4:('680e43f9','ldr x8, [x19, #0x618]','loads handle object+0x618'),
    0x6b950c:('60000054','b.eq #0x6b9518',''),
    0x6b9514:('11faff97','bl #0x6b7d58','calls 6b7d58 when the resolved controller differs from the handle'),
    0x6b9518:('680643f9','ldr x8, [x19, #0x608]','loads object+0x608'),
    0x6b9524:('28fbff97','bl #0x6b81c4','calls 6b81c4 when object+0x608 is null'),
    0x6b952c:('e480f497','bl #0x3d98bc','guard call 3d98bc gates the rest of the update'),
    0x6b9538:('73e2ff97','bl #0x6b1f04','calls 6b1f04 (reset-if-needed)'),
    0x6b9540:('62e3ff97','bl #0x6b22c8','calls 6b22c8 (per-entry play)'),
    0x6b95cc:('26e2fa97','bl #0x571e64','calls 571e64 with the resolved handle payload'),
    0x6b1a0c:('08504639','ldrb w8, [x0, #0x194]','reads object+0x194'),
    0x6b1a10:('e8072037','tbnz w8, #4, #0x6b1b0c','tbnz bit4: whole reset body skipped when set'),
    0x6b1a1c:('a09ff497','bl #0x3d989c','calls 3d989c with w1=3'),
    0x6b1a5c:('68b200b9','str w8, [x19, #0xb0]','writes 1 into object+0xb0'),
    0x6b1a68:('0001803d','str q0, [x8]','zeroes 16 bytes at object+0x108'),
    0x6b1a84:('7f1a01b9','str wzr, [x19, #0x118]','zeroes word object+0x118'),
    0x6b1a88:('7ffe15a9','stp xzr, xzr, [x19, #0x158]','zeroes pair object+0x158'),
    0x6b1a8c:('7faa00f9','str xzr, [x19, #0x150]','zeroes object+0x150'),
    0x6b1ae0:('c9038052','mov w9, #0x1e','loads w9=0x1e used by the following record'),
    0x6b1b08:('7f220639','strb wzr, [x19, #0x188]','clears byte object+0x188 at the end of the reset'),
    0x6b1c6c:('2220f597','bl #0x3f9cf4','calls 3f9cf4 before inspecting the message id'),
    0x6b1c70:('9f420071','cmp w20, #0x10','compares incoming w1 with 0x10'),
    0x6b1c8c:('e1031f2a','mov w1, wzr','w1=0 passed to the tail call'),
    0x6b1c94:('01000014','b #0x6b1c98','tail 6b1c98 with w1=0'),
    0x6b1ca0:('a1000036','tbz w1, #0, #0x6b1cb4','tbz w1 bit0: skip the 6b2050/6b1b1c pair'),
    0x6b1ca8:('ea000094','bl #0x6b2050','calls 6b2050 when w1 bit0 is set'),
    0x6b1cb0:('9bffff97','bl #0x6b1b1c','calls 6b1b1c when w1 bit0 is set'),
    0x6b1cb4:('68524639','ldrb w8, [x19, #0x194]','reads object+0x194'),
    0x6b1cb8:('08012037','tbnz w8, #4, #0x6b1cd8','tbnz bit4: skip rebuild'),
    0x6b1cc0:('66010094','bl #0x6b2258','calls 6b2258 (rebuild)'),
    0x6b1cc8:('8f000094','bl #0x6b1f04','calls 6b1f04 (reset-if-needed)'),
    0x6b1cd4:('7d010014','b #0x6b22c8','tail 6b22c8'),
    0x6b225c:('08504639','ldrb w8, [x0, #0x194]','reads object+0x194'),
    0x6b2260:('08032037','tbnz w8, #4, #0x6b22c0','tbnz bit4: rebuild suppressed'),
    0x6b2268:('001840f9','ldr x0, [x0, #0x30]','loads object+0x30'),
    0x6b2270:('c5b4f497','bl #0x3df584','calls 3df584 and tests bit0'),
    0x6b227c:('e1fdff97','bl #0x6b1a00','calls 6b1a00 (full field reset)'),
    0x6b2284:('b5130094','bl #0x6b7158','calls 6b7158'),
    0x6b2288:('68de40f9','ldr x8, [x19, #0x1b8]','loads object+0x1b8'),
    0x6b2294:('b1160094','bl #0x6b7d58','calls 6b7d58 (build output)'),
    0x6b229c:('ca170094','bl #0x6b81c4','calls 6b81c4 (build controller)'),
    0x6b22a4:('d2120094','bl #0x6b6dec','calls 6b6dec (evaluate/collect)'),
    0x6b22ac:('4c130094','bl #0x6b6fdc','calls 6b6fdc (apply)'),
    0x6b22b0:('61220891','add x1, x19, #0x208','x1 = object+0x208'),
    0x6b22bc:('67160014','b #0x6b7c58','tail 6b7c58 with (object, object+0x208)'),
    0x6b4c00:('08204639','ldrb w8, [x0, #0x188]','reads object+0x188 (initialized byte)'),
    0x6b4c08:('68000035','cbnz w8, #0x6b4c14','cbnz: skip rebuild when already initialized'),
    0x6b4c10:('92f5ff97','bl #0x6b2258','calls 6b2258 when not initialized'),
    0x6b4c14:('689e41b9','ldr w8, [x19, #0x19c]','reads controller id word object+0x19c'),
    0x6b4c1c:('680643f9','ldr x8, [x19, #0x608]','loads object+0x608'),
    0x6b4c24:('089940f9','ldr x8, [x8, #0x130]','loads object+0x608 -> +0x130'),
    0x6b4c2c:('608a44bd','ldr s0, [x19, #0x488]','loads float object+0x488'),
    0x6b4c30:('000100bd','str s0, [x8]','stores the float through the controller instance'),
    0x6b4c34:('60224639','ldrb w0, [x19, #0x188]','returns object+0x188'),
    0x6b27f0:('c05100d0','adrp x0, #0x10ec000','adrp/add forming 0x10ecb08'),
    0x6b27f8:('00202c91','add x0, x0, #0xb08','adds 0xb08 to the 0x10ec000 page'),
    0x6b2810:('8e9bf497','bl #0x3d9648','calls 3d9648 with the container'),
    0x6b282c:('899641b9','ldr w9, [x20, #0x194]','reads element+0x194'),
    0x6b2830:('29011a32','orr w9, w9, #0x40','sets bit6 (0x40) of element+0x194'),
    0x6b2834:('899601b9','str w9, [x20, #0x194]','writes the flag back'),
    0x6b283c:('17fdff97','bl #0x6b1c98','calls 6b1c98(el, 0)'),
    0x6b2848:('08791912','and w8, w8, #0xffffffbf','clears bit6 of element+0x194'),
    0x6b284c:('889601b9','str w8, [x20, #0x194]','writes the cleared flag back'),
    0x6b1f0c:('001840f9','ldr x0, [x0, #0x30]','loads object+0x30'),
    0x6b1f14:('9cb5f497','bl #0x3df584','calls 3df584'),
    0x6b1f18:('40020036','tbz w0, #0, #0x6b1f60','tbz bit0: skip the reset body'),
    0x6b1f20:('9a000094','bl #0x6b2188','calls 6b2188'),
    0x6b1f24:('688e41b9','ldr w8, [x19, #0x18c]','reads word object+0x18c'),
    0x6b1f38:('d9b6f497','bl #0x3dfa9c','calls 3dfa9c(object+0x30, 0x10e8960)'),
    0x6b1f44:('16160094','bl #0x6b779c','calls 6b779c'),
    0x6b1f4c:('9d150094','bl #0x6b75c0','calls 6b75c0 and masks the result to one bit'),
    0x6b1f5c:('68260639','strb w8, [x19, #0x189]','writes the bit into object+0x189'),
    0x6b1f70:('6b1ff597','bl #0x3f9d1c','calls 3f9d1c'),
    0x6b1f78:('0a000094','bl #0x6b1fa0','calls 6b1fa0'),
    0x6b1f7c:('68425239','ldrb w8, [x19, #0x490]','reads byte object+0x490'),
    0x6b1f88:('32000094','bl #0x6b2050','calls 6b2050 when object+0x490 is set'),
    0x6b1f90:('9cfeff97','bl #0x6b1a00','calls 6b1a00'),
    0x6b1f9c:('7b000014','b #0x6b2188','tail 6b2188'),
    0x6b205c:('130441f9','ldr x19, [x0, #0x208]','loads object+0x208'),
    0x6b2064:('08f040f9','ldr x8, [x0, #0x1e0]','loads object+0x1e0'),
    0x6b2070:('889e41b9','ldr w8, [x20, #0x19c]','reads word object+0x19c'),
    0x6b207c:('890643f9','ldr x9, [x20, #0x608]','loads object+0x608'),
    0x6b2084:('289540f9','ldr x8, [x9, #0x128]','loads object+0x608 -> +0x128'),
    0x6b2094:('299d40f9','ldr x9, [x9, #0x138]','loads object+0x608 -> +0x138'),
    0x6b20ac:('f6060094','bl #0x6b3c84','calls 6b3c84(instance sums, object+0x220, entry payload)'),
    0x6b20b8:('7a340094','bl #0x6bf2a0','calls 6bf2a0'),
    0x6b20c4:('11340094','bl #0x6bf108','calls 6bf108'),
    0x6b20d0:('3f340094','bl #0x6bf1cc','calls 6bf1cc'),
    0x6b20d4:('889241b9','ldr w8, [x20, #0x190]','reads word object+0x190'),
    0x6b20f0:('cba1f997','bl #0x51a81c','allocates 0x40 bytes through 51a81c'),
    0x6b2110:('88de40f9','ldr x8, [x20, #0x1b8]','loads object+0x1b8'),
    0x6b2140:('87340094','bl #0x6bf35c','calls 6bf35c with w2=1'),
    0x6b2144:('880a5239','ldrb w8, [x20, #0x482]','reads byte object+0x482'),
    0x6b2184:('e1350014','b #0x6bf908','tail 6bf908'),
    0x6b22d8:('799df497','bl #0x3d98bc','calls 3d98bc'),
    0x6b22e0:('68264639','ldrb w8, [x19, #0x189]','reads byte object+0x189'),
    0x6b22f0:('688e41b9','ldr w8, [x19, #0x18c]','reads word object+0x18c'),
    0x6b22fc:('68be40f9','ldr x8, [x19, #0x178]','loads object+0x178'),
    0x6b2304:('74b640f9','ldr x20, [x19, #0x168]','loads object+0x168'),
    0x6b2310:('8afcff97','bl #0x6b1538','calls 6b1538(entry)'),
    0x6b231c:('e9fcfa97','bl #0x5716c0','calls 5716c0'),
    0x6b2324:('94fbfa97','bl #0x571174','calls 571174'),
    0x6b1b2c:('000443f9','ldr x0, [x0, #0x608]','loads object+0x608'),
    0x6b1b34:('680e43f9','ldr x8, [x19, #0x618]','loads object+0x618'),
    0x6b1b50:('141540f9','ldr x20, [x8, #0x28]','loads handle payload +0x28'),
    0x6b1b58:('1bfbfa97','bl #0x5707c4','calls 5707c4'),
    0x6b1b64:('df03fb97','bl #0x572ae0','calls 572ae0'),
    0x6b1b68:('681643f9','ldr x8, [x19, #0x628]','loads object+0x628'),
    0x6b1b84:('60021591','add x0, x19, #0x540','stores zero into object+0x608'),
    0x6b1b8c:('b7b8f797','bl #0x49fe68','calls 49fe68(object+0x540)'),
    0x6b1b90:('689e41b9','ldr w8, [x19, #0x19c]','reads word object+0x19c'),
    0x6b1b9c:('05000094','bl #0x6b1bb0','calls 6b1bb0 when the id is zero'),
    0x6b1cec:('080443f9','ldr x8, [x0, #0x608]','loads object+0x608'),
    0x6b1cf4:('099c41b9','ldr w9, [x0, #0x19c]','reads word object+0x19c'),
    0x6b1cf8:('148d40f9','ldr x20, [x8, #0x118]','loads object+0x608 -> +0x118'),
    0x6b1d60:('9f0200eb','cmp x20, x0','compares the resolved object with the cached one'),
    0x6b1d6c:('6cffff97','bl #0x6b1b1c','calls 6b1b1c when they differ'),
    0x6b6ab8:('080c43f9','ldr x8, [x0, #0x618]','loads object+0x618'),
    0x6b6adc:('099041b9','ldr w9, [x0, #0x190]','reads word object+0x190'),
    0x6b6af0:('5cf0fa17','b #0x572c60','tail 572c60 with w1=0 or 3'),
    0x6b6e08:('8effff97','bl #0x6b6c40','calls 6b6c40 (controller resolve)'),
    0x6b6e14:('8ffeff97','bl #0x6b6850','calls 6b6850'),
    0x6b6e18:('689e41b9','ldr w8, [x19, #0x19c]','reads word object+0x19c'),
    0x6b6e78:('68be40f9','ldr x8, [x19, #0x178]','reads object+0x178'),
    0x6b6e90:('085940f9','ldr x8, [x8, #0xb0]','loads vtable slot +0xb0 of the resolved object'),
    0x6b6e94:('00013fd6','blr x8','indirect call through +0xb0'),
    0x6b6ec8:('8c030094','bl #0x6b7cf8','calls 6b7cf8(scratch, object+0x5e8, 1)'),
    0x6b6ed4:('63400094','bl #0x6c7060','calls 6c7060(scratch, object+0x1a0)'),
    0x6b6efc:('8fe9ff97','bl #0x6b1538','calls 6b1538(entry)'),
    0x6b6f0c:('086140f9','ldr x8, [x8, #0xc0]','loads entry vtable slot +0xc0'),
    0x6b6f10:('00013fd6','blr x8','indirect call through +0xc0 with object+0x518'),
    0x6b6f30:('c0f3ff97','bl #0x6b3e30','calls 6b3e30(scratch)'),
    0x6b6f48:('b1eeff97','bl #0x6b2a0c','calls 6b2a0c(object+0x208)'),
    0x6b6f58:('908e0094','bl #0x6da998','calls 6da998(object+0x1c8, object+0x228)'),
    0x6b6f74:('1aefff97','bl #0x6b2bdc','calls 6b2bdc(object, scratch, object+0x208, object+0x1b8)'),
    0x6b6fa4:('51efff97','bl #0x6b2ce8','calls 6b2ce8(object, object+0x1b8, object+0x208, object+0xb0, object+0x640)'),
    0x6b6fbc:('68220639','strb w8, [x19, #0x188]','writes cset(object+0x208!=0) into object+0x188'),
    0x6b6ff0:('01e00691','add x1, x0, #0x1b8','x1 = object+0x1b8'),
    0x6b6ff4:('02200891','add x2, x0, #0x208','x2 = object+0x208'),
    0x6b6ff8:('04001991','add x4, x0, #0x640','x4 = object+0x640'),
    0x6b6ffc:('e30314aa','mov x3, x20','x3 = object+0xb0'),
    0x6b7004:('39efff97','bl #0x6b2ce8','calls 6b2ce8 with the four in-object ranges'),
    0x6b701c:('e00315aa','mov x0, x21','calls 6b1538(entry)'),
    0x6b7030:('afefff97','bl #0x6b2eec','calls 6b2eec(entry_obj, object+0xb0)'),
    0x6b7044:('084d40f9','ldr x8, [x8, #0x98]','loads entry_obj vtable slot +0x98'),
    0x6b7048:('00013fd6','blr x8','indirect call through +0x98'),
    0x6b7064:('695642f9','ldr x9, [x19, #0x4a8]','loads object+0x4a8'),
    0x6b7068:('7f461239','strb wzr, [x19, #0x491]','clears byte object+0x491'),
    0x6b7070:('6a4e42f9','ldr x10, [x19, #0x498]','loads object+0x498'),
    0x6b70a0:('6bb140f9','ldr x11, [x11, #0x160]','loads the entry payload +0x160'),
    0x6b70b0:('68461239','strb w8, [x19, #0x491]','writes the OR of the tests into object+0x491'),
    0x6b6d70:('1f200639','strb wzr, [x0, #0x188]','stores zero into object+0x188'),
    0x6b6d78:('5c050094','bl #0x6b82e8','calls 6b82e8(object+0x5e8)'),
    0x6b6d80:('23efff97','bl #0x6b2a0c','calls 6b2a0c(object+0x208)'),
    0x6b6d9c:('e7e9ff97','bl #0x6b1538','calls 6b1538(entry)'),
    0x6b6da8:('001040f9','ldr x0, [x0, #0x20]','loads entry_obj+0x20'),
    0x6b6dac:('a2eefa97','bl #0x572834','calls 572834'),
    0x6b6dbc:('5c050094','bl #0x6b832c','calls 6b832c(entry_obj, object+0xb0)'),
    0x6b6ccc:('085442f9','ldr x8, [x0, #0x4a8]','loads object+0x4a8'),
    0x6b6cd8:('694e42f9','ldr x9, [x19, #0x498]','loads object+0x498'),
    0x6b6d00:('bf600094','bl #0x6ceffc','calls 6ceffc'),
    0x6b6d1c:('60da40f9','ldr x0, [x19, #0x1b0]','loads object+0x1b0'),
    0x6b6d24:('62b60094','bl #0x6e46ac','calls 6e46ac(object+0x1b0, object+0x228)'),
    0x6b6d28:('68224639','ldrb w8, [x19, #0x188]','reads byte object+0x188'),
    0x6b6d2c:('7fda00f9','str xzr, [x19, #0x1b0]','stores zero into object+0x1b0'),
    0x6b6d38:('0a000094','bl #0x6b6d60','calls 6b6d60'),
    0x6b6d40:('2b000094','bl #0x6b6dec','calls 6b6dec'),
    0x6b6d50:('a3000014','b #0x6b6fdc','tail 6b6fdc'),

    0x6b19cc:('00013fd6','blr x8','indirect call through object+0x1b8 entry vtable slot +0x38'),
    0x6b1b80:('00013fd6','blr x8','indirect call through object+0x628 payload vtable slot +0x28'),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name):
    path,pin=PROBES[name];raw=(ROOT/path).read_bytes()
    if sha(raw)!=pin:raise SystemExit(f'probe pin mismatch: {path}')
    return json.load(gzip.open(path)),pin,len(raw)
def windows(*probes):
    out={}
    for r in probes:
        for w in r['windows']:
            code=bytes.fromhex(w['hex'])
            old=out.get(w['va'])
            if old is not None and old[:len(code)]!=code[:len(old)]:raise SystemExit(f'window conflict at {w["va"]:#x}')
            if old is None or len(code)>len(old):out[w['va']]=code
    return out
def owner_of(pc,followed):
    best=None
    for f in followed:
        u=f.get('unwind')
        if u and u['start']<=pc<u['end']:best=f['entry'] if best is None else best
    return best
def build():
    a,pa,sa=load('owner130');b,pb,sb=load('owner130b')
    for r in (a,b):
        assert r['xapk_sha256']==XAPK_SHA and r['libunity_sha256']==LIBUNITY_SHA and r['libunity_size']==17783496
        assert r['provisional'] is True
    win=windows(a,b)
    spans=sorted((w,code) for w,code in win.items())
    def at(va):
        for w,code in spans:
            if w<=va<w+len(code):return code[va-w:]
            if w>va:break
        return None
    rows=[];bad=[]
    for va,(hexd,text,note) in sorted({**FACTS,**NOTES}.items()):
        code=at(va)
        ok=code is not None and len(code)>=4 and code[:4].hex()==hexd
        rows.append(dict(va=va,bytes_hex=hexd,instruction=text,note=note,verified=ok))
        if not ok:bad.append(va)
    if bad:raise SystemExit('facts not present in pinned probes: '+','.join(hex(x) for x in bad))
    followed={}
    for r in (a,b):
        for f in r['followed']:followed.setdefault(f['entry'],f)
    edges=set()
    for r in (a,b):
        for c in r['callsites']:edges.add((c['target'],c['pc'],c['kind'],c['word_hex']))
    call_rows=[dict(target=t,pc=pc,kind=k,word_hex=wh,caller_start=owner_of(pc,list(followed.values()))) for t,pc,k,wh in sorted(edges)]
    members=[]
    for r,tag in ((a,'owner130'),(b,'owner130b')):
        for s in r['slot_membership']:
            if s['table_start']!=VTABLE:continue
            members.append(dict(vtable=VTABLE,slot_index=s['slot_index'],slot_count=s['slot_count'],
                                target=s['target'],role=ROLES.get(s['slot_index'],''),probe=tag))
    uniq={}
    for m in members:uniq[(m['slot_index'],m['target'])]=m
    members=[dict(m,refs_in_vtable_slots=1) for _,m in sorted(uniq.items())]
    direct=defaultdict(int)
    for c in call_rows:direct[c['target']]+=1
    for m in members:m['direct_code_refs']=direct.get(m['target'],0)
    field=defaultdict(lambda: defaultdict(list))
    for r in rows:
        if not r['note']:continue
        found=re.findall(r'\[(x(?:0|19|20|23)), #(0x[0-9a-f]+)\]',r['instruction'])
        kind=r['instruction'].split()[0]
        if not found or not kind.startswith(('ldr','str','ldp','stp','ldur','stur')):continue
        for reg,offtxt in found:
            off=int(offtxt,16)
            if f'object+{off:#x}' not in r['note']:continue
            field[off][(kind[0]=='l' and 'load' or 'store')].append(r['va'])
    field_rows=[]
    for off in sorted(field):
        ents=[]
        for direction in ('load','store'):
            pcs=sorted(field[off].get(direction,[]))
            if pcs:ents.append(dict(direction=direction,count=len(pcs),pcs=pcs))
        field_rows.append(dict(offset=off,accesses=ents,total=sum(e['count'] for e in ents),
                               note=next((r['note'] for r in rows if r['note'] and f'#{off:#x}' in r['note']),'')))
    indirect=sorted(r['va'] for r in rows if r['instruction'].startswith('blr'))
    merged={**FACTS,**NOTES}
    chain=[]
    for stage,entry,pcs in CHAIN:
        miss=[hex(x) for x in pcs if x not in merged]
        if miss:raise SystemExit(f'chain facts missing for {stage}: {miss}')
        calls=[]
        for x in pcs:
            m=re.match(r'(?:bl|b) #0x([0-9a-f]+)$',merged[x][1])
            if m:calls.append(int(m.group(1),16))
        chain.append(dict(stage=stage,entry=entry,fact_pcs=list(pcs),calls=calls))
    related=defaultdict(list)
    for r in rows:
        for subj,offtxt in re.findall(r'(element|entry_obj|handle|instance)\+(0x[0-9a-f]+)',r['note']):
            related[(subj,int(offtxt,16))].append(r['va'])
    related_rows=[dict(subject=k[0],offset=k[1],pcs=sorted(v),count=len(v)) for k,v in sorted(related.items())]
    res=dict(provisional=True,chain=dict(count=len(chain),rows=chain),related_offsets=dict(count=len(related_rows),rows=related_rows),
        sources=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=17783496,
                     probes={k:dict(path=v[0],sha256=np,size=ns) for k,(v,np,ns) in
                             {'owner130':(PROBES['owner130'],pa,sa),'owner130b':(PROBES['owner130b'],pb,sb)}.items()},
                     tools={t:sha((ROOT/t).read_bytes()) for t in TOOLS}),
        vtable=dict(base=VTABLE,slot_count=35,members=members),
        facts=dict(count=len(rows),rows=rows),
        field_map=dict(count=len(field_rows),offsets=field_rows),
        call_edges=dict(count=len(call_rows),unique_targets=len({c['target'] for c in call_rows}),rows=call_rows),
        indirect=dict(blr_sites=indirect,blr_count=len(indirect),
                      virtual_slots=[m['slot_index'] for m in members],
                      unresolved=['contents of registry [0x10e18b0]','the object behind handle +0x618',
                                  'all vtable targets of the indirect calls','class names of every entry']),
        counts=dict(facts=len(rows),chain_stages=len(chain),related_offsets=len(related_rows),annotated=sum(1 for r in rows if r['note']),field_offsets=len(field_rows),
                    vtable_members=len(members),call_sites=len(call_rows),indirect_calls=len(indirect),
                    followed_a=len(a['followed']),followed_b=len(b['followed']),windows=len(win)),
        limits=['Static bytes only: no instruction was executed in this cycle.',
                'Caller closure is depth<=2 and does not follow virtual dispatch.',
                'Registry contents, handle payloads and class names are not recovered.',
                'Field offsets are bracket accesses on x0/x19/x20/x23 only; other base registers are ignored.'])
    return res
def render(res):
    return gzip.compress((json.dumps(res,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true')
    args=ap.parse_args();res=build();blob=render(res);out=ROOT/ARTIFACT
    if args.write:
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob);print('wrote',out,len(blob),sha(blob))
    if args.check:
        cur=out.read_bytes()
        if cur!=blob:raise SystemExit(f'artifact drift: {ARTIFACT}')
        print('check ok',ARTIFACT,len(blob),sha(blob))
    if not args.write and not args.check:
        print(json.dumps(res['counts'],sort_keys=True))
if __name__=='__main__':main()
