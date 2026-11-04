import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from cofa_kit import __version__
from cofa_kit.core import KitError, _test_summaries, init_workspace, run_check
from cofa_kit.diagnostics import diagnose, mcp_smoke, skill_status
from test_integration import ROOT, load_script


class DiagnosticsTests(unittest.TestCase):
    def test_no_install_is_optional_and_probe_is_opt_in(self):
        with tempfile.TemporaryDirectory() as temp, patch('cofa_kit.diagnostics.mcp_smoke') as probe:
            result = diagnose(temp)
            self.assertTrue(result['ok'])
            self.assertEqual(len(result['skills']), 6)
            self.assertTrue(all(s['status'] == 'not_installed' for s in result['skills']))
            self.assertFalse(list(Path(temp).iterdir()))
            probe.assert_not_called()
        with self.assertRaises(KitError):
            diagnose(check_mcp=True)

    def test_comparison_catches_changed_and_missing_references_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            load_script('install').install(root)
            self.assertTrue(all(s['status'] == 'current' for s in skill_status(root)))
            build = root / '.agents/skills/cofa-build'
            (build / 'references/existing-project.md').write_text('personal version', encoding='utf-8')
            (build / 'notes.txt').write_text('keep this', encoding='utf-8')
            (root / '.agents/skills/cofa-triage/references/tool-check.md').unlink()
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = diagnose(root)
            self.assertFalse(result['ok'])
            statuses = {s['name']: s for s in result['skills']}
            self.assertEqual(statuses['cofa-build']['status'], 'different')
            self.assertEqual(statuses['cofa-triage']['status'], 'incomplete')
            self.assertEqual(statuses['cofa-explain']['status'], 'current')
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_reparse_destination_is_not_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            load_script('install').install(root)
            original = Path.lstat
            def linked(path, *args, **kwargs):
                if path.name == '.agents':
                    from types import SimpleNamespace
                    return SimpleNamespace(st_file_attributes=1024, st_mode=original(path).st_mode)
                return original(path, *args, **kwargs)
            with patch.object(Path, 'lstat', linked):
                self.assertTrue(all(s['status'] == 'error' for s in skill_status(root)))

    def test_actual_local_mcp_probe_and_workspace_preservation(self):
        with tempfile.TemporaryDirectory(prefix='과제 ') as temp:
            root = Path(temp)
            sentinel = root / 'AGENTS.md'
            sentinel.write_text('existing instructions', encoding='utf-8')
            result = diagnose(root, check_mcp=True)
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['local_mcp']['server_version'], __version__)
            self.assertEqual(len(result['local_mcp']['tools']), 6)
            self.assertFalse(result['client_connection_checked'])
            self.assertFalse(result['remote_mcp_checked'])
            self.assertEqual(list(root.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'existing instructions')

    def test_probe_reports_timeout_and_malformed_output(self):
        with patch('cofa_kit.diagnostics.subprocess.run', side_effect=subprocess.TimeoutExpired('probe', 15)):
            self.assertEqual(mcp_smoke()['status'], 'failed')
        for payload in (b'not json\n', b'[]\n', b'null\n', b'{"id":1}\n'):
            def broken(*args, **kwargs):
                kwargs['stdout'].write(payload)
                return subprocess.CompletedProcess(args, 0)
            with self.subTest(payload=payload), patch('cofa_kit.diagnostics.subprocess.run', side_effect=broken):
                self.assertEqual(mcp_smoke()['status'], 'failed')

    def test_doctor_cli_rejects_missing_workspace_and_reports_differences(self):
        command = [sys.executable, str(ROOT / 'scripts/cofa.py'), 'doctor']
        invalid = subprocess.run(command + ['--check-mcp'], capture_output=True, text=True, encoding='utf-8', timeout=10)
        self.assertEqual(invalid.returncode, 2)
        with tempfile.TemporaryDirectory() as temp:
            load_script('install').install(temp)
            (Path(temp) / '.agents/skills/cofa-build/SKILL.md').write_text('custom', encoding='utf-8')
            result = subprocess.run(command + ['--workspace', temp], capture_output=True, text=True, encoding='utf-8', timeout=35)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(json.loads(result.stdout)['kit']['ok'])


class MCPCompatibilityTests(unittest.TestCase):
    def test_structured_results_and_legacy_text_match(self):
        module = load_script('mcp_server')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'data.csv').write_text('value\n1\n3\n', encoding='utf-8')
            for version in module.VERSIONS:
                with self.subTest(version=version):
                    server = module.Server(root)
                    init = server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {
                        'protocolVersion': version, 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}}})
                    self.assertEqual(init['result']['protocolVersion'], version)
                    self.assertEqual(init['result']['serverInfo']['version'], __version__)
                    server.handle({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
                    reply = server.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': {
                        'name': 'profile_csv', 'arguments': {'path': 'data.csv'}}})['result']
                    data = json.loads(reply['content'][0]['text'])
                    self.assertEqual(data['columns'][0]['numeric']['mean'], 2)
                    if version in ('2024-11-05', '2025-03-26'):
                        self.assertNotIn('structuredContent', reply)
                    else:
                        self.assertEqual(reply['structuredContent'], data)

    def test_structured_diagnostic_does_not_hide_tool_failure(self):
        module = load_script('mcp_server')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'requirements.json').write_text(json.dumps({
                'required_files': ['missing.txt'], 'criteria': [{'id': 'R1', 'requirement': 'result',
                'priority': 'must', 'status': 'todo', 'evidence': []}]}), encoding='utf-8')
            reply = module.call_tool(root, 'workspace_check', {})
            self.assertTrue(reply['isError'])
            self.assertFalse(reply['structuredContent']['ok'])
            self.assertEqual(reply['structuredContent'], json.loads(reply['content'][0]['text']))


