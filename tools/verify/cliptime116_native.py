"""Original clip-time/dense/aggregate functions with explicit ELF import bridges; NOT Unity playback."""
import math,struct
from unicorn.arm64_const import UC_ARM64_REG_S0,UC_ARM64_REG_S1,UC_ARM64_REG_S2,UC_ARM64_REG_S3,UC_ARM64_REG_S4,UC_ARM64_REG_S5,UC_ARM64_REG_X4
from tools.verify.tag23_113_native import Fixture
from tools.verify.interpolation114_native import bits,floatbits,f32
SREGS=(UC_ARM64_REG_S0,UC_ARM64_REG_S1,UC_ARM64_REG_S2,UC_ARM64_REG_S3,UC_ARM64_REG_S4,UC_ARM64_REG_S5)

def merge_raw(*raws):
    return dict(windows=[w for r in raws for w in r['windows']],native_slices=[w for r in raws for w in r['cells']],strings=[s for r in raws for s in r['strings']],relocations=[x for r in raws for x in r['relocations']])

class ClipFixture(Fixture):
    def __init__(self,raw115,raw116,packed=b'',continuous=0,discrete=0,dense=None,constant=(),base=0x3000000,prefill=0xa5,bridge=True):
        super().__init__(merge_raw(raw115,raw116),base);self.raws=(raw115,raw116);self.clip=base+0x4000;self.cache=base+0x5000;self.output=base+0x6000;self.records=base+0x7000;self.blob=base+0x10000;self.context=base+0xe000;self.calls=[];self.allocations=[];self.bindings=[]
        dense=dense or dict(frames=0,curves=0,rate=0,begin=0,samples=[])
        if not 0<=continuous<=65535 or not 0<=discrete<=65535:raise ValueError('native u16 counts required')
        if len(packed)%4 or ((continuous+discrete)>0 and not packed):raise ValueError('stream words required for nonzero counts')
        if dense['curves'] and (dense['frames']<1 or len(dense['samples'])!=dense['frames']*dense['curves']):raise ValueError('dense frame-major sample coverage required')
        self.stream_count=continuous+discrete
        self.count=continuous+discrete+dense['curves']+len(constant)
        if not 0<self.count<=256:raise ValueError('bounded nonempty fixture channels')
        self.sw(self.clip,len(packed)//4);self.put(self.clip+16,struct.pack('<HH',continuous,discrete),False)
        if packed:
            pointer=base+0x30000;self.put(pointer,packed,False);self.sq(self.clip+8,pointer-(self.clip+8))
        self.put(self.clip+24,struct.pack('<IIffI',dense['frames'],dense['curves'],dense['rate'],dense['begin'],len(dense['samples'])),False)
        if dense['samples']:
            pointer=base+0x40000;self.put(pointer,struct.pack('<'+'f'*len(dense['samples']),*dense['samples']),False);self.sq(self.clip+48,pointer-(self.clip+48))
        self.sw(self.clip+56,len(constant))
        if constant:
            pointer=base+0x50000;self.put(pointer,struct.pack('<'+'I'*len(constant),*constant),False);self.sq(self.clip+64,pointer-(self.clip+64))
        self.put(self.cache,bytes([prefill])*32,False);self.put(self.records,bytes([prefill])*(continuous+discrete)*20,False);self.put(self.output,bytes([prefill])*self.count*4,False)
        allocator=base+0x9000;vtable=base+0xa000;sink=base+0xb000;self.sq(allocator,vtable);self.sq(vtable,sink);self.put(sink,b'\0'*4,False)
        def allocate(f):
            size,alignment=f.reg(1),f.reg(2);index=len(self.allocations);self.allocations.append(dict(size=size,alignment=alignment))
            assert (size,alignment)==((32,8) if index==0 else ((continuous+discrete)*20,4))
            f.ret(self.cache if index==0 else self.records)
        self.sinks[sink]=allocate;self.initialization=self.call(0x6deefc,(self.clip,allocator));assert self.reg(0)==self.cache;self.sinks.clear()
        self.initialized_cache_hex=bytes(self.u.mem_read(self.cache,28)).hex()
        self.sq(self.blob+0x5f0,(self.clip-(self.blob+0x5f0))&0xffffffffffffffff)
        self.configure_time()
        if bridge:self.enable_imports()
    def configure_time(self,start=0,stop=1,cycle_offset=0,context_offset=0,direction=1,quantization_rate=0):
        for a,v in [(self.blob+0x5f8,start),(self.blob+0x5fc,stop),(self.blob+0x608,cycle_offset),(self.context+8,direction),(self.context+16,context_offset),(self.context+24,quantization_rate)]:self.sw(a,bits(f32(v)))
    def single(self,reg=UC_ARM64_REG_S0):return floatbits(self.u.reg_read(reg))
    def enable_imports(self):
        for i,(plt,symbol) in enumerate(((0x109b800,'modff'),(0x109acd0,'memcpy'))):
            w0,w1,_,w3=struct.unpack('<4I',self.source(plt,16));assert w0&0x9f00001f==0x90000010 and w1&0xffc003ff==0xf9400211 and w3==0xd61f0220
            immediate=((w0>>5)&0x7ffff)<<2|((w0>>29)&3);immediate=immediate-(1<<21) if immediate&(1<<20) else immediate
            slot=(plt&~4095)+(immediate<<12)+((w1>>10)&4095)*8
            names={r['name'] for raw in self.raws for r in raw['imports'] if r['address']==slot};assert names=={symbol},(slot,names)
            sink=self.base+0x12000+i*16;self.sq(slot,sink);self.put(sink,b'\0'*4,False)
            def imported(f,symbol=symbol):
                if symbol=='modff':
                    value=f.single();fraction,integer=math.modf(value);target=f.reg(0);f.sw(target,bits(f32(integer)));f.u.reg_write(UC_ARM64_REG_S0,bits(f32(fraction)));f.calls.append(dict(symbol=symbol,input_bits=bits(value),fraction_bits=bits(f32(fraction)),integer_bits=bits(f32(integer))))
                else:
                    dest,source,length=f.reg(0),f.reg(1),f.reg(2);assert 0<=length<=self.count*4 and self.output<=dest and dest+length<=self.output+self.count*4
                    f.guard(f.u,0,source,length,0,None);f.put(dest,bytes(f.u.mem_read(source,length)),False);f.calls.append(dict(symbol=symbol,bytes=length));f.ret(dest);return
                f.ret()
            self.sinks[sink]=imported;self.bindings.append(dict(plt=plt,slot=slot,symbol=symbol))
        return self.bindings
    def helper(self,time,start=0,stop=1,offset=0,direction=1,quantization_rate=0,loop=True):
        self.calls=[];phase=self.base+0xc000;cycles=phase+4
        for reg,value in zip(SREGS,(time,start,stop,offset,direction,quantization_rate)):self.u.reg_write(reg,bits(f32(value)))
        run=self.call(0xb93158,(int(loop),phase,cycles))
        return dict(sample_time=self.single(),sample_time_bits=self.u.reg_read(UC_ARM64_REG_S0),phase=floatbits(self.w(phase)),phase_bits=self.w(phase),cycles=floatbits(self.w(cycles)),cycles_bits=self.w(cycles),external_calls=list(self.calls),run=run)
    def sample(self,time,through_time=False,loop=True):
        if not math.isfinite(time):raise ValueError('finite fixture query required')
        self.calls=[];self.u.reg_write(UC_ARM64_REG_S0,bits(f32(time)));holder=self.base+0xd000;self.sq(holder,self.output)
        if through_time:
            self.u.reg_write(UC_ARM64_REG_X4,int(loop));run=self.call(0x6d2e94,(self.blob,self.context,self.cache,holder));returned_phase=self.single()
        else:
            clock=self.base+0xc000;self.sw(clock,bits(f32(time)));run=self.call(0x6df270,(self.clip,clock,self.cache,holder));returned_phase=None
        words=list(struct.unpack('<'+'I'*self.count,self.u.mem_read(self.output,self.count*4)))
        return dict(query=f32(time),through_time=through_time,returned_phase=returned_phase,stream_last_time=floatbits(self.w(self.cache+12)) if self.stream_count else None,stream_last_time_bits=self.w(self.cache+12),output_bits=words,external_calls=list(self.calls),run=run)
