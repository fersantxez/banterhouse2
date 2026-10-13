#!/usr/bin/env python3
"""Export audited source to a new directory and optionally ZIP it, without Git history."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from check_public_repo import ROOT, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        parser.error('destination must not exist; previous exports are never overwritten')
    names, size, links, problems = audit()
    if problems:
        raise SystemExit('Export blocked; run make public-check and resolve its findings.')
    archive = args.archive.resolve() if args.archive else None
    manifest = archive.with_suffix('.manifest.json') if archive else destination.parent / (destination.name + '.manifest.json')
    if manifest.exists() or (archive and archive.exists()):
        parser.error('archive and manifest must not exist')
    rows = []
    destination.mkdir(parents=True)
    for name in names:
        source = ROOT / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        data = target.read_bytes()
        rows.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    if archive:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as output:
            for row in rows:
                output.write(destination / row['path'], 'banterhouse2/' + row['path'])
    report = {'scope': 'source export, not a compiled game or runtime certification',
              'files': rows, 'total_bytes': size, 'local_markdown_links_checked': links}
    if archive:
        report['archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: exported {len(rows)} files to {destination}; manifest: {manifest}')
    if archive:
        print(f'ZIP: {archive}')


if __name__ == '__main__':
    main()
