"""#21: original bounded Map cctor bytes/RELA, not a new blob-count report."""
import argparse,gzip,hashlib,io,json,re,struct,zipfile
from pathlib import Path
from combat_coroutine_cells import APK_SHA,LIB_SHA,extract
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def recover(path):
 data=path.read_bytes();assert sha(data)==APK_SHA;found=[]
 with zipfile.ZipFile(io.BytesIO(data)) as outer:
  for name in outer.namelist():
   if not name.endswith('.apk'):continue
   with zipfile.ZipFile(io.BytesIO(outer.read(name))) as z:
    name='lib/arm64-v8a/libil2cpp.so'
    if name in z.namelist():found.append(z.read(name))
 assert len(found)==1;b=found[0];assert sha(b)==LIB_SHA
 source=ROOT/'reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.json';meta=json.loads(source.read_bytes());m=next(r for r in meta['methods'] if r['method']=='cctor');assert m['bytes']==100896 and not m['size_capped'] and m['ends_clean'];cell=extract(b,((int(m['rva'],16),m['bytes']),))['cells'][0]
 from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
 instructions=list(Cs(CS_ARCH_ARM64,CS_MODE_ARM).disasm(bytes.fromhex(cell['hex']),int(cell['va'],16)));assert len(instructions)*4==cell['width'];asm=ROOT/'reverse-engineering/raw/il2cpp-consts/Map_Get_Datas.asm.txt';expected={int(a,16):(op,args.strip()) for a,op,args in re.findall(r'^\s*0x([0-9a-f]+): (\w+)\s+(.*?)\s*$',asm.read_text(),re.M)}
 for i in instructions:assert expected[i.address]==(i.mnemonic,i.op_str),(hex(i.address),expected[i.address],i.mnemonic,i.op_str)
 pages={};wanted=set()
 for i in instructions:
  mt=re.fullmatch(r'(x\d+), #0x([0-9a-f]+)',i.op_str)
  if i.mnemonic=='adrp' and mt:pages[mt[1]]=int(mt[2],16)
  mt=re.fullmatch(r'x\d+, \[(x\d+)(?:, #0x([0-9a-f]+))?\]',i.op_str)
  if i.mnemonic=='ldr' and mt and mt[1] in pages:wanted.add(pages[mt[1]]+int(mt[2] or '0',16))
 shoff=struct.unpack_from('<Q',b,40)[0];size,count=struct.unpack_from('<HH',b,58);rels=[]
 for n in range(count):
  h=struct.unpack_from('<IIQQQQIIQQ',b,shoff+n*size)
  if h[1]!=4:continue
  for p in range(h[4],h[4]+h[5],h[9] or 24):
   va,kind,target=struct.unpack_from('<QQq',b,p)
   if va in wanted and kind==1027:rels.append(dict(got=hex(va),target=target,file_offset=p,hex=b[p:p+24].hex()))
 out=dict(provisional=True,provenance='arena/ef6b75ef',scope='Original native bytes + candidate RELA; NO entry-binding or dynamic pointer-flow conclusion yet',xapk_sha256=APK_SHA,lib_sha256=LIB_SHA,tool_sha256=sha(Path(__file__).read_bytes()),sources={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [source,asm,ROOT/'tools/recovery/combat_coroutine_cells.py']},method=cell,relocations=rels)
 dest=ROOT/'reverse-engineering/raw/map-entries108';dest.mkdir(parents=True,exist_ok=True);(dest/'native.json.gz').write_bytes(gzip.compress((json.dumps(out,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0));print('Map cctor original',len(instructions),'instructions;',len(rels),'candidate RELA; identity binding NOT proven')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--xapk',type=Path,required=True);recover(p.parse_args().xapk)
