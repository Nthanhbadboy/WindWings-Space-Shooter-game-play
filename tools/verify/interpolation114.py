"""Original native AnimationCurve arithmetic, not an Animator/clip-equivalence assertion."""
import argparse,gzip,hashlib,json,math,struct
from pathlib import Path
from tools.verify.interpolation114_native import CurveFixture,key,f32,bits
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/interpolation114/probe.json.gz'
OUT=ROOT/'datas/l3_ef6b75ef114_native_interpolation.json.gz'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_raw():return json.load(gzip.open(RAW))
def hermite(a,b,t):
    dt=b['time']-a['time'];u=(t-a['time'])/dt;u2=u*u;u3=u2*u
    return (2*u3-3*u2+1)*a['value']+(u3-2*u2+u)*dt*a['outSlope']+(-2*u3+3*u2)*b['value']+(u3-u2)*dt*b['inSlope']
def bezier_reference(a,b,t):
    d=b['time']-a['time'];x=(t-a['time'])/d;wo=a['outWeight'] if a['weightedMode']&2 else f32(1/3);wi=b['inWeight'] if b['weightedMode']&1 else f32(1/3)
    def poly(u,v0,v1,v2,v3):return (1-u)**3*v0+3*(1-u)**2*u*v1+3*(1-u)*u*u*v2+u**3*v3
    lo=0.;hi=1.
    for _ in range(80):
        mid=(lo+hi)/2
        if poly(mid,0,wo,1-wi,1)<x:lo=mid
        else:hi=mid
    u=(lo+hi)/2
    return poly(u,a['value'],a['value']+wo*d*a['outSlope'],b['value']-wi*d*b['inSlope'],b['value'])
def clean(x):
    if isinstance(x,float) and not math.isfinite(x):return 'NaN' if math.isnan(x) else 'Infinity' if x>0 else '-Infinity'
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x

def original_curve():
    path=ROOT/'reverse-engineering/raw/l3-visual-surface/objects-0007.jsonl.gz';row=json.loads(gzip.decompress(path.read_bytes()).splitlines()[134]);assert row['serialized_file']=='data.unity3d/level2' and row['path_id']==4783
    return path,row,row['tree']['SizeModule']['curve']['maxCurve']
def streamed_adapter(raw):
    from tools.verify.balloon_animation import decode_stream
    path=ROOT/'reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz';row=json.loads(gzip.decompress(path.read_bytes()).splitlines()[140]);assert row['path_id']==1609 and row['serialized_file']=='data.unity3d/resources.assets'
    muscle=row['tree']['m_MuscleClip'];stream=muscle['m_Clip']['data']['m_StreamedClip'];frames=decode_stream(stream['data'],stream['curveCount']+stream.get('discreteCurveCount',0));start=muscle['m_StartTime'];stop=muscle['m_StopTime']
    candidates=[(f,k) for f in frames if isinstance(f['time'],(int,float)) and start<=f['time']<stop for k in f['keys'] if k['index']<stream['curveCount'] and any(k['coeff'][:3])]
    frame,k=candidates[0];later=[f['time'] for f in frames if isinstance(f['time'],(int,float)) and frame['time']<f['time']<=stop and any(q['index']==k['index'] for q in f['keys'])];end=min(later) if later else stop
    assert frame['time']<end;fixture=CurveFixture(raw,[key(0,0),key(1,1)])
    fixture.sw(fixture.curve+4,bits(frame['time']));fixture.sw(fixture.curve+8,bits(end))
    for i,c in enumerate(k['coeff']):fixture.sw(fixture.curve+12+4*i,bits(c))
    runs=[]
    for fraction in (.25,.5,.75):
        t=f32(frame['time']+(end-frame['time'])*fraction);native=fixture.evaluate(t);dt=t-frame['time'];a,b,c,d=k['coeff'];runs.append(dict(native=native,float64_polynomial=((a*dt+b)*dt+c)*dt+d))
    return dict(raw_location=dict(path=str(path.relative_to(ROOT)),row=140),raw_object_sha256=row['raw_object_sha256'],clip=dict(serialized_file=row['serialized_file'],path_id=row['path_id']),channel=k['index'],key_time=frame['time'],end_time=end,key_byte_offset=k['byte_offset'],coeff=k['coeff'],runs=runs,scope='Decoded original StreamedClip coefficients injected into AnimationCurve cache layout to compare arithmetic only; NOT native StreamedClip memory/consumer selection or Animator equivalence')

