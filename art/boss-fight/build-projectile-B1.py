#!/usr/bin/env python3
"""Candidate alpha/pulse layers for newly generated boss projectile masters."""
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json
from pathlib import Path
from collections import deque
P=Path('art/boss-fight');S=P/'masters/bullet-B1';O=P/'exports/bullet-B1';O.mkdir(exist_ok=True,parents=True)
items={'heavy-orb':(64,64),'laser':(64,128),'panic':(64,64),'missile':(64,64),'beam-head':(64,64),'missile-trail':(64,128)}
def extract(name,size):
 im=Image.open(S/f'{name}.png').convert('RGB');im.thumbnail((704,704),Image.Resampling.LANCZOS); a=np.asarray(im,dtype=np.float32);v=a.max(2)
 if name=='missile':
  # Only edge-connected black is background; retain dark metal in missile body.
  bg=v<17; h,w=bg.shape;seen=np.zeros((h,w),bool);q=deque([(0,0),(h-1,0),(0,w-1),(h-1,w-1)])
  while q:
   y,x=q.popleft()
   if seen[y,x] or not bg[y,x]:continue
   seen[y,x]=True
   for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
    if 0<=yy<h and 0<=xx<w and not seen[yy,xx] and bg[yy,xx]:q.append((yy,xx))
  alpha=np.where(seen,0,255).astype('uint8');rgb=a.astype('uint8')
 else:
  alpha=np.clip((v-12)/170,0,1);rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');alpha=(alpha*255).astype('uint8')
 layer=Image.fromarray(np.dstack((rgb,alpha)),'RGBA');box=layer.getbbox();layer=layer.crop(box);layer.thumbnail((size[0]-8,size[1]-8),Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.alpha_composite(layer,((size[0]-layer.width)//2,(size[1]-layer.height)//2));return out
meta={}
for name,size in items.items():
 d=O/name;d.mkdir(exist_ok=True);art=extract(name,size);art.save(d/'body.png')
 if name!='missile-trail':
  # Separate additional glow layer, pulsing alpha 3 levels; original art still retains source glow.
  glow=art.copy();glow.putalpha(art.getchannel('A').filter(ImageFilter.GaussianBlur(4)))
  for i,m in enumerate((.35,.65,1.0)):
   g=glow.copy();g.putalpha(glow.getchannel('A').point(lambda a:round(a*m)));g.save(d/f'glow-{i}.png')
 # Simple checker against light and dark, one pixel-perfect display per side.
 panel=Image.new('RGBA',(size[0]*2,size[1]),(240,240,240,255));panel.alpha_composite(art,(0,0));dark=Image.new('RGBA',size,(19,25,32,255));dark.alpha_composite(art);panel.alpha_composite(dark,(size[0],0));panel.resize((size[0]*8,size[1]*4),Image.Resampling.NEAREST).convert('RGB').save(d/'light-dark.png')
 meta[name]={'canvas':size,'core':'body.png','glows':['glow-0.png','glow-1.png','glow-2.png'] if name!='missile-trail' else [],'status':'DRAFT source glow remains in body; inspect halo and readability'}
# Existing generated beam strip goes edge to edge. It is only a candidate: seams not fixed.
im=Image.open(S/'beam-strip.png').convert('RGB').resize((64,128),Image.Resampling.LANCZOS);a=np.asarray(im,dtype=np.float32);v=a.max(2);alpha=np.clip((v-8)/170,0,1);rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');out=Image.fromarray(np.dstack((rgb,(alpha*255).astype('uint8'))),'RGBA');d=O/'beam-strip';d.mkdir(exist_ok=True);out.save(d/'body.png');meta['beam-strip']={'canvas':[64,128],'core':'body.png','status':'DRAFT, tile endpoints unmatched and no glow frames'}
# Screen-size proposal: 240x350 composition, PLAYER drawn 18px = 1.4 units.
# Collider 0.3 unit diameter corresponds to approx 3.86px; artwork can be larger.
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((240,350),Image.Resampling.LANCZOS);player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((18,18),Image.Resampling.LANCZOS);bg.alpha_composite(player,(111,276));draw=ImageDraw.Draw(bg)
for name,x,y,wh in [('heavy-orb',40,90,(15,15)),('laser',88,90,(8,20)),('panic',145,90,(8,8)),('missile',196,90,(10,18)),('beam-head',64,180,(16,16))]:
 art=Image.open(O/name/'body.png').convert('RGBA').resize(wh,Image.Resampling.LANCZOS);bg.alpha_composite(art,(x-wh[0]//2,y-wh[1]//2));draw.text((x-15,y+23),{'heavy-orb':'HEAVY','laser':'LASER','panic':'FAN','missile':'MISSILE','beam-head':'BEAM'}[name],fill='white')
beam=Image.open(O/'beam-strip/body.png').resize((8,95),Image.Resampling.LANCZOS);bg.alpha_composite(beam,(60,185));bg.save(O/'projectile-real-size-study.png')
(O/'manifest.json').write_text(json.dumps({'status':'DRAFT_NOT_QA','display_proposal':'player 18px / 1.4 units, 240x350; art widths are proposed not runtime-calibrated','collision_unit_radius':.15,'assets':meta,'limitations':['Generated light is partly baked into body; separate glow layer is additive, not clean split.','Beam tile endpoints do not yet match.','Smoke extraction loses dark smoke on black.','No engine or actual-size calibration.']},indent=2)+'\n')
