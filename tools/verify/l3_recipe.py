"""Consume the joined L3 contract, optionally materializing exact raw object snapshots.
Example: python3 -m tools.verify.l3_recipe --root 10 --out /home/user/pause-recipe.json.gz --include-raw
No engine simulation or image reconstruction. Media paths refer to the external asset pack.
"""
import argparse
import gzip
import hashlib
import json
from functools import cached_property
from pathlib import Path
from tools.verify.l3_chain_graph import ROOT, RAW, key

class Recipes:
    def __init__(self):
        self.header=json.loads(gzip.decompress((ROOT/'datas/l3_scene_chains.json.gz').read_bytes()))
        self.cache={};self.raw_cache={}
    def section(self,name):
        if name not in self.cache:
            rows=[]
            for c in self.header['chunks'][name]:
                b=(ROOT/c['path']).read_bytes()
                assert hashlib.sha256(b).hexdigest()==c['sha256'],c['path']
                part=json.loads(gzip.decompress(b));assert len(part)==c['rows'];rows.extend(part)
            self.cache[name]=rows
        return self.cache[name]
    @cached_property
    def raw_chunks(self):
        b=(RAW/'index.json').read_bytes()
        assert hashlib.sha256(b).hexdigest()==self.header['input_index_sha256']
        return {str((RAW/c['path']).relative_to(ROOT)):c for c in json.loads(b)['objects']}
    def raw(self,locator):
        path=locator['path']
        if path not in self.raw_cache:
            c=self.raw_chunks[path];b=(ROOT/path).read_bytes();assert hashlib.sha256(b).hexdigest()==c['sha256']
            rows=[json.loads(line) for line in gzip.decompress(b).splitlines()];assert len(rows)==c['rows'];self.raw_cache[path]=rows
        return self.raw_cache[path][locator['row']]
    def recipe(self,root_index,include_raw=False):
        root=self.header['roots'][root_index]
        out=dict(schema=1,provisional=True,root=root,source_index_sha256=self.header['input_index_sha256'],scope=self.header['scope'],scene_context=self.header['scene_context'],native_camera_contract=self.header['native_camera_contract'])
        for name,indices in [('nodes','node_indices'),('callbacks','callback_indices'),('sounds','sound_indices'),('animators','animator_indices')]:
            table=self.section(name);out[name]=[table[i] for i in root[indices]]
        asset_ids={key(a) for a in root['asset_identities']};out['assets']=[a for a in self.section('assets') if key(a['identity']) in asset_ids]
        animator_ids={key(a['animator']) for a in out['animators']}
        out['animation_bindings']=[b for b in self.section('animation_bindings') if key(b['animator']) in animator_ids]
        clips={key(c) for a in out['animators'] for c in a['clips']}
        out['motion']=[m for m in self.section('motion') if key(m['identity']) in clips]
        from tools.verify.l3_animator_programs import load
        programs=load()
        out['controller_programs']=[c for c in programs['controllers'] if key(c['identity']) in asset_ids]
        out['animator_program_links']=[a for a in programs['animator_attachments'] if key(a['animator']) in animator_ids]
        out['binding_diagnostics']=[b for b in programs['binding_diagnostics'] if key(b['animator']) in animator_ids]
        from tools.verify.l3_ui_drivers import load as load_drivers
        drivers=load_drivers();component_ids={key(c['identity']) for n in out['nodes'] for c in n['component_identities']}
        out['native_ui']=dict(artifact='datas/l3_ui_drivers.json.gz',sha256=hashlib.sha256((ROOT/'datas/l3_ui_drivers.json.gz').read_bytes()).hexdigest(),effects=[dict(effect_index=i,**e) for i,e in enumerate(drivers['effects']) if key(e['owner']) in component_ids],callback_entries=[e for e in drivers['callback_entries'] if key(e['owner']) in component_ids],inherited_events=[e for e in drivers['inherited_events'] if key(e['owner']) in component_ids])
        if include_raw:
            locators={}
            for n in out['nodes']:
                for c in n['component_identities']:
                    if c['raw_location']:locators[key(c['identity'])]=c['raw_location']
            for a in out['assets']:locators[key(a['identity'])]=a['raw_location']
            out['raw_objects']=[self.raw(locators[k]) for k in sorted(locators)]
            out['raw_header_authority']='MonoBehaviour binary header overrides generated tree header fields; both originals retained.'
        return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=int);p.add_argument('--label',default='');p.add_argument('--out',type=Path);p.add_argument('--include-raw',action='store_true');a=p.parse_args();r=Recipes()
    if a.root is None:
        for i,root in enumerate(r.header['roots']):
            if a.label.lower() in root['label'].lower():print(i,root['kind'],root['label'],root['nodes'])
        return
    data=r.recipe(a.root,a.include_raw);b=json.dumps(data,ensure_ascii=True,separators=(',',':')).encode()
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_bytes(gzip.compress(b,mtime=0) if a.out.suffix=='.gz' else b)
        print(a.out, 'nodes',len(data['nodes']),'assets',len(data['assets']),'motion',len(data['motion']))
    else:print(b.decode())
if __name__=='__main__':main()
