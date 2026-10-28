"""Pinned native packed-clip ownership and original streamed-consumer evidence; provisional."""
import argparse,gzip,hashlib,json,math,struct
from pathlib import Path
from tools.verify.packed115_native import PackedFixture,frame
from tools.verify.interpolation114_native import bits,floatbits,f32
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/packed115/probe.json.gz'
SOURCE=ROOT/'reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz'
OUT=ROOT/'datas/l3_ef6b75ef115_packed_clip_native.json.gz'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_raw():return json.load(gzip.open(RAW))
def source_stream():
    with gzip.open(SOURCE,'rt') as source:
        for i,line in enumerate(source):
            if i==140:row=json.loads(line);break
        else:raise ValueError('missing pinned source row')
    assert row['path_id']==1609 and row['serialized_file']=='data.unity3d/resources.assets' and row['type']=='AnimationClip'
    stream=row['tree']['m_MuscleClip']['m_Clip']['data']['m_StreamedClip']
    data=struct.pack('<'+'I'*len(stream['data']),*stream['data'])
    return row,stream,data

def reference(data,time,continuous,discrete):
    """Explicit separate-f32 comparison only; never feeds decoded keys to the native consumer."""
    offset=0;records={};times=[]
    while offset<len(data):
        t,n=struct.unpack_from('<fI',data,offset);times.append(t)
        if t>time:break
        if n==0:raise ValueError('sample reached terminal sentinel')
        for i in range(n):
            index,*coeff=struct.unpack_from('<I4I',data,offset+8+i*20)
            records[index]=(t,coeff)
        offset+=8+n*20
    output=[]
    for i in range(continuous+discrete):
        t,words=records[i]
        if i>=continuous:output.append(words[3]);continue
        a,b,c,d=map(floatbits,words);dt=f32(f32(time)-t)
        value=a
        for coefficient in (b,c,d):value=f32(f32(value*dt)+coefficient)
        output.append(bits(value))
    return dict(output_bits=output,next_frame_byte_offset=offset,record_count=len(records))

def synthetic_stream(continuous=1,discrete=0):
    count=continuous+discrete
    initial=[(i,[0,0,0,bits(float(i)) if i<continuous else 100+i]) for i in range(count)]
    active=[(i,[bits(-2),bits(3),0,bits(float(i))] if i<continuous else [bits(99),bits(-31),bits(8),1000+i]) for i in reversed(range(count))]
    final=[(i,[0,0,0,bits(float(i+1))] if i<continuous else [0,0,0,2000+i]) for i in range(count)]
    return frame(-3.4028234663852886e38,initial)+frame(0,active)+frame(1,final)+frame(math.inf,[])

