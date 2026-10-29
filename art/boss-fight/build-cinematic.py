from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math, hashlib, json
from scipy import ndimage
from pathlib import Path
P=Path('art/boss-fight'); E=P/'exports'; (E/'cinematic').mkdir(parents=True,exist_ok=True)
def extract(src,solid=False):
 im=Image.open(src).convert('RGB');a=np.asarray(im).astype('float32');v=a.max(2)
 if solid:
  m=ndimage.binary_closing(v>20,iterations=2);lab,n=ndimage.label(m);cnt=np.bincount(lab.ravel());cnt[0]=0
  m=ndimage.binary_fill_holes(lab==cnt.argmax());m=ndimage.binary_dilation(m,iterations=2);alpha=(m*255).astype('uint8');rgb=a.astype('uint8')
 else:
  alpha=np.clip((v-10)/195,0,1);support=ndimage.binary_dilation(ndimage.binary_opening(v>18,iterations=2),iterations=12);alpha=np.where(support,alpha,0);rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');alpha=(alpha*255).astype('uint8')
 out=Image.fromarray(np.dstack((rgb,alpha)),'RGBA');bbox=out.getbbox()
 if not bbox: raise ValueError('empty artwork '+str(src))
 return out.crop(bbox)
def fx_export(name,source,size=256,solid=False):
 obj=extract(source,solid);obj.thumbnail((size-16,size-16),Image.Resampling.LANCZOS);dst=Image.new('RGBA',(size,size));dst.alpha_composite(obj,((size-obj.width)//2,(size-obj.height)//2));dst.save(E/'cinematic'/f'{name}.png');return dst
root=P/'masters/cinematic';names={'arc':'electric-arc.png','debris':'debris.png','beacon':'wall-warning.png','smoke':'smoke.png','turret_blast':'turret-destruction.png','pod_fire':'pod-fire.png','missile_impact':'missile-impact-redo.png','critical':'core-critical-redo.png','main_blast':'main-blast-redo.png','spark':'ambient-spark.png'}
F={k:fx_export(k,root/v,128 if k in ('debris','beacon','spark') else 256,solid=k in ('debris','beacon')) for k,v in names.items()}
for f in (E/'effects').glob('*.png'):F[f.stem]=Image.open(f).convert('RGBA')
layers={f.stem:Image.open(f).convert('RGBA') for f in (E/'boss-layers').glob('*.png')}; order=['hull','pod_left','pod_right','turret_left','turret_right','core','cannon']
W,H=480,700;bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGB');bg=bg.resize((W,round(bg.height*W/bg.width)),Image.Resampling.LANCZOS);bg=bg.crop((0,(bg.height-H)//2,W,(bg.height+H)//2)).convert('RGBA');player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((34,34),Image.Resampling.LANCZOS)
def place(dst,img,x,y,scale=1,angle=0,opacity=1):
 if opacity<=0:return
 img=img.copy()
 if scale!=1:img=img.resize((max(1,round(img.width*scale)),max(1,round(img.height*scale))),Image.Resampling.LANCZOS)
 if angle:img=img.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if opacity<1:img.putalpha(img.getchannel('A').point(lambda a:round(a*opacity)))
 dst.alpha_composite(img,(round(x-img.width/2),round(y-img.height/2)))
def pulse(t):return .55+.45*abs(math.sin(t*8))
def bosspose(t):
 if t<2:return 240,-120+270*min(1,t/2),0
 if t<7.5:return 240+8*math.sin(t),150+42*math.exp(-((t-3.8)/.8)**2)+38*math.exp(-((t-6.2)/.7)**2),0
 if t<8:return 240,150,0
 if t<15.2:return 240+24*math.sin((t-8)*1.25),150+20*math.sin((t-8)*1.3),(-3 if 8.25<t<9.1 else 0)
 if t<19.2:return 240+18*math.sin(t*1.4)+2.8*math.sin(t*23),158+2.4*math.sin(t*28),(-4 if 17<t<17.6 else 2*math.sin(t*17))
 return 240+1.5*math.sin(t*20),158+1.5*math.sin(t*22),0
def player_at(t,bx,by):
 if 9.1<=t<10.5:
  ang=-24+48*(t-9.1)/1.4; beamx=bx+math.tan(math.radians(ang))*(590-(by+90)); return max(28,min(452,beamx+35)),590
 if 17.6<=t<19.2:
  ang=20-40*(t-17.6)/1.6;beamx=bx+math.tan(math.radians(ang))*(590-(by+90));return max(28,min(452,beamx-35)),590
 return 240+145*math.sin(t*1.17)+20*math.sin(t*3),590+16*math.sin(t*2.2)
def beam(dst,bx,by,ang,opacity=1,warning=False):
 img=F['beam_warning'] if warning else F['beam-strip']; length=510; width=7 if warning else 22;img=img.resize((width,length),Image.Resampling.LANCZOS); x=bx+math.sin(math.radians(ang))*length/2;y=by+90+math.cos(math.radians(ang))*length/2;place(dst,img,x,y,angle=ang,opacity=opacity)
# HP is determined by visible PLAYER impacts: six hits = 70%, fourteen = 30%.
hits=[3.4,4.1,5.0,5.9,6.9,7.5,8.6,9.3,10.1,11.4,12.2,13.1,14.0,14.7,15.2,15.9,16.8,18.0,18.7,19.2]
freeze_times=[2.9,6.6,9.1,13.5,17.6,19.2,21.2,21.5];freeze={round(t*12):t for t in freeze_times};frames=[]
for i in range(288):
 t=i/12; frozen=None
 for first,st in freeze.items():
  if first<=i<first+3:frozen=st;break
 u=frozen if frozen is not None else t
 bx,by,tilt=bosspose(u);px,py=player_at(u,bx,by);hp=max(0,1-.05*sum(u>=x for x in hits));im=bg.copy()
 # Facility beacons track danger; images, not procedurally drawn art.
 danger=.2 if u<2 else (.35 if u<7.5 else .65 if u<15.2 else .95 if u<23 else 0)
 if danger:
  for x in (20,460):
   for y in (165,340,515):place(im,F['beacon'],x,y,.42,opacity=danger*pulse(u))
 # Smoke and embers drift consistently up-right; after 23s only smoke remains.
 if 15.2<=u<24:
  for j in range(4):
   a=(u-15.2+j*.37)%1.8
   if u>=23:a=(u-23+j*.4)%2
   place(im,F['smoke'],bx-35+j*25+22*a,by-30-45*a,.28+.13*a,opacity=max(0,.65-.2*a))
   if u<23:place(im,F['spark'],bx-60+j*38+12*a,by+35+70*a,.08,opacity=max(0,.9-a*.4))
 # Boss layer choreography; sequential activation and anticipation recoil.
 if u<21.5:
  boss=Image.new('RGBA',(512,512));aim=math.sin(u*2)*19 if u>=2 and not 7.5<=u<8 else 0
  for k in order:
   if k=='turret_left' and u>=19.5:continue
   if k=='pod_right' and u>=20.25:continue
   if k in ('turret_left','turret_right'):
    if k=='turret_left':cx,cy=144,210
    else:cx,cy=368,210
    piece=layers[k].crop((cx-90,cy-100,cx+90,cy+100));place(boss,piece,cx,cy,angle=aim if k=='turret_left' else -aim,opacity=min(1,max(0,(u-(.55 if k=='turret_left' else .9))/.35)) if u<2 else 1)
   elif k=='core':
    core_alpha=(min(1,max(0,(u-1.25)/.4)) if u<2 else .32 if 3.6<=u<4.5 or 10.5<=u<11.1 or 13.5<=u<14.2 else 1)
    place(boss,layers[k],256,256,opacity=core_alpha)
   elif k=='cannon':
    recoil=-9 if 8.4<=u<9.1 or 17<=u<17.6 else 6 if 9.1<=u<9.3 or 17.6<=u<17.8 else 0
    place(boss,layers[k],256,256+recoil)
   else:place(boss,layers[k],256,256)
  place(im,boss,bx,by,.62,angle=tilt)
 # All warnings are visually distinct from damaging effects.
 warning=(u<2.9 or 4.5<=u<5.2 or 8<=u<9.1 or 11.1<=u<12 or 14.2<=u<14.6 or 15.2<=u<16 or 17<=u<17.6)
 if warning:place(im,F['charge'],bx,by,.9,opacity=.5+.3*pulse(u))
 if 8<=u<9.1:beam(im,bx,by,-24,opacity=.55,warning=True)
 if 17<=u<17.6:beam(im,bx,by,20,opacity=.6,warning=True)
 # Overloaded core cues change of temperament and panic.
 if 7.5<=u<8.2 or 15.2<=u<19.2:place(im,F['core_overload'],bx,by-30,.5,opacity=.7*pulse(u))
 # Slow heavy shots, then two distinct angry patterns, then inaccurate panic fan.
 schedules=[(2.9,.48,2,'heavy'),(9.1,.24,4,'corner'),(14.6,.30,3,'angry'),(16,.16,7,'panic')]
 if u<19.2:
  for start,step,count,mode in schedules:
   for j in range(count):
    age=u-(start+j*step)
    if 0<=age<1.35:
     for side in (-1,1):
      sx=bx+side*70;sy=by+35
      if mode=='heavy':dx=side*20
      elif mode=='corner':dx=side*100
      elif mode=='angry':dx=-side*55
      else:dx=side*(35+((j*47)%140)-70)
      x=sx+dx*age;y=sy+age*(270 if mode=='heavy' else 320)
      place(im,F['energy'] if mode=='heavy' else F['laser_bullet'],x,y,.4,angle=-side*5)
      if age<.12:place(im,F['muzzle'],sx,sy,.3)
 # Missile lock position freezes at launch, missiles fly toward it, then explode in walls.
 for warn,launch,impact in [(4.5,5.2,6.6),(11.1,12.0,13.5)]:
  lockx,locky=player_at(launch,*bosspose(launch)[:2]);targetx=lockx+100 if launch<6 else lockx-105;targetx=max(35,min(445,targetx));targety=610
  if warn<=u<launch+.2:place(im,F['target_reticle'],targetx,targety,.31,opacity=.9)
  for j in range(3):
   age=u-(launch+j*.22)
   if 0<=age<1.4:
    for side in (-1,1):
     sx=bx+side*115;sy=by+40;q=age/1.4;x=sx+(targetx-sx)*q;y=sy+(targety-sy)*q;ang=math.degrees(math.atan2(-(targetx-sx),targety-sy));place(im,F['missile_trail'],x,y-20,.35,angle=ang,opacity=.8);place(im,F['missile'],x,y,.58,angle=ang)
  if impact<=u<impact+.38:place(im,F['missile_impact'],targetx,targety,.35+(u-impact),opacity=max(0,1-(u-impact)*2))
 if 9.1<=u<10.5:beam(im,bx,by,-24+48*(u-9.1)/1.4)
 if 17.6<=u<19.2:beam(im,bx,by,20-40*(u-17.6)/1.6)
 # Player shots visibly reach boss core. Each HP transition is tied to an impact.
 if u<19.2:
  for ht in hits:
   age=u-(ht-.7)
   if 0<=age<.7:
    startx,starty=player_at(ht-.7,*bosspose(ht-.7)[:2]);targetbx,targetby,_=bosspose(ht);q=age/.7;x=startx+(targetbx-startx)*q;y=starty+(targetby-30-starty)*q;ang=math.degrees(math.atan2(-(targetbx-startx),targetby-30-starty));place(im,F['laser_bullet'],x,y,.28,angle=ang)
   if ht<=u<ht+.15:place(im,F['armor_impact'],bx,by-30,.3,opacity=max(0,1-(u-ht)/.15))
 # Ordered four-second death sequence: distinct sources, not one generic burst.
 if 19.2<=u<20.15:place(im,F['turret_blast'],bx-70,by-30,.45+(u-19.2)*.2,opacity=max(0,1-(u-19.2)*.75))
 if 19.85<=u<21.5:place(im,F['pod_fire'],bx+115,by+10,.5,opacity=pulse(u))
 if 20.5<=u<21.5:place(im,F['arc'],bx,by,.85,opacity=pulse(u))
 if 21.0<=u<21.5:place(im,F['critical'],bx,by-30,.6+(u-21)*1.2,opacity=.9)
 if 21.5<=u<22.8:
  age=u-21.5;place(im,F['main_blast'],bx,by,.65+age*.9,opacity=max(0,1-age*.6));place(im,F['shockwave'],bx,by,.4+age*2.3,opacity=max(0,1-age*.7))
  for j in range(10):
   a=j*math.tau/10;dist=age*(110+(j%3)*60);place(im,F['debris'],bx+dist*math.cos(a),by+dist*math.sin(a),.15,angle=age*(70+j*9),opacity=max(0,1-age*.65))
 # All projectiles are suppressed after boss death; final second is smoke only.
 if u<23:place(im,player,px,py)
 # Two or three near-static frames at impact; bright flash is a compositing overlay.
 if frozen is not None:
  stage=i-round(frozen*12);strength=([.40,.88,.32] if abs(frozen-21.2)<.01 else [.18,.34,.12])[min(stage,2)];im=Image.alpha_composite(im,Image.new('RGBA',(W,H),(255,239,202,round(strength*255))))
 frames.append(im.convert('RGB'))
# Lossless in time: 216*80ms + 72*90ms = 24 s.
frames[0].save(P/'boss-cinematic-full.gif',save_all=True,append_images=frames[1:],duration=[80 if i%3!=1 else 90 for i in range(len(frames))],loop=0,optimize=False,disposal=2)
# A deterministic 6x6 board with one sample each two-thirds second.
board=Image.new('RGB',(480*6,700*6));
for j in range(36):board.paste(frames[j*8],((j%6)*480,(j//6)*700))
board.resize((1440,2100),Image.Resampling.LANCZOS).save(P/'boss-cinematic-sheet.jpg',quality=90)
# GitHub-viewing version preserves every frame and delay, sacrificing resolution/palette.
small=[im.resize((224,327),Image.Resampling.LANCZOS).quantize(colors=40,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE) for im in frames]
small[0].save(P/'boss-cinematic-github.gif',save_all=True,append_images=small[1:],duration=[80 if i%3!=1 else 90 for i in range(len(frames))],loop=0,optimize=True,disposal=2)
meta={'status':'REVIEW_PROTOTYPE_NOT_RUNTIME','fps':12,'frames':len(frames),'duration_seconds':24,'source_files':{k:{'path':str(root/v),'sha256':hashlib.sha256((root/v).read_bytes()).hexdigest()} for k,v in names.items()},'hp_hit_seconds':hits,'freeze_event_seconds':freeze_times,'assets':['exports/boss-layers','exports/effects','exports/cinematic'],'notes':['Impact timing, projectile trajectories, health and player path are staged, not runtime simulation.','The generated VFX must undergo visual alpha and gameplay QA.']}
(P/'cinematic-manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print('rendered',len(frames))
