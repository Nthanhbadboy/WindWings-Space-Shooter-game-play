"""Bounded stdlib streams for geometry #6; never build the full Graph in memory.
provenance: arena/8141386a-windwings-space-shooter-game-p
"""
from __future__ import annotations

from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw/geometry-8141386a/atlas'
BRANCH = 'arena/8141386a-windwings-space-shooter-game-p'
BATCH = 250


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


@contextmanager
def scratch(prefix='atlas-'):
    base = ROOT / '.arena/geometry-8141386a'
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base, prefix=prefix) as directory:
        yield Path(directory)


def write_document(path, header, arrays=()):
    """Append one record at a time; fixed flush schedule and gzip header, atomic replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with scratch('write-') as tmp:
        work = tmp / 'out.gz'
        with work.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, filename='', mode='wb', mtime=0,
                               compresslevel=9) as stream:
                stream.write(canonical(header)[:-1])
                for name, rows in arrays:
                    stream.write(b',' + canonical(name) + b':[')
                    for i, row in enumerate(rows):
                        if i:
                            stream.write(b',')
                        stream.write(canonical(row))
                        if (i + 1) % BATCH == 0:
                            stream.flush()
                    stream.write(b']')
                stream.write(b'}\n')
        work.replace(path)


class JsonStream:
    """Incremental raw_decode with an explicit per-value, not per-file, budget."""
    def __init__(self, handle, chunk=65536, budget=16 * 1024 * 1024):
        self.handle, self.chunk, self.budget = handle, chunk, budget
        self.buffer, self.pos, self.eof = '', 0, False
        self.decoder = json.JSONDecoder(parse_constant=self.bad_constant)

    @staticmethod
    def bad_constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)

    def fill(self):
        self.buffer = self.buffer[self.pos:]
        self.pos = 0
        part = self.handle.read(self.chunk)
        if not part:
            self.eof = True
        self.buffer += part
        if len(self.buffer) > self.budget:
            raise ValueError('JSON per-value budget exceeded')

    def peek(self):
        while True:
            while self.pos < len(self.buffer) and self.buffer[self.pos].isspace():
                self.pos += 1
            if self.pos < len(self.buffer):
                return self.buffer[self.pos]
            if self.eof:
                return ''
            self.fill()

    def take(self, expected):
        if self.peek() != expected:
            raise ValueError('expected JSON delimiter ' + repr(expected))
        self.pos += 1

    def value(self):
        self.peek()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.pos)
            except json.JSONDecodeError as error:
                if self.eof:
                    raise ValueError('truncated/invalid JSON value') from error
                self.fill()
                continue
            # A number can otherwise be accepted halfway through 123 or 1e+3.
            if end == len(self.buffer) and not self.eof:
                self.fill()
                continue
            if end < len(self.buffer) and self.buffer[end] not in ',]} \r\n\t:':
                if self.eof:
                    raise ValueError('invalid JSON value boundary')
                self.fill()
                continue
            self.pos = end
            return value


def iter_arrays_handle(handle, wanted, chunk=65536):
    """Yield (top-level array name, ordinal, one item), skipping other arrays by item.

    No entire `sprites`, peer bounds/mappings or output array is ever decoded at once.
    """
    s = JsonStream(handle, chunk=chunk)
    s.take('{')
    fields = set()
    if s.peek() != '}':
        while True:
            name = s.value()
            if not isinstance(name, str) or name in fields:
                raise ValueError('invalid/duplicate JSON root field')
            fields.add(name)
            s.take(':')
            if s.peek() == '[':
                s.take('[')
                i = 0
                if s.peek() != ']':
                    while True:
                        value = s.value()
                        if name in wanted:
                            yield name, i, value
                        i += 1
                        if s.peek() == ']':
                            break
                        s.take(',')
                s.take(']')
            else:
                s.value()
            if s.peek() == '}':
                break
            s.take(',')
    s.take('}')
    if s.peek():
        raise ValueError('trailing JSON content')
    if not set(wanted) <= fields:
        raise ValueError('requested array field absent: ' + str(set(wanted) - fields))


def iter_arrays(path, wanted):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        yield from iter_arrays_handle(stream, set(wanted))


def iter_geometry():
    """Verify every source row count + decoded SHA while reading only one JSONL row."""
    folder = ROOT / 'reverse-engineering/raw/sprite-geometry'
    index = json.loads((folder / 'index.json').read_bytes())
    for part in index['files']:
        path = folder / part['path']
        digest, count = hashlib.sha256(), 0
        with gzip.open(path, 'rb') as stream:
            for number, line in enumerate(stream):
                if len(line) > 8 * 1024 * 1024:
                    raise ValueError('raw geometry record budget')
                digest.update(line)
                count += 1
                yield json.loads(line), dict(path=str(path.relative_to(ROOT)), row=number)
        if count != part['rows'] or digest.hexdigest() != part['sha256_decompressed']:
            raise ValueError('geometry decoded SHA/row drift: ' + str(path))


def full_file(value):
    return value if value.startswith('data.unity3d/') else 'data.unity3d/' + value


def key(row):
    return full_file(row['serialized_file']), int(row['path_id'])


def identity(k):
    return dict(serialized_file=k[0], path_id=k[1]) if k else None
