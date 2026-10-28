#!/usr/bin/env python3
"""Join extracted Map segments to current InitializeArray captures; fail closed."""
import json
from pathlib import Path


def main():
    data = json.loads(Path('datas/map_table_segments.json').read_text())
    resolved = json.loads(Path('reverse-engineering/il2cpp/ia-resolved.json').read_text())
    rows = resolved['methods']['Map_Get_Datas.cctor']
    assert len(rows) == 576 and all(r['length_valid'] for r in rows)
    by_new = {r['array_new_addr']: r for r in rows}
    assert len(by_new) == len(rows)
    segments, matched = [], set()
    for segment in data['segments']:
        arrays = []
        for array in segment['arrays']:
            row = dict(array)
            if array['source'] == 'InitializeArray':
                capture = by_new[array['addr']]
                assert capture['len'] == array['len'] == len(capture['ints'])
                row.update(values=capture['ints'], field=capture['field'],
                           initialize_array_addr=capture['addr'])
                matched.add(array['addr'])
            else:
                assert len(row['values']) == row['len']
                row['complete'] = all(isinstance(v, int) for v in row['values'])
            arrays.append(row)
        segments.append(dict(index=segment['index'], arrays=arrays))
    assert len(matched) == 576
    campaign = next(s for s in segments if s['index'] == 35)['arrays']
    assert len(campaign) == 250
    assert all(all(isinstance(v, int) for v in a['values']) for a in campaign)
    for path, obj in [
        ('datas/map_segments_full.json', dict(note='PROVISIONAL APK static extraction; current call-site capture, all 576 IA lengths validated', segments=segments, standalone_arrays=data.get('standalone_arrays', []))),
        ('datas/maps.json', dict(source='PROVISIONAL listMapDatas @0x28, segment 35; zero-based array order (UI numbering not verified)', maps=[a['values'] for a in campaign]))
    ]:
        Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1)+'\n')
    print('576/576 IA joined; 250/250 campaign entries complete; campaign immediate arrays validated; dynamic standalone length left unknown')


if __name__ == '__main__':
    main()
