#!/usr/bin/env python3
"""Extract timeline and half-second test spans from encoded GIFs, not a runtime test."""
from PIL import Image,ImageSequence
from pathlib import Path
p=Path('art/boss-fight/exports/battle-study');g=Image.open(p/'battle-study.gif');targets=[i*.5 for i in range(64)];found={};elapsed=0
for frame in ImageSequence.Iterator(g):
 d=frame.info.get('duration',0)
 for t in targets:
  if t not in found and elapsed<=t*1000<elapsed+d:found[t]=frame.convert('RGB').copy()
 elapsed+=d
assert len(found)==len(targets) and elapsed==32000
sheet=Image.new('RGB',(240*8,350*8))
for i,t in enumerate(targets):sheet.paste(found[t],((i%8)*240,(i//8)*350))
sheet.save(p/'timeline-review.jpg',quality=90)
print('encoded',g.n_frames,'frames',elapsed,'ms; samples',len(targets))
