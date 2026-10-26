"""APK-derived resource/prefab binding contract, with raw-byte and native joins."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
RAW=ROOT/'reverse-engineering/raw/drone-loadout'
PREF=ROOT/'reverse-engineering/raw/drone-prefabs'
OUT=ROOT/'datas/drone_loadout_flow.json'
SELECT={'GP_Loader':{'StartDrones'},'GP_Setup':{'get_indexDrones'},'Drone_Saved_Datas':{'GetDroneUsed','SetDroneUsed','CheckDoubleIDDrone'}}
ANCHORS={'GP_Loader':{0x14f2908:('bl','#0x14f2a2c'),0x14f2924:('cmp','w8, #1'),0x14f292c:('b.lt','#0x14f29f8'),0x14f2954:('bl','#0x174a654'),0x14f2970:('bl','#0x278ab34'),0x14f2998:('bl','#0x173efb4'),0x14f29c0:('bl','#0x2789940'),0x14f29e4:('bl','#0x2789390'),0x14f29f4:('bl','#0x2781804'),0x14f2a00:('mov','w20, #1'),0x14f2a04:('tbnz','w26, #0, #0x14f28fc')},'GP_Setup':{0x14f2a8c:('mov','w1, #2'),0x14f2a94:('bl','#0x110d09c'),0x14f2a98:('cmp','w19, #4'),0x14f2aa0:('b.eq','#0x14f2adc'),0x14f2aac:('bl','#0x14dabd4'),0x14f2ac8:('bl','#0x14dabd4')},'Drone_Saved_Datas':{0x14dac64:('bl','#0x13f1a1c'),0x14dac68:('tbz','w0, #0x1f, #0x14dacb4'),0x14dacac:('mov','x2, xzr'),0x14dacb0:('bl','#0x13f1a04'),0x14dacf8:('bl','#0x13f1a1c'),0x14db2bc:('bl','#0x13f1a04'),0x14db2fc:('cmp','w0, #1'),0x14db310:('mov','w20, #0x4e21'),0x14db32c:('mov','w0, wzr'),0x14db334:('bl','#0x14db228'),0x14db348:('add','w20, w20, #1'),0x14db34c:('b.ne','#0x14db314')}}

def build():
    used={ROOT/'tools/verify/drone_loadout_flow.py',ROOT/'tools/verify/drone_loadout_models.py'}
    def read(p):
        used.add(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    idx=read(RAW/'index.json');raw=read(RAW/'cells.json');pidx=read(PREF/'component-index.json')
    for x in idx['files']:
        p=ROOT/x['path'];used.add(p);assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
    pp=PREF/'components.json.gz';records=read(pp);assert hashlib.sha256(pp.read_bytes()).hexdigest()==pidx['sha256']
    rp=PREF/'resource-managers.json.gz';managers=read(rp);assert hashlib.sha256(rp.read_bytes()).hexdigest()==pidx['resource_managers_sha256']
    dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dp);dump=gzip.decompress(dp.read_bytes()).decode()
    starts=sorted(set(int(x,16) for x in re.findall(r'// RVA: 0x([0-9A-Fa-f]+)',dump)))
    ranges=[];anchors=[]
    for cls,names in SELECT.items():
        p=RAW/'native'/(cls+'.asm.txt');used.add(p);code=instructions(p)
        for m in read(RAW/'native'/(cls+'.json'))['methods']:
            if m['method'] not in names:continue
            a=int(m['rva'],16);b=min(a+m['bytes'],starts[bisect.bisect_right(starts,a)])
            assert not m['size_capped'] and all(at in code for at in range(a,b,4))
            ranges.append(dict(cls=cls,method=m['method'],rva=hex(a),instructions=(b-a)//4))
        for a,expect in ANCHORS[cls].items():
            assert code[a]==expect,(cls,hex(a),code[a],expect)
            anchors.append(dict(cls=cls,at=hex(a),op=expect[0],args=expect[1]))
    symbols=read(ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz')['records'];sy={x['Address']:x for k in ('ScriptMetadata','ScriptMetadataMethod') for x in symbols[k]}
    rel={x['got']:x for x in raw['relocations']};joins=[]
    for got,name in [('0x2adbac8','Method$UnityEngine.Resources.Load<GameObject>()'),('0x2adbac0','Method$UnityEngine.Object.Instantiate<GameObject>()'),('0x2adc840','GameMode_TypeInfo'),('0x2adbb50','PlayerPreferences_TypeInfo')]:
        rr=rel[got];va,kind,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert hex(va)==got and kind==1027 and hex(target)==rr['effective']
        assert sy[target]['Name']==name;joins.append(dict(got=got,**sy[target]))
    literal={x['got']:x for x in raw['literals']}
    for got,text in [('0x2adc180','DroneUsed'),('0x2adf0e0','Prefabs/Drones/Drone_')]:
        x=literal[got];encoded=int.from_bytes(bytes.fromhex(x['pointee']['hex']),'little')
        assert encoded>>29==5 and (encoded&0x1fffffff)>>1==x['index']
        length,data_offset=struct.unpack('<II',bytes.fromhex(x['definition_hex']))
        assert length==len(bytes.fromhex(x['hex'])) and bytes.fromhex(x['hex']).decode()==x['utf8']==text
    scale=next(x for x in raw['float_load_candidates'] if x['va']=='0x756c14');assert scale['hex']=='cdcc4c3f'
    rows=[]
    for source_id in range(20001,20013):
        cls='Drone_Attack'+str(source_id-20000)
        candidates=[x for x in records if x['class_name']==cls]
        assert len(candidates)==3 and not any(x.get('error') for x in candidates)
        contexts=[];live=None
        for x in candidates:
            assert x['tree']['id']==source_id and struct.unpack_from('<i',bytes.fromhex(x['raw_object_hex']),32)[0]==source_id
            ancestor=x['ancestry'][-1];paths=ancestor['container_paths'];assert len(paths)==1
            contexts.append(dict(path=paths[0],path_id=x['path_id'],root_path_id=ancestor['gameobject']['path_id']))
            if paths[0].startswith('prefabs/drones/'):
                assert len(x['ancestry'])==1;live=x
        assert live and {x['path'] for x in contexts}=={'boards/board_drones','boards/popup_common/popup_newdrone',f'prefabs/drones/drone_{source_id}'}
        path=f'prefabs/drones/drone_{source_id}';root_id=live['gameobject']['path_id']
        matches=[(m,k,v) for m in managers for k,v in m['tree']['m_Container'] if k==path]
        assert len(matches)==1
        m,k,ptr=matches[0];assert ptr['m_PathID']==root_id
        target_file=m['serialized_file'] if ptr['m_FileID']==0 else m['externals'][ptr['m_FileID']-1]
        assert target_file.split('/')[-1]==live['serialized_file'].split('/')[-1]
        tree=live['tree'];rows.append(dict(source_id=source_id,cls=cls,resource_path='Prefabs/Drones/Drone_'+str(source_id),container_key=path,serialized_file=live['serialized_file'],component_path_id=live['path_id'],gameobject_path_id=root_id,contexts=contexts,serialized={k:v for k,v in tree.items() if not k.startswith('m_')},raw_sha256=hashlib.sha256(bytes.fromhex(live['raw_object_hex'])).hexdigest()))
        if source_id==20003:
            b=bytes.fromhex(live['raw_object_hex']);assert len(b)==124 and struct.unpack_from('<i',b,84)[0]==1
            assert struct.unpack_from('<fffiif',b,100)==(1.,2.,24.,80084,3,0.)
    return dict(schema=1,provisional=True,scope='12 resource-backed modern drone prefabs plus 24 UI copies; five bounded native methods; not a whole-program spawn census',bindings=rows,loadout=dict(slots=2,fresh_array_per_getter=True,mode4=[0,0],saved_prefix='DroneUsed',resource_prefix=literal['0x2adf0e0']['utf8'],scale_xy=struct.unpack('<f',bytes.fromhex(scale['hex']))[0],positions=[[-20,-20,0],[20,-20,0]]),literal_joins=[literal[x] for x in ('0x2adc180','0x2adf0e0')],native_ranges=ranges,native_anchors=anchors,symbol_joins=joins,recovery_errors=pidx['errors'],inputs=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(used)])

if __name__=='__main__':
    OUT.write_text(json.dumps(build(),indent=2)+'\n');print(OUT)
