import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from cofa_kit.__main__ import main
from cofa_kit.core import KitError, init_workspace, read_log, run_check
from cofa_kit.evidence import check_evidence, prepare_watch

ROOT = Path(__file__).resolve().parents[1]


class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        init_workspace(self.root)
        (self.root / "code.py").write_bytes(b"print(1)\n")
        (self.root / "data.csv").write_bytes(b"value\n1\n")

    def run_watched(self, code="print('done')", watch=None):
        record = run_check(self.root, "R1", [sys.executable, "-c", code],
                           watch=["code.py", "data.csv"] if watch is None else watch)
        return record, record["evidence_directory"] + "/result.json"

    def altered_record(self, record, change):
        value = copy.deepcopy(record)
        change(value)
        (self.root / "altered.json").write_text(json.dumps(value), encoding="utf-8")
        return "altered.json"

    def cli(self, arguments):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = main(arguments)
        return code, output.getvalue(), errors.getvalue()

    def test_fresh_is_separate_from_failed_command_and_does_not_change_claims(self):
        record, result_path = self.run_watched("raise SystemExit(7)")
        self.assertFalse(record["ok"])
        result = check_evidence(self.root, result_path)
        self.assertTrue(result["fresh"])
        self.assertFalse(result["execution_ok"])
        self.assertEqual(result["tracked_count"], 2)
        self.assertEqual(record["watched_files"]["before"][0]["sha256"], hashlib.sha256(b"print(1)\n").hexdigest())
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(self.cli(["evidence", "check", "--workspace", str(self.root), "--result", result_path])[0], 0)
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()})
        self.assertEqual(json.loads((self.root / "requirements.json").read_text())["criteria"][0]["status"], "todo")

    def test_same_size_and_restored_mtime_changed_content_is_stale(self):
        _, result_path = self.run_watched()
        path = self.root / "code.py"
        info = path.stat()
        path.write_bytes(b"print(2)\n")
        os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
        result = check_evidence(self.root, result_path)
        self.assertFalse(result["fresh"])
        self.assertIn({"path": "code.py", "type": "content_changed"}, result["issues"])
        self.assertEqual(self.cli(["evidence", "check", "--workspace", str(self.root), "--result", result_path])[0], 1)

    def test_missing_and_replaced_directory_cannot_pass(self):
        _, result_path = self.run_watched()
        path = self.root / "code.py"
        path.unlink()
        result = check_evidence(self.root, result_path)
        self.assertFalse(result["fresh"])
        self.assertEqual(result["issues"], [{"path": "code.py", "type": "missing"}])
        path.mkdir()
        result = check_evidence(self.root, result_path)
        self.assertIn({"path": "code.py", "type": "not_regular"}, result["issues"])

    def test_during_execution_change_remains_stale_even_after_restoration(self):
        record, result_path = self.run_watched("from pathlib import Path; Path('code.py').write_bytes(b'changed')")
        self.assertEqual(record["exit_code"], 0)
        self.assertFalse(record["ok"])
        self.assertTrue(record["watched_files"]["changed_during_run"])
        (self.root / "code.py").write_bytes(b"print(1)\n")
        result = check_evidence(self.root, result_path)
        self.assertFalse(result["fresh"])
        self.assertTrue(result["changed_during_run"])
        self.assertIn("command_ok=False", read_log(self.root)[-1]["summary"])

    def test_deleted_during_execution_is_recorded_without_false_success(self):
        record, result_path = self.run_watched("from pathlib import Path; Path('code.py').unlink()")
        self.assertFalse(record["ok"])
        self.assertEqual(record["watched_files"]["after"][0], {"path": "code.py", "error": "missing"})
        self.assertFalse(check_evidence(self.root, result_path)["fresh"])

    def test_untracked_and_unlaunched_runs_are_unverifiable(self):
        record = run_check(self.root, "R1", [sys.executable, "-c", "pass"])
        self.assertNotIn("watched_files", record)
        path = record["evidence_directory"] + "/result.json"
        self.assertEqual(self.cli(["evidence", "check", "--workspace", str(self.root), "--result", path])[0], 2)
        record = run_check(self.root, "R1", [str(self.root / "missing-executable")], watch=["code.py"])
        self.assertFalse(record["launched"])
        with self.assertRaises(KitError):
            check_evidence(self.root, record["evidence_directory"] + "/result.json")

    def test_invalid_watch_options_fail_before_command_or_evidence_write(self):
        cases = [[], ["code.py"] * 33, ["code.py", "./code.py"], ["../outside.py"],
                 [str(self.root / "code.py")], ["missing.py"], ["."], ["code.py\x00"]]
        for paths in cases:
            with self.subTest(paths=paths), self.assertRaises(KitError):
                self.run_watched("from pathlib import Path; Path('marker').touch()", watch=paths)
        self.assertFalse((self.root / "marker").exists())
        self.assertFalse((self.root / "evidence").exists())
        self.assertEqual(read_log(self.root), [])

    def test_total_content_limit_prevents_partial_success(self):
        with patch("cofa_kit.evidence.MAX_TOTAL_BYTES", 9):
            self.assertEqual(len(prepare_watch(self.root, ["code.py"])), 1)
            with self.assertRaises(KitError):
                prepare_watch(self.root, ["code.py", "data.csv"])
        _, result_path = self.run_watched(watch=["code.py"])
        (self.root / "code.py").write_bytes(b"x" * 10)
        with patch("cofa_kit.evidence.MAX_TOTAL_BYTES", 9):
            result = check_evidence(self.root, result_path)
        self.assertFalse(result["fresh"])
        self.assertEqual(result["issues"], [{"path": "code.py", "type": "size_limit"}])

    def test_snapshot_metadata_shape_hash_path_and_duplicates_are_rejected(self):
        record, _ = self.run_watched()
        changes = [
            lambda r: r["watched_files"]["before"][0].update(sha256="not-a-hash"),
            lambda r: r["watched_files"]["before"][0].update(size_bytes=True),
            lambda r: r["watched_files"]["before"][0].update(path="../outside"),
            lambda r: r["watched_files"]["before"][0].update(path="./code.py"),
            lambda r: r["watched_files"]["before"].append(dict(r["watched_files"]["before"][0])),
            lambda r: r["watched_files"]["after"].reverse(),
            lambda r: r["watched_files"].update(changed_during_run=True),
            lambda r: r["watched_files"].update(version=True),
            lambda r: r["watched_files"].update(extra="ignored?"),
            lambda r: r["watched_files"]["after"][0].update(error="invented"),
        ]
        for index, change in enumerate(changes):
            with self.subTest(index=index), self.assertRaises(KitError):
                check_evidence(self.root, self.altered_record(record, change))
        (self.root / "altered.json").write_text('{"ok":true,"ok":false}', encoding="utf-8")
        with self.assertRaisesRegex(KitError, "Duplicate JSON"):
            check_evidence(self.root, "altered.json")

    def test_unstable_file_read_never_reports_fresh(self):
        _, result_path = self.run_watched(watch=["code.py"])
        from cofa_kit import evidence
        original = evidence._regular_path
        reads = 0
        def mutate_before_final_stat(root, relative):
            nonlocal reads
            if relative == "code.py":
                reads += 1
                if reads == 2:
                    (root / relative).write_bytes(b"changed length during read")
            return original(root, relative)
        with patch.object(evidence, "_regular_path", mutate_before_final_stat):
            result = check_evidence(self.root, result_path)
        self.assertFalse(result["fresh"])
        self.assertEqual(result["issues"], [{"path": "code.py", "type": "unstable"}])

    def test_symlink_components_rejected_even_for_internal_target(self):
        link = self.root / "alias.py"
        try:
            link.symlink_to(self.root / "code.py")
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        with self.assertRaisesRegex(KitError, "unsafe_path"):
            prepare_watch(self.root, ["alias.py"])
        _, result_path = self.run_watched(watch=["code.py"])
        (self.root / "code.py").unlink()
        (self.root / "code.py").symlink_to(self.root / "data.csv")
        self.assertIn({"path": "code.py", "type": "unsafe_path"}, check_evidence(self.root, result_path)["issues"])

    def test_windows_reparse_attribute_is_rejected_on_parent_component(self):
        folder = self.root / "inputs"
        folder.mkdir()
        (folder / "value.txt").write_text("value", encoding="utf-8")
        original = Path.lstat
        def reported_reparse(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            if path == folder:
                return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=1024)
            return info
        with patch.object(Path, "lstat", reported_reparse), self.assertRaisesRegex(KitError, "unsafe_path"):
            prepare_watch(self.root, ["inputs/value.txt"])

    def test_cli_repeated_watch_before_command_and_readonly_mcp(self):
        code, output, errors = self.cli(["run", "--workspace", str(self.root), "--id", "R1",
                                       "--watch", "code.py", "--watch", "data.csv", "--",
                                       sys.executable, "-c", "print('ordinary command')"])
        self.assertEqual(code, 0, errors)
        record = json.loads(output)
        path = record["evidence_directory"] + "/result.json"
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "evidence_freshness", "arguments": {"result_path": path}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "evidence_freshness", "arguments": {"result_path": path, "watch": ["code.py"]}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "evidence_freshness", "arguments": {"result_path": "../outside.json"}}},
        ]
        def mcp():
            process = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/mcp_server.py"), "--workspace", str(self.root)],
                                     input="\n".join(json.dumps(item) for item in messages) + "\n",
                                     capture_output=True, text=True, encoding="utf-8", timeout=15)
            self.assertEqual(process.returncode, 0, process.stderr)
            return [json.loads(line) for line in process.stdout.splitlines()]
        replies = mcp()
        from cofa_kit import __version__
        self.assertEqual(replies[0]["result"]["serverInfo"]["version"], __version__)
        self.assertFalse(replies[1]["result"]["isError"])
        self.assertTrue(json.loads(replies[1]["result"]["content"][0]["text"])["fresh"])
        self.assertTrue(replies[2]["result"]["isError"])
        self.assertTrue(replies[3]["result"]["isError"])
        (self.root / "code.py").write_bytes(b"modified")
        self.assertTrue(mcp()[1]["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
