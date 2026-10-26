"""Board_Players24 consumer contract, original byte joins + bounded ARM64 fixtures."""
import gzip,hashlib,json,struct
from tools.verify.combat_argument_audit import ROOT,instructions
from tools.verify.combat_rate_consumers import class_text,fields
from tools.verify.board_power107_native import run,method
from tools.verify.player_hp_board_models import board_power
RAW=ROOT/'reverse-engineering/raw/board-power107';OUT=ROOT/'datas/l2_ef6b75ef107_board_power.json.gz'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 used=set()
 def read(p):
  used.add(p);return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
 r=read(RAW/'cells.json');rp=ROOT/'tools/recovery/board_power107.py';used.add(rp);assert sha(rp)==r['tool_sha256']
 sym=read(ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz')['records']['ScriptMetadata'];symbols={s['Address']:s for s in sym};joins=[]
 for row in r['relocations']:
  va,kind,target=struct.unpack('<QQq',bytes.fromhex(row['hex']));assert hex(va)==row['got'] and kind==1027 and target==row['target'];joins.append(dict(got=row['got'],**symbols[target]))
 names={j['got']:j['Name'] for j in joins};assert names['0x2addda0']=='Board_Players_TypeInfo'
 arrays=[];header=bytes.fromhex(r['header_hex']);dataoff,datasize=struct.unpack_from('<II',header,72)
 for a,got in zip(r['arrays'],['0x2adfd00','0x2adfd08']):
  b=bytes.fromhex(a['hex']);assert len(b)==96 and hashlib.sha256(b).hexdigest().upper()==a['field'].split('.')[-1];assert names[got]=='Field$'+a['field'];fi,ty,di=struct.unpack('<iii',bytes.fromhex(a['entry_hex']));assert fi==a['field_index'] and dataoff+di==a['data_file_offset'] and 0<=di<=datasize-96;assert bytes.fromhex(a['name_hex']).decode().rstrip('\0')==a['field'].split('.')[-1]
  arrays.append(dict(name=a['name'],got=got,field=a['field'],count=24,hex=a['hex'],values=list(struct.unpack('<24f',b))))
 mp=ROOT/'reverse-engineering/raw/l3-ui-native/method-bytes.json.gz';methods=read(mp)['methods'];ap=ROOT/'reverse-engineering/raw/l3-ui-native/native/Board_Players.asm.txt';used.add(ap);asm=instructions(ap)
 from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
 cs=Cs(CS_ARCH_ARM64,CS_MODE_ARM);ranges=[]
 for m in methods:
  if m['cls']!='Board_Players' or m['method'] not in {'ctor','cctor','GetPlayerPower','SetPlayerInfo','SetUpgradeCost'}:continue
  b=bytes.fromhex(m['hex']);decoded=list(cs.disasm(b,int(m['va'],16)));assert len(decoded)*4==m['width'];assert all(asm[i.address]==(i.mnemonic,i.op_str) for i in decoded)
  ranges.append(dict(method=m['method'],va=m['va'],instructions=len(decoded),width=m['width'],sha256=hashlib.sha256(b).hexdigest()))
 for c in r['checked_existing_methods']:
  m=next(x for x in ranges if x['method']==c['method']);assert (m['va'],m['width'],m['sha256'])==(c['va'],c['width'],c['sha256'])
 anchors={0x12d62fc:('mov','w8, #0x2711'),0x12d6304:('str','w8, [x19, #0x138]'),0x12d63d0:('mov','w1, #0x18'),0x12d63f4:('bl','#0x205b07c'),0x12d6404:('str','x19, [x8, #0x10]'),0x12d63fc:('mov','w1, #0x18'),0x12d641c:('bl','#0x205b07c'),0x12d642c:('str','x19, [x8, #0x18]'),0x12d5e88:('bl','#0x14e3b20'),0x12d5eac:('ldr','x8, [x11, #0x10]'),0x12d5edc:('ldr','x11, [x11, #0x18]'),0x12d5f20:('fmul','s0, s1, s0'),0x12d5f28:('fadd','s9, s0, s1'),0x12d5f4c:('fmul','s9, s8, s9'),0x12d5fbc:('tst','x8, #1'),0x12d5fc0:('fcsel','d0, d0, d1, eq'),0x12d13f4:('ldr','x21, [x19, #0x40]'),0x12d13fc:('bl','#0x12d5dfc'),0x12d2be4:('ldr','x21, [x19, #0x40]'),0x12d2bf0:('bl','#0x12d5dfc')}
 for pc,v in anchors.items():assert asm[pc]==v,(hex(pc),asm[pc],v)
 dp=ROOT/'reverse-engineering/il2cpp/dump.cs.gz';used.add(dp);dump=gzip.decompress(dp.read_bytes()).decode();f=fields(class_text(dump,'Board_Players'))
 for offset,name in [(0x10,'allBasicAtk'),(0x18,'allDeltaAtk'),(0x40,'textPlayerPower'),(0x138,'indexDefault')]:assert f[offset]['name']==name
 from tools.verify.l3_chain_graph import RAW as CHAIN,read_chunks,key
 idx=read(CHAIN/'index.json');objects=[]
 for row in read_chunks(idx,'objects'):
  if key(row) in {('data.unity3d/resources.assets',650952),('data.unity3d/resources.assets',619564)}:objects.append(row)
 assert len(objects)==2;board=next(o for o in objects if o['path_id']==650952);assert board['tree']['textPlayerPower']=={'m_FileID':0,'m_PathID':619564}
 # Index embeds SHA of all chunks; read_chunks validates every visited chunk.
 basic,delta=[a['values'] for a in arrays];fixtures=[]
 for source in range(10001,10025):
  for level in [0,1,10,99]:
   native=run(source,level,basic,delta);model=board_power(source,get_level=lambda _:level,basic=basic,delta=delta,index_default=10001);assert (native['pre_round_f32'],native['rounded'])==(model['power'],model['rounded']);fixtures.append(dict(source=source,level=level,**native))
 for source in [10000,10025]:
  native=run(source,1,basic,delta);model=board_power(source,get_level=lambda _:1,basic=basic,delta=delta,index_default=10001);assert native['rounded']==model['rounded'];fixtures.append(dict(source=source,level=1,**native))
 for p in ['tools/verify/board_power107.py','tools/verify/board_power107_native.py','tools/verify/player_hp_board_models.py','tools/verify/enemy_damage_model.py','tools/verify/l3_chain_graph.py','tools/verify/combat_argument_audit.py','tools/verify/combat_rate_consumers.py','tools/verify/ui_composition.py']:used.add(ROOT/p)
 return dict(schema='windwings.board-power107.v1',provisional=True,provenance='arena/ef6b75ef',scope='Source consumer + actual bounded ARM64; synthetic heap, externally supplied level/modf/string hooks. NOT live Unity, DPS, economy/save, localization or render acceptance.',toolchain=dict(capstone='5.0.3',unicorn='2.1.4'),raw_input_pins={k:r[k] for k in ['xapk_sha256','lib_sha256','metadata_sha256']},joins=joins,arrays=arrays,methods=ranges,anchors=[dict(pc=hex(pc),op=v[0],args=v[1]) for pc,v in anchors.items()],ui_sink=objects,fixtures=fixtures,formula='f32(basic[clamp(source-10001)] * f32(1 + f32(delta[clamp(source-10001)] * f32(GetPlayerLevel(source))))) then ties-even Int32 in tested finite domain',inputs={str(p.relative_to(ROOT)):sha(p) for p in sorted(used)})
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
 if a.check:assert OUT.read_bytes()==b,'artifact drift'
 else:OUT.write_bytes(b)
 print(f"board_power107: {len(r['arrays'])} arrays / {len(r['methods'])} methods / {len(r['fixtures'])} ARM64 fixtures PASS")
if __name__=='__main__':main()
