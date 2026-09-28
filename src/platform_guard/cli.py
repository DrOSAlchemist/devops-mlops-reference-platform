from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation

import yaml

from platform_guard.cost_report import summarize_costs
from platform_guard.scanner import is_blocking, load_workflow, scan_workflow
from platform_guard.server import serve


def _print_findings(findings: list[dict[str, str]], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps({"passed": not findings, "findings": findings}, indent=2))
        return
    if not findings:
        print("PASS: no workflow policy findings")
        return
    for finding in findings:
        print(
            "{severity:8} {rule_id} {path}: {message}\n  Fix: {remediation}".format(**finding)
        )
    print(f"{len(findings)} finding(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="platform-guard", description="Local-first AI workflow and cloud operations checks.")
    commands = parser.add_subparsers(dest="command", required=True)

    scan = commands.add_parser("scan", help="scan a workflow YAML for AI safety and operations guardrails")
    scan.add_argument("workflow", help="path to a workflow YAML file")
    scan.add_argument("--format", choices=("text", "json"), default="text")

    cost = commands.add_parser("cost-report", help="summarize a cloud cost CSV")
    cost.add_argument("csv_file", help="CSV with date, service, cost_usd columns")
    cost.add_argument("--budget-usd", type=Decimal)

    server = commands.add_parser("serve", help="start the local scanner API and Prometheus metrics endpoint")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8080)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "scan":
        try:
            findings = scan_workflow(load_workflow(args.workflow))
        except (OSError, yaml.YAMLError) as error:
            print(f"Could not read workflow: {error}", file=sys.stderr)
            return 2
        _print_findings(findings, args.format)
        return 1 if is_blocking(findings) else 0

    if args.command == "cost-report":
        try:
            report = summarize_costs(args.csv_file, args.budget_usd)
        except (OSError, ValueError, InvalidOperation) as error:
            print(f"Could not summarize costs: {error}", file=sys.stderr)
            return 2
        print(json.dumps(report, indent=2))
        return 0

    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())