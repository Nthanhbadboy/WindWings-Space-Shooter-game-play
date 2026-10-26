"""Preserve render metadata needed to interpret UI references; no font/image bytes."""
import gzip
import json
import os
from contextlib import ExitStack


def file_context(obj):
    reader = getattr(obj, 'object_reader', None) or obj
    sf = getattr(obj, 'assets_file', None) or getattr(reader, 'assets_file', None)
    return {'context_status': 'resolved' if sf is not None and getattr(sf, 'name', '') else 'missing_serialized_file',
            'serialized_file': str(getattr(sf, 'name', '')),
            'externals': [{'file_id': i + 1, 'path': str(getattr(e, 'path', getattr(e, 'name', '')))}
                          for i, e in enumerate(getattr(sf, 'externals', []))]}


def export_context(env, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    counts = {}
    kinds = ('Camera', 'Sprite', 'Material', 'Font', 'TMP_FontAsset')
    with ExitStack() as stack:
        streams = {k: stack.enter_context(gzip.open(os.path.join(output_dir, k + '.jsonl.gz'), 'wt'))
                   for k in kinds}
        for obj in env.objects:
            kind = obj.type.name
            if kind == 'MonoBehaviour':
                try:
                    head = obj.parse_monobehaviour_head()
                    kind = head.m_Script.deref_parse_as_object().m_ClassName
                except Exception:
                    continue
                if kind != 'TMP_FontAsset':
                    continue
            elif kind not in kinds:
                continue
            row = dict(file_context(obj), path_id=obj.path_id, type=kind)
            try:
                tree = obj.read_typetree()
                if kind == 'Font':
                    # Never embed raw font programs from the original game.
                    tree = {k: v for k, v in tree.items() if k in
                            ('m_Name', 'm_FontSize', 'm_Ascent', 'm_LineSpacing', 'm_DefaultMaterial')}
                if kind == 'Sprite':
                    tree = {k: v for k, v in tree.items() if k in
                            ('m_Name', 'm_Rect', 'm_Offset', 'm_Border', 'm_PixelsToUnits',
                             'm_Pivot', 'm_Extrude', 'm_IsPolygon', 'm_RenderDataKey', 'm_SpriteAtlas')}
                row['tree'] = tree
                row['status'] = 'exported'
            except Exception as exc:
                row.update(status='unresolved', error=str(exc)[:200])
            streams[kind].write(json.dumps(row, ensure_ascii=False, default=str) + '\n')
            counts[kind] = counts.get(kind, 0) + 1
    return counts
