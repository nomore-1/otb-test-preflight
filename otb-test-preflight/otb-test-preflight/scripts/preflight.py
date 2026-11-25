#!/usr/bin/env python3
"""Read-only checks for the OpenTenBase test runner environment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def inspect(home, search_path, source):
    checks = []

    def add(name, status, detail):
        checks.append({'check': name, 'status': status, 'detail': detail})

    root = Path(home).expanduser().resolve() if home else None
    if not root or not root.is_dir():
        add('OPENTENBASE_HOME', 'fail', 'Unset or not a directory')
    else:
        add('OPENTENBASE_HOME', 'pass', str(root))
    for name in ('postgres', 'pgxc_ctl', 'psql'):
        expected = root / 'bin' / name if root else None
        found = shutil.which(name, path=search_path)
        if not expected or not expected.is_file() or not os.access(expected, os.X_OK):
            add(name, 'fail', 'Missing or non-executable file under OPENTENBASE_HOME/bin')
        elif not found:
            add(name, 'fail', 'Executable not found on PATH')
        elif Path(found).resolve() != expected.resolve():
            add(name, 'fail', f'PATH resolves to {found}; expected {expected}')
        else:
            add(name, 'pass', str(expected))
    if source is not None:
        installed = root / 'bin' / 'postgres' if root else None
        try:
            if installed is None or not installed.is_file() or not source.is_file():
                add('postgres_binary_match', 'fail', 'Source or installed postgres binary missing')
            elif digest(source) == digest(installed):
                add('postgres_binary_match', 'pass', 'SHA-256 matches')
            else:
                add('postgres_binary_match', 'warn', 'SHA-256 differs; check whether reinstall is needed')
        except OSError as exc:
            add('postgres_binary_match', 'fail', str(exc))
    else:
        add('postgres_binary_match', 'skip', 'No --source-postgres supplied')
    summary = {s: sum(c['status'] == s for c in checks) for s in ('pass', 'warn', 'fail', 'skip')}
    return {'status': 'fail' if summary['fail'] else 'warn' if summary['warn'] else 'pass',
            'summary': summary, 'checks': checks}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', default=os.environ.get('OPENTENBASE_HOME'))
    parser.add_argument('--source-postgres', type=Path, help='Built source-tree postgres binary, optional')
    args = parser.parse_args(argv)
    report = inspect(args.home, os.environ.get('PATH', ''), args.source_postgres)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['status'] == 'fail' else 0


if __name__ == '__main__':
    sys.exit(main())
