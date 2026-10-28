"""R1 independent review119 of pinned ef123, not #27-full acceptance.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations
import argparse
import gzip
import json
import struct
from pathlib import Path
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file
from tools.verify.geometry_8141386a_review_ef123_checks import candidate_sets,constant_stores,branch,decode_rela,decode_usage,stream_relocations,table_literal
from tools.verify.l3_geometry_8141386a_review_ef123_native import RAW,replay,source_image

OUTPUT=ROOT/'datas/l3_geometry_review_ef123_8141386a.json.gz'
PEER_SCI='1d6fbcbb7e5f8ae35135ee098b5a4816ea9d4f84'
PEER_REPORT='8ac0c7ab6'
CORRECTION='ea6a3835f786306b07df9658262a6e3f6658f809'


def read(name):return json.loads(gzip.decompress((RAW/name).read_bytes()))


def validate_pins():
    v=json.loads((RAW/'peer-pins.json').read_bytes())
    if v['scientific_commit']!=PEER_SCI or v['producer_correction_commit']!=CORRECTION:raise ValueError('review target/correction changed')
    for p in v['pins']:
        if sha_file(ROOT/p['snapshot'])!=p['sha256']:raise ValueError('selected peer snapshot SHA mismatch:'+p['snapshot'])
        if p.get('encoding')=='gzip' and sha(gzip.decompress((ROOT/p['snapshot']).read_bytes()))!=p['original_sha256']:raise ValueError('selected decompressed peer source SHA mismatch')
    return v


def build():
    manifest=validate_pins();raw=read('peer-vtable123-probe.json.gz');peer=read('peer-vtable123-artifact.json.gz');fresh=read('fresh-original.json.gz');ci=read('source-ci-receipt.json.gz')
    if ci['run']['head_sha']!='c11405d772310dcbeda564e752041d76c27775dc' or ci['run']['status']!='completed' or ci['run']['conclusion']!='success' or ci['fresh_original_sha256']!=sha_file(RAW/'fresh-original.json.gz'):raise ValueError('fresh original review receipt not exact original-source GREEN')
    if ci['peer_verify_run']['head_sha']!=PEER_SCI or ci['peer_verify_run']['conclusion']!='success':raise ValueError('peer scientific Verify receipt mismatch')
    for p,h in fresh['tool_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('fresh original query/parser pin mismatch')
    retained=candidate_sets(raw['relocations']);original=candidate_sets(fresh['unity']['vtable_window_relas'])
    if retained!=original or len(original['naive'])!=53 or original['exact_reserve_notify']!=[0x10b1150,0x10b1240,0x10b1330] or original['intersection']:raise ValueError('independent candidate-universe facts changed')
    if {x['vptr'] for x in raw['vtable_candidates']}!=set(original['naive']) or {x['vptr'] for x in raw['matched_vtables']}!=set(original['exact_reserve_notify']):raise ValueError('retained list does not match independently computed predicate')
    byte_image,_,_=source_image()
    w=next(w for w in raw['windows'] if w['va']==0x6d2894);ctor=constant_stores(bytes.fromhex(w['hex']),w['va']);selected=[r for r in ctor if r['value']==0x10b1150 and r['offset']==0]
    if len(selected)!=1 or selected[0]['pc']!=0x6d28e0:raise ValueError('original constructor no longer selects stated vptr')
    builder=next(w for w in raw['windows'] if w['va']==0x6cf7b4);code=bytes.fromhex(builder['hex']);calls=[]
    for off in range(0,len(code)-3,4):
        b=branch(struct.unpack_from('<I',code,off)[0],builder['va']+off)
        if b and b['target']==0x6d2950:calls.append(b)
    if [c['pc'] for c in calls]!=[0x6cfc34,0x6cfc44] or not all(c['link'] for c in calls):raise ValueError('original graph caller BL identities changed')
    global_refs=fresh['unity']['global_graph_direct_branches']
    if [r['pc'] for r in global_refs]!=[c['pc'] for c in calls] or fresh['unity']['global_graph_relative_relas']:raise ValueError('fresh global branch/RELA negative audit mismatch')
    fdes=[]
    for v in fresh['unity']['selected_fdes']:
        old=next(r['unwind'] for r in raw['followed'] if r['entry']==v['start'])
        if old['end']!=v['end_exclusive'] or old['fde_hex']!=v['fde_hex'] or old['table_hex']!=v['table_hex']:raise ValueError('fresh/retained original FDE mismatch')
        if v['start'] in (0x6d2894,0x6d26d4,0x6d2950,0x6cf7b4,0x571a80,0x6d5134):fdes.append(v)
    replays=[]
    for old in peer['standalone']:
        r=replay(old['count'],old['prefill'])
        if r['instruction_count']!=old['run']['instruction_count'] or r['unique_executed_addresses']!=old['run']['executed_addresses']:raise ValueError('independent fixture native-PC sequence/set count differs')
        if any(r['pc_counts'].get(pc,0)!=n for pc,n in old['pc_hits'].items()):raise ValueError('independent exact PC multiplicity mismatch')
        expected=[dict(pc=x['pc'],address=x['address'],size=x['size']) for x in r['byte_writes']]
        if expected!=old['zero_writes']:raise ValueError('independent native write PC/address/size mismatch')
        if r['manager']['byte100']!=old['manager_after']['byte_100'] or r['manager']['length']!=old['manager_chunk_after']['length'] or r['owner']['count']!=old['list_owner_after']['count']:raise ValueError('independent declared-state effects differ')
        replays.append(r)
    # This equality only checks already pinned shared source outputs; parent119 is
    # deliberately not re-executed or presented as fresh/independent clip extraction.
    previous=read('peer-datas-l3_ef6b75ef118_native_current_caller.json.gz');output_dwords=0
    for a,b in zip(peer['source']['calls'],previous['source']['runs']):
        if a['native']['output_bits']!=b['native']['output_bits'] or a['native']['completion_byte']!=1:raise ValueError('shared source output bit equality mismatch')
        output_dwords+=len(a['native']['output_bits'])
    if len(peer['source']['calls'])!=10 or len(previous['source']['runs'])!=10 or output_dwords!=930:raise ValueError('source shared-count scope changed')
    relocation_pin=next(r for r in manifest['pins'] if r['path'].endswith('ui-audit/native-relocations.json.gz'));legacy=stream_relocations(ROOT/relocation_pin['snapshot'],0x2adfb48)
    if legacy['entries']!=288733 or legacy['matches']!=[dict(address=0x2adfb48,addend=0x2be5cb8)]:raise ValueError('legacy static relocation census mismatch')
    replicas=[];literal=None
    for term in ('drone-loadout','player-hp-board','wing-drone'):
        pin=next(r for r in manifest['pins'] if term in r['path']);v=json.loads((ROOT/pin['snapshot']).read_bytes());matches=[x for x in v['relocations'] if int(x['got'],0)==0x2adfb48]
        if len(matches)!=1:raise ValueError('legacy selected RELA missing/ambiguous')
        rela=decode_rela(matches[0]['rela_hex'])
        if rela['hex']!=fresh['marker']['rela']['hex']:raise ValueError('fresh/retained marker raw RELA differs')
        replicas.append(dict(path=pin['path'],sha256=pin['sha256'],rela=rela,lineage='Distinct receipts share original build/extractor lineage; not three clean-room parsers'))
        if term=='drone-loadout':literal=next(r for r in v['literals'] if r['index']==7763)
    usage=decode_usage(literal['pointee']['hex']);m=fresh['marker']
    if (usage['kind'],usage['index'],usage['encoded'])!=(m['kind'],m['index'],m['encoded_usage']) or literal['definition_hex']!=m['definition_hex'] or literal['hex']!=m['payload_hex'] or literal['data_file_offset']!=m['payload_file_offset']:raise ValueError('fresh exact token/metadata literal chain disagrees')
    pin=next(r for r in manifest['pins'] if r['path'].endswith('il2cpp/stringliteral.json'));strings=table_literal(ROOT/pin['snapshot'],0x2be5cb8)
    if strings['matches']!=[dict(address='0x2BE5CB8',value='Stop')]:raise ValueError('independent string-index match mismatch')
    corrected=gzip.decompress((RAW/'peer-report123-corrected.md.gz').read_bytes()).decode()
    if 'complementary' not in corrected.lower() or '0xa0003ca7' not in corrected.lower():raise ValueError('producer correction is not evidenced in pinned corrected report')
    sources={p['snapshot']:p['sha256'] for p in manifest['pins']}
    for p in ['tools/verify/l3_geometry_8141386a_review_ef123.py','tools/verify/l3_geometry_8141386a_review_ef123_native.py','tools/verify/geometry_8141386a_review_ef123_checks.py',str((RAW/'peer-pins.json').relative_to(ROOT)),str((RAW/'fresh-original.json.gz').relative_to(ROOT)),str((RAW/'source-ci-receipt.json.gz').relative_to(ROOT)),str((RAW/'producer-correction-comment.json.gz').relative_to(ROOT))]:sources[p]=sha_file(ROOT/p)
    findings=[dict(id='R1-01',severity='MEDIUM_DESCRIPTION',status='CORRECTED_BY_PRODUCER',original_claim='53-to-3 subset narrowing',actual='Complementary predicates with empty intersection; selected vptr not in naive53',correction_commit=CORRECTION),
              dict(id='R1-02',severity='LOW_ENCODING_DESCRIPTION',status='CORRECTED_BY_PRODUCER',original_claim='addend cell bytes are UTF8 Stop',actual='ELF RELA→encoded metadata usage kind5/index7763→metadata payload Stop, not char* at addend',correction_commit=CORRECTION),
              dict(id='R1-N1',severity='BOUNDARY_NOTE',status='DOCUMENTED_IN_REVIEW',actual='Zero-loop manager+0x100 remains prefill0xA5; count>0 gets write1 then zero. Artifact/code correct, no universal zero-state claim.'),
              dict(id='R1-N2',severity='BOUNDARY_NOTE',status='DOCUMENTED_IN_REVIEW',actual='Fresh FDE end is exclusive; several report ranges name final RET inclusive. Use explicit end/RET PCs, do not infer off-by-four byte coverage.')]
    return dict(schema=1,item=119,provenance=BRANCH,review='R1 independent static/fixture review of pinned ef123',
                verdict='APPROVE_BOUNDED_EF123_WITH_PRODUCER_DESCRIPTION_CORRECTIONS_VERIFIED_NOT_27_FULL',
                target=dict(scientific_commit=PEER_SCI,original_report_commit=manifest['report_commit'],producer_correction_commit=CORRECTION,peer_artifact_sha256=sha_file(RAW/'peer-vtable123-artifact.json.gz'),peer_probe_sha256=sha_file(RAW/'peer-vtable123-probe.json.gz')),
                findings=findings,candidate_audit=original,constructor_store=selected[0],graph_direct_calls=calls,
                fresh_original_scope=dict(source_run=ci['run']['id'],rela_total=fresh['unity']['rela_total'],relative_rela_total=fresh['unity']['relative_rela_total'],global_graph_relative_matches=0,global_graph_direct_matches=len(global_refs),matched_unique_peer_windows=len(fresh['unity']['peer_window_matches']),matched_original_fdes=len(fresh['unity']['selected_fdes']),selected_fdes=fdes),
                own_native_fixture_replays=replays,shared_source_check=dict(calls=10,dwords=930,all_equal=True,evidence='Pinned peer/source118 bit equality only; not fresh source parse/parent-chain execution/runtime'),
                marker_audit=dict(fresh=m,legacy_relocation_scan=legacy,selected_rela_receipts=replicas,index_confirmation=strings,decoded_usage=usage,
                                  conclusion='Static literal identity Stop confirmed. Not direct UTF8 at addend, native method pointer, registration, event invocation or game-state readback.'),
                counts=dict(own_native_cases=len(replays),own_instruction_counts=[r['instruction_count'] for r in replays],own_standalone_factory_calls=sum(r['count'] for r in replays),producer_source_calls_compared=10,producer_source_dwords_compared=930,description_findings_corrected=2),
                independence='Own ELF/metadata parser+fresh original CI; own integer instruction checks; own Unicorn harness with guarded retained byte reads and explicit shared fixture contract. Same source bytes/build/emulator and shared source118 lineage; no clean-room ABI or independent game state.',
                limits=['No graph-builder execution, original heap/allocator, actual manager construction/serialized controller bootstrap, active pose/apply or Unity/Android/runtime/render. #27-full acceptance remains pending owner/peer review workflow.',
                        'Review of original123 plus verified documentation correction only; no review of124/newer native behavior and no peer branch/tool/artifact edits.',
                        'Own fixture replay validates the declared counts0/1/3/3 and explicit allocator/memset/canary services, not all inputs or lifecycle/callback delivery.'],source_pins=sources)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();v=build();body=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=body:raise SystemExit('R1 review artifact drift')
    else:OUTPUT.write_bytes(body)
    print(v['verdict'],v['counts']);print('artifact',len(body),'SHA256',sha(body))
