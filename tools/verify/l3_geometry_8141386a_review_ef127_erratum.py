"""R1/124 additive verification of producer ERRATUM-127.
provenance: arena/8141386a-windwings-space-shooter-game-p
Verifies actual published correction against frozen own original bytes. Does not
rewrite/rebuild123 or127, execute producer tools, fix the generator, or add native
cases. Bounded approval is not review-queue selfACK or #27-full/runtime acceptance.
"""
from __future__ import annotations
import argparse
import gzip
import json
import struct
import subprocess
from tools.verify.geometry_8141386a_atlas_io import ROOT, BRANCH, canonical, sha, sha_file
from tools.verify.geometry_8141386a_review_ef127_checks import blob_id, decode_word
from tools.verify.geometry_8141386a_review_ef123_checks import add_imm

BASE=ROOT/'reverse-engineering/raw/geometry-8141386a'
RAW=BASE/'erratum-ef127'
OLD=BASE/'review-ef127'
OUTPUT=ROOT/'datas/l3_geometry_review_ef127_erratum_8141386a.json.gz'
OWN_SCIENCE='a7f4e1f65dee7fa1464f2706eaab94075fba4733'
PUBLICATION='5246e293c6375a3329244f1555e2d6d06d3c0303'
PRODUCER_COMMENT=6436088881
SPEC_COMMENT=6436273516
BODY_SHA='47f6f5aeef46de2becefba3d8266630fba2a6208322c0cd7d40568be744d59f3'
ACK_SHA='bc2f636b372db615ebae042dc6db6786a96b3e6d1381d753258cb01cfd097c99'
FROZEN_ARTIFACT='c34f6cbcc4d0e4ebf37190547674b308e068bac3c7fad5319591d09ccfeca337'
FRESH_SHA='74c1c83ff156605e5ee9b9f627122e5fe7a4853fdff6c99f81b55400b42bcda6'
PEER_ARTIFACT='8b9df00387893418d21608ddda6d7287c5c313ecd213770091b60720370f344e'
PEER_RAW='43adb19f62684262066e4ca71bec636b87e3e5bf0d2a06946de65e24c77fe2e1'
OWN_PATHS=('datas/l3_geometry_review_ef127_8141386a.json.gz',
 'reverse-engineering/raw/geometry-8141386a/review-ef127/fresh-original.json.gz',
 'reverse-engineering/raw/geometry-8141386a/verification-123.json.gz',
 'docs/apk-analysis/123-review-ef127-arena-8141386a-windwings-space-shooter-game-p.md')


def read(path):return json.loads(gzip.decompress(path.read_bytes()))


def validate_comments(producer=None,ack=None):
    producer=read(RAW/'producer-erratum.json.gz')if producer is None else producer
    ack=read(RAW/'spec-ack125.json.gz')if ack is None else ack
    repo='https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/pull/12#issuecomment-'
    for value,ident,digest in ((producer,PRODUCER_COMMENT,BODY_SHA),(ack,SPEC_COMMENT,ACK_SHA)):
        if value['id']!=ident or value['html_url']!=repo+str(ident)or sha(value['body'].encode())!=digest:
            raise ValueError('actual published comment identity/body changed')
    body=producer['body'].replace('**','').replace('`','')
    for phrase in ('ERRATUM (producer ef6b75ef)','graph_builder.callees["0xb98c98"].ret',
                   'b98d64','c0035fd6','b98d68','d6071494','5246e293c','không regenerate artifact 127'):
        if phrase.lower()not in body.lower():raise ValueError('producer correction scope/return assertion missing')
    return dict(producer=producer,spec_ack=ack,producer_body_sha256=BODY_SHA,spec_body_sha256=ACK_SHA,
                boundary='Pinned actual API publication; spec invitation is context, not this reviewer selfACK. Only the return label is superseded, not raw/case regeneration or source absence.')


