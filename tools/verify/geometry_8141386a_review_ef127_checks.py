"""Bounded R1/123 original-word decoder and exact published-text locators.
provenance: arena/8141386a-windwings-space-shooter-game-p
Recognizes only the actual33-witness instruction subset; not a general ARM64
semantic analyzer or a proof of published128/129 native/serialized assertions.
"""
import hashlib
import re
from tools.verify.geometry_8141386a_review_ef123_checks import branch, sign
from tools.verify.geometry_8141386a_atlas_io import sha


def blob_id(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def normalize(text):
    return re.sub(r'\s+','',text.lower())


def decode_word(word,pc):
    b=branch(word,pc)
    if b:
        return dict(kind='BL'if b['link']else'B',target=b['target'],text=('bl 'if b['link']else'b ')+hex(b['target']))
    if word&0x7e000000==0x34000000:
        op='cbnz'if word&(1<<24)else'cbz';width='x'if word&(1<<31)else'w';rt=word&31
        target=pc+sign((word>>5)&0x7ffff,19)*4
        return dict(kind=op.upper(),target=target,register=rt,text=f'{op} {width}{rt},#{hex(target)}')
    if word&0xff000010==0x54000000:
        conditions=('eq','ne','hs','lo','mi','pl','vs','vc','hi','ls','ge','lt','gt','le','al','nv')
        cond=conditions[word&15];target=pc+sign((word>>5)&0x7ffff,19)*4
        return dict(kind='B_COND',condition=cond,target=target,text=f'b.{cond} #{hex(target)}')
    if word&0xfffffc1f in (0xd63f0000,0xd65f0000):
        rn=(word>>5)&31;ret=word&0xfffffc1f==0xd65f0000
        return dict(kind='RET'if ret else'BLR',register=rn,text='ret'if ret and rn==30 else f"{'ret'if ret else'blr'} x{rn}")
    if word&0x3b000000==0x39000000 and not word&0x04000000:
        size=1<<((word>>30)&3);opc=(word>>22)&3;rn=(word>>5)&31;rt=word&31
        if opc not in (0,1):raise ValueError('load/store outside declared unsigned witness subset')
        offset=((word>>10)&4095)*size;op='ldr'if opc else'str'
        if size==1:op+='b'
        elif size==2:op+='h'
        prefix='x'if size==8 else'w';register=prefix+('zr'if rt==31 else str(rt));base='sp'if rn==31 else f'x{rn}'
        return dict(kind='LOAD'if opc else'STORE',width_bytes=size,base_register=rn,register=rt,offset=offset,
                    text=f'{op} {register},[{base},#{hex(offset)}]')
    if word&0xffe0ffe0 in (0xaa0003e0,0x2a0003e0):
        prefix='x'if word&(1<<31)else'w';rd=word&31;rm=(word>>16)&31
        return dict(kind='MOV_REGISTER',register=rd,source_register=rm,text=f'mov {prefix}{rd},{prefix}{rm}')
    raise ValueError('instruction outside declared33-witness decoder subset: '+hex(word))


def quote(pin,text,needle,before=0,after=0):
    lines=text.splitlines(keepends=True);hits=[i for i,l in enumerate(lines)if needle in l]
    if len(hits)!=1:raise ValueError('published-text locator is not unique: '+needle)
    i=hits[0];start=i-before;end=i+after+1
    if start<0 or end>len(lines):raise ValueError('published-text locator outside full snapshot')
    section='DOCUMENT_START'
    for line in lines[:i+1]:
        if line.startswith('#'):section=line.strip()
    body=''.join(lines[start:end])
    return dict(commit=pin['commit'],path=pin['path'],source_sha256=pin['source_sha256'],
        start_line=start+1,end_line=end,section=section,quote=body,quote_sha256=sha(body.encode()),
        evidence_grade='PUBLISHED_TEXT_ONLY_NOT_OWN_NATIVE_OR_SERIALIZED_VERIFICATION',
        url=f"https://github.com/Nthanhbadboy/WindWings-Space-Shooter-game-play/blob/{pin['commit']}/{pin['path']}#L{start+1}-L{end}")
