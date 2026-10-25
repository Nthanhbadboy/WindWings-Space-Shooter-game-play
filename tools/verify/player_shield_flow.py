"""Recheck exact Invoke metadata literal, packed float store and shield/zone roots."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
RAW=ROOT/'reverse-engineering/raw'
OUT=ROOT/'datas/player_shield_flow.json'
NAMES={'OnShieldActive','OnShieldDroidActive101','OnShieldDroidActive103',
       'OnShieldOneHitActive','Startup','SetInvisible','RebornDone'}
ANCHORS={
 0x14c44e0:('bl','#0x2782540'),0x14c44f4:('bl','#0x27824b8'),
 0x14c451c:('ldr','s0, [x8, #8]'),0x14c4520:('bl','#0x27822d4'),
 0x14c2d50:('bl','#0x14bb960'),0x14c2d5c:('strb','w8, [x20, #0x31]'),
 0x14c2680:('strb','w8, [x0, #0x50]'),0x14c2690:('ldrb','w8, [x0, #0x52]'),
 0x14c26a4:('strb','w9, [x8, #0x30]'),0x14c26c8:('strb','wzr, [x8, #0x30]'),
 0x14c26ec:('strb','w9, [x0, #0x51]'),0x14c2754:('strb','w9, [x0, #0x52]'),
 0x14c27c0:('strb','w10, [x0, #0x53]'),0x14c27e4:('ldrb','w9, [x0, #0x52]'),
 0x14c2f70:('b','#0x14c2fd0'),0x14c2f9c:('strb','w22, [x19, #0x70]'),
 0x14c2fac:('bl','#0x27829d8'),0x14c2fc4:('bl','#0x278276c'),
 0x14c2fd4:('cbnz','w8, #0x14c3084'),0x14c2fe0:('strb','w22, [x8, #0x49]'),
 0x14c2fec:('strb','w22, [x8, #0x91]'),0x14c3064:('strb','wzr, [x19, #0x70]'),
 0x14c4dbc:('strb','wzr, [x19, #0xa8]'),0x14c4e54:('cbz','w8, #0x14c4f2c'),
 0x14c4e64:('strb','w9, [x8, #0x90]'),0x14c4e78:('strb','wzr, [x8, #0x20]'),
 0x14c4edc:('bl','#0x14c2d04'),0x14c4f34:('cbz','w8, #0x14c4f80'),
 0x14c4f80:('cbnz','w9, #0x14c4e58'),0x14c4f88:('cbnz','w8, #0x14c4f98'),
 0x14c4f94:('strb','wzr, [x8, #0x30]'),0x14c4fa4:('cset','w9, eq'),
}


def build():
    used={ROOT/'reverse-engineering/il2cpp/dump.cs.gz',ROOT/'tools/verify/player_shield_models.py'}
    dump=gzip.decompress(next(p for p in used if p.suffix=='.gz').read_bytes()).decode()
    expected={'Player_Physics':{0x90:'activeHitEnemey',0x91:'invisible'},
      'Player_Controller':{0x48:'playerTalentScript',0x50:'isActiveShieldBySkill',
        0x51:'isActiveShieldByDroid101',0x52:'isActiveShieldByDroid103',0x53:'isActiveShieldOnehit',0xa8:'inReborning'},
      'Player_Talent':{0x20:'reborning'},'Player_Get_Datas':{8:'TimeResetInvincible',12:'TimeCanActiveInvincible'}}
    typed=[]
    for cls,wanted in expected.items():
        ff=fields(class_text(dump,cls))
        for offset,name in wanted.items():
            assert ff[offset]['name']==name,(cls,offset,ff.get(offset))
            typed.append({'class':cls,'offset':hex(offset),'name':name})
    path=RAW/'player-invincibility/invoke.json';used.add(path);r=json.loads(path.read_text())
    sl=r['string_literal'];magic,version,start,size,data,ds=struct.unpack('<6I',bytes.fromhex(r['metadata_header_hex']))
    assert magic==0xfab11baf and version==31
    rel={row['got']:row for row in r['relocations']}
    for got,row in rel.items():
        va,info,target=struct.unpack('<QQq',bytes.fromhex(row['rela_hex']))
        assert hex(va)==got and info==1027 and hex(target)==row['effective']
        assert row['pointee_cell']['va']==row['effective']
    encoded=struct.unpack('<Q',bytes.fromhex(rel['0x2ae8560']['pointee_cell']['hex']))[0]
    assert encoded==int(sl['encoded'],16) and encoded>>29==5
    index=(encoded&0x1ffffffe)>>1
    length,offset=struct.unpack('<II',bytes.fromhex(sl['definition_hex']))
    assert index==sl['index'] and index<size//8 and offset+length<=ds
    assert sl['definition_file_offset']==start+index*8 and sl['data_file_offset']==data+offset
    text=bytes.fromhex(sl['hex']);assert len(text)==length and text.decode()==sl['utf8']=='RebornDone'
    path=RAW/'combat-chain/symbols.json.gz';used.add(path)
    ss=json.loads(gzip.decompress(path.read_bytes()))['records']['ScriptMetadata']
    sy=[s for s in ss if s['Address']==int(rel['0x2ae82a0']['effective'],16)]
    assert len(sy)==1 and sy[0]['Name']=='SpaceShooter.Gameplay.GP_Controller_TypeInfo'
    path=RAW/'combat-chain/relocations.json.gz';used.add(path)
    rr=next(r for r in json.loads(gzip.decompress(path.read_bytes()))['entries'] if r['offset']=='0x2adbdd8')
    va,info,target=struct.unpack('<QQq',bytes.fromhex(rr['raw_hex']))
    assert va==0x2adbdd8 and info==1027 and hex(target)==rr['addend']
    datatype=next(s for s in ss if s['Address']==target)
    assert datatype['Name'].endswith('Player_Get_Datas_TypeInfo')
    path=RAW/'combat-chain/referenced-cells.json.gz';used.add(path)
    cell=next(c for c in json.loads(gzip.decompress(path.read_bytes()))['cells'] if c['va']=='0x757ce0')
    values=struct.unpack('<ff',bytes.fromhex(cell['hex']));assert values==(3,10)
    path=RAW/'combat-chain/native/Player_Get_Datas.asm.txt';used.add(path);code=instructions(path)
    assert code[0x14e5acc]==('ldr','d0, [x9, #0xce0]') and code[0x14e5b0c]==('str','d0, [x8, #8]')
    path=RAW/'combat-receivers/Player_Controller.asm.txt';used.add(path);code=instructions(path)
    for a,v in ANCHORS.items():assert code[a]==v,(hex(a),code[a],v)
    path=RAW/'combat-receivers/Player_Controller._DoExtraLife_d__62.asm.txt';used.add(path)
    normal=instructions(path)
    for a,v in {0x14c6130:('bl','#0x2782540'),0x14c6144:('bl','#0x27824b8'),
                0x14c6174:('ldr','s0, [x8, #8]'),0x14c6178:('bl','#0x27822d4')}.items():assert normal[a]==v
    path=RAW/'combat-receivers/Player_Controller.json';used.add(path);meta=json.loads(path.read_text())
    starts=sorted(set(int(s,16) for s in re.findall(r'// RVA: 0x([0-9a-fA-F]+)',dump)))
    methods=[]
    for m in meta['methods']:
        if m['method'] not in NAMES:continue
        a=int(m['rva'],16);end=min(a+m['bytes'],starts[bisect.bisect_right(starts,a)])
        assert not m['size_capped'] and all(i in code for i in range(a,end,4))
        methods.append({'method':m['method'],'rva':m['rva'],'instructions':(end-a)//4,
          'calls':[{'at':hex(i),'op':code[i][0],'args':code[i][1]} for i in range(a,end,4) if code[i][0] in ('bl','blr','br')]})
    assert {m['method'] for m in methods}==NAMES
    return {'status':'PROVISIONAL_APK_INVOKE_SHIELD_ZONE_ROOTS_NOT_UNITY_TIMING',
      'invoke_target':sl,'delay_typeinfo_binding':dict(got='0x2adbdd8',effective=hex(target),symbol=datatype['Name']),'global_typeinfo':sy[0],'packed_static_initializer':dict(cell,TimeResetInvincible=values[0],TimeCanActiveInvincible=values[1]),
      'typed_fields':typed,'methods':methods,'anchors':[dict(at=hex(a),op=v[0],args=v[1]) for a,v in ANCHORS.items()],
      'source_artifacts':[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(used)]}


if __name__=='__main__':
    import sys
    r=build()
    if '--check' in sys.argv:assert r==json.loads(OUT.read_text())
    else:OUT.write_text(json.dumps(r,indent=2)+'\n')
    print(len(r['methods']),'shield/zone roots;',len(r['anchors']),'anchors PASS')
