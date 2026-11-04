"""Opt-in local skill comparison and a synthetic MCP stdio smoke check."""
import json
from pathlib import Path
import stat
import shutil
import subprocess
import sys
import tempfile

from . import __version__
from .core import KitError, workspace_root

KIT = Path(__file__).resolve().parents[1]
SKILLS = ('cofa-build', 'cofa-explain', 'cofa-model-eval', 'cofa-semiconductor',
          'cofa-triage', 'cofa-verify')
TOOLS = {'workspace_check', 'profile_csv', 'semiconductor_yield', 'spc_monitor',
         'csv_join_audit', 'evidence_freshness'}


def _safe_path(root, path):
    """Reject linked components before reading even an in-workspace target."""
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            return False
        if current.exists():
            attributes = getattr(current.lstat(), 'st_file_attributes', 0)
            if attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024):
                return False
    return True


def skill_status(workspace):
    root = workspace_root(workspace)
    results = []
    for name in SKILLS:
        source = KIT / 'skills' / name
        dest = root / '.agents' / 'skills' / name
        item = {'name': name, 'source': str(source / 'SKILL.md'),
                'installed': str(dest), 'status': 'not_installed'}
        try:
            if not _safe_path(KIT, source) or not (source / 'SKILL.md').is_file():
                raise ValueError('packaged skill is missing or linked')
            files = sorted(p for p in source.rglob('*') if p.is_file() or p.is_symlink())
            if any(not _safe_path(KIT, p) for p in files):
                raise ValueError('packaged skill contains a linked path')
            if not _safe_path(root, dest):
                raise ValueError('installed skill path is linked; not read')
            if dest.exists():
                changed, missing = [], []
                for path in files:
                    relative = path.relative_to(source)
                    installed = dest / relative
                    if not _safe_path(root, installed):
                        raise ValueError('installed file path is linked; not read')
                    if not installed.is_file():
                        missing.append(relative.as_posix())
                    elif (installed.stat().st_size != path.stat().st_size
                          or path.stat().st_size > 1024 * 1024
                          or installed.read_bytes() != path.read_bytes()):
                        changed.append(relative.as_posix())
                item.update(status='different' if changed else 'incomplete' if missing else 'current',
                            changed_files=changed, missing_files=missing)
        except (OSError, ValueError) as exc:
            item.update(status='error', error=str(exc))
        results.append(item)
    return results


def mcp_smoke():
    """Replay a bounded local stdio session using disposable synthetic data."""
    try:
        with tempfile.TemporaryDirectory(prefix='cofa-mcp-check-') as temp:
            root = Path(temp)
            (root / 'sample.csv').write_text('name,value\na,1\nb,3\n', encoding='utf-8')
            messages = [
                {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
                    'protocolVersion': '2025-11-25', 'capabilities': {},
                    'clientInfo': {'name': 'cofa-doctor', 'version': __version__}}},
                {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
                {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                 'params': {'name': 'profile_csv', 'arguments': {'path': 'sample.csv'}}},
            ]
            payload = ('\n'.join(json.dumps(m) for m in messages) + '\n').encode('utf-8')
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                process = subprocess.run(
                    [sys.executable, '-B', '-u', str(KIT / 'scripts' / 'mcp_server.py'), '--workspace', temp],
                    input=payload, cwd=temp, stdout=stdout, stderr=stderr, timeout=15)
                stdout.seek(0)
                raw = stdout.read(256 * 1024 + 1)
            if process.returncode or len(raw) > 256 * 1024:
                raise ValueError('local MCP process failed or exceeded the response limit')
            replies = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
            if (any(not isinstance(r, dict) for r in replies)
                    or [r.get('id') for r in replies] != [1, 2, 3]
                    or any('error' in r for r in replies)):
                raise ValueError('invalid MCP session replies')
            init, listing, call = [r['result'] for r in replies]
            if init['protocolVersion'] != '2025-11-25' or init['serverInfo']['version'] != __version__:
                raise ValueError('unexpected local MCP protocol or kit version')
            names = {t['name'] for t in listing['tools']}
            if names != TOOLS:
                raise ValueError('local MCP tool list differs from this kit release')
            data = json.loads(call['content'][0]['text'])
            if (call.get('isError') is not False or data['rows_sampled'] != 2
                    or data['columns'][1]['numeric']['mean'] != 2
                    or call.get('structuredContent') != data):
                raise ValueError('synthetic CSV result did not match the known values')
            return {'status': 'passed', 'server_version': init['serverInfo']['version'],
                    'protocol_version': init['protocolVersion'], 'tools': sorted(names),
                    'synthetic_csv_rows': 2}
    except (OSError, ValueError, KeyError, TypeError, IndexError, RecursionError, subprocess.TimeoutExpired) as exc:
        return {'status': 'failed', 'error': str(exc),
                'next': 'Use the existing CLI or tools; check the kit path and Python runtime.'}


def plugin_support():
    """Inspect local CLI help only; never install or change configuration."""
    executable = shutil.which('codex')
    if not executable:
        return {'status': 'unavailable', 'reason': 'Codex CLI was not found', 'installation_checked': False}
    commands = [('plugin', '--help'), ('plugin', 'add', '--help'),
                ('plugin', 'marketplace', 'add', '--help')]
    try:
        for arguments in commands:
            result = subprocess.run([executable, *arguments], capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=8)
            if result.returncode != 0 or 'codex plugin' not in result.stdout.lower():
                return {'status': 'unavailable', 'reason': 'This CLI does not expose the required plugin commands',
                        'installation_checked': False}
        return {'status': 'supported', 'executable': executable, 'installation_checked': False,
                'next': 'The CLI exposes plugin install commands. Add the kit marketplace and install cofa-ready-kit@cofa-ready, then verify the installed skills.'}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'failed', 'reason': type(exc).__name__, 'installation_checked': False}


def diagnose(workspace=None, check_mcp=False, check_plugins=False):
    if check_mcp and workspace is None:
        raise KitError('--check-mcp requires --workspace')
    skills = skill_status(workspace) if workspace is not None else []
    mcp = mcp_smoke() if check_mcp else {'status': 'not_checked'}
    plugins = plugin_support() if check_plugins else {'status': 'not_checked'}
    needs_attention = any(s['status'] in ('different', 'incomplete', 'error') for s in skills)
    return {'kit_version': __version__, 'skills': skills, 'local_mcp': mcp, 'plugins': plugins,
            'ok': not needs_attention and mcp['status'] != 'failed'
                  and plugins['status'] in ('supported', 'not_checked'),
            'client_connection_checked': False, 'remote_mcp_checked': False,
            'next': 'Different does not mean outdated: it may be customized. Preserve installed files and read the source SKILL.md directly. Uninstalled skills are optional.',
            'scope': 'Compares packaged skill files only. MCP check uses a temporary synthetic workspace, not task data or the active Cofa connection. No settings are changed.'}
