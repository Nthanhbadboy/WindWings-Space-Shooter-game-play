from PIL import Image
import numpy as np
from pathlib import Path
p=Path('art/boss-fight');d=p/'exports/candidates';d.mkdir(parents=True,exist_ok=True)
for name,src in [('damage-level2','masters/A3/02-damage-level2-retry.png'),('damage-level3','masters/A2/02-damage-level3.png')]:
 im=Image.open(p/src).convert('RGB');a=np.asarray(im,dtype=np.float32);v=a.max(axis=2);alpha=np.clip((v-8)/225,0,1);rgb=np.clip(a/np.maximum(alpha[:,:,None],.001),0,255).astype('uint8');al=(alpha*255).astype('uint8');rgba=Image.fromarray(np.dstack((rgb,al)),'RGBA');rgba=rgba.crop(rgba.getbbox());rgba.thumbnail((300,250),Image.Resampling.LANCZOS);out=Image.new('RGBA',(512,512));out.alpha_composite(rgba,((512-rgba.width)//2,(512-rgba.height)//2));out.save(d/f'{name}.png')
 base=Image.open(p/'exports/boss-bare-hull.png').convert('RGBA');base.alpha_composite(out);base.save(d/f'{name}-hull.png')
 # QA panels are only composites; no artwork is drawn by code.
 board=Image.new('RGB',(1024,512))
 for x,bg in [(0,(240,240,240)),(512,(19,25,32))]:
  panel=Image.new('RGBA',(512,512),(*bg,255));panel.alpha_composite(base);board.paste(panel.convert('RGB'),(x,0))
 board.save(d/f'{name}-light-dark.png')
