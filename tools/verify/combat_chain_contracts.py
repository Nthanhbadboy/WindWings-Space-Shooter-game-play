"""Reproducible static combat reference inventory, not a whole-build execution graph."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import struct

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw/combat-chain'


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def read(path):
    blob = path.read_bytes()
    return gzip.decompress(blob) if path.suffix == '.gz' else blob


def build():
    index = json.loads((RAW / 'index.json').read_text())
    for row in index['files']:
        assert digest(read(ROOT / row['path'])) == row['sha256_decompressed'], row['path']
    dump_bytes = gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes())
    assert digest(dump_bytes) == index['dump_sha256_decompressed']
    sys.path.insert(0, str(ROOT / 'tools/apk-analyze'))
    import il2cpp_consts as native
    # Parser needs a path. Its input is preserved dump bytes, not a reconstructed header.
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp) / 'dump.cs'; p.write_bytes(dump_bytes)
        declared = native.parse_dump(str(p))
    targets = {}
    for cls, ns, name, offset, rva, sig in declared:
        targets.setdefault(rva, []).append(dict(class_name=cls, namespace=ns, method=name, signature=sig))
    addresses = sorted(targets)
    next_rva = dict(zip(addresses, addresses[1:]))
    records = []
    for path in sorted((RAW / 'native').glob('*.json')):
        info = json.loads(path.read_text())
        asm = path.with_suffix('.asm.txt').read_text()
        instructions = [(int(a, 16), op, operands.strip()) for a, op, operands in
                        re.findall(r'^[ \t]*0x([0-9a-f]+):[ \t]+(\S+)[ \t]*(.*?)$', asm, re.M)]
        for m in info['methods']:
            start = int(m['rva'], 16)
            end = min(start + m['bytes'], next_rva.get(start, start + m['bytes']))
            body = sorted(set(row for row in instructions if start <= row[0] < end))
            calls, indirect = [], []
            last_w0 = None
            for at, op, operands in body:
                if operands.startswith('w0,'):
                    match_arg = re.fullmatch(r'w0, (wzr|#(?:0x[0-9a-f]+|[0-9]+))', operands) if op == 'mov' else None
                    last_w0 = dict(at=hex(at), value=(0 if match_arg[1]=='wzr' else int(match_arg[1][1:],0))) if match_arg else None
                match = re.fullmatch(r'#0x([0-9a-f]+)', operands)
                if op in ('bl', 'b') and match:
                    destination = int(match[1], 16)
                    if op == 'b' and start <= destination < end:
                        continue
                    calls.append(dict(at=hex(at), opcode=op, target=hex(destination),
                                      declarations=targets.get(destination, []), last_straightline_w0_constant_candidate=last_w0))
                    if op == 'bl': last_w0 = None
                elif op in ('blr', 'br'):
                    indirect.append(dict(at=hex(at), opcode=op, register=operands,
                                         status='UNRESOLVED_DISPATCH_NOT_MISSING_CODE'))
            records.append(dict(class_name=info['class'], method=m['method'], rva=hex(start),
                                exported_bytes=m['bytes'], clipped_bytes=end-start,
                                size_capped=m['size_capped'], exporter_ends_clean=m['ends_clean'],
                                direct_calls=calls, indirect_sites=indirect))
    component_index = json.loads((RAW / 'component-index.json').read_text())
    components = [r for name in component_index['shards'] for r in json.loads(read(RAW / name))]
    # Narrow raw prefix only for Player_Attack_2 whose full generated tree fails.
    validated = []
    for r in components:
        if not re.fullmatch(r'Player_Attack_\d+', r['class_name']): continue
        blob = bytes.fromhex(r['raw_object_hex'])
        assert struct.unpack_from('<i', blob, 28)[0] == 0  # empty MonoBehaviour name
        assert struct.unpack_from('<i', blob, 32)[0] == r['tree']['id']
        assert bool(blob[40]) == r['tree']['demo']
        validated.append(r['path_id'])
    prefix_only = []
    for error in component_index['errors']:
        if error.get('class_name') != 'Player_Attack_2': continue
        blob = bytes.fromhex(error['raw_object_hex'])
        assert digest(blob) == error['raw_object_sha256'] and len(blob) >= 48
        assert struct.unpack_from('<i',blob,28)[0] == 0
        prefix_only.append(dict(serialized_file=error['serialized_file'],path_id=error['path_id'],
                                class_name='Player_Attack_2',id=struct.unpack_from('<i',blob,32)[0],
                                demo=bool(blob[40]),name=error['gameobject']['tree']['m_Name'],
                                status='RAW_PREFIX_ONLY_FULL_TREE_UNREADABLE'))
    ships = []
    for number in range(1, 25):
        cls = f'Player_Attack_{number}'
        family = [r for r in records if r['class_name'] == cls or r['class_name'].startswith(cls + '.')]
        assert any(r['class_name'] == cls for r in family), cls
        snapshots = [dict(serialized_file=r['serialized_file'], path_id=r['path_id'],
                          id=r['tree'].get('id'), demo=r['tree'].get('demo'),
                          name=r['gameobject']['tree'].get('m_Name'),
                          raw_sha256=r['raw_object_sha256']) for r in components if r['class_name'] == cls]
        ships.append(dict(implementation=cls, method_records=len(family), source_components=snapshots,
                          prefix_only_components=[r for r in prefix_only if r['class_name']==cls],
                          source_errors=[r for r in component_index['errors'] if r.get('class_name') == cls],
                          main_rate_consumers=[dict(class_name=r['class_name'],method=r['method'],rva=r['rva'],call=c)
                              for r in family for c in r['direct_calls']
                              if any(d['class_name']=='Player_Get_Datas' and d['method']=='GetMainCannonRate'
                                     for d in c['declarations'])],
                          callbacks=[dict(class_name=r['class_name'], method=r['method'], rva=r['rva'])
                                     for r in family if 'Collid' in r['method'] or 'Hit' in r['method']],
                          semantics_status='NATIVE_INVENTORY_NOT_ALL_SHIP_SEMANTIC_OR_RUNTIME_APPROVAL'))
    symbols = json.loads(read(RAW / 'symbols.json.gz'))
    relas = json.loads(read(RAW / 'relocations.json.gz'))['entries']
    symbol_by_address = {r['Address']: r for key in ('ScriptMetadata','ScriptMetadataMethod')
                         for r in symbols['records'][key]}
    resolved_got = []
    for row in relas:
        offset, info, addend = struct.unpack('<QQq', bytes.fromhex(row['raw_hex']))
        assert hex(offset)==row['offset'] and hex(info)==row['info'] and hex(addend)==row['addend']
        if row['type'] == 1027 and row['symbol_index'] == 0 and addend in symbol_by_address:
            resolved_got.append(dict(got=hex(offset),usage=hex(addend),symbol=symbol_by_address[addend],
                                     status='ELF_RELATIVE_TO_DUMPER_SYMBOL_NOT_RUNTIME_OBSERVATION'))
    pool_bindings = [dict(serialized_file=r['serialized_file'],component_path_id=r['path_id'],
                          class_name=r['class_name'],gameobject=r['gameobject']['tree'].get('m_Name'),
                          pointer=r['tree']['m_OPScript'], pool_entry=r['pool_entry'])
                     for r in components if r.get('pool_entry') is not None]
    receiver_classes={'Enemy_Sub','Sub_Player','Shield_Sub','Sub_ShipProtect','Skeleton_SubObj'}
    collider_roots=[]
    for r in components:
        if r['class_name'] != 'Obj_Collider': continue
        binding=r.get('root_binding')
        collider_roots.append(dict(serialized_file=r['serialized_file'],component_path_id=r['path_id'],
            root=binding, receiver_candidates=[c for c in (binding or {}).get('components',[])
                                              if c.get('class_name') in receiver_classes],
            status='STATIC_ROOT_COMPONENTS_NOT_RUNTIME_GETCOMPONENT_OBSERVATION'))
    return dict(collider_roots=collider_roots, resolved_got=resolved_got, pool_bindings=pool_bindings, prefix_validation_count=len(validated), prefix_only_components=prefix_only, status='PROVISIONAL_STATIC_COMBAT_REFERENCE_NOT_DPS_OR_RUNTIME_CLOSURE',
                inputs=index['inputs_sha256'], dump_sha256=index['dump_sha256_decompressed'],
                source_index_sha256=digest((RAW/'index.json').read_bytes()),
                counts=dict(classes=len(index['classes']), methods=len(records), ships=len(ships),
                            capped=sum(r['size_capped'] for r in records),
                            unclean=sum(not r['exporter_ends_clean'] for r in records),
                            clipped=sum(r['clipped_bytes']<r['exported_bytes'] for r in records),
                            components=len(components), component_errors=len(component_index['errors']),
                            direct_sites=sum(len(r['direct_calls']) for r in records),
                            indirect_sites=sum(len(r['indirect_sites']) for r in records)),
                ships=ships, methods=records,
                symbolic_decoder=dict(exit_code=symbols['dumper_exit_code'],source_counts=symbols['source_counts'],
                                      retained_counts={k:len(v) for k,v in symbols['records'].items()}),
                limitations=['Direct calls are static sites, not a chronological or executed timeline.',
                             'Indirect dispatch needs metadata/interface/delegate resolution at each site.',
                             'Clipping at next declared RVA bounds overlap but does not prove every native body boundary.',
                             'Parsed component headers select script identity; generated tree m_Script is not trusted.',
                             'Snapshot id/demo/barrels are not proof of instantiated runtime loadout.',
                             'Implementation suffix is not a player ID; report82 separately proves suffix-1 arguments for three captured stat getters using CFG.',
                             'No all-ship DPS, collision frequency, playback, FPCR or import/render approval.'])


if __name__ == '__main__':
    result = build()
    path = ROOT / 'datas/combat_chain_contract.json.gz'
    path.write_bytes(gzip.compress((json.dumps(result, indent=2)+'\n').encode(), mtime=0))
    print(json.dumps(result['counts'], indent=2))
