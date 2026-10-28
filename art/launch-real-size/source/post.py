from PIL import Image,ImageDraw
import numpy as np
from pathlib import Path
p=Path(__file__).resolve().parents[1]; im=Image.open(p/'exports/ships/PLAYER-10001.png').convert('RGBA');alpha=im.getchannel('A');arr=np.asarray(im.convert('RGB'),dtype=float)/255; v=arr.max(2,keepdims=True); q=np.round(v*19)/19; arr=np.clip(arr*np.divide(q,v,out=np.zeros_like(v),where=v>0),0,1); rgb=Image.fromarray(np.uint8(np.round(arr*255)),'RGB').quantize(colors=150,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).convert('RGB');rgb.putalpha(alpha);rgb.save(p/'preview/post-only-comparison.png')
board=Image.new('RGB',(640,400),(14,26,39));d=ImageDraw.Draw(board)
for x,img,title in [(0,im,'BEFORE: direct Lanczos'),(320,rgb,'AFTER: 20 levels, 150 colors')]:
 d.text((x+10,8),title,fill='white');board.paste(img,(x+32,38),img);n=img.resize((64,64),Image.Resampling.LANCZOS);board.paste(n,(x+128,325),n)
board.save(p/'preview/post-before-after.png')
