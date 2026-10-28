"""Exact producer bindings + reached gold/FX methods + serialized co-attachments."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
RAW=ROOT/'reverse-engineering/raw';BASE=RAW/'enemy-hit-callbacks'
OUT=ROOT/'datas/enemy_hit_callback_flow.json'
SELECT={'Enemy_Controller':{'CacheComponents'},'Enemy_HitSkeletonRenderer':{'Start','OnHit','CancelEffect','ctor'},
 'Enemy_DropGold':{'Start','DropGold','ctor'},'Test_Enemy':{'Start','<Start>b__8_0'},
 'Items_Manager':{'Start','OnBurstGolds','BurstOut'},'MyPhysics2D':{'GetEllipseRandomizeVector'},'BurstGold':{'ctor'}}
ANCHORS={
 'Enemy_HitSkeletonRenderer':{0x13218a0:('bl','#0x16f4f54'),0x13218d8:('bl','#0x16f4f54'),
   0x132190c:('bl','#0x20bc330'),0x1321914:('str','x21, [x20, #0x20]'),0x1321928:('b','#0x1321930'),
   0x13219f4:('bl','#0x27693cc'),0x1321aec:('bl','#0x27693cc'),
   0x1321b0c:('bl','#0x2782540'),0x1321b20:('bl','#0x27824b8'),
   0x1321b2c:('ldr','s0, [x8, #0xfe0]'),0x1321b44:('b','#0x27822d4')},
 'Enemy_DropGold':{0x1581790:('ldr','x21, [x0, #0x28]'),0x15817b4:('bl','#0x18a5dfc'),
   0x15817c4:('bl','#0x2146010'),0x15817e0:('str','x0, [x20, #0x28]'),
   0x15818f0:('blr','x8'),0x1581960:('blr','x8'),0x1581968:('fdiv','s0, s8, s0'),
   0x1581978:('fmul','s0, s0, s1'),0x1581984:('fcvtzs','w11, s0'),
   0x15819a4:('b.le','#0x1581a0c'),0x15819ac:('str','w8, [x19, #0x28]'),
   0x15819dc:('str','w8, [x20, #0x10]'),0x1581a08:('b','#0x1434cb4'),
   0x1581a10:('b.ge','#0x1581a1c'),0x1581a18:('str','w8, [x19, #0x28]'),
   0x1581a38:('ldr','d0, [x8, #0x6b8]'),0x1581a48:('str','d0, [x0, #0x20]')},
 'Test_Enemy':{0x1322e34:('bl','#0x2146010'),0x1322e4c:('str','x0, [x22, #0x20]'),
   0x13231d8:('cbnz','w8, #0x13231f4'),0x13231e4:('strb','w8, [x0, #0x50]'),0x13231ec:('bl','#0x2786dc0')},
 'Items_Manager':{0x14c8e44:('ldr','x23, [x23, #0x630]'),0x14c8ebc:('bl','#0x18a5580'),
   0x14c8ec0:('mov','w1, #6'),0x14c8ed0:('bl','#0x1434c84'),
   0x14c8fb0:('bic','w22, w9, w9, asr #31'),0x14c8fc0:('cmp','w9, #1'),
   0x14c8fd4:('cmp','w9, #4'),0x14c8fec:('ldr','s8, [x10, w9, uxtw #2]'),
   0x14c9014:('csel','w24, w8, w9, ne'),0x14c906c:('bl','#0x14c9104'),0x14c90d0:('bl','#0x14c9104'),
   0x14c9194:('fcsel','s11, s1, s0, gt'),0x14c91bc:('bl','#0x14224ec'),
   0x14c91f4:('bl','#0x123aaa0'),0x14c9284:('blr','x8'),0x14c92a4:('b','#0x2781804')},
 'MyPhysics2D':{0x1422520:('bl','#0x277d280'),0x1422548:('fsqrt','s1, s2'),
   0x1422564:('bl','#0x277d280'),0x1422570:('mov','w0, wzr'),0x1422578:('bl','#0x277d2c0'),
   0x1422580:('cmp','w0, #2'),0x1422584:('fcsel','s1, s0, s12, lt')},
}


def build():
    used={ROOT/'reverse-engineering/il2cpp/dump.cs.gz',ROOT/'tools/verify/enemy_hit_callback_models.py',BASE/'references.json',BASE/'bindings.json',BASE/'native/index.json'}
    dump=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode()
    starts=sorted(set(int(s,16) for s in re.findall(r'// RVA: 0x([0-9A-Fa-f]+)',dump)))
    assert 'public const EventID BusrtGolds = 6;' in dump
    assert re.search(r'// RVA: 0x2146010[^\n]*\n\s*public static Delegate Combine\(Delegate a, Delegate b\)',dump)
    ff={cls:fields(class_text(dump,cls)) for cls in ['Enemy_Health','Enemy_DropGold','BurstGold','Enemy_HitSkeletonRenderer','GameLayer']}
    for cls,offset,name in [('Enemy_Health',32,'hitCallback'),('Enemy_Health',40,'hitDamageCallback'),
      ('Enemy_DropGold',32,'burstCoins'),('Enemy_DropGold',36,'totalP'),('Enemy_DropGold',40,'iPlus'),
      ('BurstGold',16,'burstCoins'),('BurstGold',24,'parent'),('GameLayer',24,'layerItem')]:assert ff[cls][offset]['name']==name
    manifest=json.loads((BASE/'native/index.json').read_text())
    for row in manifest['files']:
        p=ROOT/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    methods=[];anchors=[];bodies={}
    for cls,names in SELECT.items():
        path=BASE/'native'/f'{cls}.asm.txt';meta=BASE/'native'/f'{cls}.json';used|={path,meta}
        code=instructions(path);bodies[cls]=code
        for a,v in ANCHORS.get(cls,{}).items():
            assert code[a]==v,(cls,hex(a),code[a],v)
            anchors.append(dict(cls=cls,at=hex(a),op=v[0],args=v[1]))
        found=set()
        for m in json.loads(meta.read_text())['methods']:
            if m['method'] not in names:continue
            start=int(m['rva'],16);end=min(start+m['bytes'],starts[bisect.bisect_right(starts,start)])
            assert not m['size_capped'] and all(a in code for a in range(start,end,4))
            methods.append(dict(cls=cls,method=m['method'],rva=hex(start),instructions=(end-start)//4,
              calls=[dict(at=hex(a),op=code[a][0],args=code[a][1]) for a in range(start,end,4) if code[a][0] in ('bl','blr','br') or code[a][0]=='b' and int(code[a][1][1:],16) not in range(start,end,4)]))
            found.add(m['method'])
        assert found==names,(cls,found,names)
    refs=json.loads((BASE/'references.json').read_text());assert len(refs['references'])==8
    assert set(refs['direct_reference_roots'])=={'Test_Enemy','Enemy_DropGold','Enemy_HitSkeletonRenderer','Enemy_Controller'}
    for row in refs['references']:
        data=bytes.fromhex(row['window_hex']);adrp=int(row['adrp'],16);load=int(row['load'],16)
        w=struct.unpack_from('<I',data)[0];imm=((w>>5&0x7ffff)<<2)|(w>>29&3)
        if imm&(1<<20):imm-=1<<21
        assert w&0x9f000000==0x90000000
        ld=struct.unpack_from('<I',data,len(data)-4)[0]
        assert ld&0xffc00000==0xf9400000 and (ld>>5&31)==(w&31)
        assert (adrp&~4095)+(imm<<12)+((ld>>10&4095)<<3)==int(row['got'],16)
        assert load-adrp+4==len(data)<=512
    p=RAW/'combat-chain/symbols.json.gz';used.add(p);ss=json.loads(gzip.decompress(p.read_bytes()))['records']
    sym={r['Address']:r for k in ('ScriptMetadata','ScriptMetadataMethod') for r in ss[k]}
    raw=json.loads((BASE/'bindings.json').read_text());rel={r['got']:r for r in raw['relocations']}
    bindings=[]
    for got,suffix,rva in [('0x2ae1720','Enemy_HitSkeletonRenderer.OnHit()',0x1321a1c),
      ('0x2aec478','Enemy_DropGold.DropGold()',0x1581828),('0x2ae1780','Test_Enemy.<Start>b__8_0()',0x13231d0),
      ('0x2ae8630','Items_Manager.OnBurstGolds()',0x14c8f14)]:
        row=rel[got];va,info,target=struct.unpack('<QQq',bytes.fromhex(row['rela_hex']))
        assert hex(va)==got and info==1027 and hex(target)==row['effective']
        symbol=sym[target];assert symbol['Name'].endswith(suffix) and symbol['MethodAddress']==rva
        bindings.append(dict(got=got,effective=hex(target),name=symbol['Name'],method_rva=hex(rva)))
    type_bindings=[]
    for got,suffix in [('0x2adcac8','GetComponent<IHealth>()'),('0x2ae1788','IHealth_TypeInfo'),
      ('0x2ae8648','BurstGold_TypeInfo'),('0x2ae8650','GetComponent<IItem>()'),
      ('0x2ae8658','IItem_TypeInfo'),('0x2adcdb0','GameLayer_TypeInfo')]:
        row=rel[got];va,info,target=struct.unpack('<QQq',bytes.fromhex(row['rela_hex']))
        assert hex(va)==got and info==1027 and hex(target)==row['effective']
        symbol=sym[target];assert symbol['Name'].endswith(suffix)
        type_bindings.append(dict(got=got,effective=hex(target),name=symbol['Name']))
    row=refs['metadata_bindings'][0];va,info,target=struct.unpack('<QQq',bytes.fromhex(row['rela_hex']))
    assert va==0x2ae1718 and info==1027 and sym[target]['Name'].endswith('GetComponent<Enemy_Health>()')
    assert 'Slot: 0\n\tpublic abstract float GetStartHealth();' in dump
    assert 'Slot: 1\n\tpublic abstract float GetCurrentHealth();' in dump
    literals=[]
    magic,version,ls,lc,ds,dc=struct.unpack('<6I',bytes.fromhex(raw['metadata_header_hex']))
    assert magic==0xfab11baf and version==31
    for got,text in [('0x2ae1730','CancelEffect'),('0x2adceb8','_Black')]:
        r=rel[got];literal=r['literal'];encoded=struct.unpack('<Q',bytes.fromhex(r['pointee_cell']['hex']))[0]
        index=(encoded&0x1ffffffe)>>1;length,offset=struct.unpack('<II',bytes.fromhex(literal['definition_hex']))
        assert encoded>>29==5 and index==literal['index'] and index<lc//8
        assert literal['definition_file_offset']==ls+8*index and literal['data_file_offset']==ds+offset and offset+length<=dc
        assert len(bytes.fromhex(literal['hex']))==length and bytes.fromhex(literal['hex']).decode()==text==literal['utf8']
        literals.append(dict(got=got,**literal))
    cells={r['va']:r for r in raw['cells']}
    assert struct.unpack('<ii',bytes.fromhex(cells['0x7576b8']['hex']))==(28,10)
    assert struct.unpack('<f',bytes.fromhex(cells['0x756fe0']['hex']))[0]==struct.unpack('<f',struct.pack('<f',.01))[0]
    assert cells['0x758130']['hex']=='9a9919406766e63f'
    assert cells['0x756a68']['hex']=='9a99193e'
    health=[]
    for path in sorted((RAW/'combat-chain').glob('components-*.json.gz')):
        used.add(path);health += [dict(r,source_path=str(path.relative_to(ROOT))) for r in json.loads(gzip.decompress(path.read_bytes())) if r['class_name']=='Enemy_Health']
    attachments=[]
    for cls in ('Enemy_DropGold','Enemy_HitSkeletonRenderer'):
        path=RAW/'typetrees'/f'{cls}.jsonl.gz';used.add(path)
        for line in gzip.open(path,'rt'):
            r=json.loads(line);go=r['tree']['m_GameObject'];assert go['m_FileID']==0
            matches=[h for h in health if h['gameobject']['path_id']==go['m_PathID'] and any(p['component']==dict(m_FileID=0,m_PathID=r['path_id']) for p in h['gameobject']['tree']['m_Component'])]
            assert len(matches)==1,(cls,r['path_id'],len(matches));h=matches[0]
            assert h['tree']['m_GameObject']==go
            attachments.append(dict(cls=cls,component=r['path_id'],enabled=r['tree']['m_Enabled'],serialized_file=h['serialized_file'],gameobject_id=go['m_PathID'],gameobject=r['gameobject'],health_component=h['path_id'],health_noDamage=h['tree']['noDamage'],source_path=h['source_path'],serialized_values={k:v for k,v in r['tree'].items() if not k.startswith('m_')}))
    assert len(attachments)==19
    return dict(status='PROVISIONAL_APK_CALLBACK_PRODUCERS_AND_BURST_CHAIN_NOT_RUNTIME',bindings=bindings,literals=literals,cells=list(cells.values()),
      methods=methods,anchors=anchors,type_bindings=type_bindings,direct_metadata_reference_owners=refs['direct_reference_roots'],attachments=attachments,
      attachment_rule='Legacy class record resolved uniquely by GO+component membership into file-qualified health snapshot; corrupted generated m_Script ignored; co-attachment != spawn/Start execution proof.',
      source_artifacts=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(used)])


if __name__=='__main__':
    import sys
    r=build()
    if '--check' in sys.argv:assert r==json.loads(OUT.read_text())
    else:OUT.write_text(json.dumps(r,indent=2)+'\n')
    print(len(r['methods']),'method ranges;',len(r['anchors']),'anchors;',len(r['attachments']),'serialized joins PASS')
