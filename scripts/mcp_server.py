"""Optional, local, read-only MCP stdio adapter. No sockets or model/API calls."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))
from cofa_kit import __version__

VERSIONS = ('2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05')
MAX_MESSAGE = 64 * 1024
MAX_OUTPUT = 128 * 1024
TOOLS = [
    {'name': 'evidence_freshness',
     'description': 'Read-only SHA256 comparison of explicitly watched run files. Freshness is separate from command success and cannot detect forged metadata or untracked changes.',
     'inputSchema': {'type': 'object', 'properties': {'result_path': {'type': 'string'}},
                     'required': ['result_path'], 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
    {'name': 'workspace_check',
     'description': 'Check required artifact/evidence existence and declared completion. This does NOT prove functional correctness.',
     'inputSchema': {'type': 'object', 'properties': {'manifest': {'type': 'string', 'default': 'requirements.json'}}, 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
    {'name': 'profile_csv',
     'description': 'Summarize a local CSV within the workspace: missing values, duplicates, and numeric ranges, with a bounded row sample.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'}, 'encoding': {'type': 'string', 'enum': ['utf-8-sig', 'cp949'], 'default': 'utf-8-sig'},
         'max_rows': {'type': 'integer', 'minimum': 1, 'maximum': 10000, 'default': 10000}}, 'required': ['path'], 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
    {'name': 'semiconductor_yield',
     'description': 'Compute weighted passed/tested counts by confirmed groups. Reject duplicate row keys and invalid counts; not a quality acceptance decision.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'},
         'group_by': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 16},
         'key': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 16},
         'tested_col': {'type': 'string', 'default': 'tested'}, 'passed_col': {'type': 'string', 'default': 'passed'},
         'encoding': {'type': 'string', 'enum': ['utf-8-sig', 'cp949'], 'default': 'utf-8-sig'},
         'max_rows': {'type': 'integer', 'minimum': 1, 'maximum': 10000, 'default': 10000}},
         'required': ['path', 'group_by', 'key'], 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
    {'name': 'spc_monitor',
     'description': 'Evaluate one ordered measurement stream against a frozen prefix I-MR baseline. Flags need review; they are not product defects or proven root causes.',
     'inputSchema': {'type': 'object', 'properties': {
         'path': {'type': 'string'}, 'value_col': {'type': 'string'}, 'time_col': {'type': 'string'},
         'baseline_count': {'type': 'integer', 'minimum': 3, 'maximum': 10000},
         'series_cols': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 16},
         'encoding': {'type': 'string', 'enum': ['utf-8-sig', 'cp949'], 'default': 'utf-8-sig'},
         'max_rows': {'type': 'integer', 'minimum': 1, 'maximum': 10000, 'default': 10000}},
         'required': ['path', 'value_col', 'time_col', 'baseline_count'], 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
    {'name': 'csv_join_audit',
     'description': 'Audit two local CSV key relationships and predict join row multiplication without executing a join. Counts only; does not prove business semantics or aggregate conservation.',
     'inputSchema': {'type': 'object', 'properties': {
         'left_path': {'type': 'string'}, 'right_path': {'type': 'string'},
         'left_key': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 16},
         'right_key': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 16},
         'relationship': {'type': 'string', 'enum': ['one_to_one', 'many_to_one', 'one_to_many', 'many_to_many']},
         'encoding': {'type': 'string', 'enum': ['utf-8-sig', 'cp949'], 'default': 'utf-8-sig'},
         'max_rows': {'type': 'integer', 'minimum': 1, 'maximum': 10000, 'default': 10000}},
         'required': ['left_path', 'right_path', 'left_key', 'right_key', 'relationship'], 'additionalProperties': False},
     'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}
]


def reject_non_json_number(value):
    raise ValueError(f'Invalid JSON number: {value}')


def local_path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError('path must be a nonempty workspace-relative path')
    path = (root / value).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('path must be a file inside the workspace')
    return path


def column_name(value):
    if not isinstance(value, str) or not value.strip() or ',' in value or len(value) > 256:
        raise ValueError('column names must be nonempty strings without commas, at most 256 characters')
    return value


def column_list(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 16:
        raise ValueError('column list must contain 1 to 16 names')
    names = [column_name(item) for item in value]
    if len(names) != len(set(names)):
        raise ValueError('column list contains duplicates')
    return ','.join(names)


def call_tool(root, name, args):
    if not isinstance(args, dict):
        raise ValueError('arguments must be an object')
    if name == 'evidence_freshness':
        if set(args) != {'result_path'}:
            raise ValueError('evidence_freshness requires only result_path')
        local_path(root, args.get('result_path'))
        # Preserve the original spelling so the CLI can reject symlink/reparse
        # components instead of hiding them through resolve().
        command = ['evidence', 'check', '--workspace', str(root), '--result', args['result_path']]
    elif name == 'workspace_check':
        if set(args) - {'manifest'}:
            raise ValueError('unknown argument')
        manifest = local_path(root, args.get('manifest', 'requirements.json'))
        command = ['check', '--workspace', str(root), '--manifest', str(manifest.relative_to(root))]
    elif name == 'profile_csv':
        if set(args) - {'path', 'encoding', 'max_rows'}:
            raise ValueError('unknown argument')
        path = local_path(root, args.get('path'))
        encoding = args.get('encoding', 'utf-8-sig')
        rows = args.get('max_rows', 10000)
        if encoding not in ('utf-8-sig', 'cp949') or type(rows) is not int or not 1 <= rows <= 10000:
            raise ValueError('invalid encoding or max_rows')
        command = ['profile', str(path), '--format', 'csv', '--encoding', encoding, '--max-rows', str(rows)]
    elif name == 'csv_join_audit':
        if set(args) - {'left_path', 'right_path', 'left_key', 'right_key', 'relationship', 'encoding', 'max_rows'}:
            raise ValueError('unknown argument')
        left = local_path(root, args.get('left_path'))
        right = local_path(root, args.get('right_path'))
        left_key, right_key = column_list(args.get('left_key')), column_list(args.get('right_key'))
        if len(args['left_key']) != len(args['right_key']):
            raise ValueError('left_key and right_key must have the same number of columns')
        relationship = args.get('relationship')
        if not isinstance(relationship, str) or relationship not in ('one_to_one', 'many_to_one', 'one_to_many', 'many_to_many'):
            raise ValueError('invalid or missing relationship')
        encoding = args.get('encoding', 'utf-8-sig')
        rows = args.get('max_rows', 10000)
        if encoding not in ('utf-8-sig', 'cp949') or type(rows) is not int or not 1 <= rows <= 10000:
            raise ValueError('invalid encoding or max_rows')
        command = ['data', 'join-check', str(left), str(right), '--left-key', left_key,
                   '--right-key', right_key, '--relationship', relationship, '--encoding', encoding, '--max-rows', str(rows)]
    elif name in ('semiconductor_yield', 'spc_monitor'):
        extra = {'group_by', 'key', 'tested_col', 'passed_col'} if name == 'semiconductor_yield' else {'value_col', 'time_col', 'baseline_count', 'series_cols'}
        if set(args) - ({'path', 'encoding', 'max_rows'} | extra):
            raise ValueError('unknown argument')
        path = local_path(root, args.get('path'))
        encoding = args.get('encoding', 'utf-8-sig')
        rows = args.get('max_rows', 10000)
        if encoding not in ('utf-8-sig', 'cp949') or type(rows) is not int or not 1 <= rows <= 10000:
            raise ValueError('invalid encoding or max_rows')
        if name == 'semiconductor_yield':
            command = ['semi', 'yield', str(path), '--group-by', column_list(args.get('group_by')),
                       '--key', column_list(args.get('key')), '--tested-col', column_name(args.get('tested_col', 'tested')),
                       '--passed-col', column_name(args.get('passed_col', 'passed'))]
        else:
            count = args.get('baseline_count')
            if type(count) is not int or not 3 <= count <= rows:
                raise ValueError('baseline_count must be an integer between 3 and max_rows')
            command = ['semi', 'spc', str(path), '--value-col', column_name(args.get('value_col')),
                       '--time-col', column_name(args.get('time_col')), '--baseline-count', str(count)]
            if 'series_cols' in args:
                command.extend(['--series-cols', column_list(args['series_cols'])])
        command.extend(['--encoding', encoding, '--max-rows', str(rows)])
    else:
        raise ValueError('unknown tool')
    # Disk-backed capture avoids unbounded process-output memory. The CLI has its own input bounds.
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        result = subprocess.run([sys.executable, '-X', 'utf8', str(KIT / 'scripts' / 'cofa.py'), *command],
                                cwd=root, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=30)
        stdout.seek(0)
        stderr.seek(0)
        data = stdout.read(MAX_OUTPUT + 1)
        errors = stderr.read(4096)
    if len(data) > MAX_OUTPUT:
        raise ValueError('result exceeds MCP output limit; use the CLI locally')
    text = data.decode('utf-8', errors='replace') or errors.decode('utf-8', errors='replace')
    response = {'content': [{'type': 'text', 'text': text}], 'isError': result.returncode != 0}
    # Preserve text for older clients; modern clients can consume JSON directly.
    try:
        structured = json.loads(text, parse_constant=reject_non_json_number)
    except (ValueError, RecursionError):
        structured = None
    if isinstance(structured, dict):
        response['structuredContent'] = structured
    return response


class Server:
    def __init__(self, root):
        self.root = root
        self.initialized = False
        self.ready = False
        self.protocol_version = None

    def handle(self, request):
        if not isinstance(request, dict):
            return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        req_id = request.get('id')
        # Invalid IDs must not be echoed as objects/arrays (or Python's bool-as-int).
        if 'id' in request and (type(req_id) not in (str, int, float)
                                or isinstance(req_id, float) and not math.isfinite(req_id)):
            return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request ID'}}
        def error(code, message):
            return {'jsonrpc': '2.0', 'id': req_id, 'error': {'code': code, 'message': message}}
        method = request.get('method')
        if request.get('jsonrpc') != '2.0' or not isinstance(method, str):
            return error(-32600, 'Invalid Request')
        if 'id' not in request:
            if (method == 'notifications/initialized' and self.initialized
                    and isinstance(request.get('params', {}), dict)):
                self.ready = True
            return None
        params = request.get('params', {})
        if not isinstance(params, dict):
            return error(-32602, 'params must be an object')
        if method == 'initialize':
            version = params.get('protocolVersion')
            if not isinstance(version, str) or not isinstance(params.get('capabilities'), dict) or not isinstance(params.get('clientInfo'), dict):
                return error(-32602, 'initialize requires protocolVersion, capabilities, clientInfo')
            self.initialized = True
            self.ready = False
            self.protocol_version = version if version in VERSIONS else VERSIONS[0]
            result = {'protocolVersion': self.protocol_version,
                      'capabilities': {'tools': {'listChanged': False}},
                      'serverInfo': {'name': 'cofa-local', 'version': __version__}}
        elif method == 'ping':
            result = {}
        elif not self.ready:
            return error(-32000, 'Initialize and send notifications/initialized first')
        elif method == 'tools/list':
            result = {'tools': TOOLS}
        elif method == 'tools/call':
            name = params.get('name')
            if not isinstance(name, str) or name not in {t['name'] for t in TOOLS}:
                return error(-32602, 'Unknown tool')
            try:
                result = call_tool(self.root, params['name'], params.get('arguments', {}))
            except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
                result = {'content': [{'type': 'text', 'text': str(exc)}], 'isError': True}
            if self.protocol_version in ('2024-11-05', '2025-03-26'):
                result.pop('structuredContent', None)
        else:
            return error(-32601, 'Method not found')
        return {'jsonrpc': '2.0', 'id': req_id, 'result': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True)
    args = parser.parse_args()
    root = Path(args.workspace).resolve(strict=True)
    if not root.is_dir():
        parser.error('workspace must be a directory')
    server = Server(root)
    while True:
        raw = sys.stdin.buffer.readline(MAX_MESSAGE + 1)
        if not raw:
            break
        if len(raw) > MAX_MESSAGE:
            print('MCP message exceeds 64 KiB; closing', file=sys.stderr)
            return 2
        try:
            response = server.handle(json.loads(raw.decode('utf-8'), parse_constant=reject_non_json_number))
        except (ValueError, UnicodeError, RecursionError):
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Parse error'}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
