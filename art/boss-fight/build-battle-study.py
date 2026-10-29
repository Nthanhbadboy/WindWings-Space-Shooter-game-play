#!/usr/bin/env python3
"""Deterministic art-only battle study, not engine logic or gameplay QA.
Run from repo root with Pillow and numpy available.
"""
from PIL import Image
from pathlib import Path
import math,json
P=Path('art/boss-fight'); E=P/'exports'; O=E/'battle-study'; O.mkdir(exist_ok=True,parents=True)
W,H=240,350; FPS=20; DURATION=31.5
background=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA')
L={n:Image.open(E/'boss-layers'/f'{n}.png').convert('RGBA') for n in ('hull','pod_left','pod_right','core','cannon')}
T={f'{s}_{p}':Image.open(E/'turret-pivot-tests'/f'{s}-{p}.png').convert('RGBA') for s in ('left','right') for p in ('base','head')}
F={n:Image.open(E/'effects'/f'{n}.png').convert('RGBA') for n in ('energy','laser_bullet','missile','missile_trail','target_reticle','beam-strip','beam_warning','charge','core_overload','muzzle','shockwave','armor_impact')}
F.update({n:Image.open(E/'cinematic'/f'{n}.png').convert('RGBA') for n in ('turret_blast','pod_fire','arc','main_blast','debris','smoke','beacon')})
# Distinguish enemy projectiles from player fire; preserve generated texture/alpha.
def warm(img):
 r,g,b,a=img.split(); return Image.merge('RGBA',(b.point(lambda x:min(255,round(x*1.05))),g.point(lambda x:round(x*.48)),r.point(lambda x:round(x*.14)),a))
for n in ('energy','laser_bullet','beam-strip'):
 F['enemy_'+n]=warm(F[n])
O2=Image.open(E/'A6/damage-level2.png').convert('RGBA');O3=Image.open(E/'A6/damage-level3.png').convert('RGBA')

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
 # No jumps when reticle starts or ends; smoothly leave locked position.
 def path(u):return 120+65*math.sin(u*.7),294+3*math.sin(u*1.6)
 if t<11.3:return path(t)
 start=path(11.3)
 if t<13.4:
  q=(t-11.3)/2.1;return start[0]-65*q,start[1]+(294-start[1])*q
 if t<14:
  q=(t-13.4)/.6;target=path(t);return (start[0]-65)*(1-q)+target[0]*q,294*(1-q)+target[1]*q
 return path(t)
def hp(t):
 if t<7.2:return 1.0
 if t<18.2:return .65
 if t<24:return .25
 if t<27:return .1
 return 0
# Missile lock samples exactly player position at end of 0.8s tracking.
lock=player_pos(11.3)
def beam(im,x,y,angle,warning=False):
 asset=F['beam_warning' if warning else 'enemy_beam-strip'].resize((4 if warning else 10,270),Image.Resampling.LANCZOS)
 rad=math.radians(angle);put(im,asset,x+math.sin(rad)*135,y+48+math.cos(rad)*135,angle=angle)
