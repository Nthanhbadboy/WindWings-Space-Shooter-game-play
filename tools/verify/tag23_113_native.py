"""Guarded execution of captured ARM64 callbacks, NOT a Unity runtime.
Only allocator / external registry service sinks may be substituted by callers.
Small-string layout below follows original 946d0c instructions, not a host ABI.
"""
import struct
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2, UC_ARM64_REG_X3, UC_ARM64_REG_X30, UC_ARM64_REG_PC, UC_ARM64_REG_SP
REGS=(UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3)
class Fixture:
    def __init__(self,raw,base=0x3000000):
        self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);self.pages=set();self.original=[];self.synthetic=[];self.visits=[];self.sinks={};self.base=base;self.reads=set()
        for w in raw['windows']+raw['native_slices']+raw.get('pointed_strings',[]):self.put(w['va'],bytes.fromhex(w['hex']))
        for s in raw['strings']:
            for w in s['occurrences']:self.put(w['va'],bytes.fromhex(w['hex']))
        for r in raw['relocations']:self.put(r['address'],struct.pack('<Q',r['addend']))
        self.put(base,b'\0'*0x20000,False);self.stop=base+0x1fff0
        self.u.hook_add(UC_HOOK_MEM_READ,self.guard)
        self.u.hook_add(UC_HOOK_CODE,self.hook)
    def put(self,a,b,original=True):
        for page in range(a&~4095,(a+len(b)+4095)&~4095,4096):
            if page not in self.pages:self.u.mem_map(page,4096);self.pages.add(page)
        self.u.mem_write(a,b);(self.original if original else self.synthetic).append((a,a+len(b)))
    def source(self,a,n):
        assert any(lo<=a and a+n<=hi for lo,hi in self.original),f'uncaptured static metadata {a:x}+{n}'
        return bytes(self.u.mem_read(a,n))
    def q(self,a):return struct.unpack('<Q',self.u.mem_read(a,8))[0]
    def w(self,a):return struct.unpack('<I',self.u.mem_read(a,4))[0]
    def sq(self,a,v,original=False):self.put(a,struct.pack('<Q',v),original)
    def sw(self,a,v):self.put(a,struct.pack('<I',v&0xffffffff),False)
    def reg(self,i):return self.u.reg_read(REGS[i])
    def ret(self,v=None):
        if v is not None:self.u.reg_write(UC_ARM64_REG_X0,v)
        self.u.reg_write(UC_ARM64_REG_PC,self.u.reg_read(UC_ARM64_REG_X30))
    def guard(self,u,access,a,n,value,data):
        assert any(lo<=a and a+n<=hi for lo,hi in self.original+self.synthetic),f'uncaptured data read {a:x}+{n}'
        self.reads.add((a,n))
    def hook(self,u,pc,size,data):
        if pc==self.stop:u.emu_stop();return
        if pc in self.sinks:self.sinks[pc](self);return
        assert any(lo<=pc and pc+size<=hi for lo,hi in self.original),f'uncaptured instruction {pc:x}'
        self.visits.append(pc)
    def call(self,entry,args=()):
        self.visits=[];self.reads=set()
        for reg,arg in zip(REGS,args):self.u.reg_write(reg,arg)
        self.u.reg_write(UC_ARM64_REG_X30,self.stop);self.u.reg_write(UC_ARM64_REG_SP,self.base+0x1f000)
        self.u.emu_start(entry,self.stop+4,count=10000)
        assert self.u.reg_read(UC_ARM64_REG_PC)==self.stop,'native fixture budget exhausted'
        return dict(return_value=self.reg(0)&0xffffffff,instruction_count=len(self.visits),executed_addresses=sorted(set(self.visits)),source_reads=[dict(va=a,size=n) for a,n in sorted(self.reads) if any(lo<=a and a+n<=hi for lo,hi in self.original)])
    def smallstring(self,text,inline=True):
        b=text.encode();a=self.base+0x1000;self.put(a,b'\0'*40,False)
        if inline:
            assert len(b)<=24;self.put(a,b,False);self.put(a+24,bytes([24-len(b)]),False);self.put(a+32,b'\1',False)
        else:
            p=self.base+0x2000;self.put(p,b+b'\0',False);self.sq(a,p);self.sq(a+16,len(b))
        return a

def resolve(raw,text='m_Sprite',flags=1,inline=True,base=0x3000000):
    f=Fixture(raw,base);s=f.smallstring(text,inline);out=base+0x3000;f.put(out,b'\xa5'*16,False)
    r=f.call(0x946d0c,(0,s,flags,out));return dict(text=text,flags=flags,inline=inline,output_hex=bytes(f.u.mem_read(out,16)).hex(),**r)

def callbacks(raw,value=0x12345678,base=0x3000000):
    f=Fixture(raw,base);holder=base+0x4000;obj=base+0x5000;f.sq(holder+0x18,obj);f.sw(obj+0x1f0,value)
    read=f.call(0x946d00,(0,holder));calls=[]
    def sink(f):
        calls.append(dict(object=f.reg(0),value=f.w(f.reg(1))));f.ret()
    f.sinks[0x93b09c]=sink;write=f.call(0x946ce4,(0,holder,value))
    return dict(read=read,write=write,setter_sink_calls=calls,setter_sink=0x93b09c,scope='Native reader and writer argument routing; setter body not executed')

