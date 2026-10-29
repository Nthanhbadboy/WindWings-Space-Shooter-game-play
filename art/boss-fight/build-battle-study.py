#!/usr/bin/env python3
"""Deterministic art-only battle study, not engine logic or gameplay QA.
Run from repo root with Pillow and numpy available.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math,json
P=Path('art/boss-fight'); E=P/'exports'; O=E/'battle-study'; O.mkdir(exist_ok=True,parents=True)
W,H=240,350; FPS=20; DURATION=32.0
background=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA')
L={n:Image.open(E/'boss-layers'/f'{n}.png').convert('RGBA') for n in ('hull','pod_left','pod_right','core','cannon')}
T={f'{s}_{p}':Image.open(E/'turret-pivot-tests'/f'{s}-{p}.png').convert('RGBA') for s in ('left','right') for p in ('base','head')}
F={n:Image.open(E/'effects'/f'{n}.png').convert('RGBA') for n in ('energy','laser_bullet','missile','missile_trail','target_reticle','beam-strip','beam_warning','charge','core_overload','muzzle','shockwave','armor_impact')}
F.update({n:Image.open(E/'cinematic'/f'{n}.png').convert('RGBA') for n in ('turret_blast','pod_fire','arc','main_blast','debris','smoke','beacon','missile_impact')})
# Distinguish enemy projectiles from player fire; preserve generated texture/alpha.
def warm(img):
 r,g,b,a=img.split(); return Image.merge('RGBA',(b.point(lambda x:min(255,round(x*1.05))),g.point(lambda x:round(x*.48)),r.point(lambda x:round(x*.14)),a))
for n in ('energy','laser_bullet','beam-strip'):
 F['enemy_'+n]=warm(F[n])
HULL={k:Image.open(E/'hull-variants-B2'/f'hull-{k}.png').convert('RGBA') for k in ('intact','medium','severe')}

NEW={name:{'body':Image.open(E/'bullet-B2'/name/'body.png').convert('RGBA'), 'glow':[Image.open(E/'bullet-B2'/name/f'glow-{i}.png').convert('RGBA') for i in range(3)]} for name in ('heavy-orb','laser','panic','missile','beam-head','beam-strip')}
NEW_TRAIL=Image.open(E/'bullet-B2/missile-trail/body.png').convert('RGBA')
def projectile(name,t):
 item=NEW[name]; level=[0,1,2,1][int(t*6)%4]; im=item['glow'][level].copy();im.alpha_composite(item['body']);return im

def put(dst,img,x,y,scale=1,angle=0,opacity=1):
 if opacity<=0:return
 if scale!=1:img=img.resize((max(1,round(img.width*scale)),max(1,round(img.height*scale))),Image.Resampling.LANCZOS)
 if angle:img=img.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 if opacity<1:
  img=img.copy();img.putalpha(img.getchannel('A').point(lambda a:round(a*opacity)))
 dst.alpha_composite(img,(round(x-img.width/2),round(y-img.height/2)))
def bxby(t):
 if t<1.5:return 120,-50+125*t/1.5
 if 4<=t<6:return 120,75+24*(t-4)/2
 if 6<=t<6.7:return 120,99-24*(t-6)/.7
 return 120,75

def player_pos(t):
 # Deliberate demo path: leave the locked point, then wait outside the beam fan.
 def path(u):
  x,y=120+65*math.sin(u*.7),294+3*math.sin(u*1.6)
  if 9.2<=u<9.8:
   q=(u-9.2)/.6;x=x*(1-q)+205*q
  elif 9.8<=u<=11.3:x=205
  elif 20.2<=u<20.8:
   q=(u-20.2)/.6;x=x*(1-q)+205*q
  elif 20.8<=u<=21.6:x=205
  return x,y
 if t<11.3:return path(t)
 start=path(11.3)
 if t<13.4:
  q=(t-11.3)/2.1;return start[0]-65*q,start[1]+(294-start[1])*q
 if t<14:
  q=(t-13.4)/.6;target=path(t);return (start[0]-65)*(1-q)+target[0]*q,294*(1-q)+target[1]*q
 if t<15.4:
  q=(t-14)/1.4;origin=path(14);return origin[0]*(1-q)+18*q,origin[1]*(1-q)+294*q
 if t<17.4:return 18,294
 if t<18.2:
  q=(t-17.4)/.8;dest=path(18.2);return 18*(1-q)+dest[0]*q,294*(1-q)+dest[1]*q
 if t<21.6:return path(t)
 if t<22.7:
  q=(t-21.6)/1.1;origin=path(21.6);return origin[0]*(1-q)+18*q,origin[1]*(1-q)+294*q
 if t<26.6:return 18,294
 if t<27:
  q=(t-26.6)/.4;dest=path(27);return 18*(1-q)+dest[0]*q,294*(1-q)+dest[1]*q
 return path(t)
HITS=[2.9,3.8,4.7,5.6,6.4,7.2,7.9,8.8,9.8,10.8,11.8,12.8,14.0,16.0,18.2,19.5,22.0,24.0,25.5,27.0]
def hp(t):
 # Staged hit count is only a visual mock, not gameplay damage.
 return round(max(0,1-.05*sum(t+1e-8>=x for x in HITS)),2)
# Missile lock samples exactly player position at end of 0.8s tracking.
lock=player_pos(11.3)
def beam(im,x,y,angle,warning=False,t=0):
 asset=(F['beam_warning'] if warning else projectile('beam-strip',t)).resize((4 if warning else 10,270),Image.Resampling.LANCZOS)
 rad=math.radians(angle);put(im,asset,x+math.sin(rad)*135,y+48+math.cos(rad)*135,angle=angle)
 if not warning:put(im,projectile('beam-head',t),x,y+48,.22)
frames=[]
for i in range(round(FPS*DURATION)):
 t=i/FPS; bx,by=bxby(t); px,py=player_pos(t); im=background.copy();health=hp(t)
 dying=t>=27; death=t-27
 if t<29.75:
  hullstage='intact' if health>=.30 else ('medium' if health>=.15 else 'severe')
  boss=HULL[hullstage].copy()
  for n in ('pod_left','pod_right','core','cannon'):
   if n=='pod_right' and death>=1.3:continue
   part=L[n]
   if n=='core' and t<1.5:
    part=part.copy();part.putalpha(part.getchannel('A').point(lambda a:round(a*min(1,max(0,t/1.5)))))
   boss.alpha_composite(part)
  for side,x in [('left',144),('right',368)]:
   if side=='left' and death>=.65:continue
   base=T[side+'_base'];head=T[side+'_head']; boss.alpha_composite(base,(x-256,210-256))
   ang=0 if t<1.5 else 12*math.sin(t*2)*(1 if side=='left' else -1)
   head=head.rotate(ang,Image.Resampling.BICUBIC,center=(256,256))
   if t<1.5:
    head.putalpha(head.getchannel('A').point(lambda a:round(a*min(1,max(0,(t-(.25 if side=='left' else .55))/.5)))))
   boss.alpha_composite(head,(x-256,210-256))
  opacity=1 if t<29.2 else max(0,1-(t-29.2)/.55)
  put(im,boss,bx,by,.31,opacity=opacity)
 # Visual transition: 70% phase change, not overload.
 if 7.2<=t<7.7:put(im,F['charge'],bx,by,.35,opacity=.85)
 if 0<health<.15:put(im,F['core_overload'],bx,by-8,.24,opacity=.5+.35*abs(math.sin(t*8)))
 warning=(0<=t<2.4 or 7.7<=t<8.5 or 18.7<=t<19.5)
 if warning:put(im,F['charge'],bx,by,.34,opacity=.6)
 # shots: paired turrets each use 3-shot timing from director; no hitbox claim.
 for start,interval,kind in [(2.4,.6,'heavy-orb'),(8.5,.6,'laser'),(19.5,.6/1.3,'panic')]:
  for j in range(3):
   age=t-(start+j*interval)
   if 0<=age<2.0:
    for side in (-1,1):
     shot_time=start+j*interval;shot_bx,shot_by=bxby(shot_time)
     aim=12*math.sin(shot_time*2)*(1 if side==-1 else -1);barrel=125 if side==-1 else 108
     sx=shot_bx+(side*112+math.sin(math.radians(aim))*barrel)*.31
     sy=shot_by+(210-256+math.cos(math.radians(aim))*barrel)*.31
     drift=math.tan(math.radians(side*6))*age*130 if start==19.5 else side*8*age
     put(im,projectile(kind,t),sx+drift,sy+age*130,{'heavy-orb':.25,'laser':.16,'panic':.16}[kind])
     if age<.12:put(im,F['muzzle'],sx,sy,.14)
 # Reticle follows exact player then freezes at lock coordinate.
 if 10.5<=t<11.3:put(im,F['target_reticle'],px,py,.16)
 if 11.3<=t<11.65:put(im,F['target_reticle'],*lock,.16)
 for j in range(4):
  age=t-(11.3+j*.18)
  if 0<=age<1.6:
   for side in (-1,1):
    q=age/1.6;sx=bx+side*58;sy=by+10;x=sx+(lock[0]-sx)*q;y=sy+(lock[1]-sy)*q
    angle=math.degrees(math.atan2(lock[0]-sx,lock[1]-sy));put(im,NEW_TRAIL,x-math.sin(math.radians(angle))*14,y-math.cos(math.radians(angle))*14,.12,angle,opacity=.7);put(im,projectile('missile',t),x,y,.28,angle)
  if 1.6<=age<1.8:put(im,F['missile_impact'],*lock,.13,opacity=max(0,1-(age-1.6)*5))
 # Red warning art precedes each beam; fixed timing/angles as stated in Book.
 for a,b in [(14.3,15.5),(21.6,22.8)]:
  if a<=t<b:
   beam(im,bx,by,-25,True);put(im,F['charge'],bx,by,.42,opacity=.8)
   for x in (8,232):
    for y in (80,170,255):put(im,F['beacon'],x,y,.18,opacity=1)
 if 15.5<=t<17.4:beam(im,bx,by,-25+50*(t-15.5)/1.9,t=t)
 if 22.8<=t<24.7:beam(im,bx,by,-25+50*(t-22.8)/1.9,t=t)
 if 24.7<=t<26.6:beam(im,bx,by,25-50*(t-24.7)/1.9,t=t)
 # visible player impacts illustrate HP transitions; staged, not simulated damage
 for hit in HITS:
  if hit-.65<=t<hit:
   q=(t-hit+.65)/.65;startx,starty=player_pos(hit-.65);x=startx+(bx-startx)*q;y=starty+(by-12-starty)*q;put(im,F['laser_bullet'],x,y,.12)
  if hit<=t<hit+.2:put(im,F['armor_impact'],bx,by-12,.16)
 if dying:
  if death<.95:put(im,F['turret_blast'],bx-35,by-15,.20+death*.08,opacity=min(1,(.95-death)*2))
  if .65<=death<1.9:put(im,F['pod_fire'],bx+58,by-6,.21)
  if 1.3<=death<2.2:put(im,F['arc'],bx,by,.38)
  if 2.2<=death<3.3:
   a=death-2.2;put(im,F['main_blast'],bx,by,.35+a*.35,opacity=max(0,1-a*.75));put(im,F['shockwave'],bx,by,.22+a*.95,opacity=max(0,1-a*.8))
   for j in range(4):
    theta=math.tau*j/4+.4;dist=a*(55+(j%2)*22);put(im,F['debris'],bx+dist*math.cos(theta),by+dist*math.sin(theta),.08,angle=a*(70+j*15),opacity=max(0,1-a*.7))
  if 2.9<=death<4.3:
   a=max(0,death-3.3);fade=min(1,(death-2.9)/.4)*max(0,1-a)
   for j in range(3):put(im,F['smoke'],bx-18+j*18+8*a,by-15*a,.2+.05*a,opacity=fade*.7)
 if not 28.9<=t<29.2:
  put(im,player,px,py,.07)
  # UI-only health display, not generated artwork or simulated runtime.
  draw=ImageDraw.Draw(im);draw.rectangle((36,6,204,12),fill=(6,13,20,220),outline=(171,191,203,255))
  if health>0:draw.rectangle((38,8,38+round(164*health),10),fill=(74,215,207,255) if health>.7 else (255,164,66,255) if health>=.3 else (238,72,61,255))
 if 28.9<=t<29.2:im=Image.new('RGBA',(W,H),(255,255,255,255))
 if t>=31.3:
  draw=ImageDraw.Draw(im);draw.rectangle((55,150,185,178),fill=(10,19,27,230),outline=(95,214,205,255));draw.text((82,159),'MISSION CLEAR',fill=(229,248,246,255))
 frames.append(im.convert('RGB'))
# Exact 20 fps timing; 0.3 second flash is 6 frames before GIF deduplication.
delays=[50 for i in range(len(frames))]
palette_source=Image.new('RGB',(W*6,H*6))
for j,t in enumerate([0,1.5,2.4,4,6,7.2,8.5,10.7,11.3,12,14.3,15.5,16.45,17.4,18.2,19.5,21.6,22.8,23.75,24.7,25.65,26.6,27,27.7,28.4,28.95,29.25,29.8,30.5,31.25]):
 palette_source.paste(frames[min(len(frames)-1,round(t*FPS))],((j%6)*W,(j//6)*H))
# Weight the small projectile colors explicitly, so global GIF palette retains distinct families.
for j,name in enumerate(('heavy-orb','laser','panic','missile','beam-head','beam-strip')):
 sample=projectile(name,0.3).resize((180,180),Image.Resampling.LANCZOS)
 palette_source.paste(sample.convert('RGB'),(j*W,H*5))
palette=palette_source.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
q=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
q[0].save(O/'battle-study.gif',save_all=True,append_images=q[1:],duration=delays,loop=0,optimize=True,disposal=1)
times=[0,1.5,2.4,4,6,7.2,8.5,10.7,11.3,12,14.3,15.5,16.45,17.4,18.2,19.5,21.6,22.8,23.75,24.7,25.65,26.6,27,27.7,28.4,28.95,29.25,29.8,30.5,31.25]
board=Image.new('RGB',(W*6,H*5))
for j,t in enumerate(times):board.paste(frames[min(len(frames)-1,round(t*FPS))],((j%6)*W,(j//6)*H))
board.save(O/'battle-study-sheet.jpg',quality=90)
meta={'status':'ART_READY_FOR_USER_REVIEW_NOT_RUNTIME','fps':FPS,'frames':len(frames),'duration_ms':sum(delays),'events':{'entry':[0,1.5],'advance':[4,6],'phase70':[7.2,7.7],'missile_track':[10.5,11.3],'missile_launch':[11.3,11.48,11.66,11.84],'lock_position':lock,'beam_charge':[14.3,15.5],'beam_sweep':[15.5,17.4,-25,25],'panic':18.2,'panic_shots':[19.5,19.5+.6/1.3,19.5+1.2/1.3],'final_charge':[21.6,22.8],'final_sweeps':[[22.8,24.7,-25,25],[24.7,26.6,25,-25]],'hp_below_15':24,'hp_hit_seconds':HITS,'death':[27,31.3],'mock_result':[31.3,32.0]},'limitations':['Timings are staged illustration, not game logic.','Frame quantization; events not always on frame boundary.','No hitbox/speed/damage/clear validation or proof of dodge.','Whole-hull B2 and bullet B2/B3 are submitted for user review, not yet approved.','Full-screen white flash requires accessibility review.']}
(O/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print('frames',len(frames),'duration_ms',sum(delays))
