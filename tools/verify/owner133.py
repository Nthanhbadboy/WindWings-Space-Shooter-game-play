"""Cycle 133 verifier: the graph builder's own helper chain.

The 22 recovered bodies are decoded again from the pinned probe bytes (calls, dispatch sites,
referenced strings, bracket accesses) and cross-checked against what the probe recorded. The
annotated facts are re-checked byte for byte, and slot numbers are resolved against the pinned
cycle-129 vtable membership. Nothing is executed; no class name is claimed.
"""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
LIBUNITY_SIZE=17783496
PROBE=('reverse-engineering/raw/owner133/probe.json.gz','8bb964b16017f2637b3403dacb0deb36788a5b36600d58fc25bedd3d74a90ee6')
UPSTREAM={'129':('datas/l3_ef6b75ef129_native_owner_linkage.json.gz','217f8893799733f1f36c9d73ac93ab0b9ca903ead81501492b9bab89fb85071a'),
          '132':('datas/l3_ef6b75ef132_native_dispatch_owners.json.gz','5037ba3b2641ca31c2860ec69cf142f69b8ab90591e6ad88d4838a1a66bc876d')}
TOOLS=('tools/recovery/owner133.py','tools/verify/owner133.py')
ARTIFACT='datas/l3_ef6b75ef133_native_builder_helpers.json.gz'
CLUSTER=(0x6b0000,0x6c0000)
ALLOC_CALLER=0x6b8054
BIND=0x6b97d0
UNBIND=0x6b9638
REFRESH=0x6b92c4
PRODUCER=0x6cefdc
COLLECTOR=0x6b7c58
REFRESHER=0x6b80e0
SET_PLAYABLE=0x6ce4b4
DESTRUCTORS=(0x6b753c,0x6b3e30)
GROWTH=(0x6bba08,0x6b9f6c)
FACTS={
    0x570528:('000840f9','ldr x0, [x0, #0x10]','handle field at +0x10'),
    0x570530:('54160094','bl #0x575e80','fetch the singleton when the handle is null'),
    0x570534:('6b160094','bl #0x575ee0','create a handle from the singleton'),
    0x570538:('600a00f9','str x0, [x19, #0x10]','store the handle'),
    0x57053c:('012040b9','ldr w1, [x0, #0x20]','handle version word'),
    0x570540:('131400f9','str x19, [x0, #0x28]','handle payload back-pointer set to the object'),
    0x575e80:('a85f00f0','adrp x8, #0x116c000','returns a global singleton pointer'),
    0x575e84:('00a145f9','ldr x0, [x8, #0xb40]','load from 0x116cb40'),
    0x575e88:('c0035fd6','ret','no arguments, no side effects'),
    0x576a6c:('001040f9','ldr x0, [x0, #0x20]','second handle field at +0x20'),
    0x576a74:('a85f00d0','adrp x8, #0x116c000','singleton page'),
    0x576a7c:('2cfdff97','bl #0x575f2c','different creator (575f2c)'),
    0x576a80:('601200f9','str x0, [x19, #0x20]','store the handle'),
    0x576a88:('131400f9','str x19, [x0, #0x28]','handle payload back-pointer'),
    0x6b14bc:('1f0000f9','str xzr, [x0]','zeroes the record pointer'),
    0x6b14c0:('1f0800b9','str wzr, [x0, #8]','zeroes the record count'),
    0x6b14c8:('1f1800b9','str wzr, [x0, #0x18]','zeroes the record version word'),
    0x6b14d4:('6415fb97','bl #0x576a64','handle from 576a64'),
    0x6b14d8:('600200f9','str x0, [x19]','record+0 = handle'),
    0x6b14e0:('610a00b9','str w1, [x19, #8]','record+8 = handle version'),
    0x6b14f4:('b4fcfa97','bl #0x5707c4','identity from 5707c4 when the payload exists'),
    0x6b1504:('895100b0','adrp x9, #0x10e2000','otherwise the global default at 0x10e2248'),
    0x6b1514:('680a00f9','str x8, [x19, #0x10]','record+0x10 = identity payload'),
    0x6b151c:('691a00b9','str w9, [x19, #0x18]','record+0x18 = identity version'),
    0x6b1520:('884640b9','ldr w8, [x20, #0x44]','reads playable+0x44'),
    0x6b1528:('682200b9','str w8, [x19, #0x20]','record+0x20 = max(0, that word)'),
    0x6b3e38:('000040f9','ldr x0, [x0]','same shape as 6b753c: wrapped pointer at +0'),
    0x6b3e40:('68624039','ldrb w8, [x19, #0x18]','same release flag at +0x18'),
    0x6b3e54:('c3608052','mov w3, #0x306','same line 0x306'),
    0x6b3e58:('7855f497','bl #0x3c9438','same dealloc sink 3c9438'),
    0x6b3e5c:('7f0200f9','str xzr, [x19]','clears the slot'),
    0x6b7544:('000040f9','ldr x0, [x0]','wrapped pointer'),
    0x6b7548:('200100b4','cbz x0, #0x6b756c','null pointer is a no-op'),
    0x6b754c:('68624039','ldrb w8, [x19, #0x18]','byte flag at +0x18'),
    0x6b7550:('e8000037','tbnz w8, #0, #0x6b756c','bit0 set means already released'),
    0x6b7554:('610a40b9','ldr w1, [x19, #8]','tracked size word'),
    0x6b7558:('a2d3ffd0','adrp x2, #0x12d000','page of 0x12da21'),
    0x6b7560:('c3608052','mov w3, #0x306','source line 0x306'),
    0x6b7564:('b547f497','bl #0x3c9438','dealloc sink 3c9438 (cycle 127)'),
    0x6b7568:('7f0200f9','str xzr, [x19]','clears the slot'),
    0x6b7c68:('080441f9','ldr x8, [x0, #0x208]','requires animator+0x208 to be set'),
    0x6b7c70:('290040f9','ldr x9, [x1]','source container: count at +0x10, base at +0x18'),
    0x6b7c78:('2a0940f9','ldr x10, [x9, #0x10]','element stride 0x20'),
    0x6b7c7c:('5f050071','cmp w10, #1','nothing to do when the count is below 1'),
    0x6b7c88:('4ae97bd3','lsl x10, x10, #5','count<<5 = byte size'),
    0x6b7c94:('14801391','add x20, x0, #0x4e0','destination vector at animator+0x4e0'),
    0x6b7ca4:('2a0940b9','ldr w10, [x9, #8]','record type tag at record+8'),
    0x6b7ca8:('5f590071','cmp w10, #0x16','only tag 0x16 is collected'),
    0x6b7cb0:('370d40f9','ldr x23, [x9, #0x18]','collected value pointer at record+0x18'),
    0x6b7cb4:('1f0117eb','cmp x8, x23','deduplicates consecutive equal values'),
    0x6b7cc8:('390f0094','bl #0x6bb9ac','append through 6bb9ac'),
    0x6b7cd8:('690240f9','ldr x9, [x19]','reload the container base each iteration'),
    0x6b805c:('a3d3ffb0','adrp x3, #0x12d000','page of the empty label 0x12da21'),
    0x6b8068:('63842891','add x3, x3, #0xa21','0x12d000+0xa21 = 0x12da21 (same empty label as cycles 127/129)'),
    0x6b806c:('001c8052','mov w0, #0xe0','allocation size 0xe0 (the output object size from cycle 129)'),
    0x6b8070:('c10b8052','mov w1, #0x5e','allocator tag 0x5e'),
    0x6b8074:('02018052','mov w2, #8','alignment 8'),
    0x6b8078:('c40a8052','mov w4, #0x56','source line 0x56'),
    0x6b807c:('8744f497','bl #0x3c9298','original allocator 3c9298(size, tag, align, label, line)'),
    0x6b808c:('f6580094','bl #0x6ce464','ctor 6ce464(new_object, name, owner)'),
    0x6b8090:('a9e20191','add x9, x21, #0x78','head of the intrusive list at owner+0x78'),
    0x6b8094:('68220091','add x8, x19, #8','link fields start at new_object+8'),
    0x6b8098:('3f0108eb','cmp x9, x8','if the list head already points at the new object there is nothing to splice'),
    0x6b80a0:('0a0140f9','ldr x10, [x8]','current first node'),
    0x6b80a8:('6b0a40f9','ldr x11, [x19, #0x10]','previous tail'),
    0x6b80ac:('4b0500f9','str x11, [x10, #8]','tail->next = new'),
    0x6b80b0:('6aae40a9','ldp x10, x11, [x19, #8]','reads both link words'),
    0x6b80b4:('6a0100f9','str x10, [x11]','first->prev = tail'),
    0x6b80b8:('1f7d00a9','stp xzr, xzr, [x8]','clears the new object links'),
    0x6b80bc:('2a0140f9','ldr x10, [x9]','old head value'),
    0x6b80c0:('6aa600a9','stp x10, x9, [x19, #8]','new_object[8]=old_head, new_object[0x10]=&owner+0x78'),
    0x6b80c4:('480500f9','str x8, [x10, #8]','old_head->prev = &new_object+8'),
    0x6b80c8:('690a40f9','ldr x9, [x19, #0x10]','owner list tail'),
    0x6b80cc:('280100f9','str x8, [x9]','tail->next = &new_object+8'),
    0x6b80d0:('e00313aa','mov x0, x19','returns the created object'),
    0x6b80ec:('14601291','add x20, x0, #0x498','driver vector at animator+0x498'),
    0x6b80f8:('69eafa97','bl #0x572a9c','clears the vector through 572a9c'),
    0x6b80fc:('68be40f9','ldr x8, [x19, #0x178]','playable count at +0x178'),
    0x6b8104:('75b640f9','ldr x21, [x19, #0x168]','playable base at +0x168'),
    0x6b8110:('0ae5ff97','bl #0x6b1538','resolve the playable entry (6b1538)'),
    0x6b811c:('001040f9','ldr x0, [x0, #0x20]','entry payload at +0x20'),
    0x6b8120:('c5e9fa97','bl #0x572834','572834 test'),
    0x6b8124:('c0000037','tbnz w0, #0, #0x6b813c','skip when the test bit is set'),
    0x6b8128:('c80240f9','ldr x8, [x22]','entry vptr'),
    0x6b8134:('085540f9','ldr x8, [x8, #0xa8]','entry vtable slot +0xa8, called with the driver vector'),
    0x6b8154:('685642f9','ldr x8, [x19, #0x4a8]','second loop: driver records at +0x498 / +0x4a8'),
    0x6b8188:('d3640094','bl #0x6d14d4','per-record 6d14d4 returns a word'),
    0x6b818c:('68ba44b9','ldr w8, [x19, #0x4b8]','running accumulator at +0x4b8'),
    0x6b819c:('1f00086b','cmp w0, w8','keep the larger of the two'),
    0x6b81ac:('68ba04b9','str w8, [x19, #0x4b8]','stores the accumulator back'),
    0x6b92cc:('61e3ff97','bl #0x6b2050','step 1: skin (6b2050, cycle 130)'),
    0x6b92d4:('a3f6ff97','bl #0x6b6d60','step 2: clear (6b6d60)'),
    0x6b92dc:('c4f6ff97','bl #0x6b6dec','step 3: evaluate (6b6dec)'),
    0x6b92e8:('3df7ff17','b #0x6b6fdc','step 4: apply via tail branch (6b6fdc)'),
    0x6b9654:('169441b9','ldr w22, [x0, #0x194]','reads the guard word at +0x194'),
    0x6b9658:('b6052037','tbnz w22, #4, #0x6b970c','bit 4 diverts to the assert path'),
    0x6b966c:('0809088b','add x8, x8, x8, lsl #2','count*0x28 = byte size'),
    0x6b96a0:('21a00091','add x1, x1, #0x28','walks 0x28-byte records'),
    0x6b96b4:('9b852794','bl #0x109ad20','compacting move 109ad20'),
    0x6b96c4:('68be00f9','str x8, [x19, #0x178]','decrements the recorded count'),
    0x6b96c8:('8df6fa97','bl #0x5770fc','5770fc on the removed playable'),
    0x6b96d4:('1f0008eb','cmp x0, x8','if it was the current controller handle...'),
    0x6b96e4:('7f0603f9','str xzr, [x19, #0x608]','...the handle is cleared'),
    0x6b96e8:('e099f797','bl #0x49fe68','and the vector at +0x540 is reset'),
    0x6b96f4:('36053836','tbz w22, #7, #0x6b9798','bit 7 of the guard word'),
    0x6b96fc:('e8040034','cbz w8, #0x6b9798','and the initialized byte +0x188'),
    0x6b9704:('f0feff97','bl #0x6b92c4','refresh through 6b92c4'),
    0x6b970c:('60d3ffb0','adrp x0, #0x126000','assert string 0x126b27: Cannot unbind playable while the Animator is being evaluated.'),
    0x6b97ec:('08504639','ldrb w8, [x0, #0x194]','guard byte at +0x194'),
    0x6b97f0:('e8042037','tbnz w8, #4, #0x6b988c','bit 4 diverts to the assert path'),
    0x6b97fc:('08bc40f9','ldr x8, [x0, #0x178]','playable count'),
    0x6b9840:('9f020aeb','cmp x20, x10','already bound is a no-op'),
    0x6b985c:('05f5fa97','bl #0x576c70','576c70 maps the playable to a handle'),
    0x6b9864:('680643f9','ldr x8, [x19, #0x608]','compares with the current controller handle +0x608'),
    0x6b9878:('0ddfff97','bl #0x6b14ac','builds the 0x28 record through 6b14ac'),
    0x6b9884:('98080094','bl #0x6bbae4','pushes it through 6bbae4'),
    0x6b988c:('a0d0ffd0','adrp x0, #0xcf000','assert string 0xcf1dc: Cannot bind playable while the Animator is being evaluated.'),
    0x6b9f6c:('03058052','mov w3, #0x28','insert thunk: element size 0x28, alignment 8'),
    0x6b9f74:('50dff417','b #0x3f1cb4','tail branch into 3f1cb4'),
    0x6bb9b8:('152041a9','ldp x21, x8, [x0, #0x10]','vector count at +0x10 and capacity at +0x18'),
    0x6bb9c4:('b6060091','add x22, x21, #1','count+1'),
    0x6bb9c8:('df0648eb','cmp x22, x8, lsr #1','capacity check (capacity>>1)'),
    0x6bb9d0:('760a00f9','str x22, [x19, #0x10]','stores the new count'),
    0x6bb9d8:('880240f9','ldr x8, [x20]','value pointer argument'),
    0x6bb9e4:('080940b9','ldr w8, [x8, #8]','reads the int at value+8'),
    0x6bba00:('02000094','bl #0x6bba08','growth helper for 4-byte elements'),
    0x6bba08:('81008052','mov w1, #4','growth thunk: element size 4, alignment 4'),
    0x6bba10:('08d9f417','b #0x3f1e30','tail branch into the shared array helper 3f1e30'),
    0x6bbaf0:('152041a9','ldp x21, x8, [x0, #0x10]','vector count and capacity'),
    0x6bbb18:('a022099b','madd x0, x21, x9, x8','element address = base + count*0x28'),
    0x6bbb1c:('0000803d','str q0, [x0]','copies 16 bytes'),
    0x6bbb28:('080800f9','str x8, [x0, #0x10]','record+0x10'),
    0x6bbb30:('081800b9','str w8, [x0, #0x18]','record+0x18'),
    0x6bbb3c:('082000b9','str w8, [x0, #0x20]','record+0x20'),
    0x6bbb4c:('02000094','bl #0x6bbb54','growth helper for 0x28-byte elements'),
    0x6ce4c0:('006840f9','ldr x0, [x0, #0xd0]','previous playable at +0xd0'),
    0x6ce4cc:('e10313aa','mov x1, x19','unbind the previous one (6b9638)'),
    0x6ce4d4:('746a00f9','str x20, [x19, #0xd0]','stores the new playable'),
    0x6ce4ec:('b9acff17','b #0x6b97d0','bind through the tail branch (6b97d0)'),
    0x6cefdc:('fe4fbfa9','stp x30, x19, [sp, #-0x10]!','per-node producer entry'),
    0x6cefe4:('f4010094','bl #0x6cf7b4','first builds the node graph (6cf7b4, cycles 127/129)'),
    0x6cefe8:('680240f9','ldr x8, [x19]','node vptr'),
    0x6ceff0:('017140f9','ldr x1, [x8, #0xe0]','vtable slot +0xe0'),
    0x6ceff8:('20001fd6','br x1','tail branch into the slot; the producer never returns to its caller'),
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
                    # keep the nearest ldr for this blr (one indirect call, one base)
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
        # the probe counted one row per ldr that reaches a blr; here each blr keeps its nearest ldr
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
                           fields=fields,field_count=len(fields),
                           dispatch_rows_raw=len(f['dispatch']),
                           strings=f['strings'],ret_count=f['ret_count']))
    by={b['entry']:b for b in bodies}
    facts=[];snips={b['entry']:b for b in bodies}
    wins={f['entry']:bytes.fromhex(f['hex']) for f in p['functions']}
    for va,(hx,text,note) in sorted(FACTS.items()):
        code=None
        for e,w in wins.items():
            if e<=va<e+len(w):code=w;base=e;break
        ok=code is not None and code[va-base:va-base+4].hex()==hx
        facts.append(dict(va=va,bytes_hex=hx,instruction=text,note=note,verified=ok))
        if not ok:raise SystemExit('fact missing at %#x'%va)
    def facts_at(entry):
        entry_va=by[entry]['entry'];n=by[entry]['extent']
        return [f['va'] for f in facts if entry_va<=f['va']<entry_va+n]
    # --- focus blocks -------------------------------------------------
    create=dict(entry=ALLOC_CALLER,extent=by[ALLOC_CALLER]['extent'],
                alloc=dict(size=0xe0,tag=0x5e,align=8,label=0x12da21,line=0x56),
                ctor=by[ALLOC_CALLER]['calls'][1]['target'] if len(by[ALLOC_CALLER]['calls'])>1 else None,
                list_anchor_offset=0x78,
                fact_pcs=facts_at(ALLOC_CALLER),
                call_targets=[c['target'] for c in by[ALLOC_CALLER]['calls']])
    record=dict(stride=0x28,base_field=0x168,count_field=0x178,
                handle_field=0x00,version_field=0x08,identity_field=0x10,identity_version_field=0x18,
                aux_field=0x20,push=0x6bbae4,insert=0x6b9994,builder=0x6b14ac)
    binding=dict(bind=BIND,unbind=UNBIND,setter=SET_PLAYABLE,
                 guard=dict(field=0x194,bit=4),
                 assert_bind=dict(va=0xcf1dc,hex='0xcf1dc'),
                 assert_unbind=dict(va=0x126b27,hex='0x126b27'),
                 strings=[s for e in (BIND,UNBIND) for s in by[e]['strings']],
                 refresh_rule=dict(guard_bit=7,requires_initialized=0x188,action=REFRESH),
                 bind_call_targets=[c['target'] for c in by[BIND]['calls']],
                 unbind_call_targets=[c['target'] for c in by[UNBIND]['calls']])
    refresh=dict(entry=REFRESH,extent=by[REFRESH]['extent'],
                 steps=[c['target'] for c in by[REFRESH]['calls']],
                 tail=[c['target'] for c in by[REFRESH]['calls'] if c['kind']=='b'])
    prod=dict(entry=PRODUCER,extent=by[PRODUCER]['extent'],
              first_call=by[PRODUCER]['calls'][0]['target'],
              vtable_slot=0xe0,tail_branch=True,
              resolved_target=slots.get(0xe0),
              resolution_source='cycle-129 vtable membership (node primary table)')
    coll=dict(entry=COLLECTOR,extent=by[COLLECTOR]['extent'],source_field=0x208,
              container_count_field=0x10,container_base_field=0x18,stride=0x20,
              type_tag_field=0x08,type_tag=0x16,value_field=0x18,
              destination=0x4e0,append=0x6bb9ac,
              append_value_source='object+8')
    refresher=dict(entry=REFRESHER,extent=by[REFRESHER]['extent'],
                   driver_vector=0x498,playable_base=0x168,playable_count=0x178,
                   entry_slot=0xa8,accumulator=0x4b8,per_record=0x6d14d4,
                   dispatch=[d['slot'] for d in by[REFRESHER]['dispatch']])
    destructors=[dict(entry=e,extent=by[e]['extent'],
                      sink=[c['target'] for c in by[e]['calls'] if not c['intra']],
                      line=0x306,label=0x12da21) for e in DESTRUCTORS]
    growth=[dict(entry=e,extent=by[e]['extent'],thunk=by[e]['words']) for e in GROWTH]
    const=[dict(address=t['address'],bytes=t['bytes']) for t in up['132']['callees']['thunks']]
    res=dict(provisional=True,
        pins=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=LIBUNITY_SIZE,
                  probe=dict(path=path,sha256=sha(raw),size=len(raw)),
                  upstream={k:dict(path=v[0],sha256=v[1]) for k,v in UPSTREAM.items()},
                  tools={t:sha((ROOT/t).read_bytes()) for t in TOOLS}),
        cluster=list(CLUSTER),seeds=p['seeds'],order=p['order'],
        bodies=bodies,
        focus=dict(create_output=create,playable_record=record,playable_binding=binding,
                   refresh_composite=refresh,producer=prod,collector=coll,refresher=refresher,
                   destructors=destructors,growth_thunks=growth),
        slot_resolution=dict(slots={str(k):v for k,v in sorted(slots.items())},
                             source='cycle-129 vtable_family called_slots'),
        correction=dict(previous_cycle='132',
                        previous_reading='the three 0x6b08xx helpers are generic temporary/argument thunks',
                        current_reading=('they are array-growth thunks of the same family as 6bba08: fixed element '
                                         'size + alignment forwarded to the shared helper 3f1e30'),
                        evidence=[dict(address=0x6bba08,element=4,align=4,target=0x3f1e30),
                                  dict(address=0x6b9f6c,element=0x28,align=8,target=0x3f1cb4)],
                        prior_132_thunks=const),
        counts=dict(bodies=len(bodies),facts=len(facts),
                    seeds=sum(1 for b in bodies if b['group']=='seed'),
                    followed=sum(1 for b in bodies if b['group']=='cluster_callee'),
                    calls=sum(b['call_count'] for b in bodies),
                    bl=sum(b['bl_count'] for b in bodies),
                    cluster_calls=sum(len(b['cluster_calls']) for b in bodies),
                    dispatch=sum(len(b['dispatch']) for b in bodies),
                    dispatch_rows_raw=sum(b['dispatch_rows_raw'] for b in bodies),
                    strings=sum(len(b['strings']) for b in bodies),
                    windows_bytes=sum(b['window_bytes'] for b in bodies)),
        limits=['One follow level for in-cluster callees; 22 bodies, each capped at 0x800 bytes.',
                'Only BL/B and ADRP+ADD are decoded; register-indirect flow is not followed.',
                'Field rows are raw bracket accesses on x0/x19/x20 and are not class evidence.',
                'Each blr is attributed to its nearest preceding ldr of the same register; the raw probe '
                'counted one row per reaching ldr, so 2 raw rows at 0x6b8138 are 1 direct call through +0xa8.',
                'String identity comes from original .rodata bytes; no symbol table is used.',
                'No instruction was executed in this cycle; nothing here is a runtime observation.'])
    return res
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
