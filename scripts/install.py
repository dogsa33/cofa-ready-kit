"""Copy focused skills or print optional MCP settings; never edit Codex config."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

KIT = Path(__file__).resolve().parents[1]
MCP_PRESETS = {
    'openai-docs': ('openai_docs', 'https://developers.openai.com/mcp'),
    'microsoft-learn': ('microsoft_learn', 'https://learn.microsoft.com/api/mcp'),
    'deepwiki': ('deepwiki', 'https://mcp.deepwiki.com/mcp'),
    'context7': ('context7', 'https://mcp.context7.com/mcp'),
}


def install(workspace, dry_run=False):
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('workspace must be an existing directory')
    target = root / '.agents' / 'skills'
    if not target.resolve().is_relative_to(root):
        raise ValueError('skill destination escapes workspace through a symlink')
    sources = sorted((KIT / 'skills').glob('*/SKILL.md'))
    if not sources:
        raise ValueError('no packaged skills found')
    actions = []
    for source in sources:
        if any(p.is_symlink() for p in [source.parent, *source.parent.rglob('*')]):
            raise ValueError(f'packaged skill contains a symlink: {source.parent}')
        dest = target / source.parent.name
        if dest.exists() or dest.is_symlink():
            if dest.is_symlink() or not dest.is_dir():
                raise ValueError(f'refusing existing non-directory: {dest}')
            if any(p.is_symlink() for p in dest.rglob('*')):
                raise ValueError(f'existing skill contains a symlink: {dest}')
            files = [p for p in source.parent.rglob('*') if p.is_file()]
            identical = all((dest / p.relative_to(source.parent)).is_file()
                            and (dest / p.relative_to(source.parent)).read_bytes() == p.read_bytes()
                            for p in files)
            if not identical:
                raise ValueError(f'existing skill differs; keep or rename it yourself: {dest}')
            actions.append((source.parent, dest, 'already present'))
        else:
            actions.append((source.parent, dest, 'copy'))
    for source, dest, action in actions:
        if not dry_run and action == 'copy':
            shutil.copytree(source, dest)
    return {'workspace': str(root), 'dry_run': dry_run,
            'skills': [{'name': a.name, 'action': c} for a, b, c in actions],
            'next': 'Use the provided Codex; if discovery fails, ask it to read the SKILL.md path directly.'}


def remote_server(value):
    name, separator, url = value.partition('=')
    if not separator or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', name):
        raise ValueError('--remote-mcp must be NAME=HTTPS_URL with a simple server name')
    if name == 'cofa_local':
        raise ValueError('cofa_local is reserved for the local kit server')
    try:
        parsed = urlsplit(url)
        valid = (parsed.scheme == 'https' and parsed.hostname and not parsed.username
                 and not parsed.password and not parsed.query and not parsed.fragment
                 and not any(c.isspace() or ord(c) < 32 for c in url)
                 and '\\' not in url)
        parsed.port  # Reject malformed ports before printing a candidate.
    except ValueError:
        valid = False
    if not valid:
        raise ValueError('remote MCP URL must be HTTPS without credentials, query, fragment, or whitespace')
    return name, {'url': url}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key in MCP JSON; preserve the original and resolve it first')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('MCP settings must use standard JSON numbers')


def mcp_config(workspace, with_openai_docs=False, presets=(), remote_mcp=(), merge_mcp=None):
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('workspace must be a directory')
    config = {'mcpServers': {}}
    if merge_mcp is not None:
        with Path(merge_mcp).open('rb') as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError('existing MCP JSON exceeds 1 MiB')
        config = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object,
                            parse_constant=reject_constant)
        if (not isinstance(config, dict) or not isinstance(config.get('mcpServers'), dict)
                or any(not isinstance(v, dict) for v in config['mcpServers'].values())):
            raise ValueError('existing MCP JSON must contain a mcpServers object of server objects')
    servers = config['mcpServers']

    def add(name, settings):
        if name in servers and servers[name] != settings:
            raise ValueError(f'existing MCP server differs: {name}; no settings were overwritten')
        servers[name] = settings

    add('cofa_local', {
        'command': sys.executable,
        'args': ['-u', str(KIT / 'scripts' / 'mcp_server.py'), '--workspace', str(root)]
    })
    selected = [*presets, *(['openai-docs'] if with_openai_docs else [])]
    for preset in selected:
        if preset not in MCP_PRESETS:
            raise ValueError('unknown MCP preset')
        name, url = MCP_PRESETS[preset]
        add(name, {'url': url})
    for value in remote_mcp:
        name, settings = remote_server(value)
        add(name, settings)
    return config


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace', required=True)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--mcp-json', action='store_true', help='print optional MCP server JSON; make no changes')
    p.add_argument('--with-openai-docs', action='store_true',
                   help='include the remote public OpenAI Docs server in printed JSON; requires --mcp-json')
    p.add_argument('--mcp-preset', action='append', choices=sorted(MCP_PRESETS), default=[],
                   help='include an official remote endpoint; repeat to select servers; requires --mcp-json')
    p.add_argument('--remote-mcp', action='append', default=[], metavar='NAME=HTTPS_URL',
                   help='include a custom remote endpoint without credentials; requires --mcp-json')
    p.add_argument('--merge-mcp', metavar='JSON_FILE',
                   help='preserve existing settings in printed JSON; fail on conflicts; requires --mcp-json')
    args = p.parse_args()
    if args.with_openai_docs and not args.mcp_json:
        p.error('--with-openai-docs requires --mcp-json; no settings or skills were changed')
    if (args.mcp_preset or args.remote_mcp or args.merge_mcp) and not args.mcp_json:
        p.error('MCP options require --mcp-json; no settings or skills were changed')
    try:
        result = (mcp_config(args.workspace, with_openai_docs=args.with_openai_docs,
                             presets=args.mcp_preset, remote_mcp=args.remote_mcp, merge_mcp=args.merge_mcp)
                  if args.mcp_json else install(args.workspace, args.dry_run))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RecursionError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
