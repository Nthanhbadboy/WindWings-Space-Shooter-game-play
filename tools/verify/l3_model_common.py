#!/usr/bin/env python3
"""Shared plumbing for the L3 *runtime model* tools of branch arena/a5a74747.

This module is deliberately small and side-effect free. It only provides:

* gzip JSON read/write and streamed read,
* SHA-256 pins for artifact/input files,
* the ``inputs``/``scope``/``decode_limits`` envelope used by the three model
  artifacts (``l3_particle_model``, ``l3_transition_model``, ``l3_driven_props``),
* a documented deterministic integer hash (splitmix64) used by the particle
  model so that a sample at time ``t`` is reproducible without stepping.

Nothing here claims Unity behaviour. Identities are always the qualified pair
``(serialized_file, path_id)`` from the APK export, never a global name match.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASK64 = (1 << 64) - 1


# --------------------------------------------------------------------------
# IO
# --------------------------------------------------------------------------
def sha256_file(path) -> str:
    """SHA-256 of a file's bytes (used to pin every artifact input)."""
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def read_json_gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        return json.load(fh)


def write_json_gz(path, obj) -> None:
    """Deterministic gzip write: sorted keys, fixed mtime, stable separators."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True,
                         separators=(',', ':')).encode('utf-8')
    with open(path, 'wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            gz.write(payload)


def repo_path(rel: str) -> Path:
    return ROOT / rel


def evidence(rel: str) -> dict:
    """Pin one repo input: relative path + SHA-256 (never a bare name)."""
    p = repo_path(rel)
    return {'path': rel, 'sha256': sha256_file(p) if p.exists() else None}


def inputs_map(rels) -> dict:
    return {rel: (sha256_file(repo_path(rel)) if repo_path(rel).exists() else None)
            for rel in rels}


# --------------------------------------------------------------------------
# Model envelope
# --------------------------------------------------------------------------
MODEL_NOTICE = (
    'MODEL OUTPUT — not Unity simulation, not a readback of engine state and not a '
    'render. Every number is produced by the bounded rules named in this artifact from '
    'APK-serialized inputs; where an input is absent the field says so instead of '
    'defaulting to an engine constant.'
)


def envelope(scope: str, inputs: dict, decode_limits) -> dict:
    return {
        'schema': 1,
        'provisional': True,
        'scope': scope,
        'model_notice': MODEL_NOTICE,
        'inputs': inputs,
        'decode_limits': list(decode_limits),
    }


def identity_key(obj) -> tuple:
    """Qualified identity of an exported object: (serialized_file, path_id)."""
    return (obj['serialized_file'], int(obj['path_id']))


def key_tuple(key) -> list:
    return [key[0], key[1]]


# --------------------------------------------------------------------------
# Deterministic hash used by the particle model
# --------------------------------------------------------------------------
def splitmix64(x: int) -> int:
    """splitmix64 finalizer — a documented, deterministic integer hash."""
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return (z ^ (z >> 31)) & MASK64


def uniform01(seed: int, stream: int, index: int) -> float:
    """Uniform [0,1) from (seed, stream, index).

    Deliberately NOT Unity's random generator: sequence equality with the engine
    is not claimed anywhere in this branch's artifacts.
    """
    h = splitmix64((seed & MASK64) ^ ((stream & 0xFFFFFFFF) << 32) ^ (index & 0xFFFFFFFF))
    return (h >> 11) * (1.0 / (1 << 53))


# --------------------------------------------------------------------------
# Small numeric helpers (float32-aware where the source stores float32)
# --------------------------------------------------------------------------
def f32(value: float) -> float:
    """Round a Python float to the nearest IEEE-754 binary32 value."""
    import struct
    return struct.unpack('<f', struct.pack('<f', float(value)))[0]


def fin(value) -> bool:
    """True when value is a finite JSON number (sentinel times are strings)."""
    return isinstance(value, (int, float)) and value == value and abs(value) != float('inf')


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def minmax_pair(scalar, min_scalar) -> dict:
    """Decode one serialized MinMaxCurve constant pair.

    The export carries only the two constants ``scalar`` and ``minScalar`` per
    curve. Which Unity MinMaxCurve *mode* produced them is not exported, so:

    * ``value``  = ``scalar`` — the constant the model uses by default;
    * ``bounds`` = the ordered pair, offered for spread models only;
    * ``mode``   = ``equal_values`` when both constants agree, else ``differs``.

    ``mode_proven`` is false everywhere: nothing in this repo proves the pair is
    a two-constants randomisation rather than a curve multiplier with a leftover
    second constant.
    """
    scalar = float(scalar)
    min_scalar = float(min_scalar)
    mode = 'equal_values' if scalar == min_scalar else 'differs'
    return {'value': scalar, 'min_scalar': min_scalar,
            'bounds': [min(min_scalar, scalar), max(min_scalar, scalar)],
            'mode': mode, 'mode_proven': False}
