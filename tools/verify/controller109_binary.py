"""Independent stdlib object-payload reader driven by an explicit shared schema.
No UnityPy imports/helpers. Does NOT parse Unity bundle/file headers or infer schema.
"""
import struct
PRIMITIVES={'bool':'B','char':'b','SInt8':'b','UInt8':'B','short':'h','SInt16':'h','UInt16':'H','unsigned short':'H','int':'i','SInt32':'i','UInt32':'I','unsigned int':'I','long long':'q','SInt64':'q','UInt64':'Q','unsigned long long':'Q','float':'f','double':'d'}
class DecodeError(ValueError):pass
class Reader:
 def __init__(self,data,endian='<',max_items=1000000,max_depth=128):
  if endian not in ['<','>']:raise DecodeError('unsupported endian')
  self.data=bytes(data);self.endian=endian;self.pos=0;self.max_items=max_items;self.max_depth=max_depth;self.values=0;self.arrays=0;self.padding=[];self.root_spans=[]
 def take(self,n):
  if n<0 or self.pos+n>len(self.data):raise DecodeError(f'truncated at{self.pos} request{n}')
  p=self.pos;self.pos+=n;return self.data[p:self.pos]
 def scalar(self,fmt):return struct.unpack(self.endian+fmt,self.take(struct.calcsize(fmt)))[0]
 def align(self):
  n=(-self.pos)%4
  if n:
   p=self.pos;b=self.take(n);self.padding.append(dict(offset=p,hex=b.hex()))
 def length(self):
  n=self.scalar('i')
  if n<0 or n>self.max_items:raise DecodeError(f'invalid count{n} at{self.pos-4}')
  return n
 def node(self,s,depth=0):
  if depth>self.max_depth:raise DecodeError('schema nesting budget')
  self.values+=1
  if self.values>self.max_items*16:raise DecodeError('decoded values budget')
  typ=s['type'];children=s['children'];flag=s.get('meta_flag',0)
  if typ in PRIMITIVES:
   if children:raise DecodeError('primitive has children')
   value=self.scalar(PRIMITIVES[typ])
   if typ=='bool':
    if value not in (0,1):raise DecodeError('noncanonical boolean')
    value=bool(value)
  elif typ=='string':
   n=self.length()
   try:value=self.take(n).decode('utf-8')
   except UnicodeDecodeError as e:raise DecodeError('invalid UTF8') from e
   self.align()
  elif typ=='TypelessData':value=list(self.take(self.length()))
  elif typ=='Array':
   if len(children)!=2 or children[0]['name']!='size':raise DecodeError('unsupported Array schema')
   n=self.length();self.arrays+=1;value=[self.node(children[1],depth+1) for _ in range(n)]
  elif len(children)==1 and children[0]['type']=='Array':value=self.node(children[0],depth+1)
  elif typ=='pair':
   if len(children)!=2:raise DecodeError('unsupported pair schema')
   value=[self.node(c,depth+1) for c in children]
  elif children:
   names=[c['name'] for c in children]
   if len(set(names))!=len(names):raise DecodeError('duplicate struct field')
   value={}
   for c in children:
    start=self.pos;value[c['name']]=self.node(c,depth+1)
    if depth==0:self.root_spans.append(dict(field=c['name'],start=start,end=self.pos))
  else:raise DecodeError('unsupported leaf type '+typ)
  if flag&0x4000:self.align()
  return value
 def decode(self,schema):
  value=self.node(schema)
  if self.pos!=len(self.data):raise DecodeError(f'unconsumed bytes{len(self.data)-self.pos} at{self.pos}')
  return value
