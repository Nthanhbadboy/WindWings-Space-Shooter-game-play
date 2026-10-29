#!/usr/bin/env python3
"""Build candidate boss projectile cores + separate glow layers from generated masters."""
from PIL import Image,ImageFilter,ImageDraw
from pathlib import Path
from collections import deque
import numpy as np,json,hashlib
P=Path('art/boss-fight');O=P/'exports/bullet-B2';O.mkdir(parents=True,exist_ok=True)
sources={'heavy-orb':('bullet-B2/heavy-orb.png',(64,64)),'laser':('bullet-B2/laser.png',(64,128)),'panic':('bullet-B2/panic.png',(64,64)),'missile':('bullet-B3/missile.png',(64,64)),'beam-head':('bullet-B1/beam-head.png',(64,64)),'missile-trail':('bullet-B1/missile-trail.png',(64,128))}
def extract(path,size,solid=False):
 im=Image.open(path).convert('RGB')
 if solid:
  # Preserve bright neutral collision core; remap saturated orange armour toward red.
  hsv=np.array(im.convert('HSV')); sel=(hsv[:,:,1]>70)&(hsv[:,:,0]<35);hsv[:,:,0][sel]=2;im=Image.fromarray(hsv,'HSV').convert('RGB')
 im.thumbnail((704,704),Image.Resampling.LANCZOS);a=np.asarray(im,dtype=np.float32);v=a.max(2)
 if solid:
  bg=v<17;h,w=bg.shape;seen=np.zeros((h,w),bool);q=deque([(0,0),(h-1,0),(0,w-1),(h-1,w-1)])
  while q:
   y,x=q.popleft()
   if seen[y,x] or not bg[y,x]:continue
   seen[y,x]=True
   for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
    if 0<=yy<h and 0<=xx<w and not seen[yy,xx] and bg[yy,xx]:q.append((yy,xx))
  alpha=np.where(seen,0,255).astype('uint8');rgb=a.astype('uint8')
 else:
  scale=105 if path.name=='missile-trail.png' else 200
  alpha=np.clip((v-5)/scale,0,1);rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');alpha=(alpha*255).astype('uint8')
 layer=Image.fromarray(np.dstack((rgb,alpha)),'RGBA');layer=layer.crop(layer.getbbox());layer.thumbnail((size[0]-8,size[1]-8),Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.alpha_composite(layer,((size[0]-layer.width)//2,(size[1]-layer.height)//2));return out

def export(name,art,source):
 d=O/name;d.mkdir(exist_ok=True);aa=np.asarray(art).copy();alpha=aa[:,:,3].astype('float32')
 if name in ('heavy-orb','laser','panic','beam-head','beam-strip'):
  # Separate outer low-alpha corona from core, with a smooth transition band.
  mask=np.clip((alpha-35)/115,0,1);core=aa.copy();core[:,:,3]=(alpha*mask).astype('uint8');gl=aa.copy();gl[:,:,3]=(alpha*(1-mask)).astype('uint8')
  body=Image.fromarray(core,'RGBA');halo=Image.fromarray(gl,'RGBA')
  bloom=body.copy(); bloom.putalpha(body.getchannel('A').filter(ImageFilter.GaussianBlur(3)).point(lambda a:round(a*.8))); halo.alpha_composite(bloom)
 elif name=='missile':
  body=art; halo=art.copy();halo.putalpha(art.getchannel('A').filter(ImageFilter.GaussianBlur(3)).point(lambda x:round(x*.4)))
 else:body=art;halo=None
 body.save(d/'body.png')
 if halo:
  for i,m in enumerate((.35,.7,1)):
   frame=halo.copy();frame.putalpha(halo.getchannel('A').point(lambda a:round(a*m)));frame.save(d/f'glow-{i}.png')
 panel=Image.new('RGBA',(art.width*2,art.height),(240,240,240,255));dark=Image.new('RGBA',art.size,(19,25,32,255))
 for bg in (panel,dark):
  if halo:bg.alpha_composite(halo,(0,0))
  bg.alpha_composite(body,(0,0))
 panel.alpha_composite(dark,(art.width,0));panel.resize((art.width*8,art.height*4),Image.Resampling.NEAREST).convert('RGB').save(d/'light-dark.png')
 return {'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'canvas':list(art.size),'glow_frames':3 if halo else 0,'status':'candidate'}
meta={}
for name,(src,size) in sources.items():
 source=P/'masters'/src;art=extract(source,size,name=='missile');meta[name]=export(name,art,source)
# Mirror the generated strip vertically into a periodic tile: top/bottom identical.
src=P/'masters/bullet-B1/beam-strip.png';rgb=Image.open(src).convert('RGB');a=np.asarray(rgb);v=a.max(2);coords=np.where(v.max(0)>20)[0];lo=max(0,int(coords[0])-20);hi=min(rgb.width,int(coords[-1])+21)
rgb=rgb.crop((lo,0,hi,rgb.height)).resize((48,64),Image.Resampling.LANCZOS);a=np.asarray(rgb,dtype=np.float32);v=a.max(2);alpha=np.clip((v-10)/200,0,1);c=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');half=Image.fromarray(np.dstack((c,(alpha*255).astype('uint8'))),'RGBA');strip=Image.new('RGBA',(64,128));strip.alpha_composite(half,(8,0));strip.alpha_composite(half.transpose(Image.Transpose.FLIP_TOP_BOTTOM),(8,64));assert strip.crop((0,0,64,1)).tobytes()==strip.crop((0,127,64,128)).tobytes();meta['beam-strip']=export('beam-strip',strip,src)
# UI preview at identical canvas/sprite scales as battle study.
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((240,350),Image.Resampling.LANCZOS);player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((18,18),Image.Resampling.LANCZOS);bg.alpha_composite(player,(111,276));draw=ImageDraw.Draw(bg)
placements=[('heavy-orb',40,90,(16,16)),('laser',89,90,(10,20)),('panic',142,90,(10,10)),('missile',196,90,(18,18)),('beam-head',64,180,(18,18))]
for name,x,y,wh in placements:
 body=Image.open(O/name/'body.png').convert('RGBA');glow=Image.open(O/name/'glow-2.png').convert('RGBA');glow.alpha_composite(body);body=glow.resize(wh,Image.Resampling.LANCZOS);bg.alpha_composite(body,(x-wh[0]//2,y-wh[1]//2))
beam=Image.open(O/'beam-strip/body.png').resize((12,95),Image.Resampling.LANCZOS);bg.alpha_composite(beam,(58,185));bg.save(O/'projectile-real-size-unlabelled.png')
draw=ImageDraw.Draw(bg)
for name,x,y,wh in placements:draw.text((x-15,y+23),{'heavy-orb':'HEAVY','laser':'LASER','panic':'FAN','missile':'MISSILE','beam-head':'BEAM'}[name],fill='white')
bg.save(O/'projectile-real-size-study.png')
# Join missile and separate smoke behind the rear socket for a visual-only registration test.
trail=Image.open(O/'missile-trail/body.png').convert('RGBA').resize((64,128),Image.Resampling.LANCZOS);miss=Image.open(O/'missile/body.png').convert('RGBA');preview=Image.new('RGBA',(128,192));preview.alpha_composite(trail,(32,0));preview.alpha_composite(miss,(32,116));preview.save(O/'missile-tail-test.png')
(O/'manifest.json').write_text(json.dumps({'status':'CANDIDATE_NOT_RUNTIME','items':meta,'pixel_display_example':{'canvas':[240,350],'player_width_px':18,'player_width_unit':1.4,'projectile_art_dimensions':{x[0]:x[3] for x in placements}},'warnings':['Artwork sizes are a staging choice, not actual engine display calibration.','Core-corona split uses alpha luminance estimates and may not cleanly separate all emissive light.','Missile exhaust registration is only visual.','Beam repeating boundary identical; filtering and runtime need coder QA.']},indent=2)+'\n')
