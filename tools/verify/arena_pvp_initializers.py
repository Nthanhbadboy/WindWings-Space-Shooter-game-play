#!/usr/bin/env python3
"""Reference-only initializer pass for Arena/PvP static tables.

No code is executed: the pass follows recorded instruction records, resolves
relocation slots to metadata pointers, and models only the compiler idioms that
build `List<T>`, arrays and plain objects. Both List.Add paths append once, so the
pass takes the inline fast path and follows the unconditional skip. Anything it
does not model raises, so a table is either reconstructed from every instruction
or reported as not decoded.
"""
import gzip
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASS_INIT = 0x110d028
OBJECT_NEW = 0x110d240
ARRAY_NEW = 0x110d09c
INIT_ARRAY = 0x205b07c
REF_ADD = 0x1bd7e58
INT_ADD = 0x1b94d0c
SKIP = {'fmov', 'ldp', 'strb', 'movk', 'cmp', 'cmn', 'tst', 'fcmp', 'ccmp', 'nop', 'sub', 'tbnz',
        'tbz', 'cbz', 'cbnz', 'b.hi', 'b.hs', 'b.lo', 'b.ls', 'b.eq', 'b.ne', 'b.mi', 'b.pl',
        'b.ge', 'b.gt', 'b.le', 'b.lt'}


def class_layouts():
    """{class: {offset: (field, type)}} from dump.cs."""
    text = gzip.decompress((ROOT / 'reverse-engineering/il2cpp/dump.cs.gz').read_bytes()).decode()
    out = {}
    for block in text.split('// Namespace:'):
        head = re.search(r'(?:class|struct) (\S+).*?// TypeDefIndex:', block)
        if not head:
            continue
        fields = {}
        for line in block.split('\n'):
            match = re.match(r'\s*(?:public|private|protected|internal)\s+(?:static\s+)?(.+?)\s+(\w+);\s*//\s*0x([0-9A-Fa-f]+)\s*$', line)
            if match:
                fields[int(match[3], 16)] = (match[2], match[1].strip())
        out[head[1]] = fields
    return out


def blob_ints(event):
    """Candidate int32 lists from the captured InitializeArray slots."""
    out = []
    for hex_blob in event.get('blobs', []):
        if not hex_blob:
            continue
        raw = bytes.fromhex(hex_blob)
        ints = [int.from_bytes(raw[i:i + 4], 'little', signed=True) for i in range(0, len(raw), 4)]
        if ints and ints[0] == event['length']:
            out.append(ints[1:1 + event['length']])
    return out


