"""Assemble reference-only per-rig folders from audited v2 media, without resampling."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[2]


def assemble(archive, destination, contract):
    expected=json.loads(gzip.decompress((ROOT/'reverse-engineering/raw/asset-pack-v2/archive-audit.json.gz').read_bytes()))['archive_sha256']
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
    destination.mkdir(parents=True,exist_ok=False)
    records=[]
    with zipfile.ZipFile(archive) as zipped:
        for rig in contract['rigs']:
            assert len(rig['atlases'])==1, 'multi-atlas needs a reviewed layout'
            identity=rig['identity']
            label='rig__'+hashlib.sha256(identity['serialized_file'].encode()).hexdigest()+'__'+str(identity['path_id'])
            folder=destination/label
            folder.mkdir()
            atlas=rig['atlases'][0]
            files=[]
            def copy(source,name):
                if Path(name).name!=name or name in ('.','..') or '\\' in name:
                    raise ValueError('unsafe rig page filename')
                blob=zipped.read(source['path'])
                assert len(blob)==source['bytes'] and hashlib.sha256(blob).hexdigest()==source['sha256']
                with (folder/name).open('xb') as out:
                    out.write(blob)
                files.append(dict(file=name,source=source,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
            copy(rig['skeleton'],'skeleton.json')
            copy(atlas['atlas_text'],'skeleton.atlas')
            for page in atlas['pages']:
                copy(page['texture'],page['page'])
            settings=dict(status='reference_association_not_runtime_import_approval',identity=identity,
                          unity_settings=rig['unity_settings'],blend_replacements=rig['blend_replacements'],pages=atlas['pages'],
                          limits=['Original atlas and skeleton bytes preserved. No coordinate resize or PMA/shader conversion.',
                                  'Unity scale/mixing/blend replacements require a compatible runtime setup; these are not editor-import settings.'])
            (folder/'unity-reference-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
            records.append(dict(folder=label,identity=identity,files=files))
    manifest=dict(schema_version=1,status='provisional_associated_reference_folders_not_render_verified',source_archive_sha256=expected,rigs=records)
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (destination/'README.txt').write_text('Reference only. Each rig folder contains exact skeleton/atlas text plus the PNG reached through its owning atlas material. Open manifest.json for provenance. Unity settings, blending, premultiplied alpha and version compatibility are not runtime-approved. Do not rescale atlas coordinates merely to equal PNG dimensions. Original media rights are unchanged.\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    contract=json.loads((ROOT/'datas/spine_identity.json').read_text())
    manifest=assemble(args.archive,args.output,contract)
    # Only provenance/metadata, not original media, is preserved in Git.
    (ROOT/'reverse-engineering/raw/spine-identity/reference-pack-manifest.json.gz').write_bytes(gzip.compress((json.dumps(manifest,indent=2)+'\n').encode(),mtime=0))
    print(f"assembled {len(manifest['rigs'])} reference rig folders")
