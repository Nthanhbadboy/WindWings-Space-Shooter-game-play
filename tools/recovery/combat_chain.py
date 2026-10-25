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
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CLASSES = ()

def selected(cls):
    return bool(re.match(r'Player_Attack(?:_\d+)?(?:\.|$)|Bullet(?:_|[A-Z])|Homing_Missile|Rocket_No_Attack', cls)) or cls in {'Damager', 'Sub_Object', 'Sub_Character', 'Enemy_Ingame', 'Enemy_Health', 'Enemy_Destroy', 'Enemy_Display', 'Shield_Sub', 'Player_Health', 'Player_Ingame', 'Player_Get_Datas', 'GP_Datas', 'Pool_GameObjects', 'BulletInfo', 'IBullet', 'IDamageable'}
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
    out = ROOT / 'reverse-engineering/raw/combat-chain'
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
        global CLASSES
        CLASSES = tuple(sorted({r[0] for r in rows if selected(r[0])}))
        native.parse_dump = lambda _: mask_unselected(rows)
        native.TARGET_CLASSES.clear()
        native.TARGET_CLASSES.update({cls: 'Pinned player firing consumer recovery; provisional' for cls in CLASSES})
        native.OUT_RAW = str(out / 'native')
        native.OUT_MD = str(temp / 'summary.md')
        native.OUT_CSV = str(temp / 'floats.csv')
        sys.argv = ['native', str(dump), str(temp / 'libil2cpp.so')]
        assert native.main() == 0
        # Capture exact native referenced cells, including encoded metadata usages.
        # These are initial ELF bytes, NOT initialized runtime pointers.
        binary = (temp / 'libil2cpp.so').read_bytes()
        segments = native.elf_segments(str(temp / 'libil2cpp.so'))
        cells = {}
        for path in sorted((out / 'native').glob('*.asm.txt')):
            pages = {}
            for line in path.read_text().splitlines():
                m = re.search(r'0x([0-9a-f]+): adrp\s+(x\d+), #0x([0-9a-f]+)', line)
                if m:
                    pages[m[2]] = int(m[3], 16)
                    continue
                m = re.search(r'0x([0-9a-f]+): ldr\s+([xsdq]\d+), \[(x\d+)(?:, #0x([0-9a-f]+))?\]', line)
                if not m or m[3] not in pages:
                    continue
                va = pages[m[3]] + int(m[4] or '0', 16)
                width = {'x': 8, 's': 4, 'd': 8, 'q': 16}[m[2][0]]
                seg = next((p for p in segments if p[0] <= va and va + width <= p[0] + p[2]), None)
                if seg:
                    offset = seg[1] + va - seg[0]
                    data = binary[offset:offset + width]
                    cells[(va, width)] = dict(va=hex(va), file_offset=offset, width=width, hex=data.hex())
                # Tracking is deliberately conservative; registers overwritten below invalidate pages.
                # Candidate cells are raw references, not a semantic dataflow proof.
        (out / 'referenced-cells.json.gz').write_bytes(gzip.compress(json.dumps(dict(
            status='RAW_ADRP_LDR_CANDIDATES_NOT_RUNTIME_POINTERS_OR_DATAFLOW_PROOF',
            cells=list(cells.values())), indent=2).encode(), mtime=0))
        files = [out / 'referenced-cells.json.gz', *list(sorted((out / 'native').iterdir()))]
        for path in files:
            if path.suffix == '.json':
                info = json.loads(path.read_text())
                assert info['methods']
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
