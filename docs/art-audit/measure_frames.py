#!/usr/bin/env python3
"""Measure 4 archived reference captures and 4 W0 stills per variant.

Uses the unmodified spec branch tools/design-metrics.py measure() at its pinned
SHA. These W0 stills are marketing concepts, NOT screenshots of the Godot game.
"""
import argparse
import csv
import hashlib
import importlib.util
from pathlib import Path

SCRIPT_SHA256 = "77bb6a91edd691145924b63dad4c09d95e98c9525390dbbd986d27ca3bddebc7"

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec-root',type=Path,required=True)
    ap.add_argument('--a-root',type=Path,required=True)
    ap.add_argument('--b-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    tool=args.spec_root/'tools/design-metrics.py'
    if digest(tool)!=SCRIPT_SHA256: raise ValueError('Wrong design-metrics.py SHA-256')
    spec=importlib.util.spec_from_file_location('design_metrics',tool)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    captures=['p_2_Game','slow_8_Game','p_4_Game','live_1_Game']
    jobs=[('REF',args.spec_root,f'docs/apk-analysis/ramus/2026-10-23-phone/{x}.png') for x in captures]
    for set_name,root,folder in [('A',args.a_root,'w0-listing'),('B',args.b_root,'w0-listing-b')]:
        jobs.extend((set_name,root,f'art/{folder}/huawei-appgallery/huawei_screenshot_{i}_450x800.png') for i in range(1,5))
    rows=[]
    for group,root,rel in jobs:
        path=root/rel
        m=module.measure(str(path))
        rows.append({'set':group,'path':rel,'sha256':digest(path),'width':m['w'],'height':m['h'],
                     'contrast_p95_p05':round(m['luminance_p95']-m['luminance_p05'],4),
                     'accent_all_hues':m['accent_share'],'detail_gradient':m['detail_gradient'],
                     'mean_value':m['mean_value'],'mean_saturation':m['mean_saturation']})
        print(group,rel,rows[-1]['contrast_p95_p05'],rows[-1]['accent_all_hues'],rows[-1]['detail_gradient'],flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print('Wrote',len(rows),args.out)

if __name__=='__main__': main()
