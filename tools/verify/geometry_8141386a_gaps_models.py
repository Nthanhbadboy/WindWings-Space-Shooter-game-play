"""Small explicit supplied C#/native schemas for #8, not managed SDK expansion.
provenance: arena/8141386a-windwings-space-shooter-game-p
C# field declarations/SerializeField + base-to-derived Unity serialization conventions;
C# memory offsets NEVER become serialized offsets. Native templates consulted from
UnityPy1.25.4 TPK. Strict original-byte decode/inverse validation is separate.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import gzip
import json
import re
from tools.verify.geometry_8141386a_atlas_io import ROOT,BRANCH,canonical,sha,sha_file
from tools.verify.geometry_8141386a_gaps_sources import RAW

MODEL=RAW/'explicit-schema-models.json.gz'
DUMP=ROOT/'reverse-engineering/il2cpp/dump.cs.gz'


def node(typ,name,children=(),flag=0):
    return dict(type=typ,name=name,byte_size=-1,meta_flag=flag,children=list(children))


def pointer(name,typ='Object'):
    return node('PPtr<'+typ+'>',name,[node('int','m_FileID'),node('SInt64','m_PathID')])


def array(name,element):
    return node('vector',name,[node('Array','Array',[node('int','size'),element])],0x4000)


def csharp_index():
    result={};ns='';active=None;level=0;opened=False
    with gzip.open(DUMP,'rt') as h:
        for i,line in enumerate(h,1):
            if line.startswith('// Namespace:'):ns=line.split(':',1)[1].strip()
            if active is None:
                m=re.search(r'\b(class|struct|enum) ([^\s:]+)(?:\s*:\s*([^/]+))?',line)
                if m and '// TypeDefIndex:' in line:
                    active=dict(kind=m[1],name=m[2],namespace=ns,base=(m[3] or '').strip().split(',')[0].strip(),first_line=i,lines=[]);level=0;opened=False
            if active:
                active['lines'].append(line);level+=line.count('{')-line.count('}');opened=opened or '{'in line
                if opened and level==0:
                    text=''.join(active.pop('lines'));active.update(text=text,text_sha256=sha(text.encode()),last_line=i)
                    result[(active['namespace'],active['name'])]=active;active=None
    return result


def declared_fields(decl):
    active=False;attrs=[];out=[]
    for line in decl['text'].splitlines():
        if '// Fields' in line:active=True;continue
        if '// Properties' in line or '// Methods' in line:break
        if not active:continue
        if line.strip().startswith('['):attrs.append(line.strip());continue
        m=re.match(r'\s*(public|private|protected|internal)\s+(.+?)\s+(\S+)\s*;\s*// 0x[0-9A-Fa-f]+',line)
        if m:
            access,typ,name=m.groups();flags=' '.join(attrs);attrs=[]
            if any(x in typ.split() for x in ('static','const','readonly')) or 'NonSerialized' in flags:continue
            if 'SerializeReference' in flags:raise ValueError('managed-reference registry unsupported')
            if access!='public' and 'SerializeField' not in flags:continue
            out.append(dict(name=name,type=typ,attributes=flags))
    return out


class Schemas:
    def __init__(self,index,templates):self.index=index;self.templates=templates;self.used={};self.stack=[]
    def resolve(self,name,ns):
        name=name.strip()
        parts=ns.split('.') if ns else []
        for n in range(len(parts),-1,-1):
            exact=('.'.join(parts[:n]),name)
            if exact in self.index:return exact
        possible=[k for k in self.index if k[1]==name or (k[0]+'.'+k[1])==name]
        if len(possible)!=1:raise ValueError('C# type missing/ambiguous: '+ns+'.'+name+' '+str(possible[:8]))
        return possible[0]
    def decl(self,key):self.used[key]=self.index[key];return self.index[key]
    def unity_object(self,key,seen=None):
        if key[0]=='UnityEngine' and key[1]in ('Object','Component','Behaviour','MonoBehaviour','ScriptableObject'):return True
        seen=set() if seen is None else seen
        if key in seen:raise ValueError('C# base-type cycle')
        d=self.decl(key);base=d['base']
        if not base:return False
        try:p=self.resolve(base,d['namespace'])
        except ValueError:return False
        return self.unity_object(p,seen|{key})
    def fields(self,key):
        d=self.decl(key);out=[];base=d['base']
        if base and base not in ('MonoBehaviour','Object','ValueType','Enum') and not base.startswith('I'):
            try:parent=self.resolve(base,d['namespace'])
            except ValueError:raise ValueError('unresolved serialized base '+base)
            out.extend(self.fields(parent))
        for f in declared_fields(d):out.append(self.type(f['type'],f['name'],d['namespace']))
        return out
    def type(self,typ,name,ns,in_array=False):
        if typ.endswith('[]'):
            return array(name,self.type(typ[:-2],'data',ns,True))
        if typ.startswith('List<') and typ.endswith('>'):
            return array(name,self.type(typ[5:-1],'data',ns,True))
        primitives={'int':'int','float':'float','bool':'bool','string':'string','uint':'UInt32','short':'SInt16','ushort':'UInt16','byte':'UInt8','sbyte':'SInt8','long':'SInt64','ulong':'UInt64','double':'double'}
        if typ in primitives:return node(primitives[typ],name,flag=0x4000 if typ in ('bool','byte','sbyte','short','ushort') and not in_array else 0)
        vectors={'Vector2':('x','y'),'Vector3':('x','y','z'),'Vector4':('x','y','z','w'),'Quaternion':('x','y','z','w'),'Color':('r','g','b','a')}
        if typ in vectors:return node(typ,name,[node('float',a) for a in vectors[typ]])
        if typ=='LayerMask':return node('LayerMask',name,[node('int','m_Bits')])
        if typ in self.templates:
            t=deepcopy(self.templates[typ]);t['name']=name;return t
        if typ=='UnityEvent' or typ.startswith('UnityEvent<'):
            return node(typ,name,self.fields(('UnityEngine.Events','UnityEventBase')))
        key=self.resolve(typ,ns);d=self.decl(key)
        if d['kind']=='enum':return node('int',name)
        if self.unity_object(key):return pointer(name,typ)
        if key in self.stack:raise ValueError('recursive inline C# field unsupported')
        self.stack.append(key)
        try:children=self.fields(key)
        finally:self.stack.pop()
        if not children:raise ValueError('empty inline type needs explicit serialization contract:'+typ)
        return node(typ,name,children)


def reproduce(w,templates):
    types=csharp_index();builder=Schemas(types,templates);schemas=[]
    for o in w['header_objects']:
        k=(o['namespace'],o['class_name'])
        if any(r['namespace']==k[0] and r['class_name']==k[1] for r in schemas):continue
        try:
            schema=deepcopy(o['native_header_schema']);schema['children']+=builder.fields(k)
            schemas.append(dict(namespace=k[0],class_name=k[1],schema=schema,schema_sha256=sha(canonical(schema)),status='EXPLICIT_SUPPLIED_SCHEMA'))
        except Exception as e:schemas.append(dict(namespace=k[0],class_name=k[1],status='MODEL_SCHEMA_UNSUPPORTED',error=repr(e)))
    return schemas,[builder.used[k] for k in sorted(builder.used)]


def collect():
    # TPK template extraction only; no TypeTreeGeneratorAPI/libil2cpp load here.
    import UnityPy
    from UnityPy.helpers.Tpk import get_typetree_node
    from UnityPy.helpers.UnityVersion import UnityVersion
    from tools.recovery.geometry_8141386a_builtin_bytes import type_schema
    w=json.loads(gzip.decompress((RAW/'byte-witness.json.gz').read_bytes()))
    version=next(f['unity_version'] for f in w['files'] if f['serialized_file']=='data.unity3d/resources.assets')
    candidates={}
    def walk(n):
        if n.m_Type in ('Gradient','AnimationCurve'):
            s=type_schema(n);s['name']='normalized_native_template';candidates.setdefault(n.m_Type,{})[sha(canonical(s))]=s
        for c in n.m_Children:walk(c)
    walk(get_typetree_node(198,UnityVersion.from_str(version)))
    templates={}
    for typ,shapes in candidates.items():
        if len(shapes)!=1:raise ValueError('ambiguous native template shape: '+typ+' '+str(len(shapes)))
        templates[typ]=next(iter(shapes.values()))
    schemas,declarations=reproduce(w,templates)
    paths=['tools/verify/geometry_8141386a_gaps_models.py',str(DUMP.relative_to(ROOT)),str((RAW/'byte-witness.json.gz').relative_to(ROOT))]
    return dict(schema=1,item=8,provenance=BRANCH,UnityPy=UnityPy.__version__,native_template_version=version,native_templates=templates,
                schemas=schemas,csharp_declarations=declarations,source_pins={p:sha_file(ROOT/p) for p in paths},
                scope='Supplied field-order model from C# public/SerializeField declarations + inherited ordering + native TPK templates; no C# memory offsets, SDK budget increase, original field-layout discovery or runtime evidence. Must validate complete original bytes separately.')


def load():
    v=json.loads(gzip.decompress(MODEL.read_bytes()))
    for p,h in v['source_pins'].items():
        if sha_file(ROOT/p)!=h:raise ValueError('explicit model source pin drift:'+p)
    return v


def check():
    v=load();w=json.loads(gzip.decompress((RAW/'byte-witness.json.gz').read_bytes()))
    schemas,declarations=reproduce(w,v['native_templates'])
    if schemas!=v['schemas'] or declarations!=v['csharp_declarations']:raise ValueError('C# supplied schema/declaration reproduction drift')
    print('PASS C#declaration-derived schemas reproduced; native templates remain explicitly supplied, not discovered')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:check()
    else:
        v=collect();MODEL.write_bytes(gzip.compress(canonical(v)+b'\n',mtime=0))
        print([(r['namespace'],r['class_name'],r['status'],r.get('error')) for r in v['schemas']]);print('consulted declarations',len(v['csharp_declarations']))
