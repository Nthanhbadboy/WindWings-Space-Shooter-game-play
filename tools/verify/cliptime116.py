"""Provisional native clip-time -> aggregate sampler proof, with declared modff/memcpy bridges."""
import argparse,gzip,hashlib,json,math,struct
from pathlib import Path
from tools.verify import packed115
from tools.verify.cliptime116_native import ClipFixture
from tools.verify.interpolation114_native import bits,floatbits,f32
ROOT=Path(__file__).resolve().parents[2];RAW=ROOT/'reverse-engineering/raw/cliptime116/probe.json.gz';OUT=ROOT/'datas/l3_ef6b75ef116_native_clip_time_dense.json.gz'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_raw():return json.load(gzip.open(RAW))
def time_reference(time,start=0,stop=1,offset=0,direction=1,quantization_rate=0,loop=True):
    q,start,stop,offset,direction,rate=map(f32,(time,start,stop,offset,direction,quantization_rate));duration=f32(stop-start);shifted=f32(q+offset)
    fraction,cycles=map(f32,math.modf(shifted))
    if not loop:fraction=0. if q<=0 else 1. if q>=1 else q;cycles=0.
    elif shifted<0:fraction=f32(fraction+1);cycles=f32(cycles-1)
    if bits(direction)&0x80000000:
        fraction=f32(1-fraction)
        if loop:cycles=f32(-cycles)
    sample=f32(f32(duration*fraction)+start)
    if duration>0 and rate>0:
        value=f32(sample*rate);rounded=math.copysign(math.floor(abs(value)+.5),value);sample=f32(rounded/rate)
        fraction=f32(f32(1/duration)*f32(sample-start));fraction=0. if fraction<=0 else 1. if fraction>=1 else fraction
    return dict(sample_time_bits=bits(sample),phase_bits=bits(fraction),cycles_bits=bits(cycles))
def dense_reference(dense,time):
    u=f32(f32(f32(time)-f32(dense['begin']))*f32(dense['rate']));fraction,integer=math.modf(u);i=int(integer);a=min(max(i,0),dense['frames']-1);b=min(0 if i<0 else i+1,dense['frames']-1);out=[]
    for c in range(dense['curves']):
        left=f32(dense['samples'][a*dense['curves']+c]);right=f32(dense['samples'][b*dense['curves']+c]);out.append(bits(f32(left+f32(f32(right-left)*f32(fraction)))))
    return dict(output_bits=out,scaled_time_bits=bits(u),fraction_bits=bits(fraction),left_frame=a,right_frame=b)
def helper_cases():
    cases=[]
    for loop in (False,True):
        for q in (-1,-.25,0,.25,1,1.25):cases.append(dict(time=q,loop=loop))
    cases.extend([dict(time=.25,start=2,stop=4),dict(time=.25,offset=.5),dict(time=.25,offset=.5,loop=False),dict(time=.25,direction=-1),dict(time=.25,direction=-0.),dict(time=-.25,direction=-1),dict(time=.25,quantization_rate=2),dict(time=.75,quantization_rate=2),dict(time=0,start=.1,stop=.9,quantization_rate=2),dict(time=1,start=.1,stop=.9,quantization_rate=2,loop=False),dict(time=.25,start=2,stop=2,quantization_rate=2),dict(time=.25,start=4,stop=2,quantization_rate=2)])
    return cases

