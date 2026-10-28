"""Run original Map cctor instructions; explicit allocation/List/Dictionary hooks.
Container semantics are fixture contracts, not a Unity/IL2CPP runtime observation.
"""
import gzip,hashlib,json,struct
from tools.verify.combat_argument_audit import ROOT

def run(capacity=0,challenge_length=0):
 if type(challenge_length)!=int or not 0<=challenge_length<=1024:raise ValueError("fixture challenge length")
 if type(capacity)!=int or capacity<0 or capacity>2048:raise ValueError("fixture capacity")
 import unicorn as u
 from unicorn import arm64_const as a
 raw=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/map-entries108/native.json.gz').read_bytes()));m=raw['method']
 records=json.load(gzip.open(ROOT/'reverse-engineering/raw/combat-chain/symbols.json.gz'))['records'];symbols={s['Address']:s for k in ['ScriptMetadata','ScriptMetadataMethod'] for s in records[k]};defaults=json.loads((ROOT/'reverse-engineering/il2cpp/field-defaults.json').read_bytes())['fields']
 uc=u.Uc(u.UC_ARCH_ARM64,u.UC_MODE_ARM);mapped=set();heap=[0x50000000];objects={};handles={};statics={};calls=[];last=[None];backing={};root_stores=[]
 def put(p,b):
  for page in range(p&~4095,(p+len(b)+4095)&~4095,4096):
   if page not in mapped:uc.mem_map(page,4096);mapped.add(page)
  uc.mem_write(p,b)
 def q(p,v):put(p,struct.pack('<Q',v))
 def w(p,v):put(p,struct.pack('<I',v&0xffffffff))
 def rq(p):return struct.unpack('<Q',uc.mem_read(p,8))[0]
 def rw(p):return struct.unpack('<I',uc.mem_read(p,4))[0]
 def alloc(size=4096):
  p=heap[0];heap[0]+=(size+4095)&~4095;put(p,b'\0'*size);return p
 def meta(name):
  if name in handles:return handles[name]
  p=alloc();put(p,struct.pack('<Q',p)*512);w(p+0xe0,1);sb=alloc();q(p+0xb8,sb);handles[name]=p;statics[name]=sb;return p
 for r in raw['relocations']:
  name=symbols[r['target']]['Name'];q(int(r['got'],16),r['target']);q(r['target'],meta(name))
 w(statics['Board_Challange_TypeInfo']+4,challenge_length)
 # Candidate RELA does not imply all are used. Initialization bit skips only the
 # metadata resolver prelude; all candidate metadata cells already have fixtures.
 put(0x2ce1c58,b'\1');entry=int(m['va'],16);put(entry,bytes.fromhex(m['hex']));stop=0x40000000;put(stop,bytes.fromhex('1f2003d5'));stack=alloc(65536)
 hooks={0x110d240:'newobj',0x110d09c:'newarray',0x205b07c:'InitializeArray',0x1bd768c:'List.ctor',0x1bd7e58:'List.Add',0x192b290:'Dictionary.ctor',0x192bbf8:'Dictionary.Add',0x110d12c:'classinit',0x110d028:'resolve',0x110d250:'null',0x110d258:'bounds'}
 for pc in hooks:put(pc,bytes.fromhex('c0035fd6'))
 reverse={v:k for k,v in handles.items()}
 def hook(uc,pc,size,_):
  if entry<=pc<entry+m['width']:last[0]=pc
  if pc not in hooks:return
  name=hooks[pc];x=[uc.reg_read(getattr(a,'UC_ARM64_REG_X'+str(i))) for i in range(4)];site=uc.reg_read(a.UC_ARM64_REG_LR)-4;calls.append(dict(pc=hex(site),operation=name))
  if name=='newobj':
   p=alloc();q(p,x[0]);objects[p]=dict(kind='object',type=reverse.get(x[0],'unknown'),allocation=hex(site));uc.reg_write(a.UC_ARM64_REG_X0,p)
  elif name=='newarray':
   n=x[1]&0xffffffff;assert n<10000,(hex(site),n);p=alloc(32+n*8);q(p,x[0]);w(p+24,n);objects[p]=dict(kind='array',element_type=reverse.get(x[0],'unknown'),length=n,allocation=hex(site),initializer=None);uc.reg_write(a.UC_ARM64_REG_X0,p)
  elif name=='InitializeArray':
   o=objects[x[0]];field=reverse[x[1]].removeprefix('Field$');b=bytes.fromhex(defaults[field]['raw'])[:o['length']*4];assert len(b)==o['length']*4 and hashlib.sha256(b).hexdigest().upper()==field.split('.')[-1];put(x[0]+32,b);o['initializer']=dict(pc=hex(site),field=field)
  elif name=='List.ctor':
   p=alloc(32+8*capacity);w(p+24,capacity);q(x[0]+16,p);w(x[0]+24,0);objects[x[0]].update(kind='list',items=[])
   for page in range(p&~4095,(p+32+8*capacity+4095)&~4095,4096):backing[page]=(p,x[0])
  elif name=='List.Add':
   o=objects[x[0]];assert o['kind']=='list';o['items'].append(x[1]);w(x[0]+24,len(o['items']))
   # Zero backing capacity forces source's out-of-line Add path; hook owns
   # container sequence. It does NOT emulate GC/List resize implementation.
  elif name=='Dictionary.ctor':objects[x[0]].update(kind='dictionary',items=[])
  elif name=='Dictionary.Add':objects[x[0]]['items'].append([x[1]&0xffffffff,x[2]&0xffffffff])
  elif name in ['null','bounds']:raise ValueError((name,hex(site),hex(last[0])))
  else:raise ValueError(('unexpected external',name,hex(site)))
 def store(uc,access,address,size,value,_):
  sb=statics['Map_Get_Datas_TypeInfo']
  if size==8 and sb<=address<sb+0x68:root_stores.append(dict(pc=hex(uc.reg_read(a.UC_ARM64_REG_PC)),offset=hex(address-sb),value=value))
  if size!=8 or (address&~4095) not in backing:return
  base,owner=backing[address&~4095];index=(address-base-32)//8
  if address<base+32 or index>=capacity:return
  assert address==base+32+index*8 and index==len(objects[owner]['items']),(hex(address),index)
  objects[owner]['items'].append(value)
 uc.hook_add(u.UC_HOOK_MEM_WRITE,store);uc.hook_add(u.UC_HOOK_CODE,hook);uc.reg_write(a.UC_ARM64_REG_SP,stack+0xf000);uc.reg_write(a.UC_ARM64_REG_LR,stop)
 try:uc.emu_start(entry,stop,count=200000)
 except Exception as e:raise RuntimeError(f'{e}; PC={hex(uc.reg_read(a.UC_ARM64_REG_PC))}; last={last[0]}; x25={hex(uc.reg_read(a.UC_ARM64_REG_X25))}; recent={calls[-4:]}') from e
 assert uc.reg_read(a.UC_ARM64_REG_PC)==stop,'bounded source did not return'
 roots={hex(i):rq(statics['Map_Get_Datas_TypeInfo']+i) for i in [0,8,16,24,40,48,56,64,72,80,88,96]}
 for p,o in objects.items():
  if o['kind']=='array':o['values']=list(struct.unpack('<'+'i'*o['length'],uc.mem_read(p+32,o['length']*4)))
 return dict(capacity=capacity,challenge_length=challenge_length,root_stores=root_stores,roots=roots,objects={hex(p):o for p,o in objects.items()},calls=calls,scope='Original cctor ARM64 with synthetic metadata/heap and explicit container hooks; NOT original List/Dictionary/allocator implementations or live runtime')
