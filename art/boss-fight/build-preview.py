from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, json, hashlib
from scipy import ndimage
from pathlib import Path
P=Path('art/boss-fight'); M=P/'masters'; E=P/'exports'; (E/'boss-layers').mkdir(parents=True,exist_ok=True); (E/'effects').mkdir(exist_ok=True); (P/'review').mkdir(exist_ok=True)
S={'hull':'round4/01-hull.png','turret_left':'02-left-turret.png','turret_right':'round2/03-right-turret-redo.png','cannon':'round3/04-cannon.png','pod_left':'round3/05-left-pod.png','pod_right':'round4/06-right-pod.png','core':'07-core.png','damage':'08-damage.png','energy':'09-energy.png','laser_bullet':'10-laser-bullet.png','beam':'round2/11-beam-strip.png','beam_origin':'round2/12-beam-origin.png','charge':'round3/13-charge-ring-redo.png','missile':'round2/14-missile.png','muzzle':'round2/15-muzzle.png','shockwave':'round2/16-shockwave.png','target_reticle':'round5/target-reticle.png','explosion':'round5/impact-explosion.png'}
# Black-background extraction: flood-connect near-black pixels for solid modules;
# energy VFX use luminance-derived opacity, unpremultiplied to avoid black halos.
def extract(name,fx=False):
 im=Image.open(M/S[name]).convert('RGB'); a=np.array(im).astype(np.float32); lum=a.max(axis=2)
 if fx:
  # Suppress near-black generative noise before calculating bounds and alpha.
  alpha=np.clip((lum-10)/195,0,1); rgb=np.clip(a/np.maximum(alpha[:,:,None],0.001),0,255).astype('uint8'); aa=(alpha*255).astype('uint8')
  support=ndimage.binary_opening(lum>18,iterations=2); support=ndimage.binary_dilation(support,iterations=12); aa=np.where(support,aa,0).astype('uint8')
 else:
  # Keep the largest connected solid object, fill its internal dark cavities;
  # remove isolated black-background noise rather than making black boxes.
  mask=ndimage.binary_closing(lum>20,iterations=2); labels,n=ndimage.label(mask); counts=np.bincount(labels.ravel()); counts[0]=0
  mask=labels==counts.argmax(); mask=ndimage.binary_fill_holes(mask); mask=ndimage.binary_dilation(mask,iterations=2)
  aa=(mask*255).astype('uint8'); rgb=a.astype('uint8')
 out=Image.fromarray(np.dstack((rgb,aa)),'RGBA'); bbox=out.getbbox(); return out.crop(bbox) if bbox else out

def fit(im,wh):
 im=im.copy(); im.thumbnail(wh,Image.Resampling.LANCZOS); return im

def layer(name,wh,center,fx=False):
 im=fit(extract(name,fx),wh); canvas=Image.new('RGBA',(512,512)); canvas.alpha_composite(im,(round(center[0]-im.width/2),round(center[1]-im.height/2)));canvas.save(E/'boss-layers'/f'{name}.png');return canvas
