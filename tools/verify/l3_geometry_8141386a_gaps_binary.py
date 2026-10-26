"""#8 strict complete decode + inverse bytes under explicitly supplied schemas.
provenance: arena/8141386a-windwings-space-shooter-game-p
No UnityPy/managed SDK/runtime. Supplied-schema roundtrip is corroboration,
NOT independent field-layout discovery or proof of native consumer execution.
"""
from __future__ import annotations
import math
import struct
from tools.verify.controller109_binary import Reader,PRIMITIVES
from tools.verify.geometry_8141386a_atlas_io import sha,canonical
from tools.verify.l3_geometry_8141386a_gaps_header import header


def encode(schema,value):
    out=bytearray()
    def align():out.extend(b'\0'*(-len(out)%4))
    def put(s,v):
        typ=s['type'];children=s['children']
        if typ in PRIMITIVES:
            if typ in ('float','double') and not math.isfinite(v):raise ValueError('nonfinite supplied-model scalar')
            out.extend(struct.pack('<'+PRIMITIVES[typ],v))
        elif typ=='string':
            b=v.encode('utf8');out.extend(struct.pack('<i',len(b)));out.extend(b);align()
        elif typ=='TypelessData':out.extend(struct.pack('<i',len(v)));out.extend(bytes(v))
        elif typ=='Array':
            out.extend(struct.pack('<i',len(v)))
            for a in v:put(children[1],a)
        elif len(children)==1 and children[0]['type']=='Array':put(children[0],v)
        elif typ=='pair':
            for c,a in zip(children,v):put(c,a)
        elif children:
            if set(v)!={c['name'] for c in children}:raise ValueError('supplied model struct field set mismatch')
            for c in children:put(c,v[c['name']])
        else:raise ValueError('unsupported supplied-model leaf:'+typ)
        if s.get('meta_flag',0)&0x4000:align()
    put(schema,value)
    return bytes(out)


def decode_object(original,model):
    if model['status']!='EXPLICIT_SUPPLIED_SCHEMA':raise ValueError('no supplied schema for this class')
    schema=model['schema'];blob=bytes.fromhex(original['original_hex'])
    if sha(canonical(schema))!=model['schema_sha256']:raise ValueError('supplied schema SHA drift')
    if len(blob)!=original['entry']['byte_size'] or sha(blob)!=original['object_sha256']:raise ValueError('original MB size/hash mismatch')
    reader=Reader(blob,max_items=10000);tree=reader.decode(schema)
    native=header(blob)
    if any(tree[k]!=v for k,v in native['fields'].items()):raise ValueError('modeled fields disagree with independent native header')
    inverse=encode(schema,tree)
    if inverse!=blob:raise ValueError('supplied-model inverse is not whole original-byte equal')
    spans=[dict(field=s['field'],offset=s['start'],size=s['end']-s['start'],sha256=sha(blob[s['start']:s['end']])) for s in reader.root_spans]
    return dict(identity=original['identity'],class_name=original['class_name'],namespace=original['namespace'],
                status='FULL_BYTE_ROUNDTRIP_EXPLICIT_CSHARP_NATIVE_SCHEMA_MODEL_NOT_ENGINE_SCHEMA_DISCOVERY',
                object_sha256=sha(blob),object_size=len(blob),fully_consumed_bytes=reader.pos,inverse_byte_equal=True,
                supplied_schema_sha256=model['schema_sha256'],native_header_end=native['header_end'],custom_payload_size=native['tail_size'],
                tree=tree,typed_root_spans=spans,padding=[dict(**p,scope='original alignment bytes; inverse requires canonical zero') for p in reader.padding],
                native_consumer=None,runtime_state=None,
                limit='Field names/order are explicitly supplied from C# serialization conventions/native TPK templates. Full-byte equality is not independent schema discovery, active state/callback invocation or runtime/render evidence.')