def original_bytes(raw,address,length):
    spans=[w for w in raw['windows']+raw['cells'] if w['va']<=address and address+length<=w['va']+len(w['hex'])//2]
    assert spans,f'uncaptured {address:x}+{length}'
    values=[bytes.fromhex(w['hex'])[address-w['va']:address-w['va']+length] for w in spans]
    assert all(b==values[0] for b in values)
    return values[0]

def ownership(raw):
    # Exact original instructions, not ADRP candidate labels alone.
    anchors=(0x399820,0x39868c,0xb6a850,0xb6bbd0,0xb6b944,0xb6b948,0xb6dffc,0xb922e0,0xb92300,0x6d2ee0,0x6d2f00,0x6df2ac,0x6df328)
    # Keep bytes in the artifact; tests also verify decoded operand/dataflow anchors.
    code=[dict(pc=pc,hex=original_bytes(raw,pc,4).hex()) for pc in anchors]
    record=0x10f29f0;b=original_bytes(raw,record,96);class_id,native_size=struct.unpack_from('<II',b,48)
    assert class_id==74 and native_size==592
    relocs={r['address']:r['addend'] for r in raw['relocations']}
    assert relocs[record+24]==next(s for s in raw['strings'] if s['text']=='AnimationClip')['occurrences'][0]['va']
    return dict(native_type=dict(record=record,name='AnimationClip',class_id=class_id,native_size=native_size,name_relocation=relocs[record+24],descriptor=relocs[record+88]),anchors=code,chain=[dict(from_pc=0xb6b944,to=0x6ad7e4,meaning='native compiler called with scratch input, result stored at owner+0x1e0'),dict(from_pc=0x6adbe4,to=0x6c4480,meaning='curve record producer, retained114'),dict(from_pc=0x6add58,to=0x6c498c,meaning='packed stream compiler, retained114'),dict(from_pc=0xb6e014,to=0xb6e5ac,meaning='serializer m_MuscleClip gets pointer owner+0x1e0'),dict(from_pc=0x6d2f00,to=0x6df270,meaning='compiled muscle+0x5f0 relative pointer resolved into ClipConstant dispatcher'),dict(from_pc=0x6df2ac,to=0x6df310,meaning='streamed channel sampler'),dict(from_pc=0x6df328,to=0x6df768,meaning='packed frame selector/cache writer')],scope='Original native API/serializer/compiler field linkage and static runtime callers; class74 record separately confirmed. Native object creation/engine scheduling/Animator blend and setter application NOT executed.')

def build():
    raw=load_raw();row,stream,data=source_stream();continuous=stream['curveCount'];discrete=stream.get('discreteCurveCount',0)
    fixture=PackedFixture(raw,data,continuous,discrete);runs=[]
    for time in (0,.1,.2,f32(.36666667461395264),.5,1,3.4,row['tree']['m_MuscleClip']['m_StopTime'],.1,.1):
        native=fixture.sample(time,True);comparison=reference(data,native['time'],continuous,discrete)
        assert native['output_bits']==comparison['output_bits'] and native['next_frame_byte_offset']==comparison['next_frame_byte_offset']
        runs.append(dict(native=native,reference=comparison))
    families=[]
    for continuous_count,discrete_count in ((1,0),(3,2),(4,4),(5,5),(8,8)):
        b=synthetic_stream(continuous_count,discrete_count);f=PackedFixture(raw,b,continuous_count,discrete_count);samples=[]
        for t in (.25,.5,1,.25,.25):
            native=f.sample(t);ref=reference(b,t,continuous_count,discrete_count);assert native['output_bits']==ref['output_bits'];samples.append(native)
        families.append(dict(continuous=continuous_count,discrete=discrete_count,data_sha256=hashlib.sha256(b).hexdigest(),runs=samples))
    paths=[RAW,SOURCE,Path(__file__),ROOT/'tools/verify/packed115_native.py',ROOT/'tools/verify/tag23_113_native.py',ROOT/'tools/verify/interpolation114_native.py',ROOT/'tools/recovery/packed115.py',ROOT/'tests/test_packed115.py']
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):digest(p) for p in paths},xapk_sha256=raw['xapk_sha256'],libunity_sha256=raw['libunity_sha256'],recovery_tool_sha256=raw['tool_sha256'],ownership=ownership(raw),native_entries=dict(initialize=0x6df02c,dispatch=0x6df270,sample=0x6df310,select=0x6df768,dense_sample_unexecuted=0x6df518),layout=dict(streamed_header=dict(word_count=0,relative_data_pointer=8,continuous_u16=16,discrete_u16=18),cache=dict(records_pointer=0,continuous_u16=8,discrete_u16=10,last_time=12,next_frame_byte_offset=16),record=dict(size=20,time=0,a=4,b=8,c=12,d=16),frame=dict(header_size=8,key_size=20,index=0,coefficients=4)),source=dict(identity=dict(serialized_file=row['serialized_file'],path_id=row['path_id'],name=row['tree']['m_Name']),raw_location=dict(path=str(SOURCE.relative_to(ROOT)),row=140),raw_object_sha256=row['raw_object_sha256'],word_count=len(stream['data']),byte_count=len(data),packed_data_sha256=hashlib.sha256(data).hexdigest(),continuous=continuous,discrete=discrete,start=row['tree']['m_MuscleClip']['m_StartTime'],stop=row['tree']['m_MuscleClip']['m_StopTime'],native_initialization=fixture.initialization,allocator_calls=fixture.allocator_calls,initialized_records_sha256=hashlib.sha256(bytes.fromhex(fixture.initialized_hex)).hexdigest(),runs=runs,input_adapter='Copy ALL original serialized uint32 words without decoding/repacking frames; construct only native relative-pointer/u16 header, original initializer builds cache through one explicit allocator service.'),synthetic_families=families,counts=dict(source_samples=len(runs),source_channel_values=len(runs)*(continuous+discrete),synthetic_samples=sum(len(c['runs']) for c in families),native_executed_instructions=sum(s['native']['run']['instruction_count'] for s in runs)+sum(s['run']['instruction_count'] for c in families for s in c['runs']),structural_candidates=len(raw['sampler_candidates']),captured_direct_caller_sites=len(raw['branch_references'])),scope='Actual original StreamedClip frame/channel selection and scalar/SIMD evaluation or discrete DWORD copy in native functions, zero hooks during samples; explicit allocator only during native cache initialization. Prepared native layouts and Unicorn execution, NOT Unity engine bootstrap/readback/render or full AnimationClip playback/Animator time wrapping/blending/application. Dense sampler identified but unexecuted; source discrete bits NOT promoted to resolved PPtr objects.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();b=gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==b,'artifact differs'
    else:OUT.write_bytes(b)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),counts=r['counts'])))
if __name__=='__main__':main()
