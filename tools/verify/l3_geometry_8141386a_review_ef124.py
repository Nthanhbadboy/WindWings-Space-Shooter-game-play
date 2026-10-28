"""Separate R1 addendum120: fixed ef124 static bytes and guarded native fixtures.
provenance: arena/8141386a-windwings-space-shooter-game-p
No producer124 verifier/Fixture import, peer edits, runtime or #27-full closure.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import json
import struct
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file
from tools.verify.geometry_8141386a_review_ef123_checks import branch,add_imm,constant_stores,decode_rela
from tools.verify.l3_geometry_8141386a_review_ef124_native import RAW,FACTORIES,replay,source_image

OUTPUT=ROOT/'datas/l3_geometry_review_ef124_8141386a.json.gz'
PEER_SCI='98e5ba9666103ca354ce3fd6116ca295b497c30d'
PEER_REPORT='ea6a3835f786306b07df9658262a6e3f6658f809'
SOURCE_HEAD='c0e25f963111136e1ff3ebe581b27b85a9b4e44f'
SOURCE_RUN=40386262470
OWN118='datas/l3_geometry_sprite_consumers_8141386a.json.gz'


def read(name):return json.loads(gzip.decompress((RAW/name).read_bytes()))


def validate_pins():
    m=json.loads((RAW/'peer-pins.json').read_bytes())
    if m['scientific_commit']!=PEER_SCI or m['report_commit']!=PEER_REPORT:raise ValueError('fixed124 review target changed')
    for p in m['pins']:
        b=(ROOT/p['snapshot']).read_bytes()
        if len(b)!=p['size'] or sha(b)!=p['sha256']:raise ValueError('peer124 snapshot changed')
        original=gzip.decompress(b) if p['encoding']=='gzip' else b
        if sha(original)!=p['source_sha256']:raise ValueError('peer124 decompressed source changed')
    return m


def audit_static(raw,peer,fresh):
    windows={}
    for r in raw['windows']+raw['cells']:
        k=(r['va'],len(r['hex'])//2);h=sha(bytes.fromhex(r['hex']))
        if k in windows and windows[k]!=h:raise ValueError('conflicting retained native spans')
        windows[k]=h
    observed={(r['va'],r['size']):r['sha256'] for r in fresh['peer_span_matches']}
    if observed!=windows or len(observed)!=149:raise ValueError('fresh original span coverage/hash mismatch')
    original_fdes={r['start']:r for r in fresh['selected_fdes']}
    if set(original_fdes)!={r['entry'] for r in raw['followed']} or len(original_fdes)!=132:raise ValueError('fresh FDE entry coverage mismatch')
    for r in raw['followed']:
        a=r['unwind'];b=original_fdes[r['entry']]
        if (a['end'],a['fde_va'],a['fde_hex'],a['table_va'],a['table_hex'])!=(b['end_exclusive'],b['fde_va'],b['fde_hex'],b['table_va'],b['table_hex']):raise ValueError('fresh original FDE/table bytes disagree')
        delta,size=struct.unpack_from('<iI',bytes.fromhex(b['fde_hex']),8)
        if b['fde_va']+8+delta!=b['start'] or b['start']+size!=b['end_exclusive']:raise ValueError('FDE arithmetic disagrees')
    relas={r['address']:r['addend'] for r in raw['relocations']};groups=[]
    for g in fresh['vtable_groups']:
        if len(g['slots'])!=16:raise ValueError('original vtable is not16 retained slots')
        expected=next(x for x in peer['vtable_groups'] if x['vptr']==g['vptr'])
        for n,r in enumerate(g['slots']):
            decoded=decode_rela(r['hex'])
            if decoded['address']!=g['vptr']+8*n or decoded['symbol']!=0 or decoded['type']!=1027 or decoded['addend']!=r['addend'] or relas.get(decoded['address'])!=decoded['addend']:raise ValueError('original relative vtable slot mismatch')
        addends=[r['addend'] for r in g['slots']]
        if addends!=expected['addends'] or not all(addends):raise ValueError('peer vtable addends differ from original')
        groups.append(dict(vptr=g['vptr'],addends=addends,original_relas=g['slots']))
    if {g['vptr'] for g in groups}!={r[1] for r in FACTORIES.values()} or len(groups)!=4:raise ValueError('vtable group coverage mismatch')
    w=next(r for r in raw['windows'] if r['va']==0x6cf7b4);code=bytes.fromhex(w['hex']);calls=[]
    for off in range(0,len(code)-3,4):
        b=branch(struct.unpack_from('<I',code,off)[0],w['va']+off)
        if b and b['link'] and b['target']in FACTORIES:calls.append(dict(pc=b['pc'],target=b['target']))
    if calls!=peer['graph_builder_callsites'] or calls!=[{k:r[k] for k in ('pc','target')} for r in fresh['graph_factory_calls']]:raise ValueError('independently decoded graph BLs differ')
    if Counter(r['target'] for r in calls)!=dict(zip(FACTORIES,(1,1,2,3))):raise ValueError('graph factory multiplicities changed')
    mappings=[]
    for entry,(ctor,vptr,offset,ret) in FACTORIES.items():
        f=next(r for r in raw['windows'] if r['va']==entry);blob=bytes.fromhex(f['hex']);old=peer['factory_metadata'][str(entry)]
        decoded=[branch(struct.unpack_from('<I',blob,i)[0],entry+i) for i in range(0,len(blob)-3,4)]
        targets=[b['target'] for b in decoded if b and b['link']]
        adds=[add_imm(struct.unpack_from('<I',blob,i)[0]) for i in range(0,len(blob)-3,4)]
        if not {0x3c986c,ctor,0x572a38}<=set(targets) or (0,2,offset)not in adds:raise ValueError('factory allocator/constructor/handle instruction mismatch')
        cw=next(r for r in raw['windows'] if r['va']==ctor);cb=bytes.fromhex(cw['hex'])
        stores=[s for s in constant_stores(cb,ctor) if s['value']==vptr and s['base_register']==19 and s['offset']==0]
        if len(stores)!=1:raise ValueError('constructor primary vptr not uniquely backed by instructions')
        ff,cf=original_fdes[entry],original_fdes[ctor]
        if ff['end_exclusive']!=ret+4 or blob[ret-entry:ret-entry+4]!=bytes.fromhex('c0035fd6'):raise ValueError('factory RET/exclusive FDE disagreement')
        ctor_ret=cf['end_exclusive']-4
        if cb[ctor_ret-ctor:ctor_ret-ctor+4]!=bytes.fromhex('c0035fd6'):raise ValueError('constructor RET not at exclusive FDE minus4')
        for k,value in dict(entry=entry,constructor=ctor,vptr=vptr,size_offset=offset,ret=ret,fde_end=ret+4,constructor_ret=ctor_ret,constructor_fde_end=cf['end_exclusive']).items():
            if old[k]!=value:raise ValueError('producer factory mapping differs:'+k)
        mappings.append(dict(entry=entry,constructor=ctor,vptr=vptr,allocator_size_offset=offset,ret=ret,fde=ff,constructor_fde=cf,constructor_ret=ctor_ret,vptr_store=stores[0],graph_call_pcs=[r['pc'] for r in calls if r['target']==entry]))
    if fresh['relative_rela_total']!=29267:raise ValueError('original relative relocation census changed')
    return dict(factories=mappings,graph_builder_calls=calls,vtable_groups=groups,matched_unique_spans=len(windows),matched_fdes=len(original_fdes),relative_rela_total=fresh['relative_rela_total'])


def audit_replays(peer):
    rows=[]
    if len(peer['standalone'])!=6:raise ValueError('fixture case coverage changed')
    for old in peer['standalone']:
        r=replay(**{k:old[k] for k in ('entry','prefill','label','extra','tag','owner_count','base')})
        if r['instruction_count']!=old['run']['instruction_count'] or r['unique_executed_addresses']!=old['run']['executed_addresses']:raise ValueError('own/producer fixture PC count/set mismatch')
        if any(r['pc_counts'].get(k,0)!=v for k,v in old['pc_hits'].items()):raise ValueError('specific native-PC multiplicity differs')
        if any(hex(p)in r['pc_counts'] for p in (0x3c986c,0x570ff0,0x109ace0,0x109acc0,0x573a1c,0x575b34)):raise ValueError('excluded service/cleanup/growth PC counted')
        n=r['node'];o=old['node']
        for k,old_k in dict(address='address',vptr='vptr',label='label_field',owner='owner_field',chunk='chunk_field',flags38='bitfield_38',halfword_a8='halfword_a8').items():
            if n[k]!=o[old_k]:raise ValueError('own prepared-state node effect differs:'+k)
        owner=old['owner_after'];pool=old['pool_after']
        if r['owner']!=dict(count=owner['count'],head=owner['list_head'],flags16=owner['flags_halfword']):raise ValueError('own native owner/list effect differs')
        if r['pool']!=dict(head=pool['queue_head'],tag=pool['queue_tag'],acquired=pool['acquired_count'],chunk_length=pool['chunk_length'],slot0=pool['slot0']):raise ValueError('own native pool effect differs')
        if len(old['allocator_records'])!=1 or len(r['allocator_calls'])!=1:raise ValueError('allocator multiplicity differs')
        a=old['allocator_records'][0]
        if r['allocator_calls'][0]['args']!=[a[k] for k in ('size','alignment','category','flag','label','aux')]:raise ValueError('allocator exact request differs')
        if r['ret']!=old['ret'] or old['service_calls'] or old['failure_calls']:raise ValueError('fixture return/service boundary differs')
        if r['entry']==0x6d25f4 and (n['word118'],n['byte170'])!=(o['specific']['type_dword'],o['specific']['flag_170']):raise ValueError('A fields differ')
        if r['entry']==0x6d2664 and n['byte16c']!=o['specific']['flag_16c']:raise ValueError('B field differs')
        if r['entry']==0x6d26d4 and (n['word16c'],n['qword178'])!=(o['specific']['float_bits_16c'],0):raise ValueError('C fields differ')
        if r['entry']==0x6d2744 and n['word118']!=o['specific']['type_dword']:raise ValueError('D field differs')
        rows.append(r)
    if [r['instruction_count'] for r in rows]!=[181,200,196,171,181,171]:raise ValueError('bounded instruction counts changed')
    return rows


def precision_notes():
    notes=json.loads((RAW/'producer-118-precision.json').read_bytes());a=json.loads(gzip.decompress((ROOT/OWN118).read_bytes()))
    if sha_file(ROOT/OWN118)!=notes['target_artifact_sha256']:raise ValueError('frozen118 artifact changed')
    negative=[s for s in a['sprites'] if s['coverage']=='NO_REFERENCE_IN_QUERIED_NATIVE_AND_CAPTURED_SLICES_NOT_GLOBAL_UNUSED']
    d={x['id']:x for x in notes['corrections']}
    if len(negative)!=d['D3']['negative_rows'] or sum(bool(s['atlas_memberships_not_usage']) for s in negative)!=d['D3']['negative_rows_with_atlas_membership']:raise ValueError('additive D3 measured atlas/no-reference counts disagree')
    for prefix,n in d['D1']['measured_inherited_pin_groups'].items():
        if sum(p.startswith(prefix) for p in a['source_pins'])!=n:raise ValueError('additive D1 inherited pin group disagrees')
    if len(a['source_pins'])!=1587:raise ValueError('frozen118 pin census changed')
    return notes


def shared_source(peer):
    old=ROOT/'reverse-engineering/raw/geometry-8141386a/review-ef123/peer-datas-l3_ef6b75ef118_native_current_caller.json.gz'
    previous=json.loads(gzip.decompress(old.read_bytes()));a=peer['source']['calls'];b=previous['source']['runs'];dwords=0
    if len(a)!=10 or len(b)!=10 or peer['source']['post_factory_bindings']!=[0x118,0x128,0x130,0x1d0]:raise ValueError('shared-source explicit binding/call contract changed')
    for x,y in zip(a,b):
        if x['native']['output_bits']!=y['native']['output_bits'] or x['native']['completion_byte']!=1:raise ValueError('shared source118/124 bits/completion differ')
        dwords+=len(x['native']['output_bits'])
    if dwords!=930 or peer['source']['factory']!=0x6d26d4:raise ValueError('shared-source count/factory changed')
    return dict(calls=10,dwords=930,all_equal=True,post_factory_bound_offsets=peer['source']['post_factory_bindings'],evidence='Pinned118/124 artifact equality and explicit harness binding contract only; not fresh clip extraction, own parent119 re-execution, original graph-builder or runtime.')


def build():
    manifest=validate_pins();raw=read('peer-nodefactories124-probe.json.gz');peer=read('peer-nodefactories124-artifact.json.gz');fresh=read('fresh-original.json.gz');ci=read('source-ci-receipt.json.gz')
    if ci['run']['id']!=SOURCE_RUN or ci['run']['head_sha']!=SOURCE_HEAD or ci['run']['status']!='completed' or ci['run']['conclusion']!='success' or ci['fresh_original_sha256']!=sha_file(RAW/'fresh-original.json.gz'):raise ValueError('own fresh original exact-source GREEN receipt mismatch')
    if ci['peer_verify_run']['head_sha']!=PEER_SCI or ci['peer_verify_run']['status']!='completed' or ci['peer_verify_run']['conclusion']!='success':raise ValueError('peer scientific Verify receipt mismatch')
    for p,h in fresh['tool_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('fresh source collector/parser/snapshot pin drift')
    # Merge guards ensure shared123/124 bytes/RELA/imports do not conflict.
    memory,_,_=source_image()
    if memory.get(0x12da21)!=0:raise ValueError('allocator original empty-string byte differs')
    static=audit_static(raw,peer,fresh);runs=audit_replays(peer);notes=precision_notes();shared=shared_source(peer)
    pins={p['snapshot']:p['sha256'] for p in manifest['pins']}
    paths=['tools/verify/l3_geometry_8141386a_review_ef124.py','tools/verify/l3_geometry_8141386a_review_ef124_native.py','tools/verify/l3_geometry_8141386a_review_ef123_native.py','tools/verify/geometry_8141386a_review_ef123_checks.py',OWN118,'reverse-engineering/raw/geometry-8141386a/review-ef123/peer-pins.json','reverse-engineering/raw/geometry-8141386a/review-ef123/peer-datas-l3_ef6b75ef118_native_current_caller.json.gz']
    paths += [str((RAW/n).relative_to(ROOT)) for n in ('peer-pins.json','fresh-original.json.gz','source-ci-receipt.json.gz','producer-118-precision.json')]
    for p in paths:pins[p]=sha_file(ROOT/p)
    return dict(schema=1,item=120,provenance=BRANCH,review='Separate R1 ef124 addendum; own119 and closed118 scientific evidence unchanged',
                verdict='APPROVE_BOUNDED_EF124_STATIC_AND_SIX_PREPARED_STATE_FIXTURES_NOT_27_FULL',
                target=dict(scientific_commit=PEER_SCI,report_commit=PEER_REPORT,artifact_sha256=sha_file(RAW/'peer-nodefactories124-artifact.json.gz'),probe_sha256=sha_file(RAW/'peer-nodefactories124-probe.json.gz')),
                original_source=dict(run=SOURCE_RUN,head=SOURCE_HEAD,xapk_sha256=fresh['xapk_sha256'],library=fresh['library'],fresh_witness_sha256=sha_file(RAW/'fresh-original.json.gz')),
                static_audit=static,own_native_fixture_replays=runs,shared_source_check=shared,additive_producer118_precision=notes,
                counts=dict(factories=4,graph_bl_sites=7,vtable_groups=4,relative_vtable_slots=64,own_native_cases=6,own_instruction_counts=[r['instruction_count'] for r in runs],shared_source_calls_compared=10,shared_source_dwords_compared=930,new_numeric_contradictions=0),
                independence='Own fresh original ELF read using frozen own119 parser; own integer instruction arithmetic; separate own guarded Unicorn harness, no producer124 verifier/Fixture execution. Shared original build/retained bytes, own119 loader/parser, Unicorn2.1.4 and explicitly copied prepared-state contract. No independent native ABI/game-state discovery.',
                limits=['Only selected original static spans/FDEs/64vtable slots/7graph BLs freshly read. No global factory-use census, invented class names, serialized owner rediscovery or all-input coverage.',
                        'Factory allocator at3c986c is an asserted explicit sink, not native heap. TLS/service/pool/owner/node are prepared state; cleanup570ff0 is naturally skipped. Allocator/PLT/sentinel PCs excluded from six instruction counts.',
                        '10calls/930DWORDs compare pinned shared118/124 output only, not own parent-chain execution or independent source extraction. Post-factory118/128/130/1d0 bindings are harness writes.',
                        'No graph-builder execution, game bootstrap, live clip/clock/control writers, previous/active pose/apply/Unity readback, Android/runtime/render or #27-full acceptance. Newer ef126 behavior and other lanes are outside this fixed review.'],source_pins=pins)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();v=build();body=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=body:raise SystemExit('R1 addendum124 artifact drift')
    else:OUTPUT.write_bytes(body)
    print(v['verdict'],v['counts']);print('artifact',len(body),'SHA256',sha(body))