class NodeSpecTests(unittest.TestCase):
    def test_real_spec_empty_skipped_todo_pass_and_fail(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node unavailable')
        version = subprocess.run([node, '--version'], capture_output=True, text=True, timeout=5)
        if int(version.stdout.strip().lstrip('v').split('.')[0]) < 18:
            self.skipTest('Node 18+ required')
        cases = [(None, False, 'no_tests'), ("test.skip('skip', () => {});", False, 'all_pending'),
                 ("test.todo('todo');", False, 'all_pending'), ("test('pass', () => {});", True, None),
                 ("test('fail', () => { throw Error('expected'); });", False, 'reported_failure')]
        for body, expected, flag in cases:
            with self.subTest(body=body), tempfile.TemporaryDirectory() as temp:
                init_workspace(temp)
                if body:
                    (Path(temp) / 'only.test.cjs').write_text("const test = require('node:test');\n" + body, encoding='utf-8')
                result = run_check(temp, 'R1', [node, '--test', '--test-reporter=spec'], timeout=15)
                self.assertEqual(result['test_summary']['recognized'], 'node_spec')
                self.assertEqual(result['ok'], expected)
                if flag:
                    self.assertTrue(result['test_summary'][flag])

    def test_colored_spec_and_mixed_or_incomplete_markers(self):
        footer = 'ℹ tests 1\nℹ suites 0\nℹ pass 0\nℹ fail 0\nℹ cancelled 0\nℹ skipped 1\nℹ todo 0\nℹ duration_ms 1.5\n'
        colored = '\n'.join('\x1b[36m' + line + '\x1b[39m' for line in footer.splitlines())
        self.assertTrue(_test_summaries(colored)[0]['all_pending'])
        self.assertEqual(_test_summaries(footer.replace('ℹ pass', '# pass')), [])
        self.assertEqual(_test_summaries('ℹ tests 0\nℹ pass 0\n'), [])


if __name__ == '__main__':
    unittest.main()
