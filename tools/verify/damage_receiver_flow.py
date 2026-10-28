"""APK-bound receiver source anchors and CFG arguments; provisional, not runtime."""
import bisect
import gzip
import hashlib
import json
import re
import struct
from tools.verify.combat_argument_audit import ROOT,RAW,instructions,must_w0
from tools.verify.combat_rate_consumers import class_text,fields

OUT=ROOT/'datas/damage_receiver_flow.json'
EXTRA=ROOT/'reverse-engineering/raw/combat-receivers'
SELECT={
 'Enemy_Health':{'CalculateDamage'},
 'Enemy_Controller':{'TakeDamage','OnTakeDamage','UpdateHpBar','OnDieWhenZeroHp','SetDieCallback'},
 'Enemy_Sub':{'TakeDamage','SetDieCallback'},
 'Enemy_Destroy':{'Destroy','OnDestroyByZeroHp','Pool','Destroyed'},
 'Enemy_Display':{'OnHit','SetHpBar'},
 'Player_Health':{'TakeDamage','GainHealth','Miss'},
 'Sub_Player':{'TakeDamage','SetDieCallback','Destroyed'},
 'Player_Attack':{'IsInvisible','SetInvisible'},
 'Player_Get_Datas':{'TimeToImmuneOneHit','get_abi32Amount'},
 'Enemy_DestroyDelayed':{'Destroy','DelayDestroy','<DelayDestroy>b__4_0','ctor','<>n__0'},
 'Enemy_DestroyDelayed.<DelayDestroy>d__4':{'MoveNext'},
 'MB_Destroy':{'Destroy','OnDestroyByZeroHp','DieEffect'},
 'MB_Destroy.<DieEffect>d__5':{'MoveNext'},
 'EventDispatcherExtension':{'PostEvent'},
 'EventDispatcher':{'PostEvent'},
 'Player_Controller':{'Start','OnDie','OnExtralife','DoExtraLife','DoExtraLifePVP'},
 'Player_Controller.<DoExtraLife>d__62':{'MoveNext'},
}
ANCHORS={
 'Enemy_Health':{0x1584808:('str','s0, [x19]'),0x1584820:('blr','x9'),0x1584824:('ldr','x8, [x20, #0x28]'),0x158482c:('ldr','s0, [x19]'),0x1584830:('fsub','s0, s8, s0'),0x1584838:('b.le','#0x1584858'),0x1584854:('br','x2')},
 'Enemy_Controller':{0x1582954:('bl','#0x1582974'),0x1582bb4:('bl','#0x158479c'),0x1582bec:('bl','#0x1582f10'),0x1582bf8:('ldr','s0, [x8, #0x28]'),0x1582c00:('b.ls','#0x1582dd4'),0x1582cd4:('bl','#0x1584444'),0x1582d88:('ldr','x20, [x20, #0x18]'),0x1582dd8:('bl','#0x15846f8'),0x1582de0:('ldr','x20, [x20, #0x18]'),0x1584718:('strb','w9, [x8, #0x2d]'),0x1584738:('mov','w1, wzr')},
 'Enemy_Destroy':{0x15815d0:('b','#0x1584bf0'),0x1585724:('blr','x9'),0x1585728:('ldr','x8, [x19, #0x20]'),0x158572c:('cbz','x8, #0x15857e0'),0x1585754:('bl','#0x15850bc'),0x1584c34:('str','xzr, [x19, #0x28]'),0x1584c4c:('bl','#0x1434cb4'),0x1585494:('blr','x8')},
 'Player_Health':{0x14c7050:('b.pl','#0x14c708c'),0x14c7084:('str','s0, [x19, #0x2c]'),0x14c7198:('b.le','#0x14c71bc'),0x14c71c8:('strb','wzr, [x19, #0x31]'),0x14c7418:('fcvtzs','w24, s8'),0x14c74a4:('fcsel','s1, s3, s1, eq'),0x14c74ac:('fcvtzs','w21, s9'),0x14c74dc:('fcsel','s0, s2, s0, eq'),0x14c74e8:('str','s0, [x8, #4]'),0x14c7514:('bl','#0x1434cb4'),0x14c7524:('bl','#0x1434ce4'),0x14c7530:('ldr','s0, [x8, #4]'),0x14c7690:('ldr','x8, [x19, #0x40]'),0x14c76ac:('strb','wzr, [x19, #0x48]'),0x14c76c0:('blr','x8'),0x14c774c:('bl','#0x1434cb4')},
 'Sub_Player':{0x14c838c:('ret',''),0x14c83f4:('ldr','x2, [x24]'),0x14c842c:('b','#0x14c6de4'),0x14c8434:('ret','')},
 'Enemy_DestroyDelayed.<DelayDestroy>d__4':{0x1581650:('blr','x9'),0x158169c:('bl','#0x2786670'),0x15816c4:('bl','#0x1581598')},
 'MB_Destroy.<DieEffect>d__5':{0x1574b88:('br','x10'),0x1574bcc:('bl','#0x2786508'),0x1574c18:('bl','#0x2786508'),0x1574c5c:('bl','#0x2786508'),0x1574c88:('bl','#0x15850bc')},
 'EventDispatcherExtension':{0x1434cdc:('b','#0x1434720'),0x1434d00:('b','#0x1434720')},
 'EventDispatcher':{0x14347cc:('bl','#0x1945914'),0x14347f4:('br','x3')},
 'Player_Controller':{0x14c20b4:('str','x20, [x23, #0x40]'),0x14c2830:('strb','wzr, [x8, #0x90]'),0x14c286c:('bl','#0x2782b0c'),0x14c4430:('bl','#0x14c63b4')},
}


