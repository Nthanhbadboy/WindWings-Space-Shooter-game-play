"""Native context producer and staged original caller; prepared nodes are NOT observed Animator state."""
import struct
from unicorn.arm64_const import UC_ARM64_REG_X19,UC_ARM64_REG_X20
from tools.verify.cliptime116_native import ClipFixture
from tools.verify.interpolation114_native import bits,floatbits,f32

def augmented(raw115,raw117):
    return {k:raw115.get(k,[])+raw117.get(k,[]) for k in ('windows','cells','strings','relocations','imports')}

class ContextFixture(ClipFixture):
    def __init__(self,raw115,raw116,raw117,**kwargs):
        super().__init__(augmented(raw115,raw117),raw116,**kwargs)
        self.node=self.base+0x16000;self.native_clip=self.base+0x18000;self.parameters=self.base+0x19000;self.context=self.base+0x1f1a0;self.holder=self.base+0xd000
        # Original constructor's vptr value and original RELA slot+A8, not a duration service sink.
        self.sq(self.native_clip,0x10c3fa8);self.sq(self.native_clip+0x1e0,self.blob);self.sq(self.node+0x1d0,self.native_clip);self.sq(self.node+0x118,self.blob)
        self.sq(self.node+0x128,self.cache);self.sq(self.node+0x130,self.holder);self.sq(self.holder,self.output)
        assert self.q(0x10c4050)==0xb6bf94
        self.configure_node()
    def configure_node(self,current=0,previous=0,direction=1,offset=0,quantization=-1,loop=True,node_flag=0,parameter_flag=0,secondary_flag=0):
        for a,v in ((self.node+0x60,current),(self.node+0x178,previous)):self.put(a,struct.pack('<d',v),False)
        for a,v in ((self.node+0x184,direction),(self.node+0x18c,offset),(self.node+0x1fc,quantization)):self.sw(a,bits(f32(v)))
        for a,v in ((self.node+0x188,node_flag),(self.parameters+0x29,parameter_flag),(self.node+0x1f1,secondary_flag),(self.node+0x19d,int(loop))):self.put(a,bytes([v]),False)
    def snapshot(self):
        return dict(current_bits=self.w(self.context),previous_bits=self.w(self.context+4),direction_bits=self.w(self.context+8),offset_bits=self.w(self.context+16),quantization_bits=self.w(self.context+24),node_flag=bytes(self.u.mem_read(self.context+12,1))[0],parameter_flag=bytes(self.u.mem_read(self.context+20,1))[0],secondary_flag=bytes(self.u.mem_read(self.context+21,1))[0])
    def acquire(self,prefill=0xa5):
        self.calls=[];self.put(self.context,bytes([prefill])*28,False);run=self.call(0x6d3744,(self.node,self.parameters,self.context))
        return dict(context=self.snapshot(),external_calls=list(self.calls),run=run,scope='Complete original context writer + original class74 vtable duration getter; prepared native node/clip, NOT runtime node creation or live Animator context')
    def stage(self,entry,stop):
        old=self.stop;self.stop=stop
        try:return self.call(entry)
        finally:self.stop=old
    def staged_sample(self):
        self.calls=[];self.u.reg_write(UC_ARM64_REG_X19,self.node);self.u.reg_write(UC_ARM64_REG_X20,self.parameters)
        # Each interval is an explicit manual entry/stop in the original caller, NOT a full caller execution.
        ranges=((0x6d3924,0x6d3960),(0x6d39bc,0x6d39c0),(0x6d3a20,0x6d3a48));runs=[self.stage(a,b) for a,b in ranges]
        words=list(struct.unpack('<'+'I'*self.count,self.u.mem_read(self.output,self.count*4)))
        return dict(context=self.snapshot(),output_bits=words,sample_time_bits=self.w(self.cache+12),stored_phase_bits=self.w(self.node+0x170),external_calls=list(self.calls),stages=[dict(entry=a,stop_before=b,run=r) for (a,b),r in zip(ranges,runs)],instruction_count=sum(r['instruction_count'] for r in runs),scope='Staged original caller intervals: native node/blob selection + context writer, native cache/output pointer loads, native context-to-time-to-stream call and phase store. Excludes intervening previous-time branch, full caller/TLS, conversions, scheduling, blending and application.')
