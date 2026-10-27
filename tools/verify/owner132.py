"""Cycle 132 verifier: do the dispatch-candidate owners touch the animator?

Everything here is recomputed from the pinned probe bytes: the owner bodies are decoded
again (direct BL/B targets, cluster membership, global references, vtable dispatch sites,
signature field offsets) and compared with what the probe recorded. Slot numbers are then
resolved against the vtable membership committed in cycle 130, whose SHA is pinned here.

No instruction is executed and no class name is claimed.
"""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
LIBUNITY_SIZE=17783496
PROBE=('reverse-engineering/raw/owner132/probe.json.gz','2a6ddfff033acca079842b7da2db8c359b9737f7b77c85ab252f015d3ceea69d')
PROBE_B=('reverse-engineering/raw/owner132b/probe.json.gz','89f39fdea833628c8162f808f7d4d4e7327925c26b5e4bdb7577d2f05f89c54b')
UPSTREAM={'130':('datas/l3_ef6b75ef130_native_update_trigger.json.gz','6afffcec6902b22285f1b46c84fa3f2a0221967bd7ef2b3b45471b88299c8057'),
          '131':('datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz','70cb303b9a306e7851d3911282ee81342e6d1d910be368fda039ac2590377198')}
TOOLS=('tools/recovery/owner132.py','tools/recovery/owner132b.py','tools/verify/owner132.py')
ARTIFACT='datas/l3_ef6b75ef132_native_dispatch_owners.json.gz'
CLUSTER=(0x6b0000,0x6c0000)
FIELDS=(0x188,0x194,0x19c,0x1b8,0x208,0x488,0x608,0x618,0x4a8,0x498)
SLOT_OFFSETS={2:0x10,3:0x18,10:0x50,31:0xf8,33:0x108}
BUILDER=0x6b7d58
BUILDER_FACTS={
 0x6b7d7c:('089c41b9','ldr w8, [x0, #0x19c]','reads the controller id'),
 0x6b7d84:('a80e0034','cbz w8, #0x6b7f58','id 0 skips the whole graph build'),
 0x6b7dd8:('600e43f9','ldr x0, [x19, #0x618]','existing handle'),
 0x6b7ddc:('000100b4','cbz x0, #0x6b7dfc','null handle branches to allocation'),
 0x6b7dfc:('21f8fa97','bl #0x575e80','allocates the 0xe0-byte output object'),
 0x6b7e00:('680240f9','ldr x8, [x19]','reads the animator vptr from the object itself'),
 0x6b7e08:('e00313aa','mov x0, x19','receiver is the animator'),
 0x6b7e0c:('082940f9','ldr x8, [x8, #0x50]','vtable slot 10'),
 0x6b7e10:('00013fd6','blr x8','dispatches slot 10 on the animator (resolves to 3e079c)'),
 0x6b7e18:('40d0ffb0','adrp x0, #0xc0000','page of the name string'),
 0x6b7e1c:('00383f91','add x0, x0, #0xfce','0xc0fce = "%s.Animator" (cycle 129)'),
 0x6b7e74:('600e03f9','str x0, [x19, #0x618]','stores the created handle'),
 0x6b7e78:('612206b9','str w1, [x19, #0x620]','stores the handle version word'),
 0x6b7e7c:('691643f9','ldr x9, [x19, #0x628]','existing output handle'),
 0x6b7ec0:('41d2ffd0','adrp x1, #0x101000','page of the output type name'),
 0x6b7ec4:('21441091','add x1, x1, #0x411','0x101411 = "AnimatorOuput" (cycle 129)'),
 0x6b7ec8:('63000094','bl #0x6b8054','creates the output object'),
 0x6b7ed4:('601603f9','str x0, [x19, #0x628]','stores the output handle'),
 0x6b7edc:('e00314aa','mov x0, x20','receiver is the output object'),
 0x6b7ee8:('08008012','mov w8, #-1','sentinel'),
 0x6b7eec:('88de00b9','str w8, [x20, #0xdc]','output+0xdc = -1 (cycle 129)'),
 0x6b7ef0:('610643f9','ldr x1, [x19, #0x608]','controller instance as argument'),
 0x6b7ef8:('880240f9','ldr x8, [x20]','output vptr'),
 0x6b7f00:('e2031f2a','mov w2, wzr','third argument 0'),
 0x6b7f04:('081540f9','ldr x8, [x8, #0x28]','output vtable slot +0x28'),
 0x6b7f08:('00013fd6','blr x8','dispatches output+0x28 (resolves to 6ce4fc)'),
 0x6b7f0c:('680e43f9','ldr x8, [x19, #0x618]','handle re-read'),
 0x6b7f34:('689241b9','ldr w8, [x19, #0x190]','animation mode word'),
 0x6b7f40:('0115881a','cinc w1, w8, eq','w1 = 1 or 2 depending on mode==2'),
 0x6b7f44:('4eebfa97','bl #0x572c7c','applies the mode word to the payload'),
 0x6b7f48:('680240f9','ldr x8, [x19]','animator vptr again'),
 0x6b7f50:('088540f9','ldr x8, [x8, #0x108]','vtable slot 33'),
 0x6b7f54:('00013fd6','blr x8','dispatches slot 33 on the animator (resolves to 6b6ab8)'),
 0x6b7f58:('e00313aa','mov x0, x19','fall-through target for the id-0 and null paths'),
 0x6b7f60:('685642f9','ldr x8, [x19, #0x4a8]','driver array count'),
 0x6b7f68:('774e42f9','ldr x23, [x19, #0x498]','driver array base'),
 0x6b7f6c:('e80240f9','ldr x8, [x23]','first array entry'),
 0x6b7fec:('888e40f9','ldr x8, [x20, #0x118]','owner field recovered in cycle 129'),
 0x6b8000:('089d40f9','ldr x8, [x8, #0x138]','owner slot +0x138'),
 0x6b8004:('00013fd6','blr x8','gate call through the owner slot'),
 0x6b8010:('f35b0094','bl #0x6cefdc','calls the per-node producer recovered in cycle 129'),
 0x6b802c:('a81640f9','ldr x8, [x21, #0x28]','stack canary reload'),
 0x6b8050:('1c8b2794','bl #0x109acc0','canary failure path; the target has no FDE'),
}
THUNKS={0x6b08c0:'mov w1, #8 / mov w2, #8 / b 0x3f1e30',
        0x6b08d8:'mov w1, #8 / mov w2, #8 / b 0x3f1e30',
        0x6b08e4:'mov w1, #8 / mov w2, #8 / b 0x3f1e30'}
