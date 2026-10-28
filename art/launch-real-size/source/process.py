from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_propagation
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parents[1]; original=Image.open(p/'masters/PLAYER-10001-generate-original.png').convert('RGB'); arr=np.asarray(original.crop((66,66,958,958)),dtype=float);mx=arr.max(2); h,w=mx.shape
background=mx<42; seed=np.zeros((h,w),bool);seed[0,:]=background[0,:];seed[-1,:]=background[-1,:];seed[:,0]|=background[:,0];seed[:,-1]|=background[:,-1];outside=binary_propagation(seed,mask=background)
alpha=np.ones((h,w));alpha[outside]=np.clip((mx[outside]-4)/38,0,1); rgb=arr.copy(); edge=outside&(alpha>0);rgb[edge]=np.clip(rgb[edge]/alpha[edge,None],0,255); rgb[alpha==0]=0
rgba=Image.fromarray(np.dstack([np.round(rgb).astype('uint8'),np.round(255*alpha).astype('uint8')]),'RGBA');rgba.save(p/'steps/PLAYER-10001-alpha-892.png'); small=rgba.resize((256,256),Image.Resampling.LANCZOS); small.save(p/'exports/ships/PLAYER-10001.png'); miniature=small.resize((64,64),Image.Resampling.LANCZOS); miniature.save(p/'preview/PLAYER-10001-64.png')
bg=Image.open(Path(__file__).resolve().parents[3]/'art/launch-slice/source/bg-gameplay.png').convert('RGB');target=(720,1280);scale=max(target[0]/bg.width,target[1]/bg.height);bg=bg.resize((round(bg.width*scale),round(bg.height*scale)),Image.Resampling.LANCZOS);bg=bg.crop(((bg.width-target[0])//2,0,(bg.width+target[0])//2,target[1])).convert('RGBA')
# Contract 1.4 units on a 20-unit-wide field; 720 * 1.4/20 = 50.4px.
gamepx=round(target[0]*1.4/20); player=small.resize((gamepx,gamepx),Image.Resampling.LANCZOS);bg.alpha_composite(player,((720-gamepx)//2,1000));bg.convert('RGB').save(p/'preview/gameplay-20units.png')
review=Image.new('RGB',(384,144),(24,30,39));d=ImageDraw.Draw(review)
for idx,col in enumerate([(10,20,35),(225,225,225)]):
 x=idx*192; d.rectangle((x,0,x+191,143),fill=col);review.paste(miniature,(x+64,45),miniature)
review.save(p/'preview/64-dark-light.png')
print('image size',original.size,'cropped 66..958 background',rgba.size,'game width',gamepx,'ratios',gamepx/720)
