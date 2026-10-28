"""Narrow independent SerializedFile v22 metadata reader, stdlib only.
Bundle decompression and original type schema are outside this reader's scope.
Only stripped type-tree files are supported; unsupported layouts fail closed.
"""
import struct
class FormatError(ValueError):pass
class Cursor:
 def __init__(self,b,pos=0,endian='<'):self.b=b;self.pos=pos;self.endian=endian
 def take(self,n):
  if n<0 or self.pos+n>len(self.b):raise FormatError(f'truncated metadata at{self.pos} need{n}')
  p=self.pos;self.pos+=n;return self.b[p:self.pos]
 def value(self,f):return struct.unpack(self.endian+f,self.take(struct.calcsize(f)))[0]
 def count(self):
  n=self.value('i')
  if n<0 or n>2000000:raise FormatError('invalid table count')
  return n
 def string(self):
  end=self.b.find(b'\0',self.pos)
  if end<0:raise FormatError('unterminated string')
  p=self.pos;self.pos=end+1
  try:return self.b[p:end].decode('utf-8')
  except UnicodeDecodeError as e:raise FormatError('invalid UTF8') from e
 def align(self):self.take((-self.pos)%4)
def header(b):
 if len(b)<48:raise FormatError('truncated v22 header')
 legacy_meta,legacy_file,version,legacy_data=struct.unpack_from('>4I',b)
 if version!=22:raise FormatError('only SerializedFile v22 supported')
 if b[16] not in (0,1):raise FormatError('invalid endian marker')
 meta,filesize,data_offset,unknown=struct.unpack_from('>IQQQ',b,20)
 if not 48<=data_offset<=filesize or meta>data_offset:raise FormatError('invalid file extent')
 return dict(version=version,endian='>' if b[16] else '<',metadata_size=meta,file_size=filesize,data_offset=data_offset,unknown=unknown,reserved_hex=b[17:20].hex(),legacy_fields=[legacy_meta,legacy_file,legacy_data],header_size=48)
def parse(prefix):
 h=header(prefix)
 if len(prefix)!=h['data_offset']:raise FormatError('prefix must end exactly at declared data_offset')
 c=Cursor(prefix,48,h['endian']);unity_version=c.string();platform=c.value('i');enabled=c.value('B')
 if enabled!=0:raise FormatError('embedded type tree unsupported; no schema guessing')
 def read_type(ref=False):
  start=c.pos;class_id=c.value('i');stripped=c.value('B');script_index=c.value('h')
  if stripped not in (0,1):raise FormatError('noncanonical stripped flag')
  script_id=c.take(16).hex() if class_id==114 or (ref and script_index>=0) else None
  old_hash=c.take(16).hex()
  return dict(class_id=class_id,is_stripped=bool(stripped),script_type_index=script_index,script_id=script_id,old_type_hash=old_hash,record_start=start,record_end=c.pos)
 types=[read_type() for _ in range(c.count())];object_count=c.count();objects=[];ids=set()
 for _ in range(object_count):
  c.align();start=c.pos;path_id=c.value('q');relative_start=c.value('q');size=c.value('I');type_index=c.value('i')
  if path_id in ids:raise FormatError('duplicate path ID')
  if not 0<=type_index<len(types):raise FormatError('invalid object type index')
  absolute=h['data_offset']+relative_start
  if relative_start<0 or absolute+size>h['file_size']:raise FormatError('object outside file bounds')
  ids.add(path_id);objects.append(dict(path_id=path_id,type_id=type_index,class_id=types[type_index]['class_id'],byte_start=absolute,byte_size=size,record_start=start,record_end=c.pos))
 scripts=[]
 for _ in range(c.count()):
  file_index=c.value('i');c.align();identifier=c.value('q');scripts.append(dict(file_index=file_index,path_id=identifier))
 externals=[]
 for _ in range(c.count()):externals.append(dict(empty=c.string(),guid=c.take(16).hex(),type=c.value('i'),path=c.string()))
 ref_types=[read_type(True) for _ in range(c.count())];user=c.string();end=c.pos
 if end!=48+h['metadata_size']:raise FormatError('declared metadata_size does not match parsed end')
 return dict(header=h,unity_version=unity_version,target_platform=platform,embedded_type_tree=False,types=types,objects=objects,scripts=scripts,externals=externals,ref_types=ref_types,user_information=user,metadata_end=end,prefix_padding_hex=prefix[end:].hex())
