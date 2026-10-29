#!/usr/bin/env python3
"""Register whole generated hull variants to existing artwork's 512 canvas."""
from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
P=Path('art/boss-fight');E=P/'exports';O=E/'hull-variants';O.mkdir(exist_ok=True,parents=True)
base=Image.open(E/'boss-bare-hull.png').convert('RGBA'); ba=np.asarray(base).copy()
variants={'intact':base}
for name in ['medium','severe']:
 src=P/f'masters/B1/hull-{name}.png'; im=Image.open(src).convert('RGB').resize((512,512),Image.Resampling.LANCZOS);rgba=np.asarray(im).copy();
 # Retain original art on silhouette boundary; avoids contamination from differing generated background colors.
 edge=ba[:,:,3]<250;rgba[edge]=ba[:,:,:3][edge];variant=Image.fromarray(np.dstack((rgba,ba[:,:,3])),'RGBA');variants[name]=variant
for k,v in variants.items():v.save(O/f'hull-{k}.png')
L={n:Image.open(E/'boss-layers'/f'{n}.png').convert('RGBA') for n in ('pod_left','pod_right','core','cannon')}
T={f'{s}_{p}':Image.open(E/'turret-pivot-tests'/f'{s}-{p}.png').convert('RGBA') for s in ('left','right') for p in ('base','head')}
def assembled(hull,angle=0):
 out=hull.copy()
 for k in ('pod_left','pod_right','core','cannon'):out.alpha_composite(L[k])
 for side,x in [('left',144),('right',368)]:
  out.alpha_composite(T[f'{side}_base'],(x-256,210-256))
  out.alpha_composite(T[f'{side}_head'].rotate(angle if side=='left' else -angle,Image.Resampling.BICUBIC,center=(256,256)),(x-256,210-256))
 return out
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGB').resize((240,350),Image.Resampling.LANCZOS).convert('RGBA');
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((18,18),Image.Resampling.LANCZOS)
sheet=Image.new('RGB',(720,350));names=['intact','medium','severe']
for i,name in enumerate(names):
 part=bg.copy();ship=assembled(variants[name]).resize((159,159),Image.Resampling.LANCZOS);part.alpha_composite(ship,(40,0));part.alpha_composite(player,(111,286));sheet.paste(part.convert('RGB'),(240*i,0));assembled(variants[name]).save(O/f'assembled-{name}.png')
sheet.save(O/'three-stages-gameplay.png')
# Discrete swaps on impact (no crossfade); turret bases do not rotate.
impact=Image.open(E/'effects/armor_impact.png').convert('RGBA').resize((44,44),Image.Resampling.LANCZOS)
frames=[]
for i in range(120):
 stage=names[min(i//40,2)];frame=bg.copy();ship=assembled(variants[stage],20*np.sin(i/12)).resize((159,159),Image.Resampling.LANCZOS);frame.alpha_composite(ship,(40,0));
 if i in (40,41,80,81):frame.alpha_composite(impact,(100,42))
 frame.alpha_composite(player,(111,286));frames.append(frame.convert('RGB'))
palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT);f=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames];f[0].save(O/'stage-transition.gif',save_all=True,append_images=f[1:],duration=50,loop=0,optimize=True,disposal=1)
(O/'manifest.json').write_text(json.dumps({'status':'CANDIDATE_REVIEW','canvas':[512,512],'stages':names,'gameplay_composite_canvas':[240,350],'boss_drawn_px':159,'switch':'discrete at impact, no crossfade','timing_thresholds_demo':{'medium_hp_lte':.30,'severe_hp_lt':.15},'limitations':['Whole-hull B1 generation must be checked for visual continuity in motion and gameplay.','Art study; no runtime QA.'],'masters':{k:hashlib.sha256((P/f'masters/B1/hull-{k}.png').read_bytes()).hexdigest() for k in ('medium','severe')}},indent=2)+'\n')
