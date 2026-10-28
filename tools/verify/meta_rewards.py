#!/usr/bin/env python3
"""Static decoder for daily/weekly meta rewards (build 1.3.118). No code executed.

Two kinds of static evidence are joined here, both from pinned original-APK bytes:

1. **Metadata usage slots.** `ldr x1, [xN]` where `xN` indexes `Il2CppMetadataUsage`
   carries a pointer whose 16 target bytes are `(kind << 29) | source`. String
   literal slots (kind 5) land on `Il2CppString` objects that
   `reverse-engineering/il2cpp/stringliteral.json` already indexed by address, so
   the *text* of a static string is recoverable without running the game.
2. **`InitializeArray` tokens.** Each `bl #0x205b07c` takes a `FieldInfo` token
   (kind 4) whose decoded source is `2 * ordinal + 1` in the calling image's
   `<PrivateImplementationDetails>` type. That type's fields are declared in
   `dump.cs` with their byte size, and their literal bytes live in
   `field-defaults.json` (`fieldDefaultValues`), so the array contents are the
   stored blob truncated to the declared element count.

Anything the symbolic initializer cannot model is reported as `not_decoded` with
the blocking instruction; nothing is guessed.
"""
import argparse
import gzip
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from arena_pvp_initializers import class_layouts, decode_class  # noqa: E402

NATIVE = 'reverse-engineering/raw/meta-rewards-535b0541/native.json.gz'
SOURCES = (NATIVE,
           'reverse-engineering/il2cpp/dump.cs.gz',
           'reverse-engineering/il2cpp/stringliteral.json',
           'reverse-engineering/il2cpp/field-defaults.json')
PID_CLASS = '<PrivateImplementationDetails>'
TARGET_CLASSES = ('GameDatas', 'TimeFreeRewardPack', 'Board_QuestRewards',
                  'Popup_WatchVideos', 'Board_EventSeasonPass', 'Shop_Pack')
GAPS = (
    ('MAX_LEVEL_BP', 'không tồn tại như symbol managed: 0 hit trong dump.cs và 0 hit trong '
                     'stringliteral.json; không phải field/static của build này'),
    ('giá gift/quest/video', 'pack/price nằm ở field instance (Shop_Pack, EventRewards.price) '
                             'hoặc board serialized; .so chỉ chứa bảng dựng trong .cctor'),
    ('Shop_Pack bảng theo người chơi', 'allVipRewards/allLogInRewards là List dựng trong .cctor '
                                       'nhưng nội dung theo hạng VIP được nạp lúc chạy'),
    ('ArenaManager.SeasonTimes/RankUpIndexs/RankDropIndexs',
     'gán trong LoadRemoteConfigs từ JSON remote — MODEL_NOT_MEASURED runtime'),
    ('Board_BattlePassPro/BattlePassMission', 'ngoài scope lượt này (45.308 B code); chưa trích'),
)


