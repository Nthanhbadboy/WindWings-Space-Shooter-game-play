"""Cycle 131 verifier: static reachability/dispatch scan of the animator vtable slots.

Every claim is re-derived from the pinned probe: the 35 byte facts are checked against
the stored snippets, the ADRP+ADD targets are recomputed from those bytes, and the slot
loads are re-decoded from the site windows. Nothing is executed.
"""
import argparse,gzip,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
XAPK_SHA='f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
LIBUNITY_SHA='d827b83ec91b39cee2cc010b646c1336eeabf2611f92c1b9bea2be03ccfa35b7'
PROBE=('reverse-engineering/raw/owner131/probe.json.gz','a685acffa0c5b93f3c7392fe8ef2ac90cb0e288cf5ae742902050df699f852c9')
TOOL='tools/verify/owner131.py'
ARTIFACT='datas/l3_ef6b75ef131_native_vtable_dispatch.json.gz'
FACTS={
    0x6b15f8:('e84f00f0','adrp x8, #0x10b0000','adrp page of vtable 0x10b0c80 in the helper at 6b15d4'),
    0x6b9acc:('a84f00f0','adrp x8, #0x10b0000','adrp page of vtable 0x10b0c80 in the installer 6b9ac4'),
    0x6ce47c:('084f00d0','adrp x8, #0x10b0000','adrp page of 0x10b0f30 (output vtable)'),
    0x6ceb94:('094f00f0','adrp x9, #0x10b1000','adrp page of 0x10b1000 (node ctor table pair)'),
    0x6ceb98:('084f00d0','adrp x8, #0x10b0000','second adrp of the same page in the node ctor'),
    0x6d3550:('e84e00d0','adrp x8, #0x10b1000','adrp page of 0x10b1000 in ctor 6d353c'),
    0x6d3554:('ea4e00d0','adrp x10, #0x10b1000','second adrp of the same page in ctor 6d353c'),
    0x6d28b4:('e94e00f0','adrp x9, #0x10b1000','adrp page of 0x10b1000 in factory 6d2894'),
    0x6d291c:('e84e00f0','adrp x8, #0x10b1000','adrp page of 0x10b1000 in factory 6d28fc'),
    0x47f7f0:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load followed by blr in owner 0x47f5f0'),
    0x47f7f4:('00013fd6','blr x8','blr consuming the slot 31 value'),
    0x5558ac:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x555524'),
    0x5558b0:('00013fd6','blr x8','blr consuming it'),
    0x5fc1bc:('287d40f9','ldr x8, [x9, #0xf8]','slot 31 load with x9 base in owner 0x5fc17c'),
    0x5fc1c0:('00013fd6','blr x8','blr consuming it'),
    0x60a380:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x60a324'),
    0x60a384:('00013fd6','blr x8','blr consuming it'),
    0x66cec4:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x66cde8'),
    0x66cec8:('00013fd6','blr x8','blr consuming it'),
    0x6f29fc:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x6f29c0'),
    0x6f2a0c:('00013fd6','blr x8','blr consuming it'),
    0x8b3a0c:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x8b3644'),
    0x8b3a18:('00013fd6','blr x8','blr consuming it'),
    0x8b6278:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x8b5e5c'),
    0x8b627c:('00013fd6','blr x8','blr consuming it'),
    0x8e1f74:('087d40f9','ldr x8, [x8, #0xf8]','slot 31 load in owner 0x8e1ecc'),
    0x8e1f78:('00013fd6','blr x8','blr consuming it'),
    0x3e07b0:('096800b0','adrp x9, #0x10e1000','adrp page of the accessor fallback table 0x10e19c8 inside 3e079c'),
    0x6b27f0:('c05100d0','adrp x0, #0x10ec000','adrp of the batch container 0x10ecb08 inside 6b27dc'),
    0x6b23c8:('d35100d0','adrp x19, #0x10ec000','adrp of the batch container in 6b23b8'),
    0x6b1730:('88510090','adrp x8, #0x10e1000','adrp of 0x10e18f8 inside the helper at 6b15d4'),
    0x6a74cc:('295200b0','adrp x9, #0x10ec000','adrp of the batch container in 6a74b8'),
    0x6b9b90:('805100f0','adrp x0, #0x10ec000','second code reference to the batch container'),
    0x5d4fd8:('c1580090','adrp x1, #0x10ec000','adrp of the batch container in 5d4fd0'),
    0x94cf54:('013d0090','adrp x1, #0x10ec000','adrp of the batch container in 94cf10'),
}
def sha(b):return hashlib.sha256(b).hexdigest()
def sg(v,n):return v-(1<<n) if v&(1<<(n-1)) else v
def adrp(w,pc):
    if w&0x9F000000!=0x90000000:return None
    return (w&31,(pc&~0xFFF)+(sg(((w>>5)&0x7FFFF)<<2|((w>>29)&3),21)<<12))
def add_imm(w):
    if w&0xFFC00000!=0x91000000:return None
    return ((w>>5)&31,w&31,((w>>10)&0xFFF)<<(12 if w&(1<<22) else 0))
def ldr_off(w):
    if w&0xFFC00000==0xF9400000:return ((w>>10)&0xFFF)*8
    if w&0xFFE00C00 in (0xF8400000,0xF8400400,0xF8400C00):return sg((w>>12)&0x1FF,9)
    return None
