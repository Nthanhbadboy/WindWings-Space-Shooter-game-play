"""576 InitializeArray sites -> source constructor container/index paths.
No heuristic segment-number labels, no campaign chapter/UI-number claim.
"""
import gzip,hashlib,json,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
from tools.verify.map_entries108_native import run
OUT=ROOT/'datas/l2_ef6b75ef108_map_entry_bindings.json.gz'
NAMES={0:'listMapTryPlayerDatas',8:'AllArenaStartMaps',16:'AllArenaRandomMaps',24:'AllPvPStartMaps',40:'listMapDatas',48:'listMapBranchDatas',56:'listIdBosses',64:'listMapFightBossDatas',72:'listMapChallangeDatas',80:'listMapEndlessDatas',88:'listMapObstacleDatas',96:'mapChallangeIndexs'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalize(result):
 objects=result['objects']
 def node(pointer,seen=()):
  if pointer in seen:raise ValueError('container cycle')
  obj=objects[hex(pointer)];out={k:v for k,v in obj.items() if k!='items'}
  if obj['kind']=='list':out['items']=[node(p,seen+(pointer,)) for p in obj['items']]
  elif obj['kind']=='dictionary':out['items']=obj['items']
  return out
 return {NAMES[int(off,16)]:node(ptr) for off,ptr in result['roots'].items()}
def build():
 used=set()
 def read(path):
  used.add(path);return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
 raw=read(ROOT/'reverse-engineering/raw/map-entries108/native.json.gz');tool=ROOT/'tools/recovery/map_entries108.py';used.add(tool);assert sha(tool)==raw['tool_sha256']
 for p,h in raw['sources'].items():used.add(ROOT/p);assert sha(ROOT/p)==h
 # This is the original constructor's range, not a textual presence-only audit.
 from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
 code=list(Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(bytes.fromhex(raw['method']['hex']),int(raw['method']['va'],16)));assert len(code)==25224
 dump_path=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dump_path);dump=gzip.decompress(dump_path.read_bytes()).decode();decl=fields(class_text(dump,'Map_Get_Datas'))
 for off,name in NAMES.items():assert decl[off]['name']==name
 assert fields(class_text(dump,'Board_Challange'))[4]['name']=='NumberChallanges'
 symbols=read(ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz')['records'];sy={r['Address']:r for k in ['ScriptMetadata','ScriptMetadataMethod'] for r in symbols[k]};relas=[]
 for r in raw['relocations']:
  va,kind,target=struct.unpack('<QQq',bytes.fromhex(r['hex']));assert hex(va)==r['got'] and kind==1027 and target==r['target'];relas.append(dict(got=r['got'],**sy[target]))
 assert len([r for r in relas if r['Name']=='Map_Get_Datas_TypeInfo'])==1
 zero=run(0);inline=run(1024);roots=normalize(zero);assert roots==normalize(inline),'source path mismatch zero-capacity helper vs inline-capacity writes'
 ia=read(ROOT/'reverse-engineering/il2cpp/ia-resolved.json')['methods']['Map_Get_Datas.cctor'];bycall={r['addr']:r for r in ia};assert len(bycall)==576
 bindings=[];other=[]
 def walk(node,root,path):
  if node['kind']=='list':
   for index,child in enumerate(node['items']):walk(child,root,path+[index])
  elif node['kind']=='array':
   row=dict(root=root,index_path=path,array_new_site=node['allocation'],length=node['length'],values=node['values'],initializer=node['initializer'])
   if node['initializer']:
    init=node['initializer'];r=bycall[init['pc']];assert r['array_new_addr']==node['allocation'] and r['field']==init['field'] and r['len']==node['length'] and r['ints']==node['values'];bindings.append(row)
   else:
    if root=='mapChallangeIndexs':row['length_status']='FIXTURE_ONLY_EXTERNAL_Board_Challange.NumberChallanges_not_recovered_value';row['value_status']='zero_initialized_new_array_in_fixture'
    other.append(row)
 for name,node in roots.items():walk(node,name,[])
 assert len(bindings)==len({r['initializer']['pc'] for r in bindings})==576
 assert len(other)==140
 assert len({r['array_new_site'] for r in bindings+other})==716
 legacy=read(ROOT/'datas/map_segments_full.json');byalloc={r['array_new_site']:r for r in bindings+other};oldrows=[r for s in legacy['segments'] for r in s['arrays']];assert len(oldrows)==715
 for old in oldrows:
  actual=byalloc[old['addr']];assert actual['length']==old['len'] and actual['values']==old['values']
 consumer_path=ROOT/'reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt';used.add(consumer_path);consumer_code=instructions(consumer_path)
 consumer_anchors={0x13feb84:('ldr','x0, [x8, #0x28]'),0x13feb90:('ldr','w8, [x0, #0x18]'),0x13feb98:('sub','w8, w8, #1'),0x13feba0:('cmp','w8, w19'),0x13feba4:('csel','w8, w8, w19, lt'),0x13feba8:('cmp','w19, #0'),0x13febac:('csel','w1, wzr, w8, lt'),0x13febb0:('b','#0x13feacc')}
 for pc,expected in consumer_anchors.items():assert consumer_code[pc]==expected
 stores=[]
 for row in zero['root_stores']:
  off=int(row['offset'],16);assert off in NAMES and row['value']==zero['roots'][row['offset']];stores.append(dict(pc=row['pc'],offset=row['offset'],field=NAMES[off],allocation=zero['objects'][hex(row['value'])]['allocation']))
 assert len(stores)==12 and len({r['field'] for r in stores})==12
 for p in ['tools/verify/map_entries108.py','tools/verify/map_entries108_native.py','tools/verify/combat_argument_audit.py','tools/verify/combat_rate_consumers.py','reverse-engineering/il2cpp/field-defaults.json']:used.add(ROOT/p)
 return dict(schema='windwings.map-entry108.v1',provisional=True,provenance='arena/ef6b75ef',scope='Constructor field/index binding for576 InitializeArray call sites; actual ARM64 with synthetic metadata/allocator/List/Dictionary hooks. NOT original container implementation, live readback, chapter/stage/UI numbering or mode-selection engine parity.',input_apk_sha256=raw['xapk_sha256'],input_lib_sha256=raw['lib_sha256'],toolchain=dict(capstone='5.0.3',unicorn='2.1.4'),native_instructions=25224,consumer_campaign_route=dict(method='Map_Get_Datas.GetListWaves',scope='Static source audit only, when control reaches13feb84; full mode selection/helper not executed',field='listMapDatas',static_offset='0x28',index='max(0,min(requested_mapIndex,list_count-1))',anchors=[dict(pc=hex(pc),op=v[0],args=v[1]) for pc,v in consumer_anchors.items()]),legacy_differential=dict(rows=715,value_mismatches=0,scope='same existing decoded payloads; confirms values but NOT independent APK decoder'),constructor_roots=roots,source_field_stores=stores,bindings=bindings,non_InitializeArray_leaves=other,relocations=relas,external_static_policy=dict(Board_Challange_NumberChallanges_fixture=0,source='Board_Challange_TypeInfo static+4, not observed default/runtime value',dynamic_array='mapChallangeIndexs'),capacity_crosscheck=dict(capacities=[0,1024],canonical_roots_equal=True,zero_calls=zero['calls'],inline_calls=inline['calls']),inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(used)})
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
 if a.check:assert OUT.read_bytes()==b,'108 artifact drift'
 else:OUT.write_bytes(b)
 print(f"map_entries108: {len(r['bindings'])} IA identities / {len(r['source_field_stores'])} field stores / 2 capacity executions PASS")
if __name__=='__main__':main()
