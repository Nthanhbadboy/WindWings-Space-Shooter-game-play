#!/usr/bin/env python3
"""Candidate decal extraction: no source pixels from hull are used as decal art."""
from PIL import Image
import numpy as np
from pathlib import Path
P=Path('art/boss-fight'); O=P/'exports'/'A6'; O.mkdir(exist_ok=True,parents=True)
hull=Image.open(P/'exports/boss-bare-hull.png').convert('RGBA')
for n in (2,3):
 src=Image.open(P/f'masters/A6/damage-level{n}.png').convert('RGB'); a=np.asarray(src,dtype=np.float32); value=a.max(2)
 # Black-backed emission; this does not restore opacity of dark soot (unknown).
 alpha=np.clip((value-7)/175,0,1); rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8')
 art=Image.fromarray(np.dstack((rgb,(alpha*255).astype('uint8'))),'RGBA'); art=art.crop(art.getbbox()); art.thumbnail((320,260),Image.Resampling.LANCZOS)
 overlay=Image.new('RGBA',(512,512)); overlay.alpha_composite(art,((512-art.width)//2,(512-art.height)//2))
 oa=np.asarray(overlay).copy(); ha=np.asarray(hull.getchannel('A')); oa[:,:,3]=(oa[:,:,3].astype('uint16')*ha//255).astype('uint8');overlay=Image.fromarray(oa,'RGBA');overlay.save(O/f'damage-level{n}.png')
 composite=hull.copy();composite.alpha_composite(overlay);composite.save(O/f'damage-level{n}-hull.png')
 qa=Image.new('RGB',(1024,512))
 for x,bg in ((0,(240,240,240,255)),(512,(19,25,32,255))):
  im=Image.new('RGBA',(512,512),bg);im.alpha_composite(composite);qa.paste(im.convert('RGB'),(x,0))
 qa.save(O/f'damage-level{n}-light-dark.png')
 print(n,'corners',[int(oa[y,x,3]) for x,y in [(0,0),(511,0),(0,511),(511,511)]],'outside hull',int(np.count_nonzero((oa[:,:,3]>0)&(ha==0))))