def snippets(p):
    out=[]
    for slot,v in p['sites'].items():
        for r in v['qualified']+v['other']:
            if r.get('window_hex'):
                out.append((r['ldr_pc']-4,bytes.fromhex(r['window_hex'])))
    for group in (p['vtable_refs'],p['global_refs']):
        for rows in group.values():
            for r in rows:out.append((r['pc'],bytes.fromhex(r['hex'])))
    for w in p['windows']:out.append((w['va'],bytes.fromhex(w['hex'])))
    return sorted(out)
def at(snips,va,n=4):
    for st,b in snips:
        if st<=va and va+n<=st+len(b):return b[va-st:va-st+n]
    return None
def build():
    path,pin=PROBE;raw=(ROOT/path).read_bytes()
    if sha(raw)!=pin:raise SystemExit('probe sha mismatch')
    p=json.load(gzip.open(path))
    if p['xapk_sha256']!=XAPK_SHA or p['libunity_sha256']!=LIBUNITY_SHA or p['libunity_size']!=17783496:
        raise SystemExit('probe pin mismatch')
    snips=snippets(p)
    rows=[]
    for va,(hx,text,note) in sorted(FACTS.items()):
        b=at(snips,va)
        ok=b is not None and b.hex()==hx
        rows.append(dict(va=va,bytes_hex=hx,instruction=text,note=note,verified=ok))
        if not ok:raise SystemExit(f'fact missing at {va:#x}')
    mat=[]
    for table,refs in sorted(p['vtable_refs'].items()):
        t=int(table,16);rs=[]
        for r in refs:
            a=adrp(struct.unpack('<I',at(snips,r['pc'],4))[0],r['pc'])
            w=struct.unpack('<I',bytes.fromhex(r['add_hex']))[0]
            add=add_imm(w)
            target=None
            if a and add and add[0]==a[0]:target=a[1]+add[2]
            rs.append(dict(pc=r['pc'],add_pc=r['add_pc'],owner=r['owner'],target=target,recomputed=target==t))
        mat.append(dict(table=t,count=len(rs),refs=rs))
    fam=[f for f in p['family'] if f not in {m['table'] for m in mat}]
    disp=[]
    for slot in ('2','3','31','33'):
        v=p['sites'][slot]
        q=v['qualified'];offs=p['slot_offsets'][slot]
        check=[]
        for r in q:
            w0=r['ldr_pc'];code=at(snips,w0,4)
            ok=code is not None and ldr_off(struct.unpack('<I',code)[0])==offs
            check.append(ok)
        owners=[r['owner'] for r in q if r['owner']]
        disp.append(dict(slot=int(slot),offset=offs,matches=v['matches'],with_blr=v['with_blr'],
                         qualified_stored=len(q),other_stored=v['other_count'],
                         qualified_owners=len(set(owners)),
                         in_cluster=sum(1 for o in set(owners) if 0x6b0000<=o<0x6c0000),
                         outside_cluster=sum(1 for o in set(owners) if not 0x6b0000<=o<0x6c0000),
                         slot_bytes_ok=all(check),ldr_offsets_recomputed=len(check)))
    slot31=[dict(ldr_pc=r['ldr_pc'],blr_pc=r['blr_pc'],base_kind=r['base_kind'],owner=r['owner'])
            for r in p['sites']['31']['qualified']]
    gl=[]
    for addr,refs in sorted(p['global_refs'].items(),key=lambda kv:-len(kv[1])):
        gl.append(dict(addr=int(addr,16),count=len(refs),capped=len(refs)>=64,
                       owners=sorted({r['owner'] for r in refs if r['owner']})))
    res=dict(provisional=True,
        pins=dict(xapk_sha256=XAPK_SHA,libunity_sha256=LIBUNITY_SHA,libunity_size=17783496,
                  probe=dict(path=path,sha256=sha(raw),size=len(raw)),tools={TOOL:sha((ROOT/TOOL).read_bytes())}),
        scan=dict(text=p['text'],family=p['family'],slots=p['slots'],slot_offsets=p['slot_offsets'],
                  globals=p['globals'],cluster=p['cluster'],owners=p['owners'] and len(p['owners'])),
        vtable_materialization=dict(total=sum(m['count'] for m in mat),tables=mat,unreferenced=fam),
        dispatch=dict(per_slot=disp,slot31=slot31),
        globals=gl,
        callers=dict(count=len(p['callers']),capped=p['caller_capped'],rows=p['callers']),
        facts=dict(count=len(rows),rows=rows),
        counts=dict(facts=len(rows),tables=len(mat),materializations=sum(m['count'] for m in mat),
                    slot31_matches=p['sites']['31']['matches'],slot31_with_blr=p['sites']['31']['with_blr'],
                    slot31_qualified=len(slot31),owners=len(p['owners']),callers=len(p['callers']),
                    global_rows=sum(g['count'] for g in gl)),
        limits=['Static scan only: no instruction was executed in this cycle.',
                'Slot offsets 0x10/0x18/0xf8/0x108 are generic vtable indices; a matching load is not evidence of the animator class.',
                'Base provenance looks back at most 6 words and only accepts LDR-from-x0 or ADRP.',
                'Stored site rows are capped at 64 per slot; match counts are exact.',
                'Owner attribution comes from the FDE table; functions without an FDE are reported as null.'])
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