def validate_publication(manifest=None):
    m=json.loads((RAW/'publication-pins.json').read_bytes())if manifest is None else manifest
    if (m['item'],m['provenance'],m['producer_publication_commit'])!=(124,BRANCH,PUBLICATION)or len(m['pins'])!=5:
        raise ValueError('fixed erratum publication pin coverage changed')
    for p in m['pins']:
        data=(ROOT/p['snapshot']).read_bytes()
        if p['commit']!=PUBLICATION or len(data)!=p['snapshot_size']or sha(data)!=p['snapshot_sha256']:
            raise ValueError('publication snapshot changed')
        source=data if p['encoding']=='gzip-as-source'else gzip.decompress(data)
        if sha(source)!=p['source_sha256']or blob_id(source)!=p['git_blob']:
            raise ValueError('publication source/Git identity changed')
    if sha_file(RAW/'peer-artifact127.json.gz')!=PEER_ARTIFACT or sha_file(RAW/'peer-probe127.json.gz')!=PEER_RAW:
        raise ValueError('original producer artifact/raw was regenerated')
    return m


def frozen_evidence():
    if sha_file(ROOT/OWN_PATHS[0])!=FROZEN_ARTIFACT or sha_file(OLD/'fresh-original.json.gz')!=FRESH_SHA:
        raise ValueError('original123 artifact/fresh capture changed')
    old=read(ROOT/OWN_PATHS[0]);fresh=read(OLD/'fresh-original.json.gz');receipt=read(BASE/'verification-123.json.gz')
    if old['item']!=123 or old['counts']['confirmed_published_return_pc_discrepancies']!=1 or 'CORRECTION_PENDING'not in old['verdict']:
        raise ValueError('historical123 DRIFT/conditional disposition was overwritten')
    for path,digest in old['source_pins'].items():
        if sha_file(ROOT/path)!=digest:raise ValueError('frozen123 source/input/code pin changed')
    if receipt['artifact']!=OWN_PATHS[0]or receipt['full_tests']['count']!=1655 or receipt['focused_tests']['count']!=284:
        raise ValueError('original123 verification provenance changed')
    if old['counts']['native_instructions']!=[51,51,51]or old['counts']['word_witnesses']!=33:
        raise ValueError('original null-domain scientific result changed')
    return old,fresh


def word_audit(fresh=None,peer=None):
    if fresh is None:_,fresh=frozen_evidence()
    peer=read(RAW/'peer-probe127.json.gz')if peer is None else peer
    windows=[w for w in fresh['peer_selected_spans']if w['va']==0xb98c98]
    pw=[w for w in peer['windows']if w['va']==0xb98c98]
    if len(windows)!=1 or len(pw)!=1:raise ValueError('unique original b98c98 window absent')
    w=windows[0];p=pw[0];b=bytes.fromhex(w['hex'])
    if (w['va'],w['file_offset'],w['size'],len(b))!=(0xb98c98,12143768,212,212)or w['hex']!=p['hex']or p['file_offset']!=w['file_offset']or sha(b)!=w['sha256']:
        raise ValueError('publication-window/own-original span equality differs')
    f=next(r for r in fresh['selected_fdes']if r['start']==0xb98c98)
    if f['end_exclusive']!=0xb98d6c or w['va']+len(b)!=f['end_exclusive']:
        raise ValueError('original FDE/window exclusive-end arithmetic differs')
    delta,size=struct.unpack_from('<iI',bytes.fromhex(f['fde_hex']),8)
    if f['fde_va']+8+delta!=f['start']or f['start']+size!=f['end_exclusive']:
        raise ValueError('original FDE encoding differs')
    memory={}
    for row in fresh['peer_selected_spans']:
        data=bytes.fromhex(row['hex'])
        if sha(data)!=row['sha256']:raise ValueError('own original span hash differs')
        for i,v in enumerate(data):
            a=row['va']+i
            if a in memory and memory[a]!=v:raise ValueError('original-byte overlap conflict')
            memory[a]=v
    def word(pc):return struct.unpack('<I',bytes(memory[pc+i]for i in range(4)))[0]
    expect={0xb98d4c:0x540000e1,0xb98d5c:0xf94013fe,0xb98d60:0x910143ff,
        0xb98d64:0xd65f03c0,0xb98d68:0x941407d6}
    others=(0x6cef60,0x6d0068,0x6f16b8,0xb98fc4,0xb99448,0x6cff3c)
    expect.update({pc:0xd65f03c0 for pc in others})
    if any(word(pc)!=v for pc,v in expect.items()):raise ValueError('erratum original instruction word differs')
    branch=decode_word(word(0xb98d4c),0xb98d4c);bl=decode_word(word(0xb98d68),0xb98d68)
    if (branch['kind'],branch['condition'],branch['target'])!=('B_COND','ne',0xb98d68)or(bl['kind'],bl['target'])!=('BL',0x109acc0):
        raise ValueError('canary failure/BL signed-target arithmetic differs')
    if add_imm(word(0xb98d60))!=(31,31,0x50):raise ValueError('SP-restoration instruction differs')
    ret_pcs=[w['va']+i for i in range(0,len(b),4)if struct.unpack_from('<I',b,i)[0]&0xfffffc1f==0xd65f0000]
    if ret_pcs!=[0xb98d64]:raise ValueError('bounded53-word RET scan differs')
    return dict(window=dict(va=w['va'],file_offset=w['file_offset'],size=len(b),sha256=sha(b),fde_end_exclusive=f['end_exclusive']),
        own_original_matches_producer_window=True,bounded_instruction_words_scanned=53,return_instructions=ret_pcs,
        corrected_return_pc=0xb98d64,old_label_pc=0xb98d68,old_label_actual_decode=bl,canary_failure_branch=branch,
        checked_words=[dict(pc=pc,word_hex=struct.pack('<I',v).hex())for pc,v in expect.items()],
        other_listed_callee_returns_verified=5,graph_builder_return_verified=1,
        boundary='Bounded frozen-byte verification of11 exact words and a53-word RET-opcode scan, not a general return-discovery algorithm, heuristic-generator repair, new native execution or heap/game-state evidence.')