EDGES=((10,0x6b7e0c,0x6b7e10,8,'x19'),(33,0x6b7f50,0x6b7f54,8,'x19'),(0x28,0x6b7f04,0x6b7f08,8,'x20'))

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
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return (w&31,(w>>5)&31,sg((w>>12)&0x1FF,9))
    return None
def is_blr(w):return w&0xFFFFFC1F==0xD63F0000

def decode_body(code,entry,extent):
    """Recompute calls/globals/dispatch/fields from the raw body bytes only."""
    words=list(struct.unpack_from('<%dI'%(len(code)//4),code))
    calls=[];glob=[];dispatch=[];fields=Counter()
    adrp_reg={}
    for i,w in enumerate(words):
        pc=entry+i*4
        t=bl_target(w,pc)
        if t is not None:
            ext=extent or 0
            intra=entry<=t<entry+ext
            calls.append(dict(pc=pc,target=t,kind='bl' if w>>31 else 'b',
                              intra=intra,in_cluster=(not intra) and CLUSTER[0]<=t<CLUSTER[1]))
            continue
        a=adrp(w,pc)
        if a:
            adrp_reg[a[0]]=a[1]
            for k in range(1,5):
                if i+k>=len(words):break
                add=add_imm(words[i+k])
                if add and add[0]==a[0]:
                    tgt=a[1]+add[1]
                    if tgt in (0x10ecb08,0x10e18b0,0x10e19c8,0x10e19d0,0x10e18f8,0x10e18b8):
                        glob.append(dict(pc=pc,target=tgt))
                    break
            continue
        ld=ldr_off(w)
        if ld:
            rt,rn,off=ld
            if off in FIELDS:fields[off]+=1
            if off in SLOT_OFFSETS.values():
                slot=next(k for k,v in SLOT_OFFSETS.items() if v==off)
                blr_pc=None
                for k in range(1,9):
                    if i+k>=len(words):break
                    if is_blr(words[i+k]) and ((words[i+k]>>5)&31)==rt:blr_pc=entry+(i+k)*4;break
                if blr_pc is None:continue
                prov='unknown';prov_pc=None
                for k in range(1,7):
                    if i-k<0:break
                    p2=ldr_off(words[i-k])
                    if p2 and p2[0]==rn:prov=f'vptr_from_x{p2[1]}';prov_pc=entry+(i-k)*4;break
                    a2=adrp(words[i-k],entry+(i-k)*4)
                    if a2 and a2[0]==rn:prov='adrp_base';prov_pc=entry+(i-k)*4;break
                dispatch.append(dict(slot=slot,ldr_pc=pc,blr_pc=blr_pc,base_reg=rn,base_kind=prov,provenance_pc=prov_pc))
    return calls,glob,dispatch,fields

def build():
    path,pin=PROBE;raw=(ROOT/path).read_bytes()
    if sha(raw)!=pin:raise SystemExit('probe sha mismatch')
    p=json.load(gzip.open(path))
    if p['xapk_sha256']!=XAPK_SHA or p['libunity_sha256']!=LIBUNITY_SHA or p['libunity_size']!=LIBUNITY_SIZE:
        raise SystemExit('probe pin mismatch')
    up={}
    for k,(path2,pin2) in UPSTREAM.items():
        b=(ROOT/path2).read_bytes()
        if sha(b)!=pin2:raise SystemExit(f'upstream pin mismatch: {path2}')
        up[k]=json.loads(gzip.decompress(b))
    slots={m['slot_index']:m['target'] for m in up['130']['vtable']['members']}
    owners=[]
    for o in p['owners']:
        code=bytes.fromhex(o['hex'])
        calls,glob,dispatch,fields=decode_body(code,o['entry'],o['extent'])
        # self-consistency against what the probe recorded
        raw_cluster=sum(1 for c in calls if CLUSTER[0]<=c['target']<CLUSTER[1])
        for a,b in ((len(calls),len(o['calls'])),
                    (raw_cluster,len(o['cluster_calls'])),
                    (len(glob),len(o['globals'])),
                    (len(dispatch),len(o['dispatch'])),
                    (sum(fields.values()),sum(o['fields'].values()))):
            if a!=b:raise SystemExit(f'probe/decode disagreement for {o["entry"]:#x}: {a} != {b}')
        entry=o['entry']
        rows=[dict(slot=d['slot'],ldr_pc=d['ldr_pc'],blr_pc=d['blr_pc'],base_reg=d['base_reg'],
                   base_kind=d['base_kind'],provenance_pc=d['provenance_pc'],
                   resolved_target=slots.get(d['slot']) if d['slot'] in slots else None,
                   resolution_source='cycle130 vtable 10b0c80 membership' if d['slot'] in slots else None)
              for d in dispatch]
        f=dict(slot31_dispatch_owner=0.0) if False else None
        owners.append(dict(entry=entry,group=o['group'],extent=o['extent'],window_bytes=o['window_bytes'],
                           file_offset=o['file_offset'],body_sha256=sha(code),body_words=len(code)//4,
                           calls=calls,call_count=len(calls),
                           bl_count=sum(1 for c in calls if c['kind']=='bl'),
                           b_external_count=sum(1 for c in calls if c['kind']=='b' and not c['intra']),
                           intra_branch_count=sum(1 for c in calls if c['intra']),
                           cluster_calls=[c for c in calls if c['in_cluster']],
                           cluster_call_count=sum(1 for c in calls if c['in_cluster']),
                           cluster_intra=sum(1 for c in calls if c['intra'] and CLUSTER[0]<=c['target']<CLUSTER[1]),
                           globals=glob,global_count=len(glob),
                           dispatch=rows,dispatch_slots=[d['slot'] for d in rows],
                           fields={hex(k):v for k,v in sorted(fields.items())},
                           caller_count=len(o['callers']),callers_capped=o.get('callers_capped',False)))
    def group(name):
        g=[o for o in owners if o['group']==name]
        return dict(owners=len(g),calls=sum(o['call_count'] for o in g),
                    bl_calls=sum(o['bl_count'] for o in g),
                    b_external=sum(o['b_external_count'] for o in g),
                    intra_branches=sum(o['intra_branch_count'] for o in g),
                    cluster_calls=sum(o['cluster_call_count'] for o in g),
                    cluster_targets=sorted({c['target'] for o in g for c in o['cluster_calls']}),
                    global_refs=sum(o['global_count'] for o in g),
                    field_hit_owners=sorted(o['entry'] for o in g if o['fields']),
                    dispatch_sites=sum(len(o['dispatch']) for o in g),
                    dispatch_by_slot=dict(Counter(s for o in g for s in o['dispatch_slots'])),
                    entries=sorted(o['entry'] for o in g))
    agg=dict(slot31=group('slot31_dispatch_owner'),batch=group('batch_container_owner'),
             incluster=group('incluster_slot33_owner'))
    b=next(o for o in owners if o['entry']==BUILDER)
    facts=[]
    for va,(hx,text,note) in sorted(BUILDER_FACTS.items()):
        off=va-BUILDER
        ok=0<=off<len(bytes.fromhex(next(x for x in p['owners'] if x['entry']==BUILDER)['hex'])) and \
           bytes.fromhex(next(x for x in p['owners'] if x['entry']==BUILDER)['hex'])[off:off+4].hex()==hx
        facts.append(dict(va=va,bytes_hex=hx,instruction=text,note=note,verified=ok))
        if not ok:raise SystemExit(f'builder fact missing at {va:#x}')
    edges=[]
    for slot,ldr_pc,blr_pc,reg,base in EDGES:
        edges.append(dict(slot=slot,ldr_pc=ldr_pc,blr_pc=blr_pc,base_reg=reg,base_kind=base,
                          resolved_target=slots.get(slot) if slot in slots else None,
                          resolution_source='cycle130 vtable 10b0c80 membership' if slot in slots else 'output vtable 10b0f30 (not resolved this cycle)'))
    pbpath,pbpin=PROBE_B;pbraw=(ROOT/pbpath).read_bytes()
    if sha(pbraw)!=pbpin:raise SystemExit('stage-2 probe sha mismatch')
    pb=json.load(gzip.open(pbpath))
    if pb['libunity_sha256']!=LIBUNITY_SHA:raise SystemExit('stage-2 libunity pin mismatch')
    callees=[dict(address=t['address'],owner=t['owner'],interior=t['interior'],extent=t['extent'],
                  offset_in_fde=t['offset_in_fde'],head_hex=t.get('head_hex'),
                  thunk=THUNKS.get(t['address'])) for t in pb['targets']]
    res=dict(provisional=True,
        pins=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=LIBUNITY_SIZE,
                  probe=dict(path=path,sha256=sha(raw),size=len(raw)),
                  probe_stage2=dict(path=pbpath,sha256=sha(pbraw),size=len(pbraw)),
                  upstream={k:dict(path=v[0],sha256=v[1]) for k,v in UPSTREAM.items()},
                  tools={t:sha((ROOT/t).read_bytes()) for t in TOOLS}),
        cluster=list(CLUSTER),fields=list(FIELDS),slot_offsets={str(k):v for k,v in SLOT_OFFSETS.items()},
        vtable_slots={str(k):v for k,v in sorted(slots.items())},
        owners=owners,aggregate=agg,
        graph_builder=dict(entry=BUILDER,extent=b['extent'],window_bytes=b['window_bytes'],
                           body_sha256=b['body_sha256'],facts=facts,edges=edges,
                           cluster_calls=b['cluster_calls'],
                           called_targets=sorted({c['target'] for c in b['calls']})),
        callees=dict(fde_count=pb['fde_count'],rows=callees,
                     own_fde=[t['address'] for t in callees if t['owner']==t['address']],
                     interior=[t['address'] for t in callees if t['interior']],
                     unattributed=[t['address'] for t in callees if t['owner'] is None],
                     thunks=[dict(address=k,bytes=m) for k,m in sorted(THUNKS.items())]),
        negative=dict(slot31_owners=agg['slot31']['owners'],
                      slot31_cluster_calls=agg['slot31']['cluster_calls'],
                      slot31_global_refs=agg['slot31']['global_refs'],
                      slot31_field_hit_owners=agg['slot31']['field_hit_owners'],
                      statement=('No owner of a generic slot-31 dispatch site calls into 0x6b0000..0x6c0000 '
                                 'or references the six containers; the only in-cluster dispatch of the '
                                 'recovered slots happens inside 6b7d58 on its own receiver.')),
        counts=dict(owners=len(owners),facts=len(facts),edges=len(edges),
                    slot31_owners=agg['slot31']['owners'],batch_owners=agg['batch']['owners'],
                    cluster_calls_total=sum(o['cluster_call_count'] for o in owners),
                    bl_total=sum(o['bl_count'] for o in owners),
                    b_external_total=sum(o['b_external_count'] for o in owners),
                    intra_total=sum(o['intra_branch_count'] for o in owners),
                    callees=len(callees),
                    dispatch_sites=sum(len(o['dispatch']) for o in owners),
                    callers=sum(o['caller_count'] for o in owners)),
        limits=['Bodies are the original FDE extents, capped at 0x1000 bytes; longer functions are truncated.',
                'Direct BL/B only; no indirect flow, no execution.',
                'Slot numbers come from a fixed offset map; a matching load is not class evidence by itself.',
                'Slot resolution reuses the cycle-130 vtable membership; the output vtable +0x28 is not resolved here.',
                'Field-offset hits are generic; only the graph-builder body is annotated instruction by instruction.'])
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