def build():
    raw115=packed115.load_raw();raw=load_raw();dense=dict(frames=3,curves=2,rate=2,begin=.5,samples=[0,10,10,20,20,30]);empty=ClipFixture(raw115,raw,dense=dense);helpers=[]
    for args in helper_cases():
        native=empty.helper(**args);ref=time_reference(**args)
        for k,v in ref.items():assert native[k]==v,(args,k,native[k],v)
        helpers.append(dict(input=args,native=native,reference=ref))
    dense_fixture=ClipFixture(raw115,raw,dense=dense);dense_runs=[]
    for t in (0,.25,.5,.75,1,1.25,1.5,2):
        native=dense_fixture.sample(t);ref=dense_reference(dense,t);assert native['output_bits']==ref['output_bits'];dense_runs.append(dict(native=native,reference=ref))
    mixed_constant=[bits(77),0x7fc12345];mixed=ClipFixture(raw115,raw,packed=packed115.synthetic_stream(1,1),continuous=1,discrete=1,dense=dict(frames=3,curves=2,rate=2,begin=0,samples=dense['samples']),constant=mixed_constant);mixed_runs=[]
    for t in (.25,.75,1.25,.25):
        native=mixed.sample(t);dr=dense_reference(dict(dense,begin=0),t);sr=packed115.reference(packed115.synthetic_stream(1,1),t,1,1);assert native['output_bits']==sr['output_bits']+dr['output_bits']+mixed_constant;mixed_runs.append(native)
    mixed.configure_time(start=0,stop=1,cycle_offset=.25)
    joint=mixed.sample(1,True,True);jr=time_reference(1,offset=.25);jt=floatbits(jr['sample_time_bits']);assert joint['output_bits']==packed115.reference(packed115.synthetic_stream(1,1),jt,1,1)['output_bits']+dense_reference(dict(dense,begin=0),jt)['output_bits']+mixed_constant
    row,stream,data=packed115.source_stream();muscle=row['tree']['m_MuscleClip'];source_dense=muscle['m_Clip']['data']['m_DenseClip'];source=ClipFixture(raw115,raw,packed=data,continuous=stream['curveCount'],discrete=stream['discreteCurveCount'],dense=dict(frames=source_dense['m_FrameCount'],curves=source_dense['m_CurveCount'],rate=source_dense['m_SampleRate'],begin=source_dense['m_BeginTime'],samples=source_dense['m_SampleArray']))
    source.configure_time(start=muscle['m_StartTime'],stop=muscle['m_StopTime'],cycle_offset=muscle['m_CycleOffset'],quantization_rate=-1);source_runs=[]
    for q in (0,.25,.5,.75,1,1.25,-.25,-1,.25,.25):
        native=source.sample(q,True,muscle['m_LoopTime']);tr=time_reference(q,start=muscle['m_StartTime'],stop=muscle['m_StopTime'],offset=muscle['m_CycleOffset'],quantization_rate=-1,loop=muscle['m_LoopTime']);sample=floatbits(tr['sample_time_bits']);ref=packed115.reference(data,sample,stream['curveCount'],stream['discreteCurveCount']);assert native['output_bits']==ref['output_bits'] and bits(native['stream_last_time'])==tr['sample_time_bits'] and bits(native['returned_phase'])==tr['phase_bits'];source_runs.append(dict(native=native,time_reference=tr,stream_reference=ref))
    paths=[RAW,packed115.RAW,packed115.SOURCE,Path(__file__),ROOT/'tools/verify/cliptime116_native.py',ROOT/'tools/recovery/cliptime116.py',ROOT/'tools/verify/packed115.py',ROOT/'tools/verify/interpolation114_native.py',ROOT/'tools/verify/tag23_113_native.py',ROOT/'tests/test_cliptime116.py']
    samples=[x['native'] for x in helpers]+[x['native'] for x in dense_runs]+mixed_runs+[joint]+[x['native'] for x in source_runs]
    return dict(schema=1,provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):digest(p) for p in paths},libunity_sha256=raw['libunity_sha256'],xapk_sha256=raw['xapk_sha256'],recovery_tool_sha256=raw['tool_sha256'],bindings=source.bindings,time_helper=dict(entry=0xb93158,abi=dict(s0='normalized query',s1='start',s2='stop',s3='offset sum',s4='raw sign control',s5='quantization rate control',w0='loop bit',x1='phase output pointer',x2='cycles output pointer'),cases=helpers),dense=dict(input=dense,scope='Synthetic frame-major dense values, NOT observed nonempty source dense data',initialization=dense_fixture.initialization,allocator_calls=dense_fixture.allocations,runs=dense_runs),mixed=dict(continuous=1,discrete=1,dense=2,constant=2,constant_bits=mixed_constant,allocator_calls=mixed.allocations,initialization=mixed.initialization,runs=mixed_runs,time_to_mixed=joint,scope='Synthetic stream+dense+constant dispatcher ordering and wrapper composition, with modff/memcpy bridges'),source=dict(identity=dict(serialized_file=row['serialized_file'],path_id=row['path_id']),raw_object_sha256=row['raw_object_sha256'],packed_data_sha256=hashlib.sha256(data).hexdigest(),dense_metadata=source_dense,serialized_time=dict(start=muscle['m_StartTime'],stop=muscle['m_StopTime'],cycle_offset=muscle['m_CycleOffset'],loop=muscle['m_LoopTime']),context_fixture=dict(direction=1,offset=0,quantization_rate=-1,loop_parameter_from_serialized_bool=True),allocator_calls=source.allocations,initialization=source.initialization,runs=source_runs,scope='Unchanged original packed words + serialized start/stop/cycle adapted to proved native fields; prepared context and loop parameter, NOT actual Animator context acquisition/scheduling. Source dense curves0, samples0 despite frameCount420; dense branch is skipped here.'),counts=dict(helper_samples=len(helpers),dense_samples=len(dense_runs),mixed_samples=len(mixed_runs)+1,source_samples=len(source_runs),source_channel_values=len(source_runs)*(stream['curveCount']+stream['discreteCurveCount']),sample_native_instructions=sum(s['run']['instruction_count'] for s in samples),sample_modff_calls=sum(sum(c['symbol']=='modff' for c in s['external_calls']) for s in samples),sample_memcpy_calls=sum(sum(c['symbol']=='memcpy' for c in s['external_calls']) for s in samples)),scope='Original clip time conversion -> aggregate streamed/dense/constant selection/evaluation in prepared native layouts. Explicit host modff decomposition and memcpy byte-copy bridges, allocator hooks only for native initialization; NOT Android-libm parity, Unity playback/readback/render, actual Animator timing/state/layer blending/normalization or property/PPtr application. Nonempty dense/constant fixtures synthetic, source raw-tree extraction inherited.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=build();blob=gzip.compress((json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==blob,'artifact differs'
    else:OUT.write_bytes(blob)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),counts=r['counts'])))
if __name__=='__main__':main()
