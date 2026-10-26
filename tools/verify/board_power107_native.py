"""Actual APK ARM64 GetPlayerPower, synthetic heap + explicit external hooks.
NOT Unity runtime. Finite signed Int32 inputs/results only; no formatting claim.
"""
import gzip,json,math,struct
from tools.verify.combat_argument_audit import ROOT
from tools.verify.player_hp_board_models import board_power

def method():
 r=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/l3-ui-native/method-bytes.json.gz').read_bytes()))
 return next(m for m in r['methods'] if m['cls']=='Board_Players' and m['method']=='GetPlayerPower')
def run(source,level,basic,delta,index_default=10001):
 import unicorn as u
 from unicorn import arm64_const as a
 if type(source)!=int or type(level)!=int or not -(1<<31)<=source<1<<31 or not -(1<<31)<=level<1<<31 or not -(1<<31)<=source-index_default<1<<31:raise ValueError('outside fixture signed Int32 domain')
 uc=u.Uc(u.UC_ARCH_ARM64,u.UC_MODE_ARM);mapped=set();trace=[];result={}
 def put(p,b):
  for page in range(p&~4095,(p+len(b)+4095)&~4095,4096):
   if page not in mapped:uc.mem_map(page,4096);mapped.add(page)
  uc.mem_write(p,b)
 def q(p,v):put(p,struct.pack('<Q',v))
 def w(p,v):put(p,struct.pack('<I',v&0xffffffff))
 m=method();entry=int(m['va'],16);put(entry,bytes.fromhex(m['hex']));this=0x5000000;klass=0x5010000;static=0x5020000;stop=0x7000000
 put(this,b'\0'*0x2000);put(klass,b'\0'*0x2000);put(static,b'\0'*0x2000);put(0x6000000,b'\0'*0x10000);put(stop,bytes.fromhex('1f2003d5'));w(this+0x138,index_default)
 put(0x2ce13ce,b'\1');put(0x2ce0f73,b'\1')
 for i,got in enumerate([0x2adbde0,0x2addda0,0x2adc798]):
  cell=0x5030000+i*0x100;q(got,cell);q(cell,klass)
 w(klass+0xe0,1);q(klass+0xb8,static)
 for got in [0x2add800,0x2add8e8]:q(got,0x5040000);q(0x5040000,0x5050000)
 for n,values in enumerate([basic,delta]):
  p=0x5060000+n*0x1000;q(static+0x10+n*8,0 if values is None else p)
  if values is not None:
   put(p,b'\0'*32);w(p+0x18,len(values));put(p+0x20,struct.pack('<'+'f'*len(values),*values))
 hooks={0x14e3b20:'GetPlayerLevel',0x2990b70:'modf',0x21033cc:'Int32.ToString',0x1fe4c90:'Concat',0x110d250:'null',0x110d258:'bounds'}
 for pc in hooks:put(pc,bytes.fromhex('c0035fd6'))
 def hook(uc,pc,size,_):
  if pc==0x12d5f70:result['pre_round_f32']=struct.unpack('<f',struct.pack('<I',uc.reg_read(a.UC_ARM64_REG_S9)))[0]
  if pc not in hooks:return
  name=hooks[pc];trace.append(dict(operation=name,x0=uc.reg_read(a.UC_ARM64_REG_X0)))
  if name=='GetPlayerLevel':uc.reg_write(a.UC_ARM64_REG_W0,level&0xffffffff)
  elif name=='modf':
   v=struct.unpack('<d',struct.pack('<Q',uc.reg_read(a.UC_ARM64_REG_D0)))[0];f,i=math.modf(v);put(uc.reg_read(a.UC_ARM64_REG_X0),struct.pack('<d',i));uc.reg_write(a.UC_ARM64_REG_D0,struct.unpack('<Q',struct.pack('<d',f))[0])
  elif name=='Int32.ToString':
   result['rounded']=struct.unpack('<i',uc.mem_read(uc.reg_read(a.UC_ARM64_REG_X0),4))[0];uc.reg_write(a.UC_ARM64_REG_X0,0x5050100)
  elif name=='Concat':uc.reg_write(a.UC_ARM64_REG_X0,0x5050200)
  elif name=='null':raise ValueError('native null array trap')
  else:raise IndexError('native array bounds trap')
 uc.hook_add(u.UC_HOOK_CODE,hook);uc.reg_write(a.UC_ARM64_REG_SP,0x600f000);uc.reg_write(a.UC_ARM64_REG_LR,stop);uc.reg_write(a.UC_ARM64_REG_X0,this);uc.reg_write(a.UC_ARM64_REG_W1,source&0xffffffff);uc.emu_start(entry,stop,count=2000)
 assert uc.reg_read(a.UC_ARM64_REG_PC)==stop and 'rounded' in result,'native failed bounded return'
 if not math.isfinite(result['pre_round_f32']) or not -(1<<31)<=round(result['pre_round_f32'])<1<<31:raise ValueError('outside finite Int32 result fixture')
 result['calls']=trace;return result
