"""Provisional original parent execution and second-phase guard audit, NOT pose application."""
import argparse,gzip,json,hashlib,struct
from pathlib import Path
from tools.verify import caller118,packed115
from tools.verify.caller118_native import CallerFixture,combine
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/caller119/probe.json.gz'
OUT=ROOT/'datas/l3_ef6b75ef119_native_parent_guards.json.gz'
class ParentFixture(CallerFixture):
    def __init__(self,*args,raw119,**kw):
        a,b,c,d=args
        super().__init__(a,b,c,combine(d,raw119),**kw)
        self.descriptor=self.base+0x62000
        self.put(self.descriptor,bytes(16),False);self.sq(self.parameters+0x10,self.descriptor)
    def parent(self,missing=False,mode=0):
        self.sq(self.node+0x118,0 if missing else self.blob);self.sw(self.descriptor+4,mode&0xffffffff)
        if any(bytes(self.u.mem_read(self.parameters+i,1))[0] for i in (0,0x28,0x29)) or any(bytes(self.u.mem_read(self.rig+i,1))[0] for i in (0x80,0x82)):
            raise ValueError('parent execution restricted to declared no-pose domain')
        self.context=self.base+0x1ee70;self.calls=[]
        run=self.call(0x6d46a8,(self.node,self.rig,self.parameters,self.frame_holder))
        return dict(run=run,last_native_pc=self.visits[-1],context=self.snapshot() if not missing else None,output_bits=list(struct.unpack('<'+'I'*self.count,self.u.mem_read(self.output,self.count*4))),phase_bits=self.w(self.node+0x170),completion_byte=bytes(self.u.mem_read(self.node+0x174,1))[0],external_calls=list(self.calls),pose_hex=bytes(self.u.mem_read(self.pose,0x150)).hex())
    def second_guard(self,missing=False,mode=0,flag=0):
        if not missing and mode!=-1 and flag:raise ValueError('active second-phase domain requires unvalidated rig/state; not executed')
        self.sq(self.node+0x118,0 if missing else self.blob);self.sw(self.descriptor+4,mode&0xffffffff);self.put(self.parameters+0x28,bytes([flag]),False);self.calls=[]
        before=bytes(self.u.mem_read(self.pose,0x150));run=self.call(0x6d3ebc,(self.node,self.rig,self.parameters,self.frame_holder))
        assert before==bytes(self.u.mem_read(self.pose,0x150)) and not self.calls
        return dict(run=run,last_native_pc=self.visits[-1],external_calls=self.calls,output_unchanged=True)
def raws():return caller118.raws(),json.load(gzip.open(RAW))
def fixture(source=False,**kw):
    args,r=raws()
    if source:
        row,s,data=packed115.source_stream();return ParentFixture(*args,raw119=r,packed=data,continuous=s['curveCount'],discrete=s['discreteCurveCount'],**kw),row,s,data
    return ParentFixture(*args,raw119=r,packed=packed115.synthetic_stream(),continuous=1,**kw)
def build():
    old=json.load(gzip.open(caller118.OUT));f,row,s,data=fixture(True);m=row['tree']['m_MuscleClip'];f.configure_time(start=m['m_StartTime'],stop=m['m_StopTime'],cycle_offset=m['m_CycleOffset']);results=[]
    for previous in old['source']['runs']:
        f.configure_node(current=previous['node_seconds_double'],loop=m['m_LoopTime']);r=f.parent();assert r['output_bits']==previous['native']['output_bits'] and r['context']==previous['native']['context'] and r['phase_bits']==previous['native']['phase_bits'];assert r['completion_byte']==1 and r['last_native_pc']==0x6d46f0;results.append(dict(query=previous['query'],native=r))
    guards=[]
    for missing,mode,flag in [(True,0,1),(False,-1,1),(False,0,0)]:guards.append(dict(input=dict(missing=missing,mode=mode,flag=flag),native=fixture().second_guard(missing,mode,flag)))
    null=fixture().parent(missing=True)
    paths=[RAW,caller118.RAW,caller118.OUT,ROOT/'tools/verify/parent119.py',ROOT/'tools/recovery/caller119.py',ROOT/'tests/test_parent119.py']
    return dict(provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},source=results,guards=guards,null_parent=null,counts=dict(source_calls=len(results),source_dwords=sum(len(x['native']['output_bits']) for x in results),source_native_instructions=sum(x['native']['run']['instruction_count'] for x in results),guard_cases=len(guards)),scope='Original parent entry-to-RET plus full second-phase early-return guards. Prepared descriptor/flags/TLS/node; active second phase NOT executed, NOT pose/application, observed game completion or full Animator. Source comparison inherits118, not an independent extraction.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();blob=gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==blob
    else:OUT.write_bytes(blob)
    print(json.dumps(dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),counts=r['counts'])))
if __name__=='__main__':main()
