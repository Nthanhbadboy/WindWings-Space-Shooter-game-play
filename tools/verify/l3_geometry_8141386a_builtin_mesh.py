"""Narrow own static Mesh decode + source-byte spans for #7.
provenance: arena/8141386a-windwings-space-shooter-game-p
Schema/format/16-byte stream-alignment conventions are consulted from UnityPy1.25.4;
this code does not call UnityPy/MeshHelper. Unsupported/compressed/streamed layouts
fail closed. These are actual captured Mesh payloads, never constructed primitives.
"""
from __future__ import annotations
import base64
import math
import struct
from tools.verify.geometry_8141386a_atlas_io import sha,canonical
from tools.verify.controller109_binary import Reader


def payload(value):
    if isinstance(value,list):return bytes(value)
    if isinstance(value,dict) and value.get('encoding')=='base64':
        b=base64.b64decode(value['bytes_base64'],validate=True)
        if 'size' in value and len(b)!=value['size']:raise ValueError('payload declared length')
        return b
    raise ValueError('unsupported payload encoding')


def matches(blob,value):
    hits=[];start=0
    if not value:raise ValueError('empty payload cannot prove a byte span')
    while True:
        p=blob.find(value,start)
        if p<0:break
        hits.append(dict(offset=p,size=len(value),sha256=sha(blob[p:p+len(value)])))
        start=p+1
    if not hits:raise ValueError('captured Mesh payload not present in original bytes')
    return hits


def decode(tree):
    if tree.get('m_MeshCompression',0)!=0:raise ValueError('compressed Mesh requires another decoder')
    streamed=tree.get('m_StreamData',{})
    if streamed.get('size',0) or streamed.get('path',''):raise ValueError('external Mesh stream requires actual source bytes')
    vd=tree['m_VertexData'];n=vd['m_VertexCount']
    if not 3<=n<=100000:raise ValueError('Mesh vertex-count budget')
    channels=[(i,c) for i,c in enumerate(vd['m_Channels']) if c['dimension']]
    if not channels or channels[0][0]!=0:raise ValueError('missing position channel')
    strides={}
    for i,c in channels:
        if c['format']!=0 or c['dimension'] not in (1,2,3,4) or c['offset']<0:raise ValueError('only corroborated Float32 channel domain')
        strides[c['stream']]=max(strides.get(c['stream'],0),c['offset']+4*c['dimension'])
    if sorted(strides)!=list(range(len(strides))):raise ValueError('noncontiguous stream layout')
    offsets={};stop=0
    for stream,stride in sorted(strides.items()):
        offsets[stream]=(stop+15)//16*16;stop=offsets[stream]+n*stride
    data=payload(vd['m_DataSize'])
    if len(data)!=stop:raise ValueError('Mesh vertex stream extent')
    decoded={}
    for i,c in channels:
        values=[list(struct.unpack_from('<'+'f'*c['dimension'],data,offsets[c['stream']]+v*strides[c['stream']]+c['offset'])) for v in range(n)]
        if not all(math.isfinite(x) for v in values for x in v):raise ValueError('nonfinite Mesh channel')
        decoded[str(i)]=values
    positions=decoded['0']
    if any(len(v)!=3 for v in positions):raise ValueError('position dimension is not3')
    index=payload(tree['m_IndexBuffer']);size={0:2,1:4}.get(tree['m_IndexFormat'])
    if not size:raise ValueError('unknown index format')
    fmt='H' if size==2 else 'I';triangles=[];ranges=[]
    for sub in tree['m_SubMeshes']:
        first,count,base=sub['firstByte'],sub['indexCount'],sub['baseVertex']
        if sub['topology']!=0 or count%3 or first%size or first<0 or first+count*size>len(index):raise ValueError('Mesh triangle/index extent')
        values=[v[0]+base for v in struct.iter_unpack('<'+fmt,index[first:first+count*size])]
        lo,hi=sub['firstVertex'],sub['firstVertex']+sub['vertexCount']
        if not 0<=lo<=hi<=n or any(not lo<=v<hi for v in values):raise ValueError('Mesh submesh vertex/base extent')
        triangles.extend([values[p:p+3] for p in range(0,len(values),3)]);ranges.append((first,first+count*size))
    ranges.sort()
    if not ranges or ranges[0][0]!=0 or ranges[-1][1]!=len(index) or any(a[1]!=b[0] for a,b in zip(ranges,ranges[1:])):raise ValueError('Mesh index overlap/gap')
    minimum=[min(v[i] for v in positions) for i in range(3)];maximum=[max(v[i] for v in positions) for i in range(3)]
    return dict(vertex_count=n,index_count=sum(len(t) for t in triangles),triangles=triangles,channels=decoded,positions=positions,
                minimum=minimum,maximum=maximum,span=[b-a for a,b in zip(minimum,maximum)],
                vertex_payload_sha256=sha(data),index_payload_sha256=sha(index))


def normalize_capture(value):
    if isinstance(value,dict):
        if value.get('encoding')=='base64':return list(payload(value))
        return {k:normalize_capture(v) for k,v in value.items()}
    if isinstance(value,list):return [normalize_capture(v) for v in value]
    return value


def corroborate(mesh):
    blob=bytes.fromhex(mesh['original_hex'])
    if sha(blob)!=mesh['object_sha256'] or len(blob)!=mesh['byte_size']:raise ValueError('original Mesh byte/hash/size mismatch')
    if sha(canonical(mesh['schema']))!=mesh['schema_sha256']:raise ValueError('Mesh schema pin mismatch')
    reader=Reader(blob);t=reader.decode(mesh['schema'])
    if t!=normalize_capture(mesh['tree']):raise ValueError('independent Mesh decode differs from captured UnityPy tree')
    geometry=decode(t)
    spans={name:matches(blob,value) for name,value in (
        ('vertex_payload',payload(t['m_VertexData']['m_DataSize'])),('index_payload',payload(t['m_IndexBuffer'])))}
    typed=[dict(field=r['field'],offset=r['start'],size=r['end']-r['start'],sha256=sha(blob[r['start']:r['end']])) for r in reader.root_spans]
    return dict(geometry=geometry,original_payload_spans=spans,typed_root_spans=typed,
                shared_schema_decode=dict(fully_consumed_bytes=reader.pos,captured_tree_equal=True,schema_sha256=mesh['schema_sha256']),
                stored_local_aabb=t['m_LocalAABB'],
                scope='Actual static Mesh-local bytes. Shared supplied schema independently decoded by inherited stdlib109 reader, own vertex/index layout. No builtin-ID->primitive assumption, instance transform, particle generator, runtime deformation or render readback.')