def decode_class(native, cls, layouts=None):
    layouts = layouts or class_layouts()
    m = next(x for x in native['methods'] if x['class_name'] == cls and '.cctor' in x['signature'])
    insns = m['instructions']
    index = {i['rva']: n for n, i in enumerate(insns)}
    ia = {e['initialize_rva']: e for e in m.get('initialization', []) if 'initialize_rva' in e}
    strings = {e['addend']: e['string'] for e in m.get('slot_refs', []) if e.get('string')}
    slot_values = {e['slot_va']: e['addend'] for e in m.get('slot_refs', [])}
    pool_bytes = {e['instruction_rva']: e['hex'] for e in m.get('literals', [])}
    regs, objects, arrays, statics = {}, [], [], {}

    def key(name):
        match = re.fullmatch(r'[wx](\d+)', name)
        if match:
            return 'r' + match[1]
        return name

    def put(name, value):
        regs[key(name)] = value

    def resolve(value, depth=0):
        if value is None or depth > 8:
            return None
        if value[0] == 'const':
            return value[1]
        if value[0] == 'meta':
            if value[1] in strings:
                return dict(kind='string', text=strings[value[1]])
            return dict(kind='metadata', addend=value[1])
        if value[0] == 'pool':
            raw = bytes.fromhex(value[2])
            ints = [int.from_bytes(raw[i:i + 4], 'little', signed=True) for i in range(0, len(raw), 4)]
            chars = raw.decode('utf-16-le', 'replace') if len(raw) % 2 == 0 else ''
            return dict(kind='pool', va=hex(value[1]), raw=value[2], ints=ints,
                        text=chars if all(32 <= ord(c) < 127 for c in chars) else None)
        if value[0] == 'object':
            obj = objects[value[1]]
            return dict(kind='object', new_rva=obj['new_rva'], ctor_rva=obj['ctor_rva'],
                        ctor_args=obj.get('ctor_args'),
                        static_store_rva=obj.get('static_rva'),
                        fields={hex(k): resolve(v, depth + 1) for k, v in sorted(obj['fields'].items())},
                        items=[resolve(v, depth + 1) for v in obj.get('items', [])])
        if value[0] == 'array':
            arr = arrays[value[1]]
            values = arr['values']
            if arr.get('elements'):
                slots = arr['elements']
                if values:
                    values = list(values)
                else:
                    values = [None] * arr['length']
                for k in sorted(slots):
                    values[k] = resolve(slots[k], depth + 1)
            return dict(kind='array', new_rva=arr['new_rva'], length=arr['length'],
                        initialize_rva=arr.get('initialize_rva'), values=values,
                        blob_slot=arr.get('blob_slot'))
        return None

    pc = 0
    while pc < len(insns):
        insn = insns[pc]
        pc += 1
        op, args, rva = insn['mnemonic'], insn['op_str'].replace(']!', ']'), insn['rva']
        if op == 'strb':
            match = re.fullmatch(r'(\w+), \[(\w+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]', args)
            if match and ', [sp' not in args:
                src, base, off = match.groups()
                target = regs.get(key(base))
                if isinstance(target, tuple) and target[0] == 'statics':
                    value = ('const', 0) if src in ('wzr', 'xzr') else regs.get(key(src))
                    statics[int(off or '0', 0)] = value
                    continue
            continue
        if op == 'movi':
            match = re.fullmatch(r'v(\d+)\.2s, #(\d+)', args)
            if match and int(match.group(2)) <= 255:
                pair = struct.pack('<ii', int(match.group(2)), int(match.group(2))).hex()
                put('d' + match.group(1), ('pool', 0, pair))
                continue
            raise ValueError(f'{cls}: unmodelled movi {args} @ {rva:#x}')
        if op in SKIP:
            continue
        if op == 'mov':
            a, b = [x.strip() for x in args.split(',')]
            if b.startswith('#'):
                put(a, ('const', int(b[1:], 0)))
            elif b in ('xzr', 'wzr'):
                put(a, ('const', 0))
            else:
                put(a, regs.get(key(b)))
        elif op == 'adrp':
            a, b = [x.strip() for x in args.split(',')]
            put(a, ('addr', int(b[1:], 0)))
        elif op in ('ldr', 'ldrsw', 'ldur', 'ldrb'):
            if ', [sp' in args:
                continue
            match = re.fullmatch(r'(\w+), \[(\w+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]', args)
            if not match:
                raise ValueError(f'unparsed load {args} @ {rva:#x}')
            dest, base, off = match.groups()
            off = int(off or '0', 0)
            source = regs.get(key(base))
            value = None
            if isinstance(source, tuple):
                if source[0] == 'addr' and dest[0] in 'qds' and rva in pool_bytes:
                    put(dest, ('pool', source[1] + off, pool_bytes[rva]))
                    continue
                if source[0] == 'addr':
                    put(dest, ('slot', source[1] + off))
                    continue
                if source[0] == 'slot':
                    value = ('meta', slot_values.get(source[1] + off))
                elif source[0] == 'meta' and off == 0xb8:
                    value = ('statics', source[1])
                elif source[0] == 'object' and off == 0x10:
                    value = ('backing', source[1])
                elif source[0] == 'object' and off == 0:
                    value = ('self', source[1])
            put(dest, value)
        elif op in ('str', 'stur', 'stp'):
            if ', [sp' in args:
                continue
            if op == 'stp':
                pair = re.fullmatch(r'(\w+), (\w+), \[(\w+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]', args)
                if not pair:
                    raise ValueError(f'unparsed stp {args} @ {rva:#x}')
                first, second, base, off = pair.groups()
                off = int(off or '0', 0)
                target = regs.get(key(base))
                if isinstance(target, tuple) and target[0] == 'statics':
                    statics[off] = regs.get(key(first))
                    statics[off + 8] = regs.get(key(second))
                    continue
                raise ValueError(f'unmodelled stp target {args} @ {rva:#x}')
            match = re.fullmatch(r'(\w+), \[(\w+)(?:, #(-?0x[0-9a-f]+|-?\d+))?\]', args)
            if not match:
                raise ValueError(f'unparsed store {args} @ {rva:#x}')
            src, base, off = match.groups()
            off = int(off or '0', 0)
            target = regs.get(key(base))
            value = ('const', 0) if src in ('wzr', 'xzr') else regs.get(key(src))
            if isinstance(target, tuple):
                if target[0] == 'addr':
                    put(base, ('slot', target[1] + off))
                elif target[0] == 'object':
                    objects[target[1]]['fields'][off] = value
                elif target[0] == 'statics':
                    statics[off] = value
                    if isinstance(value, tuple) and value[0] in ('object', 'array'):
                        holder = objects[value[1]] if value[0] == 'object' else arrays[value[1]]
                        holder['static_rva'] = rva
                elif target[0] == 'array' and off >= 0x20:
                    arrays[target[1]].setdefault('elements', {})[(off - 0x20) // 8] = value
                elif target[0] in ('backing', 'self_off') and off == 0x20:
                    if not isinstance(value, tuple):
                        raise ValueError(f'unexpected element {args} @ {rva:#x}')
                    objects[target[1]].setdefault('items', []).append(value)
        elif op == 'add':
            parts = [x.strip() for x in args.split(',')]
            left = regs.get(key(parts[1]))
            tag = 'backing' if isinstance(left, tuple) and left[0] == 'backing' else 'self_off' if isinstance(left, tuple) and left[0] == 'self' else None
            put(parts[0], (tag, left[1]) if tag else None)
        elif op == 'bl':
            target = int(args.lstrip('#'), 0)
            arg0, arg1 = regs.get(key('x0')), regs.get(key('x1'))
            ctor_args = [regs.get(key('w' + str(n))) for n in range(1, 5)]
            ctor_args = [v[1] if isinstance(v, tuple) and v[0] == 'const' else None for v in ctor_args]
            for name in [n for n in regs if n.startswith('r') and n[1:].isdigit() and int(n[1:]) <= 18]:
                regs.pop(name, None)
            if target == CLASS_INIT:
                continue
            if target == OBJECT_NEW:
                if not isinstance(arg0, tuple):
                    raise ValueError(f'object_new without type @ {rva:#x}')
                objects.append(dict(new_rva=rva, type_ref=arg0, ctor_rva=None, fields={}, items=[]))
                put('x0', ('object', len(objects) - 1))
            elif target == ARRAY_NEW:
                if not isinstance(arg1, tuple) or arg1[0] != 'const':
                    raise ValueError(f'array_new without length @ {rva:#x}')
                arrays.append(dict(new_rva=rva, length=arg1[1], values=[], initialize_rva=None))
                put('x0', ('array', len(arrays) - 1))
            elif target == INIT_ARRAY:
                event = ia.get(rva)
                if not isinstance(arg0, tuple) or arg0[0] != 'array' or event is None:
                    raise ValueError(f'InitializeArray mismatch @ {rva:#x}')
                arrays[arg0[1]]['initialize_rva'] = rva
                arrays[arg0[1]]['blob_slot'] = event['slot_va']
                arrays[arg0[1]]['candidates'] = blob_ints(event)
            elif target in (REF_ADD, INT_ADD):
                if not isinstance(arg0, tuple) or arg0[0] != 'object':
                    raise ValueError(f'List.Add without list @ {rva:#x}')
                objects[arg0[1]].setdefault('items', []).append(arg1)
            elif isinstance(arg0, tuple) and arg0[0] == 'object' and objects[arg0[1]]['ctor_rva'] is None:
                objects[arg0[1]]['ctor_rva'] = target
                objects[arg0[1]]['ctor_args'] = ctor_args
        elif op == 'b':
            dest = int(args.lstrip('#'), 0)
            if dest not in index or dest <= rva:
                break
            pc = index[dest]
        elif op == 'ret':
            break
        else:
            raise ValueError(f'{cls}: unmodelled {op} {args} @ {rva:#x}')

    # Arrays that were filled by InitializeArray take the candidate matching their length.
    for arr in arrays:
        for candidate in arr.get('candidates', []):
            if len(candidate) == arr['length']:
                arr['values'] = candidate
                break
        if arr['values'] == [] and arr['length'] and not arr.get('elements') and not arr.get('candidates'):
            arr['values'] = None  # not decoded; never fabricated
            arr['not_decoded'] = 'initialize-array blob not resolved'

    fields = layouts.get(cls, {})
    expanded = {}
    for offset, value in list(statics.items()):
        if isinstance(value, tuple) and value[0] == 'pool':
            raw = bytes.fromhex(value[2])
            for k in range(0, len(raw), 4):
                word = raw[k:k + 4]
                declared = fields.get(offset + k, ('<unknown>', '?'))[1]
                if declared == 'float':
                    expanded[offset + k] = ('const', struct.unpack('<f', word)[0])
                elif declared == 'double' and len(raw) - k >= 8:
                    expanded[offset + k] = ('const', struct.unpack('<d', raw[k:k + 8])[0])
                    break
                else:
                    expanded[offset + k] = ('const', int.from_bytes(word, 'little', signed=True))
        elif isinstance(value, tuple) and value[0] == 'const' and abs(value[1]) > 0xffffffff:
            declared = fields.get(offset, ('<unknown>', '?'))[1]
            if declared == 'double':
                expanded[offset] = ('const', struct.unpack('<d', (value[1] & 0xffffffffffffffff).to_bytes(8, 'little'))[0])
        else:
            if isinstance(value, tuple) and value[0] == 'const' and fields.get(offset, ('', '?'))[1] == 'float':
                raw = (value[1] & 0xffffffff).to_bytes(4, 'little')
                expanded[offset] = ('const', struct.unpack('<f', raw)[0])
            else:
                expanded[offset] = value
    out = {}
    for offset, value in sorted(expanded.items()):
        name, declared = fields.get(offset, ('<unknown>', '?'))
        out[name] = dict(offset=hex(offset), declared=declared, value=resolve(value))
    return dict(method_rva=m['rva'], bytes=m['size'], fields=out,
                evidence='STATIC_INITIALIZER_IR_NOT_RUNTIME')
