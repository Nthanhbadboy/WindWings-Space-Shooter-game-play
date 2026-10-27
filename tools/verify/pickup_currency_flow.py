"""Reproducible APK/native/metadata pickup-to-currency contract (provisional)."""
import bisect,gzip,hashlib,json,re,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
from tools.verify.pickup_currency_models import Currency,currency_delta,collect_coin,COIN_KIND
BASE=ROOT/'reverse-engineering/raw/pickup-currency'
OUT=ROOT/'datas/pickup_currency_flow.json'
SELECT={'Player_Physics':{'Start','OnCollectItem','ItemCollected','OnTriggerEnter2D'},
 'Sub_Item':{'BurstOut','CollectTo','IsForceCollect'},'Item_Movement':{'OnEnable','Update'},
 'GP_Setup':{'get_Instance','get_stageIndex'},'Tech_Datas':{'GetTechLabLevel'},
 'Device_Get_Data':{'GetStatValue2'},'Device_Saved_Data':{'GetDevice'},
 'Droid_Movement1':{'Update','CollectItems'},
 'Player_Controller':{'Start','OnCollectCoin1','OnCollectCoin2','<Start>b__11_1'}}
ANCHORS={
 'Player_Physics':{0x14bc200:('mov','w1, #2'),0x14bc210:('bl','#0x1434c84'),
  0x14bc4ac:('add','x9, x9, #0x86'),0x14bc4b0:('adr','x10, #0x14bc4c0'),
  0x14bc4b4:('ldrb','w11, [x9, x8]'),0x14bc4b8:('add','x10, x10, x11, lsl #2'),
  0x14bc4c0:('ldr','x8, [x20, #0x20]'),0x14bc4d8:('blr','x9'),
  0x14bc4e0:('bl','#0x14bcd3c'),0x14bc5a8:('ldr','x8, [x20, #0x28]'),
  0x14bc5ac:('cbnz','x8, #0x14bc4c8')},
 'Player_Controller':{0x14c1cdc:('str','x20, [x22, #0x20]'),0x14c1d0c:('str','x20, [x22, #0x28]'),
  0x14c51f4:('bl','#0x14e628c'),0x14c51f8:('str','wzr, [x19, #0x54]'),
  0x14c5260:('bl','#0x12546d0'),0x14c5274:('cmp','w8, #0x3e7'),
  0x14c5298:('bl','#0x1250134'),0x14c52a0:('fdiv','s0, s0, s1'),
  0x14c52a4:('fadd','s0, s8, s0'),0x14c52a8:('str','s0, [x19, #0x54]')},
 'Device_Get_Data':{0x12501c4:('add','w20, w22, #4'),0x12501d4:('ldrsw','x8, [x19, #0x18]'),
  0x12501f0:('b.eq','#0x1250280'),0x125024c:('sub','x10, x10, #1'),
  0x1250268:('ldr','s1, [x8, #0x20]'),0x1250274:('fmul','s0, s0, s2'),0x1250278:('fadd','s0, s1, s0')},
 'Droid_Movement1':{0x1589f14:('fmov','s0, #5.00000000'),0x1589f48:('fmov','s0, #0.50000000'),
  0x1589f74:('bl','#0x1434cb4'),0x1589f8c:('bl','#0x123acd0'),0x1589f94:('str','x8, [x19, #0x30]'),
  0x158a35c:('fmov','s14, #5.00000000'),0x158a360:('fmov','s15, #0.50000000'),
  0x158a598:('bl','#0x1434cb4'),0x158a5c8:('bl','#0x123acd0')},
 'Item_Movement':{0x14cc2fc:('fcmp','s1, s0'),0x14cc300:('b.pl','#0x14cc680'),
  0x14cc31c:('bl','#0x2781804'),0x14cc354:('b','#0x123acd0')},
}

ANCHORS['Player_Physics'].update({0x14bca84:('bl','#0x14bc328'),0x14bcaa4:('b','#0x123acd0'),0x14bcaa8:('ldrb','w8, [x19, #0x90]')})
ANCHORS['Player_Controller'].update({
 0x14c36a0:('fcmp','s2, s0'),0x14c36ec:('fcmp','s1, s0'),0x14c372c:('fcmp','s1, s0'),0x14c376c:('fcmp','s1, s0'),
 0x14c3914:('fcmp','s2, s0'),0x14c391c:('b.mi','#0x14c39ec'),0x14c3958:('fcmp','s1, s0'),0x14c3998:('fcmp','s1, s0'),0x14c39d8:('fcmp','s1, s0'),
 0x14c37ac:('cmp','w20, #0x28'),0x14c37c4:('fcvtzs','w11, s0'),0x14c37ec:('str','w9, [x8, #0x20]'),0x14c37f8:('b','#0x1434ce4'),
 0x14c3a1c:('cmp','w20, #0x28'),0x14c3a34:('fcvtzs','w11, s0'),0x14c3a5c:('str','w9, [x8, #0x20]'),0x14c3a68:('b','#0x1434ce4'),
 0x14c21f0:('mov','w1, #0x1a'),0x14c2200:('bl','#0x1434c84')})


