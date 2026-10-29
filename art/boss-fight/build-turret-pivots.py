#!/usr/bin/env python3
"""A4 independent base/head test, art-generated pixels only. Pillow + numpy."""
from PIL import Image, ImageDraw
import numpy as np, json, hashlib
from pathlib import Path
from collections import deque
P=Path(__file__).resolve().parent
D=P/'exports'/'turret-pivot-tests'; D.mkdir(parents=True,exist_ok=True)
# Mechanical hub centers manually measured on full resolution masters.
config={'left': {'base':(688,386),'head':(703,177)},'right':{'base':(704,385),'head':(704,237)}}

def extract(path,center,width):
 im=Image.open(path).convert('RGB'); im.thumbnail((704,384),Image.Resampling.LANCZOS)
 arr=np.asarray(im); v=arr.max(2); h,w=v.shape
 # Flood only edge-connected dark background: no holes inside opaque steel.
 mask=v<=15; seen=np.zeros((h,w),bool); q=deque()
 for x in range(w):
  if mask[0,x]: q.append((0,x))
  if mask[h-1,x]: q.append((h-1,x))
 for y in range(h):
  if mask[y,0]: q.append((y,0))
  if mask[y,w-1]: q.append((y,w-1))
 while q:
  y,x=q.popleft()
  if seen[y,x] or not mask[y,x]: continue
  seen[y,x]=True
  for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=yy<h and 0<=xx<w and not seen[yy,xx] and mask[yy,xx]: q.append((yy,xx))
 rgba=np.dstack((arr, np.where(seen,0,255).astype('uint8'))); out=Image.fromarray(rgba,'RGBA'); bbox=out.getbbox(); crop=out.crop(bbox)
 scale=width/crop.width; crop=crop.resize((width,round(crop.height*scale)),Image.Resampling.LANCZOS)
 # Original dimensions 1408 x 768; thumbnail half. Apply same crop/scale to measured hub.
 cx=(center[0]/2-bbox[0])*scale; cy=(center[1]/2-bbox[1])*scale
 layer=Image.new('RGBA',(512,512)); layer.alpha_composite(crop,(round(256-cx),round(256-cy)))
 return layer,{'source_hub_px':center,'crop_bbox_half_resolution':bbox,'scale_from_half':round(scale,5),'canvas_pivot':[256,256]}
manifest={}
for side,c in config.items():
 base,bm=extract(P/'masters/A4'/f'{side}-base.png',c['base'],150)
 head,hm=extract(P/'masters/A4'/f'{side}-head.png',c['head'],90)
 base.save(D/f'{side}-base.png'); head.save(D/f'{side}-head.png')
 frames=[]
 for i in range(72):
  angle=i*5
  b=Image.new('RGBA',(512,512),(20,27,34,255)); b.alpha_composite(base); b.alpha_composite(head.rotate(-angle,resample=Image.Resampling.BICUBIC,center=(256,256)))
  frames.append(b.convert('RGB').resize((256,256),Image.Resampling.LANCZOS))
 frames[0].save(D/f'{side}-360.gif',save_all=True,append_images=frames[1:],duration=60,loop=0,disposal=2)
 qa=Image.new('RGB',(1024,512))
 for x,col in ((0,(240,240,240,255)),(512,(20,27,34,255))):
  bg=Image.new('RGBA',(512,512),col); bg.alpha_composite(base);bg.alpha_composite(head);qa.paste(bg.convert('RGB'),(x,0))
 qa.save(D/f'{side}-light-dark.png')
 manifest[side]={'base':bm,'head':hm,'base_png_sha256':hashlib.sha256((D/f'{side}-base.png').read_bytes()).hexdigest(),'frame_count':72,'degrees_per_frame':5,'base_transform':'none, same pixels in every frame','warning':'Candidate only: hub manually estimated from art; visual alignment, halo, hull fit and runtime still require QA.'}
(D/'pivot-measurements.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
