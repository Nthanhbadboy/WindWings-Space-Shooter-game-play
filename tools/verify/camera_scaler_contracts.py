"""Static CameraScaler writer proof plus a bounded binary32 arithmetic model."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
from early_ui_native import section
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'reverse-engineering/raw/camera-scaler'


def sha(blob):return hashlib.sha256(blob).hexdigest()
def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def scaled_ortho(width,height,factor,minimum):
    if any(type(n) is not int or not 1<=n<=0x7fffffff for n in (width,height)):
        raise ValueError('model requires positive signed-int32 Screen dimensions')
    return max(f32(f32(f32(height)/f32(width))*factor),minimum)

def clipped_method(text,name,start,end):
    body=section(text,name);kept=[];discarded=[]
    for line in body.splitlines()[1:]:
        m=re.match(r'\s*(0x[0-9a-f]+):',line)
        if not m:continue
        (kept if start<=int(m[1],16)<end else discarded).append(line)
    return dict(instructions=kept,outside_declared_span=discarded)


def build():
    index=json.loads((RAW/'index.json').read_text());sources={}
    for ref in index['files']:
        path=RAW/ref['path'];blob=path.read_bytes()
        if path.suffix=='.gz':blob=gzip.decompress(blob)
        assert sha(blob)==ref['sha256_decompressed'];sources[ref['path']]=sha(blob)
    dump_blob=gzip.decompress((ROOT/'reverse-engineering/il2cpp/dump.cs.gz').read_bytes());assert sha(dump_blob)==index['dump_sha256_decompressed'];dump=dump_blob.decode()
    raw=json.load(gzip.open(RAW/'components.json.gz','rt'));data=json.loads((RAW/'native-data.json').read_text())
    assert data['native_sha256']==raw['binary_inputs_sha256']['lib/arm64-v8a/libil2cpp.so']
    literals={}
    for row in data['slices']:
        blob=bytes.fromhex(row['hex']);assert len(blob)==4 and sha(blob)==row['sha256']
        value=struct.unpack('<f',blob)[0];assert value==row['float32'];literals[row['va']]=value
    factor=literals['0x756f00'];minimum=literals['0x756fb8']
    assert factor==f32(5.4) and minimum==f32(9.6)
    asm=(RAW/'native/CameraScaler.asm.txt').read_text();native=json.loads((RAW/'native/CameraScaler.json').read_text())
    assert len(native['methods'])==3 and all(not m['size_capped'] for m in native['methods'])
    awake=clipped_method(asm,'Awake',0x141d70c,0x141d710);resize=section(asm,'ResizeCameras')
    checks=dict(awake_tailcalls_resize=len(awake['instructions'])==1 and '#0x141d710' in awake['instructions'][0],
        screen_height_then_width=resize.index('#0x27665e4')<resize.index('#0x27665bc'),
        height_over_width_then_factor=all(x in resize for x in ('mov      w20, w0','scvtf    s0, w20','scvtf    s3, w0','fdiv     s0, s0, s3','fmul     s0, s0, s1','fmaxnm   s8, s0, s2')),
        raw_pool_locations=all(x in resize for x in ('#0x756000','[x9, #0xf00]','[x9, #0xfb8]')),
        camera_array_at_0x20='ldr      x8, [x19, #0x20]' in resize,
        reverse_index_iteration=all(x in resize for x in ('subs     w21, w9, #1','x8, x8, w21, uxtw #3','subs     w21, w21, #1')),
        same_value_written_to_camera=all(x in resize for x in ('mov      v0.16b, v8.16b','#0x275e1b0')),
        null_camera_branches_to_failure='cbz      x0, #0x141d7a0' in resize and '0x141d7a0: bl       #0x110d250' in resize)
    assert all(checks.values()),checks
    signatures={}
    for address in ('27665E4','27665BC','275E1B0'):
        m=re.search(r'// RVA: 0x'+address+r'[^\n]*\n([^\n]+)',dump);assert m;signatures['0x'+address.lower()]=m[1].strip()
    assert 'get_height()' in signatures['0x27665e4'] and 'get_width()' in signatures['0x27665bc'] and 'set_orthographicSize(float value)' in signatures['0x275e1b0']
    declaration=re.search(r'class CameraScaler[^}]+}',dump)[0];assert 'orthographicCameras; // 0x20' in declaration
    context_blob=gzip.decompress((ROOT/'datas/scene_render_context_contract.json.gz').read_bytes());context=json.loads(context_blob)
    cameras={(c['identity']['serialized_file'],c['identity']['path_id']):c for c in context['cameras']}
    files={f['serialized_file']:f for f in raw['files']};components=[];scene_refs=set()
    for row in raw['components']:
        resolved=[];assert len(row['tree']['orthographicCameras'])==len(row['cameras'])
        for ptr,ref in zip(row['tree']['orthographicCameras'],row['cameras']):
            assert ptr==ref['pointer']
            if not ptr['m_PathID']:assert ref['status']=='null';resolved.append(None);continue
            assert ref['status']=='resolved' and ref['identity']['type']=='Camera'
            file=row['serialized_file'] if ptr['m_FileID']==0 else 'data.unity3d/'+files[row['serialized_file']]['externals'][ptr['m_FileID']-1]['path']
            assert file==ref['identity']['serialized_file'] and ptr['m_PathID']==ref['identity']['path_id']
            k=(file,ptr['m_PathID'])
            if k in cameras:
                assert cameras[k]['raw_object_sha256']==ref['raw_object_sha256'] and cameras[k]['tree']==ref['tree'];scene_refs.add(k)
            resolved.append(ref['identity'])
        components.append(dict(identity={k:row[k] for k in ('serialized_file','type','path_id')},raw_object_sha256=row['raw_object_sha256'],parsed_script_pointer=row['parsed_script_pointer'],
            serialized_component_enabled=row['tree']['m_Enabled'],gameobject=row['gameobject'],camera_array_order=resolved,native_write_order=list(reversed(resolved))))
    assert scene_refs==set(cameras)
    samples=[dict(width=w,height=h,modeled_setter_argument=scaled_ortho(w,h,factor,minimum)) for w,h in ((1080,1920),(1080,2400),(1920,1080),(720,1280),(390,844))]
    return dict(status='PROVISIONAL_STATIC_RUNTIME_WRITER_AND_ARITHMETIC_MODEL_NOT_DEVICE_EXECUTION',sources=dict(files_sha256_decompressed=sources,dump_sha256_decompressed=sha(dump_blob),scene_context_sha256_decompressed=sha(context_blob)),
        scan=dict(headers=raw['scanned_headers'],header_errors=raw['header_errors']),native_checks=checks,resolved_calls=signatures,awake_declared_span=awake,
        float_pool=data['slices'],formula='max(float32(float32(float32(Screen.height) / float32(Screen.width)) * factor), minimum)',factor=factor,minimum=minimum,
        components=components,summary=dict(components=len(components),camera_refs=sum(len(c['camera_array_order']) for c in components),scene_cameras_bound=len(scene_refs)),arithmetic_samples=samples,
        limits=['Captured Awake calls ResizeCameras; this does not prove absence of other writers, reflection calls, later camera changes or resolution-change handling.',
                'Model uses positive signed-int32 Screen dimensions and nominal IEEE binary32 rounding; runtime FPCR/device rendering is not captured.',
                'Whole Screen height/width getters are used, not a measured per-camera viewport aspect or screenshot dimensions.',
                'Awake raw export has a minimum-eight-byte overlap into the next method. Semantic instructions are clipped to the next dump RVA, preserving raw separately.',
                'Five scene camera bindings match report77 snapshots. The sharedassets component/camera is a serialized reference, not a proven spawned instance.',
                'The arithmetic model predicts the setter argument, not a Unity property readback; internal engine setter behavior is not executed.',
                'No automatic null skipping, array repair, startup execution, world-to-screen projection, stencil or visibility is simulated.'])


if __name__=='__main__':
    result=build();(ROOT/'datas/camera_scaler_contract.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(summary=result['summary'],factor=result['factor'],minimum=result['minimum'],samples=result['arithmetic_samples']),indent=2))
