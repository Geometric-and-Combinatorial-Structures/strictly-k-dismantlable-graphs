#!/usr/bin/env python3
"""Reproduce the finite calculations accompanying the mathematical proofs."""
import sys
sys.dont_write_bytecode = True
if sys.version_info < (3, 11):
    raise SystemExit('Python 3.11 or later is required.')
if not __debug__:
    raise SystemExit('Run verification without -O or -OO.')
import argparse
import time
from datetime import datetime, timezone
from dismantling import article, checks
from dismantling.output import new_directory, write_json, source_hashes, verify_manifest

CHECKS = [
    ('article', 'The 3k+8 family: reductions, clique counts and figures', article.run),
    ('4k4', 'The 4k+4 family: seven proof roots and nineteen clique rows', checks.check_4k4),
    ('6k6', 'The 6k+6 family: reductions and neighbourhood obstructions', checks.check_6k6),
    ('kernels', 'Completion of the eleven-vertex kernel', checks.check_kernels),
    ('homology', 'Reduced homology and the empty-complex convention', checks.boundaries),
    ('examples', 'Independent constructions at levels 1 to 6', checks.compare_constructions),
    ('deletions', 'Deleting one vertex from the 3k+8 family at levels 2 to 4', checks.deletion_controls),
    ('mutations', 'Rejection of deliberately altered certificates', checks.mutation_controls),
]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extended', action='store_true', help='Also check all small templates in the ranges stated in the guide.')
    parser.add_argument('--only', choices=[x[0] for x in CHECKS], help='Reproduce one group of results.')
    parser.add_argument('--output', help='A new directory; the default is a unique directory beneath results/.')
    args = parser.parse_args(argv)
    output = new_directory(args.output, 'reproduction')
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
              'status': 'INCONCLUSIVE', 'extended': args.extended, 'checks': [],
              'mathematical_scope': 'Finite verifications. The supplement proves the statements for every level.'}
    before = source_hashes()
    jobs = [('integrity', 'Integrity of the released files', lambda: verify_manifest(before))]
    jobs += [x for x in CHECKS if args.only is None or x[0] == args.only]
    if args.only is None:
        jobs.append(('templates', 'Layer identities on all templates in the stated finite ranges',
                     lambda: checks.template_controls(args.extended)))
        if args.extended:
            jobs.append(('kernel-identities', 'Kernel identities on all covered profiles with seed order at most 3', checks.kernel_controls))
    exit_code = 0
    for identifier, title, fn in jobs:
        print(title + ' ...', flush=True)
        start = time.monotonic()
        try:
            details = fn()
            record = {'id': identifier, 'title': title, 'status': 'PASS', 'details': details}
        except KeyboardInterrupt:
            record = {'id': identifier, 'title': title, 'status': 'INCONCLUSIVE', 'reason': 'Interrupted before completion.'}
            exit_code = 130
        except Exception as exc:
            record = {'id': identifier, 'title': title, 'status': 'FAIL', 'reason': f'{type(exc).__name__}: {exc}'}
            exit_code = 1
        record['seconds'] = round(time.monotonic() - start, 4)
        report['checks'].append(record)
        print('  ' + record['status'] + (': ' + record['reason'] if 'reason' in record else ''), flush=True)
        if exit_code:
            break
    after = source_hashes()
    report['inputs_unchanged'] = before == after
    if before != after:
        report['checks'].append({'id': 'input-preservation', 'status': 'FAIL', 'reason': 'A source file changed during the calculation.'})
        exit_code = 1
    done = {r['id'] for r in report['checks']}
    report['not_run'] = [identifier for identifier, _, _ in jobs if identifier not in done]
    report['status'] = 'PASS' if exit_code == 0 else ('INCONCLUSIVE' if exit_code == 130 else 'FAIL')
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    report['source_sha256'] = before
    write_json(output / 'report.json', report)
    lines = ['Reproduction of the finite calculations', '', 'Overall result: ' + report['status'], '']
    for r in report['checks']:
        lines.append(f"{r['status']}: {r.get('title', r['id'])}")
        if 'reason' in r:
            lines.append('  ' + r['reason'])
    if report['not_run']:
        lines.append('Not run: ' + ', '.join(report['not_run']))
    lines += ['', 'The calculations verify finite data. Results for every level follow from the proofs in the supplement.',
              'report.json records the computed values, the exact scope and the source checksums.', '']
    (output / 'report.txt').write_text('\n'.join(lines), encoding='utf-8')
    print('\n' + report['status'] + '. Results: ' + str(output), flush=True)
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
