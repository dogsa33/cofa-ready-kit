"""Run with python -m cofa_kit. All outputs remain on the local machine."""
import argparse
import csv
import json
import sys
from pathlib import Path

from . import __version__
from .core import (KitError, append_log, check_workspace, doctor, init_workspace,
                   profile_file, report_workspace, run_check)
from .semiconductor import column_list, spc_summary, yield_summary
from .relations import RELATIONSHIPS, join_audit
from .evidence import check_evidence
from .diagnostics import diagnose


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description="Local preparation tools; no built-in AI, network, or submission actions. 'run' executes your explicit command.")
    cli.add_argument("--version", action="version", version=__version__)
    commands = cli.add_subparsers(dest="command", required=True)
    doctor_cmd = commands.add_parser("doctor", help="Check runtimes and optionally local skills/MCP without reading credentials")
    doctor_cmd.add_argument("--workspace", help="Compare installed skills with this kit; do not change files")
    doctor_cmd.add_argument("--check-mcp", action="store_true", help="Run a local synthetic MCP smoke check; requires --workspace")
    init = commands.add_parser("init", help="Create requirement and decision files without overwriting")
    init.add_argument("--workspace", required=True)
    profile = commands.add_parser("profile", help="Summarize a bounded sample of CSV/JSON records")
    profile.add_argument("file")
    profile.add_argument("--format", choices=["auto", "csv", "json"], default="auto")
    profile.add_argument("--encoding", choices=["utf-8-sig", "cp949"], default="utf-8-sig")
    profile.add_argument("--max-rows", type=int, default=10_000)
    profile.add_argument("--output", help="Write to a NEW file; existing files are never overwritten")
    log = commands.add_parser("log", help="Append an actual decision/test/assumption to the local log")
    log.add_argument("--workspace", required=True)
    log.add_argument("--kind", required=True, choices=["decision", "test", "assumption"])
    log.add_argument("--summary", required=True)
    log.add_argument("--evidence", nargs="*", default=[], metavar="RELATIVE_PATH")
    run = commands.add_parser("run", help="Run an explicit one-shot command and save bounded local execution evidence")
    run.add_argument("--workspace", required=True)
    run.add_argument("--id", required=True, dest="criterion_id")
    run.add_argument("--timeout", type=float, default=30)
    run.add_argument("--max-output-bytes", type=int, default=65_536)
    run.add_argument("--watch", action="append", metavar="REL_PATH", help="Snapshot an explicit file before/after; repeat before -- (max 32 files, 32 MiB total)")
    run.add_argument("arguments", nargs=argparse.REMAINDER, help="-- COMMAND ARG ... (no shell inserted)")
    evidence = commands.add_parser("evidence", help="Check whether explicitly watched execution inputs still have the same contents")
    evidence_commands = evidence.add_subparsers(dest="evidence_command", required=True)
    freshness = evidence_commands.add_parser("check", help="Read-only SHA256 comparison; fresh does not imply tests passed")
    freshness.add_argument("--workspace", required=True)
    freshness.add_argument("--result", required=True, help="Workspace-relative run result.json with --watch snapshots")
    data = commands.add_parser("data", help="Inspect local data relationships without joining source files")
    data_commands = data.add_subparsers(dest="data_command", required=True)
    join = data_commands.add_parser("join-check", help="Check key cardinality and predict join row counts")
    join.add_argument("left")
    join.add_argument("right")
    join.add_argument("--left-key", required=True, help="Comma-separated left key columns in matching order")
    join.add_argument("--right-key", required=True, help="Comma-separated right key columns in matching order")
    join.add_argument("--relationship", choices=RELATIONSHIPS, required=True)
    join.add_argument("--encoding", choices=["utf-8-sig", "cp949"], default="utf-8-sig")
    join.add_argument("--max-rows", type=int, default=100_000, help="Per-file limit; reject larger inputs instead of sampling")
    join.add_argument("--output", help="Write diagnostics to a NEW file without overwriting")
    semi = commands.add_parser("semi", help="Count-based inspection pass rates and exploratory frozen-baseline I-MR")
    analyses = semi.add_subparsers(dest="analysis", required=True)
    for name in ("yield", "spc"):
        analysis = analyses.add_parser(name)
        analysis.add_argument("file")
        analysis.add_argument("--encoding", choices=["utf-8-sig", "cp949"], default="utf-8-sig")
        analysis.add_argument("--max-rows", type=int, default=100_000, help="Reject larger inputs; never return partial aggregates")
        analysis.add_argument("--output", help="Write to a NEW file without overwriting")
        if name == "yield":
            analysis.add_argument("--group-by", required=True, help="Comma-separated grouping columns")
            analysis.add_argument("--key", required=True, help="Comma-separated unique inspection key columns; duplicates fail")
            analysis.add_argument("--tested-col", default="tested")
            analysis.add_argument("--passed-col", default="passed")
        else:
            analysis.add_argument("--value-col", required=True)
            analysis.add_argument("--time-col", required=True)
            analysis.add_argument("--baseline-count", type=int, required=True)
            analysis.add_argument("--series-cols", help="Constant identity columns, comma-separated; default checks known identity columns present")
    for name in ("check", "report"):
        command = commands.add_parser(name, help="Check required evidence paths" if name == "check" else "Render actual recorded evidence as Markdown")
        command.add_argument("--workspace", required=True)
        command.add_argument("--manifest", default="requirements.json", help="Path relative to workspace")
        if name == "report":
            command.add_argument("--output", help="Write to a NEW file; existing files are never overwritten")
    return cli


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        exit_code = 0
        if args.command == "doctor":
            diagnostics = diagnose(args.workspace, args.check_mcp)
            result = doctor()
            result['kit'] = diagnostics
            exit_code = 0 if result['python_supported'] and diagnostics['ok'] else 1
        elif args.command == "init":
            result = init_workspace(args.workspace)
        elif args.command == "profile":
            result = profile_file(args.file, format=args.format, encoding=args.encoding, max_rows=args.max_rows)
        elif args.command == "log":
            result = append_log(args.workspace, args.kind, args.summary, args.evidence)
        elif args.command == "check":
            result = check_workspace(args.workspace, args.manifest)
            exit_code = 0 if result["ok"] else 1
        elif args.command == "run":
            arguments = args.arguments[1:] if args.arguments[:1] == ["--"] else args.arguments
            result = run_check(args.workspace, args.criterion_id, arguments, timeout=args.timeout, max_output_bytes=args.max_output_bytes, watch=args.watch)
            exit_code = 0 if result["ok"] else 1
        elif args.command == "evidence":
            result = check_evidence(args.workspace, args.result)
            exit_code = 0 if result["fresh"] else 1
        elif args.command == "semi":
            if args.analysis == "yield":
                result = yield_summary(args.file, group_by=column_list(args.group_by), key=column_list(args.key),
                                       tested_col=args.tested_col, passed_col=args.passed_col,
                                       encoding=args.encoding, max_rows=args.max_rows)
            else:
                result = spc_summary(args.file, value_col=args.value_col, time_col=args.time_col,
                                     baseline_count=args.baseline_count,
                                     series_cols=column_list(args.series_cols) if args.series_cols is not None else None,
                                     encoding=args.encoding, max_rows=args.max_rows)
        elif args.command == "data":
            result = join_audit(args.left, args.right, left_key=column_list(args.left_key),
                                right_key=column_list(args.right_key), relationship=args.relationship,
                                encoding=args.encoding, max_rows=args.max_rows)
            exit_code = 0 if result["ok"] else 1
        else:
            result = report_workspace(args.workspace, args.manifest)
        output = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
        if getattr(args, "output", None):
            with Path(args.output).expanduser().open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(output.rstrip() + "\n")
            print(json.dumps({"written": args.output}, ensure_ascii=False))
        else:
            print(output)
        return exit_code
    except (KitError, OSError, UnicodeError, json.JSONDecodeError, csv.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