def verify_git(fetch=False):
    m=validate_publication();refs=[dict(commit=PUBLICATION,path=p['path'],sha=p['source_sha256'],blob=p['git_blob'])for p in m['pins']]
    refs += [dict(commit=OWN_SCIENCE,path=p,sha=sha_file(ROOT/p),blob=None)for p in OWN_PATHS]
    for head in (PUBLICATION,OWN_SCIENCE):
        exists=subprocess.run(['git','-C',str(ROOT),'cat-file','-e',head+'^{commit}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
        if not exists:
            if not fetch:raise ValueError('missing fixed commit; explicit --fetch required')
            subprocess.run(['git','-C',str(ROOT),'fetch','--no-tags','--depth=1','--filter=blob:none','origin',head],check=True)
    for r in refs:
        b=subprocess.check_output(['git','-C',str(ROOT),'show',r['commit']+':'+r['path']])
        if sha(b)!=r['sha']or(r['blob']and blob_id(b)!=r['blob']):raise ValueError('actual publication/frozen science Git bytes differ')
    return len(refs)


def verify_api():
    values=[]
    for ident,digest in ((PRODUCER_COMMENT,BODY_SHA),(SPEC_COMMENT,ACK_SHA)):
        v=json.loads(subprocess.check_output(['gh','api',f'repos/Nthanhbadboy/WindWings-Space-Shooter-game-play/issues/comments/{ident}']))
        if v['id']!=ident or sha(v['body'].encode())!=digest:raise ValueError('current actual publication body differs from pinned snapshot')
        values.append(ident)
    return values


def build():
    m=validate_publication();comments=validate_comments();old,fresh=frozen_evidence();words=word_audit(fresh)
    artifact=read(RAW/'peer-artifact127.json.gz')
    if artifact['graph_builder']['callees']['0xb98c98']!={'fde_end':0xb98d6c,'ret':0xb98d68}or artifact['counts']['native_instructions']!=[51,51,51]:
        raise ValueError('original producer bad label or scientific cases were silently overwritten')
    generator=gzip.decompress((RAW/'peer-generator127.py.gz').read_bytes()).decode()
    if 'dict(ret=v-4,fde_end=v)'not in generator:raise ValueError('fixed historical root-cause generator changed')
    paths=[p['snapshot']for p in m['pins']]+[str((RAW/n).relative_to(ROOT))for n in ('producer-erratum.json.gz','spec-ack125.json.gz','publication-pins.json','coordination-status.json')]
    paths+=list(OWN_PATHS)+['reverse-engineering/raw/geometry-8141386a/scientific-ci-123.json.gz',
        'reverse-engineering/raw/geometry-8141386a/review-ef127/source-ci-receipt.json.gz',
        'tools/verify/l3_geometry_8141386a_review_ef127_erratum.py',
        'tools/verify/geometry_8141386a_review_ef127_checks.py','tools/verify/geometry_8141386a_review_ef123_checks.py']
    return dict(schema=1,item=124,provenance=BRANCH,existing_claim=6427652461,
        verdict='APPROVE_BOUNDED_EF127_NULL_ENTRY_RET_AFTER_VERIFIED_PRODUCER_ERRATUM_NOT_27_FULL',
        producer_erratum=dict(comment_id=PRODUCER_COMMENT,url=comments['producer']['html_url'],body_sha256=BODY_SHA,
            publication_commit=PUBLICATION,full_body=comments['producer']['body'],correction_kind='ADDITIVE_RETURN_LABEL_SUPERSESSION_ONLY'),
        spec_invitation=dict(comment_id=SPEC_COMMENT,url=comments['spec_ack']['html_url'],body_sha256=ACK_SHA,not_self_ack=True),
        original_review=dict(scientific_commit=OWN_SCIENCE,artifact_sha256=FROZEN_ARTIFACT,
            historical_verdict=old['verdict'],historical_confirmed_return_metadata_drift=1,
            preserved=True,original_null_domain_instruction_counts=[51,51,51],original_coverage=old['counts']),
        word_verification=words,effective_return_label=dict(function_entry=0xb98c98,return_pc=0xb98d64,fde_end_exclusive=0xb98d6c,
            replaced_historical_label=0xb98d68,old_label_instruction='BL_0x109acc0_NOT_RET',publication_overrides_label_not_bytes=True),
        counts=dict(published_comments_verified=2,producer_git_files=5,frozen_own_git_files=4,checked_original_words=11,
            bounded_window_words=53,covered_label_errata_verified=1,covered_label_blockers_remaining=0,new_native_cases=0,new_original_source_capture=0),
        preserved_qualifications=['Original123 remains conditional historical evidence with one DRIFT; original127 bytes/cases/artifact and generator stay pinned. Only this additive verification supplies a later bounded APPROVE.',
            'Original whole-FDE selected path means GB28/484 plus cleanup23/45, not full instruction coverage. Cleanup executes; five other listed callees do not. Deallocator remains a null synthetic service.',
            'Only+1c0/+1c8 are native zero stores; other output fields remain preparedA5/0. Eleven role rows retain6 witnessed and5 unasserted PCs. Counts are not additive across reports.',
            '128/129 M2a/M2b/M2c and M1a/M1b are previously published text-only context, not fresh native/serialized verification or a real instance/ABI supplied to this addendum.'],
        coordination= json.loads((RAW/'coordination-status.json').read_bytes()),
        limits=['No producer generator fix/rebuild, native tool import/execution, new51case replay as evidence, non-null graph/owner/motion object, original heap, runtime/Unity readback/render or #27-full acceptance.',
            'The publication resolves the specific return-label blocker. Heuristic repair is separately deferred by spec125; no all-program return-site completeness is claimed.',
            'Bounded evidence approval is distinct from formal PR12 handoff and spec review-queue ACK. Initial comment POST failed403; no claim/handoff publication success is invented.',
            'No frozen #4–8/118–123 report/artifact/source/receipt/log changes, peer edits, branch takeover, budget escalation or selfACK.'],
        source_pins={p:sha_file(ROOT/p)for p in sorted(set(paths))})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--git',action='store_true');p.add_argument('--fetch',action='store_true');p.add_argument('--api',action='store_true');a=p.parse_args()
    if a.fetch and not a.git:p.error('--fetch requires --git')
    v=build();b=gzip.compress(canonical(v)+b'\n',mtime=0)
    if a.check:
        if OUTPUT.read_bytes()!=b:raise SystemExit('additive erratum artifact drift')
    else:OUTPUT.write_bytes(b)
    if a.git:print('PASS actual producer publication/frozen own Git identities:',verify_git(a.fetch))
    if a.api:print('PASS actual API publication bodies:',verify_api())
    print(v['verdict'],v['counts']);print('artifact',len(b),'SHA256',sha(b))


if __name__=='__main__':main()
