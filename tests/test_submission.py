import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from cofa_kit.core import KitError
from cofa_kit.submission import _linked, submission_check

ROOT = Path(__file__).resolve().parents[1]


class SubmissionTests(unittest.TestCase):
    def test_hidden_dependencies_and_required_files_counted_without_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, size in [('report.md', 3), ('.git/objects/a', 5), ('node_modules/a.js', 7), ('.cofa-kit/x', 11)]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'x' * size)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = submission_check(root, ['report.md'], limit_bytes=26)
            self.assertTrue(result['ok'])
            self.assertEqual(result['total_bytes'], 26)
            self.assertEqual(result['file_count'], 4)
            self.assertEqual(result['largest_files'][0]['path'], '.cofa-kit/x')
            self.assertEqual(result['required_files'][0]['status'], 'present')
            self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.assertFalse(submission_check(root, limit_bytes=25)['within_limit'])

    def test_missing_empty_and_directory_are_not_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'empty.md').touch()
            (root / 'docs').mkdir()
            result = submission_check(root, ['missing.md', 'empty.md', 'docs'])
            self.assertFalse(result['ok'])
            self.assertEqual([x['status'] for x in result['required_files']], ['missing', 'empty', 'not_file'])

    def test_required_paths_cannot_escape_on_either_platform(self):
        with tempfile.TemporaryDirectory() as temp:
            for path in ['', '.', '../x', r'..\x', '/tmp/x', r'C:\x', r'C:x', r'\server\x', 'a:stream', 'x\x00y']:
                with self.subTest(path=path), self.assertRaises(KitError):
                    submission_check(temp, [path])

    def test_entry_bound_marks_partial_total_unknown_unless_already_over_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in ['a', 'b']:
                (Path(temp) / name).write_bytes(b'123')
            result = submission_check(temp, max_entries=1)
            self.assertFalse(result['complete'])
            self.assertFalse(result['ok'])
            self.assertIsNone(result['within_limit'])
            self.assertEqual(result['file_count'], 1)
            self.assertEqual(result['issues'][0]['reason'], 'entry_limit')
            self.assertFalse(submission_check(temp, max_entries=1, limit_bytes=2)['within_limit'])
            self.assertTrue(submission_check(temp, max_entries=2)['complete'])

    def test_time_bound_does_not_report_empty_workspace_success(self):
        with tempfile.TemporaryDirectory() as temp, patch('cofa_kit.submission.time.monotonic', side_effect=[0, 11]):
            result = submission_check(temp)
            self.assertFalse(result['ok'])
            self.assertIsNone(result['within_limit'])
            self.assertEqual(result['issues'][0]['reason'], 'time_limit')

    def test_unreadable_directory_marks_incomplete(self):
        with tempfile.TemporaryDirectory() as temp, patch('cofa_kit.submission.os.scandir', side_effect=PermissionError()):
            result = submission_check(temp)
            self.assertFalse(result['complete'])
            self.assertIsNone(result['within_limit'])

    def test_symlink_does_not_read_outside_workspace(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (Path(outside) / 'private.txt').write_bytes(b'private data')
            try:
                (root / 'linked').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('OS does not permit creating a symlink')
            result = submission_check(root, ['linked/private.txt'])
            self.assertEqual(result['total_bytes'], 0)
            self.assertFalse(result['complete'])
            self.assertEqual(result['required_files'][0]['status'], 'linked')

    def test_windows_junction_is_recognized_without_symlink_mode(self):
        self.assertTrue(_linked(SimpleNamespace(st_mode=0o040755, st_file_attributes=1024)))

    def test_invalid_limits_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for kwargs in [{'max_entries': 0}, {'max_entries': 1_000_001}, {'max_seconds': 0},
                           {'max_seconds': float('nan')}, {'max_seconds': float('inf')},
                           {'max_seconds': 61}, {'limit_bytes': -1}]:
                with self.subTest(kwargs=kwargs), self.assertRaises(KitError):
                    submission_check(temp, **kwargs)

    def test_largest_files_bounded(self):
        with tempfile.TemporaryDirectory() as temp:
            for i in range(25):
                (Path(temp) / str(i)).write_bytes(b'x' * i)
            result = submission_check(temp)
            self.assertEqual(len(result['largest_files']), 10)
            self.assertEqual(result['largest_files'][0]['size_bytes'], 24)
            self.assertEqual(result['total_bytes'], sum(range(25)))

    def test_cli_success_failure_and_invalid_input(self):
        with tempfile.TemporaryDirectory(prefix='제출 ') as temp:
            (Path(temp) / '요약.md').write_text('done', encoding='utf-8')
            base = [sys.executable, str(ROOT / 'scripts/cofa.py'), 'submission-check', '--workspace', temp]
            for extra, expected in [(['--required', '요약.md'], 0), (['--required', 'missing'], 1), (['--required', '../x'], 2)]:
                result = subprocess.run(base + extra, capture_output=True, text=True, encoding='utf-8', timeout=15)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertIsInstance(json.loads(result.stderr if expected == 2 else result.stdout), dict)


if __name__ == '__main__':
    unittest.main()
