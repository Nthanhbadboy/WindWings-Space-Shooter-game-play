#!/usr/bin/env python3
"""Geometric sanity check of staged visual paths, NOT game collision QA."""
import ast,math,json
from pathlib import Path
p=Path('art/boss-fight/build-battle-study.py');tree=ast.parse(p.read_text())
nodes=[]
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ('player_pos','hp'):nodes.append(n)
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HITS' for t in n.targets):nodes.append(n)
ns={'math':math};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns);pos,hp=ns['player_pos'],ns['hp']
assert hp(7.2)==.7 and hp(18.2)==.25 and hp(22)==.15 and hp(24)==.1
beams=[]
for a,b,lo,hi in [(15.5,17.4,-25,25),(22.8,24.7,-25,25),(24.7,26.6,25,-25)]:
 samples=[]
 for i in range(round(a*20),round(b*20)):
  t=i/20;x,y=pos(t);angle=lo+(hi-lo)*(t-a)/(b-a);xbeam=120+math.tan(math.radians(angle))*(y-123)
  samples.append((abs(x-xbeam),t))
 d,t=min(samples);beams.append({'start':a,'minimum_centerline_separation_px':round(d,2),'at_s':t})
lock=pos(11.3);miss=[];shots=[]
for i in range(0,round(27*20)):
 t=i/20;x,y=pos(t)
 for j in range(4):
  age=t-(11.3+j*.18)
  if 0<=age<1.6:
   for side in (-1,1):
    q=age/1.6;sx=120+side*58;sy=85;mx=sx+(lock[0]-sx)*q;my=sy+(lock[1]-sy)*q
    miss.append((math.hypot(x-mx,y-my),t))
 for start,interval in [(2.4,.6),(8.5,.6),(19.5,.6/1.3)]:
  for j in range(3):
   age=t-(start+j*interval)
   if 0<=age<2.0:
    for side in (-1,1):
     drift=math.tan(math.radians(side*6))*age*130 if start==19.5 else side*8*age
     ex=120+side*35+drift;ey=90+age*130
     # Boss remains stationary during all three shot events.
     shots.append((math.hypot(x-ex,y-ey),t))
result={'scope':'sampled visual paths at 20Hz only; player radius, projectile silhouettes, engine motion and colliders not tested','beams':beams,'missile_min_center_distance_px':round(min(miss)[0],2),'shot_min_center_distance_px':round(min(shots)[0],2),'shot_closest_time_s':min(shots)[1],'shot_risk_times_s':sorted(set(round(t,2) for d,t in shots if d<15)),'hp_boundaries':{'7.2':hp(7.2),'18.2':hp(18.2),'22':hp(22),'24':hp(24)}}
print(json.dumps(result,indent=2));Path('art/boss-fight/exports/battle-study/path-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert all(b['minimum_centerline_separation_px']>15 for b in beams)
