"""Bounded source fixtures; not a Unity runtime or observed frame timing."""
import struct

def get_used(slot, read, write):
    key='DroneUsed'+str(slot)
    if read(key,0)<0:write(key,0)
    return read(key,0)

def set_used(slot, value, write):
    write('DroneUsed'+str(slot),value)

def indices(mode, get):
    result=[0,0]  # fresh allocation on EVERY getter invocation
    if mode!=4:result[:]=[get(0),get(1)]
    return result

def load_plan(get_indices):
    result=[]
    scale=struct.unpack('<f',bytes.fromhex('cdcc4c3f'))[0]
    for slot in range(2):
        source_id=get_indices()[slot]  # not one shared snapshot
        if source_id<1:continue
        result.append(dict(slot=slot,source_id=source_id,path='Prefabs/Drones/Drone_'+str(source_id),parent_child=slot,scale=[scale,scale,1.0],local_position=[-20.0 if slot==0 else 20.0,-20.0,0.0],active=True))
    return result

def fix_duplicate(get, unlocked, set_slot, iteration_budget=100):
    """Source has NO upper bound; budget is fixture-only safety, never native behavior."""
    if get(0)!=get(1) or get(0)<1:return
    same=get(1)
    for candidate in range(20001,20001+iteration_budget):
        flag=unlocked(candidate)
        if candidate!=same and flag&1:
            set_slot(0,candidate)
            return
    raise RuntimeError('fixture safety limit; native loop has no recovered cap')