# all fixed-pose images have a shared origin and common canvas
spec={'hull':((460,455),(256,255)), 'pod_left':((105,190),(68,238)), 'pod_right':((105,190),(444,238)), 'turret_left':((112,145),(144,229)), 'turret_right':((112,145),(368,229)), 'core':((93,93),(256,207)), 'cannon':((112,170),(256,327)), 'damage':((230,200),(256,240))}
layers={k:layer(k,*v,fx=(k=='damage')) for k,v in spec.items()}
pivots={'turret_left':(144,210),'turret_right':(368,210),'cannon':(256,291)}
order=['hull','pod_left','pod_right','turret_left','turret_right','core','cannon'];boss=Image.new('RGBA',(512,512))
for k in order: boss.alpha_composite(layers[k])
boss.save(E/'boss-composite.png');layers['hull'].save(E/'boss-bare-hull.png')
def effect(name,canvas,wh):
 obj=fit(extract(name,True if name not in ('missile',) else False),wh); im=Image.new('RGBA',canvas); im.alpha_composite(obj,((canvas[0]-obj.width)//2,(canvas[1]-obj.height)//2));im.save(E/'effects'/f'{name}.png');return im
fx={}
for k,canvas,wh in [('energy',(64,64),(58,58)),('laser_bullet',(64,128),(54,118)),('beam_origin',(128,128),(116,116)),('charge',(256,256),(240,240)),('missile',(64,64),(56,58)),('muzzle',(128,128),(110,110)),('shockwave',(256,256),(240,240)),('target_reticle',(256,256),(240,240)),('explosion',(256,256),(240,240))]:fx[k]=effect(k,canvas,wh)
# beam derived from full height source, resize to strip; taper top-bottom mismatch by
# crossfading the two ends to a shared average profile (repeat seam has identical pixels).
im=Image.open(M/S['beam']).convert('RGB'); ar=np.asarray(im); luma=ar.max(axis=2); active=np.where(luma.max(axis=0)>12)[0]; im=im.crop((max(0,int(active[0])-10),0,min(im.width,int(active[-1])+11),im.height)).resize((64,256),Image.Resampling.LANCZOS)
a=np.array(im).astype(np.float32); edge=(a[0]+a[-1])/2
for i in range(24):
 t=(24-i)/24; a[i]=a[i]*(1-t)+edge*t; a[-1-i]=a[-1-i]*(1-t)+edge*t
lum=a.max(axis=2); al=np.clip((lum-5)/205,0,1); al[:,0]=0; al[:,-1]=0; rgb=np.clip(a/np.maximum(al[:,:,None],.001),0,255).astype('uint8');beam=Image.fromarray(np.dstack((rgb,(al*255).astype('uint8'))),'RGBA');beam.save(E/'effects/beam-strip.png'); assert np.array_equal(np.asarray(beam)[0],np.asarray(beam)[-1])
# Preview is built solely from exported RGBA layers/effects and approved player export.
W,H=480,700; bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGB');bg=bg.resize((W,round(bg.height*W/bg.width)),Image.Resampling.LANCZOS);bg=bg.crop((0,(bg.height-H)//2,W,(bg.height+H)//2)).convert('RGBA')
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((34,34),Image.Resampling.LANCZOS)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13); small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',10)
def paste(im,obj,xy,scale=1,angle=0,alpha=1):
 obj=obj.copy();
 if scale!=1: obj=obj.resize((max(1,round(obj.width*scale)),max(1,round(obj.height*scale))),Image.Resampling.LANCZOS)
 if angle: obj=obj.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<1: obj.putalpha(obj.getchannel('A').point(lambda a:round(a*alpha)))
 im.alpha_composite(obj,(round(xy[0]-obj.width/2),round(xy[1]-obj.height/2)))
def boss_at(t):return (240, -75+min(1,t/1.1)*260)
frames=[]
for i in range(216):
 t=i/12; im=bg.copy(); bx,by=boss_at(t); bs=.62; boss_alpha=max(0,min(1,(16.15-t)/.7)); px=240+130*math.sin(t*1.55); py=590+20*math.sin(t*2)
 # Warning rings precede each shot phase; VFX placed behind boss.
 if t<1.5 or 3.0<=t<4 or 5.9<=t<6.45 or 8<=t<8.35 or 10.3<=t<11.2: paste(im,fx['charge'],(bx,by),.8,alpha=.55+.3*math.sin(t*13)**2)
 for k in order:
  # rotating turrets pivot at target centers in the 512 canvas, not at image center
  if k in ('turret_left','turret_right') and t>1.5:
   cx,cy=pivots[k]; lay=layers[k]; box=(cx-90,cy-100,cx+90,cy+100); piece=lay.crop(box); tx=bx+(cx-256)*bs;ty=by+(cy-256)*bs;paste(im,piece,(tx,ty),bs,angle=math.sin(t*2+(0 if k.endswith('left') else 1))*18,alpha=boss_alpha)
  else: paste(im,layers[k],(bx,by),bs,alpha=boss_alpha*((.65+.35*abs(math.sin(t*8))) if k=='core' and t>8 else 1))
 # Telegraph is over the armor so it is actually visible before attacks.
 if t<1.5 or 3.0<=t<4 or 5.9<=t<6.45 or 8<=t<8.35 or 10.3<=t<11.2:
  paste(im,fx['charge'],(bx,by+10),.95,alpha=.65+.25*math.sin(t*13)**2)
 # smoke overlay under low HP
 if 8<=t<16.15:
  paste(im,layers['damage'],(bx-42,by-52),.85,alpha=.95*boss_alpha)
  paste(im,layers['damage'],(bx+40,by-40),.72,alpha=.9*boss_alpha)
 # short energy and laser bolts, charge warning precedes burst
 if 1.5<=t<3.25 or 8.35<=t<10.3:
  cadence=.30 if t>=8 else .48
  for j in range(4):
   age=(t-(1.5 if t<4 else 8.35))-j*cadence
   if 0<=age<1.35:
    for side in (-1,1):
     x=bx+side*(70+age*30); y=by+40+age*300
     paste(im,fx['energy'] if j%2==0 else fx['laser_bullet'],(x,y),.42)
  if (t*3)%1<.24: paste(im,fx['muzzle'],(bx,by+65),.45)
 # Thin preview line indicates where the sweeping beam will begin.
 if 3.0<=t<4:
  ang=-25; L=440; guide=beam.resize((5,L)); paste(im,guide,(bx+math.sin(math.radians(ang))*L/2,by+85+math.cos(math.radians(ang))*L/2),angle=ang,alpha=.45)
 # beam sweep: telegraph before firing, pivot at cannon muzzle
 if 4<=t<5.9:
  ang=-25+50*(t-4)/1.9; L=440; segment=beam.resize((20,L)); paste(im,segment,(bx+math.sin(math.radians(ang))*L/2,by+85+math.cos(math.radians(ang))*L/2),1,angle=ang);paste(im,fx['beam_origin'],(bx,by+85),.45)
 # Missiles converge on the position shown in the lock-on warning; the player can dodge it.
 lockx=240+130*math.sin(6.45*1.55); locky=590+20*math.sin(6.45*2)
 if 6.45<=t<9.1:
  for j in range(4):
   age=t-6.45-j*.33
   if 0<=age<1.45:
    for side in (-1,1):
     x0=bx+side*115; y0=by+48; u=age/1.45
     x=x0+(lockx-x0)*u; y=y0+(locky-y0)*u
     angle=math.degrees(math.atan2(-(lockx-x0),locky-y0))
     paste(im,fx['missile'],(x,y),.72,angle=angle)
 if 5.9<=t<6.7: paste(im,fx['target_reticle'],(lockx,locky),.33+.08*math.sin(t*10)**2,alpha=.8)
 # Boss shockwave is preceded by a charge warning.
 if 11.2<=t<12.8:
  age=t-11.2; paste(im,fx['shockwave'],(bx,by),.35+age*2.2,alpha=max(0,1-age*.58))
 # Counter-fire targets the core rather than missing and still destroying the boss.
 shot_times=[1.7+j*.52 for j in range(13)]+[8.7+j*.42 for j in range(15)]
 for fired in shot_times:
  age=t-fired
  if 0<=age<.8:
   u=age/.8; startx=240+130*math.sin(fired*1.55); starty=590+20*math.sin(fired*2)-12
   x=startx+(bx-startx)*u; y=starty+(by-30-starty)*u
   angle=math.degrees(math.atan2(-(bx-startx),by-30-starty))
   paste(im,fx['laser_bullet'],(x,y),.32,angle=angle,alpha=.9)
  if .8<=age<.96: paste(im,fx['beam_origin'],(bx,by-30),.20,alpha=max(0,1-(age-.8)/.16))
 if 15.45<=t<17.0:
  age=t-15.45
  paste(im,fx['explosion'],(bx,by),.45+age*.75,alpha=max(0,1-age*.62))
  paste(im,fx['shockwave'],(bx,by),.35+age*1.6,alpha=max(0,1-age*.6))
 paste(im,player,(px,py))
 d=ImageDraw.Draw(im);d.text((14,10),'BOSS-37001  /  BATTLE PREVIEW',font=font,fill=(220,245,246))
 phase=('WARNING' if t<1.5 else 'CANNONS' if t<3 else 'BEAM CHARGE' if t<4 else 'SWEEP' if t<5.9 else 'MISSILE LOCK' if t<6.45 else 'MISSILES' if t<8 else 'LOW HP' if t<10.3 else 'PULSE CHARGE' if t<11.2 else 'SHOCKWAVE' if t<12.8 else 'COUNTERATTACK' if t<15.45 else 'BOSS DOWN')
 d.text((14,30),phase,font=small,fill=(255,187,95)); d.rectangle((14,47,220,52),fill=(35,47,58))
 hits=sum(t>=fired+.8 for fired in shot_times); health=max(0,1-hits/len(shot_times))
 if health>0: d.rectangle((14,47,14+int(206*health),52),fill=(226,138,55))
 frames.append(im.convert('RGB'))
# GIF delay pattern 80/90/80 gives 216 delays = 18 s in centiseconds.
frames[0].save(P/'boss-fight-preview.gif',save_all=True,append_images=frames[1:],duration=[80 if i%3!=1 else 90 for i in range(216)],loop=0,optimize=False,disposal=2)
sheet=Image.new('RGB',(480*6,700*6),(0,0,0));
for j in range(36): sheet.paste(frames[j*6],((j%6)*480,(j//6)*700))
sheet.resize((1440,2100),Image.Resampling.LANCZOS).save(P/'boss-fight-frame-sheet.jpg',quality=90)
manifest={'status':'PROTOTYPE_REVIEW_NOT_RUNTIME_VERIFIED','source_masters':{k:{'path':str(M/v),'sha256':hashlib.sha256((M/v).read_bytes()).hexdigest()} for k,v in S.items()},'canvas':[512,512],'coordinate_system':'top-left, x right, y down; all pivot coordinates are in shared 512x512 boss canvas','layers':[{'name':k,'file':str(E/'boss-layers'/f'{k}.png'),'center':spec[k][1],'pivot':pivots.get(k),'order':n} for n,k in enumerate(order)],'damage_overlay':str(E/'boss-layers/damage.png'),'core_center':[256,207],'spawn_points':{'turret_left':[144,280],'turret_right':[368,280],'main_cannon_and_beam':[256,399],'pod_left':[68,333],'pod_right':[444,333]},'effects':{k:str(E/'effects'/f'{k}.png') for k in fx},'beam_strip':str(E/'effects/beam-strip.png'),'beam_end_rows_identical':bool(np.array_equal(np.asarray(beam)[0],np.asarray(beam)[-1])),'notes':['pivot and spawn coordinates estimated for prototype; must validate rotation and gameplay placement','left and right pods are separate generated images with similar but not identical details','alpha matte and luminous effects require artist review on light and dark backgrounds','hull has a few circular mechanical details but its central socket is closed','preview is composited, not a runtime capture']}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print('done',len(frames),'frames')