def registered_fixture(raw,enabled=True,base=0x3000000):
    f=Fixture(raw,base);service=base+0x6000;manager=base+0x7000;handler=base+0x8000;mapping=base+0xa000;slots=base+0xb000;alloc=[]
    f.sq(service,raw['registry_vtable']+16);f.sq(manager,mapping);f.sq(manager+16,0);f.sq(manager+24,128);f.sq(manager+32,slots)
    # File-absent BSS values and initialized, preallocated native containers are fixture inputs.
    f.sq(0x1162390,service if enabled else 0);f.sq(0x1185350,manager);f.sq(0x1199a98,0)
    def allocate(f):alloc.append(dict(size=f.reg(0),label=f.reg(1),alignment=f.reg(2)));f.ret(handler)
    f.put(0x3c9298,b'\0'*4,False);f.sinks={0x3c9298:allocate}
    run=f.call(0x940218)
    record=dict(run=run,allocator_calls=alloc,map_length=f.q(manager+16),map_type_descriptor=f.q(mapping),map_tag=f.w(mapping+8),slot_23=f.q(slots+23*8),handler=handler,handler_vtable=f.q(handler),hooks=[0x3c9298],scope='Native registry writes/readback in a synthetic initialized container, NOT Unity engine readback/bootstrap')
    f.manager=manager;f.handler=handler;f.slots=slots
    return f,record

def registration(raw,enabled=True,base=0x3000000):return registered_fixture(raw,enabled,base)[1]

def dispatch(raw,type_id=212,tag=23,value=0x12345678,base=0x3000000):
    component=type_records(raw)[0]
    f,reg=registered_fixture(raw,base=base);generic=base+0xc000;context=base+0xd000;output=base+0xe000;obj=base+0xf000;go=base+0x11000;lookups=[]
    f.sw(generic+12,type_id);f.put(generic+16,bytes([tag,1,0,0]),False);f.sq(context+48,go);f.sw(obj+0x1f0,value)
    def type_lookup(f):
        requested=f.reg(0)&0xffffffff;lookups.append(dict(kind='class_id_service',type_id=requested));f.ret(component['descriptor'] if requested==component['class_id'] else 0)
    def component_lookup(f):
        lookups.append(dict(kind='component_service',gameobject=f.reg(0),descriptor=f.reg(1)));f.ret(obj if f.reg(0)==go and f.reg(1)==component['descriptor'] else 0)
    for a in (0x3d5670,0x3dfa9c):f.put(a,b'\0'*4,False)
    f.sinks.update({0x3d5670:type_lookup,0x3dfa9c:component_lookup})
    selected=f.call(0x6a9674,(f.manager,generic,context,output));read=None;write=None;calls=[]
    if selected['return_value']:
        read=f.call(0x6a9898,(output,))
        def sink(f):calls.append(dict(object=f.reg(0),value=f.w(f.reg(1))));f.ret()
        f.sinks[0x93b09c]=sink;write=f.call(0x6a98c4,(output,value))
    return dict(registration=reg,lookup=selected,output=dict(attribute=f.w(output),tag=f.w(output+8),handler=f.q(output+16),object=f.q(output+24)),read=read,write=write,setter_sink_calls=calls,service_calls=lookups,hooks=[0x3c9298,0x3d5670,0x3dfa9c,0x93b09c],scope='Native tag table selection and virtual callback routing, with synthetic class-ID/component services and setter sink; no native class bootstrap or Unity scheduling')

def type_records(raw):
    f=Fixture(raw);records=[]
    for start in (0x10f0628,0x10ea010):
        name=struct.unpack('<Q',f.source(start+24,8))[0];f.source(start+48,8);f.source(start+88,8);b=bytearray()
        for i in range(128):
            v=f.source(name+i,1)[0]
            if not v:break
            b.append(v)
        else:raise ValueError('unterminated original type name')
        records.append(dict(record=start,name=b.decode(),name_va=name,class_id=f.w(start+48),native_size=f.w(start+52),descriptor=f.q(start+88)))
    return records

def binding_policy(raw,binding,target_class_id):
    component,value=type_records(raw);reg=registration(raw)
    from_source=next(s for s in raw['strings'] if s['text']=='m_Sprite')['occurrences'][0]
    name=bytes.fromhex(from_source['hex']).rstrip(b'\0').decode();match=resolve(raw,name)
    assert component['name']=='SpriteRenderer' and value['name']=='Sprite'
    assert reg['map_type_descriptor']==component['descriptor'] and reg['slot_23']==reg['handler']
    assert match['return_value']==1
    attribute=struct.unpack_from('<I',bytes.fromhex(match['output_hex']),4)[0]
    expected=dict(attribute=attribute,customType=reg['map_tag'],typeID=component['class_id'],isPPtrCurve=1,isIntCurve=0,isSerializeReferenceCurve=0)
    if target_class_id!=component['class_id'] or any(binding.get(k)!=v for k,v in expected.items()) or binding.get('script')!={'m_FileID':0,'m_PathID':0}:raise ValueError('binding outside bounded source-proved policy')
    return name
