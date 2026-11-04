import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from cofa_kit import __version__
from cofa_kit.diagnostics import diagnose, plugin_support
from test_integration import ROOT, load_script


class RemoteConfigTests(unittest.TestCase):
    def test_presets_custom_endpoint_and_legacy_alias(self):
        installer = load_script('install')
        with tempfile.TemporaryDirectory() as temp:
            config = installer.mcp_config(temp, with_openai_docs=True,
                                          presets=list(installer.MCP_PRESETS),
                                          remote_mcp=['team_docs=https://docs.example.com/mcp'])
            servers = config['mcpServers']
            self.assertEqual(len(servers), 6)
            self.assertEqual(servers['context7'], {'url': 'https://mcp.context7.com/mcp'})
            self.assertEqual(servers['microsoft_learn'], {'url': 'https://learn.microsoft.com/api/mcp'})
            self.assertEqual(servers['deepwiki'], {'url': 'https://mcp.deepwiki.com/mcp'})
            self.assertEqual(servers['team_docs'], {'url': 'https://docs.example.com/mcp'})
            self.assertFalse(list(Path(temp).iterdir()))

    def test_merge_preserves_metadata_and_original_bytes(self):
        installer = load_script('install')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / '기존 설정.json'
            original = {'mcpServers': {'existing': {'command': 'keep', 'args': ['a b']}},
                        'clientOptions': {'keep': True}}
            path.write_text(json.dumps(original), encoding='utf-8-sig')
            before = path.read_bytes()
            merged = installer.mcp_config(temp, presets=['deepwiki'], merge_mcp=path)
            self.assertEqual(merged['mcpServers']['existing'], original['mcpServers']['existing'])
            self.assertEqual(merged['clientOptions'], original['clientOptions'])
            self.assertEqual(path.read_bytes(), before)
            path.write_text(json.dumps(merged), encoding='utf-8')
            self.assertEqual(installer.mcp_config(temp, presets=['deepwiki'], merge_mcp=path), merged)

    def test_conflicts_do_not_overwrite_or_echo_credentials(self):
        installer = load_script('install')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'existing.json'
            path.write_text(json.dumps({'mcpServers': {'deepwiki': {'url': 'https://custom.example/mcp'}}}), encoding='utf-8')
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, 'existing MCP server differs'):
                installer.mcp_config(temp, presets=['deepwiki'], merge_mcp=path)
            self.assertEqual(path.read_bytes(), before)
            with self.assertRaises(ValueError) as error:
                installer.mcp_config(temp, remote_mcp=['secret=https://user:private@docs.example/mcp'])
            self.assertNotIn('private', str(error.exception))
            self.assertFalse((Path(temp) / '.agents').exists())

    def test_invalid_custom_endpoints_and_settings_are_rejected(self):
        installer = load_script('install')
        with tempfile.TemporaryDirectory() as temp:
            for value in ('missing', 'bad name=https://example.com', 'cofa_local=https://example.com',
                          'docs=http://example.com', 'docs=https://example.com?token=secret',
                          'docs=https://example.com/#fragment', 'docs=https://example.com:bad/mcp',
                          'docs=https://example.com/\npath', 'docs=https://example.com\\host'):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    installer.mcp_config(temp, remote_mcp=[value])
            path = Path(temp) / 'config.json'
            for value in ('[]', '{}', '{"mcpServers":[]}', '{"mcpServers":{"x":null}}',
                          '{"mcpServers":{"x":{},"x":{}}}', '{"mcpServers":{},"n":NaN}'):
                path.write_text(value, encoding='utf-8')
                with self.subTest(value=value), self.assertRaises(ValueError):
                    installer.mcp_config(temp, merge_mcp=path)
                self.assertEqual(path.read_text(encoding='utf-8'), value)

    def test_cli_requires_output_mode_before_any_install(self):
        with tempfile.TemporaryDirectory() as temp:
            command = [sys.executable, str(ROOT / 'scripts/install.py'), '--workspace', temp]
            for extra in (['--mcp-preset', 'deepwiki'], ['--remote-mcp', 'docs=https://example.com/mcp'],
                          ['--merge-mcp', 'missing.json']):
                result = subprocess.run(command + extra, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertFalse(list(Path(temp).iterdir()))
            result = subprocess.run(command + ['--mcp-json', '--mcp-preset', 'deepwiki',
                '--remote-mcp', 'extra=https://example.com/mcp'], capture_output=True, text=True, encoding='utf-8', timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(set(json.loads(result.stdout)['mcpServers']), {'cofa_local', 'deepwiki', 'extra'})
            self.assertFalse(list(Path(temp).iterdir()))


class PluginTests(unittest.TestCase):
    def test_manifests_and_marketplace_ship_with_skill_payload(self):
        package = load_script('package')
        packaged = {p.relative_to(ROOT).as_posix() for p in package.public_files()}
        for name in ('plugin.json', '.codex-plugin/plugin.json', '.agents/plugins/marketplace.json'):
            self.assertIn(name, packaged)
        portable = json.loads((ROOT / 'plugin.json').read_text())
        legacy = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        for manifest in (portable, legacy):
            self.assertEqual(manifest['name'], 'cofa-ready-kit')
            self.assertEqual(manifest['version'], __version__)
            self.assertNotIn('hooks', manifest)
        catalog = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        entry = catalog['plugins'][0]
        plugin_root = (ROOT / entry['source']['path']).resolve()
        self.assertEqual(plugin_root, ROOT)
        self.assertEqual(entry['name'], portable['name'])
        self.assertEqual(len(list((plugin_root / legacy['skills']).glob('*/SKILL.md'))), 6)

    def test_plugin_probe_only_runs_help_and_is_opt_in(self):
        with patch('cofa_kit.diagnostics.plugin_support') as probe:
            diagnose()
            probe.assert_not_called()
        with patch('cofa_kit.diagnostics.shutil.which', return_value='/bin/codex'), \
                patch('cofa_kit.diagnostics.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, stdout='Usage: codex plugin [options]', stderr='')
            result = plugin_support()
            self.assertEqual(result['status'], 'supported')
            self.assertFalse(result['installation_checked'])
            self.assertEqual(run.call_count, 3)
            self.assertTrue(all(call.args[0][-1] == '--help' for call in run.call_args_list))

    def test_missing_old_and_timed_out_cli_are_not_reported_supported(self):
        with patch('cofa_kit.diagnostics.shutil.which', return_value=None):
            self.assertEqual(plugin_support()['status'], 'unavailable')
            self.assertFalse(diagnose(check_plugins=True)['ok'])
        with patch('cofa_kit.diagnostics.shutil.which', return_value='/bin/codex'), \
                patch('cofa_kit.diagnostics.subprocess.run') as run:
            run.return_value = subprocess.CompletedProcess([], 2, stdout='', stderr='unknown command')
            self.assertEqual(plugin_support()['status'], 'unavailable')
            run.side_effect = subprocess.TimeoutExpired('codex', 8)
            self.assertEqual(plugin_support()['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
