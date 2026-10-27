"""Separately implemented narrow UnityFS reader. Layout consulted UnityPy, not clean-room.
No UnityPy or third-party codec imports. Supports modern 2022 v6/v7/v8, none/LZ4.
"""
import struct

class FormatError(ValueError): pass

def require(ok, message):
    if not ok: raise FormatError(message)

class Cursor:
    def __init__(self, data): self.data=data; self.pos=0
    def take(self,n):
        require(n>=0 and self.pos+n<=len(self.data),'truncated input')
        b=self.data[self.pos:self.pos+n]; self.pos+=n; return b
    def number(self,fmt): return struct.unpack('>'+fmt,self.take(struct.calcsize('>'+fmt)))[0]
    def string(self):
        end=self.data.find(b'\0',self.pos); require(end>=self.pos and end-self.pos<=4096,'unterminated string')
        try: return self.take(end-self.pos+1)[:-1].decode('utf-8')
        except UnicodeDecodeError as e: raise FormatError('invalid UTF-8') from e

def lz4(data,expected):
    require(0<=expected<=128*1024*1024,'output budget')
    c=Cursor(data); out=bytearray()
    def length(n):
        if n==15:
            while True:
                x=c.take(1)[0]; n+=x
                require(n<=expected,'length budget')
                if x!=255: break
        return n
    while c.pos<len(data):
        token=c.take(1)[0]; literals=length(token>>4)
        require(len(out)+literals<=expected,'literal output overflow'); out.extend(c.take(literals))
        if c.pos==len(data): break
        distance=int.from_bytes(c.take(2),'little'); require(0<distance<=len(out),'invalid match distance')
        count=length(token&15)+4; require(len(out)+count<=expected,'match output overflow')
        pattern=out[len(out)-distance:len(out)-distance+min(distance,count)]; out.extend((pattern*((count+distance-1)//distance))[:count])
    require(len(out)==expected,'decompressed size mismatch'); return bytes(out)

def decode(data,flags,expected):
    require(flags & ~0x7f == 0,'unsupported block flags')
    codec=flags&63
    if codec==0:
        require(len(data)==expected,'uncompressed size mismatch'); return bytes(data)
    require(codec in (2,3),'unsupported compression (only none/LZ4/LZ4HC)')
    return lz4(data,expected)

def framing(blob):
    c=Cursor(blob); require(c.string()=='UnityFS','signature'); version=c.number('I'); require(version in (6,7,8),f'format version {version}')
    player=c.string(); engine=c.string(); require(engine.startswith('2022.3.'),'unsupported engine alignment rules')
    size=c.number('q'); compressed=c.number('I'); expanded=c.number('I'); flags=c.number('I')
    require(size==len(blob),'physical bundle size'); require(flags & ~0x2ff == 0 and not flags&0x100,'unsupported/encrypted flags')
    require(flags&0x40,'separate directory unsupported'); require(expanded<=64*1024*1024,'info output budget')
    header_end=c.pos; start=(c.pos+15)//16*16 if version>=7 else c.pos
    info_start=size-compressed if flags&0x80 else start; info_end=info_start+compressed
    require(start<=info_start<=info_end<=size,'info bounds')
    info=decode(blob[info_start:info_end],flags&63,expanded); r=Cursor(info); data_hash=r.take(16).hex()
    count=r.number('i'); require(0<=count<=1000000,'block count'); blocks=[]; physical=start if flags&0x80 else info_end
    if flags&0x200: physical=(physical+15)//16*16
    data_start=physical; logical=0
    for i in range(count):
        raw=r.number('I'); packed=r.number('I'); mode=r.number('H'); require(raw<=128*1024*1024 and packed>0,'block budget')
        blocks.append(dict(index=i,physical_start=physical,compressed_size=packed,uncompressed_start=logical,uncompressed_size=raw,flags=mode)); physical+=packed; logical+=raw
    require(physical==(info_start if flags&0x80 else size),'block payload consumption')
    count=r.number('i'); require(0<=count<=1000000,'node count'); nodes=[]; names=set()
    for _ in range(count):
        offset=r.number('q'); length=r.number('q'); nodeflags=r.number('I'); path=r.string()
        require(path and not path.startswith('/') and '\\' not in path and all(p not in ('','..','.') for p in path.split('/')),'unsafe node path')
        require(path not in names,'duplicate node path'); names.add(path)
        require(0<=offset<=offset+length<=logical,'node bounds'); nodes.append(dict(path=path,offset=offset,size=length,flags=nodeflags))
    require(r.pos==len(info),'info trailing bytes')
    ranges=sorted((n['offset'],n['offset']+n['size']) for n in nodes if n['size']); require(all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:])),'overlapping nodes')
    return dict(version=version,player=player,engine=engine,size=size,flags=flags,header_end=header_end,info_start=info_start,info_size=compressed,info_uncompressed_size=expanded,data_start=data_start,data_hash_literal=data_hash,uncompressed_size=logical,blocks=blocks,nodes=nodes)

def block_bytes(blob,block):
    p=block['physical_start']; return decode(blob[p:p+block['compressed_size']],block['flags'],block['uncompressed_size'])

def read_range(blob,frame,offset,size):
    require(0<=offset<=offset+size<=frame['uncompressed_size'],'range bounds'); out=[]
    for b in frame['blocks']:
        a=b['uncompressed_start']; z=a+b['uncompressed_size']
        if offset<z and a<offset+size:
            data=block_bytes(blob,b); out.append(data[max(offset-a,0):min(offset+size-a,len(data))])
    result=b''.join(out); require(len(result)==size,'range consumption'); return result