def build():
    dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';dump=gzip.decompress(dump_path.read_bytes()).decode()
    symbols_path=ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz'
    used={dump_path,symbols_path,BASE/'index.json',BASE/'cells.json',ROOT/'tools/verify/pickup_currency_models.py'}
    index=json.loads((BASE/'index.json').read_text())
    for row in index['files']:
        path=ROOT/row['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'];used.add(path)
    starts=sorted(set(int(x,16) for x in re.findall(r'// RVA: 0x([0-9a-fA-F]+)',dump)))
    methods=[];anchors=[];bodies={}
    for cls,names in SELECT.items():
        folder=ROOT/'reverse-engineering/raw/combat-receivers' if cls=='Player_Controller' else BASE/'native'
        path=folder/(cls+'.asm.txt');meta=folder/(cls+'.json');used|={path,meta};code=instructions(path);bodies[cls]=code
        found=set()
        for m in json.loads(meta.read_text())['methods']:
            if m['method'] not in names:continue
            start=int(m['rva'],16);end=min(start+m['bytes'],starts[bisect.bisect_right(starts,start)])
            assert not m['size_capped'] and all(a in code for a in range(start,end,4))
            methods.append(dict(cls=cls,method=m['method'],rva=hex(start),instructions=(end-start)//4,
              calls=[dict(at=hex(a),op=code[a][0],args=code[a][1]) for a in range(start,end,4) if code[a][0] in ('bl','blr','br') or code[a][0]=='b' and int(code[a][1][1:],16) not in range(start,end,4)]));found.add(m['method'])
        assert found==names,(cls,found,names)
        for at,expected in ANCHORS.get(cls,{}).items():
            assert code[at]==expected,(cls,hex(at),code[at],expected)
            anchors.append(dict(cls=cls,at=hex(at),op=expected[0],args=expected[1]))
    # Identical native arithmetic skeleton in both handlers: preserve each row for review.
    arithmetic=[]
    for start,end in ((0x14c358c,0x14c3800),(0x14c3800,0x14c3a70)):
        rows=[dict(at=hex(a),op=v[0],args=v[1]) for a,v in bodies['Player_Controller'].items() if start<=a<end and (v[0].startswith('f') or v[0] in ('scvtf','csel','b.pl','b.mi','b.lt','b.le','b','str'))]
        assert len([x for x in rows if x['op']=='fcvtzs'])==2
        assert len([x for x in rows if x['op']=='fcmp'])==6
        assert sum(x['op'] in ('b.pl','b.mi') for x in rows)==4
        arithmetic+=rows
    cells_raw=json.loads((BASE/'cells.json').read_text());cells={x['va']:x for x in cells_raw['cells']}
    constants=[]
    for va,expected in [('0x756f3c',5500.),('0x756e50',4300.),('0x7570f0',3300.),('0x756fa4',2500.),('0x756de8',.8600000143051147)]:
        row=cells[va];v=struct.unpack('<f',bytes.fromhex(row['hex']))[0];assert v==expected
        constants.append(dict(va=va,hex=row['hex'],value=v))
    dispatch=bytes.fromhex(cells['0x77a000']['hex'])[0x86:0x93]
    assert dispatch.hex()=='003a3d51667afd8ea2b6003aca'
    table=[dict(id=70001+i,byte=v,target=hex(0x14bc4c0+4*v),coin_handler=COIN_KIND.get(70001+i)) for i,v in enumerate(dispatch)]
    ss=json.loads(gzip.decompress(symbols_path.read_bytes()))['records'];symbols={r['Address']:r for k in ('ScriptMetadata','ScriptMetadataMethod') for r in ss[k]}
    rel={r['got']:r for r in cells_raw['relocations']};bindings=[]
    for got,name,rva in [('0x2ae8238','Player_Physics.OnCollectItem()',0x14bc280),('0x2ae8440','Player_Controller.OnCollectCoin1()',0x14c358c),('0x2ae8448','Player_Controller.OnCollectCoin2()',0x14c3800),('0x2ae84d0','Player_Controller.<Start>b__11_1()',0x14c5168)]:
        rr=rel[got];va,info,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert hex(va)==got and info==1027 and hex(target)==rr['effective']
        sy=symbols[target];assert sy['Name'].endswith(name) and sy['MethodAddress']==rva
        bindings.append(dict(got=got,effective=hex(target),name=sy['Name'],method_rva=hex(rva)))
    typed=[]
    for got,name in [('0x2adc9c0','GetComponent<IPooling>()'),('0x2adc9c8','IPooling_TypeInfo'),('0x2adbaf8','GameDatas_TypeInfo'),('0x2adc6d8','Map_Get_Datas_TypeInfo'),('0x2adbde8','Stage_Datas_TypeInfo'),('0x2adc840','GameMode_TypeInfo')]:
        rr=rel[got];va,info,target=struct.unpack('<QQq',bytes.fromhex(rr['rela_hex']));assert hex(va)==got and info==1027 and hex(target)==rr['effective']
        sy=symbols[target];assert sy['Name'].endswith(name),(got,sy,name);typed.append(dict(got=got,name=sy['Name'],effective=hex(target)))
    magic,version,ls,lc,ds,dc=struct.unpack('<6I',bytes.fromhex(cells_raw['metadata_header_hex']));assert magic==0xfab11baf and version==31
    literals=[]
    for got,text in [('0x2adf300','Item'),('0x2adf3e0','Test'),('0x2adcca0','Game')]:
        row=next(r for r in cells_raw['literals'] if r['got']==got);cell=row['pointee']
        assert cell['va']==rel[got]['effective'];encoded=struct.unpack('<Q',bytes.fromhex(cell['hex']))[0]
        idx=(encoded&0x1ffffffe)>>1;length,offset=struct.unpack('<II',bytes.fromhex(row['definition_hex']))
        assert encoded>>29==5 and row['index']==idx<lc//8 and offset+length<=dc
        assert row['data_file_offset']==ds+offset and len(bytes.fromhex(row['hex']))==length
        assert bytes.fromhex(row['hex']).decode()==row['utf8']==text;literals.append(dict(got=got,text=text,index=idx))
    slots=[('Player_Physics',0x20,'onCollectCoin1'),('Player_Physics',0x28,'onCollectCoin2'),('Player_Controller',0x54,'addPercentCoinByDevice'),('GP_Datas',0x20,'coinCount'),('Device',0x10,'id'),('Device',0x14,'lv'),('Device',0x18,'rank'),('Device_Get_Data',0x10,'percentByLevels2')]
    for cls,off,name in slots:assert fields(class_text(dump,cls))[off]['name']==name,(cls,hex(off),name)
    assert 'Slot: 0\n\tpublic abstract int GetID();' in dump
    assert 'public const EventID CollectItems = 2;' in dump and 'public const EventID AddCoin = 48;' in dump
    posters=cells_raw['direct_event2_post_candidates'];assert [x['post'] for x in posters]==['0x1589f74','0x158a598']
    for x in posters:
        at=int(x['mov'],16);post=int(x['post'],16);assert bodies['Droid_Movement1'][at]==('mov','w1, #2')
        raw=bytes.fromhex(x['window_hex']);word=struct.unpack_from('<I',raw,len(raw)-4)[0];imm=word&0x3ffffff
        if imm&0x2000000:imm-=0x4000000
        assert word>>26==0x25 and post+4*imm==0x1434cb4
    examples=[]
    for stage in (1,40,41,90):
        for coins in (0,2500,2501,3300,3301,4300,4301,5500,5501):
            examples.append(dict(stage=stage,coins=coins,tech=0,device_percent=0,small=currency_delta(1,stage,0,coins),large=currency_delta(2,stage,0,coins)))
    burst=[]
    for stage in (1,41):
        state=Currency()
        for kind in [1]*3+[2]*5:collect_coin(kind,state,get_stage=lambda:stage,get_tech=lambda:0,post=lambda *_:None)
        burst.append(dict(stage=stage,tech=0,device_percent=0,initial_coins=0,ordered_kinds=[1]*3+[2]*5,total_added=state.coin_count))
    assert [x['total_added'] for x in burst]==[69,165]
    return dict(schema='windwings.pickup-currency.v1',status='PROVISIONAL_APK_NATIVE_STABLE_FINITE_FIXTURES',
      xapk_sha256=cells_raw['xapk_sha256'],lib_sha256=cells_raw['lib_sha256'],
      methods=methods,native_anchors=anchors,currency_arithmetic=arithmetic,constants=constants,dispatch=table,bindings=bindings,type_bindings=typed,literals=literals,
      droid_direct_event2_posts=posters,examples=examples,burst28_examples=burst,
      scope=['Coin handlers and alias IDs, synchronous dispatch/store/sound/pool order; finite stable per-call fields, initialized classes.',
       'Droid suffix modeled after native target/scan eligibility, not a replacement for full Update/CollectItems movement.',
       'GetStatValue2 formula accepts explicit stat_rows/percentByLevels2; no new table values or equipment choices invented.',
       'Direct MOVZ-w1-2/call scan is a bounded candidate selector, not an exhaustive whole-program event producer proof.',
       'Stage/tech source getter gates decoded; no wallet persistence, Unity collision schedule, collection success or runtime payout guarantee.'],
      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(used)})


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    result=build();text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.check:assert OUT.read_text()==text,'pickup currency contract drift'
    else:OUT.write_text(text)
    print(f"pickup_currency_flow: {len(result['methods'])} methods / {len(result['native_anchors'])} anchors / {len(result['examples'])} payout pairs PASS")
if __name__=='__main__':main()
