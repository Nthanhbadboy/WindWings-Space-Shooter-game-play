#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
P=Path('art/boss-fight');E=P/'exports';O=E/'hull-variants-B2'
L={n:Image.open(E/'boss-layers'/f'{n}.png').convert('RGBA') for n in ('pod_left','pod_right','core','cannon')}
T={f'{s}_{p}':Image.open(E/'turret-pivot-tests'/f'{s}-{p}.png').convert('RGBA') for s in ('left','right') for p in ('base','head')}
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((240,350),Image.Resampling.LANCZOS)
frames=[]
for i in range(144):
 stage='intact' if i<72 else 'severe';angle=(i%72)*5
 h=Image.open(O/f'hull-{stage}.png').convert('RGBA')
 for n in ('pod_left','pod_right','core','cannon'):h.alpha_composite(L[n])
 for side,x in [('left',144),('right',368)]:
  h.alpha_composite(T[side+'_base'],(x-256,210-256));h.alpha_composite(T[side+'_head'].rotate(angle if side=='left' else -angle,Image.Resampling.BICUBIC,center=(256,256)),(x-256,210-256))
 f=bg.copy();f.alpha_composite(h.resize((159,159),Image.Resampling.LANCZOS),(40,0));frames.append(f.convert('RGB'))
board=Image.new('RGB',(240*8,350*2))
for j in range(16):board.paste(frames[(j//8)*72+(j%8)*9],((j%8)*240,(j//8)*350))
board.save(O/'assembly-360-sheet.jpg',quality=90);pal=board.quantize(colors=256);f=[im.quantize(palette=pal,dither=Image.Dither.NONE) for im in frames];f[0].save(O/'assembly-360.gif',save_all=True,append_images=f[1:],duration=50,loop=0,optimize=True,disposal=1)
