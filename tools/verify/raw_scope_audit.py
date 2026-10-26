"""Inventory raw UI scopes, not an assertion that unindexed data is disposable."""
import csv
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'reverse-engineering/raw'


def ui_inventory():
    folder = RAW / 'ui'
    index = list(csv.DictReader((folder / '_index.csv').open()))
    active = {r['file'] for r in index}
    rows = []
    for path in sorted(folder.glob('*.json.gz')):
        rows.append(dict(file=path.name, compressed_bytes=path.stat().st_size,
                         in_current_index=path.name in active))
    all_names = {r['file'] for r in rows}
    return dict(index_path=str((folder / '_index.csv').relative_to(ROOT)),
                index_sha256=hashlib.sha256((folder / '_index.csv').read_bytes()).hexdigest(),
                indexed_rows=len(index), indexed_unique_files=len(active),
                indexed_nodes=sum(int(r['nodes']) for r in index),
                indexed_classes=len({r['class'] for r in index}),
                files_on_disk=len(rows), compressed_bytes=sum(r['compressed_bytes'] for r in rows),
                unindexed_files=len(all_names - active), missing_indexed_files=sorted(active - all_names),
                warning='Unindexed != invalid/duplicate; no deletion or cross-run merge approved by this inventory.',
                files=rows)


def main():
    # This snapshot is an inventory of the current checkout, not game evidence.
    result = dict(status='PROVISIONAL_PROCESS_AUDIT_NOT_GAME_FACT', ui=ui_inventory())
    dest = RAW / 'process-audit'
    dest.mkdir(exist_ok=True)
    with gzip.GzipFile(filename=str(dest / 'scope-inventory.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(result, indent=2).encode())
    print(json.dumps({k: v for k, v in result['ui'].items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
