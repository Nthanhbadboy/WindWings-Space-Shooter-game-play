"""Original packed StreamedClip selector/evaluator in prepared native memory, not Unity playback."""
import math,struct
from tools.verify.tag23_113_native import Fixture
from tools.verify.interpolation114_native import bits,floatbits,f32
from unicorn.arm64_const import UC_ARM64_REG_S0

class PackedFixture(Fixture):
    def __init__(self,raw,data,continuous,discrete=0,base=0x3000000,prefill=0xa5):
        if not data or len(data)%4:raise ValueError('word-aligned nonempty packed input required')
        if not 0<=continuous<=65535 or not 0<=discrete<=65535 or not continuous+discrete:raise ValueError('nonempty native u16 channel counts required')
        super().__init__(dict(windows=raw['windows'],native_slices=raw['cells'],strings=raw['strings'],relocations=raw['relocations']),base)
        self.clip=base+0x4000;self.cache=base+0x5000;self.output=base+0x6000;self.records=base+0x7000;self.data=base+0x30000;self.count=continuous+discrete;self.allocator_calls=[]
        if self.count>256:raise ValueError('bounded fixture channel capacity')
        self.put(self.data,data,False);self.sw(self.clip,len(data)//4);self.sq(self.clip+8,self.data-(self.clip+8));self.put(self.clip+16,struct.pack('<HH',continuous,discrete),False)
        self.put(self.records,bytes([prefill])*self.count*20,False);self.put(self.output,bytes([prefill])*self.count*4,False)
        # Original initializer performs all record clearing/count writes; only allocation is external.
        allocator=base+0x9000;vtable=base+0xa000;sink=base+0xb000
        self.sq(allocator,vtable);self.sq(vtable,sink);self.put(sink,b'\0'*4,False)
        def allocate(f):
            self.allocator_calls.append(dict(size=f.reg(1),alignment=f.reg(2)))
            assert f.reg(1)==self.count*20 and f.reg(2)==4
            f.ret(self.records)
        self.sinks[sink]=allocate;self.initialization=self.call(0x6df02c,(self.clip,self.cache,allocator));self.sinks.clear()
        self.initialized_hex=bytes(self.u.mem_read(self.records,self.count*20)).hex()
    def sample(self,time,aggregate=False):
        if not math.isfinite(time) or not math.isfinite(f32(time)):raise ValueError('finite f32 sample times only; no engine endpoint policy supplied')
        t=f32(time);self.u.reg_write(UC_ARM64_REG_S0,bits(t))
        if aggregate:
            clock=self.base+0xc000;holder=self.base+0xd000;self.sw(clock,bits(t));self.sq(holder,self.output)
            run=self.call(0x6df270,(self.clip,clock,self.cache,holder))
        else:run=self.call(0x6df310,(self.clip,self.cache,self.output))
        data=bytes(self.u.mem_read(self.output,self.count*4));words=list(struct.unpack('<'+'I'*self.count,data));cache=[]
        for i in range(self.count):
            b=bytes(self.u.mem_read(self.records+i*20,20));cache.append(dict(channel=i,time_bits=struct.unpack_from('<I',b)[0],coeff_bits=list(struct.unpack_from('<4I',b,4))))
        return dict(time=t,entry=0x6df270 if aggregate else 0x6df310,output_bits=words,continuous_values=[floatbits(w) for w in words[:struct.unpack('<H',self.u.mem_read(self.cache+8,2))[0]]],cache=cache,last_time_bits=self.w(self.cache+12),next_frame_byte_offset=self.w(self.cache+16),run=run,external_calls=[],scope='Original packed bytes -> native frame/channel selection -> native scalar/SIMD cubic or discrete DWORD copy; prepared ClipConstant/cache/output, NOT Unity playback/Animator blend/application/readback/render')

def frame(time,keys):
    """Synthetic test framing only. Keys carry exact four coefficient DWORDs."""
    return struct.pack('<fI',time,len(keys))+b''.join(struct.pack('<I4I',index,*coeff) for index,coeff in keys)
