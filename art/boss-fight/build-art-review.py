#!/usr/bin/env python3
"""Extract representative half-second spans from final encoded GIF (no runtime claims)."""
from PIL import Image,ImageSequence
from pathlib import Path
p=Path('art/boss-fight/exports/battle-study');g=Image.open(p/'battle-study.gif')
rows={'heavy':[3.2,3.35,3.5,3.65,3.7],'laser':[10.0,10.15,10.3,10.45,10.5],'missile':[12.0,12.15,12.3,12.45,12.5],'fan':[20.9,21.05,21.2,21.35,21.4],'beam':[15.6,15.75,15.9,16.05,16.1],'death':[27.0,27.7,28.4,29.3,30.4]}
ts=sorted(set(t for r in rows.values() for t in r));found={};elapsed=0
for frame in ImageSequence.Iterator(g):
 end=elapsed+frame.info.get('duration',0)
 for t in ts:
  if t not in found and elapsed<=t*1000<end:found[t]=frame.convert('RGB').copy()
 elapsed=end
assert len(found)==len(ts),(len(found),len(ts))
board=Image.new('RGB',(240*5,350*len(rows)))
for y,(name,times) in enumerate(rows.items()):
 for x,t in enumerate(times):board.paste(found[t],(240*x,350*y))
board.save(p/'art-review-spans.jpg',quality=93)
print('samples',len(ts),'duration',elapsed)
