#!/usr/bin/env python3
"""Offline inventory only: does not install tools, execute found binaries or test targets."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = ('claude', 'git', 'subfinder', 'dnsx', 'httpx', 'katana', 'gau', 'waybackurls', 'ffuf', 'nuclei')

def inspect(root=ROOT):
    required = ['SKILL.md', 'data/reports.jsonl', 'data/test-cards.json',
                'scripts/scope_check.py', 'scripts/session.py', 'scripts/evidence.py',
                'references/operating-model.md', 'references/verification.md']
    missing = [name for name in required if not (root/name).is_file()]
    integrity_errors = []
    manifest = root/'file-manifest.json'
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding='utf-8-sig'))
        for row in data['files']:
            path = (root/row['path']).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():
                integrity_errors.append(row['path']+': missing or unsafe')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                integrity_errors.append(row['path']+': changed')
    return {'skill': 'Redhood', 'version': '1.0.0', 'python': sys.version.split()[0],
            'python_supported': sys.version_info >= (3, 10), 'missing_required': missing,
            'manifest_checked': manifest.is_file(), 'integrity_errors': integrity_errors,
            'optional_executables': {name: shutil.which(name) for name in OPTIONAL},
            'notice': 'Paths only, not tool identity/version/functionality verification. httpx may be the unrelated Python CLI. Inspect actual help/version before use. No network enforcement or target tests performed.'}

def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    result = inspect()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result['python_supported'] and not result['missing_required'] and not result['integrity_errors'] else 2

if __name__ == '__main__':
    try: raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr); raise SystemExit(2)