def build():
    dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'
    dump=gzip.decompress(dump_path.read_bytes()).decode()
    starts=sorted(set(int(s,16) for s in re.findall(r'// RVA: 0x([0-9A-Fa-f]+)',dump)))
    used={dump_path,ROOT/'tools/verify/damage_receiver_models.py',ROOT/'tools/verify/enemy_damage_model.py'}
    manifest=json.loads((EXTRA/'index.json').read_text())
    for row in manifest['files']:
        p=ROOT/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    used.add(EXTRA/'index.json');used.add(EXTRA/'jump-table.json')
    result=[];found=set()
    for cls,names in SELECT.items():
        stem=re.sub(r'[^\w.]','_',cls)
        folder=EXTRA if (EXTRA/(stem+'.json')).exists() else RAW/'native'
        path=folder/(stem+'.asm.txt');meta_path=folder/(stem+'.json')
        used|={path,meta_path};body=instructions(path)
        for a,value in ANCHORS.get(cls,{}).items():assert body[a]==value,(cls,hex(a))
        meta=json.loads(meta_path.read_text())
        for m in meta['methods']:
            if m['method'] not in names:continue
            start=int(m['rva'],16);next_index=bisect.bisect_right(starts,start)
            end=min(start+m['bytes'],starts[next_index] if next_index<len(starts) else start+m['bytes'])
            code={a:v for a,v in body.items() if start<=a<end}
            assert not m['size_capped'] and set(code)==set(range(start,end,4))
            incoming=must_w0(code,start)
            args=[{'at':hex(a),'ability_id':incoming[a]} for a,v in sorted(code.items()) if v==('bl','#0x14c7758')]
            assert all(r['ability_id'] is not None for r in args)
            result.append({'class':cls,'method':m['method'],'signature':m['signature'],'rva':m['rva'],
                'instruction_count':len(code),'ability_calls':args,
                'branches':[{'at':hex(a),'op':op,'args':arg} for a,(op,arg) in sorted(code.items()) if op.startswith('b.') or op in ('cbz','cbnz','tbz','tbnz')],
                'calls':[{'at':hex(a),'op':op,'args':arg} for a,(op,arg) in sorted(code.items()) if op in ('bl','blr','br') or op=='b' and int(arg[1:],16) not in code]})
            found.add((cls,m['method']))
    assert found=={(c,n) for c,ns in SELECT.items() for n in ns}
    cell_path=RAW/'referenced-cells.json.gz';used.add(cell_path)
    cellmap={int(c['va'],16):c for c in json.loads(gzip.decompress(cell_path.read_bytes()))['cells']}
    cells=[dict(cellmap[a],f32=struct.unpack('<f',bytes.fromhex(cellmap[a]['hex']))[0]) for a in (0x756fbc,0x7570e0)]
    jumps=json.loads((EXTRA/'jump-table.json').read_text())['cells'][0]
    assert jumps['hex']=='0014273a'
    targets={str(i):hex(0x1574b8c+v*4) for i,v in enumerate(bytes.fromhex(jumps['hex']))}
    stat_fields=fields(class_text(dump,'Player_Get_Datas'))
    statics={hex(a):stat_fields[a] for a in (0x318,0x31c,0x320,0x33c,0x358,0x35c,0x360,0x364,0x368)}
    enum=dump[dump.index('public enum EventID '):];enum=enum[:enum.index('\n}')]
    events={int(n):name for name,n in re.findall(r'public const EventID (\w+) = (\d+);',enum)}
    return {'status':'PROVISIONAL_APK_NATIVE_RECEIVER_ORDER_NOT_RUNTIME','methods':result,'literal_cells':cells,
        'mb_death_state_targets':targets,'ability_coefficient_fields':statics,
        'event_names':{str(i):events[i] for i in (18,19,21,39,79,86)},
        'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(used)]}


if __name__=='__main__':
    import sys
    data=build()
    if '--check' in sys.argv:assert data==json.loads(OUT.read_text())
    else:OUT.write_text(json.dumps(data,indent=2)+'\n')
    print(f"{len(data['methods'])} receiver/helper source walks; {sum(m['instruction_count'] for m in data['methods'])} instructions; anchors PASS")
