#!/usr/bin/env python3
"""Execute every notebook cell in a fresh Python process against the exact source archive.

The released notebook uses ordinary Python only. The test supplies a local
archive through its documented test override, so it also works before a
release is published. Set --public to exercise the unmodified public URL.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import argparse
import json
import os
import subprocess
import zipfile
from dismantling.output import new_directory, source_hashes, write_json, verify_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', action='store_true')
    args = parser.parse_args()
    hashes = source_hashes()
    verify_manifest(hashes)
    out = new_directory(prefix='notebook-test')
    archive = out / 'release.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
        for name in hashes:
            zipped.write(ROOT / name, 'strictly-k-dismantlable-graphs-v1.1.1/' + name)
    nb = json.loads((ROOT / 'notebooks/reproduce.ipynb').read_text(encoding='utf-8'))
    ids = [cell.get('id') for cell in nb['cells']]
    if not all(isinstance(identifier,str) and identifier for identifier in ids) or len(set(ids)) != len(ids):
        raise ValueError('Every notebook cell must have a unique, non-empty id')
    codes = [''.join(cell['source']) for cell in nb['cells'] if cell['cell_type'] == 'code']
    runner = out / 'execute_cells.py'
    runner.write_text(
        'import sys\nsys.dont_write_bytecode = True\nimport json, time\n'
        'namespace = {"__name__": "__main__"}\n'
        'cells = ' + repr(codes) + '\n'
        'for number, cell in enumerate(cells, 1):\n'
        '    print("BEGIN NOTEBOOK CELL", number, flush=True)\n'
        '    exec(compile(cell, "notebook-cell-" + str(number), "exec"), namespace)\n'
        '    print("END NOTEBOOK CELL", number, flush=True)\n', encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    if args.public:
        env.pop('STRICT_DISMANTLING_ARCHIVE', None)
    else:
        env['STRICT_DISMANTLING_ARCHIVE'] = archive.as_uri()
    process = subprocess.run([sys.executable, str(runner)], cwd=out, env=env,
                             capture_output=True, text=True, encoding='utf-8')
    (out / 'execution.txt').write_text(process.stdout + '\n' + process.stderr, encoding='utf-8')
    completed = process.stdout.count('END NOTEBOOK CELL')
    passed = process.returncode == 0 and completed == len(codes)
    write_json(out / 'notebook_execution.json', {'status': 'PASS' if passed else 'FAIL',
               'code_cells': len(codes), 'completed_cells': completed, 'exit_code': process.returncode,
               'source_sha256': hashes['notebooks/reproduce.ipynb'],
               'archive': 'public release' if args.public else 'exact local release contents',
               'execution': 'Fresh Python process, all cells in document order, no previous notebook state.'})
    print(('PASS' if passed else 'FAIL') + f': {completed}/{len(codes)} notebook cells. Reports: {out}')
    if not passed:
        print(process.stderr)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
