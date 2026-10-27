"""Recover scoped player firing consumers only from the pinned original APK; no full export."""
import argparse
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ('Player_Get_Datas', 'Player_Attack', 'Player_Attack_1')
APK_SHA = 'f5d3c7a188dce663a1f06961380da0d6ffa541138d7cb957215e884cdd057c7e'
INPUTS = {'lib/arm64-v8a/libil2cpp.so': '9cb038e88709f38318d183d3616eed054b36c3186ead8f1c37246ece87393c99',
          'assets/bin/Data/Managed/Metadata/global-metadata.dat': '449a0698a1b71d0e4d04efafdb4e2fad97fd02ca8f8528715ad9638aa813ba69'}


def mask_unselected(rows):
    # Keep ALL offsets so method boundaries are unchanged. Hide class identity of
    # unrelated rows to bypass the shared exporter's automatic animation families.
    return [(cls if cls in CLASSES else '__not_selected__', ns, name, offset, rva, sig)
            for cls, ns, name, offset, rva, sig in rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xapk', required=True)
    args = parser.parse_args()
    apk = Path(args.xapk)
    assert hashlib.sha256(apk.read_bytes()).hexdigest() == APK_SHA
    out = ROOT / 'reverse-engineering/raw/player-firing'
    out.mkdir(exist_ok=True)
    sys.path.insert(0, str(ROOT / 'tools/apk-analyze'))
    import il2cpp_consts as native
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        seen = {}
        with zipfile.ZipFile(apk) as outer:
            for entry in outer.namelist():
                if not entry.endswith('.apk'):
                    continue
                with zipfile.ZipFile(io.BytesIO(outer.read(entry))) as part:
                    for name in sorted(INPUTS.keys() & set(part.namelist())):
                        data = part.read(name)
                        assert hashlib.sha256(data).hexdigest() == INPUTS[name]
                        destination = temp / Path(name).name
                        destination.write_bytes(data)
                        seen[name] = INPUTS[name]
        assert seen == INPUTS
        dump = temp / 'dump.cs'
        dump_bytes = gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())
        dump.write_bytes(dump_bytes)
        rows = native.parse_dump(str(dump))
        native.parse_dump = lambda _: mask_unselected(rows)
        native.TARGET_CLASSES.clear()
        native.TARGET_CLASSES.update({cls: 'Pinned player firing consumer recovery; provisional' for cls in CLASSES})
        native.OUT_RAW = str(out / 'native')
        native.OUT_MD = str(temp / 'summary.md')
        native.OUT_CSV = str(temp / 'floats.csv')
        sys.argv = ['native', str(dump), str(temp / 'libil2cpp.so')]
        assert native.main() == 0
        files = list(sorted((out / 'native').iterdir()))
        for path in files:
            if path.suffix == '.json':
                info = json.loads(path.read_text())
                assert info['methods'] and not any(m['size_capped'] for m in info['methods'])
        assert {p.name for p in (out / 'native').iterdir()} == {re.sub(r'[^\w.]', '_', c) + ext for c in CLASSES for ext in ('.asm.txt', '.json')}
        for path in files:
            assert path.stat().st_size < 5_000_000
        manifest = dict(status='PROVISIONAL_PINNED_NATIVE_RECOVERY_NOT_RUNTIME', xapk_sha256=APK_SHA,
                        inputs_sha256=seen, dump_sha256_decompressed=hashlib.sha256(dump_bytes).hexdigest(),
                        classes=list(CLASSES), files=[])
        for path in files:
            data = path.read_bytes()
            if path.suffix == '.gz':
                data = gzip.decompress(data)
            manifest['files'].append(dict(path=str(path.relative_to(ROOT)), sha256_decompressed=hashlib.sha256(data).hexdigest()))
        (out / 'index.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
