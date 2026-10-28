from PIL import Image
import numpy as np
from scipy.ndimage import binary_propagation, binary_fill_holes
from pathlib import Path
p=Path(__file__).resolve().parent; arr=np.array(Image.open(p/'PLAYER-10001-generated.png').convert('RGB'),dtype=float); v=arr.max(2); h,w=v.shape
# Outside-connected low-intensity dark is unmatted; enclosed black mechanical lines remain opaque.
low=v<42; seed=np.zeros((h,w),bool);seed[0,:]=low[0,:];seed[-1,:]=low[-1,:];seed[:,0]|=low[:,0];seed[:,-1]|=low[:,-1]; outside=binary_propagation(seed,mask=low)
a=np.ones((h,w));a[outside]=np.clip((v[outside]-4)/38,0,1);rgb=arr.copy(); nz=(a>0)&outside;rgb[nz]=np.clip(rgb[nz]/a[nz,None],0,255);rgb[a==0]=0
rgba=Image.fromarray(np.dstack((np.round(rgb).astype('uint8'),np.round(a*255).astype('uint8'))),'RGBA');box=Image.fromarray(np.uint8(v>10)*255).getbbox(); box=(max(0,box[0]-8),max(0,box[1]-8),min(w,box[2]+8),min(h,box[3]+8)); print('bbox',box,'source',rgba.size,'touches edge',box[3]==h); sprite=rgba.crop(box);s=1408; img=Image.new('RGBA',(s,s));sprite.thumbnail((int(s*.90),int(s*.90)),Image.Resampling.LANCZOS);img.alpha_composite(sprite,((s-sprite.width)//2,(s-sprite.height)//2));img.save(p/'master.png'); ex=img.resize((256,256),Image.Resampling.LANCZOS);ex.save(p/'export.png');print('master',img.size,'export',ex.size)
