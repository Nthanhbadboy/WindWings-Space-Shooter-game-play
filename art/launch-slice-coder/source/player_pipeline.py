from PIL import Image,ImageDraw
import numpy as np, sys
from pathlib import Path
P=Path(__file__).resolve().parent; N=1024
# Fixed palette before drawing. Five metal/glass hues × 30 curved lighting values.
hues=[(0.51, 0.7024999999999999, 1.0), (0.72, 0.8425, 1.0), (0.4, 0.72, 1.0), (0.84, 0.92, 1.0), (1.0, 0.44000000000000006, 0.0), (0.44000000000000006, 0.72, 1.0)]
body_hues=[(0.46099999999999997, 0.6727499999999998, 1.0), (0.692, 0.82675, 1.0), (0.4, 0.72, 1.0), (0.84, 0.92, 1.0), (1.0, 0.44000000000000006, 0.0), (0.384, 0.692, 1.0)]
pal=[]
for h in hues:
 for i in range(30):
  v=.18+.77*i/29; pal.extend([round(255*v*x) for x in h])
pal += [0]*(768-len(pal)); palette=Image.new('P',(1,1));palette.putpalette(pal)
# d = extent of underside AO; only one parameter varied between experiments.
d=float(sys.argv[1]); canvas=Image.new('RGBA',(N,N));
xgrid=np.arange(N)[None,:]/N; ygrid=np.arange(N)[:,None]/N

def plate(points, hue, center, radius, dark, bright):
 mask=Image.new('L',(N,N));ImageDraw.Draw(mask).polygon([(int(x*N),int(y*N)) for x,y in points],fill=255)
 # Continuous curvature: light on spine / upper plane, darker toward lower edge.
 xc,yc=center; rx,ry=(radius[0]*.55,radius[1]*.55)
 curvature=np.clip(1-0.55*((xgrid-xc)/rx)**2-0.45*((ygrid-yc)/ry)**2,0,1)
 curvature=np.sqrt(curvature); v=dark+(bright-dark)*curvature
 # Metallic panels only: nonlinear lighting + soft underside AO; preserve canopy.
 if hue != hues[4]:
  v=np.maximum(.25, v**1.4 - .075*np.clip((ygrid-.46)/.30,0,1)*(1-curvature))
  # Increase top-facing metallic catchlight only; retain all values <=.35.
  top=np.exp(-((ygrid-.36)/.18)**2) * (np.exp(-((xgrid-.5)/.14)**2)+.55*np.exp(-((np.abs(xgrid-.5)-.23)/.13)**2))
  gate=np.clip((v-.35)/.10,0,1)
  v=np.clip(v + .11*top*gate,0,1)
 rgb=np.empty((N,N,4),dtype=np.uint8)
 for i,component in enumerate(hue):
  if hue == body_hues[2]:
   # Allocate top of the same metal plate to the existing paler steel-blue.
   mix=np.clip((.57-ygrid)/.12,0,1)
   component=component*(1-mix)+body_hues[3][i]*mix
  rgb[:,:,i]=(255*np.clip(v*component,0,1)).astype(np.uint8)
 rgb[:,:,3]=np.asarray(mask);canvas.alpha_composite(Image.fromarray(rgb,'RGBA'))
# Distinct materials and 2–3 layered plate overlaps, without outer stroke.
plate([(.50,.08),(.59,.33),(.91,.70),(.83,.81),(.59,.70),(.50,.90),(.41,.70),(.17,.81),(.09,.70),(.41,.33)],body_hues[1],(.5,.30),(.5,.70),.23,.86)
plate([(.13,.68),(.36,.47),(.45,.58),(.32,.72),(.17,.81)],body_hues[3],(.29,.54),(.28,.32),d,.48)
plate([(.87,.68),(.64,.47),(.55,.58),(.68,.72),(.83,.81)],body_hues[3],(.71,.54),(.28,.32),d,.48)
plate([(.50,.18),(.58,.43),(.75,.65),(.68,.72),(.54,.61),(.50,.84),(.46,.61),(.32,.72),(.25,.65),(.42,.43)],body_hues[5],(.50,.32),(.35,.55),.23,.75)
plate([(.50,.12),(.57,.37),(.56,.69),(.50,.83),(.44,.69),(.43,.37)],body_hues[2],(.50,.29),(.20,.55),.21,.95)
plate([(.50,.30),(.54,.39),(.535,.55),(.50,.61),(.465,.55),(.46,.39)],body_hues[4],(.50,.40),(.08,.23),.30,.95)
plate([(.40,.72),(.46,.72),(.46,.82),(.40,.82)],body_hues[1],(.43,.71),(.08,.14),.23,.54)
plate([(.54,.72),(.60,.72),(.60,.82),(.54,.82)],body_hues[1],(.57,.71),(.08,.14),.23,.54)
# Thin short internal highlights; no outer contour.
draw=ImageDraw.Draw(canvas);draw.line([(301,690),(369,634)],fill=(157,185,205,255),width=3);draw.line([(723,690),(655,634)],fill=(157,185,205,255),width=3)
canvas.save(P/'master.png'); small=canvas.resize((256,256),Image.Resampling.LANCZOS);alpha=small.getchannel('A'); a=np.array(small.convert('RGB'),dtype=float)/255; val=a.max(axis=2,keepdims=True); discrete=np.round(val*23)/23; a=np.clip(a*np.divide(discrete,val,out=np.zeros_like(val),where=val>0),0,1); rgb=Image.fromarray(np.uint8(np.round(a*255)),'RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGB');rgb.putalpha(alpha);rgb.save(P/'player.png')
