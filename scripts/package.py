"""Build a reviewable source ZIP from an explicit public-file allowlist."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {'.gitignore', 'AGENTS.md', 'LICENSE', 'README.md', 'plugin.json',
         '.codex-plugin/plugin.json', '.agents/plugins/marketplace.json'}
DIRECTORIES = {'cofa_kit', 'docs', 'examples', 'prompts', 'scripts', 'skills', 'tests'}
EXTENSIONS = {'.py', '.md', '.json', '.jsonl', '.csv', '.yaml', '.yml', '.toml', '.ps1', '.sh'}


def public_files():
    result = [ROOT / name for name in sorted(FILES)]
    for name in sorted(DIRECTORIES):
        for path in sorted((ROOT / name).rglob('*')):
            if '__pycache__' in path.parts or not path.is_file():
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
                raise ValueError(f'Public file is a symlink or escapes repository: {path.name}')
            if path.suffix in EXTENSIONS:
                result.append(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='dist/cofa-ready-kit.zip')
    parser.add_argument('--list', action='store_true', help='print approved paths without making an archive')
    args = parser.parse_args()
    paths = public_files()
    if args.list:
        print('\n'.join(path.relative_to(ROOT).as_posix() for path in paths))
        return
    target = (ROOT / args.output).resolve()
    if not target.is_relative_to(ROOT) or target.suffix != '.zip':
        parser.error('output must be a .zip inside this repository')
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, 'cofa-ready-kit/' + path.relative_to(ROOT).as_posix())
    print(json.dumps({'archive': str(target), 'files': len(paths), 'bytes': target.stat().st_size,
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