def build():
    raw=load_raw();families=[]
    for label,keys in [('smooth',[key(0,0),key(1,1)]),('linear',[key(0,0,out_slope=1),key(1,1,in_slope=1)]),('asymmetric',[key(2,-1,out_slope=2),key(4,3,in_slope=-1)])]:
        f=CurveFixture(raw,keys);times=[keys[0]['time']+(keys[-1]['time']-keys[0]['time'])*i/4 for i in range(5)];runs=[f.evaluate(t) for t in times]
        families.append(dict(name=label,keys=keys,runs=runs,hermite_reference=[hermite(*keys,t) for t in times],scope='Native search/cache construction/evaluation; ideal Hermite is comparison only'))
    f=CurveFixture(raw,[key(0,0),key(1,1)]);cold=f.evaluate(.25);hot=f.evaluate(.5);api=f.api(.25)
    epsilon=CurveFixture(raw,[key(0,0),key(1e-5,1)]);tiny_time=f32(5e-6);cached=epsilon.evaluate(tiny_time);direct=epsilon.segment(tiny_time)
    weighted=[]
    for label,keys,bridge in [('weighted_linear_x',[key(0,0,weighted_mode=2),key(1,1,weighted_mode=1)],False),('weighted_quadratic_x',[key(0,0,weighted_mode=2,out_weight=0),key(1,1,weighted_mode=1,in_weight=2/3)],False),('weighted_cubic_x',[key(0,0,weighted_mode=2,out_weight=.1),key(1,1,weighted_mode=1,in_weight=.7)],True),('weighted_three_real_roots',[key(0,0,weighted_mode=2,out_weight=.25),key(1,1,weighted_mode=1,in_weight=.25)],True)]:
        f=CurveFixture(raw,keys);bindings=f.enable_host_math() if bridge else [];runs=[f.evaluate(t) for t in (.25,.5,.75)];weighted.append(dict(name=label,keys=keys,host_math_bridge=bridge,import_bindings=bindings,runs=runs,reference=[bezier_reference(*keys,t) for t in (.25,.5,.75)],scope='Native weighted solver; host logf/exp/atan2f/cosf only when explicitly enabled, NOT Android libm bit parity'))
    wraps=[]
    for mode in (0,1,2):
        for t in (-.25,1.25):
            f=CurveFixture(raw,[key(0,0,out_slope=1),key(1,1,in_slope=1)],pre=mode,post=mode);wraps.append(dict(raw_internal_mode=mode,run=f.evaluate(t)))
    steps=[]
    for out_slope,in_slope in [(math.inf,0),(0,math.inf),(-math.inf,0),(0,-math.inf),(math.inf,-math.inf)]:
        f=CurveFixture(raw,[key(0,2,out_slope=out_slope),key(1,7,in_slope=in_slope)]);steps.append(dict(outSlope=out_slope,inSlope=in_slope,cached=f.evaluate(.25),direct=f.segment(.25)))
    path,row,curve=original_curve();keys=curve['m_Curve'];f=CurveFixture(raw,keys);times=sorted(set([k['time'] for k in keys]+[f32((a['time']+b['time'])/2) for a,b in zip(keys,keys[1:])]));source_runs=[]
    for t in times:
        run=f.evaluate(t);pair=next(((a,b) for a,b in zip(keys,keys[1:]) if a['time']<=t<=b['time']),None);source_runs.append(dict(run=run,hermite_reference=hermite(*pair,t)))
    producer_fixture=CurveFixture(raw,[key(0,0),key(1,1)]);producer=producer_fixture.produce_records(7);packed=producer_fixture.pack_prepared_records(0xa5)
    from tools.verify.balloon_animation import decode_stream
    b=bytes.fromhex(packed['bytes_hex']);packed['decoded_frames']=decode_stream(struct.unpack('<'+'I'*(len(b)//4),b),8)
    source_fixture=CurveFixture(raw,keys);source_producer=source_fixture.produce_records(0);source_packed=source_fixture.pack_prepared_records(0xa5)
    stream_adapter=streamed_adapter(raw)
    source=dict(identity=dict(serialized_file=row['serialized_file'],path_id=row['path_id']),type=row['type'],raw_location=dict(path=str(path.relative_to(ROOT)),row=134),raw_object_sha256=row['raw_object_sha256'],field='.SizeModule.curve.maxCurve',serialized_curve=curve,runs=source_runs,scope='Original serialized keys supplied to a synthetic AnimationCurve native layout; NOT ParticleSystem consumer, simulation or mesh/readback proof. Raw infinity enums are retained, NOT equated to internal/public wrap enums.')
    paths=[RAW,path,Path(__file__),ROOT/'tools/verify/interpolation114_native.py',ROOT/'tools/verify/tag23_113_native.py',ROOT/'tools/recovery/interpolation114.py',ROOT/'reverse-engineering/il2cpp/dump.cs.gz',ROOT/'tools/verify/balloon_animation.py',ROOT/'reverse-engineering/raw/l3-visual-surface/objects-0015.jsonl.gz']
    counts=dict(followed_entries=len(raw['followed']),fde_extents=sum(r['unwind'] is not None for r in raw['followed']),bounded_windows=sum(r['unwind'] is None for r in raw['followed']),direct_caller_sites=len(raw['branch_references']),direct_caller_functions=len({r['unwind']['start'] for r in raw['branch_references'] if r['unwind']}),synthetic_unweighted_samples=sum(len(f['runs']) for f in families),weighted_samples=sum(len(f['runs']) for f in weighted),source_key_samples=len(source_runs),wrap_samples=len(wraps),step_pairs=len(steps))
    return clean(dict(schema=1,provisional=True,provenance='arena/ef6b75ef',inputs={str(p.relative_to(ROOT)):digest(p) for p in paths},xapk_sha256=raw['xapk_sha256'],libunity_sha256=raw['libunity_sha256'],recovery_tool_sha256=raw['tool_sha256'],counts=counts,entry=dict(registration=0x389544,managed_callback=0x36e71c,evaluator=0x952608,search=0x9528f8,coefficients=0x952a80,segment=0x951344,weighted=0x951468,inverse=0x951f60),families=families,cache=dict(cold=cold,hot=hot),api_bridge=api,small_interval=dict(cached=cached,direct=direct,scope='Native cached duration floor differs from direct segment normalization'),weighted=weighted,wraps=wraps,steps=steps,source_curve=source,record_producer=producer,native_frame_packing=packed,source_record_producer=source_producer,source_frame_packing=source_packed,streamed_adapter=stream_adapter,scope='Original native AnimationCurve evaluator/search/cache/weighted formulas in synthetic layouts. Zero-hook cases distinguished from managed-object bridge and host-libm cases. Direct caller coverage is NOT semantic ownership proof. NO AnimationClip streamed/dense or Animator blending equivalence, Unity bootstrap/readback, ParticleSystem simulation or render.'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();data=build();blob=gzip.compress((json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode(),mtime=0)
    if a.check:assert OUT.read_bytes()==blob,'artifact differs'
    else:OUT.write_bytes(blob)
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)),sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob),counts=data['counts'])))
if __name__=='__main__':main()
