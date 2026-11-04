import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from cofa_kit.__main__ import main
from cofa_kit.core import (KitError, append_log, check_workspace, contained_path,
                           init_workspace, profile_file, read_log, report_workspace, run_check)


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text, encoding="utf-8"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding=encoding)
        return path

    def manifest(self, status="verified", evidence=None, required=None, priority="must"):
        value = {"required_files": required if required is not None else ["answer.txt"], "criteria": [
            {"id": "R1", "requirement": "Return correct totals", "priority": priority,
             "status": status, "evidence": evidence if evidence is not None else ["checks.txt"]}]}
        self.write("requirements.json", json.dumps(value))
        return value

    def test_init_does_not_overwrite_or_partially_write(self):
        self.write("decision-log.jsonl", "keep me")
        with self.assertRaises(KitError):
            init_workspace(self.root)
        self.assertFalse((self.root / "requirements.json").exists())
        self.assertEqual((self.root / "decision-log.jsonl").read_text(), "keep me")

    def test_initialized_work_is_not_reported_complete(self):
        init_workspace(self.root)
        result = check_workspace(self.root)
        self.assertFalse(result["ok"])
        report = report_workspace(self.root)
        self.assertIn("GAPS FOUND", report)
        self.assertIn("No decisions or test outcomes", report)

    def test_csv_profile_missing_duplicate_numeric(self):
        file = self.write("data.csv", "name,value\na,2\na,2\nb,\nc,text\n")
        result = profile_file(file)
        self.assertEqual(result["rows_sampled"], 4)
        self.assertEqual(result["total_rows"], 4)
        self.assertEqual(result["duplicate_rows_in_sample"], 1)
        column = result["columns"][1]
        self.assertEqual(column["missing"], 1)
        self.assertEqual(column["numeric"]["mean"], 2)
        self.assertEqual(column["non_numeric_non_missing"], 1)

    def test_csv_bound_does_not_claim_full_scan(self):
        file = self.write("data.csv", "value\n1\n2\n3\n4\n")
        result = profile_file(file, max_rows=2)
        self.assertEqual(result["rows_sampled"], 2)
        self.assertIsNone(result["total_rows"])
        self.assertTrue(result["truncated"])
        self.assertEqual(result["columns"][0]["numeric"]["max"], 2)

    def test_csv_bad_shape_and_duplicate_headers(self):
        for text in ("a,a\n1,2\n", "a,b\n1,2,3\n", 'a,b\n"unfinished,2\n'):
            with self.subTest(text=text), self.assertRaises((KitError, __import__('csv').Error)):
                profile_file(self.write("bad.csv", text))

    def test_cp949_and_utf8_bom(self):
        for encoding in ("cp949", "utf-8-sig"):
            file = self.write("data.csv", "항목,수량\n검사,3\n", encoding)
            result = profile_file(file, encoding=encoding)
            self.assertEqual(result["columns"][0]["name"], "항목")

    def test_json_sample_missing_nested_and_boolean(self):
        file = self.write("data.json", json.dumps([{"n": 1, "flag": True}, {"n": None}, {"n": 99}]))
        result = profile_file(file, max_rows=2)
        self.assertEqual(result["total_rows"], 3)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["columns"][0]["missing"], 1)
        self.assertIsNone(result["columns"][1]["numeric"])

    def test_json_rejects_duplicate_keys_and_nan(self):
        for text in ('[{"x": 1, "x": 2}]', '[{"x": NaN}]', '[3]'):
            with self.subTest(text=text), self.assertRaises(KitError):
                profile_file(self.write("bad.json", text))

    def test_invalid_limit(self):
        file = self.write("data.csv", "a\n1\n")
        for value in (0, -1, 100001, True):
            with self.subTest(value=value), self.assertRaises(KitError):
                profile_file(file, max_rows=value)

    def test_manifest_success_and_file_gaps(self):
        self.manifest()
        self.write("answer.txt", "result")
        self.write("checks.txt", "checked actual totals")
        self.assertTrue(check_workspace(self.root)["ok"])
        self.write("answer.txt", "")
        self.assertFalse(check_workspace(self.root)["ok"])
        (self.root / "checks.txt").unlink()
        self.assertTrue(any(i["type"] == "evidence" for i in check_workspace(self.root)["issues"]))

    def test_verified_needs_evidence_and_must_needs_verified(self):
        self.manifest(evidence=[], required=[])
        self.assertFalse(check_workspace(self.root)["ok"])
        self.manifest(status="in_progress", evidence=[], required=[])
        self.assertFalse(check_workspace(self.root)["ok"])
        self.manifest(status="blocked", evidence=[], required=[], priority="could")
        result = check_workspace(self.root)
        self.assertTrue(result["ok"])
        self.assertTrue(result["warnings"])

    def test_empty_criteria_not_success(self):
        self.write("requirements.json", '{"required_files": [], "criteria": []}')
        self.assertFalse(check_workspace(self.root)["ok"])

    def test_traversal_rejected_portably(self):
        for path in ("../outside.txt", "a/../../outside.txt", "..\\outside.txt", "C:\\data.txt", "/etc/passwd"):
            with self.subTest(path=path), self.assertRaises(KitError):
                contained_path(self.root, path)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "outside.txt"
            target.write_text("private")
            link = self.root / "link.txt"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("This OS account cannot create symlinks")
            with self.assertRaises(KitError):
                contained_path(self.root, "link.txt")

    def test_log_and_report_preserve_observed_failure(self):
        init_workspace(self.root)
        self.write("failure.txt", "expected 7, found 8")
        append_log(self.root, "test", "FAILED: wrong total", ["failure.txt"])
        report = report_workspace(self.root)
        self.assertIn("FAILED: wrong total", report)
        self.assertIn("failure.txt", report)
        with self.assertRaises(KitError):
            append_log(self.root, "test", "not run", ["missing.txt"])

    def test_append_preserves_valid_log_without_final_newline(self):
        init_workspace(self.root)
        original = {"timestamp": "2026-10-30T00:00:00+00:00", "kind": "decision", "summary": "kept", "evidence": []}
        path = self.write("decision-log.jsonl", json.dumps(original))
        before = path.read_bytes()
        append_log(self.root, "test", "new observed result")
        self.assertTrue(path.read_bytes().startswith(before + b"\n"))
        records = read_log(self.root)
        self.assertEqual(records[0], original)
        self.assertEqual(records[1]["summary"], "new observed result")
        self.assertIn("new observed result", report_workspace(self.root))

    def test_append_rejects_unrelated_or_malformed_log_without_changing_bytes(self):
        init_workspace(self.root)
        for content in ('{"event":"order-created"}\n', '{"timestamp":', '{"timestamp":"x","kind":[],"summary":"x","evidence":[]}\n'):
            with self.subTest(content=content):
                path = self.write("decision-log.jsonl", content)
                before = path.read_bytes()
                with self.assertRaisesRegex(KitError, "Existing decision log is incompatible"):
                    append_log(self.root, "decision", "must not append")
                self.assertEqual(path.read_bytes(), before)

    def test_run_preflights_log_before_command_or_evidence_creation(self):
        init_workspace(self.root)
        path = self.write("decision-log.jsonl", '{"event":"order-created"}\n')
        before = path.read_bytes()
        with self.assertRaisesRegex(KitError, "Existing decision log is incompatible"):
            run_check(self.root, "R1", [sys.executable, "-c", "from pathlib import Path; Path('executed.txt').write_text('ran')"])
        self.assertFalse((self.root / "executed.txt").exists())
        self.assertFalse((self.root / "evidence").exists())
        self.assertEqual(path.read_bytes(), before)

    def test_append_size_limit_does_not_create_unreadable_oversized_log(self):
        init_workspace(self.root)
        path = self.root / "decision-log.jsonl"
        with patch("cofa_kit.core.MAX_LOG_BYTES", 32), self.assertRaises(KitError):
            append_log(self.root, "decision", "would exceed the small test limit")
        self.assertEqual(path.read_bytes(), b"")

    def test_manifest_shape_and_duplicate_id_rejected(self):
        self.write("requirements.json", '{"required_files": "x", "criteria": []}')
        with self.assertRaises(KitError):
            check_workspace(self.root)
        value = self.manifest()
        value["criteria"].append(dict(value["criteria"][0]))
        self.write("requirements.json", json.dumps(value))
        with self.assertRaises(KitError):
            check_workspace(self.root)

    def test_cli_exit_codes_and_output_no_overwrite(self):
        init_workspace(self.root)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["check", "--workspace", str(self.root)]), 1)
            self.assertEqual(main(["check", "--workspace", str(self.root), "--manifest", "absent.json"]), 2)
            file = self.write("sample.csv", "x\n1\n")
            output = self.write("keep.json", "original")
            self.assertEqual(main(["profile", str(file), "--output", str(output)]), 2)
            self.assertEqual(output.read_text(), "original")

    def test_run_records_real_failure_without_updating_status(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "import sys; print('observed failure'); sys.exit(7)"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["exit_code"], 7)
        evidence = self.root / result["evidence_directory"]
        self.assertIn("observed failure", (evidence / "stdout.txt").read_text())
        self.assertFalse(check_workspace(self.root)["ok"])
        self.assertEqual(json.loads((self.root / "requirements.json").read_text())["criteria"][0]["status"], "todo")

    def test_run_timeout_and_bounded_output(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.1)
        self.assertFalse(result["ok"])
        self.assertTrue(result["timed_out"])
        result = run_check(self.root, "R1", [sys.executable, "-c", "print('x' * 100000)"], max_output_bytes=1024)
        self.assertTrue(result["ok"])
        self.assertTrue(result["output_truncated"]["stdout"])
        self.assertEqual(result["captured_bytes"]["stdout"], 1024)
        self.assertLessEqual((self.root / result["evidence_directory"] / "stdout.txt").stat().st_size, 1024)

    def test_run_no_tests_or_all_skipped_is_not_success(self):
        init_workspace(self.root)
        for output in ("Ran 0 tests in 0.000s\nOK", "Ran 2 tests in 0.000s\nOK (skipped=2)", "1 skipped in 0.01s"):
            with self.subTest(output=output):
                result = run_check(self.root, "R1", [sys.executable, "-c", f"print({output!r})"])
                self.assertEqual(result["exit_code"], 0)
                self.assertFalse(result["ok"])

    def test_run_preserves_binary_output_bound_and_reported_failures(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "import sys; sys.stdout.buffer.write(bytes([255]) * 5000)"], max_output_bytes=1024)
        self.assertEqual((self.root / result["evidence_directory"] / "stdout.txt").stat().st_size, 1024)
        result = run_check(self.root, "R1", [sys.executable, "-c", "print('1 failed, 2 passed in 0.01s')"])
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["ok"])

    def test_run_normal_test_and_unknown_criterion(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "print('Ran 2 tests in 0.001s\\nOK')"])
        self.assertTrue(result["ok"])
        with self.assertRaises(KitError):
            run_check(self.root, "missing", [sys.executable, "--version"])

    def node(self):
        executable = shutil.which("node")
        if not executable:
            self.skipTest("Node.js is unavailable; optional real Node TAP check skipped")
        version = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5)
        if version.returncode or int(version.stdout.strip().lstrip("v").split(".")[0]) < 18:
            self.skipTest("Node.js 18+ is required for this optional real Node TAP check")
        return executable

    def test_real_node_empty_suite_is_not_test_success(self):
        executable = self.node()
        init_workspace(self.root)
        result = run_check(self.root, "R1", [executable, "--test", "--test-reporter=tap"], timeout=15)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["test_summary"]["recognized"], "node_tap")
        self.assertTrue(result["test_summary"]["no_tests"])
        self.assertFalse(result["ok"])

    def test_real_node_all_skipped_or_todo_is_not_test_success(self):
        executable = self.node()
        init_workspace(self.root)
        for declaration in ("test.skip('pending', () => {});", "test.todo('pending');"):
            with self.subTest(declaration=declaration):
                self.write("only.test.cjs", "const test = require('node:test');\n" + declaration)
                result = run_check(self.root, "R1", [executable, "--test", "--test-reporter=tap", "only.test.cjs"], timeout=15)
                self.assertEqual(result["exit_code"], 0)
                self.assertEqual(result["test_summary"]["recognized"], "node_tap")
                self.assertTrue(result["test_summary"]["all_pending"])
                self.assertFalse(result["ok"])
                self.assertIn("command_ok=False", read_log(self.root)[-1]["summary"])
                self.assertIn("all_pending=True", read_log(self.root)[-1]["summary"])

    def test_real_node_pass_and_fail_remain_distinct(self):
        executable = self.node()
        init_workspace(self.root)
        for expected, assertion in ((True, "assert.equal(2 + 2, 4)"), (False, "assert.equal(2 + 2, 5)")):
            with self.subTest(expected=expected):
                self.write("only.test.cjs", "const test = require('node:test'); const assert = require('node:assert/strict');\n"
                           + "test('arithmetic contract', () => { " + assertion + "; });\n")
                result = run_check(self.root, "R1", [executable, "--test", "--test-reporter=tap", "only.test.cjs"], timeout=15)
                self.assertEqual(result["test_summary"]["recognized"], "node_tap")
                self.assertEqual(result["ok"], expected)
                self.assertEqual(result["test_summary"]["reported_failure"], not expected)

    def test_partial_tap_text_is_not_mistaken_for_complete_node_summary(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "print('# tests 0\\n# pass 0')"])
        self.assertIsNone(result["test_summary"]["recognized"])
        self.assertTrue(result["ok"])

    def test_truncated_output_preserves_exact_tail_used_for_summary(self):
        init_workspace(self.root)
        result = run_check(self.root, "R1", [sys.executable, "-c", "print('x' * 25000); print('Ran 1 test in 0.001s\\nOK')"], max_output_bytes=1024)
        self.assertTrue(result["ok"])
        directory = self.root / result["evidence_directory"]
        self.assertNotIn(b"Ran 1 test", (directory / "stdout.txt").read_bytes())
        tail = result["tail_capture"]["streams"]["stdout"]
        tail_bytes = (self.root / tail["path"]).read_bytes()
        self.assertIn(b"Ran 1 test in 0.001s", tail_bytes)
        self.assertEqual(len(tail_bytes), tail["captured_bytes"])
        self.assertLessEqual(len(tail_bytes), 16384)
        self.assertEqual(tail["observed_end_byte_exclusive"] - tail["observed_start_byte"], len(tail_bytes))
        self.assertEqual(result["test_summary"]["evidence_path"], tail["path"])
        self.assertLessEqual(sum(p.stat().st_size for p in directory.glob("*.tail.txt")), 32768)

    def test_multiple_summaries_cannot_hide_failure_or_mix_skip_counts(self):
        init_workspace(self.root)
        cases = [
            "1 failed, 1 passed in 0.01s\n1 passed in 0.01s",
            "Ran 1 test in 0.001s\nOK\nRan 1 test in 0.001s\nOK (skipped=1)",
            "Ran 1 test in 0.001s\nOK\n1 passed in 0.01s",
        ]
        for text in cases:
            with self.subTest(text=text):
                result = run_check(self.root, "R1", [sys.executable, "-c", f"print({text!r})"])
                self.assertEqual(result["exit_code"], 0)
                self.assertFalse(result["ok"])
                self.assertTrue(result["test_summary"]["ambiguous"])
                self.assertEqual(len(result["test_summary"]["summaries"]), 2)
                self.assertFalse(result["test_summary"]["all_skipped"])
        self.assertIn("ambiguous=True", read_log(self.root)[-1]["summary"])

    def test_stdout_and_stderr_summaries_are_reviewed_separately(self):
        init_workspace(self.root)
        code = "import sys; print('1 passed in 0.01s'); print('1 failed in 0.01s', file=sys.stderr)"
        result = run_check(self.root, "R1", [sys.executable, "-c", code])
        self.assertFalse(result["ok"])
        summary = result["test_summary"]
        self.assertTrue(summary["ambiguous"])
        self.assertTrue(summary["reported_failure"])
        self.assertEqual({item["stream"] for item in summary["summaries"]}, {"stdout", "stderr"})

    def test_isolated_summary_words_and_indented_traceback_text_are_not_footers(self):
        init_workspace(self.root)
        text = "Example: Ran 1 test\n  Ran 1 test in 0.001s\n  OK\nTask said 1 failed in 0.01s\n# tests 0"
        result = run_check(self.root, "R1", [sys.executable, "-c", f"print({text!r})"])
        self.assertIsNone(result["test_summary"]["recognized"])
        self.assertTrue(result["ok"])

    def test_evidence_write_failure_cannot_record_success(self):
        init_workspace(self.root)
        original = Path.write_bytes
        def fail_tail(path, data):
            if path.name == "stdout.tail.txt":
                raise OSError("simulated evidence write failure")
            return original(path, data)
        with patch.object(Path, "write_bytes", fail_tail), self.assertRaisesRegex(OSError, "simulated evidence"):
            run_check(self.root, "R1", [sys.executable, "-c", "print('1 passed in 0.01s')"])
        self.assertEqual(read_log(self.root), [])
        self.assertEqual(list((self.root / "evidence").rglob("result.json")), [])


if __name__ == "__main__":
    unittest.main()
