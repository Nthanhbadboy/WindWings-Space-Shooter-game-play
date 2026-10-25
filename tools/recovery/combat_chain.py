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
    return bool(re.match(r'Player_Attack(?:_\d+)?(?:\.|$)|Bullet(?:_|[A-Z])|Homing_Missile|Rocket_No_Attack', cls)) or cls in {'Damager', 'Sub_Object', 'Sub_Character', 'Enemy_Sub', 'Enemy_Controller', 'Sub_Player', 'Sub_ShipProtect', 'Skeleton_SubObj', 'Enemy_Ingame', 'Enemy_Health', 'Enemy_Destroy', 'Enemy_Display', 'Shield_Sub', 'Player_Health', 'Player_Ingame', 'Player_Get_Datas', 'GP_Datas', 'Pool_GameObjects', 'BulletInfo', 'IBullet', 'IDamageable'}
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
    parser.add_argument('--dumper', required=True)
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
        # ELF GOT cells contain zero on disk: RELA addends resolve their pointees.
        shoff = struct.unpack_from('<Q', binary, 40)[0]
        shentsize, shnum = struct.unpack_from('<HH', binary, 58)
        relocations = []
        wanted_cells = {va for va, width in cells}
        for i in range(shnum):
            sh = struct.unpack_from('<IIQQQQIIQQ', binary, shoff + i * shentsize)
            if sh[1] != 4: continue  # SHT_RELA
            for pos in range(sh[4], sh[4] + sh[5], sh[9] or 24):
                offset, info, addend = struct.unpack_from('<QQq', binary, pos)
                if offset in wanted_cells:
                    relocations.append(dict(offset=hex(offset), info=hex(info), type=info & 0xffffffff,
                                            symbol_index=info >> 32, addend=hex(addend), source_file_offset=pos,
                                            raw_hex=binary[pos:pos+24].hex()))
        (out / 'relocations.json.gz').write_bytes(gzip.compress(json.dumps(dict(
            status='ELF64_RELA_ROWS_FOR_REFERENCED_CELLS_NOT_RUNTIME', entries=relocations), indent=2).encode(), mtime=0))
        # Decode symbolic metadata usage cells with the same dumper version as the original dump.
        dumper_out = temp / 'symbolic'
        dumper_out.mkdir()
        run = subprocess.run(['dotnet', str(Path(args.dumper).resolve()), str(temp / 'libil2cpp.so'),
                              str(temp / 'global-metadata.dat'), str(dumper_out)],
                             cwd=str(Path(args.dumper).resolve().parent), stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
        assert (dumper_out / 'script.json').is_file(), run.stdout[-4000:]
        script = json.loads((dumper_out / 'script.json').read_text())
        wanted = {va for va, _ in cells}
        wanted.update(r[4] for r in rows if r[0] in CLASSES)
        filtered = {key: [r for r in records if isinstance(r, dict) and (key in {'ScriptMetadata','ScriptMetadataMethod'} or r.get('Address') in wanted)]
                    for key, records in script.items() if isinstance(records, list)}
        (out / 'symbols.json.gz').write_bytes(gzip.compress(json.dumps(dict(
            status='PINNED_DUMPER_SYMBOLIC_USAGE_NOT_RUNTIME', dumper_version='6.7.46',
            dumper_exit_code=run.returncode, dumper_log_tail=run.stdout.decode(errors='replace')[-6000:], script_sha256=hashlib.sha256((dumper_out / 'script.json').read_bytes()).hexdigest(),
            source_counts={k: len(v) for k,v in script.items() if isinstance(v,list)}, records=filtered), indent=2).encode(), mtime=0))
        # Full parsed headers select source component families, never corrupted generated m_Script.
        import UnityPy
        from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
        from asset_pack_v2 import extract_payload, serialized_files
        inputs = extract_payload(apk, temp / 'unity')
        env = UnityPy.load(*(str(p) for p in sorted((temp / 'unity').iterdir())))
        gen = TypeTreeGenerator('2022.3.62f3', generator='AssetStudio')
        gen.load_il2cpp((temp / 'libil2cpp.so').read_bytes(), (temp / 'global-metadata.dat').read_bytes())
        env.typetree_generator = gen
        scripts, components, errors = {}, [], []
        scanned = 0
        for filename, sf in serialized_files(env):
            for obj in sf.objects.values():
                if obj.type.name != 'MonoBehaviour': continue
                scanned += 1
                try:
                    head = obj.parse_monobehaviour_head(); ptr = head.m_Script
                    key = (id(sf), ptr.m_FileID, ptr.m_PathID)
                    if key not in scripts:
                        script_obj = ptr.deref_parse_as_object()
                        scripts[key] = (script_obj.m_Namespace, script_obj.m_ClassName)
                    namespace, cls = scripts[key]
                except Exception as error:
                    errors.append(dict(serialized_file=filename, path_id=obj.path_id, error=repr(error))); continue
                if not (re.fullmatch(r'Player_Attack_\d+', cls) or cls.startswith(('Bullet_', 'BulletZig', 'BulletClock', 'Homing_Missile', 'Rocket_No_Attack')) or cls in {
                    'Bullet_Object','Bullet_Linearly','Bullet_Player3','Bullet_Player7','Bullet_Sword',
                    'Enemy_Sub','Enemy_Health','Shield_Sub','Sub_Player','Skeleton_SubObj'}): continue
                try:
                    tree = obj.read_typetree()
                    go = head.m_GameObject.deref()
                    components.append(dict(serialized_file=filename, path_id=obj.path_id, class_name=cls,
                        namespace=namespace, raw_object_hex=(obj.get_raw_data().hex() if cls.startswith('Player_Attack_') else None), raw_object_sha256=hashlib.sha256(obj.get_raw_data()).hexdigest(),
                        tree=tree, gameobject=dict(path_id=go.path_id, tree=go.read_typetree())))
                except Exception as error:
                    errors.append(dict(serialized_file=filename, path_id=obj.path_id, class_name=cls,error=repr(error), raw_object_hex=obj.get_raw_data().hex(), raw_object_sha256=hashlib.sha256(obj.get_raw_data()).hexdigest(), gameobject=dict(path_id=head.m_GameObject.deref().path_id, tree=head.m_GameObject.deref().read_typetree())))
        shards=[]
        for start in range(0,len(components),250):
            path=out / f'components-{start//250:03d}.json.gz'
            path.write_bytes(gzip.compress(json.dumps(components[start:start+250],indent=2).encode(),mtime=0));shards.append(path)
        (out / 'component-index.json').write_text(json.dumps(dict(status='SERIALIZED_SNAPSHOT_NOT_SPAWN_PROOF',
            inputs=inputs, scanned_headers=scanned, errors=errors, components=len(components),
            externals=[dict(serialized_file=name,externals=[dict(path=e.path,type=e.type) for e in sf.externals])
                       for name,sf in serialized_files(env)],
            shards=[p.name for p in shards]),indent=2)+'\n')
        files = [out / 'relocations.json.gz', out / 'referenced-cells.json.gz', out / 'symbols.json.gz', out / 'component-index.json', *shards, *list(sorted((out / 'native').iterdir()))]
        for path in files:
            if path.parent.name == 'native' and path.suffix == '.json':
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