frames=[]
for i in range(round(FPS*DURATION)):
 t=i/FPS; bx,by=bxby(t); px,py=player_pos(t); im=background.copy();health=hp(t)
 dying=t>=27; death=t-27
 if t<29.75:
  boss=Image.new('RGBA',(512,512))
  for n in ('hull','pod_left','pod_right','core','cannon'):
   if n=='pod_right' and death>=1.3:continue
   boss.alpha_composite(L[n])
  if health<=.25 and health>0:boss.alpha_composite(O3 if health<.15 else O2)
  for side,x in [('left',144),('right',368)]:
   if side=='left' and death>=.65:continue
   base=T[side+'_base'];head=T[side+'_head']; boss.alpha_composite(base,(x-256,210-256))
   ang=0 if t<1.5 else 12*math.sin(t*2)*(1 if side=='left' else -1)
   boss.alpha_composite(head.rotate(ang,Image.Resampling.BICUBIC,center=(256,256)),(x-256,210-256))
  opacity=1 if t<29.2 else max(0,1-(t-29.2)/.55)
  put(im,boss,bx,by,.31,opacity=opacity)
 # Visual transition: 70% phase change, not overload.
 if 7.2<=t<7.7:put(im,F['charge'],bx,by,.35,opacity=.85)
 if 0<health<.15:put(im,F['core_overload'],bx,by-8,.24,opacity=.5+.35*abs(math.sin(t*8)))
 warning=(1.5<=t<2.4 or 7.7<=t<8.5 or 18.7<=t<19.5)
 if warning:put(im,F['charge'],bx,by,.34,opacity=.6)
 # shots: paired turrets each use 3-shot timing from director; no hitbox claim.
 for start,interval,kind in [(2.4,.6,'energy'),(8.5,.6,'laser_bullet'),(19.5,.6/1.3,'laser_bullet')]:
  for j in range(3):
   age=t-(start+j*interval)
   if 0<=age<1.15:
    for side in (-1,1):
     sx=bx+side*35; sy=by+15
     drift=math.tan(math.radians(side*6))*age*130 if start==19.5 else side*8*age
     put(im,F['enemy_'+kind],sx+drift,sy+age*130,.20)
     if age<.12:put(im,F['muzzle'],sx,sy,.14)
 # Reticle follows exact player then freezes at lock coordinate.
 if 10.5<=t<11.3:put(im,F['target_reticle'],px,py,.16)
 if 11.3<=t<11.65:put(im,F['target_reticle'],*lock,.16)
 for j in range(4):
  age=t-(11.3+j*.18)
  if 0<=age<1.6:
   for side in (-1,1):
    q=age/1.6;sx=bx+side*58;sy=by+10;x=sx+(lock[0]-sx)*q;y=sy+(lock[1]-sy)*q
    angle=math.degrees(math.atan2(-(lock[0]-sx),lock[1]-sy));put(im,F['missile_trail'],x,y-8,.12,angle,opacity=.7);put(im,F['missile'],x,y,.22,angle)
 # Red warning art precedes each beam; fixed timing/angles as stated in Book.
 for a,b in [(14.3,15.5),(21.6,22.8)]:
  if a<=t<b:
   beam(im,bx,by,-25,True);put(im,F['charge'],bx,by,.42,opacity=.8)
   for x in (8,232):
    for y in (80,170,255):put(im,F['beacon'],x,y,.18,opacity=1)
 if 15.5<=t<17.4:beam(im,bx,by,-25+50*(t-15.5)/1.9)
 if 22.8<=t<24.7:beam(im,bx,by,-25+50*(t-22.8)/1.9)
 if 24.7<=t<26.6:beam(im,bx,by,25-50*(t-24.7)/1.9)
 # visible player impacts illustrate HP transitions; staged, not simulated damage
 for hit in (7.2,12,15,18.2,24,27):
  if hit-.65<=t<hit:
   q=(t-hit+.65)/.65;x=px+(bx-px)*q;y=py+(by-12-py)*q;put(im,F['laser_bullet'],x,y,.12)
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
 if not 28.9<=t<29.2:put(im,player,px,py,.07)
 if 28.9<=t<29.2:im=Image.new('RGBA',(W,H),(255,255,255,255))
 frames.append(im.convert('RGB'))
# Exact 20 fps timing; 0.3 second flash is 6 frames before GIF deduplication.
delays=[50 for i in range(len(frames))]
palette_source=Image.new('RGB',(W*6,H*5))
for j,t in enumerate([0,1.5,2.4,4,6,7.2,8.5,10.7,11.3,12,14.3,15.5,16.45,17.4,18.2,19.5,21.6,22.8,23.75,24.7,25.65,26.6,27,27.7,28.4,28.95,29.25,29.8,30.5,31.25]):
 palette_source.paste(frames[min(len(frames)-1,round(t*FPS))],((j%6)*W,(j//6)*H))
palette=palette_source.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
q=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
q[0].save(O/'battle-study.gif',save_all=True,append_images=q[1:],duration=delays,loop=0,optimize=True,disposal=1)
times=[0,1.5,2.4,4,6,7.2,8.5,10.7,11.3,12,14.3,15.5,16.45,17.4,18.2,19.5,21.6,22.8,23.75,24.7,25.65,26.6,27,27.7,28.4,28.95,29.25,29.8,30.5,31.25]
board=Image.new('RGB',(W*6,H*5))
for j,t in enumerate(times):board.paste(frames[min(len(frames)-1,round(t*FPS))],((j%6)*W,(j//6)*H))
board.save(O/'battle-study-sheet.jpg',quality=90)
meta={'status':'DRAFT_NOT_APPROVED_NOT_RUNTIME','fps':FPS,'frames':len(frames),'duration_ms':sum(delays),'events':{'entry':[0,1.5],'advance':[4,6],'phase70':[7.2,7.7],'missile_track':[10.5,11.3],'missile_launch':[11.3,11.48,11.66,11.84],'lock_position':lock,'beam_charge':[14.3,15.5],'beam_sweep':[15.5,17.4,-25,25],'panic':18.2,'panic_shots':[19.5,19.5+.6/1.3,19.5+1.2/1.3],'final_charge':[21.6,22.8],'final_sweeps':[[22.8,24.7,-25,25],[24.7,26.6,25,-25]],'hp_below_15':24,'death':[27,31.3]},'limitations':['Timings are staged illustration, not game logic.','Frame quantization; events not always on frame boundary.','No hitbox/speed/damage/clear validation or proof of dodge.','Damage overlays are candidates, not production.','Full-screen white flash requires accessibility review.']}
(O/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print('frames',len(frames),'duration_ms',sum(delays))
