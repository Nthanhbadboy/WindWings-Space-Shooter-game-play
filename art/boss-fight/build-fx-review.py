#!/usr/bin/env python3
from PIL import Image,ImageDraw
from pathlib import Path
P=Path('art/boss-fight/exports');assets=[('charge','effects/charge.png'),('reticle','effects/target_reticle.png'),('overload','effects/core_overload.png'),('muzzle','effects/muzzle.png'),('arc','cinematic/arc.png'),('turret','cinematic/turret_blast.png'),('pod','cinematic/pod_fire.png'),('smoke','cinematic/smoke.png'),('blast','cinematic/main_blast.png'),('shockwave','effects/shockwave.png'),('impact','cinematic/missile_impact.png')]
board=Image.new('RGB',(640,((len(assets)+3)//4)*160),(28,34,40));d=ImageDraw.Draw(board)
for i,(name,path) in enumerate(assets):
 x=(i%4)*160;y=(i//4)*160;img=Image.open(P/path).convert('RGBA');img.thumbnail((64,64),Image.Resampling.LANCZOS)
 for j,c in enumerate([(240,240,240,255),(18,25,32,255)]):
  b=Image.new('RGBA',(72,72),c);b.alpha_composite(img,((72-img.width)//2,(72-img.height)//2));board.paste(b.convert('RGB'),(x+j*76,y+20))
 d.text((x+4,y+3),name,fill='white')
board.save(P/'battle-study'/'fx-review.png')