def sha_file(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load_native(path=NATIVE):
    return json.loads(gzip.decompress((ROOT / path).read_bytes()))


def dump_text():
    return gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode()


def parse_pid_classes(text):
    """[TypeDefIndex, [(declared size, field hash), ...]] in declaration order.

    Every field counts. An early draft filtered on `__StaticArrayInitTypeSize=`,
    which silently dropped the scalar `internal static readonly int <hash> = -1;`
    field and shifted every ordinal by one: `src = 2 * ordinal + 1` then resolved
    to a neighbouring blob whose size happened to fit for 11 of 15 arrays.
    Including all fields makes all 15 fit exactly (see `initialize_arrays.summary`).
    """
    out = []
    pattern = re.compile(r'internal sealed class ' + re.escape(PID_CLASS) +
                         r' // TypeDefIndex: (\d+)\n\{(.*?)\n\}', re.S)
    for match in pattern.finditer(text):
        fields = []
        for line in match.group(2).split('\n'):
            declared = re.match(r'\s*internal static readonly (\S+) ([0-9A-F]{64})', line)
            if not declared:
                continue
            type_text, field = declared.groups()
            size = re.search(r'__StaticArrayInitTypeSize=(\d+)', type_text)
            fields.append((int(size.group(1)) if size else None, field, type_text))
        out.append((int(match.group(1)), fields))
    return out


def parse_type_index(text):
    out = {}
    for match in re.finditer(r'^[^\n]*?\b(?:class|struct|enum) ([\w<>`.=]+)[^\n]*?// TypeDefIndex: (\d+)$',
                             text, re.M):
        out.setdefault(match.group(1), int(match.group(2)))
    return out


def pid_for(pid_classes, type_index):
    """The `<PrivateImplementationDetails>` of the caller's image (next type index)."""
    higher = [tidx for tidx, _ in pid_classes if tidx > type_index]
    if not higher:
        return None
    target = min(higher)
    return dict(type_index=target,
                fields=next(fields for tidx, fields in pid_classes if tidx == target))


def instance_layouts(cls):
    """{offset: (field, type)} for **instance** fields of one class.

    Static and instance offsets are separate address spaces: `Shop_Pack` statics
    occupy 0x0-0x60 while its reward ints occupy 0x10-0x7C, so a merged layout
    labels instance writes with static names (`BoxRewardsRoot` instead of `Gems`).
    """
    text = dump_text()
    match = re.search(r'^[^\n]*?\bclass ' + re.escape(cls) + r'(?=[\s:<])[^\n]*// TypeDefIndex: \d+$',
                      text, re.M)
    if not match:
        return {}
    depth, pos = 0, text.index('{', match.start())
    for end in range(pos, len(text)):
        if text[end] == '{':
            depth += 1
        elif text[end] == '}':
            depth -= 1
            if depth == 0:
                break
    out = {}
    for line in text[pos:end].split('\n'):
        field = re.match(r'\s*(?:public|private|protected|internal)\s+(static\s+)?(.+?)\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)\s*$',
                         line)
        if field and not field.group(1):
            out[int(field.group(4), 16)] = (field.group(3), field.group(2).strip())
    return out


def string_table():
    entries = json.loads((ROOT / 'reverse-engineering/il2cpp/stringliteral.json').read_text())
    return {int(e['address'], 16): e['value'] for e in entries}


def field_defaults():
    return json.loads((ROOT / 'reverse-engineering/il2cpp/field-defaults.json').read_text())['fields']


def resolve_initialize_array(event, pid, defaults):
    """FieldInfo token -> `<PrivateImplementationDetails>` blob -> int list."""
    lo = event.get('token_lo')
    out = dict(initialize_rva=event.get('rva'), slot_va=event.get('slot_va'),
               addend=event.get('addend'), declared_length=event.get('length'))
    if lo is None:
        return dict(out, status='no_token_bytes')
    kind, source = (lo >> 29) & 0x7, lo & 0x1FFFFFFF
    out.update(token_kind=kind, token_source=source)
    if kind != 4:
        return dict(out, status='token_kind_not_field')
    if source % 2 == 0:
        return dict(out, status='odd_token_rule_violated')
    ordinal = (source - 1) // 2
    out['field_ordinal'] = ordinal
    if pid is None or ordinal >= len(pid['fields']):
        return dict(out, status='ordinal_out_of_image_pid')
    declared, field, type_text = pid['fields'][ordinal]
    out.update(pid_type_index=pid['type_index'], declared_bytes=declared,
               field=field, field_type=type_text)
    entry = defaults.get(f'{PID_CLASS}.{field}')
    if entry is None:
        return dict(out, status='no_field_default_value')
    raw = bytes.fromhex(entry['raw'])
    out['default_bytes'] = len(raw)
    length = event.get('length')
    if length is None:
        return dict(out, status='array_length_not_in_stream')
    if not 4 * length <= len(raw) < 4 * length + 16 or (declared is not None and declared < 4 * length):
        return dict(out, status='blob_length_mismatch')
    out.update(status='ok', ints=list(struct.unpack('<%di' % length, raw[:4 * length])),
               trailing_hex=raw[4 * length:].hex())
    return out


def metadata_usage(native, strings):
    """Every metadata slot in scope, with its token kind and resolved literal."""
    rows, per_class = [], {}
    for method in native['methods']:
        for ref in method.get('slot_refs', []):
            lo = ref.get('token_lo')
            row = dict(class_name=method['class_name'], method=method['signature'],
                       method_rva=method['rva'], instruction_rva=ref['rva'],
                       slot_va=ref['slot_va'], addend=ref['addend'],
                       token_kind=(None if lo is None else (lo >> 29) & 0x7),
                       token_source=(None if lo is None else lo & 0x1FFFFFFF),
                       string=(ref.get('string') or strings.get(ref['addend'])))
            rows.append(row)
            per_class.setdefault(method['class_name'], []).append(
                dict(instruction_rva=ref['rva'], token_kind=row['token_kind'],
                     token_source=row['token_source'], string=row['string']))
    return rows, per_class


def build(native_path=NATIVE):
    native = load_native(native_path)
    text = dump_text()
    strings = string_table()
    defaults = field_defaults()
    pids = parse_pid_classes(text)
    index = parse_type_index(text)
    layouts = class_layouts()

    usage_rows, usage_by_class = metadata_usage(native, strings)

    def pid_for_class(cls):
        return pid_for(pids, index[cls]) if cls in index else None

    # --- InitializeArray resolution per class/method -----------------------
    init_arrays = {}
    for method in native['methods']:
        events = method.get('initialize_arrays') or []
        if not events:
            continue
        pid = pid_for_class(method['class_name'])
        resolved = [resolve_initialize_array(e, pid, defaults) for e in events]
        init_arrays.setdefault(method['class_name'], []).append(
            dict(method=method['signature'], method_rva=method['rva'], arrays=resolved))
    resolved_by_rva = {}
    for entry in init_arrays.values():
        for method in entry:
            for row in method['arrays']:
                if row['status'] == 'ok':
                    resolved_by_rva[row['initialize_rva']] = row['ints']

    # --- symbolic initializer pass ----------------------------------------
    statics, failures = {}, {}
    for cls in TARGET_CLASSES + ('ArenaManager', 'ArenaConfig', 'PVP_Manager'):
        try:
            statics[cls] = decode_class(native, cls, layouts, string_table=strings,
                                        ia_resolution=resolved_by_rva)
        except (StopIteration, KeyError):
            failures[cls] = dict(stage='method_lookup', detail='no .cctor in scope')
        except ValueError as error:
            failures[cls] = dict(stage='symbolic_pass', detail=str(error))

    # --- reward tables -----------------------------------------------------
    def field_value(cls, name):
        block = statics.get(cls, {}).get('fields', {})
        return block.get(name)

    pack_layout = instance_layouts('Shop_Pack')

    def flatten(fields, layout):
        """Name each written word: a 16-byte vector store covers four int fields."""
        out = {}
        for offset_hex, value in sorted(fields.items(), key=lambda kv: int(kv[0], 16)):
            offset = int(offset_hex, 16)
            if isinstance(value, dict) and value.get('kind') == 'pool':
                for lane, word in enumerate(value.get('ints') or []):
                    key = layout.get(offset + 4 * lane, (f'0x{offset + 4 * lane:x}',))[0]
                    out[key] = word
                continue
            key = layout.get(offset, (offset_hex,))[0]
            out[key] = pack_view(value) if isinstance(value, dict) and value.get('kind') == 'object' else value
        return out

    def pack_view(node):
        """Name Shop_Pack fields by layout offset; keep only what the cctor wrote."""
        if not isinstance(node, dict):
            return node
        if node.get('kind') == 'array':
            return [pack_view(v) for v in (node.get('values') or [])]
        if node.get('kind') != 'object':
            return node
        out = flatten(node.get('fields', {}), pack_layout)
        if node.get('items'):
            out['_list'] = [pack_view(item) for item in node['items']]
        return out

    shop_packs = {}
    for name, entry in (statics.get('Shop_Pack', {}).get('fields') or {}).items():
        shop_packs[name] = pack_view(entry['value'])
    event_reward_layout = instance_layouts('Board_EventSeasonPass.EventRewards')
    event_rewards = []
    event_table = (statics.get('Board_EventSeasonPass', {}).get('fields') or {}).get('eventRewards')
    for node in ((event_table or {}).get('value') or {}).get('values') or []:
        event_rewards.append(flatten((node or {}).get('fields', {}), event_reward_layout))

    rewards = field_value('ArenaManager', 'rewards')
    arena_config = {k: field_value('ArenaConfig', k) for k in
                    ('RankSplit', 'SeasonTime', 'MaxRoomCount', 'MinRoomCount', 'SummaryTime', 'IsOpen')}
    rank_stars = field_value('PVP_Manager', 'MaxRankStars')

    not_decoded = []
    reward_items = (rewards.get('value') or {}).get('values') or \
        (rewards.get('value') or {}).get('items') or []
    if not any(isinstance(i, dict) and i.get('kind') == 'string' for i in reward_items):
        not_decoded.append(dict(item='ArenaManager.rewards contents',
                                blocking='string literal slot outside stringliteral.json'))
    for key, value in arena_config.items():
        if value is None:
            not_decoded.append(dict(item=f'ArenaConfig.{key}', blocking='static not assigned in .cctor'))
    if not rank_stars or (rank_stars.get('value') or {}).get('items') in (None, []):
        not_decoded.append(dict(item='PVP_Manager.MaxRankStars values',
                                blocking='InitializeArray token not resolved'))
    for cls, reason in failures.items():
        not_decoded.append(dict(item=f'{cls} statics', blocking=f'{reason["stage"]}: {reason["detail"]}'))

    usage_summary = dict(
        slots=len(usage_rows),
        string_literals=sum(1 for r in usage_rows if r['string'] is not None),
        unresolved=sum(1 for r in usage_rows if r['string'] is None),
        by_kind={str(k): sum(1 for r in usage_rows if r['token_kind'] == k)
                 for k in sorted({r['token_kind'] for r in usage_rows if r['token_kind'] is not None})})
    ia_rows = [row for entry in init_arrays.values() for m in entry for row in m['arrays']]
    ia_summary = dict(total=len(ia_rows),
                      ok=sum(1 for r in ia_rows if r['status'] == 'ok'),
                      status={s: sum(1 for r in ia_rows if r['status'] == s)
                              for s in sorted({r['status'] for r in ia_rows})})

    sources = []
    for path in (native_path,) + SOURCES[1:]:
        sources.append(dict(path=path, sha256=sha_file(path)))
    return dict(
        schema=1, evidence='STATIC_ONLY_ORIGINAL_APK',
        note='No emulator, device or probe. Static decode is not runtime behaviour.',
        provenance=dict(
            sources=sources,
            xapk_sha256=native.get('xapk_sha256'),
            libil2cpp_sha256=native.get('libil2cpp_sha256'),
            dump_sha256=native.get('dump_sha256'),
            families=native.get('families'),
            methods=len(native['methods']),
            classes=len({m['class_name'] for m in native['methods']})),
        metadata_usage=dict(summary=usage_summary, rows=usage_rows,
                            by_class=usage_by_class),
        initialize_arrays=dict(summary=ia_summary, by_class=init_arrays),
        unlocks=dict(arena_manager_rewards=rewards, arena_config=arena_config,
                     pvp_manager_max_rank_stars=rank_stars),
        shop_packs=shop_packs,
        event_season_pass=dict(rows=event_rewards, count=len(event_rewards)),
        gaps=[dict(item=item, note=note) for item, note in GAPS],
        initializer_statics=statics,
        not_decoded=not_decoded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', default=NATIVE)
    parser.add_argument('--output', default='datas/l2_535b0541_meta_rewards.json.gz')
    args = parser.parse_args()
    payload = build(args.native)
    target = ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(gzip.compress(json.dumps(payload, separators=(',', ':'),
                                                sort_keys=True).encode(), mtime=0))
    print(json.dumps(dict(bytes=target.stat().st_size, sha256=sha_file(args.output),
                          usage=payload['metadata_usage']['summary'],
                          initialize_arrays=payload['initialize_arrays']['summary'],
                          not_decoded=[n['item'] for n in payload['not_decoded']])))


if __name__ == '__main__':
    main()
