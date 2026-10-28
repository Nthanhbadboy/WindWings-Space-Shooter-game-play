"""Reproducible typed views of existing APK blobs; not a stage enumerator."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
BINDINGS = [
    ('0x14e5b3c', '0x14e5b48', '38', 'PlayerCosts', 'int32', 24),
    ('0x14e5e8c', '0x14e5e9c', '78', 'StartMainCannonDamages', 'float32', 24),
    ('0x14e5eb4', '0x14e5ec4', '80', 'StartMainCannonRate', 'float32', 24),
    ('0x14e5edc', '0x14e5f18', '88', 'StartWingCannonDamages', 'float32', 24),
    ('0x14e608c', '0x14e60c4', '1c8', 'shipCloneDamage', 'float32', 3),
    ('0x14e6204', '0x14e6244', '308', 'PercentToCompleteMissions222', 'float32', 3),
]


def decode(record, kind):
    """Decode only the declared element count; preserve alignment tail separately."""
    if record['length_valid'] is not True:
        raise ValueError('invalid source length')
    raw = bytes.fromhex(record['raw'])
    length = record['len']
    if length < 0 or len(raw) < length * 4:
        raise ValueError('truncated payload')
    fmt = {'int32': 'i', 'float32': 'f'}[kind]
    return dict(element_type=kind, values=list(struct.unpack('<' + fmt * length, raw[:length*4])),
                payload_bytes=length*4, trailing_hex=raw[length*4:].hex())


def build():
    sources = []
    def load(path):
        data = (ROOT / path).read_bytes()
        if path.endswith('.gz'):
            data = gzip.decompress(data)
        sources.append(dict(path=path, sha256_decompressed=hashlib.sha256(data).hexdigest()))
        return data
    original = json.loads(load('reverse-engineering/il2cpp/ia-resolved.json'))['methods']
    asm = load('reverse-engineering/raw/il2cpp-consts/Player_Get_Datas.asm.txt').decode()
    dump = load('reverse-engineering/il2cpp/dump.cs.gz').decode()
    player_decl = dump.split('class Player_Get_Datas :', 1)[1].split('// Methods', 1)[0]
    players = original['Player_Get_Datas.cctor']
    assert {r['addr'] for r in players} == {b[0] for b in BINDINGS}
    bound = []
    for call, store, offset, field, kind, length in BINDINGS:
        row = next(r for r in players if r['addr'] == call)
        assert row['len'] == length
        cs_type = {'int32': 'int', 'float32': 'float'}[kind]
        assert re.search(r'\b' + cs_type + r'\[\] ' + field + r'; // 0x' + offset.upper() + r'\b', player_decl)
        assert re.search(re.escape(call) + r': bl\s+#0x205b07c\b', asm)
        assert re.search(re.escape(store) + r': str\s+x19, \[x8, #0x' + offset + r'\]', asm)
        # Preserve native window for human review of register flow, not just endpoints.
        start = asm.rfind('\n', 0, asm.index(call + ':'))
        end = asm.index('\n', asm.index(store + ':'))
        bound.append(dict(row, **decode(row, kind), target_field=field,
                          static_offset='0x'+offset, store_addr=store,
                          native_call_to_store=asm[start+1:end]))
    maps = original['Map_Get_Datas.cctor']
    assert len(maps) == 576
    assert len({r['addr'] for r in maps}) == 576
    return dict(schema_version=1, status='provisional_static_APK_evidence', sources=sources,
                player_arrays=bound,
                map_arrays=[dict(r, **decode(r, 'int32'), binding_status='container_and_index_not_bound_here') for r in maps],
                map_length_histogram=dict(sorted(collections.Counter(str(r['len']) for r in maps).items())),
                limits=['576 InitializeArray calls are not 576 stages.',
                        'No subtraction of three opening literal arrays is justified by this inventory.',
                        'Map int32 view does not bind arrays to campaign/mode/container/index.',
                        'Player base arrays alone do not establish effective DPS, TTK or duration.',
                        'Trailing bytes are preserved, not interpreted as extra elements.'])


if __name__ == '__main__':
    out = ROOT / 'reverse-engineering/raw/initialize-arrays/typed-inventory.json.gz'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gzip.compress((json.dumps(build(), ensure_ascii=False, indent=2)+'\n').encode(), mtime=0))
    print(out.relative_to(ROOT))
