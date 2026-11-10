"""Write a new result directory, preserving all earlier calculations."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import tempfile
from .graphs import ROOT, require


def new_directory(requested=None, prefix='calculation'):
    if requested is None:
        base = ROOT / 'results'
        base.mkdir(exist_ok=True)
        return Path(tempfile.mkdtemp(prefix=prefix + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-', dir=base))
    path = Path(requested).expanduser().resolve()
    require(not path.exists(), 'The output path already exists; choose a new directory')
    require(ROOT not in path.parents or (ROOT / 'results') in path.parents,
            'Inside this repository, outputs must be placed beneath results/')
    path.mkdir(parents=True)
    return path


def write_json(path, obj):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def source_hashes():
    result = {}
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if any(p in ('.git', 'results', '__pycache__', '.ipynb_checkpoints') for p in rel.parts):
            continue
        if path.name in ('.DS_Store', 'Thumbs.db'):
            continue
        if path.is_file():
            result[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def verify_manifest(hashes):
    path = ROOT / 'SHA256SUMS.txt'
    require(path.is_file(), 'SHA256SUMS.txt is missing; use a complete release')
    expected = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        require(name not in expected and len(digest) == 64, 'Invalid checksum entry')
        expected[name] = digest
    actual = {p: h for p, h in hashes.items() if p != 'SHA256SUMS.txt'}
    differences = []
    for title, names in [
        ('Missing files', sorted(expected.keys() - actual.keys())),
        ('Changed files', sorted(p for p in expected.keys() & actual.keys() if expected[p] != actual[p])),
        ('Unlisted files', sorted(actual.keys() - expected.keys())),
    ]:
        if names:
            differences.append(title + ': ' + ', '.join(names[:12]) +
                               (f' (and {len(names)-12} more)' if len(names) > 12 else ''))
    require(not differences, '; '.join(differences) +
            '. Use the released inputs and place generated files beneath results/.')
    return {'files': len(expected), 'sha256_manifest': hashes['SHA256SUMS.txt']}
