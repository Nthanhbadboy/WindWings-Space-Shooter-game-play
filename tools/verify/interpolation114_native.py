"""Execute original curve code; synthetic native layouts are NOT Unity readback.
Arithmetic/key search/cache writes execute natively. Platform-math bridging is opt-in.
"""
import math,struct
from tools.verify.tag23_113_native import Fixture
from unicorn.arm64_const import UC_ARM64_REG_S0,UC_ARM64_REG_S1,UC_ARM64_REG_D0,UC_ARM64_REG_D1,UC_ARM64_REG_X20

def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
def floatbits(v):return struct.unpack('<f',struct.pack('<I',v))[0]
def key(time,value,in_slope=0,out_slope=0,weighted_mode=0,in_weight=1/3,out_weight=1/3):
    return dict(time=f32(time),value=f32(value),inSlope=f32(in_slope),outSlope=f32(out_slope),weightedMode=weighted_mode,inWeight=f32(in_weight),outWeight=f32(out_weight))

class CurveFixture(Fixture):
    def __init__(self,raw,keys,pre=2,post=2,base=0x3000000):
        adapted=dict(windows=raw['windows'],native_slices=raw['cells'],strings=raw['strings'],pointed_strings=[],relocations=raw['relocations'])
        super().__init__(adapted,base);self.raw=raw;self.curve=base+0x4000;self.keys=base+0x5000;self.math_calls=[]
        assert len(keys)<=100,'fixture key budget'
        for i,k in enumerate(keys):self.put(self.keys+i*28,struct.pack('<4fI2f',k['time'],k['value'],k['inSlope'],k['outSlope'],k['weightedMode'],k['inWeight'],k['outWeight']),False)
        self.sq(self.curve+0x38,self.keys);self.sq(self.curve+0x48,len(keys));self.sw(self.curve+0x58,pre);self.sw(self.curve+0x5c,post);self.invalidate()
    def invalidate(self):self.sw(self.curve,0xffffffff);self.sw(self.curve+4,bits(math.inf));self.sw(self.curve+8,bits(-math.inf))
    def single(self,reg=UC_ARM64_REG_S0):return floatbits(self.u.reg_read(reg))
    def double(self,reg=UC_ARM64_REG_D0):return struct.unpack('<d',struct.pack('<Q',self.u.reg_read(reg)))[0]
    def floating_call(self,entry,time,args):
        self.u.reg_write(UC_ARM64_REG_S0,bits(f32(time)));run=self.call(entry,args);value=self.single()
        return dict(value=value,value_bits=bits(value),**{k:v for k,v in run.items() if k!='return_value'})
    def evaluate(self,time,external_cache=False):
        cache=self.base+0x6000 if external_cache else self.curve
        if external_cache:
            self.sw(cache,0xffffffff);self.sw(cache+4,bits(math.inf));self.sw(cache+8,bits(-math.inf))
        r=self.floating_call(0x952608,time,(self.curve,cache if external_cache else 0))
        data=bytes(self.u.mem_read(cache,28));index,*values=struct.unpack('<i6f',data)
        return dict(time=f32(time),cache=dict(index=index,start=values[0],end=values[1],coefficients=values[2:],hex=data.hex()),math_import_calls=list(self.math_calls),**r)
    def segment(self,time,left=0,right=1):return self.floating_call(0x951344,time,(self.keys+28*left,self.keys+28*right))
    def api(self,time):
        # Original wrapper resolves a managed handle through an external bridge function.
        bridge=next(r['addend'] for r in self.raw['relocations'] if r['address']==0x10e18a8)
        holder=self.base+0x7000;sink=self.base+0x8000;calls=[];self.sq(bridge,sink);self.sq(holder+16,self.curve)
        def resolve(f):calls.append(dict(handle=f.reg(2)));f.sq(f.reg(1),holder);f.ret()
        self.sinks[sink]=resolve
        r=self.floating_call(0x36e71c,time,(holder,));r['managed_bridge_calls']=calls;return r
    def enable_host_math(self):
        """Bind only named ELF imports. Host libm is NOT Android-libm parity."""
        bindings=[]
        for i,entry in enumerate((0x109aeb0,0x109ae90,0x109bbc0,0x109b830)):
            w0,w1,w2,w3=struct.unpack('<4I',self.source(entry,16));assert w0&0x9f00001f==0x90000010 and w1&0xffc003ff==0xf9400211 and w3==0xd61f0220
            imm=((w0>>5)&0x7ffff)<<2|((w0>>29)&3);imm=imm-(1<<21) if imm&(1<<20) else imm
            slot=(entry&~4095)+(imm<<12)+((w1>>10)&4095)*8
            name=next(r['name'] for r in self.raw['imports'] if r['address']==slot)
            assert name in ('atan2f','logf','exp','cosf'),name
            sink=self.base+0x12000+i*16;self.sq(slot,sink)
            def call(f,name=name):
                args=[f.double()] if name=='exp' else [f.single()]+([f.single(UC_ARM64_REG_S1)] if name=='atan2f' else [])
                fn={'atan2f':math.atan2,'logf':math.log,'exp':math.exp,'cosf':math.cos}[name];value=fn(*args)
                if name=='exp':f.u.reg_write(UC_ARM64_REG_D0,struct.unpack('<Q',struct.pack('<d',value))[0])
                else:f.u.reg_write(UC_ARM64_REG_S0,bits(value));value=f32(value)
                f.math_calls.append(dict(symbol=name,args=args,value=value));f.ret()
            self.sinks[sink]=call;bindings.append(dict(plt=entry,slot=slot,symbol=name))
        return bindings
    def produce_records(self,curve_index=0):
        vector=self.base+0x15000;buffer=self.base+0x16000
        self.sq(vector,buffer);self.sq(vector+16,0);self.sq(vector+24,512)
        run=self.call(0x6c4480,(vector,curve_index,self.curve));count=self.q(vector+16);assert count<=101
        data=bytes(self.u.mem_read(buffer,count*24));records=[]
        for i in range(count):
            time,index,*coeff=struct.unpack_from('<fI4f',data,i*24);records.append(dict(time=time,index=index,coeff=coeff,hex=data[i*24:i*24+24].hex()))
        return dict(records=records,record_count=count,native_bytes_hex=data.hex(),run=run,scope='Original curve-to-time/index/four-coefficient records, native vector stores, prepared capacity; not final compressed stream serialization or Animator consumer')
    def pack_prepared_records(self,prefill=0):
        # Manual entry after sort/reserve; execute only original grouping/stores.
        vector=self.base+0x15000;buffer=self.base+0x17000;sp=self.base+0x1f000
        self.put(buffer,bytes([prefill])*4096,False);self.sq(sp,buffer);self.sq(sp+16,0);self.sq(sp+24,8192)
        self.u.reg_write(UC_ARM64_REG_X20,vector);old_stop=self.stop;self.stop=0x6c4c40
        try:run=self.call(0x6c4b8c)
        finally:self.stop=old_stop
        length=self.q(sp+16);assert length<=4096
        return dict(entry=0x6c4b8c,stop_before=0x6c4c40,bytes_hex=bytes(self.u.mem_read(buffer,length)).hex(),byte_count=length,run=run,scope='Original sorted-record grouping and frame/key stores only; manual entry with preallocated byte-vector, excludes sort, final sentinel, allocator/copy/destructor suffix')
