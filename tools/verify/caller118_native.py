"""Full original caller on a declared current-only/no-pose branch, not full Animator playback."""
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_TPIDR_EL0,UC_ARM64_REG_SP
from tools.verify.context117_native import ContextFixture

class StackCheckFailure(RuntimeError):pass

def combine(a,b):return {k:a.get(k,[])+b.get(k,[]) for k in ('windows','cells','strings','relocations','imports')}

class CallerFixture(ContextFixture):
    def __init__(self,a,b,c,d,base=0x3000000,stack_prefill=0,**kwargs):
        super().__init__(a,b,combine(c,d),base=base,**kwargs)
        self.context=base+0x1eea0;self.rig=base+0x1a000;self.frame=base+0x1b000;self.frame_holder=base+0x1c000;self.pose=base+0x1d000;self.tls=base+0x60000
        self.put(base+0x1e000,bytes([stack_prefill])*0x1000,False)
        self.put(self.rig,bytes(0x90),False);self.put(self.frame,bytes(32),False);self.sq(self.frame_holder,self.frame)
        self.put(self.pose,bytes([0xa5])*0x150,False);self.sq(self.frame+16,self.pose)
        self.put(self.parameters+0x28,b'\0\0',False);self.put(self.parameters,b'\0',False)
        self.put(self.tls,bytes(0x100),False);self.sq(self.tls+0x28,0x1122334455667788);self.u.reg_write(UC_ARM64_REG_TPIDR_EL0,self.tls)
        self.failure_calls=[]
        # Original PLT -> exact ELF symbol. Failure sink throws; it never returns fake success.
        plt=0x109acc0;w0,w1,_,w3=struct.unpack('<4I',self.source(plt,16));assert w0&0x9f00001f==0x90000010 and w1&0xffc003ff==0xf9400211 and w3==0xd61f0220
        imm=((w0>>5)&0x7ffff)<<2|((w0>>29)&3);imm=imm-(1<<21) if imm&(1<<20) else imm;slot=(plt&~4095)+(imm<<12)+((w1>>10)&4095)*8
        assert {r['name'] for r in d['imports'] if r['address']==slot}=={'__stack_chk_fail'}
        sink=base+0x12030;self.sq(slot,sink);self.put(sink,b'\0'*4,False)
        def fail(f):
            self.failure_calls.append(dict(symbol='__stack_chk_fail'));raise StackCheckFailure('original stack-canary failure path reached; no successful return')
        self.sinks[sink]=fail;self.failure_binding=dict(plt=plt,slot=slot,symbol='__stack_chk_fail')
    def run_full(self,missing_blob=False,flag=0,corrupt_canary=False):
        # Scope is enforced, not silently forcing unsupported previous/pose paths.
        if any(bytes(self.u.mem_read(self.parameters+a,1))[0] for a in (0,0x28,0x29)) or any(bytes(self.u.mem_read(self.rig+a,1))[0] for a in (0x80,0x82)):
            raise ValueError('only declared current-only/no-pose flag domain supported')
        self.sq(self.node+0x118,0 if missing_blob else self.blob);self.put(self.node+0x1f3,bytes([flag]),False);self.calls=[];self.failure_calls=[]
        hook=None
        if corrupt_canary:
            def corrupt(u,pc,size,data):
                if pc==0x6d3e84:self.sq(self.tls+0x28,0x8877665544332211)
            hook=self.u.hook_add(UC_HOOK_CODE,corrupt)
        try:run=self.call(0x6d38bc,(self.node,self.rig,self.parameters,self.frame_holder))
        finally:
            if hook is not None:self.u.hook_del(hook)
        pcs=run['executed_addresses'];words=list(struct.unpack('<'+'I'*self.count,self.u.mem_read(self.output,self.count*4)))
        return dict(entry=0x6d38bc,return_pc=self.stop,last_native_pc=self.visits[-1],stack_pointer_after=self.u.reg_read(UC_ARM64_REG_SP),missing_blob=missing_blob,context=self.snapshot() if 0x6d3744 in pcs else None,output_bits=words,phase_bits=self.w(self.node+0x170),frame_flag=bytes(self.u.mem_read(self.frame+24,1))[0],pose_bytes_hex=bytes(self.u.mem_read(self.pose,0x150)).hex(),sample_time_bits=self.w(self.cache+12) if 0x6df310 in pcs else None,external_calls=list(self.calls),stack_failure_calls=list(self.failure_calls),run=run,scope='Entire original FDE entry-to-RET on prepared current-only/no-pose flag domain, or null-blob fallback. Synthetic node/rig flags/TLS/containers; no manual PC intervals, but NOT full Animator/scheduler/pose/previous/blend/application/readback/render.')
