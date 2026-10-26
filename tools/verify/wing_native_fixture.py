"""Finite execution of APK SetBarrels bytes under Unicorn2.1.4, FPCR=0.

Only named dependency adapters below. No Unity loop, native save state, firing,
collision simulation or observed cadence. Inputs are explicit, not prefab defaults.
"""
import gzip,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_PC,UC_ARM64_REG_SP,UC_ARM64_REG_LR,UC_ARM64_REG_FPCR,UC_ARM64_REG_CPACR_EL1,UC_ARM64_REG_X0,UC_ARM64_REG_X1
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/wing-implementations/method-bytes.json.gz'
SELF=0x1000100;PLAYER=0x1001000;ARRAY=0x1002000;STOP=0x5000000

class NativeFault(Exception):pass

class SetBarrelsFixture:
    def __init__(self,implementation,field_map):
        self.fields=field_map;self.names={v['name']:int(k,16) if isinstance(k,str) else k for k,v in field_map.items()}
        payload=json.load(gzip.open(RAW));self.method=next(x for x in payload['methods'] if x['cls']==implementation and x['method']=='SetBarrels')
        self.vm=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
        for a,n in ((0x1000000,0x510000),(0x1bd7000,0x1000),(0x2ad0000,0x240000),(0x750000,0x30000),(0x4000000,0x10000),(STOP,0x1000)):
            self.vm.mem_map(a,n)
        self.vm.mem_write(int(self.method['va'],16),bytes.fromhex(self.method['hex']))
        for x in payload['pool']:self.vm.mem_write(int(x['va'],16),bytes.fromhex(x['hex']))
        # Class flags/GOT/data placeholders only; no game or metadata initializer runs.
        rel=payload['relocations']
        for x in rel:
            at=int(x['offset'],16);target=int(x['addend'],16)
            if 0x2ad0000<=at<0x2d10000 and 0x2ad0000<=target<0x2d10000:
                self.vm.mem_write(at,struct.pack('<Q',target));self.vm.mem_write(target,struct.pack('<Q',target))
        self.trace=[];self.hooks={0x110d028:self.noop,0x14793cc:self.get_player,0x14b1eb0:self.get_level,0x1bd7b94:self.list_item,0x110d250:self.null_fault,0x110d258:self.bounds_fault}
        self.vm.hook_add(UC_HOOK_CODE,self.hook)
    def noop(self):pass
    def get_player(self):self.vm.reg_write(UC_ARM64_REG_X0,PLAYER if self.has_player else 0)
    def get_level(self):
        value=next(self.levels);self.trace.append(value);self.vm.reg_write(UC_ARM64_REG_X0,value&0xffffffff)
    def list_item(self):
        i=self.vm.reg_read(UC_ARM64_REG_X1)&0xffffffff
        if i>=self.length:raise NativeFault('bounds')
        self.list_index=i;self.vm.reg_write(UC_ARM64_REG_X0,0x1003000+32*i)
    def null_fault(self):raise NativeFault('null')
    def bounds_fault(self):raise NativeFault('bounds')
    def hook(self,vm,address,size,_):
        if address in self.hooks:
            self.hooks[address]();vm.reg_write(UC_ARM64_REG_PC,vm.reg_read(UC_ARM64_REG_LR))
    def put(self,name,value):
        if name in self.names:self.vm.mem_write(SELF+self.names[name],struct.pack('<f',value))
    def get(self,name):return struct.unpack('<f',self.vm.mem_read(SELF+self.names[name],4))[0]
    def run(self,level=0,*,super_mode=False,start_rate=1.,start_speed=10.,numbers=tuple(range(100,110)),has_player=True,levels=None):
        vm=self.vm;self.has_player=has_player;self.levels=iter(levels if levels is not None else [level]*16);self.trace=[];self.list_index=None;self.length=len(numbers)
        vm.mem_write(SELF,b'\0'*0x400);vm.mem_write(PLAYER,b'\0'*0x100);vm.mem_write(PLAYER+0x2a,bytes([super_mode]))
        vm.mem_write(ARRAY,b'\0'*0x100);vm.mem_write(ARRAY+0x18,struct.pack('<I',len(numbers)))
        if numbers:vm.mem_write(ARRAY+0x20,struct.pack('<'+'i'*len(numbers),*numbers))
        if 'allNumberBullets' in self.names:vm.mem_write(SELF+self.names['allNumberBullets'],struct.pack('<Q',ARRAY))
        if 'listAllBarrels' in self.names:vm.mem_write(SELF+self.names['listAllBarrels'],struct.pack('<Q',ARRAY))
        for name,value in [('startShotRate',start_rate),('startBltSpeed',start_speed),('shotRate',-7.),('btlSpeed',-8.),('angleDelta',-9.)]:self.put(name,value)
        vm.reg_write(UC_ARM64_REG_X0,SELF);vm.reg_write(UC_ARM64_REG_SP,0x400f000);vm.reg_write(UC_ARM64_REG_LR,STOP)
        vm.reg_write(UC_ARM64_REG_CPACR_EL1,3<<20);vm.reg_write(UC_ARM64_REG_FPCR,0)
        vm.emu_start(int(self.method['va'],16),STOP,count=10000)
        assert vm.reg_read(UC_ARM64_REG_PC)==STOP,'fixture instruction budget reached'
        result={name:self.get(name) for name in ('shotRate','btlSpeed','angleDelta') if name in self.names}
        if 'numberNormal' in self.names:result['numberNormal']=struct.unpack('<i',vm.mem_read(SELF+self.names['numberNormal'],4))[0]
        if self.list_index is not None:result['barrel_list_index']=self.list_index
        result['level_reads']=self.trace[:];return result
