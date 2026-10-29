#!/usr/bin/env python3
from PIL import Image,ImageDraw
from pathlib import Path
P=Path('art/boss-fight/exports/bullet-B2');names=['heavy-orb','laser','panic','missile','beam-head','beam-strip']
bg=Image.open('art/launch-slice/source/bg-gameplay.png').convert('RGBA').resize((240,350),Image.Resampling.LANCZOS)
player=Image.open('art/launch-real-size/exports/ships/PLAYER-10001.png').convert('RGBA').resize((18,18),Image.Resampling.LANCZOS)
frames=[]
for i in range(30):
 f=bg.copy();f.alpha_composite(player,(111,280));draw=ImageDraw.Draw(f);j=[0,1,2,1,0][(i//6)%5]
 for x,name in zip([30,70,110,150,190,220],names):
  body=Image.open(P/name/'body.png').convert('RGBA');glow=Image.open(P/name/f'glow-{j}.png').convert('RGBA');glow.alpha_composite(body)
  wh={'heavy-orb':(16,16),'laser':(10,20),'panic':(10,10),'missile':(18,18),'beam-head':(18,18),'beam-strip':(12,90)}[name]
  art=glow.resize(wh,Image.Resampling.LANCZOS);f.alpha_composite(art,(x-wh[0]//2,115-wh[1]//2))
 frames.append(f.convert('RGB'))
sample=Image.new('RGB',(768,512));sample.paste(frames[0],(0,0))
for j,name in enumerate(names):
 im=Image.open(P/name/'glow-2.png').convert('RGBA');im.alpha_composite(Image.open(P/name/'body.png').convert('RGBA'));sample.paste(im.convert('RGB').resize((128,128)),(240+(j%4)*128,(j//4)*128))
pal=sample.quantize(colors=256);q=[f.quantize(palette=pal,dither=Image.Dither.NONE) for f in frames];q[0].save(P/'pulse-study.gif',save_all=True,append_images=q[1:],duration=50,loop=0,optimize=True,disposal=1)
# Three beam tiles at natural export size; seam remains checked as art, filtering belongs to engine.
beam=Image.open(P/'beam-strip/body.png').convert('RGBA');out=Image.new('RGBA',(64,384))
for y in (0,128,256):out.alpha_composite(beam,(0,y))
out.save(P/'beam-repeat.png')
